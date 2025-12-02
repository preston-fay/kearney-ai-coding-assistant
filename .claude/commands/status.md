# /project:status - Show Project Status

Display current project state and progress.

## Usage

```
/project:status
```

## Workflow

1. **Load state:**
   ```python
   from core.state_manager import load_state, get_status_summary

   state = load_state()
   summary = get_status_summary()
   ```

2. **If no project:**
   ```
   No project initialized.

   Run /project:init to start a new project.
   ```

3. **Display status:**
   ```
   PROJECT STATUS
   ==============

   Project: {project_name}
   Template: {template}
   Phase: {current_phase}

   PROGRESS
   --------
   Completed: {done} / {total} tasks ({percentage}%)
   In Progress: {in_progress} task(s)
   Blocked: {blocked} task(s)

   CURRENT TASK
   ------------
   [{task_id}] {task_description}
   Status: {status}
   Started: {started_at}

   RECENT HISTORY
   --------------
   - {action} at {timestamp}
   - {action} at {timestamp}

   ARTIFACTS
   ---------
   - {artifact_path}
   - {artifact_path}

   NEXT STEPS
   ----------
   Run /project:execute to continue working.
   ```

## Detailed View

For more detail:
```
/project:status --verbose
```

Shows:
- All tasks with status
- Full history
- File listings

## Output

Displays project status to console. Does not modify state.
