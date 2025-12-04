# tests/test_hook_runner.py
"""Tests for hook_runner module."""

import json
import pytest
from pathlib import Path


class TestBrandCheck:
    """Tests for brand_check hook."""

    def test_compliant_file_returns_zero(self, tmp_path):
        """Compliant files should return 0."""
        from core.hook_runner import brand_check

        # Create a compliant Python file
        test_file = tmp_path / "compliant.py"
        test_file.write_text("color = '#7823DC'  # Kearney purple\n")

        result = brand_check(str(test_file))
        assert result == 0

    def test_non_checkable_extension_returns_zero(self, tmp_path):
        """Non-checkable files should return 0."""
        from core.hook_runner import brand_check

        test_file = tmp_path / "data.csv"
        test_file.write_text("a,b,c\n1,2,3\n")

        result = brand_check(str(test_file))
        assert result == 0

    def test_nonexistent_file_returns_zero(self):
        """Missing files should return 0 (no error)."""
        from core.hook_runner import brand_check

        result = brand_check("/nonexistent/path/file.py")
        assert result == 0

    def test_violation_returns_one(self, tmp_path, capsys):
        """Files with violations should return 1."""
        from core.hook_runner import brand_check

        # Create file with green color (forbidden)
        test_file = tmp_path / "bad.py"
        test_file.write_text("color = '#00FF00'  # green\n")

        result = brand_check(str(test_file))
        assert result == 1

        captured = capsys.readouterr()
        assert "BRAND CHECK" in captured.out

    def test_skips_test_files(self, tmp_path):
        """Files with 'test' in path should be skipped."""
        from core.hook_runner import brand_check

        # Create file with violation but 'test' in name
        test_file = tmp_path / "test_something.py"
        test_file.write_text("color = '#00FF00'  # green\n")

        result = brand_check(str(test_file))
        assert result == 0  # Skipped, not checked

    def test_skips_dot_files(self, tmp_path):
        """Files starting with dot should be skipped."""
        from core.hook_runner import brand_check

        test_file = tmp_path / ".hidden.py"
        test_file.write_text("color = '#00FF00'  # green\n")

        result = brand_check(str(test_file))
        assert result == 0  # Skipped, not checked


class TestSessionEnd:
    """Tests for session_end hook."""

    def test_session_end_creates_log(self, tmp_path, monkeypatch):
        """session_end should create log entry."""
        from core.hook_runner import session_end

        # Change to temp directory with project_state
        project_state = tmp_path / "project_state"
        project_state.mkdir()
        monkeypatch.chdir(tmp_path)

        result = session_end()
        assert result == 0

        log_file = project_state / "session_log.jsonl"
        assert log_file.exists()

        with open(log_file) as f:
            entry = json.loads(f.readline())

        assert entry["event"] == "session_end"
        assert "timestamp" in entry

    def test_session_end_skips_non_project(self, tmp_path, monkeypatch):
        """session_end should skip if no project_state dir."""
        from core.hook_runner import session_end

        # Change to temp directory without project_state
        monkeypatch.chdir(tmp_path)

        result = session_end()
        assert result == 0

        # No log file created
        assert not (tmp_path / "project_state").exists()

    def test_session_end_appends_to_log(self, tmp_path, monkeypatch):
        """session_end should append to existing log."""
        from core.hook_runner import session_end

        # Change to temp directory with project_state
        project_state = tmp_path / "project_state"
        project_state.mkdir()
        monkeypatch.chdir(tmp_path)

        # Run twice
        session_end()
        session_end()

        log_file = project_state / "session_log.jsonl"
        with open(log_file) as f:
            lines = f.readlines()

        assert len(lines) == 2


class TestValidateWrite:
    """Tests for validate_write function."""

    def test_write_within_project_allowed(self, tmp_path, monkeypatch):
        """Writes within project directory should be allowed."""
        from core.workspace_guard import validate_write

        monkeypatch.chdir(tmp_path)

        # Create a subdirectory
        subdir = tmp_path / "outputs"
        subdir.mkdir()

        result = validate_write(str(subdir / "file.txt"))
        assert result is True

    def test_write_outside_project_blocked(self, tmp_path, monkeypatch, capsys):
        """Writes outside project directory should be blocked."""
        from core.workspace_guard import validate_write

        monkeypatch.chdir(tmp_path)

        result = validate_write("/etc/passwd")
        assert result is False

        captured = capsys.readouterr()
        assert "outside project" in captured.out
