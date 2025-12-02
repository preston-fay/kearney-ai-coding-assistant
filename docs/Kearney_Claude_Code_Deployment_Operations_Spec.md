# Kearney AI Coding Assistant

## Deployment and Operations Specification

**Project Scaffolding, Data Architecture, Collaboration, and Enterprise Integration**

*Template as Factory. Projects as Products. Users Protected.*

---

# I. Document Purpose and Relationship

This specification extends the Master Plan v2.0 and Living Requirements Addendum with deployment, operations, and enterprise integration guidance.

## Document Hierarchy

| Document | Purpose |
|----------|---------|
| Master Plan v2.0 | Core architecture, engine, agents, commands |
| Living Requirements Addendum | Interview system, spec.yaml, versioning |
| **This Document** | Deployment, scaffolding, data, collaboration, operations |

## Implementation Priority

| Priority | Scope |
|----------|-------|
| **v1.0 (Launch)** | Scaffolding, prerequisites, data handling, error recovery, QC, basic branding |
| **v1.1 (Fast Follow)** | Update mechanism, session compaction, hybrid projects, audit logging |
| **v2.0 (Future)** | Collaboration, cloud data platforms, SharePoint publishing, telemetry |

---

# II. Deployment Model

## 2.1 Core Principle: Template as Factory

The Kearney AI Coding Assistant is a **template factory**, not a workspace. Users never work inside the template repository. They create projects FROM the template, then work inside those projects.

```
┌─────────────────────────────────────────────────────────────────┐
│                         TEMPLATE                                │
│                  (GitHub Repository)                            │
│                                                                 │
│   Protected. Read-only to users. Updated by D&A admins.        │
│                                                                 │
│   ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐           │
│   │  core/  │  │ config/ │  │ .claude/│  │  docs/  │           │
│   └─────────┘  └─────────┘  └─────────┘  └─────────┘           │
│                                                                 │
│                      scaffold.py                                │
│                          │                                      │
└──────────────────────────│──────────────────────────────────────┘
                           │
                           ▼ Creates
┌─────────────────────────────────────────────────────────────────┐
│                      USER PROJECT                               │
│              (Local Directory or OneDrive)                      │
│                                                                 │
│   User's workspace. All changes happen here.                    │
│                                                                 │
│   ┌─────────────────┐  ┌─────────────────┐                     │
│   │ project_state/  │  │     data/       │                     │
│   │  spec.yaml      │  │  raw/           │                     │
│   │  plan.md        │  │  processed/     │                     │
│   │  status.json    │  │                 │                     │
│   └─────────────────┘  └─────────────────┘                     │
│                                                                 │
│   ┌─────────────────┐  ┌─────────────────┐                     │
│   │    outputs/     │  │    exports/     │  ← Final            │
│   │  charts/        │  │  client-ready   │    deliverables     │
│   │  reports/       │  │  files here     │                     │
│   └─────────────────┘  └─────────────────┘                     │
│                                                                 │
│   core/ ──────────► symlink to template                        │
│   config/ ────────► symlink to template                        │
│   .claude/ ───────► COPIED (can customize per-project)         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## 2.2 Template Home Options

### Option A: GitHub (Recommended for v1)

**Location**: Kearney internal GitHub instance  
**URL Pattern**: `https://github.kearney.com/digital-analytics/kearney-ai-coding-assistant`

**Advantages**:
- Version control built-in
- Easy updates via git pull
- Collaboration-ready infrastructure
- Standard for technical users

**Workflow**:
```bash
# One-time clone
git clone https://github.kearney.com/digital-analytics/kearney-ai-coding-assistant.git ~/kaca-template

# Create project
python ~/kaca-template/scaffold.py my-project --path ~/Projects/

# Update template (when new version released)
cd ~/kaca-template && git pull
```

### Option B: OneDrive/SharePoint (Future - v2.0)

**Location**: Shared D&A OneDrive folder  
**Path Pattern**: `OneDrive - Kearney/Shared/D&A Tools/Kearney AI Coding Assistant/`

**Advantages**:
- Familiar to non-technical consultants
- Auto-sync without git knowledge
- IT-managed distribution

**Challenges**:
- No version control (would need VERSION file checking)
- Sync conflicts possible
- Slower for large updates

**Recommendation**: Start with GitHub for v1. Add OneDrive distribution for v2 if adoption requires it for non-technical users.

## 2.3 Project Location Options

Users can create projects in several locations:

| Location | Pros | Cons | Recommendation |
|----------|------|------|----------------|
| Local (`~/Projects/`) | Fast, offline-capable | Not backed up, not shareable | Good for prototyping |
| OneDrive (`~/OneDrive/Projects/`) | Backed up, accessible anywhere | Sync latency, file locking | Good for solo projects |
| SharePoint (via sync) | Team accessible, backed up | More complex setup | Good for team projects |

**Default Recommendation**: `~/OneDrive - Kearney/Projects/Claude/{project-name}/`

This provides cloud backup while keeping local performance.

---

# III. Prerequisites and Setup

## 3.1 Required Software

| Software | Version | Purpose | Installation Source |
|----------|---------|---------|---------------------|
| Python | 3.10+ | Core engine execution | Kearney Software Center |
| Claude Desktop | Latest | AI interface | Anthropic (Enterprise license) |
| Git | 2.30+ | Template management | Kearney Software Center |
| VS Code (optional) | Latest | Code viewing/editing | Kearney Software Center |

## 3.2 Required Licenses

| License | Type | Obtained From |
|---------|------|---------------|
| Claude Enterprise | Per-user | D&A Leadership (provisioned) |
| GitHub Enterprise | Per-user | IT (auto-provisioned with Kearney account) |

## 3.3 Prerequisite Checker Script

The scaffold script MUST check prerequisites before creating a project.

