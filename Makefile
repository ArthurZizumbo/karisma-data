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

.PHONY: help dev lint test data tokens db-new db-up db-rollback db-seed check \
        verificar comprobar-env-backend comprobar-env-frontend

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
#
# La comprobacion de tipos va en dos invocaciones y no en una: tests/backend y
# tests/ml tienen cada uno su conftest.py, ninguno de los dos directorios es un
# paquete -no hay __init__.py a proposito, porque anadirlo cambiaria el nombre
# de modulo que pytest calcula para todo el directorio- y mypy resuelve los dos
# archivos al mismo modulo "conftest" y aborta con "Duplicate module named".
# Las alternativas que documenta mypy son peores aqui: --explicit-package-bases
# renombra los modulos de las pruebas y rompe el "from conftest import ..." de
# tests/backend, que es de US-002 y no se toca. El primer comando conserva
# "tests" entero -asi un directorio de pruebas nuevo queda cubierto sin editar
# esta linea- y solo aparta el subarbol del segundo.
#
# scripts/ entra en los tres objetivos desde US-015: scripts/generar_hashes_demo.py
# produce los hashes argon2id que siembra una migracion, y una herramienta que
# escribe credenciales en el esquema no puede quedarse fuera de la puerta de
# calidad. Los .sh del mismo directorio no los toca ninguna de las dos: ruff y
# mypy solo miran archivos .py.
lint: ## ruff y mypy en backend/, eslint y typecheck en frontend/
	@bash scripts/comprobar_requisitos.sh herramienta poetry
	@bash scripts/comprobar_requisitos.sh herramienta pnpm
	poetry -P backend run ruff check --config backend/pyproject.toml backend ml scripts tests
	poetry -P backend run ruff format --check --config backend/pyproject.toml backend ml scripts tests
	poetry -P backend run mypy --config-file backend/pyproject.toml --exclude '^tests/ml/' backend/app scripts tests
	poetry -P backend run mypy --config-file backend/pyproject.toml ml tests/ml
	pnpm --dir frontend lint
	pnpm --dir frontend typecheck

test: ## pytest en tests/backend y vitest en frontend/
	@bash scripts/comprobar_requisitos.sh herramienta poetry
	@bash scripts/comprobar_requisitos.sh herramienta pnpm
	poetry -P backend run pytest -c backend/pyproject.toml tests/backend tests/ml
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

verificar: ## Comprueba pines, secretos, reproducibilidad, tokens y datos
	sh scripts/verificar_pines.sh
	sh scripts/verificar_gitleaks.sh
	sh scripts/verificar_reproducibilidad.sh
	sh scripts/verificar_tokens_a4.sh
	sh scripts/verificar_datos.sh

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

data: ## Genera los silos sinteticos y la serie preagregada (semilla fija 20260720)
	@bash scripts/comprobar_requisitos.sh herramienta poetry
	poetry -P backend run python -m ml.data.generators --out data
	@echo ""
	@echo "Silos en data/silos/, serie preagregada en data/aggregates/."
	@echo "Resumen legible, esquemas y anomalias: data/README.md"

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

# El contenido del catalogo NO va en una migracion: una migracion aplicada
# jamas se edita y una definicion de negocio se corrige varias veces. El
# emisor de ml/ escribe db/seeds/catalog.sql -artefacto versionado, que es lo
# que el revisor lee- y psql lo aplica dentro del servicio dbmate, que ya trae
# el cliente y ya monta ./db en /db.
#
# Dos comandos y no uno: el primero reemite el artefacto -asi "make db-seed"
# nunca aplica una version vieja del contenido- y el segundo lo aplica. La
# logica de shell vive en scripts/seed_catalogo.sh por la misma razon que la de
# dbmate.sh: con la cadena entre comillas dentro de la receta, el objetivo
# funciona desde Git Bash y falla desde PowerShell sin decir por que.
db-seed: comprobar-env-backend ## Regenera y aplica el seed del catalogo semantico
	poetry -P backend run python -m ml.data.seed_catalog
	@bash scripts/seed_catalogo.sh

# ---------------------------------------------------------------------------
#  Comprobaciones internas
# ---------------------------------------------------------------------------

comprobar-env-backend:
	@bash scripts/comprobar_requisitos.sh entorno $(ENV_BACKEND)

comprobar-env-frontend:
	@bash scripts/comprobar_requisitos.sh entorno $(ENV_FRONTEND)
