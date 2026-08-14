#!/usr/bin/env bash
# ---------------------------------------------------------------------------
#  Smoke de la serie preagregada del tablero - US-025, Karisma Data.
#
#  Comprueba contra el stack levantado lo que ninguna prueba unitaria puede
#  ver, porque todas doblan el transporte: que el marco binario llega entero,
#  que pesa lo que el criterio de aceptacion dice, que el proxy de Nitro no lo
#  reescribe y que la autorizacion decide igual por los dos caminos.
#
#  Secciones:
#    1. carga completa .... 500 000 puntos, magia KSER, tamano <= 2.2 MB
#    2. tamanos ........... binario contra JSON a igual consulta, con cociente
#    3. autorizacion ...... 401 sin token, 403 con operativo, 200 con analista
#    4. integridad ........ sha256 identico por el api y por el proxy
#    5. cache ............. el mismo ETag dos veces y 304 con If-None-Match
#
#  La seccion 3 cierra la deuda 4 de docs/security.md: hasta esta US ninguna
#  ruta viva del portal podia responder 403, asi que la verificacion manual del
#  rechazo a traves del proxy no se habia podido hacer nunca.
#
#  Uso, con "make dev" levantado en otra terminal y "make data" corrido:
#      bash scripts/smoke_serie.sh
#
#  Variables opcionales:
#      BASE_WEB       destino del frontend  (por defecto http://127.0.0.1:3000)
#      BASE_API       destino del backend   (por defecto http://127.0.0.1:8000)
#      ESPERA_MAXIMA  segundos de espera a que los servicios respondan (60)
#
#  Sale distinto de cero al primer fallo: no acumula errores ni los resume.
# ---------------------------------------------------------------------------

set -euo pipefail

BASE_WEB="${BASE_WEB:-http://127.0.0.1:3000}"
BASE_API="${BASE_API:-http://127.0.0.1:8000}"
ESPERA_MAXIMA="${ESPERA_MAXIMA:-60}"

RUTA="/api/metrics/series"

# La carga completa: las 250 claves de la rejilla sin reducir. Es la evidencia
# de rendimiento y la cifra que el documento de A4 publica.
CONSULTA_COMPLETA="agrupacion=serie&max_puntos=2000"
PUNTOS_COMPLETOS=500000

# Consulta que las dos representaciones pueden servir: 250 lineas de 200 puntos
# son 50 000, justo el tope de la variante legible. A igual consulta, el
# cociente de tamanos es comparable y no una comparacion de peras con manzanas.
CONSULTA_COMPARABLE="agrupacion=serie&max_puntos=200"

# CA-10: el marco de la carga completa pesa como mucho 2.2 MB, y a igual
# consulta el JSON pesa al menos el triple.
TOPE_BYTES=2306867
COCIENTE_MINIMO=3

TEMPORAL="$(mktemp -d)"
trap 'rm -rf "$TEMPORAL"' EXIT

CUERPO="${TEMPORAL}/cuerpo"
CABECERAS="${TEMPORAL}/cabeceras"
GALLETAS="${TEMPORAL}/galletas"

fallar() {
  printf '\n  FALLO  %s\n\n' "$1" >&2
  exit 1
}

esperar_a() {
  local url="$1"
  local nombre="$2"
  local inicio
  inicio="$(date +%s)"
  until curl -sS -o /dev/null --max-time 5 "$url" 2>/dev/null; do
    if [ "$(( $(date +%s) - inicio ))" -ge "$ESPERA_MAXIMA" ]; then
      fallar "$nombre no respondio en ${ESPERA_MAXIMA}s ($url). Levanta el stack con make dev"
    fi
    sleep 1
  done
}

# Emite un token de un rol por la puerta de demostracion del api. Devuelve el
# token crudo, que es lo que el smoke necesita para hablar con el backend sin
# pasar por el navegador.
token_de() {
  local rol="$1"
  local respuesta
  respuesta="$(curl -sS --max-time 20 -X POST -H 'Content-Type: application/json' \
    -d "{\"rol\":\"${rol}\"}" "${BASE_API}/api/auth/demo")" \
    || fallar "sin respuesta de ${BASE_API}/api/auth/demo"
  case "$respuesta" in
    *access_token*) ;;
    *) fallar "DEMO_LOGIN_ENABLED esta apagada: sin token no hay smoke" ;;
  esac
  printf '%s' "$respuesta" | sed -e 's/.*"access_token":"//' -e 's/".*//'
}

