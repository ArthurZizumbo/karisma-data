# backend/ — API FastAPI: auth, catálogo, linaje y serie del tablero

> Sub-guía del orquestador. Las reglas transversales viven en [`../AGENTS.md`](../AGENTS.md) — aquí no se repiten, solo lo operativo de `backend/`.

## Estado

**Ocho routers montados en `create_app()`, los ocho escritos** (eran cinco hasta el 13-ago-2026; `users`, `chat` y `export` entraron ese dia con US-018, US-023 y US-009):

- `api/health.py` — `GET /health`. Sin token (sonda de Compose y Cloud Run) y **fuera de `/api`**: el guardián de permisos no lo gobierna.
- `api/auth.py` — `POST /api/auth/token` (pública), `GET /api/auth/me` (cualquier sesión) y `POST /api/auth/demo`, en un `demo_router` que solo se monta si `DEMO_LOGIN_ENABLED`; apagada, la ruta no existe (404, no 403).
- `api/catalog.py` — `GET /api/catalog/search` y `GET /api/catalog/{entry_id}`. Ranking `tsvector` parametrizado; la fase híbrida con pgvector no está escrita.
- `api/lineage.py` — `GET /api/catalog/{entry_id}/lineage`. Router propio con el prefijo del catálogo.
- `api/metrics.py` — `GET /api/metrics/series`, scope `analista`. Handler `def` síncrono a propósito: codificar medio millón de floats es trabajo de hilo, no del event loop.
- `api/chat.py` — `POST /api/chat`, scope `operativo`. **Unico `StreamingResponse` del repositorio**: SSE con `Cache-Control: no-cache` y `X-Accel-Buffering: no`. Router delgado de verdad — resuelve el proveedor por nombre y delega en `services/chat_stream.py`; la cancelacion sigue al socket del cliente.
- `api/export.py` — `POST /api/export` (202 y encola), `GET /api/export`, `GET /api/export/{job_id}` y `GET /api/export/{job_id}/download`. Los cuatro con scope `analista`: una extraccion masiva es la salida de datos con mas riesgo de fuga del portal. Pedir el trabajo de otro devuelve **404, no 403** — un 403 confirmaria el `job_id` y lo volveria oraculo de enumeracion. El `admin` lee metadatos ajenos (gobierno) pero nunca su enlace ni su archivo. El trabajo corre en `BackgroundTasks`, con `scan_parquet` + `sink_csv` en `asyncio.to_thread`: `/health` sigue por debajo de 500 ms mientras se exporta.

> Falta aqui la ficha de `api/users.py` (US-018), que se monto el mismo dia en paralelo. No es un
> olvido: la escribe su duena, para que la descripcion venga de quien conoce las decisiones detras.

**No existen todavía**, aunque `SCOPE_REGISTRY` ya publique su fila con estado `planificado`: `/api/query/records`, `/api/metrics/aggregate` y `/api/summaries/executive`. Tampoco hay `chat_service` ni `semantic_service` — el transporte del chat **no** es un service de dominio y no lleva ese sufijo: se llama `services/chat_stream.py`, y a su lado nace `services/proveedores/`, el primer paquete con **costura por `Protocol`** del repositorio (`ProveedorDeTokens` + `obtener_proveedor`), pensado para que conectar Gemini no toque una linea de contrato; `user_service.py` es solo lado de lectura (`UserRepository` + `SqlUserRepository`). **`ml/semantic/compiler.py` no existe**: el único compilador determinista de hoy es `services/series_service.py`, que traduce `SeriesParams` a un plan lazy de Polars.

**`services/almacen/` es la segunda costura por `Protocol` del repositorio**, y la regla que la
sostiene es un conteo, no una convencion: `grep -rn "export_storage_backend" backend/app --include=*.py | wc -l`
tiene que dar **2** —la declaracion en `config.py` y el `if` de `crear_almacen`— y hay una prueba que
repite ese conteo. Un segundo `if` sobre el backend de almacenamiento en cualquier otro archivo es lo
que pudre esta clase de fachada. El endpoint de descarga no pregunta por el backend configurado sino
por la **capacidad** (`isinstance` sobre `AlmacenServidoPorLaApi`, un `Protocol` `runtime_checkable`):
con GCS los enlaces los firma y los sirve el bucket, no esta API.

## Estructura

```
backend/
├── app/
│   ├── api/       auth · catalog · chat · health · lineage · metrics · users · export
│   ├── services/  auth · catalog · export · lineage · series · user  (sufijo _service)
│   │              chat_stream.py + proveedores/  (transporte SSE y su costura)
│   │              almacen/  (Protocol + local firmado con HMAC + GCS; un solo punto de eleccion)
│   ├── models/    catalog · chat · export · lineage · series · user   (SQLModel espeja lo que creó dbmate;
│   │              chat.py son eventos SSE en Pydantic puro, sin tabla detrás)
│   ├── core/      auth · config · database · permissions · scopes · security
│   ├── utils/     serie_frame.py (marco binario KSER1) — nada más
│   └── main.py    settings → logging → routers → assert_scope_coverage()
├── pyproject.toml ruff, mypy y pytest se configuran AQUI, apuntando a tests/ de la raíz
└── Dockerfile     multi-stage; el contexto de build es backend/
```

