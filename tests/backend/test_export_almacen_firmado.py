"""The twenty four hours of the download link, verified without waiting them.

The acceptance criterion is a link that expires. Proving it by sleeping for a
day proves nothing anybody will run, so the clock is injected and the cases move
it: sign at ``T``, ask at ``T + 23 h 59 m`` and at ``T + 24 h 01 m``, and tamper
with the signature. No network is touched and no second is spent waiting.

The three cases go through HTTP because the answer under test is a status code:
410 for a link that died of old age and 403 for one that was never ours. A unit
call to ``verificar`` would assert the exception and say nothing about the two
codes the interface keys its copy on.

The doubles of the job registry and the clock are imported from
``test_export_endpoint``: they belong to this feature and not to the shared
``conftest.py``, which is the write-set of another User Story.
"""

import inspect
import uuid
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import TYPE_CHECKING, Final

import httpx
import pytest
from fastapi import FastAPI
from test_export_endpoint import (
    CONJUNTO,
    INICIO,
    RelojFijo,
    RepositorioDeTrabajosEnMemoria,
    crear_almacen_de_prueba,
    sembrar_silo,
    usuario_de,
)

from app.core.config import Settings
from app.models.export import SolicitudExportacion
from app.models.user import UserOut
from app.services.almacen import (
    AlmacenDeExportaciones,
    FirmaInvalida,
    crear_almacen,
    derivar_clave_de_firma,
)
from app.services.almacen.gcs import AlmacenGCS
from app.services.almacen.local import AlmacenLocalFirmado
from app.services.export_service import (
    ExportService,
    TrabajoNoEncontradoError,
    get_export_service,
)
from app.services.user_service import get_user_repository

if TYPE_CHECKING:
    from conftest import FakeUserRepository

    from app.models.user import AppUser

# Root of the repository, reached from this file so the count of the single
# point of choice does not depend on the working directory of the runner.
RAIZ: Final[Path] = Path(__file__).resolve().parents[2]

# Members of the storage facade, with the parameter names each one promises.
# Two implementations answering to the same shape is what the facade is for.
_SUPERFICIE: Final[dict[str, tuple[str, ...]]] = {
    "guardar": ("job_id", "origen", "formato"),
    "url_firmada": ("object_key", "emitido"),
}

_URL_FIRMADA_DE_PRUEBA: Final[str] = "https://storage.example/exportacion-firmada"

# Characters a hex digest of the portal has, so that the case below is about
# the alphabet of the signature and never about its length.
_LARGO_DE_FIRMA: Final[int] = 64

# A signature of exactly that length written outside ASCII, which is what a
# value copied from a document that replaced characters, or edited by hand,
# looks like on the wire. It is the one input that used to reach
# ``hmac.compare_digest`` and make it raise instead of answer.
_FIRMA_DEL_ALFABETO_AJENO: Final[str] = "ñ" * _LARGO_DE_FIRMA


@dataclass
class Escenario:
    """Everything one signed link case needs, already wired together.

    Attributes:
        servicio: Service under test, with a real local storage behind it.
        almacen: The local storage itself, so a case can delete a file.
        reloj: Clock the cases move by hand.
        repositorio: Job registry double.
        aplicacion: Real application, with the two seams substituted.
        analista: Owner of the job.
        token: Access token of that analyst.
    """

    servicio: ExportService
    almacen: AlmacenLocalFirmado
    reloj: RelojFijo
    repositorio: RepositorioDeTrabajosEnMemoria
    aplicacion: FastAPI
    analista: UserOut
    token: str


@pytest.fixture
def escenario(
    tmp_path: Path,
    usuarios_semilla: dict[str, "AppUser"],
    repositorio_falso: "FakeUserRepository",
    token_de: Callable[..., str],
) -> Iterator[Escenario]:
    """Build the application, the service and the token of one case.

    Args:
        tmp_path: Directory of the test.
        usuarios_semilla: Rows of the seven seeded users.
        repositorio_falso: Read side of ``app_user``, doubled.
        token_de: Factory of signed tokens from the shared conftest.

    Yields:
        The wired scenario.
    """
    from app.main import create_app

    fila = next(
        usuario for usuario in usuarios_semilla.values() if usuario.role == "analista"
    )
    analista = usuario_de(fila)

    reloj = RelojFijo()
    repositorio = RepositorioDeTrabajosEnMemoria()
    data_dir = tmp_path / "data"
    sembrar_silo(data_dir)
    almacen = crear_almacen_de_prueba(tmp_path / "almacen", reloj)
    servicio = ExportService(
        repositorio=repositorio,
        almacen=almacen,
        data_dir=data_dir,
        ttl_horas=24,
        reloj=reloj,
    )

    aplicacion = create_app()
    aplicacion.dependency_overrides[get_user_repository] = lambda: repositorio_falso
    aplicacion.dependency_overrides[get_export_service] = lambda: servicio

    yield Escenario(
        servicio=servicio,
        almacen=almacen,
        reloj=reloj,
        repositorio=repositorio,
        aplicacion=aplicacion,
        analista=analista,
        token=token_de(fila.username, "analista"),
    )


