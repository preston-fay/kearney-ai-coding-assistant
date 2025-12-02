# /project:review - Run Brand Compliance Check

Validate all outputs against Kearney Design System rules.

## Usage

```
/project:review
```

## Prerequisites

- At least one output generated in `outputs/` or `exports/`

## Workflow

1. **Route to @kds-reviewer agent:**
   ```
   [ROUTING TO: @kds-reviewer]
   [CONTEXT: outputs/**, exports/**, config/governance/brand.yaml]
   ```

2. **Run automated checks:**
   ```python
   from core.brand_guard import check_directory, format_violations

   output_violations = check_directory('outputs/')
   export_violations = check_directory('exports/')

   all_violations = output_violations + export_violations
   ```

3. **Display results:**

   If PASS:
   ```
   BRAND COMPLIANCE CHECK
   ======================

   Status: PASS

   Files Scanned:
   - outputs/charts/: {count} files
   - exports/: {count} files

   Violations: 0

   All outputs are KDS-compliant.

   Next step: Run /project:export to generate final deliverables.
   ```

   If FAIL:
   ```
   BRAND COMPLIANCE CHECK
   ======================

   Status: FAIL

   Files Scanned:
   - outputs/charts/: {count} files
   - exports/: {count} files

   Violations Found: {count}

   VIOLATION DETAILS
   -----------------
   [FORBIDDEN_COLOR] outputs/charts/revenue.png
     Image contains significant green content (12% of sampled pixels).

   [NO_EMOJIS] outputs/reports/summary.md:15
     Emoji detected: (star emoji)

   REQUIRED ACTIONS
   ----------------
   1. Regenerate revenue.png using KDSChart (purple palette only)
   2. Remove emoji from summary.md line 15

   Fix these issues and run /project:review again.
   ```

4. **Update state on pass:**
   ```python
   from core.state_manager import load_state, save_state

   state = load_state()
   state.history.append({
       'action': 'review_passed',
       'timestamp': '...'
   })
   save_state(state)
   ```

## What Gets Checked

### Colors
- No green colors (any shade)
- No unapproved hues
- Kearney Purple (#7823DC) used correctly

### Content
- No emojis in any text
- Proper typography references

### Charts (via image sampling)
- No green pixels > 5% threshold
- Dark backgrounds present

### Code Files
- No gridline enablement
- No forbidden color constants

## Output

- Displays compliance report
- Updates state if passed
- Lists specific fixes if failed
