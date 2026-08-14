"""The export endpoint queues work instead of doing it, and never blocks.

The four cases here are about the shape of the request cycle, not about
permissions -those live in ``test_export_estado_scopes.py``- and not about the
signed link -that lives in ``test_export_almacen_firmado.py``-.

``TestClient`` is deliberately absent from two of them. Starlette runs the
background tasks inside the ASGI call, so the synchronous client only returns
once the export already finished: a case written with it could neither see the
job in state ``pendiente`` nor tell an event loop that stayed free from one that
was held for the whole extraction.

The in-memory repository below is shared by the three export modules of the
suite. It does not live in ``tests/backend/conftest.py`` because that file is
the write-set of another User Story, and widening it would have been the cheap
move that breaks four unrelated modules.
"""

import asyncio
import importlib.util
import threading
import time
import uuid
import zipfile
from collections.abc import Callable, Mapping, Sequence
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import TYPE_CHECKING, Any, Final, cast

import polars as pl
import pytest
from fastapi import BackgroundTasks
from fastapi.routing import APIRoute
from pydantic import ValidationError
from sqlalchemy import Executable

from app.api.export import router, solicitar_exportacion
from app.models.export import (
    _FILTROS_MAXIMOS,
    _LONGITUD_MAXIMA_DE_COLUMNA,
    _LONGITUD_MAXIMA_DE_VALOR,
    _VALORES_MAXIMOS,
    EstadoTrabajo,
    ExportJob,
    FormatoExportacion,
    SolicitudExportacion,
)
from app.models.user import UserOut
from app.services.almacen import Reloj
from app.services.almacen.local import AlmacenLocalFirmado
from app.services.export_service import (
    _FILAS_MAXIMAS_XLSX,
    ExportService,
    Extracto,
    SqlTrabajoRepository,
    TrabajosNoDisponiblesError,
    get_export_service,
)
from app.services.user_service import get_user_repository

if TYPE_CHECKING:
    from conftest import FakeUserRepository
    from sqlmodel.ext.asyncio.session import AsyncSession

    from app.models.user import AppUser

# Instant every fixture of the export suite starts from. Fixed so that an
# assertion about an expiry is an assertion about arithmetic and never about
# when the suite happened to run.
INICIO: Final[datetime] = datetime(2026, 8, 13, 12, 0, tzinfo=UTC)

# Signing key of the doubles. It is a test value with the shape of a digest and
# has nothing to do with EXPORT_SIGNING_KEY, which is empty in every versioned
# file of the repository.
CLAVE_DE_PRUEBA: Final[str] = "0" * 64

# Rows of the synthetic silo the fixtures write. Small enough to keep the suite
# fast and large enough that the extraction is real work on a real file.
FILAS_DEL_SILO: Final[int] = 2_000

# Rows the spreadsheet case measures the event loop against. The writer is pure
# Python and takes about a second on this many rows and three columns, which is
# what makes the health probe unambiguous: an extraction left on the loop would
# answer it after that second, well past the gate of 500 ms.
FILAS_DEL_SILO_XLSX: Final[int] = 50_000

# Members every spreadsheet has, whichever tool opens it. They are asserted
# instead of a reader dependency: what has to be true is that the file is an
# OOXML package and not a zip with the right extension.
MIEMBROS_XLSX: Final[tuple[str, ...]] = (
    "[Content_Types].xml",
    "xl/workbook.xml",
    "xl/worksheets/sheet1.xml",
)

_REGISTRO_CAIDO: Final[str] = "el registro de trabajos no responde"

# Dataset used by every case. It is one of the three names the model froze, so
# the body validator lets it through.
CONJUNTO: Final[str] = "creditos"


class RelojFijo:
    """Clock the tests move by hand. The only way to test a deadline fast.

    Attributes:
        instante: Value the next call to ``ahora`` returns.
    """

    def __init__(self, instante: datetime = INICIO) -> None:
        """Start the clock at a known instant.

        Args:
            instante: First value of the clock.
        """
        self.instante = instante

    def ahora(self) -> datetime:
        """Return the instant the test set.

        Returns:
            The current value of the clock.
        """
        return self.instante

    def avanzar(self, delta: timedelta) -> None:
        """Move the clock forward.

        Args:
            delta: Amount of time to add.
        """
        self.instante = self.instante + delta


class RepositorioDeTrabajosEnMemoria:
    """In-memory double of ``TrabajoRepository``.

    It records the order of the state changes, which is what lets a case show
    that a job reached its terminal state through the transitions the state
    machine declares instead of by being written once at the end.

    Attributes:
        filas: Jobs indexed by primary key.
        transiciones: Names of the state changes applied, in order.
    """

    def __init__(self, filas: Sequence[ExportJob] = ()) -> None:
        """Store the jobs this repository starts with.

        Args:
            filas: Rows already in the registry.
        """
        self.filas: dict[uuid.UUID, ExportJob] = {
            fila.id: fila for fila in filas if fila.id is not None
        }
        self.transiciones: list[str] = []

    async def crear(self, trabajo: ExportJob) -> ExportJob:
        """Insert a job in its initial state.

        Args:
            trabajo: Row to insert.

        Returns:
            The inserted row.
        """
        assert trabajo.id is not None
        self.filas[trabajo.id] = trabajo
        self.transiciones.append("crear")
        return trabajo

    async def obtener(self, job_id: uuid.UUID) -> ExportJob | None:
        """Return one job by primary key.

        Args:
            job_id: Identifier of the job.

        Returns:
            The row, or ``None``.
        """
        return self.filas.get(job_id)

    async def listar(
        self, *, requested_by: uuid.UUID, limite: int
    ) -> Sequence[ExportJob]:
        """Return the jobs of one user, newest first.

        Args:
            requested_by: Owner whose jobs are listed.
            limite: Maximum number of rows.

        Returns:
            The rows of that owner, ordered by creation instant descending.
        """
        propios = [
            fila for fila in self.filas.values() if fila.requested_by == requested_by
        ]
        propios.sort(key=lambda fila: fila.created_at or INICIO, reverse=True)
        return propios[:limite]

    async def listar_todos(self, *, limite: int) -> Sequence[ExportJob]:
        """Return every job of the registry, newest first.

        Args:
            limite: Maximum number of rows.

        Returns:
            Every row, ordered by creation instant descending.
        """
        todos = sorted(
            self.filas.values(),
            key=lambda fila: fila.created_at or INICIO,
            reverse=True,
        )
        return todos[:limite]

    async def marcar_en_proceso(
        self, job_id: uuid.UUID, *, iniciado: datetime
    ) -> ExportJob | None:
        """Take a pending job, if it is still pending.

        Args:
            job_id: Identifier of the job.
            iniciado: Instant the background task picked it up.

        Returns:
            The row now in progress, or ``None``.
        """
        fila = self.filas.get(job_id)
        if fila is None or fila.status != EstadoTrabajo.PENDIENTE.value:
            return None
        fila.status = EstadoTrabajo.EN_PROCESO.value
        fila.started_at = iniciado
        self.transiciones.append("marcar_en_proceso")
        return fila

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
        """Close a job as completed.

        Args:
            job_id: Identifier of the job.
            object_key: Handle of the produced file.
            filas: Rows written.
            tamano_bytes: Size of the produced file.
            terminado: Instant the job ended.
            caduca: Instant the link expires.

        Returns:
            The closed row, or ``None``.
        """
        fila = self.filas.get(job_id)
        if fila is None:
            return None
        fila.status = EstadoTrabajo.COMPLETADO.value
        fila.object_key = object_key
        fila.row_count = filas
        fila.byte_size = tamano_bytes
        fila.finished_at = terminado
        fila.expires_at = caduca
        self.transiciones.append("marcar_completado")
        return fila

    async def marcar_fallido(
        self, job_id: uuid.UUID, *, error_code: str, terminado: datetime
    ) -> ExportJob | None:
        """Close a job as failed.

        Args:
            job_id: Identifier of the job.
            error_code: Stable failure code.
            terminado: Instant the job ended.

        Returns:
            The closed row, or ``None``.
        """
        fila = self.filas.get(job_id)
        if fila is None:
            return None
        fila.status = EstadoTrabajo.FALLIDO.value
        fila.error_code = error_code
        fila.finished_at = terminado
        self.transiciones.append("marcar_fallido")
        return fila