## Comandos

Todo desde la raíz del repo. `-P backend` no es opcional: el proyecto Poetry no está en la raíz.

```bash
poetry -P backend add <pkg>
poetry -P backend run pytest -c backend/pyproject.toml tests/backend   # + ruta::test
make dev          # db + api + web por Docker Compose
make lint         # ruff + mypy con --config explicito, y eslint/typecheck del frontend
make test         # tests/backend + tests/ml + vitest
make check        # lint + gitleaks + verificar_permisos_ui.sh. Obligatorio antes del PR
make permisos-ui  # regenera el mapa de permisos que consume la interfaz
make db-new SLUG=x · make db-up · make db-rollback · make db-seed
```

## Convenciones

- ❌ Dejar que el LLM o el cliente redacten expresiones Polars. Solo las genera el compilador determinista —hoy `services/series_service.py`, mañana `ml/semantic/compiler.py`—; cliente y agente mandan vocabulario cerrado validado con Pydantic (`SeriesParams`, y la `SemanticQuery` cuando exista).
- ✅ Ruta nueva bajo `/api` ⇒ fila nueva en `SCOPE_REGISTRY` (`core/permissions.py`) en el mismo commit: `assert_scope_coverage()` corre al construir la app y una ruta sin fila impide arrancar.
- ✅ Un solo vocabulario de roles: `Scope` de `core/scopes.py`. Nunca un `Literal["admin", ...]` en otro módulo.
- ✅ `Security(get_current_user, scopes=[...])` antes de `Depends(get_session)` en la firma: el anónimo se rechaza sin abrir sesión de base de datos.
- ✅ Errores con código estable en `detail.codigo` (`ErrorCode`, `SeriesErrorCode`, `LineageErrorCode`); ❌ nunca una frase en español, que la interfaz bilingüe no puede traducir.
- ✅ El router traduce a HTTP las excepciones del service (`SeedMissingError`, `FieldNotFoundError`), que se declaran en `services/` junto a la lógica.
- ✅ `response_model=` siempre. Jamás serializar `AppUser` ni `hashed_password`.
- ❌ Trabajo pesado dentro del request: la exportación va a `BackgroundTasks` con `job_id` inmediato.
- ❌ Declarar `async def` un handler que hace CPU o E/S de disco.
- ❌ Aflojar el pin exacto `polars==1.43.2`: la reproducibilidad de los Parquet depende del escritor.

## No tocar

- `frontend/app/utils/permisos.generated.ts` — se genera desde `core/scopes.py` y `core/permissions.py` con `scripts/generar_permisos_ui.py`. Editarlo a mano abre una **segunda política de permisos** que puede discrepar de `ROLE_HIERARCHY`; `scripts/verificar_permisos_ui.sh` corre dentro de `make check`, regenera y difiere. Si cambias un scope: `make permisos-ui`, `git add` de la salida, y recién entonces `make check`.
- El bloque entre `<!-- matriz-permisos:inicio -->` y `<!-- matriz-permisos:fin -->` de `docs/security.md` — sale del mismo registro; lo vigila `test_security_doc.py`.
- `db/schema.sql` y toda migración aplicada — el esquema se regenera con `make db-up`; un error se corrige con una migración nueva.
- `backend/poetry.lock` (solo vía `poetry -P backend add`), `backend/.env.local`, `.mypy_cache/`, `.ruff_cache/`, `.pytest_cache/`.

## Tests

Viven en `tests/backend/` **en la raíz del repo**, no dentro de `backend/`; por eso cada herramienta recibe `-c`/`--config` explícito. `tests/backend/permisos/` cubre la matriz 401/403 por rol, el guardián de scopes y la sincronía con `docs/security.md`. Umbral `--cov-fail-under=70` sobre `backend/app` **y** `ml` juntos. Lo que necesita PostgreSQL lleva `@pytest.mark.integracion` y se omite sin `KARISMA_TEST_DATABASE_URL`; el resto sustituye `get_user_repository` y no abre conexión.

## Skills

| Acción | Skill |
|---|---|
| Router, endpoint, SSE | `portal-backend-api` |
| Auth, scopes, CRUD de usuarios | `portal-auth-jwt` |
| Consulta estructurada y compilador | `portal-semantic-layer` |
| Exportación en segundo plano | `portal-export-jobs` |
| Modelos SQLModel | `portal-db-models` |
| Búsqueda del catálogo | `portal-catalog-rag` |
| Pruebas y cobertura | `portal-testing` |
