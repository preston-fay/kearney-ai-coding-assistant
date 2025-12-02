# tests/test_data_handler.py
"""Tests for core/data_handler.py"""

import json
import os
import pytest
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Check if duckdb is available
try:
    import duckdb
    DUCKDB_AVAILABLE = True
except ImportError:
    DUCKDB_AVAILABLE = False

from core.data_handler import (
    DUCKDB_AVAILABLE as MODULE_DUCKDB_AVAILABLE,
    LARGE_FILE_THRESHOLD_MB,
    get_file_size_mb,
    should_use_duckdb,
    get_data_handler_recommendation,
)

# Only import ProjectDatabase if DuckDB is available
if DUCKDB_AVAILABLE:
    from core.data_handler import (
        ProjectDatabase,
        register_all_raw_files,
    )


class TestDuckDBAvailability:
    """Tests for DuckDB availability detection."""

    def test_module_detects_duckdb(self):
        """Test that module correctly detects DuckDB availability."""
        assert MODULE_DUCKDB_AVAILABLE == DUCKDB_AVAILABLE


class TestFileSizeHelpers:
    """Tests for file size helper functions."""

    def test_get_file_size_mb(self, tmp_path):
        """Test getting file size in MB."""
        # Create a 1KB file
        test_file = tmp_path / "test.txt"
        test_file.write_bytes(b"x" * 1024)

        size = get_file_size_mb(test_file)
        assert size == pytest.approx(0.001, rel=0.1)  # ~0.001 MB

    def test_should_use_duckdb_small_file(self, tmp_path):
        """Test that small files don't need DuckDB."""
        test_file = tmp_path / "small.csv"
        test_file.write_text("col1,col2\n1,2\n3,4")

        assert should_use_duckdb(test_file) is False

    def test_large_file_threshold(self):
        """Test the large file threshold constant."""
        assert LARGE_FILE_THRESHOLD_MB == 50

    def test_get_recommendation_small_file(self, tmp_path):
        """Test recommendation for small files."""
        test_file = tmp_path / "small.csv"
        test_file.write_text("col1,col2\n1,2\n3,4")

        rec = get_data_handler_recommendation(test_file)
        assert "pandas" in rec


