# Kearney AI Coding Assistant

## Master Plan v2.0

**The Headless IDE for AI-Assisted Consulting with Programmatic Brand Enforcement**

*Clone. Setup. Build. Brand-Compliant from Line One.*

*Windows-Ready. Python-First. State-Persistent.*

---

# Changelog: v1.0 to v2.0

This version incorporates critical feedback from multi-model architectural review. The changes address four vulnerabilities that would have caused deployment failures.

## Critical Fixes

| Issue | v2.0 Solution |
|-------|---------------|
| **Windows Gap** | All hook logic moved to Python. Shell scripts are now optional 1-line wrappers. `core/hook_runner.py` handles all platforms. |
| **Dependency Hell** | New `bootstrap/` directory with `setup_windows.bat` and `setup_mac.sh`. One-click virtual environment creation and dependency installation. |
| **Subagent Assumption** | Explicit Router pattern in CLAUDE.md. Claude is the dispatcher, not a passive reader. Commands explicitly invoke agents with required context. |
| **State Persistence** | New `project_state/` directory with `status.json` (machine-readable) alongside `plan.md` (human-readable). `state_manager.py` enables resume-from-checkpoint. |

## Architectural Changes

- `tools/` renamed to `core/` - signals this is the engine, not utilities
- `project_state/` added - durable state layer (intake.yaml, plan.md, status.json)
- `bootstrap/` added - one-time environment setup scripts
- `core/hook_runner.py` - cross-platform hook dispatcher
- `core/state_manager.py` - programmatic state tracking
- CLAUDE.md rewritten as explicit Router with Agent Routing Rules

---

# Table of Contents

1. Executive Summary
2. Strategic Rationale
3. Repository Architecture (v2.0)
4. Bootstrap System
5. CLAUDE.md Specification (Router Pattern)
6. Settings & Permissions
7. The Core Engine
8. State Management System
9. Hook System (Python-First)
10. Subagent Definitions
11. Slash Command Specifications
12. Intake Template System
13. Project Templates
14. Consultant User Journeys (v2.0)
15. Distribution & Onboarding
16. Maintenance & Iteration
17. Testing & Validation
18. Implementation Sequence (v2.0)
19. Non-Goals
20. Appendix: Complete File Contents

---

# I. Executive Summary

## 1.1 The Concept: Repository as Headless IDE

The Kearney AI Coding Assistant treats a Git repository as a "Headless IDE" where Claude Code acts as the operating system. Consultants clone the repo, run a one-time setup script, and immediately have access to AI-assisted development with programmatic brand enforcement.

This approach eliminates the need for custom web applications, hosting infrastructure, and user training on new UIs. Consultants work in the same Claude interface they already know, with guardrails baked into the repository itself.

## 1.2 What v2.0 Delivers

- One-click setup for Windows and Mac (bootstrap scripts)
- 100% Python-based automation (no shell script fragility)
- Explicit Router pattern for predictable agent behavior
- Machine-readable state for project resumption
- Programmatic brand enforcement (not just text rules)
- Cross-platform compatibility tested on Windows 10/11 and macOS

## 1.3 The 4-Step Consultant Experience

1. **Clone**: `git clone https://github.com/kearney-internal/kearney-ai-coding-assistant.git`
2. **Setup**: Double-click `bootstrap/setup_windows.bat` (or run `./bootstrap/setup_mac.sh`)
3. **Open**: Launch Claude Desktop, File > Open Folder
4. **Build**: Type `/init` and follow the workflow

> **SUCCESS**: Time from download to first output: < 15 minutes

## 1.4 Success Metrics

| Metric | Target |
|--------|--------|
| Setup success rate (Windows) | > 95% on first attempt |
| Time to first output | < 45 minutes from clone |
| Brand compliance rate | > 98% (programmatic enforcement) |
| Project resumption success | > 90% via /status |
| Consultant adoption | > 60% of D&A team in 30 days |

---

# II. Strategic Rationale

## 2.1 Why This Approach Wins

The Starter Kit turns a Git repository into a "Headless IDE" where Claude Code is the operating system. This is architecturally superior for a consulting workforce because:

### Zero Infrastructure
No servers to maintain, no databases to manage, no CI/CD pipelines to configure. The "infrastructure" is Anthropic's Claude service, which they maintain.

### Zero Training on New UIs
Consultants already use Claude. They don't need to learn a new web application. The only new knowledge is a handful of slash commands.

### Programmatic Enforcement
Brand compliance isn't a "please follow these rules" document. It's a Python program that runs automatically and blocks non-compliant outputs. You can't ship a green chart.

### State Persistence
Unlike chat-based AI, the Starter Kit maintains durable state in `project_state/status.json`. Consultants can close Claude, come back three days later, and resume exactly where they left off.

## 2.2 Comparison: v1.0 vs v2.0

