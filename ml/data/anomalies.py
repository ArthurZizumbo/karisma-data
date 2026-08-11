"""Typed injection and independent audit of deliberate data anomalies.

The rate is fixed at one per mille and the split by kind is an integer
partition decided up front, not a draw: that is what makes the counts of
data/README.md stable between runs and auditable one by one.

The audit deliberately does not read the plan. It recounts with its own
predicates over the frame that was actually written, so that comparing both
turns the documentation into a measurement instead of an intention.
"""

from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
from typing import Final

import numpy as np
import polars as pl

from ml.data.schemas import (
    CLIENT_KEY_BASE,
    LETRAS_VERIFICADORAS,
    N_CLIENTES,
    client_key_expr,
)

ANOMALY_RATE: Final[float] = 0.001

# Temporary position column. Every defect is applied by row position and not
# by value, so that two kinds can never land on the same row.
_ROW_INDEX: Final[str] = "__row__"


class AnomalyKind(StrEnum):
    """The six defects the quality view is expected to report."""

    NEGATIVE_AMOUNT = "monto_negativo"
    IMPOSSIBLE_DATE = "fecha_imposible"
    EXACT_DUPLICATE = "duplicado_exacto"
    MISSING_REQUIRED = "nulo_obligatorio"
    ORPHAN_CLIENT = "cliente_huerfano"
    MAGNITUDE_OUTLIER = "outlier_magnitud"


# Fixed partition, expressed as the counts of the declared volumes: 180 over
# 180 000 rows, 1 000 over 1 000 000 and 80 over 80 000. For any other row
# count the same proportions are kept with the largest remainder method, so a
# reduced scale run still splits the anomalies the way the full one does.
_SHARES: Final[dict[str, dict[AnomalyKind, int]]] = {
    "creditos": {
        AnomalyKind.NEGATIVE_AMOUNT: 60,
        AnomalyKind.IMPOSSIBLE_DATE: 60,
        AnomalyKind.EXACT_DUPLICATE: 40,
        AnomalyKind.MISSING_REQUIRED: 20,
        AnomalyKind.ORPHAN_CLIENT: 0,
        AnomalyKind.MAGNITUDE_OUTLIER: 0,
    },
    "liquidez": {
        AnomalyKind.NEGATIVE_AMOUNT: 300,
        AnomalyKind.IMPOSSIBLE_DATE: 200,
        AnomalyKind.EXACT_DUPLICATE: 200,
        AnomalyKind.MISSING_REQUIRED: 0,
        AnomalyKind.ORPHAN_CLIENT: 0,
        AnomalyKind.MAGNITUDE_OUTLIER: 300,
    },
    "derivados": {
        AnomalyKind.NEGATIVE_AMOUNT: 0,
        AnomalyKind.IMPOSSIBLE_DATE: 20,
        AnomalyKind.EXACT_DUPLICATE: 20,
        AnomalyKind.MISSING_REQUIRED: 0,
        AnomalyKind.ORPHAN_CLIENT: 20,
        AnomalyKind.MAGNITUDE_OUTLIER: 20,
    },
}

# First key of the orphan block. It is a valid DRV-Front encoding on purpose:
# what makes it orphan is that it falls outside the shared pool, not that it
# is malformed, so the reconciliation fails without the parser complaining.
_ORPHAN_KEY_BASE: Final[int] = 900_000


@dataclass(frozen=True, slots=True)
class AnomalyPlan:
    """How many anomalies of each kind a silo carries, decided up front."""

    silo: str
    total_rows: int
    counts: Mapping[AnomalyKind, int]

    @property
    def total(self) -> int:
        """Return the number of anomalous rows of the silo."""
        return sum(self.counts.values())

    @property
    def duplicates(self) -> int:
        """Rows appended as exact copies instead of generated as base rows."""
        return self.counts[AnomalyKind.EXACT_DUPLICATE]

    @property
    def base_rows(self) -> int:
        """Rows the generator has to build so that the file holds total_rows."""
        return self.total_rows - self.duplicates


