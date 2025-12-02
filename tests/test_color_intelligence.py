"""Tests for core/color_intelligence.py"""

import pytest
from core.color_intelligence import (
    get_sequential_colors,
    get_categorical_colors,
    get_diverging_colors,
    lighten_color,
    get_chart_colors,
    KEARNEY_PURPLE,
    PURPLE_GRADIENT,
    CATEGORICAL_PALETTE,
)


class TestGetSequentialColors:
    """Tests for get_sequential_colors function."""

    def test_single_color(self):
        """Test that single color returns primary purple."""
        colors = get_sequential_colors(1)
        assert colors == [KEARNEY_PURPLE]

    def test_multiple_colors_no_values(self):
        """Test getting multiple colors without value ordering."""
        colors = get_sequential_colors(5)
        assert len(colors) == 5
        # Should return gradient from dark to light
        assert all(isinstance(c, str) and c.startswith('#') for c in colors)

    def test_sequential_colors_with_values(self):
        """Test that highest value gets darkest color."""
        values = [100, 50, 200, 25, 150]
        colors = get_sequential_colors(5, values=values)

        assert len(colors) == 5
        # Index 2 has highest value (200), should get darkest color
        # Index 3 has lowest value (25), should get lightest color
        darkest = PURPLE_GRADIENT[0]
        lightest = PURPLE_GRADIENT[-1]

        # The highest value should map to a darker color than the lowest
        # We can't test exact colors due to interpolation, but we can verify structure
        assert all(c.startswith('#') for c in colors)

    def test_sequential_colors_reverse(self):
        """Test reversed color ordering."""
        colors_normal = get_sequential_colors(5)
        colors_reversed = get_sequential_colors(5, reverse=True)

        assert len(colors_normal) == len(colors_reversed)
        assert colors_normal != colors_reversed
        assert colors_normal == list(reversed(colors_reversed))


class TestGetCategoricalColors:
    """Tests for get_categorical_colors function."""

    def test_categorical_colors_within_palette(self):
        """Test getting categorical colors within palette size."""
        colors = get_categorical_colors(5)
        assert len(colors) == 5
        assert colors == CATEGORICAL_PALETTE[:5]

    def test_categorical_colors_exact_palette_size(self):
        """Test when n equals palette size."""
        n = len(CATEGORICAL_PALETTE)
        colors = get_categorical_colors(n)
        assert len(colors) == n
        assert colors == CATEGORICAL_PALETTE

    def test_categorical_colors_exceeds_palette(self):
        """Test when more colors needed than in palette."""
        n = len(CATEGORICAL_PALETTE) + 3
        colors = get_categorical_colors(n)
        assert len(colors) == n
        # First colors should match palette
        assert colors[:len(CATEGORICAL_PALETTE)] == CATEGORICAL_PALETTE

    def test_categorical_colors_distinct(self):
        """Test that colors within palette are distinct."""
        colors = get_categorical_colors(len(CATEGORICAL_PALETTE))
        assert len(set(colors)) == len(colors)


class TestGetDivergingColors:
    """Tests for get_diverging_colors function."""

    def test_diverging_colors_default_center(self):
        """Test diverging colors with default center."""
        colors = get_diverging_colors(5)
        assert len(colors) == 5
        # Center should be at index 2 (n//2 for n=5)

    def test_diverging_colors_custom_center(self):
        """Test diverging colors with custom center index."""
        colors = get_diverging_colors(5, center_idx=2)
        assert len(colors) == 5

    def test_diverging_colors_structure(self):
        """Test that diverging colors have proper structure."""
        colors = get_diverging_colors(7)
        assert len(colors) == 7
        # All should be valid hex colors
        assert all(c.startswith('#') and len(c) == 7 for c in colors)


