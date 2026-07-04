"""ORM model for a single game event / action within a sub-game."""

from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cop_thief.db.base import Base


class GameEvent(Base):
    """Immutable record of one action and its outcome within a sub-game.

    Every submitted action, accepted result, and state transition is
    stored here. The sequence of GameEvents is the canonical replay log.
    """

    __tablename__ = "game_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    match_id: Mapped[int] = mapped_column(ForeignKey("matches.id"), nullable=False, index=True)
    sub_game_id: Mapped[int] = mapped_column(
        ForeignKey("sub_games.id"), nullable=False, index=True
    )
    turn_index: Mapped[int] = mapped_column(Integer, nullable=False)
    actor_role: Mapped[str] = mapped_column(String(8), nullable=False)
    actor_side: Mapped[str] = mapped_column(String(16), nullable=False)
    message_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    action_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    result: Mapped[str] = mapped_column(String(32), nullable=False)
    state_before_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    state_after_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    state_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    sub_game: Mapped["SubGame"] = relationship(back_populates="events")  # noqa: F821

    def __repr__(self) -> str:
        """Return a concise string representation."""
        return (
            f"<GameEvent id={self.id} sub_game_id={self.sub_game_id}"
            f" turn={self.turn_index} actor={self.actor_role!r}>"
        )
