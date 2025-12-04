"""Tests for plan updater."""

import pytest
from datetime import datetime

from core.plan_updater import PlanUpdater, PlanUpdateResult, TaskUpdate
from core.spec_diff import DiffResult, SpecChange, ChangeType, ImpactLevel


class TestPlanUpdater:
    """Tests for PlanUpdater class."""

    def test_no_changes_returns_unchanged(self):
        """Should return all tasks unchanged when no diff."""
        updater = PlanUpdater()
        diff = DiffResult(old_version=1, new_version=1, changes=[])
        status = {
            'tasks': [
                {'id': '1.1', 'status': 'done', 'phase': 'Phase 1'},
                {'id': '2.1', 'status': 'pending', 'phase': 'Phase 2'},
            ]
        }

        result = updater.apply_diff(diff, status)

        assert result.success
        assert len(result.unchanged_tasks) == 2
        assert len(result.task_updates) == 0

    def test_affected_phase_marks_tasks_for_review(self):
        """Should mark tasks in affected phases for review."""
        updater = PlanUpdater()
        diff = DiffResult(
            old_version=1,
            new_version=2,
            changes=[
                SpecChange(
                    path='data.sources',
                    change_type=ChangeType.MODIFIED,
                    impact_level=ImpactLevel.HIGH,
                    affected_phases=['Phase 1']
                )
            ]
        )
        status = {
            'tasks': [
                {'id': '1.1', 'status': 'done', 'phase': 'Phase 1: Data Prep'},
                {'id': '2.1', 'status': 'pending', 'phase': 'Phase 2: Analysis'},
            ]
        }

        result = updater.apply_diff(diff, status)

        # Task 1.1 should be marked for review
        review_updates = [u for u in result.task_updates if u.action == 'mark_review']
        assert any(u.task_id == '1.1' for u in review_updates)

        # Task 2.1 should be unchanged
        assert '2.1' in result.unchanged_tasks

    def test_in_progress_task_generates_warning(self):
        """Should warn when in-progress task is affected."""
        updater = PlanUpdater()
        diff = DiffResult(
            old_version=1,
            new_version=2,
            changes=[
                SpecChange(
                    path='problem.business_question',
                    change_type=ChangeType.MODIFIED,
                    affected_phases=['Phase 2']
                )
            ]
        )
        status = {
            'tasks': [
                {'id': '2.1', 'status': 'in_progress', 'phase': 'Phase 2: Analysis'},
            ]
        }

        result = updater.apply_diff(diff, status)

        assert len(result.warnings) > 0
        assert '2.1' in result.warnings[0]

    def test_added_requirement_generates_new_task(self):
        """Should generate new task for added requirement."""
        updater = PlanUpdater()
        diff = DiffResult(
            old_version=1,
            new_version=2,
            changes=[
                SpecChange(
                    path='deliverables[2]',
                    change_type=ChangeType.ADDED,
                    new_value='Dashboard',
                    affected_phases=['Phase 3']
                )
            ]
        )
        status = {'tasks': []}

        result = updater.apply_diff(diff, status)

        assert len(result.new_tasks) > 0
        assert 'Dashboard' in result.new_tasks[0]['description']

    def test_apply_to_status_updates_tasks(self):
        """Should correctly apply updates to status."""
        updater = PlanUpdater()

        update_result = PlanUpdateResult(
            success=True,
            task_updates=[
                TaskUpdate(
                    task_id='1.1',
                    action='mark_review',
                    reason='Test reason',
                    new_status='needs_review'
                )
            ],
            new_tasks=[
                {'id': '3.1', 'description': 'New task', 'status': 'pending', 'phase': 'Phase 3'}
            ],
            deprecated_tasks=[],
            unchanged_tasks=['2.1'],
            summary='Test summary'
        )

        current_status = {
            'tasks': [
                {'id': '1.1', 'status': 'done', 'phase': 'Phase 1'},
                {'id': '2.1', 'status': 'pending', 'phase': 'Phase 2'},
            ],
            'history': []
        }

        updated = updater.apply_to_status(update_result, current_status)

        # Check task 1.1 was updated
        task_1_1 = next(t for t in updated['tasks'] if t['id'] == '1.1')
        assert task_1_1['status'] == 'needs_review'
        assert 'last_update' in task_1_1

        # Check new task was added
        assert len(updated['tasks']) == 3
        assert any(t['id'] == '3.1' for t in updated['tasks'])

        # Check history was updated
        assert len(updated['history']) > 0
        assert updated['history'][-1]['action'] == 'plan_updated'


