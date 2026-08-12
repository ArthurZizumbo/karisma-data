"""Project the backend permission registry onto the navigation map of the portal.

The frontend must not hold a hand written copy of the permission matrix: a copy
drifts on the first user story that adds an endpoint, and the drift is silent
because nothing compares the two. This script is the single direction of
derivation -``SCOPE_REGISTRY`` and ``ROLE_HIERARCHY`` in, one TypeScript module
out- and ``scripts/verificar_permisos_ui.sh`` proves nothing was edited by hand
afterwards.

Two inventories are crossed and neither is retyped here:

* the permission policy, imported from ``backend/app/core``;
* the A3 site map, read from ``frontend/app/utils/navegacion.ts``, which is the
  only place where a branch of the map is bound to a route.

What this file does declare, because it exists nowhere else, is which endpoints
each branch of the map consumes. That declaration is the point of the module and
the reason it aborts instead of guessing: a branch that names an endpoint the
registry does not know, a branch that declares endpoints and an explicit scope at
once, or a branch of the map with no declaration at all are all defects of the
declaration, and a generator that papers over them would emit a sidebar that
lies.

Usage::

    poetry -P backend run python scripts/generar_permisos_ui.py
    make permisos-ui
"""

import re
import sys
from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Final

from app.core.permissions import SCOPE_REGISTRY, RouteKey
from app.core.scopes import ROLE_HIERARCHY, Scope

REPO_ROOT: Final[Path] = Path(__file__).resolve().parents[1]
NAVEGACION: Final[Path] = REPO_ROOT / "frontend" / "app" / "utils" / "navegacion.ts"
SALIDA: Final[Path] = REPO_ROOT / "frontend" / "app" / "utils" / "permisos.generated.ts"

#: Identifier of the conversational assistant inside this module.
#:
#: It is not a branch of the A3 map: A3 draws it as cross cutting to the four
#: categories, so it has no module and never reaches ``SCOPE_POR_RAMA``. It needs
#: a key all the same, because its route is guarded like any other and its entry
#: in the sidebar hangs from the same resolution.
RAMA_ASISTENTE: Final[str] = "asistente"

#: A3 branch id -> endpoints it consumes, written as 'METHOD /path/template'.
#:
#: The exigency of a branch is the HIGHEST scope among its endpoints, because a
#: screen that calls two endpoints only works when both answer. Every string
#: below must exist in SCOPE_REGISTRY; the generator aborts otherwise, which is
#: what catches a route renamed in the backend.
MAPA_RAMA_ENDPOINTS: Final[Mapping[str, tuple[str, ...]]] = {
    "1.1": ("GET /api/catalog/search",),
    "1.5": ("GET /api/auth/me",),
    "2.1": ("GET /api/catalog/search", "GET /api/catalog/{entry_id}"),
    "2.2": ("POST /api/query/records",),
    "2.3": ("POST /api/export", "GET /api/export/{job_id}"),
    "2.4": ("GET /api/metrics/series", "POST /api/metrics/aggregate"),
    "3.1": ("GET /api/catalog/{entry_id}",),
    "3.3": ("GET /api/catalog/search",),
    "4.1": (
        "GET /api/users",
        "POST /api/users",
        "PATCH /api/users/{user_id}",
        "DELETE /api/users/{user_id}",
    ),
    RAMA_ASISTENTE: ("POST /api/chat",),
}

