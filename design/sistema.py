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
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final, Literal

Modo = Literal["claro", "oscuro"]

VERSION: Final[str] = "v2.0"
FECHA: Final[str] = "2026-08-16"

#: The one idea the surface owns, printed into the artifact as a contract.
TESIS: Final[str] = (
    "Ninguna cifra aparece sin su procedencia, y recorrerla hacia atras enciende "
    "la corriente que la sostiene."
)


@dataclass(frozen=True)
class Token:
    """One colour of the system, with a value per mode.

    Attributes:
        nombre: CSS custom property name without the ``--color-`` prefix.
        claro: Hex value in light mode.
        oscuro: Hex value in dark mode.
        uso: Spanish prose printed in the guide and in the report.
        informa: Whether the token may carry meaning. A token that does not
            inform is decorative and is exempt from the 3:1 component boundary.
    """

    nombre: str
    claro: str
    oscuro: str
    uso: str
    informa: bool = True

    def valor(self, modo: Modo) -> str:
        """Return the hex value for ``modo``."""
        return self.claro if modo == "claro" else self.oscuro


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


# ---------------------------------------------------------------------------
#  Ground and grid. The grid is visible: it is the world, not a guide.
# ---------------------------------------------------------------------------

SUPERFICIE: Final[tuple[Token, ...]] = (
    Token(
        "ground",
        "#F4F6F9",
        "#0A0A0C",
        "Suelo de la pantalla. En oscuro es casi negro, nunca negro puro.",
    ),
    Token(
        "ground-alt",
        "#EAEEF4",
        "#131519",
        "Fila alterna de tabla, cabecera de panel y celda agrupada.",
    ),
    Token(
        "grid",
        "#DCE2EB",
        "#1C2028",
        "La reticula visible del diagrama. Decorativa por definicion.",
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
        "#A8B2C1",
        "#4A5361",
        "Conector en reposo. Filete decorativo: PROHIBIDO que informe (1.98:1 y "
        "2.54:1).",
        informa=False,
    ),
    Token(
        "corriente-tenue",
        "#7A8698",
        "#7A8698",
        "Texto secundario y nodo alcanzable. El unico token identico en los dos modos.",
    ),
    Token(
        "corriente-medio",
        "#414B5B",
        "#B4C2D4",
        "Conector recorrido, etiqueta de eje y borde de campo que informa.",
    ),
    Token(
        "corriente-pleno",
        "#14171D",
        "#E8F4FF",
        "Corriente plena: texto de cuerpo, cifra de tabla y nodo activo.",
    ),
)

# ---------------------------------------------------------------------------
#  Channel 2: semantics. Colour AND shape AND icon, never colour alone.
# ---------------------------------------------------------------------------

SEMANTICOS: Final[tuple[Token, ...]] = (
    Token(
        "error",
        "#C4341A",
        "#FF5A36",
        "Error y accion destructiva. Siempre con icono de aspa.",
    ),
    Token("aviso", "#8A5A00", "#FFC233", "Aviso. Siempre con icono de triangulo."),
    Token("ok", "#1F6F43", "#4ADE80", "Confirmacion. Siempre con icono de marca."),
    Token(
        "info",
        "#1D4ED8",
        "#7DD3FC",
        "Informativo y enlace. Siempre subrayado o con icono.",
    ),
)

#: Categorical series for charts. Ordered so that adjacent series separate under
#: every simulated dichromacy; each one also carries its own marker shape and
#: dash pattern, because a chart may never depend on colour alone.
SERIES: Final[tuple[Token, ...]] = (
    Token(
        "serie-1", "#1D4ED8", "#7DD3FC", "Serie 1. Marcador circulo, linea continua."
    ),
    Token(
        "serie-2", "#B45309", "#FFC233", "Serie 2. Marcador cuadrado, linea de guiones."
    ),
    Token(
        "serie-3", "#1F6F43", "#4ADE80", "Serie 3. Marcador triangulo, linea de puntos."
    ),
    Token("serie-4", "#6D28D9", "#C4B5FD", "Serie 4. Marcador rombo, guion y punto."),
    Token("serie-5", "#0E7490", "#67E8F9", "Serie 5. Marcador cruz, linea larga."),
    Token("serie-6", "#9D174D", "#F9A8D4", "Serie 6. Marcador estrella, guion doble."),
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

FAMILIAS: Final[dict[str, str]] = {
    "display": '"Lexend Deca", system-ui, sans-serif',
    "sans": '"Fira Sans", system-ui, sans-serif',
    "mono": '"IBM Plex Mono", ui-monospace, monospace',
}

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
)


def tokens_de_color() -> tuple[Token, ...]:
    """Return every colour token in the order the guide prints them."""
    return SUPERFICIE + CORRIENTE + SEMANTICOS + SERIES
