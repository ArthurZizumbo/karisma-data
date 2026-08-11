"""Reproducible generators of the three synthetic silos.

Faker is called once per client and never per row: at 1.26 million rows a per
row call would dominate the whole runtime. Everything else is vectorized with
numpy, and every draw comes from the substream of its own silo, so that
changing the volume of one file cannot move the bytes of another.
"""

import argparse
import unicodedata
from collections.abc import Sequence
from datetime import timedelta
from pathlib import Path
from typing import Final

import numpy as np
import polars as pl
from faker import Faker

from ml.data.aggregates import business_days, serie_grid, write_serie_tablero
from ml.data.anomalies import anomaly_plan, audit, inject
from ml.data.manifest import (
    GenerationReport,
    SiloReport,
    sha256_of,
    write_manifest,
)

# Aliased on import: write_silos takes a write_readme flag, and a parameter
# that shadows the function it guards is a trap waiting for the next reader.
from ml.data.manifest import write_readme as emit_readme
from ml.data.schemas import (
    CALIFICACIONES,
    DIAS_HABILES,
    ESTATUS_CUENTA,
    FECHA_FIN,
    N_CLIENTES,
    N_CLIENTES_LIQUIDEZ,
    N_CONTRAPARTES,
    N_SERIES,
    PRODUCTOS,
    SILOS,
    SUBYACENTES,
    TIPOS_INSTRUMENTO,
    TIPOS_POSICION,
    client_key_creditos,
    client_key_derivados,
    client_key_liquidez,
)
from ml.utils.parquet import write_frozen_parquet
from ml.utils.seeding import SEED, seeded_faker, seeded_rng

SUCURSALES: Final[tuple[str, ...]] = tuple(f"S-{i:03d}" for i in range(1, 121))
LIBROS: Final[tuple[str, ...]] = tuple(f"BK-{i:02d}" for i in range(1, 13))
SILO_ORDER: Final[tuple[str, ...]] = ("creditos", "liquidez", "derivados")
SMOKE_DIR: Final[str] = ".smoke"
SMOKE_SCALE: Final[float] = 0.001


def _sin_acentos(texto: str) -> str:
    """Return the text in upper case and without diacritics.

    The derivatives front office exports fixed width ASCII, which is why the
    same company shows up there without the accents it carries in the other
    two systems.
    """
    descompuesto = unicodedata.normalize("NFKD", texto)
    return "".join(c for c in descompuesto if not unicodedata.combining(c)).upper()


def generate_clients(
    rng: np.random.Generator, fake: Faker, *, rows: int = N_CLIENTES
) -> pl.DataFrame:
    """Build the shared client dimension with its three encodings.

    Faker is called once per client and never per row. The dimension is built
    on every invocation, including a partial one, so that the Faker stream
    does not depend on which silo was requested.

    Args:
        rng: Substream named clientes.
        fake: Seeded Faker instance.
        rows: Number of clients of the shared pool.

    Returns:
        One row per client, with the key, the three encodings and the three
        renderings of the legal name.
    """
    nombres = [fake.company() for _ in range(rows)]
    sectores = rng.choice(
        np.array(["FINANCIERO", "INDUSTRIAL", "COMERCIO", "SERVICIOS", "GOBIERNO"]),
        size=rows,
    )
    return pl.DataFrame(
        {
            "clave": [client_key_liquidez(k) for k in range(rows)],
            "cli_ref": [client_key_creditos(k) for k in range(rows)],
            "id_cliente": [client_key_liquidez(k) for k in range(rows)],
            "ctpty_cd": [client_key_derivados(k) for k in range(rows)],
            "nom_cli": [nombre[:30] for nombre in nombres],
            "cliente_desc": nombres,
            "ctpty_name": [_sin_acentos(nombre) for nombre in nombres],
            "sector": sectores.tolist(),
        },
        schema={
            "clave": pl.Int64,
            "cli_ref": pl.Utf8,
            "id_cliente": pl.Int64,
            "ctpty_cd": pl.Utf8,
            "nom_cli": pl.Utf8,
            "cliente_desc": pl.Utf8,
            "ctpty_name": pl.Utf8,
            "sector": pl.Utf8,
        },
    )


