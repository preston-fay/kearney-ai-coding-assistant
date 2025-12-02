# tests/test_state_validator.py
"""Tests for core/state_validator.py"""

import json
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import yaml
from core.state_validator import (
    validate_spec,
    validate_status,
    validate_plan,
    validate_project_state,
    attempt_repair,
    archive_state,
    reset_state,
    list_archives,
    restore_from_archive,
    get_state_summary,
    print_validation_results,
)


@pytest.fixture
def project_dir(tmp_path):
    """Create a basic project directory structure."""
    state_dir = tmp_path / "project_state"
    state_dir.mkdir()
    (state_dir / "spec_history").mkdir()
    (state_dir / "logs").mkdir()
    (state_dir / "logs" / "sessions").mkdir()
    (state_dir / "logs" / "commands").mkdir()
    return tmp_path


@pytest.fixture
def valid_spec(project_dir):
    """Create a valid spec.yaml."""
    spec = {
        "version": 1,
        "meta": {
            "project_name": "test-project",
            "project_type": "analytics",
        },
        "problem": {
            "statement": "Test problem",
        },
    }
    spec_path = project_dir / "project_state" / "spec.yaml"
    spec_path.write_text(yaml.dump(spec))
    return spec_path


@pytest.fixture
def valid_status(project_dir):
    """Create a valid status.json."""
    status = {
        "project_name": "test-project",
        "tasks": [
            {"id": "1.1", "description": "Task 1", "status": "done"},
            {"id": "1.2", "description": "Task 2", "status": "pending"},
        ],
        "artifacts": [],
    }
    status_path = project_dir / "project_state" / "status.json"
    status_path.write_text(json.dumps(status, indent=2))
    return status_path


class TestValidateSpec:
    """Tests for validate_spec function."""

    def test_valid_spec(self, valid_spec):
        """Test validation of valid spec."""
        valid, issues = validate_spec(valid_spec)
        assert valid is True
        assert len(issues) == 0

    def test_missing_spec(self, project_dir):
        """Test validation when spec doesn't exist."""
        spec_path = project_dir / "project_state" / "spec.yaml"
        valid, issues = validate_spec(spec_path)
        assert valid is False
        assert "not found" in issues[0]

    def test_empty_spec(self, project_dir):
        """Test validation of empty spec."""
        spec_path = project_dir / "project_state" / "spec.yaml"
        spec_path.write_text("")
        valid, issues = validate_spec(spec_path)
        assert valid is False
        assert "empty" in issues[0]

    def test_invalid_yaml(self, project_dir):
        """Test validation of invalid YAML."""
        spec_path = project_dir / "project_state" / "spec.yaml"
        spec_path.write_text("invalid: yaml: content:")
        valid, issues = validate_spec(spec_path)
        assert valid is False
        assert "Invalid YAML" in issues[0]

    def test_missing_version(self, project_dir):
        """Test validation when version is missing."""
        spec_path = project_dir / "project_state" / "spec.yaml"
        spec_path.write_text(yaml.dump({"meta": {"project_name": "test", "project_type": "analytics"}}))
        valid, issues = validate_spec(spec_path)
        assert valid is False
        assert any("version" in i for i in issues)

    def test_missing_meta(self, project_dir):
        """Test validation when meta is missing."""
        spec_path = project_dir / "project_state" / "spec.yaml"
        spec_path.write_text(yaml.dump({"version": 1}))
        valid, issues = validate_spec(spec_path)
        assert valid is False
        assert any("meta" in i for i in issues)

    def test_missing_meta_fields(self, project_dir):
        """Test validation when meta fields are missing."""
        spec_path = project_dir / "project_state" / "spec.yaml"
        spec_path.write_text(yaml.dump({"version": 1, "meta": {}}))
        valid, issues = validate_spec(spec_path)
        assert valid is False
        assert any("project_name" in i for i in issues)
        assert any("project_type" in i for i in issues)


