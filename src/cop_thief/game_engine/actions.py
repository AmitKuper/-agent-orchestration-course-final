"""Action and ActionResult value types."""

from dataclasses import dataclass

from cop_thief.game_engine.coordinates import Pos

# Action types
MOVE = "move"
STAY = "stay"
BARRIER = "barrier"
FORFEIT = "forfeit"
VALID_ACTION_TYPES = {MOVE, STAY, BARRIER, FORFEIT}

# Result types
CONSUMED_SUCCESS = "consumed_success"
CONSUMED_FAILURE_STAY = "consumed_failure_stay"
REJECTED_INVALID = "rejected_invalid"
TERMINAL_FORFEIT = "terminal_forfeit"

# Public result strings (safe to send to actors)
PUBLIC_MOVE_APPLIED = "move_applied"
PUBLIC_MOVE_FAILED = "move_failed"
PUBLIC_BARRIER_PLACED = "barrier_placed"
PUBLIC_STAY_APPLIED = "stay_applied"
PUBLIC_REJECTED = "action_rejected"
PUBLIC_FORFEIT = "forfeit_accepted"


@dataclass(frozen=True)
class Action:
    """One submitted action from an actor."""

    type: str
    direction: str | None = None
    target: Pos | None = None
    message: str | None = None


@dataclass(frozen=True)
class ActionResult:
    """Outcome of applying one action to the game state.

    Callers must read state.game_over / state.winner for the authoritative
    end-of-game status — this result describes only the action mechanics.
    """

    result_type: str
    public_result: str
    turn_consumed: bool
    state_changed: bool
    from_pos: Pos | None = None
    to_pos: Pos | None = None
    barrier_at: Pos | None = None
    private_engine_reason: str | None = None
