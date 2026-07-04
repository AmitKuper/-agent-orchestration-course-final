"""Win-condition checks performed after each consumed action.

Capture and forfeit are detected in transitions.py.
This module handles: opponent trapped, thief survival.

Call check_post_action_wins() after applying a consumed action and
updating counters. It returns (winner, win_reason) or None.
"""

from cop_thief.game_engine.config import GameConfig
from cop_thief.game_engine.coordinates import DIRECTIONS, apply_direction, is_within_grid
from cop_thief.game_engine.state import COP, GameState


def _has_any_legal_move(state: GameState, actor: str, cfg: GameConfig) -> bool:
    """Return True if *actor* can move to at least one in-grid, unblocked cell."""
    pos = state.actor_position(actor)
    opp = state.opponent_position(actor)
    for d in DIRECTIONS:
        t = apply_direction(pos, d)
        if not is_within_grid(t, state.grid_cols, state.grid_rows):
            continue
        if t in state.barriers:
            continue
        if actor != COP and t == opp:
            continue
        return True
    return False


def _can_place_barrier(state: GameState, cfg: GameConfig) -> bool:
    """Return True if the cop can legally place at least one more barrier."""
    if cfg.max_barriers == 0 or state.barriers_placed >= cfg.max_barriers:
        return False
    cop_pos = state.cop_position
    for d in DIRECTIONS:
        t = apply_direction(cop_pos, d)
        if not is_within_grid(t, state.grid_cols, state.grid_rows):
            continue
        if t in state.barriers or t == state.thief_position:
            continue
        return True
    if cfg.barrier_placement_scope == "current_and_adjacent":
        t = cop_pos
        if t not in state.barriers:
            return True
    return False


def _is_trapped(state: GameState, actor: str, cfg: GameConfig) -> bool:
    """Return True if *actor* has no legal action that can consume a turn."""
    if cfg.stay_enabled:
        return False
    if _has_any_legal_move(state, actor, cfg):
        return False
    if actor == COP and _can_place_barrier(state, cfg):
        return False
    return True


def check_post_action_wins(
    state: GameState, actor: str, cfg: GameConfig
) -> tuple[str, str] | None:
    """Check for trapped and survival wins after *actor* consumed a turn.

    Returns (winner, win_reason) or None. Called only when state.game_over
    is False (capture/forfeit already handled in transitions.py).
    """
    opponent = "thief" if actor == COP else COP

    # Thief survival: after thief's consumed action reaches max_moves
    if actor != COP and state.thief_actions_completed >= cfg.max_moves:
        return ("thief", "thief_survived")

    # Opponent trapped
    if _is_trapped(state, opponent, cfg):
        win_reason = "thief_trapped" if opponent == "thief" else "cop_trapped"
        return (actor, win_reason)

    return None
