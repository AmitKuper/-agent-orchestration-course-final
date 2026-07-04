"""Crumbtrail tracking and observation filtering.

Trails are stored as dict[Pos, int] where the value is the age
(number of that actor's consumed actions since they were on that cell).
Age 0 = current position (refreshed every consumed action).
"""

from cop_thief.game_engine.config import GameConfig
from cop_thief.game_engine.coordinates import Pos, is_visible
from cop_thief.game_engine.state import COP, GameState

_TRACKS_COP = {"cop_only", "both"}
_TRACKS_THIEF = {"thief_only", "both"}


def update_trail(trail: dict[Pos, int], current_pos: Pos, max_age: int) -> dict[Pos, int]:
    """Return an updated trail after the actor completed a consumed action.

    All existing ages increment by 1, entries exceeding max_age are removed,
    and the current position is refreshed to age 0.
    """
    updated: dict[Pos, int] = {}
    for pos, age in trail.items():
        new_age = age + 1
        if max_age == -1 or new_age <= max_age:
            updated[pos] = new_age
    updated[current_pos] = 0
    return updated


def update_crumbtrails(state: GameState, actor: str, cfg: GameConfig) -> None:
    """Update the appropriate crumbtrail after *actor* completed a consumed action."""
    if cfg.crumbtrail_mode == "none":
        return
    if actor == COP and cfg.crumbtrail_mode in _TRACKS_COP:
        state.cop_trail = update_trail(state.cop_trail, state.cop_position, cfg.crumbtrail_max_age)
    if actor != COP and cfg.crumbtrail_mode in _TRACKS_THIEF:
        state.thief_trail = update_trail(  # noqa: E501
            state.thief_trail, state.thief_position, cfg.crumbtrail_max_age
        )


def visible_trail(
    trail: dict[Pos, int],
    observer_pos: Pos,
    radius: int,
    partial: bool,
    offset: int,
) -> list[list]:
    """Return trail markers visible to the observer.

    Each entry is [col, row, marker] where marker encodes age + offset
    (offset 0 for thief markers, 1000 for cop markers per the PRD).
    """
    result = []
    for pos, age in trail.items():
        if partial and not is_visible(observer_pos, pos, radius):
            continue
        result.append([pos[0], pos[1], age + offset])
    return result


def get_visible_crumbtrails(
    state: GameState, actor: str, cfg: GameConfig
) -> dict[str, list]:
    """Return crumbtrail entries visible to *actor* given the observation config."""
    observer = state.actor_position(actor)
    partial = cfg.partial_observation
    radius = cfg.view_radius
    cop_entries: list = []
    thief_entries: list = []

    # Cop can see thief trail if mode is thief_only or both
    if actor == COP and cfg.crumbtrail_mode in {"thief_only", "both"}:
        thief_entries = visible_trail(state.thief_trail, observer, radius, partial, 0)

    # Thief can see cop trail if mode is cop_only or both
    if actor != COP and cfg.crumbtrail_mode in {"cop_only", "both"}:
        cop_entries = visible_trail(state.cop_trail, observer, radius, partial, 1000)

    return {"cop": cop_entries, "thief": thief_entries}
