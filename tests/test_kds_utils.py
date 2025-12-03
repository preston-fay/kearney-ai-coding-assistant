"""Tests for kds_utils module."""

import pytest
from pathlib import Path

from core.kds_utils import safe_write_text, safe_read_text


class TestSafeWriteText:

    def test_writes_normal_text(self, tmp_path):
        test_file = tmp_path / "test.txt"
        content = "Hello, world!"

        result = safe_write_text(test_file, content)

        assert result.exists()
        assert result.read_text() == content

    def test_creates_parent_directories(self, tmp_path):
        test_file = tmp_path / "deep" / "nested" / "file.txt"

        safe_write_text(test_file, "content")

        assert test_file.exists()

    def test_removes_surrogate_pairs(self, tmp_path):
        test_file = tmp_path / "test.txt"
        # Surrogate pair that would crash normal write
        content = "Icon: \ud83d\udca4 here"

        # Should not raise
        safe_write_text(test_file, content)

        # Should be readable
        result = test_file.read_text()
        assert "Icon:" in result
        assert "\ud83d" not in result  # Surrogate removed

    def test_removes_emojis(self, tmp_path):
        test_file = tmp_path / "test.txt"
        content = "Title \U0001F4A4 with emoji"  # Sleep symbol

        safe_write_text(test_file, content)

        result = test_file.read_text()
        assert "\U0001F4A4" not in result
        assert "Title" in result
        assert "with emoji" in result

    def test_handles_string_path(self, tmp_path):
        test_file = str(tmp_path / "test.txt")

        result = safe_write_text(test_file, "content")

        assert result.exists()
        assert isinstance(result, Path)

    def test_overwrites_existing_file(self, tmp_path):
        test_file = tmp_path / "test.txt"
        test_file.write_text("old content")

        safe_write_text(test_file, "new content")

        assert test_file.read_text() == "new content"


class TestSafeReadText:

    def test_reads_normal_file(self, tmp_path):
        test_file = tmp_path / "test.txt"
        test_file.write_text("Hello!")

        result = safe_read_text(test_file)

        assert result == "Hello!"

    def test_handles_encoding_errors(self, tmp_path):
        test_file = tmp_path / "test.txt"
        # Write some bytes that aren't valid UTF-8
        test_file.write_bytes(b"Hello \xff\xfe world")

        # Should not raise
        result = safe_read_text(test_file)

        assert "Hello" in result
        assert "world" in result

    def test_handles_string_path(self, tmp_path):
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")

        result = safe_read_text(str(test_file))

        assert result == "content"

    def test_reads_unicode_content(self, tmp_path):
        test_file = tmp_path / "test.txt"
        test_file.write_text("Unicode: \u00e9\u00e8\u00ea", encoding="utf-8")

        result = safe_read_text(test_file)

        assert "\u00e9" in result  # e-acute
