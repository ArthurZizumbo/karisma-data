"""Who reaches the four export verbs, and what a stranger is told about a job.

The four routes of ``/api/export`` demand ``analista`` and not ``operativo``. A
bulk extraction is the operation of this portal with the most data crossing the
perimeter, so it sits above the punctual query; the parametrized matrix below is
what would catch a scope list copied from the catalog router, which is how that
kind of mistake actually gets made.

The first case asserts directly on ``app.routes``. It is the only inventory that
exists whether or not the startup guard runs, and it answers the question that
matters: does every mounted operation carry a security requirement, and does it
name the level the policy published.

Nothing here opens PostgreSQL. Two seams are substituted -the read side of
``app_user`` and the export service- and everything else, the authorization
dependency included, is production code.
"""

import uuid
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from datetime import timedelta
from pathlib import Path
from typing import TYPE_CHECKING, Any, Final, cast

import httpx
import pytest
from fastapi import FastAPI
from fastapi.dependencies.models import Dependant
from fastapi.routing import APIRoute, iter_route_contexts
from fastapi.security.base import SecurityBase
from test_export_endpoint import (
    CONJUNTO,
    INICIO,
    RelojFijo,
    RepositorioDeTrabajosEnMemoria,
    crear_almacen_de_prueba,
    usuario_de,
)

from app.core.scopes import Scope
from app.models.export import EstadoTrabajo, ExportJob, FormatoExportacion
from app.models.user import UserOut
from app.services.almacen.local import AlmacenLocalFirmado
from app.services.export_service import ExportService, get_export_service
from app.services.user_service import get_user_repository

if TYPE_CHECKING:
    from conftest import FakeUserRepository

    from app.models.user import AppUser

# The four operations of the feature, as method and path template. They are the
# inventory the first case cross-checks against what the application mounts.
RUTAS: Final[tuple[tuple[str, str], ...]] = (
    ("POST", "/api/export"),
    ("GET", "/api/export"),
    ("GET", "/api/export/{job_id}"),
    ("GET", "/api/export/{job_id}/download"),
)

# Dataset of the job that belongs to somebody else. Different from the one every
# other case uses, so its name showing up in an answer is unambiguous.
CONJUNTO_AJENO: Final[str] = "liquidez"

# Status each verb answers to a caller who does reach the level.
_ESPERADO: Final[dict[str, int]] = {
    "solicitar": 202,
    "historial": 200,
    "estado": 200,
    "descarga": 200,
}


@dataclass
class Escenario:
    """The application, the storage and one finished job per seeded user.

    Attributes:
        aplicacion: Real application, with the two seams substituted.
        almacen: Local storage the links are minted from.
        repositorio: Job registry double, so a case can add one more row.
        trabajos: Finished job of each user, indexed by owner.
        usuarios: Caller contract of each seeded user, indexed by role.
        token_de_rol: Factory of valid tokens per role.
    """

    aplicacion: FastAPI
    almacen: AlmacenLocalFirmado
    repositorio: RepositorioDeTrabajosEnMemoria
    trabajos: dict[uuid.UUID, ExportJob]
    usuarios: dict[Scope, UserOut]
    token_de_rol: Callable[[Scope], str]


def trabajo_completado(
    propietario: uuid.UUID, almacen: AlmacenLocalFirmado, *, dataset: str = CONJUNTO
) -> ExportJob:
    """Build a finished job and leave its file where the storage expects it.

    Args:
        propietario: Owner of the job.
        almacen: Storage the file is written into.
        dataset: Source the job exported.

    Returns:
        The row, coherent with the constraint the migration declares for a
        completed job.
    """
    job_id = uuid.uuid4()
    object_key = f"{job_id}.csv"
    ruta = almacen.ruta_de(object_key)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text("credito_id,saldo\nCR0000001,10.5\n", encoding="utf-8")
    return ExportJob(
        id=job_id,
        requested_by=propietario,
        dataset=dataset,
        export_format=FormatoExportacion.CSV.value,
        filters={},
        status=EstadoTrabajo.COMPLETADO.value,
        row_count=1,
        byte_size=ruta.stat().st_size,
        object_key=object_key,
        created_at=INICIO,
        started_at=INICIO,
        finished_at=INICIO,
        expires_at=INICIO + timedelta(hours=24),
    )


