"""Unit tests for observation filtering — hidden state must not leak."""

from cop_thief.game_engine.engine import GameEngine
from tests.unit.game_engine.conftest import make_cfg, make_state


def test_full_observation_shows_opponent():
    """Under full observation, opponent position is always visible."""
    cfg = make_cfg(partial_observation=False)
    state = make_state(cfg, cop=(0, 0), thief=(4, 4))
    eng = GameEngine(cfg)
    obs = eng.get_observation(state, "thief")
    assert obs["opponent_visible"] is True
    assert obs["opponent_position"] == [0, 0]


def test_partial_observation_hides_distant_opponent():
    """Under partial observation, far opponent position returns None."""
    cfg = make_cfg(partial_observation=True, view_radius=1)
    state = make_state(cfg, cop=(0, 0), thief=(4, 4))
    eng = GameEngine(cfg)
    obs = eng.get_observation(state, "thief")
    assert obs["opponent_visible"] is False
    assert obs["opponent_position"] is None


def test_partial_observation_shows_near_opponent():
    """Under partial observation, nearby opponent is visible."""
    cfg = make_cfg(partial_observation=True, view_radius=2)
    state = make_state(cfg, cop=(2, 2), thief=(3, 3))
    eng = GameEngine(cfg)
    obs = eng.get_observation(state, "thief")
    assert obs["opponent_visible"] is True
    assert obs["opponent_position"] == [2, 2]


def test_partial_observation_hides_distant_barrier():
    """Under partial observation, barriers outside view_radius are hidden."""
    cfg = make_cfg(partial_observation=True, view_radius=1)
    state = make_state(cfg, cop=(0, 0), thief=(4, 4))
    state.barriers.add((0, 1))  # close to cop, far from thief
    eng = GameEngine(cfg)
    obs = eng.get_observation(state, "thief")
    assert [0, 1] not in obs["visible_barriers"]


def test_partial_observation_shows_near_barrier():
    """Under partial observation, barriers inside view_radius are visible."""
    cfg = make_cfg(partial_observation=True, view_radius=1)
    state = make_state(cfg, cop=(0, 0), thief=(4, 4))
    state.barriers.add((4, 3))  # adjacent to thief
    eng = GameEngine(cfg)
    obs = eng.get_observation(state, "thief")
    assert [4, 3] in obs["visible_barriers"]


def test_candidate_actions_exclude_visible_barriers():
    """Candidate actions under full observation exclude blocked cells."""
    cfg = make_cfg(partial_observation=False)
    state = make_state(cfg, cop=(0, 0), thief=(2, 2))
    state.barriers.add((2, 3))
    eng = GameEngine(cfg)
    obs = eng.get_observation(state, "thief")
    assert "N" not in obs["candidate_actions"]


def test_candidate_actions_include_hidden_barrier_direction():
    """Under partial obs, candidate actions include direction toward hidden barrier."""
    cfg = make_cfg(partial_observation=True, view_radius=1)
    state = make_state(cfg, cop=(0, 0), thief=(2, 2))
    state.barriers.add((2, 4))  # 2 cells north, beyond radius 1
    eng = GameEngine(cfg)
    obs = eng.get_observation(state, "thief")
    # N is 2 steps away from barrier but only 1 step from thief — within radius
    # barrier at (2,4) is 2 away from thief at (2,2), so hidden
    assert "N" in obs["candidate_actions"]


def test_hashing_deterministic():
    """Same state produces same hash; different positions produce different hashes."""
    from cop_thief.game_engine.hashing import compute_state_hash
    cfg = make_cfg()
    s1 = make_state(cfg, cop=(0, 0), thief=(4, 4))
    s2 = make_state(cfg, cop=(0, 0), thief=(4, 4))
    s3 = make_state(cfg, cop=(1, 0), thief=(4, 4))
    assert compute_state_hash(s1) == compute_state_hash(s2)
    assert compute_state_hash(s1) != compute_state_hash(s3)