| Aspect | v1.0 | v2.0 |
|--------|------|------|
| Windows support | Fragile (.sh scripts) | Robust (Python-first) |
| Environment setup | Assumed | One-click bootstrap |
| Agent behavior | Implicit | Explicit Router pattern |
| State persistence | Files only | Structured JSON state |
| Project resumption | Re-read all files | Load status.json |
| Brand enforcement | Text rules + checks | Programmatic gate |

---

# III. Repository Architecture (v2.0)

## 3.1 Directory Structure

> **v2.0 CHANGE**: Reorganized with `bootstrap/`, `core/`, and `project_state/` directories.

```
kearney-ai-coding-assistant/
│
├── CLAUDE.md                           # The Brain (Router Pattern)
├── README.md                           # Getting started guide
├── LICENSE                             # Kearney internal use only
├── VERSION                             # Semantic version (2.0.0)
│
├── bootstrap/                          # ONE-TIME SETUP (NEW)
│   ├── setup_windows.bat               # Double-click for Windows
│   ├── setup_mac.sh                    # Run for macOS/Linux
│   └── requirements.txt                # Python dependencies
│
├── .claude/                            # Claude Code configuration
│   ├── settings.json                   # Permissions, model config
│   │
│   ├── agents/                         # Subagent definitions
│   │   ├── planner.md                  # Execution planning agent
│   │   ├── steward.md                  # Task execution agent
│   │   ├── kds-reviewer.md             # Brand compliance reviewer
│   │   ├── data-analyst.md             # Data profiling specialist
│   │   └── presentation-builder.md     # PPTX generation expert
│   │
│   └── commands/                       # Slash commands
│       ├── init.md                     # /init
│       ├── intake.md                   # /interview
│       ├── plan.md                     # /plan
│       ├── execute.md                  # /execute (NEW)
│       ├── status.md                   # /status
│       ├── review.md                   # /review
│       ├── export.md                   # /export
│       └── help.md                     # /help
│
├── core/                               # THE ENGINE (RENAMED from tools/)
│   ├── __init__.py
│   ├── brand_guard.py                  # Programmatic brand enforcement
│   ├── chart_engine.py                 # KDS-compliant plotting
│   ├── slide_engine.py                 # PPTX generation
│   ├── data_profiler.py                # Dataset analysis
│   ├── hook_runner.py                  # Cross-platform hook dispatcher (NEW)
│   └── state_manager.py                # Project state management (NEW)
│
├── config/                             # Configuration files
│   ├── governance/
│   │   ├── brand.yaml                  # Colors, fonts, rules
│   │   └── rules.yaml                  # Non-negotiable constraints
│   │
│   ├── templates/                      # Project type configs
│   │   ├── analytics.yaml
│   │   ├── presentation.yaml
│   │   └── webapp.yaml
│   │
│   └── intake/                         # Intake question flows
│       ├── general.yaml
│       ├── analytics.yaml
│       └── presentation.yaml
│
├── project_state/                      # DURABLE STATE LAYER (NEW)
│   ├── intake.yaml                     # Captured requirements
│   ├── plan.md                         # Execution plan (human-readable)
│   └── status.json                     # Machine-readable state (NEW)
│
├── data/                               # User data
│   ├── raw/                            # Uploaded source files
│   └── processed/                      # Cleaned data
│
├── outputs/                            # Generated artifacts
│   ├── charts/
│   └── reports/
│
├── exports/                            # Final deliverables
│
├── templates/                          # Starter project structures
│   ├── analytics/
│   └── presentation/
│
└── docs/                               # Documentation
    ├── GETTING_STARTED.md
    ├── CONSULTANT_GUIDE.md
    ├── COMMAND_REFERENCE.md
    └── TROUBLESHOOTING.md
```

## 3.2 Key Architectural Decisions

### core/ vs tools/
Renamed from "tools" to "core" to signal this is the engine of the system, not optional utilities. All automation flows through `core/`.

### project_state/
Dedicated directory for durable project state. This separates "what the project is" (intake.yaml, plan.md, status.json) from "what it produces" (outputs/, exports/).

### bootstrap/
One-time setup scripts that create a virtual environment and install dependencies. This solves "Dependency Hell" explicitly.

---

# IV. Bootstrap System

> **v2.0 CHANGE**: New section addressing the Dependency Hell problem identified in v1.0 review.

The bootstrap system ensures consultants can set up a working environment with a single click, regardless of their technical expertise.

## 4.1 requirements.txt

```
# bootstrap/requirements.txt
# Kearney AI Coding Assistant - Python Dependencies
# Install via: pip install -r bootstrap/requirements.txt

# Data Processing
pandas>=2.0.0
openpyxl>=3.1.0

# Visualization
matplotlib>=3.8.0

# Image Processing
pillow>=10.0.0

# Document Generation
python-pptx>=0.6.21

# Configuration
pyyaml>=6.0

# Testing (optional, for development)
pytest>=7.0.0
```

## 4.2 setup_windows.bat

