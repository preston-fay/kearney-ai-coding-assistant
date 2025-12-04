"""
Design system CRUD operations.

Provides functions for loading, saving, listing, and deleting
design system configurations from config/brands/.
"""

from pathlib import Path
from typing import List, Optional
import shutil

from .schema import DesignSystem

# Default paths
BRANDS_DIR = Path(__file__).parent.parent.parent / "config" / "brands"
DEFAULT_BRAND = "kearney"


def get_default() -> str:
    """
    Return default design system slug.

    Returns:
        "kearney" (the default brand).
    """
    return DEFAULT_BRAND


def get_brands_dir() -> Path:
    """
    Get the brands directory path.

    Returns:
        Path to config/brands/.
    """
    return BRANDS_DIR


def list_design_systems() -> List[str]:
    """
    Return list of available design system slugs.

    Returns:
        List of slug strings for available design systems.
    """
    if not BRANDS_DIR.exists():
        return [DEFAULT_BRAND]

    slugs = []
    for d in BRANDS_DIR.iterdir():
        if d.is_dir() and not d.name.startswith('.'):
            brand_yaml = d / "brand.yaml"
            if brand_yaml.exists():
                slugs.append(d.name)

    # Ensure default is always first
    if DEFAULT_BRAND in slugs:
        slugs.remove(DEFAULT_BRAND)
        slugs.insert(0, DEFAULT_BRAND)
    elif DEFAULT_BRAND not in slugs:
        # Always include default even if file doesn't exist yet
        slugs.insert(0, DEFAULT_BRAND)

    return slugs


def design_system_exists(slug: str) -> bool:
    """
    Check if a design system exists.

    Args:
        slug: Design system slug.

    Returns:
        True if the brand.yaml exists.
    """
    brand_path = BRANDS_DIR / slug / "brand.yaml"
    return brand_path.exists()


def load_design_system(slug: str) -> DesignSystem:
    """
    Load and parse brand.yaml for given slug.

    Args:
        slug: Design system slug (e.g., "kearney").

    Returns:
        DesignSystem instance.

    Raises:
        FileNotFoundError: If default brand not found.
    """
    brand_path = BRANDS_DIR / slug / "brand.yaml"

    if not brand_path.exists():
        if slug != DEFAULT_BRAND:
            # Fall back to Kearney if requested brand not found
            return load_design_system(DEFAULT_BRAND)
        raise FileNotFoundError(f"Default brand not found: {brand_path}")

    return DesignSystem.from_yaml(brand_path)


def save_design_system(ds: DesignSystem) -> Path:
    """
    Save DesignSystem to config/brands/{slug}/brand.yaml.

    Args:
        ds: DesignSystem to save.

    Returns:
        Path to the saved brand.yaml file.
    """
    brand_dir = BRANDS_DIR / ds.meta.slug
    brand_dir.mkdir(parents=True, exist_ok=True)

    brand_path = brand_dir / "brand.yaml"
    ds.save(brand_path)

    return brand_path


def delete_design_system(slug: str) -> bool:
    """
    Remove design system directory.

    Cannot delete the default 'kearney' design system.

    Args:
        slug: Design system slug to delete.

    Returns:
        True if deleted, False if didn't exist.

    Raises:
        ValueError: If attempting to delete 'kearney'.
    """
    if slug == DEFAULT_BRAND:
        raise ValueError("Cannot delete default Kearney design system")

    brand_dir = BRANDS_DIR / slug
    if brand_dir.exists():
        shutil.rmtree(brand_dir)
        return True
    return False


def get_design_system_info(slug: str) -> Optional[dict]:
    """
    Get summary information about a design system.

    Args:
        slug: Design system slug.

    Returns:
        Dictionary with name, version, and color info, or None if not found.
    """
    try:
        ds = load_design_system(slug)
        return {
            "slug": ds.meta.slug,
            "name": ds.meta.name,
            "version": ds.meta.version,
            "primary_color": ds.colors.primary,
            "has_logo": bool(ds.logos),
            "source_url": ds.meta.source_url,
        }
    except FileNotFoundError:
        return None


def copy_logo_to_brand(slug: str, source_path: Path, logo_key: str = "primary") -> str:
    """
    Copy a logo file to a brand's directory.

    Args:
        slug: Design system slug.
        source_path: Path to the logo file.
        logo_key: Key for the logo (e.g., "primary", "icon").

    Returns:
        Relative path to the copied logo.
    """
    brand_dir = BRANDS_DIR / slug
    brand_dir.mkdir(parents=True, exist_ok=True)

    suffix = source_path.suffix
    dest_name = f"logo_{logo_key}{suffix}"
    dest_path = brand_dir / dest_name

    shutil.copy2(source_path, dest_path)

    return str(dest_path.relative_to(BRANDS_DIR.parent.parent))


