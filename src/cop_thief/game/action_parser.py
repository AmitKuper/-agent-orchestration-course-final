"""Convert API action dicts to ``Action`` objects and back.

The API surface uses plain dicts; the game engine expects ``Action`` instances.
"""

from cop_thief.game_engine.actions import BARRIER, FORFEIT, MOVE, STAY, Action
from cop_thief.shared.errors import ValidationError


def action_from_dict(d: dict) -> Action:
    """Build an ``Action`` from an API-submitted dict.

    Expected shapes:
    - ``{"type": "move", "direction": "N"}``
    - ``{"type": "stay"}``
    - ``{"type": "forfeit"}``
    - ``{"type": "barrier", "target": [col, row]}``

    Args:
        d: Raw dict from the HTTP request body.

    Returns:
        A validated ``Action``.

    Raises:
        ValidationError: If the dict is missing required fields or has unknown type.
    """
    action_type = d.get("type", "").lower()
    if action_type == "move":
        direction = d.get("direction")
        if not direction:
            raise ValidationError("move action requires 'direction'")
        return Action(type=MOVE, direction=str(direction).upper())
    if action_type == "stay":
        return Action(type=STAY)
    if action_type == "forfeit":
        return Action(type=FORFEIT)
    if action_type == "barrier":
        target = d.get("target")
        if not target or len(target) != 2:
            raise ValidationError("barrier action requires 'target' [col, row]")
        return Action(type=BARRIER, target=(int(target[0]), int(target[1])))
    raise ValidationError(f"Unknown action type: {action_type!r}")


def action_to_dict(action: Action) -> dict:
    """Serialise an ``Action`` to a plain dict for storage in ``GameEvent``."""
    d: dict = {"type": action.type}
    if action.direction:
        d["direction"] = action.direction
    if action.target:
        d["target"] = list(action.target)
    return d
