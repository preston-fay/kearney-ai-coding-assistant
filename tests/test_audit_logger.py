# tests/test_audit_logger.py
"""Tests for core/audit_logger.py"""

import json
import pytest
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import yaml
from core.audit_logger import (
    CommandLogEntry,
    ExportLogEntry,
    log_command,
    log_export,
    get_command_history,
    get_export_history,
    get_command_stats,
    compute_file_hash,
    get_package_versions,
    create_reproducibility_record,
    create_export_manifest,
    format_command_history,
    format_export_history,
)


@pytest.fixture
def project_dir(tmp_path):
    """Create a basic project directory structure."""
    (tmp_path / "project_state" / "logs" / "commands").mkdir(parents=True)
    (tmp_path / "project_state" / "logs" / "exports").mkdir(parents=True)
    (tmp_path / "project_state" / "logs" / "sessions").mkdir(parents=True)
    (tmp_path / "data" / "raw").mkdir(parents=True)
    (tmp_path / "data" / "processed").mkdir(parents=True)
    (tmp_path / "outputs").mkdir(parents=True)
    (tmp_path / "exports").mkdir(parents=True)

    # Create .kaca-version.json
    version_info = {"template_version": "2.0.0"}
    (tmp_path / ".kaca-version.json").write_text(json.dumps(version_info))

    # Create spec.yaml
    spec = {
        "version": 1,
        "meta": {"project_name": "test-project", "project_type": "analytics"}
    }
    (tmp_path / "project_state" / "spec.yaml").write_text(yaml.dump(spec))

    return tmp_path


class TestCommandLogEntry:
    """Tests for CommandLogEntry dataclass."""

    def test_basic_entry(self):
        """Test creating a basic command log entry."""
        entry = CommandLogEntry(
            timestamp="2025-12-01T12:00:00",
            command="/project:execute"
        )
        assert entry.command == "/project:execute"
        assert entry.result == "success"

    def test_to_json_excludes_none(self):
        """Test that to_json excludes None values."""
        entry = CommandLogEntry(
            timestamp="2025-12-01T12:00:00",
            command="/project:execute"
        )
        json_str = entry.to_json()
        data = json.loads(json_str)

        assert "timestamp" in data
        assert "command" in data
        assert "error_message" not in data  # None values excluded

    def test_with_all_fields(self):
        """Test entry with all fields populated."""
        entry = CommandLogEntry(
            timestamp="2025-12-01T12:00:00",
            command="/project:execute",
            duration_sec=120.5,
            result="success",
            task_id="1.1",
            spec_version=3
        )
        data = json.loads(entry.to_json())

        assert data["duration_sec"] == 120.5
        assert data["task_id"] == "1.1"
        assert data["spec_version"] == 3


class TestExportLogEntry:
    """Tests for ExportLogEntry dataclass."""

    def test_basic_entry(self):
        """Test creating a basic export log entry."""
        entry = ExportLogEntry(
            timestamp="2025-12-01T12:00:00",
            files=["report.pptx"],
            qc_passed=True
        )
        assert entry.destination == "local"
        assert entry.human_review is False

    def test_to_json(self):
        """Test JSON serialization."""
        entry = ExportLogEntry(
            timestamp="2025-12-01T12:00:00",
            files=["report.pptx", "data.xlsx"],
            qc_passed=True,
            human_review=True,
            destination="sharepoint",
            url="https://example.com/share"
        )
        data = json.loads(entry.to_json())

        assert data["files"] == ["report.pptx", "data.xlsx"]
        assert data["url"] == "https://example.com/share"


class TestLogCommand:
    """Tests for log_command function."""

    def test_creates_log_file(self, project_dir):
        """Test that log_command creates log file."""
        log_path = log_command(project_dir, "/project:status")

        assert log_path.exists()
        assert log_path.name == "command_log.jsonl"

    def test_appends_entries(self, project_dir):
        """Test that multiple commands are appended."""
        log_command(project_dir, "/project:status")
        log_command(project_dir, "/project:execute", task_id="1.1")
        log_command(project_dir, "/project:review")

        log_path = project_dir / "project_state" / "logs" / "commands" / "command_log.jsonl"
        lines = log_path.read_text().strip().split("\n")

        assert len(lines) == 3

    def test_logs_duration(self, project_dir):
        """Test logging command duration."""
        log_command(project_dir, "/project:execute", duration_sec=45.5)

        history = get_command_history(project_dir)
        assert history[0]["duration_sec"] == 45.5

    def test_logs_error(self, project_dir):
        """Test logging command error."""
        log_command(
            project_dir,
            "/project:execute",
            result="error",
            error_message="File not found"
        )

        history = get_command_history(project_dir)
        assert history[0]["result"] == "error"
        assert history[0]["error_message"] == "File not found"


