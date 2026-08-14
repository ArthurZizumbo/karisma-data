"""The four locks against leaking ``hashed_password``, plus the one on the logs.

``response_model=`` filters, and it is the guarantee that evaporates the day
somebody returns a dictionary to debug something. Each case below exercises a
different lock, from the deepest to the most superficial:

1. the projection, read from the SQL the repository actually builds;
2. the source of the router and the service, which never name the row that
   carries the digest;
3. the OpenAPI schema of the whole API, not only of ``/api/users``;
4. the real response bodies of the three operations;
5. and the structured log records, which is where a debug session leaks a hash
   without anybody noticing for months.

The third one is deliberately written against the whole schema: it is the guard
that survives this US and turns red the day another story exposes ``AppUser`` as
a ``response_model`` anywhere.
"""

import ast
import json
import uuid
from collections.abc import Callable
from pathlib import Path
from typing import Final

import pytest
import structlog
from fastapi.testclient import TestClient

from app.core.scopes import Scope
from app.services.user_service import SqlAdminUserRepository

from .conftest import ADMIN, OTRO, SesionEspia, sql_de

DIGESTO: Final[str] = "hashed_password"
PREFIJO_ARGON: Final[str] = "$argon2"

REPO_ROOT: Final[Path] = Path(__file__).resolve().parents[3]

# The two modules of this US that must not be able to name the row of the digest.
MODULOS_SIN_ENTIDAD: Final[tuple[Path, ...]] = (
    REPO_ROOT / "backend" / "app" / "api" / "users.py",
    REPO_ROOT / "backend" / "app" / "services" / "user_admin_service.py",
)


@pytest.fixture
def registro(monkeypatch: pytest.MonkeyPatch) -> structlog.testing.CapturingLogger:
    """Replace the logger of the administration service with a capturing double.

    Reconfiguring structlog would not do: ``create_app`` caches the bound logger
    on first use, so a global change to the level would or would not take effect
    depending on the order of the suite, and a privacy test that depends on test
    ordering is worse than no test.

    Args:
        monkeypatch: Used to swap the module level logger.

    Returns:
        The double, whose ``calls`` list holds every emitted record.
    """
    from app.services import user_admin_service

    capturador = structlog.testing.CapturingLogger()
    monkeypatch.setattr(user_admin_service, "logger", capturador)
    return capturador


@pytest.mark.asyncio
async def test_ninguna_sentencia_de_administracion_lee_el_digesto(
    sesion_espia: SesionEspia,
) -> None:
    """The deepest lock: what is never selected cannot be serialised.

    A future shortcut that selects the entity instead of the eight columns puts
    the digest one ``model_dump`` away from the wire, and no ``response_model``
    would be involved in the leak.
    """
    repositorio = SqlAdminUserRepository(sesion_espia)  # type: ignore[arg-type]
    destino = uuid.UUID(int=1)

    await repositorio.list_page(limit=1, offset=0)
    await repositorio.get_by_id(destino)
    await repositorio.update_role(destino, Scope.OPERATIVO)
    await repositorio.set_disabled(destino, disabled=True)

    assert len(sesion_espia.sentencias) == 5
    for sentencia in sesion_espia.sentencias:
        assert DIGESTO not in sql_de(sentencia)


@pytest.mark.asyncio
async def test_las_sentencias_nombran_las_ocho_columnas_del_contrato(
    sesion_espia: SesionEspia,
) -> None:
    """The projection is the eight fields of the contract, named one by one.

    A column dropped from the projection reaches the interface as a missing key
    and the table renders an empty cell instead of failing loudly.
    """
    repositorio = SqlAdminUserRepository(sesion_espia)  # type: ignore[arg-type]

    await repositorio.get_by_id(uuid.UUID(int=1))

    sentencia = sql_de(sesion_espia.sentencias[0])
    for columna in (
        "id",
        "username",
        "email",
        "full_name",
        "role",
        "disabled",
        "created_at",
        "updated_at",
    ):
        assert f"app_user.{columna}" in sentencia


def identificadores(modulo: Path) -> set[str]:
    """Return every name the module actually uses, prose excluded.

    The syntax tree is walked instead of the raw text on purpose: the docstrings
    of both modules explain *why* they never name the entity, and a substring
    search would read the explanation as the offence.

    Args:
        modulo: Path of the Python module.

    Returns:
        Imported names, referenced names and attribute names.
    """
    arbol = ast.parse(modulo.read_text(encoding="utf-8"))
    nombres: set[str] = set()
    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.Name):
            nombres.add(nodo.id)
        elif isinstance(nodo, ast.Attribute):
            nombres.add(nodo.attr)
        elif isinstance(nodo, ast.alias):
            nombres.add(nodo.name.rsplit(".", 1)[-1])
            if nodo.asname:
                nombres.add(nodo.asname)
    return nombres


