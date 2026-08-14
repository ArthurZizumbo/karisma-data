# Handoff US-009 — Exportación en segundo plano (alcance S4)

> **AVISO DE COLISIÓN DE NOMBRES.** Este handoff **no** es el de US-UX-09. `docs/us-handoff/us-009.md`
> y `docs/us-planning/us-009.md` ya existen y pertenecen a **US-UX-09 (Guía de estilos, A4)**:
> **no se tocan**. Los archivos de esta US llevan el sufijo `-exportacion`.

**Estado**: testing
**Epic**: E3 · **Sprint**: S4 · **Actividad**: A4 (apartado 3, prototipos, 50 %)
**Rama**: `us-009-exportacion` (una rama por US, commits locales encadenados, sin PR — discrepancia RU-11 declarada)
**SHA base**: `a251652`
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

> **Los quince pendientes de esta lista están cerrados al 13-ago-2026.** Se conserva la redacción
> original porque documenta qué se sabía al abrir; el estado real de cada uno está en
> «Cierre de la US — integración», al final del documento.

- **P-1** — Leer `frontend/AGENTS.md` y `db/AGENTS.md` (no leídos en planeación por presupuesto de
  tiempo) y contrastar que ninguna regla de carpeta contradice §A-3 (sondeo) ni §8 (índices).
- **P-2** — Contrastar el plan contra los `SKILL.md` de `portal-export-jobs`, `portal-backend-api`,
  `portal-db-migrations`, `portal-db-models` y `portal-testing`; anotar en el plan lo que cada uno
  imponga y que aquí se haya derivado de `backend/AGENTS.md`. **Cerrado: §12 del plan.**
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

---

## O1 — esquema (ejecutada)

**Fecha**: jue 13-ago-2026 · **SHA base**: `a251652` (rama `us-018`, árbol compartido con US-018 y
US-023 en vuelo) · **Estado de la ola**: completa, con base de datos real levantada.

### Archivos escritos

| Ruta | Acción | Nota |
|---|---|---|
| `db/migrations/20260813204211_create_export_job.sql` | creado | **La marca de tiempo real es `20260813204211`**, no la prevista `20260813090000` del §3 y §8 del plan. La generó `make db-new SLUG=create_export_job` (cierra **P-5**) |
| `db/schema.sql` | regenerado por `make db-up` | No se editó a mano en ningún momento |
| `backend/app/models/export.py` | creado | Espejo del esquema + los cuatro contratos de §4.1 |
| `tests/backend/test_export_job_migracion.py` | creado | 14 casos, sin PostgreSQL: lee el SQL como texto |

Nada más se tocó. `backend/app/core/`, `backend/app/api/`, `backend/app/services/`,
`backend/app/main.py` y `frontend/` siguen intactos: son O2 y O3.

### Verificación ejecutada contra PostgreSQL real

La base de `make dev` respondía, así que la ola no dejó pendiente el volcado:

1. `make db-up` → `Applied: 20260813204211_create_export_job.sql`, `Writing: ./db/schema.sql`.
2. `make db-rollback` → revierte; `grep -c export_job db/schema.sql` baja a **0**, o sea que el
   `-- migrate:down` deshace de verdad los tres índices y la tabla.
3. `make db-up` otra vez → `db/schema.sql` **byte a byte idéntico** al del paso 1 (`diff` vacío
   contra la copia previa). La migración es reversible y reaplicable.
4. `db/schema.sql` contiene la tabla, los tres índices, los dos `CONSTRAINT` de coherencia, los
   cuatro `COMMENT` y el quinto `INSERT INTO public.schema_migrations`. Después US-018 aplicó su
   propia migración `20260813205114_add_app_user_updated_at.sql` sobre la misma base: el volcado
   de hoy lleva **seis** versiones, las cinco de esta cadena más la suya. No hubo pisada: el
   `export_job` sobrevivió intacto a su `db-up`.

### Calidad de la capa

- `ruff check --config backend/pyproject.toml` sobre los dos archivos → limpio.
- `ruff format --check` sobre los dos archivos → ya formateados.
- `mypy --config-file backend/pyproject.toml backend/app/models/export.py tests/backend/test_export_job_migracion.py` → `Success`.
- `pytest -c backend/pyproject.toml tests/backend/test_export_job_migracion.py` → **14 passed**,
  cobertura de `backend/app/models/export.py` al **100 %**.
- Suite completa `tests/backend` → **435 passed, 2 failed**. Las dos que fallan son de **US-018 en
  vuelo**, no de esta ola: `test_migracion_app_user.py::test_la_tabla_declara_las_columnas_del_modelo`
  (su `AppUser.updated_at`) y `permisos/test_permission_matrix.py[...GET /api/users...]`. También
  hay un error de mypy preexistente en `backend/app/services/user_service.py:83`, verificado con y
  sin este módulo: el conteo no cambia.

### Decisiones de la ola

1. **P-6 cerrado — `DATASETS_EXPORTABLES = ("creditos", "liquidez", "derivados")`.** El criterio es
   *la fuente tiene extracto real detrás*, y la autoridad es el catálogo: las **tres** filas de
   `catalog_source` con `has_extract = true` en `db/seeds/catalog.sql`. Las otras nueve fuentes
   documentadas no tienen Parquet, así que aceptarlas crearía un trabajo que solo puede acabar
   `fallido`. Los mismos tres nombres son las claves de `SILOS` en `ml/data/schemas.py` y los tres
   archivos que `make data` escribe en `data/silos/`: catálogo, generador y disco coinciden.
   `serie_tablero` queda **fuera** a propósito — vive en `data/aggregates/`, no tiene fila en
   `catalog_source` y ya lo sirve `GET /api/metrics/series`.
2. **Constante congelada y no consulta a la base.** El `field_validator` corre mientras FastAPI aún
   parsea el cuerpo, antes de que exista sesión: consultar ahí metería un viaje a la base en la ruta
   de una petición malformada y ataría la validación del cuerpo a que el seed esté cargado. Para que
   la constante no envejezca en silencio, una prueba la compara contra las filas `has_extract` del
   seed (`test_datasets_exportables_son_los_del_catalogo_con_extracto`). Los `.parquet` de
   `data/silos/` **no** sirven de referencia en pruebas: están en `.gitignore`.
3. **Encabezado de la migración: «Quinta migracion del proyecto», no «Tercera».** El §8 del plan
   decía «Tercera» y ya hay cuatro aplicadas. El SQL se copió íntegro; solo se corrigió el ordinal y
   se añadieron dos párrafos de prosa (por qué los dos `CONSTRAINT` y por qué esos tres índices),
   como pide `db/AGENTS.md` («encabezado que explique por qué, no qué hace el SQL»).
4. **Nombres del contrato de cable en español**, como `SeriesParams` y `ErrorSerie`: `job_id`,
   `dataset`, `formato`, `estado`, `filas`, `tamano_bytes`, `solicitado_en`, `iniciado_en`,
   `terminado_en`, `error`, `url_descarga`, `caduca_en`. Las columnas de la tabla siguen en inglés
   (`export_format`, `filters`, `row_count`, `byte_size`): el modelo espeja la base, el contrato
   espeja la interfaz.
5. **`caduca_en` vive en `TrabajoDetalle`, no en `TrabajoResumen`.** La caducidad que le importa al
   lector es la del enlace que está mirando, y el enlace se firma con ese instante dentro del
   material firmado: publicar uno sin el otro describiría un plazo que no pertenece a nada. Por eso
   `TrabajoDetalle` **hereda** de `TrabajoResumen` y añade exactamente los dos campos.
6. **`status` y `export_format` se tipan `str` en `ExportJob`**, no con sus enums, por la misma razón
   que `AppUser.role`: con la enumeración ahí SQLAlchemy mapearía la columna a su `Enum` nativo y la
   columna real es `TEXT` con `CHECK`. El vocabulario cerrado vive en los contratos.
7. **Ningún `index=True` en el modelo.** Los tres índices reales son uno compuesto y dos parciales,
   y ninguno se puede expresar en la clase; declarar un índice de una columna describiría un objeto
   que no existe en `db/schema.sql`.
8. **`filters` se mapea con `sa_type=JSONB`** (`sqlalchemy.dialects.postgresql`): SQLModel no tiene
   mapeo por defecto para `dict` y sin eso el módulo ni siquiera importa.
9. **No se escribió ningún ayudante de conversión fila→contrato.** §4.1 congela seis símbolos y
   ninguno lo es; la conversión es de `ExportService` (O2). Lo único que O2 debe respetar está
   escrito en los docstrings: `object_key` jamás se serializa.

### Símbolos que exporta `backend/app/models/export.py` (O2 y O3 consumen esto)

```python
DATASETS_EXPORTABLES: Final[tuple[str, ...]] = ("creditos", "liquidez", "derivados")

class EstadoTrabajo(StrEnum):
    PENDIENTE = "pendiente"
    EN_PROCESO = "en_proceso"
    COMPLETADO = "completado"
    FALLIDO = "fallido"

    @property
    def es_terminal(self) -> bool: ...   # True solo en COMPLETADO y FALLIDO

class FormatoExportacion(StrEnum):
    CSV = "csv"
    XLSX = "xlsx"

class ExportJob(SQLModel, table=True):
    __tablename__ = "export_job"
    id: uuid.UUID | None            # PK, gen_random_uuid() del lado de la base
    requested_by: uuid.UUID         # FK app_user.id, ON DELETE RESTRICT
    dataset: str
    export_format: str              # str, no FormatoExportacion (columna TEXT + CHECK)
    filters: dict[str, Any]         # sa_type=JSONB, default_factory=dict
    status: str                     # default "pendiente"
    row_count: int | None
    byte_size: int | None
    object_key: str | None          # interno: nunca sale en una respuesta
    error_code: str | None
    created_at: datetime | None
    started_at: datetime | None
    finished_at: datetime | None
    expires_at: datetime | None

class SolicitudExportacion(BaseModel):        # model_config = ConfigDict(extra="forbid")
    dataset: str
    formato: FormatoExportacion = FormatoExportacion.CSV
    filtros: dict[str, Any]                   # Field(default_factory=dict)

    @field_validator("dataset")
    @classmethod
    def dataset_must_be_known(cls, value: str) -> str: ...

class TrabajoResumen(BaseModel):
    job_id: uuid.UUID
    dataset: str
    formato: FormatoExportacion
    estado: EstadoTrabajo
    filas: int | None = None
    tamano_bytes: int | None = None
    solicitado_en: datetime
    iniciado_en: datetime | None = None
    terminado_en: datetime | None = None
    error: str | None = None

class TrabajoDetalle(TrabajoResumen):
    url_descarga: str | None = None
    caduca_en: datetime | None = None
```

Detalles que O2 y O3 no pueden adivinar:

- `dataset_must_be_known` **normaliza con `strip()`** y devuelve el nombre limpio: `"  creditos  "`
  es válido.
- Cuando rechaza, el `ValueError` (que Pydantic convierte en 422) dice
  `'<valor>' no es un conjunto exportable. Los exportables son creditos, liquidez, derivados` y
  añade `; el mas parecido es '<sugerencia>'` **solo** si `difflib.get_close_matches` supera el
  umbral `0.6`. Con un nombre lejano (`nomina`) no hay pista, a propósito.
- `SolicitudExportacion` es `extra="forbid"`: una clave de más es 422, no un campo ignorado.
- `EstadoTrabajo.es_terminal` es el predicado con el que el store de O3 decide apagar el
  temporizador. No hay que reimplementarlo en TypeScript con una lista de literales.

### Qué quedó desactualizado en `db/AGENTS.md` (sección «Estado»)

No lo toqué —está fuera de mi write-set— pero el siguiente que edite esa guía debe corregir:

1. «Cuatro migraciones aplicadas» → hoy son **seis** aplicadas: las cuatro de la tabla, más
   `20260813204211_create_export_job.sql` (esta ola) y `20260813205114_add_app_user_updated_at.sql`
   (US-018, aterrizó en paralelo esta tarde).
2. «Cinco tablas reales, más `schema_migrations`» → son **seis**: `export_job` existe.
3. **«No existe `export_job` ni tabla alguna de jobs de exportación» es literalmente falso desde
   hoy.** Es la frase más engañosa de la sección: quien la lea creerá que tiene que crearla.
