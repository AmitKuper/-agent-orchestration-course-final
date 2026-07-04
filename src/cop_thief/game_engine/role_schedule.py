"""Role schedule for a match: assigns Cop/Thief per valid sub-game."""

from dataclasses import dataclass

from cop_thief.game_engine.errors import ConfigError
from cop_thief.game_engine.state import COP, THIEF

_DEFAULT_SCHEDULE = [
    (COP, THIEF),
    (THIEF, COP),
    (COP, THIEF),
    (THIEF, COP),
    (COP, THIEF),
    (THIEF, COP),
]


@dataclass(frozen=True)
class RoleAssignment:
    """Role assignment for one valid sub-game."""

    valid_subgame_index: int
    player_a_role: str
    player_b_role: str

    def role_for(self, player: str) -> str:
        """Return the role ('cop'|'thief') assigned to *player* ('a'|'b')."""
        return self.player_a_role if player == "a" else self.player_b_role

    def cop_player(self) -> str:
        """Return 'a' or 'b' — whichever player is Cop this sub-game."""
        return "a" if self.player_a_role == COP else "b"

    def thief_player(self) -> str:
        """Return 'a' or 'b' — whichever player is Thief this sub-game."""
        return "b" if self.player_a_role == COP else "a"


class RoleSchedule:
    """Immutable role assignment table for a full match."""

    def __init__(self, assignments: list[tuple[str, str]]) -> None:
        """Build a schedule from a list of (player_a_role, player_b_role) tuples."""
        _validate_schedule(assignments)
        self._assignments = [
            RoleAssignment(i + 1, a, b) for i, (a, b) in enumerate(assignments)
        ]

    @classmethod
    def default(cls, num_games: int = 6) -> "RoleSchedule":
        """Build the default alternating schedule for *num_games* sub-games."""
        if num_games != 6:
            raise ConfigError("Default schedule only supports 6 sub-games.")
        return cls(_DEFAULT_SCHEDULE)

    def get(self, valid_subgame_index: int) -> RoleAssignment:
        """Return the role assignment for sub-game *valid_subgame_index* (1-based)."""
        return self._assignments[valid_subgame_index - 1]

    def __len__(self) -> int:
        """Return the total number of sub-games in the schedule."""
        return len(self._assignments)


def _validate_schedule(assignments: list[tuple[str, str]]) -> None:
    """Raise ConfigError if the schedule does not give each player equal cop/thief games."""
    cop_a = sum(1 for a, _ in assignments if a == COP)
    thief_a = sum(1 for a, _ in assignments if a == THIEF)
    if cop_a != thief_a:
        raise ConfigError(f"Player A must have equal cop/thief sub-games; got {cop_a}/{thief_a}.")
