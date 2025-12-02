# core/spec_manager.py
"""
Specification manager for Living Requirements System.
Handles spec.yaml CRUD operations with versioning and changelog.

The spec.yaml is the source of truth for project requirements.
All changes are versioned in spec_history/.
"""

from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field, asdict

import yaml


# Paths
SPEC_FILE = Path('project_state/spec.yaml')
SPEC_HISTORY_DIR = Path('project_state/spec_history')
CHANGELOG_FILE = SPEC_HISTORY_DIR / 'changelog.md'


@dataclass
class SpecMeta:
    """Metadata section of spec."""
    project_name: str
    project_type: str
    client: Optional[str] = None
    deadline: Optional[str] = None
    stakeholders: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class SpecProblem:
    """Problem definition section."""
    business_question: str = ""
    success_criteria: List[str] = field(default_factory=list)


@dataclass
class SpecData:
    """Data sources section."""
    sources: List[Dict[str, Any]] = field(default_factory=list)
    quality_notes: List[str] = field(default_factory=list)
    sensitive_fields: List[str] = field(default_factory=list)


@dataclass
class Specification:
    """
    Complete project specification.

    This is the source of truth for all project requirements.
    Type-specific sections (modeling, presentation, etc.) are stored
    in the type_specific dict keyed by project_type.
    """
    version: int
    created_at: str
    updated_at: str
    meta: SpecMeta
    problem: SpecProblem = field(default_factory=SpecProblem)
    data: SpecData = field(default_factory=SpecData)
    deliverables: List[Dict[str, Any]] = field(default_factory=list)
    constraints: Dict[str, Any] = field(default_factory=dict)
    notes: List[str] = field(default_factory=list)
    type_specific: Dict[str, Any] = field(default_factory=dict)


def _ensure_dirs() -> None:
    """Ensure required directories exist."""
    SPEC_FILE.parent.mkdir(parents=True, exist_ok=True)
    SPEC_HISTORY_DIR.mkdir(parents=True, exist_ok=True)


def _now_iso() -> str:
    """Get current time in ISO format."""
    return datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')


def _spec_to_dict(spec: Specification) -> Dict[str, Any]:
    """Convert Specification to dict for YAML serialization."""
    data = {
        'version': spec.version,
        'created_at': spec.created_at,
        'updated_at': spec.updated_at,
        'meta': asdict(spec.meta),
        'problem': asdict(spec.problem),
        'data': asdict(spec.data),
        'deliverables': spec.deliverables,
        'constraints': spec.constraints,
        'notes': spec.notes,
    }
    # Add type-specific section with project_type as key
    if spec.type_specific:
        data[spec.meta.project_type] = spec.type_specific
    return data


def _dict_to_spec(data: Dict[str, Any]) -> Specification:
    """Convert dict from YAML to Specification object."""
    meta = SpecMeta(
        project_name=data.get('meta', {}).get('project_name', ''),
        project_type=data.get('meta', {}).get('project_type', ''),
        client=data.get('meta', {}).get('client'),
        deadline=data.get('meta', {}).get('deadline'),
        stakeholders=data.get('meta', {}).get('stakeholders', []),
    )

    problem = SpecProblem(
        business_question=data.get('problem', {}).get('business_question', ''),
        success_criteria=data.get('problem', {}).get('success_criteria', []),
    )

    data_section = SpecData(
        sources=data.get('data', {}).get('sources', []),
        quality_notes=data.get('data', {}).get('quality_notes', []),
        sensitive_fields=data.get('data', {}).get('sensitive_fields', []),
    )

    # Extract type-specific section
    project_type = meta.project_type
    type_specific = data.get(project_type, {}) if project_type else {}

    return Specification(
        version=data.get('version', 1),
        created_at=data.get('created_at', ''),
        updated_at=data.get('updated_at', ''),
        meta=meta,
        problem=problem,
        data=data_section,
        deliverables=data.get('deliverables', []),
        constraints=data.get('constraints', {}),
        notes=data.get('notes', []),
        type_specific=type_specific,
    )


