# tests/test_scaffold.py
"""Tests for scaffold.py"""

import json
import os
import pytest
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from scaffold import (
    scaffold_project,
    get_template_version,
    create_symlink_or_copy,
    TEMPLATE_ROOT,
)


class TestGetTemplateVersion:
    """Tests for get_template_version function."""

    def test_version_from_file(self):
        """Test reading version from VERSION file."""
        version = get_template_version()
        # VERSION file should exist in our template
        assert version is not None
        assert version != ""

    def test_version_format(self):
        """Test version follows semver format."""
        version = get_template_version()
        # Should be something like "2.0.0"
        parts = version.split(".")
        assert len(parts) >= 2  # At least major.minor


class TestCreateSymlinkOrCopy:
    """Tests for create_symlink_or_copy function."""

    def test_copy_file(self, tmp_path):
        """Test copying a file."""
        src = tmp_path / "source.txt"
        src.write_text("test content")
        dst = tmp_path / "dest.txt"

        create_symlink_or_copy(src, dst, use_symlinks=False)

        assert dst.exists()
        assert dst.read_text() == "test content"
        assert not dst.is_symlink()

    def test_copy_directory(self, tmp_path):
        """Test copying a directory."""
        src = tmp_path / "source_dir"
        src.mkdir()
        (src / "file.txt").write_text("content")

        dst = tmp_path / "dest_dir"

        create_symlink_or_copy(src, dst, use_symlinks=False)

        assert dst.exists()
        assert dst.is_dir()
        assert (dst / "file.txt").exists()
        assert (dst / "file.txt").read_text() == "content"

    @pytest.mark.skipif(sys.platform == "win32", reason="Symlinks may require admin on Windows")
    def test_symlink_directory(self, tmp_path):
        """Test creating a symlink for directory (Unix only)."""
        src = tmp_path / "source_dir"
        src.mkdir()
        (src / "file.txt").write_text("content")

        dst = tmp_path / "link_dir"

        create_symlink_or_copy(src, dst, use_symlinks=True)

        assert dst.exists()
        assert dst.is_symlink() or dst.is_dir()  # Junction on Windows is a dir


