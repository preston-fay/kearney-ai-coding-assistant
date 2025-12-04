"""
Web scraping for brand extraction.

Extracts brand tokens (colors, fonts, logos) from client websites.
Supports conservative (single page) and moderate (with CSS files) modes.
"""

import re
import logging
from typing import Dict, List, Any, Optional
from urllib.parse import urljoin, urlparse
from collections import Counter

try:
    import requests
    from bs4 import BeautifulSoup
    HAS_WEB_DEPS = True
except ImportError:
    HAS_WEB_DEPS = False

logger = logging.getLogger(__name__)

# Regex patterns
HEX_PATTERN = re.compile(r'#[0-9A-Fa-f]{6}(?![0-9A-Fa-f])')
RGB_PATTERN = re.compile(r'rgb\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)')
RGBA_PATTERN = re.compile(r'rgba\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*[\d.]+\s*\)')
FONT_FAMILY_PATTERN = re.compile(r'font-family:\s*([^;]+)', re.IGNORECASE)

# Common colors to filter out (too generic)
COMMON_COLORS = {
    '#FFFFFF', '#FFFFFF', '#000000', '#000000',
    '#FFFFF', '#00000', '#FFF', '#000',
}

# Headers for web requests
DEFAULT_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (compatible; KACA/1.0; +https://kearney.com)',
    'Accept': 'text/html,text/css,*/*',
}


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
            - colors: List of hex colors found (ranked by frequency)
            - fonts: List of font families found
            - logo_url: URL to logo if found
            - metadata: Extraction metadata
    """
    if not HAS_WEB_DEPS:
        raise ImportError(
            "Web extraction requires 'requests' and 'beautifulsoup4'. "
            "Install with: pip install requests beautifulsoup4"
        )

    if mode == "conservative":
        return _extract_conservative(url)
    elif mode == "moderate":
        return _extract_moderate(url)
    else:
        raise ValueError(f"Unknown mode: {mode}. Use 'conservative' or 'moderate'.")


def _extract_conservative(url: str) -> Dict[str, Any]:
    """
    Extract from single page with inline styles only.

    This is the safest mode - only analyzes the main page HTML.
    """
    try:
        response = requests.get(url, headers=DEFAULT_HEADERS, timeout=15)
        response.raise_for_status()
    except requests.RequestException as e:
        raise ConnectionError(f"Failed to fetch {url}: {e}")

    soup = BeautifulSoup(response.text, 'html.parser')
    base_url = f"{urlparse(url).scheme}://{urlparse(url).netloc}"

    # Extract colors from inline styles and style tags
    colors = _extract_colors_from_soup(soup)

    # Extract fonts
    fonts = _extract_fonts_from_soup(soup)

    # Find logo
    logo_url = _find_logo(soup, base_url)

    return {
        "colors": colors,
        "fonts": fonts,
        "logo_url": logo_url,
        "metadata": {
            "mode": "conservative",
            "url": url,
            "page_title": soup.title.string if soup.title else None,
        }
    }


def _extract_moderate(url: str) -> Dict[str, Any]:
    """
    Extract including external CSS files.

    Fetches and parses external stylesheets for more complete extraction.
    """
    try:
        response = requests.get(url, headers=DEFAULT_HEADERS, timeout=15)
        response.raise_for_status()
    except requests.RequestException as e:
        raise ConnectionError(f"Failed to fetch {url}: {e}")

    soup = BeautifulSoup(response.text, 'html.parser')
    base_url = f"{urlparse(url).scheme}://{urlparse(url).netloc}"

    # Start with inline styles
    colors = _extract_colors_from_soup(soup)
    fonts = _extract_fonts_from_soup(soup)

    # Fetch external CSS files
    css_colors, css_fonts = _extract_from_css_files(soup, base_url)
    colors.extend(css_colors)
    fonts.extend(css_fonts)

    # Deduplicate and rank
    color_counts = Counter(c.upper() for c in colors)
    ranked_colors = [c for c, _ in color_counts.most_common(10)]

    # Filter out common colors
    ranked_colors = [c for c in ranked_colors if c.upper() not in COMMON_COLORS][:6]

    unique_fonts = list(dict.fromkeys(fonts))[:5]

    # Find logo
    logo_url = _find_logo(soup, base_url)

    return {
        "colors": ranked_colors,
        "fonts": unique_fonts,
        "logo_url": logo_url,
        "metadata": {
            "mode": "moderate",
            "url": url,
            "page_title": soup.title.string if soup.title else None,
            "css_files_parsed": _count_css_links(soup),
        }
    }


def _extract_colors_from_soup(soup: BeautifulSoup) -> List[str]:
    """Extract colors from inline styles and style tags."""
    colors = []

    # From <style> tags
    for style in soup.find_all('style'):
        if style.string:
            colors.extend(_extract_colors_from_text(style.string))

    # From inline style attributes
    for tag in soup.find_all(style=True):
        colors.extend(_extract_colors_from_text(tag['style']))

    return colors


def _extract_colors_from_text(text: str) -> List[str]:
    """Extract hex and RGB colors from text."""
    colors = []

    # Find hex colors
    for match in HEX_PATTERN.findall(text):
        colors.append(match.upper())

    # Find RGB colors and convert to hex
    for match in RGB_PATTERN.findall(text):
        r, g, b = int(match[0]), int(match[1]), int(match[2])
        if 0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255:
            colors.append(f"#{r:02X}{g:02X}{b:02X}")

    # Find RGBA colors and convert to hex (ignoring alpha)
    for match in RGBA_PATTERN.findall(text):
        r, g, b = int(match[0]), int(match[1]), int(match[2])
        if 0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255:
            colors.append(f"#{r:02X}{g:02X}{b:02X}")

    return colors


def _extract_fonts_from_soup(soup: BeautifulSoup) -> List[str]:
    """Extract font families from page."""
    fonts = []

    # From <style> tags
    for style in soup.find_all('style'):
        if style.string:
            fonts.extend(_extract_fonts_from_text(style.string))

    # From inline style attributes
    for tag in soup.find_all(style=True):
        fonts.extend(_extract_fonts_from_text(tag['style']))

    return fonts


def _extract_fonts_from_text(text: str) -> List[str]:
    """Extract font-family values from CSS text."""
    fonts = []

    for match in FONT_FAMILY_PATTERN.findall(text):
        # Clean up the font family string
        family = match.strip().strip('"\'')
        # Take the first font in the list
        first_font = family.split(',')[0].strip().strip('"\'')
        if first_font and first_font.lower() not in ('inherit', 'initial', 'unset'):
            fonts.append(first_font)

    return fonts


def _extract_from_css_files(soup: BeautifulSoup, base_url: str) -> tuple:
    """Fetch and parse external CSS files."""
    colors = []
    fonts = []

    for link in soup.find_all('link', rel='stylesheet'):
        href = link.get('href')
        if not href:
            continue

        css_url = urljoin(base_url, href)

        try:
            response = requests.get(css_url, headers=DEFAULT_HEADERS, timeout=10)
            response.raise_for_status()
            css_text = response.text

            colors.extend(_extract_colors_from_text(css_text))
            fonts.extend(_extract_fonts_from_text(css_text))
        except requests.RequestException:
            logger.warning(f"Failed to fetch CSS: {css_url}")
            continue

    return colors, fonts


def _count_css_links(soup: BeautifulSoup) -> int:
    """Count number of CSS link tags."""
    return len(soup.find_all('link', rel='stylesheet'))


def _find_logo(soup: BeautifulSoup, base_url: str) -> Optional[str]:
    """
    Find logo image URL in page.

    Looks for common logo patterns in img tags and CSS.
    """
    # Look for img tags with logo-related attributes
    logo_keywords = ['logo', 'brand', 'header-logo', 'site-logo']

    for img in soup.find_all('img'):
        src = img.get('src', '')
        alt = img.get('alt', '').lower()
        classes = ' '.join(img.get('class', [])).lower()
        img_id = (img.get('id') or '').lower()

        # Check if any keyword matches
        for keyword in logo_keywords:
            if (keyword in src.lower() or
                keyword in alt or
                keyword in classes or
                keyword in img_id):
                return urljoin(base_url, src)

    # Look in header for any img
    header = soup.find('header')
    if header:
        first_img = header.find('img')
        if first_img and first_img.get('src'):
            return urljoin(base_url, first_img['src'])

    return None


def _rgb_to_hex(r: int, g: int, b: int) -> str:
    """Convert RGB values to hex color."""
    return f"#{r:02X}{g:02X}{b:02X}"