```python
# core/prereq_checker.py
"""
Prerequisite checker for Kearney AI Coding Assistant.
Run before project scaffolding to ensure environment is ready.
"""

import sys
import shutil
import subprocess
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional, Tuple


@dataclass
class CheckResult:
    name: str
    passed: bool
    message: str
    fix_instructions: Optional[str] = None


def check_python_version() -> CheckResult:
    """Check Python version is 3.10+."""
    version = sys.version_info
    passed = version.major == 3 and version.minor >= 10
    
    if passed:
        return CheckResult(
            name="Python Version",
            passed=True,
            message=f"Python {version.major}.{version.minor}.{version.micro} ✓"
        )
    else:
        return CheckResult(
            name="Python Version",
            passed=False,
            message=f"Python {version.major}.{version.minor} found, need 3.10+",
            fix_instructions=(
                "Install Python 3.10+ from Kearney Software Center:\n"
                "  1. Open Software Center\n"
                "  2. Search for 'Python'\n"
                "  3. Install Python 3.11 or later\n"
                "  4. Restart your terminal"
            )
        )


def check_git_installed() -> CheckResult:
    """Check Git is installed."""
    git_path = shutil.which("git")
    
    if git_path:
        try:
            result = subprocess.run(
                ["git", "--version"],
                capture_output=True,
                text=True
            )
            version = result.stdout.strip()
            return CheckResult(
                name="Git",
                passed=True,
                message=f"{version} ✓"
            )
        except Exception:
            pass
    
    return CheckResult(
        name="Git",
        passed=False,
        message="Git not found",
        fix_instructions=(
            "Install Git from Kearney Software Center:\n"
            "  1. Open Software Center\n"
            "  2. Search for 'Git'\n"
            "  3. Install Git for Windows\n"
            "  4. Restart your terminal"
        )
    )


def check_claude_desktop() -> CheckResult:
    """Check Claude Desktop is installed."""
    # Check common installation paths
    possible_paths = [
        Path.home() / "AppData/Local/Programs/Claude/Claude.exe",  # Windows
        Path("/Applications/Claude.app"),  # macOS
        Path.home() / ".local/share/Claude/claude"  # Linux
    ]
    
    found = any(p.exists() for p in possible_paths)
    
    if found:
        return CheckResult(
            name="Claude Desktop",
            passed=True,
            message="Claude Desktop installed ✓"
        )
    else:
        return CheckResult(
            name="Claude Desktop",
            passed=False,
            message="Claude Desktop not found",
            fix_instructions=(
                "Install Claude Desktop:\n"
                "  1. Request access from D&A Leadership\n"
                "  2. Once approved, download from claude.ai/download\n"
                "  3. Install and sign in with your Kearney credentials"
            )
        )


def check_required_packages() -> CheckResult:
    """Check required Python packages are available."""
    required = ["pandas", "matplotlib", "pptx", "yaml", "PIL"]
    missing = []
    
    for package in required:
        try:
            __import__(package if package != "PIL" else "PIL")
        except ImportError:
            missing.append(package)
    
    if not missing:
        return CheckResult(
            name="Python Packages",
            passed=True,
            message="All required packages installed ✓"
        )
    else:
        return CheckResult(
            name="Python Packages",
            passed=False,
            message=f"Missing packages: {', '.join(missing)}",
            fix_instructions=(
                "Run the bootstrap script to install packages:\n"
                "  Windows: Double-click bootstrap/setup_windows.bat\n"
                "  macOS:   Run ./bootstrap/setup_mac.sh"
            )
        )


def check_template_version(template_path: Path) -> CheckResult:
    """Check template is present and get version."""
    version_file = template_path / "VERSION"
    
    if not template_path.exists():
        return CheckResult(
            name="Template",
            passed=False,
            message=f"Template not found at {template_path}",
            fix_instructions=(
                "Clone the template repository:\n"
                "  git clone https://github.kearney.com/digital-analytics/kearney-ai-coding-assistant.git ~/kaca-template"
            )
        )
    
    if version_file.exists():
        version = version_file.read_text().strip()
        return CheckResult(
            name="Template",
            passed=True,
            message=f"Template v{version} ✓"
        )
    else:
        return CheckResult(
            name="Template",
            passed=True,
            message="Template found (version unknown)"
        )


def run_all_checks(template_path: Path) -> Tuple[bool, List[CheckResult]]:
    """Run all prerequisite checks."""
    checks = [
        check_python_version(),
        check_git_installed(),
        check_claude_desktop(),
        check_required_packages(),
        check_template_version(template_path),
    ]
    
    all_passed = all(c.passed for c in checks)
    return all_passed, checks


def print_results(results: List[CheckResult]) -> None:
    """Print check results in a readable format."""
    print("\n" + "=" * 60)
    print("  KEARNEY AI CODING ASSISTANT - PREREQUISITE CHECK")
    print("=" * 60 + "\n")
    
    for result in results:
        status = "✓" if result.passed else "✗"
        print(f"  [{status}] {result.name}: {result.message}")
    
    print("\n" + "-" * 60)
    
    failed = [r for r in results if not r.passed]
    if failed:
        print("\n  ACTION REQUIRED:\n")
        for result in failed:
            print(f"  {result.name}:")
            if result.fix_instructions:
                for line in result.fix_instructions.split("\n"):
                    print(f"    {line}")
            print()
    else:
        print("\n  All checks passed! Ready to create projects.\n")


if __name__ == "__main__":
    template_path = Path(__file__).parent.parent
    all_passed, results = run_all_checks(template_path)
    print_results(results)
    sys.exit(0 if all_passed else 1)
```

## 3.4 Scaffold Script with Prerequisite Integration

```python
# scaffold.py
"""
Project scaffolding for Kearney AI Coding Assistant.

Creates a new project from the template with proper structure,
symlinks to shared infrastructure, and user-specific directories.

Usage:
  python scaffold.py <project-name>
  python scaffold.py <project-name> --path ~/Projects/
  python scaffold.py <project-name> --no-symlinks  # Copy instead of symlink
"""

import argparse
import shutil
import sys
import os
from pathlib import Path
from datetime import datetime

# Import prereq checker
from core.prereq_checker import run_all_checks, print_results

TEMPLATE_ROOT = Path(__file__).parent.resolve()


def create_symlink_or_copy(src: Path, dst: Path, use_symlinks: bool) -> None:
    """Create symlink on Unix, junction on Windows, or copy if requested."""
    if not use_symlinks:
        if src.is_dir():
            shutil.copytree(src, dst)
        else:
            shutil.copy2(src, dst)
        return
    
    if sys.platform == "win32":
        # Windows: Use junction for directories (no admin required)
        if src.is_dir():
            import subprocess
            subprocess.run(
                ["cmd", "/c", "mklink", "/J", str(dst), str(src)],
                check=True,
                capture_output=True
            )
        else:
            # For files, just copy on Windows
            shutil.copy2(src, dst)
    else:
        # Unix: Use symlinks
        dst.symlink_to(src)


def scaffold_project(
    name: str,
    target_dir: Path,
    use_symlinks: bool = True
) -> Path:
    """
    Create a new project from the template.
    
    Args:
        name: Project name (used for folder name)
        target_dir: Parent directory for the project
        use_symlinks: If True, symlink shared dirs. If False, copy everything.
    
    Returns:
        Path to created project
    """
    project_path = target_dir / name
    
    # Check if project already exists
    if project_path.exists():
        raise FileExistsError(
            f"Project already exists: {project_path}\n"
            f"Choose a different name or delete the existing project."
        )
    
    print(f"\nCreating project: {project_path}\n")
    
    # Create project root
    project_path.mkdir(parents=True)
    
    # === FILES TO COPY (user can customize) ===
    print("  Copying customizable files...")
    
    # CLAUDE.md - user might need to customize
    shutil.copy(TEMPLATE_ROOT / "CLAUDE.md", project_path / "CLAUDE.md")
    
    # .claude/ directory - agents and commands (user might customize)
    shutil.copytree(TEMPLATE_ROOT / ".claude", project_path / ".claude")
    
    # README with project-specific info
    readme_content = f"""# {name}

Created: {datetime.now().strftime("%Y-%m-%d")}
Template Version: {(TEMPLATE_ROOT / "VERSION").read_text().strip() if (TEMPLATE_ROOT / "VERSION").exists() else "unknown"}

## Quick Start

1. Open this folder in Claude Desktop
2. Type `/interview` to define your project
3. Type `/plan` to generate execution plan
4. Type `/execute` to start building

## Project Structure

- `project_state/` - Your project spec, plan, and status
- `data/raw/` - Place source data files here
- `data/processed/` - Cleaned/transformed data
- `outputs/` - Generated charts and reports
- `exports/` - Final client-ready deliverables

## Commands

| Command | Purpose |
|---------|---------|
| `/interview` | Define project requirements |
| `/plan` | Generate execution plan |
| `/execute` | Execute next task |
| `/status` | Show progress |
| `/review` | Check brand compliance |
| `/export` | Create final deliverables |
| `/help` | Show all commands |
"""
    (project_path / "README.md").write_text(readme_content)
    
    # === SHARED INFRASTRUCTURE (symlink or copy) ===
    print("  Linking shared infrastructure...")
    
    shared_dirs = ["core", "config", "bootstrap"]
    for dirname in shared_dirs:
        src = TEMPLATE_ROOT / dirname
        dst = project_path / dirname
        if src.exists():
            create_symlink_or_copy(src, dst, use_symlinks)
            link_type = "Linked" if use_symlinks else "Copied"
            print(f"    {link_type}: {dirname}/")
    
    # === USER DIRECTORIES (create empty) ===
    print("  Creating project directories...")
    
    user_dirs = [
        "project_state",
        "project_state/spec_history",
        "project_state/logs",
        "data/raw",
        "data/processed",
        "data/external",
        "outputs/charts",
        "outputs/reports",
        "exports",
    ]
    
    for dirname in user_dirs:
        (project_path / dirname).mkdir(parents=True, exist_ok=True)
        print(f"    Created: {dirname}/")
    
    # === GITIGNORE (protect sensitive data) ===
    print("  Creating .gitignore...")
    
    gitignore_content = """# Kearney AI Coding Assistant Project - Git Ignore

# === DATA (Never commit client data) ===
data/raw/*
data/processed/*
data/external/*
!data/raw/.gitkeep
!data/processed/.gitkeep
!data/external/.gitkeep

# Large files
*.csv
*.xlsx
*.xls
*.parquet
*.db
*.duckdb
*.sqlite

# === SENSITIVE FILES ===
*.env
.env.*
secrets/
credentials/

# === OUTPUTS (Regenerable) ===
outputs/charts/*
outputs/reports/*
!outputs/charts/.gitkeep
!outputs/reports/.gitkeep

# === EXPORTS (May contain client data) ===
exports/*
!exports/.gitkeep

# === SYSTEM ===
__pycache__/
*.pyc
.DS_Store
Thumbs.db
*.log
.venv/
venv/

# === SYMLINKS (Don't commit template links) ===
core
config
bootstrap
"""
    (project_path / ".gitignore").write_text(gitignore_content)
    
    # Create .gitkeep files for empty directories
    for dirname in ["data/raw", "data/processed", "data/external", 
                    "outputs/charts", "outputs/reports", "exports"]:
        (project_path / dirname / ".gitkeep").touch()
    
    # === VERSION TRACKING ===
    template_version = "unknown"
    if (TEMPLATE_ROOT / "VERSION").exists():
        template_version = (TEMPLATE_ROOT / "VERSION").read_text().strip()
    
    version_info = {
        "template_version": template_version,
        "created_at": datetime.now().isoformat(),
        "template_path": str(TEMPLATE_ROOT),
        "symlinks_used": use_symlinks
    }
    
    import json
    (project_path / ".kaca-version.json").write_text(
        json.dumps(version_info, indent=2)
    )
    
    return project_path


def main():
    parser = argparse.ArgumentParser(
        description="Create a new Kearney AI Coding Assistant project"
    )
    parser.add_argument(
        "name",
        help="Project name (will be used as folder name)"
    )
    parser.add_argument(
        "--path",
        default=".",
        help="Parent directory for the project (default: current directory)"
    )
    parser.add_argument(
        "--no-symlinks",
        action="store_true",
        help="Copy shared files instead of symlinking (for offline/portable use)"
    )
    parser.add_argument(
        "--skip-checks",
        action="store_true",
        help="Skip prerequisite checks (not recommended)"
    )
    
    args = parser.parse_args()
    
    # Run prerequisite checks
    if not args.skip_checks:
        print("\nChecking prerequisites...")
        all_passed, results = run_all_checks(TEMPLATE_ROOT)
        print_results(results)
        
        if not all_passed:
            print("Please resolve the issues above before creating a project.")
            sys.exit(1)
    
    # Create project
    try:
        project_path = scaffold_project(
            name=args.name,
            target_dir=Path(args.path).resolve(),
            use_symlinks=not args.no_symlinks
        )
        
        print("\n" + "=" * 60)
        print("  PROJECT CREATED SUCCESSFULLY")
        print("=" * 60)
        print(f"""
  Location: {project_path}

  Next steps:
    1. cd {project_path}
    2. Open this folder in Claude Desktop (File → Open Folder)
    3. Type: /interview

  Happy building!
""")
        
    except FileExistsError as e:
        print(f"\nError: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nError creating project: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
```

