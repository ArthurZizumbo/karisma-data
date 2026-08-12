"""Tests of the coverage guard, exercised against synthetic applications.

This is the part that makes the startup check trustworthy. The guard is proved
against applications built inside the test -one per class of defect- and not
only against the real one: the real application has three routes today and all
three are governed, so a suite that only audited it would be a suite that cannot
fail, and a test that cannot fail buys coverage that means nothing.

The synthetic applications carry their own security scheme instead of importing
``get_current_user``. What the guard reads is the security requirement the
schema publishes, and building it here keeps these tests free of the token, the
settings and the repository.
"""

import re
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Annotated, Final

import pytest
from fastapi import APIRouter, Depends, FastAPI, Security
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from starlette.applications import Starlette

from app.core.permissions import (
    API_PREFIX,
    PUBLIC_ROUTES,
    SCOPE_REGISTRY,
    PermissionRule,
    RouteKey,
    ScopeCoverageError,
    ViolationKind,
    assert_scope_coverage,
    audit_scope_coverage,
    live_routes,
)
from app.core.scopes import Scope, oauth2_scope_descriptions

BACKEND_APP = Path(__file__).resolve().parents[3] / "backend" / "app"

RUTA_SONDA: Final[str] = "/api/sintetica/recurso"
CLAVE_SONDA: Final[RouteKey] = RouteKey("GET", RUTA_SONDA)

# Policy used by the synthetic applications. It is passed explicitly to the
# guard so that these tests never depend on the real registry: the subject is
# the algorithm, not the portal.
REGISTRO_SINTETICO: Final[Mapping[RouteKey, PermissionRule]] = {
    CLAVE_SONDA: PermissionRule(
        scopes=(Scope.ANALISTA,),
        rule="Recurso de prueba de la guardia",
        us="US-016",
        status="vigente",
    )
}

esquema_sintetico = OAuth2PasswordBearer(
    tokenUrl="/api/auth/token",
    scopes=oauth2_scope_descriptions(),
    auto_error=False,
)


async def dependencia_sintetica(
    security_scopes: SecurityScopes,
    token: Annotated[str | None, Depends(esquema_sintetico)],
) -> str:
    """Stand in for the security dependency of the portal.

    The guard never calls it: it reads the requirement the scheme publishes in
    the schema. It returns the scopes it was declared with so that a request
    against a synthetic application shows something useful when it is made.

    Args:
        security_scopes: Scopes declared by the endpoint.
        token: Bearer token, absent in these tests.

    Returns:
        The declared scopes, joined by spaces.
    """
    return " ".join(security_scopes.scopes) if token is None else token


def _endpoint_protegido(
    scopes: list[str],
) -> Callable[..., object]:
    """Build an endpoint guarded by the synthetic dependency.

    Args:
        scopes: Scope names declared through ``Security``.

    Returns:
        The endpoint function.
    """

    async def punto_final(
        _principal: Annotated[str, Security(dependencia_sintetica, scopes=scopes)],
    ) -> dict[str, str]:
        """Answer once the security dependency resolved.

        Args:
            _principal: Result of the security dependency, unused.

        Returns:
            A fixed payload.
        """
        return {"estado": "ok"}

    return punto_final


async def _endpoint_desnudo() -> dict[str, str]:
    """Answer without any security requirement at all.

    Returns:
        A fixed payload.
    """
    return {"estado": "ok"}


def _aplicacion_con(
    scopes: list[str] | None,
    *,
    ruta: str = RUTA_SONDA,
    en_el_esquema: bool = True,
) -> FastAPI:
    """Build a one route application with the requested defect, or none.

    Args:
        scopes: Scope names the route declares, or ``None`` for a route with no
            security requirement.
        ruta: Path of the route.
        en_el_esquema: Whether the route appears in the OpenAPI schema.

    Returns:
        The synthetic application.
    """
    aplicacion = FastAPI()
    punto_final = _endpoint_desnudo if scopes is None else _endpoint_protegido(scopes)
    aplicacion.add_api_route(
        ruta,
        punto_final,
        methods=["GET"],
        include_in_schema=en_el_esquema,
        name="sonda",
    )
    return aplicacion


def _auditar(aplicacion: FastAPI) -> tuple[ViolationKind, ...]:
    """Audit a synthetic application against the synthetic policy.

    Args:
        aplicacion: Application to audit.

    Returns:
        The class of every violation found, in order.
    """
    return tuple(
        violacion.kind
        for violacion in audit_scope_coverage(
            aplicacion, registry=REGISTRO_SINTETICO, public=frozenset()
        )
    )


def test_detecta_endpoint_sin_security() -> None:
    """A route under /api with no security requirement is the defect of the US.

    It is what copying ``health.py`` as the template of a new router produces,
    and the schema shows it as an operation without ``security``.
    """
    violaciones = audit_scope_coverage(
        _aplicacion_con(None), registry=REGISTRO_SINTETICO, public=frozenset()
    )

    assert [violacion.kind for violacion in violaciones] == [ViolationKind.SIN_SCOPES]
    assert violaciones[0].route == CLAVE_SONDA
    assert "Security" in violaciones[0].detail


