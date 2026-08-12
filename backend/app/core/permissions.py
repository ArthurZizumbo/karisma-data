"""Permission policy of every route under ``/api``.

The registry below is the single source of truth of the permission matrix: the
guard that walks the application, the parametrized 401/403 test suite and the
table printed in ``docs/security.md`` all read this mapping. Adding an endpoint
without adding its row here makes the suite red and stops the application from
starting, which is the whole point of the module.

The module answers "what does each route demand and who checks it". It knows
nothing about passwords, tokens or sessions: the meaning of a role lives in
``app.core.scopes`` and the resolution of a caller lives in ``app.core.auth``.
"""

from collections.abc import Iterator, Mapping
from collections.abc import Set as AbstractSet
from dataclasses import dataclass
from enum import StrEnum
from itertools import chain
from types import MappingProxyType
from typing import Any, Final, Literal

import structlog
from fastapi import FastAPI
from fastapi.routing import APIRoute, iter_route_contexts

from app.core.scopes import Scope

logger = structlog.get_logger()

API_PREFIX: Final[str] = "/api"

# Delimiters of the generated block in docs/security.md. The document is not
# allowed to drift from this module, and these two lines are how the test
# tells the generated table from the prose around it.
MATRIX_BEGIN: Final[str] = "<!-- matriz-permisos:inicio -->"
MATRIX_END: Final[str] = "<!-- matriz-permisos:fin -->"

_MATRIX_HEADER: Final[tuple[str, str]] = (
    "| Metodo y ruta | Scopes | Regla | US | Estado |",
    "|---|---|---|---|---|",
)

_PUBLIC_CELL: Final[str] = "*(publica)*"
_AUTHENTICATED_CELL: Final[str] = "*(ninguno)*"

# Verbs that can carry an operation in an OpenAPI path item. Anything else in a
# path item -parameters, summary, servers- is metadata, not an operation.
_HTTP_METHODS: Final[frozenset[str]] = frozenset(
    {"GET", "PUT", "POST", "DELETE", "OPTIONS", "HEAD", "PATCH", "TRACE"}
)

RouteStatus = Literal["vigente", "planificado"]


@dataclass(frozen=True, order=True)
class RouteKey:
    """HTTP method and path template of a route, as FastAPI declares it.

    Attributes:
        method: Upper case verb, for example ``GET``.
        path: Path template with its parameters, for example
            ``/api/export/{job_id}``.
    """

    method: str
    path: str

    def __str__(self) -> str:
        """Render the key the way the document and the log messages show it.

        Returns:
            The verb and the path separated by a space.
        """
        return f"{self.method} {self.path}"


@dataclass(frozen=True)
class PermissionRule:
    """What a route demands, who owns it and whether it already exists.

    Attributes:
        scopes: Roles the endpoint declares. An empty tuple means that any
            authenticated caller is allowed, which is not the same rule as
            requiring ``operativo`` even though today both admit everybody.
        rule: Spanish prose printed in the document. It is the reason, and the
            reason is the part a registry entry cannot be written without.
        us: Identifier of the user story that owns the endpoint.
        status: Whether the route is already mounted or only declared ahead of
            time.
        public: Whether the route is reachable without a token at all. A public
            route never declares scopes: it is in the allow list of the guard.
    """

    scopes: tuple[Scope, ...]
    rule: str
    us: str
    status: RouteStatus
    public: bool = False


class ViolationKind(StrEnum):
    """Class of scope coverage defect found by the guard."""

    SIN_SCOPES = "sin_scopes"
    FUERA_DEL_REGISTRO = "fuera_del_registro"
    SCOPE_DIVERGENTE = "scope_divergente"
    RUTA_OCULTA = "ruta_oculta"


@dataclass(frozen=True)
class ScopeViolation:
    """A single finding, with the route and the human readable reason.

    Attributes:
        kind: Class of the defect.
        route: Route that produced it.
        detail: Spanish explanation, printed at startup and in the test output.
    """

    kind: ViolationKind
    route: RouteKey
    detail: str

    def __str__(self) -> str:
        """Render the finding as one line of the startup error.

        Returns:
            The class, the route and the reason.
        """
        return f"{self.kind.value}: {self.route} - {self.detail}"


