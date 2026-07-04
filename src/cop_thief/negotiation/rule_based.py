"""RuleBasedNegotiator — deterministic preference-ordering negotiation strategy.

Proposes configs from a ranked preference list and accepts opponent proposals
whose key parameters fall within acceptable ranges. Integrates with the
PerformanceTable for outcome-aware evaluation.
"""

from cop_thief.game_engine.config import GameConfig
from cop_thief.negotiation.base import NegotiationStrategy
from cop_thief.negotiation.performance_table import PerformanceTable

# Preference list (index 0 = most preferred).
_PREFERRED_CONFIGS: list[dict] = [
    {"grid_cols": 8, "grid_rows": 8, "max_moves": 20, "max_barriers": 5},
    {"grid_cols": 6, "grid_rows": 6, "max_moves": 15, "max_barriers": 3},
    {"grid_cols": 10, "grid_rows": 10, "max_moves": 25, "max_barriers": 5},
]

# Acceptance thresholds for evaluating opponent proposals.
_MIN_GRID = 4
_MAX_GRID = 12
_MIN_MOVES = 10
_MAX_MOVES = 50
_MAX_BARRIERS_LIMIT = 10


class RuleBasedNegotiator(NegotiationStrategy):
    """Deterministic negotiation using a ranked preference list.

    Proposes the highest-ranked config (optionally weighted by history).
    Accepts any proposal whose parameters are within defined acceptable ranges.
    """

    def __init__(self, table: PerformanceTable | None = None) -> None:
        """Bind the negotiator to an optional PerformanceTable.

        Args:
            table: Historical win/loss table; if None, history is not used.
        """
        self._table = table

    def propose(self) -> GameConfig:
        """Return the preferred config, optionally favouring historically strong ones.

        If a PerformanceTable is available, the preferred list is ranked by
        win rate and the best-performing config is proposed.

        Returns:
            A valid ``GameConfig`` to send to the opponent.
        """
        candidates = [GameConfig(**kw) for kw in _PREFERRED_CONFIGS]
        if self._table is not None:
            best = self._table.best_config(candidates)
            return best if best is not None else candidates[0]
        return candidates[0]

    def evaluate(self, proposed: GameConfig) -> bool:
        """Accept a proposal if all parameters are within acceptable bounds.

        Args:
            proposed: Config proposed by the remote server.

        Returns:
            True if the proposal is acceptable.
        """
        if not (_MIN_GRID <= proposed.grid_cols <= _MAX_GRID):
            return False
        if not (_MIN_GRID <= proposed.grid_rows <= _MAX_GRID):
            return False
        if not (_MIN_MOVES <= proposed.max_moves <= _MAX_MOVES):
            return False
        if proposed.max_barriers > _MAX_BARRIERS_LIMIT:
            return False
        if self._table is not None:
            return self._table.win_rate(proposed) >= 0.3
        return True

    def on_result(self, config: GameConfig, local_won: bool) -> None:
        """Record the match result in the performance table if available."""
        if self._table is not None:
            self._table.record(config, local_won)
