# Command Reference

Complete reference for all slash commands in the Kearney AI Coding Assistant.

## Command Overview

| Command | Purpose | Prerequisites |
|---------|---------|---------------|
| `/init` | Initialize new project | None |
| `/interview` | Gather requirements | Project initialized |
| `/plan` | Generate execution plan | Intake complete |
| `/execute` | Run next task | Plan approved |
| `/status` | Show current state | Project initialized |
| `/review` | Brand compliance check | Outputs exist |
| `/export` | Generate deliverables | Review passed |
| `/help` | Show help | None |

---

## /init

Initialize a new project from a template.

### Usage

```
/init
```

### Behavior

1. Prompts for project name
2. Shows available templates:
   - `analytics` - Data analysis with charts
   - `presentation` - Slide deck creation
   - `webapp` - Web application scaffolding
3. Creates `project_state/status.json`
4. Sets up `outputs/` directory structure

### Output

```
Project initialized: my-project
Template: analytics
Status file: project_state/status.json

Next step: /interview
```

### Files Created

- `project_state/status.json` - Project state
- `outputs/` - Output directory (empty)

---

## /interview

Gather project requirements through structured questions.

### Usage

```
/interview
```

### Behavior

1. Loads intake template based on project type
2. Asks questions sequentially:
   - Required questions must be answered
   - Optional questions can be skipped
3. Validates responses
4. Saves requirements to YAML

### Question Types

| Type | Description | Example |
|------|-------------|---------|
| `text` | Free-form text | Project description |
| `choice` | Single selection | Audience type |
| `multi_choice` | Multiple selections | Deliverable types |
| `file_path` | Path to data file | CSV location |
| `number` | Numeric value | Slide count |

### Output

```
Requirements captured:
- Project Name: Q4 Revenue Analysis
- Audience: Executive Leadership
- Data Source: data/revenue.csv
- Deliverables: Charts, Report

Saved to: project_state/requirements.yaml

Next step: /plan
```

### Files Created

- `project_state/requirements.yaml` - Captured requirements

---

## /plan

Generate an execution plan from requirements.

### Usage

```
/plan
```

### Behavior

1. Loads project state and requirements
2. Invokes Planner Agent
3. Generates phases and tasks based on:
   - Project template defaults
   - Captured requirements
   - Available data sources
4. Presents plan for approval

### Plan Structure

```
EXECUTION PLAN: Q4 Revenue Analysis
====================================

Phase 1: Data Preparation
  [ ] Profile dataset
  [ ] Assess data quality
  [ ] Clean and transform data

Phase 2: Analysis
  [ ] Generate revenue charts
  [ ] Calculate key metrics
  [ ] Identify trends

Phase 3: Deliverables
  [ ] Create summary report
  [ ] Compile chart package

Phase 4: Review
  [ ] Run brand compliance check
  [ ] Final quality review
```

### Approval

After viewing the plan:
- Say "approve" or "yes" to proceed
- Say "modify" to request changes
- Say "reject" to start over

### Files Modified

- `project_state/status.json` - Updated with plan

---

## /execute

Execute the next pending task in the plan.

### Usage

```
/execute
```

### Behavior

1. Loads current state
2. Finds next pending task
3. Invokes appropriate agent:
   - Data tasks: Data Analyst Agent
   - Presentation tasks: Presentation Builder Agent
   - Review tasks: KDS Reviewer Agent
4. Executes task using core modules
5. Updates task status
6. Shows progress

### Task States

| State | Meaning |
|-------|---------|
| `pending` | Not started |
| `in_progress` | Currently executing |
| `completed` | Successfully finished |
| `blocked` | Waiting on dependency |

### Output

```
Executing: Generate revenue charts

Using: Data Analyst Agent
Data source: data/revenue.csv

Creating charts...
- Bar chart: outputs/charts/revenue_by_region.png
- Line chart: outputs/charts/revenue_trend.png
- Pie chart: outputs/charts/revenue_distribution.png

Task completed!
Progress: 3/8 tasks done

Next step: /execute (or /status)
```

### Files Modified

- `project_state/status.json` - Task status updated
- `outputs/` - New deliverables

---

## /status

Display current project state and progress.

### Usage

```
/status
```

### Behavior

1. Loads project state
2. Calculates progress metrics
3. Shows current phase and tasks
4. Suggests next action

