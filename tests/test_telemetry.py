"""Tests for telemetry module."""

import pytest
from datetime import datetime, timedelta

from core.telemetry import (
    Telemetry, Event, EventType, Metrics, TelemetryTimer
)


class TestEvent:
    """Tests for Event dataclass."""

    def test_to_dict(self):
        """Should convert to dict with string event type."""
        event = Event(
            event_type=EventType.COMMAND_START,
            timestamp="2025-01-01T10:00:00",
            data={'command': '/interview'}
        )

        d = event.to_dict()

        assert d['event_type'] == 'command_start'
        assert d['timestamp'] == "2025-01-01T10:00:00"
        assert d['data']['command'] == '/interview'

    def test_from_dict(self):
        """Should create from dict."""
        d = {
            'event_type': 'command_start',
            'timestamp': '2025-01-01T10:00:00',
            'project_name': 'Test',
            'project_type': 'analytics',
            'data': {'command': '/plan'},
            'duration_ms': None,
            'success': True,
            'error_message': None,
        }

        event = Event.from_dict(d)

        assert event.event_type == EventType.COMMAND_START
        assert event.project_name == 'Test'
        assert event.data['command'] == '/plan'

    def test_roundtrip(self):
        """Should survive roundtrip to/from dict."""
        original = Event(
            event_type=EventType.TASK_COMPLETE,
            timestamp="2025-01-01T12:00:00",
            project_name="Test Project",
            data={'task_id': '1.1'},
            duration_ms=1500,
            success=True,
        )

        roundtrip = Event.from_dict(original.to_dict())

        assert roundtrip.event_type == original.event_type
        assert roundtrip.timestamp == original.timestamp
        assert roundtrip.duration_ms == original.duration_ms


class TestTelemetry:
    """Tests for Telemetry class."""

    @pytest.fixture
    def temp_events_dir(self, tmp_path):
        """Set up temporary events directory."""
        # Override paths for testing
        project_path = tmp_path / "project_state" / "events.jsonl"
        global_path = tmp_path / ".kaca" / "global_events.jsonl"

        original_project = Telemetry.PROJECT_EVENTS_FILE
        original_global = Telemetry.GLOBAL_EVENTS_FILE

        Telemetry.PROJECT_EVENTS_FILE = str(project_path)
        Telemetry.GLOBAL_EVENTS_FILE = str(global_path)

        yield tmp_path

        # Restore original paths
        Telemetry.PROJECT_EVENTS_FILE = original_project
        Telemetry.GLOBAL_EVENTS_FILE = original_global

    def test_log_creates_event(self, temp_events_dir):
        """Should create event and write to file."""
        event = Telemetry.log(
            EventType.COMMAND_START,
            data={'command': '/interview'}
        )

        assert event.event_type == EventType.COMMAND_START
        assert event.data['command'] == '/interview'

        # Verify written to file
        events = Telemetry.load_events()
        assert len(events) == 1
        assert events[0].data['command'] == '/interview'

    def test_log_command(self, temp_events_dir):
        """Should log command events."""
        Telemetry.log_command('/execute', start=True)
        Telemetry.log_command('/execute', start=False, duration_ms=500)

        events = Telemetry.load_events()
        assert len(events) == 2
        assert events[0].event_type == EventType.COMMAND_START
        assert events[1].event_type == EventType.COMMAND_END

    def test_log_artifact(self, temp_events_dir):
        """Should log artifact creation."""
        Telemetry.log_artifact(
            'outputs/chart.png',
            artifact_type='png',
            size_bytes=12345
        )

        events = Telemetry.load_events()
        assert len(events) == 1
        assert events[0].event_type == EventType.ARTIFACT_CREATED
        assert events[0].data['type'] == 'png'

    def test_log_brand_check(self, temp_events_dir):
        """Should log brand check results."""
        Telemetry.log_brand_check(passed=True)
        Telemetry.log_brand_check(passed=False, violations=['FORBIDDEN_COLOR'])

        events = Telemetry.load_events()
        assert len(events) == 2
        assert events[0].event_type == EventType.BRAND_CHECK_PASS
        assert events[1].event_type == EventType.BRAND_CHECK_FAIL
        assert 'FORBIDDEN_COLOR' in events[1].data['violations']

    def test_session_lifecycle(self, temp_events_dir):
        """Should track session start and end."""
        session_id = Telemetry.start_session(project_name='Test')
        assert session_id is not None

        Telemetry.end_session()

        events = Telemetry.load_events()
        assert len(events) == 2
        assert events[0].event_type == EventType.SESSION_START
        assert events[1].event_type == EventType.SESSION_END

    def test_load_events_with_since_filter(self, temp_events_dir):
        """Should filter events by timestamp."""
        # Log events at different times
        Telemetry.log(EventType.COMMAND_START, data={'cmd': '1'})

        events = Telemetry.load_events()
        assert len(events) == 1

        # Filter to future (should return nothing)
        future = datetime.now() + timedelta(hours=1)
        filtered = Telemetry.load_events(since=future)
        assert len(filtered) == 0


