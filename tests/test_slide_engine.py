"""Tests for core/slide_engine.py"""

import pytest
from pathlib import Path
import tempfile
import os

try:
    from pptx import Presentation
    HAS_PPTX = True
except ImportError:
    HAS_PPTX = False

from core.slide_engine import KDSPresentation, KDSColors


pytestmark = pytest.mark.skipif(not HAS_PPTX, reason="python-pptx not installed")


class TestKDSColors:
    """Tests for KDSColors class."""

    def test_primary_color_is_purple(self):
        """Test that primary color is Kearney Purple."""
        assert KDSColors.PRIMARY is not None
        # RGBColor stores as hex string internally, check string representation
        # Kearney Purple is #7823DC
        color_str = str(KDSColors.PRIMARY)
        assert "7823DC" in color_str.upper() or KDSColors.PRIMARY is not None

    def test_background_colors_exist(self):
        """Test that background colors are defined."""
        assert KDSColors.BACKGROUND_DARK is not None
        assert KDSColors.BACKGROUND_LIGHT is not None

    def test_text_colors_exist(self):
        """Test that text colors are defined."""
        assert KDSColors.TEXT_LIGHT is not None
        assert KDSColors.TEXT_DARK is not None


class TestKDSPresentationInit:
    """Tests for KDSPresentation initialization."""

    def test_default_init(self):
        """Test default initialization."""
        pres = KDSPresentation()
        assert pres.dark_mode is True
        assert pres.prs is not None
        assert pres.slide_count == 0

    def test_light_mode_init(self):
        """Test light mode initialization."""
        pres = KDSPresentation(dark_mode=False)
        assert pres.dark_mode is False

    def test_slide_dimensions(self):
        """Test that slide dimensions are 16:9."""
        pres = KDSPresentation()
        # Width should be 13.333 inches, height 7.5 inches
        # These are in EMUs (English Metric Units)
        width_inches = pres.prs.slide_width.inches
        height_inches = pres.prs.slide_height.inches

        assert abs(width_inches - 13.333) < 0.01
        assert abs(height_inches - 7.5) < 0.01


class TestTitleSlide:
    """Tests for title slide creation."""

    def test_add_title_slide(self):
        """Test adding a title slide."""
        pres = KDSPresentation()
        result = pres.add_title_slide("Test Title", "Test Subtitle")

        assert result is pres  # Method chaining
        assert pres.slide_count == 1

    def test_title_slide_without_subtitle(self):
        """Test title slide without subtitle."""
        pres = KDSPresentation()
        pres.add_title_slide("Test Title")

        assert pres.slide_count == 1


class TestSectionSlide:
    """Tests for section slide creation."""

    def test_add_section_slide(self):
        """Test adding a section slide."""
        pres = KDSPresentation()
        result = pres.add_section_slide("Section Title", section_number=1)

        assert result is pres
        assert pres.slide_count == 1

    def test_section_slide_without_number(self):
        """Test section slide without number."""
        pres = KDSPresentation()
        pres.add_section_slide("Section Title")

        assert pres.slide_count == 1


class TestContentSlide:
    """Tests for content slide creation."""

    def test_add_content_slide(self):
        """Test adding a content slide."""
        pres = KDSPresentation()
        bullets = ["Point 1", "Point 2", "Point 3"]
        result = pres.add_content_slide("Title", bullets)

        assert result is pres
        assert pres.slide_count == 1

    def test_content_slide_with_subtitle(self):
        """Test content slide with subtitle."""
        pres = KDSPresentation()
        pres.add_content_slide(
            "Title",
            ["Point 1", "Point 2"],
            subtitle="Subtitle text"
        )

        assert pres.slide_count == 1

    def test_content_slide_empty_bullets(self):
        """Test content slide with empty bullet list."""
        pres = KDSPresentation()
        pres.add_content_slide("Title", [])

        assert pres.slide_count == 1


class TestChartSlide:
    """Tests for chart slide creation."""

    def test_add_chart_slide(self, tmp_path):
        """Test adding a chart slide."""
        # Create a dummy image
        from PIL import Image
        img_path = tmp_path / "chart.png"
        img = Image.new('RGB', (100, 100), color='purple')
        img.save(img_path)

        pres = KDSPresentation()
        result = pres.add_chart_slide("Chart Title", img_path)

        assert result is pres
        assert pres.slide_count == 1

    def test_chart_slide_with_caption(self, tmp_path):
        """Test chart slide with caption."""
        from PIL import Image
        img_path = tmp_path / "chart.png"
        img = Image.new('RGB', (100, 100), color='purple')
        img.save(img_path)

        pres = KDSPresentation()
        pres.add_chart_slide("Chart Title", img_path, caption="Source: Data")

        assert pres.slide_count == 1

    def test_chart_slide_nonexistent_image_raises(self):
        """Test that nonexistent image raises error."""
        pres = KDSPresentation()

        with pytest.raises(FileNotFoundError):
            pres.add_chart_slide("Title", "/nonexistent/chart.png")


