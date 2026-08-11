#!/usr/bin/env bash
# ---------------------------------------------------------------------------
#  Smoke de extremo a extremo de US-001 - Karisma Data.
#
#  Recorre las diez rutas publicas del portal contra el servicio web y
#  despues consulta la sonda del api. Cubre en una sola pasada CA-4 (las rutas
#  responden), CA-7 (la franja de alcance esta en TODAS, incluidas / y /acceso)
#  y CA-8 (/health responde).
#
#  Desde US-015 tambien ENTRA, y esa parte no es decoracion. Las 322 pruebas del
#  frontend doblan $fetch y el evento de h3: ninguna arranca un servidor ni abre
#  un socket, asi que miden que cada pieza hace lo suyo y no pueden medir que
#  esten conectadas. El dia que se programo la autenticacion, un NUXT_API_BASE
#  apuntando al nombre de servicio de Compose dejaba el portal entero en pie
#  -las diez rutas en 200, esta seccion en verde- y hundia el login con un error
#  de servidor. La cobertura era del 96 % y del 80 %, y ninguna cifra lo vio.
#
#  Lo que sigue cierra esa clase de fallo: cableado, variables de entorno, un
#  proxy que no llega, una cookie que pierde un atributo. Nada de eso puede
#  quedar en verde a partir de aqui.
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

# Las diez rutas: el indice, las ocho del contrato de navegacion de A3 y la
# guia de estilos de A4, que no es rama del mapa ni prototipo y por eso vive
# fuera de RUTAS_CONTRATO. Aqui si entra: responde 200 y lleva franja.
RUTAS=(
  "/"
  "/guia"
  "/acceso"
  "/inicio"
  "/exploracion"
  "/exploracion/tableros"
  "/exploracion/exportar"
  "/gobierno"
  "/asistente"
  "/administracion"
)

TOTAL_ESPERADO=10

# Nombre y vida de la cookie de sesion (US-015). Los fija frontend/server/utils/
# sesion.ts y el backend firma el token con la misma duracion; que las dos mitades
# sigan de acuerdo es justo lo que esta seccion comprueba de extremo a extremo.
COOKIE_SESION="karisma_sesion"
VIDA_COOKIE=1800

# Rol con el que se entra por la puerta de demostracion, y el usuario sembrado
# que le corresponde en la migracion create_app_user.
ROL_DEMO="analista"
USUARIO_DEMO="dhernandez"

CUERPO=""
CABECERAS=""
GALLETAS=""

