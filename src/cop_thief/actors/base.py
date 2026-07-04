"""Actor abstract base class — interface all actor implementations must satisfy."""

from abc import ABC, abstractmethod

from cop_thief.game_engine.actions import Action

# Canonical ordering of all possible action tokens used by action masks.
ALL_ACTION_TOKENS: list[str] = [
    "N", "NE", "E", "SE", "S", "SW", "W", "NW",
    "stay", "forfeit",
    # Barrier placement tokens use the format "barrier_C_R" and are appended
    # dynamically; they are not listed here because the grid size varies.
]


class Actor(ABC):
    """Abstract base for all cop-and-thief actors (bots, models, heuristics).

    Subclasses implement ``get_action`` to translate an observation dict into
    an ``Action``.  The observation dict is produced by ``GameEngine.get_observation``
    and is guaranteed to contain no hidden state.
    """

    @abstractmethod
    def get_action(self, observation: dict) -> Action:
        """Return an action for the current turn.

        Args:
            observation: The actor-scoped observation from ``GameEngine.get_observation``.

        Returns:
            An ``Action`` selected from ``observation["candidate_actions"]``
            (or a barrier placement, if the actor is the cop).
        """

    def role(self) -> str:
        """Return a short human-readable identifier for this actor type."""
        return self.__class__.__name__
