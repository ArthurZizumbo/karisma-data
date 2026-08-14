"""The analytical pipeline of the dashboard series, over synthetic aggregates.

No test here opens ``data/aggregates/serie_tablero.parquet`` and none opens a
database. The aggregate of US-006 has twenty seven tests of its own; repeating
them would measure the same thing twice and create a second source of truth for
the headline figure of the document. What is measured here is what this User
Story adds on top: two reductions that are not the same operation, filters that
have to run first, and the provenance that must never be invented.

Every fixture is a handful of rows with values chosen so the expected number can
be computed in the head of whoever reads the assertion. A test whose expected
value comes out of the code it tests proves nothing.

``escribir_agregado`` is shared with ``test_series_endpoint.py``: the two suites
need the same synthetic aggregate and writing it twice would let them drift.
"""

import json
from collections.abc import Iterator, Mapping, Sequence
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Final

import polars as pl
import pytest

from app.models.series import Grouping, MetricName, SeriesParams
from app.services import series_service
from app.services.series_service import SeedMissingError, load_series

ESQUEMA: Final[Mapping[str, pl.DataType]] = {
    "serie_id": pl.UInt16(),
    "fecha": pl.Date(),
    "unidad_negocio": pl.String(),
    "divisa": pl.String(),
    "bucket_venc": pl.String(),
    "saldo_disponible_mxn": pl.Float64(),
    "ratio_lcr": pl.Float64(),
    "n_posiciones": pl.UInt32(),
}

ORIGEN: Final[date] = date(2020, 1, 6)

NOTA_ES: Final[str] = "Tipo de cambio sintetico fijo. No es una cotizacion de mercado."
NOTA_EN: Final[str] = "Fixed synthetic exchange rate. Not a market quote."


def fila(
    *,
    serie_id: int = 0,
    dia: int = 0,
    unidad: str = "TESORERIA",
    divisa: str = "MXN",
    bucket: str = "ON",
    saldo: float = 100.0,
    lcr: float = 1.0,
    posiciones: int = 1,
) -> dict[str, Any]:
    """Build one row of a synthetic aggregate.

    Args:
        serie_id: Key of the grid.
        dia: Offset in days from the fixed origin.
        unidad: Business unit code.
        divisa: Currency code.
        bucket: Maturity bucket code.
        saldo: Balance in pesos.
        lcr: Liquidity ratio, already weighted inside the cell.
        posiciones: Number of positions behind the cell.

    Returns:
        The row, ready to be written.
    """
    return {
        "serie_id": serie_id,
        "fecha": ORIGEN + timedelta(days=dia),
        "unidad_negocio": unidad,
        "divisa": divisa,
        "bucket_venc": bucket,
        "saldo_disponible_mxn": saldo,
        "ratio_lcr": lcr,
        "n_posiciones": posiciones,
    }


