# BL-001: Design System Module

**Status**: Ready for Implementation
**Priority**: High
**Estimated Effort**: 18-24 hours
**Created**: 2025-12-03
**Last Updated**: 2025-12-03

## Summary

Add a client design system capability that allows users to:
1. Extract brand assets from a client's website (colors, fonts, logos)
2. Upload supplementary assets (logos, PDFs, PPTXs) to refine the system
3. Store design systems in a shared library for reuse across projects
4. Select a design system (default: Kearney) during project interviews
5. Apply the selected design system to all KACA outputs with WCAG 2.1 AA accessibility compliance

---

## Purpose & Goals

**Problem**: Currently, KACA hardcodes Kearney brand values throughout the codebase. When creating deliverables for clients, consultants must manually edit outputs to match client branding, which is time-consuming and error-prone.

**Goals**:
- Enable client-branded outputs without code changes
- Maintain accessibility compliance (WCAG 2.1 AA) across all brand systems
- Provide automated brand extraction from client websites
- Keep client brand data private (not committed to git)
- Preserve Kearney brand as the high-quality default

---

## Design Principles

### 1. Single Source of Truth for Brand
All brand tokens (colors, fonts, spacing) live in `brand.yaml`. Engines never contain hardcoded hex values or font names.

### 2. Accessibility Firewall in the Middle
The `applicator.py` module sits between `DesignSystem` and `KDSTheme`, enforcing WCAG 2.1 AA contrast ratios. Invalid color combinations are automatically corrected before reaching engines.

### 3. Decoupling: DesignSystem → KDSTheme → Engines
```
brand.yaml → DesignSystem → Applicator (+ accessibility) → KDSTheme → Engines
```
Engines remain ignorant of design system internals. They only consume `KDSTheme` tokens.

### 4. Privacy by Default
Client design systems are gitignored. Only Kearney (the default) is committed. Clients' brand data never leaves the developer's machine unless explicitly shared.

### 5. Progressive Extraction
Web scraping starts conservative (safe, minimal requests) and escalates to moderate (more thorough) only if the user approves. Aggressive mode is not implemented to avoid legal/ethical concerns.

---

## Architecture Overview

### Directory Structure

```
config/
├── brands/                          # Design system library
│   ├── .gitignore                   # Ignore all except Kearney
│   ├── README.md                    # Usage documentation
│   ├── kearney/                     # Default design system (committed)
│   │   ├── brand.yaml
│   │   ├── logo_primary.svg
│   │   └── logo_icon.svg
│   └── {client-slug}/               # Client DS (gitignored)
│       ├── brand.yaml
│       └── logo_primary.png

core/
├── design_system/                   # New module
│   ├── __init__.py
│   ├── schema.py                    # DesignSystem dataclass
│   ├── accessibility.py             # WCAG 2.1 AA enforcement
│   ├── applicator.py                # DS → KDSTheme bridge
│   ├── manager.py                   # CRUD operations
│   ├── extractor.py                 # Web scraping (conservative/moderate)
│   └── analyzer.py                  # PDF/PPTX/image parsing
```

### Core Objects Diagram

```
┌─────────────────┐
│   brand.yaml    │  (YAML file)
└────────┬────────┘
         │ loaded by
         ▼
┌─────────────────┐
│ DesignSystem    │  (Python dataclass from schema.py)
│  - meta         │
│  - colors       │
│  - typography   │
│  - logos        │
└────────┬────────┘
         │ processed by
         ▼
┌─────────────────┐
│  Applicator     │  (applicator.py)
│  + accessibility│  Enforces WCAG 2.1 AA
└────────┬────────┘
         │ produces
         ▼
┌─────────────────┐
│   KDSTheme      │  (Simplified token bucket)
│  - primary      │
│  - text_color   │
│  - bg_color     │
│  - chart_palette│
└────────┬────────┘
         │ consumed by
         ▼
┌─────────────────┐
│    Engines      │  (chart, webapp, slide, etc.)
└─────────────────┘
```

---

## Core Components

### 1. DesignSystem (schema.py)

**Purpose**: Python representation of `brand.yaml` with validation.

