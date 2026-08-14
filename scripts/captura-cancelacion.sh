#!/usr/bin/env bash
# ---------------------------------------------------------------------------
#  US-023 - la evidencia de que la cancelacion del chat es real.
#
#  El criterio de aceptacion pide "una captura del registro del servidor", y no
#  una captura de pantalla del navegador: esa ultima prueba que la interfaz
#  cambio, no que el servidor se entero. Lo que este guion produce es una linea
#  JSON del log estructurado.
#
#  La linea es inequivoca porque el generador de app/services/chat_stream.py
#  tiene dos salidas mutuamente excluyentes -chat.stream.completado y
#  chat.stream.cancelado- y la segunda solo se escribe en la rama de
#  desconexion. El campo que la hace concluyente es tokens_emitidos: tiene que
#  ser MAYOR que cero y MENOR que el total del guion. Si fuera igual al total,
#  el servidor habia terminado y el corte fue cosmetico; si fuera cero, se corto
#  antes de que hubiera nada que cortar.
#
#  Tres cosas que este guion sabe y que no son obvias:
#
#   1. LOG_LEVEL se fija en INFO a la fuerza. configure_logging() instala un
#      filtering_bound_logger al nivel configurado, y ese filtro actua ANTES que
#      cualquier procesador: con LOG_LEVEL=WARNING el registro de cierre no se
#      escribe y esta evidencia no existe. No es una preferencia, es la
#      condicion de que el archivo tenga contenido.
#   2. El servicio api del Compose NO monta el codigo fuente, asi que corre la
#      imagen con la que se construyo. La captura levanta su propio uvicorn en
#      el host, contra el codigo que hay en disco ahora.
#   3. Por eso mismo el DSN de backend/.env.local no sirve tal cual: apunta a
#      "db:5432", que es el nombre del servicio dentro de la red del Compose y
#      no resuelve desde el host. Se reescribe al puerto publicado, que se
#      descubre con "docker compose port" en vez de darlo por sentado.
#
#  El token sale de POST /api/auth/demo dentro de este mismo guion. Nunca se
#  escribe a disco, nunca se pega en la evidencia y nunca se codifica aqui.
#
#  Uso:  bash scripts/captura-cancelacion.sh
#  Requisitos: poetry, curl y el PostgreSQL del Compose arriba (make dev).
# ---------------------------------------------------------------------------

set -euo pipefail

RAIZ=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$RAIZ"

PUERTO=${PUERTO_CAPTURA:-8123}
DESTINO="docs/evidencia/us-023"
LOG_SERVIDOR="$DESTINO/servidor.log"
LOG_EVIDENCIA="$DESTINO/cancelacion.log"

# El corte. 0.4 s deja pasar la tarjeta de C1 -que cierra a los 260 ms- y unos
# cuantos fragmentos de los 24 ms, y llega muy lejos del final del guion.
CORTE_SEGUNDOS=${CORTE_SEGUNDOS:-0.4}

SERVIDOR=""

limpiar() {
    if [ -n "$SERVIDOR" ] && kill -0 "$SERVIDOR" 2>/dev/null; then
        kill "$SERVIDOR" 2>/dev/null || true
        wait "$SERVIDOR" 2>/dev/null || true
    fi
}
trap limpiar EXIT

for herramienta in poetry curl; do
    if ! command -v "$herramienta" >/dev/null 2>&1; then
        echo "FALLA: $herramienta no esta en el PATH." >&2
        exit 1
    fi
done

if [ ! -f backend/.env.local ]; then
    echo "FALLA: falta backend/.env.local. Copia backend/.env.example y completalo." >&2
    exit 1
fi

mkdir -p "$DESTINO"

# --- 1. Entorno del servidor de la captura ---------------------------------
# El dotenv se carga entero y luego se pisan las tres variables que esta
# captura decide. Las variables de entorno ganan al dotenv en Pydantic
# Settings, asi que el orden importa y es este.
set -a
# shellcheck disable=SC1091
. ./backend/.env.local
set +a

