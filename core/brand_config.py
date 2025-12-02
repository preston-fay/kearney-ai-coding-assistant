# core/brand_config.py
"""
Brand configuration management with override support.

Supports:
- Default Kearney brand rules
- Project-level brand overrides for client branding
- Enforced rules that cannot be overridden

Usage:
    from core.brand_config import (
        load_brand_config,
        get_brand_colors,
        is_color_allowed,
        BrandConfig,
    )

    # Load brand config for a project
    config = load_brand_config(Path("."))

    # Check if a color is allowed
    if is_color_allowed("#0066CC", config):
        print("Color is allowed")
"""

from pathlib import Path
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, field

import yaml


# Default Kearney brand configuration
DEFAULT_BRAND_CONFIG = {
    "brand_name": "Kearney",
    "colors": {
        "primary": "#7823DC",  # Kearney Purple
        "secondary": "#1E1E1E",  # Dark background
        "background": {
            "dark": "#1E1E1E",
            "light": "#FFFFFF",
        },
        "text": {
            "primary": "#333333",
            "secondary": "#666666",
            "muted": "#999999",
        },
        "accent": ["#7823DC", "#333333", "#666666"],
        "forbidden": [
            "#00FF00", "#00ff00",
            "#2E7D32", "#2e7d32",
            "#4CAF50", "#4caf50",
            "#008000", "#008000",
            "#228B22", "#228b22",
            "#32CD32", "#32cd32",
            "#90EE90", "#90ee90",
        ],
    },
    "typography": {
        "primary": "Inter",
        "fallback": "Arial",
        "weights": [400, 500, 600],
    },
    "charts": {
        "gridlines": False,
        "data_labels_outside": True,
        "default_colors": ["#7823DC", "#333333", "#666666", "#999999", "#CCCCCC"],
    },
    "enforced": [
        "no_emojis",
        "no_gridlines",
        "data_labels_outside",
    ],
}


@dataclass
class BrandConfig:
    """Brand configuration container."""
    brand_name: str = "Kearney"
    is_override: bool = False
    override_path: Optional[str] = None

    # Colors
    primary_color: str = "#7823DC"
    secondary_color: str = "#1E1E1E"
    background_dark: str = "#1E1E1E"
    background_light: str = "#FFFFFF"
    accent_colors: List[str] = field(default_factory=lambda: ["#7823DC", "#333333", "#666666"])
    forbidden_colors: List[str] = field(default_factory=list)
    allowed_colors: Set[str] = field(default_factory=set)

    # Typography
    primary_font: str = "Inter"
    fallback_font: str = "Arial"
    font_weights: List[int] = field(default_factory=lambda: [400, 500, 600])

    # Charts
    gridlines_allowed: bool = False
    data_labels_outside: bool = True
    chart_colors: List[str] = field(default_factory=lambda: ["#7823DC", "#333333", "#666666"])

    # Enforced rules (cannot be overridden)
    enforced_rules: List[str] = field(default_factory=lambda: ["no_emojis", "no_gridlines"])

    # Logo
    logo_path: Optional[str] = None
    logo_placement: str = "top-right"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "brand_name": self.brand_name,
            "is_override": self.is_override,
            "override_path": self.override_path,
            "colors": {
                "primary": self.primary_color,
                "secondary": self.secondary_color,
                "background": {
                    "dark": self.background_dark,
                    "light": self.background_light,
                },
                "accent": self.accent_colors,
                "forbidden": self.forbidden_colors,
            },
            "typography": {
                "primary": self.primary_font,
                "fallback": self.fallback_font,
                "weights": self.font_weights,
            },
            "charts": {
                "gridlines": self.gridlines_allowed,
                "data_labels_outside": self.data_labels_outside,
                "default_colors": self.chart_colors,
            },
            "enforced": self.enforced_rules,
            "logo": {
                "path": self.logo_path,
                "placement": self.logo_placement,
            } if self.logo_path else None,
        }


def _load_yaml_file(path: Path) -> Optional[Dict[str, Any]]:
    """Load a YAML file safely."""
    if not path.exists():
        return None
    try:
        return yaml.safe_load(path.read_text())
    except (yaml.YAMLError, IOError):
        return None