4. La tabla de migraciones necesita su fila: `20260813204211_create_export_job.sql` → «`export_job`
   con `CHECK` de estados y formatos, dos `CONSTRAINT` de coherencia y tres índices (uno compuesto,
   dos parciales)».

### Pendientes que esta ola deja abiertos

- **P-9 verificado hoy y resuelto en su parte de hecho**: `backend/app/core/permissions.py` **sí
  existe** ya en el árbol, con `SCOPE_REGISTRY` y **dos** filas de esta US en estado
  `planificado` — `RouteKey("POST", "/api/export")` y `RouteKey("GET", "/api/export/{job_id}")`,
  ambas con `scopes=(Scope.ANALISTA,)` y `us="US-009"` (líneas 215 y 221). La condicional del §3 del
  plan se activa: **O2** las pasa a `vigente`, **añade** `RouteKey("GET", "/api/export")` y
  `RouteKey("GET", "/api/export/{job_id}/download")` —porque el router monta cuatro verbos y solo
  hay dos filas reservadas— y regenera el bloque de `docs/security.md` con
  `render_permission_matrix()` en el mismo commit. Esta ola no lo tocó: el archivo está fuera de su
  write-set y `assert_scope_coverage()` solo se enfada cuando el router exista.
- **P-4**: `polars (==1.43.2)` ya está en el grupo principal de `backend/pyproject.toml`. No hace
  falta `poetry add`; el pin exacto no se afloja.
- Nada de la migración quedó a medias: no hay pendiente de esquema.

---

## O2 — backend (ejecutada)

**Fecha**: jue 13-ago-2026 · **SHA base**: `a251652` (árbol compartido; US-018 y US-023 ya habían
aterrizado `api/users.py`, `api/chat.py` y sus filas de permisos cuando esta ola empezó) ·
**Estado de la ola**: completa. Suite en verde y sin PostgreSQL.

### Archivos escritos

| Ruta | Acción | Nota |
|---|---|---|
| `backend/app/services/almacen/__init__.py` | creado | `Reloj`, `RelojDelSistema`, `AlmacenDeExportaciones`, `AlmacenServidoPorLaApi`, `EnlaceCaducado`, `FirmaInvalida`, `derivar_clave_de_firma`, `crear_almacen` |
| `backend/app/services/almacen/local.py` | creado | `AlmacenLocalFirmado` (HMAC-SHA256, `compare_digest`, raíz en el directorio temporal) |
| `backend/app/services/almacen/gcs.py` | creado | `AlmacenGCS`. Import de `google.cloud.storage` **perezoso**; escrito, no ejecutado |
| `backend/app/services/export_service.py` | creado | `ExportService` (las cinco corrutinas), `TrabajoRepository`, `SqlTrabajoRepository`, `ExportErrorCode`, tres excepciones, `get_export_repository`, `get_export_service` |
| `backend/app/api/export.py` | creado | Los cuatro verbos, los cuatro con `Security(get_current_user, scopes=[Scope.ANALISTA])` |
| `backend/app/main.py` | modificado | Una línea de `include_router(export.router)` y el nombre `export` añadido al import existente. Nada reordenado |
| `backend/app/core/config.py` | modificado | Los cuatro ajustes de §4.2, con valor por defecto seguro |
| `backend/app/core/permissions.py` | modificado | `POST /api/export` y `GET /api/export/{job_id}` pasan a `vigente`; **añadidas** `GET /api/export` y `GET /api/export/{job_id}/download`. Ninguna fila ajena tocada |
| `docs/security.md` | regenerado | Solo el bloque entre marcadores, con `render_permission_matrix()`. Jamás a mano |
| `backend/.env.example` | modificado | Sección nueva con los cuatro ajustes; `EXPORT_SIGNING_KEY` vacía, como las tres obligatorias |
| `tests/backend/test_export_endpoint.py` | creado | T-1 a T-4 más el ciclo de fallos, el contrato SQL del repositorio y el 503 |
| `tests/backend/test_export_almacen_firmado.py` | creado | T-5 a T-8 más las cuatro negativas de la descarga |
| `tests/backend/test_export_estado_scopes.py` | creado | T-9 a T-12 |

Nada más se tocó. `frontend/`, `db/`, `ml/`, `backend/app/core/scopes.py` y
`backend/app/models/export.py` siguen intactos.

### Contrato de cable que consume O3

Prefijo `/api/export`, los cuatro verbos con scope `analista` (`operativo` recibe 403).

| Verbo | Éxito | Cuerpo |
|---|---|---|
| `POST /api/export` | **202** | `TrabajoDetalle` en estado `pendiente`, sin `url_descarga` ni `caduca_en` |
| `GET /api/export?limite=50` | 200 | `TrabajoResumen[]`, `created_at` descendente, solo del llamante (`limite` entre 1 y 200) |
| `GET /api/export/{job_id}` | 200 | `TrabajoDetalle` — este es el endpoint del sondeo de 3 000 ms |
| `GET /api/export/{job_id}/download?exp=<epoch>&sig=<hex>` | 200 | El archivo, `text/csv`, con `Content-Disposition` de adjunto |

**Forma exacta de la URL firmada.** `TrabajoDetalle.url_descarga` es una ruta **relativa**, nunca
absoluta, para que el proxy de Nitro la reenvíe sin reescritura:

```
/api/export/<job_id>/download?exp=<epoch en segundos>&sig=<hex de 64 caracteres>
```

`sig = HMAC-SHA256(clave, f"{object_key}:{exp}")` con `object_key = f"{job_id}.{formato}"`. El
vencimiento viaja **dentro** del material firmado. `caduca_en` es exactamente el instante que ese
`exp` codifica (truncado al segundo) y equivale a `terminado_en + EXPORT_LINK_TTL_HOURS`. Los dos
campos —`url_descarga` y `caduca_en`— viajan juntos y solo aparecen cuando el estado es `completado`
**y** el llamante es el dueño del trabajo.

**Códigos de error, que es lo que O3 pinta.** Hay dos formas de cuerpo y conviene no confundirlas:

- Los fallos de sesión y de permiso vienen de US-015 y llevan `detail` como **cadena suelta**:
  `401 credenciales_ausentes` / `sesion_expirada` / `sesion_revocada` / `credenciales_invalidas`, y
  `403 permisos_insuficientes`. Todo 401 trae `WWW-Authenticate: Bearer realm="karisma", ...,
  scope="analista"`.
- Los fallos propios de exportación llevan `detail` como **objeto con `codigo`**, o sea
  `{"detail": {"codigo": "..."}}`:

| HTTP | `detail.codigo` | Cuándo |
|---|---|---|
| 404 | `trabajo_no_encontrado` | El trabajo no existe, es de otro usuario, no terminó, o su archivo ya no está |
| 410 | `enlace_caducado` | La firma es nuestra y el plazo ya pasó |
| 403 | `firma_invalida` | La firma no es de este portal |
| 503 | `trabajos_no_disponibles` | El registro de trabajos no responde |

Y los códigos que viajan en el campo `error` de un trabajo `fallido` (son estado del trabajo, no
HTTP): `origen_ausente`, `columna_desconocida`, `formato_no_disponible`, `fallo_interno`.

**Filtros.** `filtros` es un mapa cerrado `{columna: valor}` o `{columna: [valores]}` y se compila a
`pl.col(columna).is_in([...])`, nada más. Una columna que el silo no tiene **no se ignora**: el
trabajo termina `fallido` con `columna_desconocida`.

### Firmas que expone esta ola

```python
# backend/app/services/almacen/__init__.py
class Reloj(Protocol):
    def ahora(self) -> datetime: ...
class RelojDelSistema: ...
class AlmacenDeExportaciones(Protocol):
    async def guardar(self, job_id: UUID, origen: Path, formato: str) -> str: ...
    def url_firmada(self, object_key: str, emitido: datetime) -> tuple[str, datetime]: ...
@runtime_checkable
class AlmacenServidoPorLaApi(Protocol):
    def verificar(self, object_key: str, expira_en: int, firma: str) -> None: ...
    def ruta_de(self, object_key: str) -> Path: ...
class EnlaceCaducado(Exception): ...
class FirmaInvalida(Exception): ...
def derivar_clave_de_firma(jwt_secret_key: str) -> str: ...
def crear_almacen(settings: Settings, reloj: Reloj | None = None) -> AlmacenDeExportaciones: ...

# backend/app/services/almacen/local.py
class AlmacenLocalFirmado:
    def __init__(self, *, clave: str, ttl_horas: int, reloj: Reloj, raiz: Path | None = None) -> None: ...
    async def guardar(self, job_id: UUID, origen: Path, formato: str) -> str: ...
    def url_firmada(self, object_key: str, emitido: datetime) -> tuple[str, datetime]: ...
    def firmar(self, object_key: str, expira_en: datetime) -> str: ...
    def verificar(self, object_key: str, expira_en: int, firma: str) -> None: ...
    def ruta_de(self, object_key: str) -> Path: ...

# backend/app/services/almacen/gcs.py
class AlmacenGCS:
    def __init__(self, *, ttl_horas: int, bucket: str = "karisma-data-exports",
                 prefijo: str = "exports", cliente: _Cliente | None = None) -> None: ...

# backend/app/services/export_service.py
class ExportErrorCode(StrEnum): ...            # los ocho codigos de arriba
class TrabajoNoEncontradoError(Exception): ...
class TrabajosNoDisponiblesError(Exception): ...
class ExportacionFallidaError(Exception):      # lleva .codigo
class Extracto:                                # dataclass: filas, tamano_bytes
class TrabajoRepository(Protocol):             # crear / obtener / listar / marcar_en_proceso
                                               # / marcar_completado / marcar_fallido
class SqlTrabajoRepository: ...
class ExportService:
    def __init__(self, *, repositorio: TrabajoRepository, almacen: AlmacenDeExportaciones,
                 data_dir: Path, ttl_horas: int = 24, retraso_demo: float = 0.0,
                 reloj: Reloj | None = None) -> None: ...
    async def solicitar(self, solicitud: SolicitudExportacion, usuario: UserOut) -> TrabajoDetalle: ...
    async def ejecutar(self, job_id: uuid.UUID) -> None: ...
    async def consultar(self, job_id: uuid.UUID, usuario: UserOut) -> TrabajoDetalle: ...
    async def historial(self, usuario: UserOut, limite: int = 50) -> list[TrabajoResumen]: ...
    async def resolver_descarga(self, job_id: uuid.UUID, expira_en: int, firma: str,
                                usuario: UserOut) -> Path: ...
async def get_export_repository(session) -> TrabajoRepository: ...
async def get_export_service(settings, repositorio) -> ExportService: ...
```

`get_export_service` es la costura que sustituyen las pruebas (y la que sustituiría cualquier suite
futura): nadie dobla el motor de base de datos.

### Decisiones de la ola

1. **El punto de elección quedó verificado por conteo literal.**
   `grep -rn "export_storage_backend" backend/app --include=*.py | wc -l` → **2**: la declaración en
   `config.py` y el `if` de `crear_almacen`. Eso obligó a dos renuncias de redacción que conviene no
   deshacer sin pensarlo: los cuatro ajustes llevan su prosa **debajo del campo** y no en la sección
   `Attributes:` de la clase (nombrar ahí el ajuste habría dado 3), y ni el docstring del módulo
   `almacen` ni el de la factoría escriben el nombre del ajuste. La prueba
   `test_factoria_elige_una_sola_vez` repite ese conteo, así que la regla ya no depende de que
   alguien se acuerde de correr el `grep`.
2. **Una segunda capacidad, `AlmacenServidoPorLaApi`, en vez de un segundo `if`.** El endpoint de
   descarga solo tiene sentido cuando los enlaces los canjea esta API; con GCS los firma y los sirve
   el bucket. El servicio pregunta por la **capacidad** (`isinstance` sobre un `Protocol`
   `runtime_checkable`), no por el backend configurado, así el conteo de arriba sigue en 2 y el
   despliegue en la nube responde 404 en esa ruta en lugar de describir su propia infraestructura.
3. **La clave vacía se deriva, y la derivación es explícita.**
   `derivar_clave_de_firma(jwt_secret_key)` es `HMAC-SHA256(JWT_SECRET_KEY, b"karisma:export:signing-key:v1")`.
   Separación de dominio: quien obtenga la clave de los enlaces no obtiene la que firma los tokens.
   `crear_almacen` es el único que la llama; `AlmacenLocalFirmado` nunca lee ajustes.
