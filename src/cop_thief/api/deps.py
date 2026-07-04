"""FastAPI dependencies shared across route modules."""

from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from cop_thief.db.models.user import User
from cop_thief.db.repositories import UserRepository
from cop_thief.db.session import get_session
from cop_thief.shared.security import decode_access_token
from cop_thief.webserver.config import Settings, get_settings

_bearer = HTTPBearer(auto_error=True)


async def _session_dep(
    settings: Annotated[Settings, Depends(get_settings)],
) -> AsyncGenerator[AsyncSession, None]:
    """Yield a database session for the current request."""
    async for session in get_session(settings.database_url):
        yield session


async def _current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(_bearer)],
    session: Annotated[AsyncSession, Depends(_session_dep)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> User:
    """Decode the Bearer token and return the authenticated user.

    Raises:
        HTTPException 401: If the token is invalid or the user is not found.
        HTTPException 403: If the account is disabled.
    """
    payload = decode_access_token(credentials.credentials, settings.secret_key)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token."
        )
    username: str = payload.get("sub", "")
    user = await UserRepository(session).get_by_username(username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found."
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Account is disabled."
        )
    return user


SessionDep = Annotated[AsyncSession, Depends(_session_dep)]
SettingsDep = Annotated[Settings, Depends(get_settings)]
CurrentUserDep = Annotated[User, Depends(_current_user)]
