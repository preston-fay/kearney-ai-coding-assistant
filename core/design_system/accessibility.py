"""
WCAG 2.1 AA accessibility enforcement.

Provides functions for calculating contrast ratios and ensuring
colors meet accessibility requirements. All color adjustments
attempt to preserve the original hue when possible.

WCAG 2.1 AA Requirements:
- Normal text: 4.5:1 minimum contrast ratio
- Large text (18pt+ or 14pt+ bold): 3.0:1 minimum contrast ratio
- UI components: 3.0:1 minimum contrast ratio
"""

from typing import Tuple
import colorsys


def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """
    Convert hex color to RGB tuple.

    Args:
        hex_color: Hex color string (e.g., "#7823DC" or "7823DC").

    Returns:
        Tuple of (R, G, B) values (0-255).
    """
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def rgb_to_hex(r: int, g: int, b: int) -> str:
    """
    Convert RGB to hex color.

    Args:
        r: Red value (0-255).
        g: Green value (0-255).
        b: Blue value (0-255).

    Returns:
        Hex color string (e.g., "#7823DC").
    """
    return f"#{r:02x}{g:02x}{b:02x}".upper()


def relative_luminance(hex_color: str) -> float:
    """
    Calculate relative luminance per WCAG 2.1 formula.

    Reference: https://www.w3.org/WAI/GL/wiki/Relative_luminance

    Args:
        hex_color: Hex color string.

    Returns:
        Relative luminance value between 0 and 1.
    """
    r, g, b = hex_to_rgb(hex_color)

    def channel_luminance(c: int) -> float:
        c = c / 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    return (0.2126 * channel_luminance(r) +
            0.7152 * channel_luminance(g) +
            0.0722 * channel_luminance(b))


def contrast_ratio(color1: str, color2: str) -> float:
    """
    Calculate contrast ratio between two colors.

    Reference: https://www.w3.org/WAI/GL/wiki/Contrast_ratio

    Args:
        color1: First hex color string.
        color2: Second hex color string.

    Returns:
        Contrast ratio value between 1 and 21.
    """
    l1 = relative_luminance(color1)
    l2 = relative_luminance(color2)
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


def ensure_contrast(
    foreground: str,
    background: str,
    min_ratio: float = 4.5,
    strategy: str = "auto"
) -> str:
    """
    Adjust foreground color to meet contrast requirements.

    Args:
        foreground: Hex color for text/foreground.
        background: Hex color for background.
        min_ratio: Minimum contrast ratio (4.5 for normal text, 3.0 for large).
        strategy: Adjustment strategy:
            - "binary": Use white or black
            - "tint": Lighten/darken while preserving hue
            - "auto": Try tint first, fall back to binary

    Returns:
        Adjusted foreground color that meets contrast requirements.
    """
    current_ratio = contrast_ratio(foreground, background)
    if current_ratio >= min_ratio:
        return foreground

    if strategy == "binary":
        return _ensure_contrast_binary(foreground, background, min_ratio)
    elif strategy == "tint":
        return _ensure_contrast_tint(foreground, background, min_ratio)
    else:  # auto
        tinted = _ensure_contrast_tint(foreground, background, min_ratio)
        if contrast_ratio(tinted, background) >= min_ratio:
            return tinted
        return _ensure_contrast_binary(foreground, background, min_ratio)


def _ensure_contrast_binary(fg: str, bg: str, min_ratio: float) -> str:
    """
    Return white or black based on which has better contrast.

    Args:
        fg: Foreground color (unused, kept for signature consistency).
        bg: Background color.
        min_ratio: Minimum required ratio (unused).

    Returns:
        "#FFFFFF" or "#000000" based on background luminance.
    """
    white_contrast = contrast_ratio("#FFFFFF", bg)
    black_contrast = contrast_ratio("#000000", bg)
    return "#FFFFFF" if white_contrast > black_contrast else "#000000"