4. **La firma se comprueba antes que el vencimiento.** Un enlace que nadie firmó trae un `exp`
   controlado por quien lo escribió: contestar «caducado» sería responder sobre un valor que este
   portal jamás emitió. Firma mala → 403 siempre; firma buena y plazo vencido → 410.
5. **La raíz del almacén local no es un ajuste nuevo.** El plan hablaba de `export_local_dir`, pero
   §4.2 congela **cuatro** ajustes y ninguno más. `AlmacenLocalFirmado` usa
   `tempfile.gettempdir()/karisma-exports` por defecto y acepta `raiz` por constructor (que es lo que
   inyectan las pruebas). No es un atajo: en Cloud Run `/tmp` es la única ruta escribible del
   contenedor y `data/` está montado **de solo lectura** por el compose, así que ninguna otra
   ubicación funcionaría en los dos sitios.
6. **`sink_csv` en hilo de trabajo, no en el bucle.** Todo lo que toca disco o CPU va por
   `asyncio.to_thread`: la extracción, el movimiento del archivo y la subida a GCS. El retraso de
   demostración es `asyncio.sleep`. `test_el_trabajo_no_toma_el_bucle_de_eventos` mide `/health` con
   `ejecutar` en vuelo (`httpx.AsyncClient` + `ASGITransport` + `asyncio.gather`) y además afirma que
   la extracción corrió en un hilo distinto al del bucle: en esta máquina Polars exporta 600 000
   filas en 0,06 s, así que la latencia sola no bastaba para distinguir un fallo real.
7. **Los instantes terminales se truncan al segundo.** El material firmado lleva `exp` en segundos
   enteros; si la fila guardara microsegundos, `expires_at` describiría un plazo que la firma no puede
   expresar. `terminado_en` y `caduca_en` son, por eso, exactos entre sí.
8. **Un registro inalcanzable es 503 `trabajos_no_disponibles`, no un 500.** `_tienda_disponible`
   traduce **solo** `OperationalError` e `InterfaceError` de SQLAlchemy —fallos de conexión, nunca una
   sentencia mal escrita, que debe seguir explotando como el defecto que es—. Esto no es
   decorativo: con `make dev` apagado, `GET /api/export` es la única de las cuatro rutas cuya
   validación no rechaza antes la petición, y la matriz de permisos la interroga con tres roles. Sin
   esta traducción, `permisos/test_permission_matrix.py` (que no es write-set de esta ola) se
   pondría rojo por una excepción de conexión.
9. **`admin` ve metadatos ajenos, nunca el archivo ni el enlace.** `consultar` deja pasar al `admin`
   sobre cualquier trabajo, pero `_a_detalle(..., con_enlace=False)`: sin `url_descarga` y sin
   `caduca_en`. Entregar un enlace que después el propio `resolver_descarga` rechazaría habría sido
   peor que no darlo. `resolver_descarga` es estricta y no admite excepción de gobierno.
10. **`historial` filtra siempre por el llamante**, `admin` incluido. La decisión 6 de planeación
    dice que el `admin` ve el historial completo; eso **no** se implementó y no hay endpoint que lo
    haga (queda anotado abajo). Se prefirió la regla dura —el `WHERE requested_by` no es opcional—
    porque es la fuga más barata de esta US, y está cubierta dos veces: contra el servicio y contra
    el SQL compilado con el dialecto de PostgreSQL. **Cerrado el mismo día**: el `WHERE` sigue
    siendo obligatorio y el `admin` lee por otra sentencia. Ver «Cierre de deudas de O2».
11. **El identificador y el `created_at` los pone Python, no la base.** La respuesta 202 tiene que
    llevar el `job_id` y la tarea de fondo se encola contra él antes de que la transacción sea
    visible; además así el reloj inyectado gobierna también el alta.
12. **`marcar_en_proceso` es un compare-and-set.** Solo mueve `pendiente → en_proceso`; si el trabajo
    ya no está pendiente devuelve `None` y `ejecutar` se retira. Un doble encolado —doble clic, un
    redespliegue— no vuelve a correr una extracción terminada ni mueve el plazo de un enlace que
    alguien ya tiene.

### Degradación declarada: XLSX — retirada el mismo día

Mientras duró, un trabajo con `formato: "xlsx"` terminaba **`fallido` con
`error_code = "formato_no_disponible"`** porque `xlsxwriter` no estaba instalado y esta ola tenía
prohibido añadirlo. **Ya no**: la dependencia entró, XLSX escribe una hoja real y el código de error
quedó como red de seguridad de un entorno sin escritor. La medición que obligó a poner un tope de
filas, las pruebas y el pin exacto están en «Cierre de deudas de O2», al final de este documento.

### Verificación ejecutada

- `ruff check` y `ruff format --check` con `--config backend/pyproject.toml` sobre `backend ml
  scripts tests` → limpios (109 archivos formateados).
- `mypy --config-file backend/pyproject.toml --exclude '^tests/ml/' backend/app scripts tests` →
  **Success: no issues found in 84 source files**. El error preexistente de
  `services/user_service.py:83` que anotaba O1 ya no está: US-018 lo cerró.
- `pytest -c backend/pyproject.toml tests/backend/test_export_{endpoint,almacen_firmado,estado_scopes}.py`
  → **40 passed**.
- `pytest -c backend/pyproject.toml tests/backend` → **633 passed, 17 skipped, 0 failed**, cobertura
  combinada **71,63 %** (el mínimo es 70). Las dos fallas que O1 dejó anotadas ya no existen.
- `pytest -c backend/pyproject.toml tests/backend tests/ml` (lo que corre `make test`) → **690
  passed, 17 skipped**, cobertura **97,80 %**.
- Cobertura de los módulos de la ola: `api/export.py` **100 %**, `services/export_service.py`
  **99 %**, `almacen/__init__.py` **100 %**, `almacen/local.py` **98 %**, `almacen/gcs.py` **95 %**.
  **No se usó ni un `# pragma: no cover`.** Lo único descubierto de `gcs.py` es la construcción
  perezosa del cliente real, que exige el SDK ausente.
- `scripts/verificar_permisos_ui.sh` → «Mapa de permisos en verde». `permisos.generated.ts` **no
  cambia** con estas filas: su `MAPA_RAMA_ENDPOINTS` declara dos endpoints de exportación y el scope
  resultante sigue siendo `analista`.
- `docs/security.md` regenerado con el comando del plan; `permisos/test_security_doc.py` en verde.

### Qué quedó desactualizado en `backend/AGENTS.md` (sección «Estado»)

No lo toqué —está fuera de mi write-set— pero quien edite esa guía debe corregir cuatro cosas, y las
tres primeras ya eran falsas antes de esta ola por US-018 y US-023:

1. «**Cinco** routers montados en `create_app()`» → hoy son **ocho**: health, auth, catalog, lineage,
   metrics, users, chat y export.
2. La lista «**No existen todavía**… `/api/export`, `/api/export/{job_id}`… el CRUD `/api/users` y
   `/api/chat`» y la frase «Tampoco hay `export_service`, `chat_service`…» son falsas: existen los
   cuatro verbos de `/api/export` (dos de ellos, `GET /api/export` y
   `GET /api/export/{job_id}/download`, ni siquiera estaban previstos en esa lista) y existe
   `services/export_service.py`.
3. El árbol de «Estructura» necesita: `api/ … · export`, `services/ … · export_service` **más el
   subpaquete `almacen/`** (es el primer subdirectorio de `services/`, y la convención del sufijo
   `_service` no le aplica: es una fachada de infraestructura, no un servicio de dominio), y
   `models/ … · export`.
4. La línea «❌ Trabajo pesado dentro del request: la exportación va a `BackgroundTasks` con `job_id`
   inmediato» ya no describe un plan sino algo implementado; conviene que apunte a
   `services/export_service.py` como ejemplo vivo.

### Pendientes que esta ola deja abiertos

- **P-10 — El bucket de GCS es una constante de módulo, no un ajuste.** `_BUCKET_POR_DEFECTO =
  "karisma-data-exports"` vive en `gcs.py` porque §4.2 congela cuatro ajustes y un quinto habría
  hecho falsa esa declaración. El día que Terraform cree el bucket, ese literal debe volverse ajuste
  con el mismo valor por defecto.
- **P-11 — La tarea de fondo retiene la sesión de base del request.** `BackgroundTasks` corre dentro
  del `AsyncExitStack` de la petición, así que la sesión sigue viva durante toda la exportación
  (8–15 s en el trabajo objetivo). Es correcto y es el precio de la decisión 9 de planeación
  (`BackgroundTasks` sin Celery ni Redis); si alguna vez hay concurrencia real, la tarea debería
  abrir su propia sesión.
- **P-12 — Nadie borra los archivos producidos.** Viven en el directorio temporal hasta que el
  sistema lo limpie. Es el recorte #3 (política de ciclo de vida del bucket), declarado fuera de
  alcance.
- **P-14 — `AlmacenGCS` no se ha ejecutado nunca.** Está cubierto por dobles en lo único verificable
  sin proyecto (la construcción de los argumentos de la firma V4). Su primera ejecución real será
  también su primera prueba real.
- **P-6, P-4 y P-9 quedan cerrados** por O1 y por esta ola. P-1, P-2, P-7 y P-8 no eran de backend y
  quedaron abiertos al terminarla; **los cerró la integración el mismo día** — ver el cierre al final
  del documento.
- **P-13 y la degradación de XLSX ya no son pendientes**: se cerraron el mismo 13-ago-2026, con
  código y pruebas, en «Cierre de deudas de O2» al final de este documento.
---

## O3 — frontend (ejecutada)

**Fecha**: jue 13-ago-2026 · **SHA base**: `a251652` (rama `us-018`, árbol compartido con US-018 y
US-023 en vuelo) · **Estado de la ola**: completa. Typecheck, eslint y pruebas en verde.

### Archivos escritos

| Ruta | Acción | Nota |
|---|---|---|
| `frontend/app/types/exportacion.ts` | creado | Espejo del contrato de cable de O1/O2. Nombres en español (`job_id`, `tamano_bytes`, `solicitado_en`); `TrabajoDetalle` hereda de `TrabajoResumen` y añade `url_descarga` y `caduca_en`; `TrabajoVigilado` añade lo único que el cliente sabe y el servidor no: `caducadoEnCliente`. `object_key` no aparece |
| `frontend/app/stores/exportaciones.ts` | creado | Store Pinia: historial, **un solo temporizador** de 3 000 ms, `momento` derivado, `esTerminal` y `falloDeExportacion` |
| `frontend/app/composables/useExportaciones.ts` | creado | Fachada del store + reglas de lectura: `analizarFiltros`, `claveDeFallo`, `claveDeErrorDeTrabajo`, `haCaducado`, `momentoDeConsulta`, `retrasoDeDemostracion`, `useFormatoExportaciones` |
| `frontend/app/plugins/exportaciones.client.ts` | **creado — write-set ampliado** | Engancha el ciclo de vida del sondeo al arranque de la aplicación. Ver «Dónde quedó enganchado» |
| `frontend/app/components/exportacion/FormularioExportacion.vue` | creado | Momento 1 |
| `frontend/app/components/exportacion/TarjetaTrabajo.vue` | creado | Momentos 2 y 3, una tarjeta por `job_id` |
| `frontend/app/components/exportacion/HistorialExportaciones.vue` | creado | Lista con sus cuatro estados; delega cada fila en `TarjetaTrabajo` |
| `frontend/app/pages/exploracion/exportar.vue` | reescrito | Sustituye el andamiaje `EstadoPendiente` |
| `frontend/i18n/locales/es.json` · `en.json` | modificados | **Solo** el subárbol `export.*` (44 hojas), la reescritura de `screen.exports.description` y el borrado de `screen.exports.capability.*` |
| `frontend/test/exportaciones.spec.ts` | creado | 15 casos: T-16, T-17, T-18, T-20 y cuatro comportamientos más, todos con su defecto escrito |
| `frontend/test/pantallas.spec.ts` | modificado | **Una línea**: `'/exploracion/exportar'` añadido al arreglo del filtro. Ninguna prueba borrada |

