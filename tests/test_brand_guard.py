"""Tests for core/brand_guard.py"""

import pytest
from pathlib import Path
import tempfile
import os

from core.brand_guard import (
    check_file,
    check_directory,
    check_text_content,
    normalize_hex,
    rgb_to_hex,
    is_green_rgb,
    BrandViolation,
    FORBIDDEN_COLORS,
    ALLOWED_COLORS,
)


class TestColorUtilities:
    """Tests for color utility functions."""

    def test_normalize_hex_lowercase(self):
        """Test that hex colors are normalized to lowercase."""
        assert normalize_hex("#7823DC") == "#7823dc"
        assert normalize_hex("#FFFFFF") == "#ffffff"

    def test_normalize_hex_short_form(self):
        """Test that short hex colors are expanded."""
        assert normalize_hex("#FFF") == "#ffffff"
        assert normalize_hex("#000") == "#000000"
        assert normalize_hex("#f0f") == "#ff00ff"

    def test_rgb_to_hex(self):
        """Test RGB to hex conversion."""
        assert rgb_to_hex(120, 35, 220) == "#7823dc"
        assert rgb_to_hex(255, 255, 255) == "#ffffff"
        assert rgb_to_hex(0, 0, 0) == "#000000"

    def test_is_green_rgb_true(self):
        """Test detection of green RGB values."""
        assert is_green_rgb(0, 255, 0) is True
        assert is_green_rgb(50, 200, 50) is True
        assert is_green_rgb(100, 180, 80) is True

    def test_is_green_rgb_false(self):
        """Test that non-green colors return False."""
        assert is_green_rgb(120, 35, 220) is False  # Purple
        assert is_green_rgb(255, 0, 0) is False  # Red
        assert is_green_rgb(0, 0, 255) is False  # Blue
        assert is_green_rgb(100, 100, 100) is False  # Gray


class TestTextContentChecks:
    """Tests for text content validation."""

    def test_detect_emoji(self):
        """Test that emojis are detected in text."""
        # Use actual Unicode emojis
        content = "Hello World! \U0001F600 Great job!"  # Grinning face emoji
        violations = check_text_content(content, "test.txt")
        emoji_violations = [v for v in violations if v.rule == "NO_EMOJIS"]
        assert len(emoji_violations) == 1

    def test_no_emoji_clean_text(self):
        """Test that clean text passes emoji check."""
        content = "Hello World! This is clean text."
        violations = check_text_content(content, "test.txt")
        emoji_violations = [v for v in violations if v.rule == "NO_EMOJIS"]
        assert len(emoji_violations) == 0

    def test_detect_forbidden_hex_color(self):
        """Test detection of forbidden hex colors."""
        content = 'color: #00FF00;'  # Pure green
        violations = check_text_content(content, "test.css")
        color_violations = [v for v in violations if v.rule == "FORBIDDEN_COLOR"]
        assert len(color_violations) == 1

    def test_detect_forbidden_rgb_color(self):
        """Test detection of forbidden RGB colors."""
        content = 'background: rgb(0, 255, 0);'  # Pure green
        violations = check_text_content(content, "test.css")
        color_violations = [v for v in violations if v.rule == "FORBIDDEN_COLOR"]
        assert len(color_violations) == 1

    def test_allowed_colors_pass(self):
        """Test that allowed colors don't trigger violations."""
        content = 'color: #7823DC;'  # Kearney Purple
        violations = check_text_content(content, "test.css")
        color_violations = [v for v in violations if v.rule == "FORBIDDEN_COLOR"]
        assert len(color_violations) == 0

    def test_line_numbers_reported(self):
        """Test that line numbers are correctly reported."""
        content = "Line 1\nLine 2 with emoji \U0001F600\nLine 3"  # Emoji on line 2
        violations = check_text_content(content, "test.txt")
        emoji_violations = [v for v in violations if v.rule == "NO_EMOJIS"]
        assert len(emoji_violations) == 1
        assert emoji_violations[0].line_number == 2


