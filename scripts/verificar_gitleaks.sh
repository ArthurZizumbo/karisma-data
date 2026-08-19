#!/bin/sh
# ---------------------------------------------------------------------------
#  US-002 - CA-7b: el escaneo de secretos detecta de verdad.
#
#  Un "make check" en verde solo prueba que no se encontro nada. No prueba que
#  el escaneo sea capaz de encontrar algo: una lista de permitidos demasiado
#  ancha, una configuracion mal escrita o un binario que no corre dan el mismo
#  verde silencioso. Este script inyecta un secreto de prueba, exige que gitleaks
#  lo encuentre y limpia el rastro.
#
#  El secreto se compone en tiempo de ejecucion, nunca literal en el archivo:
#  si estuviera entero aqui, este mismo script haria fallar a make check.
#
#  POSIX sh, sin argumentos y sin modos.
# ---------------------------------------------------------------------------

set -eu

RAIZ=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)

# El fixture vive FUERA del arbol de trabajo, en un directorio temporal de
# nombre impredecible. Antes se plantaba en la raiz del repositorio y no estaba
# en .gitignore: si el script moria sin ejecutar el trap -SIGKILL, cierre de la
# terminal, corte de energia- quedaba un token con forma valida a un "git add -A"
# de distancia de un commit. Un ghp_ publicado dispara el escaneo de GitHub y
# obliga a reescribir la rama. Ademas el nombre fijo era predecible: en una
# maquina compartida un tercero podia pre-crearlo como enlace simbolico y la
# redireccion habria escrito sobre el destino.
DIR_FIXTURE=$(mktemp -d)
FIXTURE="$DIR_FIXTURE/fixture.toml"

limpiar() {
    rm -rf "$DIR_FIXTURE"
}
# Se limpia pase lo que pase. Y aunque el trap no llegue a correr, lo que queda
# esta en el directorio temporal del sistema, no en el repositorio.
trap limpiar EXIT INT TERM

echo "Verificacion del escaneo de secretos (US-002, CA-7b)"
echo ""

GITLEAKS_CMD="gitleaks"
if ! command -v gitleaks >/dev/null 2>&1; then
    if command -v gitleaks.exe >/dev/null 2>&1; then
        GITLEAKS_CMD="gitleaks.exe"
    else
        echo "FALLA: gitleaks no esta en el PATH." >&2
        echo "Instalalo con: winget install --id Gitleaks.Gitleaks --exact" >&2
        echo "Tras instalarlo hay que abrir una terminal nueva: winget modifica el PATH" >&2
        echo "persistido y un shell ya abierto conserva el anterior." >&2
        exit 1
    fi
fi

echo "  gitleaks $($GITLEAKS_CMD version) encontrado"

# --- Secreto de prueba ------------------------------------------------------
# Token personal de GitHub con forma valida y cuerpo inventado. Se compone en
# dos mitades para que el patron completo no exista en ningun archivo
# versionado, ni siquiera en este.
#
# Por que este y no una clave de AWS: la configuracion por omision de gitleaks
# ignora las claves de ejemplo de la documentacion de AWS -llevan la palabra
# EXAMPLE- y su regla de AWS pide mas contexto del que da una linea suelta. Un
# fixture que el escaneo ignora por diseno convertiria esta verificacion en el
# mismo teatro que pretende evitar. Se eligio comprobando cuatro familias de
# secreto contra el binario instalado, no de memoria.
prefijo='ghp_'
cuerpo='R7kQm2XvT9pLwZ4nB6dYcF1sA3hJ8uE5oI0G'
{
    echo "# Fixture temporal de scripts/verificar_gitleaks.sh."
    echo "# Si este archivo sobrevive a una ejecucion, borralo: no es un secreto real."
    echo "github_token = \"${prefijo}${cuerpo}\""
} > "$FIXTURE"

echo "  fixture plantado en $(basename "$FIXTURE")"

# --- El escaneo debe encontrarlo -------------------------------------------
# Se apunta al fixture y no al arbol entero: la pregunta es si el escaneo
# detecta, no cuanto tarda en recorrer el repositorio.
if "$GITLEAKS_CMD" dir "$FIXTURE" \
        --config "$RAIZ/.gitleaks.toml" \
        --redact --no-banner --no-color >/dev/null 2>&1; then
    echo ""
    echo "FALLA: gitleaks salio 0 sobre un archivo con un secreto plantado." >&2
    echo "El escaneo no esta detectando. Revisa .gitleaks.toml: una lista de" >&2
    echo "permitidos demasiado ancha convierte make check en un tramite vacio." >&2
    exit 1
fi

echo "  el escaneo lo detecto y salio distinto de 0, como debe"

# --- La excepcion de .env.local sigue siendo legitima ------------------------
# .gitleaks.toml aparta los .env.local del escaneo porque .gitignore los excluye
# y ninguno puede llegar a un commit. Esa entrada es la unica de la lista que
# depende de un hecho externo al archivo de configuracion, y por eso se
# comprueba aqui: el dia que uno de esos archivos deje de estar ignorado, o
# aparezca en el indice, la exclusion pasaria de quitar ruido a esconder una
# credencial real y este guion tiene que ser quien lo diga.
echo ""
echo "  comprobando la excepcion de .env.local"

# El barrido recorre el arbol y no una lista escrita: la pregunta es si CUALQUIER
# .env.local quedo fuera del ignore, y una lista fija solo responde por los dos
# que alguien recordo escribir. `find` corre desde $RAIZ con rutas relativas para
# que un directorio con espacios -habitual en Windows- no parta el resultado.
while IFS= read -r relativo; do
    relativo="${relativo#./}"
    entorno="$RAIZ/$relativo"
    [ -f "$entorno" ] || continue

    if ! git -C "$RAIZ" check-ignore -q "$entorno"; then
        echo ""
        echo "FALLA: $relativo NO esta ignorado por git." >&2
        echo "La lista de permitidos de .gitleaks.toml lo aparta del escaneo dando" >&2
        echo "por hecho que no puede commitearse. Ya no es cierto: o vuelve a" >&2
        echo ".gitignore, o se retira esa entrada de .gitleaks.toml." >&2
        exit 1
    fi

    if [ -n "$(git -C "$RAIZ" ls-files -- "$entorno")" ]; then
        echo ""
        echo "FALLA: $relativo esta en el indice de git." >&2
        echo "Sacalo con 'git rm --cached $relativo' y rota lo que hubiera dentro:" >&2
        echo "un secreto que llego al indice se considera comprometido." >&2
        exit 1
    fi

    echo "    $relativo ignorado y fuera del indice"
done <<EOF
$(cd "$RAIZ" && find . -name '.env.local' -not -path '*/node_modules/*' -not -path './.git/*')
EOF

# --- Y el arbol real debe seguir limpio sin el fixture ----------------------
limpiar
trap - EXIT INT TERM

if ! (cd "$RAIZ" && "$GITLEAKS_CMD" dir . \
        --config .gitleaks.toml \
        --redact --no-banner --no-color >/dev/null 2>&1); then
    echo ""
    echo "FALLA: el arbol de trabajo tiene hallazgos." >&2
    echo "Corre 'make check' para verlos con su ubicacion, ya redactados." >&2
    exit 1
fi

echo "  el arbol de trabajo esta limpio"
echo ""
echo "CA-7b en verde: el escaneo detecta lo que debe y no marca lo que no."