Nada más se tocó. `navegacion.ts`, `tokens.generated.ts`, `permisos.generated.ts`, `nuxt.config.ts`,
`app/layouts/`, `backend/`, `db/` y `ml/` siguen intactos. `backend/app/models/export.py` y
`backend/app/api/export.py` se leyeron sin escribir.

### Dónde quedó enganchado el ciclo de vida del sondeo

En un **plugin de cliente nuevo**, `frontend/app/plugins/exportaciones.client.ts`, y **no** en
`app/layouts/portal.vue`. Razón: `frontend/AGENTS.md` no manda que esto viva en el layout —su
«Estructura» ni siquiera menciona `app/plugins/`, que no existía—, y `portal.vue` lo comparten las US
en vuelo esta semana. Crear la carpeta es aditivo y no colisiona con nadie. **El write-set queda
ampliado con ese archivo**, que es el único fuera de la lista del §3 del plan.

El plugin hace una sola cosa: crea el store al arrancar y llama a `observarVisibilidad()`. Lo que
hace que el sondeo sobreviva al cambio de ruta no es el plugin sino dónde vive el temporizador —en el
store, no en la página—; el plugin garantiza que la pausa por pestaña oculta rija desde cualquier
pantalla y no solo desde la que lanzó el trabajo.

**No hay desmontaje**, y es una decisión, no un olvido: el runtime de Nuxt **no publica un hook
`app:unmount`** (`app:mounted`, `app:error`, `page:finish`… sí; ese no — lo confirmó `nuxt typecheck`
con `TS2345` sobre `HookKeys<RuntimeNuxtHooks>`). Lo único que termina esta aplicación es que el
documento se vaya, y eso se lleva por delante el temporizador y el oyente. El par
`detenerSondeo()` / `olvidarVisibilidad()` sigue en la superficie del store para quien lo cree fuera
de una pestaña, que hoy es la suite: `exportaciones.spec.ts` los llama en su `afterEach` porque
happy-dom comparte un `document` entre las pruebas de un archivo y un store que siguiera oyendo
reanudaría su sondeo con el `$fetch` de otra prueba.

### Claves i18n añadidas de más (todas dentro de `export.*`)

El §3.1 enumera 24 hojas; se escribieron **44**. Las 20 adicionales, con su motivo:

| Clave | Por qué |
|---|---|
| `export.form.filtersHint` | El campo de filtros necesita decir su sintaxis (`columna=valor`, comas, punto y coma); el ejemplo vive dentro de la frase |
| `export.form.filtersInvalid` | Un texto que el backend contestaría con 422 se rechaza donde el lector lo puede arreglar |
| `export.form.sending` | Estado del botón mientras la petición va en el cable |
| `export.dataset.{creditos,liquidez,derivados}` | El `<select>` ofrece los tres conjuntos exportables; sin estas hojas la opción se rotularía con el identificador del cable |
| `export.format.{csv,xlsx}` | Rótulo de cada opción del formato (`export.form.format` es el rótulo del campo, no de las opciones) |
| `export.format.xlsxUnavailable` | La degradación declarada de XLSX, escrita al lado de la opción deshabilitada |
| `export.job.stalled` | El trabajo que el portal deja de vigilar: tope de 200 sondeos, o un 404 durante el sondeo |
| `export.job.error.{missingSource,unknownColumn,formatUnavailable,internalFailure}` | Los cuatro códigos que viajan en el campo `error` de un trabajo `fallido`. Hojas en inglés y tabla de traducción en el composable: los códigos del cable son `origen_ausente`, `columna_desconocida`, `formato_no_disponible`, `fallo_interno`, y meterlos como hoja habría roto la convención de clave jerárquica en inglés |
| `export.history.{error,retry}` | Estado de error del historial y su acción de reintento |
| `export.moment.{pinned,empty}` | Aviso de vista fijada para captura, y el vacío explícito cuando el momento fijado no tiene trabajo real detrás |
| `export.error.{unavailable,generic}` | El 503 `trabajos_no_disponibles` y el cuerpo sin código nuestro (500, red caída, proxy que contestó HTML). Sin `generic`, un fallo desconocido imprimiría un identificador del backend al lector |

**Una hoja se escribió y se retiró**: `export.form.filtersPlaceholder`. El ejemplo de sintaxis es la
misma cadena en los dos idiomas, y `idioma.spec.ts` («solo lo intraducible coincide en los dos
idiomas») solo tolera `brand.name` y `error.code`. El ejemplo se mudó dentro de `filtersHint`, que sí
se traduce, y el campo se quedó sin `placeholder`. Por el mismo motivo `export.format.xlsx` es «Hoja
de Excel (XLSX)» / «Excel workbook (XLSX)» y no la misma cadena; `export.format.csv` («CSV») pasa
porque la prueba exime a los identificadores en mayúsculas.

Fuera de `export.*` se tocó exactamente lo declarado: `screen.exports.description` reescrita y las
cuatro `screen.exports.capability.*` borradas.
`grep -rn "screen.exports.capability" frontend/` → **0**. `chat.*` no se tocó, nada se reordenó y los
dos catálogos se releyeron justo antes de editarlos (US-023 ya había dejado `chat.*` y US-018
`admin.*` en el árbol; ambos siguen intactos).

### Decisiones de la ola

1. **El predicado terminal se escribe una vez**, en `stores/exportaciones.ts`, espejo de
   `EstadoTrabajo.es_terminal`. El composable **no lo reexporta**: hacerlo provocaba
   `WARN Duplicated imports "esTerminal"` en cada build, porque Nuxt auto-importa `composables/` y
   `stores/` a la vez. `TarjetaTrabajo.vue` lo importa del store, que es el único módulo que lo
   define. Las otras comparaciones con `'completado'` que quedan en el árbol no son terminalidad:
   son la pregunta distinta de si hay enlace que ofrecer.
2. **`momento` es derivado y nada lo puede fijar**: `proceso` si hay algún trabajo vivo, `enlace` si
   el más reciente está `completado`, `solicitud` en cualquier otro caso. `?momento=` escribe
   `momentoFijado`, que solo **congela qué momento se pinta**; el trabajo expandido lo sigue
   decidiendo `trabajoDeMomento()` sobre trabajos reales. Con historial vacío y `?momento=enlace` la
   pantalla dibuja `export.moment.empty` y **no existe ningún nodo `[data-accion="descargar"]` en el
   DOM**: no es un enlace oculto, es un enlace que no se construye.
3. **La expansión se sigue sola hasta que el lector interviene.** Un `let manual` (no reactivo)
   apaga el seguimiento en cuanto se pulsa una tarjeta, y `fijarMomento` y `solicitar` lo reponen.
   Sin él, la fila que el lector acaba de abrir se cerraría en el siguiente sondeo que mueva el
   estado.
4. **La franja de honestidad se lee de `runtimeConfig.public.exportDemoDelay`.** El retraso es un
   ajuste del backend (`EXPORT_DEMO_DELAY_SECONDS`) y **los cuatro endpoints del contrato no lo
   publican**; derivarlo del tiempo que tarda un trabajo sería mentir en la propia franja, porque el
   trabajo objetivo tarda 8–15 s por sí mismo. Ausente se lee **0**, y 0 esconde la franja: anunciar
   un estiramiento que no ocurre es justo lo que la franja existe para impedir. La línea de
   `nuxt.config.ts` que faltaba (**P-15**) la escribió el orquestador al integrar: ya está cerrada.
5. **Dos formas de cuerpo de error, una sola función.** `falloDeExportacion` devuelve
   `{estado, codigo}`: lee `detail.codigo` solo cuando `detail` es objeto, y valida el código contra
   los cuatro de `ExportErrorCode`. Un `detail` de cadena suelta (401/403 de US-015) da
   `codigo: null` y cae en `export.error.generic` en vez de imprimir `[object Object]`. El 401 tiene
   su propia rama: apaga el sondeo y sale por `expirarSesion()` de US-017.
6. **Un 404 durante el sondeo también retira el trabajo de la vigilancia.** Un trabajo que el
   servidor ya no reconoce no va a empezar a reconocerlo, y sin esta rama el temporizador seguiría
   preguntando hasta que se cierre la pestaña — la misma fuga que cierra el tope de 200 sondeos.
7. **`url_descarga` se usa tal cual.** Es ruta relativa y viaja al `href` sin prefijo ni reescritura;
   la prueba compara el `href` con la cadena exacta que el servidor emitió.
8. **`solicitar` devuelve `Promise<string | null>`**, no `Promise<string>` como decía el §4.7: `null`
   es «la petición fue rechazada y el fallo ya está en `fallo`», que es lo que la pantalla necesita
   para no navegar sobre un identificador que no existe.
9. **El historial no se recarga tras cada sondeo.** `GET /api/export` devuelve `TrabajoResumen` (sin
   enlace) y el sondeo devuelve `TrabajoDetalle`; `trabajos` es la mezcla, con el detalle encima del
   resumen. Un trabajo que terminó con la pestaña cerrada no trae enlace hasta que se le pregunta por
   id, y eso se hace **una sola vez por trabajo** (`detallesPedidos`), que es lo que impide que el
   observador se realimente cuando la respuesta tampoco trae enlace.
10. **XLSX se ofrece deshabilitado y con su explicación al lado**, con `csv` preseleccionado. Ni se
    esconde (borraría una degradación declarada) ni se ofrece como si funcionara (gastaría el tiempo
    del lector en un trabajo que solo puede acabar `fallido`).
11. **Los nombres de icono son literales en cada rama** (`v-if`/`v-else` en vez de un ternario en
    `:name`), como ya hacía `acceso/FormularioAcceso.vue`: el escáner del módulo de iconos lee las
    fuentes como texto y un nombre montado en tiempo de ejecución se publica como caja vacía.
12. **Accesibilidad**: `aria-expanded` + `aria-controls` en el disparador de cada tarjeta,
    `role="progressbar"` con etiqueta traducida en la barra indeterminada, `role="alert"` en los
    fallos y `role="status"` en los avisos, `aria-busy` en el formulario y en el esqueleto,
    `ANILLO_FOCO` en todo control, y un solo `<h1>` en la pantalla (`h2` en el historial, `h3` por
    tarjeta).

### Verificación ejecutada

- `pnpm --dir frontend typecheck` → limpio, y sin el `WARN Duplicated imports` que aparecía antes de
  la decisión 1.
- `pnpm --dir frontend exec eslint` sobre los once archivos del write-set → **0 errores** (los dos
  `.json` de locales quedan fuera de la configuración de eslint, que es como estaban antes).
- `pnpm --dir frontend vitest run test/exportaciones.spec.ts test/pantallas.spec.ts` → **48 passed**
  (15 nuevos + 33 de pantallas).
- Añadidos por afectar directamente a lo que esta ola escribió:
  `vitest run test/contratos.spec.ts test/idioma.spec.ts` → **11 passed**. Son los que fijan que toda
  clave literal resuelva en los dos catálogos, que las claves de `es` y `en` sean el mismo conjunto y
  que ninguna clase de token nombre algo que el `@theme` no declare. **No se escribió una prueba de
  paridad `es`/`en` propia**: T-19 se retiró en §6 por duplicar exactamente esa señal.
- **No se corrió la suite completa del proyecto** (instrucción de la ola). En verde quedan los cuatro
  archivos de arriba: 59 casos.

### Qué quedó desactualizado en `frontend/AGENTS.md` (sección «Estado» y «Estructura»)

No lo toqué —está fuera de mi write-set— pero quien edite esa guía debe corregir seis cosas, y dos ya
eran falsas antes de esta ola por US-018:

1. «**Pendientes**: `/administracion`, `/exploracion` y `/exploracion/exportar` montan
   `comun/EstadoPendiente.vue`» → `/exploracion/exportar` ya no lo monta (esta ola) y
   `/administracion` tampoco (US-018). **La única pantalla de andamiaje que queda es `/exploracion`**,
   y eso es exactamente lo que hoy dice el filtro de `test/pantallas.spec.ts`.
2. «**Construidas**: …» debe sumar `/exploracion/exportar`, con lo que la caracteriza:
   sondeo de 3 000 ms en Pinia y enlace firmado relativo.
