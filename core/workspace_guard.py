# core/workspace_guard.py
"""
Workspace validation to prevent accidental work in the template repo.
"""

import json
from pathlib import Path
from typing import Tuple


def is_template_repo() -> bool:
    """
    Check if we're in the template repo vs a scaffolded project.

    Template repo indicators:
    - Has scaffold.py in root
    - Missing .kaca-version.json

    Scaffolded project indicators:
    - Has .kaca-version.json
    - May have symlinked core/ and config/

    Returns:
        True if in template repo, False if in scaffolded project
    """
    cwd = Path.cwd()

    has_scaffold = (cwd / "scaffold.py").exists()
    has_version = (cwd / ".kaca-version.json").exists()

    # If we have scaffold.py but no version file, we're in template
    if has_scaffold and not has_version:
        return True

    return False


def get_workspace_info() -> dict:
    """
    Get information about the current workspace.

    Returns:
        Dict with workspace details including:
        - is_template: bool
        - project_name: str or None
        - template_version: str or None
        - created_at: str or None
        - template_path: str or None
    """
    cwd = Path.cwd()

    version_file = cwd / ".kaca-version.json"
    if version_file.exists():
        try:
            with open(version_file) as f:
                info = json.load(f)
                info["is_template"] = False
                return info
        except (json.JSONDecodeError, IOError):
            pass

    return {
        "is_template": True,
        "project_name": None,
        "template_version": None,
        "created_at": None,
        "template_path": None,
    }


def verify_workspace(raise_on_template: bool = True) -> Tuple[bool, str]:
    """
    Verify we're in a valid workspace for project work.

    Args:
        raise_on_template: If True, raise RuntimeError when in template repo

    Returns:
        (is_valid, message) tuple
    """
    if is_template_repo():
        message = """
+====================================================================+
|  WARNING: You are in the KACA template repository                  |
|                                                                    |
|  This is the shared template - do not create projects here.        |
|  Your work would pollute the shared codebase.                      |
|                                                                    |
|  TO FIX:                                                           |
|                                                                    |
|  1. Create a new project:                                          |
|                                                                    |
|     Mac/Linux:                                                     |
|       python scaffold.py my-project --path ~/Projects/             |
|                                                                    |
|     Windows (PowerShell):                                          |
|       python scaffold.py my-project --path $env:USERPROFILE\\Projects|
|                                                                    |
|  2. Open the NEW project folder in Claude Code                     |
|                                                                    |
|  3. Start working there, not here                                  |
|                                                                    |
+====================================================================+
"""
        if raise_on_template:
            raise RuntimeError(message)
        return False, message

    return True, "Workspace OK"


def require_project_workspace():
    """
    Decorator to require a valid project workspace.

    Usage:
        @require_project_workspace()
        def my_function():
            # Only runs in scaffolded projects
            pass
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            verify_workspace(raise_on_template=True)
            return func(*args, **kwargs)
        return wrapper
    return decorator


def validate_write(path: str) -> bool:
    """
    Validate that a write operation is within project boundaries.

    Used by hooks to prevent writes outside the project.

    Args:
        path: Path being written to

    Returns:
        True if write is allowed, False otherwise
    """
    target = Path(path).resolve()
    cwd = Path.cwd().resolve()

    # Allow writes within project directory
    try:
        target.relative_to(cwd)
        return True
    except ValueError:
        # Path is outside project
        print(f"Write blocked: {path} is outside project directory")
        return False
