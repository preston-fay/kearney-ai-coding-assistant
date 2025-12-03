"""
Kearney Data Abstraction Layer

Provides a unified interface for loading data from CSV files and DuckDB databases.
Supports lazy loading, schema validation, and export to various BI formats.

Usage:
    from core.kds_data import KDSData

    # From dictionary config
    data = KDSData.from_dict({
        "sales": {
            "type": "csv",
            "path": "data/sales.csv",
            "keys": ["region", "product"],
            "value_cols": ["revenue", "units"]
        }
    })

    df = data.query("sales")
    snapshot = data.snapshot()  # JSON-serializable for embedding

DuckDB Recommendation:
    For datasets larger than 10MB, consider using DuckDB for better performance.
    DuckDB is optional - install with: pip install duckdb
"""

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Union

import pandas as pd
import yaml

logger = logging.getLogger(__name__)


# Size threshold for recommending DuckDB (10MB)
DUCKDB_RECOMMENDED_SIZE_MB = 10


@dataclass
class KDSDataSourceConfig:
    """Configuration for a single data source."""

    name: str
    type: Literal["csv", "duckdb"]
    path: str
    keys: List[str]
    value_cols: List[str]
    sql: Optional[str] = None

    def __post_init__(self):
        """Validate configuration after initialization."""
        if self.type == "duckdb" and not self.sql:
            raise ValueError(f"DuckDB source '{self.name}' requires 'sql' parameter")


