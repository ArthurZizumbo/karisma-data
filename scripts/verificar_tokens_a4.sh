#!/bin/sh
# ---------------------------------------------------------------------------
#  US-UX-09 - los tokens de diseno no pueden divergir de su fuente, y ninguna
#  de las dos cadenas puede escribir dentro de la otra.
#
#  Hay DOS cadenas, cada archivo generado tiene UN emisor y las dos versiones
#  son distintas a proposito, porque son sistemas separados:
#
#    portal   design/sistema.py  ->  design/emitir.py
#             -> frontend/app/assets/css/main.css              (v2.0)
#             -> frontend/app/utils/tokens.generated.ts
#
#    informe  docs/entregables/estilo/uxdoc.sty  ->  generar_tokens_a4.py
#             -> docs/entregables/estilo/a4_tokens.tex         (v1.0)
#             -> docs/entregables/datos/a4_tokens.json
#
#  Este guion comprueba las cinco condiciones que hacen cierta la guia de
#  estilos de la Actividad 4:
#
#    1. Anclas: los once colores versionados en la Actividad 1 conservan su
#       valor en uxdoc.sty. main_a1, main_a2 y main_a3 estan entregados y
#       compilan contra ellos: cambiar uno invalida tres entregas cerradas.
#    2. Inventario: uxdoc.sty declara los 37 nombres de color de la guia y el
#       manifiesto declara los 37 tokens.
#    3. Un emisor por archivo, salidas al dia e idempotencia. Las tres se
#       comprueban SIN ESCRIBIR sobre el arbol de trabajo: la version anterior
#       de este paso regeneraba en sitio con el generador del informe, que
#       entonces tambien escribia main.css, y el propio verificador dejaba la
#       paleta de papel dentro de frontend/. Es la entrada 11 del backlog.
#    4. Ningun color escrito a mano fuera de las dos fuentes declaradas.
#    5. Version: v1.0 en las salidas del informe y v2.0 en las del portal.
#
#  Las listas de abajo -anclas, versiones, fecha- estan escritas a proposito:
#  un invariante que se lee del mismo archivo que vigila no comprueba nada.
#
#  POSIX sh, sin argumentos y sin modos. No escribe ningun archivo versionado:
#  lo que necesita emitir para comparar va a un directorio temporal.
# ---------------------------------------------------------------------------

set -eu

RAIZ=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)

# El emisor del portal se invoca como modulo -"python -m design.emitir", igual
# que en el Makefile-, y eso exige que el directorio de trabajo sea la raiz.
cd -- "$RAIZ"

FUENTE_INFORME="$RAIZ/docs/entregables/estilo/uxdoc.sty"
FUENTE_PORTAL="$RAIZ/design/sistema.py"
GENERADOR_INFORME="$RAIZ/docs/entregables/generar_tokens_a4.py"
EMISOR_PORTAL="$RAIZ/design/emitir.py"
CSS="$RAIZ/frontend/app/assets/css/main.css"
TS="$RAIZ/frontend/app/utils/tokens.generated.ts"
TEX="$RAIZ/docs/entregables/estilo/a4_tokens.tex"
JSON="$RAIZ/docs/entregables/datos/a4_tokens.json"

VERSION_INFORME="v1.0"
VERSION_PORTAL="v2.0"
FECHA_ESPERADA="2026-08-16"
NOMBRES_ESPERADOS=37

TEMPORAL=""

limpiar() {
    if [ -n "$TEMPORAL" ]; then
        rm -rf "$TEMPORAL"
    fi
}
trap limpiar EXIT HUP INT TERM

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

emisor_declarado() {
    # $1: archivo generado  $2: emisor propio  $3: emisor de la otra cadena
    etiqueta=$(basename "$1")
    if ! grep -qF "$2" "$1"; then
        marcar FALLA "$etiqueta" "no declara $2 como emisor"
    elif grep -qF "$3" "$1"; then
        marcar FALLA "$etiqueta" "lo escribio $3, que no es su emisor"
    else
        marcar OK "$etiqueta" "emitido por $2"
    fi
}

echo "Verificacion de los tokens de diseno (US-UX-09)"
echo ""

for archivo in "$FUENTE_INFORME" "$FUENTE_PORTAL" "$GENERADOR_INFORME" \
    "$EMISOR_PORTAL" "$CSS" "$TS" "$TEX" "$JSON"; do
    if [ ! -f "$archivo" ]; then
        echo "FALLA: falta $archivo. Corre 'make tokens' antes de verificar." >&2
        exit 1
    fi
done

# --- 1. Las once anclas conservan su valor ---------------------------------
echo "1. Anclas versionadas en la Actividad 1"
while read -r nombre valor; do
    [ -n "$nombre" ] || continue
    if grep -q "definecolor{$nombre}{HTML}{$valor}" "$FUENTE_INFORME"; then
        marcar OK "$nombre" "$valor intacto"
    else
        leido=$(sed -n "s/.*definecolor{$nombre}{HTML}{\([0-9A-Fa-f]*\)}.*/\1/p" \
            "$FUENTE_INFORME")
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
echo "2. Inventario de color del informe"
declarados=$(grep -c 'definecolor{' "$FUENTE_INFORME" || true)
alias=$(grep -c 'colorlet{' "$FUENTE_INFORME" || true)
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

# --- 3. Un emisor por archivo, salidas al dia e idempotencia ---------------
echo ""
echo "3. Un emisor por archivo, salidas al dia e idempotencia"

