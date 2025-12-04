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
