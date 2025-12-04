# Kearney AI Coding Assistant (KACA) v3.2

**AI-powered project scaffolding with brand compliance for Kearney consultants.**

KACA helps you build data analytics projects, dashboards, presentations, and reports - all automatically styled to Kearney brand guidelines.

---

## Quick Start (5 minutes)

### Prerequisites

- Python 3.10+
- Claude Code (Claude Desktop with code execution)
- Git

### Step 1: Clone the Template

**Mac/Linux:**
```bash
git clone https://github.com/kearney/kearney-ai-coding-assistant.git ~/kaca-template
cd ~/kaca-template
```

**Windows (PowerShell):**
```powershell
git clone https://github.com/kearney/kearney-ai-coding-assistant.git $env:USERPROFILE\kaca-template
cd $env:USERPROFILE\kaca-template
```

### Step 2: Create Your Project

**Mac/Linux:**
```bash
python scaffold.py my-project --path ~/Projects/
```

**Windows (PowerShell):**
```powershell
python scaffold.py my-project --path $env:USERPROFILE\Projects
```

### Step 3: Open in Claude Code

1. Open Claude Desktop
2. File -> Open Folder
3. Navigate to your new project folder:
   - Mac: `~/Projects/my-project/`
   - Windows: `C:\Users\YourName\Projects\my-project\`
4. Select the folder

### Step 4: Start Building

In Claude Code, type:

```
/interview
```

Follow the prompts to define your project, then:

```
/plan      # Generate execution plan
/execute   # Build your project
/review    # Check brand compliance
/export    # Create deliverables
```

---

## Key Features (v3.2)

### Express Interviews
Skip lengthy questionnaires with express mode:
```bash
/interview --express           # 6-10 focused questions
/interview --template=quarterly_kpi_review  # Pre-filled templates
```

### Content Intelligence
Automatically extract insights and generate consulting-style headlines:
- **Insight Engine**: Extracts comparisons, trends, concentration risks
- **Action Titles**: Transforms "Revenue Overview" → "Northeast Drives 60% of Growth"

### Enhanced Presentations
- **Native PowerPoint Charts**: Editable bar, column, line, pie charts (not images)
- **Rich Speaker Notes**: Source, methodology, talking points included
- **Insight-to-Deck**: Generate presentations directly from insight catalogs

### Smart Planning
Update plans incrementally when requirements change:
```bash
/plan update    # Preserves completed work, updates affected tasks
```

### New Chart Types
```python
chart.waterfall(...)      # Revenue bridges
chart.stacked_bar(...)    # Composition over time
chart.combo(...)          # Dual-axis (bar + line)
chart.bullet(...)         # Performance vs target
chart.histogram(...)      # Distributions
```

### Telemetry & Metrics
Track usage and quality:
```bash
/metrics        # View session stats, compliance rates, command usage
```

### User Preferences
Persistent settings across projects:
```bash
/profile view          # See current preferences
/profile set chart.default_type horizontal_bar
```

---

## Available Commands

| Command | Description |
|---------|-------------|
| `/interview` | Start requirements gathering (supports `--express`, `--template`) |
| `/plan` | Generate execution plan |
| `/plan update` | Update plan incrementally after spec changes |
| `/execute` | Execute next task |
| `/review` | Check brand compliance |
| `/export` | Create final deliverables |
| `/profile` | Manage user preferences |
| `/metrics` | View telemetry and usage stats |
| `/status` | Show project progress |
| `/spec` | View current specification |
| `/edit` | Modify specification |

---

## Documentation

| Document | Description |
|----------|-------------|
| [Quick Start Guide](docs/QUICK_START.md) | Detailed setup for Mac and Windows |
| [User Guide](docs/USER_GUIDE.md) | Complete feature documentation |
| [Troubleshooting](docs/TROUBLESHOOTING.md) | Common issues and solutions |
| [Developer Guide](docs/DEVELOPER_GUIDE.md) | For contributors |

---

## Project Types

KACA supports 8 project types:

| Type | Description |
|------|-------------|
| `data_engineering` | Data pipelines, ETL, ingestion |
| `modeling` | Statistical/ML models |
| `analytics` | Analysis, visualization, insights |
| `presentation` | Client-facing slide decks |
| `proposal` | RFP responses, pitches |
| `dashboard` | Interactive web dashboards |
| `webapp` | Web applications, tools |
| `research` | Market research, competitive analysis |

---

## Support

- **Teams**: #Claude-Code-Help
- **Office Hours**: Wednesdays 2-3pm ET
- **Email**: da-claude@kearney.com

---

## Important: Do Not Work Here

**Do not work directly in this template repository.**

Always create a new project with `scaffold.py` first. Working in the template pollutes the shared codebase.

If you see this warning when running commands:

```
WARNING: You are in the KACA template repository
```

You need to:
1. Create a project: `python scaffold.py my-project --path ~/Projects/`
2. Open THAT folder in Claude Code
3. Work there, not here

See [Troubleshooting](docs/TROUBLESHOOTING.md) if you accidentally started work in the template.

---

*Kearney Digital & Analytics*
