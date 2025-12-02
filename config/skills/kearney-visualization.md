# Kearney Visualization Skill

Best practices for chart and visualization outputs (PNG, SVG).

## When to Use

- Charts (bar, line, scatter, pie, area)
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

| Data Story | Chart Type |
|------------|------------|
| Comparison across categories | Horizontal bar |
| Change over time | Line chart |
| Part-to-whole | Pie (max 5 slices) or stacked bar |
| Correlation | Scatter plot |
| Distribution | Histogram or box plot |
| Ranking | Horizontal bar (sorted) |

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
