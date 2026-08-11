"""Tests of the anomaly plan, its injection and its independent audit.

The frames used here are built locally and on purpose: what is under test is
the injector and the auditor, not the generator. The end to end check over the
real 1 260 000 rows lives in scripts/verificar_datos.sh.
"""

from datetime import date

import polars as pl
import pytest

from ml.data.anomalies import (
    AnomalyKind,
    anomaly_plan,
    audit,
    inject,
)
from ml.data.schemas import (
    BUCKETS_VENC,
    CALIFICACIONES,
    CLIENT_KEY_BASE,
    DIVISAS,
    ESTATUS_CUENTA,
    N_CLIENTES,
    PRODUCTOS,
    SILOS,
    SUBYACENTES,
    TIPOS_INSTRUMENTO,
    UNIDADES_NEGOCIO,
    client_key_creditos,
    client_key_derivados,
    client_key_liquidez,
    normalize_client_key,
)
from ml.utils.seeding import seeded_rng

FILAS_PRUEBA = 20_000


def _base_creditos(rows: int) -> pl.DataFrame:
    """Return a clean SIC-Core frame: no defect of any of the six kinds."""
    return pl.DataFrame(
        {
            "cli_ref": [client_key_creditos(i % N_CLIENTES) for i in range(rows)],
            "nom_cli": [f"CLIENTE {i}" for i in range(rows)],
            "prod_cd": [PRODUCTOS[i % len(PRODUCTOS)] for i in range(rows)],
            "sdo_cap": [1000.0 + i for i in range(rows)],
            "sdo_int": [10.0] * rows,
            "dias_mora": [i % 400 for i in range(rows)],
            "tasa_pct": [12.5] * rows,
            "f_apert": [date(2020, 1, 1)] * rows,
            "f_venc": [date(2030, 1, 1)] * rows,
            "suc_cd": ["S-001"] * rows,
            "est_cta": [ESTATUS_CUENTA[i % len(ESTATUS_CUENTA)] for i in range(rows)],
            "mon_cd": ["01"] * rows,
        },
        schema=SILOS["creditos"].polars_schema(),
    )


def _base_liquidez(rows: int) -> pl.DataFrame:
    """Return a clean TESO-Pos frame."""
    return pl.DataFrame(
        {
            "fec_pos": [date(2026, 6, 30)] * rows,
            "fec_val": [date(2026, 7, 1)] * rows,
            "id_cliente": [client_key_liquidez(i % 8_000) for i in range(rows)],
            "cliente_desc": [f"CLIENTE {i}" for i in range(rows)],
            "bucket_venc": [BUCKETS_VENC[i % len(BUCKETS_VENC)] for i in range(rows)],
            "divisa": [DIVISAS[i % len(DIVISAS)] for i in range(rows)],
            "unidad_negocio": [
                UNIDADES_NEGOCIO[i % len(UNIDADES_NEGOCIO)] for i in range(rows)
            ],
            "mto_disp": [1_000 + i for i in range(rows)],
            "mto_comp": [500] * rows,
            "ratio_lcr": [1.0 + (i % 100) / 1000 for i in range(rows)],
            "tipo_pos": ["ACT" if i % 2 else "PAS" for i in range(rows)],
        },
        schema=SILOS["liquidez"].polars_schema(),
    )


def _base_derivados(rows: int) -> pl.DataFrame:
    """Return a clean DRV-Front frame."""
    return pl.DataFrame(
        {
            "op_id": [f"DRV{i:08d}" for i in range(rows)],
            "ctpty_cd": [client_key_derivados(i % 1_200) for i in range(rows)],
            "ctpty_name": ["CONTRAPARTE SA DE CV"] * rows,
            "subyacente": [SUBYACENTES[i % len(SUBYACENTES)] for i in range(rows)],
            "tipo_instr": [
                TIPOS_INSTRUMENTO[i % len(TIPOS_INSTRUMENTO)] for i in range(rows)
            ],
            "nocional_usd": [1.0e6 + i for i in range(rows)],
            "mtm_val": [1.0] * rows,
            "f_trade": ["20260212"] * rows,
            "f_settle": ["20260213"] * rows,
            "book_cd": ["BK-01"] * rows,
            "cpty_rtg": [CALIFICACIONES[i % len(CALIFICACIONES)] for i in range(rows)],
        },
        schema=SILOS["derivados"].polars_schema(),
    )


_BASES = {
    "creditos": _base_creditos,
    "liquidez": _base_liquidez,
    "derivados": _base_derivados,
}


