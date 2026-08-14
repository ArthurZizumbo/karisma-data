"""Health probe router.

The probe is intentionally unauthenticated: it is the liveness check used by
Docker Compose and by Cloud Run, which call it without credentials.
"""

from typing import Literal

import structlog
from fastapi import APIRouter
from pydantic import BaseModel

logger = structlog.get_logger()

router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    """Payload returned by the health probe.

    Attributes:
        status: Fixed ``ok`` marker.
        servicio: Service identifier consumed by the smoke test.
    """

    status: Literal["ok"]
    servicio: Literal["karisma-api"]


@router.get("/health", response_model=HealthResponse, summary="Sonda de salud")
async def read_health() -> HealthResponse:
    """Report that the service is up.

    Returns:
        The fixed health payload expected by the probes and the smoke test.
    """
    logger.debug("health_probe")
    return HealthResponse(status="ok", servicio="karisma-api")