class KDSData:
    """
    Unified data abstraction layer for KACA applications.

    Supports:
    - CSV files (via pandas)
    - DuckDB databases (optional, lazy import)

    Features:
    - Column validation on load
    - Lazy DuckDB connection handling
    - JSON-serializable snapshots for embedding
    - Schema introspection
    - Export to Power BI and Tableau formats
    """

    def __init__(self):
        """Initialize empty data container."""
        self._sources: Dict[str, KDSDataSourceConfig] = {}
        self._cache: Dict[str, pd.DataFrame] = {}
        self._duckdb_conn: Optional[Any] = None

    @classmethod
    def from_dict(cls, config: Dict[str, Dict]) -> "KDSData":
        """
        Create KDSData from dictionary configuration.

        Args:
            config: Dictionary mapping source names to configurations.
                    Each config must have: type, path, keys, value_cols
                    DuckDB configs also need: sql

        Returns:
            Configured KDSData instance

        Example:
            data = KDSData.from_dict({
                "sales": {
                    "type": "csv",
                    "path": "data/sales.csv",
                    "keys": ["region"],
                    "value_cols": ["revenue"]
                }
            })
        """
        instance = cls()

        for name, source_config in config.items():
            source = KDSDataSourceConfig(
                name=name,
                type=source_config.get("type", "csv"),
                path=source_config["path"],
                keys=source_config.get("keys", []),
                value_cols=source_config.get("value_cols", []),
                sql=source_config.get("sql"),
            )
            instance._sources[name] = source

            # Check file size and recommend DuckDB if appropriate
            instance._check_size_recommendation(source)

        return instance

    @classmethod
    def from_yaml(cls, path: Union[str, Path]) -> "KDSData":
        """
        Create KDSData from YAML file.

        The YAML file should have a 'datasets' key containing source definitions.

        Args:
            path: Path to YAML file

        Returns:
            Configured KDSData instance
        """
        path = Path(path)
        with open(path) as f:
            content = yaml.safe_load(f)

        # Handle both spec.yaml format and direct datasets format
        if "datasets" in content:
            datasets = content["datasets"]
        else:
            datasets = content

        return cls.from_dict(datasets)

    @classmethod
    def from_spec(cls, spec_path: Path = Path("project_state/spec.yaml")) -> "KDSData":
        """
        Create KDSData from KACA project specification.

        This is the primary method for loading data in KACA workflows.

        Args:
            spec_path: Path to spec.yaml (default: project_state/spec.yaml)

        Returns:
            Configured KDSData instance
        """
        return cls.from_yaml(spec_path)

    def _check_size_recommendation(self, source: KDSDataSourceConfig) -> None:
        """Check file size and log recommendation for DuckDB if appropriate."""
        if source.type != "csv":
            return

        path = Path(source.path)
        if not path.exists():
            return

        size_mb = path.stat().st_size / (1024 * 1024)
        if size_mb > DUCKDB_RECOMMENDED_SIZE_MB:
            logger.info(
                f"Data source '{source.name}' is {size_mb:.1f}MB. "
                f"Consider using DuckDB for better performance with large datasets. "
                f"Install with: pip install duckdb"
            )

    def _get_duckdb_conn(self):
        """Lazy import and connection for DuckDB."""
        if self._duckdb_conn is None:
            try:
                import duckdb
                self._duckdb_conn = duckdb.connect()
            except ImportError:
                raise ImportError(
                    "DuckDB is required for this data source. "
                    "Install with: pip install duckdb"
                )
        return self._duckdb_conn

    def _load_csv(self, source: KDSDataSourceConfig) -> pd.DataFrame:
        """Load data from CSV file."""
        path = Path(source.path)
        if not path.exists():
            raise FileNotFoundError(f"CSV file not found: {path}")

        df = pd.read_csv(path)
        self._validate_columns(df, source)
        return df

    def _load_duckdb(self, source: KDSDataSourceConfig) -> pd.DataFrame:
        """Load data from DuckDB database."""
        conn = self._get_duckdb_conn()

        # If path is a file, attach it
        path = Path(source.path)
        if path.exists() and path.suffix == ".duckdb":
            # Query from file
            import duckdb
            file_conn = duckdb.connect(str(path), read_only=True)
            df = file_conn.execute(source.sql).fetchdf()
            file_conn.close()
        else:
            # Execute SQL directly (assumes tables are already loaded)
            df = conn.execute(source.sql).fetchdf()

        self._validate_columns(df, source)
        return df

    def _validate_columns(self, df: pd.DataFrame, source: KDSDataSourceConfig) -> None:
        """Validate that expected columns exist in DataFrame."""
        expected = set(source.keys + source.value_cols)
        actual = set(df.columns)
        missing = expected - actual

        if missing:
            raise ValueError(
                f"Data source '{source.name}' missing expected columns: {missing}. "
                f"Available columns: {list(df.columns)}"
            )

    def list_sources(self) -> List[str]:
        """Return list of registered data source names."""
        return list(self._sources.keys())

    def query(self, name: str, use_cache: bool = True) -> pd.DataFrame:
        """
        Query a data source by name.

        Args:
            name: Name of the data source
            use_cache: If True, return cached data if available

        Returns:
            DataFrame with the data

        Raises:
            KeyError: If source name not found
            ValueError: If required columns are missing
            FileNotFoundError: If data file not found
        """
        if name not in self._sources:
            raise KeyError(
                f"Unknown data source: '{name}'. "
                f"Available sources: {self.list_sources()}"
            )

        if use_cache and name in self._cache:
            return self._cache[name].copy()

        source = self._sources[name]

        if source.type == "csv":
            df = self._load_csv(source)
        elif source.type == "duckdb":
            df = self._load_duckdb(source)
        else:
            raise ValueError(f"Unknown source type: {source.type}")

        self._cache[name] = df
        return df.copy()

    def snapshot(self) -> Dict[str, List[Dict]]:
        """
        Get JSON-serializable snapshot of all data sources.

        This is used for embedding data in static HTML dashboards.

        Returns:
            Dictionary mapping source names to list of row dictionaries
        """
        result = {}
        for name in self._sources:
            df = self.query(name)
            # Convert to list of dicts, handling various data types
            records = df.to_dict(orient="records")
            # Ensure JSON serializable
            for record in records:
                for key, value in record.items():
                    if pd.isna(value):
                        record[key] = None
                    elif hasattr(value, "item"):  # numpy types
                        record[key] = value.item()
            result[name] = records
        return result

    def get_schema(self, name: str) -> Dict[str, str]:
        """
        Get schema (column names and types) for a data source.

        Args:
            name: Name of the data source

        Returns:
            Dictionary mapping column names to dtype strings
        """
        df = self.query(name)
        return {col: str(df[col].dtype) for col in df.columns}

    def get_unique_values(self, name: str, column: str) -> List[Any]:
        """
        Get unique values for a column (useful for filter options).

        Args:
            name: Name of the data source
            column: Column name

        Returns:
            List of unique values (sorted if sortable)
        """
        df = self.query(name)
        if column not in df.columns:
            raise ValueError(
                f"Column '{column}' not found in '{name}'. "
                f"Available: {list(df.columns)}"
            )

        values = df[column].dropna().unique().tolist()
        try:
            return sorted(values)
        except TypeError:
            return values

    def get_summary_stats(self, name: str) -> Dict[str, Dict]:
        """
        Get summary statistics for numeric columns.

        Args:
            name: Name of the data source

        Returns:
            Dictionary with stats for each numeric column
        """
        df = self.query(name)
        numeric_cols = df.select_dtypes(include=["number"]).columns

        stats = {}
        for col in numeric_cols:
            stats[col] = {
                "min": float(df[col].min()),
                "max": float(df[col].max()),
                "mean": float(df[col].mean()),
                "sum": float(df[col].sum()),
                "count": int(df[col].count()),
            }
        return stats

    def export_for_powerbi(self, name: str, output_path: Union[str, Path]) -> Path:
        """
        Export data source for Power BI consumption.

        Exports as CSV with proper formatting for Power BI.

        Args:
            name: Name of the data source
            output_path: Output file path

        Returns:
            Path to exported file
        """
        df = self.query(name)
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Power BI prefers UTF-8 with BOM
        df.to_csv(output_path, index=False, encoding="utf-8-sig")
        logger.info(f"Exported '{name}' for Power BI: {output_path}")
        return output_path

    def export_for_tableau(self, name: str, output_path: Union[str, Path]) -> Path:
        """
        Export data source for Tableau consumption.

        Exports as CSV (Tableau Hyper format would require tableauhyperapi).

        Args:
            name: Name of the data source
            output_path: Output file path

        Returns:
            Path to exported file
        """
        df = self.query(name)
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Standard CSV for Tableau
        df.to_csv(output_path, index=False)
        logger.info(f"Exported '{name}' for Tableau: {output_path}")
        return output_path

    def close(self) -> None:
        """Clean up cached connections and data."""
        self._cache.clear()
        if self._duckdb_conn is not None:
            self._duckdb_conn.close()
            self._duckdb_conn = None

    def __enter__(self) -> "KDSData":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit - clean up resources."""
        self.close()

    def __repr__(self) -> str:
        """String representation."""
        sources = ", ".join(self.list_sources())
        return f"KDSData(sources=[{sources}])"