**Key Classes**:
```python
@dataclass
class ColorPalette:
    primary: str
    secondary: Optional[str]
    accent: Optional[str]
    semantic: Dict[str, str]  # success, warning, error, info
    chart_palette: List[str]

@dataclass
class Typography:
    heading: FontFamily
    body: FontFamily
    monospace: FontFamily

@dataclass
class Logo:
    path: str
    width: Optional[int]
    height: Optional[int]
    placement: List[str]  # ["dashboard_header", "webapp_header", ...]

@dataclass
class DesignSystem:
    meta: Meta
    colors: ColorPalette
    typography: Typography
    spacing: Dict[str, int]
    borders: Dict[str, str]
    logos: Dict[str, Logo]
    extraction_metadata: Optional[ExtractionMetadata]
```

**Validation**: Ensures all required fields are present, hex colors are valid, font weights are integers.

---

### 2. Accessibility Module (accessibility.py)

**Purpose**: Enforce WCAG 2.1 AA contrast ratios (4.5:1 minimum for normal text, 3:1 for large text/UI).

**Key Functions**:
```python
def relative_luminance(hex_color: str) -> float:
    """Calculate relative luminance per WCAG formula."""

def contrast_ratio(color1: str, color2: str) -> float:
    """Calculate contrast ratio between two colors."""

def ensure_contrast(
    foreground: str,
    background: str,
    min_ratio: float = 4.5,
    strategy: str = "auto"
) -> str:
    """
    Adjust foreground color to meet contrast requirements.

    Strategies:
    - "binary": Return white or black (safe, but changes hue)
    - "tint": Lighten/darken foreground (preserves hue, may fail)
    - "auto": Try tint first, fall back to binary
    """
```

**Context-Based Strategy Selection**:
- **Buttons/CTAs**: Use `"binary"` (clarity > brand fidelity)
- **Headings**: Use `"tint"` (preserve brand color)
- **Chart labels**: Use `"binary"` (legibility critical)
- **Body text**: Use `"auto"` (try to preserve, ensure legibility)

---

### 3. Applicator (applicator.py)

**Purpose**: Bridge between `DesignSystem` and `KDSTheme`, applying accessibility rules.

**Key Function**:
```python
def apply_design_system(
    ds: DesignSystem,
    context: str = "webapp"
) -> KDSTheme:
    """
    Convert DesignSystem to KDSTheme with accessibility enforcement.

    Steps:
    1. Extract colors from ds.colors
    2. Run ensure_contrast() on all text/background pairs
    3. Build chart_palette with verified contrast
    4. Map typography to web-safe fallbacks
    5. Return simplified KDSTheme
    """
```

**Example**:
```python
ds = load_design_system("acme-corp")
theme = apply_design_system(ds, context="dashboard")
# theme.primary is now WCAG 2.1 AA compliant against theme.bg_color
```

---

### 4. Manager (manager.py)

**Purpose**: CRUD operations for design systems in `config/brands/`.

**Key Functions**:
```python
def list_design_systems() -> List[str]:
    """Return list of available design system slugs."""

def load_design_system(slug: str) -> DesignSystem:
    """Load and parse brand.yaml for given slug."""

def save_design_system(ds: DesignSystem) -> None:
    """Save DesignSystem to config/brands/{slug}/brand.yaml."""

def delete_design_system(slug: str) -> None:
    """Remove design system (cannot delete 'kearney')."""

def create_from_url(url: str, mode: str = "conservative") -> DesignSystem:
    """
    Extract design system from website.
    Calls extractor.py with specified mode.
    """

def create_from_assets(files: List[Path]) -> DesignSystem:
    """
    Analyze uploaded assets (logos, PDFs, PPTXs).
    Calls analyzer.py to extract brand tokens.
    """

def get_default() -> str:
    """Return 'kearney'."""
```

---

### 5. Extractor (extractor.py)

**Purpose**: Web scraping to extract brand tokens from a client's website.

**Modes**:
1. **Conservative** (default):
   - Single homepage GET request
   - Parse inline styles and `<style>` tags only
   - Extract 3-5 most common colors
   - Detect font-family from CSS
   - No external resource fetching

2. **Moderate** (requires user approval):
   - Fetch CSS files linked from homepage
   - Parse CSS variables (`:root { --primary: ... }`)
   - Follow logo `<img>` src to download
   - Extract up to 10 colors
   - Respect robots.txt

