# /plan update

---
name: plan-update
description: Update the existing plan based on spec changes, preserving completed work
agent: @planner
---

Updates the execution plan incrementally based on specification changes.

## Usage

```
/plan update
```

## Behavior

1. Load current spec and previous version from `spec_history/`
2. Compute semantic diff between versions using `compute_diff()`
3. Assess impact on current plan using `assess_plan_impact()`
4. For each change:
   - Identify affected tasks via spec path mappings
   - Mark completed tasks in affected areas as "needs_review"
   - Mark pending tasks in affected areas as "updated"
   - Generate new tasks for added requirements
   - Mark tasks for removed requirements as "deprecated"
5. Preserve all completed tasks in unaffected areas
6. Update `plan.md` with change annotations
7. Save updated `status.json`

## Implementation

```python
from core.spec_diff import compute_diff, assess_plan_impact
from core.plan_updater import PlanUpdater, update_plan_from_diff
from core.spec_manager import load_spec, get_history

# Load specs
current_spec = load_spec()
history = get_history()

if len(history) < 2:
    print("No previous spec version to compare against.")
    print("Run /plan to generate initial plan.")
else:
    # Get previous version
    previous_path = history[-2]  # Second to last
    with open(previous_path) as f:
        previous_spec = yaml.safe_load(f)

    # Compute diff
    diff = compute_diff(previous_spec, current_spec)

    if not diff.has_changes():
        print("No changes detected. Plan is up to date.")
    else:
        print(f"Detected {len(diff.changes)} changes:")
        for change in diff.changes:
            print(f"  - {change.description}")

        # Apply updates
        result = update_plan_from_diff(diff)
        print(f"\nPlan updated: {result.summary}")
```

## Output

Updates `project_state/status.json` with:
- Task status changes (needs_review, updated, deprecated)
- New tasks for added requirements
- History entry documenting the update

## Example

```
User: /plan update

Claude: Comparing spec v2 to v1...

Detected 3 changes:
  - Modified data > sources[0] > path: data.csv -> data_v2.csv
  - Added deliverables[2]: Dashboard
  - Modified problem > business_question

Impact Assessment:
  - 2 tasks marked for review (Phase 1, Phase 2)
  - 1 new task added for Dashboard deliverable
  - 3 tasks unchanged (Phase 4, Phase 5)

Plan updated successfully.
```
