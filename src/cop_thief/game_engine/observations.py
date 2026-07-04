"""Observation builder — produces the actor-scoped view of the game state.

Under partial observation, hidden information (opponent pos, barriers outside
radius, crumbtrails outside radius) must never appear in the returned dict.
Candidate actions are observation-safe: they reflect visible information only.
The engine validates final actions against the TRUE state, not the observation.
"""

from cop_thief.game_engine.config import GameConfig
from cop_thief.game_engine.coordinates import (
    DIRECTIONS,
    Pos,
    apply_direction,
    is_visible,
    is_within_grid,
)
from cop_thief.game_engine.crumbtrails import get_visible_crumbtrails
from cop_thief.game_engine.state import COP, GameState


def _visible_barriers(state: GameState, observer: Pos, cfg: GameConfig) -> list[list[int]]:
    """Return barriers visible to the observer."""
    if not cfg.partial_observation:
        return [[b[0], b[1]] for b in sorted(state.barriers)]
    return [
        [b[0], b[1]]
        for b in sorted(state.barriers)
        if is_visible(observer, b, cfg.view_radius)
    ]


def _candidate_actions(state: GameState, actor: str, cfg: GameConfig) -> list[str]:
    """Return observation-safe candidate actions (may include moves to hidden barriers).

    This list is NOT guaranteed to be true-legal — the engine re-validates
    submitted actions against the true state before applying them.
    """
    pos = state.actor_position(actor)
    opp_pos = state.opponent_position(actor)
    partial = cfg.partial_observation

    candidates: list[str] = []
    for d in DIRECTIONS:
        t = apply_direction(pos, d)
        if not is_within_grid(t, state.grid_cols, state.grid_rows):
            continue
        # Skip only barriers the actor can SEE, and the visible opponent cell
        if not partial:
            if t in state.barriers:
                continue
            if actor != COP and t == opp_pos:
                continue
        else:
            if is_visible(pos, t, cfg.view_radius) and t in state.barriers:
                continue
            if actor != COP and t == opp_pos:
                continue
        candidates.append(d)

    if cfg.stay_enabled:
        candidates.append("stay")
    candidates.append("forfeit")
    return candidates


def build_observation(state: GameState, actor: str, cfg: GameConfig) -> dict:
    """Build the actor-scoped observation dict. Never contains hidden state."""
    observer = state.actor_position(actor)
    opp = state.opponent_position(actor)
    partial = cfg.partial_observation
    opp_visible = (not partial) or is_visible(observer, opp, cfg.view_radius)

    obs: dict = {
        "actor": actor,
        "own_position": list(observer),
        "opponent_position": list(opp) if opp_visible else None,
        "opponent_visible": opp_visible,
        "visible_barriers": _visible_barriers(state, observer, cfg),
        "visible_crumbtrails": get_visible_crumbtrails(state, actor, cfg),
        "turn_counter": state.turn_counter,
        "thief_actions_completed": state.thief_actions_completed,
        "round_index": state.round_index,
        "game_over": state.game_over,
        "winner": state.winner,
        "win_reason": state.win_reason,
        "candidate_actions": _candidate_actions(state, actor, cfg),
    }
    if actor == COP:
        obs["barriers_remaining"] = cfg.max_barriers - state.barriers_placed
    return obs