#: A3 branch id -> (explicit scope, reason). Only for branches with no endpoint.
#:
#: Seven of the sixteen branches of the map call nothing yet. Without a rule the
#: generator would have to guess, so each one declares its scope WITH its reason
#: and the generator refuses a branch that declares both endpoints and a scope.
#: Three of the seven carry a role written by hand -the administration ones- and
#: those three disappear on their own the day US-018 and US-019 declare their
#: endpoints. The other four are ``None``, which is not a role.
SCOPE_EXPLICITO: Final[Mapping[str, tuple[Scope | None, str]]] = {
    "1.2": (None, "Historial local del lector; no consulta al servidor"),
    "1.3": (None, "Favoritos del lector; misma razon que las busquedas recientes"),
    "1.4": (None, "Alertas propias; el endpoint llega con US-028"),
    "3.2": (None, "Linaje del catalogo; hoy se pinta desde la ficha ya cargada"),
    "4.2": (Scope.ADMIN, "Solicitudes de acceso; sus endpoints llegan con US-019"),
    "4.3": (Scope.ADMIN, "Bitacora de accesos; sus endpoints llegan con US-019"),
    "4.4": (Scope.ADMIN, "Integraciones; sus endpoints llegan con US-019"),
}

CABECERA: Final[str] = """\
// GENERATED FILE - do not edit by hand.
// Source:     backend/app/core/permissions.py (SCOPE_REGISTRY, US-016)
//             backend/app/core/scopes.py      (ROLE_HIERARCHY, US-016)
//             frontend/app/utils/navegacion.ts (MODULOS, the A3 site map)
// Generator:  scripts/generar_permisos_ui.py
// Regenerate: make permisos-ui
import type { RolUsuario } from '~/types/sesion'
"""

EXIT_OK: Final[int] = 0
EXIT_DECLARACION: Final[int] = 1


class DeclaracionInvalidaError(RuntimeError):
    """Raised when the declaration above cannot produce an honest map."""


class Rama:
    """One branch of the A3 site map, as ``navegacion.ts`` declares it.

    Attributes:
        id: A3 identifier, for example ``2.3``.
        ruta: Path of the screen that renders the branch.
        modulo: Identifier of the first level category the branch hangs from.
    """

    def __init__(self, identificador: str, ruta: str) -> None:
        """Store the branch and derive the module it belongs to.

        Args:
            identificador: A3 identifier of the branch.
            ruta: Path of the screen that renders it.
        """
        self.id = identificador
        self.ruta = ruta
        self.modulo = identificador.split(".")[0]


def leer_mapa_de_navegacion() -> tuple[dict[str, str], list[Rama], str]:
    """Read the A3 site map out of the TypeScript module that declares it.

    The map is not retyped here on purpose. ``navegacion.ts`` is the single
    source of truth of which branch is rendered by which route, and a second
    copy in Python would be one more thing to keep in step.

    Returns:
        The modules as identifier to path, the sixteen branches in declaration
        order, and the path of the assistant.

    Raises:
        DeclaracionInvalidaError: If the file cannot be parsed, which is what
            happens when the shape of the declaration changes.
    """
    texto = NAVEGACION.read_text(encoding="utf-8")

    bloque = re.search(
        r"export const MODULOS[\s\S]*?Object\.freeze\(\[([\s\S]*?)\n\]\)", texto
    )
    if bloque is None:
        raise DeclaracionInvalidaError(
            f"no se encontro el bloque MODULOS en {NAVEGACION}: "
            "cambio la forma de la declaracion del mapa de A3"
        )

    modulos: dict[str, str] = {}
    ramas: list[Rama] = []
    patron = r"id:\s*'([^']+)',\s*claveEtiqueta:\s*'[^']+',\s*ruta:\s*'([^']+)'"
    for entrada in re.finditer(patron, bloque.group(1)):
        identificador, ruta = entrada.group(1), entrada.group(2)
        if "." in identificador:
            ramas.append(Rama(identificador, ruta))
        else:
            modulos[identificador] = ruta

    asistente = re.search(r"export const RUTA_ASISTENTE\s*=\s*'([^']+)'", texto)
    if not modulos or not ramas or asistente is None:
        raise DeclaracionInvalidaError(
            f"{NAVEGACION} declaro {len(modulos)} modulos, {len(ramas)} ramas y "
            f"{'no ' if asistente is None else ''}la ruta del asistente"
        )

    huerfanas = sorted(rama.id for rama in ramas if rama.modulo not in modulos)
    if huerfanas:
        raise DeclaracionInvalidaError(
            f"las ramas {huerfanas} cuelgan de un modulo que el mapa no declara"
        )

    return modulos, ramas, asistente.group(1)


