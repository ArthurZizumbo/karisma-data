"""What the emitted stylesheet paints, resolved the way a browser resolves it.

``tests/ml/test_contraste_temas.py`` already holds every value of the two themes
to its contrast floor, but it reads them from ``design.sistema`` and never looks
at what ``design.emitir`` writes. Between the two there is a whole cascade, and
the cascade is where the theme axis can fail silently: four combinations of
theme and mode are painted by five blocks that overlap, and if the pair block is
missing or loses on specificity, one combination quietly inherits another one's
colours. Nothing in the suite would notice, because every value would still be a
value the system declares.

So this file does not compare strings of CSS. It parses the emitted sheet,
resolves each custom property under a given set of root attributes and a given
``prefers-color-scheme``, applying specificity and then document order, and
compares the winner against ``design.sistema``. The cascade model is deliberately
minimal -it only understands the selector shapes the emitter writes- and a guard
test fails the moment a shape it cannot score appears, so it can never score a
sheet it does not understand.
"""

from __future__ import annotations

import re
from typing import Final, NamedTuple

import pytest
from design.emitir import RAIZ, emitir_css, emitir_ts
from design.sistema import (
    CERTIFICACION,
    FAMILIAS_POR_TEMA,
    PREFIJO_CERTIFICACION,
    TEMA_OMISION,
    TEMAS,
    TIPOGRAFIA,
    Modo,
    Tema,
    tokens_de_color,
)

#: The two families of custom property the theme axis moves. Everything else the
#: sheet declares -scale, rhythm, radius, breakpoints- is the same in the four
#: combinations and is not part of this contract.
PREFIJOS: Final[tuple[str, ...]] = ("--color-", "--font-")

#: Every selector shape the emitter writes, and the only ones this model scores.
SELECTOR_CONOCIDO: Final[re.Pattern[str]] = re.compile(
    r'^(@theme|:root(\[[\w-]+="[\w-]+"\])*(:not\(\[[\w-]+="[\w-]+"\]\))?)$'
)

#: The media query the sheet uses to follow the operating system.
CONSULTA_OSCURA: Final[str] = "prefers-color-scheme: dark"


class Bloque(NamedTuple):
    """One rule of the emitted sheet, in document order.

    Attributes:
        medio: Enclosing at-rule, empty at the top level.
        selector: Prelude of the rule, as the emitter wrote it.
        declaraciones: Property to value, comments already removed.
    """

    medio: str
    selector: str
    declaraciones: dict[str, str]


def _declaraciones(cuerpo: str) -> dict[str, str]:
    """Return the declarations of a rule body that holds no nested rule."""
    salida: dict[str, str] = {}
    for trozo in cuerpo.split(";"):
        nombre, separador, valor = trozo.partition(":")
        if separador == "":
            continue
        salida[nombre.strip()] = valor.strip()
    return salida


def _bloques(css: str, medio: str = "") -> list[Bloque]:
    """Return every rule of ``css`` in document order, at-rules flattened.

    Args:
        css: Stylesheet with its comments already stripped.
        medio: At-rule the fragment is nested in.

    Returns:
        The rules, in the order the cascade walks them.
    """
    salida: list[Bloque] = []
    inicio = 0
    indice = 0
    while indice < len(css):
        if css[indice] != "{":
            indice += 1
            continue
        prelude = css[inicio:indice].rpartition(";")[2].rpartition("}")[2].strip()
        profundidad = 1
        fin = indice + 1
        while fin < len(css) and profundidad > 0:
            if css[fin] == "{":
                profundidad += 1
            elif css[fin] == "}":
                profundidad -= 1
            fin += 1
        cuerpo = css[indice + 1 : fin - 1]
        if prelude.startswith("@media"):
            salida.extend(_bloques(cuerpo, prelude))
        else:
            salida.append(Bloque(medio, prelude, _declaraciones(cuerpo)))
        indice = fin
        inicio = fin
    return salida


