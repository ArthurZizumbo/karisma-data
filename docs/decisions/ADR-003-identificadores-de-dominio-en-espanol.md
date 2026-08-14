# ADR-003 — Los identificadores de dominio se escriben en español; la prosa del código, en inglés

**Fecha**: 14-ago-2026
**Estado**: vigente
**Deroga**: la lectura literal de «código (identificadores, comentarios, docstrings) en inglés» de
la regla de idioma del orquestador. Los comentarios y los docstrings siguen en inglés; los
identificadores, no.

## Contexto

La regla transversal dice que todo el código va en inglés. El repositorio no la cumple, y no la
incumple por descuido: la incumple **por épica**, con una frontera limpia y con los dos commits más
recientes enteros del lado del español.

En inglés, E1 y E2:

- `backend/app/services/series_service.py`: `SeedMissingError`, `PayloadTooLargeError`,
  `SeriesPayload`, `build_payload`, `load_series`.
- `backend/app/services/user_admin_service.py`: `change_role`, `set_disabled`,
  `guard_self_demotion`, `guard_self_disable`.
- `backend/app/api/users.py`: `list_users_endpoint`, `update_user_endpoint`,
  `disable_user_endpoint`.

En español, E3 y E4. Son `d8c8391` («exportacion en segundo plano») y `0ad93d5` («streaming SSE con
cancelacion real»), que entre los dos añaden ocho módulos de `backend/app/` y no dejan un solo
identificador de dominio en inglés:

- `backend/app/services/export_service.py`: `TrabajoNoEncontradoError`, `ExportacionFallidaError`,
  `_escribir_xlsx`, `_con_filtros`.
- `backend/app/services/almacen/__init__.py`: `AlmacenDeExportaciones`, `RelojDelSistema`,
  `crear_almacen`, `EnlaceCaducado`, `FirmaInvalida`.
- `backend/app/models/export.py`: `SolicitudExportacion`, `TrabajoResumen`, `EstadoTrabajo`,
  `FormatoExportacion`.
- `backend/app/services/chat_stream.py`: `transmitir`, `formatear_evento`, `streams_activos`.
- `backend/app/services/proveedores/`: `ProveedorDeTokens`, `obtener_proveedor`,
  `ProveedorGuionizado`, `generar`, `seleccionar_conversacion`.

Y dos hechos que la regla nunca describió, los dos anteriores a E3:

- **Los nombres de las pruebas son frases en español desde E1.** `tests/backend/test_series_endpoint.py`
  trae `test_etag_se_repite_y_el_if_none_match_da_304` y
  `test_datos_no_sembrados_devuelve_503_con_codigo`. No es una desviación de esta semana: la regla
  marcaba como incumplimiento cada nombre de prueba del repositorio desde julio.
- **El frontend es español casi completo.** De los dieciséis composables de
  `frontend/app/composables/` solo `useChatStream.ts` lleva una palabra en inglés; el resto va de
  `useBusquedaCatalogo.ts` a `useSesion.ts`. `frontend/app/utils/` es igual, de `navegacion.ts` a
  `serieEstadisticas.ts`.

En volumen histórico gana el inglés. En lo escrito esta semana gana el español sin una sola
excepción. No había ADR que lo recogiera —`docs/decisions/` tenía dos archivos, ADR-001 y ADR-002—,
así que cualquier revisión futura marcaba `transmitir`, `guionizado` y `AlmacenDeExportaciones` como
defecto y quien los escribió no tenía dónde señalar la decisión.

## Decisión

Híbrido, con la frontera puesta en **quién lee cada cosa**.

### 1. Identificadores de dominio: español

Lo que nombra un concepto del negocio financiero del portal se escribe con la palabra que el equipo
usa al hablar del producto, que es la misma que aparece en el plan, en los entregables y en la
interfaz: `SolicitudExportacion`, `AlmacenDeExportaciones`, `EstadoTrabajo`, `transmitir`,
`ProveedorGuionizado`. Traducir esa palabra al entrar al código obliga a un diccionario mental en
cada lectura y a deshacer la traducción al escribir la copia de la pantalla.

Los nombres de las pruebas entran aquí, y quedan **explícitamente** en español:
`test_el_historial_de_un_admin_no_reparte_enlaces` describe un criterio de aceptación, y ese
criterio está escrito en español en el plan.

