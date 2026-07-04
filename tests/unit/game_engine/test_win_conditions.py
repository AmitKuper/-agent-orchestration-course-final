"""Unit tests for all win conditions."""

from cop_thief.game_engine.actions import TERMINAL_FORFEIT, Action
from cop_thief.game_engine.engine import GameEngine
from tests.unit.game_engine.conftest import make_cfg, make_state


def test_cop_forfeit():
    """Cop voluntarily forfeiting gives thief the win."""
    cfg = make_cfg()
    state = make_state(cfg, cop=(2, 2), thief=(4, 4))
    state.current_actor = "cop"
    eng = GameEngine(cfg)
    result = eng.apply_action(state, "cop", Action("forfeit"))
    assert result.result_type == TERMINAL_FORFEIT
    assert state.winner == "thief"
    assert state.win_reason == "cop_forfeit"


def test_thief_forfeit():
    """Thief voluntarily forfeiting gives cop the win."""
    cfg = make_cfg()
    state = make_state(cfg)
    eng = GameEngine(cfg)
    result = eng.apply_action(state, "thief", Action("forfeit"))
    assert result.result_type == TERMINAL_FORFEIT
    assert state.winner == "cop"
    assert state.win_reason == "thief_forfeit"


def test_thief_trapped_when_stay_disabled():
    """Thief with no legal moves and stay disabled is trapped — cop wins."""
    # 3×3 grid; thief at corner (0,0), all 3 adjacent cells blocked by barriers.
    # Cop at (2,2) makes a legal move, triggering the trap check.
    cfg = make_cfg(stay_enabled=False, grid_cols=3, grid_rows=3, max_moves=100)
    state = make_state(cfg, cop=(2, 2), thief=(0, 0))
    state.barriers = {(1, 0), (0, 1), (1, 1)}
    state.current_actor = "cop"
    eng = GameEngine(cfg)
    eng.apply_action(state, "cop", Action("move", direction="W"))  # cop → (1,2)
    assert state.game_over
    assert state.winner == "cop"
    assert state.win_reason == "thief_trapped"


def test_capture_on_cop_move():
    """Cop entering thief's cell is a capture."""
    cfg = make_cfg()
    state = make_state(cfg, cop=(3, 4), thief=(4, 4))
    state.current_actor = "cop"
    eng = GameEngine(cfg)
    eng.apply_action(state, "cop", Action("move", direction="E"))
    assert state.game_over
    assert state.winner == "cop"
    assert state.win_reason == "capture"


def test_no_extra_cop_turn_after_survival():
    """Cop does not get an extra turn after thief survival."""
    cfg = make_cfg(max_moves=1)
    state = make_state(cfg, cop=(0, 0), thief=(4, 4))
    eng = GameEngine(cfg)
    eng.apply_action(state, "thief", Action("move", direction="W"))
    assert state.game_over
    assert state.winner == "thief"
    assert state.win_reason == "thief_survived"
