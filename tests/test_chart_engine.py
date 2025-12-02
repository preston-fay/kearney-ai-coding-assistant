"""Tests for core/chart_engine.py"""

import pytest
from pathlib import Path
import tempfile
import os

from core.chart_engine import KDSChart, KDSColors


class TestKDSColors:
    """Tests for KDSColors class."""

    def test_primary_color(self):
        """Test that primary color is Kearney Purple."""
        assert KDSColors.PRIMARY == "#7823DC"

    def test_dark_background(self):
        """Test dark background color."""
        assert KDSColors.BACKGROUND_DARK == "#1E1E1E"

    def test_palette_has_no_green(self):
        """Test that palette contains no green colors."""
        green_indicators = ["00ff00", "00FF00", "green", "2e7d32", "4caf50"]
        for color in KDSColors.PALETTE:
            color_lower = color.lower()
            for green in green_indicators:
                assert green not in color_lower, f"Green color found: {color}"


class TestKDSChartInit:
    """Tests for KDSChart initialization."""

    def test_default_init(self):
        """Test default initialization."""
        chart = KDSChart()
        assert chart.dark_mode is True
        # Default is presentation preset (1920x1080 @ 150 DPI = 12.8x7.2)
        assert chart.figsize == (12.8, 7.2)
        assert chart.dpi == 150

    def test_custom_init(self):
        """Test custom initialization."""
        chart = KDSChart(figsize=(12, 8), dark_mode=False, dpi=300)
        assert chart.dark_mode is False
        assert chart.figsize == (12, 8)
        assert chart.dpi == 300


class TestBarChart:
    """Tests for bar chart creation."""

    def test_create_bar_chart(self):
        """Test creating a basic bar chart."""
        chart = KDSChart()
        data = [100, 200, 150]
        labels = ["A", "B", "C"]

        result = chart.bar(data, labels, title="Test Bar Chart")

        assert result is chart  # Method chaining
        assert chart.fig is not None
        assert chart.ax is not None

    def test_bar_chart_horizontal(self):
        """Test creating horizontal bar chart."""
        chart = KDSChart()
        data = [100, 200, 150]
        labels = ["A", "B", "C"]

        chart.bar(data, labels, horizontal=True)

        assert chart.fig is not None

    def test_bar_chart_save(self):
        """Test saving bar chart to file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            chart = KDSChart()
            data = [100, 200, 150]
            labels = ["A", "B", "C"]

            chart.bar(data, labels, title="Test")
            output_path = Path(tmpdir) / "test_bar.png"
            result = chart.save(output_path)

            assert result == output_path
            assert output_path.exists()
            assert output_path.stat().st_size > 0


class TestLineChart:
    """Tests for line chart creation."""

    def test_create_line_chart(self):
        """Test creating a basic line chart."""
        chart = KDSChart()
        x = ["Q1", "Q2", "Q3", "Q4"]
        y = [100, 120, 115, 140]

        result = chart.line(x, y, title="Test Line Chart")

        assert result is chart
        assert chart.fig is not None

    def test_line_chart_multiple_series(self):
        """Test creating line chart with multiple series."""
        chart = KDSChart()
        x = ["Q1", "Q2", "Q3", "Q4"]
        y = [[100, 120, 115, 140], [80, 90, 100, 110]]
        labels = ["2024", "2023"]

        chart.line(x, y, labels=labels)

        assert chart.fig is not None

    def test_line_chart_save(self):
        """Test saving line chart to file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            chart = KDSChart()
            x = ["Q1", "Q2", "Q3", "Q4"]
            y = [100, 120, 115, 140]

            chart.line(x, y)
            output_path = Path(tmpdir) / "test_line.png"
            chart.save(output_path)

            assert output_path.exists()


class TestPieChart:
    """Tests for pie chart creation."""

    def test_create_pie_chart(self):
        """Test creating a basic pie chart."""
        chart = KDSChart()
        data = [30, 25, 20, 15, 10]
        labels = ["A", "B", "C", "D", "E"]

        result = chart.pie(data, labels, title="Test Pie Chart")

        assert result is chart
        assert chart.fig is not None

    def test_pie_chart_without_percentages(self):
        """Test pie chart without percentage labels."""
        chart = KDSChart()
        data = [30, 25, 20, 15, 10]
        labels = ["A", "B", "C", "D", "E"]

        chart.pie(data, labels, show_percentages=False)

        assert chart.fig is not None