def resolver_scope_de_rama(rama: str) -> Scope | None:
    """Return the highest scope among the endpoints of a branch.

    Args:
        rama: A3 identifier of the branch, or the assistant identifier.

    Returns:
        The role the branch demands, or ``None`` when any valid session is
        enough.

    Raises:
        DeclaracionInvalidaError: If the branch declares endpoints and an
            explicit scope at once, declares neither, or names an endpoint that
            is not in the registry.
    """
    endpoints = MAPA_RAMA_ENDPOINTS.get(rama)
    explicito = SCOPE_EXPLICITO.get(rama)

    if endpoints is not None and explicito is not None:
        raise DeclaracionInvalidaError(
            f"la rama {rama} declara endpoints y scope explicito a la vez: "
            "una visibilidad no se arregla tecleando un rol, se arregla "
            "declarando el endpoint que falta"
        )
    if endpoints is None and explicito is None:
        raise DeclaracionInvalidaError(
            f"la rama {rama} del mapa de A3 no tiene declaracion: anadela a "
            "MAPA_RAMA_ENDPOINTS o, si no consume ningun endpoint, a "
            "SCOPE_EXPLICITO con su motivo"
        )
    if endpoints is None:
        # Narrowed by the two guards above.
        assert explicito is not None  # noqa: S101
        return explicito[0]

    return _mayor(_scope_de_endpoint(rama, endpoint) for endpoint in endpoints)


def resolver_scope_de_ruta(ruta: str, ramas: Iterable[Rama]) -> Scope | None:
    """Return the lowest scope among the branches a route renders.

    The minimum and not the maximum: a screen is worth opening when at least one
    of the branches it holds is usable. With the maximum, the exploration screen
    would demand ``analista`` because of its exports panel and the operations
    profile would lose the ad hoc query, which is its job.

    Args:
        ruta: Path of the screen.
        ramas: Branches of the map, already read from ``navegacion.ts``.

    Returns:
        The role the route demands, or ``None`` when any valid session is
        enough.
    """
    return _menor(
        resolver_scope_de_rama(rama.id) for rama in ramas if rama.ruta == ruta
    )


def emitir_typescript() -> str:
    """Render the whole generated module as text.

    Returns:
        The TypeScript source, deterministic and idempotent: the same registry
        and the same site map always produce the same bytes.
    """
    modulos, ramas, ruta_asistente = leer_mapa_de_navegacion()
    _validar_declaracion(ramas)

    scope_por_rama: dict[str, Scope | None] = {}
    for identificador in sorted(modulos, key=_orden_de_rama):
        scope_por_rama[identificador] = _menor(
            resolver_scope_de_rama(rama.id)
            for rama in ramas
            if rama.modulo == identificador
        )
    for rama in sorted(ramas, key=lambda candidata: _orden_de_rama(candidata.id)):
        scope_por_rama[rama.id] = resolver_scope_de_rama(rama.id)

    rutas = list(dict.fromkeys([*modulos.values(), *(rama.ruta for rama in ramas)]))
    scope_por_ruta: dict[str, Scope | None] = {
        ruta: resolver_scope_de_ruta(ruta, ramas) for ruta in rutas
    }
    scope_por_ruta[ruta_asistente] = resolver_scope_de_rama(RAMA_ASISTENTE)

    endpoints_por_rama = {
        identificador: MAPA_RAMA_ENDPOINTS.get(identificador, ())
        for identificador in sorted(
            [rama.id for rama in ramas] + [RAMA_ASISTENTE], key=_orden_de_rama
        )
    }

    roles = [
        scope.value for scope in sorted(ROLE_HIERARCHY, key=lambda s: ROLE_HIERARCHY[s])
    ]

    return "\n".join(
        [
            CABECERA,
            _bloque_roles(roles),
            "",
            _bloque_scopes(
                "SCOPE_POR_RAMA",
                (
                    "Minimum role of every module and every branch of the A3 map, "
                    "keyed by\n * its A3 id. A module demands the lowest of its "
                    "branches; a branch demands the\n * highest of the endpoints "
                    "it calls."
                ),
                scope_por_rama,
            ),
            "",
            _bloque_scopes(
                "SCOPE_POR_RUTA",
                (
                    "Minimum role of every route of the navigation contract, "
                    "keyed by path.\n * '/acceso' is absent on purpose: the entry "
                    "screen is public, and guarding it\n * would redirect it to "
                    "itself."
                ),
                scope_por_ruta,
            ),
            "",
            _bloque_endpoints(endpoints_por_rama),
        ]
    )


