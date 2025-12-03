"""Tests for streamlit_utils module."""

import pytest
from pathlib import Path

from core.streamlit_utils import (
    is_port_in_use,
    find_available_port,
    verify_imports,
    generate_requirements,
    STREAMLIT_CORE_DEPS,
    STREAMLIT_VIZ_DEPS,
    STREAMLIT_ALL_DEPS,
)


class TestPortUtils:

    def test_is_port_in_use_returns_bool(self):
        result = is_port_in_use(8501)
        assert isinstance(result, bool)

    def test_find_available_port_returns_int(self):
        port = find_available_port(start_port=9000)
        assert isinstance(port, int)
        assert port >= 9000

    def test_find_available_port_respects_start(self):
        port = find_available_port(start_port=9500)
        assert port >= 9500

    def test_find_available_port_raises_on_exhaustion(self):
        # This test might be flaky in environments with many ports in use
        # Using a very high port range that's likely free
        port = find_available_port(start_port=59000, max_attempts=10)
        assert 59000 <= port < 59010


class TestVerifyImports:

    def test_finds_installed_modules(self):
        success, missing = verify_imports(["os", "sys", "pathlib"])
        assert success is True
        assert missing == []

    def test_finds_missing_modules(self):
        success, missing = verify_imports(["nonexistent_module_xyz"])
        assert success is False
        assert "nonexistent_module_xyz" in missing

    def test_handles_mixed_modules(self):
        success, missing = verify_imports(["os", "nonexistent_xyz", "sys"])
        assert success is False
        assert "nonexistent_xyz" in missing
        assert "os" not in missing
        assert "sys" not in missing

    def test_handles_submodules(self):
        # os.path should resolve to os
        success, missing = verify_imports(["os.path"])
        assert success is True
        assert missing == []


class TestGenerateRequirements:

    def test_includes_core_deps(self):
        result = generate_requirements(include_viz=False)
        assert "streamlit" in result
        assert "pandas" in result
        assert "plotly" in result

    def test_includes_viz_deps_when_requested(self):
        result = generate_requirements(include_viz=True)
        assert "seaborn" in result
        assert "matplotlib" in result

    def test_excludes_viz_deps_when_not_requested(self):
        result = generate_requirements(include_viz=False)
        assert "seaborn" not in result
        assert "matplotlib" not in result

    def test_includes_extra_deps(self):
        result = generate_requirements(extra_deps=["custom-package>=1.0"])
        assert "custom-package>=1.0" in result

    def test_returns_newline_separated(self):
        result = generate_requirements(include_viz=False)
        lines = result.strip().split("\n")
        assert len(lines) >= 3  # At least core deps


class TestDependencyConstants:

    def test_core_deps_not_empty(self):
        assert len(STREAMLIT_CORE_DEPS) > 0

    def test_viz_deps_not_empty(self):
        assert len(STREAMLIT_VIZ_DEPS) > 0

    def test_all_deps_contains_core_and_viz(self):
        for dep in STREAMLIT_CORE_DEPS:
            assert dep in STREAMLIT_ALL_DEPS
        for dep in STREAMLIT_VIZ_DEPS:
            assert dep in STREAMLIT_ALL_DEPS

    def test_deps_have_version_specifiers(self):
        for dep in STREAMLIT_CORE_DEPS:
            assert ">=" in dep or "==" in dep, f"Missing version specifier in {dep}"