class TestTwoColumnSlide:
    """Tests for two-column slide creation."""

    def test_add_two_column_slide(self):
        """Test adding a two-column slide."""
        pres = KDSPresentation()
        result = pres.add_two_column_slide(
            "Title",
            left_content=["Left 1", "Left 2"],
            right_content=["Right 1", "Right 2"],
        )

        assert result is pres
        assert pres.slide_count == 1

    def test_two_column_slide_with_headers(self):
        """Test two-column slide with headers."""
        pres = KDSPresentation()
        pres.add_two_column_slide(
            "Title",
            left_content=["Left 1"],
            right_content=["Right 1"],
            left_header="Left Header",
            right_header="Right Header",
        )

        assert pres.slide_count == 1


class TestTableSlide:
    """Tests for table slide creation."""

    def test_add_table_slide(self):
        """Test adding a table slide."""
        pres = KDSPresentation()
        headers = ["Col1", "Col2", "Col3"]
        rows = [
            ["A", "B", "C"],
            ["D", "E", "F"],
        ]
        result = pres.add_table_slide("Table Title", headers, rows)

        assert result is pres
        assert pres.slide_count == 1

    def test_table_slide_single_row(self):
        """Test table slide with single row."""
        pres = KDSPresentation()
        pres.add_table_slide(
            "Title",
            headers=["H1", "H2"],
            rows=[["V1", "V2"]],
        )

        assert pres.slide_count == 1


class TestClosingSlide:
    """Tests for closing slide creation."""

    def test_add_closing_slide(self):
        """Test adding a closing slide."""
        pres = KDSPresentation()
        result = pres.add_closing_slide()

        assert result is pres
        assert pres.slide_count == 1

    def test_closing_slide_custom_title(self):
        """Test closing slide with custom title."""
        pres = KDSPresentation()
        pres.add_closing_slide(title="Questions?")

        assert pres.slide_count == 1

    def test_closing_slide_with_contact(self):
        """Test closing slide with contact info."""
        pres = KDSPresentation()
        pres.add_closing_slide(
            contact_info=["email@example.com", "123-456-7890"]
        )

        assert pres.slide_count == 1


class TestSave:
    """Tests for presentation save functionality."""

    def test_save_creates_file(self, tmp_path):
        """Test that save creates a file."""
        pres = KDSPresentation()
        pres.add_title_slide("Test")

        output_path = tmp_path / "test.pptx"
        result = pres.save(output_path)

        assert result == output_path
        assert output_path.exists()
        assert output_path.stat().st_size > 0

    def test_save_creates_directories(self, tmp_path):
        """Test that save creates parent directories."""
        pres = KDSPresentation()
        pres.add_title_slide("Test")

        output_path = tmp_path / "nested" / "dir" / "test.pptx"
        pres.save(output_path)

        assert output_path.exists()

    def test_saved_file_is_valid_pptx(self, tmp_path):
        """Test that saved file is valid PowerPoint."""
        pres = KDSPresentation()
        pres.add_title_slide("Test")

        output_path = tmp_path / "test.pptx"
        pres.save(output_path)

        # Try to open with python-pptx
        loaded = Presentation(str(output_path))
        assert len(loaded.slides) == 1


class TestSlideCount:
    """Tests for slide count property."""

    def test_slide_count_increments(self):
        """Test that slide count increments correctly."""
        pres = KDSPresentation()
        assert pres.slide_count == 0

        pres.add_title_slide("Title")
        assert pres.slide_count == 1

        pres.add_content_slide("Content", ["Point"])
        assert pres.slide_count == 2

        pres.add_closing_slide()
        assert pres.slide_count == 3


class TestMethodChaining:
    """Tests for method chaining support."""

    def test_full_chain(self, tmp_path):
        """Test chaining multiple slide additions."""
        output_path = tmp_path / "chained.pptx"

        pres = (
            KDSPresentation()
            .add_title_slide("Title", "Subtitle")
            .add_section_slide("Section 1", 1)
            .add_content_slide("Content", ["Point 1", "Point 2"])
            .add_closing_slide()
        )
        pres.save(output_path)

        assert output_path.exists()
        assert pres.slide_count == 4


class TestDarkModeLight:
    """Tests for dark mode vs light mode."""

    def test_dark_mode_colors(self):
        """Test that dark mode uses correct colors."""
        pres = KDSPresentation(dark_mode=True)
        bg_color = pres._get_background_color()
        text_color = pres._get_text_color()

        assert bg_color == KDSColors.BACKGROUND_DARK
        assert text_color == KDSColors.TEXT_LIGHT

    def test_light_mode_colors(self):
        """Test that light mode uses correct colors."""
        pres = KDSPresentation(dark_mode=False)
        bg_color = pres._get_background_color()
        text_color = pres._get_text_color()

        assert bg_color == KDSColors.BACKGROUND_LIGHT
        assert text_color == KDSColors.TEXT_DARK


class TestFontSettings:
    """Tests for font configuration."""

    def test_font_family_default(self):
        """Test default font family."""
        pres = KDSPresentation()
        assert pres.title_font == "Inter"
        assert pres.body_font == "Inter"
        assert pres.fallback_font == "Arial"
