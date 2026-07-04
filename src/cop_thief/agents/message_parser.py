"""Message parser — summarises opponent natural-language messages for context.

Parses and distils incoming MCP messages from the opponent to extract
any strategically useful (but not rule-breaking) information.
"""

from cop_thief.shared.gatekeeper import Gatekeeper

_DEFAULT_MODEL = "claude-haiku-4-5-20251001"
_MAX_SUMMARY_LEN = 200


class MessageParser:
    """Summarises opponent messages via the Gatekeeper."""

    def __init__(self, gatekeeper: Gatekeeper, model: str = _DEFAULT_MODEL) -> None:
        """Bind the parser to a Gatekeeper instance.

        Args:
            gatekeeper: The shared LLM API proxy.
            model: Anthropic model ID to use for summarisation.
        """
        self._gk = gatekeeper
        self._model = model

    async def summarise(self, message: str) -> str:
        """Summarise *message* to extract strategic context.

        Args:
            message: Raw natural-language message from the opponent.

        Returns:
            A concise summary (≤ ``_MAX_SUMMARY_LEN`` chars) of the message.
        """
        prompt = (
            f"Opponent game message: {message!r}\n\n"
            f"Summarise in at most {_MAX_SUMMARY_LEN} characters what the opponent "
            "revealed or hinted at. Focus on position, intention, or strategy."
        )
        messages = [{"role": "user", "content": prompt}]
        summary = await self._gk.complete(messages, model=self._model)
        return summary[:_MAX_SUMMARY_LEN]
