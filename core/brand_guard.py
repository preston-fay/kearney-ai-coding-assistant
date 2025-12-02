"""
Kearney Brand Guard - Programmatic Brand Enforcement

Validates outputs against Kearney Design System (KDS) brand rules.
This module is called by hooks to enforce compliance before commit.

Brand Rules (Non-Negotiable):
    - Primary Color: Kearney Purple (#7823DC)
    - Forbidden Colors: Green (#00FF00, #2E7D32, etc.) - NEVER use
    - Typography: Inter font (Arial fallback), weights 400/500/600
    - Charts: No gridlines. Data labels outside bars/slices.
    - No Emojis: Never in any output
    - Dark Mode: Default background #1E1E1E
"""

import re
import logging
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional, Set, Tuple, Union

try:
    from PIL import Image
except ImportError:
    Image = None  # type: ignore

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore


logger = logging.getLogger(__name__)


@dataclass
class BrandViolation:
    """Represents a brand rule violation."""
    file_path: str
    rule: str
    message: str
    line_number: Optional[int] = None
    severity: str = "error"  # error, warning


# Kearney Brand Constants
KEARNEY_PURPLE = "#7823DC"
KEARNEY_PURPLE_RGB = (120, 35, 220)

# Acceptable brand colors (hex, lowercase)
ALLOWED_COLORS: Set[str] = {
    "#7823dc",  # Kearney Purple
    "#1e1e1e",  # Dark background
    "#ffffff",  # White
    "#f5f5f5",  # Light gray
    "#333333",  # Dark gray text
    "#666666",  # Medium gray
    "#999999",  # Light gray text
    "#cccccc",  # Border gray
    "#e0e0e0",  # Divider gray
}

# Forbidden colors - various greens commonly used for "success" states
FORBIDDEN_COLORS: Set[str] = {
    "#00ff00",  # Pure green
    "#008000",  # Green
    "#00ff7f",  # Spring green
    "#2e7d32",  # Material green 800
    "#388e3c",  # Material green 700
    "#43a047",  # Material green 600
    "#4caf50",  # Material green 500
    "#66bb6a",  # Material green 400
    "#81c784",  # Material green 300
    "#a5d6a7",  # Material green 200
    "#1b5e20",  # Material green 900
    "#00c853",  # Green accent
    "#00e676",  # Green accent light
    "#69f0ae",  # Green accent lighter
    "#b9f6ca",  # Green accent lightest
    "#228b22",  # Forest green
    "#32cd32",  # Lime green
    "#90ee90",  # Light green
    "#98fb98",  # Pale green
    "#adff2f",  # Green yellow
    "#7fff00",  # Chartreuse
}

# Emoji detection pattern (comprehensive)
EMOJI_PATTERN = re.compile(
    "["
    "\U0001F600-\U0001F64F"  # Emoticons
    "\U0001F300-\U0001F5FF"  # Symbols & pictographs
    "\U0001F680-\U0001F6FF"  # Transport & map
    "\U0001F1E0-\U0001F1FF"  # Flags
    "\U00002702-\U000027B0"  # Dingbats
    "\U000024C2-\U0001F251"  # Enclosed characters
    "\U0001F900-\U0001F9FF"  # Supplemental symbols
    "\U0001FA00-\U0001FA6F"  # Chess symbols
    "\U0001FA70-\U0001FAFF"  # Symbols extended
    "\U00002600-\U000026FF"  # Misc symbols
    "\U00002700-\U000027BF"  # Dingbats
    "]+"
)

# Hex color pattern
HEX_COLOR_PATTERN = re.compile(r"#[0-9a-fA-F]{6}\b|#[0-9a-fA-F]{3}\b")

# RGB color pattern (e.g., rgb(0, 255, 0) or rgba(0, 255, 0, 1))
RGB_COLOR_PATTERN = re.compile(
    r"rgba?\s*\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})"
)


def normalize_hex(color: str) -> str:
    """Normalize hex color to lowercase 6-digit format."""
    color = color.lower().strip()
    if len(color) == 4:  # #RGB -> #RRGGBB
        return f"#{color[1]*2}{color[2]*2}{color[3]*2}"
    return color


def rgb_to_hex(r: int, g: int, b: int) -> str:
    """Convert RGB values to hex color."""
    return f"#{r:02x}{g:02x}{b:02x}"


