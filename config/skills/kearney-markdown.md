# Kearney Markdown Skill

Best practices for Markdown document outputs.

## When to Use

- Technical documentation
- Research synthesis and notes
- README files
- Draft content before final formatting
- Internal reports and logs
- Any text-heavy deliverable that doesn't need formal formatting

## When NOT to Use Markdown

- Client-facing deliverables (use .docx or .pptx)
- Documents requiring precise formatting
- Anything that will be printed
- Financial models or data tables (use .xlsx)

## Document Structure

### Standard Hierarchy

```markdown
# Document Title (H1) - ONE per document
## Major Section (H2)
### Subsection (H3)
#### Detail Level (H4) - use sparingly
```

### Front Matter (for reports)

```markdown
# Report Title

**Client:** Acme Corporation
**Date:** 2025-12-01
**Author:** [Name]
**Status:** Draft | Final

---
```

## Formatting Guidelines

### Text

- Use **bold** for emphasis, not ALL CAPS
- Use *italics* for terms being defined
- Use `code` for technical terms, file names, commands
- NO emojis (Kearney brand rule)

### Lists

- Use bullet lists for unordered items
- Use numbered lists for sequences or rankings
- Keep list items parallel in structure
- Indent sub-items consistently (2 spaces)

```markdown
Good:
- Analyze the data
- Identify key trends
- Document findings

Bad:
- Data analysis
- We need to identify trends
- Findings documentation complete
```

### Tables

```markdown
| Column A | Column B | Column C |
|----------|----------|----------|
| Data 1   | Data 2   | Data 3   |
```

- Always include header row
- Align columns appropriately (left for text, right for numbers)
- Keep tables simple - complex data belongs in Excel
- Use `|:---|` for left, `|---:|` for right, `|:---:|` for center alignment

### Code Blocks

Always specify language for syntax highlighting:

```python
# Python example
from core.chart_engine import KDSChart
chart = KDSChart()
```

```sql
-- SQL example
SELECT region, SUM(sales) FROM revenue GROUP BY region
```

- Use for: code, configuration, command-line examples
- Keep blocks focused - one concept per block

### Links

- Use descriptive link text: `[Project Documentation](url)` not `[click here](url)`
- Use reference-style links for repeated URLs:

```markdown
See the [installation guide][install] and [configuration guide][config].

[install]: docs/INSTALLATION.md
[config]: docs/CONFIGURATION.md
```

### Blockquotes

Use for:
- Key findings or insights
- Important warnings
- Direct quotes from sources

```markdown
> Key Finding: The Northeast region accounts for 45% of total revenue,
> up from 38% last quarter.
```

## File Naming Conventions

| Document Type | Pattern | Example |
|---------------|---------|---------|
| Meeting notes | `YYYY-MM-DD-meeting-topic.md` | `2025-12-01-kickoff-meeting.md` |
| Research | `research-topic-name.md` | `research-competitor-analysis.md` |
| Technical docs | `component-name.md` | `data-pipeline.md` |
| Changelogs | `CHANGELOG.md` | `CHANGELOG.md` |

## Section Templates

### Analysis Document

```markdown
# [Topic] Analysis

## Executive Summary
[2-3 sentence overview of findings]

## Background
[Context and why this analysis was conducted]

## Methodology
[How the analysis was performed]

## Findings
### Finding 1
### Finding 2
### Finding 3

## Recommendations
1. [Action item 1]
2. [Action item 2]

## Next Steps
- [ ] [Task 1]
- [ ] [Task 2]

## Appendix
[Supporting data, detailed tables]
```

### Meeting Notes

```markdown
# Meeting: [Topic]

**Date:** YYYY-MM-DD
**Attendees:** [Names]
**Duration:** [X] minutes

## Agenda
1. [Item 1]
2. [Item 2]

## Discussion
### [Topic 1]
- Key point
- Decision made

### [Topic 2]
- Key point
- Action item assigned

## Action Items
| Action | Owner | Due Date |
|--------|-------|----------|
| [Task] | [Name] | YYYY-MM-DD |

## Next Meeting
- Date: YYYY-MM-DD
- Topics: [...]
```

## Conversion Path

Markdown often serves as draft before final format:

| From | To | Use Case |
|------|-----|----------|
| MD | DOCX | Proposals, formal reports |
| MD | PPTX | Extract key points for slides |
| MD | HTML | Dashboards, web content |
| MD | PDF | Technical documentation |

## Kearney Brand in Markdown

While Markdown has limited styling, maintain brand consistency:

- NO emojis anywhere in content
- Use Kearney terminology consistently
- Follow Kearney writing style (professional, concise)
- When converted to other formats, brand colors will be applied

## Quality Checklist

Before finalizing any Markdown document:

- [ ] Single H1 heading at top
- [ ] Logical heading hierarchy (no skipped levels)
- [ ] No emojis in content
- [ ] All links are valid
- [ ] Code blocks have language specified
- [ ] Tables have header rows
- [ ] Lists are parallel in structure
- [ ] Document has clear purpose and audience
- [ ] Spelling and grammar checked
