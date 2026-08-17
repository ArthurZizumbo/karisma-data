# Portal Centralizado de Datos Financieros — Guía Operativa del Orquestador

**Proyecto**: Plataforma web de inteligencia financiera centralizada — curso TC4032 UX (MNA, ITESM), Equipo 8. Nombre comercial: **Karisma Data** (decidido al entregar A1 el 26-jul-2026; usar siempre este nombre en UI, entregables y documentación).

**Stack**: FastAPI + Polars + capa semántica | Nuxt 4 SSR + Apache ECharts + Pinia + Tailwind v4 | PostgreSQL 15 + pgvector + SQLModel + dbmate | PyJWT + pwdlib (Argon2) + SecurityScopes | Google ADK + Gemini 3.5 Flash-Lite | OpenTelemetry | Terraform GCP Cloud Run scale-to-zero.

> Plan vigente, US, calendario, presupuesto y métricas: [`context/planeacion_proyecto.md`](context/planeacion_proyecto.md) — **única fuente de verdad de las User Stories**; el harness no cita IDs de US. Papers 2026 en [`docs/papers/`](docs/papers/).

## Cómo usar esta guía

- **Raíz** ([`CLAUDE.md`](CLAUDE.md) y [`AGENTS.md`](AGENTS.md), espejos idénticos): normas transversales — aplican a todo el repo. Modificar uno exige sincronizar el otro.
- **Guía de carpeta** (`<dir>/AGENTS.md` y `<dir>/CLAUDE.md`, también espejos): sobreescribe la raíz en caso de conflicto dentro de su scope. Se cargan on-demand al entrar al directorio. Cada una trae **Estado** (qué existe hoy), **Convenciones** (líneas ✅/❌) y **No tocar** (archivos generados) — leerlas ahorra más que releer código.
- **Decisiones fechadas** ([`docs/decisions/`](docs/decisions/)): el razonamiento de por qué una regla cambió vive ahí, no en esta guía. Aquí queda la regla.

## Doble pista y regla de oro

1. **Pista UX (la calificada)**: A1 (dom 26-jul, rúbrica publicada 15 pts) · A2 journey maps (2-ago) · A3 competitivo + IA (9-ago) · A4 alta fidelidad (16-ago) · A5 entrega final + SUS (23-ago). Rúbricas A2–A5 pendientes → protocolo de absorción §25.2 del plan.
2. **Pista de construcción**: los EPICs 0–5 producen el prototipo real que eleva las evidencias UX.

> **Regla de oro**: ante conflicto de tiempo, gana el entregable de la actividad UX de la semana. Capacidad 75 SP vs. 86 MUST: el déficit −11 se ejecuta con las válvulas de §10.2 del plan (congelar STRETCH E5→E4→E2, degradaciones acordadas del CRUD de usuarios y del dashboard de alto volumen).

## Comandos

```bash
make dev              # FastAPI + Nuxt 4 + PostgreSQL vía Docker Compose
make check            # lint + gitleaks + mapa de permisos (OBLIGATORIO antes de PR)
make lint             # ruff + mypy + eslint + typecheck. Ya va dentro de check
make test             # pytest tests/backend + tests/ml + vitest frontend
make verificar        # barrido completo previo a entrega: pines, reproducibilidad, tokens, datos
make data             # genera silos sintéticos (semilla fija) en data/silos/
make tokens           # regenera los tokens de diseño (salida generada, no editar a mano)
make permisos-ui      # regenera el mapa de permisos por rol (idem)
make db-new SLUG=x    # dbmate new — nueva migración SQL
make db-up            # dbmate up — aplicar migraciones
make db-rollback      # dbmate rollback

poetry -P backend add <pkg>     # deps Python. El proyecto Poetry vive en backend/, no en la raiz:
                                # `poetry add` a secas falla. Nunca pip ad-hoc
pnpm --dir frontend add <pkg>   # deps frontend (nunca npm/yarn)

# Un solo test (ruff, mypy y pytest exigen --config explicito: los tests viven en tests/)
poetry -P backend run pytest -c backend/pyproject.toml tests/backend/test_auth.py::test_name -q
```

## Stack — Decisiones Irrevocables (NO cambiar sin equipo)

