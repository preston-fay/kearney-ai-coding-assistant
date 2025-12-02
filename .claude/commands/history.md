# /project:history

---
name: history
description: View specification version history
agent: @spec-editor
---

View the specification changelog and manage version history.

## Usage

```
/project:history                      # Show changelog
/project:history --versions           # List all versions
/project:history --version 2          # Show specific version
/project:history --diff 1 3           # Compare two versions
/project:history --rollback 2         # Rollback to version
```

## Behavior

### Default (Show Changelog)

Display the changelog with all recorded changes:

```
SPECIFICATION CHANGELOG
=======================

## Version 4 (2025-12-01 15:30)
- Added executive_summary to deliverables
- Changed deck audience from c_suite to board

## Version 3 (2025-12-01 14:45)
- Added f1_score to validation metrics

## Version 2 (2025-12-01 12:00)
- Changed target from churn_90_days to churn_60_days
- Adjusted train/test split accordingly

## Version 1 (2025-12-01 10:30)
- Initial specification from interview

Current version: 4
```

### With --versions Flag

List all available versions:

```
AVAILABLE VERSIONS
==================

Version  | Date                | File
---------|---------------------|----------------------------------
v1       | 2025-12-01 10:30   | spec_history/spec_v1.yaml
v2       | 2025-12-01 12:00   | spec_history/spec_v2.yaml
v3       | 2025-12-01 14:45   | spec_history/spec_v3.yaml
v4       | (current)          | spec.yaml

Total: 4 versions
```

### With --version N Flag

Show a specific version's content:

```
/project:history --version 2

SPECIFICATION VERSION 2
=======================
Archived: 2025-12-01 12:00 UTC

PROJECT: acme-churn-model
TYPE: modeling
CLIENT: Acme Corporation

TARGET: churn_60_days
VALIDATION: time_based_split
METRICS: [auc_roc, precision_at_20pct, recall]

(Note: This is a historical version. Current version is 4.)
```

### With --diff Flag

Compare two versions:

```
/project:history --diff 2 4

COMPARISON: VERSION 2 vs VERSION 4
==================================

CHANGES IN meta:
~ deadline: 2025-12-10 -> 2025-12-15

CHANGES IN modeling:
~ target_variable: churn_60_days -> churn_90_days
+ validation.metrics: f1_score

CHANGES IN deliverables:
+ executive_summary (new deliverable)

Summary: 4 changes between versions
```

### With --rollback N Flag

Restore a previous version (creates new version with old content):

```
/project:history --rollback 2

WARNING: Rolling back to version 2 will:
- Archive current version (4) to history
- Create version 5 with content from version 2
- NOT delete any history (all versions preserved)

Changes that will be reverted:
- target_variable: churn_90_days -> churn_60_days
- Remove f1_score from metrics
- Remove executive_summary from deliverables

Proceed with rollback? (yes/no)
```

On confirmation:

```
Rolled back to version 2.

Current spec is now version 5 (with content from version 2).
All previous versions remain in history.

NOTE: The execution plan may need regeneration.
Run /project:plan to update.
```

## Core Engine Usage

```python
from core import (
    get_changelog,
    get_history,
    load_version,
    rollback_to_version,
    get_spec_summary,
)

# Show changelog
changelog = get_changelog()
print(changelog)

# List versions
history = get_history()
for h in history:
    print(f"v{h['version']}: {h['path']}")

# Load specific version
old_spec = load_version(2)
if old_spec:
    print(get_spec_summary(old_spec))

# Rollback
new_spec = rollback_to_version(2)
if new_spec:
    print(f"Rolled back. Now at version {new_spec.version}")
```

## History Storage

Versions are stored in:

```
project_state/
  spec.yaml              # Current version
  spec_history/
    spec_v1.yaml         # Version 1 archive
    spec_v2.yaml         # Version 2 archive
    spec_v3.yaml         # Version 3 archive
    changelog.md         # Human-readable changelog
```

## Error Handling

- If spec.yaml doesn't exist: "No specification found. Run /project:interview first."
- If no history exists: "No version history available yet."
- If version doesn't exist: "Version {N} not found. Available versions: 1, 2, 3"
- If rollback fails: "Could not rollback to version {N}. File may be corrupted."

## Rollback Safety

Rollback is non-destructive:
- Current version is archived before rollback
- A new version number is assigned
- All history is preserved
- You can always rollback the rollback

## Related Commands

- `/project:spec` - View current specification
- `/project:edit` - Modify specification
- `/project:interview` - Re-interview sections
- `/project:plan` - Regenerate execution plan
