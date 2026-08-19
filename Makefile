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

.PHONY: help dev lint test data tokens permisos-ui db-new db-up db-rollback db-seed check \
        verificar desplegar verificar-despliegue comprobar-env-backend comprobar-env-frontend

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
#
# design/ entra desde US-ENTREGA-A4 por el mismo motivo. Es la fuente unica de
# los 17 tokens de color y de su emisor, y hasta esta US se lintaba solo si
# alguien lo invocaba a mano: la carpeta de la que sale main.css y
# tokens.generated.ts estaba fuera de la puerta. Va en la invocacion de mypy que
# lleva ml y tests/ml, no en la de backend/app, porque design/ no es un paquete
# del backend y tests/ml es quien lo prueba.
lint: ## ruff y mypy en backend/, design/ y ml/, eslint y typecheck en frontend/
	@bash scripts/comprobar_requisitos.sh herramienta poetry
	@bash scripts/comprobar_requisitos.sh herramienta pnpm
	poetry -P backend run ruff check --config backend/pyproject.toml backend design ml scripts tests
	poetry -P backend run ruff format --check --config backend/pyproject.toml backend design ml scripts tests
	poetry -P backend run mypy --config-file backend/pyproject.toml --exclude '^tests/ml/' backend/app scripts tests
	poetry -P backend run mypy --config-file backend/pyproject.toml design ml tests/ml
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
#
# El mapa de permisos entra en "check" y no solo en "verificar": es la unica
# comprobacion que compara frontend/app/utils/permisos.generated.ts contra el
# registro del backend, y una barrera que solo corre en el barrido del viernes
# no impide que el PR del martes mezcle un mapa editado a mano. Las pruebas de
# vitest cubren la mitad del defecto -que el mapa emitido no contradiga
# docs/security.md ni la declaracion del generador-, pero no pueden ver si el
# registro de Python cambio y nadie regenero: para eso hay que correr el
# generador, y eso es Python.
#
# Nota de uso: el guion regenera y luego compara con "git diff". Si acabas de
# correr "make permisos-ui", haz "git add" del archivo generado antes de
# "make check"; sin indexar, la regeneracion legitima se ve igual que una
# edicion a mano, que es exactamente lo que el guion existe para distinguir.
check: lint ## lint, secrets-scan y mapa de permisos. Obligatorio antes de abrir un PR
	@bash scripts/comprobar_requisitos.sh herramienta gitleaks
	gitleaks dir . --config .gitleaks.toml --redact --no-banner --no-color
	@echo ""
	@echo "Comprobando que el escaneo detecta de verdad (CA-7b)..."
	bash scripts/verificar_gitleaks.sh
	@echo ""
	bash scripts/verificar_permisos_ui.sh

# El mapa de permisos sigue aqui ademas de en "check", y no es un descuido:
# "verificar" ya repite verificar_gitleaks.sh, que tambien corre "check". La
# convencion del archivo es que este objetivo sea el superconjunto -el barrido
# completo antes de una entrega- y quitarle una comprobacion lo dejaria, por
# primera vez, mas estrecho que el gate diario. El costo de la duplicacion es
# una corrida mas del generador, segundos.
#
# verificar_historicos_tablero.sh se anade aqui y no a "check" porque necesita
# data/aggregates/serie_tablero.parquet, que no se versiona: sin "make data"
# no existe, y un gate obligatorio que falla en un clon limpio se termina
# saltando. Este objetivo ya depende de esa misma condicion por
# verificar_datos.sh. Va con bash y no con sh porque asi lo documentan
# docs/manual-test/us-026.md y el handoff de US-026.
verificar: ## Comprueba pines, secretos, reproducibilidad, tokens, permisos, datos e historicos
	sh scripts/verificar_pines.sh
	sh scripts/verificar_gitleaks.sh
	sh scripts/verificar_reproducibilidad.sh
	sh scripts/verificar_tokens_a4.sh
	sh scripts/verificar_permisos_ui.sh
	sh scripts/verificar_datos.sh
	bash scripts/verificar_historicos_tablero.sh

