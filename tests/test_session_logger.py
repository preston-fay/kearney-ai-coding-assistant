# tests/test_session_logger.py
"""Tests for core/session_logger.py"""

import json
import pytest
import sys
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.session_logger import (
    TaskLog,
    DecisionLog,
    IssueLog,
    SessionLog,
    start_session,
    get_current_session,
    log_task_completion,
    log_decision,
    log_issue,
    save_session,
    compact_session,
    get_session_summary,
    load_session,
    list_sessions,
    get_recent_session,
    resume_from_session,
    log_command,
    _current_session,
    SESSIONS_DIR,
    COMMANDS_DIR,
)

# Import the module to reset global state
import core.session_logger as session_logger_module


@pytest.fixture(autouse=True)
def reset_session():
    """Reset the global session state before each test."""
    session_logger_module._current_session = None
    yield
    session_logger_module._current_session = None


@pytest.fixture
def mock_logs_dir(tmp_path, monkeypatch):
    """Use temporary directory for logs."""
    logs_dir = tmp_path / "project_state" / "logs"
    sessions_dir = logs_dir / "sessions"
    commands_dir = logs_dir / "commands"
    sessions_dir.mkdir(parents=True)
    commands_dir.mkdir(parents=True)

    monkeypatch.setattr(session_logger_module, "LOGS_DIR", logs_dir)
    monkeypatch.setattr(session_logger_module, "SESSIONS_DIR", sessions_dir)
    monkeypatch.setattr(session_logger_module, "COMMANDS_DIR", commands_dir)

    return tmp_path


class TestTaskLog:
    """Tests for TaskLog dataclass."""

    def test_task_log_creation(self):
        """Test creating a task log."""
        task = TaskLog(
            task_id="1.1",
            description="Create chart",
            output="outputs/chart.png"
        )
        assert task.task_id == "1.1"
        assert task.description == "Create chart"
        assert task.output == "outputs/chart.png"
        assert task.timestamp is not None

    def test_task_log_optional_fields(self):
        """Test task log with optional fields."""
        task = TaskLog(task_id="1.1", description="Task")
        assert task.output is None
        assert task.notes is None


class TestDecisionLog:
    """Tests for DecisionLog dataclass."""

    def test_decision_log_creation(self):
        """Test creating a decision log."""
        decision = DecisionLog(
            decision="Use bar chart",
            reason="Client preference"
        )
        assert decision.decision == "Use bar chart"
        assert decision.reason == "Client preference"

    def test_decision_log_without_reason(self):
        """Test decision log without reason."""
        decision = DecisionLog(decision="Skip APAC data")
        assert decision.reason is None


class TestIssueLog:
    """Tests for IssueLog dataclass."""

    def test_issue_log_creation(self):
        """Test creating an issue log."""
        issue = IssueLog(
            issue="Data missing",
            resolution="Used fallback",
            resolved=True
        )
        assert issue.issue == "Data missing"
        assert issue.resolved is True

    def test_issue_log_unresolved(self):
        """Test unresolved issue log."""
        issue = IssueLog(issue="Need clarification")
        assert issue.resolved is False
        assert issue.resolution is None


class TestSessionLog:
    """Tests for SessionLog dataclass."""

    def test_session_log_creation(self):
        """Test creating a session log."""
        session = SessionLog(
            session_id="2025-12-01_143022",
            started_at="2025-12-01T14:30:22"
        )
        assert session.session_id == "2025-12-01_143022"
        assert len(session.tasks_completed) == 0
        assert len(session.decisions) == 0
        assert len(session.issues) == 0

    def test_session_log_to_dict(self):
        """Test converting session to dict."""
        session = SessionLog(
            session_id="test",
            started_at="2025-12-01T14:30:22"
        )
        session.tasks_completed.append(
            TaskLog(task_id="1.1", description="Test task")
        )

        data = session.to_dict()

        assert data["session_id"] == "test"
        assert len(data["tasks_completed"]) == 1
        assert data["tasks_completed"][0]["task_id"] == "1.1"

    def test_session_log_from_dict(self):
        """Test creating session from dict."""
        data = {
            "session_id": "test",
            "started_at": "2025-12-01T14:30:22",
            "ended_at": None,
            "tasks_completed": [
                {"task_id": "1.1", "description": "Task", "timestamp": "2025-12-01T14:30:22"}
            ],
            "decisions": [],
            "issues": [],
            "next_task": None,
            "summary": None,
        }

        session = SessionLog.from_dict(data)

        assert session.session_id == "test"
        assert len(session.tasks_completed) == 1
        assert session.tasks_completed[0].task_id == "1.1"


