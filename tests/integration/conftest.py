"""Integration test fixtures — shared app and authenticated client setup."""

import os

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

import cop_thief.db.session as db_session_module
from cop_thief.db.base import Base
from cop_thief.db.models import game_event as ____  # noqa: F401
from cop_thief.db.models import match as __  # noqa: F401
from cop_thief.db.models import sub_game as ___  # noqa: F401
from cop_thief.db.models import user as _  # noqa: F401 — ensures model is registered

os.environ.setdefault("SECRET_KEY", "test-integration-secret")

_TEST_DB_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(autouse=True)
async def _reset_db_cache():
    """Replace the global engine/factory cache with a fresh in-memory DB per test."""
    engine = create_async_engine(
        _TEST_DB_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Inject into the session module's module-level caches
    db_session_module._engines[_TEST_DB_URL] = engine
    db_session_module._factories[_TEST_DB_URL] = factory

    yield

    db_session_module._engines.pop(_TEST_DB_URL, None)
    db_session_module._factories.pop(_TEST_DB_URL, None)
    await engine.dispose()


@pytest.fixture
def app():
    """App instance wired to the test DB URL."""
    os.environ["DATABASE_URL"] = _TEST_DB_URL
    from cop_thief.webserver.main import create_app  # noqa: PLC0415
    return create_app()


@pytest.fixture
async def client(app):
    """Async HTTP client with the test app."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