#: The emitted sheet, parsed once.
BLOQUES: Final[tuple[Bloque, ...]] = tuple(
    _bloques(re.sub(r"/\*.*?\*/", "", emitir_css(), flags=re.DOTALL))
)


def _especificidad(selector: str) -> int:
    """Return the middle component of the specificity of ``selector``.

    Only that component ever varies here: no rule the emitter writes carries an
    id or a bare element, so a single number orders them all. ``:not()`` adds
    nothing of its own and contributes the specificity of its argument, which
    the attribute count already includes.

    Args:
        selector: Prelude of a rule this model understands.

    Returns:
        Number of classes, attributes and pseudo-classes in the selector.
    """
    if selector == "@theme":
        # Tailwind compiles the block into a plain :root rule.
        return 1
    return selector.count("[") + len(re.findall(r":(?!not\b)[a-z-]+", selector))


def _aplica(selector: str, atributos: dict[str, str]) -> bool:
    """Report whether ``selector`` matches a root element carrying ``atributos``."""
    if selector == "@theme":
        return True
    for atributo, valor in re.findall(r':not\(\[([\w-]+)="([^"]+)"\]\)', selector):
        if atributos.get(atributo) == valor:
            return False
    exigidos = re.sub(r":not\([^)]*\)", "", selector)
    return all(
        atributos.get(atributo) == valor
        for atributo, valor in re.findall(r'\[([\w-]+)="([^"]+)"\]', exigidos)
    )


def _resolver(atributos: dict[str, str], sistema_oscuro: bool) -> dict[str, str]:
    """Return the winning value of every colour and family custom property.

    Args:
        atributos: Attributes rendered onto the root element.
        sistema_oscuro: What ``prefers-color-scheme`` reports.

    Returns:
        Property to the value that survives the cascade.
    """
    peso_ganador: dict[str, tuple[int, int]] = {}
    valores: dict[str, str] = {}
    for orden, bloque in enumerate(BLOQUES):
        if bloque.medio != "" and not (
            sistema_oscuro and CONSULTA_OSCURA in bloque.medio
        ):
            continue
        if SELECTOR_CONOCIDO.match(bloque.selector) is None:
            continue
        if not _aplica(bloque.selector, atributos):
            continue
        peso = (_especificidad(bloque.selector), orden)
        for propiedad, valor in bloque.declaraciones.items():
            if not propiedad.startswith(PREFIJOS):
                continue
            if peso_ganador.get(propiedad, (-1, -1)) < peso:
                peso_ganador[propiedad] = peso
                valores[propiedad] = valor
    return valores


class Escenario(NamedTuple):
    """One state the surface can be in, as the browser sees it.

    Attributes:
        tema: Theme the reader should be looking at.
        modo: Mode the reader should be looking at.
        atributos: What the root element carries in that state.
        sistema_oscuro: What the operating system prefers.
    """

    tema: Tema
    modo: Modo
    atributos: dict[str, str]
    sistema_oscuro: bool


#: The eight states, which are the four combinations reached both ways: by
#: letting the operating system decide and by forcing the mode. Both routes have
#: to land on the same palette, and the forced ones are where the axis breaks:
#: an explicit dark on the optional theme is the only state that needs a rule
#: carrying two attributes.
ESCENARIOS: Final[dict[str, Escenario]] = {
    "omision, sistema en claro": Escenario("corriente", "claro", {}, False),
    "omision, sistema en oscuro": Escenario("corriente", "oscuro", {}, True),
    "omision forzada a oscuro": Escenario(
        "corriente", "oscuro", {"data-modo": "oscuro"}, False
    ),
    "omision forzada a claro con el sistema en oscuro": Escenario(
        "corriente", "claro", {"data-modo": "claro"}, True
    ),
    "institucional, sistema en claro": Escenario(
        "institucional", "claro", {"data-tema": "institucional"}, False
    ),
    "institucional, sistema en oscuro": Escenario(
        "institucional", "oscuro", {"data-tema": "institucional"}, True
    ),
    "institucional forzado a oscuro": Escenario(
        "institucional",
        "oscuro",
        {"data-tema": "institucional", "data-modo": "oscuro"},
        False,
    ),
    "institucional forzado a claro con el sistema en oscuro": Escenario(
        "institucional",
        "claro",
        {"data-tema": "institucional", "data-modo": "claro"},
        True,
    ),
}


