"""ORM model for a match (one game session between two participants)."""

from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cop_thief.constants import STATUS_LIVE
from cop_thief.db.base import Base


class Match(Base):
    """Top-level match record covering one or more sub-games."""

    __tablename__ = "matches"

    id: Mapped[int] = mapped_column(primary_key=True)
    public_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    mode: Mapped[str] = mapped_column(String(32), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default=STATUS_LIVE)
    local_server_name: Mapped[str] = mapped_column(String(128), nullable=False)
    opponent_name: Mapped[str] = mapped_column(String(128), nullable=False)
    initiator_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    rules_version: Mapped[str] = mapped_column(String(16), nullable=False, default="1.0")
    config_json: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    local_score: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    opponent_score: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    result_for_local_server: Mapped[str | None] = mapped_column(String(16), nullable=True)
    valid_subgame_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    sub_games: Mapped[list["SubGame"]] = relationship(  # noqa: F821
        back_populates="match", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        """Return a concise string representation."""
        return f"<Match id={self.id} public_id={self.public_id!r} status={self.status!r}>"
