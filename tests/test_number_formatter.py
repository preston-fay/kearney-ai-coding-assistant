"""Tests for core/number_formatter.py"""

import pytest
from core.number_formatter import (
    smart_format,
    format_currency,
    format_percent,
    format_axis_label,
    smart_format_series,
)


class TestSmartFormat:
    """Tests for smart_format function."""

    def test_smart_format_small_numbers(self):
        """Test that small numbers (<1000) are shown fully."""
        assert smart_format(50) == "50"
        assert smart_format(847) == "847"
        assert smart_format(999) == "999"

    def test_smart_format_thousands(self):
        """Test thousands abbreviation."""
        assert smart_format(1000) == "1K"
        assert smart_format(2500) == "2.5K"
        assert smart_format(2000) == "2K"
        assert smart_format(50000) == "50K"

    def test_smart_format_millions(self):
        """Test millions abbreviation."""
        assert smart_format(1000000) == "1M"
        assert smart_format(2500000) == "2.5M"
        assert smart_format(3100000) == "3.1M"
        assert smart_format(50000000) == "50M"

    def test_smart_format_billions(self):
        """Test billions abbreviation."""
        assert smart_format(1000000000) == "1B"
        assert smart_format(2100000000) == "2.1B"
        assert smart_format(3500000000) == "3.5B"

    def test_smart_format_negative(self):
        """Test negative numbers."""
        assert smart_format(-500) == "-500"
        assert smart_format(-2500) == "-2.5K"
        assert smart_format(-2500000) == "-2.5M"

    def test_smart_format_with_prefix(self):
        """Test with currency prefix."""
        assert smart_format(2500, prefix="$") == "$2.5K"
        assert smart_format(2500000, prefix="$") == "$2.5M"
        assert smart_format(2500000, prefix="€") == "€2.5M"

    def test_smart_format_with_suffix(self):
        """Test with suffix."""
        assert smart_format(2500, suffix=" units") == "2.5K units"
        assert smart_format(50, suffix="%") == "50%"

    def test_smart_format_with_decimals(self):
        """Test decimal places control."""
        assert smart_format(2567, decimals=0) == "3K"
        assert smart_format(2567, decimals=1) == "2.6K"
        assert smart_format(2567, decimals=2) == "2.57K"

    def test_smart_format_force_sign(self):
        """Test forcing sign display."""
        assert smart_format(50, force_sign=True) == "+50"
        assert smart_format(2500, force_sign=True) == "+2.5K"
        assert smart_format(-50, force_sign=True) == "-50"

    def test_smart_format_none(self):
        """Test None handling."""
        assert smart_format(None) == "N/A"

    def test_smart_format_removes_trailing_zeros(self):
        """Test that trailing zeros are removed."""
        assert smart_format(2000) == "2K"
        assert smart_format(3000000) == "3M"
        assert smart_format(5000000000) == "5B"


class TestFormatCurrency:
    """Tests for format_currency function."""

    def test_format_currency_default(self):
        """Test default currency symbol."""
        assert format_currency(2500) == "$2.5K"
        assert format_currency(2500000) == "$2.5M"
        assert format_currency(3100000000) == "$3.1B"

    def test_format_currency_custom_symbol(self):
        """Test custom currency symbols."""
        assert format_currency(2500, currency="€") == "€2.5K"
        assert format_currency(2500, currency="£") == "£2.5K"
        assert format_currency(2500, currency="¥") == "¥2.5K"

    def test_format_currency_small(self):
        """Test small currency amounts."""
        assert format_currency(50) == "$50"
        assert format_currency(500) == "$500"


class TestFormatPercent:
    """Tests for format_percent function."""

    def test_format_percent_basic(self):
        """Test basic percentage formatting."""
        assert format_percent(50) == "50%"
        assert format_percent(25.5) == "25.5%"
        assert format_percent(33.333, decimals=2) == "33.33%"

    def test_format_percent_removes_trailing_zeros(self):
        """Test trailing zero removal."""
        assert format_percent(50.0) == "50%"
        assert format_percent(25.50) == "25.5%"

    def test_format_percent_small_values(self):
        """Test very small percentages."""
        assert format_percent(0.5) == "0.5%"
        assert format_percent(0.123) == "0.12%"

    def test_format_percent_none(self):
        """Test None handling."""
        assert format_percent(None) == "N/A"


class TestFormatAxisLabel:
    """Tests for format_axis_label function."""

    def test_format_axis_label_basic(self):
        """Test basic axis label formatting."""
        assert format_axis_label(2500) == "2.5K"
        assert format_axis_label(2500000) == "2.5M"

    def test_format_axis_label_currency(self):
        """Test currency axis labels."""
        assert format_axis_label(2500, is_currency=True) == "$2.5K"
        assert format_axis_label(2500000, is_currency=True) == "$2.5M"


class TestSmartFormatSeries:
    """Tests for smart_format_series function."""

    def test_smart_format_series_basic(self):
        """Test formatting a series of values."""
        values = [100, 2500, 500000, 1000000]
        formatted = smart_format_series(values)
        assert formatted == ["100", "2.5K", "500K", "1M"]

    def test_smart_format_series_with_prefix(self):
        """Test series with prefix."""
        values = [100, 2500, 500000]
        formatted = smart_format_series(values, prefix="$")
        assert formatted == ["$100", "$2.5K", "$500K"]

    def test_smart_format_series_with_suffix(self):
        """Test series with suffix."""
        values = [100, 2500, 500000]
        formatted = smart_format_series(values, suffix=" units")
        assert formatted == ["100 units", "2.5K units", "500K units"]


class TestEdgeCases:
    """Tests for edge cases."""

    def test_zero(self):
        """Test zero formatting."""
        assert smart_format(0) == "0"

    def test_very_small_float(self):
        """Test very small float values."""
        assert smart_format(0.5) == "0.5"
        assert smart_format(0.123, decimals=2) == "0.12"

    def test_exact_threshold_values(self):
        """Test values exactly at thresholds."""
        assert smart_format(1000) == "1K"
        assert smart_format(1000000) == "1M"
        assert smart_format(1000000000) == "1B"
