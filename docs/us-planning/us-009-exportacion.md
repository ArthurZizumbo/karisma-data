# Planeación US-009 — Exportación en segundo plano (alcance S4)

> **AVISO DE COLISIÓN DE NOMBRES.** Este documento **no** es el de US-UX-09 (Guía de estilos, A4).
> Ya existen `docs/us-planning/us-009.md` y `docs/us-handoff/us-009.md` y pertenecen a **US-UX-09**:
> son de otra US, de otra épica y de otro entregable, y **esta planeación no los toca ni los lee como
> fuente**. Los archivos de esta US son `docs/us-planning/us-009-exportacion.md` y
> `docs/us-handoff/us-009-exportacion.md`. Cualquier agente que reciba «US-009» debe desambiguar por
> el sufijo `-exportacion`: sin sufijo es la guía de estilos.

**Estado**: planning
**Epic**: E3 (analítica y explotación de datos)
**Actividad**: A4 (dom 16-ago-2026) — apartado 3, prototipos de alta fidelidad (50 %)
**Sprint**: S4
**Rama**: `us-009-exportacion`, creada desde la punta de `us-016`. Convención vigente del usuario desde el 10-ago-2026: **una rama por US, commits locales encadenados, sin PR**. El estándar de la raíz (`feature/E3-US-009-export-jobs`) queda declarado como discrepancia **RU-11**: se declara, no se corrige
**SHA base**: `f807a18`. Ancla del diff de cierre: `git diff --name-only f807a18`
**Estimación**: 1 SP · **Día**: jue 13-ago-2026 · **Estado esperado al cierre**: demostrada en prototipo
**Fuente normativa**: §26.2 del plan (`context/planeacion_proyecto.md`), bloque «US-009 — Exportación en segundo plano (alcance S4)»
**Fuera de alcance explícito (recorte #3)**: política de ciclo de vida del bucket y auditoría de duración

---

## Lectura previa ejecutada

| Paso | Resultado |
|---|---|
| `docs/us-handoff/us-009-exportacion.md` | **No existía** (verificado con `ls docs/us-handoff/`: hay `us-009.md`, que es de US-UX-09). Se crea con estado `planning` al cerrar esta planeación |
| `backend/AGENTS.md` | Leído. Impone: SoC router→service→model, `response_model=` siempre, `Security(...)` en todo endpoint de datos, **exportaciones pesadas en `BackgroundTasks` con `job_id` inmediato**, esquema solo por dbmate, cobertura ≥ 70 % y un gate propio: «prueba de no-bloqueo (< 500 ms en catálogo durante export 1 M filas)» |
| `frontend/AGENTS.md` · `db/AGENTS.md` | **No leídos por presupuesto de tiempo.** Las reglas que esta US necesita de ellos ya están en la raíz y en el enunciado: i18n real sin cadenas en componentes, tokens desde `design/sistema.py`, dbmate como única vía de esquema. Queda como pendiente P-1 al abrir implementación |
| `AGENTS.md` de la raíz | **No leído por instrucción explícita del encargo.** Sus reglas llegan por el prompt del orquestador |
| Memoria (`mem_search`) | **No disponible en este subagente**: el entorno expone Read, Bash, Glob, Grep y Write, sin herramientas `mem_*`. Sustituido por `grep` puntual sobre `backend/`, `frontend/` y `db/` |
| `docs/us-resolved/` | **No existe.** No hay US de exportación previa que heredar |
| Modelo de formato | `docs/us-planning/us-016.md` (`head -140`), para densidad y tono |
| Skills cargadas (`docs/orchestration/auto-invoke.md`) | `portal-export-jobs` · `portal-backend-api` · `portal-db-migrations` · `portal-db-models` · `portal-testing`. **No se abrieron sus `SKILL.md`** por presupuesto de tiempo; lo que cada una impone se cita de la regla equivalente ya escrita en `backend/AGENTS.md` y en la raíz, y se marca como pendiente P-2 de contraste |
| Context7 | **No se usa.** Las tres APIs implicadas —`fastapi.BackgroundTasks`, `hmac`/`hashlib` de la biblioteca estándar y `google.cloud.storage.Blob.generate_signed_url(version="v4")`— son API pública estable, y la de GCS **no se implementa contra un proyecto real en S4** (§2.3): la fachada la aísla detrás de un `Protocol` |

---

## Qué existe ya — verificado, no supuesto

| Artefacto | Estado real | Consecuencia para esta US |
|---|---|---|
| `db/migrations/` | Dos archivos: `20260811005732_enable_pgvector_extension.sql` y `20260811211250_create_app_user.sql`. **No existe `export_job`** | La migración `create_export_job` es de esta US y es **la única migración de las cinco US de la ola**. Nadie más toca `db/` (§8) |
| `db/schema.sql` | Versionado, volcado de dbmate, con `INSERT INTO schema_migrations` de dos versiones y comparación byte a byte en CI | El volcado se regenera con `make db-up`; el tercer `INSERT` es parte del diff y **no se edita a mano** |
| `app_user` | `id UUID PK DEFAULT gen_random_uuid()`, `role` con `CHECK IN ('operativo','analista','directivo','admin')`, baja lógica por `disabled`. Diego Hernández existe: `dhernandez`, rol `analista` | `export_job.requested_by` referencia `app_user(id)`. El scope del endpoint se decide contra ese rol real (§Ambigüedad 4) |
| `backend/app/core/scopes.py` | `Scope` (StrEnum de cuatro roles), `ErrorCode` (StrEnum de códigos estables, sin prosa: la copia bilingüe vive en el frontend), `REALM = "karisma"` | Esta US **no abre vocabulario nuevo de roles ni de errores traducibles**: añade códigos a `ErrorCode` si hacen falta y nada más |
| `backend/app/` | `main.py`, `core/{auth,config,database,scopes,security}.py`, `api/{auth,health}.py`, `models/user.py`, `services/{auth_service,user_service}.py`. **Sin routers de datos, sin chat, sin export** | `api/export.py` es el **primer endpoint de datos** del portal: es el primero que ejercita `Security(get_current_user, scopes=[...])` sobre algo que no es autenticación |
| `backend/app/main.py` | `create_app()` monta `health` y `auth` y registra un `exception_handler`. **No hay auditoría de cobertura de scopes**: `permissions.py`, `SCOPE_REGISTRY`, `PUBLIC_ROUTES` y `audit_scope_coverage` los planea US-016, que sigue en estado `planning` (verificado el 11-ago-2026: `ls backend/app/core/` devuelve `auth.py, config.py, database.py, scopes.py, security.py`) | **La red de seguridad no está puesta.** El `Security(...)` de los cuatro verbos se verifica inspeccionando `app.routes` (T-9), nunca con el arranque. Frontera con US-023: cada una añade **una sola línea** de `include_router` |
| `backend/app/core/config.py` | Pydantic Settings estricto (sin `DATABASE_URL`/`GEMINI_API_KEY`/`JWT_SECRET_KEY` no arranca) | Esta US añade **cuatro** ajustes con valor por defecto seguro (§4.2). Ninguno hace fallar el arranque de quien no exporta |
| `tests/backend/` | `conftest.py` con fixtures `minimal_env` y `client`; 10 archivos de prueba; **la suite corre SIN PostgreSQL** | Restricción de diseño, no preferencia: el repositorio de trabajos debe ser **inyectable** para que las pruebas de esta US no levanten una base (§2.4). Es la misma costura que US-015 aceptó |
| `frontend/app/pages/exploracion/exportar.vue` | **Ya existe** como pantalla de andamiaje (`EstadoPendiente`), con su clave `screen.exports.description` en los locales | Se **reescribe**, no se crea. La pantalla de andamiaje es exactamente lo que esta US sustituye |
| `frontend/app/utils/navegacion.ts` | `/exploracion/exportar` **ya está registrada**: módulo `2.3` (`nav.branch.exploreExports`), prototipo `prototype.name.export`, y la faceta transversal `nav.facets.items.exportHistory` | **Hallazgo que elimina el único solape real**: esta US **NO TOCA `navegacion.ts`**. La ruta y su faceta ya existen; añadir algo ahí sería duplicar. Frontera cerrada (§5.4) |
| `frontend/i18n/locales/{es,en}.json` | Ya tienen `screen.exports.description`, `screen.exports.capability.{request,progress,link,history}`, `nav.branch.exploreExports`, `nav.facets.items.exportHistory`. La raíz real es **`screen`, en singular**: `screens` no existe | Esta US escribe **solo** bajo `export.*` (subárbol nuevo), **reescribe** `screen.exports.description` y **retira las cuatro hojas** `screen.exports.capability.*`, que quedan huérfanas al desmontar `EstadoPendiente`. Nada más se reordena |
| `frontend/app/stores/` | Un solo store: `sistemaDiseno.ts` | El store de exportaciones es nuevo y no colisiona |
| `frontend/test/` | **16 spec** + `configuracion.ts` e `i18nDePrueba.ts`, que no son spec | Esta US añade **uno** (`exportaciones.spec.ts`) y **modifica uno**: `pantallas.spec.ts`, línea 41. Verificado, no pendiente: `RUTAS_CON_ANDAMIAJE = RUTAS_CONTRATO.filter(ruta => ruta !== RUTA_ACCESO)` incluye `/exploracion/exportar`, y tres pruebas parametrizadas (`titula`, `retitula`, `declara en prosa`) caen sobre esa lista. **P-3 queda cerrado** |
| `ml/` | Generadores sintéticos con semilla fija y utilidades Parquet. Sin capa semántica | El trabajo de exportación lee **Parquet ya generado** por `make data`; no inventa un pipeline. Esta US **no toca `ml/`** |

---

## Ambigüedades del enunciado, resueltas antes de planear

Cinco bifurcaciones que, sin cerrar, producen dos implementaciones distintas de la misma US.

### A-1. «Fachada de infraestructura»: ¿qué se construye el jueves si no hay proyecto GCP?

El criterio pide «enlace firmado con caducidad de 24 horas». En S4 no hay bucket, ni credenciales, ni
presupuesto para gastarlas en una demo. La tentación es simular el enlace con una ruta cualquiera, y
entonces el criterio de caducidad **no se prueba nunca**.

**Decisión.** Se define un `Protocol` `AlmacenDeExportaciones` con **dos** implementaciones reales:

- `AlmacenLocalFirmado` — escribe el archivo bajo `settings.export_local_dir` y emite una URL propia
  `/api/export/{job_id}/download?exp=<epoch>&sig=<hmac>` donde `sig = HMAC-SHA256(export_signing_key,
  f"{job_id}:{exp}")`, comparado con `hmac.compare_digest`. La caducidad **no es decorativa**: está
  dentro del material firmado y el endpoint la valida.
- `AlmacenGCS` — `Blob.generate_signed_url(version="v4", expiration=timedelta(hours=24))`. Se escribe
  con firmas completas y cuerpo mínimo; **no se ejecuta en S4** y su prueba es de construcción de
  argumentos, no de red.

**Por qué esto sí verifica las 24 h el jueves 13 sin GCP**: el criterio verificable no es «Google
caduca el enlace», es «un enlace cuyo `exp` ya pasó no entrega el archivo». Con `AlmacenLocalFirmado`
eso se prueba de forma determinista inyectando un reloj (`Reloj` Protocol, `ahora() -> datetime`):
firmar en `T`, pedir en `T + 23 h 59 min` → **200**; pedir en `T + 24 h 01 min` → **410 Gone** con
código `enlace_caducado`. Y firma manipulada → **403** `firma_invalida`. Esas tres aserciones son
exactamente el contrato que `AlmacenGCS` cumplirá el día que exista el bucket, porque `expiration`
es el mismo número.

### A-2. ¿Dónde se elige la implementación?

**Decisión.** En `backend/app/core/config.py`, ajuste `export_storage_backend: Literal["local","gcs"] = "local"`,
resuelto **una sola vez** por la factoría `crear_almacen(settings) -> AlmacenDeExportaciones` en
`backend/app/services/almacen/__init__.py`, e inyectado al servicio por dependencia de FastAPI. Ni el
router, ni el servicio, ni el frontend saben cuál está detrás — misma disciplina que el contrato SSE
impone al `ProveedorDeTokens` de US-023. El `if` del backend vive en un solo archivo y en una sola
línea; si aparece un segundo `if` sobre el backend de almacenamiento en cualquier otro sitio, la
revisión lo rechaza.

### A-3. «Estado consultable desde cualquier pantalla»: ¿cómo, y cada cuánto?

Un `useFetch` en la pantalla de exportación no cumple el criterio: en cuanto Diego navega a otra
pantalla, la vigilancia muere. Y SSE aquí sería sobreingeniería: US-023 ya paga el coste del
transporte de eventos y esta US vale 1 SP.

**Decisión.** **Store Pinia `exportaciones` con sondeo**, montado en el layout (no en la página), con
estas reglas y su número justificado:

- **Intervalo: 3 000 ms.** El trabajo objetivo (1 M filas a CSV con `sink_csv` de Polars sobre el
  silo sintético) tarda del orden de 8–15 s. A 3 s se obtienen entre 3 y 5 muestras del estado
  `en_proceso`: suficientes para que la barra se mueva y para que la captura del «momento 2» de A4
  no dependa de la suerte. A 1 s se triplicaría el tráfico sin añadir información perceptible
  (por debajo de ~2 s el ojo no distingue el refresco de una barra indeterminada); a 5 s un trabajo
  corto pasaría de `pendiente` a `completado` en una sola muestra y el estado intermedio sería
  invisible, que es justo lo que el criterio de A4 exige poder capturar.
- **Coste**: 20 sondeos/min por usuario activo con trabajos vivos. Con los 7 usuarios sembrados y en
  el peor caso, 140 req/min sobre un endpoint que hace un `SELECT` por clave primaria. Irrelevante
  para Cloud Run scale-to-zero y por debajo de cualquier umbral de facturación.
- **Se detiene** cuando no queda ningún trabajo en estado no terminal, cuando `document.hidden` es
  verdadero (`visibilitychange`), y a los **200 sondeos** (10 min) sobre el mismo trabajo, que pasa a
  `caducado_en_cliente` con aviso. Sin apagado, el sondeo es una fuga.
- **Un solo temporizador global** en el store, no uno por componente.

### A-4. Scope del endpoint: ¿`operativo` o `analista`?

La matriz de la raíz dice: catálogo = autenticados; consultas puntuales = `operativo`+;
**agregaciones y export = `analista`+**; resúmenes = `directivo`+; usuarios = solo `admin`.

**Decisión.** `POST /api/export`, `GET /api/export`, `GET /api/export/{job_id}` y
`GET /api/export/{job_id}/download` exigen `scopes=["analista"]`. Justificación material, no
burocrática: Diego Hernández es `analista` en `app_user`, y una extracción masiva es una salida de
datos del perímetro — es la operación con mayor riesgo de fuga de todo el portal, y por eso el nivel
está por encima del consumo puntual. Consecuencia verificada por prueba: `lmendez` (operativo) recibe
**403** `permisos_insuficientes` en los cuatro verbos, y `acastaneda` (directivo) y `movalle` (admin)
reciben 200 por la jerarquía ordinal ya fijada en US-016.

**Propiedad del trabajo.** Además del scope, un analista **no** puede descargar el trabajo de otro
analista. Se comprueba `job.requested_by == usuario.id` y, si no coincide, se responde **404**, no
403: un 403 confirmaría la existencia del `job_id` y convertiría el identificador en un oráculo de
enumeración. Excepción: `admin` ve el historial completo (es el rol de gobierno) pero **no** descarga
archivos ajenos — leer metadatos no es leer el dato.

### A-5. «Los tres momentos navegables y capturables por separado»: ¿maqueta o flujo real?

Lo fácil es un selector que pinta tres pantallas falsas. Eso es exactamente lo que el criterio
prohíbe («sin falsear el flujo real») y además destruye el valor de la evidencia en A4.

**Decisión: los tres momentos son estados reales, y lo único que se manipula es el tiempo.**

1. La pantalla renderiza **siempre** desde el estado real del store: `solicitud` (ningún trabajo
   vivo), `proceso` (hay un trabajo en `pendiente`/`en_proceso`), `enlace` (el trabajo más reciente
   está `completado`).
2. Para capturar, la ruta acepta `?momento=solicitud|proceso|enlace`, que **no fabrica datos**: fija
   qué trabajo del historial real queda expandido y desactiva el auto-avance de la vista. Si no hay
   ningún trabajo en ese estado, la pantalla lo dice; no inventa uno.
3. Para que el «momento 2» dure lo bastante como para capturarlo con calma, el ajuste
   `export_demo_delay_seconds` (por defecto `0`, en demo `8`) **retrasa** el trabajo real. Se estira
   la duración, no se falsifica el estado: el archivo que sale al final es el archivo de verdad.
4. La franja de honestidad de demo de la pantalla lo declara con clave i18n `export.demo.notice`.

---

## 1. Criterios de aceptación con métricas verificables

Comandos desde la raíz del repositorio, en Git Bash.

| # | Criterio | Métrica | Cómo se verifica |
|---|---|---|---|
| **CA-1** | `POST /api/export` devuelve `job_id` **de inmediato** | Estado `202`, cuerpo con `job_id` (UUID) y `estado="pendiente"`, **con la tarea todavía encolada**: se invoca la función del router con un `BackgroundTasks()` propio y se afirma que contiene exactamente una entrada hacia `ExportService.ejecutar`. **No se mide tiempo de pared con `TestClient`** | `pytest tests/backend/test_export_endpoint.py -q -k "no_ejecuta_en_el_handler"` |
| **CA-2** | El trabajo corre en `BackgroundTasks`, nunca en el request | El `job` pasa a `completado` **después** de devolver la respuesta; ninguna ruta llama al ejecutor de forma síncrona | T-2: se ejecuta `await service.ejecutar(job_id)` directamente sobre el servicio y se afirma el estado terminal. **`TestClient` no sirve para esto**: sus `BackgroundTasks` corren dentro de la llamada ASGI, antes de que la prueba pueda leer el cuerpo |
| **CA-3** | La interfaz nunca se bloquea | Con `asyncio.gather(service.ejecutar(job_id), sondear_health())` sobre `httpx.AsyncClient` + `ASGITransport`, el sondeo de `/health` responde **< 500 ms** mientras `ejecutar` sigue en vuelo (gate de `backend/AGENTS.md`) | `pytest tests/backend/test_export_endpoint.py -q -k "no_toma_el_bucle"` |
| **CA-4** | Estado consultable desde cualquier pantalla | El store se monta en el layout; el sondeo sobrevive a un cambio de ruta; intervalo **3 000 ms**; se detiene sin trabajos vivos | `pnpm -C frontend vitest run test/exportaciones.spec.ts -t "sondeo"` con temporizadores falsos |
| **CA-5** | Historial de exportaciones | `GET /api/export` devuelve los trabajos del usuario ordenados por `created_at DESC`; nunca los de otro usuario | `pytest tests/backend/test_export_endpoint.py -q -k "historial"` |
| **CA-6** | Enlace firmado con caducidad de **24 h** | `exp − created ≈ 86 400 s` (± 2 s); `T+23 h 59 m` → **200**; `T+24 h 01 m` → **410** `enlace_caducado`; firma alterada → **403** `firma_invalida` | `pytest tests/backend/test_export_almacen_firmado.py -q` (reloj inyectado, sin GCP) |
| **CA-7** | Fachada con dos implementaciones y **un solo** punto de elección | `crear_almacen` es la única función que ramifica por `export_storage_backend`; ambas implementaciones satisfacen el `Protocol` | `pytest tests/backend/test_export_almacen_firmado.py -q -k "protocolo or factoria"` y `grep -rn "export_storage_backend" backend/app --include=*.py \| wc -l` → **2** (definición + factoría) |
| **CA-8** | Scope `analista`+ en los cuatro verbos | 401 sin token (con `WWW-Authenticate: Bearer`); 403 para `operativo`; 200 para `analista`/`directivo`/`admin`; **404** al pedir el trabajo de otro usuario | `pytest tests/backend/test_export_estado_scopes.py -q` (parametrizado por los cuatro roles) |
| **CA-9** | Los tres momentos, capturables por separado | `/exploracion/exportar?momento=solicitud\|proceso\|enlace` renderiza la vista correspondiente **a partir de estado real**; con historial vacío, `?momento=enlace` muestra el vacío explícito, no un enlace falso | `pnpm -C frontend vitest run test/exportaciones.spec.ts -t "momento"` + 3 capturas para A4 |
| **CA-10** | Cero cadenas visibles en componentes | Ninguna letra literal fuera de `t('...')` en los archivos `.vue` de esta US; `export.*` existe en `es.json` **y** en `en.json` con el mismo conjunto de claves | `pnpm -C frontend vitest run test/exportaciones.spec.ts -t "literal"` (T-20) para los literales; la **paridad** la verifica la suite existente, `pnpm -C frontend vitest run test/idioma.spec.ts test/contratos.spec.ts`, no una prueba propia de esta US (§6) + `make lint` |
| **CA-11** | Migración reversible y esquema versionado | `make db-up` seguido de `make db-rollback` deja `db/schema.sql` idéntico al de `f807a18`; el `CHECK` de estados rechaza un valor fuera del conjunto | `pytest tests/backend/test_export_job_migracion.py -q` (lee el SQL, no la base) + `make db-up && make db-rollback && git diff --exit-code db/schema.sql` |
| **CA-12** | Gate del repositorio | `make check` limpio; cobertura backend **≥ 70 %** sobre el denominador **combinado `backend/app` + `ml`** (`backend/pyproject.toml:70`), frontend **≥ 50 %** | `make check && make test` |
| **CA-13** | Honestidad de demo | La franja `export.demo.notice` está presente siempre que `export_demo_delay_seconds > 0`; ninguna cifra de la pantalla es inventada | Prueba de montaje del componente + revisión visual de la captura |

> **Corrección fechada el 11-ago-2026 (auditoría cruzada, segunda pasada).** CA-10 se verificaba con
> `vitest -t "i18n"` sobre `exportaciones.spec.ts`, una prueba de paridad de claves que §6 decidió **no
> escribir** (T-19 retirada por duplicar `idioma.spec.ts:42` y `contratos.spec.ts:214`): el criterio
> apuntaba a un test inexistente. Se decide separar las dos mitades del criterio —los literales los
> cubre T-20 en el spec de esta US; la paridad la cubre la suite global ya existente—. Motivo: un
> criterio de aceptación cuyo comando no ejecuta nada no es verificable, y reintroducir la prueba
> propia sería exactamente la duplicación que §6 descartó.

---

## 2. Arquitectura y flujo de capas

```
NAVEGADOR                        NUXT (SSR + proxy)              FASTAPI                        ALMACEN
---------                        ------------------              -------                        -------
exportar.vue                     server/api/[...].ts             api/export.py                  AlmacenDeExportaciones
  |                                    |                            | Security(scopes=analista)      (Protocol)
  |-- solicitar() ------------------->  |-- POST /api/export ----->  |                              /        \
  |                                    |                            |-- ExportService.solicitar() -/          \
  |<-- 202 {job_id, estado} ---------- |<--------------------------  |     crea ExportJob(pendiente)            \
  |                                    |                            |     background.add_task(ejecutar)         \
  |                                    |                            |                                    AlmacenLocal   AlmacenGCS
  | store Pinia `exportaciones`        |                            |                                     (HMAC)        (v4 signed)
  |   temporizador global 3 000 ms     |                            |   [tarea de fondo]
  |-- sondear() --------------------->  |-- GET /api/export/{id} ->  |     estado=en_proceso
  |<-- {estado: en_proceso} ---------- |<--------------------------  |     Polars scan/sink -> archivo
  |                                    |                            |     almacen.guardar(...)
  |-- sondear() --------------------->  |-- GET /api/export/{id} ->  |     estado=completado, expires_at=+24h
  |<-- {estado: completado, url} ----- |<--------------------------  |
  |                                    |                            |
  |-- clic en el enlace -------------> |-- GET .../download?exp&sig->|  valida firma + exp + propiedad
  |<-- archivo o 410/403 ------------- |<--------------------------  |
```

**Recorrido petición → respuesta de `POST /api/export`**

1. El navegador llama al proxy Nitro, que reescribe `X-Forwarded-*` y adjunta el Bearer de la sesión.
2. `api/export.py` resuelve `Security(get_current_user, scopes=[Scope.ANALISTA])`. Sin token → 401
   con `WWW-Authenticate`; con `operativo` → 403 `permisos_insuficientes`. **El router no valida
   negocio**: solo tipa el cuerpo con `SolicitudExportacion` (Pydantic v2, `field_validator` sobre
   `dataset` contra el catálogo conocido y sobre `formato`).
3. `ExportService.solicitar()` crea el `ExportJob` en estado `pendiente`, registra
   `structlog` `export.job.solicitado` con `job_id`, `dataset`, `formato`, `usuario_id` — **nunca**
   filtros crudos que puedan contener datos personales, ni el `export_signing_key`.
4. El router encola `background.add_task(service.ejecutar, job_id)` y **devuelve 202 ya**.
5. La tarea de fondo: `en_proceso` → lee Parquet con Polars (`scan_parquet` + `sink_csv`, sin
   materializar en memoria) → `almacen.guardar(job_id, ruta)` → `completado` con `object_key`,
   `row_count`, `byte_size` y `expires_at = ahora + 24 h`. Cualquier excepción → `fallido` con
   `error_code`, y **el log lleva la clase de la excepción, no su mensaje** (puede traer rutas).
6. El store sondea `GET /api/export/{job_id}` cada 3 s hasta estado terminal.
7. El enlace se pide a `almacen.url_firmada(job)`; el local lo sirve `GET .../download` validando
   HMAC, `exp` y propiedad.

**Dónde vive cada regla**: la jerarquía de roles en `core/scopes.py` (US-016, no se toca); la
elección de almacén en `services/almacen/__init__.py`; el cálculo de las 24 h en un único sitio,
`settings.export_link_ttl_hours`, consumido por las dos implementaciones.

---

## 3. Archivos exactos a crear o modificar

| Ruta | Acción | Qué cambia | Quién |
|---|---|---|---|
| `db/migrations/20260813090000_create_export_job.sql` | crear | Tabla `export_job` con `CHECK` de estados y 3 índices (§8) | db |
| `db/schema.sql` | modificar | Regenerado por `make db-up`; **no se edita a mano** | db |
| `backend/app/models/export.py` | crear | `ExportJob` (SQLModel, table) + contratos Pydantic: `SolicitudExportacion`, `TrabajoResumen`, `TrabajoDetalle`, enums `EstadoTrabajo`/`FormatoExportacion` | backend |
| `backend/app/services/export_service.py` | crear | `ExportService`: `solicitar`, `ejecutar`, `consultar`, `historial`, `resolver_descarga` | backend |
| `backend/app/services/almacen/__init__.py` | crear | `AlmacenDeExportaciones` (Protocol), `Reloj` (Protocol), `crear_almacen(settings)` — **único punto de elección** | backend |
| `backend/app/services/almacen/local.py` | crear | `AlmacenLocalFirmado`: HMAC-SHA256 con `exp` dentro del material firmado | backend |
| `backend/app/services/almacen/gcs.py` | crear | `AlmacenGCS`: `generate_signed_url(version="v4")`. Escrito, **no ejecutado** en S4 | backend |
| `backend/app/api/export.py` | crear | Router con los 4 endpoints, todos con `Security(..., scopes=[Scope.ANALISTA])` | backend |
| `backend/app/main.py` | modificar | **Una sola línea**: `app.include_router(export.router)` (+ su import). Frontera con US-023 | backend |
| `backend/app/core/config.py` | modificar | 4 ajustes nuevos con valor por defecto seguro (§4.2) | backend |
| `backend/.env.example` | modificar | Los 4 ajustes documentados, sin valores reales | backend |
| `backend/pyproject.toml` | modificar **solo si** falta `polars` | `poetry add polars`; `google-cloud-storage` va como extra opcional y **no** se instala en S4 | backend |
| `frontend/app/pages/exploracion/exportar.vue` | **modificar** (ya existe) | Sustituye el andamiaje `EstadoPendiente` por los tres momentos reales | frontend |
| `frontend/app/stores/exportaciones.ts` | crear | Store Pinia con sondeo global de 3 000 ms | frontend |
| `frontend/app/composables/useExportaciones.ts` | crear | Fachada del store para los componentes (sin lógica de negocio en `.vue`) | frontend |
| `frontend/app/components/exportacion/FormularioExportacion.vue` | crear | Momento 1 | frontend |
| `frontend/app/components/exportacion/TarjetaTrabajo.vue` | crear | Momentos 2 y 3 (una tarjeta por trabajo, por `job_id`) | frontend |
| `frontend/app/components/exportacion/HistorialExportaciones.vue` | crear | Lista con enlace firmado y caducidad relativa | frontend |
| `frontend/app/types/exportacion.ts` | crear | Tipos espejo del contrato del backend | frontend |
| `frontend/i18n/locales/es.json` | modificar | **Solo** subárbol `export.*` (hojas enumeradas en §3.1) + reescritura de `screen.exports.description` + **borrado de `screen.exports.capability.*`** (cuatro hojas) | frontend |
| `frontend/i18n/locales/en.json` | modificar | Idem, mismas claves | frontend |
| `tests/backend/test_export_endpoint.py` | crear | CA-1, CA-2, CA-3, CA-5 | tests |
| `tests/backend/test_export_almacen_firmado.py` | crear | CA-6, CA-7 | tests |
| `tests/backend/test_export_estado_scopes.py` | crear | CA-8 | tests |
| `tests/backend/test_export_job_migracion.py` | crear | CA-11 | tests |
| `frontend/test/exportaciones.spec.ts` | crear | CA-4, CA-9, CA-10 | tests |
| `frontend/test/pantallas.spec.ts` | modificar | **Una línea, la 41.** `RUTAS_CON_ANDAMIAJE` se estrecha excluyendo la ruta que esta US deja de ser andamiaje: `RUTAS_CONTRATO.filter(ruta => ![RUTA_ACCESO, '/exploracion/exportar'].includes(ruta))`. Afecta a los tres bloques parametrizados que consumen esa lista. **No se borra ninguna prueba**: el propio archivo documenta el mecanismo («The list shrinks by one screen per User Story»); borrar el caso retiraría la cobertura de las pantallas que siguen siendo andamiaje. **Colisión declarada**: US-023 hace el mismo cambio para `RUTA_ASISTENTE` el vie 14. Quien llegue segundo **añade su ruta al arreglo existente**, nunca reescribe el filtro | tests (compartido secuencial: US-009 jue 13, US-023 vie 14) |
| `backend/app/core/permissions.py` | **condicional** | **Solo si US-016 ya encadenó el archivo.** Si existe: `POST /api/export` y `GET /api/export/{job_id}` pasan de `estado="planificado"` a `"vigente"`, y se **añaden** `RouteKey("GET", "/api/export")` y `RouteKey("GET", "/api/export/{job_id}/download")` con `PermissionRule(scopes=(Scope.ANALISTA,), us="US-009", estado="vigente")` — la matriz de US-016 §4.3 reserva **dos** filas y esta US monta **cuatro** rutas. Si no existe, **no se crea**: es write-set exclusivo de US-016 y el pendiente se declara en el handoff | US-016 (dueña); US-009 solo añade filas |
| `docs/security.md` | **condicional** | Solo si la fila anterior se escribió: **únicamente** el bloque entre `<!-- matriz-permisos:inicio -->` y `<!-- matriz-permisos:fin -->`, regenerado con `(cd backend && poetry run python -c "from app.core.permissions import render_permission_matrix; print(render_permission_matrix())")`. Nunca a mano | US-016 (dueña) |
| `docs/us-planning/us-009-exportacion.md` | crear | Este documento | docs |
| `docs/us-handoff/us-009-exportacion.md` | crear | Handoff, estado `planning` | docs |

**No se tocan** (declaración explícita): `frontend/app/utils/navegacion.ts` (la ruta ya existe),
`ml/`, `infra/`, `Makefile`, `docs/us-planning/us-009.md`, `docs/us-handoff/us-009.md`,
`backend/app/core/scopes.py`, `db/migrations/*` ya aplicadas. **`backend/app/core/permissions.py` no
está en esta lista**: no se toca *porque hoy no existe*, y si US-016 lo entrega antes del jueves se
edita bajo la regla condicional de la tabla. Son dos cosas distintas y confundirlas fue el defecto.

> **Corrección fechada el 11-ago-2026 (auditoría cruzada).** El plan daba por implementada la
> auditoría de cobertura de scopes de US-016 y apoyaba en ella T-9 y dos ítems del checklist;
> `backend/app/core/permissions.py`, `SCOPE_REGISTRY`, `PUBLIC_ROUTES` y `docs/security.md` **no
> existen en `f807a18`** y el handoff de US-016 sigue en `planning`. Se decide: (a) T-9 afirma sobre
> `app.routes`, que sí existe, en lugar de sobre un arranque que no puede fallar; (b) la escritura del
> registro queda **condicional** y con las **cuatro** filas que esta US necesita, porque US-016 §4.3
> solo reserva dos (`POST /api/export` y `GET /api/export/{job_id}`) y esta US monta cuatro rutas;
> (c) `docs/security.md` se regenera en el mismo commit, nunca a mano. Motivo: una prueba cuya
> aserción no puede fallar es deuda prohibida por la regla NON-NEGOTIABLE, y montar cuatro rutas con
> dos filas registradas haría abortar `create_app()` el día que US-016 aterrice.

### 3.1 Claves i18n exactas — subárbol `export.*`

Se enumeran para que la disyunción con `chat.*` (US-023/024/028) sea verificable **antes** de escribir,
que es para lo que existe el protocolo de archivo compartido. Mismas hojas en `es.json` y `en.json`:

```
export.form.{dataset,format,filters,submit}
export.job.state.{pendiente,en_proceso,completado,fallido}
export.job.{rows,size,requestedAt,expiresAt}
export.link.{download,expiresIn,expired}
export.history.{title,empty}
export.moment.{request,progress,link}
export.demo.notice
export.error.{signature,expired,notFound}
```

**Fuera del subárbol, y son las dos únicas excepciones**: reescritura de `screen.exports.description`
y **borrado** de `screen.exports.capability.{request,progress,link,history}`.

---

## 4. Firmas públicas de cada módulo nuevo

Solo firmas. Nada de implementación.

### 4.1 `backend/app/models/export.py`

```python
class EstadoTrabajo(StrEnum):
    """Lifecycle state of an export job. Mirrors the CHECK constraint in SQL."""


class FormatoExportacion(StrEnum):
    """Output format requested by the analyst: csv or xlsx."""


class ExportJob(SQLModel, table=True):
    """Persisted export job. One row per request; never deleted, only expired."""


class SolicitudExportacion(BaseModel):
    """Request body of POST /api/export."""

    @field_validator("dataset")
    @classmethod
    def dataset_must_be_known(cls, value: str) -> str:
        """Reject datasets outside the published catalog with a fuzzy hint."""


class TrabajoResumen(BaseModel):
    """Job as listed in the history: no signed URL, no internal object key."""


class TrabajoDetalle(BaseModel):
    """Job as polled: adds signed URL and expiry when the state is completed."""
```

### 4.2 `backend/app/core/config.py` (ajustes añadidos)

```python
export_storage_backend: Literal["local", "gcs"] = "local"
"""Which AlmacenDeExportaciones implementation crear_almacen returns."""

export_signing_key: SecretStr = SecretStr("")
"""HMAC key of the local signed-link facade. Empty means: derive from JWT_SECRET_KEY."""

export_link_ttl_hours: int = 24
"""Single source of the 24 hour expiry, shared by both storage implementations."""

export_demo_delay_seconds: float = 0.0
"""Artificial delay that makes the in-progress moment capturable for A4."""
```

### 4.3 `backend/app/services/almacen/__init__.py`

```python
class Reloj(Protocol):
    def ahora(self) -> datetime:
        """Current UTC instant. Injected so expiry can be tested without waiting."""


class AlmacenDeExportaciones(Protocol):
    async def guardar(self, job_id: UUID, origen: Path, formato: str) -> str:
        """Persist the produced file and return its opaque object key."""

    def url_firmada(self, object_key: str, emitido: datetime) -> tuple[str, datetime]:
        """Return a time-limited download URL and the instant it stops working."""


def crear_almacen(
    settings: Settings, reloj: Reloj | None = None
) -> AlmacenDeExportaciones:
    """Single place where export_storage_backend decides the implementation."""
```

### 4.4 `backend/app/services/almacen/local.py`

```python
class AlmacenLocalFirmado:
    """Filesystem storage with HMAC-SHA256 links; the facade used during S4."""

    def firmar(self, object_key: str, expira_en: datetime) -> str:
        """Return the hex HMAC over 'object_key:epoch', the material that expires."""

    def verificar(self, object_key: str, expira_en: int, firma: str) -> None:
        """Raise EnlaceCaducado or FirmaInvalida; constant-time comparison."""
```

### 4.5 `backend/app/services/export_service.py`

```python
class ExportService:
    """Business logic of export jobs. The router holds none of it."""

    async def solicitar(
        self, solicitud: SolicitudExportacion, usuario: UserOut
    ) -> TrabajoDetalle:
        """Create the job in state pendiente and return it without doing the work."""

    async def ejecutar(self, job_id: UUID) -> None:
        """Background entry point: produce the file and move the job to a terminal state."""

    async def consultar(self, job_id: UUID, usuario: UserOut) -> TrabajoDetalle:
        """Return one job, or raise 404 when it belongs to somebody else."""

    async def historial(
        self, usuario: UserOut, limite: int = 50
    ) -> list[TrabajoResumen]:
        """List the caller's jobs, newest first."""

    async def resolver_descarga(
        self, job_id: UUID, expira_en: int, firma: str, usuario: UserOut
    ) -> Path:
        """Validate signature, expiry and ownership before handing over the file."""
```

`UserOut` se importa de `app.models.user`: es exactamente lo que devuelve `get_current_user` (`backend/app/core/auth.py`). **No se declara ningún tipo de usuario nuevo en esta US**; el símbolo `Usuario` no existe en `backend/` y escribirlo abriría un segundo modelo de usuario.

> **Corrección fechada el 11-ago-2026 (auditoría cruzada).** Las cuatro firmas de `ExportService` tipaban `usuario: Usuario`, un símbolo que no existe en el repositorio (`grep -rn "Usuario" backend/ --include=*.py` → 0). Se sustituye por `UserOut` en las cuatro, porque es el tipo real que devuelve la dependencia de seguridad y el que US-023 ya usa en su router; con el nombre anterior el módulo no pasaría mypy o el agente abriría un modelo paralelo.

### 4.6 `backend/app/api/export.py`

```python
router = APIRouter(prefix="/api/export", tags=["export"])

@router.post("", status_code=202, response_model=TrabajoDetalle)
async def solicitar_exportacion(...) -> TrabajoDetalle:
    """Accept the request, queue the work and answer immediately with a job id."""

@router.get("", response_model=list[TrabajoResumen])
async def listar_exportaciones(...) -> list[TrabajoResumen]:
    """Export history of the authenticated analyst."""

@router.get("/{job_id}", response_model=TrabajoDetalle)
async def consultar_exportacion(...) -> TrabajoDetalle:
    """Polling endpoint used by the Pinia store every three seconds."""

@router.get("/{job_id}/download")
async def descargar_exportacion(...) -> FileResponse:
    """Serve the file behind the locally signed link; 410 once it expired."""
```

### 4.7 `frontend/app/stores/exportaciones.ts`

```ts
export const useExportacionesStore = defineStore('exportaciones', () => { /* ... */ })
// solicitar(payload): Promise<string>            crea el trabajo y devuelve su job_id
// iniciarSondeo(): void                          arranca el unico temporizador de 3 000 ms
// detenerSondeo(): void                          lo apaga sin trabajos vivos o con pestana oculta
// trabajos: ComputedRef<TrabajoResumen[]>        historial ordenado
// momento: ComputedRef<'solicitud'|'proceso'|'enlace'>   derivado del estado real
```

---

## 5. Dominios, sub-tareas y write-sets

### 5.1 Checklist de dominios

- [x] backend
- [x] frontend
- [ ] ml
- [ ] agent
- [ ] infra
- [x] db
- [x] docs

### 5.2 ¿Se reparte?

**Sí, en tres olas estrictamente secuenciales, con un único agente por ola.** La US vale 1 SP y el
reparto en paralelo no compensa: el frontend **lee** el contrato que el backend **escribe**, y la
regla del proyecto es que quien escribe va primero. Repartir en paralelo obligaría a congelar el
contrato en un cuarto documento y a reconciliar después; secuencial gasta menos.

| Ola | Agente | Subagente | Write-set exclusivo | Día |
|---|---|---|---|---|
| **O1** | esquema | `portal-db-migrations` + `portal-db-models` | `db/migrations/20260813090000_create_export_job.sql`, `db/schema.sql`, `backend/app/models/export.py`, `tests/backend/test_export_job_migracion.py` | jue 13, mañana |
| **O2** | backend | `portal-export-jobs` + `portal-backend-api` | `backend/app/services/almacen/*`, `backend/app/services/export_service.py`, `backend/app/api/export.py`, `backend/app/main.py` (1 línea), `backend/app/core/config.py`, `backend/.env.example`, `tests/backend/test_export_{endpoint,almacen_firmado,estado_scopes}.py` | jue 13, mediodía |
| **O3** | frontend | `portal-frontend-nuxt` + `portal-testing` | `frontend/app/pages/exploracion/exportar.vue`, `frontend/app/stores/exportaciones.ts`, `frontend/app/composables/useExportaciones.ts`, `frontend/app/components/exportacion/*`, `frontend/app/types/exportacion.ts`, `frontend/i18n/locales/{es,en}.json` (solo `export.*` y las dos hojas de `screen.exports`), `frontend/test/exportaciones.spec.ts`, `frontend/test/pantallas.spec.ts` (línea 41) | jue 13, tarde |

O3 **lee sin escribir**: `backend/app/models/export.py` y `backend/app/api/export.py`. Por eso va
después. Los write-sets de las tres olas son disjuntos.

### 5.3 Frontera con las otras US de la ola

| Archivo | Quién más lo toca | Regla |
|---|---|---|
| `backend/app/main.py` | US-023 (línea de montaje de `chat.router`) | Una línea de `include_router` cada una, en bloques separados. Si US-023 ya commiteó, US-009 añade la suya debajo sin reordenar |
| `frontend/i18n/locales/{es,en}.json` | US-023, US-024, US-028 (`chat.*`), US-UX-07 (nada: sus etiquetas ya existen bajo `prototype.scope.*`) | US-009 escribe **solo** bajo `export.*`, reescribe `screen.exports.description` y **retira** `screen.exports.capability.*`. Prohibido reordenar el resto del archivo |
| `frontend/test/` | todas | Archivos nuevos, uno por US. US-009 aporta `exportaciones.spec.ts` **y edita una línea de `pantallas.spec.ts`**. **No se borra ninguna prueba**: se retira la ruta de `RUTAS_CON_ANDAMIAJE` (línea 41), que es el mecanismo que el propio archivo documenta («The list shrinks by one screen per User Story»). Borrar el caso retiraría la cobertura de las pantallas que siguen siendo andamiaje. US-023 hace el mismo cambio para `/asistente` el vie 14 y **añade su ruta al arreglo**, sin reescribir el filtro |
| `frontend/app/utils/navegacion.ts` | quien añada ruta nueva | **US-009 NO lo toca**: `/exploracion/exportar`, su prototipo y su faceta transversal ya están registrados |

---

## 6. Plan de tests

Cada fila declara el defecto concreto que la haría fallar. Sin defecto identificable, la prueba no se
escribe.

| # | Prueba | Archivo | Qué defecto concreto la haría fallar | Umbral |
|---|---|---|---|---|
| **T-1** | `test_solicitud_no_ejecuta_el_trabajo_en_el_handler` | `tests/backend/test_export_endpoint.py` | Que alguien ejecute el trabajo dentro del handler (el patrón obvio: `await service.ejecutar(...)` antes del `return`). Se invoca la **función del router** con un `BackgroundTasks()` propio: respuesta 202 con `estado="pendiente"` y `tareas.tasks` con exactamente una entrada hacia `ExportService.ejecutar` | 202, 1 tarea encolada |
| **T-2** | `test_tarea_de_fondo_completa_el_trabajo` | idem | Que se encole la tarea equivocada, o que `ejecutar` no persista el estado terminal y el trabajo quede colgado en `pendiente` para siempre | estado final `completado` |
| **T-3** | `test_el_trabajo_no_toma_el_bucle_de_eventos` | idem | Que la tarea de fondo tome el bucle de eventos con E/S síncrona (leer todo el Parquet en memoria con `read_parquet` en vez de `scan_parquet`), dejando `/health` colgado. Se monta con `httpx.AsyncClient` + `ASGITransport` y `asyncio.gather`; **`TestClient` no puede expresar este caso** porque no devuelve control hasta que la tarea acabó | `/health` < 500 ms con `ejecutar` en vuelo |
| **T-4** | `test_historial_no_filtra_trabajos_ajenos` | idem | Que el `SELECT` del historial olvide el `WHERE requested_by = :usuario` — la fuga más probable y más cara de esta US | 0 trabajos ajenos |
| **T-5** | `test_enlace_valido_antes_de_24h` | `tests/backend/test_export_almacen_firmado.py` | Que el `exp` firmado se calcule en segundos donde toca milisegundos, o en hora local en vez de UTC: el enlace caducaría antes de nacer | 200 en `T+23 h 59 m` |
| **T-6** | `test_enlace_caduca_a_las_24h` | idem | Que `exp` se incluya en la URL pero **no** en el material firmado ni se valide: el clásico enlace «con caducidad» que nunca caduca. Se manipula el reloj, no se espera | 410 `enlace_caducado` en `T+24 h 01 m` |
| **T-7** | `test_firma_alterada_es_rechazada` | idem | Que la comparación use `==` en vez de `hmac.compare_digest`, o que se valide solo la longitud | 403 `firma_invalida` |
| **T-8** | `test_factoria_elige_una_sola_vez` | idem | Que aparezca un segundo `if backend == "gcs"` fuera de `crear_almacen`, que es como esta clase de fachada se pudre. Se afirma que ambas implementaciones satisfacen el `Protocol` y que la factoría devuelve la clase correcta para cada valor | 2 apariciones de `export_storage_backend` en `backend/app` |
| **T-9** | `test_router_declara_security` | `tests/backend/test_export_estado_scopes.py` | Que `api/export.py` olvide `Security(...)` en un verbo. Se afirma **directamente sobre `app.routes`**: para cada una de las 4 rutas de `/api/export`, `route.dependant.security_requirements` no está vacío y sus scopes contienen `analista`. **No se apoya en `ScopeCoverageError`: ese mecanismo no existe en `f807a18`** | 4 rutas, 4 dependencias con scope |
| **T-10** | `test_matriz_de_roles` (parametrizada ×4 roles ×4 verbos) | idem | Que se ponga `scopes=["operativo"]` por copiar-pegar del router de catálogo, abriendo la salida masiva de datos al rol más bajo | `operativo`→403, resto→200 |
| **T-11** | `test_sin_token_es_401_con_cabecera` | idem | Que el 401 salga sin `WWW-Authenticate: Bearer` y el frontend no sepa relanzar el acceso | 401 + cabecera |
| **T-12** | `test_trabajo_ajeno_devuelve_404` | idem | Que se responda 403 en vez de 404 y el `job_id` se convierta en oráculo de enumeración | 404, cuerpo sin metadatos |
| **T-13** | `test_migracion_es_reversible` | `tests/backend/test_export_job_migracion.py` | Que el bloque `-- migrate:down` falte o no deshaga los índices/tabla; el `rollback` dejaría basura y `schema.sql` divergiría. Lee el SQL como texto (la suite corre sin PostgreSQL) | ambos marcadores presentes, `DROP` de tabla e índices |
| **T-14** | `test_estados_tienen_check` | idem | Que los estados se validen solo en Python y una escritura directa meta `EstadoTrabajo` inventado: el `CHECK` es la última línea de defensa | `CHECK` con los 4 estados |
| **T-15** | `test_schema_incluye_export_job` | idem | Que se aplique la migración y **no** se regenere `db/schema.sql`, rompiendo la comparación byte a byte de CI | tabla e `INSERT` de versión presentes |
| **T-16** | `sondeo se detiene sin trabajos vivos` | `frontend/test/exportaciones.spec.ts` | Que el `setInterval` no se limpie: fuga de temporizador que sigue pegándole al backend para siempre tras terminar el último trabajo | 0 llamadas tras el estado terminal |
| **T-17** | `intervalo del sondeo es 3 000 ms` | idem | Que alguien lo baje a 500 ms «para que se vea mejor» y triplique el tráfico. Con temporizadores falsos: 3 avances de 3 s → exactamente 3 llamadas | 3 000 ms exactos |
| **T-18** | `los tres momentos derivan del estado real` | idem | Que `?momento=enlace` fabrique un enlace inexistente cuando el historial está vacío — falsear el flujo, que es justo lo prohibido | vacío explícito, sin URL |
| **T-20** | `ningun literal visible en los componentes` | idem | Que una etiqueta se escriba directa en el `.vue`, violando la regla dura de i18n | 0 literales fuera de `t()` |

**Umbral global backend**: el gate es `--cov=backend/app --cov=ml --cov-fail-under=70` (`backend/pyproject.toml:70`): una **cifra combinada** sobre `backend/app` **y** `ml`, no sobre `backend/app` a solas. Todo módulo nuevo sin pruebas resta del mismo denominador que los generadores sintéticos. Frontend: `lines: 50` en `frontend/vitest.config.ts`.

`backend/app/services/almacen/gcs.py` entra en ese denominador aunque no se ejecute. Se cubre su construcción de argumentos con un doble de `Blob` en T-8 (`expiration == timedelta(hours=24)`, `version == "v4"`), que es lo único suyo verificable sin red; si aun así el gate combinado baja del 70 %, se marca con `# pragma: no cover` **fila a fila y con justificación**, nunca el archivo entero.

**Pruebas que NO se escriben, y por qué**: **paridad de claves `es`/`en`** — `frontend/test/idioma.spec.ts:42` ya compara el conjunto de claves completo de los dos catálogos y `contratos.spec.ts:214` ya exige que toda clave escrita como literal resuelva en ambos idiomas; una prueba por subárbol duplica esa señal sin poder fallar antes que ella (por eso T-19 se retiró). Nada sobre `AlmacenGCS` contra la red (no hay proyecto y
una prueba contra un doble de `google.cloud.storage` mide el doble, no el código); nada sobre el
aspecto de la pantalla más allá de los tres momentos (A4 la puede reescribir); nada sobre la política
de ciclo de vida del bucket (recorte #3, fuera de alcance).

---

## 7. Nube

**No toca la nube en S4.** Esa es precisamente la decisión de la fachada (§A-1): el `Protocol`
permite entregar el criterio de las 24 h con `AlmacenLocalFirmado`, verificado de forma determinista
con reloj inyectado, sin crear bucket, sin credenciales y sin gastar del presupuesto de < 45 USD/mes.
`AlmacenGCS` queda escrito con firmas completas para que el día del despliegue el cambio sea una
variable de entorno (`EXPORT_STORAGE_BACKEND=gcs`) y un `poetry install --extras gcs`, no una
refactorización. El comando que se ejecutará **cuando exista el proyecto**, y no antes:
`terraform -chdir=infra apply -target=google_storage_bucket.exports` — fuera del alcance de esta US.

---

## 8. Schema — migración dbmate

Archivo: `db/migrations/20260813090000_create_export_job.sql` (`make db-new SLUG=create_export_job`
genera la marca de tiempo real; la de arriba es la prevista para el jueves 13).

```sql
-- Tercera migracion del proyecto: los trabajos de exportacion en segundo plano.
--
-- La tabla no borra nunca una fila: un trabajo caducado sigue siendo historial y
-- su enlace deja de funcionar por la firma, no por el DELETE. La politica de
-- ciclo de vida del bucket queda fuera de alcance (recorte #3 de S4).
--
-- Los estados van con CHECK y no con un ENUM de PostgreSQL a proposito: anadir un
-- valor a un ENUM es una migracion con bloqueo, y este vocabulario todavia se
-- mueve. El CHECK es la ultima linea de defensa contra una escritura directa que
-- no pase por EstadoTrabajo.

-- migrate:up
CREATE TABLE export_job (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    requested_by  UUID NOT NULL REFERENCES app_user(id) ON DELETE RESTRICT,
    dataset       TEXT NOT NULL,
    export_format TEXT NOT NULL
                  CHECK (export_format IN ('csv', 'xlsx')),
    filters       JSONB NOT NULL DEFAULT '{}'::jsonb,
    status        TEXT NOT NULL DEFAULT 'pendiente'
                  CHECK (status IN ('pendiente', 'en_proceso', 'completado', 'fallido')),
    row_count     BIGINT,
    byte_size     BIGINT,
    object_key    TEXT,
    error_code    TEXT,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    started_at    TIMESTAMPTZ,
    finished_at   TIMESTAMPTZ,
    expires_at    TIMESTAMPTZ,

    CONSTRAINT export_job_completado_coherente
        CHECK (status <> 'completado'
               OR (object_key IS NOT NULL AND expires_at IS NOT NULL AND finished_at IS NOT NULL)),
    CONSTRAINT export_job_fallido_coherente
        CHECK (status <> 'fallido' OR error_code IS NOT NULL)
);

COMMENT ON TABLE  export_job            IS 'Trabajos de exportacion en segundo plano. Nunca se borran: caducan.';
COMMENT ON COLUMN export_job.object_key IS 'Clave opaca en el almacen. Jamas se serializa en una respuesta.';
COMMENT ON COLUMN export_job.expires_at IS 'Instante en que el enlace firmado deja de servir. created_at + 24 h.';
COMMENT ON COLUMN export_job.filters    IS 'Consulta estructurada validada por Pydantic. Nunca SQL ni Polars libre.';

CREATE INDEX export_job_requested_by_created_at_idx
    ON export_job (requested_by, created_at DESC);

CREATE INDEX export_job_status_vivos_idx
    ON export_job (status)
    WHERE status IN ('pendiente', 'en_proceso');

CREATE INDEX export_job_expires_at_idx
    ON export_job (expires_at)
    WHERE status = 'completado';

-- migrate:down
DROP INDEX IF EXISTS export_job_expires_at_idx;
DROP INDEX IF EXISTS export_job_status_vivos_idx;
DROP INDEX IF EXISTS export_job_requested_by_created_at_idx;
DROP TABLE IF EXISTS export_job;
```

**Justificación de cada índice, uno a uno** (sin justificación, no entra: un índice de más es coste de
escritura permanente):

1. `(requested_by, created_at DESC)` — sirve la **única** consulta caliente de la US: el historial de
   Diego, filtrado por dueño y ordenado por fecha descendente. Compuesto y en ese orden porque la
   igualdad va primero y la ordenación después: así el índice resuelve filtro **y** orden sin `SORT`.
2. `(status) WHERE status IN ('pendiente','en_proceso')` — **parcial** a propósito. La consulta de
   trabajos vivos (recuperación tras reinicio de Cloud Run, y el barrido que decide si el store debe
   seguir sondeando) toca una fracción minúscula de la tabla; un índice total sobre una columna de
   cuatro valores sería inútil por baja cardinalidad. El parcial pesa lo que pesan los vivos.
3. `(expires_at) WHERE status = 'completado'` — soporta la futura purga por caducidad y la consulta
   «qué enlaces siguen vivos». Es el único índice que se justifica por trabajo futuro; se acepta
   porque es parcial y barato, y porque `expires_at` es `NULL` en todo lo no completado.

**Índices que NO se crean**: ninguno sobre `dataset` (no hay consulta que filtre por él en S4) y
ninguno sobre `filters` (GIN sobre JSONB sin una sola consulta que lo use es coste puro).

`db/schema.sql` se regenera con `make db-up` y el diff debe incluir la tabla, los tres índices, los
dos `CONSTRAINT` y el tercer `INSERT INTO public.schema_migrations`.

---

## 9. Aporte al entregable A4

| Rubro de A4 | Aporte | Peso |
|---|---|---|
| Apartado 3 — prototipos de alta fidelidad | Tres capturas de una **misma pantalla en tres momentos reales** del flujo asíncrono: solicitud, trabajo en curso con estado vivo, y enlace firmado con su caducidad. Es la evidencia que un archivo estático de diseño representa mal, porque su contenido es el tiempo | **50 %** del entregable; esta US aporta 3 de las láminas del apartado |
| Apartado de coherencia con el sistema de diseño | Los componentes consumen exclusivamente los tokens de `design/sistema.py` vía `frontend/app/utils/tokens.generated.ts` (US-UX-09). `uxdoc.sty` es del **informe** y está congelado: no se deriva nada de él | indirecto |
| Honestidad de demo | Franja `export.demo.notice` visible en las capturas: el retraso es artificial, el flujo no | requisito transversal |

---

## 10. Riesgos y mitigaciones

| # | Riesgo | Prob. | Impacto | Mitigación | Disparador de la válvula |
|---|---|---|---|---|---|
| R-1 | `BackgroundTasks` de FastAPI muere con el proceso: en Cloud Run scale-to-zero, un trabajo largo se pierde al escalar a cero | Media | Alto | Alcance S4 = demo local; los trabajos vivos quedan en `en_proceso` y el store los marca `caducado_en_cliente` a los 10 min. Documentado como deuda, **no** se mete Celery ni Redis (descartados) | Si el jueves el trabajo se pierde en local, se reduce el volumen del dataset de demo antes que cambiar de arquitectura |
| R-2 | La fachada local se confunde con «no está hecho» en la revisión | Media | Medio | La franja de honestidad y el handoff lo dicen; el `Protocol` y `AlmacenGCS` escritos demuestran que la costura es real | Si la revisión lo cuestiona, se enseña T-6: la caducidad se prueba, no se promete |
| R-3 | Polars sobre 1 M filas no cabe en memoria del contenedor de demo | Baja | Alto | `scan_parquet` + `sink_csv` (streaming), nunca `read_parquet`. T-3 lo vigila indirectamente | Si aún así se satura, degradación acordada del plan: 500 K filas |
| R-4 | El sondeo de 3 s se cuela como fuga de temporizador entre rutas | Media | Medio | Temporizador único en el store, apagado en `visibilitychange` y por T-16 | Si T-16 falla dos veces, se pasa a `useIntervalFn` de VueUse |
| R-5 | Colisión de nombres con US-UX-09 en `docs/us-*/us-009.md` | **Alta** | Medio | Sufijo `-exportacion` en ambos archivos y aviso en la cabecera de los dos | Si un agente escribe sobre `us-009.md`, `git checkout -- docs/us-planning/us-009.md docs/us-handoff/us-009.md` y se reabre con el sufijo |
| R-6 | `main.py` en conflicto con US-023 | Media | Bajo | Una línea de `include_router` cada una, bloques separados, orden de commits encadenado | Conflicto de merge: gana quien commiteó antes y el otro añade su línea debajo |
| R-7 | La regla de oro: A4 vence el domingo 16 y esta US es del jueves 13 | Media | Alto | Si el jueves compite con A4, se entrega O1+O2 (backend + migración, criterios CA-1..CA-8, CA-11) y la pantalla queda con dos momentos en vez de tres | Cualquier retraso de A4 el jueves por la tarde congela O3 |
| R-8 | Fuga de `export_signing_key` en logs o en la URL de la captura | Baja | Alto | `SecretStr` en Settings; la firma es un HMAC hex, no la clave; ningún log de esta US incluye la URL completa | Si aparece en una captura, se regenera la clave antes de A4 |

---

## 11. Checklist de cierre verificable

- [ ] `make check` limpio (ruff, `ruff format`, mypy strict, eslint, gitleaks).
- [ ] `make test` en verde; cobertura backend ≥ 70 % sobre el denominador combinado `backend/app` + `ml`, frontend ≥ 50 %.
- [ ] `make db-up` aplicado y `db/schema.sql` regenerado y commiteado; `make db-rollback` verificado y `git diff --exit-code db/schema.sql` limpio tras volver a aplicar.
- [ ] Pruebas 401/403 parametrizadas por los cuatro roles en verde (gate de auth de la raíz), incluido el 404 por propiedad ajena.
- [ ] `app.routes` expone las cuatro rutas de `/api/export`, cada una con dependencia de seguridad y `scopes=[Scope.ANALISTA]` (T-9). **No se invoca ninguna auditoría de arranque: no existe en `f807a18`.**
- [ ] Si `backend/app/core/permissions.py` existe al implementar: las **cuatro** filas de `/api/export` presentes y `vigente`, y el bloque de `docs/security.md` regenerado con `render_permission_matrix()`. Si no existe: pendiente declarado en el handoff y **el archivo no se crea**.
- [ ] `grep -rn "export_storage_backend" backend/app --include=*.py | wc -l` → **2**.
- [ ] Paridad de claves `export.*` entre `es.json` y `en.json` (la verifica `idioma.spec.ts`, no una prueba propia); cero literales visibles en los `.vue`.
- [ ] `grep -rn "screen.exports.capability" frontend/` → **0**: las cuatro hojas huérfanas retiradas de los dos locales.
- [ ] `frontend/test/pantallas.spec.ts` con `/exploracion/exportar` fuera de `RUTAS_CON_ANDAMIAJE` y las tres pruebas parametrizadas en verde.
- [ ] `frontend/app/utils/navegacion.ts` **sin cambios** respecto de `f807a18`.
- [ ] `docs/us-planning/us-009.md` y `docs/us-handoff/us-009.md` (US-UX-09) **sin cambios**.
- [ ] Tres capturas de A4 tomadas con `?momento=solicitud|proceso|enlace` sobre estado real, con la franja de honestidad visible.
- [ ] Ninguna prueba nueva sobre placeholders; **ninguna prueba borrada**: `/exploracion/exportar` sale de `RUTAS_CON_ANDAMIAJE` (línea 41) y las tres pruebas parametrizadas siguen cubriendo las pantallas que aún son andamiaje.

> **Corrección fechada el 11-ago-2026 (auditoría cruzada, segunda pasada).** El último ítem del
> checklist todavía pedía dar por «borrada» la aserción de andamiaje de `exportar.vue` en
> `pantallas.spec.ts`, resto de la redacción anterior a la corrección de §3 y §5.3. Se decide alinearlo
> con la matriz vinculante de `docs/us-planning/auditoria-cruzada-s4.md` (fila `pantallas.spec.ts`:
> «cada una añade **su** caso; el archivo no se reescribe»): el cambio es retirar la ruta de
> `RUTAS_CON_ANDAMIAJE`, no borrar ningún caso. Motivo: las tres pruebas parametrizadas cubren las
> demás pantallas de andamiaje y borrarlas retiraría esa cobertura, además de dejar el cierre en
> contradicción con la propia tabla de archivos de este plan.
- [ ] Commits Conventional con scope `feat(E3): ...`, **sin trailer `Co-Authored-By`**.
- [ ] `docs/us-handoff/us-009-exportacion.md` actualizado de `planning` a `en curso` al abrir implementación.

---

## 12. P-2 — Contraste contra los `SKILL.md` (ejecutado el 13-ago-2026, tras implementar)

Se leyeron los cinco `SKILL.md` que P-2 nombra y se contrastaron **contra lo entregado**, no contra
lo planeado. Se listan solo las divergencias: lo que coincide no se anota. Cada una dice si es
**override deliberado** (la implementación es mejor y se sostiene), **deuda con dueño** (hay que
cerrarla, y quién) o **divergencia de la skill** (la skill está desactualizada respecto del
repositorio).

### 12.1 `portal-export-jobs`

| # | Lo que impone la skill | Lo entregado | Veredicto |
|---|---|---|---|
| 1 | Estados `queued / running / done / failed` | `pendiente / en_proceso / completado / fallido` | **Override deliberado.** `app_user.role` ya usa vocabulario castellano dentro de un `CHECK`, y el `CHECK` de `export_job` es del mismo tipo. Mezclar los dos idiomas en la misma clase de restricción era peor que apartarse de la skill |
| 2 | Trabajo ajeno → **403** | **404** | **Override deliberado y más seguro.** Un 403 confirma que el `job_id` existe y lo convierte en oráculo de enumeración. `portal-backend-api` repite el mismo criterio («dueño del job») y también queda superado |
| 3 | «La consulta a exportar pasa por la capa semántica (`SemanticQuery`); jamás filtros libres» | `filtros` es un mapa cerrado `{columna: valor \| [valores]}` validado por Pydantic y compilado a `pl.col(columna).is_in([...])`; una columna desconocida termina el trabajo `fallido` con `columna_desconocida` | **Deuda con dueño: US-011.** No es incumplimiento por descuido: `ml/semantic/compiler.py` **no existe** y `POST /api/metrics/aggregate` sigue `planificado`. Lo entregado **no ejecuta código libre**, que es el peligro que la regla protege, pero tampoco es la capa semántica. **El día que US-011 aterrice, `filtros` debe migrar a `SemanticQuery`.** Es el hallazgo de más peso de P-2 |
| 4 | Ruta en GCS `exports/{user}/{job_id}.{ext}` | `exports/{job_id}.{formato}` — **falta el segmento del usuario** | **Deuda con dueño: quien cree el bucket.** Consecuencia concreta: sin ese segmento no se puede escribir una regla IAM por prefijo de usuario. Hoy no duele porque `AlmacenGCS` no se ejecuta; corregirlo antes del primer despliegue con `EXPORT_STORAGE_BACKEND=gcs` cuesta una línea |
| 5 | Auditoría con `duration_s` | `started_at` + `finished_at` | **Override deliberado.** La duración se deriva de los dos instantes sin perder información, y los instantes responden además «cuándo empezó», que un escalar no responde |
| 6 | Prueba de no bloqueo con `GET /api/catalog/search` < 500 ms | La misma prueba con `GET /health` | **Divergencia con motivo, y sonda más débil.** La suite corre **sin PostgreSQL** y `catalog/search` exige base; `/health` es lo más fuerte que se puede afirmar sin ella, y es la sonda que fija el gate de `backend/AGENTS.md`. **Anotado**: cuando exista entorno de integración, añadir la sonda de catálogo, que sí atraviesa la base |
| 7 | Lifecycle de 7 días del bucket (Terraform) | No existe | **Fuera de alcance declarado** (recorte #3 de S4), no un olvido |

### 12.2 `portal-backend-api`

- Su tabla canónica reserva **dos** rutas de export (`POST /api/export` y `GET /api/export/{job_id}`)
  y esta US montó **cuatro**: el historial (`GET /api/export`) y la descarga
  (`GET /api/export/{job_id}/download`) no están en la skill y sí en los criterios CA-5 y CA-6.
  **La skill está desactualizada**; el registro de permisos ya refleja las cuatro.
- Todo lo demás se cumple: `Security(...)` en los cuatro verbos, `response_model` Pydantic en los
  cuatro, router→service→model sin lógica de negocio en el router, `structlog` sin `print`, y el
  **422 con sugerencia difusa del catálogo** que la skill exige, resuelto con
  `difflib.get_close_matches` y umbral `0.6`.
- «Silo caído → 503 parcial tipificado»: se cumple en sus dos formas — `503 trabajos_no_disponibles`
  cuando el registro no responde, y `origen_ausente` como estado del trabajo cuando el Parquet falta.

### 12.3 `portal-db-migrations`

Sin divergencias de fondo: `make db-new`, secciones `up`/`down`, `schema.sql` versionado tras
`db-up`, `TIMESTAMPTZ DEFAULT now()`, FK con `ON DELETE` explícito. Una divergencia de forma: su
tabla de «migraciones canónicas» sitúa `create_export_job` en tercer lugar y en el repositorio es la
**quinta**. El orden real lo fija el calendario de sprints, no la skill.

### 12.4 `portal-db-models`

| # | Lo que impone la skill | Lo entregado | Veredicto |
|---|---|---|---|
| 1 | Patrón de tres clases `XBase → X(table=True) → XOut/XCreate/XUpdate` | `ExportJob` es tabla directa; los contratos son `SolicitudExportacion`, `TrabajoResumen` y `TrabajoDetalle` | **Override deliberado.** No hay campos compartidos que un `ExportJobBase` pudiera factorizar: el contrato **renombra casi todo** (`row_count`→`filas`, `byte_size`→`tamano_bytes`, `created_at`→`solicitado_en`) y **omite `object_key` a propósito**. Una clase base con cero campos comunes es andamiaje, y el proyecto prohíbe el andamiaje |
| 2 | `export_job` añade `size_bytes` y `duration_s` | `byte_size` y los dos instantes | **Divergencia de nombre** en el primero (la columna sigue el orden sustantivo del resto de la tabla) y override en el segundo, por el motivo de 12.1 §5 |

Se cumple lo esencial: los modelos **reflejan** lo que creó dbmate y no lo generan, nunca se llama a
`SQLModel.metadata.create_all()`, hay campo de auditoría `created_at`, y los docstrings son
Google-style en inglés.

### 12.5 `portal-testing`

- **Cumplido**: cobertura backend **98,18 %** sobre el denominador combinado (umbral 70 %) y frontend
  **88,44 %** de líneas (umbral 50 %); matriz de permisos parametrizada por los cuatro roles con 401
  sin token y 403 sin permiso; ninguna llamada real a Gemini.
- **Divergencia de la skill**: su matriz de ejemplo escribe `("/api/export", "analista", 202)`, pero
  `202` es del `POST`; el `GET /api/export` del historial responde **200**. La skill mezcla verbos en
  una fila sin verbo.
- **Deuda con dueño: US-004.** La skill exige **smoke tests post-deploy en el pipeline** (login,
  catálogo, consulta semántica, chat con tool call, export). `.github/` no existe todavía, así que
  esta US no puede cerrarlo; el paso de export de ese smoke queda especificado aquí: solicitar,
  sondear hasta terminal, descargar y comprobar `Content-Disposition`.

### 12.6 Lo que este contraste cambia

Nada del código entregado: ninguna divergencia resultó ser un defecto. Deja **tres obligaciones con
dueño escrito** —el `SemanticQuery` de US-011, el segmento de usuario en la clave de GCS antes del
primer despliegue, y el smoke post-deploy de US-004— y **tres skills desactualizadas respecto del
repositorio** (`portal-export-jobs` en estados y en el 403, `portal-backend-api` en el número de
rutas de export, `portal-testing` en la fila sin verbo de su matriz).
