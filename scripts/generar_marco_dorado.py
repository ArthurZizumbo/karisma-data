"""Regenerate the golden witness of the KSER1 frame, shared by two suites.

The witness is the only thing that keeps the Python encoder and the TypeScript
decoder from drifting apart. Python encoding and decoding against itself proves
nothing about the browser: a field reordered, a block written as ``float64`` in
a ``float32`` hole or a missing byte swap would keep the backend suite green and
break the chart. Both suites read *these* bytes, so a change to the format turns
one of them red the same day.

The witness is written as text on purpose. ``*.parquet`` and loose binaries are
excluded from review by the repository ignore rules and by human patience: a
base64 line and its JSON companion are diffable, and the diff of a format change
is meant to be loud.

Usage::

    poetry -P backend run python scripts/generar_marco_dorado.py
    poetry -P backend run python scripts/generar_marco_dorado.py --verificar

The frame is tiny and its cardinalities are chosen so that the three blocks all
need padding: with three dates and two series, the date block ends at a multiple
of four that is not a multiple of eight and the identifier block ends four bytes
short of the alignment. A witness whose blocks happened to be aligned already
would pass with the padding arithmetic deleted.
"""

import argparse
import base64
import json
import sys
from array import array
from datetime import date
from hashlib import sha256
from pathlib import Path
from typing import Any, Final

from app.utils.serie_frame import (
    AGGREGATE_SERIES_ID,
    FRAME_MEDIA_TYPE,
    FRAME_VERSION,
    encode_frame,
)

REPO_ROOT: Final[Path] = Path(__file__).resolve().parents[1]
FIXTURES_DIR: Final[Path] = REPO_ROOT / "tests" / "fixtures"
BASE64_PATH: Final[Path] = FIXTURES_DIR / "serie_frame_golden.b64"
COMPANION_PATH: Final[Path] = FIXTURES_DIR / "serie_frame_golden.json"

EXIT_OK: Final[int] = 0
EXIT_STALE: Final[int] = 1

EPOCH: Final[date] = date(1970, 1, 1)

# First three business days of the window US-006 froze. Real dates and not
# round numbers, so that a decoder that forgets the epoch produces something
# visibly wrong instead of something plausible.
GOLDEN_DATES: Final[tuple[date, ...]] = (
    date(2018, 10, 31),
    date(2018, 11, 1),
    date(2018, 11, 2),
)

# One aggregate line and one real key of the grid, which is exactly the mix the
# endpoint serves: a decoder that treats the identifier block as signed would
# read the aggregate as -1.
GOLDEN_SERIES_ID: Final[tuple[int, ...]] = (AGGREGATE_SERIES_ID, 7)

# Six values, row major by series. The first is not representable in float32 and
# pins the rounding; ``None`` is the gap of a ratio with no balance behind it;
# the small and the large one bracket the range the dashboard actually shows.
GOLDEN_VALUES: Final[tuple[float | None, ...]] = (
    1234567.89,
    0.1,
    None,
    -2.5,
    1e-08,
    987654321.0,
)


def _days_since_epoch(value: date) -> int:
    """Return the number of days between the Unix epoch and a date.

    Args:
        value: Calendar date, always UTC in this format.

    Returns:
        The offset in days, negative before 1970.
    """
    return (value - EPOCH).days


def golden_header() -> dict[str, Any]:
    """Return the header of the witness, shaped like the one the endpoint emits.

    The values are literal instead of imported from the service on purpose. What
    the witness pins is the framing -prefix, padding, block order, endianness-
    and not the metadata the endpoint chooses to publish, which grows with every
    User Story. Coupling them would turn every new header field into a false
    alarm in the frontend suite.

    Returns:
        The header, without ``offsets``: the encoder owns that key.
    """
    return {
        "metrica": "saldo_disponible_mxn",
        "agrupacion": "unidad_negocio",
        "unidad": "MXN",
        "fecha_min": GOLDEN_DATES[0].isoformat(),
        "fecha_max": GOLDEN_DATES[-1].isoformat(),
        "orden": ["serie", "fecha"],
        "conteo": {
            "puntos": len(GOLDEN_VALUES),
            "fechas": len(GOLDEN_DATES),
            "series": len(GOLDEN_SERIES_ID),
        },
        "reduccion": {
            "metodo": "media_por_bloque",
            "bloque": 1,
            "puntos_originales": len(GOLDEN_DATES),
        },
        "origen": {
            "silo": "liquidez",
            "archivo": "data/aggregates/serie_tablero.parquet",
            "filas_agregadas": 500000,
            "filas_crudas": 1000000,
            "generado_por": "make data",
            "semilla": 20260720,
            "transformaciones": ["testigo dorado: sin transformaciones reales"],
            "nota_tipo_cambio_es": (
                "Tipo de cambio sintetico fijo. No es una cotizacion de mercado."
            ),
            "nota_tipo_cambio_en": "Fixed synthetic exchange rate. Not a market quote.",
        },
        "catalogo": [
            {
                "clave": "TESORERIA",
                "serie_id": None,
                "label_es": "Tesoreria",
                "label_en": "Treasury",
            },
            {
                "clave": "7",
                "serie_id": 7,
                "label_es": "Tesoreria · Peso mexicano · Un mes",
                "label_en": "Treasury · Mexican peso · One month",
            },
        ],
    }


