"""Unit tests for the hidden-state filter."""

import pytest

from cop_thief.agents.hidden_state_filter import (
    _ALLOWED_FIELDS,
    assert_no_hidden_state,
    filter_observation,
)


def _full_obs() -> dict:
    """Build a complete observation dict with all expected fields."""
    return {
        "actor": "thief",
        "own_position": [2, 3],
        "opponent_position": None,
        "opponent_visible": False,
        "visible_barriers": [[1, 1]],
        "visible_crumbtrails": {"cop": [], "thief": []},
        "turn_counter": 5,
        "thief_actions_completed": 3,
        "round_index": 3,
        "game_over": False,
        "winner": None,
        "win_reason": None,
        "candidate_actions": ["N", "E", "stay"],
        # Hidden field that must be removed:
        "secret_cop_plan": "hidden",
    }


def test_filter_removes_disallowed_fields():
    """filter_observation must strip fields not in the allow-list."""
    obs = _full_obs()
    result = filter_observation(obs)
    assert "secret_cop_plan" not in result


def test_filter_preserves_allowed_fields():
    """filter_observation preserves all standard observation fields."""
    obs = _full_obs()
    result = filter_observation(obs)
    for field in _ALLOWED_FIELDS:
        if field in obs:
            assert field in result


def test_filter_does_not_mutate_original():
    """filter_observation returns a new dict, not a mutated original."""
    obs = _full_obs()
    result = filter_observation(obs)
    assert result is not obs
    assert "secret_cop_plan" in obs  # original unchanged


def test_assert_no_hidden_state_passes_clean_obs():
    """assert_no_hidden_state does not raise for a clean filtered observation."""
    obs = filter_observation(_full_obs())
    assert_no_hidden_state(obs)  # must not raise


def test_assert_no_hidden_state_raises_on_dirty():
    """assert_no_hidden_state raises AssertionError when hidden fields present."""
    dirty = {"actor": "cop", "internal_cop_state": "secret"}
    with pytest.raises(AssertionError, match="Hidden state"):
        assert_no_hidden_state(dirty)


def test_filter_empty_observation():
    """Filtering an empty dict returns an empty dict."""
    result = filter_observation({})
    assert result == {}
