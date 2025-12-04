"""
Bridge between DesignSystem and KDSTheme with accessibility enforcement.

Provides functions to convert a DesignSystem into a KDSTheme that
can be consumed by all KACA engines. Automatically enforces
WCAG 2.1 AA contrast requirements.
"""

from typing import TYPE_CHECKING, Optional

from .schema import DesignSystem
from .accessibility import (
    ensure_contrast,
    get_strategy_for_context,
    make_accessible_palette,
)

if TYPE_CHECKING:
    from core.kds_theme import KDSTheme


def apply_design_system(
    ds: DesignSystem,
    context: str = "webapp",
    dark_mode: bool = True,
) -> 'KDSTheme':
    """
    Convert DesignSystem to KDSTheme with accessibility enforcement.

    Args:
        ds: DesignSystem to apply.
        context: Output context ("webapp", "dashboard", "chart", etc.).
        dark_mode: Whether to use dark mode colors.

    Returns:
        KDSTheme with WCAG 2.1 AA compliant colors.
    """
    from core.kds_theme import KDSTheme

    # Determine background based on mode
    if dark_mode:
        bg_color = ds.backgrounds.get('dark', '#1E1E1E')
        text_color = ds.text.get('on_dark', '#FFFFFF')
    else:
        bg_color = ds.backgrounds.get('light', '#FFFFFF')
        text_color = ds.text.get('on_light', '#333333')

    # Ensure primary color has sufficient contrast
    primary = ensure_contrast(
        ds.colors.primary,
        bg_color,
        min_ratio=4.5,
        strategy=get_strategy_for_context("body")
    )

    # Ensure secondary color has sufficient contrast
    secondary = ds.colors.secondary or ds.colors.primary
    secondary = ensure_contrast(
        secondary,
        bg_color,
        min_ratio=4.5,
        strategy=get_strategy_for_context("body")
    )

    # Ensure text color has sufficient contrast
    text = ensure_contrast(
        text_color,
        bg_color,
        min_ratio=4.5,
        strategy="binary"
    )

    # Build accessible chart palette
    chart_palette = ds.colors.chart_palette[:6] if ds.colors.chart_palette else [ds.colors.primary]
    chart_palette = make_accessible_palette(
        chart_palette,
        bg_color,
        min_ratio=3.0,  # Charts use large text threshold
        strategy="tint"
    )

    # Pad palette to at least 6 colors if needed
    while len(chart_palette) < 6:
        chart_palette.append(primary)

    # Get accent color
    accent = ds.colors.accent or ds.colors.primary

    # Get semantic colors with defaults
    semantic = ds.colors.semantic
    positive = semantic.get('success', '#D4A5FF')
    negative = semantic.get('error', '#FF6F61')
    warning = semantic.get('warning', '#FFB74D')
    info = semantic.get('info', '#64B5F6')

    # Build font string
    body_font = ds.typography.body
    heading_font = ds.typography.heading
    font_family = f"{body_font.family}, {body_font.fallback}"
    heading_font_str = f"{heading_font.family}, {heading_font.fallback}"

    return KDSTheme(
        primary=primary,
        primary_light=chart_palette[1] if len(chart_palette) > 1 else primary,
        primary_dark=secondary,
        primary_pale=chart_palette[-1] if chart_palette else primary,
        secondary=secondary,
        accent=accent,
        positive=positive,
        negative=negative,
        warning=warning,
        info=info,
        background_dark=ds.backgrounds.get('dark', '#1E1E1E'),
        background_light=ds.backgrounds.get('light', '#FFFFFF'),
        surface_dark=ds.backgrounds.get('dark', '#1E1E1E'),
        surface_light=ds.backgrounds.get('light', '#FFFFFF'),
        text_light=ds.text.get('on_dark', '#FFFFFF'),
        text_dark=ds.text.get('on_light', '#333333'),
        text_muted='#666666',
        chart_palette=tuple(chart_palette),
        font_family=font_family,
        forbidden_colors=tuple(ds.colors.forbidden) if ds.colors.forbidden else (),
    )


def resolve_theme(spec: Optional[dict] = None) -> 'KDSTheme':
    """
    Resolve KDSTheme from project spec.

    This is the main entry point for engines. It loads the appropriate
    design system based on the spec and applies it with accessibility
    enforcement.

    Args:
        spec: Project specification dict (from spec.yaml).
              If None or missing design_system key, uses default.

    Returns:
        KDSTheme ready for use by engines.
    """
    from .manager import load_design_system, get_default

    spec = spec or {}

    # Get design system slug from spec, default to Kearney
    ds_slug = spec.get('project', {}).get('design_system', get_default())

    # Load the design system
    ds = load_design_system(ds_slug)

    # Determine context and mode from spec
    project_type = spec.get('project', {}).get('type', 'webapp')
    dark_mode = spec.get('presentation', {}).get('dark_mode', True)

    # Apply with accessibility enforcement
    return apply_design_system(ds, context=project_type, dark_mode=dark_mode)


def get_logo_for_context(ds: DesignSystem, context: str) -> Optional[dict]:
    """
    Get logo configuration for a specific context.

    Logos are only used in webapps and dashboards, not in charts,
    PPTX, DOCX, or XLSX outputs.

    Args:
        ds: DesignSystem containing logo definitions.
        context: Output context ("webapp_header", "dashboard_header", etc.).

    Returns:
        Dictionary with path, width, height if logo exists for context,
        None otherwise.
    """
    # Allowed contexts for logos
    allowed_contexts = {
        'webapp_header',
        'dashboard_header',
        'webapp_footer',
        'dashboard_footer',
    }

    if context not in allowed_contexts:
        return None

    for key, logo in ds.logos.items():
        if context in logo.placement:
            return {
                'path': logo.path,
                'width': logo.width,
                'height': logo.height,
            }

    return None
