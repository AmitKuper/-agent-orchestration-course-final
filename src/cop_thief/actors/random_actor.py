"""RandomLegalActor — selects a uniform random candidate action each turn."""

import random

from cop_thief.actors.base import Actor
from cop_thief.game_engine.actions import FORFEIT, MOVE, STAY, Action


def _parse_candidate(token: str) -> Action:
    """Convert a candidate-action token string into an ``Action``."""
    if token == "stay":
        return Action(type=STAY)
    if token == "forfeit":
        return Action(type=FORFEIT)
    return Action(type=MOVE, direction=token)


class RandomLegalActor(Actor):
    """Selects uniformly at random from the observation's candidate actions.

    This is the simplest valid actor and serves as a baseline and as a
    reliable action source for integration tests.  It never forfeits
    unless forfeit is the only remaining candidate.
    """

    def __init__(self, seed: int | None = None) -> None:
        """Initialise with an optional deterministic seed."""
        self._rng = random.Random(seed)

    def get_action(self, observation: dict) -> Action:
        """Return a uniformly random candidate action, avoiding forfeit if possible.

        Args:
            observation: Observation dict from ``GameEngine.get_observation``.

        Returns:
            A randomly chosen ``Action`` from the candidate list.

        Raises:
            ValueError: If ``candidate_actions`` is empty.
        """
        candidates: list[str] = observation.get("candidate_actions", [])
        if not candidates:
            raise ValueError("No candidate actions available in observation.")
        non_forfeit = [c for c in candidates if c != "forfeit"]
        chosen = self._rng.choice(non_forfeit if non_forfeit else candidates)
        return _parse_candidate(chosen)
