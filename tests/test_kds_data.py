"""Tests for KDSData."""

import json
import pytest
import pandas as pd
from pathlib import Path

from core.kds_data import KDSData, KDSDataSourceConfig


@pytest.fixture
def sample_csv(tmp_path):
    """Create a sample CSV file for testing."""
    csv_path = tmp_path / "test.csv"
    csv_path.write_text(
        "id,category,value\n"
        "1,A,100\n"
        "2,B,200\n"
        "3,A,150\n"
    )
    return csv_path


@pytest.fixture
def sample_config(sample_csv):
    """Create sample data config."""
    return {
        "test_data": {
            "type": "csv",
            "path": str(sample_csv),
            "keys": ["id", "category"],
            "value_cols": ["value"],
        }
    }


class TestKDSDataSourceConfig:
    """Tests for KDSDataSourceConfig dataclass."""

    def test_config_creation(self):
        """Test basic config creation."""
        config = KDSDataSourceConfig(
            name="test",
            type="csv",
            path="/path/to/file.csv",
            keys=["id"],
            value_cols=["value"],
        )
        assert config.name == "test"
        assert config.type == "csv"
        assert config.sql is None

    def test_duckdb_requires_sql(self):
        """DuckDB config without SQL should raise."""
        with pytest.raises(ValueError, match="requires 'sql'"):
            KDSDataSourceConfig(
                name="test",
                type="duckdb",
                path="/path/to/db.duckdb",
                keys=["id"],
                value_cols=["value"],
                # Missing sql parameter
            )


