"""Tests for design system manager."""

import pytest
from pathlib import Path
import tempfile
import shutil

from core.design_system.manager import (
    get_default,
    list_design_systems,
    design_system_exists,
    load_design_system,
    save_design_system,
    delete_design_system,
    get_design_system_info,
)
from core.design_system.schema import DesignSystem, Meta, ColorPalette, Typography, FontFamily


class TestGetDefault:
    """Test get_default function."""

    def test_returns_kearney(self):
        """Default should be 'kearney'."""
        assert get_default() == "kearney"


class TestListDesignSystems:
    """Test listing design systems."""

    def test_includes_kearney(self):
        """List should include kearney."""
        systems = list_design_systems()
        assert "kearney" in systems

    def test_kearney_is_first(self):
        """Kearney should be first in the list."""
        systems = list_design_systems()
        assert systems[0] == "kearney"


class TestDesignSystemExists:
    """Test design system existence check."""

    def test_kearney_exists(self):
        """Kearney design system should exist."""
        assert design_system_exists("kearney") is True

    def test_nonexistent_returns_false(self):
        """Non-existent design system should return False."""
        assert design_system_exists("nonexistent-brand") is False


class TestLoadDesignSystem:
    """Test loading design systems."""

    def test_load_kearney(self):
        """Should load Kearney design system."""
        ds = load_design_system("kearney")
        assert ds.meta.name == "Kearney"
        assert ds.meta.slug == "kearney"
        assert ds.colors.primary == "#7823DC"

    def test_load_nonexistent_falls_back(self):
        """Loading non-existent should fall back to Kearney."""
        ds = load_design_system("nonexistent")
        assert ds.meta.slug == "kearney"

    def test_load_kearney_has_forbidden_colors(self):
        """Kearney should have forbidden green colors."""
        ds = load_design_system("kearney")
        assert "#00FF00" in ds.colors.forbidden


class TestSaveDesignSystem:
    """Test saving design systems."""

    def test_save_creates_directory(self):
        """Save should create brand directory."""
        ds = DesignSystem(
            meta=Meta(name="Test Save", slug="test-save"),
            colors=ColorPalette(primary="#FF0000"),
            typography=Typography(
                heading=FontFamily(family="Inter", fallback="Arial"),
                body=FontFamily(family="Inter", fallback="Arial"),
                monospace=FontFamily(family="Courier", fallback="monospace"),
            ),
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            # Temporarily override BRANDS_DIR
            import core.design_system.manager as manager
            original_dir = manager.BRANDS_DIR
            manager.BRANDS_DIR = Path(tmpdir)

            try:
                path = save_design_system(ds)
                assert path.exists()
                assert (Path(tmpdir) / "test-save" / "brand.yaml").exists()
            finally:
                manager.BRANDS_DIR = original_dir


class TestDeleteDesignSystem:
    """Test deleting design systems."""

    def test_cannot_delete_kearney(self):
        """Should not allow deleting Kearney."""
        with pytest.raises(ValueError, match="Cannot delete default"):
            delete_design_system("kearney")

    def test_delete_nonexistent_returns_false(self):
        """Deleting non-existent should return False."""
        result = delete_design_system("nonexistent-to-delete")
        assert result is False


class TestGetDesignSystemInfo:
    """Test getting design system info."""

    def test_get_kearney_info(self):
        """Should return info about Kearney."""
        info = get_design_system_info("kearney")
        assert info is not None
        assert info["slug"] == "kearney"
        assert info["name"] == "Kearney"
        assert info["primary_color"] == "#7823DC"

    def test_get_nonexistent_returns_kearney(self):
        """Non-existent should fall back to Kearney info."""
        info = get_design_system_info("nonexistent")
        # Falls back to kearney
        assert info["slug"] == "kearney"