def golden_frame() -> bytes:
    """Encode the witness.

    Returns:
        The frame, byte for byte identical on every platform.
    """
    return encode_frame(
        golden_header(),
        [_days_since_epoch(value) for value in GOLDEN_DATES],
        GOLDEN_SERIES_ID,
        GOLDEN_VALUES,
    )


def golden_base64() -> str:
    """Return the witness as one base64 line, terminated by a newline.

    One line and not wrapped columns: the decoder of the frontend calls ``atob``
    on the trimmed text, and a wrapped file would need a rule that strips
    whitespace on both sides of the format. The frame is small enough that the
    line stays readable in a diff.

    Returns:
        The encoded frame plus its trailing newline.
    """
    return base64.b64encode(golden_frame()).decode("ascii") + "\n"


def golden_companion() -> dict[str, Any]:
    """Return the JSON companion: what a correct decoder must find inside.

    The float32 column is the point of the file. It carries the values *after*
    the narrowing, so a decoder can compare for exact equality instead of
    inventing a tolerance, and so the precision the interface declares is a
    number somebody can read rather than a claim.

    Returns:
        The companion document, ready to be serialized.
    """
    frame = golden_frame()
    narrowed = array("f", [0.0 if value is None else value for value in GOLDEN_VALUES])
    return {
        "descripcion": (
            "Testigo dorado del marco binario KSER1. Lo escribe US-025 con "
            "scripts/generar_marco_dorado.py y lo leen las dos suites: "
            "tests/backend/test_serie_frame.py y frontend/test/serieBinaria.spec.ts."
        ),
        "generado_por": "scripts/generar_marco_dorado.py",
        "formato": "KSER1",
        "version": FRAME_VERSION,
        "tipo_de_contenido": FRAME_MEDIA_TYPE,
        "nota_base64": (
            "serie_frame_golden.b64 es UNA sola linea de base64 con salto final. "
            "Decodificar con atob(texto.trim()) en el navegador."
        ),
        "nota_valores": (
            "valores son los numeros ya estrechados a float32, comparables por "
            "igualdad exacta; null es NaN, el hueco que se dibuja sin punto. "
            "valores_originales son los float64 que entraron al codificador."
        ),
        "bytes": len(frame),
        "sha256": sha256(frame).hexdigest(),
        "cabecera": _decoded_header(frame),
        "fechas": [_days_since_epoch(value) for value in GOLDEN_DATES],
        "fechas_iso": [value.isoformat() for value in GOLDEN_DATES],
        "series_id": list(GOLDEN_SERIES_ID),
        "valores": [
            None if original is None else narrowed[index]
            for index, original in enumerate(GOLDEN_VALUES)
        ],
        "valores_originales": list(GOLDEN_VALUES),
    }


def _decoded_header(frame: bytes) -> dict[str, Any]:
    """Read the header back out of an encoded frame.

    Reading it back instead of rebuilding it is what puts the offsets the
    encoder computed into the companion, which is what the decoder of the
    frontend is expected to trust.

    Args:
        frame: Encoded frame.

    Returns:
        The header as JSON.
    """
    header_len = int.from_bytes(frame[8:12], "little")
    payload: dict[str, Any] = json.loads(frame[24 : 24 + header_len].decode("utf-8"))
    return payload


def write_golden() -> None:
    """Write both witness files, creating the fixtures directory if needed."""
    FIXTURES_DIR.mkdir(parents=True, exist_ok=True)
    BASE64_PATH.write_text(golden_base64(), encoding="utf-8", newline="\n")
    COMPANION_PATH.write_text(
        json.dumps(golden_companion(), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def stale_files() -> list[Path]:
    """List the witness files that no longer match what the encoder produces.

    Returns:
        The paths that are missing or out of date, empty when both are current.
    """
    expected = {
        BASE64_PATH: golden_base64(),
        COMPANION_PATH: json.dumps(golden_companion(), ensure_ascii=False, indent=2)
        + "\n",
    }
    return [
        path
        for path, content in expected.items()
        if not path.is_file()
        or path.read_text(encoding="utf-8").replace("\r\n", "\n") != content
    ]


def main(argv: list[str] | None = None) -> int:
    """Regenerate the witness, or report that it is stale.

    Args:
        argv: Command line arguments, defaulting to the process ones.

    Returns:
        The exit status: zero when the files are current or were rewritten.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--verificar",
        action="store_true",
        help="no escribe: sale distinto de cero si el testigo esta rancio",
    )
    arguments = parser.parse_args(argv)

    stale = stale_files()
    if arguments.verificar:
        for path in stale:
            print(f"rancio: {path.relative_to(REPO_ROOT).as_posix()}")
        if stale:
            return EXIT_STALE
        print("el testigo dorado coincide con el codificador")
        return EXIT_OK

    write_golden()
    for path in (BASE64_PATH, COMPANION_PATH):
        print(f"escrito: {path.relative_to(REPO_ROOT).as_posix()}")
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