def _cobertura(rng: np.random.Generator, pool: int, rows: int) -> np.ndarray:
    """Draw row owners so that every member of the pool appears at least once.

    The first ``pool`` rows take one member each and the rest are drawn with a
    skewed weight, so the distribution is realistic and the cross joins of the
    product never come back empty because a client got no row at all.
    """
    if rows < pool:
        raise ValueError(f"{rows} rows cannot cover a pool of {pool} members")
    pesos = rng.lognormal(0.0, 0.9, pool)
    resto = rng.choice(pool, size=rows - pool, p=pesos / pesos.sum())
    return np.concatenate([np.arange(pool), resto])


def _fechas_ventana() -> np.ndarray:
    """Return the business day window as numpy dates, ascending."""
    return business_days(FECHA_FIN, DIAS_HABILES).to_numpy().astype("datetime64[D]")


def generate_creditos(
    clients: pl.DataFrame, rng: np.random.Generator, *, rows: int = 180_000
) -> pl.DataFrame:
    """Build the SIC-Core silo: amounts in pesos, dates as dates.

    Args:
        clients: Shared client dimension.
        rng: Substream named creditos.
        rows: Rows the written file will hold, duplicates included.

    Returns:
        The base frame, of ``rows`` minus the planned duplicates, with the
        dtypes of the specification and no anomaly yet.
    """
    plan = anomaly_plan("creditos", rows)
    base = plan.base_rows
    duenos = _cobertura(rng, clients.height, base)
    fechas = _fechas_ventana()

    apertura = fechas[rng.integers(0, len(fechas), base)]
    plazo = rng.integers(180, 7300, base).astype("timedelta64[D]")
    productos = np.array(PRODUCTOS)[rng.integers(0, len(PRODUCTOS), base)]
    capital = np.round(rng.lognormal(11.0, 1.2, base), 2)
    tasa = np.round(rng.uniform(6.5, 42.0, base), 2)
    mora = np.where(
        rng.random(base) < 0.15, rng.integers(1, 400, base), np.zeros(base, dtype=int)
    )
    return pl.DataFrame(
        {
            "cli_ref": clients["cli_ref"].gather(duenos),
            "nom_cli": clients["nom_cli"].gather(duenos),
            "prod_cd": productos,
            "sdo_cap": capital,
            "sdo_int": np.round(capital * tasa / 100 * rng.uniform(0.01, 0.4, base), 2),
            "dias_mora": mora,
            "tasa_pct": tasa,
            "f_apert": apertura,
            "f_venc": apertura + plazo,
            "suc_cd": np.array(SUCURSALES)[rng.integers(0, len(SUCURSALES), base)],
            "est_cta": np.array(ESTATUS_CUENTA)[
                rng.integers(0, len(ESTATUS_CUENTA), base)
            ],
            "mon_cd": np.full(base, "01"),
        },
        schema=SILOS["creditos"].polars_schema(),
    )


def _fecha_valor_expr() -> pl.Expr:
    """Return the T+1 business day of every position date, as an expression.

    The value date of the treasury system is one business day after the
    position date. It is a trap on purpose: grouping the dashboard series by
    it would shift every point one day.

    It is a mapping and not a join on purpose. A join does not promise to
    preserve the order of its left frame, and the order of the liquidity silo
    is load bearing: the spine has to stay in the leading rows, because that
    is what ``protected_rows`` protects. A reordering here would let an
    anomaly land on a grid cell that has no other row, and the published
    series would come out one point short without anything failing.
    """
    fechas = business_days(FECHA_FIN, DIAS_HABILES)
    ultimo = fechas[-1]
    # The window closes on a business day, so the day after the last one is
    # the following Monday when that day is a Friday.
    siguiente = ultimo + timedelta(days=3 if ultimo.weekday() == 4 else 1)
    valores = fechas.shift(-1).fill_null(siguiente)
    return (
        pl.col("fec_pos")
        .replace_strict(dict(zip(fechas, valores, strict=True)), return_dtype=pl.Date)
        .alias("fec_val")
    )


def liquidez_spine_rows(rows: int) -> int:
    """Return how many leading rows of the liquidity silo are the spine.

    At the declared volume the answer is the whole grid, 500 000 rows: one
    clean row per published point. The subtraction of the plan is what keeps
    room for the anomalies outside the protected head at any reduced scale,
    where the grid no longer fits in the file.

    Args:
        rows: Rows the written file will hold.

    Returns:
        The number of leading rows the injector must not touch.
    """
    plan = anomaly_plan("liquidez", rows)
    return max(0, min(plan.base_rows - plan.total, DIAS_HABILES * N_SERIES))


