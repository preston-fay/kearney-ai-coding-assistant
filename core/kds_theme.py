"""
Kearney Design System Theme - Centralized Brand Tokens

Provides a frozen dataclass containing all Kearney brand tokens that can be
exported to various formats (CSS, matplotlib, Plotly, Streamlit).

Usage:
    from core.kds_theme import KDSTheme

    theme = KDSTheme()
    css = theme.to_css_variables()
    rcparams = theme.to_matplotlib_rcparams()

Brand Rules (Non-Negotiable):
    - Primary color: Kearney Purple (#7823DC)
    - FORBIDDEN: Any green colors (#00FF00, #008000, #2E7D32, #4CAF50, etc.)
    - Typography: Inter font (Arial fallback)
    - Dark mode default: Background #1E1E1E
"""

from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass(frozen=True)
class KDSTheme:
    """
    Kearney Design System theme with brand-compliant tokens.

    This is a frozen dataclass - values cannot be modified after creation.
    Use this as the single source of truth for all Kearney brand styling.
    """

    # Primary Colors - Kearney Purple is canonical
    primary: str = "#7823DC"
    primary_light: str = "#9B4DCA"
    primary_dark: str = "#5C1BA8"
    primary_pale: str = "#D4A5FF"

    # Secondary Colors (NO GREEN - forbidden by brand_guard.py)
    secondary: str = "#B266FF"
    accent: str = "#CE93D8"

    # Semantic Colors
    positive: str = "#D4A5FF"  # Light purple for positive (NOT green)
    negative: str = "#FF6F61"  # Coral for negative
    warning: str = "#FFB74D"   # Amber for warnings
    info: str = "#64B5F6"      # Light blue for info

    # Neutrals
    background_dark: str = "#1E1E1E"
    background_light: str = "#FFFFFF"
    surface_dark: str = "#2D2D2D"
    surface_light: str = "#F5F5F5"

    # Text Colors
    text_light: str = "#FFFFFF"
    text_dark: str = "#333333"
    text_muted: str = "#666666"

    # Gray Scale
    gray_100: str = "#F5F5F5"
    gray_200: str = "#E0E0E0"
    gray_300: str = "#CCCCCC"
    gray_400: str = "#999999"
    gray_500: str = "#666666"
    gray_600: str = "#333333"

    # Chart Color Palette (purple variations + neutrals, NO GREEN)
    chart_palette: Tuple[str, ...] = (
        "#7823DC",  # Primary purple
        "#9B4DCA",  # Light purple
        "#5C1BA8",  # Dark purple
        "#B266FF",  # Bright purple
        "#4A148C",  # Deep purple
        "#CE93D8",  # Pale purple
        "#7B1FA2",  # Purple variant
        "#666666",  # Gray
        "#999999",  # Light gray
        "#333333",  # Dark gray
    )

    # Typography
    font_family: str = "Inter, Arial, sans-serif"
    font_weight_normal: int = 400
    font_weight_medium: int = 500
    font_weight_bold: int = 600
    font_size_base: str = "14px"
    font_size_small: str = "12px"
    font_size_large: str = "18px"
    font_size_xl: str = "24px"
    font_size_xxl: str = "32px"

    # Spacing
    spacing_xs: str = "4px"
    spacing_sm: str = "8px"
    spacing_md: str = "16px"
    spacing_lg: str = "24px"
    spacing_xl: str = "32px"

    # Border Radius
    border_radius_sm: str = "4px"
    border_radius_md: str = "8px"
    border_radius_lg: str = "12px"

    # Shadows
    shadow_sm: str = "0 1px 2px rgba(0,0,0,0.1)"
    shadow_md: str = "0 4px 6px rgba(0,0,0,0.1)"
    shadow_lg: str = "0 10px 15px rgba(0,0,0,0.1)"

    # Breakpoints
    breakpoint_mobile: str = "480px"
    breakpoint_tablet: str = "768px"
    breakpoint_desktop: str = "1200px"

    def to_css_variables(self, prefix: str = "--kds-") -> str:
        """
        Export theme as CSS custom properties.

        Args:
            prefix: CSS variable prefix (default: --kds-)

        Returns:
            CSS string with all variables defined in :root
        """
        lines = [":root {"]

        # Colors
        lines.append(f"  {prefix}primary: {self.primary};")
        lines.append(f"  {prefix}primary-light: {self.primary_light};")
        lines.append(f"  {prefix}primary-dark: {self.primary_dark};")
        lines.append(f"  {prefix}primary-pale: {self.primary_pale};")
        lines.append(f"  {prefix}secondary: {self.secondary};")
        lines.append(f"  {prefix}accent: {self.accent};")
        lines.append(f"  {prefix}positive: {self.positive};")
        lines.append(f"  {prefix}negative: {self.negative};")
        lines.append(f"  {prefix}warning: {self.warning};")
        lines.append(f"  {prefix}info: {self.info};")
        lines.append(f"  {prefix}background-dark: {self.background_dark};")
        lines.append(f"  {prefix}background-light: {self.background_light};")
        lines.append(f"  {prefix}surface-dark: {self.surface_dark};")
        lines.append(f"  {prefix}surface-light: {self.surface_light};")
        lines.append(f"  {prefix}text-light: {self.text_light};")
        lines.append(f"  {prefix}text-dark: {self.text_dark};")
        lines.append(f"  {prefix}text-muted: {self.text_muted};")
        lines.append(f"  {prefix}gray-100: {self.gray_100};")
        lines.append(f"  {prefix}gray-200: {self.gray_200};")
        lines.append(f"  {prefix}gray-300: {self.gray_300};")
        lines.append(f"  {prefix}gray-400: {self.gray_400};")
        lines.append(f"  {prefix}gray-500: {self.gray_500};")
        lines.append(f"  {prefix}gray-600: {self.gray_600};")

        # Chart palette as array
        for i, color in enumerate(self.chart_palette):
            lines.append(f"  {prefix}chart-{i}: {color};")

        # Typography
        lines.append(f"  {prefix}font-family: {self.font_family};")
        lines.append(f"  {prefix}font-weight-normal: {self.font_weight_normal};")
        lines.append(f"  {prefix}font-weight-medium: {self.font_weight_medium};")
        lines.append(f"  {prefix}font-weight-bold: {self.font_weight_bold};")
        lines.append(f"  {prefix}font-size-base: {self.font_size_base};")
        lines.append(f"  {prefix}font-size-small: {self.font_size_small};")
        lines.append(f"  {prefix}font-size-large: {self.font_size_large};")
        lines.append(f"  {prefix}font-size-xl: {self.font_size_xl};")
        lines.append(f"  {prefix}font-size-xxl: {self.font_size_xxl};")

        # Spacing
        lines.append(f"  {prefix}spacing-xs: {self.spacing_xs};")
        lines.append(f"  {prefix}spacing-sm: {self.spacing_sm};")
        lines.append(f"  {prefix}spacing-md: {self.spacing_md};")
        lines.append(f"  {prefix}spacing-lg: {self.spacing_lg};")
        lines.append(f"  {prefix}spacing-xl: {self.spacing_xl};")

        # Border radius
        lines.append(f"  {prefix}radius-sm: {self.border_radius_sm};")
        lines.append(f"  {prefix}radius-md: {self.border_radius_md};")
        lines.append(f"  {prefix}radius-lg: {self.border_radius_lg};")

        # Shadows
        lines.append(f"  {prefix}shadow-sm: {self.shadow_sm};")
        lines.append(f"  {prefix}shadow-md: {self.shadow_md};")
        lines.append(f"  {prefix}shadow-lg: {self.shadow_lg};")

        # Breakpoints
        lines.append(f"  {prefix}breakpoint-mobile: {self.breakpoint_mobile};")
        lines.append(f"  {prefix}breakpoint-tablet: {self.breakpoint_tablet};")
        lines.append(f"  {prefix}breakpoint-desktop: {self.breakpoint_desktop};")

        lines.append("}")
        return "\n".join(lines)

    def to_matplotlib_rcparams(self) -> Dict:
        """
        Export theme as matplotlib rcParams dictionary.

        Returns:
            Dictionary of valid matplotlib rcParams
        """
        from cycler import cycler

        return {
            # Figure
            "figure.facecolor": self.background_dark,
            "figure.edgecolor": self.background_dark,

            # Axes
            "axes.facecolor": self.background_dark,
            "axes.edgecolor": self.gray_400,
            "axes.labelcolor": self.text_light,
            "axes.titlecolor": self.text_light,
            "axes.prop_cycle": cycler(color=list(self.chart_palette)),
            "axes.grid": False,  # KDS requirement: no gridlines
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.titleweight": self.font_weight_bold,
            "axes.labelweight": self.font_weight_medium,

            # Text
            "text.color": self.text_light,
            "font.family": "sans-serif",
            "font.sans-serif": ["Inter", "Arial", "sans-serif"],
            "font.size": 11,
            "font.weight": self.font_weight_normal,

            # Ticks
            "xtick.color": self.text_light,
            "ytick.color": self.text_light,
            "xtick.labelcolor": self.text_light,
            "ytick.labelcolor": self.text_light,

            # Legend
            "legend.facecolor": self.surface_dark,
            "legend.edgecolor": self.gray_500,
            "legend.labelcolor": self.text_light,
            "legend.frameon": False,

            # Grid (disabled but styled if enabled)
            "grid.color": self.gray_500,
            "grid.alpha": 0.3,
        }

    def to_plotly_template(self) -> Dict:
        """
        Export theme as Plotly template dictionary.

        Returns:
            Dictionary suitable for plotly.io.templates
        """
        return {
            "layout": {
                "colorway": list(self.chart_palette),
                "font": {
                    "family": self.font_family,
                    "color": self.text_light,
                    "size": 14,
                },
                "title": {
                    "font": {
                        "size": 18,
                        "color": self.text_light,
                    },
                    "x": 0.5,
                    "xanchor": "center",
                },
                "paper_bgcolor": self.background_dark,
                "plot_bgcolor": self.background_dark,
                "xaxis": {
                    "gridcolor": self.gray_500,
                    "gridwidth": 0,  # No gridlines
                    "showgrid": False,
                    "linecolor": self.gray_400,
                    "tickcolor": self.text_light,
                    "tickfont": {"color": self.text_light},
                    "title": {"font": {"color": self.text_light}},
                },
                "yaxis": {
                    "gridcolor": self.gray_500,
                    "gridwidth": 0,  # No gridlines
                    "showgrid": False,
                    "linecolor": self.gray_400,
                    "tickcolor": self.text_light,
                    "tickfont": {"color": self.text_light},
                    "title": {"font": {"color": self.text_light}},
                },
                "legend": {
                    "bgcolor": "rgba(0,0,0,0)",
                    "font": {"color": self.text_light},
                    "orientation": "h",
                    "yanchor": "bottom",
                    "y": -0.2,
                    "xanchor": "center",
                    "x": 0.5,
                },
                "margin": {"l": 60, "r": 30, "t": 60, "b": 60},
            },
            "data": {
                "bar": [{"marker": {"line": {"width": 0}}}],
                "pie": [{"marker": {"line": {"color": self.background_dark, "width": 2}}}],
            },
        }

    def to_streamlit_config(self) -> str:
        """
        Export theme as Streamlit config.toml content.

        Returns:
            TOML string for .streamlit/config.toml
        """
        return f"""[theme]
primaryColor = "{self.primary}"
backgroundColor = "{self.background_dark}"
secondaryBackgroundColor = "{self.surface_dark}"
textColor = "{self.text_light}"
font = "sans serif"

[server]
headless = true

[browser]
gatherUsageStats = false
"""

    def to_react_theme(self) -> Dict:
        """
        Export theme as React/JavaScript theme object.

        Returns:
            Dictionary suitable for JSON serialization in React apps
        """
        return {
            "colors": {
                "primary": self.primary,
                "primaryLight": self.primary_light,
                "primaryDark": self.primary_dark,
                "primaryPale": self.primary_pale,
                "secondary": self.secondary,
                "accent": self.accent,
                "positive": self.positive,
                "negative": self.negative,
                "warning": self.warning,
                "info": self.info,
                "backgroundDark": self.background_dark,
                "backgroundLight": self.background_light,
                "surfaceDark": self.surface_dark,
                "surfaceLight": self.surface_light,
                "textLight": self.text_light,
                "textDark": self.text_dark,
                "textMuted": self.text_muted,
            },
            "chartPalette": list(self.chart_palette),
            "typography": {
                "fontFamily": self.font_family,
                "fontWeights": {
                    "normal": self.font_weight_normal,
                    "medium": self.font_weight_medium,
                    "bold": self.font_weight_bold,
                },
                "fontSizes": {
                    "small": self.font_size_small,
                    "base": self.font_size_base,
                    "large": self.font_size_large,
                    "xl": self.font_size_xl,
                    "xxl": self.font_size_xxl,
                },
            },
            "spacing": {
                "xs": self.spacing_xs,
                "sm": self.spacing_sm,
                "md": self.spacing_md,
                "lg": self.spacing_lg,
                "xl": self.spacing_xl,
            },
            "borderRadius": {
                "sm": self.border_radius_sm,
                "md": self.border_radius_md,
                "lg": self.border_radius_lg,
            },
            "shadows": {
                "sm": self.shadow_sm,
                "md": self.shadow_md,
                "lg": self.shadow_lg,
            },
            "breakpoints": {
                "mobile": self.breakpoint_mobile,
                "tablet": self.breakpoint_tablet,
                "desktop": self.breakpoint_desktop,
            },
        }

    def get_chart_colors(self, n: int) -> List[str]:
        """
        Get n colors from the chart palette.

        Args:
            n: Number of colors needed

        Returns:
            List of hex color codes
        """
        colors = []
        palette = list(self.chart_palette)
        for i in range(n):
            colors.append(palette[i % len(palette)])
        return colors
