# Auto-Invoke Table — Portal Centralizado de Datos Financieros

> Tabla operativa de qué skill cargar antes de cada acción. Catálogo en [`skills-catalog.md`](skills-catalog.md). Mapa skill→subagente en [`skill-owners.md`](skill-owners.md).

## Backend & Database

| Acción | Skill |
|--------|-------|
| Crear/modificar endpoint FastAPI | `portal-backend-api` |
| Definir métrica/dimensión o compilar SMQ→Polars | `portal-semantic-layer` |
| Conector async de silo (threadpool, caché TTL, degradation) | `portal-data-connectors` |
| Export en segundo plano (BackgroundTasks → GCS signed URL) | `portal-export-jobs` |
| Crear migración dbmate / índice / extensión pgvector | `portal-db-migrations` |
| Crear/modificar modelo SQLModel (`app_user`, `catalog_*`, jobs) | `portal-db-models` |
| Auth JWT, scopes, matriz RBAC, CRUD usuarios | `portal-auth-jwt` |
| Endpoint 422 con fuzzy match del catálogo | `portal-backend-api` + `portal-semantic-layer` |

## Frontend

| Acción | Skill |
|--------|-------|
| Crear componente Vue/Nuxt 4 (`Lazy*`, `app/`) | `portal-frontend-components` |
| Crear composable / Pinia store (estado dashboard↔chat) | `portal-frontend-composables` |
| Dashboard/gráfica ECharts (≥1M pts, sampling/large) | `portal-echarts-dashboards` |
| Revelación progresiva, tarjetas predictivas, workspaces por rol | `portal-ux-patterns` |
| Chat SSE en el cliente (tarjetas tool-call, Stop, Reintentar) | `portal-frontend-composables` + `portal-sse-streaming` |

## Agente & RAG

| Acción | Skill |
|--------|-------|
| Crear tool ADK nuevo (`buscar_catalogo`, `consultar_metricas`, ...) | `portal-adk-agent` |
| Configurar manager→workers (ruteo catálogo/datos/OOD) | `portal-adk-agent` |
| Catálogo semántico, embeddings, score híbrido, Hit Rate@3 | `portal-catalog-rag` |
| Streaming SSE `/api/chat` + cancelación real | `portal-sse-streaming` + `portal-backend-api` |
| Generar silos sintéticos (semilla fija, anomalías documentadas) | `portal-synthetic-data` |

## Infra & Observabilidad

| Acción | Skill |
|--------|-------|
| Crear/modificar módulo Terraform (Cloud Run, GCS, Secret Manager) | `portal-terraform-gcp` |
| Crear/modificar workflow GitHub Actions | `portal-cicd` |
| Spans OTel (`llm.call`, `llm.usage.*`, `llm.prompt_hash`, TTFT) | `portal-observability` |
| Auditar costo cloud / budget alerts / scale-to-zero | `portal-finops` |

## Seguridad & QA

| Acción | Skill |
|--------|-------|
| Audit de seguridad (OWASP, secrets, 401/403 por rol) | `portal-security-audit` |
| Escribir tests pytest / vitest / Vue Test Utils | `portal-testing` |
| Review de PR | `portal-code-review` |
| Crear commit / branch / PR | `portal-git-workflow` |
| Cerrar User Story | `portal-git-workflow` |

## UX & Entregables

| Acción | Skill |
|--------|-------|
| Diseñar/ejecutar instrumentos (encuesta 13 preguntas, entrevistas) | `portal-ux-research` |
| Elaborar personas / mapas de empatía (matriz §5.3, Anexo B) | `portal-ux-research` |
| Escenarios y journey maps con trazabilidad cita→pain→oportunidad | `portal-ux-research` |
| Benchmark competitivo, sitemap, card sorting (A3) | `portal-ux-research` + `portal-ux-deliverables` |
| Prototipo web navegable de alta fidelidad y guía de estilos (A4) | `portal-ux-patterns` + `portal-frontend-components` + `portal-ux-deliverables` |
| Revisar defectos de interfaz antes de congelar pantallas | [`checklist-ui.md`](checklist-ui.md) (archivo, no skill) |
| Pre-validación sintética de wireframes/prototipos (PerceptUI) | `portal-synthetic-users` |
| Prueba de usabilidad SUS (≥5 participantes, meta ≥75) | `portal-ux-research` |
| Redactar/maquetar documento de actividad (PDF Canvas) | `portal-ux-deliverables` |
| Absorción de rúbrica recién publicada (protocolo §25.2) | `portal-ux-deliverables` |

## Memoria

| Acción | Skill |
|--------|-------|
| Persistir decisión/gate/degradación entre sesiones Claude Code | `portal-engram-memory` (dev) |
