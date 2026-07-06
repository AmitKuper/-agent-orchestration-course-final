"""Game history, match detail, and authenticated game-action endpoints."""

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel

from cop_thief.actors.heuristic_actor import HeuristicActor
from cop_thief.api.deps import CurrentUserDep, SessionDep, SettingsDep
from cop_thief.api.ws_manager import manager as ws_manager
from cop_thief.constants import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE
from cop_thief.db.repositories import MatchRepository, SubGameRepository
from cop_thief.game.orchestrator import GameOrchestrator
from cop_thief.game_engine.config import GameConfig
from cop_thief.schemas.api import PaginatedResponse
from cop_thief.schemas.game import MatchDetail, MatchSummary, SubGameDetail
from cop_thief.shared.errors import NotFoundError, PermissionError, ValidationError

router = APIRouter()


def _default_orchestrator() -> GameOrchestrator:
    """Build an orchestrator with the default game config and heuristic bot."""
    return GameOrchestrator(GameConfig(), HeuristicActor())


class HumanActionRequest(BaseModel):
    """Request body for submitting a human action."""

    type: str
    direction: str | None = None
    target: list[int] | None = None


@router.get("/games", response_model=PaginatedResponse)
async def list_games(
    session: SessionDep,
    offset: int = Query(0, ge=0),
    limit: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE),
    public_only: bool = Query(False, description="When true, only return public matches."),
) -> PaginatedResponse:
    """Return a paginated list of matches, newest first.

    Publicly accessible — no authentication required.
    """
    repo = MatchRepository(session)
    matches = await repo.list_matches(offset=offset, limit=limit, public_only=public_only)
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


@router.post("/games/human-vs-server", status_code=status.HTTP_201_CREATED)
async def create_human_vs_server(
    current_user: CurrentUserDep,
    settings: SettingsDep,
    session: SessionDep,
) -> dict:
    """Create a new human-vs-server match and return the first observation."""
    match, obs = await _default_orchestrator().create_match(
        user_id=current_user.id,
        server_name=settings.server_name,
        session=session,
    )
    await ws_manager.broadcast(match.public_id, {"event": "state_update", "observation": obs})
    return {"match_id": match.public_id, "observation": obs}


@router.post("/games/{public_id}/human-action")
async def submit_human_action(
    public_id: str,
    body: HumanActionRequest,
    current_user: CurrentUserDep,  # noqa: ARG001
    session: SessionDep,
) -> dict:
    """Apply the authenticated user's action and return the updated observation."""
    try:
        obs = await _default_orchestrator().apply_human_action(
            public_id=public_id,
            action_dict=body.model_dump(exclude_none=True),
            session=session,
        )
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc
    await ws_manager.broadcast(public_id, {"event": "state_update", "observation": obs})
    return {"observation": obs}


@router.post("/games/{public_id}/cancel", response_model=MatchDetail)
async def cancel_game(
    public_id: str,
    current_user: CurrentUserDep,
    session: SessionDep,
) -> MatchDetail:
    """Cancel the authenticated user's own active match."""
    try:
        match = await MatchRepository(session).cancel_match(public_id, current_user.id)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return MatchDetail.model_validate(match)


@router.get("/games/{public_id}/subgames/{sg_index}", response_model=SubGameDetail)
async def get_subgame(
    public_id: str,
    sg_index: int,
    session: SessionDep,
) -> SubGameDetail:
    """Return a sub-game with its full replay event log."""
    match = await MatchRepository(session).get_by_public_id(public_id)
    if match is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match not found.")
    sub_games = await SubGameRepository(session).list_for_match(match.id)
    sg = next((s for s in sub_games if s.index == sg_index), None)
    if sg is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sub-game not found.")
    events = await SubGameRepository(session).get_events(sg.id)
    sg.events = events
    return SubGameDetail.model_validate(sg)
