"""Business rules of the background export jobs. The router holds none of them.

Four properties of this module are worth reading before changing it.

The CSV extraction is a **streaming** pipeline: ``scan_parquet`` plus
``sink_csv``, never ``read_parquet``. The target job is a million rows, and
materialising that in memory would hold the process while the health probe of
Cloud Run is waiting for an answer. For the same reason every call that touches
disk or CPU is handed to a worker thread: this coroutine runs inside the event
loop of the API, and the only thing it is allowed to do there is await.

A spreadsheet cannot be streamed -it is a zip archive whose sheet is written in
one pass- so that path materialises, and because it materialises it is capped.
The cap is a measurement and not a taste: see ``_FILAS_MAXIMAS_XLSX``.

The job repository is a protocol. That seam is what keeps the whole export suite
running without PostgreSQL, which is the property US-002 established for the
backend and this module preserves; ``get_export_repository`` is the dependency
the tests substitute, never the engine.

Ownership of a job is answered with a **404 and never a 403**. A 403 would
confirm that the identifier exists, which turns the endpoint into an oracle: an
analyst could walk the identifier space and learn how many exports other people
run and when. Reading metadata is not reading data, so an administrator does see
any job as governance -one by one and as a whole register- but never its file
and never a link to it. For everybody else the owner filter of the history is
not optional, which is why the statement that drops it is a different method of
the repository and not an argument of the one that keeps it.
"""

import asyncio
import contextlib
import importlib.util
import tempfile
import uuid
from collections.abc import AsyncIterator, Mapping, Sequence
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import StrEnum
from pathlib import Path
from typing import Annotated, Any, Final, Protocol

import polars as pl
import structlog
from fastapi import Depends
from sqlalchemy.exc import InterfaceError, OperationalError
from sqlmodel import col, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import Settings, get_settings
from app.core.database import get_session
from app.core.scopes import Scope
from app.models.export import (
    EstadoTrabajo,
    ExportJob,
    FormatoExportacion,
    SolicitudExportacion,
    TrabajoDetalle,
    TrabajoResumen,
)
from app.models.user import UserOut
from app.services.almacen import (
    AlmacenDeExportaciones,
    AlmacenServidoPorLaApi,
    FirmaInvalida,
    Reloj,
    RelojDelSistema,
    crear_almacen,
)

logger = structlog.get_logger()

# Subdirectory of the data root where ``make data`` leaves the synthetic silos.
# One file per exportable dataset, named after it.
SILOS_DIRNAME: Final[str] = "silos"

# Prefix of the file the background task writes before handing it to the
# storage. It lives in the system temporary directory because that is the only
# writable path of a Cloud Run container.
_PREFIJO_TEMPORAL: Final[str] = "karisma-export-"

# Package Polars needs to write a spreadsheet. It travels as the ``xlsxwriter``
# extra of the pinned Polars, so any deployment installed from the lock file has
# it. The check is still made: an environment assembled by hand can lack it, and
# discovering that as an ``ImportError`` inside a background task would leave the
# job in progress with nothing explaining why.
_PAQUETE_XLSX: Final[str] = "xlsxwriter"

# Rows a spreadsheet job accepts. It is not the limit of the format -a sheet
# holds 1 048 576 rows- but the limit this service can honour without missing
# the health gate of ``backend/AGENTS.md``.
#
# ``xlsxwriter`` is pure Python, so it keeps taking the interpreter lock back
# even while it runs in a worker thread. Measured over the ``liquidez`` silo
# (eleven columns) with an asyncio watcher sampling how late the event loop was
# woken during the write:
#
#     100 000 rows ->  6.1 s, worst loop delay   112 ms
#     200 000 rows -> 12.1 s, worst loop delay   198 ms, peak RSS   707 MB
#     300 000 rows -> 18.1 s, worst loop delay   381 ms, peak RSS 1 230 MB
#     500 000 rows -> 31.0 s, worst loop delay   505 ms, peak RSS 1 780 MB
#   1 000 000 rows -> 61.6 s, worst loop delay   997 ms
#
# The gate is 500 ms, so the target volume of the plan -the million rows of
# ``liquidez``- misses it by a factor of two while holding more memory than the
# instance has. Two hundred thousand keeps two and a half times of margin and
# still exports ``creditos`` (180 000 rows) and ``derivados`` (80 000) whole:
# the only source it cuts is the one that cannot be a spreadsheet anyway.
# CSV carries no such limit, because ``sink_csv`` never materialises.
_FILAS_MAXIMAS_XLSX: Final[int] = 200_000


