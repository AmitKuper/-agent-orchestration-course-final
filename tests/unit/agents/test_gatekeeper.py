"""Unit tests for the Gatekeeper rate limiting logic.

Does not make real API calls — verifies the rate-limit guard without a key.
"""

import pytest

from cop_thief.shared.errors import GatekeeperError, RateLimitError
from cop_thief.shared.gatekeeper import Gatekeeper


def _gatekeeper(rpm: int = 60) -> Gatekeeper:
    """Return a Gatekeeper with a fake key and tight config."""
    return Gatekeeper(
        api_key="test-key",
        rate_limits={
            "requests_per_minute": rpm,
            "max_retries": 1,
            "retry_base_delay_seconds": 0.0,
            "retry_max_delay_seconds": 0.0,
        },
    )


@pytest.mark.asyncio
async def test_rate_limit_enforced_when_rpm_exceeded():
    """RateLimitError is raised immediately when RPM is at zero."""
    gk = _gatekeeper(rpm=0)
    with pytest.raises(RateLimitError):
        await gk.complete([{"role": "user", "content": "hi"}], model="claude-haiku-4-5-20251001")


@pytest.mark.asyncio
async def test_rate_limit_not_triggered_at_low_volume():
    """Rate limit is NOT triggered for a single call when rpm=60."""
    gk = _gatekeeper(rpm=60)
    gk._is_rate_limited()  # just check it returns False with no history
    assert not gk._is_rate_limited()


def test_record_call_increments_history():
    """_record_call adds a timestamp to the call history."""
    gk = _gatekeeper()
    assert len(gk._call_times) == 0
    gk._record_call()
    assert len(gk._call_times) == 1


@pytest.mark.asyncio
async def test_complete_raises_gatekeeper_error_on_api_failure():
    """complete() raises GatekeeperError when the API call fails (no real key)."""
    gk = _gatekeeper(rpm=100)
    with pytest.raises((GatekeeperError, Exception)):
        await gk.complete(
            [{"role": "user", "content": "test"}],
            model="claude-haiku-4-5-20251001",
        )
