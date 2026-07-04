"""Unit tests for RuleBasedNegotiator."""

from cop_thief.game_engine.config import GameConfig
from cop_thief.negotiation.rule_based import RuleBasedNegotiator


def test_propose_returns_valid_config():
    """propose() must return a config that passes validate()."""
    negotiator = RuleBasedNegotiator()
    cfg = negotiator.propose()
    cfg.validate()  # must not raise


def test_evaluate_accepts_reasonable_proposal():
    """evaluate() accepts a proposal with normal grid and move parameters."""
    negotiator = RuleBasedNegotiator()
    reasonable = GameConfig(
        grid_cols=8, grid_rows=8, max_moves=20, max_barriers=5, num_games=6
    )
    assert negotiator.evaluate(reasonable) is True


def test_evaluate_rejects_tiny_grid():
    """evaluate() rejects a grid smaller than the minimum."""
    negotiator = RuleBasedNegotiator()
    tiny = GameConfig(grid_cols=2, grid_rows=2, max_moves=10, max_barriers=0, num_games=6)
    assert negotiator.evaluate(tiny) is False


def test_evaluate_rejects_too_many_barriers():
    """evaluate() rejects proposals with excessive max_barriers."""
    negotiator = RuleBasedNegotiator()
    heavy = GameConfig(
        grid_cols=8, grid_rows=8, max_moves=20, max_barriers=15, num_games=6
    )
    assert negotiator.evaluate(heavy) is False


def test_evaluate_rejects_too_few_moves():
    """evaluate() rejects proposals where max_moves is below the minimum."""
    negotiator = RuleBasedNegotiator()
    short = GameConfig(
        grid_cols=8, grid_rows=8, max_moves=5, max_barriers=3, num_games=6
    )
    assert negotiator.evaluate(short) is False


def test_on_result_does_not_raise_without_table():
    """on_result() is a no-op when no PerformanceTable is attached."""
    negotiator = RuleBasedNegotiator()
    cfg = negotiator.propose()
    negotiator.on_result(cfg, local_won=True)  # must not raise