@pytest.mark.parametrize("escenario", ESCENARIOS.values(), ids=list(ESCENARIOS))
def test_cada_combinacion_resuelve_a_su_propia_paleta(escenario: Escenario) -> None:
    """No combination may inherit the colours of another one.

    The defect this closes: the theme blocks are emitted before the mode ones,
    or the block that carries both attributes disappears. Either way
    ``data-tema="institucional"`` plus ``data-modo="oscuro"`` stops winning and
    the reader gets the dark palette of the default theme over the institutional
    ground -a combination nobody designed and nobody measured. Every value on
    screen would still be a value the system publishes, so no contrast test and
    no token fixation would go red.
    """
    resuelto = _resolver(escenario.atributos, escenario.sistema_oscuro)
    medido = {
        propiedad: valor
        for propiedad, valor in resuelto.items()
        if propiedad.startswith("--color-")
    }
    esperado = {
        f"--color-{token.nombre}": token.valor(escenario.tema, escenario.modo)
        for token in tokens_de_color()
    }

    assert medido == esperado


@pytest.mark.parametrize("escenario", ESCENARIOS.values(), ids=list(ESCENARIOS))
def test_cada_combinacion_resuelve_a_la_letra_de_su_tema(escenario: Escenario) -> None:
    """The axis is colour AND type family, so the letter travels with the theme.

    The defect: the family block is emitted only inside the media query, or only
    in the light rule of the theme. The optional theme would then render in the
    default theme's letter in exactly one of its two modes, which is the kind of
    difference nobody sees in a screenshot taken in the other one.
    """
    resuelto = _resolver(escenario.atributos, escenario.sistema_oscuro)
    medido = {
        propiedad: valor
        for propiedad, valor in resuelto.items()
        if propiedad.startswith("--font-")
    }
    esperado = {
        f"--font-{familia}": pila
        for familia, pila in FAMILIAS_POR_TEMA[escenario.tema].items()
    }

    assert medido == esperado


def test_ningun_bloque_fuera_del_modelo_declara_color_ni_familia() -> None:
    """A selector this model cannot score would be dropped without a word.

    The defect: the emitter grows a shape the resolver above does not
    understand -a class, a second element, a nested rule- and every assertion in
    this file keeps passing while the sheet paints something else. The model has
    to fail loudly when it stops describing the sheet, not degrade into silence.
    """
    ajenos = sorted(
        {
            bloque.selector
            for bloque in BLOQUES
            if any(propiedad.startswith(PREFIJOS) for propiedad in bloque.declaraciones)
            and SELECTOR_CONOCIDO.match(bloque.selector) is None
        }
    )

    assert ajenos == []


def test_cada_tema_declara_toda_familia_que_un_rol_tipografico_nombra() -> None:
    """A theme that drops a family paints the other theme's letter in silence.

    ``_bloque_familias`` only overrides the families the theme itself declares,
    so a missing key emits nothing at all and the role falls back to the stack
    of the ``@theme`` block. The guide would go on printing the family the theme
    claims while the screen rendered the other one, and the emitter would not
    raise: the omission is only visible by crossing the typographic roles
    against the map of families, which is what this does.
    """
    nombradas = {rol.familia for rol in TIPOGRAFIA}
    faltantes = {
        tema: sorted(nombradas - set(FAMILIAS_POR_TEMA[tema])) for tema in TEMAS
    }

    assert faltantes == {tema: [] for tema in TEMAS}