def test_detecta_ruta_fuera_del_registro() -> None:
    """A protected route with no row in the policy is not governed either.

    Declaring ``Security(...)`` is half the job: without the row there is no
    reason written down and no line in the document.
    """
    violaciones = audit_scope_coverage(
        _aplicacion_con([Scope.ANALISTA.value]),
        registry={},
        public=frozenset(),
    )

    assert [violacion.kind for violacion in violaciones] == [
        ViolationKind.FUERA_DEL_REGISTRO
    ]


def test_detecta_scope_divergente() -> None:
    """The code demanding less than the policy says is a silent downgrade.

    This is the shape of "let me lower it to unblock the demo": the document
    would keep telling the truth while the application lied.
    """
    violaciones = audit_scope_coverage(
        _aplicacion_con([Scope.OPERATIVO.value]),
        registry=REGISTRO_SINTETICO,
        public=frozenset(),
    )

    assert [violacion.kind for violacion in violaciones] == [
        ViolationKind.SCOPE_DIVERGENTE
    ]
    assert "operativo" in violaciones[0].detail
    assert "analista" in violaciones[0].detail


def test_detecta_ruta_oculta() -> None:
    """A route out of the schema is the blind spot of auditing the schema.

    ``include_in_schema=False`` hides the operation from the document, so the
    guard crosses two inventories and reports the absence as a finding.
    """
    violaciones = audit_scope_coverage(
        _aplicacion_con([Scope.ANALISTA.value], en_el_esquema=False),
        registry=REGISTRO_SINTETICO,
        public=frozenset(),
    )

    assert [violacion.kind for violacion in violaciones] == [ViolationKind.RUTA_OCULTA]


def test_endpoint_conforme_no_produce_violaciones() -> None:
    """A conforming route is silent, which is what keeps the guard switched on.

    A guard that cries wolf gets disabled, and disabled it protects nothing.
    """
    assert _auditar(_aplicacion_con([Scope.ANALISTA.value])) == ()


def test_la_ruta_de_la_lista_blanca_no_necesita_seguridad() -> None:
    """The allow list is what lets ``/api/auth/token`` mint a token.

    The same entry with no live route is not a finding: that is the case of
    ``POST /api/auth/demo`` while the flag is off.
    """
    aplicacion = _aplicacion_con(None)

    assert (
        audit_scope_coverage(aplicacion, registry={}, public=frozenset({CLAVE_SONDA}))
        == ()
    )
    assert (
        audit_scope_coverage(
            FastAPI(),
            registry={},
            public=frozenset({RouteKey("POST", "/api/inexistente")}),
        )
        == ()
    )


def test_la_guardia_ignora_lo_que_no_cuelga_de_api() -> None:
    """The scope of the guard is explicit and minimal: API routes under /api.

    ``/health`` is anonymous by an acceptance criterion of US-001, and the
    documentation endpoints are mounted by FastAPI itself. Both are out by
    construction, not by an exception written for them.
    """
    aplicacion = _aplicacion_con(None, ruta="/health")

    assert live_routes(aplicacion) == ()
    assert _auditar(aplicacion) == ()


def test_la_ruta_que_es_el_prefijo_exacto_no_se_escapa() -> None:
    """``/api`` with no trailing slash is a route, and it was slipping through.

    ``APIRouter(prefix="/api")`` with ``@router.get("")`` produces the path
    ``/api`` exactly. A guard written as ``startswith("/api/")`` never sees it:
    the endpoint gets served with no security dependency and the startup stays
    quiet, which is the exact opposite of what this module exists for. Found by
    the security audit of 12-ago-2026 over the diff of US-016 and US-008.
    """
    enrutador = APIRouter(prefix=API_PREFIX)
    enrutador.add_api_route("", _endpoint_desnudo, methods=["GET"], name="raiz")
    aplicacion = FastAPI()
    aplicacion.include_router(enrutador)

    assert live_routes(aplicacion) == (RouteKey("GET", API_PREFIX),)
    assert _auditar(aplicacion) == (ViolationKind.SIN_SCOPES,)


def test_un_mount_bajo_api_es_una_violacion_y_no_un_silencio() -> None:
    """A sub application under /api cannot be governed, so it is reported.

    A ``Mount`` has no operation in the schema and no dependency tree FastAPI
    can enforce: nothing in this module can authorize it. Skipping it quietly
    would leave a route serving under the governed prefix while the guard
    swears the application is fully covered.
    """
    aplicacion = FastAPI()
    aplicacion.mount(f"{API_PREFIX}/interno", Starlette())

    violaciones = audit_scope_coverage(
        aplicacion, registry=REGISTRO_SINTETICO, public=frozenset()
    )

    assert [violacion.kind for violacion in violaciones] == [ViolationKind.RUTA_AJENA]
    assert violaciones[0].route == RouteKey("*", f"{API_PREFIX}/interno")


