#!/usr/bin/env bash
# Runs dbmate as a Compose service with the connection string taken from the
# backend environment file.
#
# The value travels through "-e DATABASE_URL" with no "=", so Compose reads it
# from this process environment instead of placing user:password in the argv,
# where any process on the machine could read it with ps.
#
# Lives in a script and not inside the Makefile recipe because "set -a; . ./file"
# is POSIX shell and GNU Make on Windows runs recipes with cmd.exe.
set -eu

ENV_BACKEND="${ENV_BACKEND:-backend/.env.local}"

if [ ! -f "$ENV_BACKEND" ]; then
    echo "Falta $ENV_BACKEND." >&2
    echo "Crealo a partir de la plantilla: cp backend/.env.example $ENV_BACKEND" >&2
    exit 1
fi

set -a
# shellcheck disable=SC1090
. "./$ENV_BACKEND"
set +a

export DATABASE_URL="${DBMATE_URL:-$DATABASE_URL}"

exec docker compose run --rm -e DATABASE_URL dbmate "$@"
