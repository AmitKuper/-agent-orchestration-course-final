"""Unit tests for PerformanceTable."""

from cop_thief.game_engine.config import GameConfig
from cop_thief.negotiation.performance_table import PerformanceTable


def _cfg(**overrides) -> GameConfig:
    """Return a GameConfig with optional field overrides."""
    base = {"grid_cols": 8, "grid_rows": 8, "max_moves": 20, "max_barriers": 5, "num_games": 6}
    base.update(overrides)
    return GameConfig(**base)


def test_initial_win_rate_is_half():
    """Win rate for an unseen config is 0.5 (neutral prior)."""
    table = PerformanceTable()
    assert table.win_rate(_cfg()) == 0.5


def test_record_win_increases_win_rate():
    """Recording a win raises the win rate above 0.5."""
    table = PerformanceTable()
    cfg = _cfg()
    table.record(cfg, local_won=True)
    assert table.win_rate(cfg) > 0.5


def test_record_loss_decreases_win_rate():
    """Recording a loss lowers the win rate below 0.5."""
    table = PerformanceTable()
    cfg = _cfg()
    table.record(cfg, local_won=False)
    assert table.win_rate(cfg) < 0.5


def test_multiple_records_cumulate():
    """Two wins and one loss gives win_rate = 2/3."""
    table = PerformanceTable()
    cfg = _cfg()
    table.record(cfg, local_won=True)
    table.record(cfg, local_won=True)
    table.record(cfg, local_won=False)
    assert abs(table.win_rate(cfg) - 2 / 3) < 1e-9


def test_best_config_returns_highest_win_rate():
    """best_config returns the candidate with the highest recorded win rate."""
    table = PerformanceTable()
    good = _cfg(grid_cols=6)
    bad = _cfg(grid_cols=8)
    table.record(good, local_won=True)
    table.record(bad, local_won=False)
    assert table.best_config([good, bad]) is good


def test_best_config_none_on_empty_list():
    """best_config returns None for an empty candidate list."""
    table = PerformanceTable()
    assert table.best_config([]) is None


def test_different_configs_tracked_separately():
    """Different config fingerprints are tracked independently."""
    table = PerformanceTable()
    small = _cfg(grid_cols=4, grid_rows=4)
    large = _cfg(grid_cols=10, grid_rows=10)
    table.record(small, local_won=True)
    assert table.win_rate(large) == 0.5  # no history for large
