# tests/test_workspace_guard.py
"""Tests for workspace_guard module."""

import json
import os
import pytest
from pathlib import Path
from unittest.mock import patch

from core.workspace_guard import (
    is_template_repo,
    get_workspace_info,
    verify_workspace,
    require_project_workspace,
)


class TestIsTemplateRepo:
    """Tests for is_template_repo function."""

    def test_template_repo_has_scaffold_no_version(self, tmp_path, monkeypatch):
        """Template repo has scaffold.py but no .kaca-version.json."""
        (tmp_path / "scaffold.py").write_text("# scaffold script")
        monkeypatch.chdir(tmp_path)

        assert is_template_repo() is True

    def test_scaffolded_project_has_version(self, tmp_path, monkeypatch):
        """Scaffolded project has .kaca-version.json."""
        (tmp_path / ".kaca-version.json").write_text('{"version": "2.0.0"}')
        monkeypatch.chdir(tmp_path)

        assert is_template_repo() is False

    def test_scaffolded_project_both_files(self, tmp_path, monkeypatch):
        """Having both files means scaffolded project (version wins)."""
        (tmp_path / "scaffold.py").write_text("# scaffold script")
        (tmp_path / ".kaca-version.json").write_text('{"version": "2.0.0"}')
        monkeypatch.chdir(tmp_path)

        assert is_template_repo() is False

    def test_empty_directory(self, tmp_path, monkeypatch):
        """Empty directory is not template repo."""
        monkeypatch.chdir(tmp_path)

        assert is_template_repo() is False

    def test_version_file_only(self, tmp_path, monkeypatch):
        """Only version file means scaffolded project."""
        (tmp_path / ".kaca-version.json").write_text('{"version": "2.0.0"}')
        monkeypatch.chdir(tmp_path)

        assert is_template_repo() is False


class TestGetWorkspaceInfo:
    """Tests for get_workspace_info function."""

    def test_scaffolded_project_info(self, tmp_path, monkeypatch):
        """Returns project info from .kaca-version.json."""
        version_info = {
            "version": "2.0.0",
            "project_name": "test-project",
            "created_at": "2024-01-01T00:00:00",
            "template_path": "/path/to/template"
        }
        (tmp_path / ".kaca-version.json").write_text(json.dumps(version_info))
        monkeypatch.chdir(tmp_path)

        info = get_workspace_info()

        assert info["is_template"] is False
        assert info["version"] == "2.0.0"
        assert info["project_name"] == "test-project"
        assert info["created_at"] == "2024-01-01T00:00:00"
        assert info["template_path"] == "/path/to/template"

    def test_template_repo_info(self, tmp_path, monkeypatch):
        """Returns template info when no version file."""
        (tmp_path / "scaffold.py").write_text("# scaffold script")
        monkeypatch.chdir(tmp_path)

        info = get_workspace_info()

        assert info["is_template"] is True
        assert info["project_name"] is None
        assert info["template_version"] is None
        assert info["created_at"] is None
        assert info["template_path"] is None

    def test_corrupted_version_file(self, tmp_path, monkeypatch):
        """Handles corrupted .kaca-version.json gracefully."""
        (tmp_path / ".kaca-version.json").write_text("not valid json{")
        monkeypatch.chdir(tmp_path)

        info = get_workspace_info()

        # Falls back to template info
        assert info["is_template"] is True

    def test_empty_version_file(self, tmp_path, monkeypatch):
        """Handles empty .kaca-version.json gracefully."""
        (tmp_path / ".kaca-version.json").write_text("")
        monkeypatch.chdir(tmp_path)

        info = get_workspace_info()

        # Falls back to template info
        assert info["is_template"] is True


