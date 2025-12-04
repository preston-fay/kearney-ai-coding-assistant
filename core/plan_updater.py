"""
Plan Updater for KACA

Applies specification changes to execution plans incrementally,
preserving completed work where possible.

Usage:
    from core.plan_updater import PlanUpdater

    updater = PlanUpdater()
    result = updater.apply_diff(diff_result, current_status, current_plan)
"""

import json
import logging
import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

from core.spec_diff import DiffResult, ImpactLevel, ChangeType

logger = logging.getLogger(__name__)


@dataclass
class TaskUpdate:
    """Represents an update to a task."""
    task_id: str
    action: str  # "mark_review", "mark_deprecated", "keep", "update_description"
    reason: str
    new_status: Optional[str] = None
    new_description: Optional[str] = None


@dataclass
class PlanUpdateResult:
    """Result of applying a diff to a plan."""
    success: bool
    task_updates: List[TaskUpdate]
    new_tasks: List[Dict[str, Any]]
    deprecated_tasks: List[str]
    unchanged_tasks: List[str]
    summary: str
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'success': self.success,
            'task_updates': [
                {'task_id': u.task_id, 'action': u.action, 'reason': u.reason}
                for u in self.task_updates
            ],
            'new_tasks': self.new_tasks,
            'deprecated_tasks': self.deprecated_tasks,
            'unchanged_tasks': self.unchanged_tasks,
            'summary': self.summary,
            'warnings': self.warnings,
        }


