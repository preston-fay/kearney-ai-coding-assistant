# Kearney AI Coding Assistant - Test Plan

## Overview

This document provides a systematic test plan to validate the KACA system works end-to-end before release to consultants.

**Tester**: Preston Fay (or designated QA)  
**Environment**: macOS / Windows 10+  
**Duration**: ~2-3 hours for full validation

---

# Phase 1: Prerequisites & Scaffolding

## Test 1.1: Prerequisite Checker

**Purpose**: Verify prereq_checker.py catches missing dependencies

| Step | Action | Expected Result | Pass? |
|------|--------|-----------------|-------|
| 1 | Run `python core/prereq_checker.py` | Shows all checks with pass/fail | |
| 2 | Verify Python version check | Shows Python 3.10+ ✓ | |
| 3 | Verify Git check | Shows Git installed ✓ | |
| 4 | Verify Claude Desktop check | Shows installed or gives install instructions | |
| 5 | Verify package check | Shows all packages ✓ or lists missing | |

**Notes**:
```
_________________________________________________________________
_________________________________________________________________
```

## Test 1.2: Project Scaffolding

**Purpose**: Verify scaffold.py creates correct project structure

| Step | Action | Expected Result | Pass? |
|------|--------|-----------------|-------|
| 1 | Run `python scaffold.py test-project-1 --path /tmp/` | Project created message | |
| 2 | Check `/tmp/test-project-1/` exists | Directory exists | |
| 3 | Check `CLAUDE.md` copied | File exists, matches template | |
| 4 | Check `.claude/` copied | Directory exists with agents/commands | |
| 5 | Check `core/` symlinked (or copied) | Points to template or copied | |
| 6 | Check `config/` symlinked (or copied) | Points to template or copied | |
| 7 | Check `project_state/` created | Empty directory with subdirs | |
| 8 | Check `data/raw/`, `data/processed/` created | Empty directories exist | |
| 9 | Check `outputs/`, `exports/` created | Empty directories exist | |
| 10 | Check `.gitignore` created | Contains data protection rules | |
| 11 | Check `.kaca-version.json` created | Contains template version | |
| 12 | Check `README.md` generated | Project-specific README | |

**Notes**:
```
_________________________________________________________________
_________________________________________________________________
```

## Test 1.3: Scaffold Edge Cases

| Step | Action | Expected Result | Pass? |
|------|--------|-----------------|-------|
| 1 | Run scaffold with existing project name | Error: "Project already exists" | |
| 2 | Run `scaffold.py test-2 --no-symlinks` | Files copied instead of symlinked | |
| 3 | Run `scaffold.py test-3 --skip-checks` | Skips prereqs (with warning) | |

**Notes**:
```
_________________________________________________________________
_________________________________________________________________
```

---

# Phase 2: Interview System

## Test 2.1: Interview Launch

**Setup**: Open scaffolded project in Claude Desktop

| Step | Action | Expected Result | Pass? |
|------|--------|-----------------|-------|
| 1 | Type `/interview` | Claude asks for project type (1-8 list) | |
| 2 | Verify all 8 types listed | Data Eng, Modeling, Analytics, Presentation, Proposal, Dashboard, Webapp, Research | |

**Notes**:
```
_________________________________________________________________
_________________________________________________________________
```

## Test 2.2: Modeling Interview (Full Flow)

**Purpose**: Test most complex interview tree

| Step | Action | Expected Result | Pass? |
|------|--------|-----------------|-------|
| 1 | Select "2" (Statistical/ML Model) | Claude asks business question | |
| 2 | Answer: "Predict customer churn" | Claude probes for elaboration | |
| 3 | Elaborate on use case | Claude asks problem type | |
| 4 | Select "Classification" | Claude asks target variable | |
| 5 | Answer: "churned_90_days" | Claude asks about class balance | |
| 6 | Answer: "Highly imbalanced, 8%" | Claude moves to data questions | |
| 7 | Describe data sources | Claude asks about volume, quality | |
| 8 | Complete data section | Claude moves to features | |
| 9 | Complete features section | Claude moves to validation | |
| 10 | Complete validation section | Claude moves to interpretability | |
| 11 | Answer interpretability questions | Claude moves to deliverables | |
| 12 | Select deliverables | Claude shows summary | |
| 13 | Confirm "yes" | spec.yaml saved message | |
| 14 | Check `project_state/spec.yaml` | File exists with all captured data | |
| 15 | Check spec has `modeling:` section | Type-specific section present | |

