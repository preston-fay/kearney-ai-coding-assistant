"""
Kearney Web Application Engine

Generates web applications in three tiers:
- Static HTML: Single self-contained file with embedded data
- Streamlit: Python app with config and requirements
- React: Full Vite project scaffold

Usage:
    from core.kds_theme import KDSTheme
    from core.kds_data import KDSData
    from core.webapp_engine import KDSWebApp, KDSStreamlitApp, KDSReactApp

    # Static HTML
    app = KDSWebApp("Dashboard", theme=KDSTheme())
    app.set_data(data).add_metric("Revenue", "$1M").generate("output.html")

    # Streamlit
    app = KDSStreamlitApp("Dashboard", theme=KDSTheme())
    app.set_data(data).generate("output_dir/")

    # React
    app = KDSReactApp("Dashboard", theme=KDSTheme())
    app.set_data(data).generate("output_dir/")

Brand Rules:
    - Primary: Kearney Purple (#7823DC)
    - NO GREEN colors anywhere
    - Dark mode default (#1E1E1E background)
    - Inter font family
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Union

from core.kds_theme import KDSTheme
from core.kds_data import KDSData
from core.kds_utils import safe_write_text

logger = logging.getLogger(__name__)


class KDSWebApp:
    """
    Static HTML dashboard generator with Kearney brand compliance.

    Generates a single self-contained HTML file with:
    - Embedded CSS from KDSTheme
    - Embedded JSON data from KDSData
    - Plotly.js charts (CDN)
    - Client-side filtering JavaScript
    - Responsive 2-column layout

    Example:
        app = (
            KDSWebApp("Sales Dashboard")
            .set_data(data)
            .add_metric("Revenue", "$1.2M", "+15%")
            .add_chart("sales", "bar", "region", "revenue", "By Region")
            .add_table("sales", "Details")
            .generate("dashboard.html")
        )
    """

    def __init__(self, title: str, theme: Optional[KDSTheme] = None):
        """
        Initialize static HTML web app.

        Args:
            title: Dashboard title
            theme: KDSTheme instance (uses default if None)
        """
        self.title = title
        self.theme = theme or KDSTheme()
        self._data: Optional[KDSData] = None
        self._metrics: List[Dict] = []
        self._charts: List[Dict] = []
        self._tables: List[Dict] = []
        self._filters: List[Dict] = []

    def set_data(self, data: KDSData) -> "KDSWebApp":
        """
        Set the data source for the dashboard.

        Args:
            data: KDSData instance with loaded sources

        Returns:
            self for method chaining
        """
        self._data = data
        return self

    def add_metric(
        self,
        label: str,
        value: str,
        delta: Optional[str] = None,
        delta_positive: bool = True
    ) -> "KDSWebApp":
        """
        Add a KPI metric card.

        Args:
            label: Metric label (e.g., "Total Revenue")
            value: Formatted value (e.g., "$1.2M")
            delta: Optional change indicator (e.g., "+15%")
            delta_positive: If True, delta is positive (purple), else negative (coral)

        Returns:
            self for method chaining
        """
        self._metrics.append({
            "label": label,
            "value": value,
            "delta": delta,
            "delta_positive": delta_positive,
        })
        return self

    def add_chart(
        self,
        source_name: str,
        chart_type: Literal["bar", "line", "pie", "scatter"],
        x_col: str,
        y_col: str,
        title: str,
        color_col: Optional[str] = None,
        aggregation: Optional[str] = None,
    ) -> "KDSWebApp":
        """
        Add an interactive Plotly chart.

        Args:
            source_name: Name of data source
            chart_type: Type of chart
            x_col: Column for x-axis
            y_col: Column for y-axis
            title: Chart title
            color_col: Optional column for color grouping
            aggregation: Optional aggregation (sum, mean, count)

        Returns:
            self for method chaining
        """
        self._charts.append({
            "source": source_name,
            "type": chart_type,
            "x": x_col,
            "y": y_col,
            "title": title,
            "color": color_col,
            "aggregation": aggregation,
        })
        return self

    def add_table(
        self,
        source_name: str,
        title: str,
        columns: Optional[List[str]] = None,
        page_size: int = 10,
    ) -> "KDSWebApp":
        """
        Add an interactive data table.

        Args:
            source_name: Name of data source
            title: Table title
            columns: Columns to display (all if None)
            page_size: Rows per page

        Returns:
            self for method chaining
        """
        self._tables.append({
            "source": source_name,
            "title": title,
            "columns": columns,
            "page_size": page_size,
        })
        return self

    def add_filter(
        self,
        source_name: str,
        column: str,
        filter_type: Literal["dropdown", "multi", "date_range"] = "dropdown",
    ) -> "KDSWebApp":
        """
        Add an interactive filter control.

        Args:
            source_name: Name of data source
            column: Column to filter on
            filter_type: Type of filter control

        Returns:
            self for method chaining
        """
        self._filters.append({
            "source": source_name,
            "column": column,
            "type": filter_type,
        })
        return self

    def _generate_css(self) -> str:
        """Generate CSS with theme variables."""
        theme_vars = self.theme.to_css_variables()
        return f"""
{theme_vars}

