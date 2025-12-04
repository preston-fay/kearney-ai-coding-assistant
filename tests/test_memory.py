"""Tests for memory module."""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch


class TestUserProfile:
    """Tests for user profile functions."""

    def test_get_default_profile_structure(self):
        """Default profile should have expected structure."""
        from core.memory import get_default_profile
        profile = get_default_profile()

        assert 'user' in profile
        assert 'preferences' in profile
        assert 'defaults' in profile
        assert 'chart' in profile['preferences']
        assert 'interview' in profile['preferences']

    def test_load_nonexistent_profile_returns_default(self, tmp_path):
        """Loading missing profile should return defaults."""
        from core.memory import load_user_profile

        with patch('core.memory.USER_PROFILE_PATH', tmp_path / 'nonexistent.yaml'):
            profile = load_user_profile()

        assert profile is not None
        assert 'preferences' in profile

    def test_save_and_load_profile(self, tmp_path):
        """Should be able to save and reload profile."""
        from core.memory import save_user_profile, load_user_profile

        profile_path = tmp_path / "profile.yaml"

        with patch('core.memory.USER_PROFILE_PATH', profile_path):
            with patch('core.memory.USER_PROFILE_DIR', tmp_path):
                test_profile = {
                    'user': {'name': 'Test User'},
                    'preferences': {'chart': {'default_format': 'png'}}
                }

                assert save_user_profile(test_profile)
                loaded = load_user_profile()

                assert loaded['user']['name'] == 'Test User'
                assert loaded['preferences']['chart']['default_format'] == 'png'

    def test_get_user_preference(self, tmp_path):
        """Should get nested preferences."""
        from core.memory import get_user_preference, save_user_profile

        profile_path = tmp_path / "profile.yaml"

        with patch('core.memory.USER_PROFILE_PATH', profile_path):
            with patch('core.memory.USER_PROFILE_DIR', tmp_path):
                test_profile = {
                    'preferences': {'chart': {'default_format': 'svg'}}
                }
                save_user_profile(test_profile)

                result = get_user_preference('preferences.chart.default_format')
                assert result == 'svg'

    def test_get_user_preference_default(self):
        """Should return default for missing preference."""
        from core.memory import get_user_preference

        result = get_user_preference('nonexistent.path', default='fallback')
        assert result == 'fallback'


class TestEpisodes:
    """Tests for episode functions."""

    def test_add_episode(self, tmp_path, monkeypatch):
        """Should create episode file."""
        from core.memory import add_episode, get_episodes_dir

        monkeypatch.chdir(tmp_path)
        (tmp_path / "project_state").mkdir()

        filename = add_episode(
            event_type="test_event",
            summary="This is a test episode"
        )

        assert filename.endswith(".md")
        assert "test_event" in filename

        episodes_dir = tmp_path / "project_state" / "episodes"
        assert (episodes_dir / filename).exists()

    def test_add_episode_with_details(self, tmp_path, monkeypatch):
        """Should include details in episode file."""
        from core.memory import add_episode

        monkeypatch.chdir(tmp_path)
        (tmp_path / "project_state").mkdir()

        filename = add_episode(
            event_type="detailed_event",
            summary="Event with details",
            details={"key": "value", "count": 42}
        )

        episodes_dir = tmp_path / "project_state" / "episodes"
        content = (episodes_dir / filename).read_text()

        assert "## Details" in content
        assert "key: value" in content

    def test_get_recent_episodes(self, tmp_path, monkeypatch):
        """Should retrieve recent episodes."""
        from core.memory import add_episode, get_recent_episodes

        monkeypatch.chdir(tmp_path)
        (tmp_path / "project_state").mkdir()

        # Add a few episodes
        add_episode("event_one", "First event")
        add_episode("event_two", "Second event")
        add_episode("event_three", "Third event")

        episodes = get_recent_episodes(2)

        assert len(episodes) == 2
        # Most recent first
        assert episodes[0]['event_type'] == 'event_three'

    def test_get_recent_episodes_empty(self, tmp_path, monkeypatch):
        """Should handle no episodes gracefully."""
        from core.memory import get_recent_episodes

        monkeypatch.chdir(tmp_path)
        # No project_state dir

        episodes = get_recent_episodes()
        assert episodes == []


class TestSessionContext:
    """Tests for session context functions."""

    def test_update_and_get_session_context(self, tmp_path, monkeypatch):
        """Should save and load session context."""
        from core.memory import update_session_context, get_session_context

        monkeypatch.chdir(tmp_path)
        (tmp_path / "project_state").mkdir()

        update_session_context({
            'current_phase': 'Phase 2',
            'focus': 'Data analysis'
        })

        context = get_session_context()

        assert context['current_phase'] == 'Phase 2'
        assert context['focus'] == 'Data analysis'
        assert 'last_updated' in context

    def test_get_session_context_empty(self, tmp_path, monkeypatch):
        """Should return empty dict when no context exists."""
        from core.memory import get_session_context

        monkeypatch.chdir(tmp_path)

        context = get_session_context()
        assert context == {}


