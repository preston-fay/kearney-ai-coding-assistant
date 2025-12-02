# Kearney Excel/Spreadsheet Skill

Best practices for Excel and spreadsheet outputs.

## Foundation

If available, first apply all practices from: `/mnt/skills/public/xlsx/SKILL.md`

Then apply these Kearney-specific requirements (override if conflict).

## When to Use

- Financial models and calculations
- Data analysis and transformation
- Supporting data for presentations
- Client data deliverables
- Project tracking and planning

## Kearney Brand Requirements (Non-Negotiable)

### Colors

| Element | Color | Hex |
|---------|-------|-----|
| Header row background | Kearney Purple | #7823DC |
| Header row text | White | #FFFFFF |
| Alternating row (optional) | Light gray | #F5F5F5 |
| Input cells highlight | Light purple | #E8D4F8 |
| Calculation cells | No fill | - |
| Error/warning | Red | #DC2323 |
| **FORBIDDEN** | Green | Any shade |

### Typography

- Primary font: Inter or Arial
- Header size: 11pt bold
- Body size: 10-11pt regular
- Use consistent formatting across sheets

## Workbook Structure

### Required Tabs (in order)

1. **Cover** - Title, date, author, version, confidentiality
2. **Summary** - Key outputs, linked to detail tabs
3. **Data** - Raw and processed data
4. **Analysis** - Calculations and transformations
5. **Documentation** - Methodology, sources, assumptions

### Tab Naming

- Use clear, descriptive names
- No spaces (use underscores or CamelCase)
- Keep names short (max 20 characters)
- Examples: `Summary`, `RawData`, `Analysis`, `Assumptions`

## Sheet Layout

### Standard Header Block

```
+------------------------------------------------------------------+
| [Project Title]                                    [Kearney Logo] |
| Client: [Name]                                                    |
| Date: [YYYY-MM-DD]                                               |
| Author: [Name]                                                    |
| Version: [X.X]                                                    |
+------------------------------------------------------------------+
```

### Data Table Layout

```
Row 1: [Header row - Purple background, white text, bold]
Row 2: [Data row]
Row 3: [Data row - optional alternating gray]
Row 4: [Data row]
...
Last+1: [Total row - bold, may have light fill]
Last+2: [Source citation - italic, small font]
```

## Formatting Guidelines

### Numbers

| Type | Format | Example |
|------|--------|---------|
| Currency | $#,##0 or $#,##0.00 | $1,234 |
| Percentage | 0.0% | 45.2% |
| Large numbers | #,##0 | 1,234,567 |
| Dates | YYYY-MM-DD | 2025-12-01 |
| Ratios | 0.0x | 2.3x |

### Cell Formatting

- Freeze panes for header rows and key columns
- Use consistent column widths
- Right-align numbers, left-align text
- Include units in headers, not cells
- Use borders sparingly (light gray, 0.5pt)

### Conditional Formatting

**DO:**
- Use purple gradient for heat maps
- Use gray scale for intensity
- Use red for errors/warnings

**DON'T:**
- Never use green (not even for "good" values)
- Avoid traffic light formatting
- Don't overuse - keep it simple

## Model Best Practices

### Input/Output Separation

```
Inputs (highlighted):     Outputs (calculated):
+-------------------+     +-------------------+
| Revenue growth: 5%|---->| Year 1: $105M     |
| Cost reduction: 3%|---->| Year 2: $110M     |
| Base revenue: $100|---->| Year 3: $116M     |
+-------------------+     +-------------------+
```

- Input cells: Light purple highlight (#E8D4F8)
- Calculation cells: No fill
- Output cells: May have subtle border

### Formula Guidelines

- One formula per column (copy down, not across with different logic)
- Use named ranges for key inputs
- No hardcoded numbers in formulas
- Break complex formulas into steps
- Document formulas in adjacent cells or Documentation tab

### Error Handling

```excel
=IFERROR(A1/B1, "N/A")
=IF(ISBLANK(A1), "", calculation)
```

- Handle division by zero
- Handle blank cells gracefully
- Use data validation for inputs

## Charts in Excel

If creating charts within Excel (vs. importing from chart_engine):

- Remove gridlines: Format Axis > Major Gridlines > None
- Use Kearney colors only
- NO green for any series
- Data labels outside bars/slices
- Clear, insight-stating titles

Preferred: Export data and use `core/chart_engine.py` for consistent styling.

## Building Spreadsheets

Use `core/spreadsheet_engine.py` when available:

```python
from core.spreadsheet_engine import KDSSpreadsheet

wb = KDSSpreadsheet()

wb.add_cover_sheet(
    title='Revenue Model',
    client='Acme Corporation',
    date='2025-12-01',
    author='Analyst Name'
)

wb.add_data_sheet('RawData', dataframe)
wb.add_analysis_sheet('Analysis', formulas)
wb.add_summary_sheet('Summary', summary_data)

wb.save('exports/acme-revenue-model.xlsx')
```

## Data Validation

- Use dropdowns for categorical inputs
- Set min/max ranges for numeric inputs
- Add input messages explaining expected values
- Use error alerts for invalid entries

```excel
Data Validation Examples:
- Region: List (Northeast, Southeast, Midwest, West)
- Growth Rate: Decimal between -0.5 and 0.5
- Date: Date between 2020-01-01 and 2030-12-31
```

## Version Control

Include version tracking on Cover sheet:

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-12-01 | [Name] | Initial version |
| 1.1 | 2025-12-05 | [Name] | Updated Q3 actuals |
| 2.0 | 2025-12-10 | [Name] | Added sensitivity analysis |

## Quality Checklist

Before finalizing any spreadsheet:

- [ ] Cover sheet complete with all metadata
- [ ] All tabs clearly named
- [ ] Header rows frozen
- [ ] Headers formatted (purple bg, white text)
- [ ] Numbers consistently formatted
- [ ] Input cells highlighted
- [ ] No circular references
- [ ] All formulas working (no #REF!, #DIV/0!, etc.)
- [ ] Named ranges used for key inputs
- [ ] Data sources documented
- [ ] Assumptions documented
- [ ] No green anywhere (including charts)
- [ ] Version tracked
- [ ] Print area set if applicable

## File Naming

Pattern: `{client}-{model-type}-{version}.xlsx`

Examples:
- `acme-revenue-model-v1.xlsx`
- `acme-market-analysis-final.xlsx`
- `acme-financial-projections-v2.xlsx`

## Export Location

Final spreadsheets go to: `exports/`

Working drafts can remain in: `outputs/`

## Large File Handling

For files > 50MB, consider:

1. Using DuckDB for analysis (see `core/data_handler.py`)
2. Splitting into multiple files
3. Outputting summary only, keeping detail in database

```python
from core.data_handler import ProjectDatabase

db = ProjectDatabase(Path("."))
db.register_file("data/raw/large_file.csv")
summary = db.query_df("SELECT region, SUM(sales) FROM data GROUP BY region")
# Export summary to Excel, keep detail in DuckDB
```
