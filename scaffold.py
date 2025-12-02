#!/usr/bin/env python3
# scaffold.py
"""
Project scaffolding for Kearney AI Coding Assistant.

Creates a new project from the template with proper structure,
symlinks to shared infrastructure, and user-specific directories.

Usage:
    python scaffold.py <project-name>
    python scaffold.py <project-name> --path ~/Projects/
    python scaffold.py <project-name> --no-symlinks  # Copy instead of symlink
    python scaffold.py <project-name> --skip-checks  # Skip prereq checks (not recommended)
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Determine template root (where this script lives)
TEMPLATE_ROOT = Path(__file__).parent.resolve()

# Add template root to path so we can import from core/
sys.path.insert(0, str(TEMPLATE_ROOT))

from core.prereq_checker import run_all_checks, print_results


def create_symlink_or_junction(src: Path, dst: Path) -> None:
    """
    Create symlink on Unix or junction on Windows.

    Junctions on Windows don't require admin privileges and work
    similar to symlinks for directories.

    Args:
        src: Source path (must exist).
        dst: Destination path (will be created).
    """
    if sys.platform == "win32":
        # Windows: Use junction for directories (no admin required)
        if src.is_dir():
            subprocess.run(
                ["cmd", "/c", "mklink", "/J", str(dst), str(src)],
                check=True,
                capture_output=True
            )
        else:
            # For files, just copy on Windows (no junction for files)
            shutil.copy2(src, dst)
    else:
        # Unix: Use symlinks
        dst.symlink_to(src)


def create_symlink_or_copy(src: Path, dst: Path, use_symlinks: bool) -> None:
    """
    Create symlink/junction or copy based on use_symlinks flag.

    Args:
        src: Source path.
        dst: Destination path.
        use_symlinks: If True, create symlink/junction. If False, copy.
    """
    if not use_symlinks:
        if src.is_dir():
            shutil.copytree(src, dst)
        else:
            shutil.copy2(src, dst)
        return

    create_symlink_or_junction(src, dst)


def get_template_version() -> str:
    """Get the template version from VERSION file."""
    version_file = TEMPLATE_ROOT / "VERSION"
    if version_file.exists():
        return version_file.read_text().strip()
    return "unknown"


def scaffold_project(
    name: str,
    target_dir: Path,
    use_symlinks: bool = True
) -> Path:
    """
    Create a new project from the template.

    Args:
        name: Project name (used for folder name).
        target_dir: Parent directory for the project.
        use_symlinks: If True, symlink shared dirs. If False, copy everything.

    Returns:
        Path to created project.

    Raises:
        FileExistsError: If project directory already exists.
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

    template_version = get_template_version()

    # === FILES TO COPY (user can customize) ===
    print("  Copying customizable files...")

    # CLAUDE.md - user might need to customize
    shutil.copy(TEMPLATE_ROOT / "CLAUDE.md", project_path / "CLAUDE.md")
    print("    Copied: CLAUDE.md")

    # .claude/ directory - agents and commands (user might customize)
    shutil.copytree(TEMPLATE_ROOT / ".claude", project_path / ".claude")
    print("    Copied: .claude/")

    # README with project-specific info
    readme_content = f"""# {name}

Created: {datetime.now().strftime("%Y-%m-%d")}
Template Version: {template_version}

## Quick Start

1. Place your data files in `data/raw/`
2. Open this folder in Claude Desktop
3. Type `/interview` to define your project
4. Type `/plan` to generate execution plan
5. Type `/execute` to start building (repeat until done)
6. Type `/review` to check brand compliance
7. Type `/export` to create deliverables

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
| `/edit` | Modify requirements |
| `/spec` | View current specification |
| `/history` | View spec version history |
| `/help` | Show all commands |
| `/compact` | Free up context space |
| `/reset` | Start fresh |
| `/rollback` | Restore previous state |

## Data Handling

- Files < 50MB: Loaded directly with pandas
- Files 50-500MB: Use DuckDB via `core/data_handler.py`
- Files > 500MB: Query in DuckDB, never load fully into memory

Place your data files in `data/raw/` - they will NOT be committed to git.

## Need Help?

- Teams: #Claude-Code-Help
- Office Hours: Wednesdays 2-3pm ET
- Email: da-claude@kearney.com
"""
    (project_path / "README.md").write_text(readme_content)
    print("    Created: README.md")

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
        "project_state/logs/sessions",
        "project_state/logs/commands",
        "project_state/logs/exports",
        "data/raw",
        "data/processed",
        "data/external",
        "outputs/charts",
        "outputs/reports",
        "exports",
        "exports/deliverables",
        "exports/supporting",
    ]

    for dirname in user_dirs:
        (project_path / dirname).mkdir(parents=True, exist_ok=True)

    print("    Created: project_state/, data/, outputs/, exports/")

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
!exports/deliverables/.gitkeep
!exports/supporting/.gitkeep

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
    gitkeep_dirs = [
        "data/raw",
        "data/processed",
        "data/external",
        "outputs/charts",
        "outputs/reports",
        "exports",
        "exports/deliverables",
        "exports/supporting",
    ]
    for dirname in gitkeep_dirs:
        (project_path / dirname / ".gitkeep").touch()

    # === VERSION TRACKING ===
    print("  Creating version tracking...")

    version_info = {
        "template_version": template_version,
        "created_at": datetime.now().isoformat(),
        "template_path": str(TEMPLATE_ROOT),
        "symlinks_used": use_symlinks,
        "project_name": name,
    }

    (project_path / ".kaca-version.json").write_text(
        json.dumps(version_info, indent=2)
    )

    return project_path


def main():
    """CLI entry point for scaffold."""
    parser = argparse.ArgumentParser(
        description="Create a new Kearney AI Coding Assistant project",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scaffold.py my-project
  python scaffold.py client-analysis --path ~/Projects/
  python scaffold.py offline-project --no-symlinks

The project will be created with:
  - Symlinks to shared infrastructure (core/, config/, bootstrap/)
  - Copied customizable files (CLAUDE.md, .claude/)
  - Empty directories for data, outputs, and exports
  - .gitignore to protect sensitive data
"""
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
            print("\nTo skip checks (not recommended): --skip-checks")
            sys.exit(1)

    # Create project
    try:
        project_path = scaffold_project(
            name=args.name,
            target_dir=Path(args.path).resolve(),
            use_symlinks=not args.no_symlinks
        )

        link_note = ""
        if not args.no_symlinks:
            link_note = """
  Note: Shared infrastructure (core/, config/, bootstrap/) is linked
  to the template. To update, pull the latest template version.
"""

        print("\n" + "=" * 60)
        print("  PROJECT CREATED SUCCESSFULLY")
        print("=" * 60)
        print(f"""
  Location: {project_path}
{link_note}
  Next steps:
    1. cd "{project_path}"
    2. Open this folder in Claude Desktop (File -> Open Folder)
    3. Type: /project:interview

  Happy building!
""")

    except FileExistsError as e:
        print(f"\nError: {e}")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"\nError creating symlinks: {e}")
        print("Try using --no-symlinks to copy files instead.")
        sys.exit(1)
    except Exception as e:
        print(f"\nError creating project: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