* {{
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}}

body {{
    font-family: var(--kds-font-family);
    background-color: var(--kds-background-dark);
    color: var(--kds-text-light);
    line-height: 1.6;
    min-height: 100vh;
}}

.container {{
    max-width: 1400px;
    margin: 0 auto;
    padding: var(--kds-spacing-lg);
}}

header {{
    margin-bottom: var(--kds-spacing-xl);
}}

h1 {{
    font-size: var(--kds-font-size-xxl);
    font-weight: var(--kds-font-weight-bold);
    color: var(--kds-text-light);
    margin-bottom: var(--kds-spacing-sm);
}}

.subtitle {{
    color: var(--kds-text-muted);
    font-size: var(--kds-font-size-base);
}}

/* Metrics Grid */
.metrics-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: var(--kds-spacing-md);
    margin-bottom: var(--kds-spacing-xl);
}}

.metric-card {{
    background: var(--kds-surface-dark);
    border-radius: var(--kds-radius-md);
    padding: var(--kds-spacing-lg);
    border-left: 4px solid var(--kds-primary);
}}

.metric-label {{
    font-size: var(--kds-font-size-small);
    color: var(--kds-text-muted);
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: var(--kds-spacing-xs);
}}

.metric-value {{
    font-size: var(--kds-font-size-xxl);
    font-weight: var(--kds-font-weight-bold);
    color: var(--kds-text-light);
}}

.metric-delta {{
    font-size: var(--kds-font-size-small);
    margin-top: var(--kds-spacing-xs);
}}

.metric-delta.positive {{
    color: var(--kds-positive);
}}

.metric-delta.negative {{
    color: var(--kds-negative);
}}

/* Filters */
.filters-section {{
    display: flex;
    gap: var(--kds-spacing-md);
    flex-wrap: wrap;
    margin-bottom: var(--kds-spacing-xl);
    padding: var(--kds-spacing-md);
    background: var(--kds-surface-dark);
    border-radius: var(--kds-radius-md);
}}

.filter-group {{
    display: flex;
    flex-direction: column;
    gap: var(--kds-spacing-xs);
}}

.filter-label {{
    font-size: var(--kds-font-size-small);
    color: var(--kds-text-muted);
}}

.filter-select {{
    background: var(--kds-background-dark);
    color: var(--kds-text-light);
    border: 1px solid var(--kds-gray-500);
    border-radius: var(--kds-radius-sm);
    padding: var(--kds-spacing-sm) var(--kds-spacing-md);
    font-size: var(--kds-font-size-base);
    min-width: 150px;
}}

.filter-select:focus {{
    outline: none;
    border-color: var(--kds-primary);
}}

/* Charts Grid */
.charts-grid {{
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: var(--kds-spacing-lg);
    margin-bottom: var(--kds-spacing-xl);
}}

.chart-card {{
    background: var(--kds-surface-dark);
    border-radius: var(--kds-radius-md);
    padding: var(--kds-spacing-lg);
}}

.chart-title {{
    font-size: var(--kds-font-size-large);
    font-weight: var(--kds-font-weight-medium);
    margin-bottom: var(--kds-spacing-md);
    color: var(--kds-text-light);
}}

.chart-container {{
    height: 300px;
}}

/* Tables */
.table-section {{
    background: var(--kds-surface-dark);
    border-radius: var(--kds-radius-md);
    padding: var(--kds-spacing-lg);
    margin-bottom: var(--kds-spacing-xl);
    overflow-x: auto;
}}

.table-title {{
    font-size: var(--kds-font-size-large);
    font-weight: var(--kds-font-weight-medium);
    margin-bottom: var(--kds-spacing-md);
}}

