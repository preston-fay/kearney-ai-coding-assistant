# Kearney Web Application Skill

Best practices for generating web applications with KACA.

## Output Tier Selection Matrix

Choose the appropriate tier based on your requirements:

| Audience | Data Size | Refresh Need | Recommended Tier |
|----------|-----------|--------------|------------------|
| Client executives | Any | Static | **Static HTML** |
| Client executives | <10MB | Daily+ | Static HTML |
| Internal analysts | <10MB | Static | Static HTML |
| Internal analysts | Any | Real-time | **Streamlit** |
| Internal analysts | >10MB | Any | **Streamlit** |
| Engineering team | Any | Any | **React** |
| Production handoff | Any | Any | **React** |

### Tier Capabilities

| Feature | Static HTML | Streamlit | React |
|---------|-------------|-----------|-------|
| No setup required | Yes | No | No |
| Real-time data | No | Yes | Yes |
| Large datasets | <10MB | Unlimited | Unlimited |
| Interactive filters | Basic | Full | Full |
| Custom logic | No | Yes | Yes |
| Embeddable | Yes | Iframe | Yes |
| Offline capable | Yes | No | Yes (PWA) |

## Static HTML Rules

### Size Limits
- Maximum embedded data: 10MB
- Maximum file size: 15MB
- If exceeded, switch to Streamlit tier

### KPI Layout
- Maximum 6 KPIs above the fold
- Use 2-column grid on desktop
- Stack to 1-column on mobile

### Data Embedding
- All data embedded as JSON in `<script type="application/json">`
- No external data fetching
- Snapshot of data at generation time

## Brand Compliance (Non-Negotiable)

### Colors
- **Primary**: Kearney Purple `#7823DC` - all accents, buttons, highlights
- **FORBIDDEN**: Green colors - NEVER use `#00FF00`, `#008000`, `#2E7D32`, `#4CAF50`, or any green
- **Positive indicators**: Light purple `#D4A5FF` (not green)
- **Negative indicators**: Coral `#FF6F61`
- **Warning**: Amber `#FFB74D`
- **Info**: Light blue `#64B5F6`

### Background
- Dark mode default: `#1E1E1E`
- Surface/cards: `#2D2D2D`
- Light mode (if needed): `#FFFFFF`

### Chart Standards
- NO gridlines (KDS requirement)
- Data labels outside bars/slices
- Legend below chart, horizontal orientation
- Use theme chart palette for multiple series

## Typography Rules

### Font Family
```css
font-family: Inter, Arial, sans-serif;
```

### Font Weights
- Normal text: 400
- Labels/headings: 500
- Titles: 600

### Font Sizes
- Minimum: 12px (for accessibility)
- Body: 14px
- Large: 18px
- Titles: 24px-32px

### Line Height
- Body text: 1.6
- Headings: 1.2

## Layout Breakpoints

| Breakpoint | Width | Layout |
|------------|-------|--------|
| Desktop | >1200px | 2-column grid |
| Tablet | 768-1200px | 2-column, reduced spacing |
| Mobile | <768px | 1-column stack |
| Small mobile | <480px | Compact mode |

## File Naming Conventions

### Static HTML
```
exports/{project_name}_dashboard.html
```

### Streamlit
```
exports/{project_name}_app/
  app.py
  .streamlit/config.toml
  requirements.txt
  data/
  README.md
```

### React
```
exports/{project_name}_react/
  src/
    App.jsx
    components/
    data/
    styles/
  public/
  package.json
  vite.config.js
  README.md
```

## Pre-Delivery Checklist

Before delivering any web application:

