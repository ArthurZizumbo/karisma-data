#!/bin/sh
# ---------------------------------------------------------------------------
#  US-026 - el historico publicado tiene que salir del Parquet de US-006.
#
#  Las tres tarjetas predictivas de /exploracion/tableros calculan su cifra
#  sobre frontend/public/datos/historicos-tablero.json. Ese archivo se versiona
#  -el prototipo tiene que arrancar sin "make data"- y por eso puede editarse a
#  mano sin que ninguna prueba de vitest lo note: la suite comprueba la FORMA
#  del archivo, no su procedencia.
#
#  Este guion cierra ese hueco. Recalcula la derivacion de la planeacion §2.4
#  desde data/aggregates/serie_tablero.parquet y compara los 72 valores VALOR A
#  VALOR CON IGUALDAD EXACTA. No hay tolerancia, y es deliberado: una tolerancia
#  esconderia justo el defecto que se busca, que es una edicion a mano.
#
#  Modos:
#    (sin argumentos)  verifica y sale != 0 a la primera diferencia
#    --escribir        regenera el JSON desde el Parquet
#
#  Requiere "make data" corrido: data/aggregates/ no se versiona.
#  POSIX sh.
# ---------------------------------------------------------------------------

set -eu

RAIZ=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
PARQUET="$RAIZ/data/aggregates/serie_tablero.parquet"
JSON="$RAIZ/frontend/public/datos/historicos-tablero.json"

MODO="verificar"
if [ "$#" -gt 0 ]; then
    case "$1" in
        --escribir) MODO="escribir" ;;
        *)
            echo "Uso: $0 [--escribir]" >&2
            exit 2
            ;;
    esac
fi

if [ ! -f "$PARQUET" ]; then
    echo "FALLA: falta $PARQUET. Corre 'make data' antes de verificar." >&2
    exit 1
fi

if [ "$MODO" = "verificar" ] && [ ! -f "$JSON" ]; then
    echo "FALLA: falta $JSON. Corre '$0 --escribir' para generarlo." >&2
    exit 1
fi