| Capa | Elección | Nota clave |
|------|----------|------------|
| Frontend | Nuxt 4 (estructura `app/`) + pnpm/Corepack | `shallowRef` default en `useFetch`; componentes `Lazy*`. **Sin `routeRules` SWR**: tras la guarda por rol, una página cacheada le daría a un rol el HTML de otro. Se cachea el dato, no la página ([`frontend/AGENTS.md`](frontend/AGENTS.md)) |
| Visualización | Apache ECharts (`vue-echarts`) | ≥1 M puntos con agregación server-side Polars + `sampling`/`large`; degradación acordada: 500 K |
| Tablas de datos | TanStack Table (`@tanstack/vue-table`) | **Headless: cero estilo propio**, así que no contradice «sin sistema de diseño externo». Aporta orden anunciado con `aria-sort`, selección y densidad de 34 px, que siete tablas escritas a mano no tenían (US-A4-EXCELENCIA, 15-ago-2026) |
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

**Descartados — no reactivar**: fastapi-users, Alembic, Redis, Dagster, python-jose/passlib, refresh tokens, recuperación de contraseña, OAuth/SSO externo, RLS por fila, drift detection, switch A/B de LLM, EPICs 6–11 completos (consolidados en §18 del plan).

## Reglas de código NON-NEGOTIABLE

- **Idioma**: código (identificadores, comentarios, docstrings Google-style) en inglés; prosa visible al lector (docs `.md`, entregables) en español neutro. **La interfaz web es bilingüe español + inglés con i18n real**: ninguna cadena visible se escribe en un componente — [ADR-001](docs/decisions/ADR-001-ui-bilingue-i18n-real.md), operativa en [`frontend/AGENTS.md`](frontend/AGENTS.md). Los entregables PDF del curso siguen siendo solo en español.
- **Sin emojis** en código, comentarios, prints, commits ni logs.
- **El estilo del portal y el del informe son sistemas SEPARADOS.** `docs/entregables/estilo/uxdoc.sty` es la hoja de estilo **del informe** y está **congelada**: A1, A2 y A3 compilan contra ella. Prohibido derivar el aspecto del portal de esa paleta — está optimizada para tinta sobre papel. Del portal al informe viaja **contenido, no formato**. Razonamiento completo y una discrepancia abierta sobre cuál es la fuente real de los tokens: [ADR-002](docs/decisions/ADR-002-estilo-portal-separado-del-documento.md).
- **Logging**: `structlog.get_logger()`, nunca `print()` en producción.
- **Type hints** obligatorios en todo Python.
- **DRY**: función usada 2+ veces → `backend/app/utils/`, `ml/utils/` o `frontend/app/composables/`.
- **Tests solo sobre comportamiento que existe. PROHIBIDO** probar placeholders o andamiaje. Antes de escribir un test, responder qué defecto concreto lo haría fallar; si no hay respuesta, no se escribe. La cobertura es piso, nunca objetivo: **un 100 % sobre andamiaje vale menos que un 70 % sobre lógica**. Detalle operativo en [`tests/AGENTS.md`](tests/AGENTS.md).
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

1. `make check` limpio (lint + gitleaks + mapa de permisos). **No hay CI todavía** — `.github/` es US-004, así que esto corre en tu máquina o no corre.
2. `make test` en verde. Los umbrales están configurados, no son honor system: `--cov-fail-under=70` en `backend/pyproject.toml` y `thresholds: 50` en `frontend/vitest.config.ts`.
3. Si tocó schema: migración dbmate incluida y `dbmate up` verificado (`schema.sql` actualizado).
4. Si tocó permisos/auth: pruebas 401/403 parametrizadas por rol en verde.
5. Si tocó chat/agente: cancelación verificada (sin tareas colgadas) y evento `tool_call` emitido antes del texto.
6. Si es entregable UX: checklist de la actividad verificado contra la rúbrica (A1: §24 del plan).
7. Ningún test nuevo sobre placeholders ni sobre código que aún no existe (ver regla en NON-NEGOTIABLE). Si un test no puede fallar, se borra, no se ajusta.

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
| `tests/` | [tests/AGENTS.md](tests/AGENTS.md) | pytest, vitest, mocks obligatorios, umbrales de cobertura |
| `docs/` | [docs/AGENTS.md](docs/AGENTS.md) | Entregables del curso, papers, orquestación, artefactos por US |
| `docs/decisions/` | — | ADR: decisiones fechadas y su razonamiento, fuera de esta guía |
| `design/` | — | Sistema de tokens del portal (sin guía propia todavía) |
| `scripts/` | — | Generadores y verificadores que corre el Makefile (sin guía propia) |

`infra/` y `.github/` **no existen todavía**: Terraform está congelado (el puente es `gcloud run deploy`) y el pipeline es US-004, pendiente.

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
