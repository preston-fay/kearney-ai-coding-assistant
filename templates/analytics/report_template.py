# Analytics Report Template
# KDS-Compliant Report Generation
#
# Usage:
#   from templates.analytics.report_template import generate_report
#   generate_report(data_path, output_path)

import sys
from pathlib import Path
from datetime import datetime
from typing import Optional

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from core.data_profiler import profile_dataset, DatasetProfile


def generate_markdown_report(
    profile: DatasetProfile,
    title: str,
    output_path: Path,
    additional_insights: Optional[list] = None
) -> Path:
    """Generate a KDS-compliant markdown report from data profile."""

    lines = [
        f"# {title}",
        "",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "---",
        "",
        "## Dataset Overview",
        "",
        f"- **Total Rows**: {profile.row_count:,}",
        f"- **Total Columns**: {profile.column_count}",
        f"- **Memory Usage**: {profile.memory_usage_mb:.2f} MB",
        "",
    ]

    # Quality issues section
    if profile.quality_issues:
        lines.extend([
            "## Data Quality Issues",
            "",
        ])
        for issue in profile.quality_issues:
            lines.append(f"- {issue}")
        lines.append("")

    # Column details
    lines.extend([
        "## Column Analysis",
        "",
        "| Column | Type | Unique | Nulls | Sample Values |",
        "|--------|------|--------|-------|---------------|",
    ])

    for col in profile.columns:
        sample = ", ".join(str(v) for v in col.sample_values[:3]) if col.sample_values else "N/A"
        null_pct = f"{col.null_percentage:.1f}%" if col.null_percentage else "0%"
        lines.append(f"| {col.name} | {col.dtype} | {col.unique_count} | {null_pct} | {sample} |")

    lines.append("")

    # Numeric statistics
    numeric_cols = [c for c in profile.columns if c.dtype in ['int64', 'float64'] and c.statistics]
    if numeric_cols:
        lines.extend([
            "## Numeric Column Statistics",
            "",
            "| Column | Min | Max | Mean | Median | Std Dev |",
            "|--------|-----|-----|------|--------|---------|",
        ])

        for col in numeric_cols:
            stats = col.statistics
            lines.append(
                f"| {col.name} | "
                f"{stats.get('min', 'N/A'):.2f} | "
                f"{stats.get('max', 'N/A'):.2f} | "
                f"{stats.get('mean', 'N/A'):.2f} | "
                f"{stats.get('median', 'N/A'):.2f} | "
                f"{stats.get('std', 'N/A'):.2f} |"
            )
        lines.append("")

    # Additional insights
    if additional_insights:
        lines.extend([
            "## Key Insights",
            "",
        ])
        for i, insight in enumerate(additional_insights, 1):
            lines.append(f"{i}. {insight}")
        lines.append("")

    # Footer
    lines.extend([
        "---",
        "",
        "*Report generated using Kearney AI Coding Assistant*",
    ])

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines))

    return output_path


def generate_report(
    data_path: Path,
    output_path: Path,
    title: Optional[str] = None
) -> Path:
    """
    Generate a complete analytics report from a data file.

    Args:
        data_path: Path to CSV or Excel file
        output_path: Path for output markdown file
        title: Report title (defaults to filename)

    Returns:
        Path to generated report
    """
    data_path = Path(data_path)
    output_path = Path(output_path)

    if not title:
        title = f"Analysis Report: {data_path.stem}"

    # Profile the dataset
    profile = profile_dataset(data_path)

    # Generate insights based on profile
    insights = []

    # Check for high null columns
    high_null_cols = [c for c in profile.columns if c.null_percentage and c.null_percentage > 10]
    if high_null_cols:
        insights.append(
            f"Columns with significant missing data (>10%): {', '.join(c.name for c in high_null_cols)}"
        )

    # Check for potential ID columns
    potential_ids = [c for c in profile.columns if c.is_potential_id]
    if potential_ids:
        insights.append(
            f"Potential identifier columns detected: {', '.join(c.name for c in potential_ids)}"
        )

    # Check for categorical columns with many values
    high_cardinality = [
        c for c in profile.columns
        if c.dtype == 'object' and c.unique_count and c.unique_count > 100
    ]
    if high_cardinality:
        insights.append(
            f"High-cardinality categorical columns: {', '.join(c.name for c in high_cardinality)}"
        )

    return generate_markdown_report(profile, title, output_path, insights)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate KDS analytics report")
    parser.add_argument("data_path", help="Path to CSV or Excel file")
    parser.add_argument("--output", "-o", default="outputs/report.md", help="Output path")
    parser.add_argument("--title", "-t", help="Report title")

    args = parser.parse_args()

    report_path = generate_report(
        Path(args.data_path),
        Path(args.output),
        args.title
    )
    print(f"Report generated: {report_path}")