PYTHONIOENCODING=utf-8 poetry -P "$RAIZ/backend" run python - "$PARQUET" "$JSON" "$MODO" <<'PYTHON'
"""Rebuilds the published dashboard history from the preaggregated series.

The derivation is written once, here, and both modes use it: verifying with a
different expression than the one that writes would compare two beliefs instead
of a file against its source.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import polars as pl

RUTA_PARQUET = Path(sys.argv[1])
RUTA_JSON = Path(sys.argv[2])
MODO = sys.argv[3]

MESES = 24
CONTRATO = "US-006 2.4"
GENERADO_POR = "scripts/verificar_historicos_tablero.sh --escribir"

# id, source column, aggregation translation key, decimals
METRICAS = (
    ("cobertura-liquidez", "ratio_lcr", "forecast.aggregation.weightedMean", 6),
    ("saldo-disponible", "saldo_disponible_mxn", "forecast.aggregation.dailyMean", 4),
    ("concentracion-divisa", "saldo_disponible_mxn", "forecast.aggregation.shareOfTotal", 6),
)


def derivar() -> pl.DataFrame:
    """Monthly aggregation of the three metrics over the last complete months."""
    return (
        pl.scan_parquet(RUTA_PARQUET)
        .with_columns(mes=pl.col("fecha").dt.truncate("1mo"))
        .group_by("mes")
        .agg(
            cobertura_liquidez=(pl.col("ratio_lcr") * pl.col("n_posiciones")).sum()
            / pl.col("n_posiciones").sum(),
            saldo_total=pl.col("saldo_disponible_mxn").sum(),
            saldo_extranjero=pl.col("saldo_disponible_mxn")
            .filter(pl.col("divisa") != "MXN")
            .sum(),
            dias=pl.col("fecha").n_unique(),
        )
        .with_columns(
            saldo_disponible=pl.col("saldo_total") / pl.col("dias") / 1_000_000,
            concentracion_divisa=pl.col("saldo_extranjero") / pl.col("saldo_total"),
        )
        .sort("mes")
        .tail(MESES)
        .collect()
    )


COLUMNA_POR_METRICA = {
    "cobertura-liquidez": "cobertura_liquidez",
    "saldo-disponible": "saldo_disponible",
    "concentracion-divisa": "concentracion_divisa",
}


def construir(marco: pl.DataFrame) -> dict:
    """Payload exactly as the application consumes it."""
    meses = [f"{fecha.year:04d}-{fecha.month:02d}" for fecha in marco["mes"].to_list()]
    metricas = []
    for identificador, campo, clave, decimales in METRICAS:
        valores = marco[COLUMNA_POR_METRICA[identificador]].to_list()
        metricas.append(
            {
                "id": identificador,
                "campoOrigen": campo,
                "claveAgregacion": clave,
                "puntos": [
                    {"mes": mes, "valor": round(valor, decimales)}
                    for mes, valor in zip(meses, valores, strict=True)
                ],
            }
        )
    return {
        "contrato": CONTRATO,
        "fuente": "data/aggregates/serie_tablero.parquet",
        "generadoPor": GENERADO_POR,
        "ventana": {"desde": meses[0], "hasta": meses[-1], "meses": len(meses)},
        "metricas": metricas,
    }


def serializar(payload: dict) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2) + "\n"


esperado = construir(derivar())

if MODO == "escribir":
    RUTA_JSON.parent.mkdir(parents=True, exist_ok=True)
    RUTA_JSON.write_text(serializar(esperado), encoding="utf-8")
    print(f"Escrito {RUTA_JSON} con {len(esperado['metricas'])} metricas x {MESES} meses.")
    raise SystemExit(0)

publicado = json.loads(RUTA_JSON.read_text(encoding="utf-8"))
diferencias: list[str] = []

if publicado.get("ventana") != esperado["ventana"]:
    diferencias.append(
        f"ventana: publicada {publicado.get('ventana')} contra derivada {esperado['ventana']}"
    )

publicadas = {metrica.get("id"): metrica for metrica in publicado.get("metricas", [])}
for metrica in esperado["metricas"]:
    identificador = metrica["id"]
    otra = publicadas.get(identificador)
    if otra is None:
        diferencias.append(f"{identificador}: ausente del archivo publicado")
        continue
    for campo in ("campoOrigen", "claveAgregacion"):
        if otra.get(campo) != metrica[campo]:
            diferencias.append(
                f"{identificador}.{campo}: publicado {otra.get(campo)!r} "
                f"contra derivado {metrica[campo]!r}"
            )
    puntos = otra.get("puntos", [])
    if len(puntos) != len(metrica["puntos"]):
        diferencias.append(
            f"{identificador}: {len(puntos)} puntos publicados contra "
            f"{len(metrica['puntos'])} derivados"
        )
        continue
    for publicado_punto, derivado in zip(puntos, metrica["puntos"], strict=True):
        if publicado_punto.get("mes") != derivado["mes"]:
            diferencias.append(
                f"{identificador}: mes {publicado_punto.get('mes')!r} "
                f"contra {derivado['mes']!r}"
            )
        elif publicado_punto.get("valor") != derivado["valor"]:
            diferencias.append(
                f"{identificador} {derivado['mes']}: publicado "
                f"{publicado_punto.get('valor')!r} contra derivado {derivado['valor']!r}"
            )

sobrantes = set(publicadas) - {metrica["id"] for metrica in esperado["metricas"]}
for identificador in sorted(sobrantes):
    diferencias.append(f"{identificador}: metrica publicada que la derivacion no produce")

if diferencias:
    print("FALLA: el historico publicado no coincide con la serie preagregada.")
    for linea in diferencias[:20]:
        print(f"  [FALLA] {linea}")
    if len(diferencias) > 20:
        print(f"  ... y {len(diferencias) - 20} diferencia(s) mas")
    raise SystemExit(1)

print(f"{len(esperado['metricas'])} metricas x {MESES} meses verificadas contra serie_tablero.parquet")
PYTHON
