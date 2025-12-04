# /project:interview

---
name: interview
description: Conduct structured requirements gathering
agent: @interviewer
---

Conduct a structured interview to gather project requirements and generate spec.yaml.

## Usage

```
/project:interview                           # Start full interview
/project:interview --express                 # Express mode (6-10 questions)
/project:interview --template=<name>         # Start from a pre-filled template
/project:interview --type modeling           # Start with specific type
/project:interview --section data            # Re-interview specific section
/project:interview --continue                # Continue interrupted interview
```

## Express Mode

Express mode is designed for experienced users who want to get started quickly. It asks only the essential questions needed to begin execution:

- Project name and client
- Core business question/objective
- Data sources
- Primary deliverable format
- Audience level

All other settings use smart defaults. The spec will be marked with `confidence: assumed` for sections that weren't explicitly asked, allowing @planner to fill gaps as needed.

**Available for all 8 project types:**
- analytics, presentation, dashboard, modeling
- proposal, research, data_engineering, webapp

**Example:**
```
/project:interview --express
```

## Templates

Templates are pre-filled specifications for common project types. They include sensible defaults for deliverables, visualization settings, and success criteria.

**Available templates:**

| Template | Type | Description |
|----------|------|-------------|
| `quarterly_kpi_review` | analytics | Quarterly performance review with KPI dashboard |
| `executive_summary` | presentation | C-suite presentation with findings and recommendations |
| `competitive_analysis` | research | Competitive landscape analysis with benchmarking |

**Example:**
```
/project:interview --template=quarterly_kpi_review
```

When using a template, the interview will only ask questions for fields that aren't pre-filled (typically just project name, client, and data sources).

## Behavior

### If spec.yaml Already Exists

Offer options:

```
An existing specification was found:

PROJECT: {project_name}
TYPE: {project_type}
VERSION: {version}

What would you like to do?

1. Start fresh (archive current spec)
2. Edit existing spec (use /project:edit)
3. Re-interview specific section

Enter choice (1-3):
```

### Starting a New Interview

1. Display project type menu:

```
What type of work product are you building?

1. Data Engineering (ingestion, transformation, pipelines)
2. Statistical/ML Model (prediction, classification, clustering)
3. Analytics Asset (analysis, visualization, insights)
4. Presentation/Deck (client-facing slides)
5. Proposal Content (RFP response, pitch, methodology)
6. Dashboard (interactive data visualization)
7. Web Application (tool, prototype, MVP)
8. Research/Synthesis (market research, competitive analysis)
```

2. Load the appropriate interview tree from config/interviews/{type}.yaml

3. Conduct the interview:
   - Ask questions one at a time
   - Apply conditional logic to skip irrelevant questions
   - Probe for clarity when needed
   - Acknowledge answers conversationally

4. At completion:
   - Display comprehensive summary
   - Ask for confirmation
   - Save spec.yaml

### Re-interviewing a Section

If `--section` is specified:

1. Load current spec.yaml
2. Show current values for that section
3. Ask if user wants to keep and add, or start fresh
4. Run only the questions for that section
5. Merge answers back into spec.yaml
6. Increment version

## Interview Trees

Each project type has a dedicated interview tree:

| Type | Interview File | Key Questions |
|------|---------------|---------------|
| data_engineering | data_engineering.yaml | Sources, transformations, pipeline type |
| modeling | modeling.yaml | Problem type, target, validation, interpretability |
| analytics | analytics.yaml | Analysis type, metrics, visualizations |
| presentation | presentation.yaml | Purpose, audience, key messages |
| proposal | proposal.yaml | Opportunity type, competitive context, sections |
| dashboard | dashboard.yaml | Dashboard type, interactivity, views |
| webapp | webapp.yaml | App type, features, tech stack |
| research | research.yaml | Research questions, sources, synthesis format |

## Question Flow

Questions are asked in order within sections. Each question has:

- **prompt**: The text shown to the user
- **type**: How to parse the response (text, choice, boolean, etc.)
- **required**: Whether the question can be skipped
- **condition**: When to ask (based on previous answers)
- **follow_up**: Probe to ask if answer is insufficient

### Conditional Logic

Questions are skipped if their condition evaluates to false:

```yaml
condition: "problem_type == 'classification'"  # Only for classification
condition: "auth_required == True"             # Only if auth needed
```

### Follow-Up Probes

If an answer is too short or vague, ask the follow-up:

```yaml
follow_up:
  condition: "len(answer) < 30"
  prompt: "Can you elaborate on the business context?"
```

## Output

On successful completion:

```
Saved to project_state/spec.yaml (version 1).

Next step: Run /project:plan to generate the execution plan.
```

## Context Files

The interviewer agent needs access to:

- config/interviews/*.yaml (interview trees)
- project_state/spec.yaml (if exists)
- core/interview_engine.py (engine functions)
- core/spec_manager.py (spec CRUD)

## Error Handling

- If interview tree not found: "Interview tree for '{type}' not found. Available types: ..."
- If user aborts: "Interview cancelled. No changes saved."
- If required question skipped: "This question is required. Please provide an answer."

## Related Commands

- `/project:edit` - Edit specific parts of spec.yaml
- `/project:spec` - View current specification
- `/project:history` - View specification version history
- `/project:plan` - Generate execution plan from spec
