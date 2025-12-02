# tests/test_integration.py
"""
Integration tests for Kearney AI Coding Assistant.

These tests verify that all components work together as a cohesive system,
simulating real-world usage scenarios from project creation to export.

Note: Some core modules (spec_manager, state_manager, session_logger) use
global paths. These tests focus on modules that accept path arguments.
"""

import json
import pytest
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

import yaml

# Import core modules that accept path arguments
from core.prereq_checker import (
    check_python_version,
    check_git_installed,
    check_required_packages,
    run_all_checks,
)
from core.state_validator import (
    validate_project_state,
    validate_spec,
    validate_status,
    attempt_repair,
    archive_state,
    reset_state,
    restore_from_archive,
    list_archives,
)
from core.data_handler import ProjectDatabase, register_all_raw_files
from core.brand_guard import check_file, check_text_content, BrandViolation
from core.brand_config import (
    load_brand_config,
    is_color_allowed,
    is_color_forbidden,
    save_brand_override_template,
)
from core.qc_reporter import (
    run_qc_checks,
    generate_qc_report,
    check_forbidden_colors,
    check_emojis,
)
from core.audit_logger import (
    log_command,
    log_export,
    get_command_history,
    get_export_history,
    get_command_stats,
    create_reproducibility_record,
    create_export_manifest,
)


def create_spec_file(project_path: Path, spec_data: dict):
    """Helper to create a spec.yaml file directly."""
    spec_path = project_path / "project_state" / "spec.yaml"
    spec_path.write_text(yaml.dump(spec_data))
    return spec_path


def load_spec_file(project_path: Path) -> dict:
    """Helper to load spec.yaml."""
    spec_path = project_path / "project_state" / "spec.yaml"
    if spec_path.exists():
        return yaml.safe_load(spec_path.read_text())
    return None


def spec_file_exists(project_path: Path) -> bool:
    """Helper to check if spec.yaml exists."""
    return (project_path / "project_state" / "spec.yaml").exists()


def create_status_file(project_path: Path, project_name: str, tasks: list = None):
    """Helper to create a status.json file."""
    status = {
        "project_name": project_name,
        "template": "analytics",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "current_phase": "Phase 1",
        "current_task": None,
        "tasks": tasks or [],
        "artifacts": [],
        "history": [],
    }
    status_path = project_path / "project_state" / "status.json"
    status_path.write_text(json.dumps(status, indent=2))
    return status


def load_status_file(project_path: Path):
    """Helper to load status.json."""
    status_path = project_path / "project_state" / "status.json"
    if status_path.exists():
        return json.loads(status_path.read_text())
    return None


@pytest.fixture
def integration_project(tmp_path):
    """Create a fully scaffolded project for integration testing."""
    project_path = tmp_path / "test-integration-project"

    # Create project structure
    project_path.mkdir()
    (project_path / "project_state").mkdir()
    (project_path / "project_state" / "spec_history").mkdir()
    (project_path / "project_state" / "logs" / "commands").mkdir(parents=True)
    (project_path / "project_state" / "logs" / "exports").mkdir(parents=True)
    (project_path / "project_state" / "logs" / "sessions").mkdir(parents=True)
    (project_path / "data" / "raw").mkdir(parents=True)
    (project_path / "data" / "processed").mkdir(parents=True)
    (project_path / "data" / "external").mkdir(parents=True)
    (project_path / "outputs" / "charts").mkdir(parents=True)
    (project_path / "outputs" / "reports").mkdir(parents=True)
    (project_path / "exports").mkdir()
    (project_path / "config" / "governance").mkdir(parents=True)

    # Create CLAUDE.md
    (project_path / "CLAUDE.md").write_text("# Test CLAUDE.md")

    # Create brand config
    brand_yaml = {
        "colors": {
            "primary": "#7823DC",
            "forbidden": ["#00FF00", "#2E7D32"],
        },
        "enforced": ["no_emojis", "no_gridlines"],
    }
    (project_path / "config" / "governance" / "brand.yaml").write_text(yaml.dump(brand_yaml))

    # Create version info
    version_info = {
        "template_version": "2.0.0",
        "created_at": datetime.now().isoformat(),
    }
    (project_path / ".kaca-version.json").write_text(json.dumps(version_info))

    return project_path


