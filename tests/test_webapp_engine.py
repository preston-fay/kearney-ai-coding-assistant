"""Tests for KDSWebApp, KDSStreamlitApp, and KDSReactApp."""

import json
import pytest
from pathlib import Path

from core.kds_theme import KDSTheme
from core.kds_data import KDSData
from core.webapp_engine import KDSWebApp, KDSStreamlitApp, KDSReactApp


@pytest.fixture
def sample_data(tmp_path):
    """Create sample data for testing."""
    csv_path = tmp_path / "data.csv"
    csv_path.write_text(
        "region,revenue,units\n"
        "North,100000,400\n"
        "South,80000,320\n"
        "East,120000,480\n"
    )

    config = {
        "sales": {
            "type": "csv",
            "path": str(csv_path),
            "keys": ["region"],
            "value_cols": ["revenue", "units"],
        }
    }

    return KDSData.from_dict(config)


class TestKDSWebApp:
    """Tests for static HTML generator."""

    def test_basic_generation(self, sample_data, tmp_path):
        """Test basic HTML generation."""
        output_path = tmp_path / "test.html"

        app = KDSWebApp("Test Dashboard")
        app.set_data(sample_data)
        app.add_table("sales", "Sales Data")

        result = app.generate(output_path)

        assert result.exists()
        assert result.suffix == ".html"

    def test_html_contains_title(self, sample_data, tmp_path):
        """Test title appears in output."""
        output_path = tmp_path / "test.html"

        app = KDSWebApp("My Custom Title")
        app.set_data(sample_data)
        app.generate(output_path)

        html = output_path.read_text()
        assert "My Custom Title" in html

    def test_html_contains_theme_css(self, sample_data, tmp_path):
        """Test theme CSS is embedded."""
        output_path = tmp_path / "test.html"

        app = KDSWebApp("Test", theme=KDSTheme())
        app.set_data(sample_data)
        app.generate(output_path)

        html = output_path.read_text()
        assert "--kds-primary" in html
        assert "#7823DC" in html or "#7823dc" in html

    def test_html_contains_embedded_data(self, sample_data, tmp_path):
        """Test data is embedded as JSON."""
        output_path = tmp_path / "test.html"

        app = KDSWebApp("Test")
        app.set_data(sample_data)
        app.generate(output_path)

        html = output_path.read_text()
        assert "application/json" in html
        assert "North" in html  # Data value

    def test_fluent_interface(self, sample_data, tmp_path):
        """Test method chaining works."""
        output_path = tmp_path / "test.html"

        result = (
            KDSWebApp("Test")
            .set_data(sample_data)
            .add_metric("Revenue", "$300K")
            .add_table("sales", "Details")
            .generate(output_path)
        )

        assert result.exists()

    def test_metric_appears_in_output(self, sample_data, tmp_path):
        """Test metrics are rendered."""
        output_path = tmp_path / "test.html"

        app = KDSWebApp("Test")
        app.set_data(sample_data)
        app.add_metric("Total Revenue", "$300,000", "+15%")
        app.generate(output_path)

        html = output_path.read_text()
        assert "Total Revenue" in html
        assert "$300,000" in html
        assert "+15%" in html

    def test_chart_generation(self, sample_data, tmp_path):
        """Test chart is included."""
        output_path = tmp_path / "test.html"

        app = KDSWebApp("Test")
        app.set_data(sample_data)
        app.add_chart("sales", "bar", "region", "revenue", "Revenue by Region")
        app.generate(output_path)

        html = output_path.read_text()
        assert "plotly" in html.lower()
        assert "Revenue by Region" in html

    def test_no_data_raises_error(self, tmp_path):
        """Test error when no data set."""
        output_path = tmp_path / "test.html"

        app = KDSWebApp("Test")
        # Not calling set_data()

        with pytest.raises(ValueError, match="No data"):
            app.generate(output_path)

    def test_responsive_css(self, sample_data, tmp_path):
        """Test responsive CSS is included."""
        output_path = tmp_path / "test.html"

        app = KDSWebApp("Test")
        app.set_data(sample_data)
        app.generate(output_path)

        html = output_path.read_text()
        assert "@media" in html  # Responsive breakpoints

    def test_kaca_footer(self, sample_data, tmp_path):
        """Test KACA footer is present."""
        output_path = tmp_path / "test.html"

        app = KDSWebApp("Test")
        app.set_data(sample_data)
        app.generate(output_path)

        html = output_path.read_text()
        assert "KACA" in html
        assert "Kearney" in html

    def test_no_green_colors_in_output(self, sample_data, tmp_path):
        """Verify no forbidden green colors in output."""
        output_path = tmp_path / "test.html"

        app = KDSWebApp("Test")
        app.set_data(sample_data)
        app.add_chart("sales", "bar", "region", "revenue", "Test Chart")
        app.generate(output_path)

        html = output_path.read_text().lower()

        forbidden_greens = ["#00ff00", "#008000", "#2e7d32", "#4caf50"]
        for green in forbidden_greens:
            assert green not in html, f"Forbidden green {green} found in output"

    def test_filter_generation(self, sample_data, tmp_path):
        """Test filter controls are generated."""
        output_path = tmp_path / "test.html"

        app = KDSWebApp("Test")
        app.set_data(sample_data)
        app.add_filter("sales", "region", "dropdown")
        app.generate(output_path)

        html = output_path.read_text()
        assert "filter" in html.lower()
        assert "region" in html

    def test_table_generation(self, sample_data, tmp_path):
        """Test table is rendered."""
        output_path = tmp_path / "test.html"

        app = KDSWebApp("Test")
        app.set_data(sample_data)
        app.add_table("sales", "Sales Table")
        app.generate(output_path)

        html = output_path.read_text()
        assert "<table>" in html
        assert "Sales Table" in html

    def test_default_theme(self, sample_data, tmp_path):
        """Test default theme is applied when none provided."""
        output_path = tmp_path / "test.html"

        app = KDSWebApp("Test")  # No theme parameter
        app.set_data(sample_data)
        app.generate(output_path)

        html = output_path.read_text()
        assert "#7823DC" in html or "#7823dc" in html


