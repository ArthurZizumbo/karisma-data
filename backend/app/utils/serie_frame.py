"""Binary column frame used to ship the dashboard series to the browser.

The frame exists because JSON is the bottleneck, not the network: a columnar
payload maps straight onto a ``Float32Array`` view, so the browser never parses
half a million numbers. The layout is documented in
``docs/us-planning/us-025.md`` section 2.5 and reproduced here because a wire
format that lives only in a planning document drifts::

    offset  0 : magic        4 B      "KSER"
    offset  4 : version      uint16 = 1
    offset  6 : reserved     uint16 = 0
    offset  8 : header_len   uint32   bytes of the UTF-8 header JSON
    offset 12 : n_fechas     uint32
    offset 16 : n_series     uint32
    offset 20 : reserved     uint32 = 0
    offset 24 : header JSON, zero padded up to a multiple of eight
        ...   : fechas    int32  [n_fechas]            days since the epoch
        ...   : series_id uint16 [n_series]            65535 marks an aggregate
        ...   : valores   float32[n_series * n_fechas] row major, series major

Three properties are load bearing and none of them is left to chance:

1. Everything is little endian, on every machine. The prefix is packed with an
   explicit ``<`` and the typed blocks are byte swapped when the interpreter
   runs on a big endian platform. A browser reading a typed array assumes the
   native order of its host, and every host that runs one is little endian.
2. Every block starts at a multiple of ``FRAME_ALIGNMENT``. ``new
   Float32Array(buffer, offset, n)`` throws ``RangeError`` when the offset is
   not a multiple of four, and the failure appears only for some cardinalities,
   which is the worst kind of defect to find from a screenshot.
3. The offsets are computed once, here, and published inside the header. The
   decoder reads them instead of recomputing the padding arithmetic, so the two
   sides of the format cannot disagree about where a block begins.

A missing value travels as ``NaN``, never as a zero: a zero drawn on a chart is
a claim, and the gap is the truth. The JSON variant of the endpoint carries the
same absence as ``null``.
"""

import json
import struct
import sys
from array import array
from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass
from math import nan
from typing import Any, Final

FRAME_MAGIC: Final[bytes] = b"KSER"
FRAME_VERSION: Final[int] = 1
FRAME_MEDIA_TYPE: Final[str] = "application/vnd.karisma.serie-v1"
FRAME_PREFIX_BYTES: Final[int] = 24
FRAME_ALIGNMENT: Final[int] = 8

# Identifier of a line that is not one of the 250 keys of the grid but the
# aggregate of several of them. It is the largest uint16 on purpose: no real
# key can ever collide with it.
AGGREGATE_SERIES_ID: Final[int] = 0xFFFF

# Key the encoder writes into the header. A caller that supplies it would be
# publishing offsets nobody verified.
OFFSETS_KEY: Final[str] = "offsets"

# Item size of every typed block, in bytes. They are asserted against the
# ``array`` module instead of trusted: the C ``int`` behind the ``i`` type code
# is four bytes on every platform this runs on, and the guard is what turns a
# hypothetical platform where it is not into an error instead of a corrupt
# frame.
DATE_ITEM_BYTES: Final[int] = 4
SERIES_ITEM_BYTES: Final[int] = 2
VALUE_ITEM_BYTES: Final[int] = 4

# Byte order of the running interpreter, read as a module attribute so that the
# byte swapping branch can be exercised on a little endian machine, which is
# every machine this project runs on.
NATIVE_BYTEORDER: str = sys.byteorder

# Passes allowed while the header length settles. Publishing the offsets inside
# the header makes its length depend on itself; the fixed point is reached in
# two passes because the offsets only grow, and their decimal width grows far
# more slowly than the header.
_MAX_HEADER_PASSES: Final[int] = 4

_PREFIX_FORMAT: Final[str] = "<HHIII"
_UNSETTLED_HEADER: Final[str] = (
    "the header length did not settle: its offsets would not match the frame"
)
_ZERO_OFFSETS: Final[Mapping[str, int]] = {
    "fechas": 0,
    "series": 0,
    "valores": 0,
    "total": 0,
}


@dataclass(frozen=True)
class FrameOffsets:
    """Byte offset of every block. Published inside the header, never guessed.

    Attributes:
        fechas: Where the ``int32`` block of dates begins.
        series: Where the ``uint16`` block of identifiers begins.
        valores: Where the ``float32`` block of values begins.
        total: Length of the whole frame, padding included. A shorter body is a
            truncated download, which is the cheapest check the decoder has.
    """

    fechas: int
    series: int
    valores: int
    total: int


def align_up(offset: int) -> int:
    """Round an offset up to the next multiple of ``FRAME_ALIGNMENT``.

    Args:
        offset: Position in bytes from the start of the frame.

    Returns:
        The first aligned position at or after ``offset``.
    """
    remainder = offset % FRAME_ALIGNMENT
    return offset if remainder == 0 else offset + FRAME_ALIGNMENT - remainder