class TestStartSession:
    """Tests for start_session function."""

    def test_start_session_creates_session(self, mock_logs_dir):
        """Test that start_session creates a new session."""
        session = start_session()

        assert session is not None
        assert session.session_id is not None
        assert session.started_at is not None

    def test_start_session_sets_global(self, mock_logs_dir):
        """Test that start_session sets the global current session."""
        session = start_session()
        current = get_current_session()

        assert current is session


class TestLogTaskCompletion:
    """Tests for log_task_completion function."""

    def test_log_task_creates_entry(self, mock_logs_dir):
        """Test logging a task completion."""
        start_session()
        task = log_task_completion("1.1", "Created chart", "outputs/chart.png")

        assert task.task_id == "1.1"
        assert task.description == "Created chart"

        session = get_current_session()
        assert len(session.tasks_completed) == 1

    def test_log_task_auto_starts_session(self, mock_logs_dir):
        """Test that logging auto-starts a session if none exists."""
        task = log_task_completion("1.1", "Task")

        session = get_current_session()
        assert session is not None
        assert len(session.tasks_completed) == 1

    def test_log_multiple_tasks(self, mock_logs_dir):
        """Test logging multiple tasks."""
        start_session()
        log_task_completion("1.1", "Task 1")
        log_task_completion("1.2", "Task 2")
        log_task_completion("1.3", "Task 3")

        session = get_current_session()
        assert len(session.tasks_completed) == 3


class TestLogDecision:
    """Tests for log_decision function."""

    def test_log_decision_creates_entry(self, mock_logs_dir):
        """Test logging a decision."""
        start_session()
        decision = log_decision("Use bar chart", "Client preference")

        assert decision.decision == "Use bar chart"
        assert decision.reason == "Client preference"

        session = get_current_session()
        assert len(session.decisions) == 1


class TestLogIssue:
    """Tests for log_issue function."""

    def test_log_issue_creates_entry(self, mock_logs_dir):
        """Test logging an issue."""
        start_session()
        issue = log_issue("Missing data", "Used fallback", resolved=True)

        assert issue.issue == "Missing data"
        assert issue.resolved is True

        session = get_current_session()
        assert len(session.issues) == 1


class TestSaveSession:
    """Tests for save_session function."""

    def test_save_session_creates_files(self, mock_logs_dir):
        """Test that save_session creates log files."""
        session = start_session()
        log_task_completion("1.1", "Test task")

        path = save_session()

        assert path.exists()
        assert path.suffix == ".md"

        # JSON file should also exist
        json_path = path.with_suffix(".json")
        assert json_path.exists()

    def test_save_session_sets_ended_at(self, mock_logs_dir):
        """Test that save_session sets ended_at."""
        session = start_session()
        save_session()

        # Reload and check
        loaded = load_session(session.session_id)
        assert loaded.ended_at is not None

    def test_save_session_no_session_raises(self, mock_logs_dir):
        """Test that save_session raises if no session."""
        with pytest.raises(ValueError, match="No session"):
            save_session()


class TestCompactSession:
    """Tests for compact_session function."""

    def test_compact_session_saves_and_resets(self, mock_logs_dir):
        """Test that compact saves and resets the session."""
        start_session()
        log_task_completion("1.1", "Task 1")
        log_task_completion("1.2", "Task 2")
        log_decision("Decision 1")

        result = compact_session(reason="Test", next_task="Task 3")

        assert result["status"] == "compacted"
        assert result["tasks_completed"] == 2
        assert result["next_task"] == "Task 3"
        assert "log_path" in result

        # New session should be started
        new_session = get_current_session()
        assert new_session is not None
        assert len(new_session.tasks_completed) == 0

    def test_compact_no_session(self, mock_logs_dir):
        """Test compact when no session exists."""
        result = compact_session()

        assert result["status"] == "no_session"