def load_spec() -> Optional[Specification]:
    """
    Load current specification from spec.yaml.

    Returns:
        Specification object or None if file doesn't exist.
    """
    if not SPEC_FILE.exists():
        return None

    content = SPEC_FILE.read_text(encoding='utf-8')
    data = yaml.safe_load(content)
    return _dict_to_spec(data)


def save_spec(spec: Specification, changelog_entry: Optional[str] = None) -> None:
    """
    Save specification to spec.yaml.

    If this is a version update (version > 1), archives the old version
    and updates the changelog.

    Args:
        spec: The specification to save.
        changelog_entry: Description of changes for changelog.
    """
    _ensure_dirs()

    # Archive current version if it exists and we're updating
    if SPEC_FILE.exists():
        old_spec = load_spec()
        if old_spec and old_spec.version < spec.version:
            _archive_version(old_spec)

    # Update timestamp
    spec.updated_at = _now_iso()

    # Write new spec
    data = _spec_to_dict(spec)
    content = yaml.dump(data, default_flow_style=False, sort_keys=False, allow_unicode=True)
    SPEC_FILE.write_text(content, encoding='utf-8')

    # Update changelog
    if changelog_entry:
        _update_changelog(spec.version, changelog_entry)


def _archive_version(spec: Specification) -> None:
    """Archive a spec version to history."""
    archive_path = SPEC_HISTORY_DIR / f'spec_v{spec.version}.yaml'
    data = _spec_to_dict(spec)
    content = yaml.dump(data, default_flow_style=False, sort_keys=False, allow_unicode=True)
    archive_path.write_text(content, encoding='utf-8')


def _update_changelog(version: int, entry: str) -> None:
    """Append entry to changelog."""
    timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M')

    new_entry = f"\n## Version {version} ({timestamp})\n- {entry}\n"

    if CHANGELOG_FILE.exists():
        content = CHANGELOG_FILE.read_text(encoding='utf-8')
        # Insert new entry after header
        if '# Specification Changelog' in content:
            parts = content.split('\n## ', 1)
            if len(parts) == 2:
                content = parts[0] + new_entry + '\n## ' + parts[1]
            else:
                content = content + new_entry
        else:
            content = "# Specification Changelog\n" + new_entry + content
    else:
        content = "# Specification Changelog\n" + new_entry

    CHANGELOG_FILE.write_text(content, encoding='utf-8')


def create_spec(
    project_name: str,
    project_type: str,
    client: Optional[str] = None,
    deadline: Optional[str] = None,
) -> Specification:
    """
    Create a new specification.

    Args:
        project_name: Name of the project.
        project_type: Type (modeling, presentation, etc.).
        client: Optional client name.
        deadline: Optional deadline.

    Returns:
        New Specification object.
    """
    now = _now_iso()

    meta = SpecMeta(
        project_name=project_name,
        project_type=project_type,
        client=client,
        deadline=deadline,
    )

    spec = Specification(
        version=1,
        created_at=now,
        updated_at=now,
        meta=meta,
    )

    return spec


def get_version() -> int:
    """Get current spec version, or 0 if no spec exists."""
    spec = load_spec()
    return spec.version if spec else 0


def increment_version(spec: Specification) -> Specification:
    """Increment spec version for a new edit."""
    spec.version += 1
    return spec


def get_section(spec: Specification, section_path: str) -> Any:
    """
    Get a section or field from spec by dot-notation path.

    Examples:
        get_section(spec, 'meta.project_name')
        get_section(spec, 'modeling.validation')

    Args:
        spec: The specification.
        section_path: Dot-notation path to section.

    Returns:
        The section value or None if not found.
    """
    parts = section_path.split('.')
    current = _spec_to_dict(spec)

    for part in parts:
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return None

    return current


def set_section(spec: Specification, section_path: str, value: Any) -> Specification:
    """
    Set a section or field in spec by dot-notation path.

    Args:
        spec: The specification to modify.
        section_path: Dot-notation path to section.
        value: New value to set.

    Returns:
        Modified specification.
    """
    parts = section_path.split('.')

    # Convert to dict, modify, convert back
    data = _spec_to_dict(spec)

    # Navigate to parent and set value
    current = data
    for part in parts[:-1]:
        if part not in current:
            current[part] = {}
        current = current[part]

    current[parts[-1]] = value

    return _dict_to_spec(data)


