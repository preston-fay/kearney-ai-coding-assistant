# Kearney Word Document Skill

Best practices for Word document outputs.

## Foundation

If available, first apply all practices from: `/mnt/skills/public/docx/SKILL.md`

Then apply these Kearney-specific requirements (override if conflict).

## When to Use

- Formal proposals and RFP responses
- Detailed written reports
- Client memos and briefs
- Methodology documentation
- Contract-adjacent deliverables

## Kearney Brand Requirements (Non-Negotiable)

### Colors

| Element | Color | Hex |
|---------|-------|-----|
| Primary accent | Kearney Purple | #7823DC |
| Headings | Kearney Purple | #7823DC |
| Body text | Dark gray | #333333 |
| Secondary text | Medium gray | #666666 |
| Table headers | Purple bg, white text | #7823DC / #FFFFFF |

**FORBIDDEN:** Green in any shade - never use.

### Typography

| Element | Font | Weight | Size |
|---------|------|--------|------|
| Title | Inter | 600 (SemiBold) | 24pt |
| Heading 1 | Inter | 600 (SemiBold) | 18pt |
| Heading 2 | Inter | 500 (Medium) | 14pt |
| Heading 3 | Inter | 500 (Medium) | 12pt |
| Body text | Inter | 400 (Regular) | 11pt |
| Captions | Inter | 400 (Regular) | 9pt |

Fallback: Arial if Inter not available.

### Page Setup

- Margins: 1" all sides
- Line spacing: 1.15
- Paragraph spacing: 6pt after
- Page numbers: Bottom right
- Header: Client name (left), Confidential (right)
- Footer: Page X of Y (right)

## Document Types

### Proposal Structure

1. **Cover Page**
   - Project title
   - Client name
   - Date
   - Kearney logo
   - "Confidential" marking

2. **Executive Summary** (1-2 pages)
   - Challenge/opportunity
   - Proposed approach
   - Expected outcomes
   - Investment summary

3. **Situation Overview**
   - Client context
   - Market dynamics
   - Key challenges

4. **Our Approach**
   - Methodology
   - Workstreams
   - Key activities

5. **Team**
   - Team structure
   - Key personnel bios
   - Relevant experience

6. **Timeline**
   - Project phases
   - Key milestones
   - Dependencies

7. **Investment**
   - Fee structure
   - Payment terms
   - Assumptions

8. **Appendix**
   - Credentials
   - Case studies
   - Detailed bios

### Report Structure

1. **Cover Page**
2. **Executive Summary**
3. **Background/Context**
4. **Methodology**
5. **Findings**
   - Finding 1
   - Finding 2
   - Finding 3
6. **Recommendations**
7. **Implementation Roadmap**
8. **Appendix**

### Memo Structure

```
TO:      [Recipient]
FROM:    [Sender]
DATE:    [Date]
RE:      [Subject]
CC:      [Others]

---

SITUATION
[1-2 paragraphs on context]

ANALYSIS
[Key findings and supporting evidence]

RECOMMENDATION
[Clear recommendation with rationale]

NEXT STEPS
[Specific action items with owners and dates]
```

## Formatting Guidelines

### Headings

- Use heading styles (don't manually format)
- Maintain hierarchy (no skipped levels)
- Keep headings concise (5-8 words max)

### Body Text

- Left-aligned (not justified)
- Single space within paragraphs
- 6pt space after paragraphs
- NO emojis

### Lists

- Use bullets for unordered items
- Use numbers for sequences or rankings
- Indent consistently (0.25" per level)
- Parallel structure required

### Tables

```
+------------------+------------------+------------------+
| Header 1         | Header 2         | Header 3         |  <- Purple bg
+------------------+------------------+------------------+
| Data             | Data             | Data             |
+------------------+------------------+------------------+
| Data             | Data             | Data             |
+------------------+------------------+------------------+
```

- Header row: #7823DC background, white text
- No heavy borders (use subtle 0.5pt gray)
- Alternating row shading optional (very light gray #F5F5F5)
- Always cite data sources below table

### Charts and Images

- Import charts from `core/chart_engine.py`
- Center images on page
- Include captions below
- Add source citations
- Ensure readable at print size

## Building Documents

Use `core/document_engine.py` when available:

```python
from core.document_engine import KDSDocument

doc = KDSDocument()

doc.add_cover_page(
    title='Q3 Revenue Analysis',
    client='Acme Corporation',
    date='December 2025'
)

doc.add_heading('Executive Summary', level=1)
doc.add_paragraph('Key findings from our analysis...')

doc.add_heading('Findings', level=1)
doc.add_heading('Northeast Region Performance', level=2)
doc.add_paragraph('The Northeast region...')

doc.add_table(data, headers=['Region', 'Revenue', 'Growth'])

doc.save('exports/acme-q3-report.docx')
```

## Quality Checklist

Before finalizing any document:

- [ ] Cover page complete with all required elements
- [ ] Executive summary present (for reports/proposals)
- [ ] Heading styles used consistently
- [ ] No skipped heading levels
- [ ] Page numbers on all pages
- [ ] Header/footer configured correctly
- [ ] Tables have header rows
- [ ] All charts from core/chart_engine.py
- [ ] Source citations on all data
- [ ] No green colors anywhere
- [ ] Kearney Purple (#7823DC) for accents
- [ ] NO emojis anywhere
- [ ] Spell check completed
- [ ] Grammar check completed
- [ ] "Confidential" marking if required

## File Naming

Pattern: `{client}-{document-type}-{version}.docx`

Examples:
- `acme-proposal-v1.docx`
- `acme-q3-report-final.docx`
- `acme-memo-pricing-update.docx`

## Export Location

Final documents go to: `exports/`

Working drafts can remain in: `outputs/`