@pytest.mark.skipif(not DUCKDB_AVAILABLE, reason="DuckDB not installed")
class TestProjectDatabase:
    """Tests for ProjectDatabase class."""

    @pytest.fixture
    def project_dir(self, tmp_path):
        """Create a project directory structure."""
        (tmp_path / "data" / "raw").mkdir(parents=True)
        (tmp_path / "data" / "processed").mkdir(parents=True)
        return tmp_path

    @pytest.fixture
    def sample_csv(self, project_dir):
        """Create a sample CSV file."""
        csv_path = project_dir / "data" / "raw" / "sales.csv"
        csv_path.write_text("id,product,amount\n1,Widget,100\n2,Gadget,200\n3,Widget,150")
        return csv_path

    def test_database_init(self, project_dir):
        """Test database initialization."""
        db = ProjectDatabase(project_dir)
        assert db.project_path == project_dir
        assert db.db_path == project_dir / "data" / "project.duckdb"

    def test_connect_creates_db_file(self, project_dir):
        """Test that connect creates the database file."""
        db = ProjectDatabase(project_dir)
        db.connect()

        assert db.db_path.exists()
        db.close()

    def test_context_manager(self, project_dir):
        """Test database context manager."""
        with ProjectDatabase(project_dir) as db:
            db.query("SELECT 1")
        # Connection should be closed after context

    def test_register_csv_file(self, project_dir, sample_csv):
        """Test registering a CSV file."""
        with ProjectDatabase(project_dir) as db:
            table_name = db.register_file(sample_csv)

            assert table_name == "sales"
            assert "sales" in db.list_tables()

    def test_register_with_custom_name(self, project_dir, sample_csv):
        """Test registering with custom table name."""
        with ProjectDatabase(project_dir) as db:
            table_name = db.register_file(sample_csv, table_name="my_sales")

            assert table_name == "my_sales"
            assert "my_sales" in db.list_tables()

    def test_register_file_not_found(self, project_dir):
        """Test error when file doesn't exist."""
        db = ProjectDatabase(project_dir)

        with pytest.raises(FileNotFoundError):
            db.register_file(project_dir / "nonexistent.csv")

    def test_register_unsupported_file_type(self, project_dir):
        """Test error for unsupported file types."""
        txt_file = project_dir / "data" / "raw" / "notes.txt"
        txt_file.write_text("Some text")

        db = ProjectDatabase(project_dir)

        with pytest.raises(ValueError, match="Unsupported file type"):
            db.register_file(txt_file)

    def test_query_returns_results(self, project_dir, sample_csv):
        """Test executing a query."""
        with ProjectDatabase(project_dir) as db:
            db.register_file(sample_csv)
            result = db.query("SELECT COUNT(*) FROM sales").fetchone()

            assert result[0] == 3

    def test_query_df_returns_dataframe(self, project_dir, sample_csv):
        """Test query_df returns pandas DataFrame."""
        with ProjectDatabase(project_dir) as db:
            db.register_file(sample_csv)
            df = db.query_df("SELECT * FROM sales")

            assert len(df) == 3
            assert "product" in df.columns

    def test_query_list_returns_tuples(self, project_dir, sample_csv):
        """Test query_list returns list of tuples."""
        with ProjectDatabase(project_dir) as db:
            db.register_file(sample_csv)
            results = db.query_list("SELECT id, product FROM sales ORDER BY id")

            assert results[0] == (1, "Widget")
            assert len(results) == 3

    def test_list_tables(self, project_dir, sample_csv):
        """Test listing tables."""
        with ProjectDatabase(project_dir) as db:
            db.register_file(sample_csv)
            tables = db.list_tables()

            assert "sales" in tables

    def test_describe_table(self, project_dir, sample_csv):
        """Test describing a table."""
        with ProjectDatabase(project_dir) as db:
            db.register_file(sample_csv)
            info = db.describe_table("sales")

            assert info["table_name"] == "sales"
            assert info["row_count"] == 3
            assert len(info["columns"]) == 3

    def test_profile_table(self, project_dir, sample_csv):
        """Test profiling a table."""
        with ProjectDatabase(project_dir) as db:
            db.register_file(sample_csv)
            profile = db.profile_table("sales")

            assert profile["table_name"] == "sales"
            assert profile["row_count"] == 3

    def test_get_sample(self, project_dir, sample_csv):
        """Test getting sample rows."""
        with ProjectDatabase(project_dir) as db:
            db.register_file(sample_csv)
            sample = db.get_sample("sales", n=2)

            assert len(sample) == 2

    def test_export_to_parquet(self, project_dir, sample_csv):
        """Test exporting to parquet."""
        with ProjectDatabase(project_dir) as db:
            db.register_file(sample_csv)
            parquet_path = db.export_to_parquet("sales")

            assert parquet_path.exists()
            assert parquet_path.suffix == ".parquet"

    def test_export_to_csv(self, project_dir, sample_csv):
        """Test exporting to CSV."""
        with ProjectDatabase(project_dir) as db:
            db.register_file(sample_csv)
            csv_path = db.export_to_csv("sales")

            assert csv_path.exists()
            assert csv_path.suffix == ".csv"

    def test_export_to_custom_path(self, project_dir, sample_csv):
        """Test exporting to custom path."""
        custom_path = project_dir / "exports" / "custom_sales.parquet"

        with ProjectDatabase(project_dir) as db:
            db.register_file(sample_csv)
            result_path = db.export_to_parquet("sales", output_path=custom_path)

            assert result_path == custom_path
            assert custom_path.exists()


@pytest.mark.skipif(not DUCKDB_AVAILABLE, reason="DuckDB not installed")
class TestRegisterAllRawFiles:
    """Tests for register_all_raw_files function."""

    @pytest.fixture
    def project_with_files(self, tmp_path):
        """Create project with multiple data files."""
        raw_dir = tmp_path / "data" / "raw"
        raw_dir.mkdir(parents=True)

        # Create sample files
        (raw_dir / "sales.csv").write_text("id,amount\n1,100\n2,200")
        (raw_dir / "customers.csv").write_text("id,name\n1,Alice\n2,Bob")
        (raw_dir / ".gitkeep").touch()  # Should be ignored

        return tmp_path

    def test_registers_all_supported_files(self, project_with_files, capsys):
        """Test that all supported files are registered."""
        registered = register_all_raw_files(project_with_files)

        assert "sales.csv" in registered
        assert "customers.csv" in registered
        assert len(registered) == 2

    def test_ignores_unsupported_files(self, project_with_files):
        """Test that unsupported files are ignored."""
        # Add unsupported file
        txt_file = project_with_files / "data" / "raw" / "notes.txt"
        txt_file.write_text("Some notes")

        registered = register_all_raw_files(project_with_files)

        assert "notes.txt" not in registered

    def test_empty_raw_directory(self, tmp_path):
        """Test with empty raw directory."""
        raw_dir = tmp_path / "data" / "raw"
        raw_dir.mkdir(parents=True)

        registered = register_all_raw_files(tmp_path)

        assert len(registered) == 0