**Notes**:
```
_________________________________________________________________
_________________________________________________________________
```

## Test 2.3: Presentation Interview (Different Flow)

**Purpose**: Verify different interview tree works

| Step | Action | Expected Result | Pass? |
|------|--------|-----------------|-------|
| 1 | Start new project, `/interview` | Type selection | |
| 2 | Select "4" (Presentation/Deck) | Claude asks about purpose | |
| 3 | Complete presentation interview | Different questions than modeling | |
| 4 | Confirm and save | spec.yaml has `presentation:` section | |

**Notes**:
```
_________________________________________________________________
_________________________________________________________________
```

## Test 2.4: Interview Conditional Logic

**Purpose**: Verify conditions skip/show appropriate questions

| Step | Action | Expected Result | Pass? |
|------|--------|-----------------|-------|
| 1 | In modeling interview, select "Clustering" | Should NOT ask about target variable | |
| 2 | In modeling interview, select "Classification" | SHOULD ask about class balance | |
| 3 | In modeling interview, say interpretability not required | Should NOT ask about compliance | |

**Notes**:
```
_________________________________________________________________
_________________________________________________________________
```

---

# Phase 3: Spec Management

## Test 3.1: View Spec

| Step | Action | Expected Result | Pass? |
|------|--------|-----------------|-------|
| 1 | After interview, type `/spec` | Shows full spec.yaml content | |
| 2 | Type `/spec --section modeling` | Shows only modeling section | |

**Notes**:
```
_________________________________________________________________
_________________________________________________________________
```

## Test 3.2: Edit Spec

| Step | Action | Expected Result | Pass? |
|------|--------|-----------------|-------|
| 1 | Type `/edit` | Claude asks what to change | |
| 2 | Say "Change target variable to churn_60_days" | Claude shows change, asks confirm | |
| 3 | Confirm | spec.yaml updated, version incremented | |
| 4 | Check `project_state/spec_history/` | Previous version saved | |
| 5 | Check `changelog.md` | Change logged | |

**Notes**:
```
_________________________________________________________________
_________________________________________________________________
```

## Test 3.3: Spec History & Rollback

| Step | Action | Expected Result | Pass? |
|------|--------|-----------------|-------|
| 1 | Type `/history` | Shows changelog | |
| 2 | Type `/history --version 1` | Shows version 1 spec | |
| 3 | Type `/project:rollback spec 1` | Asks for confirmation | |
| 4 | Confirm | Spec restored to v1, new version created | |

**Notes**:
```
_________________________________________________________________
_________________________________________________________________
```

---

# Phase 4: Planning & Execution

## Test 4.1: Plan Generation

| Step | Action | Expected Result | Pass? |
|------|--------|-----------------|-------|
| 1 | Type `/plan` | Claude generates phased plan | |
| 2 | Check `project_state/plan.md` | Plan file created | |
| 3 | Check `project_state/status.json` | Status file with tasks | |
| 4 | Verify tasks match spec | Tasks reflect requirements | |

**Notes**:
```
_________________________________________________________________
_________________________________________________________________
```

## Test 4.2: Task Execution

| Step | Action | Expected Result | Pass? |
|------|--------|-----------------|-------|
| 1 | Type `/execute` | Claude identifies next task | |
| 2 | Let Claude execute task | Task completed, output generated | |
| 3 | Check `status.json` updated | Task marked "done" | |
| 4 | Type `/status` | Shows progress, next task | |
| 5 | Execute another task | Progress increments | |

**Notes**:
```
_________________________________________________________________
_________________________________________________________________
```

## Test 4.3: Session Resume

