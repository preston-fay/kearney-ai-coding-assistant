"""Tests for spec diff engine."""

import pytest
from core.spec_diff import (
    compute_diff,
    assess_plan_impact,
    SpecChange,
    ChangeType,
    ImpactLevel,
    DiffResult,
    _get_nested,
    _parse_path,
    _get_all_paths,
)


class TestPathParsing:
    """Tests for path parsing utilities."""

    def test_parse_simple_path(self):
        """Should parse simple dot-notation path."""
        parts = _parse_path("meta.project_name")
        assert parts == ['meta', 'project_name']

    def test_parse_path_with_array(self):
        """Should parse path with array index."""
        parts = _parse_path("data.sources[0].path")
        assert parts == ['data', 'sources', 0, 'path']

    def test_parse_nested_path(self):
        """Should parse deeply nested path."""
        parts = _parse_path("a.b.c.d")
        assert parts == ['a', 'b', 'c', 'd']


class TestGetNested:
    """Tests for nested value retrieval."""

    def test_get_simple_value(self):
        """Should get simple nested value."""
        d = {'meta': {'project_name': 'Test'}}
        assert _get_nested(d, 'meta.project_name') == 'Test'

    def test_get_array_value(self):
        """Should get value from array."""
        d = {'data': {'sources': [{'path': 'file.csv'}]}}
        assert _get_nested(d, 'data.sources[0].path') == 'file.csv'

    def test_get_missing_path_returns_none(self):
        """Should return None for missing path."""
        d = {'a': 1}
        assert _get_nested(d, 'b.c') is None


class TestGetAllPaths:
    """Tests for path enumeration."""

    def test_get_paths_simple(self):
        """Should get all paths from simple dict."""
        d = {'a': 1, 'b': 2}
        paths = _get_all_paths(d)
        assert 'a' in paths
        assert 'b' in paths

    def test_get_paths_nested(self):
        """Should get paths from nested dict."""
        d = {'meta': {'name': 'test', 'version': 1}}
        paths = _get_all_paths(d)
        assert 'meta.name' in paths
        assert 'meta.version' in paths

    def test_get_paths_with_array(self):
        """Should get paths including array indices."""
        d = {'items': [{'a': 1}, {'b': 2}]}
        paths = _get_all_paths(d)
        assert 'items[0].a' in paths
        assert 'items[1].b' in paths


class TestComputeDiff:
    """Tests for diff computation."""

    def test_no_changes(self):
        """Should detect no changes."""
        spec = {'meta': {'version': 1}}
        result = compute_diff(spec, spec)

        assert not result.has_changes()
        assert result.overall_impact == ImpactLevel.NONE

    def test_detect_added_field(self):
        """Should detect added field."""
        old = {'meta': {'version': 1}}
        new = {'meta': {'version': 2, 'client': 'Acme'}}

        result = compute_diff(old, new)

        assert result.has_changes()
        added = [c for c in result.changes if c.change_type == ChangeType.ADDED]
        assert any('client' in c.path for c in added)

    def test_detect_removed_field(self):
        """Should detect removed field."""
        old = {'meta': {'version': 1, 'notes': 'test'}}
        new = {'meta': {'version': 2}}

        result = compute_diff(old, new)

        removed = [c for c in result.changes if c.change_type == ChangeType.REMOVED]
        assert any('notes' in c.path for c in removed)

    def test_detect_modified_field(self):
        """Should detect modified field."""
        old = {'problem': {'business_question': 'Old question'}}
        new = {'problem': {'business_question': 'New question'}}

        result = compute_diff(old, new)

        modified = [c for c in result.changes if c.change_type == ChangeType.MODIFIED]
        assert any('business_question' in c.path for c in modified)

    def test_high_impact_change(self):
        """Should flag high impact changes."""
        old = {'data': {'sources': []}}
        new = {'data': {'sources': [{'path': 'new.csv'}]}}

        result = compute_diff(old, new)

        assert result.overall_impact in (ImpactLevel.HIGH, ImpactLevel.MEDIUM)

    def test_low_impact_change(self):
        """Should flag low impact changes."""
        old = {'meta': {'project_name': 'Old'}}
        new = {'meta': {'project_name': 'New'}}

        result = compute_diff(old, new)

        # meta changes should be low/no impact
        assert result.overall_impact in (ImpactLevel.NONE, ImpactLevel.LOW, ImpactLevel.MEDIUM)


