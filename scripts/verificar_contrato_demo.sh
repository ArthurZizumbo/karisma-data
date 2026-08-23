#!/bin/sh
# ---------------------------------------------------------------------------
#  US-AVANCE-5 - el contrato de datos/demo.tex compila en los dos escenarios.
#
#  docs/entregables/datos/demo.tex define \urlDemoWeb, \siHayDemoWeb y la
#  bandera \ifhaydemoweb, y decide entre dos ramas segun exista o no
#  datos/despliegue.tex, que .gitignore excluye. El escenario SIN el archivo no
#  es el raro: es como llega el repositorio a cualquiera que lo clone.
#
#  El defecto que atrapa: alguien simplifica demo.tex -quitar la rama \else del
#  \IfFileExists parece una limpieza inofensiva- y entonces, en un clon limpio,
#  o el documento deja de compilar por \urlDemoWeb indefinida, o algo peor y mas
#  silencioso: \urlDemoWeb sigue siendo \url{\urlDemoWebValor} sobre un valor
#  vacio y la entrega publica un enlace vacio donde iba la direccion. Por eso no
#  basta con que compile: se comprueba QUE RAMA quedo elegida.
#
#  Se compila un documento MINIMO, no main_completo.tex. El acumulado son 305
#  paginas y tres pasadas; aqui la pregunta cabe en un article con hyperref, que
#  es lo unico que demo.tex necesita -\url viene de hyperref-, y tarda segundos.
#
#  Nada se compila dentro del repositorio ni se toca el datos/despliegue.tex
#  local: el guion arma una copia de demo.tex en un directorio temporal y
#  compila ahi, de modo que puede fabricar los dos escenarios sin mover un
#  archivo que a otra persona le costaria una llamada a gcloud recuperar.
#
#  Va en "make verificar" y no en "make check" porque necesita xelatex. Quien
#  corre el barrido previo a la entrega es quien compila el PDF, asi que ahi la
#  herramienta esta; en el gate diario seria una dependencia nueva para todos.
#
#  POSIX sh, sin argumentos y sin modos.
# ---------------------------------------------------------------------------

set -eu

RAIZ=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
CONTRATO="$RAIZ/docs/entregables/datos/demo.tex"

echo "Verificacion del contrato de la direccion del demo (US-AVANCE-5)"
echo ""

[ -f "$CONTRATO" ] || {
    echo "FALLA: no existe docs/entregables/datos/demo.tex, que es el sujeto" >&2
    echo "de esta comprobacion. Si se renombro, este guion tiene que saberlo." >&2
    exit 1
}

TEX="xelatex"
if ! command -v xelatex >/dev/null 2>&1; then
    if command -v xelatex.exe >/dev/null 2>&1; then
        TEX="xelatex.exe"
    else
        echo "FALLA: xelatex no esta en el PATH." >&2
        echo "Es la misma herramienta con la que se compila el entregable." >&2
        exit 1
    fi
fi

BANCO=$(mktemp -d)
limpiar() {
    rm -rf "$BANCO"
}
trap limpiar EXIT INT TERM

mkdir -p "$BANCO/datos"
cp "$CONTRATO" "$BANCO/datos/demo.tex"

# El documento usa las dos macros en el cuerpo -si \urlDemoWeb quedara sin
# definir, xelatex sale distinto de cero- y ademas escribe al .log que rama
# eligio y a que quedo definida \urlDemoWeb. \meaning es expandible, asi que
# sobrevive dentro de \typeout sin ejecutar \url. Los rotulos se comprueban por
# su PRINCIPIO y no enteros: el .log corta las lineas a 79 caracteres y la frase
# de respaldo no cabe. Y \meaning de un \newcommand dice "\long macro:->" y no
# "macro:->"; esta comprobado contra xelatex, no supuesto.
cat > "$BANCO/prueba.tex" <<'TEXDOC'
\documentclass{article}
\usepackage{hyperref}
\input{datos/demo}
\begin{document}
\typeout{DEMOCHK:RAMA=\siHayDemoWeb{CON}{SIN}}
\typeout{DEMOCHK:DEF=\meaning\urlDemoWeb}
\typeout{DEMOCHK:VAL=\urlDemoWebValor}
La direccion del demo: \urlDemoWeb.
\siHayDemoWeb{Redaccion con direccion.}{Redaccion sin direccion.}
\end{document}
TEXDOC

compilar() {
    # Se compila desde el banco: \IfFileExists{datos/despliegue.tex} se resuelve
    # contra el directorio de trabajo, que es justo lo que se quiere gobernar.
    (cd "$BANCO" && "$TEX" -interaction=nonstopmode prueba.tex >/dev/null 2>&1)
}

exigir() {
    # $1 rotulo del escenario, $2 texto que el .log debe contener, $3 por que.
    if ! grep -qF "$2" "$BANCO/prueba.log"; then
        echo "" >&2
        echo "FALLA ($1): el .log no dice '$2'." >&2
        echo "$3" >&2
        exit 1
    fi
}

# --- Escenario 1: sin datos/despliegue.tex, que es como se clona -------------
rm -f "$BANCO/datos/despliegue.tex"

if ! compilar; then
    echo "FALLA: el documento NO compila sin datos/despliegue.tex." >&2
    echo "Asi es como llega el repositorio a cualquiera que lo clone: la rama" >&2
    echo "de respaldo del \IfFileExists de datos/demo.tex tiene que definir" >&2
    echo "\urlDemoWeb y \siHayDemoWeb igual que la otra." >&2
    exit 1
fi

exigir "sin direccion" "DEMOCHK:RAMA=SIN" \
    "\siHayDemoWeb eligio la rama equivocada sin el archivo del valor."
exigir "sin direccion" "DEMOCHK:DEF=\long macro:->la" \
    "Sin el archivo, \urlDemoWeb tiene que ser la frase de respaldo. Si quedo
definida como \url sobre un valor vacio, la entrega publica un enlace vacio y
nadie lo nota hasta que el evaluador hace clic."

echo "  sin datos/despliegue.tex: compila y publica la frase de respaldo"

# --- Escenario 2: con el valor presente --------------------------------------
# Valor ficticio y deliberadamente no-Cloud Run: este guion esta versionado y
# scripts/verificar_url_demo.sh lo lee.
cat > "$BANCO/datos/despliegue.tex" <<'TEXVAL'
\renewcommand{\urlDemoWebValor}{https://ejemplo.invalid/karisma}
TEXVAL

if ! compilar; then
    echo "FALLA: el documento no compila CON datos/despliegue.tex presente." >&2
    echo "Es el escenario con el que se compila la entrega." >&2
    exit 1
fi

exigir "con direccion" "DEMOCHK:RAMA=CON" \
    "Con el archivo presente, \siHayDemoWeb debe tomar la primera redaccion."
exigir "con direccion" "DEMOCHK:DEF=\long macro:->\url" \
    "Con el archivo presente, \urlDemoWeb debe ser el enlace y no el respaldo."
exigir "con direccion" "DEMOCHK:VAL=https://ejemplo.invalid/karisma" \
    "La bandera se encendio pero el valor no llego: sin el \input del archivo,
\urlDemoWeb seria un \url sobre una cadena vacia."

echo "  con datos/despliegue.tex: compila y publica el enlace"
echo ""
echo "En verde: el contrato responde en los dos escenarios."
