"""Repository layer: typed CRUD wrappers over SQLAlchemy sessions.

Routes and the SDK must use repositories — never query the ORM directly.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from cop_thief.constants import (
    DEFAULT_PAGE_SIZE,
    STATUS_CANCELLED,
    STATUS_LIVE,
    STATUS_TECHNICAL_INVALID,
)
from cop_thief.db.models.game_event import GameEvent
from cop_thief.db.models.match import Match
from cop_thief.db.models.sub_game import SubGame
from cop_thief.db.models.user import User
from cop_thief.shared.errors import NotFoundError, PermissionError


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
        public_only: bool = False,
    ) -> list[Match]:
        """Return a paginated list of matches ordered by creation date descending.

        Args:
            offset: Number of rows to skip.
            limit: Maximum rows to return.
            public_only: When True, exclude non-public matches.
        """
        q = select(Match).order_by(Match.created_at.desc()).offset(offset).limit(limit)
        if public_only:
            q = q.where(Match.is_public.is_(True))
        result = await self._session.execute(q)
        return list(result.scalars().all())

    async def list_technical_failures(self) -> list[Match]:
        """Return all matches with STATUS_TECHNICAL_INVALID, newest first."""
        result = await self._session.execute(
            select(Match)
            .where(Match.status == STATUS_TECHNICAL_INVALID)
            .order_by(Match.created_at.desc())
        )
        return list(result.scalars().all())

    async def cancel_match(self, public_id: str, user_id: int) -> Match:
        """Set a live match to cancelled, verifying ownership.

        Args:
            public_id: Public identifier of the match to cancel.
            user_id: ID of the requesting user (must be the initiator).

        Raises:
            NotFoundError: Match not found.
            PermissionError: Caller is not the match initiator.
            ValueError: Match is not in a cancellable state.
        """
        match = await self.get_by_public_id(public_id)
        if match is None:
            raise NotFoundError(f"Match {public_id!r} not found.")
        if match.initiator_user_id != user_id:
            raise PermissionError("Only the match initiator may cancel this game.")
        if match.status != STATUS_LIVE:
            raise ValueError(f"Match is {match.status!r}, only live matches can be cancelled.")
        match.status = STATUS_CANCELLED
        return await self.save(match)

    async def void_match(self, public_id: str) -> Match:
        """Mark a match as technically invalid (admin action).

        Args:
            public_id: Public identifier of the match to void.

        Raises:
            NotFoundError: Match not found.
        """
        match = await self.get_by_public_id(public_id)
        if match is None:
            raise NotFoundError(f"Match {public_id!r} not found.")
        match.status = STATUS_TECHNICAL_INVALID
        return await self.save(match)

    async def save(self, match: Match) -> Match:
        """Persist *match* (insert or update) and return it."""
        self._session.add(match)
        await self._session.commit()
        await self._session.refresh(match)
        return match


class SubGameRepository:
    """CRUD operations for SubGame and GameEvent records."""

    def __init__(self, session: AsyncSession) -> None:
        """Bind this repository to *session*."""
        self._session = session

    async def list_for_match(self, match_id: int) -> list[SubGame]:
        """Return all sub-games for *match_id* ordered by index."""
        result = await self._session.execute(
            select(SubGame)
            .where(SubGame.match_id == match_id)
            .order_by(SubGame.index)
        )
        return list(result.scalars().all())

    async def get_events(self, sub_game_id: int) -> list[GameEvent]:
        """Return all events for *sub_game_id* ordered by turn index."""
        result = await self._session.execute(
            select(GameEvent)
            .where(GameEvent.sub_game_id == sub_game_id)
            .order_by(GameEvent.turn_index)
        )
        return list(result.scalars().all())


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