class ServicioQueAnotaElHilo(ExportService):
    """Service that records which thread ran the extraction.

    Where the Polars work happens is the property under test in T-3, and a
    latency measurement alone can only observe it indirectly. This subclass
    observes it directly.

    Attributes:
        hilo_de_extraccion: Identifier of the thread that ran the extraction.
    """

    hilo_de_extraccion: int | None = None

    def _producir(
        self,
        *,
        dataset: str,
        formato: FormatoExportacion,
        filtros: Mapping[str, Any],
        destino: Path,
    ) -> Extracto:
        """Record the thread and run the real extraction.

        Args:
            dataset: Name of the silo to export.
            formato: Output format.
            filtros: Structured query.
            destino: Path the file is written to.

        Returns:
            What the extraction produced.
        """
        self.hilo_de_extraccion = threading.get_ident()
        return super()._producir(
            dataset=dataset, formato=formato, filtros=filtros, destino=destino
        )


def sembrar_silo(data_dir: Path, *, filas: int = FILAS_DEL_SILO) -> Path:
    """Write a synthetic parquet where the service expects the silo.

    Args:
        data_dir: Root of the data directory of the test.
        filas: Number of rows to write.

    Returns:
        Path of the written parquet.
    """
    destino = data_dir / "silos" / f"{CONJUNTO}.parquet"
    destino.parent.mkdir(parents=True, exist_ok=True)
    pl.DataFrame(
        {
            "credito_id": [f"CR{indice:07d}" for indice in range(filas)],
            "sucursal": [f"S{indice % 12:02d}" for indice in range(filas)],
            "saldo": [float(indice % 9973) for indice in range(filas)],
        }
    ).write_parquet(destino)
    return destino


def crear_almacen_de_prueba(raiz: Path, reloj: Reloj) -> AlmacenLocalFirmado:
    """Build the local storage the cases sign and redeem links with.

    Args:
        raiz: Directory the produced files are kept in.
        reloj: Clock the expiry is checked against.

    Returns:
        The storage, with the frozen key and the twenty four hour lifetime.
    """
    return AlmacenLocalFirmado(
        clave=CLAVE_DE_PRUEBA, ttl_horas=24, reloj=reloj, raiz=raiz
    )


def trabajo_pendiente(
    propietario: uuid.UUID, *, creado: datetime = INICIO
) -> ExportJob:
    """Build a job row in its initial state.

    Args:
        propietario: Identifier of the user who asked for it.
        creado: Creation instant.

    Returns:
        The row, ready to be put in the repository double.
    """
    return ExportJob(
        id=uuid.uuid4(),
        requested_by=propietario,
        dataset=CONJUNTO,
        export_format=FormatoExportacion.CSV.value,
        filters={},
        status=EstadoTrabajo.PENDIENTE.value,
        created_at=creado,
    )


def usuario_de(fila: "AppUser") -> UserOut:
    """Map a seeded row onto what the security dependency hands the router.

    Args:
        fila: Seeded user.

    Returns:
        The caller contract.
    """
    return UserOut.model_validate(fila, from_attributes=True)


@pytest.fixture
def reloj() -> RelojFijo:
    """Return the clock every case of this module shares.

    Returns:
        A clock parked at the fixed start instant.
    """
    return RelojFijo()


@pytest.fixture
def repositorio() -> RepositorioDeTrabajosEnMemoria:
    """Return an empty job registry.

    Returns:
        The double, with no rows.
    """
    return RepositorioDeTrabajosEnMemoria()


@pytest.fixture
def servicio(
    tmp_path: Path,
    reloj: RelojFijo,
    repositorio: RepositorioDeTrabajosEnMemoria,
) -> ServicioQueAnotaElHilo:
    """Return the service wired to a real silo and a real local storage.

    Args:
        tmp_path: Directory of the test.
        reloj: Clock of the test.
        repositorio: Job registry double.

    Returns:
        The service under test.
    """
    data_dir = tmp_path / "data"
    sembrar_silo(data_dir)
    return ServicioQueAnotaElHilo(
        repositorio=repositorio,
        almacen=crear_almacen_de_prueba(tmp_path / "almacen", reloj),
        data_dir=data_dir,
        ttl_horas=24,
        reloj=reloj,
    )


@pytest.fixture
def analista(usuarios_semilla: dict[str, "AppUser"]) -> UserOut:
    """Return the seeded analyst, who is the caller of this module.

    Args:
        usuarios_semilla: Rows of the seven seeded users.

    Returns:
        The caller contract of the analyst.
    """
    fila = next(
        usuario for usuario in usuarios_semilla.values() if usuario.role == "analista"
    )
    return usuario_de(fila)


@pytest.fixture
def administrador(usuarios_semilla: dict[str, "AppUser"]) -> UserOut:
    """Return the seeded administrator, who reads the register as governance.

    Args:
        usuarios_semilla: Rows of the seven seeded users.

    Returns:
        The caller contract of the administrator.
    """
    fila = next(
        usuario for usuario in usuarios_semilla.values() if usuario.role == "admin"
    )
    return usuario_de(fila)


@pytest.mark.asyncio
async def test_solicitud_no_ejecuta_el_trabajo_en_el_handler(
    servicio: ServicioQueAnotaElHilo,
    repositorio: RepositorioDeTrabajosEnMemoria,
    analista: UserOut,
) -> None:
    """The handler queues the work and returns; it does not do the work.

    The defect this fails on is the obvious one: an ``await servicio.ejecutar``
    before the return. It would turn a 202 into a request that lasts as long as
    the extraction, and the interface would have nothing to poll because the
    answer would already carry a finished job.

    Args:
        servicio: Service under test.
        repositorio: Job registry double.
        analista: Caller of the request.
    """
    tareas = BackgroundTasks()

    trabajo = await solicitar_exportacion(
        solicitud=SolicitudExportacion(dataset=CONJUNTO),
        current_user=analista,
        servicio=servicio,
        tareas=tareas,
    )

    declarada = next(
        ruta
        for ruta in router.routes
        if isinstance(ruta, APIRoute)
        and ruta.path == "/api/export"
        and "POST" in (ruta.methods or ())
    )

    # 202 and not 200: the resource does not exist yet, and a 200 would tell
    # the polling store that there is nothing left to wait for.
    assert declarada.status_code == 202
    assert trabajo.estado is EstadoTrabajo.PENDIENTE
    assert trabajo.url_descarga is None
    assert len(tareas.tasks) == 1
    assert tareas.tasks[0].func == servicio.ejecutar
    assert tareas.tasks[0].args == (trabajo.job_id,)
    assert repositorio.transiciones == ["crear"]


@pytest.mark.asyncio
async def test_tarea_de_fondo_completa_el_trabajo(
    servicio: ServicioQueAnotaElHilo,
    repositorio: RepositorioDeTrabajosEnMemoria,
    reloj: RelojFijo,
    analista: UserOut,
    tmp_path: Path,
) -> None:
    """The queued task moves the job to a terminal state and leaves the file.

    Two defects fail here: queueing the wrong callable, and an ``ejecutar``
    that produces the file without persisting the closing state. The second one
    is the expensive one, because the job would stay ``pendiente`` forever and
    the interface would poll it until it gave up.

    Args:
        servicio: Service under test.
        repositorio: Job registry double.
        reloj: Clock of the test.
        analista: Owner of the job.
        tmp_path: Directory of the test.
    """
    detalle = await servicio.solicitar(SolicitudExportacion(dataset=CONJUNTO), analista)
    reloj.avanzar(timedelta(seconds=9))

    await servicio.ejecutar(detalle.job_id)

    fila = repositorio.filas[detalle.job_id]
    assert fila.status == EstadoTrabajo.COMPLETADO.value
    assert fila.row_count == FILAS_DEL_SILO
    assert fila.byte_size is not None and fila.byte_size > 0
    assert fila.object_key == f"{detalle.job_id}.csv"
    assert fila.finished_at is not None
    assert fila.expires_at == fila.finished_at + timedelta(hours=24)
    assert repositorio.transiciones == [
        "crear",
        "marcar_en_proceso",
        "marcar_completado",
    ]
    assert (tmp_path / "almacen" / fila.object_key).is_file()