# Pide una URL del api con un token y deja el cuerpo en $CUERPO. Imprime el
# estado y el tamano descargado, separados por un espacio.
pedir_api() {
  local url="$1"
  local token="${2:-}"
  local autorizacion=()
  [ -n "$token" ] && autorizacion=(-H "Authorization: Bearer ${token}")
  curl -sS -o "$CUERPO" -D "$CABECERAS" -w '%{http_code} %{size_download}' \
    --max-time 60 "${autorizacion[@]}" "$url" \
    || fallar "sin respuesta de $url"
}

cabecera() {
  # $1: nombre en minusculas. Las cabeceras HTTP no distinguen mayusculas.
  tr -d '\r' < "$CABECERAS" | grep -i "^$1:" | tail -1 | cut -d' ' -f2- || true
}

sha_de() {
  sha256sum "$1" | cut -d' ' -f1
}

comprobar_carga_completa() {
  local token="$1"
  local resultado estado bytes puntos magia
  resultado="$(pedir_api "${BASE_API}${RUTA}?${CONSULTA_COMPLETA}" "$token")"
  estado="${resultado% *}"
  bytes="${resultado#* }"

  [ "$estado" = "200" ] || fallar "la carga completa respondio HTTP ${estado}"

  puntos="$(cabecera 'x-karisma-puntos')"
  [ "$puntos" = "$PUNTOS_COMPLETOS" ] \
    || fallar "la carga completa declara ${puntos} puntos y se esperaban ${PUNTOS_COMPLETOS}. Corre make data"

  magia="$(head -c 4 "$CUERPO")"
  [ "$magia" = "KSER" ] || fallar "el cuerpo no empieza por la magia KSER"

  [ "$bytes" -le "$TOPE_BYTES" ] \
    || fallar "el marco pesa ${bytes} B y CA-10 fija el tope en ${TOPE_BYTES} B"

  [ "$(cabecera 'content-type')" = "application/vnd.karisma.serie-v1" ] \
    || fallar "el marco no declara su propio tipo de contenido"

  printf '  OK   %-22s HTTP 200   %s puntos, %s B, magia KSER\n' \
    "carga completa" "$puntos" "$bytes"
}

comprobar_tamanos() {
  local token="$1"
  local binario json cociente
  binario="$(pedir_api "${BASE_API}${RUTA}?${CONSULTA_COMPARABLE}" "$token")"
  [ "${binario% *}" = "200" ] || fallar "la consulta comparable en binario dio HTTP ${binario% *}"
  binario="${binario#* }"

  json="$(pedir_api "${BASE_API}${RUTA}?${CONSULTA_COMPARABLE}&formato=json" "$token")"
  [ "${json% *}" = "200" ] || fallar "la consulta comparable en JSON dio HTTP ${json% *}"
  json="${json#* }"

  cociente="$(awk -v j="$json" -v b="$binario" 'BEGIN { printf "%.2f", j / b }')"
  awk -v c="$cociente" -v m="$COCIENTE_MINIMO" 'BEGIN { exit !(c >= m) }' \
    || fallar "el JSON pesa ${cociente}x el binario y CA-10 exige al menos ${COCIENTE_MINIMO}x"

  printf '  OK   %-22s binario %s B  JSON %s B  cociente %sx\n' \
    "tamanos" "$binario" "$json" "$cociente"
}

comprobar_autorizacion() {
  local analista="$1"
  local operativo="$2"
  local estado

  estado="$(pedir_api "${BASE_API}${RUTA}" "")"
  [ "${estado% *}" = "401" ] || fallar "sin token el api respondio HTTP ${estado% *} y se esperaba 401"
  grep -qi 'www-authenticate: *Bearer realm="karisma"' "$CABECERAS" \
    || fallar "el 401 no lleva el reto Bearer del portal"
  grep -qi 'scope="analista"' "$CABECERAS" \
    || fallar "el reto no nombra el scope que exige la ruta"

  estado="$(pedir_api "${BASE_API}${RUTA}" "$operativo")"
  [ "${estado% *}" = "403" ] \
    || fallar "operativo recibio HTTP ${estado% *} y la matriz exige 403"
  grep -q 'permisos_insuficientes' "$CUERPO" \
    || fallar "el 403 no lleva el codigo estable permisos_insuficientes"

  estado="$(pedir_api "${BASE_API}${RUTA}" "$analista")"
  [ "${estado% *}" = "200" ] || fallar "analista recibio HTTP ${estado% *} y se esperaba 200"

  printf '  OK   %-22s 401 sin token, 403 con operativo, 200 con analista\n' "autorizacion"
}

