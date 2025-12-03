#!/usr/bin/env python3
"""
Sample dashboard generation demo.
Run from repository root: python examples/sample-dashboard/run_demo.py
"""

import sys
from pathlib import Path

# Add repo root to path
repo_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(repo_root))

from core.kds_theme import KDSTheme
from core.kds_data import KDSData
from core.webapp_engine import KDSWebApp


def main():
    """Generate a sample dashboard demonstrating KACA capabilities."""
    print("KACA Web Application Demo")
    print("=" * 40)

    # Setup paths
    example_dir = Path(__file__).parent
    data_config = {
        "sales": {
            "type": "csv",
            "path": str(example_dir / "data" / "sales.csv"),
            "keys": ["region", "product", "month"],
            "value_cols": ["revenue", "units"],
        }
    }

    # Initialize theme and data
    print("\nInitializing...")
    theme = KDSTheme()
    data = KDSData.from_dict(data_config)

    print(f"  Theme: Kearney Purple ({theme.primary})")
    print(f"  Data sources: {data.list_sources()}")

    # Get summary stats for metrics
    df = data.query("sales")
    total_revenue = df["revenue"].sum()
    total_units = df["units"].sum()
    avg_deal = df["revenue"].mean()

    print(f"\nData summary:")
    print(f"  Total Revenue: ${total_revenue:,.0f}")
    print(f"  Total Units: {total_units:,.0f}")
    print(f"  Avg Deal Size: ${avg_deal:,.2f}")

    # Build dashboard
    print("\nBuilding dashboard...")
    app = (
        KDSWebApp("Regional Sales Dashboard", theme=theme)
        .set_data(data)
        .add_metric("Total Revenue", f"${total_revenue:,.0f}")
        .add_metric("Units Sold", f"{total_units:,.0f}")
        .add_metric("Avg Deal Size", f"${avg_deal:,.2f}")
        .add_chart("sales", "bar", "region", "revenue", "Revenue by Region")
        .add_chart("sales", "line", "month", "revenue", "Revenue Trend")
        .add_table("sales", "Sales Details")
        .add_filter("sales", "region", "dropdown")
        .add_filter("sales", "product", "multi")
    )

    # Generate output
    output_path = example_dir / "output" / "dashboard.html"
    result = app.generate(output_path)

    print(f"\nDashboard generated successfully!")
    print(f"  Output: {result}")
    print(f"  Size: {result.stat().st_size / 1024:.1f} KB")
    print(f"\nOpen in browser to preview.")


if __name__ == "__main__":
    main()