class TestDiffResult:
    """Tests for DiffResult methods."""

    def test_get_high_impact_changes(self):
        """Should filter high impact changes."""
        result = DiffResult(
            old_version=1,
            new_version=2,
            changes=[
                SpecChange(path='a', change_type=ChangeType.MODIFIED, impact_level=ImpactLevel.LOW),
                SpecChange(path='b', change_type=ChangeType.MODIFIED, impact_level=ImpactLevel.HIGH),
                SpecChange(path='c', change_type=ChangeType.MODIFIED, impact_level=ImpactLevel.CRITICAL),
            ]
        )

        high = result.get_high_impact_changes()
        assert len(high) == 2

    def test_get_affected_phases(self):
        """Should aggregate affected phases."""
        result = DiffResult(
            old_version=1,
            new_version=2,
            changes=[
                SpecChange(path='a', change_type=ChangeType.MODIFIED, affected_phases=['Phase 1']),
                SpecChange(path='b', change_type=ChangeType.MODIFIED, affected_phases=['Phase 2', 'Phase 3']),
            ]
        )

        phases = result.get_affected_phases()
        assert phases == {'Phase 1', 'Phase 2', 'Phase 3'}


class TestAssessPlanImpact:
    """Tests for plan impact assessment."""

    def test_no_changes_continue(self):
        """Should recommend continue when no changes."""
        diff = DiffResult(old_version=1, new_version=1, changes=[])
        status = {'tasks': [{'id': '1.1', 'status': 'done', 'phase': 'Phase 1'}]}

        impact = assess_plan_impact(diff, status)

        assert impact['recommended_action'] == 'continue'
        assert len(impact['tasks_unaffected']) == 1

    def test_affected_phase_marks_tasks(self):
        """Should mark tasks in affected phases for review."""
        diff = DiffResult(
            old_version=1,
            new_version=2,
            changes=[
                SpecChange(
                    path='data.sources',
                    change_type=ChangeType.MODIFIED,
                    impact_level=ImpactLevel.HIGH,
                    affected_phases=['Phase 1', 'Phase 2']
                )
            ],
            overall_impact=ImpactLevel.HIGH
        )

        status = {
            'tasks': [
                {'id': '1.1', 'status': 'done', 'phase': 'Phase 1: Data Prep'},
                {'id': '2.1', 'status': 'pending', 'phase': 'Phase 2: Analysis'},
                {'id': '3.1', 'status': 'pending', 'phase': 'Phase 3: Viz'},
            ]
        }

        impact = assess_plan_impact(diff, status)

        assert '1.1' in impact['tasks_to_review']
        assert '2.1' in impact['tasks_to_review']
        assert '3.1' in impact['tasks_unaffected']

    def test_high_impact_recommends_partial_replan(self):
        """Should recommend partial replan for high impact."""
        diff = DiffResult(
            old_version=1,
            new_version=2,
            changes=[
                SpecChange(
                    path='problem.business_question',
                    change_type=ChangeType.MODIFIED,
                    impact_level=ImpactLevel.HIGH,
                    affected_phases=['Phase 2']
                )
            ],
            overall_impact=ImpactLevel.HIGH
        )

        status = {'tasks': [{'id': '1.1', 'status': 'done', 'phase': 'Phase 2'}]}

        impact = assess_plan_impact(diff, status)

        assert impact['recommended_action'] == 'partial_replan'
