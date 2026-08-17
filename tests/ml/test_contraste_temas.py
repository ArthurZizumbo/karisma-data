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

The table is in three parts and the split is the point. ``FIJACION_ENTREGADA``
is the contract as it stood at commit ``aeafc6e``, which is what the published
artefacts rest on, and it does not move. ``FIJACION_AMPLIACION`` holds the four
slots the institutional identity opened afterwards -grid, action, its support
and the selected surface- and under the default theme three of the four reuse a
value the first part already fixes. ``FIJACION_CHASIS`` holds the seven the
sidebar and the certification states opened, and under the default theme not
one of them is a new colour. Growing the contract is allowed; moving what was
delivered is not, and keeping the parts apart is what lets a reader tell them
apart at a glance instead of diffing twenty-eight lines.

The rest of the file holds the optional theme to the same bar as the default
one. A second theme that quietly failed the contrast floor the portal publishes
would be worse than shipping no second theme at all.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from design import sistema
from design.contraste import (
    _suelo,
    incumplimientos,
    peor_separacion,
    razon,
    token_por_nombre,
)
from design.emitir import main
from design.sistema import CERTIFICACION, SERIES, Modo, Tema, tokens_de_color

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

#: The seven slots the chassis and the states of certification opened, and the
#: proof that the default theme paid nothing for either.
#:
#: The rail is ``ground-alt``, its resting label is ``corriente-tenue`` and the
#: module on screen is ``corriente-pleno`` over the rail's own ground: luminance
#: and weight, with no filled block, which is what the delivered screenshots
#: show. The three certification states borrow ``ok``, ``aviso`` and ``error``
#: whole. Every value below therefore appears somewhere above, and only the
#: optional theme spends the slots.
FIJACION_CHASIS: dict[str, tuple[str, str]] = {
    "barra-lateral": ("#EAEEF4", "#131519"),
    "barra-lateral-activo": ("#EAEEF4", "#131519"),
    "barra-lateral-texto": ("#5F6A7D", "#7A8698"),
    "barra-lateral-activo-texto": ("#14171D", "#E8F4FF"),
    "certificacion-certificado": ("#1F6F43", "#4ADE80"),
    "certificacion-en-revision": ("#9A6200", "#FFC233"),
    "certificacion-obsoleto": ("#8C1D18", "#FF5A36"),
}

#: The whole default theme as it stands today: the delivered contract plus both
#: extensions, fixed together so a drift in any of the three fails.
FIJACION_CORRIENTE: dict[str, tuple[str, str]] = (
    FIJACION_ENTREGADA | FIJACION_AMPLIACION | FIJACION_CHASIS
)

#: The eight colours the design file declares, and the token each one becomes.
#:
#: Six of them ship as the literal value of a token under the institutional
#: theme. This half is the transcription that the previous US did not make: its
#: plan copied six of the eight, the implementation built the palette from that
#: copy instead of from the file, and the two it dropped -*Accion and *Apoyo-
#: were the ones the file calls the heart of the identity. A theme without them
#: is the default ramp in another blue, which is exactly what shipped.
OCTETO_LITERAL: dict[str, tuple[str, str]] = {
    "Navegacion": ("102A43", "corriente-pleno"),
    "Secundario": ("1D4C6E", "corriente-medio"),
    "Accion": ("086B70", "accion"),
    "Apoyo": ("15989A", "accion-apoyo"),
    "Exito": ("287A58", "ok"),
    "Superficie": ("FFFFFF", "ground"),
}

#: The two that could not ship at their swatch value, and why.
#:
#: *Atencion gives 3.65:1 over white and a token that carries text has to clear
#: 4.5:1; *Error at its own value drops the error/success pair to dE 10.1 under
#: protanopia, so an error reads like a confirmation. Both are darkened, and
#: what is checked here is that the source still cites the swatch it departed
#: from: a derivation whose origin is not written down is indistinguishable
#: from an invented colour.
OCTETO_DERIVADO: dict[str, tuple[str, str]] = {
    "Atencion": ("B97812", "aviso"),
    "Error": ("B8443F", "error"),
}

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


def test_el_contrato_es_de_veintiocho_tokens() -> None:
    """A token added or removed changes the guide, the plates and the PDF.

    It caught exactly that: the four slots of ``FIJACION_AMPLIACION`` reached
    ``design/sistema.py`` while the palette plate of ``/guia``, the store that
    feeds it and the tables of ``a4_08`` still counted seventeen.
    """
    assert len(tokens_de_color()) == len(FIJACION_CORRIENTE) == 28
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


