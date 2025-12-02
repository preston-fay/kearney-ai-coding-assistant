# core/audit_logger.py
"""
Audit logging for Kearney AI Coding Assistant projects.

Provides:
- Command execution logging (JSONL format)
- Export history tracking
- Reproducibility records
- Session audit trails

Usage:
    from core.audit_logger import (
        log_command,
        log_export,
        get_command_history,
        create_reproducibility_record,
    )

    # Log a command execution
    log_command(
        project_path=Path("."),
        command="/project:execute",
        duration_sec=120,
        result="success",
        task_id="1.1"
    )

    # Log an export
    log_export(
        project_path=Path("."),
        files=["report.pptx", "data.xlsx"],
        qc_passed=True
    )
"""

import hashlib
import json
import platform
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict


# Log directories (relative to project_state/)
LOGS_DIR = "logs"
COMMANDS_DIR = "commands"
EXPORTS_DIR = "exports"
SESSIONS_DIR = "sessions"


@dataclass
class CommandLogEntry:
    """Log entry for a command execution."""
    timestamp: str
    command: str
    duration_sec: Optional[float] = None
    result: str = "success"  # success, error, cancelled
    error_message: Optional[str] = None
    # Additional context fields
    spec_version: Optional[int] = None
    task_id: Optional[str] = None
    tasks_created: Optional[int] = None
    qc_passed: Optional[bool] = None

    def to_json(self) -> str:
        """Convert to JSON string, excluding None values."""
        data = {k: v for k, v in asdict(self).items() if v is not None}
        return json.dumps(data)


@dataclass
class ExportLogEntry:
    """Log entry for an export operation."""
    timestamp: str
    files: List[str]
    qc_passed: bool
    human_review: bool = False
    destination: str = "local"  # local, sharepoint, etc.
    url: Optional[str] = None
    export_manifest: Optional[str] = None

    def to_json(self) -> str:
        """Convert to JSON string, excluding None values."""
        data = {k: v for k, v in asdict(self).items() if v is not None}
        return json.dumps(data)


def _ensure_log_dirs(project_path: Path) -> Path:
    """Ensure log directories exist and return logs path."""
    logs_path = Path(project_path) / "project_state" / LOGS_DIR
    (logs_path / COMMANDS_DIR).mkdir(parents=True, exist_ok=True)
    (logs_path / EXPORTS_DIR).mkdir(parents=True, exist_ok=True)
    (logs_path / SESSIONS_DIR).mkdir(parents=True, exist_ok=True)
    return logs_path


def log_command(
    project_path: Path,
    command: str,
    duration_sec: Optional[float] = None,
    result: str = "success",
    error_message: Optional[str] = None,
    **kwargs
) -> Path:
    """
    Log a command execution.

    Args:
        project_path: Root path of the project
        command: Command that was executed (e.g., "/project:execute")
        duration_sec: Duration of command in seconds
        result: Result status (success, error, cancelled)
        error_message: Error message if result is error
        **kwargs: Additional context (spec_version, task_id, etc.)

    Returns:
        Path to the log file
    """
    logs_path = _ensure_log_dirs(project_path)
    log_file = logs_path / COMMANDS_DIR / "command_log.jsonl"

    entry = CommandLogEntry(
        timestamp=datetime.now().isoformat(),
        command=command,
        duration_sec=duration_sec,
        result=result,
        error_message=error_message,
        spec_version=kwargs.get("spec_version"),
        task_id=kwargs.get("task_id"),
        tasks_created=kwargs.get("tasks_created"),
        qc_passed=kwargs.get("qc_passed"),
    )

    with open(log_file, "a") as f:
        f.write(entry.to_json() + "\n")

    return log_file