class TestLogExport:
    """Tests for log_export function."""

    def test_creates_log_file(self, project_dir):
        """Test that log_export creates log file."""
        log_path = log_export(
            project_dir,
            files=["report.pptx"],
            qc_passed=True
        )

        assert log_path.exists()
        assert log_path.name == "export_log.jsonl"

    def test_logs_files(self, project_dir):
        """Test logging exported files."""
        log_export(
            project_dir,
            files=["report.pptx", "data.xlsx", "model.pkl"],
            qc_passed=True,
            human_review=True
        )

        history = get_export_history(project_dir)
        assert len(history[0]["files"]) == 3
        assert history[0]["human_review"] is True


class TestGetCommandHistory:
    """Tests for get_command_history function."""

    def test_empty_history(self, project_dir):
        """Test getting empty history."""
        history = get_command_history(project_dir)
        assert history == []

    def test_returns_newest_first(self, project_dir):
        """Test that history is returned newest first."""
        log_command(project_dir, "/project:interview")
        log_command(project_dir, "/project:plan")
        log_command(project_dir, "/project:execute")

        history = get_command_history(project_dir)

        assert history[0]["command"] == "/project:execute"
        assert history[-1]["command"] == "/project:interview"

    def test_limit_parameter(self, project_dir):
        """Test limiting number of results."""
        for i in range(10):
            log_command(project_dir, f"/command:{i}")

        history = get_command_history(project_dir, limit=3)
        assert len(history) == 3

    def test_command_filter(self, project_dir):
        """Test filtering by command."""
        log_command(project_dir, "/project:execute", task_id="1.1")
        log_command(project_dir, "/project:status")
        log_command(project_dir, "/project:execute", task_id="1.2")

        history = get_command_history(project_dir, command_filter="/project:execute")
        assert len(history) == 2
        assert all(h["command"] == "/project:execute" for h in history)


class TestGetExportHistory:
    """Tests for get_export_history function."""

    def test_empty_history(self, project_dir):
        """Test getting empty history."""
        history = get_export_history(project_dir)
        assert history == []

    def test_returns_newest_first(self, project_dir):
        """Test that history is returned newest first."""
        log_export(project_dir, files=["file1.pptx"], qc_passed=True)
        log_export(project_dir, files=["file2.pptx"], qc_passed=True)

        history = get_export_history(project_dir)

        assert "file2.pptx" in history[0]["files"]
        assert "file1.pptx" in history[1]["files"]


class TestGetCommandStats:
    """Tests for get_command_stats function."""

    def test_empty_stats(self, project_dir):
        """Test stats with no commands."""
        stats = get_command_stats(project_dir)

        assert stats["total_commands"] == 0
        assert stats["success_rate"] == 0.0

    def test_counts_commands(self, project_dir):
        """Test command counting."""
        log_command(project_dir, "/project:execute", duration_sec=30)
        log_command(project_dir, "/project:execute", duration_sec=45)
        log_command(project_dir, "/project:status", duration_sec=5)

        stats = get_command_stats(project_dir)

        assert stats["total_commands"] == 3
        assert stats["commands_by_type"]["/project:execute"] == 2
        assert stats["commands_by_type"]["/project:status"] == 1
        assert stats["total_duration_sec"] == 80

    def test_calculates_success_rate(self, project_dir):
        """Test success rate calculation."""
        log_command(project_dir, "/project:execute", result="success")
        log_command(project_dir, "/project:execute", result="success")
        log_command(project_dir, "/project:execute", result="error")
        log_command(project_dir, "/project:execute", result="success")

        stats = get_command_stats(project_dir)

        assert stats["success_rate"] == 0.75


