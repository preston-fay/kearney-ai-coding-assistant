# core/state_validator.py
"""
Validate and repair project state files for consistency and corruption.

Provides:
- Validation of spec.yaml and status.json
- Detection of common issues
- Automatic repair of recoverable problems
- Archive and reset functionality

Usage:
    from core.state_validator import (
        validate_project_state,
        attempt_repair,
        archive_state,
        reset_state,
    )

    # Validate current state
    valid, results = validate_project_state(Path("."))

    # Attempt repairs if invalid
    if not valid:
        repairs = attempt_repair(Path("."))
"""

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Dict, Any, Optional

import yaml


def validate_spec(spec_path: Path) -> Tuple[bool, List[str]]:
    """
    Validate spec.yaml structure and required fields.

    Args:
        spec_path: Path to spec.yaml file

    Returns:
        Tuple of (is_valid, list of issues)
    """
    issues = []

    if not spec_path.exists():
        return False, ["spec.yaml not found"]

    try:
        content = spec_path.read_text()
        if not content.strip():
            return False, ["spec.yaml is empty"]
        spec = yaml.safe_load(content)
    except yaml.YAMLError as e:
        return False, [f"Invalid YAML: {e}"]

    if spec is None:
        return False, ["spec.yaml contains no data"]

    # Check required fields
    required = ["version", "meta"]
    for field in required:
        if field not in spec:
            issues.append(f"Missing required field: {field}")

    # Check meta fields
    if "meta" in spec:
        meta_required = ["project_name", "project_type"]
        for field in meta_required:
            if field not in spec["meta"]:
                issues.append(f"Missing meta field: {field}")

    # Check version format
    if "version" in spec:
        version = spec["version"]
        if not isinstance(version, int) or version < 1:
            issues.append(f"Invalid version: {version} (should be positive integer)")

    return len(issues) == 0, issues


def validate_status(status_path: Path) -> Tuple[bool, List[str]]:
    """
    Validate status.json structure.

    Args:
        status_path: Path to status.json file

    Returns:
        Tuple of (is_valid, list of issues)
    """
    issues = []

    if not status_path.exists():
        return False, ["status.json not found"]

    try:
        content = status_path.read_text()
        if not content.strip():
            return False, ["status.json is empty"]
        status = json.loads(content)
    except json.JSONDecodeError as e:
        return False, [f"Invalid JSON: {e}"]

    if status is None:
        return False, ["status.json contains no data"]

    # Check required fields
    required = ["project_name"]
    for field in required:
        if field not in status:
            issues.append(f"Missing required field: {field}")

    # Check task structure if present
    if "tasks" in status:
        if not isinstance(status["tasks"], list):
            issues.append("'tasks' must be a list")
        else:
            for i, task in enumerate(status["tasks"]):
                if not isinstance(task, dict):
                    issues.append(f"Task {i} is not a dict")
                    continue
                if "id" not in task:
                    issues.append(f"Task {i} missing 'id'")
                if "status" not in task:
                    issues.append(f"Task {i} missing 'status'")
                elif task["status"] not in ["pending", "in_progress", "done", "blocked"]:
                    issues.append(f"Task {i} has invalid status: {task['status']}")

    return len(issues) == 0, issues


def validate_plan(plan_path: Path) -> Tuple[bool, List[str]]:
    """
    Validate plan.md structure.

    Args:
        plan_path: Path to plan.md file

    Returns:
        Tuple of (is_valid, list of issues)
    """
    issues = []

    if not plan_path.exists():
        # Plan is optional
        return True, []

    try:
        content = plan_path.read_text()
        if not content.strip():
            issues.append("plan.md is empty")
    except Exception as e:
        issues.append(f"Error reading plan.md: {e}")

    return len(issues) == 0, issues