class TestValidateStatus:
    """Tests for validate_status function."""

    def test_valid_status(self, valid_status):
        """Test validation of valid status."""
        valid, issues = validate_status(valid_status)
        assert valid is True
        assert len(issues) == 0

    def test_missing_status(self, project_dir):
        """Test validation when status doesn't exist."""
        status_path = project_dir / "project_state" / "status.json"
        valid, issues = validate_status(status_path)
        assert valid is False
        assert "not found" in issues[0]

    def test_empty_status(self, project_dir):
        """Test validation of empty status."""
        status_path = project_dir / "project_state" / "status.json"
        status_path.write_text("")
        valid, issues = validate_status(status_path)
        assert valid is False
        assert "empty" in issues[0]

    def test_invalid_json(self, project_dir):
        """Test validation of invalid JSON."""
        status_path = project_dir / "project_state" / "status.json"
        status_path.write_text("{invalid json}")
        valid, issues = validate_status(status_path)
        assert valid is False
        assert "Invalid JSON" in issues[0]

    def test_missing_project_name(self, project_dir):
        """Test validation when project_name is missing."""
        status_path = project_dir / "project_state" / "status.json"
        status_path.write_text(json.dumps({"tasks": []}))
        valid, issues = validate_status(status_path)
        assert valid is False
        assert any("project_name" in i for i in issues)

    def test_invalid_task_status(self, project_dir):
        """Test validation of invalid task status."""
        status_path = project_dir / "project_state" / "status.json"
        status_path.write_text(json.dumps({
            "project_name": "test",
            "tasks": [{"id": "1.1", "status": "invalid_status"}]
        }))
        valid, issues = validate_status(status_path)
        assert valid is False
        assert any("invalid status" in i for i in issues)

    def test_task_missing_id(self, project_dir):
        """Test validation when task missing id."""
        status_path = project_dir / "project_state" / "status.json"
        status_path.write_text(json.dumps({
            "project_name": "test",
            "tasks": [{"status": "pending"}]
        }))
        valid, issues = validate_status(status_path)
        assert valid is False
        assert any("missing 'id'" in i for i in issues)


class TestValidatePlan:
    """Tests for validate_plan function."""

    def test_missing_plan_is_valid(self, project_dir):
        """Test that missing plan is considered valid (optional)."""
        plan_path = project_dir / "project_state" / "plan.md"
        valid, issues = validate_plan(plan_path)
        assert valid is True

    def test_empty_plan_is_invalid(self, project_dir):
        """Test that empty plan is invalid."""
        plan_path = project_dir / "project_state" / "plan.md"
        plan_path.write_text("")
        valid, issues = validate_plan(plan_path)
        assert valid is False
        assert any("empty" in i for i in issues)

    def test_valid_plan(self, project_dir):
        """Test validation of valid plan."""
        plan_path = project_dir / "project_state" / "plan.md"
        plan_path.write_text("# Execution Plan\n\n## Phase 1")
        valid, issues = validate_plan(plan_path)
        assert valid is True


class TestValidateProjectState:
    """Tests for validate_project_state function."""

    def test_valid_project(self, project_dir, valid_spec, valid_status):
        """Test validation of valid project."""
        valid, results = validate_project_state(project_dir)
        assert valid is True
        assert results["overall"] is True

    def test_missing_state_dir(self, tmp_path):
        """Test validation when state dir missing."""
        valid, results = validate_project_state(tmp_path)
        assert valid is False
        assert "not found" in results["directories"]["issues"][0]

    def test_missing_required_dirs(self, tmp_path):
        """Test validation when required dirs missing."""
        state_dir = tmp_path / "project_state"
        state_dir.mkdir()
        # Create spec and status but not spec_history/logs
        spec = {"version": 1, "meta": {"project_name": "test", "project_type": "analytics"}}
        (state_dir / "spec.yaml").write_text(yaml.dump(spec))
        (state_dir / "status.json").write_text(json.dumps({"project_name": "test"}))

        valid, results = validate_project_state(tmp_path)
        assert results["directories"]["valid"] is False


class TestAttemptRepair:
    """Tests for attempt_repair function."""

    def test_creates_missing_dirs(self, tmp_path):
        """Test that repair creates missing directories."""
        state_dir = tmp_path / "project_state"
        state_dir.mkdir()

        repairs = attempt_repair(tmp_path)

        assert (state_dir / "spec_history").exists()
        assert (state_dir / "logs").exists()
        assert any("spec_history" in r for r in repairs)

    def test_creates_status_from_spec(self, project_dir, valid_spec):
        """Test that repair creates status.json from spec.yaml."""
        repairs = attempt_repair(project_dir)

        status_path = project_dir / "project_state" / "status.json"
        assert status_path.exists()
        assert any("status.json" in r for r in repairs)

        status = json.loads(status_path.read_text())
        assert status["project_name"] == "test-project"

    def test_creates_state_dir_if_missing(self, tmp_path):
        """Test that repair creates project_state/ if missing."""
        repairs = attempt_repair(tmp_path)

        assert (tmp_path / "project_state").exists()
        assert any("project_state" in r for r in repairs)


