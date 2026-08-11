"""Emit the portal's design system to everything that consumes it.

The chain runs one way and starts here:

    design/sistema.py
        -> frontend/app/assets/css/main.css        (@theme plus both modes)
        -> frontend/app/utils/tokens.generated.ts  (typed palette for /guia)

``docs/entregables/estilo/uxdoc.sty`` is not in this chain and is never read or
written: it styles the course report and is frozen.

Nothing here holds a colour literal. Every hex comes from ``design.sistema``, so
the rule that no colour is written by hand is a test and not a convention.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Final, Sequence

from design.contraste import matriz, separaciones
from design.sistema import (
    CORRIENTE,
    DENSIDAD,
    ESPACIADO_BASE_PX,
    FAMILIAS,
    FECHA,
    QUIEBRES,
    RADIOS,
    REGLAS,
    SEMANTICOS,
    SERIES,
    SOMBRAS,
    SEPARACION_SEMANTICA,
    SUPERFICIE,
    TIPOGRAFIA,
    VERSION,
    Modo,
    Token,
    tokens_de_color,
)

RAIZ: Final[Path] = Path(__file__).resolve().parents[1]
CSS: Final[Path] = RAIZ / "frontend" / "app" / "assets" / "css" / "main.css"
TS: Final[Path] = RAIZ / "frontend" / "app" / "utils" / "tokens.generated.ts"

#: US-001 wrote these names and nine screens plus seven plates consume them
#: today. They are kept as names and mapped onto the new system, never given a
#: value of their own: emitting the redesign without them would break every
#: screen at once and turn a visual change into an outage.
ALIAS: Final[tuple[tuple[str, str], ...]] = (
    ("surface", "ground"),
    ("surface-alt", "ground-alt"),
    ("line", "grid"),
    ("line-strong", "corriente-medio"),
    ("muted", "corriente-tenue"),
    ("ink", "corriente-pleno"),
    ("ink-strong", "corriente-pleno"),
    ("primary", "info"),
    ("primary-100", "ground-alt"),
    ("primary-300", "corriente-apagado"),
    ("primary-500", "info"),
    ("primary-700", "corriente-medio"),
    ("primary-900", "corriente-pleno"),
    ("primary-dark", "corriente-medio"),
    ("secondary", "info"),
    ("secondary-100", "ground-alt"),
    ("secondary-300", "corriente-apagado"),
    ("secondary-500", "info"),
    ("secondary-700", "corriente-medio"),
    ("secondary-900", "corriente-pleno"),
    ("secondary-soft", "corriente-apagado"),
    ("accent", "aviso"),
    ("accent-100", "ground-alt"),
    ("accent-300", "corriente-apagado"),
    ("accent-500", "aviso"),
    ("accent-700", "aviso"),
    ("accent-900", "aviso"),
    ("accent-text", "aviso"),
    ("success", "ok"),
    ("success-100", "ground-alt"),
    ("success-300", "corriente-apagado"),
    ("success-500", "ok"),
    ("success-700", "ok"),
    ("success-900", "ok"),
    ("danger", "error"),
    ("danger-strong", "error"),
    ("warning", "aviso"),
    ("info", "info"),
)


def _cabecera(marca_comentario: str) -> list[str]:
    """Return the do-not-edit banner every output carries."""
    abre, cierra = ("/*", "*/") if marca_comentario == "css" else ("/**", " */")
    return [
        f"{abre}",
        f" * Karisma Data - sistema de diseno del portal {VERSION} - {FECHA}",
        " *",
        " * GENERADO. No editar a mano: la siguiente corrida lo sobrescribe.",
        " *",
        " * Fuente:    design/sistema.py",
        " * Emisor:    design/emitir.py",
        " * Regenerar: make tokens",
        " *",
        " * El estilo del INFORME vive en docs/entregables/estilo/uxdoc.sty y es otro",
        " * sistema: esta cadena no lo lee ni lo escribe.",
        f"{cierra}",
    ]


def _bloque_color(modo: Modo, sangria: str) -> list[str]:
    """Return every colour custom property for ``modo``."""
    lineas: list[str] = []
    grupos: tuple[tuple[str, tuple[Token, ...]], ...] = (
        ("Suelo y reticula", SUPERFICIE),
        ("Corriente - el estado se lee por luminancia", CORRIENTE),
        ("Semanticos - color mas forma mas icono, nunca color solo", SEMANTICOS),
        ("Series categoricas - cada una con su marcador y su patron", SERIES),
    )
    for titulo, grupo in grupos:
        lineas.append(f"{sangria}/* {titulo} */")
        for token in grupo:
            nota = "" if token.informa else "  /* no informa */"
            lineas.append(
                f"{sangria}--color-{token.nombre}: {token.valor(modo)};{nota}"
            )
        lineas.append("")
    lineas.append(
        f"{sangria}/* Alias de US-001: nombres viejos, valores del sistema nuevo */"
    )
    for viejo, nuevo in ALIAS:
        lineas.append(f"{sangria}--color-{viejo}: var(--color-{nuevo});")
    return lineas


def emitir_css() -> str:
    """Return the full stylesheet: the theme plus both mode overrides."""
    out = _cabecera("css")
    out += ['@import "tailwindcss";', "", "@theme {"]
    out += _bloque_color("claro", "  ")
    out.append("")
    out.append("  /* Tipografia - el peso es un canal de jerarquia, no decoracion */")
    for familia, pila in FAMILIAS.items():
        out.append(f"  --font-{familia}: {pila};")
    out.append("")
    for rol in TIPOGRAFIA:
        out.append(f"  /* {rol.uso} */")
        out.append(f"  --text-{rol.nombre}: {rol.tamano_px}px;")
        out.append(f"  --text-{rol.nombre}--line-height: {rol.interlinea_px}px;")
        out.append(f"  --text-{rol.nombre}--font-weight: {rol.peso};")
        if rol.espaciado != "0":
            out.append(f"  --text-{rol.nombre}--letter-spacing: {rol.espaciado};")
    out.append("")
    out.append(f"  --spacing: {ESPACIADO_BASE_PX}px;")
    out.append("")
    for nombre, px, uso in RADIOS:
        out.append(f"  --radius-{nombre}: {px}px;  /* {uso} */")
    out.append("")
    for nombre, claro, _oscuro, uso in SOMBRAS:
        out.append(f"  --shadow-{nombre}: {claro};  /* {uso} */")
    out.append("")
    for nombre, px, uso in QUIEBRES:
        out.append(f"  --breakpoint-{nombre}: {px}px;  /* {uso} */")
    out.append("")
    for nombre, px, uso in DENSIDAD:
        unidad = "" if nombre == "medida-maxima" else "px"
        out.append(f"  --{nombre}: {px}{unidad};  /* {uso} */")
    out.append("}")
    out.append("")

    oscuro = _bloque_color("oscuro", "    ")
    sombras_oscuras = [f"    --shadow-{n}: {o};" for n, _c, o, _u in SOMBRAS]

    out.append(
        "/* Modo oscuro. Por omision manda el sistema operativo; el lector puede"
    )
    out.append(
        "   forzarlo con data-theme, y por eso la consulta se excluye a si misma"
    )
    out.append("   cuando ya hay una eleccion explicita de modo claro. */")
    out.append("@media (prefers-color-scheme: dark) {")
    out.append('  :root:not([data-theme="claro"]) {')
    out += oscuro
    out += sombras_oscuras
    out.append("  }")
    out.append("}")
    out.append("")
    out.append(':root[data-theme="oscuro"] {')
    out += oscuro
    out += sombras_oscuras
    out.append("}")
    out.append("")
    out.append("/* Reglas que el sistema declara y que la interfaz debe cumplir:")
    for regla in REGLAS:
        out.append(f"   - {regla}")
    out.append("*/")
    return "\n".join(out) + "\n"


def _ts_token(token: Token, sangria: str) -> list[str]:
    """Return one typed token literal."""
    return [
        f"{sangria}{{",
        f"{sangria}  nombre: '{token.nombre}',",
        f"{sangria}  claro: '{token.valor('claro')}',",
        f"{sangria}  oscuro: '{token.valor('oscuro')}',",
        f"{sangria}  clase: 'bg-{token.nombre}',",
        f"{sangria}  informa: {'true' if token.informa else 'false'},",
        f"{sangria}  uso: {_cadena(token.uso)},",
        f"{sangria}}},",
    ]


def _cadena(texto: str) -> str:
    """Return ``texto`` as a single-quoted TypeScript literal."""
    return "'" + texto.replace("\\", "\\\\").replace("'", "\\'") + "'"


def emitir_ts() -> str:
    """Return the typed palette the guide reads instead of typing hex values."""
    out = _cabecera("ts")
    out += [
        "",
        "export interface TokenColor {",
        "  readonly nombre: string",
        "  readonly claro: string",
        "  readonly oscuro: string",
        "  readonly clase: string",
        "  readonly informa: boolean",
        "  readonly uso: string",
        "}",
        "",
        "export interface RolTipografico {",
        "  readonly nombre: string",
        "  readonly tamanoPx: number",
        "  readonly interlineaPx: number",
        "  readonly peso: number",
        "  readonly familia: string",
        "  readonly uso: string",
        "}",
        "",
        f"export const VERSION_SISTEMA = '{VERSION}'",
        f"export const FECHA_SISTEMA = '{FECHA}'",
        "",
    ]
    for nombre, grupo in (
        ("SUPERFICIE", SUPERFICIE),
        ("CORRIENTE", CORRIENTE),
        ("SEMANTICOS", SEMANTICOS),
        ("SERIES", SERIES),
    ):
        out.append(f"export const {nombre}: readonly TokenColor[] = [")
        for token in grupo:
            out += _ts_token(token, "  ")
        out.append("]")
        out.append("")
    out.append("export const TIPOGRAFIA: readonly RolTipografico[] = [")
    for rol in TIPOGRAFIA:
        out += [
            "  {",
            f"    nombre: '{rol.nombre}',",
            f"    tamanoPx: {rol.tamano_px},",
            f"    interlineaPx: {rol.interlinea_px},",
            f"    peso: {rol.peso},",
            f"    familia: '{rol.familia}',",
            f"    uso: {_cadena(rol.uso)},",
            "  },",
        ]
    out.append("]")
    out.append("")
    out.append("export const REGLAS: readonly string[] = [")
    for regla in REGLAS:
        out.append(f"  {_cadena(regla)},")
    out.append("]")
    out.append("")
    out += [
        "export interface ParContraste {",
        "  readonly token: string",
        "  readonly modo: 'claro' | 'oscuro'",
        "  readonly ratio: number",
        "  readonly veredicto: string",
        "}",
        "",
        "export interface SeparacionSemantica {",
        "  readonly uno: string",
        "  readonly otro: string",
        "  readonly modo: 'claro' | 'oscuro'",
        "  readonly dicromacia: string",
        "  readonly distancia: number",
        "}",
        "",
        "export const CONTRASTES: readonly ParContraste[] = [",
    ]
    for modo in ("claro", "oscuro"):
        for par in matriz(modo):
            out.append(
                f"  {{ token: '{par.frente}', modo: '{modo}', "
                f"ratio: {par.ratio}, veredicto: '{par.veredicto}' }},"
            )
    out.append("]")
    out.append("")
    out.append("export const SEPARACIONES: readonly SeparacionSemantica[] = [")
    for modo in ("claro", "oscuro"):
        for s in separaciones(modo):
            out.append(
                f"  {{ uno: '{s.uno}', otro: '{s.otro}', modo: '{modo}', "
                f"dicromacia: '{s.dicromacia}', distancia: {s.distancia} }},"
            )
    out.append("]")
    out.append("")
    out.append(
        "/** Peor separacion semantica medida por modo. En claro es un techo. */"
    )
    out.append("export const PEOR_SEPARACION = {")
    for modo, valor in SEPARACION_SEMANTICA.items():
        out.append(f"  {modo}: {valor},")
    out.append("} as const")
    out.append("")
    out.append("export const TOKENS: readonly TokenColor[] = [")
    out.append("  ...SUPERFICIE,")
    out.append("  ...CORRIENTE,")
    out.append("  ...SEMANTICOS,")
    out.append("  ...SERIES,")
    out.append("]")
    return "\n".join(out) + "\n"


def _salidas() -> tuple[tuple[Path, str], ...]:
    """Return every file this module owns, with the content it should hold."""
    return ((CSS, emitir_css()), (TS, emitir_ts()))


def main(argv: Sequence[str] | None = None) -> int:
    """Write every output, or check them when ``--verificar`` is passed."""
    parser = argparse.ArgumentParser(
        description="Emite el sistema de diseno del portal."
    )
    parser.add_argument(
        "--verificar",
        action="store_true",
        help="No escribe: devuelve 1 si alguna salida difiere de lo que hay en disco.",
    )
    args = parser.parse_args(argv)

    difiere = False
    for ruta, contenido in _salidas():
        if args.verificar:
            actual = ruta.read_text(encoding="utf-8") if ruta.exists() else ""
            if actual != contenido:
                print(f"difiere: {ruta.relative_to(RAIZ)}", file=sys.stderr)
                difiere = True
        else:
            ruta.parent.mkdir(parents=True, exist_ok=True)
            ruta.write_text(contenido, encoding="utf-8")
            print(f"escrito: {ruta.relative_to(RAIZ)}")

    if args.verificar and not difiere:
        print(f"tokens verificados: {len(tokens_de_color())} colores, 2 modos")
    return 1 if difiere else 0


if __name__ == "__main__":
    raise SystemExit(main())
