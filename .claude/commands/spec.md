# /project:spec

---
name: spec
description: View current project specification
agent: @router
---

Display the current project specification (spec.yaml).

## Usage

```
/project:spec                         # Show full spec summary
/project:spec --full                  # Show complete YAML
/project:spec --section modeling      # Show specific section
/project:spec --diff                  # Show changes from last version
```

## Behavior

### Default (Summary View)

Display a human-readable summary:

```
PROJECT SPECIFICATION (version 3)
================================

PROJECT: acme-churn-model
TYPE: modeling
CLIENT: Acme Corporation
DEADLINE: 2025-12-15

BUSINESS QUESTION:
Which customers are most likely to cancel their subscription
in the next 90 days, and what factors drive churn?

SUCCESS CRITERIA:
- Identify top 20% of at-risk customers
- Achieve minimum 0.75 AUC on holdout set
- Provide interpretable feature importance

MODELING DETAILS:
- Problem Type: classification
- Target: churned_90_days (8% positive rate)
- Validation: time_based_split
- Metrics: auc_roc, precision_at_20pct, recall, f1_score

DATA SOURCES:
- customer_data.csv (~50,000 rows)
- subscription_events.csv (~200,000 rows)

DELIVERABLES:
- Model artifact (pickle)
- Validation report (markdown)
- Interpretation deck (pptx, 10-15 slides)
- Scoring script (python)

Last updated: 2025-12-01 14:45 UTC
```

### With --full Flag

Display the raw YAML content:

```yaml
version: 3
created_at: 2025-12-01T10:30:00Z
updated_at: 2025-12-01T14:45:00Z

meta:
  project_name: acme-churn-model
  project_type: modeling
  client: Acme Corporation
  deadline: 2025-12-15
  ...
```

### With --section Flag

Display only the specified section:

```
/project:spec --section modeling.validation

VALIDATION SETTINGS:
- strategy: time_based_split
- train_period: 2024-01-01 to 2024-09-30
- test_period: 2024-10-01 to 2024-12-31
- metrics: [auc_roc, precision_at_20pct, recall, f1_score]
```

### With --diff Flag

Show changes between current and previous version:

```
CHANGES FROM VERSION 2 -> VERSION 3:

ADDED:
+ modeling.validation.metrics: f1_score

CHANGED:
~ meta.deadline: 2025-12-10 -> 2025-12-15

REMOVED:
- (none)

Changelog entry: "Added f1_score metric, extended deadline"
```

## Section Paths

Valid section paths:

- `meta` - Project metadata
- `problem` - Problem definition
- `data` - Data sources
- `deliverables` - Deliverables list
- `constraints` - Project constraints
- `notes` - Additional notes
- `modeling` - Modeling-specific (if project_type is modeling)
- `presentation` - Presentation-specific (if project_type is presentation)
- `dashboard` - Dashboard-specific (if project_type is dashboard)
- (etc. for each project type)

Nested paths also work:
- `modeling.validation`
- `modeling.features.included`
- `meta.stakeholders`

## Context Files

This command reads:

- project_state/spec.yaml (current spec)
- project_state/spec_history/spec_v{N}.yaml (for diff)

## Error Handling

- If spec.yaml doesn't exist: "No specification found. Run /project:interview first."
- If section path is invalid: "Section '{path}' not found in specification."
- If no previous version for diff: "No previous version available for comparison."

## Core Engine Usage

```python
from core import load_spec, get_section, get_spec_summary

# Load spec
spec = load_spec()
if spec is None:
    print("No specification found. Run /project:interview first.")
    return

# Summary view
print(get_spec_summary(spec))

# Section view
section = get_section(spec, 'modeling.validation')
print(section)
```

## Related Commands

- `/project:interview` - Create specification via interview
- `/project:edit` - Modify specification
- `/project:history` - View version history
- `/project:plan` - Generate plan from spec