def load_brand_config(project_path: Path) -> BrandConfig:
    """
    Load brand configuration with override support.

    Priority:
    1. config/brand_override.yaml (if exists and enabled)
    2. config/governance/brand.yaml (default)
    3. Hardcoded defaults

    Args:
        project_path: Root path of the project

    Returns:
        BrandConfig with merged settings
    """
    project_path = Path(project_path)

    # Initialize with defaults
    config = BrandConfig()
    config.forbidden_colors = DEFAULT_BRAND_CONFIG["colors"]["forbidden"].copy()
    config.chart_colors = DEFAULT_BRAND_CONFIG["charts"]["default_colors"].copy()
    config.enforced_rules = DEFAULT_BRAND_CONFIG["enforced"].copy()

    # Try to load default brand.yaml
    default_path = project_path / "config" / "governance" / "brand.yaml"
    default_config = _load_yaml_file(default_path)

    if default_config:
        _apply_config(config, default_config)

    # Check for override
    override_path = project_path / "config" / "brand_override.yaml"
    override_config = _load_yaml_file(override_path)

    if override_config and override_config.get("enabled", False):
        config.is_override = True
        config.override_path = str(override_path)
        _apply_config(config, override_config)

        # Merge forbidden colors from override
        if "colors" in override_config and "forbidden" in override_config["colors"]:
            additional_forbidden = override_config["colors"]["forbidden"]
            for color in additional_forbidden:
                if color not in config.forbidden_colors:
                    config.forbidden_colors.append(color)

        # Override enforced rules if specified, but always include core rules
        if "enforced" in override_config:
            config.enforced_rules = override_config["enforced"]
        # Always enforce these regardless of override
        core_enforced = ["no_emojis", "no_gridlines"]
        for rule in core_enforced:
            if rule not in config.enforced_rules:
                config.enforced_rules.append(rule)

    # Build allowed colors set
    config.allowed_colors = _build_allowed_colors(config)

    return config


def _apply_config(config: BrandConfig, data: Dict[str, Any]) -> None:
    """Apply configuration data to BrandConfig object."""
    if "brand_name" in data:
        config.brand_name = data["brand_name"]

    if "colors" in data:
        colors = data["colors"]
        if "primary" in colors:
            config.primary_color = colors["primary"]
        if "secondary" in colors:
            config.secondary_color = colors["secondary"]
        if "background" in colors:
            bg = colors["background"]
            if "dark" in bg:
                config.background_dark = bg["dark"]
            if "light" in bg:
                config.background_light = bg["light"]
        if "accent" in colors:
            config.accent_colors = colors["accent"]

    if "typography" in data:
        typo = data["typography"]
        if "primary" in typo:
            config.primary_font = typo["primary"]
        if "fallback" in typo:
            config.fallback_font = typo["fallback"]
        if "weights" in typo:
            config.font_weights = typo["weights"]

    if "charts" in data:
        charts = data["charts"]
        # Note: gridlines is ALWAYS false due to enforced rules
        if "gridlines" in charts:
            config.gridlines_allowed = charts["gridlines"]
        if "data_labels_outside" in charts:
            config.data_labels_outside = charts["data_labels_outside"]
        if "default_colors" in charts:
            config.chart_colors = charts["default_colors"]

    if "logo" in data:
        logo = data["logo"]
        if "path" in logo:
            config.logo_path = logo["path"]
        if "placement" in logo:
            config.logo_placement = logo["placement"]


def _build_allowed_colors(config: BrandConfig) -> Set[str]:
    """Build the set of allowed colors from config."""
    allowed = set()

    # Add primary, secondary, backgrounds
    allowed.add(config.primary_color.lower())
    allowed.add(config.secondary_color.lower())
    allowed.add(config.background_dark.lower())
    allowed.add(config.background_light.lower())

    # Add accent colors
    for color in config.accent_colors:
        allowed.add(color.lower())

    # Add chart colors
    for color in config.chart_colors:
        allowed.add(color.lower())

    # Add common neutral colors
    neutrals = ["#ffffff", "#f5f5f5", "#333333", "#666666", "#999999", "#cccccc", "#e0e0e0"]
    for color in neutrals:
        allowed.add(color)

    return allowed


