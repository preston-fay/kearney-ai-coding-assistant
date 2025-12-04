# /project:design-system - Manage Design Systems

Manage brand design systems for multi-client support.

## Usage

```
/project:design-system
/project:design-system list
/project:design-system view <slug>
/project:design-system create <url>
/project:design-system delete <slug>
```

## Workflow

1. **Present menu:**
   ```
   DESIGN SYSTEM MANAGER
   ====================

   What would you like to do?

   1. List available design systems
   2. View design system details
   3. Create from client website
   4. Create manually
   5. Delete design system

   Enter choice (1-5):
   ```

2. **For LIST (option 1):**
   ```python
   from core.design_system import list_design_systems, get_design_system_info

   systems = list_design_systems()
   for slug in systems:
       info = get_design_system_info(slug)
       print(f"- {slug}: {info['name']} ({info['primary_color']})")
   ```

   Display:
   ```
   AVAILABLE DESIGN SYSTEMS
   ========================

   - kearney: Kearney (#7823DC) [DEFAULT]
   - acme-corp: Acme Corporation (#0066CC)

   Total: 2 design systems

   To use in a project, add to spec.yaml:
     project:
       design_system: "slug-here"
   ```

3. **For VIEW (option 2):**
   Ask: "Which design system? (Enter slug):"

   ```python
   from core.design_system import load_design_system

   ds = load_design_system(slug)
   print(f"Name: {ds.meta.name}")
   print(f"Primary: {ds.colors.primary}")
   # ... display all fields
   ```

4. **For CREATE FROM URL (option 3):**
   Ask sequentially:
   - "Enter client website URL:"
   - "Enter brand name (e.g., Acme Corporation):"
   - "Enter slug (e.g., acme-corp):" (suggest based on name)
   - "Extraction mode? (conservative/moderate):" (default: conservative)

   ```python
   from core.design_system import create_from_url, slugify

   suggested_slug = slugify(name)
   ds = create_from_url(url, slug, name, mode)

   print(f"Created: {ds.meta.name}")
   print(f"Primary color: {ds.colors.primary}")
   print(f"Saved to: config/brands/{ds.meta.slug}/brand.yaml")
   ```

   Display:
   ```
   DESIGN SYSTEM CREATED
   =====================

   Name: Acme Corporation
   Slug: acme-corp

   Colors Extracted:
   - Primary: #0066CC
   - Secondary: #FF6600

   Fonts:
   - Heading: Open Sans
   - Body: Roboto

   Logo: https://acme.com/logo.png

   Saved to: config/brands/acme-corp/brand.yaml

   NOTE: Client brands are gitignored for privacy.

   To use, add to spec.yaml:
     project:
       design_system: "acme-corp"
   ```

5. **For CREATE MANUALLY (option 4):**
   Guide user to create a brand.yaml manually:
   ```
   To create a design system manually:

   1. Create directory: config/brands/<slug>/
   2. Create brand.yaml with this template:

   [Show template from config/brands/README.md]

   3. Add any logo files to the same directory
   ```

6. **For DELETE (option 5):**
   Ask: "Which design system to delete? (Enter slug):"

   ```python
   from core.design_system import delete_design_system, get_default

   if slug == get_default():
       print("ERROR: Cannot delete the default Kearney design system.")
   else:
       confirm = input(f"Delete '{slug}'? This cannot be undone. (yes/no): ")
       if confirm == "yes":
           delete_design_system(slug)
           print(f"Deleted: {slug}")
   ```

## Rules

- **Kearney cannot be deleted** - It is the default design system.
- **Client brands are gitignored** - They are stored locally only.
- **Extraction requires network access** - The create from URL option fetches the website.

## Error Handling

- Network errors during extraction: Show message with suggestion to try again
- Invalid URL: Show error and ask for valid URL
- Slug already exists: Ask to overwrite or choose different slug

## Examples

### List all design systems
```
/project:design-system list

AVAILABLE DESIGN SYSTEMS
========================

- kearney: Kearney (#7823DC) [DEFAULT]
- acme-corp: Acme Corporation (#0066CC)

Total: 2 design systems
```

### Create from URL
```
/project:design-system create https://example.com

Extracting brand tokens from https://example.com...

Enter brand name: Example Inc
Enter slug [example-inc]:
Extraction mode (conservative/moderate) [conservative]:

DESIGN SYSTEM CREATED
=====================

Name: Example Inc
Slug: example-inc
Primary: #FF5722
...
```