def validate_project_state(project_path: Path) -> Tuple[bool, Dict[str, Any]]:
    """
    Full validation of project state.

    Args:
        project_path: Root path of the project

    Returns:
        Tuple of (all_valid, results_dict)
    """
    state_dir = Path(project_path) / "project_state"

    results = {
        "spec": {"valid": False, "issues": []},
        "status": {"valid": False, "issues": []},
        "plan": {"valid": True, "issues": []},
        "directories": {"valid": True, "issues": []},
        "overall": False,
    }

    # Check state directory exists
    if not state_dir.exists():
        results["directories"]["valid"] = False
        results["directories"]["issues"].append("project_state/ directory not found")
        return False, results

    # Validate spec
    spec_valid, spec_issues = validate_spec(state_dir / "spec.yaml")
    results["spec"]["valid"] = spec_valid
    results["spec"]["issues"] = spec_issues

    # Validate status
    status_valid, status_issues = validate_status(state_dir / "status.json")
    results["status"]["valid"] = status_valid
    results["status"]["issues"] = status_issues

    # Validate plan (optional)
    plan_valid, plan_issues = validate_plan(state_dir / "plan.md")
    results["plan"]["valid"] = plan_valid
    results["plan"]["issues"] = plan_issues

    # Check required directories
    required_dirs = ["spec_history", "logs"]
    for dirname in required_dirs:
        if not (state_dir / dirname).exists():
            results["directories"]["valid"] = False
            results["directories"]["issues"].append(f"Missing directory: {dirname}/")

    # Overall validity
    results["overall"] = (
        spec_valid and
        status_valid and
        plan_valid and
        results["directories"]["valid"]
    )

    return results["overall"], results


def attempt_repair(project_path: Path) -> List[str]:
    """
    Attempt to repair common state issues.

    Args:
        project_path: Root path of the project

    Returns:
        List of repairs made
    """
    repairs = []
    state_dir = Path(project_path) / "project_state"

    # Create state directory if missing
    if not state_dir.exists():
        state_dir.mkdir(parents=True)
        repairs.append("Created project_state/ directory")

    # Repair: Create missing directories
    for subdir in ["spec_history", "logs", "logs/sessions", "logs/commands"]:
        dir_path = state_dir / subdir
        if not dir_path.exists():
            dir_path.mkdir(parents=True)
            repairs.append(f"Created missing directory: {subdir}/")

    # Repair: Initialize empty status.json if missing but spec exists
    status_path = state_dir / "status.json"
    spec_path = state_dir / "spec.yaml"

    if spec_path.exists() and not status_path.exists():
        try:
            spec = yaml.safe_load(spec_path.read_text())
            if spec:
                initial_status = {
                    "project_name": spec.get("meta", {}).get("project_name", "unknown"),
                    "template": spec.get("meta", {}).get("project_type", "unknown"),
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat(),
                    "current_phase": "",
                    "current_task": None,
                    "tasks": [],
                    "artifacts": [],
                    "history": [{
                        "action": "status_repaired",
                        "timestamp": datetime.now().isoformat()
                    }]
                }

                status_path.write_text(json.dumps(initial_status, indent=2))
                repairs.append("Created status.json from spec.yaml")
        except Exception as e:
            repairs.append(f"Could not create status.json: {e}")

    return repairs


