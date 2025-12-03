# /webapp

Generate an interactive web application from the project specification.

## Prerequisites

- `project_state/spec.yaml` must exist with `dashboard` or `webapp` project type
- Data files referenced in spec must be accessible
- For Streamlit tier: Python environment with streamlit installed
- For React tier: Node.js environment

## Workflow

1. **Read skill file**: `config/skills/kearney-webapp.md`
2. **Load specification**: `project_state/spec.yaml`
3. **Determine output tier** based on spec.delivery.output_tier:
   - If audience is "Client executives" -> Static HTML
   - If data_size is "Very large" (>10MB) -> Streamlit (needs live queries)
   - If audience is "Engineering team" -> React scaffold
   - Default -> Static HTML
4. **Initialize data layer**: `KDSData.from_spec()`
5. **Build application**: Using appropriate engine
6. **Validate output**: Run `brand_guard.check_file()` on generated files
7. **Report completion**: Provide file path and next steps

## Output Locations

| Tier | Location | Contents |
|------|----------|----------|
| Static HTML | `exports/{name}_dashboard.html` | Single self-contained file |
| Streamlit | `exports/{name}_app/` | `app.py`, `.streamlit/config.toml`, `requirements.txt` |
| React | `exports/{name}_react/` | Full Vite project scaffold |

## Usage

```
/webapp
```

No arguments. Uses current project specification.

## Tier Selection Logic

The command automatically selects the appropriate tier:

```
IF spec.delivery.audience == "Client executives":
    tier = "static_html"
ELIF spec.data.size == "Very large" OR data_file_size > 10MB:
    tier = "streamlit"
ELIF spec.delivery.audience == "Engineering team":
    tier = "react"
ELSE:
    tier = "static_html"
```

Override by explicitly setting `spec.delivery.output_tier` in the specification.

## Example Output

```
[ROUTING TO: @dashboard_builder]

Reading skill: config/skills/kearney-webapp.md
Loading spec: project_state/spec.yaml

Project: Sales Dashboard
Type: dashboard
Tier: static_html (audience: Client executives)

Initializing data layer...
  - sales: data/sales.csv (245 KB)

Building dashboard...
  - 3 metrics
  - 2 charts
  - 1 table
  - 2 filters

Validating output...
  Brand check: PASSED

Dashboard generated successfully

  Output: exports/sales_dashboard.html
  Size: 1.2 MB
  Brand check: PASSED

Next steps:
  - Open in browser to preview
  - Run /review for detailed compliance check
  - Run /export to package for delivery
```

## Related Commands

- `/interview` - Define project requirements first
- `/review` - Check brand compliance of generated output
- `/export` - Package for client delivery
- `/status` - Check current project state

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "No spec.yaml found" | Run `/interview` first to create specification |
| "Data file not found" | Check paths in spec.yaml datasets section |
| "Data too large for HTML" | Command will auto-switch to Streamlit tier |
| "Brand violations detected" | Warnings are logged; fix colors and regenerate |