```batch
@echo off
echo.
echo ========================================
echo   KEARNEY AI CODING ASSISTANT
echo   Environment Setup for Windows
echo ========================================
echo.

:: 1. Check Python
echo [1/4] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Python is not installed or not in PATH.
    echo Please install Python 3.10+ from Kearney Software Center.
    echo.
    pause
    exit /b 1
)
echo         Python found.

:: 2. Create virtual environment
echo [2/4] Creating virtual environment...
if not exist ".venv" (
    python -m venv .venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
) else (
    echo         Virtual environment already exists.
)

:: 3. Install dependencies
echo [3/4] Installing KDS tools...
call .venv\Scripts\pip install -q -r bootstrap\requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies.
    pause
    exit /b 1
)

:: 4. Verify installation
echo [4/4] Verifying installation...
.venv\Scripts\python -c "import pandas, matplotlib, pptx, yaml, PIL; print('All modules OK')"
if %errorlevel% neq 0 (
    echo [ERROR] Module verification failed.
    pause
    exit /b 1
)

echo.
echo ========================================
echo   SUCCESS! Environment Ready.
echo ========================================
echo.
echo Next steps:
echo   1. Open Claude Desktop
echo   2. File ^> Open Folder ^> Select this directory
echo   3. Type: /help
echo.
pause
```

## 4.3 setup_mac.sh

```bash
#!/bin/bash

echo ''
echo '========================================'
echo '  KEARNEY AI CODING ASSISTANT'
echo '  Environment Setup for macOS/Linux'
echo '========================================'
echo ''

# 1. Check Python
echo '[1/4] Checking Python installation...'
if ! command -v python3 &> /dev/null; then
    echo '[ERROR] Python 3 is not installed.'
    echo 'Please install Python 3.10+ via Homebrew: brew install python3'
    exit 1
fi
echo '        Python found.'

# 2. Create virtual environment
echo '[2/4] Creating virtual environment...'
if [ ! -d '.venv' ]; then
    python3 -m venv .venv
else
    echo '        Virtual environment already exists.'
fi

# 3. Install dependencies
echo '[3/4] Installing KDS tools...'
.venv/bin/pip install -q -r bootstrap/requirements.txt

# 4. Verify installation
echo '[4/4] Verifying installation...'
.venv/bin/python -c 'import pandas, matplotlib, pptx, yaml, PIL; print("All modules OK")'

echo ''
echo '========================================'
echo '  SUCCESS! Environment Ready.'
echo '========================================'
echo ''
echo 'Next steps:'
echo '  1. Open Claude Desktop'
echo '  2. File > Open Folder > Select this directory'
echo '  3. Type: /help'
echo ''
```

## 4.4 Integration with Claude Code

The bootstrap scripts create a `.venv` directory. Claude Code hooks reference this environment:

```
# In .claude/settings.json, hooks use the venv Python:
# Windows: .venv\\Scripts\\python core/hook_runner.py
# macOS:   .venv/bin/python core/hook_runner.py
```

> **NOTE**: Claude Code on Windows may require the full path to Python. The settings.json uses a platform-agnostic approach by calling 'python' and relying on the venv activation in the user's shell.

---

# V. CLAUDE.md Specification (Router Pattern)

> **v2.0 CHANGE**: Complete rewrite implementing explicit Router pattern for predictable agent behavior.

The CLAUDE.md file is the brain of the Starter Kit. It defines Claude as a Router that explicitly dispatches work to specialized agents based on command invocation.

## 5.1 Complete CLAUDE.md