---

# IV. Data Architecture

## 4.1 Data Directory Structure

```
data/
├── raw/                    # Original source files (NEVER modify)
│   ├── .gitkeep
│   ├── sales_2024.csv
│   └── customer_data.xlsx
│
├── processed/              # Cleaned, transformed data
│   ├── .gitkeep
│   ├── sales_clean.parquet
│   └── customer_features.parquet
│
└── external/               # Reference data, lookups
    ├── .gitkeep
    ├── region_mapping.csv
    └── industry_codes.csv
```

## 4.2 Large File Handling

Client data often includes large files (100MB+) that cannot be efficiently handled by standard file operations. The kit provides DuckDB integration for these cases.

### DuckDB Integration

```python
# core/data_handler.py
"""
Large file handling with DuckDB for Kearney AI Coding Assistant projects.

DuckDB provides:
- Efficient querying of large CSV/Parquet files without loading into memory
- SQL interface familiar to consultants
- Automatic schema detection
- Columnar storage for analytics workloads
"""

import duckdb
from pathlib import Path
from typing import Optional, List, Dict, Any
import json


class ProjectDatabase:
    """
    DuckDB-backed data handler for large file operations.
    
    Creates a project-local database for efficient data operations.
    """
    
    def __init__(self, project_path: Path):
        self.project_path = Path(project_path)
        self.db_path = self.project_path / "data" / "project.duckdb"
        self.conn = None
    
    def connect(self) -> duckdb.DuckDBPyConnection:
        """Get or create database connection."""
        if self.conn is None:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            self.conn = duckdb.connect(str(self.db_path))
        return self.conn
    
    def close(self) -> None:
        """Close database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None
    
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
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"Data file not found: {file_path}")
        
        table_name = table_name or file_path.stem.replace("-", "_").replace(" ", "_")
        conn = self.connect()
        
        suffix = file_path.suffix.lower()
        
        if suffix == ".csv":
            conn.execute(f"""
                CREATE OR REPLACE TABLE {table_name} AS 
                SELECT * FROM read_csv_auto('{file_path}')
            """)
        elif suffix == ".parquet":
            conn.execute(f"""
                CREATE OR REPLACE TABLE {table_name} AS 
                SELECT * FROM read_parquet('{file_path}')
            """)
        elif suffix in [".xlsx", ".xls"]:
            # DuckDB Excel support via spatial extension
            conn.execute("INSTALL spatial; LOAD spatial;")
            conn.execute(f"""
                CREATE OR REPLACE TABLE {table_name} AS 
                SELECT * FROM st_read('{file_path}')
            """)
        elif suffix == ".json":
            conn.execute(f"""
                CREATE OR REPLACE TABLE {table_name} AS 
                SELECT * FROM read_json_auto('{file_path}')
            """)
        else:
            raise ValueError(f"Unsupported file type: {suffix}")
        
        return table_name
    
    def query(self, sql: str) -> duckdb.DuckDBPyRelation:
        """Execute SQL query and return results."""
        return self.connect().execute(sql)
    
    def query_df(self, sql: str):
        """Execute SQL query and return pandas DataFrame."""
        return self.query(sql).fetchdf()
    
    def list_tables(self) -> List[str]:
        """List all registered tables."""
        result = self.query("SHOW TABLES").fetchall()
        return [row[0] for row in result]
    
    def describe_table(self, table_name: str) -> Dict[str, Any]:
        """Get schema information for a table."""
        columns = self.query(f"DESCRIBE {table_name}").fetchdf()
        row_count = self.query(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
        
        return {
            "table_name": table_name,
            "row_count": row_count,
            "columns": columns.to_dict(orient="records")
        }
    
    def profile_table(self, table_name: str) -> Dict[str, Any]:
        """Generate profile statistics for a table."""
        conn = self.connect()
        
        # Get basic info
        info = self.describe_table(table_name)
        
        # Get summary statistics
        stats = conn.execute(f"SUMMARIZE {table_name}").fetchdf()
        
        info["statistics"] = stats.to_dict(orient="records")
        return info
    
    def export_to_parquet(
        self,
        table_name: str,
        output_path: Optional[Path] = None
    ) -> Path:
        """Export table to Parquet format for efficient storage."""
        if output_path is None:
            output_path = self.project_path / "data" / "processed" / f"{table_name}.parquet"
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.query(f"COPY {table_name} TO '{output_path}' (FORMAT PARQUET)")
        return output_path


def register_all_raw_files(project_path: Path) -> Dict[str, str]:
    """
    Register all files in data/raw/ as queryable tables.
    
    Returns:
        Dict mapping file names to table names
    """
    db = ProjectDatabase(project_path)
    raw_dir = project_path / "data" / "raw"
    
    registered = {}
    
    if raw_dir.exists():
        for file_path in raw_dir.iterdir():
            if file_path.suffix.lower() in [".csv", ".parquet", ".xlsx", ".xls", ".json"]:
                try:
                    table_name = db.register_file(file_path)
                    registered[file_path.name] = table_name
                    print(f"  Registered: {file_path.name} → {table_name}")
                except Exception as e:
                    print(f"  Failed to register {file_path.name}: {e}")
    
    return registered
```

