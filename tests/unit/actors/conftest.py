"""Shared fixtures for actor unit tests."""

import pytest

from cop_thief.game_engine.config import GameConfig
from cop_thief.game_engine.engine import GameEngine
from cop_thief.game_engine.state import COP


def make_cfg(**overrides) -> GameConfig:
    """Return a small 5×5 config with optional overrides."""
    base = dict(
        grid_cols=5,
        grid_rows=5,
        max_moves=10,
        max_barriers=3,
        view_radius=5,
        partial_observation=False,
        stay_enabled=True,
        move_order="thief_first",
        crumbtrail_mode="none",
        out_of_bounds_behavior="stay",
        barrier_collision_behavior="stay",
    )
    base.update(overrides)
    return GameConfig.from_dict(base)


@pytest.fixture()
def full_obs_engine():
    """Return a GameEngine with full (non-partial) observation."""
    cfg = make_cfg()
    return GameEngine(cfg)


@pytest.fixture()
def cop_observation(full_obs_engine):
    """Return a cop observation from a fresh sub-game."""
    engine = full_obs_engine
    state = engine.initialize_subgame("m1", 1, "p_cop", "p_thief", random_seed=42)
    # Force cop to move first so we get a cop obs

    state.current_actor = COP
    return engine.get_observation(state, COP), state, engine


@pytest.fixture()
def thief_observation(full_obs_engine):
    """Return a thief observation from a fresh sub-game."""
    engine = full_obs_engine
    state = engine.initialize_subgame("m1", 1, "p_cop", "p_thief", random_seed=42)
    state.current_actor = "thief"
    return engine.get_observation(state, "thief"), state, engine