def main() -> int:
    """Write the generated module, or explain the declaration defect.

    Returns:
        ``0`` when the file was written, ``1`` when the declaration is invalid.
    """
    try:
        contenido = emitir_typescript()
    except DeclaracionInvalidaError as error:
        print(f"FALLA: {error}", file=sys.stderr)
        return EXIT_DECLARACION

    SALIDA.write_text(contenido, encoding="utf-8", newline="\n")
    print(f"Escrito {SALIDA.relative_to(REPO_ROOT).as_posix()}")
    return EXIT_OK


def _validar_declaracion(ramas: list[Rama]) -> None:
    """Check that the declaration covers the map and nothing else.

    Args:
        ramas: Branches read from ``navegacion.ts``.

    Raises:
        DeclaracionInvalidaError: If a declared identifier is not a branch of
            the map, or a branch of the map has no declaration.
    """
    del_mapa = {rama.id for rama in ramas} | {RAMA_ASISTENTE}
    declarados = set(MAPA_RAMA_ENDPOINTS) | set(SCOPE_EXPLICITO)

    sobrantes = sorted(declarados - del_mapa)
    if sobrantes:
        raise DeclaracionInvalidaError(
            f"las declaraciones {sobrantes} no corresponden a ninguna rama del "
            "mapa de A3: se renombraron o se borraron de navegacion.ts"
        )

    faltantes = sorted(del_mapa - declarados)
    if faltantes:
        raise DeclaracionInvalidaError(
            f"las ramas {faltantes} del mapa de A3 no tienen declaracion: sin "
            "ella la barra lateral las mostraria a todo el mundo"
        )


def _scope_de_endpoint(rama: str, endpoint: str) -> Scope | None:
    """Return the scope one endpoint demands, according to the registry.

    Args:
        rama: Branch that declared the endpoint, named in the error message.
        endpoint: Declaration, as ``'METHOD /path/template'``.

    Returns:
        The highest role the endpoint declares, or ``None`` when it admits any
        authenticated caller.

    Raises:
        DeclaracionInvalidaError: If the endpoint is not in ``SCOPE_REGISTRY``.
    """
    metodo, _, ruta = endpoint.partition(" ")
    regla = SCOPE_REGISTRY.get(RouteKey(metodo, ruta))
    if regla is None:
        raise DeclaracionInvalidaError(
            f"la rama {rama} declara '{endpoint}', que no existe en "
            "SCOPE_REGISTRY: la ruta se renombro en el backend o falta su fila"
        )
    return _mayor(iter(regla.scopes))


def _mayor(scopes: Iterable[Scope | None]) -> Scope | None:
    """Return the highest of several scopes.

    Args:
        scopes: Scopes to compare. ``None`` means "any valid session", which is
            below every role.

    Returns:
        The highest one, or ``None`` when they are all ``None`` or there is
        none.
    """
    reales = [scope for scope in scopes if scope is not None]
    return max(reales, key=lambda scope: ROLE_HIERARCHY[scope]) if reales else None


