# Portal Centralizado de Datos Financieros — pointer

Claude Code carga `../CLAUDE.md` y otros agentes de código (Codex, Cursor, etc.) cargan `../AGENTS.md`. Ambos archivos son **espejos idénticos** del orquestador único — modificar uno requiere sincronizar el otro.

**Estructura canónica de orquestación**:

- [`../AGENTS.md`](../AGENTS.md) y [`../CLAUDE.md`](../CLAUDE.md) — orquestador único (mismo contenido): identidad, doble pista y regla de oro, decisiones irrevocables, reglas globales, quality gates, git, routing por directorio, estilo de respuesta.
- [`../context/planeacion_proyecto.md`](../context/planeacion_proyecto.md) — plan SCRUM definido (EPIC UX + E0–E5, roadmap, riesgos, métricas, rúbrica A1). **Única fuente de verdad de las User Stories** — el harness no cita IDs de US.
- [`../docs/orchestration/`](../docs/orchestration/) — auto-invoke table, catálogo de skills, mapa skill↔subagente, comandos Make.
- [`../docs/decisions/`](../docs/decisions/) — ADR: decisiones fechadas y su razonamiento. La raíz guarda la regla; el porqué vive aquí.
- `<dir>/AGENTS.md` y `<dir>/CLAUDE.md` — guías de carpeta, también espejos byte-idénticos, en `backend/`, `frontend/`, `db/`, `ml/`, `tests/` y `docs/`.
- `skills/` — skills `portal-*`.
- `agents/` — subagentes profundos (Task tool).
- `settings.json` — configuración Claude Code (permisos engram).

> **Regla de oro del proyecto**: ante conflicto de tiempo, gana el entregable de la actividad UX de la semana (A1–A5, entregas dominicales). Ver §10.3 del plan.

> **Quality gates**: sin pre-commit y **sin CI todavía** — `.github/` no existe (es US-004). Hoy las garantías (ruff, mypy, eslint, gitleaks, mapa de permisos) viven solo en `make check`, y el barrido completo en `make verificar`. Esquema de BD solo vía dbmate. Ver §"QA Gate" en `../AGENTS.md` y [`../docs/orchestration/commands.md`](../docs/orchestration/commands.md).
