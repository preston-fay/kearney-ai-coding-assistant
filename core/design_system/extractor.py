"""
Web scraping for brand extraction.

Extracts brand tokens (colors, fonts, logos) from client websites.
Supports conservative (single page) and moderate (with CSS files) modes.

Note: This is a Phase 2 implementation stub.
"""

from typing import Dict, List, Any, Optional


def extract_from_url(url: str, mode: str = "conservative") -> Dict[str, Any]:
    """
    Extract brand tokens from website.

    Args:
        url: Website URL.
        mode: Extraction mode:
            - "conservative": Single page, inline styles only
            - "moderate": Includes external CSS files

    Returns:
        Dictionary with:
            - colors: List of hex colors found
            - fonts: List of font families found
            - logo_url: URL to logo if found
            - metadata: Extraction metadata

    Raises:
        NotImplementedError: This is a Phase 2 stub.
    """
    raise NotImplementedError(
        "Web extraction will be implemented in Phase 2. "
        "For now, create design systems manually using brand.yaml files."
    )


def _extract_conservative(url: str) -> Dict[str, Any]:
    """Extract from single page with inline styles only."""
    raise NotImplementedError("Phase 2 implementation")


def _extract_moderate(url: str) -> Dict[str, Any]:
    """Extract including external CSS files."""
    raise NotImplementedError("Phase 2 implementation")


def _extract_fonts(html_content: str) -> List[str]:
    """Extract font families from page content."""
    raise NotImplementedError("Phase 2 implementation")


def _find_logo(html_content: str, base_url: str) -> Optional[str]:
    """Find logo image URL in page."""
    raise NotImplementedError("Phase 2 implementation")
