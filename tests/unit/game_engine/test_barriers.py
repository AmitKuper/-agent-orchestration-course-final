"""Unit tests for barrier placement and collision."""

from cop_thief.game_engine.actions import CONSUMED_SUCCESS, REJECTED_INVALID, Action
from cop_thief.game_engine.engine import GameEngine
from tests.unit.game_engine.conftest import make_cfg, make_state


def test_cop_places_barrier_adjacent():
    """Cop places a barrier in an adjacent cell."""
    cfg = make_cfg()
    state = make_state(cfg, cop=(2, 2), thief=(4, 4))
    state.current_actor = "cop"
    eng = GameEngine(cfg)
    result = eng.apply_action(state, "cop", Action("barrier", target=(2, 3)))
    assert result.result_type == CONSUMED_SUCCESS
    assert (2, 3) in state.barriers
    assert state.barriers_placed == 1


def test_barrier_blocks_thief():
    """Thief cannot enter a cell with a barrier (invalid behavior)."""
    cfg = make_cfg(barrier_collision_behavior="invalid")
    state = make_state(cfg, cop=(0, 0), thief=(2, 2))
    state.barriers.add((2, 3))
    eng = GameEngine(cfg)
    result = eng.apply_action(state, "thief", Action("move", direction="N"))
    assert result.result_type == REJECTED_INVALID
    assert state.thief_position == (2, 2)


def test_barrier_limit_enforced():
    """Cop cannot place more barriers than max_barriers."""
    cfg = make_cfg(max_barriers=1)
    state = make_state(cfg, cop=(2, 2), thief=(4, 4))
    state.current_actor = "cop"
    eng = GameEngine(cfg)
    eng.apply_action(state, "cop", Action("barrier", target=(2, 3)))
    state.current_actor = "cop"
    result = eng.apply_action(state, "cop", Action("barrier", target=(3, 2)))
    assert result.result_type == REJECTED_INVALID
    assert len(state.barriers) == 1


def test_cannot_barrier_thief_cell():
    """Cop cannot place a barrier on the thief's current cell."""
    cfg = make_cfg()
    state = make_state(cfg, cop=(2, 2), thief=(2, 3))
    state.current_actor = "cop"
    eng = GameEngine(cfg)
    result = eng.apply_action(state, "cop", Action("barrier", target=(2, 3)))
    assert result.result_type == REJECTED_INVALID


def test_cannot_barrier_non_adjacent():
    """Cop cannot place a barrier outside the adjacent scope."""
    cfg = make_cfg(barrier_placement_scope="adjacent_only")
    state = make_state(cfg, cop=(0, 0), thief=(4, 4))
    state.current_actor = "cop"
    eng = GameEngine(cfg)
    result = eng.apply_action(state, "cop", Action("barrier", target=(3, 3)))
    assert result.result_type == REJECTED_INVALID


def test_barrier_collision_stay():
    """Thief hitting a barrier with stay behavior consumes the turn."""
    cfg = make_cfg(barrier_collision_behavior="stay")
    state = make_state(cfg, cop=(0, 0), thief=(2, 2))
    state.barriers.add((2, 3))
    eng = GameEngine(cfg)
    result = eng.apply_action(state, "thief", Action("move", direction="N"))
    from cop_thief.game_engine.actions import CONSUMED_FAILURE_STAY
    assert result.result_type == CONSUMED_FAILURE_STAY
    assert state.thief_actions_completed == 1