3. **Aggressive** (NOT IMPLEMENTED):
   - Would involve crawling multiple pages, analyzing images
   - Legal/ethical concerns → out of scope

**Key Function**:
```python
def extract_from_url(
    url: str,
    mode: str = "conservative"
) -> Dict[str, Any]:
    """
    Returns raw extraction data:
    {
        "colors": ["#7823DC", "#1E1E1E", ...],
        "fonts": ["Inter", "Arial", ...],
        "logo_url": "https://example.com/logo.svg",
        "metadata": {"mode": "conservative", "timestamp": ...}
    }
    """
```

**Error Handling**: Returns partial results if extraction fails. User can refine manually.

---

### 6. Analyzer (analyzer.py)

**Purpose**: Extract brand tokens from uploaded assets (images, PDFs, PPTXs).

**Capabilities**:
- **Images (PNG/SVG)**: Detect dominant colors, extract logo dimensions
- **PDFs**: Parse text for font names, extract embedded images for colors
- **PPTXs**: Extract master slide colors, fonts, logo placements

**Key Function**:
```python
def analyze_assets(
    files: List[Path]
) -> Dict[str, Any]:
    """
    Returns:
    {
        "colors": [...],
        "fonts": [...],
        "logos": [{"path": ..., "dominant_color": ...}],
        "confidence": 0.75
    }
    """
```

**Merge Strategy**: Combines extraction + analysis results by frequency (most common wins).

---

## brand.yaml Schema

Complete specification for design system definition:

```yaml
meta:
  name: "Acme Corporation"
  slug: "acme-corp"  # Used in spec.yaml and directory name
  version: "1.0.0"
  source_url: "https://www.acme.com"  # Optional
  extraction_mode: "conservative"  # conservative | moderate | manual

colors:
  primary: "#FF6600"
  secondary: "#003366"  # Optional
  accent: "#FFCC00"  # Optional
  semantic:
    success: "#28A745"
    warning: "#FFC107"
    error: "#DC3545"
    info: "#17A2B8"
  chart_palette:
    - "#FF6600"
    - "#003366"
    - "#FFCC00"
    - "#28A745"
    - "#DC3545"
    - "#17A2B8"

typography:
  heading:
    family: "Montserrat"
    fallback: "Arial, sans-serif"
    weights: [400, 600, 700]
    web_font_url: "https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700"
  body:
    family: "Open Sans"
    fallback: "Arial, sans-serif"
    weights: [400, 600]
    web_font_url: "https://fonts.googleapis.com/css2?family=Open+Sans:wght@400;600"
  monospace:
    family: "Courier New"
    fallback: "monospace"
    weights: [400]

spacing:
  base: 8  # All spacing is multiple of base
  scale: [4, 8, 16, 24, 32, 48, 64]

borders:
  radius: "4px"
  width: "1px"
  color: "#E0E0E0"

logos:
  primary:
    path: "logo_primary.svg"  # Relative to config/brands/{slug}/
    width: 200
    height: 60
    placement: ["dashboard_header", "webapp_header", "streamlit_sidebar"]
  icon:
    path: "logo_icon.svg"
    width: 32
    height: 32
    placement: ["favicon"]

extraction_metadata:  # Optional, populated by extractor
  timestamp: "2025-12-03T10:30:00Z"
  mode: "conservative"
  confidence: 0.85
  url: "https://www.acme.com"
  manual_edits: true  # User refined after extraction
```

---

## Logo Placement Rules

| Output Type | Header | Footer | Charts | Notes |
|-------------|--------|--------|--------|-------|
| **Dashboard (HTML)** | ✅ Yes | ❌ No | ❌ No | Top-left header, max 200px wide |
| **Webapp (HTML)** | ✅ Yes | ❌ No | ❌ No | Top-left header, responsive |
| **Streamlit** | ✅ Yes (sidebar) | ❌ No | ❌ No | `st.sidebar.image()` |
| **React App** | ✅ Yes | ❌ No | ❌ No | Navbar component |
| **Charts (PNG/SVG)** | ❌ No | ❌ No | ❌ No | Distraction from data |
| **PPTX** | ❌ No | ❌ No | ❌ No | Use Kearney template only |
| **DOCX** | ❌ No | ❌ No | ❌ No | Use Kearney template only |
| **XLSX** | ❌ No | ❌ No | ❌ No | Plain data, no branding |

