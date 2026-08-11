#!/bin/sh
# ---------------------------------------------------------------------------
#  US-UX-09 - los tokens de diseno no pueden divergir del documento del curso.
#
#  La guia de estilos de la Actividad 4 solo vale si la aplicacion y el PDF
#  salen del mismo archivo. Este script comprueba las cuatro condiciones que
#  hacen cierta esa afirmacion:
#
#    1. Anclas: los once colores versionados en la Actividad 1 conservan su
#       valor. main_a1, main_a2 y main_a3 estan entregados y compilan contra
#       ellos: cambiar uno invalida tres entregas cerradas.
#    2. Inventario: uxdoc.sty declara los 37 nombres de color de la guia y el
#       manifiesto declara los 37 tokens.
#    3. Idempotencia: dos corridas seguidas del generador dejan las cuatro
#       salidas byte a byte iguales, y ninguna difiere de lo que hay en disco.
#    4. Ningun color escrito a mano fuera de uxdoc.sty, y una sola version.
#
#  La lista de anclas de abajo esta escrita a proposito: un invariante que se
#  lee del mismo archivo que vigila no comprueba nada.
#
#  POSIX sh, sin argumentos y sin modos.
# ---------------------------------------------------------------------------

set -eu

RAIZ=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
FUENTE="$RAIZ/docs/entregables/estilo/uxdoc.sty"
GENERADOR="$RAIZ/docs/entregables/generar_tokens_a4.py"
CSS="$RAIZ/frontend/app/assets/css/main.css"
TS="$RAIZ/frontend/app/utils/tokens.generated.ts"
TEX="$RAIZ/docs/entregables/estilo/a4_tokens.tex"
JSON="$RAIZ/docs/entregables/datos/a4_tokens.json"

VERSION_ESPERADA="v1.0"
FECHA_ESPERADA="2026-08-16"
NOMBRES_ESPERADOS=37

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

echo "Verificacion de los tokens de diseno (US-UX-09)"
echo ""

for archivo in "$FUENTE" "$GENERADOR" "$CSS" "$TS" "$TEX" "$JSON"; do
    if [ ! -f "$archivo" ]; then
        echo "FALLA: falta $archivo. Corre 'make tokens' antes de verificar." >&2
        exit 1
    fi
done

# --- 1. Las once anclas conservan su valor ---------------------------------
echo "1. Anclas versionadas en la Actividad 1"
while read -r nombre valor; do
    [ -n "$nombre" ] || continue
    if grep -q "definecolor{$nombre}{HTML}{$valor}" "$FUENTE"; then
        marcar OK "$nombre" "$valor intacto"
    else
        leido=$(sed -n "s/.*definecolor{$nombre}{HTML}{\([0-9A-Fa-f]*\)}.*/\1/p" "$FUENTE")
        marcar FALLA "$nombre" "se esperaba $valor y se leyo '${leido:-<ausente>}'"
    fi
done <<'ANCLAS'
uxnavy 1F4D78
uxblue 2563EB
uxsky 3B82F6
uxpale B8CCE4
uxamber F97316
uxsurface F8FAFC
uxink 1E293B
uxmuted 64748B
uxline CBD5E1
uxrow EEF3FA
uxgreen 166534
ANCLAS

# --- 2. Inventario de nombres y de tokens ----------------------------------
echo ""
echo "2. Inventario de color"
declarados=$(grep -c 'definecolor{' "$FUENTE" || true)
alias=$(grep -c 'colorlet{' "$FUENTE" || true)
nombres=$((declarados + alias))
if [ "$nombres" -eq "$NOMBRES_ESPERADOS" ]; then
    marcar OK "nombres en uxdoc.sty" "$declarados definecolor + $alias colorlet = $nombres"
else
    marcar FALLA "nombres en uxdoc.sty" "se esperaban $NOMBRES_ESPERADOS y hay $nombres"
fi

tokens=$(grep -c '"nombre_tex"' "$JSON" || true)
if [ "$tokens" -eq "$NOMBRES_ESPERADOS" ]; then
    marcar OK "tokens en el manifiesto" "$tokens"
else
    marcar FALLA "tokens en el manifiesto" "se esperaban $NOMBRES_ESPERADOS y hay $tokens"
fi

