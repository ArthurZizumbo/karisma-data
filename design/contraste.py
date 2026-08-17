"""WCAG contrast and dichromacy simulation over the portal's palettes.

Every number the guide prints and the report reproduces is computed here. None
of them is typed by hand, which is what makes "verified" mean something: the
previous system published a ratio of 2.6:1 that was actually 2.80:1, and nobody
noticed because the figure had been written rather than measured.

Two families of check:

*   **Contrast**, with the WCAG 2.x relative luminance formula, for foreground
    over background pairs.
*   **Dichromacy**, with the Vienot 1999 LMS projection for protanopia,
    deuteranopia and tritanopia, followed by a CIE76 distance. It answers a
    question contrast alone cannot: whether two marks that both pass on their
    own are still distinguishable *from each other* by a reader who does not see
    one of the three cone responses.

Every entry point takes a theme as well as a mode, and the ground is resolved
per combination rather than assumed. That is not bookkeeping: the institutional
dark ground is a deep blue where the default one is almost black, so a ratio
measured on one of them says nothing about the other, and an optional theme
that quietly failed the bar the portal publishes would be worse than no second
theme at all.
"""

from __future__ import annotations

import itertools
from dataclasses import dataclass
from typing import Final, Literal

from design.sistema import (
    CERTIFICACION,
    SEMANTICOS,
    Modo,
    Tema,
    Token,
    tokens_de_color,
)

Veredicto = Literal["AAA", "AA", "AA-grande", "grafico", "superficie", "falla"]
Dicromacia = Literal["protanopia", "deuteranopia", "tritanopia"]

#: sRGB to LMS and back, Vienot, Brettel and Mollon 1999.
_RGB_LMS: Final[tuple[tuple[float, float, float], ...]] = (
    (0.31399022, 0.63951294, 0.04649755),
    (0.15537241, 0.75789446, 0.08670142),
    (0.01775239, 0.10944209, 0.87256922),
)
_LMS_RGB: Final[tuple[tuple[float, float, float], ...]] = (
    (5.47221206, -4.6419601, 0.16963708),
    (-1.1252419, 2.29317094, -0.1678952),
    (0.02980165, -0.19318073, 1.16364789),
)
_PROYECCION: Final[dict[Dicromacia, tuple[tuple[float, float, float], ...]]] = {
    "protanopia": ((0.0, 1.05118294, -0.05116099), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)),
    "deuteranopia": ((1.0, 0.0, 0.0), (0.9513092, 0.0, 0.04866992), (0.0, 0.0, 1.0)),
    "tritanopia": ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (-0.86744736, 1.86727089, 0.0)),
}


#: The families whose marks have to stay apart from each other, and the reason
#: there is more than one.
#:
#: A separation is only meaningful inside a family: two marks that never share
#: a surface do not have to be told apart, and mixing the families would
#: compare a certification badge against a link colour and then call that
#: number a floor. The certification states borrow the semantic channels whole,
#: so their three distances are a subset of the six above, which is exactly the
#: property that keeps the published floor where it was while the states gain a
#: measurement of their own.
FAMILIAS: Final[tuple[tuple[str, tuple[Token, ...]], ...]] = (
    ("semantico", SEMANTICOS),
    ("certificacion", CERTIFICACION),
)


@dataclass(frozen=True)
class Par:
    """A measured foreground over background pair.

    Attributes:
        frente: Token being read.
        fondo: Token it is read against, which is the page ground for almost
            everything and the sidebar for what lives on the sidebar.
        tema: Theme the pair was measured in.
        modo: Light or dark.
        ratio: WCAG contrast ratio.
        veredicto: Grade of that ratio.
    """

    frente: str
    fondo: str
    tema: Tema
    modo: Modo
    ratio: float
    veredicto: Veredicto


@dataclass(frozen=True)
class Separacion:
    """How far apart two marks stay for a reader with one dichromacy.

    Attributes:
        uno: First mark of the pair.
        otro: Second mark of the pair.
        familia: Family both belong to. The distance is only a requirement
            inside a family, so the number travels with the answer to "apart
            from what".
        tema: Theme the pair was measured in.
        modo: Light or dark.
        dicromacia: The simulated dichromacy that separates them worst.
        distancia: CIE76 distance under that dichromacy.
    """

    uno: str
    otro: str
    familia: str
    tema: Tema
    modo: Modo
    dicromacia: Dicromacia
    distancia: float


