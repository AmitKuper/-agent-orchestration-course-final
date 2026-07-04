"""MCP tool implementations — handlers for each supported tool name.

Each handler receives validated params and a DB session, and returns a
plain dict that is placed in the ``result`` field of the MCP response.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from cop_thief.actors.heuristic_actor import HeuristicActor
from cop_thief.db.repositories import MatchRepository
from cop_thief.game.orchestrator import GameOrchestrator, _active_subgame
from cop_thief.game.state_serializer import state_from_dict
from cop_thief.game_engine.config import GameConfig
from cop_thief.mcp.rate_limiter import check_and_record_new_game
from cop_thief.mcp.schemas import (
    GetGameStatusParams,
    GetHistoryParams,
    GetObservationParams,
    StartGameParams,
    SubmitActionParams,
)
from cop_thief.shared.errors import NotFoundError, ValidationError
from cop_thief.shared.version import RULES_VERSION

_SUPPORTED_TOOLS = [
    "list_supported_rules",
    "start_game_vs_server",
    "get_observation",
    "submit_action",
    "get_game_status",
    "get_game_history",
]


def _orchestrator() -> GameOrchestrator:
    """Return a default orchestrator with heuristic bot."""
    return GameOrchestrator(GameConfig(), HeuristicActor())


async def handle_list_supported_rules(_params: dict, _session: AsyncSession) -> dict:
    """Return the server's supported rules version and tool list."""
    return {"rules_version": RULES_VERSION, "supported_tools": _SUPPORTED_TOOLS}


async def handle_start_game(
    params: dict, session: AsyncSession, client_ip: str
) -> dict:
    """Create a new guest-vs-server game (rate-limited)."""
    rejection = check_and_record_new_game(client_ip)
    if rejection:
        raise ValidationError(rejection)
    p = StartGameParams(**params)
    orchestrator = _orchestrator()
    match, obs = await orchestrator.create_match(
        user_id=None, server_name="local", session=session
    )
    return {"match_id": match.public_id, "client_id": p.client_id, "observation": obs}


async def handle_get_observation(params: dict, session: AsyncSession) -> dict:
    """Return the caller-scoped observation for an active game."""
    p = GetObservationParams(**params)
    repo = MatchRepository(session)
    match = await repo.get_by_public_id(p.match_id)
    if match is None:
        raise NotFoundError(f"Match '{p.match_id}' not found.")
    sub_game = await _active_subgame(match, session)
    if sub_game is None or sub_game.current_state_json is None:
        raise ValidationError("No active sub-game.")
    from cop_thief.game_engine.engine import GameEngine  # noqa: PLC0415
    engine = GameEngine(GameConfig())
    state = state_from_dict(sub_game.current_state_json)
    obs = engine.get_observation(state, sub_game.local_role)
    return {"observation": obs}


async def handle_submit_action(params: dict, session: AsyncSession) -> dict:
    """Apply the caller's action and return the updated observation."""
    p = SubmitActionParams(**params)
    orchestrator = _orchestrator()
    obs = await orchestrator.apply_human_action(p.match_id, p.action, session)
    return {"observation": obs}


async def handle_get_game_status(params: dict, session: AsyncSession) -> dict:
    """Return high-level status for a match."""
    p = GetGameStatusParams(**params)
    repo = MatchRepository(session)
    match = await repo.get_by_public_id(p.match_id)
    if match is None:
        raise NotFoundError(f"Match '{p.match_id}' not found.")
    return {
        "match_id": match.public_id,
        "status": match.status,
        "local_score": match.local_score,
        "opponent_score": match.opponent_score,
    }


async def handle_get_history(params: dict, session: AsyncSession) -> dict:
    """Return paginated public match history."""
    p = GetHistoryParams(**params)
    repo = MatchRepository(session)
    matches = await repo.list_matches(offset=p.offset, limit=p.limit)
    return {
        "offset": p.offset,
        "limit": p.limit,
        "items": [
            {"match_id": m.public_id, "status": m.status, "mode": m.mode}
            for m in matches
        ],
    }
