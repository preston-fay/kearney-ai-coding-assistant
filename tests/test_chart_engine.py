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


class TestNewChartTypes:
    """Tests for new chart types in KDSChart v2."""

    def test_waterfall_creates_figure(self, tmp_path):
        """Waterfall chart should create a figure."""
        from core.chart_engine import KDSChart
        chart = KDSChart()
        chart.waterfall(
            data=[100, 20, -15, 125],
            labels=['Start', 'Add', 'Sub', 'End'],
            title='Test Waterfall'
        )
        output = tmp_path / "waterfall.png"
        chart.save(str(output))
        assert output.exists()

    def test_waterfall_method_chaining(self):
        """Waterfall chart should support method chaining."""
        chart = KDSChart()
        result = chart.waterfall(
            data=[100, 20, -15, 125],
            labels=['Start', 'Add', 'Sub', 'End']
        )
        assert result is chart

    def test_stacked_bar_creates_figure(self, tmp_path):
        """Stacked bar chart should create a figure."""
        from core.chart_engine import KDSChart
        chart = KDSChart()
        chart.stacked_bar(
            data={'A': [10, 20], 'B': [15, 25]},
            labels=['X', 'Y'],
            title='Test Stacked'
        )
        output = tmp_path / "stacked.png"
        chart.save(str(output))
        assert output.exists()

    def test_stacked_bar_horizontal(self, tmp_path):
        """Stacked bar chart should support horizontal orientation."""
        chart = KDSChart()
        chart.stacked_bar(
            data={'A': [10, 20], 'B': [15, 25]},
            labels=['X', 'Y'],
            horizontal=True
        )
        output = tmp_path / "stacked_h.png"
        chart.save(str(output))
        assert output.exists()

    def test_combo_creates_figure(self, tmp_path):
        """Combo chart should create a figure."""
        from core.chart_engine import KDSChart
        chart = KDSChart()
        chart.combo(
            bar_data=[100, 120],
            line_data=[10, 12],
            labels=['A', 'B'],
            title='Test Combo'
        )
        output = tmp_path / "combo.png"
        chart.save(str(output))
        assert output.exists()

    def test_combo_with_labels(self, tmp_path):
        """Combo chart should support series labels."""
        chart = KDSChart()
        chart.combo(
            bar_data=[100, 120, 140],
            line_data=[10, 12, 11],
            labels=['Q1', 'Q2', 'Q3'],
            bar_label='Revenue',
            line_label='Margin',
            bar_ylabel='$ Millions',
            line_ylabel='%'
        )
        output = tmp_path / "combo_labels.png"
        chart.save(str(output))
        assert output.exists()

    def test_bullet_creates_figure(self, tmp_path):
        """Bullet chart should create a figure."""
        from core.chart_engine import KDSChart
        chart = KDSChart()
        chart.bullet(
            actual=85,
            target=100,
            ranges=[50, 75, 100],
            title='Test Bullet'
        )
        output = tmp_path / "bullet.png"
        chart.save(str(output))
        assert output.exists()

    def test_bullet_vertical(self, tmp_path):
        """Bullet chart should support vertical orientation."""
        chart = KDSChart()
        chart.bullet(
            actual=85,
            target=100,
            ranges=[50, 75, 100],
            horizontal=False
        )
        output = tmp_path / "bullet_v.png"
        chart.save(str(output))
        assert output.exists()

    def test_histogram_creates_figure(self, tmp_path):
        """Histogram should create a figure."""
        from core.chart_engine import KDSChart
        chart = KDSChart()
        chart.histogram(
            data=[1, 2, 2, 3, 3, 3, 4, 4, 5],
            bins=5,
            title='Test Histogram'
        )
        output = tmp_path / "histogram.png"
        chart.save(str(output))
        assert output.exists()

    def test_histogram_with_custom_bins(self, tmp_path):
        """Histogram should support custom bin edges."""
        chart = KDSChart()
        chart.histogram(
            data=[1, 2, 2, 3, 3, 3, 4, 4, 5],
            bins=[0, 2, 4, 6],
            xlabel='Value',
            show_values=True
        )
        output = tmp_path / "histogram_custom.png"
        chart.save(str(output))
        assert output.exists()

    def test_heatmap_creates_figure(self, tmp_path):
        """Heatmap should create a figure."""
        chart = KDSChart()
        data = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
        chart.heatmap(
            data=data,
            row_labels=['A', 'B', 'C'],
            col_labels=['X', 'Y', 'Z'],
            title='Test Heatmap'
        )
        output = tmp_path / "heatmap.png"
        chart.save(str(output))
        assert output.exists()

    def test_heatmap_method_chaining(self):
        """Heatmap should support method chaining."""
        chart = KDSChart()
        result = chart.heatmap(
            data=[[1, 2], [3, 4]],
            title='Test'
        )
        assert result is chart

    def test_heatmap_without_values(self, tmp_path):
        """Heatmap should work without value annotations."""
        chart = KDSChart()
        chart.heatmap(
            data=[[1, 2], [3, 4]],
            show_values=False
        )
        output = tmp_path / "heatmap_no_values.png"
        chart.save(str(output))
        assert output.exists()

    def test_boxplot_creates_figure(self, tmp_path):
        """Boxplot should create a figure."""
        chart = KDSChart()
        data = [[1, 2, 3, 4, 5, 10], [2, 3, 4, 5, 6, 7]]
        chart.boxplot(
            data=data,
            labels=['Group A', 'Group B'],
            title='Test Boxplot'
        )
        output = tmp_path / "boxplot.png"
        chart.save(str(output))
        assert output.exists()

    def test_boxplot_single_dataset(self, tmp_path):
        """Boxplot should work with single dataset."""
        chart = KDSChart()
        chart.boxplot(
            data=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            title='Single Boxplot'
        )
        output = tmp_path / "boxplot_single.png"
        chart.save(str(output))
        assert output.exists()

    def test_boxplot_horizontal(self, tmp_path):
        """Boxplot should support horizontal orientation."""
        chart = KDSChart()
        chart.boxplot(
            data=[[1, 2, 3, 4, 5], [2, 3, 4, 5, 6]],
            labels=['A', 'B'],
            horizontal=True
        )
        output = tmp_path / "boxplot_h.png"
        chart.save(str(output))
        assert output.exists()

    def test_area_creates_figure(self, tmp_path):
        """Area chart should create a figure."""
        chart = KDSChart()
        x = [1, 2, 3, 4, 5]
        y = [10, 15, 13, 17, 20]
        chart.area(
            x_data=x,
            y_data=y,
            title='Test Area'
        )
        output = tmp_path / "area.png"
        chart.save(str(output))
        assert output.exists()

    def test_area_stacked(self, tmp_path):
        """Area chart should support stacking."""
        chart = KDSChart()
        x = [1, 2, 3, 4]
        y = [[10, 15, 13, 17], [5, 8, 6, 10]]
        chart.area(
            x_data=x,
            y_data=y,
            labels=['Series A', 'Series B'],
            stacked=True
        )
        output = tmp_path / "area_stacked.png"
        chart.save(str(output))
        assert output.exists()

    def test_donut_creates_figure(self, tmp_path):
        """Donut chart should create a figure."""
        chart = KDSChart()
        chart.donut(
            data=[30, 20, 50],
            labels=['A', 'B', 'C'],
            title='Test Donut'
        )
        output = tmp_path / "donut.png"
        chart.save(str(output))
        assert output.exists()

    def test_donut_with_center_text(self, tmp_path):
        """Donut chart should support center text."""
        chart = KDSChart()
        chart.donut(
            data=[30, 20, 50],
            labels=['Marketing', 'R&D', 'Operations'],
            center_value='$1.2M',
            center_text='Total Budget'
        )
        output = tmp_path / "donut_center.png"
        chart.save(str(output))
        assert output.exists()

    def test_sankey_creates_figure(self, tmp_path):
        """Sankey diagram should create a figure."""
        chart = KDSChart()
        chart.sankey(
            flows=[100, -30, -40, -30],
            labels=['Budget', 'Marketing', 'R&D', 'Operations'],
            title='Test Sankey'
        )
        output = tmp_path / "sankey.png"
        chart.save(str(output))
        assert output.exists()

    def test_sankey_with_unit(self, tmp_path):
        """Sankey diagram should support unit labels."""
        chart = KDSChart()
        chart.sankey(
            flows=[100, -25, -35, -40],
            labels=['Revenue', 'COGS', 'OpEx', 'Profit'],
            unit='$M',
            title='P&L Flow'
        )
        output = tmp_path / "sankey_unit.png"
        chart.save(str(output))
        assert output.exists()

    def test_sankey_custom_orientations(self, tmp_path):
        """Sankey diagram should support custom orientations."""
        chart = KDSChart()
        chart.sankey(
            flows=[100, -50, -50],
            labels=['Input', 'Output A', 'Output B'],
            orientations=[0, 1, -1]  # Down, right, left
        )
        output = tmp_path / "sankey_orient.png"
        chart.save(str(output))
        assert output.exists()