def escribir_agregado(
    raiz: Path,
    filas: Sequence[Mapping[str, Any]],
    *,
    con_sidecar: bool = True,
    con_manifiesto: bool = True,
) -> Path:
    """Write a synthetic aggregate where the service expects to find one.

    Args:
        raiz: Directory that plays the role of ``data/``.
        filas: Rows of the aggregate.
        con_sidecar: Whether the bilingual sidecar is written.
        con_manifiesto: Whether the manifest of the silos is written.

    Returns:
        The root that was populated, so a caller can pass it straight on.
    """
    agregados = raiz / "aggregates"
    agregados.mkdir(parents=True, exist_ok=True)
    marco = pl.DataFrame(list(filas), schema=dict(ESQUEMA))
    marco.write_parquet(agregados / "serie_tablero.parquet")

    if con_sidecar:
        catalogo = [
            {
                "serie_id": int(entrada["serie_id"]),
                "unidad_negocio": entrada["unidad_negocio"],
                "divisa": entrada["divisa"],
                "bucket_venc": entrada["bucket_venc"],
                "label_es": " · ".join(
                    (
                        f"Unidad {entrada['unidad_negocio']}",
                        f"Divisa {entrada['divisa']}",
                        f"Plazo {entrada['bucket_venc']}",
                    )
                ),
                "label_en": " · ".join(
                    (
                        f"Unit {entrada['unidad_negocio']}",
                        f"Currency {entrada['divisa']}",
                        f"Tenor {entrada['bucket_venc']}",
                    )
                ),
            }
            for entrada in marco.select(
                "serie_id", "unidad_negocio", "divisa", "bucket_venc"
            )
            .unique()
            .sort("serie_id")
            .to_dicts()
        ]
        (agregados / "serie_tablero_meta.json").write_text(
            json.dumps(
                {
                    "filas": marco.height,
                    "fechas": marco["fecha"].n_unique(),
                    "series": marco["serie_id"].n_unique(),
                    "tipo_cambio_nota_es": NOTA_ES,
                    "tipo_cambio_nota_en": NOTA_EN,
                    "catalogo": catalogo,
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

    if con_manifiesto:
        silos = raiz / "silos"
        silos.mkdir(parents=True, exist_ok=True)
        (silos / "manifest.json").write_text(
            json.dumps(
                {
                    "semilla": 20260720,
                    "silos": [{"nombre": "liquidez", "filas": 1000000}],
                }
            ),
            encoding="utf-8",
        )
    return raiz


@pytest.fixture(autouse=True)
def sin_cache() -> Iterator[None]:
    """Empty the in-process cache around every test.

    Two temporary aggregates written in the same nanosecond would otherwise be
    indistinguishable to a cache that keys on size and modification time.

    Yields:
        None. The fixture only clears process-wide state.
    """
    series_service.clear_cache()
    yield
    series_service.clear_cache()


@pytest.fixture
def rampa(tmp_path: Path) -> Path:
    """Write one line of a thousand days whose value is the day number.

    Returns:
        The data root holding the aggregate.
    """
    return escribir_agregado(
        tmp_path,
        [fila(dia=dia, saldo=float(dia), posiciones=1) for dia in range(1000)],
    )


def test_block_size_is_ceiling_of_the_ratio(rampa: Path) -> None:
    """A thousand dates into four hundred points are blocks of four, not three.

    With a floor division the block would be three, the series would come out in
    334 blocks and the last one would hold a single day: the final mark of the
    chart would be one measurement dressed as a trend.

    Args:
        rampa: Data root holding the aggregate.
    """
    resultado = load_series(SeriesParams(max_puntos=300), data_dir=rampa)

    assert resultado.reduccion.bloque == 4
    assert resultado.reduccion.puntos_originales == 1000
    assert resultado.conteo.fechas == 250


def test_block_label_is_its_first_date(rampa: Path) -> None:
    """A block is labelled with its first date, and averaged over its days.

    Labelling with the last date raises nothing and shifts the whole series four
    days to the right: a chart that lies without failing. The values are the
    other half of the same property: 0..3 average 1.5, 4..7 average 5.5.

    Args:
        rampa: Data root holding the aggregate.
    """
    resultado = load_series(SeriesParams(max_puntos=300), data_dir=rampa)

    assert resultado.fechas[0] == ORIGEN
    assert resultado.fechas[1] == ORIGEN + timedelta(days=4)
    assert resultado.valores[:3] == (1.5, 5.5, 9.5)


def test_lcr_is_reweighted_by_balance_when_series_are_merged(tmp_path: Path) -> None:
    """Merging two cells reweights the ratio by balance, it does not average it.

    ``ratio_lcr`` is already a weighted mean inside each cell. Averaging two of
    them without weights gives 1.5 here instead of 1.75, which is the classic
    statistical defect of this metric and the one a financial reviewer spots
    before the team does.

    Args:
        tmp_path: Directory that plays the role of ``data/``.
    """
    raiz = escribir_agregado(
        tmp_path,
        [
            fila(serie_id=0, divisa="MXN", saldo=100.0, lcr=1.0),
            fila(serie_id=1, divisa="USD", saldo=300.0, lcr=2.0),
        ],
    )

    resultado = load_series(
        SeriesParams(metrica=MetricName.LCR, agrupacion=Grouping.BUSINESS_UNIT),
        data_dir=raiz,
    )

    assert resultado.valores == (1.75,)


def test_lcr_with_zero_balance_is_null_not_zero(tmp_path: Path) -> None:
    """With no balance behind it the ratio is a gap, never a zero.

    A zero drawn on the chart is a claim about liquidity. The hole is the truth,
    and it is the difference between "we do not know" and "there is none".

    Args:
        tmp_path: Directory that plays the role of ``data/``.
    """
    raiz = escribir_agregado(
        tmp_path,
        [
            fila(serie_id=0, dia=0, saldo=0.0, lcr=1.0),
            fila(serie_id=0, dia=1, saldo=50.0, lcr=2.0),
        ],
    )

    resultado = load_series(SeriesParams(metrica=MetricName.LCR), data_dir=raiz)

    assert resultado.valores == (None, 2.0)


def test_filters_run_before_the_reduction(tmp_path: Path) -> None:
    """Excluded lines never reach the average of a block.

    Reducing first and filtering afterwards would compute the block means over
    series the reader excluded. Nothing would fail: the chart would simply
    answer a different question, and here that means 50.5 instead of 0.5.

    Args:
        tmp_path: Directory that plays the role of ``data/``.
    """
    filas = []
    for dia in range(200):
        filas.append(fila(serie_id=0, dia=dia, divisa="MXN", saldo=float(dia)))
        filas.append(fila(serie_id=1, dia=dia, divisa="USD", saldo=dia * 100.0))
    raiz = escribir_agregado(tmp_path, filas)

    resultado = load_series(
        SeriesParams(divisa=("MXN",), max_puntos=100), data_dir=raiz
    )

    assert resultado.reduccion.bloque == 2
    assert resultado.conteo.fechas == 100
    assert resultado.valores[:3] == (0.5, 2.5, 4.5)


def test_positions_are_summed_and_balance_is_summed(tmp_path: Path) -> None:
    """Merging lines adds counts and balances; it does not average them.

    An averaged count is not a count. Three positions in one currency and four
    in another are seven positions in the business unit, not three and a half.

    Args:
        tmp_path: Directory that plays the role of ``data/``.
    """
    raiz = escribir_agregado(
        tmp_path,
        [
            fila(serie_id=0, divisa="MXN", saldo=100.0, posiciones=3),
            fila(serie_id=1, divisa="USD", saldo=300.0, posiciones=4),
        ],
    )

    posiciones = load_series(SeriesParams(metrica=MetricName.POSITIONS), data_dir=raiz)
    saldo = load_series(SeriesParams(metrica=MetricName.BALANCE), data_dir=raiz)

    assert posiciones.valores == (7.0,)
    assert saldo.valores == (400.0,)


def test_a_missing_cell_is_a_gap_and_does_not_shift_the_line(tmp_path: Path) -> None:
    """A hole in the grid becomes a null in place, not a shift of everything.

    US-006 guarantees there are no holes today. If that guarantee ever breaks,
    laying the values out by position instead of joining against the full grid
    would move every point of the affected line one slot to the left, and the
    chart would keep looking perfectly reasonable.

    Args:
        tmp_path: Directory that plays the role of ``data/``.
    """
    raiz = escribir_agregado(
        tmp_path,
        [
            fila(serie_id=0, dia=0, saldo=1.0),
            fila(serie_id=0, dia=1, saldo=2.0),
            fila(serie_id=0, dia=2, saldo=3.0),
            fila(serie_id=1, dia=0, bucket="1D", saldo=10.0),
            fila(serie_id=1, dia=2, bucket="1D", saldo=30.0),
        ],
    )

    resultado = load_series(
        SeriesParams(agrupacion=Grouping.SERIES, max_puntos=100), data_dir=raiz
    )

    assert resultado.conteo.series == 2
    assert resultado.valores == (1.0, 2.0, 3.0, 10.0, None, 30.0)


def test_missing_aggregate_raises_seed_missing(tmp_path: Path) -> None:
    """A clean clone gets a typed failure and never a stack trace.

    This is R9 of US-006, written there as the expected interface of this
    endpoint: without it the first screen an evaluator opens is a 500.

    Args:
        tmp_path: Empty directory that plays the role of ``data/``.
    """
    with pytest.raises(SeedMissingError) as fallo:
        load_series(SeriesParams(), data_dir=tmp_path)

    assert fallo.value.path.name == "serie_tablero.parquet"


def test_empty_filter_result_is_not_an_error(tmp_path: Path) -> None:
    """A filter that matches nothing is an empty answer, not a failure.

    The empty state is a designed screen and a legitimate answer. Turning it
    into a 404 would force the client to catch an exception to render something
    that was never exceptional.

    Args:
        tmp_path: Directory that plays the role of ``data/``.
    """
    raiz = escribir_agregado(tmp_path, [fila()])

    resultado = load_series(SeriesParams(divisa=("JPY",)), data_dir=raiz)

    assert resultado.conteo == resultado.conteo.model_copy(
        update={"puntos": 0, "fechas": 0, "series": 0}
    )
    assert resultado.valores == ()
    assert resultado.series == ()


def test_cache_key_ignores_filter_order() -> None:
    """Two ways of writing the same filters are the same query.

    Without this ``?divisa=USD&divisa=MXN`` and ``?divisa=MXN&divisa=USD``
    produce two validators, the browser cache stops matching and nothing looks
    broken: it is only slower, which is how the defect survives for months.
    """
    una = SeriesParams(divisa=("USD", "MXN"), unidad_negocio=("A", "B"))
    otra = SeriesParams(divisa=("MXN", "USD", "USD"), unidad_negocio=("B", "A"))

    assert una.cache_key() == otra.cache_key()
    assert SeriesParams(divisa=("USD",)).cache_key() != una.cache_key()


def test_the_labels_come_from_the_sidecar_in_both_languages(tmp_path: Path) -> None:
    """The legend is read from the sidecar and never from a scan of the file.

    US-006 wrote the sidecar precisely so the dashboard would not scan half a
    million rows to paint a legend. Recovering the label of a dimension from the
    composite one is the part that can break quietly: a wrong part index would
    label every business unit with its currency.

    Args:
        tmp_path: Directory that plays the role of ``data/``.
    """
    raiz = escribir_agregado(
        tmp_path, [fila(unidad="MERCADOS", divisa="EUR", bucket="1M")]
    )

    por_unidad = load_series(SeriesParams(), data_dir=raiz).series[0]
    por_divisa = load_series(
        SeriesParams(agrupacion=Grouping.CURRENCY), data_dir=raiz
    ).series[0]

    assert (por_unidad.label_es, por_unidad.label_en) == (
        "Unidad MERCADOS",
        "Unit MERCADOS",
    )
    assert (por_divisa.label_es, por_divisa.label_en) == ("Divisa EUR", "Currency EUR")
    assert por_unidad.serie_id is None


def test_without_a_sidecar_the_code_is_its_own_label(tmp_path: Path) -> None:
    """A missing sidecar degrades to codes instead of failing.

    ``data/`` is not versioned and the two files travel separately. A legend in
    codes is readable; a 500 on the screen that shows the headline figure of the
    document is not.

    Args:
        tmp_path: Directory that plays the role of ``data/``.
    """
    raiz = escribir_agregado(tmp_path, [fila()], con_sidecar=False)

    resultado = load_series(SeriesParams(), data_dir=raiz)

    assert resultado.series[0].label_es == "TESORERIA"
    assert resultado.series[0].label_en == "TESORERIA"
    assert resultado.origen.filas_agregadas == 0


def test_provenance_without_a_manifest_leaves_the_figures_null(
    tmp_path: Path,
) -> None:
    """Without the manifest the raw row count and the seed are null, not zero.

    US-029 renders this block verbatim and the anti-hallucination rule of the
    project applies to it: a provenance that invents a figure is worse than one
    that admits it does not have it.

    Args:
        tmp_path: Directory that plays the role of ``data/``.
    """
    raiz = escribir_agregado(tmp_path, [fila()], con_manifiesto=False)

    origen = load_series(SeriesParams(), data_dir=raiz).origen

    assert origen.filas_crudas is None
    assert origen.semilla is None
    assert origen.nota_tipo_cambio_es == NOTA_ES
    assert origen.nota_tipo_cambio_en == NOTA_EN


def test_the_provenance_lists_the_reduction_that_was_applied(rampa: Path) -> None:
    """The block average is named in the provenance whenever it happened.

    The card on the screen has to say what was done to the numbers. Listing the
    upstream steps and hiding the one this endpoint applies would make the
    provenance a decoration.

    Args:
        rampa: Data root holding the aggregate.
    """
    con_reduccion = load_series(SeriesParams(max_puntos=300), data_dir=rampa).origen
    sin_reduccion = load_series(SeriesParams(max_puntos=2000), data_dir=rampa).origen

    assert "media por bloque de 4 dias habiles" in con_reduccion.transformaciones
    assert not [
        paso for paso in sin_reduccion.transformaciones if paso.startswith("media por")
    ]
    assert con_reduccion.filas_crudas == 1000000
    assert con_reduccion.semilla == 20260720
