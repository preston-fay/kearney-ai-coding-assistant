# tests/test_qc_reporter.py
"""Tests for core/qc_reporter.py"""

import json
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import yaml
from core.qc_reporter import (
    CheckStatus,
    CheckResult,
    QCReport,
    check_forbidden_colors,
    check_emojis,
    check_gridlines_in_code,
    check_pii,
    check_file_brand_compliance,
    check_data_compliance,
    check_outputs,
    run_qc_checks,
    generate_recommendations,
    generate_qc_report,
    print_qc_summary,
    get_human_approval_warning,
    get_post_export_checklist,
)


class TestCheckStatus:
    """Tests for CheckStatus enum."""

    def test_status_values(self):
        """Test status enum values."""
        assert CheckStatus.PASS.value == "pass"
        assert CheckStatus.WARNING.value == "warning"
        assert CheckStatus.FAIL.value == "fail"
        assert CheckStatus.SKIPPED.value == "skipped"


class TestCheckResult:
    """Tests for CheckResult dataclass."""

    def test_check_result_creation(self):
        """Test creating a check result."""
        result = CheckResult(
            name="Test Check",
            status=CheckStatus.PASS,
            message="All good"
        )
        assert result.name == "Test Check"
        assert result.status == CheckStatus.PASS
        assert result.file_path is None

    def test_check_result_with_file(self):
        """Test check result with file path."""
        result = CheckResult(
            name="Test",
            status=CheckStatus.FAIL,
            message="Error",
            file_path="outputs/test.py"
        )
        assert result.file_path == "outputs/test.py"


class TestQCReport:
    """Tests for QCReport dataclass."""

    def test_report_creation(self):
        """Test creating a report."""
        report = QCReport(
            project_name="test-project",
            generated_at="2025-12-01T12:00:00",
            overall_status=CheckStatus.PASS
        )
        assert report.project_name == "test-project"
        assert len(report.brand_checks) == 0
        assert len(report.recommendations) == 0

    def test_report_to_dict(self):
        """Test converting report to dict."""
        report = QCReport(
            project_name="test",
            generated_at="2025-12-01T12:00:00",
            overall_status=CheckStatus.WARNING
        )
        report.brand_checks.append(CheckResult(
            name="Colors",
            status=CheckStatus.PASS,
            message="OK"
        ))

        data = report.to_dict()

        assert data["project_name"] == "test"
        assert data["overall_status"] == "warning"
        assert len(data["brand_checks"]) == 1


class TestCheckForbiddenColors:
    """Tests for check_forbidden_colors function."""

    def test_no_forbidden_colors(self):
        """Test content with no forbidden colors."""
        content = "color = '#7823DC'"
        has_forbidden, found = check_forbidden_colors(content)
        assert has_forbidden is False
        assert len(found) == 0

    def test_finds_green_hex(self):
        """Test detecting forbidden green colors."""
        content = "color = '#00FF00'"
        has_forbidden, found = check_forbidden_colors(content)
        assert has_forbidden is True
        assert "#00FF00" in found or "#00ff00" in [f.lower() for f in found]

    def test_finds_material_green(self):
        """Test detecting material design green."""
        content = "primary_color = '#2E7D32'"
        has_forbidden, found = check_forbidden_colors(content)
        assert has_forbidden is True

    def test_case_insensitive(self):
        """Test color detection is case insensitive."""
        content = "color = '#00ff00'"
        has_forbidden, found = check_forbidden_colors(content)
        assert has_forbidden is True


class TestCheckEmojis:
    """Tests for check_emojis function."""

    def test_no_emojis(self):
        """Test content with no emojis."""
        content = "This is plain text with no emojis."
        has_emojis, found = check_emojis(content)
        assert has_emojis is False

    def test_finds_emoji(self):
        """Test detecting emojis."""
        content = "Great job! :)"  # Note: :) is not an emoji
        has_emojis, found = check_emojis(content)
        assert has_emojis is False  # :) is not a unicode emoji

    def test_finds_unicode_emoji(self):
        """Test detecting unicode emojis."""
        content = "Great job! \U0001F600"  # Grinning face emoji
        has_emojis, found = check_emojis(content)
        assert has_emojis is True