**Rationale**: Logos appear in interactive outputs (dashboards, webapps) where branding is expected. They do NOT appear in charts (data should speak for itself) or formal deliverables (PPTX/DOCX use Kearney templates with proper title slides).

---

## Integration Points

### 1. `/design-system` Command Flow

New command in `.claude/commands/design-system.md`:

```markdown
# Design System Management

You are helping the user manage KACA design systems.

## Available Actions

1. **Create from URL**
   - Prompt for client website URL
   - Ask extraction mode (conservative recommended)
   - Run extractor
   - Show preview (colors, fonts, logo)
   - Offer review/edit before saving
   - Save to config/brands/{slug}/

2. **Create from Assets**
   - Prompt for file uploads (drag-and-drop or paths)
   - Run analyzer on images, PDFs, PPTXs
   - Merge results
   - Show preview
   - Offer manual refinement
   - Save to config/brands/{slug}/

3. **List**
   - Show all available design systems
   - Highlight default (Kearney)

4. **View Details**
   - Display brand.yaml contents
   - Show logo preview if available

5. **Delete**
   - Confirm deletion (cannot delete 'kearney')
   - Remove directory
```

### 2. Interview Integration

Add ONE question to all interview trees (after project name, before project type):

```yaml
- id: design_system
  type: select
  prompt: "Which design system should this project use?"
  options:
    - value: kearney
      label: "Kearney (default)"
    - value: __from_library__
      label: "Select from library"
    - value: __create_new__
      label: "Create new from client website"
  default: kearney
  help: |
    Design systems define colors, fonts, and logos for outputs.
    Default is Kearney. You can create client design systems with /design-system.
```

If `__from_library__` selected, show available design systems.
If `__create_new__` selected, invoke `/design-system` flow inline.

### 3. spec.yaml Addition

Add `design_system` field to project metadata:

```yaml
project:
  name: "Q4 Sales Analysis"
  type: analytics
  design_system: "acme-corp"  # or "kearney" (default)
```

### 4. Engine Modifications Required

All engines must be refactored to:

1. Load `spec.yaml`
2. Call `resolve_theme(spec)` → returns `KDSTheme`
3. Use theme tokens instead of hardcoded values

**Example (chart_engine.py)**:
```python
# BEFORE
fig.update_layout(
    plot_bgcolor="#1E1E1E",
    paper_bgcolor="#1E1E1E",
    font_color="#FFFFFF"
)

# AFTER
theme = resolve_theme(spec)
fig.update_layout(
    plot_bgcolor=theme.bg_color,
    paper_bgcolor=theme.bg_color,
    font_color=theme.text_color
)
```

**Engines to Modify**:
- `chart_engine.py`
- `webapp_engine.py`
- `slide_engine.py` (Kearney only for now)
- `document_engine.py` (Kearney only for now)
- `spreadsheet_engine.py` (minimal styling)

---

## Accessibility Requirements

### WCAG 2.1 AA Compliance

**Minimum Contrast Ratios**:
- Normal text (< 18pt): **4.5:1**
- Large text (≥ 18pt or ≥ 14pt bold): **3.0:1**
- UI components (buttons, form fields): **3.0:1**

### `ensure_contrast()` Strategies

#### 1. Binary Strategy
**When**: Buttons, CTAs, chart labels (clarity > brand fidelity)

```python
def ensure_contrast_binary(fg: str, bg: str, min_ratio: float) -> str:
    """Return white (#FFFFFF) or black (#000000) based on which has better contrast."""
    if contrast_ratio(fg, bg) >= min_ratio:
        return fg
    white_contrast = contrast_ratio("#FFFFFF", bg)
    black_contrast = contrast_ratio("#000000", bg)
    return "#FFFFFF" if white_contrast > black_contrast else "#000000"
```

**Pros**: Always succeeds, maximizes legibility
**Cons**: Loses brand color

#### 2. Tint Strategy
**When**: Headings, accents (preserve brand color if possible)

```python
def ensure_contrast_tint(fg: str, bg: str, min_ratio: float) -> str:
    """Lighten or darken foreground to meet contrast, preserving hue."""
    # Convert to HSL
    # Adjust L (lightness) incrementally
    # Return adjusted color if contrast met, else fall back to binary
```

