"""
Kearney AI Coding Assistant - Intelligent Chart Coloring

Applies contextually appropriate colors based on chart type and data characteristics.
"""

from typing import List, Tuple, Optional, Literal
import colorsys

# Kearney Palette
KEARNEY_PURPLE = "#7823DC"
KEARNEY_PURPLE_RGB = (120, 35, 220)

# Pre-computed purple gradient (dark to light, 10 steps)
PURPLE_GRADIENT = [
    "#4A1587",  # Darkest (highest value)
    "#5C1A9E",
    "#6E1FB5",
    "#7823DC",  # Primary purple
    "#8F4DE0",
    "#A677E4",
    "#BDA1E8",
    "#D4CBEC",
    "#EBE5F0",
    "#F5F2F8",  # Lightest (lowest value)
]

# Categorical palette (distinct colors, no green)
CATEGORICAL_PALETTE = [
    "#7823DC",  # Purple (primary)
    "#2E86AB",  # Blue
    "#A23B72",  # Magenta
    "#F18F01",  # Orange
    "#C73E1D",  # Red
    "#3B1F2B",  # Dark purple
    "#95818D",  # Gray purple
    "#E8D5B7",  # Tan
]


def get_sequential_colors(
    n: int,
    values: Optional[List[float]] = None,
    reverse: bool = False
) -> List[str]:
    """
    Get sequential colors based on value ordering.

    Higher values get darker purple, lower values get lighter purple.

    Args:
        n: Number of colors needed
        values: Optional values to determine ordering
        reverse: If True, lower values get darker colors

    Returns:
        List of hex color codes
    """
    if n == 1:
        return [KEARNEY_PURPLE]

    # Generate n colors from the gradient
    step = (len(PURPLE_GRADIENT) - 1) / (n - 1)
    colors = [PURPLE_GRADIENT[int(i * step)] for i in range(n)]

    if values is not None:
        # Sort colors by values (highest value gets darkest color)
        sorted_indices = sorted(range(len(values)), key=lambda i: values[i], reverse=True)
        result = [None] * n
        for rank, original_idx in enumerate(sorted_indices):
            result[original_idx] = colors[rank] if not reverse else colors[-(rank+1)]
        return result

    return colors if not reverse else colors[::-1]


def get_categorical_colors(n: int) -> List[str]:
    """
    Get distinct categorical colors.

    Use when categories have no inherent order or magnitude relationship.
    """
    if n <= len(CATEGORICAL_PALETTE):
        return CATEGORICAL_PALETTE[:n]

    # If more colors needed, generate variations
    colors = CATEGORICAL_PALETTE.copy()
    while len(colors) < n:
        # Add lightened versions
        for base_color in CATEGORICAL_PALETTE:
            if len(colors) >= n:
                break
            colors.append(lighten_color(base_color, 0.3))

    return colors[:n]


def get_diverging_colors(
    n: int,
    center_idx: Optional[int] = None
) -> List[str]:
    """
    Get diverging colors for data with meaningful center point.

    Good for: profit/loss, above/below average, positive/negative change.

    Purple for positive, gray for neutral, muted red for negative.
    """
    if center_idx is None:
        center_idx = n // 2

    # Negative side (muted red gradient)
    negative_colors = [
        "#C73E1D",  # Darkest red
        "#D46A52",
        "#E19687",
        "#EEC2BC",
    ]

    # Neutral
    neutral = "#95818D"

    # Positive side (purple gradient)
    positive_colors = PURPLE_GRADIENT[:4]

    colors = []
    for i in range(n):
        if i < center_idx:
            # Negative side
            neg_idx = int((center_idx - i - 1) / center_idx * (len(negative_colors) - 1)) if center_idx > 0 else 0
            colors.append(negative_colors[min(neg_idx, len(negative_colors)-1)])
        elif i == center_idx:
            colors.append(neutral)
        else:
            # Positive side
            pos_idx = int((i - center_idx - 1) / (n - center_idx - 1) * (len(positive_colors) - 1)) if n - center_idx > 1 else 0
            colors.append(positive_colors[min(pos_idx, len(positive_colors)-1)])

    return colors


def lighten_color(hex_color: str, factor: float = 0.2) -> str:
    """Lighten a hex color by a factor."""
    hex_color = hex_color.lstrip('#')
    r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    r = int(r + (255 - r) * factor)
    g = int(g + (255 - g) * factor)
    b = int(b + (255 - b) * factor)

    return f"#{r:02x}{g:02x}{b:02x}"


def get_chart_colors(
    chart_type: Literal["bar", "pie", "line", "scatter", "area", "heatmap"],
    n: int,
    values: Optional[List[float]] = None,
    mode: Optional[Literal["sequential", "categorical", "diverging"]] = None,
    has_negative: bool = False
) -> List[str]:
    """
    Get intelligent colors based on chart type and data characteristics.

    Default behaviors by chart type:
    - bar: Sequential (value-based gradient) unless categorical detected
    - pie: Sequential by slice size (larger = darker)
    - line: Categorical (distinct colors per series)
    - scatter: Categorical by default, sequential if continuous color variable
    - area: Categorical (distinct colors per series)
    - heatmap: Always sequential

    Args:
        chart_type: Type of chart
        n: Number of colors needed
        values: Data values (used for sequential coloring)
        mode: Override automatic mode selection
        has_negative: Whether data includes negative values

    Returns:
        List of hex color codes
    """
    # Override if mode specified
    if mode == "sequential":
        return get_sequential_colors(n, values)
    elif mode == "categorical":
        return get_categorical_colors(n)
    elif mode == "diverging":
        return get_diverging_colors(n)

    # Default logic by chart type
    if chart_type == "bar":
        if has_negative:
            return get_diverging_colors(n)
        elif values is not None:
            return get_sequential_colors(n, values)
        else:
            return get_sequential_colors(n)

    elif chart_type == "pie":
        # Larger slices get darker colors
        if values is not None:
            return get_sequential_colors(n, values)
        return get_sequential_colors(n)

    elif chart_type == "line":
        # Distinct colors for each series
        return get_categorical_colors(n)

    elif chart_type == "scatter":
        # Categorical for point groups
        return get_categorical_colors(n)

    elif chart_type == "area":
        # Distinct for stacked areas
        return get_categorical_colors(n)

    elif chart_type == "heatmap":
        # Always sequential
        return get_sequential_colors(n, values)

    # Fallback
    return get_sequential_colors(n, values)
