# /profile

---
name: profile
description: View and manage your KACA user profile and preferences
---

Manage your persistent user profile that applies across all KACA projects.

## Usage

```
/profile                    # Show current profile
/profile show               # Show current profile
/profile set <path> <value> # Set a preference
/profile init               # Create default profile
/profile reset              # Reset to defaults
```

## Behavior

### View Profile (`/profile` or `/profile show`)

1. Load profile from `~/.kaca/profile.yaml`
2. Display formatted profile with sections:
   - User info
   - Interview preferences
   - Chart preferences
   - Presentation preferences
   - Document preferences
   - Client overrides

### Set Preference (`/profile set <path> <value>`)

1. Parse dot-notation path (e.g., `preferences.chart.default_format`)
2. Validate the path is a known preference
3. Update the value
4. Save profile
5. Confirm the change

**Valid paths:**
- `user.name` - Your name
- `preferences.interview.default_mode` - "full" or "express"
- `preferences.chart.default_format` - "svg" or "png"
- `preferences.chart.default_size` - "presentation" or "document"
- `preferences.chart.always_include_source` - true/false
- `preferences.presentation.always_include_exec_summary` - true/false
- `preferences.presentation.default_slide_count_target` - number
- `preferences.presentation.preferred_closing` - "next_steps" or "thank_you"
- `preferences.document.include_methodology_appendix` - true/false
- `defaults.visualization.insight_depth` - "brief" or "detailed"

### Initialize Profile (`/profile init`)

1. Create `~/.kaca/` directory if needed
2. Write default profile.yaml
3. Show the created profile

### Reset Profile (`/profile reset`)

1. Confirm with user
2. Replace profile with defaults
3. Show the reset profile

## Examples

```
User: /profile set user.name Alex
Claude: Updated user.name to "Alex"

User: /profile set preferences.interview.default_mode express
Claude: Updated preferences.interview.default_mode to "express"
       Future interviews will use express mode by default.

User: /profile set preferences.presentation.default_slide_count_target 20
Claude: Updated preferences.presentation.default_slide_count_target to 20
```

## Implementation Notes

Use these core functions:
- `from core.memory import load_user_profile, save_user_profile, update_user_preference`
- `from core.memory import get_default_profile`

When displaying the profile, format it nicely with sections and explanations of what each setting does.
