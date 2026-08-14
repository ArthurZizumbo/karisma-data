# Comandos — Portal Centralizado de Datos Financieros

> Lo que **corre hoy**. Resumen ejecutivo en [`AGENTS.md`](../../AGENTS.md). Lo que el plan promete
> pero todavía no existe está al final, en su propia sección y marcado como tal: un agente que
> invente la salida de un comando inexistente hace más daño que uno que declare `blocked`.

`make help` imprime esta misma lista desde el Makefile. Si algo de aquí no coincide con `make help`,
manda el Makefile.

## Desarrollo local

```bash
make dev              # docker compose up --build: PostgreSQL 15 + FastAPI + Nuxt 4
                      # exige .env.local en backend/ y frontend/ (lo comprueba antes de arrancar)

# Servicios sueltos, para depurar sin levantar el compose
poetry -P backend run uvicorn app.main:app --reload --port 8000
pnpm --dir frontend dev                                        # Nuxt dev server :3000
```

Para bajar el stack, `docker compose down` — no hay target `make stop`.

## Dependencias

**El proyecto Poetry vive en `backend/`, no en la raíz.** No hay `pyproject.toml` en la raíz, así
que `poetry install` y `poetry add` a secas fallan: todo lleva `-P backend`, igual que en el
Makefile. `backend/pyproject.toml` cubre backend **y** `ml/`.

```bash
poetry -P backend install                   # deps de backend y ml
poetry -P backend add <pkg>                 # deps Python (NUNCA pip ad-hoc)
poetry -P backend add --group dev <pkg>     # deps dev (pytest, ruff, mypy)
pnpm --dir frontend install
pnpm --dir frontend add <pkg>               # deps frontend (NUNCA npm/yarn)
corepack enable                             # pnpm vía Corepack
```

## Quality gates

```bash
make lint             # ruff check + ruff format --check + mypy (backend, ml, scripts, tests)
                      # + eslint + typecheck en frontend
make check            # lint + gitleaks + autocomprobación del escaneo + mapa de permisos.
                      # OBLIGATORIO antes de abrir un PR
make verificar        # superconjunto: pines, secretos, reproducibilidad, tokens, permisos,
                      # datos e históricos del tablero. Barrido previo a una entrega
```

`make check` incluye `pnpm lint`: no hace falta correrlo aparte. **No existe** `make format` ni
`make secrets-scan` sueltos; el formateo se corre con `poetry -P backend run ruff format` y el
escaneo va dentro de `check`.

`make verificar` necesita `data/aggregates/serie_tablero.parquet`, que no se versiona: sin
`make data` previo, falla. Por eso vive en `verificar` y no en `check`.

## Tests

```bash
make test             # pytest en tests/backend y tests/ml + vitest en frontend/

# Una suite o un solo test
poetry -P backend run pytest -c backend/pyproject.toml tests/backend -q
poetry -P backend run pytest -c backend/pyproject.toml tests/backend/test_auth.py::test_name -q
pnpm --dir frontend test
```

No existen `make test-backend` ni `make test-frontend`: son las dos mitades de `make test`,
arriba en su forma directa. Umbrales: backend >= 70 %, frontend >= 50 %. Reglas de qué se prueba
y qué no, en [`tests/AGENTS.md`](../../tests/AGENTS.md).

## Base de datos (dbmate)

```bash
make db-new SLUG=create_catalog   # nueva migración en db/migrations/
make db-up                        # aplica pendientes y regenera db/schema.sql
make db-rollback                  # revierte la última aplicada
make db-seed                      # seed del catálogo + seeds de db/seeds/ en orden
```

Los cuatro exigen `DATABASE_URL` en `backend/.env.local`. **No existe** `make db-status`; para el
estado, `bash scripts/dbmate.sh status`.

Regla: el esquema solo cambia por dbmate (`-- migrate:up` / `-- migrate:down`). Jamás
`SQLModel.metadata.create_all()` en producción, jamás editar una migración ya aplicada. Detalle en
[`db/AGENTS.md`](../../db/AGENTS.md).

## Datos sintéticos

```bash
make data             # silos Parquet + serie preagregada del tablero, semilla fija 20260720
```

Reproducible byte a byte. Lo que detecta un cambio de semilla es
`scripts/verificar_datos.sh` — corre `make data` una segunda vez en un temporal y compara los
Parquet byte a byte — más `tests/ml/test_generators.py`. **No** lo detecta
`verificar_reproducibilidad.sh`, que pese al nombre comprueba otra cosa: que `poetry.lock` y
`pnpm-lock.yaml` reproduzcan la instalación sin reescribirse. Anomalías inyectadas documentadas en
[`data/README.md`](../../data/README.md).

## Artefactos generados

```bash
make tokens           # tokens de diseño: @theme, paleta tipada, láminas y manifiesto
make permisos-ui      # mapa de permisos que la interfaz usa para ocultar módulos por rol
```

Las salidas de ambos son **generadas y no se editan a mano**. `make check` regenera el mapa de
permisos y difea; `make verificar` hace lo mismo con los tokens. Editar la salida a mano abre una
segunda política que puede discrepar de la del backend, y eso es justo lo que los verificadores
existen para distinguir de una regeneración legítima. Si acabas de correr `make permisos-ui`, haz
`git add` del archivo generado antes de `make check`.

## Nube (sin target de Make — se corre a mano)

```bash
gcloud config get-value project    # confirmar ANTES de nada: debe decir tareas-computo-nube
gcloud run deploy karisma-api --source backend  --region us-central1
gcloud run deploy karisma-web --source frontend --region us-central1

gcloud run services describe karisma-api --region us-central1 \
  --format='value(status.url,status.latestReadyRevisionName)'

# Migrar contra Cloud SQL: dbmate no habla el socket, hay que levantar el proxy
cloud-sql-proxy tareas-computo-nube:us-central1:karisma-pg --port 5432 &
DATABASE_URL="postgres://karisma_app:<pass>@127.0.0.1:5432/karisma?sslmode=disable" dbmate up
```

## Todavía no existe

Lo siguiente aparece en el plan y en skills, pero **no hay target ni script**. No lo invoques y no
cites su salida:

| Comando | Estado real | US que lo traería |
|---------|-------------|-------------------|
| `make tf-init` · `tf-plan` · `tf-apply` | `infra/` no existe; Terraform está congelado y el puente es `gcloud run deploy` | US-003 |
| `make cost-audit` · `make scale-to-zero-check` | sin script; la auditoría de costo se hace a mano con `gcloud billing` | US-032 |
| `scripts/measure_ttft.py` | no existe; el TTFT se mide a mano con `curl -N` y marca de tiempo del primer `event: token` | US-034 |
| CI/CD en `.github/workflows/` | `.github/` no existe todavía | US-004 |
