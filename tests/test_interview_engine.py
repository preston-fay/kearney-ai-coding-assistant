# tests/test_interview_engine.py
"""Tests for interview_engine module."""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch

from core import interview_engine
from core.interview_engine import (
    Question,
    Section,
    InterviewTree,
    InterviewState,
    FollowUp,
    load_interview_tree,
    list_available_trees,
    get_project_type_menu,
    parse_project_type_choice,
    parse_multi_select,
    evaluate_condition,
    should_ask_question,
    needs_follow_up,
    format_question,
    parse_answer,
    create_interview_state,
    get_next_question,
    advance_state,
    get_progress,
    get_answers_summary,
    answers_to_spec_dict,
    PROJECT_TYPES,
)


@pytest.fixture
def sample_question():
    """Create a sample question."""
    return Question(
        id='test_question',
        prompt='What is your name?',
        question_type='text',
        required=True,
    )


@pytest.fixture
def choice_question():
    """Create a choice question."""
    return Question(
        id='problem_type',
        prompt='What type of problem is this?',
        question_type='choice',
        options=['classification', 'regression', 'clustering'],
        required=True,
    )


@pytest.fixture
def conditional_question():
    """Create a conditional question."""
    return Question(
        id='class_balance',
        prompt='Is the target balanced?',
        question_type='choice',
        options=['balanced', 'imbalanced'],
        condition="problem_type == 'classification'",
    )


@pytest.fixture
def question_with_followup():
    """Create a question with follow-up."""
    return Question(
        id='business_question',
        prompt='What is the business question?',
        question_type='text',
        follow_up=FollowUp(
            condition="len(answer) < 20",
            prompt="Can you elaborate?",
        ),
    )


@pytest.fixture
def sample_tree():
    """Create a sample interview tree."""
    return InterviewTree(
        id='test',
        name='Test Interview',
        version='1.0.0',
        sections=[
            Section(
                id='basics',
                name='Basic Information',
                questions=[
                    Question(id='name', prompt='Project name?', question_type='text'),
                    Question(id='client', prompt='Client?', question_type='text', required=False),
                ],
            ),
            Section(
                id='details',
                name='Details',
                questions=[
                    Question(
                        id='type',
                        prompt='Type?',
                        question_type='choice',
                        options=['a', 'b', 'c'],
                    ),
                ],
            ),
        ],
    )


class TestProjectTypes:
    def test_project_types_has_8_entries(self):
        assert len(PROJECT_TYPES) == 8

    def test_project_types_includes_modeling(self):
        types = [t[0] for t in PROJECT_TYPES]
        assert 'modeling' in types

    def test_project_types_includes_presentation(self):
        types = [t[0] for t in PROJECT_TYPES]
        assert 'presentation' in types


class TestGetProjectTypeMenu:
    def test_menu_includes_all_types(self):
        menu = get_project_type_menu()
        assert 'Data Engineering' in menu
        assert 'Statistical/ML Model' in menu
        assert 'Presentation' in menu

    def test_menu_has_numbers(self):
        menu = get_project_type_menu()
        assert '1.' in menu
        assert '8.' in menu


class TestParseMultiSelect:
    """Tests for parse_multi_select function."""

    def test_parse_single(self):
        """Test parsing a single selection."""
        assert parse_multi_select("2", 5) == [2]

    def test_parse_comma_space(self):
        """Test parsing comma-separated with spaces."""
        assert parse_multi_select("2, 3, 5", 5) == [2, 3, 5]

    def test_parse_comma_only(self):
        """Test parsing comma-separated without spaces."""
        assert parse_multi_select("2,3,5", 5) == [2, 3, 5]

    def test_parse_space_only(self):
        """Test parsing space-separated."""
        assert parse_multi_select("2 3 5", 5) == [2, 3, 5]

    def test_parse_deduplicates(self):
        """Test that duplicates are removed."""
        assert parse_multi_select("2, 2, 3", 5) == [2, 3]

    def test_parse_out_of_range(self):
        """Test that out-of-range values are filtered."""
        assert parse_multi_select("2, 7, 3", 5) == [2, 3]

    def test_parse_sorted(self):
        """Test that results are sorted."""
        assert parse_multi_select("5, 1, 3", 5) == [1, 3, 5]

    def test_parse_empty(self):
        """Test parsing empty string."""
        assert parse_multi_select("", 5) == []

    def test_parse_all_invalid(self):
        """Test when all selections are invalid."""
        assert parse_multi_select("10, 20", 5) == []

    def test_parse_mixed_valid_invalid(self):
        """Test mixed valid and invalid selections."""
        assert parse_multi_select("2, abc, 4, 10", 5) == [2, 4]