def _lineal(canal: int) -> float:
    """Return the linear-light value of one 0-255 sRGB channel."""
    c = canal / 255
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _canales(hex_color: str) -> tuple[float, float, float]:
    """Return the three linear-light channels of a hex colour."""
    limpio = hex_color.lstrip("#")
    return (
        _lineal(int(limpio[0:2], 16)),
        _lineal(int(limpio[2:4], 16)),
        _lineal(int(limpio[4:6], 16)),
    )


def luminancia(hex_color: str) -> float:
    """Return WCAG relative luminance."""
    r, g, b = _canales(hex_color)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def razon(frente: str, fondo: str) -> float:
    """Return the WCAG contrast ratio between two colours."""
    claro, oscuro = sorted((luminancia(frente), luminancia(fondo)), reverse=True)
    return (claro + 0.05) / (oscuro + 0.05)


def veredicto(ratio: float) -> Veredicto:
    """Grade a contrast ratio."""
    if ratio >= 7.0:
        return "AAA"
    if ratio >= 4.5:
        return "AA"
    if ratio >= 3.0:
        return "AA-grande"
    return "falla"


Matriz3 = tuple[tuple[float, float, float], ...]


def _producto(
    matriz: Matriz3, vector: tuple[float, float, float]
) -> tuple[float, float, float]:
    """Multiply a 3x3 matrix by a vector."""
    fila_a, fila_b, fila_c = matriz
    return (
        sum(fila_a[i] * vector[i] for i in range(3)),
        sum(fila_b[i] * vector[i] for i in range(3)),
        sum(fila_c[i] * vector[i] for i in range(3)),
    )


def simular(hex_color: str, dicromacia: Dicromacia) -> tuple[float, float, float]:
    """Return the linear-light colour a dichromat perceives."""
    lms = _producto(_RGB_LMS, _canales(hex_color))
    return _producto(_LMS_RGB, _producto(_PROYECCION[dicromacia], lms))


def _lab(rgb: tuple[float, float, float]) -> tuple[float, float, float]:
    """Return CIE Lab for a linear-light sRGB triple."""
    r, g, b = rgb
    x = 0.4124 * r + 0.3576 * g + 0.1805 * b
    y = 0.2126 * r + 0.7152 * g + 0.0722 * b
    z = 0.0193 * r + 0.1192 * g + 0.9505 * b

    def f(t: float) -> float:
        return t ** (1 / 3) if t > 0.008856 else 7.787 * t + 16 / 116

    fx, fy, fz = f(x / 0.95047), f(y), f(z / 1.08883)
    return (116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz))


def distancia(uno: str, otro: str, dicromacia: Dicromacia) -> float:
    """Return the CIE76 distance between two colours as a dichromat sees them."""
    a, b = _lab(simular(uno, dicromacia)), _lab(simular(otro, dicromacia))
    return float(sum((x - y) ** 2 for x, y in zip(a, b, strict=True)) ** 0.5)


def _suelo(tema: Tema, modo: Modo) -> str:
    """Return the page ground for ``tema`` in ``modo``.

    Args:
        tema: Theme whose ground is wanted.
        modo: Light or dark.

    Returns:
        The hex value most ratios of that combination are measured against.
    """
    return _fondo("ground", tema, modo)


def _fondo(nombre: str, tema: Tema, modo: Modo) -> str:
    """Return the value a token is read against, resolved per combination.

    Args:
        nombre: Name of the token that acts as the background.
        tema: Theme being audited.
        modo: Light or dark.

    Returns:
        The hex value of that background in that combination.
    """
    return token_por_nombre(nombre).valor(tema, modo)


