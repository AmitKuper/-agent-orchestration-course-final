"""Public game history and match detail endpoints."""

from fastapi import APIRouter, HTTPException, Query, status

from cop_thief.api.deps import SessionDep
from cop_thief.constants import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE
from cop_thief.db.repositories import MatchRepository
from cop_thief.schemas.api import PaginatedResponse
from cop_thief.schemas.game import MatchDetail, MatchSummary

router = APIRouter()


@router.get("/games", response_model=PaginatedResponse)
async def list_games(
    session: SessionDep,
    offset: int = Query(0, ge=0),
    limit: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE),
) -> PaginatedResponse:
    """Return a paginated list of matches, newest first.

    Publicly accessible — no authentication required.
    """
    repo = MatchRepository(session)
    matches = await repo.list_matches(offset=offset, limit=limit)
    items = [MatchSummary.model_validate(m) for m in matches]
    return PaginatedResponse(total=len(items), offset=offset, limit=limit, items=items)


@router.get("/games/{public_id}", response_model=MatchDetail)
async def get_game(public_id: str, session: SessionDep) -> MatchDetail:
    """Return full match details including sub-game list.

    Publicly accessible — no authentication required.
    """
    repo = MatchRepository(session)
    match = await repo.get_by_public_id(public_id)
    if match is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match not found.")
    return MatchDetail.model_validate(match)
