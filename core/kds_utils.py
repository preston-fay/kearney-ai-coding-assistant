# core/kds_utils.py
"""
Utility functions for KACA file operations.
Ensures safe encoding and brand-compliant output.
"""

from pathlib import Path
from typing import Union


def safe_write_text(path: Union[str, Path], content: str, encoding: str = "utf-8") -> Path:
    """
    Write text to file with safe encoding.

    Removes/replaces characters that can't be encoded in UTF-8,
    including Unicode surrogate pairs that cause crashes.

    Args:
        path: Destination file path
        content: Text content to write
        encoding: Target encoding (default: utf-8)

    Returns:
        Path to written file
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    # Remove surrogate pairs and other unencodable characters
    safe_content = content.encode(encoding, errors='replace').decode(encoding)

    # Additionally strip any remaining emoji patterns as a safety net
    # (brand compliance - no emojis allowed)
    from core.brand_guard import EMOJI_PATTERN
    safe_content = EMOJI_PATTERN.sub('', safe_content)

    path.write_text(safe_content, encoding=encoding)
    return path


def safe_read_text(path: Union[str, Path], encoding: str = "utf-8") -> str:
    """
    Read text from file with safe encoding handling.

    Args:
        path: Source file path
        encoding: Source encoding (default: utf-8)

    Returns:
        File contents as string
    """
    path = Path(path)
    return path.read_text(encoding=encoding, errors='replace')
