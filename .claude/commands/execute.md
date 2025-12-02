# /project:execute - Execute Next Task

Execute the next pending task from the project plan.

## Usage

```
/project:execute
```

## Prerequisites

- Plan generated and approved (`/project:plan`)

## Workflow

1. **Route to @steward agent:**
   ```
   [ROUTING TO: @steward]
   [CONTEXT: project_state/status.json, project_state/plan.md]
   ```

2. **@steward loads current state:**
   ```python
   from core.state_manager import load_state, get_next_task

   state = load_state()
   task = get_next_task()
   ```

3. **If no pending tasks:**
   ```
   All tasks complete!

   Progress: {done}/{total} tasks (100%)

   Next step: Run /project:review for brand compliance check.
   ```

4. **Mark task in progress:**
   ```python
   from core.state_manager import update_task_status
   update_task_status(task.id, 'in_progress')
   ```

5. **Execute task using core/ modules:**
   - Data tasks: Use `core.data_profiler`
   - Chart tasks: Use `core.chart_engine`
   - Slide tasks: Use `core.slide_engine`

6. **Record artifacts:**
   ```python
   from core.state_manager import add_artifact
   add_artifact('outputs/charts/revenue.png')
   ```

7. **Mark task complete:**
   ```python
   update_task_status(task.id, 'done')
   ```

8. **Report status:**
   ```
   Task {id} complete: {description}
   Artifact: {path}

   Progress: {done}/{total} tasks ({percentage}%)
   Next task: {next_description}

   Run /project:execute again to continue.
   ```

## Error Handling

If task cannot be completed:

```python
update_task_status(task.id, 'blocked', blocked_reason='...')
```

Report:
```
Task {id} blocked: {description}
Reason: {blocked_reason}

Suggested resolution: {suggestion}
```

## Batch Execution

To execute multiple tasks:
```
/project:execute --all
```

This will loop through all pending tasks until complete or blocked.

## Output

- Executes one task
- Creates artifacts in outputs/ or exports/
- Updates project_state/status.json