class ExportErrorCode(StrEnum):
    """Stable codes of the export domain, returned or stored, never prose.

    The first four are answered over HTTP and the last four are written into
    ``export_job.error_code``. Both halves are contract: the interface is
    bilingual and owns the copy, so a sentence here would exist in one language
    only.

    ``FORMATO_NO_DISPONIBLE`` covers the two ways a spreadsheet is refused:
    this deployment carries no writer, or the result is larger than a
    spreadsheet job of this service may be. They are one code because the
    interface maps anything it does not know onto "internal failure", which
    neither of them is; the logs of ``_escribir_xlsx`` tell them apart.
    """

    TRABAJO_NO_ENCONTRADO = "trabajo_no_encontrado"
    ENLACE_CADUCADO = "enlace_caducado"
    FIRMA_INVALIDA = "firma_invalida"
    TRABAJOS_NO_DISPONIBLES = "trabajos_no_disponibles"
    ORIGEN_AUSENTE = "origen_ausente"
    COLUMNA_DESCONOCIDA = "columna_desconocida"
    FORMATO_NO_DISPONIBLE = "formato_no_disponible"
    FALLO_INTERNO = "fallo_interno"


class TrabajoNoEncontradoError(Exception):
    """The job does not exist, or it is not the caller's to look at."""


class TrabajosNoDisponiblesError(Exception):
    """The job registry is unreachable, so no answer about jobs is possible."""


class ExportacionFallidaError(Exception):
    """The extraction failed for a reason worth telling the analyst about.

    Attributes:
        codigo: Stable code written into the row and shown by the interface.
    """

    def __init__(self, codigo: ExportErrorCode) -> None:
        """Bind the failure to its stable code.

        Args:
            codigo: Code written into ``export_job.error_code``.
        """
        super().__init__(codigo.value)
        self.codigo = codigo


class TrabajoResumenAtribuido(TrabajoResumen):
    """History entry that also says whose job it is.

    The history of an administrator is the register of the whole portal, and a
    register without owners is unreadable as governance: it would say what was
    extracted and when, and never by whom. What travels is the identifier the
    row already carries, which is the same one every caller reads about
    themselves in ``/api/auth/me``; no address, no display name and nothing
    else about the person is added here.

    The field is filled for every caller and not only for an administrator.
    Nobody else ever sees a job that is not theirs -the owner filter of
    ``listar`` is not optional- so the value is their own identifier and tells
    them nothing they did not already have, whereas a field that appeared for
    one role only would hand the interface two shapes of the same list.

    It lives next to the service instead of in ``app.models.export`` with the
    other contracts because the wave that closed this debt did not own that
    file. It is a subclass that adds exactly one field, so moving it there
    later changes an import and nothing else.

    Attributes:
        solicitado_por: Identifier of the user who asked for the job.
    """

    solicitado_por: uuid.UUID


@dataclass(frozen=True)
class Extracto:
    """What the extraction produced, measured on the file it left on disk.

    Attributes:
        filas: Rows written, counted on the same filtered plan that was sunk.
        tamano_bytes: Size of the produced file.
    """

    filas: int
    tamano_bytes: int


class TrabajoRepository(Protocol):
    """Persistence of the export jobs, seen as a small state machine."""

    async def crear(self, trabajo: ExportJob) -> ExportJob:
        """Insert a job in its initial state.

        Args:
            trabajo: Row to insert, with its identifier already assigned.

        Returns:
            The inserted row.
        """
        ...

    async def obtener(self, job_id: uuid.UUID) -> ExportJob | None:
        """Return one job by primary key.

        Args:
            job_id: Identifier of the job.

        Returns:
            The row, or ``None`` when no job carries that identifier.
        """
        ...

    async def listar(
        self, *, requested_by: uuid.UUID, limite: int
    ) -> Sequence[ExportJob]:
        """Return the jobs of one user, newest first.

        Args:
            requested_by: Owner whose jobs are listed.
            limite: Maximum number of rows.

        Returns:
            The rows, ordered by creation instant descending.
        """
        ...

    async def listar_todos(self, *, limite: int) -> Sequence[ExportJob]:
        """Return the jobs of every user, newest first.

        It is a separate method and not a nullable argument of ``listar`` on
        purpose: the owner filter is mandatory, so dropping it has to be
        something a caller asks for by name and never something that happens
        because a parameter was left unset.

        Args:
            limite: Maximum number of rows.

        Returns:
            The rows of the whole register, ordered by creation instant
            descending.
        """
        ...

    async def marcar_en_proceso(
        self, job_id: uuid.UUID, *, iniciado: datetime
    ) -> ExportJob | None:
        """Take a pending job, if it is still pending.

        Args:
            job_id: Identifier of the job.
            iniciado: Instant the background task picked it up.

        Returns:
            The row now in progress, or ``None`` when it did not exist or was
            not pending any more.
        """
        ...

    async def marcar_completado(
        self,
        job_id: uuid.UUID,
        *,
        object_key: str,
        filas: int,
        tamano_bytes: int,
        terminado: datetime,
        caduca: datetime,
    ) -> ExportJob | None:
        """Close a job as completed, with everything its constraint demands.

        Args:
            job_id: Identifier of the job.
            object_key: Handle of the produced file in the storage.
            filas: Rows written.
            tamano_bytes: Size of the produced file.
            terminado: Instant the job reached its terminal state.
            caduca: Instant the signed link stops working.

        Returns:
            The closed row, or ``None`` when it did not exist.
        """
        ...

    async def marcar_fallido(
        self, job_id: uuid.UUID, *, error_code: str, terminado: datetime
    ) -> ExportJob | None:
        """Close a job as failed, with the stable code its constraint demands.

        Args:
            job_id: Identifier of the job.
            error_code: Stable failure code.
            terminado: Instant the job reached its terminal state.

        Returns:
            The closed row, or ``None`` when it did not exist.
        """
        ...


