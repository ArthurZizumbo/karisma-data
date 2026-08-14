"""Server side preaggregation of the dashboard series.

The contract of the written file is frozen: 500 000 rows, one per (date,
series) cell, sorted by ``(serie_id, fecha)`` so that a single series is a
contiguous slice of 2 000 rows. The dashboard reads it and does not negotiate
it; if it needs another grain, it is changed here and regenerated.
"""

import json
from datetime import date, timedelta
from pathlib import Path
from typing import Final

import polars as pl

from ml.data.manifest import SerieReport, sha256_of
from ml.data.schemas import (
    BUCKETS_VENC,
    DIAS_HABILES,
    DIVISAS,
    DOMAIN_LABELS,
    FECHA_FIN,
    FX_MXN,
    SERIE_TABLERO,
    UNIDADES_NEGOCIO,
)
from ml.utils.parquet import write_frozen_parquet

# Defensive bounds of the aggregation. They are what keeps the injected
# anomalies out of the published series: the silo is dirty by design and the
# aggregate is clean by contract, and the difference between the two is
# exactly what the data quality view reports.
RATIO_LCR_MAX: Final[float] = 3.0
NOMBRE_ARCHIVO: Final[str] = "serie_tablero.parquet"
NOMBRE_SIDECAR: Final[str] = "serie_tablero_meta.json"


