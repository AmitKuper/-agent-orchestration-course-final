"""GameConfig — all configurable game parameters with defaults.

Load from a dict (e.g. config/game_defaults.json) via GameConfig.from_dict().
No parameter may be hard-coded outside this module.
"""

from dataclasses import dataclass

from cop_thief.game_engine.errors import ConfigError

_VALID_OOB = {"stay", "invalid"}
_VALID_BARRIER_COLLISION = {"stay", "invalid"}
_VALID_BARRIER_SCOPE = {"adjacent_only", "current_and_adjacent"}
_VALID_START_MODE = {"random", "fixed"}
_VALID_MOVE_ORDER = {"thief_first", "cop_first", "alternating"}
_VALID_CRUMB_MODE = {"none", "thief_only", "cop_only", "both"}
_VALID_EXHAUST_POLICY = {"technical_invalid", "auto_forfeit"}


@dataclass
class GameConfig:
    """All configurable game parameters. All values come from config files."""

    grid_cols: int = 10
    grid_rows: int = 10
    num_games: int = 6
    max_moves: int = 25
    max_barriers: int = 5
    view_radius: int = 2
    partial_observation: bool = True
    stay_enabled: bool = True
    out_of_bounds_behavior: str = "stay"
    barrier_collision_behavior: str = "stay"
    barrier_placement_scope: str = "adjacent_only"
    starting_position_mode: str = "random"
    move_order: str = "thief_first"
    crumbtrail_mode: str = "none"
    crumbtrail_max_age: int = -1
    turn_timeout_seconds: int = 30
    max_illegal_retries: int = 2
    invalid_action_exhaustion_policy: str = "technical_invalid"
    timeout_policy: str = "technical_invalid"
    max_consecutive_technical_invalid: int = 3
    cop_win: int = 20
    thief_win: int = 10
    cop_loss: int = 5
    thief_loss: int = 5

    def validate(self) -> None:
        """Raise ConfigError if any parameter is out of specification."""
        if self.grid_cols < 2 or self.grid_rows < 2:
            raise ConfigError("grid must be at least 2×2")
        if self.max_moves < 1:
            raise ConfigError("max_moves must be >= 1")
        if self.max_barriers < 0:
            raise ConfigError("max_barriers must be >= 0")
        if self.view_radius < 1:
            raise ConfigError("view_radius must be >= 1")
        if self.out_of_bounds_behavior not in _VALID_OOB:
            raise ConfigError(f"out_of_bounds_behavior must be one of {_VALID_OOB}")
        if self.barrier_collision_behavior not in _VALID_BARRIER_COLLISION:
            raise ConfigError(f"barrier_collision_behavior must be one of {_VALID_BARRIER_COLLISION}")  # noqa: E501
        if self.barrier_placement_scope not in _VALID_BARRIER_SCOPE:
            raise ConfigError(f"barrier_placement_scope must be one of {_VALID_BARRIER_SCOPE}")
        if self.starting_position_mode not in _VALID_START_MODE:
            raise ConfigError(f"starting_position_mode must be one of {_VALID_START_MODE}")
        if self.move_order not in _VALID_MOVE_ORDER:
            raise ConfigError(f"move_order must be one of {_VALID_MOVE_ORDER}")
        if self.crumbtrail_mode not in _VALID_CRUMB_MODE:
            raise ConfigError(f"crumbtrail_mode must be one of {_VALID_CRUMB_MODE}")
        if self.invalid_action_exhaustion_policy not in _VALID_EXHAUST_POLICY:
            raise ConfigError(f"invalid_action_exhaustion_policy must be one of {_VALID_EXHAUST_POLICY}")  # noqa: E501

    @classmethod
    def from_dict(cls, d: dict) -> "GameConfig":
        """Build a GameConfig from a flat or nested config dict."""
        data: dict = dict(d)
        if "grid_size" in data:
            size = data.pop("grid_size")
            data["grid_cols"], data["grid_rows"] = size[0], size[1]
        scoring = data.pop("scoring", {})
        data["cop_win"] = scoring.get("cop_win", 20)
        data["thief_win"] = scoring.get("thief_win", 10)
        data["cop_loss"] = scoring.get("cop_loss", 5)
        data["thief_loss"] = scoring.get("thief_loss", 5)
        known = {k: v for k, v in data.items() if k in cls.__dataclass_fields__}
        cfg = cls(**known)
        cfg.validate()
        return cfg
