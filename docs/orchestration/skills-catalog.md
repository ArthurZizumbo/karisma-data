# Catálogo de Skills — Portal Centralizado de Datos Financieros

> Catálogo completo de las 27 skills `portal-*`. Resumen ejecutivo en [`AGENTS.md`](../../AGENTS.md). Detalle de cada skill en su `SKILL.md` correspondiente.

Skills viven en `.claude/skills/<nombre>/SKILL.md` con frontmatter YAML (`name`, `description`, `allowed-tools`). Claude las carga automáticamente por `description` o por invocación manual `/<nombre>`.

## Backend & Database (7)

| Skill | Descripción | Épica |
|-------|-------------|---------|
| `portal-backend-api` | Routers y endpoints FastAPI (`/api/auth/token`, `/api/users`, `/api/catalog/search`, `/api/{creditos\|liquidez\|derivados}`, `/api/export`, `/api/chat` SSE) | E1 · E2 · E3 |
| `portal-semantic-layer` | Capa semántica SMQ: métricas/dimensiones del catálogo, compilador determinístico consulta→Polars, 422 con fuzzy match | E2 |
| `portal-data-connectors` | Extractores async de silos Parquet: threadpool, caché TTL, graceful degradation por silo | E1 |
| `portal-export-jobs` | Exportaciones pesadas en segundo plano: BackgroundTasks, GCS signed URLs, estado del job | E1 |
| `portal-db-migrations` | dbmate SQL puro (`-- migrate:up/down`), extensión pgvector, índices, `schema.sql` versionado | E0–E2 (todas las US con schema) |
| `portal-db-models` | SQLModel: `app_user`, `catalog_source/field/tribal_note`, export jobs; seeds (7 usuarios, 200–400 entradas) | E1 · E2 |
| `portal-auth-jwt` | PyJWT HS256 + pwdlib Argon2 + SecurityScopes; roles operativo/analista/directivo/admin; 401/403; CRUD usuarios | E2 |

## Datos, Agente & RAG (4)

| Skill | Descripción | Épica |
|-------|-------------|---------|
| `portal-synthetic-data` | Generadores Polars+Faker con semilla fija: creditos 1–5M, liquidez ~1M, derivados ~500K, ~0.1% anomalías documentadas | E1 |
| `portal-catalog-rag` | Catálogo semántico con notas tribales (Tk-Boost), búsqueda híbrida keyword+coseno, embeddings Gemini, Hit Rate@3 ≥ 0.8 | E1 · E2 |
| `portal-adk-agent` | Google ADK `LlmAgent` manager→workers, tools gobernadas que propagan JWT, máx 5 tool calls, ruteo OOD | E3 |
| `portal-sse-streaming` | SSE `/api/chat`: eventos `tool_call`/`token`/`error`/`done`, Stop con cancelación real, Reintentar, TTFT | E3 |

## Frontend (4)

| Skill | Descripción | Épica |
|-------|-------------|---------|
| `portal-frontend-components` | Componentes Nuxt 4 (`app/`, `Lazy*`): login, homes por rol, catálogo, chat, panel admin | E4 · E2 (UI admin) |
| `portal-frontend-composables` | Composables y Pinia: `useChat`/SSE cliente, estado compartido dashboard↔chat (TwinBI), middleware + cookie JWT | E4 · E3 |
| `portal-echarts-dashboards` | Apache ECharts vía vue-echarts: ≥1M puntos con agregación server-side + `sampling`/`large`; degradación acordada 500K | E4 |
| `portal-ux-patterns` | Patrones UX 2026: Progressive Disclosure (≤2 clics), Predictive Insight Cards honestas, Tool-Call Visibility, linaje, workspaces | E4 · A4 |

## Infra & Observabilidad (4)

| Skill | Descripción | Épica |
|-------|-------------|---------|
| `portal-terraform-gcp` | Módulo `infra/` mínimo: 2 Cloud Run scale-to-zero, GCS, Secret Manager | E0 |
| `portal-cicd` | GitHub Actions: lint (ruff+eslint) + tests en push; merge a main → build, Artifact Registry, `dbmate up`, deploy | E0 · E5 |
| `portal-observability` | OpenTelemetry: spans `db.retrieval`/`rag.retrieval`/`llm.call`/`llm.postprocess`, `llm.usage.*`, `llm.prompt_hash` SHA-256, TTFT | E0 · E5 |
| `portal-finops` | Presupuesto < $45 USD/mes, alerta billing al 50 %, verificación scale-to-zero, costo por consulta del agente | E5 · §23 del plan |

## Seguridad & QA (4)

| Skill | Descripción | Épica |
|-------|-------------|---------|
| `portal-testing` | pytest + pytest-asyncio (cobertura ≥70 %), vitest/Vue Test Utils (≥50 %), pruebas 401/403 por rol, smoke tests | E5 · transversal |
| `portal-security-audit` | Auditoría: 100 % endpoints de datos con JWT, 0 contraseñas/prompts crudos en logs, secrets-scan, checklist pre-deploy | E2 · E5 |
| `portal-code-review` | Checklist de PR por épica, QA gate de AGENTS.md, verificación de rúbrica en entregables UX | Transversal |
| `portal-git-workflow` | Ramas `feature/E{epic}-US-XXX-{slug}`, Conventional Commits con scope de épica, cierre de US | Transversal |

## UX & Entregables (3)

| Skill | Descripción | Épica |
|-------|-------------|---------|
| `portal-ux-research` | Encuesta 13 preguntas (n≥15), 3 entrevistas, personas y mapas de empatía (matriz §5.3), journeys, card sorting, SUS ≥ 75 | EPIC UX |
| `portal-ux-deliverables` | Documentos A1–A5: rúbrica A1 desglosada, checklist §24, protocolo de absorción §25.2, APA de los 10 papers, PDF Canvas | EPIC UX · A1–A5 |
| `portal-synthetic-users` | Pre-validación PerceptUI: evaluadores LLM condicionados por las 6 personas para wireframes (A3) y alta fidelidad (A4) | EPIC UX |

## Transversal (1)

| Skill | Descripción | Épica |
|-------|-------------|---------|
| `portal-engram-memory` | Engram local SQLite+FTS5 como memoria dev-time entre sesiones (decisiones, rúbricas absorbidas, degradaciones, gates) | Dev tooling (no runtime) |