def is_green_rgb(r: int, g: int, b: int) -> bool:
    """Check if RGB color is a green variant (green dominates red and blue)."""
    # Green is dominant when G > R and G > B by significant margin
    if g > 100 and g > r * 1.3 and g > b * 1.3:
        return True
    return False


def check_text_content(content: str, file_path: str) -> List[BrandViolation]:
    """Check text content for brand violations."""
    violations: List[BrandViolation] = []
    lines = content.split("\n")

    for line_num, line in enumerate(lines, 1):
        # Check for emojis
        emoji_matches = EMOJI_PATTERN.findall(line)
        if emoji_matches:
            violations.append(BrandViolation(
                file_path=file_path,
                rule="NO_EMOJIS",
                message=f"Emoji detected: {''.join(emoji_matches)}",
                line_number=line_num,
            ))

        # Check hex colors
        hex_colors = HEX_COLOR_PATTERN.findall(line)
        for color in hex_colors:
            normalized = normalize_hex(color)
            if normalized in FORBIDDEN_COLORS:
                violations.append(BrandViolation(
                    file_path=file_path,
                    rule="FORBIDDEN_COLOR",
                    message=f"Forbidden green color: {color}",
                    line_number=line_num,
                ))

        # Check RGB colors
        rgb_matches = RGB_COLOR_PATTERN.findall(line)
        for match in rgb_matches:
            r, g, b = int(match[0]), int(match[1]), int(match[2])
            if is_green_rgb(r, g, b):
                violations.append(BrandViolation(
                    file_path=file_path,
                    rule="FORBIDDEN_COLOR",
                    message=f"Forbidden green RGB color: rgb({r}, {g}, {b})",
                    line_number=line_num,
                ))

    return violations


def check_python_file(file_path: Path) -> List[BrandViolation]:
    """Check Python file for brand violations in color definitions."""
    violations: List[BrandViolation] = []

    try:
        content = file_path.read_text(encoding="utf-8")
    except (IOError, UnicodeDecodeError) as e:
        logger.warning(f"Could not read {file_path}: {e}")
        return violations

    violations.extend(check_text_content(content, str(file_path)))

    # Additional Python-specific checks
    lines = content.split("\n")
    for line_num, line in enumerate(lines, 1):
        # Check for gridline settings (matplotlib)
        if "grid(" in line.lower() and "true" in line.lower():
            violations.append(BrandViolation(
                file_path=str(file_path),
                rule="NO_GRIDLINES",
                message="Gridlines detected. KDS requires no gridlines on charts.",
                line_number=line_num,
            ))

        # Check for direct matplotlib color usage with green
        if "color=" in line.lower() or "c=" in line:
            if "'green'" in line.lower() or '"green"' in line.lower():
                violations.append(BrandViolation(
                    file_path=str(file_path),
                    rule="FORBIDDEN_COLOR",
                    message="Named color 'green' is forbidden.",
                    line_number=line_num,
                ))

    return violations


def check_css_file(file_path: Path) -> List[BrandViolation]:
    """Check CSS/SCSS file for brand violations."""
    violations: List[BrandViolation] = []

    try:
        content = file_path.read_text(encoding="utf-8")
    except (IOError, UnicodeDecodeError) as e:
        logger.warning(f"Could not read {file_path}: {e}")
        return violations

    violations.extend(check_text_content(content, str(file_path)))

    # Check for named green color
    if re.search(r"\bgreen\b", content, re.IGNORECASE):
        violations.append(BrandViolation(
            file_path=str(file_path),
            rule="FORBIDDEN_COLOR",
            message="Named color 'green' is forbidden in CSS.",
        ))

    return violations


def check_html_file(file_path: Path) -> List[BrandViolation]:
    """Check HTML file for brand violations."""
    violations: List[BrandViolation] = []

    try:
        content = file_path.read_text(encoding="utf-8")
    except (IOError, UnicodeDecodeError) as e:
        logger.warning(f"Could not read {file_path}: {e}")
        return violations

    violations.extend(check_text_content(content, str(file_path)))
    return violations


def check_svg_file(file_path: Path) -> List[BrandViolation]:
    """Check SVG file for brand violations."""
    violations: List[BrandViolation] = []

    try:
        content = file_path.read_text(encoding="utf-8")
    except (IOError, UnicodeDecodeError) as e:
        logger.warning(f"Could not read {file_path}: {e}")
        return violations

    violations.extend(check_text_content(content, str(file_path)))
    return violations