table {{
    width: 100%;
    border-collapse: collapse;
}}

th, td {{
    text-align: left;
    padding: var(--kds-spacing-sm) var(--kds-spacing-md);
    border-bottom: 1px solid var(--kds-gray-600);
}}

th {{
    font-weight: var(--kds-font-weight-medium);
    color: var(--kds-text-muted);
    font-size: var(--kds-font-size-small);
    text-transform: uppercase;
}}

tr:hover {{
    background: rgba(120, 35, 220, 0.1);
}}

/* Footer */
footer {{
    text-align: center;
    padding: var(--kds-spacing-xl) 0;
    color: var(--kds-text-muted);
    font-size: var(--kds-font-size-small);
    border-top: 1px solid var(--kds-gray-600);
    margin-top: var(--kds-spacing-xl);
}}

/* Responsive */
@media (max-width: 768px) {{
    .charts-grid {{
        grid-template-columns: 1fr;
    }}

    .metrics-grid {{
        grid-template-columns: repeat(2, 1fr);
    }}

    .filters-section {{
        flex-direction: column;
    }}
}}

@media (max-width: 480px) {{
    .metrics-grid {{
        grid-template-columns: 1fr;
    }}

    .container {{
        padding: var(--kds-spacing-md);
    }}
}}
"""

    def _generate_plotly_config(self) -> Dict:
        """Generate Plotly template from theme."""
        return self.theme.to_plotly_template()

    def _generate_html(self) -> str:
        """Generate complete HTML document."""
        if self._data is None:
            raise ValueError("No data set. Call set_data() before generate().")

        # Get data snapshot
        data_snapshot = self._data.snapshot()

        # Generate unique IDs for elements
        chart_ids = [f"chart_{i}" for i in range(len(self._charts))]

        # Build metrics HTML
        metrics_html = ""
        for metric in self._metrics:
            delta_html = ""
            if metric["delta"]:
                delta_class = "positive" if metric["delta_positive"] else "negative"
                delta_html = f'<div class="metric-delta {delta_class}">{metric["delta"]}</div>'
            metrics_html += f"""
            <div class="metric-card">
                <div class="metric-label">{metric["label"]}</div>
                <div class="metric-value">{metric["value"]}</div>
                {delta_html}
            </div>
            """

        # Build filters HTML
        filters_html = ""
        if self._filters:
            filter_controls = ""
            for i, f in enumerate(self._filters):
                options = self._data.get_unique_values(f["source"], f["column"])
                options_html = '<option value="">All</option>'
                for opt in options:
                    options_html += f'<option value="{opt}">{opt}</option>'

                if f["type"] == "multi":
                    filter_controls += f"""
                    <div class="filter-group">
                        <label class="filter-label">{f["column"]}</label>
                        <select class="filter-select" id="filter_{i}" multiple data-source="{f["source"]}" data-column="{f["column"]}">
                            {options_html}
                        </select>
                    </div>
                    """
                else:
                    filter_controls += f"""
                    <div class="filter-group">
                        <label class="filter-label">{f["column"]}</label>
                        <select class="filter-select" id="filter_{i}" data-source="{f["source"]}" data-column="{f["column"]}">
                            {options_html}
                        </select>
                    </div>
                    """
            filters_html = f'<div class="filters-section">{filter_controls}</div>'

        # Build charts HTML
        charts_html = ""
        for i, chart in enumerate(self._charts):
            charts_html += f"""
            <div class="chart-card">
                <div class="chart-title">{chart["title"]}</div>
                <div class="chart-container" id="{chart_ids[i]}"></div>
            </div>
            """

        # Build tables HTML
        tables_html = ""
        for table in self._tables:
            df_data = self._data.query(table["source"])
            cols = table["columns"] or list(df_data.columns)

            headers = "".join(f"<th>{col}</th>" for col in cols)
            rows = ""
            for _, row in df_data.head(table["page_size"]).iterrows():
                cells = "".join(f"<td>{row[col]}</td>" for col in cols)
                rows += f"<tr>{cells}</tr>"

            tables_html += f"""
            <div class="table-section" data-source="{table["source"]}">
                <div class="table-title">{table["title"]}</div>
                <table>
                    <thead><tr>{headers}</tr></thead>
                    <tbody>{rows}</tbody>
                </table>
            </div>
            """

        # Build chart initialization JavaScript
        plotly_template = json.dumps(self._generate_plotly_config())
        charts_js = ""
        for i, chart in enumerate(self._charts):
            source_data = f"window.kdsData['{chart['source']}']"

            if chart["type"] == "bar":
                # Aggregate data for bar chart
                charts_js += f"""
                (function() {{
                    const data = {source_data};
                    const aggregated = {{}};
                    data.forEach(row => {{
                        const key = row['{chart["x"]}'];
                        if (!aggregated[key]) aggregated[key] = 0;
                        aggregated[key] += row['{chart["y"]}'] || 0;
                    }});
                    const x = Object.keys(aggregated);
                    const y = Object.values(aggregated);

                    Plotly.newPlot('{chart_ids[i]}', [{{
                        type: 'bar',
                        x: x,
                        y: y,
                        marker: {{ color: '{self.theme.primary}' }}
                    }}], {{
                        ...kdsTemplate.layout,
                        margin: {{ l: 50, r: 30, t: 30, b: 50 }}
                    }}, {{ responsive: true }});
                }})();
                """
            elif chart["type"] == "line":
                charts_js += f"""
                (function() {{
                    const data = {source_data};
                    const aggregated = {{}};
                    data.forEach(row => {{
                        const key = row['{chart["x"]}'];
                        if (!aggregated[key]) aggregated[key] = 0;
                        aggregated[key] += row['{chart["y"]}'] || 0;
                    }});
                    const x = Object.keys(aggregated);
                    const y = Object.values(aggregated);

                    Plotly.newPlot('{chart_ids[i]}', [{{
                        type: 'scatter',
                        mode: 'lines+markers',
                        x: x,
                        y: y,
                        line: {{ color: '{self.theme.primary}' }},
                        marker: {{ color: '{self.theme.primary}' }}
                    }}], {{
                        ...kdsTemplate.layout,
                        margin: {{ l: 50, r: 30, t: 30, b: 50 }}
                    }}, {{ responsive: true }});
                }})();
                """
            elif chart["type"] == "pie":
                charts_js += f"""
                (function() {{
                    const data = {source_data};
                    const aggregated = {{}};
                    data.forEach(row => {{
                        const key = row['{chart["x"]}'];
                        if (!aggregated[key]) aggregated[key] = 0;
                        aggregated[key] += row['{chart["y"]}'] || 0;
                    }});

                    Plotly.newPlot('{chart_ids[i]}', [{{
                        type: 'pie',
                        labels: Object.keys(aggregated),
                        values: Object.values(aggregated),
                        marker: {{ colors: {json.dumps(list(self.theme.chart_palette))} }}
                    }}], {{
                        ...kdsTemplate.layout,
                        margin: {{ l: 30, r: 30, t: 30, b: 30 }},
                        showlegend: true,
                        legend: {{ orientation: 'h', y: -0.1 }}
                    }}, {{ responsive: true }});
                }})();
                """
            elif chart["type"] == "scatter":
                charts_js += f"""
                (function() {{
                    const data = {source_data};
                    const x = data.map(row => row['{chart["x"]}']);
                    const y = data.map(row => row['{chart["y"]}']);

                    Plotly.newPlot('{chart_ids[i]}', [{{
                        type: 'scatter',
                        mode: 'markers',
                        x: x,
                        y: y,
                        marker: {{ color: '{self.theme.primary}', size: 8 }}
                    }}], {{
                        ...kdsTemplate.layout,
                        margin: {{ l: 50, r: 30, t: 30, b: 50 }}
                    }}, {{ responsive: true }});
                }})();
                """

        # Generate timestamp
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.title}</title>
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <style>
    {self._generate_css()}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>{self.title}</h1>
            <p class="subtitle">Generated {timestamp}</p>
        </header>

        <div class="metrics-grid">
            {metrics_html}
        </div>

        {filters_html}

        <div class="charts-grid">
            {charts_html}
        </div>

        {tables_html}

        <footer>
            Generated by KACA | Kearney Digital & Analytics
        </footer>
    </div>

    <script type="application/json" id="kds-data">
    {json.dumps(data_snapshot)}
    </script>

    <script>
    // Load embedded data
    window.kdsData = JSON.parse(document.getElementById('kds-data').textContent);

    // Plotly template
    const kdsTemplate = {plotly_template};

    // Initialize charts
    {charts_js}

    // Filter functionality
    document.querySelectorAll('.filter-select').forEach(select => {{
        select.addEventListener('change', function() {{
            const source = this.dataset.source;
            const column = this.dataset.column;
            const value = this.value;

            // Filter logic would update charts/tables here
            console.log('Filter:', source, column, value);
        }});
    }});
    </script>
</body>
</html>
"""

    def generate(self, output_path: Union[str, Path]) -> Path:
        """
        Generate the static HTML dashboard.

        Args:
            output_path: Output file path

        Returns:
            Path to generated file
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        html = self._generate_html()
        safe_write_text(output_path, html)

        # Run brand guard check (warn only)
        try:
            from core.brand_guard import check_file
            violations = check_file(output_path)
            for v in violations:
                logger.warning(f"Brand violation: {v.rule} - {v.message}")
        except ImportError:
            pass

        logger.info(f"Dashboard generated: {output_path}")
        return output_path


class KDSStreamlitApp:
    """
    Streamlit application generator with Kearney brand compliance.

    Generates a directory containing:
    - app.py: Main Streamlit application
    - .streamlit/config.toml: Theme configuration
    - requirements.txt: Dependencies

    Example:
        app = KDSStreamlitApp("Sales Dashboard")
        app.set_data(data).generate("output_dir/")
    """

    def __init__(self, title: str, theme: Optional[KDSTheme] = None):
        """
        Initialize Streamlit app generator.

        Args:
            title: Application title
            theme: KDSTheme instance (uses default if None)
        """
        self.title = title
        self.theme = theme or KDSTheme()
        self._data: Optional[KDSData] = None
        self._data_config: Optional[Dict] = None
        self._metrics: List[Dict] = []
        self._charts: List[Dict] = []
        self._tables: List[Dict] = []
        self._filters: List[Dict] = []

    def set_data(self, data: KDSData, config: Optional[Dict] = None) -> "KDSStreamlitApp":
        """Set data source."""
        self._data = data
        self._data_config = config
        return self

    def add_metric(self, label: str, value: str, delta: Optional[str] = None, delta_positive: bool = True) -> "KDSStreamlitApp":
        """Add a metric card."""
        self._metrics.append({"label": label, "value": value, "delta": delta, "delta_positive": delta_positive})
        return self

    def add_chart(self, source_name: str, chart_type: str, x_col: str, y_col: str, title: str, color_col: Optional[str] = None) -> "KDSStreamlitApp":
        """Add a chart."""
        self._charts.append({"source": source_name, "type": chart_type, "x": x_col, "y": y_col, "title": title, "color": color_col})
        return self

    def add_table(self, source_name: str, title: str, columns: Optional[List[str]] = None) -> "KDSStreamlitApp":
        """Add a data table."""
        self._tables.append({"source": source_name, "title": title, "columns": columns})
        return self

    def add_filter(self, source_name: str, column: str, filter_type: str = "dropdown") -> "KDSStreamlitApp":
        """Add a filter."""
        self._filters.append({"source": source_name, "column": column, "type": filter_type})
        return self

    def _generate_app_py(self) -> str:
        """Generate main Streamlit application code."""
        # Build metrics code
        metrics_code = ""
        if self._metrics:
            cols = f"cols = st.columns({len(self._metrics)})"
            metrics_items = []
            for i, m in enumerate(self._metrics):
                delta_val = f'"{m["delta"]}"' if m["delta"] else "None"
                metrics_items.append(f'cols[{i}].metric("{m["label"]}", "{m["value"]}", {delta_val})')
            metrics_code = f"{cols}\n    " + "\n    ".join(metrics_items)

        # Build filter code
        filter_code = ""
        if self._filters:
            filter_items = []
            for f in self._filters:
                var_name = f["column"].lower().replace(" ", "_")
                if f["type"] == "multi":
                    filter_items.append(f'{var_name} = st.sidebar.multiselect("{f["column"]}", data["{f["source"]}"]["{f["column"]}"].unique())')
                else:
                    filter_items.append(f'{var_name} = st.sidebar.selectbox("{f["column"]}", ["All"] + list(data["{f["source"]}"]["{f["column"]}"].unique()))')
            filter_code = "\n    ".join(filter_items)

        # Build chart code
        chart_code = ""
        for chart in self._charts:
            if chart["type"] == "bar":
                chart_code += f'''
    st.subheader("{chart["title"]}")
    chart_data = data["{chart["source"]}"].groupby("{chart["x"]}")["{chart["y"]}"].sum().reset_index()
    fig = px.bar(chart_data, x="{chart["x"]}", y="{chart["y"]}", color_discrete_sequence=["{self.theme.primary}"])
    fig.update_layout(template=None, paper_bgcolor="{self.theme.background_dark}", plot_bgcolor="{self.theme.background_dark}", font_color="{self.theme.text_light}")
    st.plotly_chart(fig, use_container_width=True)
'''
            elif chart["type"] == "line":
                chart_code += f'''
    st.subheader("{chart["title"]}")
    chart_data = data["{chart["source"]}"].groupby("{chart["x"]}")["{chart["y"]}"].sum().reset_index()
    fig = px.line(chart_data, x="{chart["x"]}", y="{chart["y"]}", color_discrete_sequence=["{self.theme.primary}"])
    fig.update_layout(template=None, paper_bgcolor="{self.theme.background_dark}", plot_bgcolor="{self.theme.background_dark}", font_color="{self.theme.text_light}")
    st.plotly_chart(fig, use_container_width=True)
'''
            elif chart["type"] == "pie":
                chart_code += f'''
    st.subheader("{chart["title"]}")
    chart_data = data["{chart["source"]}"].groupby("{chart["x"]}")["{chart["y"]}"].sum().reset_index()
    fig = px.pie(chart_data, names="{chart["x"]}", values="{chart["y"]}", color_discrete_sequence={list(self.theme.chart_palette)})
    fig.update_layout(template=None, paper_bgcolor="{self.theme.background_dark}", plot_bgcolor="{self.theme.background_dark}", font_color="{self.theme.text_light}")
    st.plotly_chart(fig, use_container_width=True)
'''

        # Build table code
        table_code = ""
        for table in self._tables:
            cols_str = f", columns={table['columns']}" if table["columns"] else ""
            table_code += f'''
    st.subheader("{table["title"]}")
    st.dataframe(data["{table["source"]}"][[{', '.join([f'"{c}"' for c in table["columns"]])}]] if {table["columns"]} else data["{table["source"]}"])
''' if table["columns"] else f'''
    st.subheader("{table["title"]}")
    st.dataframe(data["{table["source"]}"])
'''

        # Generate data loading code
        data_sources = self._data.list_sources() if self._data else []
        data_loading = ""
        for source in data_sources:
            # Assume CSV for Streamlit generation
            data_loading += f'    "{source}": pd.read_csv("data/{source}.csv"),\n'

        return f'''"""
{self.title} - Streamlit Application
Generated by KACA | Kearney Digital & Analytics
"""

import streamlit as st
import pandas as pd
import plotly.express as px

# Page config
st.set_page_config(
    page_title="{self.title}",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .stApp {{
        background-color: {self.theme.background_dark};
    }}
    .stMetric {{
        background-color: {self.theme.surface_dark};
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid {self.theme.primary};
    }}
</style>
""", unsafe_allow_html=True)

