"""Reads, filters, aggregates and reduces the preaggregated dashboard series.

The whole pipeline runs on a Polars ``LazyFrame`` so that projection and
predicates reach the parquet reader: the endpoint never materialises the million
raw rows of the silo, and it materialises the 500 000 aggregated ones only when
the caller asked for the full evidence load.

There are two reductions and they are not the same operation, which is the one
thing to get right in this module:

* **Across lines.** When 250 keys of the grid collapse into five business units,
  the balance and the position count are summed, and ``ratio_lcr`` is
  reweighted by balance. It is already a weighted mean inside each cell, so
  averaging it again without weights produces a number that is simply wrong and
  that looks entirely plausible on a chart.
* **Along time.** When 2 000 business days become ``max_puntos``, every block is
  averaged. Blocks are cut by position and not by calendar, because the series
  has no weekends: a calendar window would leave the last bucket holding a
  single day. The label of a block is its FIRST date; using the last one shifts
  the whole series k days to the right without raising anything.

Both reductions run over the same pair of columns, a numerator and a
denominator, so there is one code path and not two. With a zero denominator the
point is null and never zero: a zero drawn on a chart is a claim, and the gap is
the truth.

Nothing Polars leaves this module. The router receives a ``SeriesPayload`` of
bytes and cardinalities, which is what keeps the analytical engine out of the
HTTP layer.
"""

import json
import time
from collections import OrderedDict
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import date
from hashlib import sha256
from math import ceil
from pathlib import Path
from threading import Lock
from typing import Any, Final

import polars as pl
import structlog

from app.models.series import (
    MAX_JSON_POINTS,
    Conteo,
    Grouping,
    MetricName,
    OrigenSerie,
    Reduccion,
    ReductionMethod,
    ResponseFormat,
    SerieEtiqueta,
    SeriesJson,
    SeriesParams,
)
from app.utils.serie_frame import (
    AGGREGATE_SERIES_ID,
    FRAME_MEDIA_TYPE,
    encode_frame,
)

logger = structlog.get_logger()

AGGREGATES_DIRNAME: Final[str] = "aggregates"
AGGREGATE_FILENAME: Final[str] = "serie_tablero.parquet"
SIDECAR_FILENAME: Final[str] = "serie_tablero_meta.json"
MANIFEST_RELATIVE: Final[tuple[str, str]] = ("silos", "manifest.json")

JSON_MEDIA_TYPE: Final[str] = "application/json"

# Silo the aggregate comes from, per the contract of US-006.
SOURCE_SILO: Final[str] = "liquidez"
GENERATED_BY: Final[str] = "make data"

# Separator US-006 uses to join the three parts of a series label. Splitting on
# it is how a dimension label -"Tesoreria"- is recovered from the composite one.
LABEL_SEPARATOR: Final[str] = " · "
LABEL_PARTS: Final[int] = 3

# Steps US-006 applied before this endpoint saw a single row. They are repeated
# to the reader instead of hidden, and they move the day that generator moves.
UPSTREAM_TRANSFORMATIONS: Final[tuple[str, ...]] = (
    "filtro fec_pos dentro de los 2000 dias habiles publicados",
    "filtro mto_disp >= 0",
    "filtro ratio_lcr en [0, 3]",
    "group_by(fec_pos, unidad_negocio, divisa, bucket_venc)",
    "saldo_disponible_mxn = sum(mto_disp) * 1000 * fx[divisa]",
    "ratio_lcr = sum(ratio_lcr * mto_disp) / sum(mto_disp)",
)

# Frames kept encoded in memory. Eight full loads are about 16 MB, which fits
# in the 512 MiB of the service and is what makes the fluidity script measure
# painting instead of disk.
CACHE_ENTRIES: Final[int] = 8

# Hex characters of the ETag. Sixty four bits of a SHA-256 is far more than a
# cache validator needs and keeps the header short.
ETAG_HEX: Final[int] = 16

