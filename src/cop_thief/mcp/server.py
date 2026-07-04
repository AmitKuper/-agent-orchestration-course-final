"""FastAPI router for the MCP endpoint at /mcp.

Handles inbound tool calls from guest MCP clients and remote game servers.
Dispatches to the appropriate tool handler from ``mcp.tools``.
"""

from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse

from cop_thief.api.deps import SessionDep
from cop_thief.mcp.schemas import McpError, McpRequest, McpResponse
from cop_thief.mcp.tools import (
    handle_get_game_status,
    handle_get_history,
    handle_get_observation,
    handle_list_supported_rules,
    handle_start_game,
    handle_submit_action,
)
from cop_thief.shared.errors import NotFoundError, ValidationError

router = APIRouter()

_METHOD_MAP = {
    "list_supported_rules": handle_list_supported_rules,
    "get_game_history": handle_get_history,
}
_SESSION_ONLY = {
    "list_supported_rules": handle_list_supported_rules,
    "get_game_history": handle_get_history,
    "get_observation": handle_get_observation,
    "submit_action": handle_submit_action,
    "get_game_status": handle_get_game_status,
}


def _error(req_id, code: int, message: str) -> JSONResponse:
    """Build an MCP error response."""
    resp = McpResponse(id=req_id, error=McpError(code=code, message=message))
    return JSONResponse(content=resp.model_dump(), status_code=status.HTTP_200_OK)


@router.post("")
async def mcp_dispatch(request: Request, body: McpRequest, session: SessionDep) -> JSONResponse:
    """Single endpoint that dispatches all MCP tool calls by method name.

    All responses use HTTP 200 with a JSON-RPC-style envelope. Errors are
    signalled via the ``error`` field, not via HTTP status codes, so that
    MCP clients can process error payloads uniformly.
    """
    method = body.method
    params = body.params
    req_id = body.id
    client_ip = request.client.host if request.client else "unknown"

    if method not in {*_SESSION_ONLY, "start_game_vs_server"}:
        return _error(req_id, -32601, f"Method not found: {method!r}")

    try:
        if method == "start_game_vs_server":
            result = await handle_start_game(params, session, client_ip)
        else:
            result = await _SESSION_ONLY[method](params, session)
    except (NotFoundError, ValidationError) as exc:
        return _error(req_id, -32602, str(exc))
    except Exception as exc:
        return _error(req_id, -32603, f"Internal error: {exc}")

    return JSONResponse(
        content=McpResponse(id=req_id, result=result).model_dump(),
        status_code=status.HTTP_200_OK,
    )


@router.get("")
async def mcp_info() -> dict:
    """Return MCP server capabilities for discovery."""
    return {
        "protocol": "mcp",
        "version": "1.0",
        "endpoint": "/mcp",
        "transport": "streamable-http",
    }
