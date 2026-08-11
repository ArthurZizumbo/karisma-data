#!/bin/sh
# ---------------------------------------------------------------------------
#  US-006 - los datos sinteticos solo valen si se pueden reproducir y auditar.
#
#  Cuatro secciones, cada una contra un criterio de aceptacion:
#
#    1. Reproducibilidad: una segunda corrida de "make data" deja los cuatro
#       parquet byte a byte iguales, y "data/README.md" sin cambios.
#    2. Volumenes: 180 000, 1 000 000 y 80 000 filas en los silos y 500 000
#       puntos en la serie preagregada, con 2 000 fechas y 250 claves.
#    3. Cruce: los conjuntos de clientes estan anidados y los cruces devuelven
#       8 000 y 1 200 clientes distintos. Si esto falla, cada archivo se ve
#       perfecto por separado y el producto no tiene nada que ensenar.
#    4. Anomalias: se recuentan con predicados propios sobre el archivo ya
#       escrito y se comparan contra los numeros publicados en el README. Es
#       lo que impide que la verificacion sea una tautologia: si preguntara al
#       inyector, mediria una intencion.
#
#  Este script NO regenera nada por su cuenta salvo en la seccion 1, y ahi
#  escribe en un directorio temporal: correr el verificador no puede cambiar
#  los datos que el resto de las secciones esta mirando.
#
#  POSIX sh, sin argumentos y sin modos: un verificador con modos es un
#  verificador que alguien va a correr en el modo laxo.
# ---------------------------------------------------------------------------

set -eu

RAIZ=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
DATOS="$RAIZ/data"
README="$DATOS/README.md"
PYTHON="poetry -P backend run python"

fallos=0

marcar() {
    # $1: OK|FALLA  $2: etiqueta  $3: detalle
    if [ "$1" = "OK" ]; then
        printf '  [OK   ] %-26s %s\n' "$2" "$3"
    else
        printf '  [FALLA] %-26s %s\n' "$2" "$3" >&2
        fallos=$((fallos + 1))
    fi
}

huella() {
    if [ ! -f "$1" ]; then
        echo "<ausente>"
        return
    fi
    if command -v sha256sum >/dev/null 2>&1; then
        sha256sum "$1" | cut -d' ' -f1
    else
        certutil -hashfile "$1" SHA256 | sed -n '2p' | tr -d ' \r'
    fi
}

comprobar() {
    # $1: etiqueta  $2: observado  $3: esperado
    if [ "$2" = "$3" ]; then
        marcar OK "$1" "$2"
    else
        marcar FALLA "$1" "se esperaba '$3' y se leyo '$2'"
    fi
}

echo "Verificacion de los datos sinteticos (US-006)"
echo ""

# --- Requisitos -------------------------------------------------------------
if [ ! -d "$DATOS/silos" ] || [ ! -f "$DATOS/aggregates/serie_tablero.parquet" ]; then
    echo "Faltan los datos generados. Corre 'make data' antes de verificar." >&2
    exit 1
fi

cd "$RAIZ"

# --- 1. Reproducibilidad ----------------------------------------------------
echo "1. Reproducibilidad byte a byte"

TEMPORAL="$DATOS/.verificacion"
rm -rf "$TEMPORAL"
# Con set -eu, un fallo de la corrida de control aborta el script y dejaria el
# directorio en el arbol de trabajo. Sus parquet los tapa *.parquet, pero su
# README y su manifiesto no: acabarian propuestos para commit.
trap 'rm -rf "$TEMPORAL"' EXIT INT TERM
mkdir -p "$TEMPORAL"
# La corrida de control escribe en un directorio aparte: el README versionado
# no se toca aqui, y su idempotencia se comprueba abajo con git.
$PYTHON -m ml.data.generators --out "$TEMPORAL" >/dev/null

for archivo in silos/creditos.parquet silos/liquidez.parquet \
               silos/derivados.parquet aggregates/serie_tablero.parquet; do
    original=$(huella "$DATOS/$archivo")
    control=$(huella "$TEMPORAL/$archivo")
    if [ "$original" = "$control" ]; then
        marcar OK "$(basename "$archivo")" "$(echo "$original" | cut -c1-16)..."
    else
        marcar FALLA "$(basename "$archivo")" "la segunda corrida cambio los bytes"
    fi
done
rm -rf "$TEMPORAL"

# Sobre un archivo que git no rastrea, "git diff --quiet" sale 0 siempre: la
# comprobacion daria OK sin medir nada, que es peor que no tenerla porque
# fabrica evidencia. Por eso se exige primero que el archivo este versionado.
if command -v git >/dev/null 2>&1; then
    if ! git -C "$RAIZ" ls-files --error-unmatch data/README.md >/dev/null 2>&1; then
        marcar FALLA "README idempotente" \
            "data/README.md sin versionar: no hay contra que comparar"
    elif git -C "$RAIZ" diff --quiet -- data/README.md; then
        marcar OK "README idempotente" "sin cambios tras regenerar"
    else
        marcar FALLA "README idempotente" "data/README.md quedo modificado"
    fi
fi

echo ""

# --- 2. Volumenes -----------------------------------------------------------
echo "2. Volumenes escritos"

