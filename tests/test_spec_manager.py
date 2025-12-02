# tests/test_spec_manager.py
"""Tests for spec_manager module."""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch

from core import spec_manager
from core.spec_manager import (
    Specification,
    SpecMeta,
    SpecProblem,
    SpecData,
    create_spec,
    save_spec,
    load_spec,
    get_version,
    increment_version,
    get_section,
    set_section,
    get_history,
    load_version,
    rollback_to_version,
    get_changelog,
    analyze_impact,
    spec_exists,
    get_spec_summary,
)


@pytest.fixture
def temp_project_dir(tmp_path):
    """Create temporary project directory and patch paths."""
    spec_file = tmp_path / 'project_state' / 'spec.yaml'
    history_dir = tmp_path / 'project_state' / 'spec_history'

    with patch.object(spec_manager, 'SPEC_FILE', spec_file):
        with patch.object(spec_manager, 'SPEC_HISTORY_DIR', history_dir):
            with patch.object(spec_manager, 'CHANGELOG_FILE', history_dir / 'changelog.md'):
                yield tmp_path


@pytest.fixture
def sample_spec():
    """Create a sample specification."""
    return create_spec(
        project_name='test-project',
        project_type='modeling',
        client='Test Client',
        deadline='2025-12-31',
    )


class TestCreateSpec:
    def test_create_basic_spec(self):
        spec = create_spec('my-project', 'modeling')

        assert spec.meta.project_name == 'my-project'
        assert spec.meta.project_type == 'modeling'
        assert spec.version == 1
        assert spec.created_at != ''
        assert spec.updated_at != ''

    def test_create_spec_with_optional_fields(self):
        spec = create_spec(
            project_name='client-project',
            project_type='presentation',
            client='Acme Corp',
            deadline='2025-06-15',
        )

        assert spec.meta.client == 'Acme Corp'
        assert spec.meta.deadline == '2025-06-15'

    def test_create_spec_default_empty_fields(self):
        spec = create_spec('test', 'dashboard')

        assert spec.deliverables == []
        assert spec.notes == []
        assert spec.type_specific == {}


class TestSaveAndLoadSpec:
    def test_save_and_load_spec(self, temp_project_dir, sample_spec):
        save_spec(sample_spec)

        loaded = load_spec()

        assert loaded is not None
        assert loaded.meta.project_name == 'test-project'
        assert loaded.meta.project_type == 'modeling'
        assert loaded.version == 1

    def test_load_nonexistent_spec(self, temp_project_dir):
        loaded = load_spec()
        assert loaded is None

    def test_save_updates_timestamp(self, temp_project_dir, sample_spec):
        # Set a clearly old timestamp
        sample_spec.updated_at = '2020-01-01T00:00:00Z'
        save_spec(sample_spec)

        loaded = load_spec()
        # Updated timestamp should be newer than the original
        assert loaded.updated_at != '2020-01-01T00:00:00Z'
        assert loaded.updated_at > '2020-01-01T00:00:00Z'

    def test_save_with_changelog_entry(self, temp_project_dir, sample_spec):
        save_spec(sample_spec, "Initial specification")

        changelog = get_changelog()
        assert "Initial specification" in changelog

    def test_save_preserves_type_specific(self, temp_project_dir, sample_spec):
        sample_spec.type_specific = {
            'problem_type': 'classification',
            'target_variable': 'churn',
        }
        save_spec(sample_spec)

        loaded = load_spec()
        assert loaded.type_specific.get('problem_type') == 'classification'


class TestVersioning:
    def test_get_version_no_spec(self, temp_project_dir):
        assert get_version() == 0

    def test_get_version_with_spec(self, temp_project_dir, sample_spec):
        save_spec(sample_spec)
        assert get_version() == 1

    def test_increment_version(self, sample_spec):
        assert sample_spec.version == 1
        incremented = increment_version(sample_spec)
        assert incremented.version == 2

    def test_save_archives_old_version(self, temp_project_dir, sample_spec):
        # Save v1
        save_spec(sample_spec)

        # Save v2
        sample_spec.version = 2
        save_spec(sample_spec, "Updated to v2")

        # Check history
        history = get_history()
        assert len(history) == 1
        assert history[0]['version'] == 1

    def test_load_version_from_history(self, temp_project_dir, sample_spec):
        # Save v1
        save_spec(sample_spec)

        # Save v2
        sample_spec.version = 2
        sample_spec.meta.project_name = 'renamed-project'
        save_spec(sample_spec)

        # Load v1
        v1 = load_version(1)
        assert v1 is not None
        assert v1.meta.project_name == 'test-project'

    def test_load_nonexistent_version(self, temp_project_dir):
        assert load_version(999) is None