class TestChartRecommendation:
    """Tests for chart type recommendation."""

    def test_bridge_recommends_waterfall(self):
        """Bridge story should recommend waterfall."""
        from core.chart_engine import recommend_chart_type
        assert recommend_chart_type("bridge") == "waterfall"

    def test_distribution_recommends_histogram(self):
        """Distribution story should recommend histogram."""
        from core.chart_engine import recommend_chart_type
        assert recommend_chart_type("distribution") == "histogram"

    def test_performance_recommends_bullet(self):
        """Performance story should recommend bullet."""
        from core.chart_engine import recommend_chart_type
        assert recommend_chart_type("performance") == "bullet"

    def test_dual_metric_recommends_combo(self):
        """Dual metric story should recommend combo."""
        from core.chart_engine import recommend_chart_type
        assert recommend_chart_type("dual_metric") == "combo"

    def test_comparison_with_series_recommends_grouped(self):
        """Comparison with multiple series should recommend grouped_bar."""
        from core.chart_engine import recommend_chart_type
        result = recommend_chart_type("comparison", {"series": 3})
        assert result == "grouped_bar"

    def test_part_to_whole_with_many_categories_recommends_stacked(self):
        """Part to whole with many categories should recommend stacked_bar."""
        from core.chart_engine import recommend_chart_type
        result = recommend_chart_type("part_to_whole", {"categories": 10})
        assert result == "stacked_bar"

    def test_unknown_story_defaults_to_bar(self):
        """Unknown story should default to bar chart."""
        from core.chart_engine import recommend_chart_type
        assert recommend_chart_type("unknown_story") == "bar"

    def test_comparison_single_series_recommends_bar(self):
        """Comparison with single series should recommend bar."""
        from core.chart_engine import recommend_chart_type
        result = recommend_chart_type("comparison", {"series": 1})
        assert result == "bar"

    def test_change_over_time_recommends_line(self):
        """Change over time should recommend line chart."""
        from core.chart_engine import recommend_chart_type
        assert recommend_chart_type("change_over_time") == "line"

    def test_correlation_recommends_scatter(self):
        """Correlation should recommend scatter plot."""
        from core.chart_engine import recommend_chart_type
        assert recommend_chart_type("correlation") == "scatter"
