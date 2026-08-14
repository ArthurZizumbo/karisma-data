# Auditoría cruzada de S4 — las cinco planeaciones del 11-ago-2026

**Fecha**: 11-ago-2026
**Alcance**: `us-009-exportacion`, `us-023`, `us-024`, `us-028`, `us-ux-07` (planes y handoffs)
**SHA base**: `f807a18` (`git rev-parse --short HEAD`, rama `us-016`)
**Fuente normativa**: §26 del plan (manda durante S4)

> **Para qué sirve este archivo.** Es la tabla que se consulta **antes de tocar nada** el jueves 13
> y el viernes 14. Cinco planes escritos en paralelo reclaman archivos que se solapan; aquí queda
> escrito quién es dueño de cada uno. Si un archivo no aparece en la tabla de disputados, es de un
> solo plan y no hay nada que decidir.

---

## Cómo se construyó, y qué no prueba

La matriz sale de extraer toda ruta de archivo citada entre acentos graves en los cinco planes y
quedarse con las que aparecen en dos o más. **Eso mide menciones, no reclamaciones de escritura**:
un plan que dice «`useChatStream.ts` lo lee sin escribir» aparece igual que uno que lo crea. La
resolución de abajo asigna un dueño único con independencia de eso, así que el ruido de la
extracción no contamina la decisión — pero conviene saber que la columna «los demás» incluye tanto
a quien leía como a quien creía escribir.

Quedan fuera por construcción: `AGENTS.md` de cada carpeta, `docs/us-planning/us-016.md` y
`us-009.md`, y `docs/orchestration/auto-invoke.md`. Los citan varios planes porque son **lectura
normativa**, no write-set. Nadie los toca en S4.

---

## 1. Matriz de colisión resuelta

| Archivo | Dueño único | Los demás | Cuándo |
|---|---|---|---|
| `frontend/app/pages/asistente.vue` | **US-023** (lo crea) | US-024 y US-028 montan sus componentes dentro; no reescriben la página | vie 14 mañana |
| `frontend/app/composables/useChatStream.ts` | **US-023** | US-024 y US-028 lo **leen** | vie 14 mañana |
| `frontend/app/types/chat.ts` | **US-023** | US-024 y US-028 lo **leen** | vie 14 mañana |
| `frontend/app/components/chat/ToolCallCard.vue` | **US-028** | US-024 lo **lee**. El estado *error* de la tarjeta es de US-028 | vie 14 tarde |
| `frontend/app/components/chat/HistorialConversacion.vue` | **US-028** | US-024 lo **lee** | vie 14 tarde |
| `frontend/app/components/chat/AvisoError.vue` | **US-024** | nadie más | vie 14 noche |
| `tests/backend/test_chat_error.py` | **US-024** | US-028 no lo escribe | vie 14 noche |
| `backend/app/main.py` · `core/config.py` · `.env.example` | **US-009** jue 13, **US-023** vie 14 | secuencial por día: cada una **añade** sus líneas, ninguna reordena lo ajeno | jue y vie |
| `db/schema.sql` | **US-009** | única con migración en S4; las demás ni lo tocan | jue 13 |
| `frontend/test/pantallas.spec.ts` | **US-009** jue 13, **US-023** vie 14 | cada una añade **su** caso; el archivo no se reescribe | jue y vie |
| `frontend/package.json` | **US-UX-07** (añade Playwright) | US-028 no añade dependencias | sáb 15 |
| `frontend/app/utils/navegacion.ts` | **nadie lo escribe en S4** | `/exploracion/exportar` y `/asistente` ya existen desde US-001. US-UX-07 solo lo **lee** para la tabla ruta↔rama | — |
| `backend/app/core/permissions.py` · `docs/security.md` | **US-016** | **No existen en `f807a18`.** US-023 y US-009 escriben una fila *solo si aparecen*; si no, declaran el bloqueo y no crean el archivo | — |
| `frontend/app/components/guia/**` · `frontend/test/laminas.spec.ts` | **US-UX-09** | US-028 añade **una** lámina nueva y ajusta el conteo, sin tocar las existentes | vie 14 tarde |
| `docs/entregables/main_a4.tex` · `contenido/a4_*.tex` | **US-UX-09** crea `main_a4.tex` | US-UX-07 añade sus `\input` y sus propios `a4_*.tex`, sin tocar `a4_03_guia_estilos.tex` ni `a4_06_cierre.tex` | sáb 15 |

---

## 2. Reparto de claves i18n

`frontend/i18n/locales/{es,en}.json` los tocan cuatro US. Cada una escribe **solo su subárbol** y
no reordena el resto del archivo.

| Subárbol | Dueña | Notas |
|---|---|---|
| `export.*` | **US-009** | incluye `export.demo.notice` |
| `nav.branch.exploreExports` · `nav.facets.items.exportHistory` | **US-009** | únicas claves de `nav` que se tocan en S4 |
| `chat.page.*` · `chat.controls.*` · `chat.demo.*` | **US-023** | `chat.demo.scriptedNotice` es la franja de honestidad de demo |
| `chat.stream.*` | **US-023** | incluye `chat.stream.step.*`, `chat.stream.errorFallback` y `chat.stream.toolCallFallback` |
| `chat.error.*` | **US-024** | `title` · `message` · `action` de la tarjeta de error de turno |
| `chat.toolCall.*` | **US-028** | `announce` · `elapsed` · `source` · `result.*` · `state.*` · `tool.*` |
| `guide.plate.toolCall` | **US-028** | entrada de su lámina nueva en la guía |

