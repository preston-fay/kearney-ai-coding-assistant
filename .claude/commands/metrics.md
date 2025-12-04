# /metrics

---
name: metrics
description: Display telemetry metrics and usage report
---

Displays telemetry metrics for the current project or globally.

## Usage

```
/metrics [--global] [--since=DATE]
```

## Options

- `--global`: Show metrics across all projects
- `--since=DATE`: Only include events after DATE (ISO format)

## Behavior

1. Load events from `project_state/events.jsonl` (or `~/.kaca/global_events.jsonl` if --global)
2. Compute metrics using `Telemetry.compute_metrics()`
3. Display formatted summary report

## Implementation

```python
from core.telemetry import Telemetry
from datetime import datetime
from pathlib import Path

# Determine which events to load
if '--global' in args:
    events = Telemetry.load_events(Telemetry._get_global_path())
    print("Global Metrics (all projects)")
else:
    events = Telemetry.load_events()
    print("Project Metrics")

# Filter by date if specified
if '--since' in args:
    since_str = args.split('--since=')[1].split()[0]
    since = datetime.fromisoformat(since_str)
    events = [e for e in events if datetime.fromisoformat(e.timestamp) >= since]

# Generate and display report
report = Telemetry.get_summary_report(events)
print(report)
```

## Example Output

```
==================================================
KACA TELEMETRY REPORT
==================================================

USAGE METRICS
------------------------------
Total sessions: 12
Total commands: 47
Total artifacts: 23
Total exports: 8

Avg session duration: 342.5s
Avg task duration: 15.2s

QUALITY METRICS
------------------------------
Brand compliance rate: 94.3%
Task success rate: 97.8%
Spec edit count: 3

COMMANDS BY TYPE
------------------------------
  /execute: 18
  /interview: 5
  /plan: 4
  /review: 4
  /export: 3

ARTIFACTS BY TYPE
------------------------------
  png: 12
  pptx: 6
  docx: 3
  xlsx: 2

==================================================
```
