"""Emit the portal's design system to everything that consumes it.

The chain runs one way and starts here:

    design/sistema.py
        -> frontend/app/assets/css/main.css        (@theme plus modes and themes)
        -> frontend/app/utils/tokens.generated.ts  (typed palettes for /guia)

``docs/entregables/estilo/uxdoc.sty`` is not in this chain and is never read or
written: it styles the course report and is frozen. Its own emitter,
``docs/entregables/generar_tokens_a4.py``, owns everything under
``docs/entregables/`` and nothing else. One file, one emitter, both ways round.

Nothing here holds a colour literal. Every hex comes from ``design.sistema``, so
the rule that no colour is written by hand is a test and not a convention.

**Two axes, two attributes, and the order between them is load bearing.** The
mode travels in ``data-modo`` and the theme in ``data-tema``. Until this
version the mode travelled in ``data-theme``, a name that says theme and
carries mode: introducing a real theme while that name stayed occupied would
have guaranteed the confusion, so the attribute was renamed. The blocks are
emitted mode first, theme second and the theme-and-mode pair last, because a
rule with two attributes wins on specificity and has to be able to win.
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Final

from design.contraste import matriz, peor_separacion, separaciones
from design.sistema import (
    ACCION,
    BARRA_LATERAL,
    CERTIFICACION,
    CORRIENTE,
    DENSIDAD,
    ESPACIADO_BASE_PX,
    FAMILIAS_POR_TEMA,
    FECHA,
    PREFIJO_CERTIFICACION,
    QUIEBRES,
    RADIOS,
    REGLAS,
    SEMANTICOS,
    SERIES,
    SOMBRAS,
    SUPERFICIE,
    TEMA_OMISION,
    TEMAS,
    TIPOGRAFIA,
    VERSION,
    Modo,
    Tema,
    Token,
    tokens_de_color,
)

#: Both modes ship, and every measurement is computed once per mode.
MODOS: Final[tuple[Modo, ...]] = ("claro", "oscuro")

#: Every colour group, with the name the typed module exports and the heading
#: the stylesheet prints, in the order ``tokens_de_color`` walks them.
#:
#: One list feeds both outputs. Two lists would drift the day a group is added,
#: and the drift would be silent in the worst possible way: the sheet would
#: declare a custom property the typed module never mentions, or the guide
#: would print a swatch for a colour no rule paints.
GRUPOS: Final[tuple[tuple[str, str, tuple[Token, ...]], ...]] = (
    ("SUPERFICIE", "Suelo y reticula", SUPERFICIE),
    ("CORRIENTE", "Corriente - el estado se lee por luminancia", CORRIENTE),
    ("ACCION", "Accion y seleccion - el color con el que el tema actua", ACCION),
    (
        "BARRA_LATERAL",
        "Chasis - un solo armazon, y el tema le cambia el suelo",
        BARRA_LATERAL,
    ),
    (
        "SEMANTICOS",
        "Semanticos - color mas forma mas icono, nunca color solo",
        SEMANTICOS,
    ),
    (
        "CERTIFICACION",
        "Certificacion - tres estados, tres canales, tres iconos",
        CERTIFICACION,
    ),
    ("SERIES", "Series categoricas - cada una con su marcador y su patron", SERIES),
)

RAIZ: Final[Path] = Path(__file__).resolve().parents[1]
CSS: Final[Path] = RAIZ / "frontend" / "app" / "assets" / "css" / "main.css"
TS: Final[Path] = RAIZ / "frontend" / "app" / "utils" / "tokens.generated.ts"


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


def _nota(token: Token) -> str:
    """Return the trailing comment one declaration carries, empty when none.

    The icon is published beside the colour instead of being chosen again by
    whoever paints it. That is not documentation: the catalogue picked its icon
    with a ternary on the state code, and two states that mean opposite things
    ended up with the same triangle and the same amber.

    Args:
        token: Token being declared.

    Returns:
        A CSS comment, already spaced, or an empty string.
    """
    notas: list[str] = []
    if not token.informa:
        notas.append("no informa")
    if token.icono != "":
        notas.append(f"icono {token.icono}")
    return f"  /* {', '.join(notas)} */" if notas else ""


def _bloque_color(tema: Tema, modo: Modo, sangria: str) -> list[str]:
    """Return every colour custom property for ``tema`` in ``modo``."""
    lineas: list[str] = []
    for _, titulo, grupo in GRUPOS:
        lineas.append(f"{sangria}/* {titulo} */")
        for token in grupo:
            lineas.append(
                f"{sangria}--color-{token.nombre}: {token.valor(tema, modo)};"
                f"{_nota(token)}"
            )
        lineas.append("")
    return lineas


def _bloque_familias(tema: Tema, sangria: str) -> list[str]:
    """Return the type families ``tema`` changes with respect to the default.

    A theme that shipped the same stack as the default one would emit nothing,
    which is the honest outcome: the axis is colour *and* family, and only the
    roles that actually move are overridden.

    Args:
        tema: Theme being emitted.
        sangria: Indentation of the enclosing block.

    Returns:
        One declaration per family that differs, empty when none does.
    """
    omision = FAMILIAS_POR_TEMA[TEMA_OMISION]
    lineas: list[str] = []
    for familia, pila in FAMILIAS_POR_TEMA[tema].items():
        if pila != omision[familia]:
            lineas.append(f"{sangria}--font-{familia}: {pila};")
    if lineas:
        lineas.insert(0, f"{sangria}/* Tipografia del tema */")
        lineas.append("")
    return lineas


def emitir_css() -> str:
    """Return the full stylesheet: the theme block plus modes and themes."""
    out = _cabecera("css")
    out += ['@import "tailwindcss";', "", "@theme {"]
    out += _bloque_color(TEMA_OMISION, "claro", "  ")
    out.append("")
    out.append("  /* Tipografia - el peso es un canal de jerarquia, no decoracion */")
    for familia, pila in FAMILIAS_POR_TEMA[TEMA_OMISION].items():
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
        unidad = "ch" if nombre == "medida-maxima" else "px"
        out.append(f"  --{nombre}: {px}{unidad};  /* {uso} */")
    out.append("}")
    out.append("")

    sombras_oscuras = [f"    --shadow-{n}: {o};" for n, _c, o, _u in SOMBRAS]
    opcionales = tuple(t for t in TEMAS if t != TEMA_OMISION)

    out.append("/*")
    out.append(" * Los dos ejes de la superficie, y por que se llaman asi.")
    out.append(" *")
    out.append(" * El MODO viaja en data-modo y el TEMA en data-tema. Por omision el")
    out.append(" * modo lo decide el sistema operativo; el lector puede forzarlo, y")
    out.append(" * por eso la consulta se excluye a si misma cuando ya hay una")
    out.append(" * eleccion explicita de modo claro.")
    out.append(" *")
    out.append(" * El orden importa: los bloques de tema van DESPUES de los de modo,")
    out.append(" * y el par tema mas modo va el ultimo, porque una regla con dos")
    out.append(" * atributos gana por especificidad y debe poder ganar.")
    out.append(" */")
    out.append("@media (prefers-color-scheme: dark) {")
    out.append('  :root:not([data-modo="claro"]) {')
    out += _bloque_color(TEMA_OMISION, "oscuro", "    ")
    out += sombras_oscuras
    out.append("  }")
    for tema in opcionales:
        out.append("")
        out.append(f'  :root[data-tema="{tema}"]:not([data-modo="claro"]) {{')
        out += _bloque_color(tema, "oscuro", "    ")
        out += _bloque_familias(tema, "    ")
        out += sombras_oscuras
        out.append("  }")
    out.append("}")
    out.append("")
    out.append(':root[data-modo="oscuro"] {')
    out += _bloque_color(TEMA_OMISION, "oscuro", "    ")
    out += sombras_oscuras
    out.append("}")
    for tema in opcionales:
        out.append("")
        out.append(f':root[data-tema="{tema}"] {{')
        out += _bloque_color(tema, "claro", "    ")
        out += _bloque_familias(tema, "    ")
        out.append("}")
        out.append("")
        out.append(f':root[data-tema="{tema}"][data-modo="oscuro"] {{')
        out += _bloque_color(tema, "oscuro", "    ")
        out += _bloque_familias(tema, "    ")
        out += sombras_oscuras
        out.append("}")
    out.append("")
    out.append("/*")
    out.append(" * Desplazamiento al saltar a un ancla.")
    out.append(" *")
    out.append(" * La navegacion de laminas es pegajosa, asi que sin este margen el")
    out.append(" * encabezado de destino quedaria justo debajo de ella y el lector")
    out.append(" * aterrizaria en el parrafo, no en el titulo.")
    out.append(" */")
    out.append("[id^='lamina-'] {")
    out.append("  scroll-margin-top: calc(var(--header-height) + var(--spacing) * 12);")
    out.append("}")
    out.append("")
    out.append("@media (prefers-reduced-motion: no-preference) {")
    out.append("  html {")
    out.append("    scroll-behavior: smooth;")
    out.append("  }")
    out.append("}")
    out.append("")
    out.append("/*")
    out.append(" * Medida de linea.")
    out.append(" *")
    out.append(" * El token --medida-maxima existia y 15 de 26 parrafos largos lo")
    out.append(
        " * excedian, el peor a 205 caracteres: declarado y no aplicado, que es el"
    )
    out.append(
        " * mismo defecto que el punto de quiebre que nunca colapso. La regla vive"
    )
    out.append(" * en el sistema para que el siguiente parrafo no vuelva a escaparse.")
    out.append(" *")
    out.append(
        " * Se excluye lo que no es prosa: una celda de tabla, una etiqueta y un"
    )
    out.append(" * bloque de codigo se leen de un vistazo y limitarlos los romperia.")
    out.append(" */")
    out.append("p:not([class*='max-w']):not(td p):not(th p),")
    out.append("li:not([class*='max-w']):not(nav li):not(ul[class*='grid'] li) {")
    out.append("  max-width: var(--medida-maxima);")
    out.append("}")
    out.append("")
    out.append("/*")
    out.append(" * Objetivo tactil minimo en dispositivos de puntero grueso.")
    out.append(" *")
    out.append(
        " * Medido a 375 px sobre /guia: 58 controles por debajo de 44 px, todos"
    )
    out.append(" * por ALTURA y ninguno por ancho. Arreglarlo control a control habria")
    out.append(" * dejado el siguiente fuera, asi que la regla vive en el sistema.")
    out.append(" *")
    out.append(
        " * La condicion es pointer: coarse y no un punto de quiebre de ancho: la"
    )
    out.append(
        " * regla trata de dedos, no de pantallas estrechas, y un raton a 375 px"
    )
    op = " * no necesita 44 px de alto."
    out.append(op)
    out.append(" */")
    out.append("@media (pointer: coarse) {")
    out.append("  button,")
    out.append("  summary,")
    out.append("  input,")
    out.append("  select,")
    out.append("  textarea,")
    out.append('  [role="button"],')
    out.append("  a:not(.prosa a) {")
    out.append("    min-height: 44px;")
    out.append("  }")
    out.append("")
    out.append("  /* Un enlace dentro de un parrafo sigue el flujo del texto. */")
    out.append("  p a,")
    out.append("  .sr-only {")
    out.append("    min-height: revert;")
    out.append("  }")
    out.append("}")
    out.append("")
    out.append("/* Reglas que el sistema declara y que la interfaz debe cumplir:")
    for regla in REGLAS:
        out.append(f"   - {regla}")
    out.append("*/")
    return "\n".join(out) + "\n"


def _ts_token(token: Token, sangria: str) -> list[str]:
    """Return one typed token literal."""
    lineas = [
        f"{sangria}{{",
        f"{sangria}  nombre: '{token.nombre}',",
        f"{sangria}  claro: '{token.valor(TEMA_OMISION, 'claro')}',",
        f"{sangria}  oscuro: '{token.valor(TEMA_OMISION, 'oscuro')}',",
        f"{sangria}  clase: 'bg-{token.nombre}',",
        f"{sangria}  informa: {'true' if token.informa else 'false'},",
        f"{sangria}  uso: {_cadena(token.uso)},",
    ]
    if token.icono != "":
        lineas.append(f"{sangria}  icono: '{token.icono}',")
    lineas.append(f"{sangria}  temas: {{")
    for tema in TEMAS:
        paleta = token.paleta(tema)
        lineas.append(
            f"{sangria}    {tema}: {{ claro: '{paleta.claro}', "
            f"oscuro: '{paleta.oscuro}' }},"
        )
    lineas.append(f"{sangria}  }},")
    lineas.append(f"{sangria}}},")
    return lineas


def _cadena(texto: str) -> str:
    """Return ``texto`` as a single-quoted TypeScript literal."""
    return "'" + texto.replace("\\", "\\\\").replace("'", "\\'") + "'"


def emitir_ts() -> str:
    """Return the typed palettes the guide reads instead of typing hex values."""
    out = _cabecera("ts")
    out += [
        "",
        "export type TemaSistema = " + " | ".join(f"'{tema}'" for tema in TEMAS),
        "",
        "export type ModoSistema = 'claro' | 'oscuro'",
        "",
        "export interface PaletaTema {",
        "  readonly claro: string",
        "  readonly oscuro: string",
        "}",
        "",
        "export interface TokenColor {",
        "  readonly nombre: string",
        "  /** Valor del TEMA DE OMISION, que es el que sostiene las capturas. */",
        "  readonly claro: string",
        "  readonly oscuro: string",
        "  readonly clase: string",
        "  readonly informa: boolean",
        "  readonly uso: string",
        "  /** Icono que viaja con el color cuando el token es un estado. */",
        "  readonly icono?: string",
        "  /** El mismo token en cada tema, para la lamina comparativa. */",
        "  readonly temas: Readonly<Record<TemaSistema, PaletaTema>>",
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
        "export const TEMAS: readonly TemaSistema[] = ["
        + ", ".join(f"'{tema}'" for tema in TEMAS)
        + "]",
        f"export const TEMA_OMISION: TemaSistema = '{TEMA_OMISION}'",
        "",
        "/**",
        " * La familia tipografica es parte del eje del tema, no un interruptor",
        " * aparte: el tema de omision conserva Lexend Deca y Fira Sans y el",
        " * institucional usa Inter, que es lo que declara el archivo de diseno.",
        " */",
        "export const FAMILIAS_POR_TEMA: Readonly<",
        "  Record<TemaSistema, Readonly<Record<string, string>>>",
        "> = {",
    ]
    for tema in TEMAS:
        out.append(f"  {tema}: {{")
        for familia, pila in FAMILIAS_POR_TEMA[tema].items():
            out.append(f"    {familia}: {_cadena(pila)},")
        out.append("  },")
    out.append("}")
    out.append("")
    for nombre, _, grupo in GRUPOS:
        out.append(f"export const {nombre}: readonly TokenColor[] = [")
        for token in grupo:
            out += _ts_token(token, "  ")
        out.append("]")
        out.append("")
    out += [
        "export interface EstadoCertificacion {",
        "  /** Codigo que guarda el catalogo, sin el prefijo del token. */",
        "  readonly codigo: string",
        "  readonly token: string",
        "  readonly icono: string",
        "  readonly clase: string",
        "}",
        "",
        "/**",
        " * Los tres estados de certificacion, resueltos aqui y en ningun otro",
        " * sitio.",
        " *",
        " * El catalogo elegia el icono con una ternaria sobre el codigo, asi que",
        " * `en revision` y `obsoleto` compartian color Y forma y significan lo",
        " * contrario. Quien pinte un estado lee de aqui: con la tabla completa la",
        " * ternaria no tiene donde volver.",
        " */",
        "export const ESTADOS_CERTIFICACION: readonly EstadoCertificacion[] = [",
    ]
    for token in CERTIFICACION:
        codigo = token.nombre.removeprefix(PREFIJO_CERTIFICACION)
        out.append(
            f"  {{ codigo: '{codigo}', token: '{token.nombre}', "
            f"icono: '{token.icono}', clase: 'text-{token.nombre}' }},"
        )
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
        "  /** Token sobre el que se midio: casi siempre el suelo de la pagina. */",
        "  readonly fondo: string",
        "  readonly tema: TemaSistema",
        "  readonly modo: ModoSistema",
        "  readonly ratio: number",
        "  readonly veredicto: string",
        "}",
        "",
        "export interface SeparacionSemantica {",
        "  readonly uno: string",
        "  readonly otro: string",
        "  /** Familia dentro de la que la distancia es exigible. */",
        "  readonly familia: string",
        "  readonly tema: TemaSistema",
        "  readonly modo: ModoSistema",
        "  readonly dicromacia: string",
        "  readonly distancia: number",
        "}",
        "",
        "/**",
        " * La matriz completa: cada token sobre el suelo de SU tema y su modo.",
        " *",
        " * El suelo no es el mismo en los dos temas, ni siquiera dentro del",
        " * mismo modo, asi que una razon medida en uno no dice nada del otro.",
        " */",
        "export const CONTRASTES_POR_TEMA: readonly ParContraste[] = [",
    ]
    for tema in TEMAS:
        for modo in MODOS:
            for par in matriz(tema, modo):
                out.append(
                    f"  {{ token: '{par.frente}', fondo: '{par.fondo}', "
                    f"tema: '{tema}', modo: '{modo}', "
                    f"ratio: {par.ratio}, veredicto: '{par.veredicto}' }},"
                )
    out.append("]")
    out.append("")
    out.append("/** La matriz del tema de omision, que es la que publica el PDF. */")
    out.append(
        "export const CONTRASTES: readonly ParContraste[] = CONTRASTES_POR_TEMA.filter("
    )
    out.append(f"  (par) => par.tema === '{TEMA_OMISION}',")
    out.append(")")
    out.append("")
    for constante, familia, encabezado in (
        (
            "SEPARACIONES_POR_TEMA",
            "semantico",
            "/** Las seis parejas de las cuatro marcas semanticas. */",
        ),
        (
            "SEPARACIONES_CERTIFICACION_POR_TEMA",
            "certificacion",
            "/**\n"
            " * Las tres parejas de los tres estados de certificacion.\n"
            " *\n"
            " * Van en su propia constante y no mezcladas con las semanticas:\n"
            " * una distancia solo es exigible entre marcas que pueden compartir\n"
            " * superficie, y el piso que publica el informe es el de la familia\n"
            " * semantica. Los estados toman prestado su canal entero, asi que\n"
            " * estas tres distancias son un subconjunto de aquellas seis.\n"
            " */",
        ),
    ):
        out.append(encabezado)
        out.append(f"export const {constante}: readonly SeparacionSemantica[] = [")
        for tema in TEMAS:
            for modo in MODOS:
                for s in separaciones(tema, modo):
                    if s.familia != familia:
                        continue
                    out.append(
                        f"  {{ uno: '{s.uno}', otro: '{s.otro}', "
                        f"familia: '{s.familia}', tema: '{tema}', "
                        f"modo: '{modo}', dicromacia: '{s.dicromacia}', "
                        f"distancia: {s.distancia} }},"
                    )
        out.append("]")
        out.append("")
    out.append(
        "export const SEPARACIONES: readonly SeparacionSemantica[] = "
        "SEPARACIONES_POR_TEMA.filter("
    )
    out.append(f"  (s) => s.tema === '{TEMA_OMISION}',")
    out.append(")")
    out.append("")
    out.append("/**")
    out.append(" * Peor separacion semantica por tema y modo, DERIVADA del calculo.")
    out.append(" *")
    out.append(" * Estuvo escrita a mano y se desincronizo del computo: declaraba 13.4")
    out.append(
        " * donde la medicion daba 13.6, que es el mismo defecto que este sistema"
    )
    out.append(
        " * existe para impedir. Una prueba lo detecto y ahora no puede repetirse."
    )
    out.append(" */")
    out.append("export const PEOR_SEPARACION_POR_TEMA = {")
    for tema in TEMAS:
        out.append(f"  {tema}: {{")
        for modo in MODOS:
            out.append(f"    {modo}: {peor_separacion(tema, modo)},")
        out.append("  },")
    out.append("} as const")
    out.append("")
    out.append("/** La del tema de omision, que es la que el informe reproduce. */")
    out.append(
        f"export const PEOR_SEPARACION = PEOR_SEPARACION_POR_TEMA.{TEMA_OMISION}"
    )
    out.append("")
    out.append("/**")
    out.append(" * Peor pareja de los tres estados de certificacion, por combinacion.")
    out.append(" *")
    out.append(" * Es la cifra que responde a la pregunta que abrio esta ranura: si")
    out.append(" * `en revision` y `obsoleto` volvieran a compartir canal, esto seria")
    out.append(" * cero y la interfaz seguiria pintando sin quejarse.")
    out.append(" */")
    out.append("export const PEOR_SEPARACION_CERTIFICACION = {")
    for tema in TEMAS:
        out.append(f"  {tema}: {{")
        for modo in MODOS:
            out.append(f"    {modo}: {peor_separacion(tema, modo, 'certificacion')},")
        out.append("  },")
    out.append("} as const")
    out.append("")
    out.append("export const TOKENS: readonly TokenColor[] = [")
    for nombre, _, _grupo in GRUPOS:
        out.append(f"  ...{nombre},")
    out.append("]")
    return "\n".join(out) + "\n"


def _salidas() -> tuple[tuple[Path, str], ...]:
    """Return every file this module owns, with the content it should hold."""
    return ((CSS, emitir_css()), (TS, emitir_ts()))


def _bajo(ruta: Path, destino: Path | None) -> Path:
    """Return where ``ruta`` is read or written on this run.

    Args:
        ruta: Canonical output path, always inside the repository.
        destino: Root that replaces the repository, or ``None`` to work in
            place. The relative path is kept, so a mirrored tree can be
            compared directory against directory.

    Returns:
        The path this run works on.
    """
    if destino is None:
        return ruta
    return destino / ruta.relative_to(RAIZ)


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
    parser.add_argument(
        "--destino",
        type=Path,
        default=None,
        metavar="DIR",
        help=(
            "Escribe -o compara- bajo DIR conservando la ruta relativa, en vez "
            "de sobre el arbol de trabajo."
        ),
    )
    args = parser.parse_args(argv)

    difiere = False
    for ruta, contenido in _salidas():
        destino = _bajo(ruta, args.destino)
        if args.verificar:
            actual = destino.read_text(encoding="utf-8") if destino.exists() else ""
            if actual != contenido:
                print(f"difiere: {ruta.relative_to(RAIZ)}", file=sys.stderr)
                difiere = True
        else:
            destino.parent.mkdir(parents=True, exist_ok=True)
            destino.write_text(contenido, encoding="utf-8")
            print(f"escrito: {ruta.relative_to(RAIZ)}")

    if args.verificar and not difiere:
        print(
            f"tokens verificados: {len(tokens_de_color())} colores, "
            f"{len(TEMAS)} temas, {len(MODOS)} modos"
        )
    return 1 if difiere else 0


if __name__ == "__main__":
    raise SystemExit(main())
