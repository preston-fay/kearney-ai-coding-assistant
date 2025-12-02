# /project:init - Initialize New Project

Initialize a new project from a template.

## Usage

```
/project:init
```

## Workflow

1. **Ask for project details:**
   - Project name (slug format, e.g., "acme-revenue-q4")
   - Template type: analytics, presentation, or webapp

2. **Create project structure:**
   ```python
   from core.state_manager import init_project

   state = init_project(project_name, template)
   ```

3. **Load template configuration:**
   - Read `config/templates/{template}.yaml`
   - Display template-specific guidance

4. **Confirm initialization:**
   ```
   Project initialized: {project_name}
   Template: {template}

   Next step: Run /project:intake to gather requirements.
   ```

## Template Options

### analytics
For data analysis projects. Includes:
- Data profiling workflow
- Chart generation
- Report creation

### presentation
For slide deck creation. Includes:
- Content structuring
- KDS slide templates
- Export to PPTX

### webapp
For web application projects. Includes:
- Component scaffolding
- Style templates
- Build configuration

## Output

Creates:
- `project_state/status.json` with initial state
- Records 'init' action in history
