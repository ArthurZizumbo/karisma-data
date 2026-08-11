# ---------------------------------------------------------------------------
#  Karisma Data - unica puerta de entrada al entorno de desarrollo (US-001).
#
#  Requiere GNU Make y un shell POSIX. En Windows se ejecuta desde Git Bash:
#  # Este Makefile NO fija SHELL. Cada receta es un comando de una sola linea, de
# modo que funciona igual con cmd.exe -el shell que GNU Make usa en Windows- que
# con cualquier shell POSIX. La logica que necesita sh vive en scripts/*.sh y se
# invoca explicitamente con bash, que es el patron que ya funciona en los otros
# proyectos del equipo.
#
# La version anterior fijaba SHELL := /bin/sh y las recetas llevaban dentro
# guiones POSIX. Eso obligaba a lanzar make desde Git Bash y fallaba desde
# PowerShell con "test no se reconoce como un comando", sin decir por que.


COMPOSE := docker compose
ENV_BACKEND := backend/.env.local
ENV_FRONTEND := frontend/.env.local

.DEFAULT_GOAL := help

.PHONY: help dev lint test data tokens db-new db-up db-rollback check verificar \
        comprobar-env-backend comprobar-env-frontend

# ---------------------------------------------------------------------------
#  Ayuda
# ---------------------------------------------------------------------------

help: ## Muestra esta ayuda
	@bash scripts/ayuda.sh

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
	@bash scripts/comprobar_requisitos.sh herramienta poetry
	@bash scripts/comprobar_requisitos.sh herramienta pnpm
	poetry -P backend run ruff check --config backend/pyproject.toml backend tests
	poetry -P backend run ruff format --check --config backend/pyproject.toml backend tests
	poetry -P backend run mypy --config-file backend/pyproject.toml backend/app tests
	pnpm --dir frontend lint
	pnpm --dir frontend typecheck

test: ## pytest en tests/backend y vitest en frontend/
	@bash scripts/comprobar_requisitos.sh herramienta poetry
	@bash scripts/comprobar_requisitos.sh herramienta pnpm
	poetry -P backend run pytest -c backend/pyproject.toml tests/backend
	pnpm --dir frontend test

# El subcomando es "dir" y no "detect": gitleaks 8.30 retiro detect y lo separo
# en "dir" -recorre el arbol de trabajo- y "git" -recorre el historial-. Aqui
# interesa el arbol, porque make check se corre ANTES de abrir un PR y la
# pregunta es si lo que estas a punto de commitear lleva un secreto. El barrido
# del historial es mas lento y solo tiene sentido en CI (US-004).
check: lint ## lint mas secrets-scan. Obligatorio antes de abrir un PR
	@bash scripts/comprobar_requisitos.sh herramienta gitleaks
	gitleaks dir . --config .gitleaks.toml --redact --no-banner --no-color
	@echo ""
	@echo "Comprobando que el escaneo detecta de verdad (CA-7b)..."
	bash scripts/verificar_gitleaks.sh

verificar: ## Comprueba pines, secretos, reproducibilidad y tokens de diseno
	sh scripts/verificar_pines.sh
	sh scripts/verificar_gitleaks.sh
	sh scripts/verificar_reproducibilidad.sh
	sh scripts/verificar_tokens_a4.sh

# ---------------------------------------------------------------------------
#  Datos sinteticos
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
#  Tokens de diseno - la guia de estilos de A4 y la aplicacion salen del mismo
#  archivo. La cadena va en un solo sentido:
#      docs/entregables/estilo/uxdoc.sty  ->  generar_tokens_a4.py  ->
#      main.css + tokens.generated.ts + a4_tokens.tex + a4_tokens.json
#  Las cuatro salidas son generadas: editarlas a mano hace divergir el
#  prototipo del PDF del curso y "make verificar" lo detecta.
# ---------------------------------------------------------------------------

tokens: ## Regenera los tokens de diseno (@theme, paleta tipada, laminas y manifiesto)
	@bash scripts/comprobar_requisitos.sh herramienta poetry
	poetry -P backend run python docs/entregables/generar_tokens_a4.py

data: ## DEGRADADO hasta US-006: genera los silos sinteticos con semilla fija
	@bash scripts/degradado_data.sh

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
	@bash scripts/comprobar_requisitos.sh slug "$(SLUG)"
	@bash scripts/dbmate.sh new "$(SLUG)"

db-up: comprobar-env-backend ## Aplica las migraciones pendientes y regenera db/schema.sql
	@bash scripts/dbmate.sh --wait up

db-rollback: comprobar-env-backend ## Revierte la ultima migracion aplicada
	@bash scripts/dbmate.sh rollback

# ---------------------------------------------------------------------------
#  Comprobaciones internas
# ---------------------------------------------------------------------------

comprobar-env-backend:
	@bash scripts/comprobar_requisitos.sh entorno $(ENV_BACKEND)

comprobar-env-frontend:
	@bash scripts/comprobar_requisitos.sh entorno $(ENV_FRONTEND)
