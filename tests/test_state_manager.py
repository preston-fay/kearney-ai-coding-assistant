"""Tests for core/state_manager.py"""

import pytest
import json
from pathlib import Path
import tempfile
import os
import shutil

from core.state_manager import (
    load_state,
    save_state,
    init_project,
    init_from_plan,
    update_task_status,
    get_status_summary,
    get_next_task,
    add_artifact,
    get_completion_percentage,
    warn_if_missing_core_files,
    ProjectState,
    Task,
    STATE_FILE,
    PLAN_FILE,
    SPEC_FILE,
)


@pytest.fixture
def temp_project_dir(monkeypatch):
    """Create a temporary project directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Change to temp directory
        original_dir = os.getcwd()
        os.chdir(tmpdir)

        # Update module-level paths to use temp directory
        import core.state_manager as sm
        sm.STATE_FILE = Path("project_state/status.json")
        sm.PLAN_FILE = Path("project_state/plan.md")
        sm.SPEC_FILE = Path("project_state/spec.yaml")

        yield tmpdir

        # Restore original directory
        os.chdir(original_dir)


class TestTask:
    """Tests for Task dataclass."""

    def test_task_creation(self):
        """Test creating a Task."""
        task = Task(
            id="1.1",
            phase="Phase 1: Setup",
            description="Initialize project",
        )
        assert task.id == "1.1"
        assert task.phase == "Phase 1: Setup"
        assert task.status == "pending"

    def test_task_to_dict(self):
        """Test Task to_dict method."""
        task = Task(
            id="1.1",
            phase="Phase 1",
            description="Test task",
            status="done",
            completed_at="2025-12-01T10:00:00Z",
        )
        d = task.to_dict()
        assert d["id"] == "1.1"
        assert d["status"] == "done"
        assert "started_at" not in d  # None values excluded


class TestProjectState:
    """Tests for ProjectState dataclass."""

    def test_project_state_creation(self):
        """Test creating a ProjectState."""
        state = ProjectState(
            project_name="test-project",
            template="analytics",
            created_at="2025-12-01T10:00:00Z",
            updated_at="2025-12-01T10:00:00Z",
        )
        assert state.project_name == "test-project"
        assert state.template == "analytics"
        assert state.tasks == []

    def test_project_state_to_dict(self):
        """Test ProjectState to_dict method."""
        state = ProjectState(
            project_name="test-project",
            template="analytics",
            created_at="2025-12-01T10:00:00Z",
            updated_at="2025-12-01T10:00:00Z",
            current_phase="Phase 1",
        )
        d = state.to_dict()
        assert d["project_name"] == "test-project"
        assert d["current_phase"] == "Phase 1"
        assert isinstance(d["tasks"], list)


class TestInitProject:
    """Tests for init_project function."""

    def test_init_project_creates_state(self, temp_project_dir):
        """Test that init_project creates status.json."""
        state = init_project("my-project", "analytics")

        assert state.project_name == "my-project"
        assert state.template == "analytics"
        assert Path("project_state/status.json").exists()

    def test_init_project_sets_history(self, temp_project_dir):
        """Test that init_project records init action in history."""
        state = init_project("my-project", "analytics")

        assert len(state.history) == 1
        assert state.history[0]["action"] == "init"


class TestLoadSaveState:
    """Tests for load_state and save_state functions."""

    def test_load_nonexistent_state(self, temp_project_dir):
        """Test loading state when file doesn't exist."""
        state = load_state()
        assert state is None

    def test_save_and_load_state(self, temp_project_dir):
        """Test saving and loading state."""
        original = init_project("test-project", "presentation")
        original.current_phase = "Phase 1"

        # Load and verify
        loaded = load_state()
        assert loaded is not None
        assert loaded.project_name == "test-project"
        assert loaded.template == "presentation"

    def test_load_state_with_tasks(self, temp_project_dir):
        """Test loading state with tasks."""
        state = init_project("test-project", "analytics")
        state.tasks = [
            Task(id="1.1", phase="Phase 1", description="Task 1", status="done"),
            Task(id="1.2", phase="Phase 1", description="Task 2", status="pending"),
        ]
        save_state(state)

        loaded = load_state()
        assert len(loaded.tasks) == 2
        assert loaded.tasks[0].status == "done"


