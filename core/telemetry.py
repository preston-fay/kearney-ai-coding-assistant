"""
Telemetry module for KACA.

Provides structured event logging and metrics computation for tracking
usage patterns, performance, and quality across projects.

Usage:
    from core.telemetry import Telemetry, Event, EventType

    # Log an event
    Telemetry.log(EventType.COMMAND_START, {'command': '/interview'})

    # Compute metrics
    metrics = Telemetry.compute_metrics()
"""

import json
import logging
import os
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class EventType(Enum):
    """Types of events that can be logged."""
    # Session events
    SESSION_START = "session_start"
    SESSION_END = "session_end"

    # Command events
    COMMAND_START = "command_start"
    COMMAND_END = "command_end"
    COMMAND_ERROR = "command_error"

    # Workflow events
    INTERVIEW_START = "interview_start"
    INTERVIEW_COMPLETE = "interview_complete"
    PLAN_GENERATED = "plan_generated"
    PLAN_UPDATED = "plan_updated"
    TASK_START = "task_start"
    TASK_COMPLETE = "task_complete"
    TASK_ERROR = "task_error"

    # Output events
    ARTIFACT_CREATED = "artifact_created"
    EXPORT_CREATED = "export_created"

    # Quality events
    BRAND_CHECK_PASS = "brand_check_pass"
    BRAND_CHECK_FAIL = "brand_check_fail"
    SPEC_EDITED = "spec_edited"

    # Insight events
    INSIGHT_EXTRACTED = "insight_extracted"
    PRESENTATION_BUILT = "presentation_built"


@dataclass
class Event:
    """A single telemetry event."""
    event_type: EventType
    timestamp: str
    project_name: Optional[str] = None
    project_type: Optional[str] = None
    data: Dict[str, Any] = field(default_factory=dict)
    duration_ms: Optional[int] = None
    success: bool = True
    error_message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        d = asdict(self)
        d['event_type'] = self.event_type.value
        return d

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> 'Event':
        """Create from dictionary."""
        d = d.copy()
        d['event_type'] = EventType(d['event_type'])
        return cls(**d)


