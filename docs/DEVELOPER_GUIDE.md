# KACA Developer Guide

For contributors and maintainers of the KACA template.

---

## Architecture Overview

```
kearney-ai-coding-assistant/
+-- core/                    # Python engines (the brains)
|   +-- brand_guard.py       # Brand compliance validation
|   +-- chart_engine.py      # Matplotlib chart generation
|   +-- slide_engine.py      # PowerPoint generation
|   +-- document_engine.py   # Word document generation
|   +-- spreadsheet_engine.py# Excel generation
|   +-- webapp_engine.py     # HTML/Streamlit/React generation
|   +-- kds_theme.py         # Design system tokens
|   +-- kds_data.py          # Data abstraction layer
|   +-- kds_utils.py         # Safe file I/O utilities
|   +-- streamlit_utils.py   # Streamlit deployment helpers
|   +-- interview_engine.py  # Requirements gathering
|   +-- spec_manager.py      # Specification CRUD
|   +-- state_manager.py     # Project state management
|   +-- workspace_guard.py   # Template vs project detection
+-- config/
|   +-- interviews/          # Interview tree YAML files
|   +-- skills/              # Best practice documentation
|   +-- templates/           # Output templates
+-- .claude/
|   +-- commands/            # Slash command definitions
|   +-- agents/              # Agent persona definitions
+-- scaffold.py              # Project creation script
+-- docs/                    # Documentation
+-- tests/                   # Test suite
```

### Design Principles

1. **LLM designs, Python executes**: Claude creates specs; engines execute deterministically
2. **Brand compliance is programmatic**: `brand_guard.py` enforces rules, not suggestions
3. **State enables resumption**: `project_state/` allows picking up where you left off
4. **Symlinks share infrastructure**: Projects link to template `core/` and `config/`
5. **Safe file I/O**: All file writes use `safe_write_text()` to prevent encoding errors

---

## Adding a New Engine

1. Create `core/new_engine.py`
2. Follow the pattern:
   ```python
   from core.kds_theme import KDSTheme
   from core.kds_utils import safe_write_text
   from core.brand_guard import check_file

   class KDSNewThing:
       def __init__(self, theme: KDSTheme = None):
           self.theme = theme or KDSTheme()

       def generate(self, output_path: Path) -> Path:
           # ... generation logic using safe_write_text
           safe_write_text(output_path, content)

           # Always validate output
           violations = check_file(output_path)
           for v in violations:
               logger.warning(f"Brand violation: {v.message}")

           return output_path
   ```
3. Add exports to `core/__init__.py`
4. Create skill file `config/skills/kearney-newthing.md`
5. Add tests in `tests/test_new_engine.py`

---

## Adding a New Project Type

1. Create interview tree: `config/interviews/newtype.yaml`
2. Add to `PROJECT_TYPES` in `core/interview_engine.py`
3. Document in `docs/USER_GUIDE.md`

---

## Testing

```bash
# Run all tests
python3 -m pytest tests/ -v

# Run specific test file
python3 -m pytest tests/test_brand_guard.py -v

# Run with coverage
python3 -m pytest tests/ --cov=core --cov-report=html
```

### Test Conventions

- Use `tmp_path` fixture for file operations
- Use `monkeypatch` for changing cwd
- Test both happy path and error cases
- Verify brand compliance in generated outputs

---

## Workspace Protection

The template includes protection against accidental work in the template repo:

### How It Works

1. `scaffold.py` creates `.kaca-version.json` in scaffolded projects
2. `workspace_guard.py` checks for this file
3. Missing file + presence of `scaffold.py` = template repo
4. Commands can call `verify_workspace()` to block execution

### Adding Protection to Commands

```python
from core.workspace_guard import verify_workspace

def my_command():
    verify_workspace()  # Raises RuntimeError if in template
    # ... rest of command
```

Or use the decorator:

```python
from core.workspace_guard import require_project_workspace

@require_project_workspace()
def my_function():
    # Only runs in scaffolded projects
    pass
```

---

## Safe File I/O

Always use safe utilities for file operations:

```python
from core.kds_utils import safe_write_text, safe_read_text

# Writing - removes emojis and handles encoding errors
safe_write_text(path, content)

# Reading - handles encoding errors gracefully
content = safe_read_text(path)
```

This prevents Unicode crashes from emojis and surrogate pairs.

---

## Brand Guard

### Adding New Checks

Edit `core/brand_guard.py`:

```python
def check_new_rule(content: str, file_path: str) -> List[BrandViolation]:
    violations = []
    # ... check logic
    if problem_found:
        violations.append(BrandViolation(
            file_path=file_path,
            rule="NEW_RULE",
            message="Description of issue",
            line_number=line_num,
            severity="error"
        ))
    return violations
```

### Severity Levels

- `error`: Must be fixed before export
- `warning`: Should be fixed, doesn't block export

---

## Release Process

1. Update `VERSION` file
2. Update CLAUDE.md version number if needed
3. Run full test suite: `python3 -m pytest tests/ -v`
4. Update docs if needed
5. Create git tag: `git tag v2.x.x`
6. Push to main

---

## Code Style

- Type hints on all public functions
- Docstrings on all classes and public methods
- No emojis anywhere in code or comments
- Use `safe_write_text()` for file output
- Run `brand_guard` on generated outputs
- Follow existing patterns in the codebase

---

## Common Pitfalls

### Don't Use Emojis

```python
# Bad
page_icon = "..."  # any emoji

# Good
page_icon = "o"  # ASCII only
```

### Don't Use Direct write_text()

```python
# Bad
path.write_text(content)

# Good
from core.kds_utils import safe_write_text
safe_write_text(path, content)
```

### Don't Forget Brand Checks

```python
# Bad
def generate():
    save_file()
    return path

# Good
def generate():
    save_file()
    violations = check_file(path)
    for v in violations:
        logger.warning(f"Brand violation: {v.message}")
    return path
```

---

## Getting Help

- **Codebase questions**: Read the existing code first
- **Architecture decisions**: Check design principles above
- **Bug reports**: Include test case and expected behavior

---

*Kearney Digital & Analytics*
