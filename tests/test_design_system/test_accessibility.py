"""Tests for WCAG 2.1 AA accessibility enforcement."""

import pytest

from core.design_system.accessibility import (
    hex_to_rgb,
    rgb_to_hex,
    relative_luminance,
    contrast_ratio,
    ensure_contrast,
    validate_wcag_aa,
    make_accessible_palette,
    is_dark_color,
    get_text_color_for_background,
    get_min_ratio_for_context,
)


class TestHexToRgb:
    """Test hex to RGB conversion."""

    def test_white(self):
        """White should be (255, 255, 255)."""
        assert hex_to_rgb("#FFFFFF") == (255, 255, 255)

    def test_black(self):
        """Black should be (0, 0, 0)."""
        assert hex_to_rgb("#000000") == (0, 0, 0)

    def test_kearney_purple(self):
        """Kearney purple should convert correctly."""
        r, g, b = hex_to_rgb("#7823DC")
        assert r == 120
        assert g == 35
        assert b == 220

    def test_lowercase(self):
        """Should handle lowercase hex."""
        assert hex_to_rgb("#ffffff") == (255, 255, 255)


class TestRgbToHex:
    """Test RGB to hex conversion."""

    def test_white(self):
        """White RGB should give #FFFFFF."""
        assert rgb_to_hex(255, 255, 255) == "#FFFFFF"

    def test_black(self):
        """Black RGB should give #000000."""
        assert rgb_to_hex(0, 0, 0) == "#000000"

    def test_red(self):
        """Pure red should give #FF0000."""
        assert rgb_to_hex(255, 0, 0) == "#FF0000"


class TestRelativeLuminance:
    """Test relative luminance calculation."""

    def test_white_luminance(self):
        """White should have luminance of 1."""
        lum = relative_luminance("#FFFFFF")
        assert abs(lum - 1.0) < 0.01

    def test_black_luminance(self):
        """Black should have luminance of 0."""
        lum = relative_luminance("#000000")
        assert abs(lum - 0.0) < 0.01

    def test_gray_luminance(self):
        """50% gray should have luminance around 0.2."""
        lum = relative_luminance("#808080")
        assert 0.1 < lum < 0.3


class TestContrastRatio:
    """Test contrast ratio calculation."""

    def test_white_on_black(self):
        """White on black should have maximum contrast (21:1)."""
        ratio = contrast_ratio("#FFFFFF", "#000000")
        assert abs(ratio - 21.0) < 0.1

    def test_black_on_white(self):
        """Order shouldn't matter for contrast ratio."""
        ratio = contrast_ratio("#000000", "#FFFFFF")
        assert abs(ratio - 21.0) < 0.1

    def test_same_color(self):
        """Same color should have 1:1 contrast."""
        ratio = contrast_ratio("#7823DC", "#7823DC")
        assert abs(ratio - 1.0) < 0.01

    def test_kearney_purple_on_dark(self):
        """Kearney purple on dark background should fail WCAG AA."""
        ratio = contrast_ratio("#7823DC", "#1E1E1E")
        # Original purple doesn't meet 4.5:1
        assert ratio < 4.5


class TestEnsureContrast:
    """Test contrast adjustment."""

    def test_already_sufficient(self):
        """Should return original if contrast is sufficient."""
        result = ensure_contrast("#FFFFFF", "#000000", min_ratio=4.5)
        assert result == "#FFFFFF"

    def test_binary_strategy(self):
        """Binary strategy should return white or black."""
        result = ensure_contrast(
            "#7823DC", "#1E1E1E", min_ratio=4.5, strategy="binary"
        )
        assert result in ["#FFFFFF", "#000000"]

    def test_tint_preserves_hue(self):
        """Tint strategy should preserve approximate hue."""
        result = ensure_contrast(
            "#7823DC", "#1E1E1E", min_ratio=4.5, strategy="tint"
        )
        # Result should still be purplish
        r, g, b = hex_to_rgb(result)
        # Blue should be relatively high, green should be low
        assert b > g

    def test_result_meets_contrast(self):
        """Result should meet the contrast requirement."""
        result = ensure_contrast("#7823DC", "#1E1E1E", min_ratio=4.5)
        ratio = contrast_ratio(result, "#1E1E1E")
        assert ratio >= 4.5


class TestValidateWcagAa:
    """Test WCAG AA validation."""

    def test_passing_pair(self):
        """White on black should pass."""
        result = validate_wcag_aa("#FFFFFF", "#000000")
        assert result["passes"] is True
        assert result["ratio"] > 4.5

    def test_failing_pair(self):
        """Low contrast pair should fail."""
        result = validate_wcag_aa("#CCCCCC", "#DDDDDD")
        assert result["passes"] is False
        assert result["ratio"] < 4.5

    def test_large_text_context(self):
        """Large text only needs 3:1 ratio."""
        result = validate_wcag_aa("#CCCCCC", "#333333", context="heading_large")
        assert result["required"] == 3.0


class TestMakeAccessiblePalette:
    """Test palette accessibility adjustment."""

    def test_adjusts_colors(self):
        """Should adjust colors to meet contrast."""
        colors = ["#7823DC", "#5C1BA8"]
        result = make_accessible_palette(colors, "#1E1E1E", min_ratio=3.0)

        for color in result:
            ratio = contrast_ratio(color, "#1E1E1E")
            assert ratio >= 3.0

    def test_preserves_count(self):
        """Should return same number of colors."""
        colors = ["#7823DC", "#5C1BA8", "#9B4DCA"]
        result = make_accessible_palette(colors, "#1E1E1E")
        assert len(result) == 3


class TestIsDarkColor:
    """Test dark color detection."""

    def test_black_is_dark(self):
        """Black should be dark."""
        assert is_dark_color("#000000") is True

    def test_white_is_light(self):
        """White should not be dark."""
        assert is_dark_color("#FFFFFF") is False

    def test_dark_background_is_dark(self):
        """Dark background color should be dark."""
        assert is_dark_color("#1E1E1E") is True


class TestGetTextColorForBackground:
    """Test text color selection."""

    def test_dark_background_gets_white(self):
        """Dark background should get white text."""
        assert get_text_color_for_background("#1E1E1E") == "#FFFFFF"

    def test_light_background_gets_black(self):
        """Light background should get black text."""
        assert get_text_color_for_background("#FFFFFF") == "#000000"


class TestGetMinRatioForContext:
    """Test context-based ratio requirements."""

    def test_body_text_needs_4_5(self):
        """Body text should require 4.5:1."""
        assert get_min_ratio_for_context("body") == 4.5

    def test_heading_large_needs_3(self):
        """Large headings only need 3:1."""
        assert get_min_ratio_for_context("heading_large") == 3.0

    def test_chart_series_needs_3(self):
        """Chart series only need 3:1."""
        assert get_min_ratio_for_context("chart_series") == 3.0
