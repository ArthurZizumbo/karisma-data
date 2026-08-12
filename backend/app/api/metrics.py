"""Metrics endpoints. They receive, delegate and answer: no logic here.

The route sits behind ``Security(get_current_user, scopes=[analista])`` because
that is the rule ``SCOPE_REGISTRY`` published for it before the endpoint
existed, and it is the same level the frontend guard demands of the screen that
consumes it. A screen an ``operativo`` cannot open, served by an endpoint an
``operativo`` could read, would be two systems disagreeing about the same
permission.

The handler is synchronous on purpose. Reading a parquet, aggregating it and
encoding half a million floats is work for a thread, not for the event loop:
declared ``async def`` this endpoint would block every other request of the
process for as long as it took.

The bodies of the failures carry a stable code under ``detail.codigo`` and never
a sentence, because the interface is bilingual and owns the copy.
"""

import time
from pathlib import Path
from typing import Annotated, Final

import structlog
from fastapi import APIRouter, Depends, Header, HTTPException, Query, Security, status
from fastapi.responses import Response

from app.core.auth import get_current_user
from app.core.config import Settings, get_settings
from app.core.scopes import Scope
from app.models.series import ErrorSerie, SeriesErrorCode, SeriesParams
from app.models.user import UserOut
from app.services import series_service

logger = structlog.get_logger()

router = APIRouter(prefix="/api/metrics", tags=["metricas"])

# Five minutes in a private cache. Private and not public: the answer is
# authorized by scope and must never land in a shared cache.
CACHE_CONTROL: Final[str] = "private, max-age=300"

# Cardinality published as a header so a smoke script can assert the full load
# without decoding the frame.
POINTS_HEADER: Final[str] = "X-Karisma-Puntos"


@router.get(
    "/series",
    summary="Serie preagregada del tablero, en marco binario o en JSON",
    response_class=Response,
    responses={
        200: {"description": "Marco KSER1 o su variante JSON legible"},
        304: {"description": "El cliente ya tiene este marco"},
        413: {"description": "La variante JSON no admite tantos puntos"},
        503: {"description": "El agregado no esta sembrado: falta make data"},
    },
)
def get_series(
    _caller: Annotated[UserOut, Security(get_current_user, scopes=[Scope.ANALISTA])],
    params: Annotated[SeriesParams, Query()],
    settings: Annotated[Settings, Depends(get_settings)],
    if_none_match: Annotated[str | None, Header()] = None,
) -> Response:
    """Serve the preaggregated dashboard series.

    Returns 304 when the caller already holds the current frame, 413 when the
    JSON variant is asked for more points than it can carry, and 503 with a
    typed code when ``make data`` has not run.

    Args:
        _caller: Identity resolved by the security dependency. The series is the
            same for every role that reaches it, so the caller is only the
            guard.
        params: Validated query. The client composes a closed vocabulary and
            never an expression: the deterministic compiler of the service is
            the only thing that writes Polars.
        settings: Application settings, for the root of the data directory.
        if_none_match: Validator the client already holds, if any.

    Returns:
        The frame, its JSON variant, or an empty 304.

    Raises:
        HTTPException: 413 ``payload_excesivo`` when the JSON variant would
            exceed its ceiling; 503 ``datos_no_sembrados`` when the aggregate is
            not on disk.
    """
    data_dir = Path(settings.data_dir)
    started = time.perf_counter()

    try:
        etag = series_service.etag_for(params, data_dir=data_dir)
    except series_service.SeedMissingError as error:
        raise _not_seeded(error) from error

    if _matches(if_none_match, etag):
        logger.info(
            "serie_no_modificada",
            ms=round((time.perf_counter() - started) * 1000, 1),
        )
        return Response(
            status_code=status.HTTP_304_NOT_MODIFIED,
            headers={"ETag": etag, "Cache-Control": CACHE_CONTROL},
        )

    try:
        payload = series_service.build_payload(params, data_dir=data_dir)
    except series_service.SeedMissingError as error:
        raise _not_seeded(error) from error
    except series_service.PayloadTooLargeError as error:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail=ErrorSerie(
                codigo=SeriesErrorCode.PAYLOAD_EXCESIVO,
                puntos=error.puntos,
                maximo=error.maximo,
            ).as_detail(),
        ) from error

    return Response(
        content=payload.body,
        media_type=payload.media_type,
        headers={
            "ETag": payload.etag,
            "Cache-Control": CACHE_CONTROL,
            "Vary": "Authorization",
            POINTS_HEADER: str(payload.conteo.puntos),
        },
    )


def _not_seeded(error: series_service.SeedMissingError) -> HTTPException:
    """Build the 503 the designed empty state of the screen is waiting for.

    A fresh clone has no ``data/``: the aggregate is not versioned. Answering
    with a stack trace would turn the first screen an evaluator opens into a
    crash instead of into the state that tells them to run ``make data``.

    Args:
        error: Failure raised by the service.

    Returns:
        The exception to raise, with the name of the missing file.
    """
    return HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail=ErrorSerie(
            codigo=SeriesErrorCode.DATOS_NO_SEMBRADOS,
            archivo=error.path.name,
        ).as_detail(),
    )


def _matches(if_none_match: str | None, etag: str) -> bool:
    """Report whether a conditional request already holds this representation.

    The comparison is weak, as RFC 9110 section 8.8.3.2 requires for
    ``If-None-Match``: the ``W/`` prefix is stripped from both sides and ``*``
    matches anything the server has.

    Args:
        if_none_match: Raw header value, possibly a list of validators.
        etag: Validator of the current representation.

    Returns:
        ``True`` when the client can be answered with a 304.
    """
    if not if_none_match:
        return False
    current = etag.removeprefix("W/")
    for candidate in if_none_match.split(","):
        cleaned = candidate.strip()
        if cleaned == "*" or cleaned.removeprefix("W/") == current:
            return True
    return False
