"""Authentication endpoints: login, logout, current user.

Full implementation is part of Milestone 4. This module defines
the route stubs and schemas so the API surface is stable from day one.
"""

from fastapi import APIRouter, HTTPException, status

from cop_thief.api.deps import SessionDep, SettingsDep
from cop_thief.db.repositories import UserRepository
from cop_thief.schemas.api import LoginRequest, TokenResponse, UserResponse
from cop_thief.shared.security import create_access_token, verify_password

router = APIRouter()


@router.post("/auth/login", response_model=TokenResponse)
async def login(
    body: LoginRequest,
    session: SessionDep,
    settings: SettingsDep,
) -> TokenResponse:
    """Authenticate with username and password, return a JWT access token."""
    repo = UserRepository(session)
    user = await repo.get_by_username(body.username)
    if user is None or not verify_password(body.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password.",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled.",
        )
    token = create_access_token(user.username, settings.secret_key)
    return TokenResponse(access_token=token)


@router.post("/auth/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout() -> None:
    """Invalidate the current session.

    Client-side token deletion is sufficient for stateless JWT.
    Server-side revocation list is a future hardening step.
    """


@router.get("/me", response_model=UserResponse)
async def get_me() -> UserResponse:
    """Return the currently authenticated user's profile.

    Token verification and user injection are added in Milestone 4.
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Authentication middleware not yet implemented.",
    )