async def enlace_de(escenario: Escenario) -> tuple[uuid.UUID, str]:
    """Run one export to completion and return the link it minted.

    Args:
        escenario: Wired scenario.

    Returns:
        The identifier of the job and its signed relative URL.
    """
    detalle = await escenario.servicio.solicitar(
        SolicitudExportacion(dataset=CONJUNTO), escenario.analista
    )
    await escenario.servicio.ejecutar(detalle.job_id)
    listo = await escenario.servicio.consultar(detalle.job_id, escenario.analista)

    assert listo.url_descarga is not None
    assert listo.caduca_en == escenario.reloj.ahora() + timedelta(hours=24)
    return detalle.job_id, listo.url_descarga


async def pedir(escenario: Escenario, url: str) -> httpx.Response:
    """Request a signed URL against the real application.

    Args:
        escenario: Wired scenario.
        url: Relative URL, signature included.

    Returns:
        The answer of the portal.
    """
    transporte = httpx.ASGITransport(app=escenario.aplicacion)
    async with httpx.AsyncClient(transport=transporte, base_url="http://prueba") as red:
        return await red.get(
            url, headers={"Authorization": f"Bearer {escenario.token}"}
        )


@pytest.mark.asyncio
async def test_enlace_valido_antes_de_24h(escenario: Escenario, tmp_path: Path) -> None:
    """One minute before the deadline the file is still served.

    The defect that fails here is an expiry computed in the wrong unit or in
    local time instead of UTC: the link would be dead before it was ever handed
    to anybody, and the feature would look broken with a correct signature.

    Args:
        escenario: Wired scenario.
        tmp_path: Directory of the test.
    """
    job_id, url = await enlace_de(escenario)
    escenario.reloj.avanzar(timedelta(hours=23, minutes=59))

    respuesta = await pedir(escenario, url)

    guardado = (tmp_path / "almacen" / f"{job_id}.csv").read_bytes()
    assert respuesta.status_code == 200
    assert respuesta.content == guardado
    assert respuesta.headers["content-type"].startswith("text/csv")


@pytest.mark.asyncio
async def test_enlace_caduca_a_las_24h(escenario: Escenario) -> None:
    """One minute after the deadline the same link is gone.

    This is the case that separates a real expiry from a decorative one. It
    fails whenever the deadline travels in the URL but not inside the signed
    material, or when nobody compares it against a clock: the classic link
    "with expiry" that never expires.

    Args:
        escenario: Wired scenario.
    """
    _, url = await enlace_de(escenario)
    escenario.reloj.avanzar(timedelta(hours=24, minutes=1))

    respuesta = await pedir(escenario, url)

    assert respuesta.status_code == 410
    assert respuesta.json()["detail"]["codigo"] == "enlace_caducado"


@pytest.mark.asyncio
async def test_firma_alterada_es_rechazada(escenario: Escenario) -> None:
    """A signature this portal did not produce is refused, deadline or not.

    It fails on a comparison written with ``==`` only through the timing it
    leaks, so what this case really nails is the other half: a check that looks
    at the length of the signature, or at nothing at all, and lets an edited
    link through while it is still fresh.

    Args:
        escenario: Wired scenario.
    """
    _, url = await enlace_de(escenario)
    base, _, firma = url.partition("&sig=")
    alterada = ("0" if firma[0] != "0" else "1") + firma[1:]

    respuesta = await pedir(escenario, f"{base}&sig={alterada}")

    assert respuesta.status_code == 403
    assert respuesta.json()["detail"]["codigo"] == "firma_invalida"


