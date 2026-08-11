#!/usr/bin/env bash
# Guard for the Makefile targets: verifies that a required tool or environment
# file is present before a recipe runs.
#
# Lives in a script and not inside the recipe on purpose. GNU Make on Windows
# runs recipes with cmd.exe, where POSIX constructs such as "test -f x || { ...; }"
# are syntax errors. Keeping recipes to single commands lets the same Makefile
# work from PowerShell, from cmd and from any POSIX shell.
set -eu

uso() {
    echo "Uso: comprobar_requisitos.sh herramienta <nombre> | entorno <ruta>" >&2
    exit 2
}

[ $# -ge 2 ] || uso

case "$1" in
herramienta)
    # En Windows muchas herramientas se instalan como shim .bat, .cmd o .exe y
    # "command -v poetry" de bash no las resuelve aunque PowerShell y cmd si lo
    # hagan. Se prueban las cuatro formas antes de declarar que falta.
    encontrada=""
    for candidata in "$2" "$2.exe" "$2.cmd" "$2.bat"; do
        if command -v "$candidata" >/dev/null 2>&1; then
            encontrada="$candidata"
            break
        fi
    done
    if [ -z "$encontrada" ]; then
        echo "Falta $2 en el PATH." >&2
        case "$2" in
        gitleaks)
            echo "El secrets-scan NO se ejecuto. Instalalo con:" >&2
            echo "  winget install --id Gitleaks.Gitleaks --exact" >&2
            echo "Si ya lo instalaste, abre una terminal nueva: winget modifica el" >&2
            echo "PATH persistido y un shell ya abierto conserva el anterior." >&2
            ;;
        *)
            echo "Instalalo antes de volver a correr este objetivo." >&2
            ;;
        esac
        exit 1
    fi
    ;;
entorno)
    if [ ! -f "$2" ]; then
        echo "Falta $2." >&2
        echo "Crealo a partir de la plantilla: cp ${2%.local}.example $2" >&2
        exit 1
    fi
    ;;
slug)
    if [ -z "$2" ]; then
        echo "Falta SLUG. Uso: make db-new SLUG=create_catalog" >&2
        exit 1
    fi
    ;;
*)
    uso
    ;;
esac