# Column the filter dimensions map to. ``serie`` groups by the key itself.
_KEY_COLUMN: Final[Mapping[Grouping, str]] = {
    Grouping.BUSINESS_UNIT: "unidad_negocio",
    Grouping.CURRENCY: "divisa",
    Grouping.MATURITY: "bucket_venc",
    Grouping.SERIES: "serie_id",
}

_KEY = "clave"
_NUM = "__numerador"
_DEN = "__denominador"
_DATE = "fecha"
_BLOCK_DATE = "__fecha_bloque"
_POSITION = "__posicion"
_VALUE = "valor"

_EPOCH: Final[date] = date(1970, 1, 1)


class SeedMissingError(RuntimeError):
    """Raised when the aggregate written by ``make data`` is not on disk.

    A fresh clone has no ``data/`` directory: it is not versioned. The screen
    has a designed empty state for exactly this, so the failure has to be a
    typed answer and never a stack trace.
    """

    def __init__(self, path: Path) -> None:
        """Record which file the caller would have to seed.

        Args:
            path: Absolute path of the missing aggregate.
        """
        super().__init__(f"falta el agregado {path}")
        self.path = path


class PayloadTooLargeError(RuntimeError):
    """Raised when the readable variant is asked for more points than it holds.

    Attributes:
        puntos: Points the query would have produced.
        maximo: Ceiling of the JSON variant.
    """

    def __init__(self, puntos: int, maximo: int) -> None:
        """Record the two figures the client needs to narrow its query.

        Args:
            puntos: Points the query would have produced.
            maximo: Ceiling of the JSON variant.
        """
        super().__init__(f"{puntos} puntos superan el tope de {maximo} en JSON")
        self.puntos = puntos
        self.maximo = maximo


@dataclass(frozen=True)
class SeriesResult:
    """Everything the router needs; no Polars type escapes this module.

    Attributes:
        fechas: Dates shared by every line, ascending.
        series: One label per line, in the order of ``valores``.
        valores: ``len(series) * len(fechas)`` values, row major by series.
        conteo: Cardinalities of the answer.
        reduccion: What was done to the time axis.
        origen: Provenance of the numbers.
        etag: Validator of this representation.
    """

    fechas: tuple[date, ...]
    series: tuple[SerieEtiqueta, ...]
    valores: tuple[float | None, ...]
    conteo: Conteo
    reduccion: Reduccion
    origen: OrigenSerie
    etag: str


@dataclass(frozen=True)
class SeriesPayload:
    """An encoded answer, ready to be written to the wire.

    Attributes:
        body: Bytes of the representation.
        media_type: Content type that describes them.
        etag: Validator of this representation.
        conteo: Cardinalities, published as a header.
    """

    body: bytes
    media_type: str
    etag: str
    conteo: Conteo


def aggregate_path(data_dir: Path) -> Path:
    """Return the path of the preaggregated series.

    Args:
        data_dir: Root of the data directory.

    Returns:
        Path of the parquet US-006 writes.
    """
    return data_dir / AGGREGATES_DIRNAME / AGGREGATE_FILENAME


