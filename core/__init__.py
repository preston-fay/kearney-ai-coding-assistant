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
"""

__version__ = "2.0.0"
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
]
