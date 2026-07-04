"""Unit tests for RandomLegalActor."""

import pytest

from cop_thief.actors.random_actor import RandomLegalActor
from cop_thief.game_engine.actions import FORFEIT, MOVE, STAY


def test_random_actor_returns_legal_move(thief_observation):
    """RandomLegalActor must select a candidate from the observation."""
    obs, _state, _engine = thief_observation
    actor = RandomLegalActor(seed=0)
    action = actor.get_action(obs)
    assert action.type in (MOVE, STAY, FORFEIT)


def test_random_actor_avoids_forfeit_when_alternatives_exist(thief_observation):
    """RandomLegalActor should not forfeit when other candidates exist."""
    obs, _state, _engine = thief_observation
    actor = RandomLegalActor(seed=7)
    for _ in range(20):
        action = actor.get_action(obs)
        if len(obs["candidate_actions"]) > 1:
            assert action.type != FORFEIT


def test_random_actor_raises_on_empty_candidates():
    """RandomLegalActor raises ValueError when the candidate list is empty."""
    actor = RandomLegalActor(seed=0)
    with pytest.raises(ValueError, match="No candidate actions"):
        actor.get_action({"candidate_actions": []})


def test_random_actor_is_deterministic_with_seed(thief_observation):
    """Same seed produces same action sequence across two instances."""
    obs, _state, _engine = thief_observation
    a1, a2 = RandomLegalActor(seed=99), RandomLegalActor(seed=99)
    results_1 = [a1.get_action(obs).direction for _ in range(10)]
    results_2 = [a2.get_action(obs).direction for _ in range(10)]
    assert results_1 == results_2


def test_random_actor_only_candidate_forfeit():
    """When only forfeit is available, RandomLegalActor returns forfeit."""
    actor = RandomLegalActor(seed=0)
    obs = {"candidate_actions": ["forfeit"]}
    action = actor.get_action(obs)
    assert action.type == FORFEIT


def test_random_actor_direction_from_candidate(thief_observation):
    """Action direction must be one of the candidate move tokens."""
    obs, _state, _engine = thief_observation
    actor = RandomLegalActor(seed=3)
    move_candidates = [c for c in obs["candidate_actions"] if c not in ("stay", "forfeit")]
    for _ in range(15):
        action = actor.get_action(obs)
        if action.type == MOVE:
            assert action.direction in move_candidates
