"""Contract tests for the design token emitter of the A4 style guide.

The guide only means something if the application and the PDF cannot diverge.
Every assertion below fixes one of the conditions that make that true: the
stylesheet keeps declaring the thirty seven colours, the eleven anchors that
three delivered documents compile against never move, the WCAG formula returns
the published numbers, the four contrast defects stay detected, the emitter
holds no colour of its own, two runs write the same bytes, the US-001 aliases
keep coming from the scale and the version is the same in the three outputs.

The reference values are typed here on purpose: an invariant that reads the
same file it watches proves nothing.
"""

import importlib.util
import re
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
RUTA_GENERADOR = REPO_ROOT / "docs" / "entregables" / "generar_tokens_a4.py"
RUTA_FUENTE = REPO_ROOT / "docs" / "entregables" / "estilo" / "uxdoc.sty"

PATRON_HEX = re.compile(r"#[0-9A-Fa-f]{6}")

#: The emitter is loaded by path, so its frozen dataclasses have no static
#: type on this side. The alias keeps the intent readable in the signatures.
type SistemaDeTokens = Any

#: The eleven colours A1, A2 and A3 already compile against.
ANCLAS_ENTREGADAS: dict[str, str] = {
    "uxnavy": "#1F4D78",
    "uxblue": "#2563EB",
    "uxsky": "#3B82F6",
    "uxpale": "#B8CCE4",
    "uxamber": "#F97316",
    "uxsurface": "#F8FAFC",
    "uxink": "#1E293B",
    "uxmuted": "#64748B",
    "uxline": "#CBD5E1",
    "uxrow": "#EEF3FA",
    "uxgreen": "#166534",
}

#: Ratios published in the planning of US-UX-09, recomputed here.
PARES_DE_REFERENCIA: list[tuple[str, str, float]] = [
    ("#1E293B", "#F8FAFC", 13.98),
    ("#FFFFFF", "#2563EB", 5.17),
    ("#FFFFFF", "#166534", 7.13),
    ("#64748B", "#F8FAFC", 4.55),
    ("#FFFFFF", "#F97316", 2.80),
    ("#FFFFFF", "#1F4D78", 8.78),
]

#: numero -> (ratio medido, veredicto, ratio sustituto, veredicto sustituto)
HALLAZGOS_ESPERADOS: dict[int, tuple[float, str, float, str]] = {
    1: (2.68, "falla", 5.22, "AA"),
    2: (3.96, "AA-grande", 7.58, "AAA"),
    3: (2.68, "falla", 4.40, "AA-grande"),
    4: (1.42, "falla", 4.55, "AA"),
}

ALIAS_DE_US001: dict[str, str] = {
    "primary": "primary-500",
    "primary-dark": "primary-700",
    "secondary": "secondary-500",
    "secondary-soft": "secondary-300",
    "accent": "accent-500",
    "accent-text": "accent-900",
    "success": "success-700",
}


def _cargar_generador() -> ModuleType:
    """Load the emitter by path: ``docs/`` is not an importable package.

    The module is registered in ``sys.modules`` before it runs because its
    frozen dataclasses resolve their postponed annotations through the module
    namespace, which does not exist yet while ``exec_module`` is running.
    """
    especificacion = importlib.util.spec_from_file_location(
        "generar_tokens_a4", RUTA_GENERADOR
    )
    assert especificacion is not None
    assert especificacion.loader is not None
    modulo = importlib.util.module_from_spec(especificacion)
    sys.modules[especificacion.name] = modulo
    especificacion.loader.exec_module(modulo)
    return modulo


GENERADOR = _cargar_generador()


@pytest.fixture(scope="module")
def sistema() -> SistemaDeTokens:
    """Design system built from the versioned stylesheet."""
    return GENERADOR.construir_sistema(GENERADOR.leer_definecolor(RUTA_FUENTE))


def test_parser_lee_los_37_colores() -> None:
    """The stylesheet declares the whole palette of the guide, with no gaps."""
    colores = GENERADOR.leer_definecolor(RUTA_FUENTE)

    assert len(colores) == 37
    for nombre, color in colores.items():
        assert PATRON_HEX.fullmatch(color.hex), f"{nombre} tiene un valor invalido"
        assert color.hex == color.hex.upper()


