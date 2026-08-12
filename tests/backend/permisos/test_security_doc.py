"""Tests that keep ``docs/security.md`` from drifting away from the policy.

The permission matrix of the document is generated, not written. That is the
whole point: the gate of 6-ago was lost because a document nobody could check
said what the code did not do. Here the block between the markers is compared
line by line with what the renderer emits, so editing the table by hand turns
the suite red.

What is deliberately not tested is whether the prose of the out of scope
section names each discarded mechanism. A grep over prose does not find a
defect, it finds a word, and it would pass with the sentence written backwards.
That belongs to the closing checklist, with a human reading it.
"""

import re
from pathlib import Path
from typing import Final

import pytest

from app.core.permissions import (
    API_PREFIX,
    MATRIX_BEGIN,
    MATRIX_END,
    PUBLIC_ROUTES,
    SCOPE_REGISTRY,
    PermissionRule,
    RouteKey,
    render_permission_matrix,
)
from app.core.scopes import ErrorCode, Scope

DOCUMENTO: Final[Path] = Path(__file__).resolve().parents[3] / "docs" / "security.md"

# The twelve sections the planning document fixed for this file. The list is
# written out so that trimming the document to its table has something to fail
# against.
SECCIONES_ESPERADAS: Final[tuple[str, ...]] = (
    "1. Alcance y fuente de verdad",
    "2. Roles y jerarquía",
    "3. Matriz de permisos",
    "4. Contrato HTTP y códigos de error",
    "5. Canal de credenciales y CSRF",
    "6. Herencia del Bearer al agente",
    "7. Cómo se añade un endpoint nuevo",
    "8. Modelo de amenazas",
    "9. Privacidad de los registros",
    "10. Fuera de alcance",
    "11. Deuda aceptada",
    "12. Bitácora",
)

_METODOS_VALIDOS: Final[frozenset[str]] = frozenset(
    {"GET", "POST", "PUT", "PATCH", "DELETE"}
)

_CLAVE_I18N: Final[str] = "errores.autorizacion"

# Rows of the policy, ordered so that the identifiers of the cases are stable.
FILAS_DEL_REGISTRO: Final[list[tuple[RouteKey, PermissionRule]]] = sorted(
    SCOPE_REGISTRY.items(), key=lambda entrada: str(entrada[0])
)


def _texto() -> str:
    """Read the document.

    Returns:
        The whole file, with the line endings of Windows normalized.
    """
    return DOCUMENTO.read_text(encoding="utf-8").replace("\r\n", "\n")


def _fila_de(codigo: ErrorCode) -> list[str]:
    """Return the cells of the row that documents an error code.

    Args:
        codigo: Code to look for.

    Returns:
        The cells of the row, stripped, without the empty ends.
    """
    prefijo = f"| `{codigo.value}` |"
    filas = [linea for linea in _texto().splitlines() if linea.startswith(prefijo)]
    assert len(filas) == 1, f"{codigo.value} deberia tener una fila, hay {len(filas)}"
    return [celda.strip() for celda in filas[0].strip("|").split("|")]


def test_el_documento_existe() -> None:
    """The file the gate of 6-ago asked for is in the repository."""
    assert DOCUMENTO.is_file()


def test_el_bloque_del_documento_coincide_con_el_registro() -> None:
    """The generated table is identical to what the renderer emits.

    Anyone who edits the table by hand, or who changes the registry without
    regenerating, finds this test red. Without it the document is decorative
    again, which is exactly how the gate was lost the first time.
    """
    texto = _texto()

    assert texto.count(MATRIX_BEGIN) == 1
    assert texto.count(MATRIX_END) == 1
    bloque = texto.split(MATRIX_BEGIN, 1)[1].split(MATRIX_END, 1)[0]

    assert bloque.strip("\n") == render_permission_matrix()


def test_el_documento_tiene_las_doce_secciones() -> None:
    """The twelve level two sections are there, in order.

    The table is the part that gets copied around; the threat model, the out of
    scope list and the recipe for a new endpoint are the parts that get lost.
    """
    titulos = [
        linea.removeprefix("## ").strip()
        for linea in _texto().splitlines()
        if linea.startswith("## ")
    ]

    assert tuple(titulos) == SECCIONES_ESPERADAS


@pytest.mark.parametrize("codigo", list(ErrorCode))
def test_los_codigos_de_error_estan_documentados_en_los_dos_locales(
    codigo: ErrorCode,
) -> None:
    """Every code carries its i18n key and its copy in Spanish and in English.

    The backend answers with the code and never with the sentence, so a code
    without a row leaves US-017 with a screen it cannot write in either locale.

    Args:
        codigo: Code that must be documented.
    """
    celdas = _fila_de(codigo)

    assert len(celdas) == 4, f"la fila de {codigo.value} no tiene cuatro columnas"
    _, clave, espanol, ingles = celdas
    assert clave == f"`{_CLAVE_I18N}.{codigo.value}`"
    assert espanol and ingles
    assert espanol != ingles


def test_la_jerarquia_de_roles_esta_publicada() -> None:
    """The four canonical role names appear in the document.

    US-017 reads the vocabulary from here to label the interface, and the
    divergence this file exists to stop is a role spelled a second way.
    """
    texto = _texto()

    for scope in Scope:
        assert f"`{scope.value}`" in texto


@pytest.mark.parametrize(("clave", "regla"), FILAS_DEL_REGISTRO, ids=str)
def test_toda_regla_del_registro_tiene_us_y_estado(
    clave: RouteKey, regla: PermissionRule
) -> None:
    """Every row names its owner, its state and its reason.

    A row without an owner is a rule nobody implements, and in two weeks nobody
    remembers who was supposed to.

    Args:
        clave: Route the row describes.
        regla: Policy of that route.
    """
    assert re.fullmatch(r"US-\d{3}", regla.us), f"{clave} sin US valida"
    assert regla.status in {"vigente", "planificado"}
    assert regla.rule.strip()
    assert not regla.public


@pytest.mark.parametrize("clave", sorted(set(SCOPE_REGISTRY) | PUBLIC_ROUTES), ids=str)
def test_toda_ruta_del_registro_cuelga_de_api(clave: RouteKey) -> None:
    """The policy only governs what the guard audits: routes under ``/api``.

    A row for ``/health`` or ``/docs`` would extend the policy to routes the
    guard never looks at, and the document would promise something nobody
    enforces.

    Args:
        clave: Route declared by the policy.
    """
    assert clave.path.startswith(f"{API_PREFIX}/")
    assert clave.method in _METODOS_VALIDOS
    assert clave.path == clave.path.rstrip("/")


def test_la_lista_blanca_y_el_registro_no_se_solapan() -> None:
    """A route is public or governed, never both.

    Both structures feed the guard: an overlap would make the audit depend on
    which of the two is read first.
    """
    assert not (PUBLIC_ROUTES & set(SCOPE_REGISTRY))


@pytest.mark.parametrize("clave", sorted(PUBLIC_ROUTES), ids=str)
def test_las_rutas_publicas_se_publican_como_tales(clave: RouteKey) -> None:
    """A public route cannot demand a role: it answers before there is a token.

    The document has to say so where a reader looks for it, in the matrix, and
    not only in the prose of the section above it.

    Args:
        clave: Route of the allow list.
    """
    filas = [
        linea
        for linea in render_permission_matrix().splitlines()
        if linea.startswith(f"| `{clave}` |")
    ]

    assert len(filas) == 1
    assert "*(publica)*" in filas[0]
    assert not any(f"`{scope.value}`" in filas[0] for scope in Scope)
    assert filas[0] in _texto()