class TestKDSStreamlitApp:
    """Tests for Streamlit app generator."""

    def test_basic_generation(self, sample_data, tmp_path):
        """Test Streamlit app generation."""
        output_path = tmp_path / "streamlit_app"

        app = KDSStreamlitApp("Test Dashboard")
        app.set_data(sample_data)
        result = app.generate(output_path)

        assert result.exists()
        assert (result / "app.py").exists()
        assert (result / ".streamlit" / "config.toml").exists()
        assert (result / "requirements.txt").exists()

    def test_app_py_content(self, sample_data, tmp_path):
        """Test app.py contains expected content."""
        output_path = tmp_path / "streamlit_app"

        app = KDSStreamlitApp("My Streamlit App")
        app.set_data(sample_data)
        app.generate(output_path)

        app_py = (output_path / "app.py").read_text()
        assert "import streamlit as st" in app_py
        assert "My Streamlit App" in app_py
        assert "KACA" in app_py

    def test_config_toml_theme(self, sample_data, tmp_path):
        """Test config.toml has theme settings."""
        output_path = tmp_path / "streamlit_app"

        app = KDSStreamlitApp("Test")
        app.set_data(sample_data)
        app.generate(output_path)

        config = (output_path / ".streamlit" / "config.toml").read_text()
        assert "[theme]" in config
        assert "#7823DC" in config or "#7823dc" in config

    def test_data_exported(self, sample_data, tmp_path):
        """Test data files are exported."""
        output_path = tmp_path / "streamlit_app"

        app = KDSStreamlitApp("Test")
        app.set_data(sample_data)
        app.generate(output_path)

        assert (output_path / "data" / "sales.csv").exists()

    def test_requirements_txt(self, sample_data, tmp_path):
        """Test requirements.txt content."""
        output_path = tmp_path / "streamlit_app"

        app = KDSStreamlitApp("Test")
        app.set_data(sample_data)
        app.generate(output_path)

        requirements = (output_path / "requirements.txt").read_text()
        assert "streamlit" in requirements
        assert "pandas" in requirements
        assert "plotly" in requirements


class TestKDSReactApp:
    """Tests for React app generator."""

    def test_basic_generation(self, sample_data, tmp_path):
        """Test React app generation."""
        output_path = tmp_path / "react_app"

        app = KDSReactApp("Test Dashboard")
        app.set_data(sample_data)
        result = app.generate(output_path)

        assert result.exists()
        assert (result / "package.json").exists()
        assert (result / "src" / "App.jsx").exists()
        assert (result / "vite.config.js").exists()

    def test_package_json_content(self, sample_data, tmp_path):
        """Test package.json has correct dependencies."""
        output_path = tmp_path / "react_app"

        app = KDSReactApp("Test Dashboard")
        app.set_data(sample_data)
        app.generate(output_path)

        package_json = json.loads((output_path / "package.json").read_text())
        assert "react" in package_json["dependencies"]
        assert "recharts" in package_json["dependencies"]
        assert "vite" in package_json["devDependencies"]

    def test_data_embedded_as_json(self, sample_data, tmp_path):
        """Test data is embedded as JSON."""
        output_path = tmp_path / "react_app"

        app = KDSReactApp("Test")
        app.set_data(sample_data)
        app.generate(output_path)

        data_json = (output_path / "src" / "data" / "data.json").read_text()
        data = json.loads(data_json)
        assert "sales" in data

    def test_theme_js_exported(self, sample_data, tmp_path):
        """Test theme.js is generated."""
        output_path = tmp_path / "react_app"

        app = KDSReactApp("Test")
        app.set_data(sample_data)
        app.generate(output_path)

        theme_js = (output_path / "src" / "styles" / "theme.js").read_text()
        assert "#7823DC" in theme_js or "#7823dc" in theme_js

    def test_css_with_theme_variables(self, sample_data, tmp_path):
        """Test CSS includes theme variables."""
        output_path = tmp_path / "react_app"

        app = KDSReactApp("Test")
        app.set_data(sample_data)
        app.generate(output_path)

        css = (output_path / "src" / "styles" / "index.css").read_text()
        assert "--kds-primary" in css
        assert "#7823DC" in css or "#7823dc" in css

    def test_readme_generated(self, sample_data, tmp_path):
        """Test README is generated."""
        output_path = tmp_path / "react_app"

        app = KDSReactApp("Test Dashboard")
        app.set_data(sample_data)
        app.generate(output_path)

        readme = (output_path / "README.md").read_text()
        assert "Test Dashboard" in readme
        assert "npm" in readme

    def test_no_data_raises_error(self, tmp_path):
        """Test error when no data set."""
        output_path = tmp_path / "react_app"

        app = KDSReactApp("Test")

        with pytest.raises(ValueError, match="No data"):
            app.generate(output_path)
