"""ORM model registry — import here to ensure all models are registered."""

from cop_thief.db.models.game_event import GameEvent
from cop_thief.db.models.match import Match
from cop_thief.db.models.sub_game import SubGame
from cop_thief.db.models.user import User

__all__ = ["User", "Match", "SubGame", "GameEvent"]