class TestRollback:
    def test_rollback_to_previous_version(self, temp_project_dir, sample_spec):
        # Save v1
        save_spec(sample_spec)

        # Save v2 with changes
        sample_spec.version = 2
        sample_spec.meta.project_name = 'changed-name'
        save_spec(sample_spec)

        # Rollback to v1
        rolled_back = rollback_to_version(1)

        assert rolled_back is not None
        assert rolled_back.meta.project_name == 'test-project'
        assert rolled_back.version == 3  # New version after rollback

    def test_rollback_nonexistent_version(self, temp_project_dir, sample_spec):
        save_spec(sample_spec)
        result = rollback_to_version(999)
        assert result is None


class TestGetAndSetSection:
    def test_get_section_meta_field(self, sample_spec):
        result = get_section(sample_spec, 'meta.project_name')
        assert result == 'test-project'

    def test_get_section_nested(self, sample_spec):
        sample_spec.problem.business_question = 'Test question'
        result = get_section(sample_spec, 'problem.business_question')
        assert result == 'Test question'

    def test_get_section_not_found(self, sample_spec):
        result = get_section(sample_spec, 'nonexistent.field')
        assert result is None

    def test_set_section_simple(self, sample_spec):
        modified = set_section(sample_spec, 'meta.client', 'New Client')
        assert modified.meta.client == 'New Client'

    def test_set_section_nested(self, sample_spec):
        modified = set_section(sample_spec, 'problem.business_question', 'New question')
        assert modified.problem.business_question == 'New question'


class TestChangelog:
    def test_get_changelog_empty(self, temp_project_dir):
        changelog = get_changelog()
        assert 'No changes recorded' in changelog or 'Changelog' in changelog

    def test_changelog_entries_accumulate(self, temp_project_dir, sample_spec):
        save_spec(sample_spec, "First change")

        sample_spec.version = 2
        save_spec(sample_spec, "Second change")

        changelog = get_changelog()
        assert "First change" in changelog
        assert "Second change" in changelog


class TestImpactAnalysis:
    def test_analyze_problem_type_change(self, sample_spec):
        sample_spec.type_specific = {'problem_type': 'classification'}

        impact = analyze_impact(sample_spec, {
            'modeling.problem_type': 'regression'
        })

        assert len(impact['plan_impact']) > 0
        assert any('problem type' in s.lower() for s in impact['plan_impact'])

    def test_analyze_target_variable_change(self, sample_spec):
        sample_spec.type_specific = {'target_variable': 'old_target'}

        impact = analyze_impact(sample_spec, {
            'modeling.target_variable': 'new_target'
        })

        assert len(impact['plan_impact']) > 0 or len(impact['work_impact']) > 0


class TestSpecExists:
    def test_spec_exists_false(self, temp_project_dir):
        assert spec_exists() is False

    def test_spec_exists_true(self, temp_project_dir, sample_spec):
        save_spec(sample_spec)
        assert spec_exists() is True


class TestGetSpecSummary:
    def test_summary_includes_name(self, sample_spec):
        summary = get_spec_summary(sample_spec)
        assert 'test-project' in summary

    def test_summary_includes_type(self, sample_spec):
        summary = get_spec_summary(sample_spec)
        assert 'modeling' in summary

    def test_summary_includes_version(self, sample_spec):
        summary = get_spec_summary(sample_spec)
        assert '1' in summary

    def test_summary_includes_client(self, sample_spec):
        summary = get_spec_summary(sample_spec)
        assert 'Test Client' in summary

    def test_summary_includes_deliverables_count(self, sample_spec):
        sample_spec.deliverables = [
            {'type': 'model'},
            {'type': 'report'},
        ]
        summary = get_spec_summary(sample_spec)
        assert '2' in summary


class TestHistory:
    def test_get_history_empty(self, temp_project_dir):
        history = get_history()
        assert history == []

    def test_get_history_multiple_versions(self, temp_project_dir, sample_spec):
        save_spec(sample_spec)

        for i in range(2, 5):
            sample_spec.version = i
            save_spec(sample_spec)

        history = get_history()
        assert len(history) == 3  # v1, v2, v3 archived
        assert all('version' in h for h in history)
