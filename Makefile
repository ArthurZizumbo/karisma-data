# ---------------------------------------------------------------------------
#  Karisma Data - unica puerta de entrada al entorno de desarrollo (US-001).
#
#  Requiere GNU Make y un shell POSIX. En Windows se ejecuta desde Git Bash:
#  SHELL := /bin/sh es obligatorio porque, sin el, GNU Make lanzaria las
#  recetas con cmd.exe y ninguna de ellas funcionaria (RU-01).
#
#  Ninguna receta evalua funciones de make que invoquen a un proceso externo
#  en tiempo de parseo (CA-2b). Las variables de entorno se cargan DENTRO de
#  la receta que las necesita, de modo que un .env.local ausente no rompe ni
#  siquiera "make help".
# ---------------------------------------------------------------------------

SHELL := /bin/sh
.SHELLFLAGS := -e -c

COMPOSE := docker compose
ENV_BACKEND := backend/.env.local
ENV_FRONTEND := frontend/.env.local

.DEFAULT_GOAL := help

.PHONY: help dev lint test data db-new db-up db-rollback check verificar \
        comprobar-env-backend comprobar-env-frontend

# ---------------------------------------------------------------------------
#  Ayuda
# ---------------------------------------------------------------------------

help: ## Muestra esta ayuda
	@echo "Karisma Data - objetivos disponibles"
	@echo ""
	@awk 'BEGIN { FS = ":.*## " } /^[a-zA-Z0-9_.-]+:.*## / { printf "  %-14s %s\n", $$1, $$2 }' $(MAKEFILE_LIST)
	@echo ""
	@echo "Degradaciones vigentes (no son fallos sorpresa):"
	@echo "  data       falla: el generador de silos sinteticos llega en US-006"
	@echo ""
	@echo "Cerradas en US-002: db-new, db-up y db-rollback quedaron verificados"
	@echo "contra el PostgreSQL del compose, y check ya corre su secrets-scan."

# ---------------------------------------------------------------------------
#  Entorno de desarrollo
# ---------------------------------------------------------------------------

dev: comprobar-env-backend comprobar-env-frontend ## Levanta db, api y web con Docker Compose
	@echo "Levantando db, api y web. La primera vez construye las imagenes."
	$(COMPOSE) up --build

# ---------------------------------------------------------------------------
#  Calidad
# ---------------------------------------------------------------------------

# ruff y mypy reciben --config/--config-file explicito: los tests viven en
# tests/backend/ (raiz) y ninguna herramienta autodescubre una configuracion
# que esta en un directorio hermano del objetivo. Sin la bandera, tests/ se
# lintearia con el set por defecto de ruff y backend/app con el del proyecto:
# dos configuraciones distintas para el mismo repositorio.
lint: ## ruff y mypy en backend/, eslint y typecheck en frontend/
	@command -v poetry >/dev/null 2>&1 || { echo "Falta poetry en el PATH. Instalalo antes de correr make lint." >&2; exit 1; }
	@command -v pnpm >/dev/null 2>&1 || { echo "Falta pnpm en el PATH. Instalalo antes de correr make lint." >&2; exit 1; }
	poetry -P backend run ruff check --config backend/pyproject.toml backend tests
	poetry -P backend run ruff format --check --config backend/pyproject.toml backend tests
	poetry -P backend run mypy --config-file backend/pyproject.toml backend/app tests
	pnpm --dir frontend lint
	pnpm --dir frontend typecheck

test: ## pytest en tests/backend y vitest en frontend/
	@command -v poetry >/dev/null 2>&1 || { echo "Falta poetry en el PATH. Instalalo antes de correr make test." >&2; exit 1; }
	@command -v pnpm >/dev/null 2>&1 || { echo "Falta pnpm en el PATH. Instalalo antes de correr make test." >&2; exit 1; }
	poetry -P backend run pytest -c backend/pyproject.toml tests/backend
	pnpm --dir frontend test