class TestPlanUpdateResult:
    """Tests for PlanUpdateResult."""

    def test_to_dict(self):
        """Should serialize to dict."""
        result = PlanUpdateResult(
            success=True,
            task_updates=[
                TaskUpdate(task_id='1.1', action='keep', reason='Test')
            ],
            new_tasks=[],
            deprecated_tasks=['2.1'],
            unchanged_tasks=['3.1'],
            summary='Test summary',
            warnings=['Warning 1']
        )

        d = result.to_dict()

        assert d['success'] is True
        assert len(d['task_updates']) == 1
        assert d['deprecated_tasks'] == ['2.1']
        assert d['warnings'] == ['Warning 1']


class TestTaskGeneration:
    """Tests for new task generation."""

    def test_generates_deliverable_task(self):
        """Should generate appropriate task for deliverable."""
        updater = PlanUpdater()
        diff = DiffResult(
            old_version=1,
            new_version=2,
            changes=[
                SpecChange(
                    path='deliverables[0]',
                    change_type=ChangeType.ADDED,
                    new_value='Executive Report',
                    affected_phases=['Phase 4']
                )
            ]
        )

        result = updater.apply_diff(diff, {'tasks': []})

        assert len(result.new_tasks) == 1
        assert 'Executive Report' in result.new_tasks[0]['description']
        assert result.new_tasks[0]['status'] == 'pending'

    def test_generates_data_source_task(self):
        """Should generate appropriate task for data source."""
        updater = PlanUpdater()
        diff = DiffResult(
            old_version=1,
            new_version=2,
            changes=[
                SpecChange(
                    path='data.sources[1]',
                    change_type=ChangeType.ADDED,
                    new_value={'path': 'extra.csv'},
                    affected_phases=['Phase 1']
                )
            ]
        )

        result = updater.apply_diff(diff, {'tasks': []})

        assert len(result.new_tasks) == 1
        assert 'data source' in result.new_tasks[0]['description'].lower()


class TestDeprecatedTasks:
    """Tests for task deprecation."""

    def test_removed_requirement_deprecates_related_task(self):
        """Should deprecate task when related requirement removed."""
        updater = PlanUpdater()
        diff = DiffResult(
            old_version=1,
            new_version=2,
            changes=[
                SpecChange(
                    path='deliverables[1]',
                    change_type=ChangeType.REMOVED,
                    old_value='Quarterly Report',
                    affected_phases=['Phase 4']
                )
            ]
        )
        status = {
            'tasks': [
                {'id': '4.1', 'description': 'Create Quarterly Report', 'status': 'pending', 'phase': 'Phase 4'},
                {'id': '4.2', 'description': 'Create Dashboard', 'status': 'pending', 'phase': 'Phase 4'},
            ]
        }

        result = updater.apply_diff(diff, status)

        # Task 4.1 should be deprecated (contains "Quarterly Report")
        assert '4.1' in result.deprecated_tasks
        # Task 4.2 should not be deprecated
        assert '4.2' not in result.deprecated_tasks


class TestSummaryGeneration:
    """Tests for summary generation."""

    def test_summary_includes_all_changes(self):
        """Should generate comprehensive summary."""
        updater = PlanUpdater()
        diff = DiffResult(
            old_version=1,
            new_version=2,
            changes=[
                SpecChange(
                    path='data.sources',
                    change_type=ChangeType.MODIFIED,
                    affected_phases=['Phase 1']
                ),
                SpecChange(
                    path='deliverables[2]',
                    change_type=ChangeType.ADDED,
                    new_value='New Item',
                    affected_phases=['Phase 4']
                )
            ]
        )
        status = {
            'tasks': [
                {'id': '1.1', 'status': 'done', 'phase': 'Phase 1: Data'},
                {'id': '5.1', 'status': 'pending', 'phase': 'Phase 5: Export'},
            ]
        }

        result = updater.apply_diff(diff, status)

        # Summary should mention reviews, new tasks, and unchanged
        assert 'review' in result.summary.lower() or 'new' in result.summary.lower()
