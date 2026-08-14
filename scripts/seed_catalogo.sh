#!/usr/bin/env bash
# Applies the seeds of db/seeds/ with the psql that ships inside the dbmate
# service. Companion of scripts/dbmate.sh and, like it, the connection string
# travels through "-e DATABASE_URL" with no "=": with "-e NOMBRE=valor" the
# user:password pair would be readable with ps for as long as the command runs.
#
# Lives in a script and not inside the Makefile recipe for the same reason as
# dbmate.sh: "set -a; . ./file" is POSIX shell, and GNU Make on Windows runs
# recipes with cmd.exe. A recipe with nested quoting works from Git Bash and
# fails from PowerShell without saying why.
#
# US-029: the files are arguments, and the ORDER THEY ARRIVE IN IS THE ORDER
# THEY ARE APPLIED IN. The Makefile computes it with $(sort $(wildcard
# db/seeds/*.sql)), which is alphabetical and therefore also the dependency
# order: catalog.sql creates the sources and catalog_lineage.sql hangs from
# them. Sorting here as well would hide a caller that meant another order; with
# no arguments the catalog alone is applied, which is what this script did
# before there was a second seed.
#
# Every seed is idempotent -each truncates inside its own transaction- so
# running this twice leaves the same rows and the same identifiers.
set -eu

ENV_BACKEND="${ENV_BACKEND:-backend/.env.local}"

if [ "$#" -eq 0 ]; then
    set -- db/seeds/catalog.sql
fi

if [ ! -f "$ENV_BACKEND" ]; then
    echo "Falta $ENV_BACKEND." >&2
    echo "Crealo a partir de la plantilla: cp backend/.env.example $ENV_BACKEND" >&2
    exit 1
fi

for semilla in "$@"; do
    if [ ! -f "$semilla" ]; then
        echo "Falta $semilla." >&2
        echo "El catalogo se emite con: poetry -P backend run python -m ml.data.seed_catalog" >&2
        exit 1
    fi
    case "$semilla" in
        db/*) ;;
        *)
            echo "$semilla esta fuera de db/, que es lo unico que el servicio dbmate monta." >&2
            exit 1
            ;;
    esac
done

set -a
# shellcheck disable=SC1090
. "./$ENV_BACKEND"
set +a

export DATABASE_URL="${DBMATE_URL:-$DATABASE_URL}"

# The path travels as SEED_FILE for the same reason as the connection string:
# it is expanded by the shell inside the container, so no quoting has to be
# nested. It travels WITHOUT the leading slash and the container rebuilds it as
# /db/$SEED_FILE, which is not a detail: MSYS -Git Bash on Windows- rewrites any
# environment value that looks like an absolute POSIX path into a Windows path
# before handing it to docker.exe, and psql inside the container was asked for
# "C:/Program Files/Git/db/seeds/catalog.sql". A relative value is left alone,
# and the service already mounts ./db on /db.
for semilla in "$@"; do
    SEED_FILE="${semilla#db/}"
    export SEED_FILE
    docker compose run --rm -T --entrypoint sh -e DATABASE_URL -e SEED_FILE dbmate \
        -c 'psql -q -v ON_ERROR_STOP=1 -d "$DATABASE_URL" -f "/db/$SEED_FILE"'
done
