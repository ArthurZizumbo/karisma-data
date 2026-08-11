"""Tests of the seeding contract: one seed, independent substreams."""

import pytest

from ml.utils.seeding import SEED, STREAM_IDS, seeded_faker, seeded_rng


def test_substreams_are_independent() -> None:
    """A silo must not shift the byte stream of another one.

    The defect this catches is replacing the substreams with a single global
    default_rng(SEED): with one shared generator, changing the row count of
    creditos moves every draw of liquidez and the liquidity file changes its
    bytes without anybody touching it.
    """
    antes = seeded_rng("liquidez").integers(0, 10**9, size=5).tolist()

    consumidor = seeded_rng("creditos")
    consumidor.integers(0, 10**9, size=10_000)

    despues = seeded_rng("liquidez").integers(0, 10**9, size=5).tolist()

    assert antes == despues
    assert antes != seeded_rng("creditos").integers(0, 10**9, size=5).tolist()


def test_faker_stream_is_fixed() -> None:
    """Two Faker instances built here yield the same names.

    Without the seeding call the names change on every run and the criterion
    of byte reproducibility dies in silence: the parquet files differ while
    every row count still adds up.
    """
    primero = [seeded_faker().company() for _ in range(5)]
    segundo = [seeded_faker().company() for _ in range(5)]

    assert primero == segundo

    consumidor = seeded_faker()
    consumidor.company()
    assert seeded_faker().company() == primero[0]


def test_unknown_stream_raises() -> None:
    """An undeclared producer must not silently open a new byte stream."""
    with pytest.raises(KeyError, match="undeclared substream"):
        seeded_rng("catalogo")

    assert SEED == 20260720
    assert set(STREAM_IDS) == {
        "clientes",
        "creditos",
        "liquidez",
        "derivados",
        "anomalias",
    }
    assert len(set(STREAM_IDS.values())) == len(STREAM_IDS)
