"""
Specification Diff Engine for KACA

Computes semantic differences between spec versions and
assesses impact on execution plans.

Usage:
    from core.spec_diff import compute_diff, assess_impact

    changes = compute_diff(old_spec, new_spec)
    impact = assess_impact(changes)
"""

import logging
import re
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Set
from enum import Enum

logger = logging.getLogger(__name__)


class ChangeType(Enum):
    """Types of specification changes."""
    ADDED = "added"
    REMOVED = "removed"
    MODIFIED = "modified"
    UNCHANGED = "unchanged"


class ImpactLevel(Enum):
    """Impact level of a change on the plan."""
    NONE = "none"          # No impact on plan
    LOW = "low"            # Minor adjustment, no task changes
    MEDIUM = "medium"      # Some tasks need review
    HIGH = "high"          # Significant replanning needed
    CRITICAL = "critical"  # Full replanning required


@dataclass
class SpecChange:
    """Represents a single change in the specification."""
    path: str                           # Dot-notation path (e.g., "data.sources[0].path")
    change_type: ChangeType
    old_value: Any = None
    new_value: Any = None
    impact_level: ImpactLevel = ImpactLevel.MEDIUM
    affected_phases: List[str] = field(default_factory=list)
    description: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            'path': self.path,
            'change_type': self.change_type.value,
            'old_value': self.old_value,
            'new_value': self.new_value,
            'impact_level': self.impact_level.value,
            'affected_phases': self.affected_phases,
            'description': self.description,
        }


@dataclass
class DiffResult:
    """Result of comparing two specifications."""
    old_version: int
    new_version: int
    changes: List[SpecChange]
    overall_impact: ImpactLevel = ImpactLevel.NONE
    summary: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            'old_version': self.old_version,
            'new_version': self.new_version,
            'changes': [c.to_dict() for c in self.changes],
            'overall_impact': self.overall_impact.value,
            'summary': self.summary,
        }

    def has_changes(self) -> bool:
        return len(self.changes) > 0

    def get_high_impact_changes(self) -> List[SpecChange]:
        return [c for c in self.changes
                if c.impact_level in (ImpactLevel.HIGH, ImpactLevel.CRITICAL)]

    def get_affected_phases(self) -> Set[str]:
        phases = set()
        for change in self.changes:
            phases.update(change.affected_phases)
        return phases


# Mapping from spec paths to affected plan phases
PATH_TO_PHASE_MAP = {
    'meta.project_name': [],  # No impact
    'meta.client': [],  # No impact
    'meta.deadline': ['Phase 5'],  # Affects scheduling
    'problem.business_question': ['Phase 2', 'Phase 3', 'Phase 4'],  # Core analysis
    'problem.success_criteria': ['Phase 2', 'Phase 3'],
    'data.sources': ['Phase 1', 'Phase 2'],  # Data prep and analysis
    'data.sources[*].path': ['Phase 1'],  # Data loading
    'data.sources[*].keys': ['Phase 2'],  # Analysis grouping
    'deliverables': ['Phase 3', 'Phase 4', 'Phase 5'],  # Outputs
    'visualization': ['Phase 3'],  # Chart generation
    'visualization.format': ['Phase 3'],
    'visualization.insight_depth': ['Phase 3', 'Phase 4'],
    'type_specific': ['Phase 2', 'Phase 3'],  # Type-specific processing
}

# Impact assessment by change type and path pattern
IMPACT_RULES = {
    'data.sources': ImpactLevel.HIGH,
    'problem.business_question': ImpactLevel.HIGH,
    'deliverables': ImpactLevel.MEDIUM,
    'visualization': ImpactLevel.LOW,
    'meta': ImpactLevel.NONE,
    'notes': ImpactLevel.NONE,
}