def generate_liquidez(
    clients: pl.DataFrame, rng: np.random.Generator, *, rows: int = 1_000_000
) -> pl.DataFrame:
    """Build the liquidity silo, spine first.

    The leading rows are the spine: one clean row per grid cell, so that the
    aggregate has exactly one group per published point no matter what the
    detail rows do. Amounts are in thousands of the row currency, which is the
    trap the semantic layer exists to resolve.

    Args:
        clients: Shared client dimension.
        rng: Substream named liquidez.
        rows: Rows the written file will hold, duplicates included.

    Returns:
        The base frame, spine first, with no anomaly yet.
    """
    plan = anomaly_plan("liquidez", rows)
    base = plan.base_rows
    pool = min(N_CLIENTES_LIQUIDEZ, clients.height)
    rejilla = serie_grid()
    espina = liquidez_spine_rows(rows)
    detalle = base - espina

    celdas = rejilla.head(espina).select(
        "fecha", "unidad_negocio", "divisa", "bucket_venc"
    )
    if detalle:
        indices = rng.integers(0, rejilla.height, detalle)
        celdas = pl.concat(
            [
                celdas,
                rejilla.select(
                    "fecha", "unidad_negocio", "divisa", "bucket_venc"
                ).gather(indices),
            ]
        )

    # The spine walks the client pool in order so that every institutional
    # client is present; the detail rows are drawn freely.
    duenos = np.concatenate([np.arange(espina) % pool, rng.integers(0, pool, detalle)])
    disponible = rng.integers(1, 5_000_000, base)
    frame = celdas.rename({"fecha": "fec_pos"}).with_columns(
        pl.Series("id_cliente", clients["id_cliente"].gather(duenos)),
        pl.Series("cliente_desc", clients["cliente_desc"].gather(duenos)),
        pl.Series("mto_disp", disponible),
        pl.Series("mto_comp", (disponible * rng.uniform(0.05, 0.85, base)).astype(int)),
        pl.Series("ratio_lcr", np.round(rng.uniform(0.75, 1.85, base), 4)),
        pl.Series("tipo_pos", np.array(TIPOS_POSICION)[rng.integers(0, 2, base)]),
    )
    return (
        frame.with_columns(_fecha_valor_expr())
        .select(*SILOS["liquidez"].columns)
        .cast(SILOS["liquidez"].polars_schema())  # type: ignore[arg-type]
    )


def generate_derivados(
    clients: pl.DataFrame, rng: np.random.Generator, *, rows: int = 80_000
) -> pl.DataFrame:
    """Build the DRV-Front silo: dollars, and dates exported as text.

    Args:
        clients: Shared client dimension.
        rng: Substream named derivados.
        rows: Rows the written file will hold, duplicates included.

    Returns:
        The base frame, with no anomaly yet.
    """
    plan = anomaly_plan("derivados", rows)
    base = plan.base_rows
    pool = min(N_CONTRAPARTES, clients.height)
    duenos = _cobertura(rng, pool, base)
    fechas = _fechas_ventana()

    concertacion = fechas[rng.integers(0, len(fechas), base)]
    liquidacion = concertacion + rng.integers(1, 90, base).astype("timedelta64[D]")
    nocional = np.round(rng.lognormal(14.0, 1.1, base), 2)
    return pl.DataFrame(
        {
            "op_id": [f"DRV{i:08d}" for i in range(base)],
            "ctpty_cd": clients["ctpty_cd"].gather(duenos),
            "ctpty_name": clients["ctpty_name"].gather(duenos),
            "subyacente": np.array(SUBYACENTES)[
                rng.integers(0, len(SUBYACENTES), base)
            ],
            "tipo_instr": np.array(TIPOS_INSTRUMENTO)[
                rng.integers(0, len(TIPOS_INSTRUMENTO), base)
            ],
            "nocional_usd": nocional,
            "mtm_val": np.round(nocional * rng.normal(0.0, 0.05, base), 2),
            "f_trade": np.datetime_as_string(concertacion, unit="D"),
            "f_settle": np.datetime_as_string(liquidacion, unit="D"),
            "book_cd": np.array(LIBROS)[rng.integers(0, len(LIBROS), base)],
            "cpty_rtg": np.array(CALIFICACIONES)[
                rng.integers(0, len(CALIFICACIONES), base)
            ],
        },
        schema=SILOS["derivados"].polars_schema(),
    ).with_columns(
        pl.col("f_trade").str.replace_all("-", ""),
        pl.col("f_settle").str.replace_all("-", ""),
    )


