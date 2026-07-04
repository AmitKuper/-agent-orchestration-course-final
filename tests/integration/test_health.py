"""Integration test for the /api/health endpoint."""

import pytest
from httpx import ASGITransport, AsyncClient

from cop_thief.shared.version import VERSION
from cop_thief.webserver.main import create_app


@pytest.fixture
def app():
    """Create a fresh app instance backed by an in-memory SQLite database."""
    import os
    os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
    return create_app()


@pytest.mark.asyncio
async def test_health_returns_ok(app) -> None:
    """GET /api/health must return status=ok and the current version."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["version"] == VERSION
    assert "server_name" in body


@pytest.mark.asyncio
async def test_health_is_unauthenticated(app) -> None:
    """GET /api/health must be accessible without credentials."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/health")
    assert response.status_code == 200
