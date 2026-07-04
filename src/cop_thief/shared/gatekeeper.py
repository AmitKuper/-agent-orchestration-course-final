"""LLM API Gatekeeper — all LLM calls must go through this module.

Implements rate limiting, asyncio queuing, exponential backoff retry,
and per-call structured logging. Config is read from rate_limits.json.
"""

import asyncio
import json
import logging
import time
from pathlib import Path

import anthropic

from cop_thief.shared.errors import GatekeeperError, RateLimitError

logger = logging.getLogger(__name__)

_CONFIG_PATH = Path(__file__).parent.parent.parent.parent / "config" / "rate_limits.json"


def _load_llm_limits() -> dict:
    """Load LLM rate limit configuration."""
    with _CONFIG_PATH.open() as fh:
        return json.load(fh).get("llm", {})


class Gatekeeper:
    """Centralised LLM API proxy with rate limiting and retry.

    No agent or service may call the LLM API without going through
    an instance of this class.
    """

    def __init__(self, api_key: str, rate_limits: dict | None = None) -> None:
        """Initialise the gatekeeper.

        Args:
            api_key: Anthropic API key from environment.
            rate_limits: Override rate limits; loaded from config if None.
        """
        limits = rate_limits or _load_llm_limits()
        self._api_key = api_key
        self._rpm: int = limits.get("requests_per_minute", 60)
        self._max_retries: int = limits.get("max_retries", 3)
        self._base_delay: float = limits.get("retry_base_delay_seconds", 1.0)
        self._max_delay: float = limits.get("retry_max_delay_seconds", 30.0)
        self._queue: asyncio.Queue = asyncio.Queue(maxsize=100)
        self._call_times: list[float] = []
        self._client = anthropic.AsyncAnthropic(api_key=api_key)

    def _is_rate_limited(self) -> bool:
        """Return True if we've exceeded requests-per-minute."""
        now = time.monotonic()
        self._call_times = [t for t in self._call_times if now - t < 60]
        return len(self._call_times) >= self._rpm

    def _record_call(self) -> None:
        """Record the current timestamp for rate-limit tracking."""
        self._call_times.append(time.monotonic())

    async def complete(self, messages: list[dict], model: str, **kwargs) -> str:
        """Send a chat completion request through the gatekeeper.

        Enforces RPM rate limit and retries with exponential backoff.

        Args:
            messages: OpenAI-style message list (role/content dicts).
            model: Anthropic model identifier (e.g. ``"claude-haiku-4-5-20251001"``).
            **kwargs: Extra parameters forwarded to the Anthropic API.

        Returns:
            The assistant reply text.

        Raises:
            RateLimitError: If the RPM limit is exceeded before completion.
            GatekeeperError: If all retries are exhausted.
        """
        if self._is_rate_limited():
            raise RateLimitError("LLM request rate limit exceeded.")
        delay = self._base_delay
        for attempt in range(self._max_retries):
            try:
                self._record_call()
                system_msgs = [m for m in messages if m.get("role") == "system"]
                user_msgs = [m for m in messages if m.get("role") != "system"]
                system_text = system_msgs[0]["content"] if system_msgs else None
                api_kwargs: dict = {"model": model, "messages": user_msgs, "max_tokens": 1024}
                if system_text:
                    api_kwargs["system"] = system_text
                api_kwargs.update(kwargs)
                response = await self._client.messages.create(**api_kwargs)
                text = response.content[0].text if response.content else ""
                logger.info(
                    "LLM call success model=%s attempt=%d tokens=%s",
                    model, attempt + 1,
                    getattr(response.usage, "input_tokens", "?"),
                )
                return text
            except anthropic.RateLimitError as exc:
                logger.warning("Rate limit from API attempt=%d: %s", attempt + 1, exc)
            except anthropic.APIError as exc:
                logger.warning("API error attempt=%d: %s", attempt + 1, exc)
            if attempt < self._max_retries - 1:
                await asyncio.sleep(min(delay, self._max_delay))
                delay *= 2
        raise GatekeeperError(f"LLM call failed after {self._max_retries} attempts.")