| Step | Action | Expected Result | Pass? |
|------|--------|-----------------|-------|
| 1 | Close Claude Desktop | Session ends | |
| 2 | Re-open project in Claude Desktop | Session starts fresh | |
| 3 | Claude should detect existing project | Shows status, offers to continue | |
| 4 | Type `/status` | Shows correct progress | |
| 5 | Type `/execute` | Continues from correct task | |

**Notes**:
```
_________________________________________________________________
_________________________________________________________________
```

---

# Phase 5: Data Handling

## Test 5.1: Small File Handling

| Step | Action | Expected Result | Pass? |
|------|--------|-----------------|-------|
| 1 | Copy small CSV (<10MB) to `data/raw/` | File in place | |
| 2 | Ask Claude to analyze it | Claude uses pandas, provides analysis | |
| 3 | Check output generated | Chart or report in outputs/ | |

**Notes**:
```
_________________________________________________________________
_________________________________________________________________
```

## Test 5.2: Large File Handling (DuckDB)

| Step | Action | Expected Result | Pass? |
|------|--------|-----------------|-------|
| 1 | Copy large CSV (>100MB) to `data/raw/` | File in place | |
| 2 | Ask Claude to analyze it | Claude uses DuckDB | |
| 3 | Verify `data/project.duckdb` created | Database file exists | |
| 4 | Ask Claude to run SQL query | Query executes efficiently | |

**Notes**:
```
_________________________________________________________________
_________________________________________________________________
```

---

# Phase 6: Quality Control

## Test 6.1: Brand Guard - Charts

| Step | Action | Expected Result | Pass? |
|------|--------|-----------------|-------|
| 1 | Generate a chart via `/execute` | Chart created in outputs/charts/ | |
| 2 | Verify chart uses Kearney Purple | Primary color is #7823DC | |
| 3 | Verify no gridlines | Chart has no gridlines | |
| 4 | Verify data labels outside | Labels not inside bars/slices | |

**Notes**:
```
_________________________________________________________________
_________________________________________________________________
```

## Test 6.2: Brand Guard - Violations