**Pros**: Preserves brand hue
**Cons**: May fail for mid-luminance colors

#### 3. Auto Strategy (Default)
**When**: Body text, general use

```python
def ensure_contrast_auto(fg: str, bg: str, min_ratio: float) -> str:
    """Try tint first, fall back to binary if needed."""
    adjusted = ensure_contrast_tint(fg, bg, min_ratio)
    if contrast_ratio(adjusted, bg) >= min_ratio:
        return adjusted
    return ensure_contrast_binary(fg, bg, min_ratio)
```

### Context-Based Strategy Selection

| Context | Strategy | Reason |
|---------|----------|--------|
| Button text | Binary | Clarity critical |
| CTA background | Binary | Visibility critical |
| Heading (h1-h3) | Tint | Preserve brand, but large text (3:1 ok) |
| Heading (h4-h6) | Auto | Smaller, needs 4.5:1 |
| Body text | Auto | Legibility critical |
| Chart labels | Binary | Data must be readable |
| Chart series | Tint | Preserve distinguishability |
| Link text | Auto | Must stand out from body |

---

## Phased Implementation Plan

### Phase 1: Foundation & Accessibility (6-8 hours)

**Goal**: Establish design system infrastructure and ensure accessibility compliance.

**Tasks**:
1. Create `config/brands/kearney/brand.yaml` with current hardcoded Kearney values
2. Obtain official Kearney logo files (SVG preferred)
3. Audit codebase for hardcoded Kearney values (search for `#7823DC`, `Inter`, etc.)
4. Implement `core/design_system/schema.py`:
   - `DesignSystem`, `ColorPalette`, `Typography`, `Logo` dataclasses
   - `load_from_yaml()` function
   - Validation methods
5. Implement `core/design_system/accessibility.py`:
   - `relative_luminance()`
   - `contrast_ratio()`
   - `ensure_contrast()` with binary/tint/auto strategies
6. Implement `core/design_system/applicator.py`:
   - `apply_design_system(ds, context) -> KDSTheme`
   - Enforce contrast on all text/bg pairs
7. Refactor `core/kds_theme.py`:
   - Simplify to token bucket (no logic, just data)
   - Add `resolve_theme(spec) -> KDSTheme` function
8. Add `design_system: str` field to spec.yaml schema
9. Wire engines to call `resolve_theme(spec)` and use theme tokens
10. Write tests:
    - `test_schema.py` (parsing, validation)
    - `test_accessibility.py` (WCAG calculations, ensure_contrast)
    - `test_applicator.py` (DS → KDSTheme conversion)

**Deliverable**: Kearney design system loads from YAML, all engines use theme tokens, accessibility enforced.

---

### Phase 2: Extraction + Manager + Privacy (5-7 hours)

**Goal**: Enable creation of client design systems from websites.

**Tasks**:
1. Implement `core/design_system/manager.py`:
   - `list_design_systems()`
   - `load_design_system(slug)`
   - `save_design_system(ds)`
   - `delete_design_system(slug)` (protect Kearney)
   - `get_default()` → "kearney"
2. Implement `core/design_system/extractor.py`:
   - `extract_from_url(url, mode="conservative")`
   - Conservative mode: single GET, parse inline styles
   - Moderate mode: fetch CSS files, parse variables
   - Return `{"colors": [...], "fonts": [...], "logo_url": ...}`
3. Add `create_from_url(url, mode)` to manager:
   - Call extractor
   - Build DesignSystem from extraction data
   - Prompt user for slug and meta.name
   - Save to `config/brands/{slug}/`
4. Implement `/design-system` command:
   - Menu: Create from URL | Create from assets | List | View | Delete
   - URL flow: prompt for URL and mode, run extraction, show preview, save
5. Add review/edit step after extraction:
   - Display extracted colors/fonts
   - Offer to manually adjust before saving
6. Update `.gitignore` and `config/brands/.gitignore`:
   - Ignore all client DS except Kearney
7. Write tests:
   - `test_manager.py` (CRUD operations)
   - `test_extractor.py` (mock HTTP responses, parse results)

**Deliverable**: Users can create client design systems from URLs, systems are gitignored.

---

### Phase 3: Asset Analysis (3-4 hours)

