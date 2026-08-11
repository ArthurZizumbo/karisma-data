#!/usr/bin/env bash
# ---------------------------------------------------------------------------
#  Smoke de extremo a extremo de US-001 - Karisma Data.
#
#  Recorre las nueve rutas del contrato de navegacion contra el servicio web y
#  despues consulta la sonda del api. Cubre en una sola pasada CA-4 (las rutas
#  responden), CA-7 (la franja de alcance esta en TODAS, incluidas / y /acceso)
#  y CA-8 (/health responde).
#
#  Uso, con el entorno ya levantado por "make dev" en otra terminal:
#      bash scripts/smoke_rutas.sh
#
#  Variables opcionales:
#      BASE_WEB       destino del frontend      (por defecto http://localhost:3000)
#      BASE_API       destino del backend       (por defecto http://localhost:8000)
#      ESPERA_MAXIMA  segundos de espera a que los servicios respondan (60)
#
#  Sale distinto de cero al primer fallo: no acumula errores ni los resume.
# ---------------------------------------------------------------------------

set -euo pipefail

BASE_WEB="${BASE_WEB:-http://localhost:3000}"
BASE_API="${BASE_API:-http://localhost:8000}"
ESPERA_MAXIMA="${ESPERA_MAXIMA:-60}"

# Atributo que el componente FranjaAlcance imprime en el HTML servido por SSR.
# Es contrato, no detalle de maquetacion: si desaparece, la captura de una
# pantalla podria leerse como un sistema real y eso es lo que CA-7 impide.
MARCA_FRANJA="data-franja-alcance"

# Las nueve rutas: el indice mas las ocho del contrato de navegacion de A3.
RUTAS=(
  "/"
  "/acceso"
  "/inicio"
  "/exploracion"
  "/exploracion/tableros"
  "/exploracion/exportar"
  "/gobierno"
  "/asistente"
  "/administracion"
)

TOTAL_ESPERADO=9

CUERPO=""

limpiar() {
  if [ -n "$CUERPO" ] && [ -f "$CUERPO" ]; then
    rm -f "$CUERPO"
  fi
}
trap limpiar EXIT

fallar() {
  printf 'FALLO: %s\n' "$1" >&2
  exit 1
}

esperar_servicio() {
  local url="$1"
  local etiqueta="$2"
  local transcurrido=0

  until curl -sS -o /dev/null --max-time 5 "$url" 2>/dev/null; do
    if [ "$transcurrido" -ge "$ESPERA_MAXIMA" ]; then
      fallar "$etiqueta no respondio en ${ESPERA_MAXIMA} s ($url). Levanta el entorno con make dev."
    fi
    transcurrido=$((transcurrido + 2))
    sleep 2
  done
}

comprobar_ruta() {
  local ruta="$1"
  local url="${BASE_WEB}${ruta}"
  local codigo

  if ! codigo="$(curl -sS -o "$CUERPO" -w '%{http_code}' --max-time 20 "$url")"; then
    fallar "sin respuesta de $url"
  fi

  if [ "$codigo" != "200" ]; then
    fallar "$ruta respondio HTTP ${codigo} y se esperaba 200 (CA-4)"
  fi

  if ! grep -q "$MARCA_FRANJA" "$CUERPO"; then
    fallar "$ruta no contiene el atributo ${MARCA_FRANJA}: falta la franja de alcance (CA-7)"
  fi

  printf '  OK   %-24s HTTP 200   franja de alcance presente\n' "$ruta"
}

comprobar_salud() {
  local url="${BASE_API}/health"
  local codigo

  if ! codigo="$(curl -sS -o "$CUERPO" -w '%{http_code}' --max-time 20 "$url")"; then
    fallar "sin respuesta de $url"
  fi

  if [ "$codigo" != "200" ]; then
    fallar "/health respondio HTTP ${codigo} y se esperaba 200 (CA-8)"
  fi

  printf '  OK   %-24s HTTP 200   %s\n' "/health" "$(cat "$CUERPO")"
}

main() {
  command -v curl >/dev/null 2>&1 || fallar "falta curl en el PATH"

  if [ "${#RUTAS[@]}" -ne "$TOTAL_ESPERADO" ]; then
    fallar "el guion declara ${#RUTAS[@]} rutas y el contrato de navegacion fija ${TOTAL_ESPERADO}"
  fi

  CUERPO="$(mktemp)"

  printf 'Smoke de US-001 contra %s y %s\n\n' "$BASE_WEB" "$BASE_API"

  esperar_servicio "$BASE_WEB/" "el servicio web"
  esperar_servicio "${BASE_API}/health" "el servicio api"

  local ruta
  for ruta in "${RUTAS[@]}"; do
    comprobar_ruta "$ruta"
  done

  comprobar_salud

  printf '\n%s/%s rutas y /health en verde\n' "${#RUTAS[@]}" "$TOTAL_ESPERADO"
}

main "$@"
