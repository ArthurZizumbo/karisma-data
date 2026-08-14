#!/bin/sh
# ---------------------------------------------------------------------------
#  US-002 - CA-3: Node 22 fijado en las cuatro puertas por las que entra.
#
#  Solo una de las cuatro ACTUA (devEngines descarga el runtime y guarda su
#  checksum en el candado); las otras tres declaran. Se comprueban las cuatro
#  porque cada una atiende a un lector distinto -el humano, pnpm, Docker- y sin
#  esta comprobacion pueden contradecirse en silencio.
#
#  POSIX sh a proposito: corre igual en Git Bash de Windows, en la imagen de
#  Compose y en el runner de GitHub Actions cuando llegue US-004.
#  Sin argumentos y sin modos: un verificador con modos es un verificador que
#  alguien va a correr en el modo laxo.
# ---------------------------------------------------------------------------

set -eu

MAYOR_ESPERADO=22

# Piso de la linea 22, elevado el 10-ago-2026 al entrar @nuxtjs/i18n. Su cadena
# arrastra oxc-parser, cuyo binario nativo declara "engines: ^20.19.0 ||
# >=22.12.0". pnpm omite una dependencia OPCIONAL cuyo engines no cabe en el
# rango que declara el proyecto, asi que con ">=22.0.0" el binario no se
# instalaba y "nuxt prepare", "nuxt typecheck" y "nuxt build" morian con
# "Cannot find module ./parser.<plataforma>.node". Ocurre igual en Linux, de
# modo que la imagen de Docker se veria afectada tambien. .nvmrc y el Dockerfile
# siguen nombrando la linea, no el parche: cualquier 22.x vigente la cumple.
MINIMO_ESPERADO=22.12.0

RAIZ=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
FRONTEND="$RAIZ/frontend"

aciertos=0
fallos=0

informar() {
    # $1: veredicto (OK|FALLA)  $2: puerta  $3: detalle
    printf '  [%-5s] %-22s %s\n' "$1" "$2" "$3"
}

comprobar() {
    # $1: puerta  $2: valor observado  $3: valor esperado
    if [ "$2" = "$3" ]; then
        informar OK "$1" "$2"
        aciertos=$((aciertos + 1))
    else
        informar FALLA "$1" "se esperaba '$3' y se leyo '$2'"
        fallos=$((fallos + 1))
    fi
}

echo "Verificacion de pines de Node (US-002, CA-3)"
echo ""

# --- Puerta 1: .nvmrc ------------------------------------------------------
if [ -f "$FRONTEND/.nvmrc" ]; then
    nvmrc=$(tr -d ' \t\r\n' < "$FRONTEND/.nvmrc")
else
    nvmrc="<archivo ausente>"
fi
comprobar ".nvmrc" "$nvmrc" "$MAYOR_ESPERADO"

# --- Puertas 2 y 3: package.json -------------------------------------------
# Se extraen con sed para no exigir jq: este script corre tambien dentro de la
# imagen de Compose, donde jq no esta instalado.
if [ -f "$FRONTEND/package.json" ]; then
    # Se aplanan los saltos de linea pero NO los espacios: el valor de
    # engines.node lleva uno dentro (">=22.12.0 <23.0.0") y borrarlo haria
    # fallar la comparacion contra un manifiesto correcto.
    compacto=$(tr '\n\r\t' '   ' < "$FRONTEND/package.json" | sed 's/  */ /g')
    engines=$(printf '%s' "$compacto" \
        | sed -n 's/.*"engines" *: *{ *"node" *: *"\([^"]*\)".*/\1/p')
    dev_version=$(printf '%s' "$compacto" \
        | sed -n 's/.*"devEngines" *: *{ *"runtime" *: *{[^}]*"version" *: *"\([^"]*\)".*/\1/p')
    dev_on_fail=$(printf '%s' "$compacto" \
        | sed -n 's/.*"devEngines" *: *{ *"runtime" *: *{[^}]*"onFail" *: *"\([^"]*\)".*/\1/p')
else
    engines=""
    dev_version=""
    dev_on_fail=""
fi
comprobar "engines.node" "${engines:-<ausente>}" ">=$MINIMO_ESPERADO <$((MAYOR_ESPERADO + 1)).0.0"
comprobar "devEngines.runtime" "${dev_version:-<ausente>}" "^$MINIMO_ESPERADO"

# --- Puerta 4: Dockerfile, en TODAS sus etapas ------------------------------
# Se leen todas las lineas FROM y no solo la primera: una imagen de ejecucion
# con otra version anularia el pin justo donde importa, que es produccion.
if [ -f "$FRONTEND/Dockerfile" ]; then
    etapas=$(sed -n 's/^FROM[[:space:]]\{1,\}node:\([^[:space:]]*\).*/\1/p' "$FRONTEND/Dockerfile")
else
    etapas=""
fi
if [ -z "$etapas" ]; then
    informar FALLA "Dockerfile" "sin ninguna etapa FROM node:*"
    fallos=$((fallos + 1))
else
    numero=0
    for etapa in $etapas; do
        numero=$((numero + 1))
        comprobar "Dockerfile etapa $numero" "$etapa" "$MAYOR_ESPERADO-slim"
    done
fi

# --- devEngines debe poder actuar, no solo declarar -------------------------
echo ""
if [ "$dev_on_fail" = "download" ]; then
    informar OK "devEngines.onFail" "download"
else
    informar FALLA "devEngines.onFail" "se esperaba 'download' y se leyo '${dev_on_fail:-<ausente>}'"
    fallos=$((fallos + 1))
fi

# --- Veredicto --------------------------------------------------------------
total=$((aciertos + fallos))
echo ""
echo "Resultado: $aciertos/$total en Node $MAYOR_ESPERADO"

if [ "$fallos" -gt 0 ]; then
    echo "FALLA: $fallos comprobacion(es) no cumplen CA-3." >&2
    exit 1
fi

echo "CA-3 en verde: las cuatro puertas declaran Node $MAYOR_ESPERADO y no se contradicen."
