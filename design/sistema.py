"""The portal's design system, declared once and emitted everywhere.

The visual world is a man-machine line diagram: a visible modular grid,
orthogonal connectors, and current that lights up as a figure is traced back to
its origin. It was chosen by the user on 11-ago-2026 over the direction the
concept roll had assigned.

Two decisions govern every value below, and both were measured rather than
asserted:

1.  **State is carried by luminance, never by hue alone.** The world's original
    traffic-signal palette put red against green, which under simulated
    protanopia separates by dE=20.0: exactly on the threshold, held up only by a
    luminance difference. Green is gone. Red survives only for errors and never
    travels without a shape and an icon beside it.

2.  **The current ramp and the semantic marks are two different channels.** A
    first attempt put four states on one ladder and failed in light mode, where
    every state must sit below 0.267 relative luminance to clear 3:1 against the
    ground: dE=7.2 between the warning and the error under protanopia. Splitting
    the channels fixed it. The ramp is pure luminance, which no dichromacy
    loses; the semantic marks carry colour plus shape plus icon.

Both modes ship. ``prefers-color-scheme`` decides by default and the reader may
override it, because an eight-hour shift in a dense table is not the same scene
as a demonstration.

**Two themes ship as well, and the axis is colour *and* type family.** The
default one, ``corriente``, is the diagram world described above and it is
frozen: fifteen screenshots, a contrast matrix and a documented iteration were
delivered against it, so every value it holds is pinned byte for byte by
``tests/ml/test_contraste_temas.py`` -the seventeen that were delivered and
every slot opened afterwards, each of which reuses a delivered value under this
theme precisely so that nothing moves. The optional one, ``institucional``, is
the palette the team's Figma file declares, with Inter as its family. Neither
replaces the other: a theme is a preference, and the reader picks it.

Every institutional value below carries its provenance. A comment that opens
with an asterisk transcribes a swatch of ``docs/entregables/figma/`` literally;
any other value is a derivation and the comment states the rule that produced
it.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final, Literal

Modo = Literal["claro", "oscuro"]
Tema = Literal["corriente", "institucional"]

#: The order the guide, the emitter and the selector all walk.
TEMAS: Final[tuple[Tema, ...]] = ("corriente", "institucional")

#: The theme the portal boots into, and the one the A4 evidence was captured on.
TEMA_OMISION: Final[Tema] = "corriente"

VERSION: Final[str] = "v2.0"
FECHA: Final[str] = "2026-08-16"

#: The one idea the surface owns, printed into the artifact as a contract.
TESIS: Final[str] = (
    "Ninguna cifra aparece sin su procedencia, y recorrerla hacia atras enciende "
    "la corriente que la sostiene."
)


@dataclass(frozen=True)
class Paleta:
    """Values of one token inside one theme.

    Attributes:
        claro: Hex value in light mode.
        oscuro: Hex value in dark mode.
    """

    claro: str
    oscuro: str

    def valor(self, modo: Modo) -> str:
        """Return the hex value for ``modo``."""
        return self.claro if modo == "claro" else self.oscuro


@dataclass(frozen=True)
class Token:
    """One colour of the system, with a value per theme and per mode.

    Attributes:
        nombre: CSS custom property name without the ``--color-`` prefix.
        corriente: Palette of the default theme. Frozen evidence: the A4
            screenshots were taken against it.
        institucional: Palette of the optional theme, derived from the Figma
            file of the team.
        uso: Spanish prose printed in the guide and in the report.
        informa: Whether the token may carry meaning. A token that does not
            inform is decorative and is exempt from the 3:1 component boundary.
        icono: Name of the icon that travels with the token, when the token is
            a state. The rule "colour plus shape plus icon" is only enforceable
            if the icon is declared beside the colour instead of being chosen
            again in every component: the catalogue picked its two icons in a
            ternary and two opposite states ended up sharing one.
        sobre: Name of the token this one is read against. Almost everything is
            read over the page ground, and the exceptions are real: a label of
            the sidebar sits on the sidebar, which under the institutional
            theme is navy while the page is white. Measuring it over the page
            would publish a ratio nobody ever sees.
        es_suelo: Whether the token is itself a ground. A ground is never a
            foreground, so grading it against another ground states a
            requirement that does not exist.
    """

    nombre: str
    corriente: Paleta
    institucional: Paleta
    uso: str
    informa: bool = True
    icono: str = ""
    sobre: str = "ground"
    es_suelo: bool = False

    def valor(self, tema: Tema, modo: Modo) -> str:
        """Return the hex value for ``tema`` in ``modo``."""
        return self.paleta(tema).valor(modo)

    def paleta(self, tema: Tema) -> Paleta:
        """Return the palette this token uses under ``tema``."""
        return self.corriente if tema == "corriente" else self.institucional


@dataclass(frozen=True)
class RolTipografico:
    """One step of the type scale.

    The weight is part of the role and not a decoration. The previous system
    fixed every one of its nine roles at weight 400, and the rendered page
    measured 750 of 750 text nodes at that single weight, headings included.
    With size as the only channel and steps of 1.2, no jump read as a jump.
    """

    nombre: str
    tamano_px: int
    interlinea_px: int
    peso: int
    espaciado: str
    familia: Literal["display", "sans", "mono"]
    uso: str


def _busca(grupo: tuple[Token, ...], nombre: str) -> Token:
    """Return the token called ``nombre`` inside ``grupo``.

    Tokens that borrow another token's palette whole -the sidebar under the
    default theme, every certification state- are built with this instead of
    transcribing the hex again. A transcription is a copy, and a copy can drift
    from its original without anything noticing, which is the exact failure
    this design system was rewritten to close.

    Args:
        grupo: Group already declared above the caller.
        nombre: Token name inside that group.

    Returns:
        The token, so the caller can borrow one of its palettes.

    Raises:
        KeyError: If the group holds no token with that name.
    """
    for token in grupo:
        if token.nombre == nombre:
            return token
    raise KeyError(f"token desconocido en el grupo: {nombre}")


# ---------------------------------------------------------------------------
#  Ground and grid. The grid is visible: it is the world, not a guide.
# ---------------------------------------------------------------------------

SUPERFICIE: Final[tuple[Token, ...]] = (
    Token(
        "ground",
        Paleta("#F4F6F9", "#0A0A0C"),
        # *Superficie in light. The dark ground is derived from *Navegacion by
        # dropping its luminance: a deep blue, never pure black, which is the
        # rule the system already set itself.
        #
        # DECLARED EXCEPTION, institutional light: #FFFFFF is pure white, and
        # rule 4 of `docs/orchestration/checklist-ui.md` forbids pure white as
        # a surface. It stands because *Superficie of the design file IS pure
        # white and this theme exists to carry that file, not to improve on
        # it; the default theme keeps #F4F6F9 and remains the ground the rule
        # describes. It is a conflict between two normative sources, resolved
        # in favour of the archive and written down here so the next reader
        # does not read it as an oversight and quietly darken it -which would
        # move all 44 contrast pairs and every plate captured against them.
        Paleta("#FFFFFF", "#0B1B2B"),
        "Suelo de la pantalla. En oscuro nunca es negro puro: casi negro en el "
        "tema de omision, azul profundo en el institucional.",
        es_suelo=True,
    ),
    Token(
        "ground-alt",
        Paleta("#EAEEF4", "#131519"),
        # Light: derived from *Navegacion, lightened to 1.10:1 over white.
        # Dark: *Navegacion used as a panel over the deeper ground.
        Paleta("#F1F4F8", "#102A43"),
        "Fila alterna de tabla, cabecera de panel y celda agrupada.",
        es_suelo=True,
    ),
    Token(
        "grid",
        Paleta("#DCE2EB", "#1C2028"),
        # Derived in both modes: one step of the ground towards the ramp.
        Paleta("#DCE3EC", "#1D3348"),
        "Filete de un pelo: borde de tarjeta, separador de fila y linea de tabla.",
        informa=False,
    ),
    Token(
        "reticula",
        # The visible modular grid of the man-machine diagram. In the default
        # theme it IS the world and it is painted across the whole shell.
        Paleta("#DCE2EB", "#1C2028"),
        # The institutional theme does not inherit that world. Its own guide
        # asks for contained surfaces over a calm ground -"los neutros
        # sostienen tablas, metadatos y grandes volumenes de informacion"- and
        # a modular grid drawn under a dense table is noise competing with the
        # data. It is painted in its own ground, which makes it invisible and
        # keeps every value in this file a real colour: `transparent` would
        # read as a hex nowhere and the contrast machinery would choke on it.
        Paleta("#FFFFFF", "#0B1B2B"),
        "Cuadricula modular del chasis. Decorativa, y solo el tema de omision la "
        "pinta.",
        informa=False,
    ),
)

# ---------------------------------------------------------------------------
#  Channel 1: the current. Pure luminance, four rungs.
#  Minimum luminance step measured: 0.149 in dark, 0.061 in light.
# ---------------------------------------------------------------------------

CORRIENTE: Final[tuple[Token, ...]] = (
    Token(
        "corriente-apagado",
        Paleta("#A8B2C1", "#4A5361"),
        # Derived: the rung stays deliberately below 3:1 (2.10:1 and 2.38:1).
        Paleta("#A8B4C4", "#46586B"),
        "Conector en reposo. Filete decorativo: PROHIBIDO que informe (1.98:1 y "
        "2.54:1).",
        informa=False,
    ),
    Token(
        "corriente-tenue",
        Paleta("#5F6A7D", "#7A8698"),
        # Derived from *Navegacion towards the ground until 4.5:1 is cleared:
        # 7.05:1 in light, 6.98:1 in dark.
        Paleta("#4A5A6E", "#93A6BC"),
        "Texto secundario y nodo alcanzable. En claro se oscurece para cumplir 4.5:1.",
    ),
    Token(
        "corriente-medio",
        Paleta("#414B5B", "#B4C2D4"),
        # Light: *Secundario. Dark: derived from it by raising luminance over
        # the deep blue ground.
        Paleta("#1D4C6E", "#BFD0E2"),
        "Conector recorrido, etiqueta de eje y borde de campo que informa.",
    ),
    Token(
        "corriente-pleno",
        Paleta("#14171D", "#E8F4FF"),
        # Light: *Navegacion. Dark: derived, the same hue lifted to 15.41:1.
        Paleta("#102A43", "#EAF2FA"),
        "Corriente plena: texto de cuerpo, cifra de tabla y nodo activo.",
    ),
)

# ---------------------------------------------------------------------------
#  Channel 2: semantics. Colour AND shape AND icon, never colour alone.
# ---------------------------------------------------------------------------

SEMANTICOS: Final[tuple[Token, ...]] = (
    Token(
        "error",
        Paleta("#8C1D18", "#FF5A36"),
        # Derived from *Error (#B8443F) by darkening, hue and saturation kept.
        # The swatch itself could not ship: at #B8443F it sits at 5.33:1 and
        # *Exito at 5.23:1, so under protanopia the two separate by dE 10.1
        # against a floor of 13.6, and an error reads like a confirmation.
        # Light is #B8443F darkened 20 % -> 7.46:1 and dE 14.5. Dark starts
        # from the same swatch lifted for the deep ground (#F08078, dE 13.1
        # against a floor of 21.5) and darkens it 12 % -> 5.13:1 and dE 22.6.
        Paleta("#933632", "#EC5B51"),
        "Error y accion destructiva. Siempre con icono de aspa.",
    ),
    Token(
        "aviso",
        Paleta("#9A6200", "#FFC233"),
        # Light: *Atencion darkened 12 %, hue 36.6 deg and saturation kept.
        # The swatch itself (#B97812) gives 3.65:1 over white and a token that
        # carries text must clear 4.5:1, so the identity amber cannot ship as
        # this token. It does NOT ship as any other token either: this file
        # emits no theme invariant brand group, so the swatch lives hardcoded
        # in `MarcaKarisma.vue` -the accent bar of the symbol- with its reason
        # written there. An earlier version of this comment announced an
        # `aviso-marca` token below; that token was never written, and a
        # comment that promises a token is how a reader ends up looking for
        # one. The pending request is a `marca-*` group here, invariant to the
        # theme, which is what would let the component stop carrying hex.
        # Dark: the swatch lifted for the deep ground.
        Paleta("#A36A10", "#E8A33D"),
        "Aviso en texto. Siempre con icono de triangulo.",
    ),
    Token(
        "ok",
        Paleta("#1F6F43", "#4ADE80"),
        # Light: *Exito. Dark: the same swatch lifted for the deep ground.
        Paleta("#287A58", "#5FCB94"),
        "Confirmacion. Siempre con icono de marca.",
    ),
    Token(
        "info",
        Paleta("#6D28D9", "#C4B5FD"),
        # Light: *Secundario darkened until it clears 4.5:1 over white, hue
        # kept, which is the blue the file's own interactive-states row shows
        # for `--karisma-status-info`. Measured: 22.8 against *Exito, well over
        # the floor.
        #
        # Dark keeps a violet, and the reason is not the one written here
        # before. The earlier note blamed the action colour for colliding with
        # *Exito, which was a category error -an action is not a semantic mark
        # and the two never share a surface. The pair that actually collapses
        # is this one: `info` against `ok`. Taking the file blue into dark
        # drops them to dE 10.4 under tritanopia against a floor of 21.5,
        # because on a dark ground blue and green converge. The violet is the
        # nearest hue that survives, at 25.9, and it is declared as a departure
        # from the octet rather than presented as one of its colours.
        Paleta("#17395B", "#B9A7F2"),
        "Informativo y enlace. Siempre subrayado o con icono.",
    ),
)

#: Why "colour plus shape plus icon" is load bearing rather than polite.
#:
#: Dark mode separates the semantic marks well under all three simulated
#: dichromacies. Light mode does not, and cannot: on a light ground all four
#: must clear 4.5:1, which caps them below 0.16 relative luminance, and four
#: hues do not separate inside that band. A reader with protanopia tells an
#: error from a warning by the cross and the triangle, not by the hue.
#:
#: The number itself is deliberately absent here. It was written by hand once,
#: drifted from the computation, and a test caught it: design/contraste.py
#: measures it and design/emitir.py publishes what it measured.

#: Categorical series for charts. Ordered so that adjacent series separate under
#: every simulated dichromacy; each one also carries its own marker shape and
#: dash pattern, because a chart may never depend on colour alone.
#:
#: The six values do NOT change with the theme, and that is a decision rather
#: than an omission: a series is a data channel and not brand identity, the
#: Figma file declares no categorical palette, and these six are already
#: verified under three dichromacies. What does get re-measured per theme is
#: their ratio over each ground, because the institutional dark ground is
#: #0B1B2B and not #0A0A0C.
#: Channel 3: action and selection.
#:
#: This slot did not exist until the institutional theme asked for it, and its
#: absence is what made that theme unrecognisable. Its guide says it plainly:
#: "el azul profundo estructura la navegacion; el verde azulado concentra
#: acciones y seleccion; el ambar se reserva para atencion". With no action
#: slot the two teals had nowhere to land, the theme shipped as the default
#: ramp in another blue, and the one colour that carried the identity was the
#: one left out.
#:
#: The default theme loses nothing: its action values ARE its full current, the
#: same hex its buttons already paint, so every surface that moves from
#: `corriente-pleno` to `accion` renders byte for byte what it rendered before
#: and gains the ability to change with the theme.
ACCION: Final[tuple[Token, ...]] = (
    Token(
        "accion",
        # The default theme acts with its own full current: identical to
        # `corriente-pleno`, on purpose, so nothing about it moves.
        Paleta("#14171D", "#E8F4FF"),
        # *Accion. In dark it lifts over the deep blue ground until it clears
        # the contrast a button label needs.
        Paleta("#086B70", "#3FB3B5"),
        "Accion primaria y seleccion: boton, fila elegida y pestana en curso.",
    ),
    Token(
        "accion-apoyo",
        # Derived one rung down the default ramp.
        Paleta("#414B5B", "#B4C2D4"),
        # *Apoyo. The lighter teal the file reserves for support and emphasis.
        Paleta("#15989A", "#5FD0D2"),
        "Realce de la accion: subrayado en curso, filete de foco y grafico de apoyo.",
    ),
    Token(
        "seleccion",
        # A tint of the ground towards the action, in both themes. It is a
        # surface and never carries text on its own, so it is exempt.
        Paleta("#E7EAF0", "#181B22"),
        Paleta("#E6F2F1", "#123443"),
        "Superficie elegida: fila marcada, tarjeta seleccionada y paso en curso.",
        informa=False,
    ),
)

#: Channel 4: the chassis. One sidebar, two themes.
#:
#: The portal ships a single shell for both themes, because two shells would be
#: two products and would duplicate every unhappy state. What changes with the
#: theme is the ground the rail is painted on and how the current module is
#: marked, and those two are tokens rather than conditionals in a component:
#: a component that branched on the theme would have to be edited again the day
#: a third one appeared.
#:
#: The four values below are why the slot exists at all. Under the default
#: theme the rail is the alternate ground and the current module is told apart
#: by luminance and weight, with no filled block -which is what the delivered
#: screenshots show-. Under the institutional theme the rail is *Navegacion and
#: the current module is a filled block of *Accion, which is what its own guide
#: asks for. With one pair of tokens both readings are the same markup.
BARRA_LATERAL: Final[tuple[Token, ...]] = (
    Token(
        "barra-lateral",
        # The default theme keeps the alternate ground: the rail is a panel of
        # the same world, one step off the page and nothing else.
        _busca(SUPERFICIE, "ground-alt").corriente,
        # *Navegacion, in both modes. Its guide gives the deep blue exactly one
        # job -"el azul profundo estructura la navegacion"- and the rail is the
        # navigation, so it carries that blue whether the page around it is
        # white or the deep ground. In dark it coincides with `ground-alt`,
        # which is the same colour doing the same work.
        Paleta("#102A43", "#102A43"),
        "Suelo de la barra lateral. Con el tema cambia el suelo, nunca la estructura.",
        es_suelo=True,
    ),
    Token(
        "barra-lateral-activo",
        # No filled block under the default theme, on purpose: the current
        # module is told apart by luminance and weight. Painting the block in
        # the rail's own ground makes it invisible without introducing a
        # keyword the contrast machinery could not measure.
        _busca(SUPERFICIE, "ground-alt").corriente,
        # *Accion, filled: "el verde azulado concentra acciones y seleccion",
        # and the module on screen is the selection of the rail. It lifts with
        # the mode because the block is the action colour and not a copy of it.
        _busca(ACCION, "accion").institucional,
        "Bloque del modulo en curso. Relleno solo donde el tema tiene color de accion.",
        es_suelo=True,
    ),
    Token(
        "barra-lateral-texto",
        # What the rail already paints in the delivered screenshots.
        _busca(CORRIENTE, "corriente-tenue").corriente,
        # Derived: the light rung of the institutional ramp, 9.30:1 over the
        # navy in both modes. The page ramp cannot be reused here -under the
        # institutional light theme `corriente-pleno` IS the navy of the rail,
        # so the label would be painted in its own ground and disappear.
        Paleta("#BFD0E2", "#BFD0E2"),
        "Etiqueta en reposo de la barra lateral, medida sobre la barra y no sobre "
        "el suelo de la pagina.",
        sobre="barra-lateral",
    ),
    Token(
        "barra-lateral-activo-texto",
        _busca(CORRIENTE, "corriente-pleno").corriente,
        # Over the filled teal: white in light (6.27:1) and the deep ground in
        # dark (6.90:1). The block itself lifts with the mode, so the label
        # that sits on it has to invert with it.
        Paleta("#FFFFFF", "#0B1B2B"),
        "Etiqueta del modulo en curso, sobre su bloque.",
        sobre="barra-lateral-activo",
    ),
)

#: Prefix every certification state carries, declared once.
#:
#: The consumer strips it to recover the code the catalogue stores, so the
#: string lives here and not in the emitter and not in a component.
PREFIJO_CERTIFICACION: Final[str] = "certificacion-"


def _estado(codigo: str, canal: str, icono: str, uso: str) -> Token:
    """Return a certification state that borrows a semantic channel whole.

    The state does not own a colour: it points at one of the four semantic
    marks and takes its palette entire, in both themes and both modes. That is
    what makes "three states, three channels" a structural property instead of
    a coincidence of three hex values that happen to differ today.

    Args:
        codigo: Value the catalogue stores, without the prefix.
        canal: Name of the semantic token whose palette the state borrows.
        icono: Icon that travels with it, from the collection the app bundles.
        uso: Spanish prose printed in the guide.

    Returns:
        The state as a token of the system, named with its prefix.
    """
    base = _busca(SEMANTICOS, canal)
    return Token(
        f"{PREFIJO_CERTIFICACION}{codigo}",
        base.corriente,
        base.institucional,
        uso,
        icono=icono,
    )


#: The three states of certification, which until this version were two.
#:
#: The catalogue chose its icon with ``codigo === 'certificado' ? 'circle-check'
#: : 'triangle-alert'`` and painted everything that was not certified in the
#: warning colour. "En revision" and "Obsoleto" therefore shared colour AND
#: shape, and they mean opposite things to the person this product is for: one
#: says use it and mind the caveat, the other says do not use it. Two opposite
#: instructions rendered identically is not a palette problem, it is a wrong
#: answer given confidently.
#:
#: Each state borrows a channel whole and declares its own icon, so the rule
#: the system already published -colour AND shape AND icon- finally applies to
#: the one place that was breaking it. The three are measured against each
#: other under the three simulated dichromacies like any other family.
CERTIFICACION: Final[tuple[Token, ...]] = (
    _estado(
        "certificado",
        "ok",
        "lucide:circle-check",
        "Certificado: el dato se puede usar. Canal ok, icono de marca.",
    ),
    _estado(
        "en-revision",
        "aviso",
        "lucide:clock",
        "En revision: se puede usar con reserva. Canal aviso, icono de reloj.",
    ),
    _estado(
        "obsoleto",
        "error",
        "lucide:circle-slash",
        "Obsoleto: NO se debe usar. Canal error, icono de circulo tachado.",
    ),
)

SERIES: Final[tuple[Token, ...]] = (
    Token(
        "serie-1",
        Paleta("#1D4ED8", "#7DD3FC"),
        Paleta("#1D4ED8", "#7DD3FC"),
        "Serie 1. Marcador circulo, linea continua.",
    ),
    Token(
        "serie-2",
        Paleta("#B45309", "#FFC233"),
        Paleta("#B45309", "#FFC233"),
        "Serie 2. Marcador cuadrado, linea de guiones.",
    ),
    Token(
        "serie-3",
        Paleta("#1F6F43", "#4ADE80"),
        Paleta("#1F6F43", "#4ADE80"),
        "Serie 3. Marcador triangulo, linea de puntos.",
    ),
    Token(
        "serie-4",
        Paleta("#6D28D9", "#C4B5FD"),
        Paleta("#6D28D9", "#C4B5FD"),
        "Serie 4. Marcador rombo, guion y punto.",
    ),
    Token(
        "serie-5",
        Paleta("#0E7490", "#67E8F9"),
        Paleta("#0E7490", "#67E8F9"),
        "Serie 5. Marcador cruz, linea larga.",
    ),
    Token(
        "serie-6",
        Paleta("#9D174D", "#F9A8D4"),
        Paleta("#9D174D", "#F9A8D4"),
        "Serie 6. Marcador estrella, guion doble.",
    ),
)

# ---------------------------------------------------------------------------
#  Type. Nine roles, and the weight is a real channel this time.
# ---------------------------------------------------------------------------

TIPOGRAFIA: Final[tuple[RolTipografico, ...]] = (
    RolTipografico(
        "display",
        40,
        44,
        600,
        "-0.02em",
        "display",
        "Cifra unica que domina una pantalla.",
    ),
    RolTipografico(
        "titulo-1",
        28,
        34,
        600,
        "-0.015em",
        "display",
        "Titulo de pantalla, uno por vista.",
    ),
    RolTipografico(
        "titulo-2", 20, 26, 600, "-0.01em", "display", "Titulo de panel y de lamina."
    ),
    RolTipografico(
        "titulo-3", 15, 20, 600, "0", "sans", "Encabezado de grupo y de columna."
    ),
    RolTipografico(
        "cuerpo", 14, 21, 400, "0", "sans", "Texto por omision de la interfaz densa."
    ),
    RolTipografico(
        "cuerpo-amplio",
        16,
        26,
        400,
        "0",
        "sans",
        "Parrafo largo: ayuda y respuesta del asistente.",
    ),
    RolTipografico(
        "etiqueta",
        12,
        16,
        500,
        "0.03em",
        "sans",
        "Etiqueta de campo y encabezado de tabla.",
    ),
    RolTipografico(
        "dato",
        16,
        22,
        500,
        "0",
        "mono",
        "Cifra de tabla y de tarjeta, con cifras tabulares.",
    ),
    RolTipografico(
        "micro", 11, 15, 500, "0.02em", "sans", "Nota al pie y leyenda de grafica."
    ),
)

#: Three weights carry the hierarchy the old system tried to carry with size
#: alone: 400 for running text, 500 for labels and figures, 600 for headings.
PESOS: Final[tuple[int, ...]] = (400, 500, 600)

#: The type family is part of the theme axis, not a separate switch.
#:
#: The default theme keeps Lexend Deca for display and Fira Sans for running
#: text, which is what the fifteen delivered screenshots show. The
#: institutional theme uses Inter for both, because that is what the Figma
#: exports declare -"Inter mantiene claridad en tablas, filtros y metadatos"-
#: and a theme that swaps the palette while keeping another system's letter is
#: not the theme that was designed.
#:
#: The mono role does not move. It exists for tabular figures, where the
#: requirement is a fixed advance width rather than identity, and the Figma
#: file declares no monospace face.
FAMILIAS_POR_TEMA: Final[dict[Tema, dict[str, str]]] = {
    "corriente": {
        "display": '"Lexend Deca", system-ui, sans-serif',
        "sans": '"Fira Sans", system-ui, sans-serif',
        "mono": '"IBM Plex Mono", ui-monospace, monospace',
    },
    "institucional": {
        "display": '"Inter", system-ui, sans-serif',
        "sans": '"Inter", system-ui, sans-serif',
        "mono": '"IBM Plex Mono", ui-monospace, monospace',
    },
}

#: The families of the default theme, which are the ones the @theme block ships.
FAMILIAS: Final[dict[str, str]] = FAMILIAS_POR_TEMA[TEMA_OMISION]

# ---------------------------------------------------------------------------
#  Rhythm, shape and depth.
# ---------------------------------------------------------------------------

ESPACIADO_BASE_PX: Final[int] = 4

#: The diagram world is drawn, not moulded: corners stay tight and the pill is
#: reserved for what is genuinely round.
RADIOS: Final[tuple[tuple[str, int, str], ...]] = (
    ("sm", 2, "Chip, insignia y celda."),
    ("md", 4, "Boton, campo y nodo del diagrama."),
    ("lg", 6, "Panel y dialogo."),
    ("full", 999, "Punto de estado y boton circular de icono."),
)

#: Elevation is a last resort here. The world separates regions with the grid
#: and with ground-alt, not with shadow. The measured page used one of three
#: declared levels, so the system now declares what it actually uses.
SOMBRAS: Final[tuple[tuple[str, str, str, str], ...]] = (
    (
        "menu",
        "0 4px 12px -2px rgb(10 10 12 / 0.12)",
        "0 4px 12px -2px rgb(0 0 0 / 0.5)",
        "Menu abierto y sugerencia flotante.",
    ),
    (
        "dialogo",
        "0 16px 40px -12px rgb(10 10 12 / 0.22)",
        "0 16px 40px -12px rgb(0 0 0 / 0.7)",
        "Dialogo y panel lateral.",
    ),
)

QUIEBRES: Final[tuple[tuple[str, int, str], ...]] = (
    (
        "sm",
        768,
        "La barra lateral se colapsa a una franja de iconos. IMPLEMENTADO, no "
        "declarado.",
    ),
    ("md", 1024, "Vuelve la barra lateral con etiqueta."),
    ("lg", 1280, "Aparece la segunda columna del tablero."),
    ("xl", 1440, "Ancho de captura de las figuras del informe."),
)

DENSIDAD: Final[tuple[tuple[str, int, str], ...]] = (
    ("sidebar-width", 232, "Ancho de la barra lateral desplegada."),
    ("sidebar-collapsed", 56, "Ancho de la franja de iconos por debajo de 768 px."),
    ("header-height", 52, "Alto de la cabecera fija."),
    ("grid-gap", 16, "Canal entre columnas de la reticula de 12."),
    (
        "panel-padding",
        24,
        "Relleno interno de panel. El sistema anterior usaba 12 sobre 1137 de ancho.",
    ),
    ("table-row-height", 34, "Alto de fila de tabla densa."),
    (
        "medida-maxima",
        68,
        "Caracteres por linea maximos en prosa. Lo medido antes llegaba a 179.",
    ),
)

# ---------------------------------------------------------------------------
#  Rules that fall out of the measurements, written as rules.
# ---------------------------------------------------------------------------

REGLAS: Final[tuple[str, ...]] = (
    "El estado se lee por luminancia. El color lo refuerza y nunca lo sustituye.",
    "No hay verde en la rampa de corriente: rojo contra verde separa dE=20.0 bajo "
    "protanopia, justo en el umbral.",
    "Todo semantico viaja con forma e icono. El color solo no distingue error de "
    "aviso: bajo protanopia separan dE=7.2 si se les deja solos.",
    "corriente-apagado y grid no informan nunca. Quedan por debajo de 3:1 a proposito, "
    "porque son filete y reticula, no limite de componente.",
    "El peso es un canal de jerarquia: 400 para texto corrido, 500 para etiquetas y "
    "cifras, 600 para titulares. Nueve roles con un solo peso no son nueve roles.",
    "La prosa no pasa de 68 caracteres por linea.",
    "La barra lateral colapsa de verdad por debajo de 768 px. El sistema anterior lo "
    "declaraba y no lo implementaba, y dejaba el contenido en 135 px.",
    "El tema cambia color Y familia tipografica, y los dos temas cumplen el mismo "
    "liston en los dos modos. Un tema opcional que rebajara el umbral seria una "
    "excepcion, no un tema.",
    "La paleta de series no cambia con el tema: es canal de datos, no identidad. Lo "
    "que si se vuelve a medir es su razon sobre el suelo de cada tema.",
    "Dos estados que significan lo contrario no comparten canal ni icono. "
    "Certificado, en revision y obsoleto llevan marca, reloj y circulo tachado sobre "
    "ok, aviso y error: antes los dos ultimos eran el mismo amarillo y el mismo "
    "triangulo.",
    "Un color que vive sobre la barra lateral se mide sobre la barra lateral. Su "
    "razon sobre el suelo de la pagina no dice nada de lo que el lector ve, porque "
    "bajo el tema institucional la barra es navy y la pagina es blanca.",
)


def tokens_de_color() -> tuple[Token, ...]:
    """Return every colour token in the order the guide prints them."""
    return (
        SUPERFICIE
        + CORRIENTE
        + ACCION
        + BARRA_LATERAL
        + SEMANTICOS
        + CERTIFICACION
        + SERIES
    )
