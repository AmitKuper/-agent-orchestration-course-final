"""Unit tests for SelfPlayRunner and Trajectory."""

from cop_thief.actors.random_actor import RandomLegalActor
from cop_thief.actors.self_play_runner import SelfPlayRunner
from cop_thief.game_engine.config import GameConfig


def _runner() -> SelfPlayRunner:
    """Return a SelfPlayRunner with small config and random actors."""
    cfg = GameConfig.from_dict({"grid_cols": 4, "grid_rows": 4, "num_games": 6, "max_moves": 10})
    return SelfPlayRunner(RandomLegalActor(seed=0), RandomLegalActor(seed=1), cfg=cfg)


def test_run_episode_returns_two_trajectories():
    """run_episode returns two Trajectory objects (cop and thief)."""
    runner = _runner()
    cop_t, thief_t = runner.run_episode(seed=0)
    assert cop_t.role == "cop"
    assert thief_t.role == "thief"


def test_trajectories_are_non_empty():
    """Both trajectories have at least one step recorded."""
    runner = _runner()
    cop_t, thief_t = runner.run_episode(seed=7)
    assert len(cop_t) > 0
    assert len(thief_t) > 0


def test_trajectory_lists_same_length():
    """observations, action_masks, action_indices, and rewards are aligned."""
    runner = _runner()
    cop_t, _ = runner.run_episode(seed=3)
    assert len(cop_t.observations) == len(cop_t.action_masks)
    assert len(cop_t.observations) == len(cop_t.action_indices)
    assert len(cop_t.observations) == len(cop_t.rewards)


def test_terminal_rewards_opposite():
    """Cop terminal reward and thief terminal reward are always opposite in sign."""
    runner = _runner()
    cop_t, thief_t = runner.run_episode(seed=5)
    assert cop_t.terminal_reward == -thief_t.terminal_reward


def test_action_masks_are_binary():
    """All action mask entries are 0 or 1."""
    runner = _runner()
    cop_t, _ = runner.run_episode(seed=1)
    for mask in cop_t.action_masks:
        assert all(v in (0, 1) for v in mask)
