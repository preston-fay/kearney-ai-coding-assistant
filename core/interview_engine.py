# core/interview_engine.py
"""
Interview Engine for Living Requirements System.
Conducts structured interviews with conditional logic and follow-up probes.

The engine loads interview trees from config/interviews/ and orchestrates
the conversation flow, producing a structured spec.yaml.

Supports:
- Express mode: Shorter interviews (6-10 questions) from *_express.yaml files
- Template mode: Pre-filled specs that only ask delta questions
"""

import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, field

import yaml


logger = logging.getLogger(__name__)

# Path to interview tree configurations
INTERVIEWS_DIR = Path('config/interviews')

# Path to spec templates
TEMPLATES_DIR = Path('config/templates')


@dataclass
class FollowUp:
    """Follow-up probe configuration."""
    condition: str
    prompt: str


@dataclass
class Question:
    """Single interview question."""
    id: str
    prompt: str
    question_type: str  # text, choice, multi, boolean, number, date, list, file
    required: bool = True
    options: List[str] = field(default_factory=list)
    condition: Optional[str] = None
    follow_up: Optional[FollowUp] = None
    default: Optional[Any] = None


@dataclass
class Section:
    """Section of related questions."""
    id: str
    name: str
    questions: List[Question] = field(default_factory=list)


@dataclass
class InterviewTree:
    """Complete interview tree for a project type."""
    id: str
    name: str
    version: str
    sections: List[Section] = field(default_factory=list)


@dataclass
class InterviewState:
    """Current state of an interview."""
    tree_id: str
    current_section_idx: int = 0
    current_question_idx: int = 0
    answers: Dict[str, Any] = field(default_factory=dict)
    completed: bool = False


# Project type display names and IDs
PROJECT_TYPES = [
    ('data_engineering', 'Data Engineering (ingestion, transformation, pipelines)'),
    ('modeling', 'Statistical/ML Model (prediction, classification, clustering)'),
    ('analytics', 'Analytics Asset (analysis, visualization, insights)'),
    ('presentation', 'Presentation/Deck (client-facing slides)'),
    ('proposal', 'Proposal Content (RFP response, pitch, methodology)'),
    ('dashboard', 'Dashboard (interactive data visualization)'),
    ('webapp', 'Web Application (tool, prototype, MVP)'),
    ('research', 'Research/Synthesis (market research, competitive analysis)'),
]


def _parse_question(data: Dict[str, Any]) -> Question:
    """Parse question from YAML dict."""
    follow_up = None
    if 'follow_up' in data:
        fu_data = data['follow_up']
        follow_up = FollowUp(
            condition=fu_data.get('condition', ''),
            prompt=fu_data.get('prompt', ''),
        )

    return Question(
        id=data.get('id', ''),
        prompt=data.get('prompt', ''),
        question_type=data.get('type', 'text'),
        required=data.get('required', True),
        options=data.get('options', []),
        condition=data.get('condition'),
        follow_up=follow_up,
        default=data.get('default'),
    )


def _parse_section(data: Dict[str, Any]) -> Section:
    """Parse section from YAML dict."""
    questions = [_parse_question(q) for q in data.get('questions', [])]
    return Section(
        id=data.get('id', ''),
        name=data.get('name', ''),
        questions=questions,
    )


def express_interview_exists(project_type: str) -> bool:
    """
    Check if an express interview exists for a project type.

    Args:
        project_type: Type ID (e.g., 'modeling', 'analytics').

    Returns:
        True if express interview file exists, False otherwise.
    """
    express_path = INTERVIEWS_DIR / f'{project_type}_express.yaml'
    return express_path.exists()