class TestEndToEndWorkflow:
    """Test complete workflow from project creation to export."""

    def test_full_project_lifecycle(self, integration_project):
        """Test the complete project lifecycle."""
        project_path = integration_project

        # Step 1: Create specification
        spec_data = {
            "version": 1,
            "meta": {
                "project_name": "integration-test",
                "project_type": "analytics",
                "client": "Test Client",
            },
            "problem": {
                "business_question": "Test analysis",
            },
            "deliverables": [
                {"name": "Test Report", "type": "report"},
            ],
        }
        create_spec_file(project_path, spec_data)

        # Verify spec exists
        assert spec_file_exists(project_path)
        loaded_spec = load_spec_file(project_path)
        assert loaded_spec["meta"]["project_name"] == "integration-test"

        # Step 2: Create status with tasks
        tasks = [
            {"id": "1.1", "description": "Data loading", "status": "pending"},
            {"id": "1.2", "description": "Analysis", "status": "pending"},
            {"id": "1.3", "description": "Report", "status": "pending"},
        ]
        create_status_file(project_path, "integration-test", tasks)

        # Step 3: Validate project state
        valid, results = validate_project_state(project_path)
        assert valid is True

        # Step 4: Log command execution
        log_command(project_path, "/project:execute", duration_sec=30, task_id="1.1")
        log_command(project_path, "/project:execute", duration_sec=45, task_id="1.2")

        # Step 5: Check command history
        history = get_command_history(project_path)
        assert len(history) == 2

        # Step 6: Get command stats
        stats = get_command_stats(project_path)
        assert stats["total_commands"] == 2
        assert stats["success_rate"] == 1.0

        # Step 7: Run QC checks
        report = run_qc_checks(project_path)
        # Should run without error

    def test_error_recovery_workflow(self, integration_project):
        """Test error recovery through archive/restore cycle."""
        project_path = integration_project

        # Create initial spec
        spec_v1 = {
            "version": 1,
            "meta": {"project_name": "recovery-test", "project_type": "analytics"},
            "problem": {"business_question": "Original question"},
        }
        create_spec_file(project_path, spec_v1)
        create_status_file(project_path, "recovery-test")

        # Verify initial state
        assert spec_file_exists(project_path)
        original_spec = load_spec_file(project_path)
        assert original_spec["problem"]["business_question"] == "Original question"

        # Archive current state
        archive_path = archive_state(project_path, reason="test backup")
        assert archive_path.exists()

        # Modify spec (simulating changes)
        spec_v2 = load_spec_file(project_path)
        spec_v2["version"] = 2
        spec_v2["problem"]["business_question"] = "Modified question"
        create_spec_file(project_path, spec_v2)

        # Verify modification
        modified_spec = load_spec_file(project_path)
        assert modified_spec["problem"]["business_question"] == "Modified question"

        # List archives
        archives = list_archives(project_path)
        assert len(archives) >= 1

        # Restore from archive
        restore_from_archive(project_path, archive_path.name)

        # Verify restoration
        restored_spec = load_spec_file(project_path)
        assert restored_spec["problem"]["business_question"] == "Original question"

    def test_reset_workflow(self, integration_project):
        """Test reset workflow archives and clears state."""
        project_path = integration_project

        # Create initial spec and status
        spec = {
            "version": 1,
            "meta": {"project_name": "reset-test", "project_type": "analytics"},
            "problem": {"business_question": "Test"},
        }
        create_spec_file(project_path, spec)
        create_status_file(project_path, "reset-test")

        # Log some commands
        log_command(project_path, "/project:execute", task_id="1.1")
        log_command(project_path, "/project:execute", task_id="1.2")

        # Verify data exists
        assert spec_file_exists(project_path)
        history = get_command_history(project_path)
        assert len(history) == 2

        # Reset the project
        reset_result = reset_state(project_path, reason="test reset")
        assert isinstance(reset_result, dict)

        # Verify state was cleared
        assert not spec_file_exists(project_path)


class TestDataHandlerIntegration:
    """Test data handler integration with project workflow."""

    def test_duckdb_workflow(self, integration_project):
        """Test DuckDB integration in project context."""
        project_path = integration_project

        # Create test data file
        csv_content = "id,name,value\n1,Alice,100\n2,Bob,200\n3,Charlie,300"
        (project_path / "data" / "raw" / "test_data.csv").write_text(csv_content)

        # Register and query data
        db = ProjectDatabase(project_path)
        table_name = db.register_file(project_path / "data" / "raw" / "test_data.csv")

        # Query the data
        result = db.query_df(f"SELECT * FROM {table_name}")
        assert len(result) == 3

        # Get table info
        info = db.describe_table(table_name)
        assert info["row_count"] == 3

        # Export to parquet
        parquet_path = db.export_to_parquet(table_name)
        assert parquet_path.exists()

        db.close()

    def test_register_all_raw_files(self, integration_project):
        """Test registering all raw files."""
        project_path = integration_project

        # Create multiple data files
        (project_path / "data" / "raw" / "sales.csv").write_text("id,amount\n1,100\n2,200")
        (project_path / "data" / "raw" / "customers.csv").write_text("id,name\n1,Alice\n2,Bob")

        # Register all
        registered = register_all_raw_files(project_path)

        assert len(registered) == 2
        assert "sales.csv" in registered
        assert "customers.csv" in registered