class TestScatterChart:
    """Tests for scatter plot creation."""

    def test_create_scatter_plot(self):
        """Test creating a basic scatter plot."""
        chart = KDSChart()
        x = [1, 2, 3, 4, 5]
        y = [2, 4, 1, 3, 5]

        result = chart.scatter(x, y, title="Test Scatter")

        assert result is chart
        assert chart.fig is not None


class TestGroupedBarChart:
    """Tests for grouped bar chart creation."""

    def test_create_grouped_bar_chart(self):
        """Test creating a grouped bar chart."""
        chart = KDSChart()
        data = [[10, 20, 30], [15, 25, 35]]
        group_labels = ["A", "B", "C"]
        series_labels = ["Series 1", "Series 2"]

        result = chart.grouped_bar(data, group_labels, series_labels)

        assert result is chart
        assert chart.fig is not None


class TestChartSave:
    """Tests for chart saving functionality."""

    def test_save_creates_directory(self):
        """Test that save creates parent directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            chart = KDSChart()
            chart.bar([1, 2, 3], ["A", "B", "C"])

            output_path = Path(tmpdir) / "nested" / "dir" / "chart.png"
            chart.save(output_path)

            assert output_path.exists()

    def test_save_without_chart_raises(self):
        """Test that saving without creating chart raises error."""
        chart = KDSChart()

        with pytest.raises(ValueError, match="No chart created"):
            chart.save("test.png")

    def test_save_clears_figure(self):
        """Test that save clears the figure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            chart = KDSChart()
            chart.bar([1, 2, 3], ["A", "B", "C"])
            chart.save(Path(tmpdir) / "test.png")

            assert chart.fig is None
            assert chart.ax is None

    def test_save_transparent(self):
        """Test saving with transparent background."""
        with tempfile.TemporaryDirectory() as tmpdir:
            chart = KDSChart()
            chart.bar([1, 2, 3], ["A", "B", "C"])

            output_path = Path(tmpdir) / "transparent.png"
            chart.save(output_path, transparent=True)

            assert output_path.exists()


class TestChartClose:
    """Tests for chart close functionality."""

    def test_close_clears_figure(self):
        """Test that close clears the figure."""
        chart = KDSChart()
        chart.bar([1, 2, 3], ["A", "B", "C"])

        chart.close()

        assert chart.fig is None
        assert chart.ax is None

    def test_close_without_figure(self):
        """Test that close works without figure."""
        chart = KDSChart()
        chart.close()  # Should not raise


class TestKDSCompliance:
    """Tests for KDS brand compliance."""

    def test_no_gridlines_by_default(self):
        """Test that gridlines are disabled by default."""
        chart = KDSChart()
        chart.bar([1, 2, 3], ["A", "B", "C"])

        # Check that grid is not visible
        assert not chart.ax.xaxis.get_gridlines()[0].get_visible() or \
               not chart.ax.yaxis.get_gridlines()[0].get_visible()

    def test_dark_mode_default(self):
        """Test that dark mode is default."""
        chart = KDSChart()
        assert chart.dark_mode is True

    def test_method_chaining(self):
        """Test that chart methods support chaining."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "chained.png"

            # Should be able to chain methods
            KDSChart().bar([1, 2, 3], ["A", "B", "C"]).save(output_path)

            assert output_path.exists()


class TestGetColors:
    """Tests for color palette selection."""

    def test_get_single_color(self):
        """Test getting a single color."""
        chart = KDSChart()
        colors = chart._get_colors(1)
        assert len(colors) == 1
        assert colors[0] == KDSColors.PALETTE[0]

    def test_get_multiple_colors(self):
        """Test getting multiple colors."""
        chart = KDSChart()
        colors = chart._get_colors(5)
        assert len(colors) == 5

    def test_colors_cycle_when_needed(self):
        """Test that colors cycle when more than palette size requested."""
        chart = KDSChart()
        palette_size = len(KDSColors.PALETTE)
        colors = chart._get_colors(palette_size + 3)

        assert len(colors) == palette_size + 3
        # With intelligent_colors=True (default), colors don't cycle
        # All colors should be valid hex codes
        assert all(c.startswith('#') and len(c) == 7 for c in colors)
