"""
Kearney Data Profiler - Dataset Analysis and Profiling

Analyzes datasets to extract schema, statistics, and quality issues.
Generates markdown reports for consultant review.

Usage:
    from core.data_profiler import profile_dataset

    profile = profile_dataset('data/raw/sales.csv')
    print(profile.summary)
    profile.save_report('outputs/reports/sales_profile.md')
"""

import logging
from pathlib import Path
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union
from datetime import datetime

try:
    import pandas as pd
except ImportError:
    pd = None  # type: ignore

logger = logging.getLogger(__name__)


@dataclass
class ColumnProfile:
    """Profile for a single column."""
    name: str
    dtype: str
    non_null_count: int
    null_count: int
    null_percentage: float
    unique_count: int
    unique_percentage: float
    sample_values: List[Any] = field(default_factory=list)

    # Numeric stats (if applicable)
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    mean_value: Optional[float] = None
    median_value: Optional[float] = None
    std_value: Optional[float] = None

    # String stats (if applicable)
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    avg_length: Optional[float] = None

    # Quality flags
    has_nulls: bool = False
    is_constant: bool = False
    possible_id: bool = False
    possible_date: bool = False


@dataclass
class DataQualityIssue:
    """Represents a data quality issue."""
    severity: str  # "error", "warning", "info"
    column: Optional[str]
    issue_type: str
    description: str
    recommendation: str


@dataclass
class DatasetProfile:
    """Complete profile for a dataset."""
    file_path: str
    file_name: str
    file_size_bytes: int
    row_count: int
    column_count: int
    columns: List[ColumnProfile]
    quality_issues: List[DataQualityIssue] = field(default_factory=list)
    profiled_at: str = ""

    @property
    def summary(self) -> str:
        """Get a brief text summary of the profile."""
        lines = [
            f"Dataset: {self.file_name}",
            f"Rows: {self.row_count:,}",
            f"Columns: {self.column_count}",
            f"File Size: {self._format_size(self.file_size_bytes)}",
            f"Quality Issues: {len(self.quality_issues)}",
        ]
        return "\n".join(lines)

    @staticmethod
    def _format_size(size_bytes: int) -> str:
        """Format file size in human-readable format."""
        for unit in ["B", "KB", "MB", "GB"]:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} TB"

    def to_markdown(self) -> str:
        """Generate a markdown report."""
        lines = [
            f"# Data Profile: {self.file_name}",
            "",
            f"**Profiled:** {self.profiled_at}",
            "",
            "## Overview",
            "",
            f"| Metric | Value |",
            f"|--------|-------|",
            f"| File Path | `{self.file_path}` |",
            f"| File Size | {self._format_size(self.file_size_bytes)} |",
            f"| Rows | {self.row_count:,} |",
            f"| Columns | {self.column_count} |",
            "",
        ]

        # Quality Issues section
        if self.quality_issues:
            lines.extend([
                "## Quality Issues",
                "",
            ])

            errors = [i for i in self.quality_issues if i.severity == "error"]
            warnings = [i for i in self.quality_issues if i.severity == "warning"]
            infos = [i for i in self.quality_issues if i.severity == "info"]

            if errors:
                lines.append("### Errors")
                lines.append("")
                for issue in errors:
                    col_info = f" (Column: `{issue.column}`)" if issue.column else ""
                    lines.append(f"- **{issue.issue_type}**{col_info}: {issue.description}")
                    lines.append(f"  - Recommendation: {issue.recommendation}")
                lines.append("")

            if warnings:
                lines.append("### Warnings")
                lines.append("")
                for issue in warnings:
                    col_info = f" (Column: `{issue.column}`)" if issue.column else ""
                    lines.append(f"- **{issue.issue_type}**{col_info}: {issue.description}")
                    lines.append(f"  - Recommendation: {issue.recommendation}")
                lines.append("")

            if infos:
                lines.append("### Information")
                lines.append("")
                for issue in infos:
                    col_info = f" (Column: `{issue.column}`)" if issue.column else ""
                    lines.append(f"- **{issue.issue_type}**{col_info}: {issue.description}")
                lines.append("")

        # Column Details section
        lines.extend([
            "## Column Details",
            "",
            "| Column | Type | Non-Null | Nulls (%) | Unique |",
            "|--------|------|----------|-----------|--------|",
        ])

        for col in self.columns:
            lines.append(
                f"| `{col.name}` | {col.dtype} | {col.non_null_count:,} | "
                f"{col.null_percentage:.1f}% | {col.unique_count:,} |"
            )

        lines.append("")

        # Detailed column profiles
        lines.extend([
            "## Column Statistics",
            "",
        ])

        for col in self.columns:
            lines.append(f"### {col.name}")
            lines.append("")
            lines.append(f"- **Type:** {col.dtype}")
            lines.append(f"- **Non-null:** {col.non_null_count:,} ({100 - col.null_percentage:.1f}%)")
            lines.append(f"- **Unique values:** {col.unique_count:,} ({col.unique_percentage:.1f}%)")

            if col.min_value is not None:
                lines.append(f"- **Min:** {col.min_value:,.2f}")
                lines.append(f"- **Max:** {col.max_value:,.2f}")
                lines.append(f"- **Mean:** {col.mean_value:,.2f}")
                lines.append(f"- **Median:** {col.median_value:,.2f}")
                lines.append(f"- **Std Dev:** {col.std_value:,.2f}")

            if col.min_length is not None:
                lines.append(f"- **Min Length:** {col.min_length}")
                lines.append(f"- **Max Length:** {col.max_length}")
                lines.append(f"- **Avg Length:** {col.avg_length:.1f}")

            if col.sample_values:
                sample_str = ", ".join(str(v) for v in col.sample_values[:5])
                lines.append(f"- **Sample values:** {sample_str}")

            lines.append("")

        return "\n".join(lines)

    def save_report(self, path: Union[str, Path]) -> Path:
        """
        Save the profile as a markdown report.

        Args:
            path: Output file path.

        Returns:
            Path to the saved file.
        """
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.to_markdown(), encoding="utf-8")
        logger.info(f"Profile report saved to {path}")
        return path


