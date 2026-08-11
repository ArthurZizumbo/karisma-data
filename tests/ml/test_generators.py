"""Tests of the three generators: determinism, schema, pools and CLI."""

import json
from pathlib import Path

import polars as pl
import pytest

from ml.data.aggregates import serie_grid
from ml.data.generators import (
    SMOKE_SCALE,
    generate_clients,
    generate_creditos,
    generate_derivados,
    generate_liquidez,
    liquidez_spine_rows,
    main,
    write_silos,
)
from ml.data.schemas import SILOS, normalize_client_key
from ml.utils.seeding import seeded_faker, seeded_rng

FIXTURE = Path(__file__).parent / "fixtures" / "creditos_smoke.json"
CLIENTES_SMOKE = 60


def _clients(rows: int = CLIENTES_SMOKE) -> pl.DataFrame:
    """Build the shared client dimension at the reduced scale of the suite."""
    return generate_clients(seeded_rng("clientes"), seeded_faker(), rows=rows)


def test_generation_is_deterministic() -> None:
    """Two runs of the same generator must return identical frames.

    Any source of non determinism breaks it: random instead of the seeded
    generator, datetime.now, iteration over a set, or parallelism in the
    generation. Byte reproducibility of the parquet files dies with it.
    """
    for generador, filas in (
        (generate_creditos, 180),
        (generate_liquidez, 1_000),
        (generate_derivados, 80),
    ):
        nombre = generador.__name__.removeprefix("generate_")
        primero = generador(_clients(), seeded_rng(nombre), rows=filas)
        segundo = generador(_clients(), seeded_rng(nombre), rows=filas)
        assert primero.equals(segundo), nombre


def test_golden_sample_matches_fixture() -> None:
    """Characterization of the first rows against a committed witness.

    This is the early warning that a poetry update moved the numpy or Faker
    stream, or that somebody reordered the calls to the generator: the files
    would still be written, with every count intact, and every byte different.
    """
    muestra = generate_creditos(_clients(), seeded_rng("creditos"), rows=180).head(25)

    esperado = json.loads(FIXTURE.read_text(encoding="utf-8"))
    assert json.loads(muestra.write_json()) == esperado


def test_schema_matches_spec() -> None:
    """The written dtypes are the cryptic ones of the source, not tidy ones.

    If f_trade is emitted as a date instead of text, or mto_disp as a float,
    the heterogeneity that forces the semantic layer to cast disappears and
    nobody notices until the layer has no case left to prove.
    """
    frames = {
        "creditos": generate_creditos(_clients(), seeded_rng("creditos"), rows=180),
        "liquidez": generate_liquidez(_clients(), seeded_rng("liquidez"), rows=1_000),
        "derivados": generate_derivados(_clients(), seeded_rng("derivados"), rows=80),
    }
    for nombre, frame in frames.items():
        esperado = SILOS[nombre].polars_schema()
        assert list(frame.columns) == list(esperado), nombre
        assert dict(frame.schema) == esperado, nombre

    assert frames["derivados"]["f_trade"].dtype == pl.Utf8
    assert frames["liquidez"]["mto_disp"].dtype == pl.Int64


def test_only_flag_produces_identical_bytes(tmp_path: Path) -> None:
    """Regenerating one silo alone must give the same bytes as the full run.

    A leak between substreams would make a partial regeneration corrupt the
    coherence of the set while every file still looks perfect on its own.
    """
    completo = tmp_path / "completo"
    parcial = tmp_path / "parcial"
    completo.mkdir()
    parcial.mkdir()

    write_silos(completo, scale=SMOKE_SCALE)
    write_silos(parcial, only=["derivados"], scale=SMOKE_SCALE)

    esperado = (completo / "silos" / "derivados.parquet").read_bytes()
    assert (parcial / "silos" / "derivados.parquet").read_bytes() == esperado
    assert not (parcial / "silos" / "creditos.parquet").exists()

    with pytest.raises(ValueError, match="unknown targets"):
        write_silos(parcial, only=["tesoreria"], scale=SMOKE_SCALE)