def compute_diff(old_spec: Dict[str, Any], new_spec: Dict[str, Any]) -> DiffResult:
    """
    Compute semantic differences between two spec versions.

    Args:
        old_spec: Previous specification dict
        new_spec: New specification dict

    Returns:
        DiffResult with list of changes and impact assessment
    """
    old_version = old_spec.get('meta', {}).get('version', 0)
    new_version = new_spec.get('meta', {}).get('version', 0)

    changes = []

    # Compare all paths
    all_paths = _get_all_paths(old_spec) | _get_all_paths(new_spec)

    for path in sorted(all_paths):
        old_value = _get_nested(old_spec, path)
        new_value = _get_nested(new_spec, path)

        if old_value == new_value:
            continue

        # Determine change type
        if old_value is None:
            change_type = ChangeType.ADDED
        elif new_value is None:
            change_type = ChangeType.REMOVED
        else:
            change_type = ChangeType.MODIFIED

        # Assess impact
        impact = _assess_path_impact(path)
        affected_phases = _get_affected_phases(path)

        # Generate description
        description = _generate_change_description(path, change_type, old_value, new_value)

        changes.append(SpecChange(
            path=path,
            change_type=change_type,
            old_value=old_value,
            new_value=new_value,
            impact_level=impact,
            affected_phases=affected_phases,
            description=description,
        ))

    # Compute overall impact
    overall_impact = _compute_overall_impact(changes)

    # Generate summary
    summary = _generate_diff_summary(changes)

    return DiffResult(
        old_version=old_version,
        new_version=new_version,
        changes=changes,
        overall_impact=overall_impact,
        summary=summary,
    )


def _get_all_paths(d: Dict[str, Any], prefix: str = '') -> Set[str]:
    """Get all leaf paths in a nested dict."""
    paths = set()

    if not isinstance(d, dict):
        return paths

    for key, value in d.items():
        current_path = f"{prefix}.{key}" if prefix else key

        if isinstance(value, dict):
            paths.update(_get_all_paths(value, current_path))
        elif isinstance(value, list):
            for i, item in enumerate(value):
                if isinstance(item, dict):
                    paths.update(_get_all_paths(item, f"{current_path}[{i}]"))
                else:
                    paths.add(f"{current_path}[{i}]")
            # Also add the list itself as a path
            paths.add(current_path)
        else:
            paths.add(current_path)

    return paths


def _get_nested(d: Dict[str, Any], path: str) -> Any:
    """Get nested value using dot notation with array indices."""
    if not path:
        return d

    current = d
    parts = _parse_path(path)

    for part in parts:
        if current is None:
            return None

        if isinstance(part, int):
            # Array index
            if isinstance(current, list) and 0 <= part < len(current):
                current = current[part]
            else:
                return None
        else:
            # Dict key
            if isinstance(current, dict):
                current = current.get(part)
            else:
                return None

    return current


def _parse_path(path: str) -> List:
    """Parse a path string into parts, handling array indices."""
    parts = []

    # Split on dots, but handle array indices
    tokens = re.split(r'\.(?![^\[]*\])', path)

    for token in tokens:
        # Check for array index
        match = re.match(r'([^\[]+)(?:\[(\d+)\])?', token)
        if match:
            key = match.group(1)
            if key:
                parts.append(key)
            if match.group(2) is not None:
                parts.append(int(match.group(2)))

    return parts


def _assess_path_impact(path: str) -> ImpactLevel:
    """Determine impact level for a spec path."""
    # Check specific paths first
    for pattern, impact in IMPACT_RULES.items():
        if path.startswith(pattern):
            return impact

    # Default to medium
    return ImpactLevel.MEDIUM


def _get_affected_phases(path: str) -> List[str]:
    """Get list of phases affected by a change to this path."""
    # Check exact match first
    if path in PATH_TO_PHASE_MAP:
        return PATH_TO_PHASE_MAP[path].copy()

    # Check prefix matches
    for pattern, phases in PATH_TO_PHASE_MAP.items():
        # Handle wildcard patterns
        if '[*]' in pattern:
            base_pattern = pattern.replace('[*]', '[')
            if path.startswith(base_pattern.split('[')[0]) and '[' in path:
                return phases.copy()
        elif path.startswith(pattern):
            return phases.copy()

    # Default phases based on path prefix
    prefix = path.split('.')[0] if '.' in path else path
    defaults = {
        'data': ['Phase 1', 'Phase 2'],
        'problem': ['Phase 2', 'Phase 3'],
        'deliverables': ['Phase 3', 'Phase 4'],
        'visualization': ['Phase 3'],
        'type_specific': ['Phase 2', 'Phase 3'],
    }

    return defaults.get(prefix, ['Phase 2', 'Phase 3'])