**Goal**: Support brand extraction from uploaded assets.

**Tasks**:
1. Implement `core/design_system/analyzer.py`:
   - `analyze_image(path)` → dominant colors, dimensions
   - `analyze_pdf(path)` → fonts, embedded images
   - `analyze_pptx(path)` → master slide colors, fonts
   - `analyze_assets(files)` → merged results
2. Add dependencies:
   - Optional: `PyMuPDF` for PDF parsing
   - Use existing: `python-pptx`, `Pillow`
3. Add `create_from_assets(files)` to manager:
   - Call analyzer
   - Merge with extraction data if URL also provided
   - Build DesignSystem
   - Save
4. Extend `/design-system` command:
   - Add "Create from assets" flow
   - Prompt for file paths or drag-and-drop
   - Show analysis preview
5. Write tests:
   - `test_analyzer.py` (parse sample files)

**Deliverable**: Users can upload logos/PDFs/PPTXs to supplement or replace web extraction.

---

### Phase 4: Polish & Integration (4-5 hours)

**Goal**: Integrate design system selection into project workflow.

**Tasks**:
1. Add `design_system` question to all interview trees:
   - After project name, before project type
   - Options: Kearney (default) | From library | Create new
   - If "Create new", invoke `/design-system` inline
2. Update `spec_manager.py`:
   - Validate `design_system` field exists
   - Default to "kearney" if missing
3. Implement logo rendering:
   - `webapp_engine.py`: Add `<img src="{logo_path}">` to header
   - `streamlit_engine.py`: Add `st.sidebar.image(logo_path)`
4. Add `kaca brand check` validation command:
   - Verify all text/bg pairs pass WCAG 2.1 AA
   - Report failures with suggested fixes
5. Create `config/skills/design-system.md`:
   - Best practices for web extraction
   - How to refine extracted brands
   - Accessibility guidelines
6. Write end-to-end tests:
   - `test_integration_design_system.py`
   - Full flow: create DS → interview → spec → engine → output
7. Update documentation:
   - Add design system section to CLAUDE.md
   - Update README.md with examples

**Deliverable**: Complete design system workflow integrated into KACA.

---

## Dependencies

### Required (Already Installed)
- `beautifulsoup4` - HTML parsing for web extraction
- `requests` - HTTP requests for web extraction
- `pyyaml` - Parse brand.yaml files
- `python-pptx` - PPTX analysis
- `Pillow` - Image analysis

### Optional (Install in Phase 3)
- `PyMuPDF` (`pip install pymupdf`) - PDF parsing for font/color extraction

### System Requirements
- Python 3.8+
- Internet connection (for web extraction only)

---

## Risks & Mitigations

### Risk 1: Phase 1 Refactor Touches Every Engine
**Impact**: Large diff, potential for regressions
**Mitigation**:
- Keep `KDSTheme` backward-compatible during transition
- Migrate engines incrementally (one per commit)
- Run full test suite after each engine migration
- Add `resolve_theme(spec)` as a wrapper, engines call it before rendering

### Risk 2: Web Extraction May Fail or Return Poor Results
**Impact**: User frustration, manual cleanup required
**Mitigation**:
- Set expectations: extraction is a starting point, not final
- Always show preview before saving
- Provide manual editing UI
- Fall back to Kearney if extraction fails completely

### Risk 3: Accessibility Enforcement May Alter Brand Colors Too Much
**Impact**: Client dissatisfaction with color changes
**Mitigation**:
- Use `tint` strategy by default to preserve hue
- Explain WCAG requirements in preview
- Offer "View contrast report" to show which pairs failed
- Allow user to accept non-compliant colors with explicit warning

### Risk 4: Client DS Privacy Leak (Accidental Commit)
**Impact**: Legal/ethical concerns
**Mitigation**:
- Add `.gitignore` rules in Phase 2 (before any client DS created)
- Hook to warn if `config/brands/*` (except Kearney) staged
- Documentation emphasizes privacy-by-default

---

## Open Decisions

These decisions are documented but deferred to implementation time:

### 1. Brand Library Location
**Options**:
- A: `config/brands/` (current plan, in-repo)
- B: `~/.kaca/brands/` (global, shared across projects)