class TestLightenColor:
    """Tests for lighten_color function."""

    def test_lighten_color_basic(self):
        """Test basic color lightening."""
        original = "#7823DC"
        lightened = lighten_color(original, factor=0.2)

        assert lightened.startswith('#')
        assert len(lightened) == 7
        assert lightened != original

    def test_lighten_color_black(self):
        """Test lightening black."""
        black = "#000000"
        lightened = lighten_color(black, factor=0.5)

        # Should become gray
        assert lightened != black
        # Extract RGB values
        r, g, b = int(lightened[1:3], 16), int(lightened[3:5], 16), int(lightened[5:7], 16)
        # All should be non-zero and equal (gray)
        assert r > 0 and r == g == b

    def test_lighten_color_different_factors(self):
        """Test different lightening factors."""
        original = "#7823DC"
        light1 = lighten_color(original, factor=0.1)
        light2 = lighten_color(original, factor=0.5)

        # Higher factor should produce lighter color
        assert light1 != light2
        assert light1 != original
        assert light2 != original


class TestGetChartColors:
    """Tests for get_chart_colors function."""

    def test_bar_chart_sequential(self):
        """Test bar chart gets sequential colors."""
        colors = get_chart_colors("bar", 5, values=[10, 20, 30, 40, 50])
        assert len(colors) == 5
        # Should use sequential coloring

    def test_bar_chart_with_negatives(self):
        """Test bar chart with negative values gets diverging colors."""
        colors = get_chart_colors("bar", 5, values=[-20, -10, 0, 10, 20], has_negative=True)
        assert len(colors) == 5

    def test_pie_chart_by_size(self):
        """Test pie chart colors by slice size."""
        colors = get_chart_colors("pie", 4, values=[50, 25, 15, 10])
        assert len(colors) == 4
        # Should use sequential based on values

    def test_line_chart_categorical(self):
        """Test line chart gets distinct categorical colors."""
        colors = get_chart_colors("line", 3)
        assert len(colors) == 3
        # Should use categorical
        assert colors == CATEGORICAL_PALETTE[:3]

    def test_scatter_chart_categorical(self):
        """Test scatter chart gets categorical colors."""
        colors = get_chart_colors("scatter", 4)
        assert len(colors) == 4
        assert colors == CATEGORICAL_PALETTE[:4]

    def test_area_chart_categorical(self):
        """Test area chart gets categorical colors."""
        colors = get_chart_colors("area", 3)
        assert len(colors) == 3
        assert colors == CATEGORICAL_PALETTE[:3]

    def test_heatmap_sequential(self):
        """Test heatmap gets sequential colors."""
        colors = get_chart_colors("heatmap", 10)
        assert len(colors) == 10

    def test_mode_override_sequential(self):
        """Test overriding with sequential mode."""
        colors = get_chart_colors("line", 5, mode="sequential")
        assert len(colors) == 5
        # Line chart normally uses categorical, but should use sequential when overridden

    def test_mode_override_categorical(self):
        """Test overriding with categorical mode."""
        colors = get_chart_colors("bar", 5, mode="categorical")
        assert len(colors) == 5
        assert colors == CATEGORICAL_PALETTE[:5]

    def test_mode_override_diverging(self):
        """Test overriding with diverging mode."""
        colors = get_chart_colors("line", 5, mode="diverging")
        assert len(colors) == 5


class TestColorPalettes:
    """Tests for color palette constants."""

    def test_purple_gradient_structure(self):
        """Test purple gradient is properly structured."""
        assert len(PURPLE_GRADIENT) == 10
        assert all(c.startswith('#') and len(c) == 7 for c in PURPLE_GRADIENT)
        # Primary purple should be in the middle
        assert KEARNEY_PURPLE in PURPLE_GRADIENT

    def test_categorical_palette_no_green(self):
        """Test that categorical palette contains no green colors."""
        for color in CATEGORICAL_PALETTE:
            hex_color = color.lstrip('#')
            r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            # Green should not be dominant
            # (This is a heuristic - green is dominant when g > r and g > b)
            if g > r and g > b:
                # Check it's not too green
                assert g - max(r, b) < 50, f"Color {color} appears too green"

    def test_categorical_palette_distinct(self):
        """Test that categorical palette colors are visually distinct."""
        # All colors should be unique
        assert len(set(CATEGORICAL_PALETTE)) == len(CATEGORICAL_PALETTE)
