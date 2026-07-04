"""Async SQLAlchemy engine and session factory.

Use get_session() as a FastAPI dependency for route handlers.
Use init_db() on startup for development (SQLite create_all).
Production uses Alembic migrations instead.
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

_engines: dict[str, object] = {}
_factories: dict[str, async_sessionmaker] = {}


def _get_engine(database_url: str):
    """Return (and cache) the async engine for *database_url*.

    In-memory SQLite URLs use ``StaticPool`` so all connections share
    the same underlying connection (required for ``:memory:`` databases).
    """
    if database_url not in _engines:
        is_memory = ":memory:" in database_url
        kwargs: dict = {"echo": False}
        if is_memory:
            kwargs["connect_args"] = {"check_same_thread": False}
            kwargs["poolclass"] = StaticPool
        _engines[database_url] = create_async_engine(database_url, **kwargs)
    return _engines[database_url]


def _get_factory(database_url: str) -> async_sessionmaker:
    """Return (and cache) the session factory for *database_url*."""
    if database_url not in _factories:
        engine = _get_engine(database_url)
        _factories[database_url] = async_sessionmaker(engine, expire_on_commit=False)
    return _factories[database_url]


async def get_session(database_url: str) -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that yields an AsyncSession per request."""
    factory = _get_factory(database_url)
    async with factory() as session:
        yield session


async def init_db(database_url: str) -> None:
    """Create all tables from ORM metadata.

    Used for local SQLite development only.
    Production deployments run Alembic migrations instead.
    """
    import cop_thief.db.models  # noqa: F401 — registers all models
    from cop_thief.db.base import Base  # noqa: PLC0415

    engine = _get_engine(database_url)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