@pytest.mark.parametrize(("tema", "modo"), COMBINACIONES)
def test_los_tres_estados_de_certificacion_se_separan(tema: Tema, modo: Modo) -> None:
    """Two states that mean opposite things must not look alike.

    The defect, and it was in production: the catalogue chose the icon with
    ``codigo === 'certificado' ? 'circle-check' : 'triangle-alert'`` and painted
    everything that was not certified in the warning colour, so "en revision"
    and "obsoleto" arrived at the reader as the same amber triangle. One says
    use it with a caveat and the other says do not use it. Point two states at
    one channel again and this measures zero.
    """
    assert peor_separacion(tema, modo, "certificacion") >= PISO_DICROMACIA[modo]


def test_cada_estado_de_certificacion_lleva_su_propio_icono() -> None:
    """Colour is the channel light mode cannot deliver, so the shape carries.

    On a light ground every semantic mark has to clear 4.5:1, which caps them
    below 0.16 relative luminance, and inside that band four hues do not
    separate: the reader with protanopia tells the three states apart by the
    tick, the clock and the crossed circle. A state that reached the reader
    without an icon, or sharing one, would leave that reader with nothing.
    """
    iconos = [estado.icono for estado in CERTIFICACION]

    assert len(CERTIFICACION) == 3
    assert "" not in iconos
    assert len(set(iconos)) == len(iconos)


def test_el_octeto_del_archivo_esta_completo_con_su_procedencia() -> None:
    """A palette derived from a transcription loses whatever the copy dropped.

    This is the failure the previous US shipped: its plan transcribed six of
    the eight colours of the design file, the implementation built the theme
    from that table instead of from the file, and *Accion and *Apoyo -the two
    the file calls the heart of the identity- were simply not there. Nothing
    caught it, because a colour that is missing declares nothing.

    So this reads the source as text and asks for both halves of the promise:
    that each of the eight lands somewhere, and that the source still names the
    swatch it came from. A value with no provenance and an invented colour are
    the same object.
    """
    fuente = sistema.__file__
    assert fuente is not None
    codigo = Path(fuente).read_text(encoding="utf-8").upper()

    aterrizados = {
        rol: token_por_nombre(token).valor("institucional", "claro")
        for rol, (_, token) in OCTETO_LITERAL.items()
    }
    sin_procedencia = sorted(
        rol
        for rol, (valor, _) in (OCTETO_LITERAL | OCTETO_DERIVADO).items()
        if f"*{rol}".upper() not in codigo or valor not in codigo
    )

    assert aterrizados == {
        rol: f"#{valor}" for rol, (valor, _) in OCTETO_LITERAL.items()
    }
    assert sin_procedencia == []


@pytest.mark.parametrize("modo", ["claro", "oscuro"])
def test_la_reticula_solo_la_pinta_el_tema_de_omision(modo: Modo) -> None:
    """The modular grid is the default world and not a decoration to inherit.

    The defect in both directions. Give the institutional theme a visible grid
    and the shell draws a lattice under every dense table, which its own guide
    rules out -"los neutros sostienen tablas, metadatos y grandes volumenes de
    informacion"-. Paint the default one in its own ground and the man-machine
    diagram, which is the whole visual thesis of the product, disappears.
    """
    reticula = token_por_nombre("reticula")

    assert reticula.valor("institucional", modo) == _suelo("institucional", modo)
    assert reticula.valor("corriente", modo) != _suelo("corriente", modo)


@pytest.mark.parametrize("modo", ["claro", "oscuro"])
def test_la_barra_lateral_institucional_es_el_azul_de_navegacion(modo: Modo) -> None:
    """The rail is where the institutional identity is either visible or absent.

    Its guide gives the deep blue exactly one job -"el azul profundo estructura
    la navegacion"- and the rail is the navigation. Repaint it in the alternate
    ground and the optional theme becomes the default shell in another accent,
    which is precisely the outcome this US exists to undo. Nothing else in the
    suite fixes an institutional value, so nothing else would notice.
    """
    assert token_por_nombre("barra-lateral").valor("institucional", modo) == "#102A43"


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
