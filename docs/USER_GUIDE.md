# KACA User Guide

Complete documentation for the Kearney AI Coding Assistant.

---

## Table of Contents

1. [Overview](#overview)
2. [Project Types](#project-types)
3. [Commands Reference](#commands-reference)
4. [Working with Data](#working-with-data)
5. [Creating Dashboards](#creating-dashboards)
6. [Brand Guidelines](#brand-guidelines)
7. [Advanced Features](#advanced-features)

---

## Overview

KACA is an AI-powered system that helps Kearney consultants build data projects with automatic brand compliance. It uses a structured workflow:

```
Interview -> Specification -> Plan -> Execution -> Review -> Export
```

### Core Concepts

| Concept | Description |
|---------|-------------|
| **Specification** | Your project requirements in `project_state/spec.yaml` |
| **Plan** | Execution steps in `project_state/plan.md` |
| **Status** | Progress tracking in `project_state/status.json` |
| **Engines** | Python modules that generate brand-compliant outputs |

### Directory Structure

```
my-project/
+-- CLAUDE.md              # AI instructions (don't edit)
+-- README.md              # Project-specific readme
+-- .claude/               # Commands and agents
+-- core/                  # Shared engines (symlink)
+-- config/                # Templates and skills (symlink)
+-- project_state/         # YOUR PROJECT STATE
|   +-- spec.yaml          # Requirements (source of truth)
|   +-- plan.md            # Execution plan
|   +-- status.json        # Progress tracking
+-- data/
|   +-- raw/               # Put source files here
|   +-- processed/         # Cleaned data
|   +-- external/          # Reference data
+-- outputs/               # Generated artifacts
|   +-- charts/
|   +-- reports/
+-- exports/               # Final deliverables
```

---

## Project Types

### Analytics (`analytics`)

Analysis, visualization, and insights from data.

**Typical outputs:**
- Charts and visualizations
- Statistical summaries
- Insight reports

### Dashboard (`dashboard`)

Interactive web-based data visualization.

**Typical outputs:**
- Static HTML dashboard (Tier 1)
- Streamlit app (Tier 2)
- React scaffold (Tier 3)

### Presentation (`presentation`)

Client-facing slide decks.

**Typical outputs:**
- PowerPoint (.pptx)
- Supporting charts

### Data Engineering (`data_engineering`)

Data pipelines and transformations.

**Typical outputs:**
- ETL scripts
- Data quality reports
- Pipeline documentation

### Modeling (`modeling`)

Statistical and machine learning models.

**Typical outputs:**
- Model code
- Evaluation reports
- Prediction outputs

### Proposal (`proposal`)

RFP responses and pitch materials.

**Typical outputs:**
- Proposal document (.docx)
- Supporting slides (.pptx)

### Research (`research`)

Market research and competitive analysis.

**Typical outputs:**
- Research report (.docx)
- Data tables (.xlsx)
- Visualizations

### Web App (`webapp`)

Interactive web applications and tools.

**Typical outputs:**
- HTML/JS application
- Streamlit app
- React project

---

## Commands Reference

### Workflow Commands

| Command | Description |
|---------|-------------|
| `/interview` | Start requirements gathering |
| `/plan` | Generate execution plan from spec |
| `/execute` | Execute the next pending task |
| `/status` | Show current progress |
| `/review` | Validate brand compliance |
| `/export` | Package final deliverables |

### Specification Commands

| Command | Description |
|---------|-------------|
| `/spec` | Display current specification |
| `/edit` | Modify specific requirements |
| `/history` | View specification versions |

### Session Commands

| Command | Description |
|---------|-------------|
| `/compact` | Summarize context to free space |
| `/reset` | Archive current state and start fresh |
| `/rollback` | Restore project state from archive |

### Utility Commands

| Command | Description |
|---------|-------------|
| `/help` | Show all available commands |
| `/webapp` | Generate web dashboard |
| `/init` | Initialize new project (rarely needed) |

### Express Mode and Templates

For faster project setup, use express mode or templates:

**Express Mode** - Streamlined interview with only 6-10 essential questions:
```
/interview --express
```

**Templates** - Start from a pre-filled specification:
```
/interview --template=quarterly_kpi_review
```

| Template | Type | Best For |
|----------|------|----------|
| `quarterly_kpi_review` | analytics | Recurring quarterly business reviews |
| `executive_summary` | presentation | C-suite presentations |
| `competitive_analysis` | research | Competitive landscape research |

Templates only ask for project name, client, and data sources - everything else is pre-configured.

---

## Working with Data

### Supported Formats

| Format | Extension | Notes |
|--------|-----------|-------|
| CSV | `.csv` | Preferred for tabular data |
| Excel | `.xlsx`, `.xls` | Converted to CSV internally |
| Parquet | `.parquet` | For large datasets |
| JSON | `.json` | For nested/document data |
| DuckDB | `.duckdb` | For analytical queries |
| SQLite | `.sqlite`, `.db` | For relational data |

### Data Size Guidelines

| Size | Recommendation |
|------|----------------|
| < 10 MB | Load directly, embed in HTML |
| 10-100 MB | Use DuckDB, Streamlit tier |
| 100+ MB | DuckDB with selective queries |

### Placing Data Files

1. Put raw data in `data/raw/`
2. KACA will clean and process to `data/processed/`
3. Never commit data files (they're gitignored)

**Mac/Linux:**
```bash
cp ~/Downloads/sales_data.csv data/raw/
```

**Windows:**
```powershell
copy $env:USERPROFILE\Downloads\sales_data.csv data\raw\
```

### Data Configuration in Spec

```yaml
datasets:
  sales:
    type: csv
    path: data/raw/sales.csv
    keys: [region, product, date]
    value_cols: [revenue, units]
```

---

## Creating Dashboards

### Tier Selection

| Tier | Best For | Output |
|------|----------|--------|
| **Static HTML** | Email, embed in PPT, client viewing | Single `.html` file |
| **Streamlit** | Internal tools, live data | Python app |
| **React** | Engineering handoff, production | Full project |

### Quick Dashboard

```
/interview
# Select "dashboard" type
# Answer questions about data, metrics, charts

/plan
/execute
/review
```

### Manual Dashboard Creation

```python
from core import KDSData, KDSWebApp, KDSTheme

# Load data
data = KDSData.from_dict({
    "sales": {
        "type": "csv",
        "path": "data/raw/sales.csv",
        "keys": ["region"],
        "value_cols": ["revenue"]
    }
})

# Build dashboard
app = (
    KDSWebApp("Sales Dashboard", theme=KDSTheme())
    .set_data(data)
    .add_metric("Total Revenue", "$1.2M")
    .add_chart("sales", "bar", "region", "revenue", "By Region")
    .add_table("sales", "Details")
)

# Generate
app.generate("exports/dashboard.html")
```

### Launching Streamlit Dashboards

**Mac/Linux:**
```bash
cd exports/my_dashboard/
pip install -r requirements.txt
streamlit run app.py
```

**Windows:**
```powershell
cd exports\my_dashboard
pip install -r requirements.txt
streamlit run app.py
```

Open http://localhost:8501 in your browser.

---

## Brand Guidelines

### Colors

| Use | Color | Hex |
|-----|-------|-----|
| Primary | Kearney Purple | `#7823DC` |
| Background (dark) | Dark gray | `#1E1E1E` |
| Background (light) | White | `#FFFFFF` |
| Text | Dark gray | `#333333` |
| Positive indicator | Light purple | `#D4A5FF` |
| Negative indicator | Coral | `#FF6F61` |

### Forbidden

- **Green colors**: Never use any shade of green
- **Emojis**: Never use in any output
- **Gridlines**: Remove from all charts

### Typography

| Element | Font | Weight |
|---------|------|--------|
| Headers | Inter | 600 (SemiBold) |
| Body | Inter | 400 (Regular) |
| Data | Inter | 500 (Medium) |

Fallback: Arial, Helvetica, sans-serif

### Charts

- No gridlines
- Data labels outside bars/slices
- Legend below chart
- Kearney Purple as primary color

---

## Advanced Features

### Resuming Projects

KACA automatically saves state. To resume:

1. Open the project folder in Claude Code
2. Run `/status` to see where you left off
3. Run `/execute` to continue

### Multiple Data Sources

```yaml
datasets:
  sales:
    type: csv
    path: data/raw/sales.csv
    keys: [product_id]
    value_cols: [revenue]

  products:
    type: csv
    path: data/raw/products.csv
    keys: [product_id]
    value_cols: [name, category]

  warehouse:
    type: duckdb
    path: data/analytics.duckdb
    sql: "SELECT * FROM monthly_summary"
    keys: [month]
    value_cols: [total_revenue, total_units]
```

### Custom Themes

```python
from core import KDSTheme

custom_theme = KDSTheme(
    primary="#7823DC",
    accent_1="#9B59B6",
    # ... other customizations
)
```

### Client Brand Override

For client-branded deliverables, create `config/brand_override.yaml`:

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

---

## Getting Help

- **Commands**: `/help`
- **Teams**: #Claude-Code-Help
- **Office Hours**: Wednesdays 2-3pm ET
- **Email**: da-claude@kearney.com

---

*Kearney Digital & Analytics*