def test_plan_totals_exactly_one_per_mille() -> None:
    """The split has to add up to the published table over the real volumes.

    A partition that does not add up, or a rounding that derives the rate,
    would put a number in data/README.md that the audit then contradicts.
    """
    planes = {nombre: anomaly_plan(nombre, silo.rows) for nombre, silo in SILOS.items()}

    assert planes["creditos"].total == 180
    assert planes["liquidez"].total == 1_000
    assert planes["derivados"].total == 80

    filas = sum(silo.rows for silo in SILOS.values())
    anomalias = sum(plan.total for plan in planes.values())
    assert filas == 1_260_000
    assert anomalias == 1_260
    assert anomalias / filas == 0.001

    assert planes["creditos"].counts == {
        AnomalyKind.NEGATIVE_AMOUNT: 60,
        AnomalyKind.IMPOSSIBLE_DATE: 60,
        AnomalyKind.EXACT_DUPLICATE: 40,
        AnomalyKind.MISSING_REQUIRED: 20,
        AnomalyKind.ORPHAN_CLIENT: 0,
        AnomalyKind.MAGNITUDE_OUTLIER: 0,
    }
    assert planes["liquidez"].counts[AnomalyKind.MAGNITUDE_OUTLIER] == 300
    assert planes["derivados"].counts[AnomalyKind.ORPHAN_CLIENT] == 20

    with pytest.raises(ValueError, match="unknown silo"):
        anomaly_plan("tesoreria", 1_000)


@pytest.mark.parametrize("silo", sorted(SILOS))
def test_audit_finds_exactly_what_the_plan_declared(silo: str) -> None:
    """The audit must measure what was written, not what was intended.

    This is the central test of the story. It fails if two anomalies land on
    the same row and one overwrites the other, if a when/then does not apply
    because of a dtype, or if a duplicated row carries another defect and gets
    counted twice.
    """
    plan = anomaly_plan(silo, FILAS_PRUEBA)
    base = _BASES[silo](plan.base_rows)

    assert audit(base, silo) == dict.fromkeys(AnomalyKind, 0)

    inyectado = inject(base, plan, seeded_rng("anomalias"))

    assert audit(inyectado, silo) == dict(plan.counts)


def test_injection_never_touches_protected_rows() -> None:
    """No anomaly may land on the spine of the liquidity silo.

    A single defect there is filtered out when aggregating, that cell of the
    grid loses its only row and the published series comes out with 499 999
    points, with the figure already printed in the deliverable.
    """
    plan = anomaly_plan("liquidez", FILAS_PRUEBA)
    base = _base_liquidez(plan.base_rows)
    protegidas = 10_000

    inyectado = inject(base, plan, seeded_rng("anomalias"), protected_rows=protegidas)

    assert inyectado.head(protegidas).equals(base.head(protegidas))
    assert audit(inyectado.head(protegidas), "liquidez") == dict.fromkeys(
        AnomalyKind, 0
    )

    with pytest.raises(ValueError, match="unprotected rows"):
        inject(
            base,
            plan,
            seeded_rng("anomalias"),
            protected_rows=plan.base_rows - plan.total + 1,
        )


@pytest.mark.parametrize("silo", sorted(SILOS))
def test_duplicates_do_not_change_declared_height(silo: str) -> None:
    """The written file holds exactly the number of rows that is published.

    Appending the duplicates on top of the target instead of reserving room
    for them would leave liquidez with 1 000 200 rows while data/README.md
    keeps saying 1 000 000.
    """
    plan = anomaly_plan(silo, FILAS_PRUEBA)
    base = _BASES[silo](plan.base_rows)

    inyectado = inject(base, plan, seeded_rng("anomalias"))

    assert base.height == FILAS_PRUEBA - plan.duplicates
    assert inyectado.height == FILAS_PRUEBA
    assert inyectado.columns == base.columns


def test_orphan_clients_are_outside_the_pool() -> None:
    """An orphan that falls inside the pool is not an orphan.

    The quality view would report a reconciliation case that does not exist,
    and the cross join with creditos would return rows for it.
    """
    plan = anomaly_plan("derivados", FILAS_PRUEBA)
    base = _base_derivados(plan.base_rows)

    inyectado = inject(base, plan, seeded_rng("anomalias"))

    claves = [
        normalize_client_key(valor, "derivados")
        for valor in inyectado["ctpty_cd"].to_list()
    ]
    fuera = [
        clave
        for clave in claves
        if not CLIENT_KEY_BASE <= clave < CLIENT_KEY_BASE + N_CLIENTES
    ]

    assert len(fuera) == plan.counts[AnomalyKind.ORPHAN_CLIENT]
    assert len(set(fuera)) == len(fuera)