class TestGetSessionSummary:
    """Tests for get_session_summary function."""

    def test_summary_no_session(self, mock_logs_dir):
        """Test summary when no session."""
        summary = get_session_summary()
        assert "No active session" in summary

    def test_summary_with_tasks(self, mock_logs_dir):
        """Test summary with tasks."""
        start_session()
        log_task_completion("1.1", "Task 1")
        log_task_completion("1.2", "Task 2")

        summary = get_session_summary()

        assert "Tasks completed: 2" in summary
        assert "1.1" in summary or "1.2" in summary


class TestLoadSession:
    """Tests for load_session function."""

    def test_load_existing_session(self, mock_logs_dir):
        """Test loading an existing session."""
        session = start_session()
        log_task_completion("1.1", "Test")
        save_session()

        loaded = load_session(session.session_id)

        assert loaded is not None
        assert loaded.session_id == session.session_id
        assert len(loaded.tasks_completed) == 1

    def test_load_nonexistent_session(self, mock_logs_dir):
        """Test loading a non-existent session."""
        loaded = load_session("nonexistent")
        assert loaded is None


class TestListSessions:
    """Tests for list_sessions function."""

    def test_list_empty(self, mock_logs_dir):
        """Test listing when no sessions."""
        sessions = list_sessions()
        assert sessions == []

    def test_list_multiple_sessions(self, mock_logs_dir):
        """Test listing multiple sessions."""
        import time

        # Create and save first session
        session1 = start_session()
        log_task_completion("1.1", "Task")
        save_session()

        # Wait to ensure different timestamp
        time.sleep(1.1)

        # Reset and create second session
        session_logger_module._current_session = None
        session2 = start_session()
        log_task_completion("2.1", "Task")
        save_session()

        sessions = list_sessions()

        assert len(sessions) == 2


class TestResumeFromSession:
    """Tests for resume_from_session function."""

    def test_resume_generates_context(self, mock_logs_dir):
        """Test that resume generates context message."""
        session = start_session()
        log_task_completion("1.1", "Created chart")
        log_decision("Use bar chart")
        session.next_task = "Task 2.1"
        save_session()

        loaded = load_session(session.session_id)
        message = resume_from_session(loaded)

        assert "Resuming" in message
        assert "1.1" in message
        assert "Created chart" in message
        assert "Use bar chart" in message
        assert "Task 2.1" in message


class TestLogCommand:
    """Tests for log_command function."""

    def test_log_command_creates_entry(self, mock_logs_dir):
        """Test logging a command."""
        path = log_command("/project:execute", {"task": "1.1"})

        assert path.exists()

        # Read and verify
        content = path.read_text()
        lines = content.strip().split("\n")
        entry = json.loads(lines[-1])

        assert entry["command"] == "/project:execute"
        assert entry["args"]["task"] == "1.1"

    def test_log_command_appends(self, mock_logs_dir):
        """Test that log_command appends to existing file."""
        log_command("/project:status")
        log_command("/project:execute")
        path = log_command("/project:review")

        content = path.read_text()
        lines = content.strip().split("\n")

        assert len(lines) == 3


class TestSessionMarkdownFormat:
    """Tests for markdown generation."""

    def test_markdown_includes_tasks(self, mock_logs_dir):
        """Test that markdown includes tasks."""
        session = start_session()
        log_task_completion("1.1", "Created chart", "outputs/chart.png")
        path = save_session()

        content = path.read_text()

        assert "Task 1.1" in content
        assert "Created chart" in content
        assert "outputs/chart.png" in content

    def test_markdown_includes_decisions(self, mock_logs_dir):
        """Test that markdown includes decisions."""
        session = start_session()
        log_decision("Use bar chart", "Client preference")
        path = save_session()

        content = path.read_text()

        assert "Decisions Made" in content
        assert "Use bar chart" in content
        assert "Client preference" in content

    def test_markdown_includes_issues(self, mock_logs_dir):
        """Test that markdown includes issues."""
        session = start_session()
        log_issue("Missing data", "Used fallback", resolved=True)
        path = save_session()

        content = path.read_text()

        assert "Issues Encountered" in content
        assert "Missing data" in content
        assert "Resolved" in content
