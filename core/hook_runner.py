"""
Kearney Hook Runner - Cross-Platform Hook Dispatcher

Handles post-edit and pre-commit events for Claude Code hooks.
Replaces shell scripts to ensure Windows compatibility.

Usage:
    python -m core.hook_runner brand_check <filepath>
    python -m core.hook_runner session_end
    python core/hook_runner.py post-edit <file>
    python core/hook_runner.py pre-commit

This module is called by Claude Code hooks configured in .claude/settings.json.
"""

import json
import os
import sys
import logging
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
)
logger = logging.getLogger(__name__)


def handle_post_edit(target: Path) -> int:
    """
    Run after Claude writes a file to outputs/ or exports/.

    Validates brand compliance and blocks if violations found.

    Args:
        target: Path to the file that was written.

    Returns:
        0 if no violations, 1 if violations found.
    """
    # Import here to avoid circular imports
    from core import brand_guard

    if not target.exists():
        # File was deleted, nothing to check
        return 0

    # Only check relevant file types
    checkable_extensions = {
        ".png", ".jpg", ".jpeg", ".svg",
        ".py", ".html", ".htm", ".css", ".scss",
        ".md", ".txt", ".json", ".yaml", ".yml",
    }

    if target.suffix.lower() not in checkable_extensions:
        logger.debug(f"Skipping {target} - not a checkable file type")
        return 0

    issues = brand_guard.check_file(target)

    if issues:
        logger.error(f"BRAND VIOLATION: {target}")
        for issue in issues:
            location = f":{issue.line_number}" if issue.line_number else ""
            logger.error(f"  [{issue.rule}]{location} {issue.message}")
        logger.error("")
        logger.error("Fix these issues before continuing.")
        return 1

    logger.info(f"Brand check passed: {target}")
    return 0


def handle_pre_commit() -> int:
    """
    Run before git commit.

    Validates all outputs and exports. Warns if core files missing.
    Blocks commit if brand violations found.

    Returns:
        0 if all checks pass, 1 if violations found.
    """
    # Import here to avoid circular imports
    from core import brand_guard, state_manager

    all_issues = []

    # Check outputs directory
    outputs_dir = Path("outputs")
    if outputs_dir.exists():
        logger.info("Checking outputs/ directory...")
        issues = brand_guard.check_directory(outputs_dir)
        all_issues.extend(issues)
        if not issues:
            logger.info("  No violations found.")

    # Check exports directory
    exports_dir = Path("exports")
    if exports_dir.exists():
        logger.info("Checking exports/ directory...")
        issues = brand_guard.check_directory(exports_dir)
        all_issues.extend(issues)
        if not issues:
            logger.info("  No violations found.")

    # Warn if core state files missing (non-blocking)
    state_warnings = state_manager.warn_if_missing_core_files()
    for warning in state_warnings:
        logger.warning(f"WARNING: {warning}")

    # Report violations
    if all_issues:
        logger.error("")
        logger.error("=" * 50)
        logger.error("BRAND VIOLATIONS FOUND")
        logger.error("=" * 50)
        logger.error("")

        for issue in all_issues:
            location = f":{issue.line_number}" if issue.line_number else ""
            logger.error(f"[{issue.rule}] {issue.file_path}{location}")
            logger.error(f"  {issue.message}")
            logger.error("")

        logger.error("Fix these issues before committing.")
        logger.error("Run: python core/brand_guard.py outputs/")
        return 1

    logger.info("")
    logger.info("=" * 50)
    logger.info("Pre-commit checks passed")
    logger.info("=" * 50)
    return 0


def handle_validate(target: Path) -> int:
    """
    Validate a file or directory for brand compliance.

    Args:
        target: Path to file or directory to validate.

    Returns:
        0 if no violations, 1 if violations found.
    """
    from core import brand_guard

    if not target.exists():
        logger.error(f"Target not found: {target}")
        return 1

    if target.is_file():
        issues = brand_guard.check_file(target)
    else:
        issues = brand_guard.check_directory(target)

    print(brand_guard.format_violations(issues))

    return 1 if issues else 0


