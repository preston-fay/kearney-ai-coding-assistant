# Kearney PowerPoint Skill

Best practices for PowerPoint presentation outputs.

## Foundation

If available, first apply all practices from: `/mnt/skills/public/pptx/SKILL.md`

Then apply these Kearney-specific requirements (override if conflict).

## When to Use

- Client presentations and deliverables
- Executive briefings
- Project status updates
- Workshop facilitation materials
- Final analysis outputs

## Kearney Brand Requirements (Non-Negotiable)

### Colors

| Element | Color | Hex |
|---------|-------|-----|
| Primary accent | Kearney Purple | #7823DC |
| Dark background | Dark gray | #1E1E1E |
| Light background | White | #FFFFFF |
| Primary text (light bg) | Dark gray | #333333 |
| Primary text (dark bg) | White | #FFFFFF |
| Secondary text | Medium gray | #666666 |

**FORBIDDEN:** Green in any shade - never use for any element.

### Typography

| Element | Font | Weight | Size |
|---------|------|--------|------|
| Slide title | Inter | 600 (SemiBold) | 36pt |
| Section header | Inter | 500 (Medium) | 28pt |
| Body text | Inter | 400 (Regular) | 18pt |
| Captions | Inter | 400 (Regular) | 14pt |
| Footnotes | Inter | 400 (Regular) | 10pt |

Fallback: Arial if Inter not available.

## Slide Structure

### Required Slides

1. **Title slide** (slide 1)
   - Project name
   - Client name
   - Date
   - Kearney logo (bottom right)

2. **Executive summary** (slide 2)
   - 3-5 key messages only
   - No detailed data
   - "So what" for executives

3. **Content slides** (slides 3-N)
   - One insight per slide
   - Action title (states the finding)
   - Supporting evidence

4. **Appendix** (if needed)
   - Clearly labeled "Appendix"
   - Detailed backup data
   - Methodology notes

### Slide Layout Rules

- Title at top (action title stating the insight)
- Maximum 5 bullet points per slide
- NO full sentences in bullets
- White space is intentional - don't fill every corner
- Footer: Page number, confidentiality notice

## Action Titles

Headlines should state the insight, not describe the content.

| Bad Title | Good Title |
|-----------|------------|
| "Revenue by Region" | "Northeast Leads with 45% Revenue Share" |
| "Customer Analysis" | "Enterprise Customers Drive 3x Higher LTV" |
| "Market Overview" | "Market Growing 12% YoY Despite Headwinds" |

## Chart Integration

All charts must come from `core/chart_engine.py`:

```python
from core.chart_engine import KDSChart

chart = KDSChart()
chart.bar(data, labels, title='Northeast Leads Revenue Growth')
chart.save('outputs/charts/revenue.png')
```

### Chart Slide Layout

```
+------------------------------------------+
| Northeast Leads with 45% Revenue Share   |  <- Action title
+------------------------------------------+
|                                          |
|        [Chart Image - centered]          |
|                                          |
|                                          |
+------------------------------------------+
| Source: Internal sales data, Q3 2025     |  <- Source citation
+------------------------------------------+
```

### Chart Requirements

- NO gridlines
- Data labels OUTSIDE bars/slices
- Source citation at bottom of slide
- Kearney color palette only

## Text Guidelines

### Bullet Points

```
Good:
- 45% revenue from Northeast region
- 3x customer lifetime value
- 12% YoY market growth

Bad:
- The Northeast region contributes approximately 45% of total revenue.
- Customer lifetime value is about 3x higher than other segments.
- The market has been growing at 12% year over year.
```

### Numbers

- Use numerals, not words: "45%" not "forty-five percent"
- Round appropriately: "$2.3M" not "$2,347,892"
- Include units and comparisons: "45% (+7pp YoY)"

## Building Presentations

Always use `core/slide_engine.py`:

```python
from core.slide_engine import KDSPresentation

pres = KDSPresentation()

pres.add_title_slide(
    title='Q3 Revenue Analysis',
    subtitle='Acme Corporation',
    date='December 2025'
)

pres.add_executive_summary([
    'Northeast leads with 45% revenue share',
    'Enterprise segment drives highest LTV',
    'Market growing 12% despite headwinds'
])

pres.add_chart_slide(
    title='Northeast Leads with 45% Revenue Share',
    chart_path='outputs/charts/revenue.png',
    source='Internal sales data, Q3 2025'
)

pres.save('exports/acme-q3-analysis.pptx')
```

Never use python-pptx directly.

## Slide Count Guidelines

| Presentation Type | Target Slides |
|-------------------|---------------|
| Executive briefing | 5-10 |
| Project update | 10-15 |
| Full analysis | 20-30 |
| Workshop | 15-25 |

Rule of thumb: 1-2 minutes per slide for verbal presentations.

## Quality Checklist

Before finalizing any presentation:

- [ ] Title slide has project name, client, date, logo
- [ ] Executive summary is slide 2
- [ ] All titles are action titles (state the insight)
- [ ] Maximum 5 bullets per slide
- [ ] No full sentences in bullets
- [ ] All charts from core/chart_engine.py
- [ ] No gridlines on charts
- [ ] Data labels outside bars/slices
- [ ] No green colors anywhere
- [ ] Kearney Purple (#7823DC) used for emphasis
- [ ] Source citations on data slides
- [ ] Page numbers on all slides
- [ ] Appendix clearly labeled
- [ ] NO emojis anywhere
- [ ] Spell check completed

## File Naming

Pattern: `{client}-{project}-{version}.pptx`

Examples:
- `acme-q3-analysis-v1.pptx`
- `acme-q3-analysis-final.pptx`
- `acme-q3-analysis-client-review.pptx`

## Export Location

Final presentations go to: `exports/`

Working drafts can remain in: `outputs/`