def _ensure_contrast_tint(fg: str, bg: str, min_ratio: float) -> str:
    """
    Lighten or darken foreground to meet contrast, preserving hue.

    Args:
        fg: Foreground color.
        bg: Background color.
        min_ratio: Minimum required ratio.

    Returns:
        Adjusted color with preserved hue.
    """
    r, g, b = hex_to_rgb(fg)
    h, l, s = colorsys.rgb_to_hls(r/255, g/255, b/255)

    bg_luminance = relative_luminance(bg)

    # Determine direction: lighten if bg is dark, darken if bg is light
    direction = 1 if bg_luminance < 0.5 else -1

    # Incrementally adjust lightness
    original_l = l
    for step in range(100):
        l = max(0, min(1, original_l + (direction * step * 0.01)))
        r2, g2, b2 = colorsys.hls_to_rgb(h, l, s)
        new_color = rgb_to_hex(
            int(round(r2 * 255)),
            int(round(g2 * 255)),
            int(round(b2 * 255))
        )
        if contrast_ratio(new_color, bg) >= min_ratio:
            return new_color

    # If we can't meet contrast with tint, return the most extreme version
    l = 1.0 if direction > 0 else 0.0
    r2, g2, b2 = colorsys.hls_to_rgb(h, l, s)
    return rgb_to_hex(
        int(round(r2 * 255)),
        int(round(g2 * 255)),
        int(round(b2 * 255))
    )


def get_strategy_for_context(context: str) -> str:
    """
    Return appropriate contrast strategy for given context.

    Args:
        context: UI context name.

    Returns:
        Strategy name ("binary", "tint", or "auto").
    """
    strategies = {
        "button": "binary",
        "cta": "binary",
        "chart_label": "binary",
        "heading_large": "tint",
        "heading_small": "auto",
        "body": "auto",
        "link": "auto",
        "chart_series": "tint",
    }
    return strategies.get(context, "auto")


def get_min_ratio_for_context(context: str) -> float:
    """
    Get minimum contrast ratio for a given context.

    Args:
        context: UI context name.

    Returns:
        Minimum contrast ratio (3.0 or 4.5).
    """
    # Large text and UI components only need 3:1
    large_text_contexts = {
        "heading_large",
        "ui_component",
        "chart_series",
        "icon",
    }
    return 3.0 if context in large_text_contexts else 4.5


def validate_wcag_aa(fg: str, bg: str, context: str = "body") -> dict:
    """
    Validate a color pair against WCAG 2.1 AA.

    Args:
        fg: Foreground (text) color.
        bg: Background color.
        context: UI context for determining requirements.

    Returns:
        Dictionary with validation results:
            - foreground: Input foreground color
            - background: Input background color
            - ratio: Calculated contrast ratio
            - required: Minimum required ratio
            - passes: Whether the pair passes WCAG AA
            - context: Input context
    """
    ratio = contrast_ratio(fg, bg)
    min_ratio = get_min_ratio_for_context(context)

    return {
        "foreground": fg,
        "background": bg,
        "ratio": round(ratio, 2),
        "required": min_ratio,
        "passes": ratio >= min_ratio,
        "context": context,
    }


def make_accessible_palette(
    colors: list,
    background: str,
    min_ratio: float = 3.0,
    strategy: str = "tint"
) -> list:
    """
    Adjust a list of colors to be accessible against a background.

    Args:
        colors: List of hex color strings.
        background: Background color.
        min_ratio: Minimum contrast ratio.
        strategy: Adjustment strategy.

    Returns:
        List of adjusted hex color strings.
    """
    return [
        ensure_contrast(color, background, min_ratio, strategy)
        for color in colors
    ]


def is_dark_color(hex_color: str) -> bool:
    """
    Determine if a color is considered dark.

    Args:
        hex_color: Hex color string.

    Returns:
        True if the color has luminance < 0.5.
    """
    return relative_luminance(hex_color) < 0.5


def get_text_color_for_background(background: str) -> str:
    """
    Get appropriate text color (white or black) for a background.

    Args:
        background: Background hex color.

    Returns:
        "#FFFFFF" for dark backgrounds, "#000000" for light.
    """
    return "#FFFFFF" if is_dark_color(background) else "#000000"