```markdown
# Kearney AI Code Builder (v2.0)

## SYSTEM PRIME DIRECTIVE

You are a Kearney Digital & Analytics AI Assistant operating as a ROUTER.
You dispatch work to specialized agents and enforce brand compliance
programmatically through the core/ Python engine.

You MUST NOT write raw code for charts, slides, or data processing.
You MUST use the core/ engine for all operations.
You MUST maintain state in project_state/ for project continuity.

---

## BRAND GUARDRAILS (Non-Negotiable)

These rules are enforced programmatically by core/brand_guard.py:

1. **PRIMARY COLOR**: Kearney Purple (#7823DC) - all accents
2. **FORBIDDEN COLORS**: Green (#00FF00, #2E7D32, etc.) - NEVER use
3. **TYPOGRAPHY**: Inter font (Arial fallback) - weights 400/500/600
4. **CHARTS**: No gridlines. Data labels outside bars/slices.
5. **NO EMOJIS**: Never in any output
6. **DARK MODE**: Default background #1E1E1E

Violations will be caught by hooks and blocked before commit.

---

## AGENT ROUTING RULES

You, the primary Claude process, are the ROUTER. When a /project:*
command is invoked, you MUST:

1. Load the command spec from .claude/commands/
2. Identify which agent(s) to invoke
3. Load required context files for that agent
4. Execute the agent's workflow
5. Update project_state/ with results

### Command -> Agent Mapping

| Command | Agent | Context to Load |
|---------|-------|-----------------|
| /init | ROUTER (you) | config/templates/*.yaml |
| /interview | INTAKE_SPECIALIST | config/intake/*.yaml |
| /plan | PLANNER | project_state/intake.yaml, data/raw/** |
| /execute | STEWARD | project_state/status.json, project_state/plan.md |
| /status | ROUTER (you) | project_state/status.json |
| /review | KDS_REVIEWER | outputs/**, config/governance/** |
| /export | PRESENTATION_BUILDER | outputs/**, project_state/intake.yaml |

### Agent Invocation

When you need to invoke an agent, explicitly state:

```
[ROUTING TO: @planner]
[CONTEXT: project_state/intake.yaml, data/raw/sales.csv]
```

Then adopt that agent's persona from .claude/agents/{agent}.md.

---

## TOOL UTILIZATION RULES

### Charts
NEVER use matplotlib directly.
ALWAYS use:
```python
from core.chart_engine import KDSChart
chart = KDSChart()
chart.bar(data, labels, title='Title')
chart.save('outputs/charts/filename.png')
```

### Presentations
NEVER use python-pptx directly.
ALWAYS use:
```python
from core.slide_engine import KDSPresentation
pres = KDSPresentation()
pres.add_title_slide('Title')
pres.save('exports/filename.pptx')
```

### Data Processing
ALWAYS use:
```python
from core.data_profiler import profile_dataset
profile = profile_dataset('data/raw/file.csv')
```

### Validation
After generating outputs, ALWAYS run:
```bash
python core/brand_guard.py outputs/
```

---

## STATE MANAGEMENT

Project state lives in project_state/:

- **intake.yaml**: Human-readable requirements
- **plan.md**: Human-readable execution plan
- **status.json**: Machine-readable state (for resumption)

### Resuming a Project

When a session starts, check if project_state/status.json exists.
If yes, load it and report current status:

```
Project: {name}
Phase: {current_phase}
Completed: {n} / {total} tasks
Next task: {next_task_description}
```

### Updating State

After completing a task, update status.json:
```python
from core.state_manager import update_task_status
update_task_status(task_id='1.2', status='done')
```

---

## AVAILABLE COMMANDS

| Command | Purpose |
|---------|---------|
| /init | Initialize new project from template |
| /interview | Gather requirements interactively |
| /plan | Generate execution plan |
| /execute | Execute next pending task |
| /status | Show current project state |
| /review | Run brand compliance check |
| /export | Generate final deliverables |
| /help | Show this command list |

---

## STARTUP BEHAVIOR

When a new session starts:

1. Check if project_state/status.json exists
2. If YES: Greet with project status and offer to continue
3. If NO: Greet and suggest /init for new project

---

## NON-GOALS (Do NOT Build)

- User authentication
- Multi-tenant features
- Arbitrary code execution outside core/
- Custom plugins
- Mobile layouts
- External API integrations unless specified
```

---

# VI. Settings & Permissions

## 6.1 .claude/settings.json (v2.0)

> **v2.0 CHANGE**: Updated to use Python-based hook_runner.py instead of shell scripts.

```json
{
  "model": "claude-sonnet-4-5-20250514",
  "maxTokens": 8192,
  
  "permissions": {
    "allowedTools": [
      "Read",
      "Write(data/**)",
      "Write(outputs/**)",
      "Write(exports/**)",
      "Write(project_state/**)",
      "Bash(python core/*.py *)",
      "Bash(.venv/Scripts/python core/*.py *)",
      "Bash(.venv/bin/python core/*.py *)",
      "Bash(git status)",
      "Bash(git diff)",
      "Bash(git add)",
      "Bash(git commit)",
      "Glob",
      "Grep"
    ],
    "deny": [
      "Read(.env*)",
      "Read(**/secrets/**)",
      "Write(.claude/**)",
      "Write(CLAUDE.md)",
      "Write(config/governance/**)",
      "Write(core/**)",
      "Write(bootstrap/**)",
      "Bash(rm -rf *)",
      "Bash(sudo *)",
      "Bash(curl *)",
      "Bash(wget *)",
      "Bash(pip install *)"
    ]
  },
  
  "hooks": {
    "PostToolUse:Write": [
      {
        "matcher": "outputs/**",
        "command": "python core/hook_runner.py post-edit $file"
      },
      {
        "matcher": "exports/**",
        "command": "python core/hook_runner.py post-edit $file"
      }
    ],
    "PreCommit": [
      {
        "command": "python core/hook_runner.py pre-commit"
      }
    ]
  }
}
```

## 6.2 Permission Philosophy