@pytest.mark.asyncio
async def test_el_trabajo_no_toma_el_bucle_de_eventos(
    tmp_path: Path,
    reloj: RelojFijo,
    repositorio: RepositorioDeTrabajosEnMemoria,
    analista: UserOut,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The health probe answers while an export is in flight.

    This is the case ``TestClient`` cannot express: it does not return until
    the background task finished, so it can never ask anything of the
    application while the export is running.

    It fails on any blocking work left on the event loop -the demo delay
    written with ``time.sleep`` instead of ``asyncio.sleep``, or the extraction
    run inline instead of handed to a worker thread- because the health probe
    would then have to wait for the export before being served. The second
    assertion nails the same property down directly, since on this machine
    Polars is fast enough that latency alone would not always notice.

    Args:
        tmp_path: Directory of the test.
        reloj: Clock of the test.
        repositorio: Job registry double.
        analista: Owner of the job.
        monkeypatch: Used to pin the environment of the application.
    """
    import httpx

    from app.main import create_app

    data_dir = tmp_path / "data"
    sembrar_silo(data_dir)
    servicio = ServicioQueAnotaElHilo(
        repositorio=repositorio,
        almacen=crear_almacen_de_prueba(tmp_path / "almacen", reloj),
        data_dir=data_dir,
        ttl_horas=24,
        retraso_demo=0.6,
        reloj=reloj,
    )
    monkeypatch.setenv("APP_ENV", "test")
    aplicacion = create_app()
    detalle = await servicio.solicitar(SolicitudExportacion(dataset=CONJUNTO), analista)

    transporte = httpx.ASGITransport(app=aplicacion)
    async with httpx.AsyncClient(transport=transporte, base_url="http://prueba") as red:

        async def sondear() -> tuple[int, float]:
            respuesta = await red.get("/health")
            return respuesta.status_code, time.perf_counter() - inicio

        inicio = time.perf_counter()
        _, (estado, latencia) = await asyncio.gather(
            servicio.ejecutar(detalle.job_id), sondear()
        )

    assert estado == 200
    assert latencia < 0.5
    assert repositorio.filas[detalle.job_id].status == EstadoTrabajo.COMPLETADO.value
    assert servicio.hilo_de_extraccion is not None
    assert servicio.hilo_de_extraccion != threading.get_ident()


@pytest.mark.asyncio
async def test_historial_no_filtra_trabajos_ajenos(
    servicio: ServicioQueAnotaElHilo,
    repositorio: RepositorioDeTrabajosEnMemoria,
    analista: UserOut,
    usuarios_semilla: dict[str, "AppUser"],
) -> None:
    """The history of one analyst never carries the job of another user.

    The defect is a ``SELECT`` that forgets its ``WHERE requested_by``. It is
    the cheapest leak this feature could ship: the history says what every
    other user of the portal has been extracting and when.

    Args:
        servicio: Service under test.
        repositorio: Job registry double.
        analista: Caller of the request.
        usuarios_semilla: Rows of the seven seeded users.
    """
    ajeno = next(
        usuario_de(usuario)
        for usuario in usuarios_semilla.values()
        if usuario.id != analista.id
    )
    propio_viejo = trabajo_pendiente(analista.id, creado=INICIO)
    propio_nuevo = trabajo_pendiente(analista.id, creado=INICIO + timedelta(minutes=5))
    for fila in (propio_viejo, propio_nuevo, trabajo_pendiente(ajeno.id)):
        await repositorio.crear(fila)

    historial = await servicio.historial(analista)

    assert [resumen.job_id for resumen in historial] == [
        propio_nuevo.id,
        propio_viejo.id,
    ]
    assert {resumen.solicitado_por for resumen in historial} == {analista.id}


@pytest.mark.asyncio
async def test_el_historial_de_un_admin_es_el_registro_completo(
    servicio: ServicioQueAnotaElHilo,
    repositorio: RepositorioDeTrabajosEnMemoria,
    analista: UserOut,
    administrador: UserOut,
) -> None:
    """Governance reads every job, and reads whose each one is.

    The defect is the history filtering by the caller for every role, which is
    what this module did until this case existed: an administrator would open
    the register of the portal and see only their own extractions, so the one
    role whose job is to audit what leaves the perimeter would be the role that
    cannot. The ownership assertion is half the case: a listing that returned
    every row without saying who asked for it would answer the question "what
    was extracted" and never "by whom", which is the question governance has.

    Args:
        servicio: Service under test.
        repositorio: Job registry double.
        analista: Owner of the older job.
        administrador: Caller of the request.
    """
    del_analista = trabajo_pendiente(analista.id, creado=INICIO)
    del_admin = trabajo_pendiente(
        administrador.id, creado=INICIO + timedelta(minutes=5)
    )
    for fila in (del_analista, del_admin):
        await repositorio.crear(fila)

    historial = await servicio.historial(administrador)

    assert [(resumen.job_id, resumen.solicitado_por) for resumen in historial] == [
        (del_admin.id, administrador.id),
        (del_analista.id, analista.id),
    ]


@pytest.mark.asyncio
async def test_el_historial_de_un_admin_no_reparte_enlaces(
    tmp_path: Path,
    reloj: RelojFijo,
    repositorio: RepositorioDeTrabajosEnMemoria,
    analista: UserOut,
    administrador: UserOut,
) -> None:
    """The register an administrator reads carries no link to anybody's file.

    Reading metadata is not reading data. The defect is a history that answers
    with the polled contract instead of the summary: every finished job of
    every user would arrive with a signed URL, and the rule that an
    administrator never downloads a foreign file -which ``resolver_descarga``
    still enforces- would be contradicted by the very list that offered it.

    Args:
        tmp_path: Directory of the test.
        reloj: Clock of the test.
        repositorio: Job registry double.
        analista: Owner of the finished job.
        administrador: Caller of the request.
    """
    data_dir = tmp_path / "data"
    sembrar_silo(data_dir)
    servicio = ExportService(
        repositorio=repositorio,
        almacen=crear_almacen_de_prueba(tmp_path / "almacen", reloj),
        data_dir=data_dir,
        ttl_horas=24,
        reloj=reloj,
    )
    detalle = await servicio.solicitar(SolicitudExportacion(dataset=CONJUNTO), analista)
    await servicio.ejecutar(detalle.job_id)

    historial = await servicio.historial(administrador)

    terminado = repositorio.filas[detalle.job_id]
    assert terminado.status == EstadoTrabajo.COMPLETADO.value
    assert terminado.object_key is not None
    assert [resumen.job_id for resumen in historial] == [detalle.job_id]
    cuerpo = historial[0].model_dump()
    assert "url_descarga" not in cuerpo
    assert "caduca_en" not in cuerpo
    assert terminado.object_key not in str(cuerpo)


@pytest.mark.asyncio
async def test_un_silo_ausente_cierra_el_trabajo_como_fallido(
    tmp_path: Path,
    reloj: RelojFijo,
    repositorio: RepositorioDeTrabajosEnMemoria,
    analista: UserOut,
) -> None:
    """A source that is not on disk fails the job instead of hanging it.

    The defect is an ``ejecutar`` that lets the exception escape the background
    task: the job would stay ``en_proceso`` forever, the polling store would
    keep asking for ten minutes and the analyst would never be told that the
    silo was never generated.

    Args:
        tmp_path: Directory of the test.
        reloj: Clock of the test.
        repositorio: Job registry double.
        analista: Owner of the job.
    """
    servicio = ExportService(
        repositorio=repositorio,
        almacen=crear_almacen_de_prueba(tmp_path / "almacen", reloj),
        data_dir=tmp_path / "vacio",
        ttl_horas=24,
        reloj=reloj,
    )
    detalle = await servicio.solicitar(SolicitudExportacion(dataset=CONJUNTO), analista)

    await servicio.ejecutar(detalle.job_id)

    fila = repositorio.filas[detalle.job_id]
    assert fila.status == EstadoTrabajo.FALLIDO.value
    assert fila.error_code == "origen_ausente"
    assert fila.finished_at is not None


@pytest.mark.asyncio
async def test_un_filtro_sobre_columna_inexistente_no_exporta_el_conjunto_entero(
    servicio: ServicioQueAnotaElHilo,
    repositorio: RepositorioDeTrabajosEnMemoria,
    analista: UserOut,
) -> None:
    """A filter naming a column the silo lacks fails; it is never ignored.

    The defect is a compiler that drops what it does not understand. The
    analyst would receive a complete file believing it was filtered, and the
    number they read from it would answer a question nobody asked.

    Args:
        servicio: Service under test.
        repositorio: Job registry double.
        analista: Owner of the job.
    """
    detalle = await servicio.solicitar(
        SolicitudExportacion(dataset=CONJUNTO, filtros={"moneda": "MXN"}), analista
    )

    await servicio.ejecutar(detalle.job_id)

    fila = repositorio.filas[detalle.job_id]
    assert fila.status == EstadoTrabajo.FALLIDO.value
    assert fila.error_code == "columna_desconocida"
    assert fila.row_count is None


@pytest.mark.asyncio
async def test_un_filtro_declarado_recorta_el_extracto(
    servicio: ServicioQueAnotaElHilo,
    repositorio: RepositorioDeTrabajosEnMemoria,
    analista: UserOut,
) -> None:
    """The declared filter reaches the file: fewer rows come out than went in.

    The defect is the mirror of the previous one: a known column accepted and
    then never applied, which is invisible unless somebody counts the rows.

    Args:
        servicio: Service under test.
        repositorio: Job registry double.
        analista: Owner of the job.
    """
    detalle = await servicio.solicitar(
        SolicitudExportacion(dataset=CONJUNTO, filtros={"sucursal": ["S00", "S01"]}),
        analista,
    )

    await servicio.ejecutar(detalle.job_id)

    # Derived from the same rule ``sembrar_silo`` writes with, so the expected
    # number is a count and not a constant somebody would adjust to fit.
    esperadas = sum(
        1 for indice in range(FILAS_DEL_SILO) if f"S{indice % 12:02d}" in ("S00", "S01")
    )
    fila = repositorio.filas[detalle.job_id]
    assert fila.status == EstadoTrabajo.COMPLETADO.value
    assert fila.row_count == esperadas
    assert esperadas < FILAS_DEL_SILO


@pytest.mark.parametrize(
    "filtros",
    [
        {f"columna_{indice}": "x" for indice in range(_FILTROS_MAXIMOS + 1)},
        {"suc_cd": ["S00"] * (_VALORES_MAXIMOS + 1)},
        {"nom_cli": "x" * (_LONGITUD_MAXIMA_DE_VALOR + 1)},
        {"c" * (_LONGITUD_MAXIMA_DE_COLUMNA + 1): "S00"},
        {"suc_cd": {"anidado": "S00"}},
        {"suc_cd": [["S00"]]},
        {"suc_cd": None},
    ],
    ids=[
        "demasiadas_columnas",
        "demasiados_valores",
        "un_valor_demasiado_largo",
        "un_nombre_de_columna_demasiado_largo",
        "un_objeto_anidado",
        "una_lista_de_listas",
        "un_nulo",
    ],
)
def test_el_contrato_de_filtros_rechaza_lo_que_no_deberia_persistirse(
    filtros: dict[str, Any],
) -> None:
    """Each shape the filter map has no business carrying is refused at the body.

    ``filtros`` was ``dict[str, Any]`` with no ceiling of any kind, and the
    first statement of the job writes it verbatim into a JSONB column: whatever
    the body declared is what the table stored, and nothing downstream ever
    looked at its size -the compiler reads the keys against the schema of the
    silo and the values into an ``is_in``, neither of which cares how many there
    are-. The seven cases are seven ways that was exploitable or simply wrong:
    the four ceilings, plus the three values ``Any`` allowed into a membership
    predicate that can only compare scalars.

    Args:
        filtros: Filter map that must not be accepted.
    """
    with pytest.raises(ValidationError):
        SolicitudExportacion(dataset=CONJUNTO, filtros=filtros)


@pytest.mark.parametrize(
    "filtros",
    [
        {},
        {"suc_cd": "S07"},
        {"suc_cd": ["S00", "S01"]},
        {"dias_mora": 30},
        {"ratio_lcr": 1.25},
        {"revolvente": True},
        {"suc_cd": ["S00"] * _VALORES_MAXIMOS},
    ],
    ids=[
        "sin_filtros",
        "un_valor",
        "una_lista",
        "un_entero",
        "un_decimal",
        "un_booleano",
        "la_lista_mas_larga_admitida",
    ],
)
def test_el_contrato_de_filtros_sigue_aceptando_lo_que_el_portal_envia(
    filtros: dict[str, Any],
) -> None:
    """Bounding the map must not narrow it below what the portal really sends.

    This is the other half of the ceiling and it fails on the likelier defect:
    a contract tightened until it refuses a legitimate request. The first three
    cases are literally what ``analizarFiltros`` of ``useExportaciones.ts``
    produces -a string, or a list of strings when the reader typed commas- and
    the next three are the JSON scalars a numeric or boolean column takes from a
    client or from the agent. The last one pins the boundary as inclusive: a
    ceiling written with the wrong comparison would refuse the exact size it
    publishes as allowed.

    Args:
        filtros: Filter map that must survive validation unchanged.
    """
    solicitud = SolicitudExportacion(dataset=CONJUNTO, filtros=filtros)

    assert solicitud.filtros == filtros


@pytest.mark.asyncio
async def test_un_diccionario_de_filtros_desmedido_no_llega_a_la_tabla(
    tmp_path: Path,
    reloj: RelojFijo,
    repositorio: RepositorioDeTrabajosEnMemoria,
    usuarios_semilla: dict[str, "AppUser"],
    repositorio_falso: "FakeUserRepository",
    token_de: Callable[..., str],
) -> None:
    """The ceiling runs before the insert, so the oversized body leaves no row.

    The case above proves the contract refuses the map; this one proves the
    refusal happens early enough to matter. A ceiling checked inside the service
    -after ``crear``, or as a defensive assertion in the extraction- would
    answer the same 422 to the caller and still have written the row it was
    supposed to prevent, which is the whole point of the finding: the map is
    persisted as JSONB by the first statement of the job. The registry double
    records every transition, so an insert that happened is visible here.

    Args:
        tmp_path: Directory of the test.
        reloj: Clock of the test.
        repositorio: Job registry double.
        usuarios_semilla: Rows of the seven seeded users.
        repositorio_falso: Read side of ``app_user``, doubled.
        token_de: Factory of signed tokens.
    """
    import httpx

    from app.main import create_app

    fila = next(
        usuario for usuario in usuarios_semilla.values() if usuario.role == "analista"
    )
    servicio = ExportService(
        repositorio=repositorio,
        almacen=crear_almacen_de_prueba(tmp_path / "almacen", reloj),
        data_dir=tmp_path / "data",
        ttl_horas=24,
        reloj=reloj,
    )
    aplicacion = create_app()
    aplicacion.dependency_overrides[get_user_repository] = lambda: repositorio_falso
    aplicacion.dependency_overrides[get_export_service] = lambda: servicio
    columnas = {f"columna_{indice}": "x" for indice in range(_FILTROS_MAXIMOS + 1)}
    cuerpo = {"dataset": CONJUNTO, "filtros": columnas}

    transporte = httpx.ASGITransport(app=aplicacion)
    async with httpx.AsyncClient(transport=transporte, base_url="http://prueba") as red:
        respuesta = await red.post(
            "/api/export",
            json=cuerpo,
            headers={"Authorization": f"Bearer {token_de(fila.username, 'analista')}"},
        )

    assert respuesta.status_code == 422
    assert repositorio.transiciones == []
    assert repositorio.filas == {}


@pytest.mark.asyncio
async def test_encolar_dos_veces_el_mismo_trabajo_lo_ejecuta_una_sola(
    servicio: ServicioQueAnotaElHilo,
    repositorio: RepositorioDeTrabajosEnMemoria,
    analista: UserOut,
) -> None:
    """A job that is no longer pending is not run again.

    The defect is a retry -a double click on the button, a task queued twice by
    a redeploy- that re-runs a finished extraction, overwrites its file and
    moves the deadline of a link somebody already holds.

    Args:
        servicio: Service under test.
        repositorio: Job registry double.
        analista: Owner of the job.
    """
    detalle = await servicio.solicitar(SolicitudExportacion(dataset=CONJUNTO), analista)
    await servicio.ejecutar(detalle.job_id)

    await servicio.ejecutar(detalle.job_id)

    assert repositorio.transiciones == [
        "crear",
        "marcar_en_proceso",
        "marcar_completado",
    ]


@pytest.mark.asyncio
async def test_un_trabajo_xlsx_deja_una_hoja_de_calculo_legible(
    servicio: ServicioQueAnotaElHilo,
    repositorio: RepositorioDeTrabajosEnMemoria,
    analista: UserOut,
    tmp_path: Path,
) -> None:
    """The spreadsheet format produces a spreadsheet, opened here to prove it.

    The file is read back as what it is -a zip archive of OOXML parts- and its
    sheet is counted, because the defect this replaces was believing the format
    worked on the evidence that the writer imported. A ``write_excel`` that
    silently produced an empty sheet, or one row per chunk, or a file with the
    right extension and nothing inside, would pass any check that only looked
    at the state of the job.

    Args:
        servicio: Service under test.
        repositorio: Job registry double.
        analista: Owner of the job.
        tmp_path: Directory of the test.
    """
    detalle = await servicio.solicitar(
        SolicitudExportacion(dataset=CONJUNTO, formato=FormatoExportacion.XLSX),
        analista,
    )

    await servicio.ejecutar(detalle.job_id)

    fila = repositorio.filas[detalle.job_id]
    assert fila.status == EstadoTrabajo.COMPLETADO.value
    assert fila.error_code is None
    assert fila.row_count == FILAS_DEL_SILO
    assert fila.object_key == f"{detalle.job_id}.xlsx"

    hoja = tmp_path / "almacen" / fila.object_key
    assert fila.byte_size == hoja.stat().st_size
    with zipfile.ZipFile(hoja) as libro:
        miembros = set(libro.namelist())
        contenido = libro.read("xl/worksheets/sheet1.xml").decode("utf-8")

    assert set(MIEMBROS_XLSX) <= miembros

    # One row of headers plus one row per exported record: the count of the job
    # and the count inside the sheet are the same number read two ways.
    assert contenido.count("<row ") == FILAS_DEL_SILO + 1


@pytest.mark.asyncio
async def test_la_hoja_de_calculo_no_toma_el_bucle_de_eventos(
    tmp_path: Path,
    reloj: RelojFijo,
    repositorio: RepositorioDeTrabajosEnMemoria,
    analista: UserOut,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The health probe answers while a spreadsheet is being written.

    The CSV case sinks in streaming; this one cannot, because a sheet is
    written in one pass and ``write_excel`` needs the frame materialised. That
    difference is exactly what makes the case worth its second: the defect is a
    ``collect`` plus ``write_excel`` left on the event loop, which would hold
    the whole API for as long as the spreadsheet takes, and the spreadsheet
    writer is pure Python and slow.

    The gate of 500 ms is asserted, and next to it something no machine can
    make ambiguous: the probe was answered before the job was half done. On a
    fast enough host the absolute latency alone could stay under the gate even
    with the work left on the loop.

    Args:
        tmp_path: Directory of the test.
        reloj: Clock of the test.
        repositorio: Job registry double.
        analista: Owner of the job.
        monkeypatch: Used to pin the environment of the application.
    """
    import httpx

    from app.main import create_app

    data_dir = tmp_path / "data"
    sembrar_silo(data_dir, filas=FILAS_DEL_SILO_XLSX)
    servicio = ServicioQueAnotaElHilo(
        repositorio=repositorio,
        almacen=crear_almacen_de_prueba(tmp_path / "almacen", reloj),
        data_dir=data_dir,
        ttl_horas=24,
        reloj=reloj,
    )
    monkeypatch.setenv("APP_ENV", "test")
    aplicacion = create_app()
    detalle = await servicio.solicitar(
        SolicitudExportacion(dataset=CONJUNTO, formato=FormatoExportacion.XLSX),
        analista,
    )

    transporte = httpx.ASGITransport(app=aplicacion)
    async with httpx.AsyncClient(transport=transporte, base_url="http://prueba") as red:

        async def exportar() -> float:
            comienzo = time.perf_counter()
            await servicio.ejecutar(detalle.job_id)
            return time.perf_counter() - comienzo

        async def sondear() -> tuple[int, float]:
            respuesta = await red.get("/health")
            return respuesta.status_code, time.perf_counter() - inicio

        inicio = time.perf_counter()
        duracion, (estado, latencia) = await asyncio.gather(exportar(), sondear())

    assert estado == 200
    assert latencia < 0.5
    assert latencia < duracion / 2
    assert repositorio.filas[detalle.job_id].status == EstadoTrabajo.COMPLETADO.value
    assert servicio.hilo_de_extraccion is not None
    assert servicio.hilo_de_extraccion != threading.get_ident()


@pytest.mark.asyncio
async def test_una_hoja_por_encima_del_limite_no_se_materializa(
    tmp_path: Path,
    reloj: RelojFijo,
    repositorio: RepositorioDeTrabajosEnMemoria,
    analista: UserOut,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A result too big for a spreadsheet is refused before it is loaded.

    The limit exists because the writer misses the health gate long before the
    format runs out of rows: the million rows of ``liquidez`` measured 61,6 s
    and stalled the event loop for 997 ms, against a gate of 500 ms.

    The defect is an order of operations: counting after materialising, or not
    counting at all. The job would still end as failed, so the state alone
    proves nothing; what proves it is that no frame of data was ever collected.
    Every ``collect`` of the run is spied on, and the only one allowed to
    happen is the single row of the count.

    Args:
        tmp_path: Directory of the test.
        reloj: Clock of the test.
        repositorio: Job registry double.
        analista: Owner of the job.
        monkeypatch: Used to spy on the materialisation.
    """
    data_dir = tmp_path / "data"
    sembrar_silo(data_dir, filas=_FILAS_MAXIMAS_XLSX + 1)
    servicio = ExportService(
        repositorio=repositorio,
        almacen=crear_almacen_de_prueba(tmp_path / "almacen", reloj),
        data_dir=data_dir,
        ttl_horas=24,
        reloj=reloj,
    )
    alturas: list[int] = []
    recolectar = pl.LazyFrame.collect

    def espiar(self: pl.LazyFrame) -> pl.DataFrame:
        """Run the real collect and record how much data it brought back.

        Args:
            self: Plan being materialised.

        Returns:
            What the real ``collect`` returned.
        """
        marco = recolectar(self)
        alturas.append(marco.height)
        return marco

    monkeypatch.setattr(pl.LazyFrame, "collect", espiar)
    detalle = await servicio.solicitar(
        SolicitudExportacion(dataset=CONJUNTO, formato=FormatoExportacion.XLSX),
        analista,
    )

    await servicio.ejecutar(detalle.job_id)

    fila = repositorio.filas[detalle.job_id]
    assert fila.status == EstadoTrabajo.FALLIDO.value
    assert fila.error_code == "formato_no_disponible"
    assert fila.row_count is None
    assert fila.object_key is None
    assert alturas == [1]
    assert not list((tmp_path / "almacen").glob("*"))


@pytest.mark.asyncio
async def test_sin_escritor_de_xlsx_el_trabajo_falla_con_codigo(
    servicio: ServicioQueAnotaElHilo,
    repositorio: RepositorioDeTrabajosEnMemoria,
    analista: UserOut,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Without the writer the format degrades into a closed job, not a traceback.

    The package now travels as an extra of the pinned Polars, so the guard is a
    safety net for an environment somebody assembled by hand. The absence is
    simulated at the only place the code asks about it, and the defect is
    removing the guard on the grounds that the dependency is now declared: the
    ``ImportError`` would surface inside a background task, after the response
    was already sent, and the job would stay in progress with nothing
    explaining why.

    Args:
        servicio: Service under test.
        repositorio: Job registry double.
        analista: Owner of the job.
        monkeypatch: Used to hide the writer from the module.
    """
    buscar = importlib.util.find_spec

    def sin_xlsxwriter(
        nombre: str, paquete: str | None = None
    ) -> importlib.machinery.ModuleSpec | None:
        """Answer as an installation without the spreadsheet writer would.

        Args:
            nombre: Module being looked up.
            paquete: Anchor of a relative lookup.

        Returns:
            The real specification, except for the writer, which is absent.
        """
        return None if nombre == "xlsxwriter" else buscar(nombre, paquete)

    monkeypatch.setattr(importlib.util, "find_spec", sin_xlsxwriter)
    detalle = await servicio.solicitar(
        SolicitudExportacion(dataset=CONJUNTO, formato=FormatoExportacion.XLSX),
        analista,
    )

    await servicio.ejecutar(detalle.job_id)

    fila = repositorio.filas[detalle.job_id]
    assert fila.status == EstadoTrabajo.FALLIDO.value
    assert fila.error_code == "formato_no_disponible"
    assert fila.object_key is None


@pytest.mark.asyncio
async def test_un_registro_que_no_cierra_no_derriba_la_tarea_de_fondo(
    servicio: ServicioQueAnotaElHilo,
    repositorio: RepositorioDeTrabajosEnMemoria,
    analista: UserOut,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """When even the failure cannot be written, nothing escapes upwards.

    The defect is an exception raised while closing a job that already failed.
    It would leave the background task with an unhandled error long after the
    202 was answered, and nothing downstream could do anything with it.

    Args:
        servicio: Service under test.
        repositorio: Job registry double.
        analista: Owner of the job.
        monkeypatch: Used to break the closing write.
    """

    async def caerse(*_: object, **__: object) -> None:
        message = "el registro de trabajos dejo de responder"
        raise RuntimeError(message)

    detalle = await servicio.solicitar(SolicitudExportacion(dataset=CONJUNTO), analista)
    monkeypatch.setattr(servicio, "_data_dir", Path("no-existe"))
    monkeypatch.setattr(repositorio, "marcar_fallido", caerse)

    await servicio.ejecutar(detalle.job_id)

    assert repositorio.filas[detalle.job_id].status == EstadoTrabajo.EN_PROCESO.value


class SesionDoble:
    """Double of ``AsyncSession`` that records statements and mutations.

    It exists so the statements of ``SqlTrabajoRepository`` can be compiled and
    read without a server. The rows it serves are irrelevant: what is being
    interrogated is the SQL the repository builds, and that is checked against
    the PostgreSQL dialect and not against this class.

    Attributes:
        filas: Rows indexed by primary key.
        sentencias: Statements handed to ``exec``, in order.
        agregados: Rows added to the session.
        confirmaciones: Number of commits requested.
        reversiones: Number of rollbacks requested.
    """

    def __init__(self, filas: Sequence[ExportJob] = ()) -> None:
        """Store the rows this session will serve.

        Args:
            filas: Rows already in the table.
        """
        self.filas: dict[uuid.UUID, ExportJob] = {
            fila.id: fila for fila in filas if fila.id is not None
        }
        self.sentencias: list[Any] = []
        self.agregados: list[ExportJob] = []
        self.confirmaciones = 0
        self.reversiones = 0

    async def get(self, modelo: object, clave: uuid.UUID) -> ExportJob | None:
        """Return one row by primary key.

        Args:
            modelo: Mapped class, ignored.
            clave: Primary key.

        Returns:
            The row, or ``None``.
        """
        return self.filas.get(clave)

    async def exec(self, sentencia: Executable) -> "_ResultadoDoble":
        """Record the statement and answer with every row.

        Args:
            sentencia: Statement built by the repository.

        Returns:
            The rows of the table.
        """
        self.sentencias.append(sentencia)
        return _ResultadoDoble(list(self.filas.values()))

    def add(self, instancia: ExportJob) -> None:
        """Record a row added to the session.

        Args:
            instancia: Row handed to the session.
        """
        self.agregados.append(instancia)

    async def commit(self) -> None:
        """Record a commit."""
        self.confirmaciones += 1

    async def rollback(self) -> None:
        """Record a rollback.

        A real ``AsyncSession`` is left in a transaction that refuses every
        further statement once one of them failed, so the repository has to roll
        it back before anybody reuses it. The counter is what lets a case assert
        that it did.
        """
        self.reversiones += 1


class _ResultadoDoble:
    """Result of the doubled ``exec``."""

    def __init__(self, filas: list[ExportJob]) -> None:
        """Store the rows.

        Args:
            filas: Rows to serve.
        """
        self._filas = filas

    def all(self) -> list[ExportJob]:
        """Return every row.

        Returns:
            The rows.
        """
        return self._filas


@pytest.mark.asyncio
async def test_el_historial_sql_filtra_por_propietario_y_ordena(
    analista: UserOut,
) -> None:
    """The listing statement carries its owner filter, its order and its limit.

    The service case above shows that a caller only sees their own jobs against
    a double that filters in Python; this one reads the SQL that will run in
    production. The defect is the same and it is the expensive one -a SELECT
    without its owner predicate- but only here would it be caught before a
    database exists to notice.

    Args:
        analista: Owner whose history is listed.
    """
    from sqlalchemy.dialects.postgresql.base import PGDialect

    sesion = SesionDoble()
    repositorio = SqlTrabajoRepository(cast("AsyncSession", sesion))

    await repositorio.listar(requested_by=analista.id, limite=7)

    # SQLAlchemy ships no annotations for its dialect constructors, so the
    # silencer is scoped to the one call that builds the PostgreSQL one.
    dialecto = PGDialect()  # type: ignore[no-untyped-call]
    sql = str(sesion.sentencias[0].compile(dialect=dialecto))
    assert "WHERE export_job.requested_by =" in sql
    assert "ORDER BY export_job.created_at DESC" in sql
    assert "LIMIT" in sql


@pytest.mark.asyncio
async def test_el_historial_de_gobierno_sql_no_lleva_filtro_y_sigue_acotado() -> None:
    """The statement without an owner filter is the only one without one.

    Two defects meet here. One is a governance listing that kept a filter and
    would show an administrator their own jobs while claiming to show the
    register. The other is the expensive one and is why this statement is a
    method of its own: an unbounded ``SELECT`` over a growing table, read in a
    request. The order and the limit are asserted for that reason.
    """
    from sqlalchemy.dialects.postgresql.base import PGDialect

    sesion = SesionDoble()
    repositorio = SqlTrabajoRepository(cast("AsyncSession", sesion))

    await repositorio.listar_todos(limite=7)

    dialecto = PGDialect()  # type: ignore[no-untyped-call]
    sql = str(sesion.sentencias[0].compile(dialect=dialecto))
    assert "WHERE" not in sql
    assert "ORDER BY export_job.created_at DESC" in sql
    assert "LIMIT" in sql


@pytest.mark.asyncio
async def test_las_transiciones_sql_escriben_lo_que_exige_el_constraint(
    analista: UserOut,
) -> None:
    """Each state change writes every column its CHECK demands, and commits.

    The migration refuses a completed job without object key, expiry and end
    instant, and a failed one without a code. The defect is a transition that
    writes the state and forgets one of them: the row would be rejected by the
    database at run time, inside a background task, where nobody is looking.

    Args:
        analista: Owner of the jobs.
    """
    pendiente = trabajo_pendiente(analista.id)
    fallido = trabajo_pendiente(analista.id)
    sesion = SesionDoble([pendiente, fallido])
    repositorio = SqlTrabajoRepository(cast("AsyncSession", sesion))
    assert pendiente.id is not None
    assert fallido.id is not None

    nuevo = trabajo_pendiente(analista.id)
    insertado = await repositorio.crear(nuevo)
    en_proceso = await repositorio.marcar_en_proceso(pendiente.id, iniciado=INICIO)
    completado = await repositorio.marcar_completado(
        pendiente.id,
        object_key=f"{pendiente.id}.csv",
        filas=11,
        tamano_bytes=222,
        terminado=INICIO + timedelta(seconds=9),
        caduca=INICIO + timedelta(hours=24),
    )
    cerrado = await repositorio.marcar_fallido(
        fallido.id, error_code="origen_ausente", terminado=INICIO
    )

    assert insertado is nuevo
    assert sesion.agregados[0] is nuevo
    assert en_proceso is not None
    assert en_proceso.started_at == INICIO
    assert completado is not None
    assert completado.status == EstadoTrabajo.COMPLETADO.value
    assert completado.object_key is not None
    assert completado.expires_at is not None
    assert completado.finished_at is not None
    assert (completado.row_count, completado.byte_size) == (11, 222)
    assert cerrado is not None
    assert cerrado.error_code == "origen_ausente"
    assert cerrado.finished_at == INICIO
    assert sesion.confirmaciones == 4


@pytest.mark.asyncio
async def test_las_transiciones_sql_sobre_un_trabajo_que_no_esta(
    analista: UserOut,
) -> None:
    """A transition that matches no row answers None instead of writing.

    The defect is a repository that creates or resurrects the job it was asked
    to update: a stale queue or a wrong identifier would silently produce a row
    nobody requested. The second call also shows the compare and set: a job
    that is no longer pending is not taken again.

    Args:
        analista: Owner used only to build the rows.
    """
    completado = trabajo_pendiente(analista.id)
    completado.status = EstadoTrabajo.COMPLETADO.value
    sesion = SesionDoble([completado])
    repositorio = SqlTrabajoRepository(cast("AsyncSession", sesion))
    ausente = uuid.uuid4()
    assert completado.id is not None

    sin_fila = await repositorio.marcar_completado(
        ausente,
        object_key="x.csv",
        filas=0,
        tamano_bytes=0,
        terminado=INICIO,
        caduca=INICIO,
    )
    sin_cierre = await repositorio.marcar_fallido(
        ausente, error_code="fallo_interno", terminado=INICIO
    )

    assert await repositorio.obtener(ausente) is None
    assert await repositorio.marcar_en_proceso(ausente, iniciado=INICIO) is None
    assert await repositorio.marcar_en_proceso(completado.id, iniciado=INICIO) is None
    assert sin_fila is None
    assert sin_cierre is None
    assert sesion.confirmaciones == 0


@pytest.mark.asyncio
async def test_una_base_inalcanzable_es_un_fallo_tipado_y_no_un_stack(
    analista: UserOut,
) -> None:
    """A connection that is not there becomes the typed failure of this domain.

    On a service that scales to zero the registry really is unreachable now and
    then. The defect is letting the raw driver error travel upwards: the
    history screen would answer a 500 with a stack trace instead of the empty
    state that was designed for exactly this.

    Args:
        analista: Owner whose job is inserted.
    """
    from sqlalchemy.exc import OperationalError

    class SesionCaida(SesionDoble):
        """Session that cannot reach the server on any read."""

        async def get(self, modelo: object, clave: uuid.UUID) -> ExportJob | None:
            """Fail the way psycopg fails when nothing answers.

            Args:
                modelo: Mapped class, ignored.
                clave: Primary key, ignored.

            Raises:
                OperationalError: Always.
            """
            raise OperationalError("SELECT 1", {}, Exception("no hay servidor"))

        async def exec(self, sentencia: Executable) -> "_ResultadoDoble":
            """Fail the same way on the statements the history runs.

            Args:
                sentencia: Statement that will never be sent.

            Raises:
                OperationalError: Always.
            """
            raise OperationalError("SELECT 1", {}, Exception("no hay servidor"))

    repositorio = SqlTrabajoRepository(cast("AsyncSession", SesionCaida()))

    with pytest.raises(TrabajosNoDisponiblesError):
        await repositorio.obtener(uuid.uuid4())

    # Each statement carries its own translation, so a method that forgets it
    # answers a 500 with a stack trace where the screen has an empty state.
    with pytest.raises(TrabajosNoDisponiblesError):
        await repositorio.listar(requested_by=analista.id, limite=1)
    with pytest.raises(TrabajosNoDisponiblesError):
        await repositorio.listar_todos(limite=1)


@pytest.mark.asyncio
async def test_una_reversion_que_tambien_falla_no_tapa_el_fallo_tipado() -> None:
    """A rollback that fails must not replace the failure it was cleaning up after.

    The rollback exists so the session survives a connection error, and it runs
    in the one situation where it can fail for the same reason the statement
    did: the connection is already gone. The defect is letting that second
    failure travel upwards. It would arrive as a driver exception nobody catches
    -so a 500 with a stack trace where the export screen has a designed empty
    state- and it would do it while hiding the cause, since what actually
    happened is that the registry is unreachable, which is exactly what the
    typed failure says.
    """
    from sqlalchemy.exc import OperationalError

    class SesionQueNiRevierte(SesionDoble):
        """Session whose connection is gone for reads and for rollbacks alike."""

        async def get(self, modelo: object, clave: uuid.UUID) -> ExportJob | None:
            """Fail the way psycopg fails when nothing answers.

            Args:
                modelo: Mapped class, ignored.
                clave: Primary key, ignored.

            Raises:
                OperationalError: Always.
            """
            raise OperationalError("SELECT 1", {}, Exception("no hay servidor"))

        async def rollback(self) -> None:
            """Fail as well, the way a rollback on a dead connection can.

            Raises:
                RuntimeError: Always.
            """
            message = "la conexion ya no admite ni la reversion"
            raise RuntimeError(message)

    repositorio = SqlTrabajoRepository(cast("AsyncSession", SesionQueNiRevierte()))

    with pytest.raises(TrabajosNoDisponiblesError):
        await repositorio.obtener(uuid.uuid4())


@pytest.mark.asyncio
async def test_una_sesion_sucia_no_deja_el_trabajo_colgado_en_proceso(
    tmp_path: Path,
    reloj: RelojFijo,
    analista: UserOut,
) -> None:
    """After a failed statement the recovery write still closes the job.

    This is the case the in-memory registry cannot express, because a dictionary
    has no transaction. A real ``AsyncSession`` does: once a statement fails, the
    session refuses every further one with ``PendingRollbackError`` until
    somebody rolls it back, and that exception is not a connection error, so
    nothing in this module translates it.

    The defect is a repository that turns the connection failure into
    ``TrabajosNoDisponiblesError`` and hands the session back poisoned. The
    background task catches that failure and calls ``_fallar`` on the very same
    session, the closing write is refused, and the job stays ``en_proceso``
    forever: the interface polls it to its two hundred attempt ceiling and the
    analyst is never told anything. It is the worst end state of this feature
    and the only one no user can get out of.

    The session double fails the second read -the one ``marcar_completado``
    makes after the file was already produced- and then behaves the way
    SQLAlchemy does, which is what makes the assertion on ``reversiones``
    meaningful rather than decorative: without the rollback the terminal write
    never lands.

    Args:
        tmp_path: Directory of the test.
        reloj: Clock of the test.
        analista: Owner of the job.
    """
    from sqlalchemy.exc import OperationalError, PendingRollbackError

    class SesionQueSeEnsucia(SesionDoble):
        """Session that fails one read and refuses everything until a rollback.

        Attributes:
            sucia: Whether a statement failed and nobody rolled back yet.
        """

        def __init__(self, filas: Sequence[ExportJob], *, falla_en: int) -> None:
            """Bind the double to the read it fails on.

            Args:
                filas: Rows already in the table.
                falla_en: Ordinal of the read that loses the connection.
            """
            super().__init__(filas)
            self._falla_en = falla_en
            self._lecturas = 0
            self.sucia = False

        def _exigir_transaccion_limpia(self) -> None:
            """Refuse to work while the failed transaction is still open.

            Raises:
                PendingRollbackError: If nobody rolled the session back.
            """
            if self.sucia:
                message = "no se puede reconectar hasta revertir la transaccion"
                raise PendingRollbackError(message)

        async def get(self, modelo: object, clave: uuid.UUID) -> ExportJob | None:
            """Serve the row, unless this is the read that loses the server.

            Args:
                modelo: Mapped class, ignored.
                clave: Primary key.

            Returns:
                The row, or ``None``.

            Raises:
                OperationalError: On the read the case makes fail.
            """
            self._exigir_transaccion_limpia()
            self._lecturas += 1
            if self._lecturas == self._falla_en:
                self.sucia = True
                raise OperationalError("SELECT 1", {}, Exception("no hay servidor"))
            return await super().get(modelo, clave)

        async def commit(self) -> None:
            """Commit, unless the transaction is still waiting for a rollback."""
            self._exigir_transaccion_limpia()
            await super().commit()

        async def rollback(self) -> None:
            """Make the session usable again, the way a real rollback does."""
            self.sucia = False
            await super().rollback()

    data_dir = tmp_path / "data"
    sembrar_silo(data_dir)
    pendiente = trabajo_pendiente(analista.id)
    assert pendiente.id is not None
    sesion = SesionQueSeEnsucia([pendiente], falla_en=2)
    servicio = ExportService(
        repositorio=SqlTrabajoRepository(cast("AsyncSession", sesion)),
        almacen=crear_almacen_de_prueba(tmp_path / "almacen", reloj),
        data_dir=data_dir,
        ttl_horas=24,
        reloj=reloj,
    )

    await servicio.ejecutar(pendiente.id)

    assert sesion.reversiones == 1
    assert pendiente.status == EstadoTrabajo.FALLIDO.value
    assert pendiente.error_code == "fallo_interno"
    assert pendiente.finished_at is not None


class RegistroCaido(RepositorioDeTrabajosEnMemoria):
    """Registry double that is unreachable for every operation of the router."""

    async def crear(self, trabajo: ExportJob) -> ExportJob:
        """Fail instead of inserting.

        Args:
            trabajo: Row that will not be written.

        Raises:
            TrabajosNoDisponiblesError: Always.
        """
        raise TrabajosNoDisponiblesError(_REGISTRO_CAIDO)

    async def obtener(self, job_id: uuid.UUID) -> ExportJob | None:
        """Fail instead of reading.

        Args:
            job_id: Identifier that will not be looked up.

        Raises:
            TrabajosNoDisponiblesError: Always.
        """
        raise TrabajosNoDisponiblesError(_REGISTRO_CAIDO)

    async def listar(
        self, *, requested_by: uuid.UUID, limite: int
    ) -> Sequence[ExportJob]:
        """Fail instead of listing.

        Args:
            requested_by: Owner that will not be looked up.
            limite: Page size, ignored.

        Raises:
            TrabajosNoDisponiblesError: Always.
        """
        raise TrabajosNoDisponiblesError(_REGISTRO_CAIDO)

    async def listar_todos(self, *, limite: int) -> Sequence[ExportJob]:
        """Fail instead of listing the whole register.

        Args:
            limite: Page size, ignored.

        Raises:
            TrabajosNoDisponiblesError: Always.
        """
        raise TrabajosNoDisponiblesError(_REGISTRO_CAIDO)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("metodo", "ruta", "cuerpo", "rol"),
    [
        ("POST", "/api/export", {"dataset": CONJUNTO}, "analista"),
        ("GET", "/api/export", None, "analista"),
        ("GET", "/api/export", None, "admin"),
        ("GET", f"/api/export/{uuid.uuid4()}", None, "analista"),
        (
            "GET",
            f"/api/export/{uuid.uuid4()}/download?exp=1&sig={'a' * 64}",
            None,
            "analista",
        ),
    ],
    ids=["solicitar", "historial", "historial_de_gobierno", "estado", "descarga"],
)
async def test_un_registro_inalcanzable_se_publica_como_503(
    tmp_path: Path,
    reloj: RelojFijo,
    usuarios_semilla: dict[str, "AppUser"],
    repositorio_falso: "FakeUserRepository",
    token_de: Callable[..., str],
    metodo: str,
    ruta: str,
    cuerpo: dict[str, Any] | None,
    rol: str,
) -> None:
    """An unreachable registry is a 503 with a code, not a 500 with a trace.

    The defect is a router that lets the failure of the store escape as an
    unhandled exception. The export screen would show a stack trace where it
    has an empty state, and the interface would have no stable code to key its
    copy on -it is bilingual and owns the copy, so a sentence is useless to it.

    Args:
        tmp_path: Directory of the test.
        reloj: Clock of the test.
        usuarios_semilla: Rows of the seven seeded users.
        repositorio_falso: Read side of ``app_user``, doubled.
        token_de: Factory of signed tokens.
        metodo: HTTP method under test.
        ruta: Relative URL under test.
        cuerpo: JSON body, if any.
        rol: Role the request is made with. The history is asked twice, once
            per branch: the governance one reads a different statement, so a
            translation missing there would be a 500 the filtered branch never
            shows.
    """
    import httpx

    from app.main import create_app

    fila = next(usuario for usuario in usuarios_semilla.values() if usuario.role == rol)
    servicio = ExportService(
        repositorio=RegistroCaido(),
        almacen=crear_almacen_de_prueba(tmp_path / "almacen", reloj),
        data_dir=tmp_path / "data",
        ttl_horas=24,
        reloj=reloj,
    )
    aplicacion = create_app()
    aplicacion.dependency_overrides[get_user_repository] = lambda: repositorio_falso
    aplicacion.dependency_overrides[get_export_service] = lambda: servicio

    transporte = httpx.ASGITransport(app=aplicacion)
    async with httpx.AsyncClient(transport=transporte, base_url="http://prueba") as red:
        respuesta = await red.request(
            metodo,
            ruta,
            json=cuerpo,
            headers={"Authorization": f"Bearer {token_de(fila.username, rol)}"},
        )

    assert respuesta.status_code == 503
    assert respuesta.json() == {"detail": {"codigo": "trabajos_no_disponibles"}}


class AlmacenQueSeNiega:
    """Storage that refuses every file, the way a full disk would."""

    async def guardar(self, job_id: uuid.UUID, origen: Path, formato: str) -> str:
        """Refuse to keep the file.

        Args:
            job_id: Identifier of the job.
            origen: Path of the produced file.
            formato: Output format code.

        Raises:
            RuntimeError: Always.
        """
        message = "el almacen rechazo el archivo"
        raise RuntimeError(message)

    def url_firmada(self, object_key: str, emitido: datetime) -> tuple[str, datetime]:
        """Refuse to mint a link, since nothing was ever kept.

        Args:
            object_key: Key that does not exist.
            emitido: Instant the lifetime would be counted from.

        Raises:
            RuntimeError: Always.
        """
        message = "este almacen nunca llega a firmar"
        raise RuntimeError(message)


@pytest.mark.asyncio
async def test_un_fallo_inesperado_del_almacen_tambien_cierra_el_trabajo(
    tmp_path: Path,
    reloj: RelojFijo,
    repositorio: RepositorioDeTrabajosEnMemoria,
    analista: UserOut,
) -> None:
    """A failure nobody classified still ends the job, with a generic code.

    The typed failures of the extraction are the ones that were foreseen. This
    covers the other half: a disk that fills up, a bucket that refuses the
    upload, anything the storage raises that this module never named. Without
    the catch-all the job would stay in progress forever and the exception
    would surface inside a background task, long after the 202 was answered.

    Args:
        tmp_path: Directory of the test.
        reloj: Clock of the test.
        repositorio: Job registry double.
        analista: Owner of the job.
    """
    data_dir = tmp_path / "data"
    sembrar_silo(data_dir)
    servicio = ExportService(
        repositorio=repositorio,
        almacen=AlmacenQueSeNiega(),
        data_dir=data_dir,
        ttl_horas=24,
        reloj=reloj,
    )
    detalle = await servicio.solicitar(SolicitudExportacion(dataset=CONJUNTO), analista)

    await servicio.ejecutar(detalle.job_id)

    fila = repositorio.filas[detalle.job_id]
    assert fila.status == EstadoTrabajo.FALLIDO.value
    assert fila.error_code == "fallo_interno"
