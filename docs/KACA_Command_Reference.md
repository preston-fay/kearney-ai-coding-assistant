# Kearney AI Coding Assistant - Command Reference

## Quick Reference Card

```
┌─────────────────────────────────────────────────────────────────────────┐
│                KEARNEY AI CODING ASSISTANT COMMANDS                     │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  CORE WORKFLOW                                                          │
│  ─────────────                                                          │
│  /interview     Define project requirements (start here)        │
│  /plan          Generate execution plan                         │
│  /execute       Run the next task                               │
│  /status        Show current progress                           │
│  /review        Check brand compliance                          │
│  /export        Generate final deliverables                     │
│                                                                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  REQUIREMENTS MANAGEMENT                                                │
│  ───────────────────────                                                │
│  /spec          View current requirements                       │
│  /edit          Change requirements                             │
│  /history       View requirement changes                        │
│                                                                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ERROR RECOVERY                                                         │
│  ──────────────                                                         │
│  /project:reset         Archive and start fresh                         │
│  /project:rollback      Restore previous state                          │
│  /project:compact       Free up context (long sessions)                 │
│                                                                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  HELP                                                                   │
│  ────                                                                   │
│  /help          Show all commands                               │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Detailed Command Reference

### /interview

**Purpose**: Define your project requirements through guided conversation

**Usage**:
```
/interview                    # Start new interview
/interview --type modeling    # Start with specific type
/interview --section data     # Re-interview specific section
/interview --continue         # Resume interrupted interview
```

**When to use**: 
- Starting a new project
- Redefining a project after major pivot
- Revisiting specific sections

**Output**: Creates/updates `project_state/spec.yaml`

---

### /plan

**Purpose**: Generate an execution plan from your requirements

**Usage**:
```
/plan                         # Generate plan
/plan --regenerate            # Force regenerate (after spec changes)
```

**When to use**:
- After completing interview
- After significant spec changes

**Output**: 
- Creates `project_state/plan.md`
- Creates `project_state/status.json`

---

### /execute

**Purpose**: Execute the next pending task from your plan

**Usage**:
```
/execute                      # Run next task
/execute --task 2.3           # Run specific task
```

**When to use**:
- Building your project (repeat until done)
- Resuming after a break

**Output**: 
- Work products in `outputs/` or `exports/`
- Updates `status.json`

---

### /status

**Purpose**: Show current project progress and state

**Usage**:
```
/status                       # Show status summary
/status --detailed            # Show all tasks
```

**When to use**:
- Checking where you are
- Resuming a project
- Before meetings to know progress

**Output**: Progress summary, completed tasks, next task

**Example output**:
```
Project: acme-churn-model
Phase: Phase 2: Model Development
Progress: 5/12 tasks complete (42%)
Next task: 2.3 - Train classification model

Recent:
  ✓ 2.1 - Profile training data
  ✓ 2.2 - Engineer features
  → 2.3 - Train classification model (next)
  ○ 2.4 - Validate on holdout
```

---

### /review

**Purpose**: Run brand compliance and quality checks

**Usage**:
```
/review                       # Check all outputs
/review --fix                 # Auto-fix simple issues
```

**When to use**:
- Before exporting
- After generating charts/visuals
- When you want QC assurance

**Output**: Creates `outputs/reports/qc_report.md`

**Checks performed**:
- Kearney color palette (flags green)
- Typography (correct fonts)
- Chart formatting (gridlines, labels)
- Data compliance (no PII exposure)

---

### /export

**Purpose**: Generate final client-ready deliverables

**Usage**:
```
/export                       # Export all deliverables
/export --type presentation   # Export specific type
```

**When to use**:
- Project is complete
- Ready for client delivery

**Output**:
- Deliverables in `exports/`
- Creates `exports/manifest.json`
- Logs to `project_state/logs/exports/`

**Important**: Human review required before sending to client!

---

### /spec

**Purpose**: View current project requirements

**Usage**:
```
/spec                         # Show full spec
/spec --section modeling      # Show specific section
/spec --section meta          # Show project metadata
/spec --diff                  # Show changes from last version
```

**When to use**:
- Reviewing what you defined
- Checking specific requirements
- Before planning to verify accuracy

---

### /edit

**Purpose**: Modify project requirements

**Usage**:
```
/edit                         # Open edit mode
/edit modeling.target_variable  # Edit specific field
/edit --section deliverables  # Edit entire section
```

**When to use**:
- Requirements change
- Fix mistakes from interview
- Add something you forgot

**Example**:
```
You:    /edit

Claude: What would you like to change?

You:    Change the target variable to churn_60_days instead of churn_90_days

Claude: I'll update:
        - modeling.target_variable: churn_90_days → churn_60_days
        - modeling.target_definition: Updated to reflect 60-day window
        
        This affects validation since observation window changes.
        Proceed? (yes/no)

You:    yes

Claude: Updated. spec.yaml is now version 2.
```

---

### /history

**Purpose**: View requirement change history

**Usage**:
```
/history                      # Show changelog
/history --version 2          # Show specific version
/history --diff 1 2           # Compare versions
```

**When to use**:
- Reviewing what changed
- Before rollback to see options
- Audit trail

---

### /project:reset

**Purpose**: Archive current state and start fresh

**Usage**:
```
/project:reset                        # Reset with confirmation
/project:reset --keep-outputs         # Keep generated files
```

**When to use**:
- Major project pivot
- Want to try different approach
- Corrupted state

**What happens**:
1. Current spec, plan, status archived to `project_state/archive/{timestamp}/`
2. State files cleared
3. Data and outputs preserved
4. Ready for new `/interview`

---

### /project:rollback

**Purpose**: Restore previous project state

**Usage**:
```
/project:rollback spec 2              # Rollback spec to version 2
/project:rollback archive             # List available archives
/project:rollback archive 1           # Restore from archive #1
```

**When to use**:
- Edit went wrong
- Want to undo changes
- Restore after accidental reset

---

### /project:compact

**Purpose**: Summarize work and free up context for long sessions

**Usage**:
```
/project:compact                      # Compact current session
```

**When to use**:
- Claude mentions context is long
- Responses getting slower
- Before starting new phase
- Natural break points

**What happens**:
1. Completed work summarized
2. Session log written to `project_state/logs/sessions/`
3. Context freed
4. State preserved for continuation

---

### /help

**Purpose**: Show available commands

**Usage**:
```
/help                         # Show all commands
/help interview               # Help for specific command
```

---

## Command Flow Cheat Sheet

### Starting a New Project
```
/interview → /plan → /execute (repeat)
```

### Resuming Work
```
/status → /execute (repeat)
```

### Changing Requirements
```
/edit → /plan --regenerate → /execute
```

### Quality Check & Export
```
/review → (fix issues) → /export
```

### Recovery
```
/project:rollback spec 1    # Undo spec change
/project:reset              # Start completely over
```

---

## Keyboard Shortcuts

None currently - all commands are typed. Consider creating aliases in your shell:

```bash
# Add to ~/.bashrc or ~/.zshrc
alias pi='/interview'
alias pp='/plan'
alias pe='/execute'
alias ps='/status'
```

---

*Kearney Digital & Analytics*