@pytest.mark.asyncio
async def test_una_firma_del_largo_correcto_y_del_alfabeto_ajeno_no_es_un_500(
    escenario: Escenario,
) -> None:
    """The right length in the wrong alphabet is refused, not turned into a 500.

    ``hmac.compare_digest`` does not answer False for a string carrying a
    character outside ASCII: it raises ``TypeError``. A signature of exactly
    sixty four such characters therefore satisfied the only constraint the
    parameter declared -its length- and blew up inside the verification, so the
    download answered 500 where the contract publishes 403 ``firma_invalida``.
    A 500 is not a cosmetic difference here: it tells the interface, and anybody
    probing it, that the portal broke on a link it was in fact rejecting
    correctly.

    Two independent defects put this red and each is checked where it lives.
    Dropping the alphabet from the query parameter leaves only the service
    translation, and the request is then a 403; dropping the translation leaves
    only the parameter, and the request is a 422. Removing both is the state
    this case was written against, and only then does the status leave the pair
    below. The direct call to the service is what keeps the second half honest,
    since no query parameter guards it.

    Args:
        escenario: Wired scenario.
    """
    job_id, url = await enlace_de(escenario)
    base = url.partition("&sig=")[0]
    exp = int(url.partition("exp=")[2].partition("&")[0])

    # ``raise_app_exceptions=False`` is what makes the assertion below about a
    # status code. The ASGI transport re-raises anything the application let
    # escape, and a server does not: it answers 500. The subject of this case is
    # the answer the caller receives, so the transport is asked to behave the way
    # the deployment does instead of handing the exception back to the test.
    transporte = httpx.ASGITransport(
        app=escenario.aplicacion, raise_app_exceptions=False
    )
    async with httpx.AsyncClient(transport=transporte, base_url="http://prueba") as red:
        respuesta = await red.get(
            f"{base}&sig={_FIRMA_DEL_ALFABETO_AJENO}",
            headers={"Authorization": f"Bearer {escenario.token}"},
        )

    assert len(_FIRMA_DEL_ALFABETO_AJENO) == _LARGO_DE_FIRMA
    assert respuesta.status_code in {403, 422}
    with pytest.raises(FirmaInvalida):
        await escenario.servicio.resolver_descarga(
            job_id, exp, _FIRMA_DEL_ALFABETO_AJENO, escenario.analista
        )


def test_factoria_elige_una_sola_vez(monkeypatch: pytest.MonkeyPatch) -> None:
    """One function decides the storage, and both answers keep the same shape.

    The defect is a second branch on the storage setting somewhere else, which
    is exactly how this kind of facade rots: the day the bucket exists, the
    deployment flips one variable and two of the three branches keep writing to
    the local disk. The count below is the same one the plan wrote as its
    verifiable criterion.

    Args:
        monkeypatch: Used to switch the setting between the two backends.
    """
    from app.core.config import get_settings

    local = crear_almacen(get_settings())
    monkeypatch.setenv("EXPORT_STORAGE_BACKEND", "gcs")
    get_settings.cache_clear()
    remoto = crear_almacen(get_settings())

    apariciones = [
        f"{ruta.relative_to(RAIZ)}:{numero}"
        for ruta in sorted((RAIZ / "backend" / "app").rglob("*.py"))
        for numero, linea in enumerate(
            ruta.read_text(encoding="utf-8").splitlines(), start=1
        )
        if "export_storage_backend" in linea
    ]

    assert isinstance(local, AlmacenLocalFirmado)
    assert isinstance(remoto, AlmacenGCS)
    assert len(apariciones) == 2, apariciones
    for almacen in (local, remoto):
        for nombre, parametros in _SUPERFICIE.items():
            miembro = getattr(almacen, nombre)
            assert callable(miembro)
            assert tuple(inspect.signature(miembro).parameters) == parametros


# The four settings of the feature. Every one of them has a default, which is
# what the section that froze them promised: an environment that never exports
# still starts.
_AJUSTES_DE_EXPORTACION: Final[tuple[str, ...]] = (
    "EXPORT_STORAGE_BACKEND",
    "EXPORT_SIGNING_KEY",
    "EXPORT_LINK_TTL_HOURS",
    "EXPORT_DEMO_DELAY_SECONDS",
)


def ajustes_de_quien_no_exporta(monkeypatch: pytest.MonkeyPatch) -> Settings:
    """Build the settings of a deployment that declares no export variable.

    ``_env_file=None`` for the same reason ``test_config.py`` uses it: the
    assertion is about the defaults written in the code and never about a file
    of the machine running the suite.

    Args:
        monkeypatch: Fixture used to clear the four variables.

    Returns:
        The settings such a deployment would boot with.
    """
    for nombre in _AJUSTES_DE_EXPORTACION:
        monkeypatch.delenv(nombre, raising=False)
    # pydantic-settings accepts _env_file at runtime but it is absent from the
    # synthesised __init__, so mypy does not know about it.
    return Settings(_env_file=None)  # type: ignore[call-arg]