limpiar() {
  # El tarro de galletas lleva un JWT valido durante media hora: se borra pase lo
  # que pase, igual que el cuerpo y las cabeceras.
  local temporal
  for temporal in "$CUERPO" "$CABECERAS" "$GALLETAS"; do
    if [ -n "$temporal" ] && [ -f "$temporal" ]; then
      rm -f "$temporal"
    fi
  done
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

# ---------------------------------------------------------------------------
#  Sesion (US-015): entrar de verdad, no solo comprobar que la pantalla exista.
# ---------------------------------------------------------------------------

# Lee la linea Set-Cookie de la sesion del volcado de cabeceras.
# Del volcado y no del tarro de galletas a proposito: curl no guarda HttpOnly ni
# SameSite al escribir el tarro, y son justo los dos atributos que sostienen
# CA-5 y CA-18.
linea_de_cookie() {
  grep -i "^set-cookie: ${COOKIE_SESION}=" "$CABECERAS" | tr -d '\r' | head -n 1
}

comprobar_entrada_de_demostracion() {
  local url="${BASE_WEB}/api/auth/demo"
  local codigo cookie usuario

  if ! codigo="$(curl -sS -o "$CUERPO" -D "$CABECERAS" -c "$GALLETAS" \
      -w '%{http_code}' --max-time 20 \
      -X POST -H 'Content-Type: application/json' \
      -d "{\"rol\":\"${ROL_DEMO}\"}" "$url")"; then
    fallar "sin respuesta de $url"
  fi

  if [ "$codigo" = "404" ]; then
    # Que la puerta este apagada es una decision de despliegue legitima, asi que
    # no se falla. Pero se dice: en ese caso el resto de esta seccion no corre y
    # el verde final cubre menos de lo que parece.
    printf '  OMIT %-24s DEMO_LOGIN_ENABLED apagada: la ruta no existe\n' "/api/auth/demo"
    return 1
  fi

  # Este es el codigo que delata un fallo de cableado. Un 502 aqui, con las diez
  # rutas en 200 mas arriba, es exactamente la forma que tuvo el defecto de
  # US-015: el portal entero en pie y la API inalcanzable desde el proceso que
  # sirve el frontend.
  if [ "$codigo" != "200" ]; then
    fallar "$url respondio HTTP ${codigo} y se esperaba 200. Un 502 aqui casi siempre significa que NUXT_API_BASE no alcanza al backend desde el proceso que sirve el frontend"
  fi

  if grep -q 'access_token' "$CUERPO"; then
    fallar "la respuesta de $url lleva el token al navegador, y CA-5 dice que vive solo en la cookie httpOnly"
  fi

  usuario="$(sed -n 's/.*"usuario"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' "$CUERPO")"
  if [ "$usuario" != "$USUARIO_DEMO" ]; then
    fallar "el rol ${ROL_DEMO} entro como '${usuario}' y la migracion siembra a '${USUARIO_DEMO}' como su usuario canonico"
  fi

  cookie="$(linea_de_cookie)"
  if [ -z "$cookie" ]; then
    fallar "$url no puso la cookie ${COOKIE_SESION}"
  fi

  printf '%s' "$cookie" | grep -qi 'HttpOnly' \
    || fallar "la cookie ${COOKIE_SESION} salio sin HttpOnly: cualquier XSS se lleva la sesion (CA-5)"
  printf '%s' "$cookie" | grep -qi 'SameSite=Strict' \
    || fallar "la cookie ${COOKIE_SESION} salio sin SameSite=Strict, que es la mitad de navegador de QA-M2 (CA-18)"
  printf '%s' "$cookie" | grep -qi "Max-Age=${VIDA_COOKIE}" \
    || fallar "la cookie ${COOKIE_SESION} no vive ${VIDA_COOKIE} s y dejaria de morir con el token"

  printf '  OK   %-24s HTTP 200   %s entra, cookie httpOnly y estricta\n' "/api/auth/demo" "$usuario"
  return 0
}

comprobar_sesion_viva() {
  local url="${BASE_WEB}/api/auth/me"
  local codigo

  # Sin cabecera Authorization a proposito: la pone el proxy leyendo la cookie.
  # Si esta llamada da 401, el bearer dejo de inyectarse y la sesion entera cae.
  if ! codigo="$(curl -sS -o "$CUERPO" -b "$GALLETAS" -w '%{http_code}' --max-time 20 "$url")"; then
    fallar "sin respuesta de $url"
  fi

  if [ "$codigo" != "200" ]; then
    fallar "$url respondio HTTP ${codigo} con una sesion recien abierta: el proxy no esta convirtiendo la cookie en Bearer (CA-6)"
  fi

  grep -q "\"username\"[[:space:]]*:[[:space:]]*\"${USUARIO_DEMO}\"" "$CUERPO" \
    || fallar "$url no devolvio a ${USUARIO_DEMO}"

  if grep -q 'hashed_password' "$CUERPO"; then
    fallar "$url serializa el hash de la contrasena"
  fi

  printf '  OK   %-24s HTTP 200   la cookie viaja como Bearer\n' "/api/auth/me"
}

comprobar_credencial_rechazada() {
  local url="${BASE_WEB}/api/auth/token"
  local codigo

  # Un usuario que la migracion no siembra. Tiene que dar 401 y no 502: un 502
  # significaria que el backend no responde, y entonces el 401 de un login real
  # tampoco estaria probando nada.
  if ! codigo="$(curl -sS -o "$CUERPO" -w '%{http_code}' --max-time 20 \
      -X POST -H 'Content-Type: application/json' \
      -d '{"usuario":"nadie","contrasena":"tampoco"}' "$url")"; then
    fallar "sin respuesta de $url"
  fi

  if [ "$codigo" != "401" ]; then
    fallar "un usuario inexistente en $url dio HTTP ${codigo} y se esperaba 401 (CA-7)"
  fi

  grep -q 'credenciales_invalidas' "$CUERPO" \
    || fallar "el rechazo de $url no lleva el codigo credenciales_invalidas que la pantalla traduce a su idioma"

  printf '  OK   %-24s HTTP 401   rechazo neutro y tipificado\n' "/api/auth/token"
}

comprobar_alias_del_path() {
  local url="${BASE_WEB}/api/auth%2Fdemo"
  local codigo

  # Regresion de QA-15-01, que estuvo vivo y explotable. h3 enruta sobre el path
  # crudo y uvicorn decodifica una vez, asi que la barra escapada esquivaba el
  # manejador de Nitro, caia al comodin y volvia con un JWT crudo en el cuerpo:
  # fuera de la cookie httpOnly y al alcance de cualquier script de la pagina.
  if ! codigo="$(curl -sS -o "$CUERPO" -w '%{http_code}' --max-time 20 \
      -X POST -H 'Content-Type: application/json' \
      -d '{"rol":"admin"}' "$url")"; then
    fallar "sin respuesta de $url"
  fi

  if [ "$codigo" != "404" ]; then
    fallar "$url respondio HTTP ${codigo} y se esperaba 404: el alias del path vuelve a esquivar la ruta de Nitro (QA-15-01)"
  fi

  if grep -q 'access_token' "$CUERPO"; then
    fallar "$url devolvio un token crudo al navegador: QA-15-01 ha vuelto"
  fi

  printf '  OK   %-24s HTTP 404   el alias no esquiva la cookie\n' "/api/auth%2Fdemo"
}
main() {
  command -v curl >/dev/null 2>&1 || fallar "falta curl en el PATH"

  if [ "${#RUTAS[@]}" -ne "$TOTAL_ESPERADO" ]; then
    fallar "el guion declara ${#RUTAS[@]} rutas y el portal publica ${TOTAL_ESPERADO}"
  fi

  CUERPO="$(mktemp)"
  CABECERAS="$(mktemp)"
  GALLETAS="$(mktemp)"

  printf 'Smoke de US-001 contra %s y %s\n\n' "$BASE_WEB" "$BASE_API"

  esperar_servicio "$BASE_WEB/" "el servicio web"
  esperar_servicio "${BASE_API}/health" "el servicio api"

  local ruta
  for ruta in "${RUTAS[@]}"; do
    comprobar_ruta "$ruta"
  done

  comprobar_salud

  printf '
'

  # La entrada de demostracion decide si el resto tiene sentido: sin token no
  # hay sesion que comprobar. El alias se verifica igual, porque no necesita
  # haber entrado.
  if comprobar_entrada_de_demostracion; then
    comprobar_sesion_viva
  fi
  comprobar_credencial_rechazada
  comprobar_alias_del_path

  printf '
%s/%s rutas, /health y la sesion en verde
' "${#RUTAS[@]}" "$TOTAL_ESPERADO"
}

main "$@"
