# Analytics Chart Template
# KDS-Compliant Chart Generation
#
# Usage:
#   from templates.analytics.chart_template import create_kds_charts
#   create_kds_charts(data_path, output_dir)

import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from core.chart_engine import KDSChart, ChartConfig
from core.data_profiler import profile_dataset
import pandas as pd


def create_bar_chart(
    df: pd.DataFrame,
    x_column: str,
    y_column: str,
    title: str,
    output_path: Path,
    horizontal: bool = False
) -> Path:
    """Create a KDS-compliant bar chart."""
    chart = KDSChart()
    config = ChartConfig(
        title=title,
        x_label=x_column,
        y_label=y_column,
        show_legend=False
    )

    categories = df[x_column].tolist()
    values = df[y_column].tolist()

    chart.bar_chart(
        categories=categories,
        values=values,
        config=config,
        horizontal=horizontal
    )

    chart.save(output_path)
    return output_path


def create_line_chart(
    df: pd.DataFrame,
    x_column: str,
    y_columns: list,
    title: str,
    output_path: Path
) -> Path:
    """Create a KDS-compliant line chart."""
    chart = KDSChart()
    config = ChartConfig(
        title=title,
        x_label=x_column,
        y_label="Value",
        show_legend=len(y_columns) > 1
    )

    x_values = df[x_column].tolist()
    series_data = {col: df[col].tolist() for col in y_columns}

    chart.line_chart(
        x_values=x_values,
        series_data=series_data,
        config=config
    )

    chart.save(output_path)
    return output_path


def create_pie_chart(
    df: pd.DataFrame,
    label_column: str,
    value_column: str,
    title: str,
    output_path: Path
) -> Path:
    """Create a KDS-compliant pie chart."""
    chart = KDSChart()
    config = ChartConfig(
        title=title,
        show_legend=True
    )

    labels = df[label_column].tolist()
    values = df[value_column].tolist()

    chart.pie_chart(
        labels=labels,
        values=values,
        config=config,
        show_percentages=True
    )

    chart.save(output_path)
    return output_path


def create_kds_charts(data_path: Path, output_dir: Path) -> dict:
    """
    Automatically generate appropriate charts based on data profile.

    Returns dict of chart type -> output path.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Profile the dataset
    profile = profile_dataset(data_path)
    df = pd.read_csv(data_path) if str(data_path).endswith('.csv') else pd.read_excel(data_path)

    charts_created = {}

    # Find categorical and numeric columns
    categorical_cols = [c.name for c in profile.columns if c.dtype == 'object']
    numeric_cols = [c.name for c in profile.columns if c.dtype in ['int64', 'float64']]

    # Create bar chart if we have categorical + numeric
    if categorical_cols and numeric_cols:
        cat_col = categorical_cols[0]
        num_col = numeric_cols[0]

        # Aggregate if needed
        agg_df = df.groupby(cat_col)[num_col].sum().reset_index()

        bar_path = output_dir / "bar_chart.png"
        create_bar_chart(
            agg_df,
            cat_col,
            num_col,
            f"{num_col} by {cat_col}",
            bar_path
        )
        charts_created['bar'] = bar_path

    # Create pie chart for categorical distribution
    if categorical_cols:
        cat_col = categorical_cols[0]
        pie_df = df[cat_col].value_counts().reset_index()
        pie_df.columns = [cat_col, 'count']

        pie_path = output_dir / "pie_chart.png"
        create_pie_chart(
            pie_df,
            cat_col,
            'count',
            f"Distribution of {cat_col}",
            pie_path
        )
        charts_created['pie'] = pie_path

    # Create line chart if we have date-like column
    date_cols = [c for c in df.columns if 'date' in c.lower() or 'time' in c.lower()]
    if date_cols and numeric_cols:
        date_col = date_cols[0]
        num_col = numeric_cols[0]

        line_df = df.sort_values(date_col)[[date_col, num_col]].head(20)

        line_path = output_dir / "line_chart.png"
        create_line_chart(
            line_df,
            date_col,
            [num_col],
            f"{num_col} over Time",
            line_path
        )
        charts_created['line'] = line_path

    return charts_created


if __name__ == "__main__":
    # Example usage
    import argparse

    parser = argparse.ArgumentParser(description="Generate KDS charts from data")
    parser.add_argument("data_path", help="Path to CSV or Excel file")
    parser.add_argument("--output", "-o", default="outputs/charts", help="Output directory")

    args = parser.parse_args()

    charts = create_kds_charts(Path(args.data_path), Path(args.output))
    print(f"Created {len(charts)} charts:")
    for chart_type, path in charts.items():
        print(f"  - {chart_type}: {path}")