def _compute_overall_impact(changes: List[SpecChange]) -> ImpactLevel:
    """Compute overall impact from individual changes."""
    if not changes:
        return ImpactLevel.NONE

    # Highest impact wins
    impact_order = [
        ImpactLevel.CRITICAL,
        ImpactLevel.HIGH,
        ImpactLevel.MEDIUM,
        ImpactLevel.LOW,
        ImpactLevel.NONE,
    ]

    for level in impact_order:
        if any(c.impact_level == level for c in changes):
            return level

    return ImpactLevel.NONE


def _generate_change_description(
    path: str,
    change_type: ChangeType,
    old_value: Any,
    new_value: Any
) -> str:
    """Generate human-readable description of a change."""
    path_name = path.replace('.', ' > ').replace('[', ' #').replace(']', '')

    if change_type == ChangeType.ADDED:
        return f"Added {path_name}: {_truncate(new_value)}"
    elif change_type == ChangeType.REMOVED:
        return f"Removed {path_name}: {_truncate(old_value)}"
    else:
        return f"Changed {path_name}: {_truncate(old_value)} -> {_truncate(new_value)}"


def _truncate(value: Any, max_len: int = 50) -> str:
    """Truncate value for display."""
    s = str(value)
    if len(s) > max_len:
        return s[:max_len-3] + "..."
    return s


def _generate_diff_summary(changes: List[SpecChange]) -> str:
    """Generate summary of all changes."""
    if not changes:
        return "No changes detected."

    added = sum(1 for c in changes if c.change_type == ChangeType.ADDED)
    removed = sum(1 for c in changes if c.change_type == ChangeType.REMOVED)
    modified = sum(1 for c in changes if c.change_type == ChangeType.MODIFIED)

    parts = []
    if added:
        parts.append(f"{added} added")
    if removed:
        parts.append(f"{removed} removed")
    if modified:
        parts.append(f"{modified} modified")

    summary = f"{len(changes)} changes: {', '.join(parts)}"

    # Add impact note
    high_impact = [c for c in changes
                   if c.impact_level in (ImpactLevel.HIGH, ImpactLevel.CRITICAL)]
    if high_impact:
        summary += f". {len(high_impact)} high-impact changes require plan updates."

    return summary


def assess_plan_impact(
    diff_result: DiffResult,
    current_status: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Assess how spec changes impact the current plan status.

    Args:
        diff_result: Result from compute_diff()
        current_status: Current status.json content

    Returns:
        Dict with:
            - tasks_to_review: List of task IDs that need review
            - tasks_unaffected: List of task IDs not affected
            - phases_affected: Set of affected phase names
            - recommended_action: "continue", "partial_replan", or "full_replan"
    """
    if not diff_result.has_changes():
        return {
            'tasks_to_review': [],
            'tasks_unaffected': [t['id'] for t in current_status.get('tasks', [])],
            'phases_affected': set(),
            'recommended_action': 'continue',
        }

    affected_phases = diff_result.get_affected_phases()
    tasks = current_status.get('tasks', [])

    tasks_to_review = []
    tasks_unaffected = []

    for task in tasks:
        task_phase = task.get('phase', '')
        task_status = task.get('status', '')

        # Check if task is in an affected phase
        phase_affected = any(phase in task_phase for phase in affected_phases)

        if phase_affected:
            # Completed tasks in affected phases need review
            if task_status == 'done':
                tasks_to_review.append(task['id'])
            # Pending tasks in affected phases also need review
            elif task_status == 'pending':
                tasks_to_review.append(task['id'])
            else:
                tasks_to_review.append(task['id'])
        else:
            tasks_unaffected.append(task['id'])

    # Determine recommended action
    if diff_result.overall_impact == ImpactLevel.CRITICAL:
        recommended_action = 'full_replan'
    elif diff_result.overall_impact == ImpactLevel.HIGH:
        recommended_action = 'partial_replan'
    elif len(tasks_to_review) > len(tasks) / 2:
        recommended_action = 'partial_replan'
    else:
        recommended_action = 'continue'

    return {
        'tasks_to_review': tasks_to_review,
        'tasks_unaffected': tasks_unaffected,
        'phases_affected': affected_phases,
        'recommended_action': recommended_action,
    }