@pytest.fixture
def escenario(
    tmp_path: Path,
    usuarios_semilla: dict[str, "AppUser"],
    repositorio_falso: "FakeUserRepository",
    token_de: Callable[..., str],
) -> Iterator[Escenario]:
    """Wire the application, one finished job per user and the four tokens.

    Args:
        tmp_path: Directory of the test.
        usuarios_semilla: Rows of the seven seeded users.
        repositorio_falso: Read side of ``app_user``, doubled.
        token_de: Factory of signed tokens from the shared conftest.

    Yields:
        The wired scenario.
    """
    from app.main import create_app

    por_rol: dict[Scope, AppUser] = {}
    for fila in usuarios_semilla.values():
        por_rol.setdefault(Scope(fila.role), fila)

    almacen = crear_almacen_de_prueba(tmp_path / "almacen", RelojFijo())
    trabajos = {
        fila.id: trabajo_completado(fila.id, almacen)
        for fila in por_rol.values()
        if fila.id is not None
    }
    repositorio = RepositorioDeTrabajosEnMemoria(list(trabajos.values()))
    servicio = ExportService(
        repositorio=repositorio,
        almacen=almacen,
        data_dir=tmp_path / "data",
        ttl_horas=24,
        reloj=RelojFijo(),
    )

    aplicacion = create_app()
    aplicacion.dependency_overrides[get_user_repository] = lambda: repositorio_falso
    aplicacion.dependency_overrides[get_export_service] = lambda: servicio

    yield Escenario(
        aplicacion=aplicacion,
        almacen=almacen,
        repositorio=repositorio,
        trabajos=trabajos,
        usuarios={rol: usuario_de(fila) for rol, fila in por_rol.items()},
        token_de_rol=lambda rol: token_de(por_rol[rol].username, rol.value),
    )


def peticion(
    escenario: Escenario, verbo: str, rol: Scope
) -> tuple[str, str, dict[str, Any] | None]:
    """Build one concrete request of the matrix.

    Args:
        escenario: Wired scenario.
        verbo: Key of the operation under test.
        rol: Role the request is made with.

    Returns:
        The method, the URL and the body, if any.
    """
    propio = escenario.trabajos[escenario.usuarios[rol].id]
    assert propio.id is not None and propio.object_key is not None
    if verbo == "solicitar":
        return "POST", "/api/export", {"dataset": CONJUNTO}
    if verbo == "historial":
        return "GET", "/api/export", None
    if verbo == "estado":
        return "GET", f"/api/export/{propio.id}", None
    url, _ = escenario.almacen.url_firmada(propio.object_key, INICIO)
    return "GET", url, None


async def responder(
    escenario: Escenario,
    metodo: str,
    url: str,
    cuerpo: dict[str, Any] | None,
    token: str | None,
) -> httpx.Response:
    """Send one request to the real application.

    Args:
        escenario: Wired scenario.
        metodo: HTTP method.
        url: Relative URL.
        cuerpo: JSON body, if any.
        token: Encoded token, or ``None`` for an anonymous request.

    Returns:
        The answer of the portal.
    """
    cabeceras = {"Authorization": f"Bearer {token}"} if token else {}
    transporte = httpx.ASGITransport(app=escenario.aplicacion)
    async with httpx.AsyncClient(transport=transporte, base_url="http://prueba") as red:
        return await red.request(metodo, url, json=cuerpo, headers=cabeceras)


