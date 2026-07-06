"""Admin-only endpoints for match management and failure inspection.

Routes
------
GET  /api/admin/technical-failures     — list voided/invalid matches
POST /api/admin/games/{public_id}/void — mark a match as technically invalid
"""

from fastapi import APIRouter, HTTPException, status

from cop_thief.api.deps import CurrentUserDep, SessionDep
from cop_thief.constants import ROLE_ADMIN
from cop_thief.db.models.user import User
from cop_thief.db.repositories import MatchRepository
from cop_thief.schemas.api import PaginatedResponse
from cop_thief.schemas.game import MatchDetail, MatchSummary
from cop_thief.shared.errors import NotFoundError

router = APIRouter()


def _require_admin(user: User) -> None:
    """Raise 403 if *user* is not an admin.

    Args:
        user: The currently authenticated user.

    Raises:
        HTTPException 403: When the user's role is not ROLE_ADMIN.
    """
    if user.role != ROLE_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin role required.",
        )


@router.get("/admin/technical-failures", response_model=PaginatedResponse)
async def list_technical_failures(
    current_user: CurrentUserDep,
    session: SessionDep,
) -> PaginatedResponse:
    """Return all matches marked as technically invalid, newest first.

    Requires admin role.
    """
    _require_admin(current_user)
    matches = await MatchRepository(session).list_technical_failures()
    items = [MatchSummary.model_validate(m) for m in matches]
    return PaginatedResponse(total=len(items), offset=0, limit=len(items), items=items)


@router.post("/admin/games/{public_id}/void", response_model=MatchDetail)
async def void_match(
    public_id: str,
    current_user: CurrentUserDep,
    session: SessionDep,
) -> MatchDetail:
    """Mark a match as technically invalid (void it).

    Requires admin role.
    """
    _require_admin(current_user)
    try:
        match = await MatchRepository(session).void_match(public_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return MatchDetail.model_validate(match)
