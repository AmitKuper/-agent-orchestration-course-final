"""Unit tests for the MCP guest rate limiter."""


import pytest

from cop_thief.mcp import rate_limiter as rl


@pytest.fixture(autouse=True)
def _clear_state():
    """Reset rate limiter state between tests."""
    rl._game_history.clear()
    rl._active_counts.clear()
    yield
    rl._game_history.clear()
    rl._active_counts.clear()


def test_first_game_allowed():
    """A fresh IP has no rate limit and the first game is allowed."""
    result = rl.check_and_record_new_game("1.2.3.4")
    assert result is None


def test_second_game_allowed_within_limit():
    """A second game from the same IP is allowed when under concurrent limit."""
    rl.check_and_record_new_game("1.2.3.4")
    result = rl.check_and_record_new_game("1.2.3.4")
    assert result is None


def test_concurrent_limit_enforced():
    """Third concurrent game from same IP is rejected when max is 2."""
    orig = rl._MAX_CONCURRENT
    rl._MAX_CONCURRENT = 2
    rl.check_and_record_new_game("5.5.5.5")
    rl.check_and_record_new_game("5.5.5.5")
    result = rl.check_and_record_new_game("5.5.5.5")
    rl._MAX_CONCURRENT = orig
    assert result is not None
    assert "concurrent" in result.lower()


def test_release_decrements_counter():
    """release_game reduces the active game count, allowing new games."""
    orig = rl._MAX_CONCURRENT
    rl._MAX_CONCURRENT = 1
    rl.check_and_record_new_game("6.6.6.6")
    assert rl.check_and_record_new_game("6.6.6.6") is not None
    rl.release_game("6.6.6.6")
    assert rl.check_and_record_new_game("6.6.6.6") is None
    rl._MAX_CONCURRENT = orig


def test_different_ips_do_not_interfere():
    """Rate limits are tracked per IP — one IP's state does not affect another."""
    orig = rl._MAX_CONCURRENT
    rl._MAX_CONCURRENT = 1
    rl.check_and_record_new_game("10.0.0.1")
    result = rl.check_and_record_new_game("10.0.0.2")
    rl._MAX_CONCURRENT = orig
    assert result is None