class TestCheckGridlines:
    """Tests for check_gridlines_in_code function."""

    def test_no_gridlines(self):
        """Test code without gridlines."""
        content = """
import matplotlib.pyplot as plt
fig, ax = plt.subplots()
ax.bar([1, 2, 3], [4, 5, 6])
plt.show()
"""
        assert check_gridlines_in_code(content) is False

    def test_finds_grid_true(self):
        """Test detecting grid(True)."""
        content = "ax.grid(True)"
        assert check_gridlines_in_code(content) is True

    def test_finds_grid_empty(self):
        """Test detecting grid() with no args."""
        content = "ax.grid()"
        assert check_gridlines_in_code(content) is True

    def test_finds_plt_grid(self):
        """Test detecting plt.grid()."""
        content = "plt.grid(True)"
        assert check_gridlines_in_code(content) is True


class TestCheckPII:
    """Tests for check_pii function."""

    def test_no_pii(self):
        """Test content with no PII."""
        content = "Revenue was $1.2M in Q4."
        has_pii, found = check_pii(content)
        assert has_pii is False

    def test_finds_email(self):
        """Test detecting email addresses."""
        content = "Contact: john.doe@example.com"
        has_pii, found = check_pii(content)
        assert has_pii is True
        assert "email" in found

    def test_finds_phone(self):
        """Test detecting phone numbers."""
        content = "Call: 555-123-4567"
        has_pii, found = check_pii(content)
        assert has_pii is True
        assert "phone" in found

    def test_finds_ssn(self):
        """Test detecting SSN patterns."""
        content = "SSN: 123-45-6789"
        has_pii, found = check_pii(content)
        assert has_pii is True
        assert "ssn" in found

    def test_finds_credit_card(self):
        """Test detecting credit card numbers."""
        content = "Card: 1234-5678-9012-3456"
        has_pii, found = check_pii(content)
        assert has_pii is True
        assert "credit_card" in found


class TestCheckFileBrandCompliance:
    """Tests for check_file_brand_compliance function."""

    def test_compliant_file(self, tmp_path):
        """Test checking a compliant file."""
        file_path = tmp_path / "test.md"
        file_path.write_text("# Report\n\nThis is a clean report.")

        results = check_file_brand_compliance(file_path)

        # Should have checks for colors and emojis
        assert len(results) >= 2
        assert all(r.status == CheckStatus.PASS for r in results)

    def test_file_with_forbidden_colors(self, tmp_path):
        """Test file with forbidden colors."""
        file_path = tmp_path / "test.md"
        file_path.write_text("Use color #00FF00 for success")

        results = check_file_brand_compliance(file_path)

        color_check = next(r for r in results if r.name == "Forbidden Colors")
        assert color_check.status == CheckStatus.FAIL

    def test_python_file_with_gridlines(self, tmp_path):
        """Test Python file with gridlines."""
        file_path = tmp_path / "chart.py"
        file_path.write_text("ax.grid(True)")

        results = check_file_brand_compliance(file_path)

        grid_check = next(r for r in results if r.name == "Gridlines")
        assert grid_check.status == CheckStatus.FAIL


@pytest.fixture
def project_dir(tmp_path):
    """Create a project directory structure."""
    # Create directories
    (tmp_path / "project_state").mkdir()
    (tmp_path / "outputs" / "charts").mkdir(parents=True)
    (tmp_path / "outputs" / "reports").mkdir(parents=True)
    (tmp_path / "exports").mkdir()
    (tmp_path / "data" / "raw").mkdir(parents=True)

    # Create spec
    spec = {
        "version": 1,
        "meta": {
            "project_name": "test-project",
            "project_type": "analytics"
        }
    }
    (tmp_path / "project_state" / "spec.yaml").write_text(yaml.dump(spec))

    return tmp_path