class TestParseProjectTypeChoice:
    def test_parse_by_number(self):
        assert parse_project_type_choice('2') == 'modeling'

    def test_parse_by_name(self):
        assert parse_project_type_choice('modeling') == 'modeling'

    def test_parse_by_partial_match(self):
        result = parse_project_type_choice('presentation')
        assert result == 'presentation'

    def test_parse_invalid(self):
        assert parse_project_type_choice('xyz') is None

    def test_parse_number_out_of_range(self):
        assert parse_project_type_choice('99') is None

    def test_parse_multiple_with_flag(self):
        """Test parsing multiple selections with allow_multiple=True."""
        result = parse_project_type_choice('2, 4', allow_multiple=True)
        assert result == ['modeling', 'presentation']

    def test_parse_single_with_multiple_flag(self):
        """Test single selection returns list when allow_multiple=True."""
        result = parse_project_type_choice('2', allow_multiple=True)
        assert result == ['modeling']

    def test_parse_multiple_without_flag(self):
        """Test that multiple selections fail without allow_multiple flag."""
        # Without the flag, only the first number is parsed
        result = parse_project_type_choice('2, 4', allow_multiple=False)
        # Should fail to parse because "2, 4" isn't a valid single int
        assert result is None


class TestEvaluateCondition:
    def test_empty_condition(self):
        assert evaluate_condition('', {}) is True

    def test_none_condition(self):
        assert evaluate_condition(None, {}) is True

    def test_simple_equality(self):
        answers = {'problem_type': 'classification'}
        assert evaluate_condition("problem_type == 'classification'", answers) is True
        assert evaluate_condition("problem_type == 'regression'", answers) is False

    def test_not_equal(self):
        answers = {'problem_type': 'clustering'}
        assert evaluate_condition("problem_type != 'classification'", answers) is True

    def test_in_list(self):
        answers = {'problem_type': 'classification'}
        assert evaluate_condition("problem_type in ['classification', 'regression']", answers) is True

    def test_boolean_check(self):
        answers = {'required': True}
        assert evaluate_condition("required == True", answers) is True

    def test_len_function(self):
        answers = {'text': 'short'}
        assert evaluate_condition("len(text) < 10", answers) is True
        assert evaluate_condition("len(text) > 100", answers) is False

    def test_invalid_condition_returns_true(self):
        # Invalid conditions should default to True (show question)
        assert evaluate_condition("invalid syntax !!!", {}) is True


class TestShouldAskQuestion:
    def test_no_condition(self, sample_question):
        assert should_ask_question(sample_question, {}) is True

    def test_condition_met(self, conditional_question):
        answers = {'problem_type': 'classification'}
        assert should_ask_question(conditional_question, answers) is True

    def test_condition_not_met(self, conditional_question):
        answers = {'problem_type': 'regression'}
        assert should_ask_question(conditional_question, answers) is False


class TestNeedsFollowUp:
    def test_no_followup_defined(self, sample_question):
        assert needs_follow_up(sample_question, 'any answer', {}) is False

    def test_followup_condition_met(self, question_with_followup):
        # Answer is too short
        assert needs_follow_up(question_with_followup, 'short', {}) is True

    def test_followup_condition_not_met(self, question_with_followup):
        # Answer is long enough
        long_answer = 'This is a sufficiently long answer to the question'
        assert needs_follow_up(question_with_followup, long_answer, {}) is False


class TestFormatQuestion:
    def test_format_text_question(self, sample_question):
        formatted = format_question(sample_question)
        assert 'What is your name?' in formatted

    def test_format_choice_question(self, choice_question):
        formatted = format_question(choice_question)
        assert '1. classification' in formatted
        assert '2. regression' in formatted
        assert '3. clustering' in formatted

    def test_format_optional_question(self):
        question = Question(
            id='opt',
            prompt='Optional?',
            question_type='text',
            required=False,
        )
        formatted = format_question(question)
        assert 'Optional' in formatted or 'skip' in formatted.lower()

    def test_format_boolean_question(self):
        question = Question(
            id='bool',
            prompt='Is this true?',
            question_type='boolean',
        )
        formatted = format_question(question)
        assert 'yes' in formatted.lower() or 'no' in formatted.lower()


