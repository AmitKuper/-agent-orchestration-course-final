"""ORM model for application users."""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from cop_thief.constants import ROLE_USER
from cop_thief.db.base import Base


class User(Base):
    """Authenticated user who can initiate and play games."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    display_name: Mapped[str] = mapped_column(String(128), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(256), nullable=False)
    role: Mapped[str] = mapped_column(String(16), nullable=False, default=ROLE_USER)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    def __repr__(self) -> str:
        """Return a concise string representation."""
        return f"<User id={self.id} username={self.username!r} role={self.role!r}>"