# El subcomando es "dir" y no "detect": gitleaks 8.30 retiro detect y lo separo
# en "dir" -recorre el arbol de trabajo- y "git" -recorre el historial-. Aqui
# interesa el arbol, porque make check se corre ANTES de abrir un PR y la
# pregunta es si lo que estas a punto de commitear lleva un secreto. El barrido
# del historial es mas lento y solo tiene sentido en CI (US-004).
check: lint ## lint mas secrets-scan. Obligatorio antes de abrir un PR
	@command -v gitleaks >/dev/null 2>&1 || { \
	    echo "secrets-scan NO ejecutado: gitleaks no esta en el PATH." >&2; \
	    echo "Instalalo con: winget install --id Gitleaks.Gitleaks --exact" >&2; \
	    echo "Si ya lo instalaste, abre una terminal nueva: winget modifica el PATH" >&2; \
	    echo "persistido y un shell ya abierto conserva el anterior." >&2; \
	    exit 1; }
	gitleaks dir . --config .gitleaks.toml --redact --no-banner --no-color
	@echo ""
	@echo "Comprobando que el escaneo detecta de verdad (CA-7b)..."
	bash scripts/verificar_gitleaks.sh

verificar: ## Comprueba pines de Node, deteccion de secretos y reproducibilidad
	sh scripts/verificar_pines.sh
	sh scripts/verificar_gitleaks.sh
	sh scripts/verificar_reproducibilidad.sh

# ---------------------------------------------------------------------------
#  Datos sinteticos
# ---------------------------------------------------------------------------

data: ## DEGRADADO hasta US-006: genera los silos sinteticos con semilla fija
	@echo "make data todavia no genera nada." >&2
	@echo "El generador de silos sinteticos (ml/data/generators.py, semilla fija) se entrega en US-006." >&2
	@echo "data/silos/ sigue vacio a proposito: ninguna capa de US-001 depende de datos generados." >&2
	@exit 1

# ---------------------------------------------------------------------------
#  Esquema de base de datos - unica via de cambio: dbmate
#
#  La forma "-e NOMBRE" sin "=" toma el valor del entorno del proceso y NO lo
#  coloca en el argv de docker compose. Con "-e NOMBRE=valor" la cadena
#  usuario:contrasena@host quedaba visible en "ps" para cualquier proceso de
#  la maquina mientras durara el comando.
#  dbmate corre como servicio de Compose, no como binario del host: evita una
#  instalacion manual por maquina y hace que el objetivo se comporte igual en
#  las tres. Primera migracion aplicada en US-002: enable_pgvector_extension.
# ---------------------------------------------------------------------------

db-new: comprobar-env-backend ## Crea una migracion. Uso: make db-new SLUG=create_catalog
	@test -n "$(SLUG)" || { echo "Falta SLUG. Uso: make db-new SLUG=create_catalog" >&2; exit 1; }
	@set -a; . ./$(ENV_BACKEND); set +a; \
	    export DATABASE_URL="$${DBMATE_URL:-$$DATABASE_URL}"; \
	    $(COMPOSE) run --rm -e DATABASE_URL dbmate new "$(SLUG)"

db-up: comprobar-env-backend ## Aplica las migraciones pendientes y regenera db/schema.sql
	@set -a; . ./$(ENV_BACKEND); set +a; \
	    export DATABASE_URL="$${DBMATE_URL:-$$DATABASE_URL}"; \
	    $(COMPOSE) run --rm -e DATABASE_URL dbmate --wait up

db-rollback: comprobar-env-backend ## Revierte la ultima migracion aplicada
	@set -a; . ./$(ENV_BACKEND); set +a; \
	    export DATABASE_URL="$${DBMATE_URL:-$$DATABASE_URL}"; \
	    $(COMPOSE) run --rm -e DATABASE_URL dbmate rollback

# ---------------------------------------------------------------------------
#  Comprobaciones internas
# ---------------------------------------------------------------------------

comprobar-env-backend:
	@test -f $(ENV_BACKEND) || { \
	    echo "Falta $(ENV_BACKEND)." >&2; \
	    echo "Crealo a partir de la plantilla: cp backend/.env.example $(ENV_BACKEND)" >&2; \
	    exit 1; }

comprobar-env-frontend:
	@test -f $(ENV_FRONTEND) || { \
	    echo "Falta $(ENV_FRONTEND)." >&2; \
	    echo "Crealo a partir de la plantilla: cp frontend/.env.example $(ENV_FRONTEND)" >&2; \
	    exit 1; }
