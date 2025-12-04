"""
Action Title Generator for KACA

Transforms descriptive titles into consulting-style action titles
that state the insight rather than describe the data.

Good: "Northeast Drives 60% of Revenue Growth"
Bad: "Regional Revenue Analysis"

Usage:
    from core.action_titles import transform_to_action_title, suggest_action_titles
"""

import re
from typing import Optional, Dict, Any, List


# Common weak title patterns to avoid
WEAK_PATTERNS = [
    r'^(overview|summary|analysis|review|report|data|chart|graph|table)\s*(of|:)?',
    r'^(regional|quarterly|monthly|annual|yearly)\s+',
    r'\s+(overview|summary|breakdown|analysis)$',
]

# Strong action verbs for titles
ACTION_VERBS = {
    'increase': ['Drives', 'Leads', 'Grows', 'Expands', 'Accelerates'],
    'decrease': ['Declines', 'Falls', 'Drops', 'Contracts', 'Shrinks'],
    'stable': ['Maintains', 'Holds', 'Stabilizes', 'Sustains'],
    'compare': ['Outperforms', 'Leads', 'Trails', 'Matches'],
    'risk': ['Creates', 'Poses', 'Introduces', 'Raises'],
    'opportunity': ['Presents', 'Offers', 'Opens', 'Enables'],
}


def is_weak_title(title: str) -> bool:
    """
    Check if a title is descriptive rather than action-oriented.

    Weak titles describe what the slide shows.
    Strong titles state the insight.

    Args:
        title: The title to check

    Returns:
        True if the title is weak/descriptive
    """
    title_lower = title.lower().strip()

    # Check against weak patterns
    for pattern in WEAK_PATTERNS:
        if re.search(pattern, title_lower, re.IGNORECASE):
            return True

    # Check if it's just a noun phrase (no verb)
    # Simple heuristic: if it doesn't contain a verb-like word, it's weak
    action_indicators = [
        'drives', 'leads', 'grows', 'declines', 'falls', 'creates',
        'outperforms', 'exceeds', 'trails', 'remains', 'shows',
        'increases', 'decreases', 'maintains', 'achieves', 'reaches',
        'dominates', 'captures', 'represents', 'accounts',
    ]

    has_action = any(word in title_lower for word in action_indicators)

    # Also check for percentage or specific number (indicates specificity)
    has_specifics = bool(re.search(r'\d+%|\$[\d,]+|\d+x', title))

    # A title with specifics but no action verb is borderline
    # A title with neither is definitely weak
    if not has_action and not has_specifics:
        return True

    return False


def transform_to_action_title(
    descriptive_title: str,
    key_metric: Optional[str] = None,
    key_value: Optional[str] = None,
    trend: Optional[str] = None,
) -> str:
    """
    Transform a descriptive title into an action title.

    Args:
        descriptive_title: The original descriptive title
        key_metric: The main metric being shown (e.g., "Revenue")
        key_value: The key value or finding (e.g., "60%", "$2.5M")
        trend: Direction of change ("up", "down", "stable", None)

    Returns:
        Action-oriented title

    Example:
        transform_to_action_title(
            "Q3 Regional Revenue Analysis",
            key_metric="Revenue",
            key_value="Northeast 45%",
            trend="up"
        )
        # Returns: "Northeast Captures 45% of Revenue"
    """
    # If we have specific data, build from that
    if key_metric and key_value:
        # Parse key_value for entity and number
        # Expected formats: "Entity XX%", "Entity $XXX", "$XXX", "XX%"

        # Try to extract entity and value
        match = re.match(r'^([A-Za-z\s]+?)\s*([\d.]+%|\$[\d,.]+|\d+x?)$', key_value.strip())

        if match:
            entity = match.group(1).strip()
            value = match.group(2)

            if trend == 'up':
                verb = 'Drives'
            elif trend == 'down':
                verb = 'Loses'
            else:
                verb = 'Captures'

            return f"{entity} {verb} {value} of {key_metric}"
        else:
            # key_value is just a number
            if trend == 'up':
                return f"{key_metric} Grows {key_value}"
            elif trend == 'down':
                return f"{key_metric} Declines {key_value}"
            else:
                return f"{key_metric} Reaches {key_value}"

    # Fallback: try to improve the descriptive title
    # Remove weak words
    improved = descriptive_title
    for pattern in WEAK_PATTERNS:
        improved = re.sub(pattern, '', improved, flags=re.IGNORECASE)

    improved = improved.strip()

    # If we stripped everything, return original
    if not improved:
        return descriptive_title

    # Capitalize properly
    return improved.title()


def suggest_action_titles(
    data_description: str,
    values: Dict[str, Any],
    context: Optional[str] = None,
) -> List[str]:
    """
    Suggest multiple action title options based on data.

    Args:
        data_description: What the data shows (e.g., "regional revenue comparison")
        values: Dict of data values
        context: Additional context

    Returns:
        List of suggested action titles (ranked by quality)
    """
    suggestions = []

    # Analyze the values
    if isinstance(values, dict) and values:
        # Find leader
        numeric_values = {k: v for k, v in values.items() if isinstance(v, (int, float))}

        if numeric_values:
            sorted_items = sorted(numeric_values.items(), key=lambda x: x[1], reverse=True)
            leader, leader_val = sorted_items[0]

            total = sum(numeric_values.values())
            if total > 0:
                leader_share = leader_val / total * 100

                # Generate options
                suggestions.append(f"{leader} Leads with {leader_share:.0f}% Share")
                suggestions.append(f"{leader} Dominates at {leader_share:.0f}%")
                suggestions.append(f"{leader} Captures {leader_share:.0f}% of Total")

                if len(sorted_items) > 1:
                    runner_up = sorted_items[1][0]
                    gap = leader_val - sorted_items[1][1]
                    suggestions.append(f"{leader} Outperforms {runner_up} by {gap:,.0f}")

    # If no specific suggestions, provide generic strong templates
    if not suggestions:
        suggestions = [
            "Key Finding from Analysis",
            "Primary Insight: [Specific Finding]",
            "[Entity] Drives [Metric] Performance",
        ]

    return suggestions


def validate_action_title(title: str) -> Dict[str, Any]:
    """
    Validate an action title and provide feedback.

    Args:
        title: The title to validate

    Returns:
        Dict with 'valid' bool and 'feedback' string
    """
    result = {
        'valid': True,
        'feedback': '',
        'suggestions': [],
    }

    # Check length
    if len(title) > 80:
        result['valid'] = False
        result['feedback'] = "Title too long (max 80 chars). "
        result['suggestions'].append(title[:77] + "...")

    if len(title) < 10:
        result['valid'] = False
        result['feedback'] += "Title too short. Add specifics. "

    # Check for weak patterns
    if is_weak_title(title):
        result['valid'] = False
        result['feedback'] += "Title is descriptive, not action-oriented. State the insight, not what the slide shows. "
        result['suggestions'].extend([
            "Add a specific finding (e.g., 'Northeast Leads with 45%')",
            "Include the key number or percentage",
            "Start with the subject that's performing the action",
        ])

    # Check for question marks (titles should be statements)
    if '?' in title:
        result['valid'] = False
        result['feedback'] += "Titles should be statements, not questions. "

    if result['valid']:
        result['feedback'] = "Title is action-oriented and specific."

    return result
