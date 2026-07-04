"""PerformanceTable — tracks win/loss ratios by game config fingerprint.

Used by adaptive negotiation strategies to prefer configs the local server
has historically won under, and avoid configs with poor win rates.
"""

from dataclasses import dataclass

from cop_thief.game_engine.config import GameConfig


def _fingerprint(config: GameConfig) -> str:
    """Return a short string key summarising the key parameters of *config*."""
    return (
        f"{config.grid_cols}x{config.grid_rows},"
        f"mv{config.max_moves},"
        f"br{config.max_barriers},"
        f"{'partial' if config.partial_observation else 'full'}"
    )


@dataclass
class ConfigRecord:
    """Win/loss record for one config fingerprint."""

    wins: int = 0
    losses: int = 0

    @property
    def total(self) -> int:
        """Total games played under this config."""
        return self.wins + self.losses

    @property
    def win_rate(self) -> float:
        """Fraction of games won; 0.5 if no history."""
        return self.wins / self.total if self.total > 0 else 0.5


class PerformanceTable:
    """Tracks historical win/loss by config fingerprint."""

    def __init__(self) -> None:
        """Initialise an empty performance table."""
        self._table: dict[str, ConfigRecord] = {}

    def record(self, config: GameConfig, local_won: bool) -> None:
        """Record the outcome of a match played under *config*.

        Args:
            config: The config the completed match was played under.
            local_won: True if the local server won.
        """
        key = _fingerprint(config)
        rec = self._table.setdefault(key, ConfigRecord())
        if local_won:
            rec.wins += 1
        else:
            rec.losses += 1

    def win_rate(self, config: GameConfig) -> float:
        """Return the win rate for *config*, or 0.5 if no history exists."""
        key = _fingerprint(config)
        return self._table.get(key, ConfigRecord()).win_rate

    def best_config(self, candidates: list[GameConfig]) -> GameConfig | None:
        """Return the candidate with the highest historical win rate.

        Args:
            candidates: Configs to rank.

        Returns:
            The best candidate, or None if the list is empty.
        """
        if not candidates:
            return None
        return max(candidates, key=self.win_rate)

    def all_records(self) -> dict[str, ConfigRecord]:
        """Return a copy of the full performance table."""
        return dict(self._table)
