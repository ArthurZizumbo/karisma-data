"""The KSER1 encoder, read back with the standard library and nothing else.

Every assertion here decodes the frame by hand -``struct``, with an explicit
little endian marker- and never through the module under test. A decoder written
next to its encoder shares its bugs: it would swap the same two fields, assume
the same byte order and read past the same missing padding, and the suite would
stay green while the browser drew noise.

The golden witness is the other half of the same idea. ``frontend/test/
serieBinaria.spec.ts`` reads the very bytes this file pins, so a change to the
format cannot be green on both sides.
"""

import base64
import json
import math
import struct
from collections.abc import Sequence
from typing import Final

import pytest
from generar_marco_dorado import (
    BASE64_PATH,
    COMPANION_PATH,
    GOLDEN_VALUES,
    golden_base64,
    golden_frame,
    stale_files,
)

from app.utils import serie_frame
from app.utils.serie_frame import (
    FRAME_ALIGNMENT,
    FRAME_MAGIC,
    FRAME_PREFIX_BYTES,
    FRAME_VERSION,
    encode_frame,
)

# Relative error the interface declares for the chart values, section 2.4 of the
# planning document. The table and the tooltip read the exact JSON variant.
ERROR_DECLARADO: Final[float] = 6e-8

CABECERA_MINIMA: Final[dict[str, str]] = {"metrica": "saldo_disponible_mxn"}


def _prefijo(marco: bytes) -> tuple[int, int, int, int]:
    """Read the fixed prefix of a frame.

    Args:
        marco: Encoded frame.

    Returns:
        Version, header length, number of dates and number of series.
    """
    version, reservado, cabecera_len, n_fechas, n_series = struct.unpack_from(
        "<HHIII", marco, len(FRAME_MAGIC)
    )
    assert marco[: len(FRAME_MAGIC)] == FRAME_MAGIC
    assert reservado == 0
    return int(version), int(cabecera_len), int(n_fechas), int(n_series)


def _cabecera(marco: bytes) -> dict[str, object]:
    """Read the header JSON of a frame.

    Args:
        marco: Encoded frame.

    Returns:
        The decoded header.
    """
    _, cabecera_len, _, _ = _prefijo(marco)
    contenido: dict[str, object] = json.loads(
        marco[FRAME_PREFIX_BYTES : FRAME_PREFIX_BYTES + cabecera_len].decode("utf-8")
    )
    return contenido


def _offsets(marco: bytes) -> dict[str, int]:
    """Read the offsets the header publishes.

    Args:
        marco: Encoded frame.

    Returns:
        The four offsets, as the decoder of the browser reads them.
    """
    publicados = _cabecera(marco)["offsets"]
    assert isinstance(publicados, dict)
    return {str(clave): int(valor) for clave, valor in publicados.items()}


def _bloque(marco: bytes, offset: int, typecode: str, longitud: int) -> list[float]:
    """Read one typed block assuming the little endian the format promises.

    Args:
        marco: Encoded frame.
        offset: Where the block starts.
        typecode: ``struct`` type code of one item.
        longitud: Number of items.

    Returns:
        The items of the block.
    """
    return [
        float(valor)
        for valor in struct.unpack_from(f"<{longitud}{typecode}", marco, offset)
    ]


def _marco_de(
    n_fechas: int, n_series: int, valores: Sequence[float | None] | None = None
) -> bytes:
    """Encode a frame of the given shape with filler content.

    Args:
        n_fechas: Number of dates.
        n_series: Number of lines.
        valores: Values to encode; filler when omitted.

    Returns:
        The encoded frame.
    """
    return encode_frame(
        CABECERA_MINIMA,
        list(range(n_fechas)),
        list(range(n_series)),
        list(valores) if valores is not None else [1.0] * (n_fechas * n_series),
    )


@pytest.mark.parametrize(
    ("n_fechas", "n_series"),
    [(1, 1), (2, 1), (3, 2), (5, 3), (7, 7), (2000, 250)],
)
def test_offsets_are_aligned_to_eight_bytes(n_fechas: int, n_series: int) -> None:
    """Every block starts on an eight byte boundary, whatever the cardinalities.

    The defect this catches is a field added to the header that leaves the value
    block on an offset that is not a multiple of four. Python would not notice:
    ``new Float32Array(buffer, offset, n)`` throws ``RangeError`` in the browser,
    and only for some shapes, which is how a bug like this reaches production
    through a green suite.

    Args:
        n_fechas: Number of dates of the frame under test.
        n_series: Number of lines of the frame under test.
    """
    marco = _marco_de(n_fechas, n_series)
    offsets = _offsets(marco)

    for nombre in ("fechas", "series", "valores", "total"):
        assert offsets[nombre] % FRAME_ALIGNMENT == 0, nombre
    assert offsets["total"] == len(marco)
    assert _bloque(marco, offsets["fechas"], "i", n_fechas) == list(range(n_fechas))
    assert _bloque(marco, offsets["series"], "H", n_series) == list(range(n_series))