medidas=$($PYTHON - "$DATOS" <<'PY'
import sys
from pathlib import Path

import polars as pl

base = Path(sys.argv[1])
for nombre in ("creditos", "liquidez", "derivados"):
    ruta = base / "silos" / f"{nombre}.parquet"
    print(nombre, pl.scan_parquet(ruta).select(pl.len()).collect().item())
serie = pl.read_parquet(base / "aggregates" / "serie_tablero.parquet")
print("serie_filas", serie.height)
print("serie_fechas", serie["fecha"].n_unique())
print("serie_claves", serie["serie_id"].n_unique())
print("serie_nulos", serie.null_count().sum_horizontal().item())
print("serie_orden", int(serie.equals(serie.sort("serie_id", "fecha"))))
print("serie_vacios", serie.filter(pl.col("n_posiciones") < 1).height)
PY
)

leer() {
    echo "$medidas" | awk -v clave="$1" '$1 == clave { print $2 }'
}

comprobar "filas creditos" "$(leer creditos)" "180000"
comprobar "filas liquidez" "$(leer liquidez)" "1000000"
comprobar "filas derivados" "$(leer derivados)" "80000"
comprobar "puntos de la serie" "$(leer serie_filas)" "500000"
comprobar "fechas de la serie" "$(leer serie_fechas)" "2000"
comprobar "claves de la serie" "$(leer serie_claves)" "250"
comprobar "nulos de la serie" "$(leer serie_nulos)" "0"
comprobar "orden (serie_id, fecha)" "$(leer serie_orden)" "1"
comprobar "puntos sin fila cruda" "$(leer serie_vacios)" "0"

echo ""

# --- 3. Cruce entre silos ---------------------------------------------------
echo "3. Cruce de clientes entre silos"

cruces=$($PYTHON - "$DATOS" <<'PY'
import sys
from pathlib import Path

import polars as pl

from ml.data.schemas import SILOS, client_key_expr

base = Path(sys.argv[1])
claves = {}
for nombre in SILOS:
    frame = pl.read_parquet(base / "silos" / f"{nombre}.parquet")
    columna = client_key_expr(nombre).alias("k")
    claves[nombre] = set(frame.select(columna)["k"].drop_nulls().to_list())

print("distintos_creditos", len(claves["creditos"]))
print("cruce_liquidez", len(claves["creditos"] & claves["liquidez"]))
print("cruce_derivados", len(claves["creditos"] & claves["derivados"]))
print("anidado", int(claves["liquidez"] <= claves["creditos"]))
PY
)

leer_cruce() {
    echo "$cruces" | awk -v clave="$1" '$1 == clave { print $2 }'
}

comprobar "clientes en creditos" "$(leer_cruce distintos_creditos)" "60000"
comprobar "creditos x liquidez" "$(leer_cruce cruce_liquidez)" "8000"
comprobar "creditos x derivados" "$(leer_cruce cruce_derivados)" "1200"
comprobar "liquidez dentro de creditos" "$(leer_cruce anidado)" "1"

echo ""

# --- 4. Anomalias -----------------------------------------------------------
echo "4. Anomalias medidas contra lo publicado en el README"

auditoria=$($PYTHON - "$DATOS" "$README" <<'PY'
import re
import sys
from pathlib import Path

import polars as pl

from ml.data.anomalies import LABELS_ES, audit, audited_kinds
from ml.data.schemas import SILOS

base, readme = Path(sys.argv[1]), Path(sys.argv[2])
texto = readme.read_text(encoding="utf-8")

total = 0
filas = 0
for nombre in SILOS:
    frame = pl.read_parquet(base / "silos" / f"{nombre}.parquet")
    filas += frame.height
    medido = audit(frame, nombre)
    for kind in audited_kinds(nombre):
        conteo = medido[kind]
        total += conteo
        patron = rf"\|\s*`{nombre}`\s*\|\s*{LABELS_ES[kind]}\s*\|\s*(\d+)\s*\|"
        encontrado = re.search(patron, texto)
        publicado = encontrado.group(1) if encontrado else "<sin publicar>"
        estado = "OK" if publicado == str(conteo) else "FALLA"
        print(f"{estado} {nombre}.{kind.value} medido={conteo} readme={publicado}")

print(f"TOTAL {total} {filas}")
PY
)

echo "$auditoria" | while IFS= read -r linea; do
    case "$linea" in
        OK*) printf '  [OK   ] %s\n' "$(echo "$linea" | cut -d' ' -f2-)" ;;
        FALLA*) printf '  [FALLA] %s\n' "$(echo "$linea" | cut -d' ' -f2-)" >&2 ;;
        *) : ;;
    esac
done

# El bucle de arriba corre en una subshell, asi que el contador se recalcula
# aqui sobre la misma salida en lugar de heredarse.
descuadres=$(echo "$auditoria" | grep -c '^FALLA' || true)
if [ "$descuadres" -gt 0 ]; then
    fallos=$((fallos + descuadres))
fi

total_anomalias=$(echo "$auditoria" | awk '$1 == "TOTAL" { print $2 }')
total_filas=$(echo "$auditoria" | awk '$1 == "TOTAL" { print $3 }')
comprobar "anomalias totales" "$total_anomalias" "1260"
comprobar "filas totales" "$total_filas" "1260000"

echo ""

# --- Veredicto --------------------------------------------------------------
if [ "$fallos" -gt 0 ]; then
    echo "FALLA: $fallos comprobacion(es) no cumplen los criterios de US-006." >&2
    exit 1
fi

echo "Datos sinteticos en verde: reproducibles, con los volumenes declarados,"
echo "cruzables entre silos y con 1 260 anomalias que el README documenta una a una."
