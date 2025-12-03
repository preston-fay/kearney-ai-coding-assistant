# Troubleshooting Guide

Solutions for common issues with the Kearney AI Coding Assistant.

## Setup Issues

### Python Not Found

**Symptom:**
```
[ERROR] Python is not installed or not in PATH
```

**Windows Solution:**
1. Open Kearney Software Center
2. Search for "Python"
3. Install Python 3.10 or higher
4. Restart your terminal
5. Run setup again

**macOS Solution:**
```bash
brew install python3
```

### Virtual Environment Creation Failed

**Symptom:**
```
[ERROR] Failed to create virtual environment
```

**Causes:**
- Insufficient permissions
- Disk space issue
- Corrupted Python installation

**Solution:**
1. Delete existing `.venv` folder if present
2. Ensure you have write permissions to the directory
3. Try creating manually:
   ```bash
   python3 -m venv .venv
   ```

### Module Installation Failed

**Symptom:**
```
[ERROR] Failed to install dependencies
```

**Windows Solution:**
1. Check your network connection
2. If behind proxy, configure pip:
   ```
   set HTTP_PROXY=http://proxy.kearney.com:8080
   set HTTPS_PROXY=http://proxy.kearney.com:8080
   ```
3. Retry setup

**macOS Solution:**
```bash
export HTTP_PROXY=http://proxy.kearney.com:8080
export HTTPS_PROXY=http://proxy.kearney.com:8080
bash bootstrap/setup_mac.sh
```

---

## Windows-Specific Issues

### Script Execution Policy

**Symptom:**
```
cannot be loaded because running scripts is disabled on this system
```

**Solution:**
The setup uses `.bat` files specifically to avoid this issue. If you still encounter it:

1. Open PowerShell as Administrator
2. Run: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
3. Confirm with "Y"

### Path Too Long

**Symptom:**
```
[ERROR] The filename or extension is too long
```

**Solution:**
1. Move the project to a shorter path (e.g., `C:\KACA`)
2. Or enable long paths in Windows:
   - Run `regedit`
   - Navigate to `HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\FileSystem`
   - Set `LongPathsEnabled` to `1`
   - Restart

### Permission Denied

**Symptom:**
```
PermissionError: [Errno 13] Permission denied
```

**Solution:**
1. Close any programs using project files
2. Check if antivirus is blocking
3. Run Claude Desktop as Administrator (temporary)
4. Move project to a user-writable location

---

## Project Issues

### "No Project Initialized"

**Symptom:**
```
Error: No project found. Run /init first.
```

**Solution:**
1. Ensure you're in the correct directory
2. Run `/init` to create a new project
3. Or check if `project_state/status.json` exists

### State File Corrupted

**Symptom:**
```
Error: Failed to load project state
JSONDecodeError: ...
```

**Solution:**
1. Run the state validator to diagnose:
   ```python
   from core.state_validator import validate_project_state, attempt_repair
   valid, results = validate_project_state(Path("."))
   if not valid:
       repairs = attempt_repair(Path("."))
   ```

2. Or use recovery commands:
   - `/rollback` - Restore from previous archive
   - `/reset` - Archive corrupted state and start fresh

3. Manual fix:
   - Back up `project_state/status.json`
   - Fix JSON syntax errors
   - Or delete and let system regenerate

### Intake Questions Loop

**Symptom:**
Claude keeps asking the same intake questions

**Solution:**
1. Check if responses are being saved
2. Verify `project_state/requirements.yaml` exists
3. Ensure you complete all required questions
4. Type "done" or "finish" to end intake

### Plan Not Generating

**Symptom:**
`/plan` produces empty or incomplete plan

**Solution:**
1. Verify intake is complete: check `requirements.yaml`
2. Ensure requirements include necessary fields:
   - Project name
   - Project type/template
   - At least one deliverable
3. Re-run `/interview` if needed

---

## Output Issues

### Charts Not Generating

**Symptom:**
No charts created in `outputs/charts/`

**Possible Causes:**
1. Data file not found
2. Matplotlib not installed
3. Invalid data format

**Solution:**
1. Verify data path in requirements:
   ```yaml
   data_source: path/to/your/data.csv
   ```
2. Check data file exists and is readable
3. Ensure CSV/Excel has valid headers
4. Check for matplotlib errors in Claude's output

### Brand Violations

**Symptom:**
`/review` reports color or content violations

**Solution:**

**For Color Violations:**
- Check source files for hardcoded colors
- Only use these colors:
  ```
  Primary: #7823DC (Kearney Purple)
  Grays: #F5F5F5, #E0E0E0, #CCCCCC, #999999, #666666, #333333
  Background: #1E1E1E (dark), #FFFFFF (light)
  ```
- Never use green, red, blue, or other hues

