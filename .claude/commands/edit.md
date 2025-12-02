# /project:edit

---
name: edit
description: Edit specific parts of the project specification
agent: @spec-editor
---

Edit the project specification (spec.yaml) with version control and impact analysis.

## Usage

```
/project:edit                         # Open general edit mode
/project:edit meta.deadline           # Edit single field
/project:edit modeling.validation     # Edit section
/project:edit deliverables            # Edit deliverables list
```

## Behavior

### No Arguments (General Edit Mode)

Display current spec summary and offer options:

```
Current Specification (version 3):

PROJECT: acme-churn-model
TYPE: modeling
CLIENT: Acme Corporation
DEADLINE: 2025-12-15

What would you like to edit?

1. Basic info (name, client, deadline)
2. Problem definition
3. Type-specific settings (modeling)
4. Data sources
5. Deliverables
6. Constraints
7. Specify section path directly

Enter choice or section path:
```

### With Section Path

Show current value and prompt for new value:

```
/project:edit meta.deadline

Current value: 2025-12-15

Enter new deadline (or press Enter to keep current):
```

### For Nested Sections

Show all fields in the section:

```
/project:edit modeling.validation

Current validation settings:

  strategy: time_based_split
  train_period: 2024-01-01 to 2024-09-30
  test_period: 2024-10-01 to 2024-12-31
  metrics: [auc_roc, precision_at_20pct, recall]

What would you like to change?
Options: strategy, train_period, test_period, metrics, or 'all'
```

## Section Paths

Common paths for editing:

### Meta
- `meta.project_name` - Project name
- `meta.client` - Client name
- `meta.deadline` - Target deadline

### Problem
- `problem.business_question` - Core business question
- `problem.success_criteria` - Success criteria list

### Modeling (for modeling projects)
- `modeling.problem_type` - classification, regression, etc.
- `modeling.target_variable` - Target to predict
- `modeling.target_definition` - Definition of target
- `modeling.class_balance` - balanced, imbalanced
- `modeling.features.included` - Included features
- `modeling.features.excluded` - Excluded features
- `modeling.validation.strategy` - Validation approach
- `modeling.validation.metrics` - Metrics to track
- `modeling.interpretability.required` - Is interpretability needed

### Presentation (for presentation projects)
- `presentation.purpose` - Deck purpose
- `presentation.audience` - Target audience
- `presentation.slide_count` - Number of slides
- `presentation.key_messages` - Key messages list

### Other Types
Each project type has its own section under the type name (e.g., `dashboard.interactivity`, `webapp.features`).

## Impact Analysis

For significant changes, show impact before applying:

```
This is a significant change. Impact analysis:

PLAN IMPACT:
- Task 2.1 (Train classifier) would become (Train regressor)
- Task 2.3 metrics would change

COMPLETED WORK IMPACT:
- Task 1.2 (Feature engineering) is still valid
- Model training would need to be re-run

Proceed with this change? (yes/no)
```

Significant changes that trigger impact analysis:
- `problem_type` changes
- `target_variable` changes
- Validation strategy changes
- Major deliverable changes

## Versioning

Every edit creates a new version:

1. Old version is archived to spec_history/spec_v{N}.yaml
2. Changelog is updated with description
3. New version is saved to spec.yaml

After saving:

```
spec.yaml updated to version 4.
Changelog entry: "Changed deadline to 2025-12-31"

Changes archived to: project_state/spec_history/spec_v3.yaml
```

## Plan Regeneration

If the change affects the execution plan, inform user:

```
NOTE: This change may require plan regeneration.
Run /project:plan to update the execution plan.
```

## List Editing

For list fields (metrics, deliverables, features):

```
/project:edit modeling.validation.metrics

Current metrics: [auc_roc, precision_at_20pct, recall]

Options:
1. Add item
2. Remove item
3. Replace all
4. Keep current

Enter choice:
```

## Context Files

The spec-editor agent needs access to:

- project_state/spec.yaml (current spec)
- project_state/spec_history/ (version archive)
- core/spec_manager.py (spec CRUD functions)

## Error Handling

- If spec.yaml doesn't exist: "No specification found. Run /project:interview first."
- If path is invalid: "Section '{path}' not found. Available sections: ..."
- If user cancels: "Edit cancelled. No changes saved."

## Related Commands

- `/project:interview` - Create new specification via interview
- `/project:spec` - View current specification
- `/project:history` - View specification version history
- `/project:plan` - Regenerate execution plan
