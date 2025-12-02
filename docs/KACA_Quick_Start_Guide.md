# Kearney AI Coding Assistant - Quick Start Guide

## What is This?

The Kearney AI Coding Assistant turns Claude into your AI-powered project assistant. It handles:

- **Structured requirements gathering** (not just chat)
- **Project planning and execution tracking**
- **Brand-compliant outputs** (Kearney purple, no green, proper formatting)
- **Quality control and export**

---

## 5-Minute Setup

### Step 1: Create Your Project

Open Terminal (Mac) or Command Prompt (Windows):

```bash
python3 ~/Projects/KACA/scaffold.py my-project-name --path ~/Projects/
```

Replace `my-project-name` with your actual project name (e.g., `acme-churn-model`).

### Step 2: Open in Claude Desktop

1. Open **Claude Desktop**
2. **File → Open Folder**
3. Navigate to your project folder (e.g., `~/Projects/my-project-name`)
4. Click **Open**

### Step 3: Start Building

Type in Claude:

```
/interview
```

Claude will guide you through defining your project.

---

## The Standard Workflow

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│   /interview    →    Define what you're building            │
│        │                                                    │
│        ▼                                                    │
│   /plan         →    Get your execution plan                │
│        │                                                    │
│        ▼                                                    │
│   /execute      →    Build it (repeat until done)           │
│        │                                                    │
│        ▼                                                    │
│   /review       →    Check brand compliance                 │
│        │                                                    │
│        ▼                                                    │
│   /export       →    Get final deliverables                 │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Project Types

When you start `/interview`, you'll choose your project type:

| # | Type | What You're Building |
|---|------|----------------------|
| 1 | Data Engineering | Data pipelines, ETL, data cleaning |
| 2 | Statistical/ML Model | Predictions, classification, clustering |
| 3 | Analytics Asset | Analysis, insights, visualizations |
| 4 | Presentation/Deck | Client presentations, readouts |
| 5 | Proposal Content | RFP responses, pitches, proposals |
| 6 | Dashboard | Interactive data visualization |
| 7 | Web Application | Tools, prototypes, calculators |
| 8 | Research/Synthesis | Market research, competitive analysis |

**Doing multiple?** Select what you need - the system handles hybrid projects.

---

## Your Project Folders

```
my-project/
├── data/
│   ├── raw/          ← Put your source files here
│   └── processed/    ← Cleaned data goes here
│
├── outputs/          ← Charts and reports appear here
│
└── exports/          ← Final client-ready deliverables
```

---

## Essential Commands

| Command | What It Does |
|---------|--------------|
| `/interview` | Define your project requirements |
| `/plan` | Generate execution plan |
| `/execute` | Run the next task |
| `/status` | See where you are |
| `/review` | Check brand compliance |
| `/export` | Create final deliverables |
| `/help` | Show all commands |

---

## Picking Up Where You Left Off

Close Claude, come back later? No problem.

1. **File → Open Folder** → Your project
2. Claude will show your current status
3. Type `/execute` to continue

---

## Need Help?

- **Teams**: #Claude-Code-Help
- **Office Hours**: Wednesdays 2-3pm ET
- **Email**: da-claude@kearney.com

---

*Kearney Digital & Analytics*
