---
name: compact
description: Summarize and archive old context to free up space
agent: @router
---

# /project:compact

## Purpose

When a session runs long, context fills up. This command:
1. Summarizes completed work
2. Archives detailed logs
3. Resets to a clean state with full project awareness

## Behavior

1. **Generate Summary**
   - List all completed tasks with brief outcomes
   - Note key decisions made
   - Capture any blockers or issues

2. **Archive to Logs**
   - Write detailed session log to project_state/logs/sessions/session_{timestamp}.md
   - Include all outputs generated
   - Include any errors or warnings

3. **Reset Context**
   - Keep only: spec.yaml, status.json, current task context
   - Drop: Detailed conversation history, intermediate outputs

4. **Confirm**
   - Report: "Session compacted. {n} tasks summarized. Context freed.
     You're on task {current_task}. Type /project:execute to continue."

## Implementation

Use the session logger to compact:

```python
from core.session_logger import compact_session, get_current_session
from core.state_manager import get_next_task

# Get current task for continuity
next_task = get_next_task()
next_task_desc = next_task.description if next_task else "No pending tasks"

# Compact the session
result = compact_session(
    reason="User requested compaction",
    next_task=next_task_desc
)

# Report results
print(f"Session compacted. {result['tasks_completed']} tasks summarized.")
print(f"Log saved to: {result['log_path']}")
print(f"Next task: {next_task_desc}")
```

## When to Use

- When Claude mentions context is getting long
- When responses start getting slower
- Before starting a new phase
- At natural break points

## Automatic Trigger

If context exceeds 80% capacity, Claude should suggest:
"We've been working for a while. Run /project:compact to
summarize progress and free up context?"

## Output Format

```
============================================================
  SESSION COMPACTED
============================================================

  Tasks Summarized: 5
  Decisions Logged: 3
  Issues Tracked: 1 (0 open)

  Log saved to: project_state/logs/sessions/session_2025-12-01_143022.md

  Context has been reset. Project state preserved in:
  - project_state/spec.yaml
  - project_state/status.json

  Next task: 3.1 - Build recommendation slide deck

  Type /project:execute to continue working.
============================================================
```