def test_un_mount_fuera_de_api_no_molesta() -> None:
    """The rule is about the governed prefix, not about mounts in general.

    Static files or a metrics exporter mounted elsewhere are none of this
    module's business, and a guard that cries wolf gets switched off.
    """
    aplicacion = FastAPI()
    aplicacion.mount("/estaticos", Starlette())

    assert _auditar(aplicacion) == ()


def test_auditar_no_congela_el_esquema_de_la_aplicacion() -> None:
    """Auditing must not freeze the document of an application still growing.

    ``app.openapi()`` caches its result, so a guard that left the cache behind
    would make every route mounted afterwards invisible to ``/openapi.json``.
    """
    aplicacion = _aplicacion_con([Scope.ANALISTA.value])
    _auditar(aplicacion)
    aplicacion.add_api_route(
        "/api/sintetica/tardia",
        _endpoint_protegido([Scope.ADMIN.value]),
        methods=["GET"],
        name="tardia",
    )

    assert "/api/sintetica/tardia" in aplicacion.openapi()["paths"]


def test_assert_scope_coverage_lanza_con_violaciones() -> None:
    """The wrapper used by ``create_app`` aborts instead of logging and going on.

    A test is skipped with ``-k``; a startup is not. In Cloud Run the revision
    never becomes healthy and the traffic stays where it was.
    """
    with pytest.raises(ScopeCoverageError) as error:
        assert_scope_coverage(_aplicacion_con(None))

    mensaje = str(error.value)
    assert ViolationKind.SIN_SCOPES.value in mensaje
    assert RUTA_SONDA in mensaje


def test_assert_scope_coverage_calla_cuando_todo_esta_gobernado(
    crear_aplicacion: Callable[..., FastAPI],
) -> None:
    """The real application passes the check it runs on itself at startup.

    Args:
        crear_aplicacion: Factory of real applications.
    """
    assert_scope_coverage(crear_aplicacion(demo=False))


@pytest.mark.parametrize("demo", [True, False])
def test_la_aplicacion_real_no_tiene_violaciones(
    crear_aplicacion: Callable[..., FastAPI], demo: bool
) -> None:
    """The real application is governed with the demo flag on and off.

    A route mounted behind a flag exists in one startup and not in the other, so
    the guard has to pass in both. With the flag on, ``POST /api/auth/demo`` is
    live and answers without credentials: it is in the allow list, and that is
    the entry whose absence would have killed ``make dev``.

    Args:
        crear_aplicacion: Factory of real applications.
        demo: State of ``DEMO_LOGIN_ENABLED``.
    """
    aplicacion = crear_aplicacion(demo=demo)
    rutas = live_routes(aplicacion)

    assert audit_scope_coverage(aplicacion) == ()
    assert (RouteKey("POST", "/api/auth/demo") in rutas) is demo
    assert RouteKey("GET", "/api/auth/token") not in rutas


def test_toda_ruta_viva_esta_declarada(
    crear_aplicacion: Callable[..., FastAPI],
) -> None:
    """Every live route is either public policy or a row of the registry.

    This is the invariant the document depends on: a route that is neither would
    be served by the portal and absent from ``docs/security.md``.

    Args:
        crear_aplicacion: Factory of real applications.
    """
    vivas = set(live_routes(crear_aplicacion(demo=True)))

    assert vivas
    assert vivas <= (set(SCOPE_REGISTRY) | PUBLIC_ROUTES)


def test_ningun_router_usa_depends_pelado() -> None:
    """``Depends(get_current_user)`` is the one defect the schema cannot see.

    It produces the same security requirement as ``Security(..., scopes=[])``,
    so the guard cannot tell them apart. The project rule is ``Security``, and
    this sweep is what enforces it.
    """
    ofensores = [
        ruta.name
        for ruta in sorted((BACKEND_APP / "api").rglob("*.py"))
        if "Depends(get_current_user)" in ruta.read_text(encoding="utf-8")
    ]

    assert ofensores == []


def test_la_jerarquia_no_se_compara_fuera_de_scopes() -> None:
    """A second comparison of the hierarchy would be a second policy.

    The decision lives in ``covers``: anywhere else it drifts, and the drift is
    invisible until a role is added.
    """
    ofensores = [
        str(ruta.relative_to(BACKEND_APP))
        for ruta in sorted(BACKEND_APP.rglob("*.py"))
        if ruta.name != "scopes.py"
        and "ROLE_HIERARCHY[" in ruta.read_text(encoding="utf-8")
    ]

    assert ofensores == []


def test_vocabulario_de_roles_en_un_solo_modulo() -> None:
    """The four role names are literals in exactly one module of the backend.

    A second spelling of a role is the ``admin`` against ``administrador``
    divergence of the frontend, this time inside the API, where it decides who
    reads what.
    """
    patron = re.compile("|".join(f'"{scope.value}"' for scope in Scope))
    ofensores = [
        str(ruta.relative_to(BACKEND_APP))
        for ruta in sorted(BACKEND_APP.rglob("*.py"))
        if ruta.name != "scopes.py" and patron.search(ruta.read_text(encoding="utf-8"))
    ]

    assert ofensores == []