def matriz(tema: Tema, modo: Modo) -> tuple[Par, ...]:
    """Return every token measured against what it is actually read on.

    Almost every token is read over the page ground, and the ones that are not
    say so: the labels of the sidebar declare ``sobre="barra-lateral"`` because
    under the institutional theme the rail is navy while the page is white, and
    a ratio taken over the page would be a number the reader never sees.

    Args:
        tema: Theme to measure.
        modo: Light or dark.

    Returns:
        One graded pair per token, in the order the guide prints them.
    """
    pares: list[Par] = []
    for token in tokens_de_color():
        if token.nombre == token.sobre:
            # The ground read against itself. Nothing is ever painted on the
            # page with the page as its foreground.
            continue
        ratio = razon(token.valor(tema, modo), _fondo(token.sobre, tema, modo))
        grado = veredicto(ratio)
        if token.es_suelo:
            # A background measured against another background is not a
            # contrast requirement: nothing is ever read *on top of* the ground
            # with the alternate row as its foreground. Grading it "falla" made
            # the guide accuse itself of an infringement that does not exist.
            grado = "superficie"
        elif not token.informa:
            grado = "grafico"
        pares.append(Par(token.nombre, token.sobre, tema, modo, round(ratio, 2), grado))
    return tuple(pares)


def separaciones(tema: Tema, modo: Modo) -> tuple[Separacion, ...]:
    """Return the worst dichromatic separation of every pair, family by family.

    Two families walk here: the four semantic marks and the three states of
    certification. They are measured apart because a distance is only a
    requirement between marks that can share a surface, and they are reported
    together because the floor the portal publishes has to hold for both.

    Args:
        tema: Theme to measure.
        modo: Light or dark.

    Returns:
        One entry per pair, each carrying the family it belongs to.
    """
    salida: list[Separacion] = []
    for familia, grupo in FAMILIAS:
        for uno, otro in itertools.combinations(grupo, 2):
            peor: Separacion | None = None
            for dicromacia in _PROYECCION:
                d = distancia(uno.valor(tema, modo), otro.valor(tema, modo), dicromacia)
                if peor is None or d < peor.distancia:
                    peor = Separacion(
                        uno.nombre,
                        otro.nombre,
                        familia,
                        tema,
                        modo,
                        dicromacia,
                        round(d, 1),
                    )
            if peor is not None:
                salida.append(peor)
    return tuple(salida)


def peor_separacion(tema: Tema, modo: Modo, familia: str | None = None) -> float:
    """Return the worst separation of one theme and mode.

    Args:
        tema: Theme to measure.
        modo: Light or dark.
        familia: Restrict the answer to one family, or ``None`` for the floor
            of the whole palette, which is the number the report publishes.

    Returns:
        The smallest CIE76 distance found.
    """
    return min(
        s.distancia
        for s in separaciones(tema, modo)
        if familia is None or s.familia == familia
    )


def incumplimientos(tema: Tema, modo: Modo) -> tuple[str, ...]:
    """Return every rule the palette breaks in ``tema`` and ``modo``, as prose.

    An empty result is the only acceptable one, and it is what the test asserts
    for the four combinations. A token that declares it does not inform is
    exempt from the component boundary: that exemption is the whole reason the
    flag exists.

    Args:
        tema: Theme to audit.
        modo: Light or dark.

    Returns:
        One Spanish sentence per infringement, empty when there is none.
    """
    fallos: list[str] = []
    for token in tokens_de_color():
        if token.es_suelo:
            # A ground is never a foreground. The sidebar of the institutional
            # theme is navy over a white page and reaches 14.64:1, which is a
            # surface doing its job and not a mark that informs.
            continue
        ratio = razon(token.valor(tema, modo), _fondo(token.sobre, tema, modo))
        if token.informa and ratio < 3.0:
            fallos.append(
                f"{token.nombre} informa y solo alcanza {ratio:.2f}:1 sobre "
                f"{token.sobre} en {tema} {modo}"
            )
        if not token.informa and ratio >= 3.0:
            fallos.append(
                f"{token.nombre} declara que no informa y alcanza "
                f"{ratio:.2f}:1 sobre {token.sobre} en {tema} {modo}"
            )
    return tuple(fallos)


def token_por_nombre(nombre: str) -> Token:
    """Return the token called ``nombre``."""
    for token in tokens_de_color():
        if token.nombre == nombre:
            return token
    raise KeyError(f"token desconocido: {nombre}")