def archive_state(
    project_path: Path,
    reason: Optional[str] = None
) -> Path:
    """
    Archive current project state.

    Args:
        project_path: Root path of the project
        reason: Optional reason for archiving

    Returns:
        Path to the archive directory
    """
    state_dir = Path(project_path) / "project_state"
    archive_base = state_dir / "archive"
    archive_base.mkdir(parents=True, exist_ok=True)

    # Create timestamped archive folder with uniqueness handling
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    archive_dir = archive_base / timestamp

    # If timestamp already exists, add a counter
    if archive_dir.exists():
        counter = 1
        while (archive_base / f"{timestamp}_{counter}").exists():
            counter += 1
        archive_dir = archive_base / f"{timestamp}_{counter}"

    archive_dir.mkdir()

    # Files to archive
    files_to_archive = ["spec.yaml", "plan.md", "status.json"]
    for filename in files_to_archive:
        src = state_dir / filename
        if src.exists():
            shutil.copy2(src, archive_dir / filename)

    # Archive spec_history
    spec_history = state_dir / "spec_history"
    if spec_history.exists() and any(spec_history.iterdir()):
        shutil.copytree(spec_history, archive_dir / "spec_history")

    # Archive logs
    logs_dir = state_dir / "logs"
    if logs_dir.exists() and any(logs_dir.iterdir()):
        shutil.copytree(logs_dir, archive_dir / "logs")

    # Write reason file
    if reason:
        (archive_dir / "archive_reason.txt").write_text(reason)

    # Write archive metadata
    metadata = {
        "archived_at": datetime.now().isoformat(),
        "reason": reason,
        "files": [f.name for f in archive_dir.iterdir() if f.is_file()],
    }
    (archive_dir / "archive_metadata.json").write_text(
        json.dumps(metadata, indent=2)
    )

    return archive_dir


def reset_state(project_path: Path, reason: Optional[str] = None) -> Dict[str, Any]:
    """
    Archive current state and reset to fresh state.

    Args:
        project_path: Root path of the project
        reason: Reason for reset

    Returns:
        Dict with reset results
    """
    state_dir = Path(project_path) / "project_state"

    result = {
        "archive_path": None,
        "reset_complete": False,
        "message": "",
    }

    # Archive current state first
    try:
        archive_path = archive_state(project_path, reason or "Project reset")
        result["archive_path"] = str(archive_path)
    except Exception as e:
        result["message"] = f"Failed to archive: {e}"
        return result

    # Remove current state files
    files_to_remove = ["spec.yaml", "plan.md", "status.json"]
    for filename in files_to_remove:
        filepath = state_dir / filename
        if filepath.exists():
            filepath.unlink()

    # Clear spec_history (but keep directory)
    spec_history = state_dir / "spec_history"
    if spec_history.exists():
        for f in spec_history.iterdir():
            if f.is_file():
                f.unlink()

    # Clear logs (but keep directory structure)
    logs_dir = state_dir / "logs"
    if logs_dir.exists():
        for subdir in ["sessions", "commands"]:
            subpath = logs_dir / subdir
            if subpath.exists():
                for f in subpath.iterdir():
                    if f.is_file():
                        f.unlink()

    result["reset_complete"] = True
    result["message"] = f"Project reset. Previous state archived to {archive_path.name}"

    return result


def list_archives(project_path: Path) -> List[Dict[str, Any]]:
    """
    List all available archives.

    Args:
        project_path: Root path of the project

    Returns:
        List of archive info dicts
    """
    archive_base = Path(project_path) / "project_state" / "archive"

    if not archive_base.exists():
        return []

    archives = []
    for archive_dir in sorted(archive_base.iterdir(), reverse=True):
        if not archive_dir.is_dir():
            continue

        info = {
            "name": archive_dir.name,
            "path": str(archive_dir),
            "files": [],
            "reason": None,
            "archived_at": None,
        }

        # Read metadata if available
        metadata_path = archive_dir / "archive_metadata.json"
        if metadata_path.exists():
            try:
                metadata = json.loads(metadata_path.read_text())
                info["reason"] = metadata.get("reason")
                info["archived_at"] = metadata.get("archived_at")
                info["files"] = metadata.get("files", [])
            except json.JSONDecodeError:
                pass

        # List files if no metadata
        if not info["files"]:
            info["files"] = [f.name for f in archive_dir.iterdir() if f.is_file()]

        archives.append(info)

    return archives