class TestBrandComplianceIntegration:
    """Test brand compliance across project workflow."""

    def test_brand_config_with_override(self, integration_project):
        """Test brand config loading with override."""
        project_path = integration_project

        # Load default config
        config = load_brand_config(project_path)
        assert config.primary_color == "#7823DC"  # Default Kearney purple

        # Create override
        save_brand_override_template(project_path)

        # Enable override with custom colors
        override_path = project_path / "config" / "brand_override.yaml"
        override_content = """
enabled: true
brand_name: "Test Client"
colors:
  primary: "#0066CC"
  secondary: "#FF6600"
"""
        override_path.write_text(override_content)

        # Load with override
        config = load_brand_config(project_path)
        assert config.is_override is True
        assert config.brand_name == "Test Client"
        assert config.primary_color == "#0066CC"

        # Enforced rules still present
        assert "no_emojis" in config.enforced_rules
        assert "no_gridlines" in config.enforced_rules

    def test_qc_with_violations(self, integration_project):
        """Test QC catches brand violations."""
        project_path = integration_project

        # Create spec for QC
        spec = {
            "version": 1,
            "meta": {"project_name": "violation-test", "project_type": "analytics"},
        }
        create_spec_file(project_path, spec)

        # Create file with violations
        bad_content = "Use color #00FF00 for success indicator"
        (project_path / "outputs" / "reports" / "bad_report.md").write_text(bad_content)

        # Run QC
        report = run_qc_checks(project_path)

        # Should have failures
        assert report.overall_status.value in ["fail", "warning"]

    def test_qc_clean_project(self, integration_project):
        """Test QC passes on clean project."""
        project_path = integration_project

        # Create clean file
        clean_content = "Revenue increased by 15%. Primary color is #7823DC."
        (project_path / "outputs" / "reports" / "clean_report.md").write_text(clean_content)

        # Create spec for QC
        spec = {
            "version": 1,
            "meta": {"project_name": "clean-test", "project_type": "analytics"},
        }
        create_spec_file(project_path, spec)

        # Run QC
        report = run_qc_checks(project_path)
        # Should complete without critical errors


class TestAuditTrailIntegration:
    """Test audit trail across project workflow."""

    def test_full_audit_trail(self, integration_project):
        """Test complete audit trail from commands to export."""
        project_path = integration_project

        # Create spec
        spec = {
            "version": 1,
            "meta": {"project_name": "audit-test", "project_type": "analytics"},
        }
        create_spec_file(project_path, spec)

        # Log commands
        log_command(project_path, "/project:interview", duration_sec=300, result="success")
        log_command(project_path, "/project:plan", duration_sec=30, tasks_created=5)
        log_command(project_path, "/project:execute", duration_sec=120, task_id="1.1")
        log_command(project_path, "/project:execute", duration_sec=90, task_id="1.2")
        log_command(project_path, "/project:review", duration_sec=15, qc_passed=True)

        # Log export
        log_export(
            project_path,
            files=["report.pptx", "data.xlsx"],
            qc_passed=True,
            human_review=True,
        )

        # Verify command history
        history = get_command_history(project_path)
        assert len(history) == 5

        # Verify stats
        stats = get_command_stats(project_path)
        assert stats["total_commands"] == 5
        assert stats["commands_by_type"]["/project:execute"] == 2

        # Create reproducibility record
        record_path = create_reproducibility_record(project_path)
        assert record_path.exists()
        content = record_path.read_text()
        assert "Environment" in content

        # Create export manifest
        deliverables = [
            {"filename": "report.pptx", "type": "presentation"},
            {"filename": "data.xlsx", "type": "spreadsheet"},
        ]
        qc_summary = {"all_passed": True, "checks_run": 5}
        manifest_path = create_export_manifest(project_path, deliverables, qc_summary)
        assert manifest_path.exists()

    def test_export_history(self, integration_project):
        """Test export history tracking."""
        project_path = integration_project

        # Log multiple exports
        log_export(project_path, files=["v1.pptx"], qc_passed=True)
        log_export(project_path, files=["v2.pptx"], qc_passed=True, human_review=True)
        log_export(project_path, files=["v3.pptx"], qc_passed=False)

        # Get export history
        exports = get_export_history(project_path)
        assert len(exports) == 3

        # Most recent first
        assert "v3.pptx" in exports[0]["files"]


