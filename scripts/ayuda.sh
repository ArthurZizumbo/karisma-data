#!/usr/bin/env bash
# Prints the Makefile targets that carry a "## " description.
#
# Lives in a script because awk is not on the PATH of cmd.exe or PowerShell on
# Windows: it ships with Git, and only bash brings it along. Calling it from a
# recipe worked from Git Bash and failed everywhere else.
set -eu
echo "Karisma Data - objetivos disponibles"
echo ""
awk 'BEGIN { FS = ":.*## " } /^[a-zA-Z0-9_.-]+:.*## / { printf "  %-14s %s\n", $1, $2 }' Makefile
echo ""
echo "data/ no se versiona: los silos se regeneran con semilla fija. Sin"
echo "'make data' el explorador y el tablero no tienen nada que mostrar."
