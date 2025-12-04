"""Tests for design system applicator."""

import pytest

from core.design_system.applicator import (
    apply_design_system,
    resolve_theme,
    get_logo_for_context,
)
from core.design_system.manager import load_design_system
from core.design_system.schema import DesignSystem, Meta, ColorPalette, Typography, FontFamily, Logo
from core.design_system.accessibility import contrast_ratio


class TestApplyDesignSystem:
    """Test applying design system to create KDSTheme."""

    def test_creates_kds_theme(self):
        """Should create a KDSTheme from DesignSystem."""
        ds = load_design_system("kearney")
        theme = apply_design_system(ds)

        # Should have primary color
        assert theme.primary is not None
        # Should have chart palette
        assert len(theme.chart_palette) >= 6

    def test_enforces_accessibility(self):
        """Primary color should meet WCAG AA contrast."""
        ds = load_design_system("kearney")
        theme = apply_design_system(ds, dark_mode=True)

        # Check primary has sufficient contrast
        ratio = contrast_ratio(theme.primary, theme.background_dark)
        assert ratio >= 4.5

    def test_chart_palette_accessible(self):
        """Chart palette colors should have sufficient contrast."""
        ds = load_design_system("kearney")
        theme = apply_design_system(ds, dark_mode=True)

        for color in theme.chart_palette:
            ratio = contrast_ratio(color, theme.background_dark)
            # Charts use 3:1 threshold
            assert ratio >= 3.0

    def test_includes_forbidden_colors(self):
        """Theme should include forbidden colors from design system."""
        ds = load_design_system("kearney")
        theme = apply_design_system(ds)

        assert len(theme.forbidden_colors) > 0
        assert "#00FF00" in theme.forbidden_colors

    def test_dark_mode(self):
        """Dark mode should use dark background."""
        ds = load_design_system("kearney")
        theme = apply_design_system(ds, dark_mode=True)

        assert theme.background_dark == "#1E1E1E"

    def test_light_mode(self):
        """Light mode should still work."""
        ds = load_design_system("kearney")
        theme = apply_design_system(ds, dark_mode=False)

        # Should still have accessible colors
        assert theme.primary is not None


class TestResolveTheme:
    """Test theme resolution from spec."""

    def test_default_spec(self):
        """Empty spec should use Kearney defaults."""
        theme = resolve_theme({})
        assert theme.primary is not None

    def test_none_spec(self):
        """None spec should use Kearney defaults."""
        theme = resolve_theme(None)
        assert theme.primary is not None

    def test_spec_with_design_system(self):
        """Should use design system from spec."""
        spec = {"project": {"design_system": "kearney"}}
        theme = resolve_theme(spec)
        assert theme.primary is not None

    def test_spec_with_unknown_design_system(self):
        """Unknown design system should fall back to Kearney."""
        spec = {"project": {"design_system": "unknown-brand"}}
        theme = resolve_theme(spec)
        # Should still work, falling back to Kearney
        assert theme.primary is not None


class TestGetLogoForContext:
    """Test logo resolution for contexts."""

    def test_no_logos_returns_none(self):
        """Design system without logos should return None."""
        ds = load_design_system("kearney")
        result = get_logo_for_context(ds, "webapp_header")
        assert result is None

    def test_disallowed_context_returns_none(self):
        """Non-webapp/dashboard contexts should return None."""
        ds = DesignSystem(
            meta=Meta(name="Test", slug="test"),
            colors=ColorPalette(primary="#FF0000"),
            typography=Typography(
                heading=FontFamily(family="Inter", fallback="Arial"),
                body=FontFamily(family="Inter", fallback="Arial"),
                monospace=FontFamily(family="Courier", fallback="monospace"),
            ),
            logos={"primary": Logo(path="logo.svg", placement=["pptx_cover"])},
        )
        # Charts and PPTX should not get logos
        result = get_logo_for_context(ds, "chart_title")
        assert result is None

    def test_webapp_header_gets_logo(self):
        """Webapp header should get logo if configured."""
        ds = DesignSystem(
            meta=Meta(name="Test", slug="test"),
            colors=ColorPalette(primary="#FF0000"),
            typography=Typography(
                heading=FontFamily(family="Inter", fallback="Arial"),
                body=FontFamily(family="Inter", fallback="Arial"),
                monospace=FontFamily(family="Courier", fallback="monospace"),
            ),
            logos={"primary": Logo(
                path="config/brands/test/logo.svg",
                width=200,
                height=50,
                placement=["webapp_header", "dashboard_header"],
            )},
        )
        result = get_logo_for_context(ds, "webapp_header")
        assert result is not None
        assert result["path"] == "config/brands/test/logo.svg"
        assert result["width"] == 200
