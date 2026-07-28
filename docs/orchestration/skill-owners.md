# Mapa Skill → Subagente owner — Portal Centralizado de Datos Financieros

> Cada skill tiene 1+ subagente que la opera. Las skills transversales (git, memoria dev) son self-served. Auto-invoke en [`auto-invoke.md`](auto-invoke.md). Subagentes en [`.claude/agents/`](../../.claude/agents/).

| Skill | Owner(s) |
|-------|----------|
| `portal-backend-api` | `backend-engineer` |
| `portal-semantic-layer` | `backend-engineer`, `data-engineer` |
| `portal-data-connectors` | `backend-engineer`, `data-engineer` |
| `portal-export-jobs` | `backend-engineer`, `platform-engineer` |
| `portal-db-migrations` | `data-engineer`, `backend-engineer` |
| `portal-db-models` | `backend-engineer` |
| `portal-auth-jwt` | `backend-engineer`, `security-reviewer` |
| `portal-synthetic-data` | `data-engineer` |
| `portal-catalog-rag` | `data-engineer`, `agent-engineer` |
| `portal-adk-agent` | `agent-engineer`, `backend-engineer` |
| `portal-sse-streaming` | `agent-engineer`, `frontend-engineer`, `backend-engineer` |
| `portal-frontend-components` | `frontend-engineer` |
| `portal-frontend-composables` | `frontend-engineer` |
| `portal-echarts-dashboards` | `frontend-engineer` |
| `portal-ux-patterns` | `frontend-engineer`, `ux-researcher` |
| `portal-terraform-gcp` | `platform-engineer`, `finops-auditor` |
| `portal-cicd` | `platform-engineer` |
| `portal-observability` | `platform-engineer`, `agent-engineer` |
| `portal-finops` | `finops-auditor`, `platform-engineer` |
| `portal-testing` | `backend-engineer`, `frontend-engineer` |
| `portal-security-audit` | `security-reviewer` |
| `portal-code-review` | `security-reviewer` |
| `portal-git-workflow` | transversal (cualquier subagente al commitear/cerrar US) |
| `portal-ux-research` | `ux-researcher` |
| `portal-ux-deliverables` | `deliverable-writer`, `ux-researcher` |
| `portal-synthetic-users` | `ux-researcher`, `agent-engineer` |
| `portal-engram-memory` | self-served (dev-time only, cualquier sesión Claude Code) |

## Subagentes (9 totales en `.claude/agents/`)

| Subagente | Cuándo invocarlo |
|-----------|------------------|
| `backend-engineer` | FastAPI, capa semántica, auth JWT/scopes, export jobs, SSE server-side, SQLModel |
| `frontend-engineer` | Nuxt 4, componentes/composables, Pinia, ECharts, chat streaming cliente, patrones UX en código |
| `agent-engineer` | Tools ADK, manager→workers, ruteo OOD, RAG del catálogo, streaming del agente, eval Hit Rate@3 |
| `data-engineer` | Silos sintéticos, conectores async, migraciones dbmate, seeds del catálogo, embeddings |
| `platform-engineer` | Terraform GCP, CI/CD GitHub Actions, Docker Compose, OTel, deploy Cloud Run |
| `security-reviewer` | Auditoría OWASP, RBAC 401/403, secret scanning, review de PR, privacidad de logs |
| `ux-researcher` | Instrumentos de campo, personas/mapas, journeys, card sorting, SUS, pre-validación sintética |
| `deliverable-writer` | Redacción/maquetación de A1–A5, rúbricas y checklists, referencias APA, PDF Canvas |
| `finops-auditor` | Presupuesto < $45 USD/mes, budget alerts, scale-to-zero, costo por consulta LLM |
