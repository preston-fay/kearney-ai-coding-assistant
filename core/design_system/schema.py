"""
Design System schema and validation.

Defines the DesignSystem dataclass and related types for brand configuration.
Supports loading from and saving to YAML files.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from pathlib import Path
import re

import yaml

# Regex pattern for valid hex colors
HEX_PATTERN = re.compile(r'^#[0-9A-Fa-f]{6}$')


def validate_hex_color(color: str) -> bool:
    """Validate a hex color string."""
    return bool(HEX_PATTERN.match(color))


@dataclass
class FontFamily:
    """Typography font family configuration."""
    family: str
    fallback: str
    weights: List[int] = field(default_factory=lambda: [400, 500, 600])
    web_font_url: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> 'FontFamily':
        """Create FontFamily from dictionary."""
        return cls(
            family=data.get('family', 'Inter'),
            fallback=data.get('fallback', 'Arial, sans-serif'),
            weights=data.get('weights', [400, 500, 600]),
            web_font_url=data.get('web_font_url'),
        )

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        result = {
            'family': self.family,
            'fallback': self.fallback,
            'weights': self.weights,
        }
        if self.web_font_url:
            result['web_font_url'] = self.web_font_url
        return result


@dataclass
class Typography:
    """Typography configuration for headings, body, and monospace text."""
    heading: FontFamily
    body: FontFamily
    monospace: FontFamily

    @classmethod
    def from_dict(cls, data: dict) -> 'Typography':
        """Create Typography from dictionary."""
        return cls(
            heading=FontFamily.from_dict(data.get('heading', {})),
            body=FontFamily.from_dict(data.get('body', {})),
            monospace=FontFamily.from_dict(data.get('monospace', {
                'family': 'Courier New',
                'fallback': 'monospace',
                'weights': [400],
            })),
        )

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'heading': self.heading.to_dict(),
            'body': self.body.to_dict(),
            'monospace': self.monospace.to_dict(),
        }


@dataclass
class ColorPalette:
    """Color palette configuration with validation."""
    primary: str
    secondary: Optional[str] = None
    accent: Optional[str] = None
    semantic: Dict[str, str] = field(default_factory=dict)
    chart_palette: List[str] = field(default_factory=list)
    forbidden: List[str] = field(default_factory=list)

    def __post_init__(self):
        """Validate colors after initialization."""
        self._validate_colors()

    def _validate_colors(self):
        """Validate that all colors are valid hex codes."""
        for color in [self.primary, self.secondary, self.accent]:
            if color and not validate_hex_color(color):
                raise ValueError(f"Invalid hex color: {color}")

        for color in self.chart_palette:
            if not validate_hex_color(color):
                raise ValueError(f"Invalid hex color in chart_palette: {color}")

        for key, color in self.semantic.items():
            if not validate_hex_color(color):
                raise ValueError(f"Invalid hex color for semantic.{key}: {color}")

    @classmethod
    def from_dict(cls, data: dict) -> 'ColorPalette':
        """Create ColorPalette from dictionary."""
        return cls(
            primary=data.get('primary', '#7823DC'),
            secondary=data.get('secondary'),
            accent=data.get('accent'),
            semantic=data.get('semantic', {}),
            chart_palette=data.get('chart_palette', []),
            forbidden=data.get('forbidden', []),
        )

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        result = {
            'primary': self.primary,
        }
        if self.secondary:
            result['secondary'] = self.secondary
        if self.accent:
            result['accent'] = self.accent
        if self.semantic:
            result['semantic'] = self.semantic
        if self.chart_palette:
            result['chart_palette'] = self.chart_palette
        if self.forbidden:
            result['forbidden'] = self.forbidden
        return result


@dataclass
class Logo:
    """Logo asset configuration."""
    path: str
    width: Optional[int] = None
    height: Optional[int] = None
    placement: List[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict) -> 'Logo':
        """Create Logo from dictionary."""
        return cls(
            path=data.get('path', ''),
            width=data.get('width'),
            height=data.get('height'),
            placement=data.get('placement', []),
        )

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        result = {'path': self.path}
        if self.width:
            result['width'] = self.width
        if self.height:
            result['height'] = self.height
        if self.placement:
            result['placement'] = self.placement
        return result


@dataclass
class Meta:
    """Design system metadata."""
    name: str
    slug: str
    version: str = "1.0.0"
    source_url: Optional[str] = None
    extraction_mode: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> 'Meta':
        """Create Meta from dictionary."""
        return cls(
            name=data.get('name', 'Unknown'),
            slug=data.get('slug', 'unknown'),
            version=data.get('version', '1.0.0'),
            source_url=data.get('source_url'),
            extraction_mode=data.get('extraction_mode'),
        )

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        result = {
            'name': self.name,
            'slug': self.slug,
            'version': self.version,
        }
        if self.source_url:
            result['source_url'] = self.source_url
        if self.extraction_mode:
            result['extraction_mode'] = self.extraction_mode
        return result


@dataclass
class DesignSystem:
    """
    Complete design system configuration.

    Contains all brand tokens including colors, typography, spacing,
    and optional logo assets. Supports loading from and saving to YAML files.
    """
    meta: Meta
    colors: ColorPalette
    typography: Typography
    spacing: Dict[str, Any] = field(default_factory=lambda: {'base': 8})
    borders: Dict[str, str] = field(default_factory=lambda: {'radius': '4px', 'width': '1px'})
    backgrounds: Dict[str, str] = field(default_factory=lambda: {'dark': '#1E1E1E', 'light': '#FFFFFF'})
    text: Dict[str, str] = field(default_factory=lambda: {'on_dark': '#FFFFFF', 'on_light': '#333333'})
    logos: Dict[str, Logo] = field(default_factory=dict)
    extraction_metadata: Optional[Dict] = None

    @classmethod
    def from_yaml(cls, path: Path) -> 'DesignSystem':
        """
        Load DesignSystem from brand.yaml file.

        Args:
            path: Path to brand.yaml file.

        Returns:
            DesignSystem instance.

        Raises:
            FileNotFoundError: If file doesn't exist.
            yaml.YAMLError: If YAML is invalid.
        """
        with open(path, 'r') as f:
            data = yaml.safe_load(f)
        return cls.from_dict(data)

    @classmethod
    def from_dict(cls, data: dict) -> 'DesignSystem':
        """
        Create DesignSystem from dictionary.

        Args:
            data: Dictionary with design system configuration.

        Returns:
            DesignSystem instance.
        """
        # Parse nested structures
        meta = Meta.from_dict(data.get('meta', {}))
        colors = ColorPalette.from_dict(data.get('colors', {}))
        typography = Typography.from_dict(data.get('typography', {}))

        # Parse logos
        logos = {}
        for key, logo_data in data.get('logos', {}).items():
            if logo_data:  # Skip empty logo definitions
                logos[key] = Logo.from_dict(logo_data)

        return cls(
            meta=meta,
            colors=colors,
            typography=typography,
            spacing=data.get('spacing', {'base': 8}),
            borders=data.get('borders', {'radius': '4px', 'width': '1px'}),
            backgrounds=data.get('backgrounds', {'dark': '#1E1E1E', 'light': '#FFFFFF'}),
            text=data.get('text', {'on_dark': '#FFFFFF', 'on_light': '#333333'}),
            logos=logos,
            extraction_metadata=data.get('extraction_metadata'),
        )

    def to_dict(self) -> dict:
        """
        Convert to dictionary for YAML export.

        Returns:
            Dictionary representation of the design system.
        """
        result = {
            'meta': self.meta.to_dict(),
            'colors': self.colors.to_dict(),
            'typography': self.typography.to_dict(),
            'spacing': self.spacing,
            'borders': self.borders,
            'backgrounds': self.backgrounds,
            'text': self.text,
        }

        if self.logos:
            result['logos'] = {k: v.to_dict() for k, v in self.logos.items()}

        if self.extraction_metadata:
            result['extraction_metadata'] = self.extraction_metadata

        return result

    def save(self, path: Path) -> None:
        """
        Save to brand.yaml file.

        Args:
            path: Path to save the brand.yaml file.
        """
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w') as f:
            yaml.dump(self.to_dict(), f, default_flow_style=False, sort_keys=False)

    @property
    def slug(self) -> str:
        """Get the design system slug."""
        return self.meta.slug

    @property
    def name(self) -> str:
        """Get the design system name."""
        return self.meta.name
