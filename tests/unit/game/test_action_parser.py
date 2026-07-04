"""Unit tests for action_from_dict and action_to_dict."""

import pytest

from cop_thief.game.action_parser import action_from_dict, action_to_dict
from cop_thief.game_engine.actions import BARRIER, FORFEIT, MOVE, STAY
from cop_thief.shared.errors import ValidationError


def test_move_action():
    """'move' dict produces a MOVE action with the correct direction."""
    action = action_from_dict({"type": "move", "direction": "NE"})
    assert action.type == MOVE
    assert action.direction == "NE"


def test_stay_action():
    """'stay' dict produces a STAY action."""
    action = action_from_dict({"type": "stay"})
    assert action.type == STAY


def test_forfeit_action():
    """'forfeit' dict produces a FORFEIT action."""
    action = action_from_dict({"type": "forfeit"})
    assert action.type == FORFEIT


def test_barrier_action():
    """'barrier' dict produces a BARRIER action with the correct target."""
    action = action_from_dict({"type": "barrier", "target": [3, 4]})
    assert action.type == BARRIER
    assert action.target == (3, 4)


def test_move_missing_direction_raises():
    """move without direction raises ValidationError."""
    with pytest.raises(ValidationError, match="direction"):
        action_from_dict({"type": "move"})


def test_barrier_missing_target_raises():
    """barrier without target raises ValidationError."""
    with pytest.raises(ValidationError, match="target"):
        action_from_dict({"type": "barrier"})


def test_unknown_type_raises():
    """Unknown action type raises ValidationError."""
    with pytest.raises(ValidationError, match="Unknown"):
        action_from_dict({"type": "teleport"})


def test_action_to_dict_move():
    """MOVE action serialises to dict with type and direction."""
    from cop_thief.game_engine.actions import Action  # noqa: PLC0415
    d = action_to_dict(Action(type=MOVE, direction="S"))
    assert d == {"type": MOVE, "direction": "S"}


def test_action_to_dict_barrier():
    """BARRIER action serialises to dict with type and target list."""
    from cop_thief.game_engine.actions import Action  # noqa: PLC0415
    d = action_to_dict(Action(type=BARRIER, target=(1, 2)))
    assert d == {"type": BARRIER, "target": [1, 2]}