if [ -z "${DATABASE_URL_CAPTURA:-}" ]; then
    PUBLICADO=$(docker compose port db 5432 2>/dev/null || true)
    if [ -z "$PUBLICADO" ]; then
        echo "FALLA: el PostgreSQL del Compose no esta publicado. Corre 'make dev'," >&2
        echo "       o exporta DATABASE_URL_CAPTURA con un DSN alcanzable." >&2
        exit 1
    fi
    # "127.0.0.1:55432" -> se sustituye el tramo host:puerto del DSN, que en
    # .env.local nombra al servicio del Compose y no resuelve desde el host.
    DATABASE_URL_CAPTURA=$(printf '%s' "$DATABASE_URL" \
        | sed -E "s#@[^/]+/#@${PUBLICADO}/#")
fi

export DATABASE_URL="$DATABASE_URL_CAPTURA"
export LOG_LEVEL=INFO
export DEMO_LOGIN_ENABLED=true
export APP_ENV=local

echo "Captura de la cancelacion del chat (US-023)"
echo ""
echo "1. Levantando uvicorn en el puerto $PUERTO"

# El servidor no se levanta con "uvicorn" a secas, y el motivo es de entorno y
# no del codigo: en Windows el bucle por omision de asyncio es ProactorEventLoop
# y psycopg se niega a correr en modo asincrono sobre el, asi que la primera
# consulta a PostgreSQL revienta con InterfaceError. En Linux -el Compose, Cloud
# Run- no pasa. El lanzador de abajo fija el bucle de seleccion solo en Windows
# y arranca uvicorn por su API; la rama es inerte en cualquier otro sistema.
# Vive en un temporal y no en el arbol: es andamiaje de esta captura, no del
# servicio.
LANZADOR=$(mktemp)
trap 'limpiar; rm -f "$LANZADOR"' EXIT
cat > "$LANZADOR" <<'PY'
"""Launch the API for the capture, with an event loop psycopg accepts."""

import asyncio
import sys

import uvicorn

# The server is driven by hand instead of through ``uvicorn.run``: that helper
# sets up its own event loop, so changing the policy beforehand is ignored and
# psycopg still meets a ProactorEventLoop. Passing the factory to asyncio.run
# is what actually decides which loop the connection is opened on.
config = uvicorn.Config(
    "app.main:create_app",
    factory=True,
    host="127.0.0.1",
    port=int(sys.argv[1]),
    log_level="warning",
)
server = uvicorn.Server(config)

if sys.platform == "win32":
    asyncio.run(server.serve(), loop_factory=asyncio.SelectorEventLoop)
else:
    asyncio.run(server.serve())
PY

: > "$LOG_SERVIDOR"
(
    cd backend
    poetry run python "$LANZADOR" "$PUERTO"
) > "$LOG_SERVIDOR" 2>&1 &
SERVIDOR=$!

listo=0
for _ in $(seq 1 40); do
    if curl -sf "http://127.0.0.1:$PUERTO/health" >/dev/null 2>&1; then
        listo=1
        break
    fi
    if ! kill -0 "$SERVIDOR" 2>/dev/null; then
        echo "FALLA: el servidor murio al arrancar. Su salida:" >&2
        tail -n 20 "$LOG_SERVIDOR" >&2
        exit 1
    fi
    sleep 0.5
done

if [ "$listo" -ne 1 ]; then
    echo "FALLA: el servidor no respondio /health a tiempo." >&2
    tail -n 20 "$LOG_SERVIDOR" >&2
    exit 1
fi

echo "   servidor arriba"

# --- 2. Token de demostracion, obtenido aqui y nunca escrito ---------------
echo ""
echo "2. Pidiendo un token de demostracion para el rol operativo"