3. «También existen 14 composables, dos stores Pinia (`workspace`, `sistemaDiseno`)» → hoy son **16
   composables** y **tres stores**: `exportaciones` es el tercero, y es el primero que posee un
   temporizador.
4. El árbol de «Estructura» **no menciona `app/plugins/`**, que ahora existe con un solo archivo. Es
   el sitio donde arranca el ciclo de vida del sondeo, así que conviene que la guía lo nombre antes de
   que la siguiente US lo busque en `layouts/`.
5. «`components/` — **diez familias**» → son **doce** contando `administracion/` (US-018) y
   `exportacion/` (esta ola).
6. «En `frontend/test/`: **34** `*.spec.ts`» → son **38**.

### Pendientes que esta ola deja abiertos

- **P-15 — CERRADO al integrar (jue 13-ago-2026).** La clave
  `exportDemoDelay: Number(process.env.NUXT_PUBLIC_EXPORT_DEMO_DELAY ?? 0)` ya está declarada en
  `runtimeConfig.public` de `frontend/nuxt.config.ts`, con el comentario que explica por qué el valor
  no puede leerse del backend. La escribió el orquestador al integrar, no esta ola: el archivo lo
  comparten las US en vuelo y quedaba fuera de su write-set. Nuxt solo expone las claves declaradas y
  `NUXT_PUBLIC_*` únicamente sobrescribe las existentes, así que sin esa línea la franja no encendía.
  El valor debe seguir coincidiendo con `EXPORT_DEMO_DELAY_SECONDS` del backend. **Desbloquea P-7.**
- **P-16 y P-17 quedan cerrados**, no diferidos: ver «Cierre de deudas de O3» al final de este
  documento.
- **P-7** (las tres capturas de A4) ya no depende de nada: P-15 está cerrado. **P-1 queda cerrado en su
  mitad de frontend**: `frontend/AGENTS.md` se leyó al abrir esta ola y no contradice §A-3 —el sondeo
  en Pinia es justo lo que su línea «Pinia guarda decisiones, nunca los puntos» permite—, aunque su
  «Estado» sí quedó desactualizado, como queda anotado arriba.

### Cierre de deudas de O3

**Fecha**: jue 13-ago-2026 · Write-set: `frontend/app/stores/exportaciones.ts`,
`frontend/app/composables/useExportaciones.ts`,
`frontend/app/components/exportacion/TarjetaTrabajo.vue` y `frontend/test/exportaciones.spec.ts`.
Nada más se tocó: `HistorialExportaciones.vue` no hizo falta, y `nuxt.config.ts`, los locales,
`navegacion.ts` y los `*.generated.ts` siguen intactos. **No se añadió ninguna hoja de i18n**: las
dos deudas se cierran con claves que ya existían (`export.link.expired`).

**P-16 — el enlace se retira solo en el instante en que caduca.** La objeción anotada («pediría un
segundo temporizador») valía para un **sondeo** periódico, no para un vencimiento: el instante exacto
ya viaja en `caduca_en`, así que basta un **disparo único** armado para ese instante. Vive en el
composable nuevo `useCaducidadDeEnlace(caducaEn)`, que devuelve el veredicto como `ComputedRef` y no
como una comparación hecha en el render; `TarjetaTrabajo` ya no llama a `haCaducado` —que sigue
existiendo como el predicado puro que el composable usa— sino que lee ese `computed`. **Cero
peticiones**: la caducidad se aprende del plazo que la firma ya llevaba dentro, y el backend sigue
siendo la autoridad (410 `enlace_caducado`) para quien traiga un enlace vencido. Un temporizador por
tarjeta visible, cancelado con `onScopeDispose` y **re-armado** por `watch` cuando `caduca_en` cambia
—un trabajo sin enlace lo trae en `null` y el sondeo lo rellena al terminar—.

Un detalle que costó un fallo real y conviene no deshacer: el disparo **se vuelve a armar** en lugar
de declarar muerto el enlace al saltar. Un retraso de `setTimeout` se guarda en 32 bits, así que
cualquier plazo mayor a ~24 días dispara **de inmediato**; con el `caduca_en` de diciembre que usa la
suite, la primera versión marcaba caducado un enlace vivo y tiró dos pruebas que ya estaban en verde.
Al saltar se relee el reloj y, si el plazo sigue por delante, se cubre el resto. Lo mismo protege del
disparo que se adelanta un milisegundo.

**P-17 — el historial se relee cuando un trabajo alcanza estado terminal.** Una sola relectura **por
transición**, nunca por sondeo. El store guarda `terminales: Set<string>`, sembrado por cada lectura
del historial **y** por cada detalle; `consultar` compara antes de guardar y solo entonces llama a
`releerHistorial()`, que es silenciosa: si la relectura falla, las filas en pantalla se quedan como
estaban en vez de convertirse en un banner de error, porque son lo último que el servidor dijo de
verdad (el 401 sigue siendo la excepción y sale por `expirarSesion()`). La siembra es lo que impide
la relectura inútil del caso más común: un trabajo que **ya** estaba terminado cuando el historial lo
trajo no ha transitado a nada, así que pedir su enlace firmado no vuelve a poner la lista en el
cable. `releerHistorial` termina en `iniciarSondeo()`: si la otra pestaña dejó un trabajo vivo, esta
pasa a vigilarlo también. No duplica filas ni reordena: `resumenes` se sustituye entero con lo que
mandó el servidor y la mezcla con `detalles` es la de siempre.

**Pruebas** (`frontend/test/exportaciones.spec.ts`, de 15 casos a **19**):

| Caso | Defecto que lo hace fallar |
|---|---|
| `retira la descarga en el instante exacto de la caducidad, sin recargar` | Con reloj falso, se avanza más allá de `caduca_en`: desaparece `[data-accion="descargar"]` y aparece `[data-aviso="caducado"]` con el texto de `export.link.expired`. Afirma además **0 peticiones** de detalle |
| `no deja el disparo de caducidad vivo tras desmontar la pantalla` | `vi.getTimerCount()` baja a **0** al desmontar: ningún temporizador sobrevive a su componente |
| `trae el trabajo que otra pestana pidio, sin recargar la pantalla` | El historial crece durante el sondeo; hasta la transición a terminal hay **1** llamada a la lista y el trabajo ajeno no existe, después hay **2** y aparece, en su orden y sin duplicarse. Cinco intervalos más → **ninguna** relectura extra |
| `no relee por un trabajo que ya conocia terminado` | Abrir la pantalla con una exportación vieja pide su enlace una vez y deja la lista en **1** llamada |

**T-17 sigue midiendo lo que decía** —tres avances de 3 s, exactamente 3 llamadas al detalle— y ahora
además afirma `llamadas.lista === 0`: es la prueba que impide que alguien «arregle» P-17 releyendo el
historial en cada ronda. Las dos deudas se verificaron por mutación: anulando el re-armado del
disparo y la llamada a `releerHistorial`, fallan exactamente los dos casos nuevos y ningún otro.

**Verificación**: `pnpm --dir frontend typecheck` limpio · eslint sobre los cuatro archivos, 0
errores · `vitest run test/exportaciones.spec.ts test/pantallas.spec.ts test/idioma.spec.ts
test/contratos.spec.ts` → **63 passed** (19 + 33 + 9 + 2). No se corrió la suite completa del
proyecto, por instrucción.

---

### Cierre de deudas de O2

**Fecha**: jue 13-ago-2026, después de O3 · **Write-set**: `services/export_service.py`,
`api/export.py`, `backend/pyproject.toml`, `poetry.lock`, `tests/backend/test_export_endpoint.py`,
`tests/backend/test_export_estado_scopes.py`. Nada más se tocó: ni `models/export.py`, ni `core/`,
ni `main.py`, ni `docs/security.md`, ni `frontend/`, `db/` o `ml/`. Los scopes y las cuatro filas de
la matriz siguen igual —`admin` ya alcanzaba `analista` por jerarquía—, así que
`permisos.generated.ts` y `docs/security.md` no cambian.

#### P-13 — el `admin` ya ve el registro completo

- **`TrabajoRepository.listar_todos(*, limite)`**, con su implementación SQL. Es un método aparte y
  no un argumento opcional de `listar`: el `WHERE requested_by` sigue siendo obligatorio y ahora es
  imposible perderlo por dejar un parámetro sin poner. `listar_todos` es la **única** sentencia del
  módulo sin filtro de propietario, y su único llamante es la rama de gobierno de `historial`.
- **`ExportService.historial`** bifurca por `usuario.role is Scope.ADMIN` y deja traza
  (`export.historial.gobierno` con el id del llamante y el **número** de trabajos, nunca el dataset
  ni los filtros de otro).
- **`resolver_descarga` no se tocó**: sigue exigiendo propiedad estricta, sin excepción de gobierno.
  Un `admin` ve el metadato del trabajo ajeno y sigue recibiendo 404 al pedir su archivo.
- **El dueño viaja en el contrato, y el modelo no se tocó.** `GET /api/export` responde ahora
  `TrabajoResumenAtribuido[]`: es `TrabajoResumen` **más un campo**, `solicitado_por` (el `uuid` de
  `app_user`, el mismo identificador que cada quien ya lee de sí en `/api/auth/me`; ni correo ni
  nombre). La clase vive en `services/export_service.py` y **no** en `models/export.py` porque ese
  archivo no es write-set de este cierre; es una subclase de una línea, así que mudarla el día que
  alguien tenga ese archivo abierto es cambiar un `import`. Se rellena para **todos** los roles: a
  quien no es `admin` el filtro solo le devuelve lo suyo, de modo que el valor es su propio id y no
  añade información, y la interfaz recibe una sola forma de lista en vez de dos.
- **Sigue sin haber enlace**: `TrabajoResumen` no tiene `url_descarga` ni `caduca_en`, que es la
  misma regla que `consultar` aplica con `_a_detalle(..., con_enlace=False)`.

| Prueba | Defecto que atrapa |
|---|---|
| `test_historial_no_filtra_trabajos_ajenos` | El `SELECT` sin su `WHERE requested_by`: la fuga más barata de la US. **Regresión intacta** |
| `test_el_historial_sql_filtra_por_propietario_y_ordena` | La misma fuga, leída sobre el SQL compilado con el dialecto de PostgreSQL |
| `test_el_historial_de_un_admin_es_el_registro_completo` | El historial filtrando por el llamante para todo rol —lo que hacía O2—: el único rol que audita sería el único que no puede |
| `test_el_historial_de_un_admin_no_reparte_enlaces` | Un historial que respondiera con el contrato del sondeo: repartiría enlaces firmados de archivos ajenos |
| `test_el_historial_de_gobierno_sql_no_lleva_filtro_y_sigue_acotado` | Una sentencia de gobierno con filtro, o sin `ORDER BY`/`LIMIT` sobre una tabla que crece |
| `test_el_historial_de_gobierno_viaja_sin_enlaces` (scopes) | Lo mismo sobre el cable y no sobre los objetos: quien decide qué campos existen es `response_model` |
| `test_un_registro_inalcanzable_se_publica_como_503[historial_de_gobierno]` | La rama nueva sin la traducción de `_tienda_disponible`: 500 con traza donde la pantalla tiene vacío diseñado |

#### XLSX — funcionando, con un tope medido

- **Dependencia**: `poetry -P backend add "polars[xlsxwriter]==1.43.2"`. En `pyproject.toml` el pin
  exacto se conserva —`"polars[xlsxwriter] (==1.43.2)"`, solo cambió el extra— y el `poetry.lock`
  fija **`xlsxwriter 3.2.9`** en el grupo `main` con sus dos hashes. No se aflojó ningún rango.
- **`_escribir_xlsx` devuelve el conteo** y ordena el trabajo al revés que antes: cuenta sobre el
  plan (`select(pl.len())`), decide, y solo entonces materializa. El `collect()` sigue corriendo en
  hilo de trabajo, como todo lo pesado.