def test_los_plazos_por_defecto_son_los_que_el_criterio_describe(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Nobody has to configure anything for a link to last twenty four hours.

    Two defects hide in a default and neither is visible anywhere else in the
    suite, because every other case of this feature passes the numbers by hand:
    a lifetime that drifts from twenty four hours would mint links the
    acceptance criterion never described, and the eight seconds of the
    demonstration left as the default would stretch every real export of every
    deployment -while the honesty band, driven by a different setting on the
    interface, stayed hidden. Building the settings at all is the third
    assertion: a fifth export variable declared without a default would stop the
    portal from starting for everybody who never exports.

    Args:
        monkeypatch: Fixture used to clear the four variables.
    """
    settings = ajustes_de_quien_no_exporta(monkeypatch)

    almacen = crear_almacen(settings, RelojFijo())
    _, caduca = almacen.url_firmada("un-trabajo.csv", INICIO)

    assert caduca == INICIO + timedelta(hours=24)
    assert settings.export_demo_delay_seconds == 0.0


def test_la_clave_de_firma_vacia_se_deriva_y_jamas_firma_con_nada(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """An unset signing key means "derive one", never "sign with nothing".

    The empty default is what lets a deployment that never exports start, and
    it is one edit away from being a hole. ``clave=declarada`` on its own signs
    every link with an empty HMAC key, which anybody who read this repository
    can reproduce and forge; ``clave=declarada or jwt_secret_key`` hands whoever
    obtains one download link the key that mints access tokens. Both defects
    leave the rest of this file green -a portal that signs and verifies with the
    same wrong key agrees with itself- so they are caught by asking two
    storages built with exactly those keys to accept a signature the real one
    minted.

    Args:
        monkeypatch: Fixture used to clear the four variables.
    """
    settings = ajustes_de_quien_no_exporta(monkeypatch)
    almacen = crear_almacen(settings, RelojFijo())
    assert isinstance(almacen, AlmacenLocalFirmado)
    object_key = "un-trabajo.csv"

    url, caduca = almacen.url_firmada(object_key, INICIO)
    firma = url.partition("&sig=")[2]
    expira_en = int(caduca.timestamp())

    # Control: the portal accepts what the portal signed. Without it the two
    # refusals below could be produced by a signature nobody can redeem.
    almacen.verificar(object_key, expira_en, firma)

    for clave in ("", settings.jwt_secret_key):
        impostor = AlmacenLocalFirmado(clave=clave, ttl_horas=24, reloj=RelojFijo())
        with pytest.raises(FirmaInvalida):
            impostor.verificar(object_key, expira_en, firma)

    assert derivar_clave_de_firma(settings.jwt_secret_key) != settings.jwt_secret_key


class _BlobDoble:
    """Double of a Cloud Storage blob that records what it was asked for.

    Attributes:
        subidas: Paths handed to ``upload_from_filename``.
        firmas: Pairs of version and lifetime handed to the signer.
    """

    def __init__(self) -> None:
        """Start with nothing recorded."""
        self.subidas: list[str] = []
        self.firmas: list[tuple[str, timedelta]] = []

    def upload_from_filename(self, filename: str) -> None:
        """Record the upload.

        Args:
            filename: Path of the file.
        """
        self.subidas.append(filename)

    def generate_signed_url(self, *, version: str, expiration: timedelta) -> str:
        """Record the signing arguments and answer with a fixed URL.

        Args:
            version: Signing scheme.
            expiration: Lifetime of the URL.

        Returns:
            A URL with the shape of a signed one.
        """
        self.firmas.append((version, expiration))
        return _URL_FIRMADA_DE_PRUEBA


class _BucketDoble:
    """Double of a bucket that always hands out the same blob."""

    def __init__(self, blob: _BlobDoble) -> None:
        """Bind the double to the blob it serves.

        Args:
            blob: Blob every key resolves to.
        """
        self._blob = blob
        self.claves: list[str] = []

    def blob(self, blob_name: str) -> _BlobDoble:
        """Record the key and return the blob.

        Args:
            blob_name: Object key.

        Returns:
            The blob double.
        """
        self.claves.append(blob_name)
        return self._blob


class _ClienteDoble:
    """Double of the Cloud Storage client. No SDK, no credentials, no network."""

    def __init__(self, bucket: _BucketDoble) -> None:
        """Bind the double to the bucket it serves.

        Args:
            bucket: Bucket every name resolves to.
        """
        self._bucket = bucket
        self.nombres: list[str] = []

    def bucket(self, bucket_name: str) -> _BucketDoble:
        """Record the name and return the bucket.

        Args:
            bucket_name: Name of the bucket.

        Returns:
            The bucket double.
        """
        self.nombres.append(bucket_name)
        return self._bucket


@pytest.mark.asyncio
async def test_gcs_firma_v4_con_la_misma_vigencia(tmp_path: Path) -> None:
    """The dormant implementation asks Cloud Storage for the same deadline.

    This is the only part of ``AlmacenGCS`` that can be verified without a
    project: the arguments it builds. It fails if somebody signs with the V2
    scheme -which takes an absolute instant and would receive a duration- or if
    the lifetime stops coming from the single setting and drifts away from the
    twenty four hours the local facade enforces.

    Args:
        tmp_path: Directory of the test.
    """
    blob = _BlobDoble()
    cliente = _ClienteDoble(_BucketDoble(blob))
    almacen = AlmacenGCS(ttl_horas=24, cliente=cliente)
    job_id = uuid.uuid4()
    origen = tmp_path / "extracto.csv"
    origen.write_text("credito_id\nCR0000001\n", encoding="utf-8")

    object_key = await almacen.guardar(job_id, origen, "csv")
    url, caduca = almacen.url_firmada(object_key, INICIO)

    assert object_key == f"exports/{job_id}.csv"
    assert blob.subidas == [str(origen)]
    assert blob.firmas == [("v4", timedelta(hours=24))]
    assert url == _URL_FIRMADA_DE_PRUEBA
    assert caduca - datetime.now(UTC) > timedelta(hours=23, minutes=59)


def test_ambas_implementaciones_satisfacen_el_protocolo() -> None:
    """The facade is one type, so the service can be written against it alone.

    It fails the day one implementation renames a parameter or drops a member:
    the service would keep type checking against the protocol and break at run
    time only in the deployment that uses the other backend.
    """
    for nombre, parametros in _SUPERFICIE.items():
        declarado = getattr(AlmacenDeExportaciones, nombre)
        firma = tuple(inspect.signature(declarado).parameters)
        assert firma == ("self", *parametros)


@pytest.mark.asyncio
async def test_la_descarga_se_niega_por_cuatro_razones_y_todas_son_404(
    escenario: Escenario, tmp_path: Path
) -> None:
    """Every reason to refuse a file is answered the same way: as absence.

    Four different defects hide behind one status code here. Handing the file
    to somebody who does not own it; serving a job that never completed and
    therefore has no file; letting the endpoint answer for a deployment whose
    links are signed and served by the bucket instead of by this API; and
    turning a file missing from disk into a 500. The first three would leak or
    invent data, and the fourth would say that the portal is broken when what
    happened is that a temporary directory was cleaned.

    Args:
        escenario: Wired scenario.
        tmp_path: Directory of the test.
    """
    job_id, url = await enlace_de(escenario)
    fila = escenario.repositorio.filas[job_id]
    assert fila.object_key is not None
    exp = int(url.partition("exp=")[2].partition("&")[0])
    firma = url.partition("&sig=")[2]
    ajeno = UserOut.model_validate(
        {**escenario.analista.model_dump(), "id": uuid.uuid4()}
    )

    with pytest.raises(TrabajoNoEncontradoError):
        await escenario.servicio.resolver_descarga(job_id, exp, firma, ajeno)

    servicio_en_la_nube = ExportService(
        repositorio=escenario.repositorio,
        almacen=AlmacenGCS(
            ttl_horas=24, cliente=_ClienteDoble(_BucketDoble(_BlobDoble()))
        ),
        data_dir=tmp_path / "data",
        ttl_horas=24,
        reloj=escenario.reloj,
    )
    with pytest.raises(TrabajoNoEncontradoError):
        await servicio_en_la_nube.resolver_descarga(
            job_id, exp, firma, escenario.analista
        )

    escenario.almacen.ruta_de(fila.object_key).unlink()
    with pytest.raises(TrabajoNoEncontradoError):
        await escenario.servicio.resolver_descarga(
            job_id, exp, firma, escenario.analista
        )

    fila.status = "pendiente"
    with pytest.raises(TrabajoNoEncontradoError):
        await escenario.servicio.resolver_descarga(
            job_id, exp, firma, escenario.analista
        )