### What Claude CAN Do
- **Read**: Unrestricted for context gathering
- **Write**: data/, outputs/, exports/, project_state/
- **Bash**: Only core/*.py scripts and git commands
- **Glob/Grep**: Unrestricted for navigation

### What Claude CANNOT Do
- Modify its own configuration (.claude/, CLAUDE.md)
- Modify the engine (core/, bootstrap/)
- Modify governance rules (config/governance/)
- Run destructive commands (rm, sudo, curl, wget)
- Install packages (pip install)

---

# VII. The Core Engine

> **v2.0 CHANGE**: Renamed from 'tools/' to 'core/' and added hook_runner.py and state_manager.py.

The `core/` directory is the engine of the Starter Kit. All automation, validation, and generation flows through these Python modules.

## 7.1 Module Overview

| Module | Purpose |
|--------|---------|
| brand_guard.py | Programmatic brand enforcement. Validates colors, fonts, gridlines in outputs. |
| chart_engine.py | KDS-compliant charting. Wraps matplotlib with brand defaults. |
| slide_engine.py | PPTX generation with Kearney templates and branding. |
| data_profiler.py | Dataset analysis: schema, statistics, quality issues. |
| hook_runner.py (NEW) | Cross-platform hook dispatcher. Handles post-edit and pre-commit events. |
| state_manager.py (NEW) | Project state management. Read/write status.json for resumption. |

## 7.2 hook_runner.py

The cross-platform hook dispatcher that replaces shell scripts:

```python
# core/hook_runner.py
"""
Cross-platform hook dispatcher for Claude Code.
Replaces shell scripts to ensure Windows compatibility.

Usage:
  python core/hook_runner.py post-edit <file>
  python core/hook_runner.py pre-commit
"""

import sys
from pathlib import Path

# Import sibling modules
from core import brand_guard, state_manager


def handle_post_edit(target: Path) -> int:
    """Run after Claude writes a file."""
    if not target.exists():
        return 0  # File was deleted, nothing to check
    
    # Only check relevant file types
    if target.suffix in ['.png', '.jpg', '.svg', '.py', '.html', '.css']:
        issues = brand_guard.check_file(target)
        if issues:
            print(f'BRAND VIOLATION: {target}')
            for issue in issues:
                print(f'  - {issue}')
            return 1
    
    return 0


def handle_pre_commit() -> int:
    """Run before git commit."""
    all_issues = []
    
    # Check outputs directory
    outputs_dir = Path('outputs')
    if outputs_dir.exists():
        issues = brand_guard.check_directory(outputs_dir)
        all_issues.extend(issues)
    
    # Check exports directory
    exports_dir = Path('exports')
    if exports_dir.exists():
        issues = brand_guard.check_directory(exports_dir)
        all_issues.extend(issues)
    
    # Warn if core state files missing
    state_warnings = state_manager.warn_if_missing_core_files()
    for warning in state_warnings:
        print(f'WARNING: {warning}')
    
    if all_issues:
        print('BRAND VIOLATIONS FOUND:')
        for issue in all_issues:
            print(f'  - {issue}')
        print('Fix these issues before committing.')
        return 1
    
    print('Pre-commit checks passed.')
    return 0


def main():
    if len(sys.argv) < 2:
        print('Usage: python core/hook_runner.py <event> [target]')
        sys.exit(1)
    
    event = sys.argv[1]
    target = Path(sys.argv[2]) if len(sys.argv) > 2 else None
    
    if event == 'post-edit':
        if target is None:
            print('post-edit requires a target file')
            sys.exit(1)
        sys.exit(handle_post_edit(target))
    
    elif event == 'pre-commit':
        sys.exit(handle_pre_commit())
    
    else:
        print(f'Unknown event: {event}')
        sys.exit(1)


if __name__ == '__main__':
    main()
```

---

# VIII. State Management System

> **v2.0 CHANGE**: New section implementing machine-readable state for project resumption.

The state management system enables consultants to resume projects after closing Claude. `status.json` provides machine-readable state that Claude can load instantly.

## 8.1 State Schema

```json
{
  "project_name": "acme-revenue-q4",
  "template": "analytics",
  "created_at": "2025-12-01T10:30:00Z",
  "updated_at": "2025-12-01T14:45:00Z",
  
  "current_phase": "Phase 2: Analysis",
  "current_task": "2.1",
  
  "tasks": [
    {
      "id": "1.1",
      "phase": "Phase 1: Data Preparation",
      "description": "Profile sales.csv",
      "status": "done",
      "completed_at": "2025-12-01T11:00:00Z"
    },
    {
      "id": "1.2",
      "phase": "Phase 1: Data Preparation",
      "description": "Clean and validate data",
      "status": "done",
      "completed_at": "2025-12-01T12:30:00Z"
    },
    {
      "id": "2.1",
      "phase": "Phase 2: Analysis",
      "description": "Revenue by region chart",
      "status": "in_progress",
      "started_at": "2025-12-01T14:00:00Z"
    },
    {
      "id": "2.2",
      "phase": "Phase 2: Analysis",
      "description": "YoY growth comparison",
      "status": "pending"
    }
  ],
  
  "artifacts": [
    "data/processed/sales_clean.parquet",
    "outputs/reports/profile_report.md"
  ],
  
  "history": [
    {"action": "init", "timestamp": "2025-12-01T10:30:00Z"},
    {"action": "intake_complete", "timestamp": "2025-12-01T10:45:00Z"},
    {"action": "plan_approved", "timestamp": "2025-12-01T11:00:00Z"},
    {"action": "task_1.1_done", "timestamp": "2025-12-01T11:30:00Z"},
    {"action": "task_1.2_done", "timestamp": "2025-12-01T12:30:00Z"}
  ]
}
```

## 8.2 state_manager.py

```python
# core/state_manager.py
"""
Project state management for resumable workflows.
Manages project_state/status.json for machine-readable state.
"""

import json
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict, field
from typing import List, Literal, Optional

STATE_FILE = Path('project_state/status.json')
PLAN_FILE = Path('project_state/plan.md')

TaskStatus = Literal['pending', 'in_progress', 'done', 'blocked']


@dataclass
class Task:
    id: str
    phase: str
    description: str
    status: TaskStatus = 'pending'
    started_at: Optional[str] = None
    completed_at: Optional[str] = None


@dataclass
class ProjectState:
    project_name: str
    template: str
    created_at: str
    updated_at: str
    current_phase: str = ''
    current_task: Optional[str] = None
    tasks: List[Task] = field(default_factory=list)
    artifacts: List[str] = field(default_factory=list)
    history: List[dict] = field(default_factory=list)


def load_state() -> Optional[ProjectState]:
    """Load project state from status.json."""
    if not STATE_FILE.exists():
        return None
    
    data = json.loads(STATE_FILE.read_text())
    tasks = [Task(**t) for t in data.get('tasks', [])]
    
    return ProjectState(
        project_name=data['project_name'],
        template=data['template'],
        created_at=data['created_at'],
        updated_at=data['updated_at'],
        current_phase=data.get('current_phase', ''),
        current_task=data.get('current_task'),
        tasks=tasks,
        artifacts=data.get('artifacts', []),
        history=data.get('history', [])
    )


def save_state(state: ProjectState) -> None:
    """Save project state to status.json."""
    state.updated_at = datetime.utcnow().isoformat() + 'Z'
    
    data = asdict(state)
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(data, indent=2))


def init_project(project_name: str, template: str) -> ProjectState:
    """Initialize a new project state."""
    now = datetime.utcnow().isoformat() + 'Z'
    
    state = ProjectState(
        project_name=project_name,
        template=template,
        created_at=now,
        updated_at=now,
        history=[{'action': 'init', 'timestamp': now}]
    )
    
    save_state(state)
    return state


def init_from_plan(project_name: str, template: str) -> ProjectState:
    """Parse plan.md and initialize tasks in status.json."""
    state = load_state() or init_project(project_name, template)
    
    if not PLAN_FILE.exists():
        return state
    
    plan_content = PLAN_FILE.read_text()
    
    # Parse tasks from plan.md
    # Looking for: - [ ] Task description
    import re
    current_phase = ''
    task_id = 0
    phase_num = 0
    
    for line in plan_content.split('\n'):
        # Detect phase headers
        if line.startswith('## Phase'):
            current_phase = line.replace('##', '').strip()
            phase_num += 1
            task_id = 0
        
        # Detect tasks
        task_match = re.match(r'^- \[[ x]\] (.+)$', line)
        if task_match:
            task_id += 1
            description = task_match.group(1)
            is_done = '[x]' in line.lower()
            
            task = Task(
                id=f'{phase_num}.{task_id}',
                phase=current_phase,
                description=description,
                status='done' if is_done else 'pending'
            )
            state.tasks.append(task)
    
    # Set current phase and task
    pending = [t for t in state.tasks if t.status == 'pending']
    if pending:
        state.current_task = pending[0].id
        state.current_phase = pending[0].phase
    
    state.history.append({
        'action': 'plan_parsed',
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    })
    
    save_state(state)
    return state


def update_task_status(task_id: str, status: TaskStatus) -> ProjectState:
    """Update a task status and advance current_task if needed."""
    state = load_state()
    if state is None:
        raise ValueError('No project state found')
    
    now = datetime.utcnow().isoformat() + 'Z'
    
    for task in state.tasks:
        if task.id == task_id:
            task.status = status
            if status == 'in_progress':
                task.started_at = now
            elif status == 'done':
                task.completed_at = now
            break
    
    # Advance to next pending task
    pending = [t for t in state.tasks if t.status == 'pending']
    if pending:
        state.current_task = pending[0].id
        state.current_phase = pending[0].phase
    else:
        state.current_task = None
        state.current_phase = 'Complete'
    
    state.history.append({
        'action': f'task_{task_id}_{status}',
        'timestamp': now
    })
    
    save_state(state)
    return state


def get_status_summary() -> str:
    """Get a human-readable status summary."""
    state = load_state()
    if state is None:
        return 'No project initialized. Run /init to start.'
    
    done = len([t for t in state.tasks if t.status == 'done'])
    total = len(state.tasks)
    
    next_task = None
    for t in state.tasks:
        if t.id == state.current_task:
            next_task = t.description
            break
    
    summary = f'''
Project: {state.project_name}
Template: {state.template}
Phase: {state.current_phase}
Progress: {done} / {total} tasks complete
'''
    
    if next_task:
        summary += f'Next task: {next_task}\n'
    
    return summary.strip()


def warn_if_missing_core_files() -> List[str]:
    """Check if core project files are missing."""
    warnings = []
    
    if not Path('project_state/intake.yaml').exists():
        warnings.append('No intake.yaml found. Run /interview.')
    
    if not Path('project_state/plan.md').exists():
        warnings.append('No plan.md found. Run /plan.')
    
    return warnings
```

## 8.3 Integration with Workflow

The state manager integrates with the workflow at key points:

1. `/init` calls `init_project()` to create initial status.json
2. `/plan` calls `init_from_plan()` to parse tasks from plan.md
3. `/execute` calls `load_state()` to find next task, then `update_task_status()` when done
4. `/status` calls `get_status_summary()` for instant project overview
5. Session startup checks `STATE_FILE.exists()` to enable resumption

---

# IX. Hook System (Python-First)

> **v2.0 CHANGE**: Hooks now route through hook_runner.py for Windows compatibility.

## 9.1 Hook Architecture

All hooks route through `core/hook_runner.py`, which provides:

- Cross-platform compatibility (Windows/macOS/Linux)
- Centralized logic in Python (not scattered shell scripts)
- Easy testing and debugging
- Consistent error handling and reporting

## 9.2 Hook Events

| Event | Behavior |
|-------|----------|
| post-edit | Runs after Claude writes a file to outputs/ or exports/. Validates brand compliance. Blocks if violations found. |
| pre-commit | Runs before git commit. Validates all outputs and exports. Warns if core files missing. Blocks if violations found. |

## 9.3 Optional Shell Wrappers

For environments that require shell scripts (e.g., git hooks), thin wrappers can call hook_runner.py:

```bash
# .githooks/pre-commit (optional, for git hook integration)
#!/bin/bash
python core/hook_runner.py pre-commit
```

> **NOTE**: These are OPTIONAL. The primary hook mechanism is through .claude/settings.json, which calls hook_runner.py directly.

---

# X. Subagent Definitions

Subagents are specialized AI workers defined in `.claude/agents/`. Each has a specific role, context requirements, and tool permissions.

## 10.1 Agent Summary

| Agent | Role | Key Output |
|-------|------|------------|
| @planner | Generate execution plan | project_state/plan.md |
| @steward | Execute tasks from plan | outputs/*, updated status.json |
| @kds-reviewer | Validate brand compliance | Pass/fail report |
| @data-analyst | Profile and analyze data | outputs/reports/profile.md |
| @presentation-builder | Generate PPTX | exports/*.pptx |

Full agent specifications are provided in the Appendix.

---

# XI. Slash Command Specifications

## 11.1 Command Overview

| Command | Purpose |
|---------|---------|
| /init | Initialize new project. Creates structure, initializes status.json. |
| /interview | Gather requirements. Writes project_state/intake.yaml. |
| /plan | Generate plan via @planner. Writes plan.md, parses into status.json. |
| /execute | Execute next pending task via @steward. Updates status.json. |
| /status | Show current project state from status.json. Enables resumption. |
| /review | Run brand compliance via @kds-reviewer and brand_guard.py. |
| /export | Generate final deliverables via @presentation-builder. |
| /help | Display available commands and current project state. |

Full command specifications are provided in the Appendix.

---

# XVIII. Implementation Sequence (v2.0)

> **v2.0 CHANGE**: Reordered to build core engine first, then wire hooks and commands.

## Phase 1: Core Engine (Days 1-3)

1. Create repository structure per Section III
2. Implement `core/__init__.py`
3. Implement `core/brand_guard.py` with `check_file()` and `check_directory()`
4. Implement `core/chart_engine.py` with `KDSChart` class
5. Implement `core/state_manager.py` with full schema
6. Create `config/governance/brand.yaml`
7. Write pytest tests for all core modules

**Deliverable**: All core modules working and tested. Run tests to confirm.

## Phase 2: Bootstrap (Days 4-5)

1. Create `bootstrap/requirements.txt`
2. Create `bootstrap/setup_windows.bat`
3. Create `bootstrap/setup_mac.sh`
4. Test that the scripts work (simulate the checks)

**Deliverable**: One-click setup scripts ready.

## Phase 3: Router + Hooks (Days 6-7)

1. Write `CLAUDE.md` with Router pattern (Section V of Master Plan)
2. Implement `core/hook_runner.py`
3. Create `.claude/settings.json` with permissions and hooks

**Deliverable**: Router pattern and hook system configured.

## Phase 4: Agents + Commands (Days 8-10)

1. Write all agents in `.claude/agents/` (planner.md, steward.md, kds-reviewer.md, data-analyst.md, presentation-builder.md)
2. Write all commands in `.claude/commands/` (init.md, intake.md, plan.md, execute.md, status.md, review.md, export.md, help.md)
3. Create intake templates in `config/intake/`

**Deliverable**: Full agent and command system.

## Phase 5: Templates + Documentation (Days 11-12)

1. Create `templates/analytics/` structure
2. Create `templates/presentation/` structure
3. Write `docs/GETTING_STARTED.md`
4. Write `docs/CONSULTANT_GUIDE.md`
5. Write `docs/COMMAND_REFERENCE.md`
6. Write `docs/TROUBLESHOOTING.md` (include Windows-specific section)
7. Create example project in `examples/`

**Deliverable**: Complete documentation and templates.

## Phase 6: Testing + Launch (Days 13-15)

1. Run end-to-end tests on Windows
2. Run end-to-end tests on macOS
3. Conduct UAT with 3-5 consultants
4. Fix critical issues
5. Set up GitHub repository
6. Record video tutorial
7. Announce to D&A team

**Deliverable**: Live Starter Kit v2.0 available to all consultants.

---

# XIX. Non-Goals

Explicitly out of scope for v2.0:

## Enterprise Features
- No user authentication
- No multi-tenant support
- No RBAC
- No audit logging

## External Integrations
- No cloud storage (S3, Azure, GCS)
- No OAuth/SSO
- No Slack/Teams notifications

## Advanced Execution
- No arbitrary code execution outside core/
- No user-uploaded plugins
- No custom agent definitions

## UI/UX
- No custom web interface
- No mobile support

---

# XX. Appendix: Key File Contents

## config/governance/brand.yaml

```yaml
# Kearney Design System - Brand Tokens
# Source of truth for programmatic brand enforcement

version: 1.0.0

colors:
  primary:
    purple: "#7823DC"
    purple_light: "#9B4DFF"
    purple_dark: "#5A1BA8"
  
  background:
    dark: "#1E1E1E"
    light: "#FFFFFF"
  
  text:
    primary: "#FFFFFF"
    secondary: "#CCCCCC"
    muted: "#666666"
  
  accent:
    - "#7823DC"  # Primary purple
    - "#9B4DFF"  # Light purple
    - "#5A1BA8"  # Dark purple
    - "#A0A0A0"  # Gray
  
  forbidden:
    - "#00FF00"  # Pure green
    - "#00FF00"  # Lime
    - "#2E7D32"  # Material green
    - "#4CAF50"  # Green 500
    - "#8BC34A"  # Light green
    - "#CDDC39"  # Lime
    - "#009688"  # Teal (too green)

typography:
  primary: "Inter"
  fallback: "Arial"
  weights:
    - 400  # Regular
    - 500  # Medium
    - 600  # Semi-bold
  
  forbidden:
    - "Comic Sans"
    - "Papyrus"
    - "Impact"

charts:
  gridlines: false
  axis_color: "#666666"
  data_label_position: "outside"
  default_colors:
    - "#7823DC"
    - "#9B4DFF"
    - "#5A1BA8"
    - "#A0A0A0"
    - "#666666"

content:
  emojis: false
  success_color: "#7823DC"  # Use purple, not green
  error_color: "#DC2323"
```

## README.md

```markdown
# Kearney AI Coding Assistant

AI-assisted development with programmatic brand enforcement.

## Quick Start

1. **Clone**: `git clone https://github.com/kearney-internal/kearney-ai-coding-assistant.git`
2. **Setup**: Double-click `bootstrap/setup_windows.bat` (or `./bootstrap/setup_mac.sh`)
3. **Open**: Launch Claude Desktop → File → Open Folder → Select this directory
4. **Start**: Type `/help`

## Commands

| Command | Purpose |
|---------|---------|
| `/init` | Initialize new project |
| `/interview` | Gather requirements |
| `/plan` | Generate execution plan |
| `/execute` | Execute next task |
| `/status` | Show project status |
| `/review` | Check brand compliance |
| `/export` | Generate deliverables |
| `/help` | Show help |

## Documentation

- [Getting Started](docs/GETTING_STARTED.md)
- [Consultant Guide](docs/CONSULTANT_GUIDE.md)
- [Command Reference](docs/COMMAND_REFERENCE.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)

## Support

- Slack: #claude-code-help
- Email: d&a-support@kearney.com
```

---

# END OF KEARNEY AI CODING ASSISTANT MASTER PLAN v2.0

*Clone. Setup. Build. Brand-Compliant from Line One.*

*Windows-Ready. Python-First. State-Persistent.*

**Kearney Digital & Analytics**
