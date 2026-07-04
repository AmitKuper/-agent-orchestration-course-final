"""Integration tests for the /mcp endpoint."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_mcp_info_returns_capabilities(client: AsyncClient) -> None:
    """GET /mcp returns protocol info without authentication."""
    response = await client.get("/mcp")
    assert response.status_code == 200
    body = response.json()
    assert body["protocol"] == "mcp"


@pytest.mark.asyncio
async def test_list_supported_rules(client: AsyncClient) -> None:
    """MCP list_supported_rules tool returns rules_version and tool list."""
    response = await client.post(
        "/mcp",
        json={"method": "list_supported_rules", "params": {}, "id": 1},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["error"] is None
    assert "rules_version" in body["result"]
    assert "supported_tools" in body["result"]


@pytest.mark.asyncio
async def test_unknown_method_returns_error(client: AsyncClient) -> None:
    """Calling an unknown MCP method returns an error envelope, not HTTP 4xx."""
    response = await client.post(
        "/mcp",
        json={"method": "do_something_illegal", "params": {}, "id": 2},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["error"] is not None
    assert body["error"]["code"] == -32601


@pytest.mark.asyncio
async def test_get_game_history_empty(client: AsyncClient) -> None:
    """get_game_history returns an empty list on a fresh database."""
    response = await client.post(
        "/mcp",
        json={"method": "get_game_history", "params": {"offset": 0, "limit": 5}, "id": 3},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["error"] is None
    assert body["result"]["items"] == []


@pytest.mark.asyncio
async def test_get_observation_nonexistent_match(client: AsyncClient) -> None:
    """get_observation for an unknown match returns an error envelope."""
    response = await client.post(
        "/mcp",
        json={
            "method": "get_observation",
            "params": {"match_id": "no-such-match", "client_id": "bot"},
            "id": 4,
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["error"] is not None
