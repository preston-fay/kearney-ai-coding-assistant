"""Tests for design system schema validation."""

import pytest
from pathlib import Path
import tempfile

from core.design_system.schema import (
    DesignSystem,
    Meta,
    ColorPalette,
    Typography,
    FontFamily,
    Logo,
    validate_hex_color,
)


class TestValidateHexColor:
    """Test hex color validation."""

    def test_valid_hex_colors(self):
        """Valid hex colors should pass."""
        assert validate_hex_color("#7823DC") is True
        assert validate_hex_color("#FFFFFF") is True
        assert validate_hex_color("#000000") is True
        assert validate_hex_color("#1e1e1e") is True

    def test_invalid_hex_colors(self):
        """Invalid hex colors should fail."""
        assert validate_hex_color("7823DC") is False  # Missing #
        assert validate_hex_color("#FFF") is False  # Too short
        assert validate_hex_color("#GGGGGG") is False  # Invalid chars
        assert validate_hex_color("rgb(255,255,255)") is False


class TestMeta:
    """Test Meta dataclass."""

    def test_from_dict(self):
        """Should create Meta from dictionary."""
        data = {
            "name": "Test Brand",
            "slug": "test-brand",
            "version": "2.0.0",
            "source_url": "https://example.com",
        }
        meta = Meta.from_dict(data)
        assert meta.name == "Test Brand"
        assert meta.slug == "test-brand"
        assert meta.version == "2.0.0"
        assert meta.source_url == "https://example.com"

    def test_to_dict(self):
        """Should convert Meta to dictionary."""
        meta = Meta(name="Test", slug="test", version="1.0.0")
        result = meta.to_dict()
        assert result["name"] == "Test"
        assert result["slug"] == "test"
        assert result["version"] == "1.0.0"


class TestColorPalette:
    """Test ColorPalette dataclass."""

    def test_from_dict(self):
        """Should create ColorPalette from dictionary."""
        data = {
            "primary": "#7823DC",
            "secondary": "#5C1BA8",
            "chart_palette": ["#7823DC", "#9B4DCA"],
            "forbidden": ["#00FF00"],
        }
        palette = ColorPalette.from_dict(data)
        assert palette.primary == "#7823DC"
        assert palette.secondary == "#5C1BA8"
        assert len(palette.chart_palette) == 2
        assert "#00FF00" in palette.forbidden

    def test_validates_colors(self):
        """Should reject invalid hex colors."""
        with pytest.raises(ValueError, match="Invalid hex color"):
            ColorPalette(primary="invalid")

    def test_validates_chart_palette(self):
        """Should reject invalid colors in chart palette."""
        with pytest.raises(ValueError, match="Invalid hex color"):
            ColorPalette(primary="#7823DC", chart_palette=["#7823DC", "invalid"])


class TestTypography:
    """Test Typography dataclass."""

    def test_from_dict(self):
        """Should create Typography from dictionary."""
        data = {
            "heading": {"family": "Inter", "fallback": "Arial"},
            "body": {"family": "Roboto", "fallback": "sans-serif"},
            "monospace": {"family": "Courier", "fallback": "monospace"},
        }
        typo = Typography.from_dict(data)
        assert typo.heading.family == "Inter"
        assert typo.body.family == "Roboto"
        assert typo.monospace.family == "Courier"


class TestDesignSystem:
    """Test DesignSystem dataclass."""

    def test_from_yaml_kearney(self):
        """Should load Kearney brand.yaml correctly."""
        brand_path = Path("config/brands/kearney/brand.yaml")
        ds = DesignSystem.from_yaml(brand_path)

        assert ds.meta.name == "Kearney"
        assert ds.meta.slug == "kearney"
        assert ds.colors.primary == "#7823DC"
        assert len(ds.colors.chart_palette) >= 6
        assert "#00FF00" in ds.colors.forbidden

    def test_from_dict(self):
        """Should create DesignSystem from dictionary."""
        data = {
            "meta": {"name": "Test", "slug": "test"},
            "colors": {"primary": "#FF0000"},
            "typography": {
                "heading": {"family": "Inter", "fallback": "Arial"},
                "body": {"family": "Inter", "fallback": "Arial"},
                "monospace": {"family": "Courier", "fallback": "monospace"},
            },
            "backgrounds": {"dark": "#1E1E1E", "light": "#FFFFFF"},
            "text": {"on_dark": "#FFFFFF", "on_light": "#333333"},
        }
        ds = DesignSystem.from_dict(data)
        assert ds.meta.name == "Test"
        assert ds.colors.primary == "#FF0000"

    def test_to_dict_roundtrip(self):
        """Should round-trip through to_dict and from_dict."""
        brand_path = Path("config/brands/kearney/brand.yaml")
        ds1 = DesignSystem.from_yaml(brand_path)
        data = ds1.to_dict()
        ds2 = DesignSystem.from_dict(data)

        assert ds1.meta.name == ds2.meta.name
        assert ds1.colors.primary == ds2.colors.primary

    def test_save_and_load(self):
        """Should save and load design system."""
        ds = DesignSystem.from_dict({
            "meta": {"name": "SaveTest", "slug": "savetest"},
            "colors": {"primary": "#123456"},
            "typography": {
                "heading": {"family": "Inter", "fallback": "Arial"},
                "body": {"family": "Inter", "fallback": "Arial"},
                "monospace": {"family": "Courier", "fallback": "monospace"},
            },
        })

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "brand.yaml"
            ds.save(path)
            loaded = DesignSystem.from_yaml(path)

            assert loaded.meta.name == "SaveTest"
            assert loaded.colors.primary == "#123456"

    def test_slug_property(self):
        """Should expose slug property."""
        ds = DesignSystem.from_dict({
            "meta": {"name": "Test", "slug": "test-slug"},
            "colors": {"primary": "#7823DC"},
            "typography": {
                "heading": {"family": "Inter", "fallback": "Arial"},
                "body": {"family": "Inter", "fallback": "Arial"},
                "monospace": {"family": "Courier", "fallback": "monospace"},
            },
        })
        assert ds.slug == "test-slug"
