"""Unit tests for state_to_dict / state_from_dict round-trip."""


from cop_thief.game.state_serializer import state_from_dict, state_to_dict
from cop_thief.game_engine.config import GameConfig
from cop_thief.game_engine.engine import GameEngine


def _engine() -> GameEngine:
    """Return a small 5×5 engine."""
    cfg = GameConfig.from_dict({"grid_cols": 5, "grid_rows": 5, "num_games": 6})
    return GameEngine(cfg)


def test_round_trip_fresh_state():
    """Serialising and deserialising a fresh state produces an equal state."""
    engine = _engine()
    state = engine.initialize_subgame("m1", 1, "cop_p", "thief_p", random_seed=7)
    d = state_to_dict(state)
    restored = state_from_dict(d)
    assert restored.cop_position == state.cop_position
    assert restored.thief_position == state.thief_position
    assert restored.turn_counter == 0
    assert restored.game_over is False


def test_round_trip_preserves_barriers():
    """Barriers (set of tuples) survive serialisation."""
    engine = _engine()
    state = engine.initialize_subgame("m1", 1, "c", "t", random_seed=3)
    state.barriers.add((1, 2))
    state.barriers.add((3, 4))
    restored = state_from_dict(state_to_dict(state))
    assert (1, 2) in restored.barriers
    assert (3, 4) in restored.barriers
    assert len(restored.barriers) == 2


def test_round_trip_preserves_trails():
    """Crumbtrail dicts (with tuple keys) survive serialisation."""
    engine = _engine()
    state = engine.initialize_subgame("m1", 1, "c", "t", random_seed=5)
    state.cop_trail[(2, 3)] = 1
    state.thief_trail[(0, 0)] = 0
    restored = state_from_dict(state_to_dict(state))
    assert restored.cop_trail[(2, 3)] == 1
    assert restored.thief_trail[(0, 0)] == 0


def test_round_trip_after_moves():
    """State after several applied actions round-trips correctly."""

    engine = _engine()
    state = engine.initialize_subgame("m1", 1, "c", "t", random_seed=11)
    # Apply a few actions (engine handles turn order automatically)
    for _ in range(4):
        actor = state.current_actor
        obs = engine.get_observation(state, actor)
        from cop_thief.actors.random_actor import (  # noqa: PLC0415
            RandomLegalActor,
        )
        a = RandomLegalActor(seed=0).get_action(obs)
        if not state.game_over:
            engine.apply_action(state, actor, a)
    restored = state_from_dict(state_to_dict(state))
    assert restored.turn_counter == state.turn_counter
    assert restored.current_actor == state.current_actor


def test_state_to_dict_barriers_are_sorted():
    """Serialised barrier list is deterministically sorted."""
    engine = _engine()
    state = engine.initialize_subgame("m1", 1, "c", "t", random_seed=2)
    state.barriers = {(3, 1), (0, 4), (2, 2)}
    d = state_to_dict(state)
    assert d["barriers"] == sorted(d["barriers"])


def test_round_trip_game_over_state():
    """Serialisation preserves game_over, winner, and win_reason."""
    engine = _engine()
    state = engine.initialize_subgame("m1", 1, "c", "t", random_seed=9)
    state.game_over = True
    state.winner = "cop"
    state.win_reason = "capture"
    restored = state_from_dict(state_to_dict(state))
    assert restored.game_over is True
    assert restored.winner == "cop"
    assert restored.win_reason == "capture"
