"""Unit tests for HeuristicActor."""

from cop_thief.actors.heuristic_actor import HeuristicActor
from cop_thief.game_engine.actions import MOVE, STAY


def _obs(actor: str, own: list, opp: list | None, candidates: list[str]) -> dict:
    """Build a minimal observation dict for heuristic tests."""
    return {
        "actor": actor,
        "own_position": own,
        "opponent_position": opp,
        "candidate_actions": candidates,
    }


def test_cop_moves_toward_thief():
    """Cop heuristic picks the direction that closes distance to thief."""
    # Thief is directly East at (4,2), cop at (2,2). E should be chosen.
    actor = HeuristicActor(seed=0)
    obs = _obs("cop", [2, 2], [4, 2], ["N", "E", "S", "W", "stay", "forfeit"])
    action = actor.get_action(obs)
    assert action.type == MOVE
    assert action.direction == "E"


def test_thief_moves_away_from_cop():
    """Thief heuristic picks the direction that maximises distance from cop."""
    # Cop is at (0, 2), thief at (2, 2). Best escape is East = (3,2) or similar.
    actor = HeuristicActor(seed=0)
    obs = _obs("thief", [2, 2], [0, 2], ["N", "E", "S", "W", "stay", "forfeit"])
    action = actor.get_action(obs)
    assert action.type == MOVE
    assert action.direction == "E"


def test_heuristic_falls_back_to_random_when_opponent_hidden():
    """Heuristic delegates to RandomLegalActor when opponent is not visible."""
    actor = HeuristicActor(seed=42)
    obs = _obs("thief", [2, 2], None, ["N", "E", "stay", "forfeit"])
    action = actor.get_action(obs)
    assert action.type in (MOVE, STAY)


def test_heuristic_returns_candidate_action(cop_observation):
    """Heuristic must return an action whose token is in the candidate list."""
    obs, _state, _engine = cop_observation
    actor = HeuristicActor(seed=1)
    action = actor.get_action(obs)
    direction_or_type = action.direction if action.direction else action.type
    candidates = obs["candidate_actions"]
    # Either the direction string is a candidate, or the type resolves to stay/forfeit
    assert direction_or_type in candidates or action.type in ("stay", "forfeit")


def test_heuristic_never_selects_direction_not_in_candidates():
    """Heuristic must never return a direction absent from candidate_actions."""
    actor = HeuristicActor(seed=5)
    # Only N and W are available move candidates
    obs = _obs("cop", [2, 2], [1, 4], ["N", "W", "stay", "forfeit"])
    for _ in range(10):
        action = actor.get_action(obs)
        if action.type == MOVE:
            assert action.direction in ("N", "W")