class TestCheckDataCompliance:
    """Tests for check_data_compliance function."""

    def test_clean_outputs(self, project_dir):
        """Test project with clean outputs."""
        # Create a clean output file
        (project_dir / "outputs" / "reports" / "summary.md").write_text(
            "# Summary\n\nRevenue increased by 15%."
        )

        results = check_data_compliance(project_dir)

        pii_check = next((r for r in results if r.name == "PII Detection"), None)
        assert pii_check is not None
        assert pii_check.status == CheckStatus.PASS

    def test_outputs_with_pii(self, project_dir):
        """Test project with PII in outputs."""
        (project_dir / "outputs" / "reports" / "contacts.csv").write_text(
            "name,email\nJohn,john@example.com"
        )

        results = check_data_compliance(project_dir)

        pii_check = next((r for r in results if r.name == "PII Detection"), None)
        assert pii_check is not None
        assert pii_check.status == CheckStatus.WARNING

    def test_raw_data_in_exports(self, project_dir):
        """Test detecting raw data in exports."""
        # Create raw file
        (project_dir / "data" / "raw" / "sales.csv").write_text("data")
        # Copy to exports (bad practice)
        (project_dir / "exports" / "sales.csv").write_text("data")

        results = check_data_compliance(project_dir)

        exposure_check = next((r for r in results if r.name == "Raw Data Exposure"), None)
        assert exposure_check is not None
        assert exposure_check.status == CheckStatus.FAIL


class TestRunQCChecks:
    """Tests for run_qc_checks function."""

    def test_run_on_clean_project(self, project_dir):
        """Test running QC on clean project."""
        report = run_qc_checks(project_dir)

        assert report.project_name == "test-project"
        assert report.overall_status == CheckStatus.PASS

    def test_run_detects_issues(self, project_dir):
        """Test running QC detects issues."""
        # Add file with forbidden color
        (project_dir / "outputs" / "reports" / "bad.md").write_text(
            "Use color #00FF00"
        )

        report = run_qc_checks(project_dir)

        assert report.overall_status == CheckStatus.FAIL


class TestGenerateRecommendations:
    """Tests for generate_recommendations function."""

    def test_recommendations_for_colors(self):
        """Test recommendations for color issues."""
        report = QCReport(
            project_name="test",
            generated_at="2025-12-01",
            overall_status=CheckStatus.FAIL
        )
        report.brand_checks.append(CheckResult(
            name="Forbidden Colors",
            status=CheckStatus.FAIL,
            message="Found green"
        ))

        recs = generate_recommendations(report)

        assert any("green" in r.lower() or "purple" in r.lower() for r in recs)

    def test_recommendations_for_emojis(self):
        """Test recommendations for emoji issues."""
        report = QCReport(
            project_name="test",
            generated_at="2025-12-01",
            overall_status=CheckStatus.FAIL
        )
        report.brand_checks.append(CheckResult(
            name="Emojis",
            status=CheckStatus.FAIL,
            message="Found emojis"
        ))

        recs = generate_recommendations(report)

        assert any("emoji" in r.lower() for r in recs)


class TestGenerateQCReport:
    """Tests for generate_qc_report function."""

    def test_generates_report_files(self, project_dir):
        """Test that report files are generated."""
        report_path = generate_qc_report(project_dir)

        assert report_path.exists()
        assert report_path.suffix == ".md"

        # JSON should also exist
        json_path = report_path.with_suffix(".json")
        assert json_path.exists()

    def test_report_contains_project_name(self, project_dir):
        """Test that report contains project name."""
        report_path = generate_qc_report(project_dir)

        content = report_path.read_text()
        assert "test-project" in content


class TestPrintQCSummary:
    """Tests for print_qc_summary function."""

    def test_prints_without_error(self, capsys):
        """Test that print doesn't error."""
        report = QCReport(
            project_name="test",
            generated_at="2025-12-01",
            overall_status=CheckStatus.PASS
        )

        print_qc_summary(report)

        captured = capsys.readouterr()
        assert "QUALITY CONTROL" in captured.out
        assert "test" in captured.out


class TestHumanApprovalWarning:
    """Tests for get_human_approval_warning function."""

    def test_warning_includes_deliverables(self):
        """Test warning includes deliverable list."""
        warning = get_human_approval_warning([
            "report.pptx",
            "analysis.xlsx"
        ])

        assert "report.pptx" in warning
        assert "analysis.xlsx" in warning
        assert "HUMAN REVIEW" in warning


class TestPostExportChecklist:
    """Tests for get_post_export_checklist function."""

    def test_checklist_content(self):
        """Test checklist contains key items."""
        checklist = get_post_export_checklist()

        assert "accuracy" in checklist.lower()
        assert "sensitive data" in checklist.lower()
        assert "brand" in checklist.lower()
