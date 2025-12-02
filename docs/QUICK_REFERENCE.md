# Kearney AI Coding Assistant - Quick Reference

```
+---------------------------------------------------------------------+
|         KEARNEY AI CODING ASSISTANT - QUICK REFERENCE               |
+---------------------------------------------------------------------+

  CREATE NEW PROJECT
  ------------------
  python ~/kaca-template/scaffold.py my-project-name
  cd my-project-name
  Open folder in Claude Desktop (File -> Open Folder)

+---------------------------------------------------------------------+

  THE STANDARD WORKFLOW
  ---------------------

    +------------------+
    |  1. /project:    |  Define what you're building
    |     interview    |  (requirements, deliverables)
    +--------+---------+
             |
             v
    +------------------+
    |  2. /project:    |  Get phased execution plan
    |     plan         |
    +--------+---------+
             |
             v
    +------------------+
    |  3. /project:    |  Build it (repeat until done)
    |     execute      |
    +--------+---------+
             |
             v
    +------------------+
    |  4. /project:    |  Check brand compliance
    |     review       |
    +--------+---------+
             |
             v
    +------------------+
    |  5. /project:    |  Get final deliverables
    |     export       |
    +------------------+

+---------------------------------------------------------------------+

  OTHER USEFUL COMMANDS
  ---------------------
  /status   Where am I? What's next?
  /edit     Change requirements
  /spec     View current spec
  /history  View spec versions
  /compact          Free up context (long sessions)
  /reset            Start over (archives current state)
  /rollback         Restore from archive
  /help     Show all commands

+---------------------------------------------------------------------+

  YOUR PROJECT FOLDERS
  --------------------
  data/raw/        <- Put source files here
  data/processed/  <- Cleaned data goes here
  outputs/         <- Charts and reports appear here
  exports/         <- Final deliverables here

+---------------------------------------------------------------------+

  PROJECT TYPES
  -------------
  1. Data Engineering    5. Proposal Content
  2. ML/Stats Modeling   6. Dashboard
  3. Analytics Asset     7. Web Application
  4. Presentation/Deck   8. Research/Synthesis

+---------------------------------------------------------------------+

  BRAND RULES (Enforced Automatically)
  ------------------------------------
  PRIMARY COLOR: #7823DC (Kearney Purple)
  FORBIDDEN: Any green colors
  TYPOGRAPHY: Inter (Arial fallback)
  CHARTS: No gridlines, dark mode default
  CONTENT: No emojis

+---------------------------------------------------------------------+

  RECOVERY COMMANDS
  -----------------
  Problem             | Solution
  --------------------|------------------------------------------
  Corrupted state     | /reset (archives and starts fresh)
  Wrong direction     | /rollback (restore from archive)
  Long session        | /compact (summarize and free context)
  Brand violations    | /review (check compliance)

+---------------------------------------------------------------------+

  DATA FILE GUIDELINES
  --------------------
  < 50MB      | Load directly with pandas
  50-500MB    | Use DuckDB via core/data_handler.py
  > 500MB     | Query in DuckDB, never load fully

+---------------------------------------------------------------------+

  NEED HELP?
  ----------
  Teams: #Claude-Code-Help
  Office Hours: Wednesdays 2-3pm ET
  Email: da-claude@kearney.com

+---------------------------------------------------------------------+
```

## Command Quick Reference

### Workflow Commands

| Command | Purpose |
|---------|---------|
| `/init` | Initialize new project from template |
| `/interview` | Gather requirements via structured interview |
| `/plan` | Generate execution plan from spec |
| `/execute` | Execute next pending task |
| `/status` | Show current project state |
| `/review` | Run brand compliance check |
| `/export` | Generate final deliverables |

### State Management

| Command | Purpose |
|---------|---------|
| `/edit` | Edit specific parts of specification |
| `/spec` | View current specification |
| `/history` | View specification version history |

### Session Management

| Command | Purpose |
|---------|---------|
| `/compact` | Summarize and archive old context |
| `/reset` | Archive current state and start fresh |
| `/rollback` | Restore project state from archive |

## Color Palette

| Color | Hex Code | Usage |
|-------|----------|-------|
| Kearney Purple | `#7823DC` | Primary accent |
| Dark Background | `#1E1E1E` | Default background |
| White | `#FFFFFF` | Light background |
| Text Primary | `#333333` | Main text |
| Text Secondary | `#666666` | Secondary text |
| Text Muted | `#999999` | Muted text |
| Border | `#CCCCCC` | Borders, dividers |

## Forbidden Colors

Never use any shade of green:
- `#00FF00` - Pure green
- `#2E7D32` - Material green
- `#4CAF50` - Material green 500
- `#228B22` - Forest green
- Any green variant

## File Size Guidelines

| Size | Approach |
|------|----------|
| < 50MB | `pd.read_csv()` directly |
| 50-500MB | Use `ProjectDatabase` from `core/data_handler.py` |
| > 500MB | Query in DuckDB, never load fully |

```python
# Large file example
from core.data_handler import ProjectDatabase
from pathlib import Path

db = ProjectDatabase(Path("."))
db.register_file("data/raw/large_file.csv")
result = db.query_df("SELECT region, SUM(sales) FROM large_file GROUP BY region")
```

## Quality Control Checks

Before export, `/review` checks:

1. **Brand Colors** - No forbidden colors
2. **Emojis** - No emojis in content
3. **Gridlines** - No gridlines in charts
4. **PII** - No emails, phone numbers, SSNs
5. **Raw Data** - No raw data in exports

## Support

- **Teams**: #Claude-Code-Help
- **Office Hours**: Wednesdays 2-3pm ET
- **Email**: da-claude@kearney.com
