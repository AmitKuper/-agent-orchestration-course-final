"""FastAPI application factory.

All routers must be registered here. The app object is the ASGI entry
point used by uvicorn.
"""

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from cop_thief.api.routes_admin import router as admin_router
from cop_thief.api.routes_auth import router as auth_router
from cop_thief.api.routes_games import router as games_router
from cop_thief.api.routes_health import router as health_router
from cop_thief.api.routes_ws import router as ws_router
from cop_thief.constants import API_PREFIX, APP_NAME, MCP_PREFIX, WS_PREFIX
from cop_thief.db.session import init_db
from cop_thief.mcp.server import router as mcp_router
from cop_thief.shared.version import VERSION
from cop_thief.webserver.config import get_settings

logger = logging.getLogger(__name__)

_STATIC_DIR = Path(__file__).parent.parent / "frontend" / "static"


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
    app.include_router(ws_router, prefix=WS_PREFIX, tags=["ws"])

    # Serve the frontend SPA under /app/*
    app.mount("/app", StaticFiles(directory=_STATIC_DIR, html=True), name="frontend")

    @app.get("/", include_in_schema=False)
    async def _root() -> FileResponse:
        """Redirect root to the frontend index page."""
        return FileResponse(_STATIC_DIR / "index.html")

    return app


app = create_app()