@asynccontextmanager
async def _tienda_disponible(session: AsyncSession) -> AsyncIterator[None]:
    """Turn an unreachable database into a typed failure, session still usable.

    Only connection level errors are translated. A malformed statement is a
    defect and has to keep surfacing as one; a database that is not answering
    is an operational state the export history has a designed empty view for,
    and on a service that scales to zero it is a state that really happens.

    The rollback is what makes the translation honest. SQLAlchemy leaves the
    session in a transaction that refuses every further statement -any use of it
    raises ``PendingRollbackError`` until somebody rolls back- and this domain
    has a caller that keeps using the very same session after the failure: the
    background task catches whatever ``ejecutar`` raised and calls ``_fallar``,
    which writes the terminal state through this repository. Without the
    rollback that recovery write is refused too, the job stays ``en_proceso``
    for good and the interface polls it until it gives up. The session travels
    as an argument for the smallest possible surface: the manager is private to
    this module and every caller is a method that already holds it, so nothing
    outside the repository learns that a rollback happens at all.

    Translating and rolling back stay together on purpose. A failure that is
    translated is one the caller is meant to survive; a failure that is not
    translated is a defect that ends the request, and the session dies with it.

    Args:
        session: Session the statement runs on, left usable before the typed
            failure escapes.

    Yields:
        None. The manager only reshapes the failure.

    Raises:
        TrabajosNoDisponiblesError: If the registry cannot be reached.
    """
    try:
        yield
    except (InterfaceError, OperationalError) as error:
        logger.error("export.registro.inalcanzable", causa=type(error).__name__)
        await _revertir(session)
        message = "no se pudo consultar el registro de trabajos de exportacion"
        raise TrabajosNoDisponiblesError(message) from error


async def _revertir(session: AsyncSession) -> None:
    """Roll the failed transaction back without hiding the failure that caused it.

    The rollback itself can fail -the connection is already gone in the case
    this runs in- and that must not replace the typed failure of the domain with
    a driver error nobody upstream knows how to answer. So it is logged and
    swallowed: what the caller needs to be told is that the registry is
    unreachable, which is what the manager raises next.

    Args:
        session: Session to return to a usable state.
    """
    try:
        await session.rollback()
    except Exception as error:
        logger.warning("export.registro.sin_reversion", causa=type(error).__name__)