def _profile_column(series: "pd.Series", name: str) -> ColumnProfile:
    """Profile a single pandas Series."""
    total = len(series)
    non_null = series.count()
    null_count = total - non_null
    unique_count = series.nunique()

    profile = ColumnProfile(
        name=name,
        dtype=str(series.dtype),
        non_null_count=non_null,
        null_count=null_count,
        null_percentage=(null_count / total * 100) if total > 0 else 0,
        unique_count=unique_count,
        unique_percentage=(unique_count / non_null * 100) if non_null > 0 else 0,
        has_nulls=null_count > 0,
        is_constant=unique_count <= 1,
        possible_id=unique_count == non_null and non_null > 0,
    )

    # Get sample values
    try:
        profile.sample_values = series.dropna().head(5).tolist()
    except Exception:
        profile.sample_values = []

    # Numeric statistics
    if pd.api.types.is_numeric_dtype(series):
        try:
            profile.min_value = float(series.min())
            profile.max_value = float(series.max())
            profile.mean_value = float(series.mean())
            profile.median_value = float(series.median())
            profile.std_value = float(series.std())
        except Exception:
            pass

    # String statistics
    if pd.api.types.is_string_dtype(series) or series.dtype == "object":
        try:
            lengths = series.dropna().astype(str).str.len()
            if len(lengths) > 0:
                profile.min_length = int(lengths.min())
                profile.max_length = int(lengths.max())
                profile.avg_length = float(lengths.mean())
        except Exception:
            pass

    # Check for possible date column
    if "date" in name.lower() or "time" in name.lower():
        profile.possible_date = True

    return profile


def _detect_quality_issues(
    df: "pd.DataFrame",
    columns: List[ColumnProfile],
) -> List[DataQualityIssue]:
    """Detect data quality issues in the dataset."""
    issues: List[DataQualityIssue] = []

    # Dataset-level checks
    if len(df) == 0:
        issues.append(DataQualityIssue(
            severity="error",
            column=None,
            issue_type="Empty Dataset",
            description="The dataset contains no rows.",
            recommendation="Verify the data source and re-export.",
        ))
        return issues

    # Check for duplicate rows
    dup_count = df.duplicated().sum()
    if dup_count > 0:
        dup_pct = (dup_count / len(df)) * 100
        issues.append(DataQualityIssue(
            severity="warning" if dup_pct < 5 else "error",
            column=None,
            issue_type="Duplicate Rows",
            description=f"Found {dup_count:,} duplicate rows ({dup_pct:.1f}%).",
            recommendation="Review duplicates and deduplicate if appropriate.",
        ))

    # Column-level checks
    for col in columns:
        # High null percentage
        if col.null_percentage > 50:
            issues.append(DataQualityIssue(
                severity="warning",
                column=col.name,
                issue_type="High Null Rate",
                description=f"{col.null_percentage:.1f}% of values are null.",
                recommendation="Consider imputation or removal if not needed.",
            ))

        # Constant column
        if col.is_constant:
            issues.append(DataQualityIssue(
                severity="info",
                column=col.name,
                issue_type="Constant Value",
                description="Column contains only one unique value.",
                recommendation="May be removable if not needed for analysis.",
            ))

        # Possible ID column
        if col.possible_id and col.unique_count > 100:
            issues.append(DataQualityIssue(
                severity="info",
                column=col.name,
                issue_type="Possible ID Column",
                description="All values are unique - may be an identifier.",
                recommendation="Confirm if this is an ID field.",
            ))

        # High cardinality categorical
        if (col.dtype == "object" and
                col.unique_count > 100 and
                col.unique_percentage > 50):
            issues.append(DataQualityIssue(
                severity="warning",
                column=col.name,
                issue_type="High Cardinality",
                description=f"{col.unique_count:,} unique values in text column.",
                recommendation="May need binning or encoding for modeling.",
            ))

    return issues


