"""Message generator — converts an actor decision into a natural-language turn message.

The generated message is sent to the opponent over MCP to provide context.
The prompt template is loaded from ``prompts/game_turn_message.md``.
"""

import json
from pathlib import Path

from cop_thief.agents.hidden_state_filter import filter_observation
from cop_thief.game_engine.actions import Action
from cop_thief.shared.gatekeeper import Gatekeeper

_PROMPT_PATH = Path(__file__).parent / "prompts" / "game_turn_message.md"
_DEFAULT_MODEL = "claude-haiku-4-5-20251001"


def _load_template() -> str:
    """Load the turn-message prompt template from disk."""
    if _PROMPT_PATH.exists():
        return _PROMPT_PATH.read_text(encoding="utf-8")
    return (
        "You are playing a Cop and Thief pursuit game as {actor}.\n"
        "Current observation: {observation}\n"
        "You chose action: {action}\n"
        "Write a brief, in-character game message (1-2 sentences) describing your move."
    )


class MessageGenerator:
    """Generates natural-language turn messages via the Gatekeeper."""

    def __init__(self, gatekeeper: Gatekeeper, model: str = _DEFAULT_MODEL) -> None:
        """Bind the generator to a Gatekeeper instance.

        Args:
            gatekeeper: The shared LLM API proxy.
            model: Anthropic model ID to use for generation.
        """
        self._gk = gatekeeper
        self._model = model
        self._template = _load_template()

    async def generate(self, observation: dict, action: Action) -> str:
        """Generate a turn message for *action* taken from *observation*.

        The observation is filtered to remove hidden state before being
        embedded in the prompt.

        Args:
            observation: Raw observation dict from the game engine.
            action: The action the actor chose.

        Returns:
            A natural-language string describing the move.
        """
        safe_obs = filter_observation(observation)
        action_str = json.dumps(
            {"type": action.type, "direction": action.direction, "target": action.target}
        )
        prompt = self._template.format(
            actor=observation.get("actor", "unknown"),
            observation=json.dumps(safe_obs, indent=2),
            action=action_str,
        )
        messages = [{"role": "user", "content": prompt}]
        return await self._gk.complete(messages, model=self._model)
