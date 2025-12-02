# tests/test_brand_config.py
"""Tests for core/brand_config.py"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import yaml
from core.brand_config import (
    BrandConfig,
    DEFAULT_BRAND_CONFIG,
    load_brand_config,
    is_color_allowed,
    is_color_forbidden,
    get_brand_colors,
    get_chart_colors,
    is_rule_enforced,
    create_brand_override_template,
    save_brand_override_template,
    get_brand_summary,
)


class TestBrandConfig:
    """Tests for BrandConfig dataclass."""

    def test_default_values(self):
        """Test default config values."""
        config = BrandConfig()
        assert config.brand_name == "Kearney"
        assert config.primary_color == "#7823DC"
        assert config.is_override is False

    def test_to_dict(self):
        """Test converting config to dict."""
        config = BrandConfig()
        data = config.to_dict()

        assert data["brand_name"] == "Kearney"
        assert data["colors"]["primary"] == "#7823DC"
        assert data["is_override"] is False


class TestLoadBrandConfig:
    """Tests for load_brand_config function."""

    def test_load_with_no_files(self, tmp_path):
        """Test loading config when no config files exist."""
        config = load_brand_config(tmp_path)

        assert config.brand_name == "Kearney"
        assert config.primary_color == "#7823DC"
        assert config.is_override is False

    def test_load_default_brand_yaml(self, tmp_path):
        """Test loading from default brand.yaml."""
        # Create config/governance/brand.yaml
        config_dir = tmp_path / "config" / "governance"
        config_dir.mkdir(parents=True)

        brand_yaml = {
            "brand_name": "Kearney",
            "colors": {
                "primary": "#7823DC",
                "accent": ["#7823DC", "#444444"],
            },
            "charts": {
                "default_colors": ["#7823DC", "#555555", "#888888"],
            },
        }
        (config_dir / "brand.yaml").write_text(yaml.dump(brand_yaml))

        config = load_brand_config(tmp_path)

        assert config.brand_name == "Kearney"
        assert config.accent_colors == ["#7823DC", "#444444"]

    def test_load_with_override_disabled(self, tmp_path):
        """Test that disabled override is ignored."""
        config_dir = tmp_path / "config"
        config_dir.mkdir(parents=True)

        override_yaml = {
            "enabled": False,
            "brand_name": "Client Corp",
            "colors": {
                "primary": "#0066CC",
            },
        }
        (config_dir / "brand_override.yaml").write_text(yaml.dump(override_yaml))

        config = load_brand_config(tmp_path)

        # Should still be Kearney since override is disabled
        assert config.brand_name == "Kearney"
        assert config.is_override is False

    def test_load_with_override_enabled(self, tmp_path):
        """Test loading with enabled override."""
        config_dir = tmp_path / "config"
        config_dir.mkdir(parents=True)

        override_yaml = {
            "enabled": True,
            "brand_name": "Client Corp",
            "colors": {
                "primary": "#0066CC",
                "secondary": "#FF6600",
            },
        }
        (config_dir / "brand_override.yaml").write_text(yaml.dump(override_yaml))

        config = load_brand_config(tmp_path)

        assert config.brand_name == "Client Corp"
        assert config.primary_color == "#0066CC"
        assert config.is_override is True

    def test_override_adds_forbidden_colors(self, tmp_path):
        """Test that override can add forbidden colors."""
        config_dir = tmp_path / "config"
        config_dir.mkdir(parents=True)

        override_yaml = {
            "enabled": True,
            "brand_name": "Client",
            "colors": {
                "forbidden": ["#FF0000"],  # Add red as forbidden
            },
        }
        (config_dir / "brand_override.yaml").write_text(yaml.dump(override_yaml))

        config = load_brand_config(tmp_path)

        assert "#FF0000" in config.forbidden_colors

    def test_enforced_rules_always_present(self, tmp_path):
        """Test that core enforced rules cannot be removed."""
        config_dir = tmp_path / "config"
        config_dir.mkdir(parents=True)

        override_yaml = {
            "enabled": True,
            "brand_name": "Client",
            "enforced": [],  # Try to remove all rules
        }
        (config_dir / "brand_override.yaml").write_text(yaml.dump(override_yaml))

        config = load_brand_config(tmp_path)

        # Core rules should still be enforced
        assert "no_emojis" in config.enforced_rules
        assert "no_gridlines" in config.enforced_rules

    def test_logo_configuration(self, tmp_path):
        """Test logo configuration from override."""
        config_dir = tmp_path / "config"
        config_dir.mkdir(parents=True)

        override_yaml = {
            "enabled": True,
            "brand_name": "Client",
            "logo": {
                "path": "config/assets/logo.png",
                "placement": "top-left",
            },
        }
        (config_dir / "brand_override.yaml").write_text(yaml.dump(override_yaml))

        config = load_brand_config(tmp_path)

        assert config.logo_path == "config/assets/logo.png"
        assert config.logo_placement == "top-left"


class TestIsColorAllowed:
    """Tests for is_color_allowed function."""

    def test_primary_color_allowed(self):
        """Test that primary color is allowed."""
        config = BrandConfig()
        config.allowed_colors = {"#7823dc"}

        assert is_color_allowed("#7823DC", config) is True
        assert is_color_allowed("#7823dc", config) is True

    def test_forbidden_color_not_allowed(self):
        """Test that forbidden colors are not allowed."""
        config = BrandConfig()
        config.forbidden_colors = ["#00FF00"]

        assert is_color_allowed("#00FF00", config) is False
        assert is_color_allowed("#00ff00", config) is False

    def test_unknown_color_allowed(self):
        """Test that unknown colors are allowed by default."""
        config = BrandConfig()
        config.forbidden_colors = []
        config.allowed_colors = set()

        # Random color should be allowed if not forbidden
        assert is_color_allowed("#ABCDEF", config) is True


class TestIsColorForbidden:
    """Tests for is_color_forbidden function."""

    def test_green_is_forbidden(self):
        """Test that green colors are forbidden."""
        config = BrandConfig()
        config.forbidden_colors = ["#00FF00", "#2E7D32"]

        assert is_color_forbidden("#00FF00", config) is True
        assert is_color_forbidden("#2E7D32", config) is True

    def test_purple_not_forbidden(self):
        """Test that Kearney purple is not forbidden."""
        config = BrandConfig()
        config.forbidden_colors = ["#00FF00"]

        assert is_color_forbidden("#7823DC", config) is False


class TestGetBrandColors:
    """Tests for get_brand_colors function."""

    def test_returns_color_dict(self):
        """Test that function returns color dictionary."""
        config = BrandConfig()
        colors = get_brand_colors(config)

        assert "primary" in colors
        assert "secondary" in colors
        assert colors["primary"] == "#7823DC"


class TestGetChartColors:
    """Tests for get_chart_colors function."""

    def test_returns_chart_palette(self):
        """Test that function returns chart color palette."""
        config = BrandConfig()
        config.chart_colors = ["#7823DC", "#333333", "#666666"]

        colors = get_chart_colors(config)

        assert len(colors) == 3
        assert "#7823DC" in colors

    def test_returns_copy(self):
        """Test that function returns a copy, not the original list."""
        config = BrandConfig()
        config.chart_colors = ["#7823DC"]

        colors = get_chart_colors(config)
        colors.append("#000000")

        # Original should be unchanged
        assert len(config.chart_colors) == 1


class TestIsRuleEnforced:
    """Tests for is_rule_enforced function."""

    def test_no_emojis_enforced(self):
        """Test that no_emojis rule is enforced."""
        config = BrandConfig()
        config.enforced_rules = ["no_emojis", "no_gridlines"]

        assert is_rule_enforced("no_emojis", config) is True

    def test_custom_rule_not_enforced(self):
        """Test that non-enforced rules return False."""
        config = BrandConfig()
        config.enforced_rules = ["no_emojis"]

        assert is_rule_enforced("custom_rule", config) is False


class TestCreateBrandOverrideTemplate:
    """Tests for create_brand_override_template function."""

    def test_creates_valid_yaml(self):
        """Test that template is valid YAML."""
        template = create_brand_override_template()
        data = yaml.safe_load(template)

        assert "enabled" in data
        assert data["enabled"] is False  # Template should be disabled by default

    def test_template_has_all_sections(self):
        """Test that template has all required sections."""
        template = create_brand_override_template()
        data = yaml.safe_load(template)

        assert "brand_name" in data
        assert "colors" in data
        assert "typography" in data
        assert "charts" in data
        assert "enforced" in data


class TestSaveBrandOverrideTemplate:
    """Tests for save_brand_override_template function."""

    def test_creates_file(self, tmp_path):
        """Test that file is created."""
        path = save_brand_override_template(tmp_path)

        assert path.exists()
        assert path.name == "brand_override.yaml"

    def test_creates_config_dir(self, tmp_path):
        """Test that config directory is created."""
        save_brand_override_template(tmp_path)

        assert (tmp_path / "config").exists()


class TestGetBrandSummary:
    """Tests for get_brand_summary function."""

    def test_includes_brand_name(self):
        """Test that summary includes brand name."""
        config = BrandConfig()
        config.brand_name = "TestBrand"

        summary = get_brand_summary(config)

        assert "TestBrand" in summary

    def test_includes_colors(self):
        """Test that summary includes color info."""
        config = BrandConfig()
        config.primary_color = "#7823DC"

        summary = get_brand_summary(config)

        assert "#7823DC" in summary

    def test_includes_override_status(self):
        """Test that summary shows override status."""
        config = BrandConfig()
        config.is_override = True

        summary = get_brand_summary(config)

        assert "Override Active: Yes" in summary

    def test_includes_logo_when_set(self):
        """Test that summary includes logo info when set."""
        config = BrandConfig()
        config.logo_path = "logo.png"
        config.logo_placement = "top-right"

        summary = get_brand_summary(config)

        assert "logo.png" in summary
        assert "top-right" in summary


class TestDefaultBrandConfig:
    """Tests for DEFAULT_BRAND_CONFIG constant."""

    def test_has_required_keys(self):
        """Test that default config has all required keys."""
        assert "brand_name" in DEFAULT_BRAND_CONFIG
        assert "colors" in DEFAULT_BRAND_CONFIG
        assert "typography" in DEFAULT_BRAND_CONFIG
        assert "charts" in DEFAULT_BRAND_CONFIG
        assert "enforced" in DEFAULT_BRAND_CONFIG

    def test_kearney_purple_is_primary(self):
        """Test that Kearney purple is the primary color."""
        assert DEFAULT_BRAND_CONFIG["colors"]["primary"] == "#7823DC"

    def test_gridlines_disabled(self):
        """Test that gridlines are disabled by default."""
        assert DEFAULT_BRAND_CONFIG["charts"]["gridlines"] is False

    def test_green_in_forbidden(self):
        """Test that green colors are forbidden."""
        forbidden = DEFAULT_BRAND_CONFIG["colors"]["forbidden"]
        assert "#00FF00" in forbidden or "#00ff00" in forbidden