- [ ] Brand guard validation passed (`python core/brand_guard.py exports/`)
- [ ] No green colors anywhere in output
- [ ] Kearney Purple (#7823DC) is primary color
- [ ] No gridlines on any charts
- [ ] Data labels outside bars/slices
- [ ] Inter font applied (or Arial fallback)
- [ ] Responsive layout tested at all breakpoints
- [ ] Footer contains "KACA | Kearney Digital & Analytics"
- [ ] File opens without console errors
- [ ] All charts render correctly
- [ ] Filters function as expected

## Data Recommendations

### When to use DuckDB

Consider DuckDB for your data source when:
- Dataset exceeds 10MB
- You need SQL query capabilities
- Data will be joined from multiple sources
- Performance is critical

Install with: `pip install duckdb`

### Data Validation

Always validate data sources before generation:
1. Confirm all required columns exist
2. Check for missing values in key columns
3. Verify data types match expectations
4. Test with sample queries

## Engine Usage

### Static HTML (KDSWebApp)

```python
from core import KDSTheme, KDSData, KDSWebApp

theme = KDSTheme()
data = KDSData.from_spec()

app = (
    KDSWebApp("Dashboard Title", theme=theme)
    .set_data(data)
    .add_metric("Revenue", "$1.2M", "+15%")
    .add_chart("sales", "bar", "region", "revenue", "By Region")
    .add_table("sales", "Details")
    .add_filter("sales", "region", "dropdown")
)

app.generate("exports/dashboard.html")
```

### Streamlit (KDSStreamlitApp)

```python
from core import KDSTheme, KDSData, KDSStreamlitApp

app = (
    KDSStreamlitApp("Dashboard Title", theme=KDSTheme())
    .set_data(data)
    .add_metric("Revenue", "$1.2M")
    .add_chart("sales", "bar", "region", "revenue", "By Region")
)

app.generate("exports/my_app/")
```

### React (KDSReactApp)

```python
from core import KDSTheme, KDSData, KDSReactApp

app = (
    KDSReactApp("Dashboard Title", theme=KDSTheme())
    .set_data(data)
    .add_metric("Revenue", "$1.2M")
    .add_chart("sales", "bar", "region", "revenue", "By Region")
)

app.generate("exports/my_react_app/")
```

## Error Handling

| Error | Resolution |
|-------|------------|
| "No data set" | Call `set_data()` before `generate()` |
| "Unknown data source" | Check source name in `KDSData.list_sources()` |
| "Missing columns" | Verify columns exist in source data |
| "Data too large" | Switch to Streamlit tier |
| "Brand violation" | Check for forbidden colors, fix and regenerate |

---

## Dependency Management (Mandatory)

### Before Generation

Verify the target environment has required packages:

```python
from core.streamlit_utils import verify_imports, STREAMLIT_ALL_DEPS

success, missing = verify_imports(["streamlit", "pandas", "plotly", "seaborn"])
if not success:
    print(f"Missing: {missing}")
```

### During Generation

Always generate `requirements.txt` using the standard deps:

```python
from core.streamlit_utils import generate_requirements
from core.kds_utils import safe_write_text

req_content = generate_requirements(include_viz=True)
safe_write_text(output_dir / "requirements.txt", req_content)
```

### After Generation

Install before testing:

```bash
pip install -r requirements.txt
```

Never assume dependencies are installed. Always verify.

---

## Launch Protocol (Streamlit)

### Recommended: Use Launch Utility

```python
from core.streamlit_utils import launch_streamlit

success, message = launch_streamlit(
    app_path=Path("app.py"),
    port=8501,
    auto_kill=True,
    install_deps=True
)
print(message)
```

### Manual Launch

```bash
# 1. Kill existing processes
lsof -ti:8501 | xargs kill -9 2>/dev/null || true

# 2. Install deps
pip install -r requirements.txt -q

# 3. Launch
streamlit run app.py --server.port=8501 --server.headless=true

# 4. Verify
curl -s -o /dev/null -w "%{http_code}" http://localhost:8501
```

### Port Conflict Resolution

If port 8501 is in use:
1. Kill existing process: `lsof -ti:8501 | xargs kill -9`
2. Or use alternate port: `--server.port=8502`

---

## Completion Checklist (Non-Negotiable)

Do NOT declare a dashboard "complete" until ALL pass:

| Check | Command | Expected |
|-------|---------|----------|
| Deps installed | `pip install -r requirements.txt` | Exit 0 |
| Imports work | `python -c "import streamlit, pandas, plotly"` | No error |
| App launches | `streamlit run app.py` | No error |
| Health check | `curl http://localhost:PORT` | HTTP 200 |
| Brand check | `python -m core.brand_guard .` | No errors |
| No emojis | Check all `.py` files | None found |

### Quick Validation Script

```bash
# Run all checks
pip install -r requirements.txt -q && \
python -c "import streamlit, pandas, plotly, seaborn" && \
timeout 10 streamlit run app.py --server.headless=true &
sleep 5 && curl -s -o /dev/null -w "%{http_code}" http://localhost:8501 | grep -q 200 && \
echo "[ok] All checks passed"
```

---

## Brand Compliance Reminders

### No Emojis - Anywhere

Emojis are forbidden in:
- `page_icon` parameter
- Titles and headers
- Comments
- Data labels

Use Lucide icons instead (see below).

### Lucide Icons (Approved Alternative)

For Streamlit apps, use text-based indicators or Lucide icon names for documentation:

| Use Case | Instead of Emoji | Use |
|----------|------------------|-----|
| Success | (checkmark emoji) | `[check]` or Lucide: `<CheckCircle />` |
| Warning | (warning emoji) | `[!]` or Lucide: `<AlertTriangle />` |
| Error | (x emoji) | `[x]` or Lucide: `<XCircle />` |
| Info | (info emoji) | `[i]` or Lucide: `<Info />` |
| Chart | (chart emoji) | Lucide: `<BarChart3 />` |
| Dashboard | (graph emoji) | Lucide: `<LayoutDashboard />` |
| Settings | (gear emoji) | Lucide: `<Settings />` |
| Data | (folder emoji) | Lucide: `<Database />` |
| Sleep/Rest | (zzz emoji) | Lucide: `<Moon />` |
| Time | (clock emoji) | Lucide: `<Clock />` |

For page icons in Streamlit, use simple ASCII or omit entirely:

```python
# Bad
st.set_page_config(page_icon="(sleep emoji)")

# Good
st.set_page_config(page_icon="o")  # Simple circle

# Better - omit entirely
st.set_page_config(page_title="Sleep Study Dashboard", layout="wide")
```