class SqlTrabajoRepository:
    """PostgreSQL implementation. The only place of the module that speaks SQL."""

    def __init__(self, session: AsyncSession) -> None:
        """Bind the repository to the session of the current request.

        Args:
            session: Session yielded by ``get_session``.
        """
        self._session = session

    async def crear(self, trabajo: ExportJob) -> ExportJob:
        """Insert a job in its initial state.

        Args:
            trabajo: Row to insert, with its identifier already assigned.

        Returns:
            The inserted row.
        """
        async with _tienda_disponible(self._session):
            self._session.add(trabajo)
            await self._session.commit()
        return trabajo

    async def obtener(self, job_id: uuid.UUID) -> ExportJob | None:
        """Return one job by primary key.

        Args:
            job_id: Identifier of the job.

        Returns:
            The row, or ``None`` when no job carries that identifier.
        """
        async with _tienda_disponible(self._session):
            return await self._session.get(ExportJob, job_id)

    async def listar(
        self, *, requested_by: uuid.UUID, limite: int
    ) -> Sequence[ExportJob]:
        """Return the jobs of one user, newest first.

        The filter by owner is written here, in the only statement that lists
        jobs, so that no caller can forget it: the history of exports is the
        cheapest data leak this feature could ship.

        Args:
            requested_by: Owner whose jobs are listed.
            limite: Maximum number of rows.

        Returns:
            The rows, ordered by creation instant descending.
        """
        statement = (
            select(ExportJob)
            .where(col(ExportJob.requested_by) == requested_by)
            .order_by(col(ExportJob.created_at).desc())
            .limit(limite)
        )
        async with _tienda_disponible(self._session):
            result = await self._session.exec(statement)
            return list(result.all())

    async def listar_todos(self, *, limite: int) -> Sequence[ExportJob]:
        """Return the jobs of every user, newest first.

        This is the only statement of the module without a ``WHERE
        requested_by``, and the only caller allowed to reach it is the
        governance branch of ``ExportService.historial``. The composite index
        of the migration is ``(requested_by, created_at DESC)``, so this query
        does not use it and sorts; the register is small and read by one role,
        which is a cost worth paying for not weakening the filtered statement
        that every other caller runs.

        Args:
            limite: Maximum number of rows.

        Returns:
            The rows of the whole register, ordered by creation instant
            descending.
        """
        statement = (
            select(ExportJob).order_by(col(ExportJob.created_at).desc()).limit(limite)
        )
        async with _tienda_disponible(self._session):
            result = await self._session.exec(statement)
            return list(result.all())

    async def marcar_en_proceso(
        self, job_id: uuid.UUID, *, iniciado: datetime
    ) -> ExportJob | None:
        """Take a pending job, if it is still pending.

        The state is checked before it is written, so a job that somehow got
        queued twice is executed once: the second attempt finds it out of the
        pending state and gets nothing to work on.

        Args:
            job_id: Identifier of the job.
            iniciado: Instant the background task picked it up.

        Returns:
            The row now in progress, or ``None`` when it did not exist or was
            not pending any more.
        """
        async with _tienda_disponible(self._session):
            trabajo = await self._session.get(ExportJob, job_id)
            if trabajo is None or trabajo.status != EstadoTrabajo.PENDIENTE.value:
                return None
            trabajo.status = EstadoTrabajo.EN_PROCESO.value
            trabajo.started_at = iniciado
            self._session.add(trabajo)
            await self._session.commit()
            return trabajo

    async def marcar_completado(
        self,
        job_id: uuid.UUID,
        *,
        object_key: str,
        filas: int,
        tamano_bytes: int,
        terminado: datetime,
        caduca: datetime,
    ) -> ExportJob | None:
        """Close a job as completed, with everything its constraint demands.

        Args:
            job_id: Identifier of the job.
            object_key: Handle of the produced file in the storage.
            filas: Rows written.
            tamano_bytes: Size of the produced file.
            terminado: Instant the job reached its terminal state.
            caduca: Instant the signed link stops working.

        Returns:
            The closed row, or ``None`` when it did not exist.
        """
        async with _tienda_disponible(self._session):
            trabajo = await self._session.get(ExportJob, job_id)
            if trabajo is None:
                return None
            trabajo.status = EstadoTrabajo.COMPLETADO.value
            trabajo.object_key = object_key
            trabajo.row_count = filas
            trabajo.byte_size = tamano_bytes
            trabajo.finished_at = terminado
            trabajo.expires_at = caduca
            self._session.add(trabajo)
            await self._session.commit()
            return trabajo

    async def marcar_fallido(
        self, job_id: uuid.UUID, *, error_code: str, terminado: datetime
    ) -> ExportJob | None:
        """Close a job as failed, with the stable code its constraint demands.

        Args:
            job_id: Identifier of the job.
            error_code: Stable failure code.
            terminado: Instant the job reached its terminal state.

        Returns:
            The closed row, or ``None`` when it did not exist.
        """
        async with _tienda_disponible(self._session):
            trabajo = await self._session.get(ExportJob, job_id)
            if trabajo is None:
                return None
            trabajo.status = EstadoTrabajo.FALLIDO.value
            trabajo.error_code = error_code
            trabajo.finished_at = terminado
            self._session.add(trabajo)
            await self._session.commit()
            return trabajo