### 2. Prosa del código: inglés

Docstrings Google-style y comentarios, sin excepción y también dentro de los módulos con
identificadores en español. `RelojDelSistema.ahora` documenta *«Return the current UTC instant»* y
`_escribir_xlsx` abre con *«Write the spreadsheet, when this deployment and this size allow one»*.
La prosa es la parte larga, la que explica el porqué y la que un revisor externo lee primero; el
inglés le quita la ambigüedad de género y el problema de los acentos en un archivo que también
puede leer una herramienta.

### 3. Se queda en inglés, además, todo lo que no elegimos nosotros

- **El vocabulario del framework y del protocolo**: `Depends`, `Security`, `field_validator`,
  `response_model`, `status`, `GET`, `Bearer`.
- **Las columnas del esquema y los campos de `SQLModel` que las espejan.** `db/schema.sql` es la
  salida de dbmate y `ExportJob` la copia campo a campo: `requested_by`, `export_format`,
  `object_key`, `row_count`, `created_at`. E3 escribió su modelo de negocio en español y su tabla en
  inglés **en el mismo commit**, y esa es la frontera correcta: renombrar una columna ya aplicada
  exige una migración, y una migración por estética no se escribe.
- **Las claves de i18n**, jerárquicas y en inglés por [ADR-001](ADR-001-ui-bilingue-i18n-real.md).
- **Los identificadores técnicos que ya viajan en el contrato HTTP**: `job_id` y `dataset` en
  `TrabajoResumen`, cuyo resto de campos sí es español (`formato`, `estado`, `filas`,
  `tamano_bytes`, `solicitado_en`).
- **Los nombres de span y de atributo de OpenTelemetry**: `db.retrieval`, `llm.call`,
  `llm.prompt_hash`. Son vocabulario de una convención externa, no del portal.

### 4. Lo escrito en inglés no se renombra

`series_service.py`, `user_admin_service.py` y `api/users.py` se quedan como están. Un renombrado
masivo es un diff grande sin cambio de comportamiento, encima de tres US en vuelo la semana del
entregable A4, y la regla que lo pediría no vale ese riesgo.

De ahí la consecuencia práctica: la frontera no es la épica, es la fecha. Un módulo nuevo nace en
español; uno existente conserva su idioma, y un nombre nuevo dentro de un módulo en inglés sigue al
módulo y no a este ADR. `ml/data/aggregates.py` es el ejemplo de lo contrario y de por qué importa:
convive `business_days` con `serie_grid` y `build_serie_tablero` en el mismo archivo, y un archivo
con dos idiomas se lee peor que un repositorio con dos.

## Consecuencias

- La revisión deja de marcar como defecto `transmitir`, `guionizado` y `AlmacenDeExportaciones`, y
  empieza a marcar lo contrario: un concepto del dominio bautizado en inglés en un módulo nuevo.
- **Sin comprobación mecánica.** Ningún linter distingue un identificador de dominio de uno técnico:
  ruff no sabe qué es `transmitir`. La regla vive en la revisión, igual que la prohibición de
  cadenas sueltas en los componentes de ADR-001.
- **Los mensajes de error no los cubre este ADR.** Hoy varios validadores Pydantic lanzan una frase
  en español —`"el mensaje no puede ser solo espacios en blanco"` en `backend/app/models/chat.py`—
  y eso es un defecto distinto, no una aplicación de esta decisión: la interfaz bilingüe no puede
  traducir una frase y el contrato exige código estable en `detail.codigo`. Queda abierto en
  [`docs/us-backlog/10-codigo-estable-en-el-422.md`](../us-backlog/10-codigo-estable-en-el-422.md).
- El día que este ADR se derogue, se deroga entero y con su plan de renombrado. Un repositorio con
  la mitad convertida es peor que cualquiera de los dos extremos.

## Dónde vive la regla

Sección «Reglas de código NON-NEGOTIABLE» de [`AGENTS.md`](../../AGENTS.md) y
[`CLAUDE.md`](../../CLAUDE.md), que son espejos y se sincronizan en el mismo commit.

**Los dos archivos raíz todavía dicen la regla anterior.** La auditoría del 14-ago-2026 que escribió
este ADR no los tenía en su write-set, precisamente por la sincronía que exigen; el texto exacto que
los sustituye viaja en su reporte y lo aplica quien tenga los dos archivos.
