"""Export endpoints. They receive, delegate and answer: no logic here.

The four verbs sit behind ``Security(get_current_user, scopes=[analista])``. Not
``operativo``: a bulk extraction is the operation of this portal with the
highest risk of data leaving the perimeter, so it sits above the punctual query
in the same hierarchy the permission matrix publishes.

``POST`` answers 202 and never 200. The work is queued in ``BackgroundTasks``
and the response carries the identifier the interface polls; doing the
extraction inside the handler would hold the request for the ten seconds the
million rows take and block the event loop of every other caller.

The bodies of the failures carry a stable code under ``detail.codigo`` and never
a sentence, because the interface is bilingual and owns the copy. The two
failures of a link are distinct on purpose: 410 says the link died of old age
and asking again for a fresh one will work, 403 says the signature was never
ours and asking again will not.
"""

import uuid
from typing import Annotated, Final

import structlog
from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    HTTPException,
    Query,
    Security,
    status,
)
from fastapi.responses import FileResponse

from app.core.auth import get_current_user
from app.core.scopes import Scope
from app.models.export import SolicitudExportacion, TrabajoDetalle
from app.models.user import UserOut
from app.services.almacen import EnlaceCaducado, FirmaInvalida
from app.services.export_service import (
    ExportErrorCode,
    ExportService,
    TrabajoNoEncontradoError,
    TrabajoResumenAtribuido,
    TrabajosNoDisponiblesError,
    get_export_service,
)

logger = structlog.get_logger()

router: Final[APIRouter] = APIRouter(prefix="/api/export", tags=["exportacion"])

# Media type served per produced extension. It is written here and not guessed
# from the filesystem because the answer must be the same on every machine: the
# registry of a developer workstation is not part of the contract.
_TIPOS: Final[dict[str, str]] = {
    ".csv": "text/csv",
    ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
}

_TIPO_POR_DEFECTO: Final[str] = "application/octet-stream"

# Shape of a signature this portal can have minted: sixty four lower case
# hexadecimal characters, which is what ``hexdigest`` of HMAC-SHA256 produces.
# The alphabet is part of the contract and not decoration. Length alone lets
# through a string of sixty four characters outside ASCII, and the comparison
# that verifies a signature -``hmac.compare_digest``- raises instead of
# answering false on those, so a link that was never ours would leave as a 500
# where the contract publishes 403. Refusing it here costs a 422 and one regular
# expression; the service still translates the same failure for the callers that
# do not come through this parameter.
_FIRMA_HEX: Final[str] = r"^[0-9a-f]{64}$"


@router.post(
    "",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=TrabajoDetalle,
    summary="Solicita una exportacion y la encola en segundo plano",
    responses={
        202: {"description": "Trabajo aceptado, aun sin archivo"},
        422: {"description": "El conjunto pedido no es exportable"},
        503: {"description": "El registro de trabajos no responde"},
    },
)
async def solicitar_exportacion(
    solicitud: SolicitudExportacion,
    current_user: Annotated[
        UserOut, Security(get_current_user, scopes=[Scope.ANALISTA])
    ],
    servicio: Annotated[ExportService, Depends(get_export_service)],
    tareas: BackgroundTasks,
) -> TrabajoDetalle:
    """Accept the request, queue the work and answer immediately with a job id.

    Args:
        solicitud: Validated body of the request.
        current_user: Caller resolved by the security dependency.
        servicio: Business logic of the export jobs.
        tareas: Queue of work that runs once the response is on the wire.

    Returns:
        The job in state ``pendiente``, with the identifier the interface polls.

    Raises:
        HTTPException: 503 ``trabajos_no_disponibles`` when the registry of
            jobs cannot be reached.
    """
    try:
        trabajo = await servicio.solicitar(solicitud, current_user)
    except TrabajosNoDisponiblesError as error:
        raise _no_disponible() from error

    tareas.add_task(servicio.ejecutar, trabajo.job_id)
    return trabajo


@router.get(
    "",
    response_model=list[TrabajoResumenAtribuido],
    summary="Historial de exportaciones; para admin, el registro completo",
    responses={503: {"description": "El registro de trabajos no responde"}},
)
async def listar_exportaciones(
    current_user: Annotated[
        UserOut, Security(get_current_user, scopes=[Scope.ANALISTA])
    ],
    servicio: Annotated[ExportService, Depends(get_export_service)],
    limite: Annotated[int, Query(ge=1, le=200)] = 50,
) -> list[TrabajoResumenAtribuido]:
    """Export history: the caller's jobs, or every job when the caller is admin.

    The two answers have one shape and one scope. Which rows travel is decided
    in the service, because it is a rule about who owns what and not about
    HTTP, and what travels is metadata either way: this contract carries no
    signed URL for anybody, so the register an administrator reads never turns
    into a file they could download.

    Args:
        current_user: Caller resolved by the security dependency.
        servicio: Business logic of the export jobs.
        limite: Maximum number of rows.

    Returns:
        The jobs, newest first, each attributed to whoever asked for it.

    Raises:
        HTTPException: 503 ``trabajos_no_disponibles`` when the registry of
            jobs cannot be reached.
    """
    try:
        return await servicio.historial(current_user, limite)
    except TrabajosNoDisponiblesError as error:
        raise _no_disponible() from error