def frame_offsets(header_len: int, n_fechas: int, n_series: int) -> FrameOffsets:
    """Return the aligned offsets of a frame with the given cardinalities.

    Args:
        header_len: Length in bytes of the UTF-8 header JSON, padding excluded.
        n_fechas: Number of dates shared by every line.
        n_series: Number of lines.

    Returns:
        The offset of the three blocks and the total length of the frame.
    """
    fechas = align_up(FRAME_PREFIX_BYTES + header_len)
    series = align_up(fechas + n_fechas * DATE_ITEM_BYTES)
    valores = align_up(series + n_series * SERIES_ITEM_BYTES)
    total = align_up(valores + n_series * n_fechas * VALUE_ITEM_BYTES)
    return FrameOffsets(fechas=fechas, series=series, valores=valores, total=total)


def encode_frame(
    header: Mapping[str, Any],
    fechas: Sequence[int],
    series_id: Sequence[int],
    valores: Sequence[float | None],
) -> bytes:
    """Encode one frame, little endian, every block aligned to eight bytes.

    Args:
        header: Metadata written as UTF-8 JSON with sorted keys. ``offsets`` is
            added here and must not be supplied by the caller.
        fechas: Days since the Unix epoch, ascending.
        series_id: Identifier of every line; ``AGGREGATE_SERIES_ID`` marks an
            aggregate.
        valores: ``len(series_id) * len(fechas)`` values, row major by series.
            ``None`` travels as ``NaN`` and the browser draws a gap.

    Returns:
        The complete frame.

    Raises:
        ValueError: When the caller supplies ``offsets``, or when the value
            count does not match the two cardinalities.
    """
    if OFFSETS_KEY in header:
        message = "the caller must not supply the offsets: the encoder owns them"
        raise ValueError(message)

    n_fechas = len(fechas)
    n_series = len(series_id)
    expected = n_fechas * n_series
    if len(valores) != expected:
        message = (
            f"the frame declares {n_series} series of {n_fechas} dates, which is "
            f"{expected} values, and {len(valores)} were given"
        )
        raise ValueError(message)

    payload, offsets = _settle_header(dict(header), n_fechas, n_series)

    frame = bytearray(offsets.total)
    frame[0 : len(FRAME_MAGIC)] = FRAME_MAGIC
    struct.pack_into(
        _PREFIX_FORMAT,
        frame,
        len(FRAME_MAGIC),
        FRAME_VERSION,
        0,
        len(payload),
        n_fechas,
        n_series,
    )
    frame[FRAME_PREFIX_BYTES : FRAME_PREFIX_BYTES + len(payload)] = payload

    for offset, block in (
        (offsets.fechas, _packed("i", DATE_ITEM_BYTES, fechas)),
        (offsets.series, _packed("H", SERIES_ITEM_BYTES, series_id)),
        (
            offsets.valores,
            _packed(
                "f",
                VALUE_ITEM_BYTES,
                [nan if value is None else value for value in valores],
            ),
        ),
    ):
        frame[offset : offset + len(block)] = block

    return bytes(frame)


def _settle_header(
    header: dict[str, Any], n_fechas: int, n_series: int
) -> tuple[bytes, FrameOffsets]:
    """Serialize the header with offsets that describe the frame it produces.

    The header publishes the offsets, and the offsets depend on the length of
    the header, so the two are settled by iteration instead of by a formula
    nobody could read.

    Args:
        header: Metadata supplied by the caller, without ``offsets``.
        n_fechas: Number of dates.
        n_series: Number of lines.

    Returns:
        The encoded header and the offsets it publishes.

    Raises:
        ValueError: If the length does not settle, which would mean the frame
            declares offsets that do not describe itself.
    """
    header[OFFSETS_KEY] = dict(_ZERO_OFFSETS)
    payload = _dump(header)
    for _ in range(_MAX_HEADER_PASSES):
        offsets = frame_offsets(len(payload), n_fechas, n_series)
        header[OFFSETS_KEY] = asdict(offsets)
        settled = _dump(header)
        if len(settled) == len(payload):
            return settled, offsets
        payload = settled
    # Unreachable while the offsets keep growing monotonically, which they do:
    # it is the guard that turns a broken invariant into an error instead of a
    # frame whose header describes a different frame.
    raise ValueError(_UNSETTLED_HEADER)  # pragma: no cover


def _dump(header: Mapping[str, Any]) -> bytes:
    """Serialize the header canonically.

    Keys are sorted and the separators are compact so that two equal headers
    always produce the same bytes: the ETag of the endpoint and the golden
    witness of the test suite both depend on that.

    Args:
        header: Metadata to serialize.

    Returns:
        The UTF-8 JSON, without a trailing newline.
    """
    return json.dumps(
        header, ensure_ascii=False, separators=(",", ":"), sort_keys=True
    ).encode("utf-8")


def _packed(typecode: str, item_bytes: int, values: Sequence[Any]) -> bytes:
    """Pack a typed block, little endian whatever the host does.

    Args:
        typecode: ``array`` type code of the block.
        item_bytes: Width the format demands for one item.
        values: Items of the block.

    Returns:
        The bytes of the block.

    Raises:
        ValueError: When the interpreter gives that type code another width, in
            which case writing the block would silently corrupt the frame.
    """
    block = array(typecode, values)
    if block.itemsize != item_bytes:  # pragma: no cover - platform guard
        message = (
            f"this interpreter stores '{typecode}' in {block.itemsize} bytes and "
            f"the frame declares {item_bytes}"
        )
        raise ValueError(message)
    if NATIVE_BYTEORDER != "little":
        block.byteswap()
    return block.tobytes()