class TestContextBuilding:
    """Tests for context building functions."""

    def test_build_memory_context_basic(self, tmp_path, monkeypatch):
        """Should build context string."""
        from core.memory import build_memory_context

        monkeypatch.chdir(tmp_path)

        context = build_memory_context()

        # Should return a string
        assert isinstance(context, str)

    def test_build_memory_context_with_profile(self, tmp_path):
        """Should include profile info in context."""
        from core.memory import build_memory_context, save_user_profile

        profile_path = tmp_path / "profile.yaml"

        with patch('core.memory.USER_PROFILE_PATH', profile_path):
            with patch('core.memory.USER_PROFILE_DIR', tmp_path):
                save_user_profile({
                    'user': {'name': 'Test User'},
                    'preferences': {
                        'interview': {'default_mode': 'express'},
                        'chart': {'default_format': 'png'}
                    }
                })

                context = build_memory_context()

                assert 'Test User' in context
                assert 'express' in context.lower()

    def test_build_memory_context_respects_max_tokens(self, tmp_path, monkeypatch):
        """Should truncate context if too long."""
        from core.memory import build_memory_context, add_episode

        monkeypatch.chdir(tmp_path)
        (tmp_path / "project_state").mkdir()

        # Add episodes with long summaries
        for i in range(10):
            add_episode(f"event_{i}", "A" * 500)

        context = build_memory_context(max_tokens=100)

        # Should be limited (100 tokens * 4 chars = 400 chars max)
        assert len(context) <= 450  # Some buffer for truncation


class TestHelperFunctions:
    """Tests for helper functions."""

    def test_deep_merge(self):
        """Should deeply merge dictionaries."""
        from core.memory import _deep_merge

        base = {'a': 1, 'b': {'c': 2, 'd': 3}}
        override = {'b': {'c': 99}, 'e': 4}

        result = _deep_merge(base, override)

        assert result['a'] == 1
        assert result['b']['c'] == 99
        assert result['b']['d'] == 3
        assert result['e'] == 4

    def test_deep_merge_empty(self):
        """Should handle empty dicts."""
        from core.memory import _deep_merge

        result = _deep_merge({}, {'a': 1})
        assert result == {'a': 1}

        result = _deep_merge({'a': 1}, {})
        assert result == {'a': 1}

    def test_get_nested(self):
        """Should get nested values."""
        from core.memory import _get_nested

        d = {'a': {'b': {'c': 'value'}}}

        assert _get_nested(d, 'a.b.c') == 'value'
        assert _get_nested(d, 'a.b.d', 'default') == 'default'
        assert _get_nested(d, 'x.y.z', None) is None

    def test_get_nested_single_key(self):
        """Should handle single key paths."""
        from core.memory import _get_nested

        d = {'key': 'value'}
        assert _get_nested(d, 'key') == 'value'

    def test_set_nested(self):
        """Should set nested values."""
        from core.memory import _set_nested

        d = {}
        _set_nested(d, 'a.b.c', 'value')

        assert d['a']['b']['c'] == 'value'

    def test_set_nested_overwrites(self):
        """Should overwrite existing values."""
        from core.memory import _set_nested

        d = {'a': {'b': {'c': 'old'}}}
        _set_nested(d, 'a.b.c', 'new')

        assert d['a']['b']['c'] == 'new'


