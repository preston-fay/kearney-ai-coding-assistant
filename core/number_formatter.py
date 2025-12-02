"""
Kearney AI Coding Assistant - Smart Number Formatting

Formats large numbers for human readability in charts and reports.
"""

from typing import Union, Optional
import re


def smart_format(
    value: Union[int, float],
    prefix: str = "",
    suffix: str = "",
    decimals: int = 1,
    force_sign: bool = False
) -> str:
    """
    Format a number with smart abbreviations.

    Thresholds:
    - < 1,000: Show full number (e.g., 847)
    - 1,000 - 999,999: Use K (e.g., 2.5K)
    - 1,000,000 - 999,999,999: Use M (e.g., 3.1M)
    - >= 1,000,000,000: Use B (e.g., 2.1B)

    Args:
        value: Number to format
        prefix: Prefix like "$" or "€"
        suffix: Suffix like "%" or " units"
        decimals: Decimal places for abbreviated numbers
        force_sign: Show + for positive numbers

    Returns:
        Formatted string (e.g., "$2.5M", "3.1B", "45.2%")
    """
    if value is None:
        return "N/A"

    # Handle sign
    sign = ""
    if value < 0:
        sign = "-"
        value = abs(value)
    elif force_sign and value > 0:
        sign = "+"

    # Determine abbreviation
    if value >= 1_000_000_000:
        formatted = f"{value / 1_000_000_000:.{decimals}f}B"
    elif value >= 1_000_000:
        formatted = f"{value / 1_000_000:.{decimals}f}M"
    elif value >= 1_000:
        formatted = f"{value / 1_000:.{decimals}f}K"
    else:
        # For small numbers, show appropriate decimals
        if isinstance(value, float) and value != int(value):
            formatted = f"{value:.{decimals}f}"
        else:
            formatted = str(int(value))

    # Remove trailing zeros after decimal (e.g., "2.0K" → "2K")
    if '.' in formatted:
        # Split by abbreviation letter if present
        parts = re.split(r'([KMB])', formatted)
        if len(parts) > 1:
            # Has abbreviation
            num_part = parts[0].rstrip('0').rstrip('.')
            abbr_part = parts[1]
            formatted = num_part + abbr_part
        else:
            # No abbreviation, just remove trailing zeros
            formatted = formatted.rstrip('0').rstrip('.')

    return f"{sign}{prefix}{formatted}{suffix}"


def format_currency(value: Union[int, float], currency: str = "$") -> str:
    """Format as currency with smart abbreviation."""
    return smart_format(value, prefix=currency)


def format_percent(value: Union[int, float], decimals: int = 1) -> str:
    """Format as percentage (assumes value is already in percent form)."""
    if value is None:
        return "N/A"

    # Format the number
    if abs(value) < 1 and value != 0:
        # Very small percentages, show more decimals
        formatted = f"{value:.2f}"
    else:
        formatted = f"{value:.{decimals}f}"

    # Remove trailing zeros
    formatted = formatted.rstrip('0').rstrip('.')

    return f"{formatted}%"


def format_axis_label(value: Union[int, float], is_currency: bool = False) -> str:
    """Format for chart axis labels."""
    prefix = "$" if is_currency else ""
    return smart_format(value, prefix=prefix, decimals=1)


def smart_format_series(
    values: list,
    prefix: str = "",
    suffix: str = ""
) -> list:
    """Format a list of values consistently."""
    return [smart_format(v, prefix=prefix, suffix=suffix) for v in values]
