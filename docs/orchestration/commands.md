# Comandos — Portal Centralizado de Datos Financieros

> Lista completa de comandos Make/Poetry/pnpm/dbmate/pytest del proyecto. Resumen ejecutivo en [`AGENTS.md`](../../AGENTS.md).

## Desarrollo local

```bash
make dev                    # docker-compose: FastAPI + Nuxt 4 + PostgreSQL 15 (pgvector)
make stop

# Servicios sueltos (fuera de compose, para debug rápido)
poetry run uvicorn app.main:app --reload --port 8000       # backend solo (desde backend/)
pnpm dev                                                   # Nuxt 4 dev server :3000 (desde frontend/)
```

## Bootstrap / scaffolding

```bash
pnpm dlx nuxi init frontend         # scaffold Nuxt 4 (solo bootstrap inicial; estructura app/)
corepack enable && corepack use pnpm@latest
poetry install                      # deps backend/ml
poetry add <pkg>                    # deps Python (NUNCA pip ad-hoc)
poetry add --group dev <pkg>        # deps dev (pytest, ruff, mypy)
pnpm add <pkg>                      # deps frontend (NUNCA npm/yarn)
```

## Quality gates

```bash
make check                  # lint + secrets-scan (OBLIGATORIO antes de PR)
make lint                   # ruff check + ruff format --check + mypy + pnpm lint (eslint)
make format                 # ruff format + prettier
make secrets-scan           # gitleaks detect --no-banner --redact
```

## Base de datos (dbmate)

```bash
make db-new SLUG=create_catalog_tables    # dbmate new — nueva migración SQL en db/migrations/
make db-up                                # dbmate up — aplica migraciones y regenera schema.sql
make db-rollback                          # dbmate rollback — revierte la última migración
make db-status                            # migraciones aplicadas vs. pendientes
make db-seed                              # seeds: 7 usuarios, 200-400 entradas de catálogo, ~30 notas tribales

# dbmate directo (equivalente, requiere DATABASE_URL en .env.local)
dbmate new create_catalog_tables
dbmate up
dbmate rollback
```

Regla: migraciones SOLO vía dbmate (`db/migrations/*.sql` con `-- migrate:up/down`). Jamás `SQLModel.metadata.create_all()` en prod ni editar migraciones aplicadas.

## Datos sintéticos

```bash
make data                   # ml/data/generators.py: silos Parquet con semilla fija en data/silos/
                            # creditos 1-5M filas, liquidez ~1M, derivados ~500K, ~0.1% anomalías (data/README.md)
```

## Tests

```bash
make test                   # pytest backend/ml (cobertura >=70 %) + vitest/Vue Test Utils (>=50 %)
make test-backend           # solo pytest
make test-frontend          # solo vitest

# Un solo test / un solo archivo
pytest tests/backend/test_auth.py::test_login_wrong_password -q
poetry run pytest tests/backend/test_semantic_compiler.py -q
pnpm vitest run tests/components/ToolCallCard.spec.ts
```

## Agente y latencia (TTFT)

```bash
# Medición TTFT del chat SSE: tiempo hasta el primer evento `token` (meta p50 < 700 ms)
poetry run python scripts/measure_ttft.py --n 20 --endpoint http://localhost:8000/api/chat
# El script emite p50/p90/p99 leyendo el span OTel `llm.call` (atributo TTFT) o midiendo
# curl -N + timestamp del primer `event: token`.

# Verificación manual de streaming y cancelación
curl -N -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"message": "Saldo total de cartera vigente a ayer"}' \
  http://localhost:8000/api/chat        # Ctrl+C debe cancelar la llamada LLM en ms
```

## Terraform / Deploy

```bash
make tf-init                # terraform init en infra/
make tf-plan                # plan del módulo mínimo (2 Cloud Run, GCS, Secret Manager)
make tf-apply               # aplicar (requiere aprobación del equipo)
```

CI/CD: push → lint + tests; merge a `main` → build, Artifact Registry, `dbmate up`, deploy Cloud Run (GitHub Actions, skill `portal-cicd`).

## FinOps

```bash
make cost-audit             # gcloud billing: costos últimos 30 días vs. presupuesto $45 USD/mes
make scale-to-zero-check    # verifica min_instances=0 en ambos Cloud Run
```