@pytest.mark.parametrize(
    "modulo", MODULOS_SIN_ENTIDAD, ids=[ruta.name for ruta in MODULOS_SIN_ENTIDAD]
)
def test_el_router_y_el_servicio_no_pueden_nombrar_la_fila(modulo: Path) -> None:
    """Without the symbol imported there is no way to write the leak.

    This is a source level assertion on purpose: it is the only one that catches
    the import *before* somebody uses it, which is the moment the defect is one
    line away instead of already shipped.
    """
    nombres = identificadores(modulo)

    assert "AppUser" not in nombres
    assert DIGESTO not in nombres


def sin_prosa(nodo: object) -> object:
    """Return the same structure with every human readable text removed.

    The docstring of ``UserAdminOut`` explains that the field does not exist and
    travels into the schema as a description; keeping it would make the guard
    fail on its own documentation.

    Args:
        nodo: Any fragment of the OpenAPI document.

    Returns:
        The fragment without ``description``, ``summary`` or ``title`` values.
    """
    if isinstance(nodo, dict):
        return {
            clave: sin_prosa(valor)
            for clave, valor in nodo.items()
            if clave not in {"description", "summary", "title"}
        }
    if isinstance(nodo, list):
        return [sin_prosa(elemento) for elemento in nodo]
    return nodo


def test_el_esquema_openapi_completo_no_menciona_el_digesto(
    cliente_admin: TestClient,
) -> None:
    """No schema of the whole API exposes the digest, not only the users ones.

    This is the guard that outlives this US: it turns red the day any story
    declares ``AppUser`` as a ``response_model`` on any route of the portal.
    """
    documento = cliente_admin.app.openapi()  # type: ignore[attr-defined]

    esquema = json.dumps(sin_prosa(documento))

    assert DIGESTO not in esquema


def test_ningun_cuerpo_de_las_tres_operaciones_lleva_el_digesto(
    cliente_admin: TestClient,
    cabecera_admin: dict[str, str],
    id_de: Callable[[str], uuid.UUID],
) -> None:
    """The real bodies carry neither the field name nor an argon2 digest.

    A router that builds its answer as a dictionary to debug a conflict is the
    way this reappears after ``response_model`` has been in place for months.
    """
    destino = f"/api/users/{id_de(OTRO)}"
    respuestas = [
        cliente_admin.get("/api/users", headers=cabecera_admin),
        cliente_admin.patch(
            destino, json={"role": Scope.OPERATIVO.value}, headers=cabecera_admin
        ),
        cliente_admin.delete(destino, headers=cabecera_admin),
    ]

    for respuesta in respuestas:
        assert respuesta.status_code == 200
        assert DIGESTO not in respuesta.text
        assert PREFIJO_ARGON not in respuesta.text


def test_ningun_registro_estructurado_lleva_el_digesto(
    cliente_admin: TestClient,
    cabecera_admin: dict[str, str],
    id_de: Callable[[str], uuid.UUID],
    registro: structlog.testing.CapturingLogger,
) -> None:
    """The events of this US carry identity and roles, never the hash.

    Logging the whole user object while debugging a 409 leaves the digest in
    production records, where it survives every later fix of the endpoint.
    """
    destino = f"/api/users/{id_de(OTRO)}"

    cliente_admin.patch(
        destino, json={"role": Scope.OPERATIVO.value}, headers=cabecera_admin
    )
    cliente_admin.delete(destino, headers=cabecera_admin)
    cliente_admin.delete(f"/api/users/{id_de(ADMIN)}", headers=cabecera_admin)

    registrado = " ".join(repr(llamada) for llamada in registro.calls)
    assert registro.calls, "sin eventos capturados la prueba no probaria nada"
    assert DIGESTO not in registrado
    assert PREFIJO_ARGON not in registrado
    assert "@" not in registrado


def test_los_eventos_de_administracion_identifican_al_actor_y_al_afectado(
    cliente_admin: TestClient,
    cabecera_admin: dict[str, str],
    id_de: Callable[[str], uuid.UUID],
    registro: structlog.testing.CapturingLogger,
) -> None:
    """An administrative change is traceable without an access log existing.

    A silent write is indistinguishable from no write at all when the incident
    is reviewed, and this US deliberately ships no audit table: the event and
    the ``updated_at`` column are the whole trail.
    """
    cliente_admin.delete(f"/api/users/{id_de(OTRO)}", headers=cabecera_admin)

    desactivaciones = [
        llamada
        for llamada in registro.calls
        if llamada.args and llamada.args[0] == "usuario_desactivado"
    ]
    assert len(desactivaciones) == 1
    campos = desactivaciones[0].kwargs
    assert campos["username"] == OTRO
    assert campos["actor"] == ADMIN
    assert "email" not in campos