class TestMemoryIntegration:
    """Tests for memory integration functions."""

    def test_get_agent_context_interviewer(self, tmp_path):
        """Should get interviewer-specific context."""
        from core.memory_integration import get_agent_context
        from core.memory import save_user_profile

        with patch('core.memory.USER_PROFILE_PATH', tmp_path / 'profile.yaml'):
            with patch('core.memory.USER_PROFILE_DIR', tmp_path):
                save_user_profile({
                    'user': {'name': 'Test User'},
                    'preferences': {'interview': {'default_mode': 'express'}}
                })

                context = get_agent_context('interviewer')

                assert 'express' in context.lower()
                assert 'Test User' in context

    def test_get_agent_context_presentation_builder(self, tmp_path):
        """Should get presentation-specific context."""
        from core.memory_integration import get_agent_context
        from core.memory import save_user_profile

        with patch('core.memory.USER_PROFILE_PATH', tmp_path / 'profile.yaml'):
            with patch('core.memory.USER_PROFILE_DIR', tmp_path):
                save_user_profile({
                    'preferences': {
                        'presentation': {
                            'always_include_exec_summary': True,
                            'default_slide_count_target': 12
                        }
                    }
                })

                context = get_agent_context('presentation-builder')

                assert 'executive summary' in context.lower()
                assert '12' in context

    def test_get_agent_context_planner(self, tmp_path, monkeypatch):
        """Should get planner-specific context with episodes."""
        from core.memory_integration import get_agent_context
        from core.memory import add_episode

        monkeypatch.chdir(tmp_path)
        (tmp_path / "project_state").mkdir()

        add_episode("test_event", "Test summary for planner context")

        context = get_agent_context('planner')

        assert 'Recent project history' in context or 'test_event' in context

    def test_apply_user_defaults_to_spec(self, tmp_path):
        """Should apply user defaults to spec."""
        from core.memory_integration import apply_user_defaults_to_spec
        from core.memory import save_user_profile

        with patch('core.memory.USER_PROFILE_PATH', tmp_path / 'profile.yaml'):
            with patch('core.memory.USER_PROFILE_DIR', tmp_path):
                save_user_profile({
                    'preferences': {
                        'chart': {'default_format': 'png', 'default_size': 'document'}
                    },
                    'defaults': {
                        'visualization': {'insight_depth': 'detailed'},
                        'branding': 'kearney'
                    }
                })

                spec = {'meta': {'project_name': 'Test'}}
                result = apply_user_defaults_to_spec(spec)

                assert result['visualization']['format'] == 'png'
                assert result['visualization']['insight_depth'] == 'detailed'

    def test_apply_user_defaults_preserves_existing(self, tmp_path):
        """Should not overwrite existing spec values."""
        from core.memory_integration import apply_user_defaults_to_spec
        from core.memory import save_user_profile

        with patch('core.memory.USER_PROFILE_PATH', tmp_path / 'profile.yaml'):
            with patch('core.memory.USER_PROFILE_DIR', tmp_path):
                save_user_profile({
                    'preferences': {
                        'chart': {'default_format': 'png'}
                    }
                })

                spec = {'visualization': {'format': 'svg'}}
                result = apply_user_defaults_to_spec(spec)

                # Should keep existing value
                assert result['visualization']['format'] == 'svg'

    def test_get_client_overrides(self, tmp_path):
        """Should get client-specific overrides."""
        from core.memory_integration import get_client_overrides
        from core.memory import save_user_profile

        with patch('core.memory.USER_PROFILE_PATH', tmp_path / 'profile.yaml'):
            with patch('core.memory.USER_PROFILE_DIR', tmp_path):
                save_user_profile({
                    'client_overrides': {
                        'Acme Corp': {
                            'use_light_mode': True,
                            'custom_disclaimer': 'Confidential'
                        }
                    }
                })

                overrides = get_client_overrides('Acme Corp')

                assert overrides['use_light_mode'] == True
                assert 'Confidential' in overrides['custom_disclaimer']

    def test_get_client_overrides_case_insensitive(self, tmp_path):
        """Should find client overrides case-insensitively."""
        from core.memory_integration import get_client_overrides
        from core.memory import save_user_profile

        with patch('core.memory.USER_PROFILE_PATH', tmp_path / 'profile.yaml'):
            with patch('core.memory.USER_PROFILE_DIR', tmp_path):
                save_user_profile({
                    'client_overrides': {
                        'Acme Corp': {'setting': 'value'}
                    }
                })

                # Should work with different casing
                assert get_client_overrides('acme corp')['setting'] == 'value'
                assert get_client_overrides('ACME CORP')['setting'] == 'value'

    def test_get_client_overrides_not_found(self, tmp_path):
        """Should return empty dict for unknown client."""
        from core.memory_integration import get_client_overrides
        from core.memory import save_user_profile

        with patch('core.memory.USER_PROFILE_PATH', tmp_path / 'profile.yaml'):
            with patch('core.memory.USER_PROFILE_DIR', tmp_path):
                save_user_profile({
                    'client_overrides': {
                        'Acme Corp': {'setting': 'value'}
                    }
                })

                overrides = get_client_overrides('Unknown Client')
                assert overrides == {}

    def test_update_session_after_task(self, tmp_path, monkeypatch):
        """Should update session context after task completion."""
        from core.memory_integration import update_session_after_task
        from core.memory import get_session_context

        monkeypatch.chdir(tmp_path)
        (tmp_path / "project_state").mkdir()

        update_session_after_task("1.1", "Test task", "Phase 1")

        context = get_session_context()
        assert context['current_phase'] == 'Phase 1'
        assert '1.1' in context['last_task']
        assert context['tasks_completed'] == 1