def is_color_allowed(color: str, config: BrandConfig) -> bool:
    """
    Check if a color is allowed under the brand config.

    Args:
        color: Hex color string (e.g., "#7823DC")
        config: BrandConfig to check against

    Returns:
        True if color is allowed
    """
    normalized = color.lower().strip()

    # Check if explicitly forbidden
    for forbidden in config.forbidden_colors:
        if normalized == forbidden.lower():
            return False

    # Check if explicitly allowed
    if normalized in config.allowed_colors:
        return True

    # Default: allow (only forbidden colors are blocked)
    return True


def is_color_forbidden(color: str, config: BrandConfig) -> bool:
    """
    Check if a color is explicitly forbidden.

    Args:
        color: Hex color string (e.g., "#00FF00")
        config: BrandConfig to check against

    Returns:
        True if color is forbidden
    """
    normalized = color.lower().strip()
    for forbidden in config.forbidden_colors:
        if normalized == forbidden.lower():
            return True
    return False


def get_brand_colors(config: BrandConfig) -> Dict[str, str]:
    """
    Get the brand colors from config.

    Args:
        config: BrandConfig

    Returns:
        Dict of color name to hex value
    """
    return {
        "primary": config.primary_color,
        "secondary": config.secondary_color,
        "background_dark": config.background_dark,
        "background_light": config.background_light,
    }


def get_chart_colors(config: BrandConfig) -> List[str]:
    """
    Get the chart color palette from config.

    Args:
        config: BrandConfig

    Returns:
        List of hex colors for charts
    """
    return config.chart_colors.copy()


def is_rule_enforced(rule: str, config: BrandConfig) -> bool:
    """
    Check if a rule is enforced (cannot be overridden).

    Args:
        rule: Rule name (e.g., "no_emojis")
        config: BrandConfig

    Returns:
        True if rule is enforced
    """
    return rule in config.enforced_rules


def create_brand_override_template() -> str:
    """
    Create a template brand_override.yaml file content.

    Returns:
        YAML content string
    """
    template = """# Brand Override Configuration
# This file overrides default Kearney branding for this project.
# Delete this file to revert to Kearney defaults.

enabled: false  # Set to true to enable override

brand_name: "Client Name"

colors:
  primary: "#0066CC"  # Client primary color
  secondary: "#FF6600"  # Client secondary color
  background:
    dark: "#1A1A2E"
    light: "#FFFFFF"

  # Additional colors to forbid (in addition to greens)
  forbidden:
    - "#FF0000"  # Example: competitor color

typography:
  primary: "Helvetica Neue"
  fallback: "Helvetica"
  weights: [400, 700]

charts:
  gridlines: false  # Always enforced as false
  data_labels_outside: true
  default_colors:
    - "#0066CC"
    - "#FF6600"
    - "#333333"

# Logo placement (optional)
logo:
  path: "config/assets/client_logo.png"
  placement: "top-right"  # top-left, top-right, bottom-left, bottom-right

# Rules that are ALWAYS enforced regardless of override:
# - no_emojis
# - no_gridlines
# These cannot be disabled.

enforced:
  - no_emojis
  - no_gridlines
  - data_labels_outside
"""
    return template


def save_brand_override_template(project_path: Path) -> Path:
    """
    Save a brand override template to a project.

    Args:
        project_path: Root path of the project

    Returns:
        Path to the created file
    """
    config_dir = Path(project_path) / "config"
    config_dir.mkdir(parents=True, exist_ok=True)

    override_path = config_dir / "brand_override.yaml"
    override_path.write_text(create_brand_override_template())

    return override_path


def get_brand_summary(config: BrandConfig) -> str:
    """
    Get a human-readable summary of brand config.

    Args:
        config: BrandConfig

    Returns:
        Summary string
    """
    lines = [
        f"Brand: {config.brand_name}",
        f"Override Active: {'Yes' if config.is_override else 'No'}",
        "",
        "Colors:",
        f"  Primary: {config.primary_color}",
        f"  Secondary: {config.secondary_color}",
        f"  Chart Palette: {', '.join(config.chart_colors[:3])}...",
        "",
        "Typography:",
        f"  Font: {config.primary_font} ({config.fallback_font} fallback)",
        "",
        "Enforced Rules:",
    ]

    for rule in config.enforced_rules:
        lines.append(f"  - {rule}")

    if config.logo_path:
        lines.extend([
            "",
            f"Logo: {config.logo_path} ({config.logo_placement})",
        ])

    return "\n".join(lines)