**For Emoji Violations:**
- Search outputs for emoji characters
- Remove any emoji from:
  - Chart titles
  - Report text
  - Slide content

**For Gridline Violations:**
- Regenerate charts using core/chart_engine.py
- Manual fix: Edit chart and remove gridlines

### PowerPoint Formatting Issues

**Symptom:**
Slides have wrong fonts or colors

**Solution:**
1. Ensure python-pptx is installed:
   ```
   pip install python-pptx
   ```
2. Regenerate presentation using `/execute`
3. Check that no external templates are being used
4. Verify Inter font is installed on your system

---

## Performance Issues

### Slow Response Times

**Symptom:**
Claude takes a long time to respond

**Possible Causes:**
- Large data files
- Many files in outputs directory
- Complex plan with many tasks

**Solution:**
1. Use smaller data samples for initial analysis
2. Clean up old outputs: `rm -rf outputs/*`
3. Break large projects into smaller phases

### Memory Errors

**Symptom:**
```
MemoryError or process killed
```

**Solution:**
1. Reduce data file size (sample your data)
2. Process data in chunks
3. Close other applications
4. Increase Python memory limit (if possible)

---

## Claude Desktop Issues

### Commands Not Recognized

**Symptom:**
Claude doesn't respond to `/project:*` commands

**Solution:**
1. Ensure you opened the project folder correctly:
   - File > Open Folder > Select KACA directory
2. Check `.claude/commands/` directory exists
3. Verify command files have `.md` extension
4. Restart Claude Desktop

### Settings Not Applied

**Symptom:**
Hooks or permissions not working

**Solution:**
1. Check `.claude/settings.json` syntax
2. Validate JSON format (no trailing commas)
3. Restart Claude Desktop after changes
4. Check Claude Desktop logs for errors

### Session Lost

**Symptom:**
Progress lost after closing Claude

**Solution:**
1. Always let Claude finish current task before closing
2. Check `project_state/status.json` exists
3. Run `/status` to see saved progress
4. If state is lost, you'll need to re-run from last known point

---

## Data Issues

### CSV Parsing Errors

**Symptom:**
```
ParserError: Error tokenizing data
```

**Solution:**
1. Check CSV encoding (use UTF-8)
2. Verify delimiter (comma vs semicolon)
3. Look for unescaped quotes in data
4. Try opening in Excel and re-saving as CSV

### Excel File Errors

**Symptom:**
```
openpyxl.utils.exceptions.InvalidFileException
```

**Solution:**
1. Ensure file is `.xlsx` (not `.xls`)
2. Check file isn't password-protected
3. Verify file isn't corrupted:
   - Try opening in Excel
   - Re-save as new file
4. Update openpyxl: `pip install --upgrade openpyxl`

### Missing Columns

**Symptom:**
```
KeyError: 'column_name'
```

**Solution:**
1. Check exact column names in your data
2. Column names are case-sensitive
3. Remove leading/trailing spaces from headers
4. Update requirements with correct column names

---

## Large File Issues

### Memory Errors with Large CSV

**Symptom:**
```
MemoryError when loading large file
```

**Solution:**
Use DuckDB instead of loading into memory:

```python
from core.data_handler import ProjectDatabase

db = ProjectDatabase(Path("."))
db.register_file("data/raw/large_file.csv")
# Query without loading entire file
result = db.query_df("SELECT * FROM large_file LIMIT 1000")
```

### DuckDB Database Locked

**Symptom:**
```
duckdb.IOException: database is locked
```

**Solution:**
1. Close any other Python processes accessing the database
2. Delete `data/project.duckdb` and re-register files
3. Use separate database connections for different operations

---

## Session Management Issues

### Context Getting Full

**Symptom:**
Claude mentions context is getting long or responses slow down

**Solution:**
Run `/compact` to:
1. Summarize completed work
2. Archive detailed logs
3. Reset to clean state with project awareness

### Lost Progress After Session Reset

**Symptom:**
Progress lost after closing Claude or system crash

**Solution:**
1. Check `project_state/logs/sessions/` for recent session logs
2. Run `/rollback archive` to list available archives
3. Restore from the most recent good state:
   ```
   /rollback archive 1
   ```

---

## Recovery Commands

### /reset Not Working

**Symptom:**
Reset command fails or doesn't archive properly

**Solution:**
1. Check disk space
2. Verify write permissions to project_state/
3. Manually archive:
   ```python
   from core.state_validator import archive_state, reset_state
   archive_state(Path("."), reason="manual reset")
   reset_state(Path("."))
   ```

### /rollback Shows No Archives

**Symptom:**
Rollback command shows empty archive list

**Solution:**
Archives are only created by:
- Running `/reset`
- Restoring from another archive
- Manually calling `archive_state()`

If no archives exist, you'll need to start fresh with `/interview`.

---

## Brand Override Issues