class ExportService:
    """Business logic of export jobs. The router holds none of it."""

    def __init__(
        self,
        *,
        repositorio: TrabajoRepository,
        almacen: AlmacenDeExportaciones,
        data_dir: Path,
        ttl_horas: int = 24,
        retraso_demo: float = 0.0,
        reloj: Reloj | None = None,
    ) -> None:
        """Assemble the service from its four collaborators.

        Args:
            repositorio: Persistence of the jobs.
            almacen: Storage of the produced files and minter of their links.
            data_dir: Root of the read only data directory.
            ttl_horas: Lifetime of a signed link, in hours. It is the same
                number the storage signs, read from the same setting.
            retraso_demo: Seconds the real work is stretched by, so the in
                progress moment can be captured for the deliverable.
            reloj: Clock stamped on every state change. Defaults to the system
                clock.
        """
        self._repositorio = repositorio
        self._almacen = almacen
        self._data_dir = data_dir
        self._ttl = timedelta(hours=ttl_horas)
        self._retraso_demo = retraso_demo
        self._reloj = reloj or RelojDelSistema()

    async def solicitar(
        self, solicitud: SolicitudExportacion, usuario: UserOut
    ) -> TrabajoDetalle:
        """Create the job in state pendiente and return it without doing the work.

        The identifier is minted here and not by the database default. The
        answer of the endpoint has to carry it, and the background task has to
        be queued against it, both before the transaction is anywhere near
        visible to another request.

        Args:
            solicitud: Validated body of the request.
            usuario: Caller resolved by the security dependency.

        Returns:
            The job as just created: no link, no expiry, state ``pendiente``.
        """
        trabajo = ExportJob(
            id=uuid.uuid4(),
            requested_by=usuario.id,
            dataset=solicitud.dataset,
            export_format=solicitud.formato.value,
            filters=dict(solicitud.filtros),
            status=EstadoTrabajo.PENDIENTE.value,
            created_at=self._reloj.ahora().replace(microsecond=0),
        )
        creado = await self._repositorio.crear(trabajo)

        # The raw filters never reach the log: they are the query of the user
        # and can name accounts, counterparties or dates of a single client.
        logger.info(
            "export.job.solicitado",
            job_id=str(creado.id),
            dataset=creado.dataset,
            formato=creado.export_format,
            usuario_id=str(usuario.id),
        )
        return self._a_detalle(creado, con_enlace=False)

    async def ejecutar(self, job_id: uuid.UUID) -> None:
        """Background entry point: produce the file and reach a terminal state.

        Every failure closes the job. A job that stays in progress forever is
        worse than a failed one: the interface polls it until it gives up and
        the analyst never learns what happened.

        Args:
            job_id: Identifier of the job to run.
        """
        trabajo = await self._repositorio.marcar_en_proceso(
            job_id, iniciado=self._reloj.ahora()
        )
        if trabajo is None:
            logger.warning("export.job.no_ejecutable", job_id=str(job_id))
            return

        temporal = (
            Path(tempfile.gettempdir())
            / f"{_PREFIJO_TEMPORAL}{job_id}.{trabajo.export_format}"
        )
        try:
            if self._retraso_demo > 0:
                # Asynchronous on purpose: it stretches the duration of the real
                # job without taking the event loop away from anybody else.
                await asyncio.sleep(self._retraso_demo)

            formato = FormatoExportacion(trabajo.export_format)
            extracto = await asyncio.to_thread(
                self._producir,
                dataset=trabajo.dataset,
                formato=formato,
                filtros=trabajo.filters,
                destino=temporal,
            )
            object_key = await self._almacen.guardar(job_id, temporal, formato.value)

            # Truncated to the second because that is the precision the signed
            # material carries: the row must not promise a deadline finer than
            # the signature can express.
            terminado = self._reloj.ahora().replace(microsecond=0)
            await self._repositorio.marcar_completado(
                job_id,
                object_key=object_key,
                filas=extracto.filas,
                tamano_bytes=extracto.tamano_bytes,
                terminado=terminado,
                caduca=terminado + self._ttl,
            )
            logger.info(
                "export.job.completado",
                job_id=str(job_id),
                dataset=trabajo.dataset,
                filas=extracto.filas,
                tamano_bytes=extracto.tamano_bytes,
            )
        except ExportacionFallidaError as error:
            await self._fallar(job_id, error.codigo, causa=type(error).__name__)
        except Exception as error:
            # The class of the exception is logged and never its message: the
            # message of an I/O failure carries absolute paths of the host.
            await self._fallar(
                job_id, ExportErrorCode.FALLO_INTERNO, causa=type(error).__name__
            )
        finally:
            with contextlib.suppress(OSError):
                temporal.unlink(missing_ok=True)

    async def consultar(self, job_id: uuid.UUID, usuario: UserOut) -> TrabajoDetalle:
        """Return one job, or raise 404 when it belongs to somebody else.

        An administrator does see any job, because governance is reading the
        register of who exported what. What an administrator does not get is a
        link: the detail of a job that is not theirs comes without a URL and
        without an expiry, so the metadata never turns into the file.

        Args:
            job_id: Identifier of the job.
            usuario: Caller resolved by the security dependency.

        Returns:
            The job, with its signed link only when the caller owns it.

        Raises:
            TrabajoNoEncontradoError: If the job does not exist or is not the
                caller's and the caller is not an administrator.
        """
        trabajo = await self._repositorio.obtener(job_id)
        propio = trabajo is not None and trabajo.requested_by == usuario.id
        if trabajo is None or not (propio or usuario.role is Scope.ADMIN):
            raise self._no_encontrado(job_id)
        return self._a_detalle(trabajo, con_enlace=propio)

    async def historial(
        self, usuario: UserOut, limite: int = 50
    ) -> list[TrabajoResumenAtribuido]:
        """List jobs newest first: the caller's, or all of them for an admin.

        Governance is why the register exists, so an administrator reads it
        whole. What they read is metadata and stays metadata: a summary has no
        URL and no expiry to begin with, which is the same answer ``consultar``
        gives them with ``con_enlace=False``, and ``resolver_descarga`` keeps
        refusing them the file of anybody else. Every other role gets the
        filtered statement, and the filter lives inside it.

        Args:
            usuario: Caller resolved by the security dependency.
            limite: Maximum number of rows.

        Returns:
            The history, with the owner of each job attributed.
        """
        if usuario.role is Scope.ADMIN:
            filas = await self._repositorio.listar_todos(limite=limite)
            # Reading the whole register is an act of governance and leaves a
            # trace. Only the count travels: what was exported is in the rows
            # and naming it here would put the query of somebody else in a log.
            logger.info(
                "export.historial.gobierno",
                usuario_id=str(usuario.id),
                trabajos=len(filas),
            )
        else:
            filas = await self._repositorio.listar(
                requested_by=usuario.id, limite=limite
            )
        return [_a_resumen_atribuido(fila) for fila in filas]

    async def resolver_descarga(
        self, job_id: uuid.UUID, expira_en: int, firma: str, usuario: UserOut
    ) -> Path:
        """Validate signature, expiry and ownership before handing over the file.

        Ownership is strict here and admits no governance exception: reading
        metadata is not reading data, so an administrator who can see a foreign
        job still cannot download it.

        Args:
            job_id: Identifier of the job.
            expira_en: Deadline carried by the link, as a Unix timestamp.
            firma: Signature carried by the link.
            usuario: Caller resolved by the security dependency.

        Returns:
            The path of the produced file.

        Raises:
            TrabajoNoEncontradoError: If the job does not exist, is not the
                caller's, never completed, or this deployment does not serve
                its files from this API.
            FirmaInvalida: If the link was not signed by this portal, or
                carries a signature the portal cannot even compare.
            EnlaceCaducado: If the deadline of the link already passed.
        """
        trabajo = await self._repositorio.obtener(job_id)
        if trabajo is None or trabajo.requested_by != usuario.id:
            raise self._no_encontrado(job_id)
        if trabajo.status != EstadoTrabajo.COMPLETADO.value or not trabajo.object_key:
            raise self._no_encontrado(job_id)

        if not isinstance(self._almacen, AlmacenServidoPorLaApi):
            # The bucket signs and serves its own links, so this endpoint has
            # nothing to hand over. It answers as if the job did not exist
            # rather than describing the deployment to the caller.
            logger.warning("export.descarga.no_la_sirve_esta_api", job_id=str(job_id))
            raise self._no_encontrado(job_id)

        try:
            self._almacen.verificar(trabajo.object_key, expira_en, firma)
        except TypeError as error:
            # ``hmac.compare_digest`` does not answer False for a string with a
            # character outside ASCII: it raises. So a signature nobody could
            # have minted was leaving this method as a ``TypeError`` and the
            # download answered 500, which says "the portal is broken" about the
            # one case where the portal is working exactly as designed. The
            # router already refuses that shape with a 422, and this stays as
            # the second line: a signature that cannot even be compared is a
            # signature that is not ours, which is what ``FirmaInvalida`` means
            # and what the 403 of the contract publishes. The value is never
            # logged; it is attacker controlled text.
            logger.warning("export.descarga.firma_incomparable", job_id=str(job_id))
            message = "la firma del enlace no es comparable con la de este portal"
            raise FirmaInvalida(message) from error

        ruta = self._almacen.ruta_de(trabajo.object_key)
        if not ruta.is_file():
            logger.warning("export.descarga.archivo_ausente", job_id=str(job_id))
            raise self._no_encontrado(job_id)
        return ruta

    def _producir(
        self,
        *,
        dataset: str,
        formato: FormatoExportacion,
        filtros: Mapping[str, Any],
        destino: Path,
    ) -> Extracto:
        """Run the extraction. Synchronous: it is called from a worker thread.

        Args:
            dataset: Name of the silo to export.
            formato: Output format.
            filtros: Structured query, already validated by Pydantic.
            destino: Path the produced file is written to.

        Returns:
            What the extraction produced.

        Raises:
            ExportacionFallidaError: If the silo is not on disk, if a filter
                names a column that does not exist, or if the spreadsheet
                cannot be written by this deployment or at this size.
        """
        origen = self._data_dir / SILOS_DIRNAME / f"{dataset}.parquet"
        if not origen.is_file():
            logger.warning("export.extraccion.silo_ausente", dataset=dataset)
            raise ExportacionFallidaError(ExportErrorCode.ORIGEN_AUSENTE)

        marco = _con_filtros(pl.scan_parquet(origen), filtros)
        destino.parent.mkdir(parents=True, exist_ok=True)
        if formato is FormatoExportacion.CSV:
            marco.sink_csv(destino)
            filas = int(marco.select(pl.len()).collect().item())
        else:
            filas = _escribir_xlsx(marco, destino)
        return Extracto(filas=filas, tamano_bytes=destino.stat().st_size)

    async def _fallar(
        self, job_id: uuid.UUID, codigo: ExportErrorCode, *, causa: str
    ) -> None:
        """Close a job as failed and record why, without leaking the message.

        Args:
            job_id: Identifier of the job.
            codigo: Stable code stored in the row.
            causa: Class name of the exception. The message is deliberately
                dropped: it carries host paths and, for a database failure, the
                connection string.
        """
        logger.warning(
            "export.job.fallido", job_id=str(job_id), codigo=codigo.value, causa=causa
        )
        try:
            await self._repositorio.marcar_fallido(
                job_id,
                error_code=codigo.value,
                terminado=self._reloj.ahora().replace(microsecond=0),
            )
        except Exception as error:
            # The job cannot even be marked as failed. Nothing else can be done
            # from a background task, and raising here would only surface after
            # the response was already sent.
            logger.error(
                "export.job.sin_cierre",
                job_id=str(job_id),
                causa=type(error).__name__,
            )

    def _a_detalle(self, trabajo: ExportJob, *, con_enlace: bool) -> TrabajoDetalle:
        """Describe one job, minting its link only when it is due.

        Args:
            trabajo: Row to describe.
            con_enlace: Whether the caller is entitled to a download link.

        Returns:
            The detail contract, with URL and expiry only for a completed job
            of the caller.
        """
        resumen = _a_resumen(trabajo).model_dump()

        # The three conditions are written inline instead of behind a flag so
        # that the narrowing is visible to the reader and to the type checker:
        # the link is minted from the object key and the end of the job, and
        # neither exists before the state is completed.
        if (
            not con_enlace
            or trabajo.status != EstadoTrabajo.COMPLETADO.value
            or trabajo.object_key is None
            or trabajo.finished_at is None
        ):
            return TrabajoDetalle(**resumen)

        url, caduca = self._almacen.url_firmada(trabajo.object_key, trabajo.finished_at)
        return TrabajoDetalle(**resumen, url_descarga=url, caduca_en=caduca)

    def _no_encontrado(self, job_id: uuid.UUID) -> TrabajoNoEncontradoError:
        """Build the single failure every ownership check answers with.

        Args:
            job_id: Identifier of the job, for the log and never for the body.

        Returns:
            The exception the router turns into a 404.
        """
        logger.info("export.job.no_encontrado", job_id=str(job_id))
        message = f"no hay trabajo {job_id} para este usuario"
        return TrabajoNoEncontradoError(message)


