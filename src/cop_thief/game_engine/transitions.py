"""State transition functions — apply a validated action and mutate GameState.

Each function returns an ActionResult describing what happened.
Win-condition checks (trapped, survival) happen in engine.py after this.
"""

from cop_thief.game_engine.actions import (
    BARRIER,
    CONSUMED_FAILURE_STAY,
    CONSUMED_SUCCESS,
    FORFEIT,
    MOVE,
    PUBLIC_BARRIER_PLACED,
    PUBLIC_FORFEIT,
    PUBLIC_MOVE_APPLIED,
    PUBLIC_MOVE_FAILED,
    PUBLIC_REJECTED,
    PUBLIC_STAY_APPLIED,
    REJECTED_INVALID,
    STAY,
    TERMINAL_FORFEIT,
    Action,
    ActionResult,
)
from cop_thief.game_engine.config import GameConfig
from cop_thief.game_engine.coordinates import apply_direction, is_within_grid
from cop_thief.game_engine.state import COP, GameState


def _rejected(reason: str) -> ActionResult:
    """Return a REJECTED_INVALID result with the given engine reason."""
    return ActionResult(
        REJECTED_INVALID, PUBLIC_REJECTED, False, False, private_engine_reason=reason
    )


def _failed_stay(from_pos, reason: str) -> ActionResult:
    """Return a CONSUMED_FAILURE_STAY result (actor stays in place)."""
    return ActionResult(
        CONSUMED_FAILURE_STAY, PUBLIC_MOVE_FAILED, True, False,
        from_pos, from_pos, private_engine_reason=reason,
    )


def apply_action(state: GameState, actor: str, action: Action, cfg: GameConfig) -> ActionResult:
    """Dispatch action to the appropriate handler and return the result."""
    if action.type == MOVE:
        return _apply_move(state, actor, action, cfg)
    if action.type == STAY:
        return _apply_stay(state, actor, cfg)
    if action.type == BARRIER:
        return _apply_barrier(state, actor, action, cfg)
    if action.type == FORFEIT:
        return _apply_forfeit(state, actor)
    return _rejected("unknown_action_type")


def _apply_move(state: GameState, actor: str, action: Action, cfg: GameConfig) -> ActionResult:
    """Validate and apply a move action."""
    if not action.direction:
        return _rejected("missing_direction")
    from_pos = state.actor_position(actor)
    opp_pos = state.opponent_position(actor)
    target = apply_direction(from_pos, action.direction)

    if not is_within_grid(target, state.grid_cols, state.grid_rows):
        if cfg.out_of_bounds_behavior == "invalid":
            return _rejected("out_of_bounds")
        return _failed_stay(from_pos, "out_of_bounds")

    if target in state.barriers:
        if cfg.barrier_collision_behavior == "invalid":
            return _rejected("barrier_collision")
        return _failed_stay(from_pos, "barrier_collision")

    if actor != COP and target == opp_pos:
        return _rejected("cop_cell")

    state.set_position(actor, target)

    if actor == COP and target == opp_pos:  # capture
        state.game_over = True
        state.winner = COP
        state.win_reason = "capture"

    return ActionResult(CONSUMED_SUCCESS, PUBLIC_MOVE_APPLIED, True, True, from_pos, target)


def _apply_stay(state: GameState, actor: str, cfg: GameConfig) -> ActionResult:
    """Apply a stay action if stay is enabled."""
    if not cfg.stay_enabled:
        return _rejected("stay_disabled")
    pos = state.actor_position(actor)
    return ActionResult(CONSUMED_SUCCESS, PUBLIC_STAY_APPLIED, True, False, pos, pos)


def _apply_barrier(state: GameState, actor: str, action: Action, cfg: GameConfig) -> ActionResult:
    """Validate and apply a barrier placement by the cop."""
    if actor != COP:
        return _rejected("only_cop_places_barriers")
    if cfg.max_barriers == 0 or state.barriers_placed >= cfg.max_barriers:
        return _rejected("barrier_limit_reached")
    if not action.target:
        return _rejected("missing_target")
    target = action.target
    if not is_within_grid(target, state.grid_cols, state.grid_rows):
        return _rejected("target_out_of_bounds")
    if target in state.barriers:
        return _rejected("cell_already_barrier")
    if target == state.thief_position:
        return _rejected("cannot_barrier_thief_cell")

    cop_pos = state.cop_position
    dc = abs(target[0] - cop_pos[0])
    dr = abs(target[1] - cop_pos[1])
    if cfg.barrier_placement_scope == "adjacent_only" and max(dc, dr) != 1:
        return _rejected("target_not_adjacent")
    if cfg.barrier_placement_scope != "adjacent_only" and max(dc, dr) > 1:
        return _rejected("target_not_adjacent_or_current")

    state.barriers.add(target)
    state.barriers_placed += 1
    return ActionResult(
        CONSUMED_SUCCESS, PUBLIC_BARRIER_PLACED, True, True, cop_pos, cop_pos, barrier_at=target
    )


def _apply_forfeit(state: GameState, actor: str) -> ActionResult:
    """Apply a voluntary forfeit — opponent wins immediately."""
    opponent = "thief" if actor == COP else COP
    state.game_over = True
    state.winner = opponent
    state.win_reason = f"{actor}_forfeit"
    pos = state.actor_position(actor)
    return ActionResult(TERMINAL_FORFEIT, PUBLIC_FORFEIT, True, False, pos, pos)
