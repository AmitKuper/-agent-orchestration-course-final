"""CommunicationAgent — top-level agent orchestrating LLM message flow.

Combines the MessageGenerator and MessageParser behind a single interface.
Used by the game orchestrator when generating inter-server MCP messages.
"""

from cop_thief.agents.hidden_state_filter import filter_observation
from cop_thief.agents.message_generator import MessageGenerator
from cop_thief.agents.message_parser import MessageParser
from cop_thief.game_engine.actions import Action
from cop_thief.shared.gatekeeper import Gatekeeper


class CommunicationAgent:
    """Manages LLM-generated turn messages for one game session.

    Generates outgoing messages after each actor decision and summarises
    incoming opponent messages to enrich the actor's context.
    """

    def __init__(self, gatekeeper: Gatekeeper, model: str | None = None) -> None:
        """Initialise with a shared Gatekeeper and optional model override.

        Args:
            gatekeeper: Shared LLM API proxy — all calls go through here.
            model: Optional model override; defaults to each sub-module's default.
        """
        kwargs: dict = {} if model is None else {"model": model}
        self._generator = MessageGenerator(gatekeeper, **kwargs)
        self._parser = MessageParser(gatekeeper, **kwargs)
        self._context: list[str] = []

    async def on_action_taken(self, observation: dict, action: Action) -> str:
        """Generate and record an outgoing turn message after *action* was applied.

        Args:
            observation: Game observation at the time of the action.
            action: The action the local actor took.

        Returns:
            The generated natural-language message to send to the opponent.
        """
        message = await self._generator.generate(observation, action)
        self._context.append(f"sent: {message}")
        return message

    async def on_message_received(self, message: str) -> str:
        """Parse an incoming opponent message and record a summary.

        Args:
            message: Raw natural-language message from the opponent.

        Returns:
            A concise summary of the opponent's message.
        """
        summary = await self._parser.summarise(message)
        self._context.append(f"received: {summary}")
        return summary

    def context_snapshot(self) -> list[str]:
        """Return a copy of the accumulated message context for debugging."""
        return list(self._context)

    def safe_observation(self, observation: dict) -> dict:
        """Return a filtered observation safe for embedding in LLM prompts."""
        return filter_observation(observation)