# --- 3. Idempotencia --------------------------------------------------------
echo ""
echo "3. Idempotencia del generador"
if command -v poetry >/dev/null 2>&1; then
    # El orden importa: primero se pregunta si el arbol de trabajo esta al dia
    # -que es lo que rompe el "git diff --exit-code" de CA-6- y solo despues se
    # regenera dos veces para comparar una corrida con la siguiente. Al reves,
    # la primera regeneracion borraria la prueba.
    if poetry -P "$RAIZ/backend" run python "$GENERADOR" --verificar >/dev/null 2>&1; then
        marcar OK "salidas en disco" "coinciden con lo que uxdoc.sty produce hoy"
    else
        marcar FALLA "salidas en disco" "alguna difiere: corre 'make tokens' y commitea"
    fi

    if poetry -P "$RAIZ/backend" run python "$GENERADOR" >/dev/null 2>&1; then
        primera_css=$(huella "$CSS")
        primera_ts=$(huella "$TS")
        primera_tex=$(huella "$TEX")
        primera_json=$(huella "$JSON")
        if poetry -P "$RAIZ/backend" run python "$GENERADOR" >/dev/null 2>&1; then
            cambiadas=0
            for par in "main.css:$primera_css:$CSS" \
                "tokens.generated.ts:$primera_ts:$TS" \
                "a4_tokens.tex:$primera_tex:$TEX" \
                "a4_tokens.json:$primera_json:$JSON"; do
                clave=${par%%:*}
                resto=${par#*:}
                previa=${resto%%:*}
                archivo=${resto#*:}
                if [ "$previa" != "$(huella "$archivo")" ]; then
                    marcar FALLA "$clave" "la segunda corrida escribio algo distinto"
                    cambiadas=$((cambiadas + 1))
                fi
            done
            if [ "$cambiadas" -eq 0 ]; then
                marcar OK "dos corridas seguidas" "las cuatro salidas quedan byte a byte iguales"
            fi
        else
            marcar FALLA "segunda corrida" "el emisor termino con error"
        fi
    else
        marcar FALLA "primera corrida" "el emisor termino con error"
    fi
else
    marcar FALLA "poetry" "no esta en el PATH: la idempotencia no se pudo comprobar"
fi

# --- 4. Ningun color escrito a mano ----------------------------------------
echo ""
echo "4. Ningun color escrito a mano fuera de uxdoc.sty"
vigilados="$GENERADOR"
for candidato in \
    "$RAIZ"/docs/entregables/contenido/a4_*.tex \
    "$RAIZ/frontend/app/pages/guia.vue" \
    "$RAIZ"/frontend/app/components/guia/*.vue; do
    [ -f "$candidato" ] && vigilados="$vigilados $candidato"
done
# shellcheck disable=SC2086
sueltos=$(grep -lE '#[0-9A-Fa-f]{6}' $vigilados 2>/dev/null || true)
if [ -z "$sueltos" ]; then
    revisados=$(echo "$vigilados" | wc -w | tr -d ' ')
    marcar OK "archivos revisados" "$revisados sin ningun hexadecimal"
else
    for archivo in $sueltos; do
        marcar FALLA "hexadecimal a mano" "${archivo#"$RAIZ/"}"
    done
fi

# --- 5. Una sola version ----------------------------------------------------
echo ""
echo "5. Version de la guia en las tres salidas"
for archivo in "$CSS" "$TS" "$JSON"; do
    etiqueta=$(basename "$archivo")
    if grep -q "$VERSION_ESPERADA" "$archivo" && grep -q "$FECHA_ESPERADA" "$archivo"; then
        marcar OK "$etiqueta" "$VERSION_ESPERADA - $FECHA_ESPERADA"
    else
        marcar FALLA "$etiqueta" "no declara $VERSION_ESPERADA - $FECHA_ESPERADA"
    fi
done
GUIA="$RAIZ/docs/entregables/contenido/a4_03_guia_estilos.tex"
if [ -f "$GUIA" ]; then
    if grep -q "$VERSION_ESPERADA" "$GUIA"; then
        marcar OK "a4_03_guia_estilos.tex" "declara $VERSION_ESPERADA"
    else
        marcar FALLA "a4_03_guia_estilos.tex" "no declara $VERSION_ESPERADA"
    fi
else
    printf '  [nota  ] %-26s %s\n' "a4_03_guia_estilos.tex" \
        "todavia no existe: lo escribe la ola C"
fi

# --- Veredicto --------------------------------------------------------------
echo ""
if [ "$fallos" -gt 0 ]; then
    echo "FALLA: $fallos comprobacion(es) de los tokens no cumplen." >&2
    exit 1
fi

echo "Tokens en verde: una sola fuente, 37 nombres, salidas idempotentes."
