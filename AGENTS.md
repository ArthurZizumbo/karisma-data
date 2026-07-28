# Portal Centralizado de Datos Financieros — Guía Operativa del Orquestador

**Proyecto**: Plataforma web de inteligencia financiera centralizada — curso TC4032 UX (MNA, ITESM), Equipo 8. Nombre comercial ⚠️ PENDIENTE (candidatos: Faro, Atlas Financiero, Prisma).

**Stack**: FastAPI + Polars + capa semántica | Nuxt 4 SSR + Apache ECharts + Pinia + Tailwind v4 | PostgreSQL 15 + pgvector + SQLModel + dbmate | PyJWT + pwdlib (Argon2) + SecurityScopes | Google ADK + Gemini 3.5 Flash-Lite | OpenTelemetry | Terraform GCP Cloud Run scale-to-zero.

> Plan vigente, US, calendario, presupuesto y métricas: [`context/planeacion_proyecto.md`](context/planeacion_proyecto.md) — **única fuente de verdad de las User Stories**; el harness no cita IDs de US. Papers 2026 en [`docs/papers/`](docs/papers/).

## Cómo usar esta guía

- **Raíz** ([`CLAUDE.md`](CLAUDE.md) y [`AGENTS.md`](AGENTS.md), espejos idénticos): normas transversales — aplican a todo el repo. Modificar uno exige sincronizar el otro.
- **Guía de carpeta** (`<dir>/AGENTS.md`): sobreescribe la raíz en caso de conflicto dentro de su scope. Se cargan on-demand al entrar al directorio.

## Doble pista y regla de oro

1. **Pista UX (la calificada)**: A1 (dom 26-jul, rúbrica publicada 15 pts) · A2 journey maps (2-ago) · A3 competitivo + IA (9-ago) · A4 alta fidelidad (16-ago) · A5 entrega final + SUS (23-ago). Rúbricas A2–A5 pendientes → protocolo de absorción §25.2 del plan.
2. **Pista de construcción**: los EPICs 0–5 producen el prototipo real que eleva las evidencias UX.

> **Regla de oro**: ante conflicto de tiempo, gana el entregable de la actividad UX de la semana. Capacidad 75 SP vs. 86 MUST: el déficit −11 se ejecuta con las válvulas de §10.2 del plan (congelar STRETCH E5→E4→E2, degradaciones acordadas del CRUD de usuarios y del dashboard de alto volumen).

## Comandos

```bash
make dev              # FastAPI + Nuxt 4 + PostgreSQL vía Docker Compose
make check            # lint + secrets-scan (OBLIGATORIO antes de PR)
make lint             # ruff + mypy + pnpm lint (eslint)
make test             # pytest backend/ml + vitest/Vue Test Utils frontend
make data             # genera silos sintéticos (semilla fija) en data/silos/
make db-new SLUG=x    # dbmate new — nueva migración SQL
make db-up            # dbmate up — aplicar migraciones
make db-rollback      # dbmate rollback

poetry add <pkg>      # deps Python (nunca pip ad-hoc)
pnpm add <pkg>        # deps frontend (nunca npm/yarn)

pytest tests/backend/test_auth.py::test_name -q   # un solo test
```

## Stack — Decisiones Irrevocables (NO cambiar sin equipo)

| Capa | Elección | Nota clave |
|------|----------|------------|
| Frontend | Nuxt 4 (estructura `app/`) + pnpm/Corepack | `shallowRef` default en `useFetch`; componentes `Lazy*`; `routeRules` SWR en dashboard directivo |
| Visualización | Apache ECharts (`vue-echarts`) | ≥1 M puntos con agregación server-side Polars + `sampling`/`large`; degradación acordada: 500 K |
| Estado / estilos | Pinia + TailwindCSS v4 | Estado compartido dashboard↔chat (patrón TwinBI) |
| API | FastAPI async + Pydantic v2 + Poetry | Pydantic Settings estricto: sin `DATABASE_URL`/`GEMINI_API_KEY`/`JWT_SECRET_KEY` la app NO arranca |
| Motor analítico | Polars 1.x + capa semántica (SMQ) | Compilador determinístico consulta→Polars; el LLM nunca redacta código libre |
| Persistencia | PostgreSQL 15 + pgvector + SQLModel | Catálogo, usuarios, export jobs, embeddings |
| Migraciones | dbmate | `db/migrations/*.sql` con `-- migrate:up/down`; `schema.sql` versionado; única vía de cambio de esquema |
| Auth | PyJWT (HS256) + pwdlib Argon2 + SecurityScopes ✔C7 | Roles como scopes: `operativo`/`analista`/`directivo`/`admin`; 401 sin token, 403 sin permiso |
| Agente | Google ADK (`LlmAgent` + `Runner` + `SessionService`) ✔C7 | Manager→workers; máx 5 tool calls; tools envuelven endpoints gobernados y propagan el JWT del usuario |
| LLM | Gemini 3.5 Flash-Lite | `thinking_level: medium` default; streaming SSE con cancelación real |
| Observabilidad | OpenTelemetry | Spans `db.retrieval`/`rag.retrieval`/`llm.call`/`llm.postprocess`; `llm.usage.*` + `llm.prompt_hash` SHA-256 |
| Cloud | GCP: Cloud Run scale-to-zero, Secret Manager, GCS, Artifact Registry + Terraform (`infra/`) | Presupuesto < $45 USD/mes, alerta billing al 50 % |
| CI/CD | GitHub Actions | push → lint+test; merge a `main` → build + `dbmate up` + deploy |

