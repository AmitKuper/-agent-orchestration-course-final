"""FastAPI dependencies shared across route modules."""

from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from cop_thief.db.session import get_session
from cop_thief.webserver.config import Settings, get_settings


async def _session_dep(
    settings: Annotated[Settings, Depends(get_settings)],
) -> AsyncGenerator[AsyncSession, None]:
    """Yield a database session for the current request."""
    async for session in get_session(settings.database_url):
        yield session


SessionDep = Annotated[AsyncSession, Depends(_session_dep)]
SettingsDep = Annotated[Settings, Depends(get_settings)]