**Tradeoff**: A is simpler, B allows brand reuse across templates.
**Decision**: Start with A, add B in future enhancement if requested.

### 2. Logo File Format Preference
**Options**:
- SVG (vector, scales infinitely)
- PNG (raster, fixed resolution)

**Decision**: Prefer SVG, accept PNG. Warn if PNG < 200px wide.

### 3. Design System Versioning
**Options**:
- Simple slug-based (current plan): `acme-corp`, `acme-corp-2024`
- Semantic versioning in brand.yaml: `version: "1.2.0"`

**Decision**: Simple slugs for now. Add semantic versioning if clients request rollback capability.

### 4. Chart Color Palette Size
**Options**:
- Fixed 6 colors (current plan)
- Dynamic based on data cardinality
- User-specified

**Decision**: Fixed 6 for now. If more needed, repeat palette (color1, color2, ..., color6, color1, ...).

---

## Pre-Implementation Checklist

Before starting Phase 1, complete these tasks:

- [ ] **Audit Hardcoded Kearney Values**: Search codebase for:
  - `#7823DC` (Kearney purple)
  - `#1E1E1E` (dark background)
  - `#FFFFFF` (white text)
  - `Inter` (font family)
  - `Arial` (fallback font)
  - Create a spreadsheet mapping each occurrence to its engine/module

- [ ] **Obtain Official Kearney Logo Files**:
  - Request SVG files from Kearney brand team
  - Primary logo (horizontal)
  - Icon/mark (square)
  - Confirm usage rights for AI-generated outputs

- [ ] **Confirm Kearney Brand Token Values**:
  - Verify `#7823DC` is correct primary color
  - Confirm font is Inter (not Lato or similar)
  - Get official spacing/border radius values if available

- [ ] **Decide on Brand Library Location** (optional):
  - If using `~/.kaca/brands/`, create directory and update manager.py paths
  - If staying with `config/brands/`, no action needed

---

## Success Criteria

Implementation is complete when ALL of the following are true:

- [ ] Kearney design system loads from `config/brands/kearney/brand.yaml`
- [ ] No hardcoded hex color values exist in any engine file
- [ ] All text/background pairs in outputs pass WCAG 2.1 AA contrast
- [ ] A client design system can be created from a website URL in under 2 minutes
- [ ] Client design systems do NOT appear in `git status` (gitignored)
- [ ] Logos appear in dashboard headers and Streamlit sidebars
- [ ] Logos do NOT appear in charts, PPTX, or DOCX outputs
- [ ] `/design-system` command offers Create | List | View | Delete options
- [ ] Interview includes "Which design system?" question
- [ ] `spec.yaml` includes `design_system: "kearney"` field
- [ ] `kaca brand check` command validates WCAG compliance
- [ ] All 673+ existing tests pass
- [ ] New design system tests achieve >90% coverage

---

## Related Files

Reference these files when implementing:

### Core Modules
- `core/kds_theme.py` - Current theme implementation (to be simplified)
- `core/brand_guard.py` - Current brand validation (to be extended)
- `core/webapp_engine.py` - Will need logo rendering in header
- `core/chart_engine.py` - Will use theme.chart_palette
- `core/interview_engine.py` - Will add design system question

### Configuration
- `config/skills/kearney-webapp.md` - Brand rules documentation
- `config/interviews/*.yaml` - Interview trees to update

### Specifications
- `docs/spec_schema.md` - spec.yaml schema (add design_system field)
- `templates/spec_template.yaml` - Template for new projects

### Tests
- `tests/test_kds_theme.py` - Theme tests to update
- `tests/test_brand_guard.py` - Brand validation tests to extend

---

## Next Steps

When ready to implement:

1. **Review this specification** with the team
2. **Complete Pre-Implementation Checklist** (above)
3. **Create feature branch**: `git checkout -b feature/design-system-module`
4. **Implement Phase 1** (Foundation & Accessibility)
5. **Run tests and commit**: `git commit -m "feat(design-system): Phase 1 - Foundation & Accessibility"`
6. **Continue with Phases 2-4**
7. **Open pull request** for review
8. **Merge to main** after approval

Estimated total time: **18-24 hours** (spread over 3-4 days)

---

**Document Status**: Ready for Implementation
**Last Updated**: 2025-12-03
**Owner**: KACA Core Team
