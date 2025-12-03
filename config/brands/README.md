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

## Privacy

Client design systems are **gitignored by default**. Only the Kearney design system is committed to the repository.

To share a client DS with teammates, manually copy the `config/brands/{client-slug}/` directory.

## See Also

- [Design System Module Specification](../../docs/backlog/BL-001-design-system-module.md)
- [Kearney Brand Guidelines](./kearney/brand.yaml)
