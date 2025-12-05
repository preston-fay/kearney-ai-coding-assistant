# Kearney Visualization Skill

Best practices for chart and visualization outputs (PNG, SVG).

## When to Use

- Charts (bar, line, scatter, pie, area, histogram, boxplot, heatmap, donut, sankey)
- Comparison charts (grouped_bar, stacked_bar, combo, bullet)
- Flow diagrams (sankey, waterfall)
- Diagrams (architecture, process flows, org charts)
- Infographics and data callouts
- Any visual asset for presentations or reports

## Format Selection

| Use Case | Format | Rationale |
|----------|--------|-----------|
| Web/dashboard | SVG | Scalable, small file size |
| Print/presentation | PNG (300dpi) | Universal compatibility |
| Complex charts | PNG | Better gradient/effect support |
| Simple diagrams | SVG | Editable, crisp at any size |

## Kearney Brand Requirements (Non-Negotiable)

- Primary color: #7823DC (Kearney Purple)
- FORBIDDEN: Green (#00FF00, #2E7D32, #4CAF50, etc.) - never use
- Background: #1E1E1E (dark mode default) or #FFFFFF (light)
- Typography: Inter (Arial fallback)
- NO gridlines on charts
- Data labels OUTSIDE bars/slices
- NO emojis or decorative elements

## Approved Color Palette

| Color | Hex | Usage |
|-------|-----|-------|
| Kearney Purple | #7823DC | Primary accent, highlights |
| Dark Background | #1E1E1E | Default chart background |
| White | #FFFFFF | Light mode background |
| Text Primary | #333333 | Main text on light backgrounds |
| Text Light | #FFFFFF | Text on dark backgrounds |
| Gray 1 | #F5F5F5 | Light fills |
| Gray 2 | #E0E0E0 | Borders, dividers |
| Gray 3 | #CCCCCC | Secondary borders |
| Gray 4 | #999999 | Muted text |
| Gray 5 | #666666 | Secondary text |

## Chart Best Practices

1. **Clarity over decoration** - remove all non-data ink
2. **One message per chart** - don't overload
3. **Title states the insight** - not just "Revenue by Region" but "Northeast Leads Revenue Growth"
4. **Accessible colors** - use Kearney palette which is colorblind-safe
5. **Consistent sizing** - 1200x800px default for presentations
6. **Label everything** - axes, data points, legends

## Chart Type Selection

| Data Story | Chart Type | Method |
|------------|------------|--------|
| Comparison across categories | Horizontal bar | `bar(horizontal=True)` |
| Multiple series comparison | Grouped bar | `grouped_bar()` |
| Change over time | Line chart | `line()` |
| Magnitude over time | Area chart | `area()` |
| Part-to-whole | Pie or Donut | `pie()` or `donut()` |
| Part-to-whole over time | Stacked bar | `stacked_bar()` |
| Correlation | Scatter plot | `scatter()` |
| Distribution | Histogram | `histogram()` |
| Distribution comparison | Box plot | `boxplot()` |
| Intensity/correlation matrix | Heatmap | `heatmap()` |
| Ranking | Horizontal bar (sorted) | `bar(horizontal=True)` |
| KPI vs target | Bullet chart | `bullet()` |
| Cumulative change | Waterfall | `waterfall()` |
| Dual metric comparison | Combo (bar + line) | `combo()` |
| Flow/allocation | Sankey diagram | `sankey()` |

## SVG-Specific Guidelines

- Use viewBox for responsiveness: `viewBox="0 0 1200 800"`
- Embed fonts or convert text to paths for portability
- Optimize with SVGO for file size
- Use `<title>` and `<desc>` for accessibility
- Group related elements with `<g>` tags

## PNG-Specific Guidelines

- 300dpi for print, 150dpi for screen
- Default size: 1200x800px for presentations
- Use transparency where appropriate (PNG-24)
- Compress without quality loss
- Include @2x versions for retina displays if needed

## Data Label Placement

```
CORRECT:                    INCORRECT:
   ___                         ___
  |   | 45%                   | 45%|
  |   |                       |   |
  |___|                       |___|

Labels OUTSIDE bars          Labels INSIDE bars
```

## Axis Guidelines

- Y-axis: Start at zero for bar charts (unless showing change)
- X-axis: Use meaningful labels, not codes
- Rotate labels only if necessary (45 degrees max)
- Include units in axis titles

## Legend Placement

- Position: Right side or below chart
- Order: Match visual order in chart
- Keep concise - max 6 items
- Consider direct labeling instead of legend when possible

## Always Use core/chart_engine.py

Never use matplotlib directly. The chart engine enforces brand compliance:

```python
from core.chart_engine import KDSChart

chart = KDSChart()
chart.bar(data, labels, title='Northeast Leads Revenue Growth')
chart.save('outputs/charts/revenue_by_region.png')
```

## Available Chart Methods

All methods return `self` for chaining and support `title`, axis labels, and KDS-compliant styling.

### Basic Charts
```python
chart.bar(data, labels, title='...')                    # Vertical/horizontal bar
chart.line(x_data, y_data, title='...')                 # Line chart
chart.pie(data, labels, title='...')                    # Pie chart
chart.scatter(x_data, y_data, title='...')              # Scatter plot
chart.histogram(data, bins=10, title='...')             # Distribution histogram
chart.area(x_data, y_data, title='...', stacked=False)  # Filled area chart
```

### Comparison Charts
```python
chart.grouped_bar(data, group_labels, series_labels)    # Side-by-side bars
chart.stacked_bar(data, group_labels, series_labels)    # Stacked bars
chart.combo(categories, bar_data, line_data)            # Bar + line overlay
chart.bullet(actual, target, ranges, label)             # KPI vs target
```

### Statistical Charts
```python
chart.boxplot(data, labels, title='...')                # Distribution box plot
chart.heatmap(data_2d, row_labels, col_labels)          # Intensity matrix
```

### Flow Charts
```python
chart.waterfall(values, labels, title='...')            # Cumulative change
chart.sankey(flows, labels, title='...', unit='$M')     # Flow allocation
```

### Part-to-Whole
```python
chart.pie(data, labels, title='...')                    # Simple pie
chart.donut(data, labels, center_value='$1.2M')         # Donut with center KPI
```

## Quality Checklist

Before finalizing any visualization:

- [ ] No gridlines visible
- [ ] No green colors used
- [ ] Data labels outside bars/slices
- [ ] Title states the insight
- [ ] All axes labeled with units
- [ ] Legend present if needed
- [ ] Kearney Purple (#7823DC) used for emphasis
- [ ] Dark mode background (#1E1E1E) or white (#FFFFFF)
- [ ] No emojis or decorative elements
- [ ] File saved to outputs/charts/
