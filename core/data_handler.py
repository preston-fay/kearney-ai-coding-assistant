# core/data_handler.py
"""
Large file handling with DuckDB for Kearney AI Coding Assistant projects.

DuckDB provides:
- Efficient querying of large CSV/Parquet files without loading into memory
- SQL interface familiar to consultants
- Automatic schema detection
- Columnar storage for analytics workloads

Usage:
    from core.data_handler import ProjectDatabase, register_all_raw_files

    # Single file
    db = ProjectDatabase(Path("."))
    db.register_file("data/raw/sales.csv")
    df = db.query_df("SELECT region, SUM(amount) FROM sales GROUP BY region")

    # All raw files
    tables = register_all_raw_files(Path("."))
"""

from pathlib import Path
from typing import Optional, List, Dict, Any

# DuckDB is optional - gracefully handle if not installed
try:
    import duckdb
    DUCKDB_AVAILABLE = True
except ImportError:
    duckdb = None
    DUCKDB_AVAILABLE = False


# Size threshold for recommending DuckDB (50MB)
LARGE_FILE_THRESHOLD_MB = 50


class ProjectDatabase:
    """
    DuckDB-backed data handler for large file operations.

    Creates a project-local database for efficient data operations.
    """

    def __init__(self, project_path: Path):
        """
        Initialize database handler.

        Args:
            project_path: Root path of the KACA project
        """
        if not DUCKDB_AVAILABLE:
            raise ImportError(
                "DuckDB is not installed. Install with:\n"
                "  pip install duckdb\n"
                "Or use the bootstrap script:\n"
                "  Windows: bootstrap/setup_windows.bat\n"
                "  macOS: bootstrap/setup_mac.sh"
            )

        self.project_path = Path(project_path)
        self.db_path = self.project_path / "data" / "project.duckdb"
        self._conn = None

    @property
    def conn(self):
        """Lazy connection property."""
        if self._conn is None:
            self._conn = self.connect()
        return self._conn

    def connect(self) -> "duckdb.DuckDBPyConnection":
        """
        Get or create database connection.

        Returns:
            DuckDB connection object
        """
        if self._conn is not None:
            return self._conn

        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = duckdb.connect(str(self.db_path))
        return self._conn

    def close(self) -> None:
        """Close database connection."""
        if self._conn:
            self._conn.close()
            self._conn = None

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

    def register_file(
        self,
        file_path: Path,
        table_name: Optional[str] = None
    ) -> str:
        """
        Register a file as a queryable table.

        Supports: CSV, Parquet, JSON, Excel

        Args:
            file_path: Path to data file
            table_name: Optional table name (defaults to filename stem)

        Returns:
            Table name that was registered

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file type not supported
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"Data file not found: {file_path}")

        # Sanitize table name from filename
        if table_name is None:
            table_name = file_path.stem
            # Replace characters invalid for SQL identifiers
            table_name = table_name.replace("-", "_").replace(" ", "_")
            # Ensure starts with letter
            if table_name[0].isdigit():
                table_name = "t_" + table_name

        suffix = file_path.suffix.lower()

        # Use absolute path for file registration
        abs_path = str(file_path.resolve())

        if suffix == ".csv":
            self.conn.execute(f"""
                CREATE OR REPLACE TABLE {table_name} AS
                SELECT * FROM read_csv_auto('{abs_path}')
            """)
        elif suffix == ".parquet":
            self.conn.execute(f"""
                CREATE OR REPLACE TABLE {table_name} AS
                SELECT * FROM read_parquet('{abs_path}')
            """)
        elif suffix in [".xlsx", ".xls"]:
            # DuckDB Excel support via spatial extension
            try:
                self.conn.execute("INSTALL spatial; LOAD spatial;")
                self.conn.execute(f"""
                    CREATE OR REPLACE TABLE {table_name} AS
                    SELECT * FROM st_read('{abs_path}')
                """)
            except Exception as e:
                # Fallback: try httpfs extension for newer DuckDB
                try:
                    self.conn.execute("INSTALL httpfs; LOAD httpfs;")
                    self.conn.execute(f"""
                        CREATE OR REPLACE TABLE {table_name} AS
                        SELECT * FROM read_xlsx('{abs_path}')
                    """)
                except Exception:
                    raise ValueError(
                        f"Could not read Excel file: {e}\n"
                        "Try converting to CSV or Parquet first."
                    )
        elif suffix == ".json":
            self.conn.execute(f"""
                CREATE OR REPLACE TABLE {table_name} AS
                SELECT * FROM read_json_auto('{abs_path}')
            """)
        else:
            raise ValueError(
                f"Unsupported file type: {suffix}\n"
                "Supported: .csv, .parquet, .xlsx, .xls, .json"
            )

        return table_name

    def query(self, sql: str) -> "duckdb.DuckDBPyRelation":
        """
        Execute SQL query and return results.

        Args:
            sql: SQL query string

        Returns:
            DuckDB relation object
        """
        return self.conn.execute(sql)

    def query_df(self, sql: str):
        """
        Execute SQL query and return pandas DataFrame.

        Args:
            sql: SQL query string

        Returns:
            pandas DataFrame with query results
        """
        return self.query(sql).fetchdf()

    def query_list(self, sql: str) -> List[tuple]:
        """
        Execute SQL query and return list of tuples.

        Args:
            sql: SQL query string

        Returns:
            List of result tuples
        """
        return self.query(sql).fetchall()

    def list_tables(self) -> List[str]:
        """
        List all registered tables.

        Returns:
            List of table names
        """
        result = self.query("SHOW TABLES").fetchall()
        return [row[0] for row in result]

    def describe_table(self, table_name: str) -> Dict[str, Any]:
        """
        Get schema information for a table.

        Args:
            table_name: Name of table to describe

        Returns:
            Dict with table_name, row_count, and columns info
        """
        columns = self.query(f"DESCRIBE {table_name}").fetchdf()
        row_count = self.query(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]

        return {
            "table_name": table_name,
            "row_count": row_count,
            "columns": columns.to_dict(orient="records")
        }

    def profile_table(self, table_name: str) -> Dict[str, Any]:
        """
        Generate profile statistics for a table.

        Includes basic info plus summary statistics for all columns.

        Args:
            table_name: Name of table to profile

        Returns:
            Dict with table info and statistics
        """
        # Get basic info
        info = self.describe_table(table_name)

        # Get summary statistics
        try:
            stats = self.conn.execute(f"SUMMARIZE {table_name}").fetchdf()
            info["statistics"] = stats.to_dict(orient="records")
        except Exception:
            # SUMMARIZE might not be available in all DuckDB versions
            info["statistics"] = []

        return info

    def export_to_parquet(
        self,
        table_name: str,
        output_path: Optional[Path] = None
    ) -> Path:
        """
        Export table to Parquet format for efficient storage.

        Args:
            table_name: Name of table to export
            output_path: Optional output path (defaults to data/processed/)

        Returns:
            Path to created parquet file
        """
        if output_path is None:
            output_path = self.project_path / "data" / "processed" / f"{table_name}.parquet"

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        self.query(f"COPY {table_name} TO '{output_path}' (FORMAT PARQUET)")
        return output_path

    def export_to_csv(
        self,
        table_name: str,
        output_path: Optional[Path] = None
    ) -> Path:
        """
        Export table to CSV format.

        Args:
            table_name: Name of table to export
            output_path: Optional output path (defaults to data/processed/)

        Returns:
            Path to created CSV file
        """
        if output_path is None:
            output_path = self.project_path / "data" / "processed" / f"{table_name}.csv"

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        self.query(f"COPY {table_name} TO '{output_path}' (FORMAT CSV, HEADER)")
        return output_path

    def get_sample(self, table_name: str, n: int = 10) -> List[tuple]:
        """
        Get sample rows from a table.

        Args:
            table_name: Name of table
            n: Number of rows to sample

        Returns:
            List of sample rows
        """
        return self.query(f"SELECT * FROM {table_name} LIMIT {n}").fetchall()

    def execute_script(self, sql: str) -> None:
        """
        Execute multiple SQL statements.

        Args:
            sql: SQL script with multiple statements separated by semicolons
        """
        for statement in sql.split(";"):
            statement = statement.strip()
            if statement:
                self.conn.execute(statement)


def register_all_raw_files(project_path: Path) -> Dict[str, str]:
    """
    Register all files in data/raw/ as queryable tables.

    Args:
        project_path: Root path of KACA project

    Returns:
        Dict mapping file names to table names
    """
    db = ProjectDatabase(project_path)
    raw_dir = Path(project_path) / "data" / "raw"

    registered = {}
    supported_extensions = [".csv", ".parquet", ".xlsx", ".xls", ".json"]

    if raw_dir.exists():
        for file_path in raw_dir.iterdir():
            if file_path.suffix.lower() in supported_extensions:
                try:
                    table_name = db.register_file(file_path)
                    registered[file_path.name] = table_name
                    print(f"  Registered: {file_path.name} → {table_name}")
                except Exception as e:
                    print(f"  Failed to register {file_path.name}: {e}")

    return registered


def get_file_size_mb(file_path: Path) -> float:
    """
    Get file size in megabytes.

    Args:
        file_path: Path to file

    Returns:
        Size in MB
    """
    return Path(file_path).stat().st_size / (1024 * 1024)


def should_use_duckdb(file_path: Path) -> bool:
    """
    Determine if a file should be processed with DuckDB vs pandas.

    Files over 50MB should use DuckDB for memory efficiency.

    Args:
        file_path: Path to data file

    Returns:
        True if DuckDB is recommended
    """
    size_mb = get_file_size_mb(file_path)
    return size_mb >= LARGE_FILE_THRESHOLD_MB


def get_data_handler_recommendation(file_path: Path) -> str:
    """
    Get a recommendation for how to handle a data file.

    Args:
        file_path: Path to data file

    Returns:
        Recommendation string
    """
    file_path = Path(file_path)
    size_mb = get_file_size_mb(file_path)

    if size_mb < LARGE_FILE_THRESHOLD_MB:
        return f"File is {size_mb:.1f}MB - use pandas for direct loading"
    elif size_mb < 500:
        return (
            f"File is {size_mb:.1f}MB - use DuckDB:\n"
            f"  from core.data_handler import ProjectDatabase\n"
            f"  db = ProjectDatabase(Path('.'))\n"
            f"  db.register_file('{file_path}')"
        )
    else:
        return (
            f"File is {size_mb:.1f}MB - use DuckDB, avoid loading into memory:\n"
            f"  from core.data_handler import ProjectDatabase\n"
            f"  db = ProjectDatabase(Path('.'))\n"
            f"  db.register_file('{file_path}')\n"
            f"  # Query directly, don't use query_df() on full table\n"
            f"  result = db.query('SELECT col1, SUM(col2) FROM table GROUP BY col1')"
        )
