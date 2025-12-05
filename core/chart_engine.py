"""
Kearney Chart Engine - KDS-Compliant Charting

Wraps matplotlib with Kearney Design System (KDS) brand defaults.
All charts generated through this engine are automatically brand-compliant.

Usage:
    from core.chart_engine import KDSChart

    chart = KDSChart()
    chart.bar(data, labels, title='Revenue by Region')
    chart.save('outputs/charts/revenue.png')

Brand Rules Enforced:
    - Primary color: Kearney Purple (#7823DC)
    - No gridlines
    - Data labels outside bars/slices
    - Dark mode default (background #1E1E1E)
    - Inter font (Arial fallback)
    - No emojis in any text
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple, Union

import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for server use
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.figure import Figure
from matplotlib.axes import Axes
from matplotlib.ticker import FuncFormatter

from core.number_formatter import smart_format, format_axis_label
from core.color_intelligence import get_chart_colors

logger = logging.getLogger(__name__)


# Kearney Brand Colors
class KDSColors:
    """Kearney Design System color palette."""
    PRIMARY = "#7823DC"  # Kearney Purple
    BACKGROUND_DARK = "#1E1E1E"
    BACKGROUND_LIGHT = "#FFFFFF"
    TEXT_LIGHT = "#FFFFFF"
    TEXT_DARK = "#333333"
    GRAY_100 = "#F5F5F5"
    GRAY_200 = "#E0E0E0"
    GRAY_300 = "#CCCCCC"
    GRAY_400 = "#999999"
    GRAY_500 = "#666666"
    GRAY_600 = "#333333"

    # Chart color palette (purple variations + neutrals, NO GREEN)
    PALETTE = [
        "#7823DC",  # Primary purple
        "#9B4DCA",  # Light purple
        "#5C1BA8",  # Dark purple
        "#B266FF",  # Bright purple
        "#4A148C",  # Deep purple
        "#666666",  # Gray
        "#999999",  # Light gray
        "#333333",  # Dark gray
        "#CE93D8",  # Pale purple
        "#7B1FA2",  # Purple variant
    ]


# Size presets for visualizations
SIZE_PRESETS = {
    "presentation": (1920, 1080),  # 16:9
    "document": (1200, 900),       # 4:3
    "square": (1200, 1200),        # 1:1
    "banner": (1800, 600),         # 3:1
    "full_slide": (1920, 1080),    # Same as presentation
    "half_slide": (960, 720),      # Half width for two-column layouts
}


def parse_size_preset(size_spec: str) -> Tuple[int, int]:
    """
    Parse a size specification into width, height pixels.

    Args:
        size_spec: Either a preset name ('presentation', 'document', etc.)
                   or a custom size string ('1400x800').

    Returns:
        Tuple of (width, height) in pixels.
    """
    # Check if it's a preset
    if size_spec.lower() in SIZE_PRESETS:
        return SIZE_PRESETS[size_spec.lower()]

    # Try to parse as custom size (e.g., "1400x800")
    if 'x' in size_spec.lower():
        parts = size_spec.lower().split('x')
        try:
            width = int(parts[0].strip())
            height = int(parts[1].strip())
            return (width, height)
        except (ValueError, IndexError):
            pass

    # Default to presentation size
    return SIZE_PRESETS["presentation"]


def pixels_to_inches(width: int, height: int, dpi: int = 150) -> Tuple[float, float]:
    """Convert pixel dimensions to inches for matplotlib."""
    return (width / dpi, height / dpi)


class KDSChart:
    """
    KDS-compliant chart generator.

    Wraps matplotlib with brand defaults automatically applied.
    All charts use dark mode by default with Kearney Purple accents.

    Supports size presets for common output contexts:
        - presentation: 1920x1080 (16:9)
        - document: 1200x900 (4:3)
        - square: 1200x1200 (1:1)
        - banner: 1800x600 (3:1)
        - full_slide: 1920x1080
        - half_slide: 960x720
    """

    def __init__(
        self,
        figsize: Optional[Tuple[float, float]] = None,
        size_preset: Optional[str] = None,
        dark_mode: bool = True,
        dpi: int = 150,
        default_format: str = "svg",
        smart_numbers: bool = True,
        intelligent_colors: bool = True,
        theme: Optional["KDSTheme"] = None,
    ):
        """
        Initialize KDSChart with brand defaults.

        Args:
            figsize: Figure size in inches (width, height). Overrides size_preset.
            size_preset: Named preset ('presentation', 'document', 'square', etc.)
                         or custom size string ('1400x800'). Ignored if figsize set.
            dark_mode: If True, use dark background. Default True per KDS.
            dpi: Resolution for saved images.
            default_format: Default output format ('svg' or 'png'). SVG recommended.
            smart_numbers: If True, format large numbers with K/M/B abbreviations.
            intelligent_colors: If True, use context-aware coloring based on chart type.
            theme: Optional KDSTheme instance for custom theming. If provided,
                   applies theme's matplotlib rcParams after default setup.
        """
        # Handle size - priority: figsize > size_preset > default
        if figsize is not None:
            self.figsize = figsize
        elif size_preset is not None:
            width_px, height_px = parse_size_preset(size_preset)
            self.figsize = pixels_to_inches(width_px, height_px, dpi)
        else:
            # Default to presentation size
            width_px, height_px = SIZE_PRESETS["presentation"]
            self.figsize = pixels_to_inches(width_px, height_px, dpi)

        self.dark_mode = dark_mode
        self.dpi = dpi
        self.default_format = default_format.lower()
        self.smart_numbers = smart_numbers
        self.intelligent_colors = intelligent_colors
        self.theme = theme
        self.fig: Optional[Figure] = None
        self.ax: Optional[Axes] = None
        self._setup_style()

        # Apply custom theme if provided (overrides defaults)
        if self.theme is not None:
            self._apply_theme()

    def _setup_style(self) -> None:
        """Configure matplotlib style for KDS compliance."""
        # Try to use Inter font, fall back to Arial
        available_fonts = [f.name for f in fm.fontManager.ttflist]

        if "Inter" in available_fonts:
            self.font_family = "Inter"
        elif "Arial" in available_fonts:
            self.font_family = "Arial"
        else:
            self.font_family = "sans-serif"

        # Set global style
        plt.rcParams.update({
            "font.family": self.font_family,
            "font.size": 11,
            "font.weight": 400,
            "axes.titleweight": 600,
            "axes.labelweight": 500,
            "axes.grid": False,  # NO GRIDLINES - KDS requirement
            "axes.spines.top": False,
            "axes.spines.right": False,
            "legend.frameon": False,
            "figure.facecolor": KDSColors.BACKGROUND_DARK if self.dark_mode else KDSColors.BACKGROUND_LIGHT,
            "axes.facecolor": KDSColors.BACKGROUND_DARK if self.dark_mode else KDSColors.BACKGROUND_LIGHT,
            "text.color": KDSColors.TEXT_LIGHT if self.dark_mode else KDSColors.TEXT_DARK,
            "axes.labelcolor": KDSColors.TEXT_LIGHT if self.dark_mode else KDSColors.TEXT_DARK,
            "axes.edgecolor": KDSColors.GRAY_400 if self.dark_mode else KDSColors.GRAY_300,
            "xtick.color": KDSColors.TEXT_LIGHT if self.dark_mode else KDSColors.TEXT_DARK,
            "ytick.color": KDSColors.TEXT_LIGHT if self.dark_mode else KDSColors.TEXT_DARK,
        })

    def _apply_theme(self) -> None:
        """
        Apply KDSTheme to matplotlib rcParams.

        Only called if a theme was provided to __init__.
        This allows custom themes to override the default KDS styling.
        """
        if self.theme is not None:
            rcparams = self.theme.to_matplotlib_rcparams()
            plt.rcParams.update(rcparams)

    def _create_figure(self) -> Tuple[Figure, Axes]:
        """Create a new figure with KDS styling."""
        fig, ax = plt.subplots(figsize=self.figsize)
        fig.set_facecolor(
            KDSColors.BACKGROUND_DARK if self.dark_mode else KDSColors.BACKGROUND_LIGHT
        )
        ax.set_facecolor(
            KDSColors.BACKGROUND_DARK if self.dark_mode else KDSColors.BACKGROUND_LIGHT
        )
        # Ensure no grid
        ax.grid(False)
        return fig, ax

    def _get_colors(
        self,
        n: int,
        chart_type: str = "bar",
        values: Optional[List[float]] = None,
        mode: Optional[str] = None
    ) -> List[str]:
        """
        Get n colors with intelligent selection.

        Args:
            n: Number of colors needed
            chart_type: Type of chart (bar, pie, line, etc.)
            values: Data values for sequential coloring
            mode: Override mode (sequential, categorical, diverging, or None for auto)

        Returns:
            List of hex color codes
        """
        if self.intelligent_colors:
            has_negative = values is not None and any(v < 0 for v in values)
            return get_chart_colors(
                chart_type=chart_type,
                n=n,
                values=values,
                mode=mode,
                has_negative=has_negative
            )
        else:
            # Fallback to old palette cycling
            colors = []
            for i in range(n):
                colors.append(KDSColors.PALETTE[i % len(KDSColors.PALETTE)])
            return colors

    def _format_value(self, value: float, is_currency: bool = False) -> str:
        """Format a value for display with smart abbreviations."""
        if not self.smart_numbers:
            return str(value)
        prefix = "$" if is_currency else ""
        return smart_format(value, prefix=prefix)

    def _setup_axis_formatter(self, ax: Axes, axis: str = 'y', is_currency: bool = False) -> None:
        """Setup smart number formatting for an axis."""
        if not self.smart_numbers:
            return

        def formatter(x, pos):
            return format_axis_label(x, is_currency=is_currency)

        if axis == 'y':
            ax.yaxis.set_major_formatter(FuncFormatter(formatter))
        elif axis == 'x':
            ax.xaxis.set_major_formatter(FuncFormatter(formatter))

    def bar(
        self,
        data: Sequence[float],
        labels: Sequence[str],
        title: str = "",
        xlabel: str = "",
        ylabel: str = "",
        horizontal: bool = False,
        show_values: bool = True,
        colors: Optional[List[str]] = None,
    ) -> "KDSChart":
        """
        Create a KDS-compliant bar chart.

        Args:
            data: Values for each bar.
            labels: Labels for each bar.
            title: Chart title.
            xlabel: X-axis label.
            ylabel: Y-axis label.
            horizontal: If True, create horizontal bar chart.
            show_values: If True, show data labels outside bars.
            colors: Optional custom colors. Uses KDS palette if None.

        Returns:
            self for method chaining.
        """
        self.fig, self.ax = self._create_figure()

        if colors is None:
            colors = self._get_colors(len(data), chart_type="bar", values=list(data))

        if horizontal:
            bars = self.ax.barh(labels, data, color=colors)
            if xlabel:
                self.ax.set_xlabel(xlabel)
            if ylabel:
                self.ax.set_ylabel(ylabel)

            # Setup smart formatting for x-axis
            self._setup_axis_formatter(self.ax, axis='x')

            # Data labels outside bars (KDS requirement)
            if show_values:
                for bar, value in zip(bars, data):
                    width = bar.get_width()
                    self.ax.annotate(
                        self._format_value(value),
                        xy=(width, bar.get_y() + bar.get_height() / 2),
                        xytext=(5, 0),
                        textcoords="offset points",
                        ha="left",
                        va="center",
                        fontsize=10,
                        color=KDSColors.TEXT_LIGHT if self.dark_mode else KDSColors.TEXT_DARK,
                    )
        else:
            bars = self.ax.bar(labels, data, color=colors)
            if xlabel:
                self.ax.set_xlabel(xlabel)
            if ylabel:
                self.ax.set_ylabel(ylabel)

            # Setup smart formatting for y-axis
            self._setup_axis_formatter(self.ax, axis='y')

            # Data labels outside bars (KDS requirement)
            if show_values:
                for bar, value in zip(bars, data):
                    height = bar.get_height()
                    self.ax.annotate(
                        self._format_value(value),
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 5),
                        textcoords="offset points",
                        ha="center",
                        va="bottom",
                        fontsize=10,
                        color=KDSColors.TEXT_LIGHT if self.dark_mode else KDSColors.TEXT_DARK,
                    )

        if title:
            self.ax.set_title(title, fontsize=14, fontweight=600, pad=20)

        # Remove spines for cleaner look
        self.ax.spines["top"].set_visible(False)
        self.ax.spines["right"].set_visible(False)

        plt.tight_layout()
        return self

    def line(
        self,
        x_data: Sequence,
        y_data: Union[Sequence[float], List[Sequence[float]]],
        labels: Optional[List[str]] = None,
        title: str = "",
        xlabel: str = "",
        ylabel: str = "",
        show_markers: bool = True,
        colors: Optional[List[str]] = None,
    ) -> "KDSChart":
        """
        Create a KDS-compliant line chart.

        Args:
            x_data: X-axis values.
            y_data: Y-axis values. Can be a single series or list of series.
            labels: Labels for each line (if multiple series).
            title: Chart title.
            xlabel: X-axis label.
            ylabel: Y-axis label.
            show_markers: If True, show data point markers.
            colors: Optional custom colors. Uses KDS palette if None.

        Returns:
            self for method chaining.
        """
        self.fig, self.ax = self._create_figure()

        # Handle single series or multiple series
        if y_data and not isinstance(y_data[0], (list, tuple)):
            y_data = [y_data]
            if labels:
                labels = [labels[0]] if isinstance(labels, list) else [labels]

        if colors is None:
            # Line charts use categorical colors for distinct series
            colors = self._get_colors(len(y_data), chart_type="line")

        for i, series in enumerate(y_data):
            label = labels[i] if labels and i < len(labels) else None
            marker = "o" if show_markers else None
            self.ax.plot(
                x_data,
                series,
                color=colors[i],
                marker=marker,
                markersize=6,
                linewidth=2,
                label=label,
            )

        if xlabel:
            self.ax.set_xlabel(xlabel)
        if ylabel:
            self.ax.set_ylabel(ylabel)
        if title:
            self.ax.set_title(title, fontsize=14, fontweight=600, pad=20)
        if labels:
            self.ax.legend()

        self.ax.spines["top"].set_visible(False)
        self.ax.spines["right"].set_visible(False)

        plt.tight_layout()
        return self

    def pie(
        self,
        data: Sequence[float],
        labels: Sequence[str],
        title: str = "",
        show_percentages: bool = True,
        colors: Optional[List[str]] = None,
        explode: Optional[Sequence[float]] = None,
    ) -> "KDSChart":
        """
        Create a KDS-compliant pie chart.

        Args:
            data: Values for each slice.
            labels: Labels for each slice.
            title: Chart title.
            show_percentages: If True, show percentage labels outside slices.
            colors: Optional custom colors. Uses KDS palette if None.
            explode: Optional sequence of explode values for each slice.

        Returns:
            self for method chaining.
        """
        self.fig, self.ax = self._create_figure()

        if colors is None:
            # Pie charts use sequential coloring - larger slices get darker colors
            colors = self._get_colors(len(data), chart_type="pie", values=list(data))

        # KDS requirement: labels outside slices
        if show_percentages:
            wedges, texts, autotexts = self.ax.pie(
                data,
                labels=labels,
                colors=colors,
                autopct="%1.1f%%",
                explode=explode,
                startangle=90,
                pctdistance=0.85,
                labeldistance=1.15,
            )
            for autotext in autotexts:
                autotext.set_color(KDSColors.TEXT_LIGHT)
                autotext.set_fontsize(9)
                autotext.set_fontweight(500)
        else:
            wedges, texts = self.ax.pie(
                data,
                labels=labels,
                colors=colors,
                explode=explode,
                startangle=90,
                labeldistance=1.15,
            )

        # Style the labels
        for text in texts:
            text.set_color(KDSColors.TEXT_LIGHT if self.dark_mode else KDSColors.TEXT_DARK)
            text.set_fontsize(10)

        if title:
            self.ax.set_title(title, fontsize=14, fontweight=600, pad=20)

        self.ax.axis("equal")  # Equal aspect ratio for circular pie
        plt.tight_layout()
        return self

    def scatter(
        self,
        x_data: Sequence[float],
        y_data: Sequence[float],
        title: str = "",
        xlabel: str = "",
        ylabel: str = "",
        size: Union[float, Sequence[float]] = 50,
        color: Optional[str] = None,
        alpha: float = 0.7,
    ) -> "KDSChart":
        """
        Create a KDS-compliant scatter plot.

        Args:
            x_data: X-axis values.
            y_data: Y-axis values.
            title: Chart title.
            xlabel: X-axis label.
            ylabel: Y-axis label.
            size: Marker size (single value or sequence).
            color: Marker color. Uses Kearney Purple if None.
            alpha: Marker transparency.

        Returns:
            self for method chaining.
        """
        self.fig, self.ax = self._create_figure()

        if color is None:
            color = KDSColors.PRIMARY

        self.ax.scatter(x_data, y_data, s=size, c=color, alpha=alpha)

        if xlabel:
            self.ax.set_xlabel(xlabel)
        if ylabel:
            self.ax.set_ylabel(ylabel)
        if title:
            self.ax.set_title(title, fontsize=14, fontweight=600, pad=20)

        self.ax.spines["top"].set_visible(False)
        self.ax.spines["right"].set_visible(False)

        plt.tight_layout()
        return self

    def grouped_bar(
        self,
        data: List[Sequence[float]],
        group_labels: Sequence[str],
        series_labels: Sequence[str],
        title: str = "",
        xlabel: str = "",
        ylabel: str = "",
        show_values: bool = True,
        colors: Optional[List[str]] = None,
    ) -> "KDSChart":
        """
        Create a KDS-compliant grouped bar chart.

        Args:
            data: List of series, each containing values for each group.
            group_labels: Labels for each group (x-axis).
            series_labels: Labels for each series (legend).
            title: Chart title.
            xlabel: X-axis label.
            ylabel: Y-axis label.
            show_values: If True, show data labels.
            colors: Optional custom colors. Uses KDS palette if None.

        Returns:
            self for method chaining.
        """
        import numpy as np

        self.fig, self.ax = self._create_figure()

        if colors is None:
            colors = self._get_colors(len(data))

        n_groups = len(group_labels)
        n_series = len(data)
        bar_width = 0.8 / n_series
        x = np.arange(n_groups)

        for i, (series, label) in enumerate(zip(data, series_labels)):
            offset = (i - n_series / 2 + 0.5) * bar_width
            bars = self.ax.bar(
                x + offset,
                series,
                bar_width,
                label=label,
                color=colors[i],
            )

            if show_values:
                for bar, value in zip(bars, series):
                    height = bar.get_height()
                    self.ax.annotate(
                        f"{value:,.0f}",
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha="center",
                        va="bottom",
                        fontsize=8,
                        color=KDSColors.TEXT_LIGHT if self.dark_mode else KDSColors.TEXT_DARK,
                    )

        self.ax.set_xticks(x)
        self.ax.set_xticklabels(group_labels)

        if xlabel:
            self.ax.set_xlabel(xlabel)
        if ylabel:
            self.ax.set_ylabel(ylabel)
        if title:
            self.ax.set_title(title, fontsize=14, fontweight=600, pad=20)

        self.ax.legend()
        self.ax.spines["top"].set_visible(False)
        self.ax.spines["right"].set_visible(False)

        plt.tight_layout()
        return self

    def waterfall(
        self,
        data: Sequence[float],
        labels: Sequence[str],
        title: str = "",
        show_connectors: bool = True,
        show_values: bool = True,
        colors: Optional[Dict[str, str]] = None,
    ) -> "KDSChart":
        """
        Create a KDS-compliant waterfall chart.

        Common use: Revenue bridges, variance analysis, P&L waterfalls.

        Args:
            data: Values for each bar. Positive = increase, negative = decrease.
                  First value is typically the starting point.
                  Last value can be the ending total (will be drawn from baseline).
            labels: Labels for each bar.
            title: Chart title.
            show_connectors: If True, show connector lines between bars.
            show_values: If True, show value labels on bars.
            colors: Optional dict with 'increase', 'decrease', 'total' colors.
                    Defaults to KDS purple palette.

        Returns:
            self for method chaining.
        """
        import numpy as np

        self.fig, self.ax = self._create_figure()

        # Default colors using KDS palette
        default_colors = {
            'increase': KDSColors.PRIMARY,      # Kearney Purple for increases
            'decrease': KDSColors.GRAY_400,     # Gray for decreases
            'total': KDSColors.PALETTE[2],      # Dark purple for totals
        }
        if colors:
            default_colors.update(colors)

        n = len(data)
        x = np.arange(n)

        # Calculate cumulative positions for waterfall effect
        cumulative = [0.0]  # Running total
        bar_bottoms = []
        bar_heights = []
        bar_colors = []

        for i, value in enumerate(data):
            if i == 0:
                # First bar: starts from 0
                bar_bottoms.append(0)
                bar_heights.append(value)
                bar_colors.append(default_colors['total'])
                cumulative.append(value)
            elif i == n - 1:
                # Last bar: total bar from 0 to final value
                final_value = cumulative[-1]
                bar_bottoms.append(0)
                bar_heights.append(final_value)
                bar_colors.append(default_colors['total'])
            else:
                # Middle bars: show change from previous cumulative
                prev_cumulative = cumulative[-1]
                if value >= 0:
                    bar_bottoms.append(prev_cumulative)
                    bar_heights.append(value)
                    bar_colors.append(default_colors['increase'])
                else:
                    bar_bottoms.append(prev_cumulative + value)
                    bar_heights.append(abs(value))
                    bar_colors.append(default_colors['decrease'])
                cumulative.append(prev_cumulative + value)

        # Draw bars
        bars = self.ax.bar(x, bar_heights, bottom=bar_bottoms, color=bar_colors, width=0.6)

        # Draw connector lines
        if show_connectors and n > 1:
            for i in range(n - 1):
                if i == n - 2:
                    # Don't draw connector to total bar
                    continue
                y_connect = bar_bottoms[i] + bar_heights[i]
                self.ax.hlines(
                    y=y_connect,
                    xmin=x[i] + 0.3,
                    xmax=x[i + 1] - 0.3,
                    color=KDSColors.GRAY_400,
                    linestyle='--',
                    linewidth=1,
                    alpha=0.7
                )

        # Add value labels
        if show_values:
            text_color = KDSColors.TEXT_LIGHT if self.dark_mode else KDSColors.TEXT_DARK
            for i, (bar, value) in enumerate(zip(bars, data)):
                height = bar.get_height()
                bottom = bar.get_y()
                # Position label above or below bar based on value sign
                if i == 0 or i == n - 1:
                    # Total bars: label above
                    y_pos = bottom + height
                    va = 'bottom'
                    offset = 5
                elif value >= 0:
                    y_pos = bottom + height
                    va = 'bottom'
                    offset = 5
                else:
                    y_pos = bottom
                    va = 'top'
                    offset = -5

                self.ax.annotate(
                    self._format_value(value if i != n - 1 else bar_heights[i]),
                    xy=(bar.get_x() + bar.get_width() / 2, y_pos),
                    xytext=(0, offset),
                    textcoords="offset points",
                    ha="center",
                    va=va,
                    fontsize=10,
                    color=text_color,
                )

        self.ax.set_xticks(x)
        self.ax.set_xticklabels(labels)

        if title:
            self.ax.set_title(title, fontsize=14, fontweight=600, pad=20)

        # Setup smart formatting for y-axis
        self._setup_axis_formatter(self.ax, axis='y')

        self.ax.spines["top"].set_visible(False)
        self.ax.spines["right"].set_visible(False)

        plt.tight_layout()
        return self

    def stacked_bar(
        self,
        data: Dict[str, Sequence[float]],
        labels: Sequence[str],
        title: str = "",
        xlabel: str = "",
        ylabel: str = "",
        horizontal: bool = False,
        show_values: bool = True,
        show_totals: bool = True,
        colors: Optional[List[str]] = None,
    ) -> "KDSChart":
        """
        Create a KDS-compliant stacked bar chart.

        Common use: Part-to-whole comparisons across categories.

        Args:
            data: Dict mapping series names to their values per category.
            labels: Category labels.
            title: Chart title.
            xlabel: X-axis label.
            ylabel: Y-axis label.
            horizontal: If True, create horizontal stacked bars.
            show_values: If True, show values inside each segment.
            show_totals: If True, show total at end of each bar.
            colors: Optional custom colors for series.

        Returns:
            self for method chaining.
        """
        import numpy as np

        self.fig, self.ax = self._create_figure()

        series_names = list(data.keys())
        n_series = len(series_names)
        n_categories = len(labels)

        if colors is None:
            colors = self._get_colors(n_series, chart_type="bar")

        x = np.arange(n_categories)
        text_color = KDSColors.TEXT_LIGHT if self.dark_mode else KDSColors.TEXT_DARK

        # Calculate totals for each category
        totals = [sum(data[series][i] for series in series_names) for i in range(n_categories)]

        # Stack the bars
        bottom = np.zeros(n_categories)
        for idx, series_name in enumerate(series_names):
            values = list(data[series_name])
            if horizontal:
                bars = self.ax.barh(x, values, left=bottom, label=series_name, color=colors[idx], height=0.6)
            else:
                bars = self.ax.bar(x, values, bottom=bottom, label=series_name, color=colors[idx], width=0.6)

            # Add value labels inside segments
            if show_values:
                for i, (bar, value) in enumerate(zip(bars, values)):
                    if value > 0:  # Only show if segment is visible
                        if horizontal:
                            cx = bar.get_x() + bar.get_width() / 2
                            cy = bar.get_y() + bar.get_height() / 2
                        else:
                            cx = bar.get_x() + bar.get_width() / 2
                            cy = bar.get_y() + bar.get_height() / 2

                        # Only show label if segment is large enough
                        segment_ratio = value / totals[i] if totals[i] > 0 else 0
                        if segment_ratio > 0.08:  # Show if > 8% of total
                            self.ax.annotate(
                                self._format_value(value),
                                xy=(cx, cy),
                                ha="center",
                                va="center",
                                fontsize=9,
                                color=KDSColors.TEXT_LIGHT,
                                fontweight=500,
                            )

            bottom = bottom + np.array(values)

        # Add total labels
        if show_totals:
            for i, total in enumerate(totals):
                if horizontal:
                    self.ax.annotate(
                        self._format_value(total),
                        xy=(total, i),
                        xytext=(5, 0),
                        textcoords="offset points",
                        ha="left",
                        va="center",
                        fontsize=10,
                        color=text_color,
                        fontweight=600,
                    )
                else:
                    self.ax.annotate(
                        self._format_value(total),
                        xy=(i, total),
                        xytext=(0, 5),
                        textcoords="offset points",
                        ha="center",
                        va="bottom",
                        fontsize=10,
                        color=text_color,
                        fontweight=600,
                    )

        if horizontal:
            self.ax.set_yticks(x)
            self.ax.set_yticklabels(labels)
            self._setup_axis_formatter(self.ax, axis='x')
        else:
            self.ax.set_xticks(x)
            self.ax.set_xticklabels(labels)
            self._setup_axis_formatter(self.ax, axis='y')

        if xlabel:
            self.ax.set_xlabel(xlabel)
        if ylabel:
            self.ax.set_ylabel(ylabel)
        if title:
            self.ax.set_title(title, fontsize=14, fontweight=600, pad=20)

        self.ax.legend(loc='upper right')
        self.ax.spines["top"].set_visible(False)
        self.ax.spines["right"].set_visible(False)

        plt.tight_layout()
        return self

    def combo(
        self,
        bar_data: Sequence[float],
        line_data: Sequence[float],
        labels: Sequence[str],
        title: str = "",
        bar_label: str = "",
        line_label: str = "",
        xlabel: str = "",
        bar_ylabel: str = "",
        line_ylabel: str = "",
        show_values: bool = True,
        bar_color: Optional[str] = None,
        line_color: Optional[str] = None,
    ) -> "KDSChart":
        """
        Create a KDS-compliant combo chart with bars and line overlay.

        Common use: Revenue vs margin, volume vs price, actuals vs targets.

        Uses dual y-axes: left for bars, right for line.

        Args:
            bar_data: Values for bars (left y-axis).
            line_data: Values for line (right y-axis).
            labels: Category labels (x-axis).
            title: Chart title.
            bar_label: Label for bar series (legend).
            line_label: Label for line series (legend).
            xlabel: X-axis label.
            bar_ylabel: Left y-axis label (for bars).
            line_ylabel: Right y-axis label (for line).
            show_values: If True, show value labels.
            bar_color: Custom color for bars.
            line_color: Custom color for line.

        Returns:
            self for method chaining.
        """
        import numpy as np

        self.fig, self.ax = self._create_figure()

        # Colors
        if bar_color is None:
            bar_color = KDSColors.PRIMARY
        if line_color is None:
            line_color = KDSColors.PALETTE[1]  # Light purple

        x = np.arange(len(labels))
        text_color = KDSColors.TEXT_LIGHT if self.dark_mode else KDSColors.TEXT_DARK

        # Create bars on primary axis
        bars = self.ax.bar(x, bar_data, color=bar_color, width=0.6, label=bar_label, alpha=0.9)

        # Add bar value labels
        if show_values:
            for bar, value in zip(bars, bar_data):
                height = bar.get_height()
                self.ax.annotate(
                    self._format_value(value),
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 5),
                    textcoords="offset points",
                    ha="center",
                    va="bottom",
                    fontsize=9,
                    color=text_color,
                )

        self.ax.set_xticks(x)
        self.ax.set_xticklabels(labels)
        if bar_ylabel:
            self.ax.set_ylabel(bar_ylabel, color=bar_color)
        self.ax.tick_params(axis='y', labelcolor=bar_color)
        self._setup_axis_formatter(self.ax, axis='y')

        # Create secondary axis for line
        ax2 = self.ax.twinx()
        ax2.set_facecolor('none')  # Transparent background

        # Plot line on secondary axis
        line = ax2.plot(x, line_data, color=line_color, marker='o', markersize=8,
                       linewidth=2.5, label=line_label)

        # Add line value labels
        if show_values:
            for i, value in enumerate(line_data):
                ax2.annotate(
                    self._format_value(value),
                    xy=(i, value),
                    xytext=(0, 10),
                    textcoords="offset points",
                    ha="center",
                    va="bottom",
                    fontsize=9,
                    color=line_color,
                    fontweight=500,
                )

        if line_ylabel:
            ax2.set_ylabel(line_ylabel, color=line_color)
        ax2.tick_params(axis='y', labelcolor=line_color)
        ax2.spines["top"].set_visible(False)

        if xlabel:
            self.ax.set_xlabel(xlabel)
        if title:
            self.ax.set_title(title, fontsize=14, fontweight=600, pad=20)

        # Combined legend
        lines1, labels1 = self.ax.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        if bar_label or line_label:
            self.ax.legend(lines1 + lines2, labels1 + labels2, loc='upper left')

        self.ax.spines["top"].set_visible(False)
        self.ax.spines["right"].set_visible(False)

        plt.tight_layout()
        return self

    def bullet(
        self,
        actual: float,
        target: float,
        ranges: Sequence[float],
        title: str = "",
        label: str = "",
        horizontal: bool = True,
        show_values: bool = True,
        range_colors: Optional[List[str]] = None,
    ) -> "KDSChart":
        """
        Create a KDS-compliant bullet chart.

        Common use: KPI performance vs target with context ranges.

        Args:
            actual: The actual/current value (shown as main bar).
            target: The target value (shown as marker line).
            ranges: Threshold values for background ranges (poor/ok/good).
            horizontal: If True, horizontal bullet (default). Vertical otherwise.
            show_values: If True, show value labels.
            range_colors: Colors for range bands. Defaults to grays.

        Returns:
            self for method chaining.
        """
        self.fig, self.ax = self._create_figure()

        # Default range colors (light to dark grays)
        if range_colors is None:
            range_colors = [KDSColors.GRAY_200, KDSColors.GRAY_300, KDSColors.GRAY_400]

        # Ensure we have enough colors
        while len(range_colors) < len(ranges):
            range_colors.append(KDSColors.GRAY_400)

        text_color = KDSColors.TEXT_LIGHT if self.dark_mode else KDSColors.TEXT_DARK
        sorted_ranges = sorted(ranges)

        if horizontal:
            # Draw range bands (background)
            prev = 0
            for i, r in enumerate(sorted_ranges):
                self.ax.barh(0, r - prev, left=prev, height=0.5,
                            color=range_colors[i], alpha=0.6)
                prev = r

            # Draw actual value bar
            self.ax.barh(0, actual, height=0.25, color=KDSColors.PRIMARY)

            # Draw target marker
            self.ax.axvline(x=target, ymin=0.25, ymax=0.75,
                          color=KDSColors.TEXT_DARK, linewidth=3)

            # Labels
            if show_values:
                self.ax.annotate(
                    f"Actual: {self._format_value(actual)}",
                    xy=(actual, 0.15),
                    xytext=(5, 0),
                    textcoords="offset points",
                    ha="left",
                    va="center",
                    fontsize=10,
                    color=KDSColors.PRIMARY,
                    fontweight=600,
                )
                self.ax.annotate(
                    f"Target: {self._format_value(target)}",
                    xy=(target, -0.15),
                    xytext=(5, 0),
                    textcoords="offset points",
                    ha="left",
                    va="center",
                    fontsize=10,
                    color=text_color,
                )

            self.ax.set_ylim(-0.4, 0.4)
            self.ax.set_xlim(0, max(sorted_ranges[-1], actual, target) * 1.1)
            self.ax.set_yticks([])
            self._setup_axis_formatter(self.ax, axis='x')

        else:
            # Vertical bullet chart
            prev = 0
            for i, r in enumerate(sorted_ranges):
                self.ax.bar(0, r - prev, bottom=prev, width=0.5,
                           color=range_colors[i], alpha=0.6)
                prev = r

            # Draw actual value bar
            self.ax.bar(0, actual, width=0.25, color=KDSColors.PRIMARY)

            # Draw target marker
            self.ax.axhline(y=target, xmin=0.25, xmax=0.75,
                          color=KDSColors.TEXT_DARK, linewidth=3)

            if show_values:
                self.ax.annotate(
                    f"Actual: {self._format_value(actual)}",
                    xy=(0.15, actual),
                    xytext=(0, 5),
                    textcoords="offset points",
                    ha="center",
                    va="bottom",
                    fontsize=10,
                    color=KDSColors.PRIMARY,
                    fontweight=600,
                )
                self.ax.annotate(
                    f"Target: {self._format_value(target)}",
                    xy=(-0.15, target),
                    xytext=(0, 5),
                    textcoords="offset points",
                    ha="center",
                    va="bottom",
                    fontsize=10,
                    color=text_color,
                )

            self.ax.set_xlim(-0.4, 0.4)
            self.ax.set_ylim(0, max(sorted_ranges[-1], actual, target) * 1.1)
            self.ax.set_xticks([])
            self._setup_axis_formatter(self.ax, axis='y')

        if title:
            self.ax.set_title(title, fontsize=14, fontweight=600, pad=20)
        if label:
            if horizontal:
                self.ax.set_xlabel(label)
            else:
                self.ax.set_ylabel(label)

        self.ax.spines["top"].set_visible(False)
        self.ax.spines["right"].set_visible(False)
        self.ax.spines["left"].set_visible(False)
        self.ax.spines["bottom"].set_visible(False)

        plt.tight_layout()
        return self

    def histogram(
        self,
        data: Sequence[float],
        bins: Union[int, Sequence[float]] = 10,
        title: str = "",
        xlabel: str = "",
        ylabel: str = "Frequency",
        show_values: bool = False,
        color: Optional[str] = None,
    ) -> "KDSChart":
        """
        Create a KDS-compliant histogram.

        Common use: Distribution analysis, frequency analysis.

        Args:
            data: Raw data values to bin and count.
            bins: Number of bins or sequence of bin edges.
            title: Chart title.
            xlabel: X-axis label.
            ylabel: Y-axis label.
            show_values: If True, show count labels on bars.
            color: Custom bar color.

        Returns:
            self for method chaining.
        """
        self.fig, self.ax = self._create_figure()

        if color is None:
            color = KDSColors.PRIMARY

        text_color = KDSColors.TEXT_LIGHT if self.dark_mode else KDSColors.TEXT_DARK

        # Create histogram
        n, bin_edges, patches = self.ax.hist(
            data, bins=bins, color=color, edgecolor=KDSColors.BACKGROUND_DARK,
            linewidth=1, alpha=0.9
        )

        # Add value labels
        if show_values:
            for count, patch in zip(n, patches):
                if count > 0:
                    x = patch.get_x() + patch.get_width() / 2
                    y = patch.get_height()
                    self.ax.annotate(
                        f"{int(count)}",
                        xy=(x, y),
                        xytext=(0, 5),
                        textcoords="offset points",
                        ha="center",
                        va="bottom",
                        fontsize=9,
                        color=text_color,
                    )

        if xlabel:
            self.ax.set_xlabel(xlabel)
        if ylabel:
            self.ax.set_ylabel(ylabel)
        if title:
            self.ax.set_title(title, fontsize=14, fontweight=600, pad=20)

        self._setup_axis_formatter(self.ax, axis='x')
        self._setup_axis_formatter(self.ax, axis='y')

        self.ax.spines["top"].set_visible(False)
        self.ax.spines["right"].set_visible(False)

        plt.tight_layout()
        return self

    def heatmap(
        self,
        data: Sequence[Sequence[float]],
        row_labels: Optional[Sequence[str]] = None,
        col_labels: Optional[Sequence[str]] = None,
        title: str = "",
        show_values: bool = True,
        cmap: Optional[str] = None,
        vmin: Optional[float] = None,
        vmax: Optional[float] = None,
    ) -> "KDSChart":
        """
        Create a KDS-compliant heatmap.

        Common use: Correlation matrices, cross-tabulations, intensity grids.

        Args:
            data: 2D array of values (list of lists or numpy array).
            row_labels: Labels for rows (y-axis).
            col_labels: Labels for columns (x-axis).
            title: Chart title.
            show_values: If True, show values in cells.
            cmap: Colormap name. Defaults to purple gradient.
            vmin: Minimum value for color scale.
            vmax: Maximum value for color scale.

        Returns:
            self for method chaining.
        """
        import numpy as np

        self.fig, self.ax = self._create_figure()

        data_array = np.array(data)
        text_color = KDSColors.TEXT_LIGHT if self.dark_mode else KDSColors.TEXT_DARK

        # KDS-compliant purple colormap
        if cmap is None:
            from matplotlib.colors import LinearSegmentedColormap
            colors = [KDSColors.BACKGROUND_DARK, KDSColors.PRIMARY, "#B266FF"]
            cmap = LinearSegmentedColormap.from_list("kds_purple", colors)

        im = self.ax.imshow(data_array, cmap=cmap, aspect='auto', vmin=vmin, vmax=vmax)

        # Add colorbar
        cbar = self.fig.colorbar(im, ax=self.ax, shrink=0.8)
        cbar.ax.yaxis.set_tick_params(color=text_color)
        plt.setp(plt.getp(cbar.ax.axes, 'yticklabels'), color=text_color)

        # Set labels
        if col_labels is not None:
            self.ax.set_xticks(range(len(col_labels)))
            self.ax.set_xticklabels(col_labels, rotation=45, ha='right')
        if row_labels is not None:
            self.ax.set_yticks(range(len(row_labels)))
            self.ax.set_yticklabels(row_labels)

        # Show values in cells
        if show_values:
            for i in range(data_array.shape[0]):
                for j in range(data_array.shape[1]):
                    val = data_array[i, j]
                    # Choose text color based on cell brightness
                    cell_color = "white" if val > (data_array.max() + data_array.min()) / 2 else "black"
                    formatted_val = self._format_value(val) if self.smart_numbers else f"{val:.2f}"
                    self.ax.text(j, i, formatted_val, ha="center", va="center",
                                color=cell_color, fontsize=9)

        if title:
            self.ax.set_title(title, fontsize=14, fontweight=600, pad=20)

        plt.tight_layout()
        return self

    def boxplot(
        self,
        data: Union[Sequence[float], Sequence[Sequence[float]]],
        labels: Optional[Sequence[str]] = None,
        title: str = "",
        xlabel: str = "",
        ylabel: str = "",
        show_outliers: bool = True,
        horizontal: bool = False,
        color: Optional[str] = None,
    ) -> "KDSChart":
        """
        Create a KDS-compliant box plot.

        Common use: Distribution comparison, outlier detection, statistical summary.

        Args:
            data: Single dataset or list of datasets to compare.
            labels: Labels for each box.
            title: Chart title.
            xlabel: X-axis label.
            ylabel: Y-axis label.
            show_outliers: If True, show outlier points.
            horizontal: If True, draw horizontal boxes.
            color: Box fill color.

        Returns:
            self for method chaining.
        """
        self.fig, self.ax = self._create_figure()

        if color is None:
            color = KDSColors.PRIMARY

        text_color = KDSColors.TEXT_LIGHT if self.dark_mode else KDSColors.TEXT_DARK

        # Ensure data is list of lists for multiple boxes
        if isinstance(data[0], (int, float)):
            data = [data]

        bp = self.ax.boxplot(
            data,
            vert=not horizontal,
            patch_artist=True,
            showfliers=show_outliers,
            labels=labels,
        )

        # Style the boxes
        for patch in bp['boxes']:
            patch.set_facecolor(color)
            patch.set_alpha(0.7)
        for whisker in bp['whiskers']:
            whisker.set_color(text_color)
        for cap in bp['caps']:
            cap.set_color(text_color)
        for median in bp['medians']:
            median.set_color(KDSColors.TEXT_LIGHT)
            median.set_linewidth(2)
        if show_outliers:
            for flier in bp['fliers']:
                flier.set_markerfacecolor(color)
                flier.set_markeredgecolor(text_color)

        if xlabel:
            self.ax.set_xlabel(xlabel)
        if ylabel:
            self.ax.set_ylabel(ylabel)
        if title:
            self.ax.set_title(title, fontsize=14, fontweight=600, pad=20)

        self.ax.spines["top"].set_visible(False)
        self.ax.spines["right"].set_visible(False)

        plt.tight_layout()
        return self

    def area(
        self,
        x_data: Sequence,
        y_data: Union[Sequence[float], List[Sequence[float]]],
        title: str = "",
        xlabel: str = "",
        ylabel: str = "",
        labels: Optional[Sequence[str]] = None,
        stacked: bool = False,
        alpha: float = 0.7,
        colors: Optional[List[str]] = None,
    ) -> "KDSChart":
        """
        Create a KDS-compliant area chart.

        Common use: Time series with magnitude, cumulative totals, part-to-whole over time.

        Args:
            x_data: X-axis values (e.g., dates, categories).
            y_data: Y values - single series or list of series for stacked.
            title: Chart title.
            xlabel: X-axis label.
            ylabel: Y-axis label.
            labels: Labels for legend (if multiple series).
            stacked: If True and multiple series, stack the areas.
            alpha: Fill transparency.
            colors: Custom colors for each series.

        Returns:
            self for method chaining.
        """
        self.fig, self.ax = self._create_figure()

        # Normalize y_data to list of series
        if not isinstance(y_data[0], (list, tuple)):
            y_data = [y_data]

        if colors is None:
            colors = self._get_colors(len(y_data), chart_type="area")

        if stacked and len(y_data) > 1:
            self.ax.stackplot(x_data, *y_data, labels=labels, colors=colors, alpha=alpha)
        else:
            for i, series in enumerate(y_data):
                label = labels[i] if labels and i < len(labels) else None
                self.ax.fill_between(x_data, series, alpha=alpha, color=colors[i], label=label)
                self.ax.plot(x_data, series, color=colors[i], linewidth=2)

        if xlabel:
            self.ax.set_xlabel(xlabel)
        if ylabel:
            self.ax.set_ylabel(ylabel)
        if title:
            self.ax.set_title(title, fontsize=14, fontweight=600, pad=20)
        if labels:
            self.ax.legend()

        self._setup_axis_formatter(self.ax, axis='y')

        self.ax.spines["top"].set_visible(False)
        self.ax.spines["right"].set_visible(False)

        plt.tight_layout()
        return self

    def donut(
        self,
        data: Sequence[float],
        labels: Sequence[str],
        title: str = "",
        show_percentages: bool = True,
        colors: Optional[List[str]] = None,
        center_text: Optional[str] = None,
        center_value: Optional[str] = None,
    ) -> "KDSChart":
        """
        Create a KDS-compliant donut chart.

        Common use: Part-to-whole with center metric, KPI display with breakdown.

        Args:
            data: Values for each slice.
            labels: Labels for each slice.
            title: Chart title.
            show_percentages: If True, show percentage labels.
            colors: Optional custom colors. Uses KDS palette if None.
            center_text: Optional label text in center of donut.
            center_value: Optional value text in center of donut.

        Returns:
            self for method chaining.
        """
        self.fig, self.ax = self._create_figure()

        if colors is None:
            colors = self._get_colors(len(data), chart_type="pie", values=list(data))

        text_color = KDSColors.TEXT_LIGHT if self.dark_mode else KDSColors.TEXT_DARK

        # Create donut (pie with white circle in center)
        if show_percentages:
            wedges, texts, autotexts = self.ax.pie(
                data,
                labels=labels,
                colors=colors,
                autopct="%1.1f%%",
                startangle=90,
                pctdistance=0.75,
                labeldistance=1.15,
                wedgeprops=dict(width=0.5, edgecolor=KDSColors.BACKGROUND_DARK if self.dark_mode else KDSColors.BACKGROUND_LIGHT),
            )
            for autotext in autotexts:
                autotext.set_color(text_color)
                autotext.set_fontsize(9)
                autotext.set_fontweight(500)
        else:
            wedges, texts = self.ax.pie(
                data,
                labels=labels,
                colors=colors,
                startangle=90,
                labeldistance=1.15,
                wedgeprops=dict(width=0.5, edgecolor=KDSColors.BACKGROUND_DARK if self.dark_mode else KDSColors.BACKGROUND_LIGHT),
            )

        # Style the labels
        for text in texts:
            text.set_color(text_color)
            text.set_fontsize(10)

        # Add center text
        if center_value or center_text:
            if center_value:
                self.ax.text(0, 0.05, center_value, ha='center', va='center',
                            fontsize=24, fontweight='bold', color=text_color)
            if center_text:
                y_pos = -0.15 if center_value else 0
                self.ax.text(0, y_pos, center_text, ha='center', va='center',
                            fontsize=12, color=KDSColors.GRAY_400)

        if title:
            self.ax.set_title(title, fontsize=14, fontweight=600, pad=20)

        self.ax.axis("equal")
        plt.tight_layout()
        return self

    def sankey(
        self,
        flows: Sequence[float],
        labels: Sequence[str],
        orientations: Optional[Sequence[int]] = None,
        title: str = "",
        unit: str = "",
        color: Optional[str] = None,
    ) -> "KDSChart":
        """
        Create a KDS-compliant Sankey diagram.

        Common use: Flow visualization, budget allocation, process flows,
        energy/resource transfers.

        Args:
            flows: Flow values (positive = in, negative = out). First value
                   is the trunk/main flow, subsequent values branch off.
            labels: Labels for each flow connection point.
            orientations: Direction of each flow (-1=left, 0=down, 1=right).
                         If None, auto-assigns based on flow sign.
            title: Chart title.
            unit: Unit label for flow values (e.g., "MW", "$M").
            color: Main flow color. Uses Kearney Purple if None.

        Returns:
            self for method chaining.

        Example:
            # Budget allocation example
            chart.sankey(
                flows=[100, -30, -40, -20, -10],  # 100 in, distributed out
                labels=['Budget', 'Marketing', 'R&D', 'Operations', 'Admin'],
                title='Budget Allocation Flow',
                unit='$M'
            )
        """
        from matplotlib.sankey import Sankey

        self.fig, self.ax = self._create_figure()

        if color is None:
            color = KDSColors.PRIMARY

        text_color = KDSColors.TEXT_LIGHT if self.dark_mode else KDSColors.TEXT_DARK

        # Auto-assign orientations if not provided
        if orientations is None:
            orientations = []
            for i, flow in enumerate(flows):
                if i == 0:
                    orientations.append(0)  # Main trunk goes down
                elif flow >= 0:
                    orientations.append(-1)  # Inputs from left
                else:
                    orientations.append(1)  # Outputs to right

        # Create Sankey diagram
        sankey = Sankey(
            ax=self.ax,
            unit=unit,
            scale=1.0 / max(abs(f) for f in flows) * 0.5,
            offset=0.3,
            head_angle=120,
            format='%.1f',
            gap=0.3,
        )

        sankey.add(
            flows=list(flows),
            labels=list(labels),
            orientations=list(orientations),
            facecolor=color,
            edgecolor=text_color,
            alpha=0.8,
        )

        diagrams = sankey.finish()

        # Style the text
        for text in self.ax.texts:
            text.set_color(text_color)
            text.set_fontsize(10)

        if title:
            self.ax.set_title(title, fontsize=14, fontweight=600, pad=20)

        self.ax.axis("off")
        plt.tight_layout()
        return self

    def save(
        self,
        path: Union[str, Path],
        transparent: bool = False,
        format: Optional[str] = None,
    ) -> Path:
        """
        Save the chart to a file.

        Args:
            path: Output file path. If no extension, uses default_format.
            transparent: If True, save with transparent background.
            format: Output format ('svg', 'png', 'pdf'). Overrides path extension.

        Returns:
            Path to the saved file.

        Raises:
            ValueError: If no chart has been created yet.
        """
        if self.fig is None:
            raise ValueError("No chart created. Call a chart method first (bar, line, pie, etc.)")

        path = Path(path)

        # Determine format - priority: explicit format > path extension > default
        if format is not None:
            output_format = format.lower()
        elif path.suffix:
            output_format = path.suffix.lstrip('.').lower()
        else:
            output_format = self.default_format

        # Ensure path has correct extension
        if not path.suffix or path.suffix.lstrip('.').lower() != output_format:
            path = path.with_suffix(f'.{output_format}')

        path.parent.mkdir(parents=True, exist_ok=True)

        # SVG-specific settings
        if output_format == 'svg':
            self.fig.savefig(
                path,
                format='svg',
                bbox_inches="tight",
                facecolor=self.fig.get_facecolor() if not transparent else "none",
                edgecolor="none",
                transparent=transparent,
            )
        else:
            self.fig.savefig(
                path,
                dpi=self.dpi,
                format=output_format,
                bbox_inches="tight",
                facecolor=self.fig.get_facecolor() if not transparent else "none",
                edgecolor="none",
                transparent=transparent,
            )

        plt.close(self.fig)
        self.fig = None
        self.ax = None

        logger.info(f"Chart saved to {path} ({output_format.upper()})")
        return path

    def show(self) -> None:
        """Display the chart (for interactive use)."""
        if self.fig is None:
            raise ValueError("No chart created. Call a chart method first.")
        plt.show()

    def close(self) -> None:
        """Close the current figure and free resources."""
        if self.fig is not None:
            plt.close(self.fig)
            self.fig = None
            self.ax = None

    def save_both(
        self,
        base_path: Union[str, Path],
        transparent: bool = False,
    ) -> Tuple[Path, Path]:
        """
        Save the chart in both SVG and PNG formats.

        Useful when you need both formats (SVG for editing, PNG for embedding).

        Args:
            base_path: Base output path (without extension).
            transparent: If True, save with transparent background.

        Returns:
            Tuple of (svg_path, png_path).
        """
        base_path = Path(base_path).with_suffix('')  # Remove any extension

        # Save SVG first (need to recreate figure for second save)
        # Instead, we'll save to a temp buffer approach
        if self.fig is None:
            raise ValueError("No chart created. Call a chart method first.")

        svg_path = base_path.with_suffix('.svg')
        png_path = base_path.with_suffix('.png')

        svg_path.parent.mkdir(parents=True, exist_ok=True)

        # Save SVG
        self.fig.savefig(
            svg_path,
            format='svg',
            bbox_inches="tight",
            facecolor=self.fig.get_facecolor() if not transparent else "none",
            edgecolor="none",
            transparent=transparent,
        )

        # Save PNG
        self.fig.savefig(
            png_path,
            dpi=self.dpi,
            format='png',
            bbox_inches="tight",
            facecolor=self.fig.get_facecolor() if not transparent else "none",
            edgecolor="none",
            transparent=transparent,
        )

        plt.close(self.fig)
        self.fig = None
        self.ax = None

        logger.info(f"Chart saved to {svg_path} and {png_path}")
        return (svg_path, png_path)


def recommend_chart_type(data_story: str, data_shape: Optional[Dict[str, int]] = None) -> str:
    """
    Suggest chart type based on story intent and data characteristics.

    Args:
        data_story: One of:
            - "comparison" (compare values across categories)
            - "change_over_time" (show trends)
            - "part_to_whole" (show composition)
            - "correlation" (show relationships)
            - "distribution" (show frequency/spread)
            - "bridge" (show incremental changes)
            - "performance" (show actual vs target)
            - "dual_metric" (show two related metrics)
        data_shape: Optional dict with hints like:
            - "series": number of data series (1, 2, many)
            - "categories": number of categories
            - "has_negative": whether data includes negative values

    Returns:
        Recommended chart type string.
    """
    recommendations = {
        "comparison": "bar",
        "change_over_time": "line",
        "part_to_whole": "pie",
        "correlation": "scatter",
        "distribution": "histogram",
        "bridge": "waterfall",
        "performance": "bullet",
        "dual_metric": "combo",
    }

    chart_type = recommendations.get(data_story, "bar")

    # Refine based on data shape
    if data_shape:
        if data_story == "comparison" and data_shape.get("series", 1) > 1:
            chart_type = "grouped_bar"
        elif data_story == "part_to_whole" and data_shape.get("categories", 0) > 5:
            chart_type = "stacked_bar"

    return chart_type


def main():
    """Demo of KDSChart capabilities."""
    import random

    # Example usage with size presets
    print("Creating charts with KDSChart...")
    print("\n--- Original Chart Types ---")

    # Bar chart - presentation size (default), SVG output
    chart = KDSChart(size_preset="presentation")
    data = [120, 85, 95, 110, 75]
    labels = ["North", "South", "East", "West", "Central"]
    chart.bar(data, labels, title="Revenue by Region ($ millions)")
    chart.save("outputs/charts/demo_bar")  # Saves as SVG by default
    print("  Saved: demo_bar.svg (presentation size)")

    # Line chart - document size, PNG output
    chart = KDSChart(size_preset="document", default_format="png")
    x = ["Q1", "Q2", "Q3", "Q4"]
    y = [[100, 120, 115, 140], [80, 95, 100, 110]]
    chart.line(x, y, labels=["2024", "2023"], title="Quarterly Performance")
    chart.save("outputs/charts/demo_line")
    print("  Saved: demo_line.png (document size)")

    # Pie chart - square size, both formats
    chart = KDSChart(size_preset="square")
    data = [35, 25, 20, 15, 5]
    labels = ["Product A", "Product B", "Product C", "Product D", "Other"]
    chart.pie(data, labels, title="Market Share")
    chart.save_both("outputs/charts/demo_pie")
    print("  Saved: demo_pie.svg and demo_pie.png (square size)")

    # Custom size example
    chart = KDSChart(size_preset="1400x800")
    data = [45, 62, 38, 55, 70]
    labels = ["Jan", "Feb", "Mar", "Apr", "May"]
    chart.bar(data, labels, title="Monthly Sales")
    chart.save("outputs/charts/demo_custom.svg")
    print("  Saved: demo_custom.svg (custom 1400x800)")

    print("\n--- New Chart Types (v2) ---")

    # Waterfall chart - Revenue bridge
    chart = KDSChart(size_preset="presentation")
    chart.waterfall(
        data=[100, 20, -15, 30, -10, 125],
        labels=['Q3 Start', 'Growth', 'Churn', 'Upsell', 'Costs', 'Q4 End'],
        title='Revenue Bridge Q3 to Q4 ($ millions)'
    )
    chart.save("outputs/charts/demo_waterfall.svg")
    print("  Saved: demo_waterfall.svg (waterfall chart)")

    # Stacked bar chart - Revenue by product
    chart = KDSChart(size_preset="presentation")
    chart.stacked_bar(
        data={
            'Product A': [30, 35, 40, 45],
            'Product B': [25, 30, 28, 35],
            'Product C': [15, 18, 22, 25],
        },
        labels=['Q1', 'Q2', 'Q3', 'Q4'],
        title='Revenue by Product ($ millions)'
    )
    chart.save("outputs/charts/demo_stacked.svg")
    print("  Saved: demo_stacked.svg (stacked bar chart)")

    # Combo chart - Revenue vs Margin
    chart = KDSChart(size_preset="presentation")
    chart.combo(
        bar_data=[100, 120, 140, 160],
        line_data=[10, 12, 11, 15],
        labels=['Q1', 'Q2', 'Q3', 'Q4'],
        title='Revenue vs Margin',
        bar_label='Revenue ($M)',
        line_label='Margin (%)',
        bar_ylabel='Revenue',
        line_ylabel='Margin %'
    )
    chart.save("outputs/charts/demo_combo.svg")
    print("  Saved: demo_combo.svg (combo chart)")

    # Bullet chart - Sales performance
    chart = KDSChart(size_preset="document")
    chart.bullet(
        actual=85,
        target=100,
        ranges=[50, 75, 100],
        title='Sales Performance vs Target'
    )
    chart.save("outputs/charts/demo_bullet.svg")
    print("  Saved: demo_bullet.svg (bullet chart)")

    # Histogram - Distribution analysis
    chart = KDSChart(size_preset="document")
    random.seed(42)
    dist_data = [random.gauss(50, 15) for _ in range(200)]
    chart.histogram(
        data=dist_data,
        bins=15,
        title='Customer Age Distribution',
        xlabel='Age',
        ylabel='Count'
    )
    chart.save("outputs/charts/demo_histogram.svg")
    print("  Saved: demo_histogram.svg (histogram)")

    print("\n--- Chart Recommendation Demo ---")
    stories = ["bridge", "distribution", "performance", "dual_metric", "comparison"]
    for story in stories:
        rec = recommend_chart_type(story)
        print(f"  '{story}' -> {rec}")

    # Test with data shape
    rec = recommend_chart_type("comparison", {"series": 3})
    print(f"  'comparison' with 3 series -> {rec}")

    print("\nDemo charts saved to outputs/charts/")


if __name__ == "__main__":
    main()