| Step | Action | Expected Result | Pass? |
|------|--------|-----------------|-------|
| 1 | Manually create file with green (#00FF00) in outputs/ | File in place | |
| 2 | Run `/review` | Brand violation detected | |
| 3 | Check QC report generated | `outputs/reports/qc_report.md` exists | |
| 4 | Verify violation listed | Green color flagged | |

**Notes**:
```
_________________________________________________________________
_________________________________________________________________
```

## Test 6.3: QC Report

| Step | Action | Expected Result | Pass? |
|------|--------|-----------------|-------|
| 1 | Type `/review` | QC check runs | |
| 2 | Check `outputs/reports/qc_report.md` | Report generated | |
| 3 | Verify report sections | Brand, Chart Quality, Data Compliance, Recommendations | |

**Notes**:
```
_________________________________________________________________
_________________________________________________________________
```

---

# Phase 7: Export

## Test 7.1: Export Generation

| Step | Action | Expected Result | Pass? |
|------|--------|-----------------|-------|
| 1 | Type `/export` | Human review warning displayed | |
| 2 | Confirm export | Files generated in exports/ | |
| 3 | Check `exports/manifest.json` | Manifest with file list, QC status | |
| 4 | Check `project_state/logs/exports/export_log.jsonl` | Export logged | |

**Notes**:
```
_________________________________________________________________
_________________________________________________________________
```

## Test 7.2: Human Review Warning

| Step | Action | Expected Result | Pass? |
|------|--------|-----------------|-------|
| 1 | On `/export` | Warning box appears | |
| 2 | Warning includes responsibility notice | "YOU are responsible for reviewing" | |
| 3 | Post-export shows checklist | Review checklist displayed | |

**Notes**:
```
_________________________________________________________________
_________________________________________________________________
```

---

# Phase 8: Error Recovery

## Test 8.1: Project Reset

| Step | Action | Expected Result | Pass? |
|------|--------|-----------------|-------|
| 1 | Type `/project:reset` | Confirmation prompt | |
| 2 | Confirm | Archive created in `project_state/archive/` | |
| 3 | Check spec.yaml cleared/reset | Ready for new interview | |
| 4 | Check data/ intact | Data files NOT deleted | |
| 5 | Check outputs/ intact | Previous outputs still there | |

**Notes**:
```
_________________________________________________________________
_________________________________________________________________
```

## Test 8.2: State Validation

| Step | Action | Expected Result | Pass? |
|------|--------|-----------------|-------|
| 1 | Manually corrupt spec.yaml (delete required field) | File corrupted | |
| 2 | Type `/status` | Validation error detected | |
| 3 | System offers repair or rollback | Recovery options presented | |

**Notes**:
```
_________________________________________________________________
_________________________________________________________________
```

## Test 8.3: Rollback from Archive

| Step | Action | Expected Result | Pass? |
|------|--------|-----------------|-------|
| 1 | After reset, type `/project:rollback archive` | List of archives shown | |
| 2 | Select archive to restore | Confirmation prompt | |
| 3 | Confirm | Previous state restored | |
| 4 | Verify spec.yaml restored | Content matches archived version | |

**Notes**:
```
_________________________________________________________________
_________________________________________________________________
```

---

# Phase 9: Session Management

## Test 9.1: Session Compaction

| Step | Action | Expected Result | Pass? |
|------|--------|-----------------|-------|
| 1 | After extended work, type `/project:compact` | Session summary generated | |
| 2 | Check `project_state/logs/sessions/` | Session log file created | |
| 3 | Verify context freed | Claude confirms context compacted | |
| 4 | Type `/execute` | Work continues from correct task | |

**Notes**:
```
_________________________________________________________________
_________________________________________________________________
```

---

# Phase 10: Audit Trail

## Test 10.1: Command Logging

| Step | Action | Expected Result | Pass? |
|------|--------|-----------------|-------|
| 1 | Run several commands | Commands execute | |
| 2 | Check `project_state/logs/commands/command_log.jsonl` | Log file exists | |
| 3 | Verify entries | Each command logged with timestamp | |

**Notes**:
```
_________________________________________________________________
_________________________________________________________________
```

---

# Phase 11: Skills Integration

## Test 11.1: Skill Reference on Output

| Step | Action | Expected Result | Pass? |
|------|--------|-----------------|-------|
| 1 | Ask Claude to create a PowerPoint | Claude references pptx skill | |
| 2 | Ask Claude to create a chart | Claude references visualization skill | |
| 3 | Ask Claude to write markdown doc | Claude references markdown skill | |

**Notes**:
```
_________________________________________________________________
_________________________________________________________________
```

---

# Phase 12: Branding Override

## Test 12.1: Client Branding

| Step | Action | Expected Result | Pass? |
|------|--------|-----------------|-------|
| 1 | Copy `brand_override.yaml.template` to `config/brand_override.yaml` | File in place | |
| 2 | Edit with custom client colors | Custom colors set | |
| 3 | Generate a chart | Chart uses client colors | |
| 4 | Verify enforced rules still apply | No gridlines, labels outside | |

**Notes**:
```
_________________________________________________________________
_________________________________________________________________
```

---

# Summary & Sign-Off

## Test Summary

| Phase | Tests | Passed | Failed | Notes |
|-------|-------|--------|--------|-------|
| 1. Prerequisites & Scaffolding | 15 | | | |
| 2. Interview System | 19 | | | |
| 3. Spec Management | 9 | | | |
| 4. Planning & Execution | 10 | | | |
| 5. Data Handling | 7 | | | |
| 6. Quality Control | 10 | | | |
| 7. Export | 6 | | | |
| 8. Error Recovery | 9 | | | |
| 9. Session Management | 4 | | | |
| 10. Audit Trail | 3 | | | |
| 11. Skills Integration | 3 | | | |
| 12. Branding Override | 4 | | | |
| **TOTAL** | **99** | | | |

## Critical Issues Found

```
_________________________________________________________________
_________________________________________________________________
_________________________________________________________________
```

## Sign-Off

| Role | Name | Date | Signature |
|------|------|------|-----------|
| Tester | | | |
| Developer | | | |
| Approver | | | |

---

**v1.0 Release Criteria**: All critical path tests (Phases 1-8) must pass. Phases 9-12 are important but can have minor issues for initial release.