def requisitos_de(dependant: Dependant) -> tuple[set[str], bool]:
    """Walk a dependency tree and report what it demands of the caller.

    Since FastAPI 0.141 a ``Dependant`` no longer carries a flat
    ``security_requirements`` list: the scheme is a sub dependency whose call
    is a ``SecurityBase`` and the scopes travel in ``own_oauth_scopes``. This
    reads the same fact from the tree that actually enforces it.

    Args:
        dependant: Root of the dependency tree of one operation.

    Returns:
        The scopes the tree demands and whether it declares a security scheme
        at all.
    """
    scopes: set[str] = set()
    con_esquema = False
    pendientes = [dependant]
    while pendientes:
        actual = pendientes.pop()
        scopes.update(str(scope) for scope in actual.own_oauth_scopes or ())
        # Cast to object first: the declared type of ``call`` is a plain
        # callable, and a security scheme is an instance that happens to be
        # callable, which the type checker reads as impossible.
        if isinstance(cast(object, actual.call), SecurityBase):
            con_esquema = True
        pendientes.extend(actual.dependencies)
    return scopes, con_esquema


def test_router_declara_security(minimal_env: None) -> None:
    """Every mounted export operation carries the analyst requirement.

    The defect is a verb that forgets ``Security(...)``: it would answer to
    anybody with a valid session, or to nobody at all, and the matrix below
    would still be green for the other three. The assertion is on the routes
    the application mounts, so a router that stops being included fails here
    too instead of silently having nothing to check.

    Args:
        minimal_env: Declared so the settings are in place before the app is
            built.
    """
    from app.main import create_app

    aplicacion = create_app()
    exigidos: dict[tuple[str, str], tuple[set[str], bool]] = {}
    for contexto in iter_route_contexts(aplicacion.routes):
        ruta = contexto.original_route
        if not isinstance(ruta, APIRoute) or not str(contexto.path).startswith(
            "/api/export"
        ):
            continue
        for metodo in contexto.methods or ():
            exigidos[metodo.upper(), str(contexto.path)] = requisitos_de(ruta.dependant)

    assert set(exigidos) == set(RUTAS)
    for clave, (scopes, con_esquema) in exigidos.items():
        assert con_esquema, f"{clave} no declara ningun esquema de seguridad"
        assert Scope.ANALISTA.value in scopes, clave


@pytest.mark.asyncio
@pytest.mark.parametrize("verbo", list(_ESPERADO))
@pytest.mark.parametrize("rol", list(Scope))
async def test_matriz_de_roles(escenario: Escenario, verbo: str, rol: Scope) -> None:
    """The four verbs against the four roles: only ``operativo`` is refused.

    The defect is ``scopes=[Scope.OPERATIVO]`` copied from the catalog router,
    which would open the bulk extraction of the portal to its lowest role. The
    upper three are asserted with the exact status of a success and not merely
    with "not a 403", so a route that answers 200 where it promised 202 -or one
    that hands the file to a caller whose signature never matched- is caught
    here as well.

    Args:
        escenario: Wired scenario.
        verbo: Operation under test.
        rol: Role carried by the token.
    """
    metodo, url, cuerpo = peticion(escenario, verbo, rol)

    respuesta = await responder(
        escenario, metodo, url, cuerpo, escenario.token_de_rol(rol)
    )

    if rol is Scope.OPERATIVO:
        assert respuesta.status_code == 403
        assert respuesta.json()["detail"] == "permisos_insuficientes"
    else:
        assert respuesta.status_code == _ESPERADO[verbo]


@pytest.mark.asyncio
@pytest.mark.parametrize("verbo", list(_ESPERADO))
async def test_sin_token_es_401_con_cabecera(escenario: Escenario, verbo: str) -> None:
    """An anonymous request is refused with the challenge the client needs.

    Without ``WWW-Authenticate: Bearer`` the interface cannot tell an expired
    session from a forbidden screen, so it would either relaunch the login on
    every failure or on none of them.

    Args:
        escenario: Wired scenario.
        verbo: Operation under test.
    """
    metodo, url, cuerpo = peticion(escenario, verbo, Scope.ANALISTA)

    respuesta = await responder(escenario, metodo, url, cuerpo, None)

    assert respuesta.status_code == 401
    assert respuesta.headers["www-authenticate"].startswith('Bearer realm="karisma"')
    assert 'scope="analista"' in respuesta.headers["www-authenticate"]


