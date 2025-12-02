# Sample Analytics Project

This example demonstrates a completed analytics project using the Kearney AI Coding Assistant.

## Project Overview

- **Name**: Q4 Sales Analysis
- **Template**: analytics
- **Status**: Completed

## Contents

```
sample-analytics/
  data/
    sales_data.csv          # Source data (24 rows)
  project_state/
    status.json             # Project state (completed)
    requirements.yaml       # Captured requirements
  outputs/
    charts/                 # (would contain PNGs)
    reports/
      analysis.md           # Generated analysis report
```

## What This Demonstrates

1. **Project Structure**: How files are organized after running through the workflow
2. **State Persistence**: The `status.json` shows all tasks completed
3. **Requirements Capture**: The `requirements.yaml` shows intake responses
4. **Output Format**: The `analysis.md` shows a KDS-compliant report

## Running This Example

To regenerate the charts from this example:

```bash
cd examples/sample-analytics
python ../../templates/analytics/chart_template.py data/sales_data.csv --output outputs/charts
```

## Using as a Starting Point

To create a similar project:

1. Copy this directory as a template
2. Replace `data/sales_data.csv` with your data
3. Update `project_state/requirements.yaml` with your requirements
4. Delete `project_state/status.json` to reset
5. Run `/project:init` in Claude Desktop
