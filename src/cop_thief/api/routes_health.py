"""Health-check endpoint — publicly accessible, no auth required."""

from fastapi import APIRouter

from cop_thief.api.deps import SettingsDep
from cop_thief.constants import HEALTH_OK
from cop_thief.schemas.api import HealthResponse
from cop_thief.shared.version import VERSION

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health(settings: SettingsDep) -> HealthResponse:
    """Return application health status and version.

    Used by load balancers and monitoring tools.
    """
    return HealthResponse(
        status=HEALTH_OK,
        version=VERSION,
        server_name=settings.server_name,
    )
