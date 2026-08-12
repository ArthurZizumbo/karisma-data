#!/usr/bin/env bash
# ---------------------------------------------------------------------------
#  Verificacion de los cuatro espacios de trabajo de US-027 - Karisma Data.
#
#  Abre una sesion de demostracion por cada uno de los cuatro perfiles, pide la
#  pantalla principal que le corresponde y comprueba en el HTML servido que sea
#  la composicion esperada. Cuatro perfiles, un solo comando: es lo que sostiene
#  el criterio "las tres composiciones se alcanzan sin tres accesos a mano".
#
#  Por que sin navegador. Playwright no esta instalado y meterlo en una US de un
#  punto seria alcance que nadie pidio. Lo que hay que garantizar es que las
#  cuatro pantallas se sirven ya compuestas -en SSR, antes del primer byte de
#  HTML- y eso se ve en el cuerpo de la respuesta. Cuando US-UX-07 instale el
#  navegador para las figuras del informe, su guion son estos mismos cuatro
#  pasos con un page.screenshot() al final, asi que este archivo queda como su
#  especificacion ejecutable y como comprobacion de humo cuando no hay navegador.
#
#  Depende de POST /api/auth/demo, que es publica por diseno (US-015). Si esa
#  puerta esta apagada el guion falla ruidosamente y dice por que: no se simula
#  una sesion que el entorno no puede acunar.
#
#  Uso, con el entorno ya levantado por "make dev" en otra terminal:
#      bash scripts/capturar_espacios.sh
#
#  Variables opcionales:
#      BASE_WEB       destino del frontend  (por defecto http://localhost:3000)
#      ESPERA_MAXIMA  segundos de espera a que el servicio responda (60)
#
#  Sale distinto de cero al primer fallo: no acumula errores ni los resume.
# ---------------------------------------------------------------------------

set -euo pipefail

BASE_WEB="${BASE_WEB:-http://localhost:3000}"
ESPERA_MAXIMA="${ESPERA_MAXIMA:-60}"

# Los cuatro espacios, en el orden del contrato de identidad:
#   rol | pantalla principal | composicion que el HTML debe declarar
#
# El administrador es el unico que no aterriza en /inicio. Su fila comprueba dos
# cosas de una vez: que entra a /administracion, y que si abre /inicio a mano
# recibe la composicion operativa, que es la mas general.
ESPACIOS=(
  "operativo|/inicio|operativo"
  "analista|/inicio|analista"
  "directivo|/inicio|directivo"
  "admin|/administracion|"
)

# Comprobacion extra del quinto caso: el admin que abre /inicio a mano.
RUTA_INICIO="/inicio"
COMPOSICION_DEL_ADMIN="operativo"

# Atributo que la franja de alcance imprime en toda ruta. Es contrato: sin el,
# una captura de pantalla podria leerse como un sistema real.
MARCA_FRANJA="data-franja-alcance"

# Marca que el layout del portal imprime cuando el perfil no alcanza la ruta.
# Un espacio verificado no puede llevarla: significaria que el guion dio por
# buena una pantalla que en realidad es una puerta cerrada.
MARCA_SIN_PERMISO='data-estado="sin-permiso"'

CUERPO=""
GALLETAS=""

limpiar() {
  # El tarro lleva un JWT valido durante media hora: se borra pase lo que pase.
  local temporal
  for temporal in "$CUERPO" "$GALLETAS"; do
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
  local transcurrido=0

  until curl -sS -o /dev/null --max-time 5 "${BASE_WEB}/" 2>/dev/null; do
    if [ "$transcurrido" -ge "$ESPERA_MAXIMA" ]; then
      fallar "el servicio web no respondio en ${ESPERA_MAXIMA} s (${BASE_WEB}). Levanta el entorno con make dev."
    fi
    transcurrido=$((transcurrido + 2))
    sleep 2
  done
}