@pytest.mark.skipif(not DUCKDB_AVAILABLE, reason="DuckDB not installed")
class TestJSONSupport:
    """Tests for JSON file support."""

    @pytest.fixture
    def json_file(self, tmp_path):
        """Create a sample JSON file."""
        raw_dir = tmp_path / "data" / "raw"
        raw_dir.mkdir(parents=True)

        json_path = raw_dir / "data.json"
        data = [
            {"id": 1, "value": "a"},
            {"id": 2, "value": "b"},
        ]
        json_path.write_text(json.dumps(data))
        return json_path, tmp_path

    def test_register_json_file(self, json_file):
        """Test registering a JSON file."""
        json_path, project_dir = json_file

        with ProjectDatabase(project_dir) as db:
            table_name = db.register_file(json_path)
            count = db.query("SELECT COUNT(*) FROM data").fetchone()[0]

            assert table_name == "data"
            assert count == 2


@pytest.mark.skipif(not DUCKDB_AVAILABLE, reason="DuckDB not installed")
class TestParquetSupport:
    """Tests for Parquet file support."""

    @pytest.fixture
    def parquet_file(self, tmp_path):
        """Create a sample Parquet file if pyarrow is available."""
        try:
            import pandas as pd
            raw_dir = tmp_path / "data" / "raw"
            raw_dir.mkdir(parents=True)

            parquet_path = raw_dir / "data.parquet"
            df = pd.DataFrame({"id": [1, 2, 3], "value": ["a", "b", "c"]})
            df.to_parquet(parquet_path)
            return parquet_path, tmp_path
        except ImportError:
            pytest.skip("pandas/pyarrow not available for parquet test")

    def test_register_parquet_file(self, parquet_file):
        """Test registering a Parquet file."""
        parquet_path, project_dir = parquet_file

        with ProjectDatabase(project_dir) as db:
            table_name = db.register_file(parquet_path)
            count = db.query("SELECT COUNT(*) FROM data").fetchone()[0]

            assert table_name == "data"
            assert count == 3


@pytest.mark.skipif(not DUCKDB_AVAILABLE, reason="DuckDB not installed")
class TestTableNameSanitization:
    """Tests for table name sanitization."""

    @pytest.fixture
    def project_dir(self, tmp_path):
        """Create project directory."""
        (tmp_path / "data" / "raw").mkdir(parents=True)
        return tmp_path

    def test_hyphen_in_filename(self, project_dir):
        """Test filename with hyphens is sanitized."""
        csv_path = project_dir / "data" / "raw" / "sales-2024.csv"
        csv_path.write_text("id,value\n1,100")

        with ProjectDatabase(project_dir) as db:
            table_name = db.register_file(csv_path)
            assert table_name == "sales_2024"

    def test_space_in_filename(self, project_dir):
        """Test filename with spaces is sanitized."""
        csv_path = project_dir / "data" / "raw" / "sales data.csv"
        csv_path.write_text("id,value\n1,100")

        with ProjectDatabase(project_dir) as db:
            table_name = db.register_file(csv_path)
            assert table_name == "sales_data"

    def test_numeric_start_filename(self, project_dir):
        """Test filename starting with number is prefixed."""
        csv_path = project_dir / "data" / "raw" / "2024_sales.csv"
        csv_path.write_text("id,value\n1,100")

        with ProjectDatabase(project_dir) as db:
            table_name = db.register_file(csv_path)
            assert table_name == "t_2024_sales"


@pytest.mark.skipif(not DUCKDB_AVAILABLE, reason="DuckDB not installed")
class TestDatabasePersistence:
    """Tests for database persistence."""

    def test_database_persists_across_sessions(self, tmp_path):
        """Test that database data persists when reopened."""
        project_dir = tmp_path
        (project_dir / "data" / "raw").mkdir(parents=True)

        csv_path = project_dir / "data" / "raw" / "test.csv"
        csv_path.write_text("id,value\n1,100\n2,200")

        # First session: create and register
        with ProjectDatabase(project_dir) as db:
            db.register_file(csv_path)

        # Second session: should still have table
        with ProjectDatabase(project_dir) as db:
            tables = db.list_tables()
            assert "test" in tables

            count = db.query("SELECT COUNT(*) FROM test").fetchone()[0]
            assert count == 2
