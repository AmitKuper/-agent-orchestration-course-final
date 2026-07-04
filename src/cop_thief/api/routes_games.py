"""Game history, match detail, and authenticated game-action endpoints."""

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel

from cop_thief.actors.heuristic_actor import HeuristicActor
from cop_thief.api.deps import CurrentUserDep, SessionDep, SettingsDep
from cop_thief.constants import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE
from cop_thief.db.repositories import MatchRepository
from cop_thief.game.orchestrator import GameOrchestrator
from cop_thief.game_engine.config import GameConfig
from cop_thief.schemas.api import PaginatedResponse
from cop_thief.schemas.game import MatchDetail, MatchSummary
from cop_thief.shared.errors import NotFoundError, ValidationError

router = APIRouter()


def _default_orchestrator() -> GameOrchestrator:
    """Build an orchestrator with the default game config and heuristic bot."""
    cfg = GameConfig()
    return GameOrchestrator(cfg, HeuristicActor())


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


@router.post("/games/human-vs-server", status_code=status.HTTP_201_CREATED)
async def create_human_vs_server(
    current_user: CurrentUserDep,
    settings: SettingsDep,
    session: SessionDep,
) -> dict:
    """Create a new human-vs-server match and return the first observation."""
    orchestrator = _default_orchestrator()
    match, obs = await orchestrator.create_match(
        user_id=current_user.id,
        server_name=settings.server_name,
        session=session,
    )
    return {"match_id": match.public_id, "observation": obs}


@router.post("/games/{public_id}/human-action")
async def submit_human_action(
    public_id: str,
    body: HumanActionRequest,
    current_user: CurrentUserDep,  # noqa: ARG001
    session: SessionDep,
) -> dict:
    """Apply the authenticated user's action and return the updated observation."""
    orchestrator = _default_orchestrator()
    try:
        obs = await orchestrator.apply_human_action(
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
    return {"observation": obs}