@dataclass
class Metrics:
    """Computed metrics from telemetry data."""
    # Time metrics
    avg_time_to_first_output_seconds: Optional[float] = None
    avg_session_duration_seconds: Optional[float] = None
    avg_task_duration_seconds: Optional[float] = None

    # Volume metrics
    total_sessions: int = 0
    total_commands: int = 0
    total_artifacts: int = 0
    total_exports: int = 0

    # Quality metrics
    brand_compliance_rate: Optional[float] = None
    task_success_rate: Optional[float] = None
    spec_edit_count: int = 0

    # Usage patterns
    commands_by_type: Dict[str, int] = field(default_factory=dict)
    project_types: Dict[str, int] = field(default_factory=dict)
    artifacts_by_type: Dict[str, int] = field(default_factory=dict)

    # Insight metrics
    insights_extracted: int = 0
    presentations_built: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class Telemetry:
    """
    Telemetry system for KACA.

    Events are stored in JSONL format at project_state/events.jsonl
    and optionally at ~/.kaca/global_events.jsonl for cross-project metrics.
    """

    # Default paths
    PROJECT_EVENTS_FILE = "project_state/events.jsonl"
    GLOBAL_EVENTS_FILE = "~/.kaca/global_events.jsonl"

    _current_session_id: Optional[str] = None
    _session_start_time: Optional[datetime] = None

    @classmethod
    def _get_project_path(cls) -> Path:
        """Get project events file path."""
        return Path(cls.PROJECT_EVENTS_FILE)

    @classmethod
    def _get_global_path(cls) -> Path:
        """Get global events file path."""
        return Path(os.path.expanduser(cls.GLOBAL_EVENTS_FILE))

    @classmethod
    def _ensure_dirs(cls, path: Path) -> None:
        """Ensure parent directories exist."""
        path.parent.mkdir(parents=True, exist_ok=True)

    @classmethod
    def start_session(cls, project_name: Optional[str] = None) -> str:
        """Start a new telemetry session."""
        cls._current_session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        cls._session_start_time = datetime.now()

        cls.log(EventType.SESSION_START, {
            'session_id': cls._current_session_id,
            'project_name': project_name,
        })

        return cls._current_session_id

    @classmethod
    def end_session(cls) -> None:
        """End the current session."""
        duration_ms = None
        if cls._session_start_time:
            duration_ms = int((datetime.now() - cls._session_start_time).total_seconds() * 1000)

        cls.log(EventType.SESSION_END, {
            'session_id': cls._current_session_id,
        }, duration_ms=duration_ms)

        cls._current_session_id = None
        cls._session_start_time = None

    @classmethod
    def log(
        cls,
        event_type: EventType,
        data: Optional[Dict[str, Any]] = None,
        duration_ms: Optional[int] = None,
        success: bool = True,
        error_message: Optional[str] = None,
        project_name: Optional[str] = None,
        project_type: Optional[str] = None,
    ) -> Event:
        """
        Log a telemetry event.

        Args:
            event_type: Type of event
            data: Additional event data
            duration_ms: Duration in milliseconds (if applicable)
            success: Whether the event represents success
            error_message: Error message if success=False
            project_name: Override project name
            project_type: Override project type

        Returns:
            The created Event
        """
        event = Event(
            event_type=event_type,
            timestamp=datetime.now().isoformat(),
            project_name=project_name,
            project_type=project_type,
            data=data or {},
            duration_ms=duration_ms,
            success=success,
            error_message=error_message,
        )

        # Write to project events file
        try:
            project_path = cls._get_project_path()
            cls._ensure_dirs(project_path)
            with open(project_path, 'a') as f:
                f.write(json.dumps(event.to_dict()) + '\n')
        except Exception as e:
            logger.warning(f"Failed to write project event: {e}")

        # Write to global events file
        try:
            global_path = cls._get_global_path()
            cls._ensure_dirs(global_path)
            with open(global_path, 'a') as f:
                f.write(json.dumps(event.to_dict()) + '\n')
        except Exception as e:
            logger.warning(f"Failed to write global event: {e}")

        return event

    @classmethod
    def log_command(
        cls,
        command: str,
        start: bool = True,
        duration_ms: Optional[int] = None,
        success: bool = True,
        error_message: Optional[str] = None,
    ) -> Event:
        """Convenience method for logging command events."""
        event_type = EventType.COMMAND_START if start else EventType.COMMAND_END
        if not success:
            event_type = EventType.COMMAND_ERROR

        return cls.log(
            event_type,
            data={'command': command},
            duration_ms=duration_ms,
            success=success,
            error_message=error_message,
        )

    @classmethod
    def log_artifact(
        cls,
        artifact_path: str,
        artifact_type: str,
        size_bytes: Optional[int] = None,
    ) -> Event:
        """Convenience method for logging artifact creation."""
        return cls.log(
            EventType.ARTIFACT_CREATED,
            data={
                'path': artifact_path,
                'type': artifact_type,
                'size_bytes': size_bytes,
            }
        )

    @classmethod
    def log_brand_check(cls, passed: bool, violations: Optional[List[str]] = None) -> Event:
        """Convenience method for logging brand check results."""
        event_type = EventType.BRAND_CHECK_PASS if passed else EventType.BRAND_CHECK_FAIL
        return cls.log(
            event_type,
            data={'violations': violations or []},
            success=passed,
        )

    @classmethod
    def load_events(cls, path: Optional[Path] = None, since: Optional[datetime] = None) -> List[Event]:
        """
        Load events from file.

        Args:
            path: Path to events file (defaults to project events)
            since: Only load events after this timestamp

        Returns:
            List of Event objects
        """
        if path is None:
            path = cls._get_project_path()

        events = []
        if not path.exists():
            return events

        with open(path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    d = json.loads(line)
                    event = Event.from_dict(d)

                    if since:
                        event_time = datetime.fromisoformat(event.timestamp)
                        if event_time < since:
                            continue

                    events.append(event)
                except Exception as e:
                    logger.warning(f"Failed to parse event: {e}")

        return events

    @classmethod
    def compute_metrics(cls, events: Optional[List[Event]] = None) -> Metrics:
        """
        Compute metrics from events.

        Args:
            events: List of events (loads from project file if not provided)

        Returns:
            Metrics object
        """
        if events is None:
            events = cls.load_events()

        if not events:
            return Metrics()

        metrics = Metrics()

        # Track for calculations
        session_durations = []
        task_durations = []
        brand_checks = {'pass': 0, 'fail': 0}
        task_results = {'success': 0, 'fail': 0}

        for event in events:
            # Session metrics
            if event.event_type == EventType.SESSION_START:
                metrics.total_sessions += 1

            elif event.event_type == EventType.SESSION_END:
                if event.duration_ms:
                    session_durations.append(event.duration_ms / 1000)

            # Command metrics
            elif event.event_type == EventType.COMMAND_START:
                metrics.total_commands += 1
                cmd = event.data.get('command', 'unknown')
                metrics.commands_by_type[cmd] = metrics.commands_by_type.get(cmd, 0) + 1

            # Task metrics
            elif event.event_type == EventType.TASK_COMPLETE:
                if event.duration_ms:
                    task_durations.append(event.duration_ms / 1000)
                if event.success:
                    task_results['success'] += 1
                else:
                    task_results['fail'] += 1

            elif event.event_type == EventType.TASK_ERROR:
                task_results['fail'] += 1

            # Artifact metrics
            elif event.event_type == EventType.ARTIFACT_CREATED:
                metrics.total_artifacts += 1
                artifact_type = event.data.get('type', 'unknown')
                metrics.artifacts_by_type[artifact_type] = metrics.artifacts_by_type.get(artifact_type, 0) + 1

            elif event.event_type == EventType.EXPORT_CREATED:
                metrics.total_exports += 1

            # Brand check metrics
            elif event.event_type == EventType.BRAND_CHECK_PASS:
                brand_checks['pass'] += 1

            elif event.event_type == EventType.BRAND_CHECK_FAIL:
                brand_checks['fail'] += 1

            # Spec metrics
            elif event.event_type == EventType.SPEC_EDITED:
                metrics.spec_edit_count += 1

            # Insight metrics
            elif event.event_type == EventType.INSIGHT_EXTRACTED:
                metrics.insights_extracted += 1

            elif event.event_type == EventType.PRESENTATION_BUILT:
                metrics.presentations_built += 1

            # Project type tracking
            if event.project_type:
                metrics.project_types[event.project_type] = metrics.project_types.get(event.project_type, 0) + 1

        # Compute averages
        if session_durations:
            metrics.avg_session_duration_seconds = sum(session_durations) / len(session_durations)

        if task_durations:
            metrics.avg_task_duration_seconds = sum(task_durations) / len(task_durations)

        # Compute rates
        total_brand_checks = brand_checks['pass'] + brand_checks['fail']
        if total_brand_checks > 0:
            metrics.brand_compliance_rate = brand_checks['pass'] / total_brand_checks

        total_tasks = task_results['success'] + task_results['fail']
        if total_tasks > 0:
            metrics.task_success_rate = task_results['success'] / total_tasks

        return metrics

    @classmethod
    def get_summary_report(cls, events: Optional[List[Event]] = None) -> str:
        """
        Generate a human-readable summary report.

        Args:
            events: List of events (loads from project file if not provided)

        Returns:
            Formatted report string
        """
        metrics = cls.compute_metrics(events)

        lines = [
            "=" * 50,
            "KACA TELEMETRY REPORT",
            "=" * 50,
            "",
            "USAGE METRICS",
            "-" * 30,
            f"Total sessions: {metrics.total_sessions}",
            f"Total commands: {metrics.total_commands}",
            f"Total artifacts: {metrics.total_artifacts}",
            f"Total exports: {metrics.total_exports}",
            "",
        ]

        if metrics.avg_session_duration_seconds:
            lines.append(f"Avg session duration: {metrics.avg_session_duration_seconds:.1f}s")

        if metrics.avg_task_duration_seconds:
            lines.append(f"Avg task duration: {metrics.avg_task_duration_seconds:.1f}s")

        lines.extend([
            "",
            "QUALITY METRICS",
            "-" * 30,
        ])

        if metrics.brand_compliance_rate is not None:
            lines.append(f"Brand compliance rate: {metrics.brand_compliance_rate:.1%}")

        if metrics.task_success_rate is not None:
            lines.append(f"Task success rate: {metrics.task_success_rate:.1%}")

        lines.append(f"Spec edit count: {metrics.spec_edit_count}")

        if metrics.commands_by_type:
            lines.extend([
                "",
                "COMMANDS BY TYPE",
                "-" * 30,
            ])
            for cmd, count in sorted(metrics.commands_by_type.items(), key=lambda x: -x[1]):
                lines.append(f"  {cmd}: {count}")

        if metrics.artifacts_by_type:
            lines.extend([
                "",
                "ARTIFACTS BY TYPE",
                "-" * 30,
            ])
            for atype, count in sorted(metrics.artifacts_by_type.items(), key=lambda x: -x[1]):
                lines.append(f"  {atype}: {count}")

        if metrics.insights_extracted or metrics.presentations_built:
            lines.extend([
                "",
                "CONTENT INTELLIGENCE",
                "-" * 30,
                f"Insights extracted: {metrics.insights_extracted}",
                f"Presentations built: {metrics.presentations_built}",
            ])

        lines.extend(["", "=" * 50])

        return "\n".join(lines)

    @classmethod
    def clear_project_events(cls) -> None:
        """Clear project events file."""
        path = cls._get_project_path()
        if path.exists():
            path.unlink()


# Context manager for timing operations
class TelemetryTimer:
    """Context manager for timing operations and logging events."""

    def __init__(
        self,
        event_type: EventType,
        data: Optional[Dict[str, Any]] = None,
        log_start: bool = False,
    ):
        self.event_type = event_type
        self.data = data or {}
        self.log_start = log_start
        self.start_time: Optional[datetime] = None

    def __enter__(self) -> 'TelemetryTimer':
        self.start_time = datetime.now()
        if self.log_start:
            # Log start event (e.g., COMMAND_START)
            start_type = EventType(self.event_type.value.replace('_complete', '_start').replace('_end', '_start'))
            Telemetry.log(start_type, self.data)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        duration_ms = int((datetime.now() - self.start_time).total_seconds() * 1000)
        success = exc_type is None
        error_message = str(exc_val) if exc_val else None

        Telemetry.log(
            self.event_type,
            self.data,
            duration_ms=duration_ms,
            success=success,
            error_message=error_message,
        )