def should_use_express_mode(project_type: str, explicit_mode: str = None) -> bool:
    """
    Determine if express mode should be used for an interview.

    Checks user preferences and express interview availability.
    An explicit mode parameter overrides user preferences.

    Args:
        project_type: Type ID (e.g., 'modeling', 'analytics').
        explicit_mode: If provided ('express' or 'full'), overrides preferences.

    Returns:
        True if express mode should be used, False otherwise.
    """
    # Explicit mode overrides everything
    if explicit_mode == 'express':
        return express_interview_exists(project_type)
    if explicit_mode == 'full':
        return False

    # Check user preference
    try:
        from core.memory import get_user_preference
        default_mode = get_user_preference('preferences.interview.default_mode', 'full')
    except ImportError:
        default_mode = 'full'

    # Use express if user prefers it AND express interview exists
    if default_mode == 'express':
        return express_interview_exists(project_type)

    return False


def load_interview_tree(
    project_type: str,
    express: bool = False,
) -> Optional[InterviewTree]:
    """
    Load interview tree for a project type.

    Args:
        project_type: Type ID (e.g., 'modeling', 'presentation').
        express: If True, attempt to load express (shorter) interview.
                Falls back to full interview with warning if express doesn't exist.

    Returns:
        InterviewTree or None if not found.
    """
    # Determine which file to load
    if express:
        express_path = INTERVIEWS_DIR / f'{project_type}_express.yaml'
        if express_path.exists():
            path = express_path
        else:
            logger.warning(
                f"Express interview for '{project_type}' not found. "
                f"Falling back to full interview."
            )
            path = INTERVIEWS_DIR / f'{project_type}.yaml'
    else:
        path = INTERVIEWS_DIR / f'{project_type}.yaml'

    if not path.exists():
        return None

    content = path.read_text(encoding='utf-8')
    data = yaml.safe_load(content)

    sections = [_parse_section(s) for s in data.get('sections', [])]

    return InterviewTree(
        id=data.get('id', project_type),
        name=data.get('name', project_type.title()),
        version=data.get('version', '1.0.0'),
        sections=sections,
    )


def list_available_trees() -> List[str]:
    """List available interview tree IDs."""
    if not INTERVIEWS_DIR.exists():
        return []
    # Exclude express interviews from the main list
    return [
        p.stem for p in INTERVIEWS_DIR.glob('*.yaml')
        if not p.stem.endswith('_express')
    ]


def list_available_templates() -> List[str]:
    """
    List available spec template names.

    Returns:
        List of template names (file stems) that contain _template metadata.
    """
    if not TEMPLATES_DIR.exists():
        return []

    templates = []
    for path in TEMPLATES_DIR.glob('*.yaml'):
        try:
            content = path.read_text(encoding='utf-8')
            data = yaml.safe_load(content)
            # Only include files that have _template metadata
            if data and '_template' in data:
                templates.append(path.stem)
        except (yaml.YAMLError, OSError):
            # Skip files that can't be parsed
            continue

    return sorted(templates)


def load_spec_template(template_name: str) -> Optional[Dict[str, Any]]:
    """
    Load a pre-filled spec template.

    Templates are pre-filled spec.yaml structures with a _template section
    containing metadata about the template (name, description, base_type).

    Args:
        template_name: Name of the template (file stem without .yaml).

    Returns:
        Dict containing the template data, or None if not found.
        The _template section contains:
            - name: Human-readable template name
            - description: What the template is for
            - base_type: Which interview to use for delta questions
    """
    path = TEMPLATES_DIR / f'{template_name}.yaml'
    if not path.exists():
        return None

    try:
        content = path.read_text(encoding='utf-8')
        data = yaml.safe_load(content)

        # Validate that this is a proper spec template
        if not data or '_template' not in data:
            logger.warning(
                f"Template '{template_name}' missing _template metadata section."
            )
            return None

        return data
    except (yaml.YAMLError, OSError) as e:
        logger.error(f"Failed to load template '{template_name}': {e}")
        return None


