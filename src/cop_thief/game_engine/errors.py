"""Game-engine-specific errors."""

from cop_thief.shared.errors import CopThiefError


class ConfigError(CopThiefError):
    """Raised when the game configuration is invalid."""


class ActionOwnershipError(CopThiefError):
    """Raised when an actor submits an action out of turn."""


class EngineStateError(CopThiefError):
    """Raised when an operation is attempted on a finished sub-game."""