class ScopeCoverageError(RuntimeError):
    """Raised at startup when a route under ``/api`` is not governed."""


# Routes that answer without a token. The list is deliberately tiny: an
# exception granted by prefix -"everything under /api/auth"- would let a
# GET /api/auth/usuarios through tomorrow for living in the right neighbourhood.
_PUBLIC_POLICY: Final[Mapping[RouteKey, PermissionRule]] = MappingProxyType(
    {
        RouteKey("POST", "/api/auth/token"): PermissionRule(
            scopes=(),
            rule="Emite el token; no puede exigirlo",
            us="US-015",
            status="vigente",
            public=True,
        ),
        RouteKey("POST", "/api/auth/demo"): PermissionRule(
            scopes=(),
            rule=(
                "Emite token sin credenciales, como /token; existe solo cuando "
                "DEMO_LOGIN_ENABLED es verdadero"
            ),
            us="US-015",
            status="vigente",
            public=True,
        ),
    }
)

PUBLIC_ROUTES: Final[frozenset[RouteKey]] = frozenset(_PUBLIC_POLICY)

# The policy of every governed route. Rows whose status is "planificado" are
# published ahead of the endpoint on purpose: a row without a live route is not
# a violation, a live route without a row is.
SCOPE_REGISTRY: Final[Mapping[RouteKey, PermissionRule]] = MappingProxyType(
    {
        RouteKey("GET", "/api/auth/me"): PermissionRule(
            scopes=(),
            rule="Cualquier sesion valida consulta su propio perfil",
            us="US-015",
            status="vigente",
        ),
        RouteKey("GET", "/api/catalog/search"): PermissionRule(
            scopes=(),
            rule="Catalogo para todos los autenticados",
            us="US-008",
            status="planificado",
        ),
        RouteKey("GET", "/api/catalog/{entry_id}"): PermissionRule(
            scopes=(),
            rule="Ficha de catalogo, mismo criterio",
            us="US-008",
            status="planificado",
        ),
        RouteKey("POST", "/api/query/records"): PermissionRule(
            scopes=(Scope.OPERATIVO,),
            rule="Consulta puntual sobre un silo",
            us="US-011",
            status="planificado",
        ),
        RouteKey("GET", "/api/metrics/series"): PermissionRule(
            scopes=(Scope.ANALISTA,),
            rule="Serie preagregada del tablero",
            us="US-025",
            status="planificado",
        ),
        RouteKey("POST", "/api/metrics/aggregate"): PermissionRule(
            scopes=(Scope.ANALISTA,),
            rule="Agregaciones y cruces de la capa semantica",
            us="US-011",
            status="planificado",
        ),
        RouteKey("POST", "/api/export"): PermissionRule(
            scopes=(Scope.ANALISTA,),
            rule="Exportacion en segundo plano",
            us="US-009",
            status="planificado",
        ),
        RouteKey("GET", "/api/export/{job_id}"): PermissionRule(
            scopes=(Scope.ANALISTA,),
            rule="Estado del trabajo y enlace firmado",
            us="US-009",
            status="planificado",
        ),
        RouteKey("GET", "/api/summaries/executive"): PermissionRule(
            scopes=(Scope.DIRECTIVO,),
            rule="Resumenes directivos",
            us="US-026",
            status="planificado",
        ),
        RouteKey("GET", "/api/users"): PermissionRule(
            scopes=(Scope.ADMIN,),
            rule="Gestion de usuarios",
            us="US-018",
            status="planificado",
        ),
        RouteKey("POST", "/api/users"): PermissionRule(
            scopes=(Scope.ADMIN,),
            rule="Alta de usuario",
            us="US-018",
            status="planificado",
        ),
        RouteKey("PATCH", "/api/users/{user_id}"): PermissionRule(
            scopes=(Scope.ADMIN,),
            rule="Cambio de rol; un admin no se degrada a si mismo",
            us="US-018",
            status="planificado",
        ),
        RouteKey("DELETE", "/api/users/{user_id}"): PermissionRule(
            scopes=(Scope.ADMIN,),
            rule="Borrado logico; un admin no se desactiva a si mismo",
            us="US-018",
            status="planificado",
        ),
        RouteKey("POST", "/api/chat"): PermissionRule(
            scopes=(),
            rule=(
                "El agente propaga el Bearer del usuario; cada tool cae en la "
                "fila del endpoint que envuelve"
            ),
            us="US-023",
            status="planificado",
        ),
    }
)