- **Tope: 200 000 filas.** No es el límite del formato (una hoja aguanta 1 048 576) sino el límite
  que este servicio puede sostener sin incumplir el gate de `/health` < 500 ms. Medido sobre
  `liquidez` (once columnas), escribiendo desde un hilo de trabajo con un vigilante asyncio midiendo
  cuánto tardaba en despertar el bucle:

  | Filas | `write_excel` | Peor retraso del bucle | Pico de memoria |
  |---|---|---|---|
  | 100 000 | 6,1 s | 112 ms | — |
  | **200 000** | **12,1 s** | **198 ms** | **707 MB** |
  | 300 000 | 18,1 s | 381 ms | 1 230 MB |
  | 500 000 | 31,0 s | 505 ms | 1 780 MB |
  | 1 000 000 | 61,6 s | **997 ms** | — |

  O sea: **el volumen objetivo del plan —el millón de filas de `liquidez`— no puede cumplir el gate
  en XLSX**: 61,6 s de escritura y 997 ms de bloqueo del bucle, contra 500 ms. `xlsxwriter` es Python
  puro y recupera el GIL a rodajas aunque corra en otro hilo, así que el hilo de trabajo no basta por
  sí solo. 200 000 deja 2,5× de margen y además exporta enteros `creditos` (180 000 filas) y
  `derivados` (80 000): la única fuente que recorta es la que no cabe en una hoja de cálculo. **CSV no
  lleva tope**, porque `sink_csv` no materializa.
- **El código de error del tope es `formato_no_disponible`, el mismo de la red de seguridad**, y es
  una renuncia consciente: la interfaz mapea todo código que no conoce a `internalFailure`
  (`claveDeErrorDeTrabajo`, en `useExportaciones.ts`), así que un código propio y preciso se leería como «fallo interno», que
  es justo lo que no es. Los dos casos se distinguen en el log
  (`export.extraccion.sin_escritor_xlsx` frente a `export.extraccion.xlsx_excede_el_limite`, este con
  `filas` y `maximo`). **Consecuencia para quien tenga `frontend/` en su write-set** (aquí no lo
  estaba): `export.format.xlsxUnavailable` y la opción deshabilitada del formulario describen un
  portal que ya no existe, y la copia de `formatUnavailable` debería nombrar el tope de filas.

| Prueba | Defecto que atrapa |
|---|---|
| `test_un_trabajo_xlsx_deja_una_hoja_de_calculo_legible` | Dar por bueno el formato porque el módulo importa. Abre el archivo como zip OOXML y cuenta las filas de `sheet1.xml`: 2 000 datos + 1 de encabezado |
| `test_la_hoja_de_calculo_no_toma_el_bucle_de_eventos` | El `collect()` + `write_excel` dejados en el bucle. Sondea `/health` con una hoja de 50 000 filas en vuelo: exige < 500 ms **y** que la respuesta llegue antes de la mitad del trabajo, que es lo que ninguna máquina rápida puede volver ambiguo |
| `test_una_hoja_por_encima_del_limite_no_se_materializa` | Contar después de materializar. Espía cada `collect()` de la corrida y exige que el único que ocurra sea el del conteo (altura 1); si no, el millón de filas se cargaría en memoria para después rechazarlo |
| `test_sin_escritor_de_xlsx_el_trabajo_falla_con_codigo` | Quitar la guardia ahora que la dependencia está declarada: el `ImportError` saldría dentro de la tarea de fondo, con el 202 ya contestado. Ya no se salta sola —el `skipif` desapareció—: oculta el paquete en el único sitio donde el código pregunta por él |

#### Verificación ejecutada

- `ruff check` y `ruff format --check` con `--config backend/pyproject.toml` sobre los cuatro
  archivos → limpios.
- `mypy --config-file backend/pyproject.toml --exclude '^tests/ml/' backend/app scripts tests` →
  **Success: no issues found in 85 source files**.
- `pytest -c backend/pyproject.toml tests/backend/test_export_{endpoint,almacen_firmado,estado_scopes,job_migracion}.py`
  → **70 passed**, repartidos 26 + 7 + 23 + 14 por archivo. Son **ocho casos más** que antes de este
  cierre, y **cero omitidos**: el `skipif` de XLSX ya no existe.
- `pytest -c backend/pyproject.toml tests/backend/permisos/test_permission_matrix.py` → **107 passed**.
- Cobertura de los módulos tocados: `api/export.py` **100 %**, `services/export_service.py` **98 %**
  (sin descubrir nada nuevo: las cuatro líneas son la guardia de `_a_resumen` y los dos `return` de
  las factorías de dependencias, que ya estaban así).
- **Cada prueba nueva se vio fallar.** Cinco defectos inyectados de uno en uno sobre el servicio, con
  la suite de exportación como juez: historial filtrando siempre (**3 fallos**), XLSX materializando
  antes de contar (**1**), guardia del escritor retirada (**1**), extracción devuelta al bucle
  (**2**), sentencia de gobierno con filtro (**1**). Ninguna prueba nueva es de las que no pueden
  fallar.

#### Lo que este cierre **no** hace

- No toca `models/export.py`: por eso `TrabajoResumenAtribuido` vive junto al servicio.
- No añade `solicitado_por` a `TrabajoDetalle`: el sondeo es la vista del dueño y el gobierno se lee
  en la lista, que ya dice de quién es cada trabajo.
- No arregla la copia del frontend sobre XLSX ni el `<select>` deshabilitado: está fuera del
  write-set y queda anotado arriba para quien lo tenga.
- P-10, P-11, P-12 y P-14 siguen abiertos tal como O2 los dejó.

### Ajuste de la interfaz al XLSX real

**Fecha**: jue 13-ago-2026, después del cierre de O2 · **Write-set**:
`frontend/app/components/exportacion/FormularioExportacion.vue`, `frontend/i18n/locales/{es,en}.json`
(solo el subárbol `export.*`) y `frontend/test/exportaciones.spec.ts`. Nada más: ni el composable, ni
la tienda, ni la página.

- **La opción XLSX deja de estar deshabilitada.** El control del formato no es un `<select>` sino un
  grupo de radios, y ese radio ya solo se apaga mientras hay una solicitud en vuelo
  (`:disabled="enviando"`); la etiqueta perdió además el gris de formato inalcanzable. `csv` sigue
  preseleccionado, ahora por ser el formato **sin tope** y no por ser el único que termina. El
  formulario no valida el tope: la altura del extracto es propiedad del conjunto y solo el backend la
  conoce, así que anticiparla aquí sería el segundo validador que este componente existe para no ser.
- **`export.format.xlsxUnavailable` ya no existe** en ninguno de los dos catálogos: afirmaba que el
  portal no lleva el escritor de hojas de cálculo. Su hueco lo ocupa `export.format.xlsxRowLimit`,
  que nombra el tope de 200 000 filas, dice qué pasa por encima y recuerda que el CSV no lo tiene.
  El aviso se sigue pintando bajo los radios (`data-aviso="xlsx"`).
- **`export.job.error.formatUnavailable` nombra el tope.** De las dos causas del código
  `formato_no_disponible`, esa es la única que un analista puede provocar desde el formulario; la
  otra —falta el escritor— es del despliegue y no le dice nada a quien lee. La redacción ofrece la
  salida: acotar los filtros o pedir la exportación en CSV.
- **`formatoDisponible` y `FORMATOS_DEGRADADOS` se quedan sin llamantes** en `useExportaciones.ts`,
  con un comentario que todavía afirma que `xlsxwriter` no está instalado. El composable no era
  write-set de este ajuste; queda anotado para quien lo tenga.

| Prueba | Defecto que atrapa |
|---|---|
| `deja pedir XLSX y manda a la API el formato que el lector eligio` | La opción vuelta a deshabilitar. Comprueba el atributo **y** el cuerpo del POST, porque un control deshabilitado también se traga el `change` que mueve el modelo. Con el defecto reinyectado se vio fallar por las dos vías, una a una |
| `explica el fallo de formato por el tope de filas que lo provoca` | El regreso de la copia vieja: exige que las dos redacciones de `formatUnavailable` y de `xlsxRowLimit` nombren las 200 000 filas |

`test/idioma.spec.ts` cubre el resto sin cambios: las dos hojas nuevas están redactadas distinto en
cada idioma y ninguna es de las dos excepciones permitidas.

**Verificación**: `pnpm typecheck` limpio; `eslint` sobre los archivos tocados sin errores;
`vitest run test/exportaciones.spec.ts test/idioma.spec.ts test/contratos.spec.ts` → **32 passed**.

### Cobertura final de pruebas (US-009)

**Fecha**: jue 13-ago-2026, después del ajuste de la interfaz al XLSX real · **Write-set**:
`tests/backend/test_export_almacen_firmado.py` y `frontend/test/exportaciones.spec.ts`. **Ningún
archivo de producción se tocó**, ninguna aserción existente se bajó y ninguna prueba se borró ni se
marcó `skip`. Tampoco se creó ningún archivo de prueba nuevo: los dos huecos de backend caben junto
a la factoría del almacén, que ya era la vecina de los ajustes, y los cinco de frontend junto a los
`describe` que ya hablaban del sondeo, de los momentos y de la franja.

**Método**: cada prueba nueva se vio fallar. Se inyectó el defecto que su docstring describe, se
comprobó que la suite se ponía roja **en esa prueba y en ninguna otra**, y se restauró el archivo
desde una copia previa. **Once defectos inyectados** de uno en uno: dos por cada prueba de backend y
uno por cada una de las siete de frontend.

#### Los siete huecos que quedaban

La cobertura de las tres olas y de los dos cierres ya era casi completa —`api/export.py` al 100 %,
`export_service.py` al 98 %— así que el hueco no estaba en las líneas sin ejecutar sino en tres
sitios donde **nadie afirmaba nada**:

1. **Los valores por defecto de los cuatro ajustes de §4.2.** Todas las pruebas de la US pasan
   `ttl_horas=24` y `retraso_demo` a mano, así que las 24 horas del criterio de aceptación y el cero
   del estiramiento de demostración no estaban afirmados en ninguna parte: cambiarlos en `config.py`
   dejaba la suite entera en verde. (`export_storage_backend` sí lo estaba, por
   `test_factoria_elige_una_sola_vez`.)
2. **La derivación de la clave de firma.** `derivar_clave_de_firma` no tenía ni un llamante en las
   pruebas. Un portal que firma y verifica con la misma clave equivocada está de acuerdo consigo
   mismo, de modo que las siete pruebas del enlace firmado seguían pasando con la clave vacía o con
   la del JWT.
3. **El ciclo de vida del sondeo fuera de la página.** Las pruebas del temporizador conducen la
   tienda directamente, sin montar nada, y las que montan la pantalla no tenían ningún trabajo vivo:
   entre unas y otras, **nadie ejercía el par pantalla+temporizador**, que es CA-4 completo. Y
   `plugins/exportaciones.client.ts` —el archivo más nuevo— no tenía ninguna prueba.
4. **El primer momento y el momento que el portal no conoce.** `?momento=proceso` y `?momento=enlace`
   estaban cubiertos; `solicitud` y un valor desconocido, no.
5. **La declaración de `exportDemoDelay` en `nuxt.config.ts`.** Las dos pruebas de la franja doblan
   `useRuntimeConfig`, así que dicen qué hace la pantalla con el valor y nada sobre si el valor puede
   llegar.
6. **El 503 `trabajos_no_disponibles` sobre el cable de la pantalla.** La traducción del registro
   caído está probada en backend y `falloDeExportacion` como función, pero nadie comprobaba que el
   lector acabara viendo la frase del registro caído ni que el botón de reintento reintentara.

#### Pruebas añadidas y el defecto que pone roja a cada una

**Backend** (`tests/backend/test_export_almacen_firmado.py`, de 7 casos a **9**):

| Caso | Defecto que la pone roja |
|---|---|
| `test_los_plazos_por_defecto_son_los_que_el_criterio_describe` | `export_link_ttl_hours = 1` (enlaces que caducan en una hora y un criterio de aceptación que ya no describe nada) y `export_demo_delay_seconds = 8.0` (el estiramiento de la demostración convertido en el comportamiento de todos los despliegues, con la franja de honestidad —que la lee del otro lado— apagada). Ambos se inyectaron y ambos tiran solo esta prueba |
| `test_la_clave_de_firma_vacia_se_deriva_y_jamas_firma_con_nada` | `clave=declarada` a secas: la clave vacía firma de verdad y cualquiera que lea el repositorio reproduce la firma. Y `clave=declarada or settings.jwt_secret_key`: quien obtenga un enlace de descarga obtiene la clave que emite los tokens. Se comprueba pidiendo a dos almacenes construidos con esas dos claves que acepten una firma real; el control positivo evita que las dos negativas vengan de una firma que nadie puede canjear |

