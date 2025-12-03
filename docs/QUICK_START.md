# KACA Quick Start Guide

Get from zero to working project in 5 minutes.

---

## Prerequisites

### Required Software

| Software | Version | Check Command |
|----------|---------|---------------|
| Python | 3.10+ | `python --version` or `python3 --version` |
| Git | Any recent | `git --version` |
| Claude Desktop | Latest | Open the app |

### Installation Links

- **Python**: https://www.python.org/downloads/
- **Git**: https://git-scm.com/downloads
- **Claude Desktop**: https://claude.ai/download

---

## Setup Instructions

### Mac / Linux

Open Terminal and run:

```bash
# 1. Clone the template (one-time setup)
git clone https://github.com/kearney/kearney-ai-coding-assistant.git ~/kaca-template

# 2. Create your project
cd ~/kaca-template
python scaffold.py my-project --path ~/Projects/

# 3. Verify creation
ls ~/Projects/my-project/
```

You should see:
```
CLAUDE.md
README.md
.claude/
core/          -> (symlink to template)
config/        -> (symlink to template)
data/
exports/
outputs/
project_state/
```

### Windows (PowerShell)

Open PowerShell and run:

```powershell
# 1. Clone the template (one-time setup)
git clone https://github.com/kearney/kearney-ai-coding-assistant.git $env:USERPROFILE\kaca-template

# 2. Create your project
cd $env:USERPROFILE\kaca-template
python scaffold.py my-project --path $env:USERPROFILE\Projects

# 3. Verify creation
dir $env:USERPROFILE\Projects\my-project
```

You should see:
```
CLAUDE.md
README.md
.claude/
core/          -> (junction to template)
config/        -> (junction to template)
data/
exports/
outputs/
project_state/
```

---

## Connect Claude Code

### Step 1: Open Claude Desktop

Launch the Claude Desktop application.

### Step 2: Open Your Project Folder

1. Click **File** -> **Open Folder** (or press `Cmd+O` / `Ctrl+O`)
2. Navigate to your project:
   - **Mac**: `~/Projects/my-project/`
   - **Windows**: `C:\Users\YourName\Projects\my-project\`
3. Click **Open**

### Step 3: Verify Connection

Claude should display the project context. Type:

```
What files are in this project?
```

Claude should list your project files including `CLAUDE.md`, `data/`, etc.

---

## Your First Project

### Define Requirements

Type:

```
/interview
```

Claude will ask you questions about:
- Project type (dashboard, presentation, analytics, etc.)
- Data sources
- Deliverables
- Audience

Answer the questions. Claude creates `project_state/spec.yaml`.

### Generate Plan

Type:

```
/plan
```

Claude creates an execution plan in `project_state/plan.md`.

### Build It

Type:

```
/execute
```

Claude works through the plan, creating files in:
- `outputs/` - Charts, reports, intermediate files
- `exports/` - Final deliverables

### Check Brand Compliance

Type:

```
/review
```

Claude validates all outputs against Kearney brand guidelines.

### Get Your Deliverables

Your finished files are in `exports/`:
- Presentations: `.pptx`
- Documents: `.docx`
- Dashboards: `.html` or `app.py`
- Spreadsheets: `.xlsx`

---

## Common Commands

| Command | What It Does |
|---------|--------------|
| `/interview` | Define project requirements |
| `/plan` | Generate execution plan |
| `/execute` | Execute next task |
| `/status` | Show current progress |
| `/review` | Check brand compliance |
| `/export` | Create final deliverables |
| `/spec` | View current specification |
| `/edit` | Modify requirements |
| `/webapp` | Generate web dashboard |
| `/help` | Show all commands |

### Session Management

| Command | What It Does |
|---------|--------------|
| `/compact` | Summarize context to free space |
| `/reset` | Archive and start fresh |
| `/rollback` | Restore from previous state |

---

## Next Steps

- Read the full [User Guide](USER_GUIDE.md) for advanced features
- Check [Troubleshooting](TROUBLESHOOTING.md) if you hit issues
- Join **#Claude-Code-Help** on Teams for support

---

## Quick Reference Card

Save this for easy reference:

```
+-------------------------------------------------------------+
|  KACA QUICK REFERENCE                                       |
+-------------------------------------------------------------+
|                                                             |
|  CREATE PROJECT                                             |
|    Mac:     python scaffold.py NAME --path ~/Projects/      |
|    Windows: python scaffold.py NAME --path $env:USERPROFILE\Projects |
|                                                             |
|  WORKFLOW                                                   |
|    /interview  ->  /plan  ->  /execute  ->  /review  -> done|
|                                                             |
|  KEY FOLDERS                                                |
|    data/raw/       Put your source data here                |
|    outputs/        Generated charts and reports             |
|    exports/        Final deliverables                       |
|                                                             |
|  GET HELP                                                   |
|    /help           Show all commands                        |
|    /status         Show current progress                    |
|    Teams:          #Claude-Code-Help                        |
|                                                             |
+-------------------------------------------------------------+
```

---

*Kearney Digital & Analytics*