class TestParseAnswer:
    def test_parse_text(self):
        q = Question(id='t', prompt='', question_type='text')
        assert parse_answer(q, 'hello world') == 'hello world'

    def test_parse_text_strips_whitespace(self):
        q = Question(id='t', prompt='', question_type='text')
        assert parse_answer(q, '  hello  ') == 'hello'

    def test_parse_choice_by_number(self, choice_question):
        assert parse_answer(choice_question, '1') == 'classification'
        assert parse_answer(choice_question, '2') == 'regression'

    def test_parse_choice_by_name(self, choice_question):
        assert parse_answer(choice_question, 'regression') == 'regression'

    def test_parse_boolean_yes(self):
        q = Question(id='b', prompt='', question_type='boolean')
        assert parse_answer(q, 'yes') is True
        assert parse_answer(q, 'y') is True
        assert parse_answer(q, 'true') is True

    def test_parse_boolean_no(self):
        q = Question(id='b', prompt='', question_type='boolean')
        assert parse_answer(q, 'no') is False
        assert parse_answer(q, 'n') is False

    def test_parse_number_int(self):
        q = Question(id='n', prompt='', question_type='number')
        assert parse_answer(q, '42') == 42

    def test_parse_number_float(self):
        q = Question(id='n', prompt='', question_type='number')
        assert parse_answer(q, '3.14') == 3.14

    def test_parse_list(self):
        q = Question(id='l', prompt='', question_type='list')
        assert parse_answer(q, 'a, b, c') == ['a', 'b', 'c']

    def test_parse_multi_by_number(self):
        q = Question(
            id='m',
            prompt='',
            question_type='multi',
            options=['opt1', 'opt2', 'opt3'],
        )
        assert parse_answer(q, '1, 3') == ['opt1', 'opt3']

    def test_parse_empty_with_default(self):
        q = Question(id='d', prompt='', question_type='text', default='default_value')
        assert parse_answer(q, '') == 'default_value'

    def test_parse_empty_optional(self):
        q = Question(id='o', prompt='', question_type='text', required=False)
        assert parse_answer(q, '') is None


class TestInterviewState:
    def test_create_state(self):
        state = create_interview_state('modeling')
        assert state.tree_id == 'modeling'
        assert state.current_section_idx == 0
        assert state.current_question_idx == 0
        assert state.answers == {}
        assert state.completed is False


class TestGetNextQuestion:
    def test_get_first_question(self, sample_tree):
        state = create_interview_state('test')
        question = get_next_question(sample_tree, state)

        assert question is not None
        assert question.id == 'name'

    def test_advance_to_next_question(self, sample_tree):
        state = create_interview_state('test')
        state.answers['name'] = 'Test'

        get_next_question(sample_tree, state)
        advance_state(state)

        question = get_next_question(sample_tree, state)
        assert question.id == 'client'

    def test_advance_to_next_section(self, sample_tree):
        state = create_interview_state('test')
        state.current_section_idx = 0
        state.current_question_idx = 2  # Past last question in section

        question = get_next_question(sample_tree, state)
        assert question.id == 'type'
        assert state.current_section_idx == 1

    def test_complete_when_no_more_questions(self, sample_tree):
        state = create_interview_state('test')
        state.current_section_idx = 2  # Past last section

        question = get_next_question(sample_tree, state)
        assert question is None
        assert state.completed is True

    def test_skips_conditional_questions(self):
        tree = InterviewTree(
            id='test',
            name='Test',
            version='1.0.0',
            sections=[
                Section(
                    id='s1',
                    name='S1',
                    questions=[
                        Question(id='q1', prompt='Q1', question_type='text'),
                        Question(
                            id='q2',
                            prompt='Q2',
                            question_type='text',
                            condition="some_var == 'yes'",
                        ),
                        Question(id='q3', prompt='Q3', question_type='text'),
                    ],
                ),
            ],
        )
        state = create_interview_state('test')
        state.answers = {'some_var': 'no'}
        state.current_question_idx = 1  # Start at q2

        question = get_next_question(tree, state)
        assert question.id == 'q3'  # Skipped q2