### Output

```
PROJECT STATUS: Q4 Revenue Analysis
====================================

Template: analytics
Phase: 2 of 4 (Analysis)
Progress: 5/12 tasks (42%)

Completed:
  [x] Profile dataset
  [x] Assess data quality
  [x] Clean and transform data
  [x] Generate revenue charts
  [x] Calculate key metrics

In Progress:
  [>] Identify trends

Pending:
  [ ] Create summary report
  [ ] Compile chart package
  [ ] Run brand compliance check
  [ ] Final quality review

Outputs generated: 4 files
Last updated: 2024-01-15 14:30

Suggested next: /execute
```

---

## /review

Run brand compliance check on all outputs.

### Usage

```
/review
```

### Behavior

1. Scans `outputs/` directory
2. Checks each file against brand rules:
   - Color validation (no green, proper purple)
   - Font verification (Inter family)
   - Content check (no emojis)
   - Chart styling (no gridlines)
3. Reports violations
4. Provides fix suggestions

### Output (Pass)

```
BRAND COMPLIANCE REVIEW
========================

Scanning: outputs/

Checked 8 files:
  [OK] charts/revenue_by_region.png
  [OK] charts/revenue_trend.png
  [OK] charts/revenue_distribution.png
  [OK] reports/analysis.md
  [OK] presentations/summary.pptx

Result: ALL CHECKS PASSED

Ready for: /export
```

### Output (Violations)

```
BRAND COMPLIANCE REVIEW
========================

Scanning: outputs/

Checked 8 files:
  [OK] charts/revenue_by_region.png
  [FAIL] charts/comparison.png
    - Forbidden color detected: #00FF00 (green)
    - Line 0: gridlines visible
  [OK] reports/analysis.md

Result: 1 VIOLATION(s) FOUND

Fixes needed:
1. charts/comparison.png
   - Replace green (#00FF00) with Kearney Purple (#7823DC)
   - Remove gridlines from chart

Run /execute to regenerate, then /review again.
```

---

## /export

Generate final deliverables package.

### Usage

```
/export
```

### Behavior

1. Verifies review passed
2. Collects all outputs
3. Creates export package:
   - Copies files to export directory
   - Generates manifest
   - Creates ZIP archive (optional)

### Output

```
EXPORT DELIVERABLES
====================

Project: Q4 Revenue Analysis
Export location: exports/q4-revenue-analysis/

Contents:
  charts/
    revenue_by_region.png (245 KB)
    revenue_trend.png (198 KB)
    revenue_distribution.png (167 KB)
  reports/
    analysis.md (12 KB)
  presentations/
    summary.pptx (1.2 MB)

Total: 5 files, 1.8 MB

Manifest: exports/q4-revenue-analysis/manifest.yaml

Export complete!
```

---

## /help

Display help and available commands.

### Usage

```
/help
```

### Output

```
KEARNEY AI CODING ASSISTANT v2.0
=================================

Available Commands:

  /init      Initialize a new project from template
  /interview    Gather project requirements interactively
  /plan      Generate execution plan from requirements
  /execute   Execute the next pending task
  /status    Show current project state and progress
  /review    Run brand compliance check on outputs
  /export    Generate final deliverables
  /help      Show this help message

Typical Workflow:

  1. /init      - Start new project
  2. /interview    - Answer requirement questions
  3. /plan      - Generate and approve plan
  4. /execute   - Work through tasks (repeat)
  5. /review    - Validate brand compliance
  6. /export    - Generate deliverables

Brand Rules (Enforced Automatically):

  - Primary Color: Kearney Purple (#7823DC)
  - Forbidden: Green colors (any shade)
  - Typography: Inter font (Arial fallback)
  - Charts: No gridlines, dark mode default
  - Content: No emojis allowed
```

---

## Error Handling

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| "No project initialized" | Running command before init | Run `/init` first |
| "Intake not complete" | Missing requirements | Run `/interview` |
| "Plan not approved" | Plan not confirmed | Approve plan in `/plan` |
| "Review has violations" | Brand compliance failed | Fix issues, run `/review` |
| "File not found" | Missing data source | Check file path in requirements |

### Recovery

If stuck, you can:

1. Check status: `/status`
2. Review state file: `project_state/status.json`
3. Reset project: Delete `project_state/` and run `/init`
