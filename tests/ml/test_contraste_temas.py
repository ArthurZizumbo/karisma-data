"""The theme axis of the design system, asserted against what it promises.

The first test in this file is the reason the file exists, and its table was
written before the first line of the theme axis. Fifteen screenshots of the A4
deliverable, a contrast matrix and a documented iteration were all produced
under the default theme: if opening a second theme moved one of its seventeen
values, every one of those artefacts would stop describing the product, and
nothing else in the suite would notice.

The pairs below are typed by hand on purpose. An invariant that reads the same
file it watches proves nothing, so the table is a transcription of
``design/sistema.py`` and it is never regenerated: a diff on it is exactly the
alarm it exists to raise.

The table is in two halves and the split is the point. ``FIJACION_ENTREGADA``
is the contract as it stood at commit ``aeafc6e``, which is what the published
artefacts rest on, and it does not move. ``FIJACION_AMPLIACION`` holds the four
slots the institutional identity opened afterwards -grid, action, its support
and the selected surface- and under the default theme three of the four reuse a
value the first half already fixes. Growing the contract is allowed; moving what
was delivered is not, and keeping the halves apart is what lets a reader tell
the two apart at a glance instead of diffing twenty-one lines.

The rest of the file holds the optional theme to the same bar as the default
one. A second theme that quietly failed the contrast floor the portal publishes
would be worse than shipping no second theme at all.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from design.contraste import _suelo, incumplimientos, peor_separacion, razon
from design.emitir import main
from design.sistema import SERIES, Modo, Tema, tokens_de_color

#: nombre -> (claro, oscuro) of the default theme, transcribed from
#: design/sistema.py at aeafc6e, before the theme axis was opened.
#:
#: These seventeen are the delivered contract: every screenshot, the contrast
#: matrix and the PDF already published rest on them, so a diff on any pair
#: below is the alarm this file exists to raise.
FIJACION_ENTREGADA: dict[str, tuple[str, str]] = {
    "ground": ("#F4F6F9", "#0A0A0C"),
    "ground-alt": ("#EAEEF4", "#131519"),
    "grid": ("#DCE2EB", "#1C2028"),
    "corriente-apagado": ("#A8B2C1", "#4A5361"),
    "corriente-tenue": ("#5F6A7D", "#7A8698"),
    "corriente-medio": ("#414B5B", "#B4C2D4"),
    "corriente-pleno": ("#14171D", "#E8F4FF"),
    "error": ("#8C1D18", "#FF5A36"),
    "aviso": ("#9A6200", "#FFC233"),
    "ok": ("#1F6F43", "#4ADE80"),
    "info": ("#6D28D9", "#C4B5FD"),
    "serie-1": ("#1D4ED8", "#7DD3FC"),
    "serie-2": ("#B45309", "#FFC233"),
    "serie-3": ("#1F6F43", "#4ADE80"),
    "serie-4": ("#6D28D9", "#C4B5FD"),
    "serie-5": ("#0E7490", "#67E8F9"),
    "serie-6": ("#9D174D", "#F9A8D4"),
}

#: The four slots the institutional identity needed and the delivered contract
#: did not have: a modular grid separable from the hairline, an action colour,
#: its support, and the surface of a chosen row.
#:
#: Under the default theme none of the four is a new colour. Each one reuses a
#: value already in the table above -``reticula`` is ``grid``, ``accion`` is
#: ``corriente-pleno``, ``accion-apoyo`` is ``corriente-medio``- so the theme
#: that sustains the published artefacts does not move a pixel, and only the
#: optional theme spends the slot. ``seleccion`` is the one genuinely new pair,
#: and it is a tint that nothing delivered painted.
FIJACION_AMPLIACION: dict[str, tuple[str, str]] = {
    "reticula": ("#DCE2EB", "#1C2028"),
    "accion": ("#14171D", "#E8F4FF"),
    "accion-apoyo": ("#414B5B", "#B4C2D4"),
    "seleccion": ("#E7EAF0", "#181B22"),
}

#: The whole default theme as it stands today: the delivered contract plus the
#: extension, fixed together so a drift in either half fails.
FIJACION_CORRIENTE: dict[str, tuple[str, str]] = (
    FIJACION_ENTREGADA | FIJACION_AMPLIACION
)

#: The floor each mode has to hold, in CIE76 distance under the worst of the
#: three simulated dichromacies. They are the numbers the default theme already
#: sustains, so the optional theme may raise them and may never lower them.
PISO_DICROMACIA: dict[Modo, float] = {"claro": 13.6, "oscuro": 21.5}

#: The four states the surface can be in. Themes and modes are named here
#: rather than read from the modules under test: a parametrisation built from
#: ``TEMAS`` would shrink in silence the day a theme disappeared, and a
#: parametrisation that shrinks is a suite that stops asking.
COMBINACIONES: list[tuple[Tema, Modo]] = [
    ("corriente", "claro"),
    ("corriente", "oscuro"),
    ("institucional", "claro"),
    ("institucional", "oscuro"),
]


def test_el_tema_de_omision_no_se_mueve() -> None:
    """Fix every default-theme value, byte for byte, in both modes."""
    medido = {
        token.nombre: (
            token.valor("corriente", "claro"),
            token.valor("corriente", "oscuro"),
        )
        for token in tokens_de_color()
    }

    assert medido == FIJACION_CORRIENTE


def test_el_contrato_es_de_veintiun_tokens() -> None:
    """A token added or removed changes the guide, the plates and the PDF.

    It caught exactly that: the four slots of ``FIJACION_AMPLIACION`` reached
    ``design/sistema.py`` while the palette plate of ``/guia``, the store that
    feeds it and the tables of ``a4_08`` still counted seventeen.
    """
    assert len(tokens_de_color()) == len(FIJACION_CORRIENTE) == 21
    assert len(FIJACION_ENTREGADA) == 17


@pytest.mark.parametrize(("tema", "modo"), COMBINACIONES)
def test_ningun_token_que_informa_incumple_su_liston(tema: Tema, modo: Modo) -> None:
    """Adopting the theme with Atencion at 3.65:1 would fail its own bar."""
    assert incumplimientos(tema, modo) == ()


@pytest.mark.parametrize(("tema", "modo"), COMBINACIONES)
def test_la_separacion_bajo_dicromacia_no_baja_del_piso(tema: Tema, modo: Modo) -> None:
    """Two different states must not look alike to a dichromat.

    The informative mark and the confirmation collapse under tritanopia if the
    hue is chosen by taste, and the error collapses with the confirmation under
    protanopia if the two are left sitting at the same luminance.
    """
    assert peor_separacion(tema, modo) >= PISO_DICROMACIA[modo]


@pytest.mark.parametrize(("tema", "modo"), COMBINACIONES)
def test_las_series_conservan_su_razon_sobre_cada_suelo(tema: Tema, modo: Modo) -> None:
    """The six series are shared, the ground they sit on is not.

    The institutional dark ground is #0B1B2B and not #0A0A0C, so a series that
    cleared the graphical boundary on one of them could fall below it on the
    other without anybody noticing.
    """
    fondo = _suelo(tema, modo)
    bajas = [
        serie.nombre for serie in SERIES if razon(serie.valor(tema, modo), fondo) < 3.0
    ]

    assert bajas == []


def test_el_suelo_oscuro_institucional_es_azul_y_no_negro() -> None:
    """A dark theme derived from its own navigation colour, never pure black."""
    assert _suelo("institucional", "oscuro") == "#0B1B2B"


def test_el_emisor_es_idempotente(tmp_path: Path) -> None:
    """Two runs writing different bytes make every commit show a divergence.

    ``scripts/verificar_tokens_a4.sh`` compares what is on disk against what
    the emitter produces today, so an emitter whose output depended on
    iteration order would report a defect on every run and train the team to
    ignore it.
    """
    primera, segunda = tmp_path / "uno", tmp_path / "dos"
    assert main(["--destino", str(primera)]) == 0
    assert main(["--destino", str(segunda)]) == 0

    escritos = sorted(p.relative_to(primera) for p in primera.rglob("*") if p.is_file())
    assert escritos, "el emisor no escribio ninguna salida"
    for relativa in escritos:
        assert (primera / relativa).read_bytes() == (segunda / relativa).read_bytes()