class TestFileChecks:
    """Tests for file validation."""

    def test_check_nonexistent_file(self):
        """Test that nonexistent files return no violations."""
        violations = check_file(Path("/nonexistent/file.py"))
        assert len(violations) == 0

    def test_check_python_file_with_green(self):
        """Test checking Python file with green color."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("color = '#00FF00'  # Green color\n")
            f.flush()
            temp_path = Path(f.name)

        try:
            violations = check_file(temp_path)
            color_violations = [v for v in violations if v.rule == "FORBIDDEN_COLOR"]
            assert len(color_violations) >= 1
        finally:
            os.unlink(temp_path)

    def test_check_python_file_with_gridlines(self):
        """Test checking Python file with gridlines enabled."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("ax.grid(True)  # Enable grid\n")
            f.flush()
            temp_path = Path(f.name)

        try:
            violations = check_file(temp_path)
            grid_violations = [v for v in violations if v.rule == "NO_GRIDLINES"]
            assert len(grid_violations) == 1
        finally:
            os.unlink(temp_path)

    def test_check_css_file_with_named_green(self):
        """Test checking CSS file with named green color."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.css', delete=False) as f:
            f.write(".success { color: green; }\n")
            f.flush()
            temp_path = Path(f.name)

        try:
            violations = check_file(temp_path)
            color_violations = [v for v in violations if v.rule == "FORBIDDEN_COLOR"]
            assert len(color_violations) >= 1
        finally:
            os.unlink(temp_path)

    def test_check_clean_python_file(self):
        """Test that clean Python files pass validation."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("color = '#7823DC'  # Kearney Purple\n")
            f.write("ax.grid(False)  # No grid\n")
            f.flush()
            temp_path = Path(f.name)

        try:
            violations = check_file(temp_path)
            assert len(violations) == 0
        finally:
            os.unlink(temp_path)


class TestDirectoryChecks:
    """Tests for directory validation."""

    def test_check_nonexistent_directory(self):
        """Test that nonexistent directories return no violations."""
        violations = check_directory(Path("/nonexistent/directory"))
        assert len(violations) == 0

    def test_check_directory_with_violations(self):
        """Test checking a directory with brand violations."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a file with violations
            bad_file = Path(tmpdir) / "bad.py"
            bad_file.write_text("color = '#00FF00'  # Green\n")

            violations = check_directory(Path(tmpdir))
            assert len(violations) >= 1

    def test_check_directory_recursive(self):
        """Test recursive directory checking."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create nested structure
            subdir = Path(tmpdir) / "subdir"
            subdir.mkdir()

            bad_file = subdir / "nested.py"
            bad_file.write_text("color = '#4CAF50'  # Material green\n")

            violations = check_directory(Path(tmpdir), recursive=True)
            assert len(violations) >= 1

    def test_check_directory_non_recursive(self):
        """Test non-recursive directory checking."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create nested structure
            subdir = Path(tmpdir) / "subdir"
            subdir.mkdir()

            nested_file = subdir / "nested.py"
            nested_file.write_text("color = '#4CAF50'  # Material green\n")

            root_file = Path(tmpdir) / "root.py"
            root_file.write_text("# Clean file\n")

            violations = check_directory(Path(tmpdir), recursive=False)
            # Should only check root.py, not nested.py
            nested_violations = [v for v in violations if "nested" in v.file_path]
            assert len(nested_violations) == 0


class TestBrandViolation:
    """Tests for BrandViolation dataclass."""

    def test_brand_violation_creation(self):
        """Test creating a BrandViolation."""
        violation = BrandViolation(
            file_path="test.py",
            rule="FORBIDDEN_COLOR",
            message="Green color detected",
            line_number=42,
            severity="error",
        )
        assert violation.file_path == "test.py"
        assert violation.rule == "FORBIDDEN_COLOR"
        assert violation.line_number == 42
        assert violation.severity == "error"

    def test_brand_violation_default_severity(self):
        """Test that default severity is 'error'."""
        violation = BrandViolation(
            file_path="test.py",
            rule="NO_EMOJIS",
            message="Emoji detected",
        )
        assert violation.severity == "error"


class TestForbiddenColors:
    """Tests for forbidden color definitions."""

    def test_common_greens_forbidden(self):
        """Test that common green colors are in forbidden list."""
        assert "#00ff00" in FORBIDDEN_COLORS
        assert "#4caf50" in FORBIDDEN_COLORS  # Material green 500
        assert "#2e7d32" in FORBIDDEN_COLORS  # Material green 800

    def test_kearney_purple_allowed(self):
        """Test that Kearney Purple is in allowed list."""
        assert "#7823dc" in ALLOWED_COLORS

    def test_no_overlap(self):
        """Test that there's no overlap between allowed and forbidden."""
        overlap = ALLOWED_COLORS & FORBIDDEN_COLORS
        assert len(overlap) == 0