def _menor(scopes: Iterable[Scope | None]) -> Scope | None:
    """Return the lowest of several scopes.

    Args:
        scopes: Scopes to compare. ``None`` means "any valid session", which is
            below every role and therefore wins the minimum.

    Returns:
        The lowest one, or ``None`` when any of them is ``None`` or there is
        none.
    """
    materializados = list(scopes)
    if not materializados or any(scope is None for scope in materializados):
        return None
    return min(
        (scope for scope in materializados if scope is not None),
        key=lambda scope: ROLE_HIERARCHY[scope],
    )


def _orden_de_rama(identificador: str) -> tuple[int, ...]:
    """Sort key that orders '2.10' after '2.9' and leaves the assistant last.

    Args:
        identificador: A3 identifier or the assistant identifier.

    Returns:
        A tuple of integers, or a sentinel that sorts after every branch.
    """
    if not identificador[0].isdigit():
        return (999,)
    return tuple(int(tramo) for tramo in identificador.split("."))


def _valor_ts(scope: Scope | None) -> str:
    """Render a scope as the TypeScript literal the frontend reads.

    Args:
        scope: Scope to render.

    Returns:
        The quoted role, or ``null``.
    """
    return "null" if scope is None else f"'{scope.value}'"


def _bloque_roles(roles: list[str]) -> str:
    """Render the ordered role vocabulary.

    Args:
        roles: Role names, from lowest to highest.

    Returns:
        The exported constant, with its documentation comment.
    """
    miembros = "\n".join(f"  '{rol}'," for rol in roles)
    return (
        "/** The four roles, from lowest to highest, mirroring ROLE_HIERARCHY. */\n"
        "export const ROLES_EN_ORDEN: readonly RolUsuario[] = Object.freeze([\n"
        f"{miembros}\n"
        "])"
    )


def _bloque_scopes(
    nombre: str, descripcion: str, entradas: Mapping[str, Scope | None]
) -> str:
    """Render one of the two scope maps.

    Args:
        nombre: Name of the exported constant.
        descripcion: Body of its documentation comment, already wrapped.
        entradas: Keys and resolved scopes, in the order they must be emitted.

    Returns:
        The exported constant, with its documentation comment.
    """
    filas = "\n".join(
        f"  '{clave}': {_valor_ts(scope)}," for clave, scope in entradas.items()
    )
    return (
        f"/**\n * {descripcion}\n */\n"
        f"export const {nombre}: Readonly<Record<string, RolUsuario | null>>"
        " = Object.freeze({\n"
        f"{filas}\n"
        "})"
    )


def _bloque_endpoints(entradas: Mapping[str, tuple[str, ...]]) -> str:
    """Render the endpoint inventory each branch consumes.

    Args:
        entradas: Branch identifier to endpoints, in the order to be emitted.

    Returns:
        The exported constant, with its documentation comment.
    """
    filas: list[str] = []
    for clave, endpoints in entradas.items():
        if not endpoints:
            filas.append(f"  '{clave}': [],")
            continue
        interior = "".join(f"    '{endpoint}',\n" for endpoint in endpoints)
        filas.append(f"  '{clave}': [\n{interior}  ],")
    cuerpo = "\n".join(filas)
    return (
        "/**\n"
        " * Endpoints every branch consumes, as 'METHOD /path/template'.\n"
        " *\n"
        " * Only test/permisos.spec.ts reads this: it crosses the list against "
        "the matrix\n"
        " * published in docs/security.md, so a scope changed in the backend "
        "and not\n"
        " * regenerated here turns the suite red instead of hiding a module "
        "from the\n"
        " * wrong people.\n"
        " */\n"
        "export const ENDPOINTS_POR_RAMA: Readonly<Record<string, readonly string[]>>"
        " = Object.freeze({\n"
        f"{cuerpo}\n"
        "})"
    )


if __name__ == "__main__":
    sys.exit(main())