def live_routes(app: FastAPI) -> tuple[RouteKey, ...]:
    """List the routes under ``/api`` the application actually serves today.

    Args:
        app: Application to inspect, already built.

    Returns:
        The keys of every mounted API route, sorted and without duplicates.
    """
    return tuple(sorted(set(_walk_api_routes(app))))


def audit_scope_coverage(
    app: FastAPI,
    *,
    registry: Mapping[RouteKey, PermissionRule] = SCOPE_REGISTRY,
    public: AbstractSet[RouteKey] = PUBLIC_ROUTES,
) -> tuple[ScopeViolation, ...]:
    """Return every scope coverage violation of the application.

    Two inventories are crossed instead of one. The OpenAPI schema carries the
    security requirements, which is what tells a governed route from a forgotten
    one, but a route declared with ``include_in_schema=False`` never reaches it;
    the list of mounted routes carries those. A route in the second inventory
    and not in the first is a hidden route, not a silence.

    The registry and the allow list are parameters so that the guard can be
    tested against synthetic applications instead of being trusted.

    Args:
        app: Application to audit, already built.
        registry: Policy to audit against. Defaults to the policy of the portal.
        public: Routes allowed to answer without a token.

    Returns:
        One violation per offending route, sorted by route, empty when the
        application is fully governed.
    """
    declared = _declared_scopes(app)
    violations: list[ScopeViolation] = []

    for key in live_routes(app):
        if key in public:
            continue

        if key not in declared:
            violations.append(
                ScopeViolation(
                    kind=ViolationKind.RUTA_OCULTA,
                    route=key,
                    detail=(
                        "La ruta no aparece en el esquema OpenAPI "
                        "(include_in_schema=False) y no esta en la lista blanca"
                    ),
                )
            )
            continue

        scopes = declared[key]
        if scopes is None:
            violations.append(
                ScopeViolation(
                    kind=ViolationKind.SIN_SCOPES,
                    route=key,
                    detail=(
                        "La operacion no declara ningun requisito de seguridad: "
                        "falta Security(get_current_user, scopes=[...])"
                    ),
                )
            )
            continue

        rule = registry.get(key)
        if rule is None:
            violations.append(
                ScopeViolation(
                    kind=ViolationKind.FUERA_DEL_REGISTRO,
                    route=key,
                    detail=(
                        "La ruta esta protegida pero no tiene fila en "
                        "SCOPE_REGISTRY, asi que no aparece en docs/security.md"
                    ),
                )
            )
            continue

        expected = tuple(sorted(scope.value for scope in rule.scopes))
        if scopes != expected:
            violations.append(
                ScopeViolation(
                    kind=ViolationKind.SCOPE_DIVERGENTE,
                    route=key,
                    detail=(
                        f"El codigo exige {list(scopes)} y la politica declara "
                        f"{list(expected)}"
                    ),
                )
            )

    return tuple(violations)


def assert_scope_coverage(app: FastAPI) -> None:
    """Raise ``ScopeCoverageError`` when the application is not fully governed.

    This is the third layer of the mechanism and the only one that cannot be
    skipped: a test is avoided with ``-k``, a startup is not. In Cloud Run the
    revision does not become healthy and the traffic stays on the previous one,
    so a badly governed deployment fails closed.

    Args:
        app: Application to audit, already built.

    Raises:
        ScopeCoverageError: If any route under ``/api`` is not governed.
    """
    violations = audit_scope_coverage(app)
    if not violations:
        return

    logger.critical(
        "cobertura_de_scopes_incompleta",
        violaciones=[str(violation) for violation in violations],
    )
    detail = "; ".join(str(violation) for violation in violations)
    message = (
        f"{len(violations)} ruta(s) bajo {API_PREFIX} sin gobierno de permisos: "
        f"{detail}"
    )
    raise ScopeCoverageError(message)


