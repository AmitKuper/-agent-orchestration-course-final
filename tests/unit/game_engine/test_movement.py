"""Unit tests for movement, capture, and out-of-bounds behaviour."""

import pytest

from cop_thief.game_engine.actions import (
    CONSUMED_FAILURE_STAY,
    CONSUMED_SUCCESS,
    REJECTED_INVALID,
    Action,
)
from cop_thief.game_engine.engine import GameEngine
from cop_thief.game_engine.errors import ActionOwnershipError
from tests.unit.game_engine.conftest import make_cfg, make_state


def test_thief_moves_north():
    """Thief moves one step north — position updates, turn consumed."""
    cfg = make_cfg()
    state = make_state(cfg, thief=(2, 2))
    eng = GameEngine(cfg)
    result = eng.apply_action(state, "thief", Action("move", direction="N"))
    assert result.result_type == CONSUMED_SUCCESS
    assert state.thief_position == (2, 3)
    assert state.turn_counter == 1
    assert state.thief_actions_completed == 1


def test_cop_captures_thief():
    """Cop moves into thief's cell — capture, game over."""
    cfg = make_cfg()
    state = make_state(cfg, cop=(2, 2), thief=(2, 3))
    state.current_actor = "cop"
    eng = GameEngine(cfg)
    eng.apply_action(state, "cop", Action("move", direction="N"))
    assert state.game_over
    assert state.winner == "cop"
    assert state.win_reason == "capture"


def test_thief_cannot_enter_cop_cell():
    """Thief attempting to enter cop's cell is rejected."""
    cfg = make_cfg()
    state = make_state(cfg, cop=(2, 3), thief=(2, 2))
    eng = GameEngine(cfg)
    result = eng.apply_action(state, "thief", Action("move", direction="N"))
    assert result.result_type == REJECTED_INVALID
    assert state.thief_position == (2, 2)
    assert state.turn_counter == 0


def test_out_of_bounds_stay_behavior():
    """OOB move consumes turn with stay behavior — actor stays in place."""
    cfg = make_cfg(out_of_bounds_behavior="stay")
    state = make_state(cfg, thief=(0, 0))
    eng = GameEngine(cfg)
    result = eng.apply_action(state, "thief", Action("move", direction="S"))
    assert result.result_type == CONSUMED_FAILURE_STAY
    assert state.thief_position == (0, 0)
    assert state.thief_actions_completed == 1


def test_out_of_bounds_invalid_behavior():
    """OOB move is rejected with invalid behavior — turn not consumed."""
    cfg = make_cfg(out_of_bounds_behavior="invalid")
    state = make_state(cfg, thief=(0, 0))
    eng = GameEngine(cfg)
    result = eng.apply_action(state, "thief", Action("move", direction="S"))
    assert result.result_type == REJECTED_INVALID
    assert state.thief_actions_completed == 0


def test_wrong_actor_raises():
    """Submitting action out of turn raises ActionOwnershipError."""
    cfg = make_cfg()
    state = make_state(cfg)  # current_actor = thief
    eng = GameEngine(cfg)
    with pytest.raises(ActionOwnershipError):
        eng.apply_action(state, "cop", Action("move", direction="N"))


def test_all_eight_directions():
    """All 8 movement directions produce valid positions from the centre."""
    cfg = make_cfg()
    dirs = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    expected = [(2, 3), (3, 3), (3, 2), (3, 1), (2, 1), (1, 1), (1, 2), (1, 3)]
    for d, exp in zip(dirs, expected):
        state = make_state(cfg, thief=(2, 2))
        eng = GameEngine(cfg)
        eng.apply_action(state, "thief", Action("move", direction=d))
        assert state.thief_position == exp, f"direction {d}"


def test_thief_survived():
    """Thief surviving max_moves consumed actions wins."""
    cfg = make_cfg(max_moves=2)
    state = make_state(cfg, cop=(0, 0), thief=(4, 4))
    eng = GameEngine(cfg)
    eng.apply_action(state, "thief", Action("move", direction="W"))
    assert not state.game_over
    state.current_actor = "thief"  # skip cop for this test
    state.actor_turn_index_in_round = 0
    eng.apply_action(state, "thief", Action("move", direction="W"))
    assert state.game_over
    assert state.winner == "thief"
    assert state.win_reason == "thief_survived"
