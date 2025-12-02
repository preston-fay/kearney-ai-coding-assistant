# Consultant Guide

Complete guide for using the Kearney AI Coding Assistant in your daily work.

## Overview

The Kearney AI Coding Assistant transforms Claude Desktop into a "Headless IDE" - a structured environment where Claude can:

- Follow consistent project workflows
- Automatically enforce brand guidelines
- Generate compliant charts, reports, and presentations
- Maintain state across sessions

## Core Concepts

### Router Pattern

Claude operates as a "Router" that delegates tasks to specialized agents:

- **Planner Agent**: Creates execution plans from requirements
- **Steward Agent**: Executes individual tasks
- **KDS Reviewer Agent**: Validates brand compliance
- **Data Analyst Agent**: Profiles and analyzes data
- **Presentation Builder Agent**: Creates slide decks

You don't need to invoke agents directly - Claude routes automatically based on your commands.

### State Persistence

Your project state is saved in `project_state/status.json`. This enables:

- Resuming work after closing Claude Desktop
- Tracking progress across multiple sessions
- Clear visibility into completed and pending tasks

### Brand Enforcement

The `core/brand_guard.py` module programmatically validates:

- Color usage (only Kearney Purple and neutrals allowed)
- Typography (Inter font family)
- Content (no emojis)
- Chart styling (no gridlines, proper data labels)

## Workflows

### Analytics Project

Best for: Data analysis, market research, financial modeling

1. **Initialize**
   ```
   /init
   ```
   Select "analytics" template

2. **Intake**
   ```
   /interview
   ```
   Provide:
   - Data source location (CSV, Excel)
   - Analysis objectives
   - Target audience
   - Required visualizations

3. **Plan**
   ```
   /plan
   ```
   Review the generated plan covering:
   - Data profiling
   - Quality assessment
   - Chart generation
   - Report compilation

4. **Execute**
   ```
   /execute
   ```
   Claude will:
   - Profile your dataset
   - Identify data quality issues
   - Generate KDS-compliant charts
   - Create analysis report

5. **Review**
   ```
   /review
   ```
   Validates all outputs against brand guidelines

6. **Export**
   ```
   /export
   ```
   Packages deliverables:
   - Charts (PNG, high-res)
   - Report (Markdown or PDF)
   - Data summary

### Presentation Project

Best for: Client decks, internal presentations, proposals

1. **Initialize**
   ```
   /init
   ```
   Select "presentation" template

2. **Intake**
   ```
   /interview
   ```
   Provide:
   - Presentation purpose
   - Target audience
   - Key messages (3-5)
   - Desired slide count

3. **Plan**
   ```
   /plan
   ```
   Review structure:
   - Title slide
   - Agenda
   - Content sections
   - Summary/Next steps

4. **Execute**
   ```
   /execute
   ```
   Claude will:
   - Create slide structure
   - Apply KDS styling
   - Add content per section
   - Embed charts if provided

5. **Review**
   ```
   /review
   ```
   Checks:
   - Color compliance
   - Font usage
   - Layout consistency

6. **Export**
   ```
   /export
   ```
   Generates:
   - PowerPoint file (.pptx)
   - PDF version (optional)

### Web Application Project

Best for: Internal tools, dashboards, prototypes

1. **Initialize**
   ```
   /init
   ```
   Select "webapp" template

2. **Intake**
   ```
   /interview
   ```
   Provide:
   - Application purpose
   - Target users
   - Key features
   - Data requirements

3. **Plan**
   ```
   /plan
   ```
   Review scaffolding:
   - Project structure
   - Component list
   - Styling approach

4. **Execute**
   ```
   /execute
   ```
   Claude will:
   - Create project structure
   - Generate HTML/CSS
   - Apply KDS styles
   - Add basic interactivity

5. **Review**
   ```
   /review
   ```
   Validates:
   - CSS color values
   - Font declarations
   - Accessibility basics

## Best Practices

### Providing Good Requirements

**Good intake responses:**
- "Quarterly revenue analysis for EMEA leadership"
- "5-slide pitch for Series B investors"
- "Customer segmentation dashboard for marketing team"

**Avoid:**
- Vague descriptions ("make it look nice")
- Undefined audiences ("everyone")
- Missing context

### Working with Data

1. **Place data files in the project directory** before running intake
2. **Use standard formats**: CSV, Excel (.xlsx), Parquet
3. **Clean column names**: Avoid special characters
4. **Include headers**: First row should be column names

### Iterating on Outputs

After initial execution:

1. Review outputs in `outputs/` directory
2. Provide feedback directly to Claude
3. Claude will regenerate specific items
4. Run `/review` again before export

### Handling Large Projects

For complex projects with many deliverables:

1. Check status frequently: `/status`
2. Execute one task at a time
3. Review outputs incrementally
4. Save your session periodically (Claude auto-saves state)

## File Locations

| Directory | Contents |
|-----------|----------|
| `project_state/` | Status JSON, requirements YAML |
| `outputs/` | All generated deliverables |
| `outputs/charts/` | PNG chart images |
| `outputs/reports/` | Markdown reports |
| `outputs/presentations/` | PowerPoint files |
| `core/` | Engine modules (do not modify) |
| `config/` | Templates and governance rules |

## Customization

### Modifying Brand Colors

Edit `config/governance/brand.yaml` to adjust:
- Primary purple shade
- Gray scale values
- Background colors

**Note**: Do not add green or other forbidden colors.

### Adding Intake Questions

Create custom intake templates in `config/intake/`:

```yaml
template: custom
version: "1.0"

questions:
  - id: custom_field
    text: "Your custom question?"
    type: text
    required: true
```

### Creating Custom Commands

Add markdown files to `.claude/commands/`:

```markdown
# /project:custom - Description

Instructions for Claude to execute.
```

## Security Notes

- Never commit sensitive data to the repository
- Review outputs before sharing externally
- The kit does not transmit data outside your machine
- All processing happens locally via Python

## Getting Help

1. Check [Troubleshooting](TROUBLESHOOTING.md) for common issues
2. Run `/help` for command overview
3. Contact the Digital Innovation team for support