class TestArchiveState:
    """Tests for archive_state function."""

    def test_creates_archive_dir(self, project_dir, valid_spec, valid_status):
        """Test that archive creates timestamped directory."""
        archive_path = archive_state(project_dir, "Test archive")

        assert archive_path.exists()
        assert (archive_path / "spec.yaml").exists()
        assert (archive_path / "status.json").exists()
        assert (archive_path / "archive_reason.txt").exists()
        assert (archive_path / "archive_metadata.json").exists()

    def test_archive_includes_spec_history(self, project_dir, valid_spec, valid_status):
        """Test that archive includes spec_history."""
        # Add a file to spec_history
        history_file = project_dir / "project_state" / "spec_history" / "spec_v1.yaml"
        history_file.write_text("version: 1")

        archive_path = archive_state(project_dir)

        assert (archive_path / "spec_history" / "spec_v1.yaml").exists()

    def test_archive_metadata(self, project_dir, valid_spec, valid_status):
        """Test that archive metadata is correct."""
        archive_path = archive_state(project_dir, "Test reason")

        metadata = json.loads((archive_path / "archive_metadata.json").read_text())
        assert metadata["reason"] == "Test reason"
        assert "archived_at" in metadata


class TestResetState:
    """Tests for reset_state function."""

    def test_reset_archives_and_clears(self, project_dir, valid_spec, valid_status):
        """Test that reset archives current state and clears files."""
        result = reset_state(project_dir, "Test reset")

        assert result["reset_complete"] is True
        assert result["archive_path"] is not None

        # State files should be removed
        assert not (project_dir / "project_state" / "spec.yaml").exists()
        assert not (project_dir / "project_state" / "status.json").exists()

        # Archive should exist
        archive_base = project_dir / "project_state" / "archive"
        assert any(archive_base.iterdir())


class TestListArchives:
    """Tests for list_archives function."""

    def test_empty_archives(self, project_dir):
        """Test listing when no archives."""
        archives = list_archives(project_dir)
        assert archives == []

    def test_lists_archives(self, project_dir, valid_spec, valid_status):
        """Test listing archives."""
        # Create an archive
        archive_state(project_dir, "First archive")

        archives = list_archives(project_dir)

        assert len(archives) == 1
        assert archives[0]["reason"] == "First archive"


class TestRestoreFromArchive:
    """Tests for restore_from_archive function."""

    def test_restore_from_archive(self, project_dir, valid_spec, valid_status):
        """Test restoring from archive."""
        # Create archive
        archive_path = archive_state(project_dir, "Original state")
        archive_name = archive_path.name

        # Clear current state
        (project_dir / "project_state" / "spec.yaml").unlink()

        # Restore
        result = restore_from_archive(project_dir, archive_name)

        assert result["restored"] is True
        assert (project_dir / "project_state" / "spec.yaml").exists()

    def test_restore_nonexistent_archive(self, project_dir):
        """Test restoring from non-existent archive."""
        result = restore_from_archive(project_dir, "nonexistent")

        assert result["restored"] is False
        assert "not found" in result["message"]

    def test_restore_archives_current_first(self, project_dir, valid_spec, valid_status):
        """Test that restore archives current state first."""
        # Create first archive
        archive_path = archive_state(project_dir, "Original")
        archive_name = archive_path.name

        # Restore (should create safety backup)
        result = restore_from_archive(project_dir, archive_name)

        assert result["current_archived_to"] is not None
        archives = list_archives(project_dir)
        assert len(archives) >= 2


class TestGetStateSummary:
    """Tests for get_state_summary function."""

    def test_summary_with_full_state(self, project_dir, valid_spec, valid_status):
        """Test summary with full project state."""
        summary = get_state_summary(project_dir)

        assert summary["has_spec"] is True
        assert summary["has_status"] is True
        assert summary["project_name"] == "test-project"
        assert summary["spec_version"] == 1
        assert summary["tasks_total"] == 2
        assert summary["tasks_done"] == 1

    def test_summary_empty_project(self, project_dir):
        """Test summary with empty project."""
        summary = get_state_summary(project_dir)

        assert summary["has_spec"] is False
        assert summary["has_status"] is False
        assert summary["tasks_total"] == 0


class TestPrintValidationResults:
    """Tests for print_validation_results function."""

    def test_prints_without_error(self, project_dir, valid_spec, valid_status, capsys):
        """Test that print doesn't error."""
        valid, results = validate_project_state(project_dir)
        print_validation_results(results)

        captured = capsys.readouterr()
        assert "PROJECT STATE VALIDATION" in captured.out
        assert "VALID" in captured.out
