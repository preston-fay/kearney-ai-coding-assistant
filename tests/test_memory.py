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