### Usage in spec.yaml

When the interview engine gathers data information, it can reference DuckDB tables:

```yaml
# project_state/spec.yaml (data section)
data:
  sources:
    - name: sales_2024.csv
      type: csv
      location: data/raw/sales_2024.csv
      duckdb_table: sales_2024
      rows: 1250000
      size_mb: 450
      
    - name: customer_data.xlsx
      type: excel
      location: data/raw/customer_data.xlsx
      duckdb_table: customer_data
      rows: 50000
      
  database: data/project.duckdb
  
  quality_notes:
    - Large file (450MB) - using DuckDB for queries
    - Some null values in region column
```

## 4.3 Cloud Data Platform Integration (v2.0+)

Future versions will support direct connections to enterprise data platforms:

```yaml
# config/data_connections.yaml (Future)
connections:
  snowflake:
    account: kearney.us-east-1
    warehouse: ANALYTICS_WH
    database: CLIENT_DATA
    schema: PUBLIC
    auth: sso  # Use Kearney SSO
    
  azure:
    storage_account: kearneydata
    container: client-projects
    auth: managed_identity
    
  bigquery:
    project: kearney-analytics
    dataset: client_data
    auth: service_account
```

## 4.4 Data Guidance for CLAUDE.md

Add to CLAUDE.md:

```markdown
## DATA HANDLING RULES

### File Size Guidelines
- Files < 50MB: Load directly with pandas
- Files 50-500MB: Use DuckDB via core/data_handler.py
- Files > 500MB: Query in DuckDB, never load fully into memory

### Data Location Rules
- Raw data: data/raw/ (NEVER modify these files)
- Processed data: data/processed/ (cleaned, transformed)
- External references: data/external/ (lookups, mappings)

### Data Security
- NEVER commit data files to git (enforced by .gitignore)
- NEVER include raw data in outputs or exports
- Aggregated/anonymized data only in deliverables

### DuckDB Usage
When working with large files:
```python
from core.data_handler import ProjectDatabase

db = ProjectDatabase(Path("."))
db.register_file("data/raw/large_file.csv")
result = db.query_df("SELECT region, SUM(sales) FROM large_file GROUP BY region")
```
```

---

# V. Project Management and Claude Projects Integration

## 5.1 Leveraging Claude Projects

Claude Desktop has a "Projects" feature that maintains context across conversations. Each Kearney AI Coding Assistant project SHOULD be a Claude Project.

### How Claude Projects Work
- A Claude Project is a named container in Claude Desktop
- It maintains conversation history and context
- Files opened in the project are remembered
- Custom instructions can be added

### Integration Approach

When a user scaffolds a project and opens it in Claude Desktop:

1. **First Open**: Claude reads CLAUDE.md and recognizes this as a KACA project
2. **Project Detection**: Check for `.kaca-version.json` to confirm KACA project
3. **Context Loading**: Automatically load `project_state/spec.yaml` and `project_state/status.json`
4. **Continuity**: User can close and reopen; state persists in files

### CLAUDE.md Startup Behavior (Updated)

```markdown
## STARTUP BEHAVIOR

When a session starts in this project:

1. **Detect KACA Project**
   - Check for .kaca-version.json
   - If missing, this is not a KACA project - inform user
   
2. **Check Template Version**
   - Read .kaca-version.json
   - Compare template_version to current expectations
   - If outdated, suggest: "Your project was created with template v{old}. 
     Current version is v{new}. Run /project:update for new features."

3. **Load Project State**
   - If project_state/spec.yaml exists:
     - Load spec.yaml
     - Load status.json
     - Report: "Welcome back to {project_name}. You're on {current_phase}. 
       {n}/{total} tasks complete. Next: {next_task}"
   - If spec.yaml does NOT exist:
     - Report: "This project hasn't been set up yet. 
       Type /interview to define your project."

4. **Offer Quick Actions**
   - If project in progress: "Type /execute to continue, 
     or /status for details."
   - If project complete: "Project complete! Type /export 
     to generate final deliverables."
```

## 5.2 Multi-Project Workflow

Consultants often work on multiple projects. The recommended workflow:

### Switching Projects

```
# In Claude Desktop:
# File → Open Folder → Select different project folder

# Claude will automatically:
# 1. Load that project's CLAUDE.md
# 2. Read that project's spec.yaml and status.json
# 3. Context is now that project
```

### Project Registry (Future Enhancement)

For v2.0, consider a `/kaca:projects` command that lists all KACA projects:

```markdown
# .claude/commands/projects.md (Future)

## /kaca:projects

List all Kearney AI Coding Assistant projects on this machine.

Searches:
- ~/Projects/
- ~/OneDrive - Kearney/Projects/
- Custom paths in ~/.kaca-config.json

Output:
```
Your KACA Projects:
┌─────────────────────────────────────────────────────────────┐
│  Project              │ Status     │ Last Updated          │
├───────────────────────┼────────────┼───────────────────────┤
│  acme-churn-model     │ In Progress│ 2025-12-01 14:30      │
│  beta-corp-dashboard  │ Complete   │ 2025-11-28 16:45      │
│  gamma-inc-proposal   │ Not Started│ 2025-12-01 09:00      │
└─────────────────────────────────────────────────────────────┘

Open a project: File → Open Folder → [path]
```
```

---

# VI. Collaboration Model (v2.0+)

## 6.1 Git-Based Collaboration

For team projects, use Git for collaboration:

### Repository Setup

```bash
# Team lead creates project
python ~/kaca-template/scaffold.py client-engagement --path ~/Projects/

# Initialize git (optional - for collaboration)
cd ~/Projects/client-engagement
git init
git add .
git commit -m "Initial project setup"

# Create remote (on Kearney GitHub or Azure DevOps)
git remote add origin https://github.kearney.com/projects/client-engagement.git
git push -u origin main
```

### Team Member Workflow

```bash
# Clone the project
git clone https://github.kearney.com/projects/client-engagement.git
cd client-engagement

# Before starting work
git pull

# After completing work
git add .
git commit -m "Completed Phase 2 analysis"
git push
```

## 6.2 Merge Conflict Handling

### Files That May Conflict

