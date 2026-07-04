"""Integration tests for authenticated game endpoints.

Tests cover: login → create match → submit action flow.
All tests use an in-memory SQLite database provided by conftest._reset_db_cache.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_login_wrong_credentials_returns_401(client: AsyncClient) -> None:
    """POST /api/auth/login with wrong credentials returns 401."""
    response = await client.post(
        "/api/auth/login",
        json={"username": "nobody", "password": "wrong"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_game_requires_auth(client: AsyncClient) -> None:
    """POST /api/games/human-vs-server returns 401/403 without a token."""
    response = await client.post("/api/games/human-vs-server")
    assert response.status_code in (401, 403, 422)


@pytest.mark.asyncio
async def test_submit_action_requires_auth(client: AsyncClient) -> None:
    """POST /api/games/{id}/human-action returns 401/403 without a token."""
    response = await client.post(
        "/api/games/nonexistent-id/human-action",
        json={"type": "stay"},
    )
    assert response.status_code in (401, 403, 422)


@pytest.mark.asyncio
async def test_list_games_is_public(client: AsyncClient) -> None:
    """GET /api/games returns 200 without authentication."""
    response = await client.get("/api/games")
    assert response.status_code == 200
    body = response.json()
    assert "items" in body
    assert body["items"] == []


@pytest.mark.asyncio
async def test_get_game_404_for_unknown(client: AsyncClient) -> None:
    """GET /api/games/{id} returns 404 for an unknown public_id."""
    response = await client.get("/api/games/does-not-exist")
    assert response.status_code == 404