def get_project_type_menu(show_express_indicator: bool = True) -> str:
    """
    Get formatted menu of project types.

    Args:
        show_express_indicator: If True, show [EXPRESS] tag for types
            that have express mode available.

    Returns:
        Formatted menu string.
    """
    lines = ["What type of work product are you building?", ""]
    for i, (type_id, description) in enumerate(PROJECT_TYPES, 1):
        if show_express_indicator and express_interview_exists(type_id):
            lines.append(f"{i}. {description} [EXPRESS]")
        else:
            lines.append(f"{i}. {description}")
    lines.append("")
    lines.append("━" * 60)
    lines.append("Select one or more (e.g., '2' or '2, 3, 6')")
    if show_express_indicator:
        lines.append("[EXPRESS] = Express mode available (shorter interview)")
    lines.append("━" * 60)
    return '\n'.join(lines)


def parse_multi_select(user_input: str, max_option: int) -> List[int]:
    """
    Parse user input that may contain multiple selections.

    Handles:
    - "2" → [2]
    - "2, 3, 5" → [2, 3, 5]
    - "2,3,5" → [2, 3, 5]
    - "2 3 5" → [2, 3, 5]

    Args:
        user_input: Raw user input string
        max_option: Maximum valid option number

    Returns:
        Sorted, deduplicated list of valid selections
    """
    # Remove all whitespace around commas
    cleaned = re.sub(r'\s*,\s*', ',', user_input.strip())

    # Split on comma or space
    parts = re.split(r'[,\s]+', cleaned)

    # Parse to integers, validate range
    selections = []
    for part in parts:
        part = part.strip()
        if part and part.isdigit():
            num = int(part)
            if 1 <= num <= max_option:
                selections.append(num)

    return sorted(set(selections))


def parse_project_type_choice(choice: str, allow_multiple: bool = False) -> Optional[Union[str, List[str]]]:
    """
    Parse user's project type selection.

    Args:
        choice: User input (number or type name).
        allow_multiple: If True, parse and return multiple selections as list.

    Returns:
        Project type ID (single) or list of IDs (if allow_multiple=True).
        Returns None if invalid.
    """
    choice = choice.strip()

    # Handle multi-select
    if allow_multiple and any(sep in choice for sep in [',', ' ']):
        selections = parse_multi_select(choice, len(PROJECT_TYPES))
        if selections:
            return [PROJECT_TYPES[idx - 1][0] for idx in selections]
        return None

    # Try as single number
    try:
        idx = int(choice)
        if 1 <= idx <= len(PROJECT_TYPES):
            result = PROJECT_TYPES[idx - 1][0]
            return [result] if allow_multiple else result
    except ValueError:
        pass

    # Try as name match
    choice_lower = choice.lower()
    for type_id, description in PROJECT_TYPES:
        if type_id == choice_lower or choice_lower in description.lower():
            return [type_id] if allow_multiple else type_id

    return None


def evaluate_condition(condition: str, answers: Dict[str, Any]) -> bool:
    """
    Evaluate a condition string against current answers.

    Supports basic Python expressions with answer variables.

    Args:
        condition: Condition string (e.g., "problem_type == 'classification'").
        answers: Current answers dict.

    Returns:
        True if condition is met, False otherwise.
    """
    if not condition:
        return True

    try:
        # Create safe evaluation context with answers
        context = dict(answers)
        # Add helper for len()
        context['len'] = len

        # Evaluate condition
        result = eval(condition, {"__builtins__": {}}, context)
        return bool(result)
    except Exception:
        # If condition fails to evaluate, assume True (show the question)
        return True


def should_ask_question(question: Question, answers: Dict[str, Any]) -> bool:
    """
    Determine if a question should be asked based on conditions.

    Args:
        question: The question to check.
        answers: Current answers dict.

    Returns:
        True if question should be asked.
    """
    if question.condition is None:
        return True
    return evaluate_condition(question.condition, answers)


