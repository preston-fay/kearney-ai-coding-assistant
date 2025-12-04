"""Tests for asset analyzer."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os

from core.design_system.analyzer import (
    analyze_assets,
    analyze_image,
    analyze_pdf,
    analyze_pptx,
    _extract_dominant_colors,
    _filter_extreme_colors,
    _is_logo_candidate,
    IMAGE_EXTENSIONS,
    DOCUMENT_EXTENSIONS,
    PRESENTATION_EXTENSIONS,
)


class TestFileTypeConstants:
    """Test file extension constants."""

    def test_image_extensions(self):
        """Should include common image formats."""
        assert '.png' in IMAGE_EXTENSIONS
        assert '.jpg' in IMAGE_EXTENSIONS
        assert '.jpeg' in IMAGE_EXTENSIONS
        assert '.webp' in IMAGE_EXTENSIONS

    def test_document_extensions(self):
        """Should include PDF."""
        assert '.pdf' in DOCUMENT_EXTENSIONS

    def test_presentation_extensions(self):
        """Should include PowerPoint."""
        assert '.pptx' in PRESENTATION_EXTENSIONS


class TestFilterExtremeColors:
    """Test color filtering for extreme values."""

    def test_filters_black(self):
        """Should filter near-black colors."""
        colors = ["#000000", "#7823DC", "#111111"]
        filtered = _filter_extreme_colors(colors)
        assert "#000000" not in filtered
        assert "#111111" not in filtered
        assert "#7823DC" in filtered

    def test_filters_white(self):
        """Should filter near-white colors."""
        colors = ["#FFFFFF", "#7823DC", "#FAFAFA"]
        filtered = _filter_extreme_colors(colors)
        assert "#FFFFFF" not in filtered
        assert "#FAFAFA" not in filtered
        assert "#7823DC" in filtered

    def test_keeps_medium_colors(self):
        """Should keep colors in the middle range."""
        colors = ["#7823DC", "#0066CC", "#FF6600"]
        filtered = _filter_extreme_colors(colors)
        assert len(filtered) == 3

    def test_empty_list(self):
        """Should handle empty list."""
        filtered = _filter_extreme_colors([])
        assert filtered == []


class TestAnalyzeAssets:
    """Test the main analyze_assets function."""

    def test_handles_nonexistent_files(self):
        """Should skip non-existent files gracefully."""
        result = analyze_assets([Path("/nonexistent/file.png")])
        assert result["colors"] == []
        assert result["fonts"] == []
        assert result["logos"] == []

    def test_returns_empty_for_empty_list(self):
        """Should return empty results for empty file list."""
        result = analyze_assets([])
        assert result["colors"] == []
        assert result["fonts"] == []
        assert result["logos"] == []

    @patch('core.design_system.analyzer.HAS_PIL', True)
    @patch('core.design_system.analyzer.Image')
    def test_processes_image_files(self, mock_image):
        """Should process image files when PIL is available."""
        # Create a temp file
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            temp_path = Path(f.name)

        try:
            # Mock PIL Image
            mock_img = MagicMock()
            mock_img.mode = 'RGB'
            mock_img.size = (100, 100)
            mock_img.resize.return_value = mock_img
            mock_img.getdata.return_value = [(120, 35, 220)] * 100
            mock_image.open.return_value = mock_img

            result = analyze_assets([temp_path])
            # Should have attempted to process
            mock_image.open.assert_called()
        finally:
            os.unlink(temp_path)


class TestAnalyzeImage:
    """Test image analysis."""

    @patch('core.design_system.analyzer.HAS_PIL', False)
    def test_returns_empty_without_pil(self):
        """Should return empty results when PIL not available."""
        result = analyze_image(Path("test.png"))
        assert result["colors"] == []
        assert result["is_logo_candidate"] is False

    @patch('core.design_system.analyzer.HAS_PIL', True)
    @patch('core.design_system.analyzer.Image')
    def test_extracts_colors_from_rgb(self, mock_image):
        """Should extract colors from RGB image."""
        mock_img = MagicMock()
        mock_img.mode = 'RGB'
        mock_img.size = (200, 100)
        mock_img.resize.return_value = mock_img
        mock_img.getdata.return_value = [(120, 35, 220)] * 100
        mock_image.open.return_value = mock_img

        result = analyze_image(Path("test.png"))

        assert "#7823DC" in result["colors"]
        assert result["width"] == 200
        assert result["height"] == 100

    @patch('core.design_system.analyzer.HAS_PIL', True)
    @patch('core.design_system.analyzer.Image')
    def test_converts_rgba_to_rgb(self, mock_image):
        """Should convert RGBA images to RGB."""
        mock_img = MagicMock()
        mock_img.mode = 'RGBA'
        mock_img.size = (100, 100)
        mock_alpha = MagicMock()
        mock_img.split.return_value = [None, None, None, mock_alpha]

        mock_rgb = MagicMock()
        mock_rgb.mode = 'RGB'
        mock_rgb.resize.return_value = mock_rgb
        mock_rgb.getdata.return_value = [(255, 255, 255)] * 100

        mock_background = MagicMock()
        mock_background.resize.return_value = mock_background
        mock_background.getdata.return_value = [(255, 255, 255)] * 100

        mock_image.open.return_value = mock_img
        mock_image.new.return_value = mock_background

        result = analyze_image(Path("test.png"))
        mock_image.new.assert_called_with('RGB', (100, 100), (255, 255, 255))


class TestIsLogoCandidate:
    """Test logo detection heuristics."""

    @patch('core.design_system.analyzer.HAS_PIL', True)
    def test_detects_logo_in_filename(self):
        """Should detect logo if filename contains 'logo'."""
        result = _is_logo_candidate(
            Path("company_logo.png"),
            width=200,
            height=100,
            img=MagicMock()
        )
        assert result is True

    @patch('core.design_system.analyzer.HAS_PIL', True)
    def test_detects_brand_in_filename(self):
        """Should detect logo if filename contains 'brand'."""
        result = _is_logo_candidate(
            Path("brand_asset.png"),
            width=200,
            height=100,
            img=MagicMock()
        )
        assert result is True

    @patch('core.design_system.analyzer.HAS_PIL', True)
    def test_detects_icon_in_filename(self):
        """Should detect logo if filename contains 'icon'."""
        result = _is_logo_candidate(
            Path("favicon_icon.png"),
            width=200,
            height=100,
            img=MagicMock()
        )
        assert result is True

    @patch('core.design_system.analyzer.HAS_PIL', True)
    def test_detects_logo_by_dimensions(self):
        """Should detect logo by reasonable dimensions."""
        result = _is_logo_candidate(
            Path("unnamed.png"),
            width=300,
            height=100,
            img=MagicMock()
        )
        assert result is True

    @patch('core.design_system.analyzer.HAS_PIL', True)
    def test_rejects_too_large_image(self):
        """Should reject images that are too large for logos."""
        result = _is_logo_candidate(
            Path("photo.png"),
            width=2000,
            height=1500,
            img=MagicMock()
        )
        assert result is False

    @patch('core.design_system.analyzer.HAS_PIL', True)
    def test_rejects_too_small_image(self):
        """Should reject images that are too small for logos."""
        result = _is_logo_candidate(
            Path("tiny.png"),
            width=10,
            height=10,
            img=MagicMock()
        )
        assert result is False


class TestAnalyzePdf:
    """Test PDF analysis."""

    def test_returns_empty_results(self):
        """PDF analysis returns empty (limited implementation)."""
        result = analyze_pdf(Path("test.pdf"))
        assert result["colors"] == []
        assert result["fonts"] == []
        assert "note" in result


class TestAnalyzePptx:
    """Test PowerPoint analysis."""

    @patch('core.design_system.analyzer.HAS_PPTX', False)
    def test_returns_empty_without_pptx(self):
        """Should return empty results when python-pptx not available."""
        result = analyze_pptx(Path("test.pptx"))
        assert result["colors"] == []
        assert result["fonts"] == []

    @patch('core.design_system.analyzer.HAS_PPTX', True)
    @patch('core.design_system.analyzer.Presentation')
    def test_extracts_theme_colors(self, mock_pres_class):
        """Should extract colors from PowerPoint theme."""
        # Mock presentation
        mock_pres = MagicMock()
        mock_pres_class.return_value = mock_pres

        # Mock slide master
        mock_master = MagicMock()
        mock_master.shapes = []
        mock_master.slide_layouts = []
        mock_pres.slide_masters = [mock_master]
        mock_pres.slides = []

        with tempfile.NamedTemporaryFile(suffix='.pptx', delete=False) as f:
            temp_path = Path(f.name)

        try:
            result = analyze_pptx(temp_path)
            assert isinstance(result["colors"], list)
            assert isinstance(result["fonts"], list)
        finally:
            os.unlink(temp_path)


class TestExtractDominantColors:
    """Test color extraction from images."""

    def test_extracts_hex_colors(self):
        """Should convert RGB to hex."""
        mock_img = MagicMock()
        mock_img.getdata.return_value = [
            (120, 35, 220),
            (120, 35, 220),
            (255, 255, 255),
        ]

        colors = _extract_dominant_colors(mock_img, num_colors=2)

        assert "#7823DC" in colors
        assert "#FFFFFF" in colors

    def test_limits_color_count(self):
        """Should limit number of colors returned."""
        mock_img = MagicMock()
        mock_img.getdata.return_value = [
            (255, 0, 0),
            (0, 255, 0),
            (0, 0, 255),
            (255, 255, 0),
            (255, 0, 255),
            (0, 255, 255),
        ]

        colors = _extract_dominant_colors(mock_img, num_colors=3)

        assert len(colors) <= 3


class TestCreateFromAssets:
    """Test create_from_assets manager function."""

    @patch('core.design_system.analyzer.analyze_assets')
    def test_creates_design_system_from_assets(self, mock_analyze):
        """Should create DesignSystem from analyzed assets."""
        from core.design_system.manager import create_from_assets, BRANDS_DIR
        import shutil

        mock_analyze.return_value = {
            'colors': ['#0066CC', '#FF6600'],
            'fonts': ['Roboto', 'Open Sans'],
            'logos': [],
        }

        # Use a unique slug to avoid conflicts
        slug = "test-brand-assets"
        brand_dir = BRANDS_DIR / slug

        try:
            ds = create_from_assets(
                files=[Path("test.png")],
                slug=slug,
                name="Test Brand"
            )

            assert ds.meta.name == "Test Brand"
            assert ds.meta.slug == slug
            assert ds.colors.primary == "#0066CC"
            assert ds.colors.secondary == "#FF6600"
        finally:
            # Cleanup
            if brand_dir.exists():
                shutil.rmtree(brand_dir)

    @patch('core.design_system.analyzer.analyze_assets')
    def test_uses_fallback_colors(self, mock_analyze):
        """Should use fallback colors when none extracted."""
        from core.design_system.manager import create_from_assets, BRANDS_DIR
        import shutil

        mock_analyze.return_value = {
            'colors': [],
            'fonts': [],
            'logos': [],
        }

        slug = "empty-brand-test"
        brand_dir = BRANDS_DIR / slug

        try:
            ds = create_from_assets(
                files=[],
                slug=slug,
                name="Empty Brand"
            )

            # Should fallback to Kearney purple
            assert ds.colors.primary == "#7823DC"
        finally:
            # Cleanup
            if brand_dir.exists():
                shutil.rmtree(brand_dir)

    @patch('core.design_system.analyzer.analyze_assets')
    def test_extracts_fonts(self, mock_analyze):
        """Should extract fonts from assets."""
        from core.design_system.manager import create_from_assets, BRANDS_DIR
        import shutil

        mock_analyze.return_value = {
            'colors': ['#0066CC'],
            'fonts': ['Helvetica', 'Georgia'],
            'logos': [],
        }

        slug = "font-test-brand"
        brand_dir = BRANDS_DIR / slug

        try:
            ds = create_from_assets(
                files=[Path("test.pptx")],
                slug=slug,
                name="Font Test"
            )

            assert ds.typography.heading.family == "Helvetica"
            assert ds.typography.body.family == "Georgia"
        finally:
            # Cleanup
            if brand_dir.exists():
                shutil.rmtree(brand_dir)