class PlanUpdater:
    """
    Updates execution plans based on specification changes.

    Strategies:
    - Completed tasks in unaffected phases: Keep as-is
    - Completed tasks in affected phases: Mark "needs_review"
    - Pending tasks in affected phases: Mark "updated"
    - Removed requirements: Mark related tasks "deprecated"
    - Added requirements: Generate new tasks
    """

    def __init__(self):
        self.task_counter = 0

    def apply_diff(
        self,
        diff_result: DiffResult,
        current_status: Dict[str, Any],
        current_plan: str = None,
    ) -> PlanUpdateResult:
        """
        Apply specification diff to update the plan.

        Args:
            diff_result: Result from compute_diff()
            current_status: Current status.json content
            current_plan: Current plan.md content (optional)

        Returns:
            PlanUpdateResult with all updates
        """
        if not diff_result.has_changes():
            return PlanUpdateResult(
                success=True,
                task_updates=[],
                new_tasks=[],
                deprecated_tasks=[],
                unchanged_tasks=[t['id'] for t in current_status.get('tasks', [])],
                summary="No changes to apply.",
            )

        task_updates = []
        new_tasks = []
        deprecated_tasks = []
        unchanged_tasks = []
        warnings = []

        affected_phases = diff_result.get_affected_phases()
        tasks = current_status.get('tasks', [])

        # Find the highest task number for generating new IDs
        self.task_counter = self._find_max_task_number(tasks)

        # Process existing tasks
        for task in tasks:
            task_id = task['id']
            task_phase = task.get('phase', '')
            task_status = task.get('status', 'pending')

            # Check if task's phase is affected
            phase_affected = any(phase in task_phase for phase in affected_phases)

            if not phase_affected:
                # Task not affected, keep as-is
                unchanged_tasks.append(task_id)
                task_updates.append(TaskUpdate(
                    task_id=task_id,
                    action="keep",
                    reason="Phase not affected by changes"
                ))
            else:
                # Task is in an affected phase
                if task_status == 'done':
                    # Completed task needs review
                    task_updates.append(TaskUpdate(
                        task_id=task_id,
                        action="mark_review",
                        reason=f"Phase affected by spec changes: {', '.join(affected_phases)}",
                        new_status="needs_review"
                    ))
                elif task_status == 'in_progress':
                    # In-progress task needs attention
                    task_updates.append(TaskUpdate(
                        task_id=task_id,
                        action="mark_review",
                        reason="Spec changed while task in progress",
                        new_status="needs_review"
                    ))
                    warnings.append(f"Task {task_id} was in progress when spec changed")
                else:
                    # Pending task marked as updated
                    task_updates.append(TaskUpdate(
                        task_id=task_id,
                        action="mark_review",
                        reason="Pending task in affected phase",
                        new_status="updated"
                    ))

        # Check for removed requirements -> deprecate related tasks
        for change in diff_result.changes:
            if change.change_type == ChangeType.REMOVED:
                # Find tasks that might be related to removed content
                related = self._find_related_tasks(change.path, change.old_value, tasks)
                for task_id in related:
                    if task_id not in deprecated_tasks:
                        deprecated_tasks.append(task_id)
                        task_updates.append(TaskUpdate(
                            task_id=task_id,
                            action="mark_deprecated",
                            reason=f"Related requirement removed: {change.path}",
                            new_status="deprecated"
                        ))

        # Check for added requirements -> generate new tasks
        for change in diff_result.changes:
            if change.change_type == ChangeType.ADDED:
                new = self._generate_tasks_for_addition(change, diff_result)
                new_tasks.extend(new)

        # Generate summary
        summary = self._generate_summary(
            task_updates, new_tasks, deprecated_tasks, unchanged_tasks
        )

        return PlanUpdateResult(
            success=True,
            task_updates=task_updates,
            new_tasks=new_tasks,
            deprecated_tasks=deprecated_tasks,
            unchanged_tasks=unchanged_tasks,
            summary=summary,
            warnings=warnings,
        )

    def apply_to_status(
        self,
        update_result: PlanUpdateResult,
        current_status: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Apply update result to status.json content.

        Args:
            update_result: Result from apply_diff()
            current_status: Current status.json content

        Returns:
            Updated status.json content
        """
        updated_status = current_status.copy()
        tasks = [t.copy() for t in updated_status.get('tasks', [])]

        # Apply task updates
        for update in update_result.task_updates:
            for task in tasks:
                if task['id'] == update.task_id:
                    if update.new_status:
                        task['status'] = update.new_status
                    if update.new_description:
                        task['description'] = update.new_description
                    # Add update tracking
                    task['last_update'] = {
                        'action': update.action,
                        'reason': update.reason,
                        'timestamp': datetime.now().isoformat()
                    }
                    break

        # Add new tasks
        for new_task in update_result.new_tasks:
            tasks.append(new_task)

        # Update status
        updated_status['tasks'] = tasks
        updated_status['spec_version'] = updated_status.get('spec_version', 0) + 1

        # Add to history
        history = updated_status.get('history', []).copy()
        history.append({
            'action': 'plan_updated',
            'timestamp': datetime.now().isoformat(),
            'summary': update_result.summary,
        })
        updated_status['history'] = history

        return updated_status

    def _find_max_task_number(self, tasks: List[Dict]) -> int:
        """Find the highest task number in current tasks."""
        max_num = 0
        for task in tasks:
            task_id = task.get('id', '')
            # Parse task ID (e.g., "2.3" -> 2.3)
            match = re.match(r'(\d+)\.(\d+)', task_id)
            if match:
                phase_num = int(match.group(1))
                task_num = int(match.group(2))
                # Use phase * 100 + task as a single number for comparison
                num = phase_num * 100 + task_num
                max_num = max(max_num, num)
        return max_num

    def _find_related_tasks(
        self,
        path: str,
        value: Any,
        tasks: List[Dict]
    ) -> List[str]:
        """Find tasks that might be related to a removed spec element."""
        related = []

        # Convert value to searchable string
        if isinstance(value, dict):
            search_terms = list(value.values())
        elif isinstance(value, list):
            search_terms = value
        else:
            search_terms = [str(value)]

        # Look for tasks with descriptions matching the removed content
        for task in tasks:
            description = task.get('description', '').lower()
            for term in search_terms:
                if str(term).lower() in description:
                    related.append(task['id'])
                    break

        return related

    def _generate_tasks_for_addition(
        self,
        change,
        diff_result: DiffResult
    ) -> List[Dict[str, Any]]:
        """Generate new tasks for added requirements."""
        new_tasks = []

        # Determine which phase the new task belongs to
        phases = change.affected_phases or ['Phase 3']
        target_phase = phases[0] if phases else 'Phase 3'

        # Generate task ID
        self.task_counter += 1
        phase_num = self._extract_phase_number(target_phase)
        task_num = (self.task_counter % 100) or 1
        task_id = f"{phase_num}.{task_num}"

        # Generate task based on what was added
        if 'deliverables' in change.path:
            description = f"Create new deliverable: {change.new_value}"
        elif 'data.sources' in change.path:
            description = f"Process new data source: {change.new_value}"
        elif 'visualization' in change.path:
            description = f"Update visualization: {change.path.split('.')[-1]}"
        else:
            description = f"Handle addition: {change.path}"

        new_tasks.append({
            'id': task_id,
            'description': description,
            'phase': target_phase,
            'status': 'pending',
            'added_at': datetime.now().isoformat(),
            'source': f"Spec change: {change.path}",
        })

        return new_tasks

    def _extract_phase_number(self, phase: str) -> int:
        """Extract phase number from phase name."""
        match = re.search(r'Phase\s*(\d+)', phase)
        if match:
            return int(match.group(1))
        return 5  # Default to Phase 5 if unknown

    def _generate_summary(
        self,
        task_updates: List[TaskUpdate],
        new_tasks: List[Dict],
        deprecated_tasks: List[str],
        unchanged_tasks: List[str]
    ) -> str:
        """Generate human-readable summary."""
        parts = []

        # Count by action
        reviews = sum(1 for u in task_updates if u.action == "mark_review")
        keeps = len(unchanged_tasks)

        if reviews:
            parts.append(f"{reviews} tasks marked for review")
        if new_tasks:
            parts.append(f"{len(new_tasks)} new tasks added")
        if deprecated_tasks:
            parts.append(f"{len(deprecated_tasks)} tasks deprecated")
        if keeps:
            parts.append(f"{keeps} tasks unchanged")

        return "; ".join(parts) if parts else "No task changes"


def update_plan_from_diff(
    diff_result: DiffResult,
    status_path: str = "project_state/status.json",
    plan_path: str = "project_state/plan.md",
) -> PlanUpdateResult:
    """
    Convenience function to update plan files from a diff result.

    Args:
        diff_result: Result from compute_diff()
        status_path: Path to status.json
        plan_path: Path to plan.md

    Returns:
        PlanUpdateResult
    """
    # Load current status
    status_file = Path(status_path)
    if status_file.exists():
        with open(status_file, 'r') as f:
            current_status = json.load(f)
    else:
        current_status = {'tasks': [], 'history': []}

    # Load current plan
    plan_file = Path(plan_path)
    current_plan = plan_file.read_text() if plan_file.exists() else ""

    # Apply diff
    updater = PlanUpdater()
    result = updater.apply_diff(diff_result, current_status, current_plan)

    if result.success:
        # Update status file
        updated_status = updater.apply_to_status(result, current_status)
        status_file.parent.mkdir(parents=True, exist_ok=True)
        with open(status_file, 'w') as f:
            json.dump(updated_status, f, indent=2)

        logger.info(f"Plan updated: {result.summary}")

    return result