def _a_resumen(trabajo: ExportJob) -> TrabajoResumen:
    """Map one row onto the contract the history is made of.

    Args:
        trabajo: Row to describe.

    Returns:
        The summary contract, without the object key and without a link.
    """
    if trabajo.id is None or trabajo.created_at is None:
        message = "una fila de export_job sin identificador o sin alta no es legible"
        raise ValueError(message)
    return TrabajoResumen(
        job_id=trabajo.id,
        dataset=trabajo.dataset,
        formato=FormatoExportacion(trabajo.export_format),
        estado=EstadoTrabajo(trabajo.status),
        filas=trabajo.row_count,
        tamano_bytes=trabajo.byte_size,
        solicitado_en=trabajo.created_at,
        iniciado_en=trabajo.started_at,
        terminado_en=trabajo.finished_at,
        error=trabajo.error_code,
    )


def _a_resumen_atribuido(trabajo: ExportJob) -> TrabajoResumenAtribuido:
    """Map one row onto the history entry, owner included.

    Args:
        trabajo: Row to describe.

    Returns:
        The summary, with the identifier of whoever asked for the job.
    """
    return TrabajoResumenAtribuido(
        **_a_resumen(trabajo).model_dump(), solicitado_por=trabajo.requested_by
    )


def _con_filtros(marco: pl.LazyFrame, filtros: Mapping[str, Any]) -> pl.LazyFrame:
    """Add one membership predicate per declared filter, and nothing else.

    This is the whole vocabulary the caller gets: a column of the silo and the
    value or values it must take. No expression arrives from outside and none is
    assembled from a string, which is the rule that keeps a language model -or a
    client- from writing the query this job runs.

    Args:
        marco: Lazy plan over the silo.
        filtros: Structured query, already validated by Pydantic.

    Returns:
        The plan with the predicates applied.

    Raises:
        ExportacionFallidaError: If a filter names a column the silo does not have.
    """
    if not filtros:
        return marco

    columnas = set(marco.collect_schema().names())
    for nombre in sorted(filtros):
        if nombre not in columnas:
            logger.warning("export.extraccion.columna_desconocida", columna=nombre)
            raise ExportacionFallidaError(ExportErrorCode.COLUMNA_DESCONOCIDA)
        valor = filtros[nombre]
        valores = valor if isinstance(valor, list) else [valor]
        marco = marco.filter(pl.col(nombre).is_in(valores))
    return marco