def test_liquidez_spine_stays_in_the_leading_rows() -> None:
    """The spine has to be the head of the frame, cell by cell and in order.

    Everything downstream leans on it: protected_rows protects a prefix, so a
    reordering -- a join that does not promise to preserve the order of its
    left frame is enough -- lets an anomaly land on a grid cell that has no
    other row behind it. The aggregate then drops that cell and the published
    series comes out with one point less than the deliverable says, with no
    error anywhere.
    """
    filas = 1_000
    espina = liquidez_spine_rows(filas)
    frame = generate_liquidez(_clients(), seeded_rng("liquidez"), rows=filas)

    cabeza = frame.head(espina).select(
        "fec_pos", "unidad_negocio", "divisa", "bucket_venc"
    )
    rejilla = (
        serie_grid()
        .head(espina)
        .select("fecha", "unidad_negocio", "divisa", "bucket_venc")
    )

    assert cabeza.equals(rejilla.rename({"fecha": "fec_pos"}))


def test_only_serie_rebuilds_from_the_written_silo(tmp_path: Path) -> None:
    """Rebuilding only the series must work on top of an existing silo.

    Two real defects hide in this path, and both are reachable from the CLI:
    a report with no silo has zero rows, and without the guard of anomaly_rate
    reading its rate is a ZeroDivisionError; and asking for the series before
    liquidez exists has to fail on the missing input instead of publishing an
    empty series that the dashboard would paint as a flat line.
    """
    write_silos(tmp_path, scale=SMOKE_SCALE)
    esperado = (tmp_path / "aggregates" / "serie_tablero.parquet").read_bytes()

    solo_serie = write_silos(tmp_path, only=["serie"], scale=SMOKE_SCALE)

    assert solo_serie.silos == ()
    assert solo_serie.anomaly_rate == 0.0
    assert (tmp_path / "aggregates" / "serie_tablero.parquet").read_bytes() == esperado

    vacio = tmp_path / "vacio"
    vacio.mkdir()
    with pytest.raises(FileNotFoundError):
        write_silos(vacio, only=["serie"], scale=SMOKE_SCALE)


def test_client_pools_are_nested(tmp_path: Path) -> None:
    """Disjoint pools would make every cross join of the product empty.

    Each file would look perfect on its own and the counterparty exposure
    view, which is the whole point of the dataset, would return no rows.
    """
    write_silos(tmp_path, scale=SMOKE_SCALE)
    silos = {
        nombre: pl.read_parquet(tmp_path / "silos" / f"{nombre}.parquet")
        for nombre in SILOS
    }
    claves = {
        nombre: {
            normalize_client_key(valor, nombre)
            for valor in frame[
                next(c.name for c in SILOS[nombre].fields if c.is_client_key)
            ].to_list()
        }
        for nombre, frame in silos.items()
    }

    assert claves["derivados"] <= claves["liquidez"] <= claves["creditos"]
    assert len(claves["creditos"]) == CLIENTES_SMOKE
    assert claves["creditos"] & claves["liquidez"]


def test_smoke_scale_never_writes_readme(tmp_path: Path) -> None:
    """A quick local check must not be able to corrupt the versioned document.

    Without the guard, one --scale smoke run would commit a data/README.md
    that declares 180 rows where the deliverable says 180 000.
    """
    assert main(["--out", str(tmp_path), "--scale", "smoke"]) == 0

    escritos = sorted(p.name for p in tmp_path.rglob("*") if p.is_file())
    assert "README.md" not in escritos
    assert (tmp_path / ".smoke" / "silos" / "creditos.parquet").exists()
    assert (
        pl.read_parquet(tmp_path / ".smoke" / "silos" / "creditos.parquet").height
        == 180
    )
