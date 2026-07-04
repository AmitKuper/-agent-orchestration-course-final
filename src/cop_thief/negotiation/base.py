"""NegotiationStrategy — abstract base for pre-match config proposal logic."""

from abc import ABC, abstractmethod

from cop_thief.game_engine.config import GameConfig


class NegotiationStrategy(ABC):
    """Abstract base for all pre-match negotiation strategies.

    A strategy proposes a ``GameConfig`` to the opponent and evaluates
    their counter-proposal, either accepting or rejecting it.
    """

    @abstractmethod
    def propose(self) -> GameConfig:
        """Return the config this strategy wants to play under.

        Returns:
            A valid ``GameConfig`` to propose to the remote server.
        """

    @abstractmethod
    def evaluate(self, proposed: GameConfig) -> bool:
        """Decide whether to accept a config proposed by the remote server.

        Args:
            proposed: The ``GameConfig`` the opponent wants to use.

        Returns:
            True to accept, False to reject.
        """

    def on_result(self, config: GameConfig, local_won: bool) -> None:
        """Optionally record the outcome for adaptive strategies.

        Args:
            config: The config the completed match was played under.
            local_won: True if the local server won the match.
        """
