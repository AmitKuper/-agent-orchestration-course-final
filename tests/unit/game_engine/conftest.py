"""Shared fixtures for game-engine unit tests."""

import pytest

from cop_thief.game_engine.config import GameConfig
from cop_thief.game_engine.engine import GameEngine
from cop_thief.game_engine.state import GameState


def make_cfg(**overrides) -> GameConfig:
    """Return a minimal 5×5 GameConfig with optional overrides."""
    defaults = dict(
        grid_cols=5,
        grid_rows=5,
        max_moves=10,
        max_barriers=3,
        partial_observation=False,
        stay_enabled=True,
        out_of_bounds_behavior="stay",
        barrier_collision_behavior="stay",
        barrier_placement_scope="adjacent_only",
        move_order="thief_first",
        crumbtrail_mode="none",
    )
    defaults.update(overrides)
    return GameConfig(**defaults)


def make_state(cfg: GameConfig, cop: tuple = (0, 0), thief: tuple = (4, 4)) -> GameState:
    """Return a GameState with given positions on the cfg grid."""
    return GameState(
        match_id="test",
        valid_subgame_index=1,
        replay_attempt_index=0,
        grid_cols=cfg.grid_cols,
        grid_rows=cfg.grid_rows,
        cop_player_id="a",
        thief_player_id="b",
        cop_position=cop,
        thief_position=thief,
        current_actor="thief",
    )


@pytest.fixture
def cfg() -> GameConfig:
    """Default 5×5 test config."""
    return make_cfg()


@pytest.fixture
def engine(cfg) -> GameEngine:
    """Default GameEngine bound to the 5×5 config."""
    return GameEngine(cfg)
