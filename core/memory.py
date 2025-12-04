"""
KACA Memory System

Provides persistent memory across sessions:
- User profile: preferences that persist across projects
- Project episodes: summaries of key decisions in current project
- Context injection: automatic loading of relevant memory into prompts

Usage:
    from core.memory import (
        load_user_profile,
        save_user_profile,
        add_episode,
        get_recent_episodes,
        build_memory_context
    )
"""

import os
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any
import yaml

logger = logging.getLogger(__name__)

# Default user profile location
USER_PROFILE_DIR = Path.home() / ".kaca"
USER_PROFILE_PATH = USER_PROFILE_DIR / "profile.yaml"

# Project episode location (relative to project root)
EPISODES_DIR = "project_state/episodes"
SESSION_CONTEXT_FILE = "project_state/episodes/session_context.yaml"


# =============================================================================
# User Profile Functions
# =============================================================================

def get_default_profile() -> Dict[str, Any]:
    """Return default user profile structure."""
    return {
        "user": {
            "name": "",
        },
        "preferences": {
            "chart": {
                "default_format": "svg",
                "default_size": "presentation",
                "always_include_source": False,
            },
            "presentation": {
                "always_include_exec_summary": True,
                "default_slide_count_target": 15,
                "preferred_closing": "next_steps",
            },
            "document": {
                "include_methodology_appendix": False,
            },
            "interview": {
                "default_mode": "full",  # "full" or "express"
            },
        },
        "defaults": {
            "visualization": {
                "insight_depth": "brief",
            },
            "branding": "kearney",
        },
        "client_overrides": {},
    }


def load_user_profile() -> Dict[str, Any]:
    """
    Load user profile from ~/.kaca/profile.yaml.

    Returns default profile if file doesn't exist.
    """
    if not USER_PROFILE_PATH.exists():
        logger.debug("No user profile found, using defaults")
        return get_default_profile()

    try:
        with open(USER_PROFILE_PATH, 'r') as f:
            profile = yaml.safe_load(f) or {}

        # Merge with defaults to ensure all keys exist
        default = get_default_profile()
        merged = _deep_merge(default, profile)
        return merged
    except Exception as e:
        logger.warning(f"Error loading user profile: {e}")
        return get_default_profile()


def save_user_profile(profile: Dict[str, Any]) -> bool:
    """
    Save user profile to ~/.kaca/profile.yaml.

    Creates directory if it doesn't exist.

    Returns:
        True if saved successfully, False otherwise.
    """
    try:
        USER_PROFILE_DIR.mkdir(parents=True, exist_ok=True)

        with open(USER_PROFILE_PATH, 'w') as f:
            yaml.dump(profile, f, default_flow_style=False, sort_keys=False)

        logger.info(f"User profile saved to {USER_PROFILE_PATH}")
        return True
    except Exception as e:
        logger.error(f"Error saving user profile: {e}")
        return False


def update_user_preference(path: str, value: Any) -> bool:
    """
    Update a specific preference in the user profile.

    Args:
        path: Dot-notation path (e.g., "preferences.chart.default_format")
        value: New value to set

    Returns:
        True if updated successfully.
    """
    profile = load_user_profile()
    _set_nested(profile, path, value)
    return save_user_profile(profile)


def get_user_preference(path: str, default: Any = None) -> Any:
    """
    Get a specific preference from the user profile.

    Args:
        path: Dot-notation path (e.g., "preferences.chart.default_format")
        default: Default value if path doesn't exist

    Returns:
        The preference value or default.
    """
    profile = load_user_profile()
    return _get_nested(profile, path, default)


# =============================================================================
# Project Episode Functions
# =============================================================================

def get_episodes_dir() -> Path:
    """Get the episodes directory for the current project."""
    return Path(EPISODES_DIR)


def add_episode(
    event_type: str,
    summary: str,
    details: Optional[Dict[str, Any]] = None
) -> str:
    """
    Add a new episode to the project history.

    Args:
        event_type: Type of event (e.g., "interview_complete", "plan_generated")
        summary: Brief human-readable summary
        details: Optional additional structured data

    Returns:
        The episode filename.
    """
    episodes_dir = get_episodes_dir()
    episodes_dir.mkdir(parents=True, exist_ok=True)

    # Get next episode number
    existing = list(episodes_dir.glob("*.md"))
    next_num = len(existing) + 1

    timestamp = datetime.now()
    filename = f"{next_num:03d}_{event_type}.md"
    filepath = episodes_dir / filename

    # Build episode content
    content = f"""# Episode {next_num}: {event_type.replace('_', ' ').title()}

**Timestamp:** {timestamp.isoformat()}
**Type:** {event_type}

## Summary

{summary}
"""

    if details:
        content += "\n## Details\n\n```yaml\n"
        content += yaml.dump(details, default_flow_style=False)
        content += "```\n"

    with open(filepath, 'w') as f:
        f.write(content)

    logger.info(f"Episode recorded: {filename}")
    return filename


