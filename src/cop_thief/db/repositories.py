"""Repository layer: typed CRUD wrappers over SQLAlchemy sessions.

Routes and the SDK must use repositories — never query the ORM directly.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from cop_thief.constants import DEFAULT_PAGE_SIZE
from cop_thief.db.models.match import Match
from cop_thief.db.models.user import User


class MatchRepository:
    """CRUD operations for Match records."""

    def __init__(self, session: AsyncSession) -> None:
        """Bind this repository to *session*."""
        self._session = session

    async def get_by_public_id(self, public_id: str) -> Match | None:
        """Return the match with *public_id*, or None if not found."""
        result = await self._session.execute(
            select(Match).where(Match.public_id == public_id)
        )
        return result.scalar_one_or_none()

    async def list_matches(
        self,
        offset: int = 0,
        limit: int = DEFAULT_PAGE_SIZE,
    ) -> list[Match]:
        """Return a paginated list of matches ordered by creation date descending."""
        result = await self._session.execute(
            select(Match).order_by(Match.created_at.desc()).offset(offset).limit(limit)
        )
        return list(result.scalars().all())

    async def save(self, match: Match) -> Match:
        """Persist *match* (insert or update) and return it."""
        self._session.add(match)
        await self._session.commit()
        await self._session.refresh(match)
        return match


class UserRepository:
    """CRUD operations for User records."""

    def __init__(self, session: AsyncSession) -> None:
        """Bind this repository to *session*."""
        self._session = session

    async def get_by_username(self, username: str) -> User | None:
        """Return the user with *username*, or None if not found."""
        result = await self._session.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()

    async def save(self, user: User) -> User:
        """Persist *user* (insert or update) and return it."""
        self._session.add(user)
        await self._session.commit()
        await self._session.refresh(user)
        return user
