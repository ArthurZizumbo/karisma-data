#!/usr/bin/env bash
# Applies db/seeds/catalog.sql with the psql that ships inside the dbmate
# service. Companion of scripts/dbmate.sh and, like it, the connection string
# travels through "-e DATABASE_URL" with no "=": with "-e NOMBRE=valor" the
# user:password pair would be readable with ps for as long as the command runs.
#
# Lives in a script and not inside the Makefile recipe for the same reason as
# dbmate.sh: "set -a; . ./file" is POSIX shell, and GNU Make on Windows runs
# recipes with cmd.exe. A recipe with nested quoting works from Git Bash and
# fails from PowerShell without saying why.
#
# The seed is idempotent -it truncates inside its own transaction- so running
# this twice leaves the same rows and the same identifiers.
set -eu

ENV_BACKEND="${ENV_BACKEND:-backend/.env.local}"

if [ ! -f "$ENV_BACKEND" ]; then
    echo "Falta $ENV_BACKEND." >&2
    echo "Crealo a partir de la plantilla: cp backend/.env.example $ENV_BACKEND" >&2
    exit 1
fi

if [ ! -f "db/seeds/catalog.sql" ]; then
    echo "Falta db/seeds/catalog.sql." >&2
    echo "Emitelo con: poetry -P backend run python -m ml.data.seed_catalog" >&2
    exit 1
fi

set -a
# shellcheck disable=SC1090
. "./$ENV_BACKEND"
set +a

export DATABASE_URL="${DBMATE_URL:-$DATABASE_URL}"

exec docker compose run --rm -T --entrypoint sh -e DATABASE_URL dbmate \
    -c 'psql -q -v ON_ERROR_STOP=1 -d "$DATABASE_URL" -f /db/seeds/catalog.sql'