### Custom Brand Not Applied

**Symptom:**
Brand override settings not being used

**Solution:**
1. Check file location: `config/brand_override.yaml`
2. Ensure `enabled: true` is set
3. Validate YAML syntax
4. Check that colors are valid hex codes (#RRGGBB)

### Enforced Rules Still Active

**Symptom:**
Can't disable no_emojis or no_gridlines rules

**This is expected behavior.** These rules are always enforced regardless of brand override:
- no_emojis
- no_gridlines
- data_labels_outside

---

## Getting More Help

If these solutions don't resolve your issue:

1. **Check logs**: Look at `project_state/logs/commands/command_log.jsonl`
2. **Run diagnostics**:
   ```python
   from core.state_validator import validate_project_state, print_validation_results
   valid, results = validate_project_state(Path("."))
   print_validation_results(results)
   ```
3. **Verify setup**: Re-run `python3 core/prereq_checker.py`
4. **Test modules**: Run `pytest tests/` to verify installation
5. **Fresh start**: Run `/reset` or delete `project_state/` and `.venv/`, then re-setup
6. **Contact support**: Reach out with:
   - Error message (full text)
   - Steps to reproduce
   - Operating system version
   - Python version (`python --version`)
   - Command log from `project_state/logs/commands/command_log.jsonl`

### Support Channels

- **Teams**: #Claude-Code-Help
- **Office Hours**: Wednesdays 2-3pm ET
- **Email**: da-claude@kearney.com

---

## Workspace Issues

### Working in Template Repository

**Symptom:**
```
WARNING: You are in the KACA template repository, not a scaffolded project.

Project work should happen in scaffolded projects, not the template.
```

**Why This Happens:**
You opened the template repository in Claude Code instead of a scaffolded project. Working in the template pollutes the shared codebase.

**Solution:**

**Mac/Linux:**
```bash
cd ~/kaca-template
python scaffold.py my-project --path ~/Projects/
```

**Windows (PowerShell):**
```powershell
cd $env:USERPROFILE\kaca-template
python scaffold.py my-project --path $env:USERPROFILE\Projects
```

Then open `~/Projects/my-project/` (or `C:\Users\YourName\Projects\my-project\`) in Claude Code.

### Accidentally Started Work in Template

**Symptom:**
You created files, wrote code, or generated outputs in the template repository.

**Solution:**

1. **Identify the work you did:**
   ```bash
   git status
   ```

2. **If work is in `data/`, `outputs/`, `exports/`, or `project_state/`:**
   These directories are gitignored. Your work is safe but local.
   - Create a new project: `python scaffold.py my-project --path ~/Projects/`
   - Copy your data: `cp -r data/raw/* ~/Projects/my-project/data/raw/`
   - Start fresh in the new project

3. **If work modified tracked files:**
   ```bash
   # See what changed
   git diff

   # Discard changes to template files
   git checkout -- core/ config/ .claude/

   # Or reset everything
   git reset --hard HEAD
   ```

4. **If you committed changes:**
   ```bash
   # Undo the last commit (keep changes as unstaged)
   git reset HEAD~1

   # Then move work to a proper project
   ```

### Symlinks/Junctions Broken

**Symptom:**
```
FileNotFoundError: core/chart_engine.py
```
or `core/` and `config/` appear as empty directories.

**Cause:**
The symlinks (Mac/Linux) or junctions (Windows) to the template are broken, usually because the template was moved or deleted.

**Solution:**

**Mac/Linux:**
```bash
# Check where symlink points
ls -la core/

# If broken, recreate
rm core config
ln -s ~/kaca-template/core core
ln -s ~/kaca-template/config config
```

**Windows (PowerShell as Admin):**
```powershell
# Check junction
dir core

# If broken, recreate
rmdir core
rmdir config
cmd /c mklink /J core $env:USERPROFILE\kaca-template\core
cmd /c mklink /J config $env:USERPROFILE\kaca-template\config
```

### Missing .kaca-version.json

**Symptom:**
Workspace guard thinks you're in the template even though you scaffolded.

**Cause:**
The `.kaca-version.json` file is missing from your project root.

**Solution:**

Create the file manually:
```bash
echo '{"version": "2.0.0", "scaffolded": "2024-01-01", "template": "kaca"}' > .kaca-version.json
```

Or re-scaffold the project (this will preserve your data if in `data/raw/`).

### Template Repository Has Pollution

**Symptom:**
Your template repo has `project_state/`, filled `data/` directories, or `outputs/`.

**Solution:**
These directories are gitignored, so they won't affect the template for others:

```bash
# Verify they're not tracked
git status

# Clean up if needed (removes untracked files)
git clean -fd data/ outputs/ exports/ project_state/
```

**WARNING:** `git clean -fd` permanently deletes files. Check `git status` first.