def log_export(
    project_path: Path,
    files: List[str],
    qc_passed: bool,
    human_review: bool = False,
    destination: str = "local",
    url: Optional[str] = None,
    export_manifest: Optional[str] = None,
) -> Path:
    """
    Log an export operation.

    Args:
        project_path: Root path of the project
        files: List of exported file names
        qc_passed: Whether QC checks passed
        human_review: Whether human review was completed
        destination: Export destination (local, sharepoint)
        url: URL if published remotely
        export_manifest: Path to export manifest

    Returns:
        Path to the log file
    """
    logs_path = _ensure_log_dirs(project_path)
    log_file = logs_path / EXPORTS_DIR / "export_log.jsonl"

    entry = ExportLogEntry(
        timestamp=datetime.now().isoformat(),
        files=files,
        qc_passed=qc_passed,
        human_review=human_review,
        destination=destination,
        url=url,
        export_manifest=export_manifest,
    )

    with open(log_file, "a") as f:
        f.write(entry.to_json() + "\n")

    return log_file


def get_command_history(
    project_path: Path,
    limit: Optional[int] = None,
    command_filter: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Get command execution history.

    Args:
        project_path: Root path of the project
        limit: Maximum number of entries to return (newest first)
        command_filter: Filter by command name (e.g., "/project:execute")

    Returns:
        List of command log entries
    """
    log_file = Path(project_path) / "project_state" / LOGS_DIR / COMMANDS_DIR / "command_log.jsonl"

    if not log_file.exists():
        return []

    entries = []
    for line in log_file.read_text().strip().split("\n"):
        if line:
            try:
                entry = json.loads(line)
                if command_filter is None or entry.get("command") == command_filter:
                    entries.append(entry)
            except json.JSONDecodeError:
                continue

    # Reverse for newest first
    entries.reverse()

    if limit:
        entries = entries[:limit]

    return entries


def get_export_history(
    project_path: Path,
    limit: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """
    Get export history.

    Args:
        project_path: Root path of the project
        limit: Maximum number of entries to return (newest first)

    Returns:
        List of export log entries
    """
    log_file = Path(project_path) / "project_state" / LOGS_DIR / EXPORTS_DIR / "export_log.jsonl"

    if not log_file.exists():
        return []

    entries = []
    for line in log_file.read_text().strip().split("\n"):
        if line:
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    entries.reverse()

    if limit:
        entries = entries[:limit]

    return entries


def get_command_stats(project_path: Path) -> Dict[str, Any]:
    """
    Get statistics about command usage.

    Args:
        project_path: Root path of the project

    Returns:
        Dict with command statistics
    """
    history = get_command_history(project_path)

    stats = {
        "total_commands": len(history),
        "commands_by_type": {},
        "success_rate": 0.0,
        "total_duration_sec": 0.0,
        "first_command": None,
        "last_command": None,
    }

    if not history:
        return stats

    success_count = 0
    for entry in history:
        command = entry.get("command", "unknown")
        stats["commands_by_type"][command] = stats["commands_by_type"].get(command, 0) + 1

        if entry.get("result") == "success":
            success_count += 1

        duration = entry.get("duration_sec")
        if duration:
            stats["total_duration_sec"] += duration

    stats["success_rate"] = success_count / len(history) if history else 0.0
    stats["first_command"] = history[-1].get("timestamp") if history else None
    stats["last_command"] = history[0].get("timestamp") if history else None

    return stats


def compute_file_hash(file_path: Path) -> str:
    """
    Compute SHA-256 hash of a file.

    Args:
        file_path: Path to file

    Returns:
        Hex string of SHA-256 hash
    """
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def get_package_versions() -> Dict[str, str]:
    """
    Get versions of key packages.

    Returns:
        Dict of package name to version
    """
    packages = {}

    # Core packages to check
    package_list = [
        "pandas",
        "matplotlib",
        "python-pptx",
        "pyyaml",
        "pillow",
        "duckdb",
    ]

    for pkg_name in package_list:
        try:
            if pkg_name == "python-pptx":
                import pptx
                packages[pkg_name] = getattr(pptx, "__version__", "unknown")
            elif pkg_name == "pyyaml":
                import yaml
                packages[pkg_name] = getattr(yaml, "__version__", "unknown")
            elif pkg_name == "pillow":
                from PIL import Image
                packages[pkg_name] = getattr(Image, "__version__", "unknown")
            else:
                module = __import__(pkg_name)
                packages[pkg_name] = getattr(module, "__version__", "unknown")
        except ImportError:
            packages[pkg_name] = "not installed"

    return packages


def create_reproducibility_record(
    project_path: Path,
    include_data_hashes: bool = True,
    include_model_info: bool = True,
) -> Path:
    """
    Create a reproducibility record for the project.

    Args:
        project_path: Root path of the project
        include_data_hashes: Whether to compute data file hashes
        include_model_info: Whether to include model artifacts

    Returns:
        Path to the created record file
    """
    project_path = Path(project_path)
    logs_path = _ensure_log_dirs(project_path)
    record_path = logs_path / "reproducibility.md"

    # Get template version
    template_version = "unknown"
    version_file = project_path / ".kaca-version.json"
    if version_file.exists():
        try:
            data = json.loads(version_file.read_text())
            template_version = data.get("template_version", "unknown")
        except (json.JSONDecodeError, IOError):
            pass

    # Get package versions
    packages = get_package_versions()

    # Build record content
    lines = [
        "# Reproducibility Record",
        "",
        f"Generated: {datetime.now().isoformat()}",
        "",
        "## Environment",
        "",
        f"- Template Version: {template_version}",
        f"- Python Version: {sys.version.split()[0]}",
        f"- Platform: {platform.system()} {platform.release()}",
        "",
        "### Key Package Versions",
        "",
    ]

    for pkg, version in sorted(packages.items()):
        lines.append(f"- {pkg}: {version}")

    lines.append("")

    # Data hashes
    if include_data_hashes:
        lines.extend([
            "## Data Snapshot",
            "",
        ])

        raw_dir = project_path / "data" / "raw"
        processed_dir = project_path / "data" / "processed"

        for data_dir, label in [(raw_dir, "Raw"), (processed_dir, "Processed")]:
            if data_dir.exists():
                data_files = [f for f in data_dir.iterdir() if f.is_file() and not f.name.startswith(".")]
                if data_files:
                    lines.append(f"### {label} Data")
                    lines.append("")
                    for file_path in sorted(data_files)[:10]:  # Limit to 10 files
                        try:
                            file_hash = compute_file_hash(file_path)
                            size_kb = file_path.stat().st_size / 1024
                            lines.append(f"- {file_path.name}: {file_hash[:16]}... ({size_kb:.1f} KB)")
                        except Exception:
                            lines.append(f"- {file_path.name}: (could not compute hash)")
                    lines.append("")

    # Model artifacts
    if include_model_info:
        outputs_dir = project_path / "outputs"
        model_files = []

        if outputs_dir.exists():
            for ext in [".pkl", ".joblib", ".h5", ".pt", ".onnx"]:
                model_files.extend(outputs_dir.rglob(f"*{ext}"))

        if model_files:
            lines.extend([
                "## Model Artifacts",
                "",
            ])
            for model_path in model_files:
                try:
                    file_hash = compute_file_hash(model_path)
                    size_kb = model_path.stat().st_size / 1024
                    lines.append(f"- {model_path.name}")
                    lines.append(f"  - Hash: {file_hash[:16]}...")
                    lines.append(f"  - Size: {size_kb:.1f} KB")
                    lines.append(f"  - Modified: {datetime.fromtimestamp(model_path.stat().st_mtime).isoformat()}")
                except Exception:
                    lines.append(f"- {model_path.name}: (could not read)")
            lines.append("")

    # Command history summary
    stats = get_command_stats(project_path)
    if stats["total_commands"] > 0:
        lines.extend([
            "## Session History",
            "",
            f"- Total Commands: {stats['total_commands']}",
            f"- Success Rate: {stats['success_rate']:.1%}",
            f"- Total Duration: {stats['total_duration_sec']:.0f} seconds",
            f"- First Command: {stats['first_command']}",
            f"- Last Command: {stats['last_command']}",
            "",
        ])

    lines.extend([
        "---",
        "",
        "*Generated by Kearney AI Coding Assistant Audit Logger*",
    ])

    record_path.write_text("\n".join(lines))
    return record_path


def create_export_manifest(
    project_path: Path,
    deliverables: List[Dict[str, Any]],
    qc_summary: Dict[str, Any],
) -> Path:
    """
    Create an export manifest file.

    Args:
        project_path: Root path of the project
        deliverables: List of deliverable info dicts
        qc_summary: QC check summary

    Returns:
        Path to the created manifest
    """
    project_path = Path(project_path)
    exports_dir = project_path / "exports"
    exports_dir.mkdir(parents=True, exist_ok=True)

    # Get project name from spec
    project_name = "unknown"
    spec_path = project_path / "project_state" / "spec.yaml"
    if spec_path.exists():
        try:
            import yaml
            spec = yaml.safe_load(spec_path.read_text())
            project_name = spec.get("meta", {}).get("project_name", "unknown")
        except Exception:
            pass

    manifest = {
        "project_name": project_name,
        "exported_at": datetime.now().isoformat(),
        "template_version": _get_template_version(project_path),
        "deliverables": deliverables,
        "qc_summary": qc_summary,
        "human_review_required": True,
        "human_review_completed": False,
    }

    manifest_path = exports_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2))

    return manifest_path


def _get_template_version(project_path: Path) -> str:
    """Get template version from .kaca-version.json."""
    version_file = Path(project_path) / ".kaca-version.json"
    if version_file.exists():
        try:
            data = json.loads(version_file.read_text())
            return data.get("template_version", "unknown")
        except (json.JSONDecodeError, IOError):
            pass
    return "unknown"


def format_command_history(history: List[Dict[str, Any]], max_entries: int = 20) -> str:
    """
    Format command history for display.

    Args:
        history: List of command entries
        max_entries: Maximum entries to show

    Returns:
        Formatted string
    """
    if not history:
        return "No command history available."

    lines = [
        "Command History",
        "=" * 60,
        "",
    ]

    for entry in history[:max_entries]:
        timestamp = entry.get("timestamp", "")[:19]  # Truncate to seconds
        command = entry.get("command", "unknown")
        result = entry.get("result", "")
        duration = entry.get("duration_sec", "")

        status = "[OK]" if result == "success" else "[ERR]"
        duration_str = f"({duration:.1f}s)" if duration else ""

        lines.append(f"  {status} {timestamp} {command} {duration_str}")

        if entry.get("task_id"):
            lines.append(f"       Task: {entry['task_id']}")
        if entry.get("error_message"):
            lines.append(f"       Error: {entry['error_message']}")

    if len(history) > max_entries:
        lines.append(f"\n  ... and {len(history) - max_entries} more entries")

    return "\n".join(lines)


def format_export_history(history: List[Dict[str, Any]], max_entries: int = 10) -> str:
    """
    Format export history for display.

    Args:
        history: List of export entries
        max_entries: Maximum entries to show

    Returns:
        Formatted string
    """
    if not history:
        return "No export history available."

    lines = [
        "Export History",
        "=" * 60,
        "",
    ]

    for entry in history[:max_entries]:
        timestamp = entry.get("timestamp", "")[:19]
        files = entry.get("files", [])
        qc = "QC:PASS" if entry.get("qc_passed") else "QC:FAIL"
        review = "Reviewed" if entry.get("human_review") else "Pending Review"
        dest = entry.get("destination", "local")

        lines.append(f"  {timestamp} - {dest} - {qc} - {review}")
        for f in files[:5]:
            lines.append(f"    - {f}")
        if len(files) > 5:
            lines.append(f"    ... and {len(files) - 5} more files")
        lines.append("")

    return "\n".join(lines)
