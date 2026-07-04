"""HeuristicActor — simple rule-based actor for cop and thief roles.

Cop strategy: move toward the thief's last known position (or random if hidden).
Thief strategy: move away from the cop's last known position (or random if hidden).
Falls back to RandomLegalActor when the opponent is not visible.
"""

import random

from cop_thief.actors.base import Actor
from cop_thief.actors.random_actor import RandomLegalActor, _parse_candidate
from cop_thief.game_engine.actions import Action
from cop_thief.game_engine.coordinates import DIRECTIONS, apply_direction


def _chebyshev(a: list[int], b: list[int]) -> int:
    """Chebyshev distance between two [col, row] positions."""
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))


def _best_cop_direction(
    own: list[int], target: list[int], candidates: list[str], rng: random.Random
) -> str:
    """Return the candidate direction that minimises distance to *target*."""
    move_candidates = [c for c in candidates if c in DIRECTIONS]
    if not move_candidates:
        return rng.choice([c for c in candidates if c != "forfeit"] or candidates)
    best = min(move_candidates, key=lambda d: _chebyshev(apply_direction(tuple(own), d), target))
    return best


def _best_thief_direction(
    own: list[int], threat: list[int], candidates: list[str], rng: random.Random
) -> str:
    """Return the candidate direction that maximises distance from *threat*."""
    move_candidates = [c for c in candidates if c in DIRECTIONS]
    if not move_candidates:
        return rng.choice([c for c in candidates if c != "forfeit"] or candidates)
    best = max(move_candidates, key=lambda d: _chebyshev(apply_direction(tuple(own), d), threat))
    return best


class HeuristicActor(Actor):
    """Greedy single-step heuristic for either role.

    - Cop: closes Chebyshev distance to visible thief; random otherwise.
    - Thief: maximises Chebyshev distance from visible cop; random otherwise.

    The actor never deliberately forfeits unless no other candidates exist.
    """

    def __init__(self, seed: int | None = None) -> None:
        """Initialise with an optional deterministic seed."""
        self._rng = random.Random(seed)
        self._fallback = RandomLegalActor(seed=seed)

    def get_action(self, observation: dict) -> Action:
        """Return a heuristic action based on visible opponent position.

        Args:
            observation: Observation dict from ``GameEngine.get_observation``.

        Returns:
            A move ``Action`` based on greedy distance heuristic,
            or a random action when the opponent is not visible.
        """
        candidates: list[str] = observation.get("candidate_actions", [])
        if not candidates:
            raise ValueError("No candidate actions available in observation.")

        actor: str = observation["actor"]
        own: list[int] = observation["own_position"]
        opp: list[int] | None = observation.get("opponent_position")

        if opp is None:
            return self._fallback.get_action(observation)

        if actor == "cop":
            token = _best_cop_direction(own, opp, candidates, self._rng)
        else:
            token = _best_thief_direction(own, opp, candidates, self._rng)

        return _parse_candidate(token)
