"""
Kearney State Manager - Project State Management

Manages project_state/status.json for machine-readable state.
Enables project resumption across Claude sessions.

Usage:
    from core.state_manager import (
        init_project,
        load_state,
        update_task_status,
        get_status_summary,
    )

    # Initialize new project
    state = init_project("acme-revenue-q4", "analytics")

    # Update task status
    update_task_status("1.1", "done")

    # Get summary for display
    print(get_status_summary())
"""

import json
import re
import logging
from pathlib import Path
from datetime import datetime, timezone
from dataclasses import dataclass, asdict, field
from typing import List, Literal, Optional, Dict, Any

logger = logging.getLogger(__name__)

# File paths
STATE_FILE = Path("project_state/status.json")
PLAN_FILE = Path("project_state/plan.md")
SPEC_FILE = Path("project_state/spec.yaml")

# Type definitions
TaskStatus = Literal["pending", "in_progress", "done", "blocked"]


@dataclass
class Task:
    """Represents a single task in the project plan."""
    id: str
    phase: str
    description: str
    status: TaskStatus = "pending"
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    blocked_reason: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary, excluding None values."""
        d = asdict(self)
        return {k: v for k, v in d.items() if v is not None}


@dataclass
class ProjectState:
    """
    Represents the complete project state.

    This is persisted to project_state/status.json and enables
    project resumption across Claude sessions.
    """
    project_name: str
    template: str
    created_at: str
    updated_at: str
    current_phase: str = ""
    current_task: Optional[str] = None
    tasks: List[Task] = field(default_factory=list)
    artifacts: List[str] = field(default_factory=list)
    history: List[Dict[str, str]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "project_name": self.project_name,
            "template": self.template,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "current_phase": self.current_phase,
            "current_task": self.current_task,
            "tasks": [t.to_dict() for t in self.tasks],
            "artifacts": self.artifacts,
            "history": self.history,
        }


def _now_iso() -> str:
    """Get current UTC time in ISO format."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_state() -> Optional[ProjectState]:
    """
    Load project state from status.json.

    Returns:
        ProjectState if file exists and is valid, None otherwise.
    """
    if not STATE_FILE.exists():
        return None

    try:
        data = json.loads(STATE_FILE.read_text(encoding="utf-8"))

        tasks = [
            Task(
                id=t["id"],
                phase=t["phase"],
                description=t["description"],
                status=t.get("status", "pending"),
                started_at=t.get("started_at"),
                completed_at=t.get("completed_at"),
                blocked_reason=t.get("blocked_reason"),
            )
            for t in data.get("tasks", [])
        ]

        return ProjectState(
            project_name=data["project_name"],
            template=data["template"],
            created_at=data["created_at"],
            updated_at=data["updated_at"],
            current_phase=data.get("current_phase", ""),
            current_task=data.get("current_task"),
            tasks=tasks,
            artifacts=data.get("artifacts", []),
            history=data.get("history", []),
        )
    except (json.JSONDecodeError, KeyError) as e:
        logger.error(f"Failed to load state: {e}")
        return None


def save_state(state: ProjectState) -> None:
    """
    Save project state to status.json.

    Args:
        state: The ProjectState to save.
    """
    state.updated_at = _now_iso()

    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(
        json.dumps(state.to_dict(), indent=2),
        encoding="utf-8",
    )
    logger.info(f"State saved to {STATE_FILE}")


def init_project(project_name: str, template: str) -> ProjectState:
    """
    Initialize a new project state.

    Args:
        project_name: Name for the project (e.g., "acme-revenue-q4").
        template: Template type (e.g., "analytics", "presentation").

    Returns:
        The newly created ProjectState.
    """
    now = _now_iso()

    state = ProjectState(
        project_name=project_name,
        template=template,
        created_at=now,
        updated_at=now,
        history=[{"action": "init", "timestamp": now}],
    )

    save_state(state)
    logger.info(f"Project initialized: {project_name} ({template})")
    return state


