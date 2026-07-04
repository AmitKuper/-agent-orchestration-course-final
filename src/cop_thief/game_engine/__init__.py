"""Game engine — deterministic rules, state, and observation.

Public entry point: GameEngine (engine.py).
All other sub-modules are internal implementation details.
"""

from cop_thief.game_engine.actions import Action, ActionResult
from cop_thief.game_engine.config import GameConfig
from cop_thief.game_engine.engine import GameEngine
from cop_thief.game_engine.state import GameState

__all__ = ["GameEngine", "GameConfig", "GameState", "Action", "ActionResult"]
