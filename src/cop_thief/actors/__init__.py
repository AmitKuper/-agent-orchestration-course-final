"""Actor package — all agent/bot implementations for cop and thief roles.

External callers must import from this package, not sub-modules directly.
"""

from cop_thief.actors.action_mask import build_action_mask
from cop_thief.actors.base import Actor
from cop_thief.actors.heuristic_actor import HeuristicActor
from cop_thief.actors.model_actor import ModelActor
from cop_thief.actors.model_bank import ModelBank, ModelMetadata
from cop_thief.actors.random_actor import RandomLegalActor

__all__ = [
    "Actor",
    "RandomLegalActor",
    "HeuristicActor",
    "ModelActor",
    "ModelBank",
    "ModelMetadata",
    "build_action_mask",
]