def test_ningun_grupo_de_color_se_queda_fuera_de_las_dos_salidas() -> None:
    """A group opened in the source and forgotten in the emitter ships nothing.

    ``GRUPOS`` exists precisely so the sheet and the typed module cannot drift,
    but nothing so far checks that the single list still covers the source it
    claims to walk. Add a channel to ``tokens_de_color`` and forget it there and
    the failure is silent in both directions: the custom property is never
    declared -so ``bg-<name>`` compiles to nothing- and the typed module never
    exports the group, while the token keeps being counted by
    ``tokens_de_color``. It is the same defect the palette plate shipped one
    layer above, where a group the store did not expose left the guide
    announcing twenty-one tokens and painting eighteen.

    The order is asserted too, and not only the set: the guide, the report and
    the plates print the groups in the order the source declares them.
    """
    esperados = [token.nombre for token in tokens_de_color()]
    # Deduplicated preserving order: the sheet declares every token once per
    # combination, and the first block is the one the groups lay out.
    en_css = list(dict.fromkeys(re.findall(r"--color-([\w-]+):", emitir_css())))
    en_ts = [
        nombre
        for _, cuerpo in re.findall(
            r"export const (\w+): readonly TokenColor\[\] = \[(.*?)\n\]",
            emitir_ts(),
            re.S,
        )
        for nombre in re.findall(r"nombre: '([\w-]+)'", cuerpo)
    ]

    assert en_css == esperados
    assert en_ts == esperados


def test_los_tres_estados_llegan_al_modulo_tipado_con_su_icono() -> None:
    """A colour published without its icon is an icon chosen again downstream.

    That is not hypothetical: with only the colour emitted, the catalogue
    resolved the shape itself with
    ``codigo === 'certificado' ? 'circle-check' : 'triangle-alert'``, and the
    two states that mean opposite things ended up with the same triangle. The
    emitter can regress in silence here -drop the field, invert the condition
    that skips it- and every contrast assertion would stay green, because the
    palette would still be correct and simply unreachable.
    """
    modulo = emitir_ts()
    tabla = dict(
        re.findall(r"codigo: '([\w-]+)', token: '[\w-]+', icono: '([\w:-]+)'", modulo)
    )

    assert tabla == {
        estado.nombre.removeprefix(PREFIJO_CERTIFICACION): estado.icono
        for estado in CERTIFICACION
    }
    # Twice on purpose and never emptily: inline on the token, which is what
    # the plate of the guide walks, and in the table of states, which is what
    # whoever paints a row reads.
    assert (
        re.findall(r"icono: '([^']*)'", modulo)
        == [estado.icono for estado in CERTIFICACION] * 2
    )


def test_la_letra_propia_de_un_tema_esta_entre_las_que_se_descargan() -> None:
    """A face nobody downloads renders as the other theme's letter.

    The defect: the optional theme moves to a face that ``nuxt.config.ts`` never
    lists, so the module never fetches it, the stack falls through to
    ``system-ui`` and the theme is published as one letter and painted in
    another. Only the faces that actually change with the theme are required
    here: a stack shared by every theme is not part of the axis, and the
    repository already leaves those to the automatic detection of the module.
    """
    configuracion = (RAIZ / "frontend" / "nuxt.config.ts").read_text(encoding="utf-8")
    declaradas = re.search(
        r"fonts:\s*\{\s*families:\s*\[(.*?)\]", configuracion, flags=re.DOTALL
    )
    assert declaradas is not None, "nuxt.config.ts ya no declara fonts.families"
    descargadas = set(re.findall(r"name: '([^']+)'", declaradas.group(1)))

    propias: set[str] = set()
    for familia in FAMILIAS_POR_TEMA[TEMA_OMISION]:
        pilas = {FAMILIAS_POR_TEMA[tema][familia] for tema in TEMAS}
        if len(pilas) == 1:
            continue
        propias |= {
            cara for cara in (_cara(pila) for pila in pilas) if cara is not None
        }

    assert propias, "ningun tema cambia de familia: el eje dejo de ser color Y letra"
    assert propias <= descargadas


def _cara(pila: str) -> str | None:
    """Return the first named face of a font stack, or None when it is generic."""
    encontrada = re.match(r'"([^"]+)"', pila.strip())
    return None if encontrada is None else encontrada.group(1)