def business_days(end: date, count: int) -> pl.Series:
    """Return the last ``count`` weekdays ending at ``end``, ascending.

    No holiday calendar: the simplification is declared in data/README.md.
    With end 2026-06-30 and count 2000 the window opens on 2018-10-31,
    because 2 000 weekdays are exactly 400 calendar weeks.

    Args:
        end: Last day of the window. It has to be a weekday.
        count: Number of business days.

    Returns:
        A Date series of ``count`` values, strictly increasing.

    Raises:
        ValueError: If the count is not positive or the end is a weekend day.
    """
    if count <= 0:
        raise ValueError(f"the window needs at least one day, got {count}")
    if end.weekday() >= 5:
        raise ValueError(f"{end} is not a weekday and cannot close the window")
    # Seven calendar days per five business days, plus two weeks of slack so
    # that the tail never comes up short.
    inicio = end - timedelta(days=(count // 5) * 7 + 14)
    todos = pl.date_range(inicio, end, interval="1d", eager=True)
    habiles = todos.filter(todos.dt.weekday() <= 5)
    return habiles.tail(count).alias("fecha")


def serie_grid() -> pl.DataFrame:
    """Return the 500 000 cell grid: 2 000 dates x 250 series, no metrics.

    Returns:
        The grid with its dimension columns, sorted by (serie_id, fecha), the
        same order the published file uses.
    """
    fechas = business_days(FECHA_FIN, DIAS_HABILES)
    celdas = pl.DataFrame(
        {
            "unidad_negocio": [
                unidad
                for unidad in UNIDADES_NEGOCIO
                for _ in DIVISAS
                for _ in BUCKETS_VENC
            ],
            "divisa": [
                divisa
                for _ in UNIDADES_NEGOCIO
                for divisa in DIVISAS
                for _ in BUCKETS_VENC
            ],
            "bucket_venc": [
                bucket
                for _ in UNIDADES_NEGOCIO
                for _ in DIVISAS
                for bucket in BUCKETS_VENC
            ],
        }
    ).with_row_index("serie_id")
    return (
        celdas.join(pl.DataFrame(fechas), how="cross")
        .with_columns(pl.col("serie_id").cast(pl.UInt16))
        .select("serie_id", "fecha", "unidad_negocio", "divisa", "bucket_venc")
        .sort("serie_id", "fecha")
    )


def _serie_id_expr() -> pl.Expr:
    """Return the vectorized form of the series identifier."""
    unidad = pl.col("unidad_negocio").replace_strict(
        {valor: indice for indice, valor in enumerate(UNIDADES_NEGOCIO)},
        return_dtype=pl.UInt16,
    )
    divisa = pl.col("divisa").replace_strict(
        {valor: indice for indice, valor in enumerate(DIVISAS)},
        return_dtype=pl.UInt16,
    )
    bucket = pl.col("bucket_venc").replace_strict(
        {valor: indice for indice, valor in enumerate(BUCKETS_VENC)},
        return_dtype=pl.UInt16,
    )
    return (unidad * 50 + divisa * 10 + bucket).cast(pl.UInt16).alias("serie_id")


def build_serie_tablero(liquidez: pl.LazyFrame) -> pl.DataFrame:
    """Aggregate the liquidity silo into the published series.

    Filters out the injected anomalies before grouping, converts thousands of
    the original currency into pesos with the fixed synthetic rate, and
    returns the frame sorted by (serie_id, fecha) because that order is part
    of the contract the dashboard relies on to slice a single series.

    Args:
        liquidez: Lazy scan of the liquidity silo.

    Returns:
        One row per non empty grid cell, with the dtypes of SERIE_TABLERO.
    """
    fechas = business_days(FECHA_FIN, DIAS_HABILES)
    tipo_cambio = pl.col("divisa").replace_strict(FX_MXN, return_dtype=pl.Float64)
    return (
        liquidez.filter(pl.col("fec_pos").is_in(fechas.implode()))
        .filter(pl.col("mto_disp") >= 0)
        .filter(pl.col("ratio_lcr").is_between(0.0, RATIO_LCR_MAX))
        .group_by("fec_pos", "unidad_negocio", "divisa", "bucket_venc")
        .agg(
            (pl.col("mto_disp") * 1000 * tipo_cambio)
            .sum()
            .alias("saldo_disponible_mxn"),
            (pl.col("ratio_lcr") * pl.col("mto_disp")).sum().alias("__ponderado__"),
            pl.col("mto_disp").sum().alias("__peso__"),
            pl.len().alias("n_posiciones"),
        )
        .with_columns(
            (pl.col("__ponderado__") / pl.col("__peso__")).alias("ratio_lcr"),
            _serie_id_expr(),
            pl.col("fec_pos").alias("fecha"),
            pl.col("n_posiciones").cast(pl.UInt32),
        )
        .select(*SERIE_TABLERO.columns)
        .sort("serie_id", "fecha")
        .collect()
    )


def _sidecar(frame: pl.DataFrame) -> dict[str, object]:
    """Build the bilingual sidecar that saves the dashboard a full scan."""
    catalogo = [
        {
            "serie_id": int(fila["serie_id"]),
            "unidad_negocio": fila["unidad_negocio"],
            "divisa": fila["divisa"],
            "bucket_venc": fila["bucket_venc"],
            "label_es": " · ".join(
                (
                    DOMAIN_LABELS["unidad_negocio"][fila["unidad_negocio"]][0],
                    DOMAIN_LABELS["divisa"][fila["divisa"]][0],
                    DOMAIN_LABELS["bucket_venc"][fila["bucket_venc"]][0],
                )
            ),
            "label_en": " · ".join(
                (
                    DOMAIN_LABELS["unidad_negocio"][fila["unidad_negocio"]][1],
                    DOMAIN_LABELS["divisa"][fila["divisa"]][1],
                    DOMAIN_LABELS["bucket_venc"][fila["bucket_venc"]][1],
                )
            ),
        }
        for fila in frame.select("serie_id", "unidad_negocio", "divisa", "bucket_venc")
        .unique()
        .sort("serie_id")
        .to_dicts()
    ]
    return {
        "filas": frame.height,
        "fechas": frame["fecha"].n_unique(),
        "series": frame["serie_id"].n_unique(),
        "fecha_min": str(frame["fecha"].min()),
        "fecha_max": str(frame["fecha"].max()),
        "orden": ["serie_id", "fecha"],
        "tipo_cambio": FX_MXN,
        "tipo_cambio_nota_es": (
            "Tipo de cambio sintetico fijo. No es una cotizacion de mercado."
        ),
        "tipo_cambio_nota_en": "Fixed synthetic exchange rate. Not a market quote.",
        "catalogo": catalogo,
    }


def write_serie_tablero(liquidez_path: Path, out_dir: Path) -> SerieReport:
    """Write the parquet and its bilingual sidecar, and return the measurements.

    Args:
        liquidez_path: Path of the written liquidity silo.
        out_dir: Data directory; the series goes under its aggregates/ folder.

    Returns:
        What the written series actually contains.
    """
    serie = build_serie_tablero(pl.scan_parquet(liquidez_path))
    destino = out_dir / "aggregates"
    ruta = destino / NOMBRE_ARCHIVO
    write_frozen_parquet(serie, ruta)
    ruta_meta = destino / NOMBRE_SIDECAR
    ruta_meta.write_text(
        json.dumps(_sidecar(serie), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return SerieReport(
        path=ruta,
        meta_path=ruta_meta,
        rows=serie.height,
        dates=serie["fecha"].n_unique(),
        series=serie["serie_id"].n_unique(),
        date_min=str(serie["fecha"].min()),
        date_max=str(serie["fecha"].max()),
        sha256=sha256_of(ruta),
    )
