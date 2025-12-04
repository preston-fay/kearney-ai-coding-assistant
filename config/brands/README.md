# KACA Design System Library

This directory contains design system definitions for KACA outputs.

## Structure

```
brands/
├── kearney/          # Default design system (committed)
│   ├── brand.yaml
│   ├── logo_primary.svg
│   └── logo_icon.svg
├── {client-slug}/    # Client design systems (local only, gitignored)
│   ├── brand.yaml
│   └── logo_primary.png
```

## Usage

Design systems are selected per-project in `spec.yaml`:

```yaml
project:
  name: "My Project"
  design_system: "kearney"  # or "acme-corp", etc.
```

## Creating a New Design System

Use the `/design-system` command in Claude Code:

```
/design-system
```

Options:
1. Create from website URL
2. Create from uploaded assets
3. List available design systems
4. View details
5. Delete

## brand.yaml Template

```yaml
# Design System Configuration
meta:
  name: "Client Name"
  slug: "client-slug"
  version: "1.0.0"
  source_url: "https://client.com"  # Optional

colors:
  primary: "#0066CC"           # Main brand color
  secondary: "#004499"         # Secondary (optional)
  accent: "#FF6600"            # Accent (optional)
  chart_palette:               # For data visualizations
    - "#0066CC"
    - "#FF6600"
    - "#00AA88"
  forbidden:                   # Colors to never use
    - "#00FF00"

typography:
  heading:
    family: "Open Sans"
    fallback: "Arial, sans-serif"
    weights: [400, 600, 700]
  body:
    family: "Roboto"
    fallback: "Arial, sans-serif"
    weights: [400, 500]

backgrounds:
  dark: "#1E1E1E"
  light: "#FFFFFF"

text:
  on_dark: "#FFFFFF"
  on_light: "#333333"

logos:
  primary:
    path: "logo_primary.png"
    placement: [webapp_header, dashboard_header]
```

## Privacy

Client design systems are **gitignored by default**. Only the Kearney design system is committed to the repository.

To share a client DS with teammates, manually copy the `config/brands/{client-slug}/` directory.

## See Also

- [Design System Module Specification](../../docs/backlog/BL-001-design-system-module.md)
- [Kearney Brand Guidelines](./kearney/brand.yaml)