def needs_follow_up(question: Question, answer: Any, answers: Dict[str, Any]) -> bool:
    """
    Check if a follow-up probe is needed.

    Args:
        question: The question that was answered.
        answer: The user's answer.
        answers: All answers so far.

    Returns:
        True if follow-up should be asked.
    """
    if question.follow_up is None:
        return False

    # Add current answer to context
    context = dict(answers)
    context['answer'] = answer

    return evaluate_condition(question.follow_up.condition, context)


def get_follow_up_prompt(question: Question) -> str:
    """Get the follow-up prompt for a question."""
    if question.follow_up:
        return question.follow_up.prompt
    return ""


def is_skip_input(raw_answer: str) -> bool:
    """
    Check if user input indicates they want to skip the question.

    Args:
        raw_answer: Raw string from user.

    Returns:
        True if user wants to skip.
    """
    if not raw_answer:
        return True
    normalized = raw_answer.strip().lower()
    if not normalized:  # Whitespace-only input
        return True
    return normalized in ('skip', '0', 'n/a', 'na', 'none', '-')


def format_question(question: Question) -> str:
    """
    Format a question for display.

    Args:
        question: The question to format.

    Returns:
        Formatted question string.
    """
    lines = [question.prompt.strip()]

    if question.question_type == 'choice' and question.options:
        lines.append("")
        for i, option in enumerate(question.options, 1):
            lines.append(f"{i}. {option}")

    if question.question_type == 'multi' and question.options:
        lines.append("")
        lines.append("(Select multiple: e.g., '1, 3, 5' or '1 3 5')")
        for i, option in enumerate(question.options, 1):
            lines.append(f"{i}. {option}")

    if question.question_type == 'boolean':
        lines.append("")
        lines.append("(yes/no)")

    if not question.required:
        lines.append("")
        lines.append("(Optional - type 'skip' or press Enter to skip)")

    return '\n'.join(lines)


def parse_answer(question: Question, raw_answer: str) -> Any:
    """
    Parse user's raw answer into appropriate type.

    Args:
        question: The question being answered.
        raw_answer: Raw string from user.

    Returns:
        Parsed answer value.
    """
    raw_answer = raw_answer.strip()

    # Handle skip input for optional questions
    if not question.required and is_skip_input(raw_answer):
        if question.default is not None:
            return question.default
        return None

    # Handle empty answer for required questions
    if not raw_answer:
        if question.default is not None:
            return question.default
        return ""

    # Parse by type
    if question.question_type == 'text':
        return raw_answer

    elif question.question_type == 'choice':
        # Try as number
        try:
            idx = int(raw_answer)
            if 1 <= idx <= len(question.options):
                return question.options[idx - 1]
        except ValueError:
            pass
        # Try as direct match
        lower = raw_answer.lower()
        for opt in question.options:
            if opt.lower() == lower or lower in opt.lower():
                return opt
        return raw_answer

    elif question.question_type == 'multi':
        # Support both comma-separated and space-separated input
        # First normalize: replace multiple spaces with single, then split by comma or space
        normalized = re.sub(r'\s+', ' ', raw_answer)
        if ',' in normalized:
            parts = [p.strip() for p in normalized.split(',')]
        else:
            parts = normalized.split()

        selected = []
        for part in parts:
            if not part:
                continue
            try:
                idx = int(part)
                if 1 <= idx <= len(question.options):
                    opt = question.options[idx - 1]
                    if opt not in selected:  # Avoid duplicates
                        selected.append(opt)
            except ValueError:
                # Try direct match
                for opt in question.options:
                    if opt.lower() == part.lower() and opt not in selected:
                        selected.append(opt)
                        break
        return selected

    elif question.question_type == 'boolean':
        return raw_answer.lower() in ('yes', 'y', 'true', '1')

    elif question.question_type == 'number':
        try:
            if '.' in raw_answer:
                return float(raw_answer)
            return int(raw_answer)
        except ValueError:
            return raw_answer

    elif question.question_type == 'date':
        return raw_answer  # Keep as string for now

    elif question.question_type == 'list':
        return [p.strip() for p in raw_answer.split(',') if p.strip()]

    elif question.question_type == 'file':
        return raw_answer  # Path as string

    return raw_answer