acunar_sesion() {
  # $1: rol
  local rol="$1"
  local url="${BASE_WEB}/api/auth/demo"
  local codigo

  if ! codigo="$(curl -sS -o "$CUERPO" -c "$GALLETAS" -w '%{http_code}' --max-time 20 \
      -X POST -H 'Content-Type: application/json' \
      -d "{\"rol\":\"${rol}\"}" "$url")"; then
    fallar "sin respuesta de $url"
  fi

  if [ "$codigo" = "404" ]; then
    fallar "DEMO_LOGIN_ENABLED esta apagada en este entorno: sin la puerta de demostracion no se puede acunar la sesion de ${rol} y ninguno de los cuatro espacios es verificable"
  fi

  if [ "$codigo" != "200" ]; then
    fallar "$url respondio HTTP ${codigo} al acunar la sesion de ${rol} y se esperaba 200"
  fi
}

pedir_pantalla() {
  # $1: ruta
  local ruta="$1"
  local codigo

  if ! codigo="$(curl -sS -o "$CUERPO" -b "$GALLETAS" -w '%{http_code}' --max-time 20 \
      "${BASE_WEB}${ruta}")"; then
    fallar "sin respuesta de ${BASE_WEB}${ruta}"
  fi

  if [ "$codigo" != "200" ]; then
    fallar "${ruta} respondio HTTP ${codigo} y se esperaba 200"
  fi

  grep -q "$MARCA_FRANJA" "$CUERPO" \
    || fallar "${ruta} llego sin ${MARCA_FRANJA}: la captura podria leerse como un sistema real"

  if grep -q "$MARCA_SIN_PERMISO" "$CUERPO"; then
    fallar "${ruta} devolvio el estado sin permiso: el espacio no es alcanzable por su propio perfil"
  fi
}

comprobar_composicion() {
  # $1: ruta  $2: composicion esperada
  local ruta="$1"
  local composicion="$2"

  grep -q "data-espacio=\"${composicion}\"" "$CUERPO" \
    || fallar "${ruta} no declara data-espacio=\"${composicion}\" en el HTML servido: o la composicion es otra, o se resolvio despues de hidratar y la captura del informe saldria vacia"
}

main() {
  command -v curl >/dev/null 2>&1 || fallar "falta curl en el PATH"

  CUERPO="$(mktemp)"
  GALLETAS="$(mktemp)"

  printf 'Espacios de trabajo de US-027 contra %s\n\n' "$BASE_WEB"

  esperar_servicio

  local fila rol ruta composicion verificados=0
  for fila in "${ESPACIOS[@]}"; do
    IFS='|' read -r rol ruta composicion <<< "$fila"

    acunar_sesion "$rol"
    pedir_pantalla "$ruta"

    if [ -n "$composicion" ]; then
      comprobar_composicion "$ruta" "$composicion"
      printf '  OK   %-10s %-16s composicion %s\n' "$rol" "$ruta" "$composicion"
    else
      # El administrador no compone /inicio: su espacio es otra pantalla, y lo
      # que se comprueba es que aterriza en ella y que abrirla no le cierra la
      # puerta en la cara.
      printf '  OK   %-10s %-16s pantalla propia del perfil\n' "$rol" "$ruta"
    fi

    verificados=$((verificados + 1))
  done

  # Quinto caso, con la sesion de administracion todavia en el tarro: abrir
  # /inicio a mano da la composicion operativa. Es la unica manera de ver que el
  # respaldo del contrato existe de verdad y no solo en una prueba unitaria.
  pedir_pantalla "$RUTA_INICIO"
  comprobar_composicion "$RUTA_INICIO" "$COMPOSICION_DEL_ADMIN"
  printf '  OK   %-10s %-16s recae en la composicion %s\n' \
    "admin" "$RUTA_INICIO" "$COMPOSICION_DEL_ADMIN"

  printf '\n%s/%s espacios verificados\n' "$verificados" "${#ESPACIOS[@]}"
}

main "$@"
