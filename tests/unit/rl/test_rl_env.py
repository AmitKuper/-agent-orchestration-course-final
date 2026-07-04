"""Unit tests for the CopThiefEnv RL environment."""

import pytest

from cop_thief.actors.rl_env import CopThiefEnv


@pytest.fixture
def cop_env():
    """Return a CopThiefEnv configured for the cop role (small 4×4 grid)."""
    from cop_thief.game_engine.config import GameConfig  # noqa: PLC0415
    cfg = GameConfig.from_dict({"grid_cols": 4, "grid_rows": 4, "num_games": 6, "max_moves": 10})
    return CopThiefEnv(role="cop", cfg=cfg)


@pytest.fixture
def thief_env():
    """Return a CopThiefEnv configured for the thief role (small 4×4 grid)."""
    from cop_thief.game_engine.config import GameConfig  # noqa: PLC0415
    cfg = GameConfig.from_dict({"grid_cols": 4, "grid_rows": 4, "num_games": 6, "max_moves": 10})
    return CopThiefEnv(role="thief", cfg=cfg)


def test_reset_returns_observation(cop_env):
    """reset() returns a non-empty observation dict."""
    obs = cop_env.reset()
    assert isinstance(obs, dict)
    assert "own_position" in obs
    assert "candidate_actions" in obs


def test_action_space_size_is_ten(cop_env):
    """action_space_size returns 10 (8 dirs + stay + forfeit)."""
    assert cop_env.action_space_size == 10


def test_step_returns_valid_tuple(cop_env):
    """step() returns (obs, reward, done) with correct types."""
    cop_env.reset()
    obs, reward, done = cop_env.step(0)  # action 0 = North
    assert isinstance(obs, dict)
    assert isinstance(reward, float)
    assert isinstance(done, bool)


def test_step_reward_in_range(cop_env):
    """Reward is always -1, 0, or +1."""
    cop_env.reset()
    for _ in range(5):
        _, reward, done = cop_env.step(0)
        assert reward in (-1.0, 0.0, 1.0)
        if done:
            break


def test_episode_terminates(cop_env):
    """An episode eventually terminates."""
    cop_env.reset()
    done = False
    for _ in range(500):
        _, _, done = cop_env.step(0)
        if done:
            break
    assert done


def test_step_before_reset_raises():
    """step() without a preceding reset() raises RuntimeError."""
    env = CopThiefEnv(role="cop")
    with pytest.raises(RuntimeError, match="reset"):
        env.step(0)


def test_thief_env_observation_contains_actor(thief_env):
    """Observation actor field matches the configured role."""
    obs = thief_env.reset()
    assert obs["actor"] == "thief"
