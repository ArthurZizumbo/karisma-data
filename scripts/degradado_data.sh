#!/usr/bin/env bash
# Explains why "make data" does not generate anything yet, and fails on purpose.
# A degraded target that exits 0 in silence reads as a target that worked.
set -eu
echo "make data todavia no genera nada." >&2
echo "El generador de silos sinteticos (ml/data/generators.py, semilla fija) se entrega en US-006." >&2
echo "data/silos/ sigue vacio a proposito: ninguna capa de US-001 depende de datos generados." >&2
exit 1