def anomaly_plan(silo: str, total_rows: int) -> AnomalyPlan:
    """Return the fixed integer partition of one per mille of the rows.

    The total is an integer division and not a rounding: the rate is exactly
    one per mille by construction, so nobody can derive a different rate from
    a rounding rule that changed.

    Args:
        silo: One of creditos, liquidez or derivados.
        total_rows: Rows the written file will hold.

    Returns:
        The plan, with the six kinds present even when a kind is zero, so that
        the table of the README is always complete.

    Raises:
        ValueError: If the silo is unknown.
    """
    if silo not in _SHARES:
        raise ValueError(f"unknown silo {silo!r}")
    shares = _SHARES[silo]
    total = total_rows // 1000
    base = sum(shares.values())
    exact = {kind: total * share / base for kind, share in shares.items()}
    counts = {kind: int(value) for kind, value in exact.items()}
    remainder = total - sum(counts.values())
    # Largest remainder, with the declaration order of the table breaking the
    # ties: two kinds with the same fractional part must not depend on the
    # iteration order of a set.
    orden = sorted(
        shares,
        key=lambda kind: (-(exact[kind] - counts[kind]), list(shares).index(kind)),
    )
    for kind in orden[:remainder]:
        counts[kind] += 1
    return AnomalyPlan(silo=silo, total_rows=total_rows, counts=counts)


def _positions(
    rng: np.random.Generator, plan: AnomalyPlan, height: int, protected_rows: int
) -> dict[AnomalyKind, np.ndarray]:
    """Draw disjoint row positions for every kind, outside the protected head.

    Disjoint on purpose: two anomalies on the same row would make the audit
    count one of them twice, or none, depending on which one overwrote the
    other. The duplicate kind gets source rows that carry no other defect for
    the same reason.
    """
    available = height - protected_rows
    needed = plan.total
    if needed > available:
        raise ValueError(
            f"{plan.silo} needs {needed} unprotected rows and only has {available}"
        )
    drawn = rng.choice(available, size=needed, replace=False) + protected_rows
    drawn.sort()
    positions: dict[AnomalyKind, np.ndarray] = {}
    cursor = 0
    for kind in AnomalyKind:
        count = plan.counts[kind]
        positions[kind] = drawn[cursor : cursor + count]
        cursor += count
    return positions


def _mask(column: str, rows: np.ndarray) -> pl.Expr:
    """Return the predicate that selects the drawn row positions.

    The implode is not decoration: since polars 1.35 an is_in against a series
    of the same dtype is ambiguous and deprecated, and the imploded form is
    the one that keeps meaning membership in the list.
    """
    return pl.col(column).is_in(pl.Series(rows, dtype=pl.UInt32).implode())


def _inject_creditos(
    frame: pl.DataFrame, positions: Mapping[AnomalyKind, np.ndarray]
) -> pl.DataFrame:
    """Apply the four defects SIC-Core is known to export."""
    negativo = _mask(_ROW_INDEX, positions[AnomalyKind.NEGATIVE_AMOUNT])
    fecha = _mask(_ROW_INDEX, positions[AnomalyKind.IMPOSSIBLE_DATE])
    nulo = _mask(_ROW_INDEX, positions[AnomalyKind.MISSING_REQUIRED])
    return frame.with_columns(
        pl.when(negativo)
        .then(-pl.col("sdo_cap").abs())
        .otherwise(pl.col("sdo_cap"))
        .alias("sdo_cap"),
        pl.when(fecha)
        .then(pl.col("f_apert").dt.offset_by("-1d"))
        .otherwise(pl.col("f_venc"))
        .alias("f_venc"),
        pl.when(nulo).then(None).otherwise(pl.col("prod_cd")).alias("prod_cd"),
    )


def _inject_liquidez(
    frame: pl.DataFrame, positions: Mapping[AnomalyKind, np.ndarray]
) -> pl.DataFrame:
    """Apply the three defects TESO-Pos is known to export."""
    negativo = _mask(_ROW_INDEX, positions[AnomalyKind.NEGATIVE_AMOUNT])
    fecha = _mask(_ROW_INDEX, positions[AnomalyKind.IMPOSSIBLE_DATE])
    outlier = _mask(_ROW_INDEX, positions[AnomalyKind.MAGNITUDE_OUTLIER])
    return frame.with_columns(
        pl.when(negativo)
        .then(-pl.col("mto_disp").abs())
        .otherwise(pl.col("mto_disp"))
        .alias("mto_disp"),
        pl.when(negativo)
        .then(pl.lit("ACT"))
        .otherwise(pl.col("tipo_pos"))
        .alias("tipo_pos"),
        pl.when(fecha)
        .then(pl.col("fec_pos").dt.offset_by("-1d"))
        .otherwise(pl.col("fec_val"))
        .alias("fec_val"),
        pl.when(outlier)
        .then(pl.col("ratio_lcr") + pl.lit(50.0))
        .otherwise(pl.col("ratio_lcr"))
        .alias("ratio_lcr"),
    )