def get_recent_episodes(n: int = 3) -> List[Dict[str, Any]]:
    """
    Get the n most recent episodes.

    Returns:
        List of episode dicts with 'filename', 'event_type', 'summary'.
    """
    episodes_dir = get_episodes_dir()
    if not episodes_dir.exists():
        return []

    episode_files = sorted(episodes_dir.glob("*.md"), reverse=True)[:n]
    episodes = []

    for filepath in episode_files:
        try:
            content = filepath.read_text()
            # Parse basic info from content
            lines = content.split('\n')
            event_type = filepath.stem.split('_', 1)[1] if '_' in filepath.stem else 'unknown'

            # Extract summary section
            summary = ""
            in_summary = False
            for line in lines:
                if line.strip() == "## Summary":
                    in_summary = True
                elif line.startswith("## ") and in_summary:
                    break
                elif in_summary and line.strip():
                    summary += line + " "

            episodes.append({
                'filename': filepath.name,
                'event_type': event_type,
                'summary': summary.strip()[:500],  # Limit length
            })
        except Exception as e:
            logger.warning(f"Error reading episode {filepath}: {e}")

    return episodes


def update_session_context(context: Dict[str, Any]) -> bool:
    """
    Update the rolling session context file.

    This file contains a compressed summary of the current session,
    updated as the session progresses.
    """
    context_path = Path(SESSION_CONTEXT_FILE)
    context_path.parent.mkdir(parents=True, exist_ok=True)

    context['last_updated'] = datetime.now().isoformat()

    try:
        with open(context_path, 'w') as f:
            yaml.dump(context, f, default_flow_style=False)
        return True
    except Exception as e:
        logger.error(f"Error updating session context: {e}")
        return False


def get_session_context() -> Dict[str, Any]:
    """Load the current session context."""
    context_path = Path(SESSION_CONTEXT_FILE)
    if not context_path.exists():
        return {}

    try:
        with open(context_path, 'r') as f:
            return yaml.safe_load(f) or {}
    except Exception:
        return {}


# =============================================================================
# Context Building Functions
# =============================================================================

def build_memory_context(max_tokens: int = 500) -> str:
    """
    Build a memory context string for injection into agent prompts.

    Combines user profile highlights and recent episodes into
    a compressed context suitable for prompt injection.

    Args:
        max_tokens: Approximate maximum tokens for the context.

    Returns:
        Formatted memory context string.
    """
    parts = []

    # User profile highlights
    profile = load_user_profile()
    user_name = profile.get('user', {}).get('name', '')
    if user_name:
        parts.append(f"User: {user_name}")

    # Key preferences
    prefs = profile.get('preferences', {})
    interview_mode = prefs.get('interview', {}).get('default_mode', 'full')
    if interview_mode == 'express':
        parts.append("Prefers express interviews")

    chart_format = prefs.get('chart', {}).get('default_format', 'svg')
    parts.append(f"Default chart format: {chart_format}")

    # Recent episodes
    episodes = get_recent_episodes(3)
    if episodes:
        parts.append("\nRecent context:")
        for ep in episodes:
            # Truncate summary to save tokens
            summary = ep['summary'][:100] + "..." if len(ep['summary']) > 100 else ep['summary']
            parts.append(f"- {ep['event_type']}: {summary}")

    # Session context
    session = get_session_context()
    if session.get('current_phase'):
        parts.append(f"\nCurrent phase: {session['current_phase']}")
    if session.get('focus'):
        parts.append(f"Focus: {session['focus']}")

    context = "\n".join(parts)

    # Rough token limiting (1 token ~ 4 chars)
    max_chars = max_tokens * 4
    if len(context) > max_chars:
        context = context[:max_chars] + "..."

    return context


# =============================================================================
# Helper Functions
# =============================================================================

def _deep_merge(base: dict, override: dict) -> dict:
    """Deep merge two dictionaries, with override taking precedence."""
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def _get_nested(d: dict, path: str, default: Any = None) -> Any:
    """Get a nested value using dot notation."""
    keys = path.split('.')
    current = d
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
    return current


def _set_nested(d: dict, path: str, value: Any) -> None:
    """Set a nested value using dot notation."""
    keys = path.split('.')
    current = d
    for key in keys[:-1]:
        if key not in current:
            current[key] = {}
        current = current[key]
    current[keys[-1]] = value


# =============================================================================
# CLI Interface
# =============================================================================

def main():
    """CLI for memory management."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m core.memory <command>")
        print("Commands:")
        print("  show-profile     Show current user profile")
        print("  show-episodes    Show recent episodes")
        print("  show-context     Show built memory context")
        print("  init-profile     Create default profile")
        return

    command = sys.argv[1]

    if command == "show-profile":
        profile = load_user_profile()
        print(yaml.dump(profile, default_flow_style=False))

    elif command == "show-episodes":
        episodes = get_recent_episodes(5)
        for ep in episodes:
            print(f"[{ep['filename']}] {ep['event_type']}")
            print(f"  {ep['summary'][:100]}...")
            print()

    elif command == "show-context":
        context = build_memory_context()
        print(context)

    elif command == "init-profile":
        profile = get_default_profile()
        save_user_profile(profile)
        print(f"Profile initialized at {USER_PROFILE_PATH}")

    else:
        print(f"Unknown command: {command}")


if __name__ == "__main__":
    main()