comprobar_proxy() {
  local rol="$1"
  local esperado="$2"
  local estado

  rm -f "$GALLETAS"
  estado="$(curl -sS -o "$CUERPO" -c "$GALLETAS" -w '%{http_code}' --max-time 20 \
    -X POST -H 'Content-Type: application/json' -d "{\"rol\":\"${rol}\"}" \
    "${BASE_WEB}/api/auth/demo")" || fallar "sin respuesta del proxy al acunar ${rol}"
  [ "$estado" = "200" ] || fallar "el proxy respondio HTTP ${estado} al acunar la sesion de ${rol}"

  estado="$(curl -sS -o "${TEMPORAL}/proxy.bin" -b "$GALLETAS" -w '%{http_code}' \
    --max-time 60 "${BASE_WEB}${RUTA}?${CONSULTA_COMPARABLE}")" \
    || fallar "sin respuesta del proxy en ${RUTA}"
  [ "$estado" = "$esperado" ] \
    || fallar "por el proxy, ${rol} recibio HTTP ${estado} y se esperaba ${esperado}"
}

comprobar_integridad() {
  local token="$1"
  local del_api del_proxy

  pedir_api "${BASE_API}${RUTA}?${CONSULTA_COMPARABLE}" "$token" >/dev/null
  cp "$CUERPO" "${TEMPORAL}/api.bin"

  comprobar_proxy "analista" "200"
  del_api="$(sha_de "${TEMPORAL}/api.bin")"
  del_proxy="$(sha_de "${TEMPORAL}/proxy.bin")"

  [ "$del_api" = "$del_proxy" ] \
    || fallar "el proxy devolvio un cuerpo distinto: ${del_api} contra ${del_proxy}"

  comprobar_proxy "operativo" "403"

  printf '  OK   %-22s sha256 identico por el api y por el proxy, y 403 por los dos\n' \
    "integridad del proxy"
}

comprobar_cache() {
  local token="$1"
  local primero segundo estado

  pedir_api "${BASE_API}${RUTA}?${CONSULTA_COMPARABLE}" "$token" >/dev/null
  primero="$(cabecera 'etag')"
  [ -n "$primero" ] || fallar "la respuesta no lleva ETag"

  pedir_api "${BASE_API}${RUTA}?${CONSULTA_COMPARABLE}" "$token" >/dev/null
  segundo="$(cabecera 'etag')"
  [ "$primero" = "$segundo" ] || fallar "el ETag cambia entre dos peticiones iguales"

  estado="$(curl -sS -o /dev/null -D "$CABECERAS" -w '%{http_code}' --max-time 30 \
    -H "Authorization: Bearer ${token}" -H "If-None-Match: ${primero}" \
    "${BASE_API}${RUTA}?${CONSULTA_COMPARABLE}")" || fallar "sin respuesta condicional"
  [ "$estado" = "304" ] || fallar "la peticion condicional respondio HTTP ${estado} y se esperaba 304"

  printf '  OK   %-22s ETag estable %s y 304 con If-None-Match\n' "cache" "$primero"
}

main() {
  command -v curl >/dev/null 2>&1 || fallar "falta curl en el PATH"
  command -v sha256sum >/dev/null 2>&1 || fallar "falta sha256sum en el PATH"
  command -v awk >/dev/null 2>&1 || fallar "falta awk en el PATH"

  printf '\nSmoke de la serie del tablero (US-025)\n'
  printf '  api %s   web %s\n\n' "$BASE_API" "$BASE_WEB"

  esperar_a "${BASE_API}/health" "el api"
  esperar_a "${BASE_WEB}/" "el frontend"

  local analista operativo
  analista="$(token_de analista)"
  operativo="$(token_de operativo)"

  comprobar_carga_completa "$analista"
  comprobar_tamanos "$analista"
  comprobar_autorizacion "$analista" "$operativo"
  comprobar_integridad "$analista"
  comprobar_cache "$analista"

  printf '\n  VEREDICTO  la serie se sirve entera, pesa lo declarado y decide igual por los dos caminos\n\n'
}

main "$@"