def build_payload(params: SeriesParams, *, data_dir: Path) -> SeriesPayload:
    """Return the encoded answer of a query, from cache when possible.

    The cache is keyed on the canonical query and on the size and modification
    time of the parquet, so regenerating the data with ``make data`` invalidates
    every entry in the same second without anybody having to remember.

    Args:
        params: Validated query.
        data_dir: Root of the data directory.

    Returns:
        The bytes, their content type, the validator and the cardinalities.

    Raises:
        SeedMissingError: When the aggregate is absent.
        PayloadTooLargeError: When the JSON variant would exceed its ceiling.
    """
    path = aggregate_path(data_dir)
    if not path.is_file():
        raise SeedMissingError(path)

    stat = path.stat()
    cache_key = (params.cache_key(), str(path), stat.st_size, stat.st_mtime_ns)
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached

    started = time.perf_counter()
    result = load_series(params, data_dir=data_dir)
    if params.formato is ResponseFormat.JSON and result.conteo.puntos > MAX_JSON_POINTS:
        raise PayloadTooLargeError(result.conteo.puntos, MAX_JSON_POINTS)

    if params.formato is ResponseFormat.JSON:
        body = _json_body(result, params)
        media_type = JSON_MEDIA_TYPE
    else:
        body = encode_result(result, params)
        media_type = FRAME_MEDIA_TYPE

    payload = SeriesPayload(
        body=body, media_type=media_type, etag=result.etag, conteo=result.conteo
    )
    _cache_put(cache_key, payload)

    # The filters are the reader's question and never travel to the log as text.
    # What is recorded is the hash of the canonical query, which is enough to
    # tell repeated requests apart, plus the shape of the answer.
    #
    # This digest is deliberately unsalted, unlike the fingerprint of the
    # catalog search. Nothing here is free text: SeriesParams is a closed
    # vocabulary of enums, of identifiers bounded to the frozen grid and of
    # dates, so the whole input space is enumerable by anyone and a salt would
    # buy no secrecy at all -confirming a guess would reveal only which cell of
    # a public grid somebody charted. What the salt would cost is real: the same
    # query has to hash to the same value across restarts and across replicas
    # for the bytes and the ms of these records to be comparable cold against
    # warm.
    logger.info(
        "serie_servida",
        consulta_hash=sha256(params.cache_key().encode("utf-8")).hexdigest(),
        metrica=params.metrica.value,
        agrupacion=params.agrupacion.value,
        formato=params.formato.value,
        series=result.conteo.series,
        fechas=result.conteo.fechas,
        puntos=result.conteo.puntos,
        bloque=result.reduccion.bloque,
        bytes=len(body),
        ms=round((time.perf_counter() - started) * 1000, 1),
    )
    return payload


def etag_for(params: SeriesParams, *, data_dir: Path) -> str:
    """Return the validator of a query without reading a single row.

    The validator depends on the canonical query and on the identity of the
    parquet, so a conditional request can be answered with one ``stat`` call.
    That is the whole point of the cache: coming back to the dashboard must not
    move two megabytes, and must not run the aggregation either.

    Args:
        params: Validated query.
        data_dir: Root of the data directory.

    Returns:
        The value of the ``ETag`` header.

    Raises:
        SeedMissingError: When the aggregate is absent.
    """
    path = aggregate_path(data_dir)
    if not path.is_file():
        raise SeedMissingError(path)
    stat = path.stat()
    return _etag(params, stat.st_size, stat.st_mtime_ns)


def load_series(params: SeriesParams, *, data_dir: Path) -> SeriesResult:
    """Read, filter, aggregate and reduce the dashboard series.

    Args:
        params: Validated query.
        data_dir: Root of the data directory.

    Returns:
        The dense matrix of lines and dates, with its provenance.

    Raises:
        SeedMissingError: When the aggregate is absent.
    """
    path = aggregate_path(data_dir)
    if not path.is_file():
        raise SeedMissingError(path)

    sidecar = _read_json(path.with_name(SIDECAR_FILENAME))
    manifest = _read_json(data_dir.joinpath(*MANIFEST_RELATIVE))

    frame = _filtered(pl.scan_parquet(path), params)
    aggregated = _aggregate_lines(frame, params).collect()

    fechas = _dates_of(aggregated)
    reduced, reduccion = reduce_by_block(aggregated.lazy(), params.max_puntos, fechas)
    fechas_salida = _block_labels(fechas, reduccion.bloque)

    claves = _keys_frame(aggregated)
    valores = _dense_values(reduced, claves, fechas_salida)
    series = _labels(claves.get_column(_KEY).to_list(), params.agrupacion, sidecar)

    conteo = Conteo(puntos=len(valores), fechas=len(fechas_salida), series=len(series))
    stat = path.stat()
    return SeriesResult(
        fechas=fechas_salida,
        series=series,
        valores=valores,
        conteo=conteo,
        reduccion=reduccion,
        origen=_origin(params, sidecar, manifest, reduccion),
        etag=_etag(params, stat.st_size, stat.st_mtime_ns),
    )