def restore_from_archive(
    project_path: Path,
    archive_name: str,
    archive_current: bool = True
) -> Dict[str, Any]:
    """
    Restore project state from an archive.

    Args:
        project_path: Root path of the project
        archive_name: Name of archive to restore (timestamp folder name)
        archive_current: Whether to archive current state before restoring

    Returns:
        Dict with restore results
    """
    state_dir = Path(project_path) / "project_state"
    archive_dir = state_dir / "archive" / archive_name

    result = {
        "restored": False,
        "current_archived_to": None,
        "message": "",
    }

    if not archive_dir.exists():
        result["message"] = f"Archive not found: {archive_name}"
        return result

    # Archive current state first (safety)
    if archive_current:
        try:
            current_archive = archive_state(
                project_path,
                f"Auto-archived before restore from {archive_name}"
            )
            result["current_archived_to"] = str(current_archive)
        except Exception as e:
            result["message"] = f"Failed to archive current state: {e}"
            return result

    # Restore files
    files_to_restore = ["spec.yaml", "plan.md", "status.json"]
    restored_files = []

    for filename in files_to_restore:
        src = archive_dir / filename
        dst = state_dir / filename
        if src.exists():
            shutil.copy2(src, dst)
            restored_files.append(filename)

    # Restore spec_history if present
    archived_history = archive_dir / "spec_history"
    if archived_history.exists():
        target_history = state_dir / "spec_history"
        if target_history.exists():
            shutil.rmtree(target_history)
        shutil.copytree(archived_history, target_history)
        restored_files.append("spec_history/")

    result["restored"] = True
    result["files"] = restored_files
    result["message"] = f"Restored {len(restored_files)} items from {archive_name}"

    return result


def get_state_summary(project_path: Path) -> Dict[str, Any]:
    """
    Get a summary of current project state.

    Args:
        project_path: Root path of the project

    Returns:
        Dict with state summary
    """
    state_dir = Path(project_path) / "project_state"

    summary = {
        "has_spec": False,
        "has_status": False,
        "has_plan": False,
        "spec_version": None,
        "project_name": None,
        "tasks_total": 0,
        "tasks_done": 0,
        "archives_count": 0,
    }

    # Check spec
    spec_path = state_dir / "spec.yaml"
    if spec_path.exists():
        summary["has_spec"] = True
        try:
            spec = yaml.safe_load(spec_path.read_text())
            if spec:
                summary["spec_version"] = spec.get("version")
                summary["project_name"] = spec.get("meta", {}).get("project_name")
        except Exception:
            pass

    # Check status
    status_path = state_dir / "status.json"
    if status_path.exists():
        summary["has_status"] = True
        try:
            status = json.loads(status_path.read_text())
            tasks = status.get("tasks", [])
            summary["tasks_total"] = len(tasks)
            summary["tasks_done"] = sum(1 for t in tasks if t.get("status") == "done")
        except Exception:
            pass

    # Check plan
    summary["has_plan"] = (state_dir / "plan.md").exists()

    # Count archives
    archive_dir = state_dir / "archive"
    if archive_dir.exists():
        summary["archives_count"] = sum(1 for d in archive_dir.iterdir() if d.is_dir())

    return summary


def print_validation_results(results: Dict[str, Any]) -> None:
    """
    Print validation results in a readable format.

    Args:
        results: Results dict from validate_project_state
    """
    print("\n" + "=" * 60)
    print("  PROJECT STATE VALIDATION")
    print("=" * 60 + "\n")

    overall = results.get("overall", False)
    status_str = "VALID" if overall else "INVALID"
    print(f"  Overall Status: {status_str}\n")

    for component in ["spec", "status", "plan", "directories"]:
        if component not in results:
            continue

        comp_result = results[component]
        valid = comp_result.get("valid", False)
        issues = comp_result.get("issues", [])

        status = "[PASS]" if valid else "[FAIL]"
        print(f"  {status} {component}")

        for issue in issues:
            print(f"         - {issue}")

    print("\n" + "-" * 60)

    if not overall:
        print("\n  Run attempt_repair() to fix common issues.\n")
