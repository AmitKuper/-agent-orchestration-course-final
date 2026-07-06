"""REST endpoints for managing uvicorn sub-processes.

Routes
------
GET  /api/servers          — list all managed servers
POST /api/servers          — start a server on a given port
DELETE /api/servers/{port} — stop a specific server
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from cop_thief.api.deps import CurrentUserDep
from cop_thief.webserver.server_manager import ServerEntry, ServerManager, get_server_manager

router = APIRouter()

_ManagerDep = Annotated[ServerManager, Depends(get_server_manager)]


class StartServerRequest(BaseModel):
    """Request body for POST /api/servers."""

    port: int = Field(..., ge=1024, le=65535, description="TCP port to bind the new server on.")


class ServerEntryResponse(BaseModel):
    """Public representation of a managed server."""

    port: int
    pid: int
    started_at: str
    status: str


def _to_response(entry: ServerEntry) -> ServerEntryResponse:
    """Convert a domain ServerEntry to its API schema."""
    return ServerEntryResponse(
        port=entry.port,
        pid=entry.pid,
        started_at=entry.started_at,
        status=entry.status,
    )


@router.get("/servers", response_model=list[ServerEntryResponse])
async def list_servers(
    _user: CurrentUserDep,
    manager: _ManagerDep,
) -> list[ServerEntryResponse]:
    """List all managed servers with their port, pid, and status.

    Requires authentication. Returns an empty list when no servers are running.
    """
    return [_to_response(e) for e in manager.list_servers()]


@router.post("/servers", response_model=ServerEntryResponse, status_code=status.HTTP_201_CREATED)
async def start_server(
    body: StartServerRequest,
    _user: CurrentUserDep,
    manager: _ManagerDep,
) -> ServerEntryResponse:
    """Start a new uvicorn process on *port*.

    Returns HTTP 201 with the new server's details on success.
    Returns HTTP 409 if the port is already in use by a managed server.
    Returns HTTP 400 if the port is reserved or the process fails to launch.
    """
    try:
        entry = manager.start(body.port)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return _to_response(entry)


@router.delete("/servers/{port}", response_model=ServerEntryResponse)
async def stop_server(
    port: int,
    _user: CurrentUserDep,
    manager: _ManagerDep,
) -> ServerEntryResponse:
    """Stop the managed server on *port*.

    Returns HTTP 404 if no server is managed on that port.
    """
    try:
        entry = manager.stop(port)
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return _to_response(entry)