class TestMetricsComputation:
    """Tests for metrics computation."""

    def test_compute_metrics_empty(self):
        """Should handle empty events list."""
        metrics = Telemetry.compute_metrics([])

        assert metrics.total_sessions == 0
        assert metrics.total_commands == 0

    def test_compute_metrics_counts(self):
        """Should count events correctly."""
        events = [
            Event(EventType.SESSION_START, "2025-01-01T10:00:00"),
            Event(EventType.COMMAND_START, "2025-01-01T10:01:00", data={'command': '/interview'}),
            Event(EventType.COMMAND_START, "2025-01-01T10:02:00", data={'command': '/plan'}),
            Event(EventType.COMMAND_START, "2025-01-01T10:03:00", data={'command': '/interview'}),
            Event(EventType.ARTIFACT_CREATED, "2025-01-01T10:04:00", data={'type': 'png'}),
            Event(EventType.ARTIFACT_CREATED, "2025-01-01T10:05:00", data={'type': 'png'}),
            Event(EventType.ARTIFACT_CREATED, "2025-01-01T10:06:00", data={'type': 'pptx'}),
        ]

        metrics = Telemetry.compute_metrics(events)

        assert metrics.total_sessions == 1
        assert metrics.total_commands == 3
        assert metrics.total_artifacts == 3
        assert metrics.commands_by_type['/interview'] == 2
        assert metrics.commands_by_type['/plan'] == 1
        assert metrics.artifacts_by_type['png'] == 2
        assert metrics.artifacts_by_type['pptx'] == 1

    def test_compute_brand_compliance_rate(self):
        """Should compute brand compliance rate."""
        events = [
            Event(EventType.BRAND_CHECK_PASS, "2025-01-01T10:00:00"),
            Event(EventType.BRAND_CHECK_PASS, "2025-01-01T10:01:00"),
            Event(EventType.BRAND_CHECK_PASS, "2025-01-01T10:02:00"),
            Event(EventType.BRAND_CHECK_FAIL, "2025-01-01T10:03:00"),
        ]

        metrics = Telemetry.compute_metrics(events)

        assert metrics.brand_compliance_rate == 0.75  # 3/4

    def test_compute_task_success_rate(self):
        """Should compute task success rate."""
        events = [
            Event(EventType.TASK_COMPLETE, "2025-01-01T10:00:00", success=True),
            Event(EventType.TASK_COMPLETE, "2025-01-01T10:01:00", success=True),
            Event(EventType.TASK_ERROR, "2025-01-01T10:02:00", success=False),
        ]

        metrics = Telemetry.compute_metrics(events)

        assert metrics.task_success_rate == pytest.approx(0.666, rel=0.01)

    def test_compute_insight_metrics(self):
        """Should count insight events."""
        events = [
            Event(EventType.INSIGHT_EXTRACTED, "2025-01-01T10:00:00"),
            Event(EventType.INSIGHT_EXTRACTED, "2025-01-01T10:01:00"),
            Event(EventType.PRESENTATION_BUILT, "2025-01-01T10:02:00"),
        ]

        metrics = Telemetry.compute_metrics(events)

        assert metrics.insights_extracted == 2
        assert metrics.presentations_built == 1


