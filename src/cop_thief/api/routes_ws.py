"""WebSocket endpoint for live game observation streaming.

Clients connect to ``WS /ws/games/{public_id}`` and receive a JSON
message every time the game state changes (after each action).

Message schema
--------------
On connection the server sends the current observation immediately.
Each subsequent push has the shape::

    {"event": "state_update", "observation": {...}}

When the game ends::

    {"event": "game_over", "winner": "cop"|"thief"|null}

On error (match not found)::

    {"event": "error", "detail": "..."}
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from cop_thief.api.ws_manager import manager
from cop_thief.db.repositories import MatchRepository
from cop_thief.db.session import get_session
from cop_thief.webserver.config import get_settings

router = APIRouter()


@router.websocket("/games/{public_id}")
async def ws_game(public_id: str, websocket: WebSocket) -> None:
    """Stream observation updates for *public_id* to a WebSocket client.

    The client receives the current match status immediately on connect,
    then gets pushed ``state_update`` events whenever the game progresses.
    """
    settings = get_settings()
    await manager.connect(public_id, websocket)
    try:
        async for session in get_session(settings.database_url):
            match = await MatchRepository(session).get_by_public_id(public_id)
            if match is None:
                await websocket.send_json({"event": "error", "detail": "Match not found."})
                return
            await websocket.send_json({
                "event": "connected",
                "match_id": public_id,
                "status": match.status,
            })
            break

        # Keep the socket alive; server pushes updates via manager.broadcast().
        while True:
            await websocket.receive_text()  # client heartbeat / ignored
    except WebSocketDisconnect:
        pass
    finally:
        await manager.disconnect(public_id, websocket)