_GENERADORES = {
    "creditos": generate_creditos,
    "liquidez": generate_liquidez,
    "derivados": generate_derivados,
}


def _escalado(valor: int, scale: float) -> int:
    """Return a volume reduced by the scale, never below one row."""
    return max(1, round(valor * scale))


def write_silos(
    out_dir: Path,
    *,
    only: Sequence[str] | None = None,
    scale: float = 1.0,
    write_readme: bool = True,
) -> GenerationReport:
    """Generate, inject, write and report. The single entry point.

    Args:
        out_dir: Data directory; silos/ and aggregates/ hang from it.
        only: Subset of creditos, liquidez, derivados and serie. The client
            dimension is built anyway, so a partial run writes the same bytes
            as the complete one.
        scale: Factor applied to every declared volume. One is the real size.
        write_readme: Whether the versioned README may be rewritten. It is
            only rewritten when the run is complete at the declared volumes.

    Returns:
        What was actually written, measured file by file.

    Raises:
        ValueError: If a name of ``only`` is not a silo or the series.
    """
    pedidos = tuple(only) if only else (*SILO_ORDER, "serie")
    desconocidos = set(pedidos) - {*SILO_ORDER, "serie"}
    if desconocidos:
        raise ValueError(f"unknown targets: {sorted(desconocidos)}")

    clients = generate_clients(
        seeded_rng("clientes"), seeded_faker(), rows=_escalado(N_CLIENTES, scale)
    )
    informes: list[SiloReport] = []
    for nombre in SILO_ORDER:
        if nombre not in pedidos:
            continue
        filas = _escalado(SILOS[nombre].rows, scale)
        plan = anomaly_plan(nombre, filas)
        frame = _GENERADORES[nombre](clients, seeded_rng(nombre), rows=filas)
        protegidas = liquidez_spine_rows(filas) if nombre == "liquidez" else 0
        # A fresh substream per silo, not a shared one: sharing it would make
        # the anomalies of derivados depend on whether liquidez ran before.
        frame = inject(frame, plan, seeded_rng("anomalias"), protected_rows=protegidas)
        ruta = out_dir / "silos" / f"{nombre}.parquet"
        tamanio = write_frozen_parquet(frame, ruta)
        informes.append(
            SiloReport(
                name=nombre,
                path=ruta,
                rows=frame.height,
                columns=frame.width,
                size_bytes=tamanio,
                sha256=sha256_of(ruta),
                anomalies=audit(frame, nombre),
            )
        )

    serie = None
    if "serie" in pedidos:
        serie = write_serie_tablero(out_dir / "silos" / "liquidez.parquet", out_dir)

    report = GenerationReport(seed=SEED, silos=tuple(informes), serie=serie)
    if report.is_complete:
        # Both documents carry the same guard. A partial manifest is worse
        # than the one of the previous run: since a partial run reproduces the
        # same bytes, the older manifest still describes what is on disk
        # exactly, while a freshly written one listing a single silo would
        # leave the data quality view with one source instead of three.
        write_manifest(report, out_dir)
        if write_readme:
            emit_readme(report, out_dir)
    return report


def main(argv: Sequence[str] | None = None) -> int:
    """Command line entry point of ``make data``.

    Args:
        argv: Arguments, or None to read them from the process.

    Returns:
        The process exit code.
    """
    parser = argparse.ArgumentParser(
        prog="python -m ml.data.generators",
        description=(
            "Genera los silos sinteticos y la serie preagregada con semilla fija."
        ),
    )
    parser.add_argument("--out", default="data", help="directorio de salida")
    parser.add_argument(
        "--only",
        action="append",
        choices=[*SILO_ORDER, "serie"],
        help="genera solo lo indicado; se puede repetir",
    )
    parser.add_argument(
        "--scale",
        choices=("full", "smoke"),
        default="full",
        help="smoke escribe en <out>/.smoke y nunca toca data/README.md",
    )
    args = parser.parse_args(argv)

    salida = Path(args.out)
    scale = 1.0
    if args.scale == "smoke":
        salida = salida / SMOKE_DIR
        scale = SMOKE_SCALE
    salida.mkdir(parents=True, exist_ok=True)

    report = write_silos(
        salida, only=args.only, scale=scale, write_readme=args.scale == "full"
    )
    for silo in report.silos:
        print(f"{silo.name:>10}: {silo.rows} filas, {silo.size_bytes} bytes")
    if report.serie is not None:
        print(f"{'serie':>10}: {report.serie.rows} filas, {report.serie.series} claves")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