class TestGetProgress:
    def test_progress_at_start(self, sample_tree):
        state = create_interview_state('test')
        answered, total = get_progress(sample_tree, state)
        assert answered == 0
        assert total == 3

    def test_progress_after_answers(self, sample_tree):
        state = create_interview_state('test')
        state.answers = {'name': 'Test', 'client': 'Client'}
        answered, total = get_progress(sample_tree, state)
        assert answered == 2
        assert total == 3


class TestGetAnswersSummary:
    def test_summary_empty(self):
        state = create_interview_state('test')
        summary = get_answers_summary(state)
        assert 'No answers' in summary

    def test_summary_with_answers(self):
        state = create_interview_state('test')
        state.answers = {
            'name': 'Test Project',
            'type': 'modeling',
        }
        summary = get_answers_summary(state)
        assert 'name' in summary
        assert 'Test Project' in summary


class TestAnswersToSpecDict:
    def test_basic_conversion(self):
        answers = {
            'project_name': 'My Project',
            'client': 'Acme Corp',
            'business_question': 'How to predict churn?',
        }
        spec = answers_to_spec_dict('modeling', answers)

        assert spec['meta']['project_name'] == 'My Project'
        assert spec['meta']['project_type'] == 'modeling'
        assert spec['meta']['client'] == 'Acme Corp'
        assert spec['problem']['business_question'] == 'How to predict churn?'

    def test_modeling_type_specific(self):
        answers = {
            'project_name': 'Churn Model',
            'problem_type': 'classification',
            'target_variable': 'churned',
            'validation_strategy': 'time_based',
        }
        spec = answers_to_spec_dict('modeling', answers)

        assert 'modeling' in spec
        assert spec['modeling']['problem_type'] == 'classification'
        assert spec['modeling']['target_variable'] == 'churned'

    def test_presentation_type_specific(self):
        answers = {
            'project_name': 'Q4 Readout',
            'purpose': 'readout',
            'audience': 'c_suite',
            'slide_count': '15',
        }
        spec = answers_to_spec_dict('presentation', answers)

        assert 'presentation' in spec
        assert spec['presentation']['purpose'] == 'readout'
        assert spec['presentation']['audience'] == 'c_suite'

    def test_brand_constraint_always_set(self):
        answers = {'project_name': 'Test'}
        spec = answers_to_spec_dict('analytics', answers)

        assert spec['constraints']['brand'] == 'kearney'


class TestLoadInterviewTree:
    def test_load_nonexistent_tree(self, tmp_path):
        with patch.object(interview_engine, 'INTERVIEWS_DIR', tmp_path):
            result = load_interview_tree('nonexistent')
            assert result is None

    def test_load_valid_tree(self, tmp_path):
        # Create a test tree file
        tree_content = """
id: test_tree
name: Test Tree
version: "1.0.0"
sections:
  - id: basics
    name: Basics
    questions:
      - id: q1
        prompt: Question 1?
        type: text
        required: true
"""
        tree_file = tmp_path / 'test_tree.yaml'
        tree_file.write_text(tree_content)

        with patch.object(interview_engine, 'INTERVIEWS_DIR', tmp_path):
            tree = load_interview_tree('test_tree')

            assert tree is not None
            assert tree.id == 'test_tree'
            assert tree.name == 'Test Tree'
            assert len(tree.sections) == 1
            assert len(tree.sections[0].questions) == 1


class TestListAvailableTrees:
    def test_list_empty_dir(self, tmp_path):
        with patch.object(interview_engine, 'INTERVIEWS_DIR', tmp_path):
            trees = list_available_trees()
            assert trees == []

    def test_list_with_trees(self, tmp_path):
        (tmp_path / 'modeling.yaml').write_text('id: modeling')
        (tmp_path / 'presentation.yaml').write_text('id: presentation')

        with patch.object(interview_engine, 'INTERVIEWS_DIR', tmp_path):
            trees = list_available_trees()
            assert 'modeling' in trees
            assert 'presentation' in trees
