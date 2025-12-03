"""Tests for brand_guard Python file checking."""

import pytest
from pathlib import Path

from core.brand_guard import check_python_file, BrandViolation


class TestCheckPythonFile:

    def test_detects_emoji_in_python(self, tmp_path):
        py_file = tmp_path / "test.py"
        py_file.write_text('page_icon = "\U0001F4A4"')  # Sleep symbol

        violations = check_python_file(py_file)

        assert len(violations) > 0
        assert any(v.rule == "NO_EMOJIS" for v in violations)

    def test_detects_forbidden_green_color(self, tmp_path):
        py_file = tmp_path / "test.py"
        py_file.write_text('success_color = "#2e7d32"')

        violations = check_python_file(py_file)

        assert len(violations) > 0
        assert any(v.rule == "FORBIDDEN_COLOR" for v in violations)

    def test_passes_clean_python(self, tmp_path):
        py_file = tmp_path / "test.py"
        py_file.write_text('''
# Clean Python file
import streamlit as st

st.set_page_config(
    page_title="Dashboard",
    layout="wide"
)

PRIMARY_COLOR = "#7823DC"  # Kearney Purple
''')

        violations = check_python_file(py_file)

        assert len(violations) == 0

    def test_reports_correct_line_numbers(self, tmp_path):
        py_file = tmp_path / "test.py"
        py_file.write_text('''line 1
line 2
emoji here \U0001F600
line 4
''')

        violations = check_python_file(py_file)

        assert len(violations) == 1
        assert violations[0].line_number == 3

    def test_handles_unreadable_file(self, tmp_path):
        py_file = tmp_path / "nonexistent.py"

        violations = check_python_file(py_file)

        assert len(violations) == 1
        assert violations[0].rule == "FILE_READ_ERROR"
        assert violations[0].severity == "warning"

    def test_detects_gridlines_true(self, tmp_path):
        py_file = tmp_path / "test.py"
        py_file.write_text('ax.grid(True)')

        violations = check_python_file(py_file)

        assert any(v.rule == "NO_GRIDLINES" for v in violations)

    def test_passes_gridlines_false(self, tmp_path):
        py_file = tmp_path / "test.py"
        py_file.write_text('ax.grid(False)')

        violations = check_python_file(py_file)

        grid_violations = [v for v in violations if v.rule == "NO_GRIDLINES"]
        assert len(grid_violations) == 0

    def test_detects_named_green_color(self, tmp_path):
        py_file = tmp_path / "test.py"
        py_file.write_text("plt.plot(x, y, color='green')")

        violations = check_python_file(py_file)

        assert any(v.rule == "FORBIDDEN_COLOR" for v in violations)

    def test_detects_multiple_violations(self, tmp_path):
        py_file = tmp_path / "test.py"
        py_file.write_text('''
page_icon = "\U0001F4A4"  # emoji violation
success_color = "#4caf50"  # green violation
ax.grid(True)  # gridline violation
''')

        violations = check_python_file(py_file)

        rules = {v.rule for v in violations}
        assert "NO_EMOJIS" in rules
        assert "FORBIDDEN_COLOR" in rules
        assert "NO_GRIDLINES" in rules

    def test_kearney_purple_allowed(self, tmp_path):
        py_file = tmp_path / "test.py"
        py_file.write_text('PRIMARY = "#7823DC"')

        violations = check_python_file(py_file)

        color_violations = [v for v in violations if v.rule == "FORBIDDEN_COLOR"]
        assert len(color_violations) == 0

    def test_handles_encoding_errors_gracefully(self, tmp_path):
        py_file = tmp_path / "test.py"
        # Write invalid UTF-8 bytes
        py_file.write_bytes(b"# -*- coding: utf-8 -*-\ncolor = '\xff\xfe'\n")

        # Should not raise, should handle gracefully
        violations = check_python_file(py_file)

        # May or may not have violations, but should not crash
        assert isinstance(violations, list)


class TestBrandViolationDataclass:

    def test_file_read_error_has_warning_severity(self, tmp_path):
        py_file = tmp_path / "nonexistent.py"

        violations = check_python_file(py_file)

        assert len(violations) == 1
        assert violations[0].severity == "warning"
        assert "FILE_READ_ERROR" == violations[0].rule

    def test_emoji_violation_has_error_severity(self, tmp_path):
        py_file = tmp_path / "test.py"
        py_file.write_text('icon = "\U0001F600"')

        violations = check_python_file(py_file)

        emoji_violations = [v for v in violations if v.rule == "NO_EMOJIS"]
        assert len(emoji_violations) == 1
        assert emoji_violations[0].severity == "error"
