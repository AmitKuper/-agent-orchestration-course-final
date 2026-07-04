"""GameState — mutable true game state for one sub-game.

Only the engine and orchestrator touch this object directly.
Actors receive ObservationState (see observations.py), never GameState.
"""

from dataclasses import dataclass, field

from cop_thief.game_engine.coordinates import Pos

COP = "cop"
THIEF = "thief"


@dataclass
class GameState:
    """Complete true state of one sub-game instance."""

    match_id: str
    valid_subgame_index: int
    replay_attempt_index: int
    grid_cols: int
    grid_rows: int
    cop_player_id: str
    thief_player_id: str
    cop_position: Pos
    thief_position: Pos
    current_actor: str = THIEF

    barriers: set[Pos] = field(default_factory=set)
    barriers_placed: int = 0

    turn_counter: int = 0
    thief_actions_completed: int = 0
    round_index: int = 1
    actor_turn_index_in_round: int = 0

    # Crumbtrails: pos → age in that actor's consumed actions (0 = current)
    cop_trail: dict[Pos, int] = field(default_factory=dict)
    thief_trail: dict[Pos, int] = field(default_factory=dict)

    game_over: bool = False
    winner: str | None = None
    win_reason: str | None = None

    def actor_position(self, actor: str) -> Pos:
        """Return the current position of *actor*."""
        return self.cop_position if actor == COP else self.thief_position

    def opponent_position(self, actor: str) -> Pos:
        """Return the current position of the opponent of *actor*."""
        return self.thief_position if actor == COP else self.cop_position

    def set_position(self, actor: str, pos: Pos) -> None:
        """Update *actor*'s position."""
        if actor == COP:
            self.cop_position = pos
        else:
            self.thief_position = pos

    def player_id(self, role: str) -> str:
        """Return the player ID for the given *role*."""
        return self.cop_player_id if role == COP else self.thief_player_id