def create_from_url(
    url: str,
    slug: str,
    name: str,
    mode: str = "conservative"
) -> DesignSystem:
    """
    Create a design system from website extraction.

    Extracts brand tokens (colors, fonts, logo) from a website and
    creates a new design system.

    Args:
        url: Website URL to extract from.
        slug: Slug for the new design system (e.g., "acme-corp").
        name: Display name for the brand (e.g., "Acme Corporation").
        mode: Extraction mode ("conservative" or "moderate").

    Returns:
        The created DesignSystem.
    """
    from .extractor import extract_from_url
    from .schema import (
        DesignSystem,
        Meta,
        ColorPalette,
        Typography,
        FontFamily,
        Logo,
    )

    # Extract brand tokens from URL
    data = extract_from_url(url, mode)

    # Build color palette
    colors = data.get('colors', [])
    primary = colors[0] if colors else "#7823DC"  # Fallback to Kearney purple
    secondary = colors[1] if len(colors) > 1 else None
    accent = colors[2] if len(colors) > 2 else None
    chart_palette = colors[:6] if colors else [primary]

    # Build typography
    fonts = data.get('fonts', [])
    primary_font = fonts[0] if fonts else "Inter"
    body_font = fonts[1] if len(fonts) > 1 else primary_font

    typography = Typography(
        heading=FontFamily(
            family=primary_font,
            fallback="Arial, sans-serif",
            weights=[400, 500, 600],
        ),
        body=FontFamily(
            family=body_font,
            fallback="Arial, sans-serif",
            weights=[400, 500],
        ),
        monospace=FontFamily(
            family="Courier New",
            fallback="monospace",
            weights=[400],
        ),
    )

    # Build logos (if found)
    logos = {}
    logo_url = data.get('logo_url')
    if logo_url:
        logos['primary'] = Logo(
            path=logo_url,  # External URL for now
            placement=['webapp_header', 'dashboard_header'],
        )

    # Create the design system
    ds = DesignSystem(
        meta=Meta(
            name=name,
            slug=slug,
            version="1.0.0",
            source_url=url,
            extraction_mode=mode,
        ),
        colors=ColorPalette(
            primary=primary,
            secondary=secondary,
            accent=accent,
            chart_palette=chart_palette,
            # Inherit Kearney's forbidden colors (no green)
            forbidden=[
                "#00FF00",
                "#008000",
                "#4CAF50",
                "#2E7D32",
            ],
        ),
        typography=typography,
        spacing={'base': 8},
        borders={'radius': '4px', 'width': '1px'},
        backgrounds={'dark': '#1E1E1E', 'light': '#FFFFFF'},
        text={'on_dark': '#FFFFFF', 'on_light': '#333333'},
        logos=logos,
        extraction_metadata=data.get('metadata'),
    )

    # Save and return
    save_design_system(ds)
    return ds


def slugify(name: str) -> str:
    """
    Convert a name to a valid slug.

    Args:
        name: Brand name (e.g., "Acme Corporation").

    Returns:
        Slug (e.g., "acme-corporation").
    """
    import re
    # Convert to lowercase
    slug = name.lower()
    # Replace spaces and underscores with hyphens
    slug = re.sub(r'[\s_]+', '-', slug)
    # Remove non-alphanumeric characters except hyphens
    slug = re.sub(r'[^a-z0-9-]', '', slug)
    # Remove multiple consecutive hyphens
    slug = re.sub(r'-+', '-', slug)
    # Remove leading/trailing hyphens
    slug = slug.strip('-')
    return slug or 'unnamed-brand'


def create_from_assets(
    files: List[Path],
    slug: str,
    name: str,
) -> DesignSystem:
    """
    Create a design system from uploaded assets.

    Analyzes images, PowerPoints, and PDFs to extract brand tokens.

    Args:
        files: List of asset file paths.
        slug: Slug for the new design system.
        name: Display name for the brand.

    Returns:
        The created DesignSystem.
    """
    from .analyzer import analyze_assets
    from .schema import (
        DesignSystem,
        Meta,
        ColorPalette,
        Typography,
        FontFamily,
        Logo,
    )

    # Analyze all provided assets
    data = analyze_assets(files)

    # Build color palette
    colors = data.get('colors', [])
    primary = colors[0] if colors else "#7823DC"
    secondary = colors[1] if len(colors) > 1 else None
    accent = colors[2] if len(colors) > 2 else None
    chart_palette = colors[:6] if colors else [primary]

    # Build typography
    fonts = data.get('fonts', [])
    primary_font = fonts[0] if fonts else "Inter"
    body_font = fonts[1] if len(fonts) > 1 else primary_font

    typography = Typography(
        heading=FontFamily(
            family=primary_font,
            fallback="Arial, sans-serif",
            weights=[400, 500, 600],
        ),
        body=FontFamily(
            family=body_font,
            fallback="Arial, sans-serif",
            weights=[400, 500],
        ),
        monospace=FontFamily(
            family="Courier New",
            fallback="monospace",
            weights=[400],
        ),
    )

    # Build logos from candidates
    logos = {}
    logo_candidates = data.get('logos', [])
    if logo_candidates:
        # Copy the first logo candidate to the brand directory
        first_logo = logo_candidates[0]
        source_path = Path(first_logo['path'])
        if source_path.exists():
            logo_path = copy_logo_to_brand(slug, source_path, 'primary')
            logos['primary'] = Logo(
                path=logo_path,
                width=first_logo.get('width'),
                height=first_logo.get('height'),
                placement=['webapp_header', 'dashboard_header'],
            )

    # Create the design system
    ds = DesignSystem(
        meta=Meta(
            name=name,
            slug=slug,
            version="1.0.0",
            extraction_mode="assets",
        ),
        colors=ColorPalette(
            primary=primary,
            secondary=secondary,
            accent=accent,
            chart_palette=chart_palette,
            forbidden=[
                "#00FF00",
                "#008000",
                "#4CAF50",
                "#2E7D32",
            ],
        ),
        typography=typography,
        spacing={'base': 8},
        borders={'radius': '4px', 'width': '1px'},
        backgrounds={'dark': '#1E1E1E', 'light': '#FFFFFF'},
        text={'on_dark': '#FFFFFF', 'on_light': '#333333'},
        logos=logos,
        extraction_metadata={
            'source': 'assets',
            'files_analyzed': len(files),
        },
    )

    # Save and return
    save_design_system(ds)
    return ds
