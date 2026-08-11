"""Tests of the published series: window, grid, coverage, order and units."""

from datetime import date

import polars as pl
import pytest

from ml.data.aggregates import (
    build_serie_tablero,
    business_days,
    serie_grid,
)
from ml.data.schemas import (
    DIAS_HABILES,
    FECHA_FIN,
    FX_MXN,
    N_SERIES,
    SERIE_TABLERO,
    SILOS,
    serie_id,
)


def _como_liquidez(celdas: pl.DataFrame, mto: int, ratio: float) -> pl.LazyFrame:
    """Turn grid cells into a liquidity frame with constant metrics.

    Only the spine is built on purpose: it is the frame that has to produce
    exactly one group per published point.
    """
    return (
        celdas.rename({"fecha": "fec_pos"})
        .with_columns(
            pl.col("fec_pos").dt.offset_by("1d").alias("fec_val"),
            pl.lit(100_000, dtype=pl.Int64).alias("id_cliente"),
            pl.lit("CLIENTE").alias("cliente_desc"),
            pl.lit(mto, dtype=pl.Int64).alias("mto_disp"),
            pl.lit(mto // 2, dtype=pl.Int64).alias("mto_comp"),
            pl.lit(ratio, dtype=pl.Float64).alias("ratio_lcr"),
            pl.lit("ACT").alias("tipo_pos"),
        )
        .select(*SILOS["liquidez"].columns)
        .lazy()
    )


def test_business_days_window() -> None:
    """An off by one or a weekend inside the window moves every point.

    The deliverable already cites 2 000 business days from 2018-10-31 to
    2026-06-30; a window that drifts makes the figure false without anything
    failing.
    """
    fechas = business_days(FECHA_FIN, DIAS_HABILES)

    assert fechas.len() == DIAS_HABILES
    assert fechas.max() == FECHA_FIN
    assert fechas.min() == date(2018, 10, 31)
    assert fechas.is_sorted(descending=False)
    assert fechas.n_unique() == DIAS_HABILES
    assert fechas.dt.weekday().max() == 5

    with pytest.raises(ValueError, match="at least one day"):
        business_days(FECHA_FIN, 0)
    with pytest.raises(ValueError, match="not a weekday"):
        business_days(date(2026, 6, 28), 10)


def test_serie_grid_is_exactly_500k() -> None:
    """Changing the cardinality of a dimension changes the headline number.

    Five hundred thousand points is the criterion of the story; one more
    currency turns it into six hundred thousand and nothing complains.
    """
    rejilla = serie_grid()

    assert rejilla.height == DIAS_HABILES * N_SERIES == 500_000
    assert rejilla["fecha"].n_unique() == DIAS_HABILES
    assert rejilla["serie_id"].n_unique() == N_SERIES
    assert rejilla.unique(subset=["serie_id", "fecha"]).height == rejilla.height
    assert rejilla["serie_id"].dtype == pl.UInt16


def test_aggregate_covers_every_grid_cell() -> None:
    """Every cell of the grid must survive the anti anomaly filters.

    A filter that is too aggressive takes legitimate groups with it, and the
    published series comes out with fewer points than the document says.
    """
    espina = _como_liquidez(serie_grid(), mto=1_000, ratio=1.2)

    serie = build_serie_tablero(espina)

    assert serie.height == 500_000
    assert serie["fecha"].n_unique() == DIAS_HABILES
    assert serie["serie_id"].n_unique() == N_SERIES
    assert serie.null_count().sum_horizontal().item() == 0
    assert serie.filter(pl.col("n_posiciones") < 1).height == 0
    assert list(serie.columns) == list(SERIE_TABLERO.columns)
    assert dict(serie.schema) == SERIE_TABLERO.polars_schema()


def test_aggregate_order_is_the_published_contract() -> None:
    """A different order on disk breaks the slicing the dashboard relies on.

    Nothing raises: the file is written, the chart paints, and a filter by
    series stops reading one contiguous block.
    """
    espina = _como_liquidez(serie_grid().head(20_000), mto=1_000, ratio=1.2)

    serie = build_serie_tablero(espina)

    assert serie.equals(serie.sort("serie_id", "fecha"))
    primera = serie.filter(pl.col("serie_id") == 0)
    assert primera.height == DIAS_HABILES
    assert primera["fecha"].is_sorted(descending=False)


def test_units_are_converted_to_mxn() -> None:
    """Forgetting the factor of a thousand or the exchange rate.

    It is the classic defect this dataset exists to dramatize, and the only
    place where it can be caught is here: downstream everything is a plain
    number of pesos.
    """
    fecha = business_days(FECHA_FIN, DIAS_HABILES)[0]
    celda = pl.DataFrame(
        {
            "fecha": [fecha, fecha],
            "unidad_negocio": ["TESORERIA", "TESORERIA"],
            "divisa": ["USD", "USD"],
            "bucket_venc": ["ON", "ON"],
        }
    )
    frame = (
        celda.rename({"fecha": "fec_pos"})
        .with_columns(
            pl.col("fec_pos").dt.offset_by("1d").alias("fec_val"),
            pl.lit(100_000, dtype=pl.Int64).alias("id_cliente"),
            pl.lit("CLIENTE").alias("cliente_desc"),
            pl.Series("mto_disp", [100, 200], dtype=pl.Int64),
            pl.Series("mto_comp", [50, 100], dtype=pl.Int64),
            pl.Series("ratio_lcr", [1.0, 1.6], dtype=pl.Float64),
            pl.lit("ACT").alias("tipo_pos"),
        )
        .select(*SILOS["liquidez"].columns)
    )

    serie = build_serie_tablero(frame.lazy())

    assert serie.height == 1
    fila = serie.row(0, named=True)
    assert fila["serie_id"] == serie_id("TESORERIA", "USD", "ON")
    assert fila["saldo_disponible_mxn"] == pytest.approx(300 * 1000 * FX_MXN["USD"])
    assert fila["ratio_lcr"] == pytest.approx((1.0 * 100 + 1.6 * 200) / 300)
    assert fila["n_posiciones"] == 2