def create_interview_state(project_type: str) -> InterviewState:
    """
    Create a new interview state.

    Args:
        project_type: The project type ID.

    Returns:
        New InterviewState.
    """
    return InterviewState(tree_id=project_type)


def get_next_question(
    tree: InterviewTree,
    state: InterviewState,
) -> Optional[Question]:
    """
    Get the next question to ask.

    Skips questions whose conditions aren't met.

    Args:
        tree: The interview tree.
        state: Current interview state.

    Returns:
        Next Question or None if interview is complete.
    """
    while state.current_section_idx < len(tree.sections):
        section = tree.sections[state.current_section_idx]

        while state.current_question_idx < len(section.questions):
            question = section.questions[state.current_question_idx]

            if should_ask_question(question, state.answers):
                return question

            # Skip this question
            state.current_question_idx += 1

        # Move to next section
        state.current_section_idx += 1
        state.current_question_idx = 0

    # Interview complete
    state.completed = True
    return None


def advance_state(state: InterviewState) -> None:
    """Advance state to next question."""
    state.current_question_idx += 1


def get_current_section_name(tree: InterviewTree, state: InterviewState) -> str:
    """Get name of current section."""
    if state.current_section_idx < len(tree.sections):
        return tree.sections[state.current_section_idx].name
    return ""


def get_progress(tree: InterviewTree, state: InterviewState) -> tuple:
    """
    Get interview progress.

    Returns:
        Tuple of (answered_count, total_questions).
    """
    total = sum(len(s.questions) for s in tree.sections)
    answered = len(state.answers)
    return (answered, total)


def get_answers_summary(state: InterviewState) -> str:
    """
    Get a formatted summary of all answers.

    Args:
        state: Interview state with answers.

    Returns:
        Formatted summary string.
    """
    if not state.answers:
        return "No answers recorded yet."

    lines = ["Interview Summary:", ""]
    for key, value in state.answers.items():
        if isinstance(value, list):
            value_str = ', '.join(str(v) for v in value)
        else:
            value_str = str(value)

        # Truncate long values
        if len(value_str) > 100:
            value_str = value_str[:100] + "..."

        lines.append(f"  {key}: {value_str}")

    return '\n'.join(lines)


