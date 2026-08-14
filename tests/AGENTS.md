# tests/ — suites reales, dobles y la regla de que un test debe poder fallar

> Sub-guia del orquestador. Las reglas transversales viven en [`../AGENTS.md`](../AGENTS.md) — aqui no se repiten, solo lo operativo de `tests/`.

## Estado

38 archivos versionados, 33 de ellos modulos de prueba. Lo que existe HOY:

- **`tests/backend/`** (21 modulos): settings estrictos y DSN, `/health`, migraciones y `db/schema.sql` como texto versionado, `.env.example`, autenticacion (token, demo, los cinco vectores de 401 de `get_current_user`, y lo que el login puede loguear), catalogo y linaje —contrato con sesion doblada mas integracion— y la serie del tablero (servicio, endpoint, codificador KSER1).
- **`tests/backend/permisos/`** (4 modulos; `__init__.py` deliberado): jerarquia de roles, guardia de cobertura de scopes contra apps sinteticas, matriz 401/403 por rol sobre una app sonda y `docs/security.md` blindado contra derivas.
- **`tests/ml/`** (7 modulos): generadores deterministas, contratos de columna congelados, anomalias y su auditor, agregados, manifiesto, semillas y seed del catalogo.
- **`tests/entregables/`**: tokens de A4. **No lo corre `make test`**; se invoca con `--no-cov`.
- **`tests/fixtures/`**: testigo dorado KSER1 que leen `test_serie_frame.py` y `serieBinaria.spec.ts`.

El frontend no vive aqui: 37 specs en `frontend/test/` (vitest + happy-dom). **No existe todavia** suite de capa semantica ni de agente ADK: no escribas helpers anticipandolas. **No hay CI**: la puerta es local.

**Chat SSE (US-023) ya tiene suite**: `test_chat_sse.py` y `test_chat_cancelacion.py`. Dos cosas de ahi se aplican a cualquier prueba futura de streaming. Primera: la cancelacion se prueba **sin socket**, porque `request.is_disconnected()` no dispara con el cliente ASGI y una prueba escrita contra el `Request` seria un adorno que pasa haga lo que haga el transporte; por eso `chat_stream.transmitir` recibe el detector como `Callable`. Segunda: **el cliente ASGI acumula el cuerpo entero**, asi que `iter_raw()` devuelve un solo trozo produzca lo que produzca el servidor — la entrega incremental se mide sobre el generador y el socket real solo en `docs/manual-test/us-023.md`.

**Trampa de `capture_logs`**: `configure_logging()` instala un `filtering_bound_logger` al nivel de `LOG_LEVEL`, y ese filtro actua **antes** que los procesadores. Como el entorno de la suite fija `WARNING`, un `logger.info(...)` no llega nunca a `structlog.testing.capture_logs`, que solo intercambia procesadores. La fixture `registro_visible` de `test_chat_cancelacion.py` es el patron: baja el filtro a `NOTSET` y sustituye el logger del modulo por uno sin cachear.

## Estructura

```
tests/
├── backend/  conftest.py (MINIMAL_ENV, dobles, fabrica de tokens) · 19 test_*.py
│             permisos/ (__init__, conftest + 4 modulos)
├── ml/       data/consultas_referencia.json (20 congeladas, Hit Rate@3 >= 0.8)
│             fixtures/creditos_smoke.json · 7 test_*.py
├── entregables/test_tokens_a4.py
└── fixtures/serie_frame_golden.{b64,json}
```

## Comandos

```bash
make test    # pytest tests/backend tests/ml + vitest

PYT="poetry -P backend run pytest -c backend/pyproject.toml"
$PYT tests/backend/permisos -q                  # una suite
$PYT tests/backend/test_auth_token.py::test_x   # un caso
KARISMA_TEST_DATABASE_URL=postgres://... $PYT -m integracion
$PYT tests/entregables --no-cov -q
pnpm --dir frontend test                        # vitest run --coverage
```

`-c backend/pyproject.toml` **siempre**: la config vive en un directorio hermano; sin la bandera se pierden `pythonpath` y `--strict-markers`.

## Convenciones

- ✅ Antes de escribirlo, deja en su docstring que defecto concreto lo pone rojo. Sin respuesta, no se escribe.
- ❌ Probar placeholders, andamiaje o marcado que la siguiente US va a reescribir.
- ❌ Aserciones que no pueden fallar: que un archivo exista, que una guardia apruebe una app cuyas rutas ya cumplen todas.
- ✅ Si el sujeto es una guardia, ejercerla contra objetos sinteticos, uno por clase de defecto (`permisos/test_scope_coverage.py`).
- ✅ Verificar una salida con la biblioteca estandar, nunca con el modulo que la produjo (`test_serie_frame.py` usa `struct`).
- ❌ Sumar casos triviales para levantar el porcentaje: el umbral es piso, no meta.
- ✅ Nombre, docstring y asercion miden lo mismo.
- ✅ Probar solo los archivos nuevos o modificados de la US; si una suite ajena enrojece, se arregla la causa, no el test.
- ❌ Borrar o marcar `skip` para dejar la suite en verde.
- ✅ Tocaste auth o scopes → matriz 401/403 parametrizada por rol en `permisos/`.
- ✅ Tocaste SSE → prueba que la cancelacion cierra el generador sin tareas colgadas y que `tool_call` precede al texto.
- ✅ Prueba con PostgreSQL → marcador `integracion`, `skipif` sobre `KARISMA_TEST_DATABASE_URL` y transaccion revertida.
- ❌ Ejercer SQL de PostgreSQL contra SQLite: sin `tsvector` ni `CHECK` equivalentes medirias otro motor. Sujeto con mitad pura y mitad SQL → dos archivos: contrato e integracion.

## Que se mockea

| Dependencia | Como |
|-------------|------|
| Gemini | Jamas se llama; hoy es solo una clave falsa en `MINIMAL_ENV`. Con agente se dobla el cliente: ninguna prueba gasta tokens |
| GCS / Cloud SQL | Ninguna prueba abre conexion a la nube; integracion usa PostgreSQL local |
| PostgreSQL | Sesion sustituida via `dependency_overrides`; motor real solo bajo `integracion` |
| Usuarios y tokens | `get_user_repository` doblado; los JWT los firma la fabrica del conftest |
| Auto-imports de Nuxt | `useCookie`, `useState`, `useHead`, `useRuntimeConfig`, `useRequestFetch` y Pinia en `frontend/test/configuracion.ts`; `$fetch` por spec |

## Umbrales

**Configurados**, no solo en la prosa del QA gate: el comando falla solo.

- Backend >= 70 %: `--cov=backend/app --cov=ml --cov-fail-under=70` en `addopts` de `backend/pyproject.toml`, con `branch = true`.
- Frontend >= 50 %: `thresholds` de lines, functions, branches y statements en `frontend/vitest.config.ts` (v8 sobre `app/**` y `server/**`).
- `tests/entregables/` no entra en la medicion; por eso corre con `--no-cov`.

## Skills

| Accion | Skill |
|--------|-------|
| Escribir o correr cualquier prueba | `portal-testing` |
| Matriz 401/403, scopes, fugas en logs | `portal-security-audit` |
| Cancelacion SSE y orden de eventos | `portal-sse-streaming` |
| Cobertura de un PR | `portal-code-review` |
| Consultas de referencia, Hit Rate@3 | `portal-catalog-rag` |
| Fixtures de silos sinteticos | `portal-synthetic-data` |