**Frontend** (`frontend/test/exportaciones.spec.ts`, de 21 casos a **28**):

| Caso | Defecto que la pone roja |
|---|---|
| `sigue el trabajo despues de que el lector se vaya a otra ruta` | Un `onUnmounted(() => detenerSondeo())` en `exportar.vue`, o el temporizador devuelto a la página. **Ninguna prueba anterior lo veía**, porque las del sondeo no montan nada. El lector pide un millón de filas, se va al tablero y vuelve a una pantalla que nunca supo que la exportación terminó |
| `queda atenta a la pestana antes de que exista ningun trabajo` | Quitar `observarVisibilidad()` del arranque. `iniciarSondeo` se retira ante un documento oculto **antes** de enganchar el oyente, así que un trabajo pedido desde una pestaña de fondo no se vigila nunca: cuando el lector vuelve, no hay nadie escuchando. Esta es la razón de existir del plugin y aquí queda escrita |
| `no pone nada en el cable por el mero hecho de arrancar` | Un `cargarHistorial()` añadido al arranque para que alguna insignia cuente algo: una petición por visita, en todas las pantallas y para todos los roles, incluido el que recibe 403 |
| `con un trabajo terminado, momento=solicitud no presta el enlace del tercero` | `trabajoDeMomento('solicitud')` devolviendo «el más reciente», que es la simplificación natural: la captura del primer momento saldría con el enlace firmado del tercero dentro |
| `un momento que el portal no conoce no fija nada ni imprime su clave` | `momentoDeConsulta` devolviendo la cadena cruda: la etiqueta imprimiría `export.moment.undefined` al lector y la pantalla quedaría fijada a un momento que no existe |
| `declara exportDemoDelay en la mitad publica de runtimeConfig` | Borrar la línea de `nuxt.config.ts`. Nuxt solo expone las claves declaradas y `NUXT_PUBLIC_*` sobrescribe las existentes, nunca las crea: la demostración fija la variable, la interfaz lee `undefined`, la franja no enciende y la captura de A4 muestra un trabajo estirado sin nada que declare el estiramiento —la mentira exacta que la franja existe para impedir |
| `nombra el registro caido y deja volver a pedirlo` | Tres a la vez: el código mapeado a la frase genérica (que no dice nada ni ofrece salida), el reintento emitiendo un evento que nadie atiende (recargar como única salida) y el fallo dejando la fase en `cargando` (un esqueleto latiendo para siempre) |

#### Lo que se descartó por no poder fallar, o por ser señal repetida

- **La construcción de los argumentos de la firma V4 de `AlmacenGCS`.** Ya la cubre
  `test_gcs_firma_v4_con_la_misma_vigencia`, que afirma `("v4", timedelta(hours=24))` sobre el doble
  del blob. Es lo único verificable sin proyecto y ya estaba verificado.
- **«El arranque de quien no exporta no falla» como aserción propia.** Toda la suite construye los
  ajustes sin ninguna variable `EXPORT_*`, así que un quinto ajuste sin valor por defecto ya derriba
  cientos de casos; una prueba dedicada no añadiría señal, solo un segundo sitio donde leerla. Lo que
  sí puede fallar sola —el **valor** de cada defecto— es lo que se afirma.
- **Pruebas unitarias de `momentoDeConsulta` y de `claveDeFallo`.** Lo que deciden ya se afirma a
  través de la pantalla, que es donde el defecto lo ve un lector. Una segunda copia al nivel de la
  función mediría lo mismo dos veces.
- **Que `exportaciones.client.ts` termine en `.client`.** Es una aserción sobre un nombre de archivo;
  no hay defecto que un lector pueda sentir que la ponga roja, porque la tienda ya se guarda con
  `typeof document === 'undefined'`.
- **El cuerpo de los dos `CONSTRAINT` de coherencia de la migración.** Sus nombres ya se afirman
  contra `db/schema.sql`. Afirmar además su SQL sería comparar el texto del archivo consigo mismo:
  el valor de las pruebas de `CHECK` que ya existen viene de que enfrentan **dos** fuentes, el SQL y
  las enumeraciones de Python, y aquí no hay segunda fuente.
- **Una prueba de paridad `es`/`en` del subárbol `export.*`.** Es T-19, retirada en §6 por duplicar
  exactamente lo que mide `idioma.spec.ts`. Sigue retirada.

#### Dos cambios en la infraestructura compartida de la suite de frontend

Los dos son aditivos y ninguno toca una aserción existente:

- `crearServidor` acepta `fallosDeLista`, que hace fallar esa cantidad de lecturas iniciales del
  historial con el 503 y el código que emite la API. Por defecto es 0, así que los 21 casos
  anteriores no cambian de comportamiento.
- El `afterEach` devuelve `document.hidden` a `false`. happy-dom comparte un `document` entre las
  pruebas de un archivo, y una pestaña que un caso dejara oculta apagaría el sondeo del siguiente
  antes de que llegara a armar su temporizador.

#### Aserciones obsoletas: ninguna

No se encontró ninguna prueba que afirme un comportamiento que ya no existe. El único texto del
árbol que describe un portal retirado es un comentario de `useExportaciones.ts` —el que aún dice que
`xlsxwriter` no está instalado, junto a `formatoDisponible` y `FORMATOS_DEGRADADOS` sin llamantes—,
y ya está anotado como pendiente en «Ajuste de la interfaz al XLSX real». Ninguna prueba lo afirma.

#### Conteo final y verificación

- `pytest -c backend/pyproject.toml tests/backend/test_export_{endpoint,almacen_firmado,estado_scopes,job_migracion}.py`
  → **72 passed**, repartidos 26 + 9 + 23 + 14. Eran 70.
- `vitest run test/exportaciones.spec.ts test/pantallas.spec.ts test/idioma.spec.ts test/contratos.spec.ts`
  → **72 passed** (28 + 33 + 9 + 2). Eran 65.
- `ruff check` y `ruff format --check` sobre el archivo tocado → limpios ·
  `mypy --config-file backend/pyproject.toml --exclude '^tests/ml/' backend/app scripts tests` →
  **Success: no issues found in 85 source files**.
- `eslint test/exportaciones.spec.ts` → 0 errores · `pnpm typecheck` → limpio.
- **No se corrió la suite completa del proyecto**, por instrucción. Sí se corrió `tests/backend`
  entero una vez, para descartar daño colateral: **654 passed, 17 skipped, 0 failed**.

---

## Cierre de la US — integración (jue 13-ago-2026)

**Estado**: `coding`. **SHA base del diff**: `a251652` — el ancla es
`git diff --name-only a251652`, nunca `HEAD~N`: el árbol se compartió con US-018 y US-023 y los
commits se intercalan.

**Migración aplicada**: `db/migrations/20260813204211_create_export_job.sql` (la marca de tiempo real
la generó `make db-new`; la `20260813090000` del plan era la prevista). Verificada reversible contra
PostgreSQL real: `db-up` → `db-rollback` → `db-up` deja `db/schema.sql` byte a byte idéntico.
**Despliegue**: ninguno. Esta US no toca la nube (§7 del plan); la fachada entrega el criterio de las
24 h en local y el día del bucket el cambio es `EXPORT_STORAGE_BACKEND=gcs`, no una refactorización.

### Snapshot de archivos de la US

Nuevos (19): `db/migrations/20260813204211_create_export_job.sql` ·
`backend/app/models/export.py` · `backend/app/services/almacen/{__init__,local,gcs}.py` ·
`backend/app/services/export_service.py` · `backend/app/api/export.py` ·
`frontend/app/types/exportacion.ts` · `frontend/app/stores/exportaciones.ts` ·
`frontend/app/composables/useExportaciones.ts` · `frontend/app/plugins/exportaciones.client.ts` ·
`frontend/app/components/exportacion/{FormularioExportacion,TarjetaTrabajo,HistorialExportaciones}.vue` ·
`frontend/test/exportaciones.spec.ts` ·
`tests/backend/test_export_{job_migracion,endpoint,almacen_firmado,estado_scopes}.py`.

Modificados (11): `db/schema.sql` (regenerado) · `backend/app/main.py` (una línea) ·
`backend/app/core/config.py` (cuatro ajustes) · `backend/app/core/permissions.py` (cuatro filas) ·
`backend/.env.example` · `backend/pyproject.toml` y `backend/poetry.lock`
(`polars[xlsxwriter] (==1.43.2)`, lock con `xlsxwriter 3.2.9`) · `docs/security.md` (bloque
regenerado) · `frontend/nuxt.config.ts` (`exportDemoDelay`) ·
`frontend/app/pages/exploracion/exportar.vue` (reescrita, sin `EstadoPendiente`) ·
`frontend/i18n/locales/{es,en}.json` (`export.*`, `screen.exports.description`, y **borradas** las
cuatro hojas `screen.exports.capability.*`) · `frontend/test/pantallas.spec.ts` (una línea).

Evidencia A4 (3): `docs/entregables/imagenes/us009_exportacion_momento{1_solicitud,2_proceso,3_enlace}.png`.

### Ampliaciones del write-set del plan, y por qué

| Archivo | Quién lo escribió | Motivo |
|---|---|---|
| `frontend/app/plugins/exportaciones.client.ts` | O3 | CA-4 pide que el estado sea consultable **desde cualquier pantalla**, y el plan situaba el ciclo de vida «en el layout». La carpeta `app/plugins/` no existía: crearla es aditivo y deja `layouts/portal.vue` —compartido con las US en vuelo— sin tocar |
| `frontend/nuxt.config.ts` | integración | Nuxt solo expone las claves declaradas en `runtimeConfig.public` y `NUXT_PUBLIC_*` únicamente sobrescribe las existentes: sin `exportDemoDelay` la franja de honestidad no encendía nunca, y era bloqueante para las capturas |
| `backend/pyproject.toml` · `poetry.lock` | cierre de deudas | Levantar la degradación de XLSX exigía la dependencia. Pin exacto conservado |

### P-7 cerrado — verificación de extremo a extremo en el portal levantado

Las tres capturas se tomaron con Playwright sobre `docker compose up`, con sesión real de
`dhernandez` (rol `analista`) y **estado real**, no maqueta. Para que el momento 2 durara lo bastante
se puso `EXPORT_DEMO_DELAY_SECONDS=8` en `backend/.env.local` y su espejo
`NUXT_PUBLIC_EXPORT_DEMO_DELAY=8` en `frontend/.env.local` — **ambos archivos son locales y están en
`.gitignore`**; conviene devolverlos a 0 cuando la demostración termine.

El trabajo capturado es real: `creditos`, **180 000 filas**, **17,1 MB**, solicitado 13/8/26 20:38 y
`caduca_en` 14/8/26 20:38. La franja `export.demo.notice` está visible en las tres.

Cuatro comprobaciones hechas contra el portal en marcha, no contra un doble:

1. **CA-6, las 24 h, sobre el reloj real.** El `exp` del enlace emitido es `1786761493`, o sea
   2026-08-14 20:38:13 local: exactamente `terminado_en + 24 h`.
2. **La descarga entrega el archivo de verdad.** `200`, `text/csv; charset=utf-8`,
   `Content-Disposition: attachment`, **17 940 930 bytes**, y la primera línea es la cabecera críptica
   del silo (`cli_ref,nom_cli,prod_cd,sdo_cap,...`): es el dato, no un marcador.
3. **Firma alterada → 403 `firma_invalida`.**
4. **`exp` manipulado → 403 `firma_invalida`, no 410.** Esto es lo que **prueba** que el vencimiento
   viaja **dentro** del material firmado: si el `exp` no estuviera firmado, cambiarlo habría dado 410
   o 200. Es la decisión 4 de O2 observable desde fuera.

Los dos únicos errores de consola de la pantalla son esas dos peticiones forjadas a propósito.

### Deudas cerradas en este run (ninguna queda declarada)

