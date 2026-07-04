"""LLM API Gatekeeper.

All LLM API calls in the application must go through this module.
It enforces rate limits (from config/rate_limits.json), queues requests,
retries with exponential backoff, and logs every call.

This module is a stub in Milestone 1 — the full implementation
is built in Phase 6 (Built-In LLM Agent).
"""

import logging

from cop_thief.shared.errors import GatekeeperError

logger = logging.getLogger(__name__)


class Gatekeeper:
    """Centralised LLM API proxy with rate limiting and retry.

    No agent or service may call the LLM API without going through
    an instance of this class.
    """

    def __init__(self, api_key: str, rate_limits: dict) -> None:
        """Initialise the gatekeeper.

        Args:
            api_key: LLM provider API key from environment.
            rate_limits: Rate-limit configuration loaded from
                         config/rate_limits.json.
        """
        self._api_key = api_key
        self._rate_limits = rate_limits

    async def complete(self, messages: list[dict], model: str, **kwargs) -> str:
        """Send a chat completion request through the gatekeeper.

        Enforces rate limits and retries on transient errors.

        Args:
            messages: OpenAI-style message list.
            model: Model identifier string.
            **kwargs: Additional provider-specific parameters.

        Returns:
            The assistant reply text.

        Raises:
            GatekeeperError: If the request fails after all retries.
        """
        # Stub — full implementation in Phase 6
        raise GatekeeperError("Gatekeeper not yet implemented (Phase 6).")