def _inject_derivados(
    frame: pl.DataFrame, positions: Mapping[AnomalyKind, np.ndarray]
) -> pl.DataFrame:
    """Apply the three defects DRV-Front is known to export."""
    fecha = _mask(_ROW_INDEX, positions[AnomalyKind.IMPOSSIBLE_DATE])
    huerfano = positions[AnomalyKind.ORPHAN_CLIENT]
    outlier = _mask(_ROW_INDEX, positions[AnomalyKind.MAGNITUDE_OUTLIER])
    # One code per orphan row, each with its own key, laid out as a column of
    # the same height as the frame. A join would say the same thing and would
    # not promise to give the rows back in the order they came in, and this
    # frame is written to disk exactly as it leaves here.
    codigos: list[str | None] = [None] * frame.height
    for offset, row in enumerate(huerfano):
        codigos[int(row)] = _orphan_code(_ORPHAN_KEY_BASE + offset)
    return frame.with_columns(
        pl.when(fecha)
        .then(pl.lit("20261332"))
        .otherwise(pl.col("f_trade"))
        .alias("f_trade"),
        pl.when(outlier)
        .then(pl.lit(5.0e10))
        .otherwise(pl.col("nocional_usd"))
        .alias("nocional_usd"),
        pl.coalesce(
            pl.Series("__ctpty__", codigos, dtype=pl.Utf8), pl.col("ctpty_cd")
        ).alias("ctpty_cd"),
    )


def _orphan_code(number: int) -> str:
    """Return a well formed counterparty code that points outside the pool."""
    return f"C{number:06d}{LETRAS_VERIFICADORAS[number % 10]}"


def inject(
    frame: pl.DataFrame,
    plan: AnomalyPlan,
    rng: np.random.Generator,
    *,
    protected_rows: int = 0,
) -> pl.DataFrame:
    """Apply the plan and return a frame of exactly plan.total_rows rows.

    Args:
        frame: Base frame of plan.base_rows rows.
        plan: Partition to apply.
        rng: Substream named anomalias.
        protected_rows: Leading rows that must not be touched. The liquidity
            spine uses it so that no cell of the dashboard grid can lose its
            only row and the published series end up one point short.

    Returns:
        The frame with the anomalies applied and the exact duplicates already
        appended, in the same column order it came in.

    Raises:
        ValueError: If the frame does not hold plan.base_rows rows, or if the
            unprotected region is too small for the plan.
    """
    if frame.height != plan.base_rows:
        raise ValueError(
            f"{plan.silo} base frame has {frame.height} rows "
            f"and the plan needs {plan.base_rows}"
        )
    if plan.total == 0:
        return frame
    columnas = frame.columns
    indexed = frame.with_row_index(_ROW_INDEX)
    positions = _positions(rng, plan, frame.height, protected_rows)
    if plan.silo == "creditos":
        mutated = _inject_creditos(indexed, positions)
    elif plan.silo == "liquidez":
        mutated = _inject_liquidez(indexed, positions)
    else:
        mutated = _inject_derivados(indexed, positions)
    copias = mutated.filter(_mask(_ROW_INDEX, positions[AnomalyKind.EXACT_DUPLICATE]))
    return pl.concat([mutated, copias]).select(columnas)


def audit(frame: pl.DataFrame, silo: str) -> dict[AnomalyKind, int]:
    """Count anomalies with independent predicates over the written frame.

    Deliberately does not read the plan: comparing this result against it is
    what turns the documentation into a measurement. A kind whose predicate
    does not apply to the silo, because the columns it needs are not there,
    counts zero.

    Args:
        frame: Frame as it was written to disk.
        silo: One of creditos, liquidez or derivados.

    Returns:
        One count per kind, with the six kinds always present.

    Raises:
        ValueError: If the silo is unknown.
    """
    if silo not in _SHARES:
        raise ValueError(f"unknown silo {silo!r}")
    counts = dict.fromkeys(AnomalyKind, 0)
    counts[AnomalyKind.EXACT_DUPLICATE] = frame.height - frame.unique().height
    clave = client_key_expr(silo)
    fuera = (clave < CLIENT_KEY_BASE) | (clave >= CLIENT_KEY_BASE + N_CLIENTES)
    counts[AnomalyKind.ORPHAN_CLIENT] = _count(frame, fuera)
    if silo == "creditos":
        counts[AnomalyKind.NEGATIVE_AMOUNT] = _count(frame, pl.col("sdo_cap") < 0)
        counts[AnomalyKind.IMPOSSIBLE_DATE] = _count(
            frame, pl.col("f_venc") < pl.col("f_apert")
        )
        counts[AnomalyKind.MISSING_REQUIRED] = _count(
            frame, pl.col("prod_cd").is_null()
        )
    elif silo == "liquidez":
        counts[AnomalyKind.NEGATIVE_AMOUNT] = _count(
            frame, (pl.col("mto_disp") < 0) & (pl.col("tipo_pos") == "ACT")
        )
        counts[AnomalyKind.IMPOSSIBLE_DATE] = _count(
            frame, pl.col("fec_val") < pl.col("fec_pos")
        )
        counts[AnomalyKind.MAGNITUDE_OUTLIER] = _count(frame, pl.col("ratio_lcr") > 10)
    else:
        counts[AnomalyKind.IMPOSSIBLE_DATE] = _count(
            frame,
            pl.col("f_trade").str.to_date("%Y%m%d", strict=False).is_null(),
        )
        counts[AnomalyKind.MAGNITUDE_OUTLIER] = _count(
            frame, pl.col("nocional_usd") > 1e10
        )
    return counts