def test_frame_matches_the_golden_witness() -> None:
    """The committed witness is exactly what the encoder produces today.

    A field reordered, a type widened or a byte order flipped changes these
    bytes. Without the witness the change is invisible from Python, which keeps
    encoding and decoding against itself, and the one that breaks is the
    browser.
    """
    commiteado = BASE64_PATH.read_text(encoding="utf-8").strip()

    assert base64.b64decode(commiteado) == golden_frame()
    assert commiteado + "\n" == golden_base64()
    assert "\n" not in commiteado


def test_golden_witness_is_up_to_date() -> None:
    """Nobody changed the encoder and left the witness behind.

    The frontend suite reads the committed file. A stale witness would let the
    two sides of the format diverge with both suites green, which is the one
    failure mode a shared fixture exists to prevent.
    """
    rancios = [ruta.name for ruta in stale_files()]

    assert not rancios, (
        f"regenera con: poetry -P backend run python "
        f"scripts/generar_marco_dorado.py ({', '.join(rancios)})"
    )


def test_the_golden_witness_carries_the_frame_it_declares() -> None:
    """The witness content matches its own companion, block by block.

    The companion is what the TypeScript decoder asserts against. If it drifted
    from the base64 line -a value edited by hand, a date list left stale- the
    frontend suite would be pinned to a frame that does not exist, and the two
    files that are supposed to be one witness would be two.
    """
    companero = json.loads(COMPANION_PATH.read_text(encoding="utf-8"))
    marco = golden_frame()
    offsets = _offsets(marco)

    assert companero["bytes"] == len(marco)
    assert companero["cabecera"] == _cabecera(marco)
    assert companero["fechas"] == _bloque(marco, offsets["fechas"], "i", 3)
    assert companero["series_id"] == _bloque(marco, offsets["series"], "H", 2)
    leidos = _bloque(marco, offsets["valores"], "f", len(GOLDEN_VALUES))
    esperados = [math.nan if valor is None else valor for valor in companero["valores"]]
    for leido, esperado in zip(leidos, esperados, strict=True):
        assert (math.isnan(leido) and math.isnan(esperado)) or leido == esperado


def test_value_count_mismatch_is_rejected() -> None:
    """A frame whose value count contradicts its cardinalities never ships.

    This is the quiet corruption: a filter that leaves 249 series and a value
    vector sized for 250 would make the decoder read every line after the first
    one shifted, and the chart would show another series' data with a perfectly
    credible shape.
    """
    with pytest.raises(ValueError, match="3 series of 2 dates"):
        encode_frame(CABECERA_MINIMA, [0, 1], [0, 1, 2], [1.0] * 5)


def test_the_caller_cannot_publish_its_own_offsets() -> None:
    """Only the encoder writes the offsets, because only it does the padding.

    A service that computed them itself would be a second implementation of the
    padding arithmetic, and the day the two disagree the header would describe a
    frame the browser does not have.
    """
    with pytest.raises(ValueError, match="offsets"):
        encode_frame({"offsets": {"fechas": 0}}, [0], [0], [1.0])


def test_float32_roundtrip_stays_within_declared_error() -> None:
    """Values arrive as float32 within the error the interface declares.

    Writing float64 into a float32 hole -or the reverse- turns half the numbers
    into garbage. And the declared error is not decoration: it is the sentence
    the provenance card of the screen shows, so it has to be a measured bound.
    """
    originales: list[float | None] = [
        1234567.89,
        0.1,
        None,
        -2.5,
        1e-08,
        987654321.0,
        0.0,
    ]
    marco = encode_frame(CABECERA_MINIMA, [0], list(range(7)), originales)

    leidos = _bloque(marco, _offsets(marco)["valores"], "f", 7)

    assert math.isnan(leidos[2])
    for leido, original in zip(leidos, originales, strict=True):
        if original is None:
            continue
        assert not math.isnan(leido)
        if original == 0.0:
            assert leido == 0.0
            continue
        assert abs(leido - original) / abs(original) <= ERROR_DECLARADO


def test_encoder_declares_little_endian(monkeypatch: pytest.MonkeyPatch) -> None:
    """On a big endian host the typed blocks are swapped and the prefix is not.

    The branch exists and no machine of this team exercises it, so it is
    exercised here. Deleting the swap would ship a frame whose numbers every
    browser reads backwards, and no test would notice.

    Args:
        monkeypatch: Used to pretend the interpreter runs on a big endian host.
    """
    fechas = [17835, 17836]
    monkeypatch.setattr(serie_frame, "NATIVE_BYTEORDER", "big")

    marco = encode_frame(CABECERA_MINIMA, fechas, [7], [1.0, 2.0])
    offsets = _offsets(marco)

    # The prefix is packed with an explicit "<" and never swapped: the reader
    # has to be able to find the header before it knows anything else.
    version, _, n_fechas, n_series = _prefijo(marco)
    assert (version, n_fechas, n_series) == (FRAME_VERSION, 2, 1)
    assert list(struct.unpack_from(">2i", marco, offsets["fechas"])) == fechas
    assert struct.unpack_from(">H", marco, offsets["series"])[0] == 7
