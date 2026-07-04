"""Async SQLAlchemy engine and session factory.

Use get_session() as a FastAPI dependency for route handlers.
Use init_db() on startup for development (SQLite create_all).
Production uses Alembic migrations instead.
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

_engine = None
_session_factory: async_sessionmaker | None = None


def _get_engine(database_url: str):
    """Return (and cache) the async engine for *database_url*."""
    global _engine
    if _engine is None:
        _engine = create_async_engine(database_url, echo=False)
    return _engine


def _get_factory(database_url: str) -> async_sessionmaker:
    """Return (and cache) the session factory."""
    global _session_factory
    if _session_factory is None:
        engine = _get_engine(database_url)
        _session_factory = async_sessionmaker(engine, expire_on_commit=False)
    return _session_factory


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
    from cop_thief.db.base import Base

    engine = _get_engine(database_url)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