def _count(frame: pl.DataFrame, predicate: pl.Expr) -> int:
    """Return how many rows satisfy the predicate, nulls counting as false."""
    return int(frame.select(predicate.fill_null(False).sum()).item())


# The predicate each kind is audited with, per silo, in the words a reader of
# data/README.md can recount by hand. It is a single table and not prose in
# two places: audited_kinds derives from it, so a kind without a predicate is
# a kind the audit does not claim to detect in that silo.
_DUPLICADO: Final[str] = "filas menos filas unicas en todas las columnas"
_HUERFANO: Final[str] = "clave normalizada fuera de [100000, 160000)"

_PREDICADOS: Final[dict[str, dict[AnomalyKind, str]]] = {
    "creditos": {
        AnomalyKind.NEGATIVE_AMOUNT: "sdo_cap < 0",
        AnomalyKind.IMPOSSIBLE_DATE: "f_venc < f_apert",
        AnomalyKind.EXACT_DUPLICATE: _DUPLICADO,
        AnomalyKind.MISSING_REQUIRED: "prod_cd nulo",
        AnomalyKind.ORPHAN_CLIENT: _HUERFANO,
    },
    "liquidez": {
        AnomalyKind.NEGATIVE_AMOUNT: "mto_disp < 0 y tipo_pos = ACT",
        AnomalyKind.IMPOSSIBLE_DATE: "fec_val < fec_pos",
        AnomalyKind.EXACT_DUPLICATE: _DUPLICADO,
        AnomalyKind.ORPHAN_CLIENT: _HUERFANO,
        AnomalyKind.MAGNITUDE_OUTLIER: "ratio_lcr > 10",
    },
    "derivados": {
        AnomalyKind.IMPOSSIBLE_DATE: "f_trade no parsea con el formato AAAAMMDD",
        AnomalyKind.EXACT_DUPLICATE: _DUPLICADO,
        AnomalyKind.ORPHAN_CLIENT: _HUERFANO,
        AnomalyKind.MAGNITUDE_OUTLIER: "nocional_usd > 1e10",
    },
}

LABELS_ES: Final[dict[AnomalyKind, str]] = {
    AnomalyKind.NEGATIVE_AMOUNT: "Monto negativo",
    AnomalyKind.IMPOSSIBLE_DATE: "Fecha imposible",
    AnomalyKind.EXACT_DUPLICATE: "Duplicado exacto",
    AnomalyKind.MISSING_REQUIRED: "Nulo obligatorio",
    AnomalyKind.ORPHAN_CLIENT: "Cliente huerfano",
    AnomalyKind.MAGNITUDE_OUTLIER: "Outlier de magnitud",
}


def audited_kinds(silo: str) -> tuple[AnomalyKind, ...]:
    """Return the kinds the audit of a silo can actually detect.

    Args:
        silo: One of creditos, liquidez or derivados.

    Returns:
        The kinds whose predicate has columns to work with in that silo, in
        the declaration order of AnomalyKind.

    Raises:
        ValueError: If the silo is unknown.
    """
    if silo not in _PREDICADOS:
        raise ValueError(f"unknown silo {silo!r}")
    return tuple(kind for kind in AnomalyKind if kind in _PREDICADOS[silo])


def predicate_es(silo: str, kind: AnomalyKind) -> str:
    """Return the readable predicate the audit uses for a kind in a silo.

    Args:
        silo: One of creditos, liquidez or derivados.
        kind: Kind of anomaly.

    Returns:
        The predicate in Spanish, as data/README.md publishes it.

    Raises:
        ValueError: If the silo is unknown.
        KeyError: If that kind is not audited in that silo.
    """
    if silo not in _PREDICADOS:
        raise ValueError(f"unknown silo {silo!r}")
    return _PREDICADOS[silo][kind]
