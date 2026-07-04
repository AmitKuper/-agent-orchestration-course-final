"""MCP request/response Pydantic schemas.

The MCP protocol uses a JSON-RPC-style envelope: each call specifies a
``method`` and ``params``, and receives a ``result`` or ``error``.
"""

from pydantic import BaseModel


class McpRequest(BaseModel):
    """Envelope for an inbound MCP tool call."""

    method: str
    params: dict = {}
    id: str | int | None = None


class McpError(BaseModel):
    """Error payload returned on failure."""

    code: int
    message: str


class McpResponse(BaseModel):
    """Envelope for the MCP tool-call response."""

    id: str | int | None = None
    result: dict | None = None
    error: McpError | None = None


# --- Per-tool parameter schemas ------------------------------------------------


class StartGameParams(BaseModel):
    """Parameters for the ``start_game_vs_server`` tool."""

    client_id: str
    preferred_role: str = "any"


class GetObservationParams(BaseModel):
    """Parameters for the ``get_observation`` tool."""

    match_id: str
    client_id: str


class SubmitActionParams(BaseModel):
    """Parameters for the ``submit_action`` tool."""

    match_id: str
    client_id: str
    action: dict


class GetGameStatusParams(BaseModel):
    """Parameters for the ``get_game_status`` tool."""

    match_id: str


class GetHistoryParams(BaseModel):
    """Parameters for the ``get_game_history`` tool."""

    offset: int = 0
    limit: int = 20