class TestScaffoldProject:
    """Tests for scaffold_project function."""

    def test_scaffold_creates_project_directory(self, tmp_path):
        """Test that scaffold creates the project directory."""
        project_path = scaffold_project(
            name="test-project",
            target_dir=tmp_path,
            use_symlinks=False  # Use copy for testing
        )

        assert project_path.exists()
        assert project_path.is_dir()
        assert project_path.name == "test-project"

    def test_scaffold_creates_claude_md(self, tmp_path):
        """Test that CLAUDE.md is copied."""
        project_path = scaffold_project(
            name="test-project",
            target_dir=tmp_path,
            use_symlinks=False
        )

        claude_md = project_path / "CLAUDE.md"
        assert claude_md.exists()
        content = claude_md.read_text()
        assert "KEARNEY" in content.upper() or "ROUTER" in content.upper()

    def test_scaffold_creates_claude_directory(self, tmp_path):
        """Test that .claude/ directory is copied."""
        project_path = scaffold_project(
            name="test-project",
            target_dir=tmp_path,
            use_symlinks=False
        )

        claude_dir = project_path / ".claude"
        assert claude_dir.exists()
        assert (claude_dir / "agents").exists()
        assert (claude_dir / "commands").exists()

    def test_scaffold_creates_readme(self, tmp_path):
        """Test that README.md is created with project name."""
        project_path = scaffold_project(
            name="my-cool-project",
            target_dir=tmp_path,
            use_symlinks=False
        )

        readme = project_path / "README.md"
        assert readme.exists()
        content = readme.read_text()
        assert "my-cool-project" in content

    def test_scaffold_creates_data_directories(self, tmp_path):
        """Test that data directories are created."""
        project_path = scaffold_project(
            name="test-project",
            target_dir=tmp_path,
            use_symlinks=False
        )

        assert (project_path / "data" / "raw").exists()
        assert (project_path / "data" / "processed").exists()
        assert (project_path / "data" / "external").exists()

    def test_scaffold_creates_output_directories(self, tmp_path):
        """Test that output directories are created."""
        project_path = scaffold_project(
            name="test-project",
            target_dir=tmp_path,
            use_symlinks=False
        )

        assert (project_path / "outputs" / "charts").exists()
        assert (project_path / "outputs" / "reports").exists()
        assert (project_path / "exports").exists()

    def test_scaffold_creates_project_state_directories(self, tmp_path):
        """Test that project_state directories are created."""
        project_path = scaffold_project(
            name="test-project",
            target_dir=tmp_path,
            use_symlinks=False
        )

        assert (project_path / "project_state").exists()
        assert (project_path / "project_state" / "spec_history").exists()
        assert (project_path / "project_state" / "logs").exists()
        assert (project_path / "project_state" / "logs" / "sessions").exists()
        assert (project_path / "project_state" / "logs" / "commands").exists()

    def test_scaffold_creates_gitignore(self, tmp_path):
        """Test that .gitignore is created with data protection."""
        project_path = scaffold_project(
            name="test-project",
            target_dir=tmp_path,
            use_symlinks=False
        )

        gitignore = project_path / ".gitignore"
        assert gitignore.exists()
        content = gitignore.read_text()
        assert "data/raw/*" in content
        assert "*.csv" in content
        assert "*.xlsx" in content

    def test_scaffold_creates_gitkeep_files(self, tmp_path):
        """Test that .gitkeep files are created in empty directories."""
        project_path = scaffold_project(
            name="test-project",
            target_dir=tmp_path,
            use_symlinks=False
        )

        assert (project_path / "data" / "raw" / ".gitkeep").exists()
        assert (project_path / "outputs" / "charts" / ".gitkeep").exists()

    def test_scaffold_creates_version_json(self, tmp_path):
        """Test that .kaca-version.json is created."""
        project_path = scaffold_project(
            name="test-project",
            target_dir=tmp_path,
            use_symlinks=False
        )

        version_file = project_path / ".kaca-version.json"
        assert version_file.exists()

        version_info = json.loads(version_file.read_text())
        assert "template_version" in version_info
        assert "created_at" in version_info
        assert version_info["project_name"] == "test-project"
        assert version_info["symlinks_used"] is False

    def test_scaffold_copies_core_without_symlinks(self, tmp_path):
        """Test that core/ is copied when symlinks disabled."""
        project_path = scaffold_project(
            name="test-project",
            target_dir=tmp_path,
            use_symlinks=False
        )

        core_dir = project_path / "core"
        assert core_dir.exists()
        assert (core_dir / "__init__.py").exists()
        # When copied, it should not be a symlink
        assert not core_dir.is_symlink()

    def test_scaffold_raises_if_project_exists(self, tmp_path):
        """Test that scaffold raises error if project already exists."""
        # Create project first
        project_path = tmp_path / "existing-project"
        project_path.mkdir()

        with pytest.raises(FileExistsError):
            scaffold_project(
                name="existing-project",
                target_dir=tmp_path,
                use_symlinks=False
            )

    def test_scaffold_version_info_has_symlinks_flag(self, tmp_path):
        """Test that version info records symlinks flag correctly."""
        # Test with symlinks=False
        project1 = scaffold_project(
            name="project-no-symlinks",
            target_dir=tmp_path,
            use_symlinks=False
        )
        info1 = json.loads((project1 / ".kaca-version.json").read_text())
        assert info1["symlinks_used"] is False

    def test_scaffold_readme_contains_commands(self, tmp_path):
        """Test that README contains command reference."""
        project_path = scaffold_project(
            name="test-project",
            target_dir=tmp_path,
            use_symlinks=False
        )

        readme = project_path / "README.md"
        content = readme.read_text()

        assert "/interview" in content
        assert "/plan" in content
        assert "/execute" in content


class TestScaffoldIntegration:
    """Integration tests for scaffold."""

    def test_full_scaffold_workflow(self, tmp_path):
        """Test the full scaffold workflow produces usable project."""
        project_path = scaffold_project(
            name="integration-test",
            target_dir=tmp_path,
            use_symlinks=False
        )

        # Verify critical files exist
        assert (project_path / "CLAUDE.md").exists()
        assert (project_path / ".claude" / "agents" / "interviewer.md").exists()
        assert (project_path / ".claude" / "commands" / "interview.md").exists()
        assert (project_path / "core" / "__init__.py").exists()
        assert (project_path / "config" / "interviews" / "modeling.yaml").exists()

        # Verify .gitignore protects data
        gitignore = (project_path / ".gitignore").read_text()
        assert "data/raw/*" in gitignore
        assert "*.csv" in gitignore

        # Verify version tracking
        version = json.loads((project_path / ".kaca-version.json").read_text())
        assert version["project_name"] == "integration-test"