**Descartados — no reactivar**: fastapi-users, Alembic, Redis, Dagster, python-jose/passlib, refresh tokens, recuperación de contraseña, OAuth/SSO externo, RLS por fila, i18n, drift detection, switch A/B de LLM, EPICs 6–11 completos (consolidados en §18 del plan).

## Reglas de código NON-NEGOTIABLE

- **Idioma**: código (identificadores, comentarios, docstrings Google-style) en inglés; prosa visible al lector (UI, docs `.md`, entregables) en español neutro. **No hay i18n**: la UI es solo en español.
- **Sin emojis** en código, comentarios, prints, commits ni logs.
- **Logging**: `structlog.get_logger()`, nunca `print()` en producción.
- **Type hints** obligatorios en todo Python.
- **DRY**: función usada 2+ veces → `backend/app/utils/`, `ml/utils/` o `frontend/app/composables/`.
- **SoC**: router recibe → service procesa → model persiste. Tools ADK en `ml/agent/tools/`, nunca en routers; sin lógica de negocio en routers ni componentes Vue.
- **Seguridad por rol**: todo endpoint de datos con `Security(get_current_user, scopes=[...])`; matriz de permisos en `docs/security.md`; `/api/chat` propaga el Bearer del usuario a cada tool call (el agente jamás ve datos que el usuario no puede ver).
- **Anti-alucinación**: toda cifra en respuestas del agente proviene de un tool call; sin tool call no se muestran números; se cita la fuente del catálogo.
- **Capa semántica**: el LLM y el cliente componen consultas estructuradas validadas con Pydantic; solo el compilador determinístico genera expresiones Polars. Nunca ejecutar código libre.
- **Privacidad**: contraseñas y prompts crudos jamás en logs/trazas; solo `llm.prompt_hash` (SHA-256).
- **Secrets**: jamás hardcodear. `.env.local` en dev, Secret Manager en prod.
- **Migraciones**: solo `dbmate up` / `dbmate new`. Jamás `SQLModel.metadata.create_all()` en prod ni modificar migraciones aplicadas.
- **Datos sintéticos**: siempre semilla fija (reproducible); anomalías inyectadas documentadas en `data/README.md`; honestidad de demo (previsiones etiquetadas "proyección simulada").
- **Commits sin trailer `Co-Authored-By`** de asistentes IA — la autoría queda en el `Author:` real.

## QA Gate antes de PR

1. `make check` limpio (lint + secrets-scan).
2. Tests cobertura ≥70 % backend, ≥50 % frontend.
3. Si tocó schema: migración dbmate incluida y `dbmate up` verificado (`schema.sql` actualizado).
4. Si tocó permisos/auth: pruebas 401/403 parametrizadas por rol en verde.
5. Si tocó chat/agente: cancelación verificada (sin tareas colgadas) y evento `tool_call` emitido antes del texto.
6. Si es entregable UX: checklist de la actividad verificado contra la rúbrica (A1: §24 del plan).

## Git y PR

- Rama: `feature/E{epic}-US-XXX-{slug}` (épicas: `UX`, `E0`…`E5`).
- Conventional Commits con scope de épica: `feat(E2): ...`, `fix(E3): ...`, `docs(UX): ...`.
- `make check` limpio antes de abrir PR a `develop`.

## Routing por directorio

| Directorio | Guía | Especialidad |
|------------|------|--------------|
| `backend/` | [backend/AGENTS.md](backend/AGENTS.md) | FastAPI, SQLModel, auth JWT/scopes, SSE, export jobs, OTel |
| `frontend/` | [frontend/AGENTS.md](frontend/AGENTS.md) | Nuxt 4, ECharts, Pinia, chat streaming, patrones UX |
| `db/` | [db/AGENTS.md](db/AGENTS.md) | dbmate, pgvector, seeds, schema.sql |
| `ml/` | [ml/AGENTS.md](ml/AGENTS.md) | Generadores sintéticos, capa semántica, agente ADK, RAG |
| `docs/` | — | Entregables del curso, papers, orquestación, security.md |
| `infra/` | — | Terraform GCP (módulo mínimo MVP) |

## Skills y plan

- Qué skill `portal-*` cargar antes de cada acción: [`docs/orchestration/auto-invoke.md`](docs/orchestration/auto-invoke.md).
- Catálogo de skills y mapa skill→subagente: [`docs/orchestration/`](docs/orchestration/).
- Plan SCRUM, US, calendario, riesgos y métricas: [`context/planeacion_proyecto.md`](context/planeacion_proyecto.md).
- Al publicarse una rúbrica A2–A5: aplicar protocolo de absorción (§25.2 del plan) antes de cualquier trabajo de esa actividad.

## Estilo de respuesta

- Antes del primer tool call: una frase con el plan (≤20 palabras).
- Tareas con >3 tool calls o >30 s: `TodoWrite` al inicio.
- Código > prosa: el diff es la respuesta; respuestas triviales ≤4 líneas.
- Tool calls independientes en paralelo · Grep antes que Read · solo lo preguntado.
- Sin preámbulos ("Perfecto, voy a...", "Listo, he..."), sin narrar tool calls, sin emojis.