# ---------------------------------------------------------------------------
#  Datos sinteticos
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
#  Tokens de diseno - son DOS cadenas con DOS emisores, y por eso hay dos
#  comandos. No se pueden fundir en uno: cada cadena tiene su fuente, su paleta
#  y su version, y ninguna deriva de la otra.
#
#    1) El portal, para la pantalla:
#       design/sistema.py  ->  design/emitir.py  ->
#           frontend/app/assets/css/main.css        (@theme y los dos modos)
#           frontend/app/utils/tokens.generated.ts  (paleta tipada de /guia)
#
#    2) El informe del curso, para el papel:
#       docs/entregables/estilo/uxdoc.sty  ->  generar_tokens_a4.py  ->
#           docs/entregables/estilo/a4_tokens.tex   (laminas de la guia)
#           docs/entregables/datos/a4_tokens.json   (manifiesto)
#
#  El orden es el de la cadena de A4 leida de principio a fin: primero se emite
#  la interfaz, despues se captura y la captura entra en el PDF. Los dos
#  conjuntos de salidas son disjuntos -uno solo escribe bajo frontend/, el otro
#  solo bajo docs/entregables/-, asi que el orden no cambia el resultado.
#
#  Hasta el 14-ago-2026 este objetivo corria solo el segundo emisor, que ademas
#  escribia main.css y tokens.generated.ts: cada "make tokens" sustituia el
#  sistema de diseno del portal por la paleta de impresion del informe, que es
#  lo que la regla NON-NEGOTIABLE de AGENTS.md prohibe. Hoy cada archivo tiene
#  un solo emisor y "make tokens" sobre un arbol limpio lo deja limpio.
#
#  Las cuatro salidas son generadas: editarlas a mano se pierde en la siguiente
#  corrida y "make verificar" lo detecta sin escribir nada.
# ---------------------------------------------------------------------------

tokens: ## Regenera los tokens del portal y las laminas de la guia de estilos de A4
	@bash scripts/comprobar_requisitos.sh herramienta poetry
	poetry -P backend run python -m design.emitir
	poetry -P backend run python docs/entregables/generar_tokens_a4.py

# ---------------------------------------------------------------------------
#  Mapa de permisos de la interfaz - la matriz de permisos vive en el backend y
#  el frontend consume una PROYECCION generada de ella sobre el mapa de sitio
#  de A3. La cadena, tambien en un solo sentido:
#      backend/app/core/{scopes,permissions}.py + frontend/app/utils/navegacion.ts
#      ->  scripts/generar_permisos_ui.py  ->  frontend/app/utils/permisos.generated.ts
#  Editar la salida a mano abre una segunda politica que puede discrepar de
#  ROLE_HIERARCHY; "make verificar" lo detecta regenerando y difiendo.
# ---------------------------------------------------------------------------

permisos-ui: ## Regenera el mapa de permisos que la interfaz usa para ocultar por rol
	@bash scripts/comprobar_requisitos.sh herramienta poetry
	poetry -P backend run python scripts/generar_permisos_ui.py

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
#
# US-029: el seed dejo de ser uno solo. El recorrido lo calcula make -sort sobre
# wildcard- y no un bucle dentro de la receta, que volveria a exigir un shell
# POSIX y romperia desde PowerShell. El orden alfabetico es tambien el de
# dependencia: catalog.sql crea las fuentes y catalog_lineage.sql cuelga de
# ellas. Un seed nuevo entra sin tocar este objetivo.
SEEDS := $(sort $(wildcard db/seeds/*.sql))

db-seed: comprobar-env-backend ## Regenera y aplica los seeds de db/seeds/ en orden
	poetry -P backend run python -m ml.data.seed_catalog
	@bash scripts/seed_catalogo.sh $(SEEDS)

# ---------------------------------------------------------------------------
#  Comprobaciones internas
# ---------------------------------------------------------------------------

comprobar-env-backend:
	@bash scripts/comprobar_requisitos.sh entorno $(ENV_BACKEND)

comprobar-env-frontend:
	@bash scripts/comprobar_requisitos.sh entorno $(ENV_FRONTEND)

# ---------------------------------------------------------------------------
#  Despliegue puente en GCP (US-M01)
# ---------------------------------------------------------------------------

desplegar: comprobar-env-backend ## Despliega karisma-api y karisma-web en Cloud Run con Cloud SQL
	@bash scripts/desplegar.sh

verificar-despliegue: ## Comprueba el aislamiento, rutas y permisos sobre el despliegue en GCP
	@bash scripts/verificar_despliegue.sh
