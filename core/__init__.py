"""
Kearney AI Coding Assistant - Core Engine

This package contains the core automation and validation modules
that power the Headless IDE for Kearney consultants.

Modules:
    brand_guard: Programmatic brand enforcement
    chart_engine: KDS-compliant charting
    slide_engine: PPTX generation with Kearney templates
    spreadsheet_engine: Excel/XLSX generation with brand compliance
    document_engine: Word/DOCX generation with brand compliance
    data_profiler: Dataset analysis and profiling
    state_manager: Project state management for resumption
    hook_runner: Cross-platform hook dispatcher
    interview_engine: Interview orchestration for requirements gathering
    spec_manager: Specification CRUD with versioning
    design_system: Multi-brand theming with WCAG accessibility
"""

__version__ = "3.0.0"
__author__ = "Kearney Digital & Analytics"

from core.brand_guard import check_file, check_directory, BrandViolation
from core.chart_engine import KDSChart
from core.slide_engine import KDSPresentation
from core.spreadsheet_engine import KDSSpreadsheet
from core.document_engine import KDSDocument
from core.data_profiler import profile_dataset
from core.state_manager import (
    load_state,
    save_state,
    init_project,
    init_from_plan,
    update_task_status,
    get_status_summary,
    ProjectState,
    Task,
)
from core.spec_manager import (
    Specification,
    create_spec,
    load_spec,
    save_spec,
    get_version,
    spec_exists,
    get_spec_summary,
)
from core.interview_engine import (
    InterviewTree,
    InterviewState,
    load_interview_tree,
    get_project_type_menu,
    parse_project_type_choice,
    parse_multi_select,
    create_interview_state,
    get_next_question,
    answers_to_spec_dict,
)

# Web Application Support (v2.1)
from core.kds_theme import KDSTheme
from core.kds_data import KDSData, KDSDataSourceConfig
from core.webapp_engine import KDSWebApp, KDSStreamlitApp, KDSReactApp

# Utilities (v2.2)
from core.kds_utils import safe_write_text, safe_read_text
from core.streamlit_utils import (
    launch_streamlit,
    generate_requirements,
    verify_imports,
    is_port_in_use,
    find_available_port,
    STREAMLIT_CORE_DEPS,
    STREAMLIT_ALL_DEPS,
)

# Workspace Protection (v2.2)
from core.workspace_guard import (
    is_template_repo,
    verify_workspace,
    get_workspace_info,
    require_project_workspace,
)

# Design System Module (v3.0)
from core.design_system import (
    DesignSystem,
    load_design_system,
    save_design_system,
    list_design_systems,
    resolve_theme,
    apply_design_system,
    contrast_ratio,
    ensure_contrast,
)

# Memory System (v3.1)
from core.memory import (
    load_user_profile,
    save_user_profile,
    get_user_preference,
    update_user_preference,
    add_episode,
    get_recent_episodes,
    build_memory_context,
    update_session_context,
    get_session_context,
)

# Memory Integration (v3.1)
from core.memory_integration import (
    get_agent_context,
    update_session_after_task,
    apply_user_defaults_to_spec,
    get_client_overrides,
)

# Insight Engine (v3.2)
from core.insight_engine import (
    Insight,
    Evidence,
    InsightCatalog,
    InsightEngine,
)

# Action Titles (v3.2)
from core.action_titles import (
    is_weak_title,
    transform_to_action_title,
    suggest_action_titles,
    validate_action_title,
)

# Spec Diff Engine (v3.2)
from core.spec_diff import (
    compute_diff,
    assess_plan_impact,
    SpecChange,
    ChangeType,
    ImpactLevel,
    DiffResult,
)

# Plan Updater (v3.2)
from core.plan_updater import (
    PlanUpdater,
    PlanUpdateResult,
    TaskUpdate,
    update_plan_from_diff,
)

# Telemetry (v3.3)
from core.telemetry import (
    Telemetry,
    Event,
    EventType,
    Metrics,
    TelemetryTimer,
)

__all__ = [
    # Brand Guard
    "check_file",
    "check_directory",
    "BrandViolation",
    # Chart Engine
    "KDSChart",
    # Slide Engine
    "KDSPresentation",
    # Spreadsheet Engine
    "KDSSpreadsheet",
    # Document Engine
    "KDSDocument",
    # Data Profiler
    "profile_dataset",
    # State Manager
    "load_state",
    "save_state",
    "init_project",
    "init_from_plan",
    "update_task_status",
    "get_status_summary",
    "ProjectState",
    "Task",
    # Spec Manager
    "Specification",
    "create_spec",
    "load_spec",
    "save_spec",
    "get_version",
    "spec_exists",
    "get_spec_summary",
    # Interview Engine
    "InterviewTree",
    "InterviewState",
    "load_interview_tree",
    "get_project_type_menu",
    "parse_project_type_choice",
    "parse_multi_select",
    "create_interview_state",
    "get_next_question",
    "answers_to_spec_dict",
    # Web Application Support (v2.1)
    "KDSTheme",
    "KDSData",
    "KDSDataSourceConfig",
    "KDSWebApp",
    "KDSStreamlitApp",
    "KDSReactApp",
    # Utilities (v2.2)
    "safe_write_text",
    "safe_read_text",
    "launch_streamlit",
    "generate_requirements",
    "verify_imports",
    "is_port_in_use",
    "find_available_port",
    "STREAMLIT_CORE_DEPS",
    "STREAMLIT_ALL_DEPS",
    # Workspace Protection (v2.2)
    "is_template_repo",
    "verify_workspace",
    "get_workspace_info",
    "require_project_workspace",
    # Design System Module (v3.0)
    "DesignSystem",
    "load_design_system",
    "save_design_system",
    "list_design_systems",
    "resolve_theme",
    "apply_design_system",
    "contrast_ratio",
    "ensure_contrast",
    # Memory System (v3.1)
    "load_user_profile",
    "save_user_profile",
    "get_user_preference",
    "update_user_preference",
    "add_episode",
    "get_recent_episodes",
    "build_memory_context",
    "update_session_context",
    "get_session_context",
    # Memory Integration (v3.1)
    "get_agent_context",
    "update_session_after_task",
    "apply_user_defaults_to_spec",
    "get_client_overrides",
    # Insight Engine (v3.2)
    "Insight",
    "Evidence",
    "InsightCatalog",
    "InsightEngine",
    # Action Titles (v3.2)
    "is_weak_title",
    "transform_to_action_title",
    "suggest_action_titles",
    "validate_action_title",
    # Spec Diff Engine (v3.2)
    "compute_diff",
    "assess_plan_impact",
    "SpecChange",
    "ChangeType",
    "ImpactLevel",
    "DiffResult",
    # Plan Updater (v3.2)
    "PlanUpdater",
    "PlanUpdateResult",
    "TaskUpdate",
    "update_plan_from_diff",
    # Telemetry (v3.3)
    "Telemetry",
    "Event",
    "EventType",
    "Metrics",
    "TelemetryTimer",
]
