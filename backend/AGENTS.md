# backend/ — FastAPI, Auth, Capa Semántica y Export Jobs

Guía de carpeta: sobreescribe la raíz dentro de `backend/`. Normas transversales en [`../AGENTS.md`](../AGENTS.md).

## Estructura

```
backend/app/
├── api/          # Routers: auth, users, catalog, creditos, liquidez, derivados, export, chat
├── services/     # Lógica de negocio: semantic_service, catalog_service, export_service, user_service, chat_service
├── models/       # SQLModel + contratos Pydantic (user, catalog, export, semantic)
├── core/         # auth.py (JWT/scopes), config.py (Pydantic Settings), database.py, telemetry.py
└── utils/        # DRY: errores tipificados, helpers compartidos
```

## Reglas — NON-NEGOTIABLE

- SoC estricto: router recibe → service procesa → model persiste. Cero lógica de negocio en `api/`.
- Todo endpoint de datos con `Security(get_current_user, scopes=[...])`; 401 sin token (`WWW-Authenticate: Bearer`), 403 sin permiso. Matriz de permisos en `docs/security.md`.
- Respuestas con modelos Pydantic (`response_model=`); nunca SQLModel crudo ni `hashed_password` serializado.
- Consultas analíticas SOLO vía capa semántica (`SemanticQuery` → compilador `ml/semantic/compiler.py`); nunca código libre del cliente o del LLM.
- `/api/chat` es SSE (`tool_call`, `token`, `error`, `done`); desconexión del cliente cancela la llamada LLM; el Bearer del usuario se propaga a cada tool.
- Exportaciones pesadas en `BackgroundTasks` con `job_id` inmediato; jamás trabajo pesado dentro del request.
- Pydantic Settings estricto: la app NO arranca sin `DATABASE_URL`, `GEMINI_API_KEY`, `JWT_SECRET_KEY`.
- `structlog.get_logger()`, nunca `print()`; contraseñas y prompts crudos jamás en logs (solo `llm.prompt_hash`).
- Esquema de BD solo vía dbmate (`db/`); jamás `SQLModel.metadata.create_all()` en prod.

## Comandos

```bash
poetry install                    # deps (nunca pip ad-hoc)
poetry add <pkg>
make dev                          # stack completo vía Docker Compose
poetry run pytest tests/backend -q
poetry run pytest tests/backend/test_auth.py::test_login_ok -q
make lint                         # ruff + mypy
make check                        # OBLIGATORIO antes de PR (lint + secrets-scan)
```

## QA gate específico

- Cobertura backend >= 70 %.
- Si tocaste permisos/auth: pruebas 401/403 parametrizadas por rol en verde.
- Si tocaste chat: cancelación verificada (sin tareas colgadas) y evento `tool_call` antes del texto.
- Si tocaste export: prueba de no-bloqueo (< 500 ms en catálogo durante export 1 M filas).

## Skills relevantes

| Acción | Skill |
|--------|-------|
| Routers/endpoints/SSE | `portal-backend-api` |
| Auth, scopes, CRUD usuarios | `portal-auth-jwt` |
| Consultas semánticas | `portal-semantic-layer` |
| Export en segundo plano | `portal-export-jobs` |
| Modelos SQLModel | `portal-db-models` |
| Búsqueda del catálogo | `portal-catalog-rag` |
