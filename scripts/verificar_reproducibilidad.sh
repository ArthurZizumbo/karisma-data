#!/bin/sh
# ---------------------------------------------------------------------------
#  US-002 - CA-8: los candados reproducen, no solo existen.
#
#  Un candado que nadie comprueba con instalacion limpia no es un candado, es un
#  archivo. Este script instala desde poetry.lock y pnpm-lock.yaml exigiendo que
#  ninguno de los dos se modifique: si la instalacion los reescribe, el entorno
#  del martes no sera el del domingo y el despliegue construira una imagen
#  distinta de la que se probo.
#
#  POSIX sh, sin argumentos y sin modos.
# ---------------------------------------------------------------------------

set -eu

RAIZ=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
CANDADO_PY="$RAIZ/backend/poetry.lock"
CANDADO_JS="$RAIZ/frontend/pnpm-lock.yaml"

fallos=0

huella() {
    # Huella del contenido, independiente de la fecha de modificacion: lo que
    # importa es si el archivo cambio, no si alguien lo toco.
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

comparar() {
    # $1: etiqueta  $2: ruta  $3: huella previa
    despues=$(huella "$2")
    if [ "$3" = "$despues" ]; then
        printf '  [OK   ] %-24s intacto tras instalar\n' "$1"
    else
        printf '  [FALLA] %-24s la instalacion lo modifico\n' "$1"
        echo "         antes:   $3" >&2
        echo "         despues: $despues" >&2
        fallos=$((fallos + 1))
    fi
}

echo "Verificacion de reproducibilidad de dependencias (US-002, CA-8)"
echo ""

# --- Los candados tienen que existir antes de nada --------------------------
for candado in "$CANDADO_PY" "$CANDADO_JS"; do
    if [ ! -f "$candado" ]; then
        echo "FALLA: falta $candado. Sin candado no hay reproducibilidad que verificar." >&2
        exit 1
    fi
done

antes_py=$(huella "$CANDADO_PY")
antes_js=$(huella "$CANDADO_JS")

# --- Backend: el candado debe bastar para resolver el arbol -----------------
if command -v poetry >/dev/null 2>&1; then
    echo "  instalando backend desde poetry.lock..."
    # --sync elimina lo que sobra: comprueba que el candado describe el entorno
    # entero, no solo que sea compatible con lo que ya hubiera instalado.
    if ! poetry -P "$RAIZ/backend" install --sync --no-interaction >/dev/null 2>&1; then
        echo "  [FALLA] backend                  poetry install --sync fallo" >&2
        fallos=$((fallos + 1))
    fi
    comparar "backend/poetry.lock" "$CANDADO_PY" "$antes_py"
else
    echo "  [FALLA] poetry                   no esta en el PATH" >&2
    fallos=$((fallos + 1))
fi

# --- Frontend: --frozen-lockfile falla si el candado no basta ---------------
if command -v pnpm >/dev/null 2>&1; then
    echo "  instalando frontend desde pnpm-lock.yaml..."
    # --frozen-lockfile aborta en vez de actualizar el candado en silencio, que
    # es exactamente la diferencia entre reproducir y parecerse.
    if ! (cd "$RAIZ/frontend" && pnpm install --frozen-lockfile >/dev/null 2>&1); then
        echo "  [FALLA] frontend                 pnpm install --frozen-lockfile fallo" >&2
        echo "         El candado no describe el manifiesto actual. Regeneralo con" >&2
        echo "         'pnpm install' y revisa el diff antes de commitearlo." >&2
        fallos=$((fallos + 1))
    fi
    comparar "frontend/pnpm-lock.yaml" "$CANDADO_JS" "$antes_js"
else
    echo "  [FALLA] pnpm                     no esta en el PATH" >&2
    fallos=$((fallos + 1))
fi

# --- El runtime fijado tiene que ser el que corre ---------------------------
echo ""
if command -v pnpm >/dev/null 2>&1; then
    version_proyecto=$(cd "$RAIZ/frontend" && pnpm exec node --version 2>/dev/null || echo "<sin resolver>")
    case "$version_proyecto" in
        v22.*)
            printf '  [OK   ] %-24s %s (el host puede correr otra)\n' "runtime del proyecto" "$version_proyecto"
            ;;
        *)
            printf '  [FALLA] %-24s se esperaba v22.* y se leyo %s\n' "runtime del proyecto" "$version_proyecto" >&2
            fallos=$((fallos + 1))
            ;;
    esac
fi

# --- Veredicto --------------------------------------------------------------
echo ""
if [ "$fallos" -gt 0 ]; then
    echo "FALLA: $fallos comprobacion(es) no cumplen CA-8." >&2
    exit 1
fi

echo "CA-8 en verde: los dos candados reproducen sin modificarse."
