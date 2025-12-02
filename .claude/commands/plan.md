# /project:plan - Generate Execution Plan

Generate a detailed execution plan based on intake requirements.

## Usage

```
/project:plan
```

## Prerequisites

- Project initialized (`/project:init`)
- Requirements captured (`/project:intake`)

## Workflow

1. **Route to @planner agent:**
   ```
   [ROUTING TO: @planner]
   [CONTEXT: project_state/intake.yaml, data/raw/**]
   ```

2. **@planner analyzes requirements:**
   - Reads intake.yaml
   - Profiles data sources (if analytics)
   - Identifies required tasks

3. **Generate plan.md:**
   - Creates phased execution plan
   - Each task is specific and actionable
   - Includes validation steps

4. **Initialize task tracker:**
   ```python
   from core.state_manager import init_from_plan

   state = init_from_plan(project_name, template)
   ```

5. **Present plan for approval:**
   ```
   Execution Plan Generated

   Phase 1: Data Preparation (3 tasks)
   Phase 2: Analysis (4 tasks)
   Phase 3: Visualization (3 tasks)
   Phase 4: Documentation (2 tasks)
   Phase 5: Review & Export (2 tasks)

   Total: 14 tasks

   Review the plan at: project_state/plan.md

   Approve this plan? (yes/no)
   ```

6. **On approval, update state:**
   ```python
   from core.state_manager import mark_plan_approved
   mark_plan_approved()
   ```

7. **Confirm:**
   ```
   Plan approved and ready for execution.

   Next step: Run /project:execute to start working on tasks.
   ```

## Plan Format

```markdown
# Execution Plan: {project_name}

Generated: {timestamp}
Template: {template}

## Phase 1: Data Preparation
- [ ] Profile sales_q4.csv dataset
- [ ] Profile regions.xlsx dataset
- [ ] Clean and validate data

## Phase 2: Analysis
- [ ] Calculate revenue by region
- [ ] Calculate YoY growth rates
- [ ] Identify top performers

## Phase 3: Visualization
- [ ] Create revenue by region bar chart
- [ ] Create growth comparison chart

## Phase 4: Documentation
- [ ] Generate analysis summary
- [ ] Create executive presentation

## Phase 5: Review & Export
- [ ] Run brand compliance check
- [ ] Export final deliverables
```

## Output

Creates:
- `project_state/plan.md` with execution plan
- Updates `project_state/status.json` with parsed tasks
