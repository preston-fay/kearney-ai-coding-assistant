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
from typing import List, Optional, Sequence, Tuple, Union

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
        self.fig: Optional[Figure] = None
        self.ax: Optional[Axes] = None
        self._setup_style()

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


def main():
    """Demo of KDSChart capabilities."""
    # Example usage with size presets
    print("Creating charts with KDSChart...")

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

    print("\nDemo charts saved to outputs/charts/")


if __name__ == "__main__":
    main()