def init_from_plan(project_name: str, template: str) -> ProjectState:
    """
    Parse plan.md and initialize tasks in status.json.

    Reads the plan file, extracts tasks marked with [ ] or [x],
    and creates the task list in the project state.

    Args:
        project_name: Name for the project.
        template: Template type.

    Returns:
        The ProjectState with tasks populated from plan.md.
    """
    state = load_state() or init_project(project_name, template)

    if not PLAN_FILE.exists():
        logger.warning(f"{PLAN_FILE} not found. No tasks parsed.")
        return state

    plan_content = PLAN_FILE.read_text(encoding="utf-8")

    # Clear existing tasks before re-parsing
    state.tasks = []

    # Parse tasks from plan.md
    # Looking for: - [ ] Task description OR - [x] Task description
    current_phase = ""
    task_id = 0
    phase_num = 0

    for line in plan_content.split("\n"):
        # Detect phase headers (## Phase X: Name)
        phase_match = re.match(r"^##\s*Phase\s*\d*:?\s*(.+)$", line, re.IGNORECASE)
        if phase_match or line.startswith("## Phase"):
            current_phase = line.replace("##", "").strip()
            phase_num += 1
            task_id = 0
            continue

        # Also detect simpler headers like "## Data Preparation"
        header_match = re.match(r"^##\s+(.+)$", line)
        if header_match and not phase_match:
            current_phase = header_match.group(1).strip()
            phase_num += 1
            task_id = 0
            continue

        # Detect tasks: - [ ] description or - [x] description
        task_match = re.match(r"^-\s*\[([ xX])\]\s*(.+)$", line)
        if task_match:
            task_id += 1
            is_done = task_match.group(1).lower() == "x"
            description = task_match.group(2).strip()

            task = Task(
                id=f"{phase_num}.{task_id}",
                phase=current_phase or f"Phase {phase_num}",
                description=description,
                status="done" if is_done else "pending",
                completed_at=_now_iso() if is_done else None,
            )
            state.tasks.append(task)

    # Set current phase and task
    pending = [t for t in state.tasks if t.status == "pending"]
    if pending:
        state.current_task = pending[0].id
        state.current_phase = pending[0].phase
    else:
        state.current_task = None
        state.current_phase = "Complete" if state.tasks else ""

    state.history.append({
        "action": "plan_parsed",
        "timestamp": _now_iso(),
        "tasks_count": str(len(state.tasks)),
    })

    save_state(state)
    logger.info(f"Parsed {len(state.tasks)} tasks from plan.md")
    return state


def update_task_status(
    task_id: str,
    status: TaskStatus,
    blocked_reason: Optional[str] = None,
) -> ProjectState:
    """
    Update a task status and advance current_task if needed.

    Args:
        task_id: The task ID (e.g., "1.2").
        status: New status ("pending", "in_progress", "done", "blocked").
        blocked_reason: Reason if status is "blocked".

    Returns:
        The updated ProjectState.

    Raises:
        ValueError: If no project state exists or task not found.
    """
    state = load_state()
    if state is None:
        raise ValueError("No project state found. Run init_project first.")

    now = _now_iso()
    task_found = False

    for task in state.tasks:
        if task.id == task_id:
            task.status = status
            if status == "in_progress":
                task.started_at = now
            elif status == "done":
                task.completed_at = now
            elif status == "blocked":
                task.blocked_reason = blocked_reason
            task_found = True
            break

    if not task_found:
        raise ValueError(f"Task {task_id} not found.")

    # Advance to next pending task if current task is done
    if status == "done":
        pending = [t for t in state.tasks if t.status == "pending"]
        if pending:
            state.current_task = pending[0].id
            state.current_phase = pending[0].phase
        else:
            # Check if any tasks are blocked
            blocked = [t for t in state.tasks if t.status == "blocked"]
            if blocked:
                state.current_task = blocked[0].id
                state.current_phase = blocked[0].phase
            else:
                state.current_task = None
                state.current_phase = "Complete"

    state.history.append({
        "action": f"task_{task_id}_{status}",
        "timestamp": now,
    })

    save_state(state)
    logger.info(f"Task {task_id} status updated to {status}")
    return state


def add_artifact(artifact_path: str) -> ProjectState:
    """
    Record a generated artifact in the project state.

    Args:
        artifact_path: Path to the artifact file.

    Returns:
        The updated ProjectState.

    Raises:
        ValueError: If no project state exists.
    """
    state = load_state()
    if state is None:
        raise ValueError("No project state found. Run init_project first.")

    if artifact_path not in state.artifacts:
        state.artifacts.append(artifact_path)
        state.history.append({
            "action": "artifact_created",
            "timestamp": _now_iso(),
            "path": artifact_path,
        })
        save_state(state)
        logger.info(f"Artifact recorded: {artifact_path}")

    return state