@router.get(
    "/{job_id}",
    response_model=TrabajoDetalle,
    summary="Estado del trabajo y enlace firmado cuando ya termino",
    responses={
        404: {"description": "No hay trabajo con ese identificador para el llamante"},
        503: {"description": "El registro de trabajos no responde"},
    },
)
async def consultar_exportacion(
    job_id: uuid.UUID,
    current_user: Annotated[
        UserOut, Security(get_current_user, scopes=[Scope.ANALISTA])
    ],
    servicio: Annotated[ExportService, Depends(get_export_service)],
) -> TrabajoDetalle:
    """Polling endpoint used by the Pinia store every three seconds.

    Args:
        job_id: Identifier of the job.
        current_user: Caller resolved by the security dependency.
        servicio: Business logic of the export jobs.

    Returns:
        The job, with its signed link once it completed.

    Raises:
        HTTPException: 404 ``trabajo_no_encontrado`` when the job does not
            exist or is not the caller's; 503 ``trabajos_no_disponibles`` when
            the registry cannot be reached.
    """
    try:
        return await servicio.consultar(job_id, current_user)
    except TrabajoNoEncontradoError as error:
        raise _no_encontrado() from error
    except TrabajosNoDisponiblesError as error:
        raise _no_disponible() from error


@router.get(
    "/{job_id}/download",
    response_class=FileResponse,
    summary="Entrega el archivo detras del enlace firmado",
    responses={
        200: {"description": "El archivo producido"},
        403: {"description": "La firma del enlace no es de este portal"},
        404: {"description": "No hay trabajo con ese identificador para el llamante"},
        410: {"description": "El enlace firmado ya vencio"},
        422: {"description": "La firma no tiene la forma de una firma del portal"},
    },
)
async def descargar_exportacion(
    job_id: uuid.UUID,
    current_user: Annotated[
        UserOut, Security(get_current_user, scopes=[Scope.ANALISTA])
    ],
    servicio: Annotated[ExportService, Depends(get_export_service)],
    exp: Annotated[int, Query(description="Vencimiento del enlace, en epoch")],
    sig: Annotated[str, Query(min_length=64, max_length=64, pattern=_FIRMA_HEX)],
) -> FileResponse:
    """Serve the file behind the locally signed link; 410 once it expired.

    Args:
        job_id: Identifier of the job.
        current_user: Caller resolved by the security dependency. The signature
            is not a substitute for the session: a leaked link is still useless
            to somebody who is not the owner of the job.
        servicio: Business logic of the export jobs.
        exp: Deadline carried by the link, as a Unix timestamp.
        sig: Signature carried by the link, constrained to the alphabet a
            digest of this portal is written in.

    Returns:
        The produced file.

    Raises:
        HTTPException: 403 ``firma_invalida`` when the signature is not ours;
            410 ``enlace_caducado`` when the deadline passed; 404
            ``trabajo_no_encontrado`` when the job is not the caller's; 503
            ``trabajos_no_disponibles`` when the registry cannot be reached.
    """
    try:
        ruta = await servicio.resolver_descarga(job_id, exp, sig, current_user)
    except FirmaInvalida as error:
        raise _falla(status.HTTP_403_FORBIDDEN, ExportErrorCode.FIRMA_INVALIDA) from (
            error
        )
    except EnlaceCaducado as error:
        raise _falla(status.HTTP_410_GONE, ExportErrorCode.ENLACE_CADUCADO) from error
    except TrabajoNoEncontradoError as error:
        raise _no_encontrado() from error
    except TrabajosNoDisponiblesError as error:
        raise _no_disponible() from error

    return FileResponse(
        ruta,
        media_type=_TIPOS.get(ruta.suffix, _TIPO_POR_DEFECTO),
        filename=ruta.name,
    )


def _no_encontrado() -> HTTPException:
    """Build the 404 every ownership failure answers with.

    It is 404 and not 403 on purpose, and the body carries the code and nothing
    else: a 403 would confirm that the identifier exists and turn it into an
    oracle for enumerating the exports of other people.

    Returns:
        The exception to raise.
    """
    return _falla(status.HTTP_404_NOT_FOUND, ExportErrorCode.TRABAJO_NO_ENCONTRADO)


def _no_disponible() -> HTTPException:
    """Build the 503 the export screen has a designed empty state for.

    Returns:
        The exception to raise.
    """
    return _falla(
        status.HTTP_503_SERVICE_UNAVAILABLE, ExportErrorCode.TRABAJOS_NO_DISPONIBLES
    )


def _falla(codigo_http: int, codigo: ExportErrorCode) -> HTTPException:
    """Assemble one failure of this router.

    Args:
        codigo_http: Status of the answer.
        codigo: Stable code the interface keys its copy on.

    Returns:
        The exception to raise, with the code under ``detail.codigo``.
    """
    return HTTPException(status_code=codigo_http, detail={"codigo": codigo.value})
