---
name: reset
description: Archive current state and start fresh
agent: @router
---

# /project:reset

## Purpose

When a project needs to start over:
- Major requirements change
- Corrupted state files
- "Let's try a different approach"

## Behavior

1. **Confirm Intent**
   - "This will archive your current project state and start fresh.
     Your data files will NOT be deleted.
     Current progress: {n}/{total} tasks complete.
     Are you sure? Type 'yes' to confirm."

2. **Archive Current State**
   - Create project_state/archive/{timestamp}/
   - Copy spec.yaml, plan.md, status.json to archive
   - Copy spec_history/ contents to archive
   - Log the reset action

3. **Reset State**
   - Remove current state files
   - Clear spec_history/ (keep directory)
   - Keep data/ intact
   - Keep outputs/ intact

4. **Offer Next Steps**
   - "Project reset complete. Previous state archived.
     Type /project:interview to define your new approach."

## Implementation

```python
from core.state_validator import (
    get_state_summary,
    reset_state,
)

# Get current progress
summary = get_state_summary(Path("."))
tasks_done = summary["tasks_done"]
tasks_total = summary["tasks_total"]

# Confirm with user
print(f"""
This will archive your current project state and start fresh.
Your data files will NOT be deleted.
Current progress: {tasks_done}/{tasks_total} tasks complete.

Are you sure? Type 'yes' to confirm.
""")

# After confirmation:
result = reset_state(Path("."), reason="User requested reset")

if result["reset_complete"]:
    print(f"""
============================================================
  PROJECT RESET COMPLETE
============================================================

  Previous state archived to: {result["archive_path"]}

  Your data files are preserved in data/
  Your outputs are preserved in outputs/

  Next steps:
    Type /project:interview to define your new approach.
============================================================
""")
```

## Archive Structure

```
project_state/
├── archive/
│   └── 2025-12-01_143022/
│       ├── spec.yaml
│       ├── plan.md
│       ├── status.json
│       ├── spec_history/
│       ├── logs/
│       ├── archive_reason.txt
│       └── archive_metadata.json
├── spec.yaml (removed)
├── plan.md (removed)
└── status.json (removed)
```

## Safety Features

- Archives are never automatically deleted
- Data files are never touched
- Output files are preserved
- User must confirm before reset
