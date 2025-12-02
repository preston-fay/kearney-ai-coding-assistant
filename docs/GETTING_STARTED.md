# Getting Started with Kearney AI Coding Assistant

This guide will help you set up and start using the Kearney AI Coding Assistant in under 10 minutes.

## Prerequisites

- Python 3.10 or higher
- Claude Desktop application
- Git (for cloning the repository)

## Quick Setup

### Option 1: Run Prerequisite Check First

Before setting up, verify your environment is ready:

```bash
python3 core/prereq_checker.py
```

This checks for:
- Python version (3.10+)
- Git installation
- Claude Desktop
- Required Python packages
- Template presence and version

### Option 2: Bootstrap Setup

### Windows

1. Download or clone this repository
2. Double-click `bootstrap/setup_windows.bat`
3. Wait for the "SUCCESS!" message
4. Open Claude Desktop

### macOS / Linux

1. Download or clone this repository
2. Open Terminal in the project directory
3. Run: `bash bootstrap/setup_mac.sh`
4. Wait for the "SUCCESS!" message
5. Open Claude Desktop

## First Project

### Step 1: Open in Claude Desktop

1. Launch Claude Desktop
2. Go to **File > Open Folder**
3. Select the Kearney AI Coding Assistant directory
4. You should see the project files in the sidebar

### Step 2: Initialize Your Project

Type in the chat:

```
/init
```

Claude will ask you to choose a template:
- **analytics** - Data analysis with charts and reports
- **presentation** - Slide deck creation
- **webapp** - Web application scaffolding

### Step 3: Answer Intake Questions

After initialization, run:

```
/interview
```

Claude will ask questions about your project:
- Project name and description
- Audience and deliverables
- Data sources (if applicable)
- Timeline considerations

### Step 4: Generate Your Plan

Once intake is complete:

```
/plan
```

Claude will create a detailed execution plan with phases and tasks.

### Step 5: Execute Tasks

Work through your plan:

```
/execute
```

This advances to the next pending task. Repeat until all tasks are complete.

### Step 6: Review and Export

When finished:

```
/review
```

This runs brand compliance checks on all outputs.

Then export your deliverables:

```
/export
```

## Command Reference

### Core Workflow Commands

| Command | Description |
|---------|-------------|
| `/init` | Start a new project |
| `/interview` | Gather requirements via structured interview |
| `/plan` | Generate execution plan |
| `/execute` | Run next task |
| `/status` | Check progress |
| `/review` | Brand compliance check |
| `/export` | Generate deliverables |
| `/help` | Show help |

### Session Management Commands

| Command | Description |
|---------|-------------|
| `/compact` | Summarize and archive old context to free up space |
| `/reset` | Archive current state and start fresh |
| `/rollback` | Restore project state from archive or history |

### Additional Commands

| Command | Description |
|---------|-------------|
| `/edit` | Edit specific parts of specification |
| `/spec` | View current specification |
| `/history` | View specification version history |

## Brand Guidelines (Enforced Automatically)

The kit automatically enforces Kearney brand standards:

- **Primary Color**: Kearney Purple (#7823DC)
- **Forbidden**: Green colors (any shade)
- **Typography**: Inter font (Arial fallback)
- **Charts**: No gridlines, dark mode default
- **Content**: No emojis allowed

## Project Structure

After initialization, your project will have:

```
project_state/
  spec.yaml           # Living requirements (source of truth)
  plan.md             # Generated execution plan
  status.json         # Project state (enables resume)
  spec_history/       # Version history
  logs/
    commands/         # Command execution history
    exports/          # Export history
    sessions/         # Session logs

data/
  raw/               # Source data files (never modified)
  processed/         # Cleaned, transformed data
  external/          # Reference data, lookups
  project.duckdb     # DuckDB database for large files

outputs/
  charts/            # Generated visualizations
  reports/           # Analysis documents

exports/             # Final client-ready deliverables
```

## Working with Large Data Files

For files larger than 50MB, use the DuckDB integration:

```python
from core.data_handler import ProjectDatabase

db = ProjectDatabase(Path("."))
db.register_file("data/raw/large_file.csv")
result = db.query_df("SELECT region, SUM(sales) FROM large_file GROUP BY region")
```

| File Size | Recommended Approach |
|-----------|---------------------|
| < 50MB | Load directly with pandas |
| 50-500MB | Use DuckDB via core/data_handler.py |
| > 500MB | Query in DuckDB, never load fully |

## Resuming Work

The kit automatically saves your progress. If you close Claude Desktop and return later:

1. Open the same folder
2. Run `/status` to see where you left off
3. Continue with `/execute`

## Brand Override for Client Projects

For client-branded deliverables, create a `config/brand_override.yaml`:

```yaml
enabled: true
brand_name: "Client Name"

colors:
  primary: "#0066CC"  # Client primary color
  secondary: "#FF6600"

typography:
  primary: "Helvetica Neue"
  fallback: "Helvetica"
```

Note: Some rules are always enforced regardless of override:
- No emojis
- No gridlines
- Data labels outside bars/slices

## Error Recovery

If something goes wrong:

| Problem | Solution |
|---------|----------|
| Corrupted state | Run `/reset` to archive and start fresh |
| Wrong direction | Run `/rollback` to restore from archive |
| Long session | Run `/compact` to free up context |
| Brand issues | Run `/review` to check compliance |

## Quality Control

Before exporting, run `/review` to check:
- Brand color compliance (no forbidden colors)
- Emoji detection
- Gridline detection in charts
- PII detection in outputs
- Raw data exposure check

## Next Steps

- Read the [Consultant Guide](CONSULTANT_GUIDE.md) for detailed workflows
- See [Command Reference](COMMAND_REFERENCE.md) for all options
- Check [Troubleshooting](TROUBLESHOOTING.md) if you encounter issues

## Getting Help

- Type `/help` for command overview
- Teams Channel: #Claude-Code-Help
- Office Hours: Wednesdays 2-3pm ET
- Email: da-claude@kearney.com