def reduce_by_block(
    frame: pl.LazyFrame, max_points: int, fechas: Sequence[date]
) -> tuple[pl.LazyFrame, Reduccion]:
    """Average every block of k business days, k = ceil(n_dates / max_points).

    The ceiling is not a detail. With a floor, 2 000 dates and 400 points give
    401 blocks and the last one holds a single day, so the last mark of the
    chart is noise shaped like a trend.

    Args:
        frame: Aggregated lines, one row per key and date, carrying the
            numerator and the denominator of the metric.
        max_points: Points per line the caller asked for.
        fechas: Ascending dates present in ``frame``.

    Returns:
        The reduced frame, labelled by the first date of each block, and the
        description of what was done.
    """
    total = len(fechas)
    block = max(1, ceil(total / max_points)) if total else 1
    reduccion = Reduccion(
        metodo=ReductionMethod.BLOCK_MEAN, bloque=block, puntos_originales=total
    )
    if block == 1:
        return frame.rename({_DATE: _BLOCK_DATE}), reduccion

    mapping = pl.DataFrame(
        {
            _DATE: list(fechas),
            _BLOCK_DATE: [fechas[(index // block) * block] for index in range(total)],
        },
        schema={_DATE: pl.Date, _BLOCK_DATE: pl.Date},
    )
    reduced = (
        frame.join(mapping.lazy(), on=_DATE, how="inner")
        .group_by(_KEY, _BLOCK_DATE)
        .agg(pl.col(_NUM).mean(), pl.col(_DEN).mean())
    )
    return reduced, reduccion


def encode_result(result: SeriesResult, params: SeriesParams) -> bytes:
    """Turn a result into the KSER1 frame.

    Args:
        result: Everything the answer carries.
        params: Query that produced it, echoed in the header.

    Returns:
        The complete frame.
    """
    header: dict[str, Any] = {
        "metrica": params.metrica.value,
        "agrupacion": params.agrupacion.value,
        "unidad": _unit_of(params.metrica),
        "fecha_min": result.fechas[0].isoformat() if result.fechas else None,
        "fecha_max": result.fechas[-1].isoformat() if result.fechas else None,
        "orden": ["serie", "fecha"],
        "conteo": result.conteo.model_dump(),
        "reduccion": result.reduccion.model_dump(mode="json"),
        "origen": result.origen.model_dump(mode="json"),
        "catalogo": [etiqueta.model_dump() for etiqueta in result.series],
    }
    return encode_frame(
        header,
        [(fecha - _EPOCH).days for fecha in result.fechas],
        [
            AGGREGATE_SERIES_ID if etiqueta.serie_id is None else etiqueta.serie_id
            for etiqueta in result.series
        ],
        result.valores,
    )


def clear_cache() -> None:
    """Empty the in-process cache of encoded frames.

    The cache is keyed on the size and the modification time of the parquet, so
    it invalidates itself in production. Tests that write a different aggregate
    to the same path within the same nanosecond do not get that for free.
    """
    with _CACHE_LOCK:
        _CACHE.clear()


def _unit_of(metric: MetricName) -> str:
    """Return the unit of a metric, as the axis of the chart labels it.

    Args:
        metric: Metric of the answer.

    Returns:
        A short unit code, not a sentence: the interface is bilingual.
    """
    return {
        MetricName.BALANCE: "MXN",
        MetricName.LCR: "ratio",
        MetricName.POSITIONS: "conteo",
    }[metric]


def _filtered(frame: pl.LazyFrame, params: SeriesParams) -> pl.LazyFrame:
    """Apply every filter before anything is aggregated.

    Filtering after the reduction would average blocks over lines the reader
    excluded, and no error would ever point at it.

    Args:
        frame: Lazy scan of the aggregate.
        params: Validated query.

    Returns:
        The filtered lazy frame.
    """
    for column, values in (
        ("unidad_negocio", params.unidad_negocio),
        ("divisa", params.divisa),
        ("bucket_venc", params.bucket_venc),
    ):
        if values:
            frame = frame.filter(pl.col(column).is_in(sorted(set(values))))
    if params.serie_id:
        frame = frame.filter(pl.col("serie_id").is_in(sorted(set(params.serie_id))))
    if params.desde is not None:
        frame = frame.filter(pl.col(_DATE) >= params.desde)
    if params.hasta is not None:
        frame = frame.filter(pl.col(_DATE) <= params.hasta)
    return frame


def _aggregate_lines(frame: pl.LazyFrame, params: SeriesParams) -> pl.LazyFrame:
    """Collapse the grid into one line per key of the grouping dimension.

    Both reductions of this module run over a numerator and a denominator. For
    balance and positions the denominator is one, so the average of the ratio is
    the average of the value; for ``ratio_lcr`` the denominator is the balance,
    which is what reweights a mean that was already weighted.

    Args:
        frame: Filtered lazy frame.
        params: Validated query.

    Returns:
        One row per key and date, with the numerator and the denominator.
    """
    grouped = frame.with_columns(pl.col(_KEY_COLUMN[params.agrupacion]).alias(_KEY))
    if params.metrica is MetricName.LCR:
        return grouped.group_by(_KEY, _DATE).agg(
            (pl.col("ratio_lcr") * pl.col("saldo_disponible_mxn")).sum().alias(_NUM),
            pl.col("saldo_disponible_mxn").sum().alias(_DEN),
        )
    return (
        grouped.group_by(_KEY, _DATE)
        .agg(pl.col(params.metrica.value).cast(pl.Float64).sum().alias(_NUM))
        .with_columns(pl.lit(1.0, dtype=pl.Float64).alias(_DEN))
    )


def _dates_of(frame: pl.DataFrame) -> tuple[date, ...]:
    """Return the ascending distinct dates of an aggregated frame.

    Args:
        frame: Collected aggregation.

    Returns:
        The dates, empty when the filters left nothing.
    """
    if frame.height == 0:
        return ()
    return tuple(frame.get_column(_DATE).unique().sort().to_list())


def _keys_frame(frame: pl.DataFrame) -> pl.DataFrame:
    """Return the keys of the answer in display order, with their position.

    Sorting on the native column is what keeps ``serie_id`` in numeric order: as
    text, key 100 would sit between 10 and 11. The dtype is carried along for
    the same reason the values are: a grid built from Python integers would join
    an ``Int64`` against the ``UInt16`` of the file.

    Args:
        frame: Collected aggregation.

    Returns:
        A frame with the key column and its display position.
    """
    return (
        frame.get_column(_KEY).unique().sort().to_frame(_KEY).with_row_index(_POSITION)
    )


def _block_labels(fechas: Sequence[date], block: int) -> tuple[date, ...]:
    """Return the label of every block: its first date.

    Args:
        fechas: Ascending dates before the reduction.
        block: Business days per block.

    Returns:
        One date per block.
    """
    return tuple(fechas[index] for index in range(0, len(fechas), block))


def _dense_values(
    frame: pl.LazyFrame, claves: pl.DataFrame, fechas: Sequence[date]
) -> tuple[float | None, ...]:
    """Lay the reduced lines out on the full grid, row major by series.

    The grid is built explicitly and joined instead of trusting that the source
    has a row for every pair. It does today -US-006 guarantees it- but a single
    missing cell would shift every value after it and draw a chart that lies
    without failing.

    Args:
        frame: Reduced lines.
        claves: Keys in display order, with their position.
        fechas: Block labels in ascending order.

    Returns:
        ``claves * fechas`` values, ``None`` where there is no cell.
    """
    if claves.height == 0 or not fechas:
        return ()

    grid = claves.join(
        pl.DataFrame({_BLOCK_DATE: list(fechas)}, schema={_BLOCK_DATE: pl.Date}),
        how="cross",
    )
    dense = (
        grid.lazy()
        .join(frame, on=[_KEY, _BLOCK_DATE], how="left")
        .with_columns(
            pl.when(pl.col(_DEN) != 0)
            .then(pl.col(_NUM) / pl.col(_DEN))
            .otherwise(None)
            .alias(_VALUE)
        )
        .sort(_POSITION, _BLOCK_DATE)
        .select(_VALUE)
        .collect()
    )
    return tuple(dense.get_column(_VALUE).to_list())


def _labels(
    claves: Sequence[object], grouping: Grouping, sidecar: Mapping[str, Any]
) -> tuple[SerieEtiqueta, ...]:
    """Name every line in both languages, reading the sidecar of US-006.

    Args:
        claves: Keys in display order.
        grouping: Dimension the keys belong to.
        sidecar: Parsed ``serie_tablero_meta.json``; empty when it is missing.

    Returns:
        One label per key.
    """
    catalogue = sidecar.get("catalogo", [])
    entries = catalogue if isinstance(catalogue, list) else []
    if grouping is Grouping.SERIES:
        by_id = {int(entry["serie_id"]): entry for entry in entries}
        return tuple(
            SerieEtiqueta(
                clave=str(clave),
                serie_id=int(str(clave)),
                label_es=str(
                    by_id.get(int(str(clave)), {}).get("label_es", str(clave))
                ),
                label_en=str(
                    by_id.get(int(str(clave)), {}).get("label_en", str(clave))
                ),
            )
            for clave in claves
        )

    dimension = _KEY_COLUMN[grouping]
    part = ("unidad_negocio", "divisa", "bucket_venc").index(dimension)
    by_code = _dimension_labels(entries, dimension, part)
    return tuple(
        SerieEtiqueta(
            clave=str(clave),
            serie_id=None,
            label_es=by_code.get(str(clave), (str(clave), str(clave)))[0],
            label_en=by_code.get(str(clave), (str(clave), str(clave)))[1],
        )
        for clave in claves
    )


def _dimension_labels(
    entries: Sequence[Any], dimension: str, part: int
) -> dict[str, tuple[str, str]]:
    """Recover the label of a dimension from the composite labels of US-006.

    The sidecar names a key of the grid as three parts joined by a separator, so
    the label of a business unit is the first part of any of its keys. When the
    split does not yield the three parts the code is used as its own label: a
    made up translation would be worse than an untranslated code.

    Args:
        entries: Catalogue of the sidecar.
        dimension: Column whose codes are being labelled.
        part: Index of the part that belongs to that dimension.

    Returns:
        The Spanish and English labels per code.
    """
    labels: dict[str, tuple[str, str]] = {}
    for entry in entries:
        if not isinstance(entry, dict) or dimension not in entry:
            continue
        code = str(entry[dimension])
        if code in labels:
            continue
        spanish = str(entry.get("label_es", "")).split(LABEL_SEPARATOR)
        english = str(entry.get("label_en", "")).split(LABEL_SEPARATOR)
        if len(spanish) != LABEL_PARTS or len(english) != LABEL_PARTS:
            labels[code] = (code, code)
            continue
        labels[code] = (spanish[part], english[part])
    return labels


def _origin(
    params: SeriesParams,
    sidecar: Mapping[str, Any],
    manifest: Mapping[str, Any],
    reduccion: Reduccion,
) -> OrigenSerie:
    """Assemble the provenance block US-029 renders verbatim.

    ``filas_crudas`` and ``semilla`` come from the manifest of the silos. Absent
    the manifest they stay null and the interface shows nothing: a provenance
    that invents a figure is worse than one that admits it does not have it.

    Args:
        params: Validated query.
        sidecar: Parsed sidecar of the aggregate.
        manifest: Parsed manifest of the silos.
        reduccion: What was done to the time axis.

    Returns:
        The provenance of every number of the answer.
    """
    silos = manifest.get("silos", [])
    raw_rows: int | None = None
    if isinstance(silos, list):
        for silo in silos:
            if isinstance(silo, dict) and silo.get("nombre") == SOURCE_SILO:
                raw_rows = int(silo.get("filas", 0)) or None
    seed = manifest.get("semilla")
    transformations = [
        *UPSTREAM_TRANSFORMATIONS,
        f"agregacion por {params.agrupacion.value}",
    ]
    if reduccion.bloque > 1:
        transformations.append(f"media por bloque de {reduccion.bloque} dias habiles")
    return OrigenSerie(
        silo=SOURCE_SILO,
        archivo=f"data/{AGGREGATES_DIRNAME}/{AGGREGATE_FILENAME}",
        filas_agregadas=int(sidecar.get("filas", 0)),
        filas_crudas=raw_rows,
        generado_por=GENERATED_BY,
        semilla=int(seed) if isinstance(seed, int) else None,
        transformaciones=tuple(transformations),
        nota_tipo_cambio_es=str(sidecar.get("tipo_cambio_nota_es", "")),
        nota_tipo_cambio_en=str(sidecar.get("tipo_cambio_nota_en", "")),
    )


def _json_body(result: SeriesResult, params: SeriesParams) -> bytes:
    """Serialise the exact, human readable variant of an answer.

    Args:
        result: Everything the answer carries.
        params: Query that produced it.

    Returns:
        The UTF-8 JSON body.
    """
    width = len(result.fechas)
    rows = tuple(
        tuple(result.valores[index * width : (index + 1) * width])
        for index in range(len(result.series))
    )
    document = SeriesJson(
        metrica=params.metrica,
        agrupacion=params.agrupacion,
        fechas=result.fechas,
        series=result.series,
        valores=rows,
        conteo=result.conteo,
        reduccion=result.reduccion,
        origen=result.origen,
    )
    return document.model_dump_json().encode("utf-8")


def _etag(params: SeriesParams, size: int, mtime_ns: int) -> str:
    """Build the weak validator of a representation.

    It is computed from the query and from the identity of the file, and never
    from the body: hashing two megabytes on every request would cost more than
    the reduction that produced them, and it would not detect a regenerated file
    that happens to be identical, which is precisely the case where reusing the
    cached frame is correct.

    Args:
        params: Validated query.
        size: Size of the parquet in bytes.
        mtime_ns: Modification time of the parquet in nanoseconds.

    Returns:
        The value of the ``ETag`` header, quotes included.
    """
    material = f"{size}:{mtime_ns}:{params.cache_key()}".encode()
    return f'W/"{sha256(material).hexdigest()[:ETAG_HEX]}"'


def _read_json(path: Path) -> dict[str, Any]:
    """Read a JSON document, tolerating its absence.

    Args:
        path: File to read.

    Returns:
        The parsed document, or an empty mapping when it is missing or invalid.
    """
    try:
        parsed = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        logger.warning("metadato_ausente", archivo=path.name)
        return {}
    return parsed if isinstance(parsed, dict) else {}


_CacheKey = tuple[str, str, int, int]
_CACHE: "OrderedDict[_CacheKey, SeriesPayload]" = OrderedDict()
_CACHE_LOCK: Final[Lock] = Lock()


def _cache_get(key: _CacheKey) -> SeriesPayload | None:
    """Return a cached payload and mark it as the most recently used.

    Args:
        key: Canonical query plus the identity of the parquet.

    Returns:
        The payload, or ``None`` when it is not cached.
    """
    with _CACHE_LOCK:
        payload = _CACHE.get(key)
        if payload is not None:
            _CACHE.move_to_end(key)
        return payload


def _cache_put(key: _CacheKey, payload: SeriesPayload) -> None:
    """Store a payload, evicting the least recently used entry.

    Args:
        key: Canonical query plus the identity of the parquet.
        payload: Encoded answer to keep.
    """
    with _CACHE_LOCK:
        _CACHE[key] = payload
        _CACHE.move_to_end(key)
        while len(_CACHE) > CACHE_ENTRIES:
            _CACHE.popitem(last=False)
