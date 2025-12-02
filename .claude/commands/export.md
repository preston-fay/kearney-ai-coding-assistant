# /project:export - Generate Final Deliverables

Generate and export final deliverables (presentations, reports).

## Usage

```
/project:export
```

## Prerequisites

- Brand compliance check passed (`/project:review`)

## Workflow

1. **Verify review status:**
   ```python
   from core.state_manager import load_state

   state = load_state()
   review_passed = any(
       h['action'] == 'review_passed'
       for h in state.history
   )
   ```

   If not passed:
   ```
   Brand compliance review required before export.

   Run /project:review first.
   ```

2. **Route to @presentation-builder:**
   ```
   [ROUTING TO: @presentation-builder]
   [CONTEXT: outputs/**, project_state/intake.yaml]
   ```

3. **Build presentation:**
   ```python
   from core.slide_engine import KDSPresentation

   pres = KDSPresentation()

   # Add slides based on intake requirements
   pres.add_title_slide(...)
   pres.add_content_slide(...)
   pres.add_chart_slide(...)
   pres.add_closing_slide(...)

   pres.save('exports/{project_name}.pptx')
   ```

4. **Run final validation:**
   ```python
   from core.brand_guard import check_file

   violations = check_file('exports/{project_name}.pptx')
   ```

5. **Record artifact:**
   ```python
   from core.state_manager import add_artifact
   add_artifact('exports/{project_name}.pptx')
   ```

6. **Generate export manifest:**
   ```python
   from core.audit_logger import create_export_manifest, log_export
   from pathlib import Path

   # Collect deliverable info
   deliverables = [
       {"filename": "{project_name}.pptx", "type": "presentation", "slides": slide_count}
   ]

   # Get QC summary from review step
   qc_summary = {
       "all_passed": True,
       "checks_run": ["colors", "emojis", "gridlines", "pii"],
       "violations": 0
   }

   # Create manifest.json in exports/
   manifest_path = create_export_manifest(Path("."), deliverables, qc_summary)
   ```

7. **Log export to audit trail:**
   ```python
   # Log to project_state/logs/exports/export_log.jsonl
   log_export(
       Path("."),
       files=["{project_name}.pptx", "manifest.json"],
       qc_passed=True,
       human_review=True  # Always requires human review
   )
   ```

8. **Update state:**
   ```python
   state.history.append({
       'action': 'export_complete',
       'timestamp': '...'
   })
   save_state(state)
   ```

9. **Confirm export with human review warning:**
   ```
   EXPORT COMPLETE
   ===============

   Deliverables generated:
   - exports/{project_name}.pptx ({slide_count} slides)
   - exports/manifest.json (export metadata)

   File location: exports/

   +---------------------------------------------------------+
   |  HUMAN REVIEW REQUIRED                                  |
   |  All AI-generated deliverables must be reviewed by a    |
   |  qualified consultant before client delivery.           |
   +---------------------------------------------------------+

   Export logged to: project_state/logs/exports/export_log.jsonl

   Project Status: COMPLETE (pending review)
   ```

## Export Options

### Presentation Only
```
/project:export --presentation
```

### Report Only
```
/project:export --report
```

### All Deliverables
```
/project:export --all
```

## Output Contents

The exported presentation includes:
- Title slide with project name and client
- Executive summary of key findings
- All charts from outputs/charts/
- Data tables where applicable
- Recommendations and next steps
- Closing slide with contact info

## Output

Creates:
- `exports/{project_name}.pptx` - Final presentation
- `exports/manifest.json` - Export metadata with checksums
- `project_state/logs/exports/export_log.jsonl` - Audit trail entry
- Updates project_state/status.json
- Marks project as complete (pending human review)