| Pendiente | Cómo se cerró |
|---|---|
| **P-4** | `polars` ya estaba pinneado; no hizo falta `poetry add` |
| **P-5** | Marca de tiempo real de la migración, generada por `make db-new` |
| **P-6** | `DATASETS_EXPORTABLES = ("creditos", "liquidez", "derivados")`: las tres filas de `catalog_source` con `has_extract = true` |
| **P-9** | `permissions.py` existía: las dos filas pasaron a `vigente` y se añadieron las otras dos |
| **P-13** | `listar_todos` como método aparte; el `admin` ve metadatos de todos los trabajos, sin enlace |
| **P-15** | `exportDemoDelay` declarado en `runtimeConfig.public` |
| **P-16** | Disparo único por tarjeta armado para el instante de `caduca_en`, con rearme; cero peticiones nuevas |
| **P-17** | Relectura del historial una sola vez por transición a terminal |
| **XLSX** | Funciona de verdad, con tope **medido** de 200 000 filas |
| **P-7** | Las tres capturas, arriba |

- **P-2 — CERRADO el 13-ago-2026.** El contraste contra los cinco `SKILL.md`
  (`portal-export-jobs`, `portal-backend-api`, `portal-db-migrations`, `portal-db-models`,
  `portal-testing`) está escrito en el **§12 del plan**. Resultado: ninguna divergencia era un
  defecto; quedan **tres obligaciones con dueño** —migrar `filtros` a `SemanticQuery` cuando aterrice
  US-011, añadir el segmento de usuario a la clave de GCS antes del primer despliegue con
  `EXPORT_STORAGE_BACKEND=gcs`, y el smoke post-deploy de export en US-004— y **tres skills
  desactualizadas** respecto del repositorio.

### Hallazgos que corrigen al plan

1. **El volumen objetivo de 1 M de filas no es alcanzable en XLSX.** Medido: 997 ms de bloqueo del
   bucle contra el gate de 500 ms de `/health`. Curva: 100 k → 112 ms · 200 k → 198 ms · 300 k →
   381 ms · 500 k → 505 ms. El tope de 200 000 filas tiene 2,5× de margen y aún exporta enteros
   `creditos` (180 k) y `derivados` (80 k). **CSV no tiene tope**: `scan_parquet` + `sink_csv` no
   materializa.
2. **`setTimeout` guarda su retraso en 32 bits.** Cualquier plazo más allá de ~24 días dispara de
   inmediato, así que el disparo que retira un enlace caducado debe **rearmarse**, no declarar la
   muerte del enlace al primer disparo.
3. **El orden de las US en `pantallas.spec.ts` se invirtió**: el plan preveía US-009 (jue 13) antes
   que US-023 (vie 14), y US-023 llegó primero. Se aplicó la regla acordada —quien llega segundo
   **añade su ruta al arreglo existente**— y hoy el filtro excluye `[RUTA_ACCESO, RUTA_ASISTENTE,
   '/exploracion/exportar']`. Ninguna prueba se borró.

### Incidente registrado

El agente de pruebas ejecutó `git checkout backend/app/core/config.py` para revertir una mutación,
sin considerar que **todo el árbol de las tres US está sin commitear**: eso borró los cuatro ajustes
`export_*` **y** el `chat_provider` de US-023. Lo restauró y la integración lo verificó por cuatro
vías: los cuatro ajustes presentes, `chat_provider` presente y consumido por `api/chat.py:85`, el
conteo de `export_storage_backend` de vuelta en **2**, y la suite de backend completa en verde.
**Lección para la cadena**: con el árbol sin commitear, `git checkout <archivo>` no revierte una
mutación, borra el trabajo de todas las US que tocaron ese archivo. Para revertir una mutación se
restaura el texto leído, nunca el índice.

---

## QA — pasada del 13-ago-2026 (SHA base `a251652`)

**Veredicto**: **PASA CON ARREGLOS**. Ocho defectos corregidos en esta pasada; ninguno abierto de
severidad alta ni media.

Gate del repositorio tras los arreglos: `make check` limpio y `make test` en verde — backend
**733 passed, 17 skipped, cobertura 98,20 %**; frontend **752 passed, cobertura 89,0 %**. Cobertura
de los archivos de esta US: `api/export.py` 100 %, `models/export.py` 100 %,
`services/export_service.py` 99 %, `services/almacen/` 95-100 %, `stores/exportaciones.ts` 89 %,
`composables/useExportaciones.ts` 96 %.

Auditoría: 9 agentes de revisión sobre los archivos del diff y 49 verificadores adversarios, uno
por hallazgo. **22 hallazgos confirmados, 27 refutados y descartados** por no reproducir.

### Defectos encontrados y corregidos

| # | Sev. | Qué pasaba | Dónde | Estado |
|---|---|---|---|---|
| QA-A4 | **alto** | **Fuga de datos entre sesiones en la misma pestaña.** El mapa `detalles` no se limpiaba nunca, y el getter `trabajos` reinyecta como filas los detalles ausentes del historial. El analista A exporta y sale; B entra en la misma pestaña y **ve los trabajos de A**: dataset, filas, tamaño, instantes | `stores/exportaciones.ts:220` | **corregido**: acción `olvidar()` que vacía las estructuras vivas y apaga el temporizador, invocada desde `expiro` (401) y desde un `watch` sobre el usuario de la sesión en `plugins/exportaciones.client.ts`, que cubre el cierre de sesión explícito |
| QA-B2 | medio | `sig` estaba acotado en longitud pero no en alfabeto: 64 caracteres no ASCII hacían que `hmac.compare_digest` lanzara `TypeError` y el endpoint respondiera **500** en vez del 403 del contrato | `api/export.py:203` | **corregido**: `pattern` hexadecimal en el `Query` (422) más traducción `TypeError` a `FirmaInvalida` en `resolver_descarga` |
| QA-B4 | medio | `_tienda_disponible` traducía el error de conexión pero **no revertía la sesión**. Esa misma sesión es la del camino de recuperación `_fallar` a `marcar_fallido`: SQLAlchemy la deja en transacción inválida y el estado terminal **no se escribía**, dejando el trabajo colgado en `en_proceso` hasta los 200 sondeos | `services/export_service.py:333` | **corregido**: `rollback()` antes de levantar `TrabajosNoDisponiblesError`, con el fallo del propio rollback registrado y no propagado |
| QA-B5 | medio | `filtros` era `dict[str, Any]` **sin ningún tope**, y se persiste como JSONB antes de que nada lo acote | `models/export.py:169` | **corregido**: cuatro topes justificados contra los silos (32 filtros, 100 valores, 64 y 128 caracteres) y tipo de valor cerrado, sin estrechar lo que el frontend produce |
| QA-B6 | medio | **Vacío falso.** `sinTrabajo` se derivaba de `trabajoDestacado`, que el lector pone en `null` con un clic: la pantalla decía «no hay ningún trabajo» con el trabajo corriendo y visible abajo | `pages/exploracion/exportar.vue:63` | **corregido**: nuevo computed `trabajoDelMomento` en el store; `trabajoDestacado` queda solo para la fila expandida |
| QA-B7 | medio | **Error pegajoso.** Un único sondeo fallido dejaba la franja roja para siempre: ningún camino de éxito devolvía `fallo` a `null` | `stores/exportaciones.ts:387` | **corregido** en `consultar` y en `releerHistorial` |
| QA-B1 | medio | La matriz de permisos publicaba «Historial del propio llamante» mientras `ExportService.historial` devuelve **el registro completo** cuando el rol es `admin`: la matriz normativa declaraba **menos** exposición de la que el código entrega | `core/permissions.py:223` | **corregido**: las dos reglas reescritas y el bloque de `docs/security.md` **reemitido con `render_permission_matrix()`**, jamás a mano |
| QA-B8 | medio | La etiqueta de estado —el único texto que cambia sin acción del lector, que el sondeo mueve de «En cola» a «Completado»— no vivía en ninguna región `aria-live`, y el bloque del enlace tampoco | `components/exportacion/TarjetaTrabajo.vue:110` | **corregido**: dos regiones vivas que **existen siempre**, porque un elemento que aparece ya poblado no se anuncia, que era justo el defecto |
| QA-B9 | bajo | El giro del icono y el pulso de la barra corrían sin `motion-reduce:animate-none` | `components/exportacion/TarjetaTrabajo.vue:114,132` | **corregido** |
| QA-C1 | bajo | El `COMMENT` de `export_job.expires_at` dice «`created_at` mas 24 h» y el código escribe `terminado_en mas 24 h`. El comentario viaja a `db/schema.sql` | `db/migrations/20260813204211_create_export_job.sql:49` | **abierto**, bajo. Una migración aplicada es inmutable (`db/AGENTS.md`): se corrige por rollforward, no aquí |
| QA-C2 | bajo | `test_el_protocolo_declara_la_superficie_acordada` promete medir las dos implementaciones y solo inspecciona el `Protocol`: renombrar un parámetro en `AlmacenLocalFirmado` no la pone roja | `tests/backend/test_export_almacen_firmado.py:513` | **abierto**, bajo |

Los casos nuevos se verificaron **rojos antes del arreglo**. Uno se reescribió porque su primera
redacción pasaba con el defecto puesto: `releerHistorial` limpiaba el fallo por otra vía.

### Criterios de aceptación contra el código real

| Crit. | Enunciado | Estado | Evidencia |
|---|---|---|---|
| A | `POST /api/export` valida y responde **ya** con `job_id`; el trabajo en `BackgroundTasks` | **cumple** | `api/export.py:64-101`, `status_code=202`, `add_task` tras el retorno del service |
| B | `GET /api/export/{job_id}` con sondeo del frontend | **cumple** | Un solo temporizador, 3 000 ms, apagado con `document.hidden` y a los 200 sondeos |
| C | GCS `exports/{user}/{job_id}.{ext}`, signed URL 24 h, lifecycle 7 días | **parcial, recorte declarado** | Las 24 h **sí se entregan de verdad**: el `exp` viaja dentro del HMAC, 403 si se altera y 410 si venció, con reloj inyectable. **No se entregan**: el segmento `{user}` de la clave ni el lifecycle. El recorte 3 del §10.2 del plan dice «sin lifecycle ni auditoría de duración; una sola signed URL» |
| D | Registro con usuario, filtros, tamaño y duración | **cumple** | `requested_by`, `filters` JSONB, `byte_size`, `row_count`, y `started_at` mas `finished_at`, que son las dos columnas con las que la duración se calcula |
| E | No bloqueo: `/api/catalog/search` bajo 500 ms durante un export de **1 M filas** | **cumple de nombre** | `test_export_endpoint.py:568-631` mide `/health` con **2 000 filas** y un `sleep`, no con 1 M. La medición real de 1 M existe pero está en el handoff como prosa, no como prueba. Queda en la prueba manual, §5 |

Verificado sin hallazgo: el 404-y-nunca-403 de propiedad, la ausencia de `object_key` en toda
respuesta, el `admin` que lee el registro pero **no** descarga ajeno, la derivación de la clave de
firma cuando `EXPORT_SIGNING_KEY` está vacía —HMAC con etiqueta de separación de dominio, no cadena
vacía—, el `scan_parquet` mas `sink_csv` en `asyncio.to_thread`, y que el compilador de filtros solo
compone `is_in` sobre columnas verificadas: el cliente **no** redacta Polars.

### Estados no felices

Vacío: cumple. Cargando sin salto: cumple. Error: cumple, pegajosidad corregida en QA-B7. Sin
permiso: cumple. Accesibilidad: regiones vivas añadidas en QA-B8, movimiento reducido en QA-B9.

### Archivos auditados de esta US

`backend/app/api/export.py` · `backend/app/models/export.py` ·
`backend/app/services/export_service.py` · `backend/app/services/almacen/{__init__,local,gcs}.py` ·
`backend/app/core/{config,permissions}.py` · `backend/.env.example` ·
`db/migrations/20260813204211_create_export_job.sql` · `db/schema.sql` · `docs/security.md` ·
`frontend/app/pages/exploracion/exportar.vue` · `frontend/app/components/exportacion/*.vue` ·
`frontend/app/composables/useExportaciones.ts` · `frontend/app/stores/exportaciones.ts` ·
`frontend/app/plugins/exportaciones.client.ts` · `frontend/app/types/exportacion.ts` ·
`tests/backend/test_export_*.py` · `frontend/test/exportaciones.spec.ts`.

Prueba manual **nueva**:
[`docs/manual-test/us-009-exportacion.md`](../manual-test/us-009-exportacion.md), escrita en esta
pasada y pendiente de ejecutar por una persona.
