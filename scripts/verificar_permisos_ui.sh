#!/bin/sh
# ---------------------------------------------------------------------------
#  US-017 - el mapa de permisos del portal no puede divergir del backend.
#
#  La matriz de permisos vive en backend/app/core/permissions.py y en ningun
#  otro sitio. El frontend consume una PROYECCION de esa matriz sobre el mapa
#  de sitio de la Actividad 3, y esa proyeccion es un archivo generado:
#  frontend/app/utils/permisos.generated.ts.
#
#  Este guion comprueba las dos cosas que hacen cierta esa frase:
#
#    1. Diferencia: regenerar el archivo con el registro de hoy no cambia lo
#       que hay en disco. Atrapa las dos formas del mismo defecto -editar el
#       archivo generado a mano, o cambiar un scope en el backend y no
#       regenerar-, que es el defecto numero uno de la auditoria del lote
#       anterior.
#    2. Idempotencia: dos corridas seguidas dejan el archivo byte a byte igual.
#       Un generador que ordena por un conjunto de Python produce un archivo
#       distinto en cada corrida y convierte el punto 1 en ruido.
#
#  La tercera barrera -que el mapa coincida endpoint por endpoint con
#  docs/security.md- no esta aqui: vive en frontend/test/permisos.spec.ts,
#  para que corra en el gate diario y no solo en el del viernes.
#
#  POSIX sh, sin argumentos y sin modos.
# ---------------------------------------------------------------------------

set -eu

RAIZ=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
GENERADOR="$RAIZ/scripts/generar_permisos_ui.py"
DESTINO="frontend/app/utils/permisos.generated.ts"

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

echo "Verificacion del mapa de permisos de la interfaz (US-017)"
echo ""

if [ ! -f "$GENERADOR" ]; then
    echo "FALLA: falta $GENERADOR." >&2
    exit 1
fi

POETRY_CMD="poetry"
if ! command -v poetry >/dev/null 2>&1; then
    if command -v poetry.exe >/dev/null 2>&1; then
        POETRY_CMD="poetry.exe"
    else
        echo "FALLA: poetry no esta en el PATH; el generador no se puede correr." >&2
        exit 1
    fi
fi

# --- 1. Regenerar no cambia lo que hay en disco ----------------------------
echo "1. El archivo generado esta al dia"
if ! (cd "$RAIZ" && "$POETRY_CMD" -P backend run python scripts/generar_permisos_ui.py >/dev/null); then
    echo "FALLA: el generador termino con error. Corre 'make permisos-ui' y lee su salida." >&2
    exit 1
fi

if git -C "$RAIZ" diff --exit-code -- "$DESTINO" >/dev/null 2>&1; then
    marcar OK "sin diferencias" "$DESTINO coincide con el registro de hoy"
else
    marcar FALLA "hay diferencias" \
        "$DESTINO se edito a mano o el backend cambio: corre 'make permisos-ui' y commitea"
fi

# --- 2. Dos corridas seguidas producen el mismo archivo --------------------
echo ""
echo "2. Idempotencia del generador"
primera=$(huella "$RAIZ/$DESTINO")
if (cd "$RAIZ" && "$POETRY_CMD" -P backend run python scripts/generar_permisos_ui.py >/dev/null); then
    if [ "$primera" = "$(huella "$RAIZ/$DESTINO")" ]; then
        marcar OK "dos corridas seguidas" "el archivo queda byte a byte igual"
    else
        marcar FALLA "dos corridas seguidas" "la segunda corrida escribio algo distinto"
    fi
else
    marcar FALLA "segunda corrida" "el emisor termino con error"
fi

# --- 3. La cabecera declara que es generado --------------------------------
echo ""
echo "3. El archivo se declara generado"
if grep -q 'GENERATED FILE - do not edit by hand' "$RAIZ/$DESTINO"; then
    marcar OK "cabecera" "declara que nadie lo edita a mano"
else
    marcar FALLA "cabecera" "perdio la advertencia de archivo generado"
fi

# --- Veredicto --------------------------------------------------------------
echo ""
if [ "$fallos" -gt 0 ]; then
    echo "FALLA: $fallos comprobacion(es) del mapa de permisos no cumplen." >&2
    exit 1
fi

echo "Mapa de permisos en verde: una sola fuente y una sola direccion de derivacion."