def brand_check(filepath: str) -> int:
    """
    Run brand compliance check on a file.

    Called by Claude Code PostToolUse hook for Write/Edit operations.

    Args:
        filepath: Path to the file to check.

    Returns:
        0 if compliant or non-checkable file
        1 if violations found (prints warnings but doesn't block)
    """
    from core.brand_guard import check_file

    path = Path(filepath)

    # Only check relevant file types
    checkable_extensions = {'.py', '.html', '.css', '.js', '.jsx', '.tsx', '.svg', '.md'}
    if path.suffix.lower() not in checkable_extensions:
        return 0

    # Skip files outside project
    if not path.exists():
        return 0

    # Skip test files and config
    # Only skip if filename contains 'test' or in tests/ directory
    if path.name.lower().startswith('test') or '/tests/' in str(path) or path.name.startswith('.'):
        return 0

    try:
        violations = check_file(str(path))
        if violations:
            print(f"\nBRAND CHECK: {len(violations)} issue(s) in {path.name}")
            for v in violations[:3]:  # Show max 3
                print(f"   - {v.rule}: {v.message}")
            if len(violations) > 3:
                print(f"   ... and {len(violations) - 3} more")
            print(f"   Run: python -m core.brand_guard check-file \"{filepath}\"")
            return 1
    except Exception as e:
        # Don't fail the hook on errors
        print(f"Brand check error: {e}")

    return 0


def session_end() -> int:
    """
    Log session end for telemetry foundation.

    Called by Claude Code Stop hook.
    Creates/appends to project_state/session_log.jsonl

    Returns:
        0 always (silent operation)
    """
    log_dir = Path("project_state")
    if not log_dir.exists():
        # Not in a KACA project, skip
        return 0

    log_file = log_dir / "session_log.jsonl"

    entry = {
        "event": "session_end",
        "timestamp": datetime.now().isoformat(),
        "cwd": os.getcwd()
    }

    try:
        with open(log_file, "a") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception:
        pass  # Silent fail - don't disrupt session end

    return 0


def main():
    """CLI entry point for hook_runner."""
    if len(sys.argv) < 2:
        print("Kearney Hook Runner - Cross-Platform Hook Dispatcher")
        print("")
        print("Usage:")
        print("  python -m core.hook_runner brand_check <filepath>")
        print("  python -m core.hook_runner session_end")
        print("  python core/hook_runner.py post-edit <file>")
        print("  python core/hook_runner.py pre-commit")
        print("  python core/hook_runner.py validate <file_or_dir>")
        print("")
        print("Commands:")
        print("  brand_check - Check file for brand compliance (Claude Code hook)")
        print("  session_end - Log session end (Claude Code hook)")
        print("  post-edit   - Run after Claude writes a file (legacy)")
        print("  pre-commit  - Run before git commit")
        print("  validate    - Validate a file or directory")
        sys.exit(1)

    command = sys.argv[1]

    if command == "brand_check":
        if len(sys.argv) < 3:
            print("Usage: python -m core.hook_runner brand_check <filepath>")
            sys.exit(1)
        sys.exit(brand_check(sys.argv[2]))

    elif command == "session_end":
        sys.exit(session_end())

    elif command == "post-edit":
        if len(sys.argv) < 3:
            logger.error("post-edit requires a target file")
            logger.error("Usage: python core/hook_runner.py post-edit <file>")
            sys.exit(1)
        target = Path(sys.argv[2])
        sys.exit(handle_post_edit(target))

    elif command == "pre-commit":
        sys.exit(handle_pre_commit())

    elif command == "validate":
        if len(sys.argv) < 3:
            logger.error("validate requires a target file or directory")
            logger.error("Usage: python core/hook_runner.py validate <file_or_dir>")
            sys.exit(1)
        target = Path(sys.argv[2])
        sys.exit(handle_validate(target))

    else:
        logger.error(f"Unknown command: {command}")
        logger.error("Valid commands: brand_check, session_end, post-edit, pre-commit, validate")
        sys.exit(1)


if __name__ == "__main__":
    main()
