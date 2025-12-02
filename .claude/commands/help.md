# /help - Show Available Commands

Display help information and available commands.

## Usage

```
/help
```

## Output

```
KEARNEY AI CODING ASSISTANT v2.0
=================================

Available Commands:

  /interview  Gather requirements via structured interview
  /edit       Edit specific parts of specification
  /spec       View current specification
  /history    View specification version history
  /plan       Generate execution plan from spec
  /execute    Execute the next pending task
  /status     Show current project state and progress
  /review     Run brand compliance check on outputs
  /export     Generate final deliverables
  /help       Show this help message

Session Management:

  /compact    Summarize context to free up space
  /reset      Archive current state and start fresh
  /rollback   Restore from previous archive

Typical Workflow:

  1. /interview  - Answer requirement questions
  2. /plan       - Generate and approve plan
  3. /execute    - Work through tasks (repeat)
  4. /status     - Check progress
  5. /review     - Validate brand compliance
  6. /export     - Generate deliverables

At any point:
  - /edit       - Modify requirements
  - /spec       - View current requirements
  - /history    - View/rollback versions

Project Types:

  data_engineering   - Data pipelines, ETL, ingestion
  modeling           - Statistical/ML models
  analytics          - Analysis, visualization, insights
  presentation       - Client-facing slide decks
  proposal           - RFP responses, pitches
  dashboard          - Interactive data visualization
  webapp             - Web applications, tools, prototypes
  research           - Market research, competitive analysis

Brand Rules (Enforced Automatically):

  - Primary Color: Kearney Purple (#7823DC)
  - Forbidden: Green colors (any shade)
  - Typography: Inter font (Arial fallback)
  - Charts: No gridlines, dark mode default
  - Content: No emojis allowed

Documentation:

  docs/GETTING_STARTED.md    - Quick start guide
  docs/TROUBLESHOOTING.md    - Common issues and fixes
  docs/QUICK_REFERENCE.md    - Command quick reference
```

## Context-Aware Help

If a project exists, also show:

```
CURRENT PROJECT
---------------
Project: {project_name}
Type: {project_type}
Spec Version: {version}
Status: {current_phase}
Progress: {done}/{total} tasks

Suggested next command: /{suggested}
```