---

## 3. Defectos

### BLOQUEANTE-1 — el vocabulario de `paso`, traducido dos veces

`us-023.md` declara `chat.stream.step.*` y `us-024.md` declara `chat.error.step.*` **para el mismo
vocabulario cerrado de cuatro valores**: `recuperacion_de_datos`, `verificacion_de_permiso`,
`generacion_de_texto`, `transporte`.

Por qué es bloqueante y no cosmético: son dos subárboles de traducción para la misma enumeración,
en dos archivos escritos por dos agentes distintos el mismo viernes. El día que alguien afine el
texto de «verificación de permiso», lo afina en uno solo, y la aplicación pasa a decir dos cosas
distintas del mismo paso según se lo pregunte a la tarjeta o al aviso de turno. Ninguna prueba lo
ve, porque cada subárbol es internamente consistente.

**Decisión**: se unifica en **`chat.stream.step.*`, propiedad de US-023**, que es quien emite los
valores desde el generador. US-024 y US-028 lo **consumen** y no definen claves de paso propias.
`us-024.md` renuncia a `chat.error.step.*`.

### MAYOR-1 — dos dueños posibles para el estado *error* de la tarjeta

`us-024.md` incluye entre sus tareas «tarjeta de tool call en su cuarto estado», y `us-028.md`
define los cuatro estados de `ToolCallCard.vue` como suyos.

**Decisión**: el cuarto estado de la tarjeta es de **US-028**. US-024 es dueña del error **del
turno** (`AvisoError.vue`), que es otra cosa: un 403 emite ambos eventos y se pintan dos superficies
distintas y jerárquicas — la tarjeta dice qué consulta falló, el aviso dice qué hacer. Por eso
US-024 va **después** de US-028 en el viernes: necesita que la tarjeta exista para no duplicarle el
estado.

### MENOR-1 — `frontend/package.json` reclamado por dos

US-028 lo menciona; US-UX-07 necesita añadir Playwright. **Decisión**: dueña US-UX-07. US-028 no
añade dependencias — su lámina y su prueba de re-render se resuelven con lo que ya hay.

---

## 4. Descartado — lo que parecía defecto y no lo era

**`backend/app/core/permissions.py` no es un error de `us-023.md`.** Durante la sesión se dio por
confirmado que el plan citaba un módulo inexistente cuando el real es `core/scopes.py`. Es falso:
[`us-023.md:39`](us-023.md#L39) ya lo verificó el 11-ago-2026, dejó escrito que el archivo **no
existe en `f807a18`**, que es write-set exclusivo de US-016, y montó una puerta `test -f` antes de
escribir una sola línea, con la prueba B-8 declarada como bloqueada si la puerta es falsa. El plan
tenía razón. Queda registrado aquí porque un hallazgo equivocado que no se documenta vuelve a
aparecer en la siguiente auditoría.

---

## 5. Orden de ejecución

| Cuándo | US | Depende de |
|---|---|---|
| **jue 13** | **US-009** completa: migración, endpoint, almacén firmado, pantalla | nada de S4 |
| **vie 14, 09:00–13:00** | **US-023**: ola backend + `useChatStream.ts` + `asistente.vue` | US-009 ya escribió su parte de `main.py`/`config.py` |
| **vie 14, 13:00–17:00** | **US-028**: `ToolCallCard.vue`, historial, lámina de la guía | contrato de eventos y `types/chat.ts` en disco |
| **vie 14, 17:00–19:00** | **US-024**: `AvisoError.vue` y el subárbol `chat.error.*` | `ToolCallCard.vue` existente |
| **sáb 15 · dom 16** | **US-UX-07**: capturas, `a4_*.tex`, pre-validación, PDF | las siete pantallas navegables; **go/no-go de Gemini el sáb 15 a las 12:00**, con sus dos ramas declaradas |

El viernes es la única fecha con tres US encadenadas. La secuencia no es negociable: quien escribe
va antes que quien lee.

---

## 6. Pendientes que esta auditoría no cierra

| Pendiente | Quién lo cierra |
|---|---|
| La verificación línea a línea de las secciones 6 (plan de tests) de los cinco planes quedó a medias: la fase de parcheo se interrumpió | quien abra implementación de cada US, al leer su propia sección 6 |
| `docs/security.md` y `backend/app/core/permissions.py` siguen sin existir; el gate venció el 6-ago | US-016, antes de que US-023 escriba su fila |
| Las claves i18n en `en.json` no se han contrastado contra `es.json` para paridad de árbol | la primera US que toque i18n el jueves (US-009) |

---

> **Nota de procedencia.** Los cinco planes ya llevan sus notas fechadas de esta misma auditoría,
> aplicadas antes de que se escribiera este resumen. Este archivo no las repite: recoge lo que
> exige mirar los cinco a la vez, que es exactamente lo que ningún plan puede ver desde dentro.