| File | Conflict Risk | Resolution Strategy |
|------|---------------|---------------------|
| spec.yaml | Medium | Version control handles; human review |
| plan.md | Low | Regenerate from spec if conflict |
| status.json | High | Take version with more progress; reconcile tasks |
| outputs/* | None | Each user outputs to own machine |

### status.json Conflict Resolution

```python
# core/conflict_resolver.py (Future)
"""
Merge conflict resolution for status.json.

Strategy: Take the union of completed tasks from both versions.
If same task has different status, take the more "advanced" status.
"""

STATUS_PRIORITY = {
    "pending": 0,
    "in_progress": 1,
    "done": 2,
    "blocked": 1  # Same as in_progress
}

def merge_status_files(ours: dict, theirs: dict) -> dict:
    """Merge two status.json files, preserving maximum progress."""
    merged = ours.copy()
    
    # Create task lookup
    our_tasks = {t["id"]: t for t in ours.get("tasks", [])}
    their_tasks = {t["id"]: t for t in theirs.get("tasks", [])}
    
    # Merge tasks
    all_task_ids = set(our_tasks.keys()) | set(their_tasks.keys())
    merged_tasks = []
    
    for task_id in sorted(all_task_ids):
        our_task = our_tasks.get(task_id)
        their_task = their_tasks.get(task_id)
        
        if our_task and their_task:
            # Both have the task - take higher priority status
            our_priority = STATUS_PRIORITY.get(our_task["status"], 0)
            their_priority = STATUS_PRIORITY.get(their_task["status"], 0)
            
            if their_priority > our_priority:
                merged_tasks.append(their_task)
            else:
                merged_tasks.append(our_task)
        else:
            # Only one has the task
            merged_tasks.append(our_task or their_task)
    
    merged["tasks"] = merged_tasks
    
    # Merge artifacts (union)
    our_artifacts = set(ours.get("artifacts", []))
    their_artifacts = set(theirs.get("artifacts", []))
    merged["artifacts"] = list(our_artifacts | their_artifacts)
    
    # Merge history (union, sorted by timestamp)
    all_history = ours.get("history", []) + theirs.get("history", [])
    seen = set()
    unique_history = []
    for entry in sorted(all_history, key=lambda x: x.get("timestamp", "")):
        key = (entry.get("action"), entry.get("timestamp"))
        if key not in seen:
            seen.add(key)
            unique_history.append(entry)
    merged["history"] = unique_history
    
    return merged
```

### Collaboration Guidelines (for docs/)

```markdown
# docs/COLLABORATION_GUIDE.md

## Working on Team Projects

### Before You Start Each Session
1. Pull latest changes: `git pull`
2. Open project in Claude Desktop
3. Check /status for current state

### While Working
- Communicate with teammates about who's doing what
- Commit frequently with clear messages
- Push when you complete a logical unit of work

### Handling Conflicts
If git reports a merge conflict:

1. **spec.yaml conflict**: Review both versions, combine requirements
2. **status.json conflict**: Run `python core/conflict_resolver.py` to auto-merge
3. **plan.md conflict**: Regenerate with /plan after resolving spec

### Best Practice: Divide by Phase
- Assign different phases to different team members
- Avoid two people working on same phase simultaneously
```

---

# VII. Session Management

## 7.1 Session Compaction

Long Claude sessions can exhaust context windows. The kit provides compaction to manage this.

### /project:compact Command

```markdown
# .claude/commands/compact.md

---
name: compact
description: Summarize and archive old context to free up space
agent: @router
---

# /project:compact

## Purpose

When a session runs long, context fills up. This command:
1. Summarizes completed work
2. Archives detailed logs
3. Resets to a clean state with full project awareness

## Behavior

1. **Generate Summary**
   - List all completed tasks with brief outcomes
   - Note key decisions made
   - Capture any blockers or issues

2. **Archive to Logs**
   - Write detailed session log to project_state/logs/session_{timestamp}.md
   - Include all outputs generated
   - Include any errors or warnings

3. **Reset Context**
   - Keep only: spec.yaml, status.json, current task context
   - Drop: Detailed conversation history, intermediate outputs

4. **Confirm**
   - Report: "Session compacted. {n} tasks summarized. Context freed.
     You're on task {current_task}. Type /execute to continue."

## When to Use

- When Claude mentions context is getting long
- When responses start getting slower
- Before starting a new phase
- At natural break points

## Automatic Trigger

If context exceeds 80% capacity, Claude should suggest:
"We've been working for a while. Run /project:compact to 
summarize progress and free up context?"
```

### Session Log Format

```markdown
# project_state/logs/session_2025-12-01_143022.md

## Session Summary

**Date**: 2025-12-01 14:30 - 16:45
**Duration**: 2h 15m
**Tasks Completed**: 3

## Work Completed

### Task 2.1: Revenue by Region Chart
- Created bar chart showing Q4 revenue by region
- Top region: Northeast ($4.2M)
- Output: outputs/charts/revenue_by_region.png

### Task 2.2: YoY Comparison
- Built comparison chart (2023 vs 2024)
- Key finding: 12% overall growth
- Output: outputs/charts/yoy_comparison.png

### Task 2.3: Executive Summary
- Drafted 1-page summary of findings
- Output: outputs/reports/exec_summary.md

## Decisions Made

- Client prefers bar charts over pie charts
- Excluded APAC region (incomplete data)

## Issues Encountered

- Initial chart had wrong date range (fixed)
- Brand check caught gridlines (removed)

## Next Up

- Task 3.1: Build recommendation slide deck
```

## 7.2 Context Management in CLAUDE.md

Add to CLAUDE.md:

```markdown
## CONTEXT MANAGEMENT

### Monitoring
Track approximate context usage. When nearing limits:
- Suggest /project:compact
- Summarize completed work
- Focus on current task only

### What to Keep in Context
- Current task details
- Relevant spec.yaml sections
- Recent outputs for reference
- Active error/issue state

### What to Drop
- Completed task details (archived in logs)
- Full conversation history
- Superseded outputs
- Resolved issues

### Recovery from Context Loss
If context is lost mid-session:
1. Read project_state/status.json
2. Read most recent log in project_state/logs/
3. Resume from current_task
4. Inform user: "Session was reset. Resuming from {task}."
```

---

# VIII. Error Recovery

## 8.1 Recovery Commands

### /project:reset

```markdown
# .claude/commands/reset.md

---
name: reset
description: Archive current state and start fresh
agent: @router
---

# /project:reset

## Purpose

When a project needs to start over:
- Major requirements change
- Corrupted state files
- "Let's try a different approach"

## Behavior

1. **Confirm Intent**
   - "This will archive your current project state and start fresh.
     Your data files will NOT be deleted.
     Current progress: {n}/{total} tasks complete.
     Are you sure? Type 'yes' to confirm."

2. **Archive Current State**
   - Create project_state/archive/{timestamp}/
   - Move spec.yaml, plan.md, status.json to archive
   - Move spec_history/ contents to archive
   - Log the reset action

3. **Reset State**
   - Create fresh project_state/ directory
   - Clear status (but keep outputs/)
   - Keep data/ intact

4. **Offer Next Steps**
   - "Project reset complete. Previous state archived.
     Type /interview to define your new approach."

## Archive Structure

project_state/
├── archive/
│   └── 2025-12-01_143022/
│       ├── spec.yaml
│       ├── plan.md
│       ├── status.json
│       ├── spec_history/
│       └── reset_reason.txt
├── spec.yaml (empty/new)
└── ...
```

### /project:rollback

```markdown
# .claude/commands/rollback.md

---
name: rollback
description: Restore project state from archive or history
agent: @spec-editor
---

# /project:rollback

## Usage

/project:rollback spec 3        # Rollback spec to version 3
/project:rollback archive       # List available archives
/project:rollback archive 2     # Restore from archive #2

## Spec Version Rollback

1. List available versions from spec_history/
2. Show diff between current and target version
3. Confirm with user
4. Replace spec.yaml with historical version
5. Increment version number (so history is preserved)
6. Suggest regenerating plan

## Archive Rollback

1. List available archives with dates and status
2. Show what will be restored
3. Confirm with user
4. Archive CURRENT state first (safety)
5. Restore files from selected archive
6. Report restored state
```

## 8.2 State Validation

```python
# core/state_validator.py
"""
Validate project state files for consistency and corruption.
"""

import json
import yaml
from pathlib import Path
from typing import List, Tuple


def validate_spec(spec_path: Path) -> Tuple[bool, List[str]]:
    """Validate spec.yaml structure and required fields."""
    issues = []
    
    if not spec_path.exists():
        return False, ["spec.yaml not found"]
    
    try:
        spec = yaml.safe_load(spec_path.read_text())
    except yaml.YAMLError as e:
        return False, [f"Invalid YAML: {e}"]
    
    # Check required fields
    required = ["version", "meta", "problem"]
    for field in required:
        if field not in spec:
            issues.append(f"Missing required field: {field}")
    
    # Check meta fields
    if "meta" in spec:
        meta_required = ["project_name", "project_type"]
        for field in meta_required:
            if field not in spec["meta"]:
                issues.append(f"Missing meta field: {field}")
    
    return len(issues) == 0, issues


def validate_status(status_path: Path) -> Tuple[bool, List[str]]:
    """Validate status.json structure."""
    issues = []
    
    if not status_path.exists():
        return False, ["status.json not found"]
    
    try:
        status = json.loads(status_path.read_text())
    except json.JSONDecodeError as e:
        return False, [f"Invalid JSON: {e}"]
    
    # Check required fields
    required = ["project_name", "tasks"]
    for field in required:
        if field not in status:
            issues.append(f"Missing required field: {field}")
    
    # Check task structure
    if "tasks" in status:
        for i, task in enumerate(status["tasks"]):
            if "id" not in task:
                issues.append(f"Task {i} missing 'id'")
            if "status" not in task:
                issues.append(f"Task {i} missing 'status'")
    
    return len(issues) == 0, issues


def validate_project_state(project_path: Path) -> Tuple[bool, dict]:
    """
    Full validation of project state.
    
    Returns:
        Tuple of (all_valid, results_dict)
    """
    state_dir = project_path / "project_state"
    
    results = {
        "spec": {"valid": False, "issues": []},
        "status": {"valid": False, "issues": []},
        "overall": False
    }
    
    # Validate spec
    spec_valid, spec_issues = validate_spec(state_dir / "spec.yaml")
    results["spec"]["valid"] = spec_valid
    results["spec"]["issues"] = spec_issues
    
    # Validate status
    status_valid, status_issues = validate_status(state_dir / "status.json")
    results["status"]["valid"] = status_valid
    results["status"]["issues"] = status_issues
    
    results["overall"] = spec_valid and status_valid
    
    return results["overall"], results


def attempt_repair(project_path: Path) -> List[str]:
    """
    Attempt to repair common state issues.
    
    Returns:
        List of repairs made
    """
    repairs = []
    state_dir = project_path / "project_state"
    
    # Repair: Create missing directories
    for subdir in ["spec_history", "logs"]:
        dir_path = state_dir / subdir
        if not dir_path.exists():
            dir_path.mkdir(parents=True)
            repairs.append(f"Created missing directory: {subdir}/")
    
    # Repair: Initialize empty status.json if missing but spec exists
    status_path = state_dir / "status.json"
    spec_path = state_dir / "spec.yaml"
    
    if spec_path.exists() and not status_path.exists():
        spec = yaml.safe_load(spec_path.read_text())
        
        initial_status = {
            "project_name": spec.get("meta", {}).get("project_name", "unknown"),
            "template": spec.get("meta", {}).get("project_type", "unknown"),
            "created_at": spec.get("created_at", ""),
            "updated_at": spec.get("updated_at", ""),
            "current_phase": "",
            "current_task": None,
            "tasks": [],
            "artifacts": [],
            "history": [{"action": "status_repaired", "timestamp": ""}]
        }
        
        status_path.write_text(json.dumps(initial_status, indent=2))
        repairs.append("Created status.json from spec.yaml")
    
    return repairs
```

---

# IX. Quality Control

## 9.1 Automated QC Pipeline

The kit provides extensive automated checking at multiple points:

### QC Checkpoints

| Checkpoint | Trigger | Checks Performed |
|------------|---------|------------------|
| Post-Edit | Every file write | Brand colors, fonts, gridlines, emojis |
| Pre-Export | /export | All outputs, data labels, chart formatting |
| Pre-Commit | git commit | All outputs + exports, state validity |
| On-Demand | /review | Comprehensive review with report |

### QC Report Format

```markdown
# outputs/reports/qc_report.md

## Quality Control Report

**Generated**: 2025-12-01 15:30:00
**Project**: acme-churn-model
**Status**: ⚠️ 2 WARNINGS

### Brand Compliance

| Check | Status | Details |
|-------|--------|---------|
| Colors | ✓ Pass | All colors within KDS palette |
| Typography | ✓ Pass | Inter font used throughout |
| Gridlines | ✓ Pass | No gridlines detected |
| Emojis | ✓ Pass | No emojis detected |

### Chart Quality

| File | Status | Issues |
|------|--------|--------|
| revenue_by_region.png | ✓ Pass | - |
| yoy_comparison.png | ⚠️ Warning | Data labels overlap |

### Data Compliance

| Check | Status | Details |
|-------|--------|---------|
| PII Detection | ✓ Pass | No PII found in outputs |
| Raw Data Exposure | ✓ Pass | No raw data in exports |

### Recommendations

1. Adjust data label positioning in yoy_comparison.png to prevent overlap
2. Consider adding chart titles for accessibility

---

*This report was generated automatically by Kearney AI Coding Assistant QC.*
*User is responsible for final review before client delivery.*
```

## 9.2 Human Approval Requirements

Add to export deliverables:

```markdown
# .claude/commands/export.md (addition)

## Human Approval Warning

Before generating exports, display:

```
╔═══════════════════════════════════════════════════════════════╗
║                    HUMAN REVIEW REQUIRED                      ║
╠═══════════════════════════════════════════════════════════════╣
║  These deliverables will be generated:                        ║
║                                                               ║
║  • executive_summary.pptx (12 slides)                         ║
║  • model_documentation.docx (8 pages)                         ║
║  • scoring_script.py                                          ║
║                                                               ║
║  ⚠️  YOU are responsible for reviewing these outputs          ║
║      before sending to the client.                            ║
║                                                               ║
║  Automated checks passed, but human judgment required for:    ║
║  • Content accuracy                                           ║
║  • Appropriate messaging                                      ║
║  • Client-specific sensitivities                              ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
```

After export, include reminder:

```
Exports created in: exports/

BEFORE SENDING TO CLIENT:
□ Review all content for accuracy
□ Check messaging aligns with client expectations
□ Verify no sensitive data exposed
□ Confirm brand compliance

Your signature: _____________ Date: _____________
```
```

---

# X. Branding System

## 10.1 Default Kearney Branding

Defined in `config/governance/brand.yaml` (see Master Plan v2.0).

## 10.2 Custom Brand Override

Projects can override branding for client-branded deliverables:

### Project-Level Override

```yaml
# config/brand_override.yaml (optional, per-project)

# This file overrides default Kearney branding for this project.
# Delete this file to revert to Kearney defaults.

enabled: true

brand_name: "Acme Corporation"

colors:
  primary: "#0066CC"  # Acme Blue
  secondary: "#FF6600"  # Acme Orange
  background:
    dark: "#1A1A2E"
    light: "#FFFFFF"
  
  forbidden:
    - "#FF0000"  # Competitor red

typography:
  primary: "Helvetica Neue"
  fallback: "Helvetica"
  weights: [400, 700]

charts:
  gridlines: false  # Still enforce no gridlines
  default_colors:
    - "#0066CC"
    - "#FF6600"
    - "#333333"

logo:
  path: "config/assets/acme_logo.png"
  placement: "top-right"

# Still enforced regardless of override:
enforced:
  - no_emojis
  - no_gridlines
  - data_labels_outside
```

### brand_guard.py Update

```python
# core/brand_guard.py (addition)

def load_brand_config(project_path: Path) -> dict:
    """
    Load brand configuration with override support.
    
    Priority:
    1. config/brand_override.yaml (if exists)
    2. config/governance/brand.yaml (default)
    """
    override_path = project_path / "config" / "brand_override.yaml"
    default_path = project_path / "config" / "governance" / "brand.yaml"
    
    # Load default
    if default_path.exists():
        default_config = yaml.safe_load(default_path.read_text())
    else:
        default_config = {}
    
    # Check for override
    if override_path.exists():
        override_config = yaml.safe_load(override_path.read_text())
        
        if override_config.get("enabled", False):
            # Merge: override takes precedence, but enforced rules remain
            merged = {**default_config, **override_config}
            
            # Always enforce certain rules
            enforced = override_config.get("enforced", [
                "no_emojis", "no_gridlines", "data_labels_outside"
            ])
            merged["enforced"] = enforced
            
            return merged
    
    return default_config
```

---

# XI. Telemetry and Usage Tracking (v2.0+)

## 11.1 Privacy-First Approach

Telemetry is OPTIONAL and privacy-respecting:

- No client data captured
- No conversation content
- Only: command usage, project types, completion rates

### Opt-In Configuration

```yaml
# ~/.kaca-config.yaml (user's home directory)

telemetry:
  enabled: false  # User must explicitly opt in
  
  # If enabled, what to share:
  share:
    - command_usage  # Which commands used
    - project_types  # Analytics, presentation, etc.
    - completion_rates  # % of projects completed
    
  # Never share:
  never:
    - project_names
    - client_names
    - file_contents
    - conversation_history
```

## 11.2 Local Analytics

For v1, track locally per-user:

```json
// ~/.kaca-stats.json

{
  "user_id": "anonymous-hash",
  "first_use": "2025-11-01",
  "last_use": "2025-12-01",
  
  "projects": {
    "total_created": 12,
    "total_completed": 8,
    "by_type": {
      "modeling": 4,
      "presentation": 3,
      "dashboard": 3,
      "analytics": 2
    }
  },
  
  "commands": {
    "/interview": 15,
    "/plan": 14,
    "/execute": 87,
    "/status": 45,
    "/review": 12,
    "/export": 8
  },
  
  "tokens": {
    "total_input": 245000,
    "total_output": 189000,
    "by_project": {
      "acme-churn": {"input": 45000, "output": 32000},
      "beta-dashboard": {"input": 38000, "output": 29000}
    }
  }
}
```

---

# XII. Training and Support

## 12.1 Training Assets

| Asset | Format | Purpose |
|-------|--------|---------|
| Quick Reference Card | PDF (1 page) | Desk reference for commands |
| Getting Started Video | MP4 (15 min) | End-to-end walkthrough |
| Command Reference | Markdown | Detailed command documentation |
| FAQ | SharePoint page | Common questions and answers |

## 12.2 Support Channels

| Channel | Purpose | Response Time |
|---------|---------|---------------|
| Teams Channel: #Claude-Code-Help | General questions, tips | Community (async) |
| D&A Office Hours | Live troubleshooting | Weekly (scheduled) |
| Email: da-claude@kearney.com | Bug reports, feature requests | 2 business days |

## 12.3 Quick Reference Card

```
┌─────────────────────────────────────────────────────────────────┐
│         KEARNEY AI CODING ASSISTANT - QUICK REFERENCE           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  CREATE NEW PROJECT                                             │
│  ─────────────────                                              │
│  python ~/kaca-template/scaffold.py my-project-name              │
│  cd my-project-name                                             │
│  Open folder in Claude Desktop (File → Open Folder)             │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  THE STANDARD WORKFLOW                                          │
│  ─────────────────────                                          │
│                                                                 │
│    ┌──────────────────┐                                         │
│    │  1. /project:    │  Define what you're building            │
│    │     interview    │  (requirements, deliverables)           │
│    └────────┬─────────┘                                         │
│             ▼                                                   │
│    ┌──────────────────┐                                         │
│    │  2. /project:    │  Get phased execution plan              │
│    │     plan         │                                         │
│    └────────┬─────────┘                                         │
│             ▼                                                   │
│    ┌──────────────────┐                                         │
│    │  3. /project:    │  Build it (repeat until done)           │
│    │     execute      │                                         │
│    └────────┬─────────┘                                         │
│             ▼                                                   │
│    ┌──────────────────┐                                         │
│    │  4. /project:    │  Check brand compliance                 │
│    │     review       │                                         │
│    └────────┬─────────┘                                         │
│             ▼                                                   │
│    ┌──────────────────┐                                         │
│    │  5. /project:    │  Get final deliverables                 │
│    │     export       │                                         │
│    └──────────────────┘                                         │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  OTHER USEFUL COMMANDS                                          │
│  ─────────────────────                                          │
│  /status   Where am I? What's next?                     │
│  /edit     Change requirements                          │
│  /spec     View current spec                            │
│  /history  View spec versions                           │
│  /project:compact  Free up context (long sessions)              │
│  /project:reset    Start over (archives current state)          │
│  /help     Show all commands                            │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  YOUR PROJECT FOLDERS                                           │
│  ────────────────────                                           │
│  data/raw/        ← Put source files here                       │
│  data/processed/  ← Cleaned data goes here                      │
│  outputs/         ← Charts and reports appear here              │
│  exports/         ← Final deliverables here                     │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  PROJECT TYPES                                                  │
│  ─────────────                                                  │
│  1. Data Engineering    5. Proposal Content                     │
│  2. ML/Stats Modeling   6. Dashboard                            │
│  3. Analytics Asset     7. Web Application                      │
│  4. Presentation/Deck   8. Research/Synthesis                   │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  NEED HELP?                                                     │
│  ──────────                                                     │
│  Teams: #Claude-Code-Help                                       │
│  Office Hours: Wednesdays 2-3pm ET                              │
│  Email: da-claude@kearney.com                                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

# XIII. Hybrid and Multi-Type Projects

## 13.1 The Reality of Consulting Projects

Most real consulting engagements involve multiple work product types:

**Example: "Full-Stack" Client Engagement**
1. Data engineering (ingest and clean client data)
2. Statistical modeling (build churn model)
3. Dashboard (model monitoring interface)
4. Presentation (executive readout)

## 13.2 Multi-Type spec.yaml

The spec.yaml schema supports multiple type-specific sections:

```yaml
# project_state/spec.yaml (multi-type project)

version: 3
meta:
  project_name: acme-full-engagement
  project_type: multi  # Special type indicator
  client: Acme Corporation
  deadline: 2025-12-31
  
problem:
  business_question: |
    Reduce customer churn through predictive modeling,
    executive visibility, and operational dashboards.

# === MULTIPLE TYPE-SPECIFIC SECTIONS ===

data_engineering:
  sources:
    - name: CRM export
      type: csv
      volume: 500MB
  transformations:
    - Join customer and transaction tables
    - Calculate rolling 90-day metrics
  outputs:
    - analytical_dataset.parquet

modeling:
  problem_type: classification
  target_variable: churned_90_days
  validation:
    strategy: time_based_split
    metrics: [auc, precision_at_20pct]
  interpretability:
    required: true
    audience: business_users

dashboard:
  type: operational
  update_frequency: daily
  views:
    - name: Churn Risk Monitor
      metrics: [at_risk_count, trend]
    - name: Model Performance
      metrics: [auc_over_time, drift]

presentation:
  purpose: executive_readout
  audience: c_suite
  slide_count: 15
  key_messages:
    - Model identifies 80% of churners in top 20%
    - Dashboard enables proactive intervention

# === PHASES MAP TO TYPES ===
phases:
  - phase: 1
    name: Data Foundation
    type: data_engineering
    
  - phase: 2
    name: Model Development
    type: modeling
    
  - phase: 3
    name: Dashboard Build
    type: dashboard
    
  - phase: 4
    name: Executive Readout
    type: presentation
```

## 13.3 Interview Flow for Multi-Type Projects

```markdown
# Interview adaptation for multi-type projects

Claude: What type of work product are you building?
        
        1. Data Engineering
        2. Statistical/ML Model
        ...
        9. Multi-Type Project (combines several of the above)

User: 9

Claude: You're building a multi-type project. Let's identify the components.
        
        Which of the following will this project include? (Select all that apply)
        
        [x] Data Engineering
        [x] Statistical/ML Model
        [ ] Analytics Asset
        [ ] Presentation/Deck
        [ ] Proposal Content
        [x] Dashboard
        [ ] Web Application
        [ ] Research/Synthesis

User: Data Engineering, ML Model, Dashboard, Presentation

Claude: Got it. Your project has 4 components:
        1. Data Engineering
        2. ML Model
        3. Dashboard
        4. Presentation
        
        We'll walk through each component's requirements in order.
        Let's start with Data Engineering...
        
        [Continues with data_engineering interview tree]
        [Then modeling interview tree]
        [Then dashboard interview tree]
        [Then presentation interview tree]
```

---

# XIV. Output and Publishing

## 14.1 Export Directory Structure

```
exports/
├── deliverables/           # Final client-ready files
│   ├── Acme_Executive_Readout_2025-12-01.pptx
│   ├── Acme_Model_Documentation.docx
│   └── churn_scoring_script.py
│
├── supporting/             # Reference materials
│   ├── data_dictionary.md
│   └── methodology_notes.md
│
└── manifest.json           # Export manifest
```

### Export Manifest

```json
{
  "project_name": "acme-churn-model",
  "exported_at": "2025-12-01T16:30:00Z",
  "exported_by": "jsmith",
  
  "deliverables": [
    {
      "filename": "Acme_Executive_Readout_2025-12-01.pptx",
      "type": "presentation",
      "slides": 15,
      "size_kb": 2340,
      "qc_passed": true
    },
    {
      "filename": "churn_scoring_script.py",
      "type": "code",
      "lines": 245,
      "qc_passed": true
    }
  ],
  
  "qc_summary": {
    "all_passed": true,
    "checks_run": 12,
    "warnings": 0,
    "errors": 0
  },
  
  "human_review_required": true,
  "human_review_completed": false
}
```

## 14.2 SharePoint Publishing (v2.0+)

Future integration to publish directly to SharePoint:

```markdown
# .claude/commands/publish.md (Future - v2.0)

## /project:publish

Publish exports to SharePoint/Teams.

### Usage

/project:publish                    # Publish to default location
/project:publish --target "Client Shared/Deliverables"

### Behavior

1. Validate exports exist and QC passed
2. Confirm human review completed
3. Connect to SharePoint (using Kearney SSO)
4. Upload deliverables folder
5. Set appropriate permissions
6. Return share link

### Configuration

Set default publish target in project spec:

```yaml
# In spec.yaml
publishing:
  target: "SharePoint/Clients/Acme/Deliverables"
  notify:
    - jane.smith@kearney.com
    - bob.jones@kearney.com
```
```

---

# XV. Audit Trail

## 15.1 Logging Architecture

```
project_state/
├── logs/
│   ├── sessions/               # Per-session logs
│   │   ├── 2025-12-01_093000.md
│   │   └── 2025-12-01_143022.md
│   │
│   ├── commands/               # Command execution log
│   │   └── command_log.jsonl
│   │
│   └── exports/                # Export history
│       └── export_log.jsonl
```

## 15.2 Command Log Format

```jsonl
{"timestamp": "2025-12-01T09:30:00Z", "command": "/interview", "duration_sec": 1245, "result": "success", "spec_version": 1}
{"timestamp": "2025-12-01T10:05:00Z", "command": "/plan", "duration_sec": 45, "result": "success", "tasks_created": 12}
{"timestamp": "2025-12-01T10:10:00Z", "command": "/execute", "duration_sec": 320, "result": "success", "task_id": "1.1"}
{"timestamp": "2025-12-01T10:20:00Z", "command": "/execute", "duration_sec": 280, "result": "success", "task_id": "1.2"}
{"timestamp": "2025-12-01T10:30:00Z", "command": "/review", "duration_sec": 15, "result": "success", "qc_passed": true}
```

## 15.3 Export Log Format

```jsonl
{"timestamp": "2025-12-01T16:30:00Z", "files": ["exec_readout.pptx", "model_doc.docx"], "qc_passed": true, "human_review": false, "destination": "local"}
{"timestamp": "2025-12-02T09:00:00Z", "files": ["exec_readout.pptx", "model_doc.docx"], "qc_passed": true, "human_review": true, "destination": "sharepoint", "url": "https://..."}
```

## 15.4 Reproducibility

For regulated clients requiring reproducibility:

```markdown
# project_state/logs/reproducibility.md

## Reproducibility Record

This document captures information needed to reproduce this project's outputs.

### Environment
- Template Version: 2.0.3
- Python Version: 3.11.4
- Key Package Versions:
  - pandas: 2.1.0
  - matplotlib: 3.8.0
  - python-pptx: 0.6.21

### Data Snapshot
- Raw data hash (SHA-256): a1b2c3d4...
- Processed data hash: e5f6g7h8...

### Model Artifacts (if applicable)
- Model file: model_v1.pkl
- Model hash: i9j0k1l2...
- Training date: 2025-12-01
- Validation AUC: 0.82

### Outputs
| File | Hash | Created |
|------|------|---------|
| exec_readout.pptx | m3n4o5p6... | 2025-12-01 16:30 |
| model_doc.docx | q7r8s9t0... | 2025-12-01 16:30 |
```

---

# XVI. Implementation Checklist

## v1.0 (Launch)

### Core Scaffolding
- [ ] scaffold.py with prerequisite checking
- [ ] prereq_checker.py
- [ ] .gitignore template
- [ ] .kaca-version.json tracking

### Data Handling
- [ ] data_handler.py with DuckDB integration
- [ ] Data guidance in CLAUDE.md
- [ ] Large file handling documentation

### Error Recovery
- [ ] /project:reset command
- [ ] /project:rollback command
- [ ] state_validator.py
- [ ] Archive system for reset states

### Quality Control
- [ ] QC report generation
- [ ] Human approval warnings on export
- [ ] Export manifest

### Branding
- [ ] brand_override.yaml support
- [ ] Load override in brand_guard.py

### Documentation
- [ ] Quick Reference Card (PDF)
- [ ] GETTING_STARTED.md
- [ ] TROUBLESHOOTING.md

## v1.1 (Fast Follow)

- [ ] /project:compact command
- [ ] Session logging
- [ ] Multi-type project interview flow
- [ ] Audit logging (command_log.jsonl)
- [ ] Update mechanism

## v2.0 (Future)

- [ ] Git collaboration workflow
- [ ] Merge conflict resolver
- [ ] SharePoint publishing
- [ ] Cloud data platform connectors
- [ ] Telemetry (opt-in)
- [ ] Project registry

---

# END OF DEPLOYMENT AND OPERATIONS SPECIFICATION

*Template as Factory. Projects as Products. Users Protected.*

**Kearney Digital & Analytics**