RESPUESTA_TOKEN=$(curl -sf -X POST "http://127.0.0.1:$PUERTO/api/auth/demo" \
    -H "Content-Type: application/json" -d '{"rol":"operativo"}')
TOKEN_DEMO=$(printf '%s' "$RESPUESTA_TOKEN" \
    | sed -E 's/.*"access_token"[[:space:]]*:[[:space:]]*"([^"]+)".*/\1/')

if [ -z "$TOKEN_DEMO" ] || [ "$TOKEN_DEMO" = "$RESPUESTA_TOKEN" ]; then
    echo "FALLA: /api/auth/demo no devolvio un token." >&2
    exit 1
fi
unset RESPUESTA_TOKEN

echo "   token obtenido (no se escribe en ningun archivo)"

# --- 3. El corte -----------------------------------------------------------
echo ""
echo "3. Abriendo el stream y cortandolo a los $CORTE_SEGUNDOS s"

curl -sN -X POST "http://127.0.0.1:$PUERTO/api/chat" \
    -H "Authorization: Bearer $TOKEN_DEMO" \
    -H "Content-Type: application/json" \
    -d '{"mensaje":"Cual es la morosidad de la cartera hipotecaria este mes","conversacion":"morosidad"}' \
    --max-time "$CORTE_SEGUNDOS" > /dev/null 2>&1 || true
unset TOKEN_DEMO

# El servidor necesita una vuelta del bucle para enterarse de que el socket se
# cerro y escribir su registro de cierre.
sleep 1
limpiar
SERVIDOR=""

# --- 4. La evidencia -------------------------------------------------------
echo ""
echo "4. Extrayendo la linea de la cancelacion"

grep '"event": "chat.stream.cancelado"' "$LOG_SERVIDOR" > "$LOG_EVIDENCIA" || true

if [ ! -s "$LOG_EVIDENCIA" ]; then
    echo "FALLA: no hay ninguna linea chat.stream.cancelado en el log." >&2
    echo "       Con LOG_LEVEL por encima de INFO el registro no se escribe." >&2
    tail -n 20 "$LOG_SERVIDOR" >&2
    exit 1
fi

# --- 5. El veredicto -------------------------------------------------------
# La linea util es la que cumple 0 < tokens_emitidos < total del guion. El
# total no se codifica aqui: se lee del propio guion, para que reescribir la
# frase de C1 mueva el umbral en vez de dejarlo mintiendo.
echo ""
echo "5. Comprobando que el corte fue real y no cosmetico"

poetry -P backend run python - "$LOG_EVIDENCIA" <<'PY'
"""Read the captured record and decide whether it proves a real cancellation."""

import json
import sys
from pathlib import Path

sys.path.insert(0, "backend")

from app.services.proveedores.guionizado import (  # noqa: E402
    CONVERSACIONES,
    fragmentos_de,
)

total = sum(
    len(fragmentos_de(paso.texto))
    for paso in CONVERSACIONES["morosidad"]
    if paso.herramienta is None
)

lineas = [
    json.loads(linea)
    for linea in Path(sys.argv[1]).read_text(encoding="utf-8").splitlines()
    if linea.strip()
]

utiles = [linea for linea in lineas if 0 < linea["tokens_emitidos"] < total]

for linea in lineas:
    print(
        f"   stream_id={linea['stream_id']} "
        f"tokens_emitidos={linea['tokens_emitidos']}/{total} "
        f"duracion_ms={linea['duracion_ms']}"
    )

if not utiles:
    print(
        f"\nFALLA: ninguna linea cumple 0 < tokens_emitidos < {total}. "
        "El corte fue cosmetico o llego antes del primer fragmento.",
        file=sys.stderr,
    )
    raise SystemExit(1)

print(f"\nEvidencia valida: {len(utiles)} linea(s) con un corte real.")
PY

echo ""
echo "Listo. La evidencia esta en $LOG_EVIDENCIA"
echo "El log completo del servidor queda en $LOG_SERVIDOR"