def render_permission_matrix() -> str:
    """Render the registry as the markdown table embedded in ``docs/security.md``.

    Returns:
        The table, without the surrounding markers and without a trailing
        newline, so that the document and this function can be compared line by
        line.
    """
    rows = [
        _matrix_row(key, rule)
        for key, rule in chain(_PUBLIC_POLICY.items(), SCOPE_REGISTRY.items())
    ]
    return "\n".join([*_MATRIX_HEADER, *rows])


def _matrix_row(key: RouteKey, rule: PermissionRule) -> str:
    """Render one row of the permission matrix.

    Args:
        key: Route the row describes.
        rule: Policy of that route.

    Returns:
        The markdown row, pipes included.
    """
    if rule.public:
        scopes = _PUBLIC_CELL
    elif not rule.scopes:
        scopes = _AUTHENTICATED_CELL
    else:
        scopes = " ".join(f"`{scope.value}`" for scope in rule.scopes)
    return f"| `{key}` | {scopes} | {rule.rule} | {rule.us} | {rule.status} |"


def _walk_api_routes(app: FastAPI) -> Iterator[RouteKey]:
    """Yield one key per method of every mounted API route under ``/api``.

    ``app.routes`` is not a flat list of ``APIRoute`` any more: since FastAPI
    0.141 ``include_router`` stores a lazy branch, so the routes are flattened
    with ``iter_route_contexts``, the same helper the public ``get_openapi``
    consumes. Only ``APIRoute`` is considered: the documentation endpoints and
    anything mounted by Starlette are out of scope by construction, and so is
    ``/health``, which does not hang from ``/api``.

    Args:
        app: Application to inspect, already built.

    Yields:
        The key of every method of every API route under the prefix.
    """
    for context in iter_route_contexts(app.routes):
        if not isinstance(context.original_route, APIRoute):
            continue
        path = context.path
        if path is None or not path.startswith(f"{API_PREFIX}/"):
            continue
        for method in context.methods or ():
            yield RouteKey(method.upper(), path)


def _declared_scopes(app: FastAPI) -> dict[RouteKey, tuple[str, ...] | None]:
    """Read the scopes every documented operation declares, from the schema.

    The schema is public and stable API, unlike the dependency tree, and it is
    what the interactive documentation shows: auditing it means auditing what
    the portal publishes about itself. The cached schema of the application is
    restored afterwards so that a call to the guard never freezes the document
    of an application that still has routes to mount.

    Args:
        app: Application to inspect, already built.

    Returns:
        The declared scopes per operation, sorted; ``None`` when the operation
        declares no security requirement at all.
    """
    cached = app.openapi_schema
    try:
        schema: dict[str, Any] = app.openapi()
    finally:
        app.openapi_schema = cached

    declared: dict[RouteKey, tuple[str, ...] | None] = {}
    for path, path_item in schema.get("paths", {}).items():
        for method, operation in path_item.items():
            if method.upper() not in _HTTP_METHODS or not isinstance(operation, dict):
                continue
            declared[RouteKey(method.upper(), path)] = _requirement_scopes(operation)
    return declared


def _requirement_scopes(operation: dict[str, Any]) -> tuple[str, ...] | None:
    """Collect the scopes of every security requirement of one operation.

    Args:
        operation: Operation object of the OpenAPI schema.

    Returns:
        The union of the scopes of every requirement, sorted; ``None`` when the
        operation carries no requirement.
    """
    requirements = operation.get("security")
    if not requirements:
        return None
    names: set[str] = set()
    for requirement in requirements:
        for scopes in requirement.values():
            names.update(str(scope) for scope in scopes)
    return tuple(sorted(names))
