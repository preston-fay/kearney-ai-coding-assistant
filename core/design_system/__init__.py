"""
Design System Module for KACA.

Provides centralized brand theming with WCAG 2.1 AA accessibility compliance.
Supports multiple design systems while defaulting to Kearney branding.

Usage:
    from core.design_system import load_design_system, resolve_theme

    # Load a specific design system
    ds = load_design_system("kearney")

    # Resolve theme from project spec (recommended)
    theme = resolve_theme(spec)

    # Apply with accessibility enforcement
    from core.design_system import apply_design_system
    theme = apply_design_system(ds)

Key Components:
    - schema: DesignSystem dataclass and validation
    - accessibility: WCAG 2.1 AA contrast enforcement
    - applicator: DesignSystem to KDSTheme bridge
    - manager: CRUD operations for design systems
"""

from .schema import (
    DesignSystem,
    Meta,
    ColorPalette,
    Typography,
    FontFamily,
    Logo,
)
from .manager import (
    load_design_system,
    save_design_system,
    list_design_systems,
    get_default,
    delete_design_system,
    create_from_url,
    slugify,
)
from .applicator import (
    apply_design_system,
    resolve_theme,
)
from .accessibility import (
    contrast_ratio,
    ensure_contrast,
    validate_wcag_aa,
    relative_luminance,
)

__all__ = [
    # Schema
    "DesignSystem",
    "Meta",
    "ColorPalette",
    "Typography",
    "FontFamily",
    "Logo",
    # Manager
    "load_design_system",
    "save_design_system",
    "list_design_systems",
    "get_default",
    "delete_design_system",
    "create_from_url",
    "slugify",
    # Applicator
    "apply_design_system",
    "resolve_theme",
    # Accessibility
    "contrast_ratio",
    "ensure_contrast",
    "validate_wcag_aa",
    "relative_luminance",
]
