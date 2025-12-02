"""Tests for core/data_profiler.py"""

import pytest
from pathlib import Path
import tempfile
import os

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False

from core.data_profiler import (
    profile_dataset,
    DatasetProfile,
    ColumnProfile,
    DataQualityIssue,
    compare_datasets,
)


pytestmark = pytest.mark.skipif(not HAS_PANDAS, reason="pandas not installed")


@pytest.fixture
def sample_csv(tmp_path):
    """Create a sample CSV file for testing."""
    csv_content = """name,age,salary,department
Alice,30,50000,Engineering
Bob,25,45000,Marketing
Charlie,35,60000,Engineering
Diana,28,52000,Sales
Eve,32,,Marketing
"""
    csv_path = tmp_path / "sample.csv"
    csv_path.write_text(csv_content)
    return csv_path


@pytest.fixture
def csv_with_duplicates(tmp_path):
    """Create a CSV with duplicate rows."""
    csv_content = """name,value
A,1
B,2
A,1
C,3
A,1
"""
    csv_path = tmp_path / "duplicates.csv"
    csv_path.write_text(csv_content)
    return csv_path


@pytest.fixture
def csv_with_high_nulls(tmp_path):
    """Create a CSV with high null percentage."""
    csv_content = """id,value,optional
1,100,
2,200,
3,300,
4,400,data
5,500,
"""
    csv_path = tmp_path / "high_nulls.csv"
    csv_path.write_text(csv_content)
    return csv_path


class TestProfileDataset:
    """Tests for profile_dataset function."""

    def test_profile_basic_csv(self, sample_csv):
        """Test profiling a basic CSV file."""
        profile = profile_dataset(sample_csv)

        assert profile.file_name == "sample.csv"
        assert profile.row_count == 5
        assert profile.column_count == 4

    def test_profile_column_types(self, sample_csv):
        """Test that column types are correctly identified."""
        profile = profile_dataset(sample_csv)

        col_names = [c.name for c in profile.columns]
        assert "name" in col_names
        assert "age" in col_names
        assert "salary" in col_names

    def test_profile_null_detection(self, sample_csv):
        """Test that nulls are correctly detected."""
        profile = profile_dataset(sample_csv)

        salary_col = next(c for c in profile.columns if c.name == "salary")
        assert salary_col.null_count == 1
        assert salary_col.has_nulls  # Use truthy check for numpy bool compatibility

    def test_profile_unique_counts(self, sample_csv):
        """Test that unique counts are calculated."""
        profile = profile_dataset(sample_csv)

        name_col = next(c for c in profile.columns if c.name == "name")
        assert name_col.unique_count == 5  # All unique

        dept_col = next(c for c in profile.columns if c.name == "department")
        assert dept_col.unique_count == 3  # Engineering, Marketing, Sales

    def test_profile_numeric_stats(self, sample_csv):
        """Test that numeric statistics are calculated."""
        profile = profile_dataset(sample_csv)

        age_col = next(c for c in profile.columns if c.name == "age")
        assert age_col.min_value is not None
        assert age_col.max_value is not None
        assert age_col.mean_value is not None

    def test_profile_nonexistent_file_raises(self):
        """Test that profiling nonexistent file raises error."""
        with pytest.raises(FileNotFoundError):
            profile_dataset(Path("/nonexistent/file.csv"))

    def test_profile_unsupported_format_raises(self, tmp_path):
        """Test that unsupported format raises error."""
        bad_file = tmp_path / "file.xyz"
        bad_file.write_text("data")

        with pytest.raises(ValueError, match="Unsupported file format"):
            profile_dataset(bad_file)


class TestDataQualityIssues:
    """Tests for data quality issue detection."""

    def test_detect_duplicate_rows(self, csv_with_duplicates):
        """Test detection of duplicate rows."""
        profile = profile_dataset(csv_with_duplicates)

        dup_issues = [i for i in profile.quality_issues
                      if i.issue_type == "Duplicate Rows"]
        assert len(dup_issues) == 1

    def test_detect_high_null_rate(self, csv_with_high_nulls):
        """Test detection of high null rate."""
        profile = profile_dataset(csv_with_high_nulls)

        null_issues = [i for i in profile.quality_issues
                       if i.issue_type == "High Null Rate"]
        # 'optional' column has 80% nulls
        assert len(null_issues) >= 1

    def test_detect_constant_column(self, tmp_path):
        """Test detection of constant value columns."""
        csv_content = """id,constant,value
1,X,100
2,X,200
3,X,300
"""
        csv_path = tmp_path / "constant.csv"
        csv_path.write_text(csv_content)

        profile = profile_dataset(csv_path)

        const_issues = [i for i in profile.quality_issues
                        if i.issue_type == "Constant Value"]
        assert len(const_issues) == 1

    def test_detect_possible_id(self, tmp_path):
        """Test detection of possible ID columns."""
        # Create CSV with more than 100 unique values to trigger possible_id detection
        rows = ["id,value"] + [f"ID{i:04d},{i}" for i in range(150)]
        csv_path = tmp_path / "ids.csv"
        csv_path.write_text("\n".join(rows))

        profile = profile_dataset(csv_path)

        id_issues = [i for i in profile.quality_issues
                     if i.issue_type == "Possible ID Column"]
        # 'id' column has all unique values and > 100 unique
        assert len(id_issues) >= 1


