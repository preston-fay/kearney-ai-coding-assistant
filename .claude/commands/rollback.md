---
name: rollback
description: Restore project state from archive or history
agent: @spec-editor
---

# /project:rollback

## Usage

```
/project:rollback spec 3        # Rollback spec to version 3
/project:rollback archive       # List available archives
/project:rollback archive 2     # Restore from archive #2
```

## Spec Version Rollback

Rollback spec.yaml to a previous version from spec_history/.

### Process

1. List available versions from spec_history/
2. Show diff between current and target version
3. Confirm with user
4. Replace spec.yaml with historical version
5. Increment version number (so history is preserved)
6. Suggest regenerating plan

### Implementation

```python
from core.spec_manager import load_spec, get_history, rollback

# List versions
history = get_history()
print("Available versions:")
for entry in history:
    print(f"  v{entry['version']}: {entry['timestamp']} - {entry.get('changes', 'No description')}")

# Rollback to specific version
rollback(target_version=3)
print("Spec rolled back to v3. Run /project:plan to regenerate execution plan.")
```

## Archive Rollback

Restore complete project state from a previous archive.

### Process

1. List available archives with dates and status
2. Show what will be restored
3. Confirm with user
4. Archive CURRENT state first (safety)
5. Restore files from selected archive
6. Report restored state

### Implementation

```python
from core.state_validator import (
    list_archives,
    restore_from_archive,
    get_state_summary,
)

# List archives
archives = list_archives(Path("."))

print("Available archives:")
for i, archive in enumerate(archives, 1):
    print(f"  {i}. {archive['name']}")
    if archive['reason']:
        print(f"     Reason: {archive['reason']}")
    print(f"     Files: {', '.join(archive['files'])}")

# Restore from archive (after confirmation)
result = restore_from_archive(
    Path("."),
    archive_name="2025-12-01_143022",
    archive_current=True  # Safety: archive current state first
)

if result["restored"]:
    print(f"""
============================================================
  ARCHIVE RESTORED
============================================================

  Restored from: {archive_name}
  Files restored: {', '.join(result['files'])}

  Your current state was archived to: {result['current_archived_to']}

  Run /project:status to see restored state.
============================================================
""")
```

## Output Format

### Listing Archives

```
Available Archives:
============================================================

  #1  2025-12-01_143022
      Reason: Project reset
      Files: spec.yaml, plan.md, status.json, spec_history/

  #2  2025-11-30_091500
      Reason: Before major requirements change
      Files: spec.yaml, status.json

============================================================

To restore: /project:rollback archive 1
```

### After Restore

```
============================================================
  ARCHIVE RESTORED
============================================================

  Source: 2025-12-01_143022

  Restored:
    - spec.yaml (v3)
    - plan.md
    - status.json (5/8 tasks complete)
    - spec_history/ (3 versions)

  Safety backup created: archive/2025-12-01_160000

  Run /project:status to continue from restored state.
============================================================
```

## Safety Features

- Current state is ALWAYS archived before restore
- Archives are never deleted
- User must confirm before restore
- Spec rollback preserves version history