# 3a. Cada salida dice de que cadena viene, y no lleva la firma de la otra.
# Esta es la comprobacion que faltaba: cuando los dos programas escribian
# main.css, el ganador era el ultimo que hubiera corrido y nadie lo veia.
emisor_declarado "$CSS" "design/emitir.py" "generar_tokens_a4.py"
emisor_declarado "$TS" "design/emitir.py" "generar_tokens_a4.py"
emisor_declarado "$TEX" "generar_tokens_a4.py" "design/emitir.py"
emisor_declarado "$JSON" "generar_tokens_a4.py" "design/emitir.py"

# 3b. Las salidas en disco son las que producen hoy sus fuentes, y dos corridas
# seguidas producen lo mismo. Ninguna de las dos preguntas se responde
# regenerando en sitio: "--verificar" recorre sin escribir y "--destino" emite
# a un directorio temporal que se borra al salir.
if command -v poetry >/dev/null 2>&1; then
    if poetry -P "$RAIZ/backend" run python -m design.emitir --verificar \
        >/dev/null 2>&1; then
        marcar OK "portal en disco" "coincide con lo que design/sistema.py produce hoy"
    else
        marcar FALLA "portal en disco" "difiere: corre 'make tokens' y commitea"
    fi

    if poetry -P "$RAIZ/backend" run python "$GENERADOR_INFORME" --verificar \
        >/dev/null 2>&1; then
        marcar OK "informe en disco" "coincide con lo que uxdoc.sty produce hoy"
    else
        marcar FALLA "informe en disco" "difiere: corre 'make tokens' y commitea"
    fi

    TEMPORAL=$(mktemp -d 2>/dev/null || mktemp -d -t verificar_tokens)
    emitido=1
    for ronda in 1 2; do
        poetry -P "$RAIZ/backend" run python -m design.emitir \
            --destino "$TEMPORAL/portal_$ronda" >/dev/null 2>&1 || emitido=0
        poetry -P "$RAIZ/backend" run python "$GENERADOR_INFORME" \
            --destino "$TEMPORAL/informe_$ronda" >/dev/null 2>&1 || emitido=0
    done
    if [ "$emitido" -eq 0 ]; then
        marcar FALLA "emision a temporal" "algun emisor termino con error"
    elif ! diff -r "$TEMPORAL/portal_1" "$TEMPORAL/portal_2" >/dev/null 2>&1; then
        marcar FALLA "dos corridas del portal" "la segunda escribio algo distinto"
    elif ! diff -r "$TEMPORAL/informe_1" "$TEMPORAL/informe_2" >/dev/null 2>&1; then
        marcar FALLA "dos corridas del informe" "la segunda escribio algo distinto"
    else
        marcar OK "dos corridas seguidas" "las cuatro salidas quedan byte a byte iguales"
    fi
else
    marcar FALLA "poetry" "no esta en el PATH: la idempotencia no se pudo comprobar"
fi

# --- 4. Ningun color escrito a mano ----------------------------------------
echo ""
echo "4. Ningun color escrito a mano fuera de uxdoc.sty y design/sistema.py"
vigilados="$GENERADOR_INFORME $EMISOR_PORTAL"
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

# --- 5. Una version por cadena ----------------------------------------------
echo ""
echo "5. Version de cada cadena en sus salidas"
for archivo in "$CSS" "$TS"; do
    etiqueta=$(basename "$archivo")
    if grep -qF "$VERSION_PORTAL" "$archivo" && grep -qF "$FECHA_ESPERADA" "$archivo"; then
        marcar OK "$etiqueta" "$VERSION_PORTAL - $FECHA_ESPERADA"
    else
        marcar FALLA "$etiqueta" "no declara $VERSION_PORTAL - $FECHA_ESPERADA"
    fi
done
for archivo in "$TEX" "$JSON"; do
    etiqueta=$(basename "$archivo")
    if grep -qF "$VERSION_INFORME" "$archivo" && grep -qF "$FECHA_ESPERADA" "$archivo"; then
        marcar OK "$etiqueta" "$VERSION_INFORME - $FECHA_ESPERADA"
    else
        marcar FALLA "$etiqueta" "no declara $VERSION_INFORME - $FECHA_ESPERADA"
    fi
done
# El documento del entregable NO declara version, y esa ausencia es la regla:
# el evaluador de A4 pidio que el trabajo no llevara seguimiento de versiones,
# que es util en el proyecto y sobra en la entrega (19-ago-2026). La cadena
# sigue viva donde sirve -las cuatro salidas generadas de arriba-, asi que aqui
# se comprueba lo contrario que antes: que el .tex no la imprima.
GUIA="$RAIZ/docs/entregables/contenido/a4_03_guia_estilos.tex"
if [ -f "$GUIA" ]; then
    if grep -qE '\\(versionguia|fechaguia)' "$GUIA"; then
        marcar FALLA "a4_03_guia_estilos.tex" "vuelve a imprimir la version"
    else
        marcar OK "a4_03_guia_estilos.tex" "sin version impresa, como se pidio"
    fi
fi

# --- Veredicto --------------------------------------------------------------
echo ""
if [ "$fallos" -gt 0 ]; then
    echo "FALLA: $fallos comprobacion(es) de los tokens no cumplen." >&2
    exit 1
fi

echo "Tokens en verde: dos cadenas, un emisor por archivo, salidas idempotentes."