@pytest.mark.asyncio
async def test_el_historial_de_gobierno_viaja_sin_enlaces(escenario: Escenario) -> None:
    """An administrator receives the whole register, and it carries no link.

    Two defects are read off the same answer. The first is the history
    filtering by the caller for every role: the register would arrive with one
    job in it and the role that audits the extractions of the portal would be
    the one role that cannot. The second is the answer being built from the
    polled contract instead of the summary, which would hand an administrator a
    signed URL for the file of somebody else -a file ``resolver_descarga``
    would then refuse them, which is worse than never offering it.

    The assertion is made over the wire and not over the returned objects
    because what decides which fields exist is ``response_model``: a service
    that stopped minting links would still leak them if the declared model
    carried the fields.

    Args:
        escenario: Wired scenario.
    """
    respuesta = await responder(
        escenario, "GET", "/api/export", None, escenario.token_de_rol(Scope.ADMIN)
    )
    propio = await responder(
        escenario, "GET", "/api/export", None, escenario.token_de_rol(Scope.ANALISTA)
    )

    registro = respuesta.json()
    analista = escenario.usuarios[Scope.ANALISTA]
    directivo = escenario.usuarios[Scope.DIRECTIVO]

    assert respuesta.status_code == 200
    assert {trabajo["solicitado_por"] for trabajo in registro} == {
        str(usuario.id) for usuario in escenario.usuarios.values()
    }
    assert all(
        "url_descarga" not in trabajo and "caduca_en" not in trabajo
        for trabajo in registro
    )

    # The handle of the file of somebody else is not in the answer either: it
    # is the one string a governance reader could try against the storage.
    assert str(escenario.trabajos[directivo.id].object_key) not in respuesta.text

    # And the filtered branch stays filtered: this is the leak the register is
    # allowed to be an exception to, and only for the role that governs.
    assert [trabajo["solicitado_por"] for trabajo in propio.json()] == [
        str(analista.id)
    ]


@pytest.mark.asyncio
async def test_trabajo_ajeno_devuelve_404(escenario: Escenario) -> None:
    """A job of somebody else is answered as if it did not exist.

    A 403 here would confirm that the identifier is real, turning the endpoint
    into an oracle: walking the identifier space would tell an analyst how many
    exports the rest of the portal runs and when. The body is checked as well,
    because a 404 that leaks the dataset in its message gives away exactly what
    the status code refused to say.

    Args:
        escenario: Wired scenario.
    """
    directivo = escenario.usuarios[Scope.DIRECTIVO]
    ajeno = trabajo_completado(directivo.id, escenario.almacen, dataset=CONJUNTO_AJENO)
    await escenario.repositorio.crear(ajeno)

    respuesta = await responder(
        escenario,
        "GET",
        f"/api/export/{ajeno.id}",
        None,
        escenario.token_de_rol(Scope.ANALISTA),
    )

    url, _ = escenario.almacen.url_firmada(str(ajeno.object_key), INICIO)
    descarga = await responder(
        escenario, "GET", url, None, escenario.token_de_rol(Scope.ANALISTA)
    )

    assert respuesta.status_code == 404
    assert respuesta.json() == {"detail": {"codigo": "trabajo_no_encontrado"}}
    assert CONJUNTO_AJENO not in respuesta.text

    # The signature is valid and the deadline has not passed: what refuses the
    # file is ownership alone, and it refuses it as absence.
    assert descarga.status_code == 404
    assert descarga.json() == {"detail": {"codigo": "trabajo_no_encontrado"}}