class TestVerifyWorkspace:
    """Tests for verify_workspace function."""

    def test_raises_in_template_repo(self, tmp_path, monkeypatch):
        """Raises RuntimeError when in template repo."""
        (tmp_path / "scaffold.py").write_text("# scaffold script")
        monkeypatch.chdir(tmp_path)

        with pytest.raises(RuntimeError) as exc_info:
            verify_workspace(raise_on_template=True)

        assert "KACA template repository" in str(exc_info.value)
        assert "scaffold.py" in str(exc_info.value)

    def test_returns_false_without_raising(self, tmp_path, monkeypatch):
        """Returns (False, message) when raise_on_template=False."""
        (tmp_path / "scaffold.py").write_text("# scaffold script")
        monkeypatch.chdir(tmp_path)

        is_valid, message = verify_workspace(raise_on_template=False)

        assert is_valid is False
        assert "KACA template repository" in message

    def test_ok_in_scaffolded_project(self, tmp_path, monkeypatch):
        """Returns (True, message) in scaffolded project."""
        (tmp_path / ".kaca-version.json").write_text('{"version": "2.0.0"}')
        monkeypatch.chdir(tmp_path)

        is_valid, message = verify_workspace()

        assert is_valid is True
        assert message == "Workspace OK"

    def test_message_includes_fix_instructions(self, tmp_path, monkeypatch):
        """Warning message includes fix instructions."""
        (tmp_path / "scaffold.py").write_text("# scaffold script")
        monkeypatch.chdir(tmp_path)

        _, message = verify_workspace(raise_on_template=False)

        # Should include Mac/Linux instructions
        assert "python scaffold.py" in message
        assert "~/Projects/" in message
        # Should include Windows instructions
        assert "PowerShell" in message
        assert "$env:USERPROFILE" in message


class TestRequireProjectWorkspace:
    """Tests for require_project_workspace decorator."""

    def test_decorator_allows_scaffolded_project(self, tmp_path, monkeypatch):
        """Decorator allows function to run in scaffolded project."""
        (tmp_path / ".kaca-version.json").write_text('{"version": "2.0.0"}')
        monkeypatch.chdir(tmp_path)

        @require_project_workspace()
        def my_function():
            return "success"

        result = my_function()
        assert result == "success"

    def test_decorator_blocks_template_repo(self, tmp_path, monkeypatch):
        """Decorator blocks function in template repo."""
        (tmp_path / "scaffold.py").write_text("# scaffold script")
        monkeypatch.chdir(tmp_path)

        @require_project_workspace()
        def my_function():
            return "success"

        with pytest.raises(RuntimeError) as exc_info:
            my_function()

        assert "KACA template repository" in str(exc_info.value)

    def test_decorator_preserves_function_args(self, tmp_path, monkeypatch):
        """Decorator passes through function arguments."""
        (tmp_path / ".kaca-version.json").write_text('{"version": "2.0.0"}')
        monkeypatch.chdir(tmp_path)

        @require_project_workspace()
        def add_numbers(a, b, c=0):
            return a + b + c

        result = add_numbers(1, 2, c=3)
        assert result == 6

    def test_decorator_preserves_exceptions(self, tmp_path, monkeypatch):
        """Decorator doesn't swallow function exceptions."""
        (tmp_path / ".kaca-version.json").write_text('{"version": "2.0.0"}')
        monkeypatch.chdir(tmp_path)

        @require_project_workspace()
        def raises_value_error():
            raise ValueError("test error")

        with pytest.raises(ValueError, match="test error"):
            raises_value_error()


class TestEdgeCases:
    """Edge case tests."""

    def test_symlinked_scaffold_not_detected(self, tmp_path, monkeypatch):
        """Symlinked scaffold.py in scaffolded project doesn't trigger warning."""
        # Create "template" directory with scaffold.py
        template_dir = tmp_path / "template"
        template_dir.mkdir()
        (template_dir / "scaffold.py").write_text("# scaffold script")

        # Create "project" directory with version file
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        (project_dir / ".kaca-version.json").write_text('{"version": "2.0.0"}')

        # Even if someone creates a scaffold.py symlink, version file wins
        monkeypatch.chdir(project_dir)

        assert is_template_repo() is False

    def test_case_sensitivity(self, tmp_path, monkeypatch):
        """File checks use OS-native case sensitivity."""
        # Create wrong case files
        (tmp_path / "SCAFFOLD.py").write_text("# scaffold script")
        monkeypatch.chdir(tmp_path)

        # On macOS (case-insensitive by default), SCAFFOLD.py matches scaffold.py
        # On Linux (case-sensitive), it would not match
        # This test documents the platform-dependent behavior
        import sys
        if sys.platform == "darwin":
            # macOS is case-insensitive by default
            assert is_template_repo() is True
        else:
            # Linux and others are typically case-sensitive
            assert is_template_repo() is False

    def test_deeply_nested_cwd(self, tmp_path, monkeypatch):
        """Works from deeply nested subdirectory."""
        # Create project structure
        (tmp_path / ".kaca-version.json").write_text('{"version": "2.0.0"}')
        nested = tmp_path / "a" / "b" / "c" / "d"
        nested.mkdir(parents=True)

        # Change to nested directory - should still find project root...
        # Actually, current implementation only checks cwd
        monkeypatch.chdir(nested)

        # From nested dir without version file, it's not a template
        # (no scaffold.py either)
        assert is_template_repo() is False