def answers_to_spec_dict(
    project_type: str,
    answers: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Convert interview answers to spec.yaml structure.

    Maps answer IDs to appropriate spec sections based on project type.

    Args:
        project_type: The project type.
        answers: Interview answers.

    Returns:
        Dict ready for spec.yaml.
    """
    spec = {
        'meta': {
            'project_name': answers.get('project_name', ''),
            'project_type': project_type,
            'client': answers.get('client'),
            'deadline': answers.get('deadline'),
        },
        'problem': {
            'business_question': answers.get('business_question', ''),
            'success_criteria': answers.get('success_criteria', []),
        },
        'data': {
            'sources': [],
            'quality_notes': answers.get('quality_notes', []),
            'sensitive_fields': answers.get('sensitive_fields', []),
        },
        'deliverables': answers.get('deliverables', []),
        'constraints': {
            'brand': 'kearney',
        },
        'notes': answers.get('notes', []),
    }

    # Handle data sources if provided
    if 'data_sources' in answers:
        sources = answers['data_sources']
        if isinstance(sources, str):
            sources = [s.strip() for s in sources.split(',')]
        spec['data']['sources'] = [{'name': s, 'type': 'unknown'} for s in sources]

    # Add type-specific section
    type_specific = {}

    if project_type == 'modeling':
        type_specific = {
            'problem_type': answers.get('problem_type', ''),
            'target_variable': answers.get('target_variable', ''),
            'target_definition': answers.get('target_definition', ''),
            'class_balance': answers.get('class_balance', ''),
            'features': {
                'included': answers.get('features_included', []),
                'excluded': answers.get('features_excluded', []),
                'to_engineer': answers.get('features_to_engineer', []),
            },
            'validation': {
                'strategy': answers.get('validation_strategy', ''),
                'metrics': answers.get('validation_metrics', []),
            },
            'interpretability': {
                'required': answers.get('interpretability_required', False),
                'audience': answers.get('interpretability_audience', ''),
            },
        }

    elif project_type == 'presentation':
        type_specific = {
            'purpose': answers.get('purpose', ''),
            'audience': answers.get('audience', ''),
            'slide_count': answers.get('slide_count', ''),
            'key_messages': answers.get('key_messages', []),
            'visual_style': answers.get('visual_style', ''),
            'includes_appendix': answers.get('includes_appendix', False),
        }

    elif project_type == 'proposal':
        type_specific = {
            'type': answers.get('proposal_type', ''),
            'sections': answers.get('sections', []),
            'tone': answers.get('tone', ''),
            'competitive_context': answers.get('competitive_context', ''),
            'differentiators': answers.get('differentiators', []),
            'pricing_included': answers.get('pricing_included', False),
        }

    elif project_type == 'dashboard':
        type_specific = {
            'type': answers.get('dashboard_type', ''),
            'update_frequency': answers.get('update_frequency', ''),
            'interactivity': answers.get('interactivity', ''),
            'views': answers.get('views', []),
            'filters': answers.get('filters', []),
            'target_platform': answers.get('target_platform', ''),
        }

    elif project_type == 'webapp':
        type_specific = {
            'type': answers.get('webapp_type', ''),
            'users': answers.get('users', []),
            'features': answers.get('features', []),
            'tech_stack': answers.get('tech_stack', {}),
            'auth_required': answers.get('auth_required', False),
            'deployment_target': answers.get('deployment_target', ''),
        }

    elif project_type == 'data_engineering':
        type_specific = {
            'sources': answers.get('de_sources', []),
            'transformations': answers.get('transformations', []),
            'output_format': answers.get('output_format', ''),
            'pipeline_type': answers.get('pipeline_type', ''),
        }

    elif project_type == 'analytics':
        type_specific = {
            'analysis_type': answers.get('analysis_type', ''),
            'metrics': answers.get('metrics', []),
            'visualizations': answers.get('visualizations', []),
            'comparisons': answers.get('comparisons', []),
        }

    elif project_type == 'research':
        type_specific = {
            'research_questions': answers.get('research_questions', []),
            'sources': answers.get('research_sources', []),
            'synthesis_format': answers.get('synthesis_format', ''),
        }

    if type_specific:
        spec[project_type] = type_specific

    return spec


def record_interview_episode(spec: dict) -> str:
    """
    Record an episode when interview completes.

    Args:
        spec: The completed specification dict

    Returns:
        Episode filename
    """
    from core.memory import add_episode

    project_name = spec.get('meta', {}).get('project_name', 'Unknown Project')
    project_type = spec.get('meta', {}).get('project_type', 'unknown')
    client = spec.get('meta', {}).get('client', '')

    # Build summary
    business_question = spec.get('problem', {}).get('business_question', '')
    deliverables = spec.get('deliverables', [])

    summary = f"Completed requirements gathering for '{project_name}'"
    if client:
        summary += f" (Client: {client})"
    summary += f"\n\nProject type: {project_type}"
    if business_question:
        summary += f"\n\nBusiness question: {business_question}"
    if deliverables:
        summary += f"\n\nDeliverables:\n" + "\n".join(f"- {d}" for d in deliverables[:5])

    details = {
        'project_name': project_name,
        'project_type': project_type,
        'client': client,
        'deliverable_count': len(deliverables),
    }

    return add_episode(
        event_type="interview_complete",
        summary=summary,
        details=details
    )