def get_history() -> List[Dict[str, Any]]:
    """
    Get list of archived versions.

    Returns:
        List of dicts with version number and path.
    """
    if not SPEC_HISTORY_DIR.exists():
        return []

    versions = []
    for path in sorted(SPEC_HISTORY_DIR.glob('spec_v*.yaml')):
        version_num = int(path.stem.replace('spec_v', ''))
        versions.append({
            'version': version_num,
            'path': str(path),
        })

    return versions


def load_version(version: int) -> Optional[Specification]:
    """
    Load a specific version from history.

    Args:
        version: Version number to load.

    Returns:
        Specification or None if version not found.
    """
    path = SPEC_HISTORY_DIR / f'spec_v{version}.yaml'
    if not path.exists():
        return None

    content = path.read_text(encoding='utf-8')
    data = yaml.safe_load(content)
    return _dict_to_spec(data)


def rollback_to_version(version: int) -> Optional[Specification]:
    """
    Rollback to a previous version.

    Archives current version and restores the specified version
    as a new version.

    Args:
        version: Version to rollback to.

    Returns:
        New specification (rolled back) or None if version not found.
    """
    old_spec = load_version(version)
    if old_spec is None:
        return None

    current = load_spec()
    if current:
        # Archive current before rollback
        _archive_version(current)
        new_version = current.version + 1
    else:
        new_version = 1

    old_spec.version = new_version
    save_spec(old_spec, f"Rolled back to version {version}")

    return old_spec


def get_changelog() -> str:
    """Get changelog contents."""
    if not CHANGELOG_FILE.exists():
        return "# Specification Changelog\n\nNo changes recorded yet."
    return CHANGELOG_FILE.read_text(encoding='utf-8')


def analyze_impact(spec: Specification, changes: Dict[str, Any]) -> Dict[str, List[str]]:
    """
    Analyze impact of proposed changes on plan and completed work.

    Args:
        spec: Current specification.
        changes: Proposed changes as dot-notation paths to new values.

    Returns:
        Dict with 'plan_impact', 'work_impact', 'metrics_change' lists.
    """
    impact = {
        'plan_impact': [],
        'work_impact': [],
        'metrics_change': [],
    }

    for path, new_value in changes.items():
        old_value = get_section(spec, path)

        # Detect major changes
        if 'problem_type' in path:
            impact['plan_impact'].append(f"Problem type changing from {old_value} to {new_value}")
            impact['work_impact'].append("Model training tasks will need to be re-executed")

        if 'target_variable' in path:
            impact['plan_impact'].append(f"Target variable changing from {old_value} to {new_value}")
            impact['work_impact'].append("Feature engineering may need adjustment")

        if 'validation' in path and 'metrics' in path:
            impact['metrics_change'].append(f"Validation metrics changing")

        if 'deliverables' in path:
            impact['plan_impact'].append("Deliverables list changing - plan may need new tasks")

    return impact


def spec_exists() -> bool:
    """Check if spec.yaml exists."""
    return SPEC_FILE.exists()


def get_spec_summary(spec: Specification) -> str:
    """
    Get a human-readable summary of the spec.

    Args:
        spec: The specification.

    Returns:
        Formatted summary string.
    """
    lines = [
        f"PROJECT: {spec.meta.project_name}",
        f"TYPE: {spec.meta.project_type}",
        f"VERSION: {spec.version}",
    ]

    if spec.meta.client:
        lines.append(f"CLIENT: {spec.meta.client}")

    if spec.meta.deadline:
        lines.append(f"DEADLINE: {spec.meta.deadline}")

    if spec.problem.business_question:
        lines.append(f"\nBUSINESS QUESTION:\n{spec.problem.business_question}")

    if spec.deliverables:
        lines.append(f"\nDELIVERABLES: {len(spec.deliverables)} items")
        for d in spec.deliverables[:3]:
            dtype = d.get('type', 'unknown')
            lines.append(f"  - {dtype}")
        if len(spec.deliverables) > 3:
            lines.append(f"  ... and {len(spec.deliverables) - 3} more")

    return '\n'.join(lines)