class TestInitFromPlan:
    """Tests for init_from_plan function."""

    def test_init_from_plan_parses_tasks(self, temp_project_dir):
        """Test that init_from_plan parses tasks from plan.md."""
        # Create project state first
        init_project("test-project", "analytics")

        # Create plan.md
        plan_content = """# Project Plan

## Phase 1: Data Preparation
- [ ] Profile the dataset
- [ ] Clean missing values
- [x] Already done task

## Phase 2: Analysis
- [ ] Create revenue chart
- [ ] Generate report
"""
        Path("project_state").mkdir(parents=True, exist_ok=True)
        Path("project_state/plan.md").write_text(plan_content)

        state = init_from_plan("test-project", "analytics")

        assert len(state.tasks) == 5
        # Check task parsing
        assert state.tasks[0].description == "Profile the dataset"
        assert state.tasks[0].status == "pending"
        assert state.tasks[2].status == "done"  # Already done task

    def test_init_from_plan_sets_current_task(self, temp_project_dir):
        """Test that init_from_plan sets current_task to first pending."""
        init_project("test-project", "analytics")

        plan_content = """# Plan
## Phase 1
- [x] Done task
- [ ] Pending task
"""
        Path("project_state").mkdir(parents=True, exist_ok=True)
        Path("project_state/plan.md").write_text(plan_content)

        state = init_from_plan("test-project", "analytics")

        assert state.current_task == "1.2"  # Second task (first pending)


class TestUpdateTaskStatus:
    """Tests for update_task_status function."""

    def test_update_task_to_done(self, temp_project_dir):
        """Test updating task status to done."""
        state = init_project("test-project", "analytics")
        state.tasks = [
            Task(id="1.1", phase="Phase 1", description="Task 1"),
            Task(id="1.2", phase="Phase 1", description="Task 2"),
        ]
        state.current_task = "1.1"
        save_state(state)

        updated = update_task_status("1.1", "done")

        assert updated.tasks[0].status == "done"
        assert updated.tasks[0].completed_at is not None
        assert updated.current_task == "1.2"  # Advanced to next

    def test_update_task_to_in_progress(self, temp_project_dir):
        """Test updating task status to in_progress."""
        state = init_project("test-project", "analytics")
        state.tasks = [Task(id="1.1", phase="Phase 1", description="Task 1")]
        save_state(state)

        updated = update_task_status("1.1", "in_progress")

        assert updated.tasks[0].status == "in_progress"
        assert updated.tasks[0].started_at is not None

    def test_update_nonexistent_task_raises(self, temp_project_dir):
        """Test that updating nonexistent task raises ValueError."""
        init_project("test-project", "analytics")

        with pytest.raises(ValueError, match="Task 99.99 not found"):
            update_task_status("99.99", "done")

    def test_update_without_state_raises(self, temp_project_dir):
        """Test that updating without state raises ValueError."""
        with pytest.raises(ValueError, match="No project state found"):
            update_task_status("1.1", "done")


class TestGetStatusSummary:
    """Tests for get_status_summary function."""

    def test_summary_no_project(self, temp_project_dir):
        """Test summary when no project exists."""
        summary = get_status_summary()
        assert "No project initialized" in summary

    def test_summary_with_project(self, temp_project_dir):
        """Test summary with active project."""
        state = init_project("test-project", "analytics")
        state.tasks = [
            Task(id="1.1", phase="Phase 1", description="Task 1", status="done"),
            Task(id="1.2", phase="Phase 1", description="Task 2", status="pending"),
        ]
        state.current_phase = "Phase 1"
        state.current_task = "1.2"
        save_state(state)

        summary = get_status_summary()

        assert "test-project" in summary
        assert "analytics" in summary
        assert "1 / 2" in summary  # 1 done of 2 total


