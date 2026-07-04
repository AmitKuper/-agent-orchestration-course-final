"""Sub-game and match scoring."""

from dataclasses import dataclass

from cop_thief.game_engine.config import GameConfig
from cop_thief.game_engine.state import COP, GameState

_COP_WINS = {"capture", "thief_trapped", "thief_forfeit"}
_THIEF_WINS = {"thief_survived", "cop_trapped", "cop_forfeit"}


@dataclass(frozen=True)
class SubGameScore:
    """Score awarded to each role at the end of one sub-game."""

    cop_score: int
    thief_score: int
    winner: str | None
    win_reason: str | None

    def for_player(self, player_role: str) -> int:
        """Return the score earned by a player acting as *player_role*."""
        return self.cop_score if player_role == COP else self.thief_score


def score_subgame(state: GameState, cfg: GameConfig) -> SubGameScore:
    """Compute the score for a completed sub-game.

    Technical-invalid sub-games return zero scores regardless of winner.
    """
    if not state.game_over or state.winner is None:
        return SubGameScore(0, 0, state.winner, state.win_reason)

    if state.win_reason in _COP_WINS:
        return SubGameScore(cfg.cop_win, cfg.cop_loss, COP, state.win_reason)
    if state.win_reason in _THIEF_WINS:
        return SubGameScore(cfg.cop_loss, cfg.thief_win, "thief", state.win_reason)

    return SubGameScore(0, 0, None, state.win_reason)