def profile_dataset(
    file_path: Union[str, Path],
    sample_size: Optional[int] = None,
) -> DatasetProfile:
    """
    Profile a dataset file.

    Supports CSV, Excel (.xlsx, .xls), and Parquet files.

    Args:
        file_path: Path to the data file.
        sample_size: If provided, only profile this many rows.

    Returns:
        DatasetProfile with complete analysis.

    Raises:
        ImportError: If pandas is not installed.
        FileNotFoundError: If the file doesn't exist.
        ValueError: If the file format is not supported.
    """
    if pd is None:
        raise ImportError("pandas is required for data profiling. Install with: pip install pandas")

    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    # Load data based on file type
    suffix = file_path.suffix.lower()

    if suffix == ".csv":
        df = pd.read_csv(file_path, nrows=sample_size)
    elif suffix in {".xlsx", ".xls"}:
        df = pd.read_excel(file_path, nrows=sample_size)
    elif suffix == ".parquet":
        df = pd.read_parquet(file_path)
        if sample_size:
            df = df.head(sample_size)
    elif suffix == ".json":
        df = pd.read_json(file_path)
        if sample_size:
            df = df.head(sample_size)
    else:
        raise ValueError(f"Unsupported file format: {suffix}")

    # Profile each column
    columns = [_profile_column(df[col], col) for col in df.columns]

    # Detect quality issues
    quality_issues = _detect_quality_issues(df, columns)

    # Create profile
    profile = DatasetProfile(
        file_path=str(file_path),
        file_name=file_path.name,
        file_size_bytes=file_path.stat().st_size,
        row_count=len(df),
        column_count=len(df.columns),
        columns=columns,
        quality_issues=quality_issues,
        profiled_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    )

    logger.info(f"Profiled {file_path}: {profile.row_count:,} rows, {profile.column_count} columns")
    return profile


def compare_datasets(
    profile1: DatasetProfile,
    profile2: DatasetProfile,
) -> str:
    """
    Compare two dataset profiles and return a summary of differences.

    Args:
        profile1: First dataset profile.
        profile2: Second dataset profile.

    Returns:
        Markdown string describing differences.
    """
    lines = [
        "# Dataset Comparison",
        "",
        "| Metric | Dataset 1 | Dataset 2 |",
        "|--------|-----------|-----------|",
        f"| File | {profile1.file_name} | {profile2.file_name} |",
        f"| Rows | {profile1.row_count:,} | {profile2.row_count:,} |",
        f"| Columns | {profile1.column_count} | {profile2.column_count} |",
        "",
    ]

    # Column differences
    cols1 = {c.name for c in profile1.columns}
    cols2 = {c.name for c in profile2.columns}

    only_in_1 = cols1 - cols2
    only_in_2 = cols2 - cols1
    common = cols1 & cols2

    if only_in_1:
        lines.append(f"**Columns only in {profile1.file_name}:** {', '.join(sorted(only_in_1))}")
        lines.append("")

    if only_in_2:
        lines.append(f"**Columns only in {profile2.file_name}:** {', '.join(sorted(only_in_2))}")
        lines.append("")

    lines.append(f"**Common columns:** {len(common)}")

    return "\n".join(lines)


def main():
    """CLI entry point for data_profiler."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python core/data_profiler.py <file_path> [output_path]")
        sys.exit(1)

    file_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None

    try:
        profile = profile_dataset(file_path)
        print(profile.summary)
        print()

        if output_path:
            profile.save_report(output_path)
            print(f"Report saved to: {output_path}")
        else:
            print(profile.to_markdown())

    except Exception as e:
        print(f"Error profiling dataset: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