class TestDatasetProfile:
    """Tests for DatasetProfile class."""

    def test_summary_property(self, sample_csv):
        """Test the summary property."""
        profile = profile_dataset(sample_csv)
        summary = profile.summary

        assert "sample.csv" in summary
        assert "5" in summary  # row count
        assert "4" in summary  # column count

    def test_to_markdown(self, sample_csv):
        """Test markdown report generation."""
        profile = profile_dataset(sample_csv)
        markdown = profile.to_markdown()

        assert "# Data Profile: sample.csv" in markdown
        assert "## Overview" in markdown
        assert "## Column Details" in markdown

    def test_save_report(self, sample_csv, tmp_path):
        """Test saving report to file."""
        profile = profile_dataset(sample_csv)
        output_path = tmp_path / "report.md"

        result = profile.save_report(output_path)

        assert result == output_path
        assert output_path.exists()
        content = output_path.read_text()
        assert "# Data Profile:" in content


class TestColumnProfile:
    """Tests for ColumnProfile class."""

    def test_column_profile_creation(self):
        """Test creating a ColumnProfile."""
        col = ColumnProfile(
            name="test_column",
            dtype="int64",
            non_null_count=100,
            null_count=0,
            null_percentage=0.0,
            unique_count=50,
            unique_percentage=50.0,
        )
        assert col.name == "test_column"
        assert col.has_nulls is False

    def test_column_profile_with_stats(self):
        """Test ColumnProfile with numeric stats."""
        col = ColumnProfile(
            name="numeric_col",
            dtype="float64",
            non_null_count=100,
            null_count=0,
            null_percentage=0.0,
            unique_count=80,
            unique_percentage=80.0,
            min_value=0.0,
            max_value=100.0,
            mean_value=50.0,
            median_value=48.0,
            std_value=25.0,
        )
        assert col.min_value == 0.0
        assert col.max_value == 100.0


class TestDataQualityIssue:
    """Tests for DataQualityIssue class."""

    def test_quality_issue_creation(self):
        """Test creating a DataQualityIssue."""
        issue = DataQualityIssue(
            severity="warning",
            column="test_col",
            issue_type="High Null Rate",
            description="60% of values are null.",
            recommendation="Consider imputation.",
        )
        assert issue.severity == "warning"
        assert issue.column == "test_col"


class TestCompareDatasets:
    """Tests for compare_datasets function."""

    def test_compare_same_structure(self, sample_csv):
        """Test comparing datasets with same structure."""
        profile1 = profile_dataset(sample_csv)
        profile2 = profile_dataset(sample_csv)

        comparison = compare_datasets(profile1, profile2)

        assert "Dataset Comparison" in comparison
        assert "Common columns" in comparison

    def test_compare_different_columns(self, tmp_path):
        """Test comparing datasets with different columns."""
        csv1 = tmp_path / "data1.csv"
        csv1.write_text("a,b,c\n1,2,3\n")

        csv2 = tmp_path / "data2.csv"
        csv2.write_text("a,b,d\n1,2,4\n")

        profile1 = profile_dataset(csv1)
        profile2 = profile_dataset(csv2)

        comparison = compare_datasets(profile1, profile2)

        assert "only in" in comparison.lower()


class TestFormatSize:
    """Tests for file size formatting."""

    def test_format_bytes(self):
        """Test formatting bytes."""
        profile = DatasetProfile(
            file_path="test.csv",
            file_name="test.csv",
            file_size_bytes=500,
            row_count=10,
            column_count=3,
            columns=[],
        )
        assert "B" in profile._format_size(500)

    def test_format_kilobytes(self):
        """Test formatting kilobytes."""
        profile = DatasetProfile(
            file_path="test.csv",
            file_name="test.csv",
            file_size_bytes=5000,
            row_count=10,
            column_count=3,
            columns=[],
        )
        assert "KB" in profile._format_size(5000)

    def test_format_megabytes(self):
        """Test formatting megabytes."""
        profile = DatasetProfile(
            file_path="test.csv",
            file_name="test.csv",
            file_size_bytes=5000000,
            row_count=10,
            column_count=3,
            columns=[],
        )
        assert "MB" in profile._format_size(5000000)


class TestSampleSize:
    """Tests for sample size parameter."""

    def test_profile_with_sample_size(self, tmp_path):
        """Test profiling with sample size limit."""
        # Create larger CSV
        rows = ["name,value"] + [f"item{i},{i}" for i in range(100)]
        csv_path = tmp_path / "large.csv"
        csv_path.write_text("\n".join(rows))

        profile = profile_dataset(csv_path, sample_size=10)

        # Should only have 10 rows profiled
        assert profile.row_count == 10


class TestExcelSupport:
    """Tests for Excel file support."""

    def test_profile_xlsx_file(self, tmp_path):
        """Test profiling an Excel file."""
        try:
            import openpyxl
        except ImportError:
            pytest.skip("openpyxl not installed")

        # Create Excel file
        df = pd.DataFrame({
            "name": ["Alice", "Bob"],
            "value": [100, 200],
        })
        xlsx_path = tmp_path / "test.xlsx"
        df.to_excel(xlsx_path, index=False)

        profile = profile_dataset(xlsx_path)

        assert profile.row_count == 2
        assert profile.column_count == 2
