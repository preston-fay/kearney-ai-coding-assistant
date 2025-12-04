"""
Memory Integration for KACA Agents

Provides functions for injecting memory context into agent workflows
and recording significant events.
"""

import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


def get_agent_context(agent_name: str, max_tokens: int = 400) -> str:
    """
    Build memory context tailored for a specific agent.

    Different agents need different context:
    - @interviewer: User preferences for interview style
    - @planner: Recent decisions, project history
    - @steward: Current phase, recent work
    - @presentation-builder: Presentation preferences

    Args:
        agent_name: Name of the agent (without @)
        max_tokens: Maximum tokens for context

    Returns:
        Formatted context string for prompt injection
    """
    from core.memory import (
        load_user_profile,
        get_recent_episodes,
        get_session_context,
        build_memory_context
    )

    parts = []
    profile = load_user_profile()

    # Agent-specific context
    if agent_name == "interviewer":
        # Interview preferences
        interview_prefs = profile.get('preferences', {}).get('interview', {})
        if interview_prefs.get('default_mode') == 'express':
            parts.append("User prefers express interviews (6-10 questions)")

        user_name = profile.get('user', {}).get('name', '')
        if user_name:
            parts.append(f"User: {user_name}")

    elif agent_name == "planner":
        # Recent context is most important for planning
        episodes = get_recent_episodes(3)
        if episodes:
            parts.append("Recent project history:")
            for ep in episodes:
                parts.append(f"- {ep['event_type']}: {ep['summary'][:80]}...")

    elif agent_name == "steward":
        # Current session context
        session = get_session_context()
        if session.get('current_phase'):
            parts.append(f"Current phase: {session['current_phase']}")
        if session.get('last_task'):
            parts.append(f"Last completed: {session['last_task']}")

    elif agent_name in ["presentation-builder", "presentation_builder"]:
        # Presentation preferences
        pres_prefs = profile.get('preferences', {}).get('presentation', {})
        if pres_prefs.get('always_include_exec_summary'):
            parts.append("User prefers executive summary slide")
        target = pres_prefs.get('default_slide_count_target')
        if target:
            parts.append(f"Target slide count: {target}")
        closing = pres_prefs.get('preferred_closing')
        if closing:
            parts.append(f"Preferred closing: {closing}")

    elif agent_name == "dashboard_builder":
        # Chart preferences
        chart_prefs = profile.get('preferences', {}).get('chart', {})
        fmt = chart_prefs.get('default_format', 'svg')
        parts.append(f"Default chart format: {fmt}")

    else:
        # Generic context for other agents
        return build_memory_context(max_tokens)

    if not parts:
        return ""

    # Format as memory context block
    context = "<memory_context>\n" + "\n".join(parts) + "\n</memory_context>"

    # Rough token limiting
    max_chars = max_tokens * 4
    if len(context) > max_chars:
        context = context[:max_chars-20] + "...\n</memory_context>"

    return context


def update_session_after_task(task_id: str, task_description: str, phase: str) -> None:
    """
    Update session context after a task completes.

    Args:
        task_id: ID of completed task
        task_description: Description of the task
        phase: Current phase name
    """
    from core.memory import update_session_context, get_session_context

    context = get_session_context()
    context['current_phase'] = phase
    context['last_task'] = f"{task_id}: {task_description}"
    context['tasks_completed'] = context.get('tasks_completed', 0) + 1

    update_session_context(context)


def apply_user_defaults_to_spec(spec: dict) -> dict:
    """
    Apply user preferences as defaults to a specification.

    This allows user preferences to pre-fill spec values
    without overriding explicit choices from the interview.

    Args:
        spec: The specification dict

    Returns:
        Modified spec with defaults applied
    """
    from core.memory import load_user_profile

    profile = load_user_profile()
    defaults = profile.get('defaults', {})
    prefs = profile.get('preferences', {})

    # Apply visualization defaults
    if 'visualization' not in spec:
        spec['visualization'] = {}

    viz = spec['visualization']
    viz_defaults = defaults.get('visualization', {})

    if 'insight_depth' not in viz and 'insight_depth' in viz_defaults:
        viz['insight_depth'] = viz_defaults['insight_depth']

    chart_prefs = prefs.get('chart', {})
    if 'format' not in viz and 'default_format' in chart_prefs:
        viz['format'] = chart_prefs['default_format']
    if 'size' not in viz and 'default_size' in chart_prefs:
        viz['size'] = chart_prefs['default_size']

    # Apply branding default
    if 'branding' not in viz:
        viz['branding'] = defaults.get('branding', 'kearney')

    return spec


def get_client_overrides(client_name: str) -> Dict[str, Any]:
    """
    Get any client-specific overrides from user profile.

    Args:
        client_name: Name of the client

    Returns:
        Dict of overrides for this client
    """
    from core.memory import load_user_profile

    profile = load_user_profile()
    overrides = profile.get('client_overrides', {})

    # Case-insensitive lookup
    for key, value in overrides.items():
        if key.lower() == client_name.lower():
            return value

    return {}
