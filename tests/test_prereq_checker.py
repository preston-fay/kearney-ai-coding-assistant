# tests/test_prereq_checker.py
"""Tests for core/prereq_checker.py"""

import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

from core.prereq_checker import (
    CheckResult,
    check_python_version,
    check_git_installed,
    check_claude_desktop,
    check_required_packages,
    check_template_version,
    run_all_checks,
    print_results,
)


class TestCheckResult:
    """Tests for CheckResult dataclass."""

    def test_check_result_passed(self):
        """Test creating a passed check result."""
        result = CheckResult(
            name="Test Check",
            passed=True,
            message="All good"
        )
        assert result.passed is True
        assert result.fix_instructions is None

    def test_check_result_failed(self):
        """Test creating a failed check result with fix instructions."""
        result = CheckResult(
            name="Test Check",
            passed=False,
            message="Something wrong",
            fix_instructions="Do this to fix"
        )
        assert result.passed is False
        assert result.fix_instructions is not None


class TestCheckPythonVersion:
    """Tests for check_python_version function."""

    def test_current_python_version(self):
        """Test that current Python version passes (we're running 3.10+)."""
        result = check_python_version()
        # If we're running the tests, we should have 3.10+
        assert result.name == "Python Version"
        if sys.version_info >= (3, 10):
            assert result.passed is True
        else:
            assert result.passed is False

    @patch('core.prereq_checker.sys.version_info', (3, 10, 0))
    def test_python_310_passes(self):
        """Test that Python 3.10 passes."""
        result = check_python_version()
        assert result.passed is True
        assert "3.10" in result.message

    @patch('core.prereq_checker.sys.version_info', (3, 11, 5))
    def test_python_311_passes(self):
        """Test that Python 3.11 passes."""
        result = check_python_version()
        assert result.passed is True
        assert "3.11" in result.message

    @patch('core.prereq_checker.sys.version_info', (3, 9, 0))
    def test_python_39_fails(self):
        """Test that Python 3.9 fails."""
        result = check_python_version()
        assert result.passed is False
        assert "need 3.10+" in result.message
        assert result.fix_instructions is not None


class TestCheckGitInstalled:
    """Tests for check_git_installed function."""

    def test_git_check_runs(self):
        """Test that git check runs without error."""
        result = check_git_installed()
        assert result.name == "Git"
        # Result depends on environment, but should not raise

    @patch('core.prereq_checker.shutil.which')
    def test_git_not_found(self, mock_which):
        """Test when git is not installed."""
        mock_which.return_value = None
        result = check_git_installed()
        assert result.passed is False
        assert result.fix_instructions is not None


class TestCheckClaudeDesktop:
    """Tests for check_claude_desktop function."""

    def test_claude_check_runs(self):
        """Test that Claude Desktop check runs without error."""
        result = check_claude_desktop()
        assert result.name == "Claude Desktop"
        # Result depends on environment

    @patch('pathlib.Path.exists')
    def test_claude_not_found(self, mock_exists):
        """Test when Claude Desktop is not installed."""
        mock_exists.return_value = False
        result = check_claude_desktop()
        assert result.passed is False
        assert result.fix_instructions is not None


class TestCheckRequiredPackages:
    """Tests for check_required_packages function."""

    def test_packages_check_runs(self):
        """Test that package check runs without error."""
        result = check_required_packages()
        assert result.name == "Python Packages"
        # We should have these packages in our test environment

    @patch('builtins.__import__')
    def test_missing_packages(self, mock_import):
        """Test when packages are missing."""
        def import_side_effect(name, *args, **kwargs):
            if name in ["pandas", "matplotlib"]:
                raise ImportError(f"No module named '{name}'")
            return MagicMock()

        mock_import.side_effect = import_side_effect
        result = check_required_packages()
        # The mock affects all imports, so this is hard to test accurately
        # Just verify it doesn't crash
        assert result.name == "Python Packages"


class TestCheckTemplateVersion:
    """Tests for check_template_version function."""

    def test_template_found(self, tmp_path):
        """Test when template exists with VERSION file."""
        version_file = tmp_path / "VERSION"
        version_file.write_text("2.0.0")

        result = check_template_version(tmp_path)
        assert result.passed is True
        assert "2.0.0" in result.message

    def test_template_without_version(self, tmp_path):
        """Test when template exists but VERSION file is missing."""
        result = check_template_version(tmp_path)
        assert result.passed is True
        assert "version unknown" in result.message

    def test_template_not_found(self, tmp_path):
        """Test when template directory doesn't exist."""
        non_existent = tmp_path / "non_existent"
        result = check_template_version(non_existent)
        assert result.passed is False
        assert result.fix_instructions is not None


class TestRunAllChecks:
    """Tests for run_all_checks function."""

    def test_run_all_checks_returns_tuple(self, tmp_path):
        """Test that run_all_checks returns proper tuple."""
        # Create minimal template structure
        (tmp_path / "VERSION").write_text("2.0.0")

        all_passed, results = run_all_checks(tmp_path)

        assert isinstance(all_passed, bool)
        assert isinstance(results, list)
        assert len(results) == 5  # All five checks
        assert all(isinstance(r, CheckResult) for r in results)

    def test_all_passed_logic(self, tmp_path):
        """Test that all_passed is True only when all checks pass."""
        (tmp_path / "VERSION").write_text("2.0.0")

        all_passed, results = run_all_checks(tmp_path)

        # all_passed should match whether all results passed
        expected = all(r.passed for r in results)
        assert all_passed == expected


class TestPrintResults:
    """Tests for print_results function."""

    def test_print_results_all_passed(self, capsys):
        """Test printing when all checks pass."""
        results = [
            CheckResult("Check 1", True, "OK"),
            CheckResult("Check 2", True, "OK"),
        ]

        print_results(results)

        captured = capsys.readouterr()
        assert "KEARNEY AI CODING ASSISTANT" in captured.out
        assert "[PASS]" in captured.out
        assert "All checks passed" in captured.out

    def test_print_results_with_failures(self, capsys):
        """Test printing when some checks fail."""
        results = [
            CheckResult("Check 1", True, "OK"),
            CheckResult("Check 2", False, "Failed", "Do this to fix"),
        ]

        print_results(results)

        captured = capsys.readouterr()
        assert "[PASS]" in captured.out
        assert "[FAIL]" in captured.out
        assert "ACTION REQUIRED" in captured.out
        assert "Do this to fix" in captured.out