# Load data
@st.cache_data
def load_data():
    return {{
{data_loading}    }}

data = load_data()

# Title
st.title("{self.title}")

# Sidebar filters
st.sidebar.header("Filters")
{filter_code if filter_code else "# No filters defined"}

# Metrics
{metrics_code if metrics_code else "# No metrics defined"}

# Charts
{chart_code if chart_code else "# No charts defined"}

# Tables
{table_code if table_code else "# No tables defined"}

# Footer
st.markdown("---")
st.markdown("*Generated by KACA | Kearney Digital & Analytics*")
'''

    def _generate_config_toml(self) -> str:
        """Generate Streamlit config.toml."""
        return self.theme.to_streamlit_config()

    def _generate_requirements(self) -> str:
        """Generate requirements.txt."""
        return """streamlit>=1.28.0
pandas>=2.0.0
plotly>=5.17.0
"""

    def generate(self, output_path: Union[str, Path]) -> Path:
        """
        Generate Streamlit application directory.

        Args:
            output_path: Output directory path

        Returns:
            Path to generated directory
        """
        if self._data is None:
            raise ValueError("No data set. Call set_data() before generate().")

        output_path = Path(output_path)
        output_path.mkdir(parents=True, exist_ok=True)

        # Create .streamlit directory
        streamlit_dir = output_path / ".streamlit"
        streamlit_dir.mkdir(exist_ok=True)

        # Create data directory and export data
        data_dir = output_path / "data"
        data_dir.mkdir(exist_ok=True)
        for source in self._data.list_sources():
            df = self._data.query(source)
            df.to_csv(data_dir / f"{source}.csv", index=False)

        # Write files with safe encoding
        app_py_path = output_path / "app.py"
        safe_write_text(app_py_path, self._generate_app_py())
        safe_write_text(streamlit_dir / "config.toml", self._generate_config_toml())
        safe_write_text(output_path / "requirements.txt", self._generate_requirements())

        # Create README
        safe_write_text(output_path / "README.md", f"""# {self.title}

Streamlit application generated by KACA.

## Quick Start

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Files

- `app.py` - Main application
- `.streamlit/config.toml` - Theme configuration
- `data/` - Data files
- `requirements.txt` - Dependencies

---
Generated by KACA | Kearney Digital & Analytics
""")

        # Run brand guard check on generated Python files
        try:
            from core.brand_guard import check_python_file
            violations = check_python_file(app_py_path)
            for v in violations:
                logger.warning(f"Brand violation in app.py: {v.rule} - {v.message} (line {v.line_number})")
        except ImportError:
            pass

        logger.info(f"Streamlit app generated: {output_path}")
        return output_path


class KDSReactApp:
    """
    React application scaffold generator with Kearney brand compliance.

    Generates a Vite + React project with:
    - Pre-configured theme
    - Sample components
    - Data loading utilities
    - Recharts for visualizations

    Example:
        app = KDSReactApp("Sales Dashboard")
        app.set_data(data).generate("output_dir/")
    """

    def __init__(self, title: str, theme: Optional[KDSTheme] = None):
        """
        Initialize React app generator.

        Args:
            title: Application title
            theme: KDSTheme instance (uses default if None)
        """
        self.title = title
        self.theme = theme or KDSTheme()
        self._data: Optional[KDSData] = None
        self._metrics: List[Dict] = []
        self._charts: List[Dict] = []
        self._tables: List[Dict] = []
        self._filters: List[Dict] = []

    def set_data(self, data: KDSData) -> "KDSReactApp":
        """Set data source."""
        self._data = data
        return self

    def add_metric(self, label: str, value: str, delta: Optional[str] = None, delta_positive: bool = True) -> "KDSReactApp":
        """Add a metric card."""
        self._metrics.append({"label": label, "value": value, "delta": delta, "delta_positive": delta_positive})
        return self

    def add_chart(self, source_name: str, chart_type: str, x_col: str, y_col: str, title: str, color_col: Optional[str] = None) -> "KDSReactApp":
        """Add a chart."""
        self._charts.append({"source": source_name, "type": chart_type, "x": x_col, "y": y_col, "title": title, "color": color_col})
        return self

    def add_table(self, source_name: str, title: str, columns: Optional[List[str]] = None) -> "KDSReactApp":
        """Add a data table."""
        self._tables.append({"source": source_name, "title": title, "columns": columns})
        return self

    def add_filter(self, source_name: str, column: str, filter_type: str = "dropdown") -> "KDSReactApp":
        """Add a filter."""
        self._filters.append({"source": source_name, "column": column, "type": filter_type})
        return self

    def generate(self, output_path: Union[str, Path]) -> Path:
        """
        Generate React application scaffold.

        Args:
            output_path: Output directory path

        Returns:
            Path to generated directory
        """
        if self._data is None:
            raise ValueError("No data set. Call set_data() before generate().")

        output_path = Path(output_path)
        output_path.mkdir(parents=True, exist_ok=True)

        # Create directory structure
        (output_path / "src").mkdir(exist_ok=True)
        (output_path / "src" / "components").mkdir(exist_ok=True)
        (output_path / "src" / "data").mkdir(exist_ok=True)
        (output_path / "src" / "styles").mkdir(exist_ok=True)
        (output_path / "public").mkdir(exist_ok=True)

        # Export data as JSON
        data_snapshot = self._data.snapshot()
        safe_write_text(output_path / "src" / "data" / "data.json", json.dumps(data_snapshot, indent=2))

        # Generate theme file
        theme_js = self.theme.to_react_theme()
        safe_write_text(output_path / "src" / "styles" / "theme.js", f"export const theme = {json.dumps(theme_js, indent=2)};")

        # Generate package.json
        package_json = {
            "name": self.title.lower().replace(" ", "-"),
            "private": True,
            "version": "0.1.0",
            "type": "module",
            "scripts": {
                "dev": "vite",
                "build": "vite build",
                "preview": "vite preview"
            },
            "dependencies": {
                "react": "^18.2.0",
                "react-dom": "^18.2.0",
                "recharts": "^2.10.0"
            },
            "devDependencies": {
                "@types/react": "^18.2.0",
                "@types/react-dom": "^18.2.0",
                "@vitejs/plugin-react": "^4.2.0",
                "vite": "^5.0.0"
            }
        }
        safe_write_text(output_path / "package.json", json.dumps(package_json, indent=2))

        # Generate vite.config.js
        safe_write_text(output_path / "vite.config.js", """import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
})
""")

        # Generate index.html
        safe_write_text(output_path / "index.html", f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{self.title}</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>
""")

        # Generate main.jsx
        safe_write_text(output_path / "src" / "main.jsx", """import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './styles/index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
""")

        # Generate CSS
        safe_write_text(output_path / "src" / "styles" / "index.css", f"""
:root {{
  --kds-primary: {self.theme.primary};
  --kds-background: {self.theme.background_dark};
  --kds-surface: {self.theme.surface_dark};
  --kds-text: {self.theme.text_light};
  --kds-text-muted: {self.theme.text_muted};
}}

* {{
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}}

body {{
  font-family: {self.theme.font_family};
  background-color: var(--kds-background);
  color: var(--kds-text);
}}

.container {{
  max-width: 1400px;
  margin: 0 auto;
  padding: 24px;
}}

.metrics-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 32px;
}}

.metric-card {{
  background: var(--kds-surface);
  padding: 24px;
  border-radius: 8px;
  border-left: 4px solid var(--kds-primary);
}}

.metric-label {{
  font-size: 12px;
  color: var(--kds-text-muted);
  text-transform: uppercase;
  margin-bottom: 4px;
}}

.metric-value {{
  font-size: 32px;
  font-weight: 600;
}}

.charts-grid {{
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 24px;
}}

.chart-card {{
  background: var(--kds-surface);
  padding: 24px;
  border-radius: 8px;
}}

.chart-title {{
  font-size: 18px;
  font-weight: 500;
  margin-bottom: 16px;
}}

@media (max-width: 768px) {{
  .charts-grid {{
    grid-template-columns: 1fr;
  }}
}}
""")

        # Generate App.jsx
        metrics_jsx = ""
        for m in self._metrics:
            metrics_jsx += f"""
        <div className="metric-card">
          <div className="metric-label">{m["label"]}</div>
          <div className="metric-value">{m["value"]}</div>
        </div>"""

        charts_jsx = ""
        for i, chart in enumerate(self._charts):
            charts_jsx += f"""
        <div className="chart-card">
          <div className="chart-title">{chart["title"]}</div>
          <ResponsiveContainer width="100%" height={{300}}>
            <BarChart data={{data.{chart["source"]}}}>
              <XAxis dataKey="{chart["x"]}" stroke="#999" />
              <YAxis stroke="#999" />
              <Tooltip />
              <Bar dataKey="{chart["y"]}" fill="{self.theme.primary}" />
            </BarChart>
          </ResponsiveContainer>
        </div>"""

        safe_write_text(output_path / "src" / "App.jsx", f"""import React from 'react';
import {{ BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer }} from 'recharts';
import data from './data/data.json';

function App() {{
  return (
    <div className="container">
      <h1>{self.title}</h1>

      <div className="metrics-grid">
        {metrics_jsx}
      </div>

      <div className="charts-grid">
        {charts_jsx}
      </div>

      <footer style={{{{ textAlign: 'center', marginTop: '48px', color: '#666' }}}}>
        Generated by KACA | Kearney Digital & Analytics
      </footer>
    </div>
  );
}}

export default App;
""")

        # Generate README
        safe_write_text(output_path / "README.md", f"""# {self.title}

React application generated by KACA.

## Quick Start

```bash
npm install
npm run dev
```

## Build for Production

```bash
npm run build
```

## Files

- `src/App.jsx` - Main application component
- `src/data/data.json` - Embedded data
- `src/styles/theme.js` - KDS theme tokens
- `src/styles/index.css` - Global styles

---
Generated by KACA | Kearney Digital & Analytics
""")

        logger.info(f"React app generated: {output_path}")
        return output_path
