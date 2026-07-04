"""Integration test for the /api/health endpoint."""

import pytest
from httpx import AsyncClient

from cop_thief.shared.version import VERSION


@pytest.mark.asyncio
async def test_health_returns_ok(client: AsyncClient) -> None:
    """GET /api/health must return status=ok and the current version."""
    response = await client.get("/api/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["version"] == VERSION
    assert "server_name" in body


@pytest.mark.asyncio
async def test_health_is_unauthenticated(client: AsyncClient) -> None:
    """GET /api/health must be accessible without credentials."""
    response = await client.get("/api/health")
    assert response.status_code == 200
