"""Tests for web extractor."""

import pytest
from unittest.mock import Mock, patch

from core.design_system.extractor import (
    _extract_colors_from_text,
    _extract_fonts_from_text,
    HEX_PATTERN,
    RGB_PATTERN,
)


class TestExtractColorsFromText:
    """Test color extraction from CSS text."""

    def test_extracts_hex_colors(self):
        """Should extract hex colors from CSS."""
        css = "color: #7823DC; background: #1E1E1E;"
        colors = _extract_colors_from_text(css)
        assert "#7823DC" in colors
        assert "#1E1E1E" in colors

    def test_extracts_rgb_colors(self):
        """Should convert RGB to hex."""
        css = "color: rgb(120, 35, 220);"
        colors = _extract_colors_from_text(css)
        assert "#7823DC" in colors

    def test_extracts_rgba_colors(self):
        """Should convert RGBA to hex (ignoring alpha)."""
        css = "color: rgba(255, 255, 255, 0.5);"
        colors = _extract_colors_from_text(css)
        assert "#FFFFFF" in colors

    def test_handles_lowercase_hex(self):
        """Should handle lowercase hex colors."""
        css = "color: #ffffff;"
        colors = _extract_colors_from_text(css)
        assert "#FFFFFF" in colors

    def test_empty_text(self):
        """Should return empty list for empty text."""
        colors = _extract_colors_from_text("")
        assert colors == []


class TestExtractFontsFromText:
    """Test font extraction from CSS text."""

    def test_extracts_font_family(self):
        """Should extract font-family values."""
        css = "font-family: Inter, Arial, sans-serif;"
        fonts = _extract_fonts_from_text(css)
        assert "Inter" in fonts

    def test_extracts_quoted_fonts(self):
        """Should handle quoted font names."""
        css = 'font-family: "Open Sans", sans-serif;'
        fonts = _extract_fonts_from_text(css)
        assert "Open Sans" in fonts

    def test_ignores_inherit(self):
        """Should ignore 'inherit' value."""
        css = "font-family: inherit;"
        fonts = _extract_fonts_from_text(css)
        assert fonts == []

    def test_multiple_declarations(self):
        """Should extract from multiple font-family declarations."""
        css = """
        h1 { font-family: Roboto; }
        p { font-family: Inter; }
        """
        fonts = _extract_fonts_from_text(css)
        assert "Roboto" in fonts
        assert "Inter" in fonts


class TestHexPattern:
    """Test hex color regex pattern."""

    def test_matches_valid_hex(self):
        """Should match valid 6-digit hex colors."""
        assert HEX_PATTERN.search("#7823DC")
        assert HEX_PATTERN.search("#ffffff")
        assert HEX_PATTERN.search("#000000")

    def test_no_match_short_hex(self):
        """Should not match 3-digit hex colors."""
        assert HEX_PATTERN.search("#FFF") is None

    def test_no_match_8_digit(self):
        """Should not match 8-digit hex (with alpha)."""
        # Our pattern uses negative lookahead to reject 8-digit colors
        matches = HEX_PATTERN.findall("#FFFFFF00")
        # Should NOT match because the pattern rejects when followed by hex digit
        assert matches == []

    def test_matches_hex_followed_by_non_hex(self):
        """Should match hex when followed by non-hex character."""
        matches = HEX_PATTERN.findall("#FFFFFF;")
        assert "#FFFFFF" in matches


class TestRgbPattern:
    """Test RGB color regex pattern."""

    def test_matches_rgb(self):
        """Should match rgb() values."""
        match = RGB_PATTERN.search("rgb(255, 128, 0)")
        assert match is not None
        assert match.groups() == ('255', '128', '0')

    def test_matches_with_spaces(self):
        """Should handle various spacing."""
        assert RGB_PATTERN.search("rgb(255,128,0)")
        assert RGB_PATTERN.search("rgb( 255 , 128 , 0 )")


# Integration tests would require mocking requests
class TestExtractFromUrl:
    """Test URL extraction (mocked)."""

    @patch('core.design_system.extractor.requests')
    @patch('core.design_system.extractor.HAS_WEB_DEPS', True)
    def test_extract_conservative_mode(self, mock_requests):
        """Should extract in conservative mode."""
        from core.design_system.extractor import extract_from_url

        # Mock response
        mock_response = Mock()
        mock_response.text = '''
        <html>
        <head>
            <style>
            .header { color: #7823DC; font-family: Inter; }
            </style>
        </head>
        <body>
            <header>
                <img src="/logo.png" alt="Company Logo">
            </header>
        </body>
        </html>
        '''
        mock_response.raise_for_status = Mock()
        mock_requests.get.return_value = mock_response

        result = extract_from_url("https://example.com", mode="conservative")

        assert "#7823DC" in result['colors']
        assert "Inter" in result['fonts']
        assert result['metadata']['mode'] == "conservative"
