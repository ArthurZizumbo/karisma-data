"""Tests of the frozen column contracts and of the shared client key."""

import itertools

import polars as pl
import pytest

from ml.data.schemas import (
    BUCKETS_VENC,
    CLIENT_KEY_BASE,
    DIVISAS,
    DOMAIN_LABELS,
    N_SERIES,
    SERIE_TABLERO,
    SILOS,
    UNIDADES_NEGOCIO,
    client_key_creditos,
    client_key_derivados,
    client_key_expr,
    client_key_liquidez,
    normalize_client_key,
    serie_id,
)


def test_column_names_are_disjoint_across_silos() -> None:
    """No physical column name may repeat between two silos.

    If the names coincide the semantic catalog translates nothing and the
    screen cannot show the problem the product exists to solve, so somebody
    tidying up the schemas into a shared id_cliente would quietly remove the
    premise of the whole thing.
    """
    nombres = {nombre: set(silo.columns) for nombre, silo in SILOS.items()}

    for uno, otro in itertools.combinations(sorted(nombres), 2):
        assert nombres[uno] & nombres[otro] == set(), (uno, otro)


def test_client_key_encodings_round_trip() -> None:
    """The three encodings of one client reduce to the same integer.

    An off by one in the zero padding or in the check letter does not raise:
    the three files are generated fine and every cross join silently returns
    zero rows.
    """
    for key in (0, 42, 1_199, 7_999, 59_999):
        esperado = CLIENT_KEY_BASE + key
        assert normalize_client_key(client_key_creditos(key), "creditos") == esperado
        assert normalize_client_key(client_key_liquidez(key), "liquidez") == esperado
        assert normalize_client_key(client_key_derivados(key), "derivados") == esperado

    assert client_key_creditos(42) == "CLI-100042"
    assert client_key_liquidez(42) == 100042
    assert client_key_derivados(42) == "C100042C"


def test_normalize_rejects_foreign_encoding() -> None:
    """A value of another silo must raise instead of returning a key.

    Returning a plausible integer would turn an orphan counterparty into a
    false positive of reconciliation, which is the opposite of what the
    quality view has to report.
    """
    with pytest.raises(ValueError, match="SIC-Core"):
        normalize_client_key(client_key_derivados(42), "creditos")
    with pytest.raises(ValueError, match="DRV-Front"):
        normalize_client_key(client_key_creditos(42), "derivados")
    with pytest.raises(ValueError, match="DRV-Front"):
        normalize_client_key("C100042X", "derivados")
    with pytest.raises(ValueError, match="TESO-Pos"):
        normalize_client_key("CLI-100042", "liquidez")
    with pytest.raises(ValueError, match="unknown silo"):
        normalize_client_key(100042, "tesoreria")

    # A well formed key outside the pool is returned, not rejected: that is
    # what makes the orphan anomaly detectable downstream.
    assert normalize_client_key("C900000A", "derivados") == 900_000


def test_client_key_expr_agrees_with_the_scalar_rule() -> None:
    """The vectorized rule and the scalar one must not drift apart.

    The audit normalizes whole columns and the catalog documents the scalar
    function; if one of the two changes alone, the orphan count of the README
    stops matching the rule the note describes.
    """
    claves = [0, 42, 1_199, 59_999]
    frames = {
        "creditos": pl.DataFrame({"cli_ref": [client_key_creditos(k) for k in claves]}),
        "liquidez": pl.DataFrame(
            {"id_cliente": [client_key_liquidez(k) for k in claves]}
        ),
        "derivados": pl.DataFrame(
            {"ctpty_cd": [client_key_derivados(k) for k in claves]}
        ),
    }
    esperado = [CLIENT_KEY_BASE + k for k in claves]

    for silo, frame in frames.items():
        vectorizado = frame.select(client_key_expr(silo).alias("k"))["k"].to_list()
        assert vectorizado == esperado, silo

    malformado = pl.DataFrame({"ctpty_cd": ["C100042X", "basura"]})
    assert malformado.select(client_key_expr("derivados").alias("k"))[
        "k"
    ].to_list() == [None, None]


def test_every_field_has_both_locales() -> None:
    """Every label the interface can show exists in Spanish and in English.

    A field added only in Spanish shows up in the English view as an empty
    column header or as a raw physical code.
    """
    especificaciones = [*SILOS.values(), SERIE_TABLERO]
    campos = [campo for spec in especificaciones for campo in spec.fields]
    assert len(campos) == 34 + 8

    for campo in campos:
        assert campo.label_es.strip(), campo.name
        assert campo.label_en.strip(), campo.name
        assert campo.description_es.strip(), campo.name
        assert campo.description_en.strip(), campo.name

    for dominio, valores in DOMAIN_LABELS.items():
        for valor, (label_es, label_en) in valores.items():
            assert label_es.strip(), (dominio, valor)
            assert label_en.strip(), (dominio, valor)

    # Every enumerated domain of a field has its labels published.
    for campo in campos:
        if campo.domain is None:
            continue
        etiquetas = DOMAIN_LABELS.get(campo.name, {})
        assert set(campo.domain) <= set(etiquetas), campo.name


def test_grid_dimensions_multiply_to_250() -> None:
    """Adding one currency would turn the series into 600 000 points.

    Nothing else would fail: the file would be written, the dashboard would
    paint it and the headline number of the deliverable would be wrong.
    """
    assert len(UNIDADES_NEGOCIO) == 5
    assert len(DIVISAS) == 5
    assert len(BUCKETS_VENC) == 10
    assert N_SERIES == 250
    assert SERIE_TABLERO.rows == 500_000

    identificadores = {
        serie_id(unidad, divisa, bucket)
        for unidad in UNIDADES_NEGOCIO
        for divisa in DIVISAS
        for bucket in BUCKETS_VENC
    }
    assert identificadores == set(range(250))
    assert serie_id("TESORERIA", "MXN", "ON") == 0
    assert serie_id(UNIDADES_NEGOCIO[4], DIVISAS[4], BUCKETS_VENC[9]) == 249

    with pytest.raises(ValueError, match="not a cell of the grid"):
        serie_id("TESORERIA", "CHF", "ON")