class TestTelemetryTimer:
    """Tests for TelemetryTimer context manager."""

    def test_timer_logs_duration(self, tmp_path):
        """Should log event with duration."""
        # Override paths
        Telemetry.PROJECT_EVENTS_FILE = str(tmp_path / "events.jsonl")
        Telemetry.GLOBAL_EVENTS_FILE = str(tmp_path / "global.jsonl")

        with TelemetryTimer(EventType.TASK_COMPLETE, {'task_id': '1.1'}):
            # Simulate some work
            pass

        events = Telemetry.load_events()
        assert len(events) == 1
        assert events[0].duration_ms is not None
        assert events[0].duration_ms >= 0

    def test_timer_captures_error(self, tmp_path):
        """Should capture error on exception."""
        Telemetry.PROJECT_EVENTS_FILE = str(tmp_path / "events.jsonl")
        Telemetry.GLOBAL_EVENTS_FILE = str(tmp_path / "global.jsonl")

        try:
            with TelemetryTimer(EventType.TASK_COMPLETE, {'task_id': '1.1'}):
                raise ValueError("Test error")
        except ValueError:
            pass

        events = Telemetry.load_events()
        assert len(events) == 1
        assert events[0].success is False
        assert "Test error" in events[0].error_message


class TestSummaryReport:
    """Tests for summary report generation."""

    def test_generates_report(self):
        """Should generate formatted report."""
        events = [
            Event(EventType.SESSION_START, "2025-01-01T10:00:00"),
            Event(EventType.COMMAND_START, "2025-01-01T10:01:00", data={'command': '/interview'}),
            Event(EventType.BRAND_CHECK_PASS, "2025-01-01T10:02:00"),
        ]

        report = Telemetry.get_summary_report(events)

        assert "KACA TELEMETRY REPORT" in report
        assert "Total sessions: 1" in report
        assert "Total commands: 1" in report

    def test_report_includes_quality_metrics(self):
        """Should include quality metrics in report."""
        events = [
            Event(EventType.BRAND_CHECK_PASS, "2025-01-01T10:00:00"),
            Event(EventType.BRAND_CHECK_PASS, "2025-01-01T10:01:00"),
            Event(EventType.SPEC_EDITED, "2025-01-01T10:02:00"),
        ]

        report = Telemetry.get_summary_report(events)

        assert "QUALITY METRICS" in report
        assert "Brand compliance rate: 100.0%" in report
        assert "Spec edit count: 1" in report

    def test_report_includes_content_intelligence(self):
        """Should include content intelligence section."""
        events = [
            Event(EventType.INSIGHT_EXTRACTED, "2025-01-01T10:00:00"),
            Event(EventType.PRESENTATION_BUILT, "2025-01-01T10:01:00"),
        ]

        report = Telemetry.get_summary_report(events)

        assert "CONTENT INTELLIGENCE" in report
        assert "Insights extracted: 1" in report
        assert "Presentations built: 1" in report


class TestMetricsDataclass:
    """Tests for Metrics dataclass."""

    def test_to_dict(self):
        """Should convert to dict."""
        metrics = Metrics(
            total_sessions=5,
            total_commands=10,
            brand_compliance_rate=0.95,
            commands_by_type={'/interview': 3, '/plan': 2},
        )

        d = metrics.to_dict()

        assert d['total_sessions'] == 5
        assert d['total_commands'] == 10
        assert d['brand_compliance_rate'] == 0.95
        assert d['commands_by_type'] == {'/interview': 3, '/plan': 2}

    def test_default_values(self):
        """Should have sensible defaults."""
        metrics = Metrics()

        assert metrics.total_sessions == 0
        assert metrics.total_commands == 0
        assert metrics.brand_compliance_rate is None
        assert metrics.commands_by_type == {}