def check_image_file(file_path: Path) -> List[BrandViolation]:
    """Check image file (PNG, JPG) for forbidden colors using pixel sampling."""
    violations: List[BrandViolation] = []

    if Image is None:
        logger.warning("PIL not installed. Skipping image color check.")
        return violations

    try:
        with Image.open(file_path) as img:
            # Convert to RGB if needed
            if img.mode != "RGB":
                img = img.convert("RGB")

            # Sample pixels (don't check every pixel for performance)
            width, height = img.size
            sample_step = max(1, min(width, height) // 50)  # Sample ~50x50 grid

            green_pixel_count = 0
            total_sampled = 0

            for x in range(0, width, sample_step):
                for y in range(0, height, sample_step):
                    r, g, b = img.getpixel((x, y))
                    total_sampled += 1

                    if is_green_rgb(r, g, b):
                        green_pixel_count += 1

            # If more than 5% of sampled pixels are green, flag it
            if total_sampled > 0:
                green_ratio = green_pixel_count / total_sampled
                if green_ratio > 0.05:
                    violations.append(BrandViolation(
                        file_path=str(file_path),
                        rule="FORBIDDEN_COLOR",
                        message=f"Image contains significant green content ({green_ratio:.1%} of sampled pixels).",
                    ))

    except Exception as e:
        logger.warning(f"Could not analyze image {file_path}: {e}")

    return violations


def check_file(file_path: Union[Path, str]) -> List[BrandViolation]:
    """
    Check a single file for brand violations.

    Args:
        file_path: Path to the file to check.

    Returns:
        List of BrandViolation objects. Empty list if no violations.
    """
    file_path = Path(file_path)

    if not file_path.exists():
        return []

    suffix = file_path.suffix.lower()

    if suffix == ".py":
        return check_python_file(file_path)
    elif suffix in {".css", ".scss", ".sass", ".less"}:
        return check_css_file(file_path)
    elif suffix in {".html", ".htm"}:
        return check_html_file(file_path)
    elif suffix == ".svg":
        return check_svg_file(file_path)
    elif suffix in {".png", ".jpg", ".jpeg"}:
        return check_image_file(file_path)
    elif suffix in {".md", ".txt", ".json", ".yaml", ".yml"}:
        # Check text files for emojis and colors in content
        try:
            content = file_path.read_text(encoding="utf-8")
            return check_text_content(content, str(file_path))
        except (IOError, UnicodeDecodeError):
            return []

    return []


def check_directory(
    directory: Union[Path, str],
    recursive: bool = True,
    extensions: Optional[Set[str]] = None,
) -> List[BrandViolation]:
    """
    Check all files in a directory for brand violations.

    Args:
        directory: Path to the directory to check.
        recursive: If True, check subdirectories recursively.
        extensions: Set of file extensions to check. If None, checks common types.

    Returns:
        List of all BrandViolation objects found.
    """
    directory = Path(directory)

    if not directory.exists():
        return []

    if extensions is None:
        extensions = {
            ".py", ".css", ".scss", ".sass", ".less",
            ".html", ".htm", ".svg", ".png", ".jpg", ".jpeg",
            ".md", ".txt", ".json", ".yaml", ".yml",
        }

    all_violations: List[BrandViolation] = []

    pattern = "**/*" if recursive else "*"

    for file_path in directory.glob(pattern):
        if file_path.is_file() and file_path.suffix.lower() in extensions:
            violations = check_file(file_path)
            all_violations.extend(violations)

    return all_violations


def format_violations(violations: List[BrandViolation]) -> str:
    """Format violations as a human-readable report."""
    if not violations:
        return "No brand violations found."

    lines = [f"Found {len(violations)} brand violation(s):"]
    lines.append("")

    for v in violations:
        location = v.file_path
        if v.line_number:
            location += f":{v.line_number}"
        lines.append(f"  [{v.rule}] {location}")
        lines.append(f"    {v.message}")

    return "\n".join(lines)


def main():
    """CLI entry point for brand_guard."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python core/brand_guard.py <file_or_directory>")
        sys.exit(1)

    target = Path(sys.argv[1])

    if target.is_file():
        violations = check_file(target)
    elif target.is_dir():
        violations = check_directory(target)
    else:
        print(f"Error: {target} does not exist.")
        sys.exit(1)

    print(format_violations(violations))

    if violations:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