def _escribir_xlsx(marco: pl.LazyFrame, destino: Path) -> int:
    """Write the spreadsheet, when this deployment and this size allow one.

    The rows are counted before anything is materialised, on the plan and not
    on the data, so a result that does not fit the budget is refused without
    ever being loaded. That is also why this function returns the count instead
    of letting the caller ask for it again: the frame is already gone.

    Both refusals answer ``formato_no_disponible`` and the logs tell them
    apart. A code of its own would be more precise and less useful today: the
    interface maps every code it does not know onto "internal failure", which
    is the one thing neither of these is.

    Args:
        marco: Lazy plan over the silo.
        destino: Path the file is written to.

    Returns:
        Rows written into the sheet, header excluded.

    Raises:
        ExportacionFallidaError: If the writer package is not installed, or if
            the result is larger than a spreadsheet job of this service may be.
    """
    if importlib.util.find_spec(_PAQUETE_XLSX) is None:
        logger.warning("export.extraccion.sin_escritor_xlsx")
        raise ExportacionFallidaError(ExportErrorCode.FORMATO_NO_DISPONIBLE)

    filas = int(marco.select(pl.len()).collect().item())
    if filas > _FILAS_MAXIMAS_XLSX:
        logger.warning(
            "export.extraccion.xlsx_excede_el_limite",
            filas=filas,
            maximo=_FILAS_MAXIMAS_XLSX,
        )
        raise ExportacionFallidaError(ExportErrorCode.FORMATO_NO_DISPONIBLE)

    marco.collect().write_excel(destino)
    return filas


async def get_export_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> TrabajoRepository:
    """Return the job repository bound to the session of the request.

    This is the seam the suite substitutes, never the engine.

    Args:
        session: Session yielded by ``get_session``.

    Returns:
        The PostgreSQL implementation of the repository.
    """
    return SqlTrabajoRepository(session)


async def get_export_service(
    settings: Annotated[Settings, Depends(get_settings)],
    repositorio: Annotated[TrabajoRepository, Depends(get_export_repository)],
) -> ExportService:
    """Assemble the export service for one request.

    Args:
        settings: Application settings.
        repositorio: Persistence of the jobs.

    Returns:
        The service, with the storage chosen by the single factory that is
        allowed to choose one.
    """
    return ExportService(
        repositorio=repositorio,
        almacen=crear_almacen(settings),
        data_dir=settings.data_dir,
        ttl_horas=settings.export_link_ttl_hours,
        retraso_demo=settings.export_demo_delay_seconds,
    )
