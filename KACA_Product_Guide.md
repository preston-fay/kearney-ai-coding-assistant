# KACA Product Guide

## Comprehensive Technical and Product Documentation for AI Research Partners

**Version:** 2.0.0
**Last Updated:** 2025-12-04
**Purpose:** Enable AI assistants (Gemini, ChatGPT, etc.) to understand KACA and provide meaningful enhancement recommendations

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [System Architecture](#2-system-architecture)
3. [Core Engines](#3-core-engines)
4. [Agent System](#4-agent-system)
5. [Command System](#5-command-system)
6. [Data Model and State](#6-data-model-and-state)
7. [Brand and Design System (KDS)](#7-brand-and-design-system-kds)
8. [Interview System](#8-interview-system)
9. [Skills System](#9-skills-system)
10. [Current Capabilities](#10-current-capabilities)
11. [Known Limitations and Pain Points](#11-known-limitations-and-pain-points)
12. [Technical Stack](#12-technical-stack)
13. [Strategic Context](#13-strategic-context)
14. [Research Guidelines](#14-research-guidelines)

---

## 1. Executive Summary

### What is KACA?

**KACA (Kearney AI Code Builder)** is a Claude Code-powered development framework designed specifically for management consulting deliverables. It transforms requirements gathering, execution, and brand compliance into a structured, repeatable workflow for Kearney Digital & Analytics consultants.

### Who is it for?

- **Primary Users:** Kearney consultants creating data visualizations, presentations, dashboards, and analytical deliverables
- **Secondary Users:** Internal teams building client-facing tools and prototypes
- **Technical Context:** Users with minimal coding experience who need production-quality outputs

### Primary Value Proposition

1. **Automated Brand Compliance:** Programmatic enforcement of Kearney Design System (KDS) rules eliminates manual brand review
2. **Structured Requirements Gathering:** Interview-driven specification system captures complete requirements before execution
3. **Repeatable Workflows:** State management enables session resumption and project continuity
4. **Multi-Format Output:** Single specification produces charts, presentations, documents, dashboards, and web apps
5. **LLM-Agnostic Execution:** Claude designs, Python engines execute deterministically

### Core Philosophy

```
"LLM designs, Python executes"
```

Claude acts as a ROUTER that dispatches work to specialized agents while Python engines handle all actual file generation. This separation ensures:
- Consistent, predictable outputs
- Programmatic brand compliance
- Testable, deterministic execution
- State persistence across sessions

---

## 2. System Architecture

### 2.1 Router-Agent Pattern

KACA implements a Router-Agent architecture where Claude serves as the primary orchestrator:

```
User Input -> [ROUTER (Claude)] -> [AGENT] -> [CORE ENGINE] -> Output
                    |
                    +-> Loads agent context from .claude/agents/
                    +-> Dispatches to specialized agent
                    +-> Agent uses core/ Python engines
                    +-> Updates project_state/
```

### 2.2 Execution Flow

```
1. /interview    -> @interviewer    -> spec.yaml (requirements)
2. /plan         -> @planner        -> plan.md, status.json (execution plan)
3. /execute      -> @steward        -> outputs/* (artifacts)
4. /review       -> @kds-reviewer   -> validation report
5. /export       -> @presentation-builder -> exports/* (deliverables)
```

### 2.3 File Structure

```
kearney-ai-coding-assistant/
|-- CLAUDE.md                    # Primary system prompt and instructions
|-- VERSION                      # Current version (2.0.0)
|-- scaffold.py                  # Project scaffolding script
|
|-- core/                        # Python execution engines
|   |-- __init__.py              # Public API exports
|   |-- brand_guard.py           # Brand compliance validation
|   |-- brand_config.py          # Brand color constants
|   |-- chart_engine.py          # Matplotlib chart generation
|   |-- slide_engine.py          # PowerPoint generation
|   |-- document_engine.py       # Word document generation
|   |-- spreadsheet_engine.py    # Excel generation
|   |-- webapp_engine.py         # HTML/Streamlit/React generation
|   |-- kds_theme.py             # Design system tokens (frozen dataclass)
|   |-- kds_data.py              # Data abstraction layer
|   |-- kds_utils.py             # Safe file I/O utilities
|   |-- streamlit_utils.py       # Streamlit deployment helpers
|   |-- data_profiler.py         # Dataset analysis and profiling
|   |-- data_handler.py          # DuckDB-based large file handling
|   |-- interview_engine.py      # Requirements gathering engine
|   |-- spec_manager.py          # Specification CRUD operations
|   |-- state_manager.py         # Project state tracking
|   |-- workspace_guard.py       # Template vs project detection
|
|-- config/
|   |-- interviews/              # Interview tree YAML definitions
|   |   |-- modeling.yaml        # ML/statistical modeling interview
|   |   |-- dashboard.yaml       # Dashboard/webapp interview
|   |   |-- presentation.yaml    # Presentation interview
|   |   |-- analytics.yaml       # Analytics interview
|   |   |-- proposal.yaml        # Proposal interview
|   |   |-- research.yaml        # Research interview
|   |   |-- data_engineering.yaml
|   |   |-- webapp.yaml
|   |
|   |-- skills/                  # Best practice documentation
|   |   |-- kearney-visualization.md
|   |   |-- kearney-pptx.md
|   |   |-- kearney-docx.md
|   |   |-- kearney-xlsx.md
|   |   |-- kearney-markdown.md
|   |   |-- kearney-webapp.md
|   |
|   |-- templates/               # Project templates
|   |   |-- analytics.yaml
|   |   |-- presentation.yaml
|   |   |-- webapp.yaml
|   |
|   |-- governance/
|       |-- brand.yaml           # KDS brand rules configuration
|
|-- .claude/
|   |-- commands/                # Slash command definitions
|   |   |-- interview.md
|   |   |-- plan.md
|   |   |-- execute.md
|   |   |-- review.md
|   |   |-- export.md
|   |   |-- spec.md
|   |   |-- edit.md
|   |   |-- history.md
|   |   |-- status.md
|   |   |-- webapp.md
|   |   |-- help.md
|   |   |-- init.md
|   |   |-- compact.md
|   |   |-- reset.md
|   |   |-- rollback.md
|   |
|   |-- agents/                  # Agent persona definitions
|       |-- interviewer.md
|       |-- planner.md
|       |-- steward.md
|       |-- kds-reviewer.md
|       |-- presentation-builder.md
|       |-- dashboard_builder.md
|       |-- document-builder.md
|       |-- data-analyst.md
|       |-- spec-editor.md
|
|-- docs/                        # Documentation
|   |-- QUICK_START.md
|   |-- USER_GUIDE.md
|   |-- DEVELOPER_GUIDE.md
|   |-- TROUBLESHOOTING.md
|   |-- CONSULTANT_GUIDE.md
|   |-- KACA_Command_Reference.md
|
|-- project_state/               # Runtime state (per-project)
|   |-- spec.yaml                # Living requirements document
|   |-- plan.md                  # Execution plan
|   |-- status.json              # Task tracking state
|   |-- spec_history/            # Spec version history
|
|-- data/
|   |-- raw/                     # Input data files
|   |-- processed/               # Transformed data
|
|-- outputs/
|   |-- charts/                  # Generated visualizations
|   |-- reports/                 # Analysis reports
|
|-- exports/                     # Final deliverables
```

### 2.4 Scaffolding System

Projects are created via `scaffold.py` which:

1. Creates a new project directory
2. Creates symlinks (Mac/Linux) or junctions (Windows) to template `core/` and `config/`
3. Copies project-specific files (CLAUDE.md, .claude/, etc.)
4. Creates `.kaca-version.json` to mark as scaffolded project
5. Creates empty `data/`, `outputs/`, `exports/`, `project_state/` directories

This allows multiple projects to share a single template installation while maintaining isolated state.

---

## 3. Core Engines

### 3.1 chart_engine.py (KDSChart)

**Purpose:** Generate brand-compliant matplotlib charts

**Key Class:** `KDSChart`

**Methods:**
- `bar(data, labels, title, horizontal=False)` - Bar charts
- `line(data, labels, title)` - Line charts
- `pie(data, labels, title)` - Pie charts (max 5 slices)
- `scatter(x, y, title, labels=None)` - Scatter plots
- `save(path, format='png', dpi=150)` - Save chart

**Enforced Rules:**
- No gridlines
- Data labels outside bars/slices
- Kearney Purple (#7823DC) primary color
- Dark background (#1E1E1E) default
- No green colors ever

**Example:**
```python
from core.chart_engine import KDSChart

chart = KDSChart()
chart.bar(
    data=[4.2, 3.1, 2.8, 2.1],
    labels=['North', 'South', 'East', 'West'],
    title='Northeast Leads Revenue Growth'
)
chart.save('outputs/charts/revenue.png')
```

### 3.2 slide_engine.py (KDSPresentation)

**Purpose:** Generate brand-compliant PowerPoint presentations

**Key Class:** `KDSPresentation`

**Methods:**
- `add_title_slide(title, subtitle='')` - Title slide
- `add_section_slide(section_title, section_number=None)` - Section divider
- `add_content_slide(title, bullet_points)` - Bullet point slide
- `add_chart_slide(title, chart_path, caption='')` - Chart with context
- `add_two_column_slide(title, left_content, right_content)` - Two-column layout
- `add_table_slide(title, headers, rows)` - Data table
- `add_closing_slide(title, contact_info)` - Thank you slide
- `save(path)` - Save to .pptx

**Specifications:**
- 16:9 aspect ratio (13.333" x 7.5")
- Dark mode default
- Inter/Arial typography
- Kearney Purple accents

### 3.3 document_engine.py (KDSDocument)

**Purpose:** Generate brand-compliant Word documents

**Key Class:** `KDSDocument`

**Methods:**
- `add_cover_page(title, client, date, author, confidential)` - Cover page
- `add_heading(text, level)` - Headings (1-4)
- `add_paragraph(text, bold, italic)` - Body text
- `add_bullet_list(items)` - Bullet points
- `add_numbered_list(items)` - Numbered list
- `add_table(data, headers, caption)` - Tables with purple headers
- `add_chart(image_path, caption)` - Embedded images
- `add_executive_summary(points)` - Executive summary section
- `add_recommendations(recommendations)` - Recommendations section
- `save(path)` - Save to .docx

**Convenience Functions:**
- `create_memo(to, from_sender, subject, ...)` - Generate memo
- `create_report(title, client, executive_summary, ...)` - Generate report

### 3.4 spreadsheet_engine.py (KDSSpreadsheet)

**Purpose:** Generate brand-compliant Excel workbooks

**Key Class:** `KDSSpreadsheet`

**Methods:**
- `add_cover_sheet(title, client, date, author, version)` - Cover sheet
- `add_data_sheet(name, data, headers, freeze_header)` - Data tables
- `add_summary_sheet(name, metrics)` - Summary metrics
- `add_documentation_sheet(methodology, sources, assumptions)` - Documentation
- `mark_input_cells(sheet_name, cell_ranges)` - Input cell highlighting
- `save(path)` - Save to .xlsx

**Styling:**
- Purple headers with white text
- Alternating row colors
- Frozen header rows
- Auto-adjusted column widths
- Light purple input cells

### 3.5 webapp_engine.py (KDSWebApp, KDSStreamlitApp, KDSReactApp)

**Purpose:** Generate web dashboards in three tiers

**Tier 1 - Static HTML (KDSWebApp):**
- Single self-contained HTML file
- Embedded CSS from KDSTheme
- Embedded JSON data
- Plotly.js charts (CDN)
- Client-side filtering

**Tier 2 - Streamlit (KDSStreamlitApp):**
- Python app with Streamlit
- `.streamlit/config.toml` theme
- `requirements.txt`
- Data files in `data/` directory

**Tier 3 - React (KDSReactApp):**
- Vite + React project scaffold
- Recharts for visualizations
- KDS theme tokens
- Data as JSON import

**Common API:**
```python
app = KDSWebApp("Dashboard Title")
app.set_data(data)
app.add_metric(label, value, delta)
app.add_chart(source, type, x, y, title)
app.add_table(source, title, columns)
app.add_filter(source, column, type)
app.generate("output_path")
```

### 3.6 data_profiler.py

**Purpose:** Analyze datasets and generate quality reports

**Key Function:** `profile_dataset(file_path, sample_size=None)`

**Returns:** `DatasetProfile` with:
- Row/column counts
- Column profiles (dtype, nulls, unique values, statistics)
- Quality issues (duplicates, high nulls, constants)
- Markdown report generation

**Supported Formats:** CSV, Excel (.xlsx/.xls), Parquet, JSON

### 3.7 data_handler.py (ProjectDatabase)

**Purpose:** DuckDB-backed handler for large files (>50MB)

**Key Class:** `ProjectDatabase`

**Methods:**
- `register_file(file_path, table_name)` - Register file as queryable table
- `query(sql)` - Execute SQL query
- `query_df(sql)` - Query to pandas DataFrame
- `list_tables()` - List registered tables
- `describe_table(table_name)` - Get schema
- `export_to_parquet(table_name)` - Export to Parquet
- `export_to_csv(table_name)` - Export to CSV

### 3.8 kds_theme.py (KDSTheme)

**Purpose:** Centralized brand tokens as frozen dataclass

**Exports:**
- `to_css_variables()` - CSS custom properties
- `to_matplotlib_rcparams()` - Matplotlib configuration
- `to_plotly_template()` - Plotly theme
- `to_streamlit_config()` - Streamlit config.toml
- `to_react_theme()` - React/JS theme object
- `get_chart_colors(n)` - Get n colors from palette

**Key Tokens:**
```python
primary = "#7823DC"           # Kearney Purple
background_dark = "#1E1E1E"   # Dark mode background
background_light = "#FFFFFF"  # Light mode background
text_light = "#FFFFFF"        # Text on dark
text_dark = "#333333"         # Text on light
positive = "#D4A5FF"          # Positive indicator (NOT green)
negative = "#FF6F61"          # Negative indicator
font_family = "Inter, Arial, sans-serif"
```

### 3.9 kds_data.py (KDSData)

**Purpose:** Unified data abstraction layer

**Key Class:** `KDSData`

**Creation Methods:**
- `KDSData.from_dict(config)` - From dictionary configuration
- `KDSData.from_yaml(path)` - From YAML file
- `KDSData.from_spec(spec_path)` - From project spec.yaml

**Methods:**
- `query(name)` - Get DataFrame by source name
- `snapshot()` - JSON-serializable snapshot for embedding
- `get_schema(name)` - Column names and types
- `get_unique_values(name, column)` - Unique values for filters
- `get_summary_stats(name)` - Summary statistics
- `export_for_powerbi(name, path)` - Export for Power BI
- `export_for_tableau(name, path)` - Export for Tableau

### 3.10 brand_guard.py

**Purpose:** Programmatic brand compliance validation

**Key Functions:**
- `check_file(path)` - Check single file
- `check_directory(path)` - Check all files in directory
- `check_python_file(path)` - Check Python source code
- `format_violations(violations)` - Format for display

**Checked Rules:**
- **Forbidden colors:** Any green (#00FF00, #2E7D32, #4CAF50, etc.)
- **Emojis:** None allowed
- **Gridlines:** Must be disabled
- **Typography:** Inter/Arial only

**Violation Object:**
```python
@dataclass
class BrandViolation:
    file_path: str
    rule: str           # e.g., "FORBIDDEN_COLOR", "EMOJI"
    message: str
    line_number: int
    severity: str       # "error" or "warning"
```

### 3.11 interview_engine.py

**Purpose:** Structured requirements gathering

**Key Functions:**
- `load_interview_tree(project_type)` - Load interview YAML
- `get_project_type_menu()` - Display project type options
- `parse_project_type_choice(choice)` - Parse user selection
- `create_interview_state(project_type)` - Initialize interview state
- `get_next_question(tree, state)` - Get next question to ask
- `should_ask_question(question, state)` - Check conditional logic
- `answers_to_spec_dict(state)` - Convert answers to spec format

### 3.12 spec_manager.py

**Purpose:** Specification CRUD operations

**Key Functions:**
- `create_spec(data)` - Create new spec
- `load_spec()` - Load current spec
- `save_spec(spec, changelog_entry)` - Save with versioning
- `get_version(spec)` - Get spec version number
- `increment_version(spec)` - Increment version
- `get_section(spec, path)` - Get nested section (dot notation)
- `set_section(spec, path, value)` - Set nested section
- `get_history()` - List all versions
- `load_version(version)` - Load specific version
- `rollback_to_version(version)` - Rollback to version
- `get_changelog()` - Get human-readable changelog
- `analyze_impact(spec, changes)` - Analyze change impact

### 3.13 state_manager.py

**Purpose:** Project state tracking and persistence

**Key Functions:**
- `load_state()` - Load status.json
- `save_state(state)` - Save status.json
- `get_next_task()` - Get next pending task
- `update_task_status(task_id, status, blocked_reason=None)` - Update task
- `add_artifact(path)` - Record generated artifact
- `init_from_plan(project_name, project_type)` - Initialize from plan.md

---

## 4. Agent System

### 4.1 Agent Overview

Agents are specialized personas that Claude adopts when handling specific types of work. Each agent has defined:
- **Role:** What the agent does
- **Activation:** When the agent is invoked
- **Required Context:** Files the agent needs access to
- **Tools:** Which core engines to use
- **Constraints:** Limitations and rules

### 4.2 Available Agents

#### @interviewer
- **Role:** Conduct structured requirements gathering interviews
- **Activation:** `/interview` command
- **Output:** `project_state/spec.yaml`
- **Behavior:**
  - Asks questions one at a time
  - Applies conditional logic
  - Probes for clarity on vague answers
  - Summarizes before saving

#### @planner
- **Role:** Generate execution plans from specifications
- **Activation:** `/plan` command
- **Input:** `spec.yaml`
- **Output:** `plan.md`, `status.json`
- **Behavior:**
  - Analyzes spec requirements
  - Profiles data if applicable
  - Generates phased task list
  - Initializes task tracker

#### @steward
- **Role:** Execute individual tasks from the plan
- **Activation:** `/execute` command
- **Input:** `status.json`, `plan.md`
- **Output:** Files in `outputs/`
- **Behavior:**
  - Loads next pending task
  - Marks task in progress
  - Executes using core engines
  - Records artifacts
  - Updates state

#### @kds-reviewer
- **Role:** Validate brand compliance
- **Activation:** `/review` command
- **Input:** `outputs/**`, `exports/**`
- **Output:** Validation report
- **Behavior:**
  - Runs automated brand_guard checks
  - Performs manual checklist review
  - Reports PASS/FAIL status
  - Lists required fixes

#### @presentation-builder
- **Role:** Generate PowerPoint presentations
- **Activation:** `/export` for presentations, by @steward for presentation tasks
- **Input:** `outputs/charts/**`, `spec.yaml`
- **Output:** `.pptx` files in `exports/`
- **Skills Required:** `kearney-pptx.md`, `kearney-visualization.md`

#### @dashboard_builder
- **Role:** Generate web dashboards
- **Activation:** `/webapp` command, dashboard projects
- **Output:** HTML, Streamlit app, or React scaffold
- **Behavior:**
  - Selects output tier based on audience and data size
  - Uses webapp_engine for generation
  - Validates output for brand compliance
  - Runs launch verification for Streamlit

#### @document-builder
- **Role:** Generate Word documents and Markdown reports
- **Activation:** `/export` for documents, by @steward for report tasks
- **Output:** `.docx` files, `.md` reports
- **Skills Required:** `kearney-docx.md`, `kearney-markdown.md`

#### @data-analyst
- **Role:** Profile datasets and identify data quality issues
- **Activation:** By @steward for data tasks, data exploration requests
- **Output:** Data profiles, quality assessments
- **Tools:** `data_profiler.py`

#### @spec-editor
- **Role:** Modify project specification
- **Activation:** `/edit` command
- **Behavior:**
  - Loads current spec
  - Understands requested changes
  - Analyzes impact on plan
  - Versions and archives old spec

---

## 5. Command System

### 5.1 Core Workflow Commands

| Command | Agent | Description |
|---------|-------|-------------|
| `/interview` | @interviewer | Gather requirements via structured interview |
| `/plan` | @planner | Generate execution plan from spec |
| `/execute` | @steward | Execute next pending task |
| `/review` | @kds-reviewer | Run brand compliance check |
| `/export` | @presentation-builder | Generate final deliverables |

### 5.2 State Management Commands

| Command | Description |
|---------|-------------|
| `/status` | Show current project state and progress |
| `/spec` | View current specification |
| `/edit` | Edit specific parts of specification |
| `/history` | View specification version history |

### 5.3 Output Commands

| Command | Description |
|---------|-------------|
| `/webapp` | Generate web dashboard (HTML/Streamlit/React) |

### 5.4 Session Management Commands

| Command | Description |
|---------|-------------|
| `/compact` | Summarize context to free up space |
| `/reset` | Archive current state and start fresh |
| `/rollback` | Restore from previous archive or history |
| `/init` | Initialize new project from template |
| `/help` | Show all available commands |

### 5.5 Command Definition Schema

Commands are defined in `.claude/commands/{name}.md`:

```markdown
# /command-name

---
name: command-name
description: What the command does
agent: @agent-name (optional)
---

Detailed instructions for the command...

## Usage

\```
/command-name [options]
\```

## Behavior

1. Step one
2. Step two

## Output

What the command produces...
```

---

## 6. Data Model and State

### 6.1 spec.yaml Schema

The specification is the **source of truth** for project requirements:

```yaml
# Meta information
meta:
  project_name: "Sales Analysis"
  project_type: "analytics"
  client: "Acme Corp"
  deadline: "2025-12-31"
  version: 1

# Problem definition
problem:
  business_question: "What factors drive regional sales performance?"
  success_criteria:
    - "Identify top 3 factors by region"
    - "Quantify impact of each factor"

# Type-specific configuration
type_specific:
  # Varies by project_type (modeling, dashboard, presentation, etc.)

# Data sources
data:
  sources:
    - name: "sales"
      type: "csv"
      path: "data/raw/sales.csv"
      keys: ["region", "product"]
      value_cols: ["revenue", "units"]

# Deliverables
deliverables:
  - "Executive summary presentation"
  - "Regional performance charts"
  - "Recommendations document"

# Visualization preferences
visualization:
  format: "png"
  size: "presentation"
  include_insights: true
  insight_depth: "brief"

# Additional notes
notes: "Focus on Q4 data only"
```

### 6.2 plan.md Structure

The execution plan is derived from the specification:

```markdown
# Execution Plan: Sales Analysis

**Generated:** 2025-12-04
**Based on spec version:** 1

## Phase 1: Data Preparation

- [ ] 1.1 Profile sales data source
- [ ] 1.2 Identify data quality issues
- [ ] 1.3 Clean and validate data

## Phase 2: Analysis

- [ ] 2.1 Calculate regional metrics
- [ ] 2.2 Identify performance factors
- [ ] 2.3 Generate insights

## Phase 3: Visualization

- [ ] 3.1 Create regional comparison charts
- [ ] 3.2 Create factor impact visualization

## Phase 4: Documentation

- [ ] 4.1 Generate executive summary
- [ ] 4.2 Create recommendations document

## Phase 5: Review & Export

- [ ] 5.1 Run brand compliance check
- [ ] 5.2 Export final deliverables
```

### 6.3 status.json Schema

```json
{
  "project_name": "Sales Analysis",
  "project_type": "analytics",
  "current_phase": "Phase 2: Analysis",
  "spec_version": 1,
  "tasks": [
    {
      "id": "1.1",
      "description": "Profile sales data source",
      "phase": "Phase 1: Data Preparation",
      "status": "done",
      "completed_at": "2025-12-04T10:30:00"
    },
    {
      "id": "2.1",
      "description": "Calculate regional metrics",
      "phase": "Phase 2: Analysis",
      "status": "in_progress",
      "started_at": "2025-12-04T10:45:00"
    },
    {
      "id": "2.2",
      "description": "Identify performance factors",
      "phase": "Phase 2: Analysis",
      "status": "pending"
    }
  ],
  "artifacts": [
    "outputs/reports/data_profile.md",
    "outputs/charts/regional_comparison.png"
  ],
  "history": [
    {
      "action": "project_created",
      "timestamp": "2025-12-04T10:00:00"
    },
    {
      "action": "plan_generated",
      "timestamp": "2025-12-04T10:15:00"
    }
  ]
}
```

### 6.4 State Flow

```
/interview -> spec.yaml (v1)
                 |
/plan -----------+-----------> plan.md
                 |                 |
                 |                 v
                 |           status.json (tasks: pending)
                 |
/execute --------+-----------> status.json (tasks: in_progress -> done)
                 |                 |
                 |                 v
                 |           outputs/* (artifacts)
                 |
/edit -----------+-----------> spec.yaml (v2)
                 |                 |
                 |                 v
                 |           spec_history/spec_v1.yaml (archived)
                 |
/plan -----------+-----------> plan.md (regenerated)
                                   |
                                   v
                              status.json (tasks updated)
```

---

## 7. Brand and Design System (KDS)

### 7.1 Core Brand Rules (Non-Negotiable)

These rules are programmatically enforced by `brand_guard.py`:

| Rule | Requirement | Enforcement |
|------|-------------|-------------|
| Primary Color | Kearney Purple #7823DC | All accents, highlights |
| Forbidden Colors | NO GREEN ever | Block on detection |
| Typography | Inter (Arial fallback) | weights 400/500/600 |
| Charts | No gridlines | Block if enabled |
| Data Labels | Outside bars/slices | Warning if inside |
| Background | Dark #1E1E1E default | Light #FFFFFF option |
| Emojis | NEVER | Block on detection |

### 7.2 Color Palette

**Approved Colors:**

| Name | Hex | RGB | Usage |
|------|-----|-----|-------|
| Kearney Purple | #7823DC | 120, 35, 220 | Primary accent |
| Dark Background | #1E1E1E | 30, 30, 30 | Chart/slide background |
| Light Background | #FFFFFF | 255, 255, 255 | Print alternative |
| Text Light | #FFFFFF | 255, 255, 255 | Text on dark |
| Text Dark | #333333 | 51, 51, 51 | Text on light |
| Gray 100 | #F5F5F5 | 245, 245, 245 | Light fills |
| Gray 200 | #E0E0E0 | 224, 224, 224 | Dividers |
| Gray 300 | #CCCCCC | 204, 204, 204 | Disabled states |
| Gray 400 | #999999 | 153, 153, 153 | Secondary text |
| Gray 500 | #666666 | 102, 102, 102 | Body text |

**Chart Palette (NO GREEN):**
```python
chart_palette = [
    "#7823DC",  # Primary purple
    "#9B4DCA",  # Light purple
    "#5C1BA8",  # Dark purple
    "#B266FF",  # Bright purple
    "#4A148C",  # Deep purple
    "#CE93D8",  # Pale purple
    "#7B1FA2",  # Purple variant
    "#666666",  # Gray
    "#999999",  # Light gray
    "#333333",  # Dark gray
]
```

**Semantic Colors:**
- **Positive:** #D4A5FF (Light purple - NOT green)
- **Negative:** #FF6F61 (Coral)
- **Warning:** #FFB74D (Amber)
- **Info:** #64B5F6 (Light blue)

### 7.3 Forbidden Colors

Green is **completely forbidden** because it's commonly used for "success" states in other systems. Kearney uses purple for positive indicators.

```yaml
forbidden_colors:
  - "#00FF00"   # Pure Green
  - "#008000"   # Green
  - "#2E7D32"   # Material Green 800
  - "#4CAF50"   # Material Green 500
  - "#66BB6A"   # Material Green 400
  - "#228B22"   # Forest Green
  - "#32CD32"   # Lime Green
  # ... many more shades
```

### 7.4 Typography

```yaml
typography:
  primary_font: "Inter"
  fallback: "Arial"
  type: "sans-serif"

  weights:
    regular: 400
    medium: 500
    semibold: 600

  sizes:
    slide_title: 32pt
    slide_subtitle: 24pt
    slide_body: 20pt
    chart_title: 14pt
    chart_label: 11pt
```

### 7.5 Chart Rules

```yaml
charts:
  default_background: "dark"      # #1E1E1E
  gridlines: false               # NEVER enable

  data_labels:
    position: "outside"          # Outside bars/slices
    font_size: 10
    show_values: true

  spines:
    top: false
    right: false
    left: true
    bottom: true

  legend:
    frame: false
```

### 7.6 Presentation Rules

```yaml
presentations:
  aspect_ratio: "16:9"
  width_inches: 13.333
  height_inches: 7.5
  default_mode: "dark"

  margins:
    left: 0.75"
    right: 0.75"
    top: 0.5"

  title_alignment: "left"
  bullet_style: "filled_circle"
```

---

## 8. Interview System

### 8.1 How Interviews Work

The interview system uses YAML-defined "interview trees" that guide requirements gathering:

1. **Project Type Selection:** User chooses from 8 project types
2. **Tree Loading:** Appropriate interview tree is loaded from `config/interviews/`
3. **Sequential Questions:** Questions asked one at a time
4. **Conditional Logic:** Questions skipped based on previous answers
5. **Follow-up Probes:** Short/vague answers trigger follow-ups
6. **Summary and Confirmation:** Full summary shown before saving
7. **Spec Generation:** Answers converted to `spec.yaml`

### 8.2 Project Types

| Type | Interview File | Description |
|------|---------------|-------------|
| data_engineering | data_engineering.yaml | Pipelines, ETL, ingestion |
| modeling | modeling.yaml | ML/statistical models |
| analytics | analytics.yaml | Analysis, visualization, insights |
| presentation | presentation.yaml | Client-facing slide decks |
| proposal | proposal.yaml | RFP responses, pitches |
| dashboard | dashboard.yaml | Interactive data visualization |
| webapp | webapp.yaml | Web applications, tools |
| research | research.yaml | Market/competitive research |

### 8.3 Interview Tree Schema

```yaml
id: modeling
name: Statistical/ML Modeling
version: "1.0.0"

sections:
  - id: basics
    name: Basic Information
    questions:
      - id: project_name
        prompt: |
          What is this project called?
        type: text
        required: true

      - id: problem_type
        prompt: |
          What type of problem is this?

          1. Classification
          2. Regression
          3. Clustering
        type: choice
        options: [classification, regression, clustering]
        required: true

      - id: target_variable
        prompt: What is the target variable?
        type: text
        required: true
        condition: "problem_type not in ['clustering']"
        follow_up:
          condition: "len(answer) < 20"
          prompt: "Can you describe this variable in more detail?"
```

### 8.4 Question Types

| Type | User Input | Parsed Value |
|------|-----------|--------------|
| text | Free text | String |
| choice | Number or name | Selected option string |
| multi | Comma-separated numbers | List of selected options |
| boolean | yes/no/y/n | True/False |
| number | Numeric value | int or float |
| date | Date string | String |
| list | Comma-separated | List of strings |
| file | Path | String path |

### 8.5 Conditional Logic

Questions can have conditions based on previous answers:

```yaml
condition: "problem_type == 'classification'"
condition: "auth_required == True"
condition: "'presentation' in deliverables"
condition: "interpretability_audience in ['regulators', 'all']"
```

### 8.6 Follow-up Probes

Short or vague answers can trigger follow-up questions:

```yaml
follow_up:
  condition: "len(answer) < 50"
  prompt: |
    Can you elaborate? What decision will stakeholders make
    based on this model's predictions?
```

---

## 9. Skills System

### 9.1 What Skills Are

Skills are best-practice documentation files that agents must read before creating specific output types. They provide detailed guidance beyond what's in CLAUDE.md.

### 9.2 Available Skills

| Skill File | Output Types | Key Content |
|------------|--------------|-------------|
| kearney-visualization.md | PNG, SVG charts | Chart type selection, axis guidelines, label placement |
| kearney-pptx.md | PowerPoint | Slide structure, action titles, layout rules |
| kearney-docx.md | Word documents | Document types, heading hierarchy, formatting |
| kearney-xlsx.md | Excel | Sheet structure, cell styling, formulas |
| kearney-markdown.md | Markdown reports | Structure, tables, code blocks |
| kearney-webapp.md | Web dashboards | Tier selection, component layout, responsive design |

### 9.3 Skill Usage Workflow

Before creating any deliverable:

```
1. Identify output type (pptx, docx, xlsx, png, html)
2. Read: config/skills/kearney-{type}.md
3. Apply skill best practices
4. Use appropriate core/ engine
5. Run brand_guard.py validation
6. Save to correct location
```

### 9.4 Skill File Example (kearney-visualization.md)

```markdown
# Kearney Visualization Skill

## Kearney Brand Requirements (Non-Negotiable)

- Primary color: #7823DC (Kearney Purple)
- FORBIDDEN: Green - never use
- Background: #1E1E1E (dark mode default)
- NO gridlines on charts
- Data labels OUTSIDE bars/slices
- NO emojis

## Chart Type Selection

| Data Story | Chart Type |
|------------|------------|
| Comparison | Horizontal bar |
| Change over time | Line chart |
| Part-to-whole | Pie (max 5 slices) |
| Correlation | Scatter plot |

## Quality Checklist

- [ ] No gridlines visible
- [ ] No green colors used
- [ ] Data labels outside bars
- [ ] Title states the insight
- [ ] Kearney Purple used for emphasis
```

---

## 10. Current Capabilities

### 10.1 Output Formats

| Format | Engine | Features |
|--------|--------|----------|
| **PNG/SVG Charts** | chart_engine.py | Bar, line, pie, scatter; dark mode; no gridlines |
| **PowerPoint (.pptx)** | slide_engine.py | Title, content, chart, table, two-column slides |
| **Word (.docx)** | document_engine.py | Reports, memos, proposals; tables; embedded charts |
| **Excel (.xlsx)** | spreadsheet_engine.py | Data tables, cover sheets, documentation |
| **Static HTML** | webapp_engine.py | Self-contained dashboards with Plotly.js |
| **Streamlit App** | webapp_engine.py | Interactive Python dashboard |
| **React App** | webapp_engine.py | Vite scaffold with Recharts |
| **Markdown Reports** | (manual) | Data profiles, analysis summaries |

### 10.2 Project Type Support

| Project Type | Typical Outputs | Key Capabilities |
|--------------|-----------------|------------------|
| Analytics | Charts, reports, presentations | Data profiling, metric calculation, visualization |
| Modeling | Model artifacts, validation reports, presentations | Feature engineering, validation, interpretability |
| Dashboard | HTML, Streamlit, React apps | Metrics, charts, tables, filters |
| Presentation | PowerPoint decks | Slide generation, chart embedding |
| Proposal | Word documents | Structured proposals, action plans |
| Research | Markdown reports | Synthesis, analysis documentation |
| Data Engineering | Documentation, specifications | Pipeline design, ETL documentation |
| Web App | HTML, Streamlit, React | Interactive tools, prototypes |

### 10.3 Data Handling

- **Small files (<50MB):** Pandas via data_profiler.py
- **Large files (>50MB):** DuckDB via data_handler.py
- **Supported formats:** CSV, Excel, Parquet, JSON
- **Profiling:** Automatic schema detection, quality issue identification
- **Export:** Power BI and Tableau compatible formats

### 10.4 Brand Compliance

- **Automated validation:** brand_guard.py checks all outputs
- **Pre-commit hooks:** Block commits with violations
- **Agent integration:** Agents validate before saving
- **Severity levels:** Errors (block), Warnings (inform)

---

## 11. Known Limitations and Pain Points

### 11.1 Technical Limitations

| Limitation | Description | Impact |
|------------|-------------|--------|
| **Single-session state** | State persists via files, not memory | Must reload state each session |
| **No real-time data** | Data loaded at execution time | Dashboards are static snapshots |
| **Font embedding** | Inter font may not be installed | Falls back to Arial |
| **Large file memory** | Pandas loads entire files | Need DuckDB for >50MB |
| **Symlink requirements** | Windows needs admin for junctions | Setup friction |

### 11.2 User Experience Pain Points

| Pain Point | Description | Current Workaround |
|------------|-------------|-------------------|
| **Long interviews** | Many questions for complex projects | Conditional logic reduces questions |
| **Plan regeneration** | Spec changes require re-planning | Manual task preservation |
| **Context limits** | Long sessions hit context limits | `/compact` command |
| **Error recovery** | Crashed sessions lose progress | State files preserve progress |
| **Visualization customization** | Limited chart type options | Use core engines directly |

### 11.3 Integration Gaps

| Gap | Description | Desired State |
|-----|-------------|---------------|
| **No CI/CD** | Manual deployment | Automated testing and deployment |
| **No external APIs** | Can't fetch live data | API integration for real-time data |
| **No collaborative editing** | Single-user projects | Team collaboration support |
| **No version control integration** | Manual git operations | Automated commit/push |
| **Limited BI tool export** | Basic CSV export | Native Power BI / Tableau connectors |

### 11.4 Content Gaps

| Gap | Description |
|-----|-------------|
| **No ML model training** | Documentation only, no actual training |
| **No database connections** | File-based only |
| **Limited animation** | Static charts and slides |
| **No video generation** | Presentations are static |

---

## 12. Technical Stack

### 12.1 Core Technologies

| Technology | Version | Purpose |
|------------|---------|---------|
| **Python** | 3.10+ | Core execution engine |
| **Claude Code** | Latest | LLM orchestration |
| **Git** | Any recent | Version control |

### 12.2 Python Dependencies

```
# Data Processing
pandas>=2.0.0
numpy>=1.24.0
pyyaml>=6.0

# Visualization
matplotlib>=3.7.0
seaborn>=0.12.0

# Document Generation
python-pptx>=0.6.21
python-docx>=0.8.11
openpyxl>=3.1.0

# Large File Handling (optional)
duckdb>=0.9.0

# Web Apps (optional)
streamlit>=1.28.0
plotly>=5.17.0

# Testing
pytest>=7.0.0
pytest-cov>=4.0.0
```

### 12.3 Claude Code Integration

KACA integrates with Claude Code via:

1. **CLAUDE.md:** System prompt defining behavior, constraints, and workflows
2. **.claude/commands/:** Slash command definitions
3. **.claude/agents/:** Agent persona definitions
4. **.claude/settings.json:** Permissions and hooks configuration

### 12.4 File I/O Safety

All file operations use `safe_write_text()` from `kds_utils.py`:

```python
def safe_write_text(path, content, encoding="utf-8"):
    """
    Write text with safe encoding.
    - Removes surrogate pairs
    - Strips emojis (brand compliance)
    - Creates parent directories
    """
```

---

## 13. Strategic Context

### 13.1 Target Users

**Primary Persona: Kearney Consultant**
- Has domain expertise, limited coding skills
- Needs production-quality deliverables quickly
- Works under tight deadlines
- Must adhere to brand guidelines
- Uses Claude Desktop as primary interface

**Secondary Persona: Internal Developer**
- Builds tools and prototypes for clients
- Has coding skills but needs brand compliance
- Creates reusable templates and components

### 13.2 Use Cases

| Use Case | Description | Key Outputs |
|----------|-------------|-------------|
| **Client Presentation** | Create branded slide deck from analysis | PowerPoint |
| **Executive Dashboard** | Build KPI dashboard for leadership | HTML/Streamlit |
| **Data Analysis** | Profile data and generate insights | Charts, reports |
| **Proposal Development** | Structure and draft proposal content | Word document |
| **Model Documentation** | Document ML model for stakeholders | Report, presentation |
| **Research Synthesis** | Compile research findings | Markdown, presentation |

### 13.3 Competitive Positioning

**vs. Generic AI Coding Assistants:**
- Brand compliance is programmatic, not advisory
- Interview system captures complete requirements
- State management enables session continuity
- Output engines guarantee consistent quality

**vs. Traditional BI Tools:**
- Faster from requirements to deliverables
- Natural language specification
- Multiple output format support
- No licensing costs

**vs. Manual Creation:**
- Hours to minutes for standard deliverables
- Consistent brand application
- Reduced errors and rework
- Repeatable workflows

### 13.4 Success Metrics (Hypothetical)

| Metric | Description |
|--------|-------------|
| Time to First Output | Minutes from project start to first deliverable |
| Brand Compliance Rate | % of outputs passing automated review |
| Session Resumption Success | % of interrupted sessions successfully resumed |
| Output Quality Score | User satisfaction with generated deliverables |
| Rework Reduction | Decrease in manual post-processing needed |

---

## 14. Research Guidelines

### 14.1 Valuable Enhancement Areas

When researching improvements to KACA, consider these high-value areas:

#### Architecture & Performance
- Session state management across context limits
- Incremental plan updates (vs. full regeneration)
- Parallel task execution
- Caching strategies for data and outputs

#### User Experience
- Interview flow optimization (fewer questions, better defaults)
- Progress visualization and feedback
- Error recovery and debugging assistance
- Onboarding and help system improvements

#### Output Quality
- Additional chart types and customization
- Advanced presentation layouts
- Richer document formatting
- Animation and interactivity options

#### Integration & Ecosystem
- CI/CD pipeline integration
- Database connectivity
- Real-time data sources
- Team collaboration features
- Version control automation

#### Intelligence & Automation
- Smart defaults based on data analysis
- Automatic insight generation
- Layout optimization
- Content suggestions

### 14.2 Research Questions

Consider researching answers to these questions:

1. **Architecture:** How do other AI coding assistants handle long-running sessions and state persistence?

2. **Interview Design:** What are best practices for requirements elicitation in conversational AI?

3. **Brand Compliance:** How can programmatic brand enforcement be made more comprehensive and less restrictive?

4. **Output Generation:** What are the latest techniques for AI-assisted document and presentation generation?

5. **Data Integration:** How can KACA better connect to enterprise data sources while maintaining security?

6. **Collaboration:** What patterns exist for multi-user AI-assisted project workflows?

7. **Testing & Quality:** How can output quality be automatically validated beyond brand compliance?

8. **Extensibility:** What plugin or extension architectures would allow custom engines and integrations?

### 14.3 What Would Be Most Valuable

Recommendations in these categories would be most impactful:

| Category | Examples |
|----------|----------|
| **Quick Wins** | Small changes with immediate UX improvement |
| **Architecture Patterns** | Proven approaches from similar systems |
| **New Capabilities** | Features that expand what KACA can produce |
| **Integration Options** | Ways to connect with enterprise tools |
| **Best Practices** | Industry standards KACA should adopt |
| **Competitive Features** | Capabilities competitors have that KACA lacks |

### 14.4 Constraints to Consider

Any recommendations should account for these constraints:

- **Brand compliance is non-negotiable:** All outputs must pass brand_guard
- **Users have limited coding skills:** Solutions must be accessible
- **Claude Code is the interface:** Recommendations must work within Claude's capabilities
- **State persistence is file-based:** No external databases currently
- **Python is the execution environment:** Core engines are Python-based
- **No green colors ever:** This is a strict brand requirement

---

## Appendix A: Quick Reference

### Command Cheat Sheet

```
WORKFLOW:       /interview -> /plan -> /execute -> /review -> /export
STATE:          /status, /spec, /edit, /history
OUTPUT:         /webapp
SESSION:        /compact, /reset, /rollback
HELP:           /help
```

### File Locations

```
Requirements:   project_state/spec.yaml
Plan:           project_state/plan.md
State:          project_state/status.json
Input Data:     data/raw/
Intermediate:   outputs/
Final:          exports/
```

### Brand Colors

```
Primary:        #7823DC (Kearney Purple)
Background:     #1E1E1E (dark), #FFFFFF (light)
Text:           #FFFFFF (on dark), #333333 (on light)
FORBIDDEN:      Any green (#00FF00, #4CAF50, etc.)
```

### Engine Imports

```python
from core.chart_engine import KDSChart
from core.slide_engine import KDSPresentation
from core.document_engine import KDSDocument
from core.spreadsheet_engine import KDSSpreadsheet
from core.webapp_engine import KDSWebApp, KDSStreamlitApp, KDSReactApp
from core.kds_theme import KDSTheme
from core.kds_data import KDSData
from core.brand_guard import check_file, check_directory
from core.data_profiler import profile_dataset
```

---

## Appendix B: Version History

| Version | Date | Changes |
|---------|------|---------|
| 2.0.0 | 2025-12 | Living requirements, webapp engine, state management |
| 1.0.0 | 2025-11 | Initial release with core engines |

---

*This guide was created to enable AI research partners to understand KACA comprehensively and provide meaningful enhancement recommendations.*

*Kearney Digital & Analytics*