class TestGetNextTask:
    """Tests for get_next_task function."""

    def test_get_next_task_returns_pending(self, temp_project_dir):
        """Test getting next pending task."""
        state = init_project("test-project", "analytics")
        state.tasks = [
            Task(id="1.1", phase="Phase 1", description="Task 1", status="done"),
            Task(id="1.2", phase="Phase 1", description="Task 2", status="pending"),
        ]
        state.current_task = "1.2"
        save_state(state)

        next_task = get_next_task()

        assert next_task is not None
        assert next_task.id == "1.2"

    def test_get_next_task_returns_in_progress_first(self, temp_project_dir):
        """Test that in_progress tasks are returned first."""
        state = init_project("test-project", "analytics")
        state.tasks = [
            Task(id="1.1", phase="Phase 1", description="Task 1", status="in_progress"),
            Task(id="1.2", phase="Phase 1", description="Task 2", status="pending"),
        ]
        save_state(state)

        next_task = get_next_task()

        assert next_task.id == "1.1"

    def test_get_next_task_none_when_complete(self, temp_project_dir):
        """Test that None is returned when all tasks complete."""
        state = init_project("test-project", "analytics")
        state.tasks = [
            Task(id="1.1", phase="Phase 1", description="Task 1", status="done"),
        ]
        state.current_task = None
        save_state(state)

        next_task = get_next_task()

        assert next_task is None


class TestAddArtifact:
    """Tests for add_artifact function."""

    def test_add_artifact(self, temp_project_dir):
        """Test adding an artifact."""
        init_project("test-project", "analytics")

        state = add_artifact("outputs/charts/revenue.png")

        assert "outputs/charts/revenue.png" in state.artifacts
        assert any(h["action"] == "artifact_created" for h in state.history)

    def test_add_duplicate_artifact_ignored(self, temp_project_dir):
        """Test that duplicate artifacts are not added."""
        init_project("test-project", "analytics")

        add_artifact("outputs/charts/revenue.png")
        state = add_artifact("outputs/charts/revenue.png")

        assert state.artifacts.count("outputs/charts/revenue.png") == 1


class TestCompletionPercentage:
    """Tests for get_completion_percentage function."""

    def test_completion_no_tasks(self, temp_project_dir):
        """Test completion with no tasks."""
        init_project("test-project", "analytics")
        assert get_completion_percentage() == 0.0

    def test_completion_half_done(self, temp_project_dir):
        """Test completion at 50%."""
        state = init_project("test-project", "analytics")
        state.tasks = [
            Task(id="1.1", phase="Phase 1", description="Task 1", status="done"),
            Task(id="1.2", phase="Phase 1", description="Task 2", status="pending"),
        ]
        save_state(state)

        assert get_completion_percentage() == 50.0

    def test_completion_all_done(self, temp_project_dir):
        """Test completion at 100%."""
        state = init_project("test-project", "analytics")
        state.tasks = [
            Task(id="1.1", phase="Phase 1", description="Task 1", status="done"),
            Task(id="1.2", phase="Phase 1", description="Task 2", status="done"),
        ]
        save_state(state)

        assert get_completion_percentage() == 100.0


class TestWarnIfMissingCoreFiles:
    """Tests for warn_if_missing_core_files function."""

    def test_warns_when_spec_missing(self, temp_project_dir):
        """Test warning when spec.yaml is missing."""
        warnings = warn_if_missing_core_files()
        assert any("spec.yaml" in w for w in warnings)

    def test_warns_when_plan_missing(self, temp_project_dir):
        """Test warning when plan.md is missing."""
        warnings = warn_if_missing_core_files()
        assert any("plan.md" in w for w in warnings)

    def test_no_warnings_when_files_exist(self, temp_project_dir):
        """Test no warnings when all files exist."""
        Path("project_state").mkdir(parents=True, exist_ok=True)
        Path("project_state/spec.yaml").write_text("# spec")
        Path("project_state/plan.md").write_text("# plan")

        warnings = warn_if_missing_core_files()
        assert len(warnings) == 0
