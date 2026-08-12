# Handoff US-009 — Exportación en segundo plano (alcance S4)

> **AVISO DE COLISIÓN DE NOMBRES.** Este handoff **no** es el de US-UX-09. `docs/us-handoff/us-009.md`
> y `docs/us-planning/us-009.md` ya existen y pertenecen a **US-UX-09 (Guía de estilos, A4)**:
> **no se tocan**. Los archivos de esta US llevan el sufijo `-exportacion`.

**Estado**: planning
**Epic**: E3 · **Sprint**: S4 · **Actividad**: A4 (apartado 3, prototipos, 50 %)
**Rama**: `us-009-exportacion` (una rama por US, commits locales encadenados, sin PR — discrepancia RU-11 declarada)
**SHA base**: `f807a18`
**Estimación**: 1 SP · **Día**: jue 13-ago-2026 · **Estado esperado al cierre**: demostrada en prototipo
**Plan**: [`docs/us-planning/us-009-exportacion.md`](../us-planning/us-009-exportacion.md)
**Fuera de alcance (recorte #3)**: política de ciclo de vida del bucket y auditoría de duración

---

## Dominios y sub-tareas tocados

- [x] backend
- [x] frontend
- [ ] ml
- [ ] agent
- [ ] infra
- [x] db
- [x] docs

Tres olas **estrictamente secuenciales**, un agente por ola. La US vale 1 SP: no se reparte en
paralelo porque el frontend lee el contrato que el backend escribe, y quien escribe va primero.

| Ola | Agente | Subagente | Write-set exclusivo | Día |
|---|---|---|---|---|
| **O1** | esquema | `portal-db-migrations` + `portal-db-models` | `db/migrations/20260813090000_create_export_job.sql` · `db/schema.sql` · `backend/app/models/export.py` · `tests/backend/test_export_job_migracion.py` | jue 13, mañana |
| **O2** | backend | `portal-export-jobs` + `portal-backend-api` | `backend/app/services/almacen/{__init__,local,gcs}.py` · `backend/app/services/export_service.py` · `backend/app/api/export.py` · `backend/app/main.py` (1 línea) · `backend/app/core/config.py` · `backend/.env.example` · `tests/backend/test_export_{endpoint,almacen_firmado,estado_scopes}.py` | jue 13, mediodía |
| **O3** | frontend | `portal-frontend-nuxt` + `portal-testing` | `frontend/app/pages/exploracion/exportar.vue` · `frontend/app/stores/exportaciones.ts` · `frontend/app/composables/useExportaciones.ts` · `frontend/app/components/exportacion/*` · `frontend/app/types/exportacion.ts` · `frontend/i18n/locales/{es,en}.json` (solo `export.*` y las dos hojas de `screen.exports`) · `frontend/test/exportaciones.spec.ts` · `frontend/test/pantallas.spec.ts` (línea 41) | jue 13, tarde |

O3 **lee sin escribir** `backend/app/models/export.py` y `backend/app/api/export.py`.

---

## Zonas sensibles

| Archivo | Por qué |
|---|---|
| `docs/us-planning/us-009.md` · `docs/us-handoff/us-009.md` | **Son de US-UX-09.** Sobrescribirlos destruye el entregable de la guía de estilos. Prohibido tocarlos |
| `backend/app/main.py` | Lo toca también US-023. Cada US añade **una sola línea** de `include_router` en bloque propio; nada de reordenar imports |
| `backend/app/core/scopes.py` | Propiedad de US-016. Esta US **consume** `Scope` y `ErrorCode`; no abre vocabulario de roles nuevo |
| `frontend/app/utils/navegacion.ts` | **NO se toca**: `/exploracion/exportar`, su prototipo y la faceta `nav.facets.items.exportHistory` ya están registrados desde US-001. Añadir algo sería duplicar |
| `frontend/i18n/locales/{es,en}.json` | Compartido con las tres US del chat. US-009 escribe **solo** bajo `export.*`, reescribe `screen.exports.description` y **retira** `screen.exports.capability.*` (cuatro hojas huérfanas). La raíz es `screen`, **en singular**. Prohibido reordenar el resto |
| `db/schema.sql` | Se regenera con `make db-up`, **jamás se edita a mano**: CI lo compara byte a byte |
| `db/migrations/*` ya aplicadas | Inmutables. Una migración aplicada no se modifica: se escribe otra |
| `backend/app/core/config.py` | Pydantic Settings estricto. Los cuatro ajustes nuevos llevan valor por defecto seguro; **ninguno** puede hacer fallar el arranque de quien no exporta |
| `export_signing_key` | `SecretStr`. Jamás en logs, jamás en una captura, jamás en `.env.example` con valor real |
| `frontend/test/pantallas.spec.ts` | **Compartido y secuencial con US-023.** Verificado el 11-ago-2026: la línea 41 define `RUTAS_CON_ANDAMIAJE = RUTAS_CONTRATO.filter(ruta => ruta !== RUTA_ACCESO)` e incluye `/exploracion/exportar`. US-009 (jue 13) añade su ruta al filtro; US-023 (vie 14) añade `RUTA_ASISTENTE` encima. **No se borra ninguna prueba**: retirarla quitaría la cobertura de las pantallas que siguen siendo andamiaje |
| `backend/app/core/permissions.py` · `docs/security.md` | **No existen en `f807a18`** y son write-set de US-016, que sigue en `planning`. Si US-016 aterriza antes del jueves, US-009 añade **cuatro** filas (`POST /api/export`, `GET /api/export`, `GET /api/export/{job_id}`, `GET /api/export/{job_id}/download`) y regenera el bloque de `docs/security.md` con `render_permission_matrix()`. Si no, **no se crean**: se declara el pendiente |

---

## Contratos con otras US

1. **US-016 (RBAC)** — **dependencia dura no satisfecha al planear.** Lo que sí existe y se consume es
   `backend/app/core/scopes.py`: `Scope.ANALISTA`, `ErrorCode` y la jerarquía ordinal. Lo que **no**
   existe es la matriz: `backend/app/core/permissions.py`, `SCOPE_REGISTRY`, `PUBLIC_ROUTES`,
   `audit_scope_coverage` y `docs/security.md` (verificado el 11-ago-2026 sobre `f807a18`; el handoff
   de US-016 está en `planning`). Consecuencia: **la auditoría de arranque no es una prueba gratis**,
   T-9 afirma sobre `app.routes`, y la escritura del registro es condicional. Además la matriz de
   US-016 §4.3 reserva **dos** filas de `/api/export` y esta US monta **cuatro**: las otras dos las
   añade US-009 el día que el archivo exista.
2. **US-023 (chat SSE)** — único punto de contacto: la línea de montaje en `main.py`. El contrato SSE
   v1 **no aplica** a esta US: la exportación se consulta por sondeo, no por SSE, decisión razonada en
   §A-3 del plan.
3. **US-015 (auth)** — consumido: `get_current_user`, el JWT propagado por el proxy Nitro, y el
   usuario `dhernandez` con rol `analista` sembrado en `app_user`.
4. **US-UX-09 (guía de estilos)** — los componentes de exportación consumen tokens desde
   `frontend/app/utils/tokens.generated.ts` (origen `design/sistema.py`). `uxdoc.sty` es del
   **informe** y está congelado: no se deriva nada de él.
5. **Consumidores futuros** — `AlmacenDeExportaciones` es el `Protocol` que reutilizará cualquier US
   que produzca artefactos descargables. La factoría `crear_almacen` es el único punto de elección.

---

## Decisiones tomadas en planeación

1. **Fachada de infraestructura con `Protocol` y dos implementaciones reales.**
   `AlmacenDeExportaciones` con `AlmacenLocalFirmado` (HMAC-SHA256 sobre `f"{object_key}:{exp}"`,
   comparado con `hmac.compare_digest`) y `AlmacenGCS`
   (`generate_signed_url(version="v4", expiration=timedelta(hours=24))`, escrito pero no ejecutado en
   S4). El `exp` va **dentro** del material firmado; si no, la caducidad es decorativa.
2. **Las 24 h se verifican el jueves 13 sin proyecto GCP** inyectando un `Reloj` Protocol: firmar en
   `T`, pedir en `T+23 h 59 m` → 200; en `T+24 h 01 m` → **410 `enlace_caducado`**; firma alterada →
   **403 `firma_invalida`**. Determinista, sin esperas, sin red.
3. **Un solo punto de elección**: `crear_almacen(settings)` en `backend/app/services/almacen/__init__.py`,
   gobernado por `export_storage_backend: Literal["local","gcs"] = "local"`. Verificable:
   `grep -rn "export_storage_backend" backend/app --include=*.py | wc -l` → **2**.
4. **Estado consultable desde cualquier pantalla = store Pinia `exportaciones` montado en el layout,
   con sondeo de 3 000 ms.** Justificación numérica: el trabajo objetivo (1 M filas a CSV con
   `sink_csv`) tarda 8–15 s, así que 3 s da 3–5 muestras del estado intermedio; a 1 s se triplica el
   tráfico sin información nueva; a 5 s un trabajo corto salta de `pendiente` a `completado` sin
   estado intermedio visible, que es justo lo que A4 necesita capturar. Coste: 20 req/min por usuario
   activo, irrelevante. Un único temporizador global, apagado sin trabajos vivos, con
   `document.hidden`, y tope de 200 sondeos (10 min).
5. **Scope `analista` en los cuatro verbos**, no `operativo`: la extracción masiva es la salida de
   datos con mayor riesgo de fuga del portal, y Diego Hernández es `analista` en `app_user`.
   Verificado con matriz parametrizada: `operativo` → 403 en los cuatro verbos.
6. **Propiedad del trabajo: pedir el trabajo de otro usuario devuelve 404, no 403.** Un 403
   confirmaría la existencia del `job_id` y lo convertiría en oráculo de enumeración. `admin` ve el
   historial completo (gobierno) pero **no** descarga archivos ajenos.
7. **Los tres momentos son estados reales; lo único que se manipula es el tiempo.**
   `?momento=solicitud|proceso|enlace` fija qué trabajo real queda expandido y desactiva el
   auto-avance; **no fabrica datos** (con historial vacío, `?momento=enlace` muestra vacío explícito).
   `export_demo_delay_seconds` (0 por defecto, 8 en demo) estira la duración del trabajo real para
   poder capturarlo. Franja de honestidad `export.demo.notice` siempre visible cuando ese retraso es
   mayor que cero.
8. **La migración `create_export_job` es la única de las cinco US.** Estados como `CHECK` y no como
   `ENUM` de PostgreSQL (añadir un valor a un ENUM es migración con bloqueo y el vocabulario aún se
   mueve). Dos `CONSTRAINT` de coherencia: `completado` exige `object_key`, `expires_at` y
   `finished_at`; `fallido` exige `error_code`. Tres índices, cada uno justificado:
   `(requested_by, created_at DESC)` para el historial (filtro + orden sin `SORT`); parcial
   `(status) WHERE status IN ('pendiente','en_proceso')` para los trabajos vivos (un índice total
   sobre cuatro valores sería inútil por baja cardinalidad); parcial `(expires_at) WHERE status =
   'completado'` para la purga futura. **Sin** índice sobre `dataset` ni GIN sobre `filters`: no hay
   consulta que los use. `-- migrate:down` revierte índices y tabla.
9. **`BackgroundTasks` de FastAPI, sin Celery ni Redis** (descartados por la raíz). Se acepta como
   deuda declarada que un trabajo vivo se pierde si Cloud Run escala a cero; el store lo marca
   `caducado_en_cliente` a los 10 min.
10. **La tarea de fondo usa `scan_parquet` + `sink_csv` (streaming), nunca `read_parquet`**: el gate
    de `backend/AGENTS.md` exige `/health` por debajo de 500 ms durante una exportación de 1 M filas,
    y materializar en memoria bloquearía el bucle de eventos.
11. **No toca la nube.** El criterio de las 24 h se entrega con la fachada local; el bucket se crea
    cuando exista el proyecto, y entonces el cambio es `EXPORT_STORAGE_BACKEND=gcs`, no una
    refactorización.
12. **`navegacion.ts` no se toca**: la ruta ya existe desde US-001. Esto elimina el único solape real
    con las otras US de la ola y deja los tres write-sets disjuntos.

---

## Pendientes al abrir implementación

- **P-1** — Leer `frontend/AGENTS.md` y `db/AGENTS.md` (no leídos en planeación por presupuesto de
  tiempo) y contrastar que ninguna regla de carpeta contradice §A-3 (sondeo) ni §8 (índices).
- **P-2** — Contrastar el plan contra los `SKILL.md` de `portal-export-jobs`, `portal-backend-api`,
  `portal-db-migrations`, `portal-db-models` y `portal-testing`; anotar en el plan lo que cada uno
  imponga y que aquí se haya derivado de `backend/AGENTS.md`.
- **P-3** — **Cerrado el 11-ago-2026 por la auditoría cruzada.** `pantallas.spec.ts:41` sí cubre
  `/exploracion/exportar`; el cambio es una línea del filtro `RUTAS_CON_ANDAMIAJE`, ya declarado en el
  write-set de O3, y **no se borra ninguna prueba**.
- **P-9** — Verificar al abrir O2 si `backend/app/core/permissions.py` existe. Si existe: cuatro filas
  + `docs/security.md` regenerado. Si no: no se crea y se anota aquí el pendiente para US-016.
- **P-4** — Confirmar si `polars` ya está en `backend/pyproject.toml`; si no, `poetry add polars`.
  `google-cloud-storage` va como extra opcional y **no** se instala en S4.
- **P-5** — Ejecutar `make db-new SLUG=create_export_job` para obtener la marca de tiempo real del
  archivo de migración (la del plan, `20260813090000`, es la prevista).
- **P-6** — Decidir el conjunto exacto de `dataset` válidos del `field_validator` contra los silos que
  produce `make data`; hoy el catálogo aún no está publicado.
- **P-7** — Tomar y archivar las tres capturas de A4 con la franja de honestidad visible, sobre
  estado real, antes del domingo 16.
- **P-8** — Actualizar este handoff de `planning` a `en curso` al empezar O1, y a `cerrada` con el
  resultado de QA al terminar.