def get_status_summary() -> str:
    """
    Get a human-readable status summary.

    Returns:
        Formatted string with project status.
    """
    state = load_state()
    if state is None:
        return "No project initialized. Run /project:init to start."

    done = len([t for t in state.tasks if t.status == "done"])
    in_progress = len([t for t in state.tasks if t.status == "in_progress"])
    blocked = len([t for t in state.tasks if t.status == "blocked"])
    total = len(state.tasks)

    next_task = None
    for t in state.tasks:
        if t.id == state.current_task:
            next_task = t.description
            break

    lines = [
        f"Project: {state.project_name}",
        f"Template: {state.template}",
        f"Phase: {state.current_phase}",
        f"Progress: {done} / {total} tasks complete",
    ]

    if in_progress > 0:
        lines.append(f"In Progress: {in_progress} task(s)")
    if blocked > 0:
        lines.append(f"Blocked: {blocked} task(s)")
    if next_task:
        lines.append(f"Next task: {next_task}")
    if state.artifacts:
        lines.append(f"Artifacts: {len(state.artifacts)} file(s)")

    return "\n".join(lines)


def get_next_task() -> Optional[Task]:
    """
    Get the next task to work on.

    Returns the current pending or in_progress task.

    Returns:
        The next Task, or None if all tasks are complete.
    """
    state = load_state()
    if state is None:
        return None

    # First look for in_progress tasks
    for task in state.tasks:
        if task.status == "in_progress":
            return task

    # Then look for the current task
    if state.current_task:
        for task in state.tasks:
            if task.id == state.current_task:
                return task

    # Finally, find first pending task
    for task in state.tasks:
        if task.status == "pending":
            return task

    return None


def warn_if_missing_core_files() -> List[str]:
    """
    Check if core project files are missing.

    Returns:
        List of warning messages for missing files.
    """
    warnings = []

    if not SPEC_FILE.exists():
        warnings.append(f"{SPEC_FILE} not found. Run /project:interview.")

    if not PLAN_FILE.exists():
        warnings.append(f"{PLAN_FILE} not found. Run /project:plan.")

    return warnings


def mark_interview_complete() -> ProjectState:
    """
    Mark the interview phase as complete in history.

    Returns:
        The updated ProjectState.
    """
    state = load_state()
    if state is None:
        raise ValueError("No project state found.")

    state.history.append({
        "action": "interview_complete",
        "timestamp": _now_iso(),
    })

    save_state(state)
    return state


def mark_plan_approved() -> ProjectState:
    """
    Mark the plan as approved in history.

    Returns:
        The updated ProjectState.
    """
    state = load_state()
    if state is None:
        raise ValueError("No project state found.")

    state.history.append({
        "action": "plan_approved",
        "timestamp": _now_iso(),
    })

    save_state(state)
    return state


def get_task_by_id(task_id: str) -> Optional[Task]:
    """
    Get a specific task by its ID.

    Args:
        task_id: The task ID (e.g., "1.2").

    Returns:
        The Task if found, None otherwise.
    """
    state = load_state()
    if state is None:
        return None

    for task in state.tasks:
        if task.id == task_id:
            return task

    return None


def get_tasks_by_phase(phase: str) -> List[Task]:
    """
    Get all tasks in a specific phase.

    Args:
        phase: The phase name.

    Returns:
        List of tasks in that phase.
    """
    state = load_state()
    if state is None:
        return []

    return [t for t in state.tasks if t.phase == phase]


def get_completion_percentage() -> float:
    """
    Calculate project completion percentage.

    Returns:
        Percentage complete (0.0 to 100.0).
    """
    state = load_state()
    if state is None or not state.tasks:
        return 0.0

    done = len([t for t in state.tasks if t.status == "done"])
    return (done / len(state.tasks)) * 100


def main():
    """CLI entry point for state_manager."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python core/state_manager.py <command> [args]")
        print("Commands:")
        print("  status          - Show project status")
        print("  init <name> <template> - Initialize project")
        print("  parse-plan      - Parse plan.md into tasks")
        sys.exit(1)

    command = sys.argv[1]

    if command == "status":
        print(get_status_summary())
    elif command == "init":
        if len(sys.argv) < 4:
            print("Usage: python core/state_manager.py init <name> <template>")
            sys.exit(1)
        init_project(sys.argv[2], sys.argv[3])
        print(f"Project initialized: {sys.argv[2]}")
    elif command == "parse-plan":
        state = load_state()
        if state:
            init_from_plan(state.project_name, state.template)
            print(get_status_summary())
        else:
            print("No project initialized. Run init first.")
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
