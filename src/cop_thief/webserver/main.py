"""FastAPI application factory.

All routers must be registered here. The app object is the ASGI entry
point used by uvicorn.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from cop_thief.api.routes_admin import router as admin_router
from cop_thief.api.routes_auth import router as auth_router
from cop_thief.api.routes_games import router as games_router
from cop_thief.api.routes_health import router as health_router
from cop_thief.constants import API_PREFIX, APP_NAME, MCP_PREFIX
from cop_thief.db.session import init_db
from cop_thief.mcp.server import router as mcp_router
from cop_thief.shared.version import VERSION
from cop_thief.webserver.config import get_settings

logger = logging.getLogger(__name__)


@asynccontextmanager
async def _lifespan(app: FastAPI):
    """Run startup and shutdown logic."""
    settings = get_settings()
    logging.basicConfig(level=settings.log_level.upper())
    logger.info("Starting %s v%s", APP_NAME, VERSION)
    await init_db(settings.database_url)
    yield
    logger.info("Shutting down %s", APP_NAME)


def create_app() -> FastAPI:
    """Build and configure the FastAPI application."""
    settings = get_settings()
    app = FastAPI(
        title=APP_NAME,
        version=VERSION,
        lifespan=_lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(health_router, prefix=API_PREFIX, tags=["health"])
    app.include_router(auth_router, prefix=API_PREFIX, tags=["auth"])
    app.include_router(games_router, prefix=API_PREFIX, tags=["games"])
    app.include_router(admin_router, prefix=API_PREFIX, tags=["admin"])
    app.include_router(mcp_router, prefix=MCP_PREFIX, tags=["mcp"])
    return app


app = create_app()
