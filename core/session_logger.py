# core/session_logger.py
"""
Session logging and compaction for Kearney AI Coding Assistant projects.

Manages:
- Session logs for completed work
- Context compaction for long sessions
- Session recovery after context loss

Usage:
    from core.session_logger import (
        start_session,
        log_task_completion,
        log_decision,
        log_issue,
        compact_session,
        get_session_summary,
    )

    # Start tracking
    session = start_session()

    # Log completed work
    log_task_completion("2.1", "Created revenue chart", "outputs/charts/revenue.png")

    # Compact when context gets long
    compact_session("Context getting long, saving state")
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, asdict, field


# Directory paths (relative to project root)
LOGS_DIR = Path("project_state/logs")
SESSIONS_DIR = LOGS_DIR / "sessions"
COMMANDS_DIR = LOGS_DIR / "commands"


@dataclass
class TaskLog:
    """Log entry for a completed task."""
    task_id: str
    description: str
    output: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    notes: Optional[str] = None


@dataclass
class DecisionLog:
    """Log entry for a decision made during the session."""
    decision: str
    reason: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class IssueLog:
    """Log entry for an issue encountered."""
    issue: str
    resolution: Optional[str] = None
    resolved: bool = False
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class SessionLog:
    """Complete log for a session."""
    session_id: str
    started_at: str
    ended_at: Optional[str] = None
    tasks_completed: List[TaskLog] = field(default_factory=list)
    decisions: List[DecisionLog] = field(default_factory=list)
    issues: List[IssueLog] = field(default_factory=list)
    next_task: Optional[str] = None
    summary: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "session_id": self.session_id,
            "started_at": self.started_at,
            "ended_at": self.ended_at,
            "tasks_completed": [asdict(t) for t in self.tasks_completed],
            "decisions": [asdict(d) for d in self.decisions],
            "issues": [asdict(i) for i in self.issues],
            "next_task": self.next_task,
            "summary": self.summary,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SessionLog":
        """Create from dictionary."""
        return cls(
            session_id=data["session_id"],
            started_at=data["started_at"],
            ended_at=data.get("ended_at"),
            tasks_completed=[TaskLog(**t) for t in data.get("tasks_completed", [])],
            decisions=[DecisionLog(**d) for d in data.get("decisions", [])],
            issues=[IssueLog(**i) for i in data.get("issues", [])],
            next_task=data.get("next_task"),
            summary=data.get("summary"),
        )


# Global current session
_current_session: Optional[SessionLog] = None


def _ensure_dirs() -> None:
    """Ensure log directories exist."""
    SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
    COMMANDS_DIR.mkdir(parents=True, exist_ok=True)


def _generate_session_id() -> str:
    """Generate a unique session ID."""
    return datetime.now().strftime("%Y-%m-%d_%H%M%S")


def start_session() -> SessionLog:
    """
    Start a new session log.

    Returns:
        The new SessionLog instance
    """
    global _current_session

    _ensure_dirs()

    session_id = _generate_session_id()
    _current_session = SessionLog(
        session_id=session_id,
        started_at=datetime.now().isoformat(),
    )

    return _current_session


def get_current_session() -> Optional[SessionLog]:
    """
    Get the current session.

    Returns:
        Current SessionLog or None if no session started
    """
    return _current_session


def log_task_completion(
    task_id: str,
    description: str,
    output: Optional[str] = None,
    notes: Optional[str] = None
) -> TaskLog:
    """
    Log a completed task.

    Args:
        task_id: ID of the completed task
        description: Brief description of what was done
        output: Path to any output file created
        notes: Additional notes

    Returns:
        The created TaskLog
    """
    global _current_session

    if _current_session is None:
        start_session()

    task_log = TaskLog(
        task_id=task_id,
        description=description,
        output=output,
        notes=notes,
    )
    _current_session.tasks_completed.append(task_log)

    return task_log


def log_decision(decision: str, reason: Optional[str] = None) -> DecisionLog:
    """
    Log a decision made during the session.

    Args:
        decision: The decision that was made
        reason: Why the decision was made

    Returns:
        The created DecisionLog
    """
    global _current_session

    if _current_session is None:
        start_session()

    decision_log = DecisionLog(decision=decision, reason=reason)
    _current_session.decisions.append(decision_log)

    return decision_log


def log_issue(
    issue: str,
    resolution: Optional[str] = None,
    resolved: bool = False
) -> IssueLog:
    """
    Log an issue encountered during the session.

    Args:
        issue: Description of the issue
        resolution: How it was resolved (if resolved)
        resolved: Whether the issue is resolved

    Returns:
        The created IssueLog
    """
    global _current_session

    if _current_session is None:
        start_session()

    issue_log = IssueLog(issue=issue, resolution=resolution, resolved=resolved)
    _current_session.issues.append(issue_log)

    return issue_log


def save_session(session: Optional[SessionLog] = None) -> Path:
    """
    Save session to a log file.

    Args:
        session: Session to save (defaults to current session)

    Returns:
        Path to the saved log file
    """
    _ensure_dirs()

    session = session or _current_session
    if session is None:
        raise ValueError("No session to save")

    session.ended_at = datetime.now().isoformat()

    # Save as JSON for machine readability
    json_path = SESSIONS_DIR / f"session_{session.session_id}.json"
    json_path.write_text(json.dumps(session.to_dict(), indent=2))

    # Also save as Markdown for human readability
    md_path = SESSIONS_DIR / f"session_{session.session_id}.md"
    md_path.write_text(_session_to_markdown(session))

    return md_path


def _session_to_markdown(session: SessionLog) -> str:
    """Convert session to markdown format."""
    lines = [
        f"# Session Log: {session.session_id}",
        "",
        "## Session Summary",
        "",
        f"**Started**: {session.started_at}",
        f"**Ended**: {session.ended_at or 'In Progress'}",
        f"**Tasks Completed**: {len(session.tasks_completed)}",
        "",
    ]

    if session.summary:
        lines.extend([
            "## Summary",
            "",
            session.summary,
            "",
        ])

    if session.tasks_completed:
        lines.extend([
            "## Work Completed",
            "",
        ])
        for task in session.tasks_completed:
            lines.append(f"### Task {task.task_id}: {task.description}")
            if task.output:
                lines.append(f"- Output: {task.output}")
            if task.notes:
                lines.append(f"- Notes: {task.notes}")
            lines.append("")

    if session.decisions:
        lines.extend([
            "## Decisions Made",
            "",
        ])
        for decision in session.decisions:
            lines.append(f"- {decision.decision}")
            if decision.reason:
                lines.append(f"  - Reason: {decision.reason}")
        lines.append("")

    if session.issues:
        lines.extend([
            "## Issues Encountered",
            "",
        ])
        for issue in session.issues:
            status = "Resolved" if issue.resolved else "Open"
            lines.append(f"- [{status}] {issue.issue}")
            if issue.resolution:
                lines.append(f"  - Resolution: {issue.resolution}")
        lines.append("")

    if session.next_task:
        lines.extend([
            "## Next Up",
            "",
            f"- {session.next_task}",
            "",
        ])

    lines.extend([
        "---",
        "",
        "*Generated by Kearney AI Coding Assistant Session Logger*",
    ])

    return "\n".join(lines)


def compact_session(reason: Optional[str] = None, next_task: Optional[str] = None) -> Dict[str, Any]:
    """
    Compact the current session by saving it and generating a summary.

    This is used when Claude's context is getting full.

    Args:
        reason: Why compaction was triggered
        next_task: What task to continue with after compaction

    Returns:
        Dict with summary information for context reset
    """
    global _current_session

    if _current_session is None:
        return {"status": "no_session", "message": "No active session to compact"}

    # Generate summary
    summary_lines = []
    if reason:
        summary_lines.append(f"Compacted: {reason}")

    summary_lines.append(f"Tasks completed: {len(_current_session.tasks_completed)}")

    if _current_session.tasks_completed:
        summary_lines.append("Completed:")
        for task in _current_session.tasks_completed:
            summary_lines.append(f"  - {task.task_id}: {task.description}")

    if _current_session.decisions:
        summary_lines.append(f"Key decisions: {len(_current_session.decisions)}")

    if _current_session.issues:
        open_issues = [i for i in _current_session.issues if not i.resolved]
        if open_issues:
            summary_lines.append(f"Open issues: {len(open_issues)}")

    _current_session.summary = "\n".join(summary_lines)
    _current_session.next_task = next_task

    # Save the session
    log_path = save_session(_current_session)

    # Prepare result
    result = {
        "status": "compacted",
        "session_id": _current_session.session_id,
        "log_path": str(log_path),
        "tasks_completed": len(_current_session.tasks_completed),
        "next_task": next_task,
        "summary": _current_session.summary,
    }

    # Start a fresh session
    _current_session = None
    start_session()

    return result


def get_session_summary() -> str:
    """
    Get a summary of the current session for context management.

    Returns:
        Summary string
    """
    if _current_session is None:
        return "No active session."

    lines = [
        f"Session: {_current_session.session_id}",
        f"Started: {_current_session.started_at}",
        f"Tasks completed: {len(_current_session.tasks_completed)}",
    ]

    if _current_session.tasks_completed:
        lines.append("Recent tasks:")
        for task in _current_session.tasks_completed[-3:]:  # Last 3 tasks
            lines.append(f"  - {task.task_id}: {task.description}")

    open_issues = [i for i in _current_session.issues if not i.resolved]
    if open_issues:
        lines.append(f"Open issues: {len(open_issues)}")

    return "\n".join(lines)


def load_session(session_id: str) -> Optional[SessionLog]:
    """
    Load a previous session from logs.

    Args:
        session_id: ID of the session to load

    Returns:
        SessionLog or None if not found
    """
    json_path = SESSIONS_DIR / f"session_{session_id}.json"

    if not json_path.exists():
        return None

    data = json.loads(json_path.read_text())
    return SessionLog.from_dict(data)


def list_sessions() -> List[Dict[str, Any]]:
    """
    List all available session logs.

    Returns:
        List of session info dicts
    """
    _ensure_dirs()

    sessions = []
    for json_file in sorted(SESSIONS_DIR.glob("session_*.json"), reverse=True):
        try:
            data = json.loads(json_file.read_text())
            sessions.append({
                "session_id": data.get("session_id"),
                "started_at": data.get("started_at"),
                "ended_at": data.get("ended_at"),
                "tasks_completed": len(data.get("tasks_completed", [])),
            })
        except (json.JSONDecodeError, KeyError):
            continue

    return sessions


def get_recent_session() -> Optional[SessionLog]:
    """
    Get the most recent completed session.

    Returns:
        Most recent SessionLog or None
    """
    sessions = list_sessions()
    if not sessions:
        return None

    return load_session(sessions[0]["session_id"])


def resume_from_session(session: SessionLog) -> str:
    """
    Generate a context restoration message from a previous session.

    Args:
        session: The session to resume from

    Returns:
        Message describing what was done and what's next
    """
    lines = [
        f"Resuming from session {session.session_id}",
        "",
        f"Previously completed {len(session.tasks_completed)} tasks:",
    ]

    for task in session.tasks_completed:
        lines.append(f"  - {task.task_id}: {task.description}")

    if session.decisions:
        lines.append("")
        lines.append("Key decisions from last session:")
        for decision in session.decisions:
            lines.append(f"  - {decision.decision}")

    open_issues = [i for i in session.issues if not i.resolved]
    if open_issues:
        lines.append("")
        lines.append("Outstanding issues:")
        for issue in open_issues:
            lines.append(f"  - {issue.issue}")

    if session.next_task:
        lines.append("")
        lines.append(f"Next up: {session.next_task}")

    return "\n".join(lines)


def log_command(command: str, args: Optional[Dict[str, Any]] = None) -> Path:
    """
    Log a command execution to the commands log.

    Args:
        command: The command that was executed
        args: Arguments passed to the command

    Returns:
        Path to the log file
    """
    _ensure_dirs()

    timestamp = datetime.now()
    log_entry = {
        "timestamp": timestamp.isoformat(),
        "command": command,
        "args": args or {},
    }

    # Append to daily log file
    log_file = COMMANDS_DIR / f"commands_{timestamp.strftime('%Y-%m-%d')}.jsonl"

    with open(log_file, "a") as f:
        f.write(json.dumps(log_entry) + "\n")

    return log_file