def test_anclas_conservan_su_valor() -> None:
    """The eleven delivered colours keep their value byte for byte.

    Changing one of them would silently repaint the PDFs of A1, A2 and A3,
    which are already submitted.
    """
    colores = GENERADOR.leer_definecolor(RUTA_FUENTE)

    for nombre, esperado in ANCLAS_ENTREGADAS.items():
        assert nombre in colores, f"uxdoc.sty perdio el ancla {nombre}"
        assert colores[nombre].hex == esperado


@pytest.mark.parametrize(("frente", "fondo", "esperado"), PARES_DE_REFERENCIA)
def test_razon_de_contraste_valores_de_referencia(
    frente: str, fondo: str, esperado: float
) -> None:
    """The WCAG 2.x formula returns the ratios published in the planning."""
    assert GENERADOR.razon_de_contraste(frente, fondo) == pytest.approx(
        esperado, abs=0.01
    )


def test_los_cuatro_hallazgos_siguen_detectados(sistema: SistemaDeTokens) -> None:
    """The four contrast defects stay detected and their substitute passes.

    If somebody "fixes" the system by moving a hex instead of moving the token,
    the ratios drift and this test says so.
    """
    hallazgos = {hallazgo.numero: hallazgo for hallazgo in sistema.hallazgos}

    assert set(hallazgos) == set(HALLAZGOS_ESPERADOS)
    for numero, (
        ratio,
        veredicto,
        ratio_ok,
        veredicto_ok,
    ) in HALLAZGOS_ESPERADOS.items():
        hallazgo = hallazgos[numero]
        assert hallazgo.par.ratio == pytest.approx(ratio, abs=0.01)
        assert hallazgo.par.veredicto == veredicto
        assert hallazgo.sustituto.ratio == pytest.approx(ratio_ok, abs=0.01)
        assert hallazgo.sustituto.veredicto == veredicto_ok
        assert hallazgo.sustituto.ratio > hallazgo.par.ratio


def test_ningun_hex_literal_en_el_generador() -> None:
    """The emitter holds no colour of its own, so uxdoc.sty stays the source."""
    codigo = RUTA_GENERADOR.read_text(encoding="utf-8")

    assert PATRON_HEX.findall(codigo) == []


def test_emision_idempotente(tmp_path: Path) -> None:
    """Two full runs write the same bytes: the tree stays clean after `make`."""
    rondas: list[dict[str, bytes]] = []
    for numero in (1, 2):
        destino = tmp_path / f"ronda{numero}"
        destino.mkdir()
        construido = GENERADOR.construir_sistema(
            GENERADOR.leer_definecolor(RUTA_FUENTE)
        )
        for nombre, emisor in (
            ("main.css", GENERADOR.emitir_theme_css),
            ("tokens.generated.ts", GENERADOR.emitir_tokens_ts),
            ("a4_tokens.tex", GENERADOR.emitir_laminas_tex),
            ("a4_tokens.json", GENERADOR.emitir_manifiesto_json),
        ):
            (destino / nombre).write_bytes(emisor(construido).encode("utf-8"))
        rondas.append(
            {archivo.name: archivo.read_bytes() for archivo in destino.iterdir()}
        )

    assert rondas[0] == rondas[1]


def test_alias_derivan_de_la_escala(sistema: SistemaDeTokens) -> None:
    """Every US-001 name keeps existing and takes its value from the scale.

    The prototype consumes these names today. An alias emitted apart from its
    step would look right on screen and lie in the PDF.
    """
    css = GENERADOR.emitir_theme_css(sistema)
    emitidos = {alias.nombre: alias for alias in sistema.alias}

    assert set(emitidos) == set(ALIAS_DE_US001)
    for nombre, origen in ALIAS_DE_US001.items():
        alias = emitidos[nombre]
        assert alias.origen == origen
        assert alias.tono is sistema.tono(origen)
        assert f"  --color-{nombre}: {alias.tono.color.hex};" in css


def test_version_en_las_tres_salidas(sistema: SistemaDeTokens) -> None:
    """The version and the date are the same in the CSS, the palette and JSON."""
    salidas = (
        GENERADOR.emitir_theme_css(sistema),
        GENERADOR.emitir_tokens_ts(sistema),
        GENERADOR.emitir_manifiesto_json(sistema),
    )

    for salida in salidas:
        assert GENERADOR.VERSION_GUIA in salida
        assert GENERADOR.FECHA_GUIA in salida