class TestComputeFileHash:
    """Tests for compute_file_hash function."""

    def test_computes_hash(self, tmp_path):
        """Test computing file hash."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Hello, World!")

        hash1 = compute_file_hash(test_file)

        assert len(hash1) == 64  # SHA-256 hex length
        assert hash1.isalnum()

    def test_same_content_same_hash(self, tmp_path):
        """Test that same content produces same hash."""
        file1 = tmp_path / "file1.txt"
        file2 = tmp_path / "file2.txt"
        file1.write_text("Same content")
        file2.write_text("Same content")

        assert compute_file_hash(file1) == compute_file_hash(file2)

    def test_different_content_different_hash(self, tmp_path):
        """Test that different content produces different hash."""
        file1 = tmp_path / "file1.txt"
        file2 = tmp_path / "file2.txt"
        file1.write_text("Content A")
        file2.write_text("Content B")

        assert compute_file_hash(file1) != compute_file_hash(file2)


class TestGetPackageVersions:
    """Tests for get_package_versions function."""

    def test_returns_dict(self):
        """Test that function returns a dict."""
        versions = get_package_versions()
        assert isinstance(versions, dict)

    def test_includes_key_packages(self):
        """Test that key packages are included."""
        versions = get_package_versions()

        assert "pandas" in versions
        assert "pyyaml" in versions


class TestCreateReproducibilityRecord:
    """Tests for create_reproducibility_record function."""

    def test_creates_file(self, project_dir):
        """Test that record file is created."""
        record_path = create_reproducibility_record(project_dir)

        assert record_path.exists()
        assert record_path.name == "reproducibility.md"

    def test_includes_environment_info(self, project_dir):
        """Test that record includes environment info."""
        record_path = create_reproducibility_record(project_dir)
        content = record_path.read_text()

        assert "Environment" in content
        assert "Python Version" in content
        assert "Template Version" in content

    def test_includes_data_hashes(self, project_dir):
        """Test that record includes data hashes."""
        # Create a data file
        (project_dir / "data" / "raw" / "test.csv").write_text("id,value\n1,100")

        record_path = create_reproducibility_record(project_dir, include_data_hashes=True)
        content = record_path.read_text()

        assert "Data Snapshot" in content
        assert "test.csv" in content

    def test_includes_command_stats(self, project_dir):
        """Test that record includes command history stats."""
        log_command(project_dir, "/project:execute", duration_sec=30)
        log_command(project_dir, "/project:status", duration_sec=5)

        record_path = create_reproducibility_record(project_dir)
        content = record_path.read_text()

        assert "Session History" in content
        assert "Total Commands" in content


class TestCreateExportManifest:
    """Tests for create_export_manifest function."""

    def test_creates_manifest(self, project_dir):
        """Test that manifest file is created."""
        deliverables = [
            {"filename": "report.pptx", "type": "presentation"}
        ]
        qc_summary = {"all_passed": True, "checks_run": 5}

        manifest_path = create_export_manifest(project_dir, deliverables, qc_summary)

        assert manifest_path.exists()
        assert manifest_path.name == "manifest.json"

    def test_manifest_content(self, project_dir):
        """Test manifest content."""
        deliverables = [
            {"filename": "report.pptx", "type": "presentation", "slides": 15}
        ]
        qc_summary = {"all_passed": True, "checks_run": 5, "warnings": 0}

        manifest_path = create_export_manifest(project_dir, deliverables, qc_summary)
        manifest = json.loads(manifest_path.read_text())

        assert manifest["project_name"] == "test-project"
        assert manifest["template_version"] == "2.0.0"
        assert len(manifest["deliverables"]) == 1
        assert manifest["qc_summary"]["all_passed"] is True
        assert manifest["human_review_required"] is True


class TestFormatCommandHistory:
    """Tests for format_command_history function."""

    def test_empty_history(self):
        """Test formatting empty history."""
        result = format_command_history([])
        assert "No command history" in result

    def test_formats_entries(self, project_dir):
        """Test formatting command entries."""
        log_command(project_dir, "/project:execute", duration_sec=30, result="success")
        history = get_command_history(project_dir)

        result = format_command_history(history)

        assert "[OK]" in result
        assert "/project:execute" in result


class TestFormatExportHistory:
    """Tests for format_export_history function."""

    def test_empty_history(self):
        """Test formatting empty history."""
        result = format_export_history([])
        assert "No export history" in result

    def test_formats_entries(self, project_dir):
        """Test formatting export entries."""
        log_export(project_dir, files=["report.pptx"], qc_passed=True)
        history = get_export_history(project_dir)

        result = format_export_history(history)

        assert "QC:PASS" in result
        assert "report.pptx" in result