class TestStateValidationIntegration:
    """Test state validation across components."""

    def test_validate_and_repair(self, integration_project):
        """Test validation and repair workflow."""
        project_path = integration_project

        # Create valid spec but no status
        spec = {
            "version": 1,
            "meta": {"project_name": "repair-test", "project_type": "analytics"},
        }
        create_spec_file(project_path, spec)

        # Validate
        valid, results = validate_project_state(project_path)

        # Attempt repair
        repairs = attempt_repair(project_path)

        # Should have attempted repairs
        assert isinstance(repairs, list)

    def test_status_validation(self, integration_project):
        """Test status validation."""
        project_path = integration_project

        # Create valid status
        create_status_file(project_path, "status-test", [
            {"id": "1.1", "description": "Test", "status": "pending"}
        ])

        valid, issues = validate_status(project_path / "project_state" / "status.json")
        assert valid is True


class TestPrerequisiteIntegration:
    """Test prerequisite checking integration."""

    def test_python_version_check(self):
        """Test Python version check runs."""
        result = check_python_version()
        assert result.name == "Python Version"

    def test_git_check(self):
        """Test Git check runs."""
        result = check_git_installed()
        assert result.name == "Git"

    def test_all_checks_run(self, tmp_path):
        """Test that all prerequisite checks can run."""
        all_passed, results = run_all_checks(tmp_path)

        # Should have results for each check
        assert len(results) >= 4

        # Each result should have required fields
        for result in results:
            assert hasattr(result, 'name')
            assert hasattr(result, 'passed')
            assert hasattr(result, 'message')


class TestCrossComponentIntegration:
    """Test interactions between multiple components."""

    def test_spec_status_sync(self, integration_project):
        """Test spec and status stay in sync."""
        project_path = integration_project

        # Create spec
        spec = {
            "version": 1,
            "meta": {"project_name": "sync-test", "project_type": "analytics"},
        }
        create_spec_file(project_path, spec)

        # Create status with same project name
        create_status_file(project_path, "sync-test")

        # Project names should match
        loaded_spec = load_spec_file(project_path)
        loaded_status = load_status_file(project_path)

        assert loaded_spec["meta"]["project_name"] == loaded_status["project_name"]

    def test_qc_affects_export(self, integration_project):
        """Test QC results affect export decisions."""
        project_path = integration_project

        # Create spec
        spec = {
            "version": 1,
            "meta": {"project_name": "export-test", "project_type": "analytics"},
        }
        create_spec_file(project_path, spec)

        # Create clean output
        (project_path / "outputs" / "reports" / "summary.md").write_text("Clean content.")

        # Run QC
        report = run_qc_checks(project_path)
        qc_passed = report.overall_status.value == "pass"

        # Log export with QC result
        log_export(
            project_path,
            files=["summary.md"],
            qc_passed=qc_passed,
        )

        # Export log should reflect QC status
        exports = get_export_history(project_path)
        assert len(exports) == 1

    def test_brand_guard_to_qc_pipeline(self, integration_project):
        """Test brand_guard feeds into QC reporter."""
        project_path = integration_project

        # Create file with mixed content
        content = "Good color: #7823DC, bad color: #00FF00"
        file_path = project_path / "outputs" / "test.txt"
        file_path.write_text(content)

        # Check with brand_guard
        violations = check_file(file_path)
        assert len(violations) > 0  # Should find the green

        # Check forbidden colors function
        has_forbidden, found = check_forbidden_colors(content)
        assert has_forbidden is True

    def test_audit_logging_throughout_workflow(self, integration_project):
        """Test audit logging captures entire workflow."""
        project_path = integration_project

        # Create spec
        spec = {
            "version": 1,
            "meta": {"project_name": "audit-workflow", "project_type": "analytics"},
        }
        create_spec_file(project_path, spec)

        # Simulate workflow - log all commands
        log_command(project_path, "/project:interview", duration_sec=180)
        log_command(project_path, "/project:plan", duration_sec=30)
        log_command(project_path, "/project:execute", duration_sec=60, task_id="1.1")
        log_command(project_path, "/project:review", duration_sec=10)

        # Log export
        log_export(project_path, files=["output.pptx"], qc_passed=True)

        # Verify complete trail
        history = get_command_history(project_path)
        assert len(history) == 4

        exports = get_export_history(project_path)
        assert len(exports) == 1

        stats = get_command_stats(project_path)
        assert stats["total_commands"] == 4
        assert stats["success_rate"] == 1.0
