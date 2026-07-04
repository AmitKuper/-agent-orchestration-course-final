"""ORM model for a single sub-game within a match."""

from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from cop_thief.db.base import Base


class SubGame(Base):
    """One round of a match where Cop and Thief roles may be swapped."""

    __tablename__ = "sub_games"

    id: Mapped[int] = mapped_column(primary_key=True)
    match_id: Mapped[int] = mapped_column(ForeignKey("matches.id"), nullable=False, index=True)
    index: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    local_role: Mapped[str] = mapped_column(String(8), nullable=False)
    opponent_role: Mapped[str] = mapped_column(String(8), nullable=False)
    winner_role: Mapped[str | None] = mapped_column(String(8), nullable=True)
    winner_side: Mapped[str | None] = mapped_column(String(16), nullable=True)
    win_reason: Mapped[str | None] = mapped_column(String(32), nullable=True)
    thief_actions: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    turn_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    barriers_used: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    initial_state_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    current_state_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    final_state_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    match: Mapped["Match"] = relationship(back_populates="sub_games")  # noqa: F821
    events: Mapped[list["GameEvent"]] = relationship(  # noqa: F821
        back_populates="sub_game", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        """Return a concise string representation."""
        return f"<SubGame id={self.id} match_id={self.match_id} index={self.index}>"
