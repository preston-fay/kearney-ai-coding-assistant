"""Tests for KDSTheme."""

import pytest
from core.kds_theme import KDSTheme


class TestKDSTheme:
    """Test suite for KDSTheme dataclass."""

    def test_default_primary_is_kearney_purple(self):
        """Verify default primary color is Kearney Purple."""
        theme = KDSTheme()
        assert theme.primary == "#7823DC"

    def test_no_green_colors_in_palette(self):
        """Verify no forbidden green colors exist in theme."""
        theme = KDSTheme()

        # Forbidden green patterns
        green_patterns = [
            "#00ff00", "#008000", "#2e7d32", "#4caf50",
            "#66bb6a", "#81c784", "#a5d6a7", "#c8e6c9",
        ]

        for attr_name in dir(theme):
            if attr_name.startswith("_"):
                continue
            value = getattr(theme, attr_name)
            if isinstance(value, str) and value.startswith("#"):
                assert value.lower() not in green_patterns, \
                    f"Forbidden green color found: {attr_name}={value}"

    def test_chart_palette_no_green(self):
        """Verify chart palette contains no green colors."""
        theme = KDSTheme()

        green_patterns = ["#00ff00", "#008000", "#2e7d32", "#4caf50", "#66bb6a"]

        for color in theme.chart_palette:
            assert color.lower() not in green_patterns, \
                f"Forbidden green in chart_palette: {color}"

    def test_to_css_variables_produces_valid_css(self):
        """Test CSS variable export."""
        theme = KDSTheme()
        css = theme.to_css_variables()

        assert ":root {" in css
        assert "--kds-primary:" in css
        assert "#7823DC" in css or "#7823dc" in css
        assert css.count(";") > 10  # Multiple variables

    def test_to_css_variables_custom_prefix(self):
        """Test CSS variable export with custom prefix."""
        theme = KDSTheme()
        css = theme.to_css_variables(prefix="--custom-")

        assert "--custom-primary:" in css
        assert "--kds-" not in css

    def test_to_matplotlib_rcparams_is_valid(self):
        """Test matplotlib rcParams export."""
        theme = KDSTheme()
        params = theme.to_matplotlib_rcparams()

        assert isinstance(params, dict)
        assert "axes.prop_cycle" in params
        assert params["axes.grid"] is False  # KDS rule: no gridlines

    def test_to_plotly_template_structure(self):
        """Test Plotly template export."""
        theme = KDSTheme()
        template = theme.to_plotly_template()

        assert "layout" in template
        assert "colorway" in template["layout"]
        assert "#7823DC" in template["layout"]["colorway"]
        assert template["layout"]["xaxis"]["showgrid"] is False
        assert template["layout"]["yaxis"]["showgrid"] is False

    def test_theme_is_frozen(self):
        """Verify theme is immutable."""
        theme = KDSTheme()
        with pytest.raises(AttributeError):
            theme.primary = "#000000"

    def test_to_streamlit_config(self):
        """Test Streamlit config export."""
        theme = KDSTheme()
        config = theme.to_streamlit_config()

        assert "[theme]" in config
        assert "primaryColor" in config
        assert "#7823DC" in config or "#7823dc" in config

    def test_to_react_theme(self):
        """Test React theme export."""
        theme = KDSTheme()
        react_theme = theme.to_react_theme()

        assert "colors" in react_theme
        assert react_theme["colors"]["primary"] == "#7823DC"
        assert "chartPalette" in react_theme
        assert "typography" in react_theme

    def test_get_chart_colors(self):
        """Test chart color retrieval."""
        theme = KDSTheme()

        colors = theme.get_chart_colors(3)
        assert len(colors) == 3
        assert colors[0] == "#7823DC"  # First is primary

        # Test wrapping
        colors = theme.get_chart_colors(15)
        assert len(colors) == 15

    def test_positive_color_is_not_green(self):
        """Verify positive indicator is not green."""
        theme = KDSTheme()

        # Positive should be light purple, not green
        assert theme.positive == "#D4A5FF"
        assert not theme.positive.lower().startswith("#0")  # Not green
        assert not theme.positive.lower().startswith("#2e")
        assert not theme.positive.lower().startswith("#4c")

    def test_negative_color_is_coral(self):
        """Verify negative indicator is coral."""
        theme = KDSTheme()
        assert theme.negative == "#FF6F61"

    def test_background_colors(self):
        """Test background color values."""
        theme = KDSTheme()

        assert theme.background_dark == "#1E1E1E"
        assert theme.background_light == "#FFFFFF"
        assert theme.surface_dark == "#2D2D2D"

    def test_font_family(self):
        """Test font family setting."""
        theme = KDSTheme()
        assert "Inter" in theme.font_family
        assert "Arial" in theme.font_family