class TestKDSData:
    """Tests for KDSData class."""

    def test_from_dict(self, sample_config):
        """Test creation from dictionary."""
        data = KDSData.from_dict(sample_config)
        assert "test_data" in data.list_sources()

    def test_query_csv(self, sample_config):
        """Test querying CSV data."""
        data = KDSData.from_dict(sample_config)
        df = data.query("test_data")

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 3
        assert list(df.columns) == ["id", "category", "value"]

    def test_query_returns_copy(self, sample_config):
        """Verify query returns a copy, not original."""
        data = KDSData.from_dict(sample_config)
        df1 = data.query("test_data")
        df2 = data.query("test_data")

        df1["value"] = 999
        assert df2["value"].iloc[0] != 999

    def test_query_unknown_source_raises(self, sample_config):
        """Unknown source should raise KeyError."""
        data = KDSData.from_dict(sample_config)

        with pytest.raises(KeyError, match="Unknown data source"):
            data.query("nonexistent")

    def test_column_validation(self, tmp_path):
        """Missing columns should raise ValueError."""
        csv_path = tmp_path / "bad.csv"
        csv_path.write_text("x,y\n1,2\n")

        config = {
            "bad_data": {
                "type": "csv",
                "path": str(csv_path),
                "keys": ["id"],  # Doesn't exist
                "value_cols": ["value"],  # Doesn't exist
            }
        }

        data = KDSData.from_dict(config)
        with pytest.raises(ValueError, match="missing expected columns"):
            data.query("bad_data")

    def test_snapshot_returns_json_serializable(self, sample_config):
        """Snapshot should be JSON-serializable."""
        data = KDSData.from_dict(sample_config)
        snapshot = data.snapshot()

        # Should be JSON-serializable
        json_str = json.dumps(snapshot)
        assert "test_data" in json_str

        # Structure check
        assert isinstance(snapshot, dict)
        assert isinstance(snapshot["test_data"], list)
        assert isinstance(snapshot["test_data"][0], dict)

    def test_get_schema(self, sample_config):
        """Test schema retrieval."""
        data = KDSData.from_dict(sample_config)
        schema = data.get_schema("test_data")

        assert "id" in schema
        assert "category" in schema
        assert "value" in schema

    def test_get_unique_values(self, sample_config):
        """Test unique value retrieval."""
        data = KDSData.from_dict(sample_config)
        values = data.get_unique_values("test_data", "category")

        assert sorted(values) == ["A", "B"]

    def test_get_unique_values_invalid_column(self, sample_config):
        """Invalid column should raise ValueError."""
        data = KDSData.from_dict(sample_config)

        with pytest.raises(ValueError, match="not found"):
            data.get_unique_values("test_data", "nonexistent")

    def test_get_summary_stats(self, sample_config):
        """Test summary statistics."""
        data = KDSData.from_dict(sample_config)
        stats = data.get_summary_stats("test_data")

        assert "value" in stats
        assert stats["value"]["sum"] == 450
        assert stats["value"]["count"] == 3

    def test_from_yaml(self, tmp_path, sample_csv):
        """Test loading from YAML file."""
        yaml_content = f"""
datasets:
  yaml_test:
    type: csv
    path: {sample_csv}
    keys: [id]
    value_cols: [value]
"""
        yaml_path = tmp_path / "spec.yaml"
        yaml_path.write_text(yaml_content)

        data = KDSData.from_yaml(yaml_path)
        assert "yaml_test" in data.list_sources()

    def test_file_not_found(self, tmp_path):
        """Missing file should raise FileNotFoundError."""
        config = {
            "missing": {
                "type": "csv",
                "path": str(tmp_path / "nonexistent.csv"),
                "keys": ["id"],
                "value_cols": ["value"],
            }
        }

        data = KDSData.from_dict(config)
        with pytest.raises(FileNotFoundError):
            data.query("missing")

    def test_list_sources(self, sample_config):
        """Test listing all sources."""
        data = KDSData.from_dict(sample_config)
        sources = data.list_sources()

        assert isinstance(sources, list)
        assert "test_data" in sources

    def test_context_manager(self, sample_config):
        """Test context manager usage."""
        with KDSData.from_dict(sample_config) as data:
            df = data.query("test_data")
            assert len(df) == 3

    def test_repr(self, sample_config):
        """Test string representation."""
        data = KDSData.from_dict(sample_config)
        repr_str = repr(data)

        assert "KDSData" in repr_str
        assert "test_data" in repr_str

    def test_export_for_powerbi(self, sample_config, tmp_path):
        """Test Power BI export."""
        data = KDSData.from_dict(sample_config)
        output_path = tmp_path / "powerbi.csv"

        result = data.export_for_powerbi("test_data", output_path)

        assert result.exists()
        # Power BI uses UTF-8 with BOM
        content = result.read_bytes()
        assert content.startswith(b'\xef\xbb\xbf')  # UTF-8 BOM

    def test_export_for_tableau(self, sample_config, tmp_path):
        """Test Tableau export."""
        data = KDSData.from_dict(sample_config)
        output_path = tmp_path / "tableau.csv"

        result = data.export_for_tableau("test_data", output_path)

        assert result.exists()


class TestKDSDataDuckDB:
    """Tests for DuckDB backend - skipped if duckdb not installed."""

    @pytest.fixture
    def duckdb_file(self, tmp_path):
        """Create a test DuckDB database."""
        try:
            import duckdb
        except ImportError:
            pytest.skip("duckdb not installed")

        db_path = tmp_path / "test.duckdb"
        conn = duckdb.connect(str(db_path))
        conn.execute("""
            CREATE TABLE sales (
                id INTEGER,
                region VARCHAR,
                revenue DOUBLE
            )
        """)
        conn.execute("""
            INSERT INTO sales VALUES
            (1, 'North', 100.0),
            (2, 'South', 200.0)
        """)
        conn.close()
        return db_path

    def test_query_duckdb(self, duckdb_file):
        """Test DuckDB query."""
        config = {
            "sales": {
                "type": "duckdb",
                "path": str(duckdb_file),
                "sql": "SELECT * FROM sales",
                "keys": ["id", "region"],
                "value_cols": ["revenue"],
            }
        }

        data = KDSData.from_dict(config)
        df = data.query("sales")

        assert len(df) == 2
        assert "region" in df.columns
