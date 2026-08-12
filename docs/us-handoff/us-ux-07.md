# Handoff US-UX-07 — Interfaces de alta fidelidad (A4)

**Estado**: planning
**Epic**: UX
**Sprint**: S4 · **Actividad**: A4 (dom 16-ago-2026), apartado 3 de la rúbrica: **prototipos, 50 % = 12.50 de 25 puntos**
**Rama**: `us-ux-07` desde **la punta de `us-024`**, última de la cadena del chat (corregido el 11-ago-2026: la ola A captura `/asistente` y `components/chat/`, que solo existen ahí). Una rama por US, commits locales encadenados, **sin PR** (discrepancia RU-11 declarada frente a `feature/E{epic}-US-XXX-{slug}`)
**SHA base**: punta de `us-024`; ancla del diff `git diff --name-only $(git rev-parse --short us-024)`
**Estimación**: 5 SP · **Días**: sáb 15 y dom 16 · **Estado esperado al cierre**: cerrada
**Plan**: [`docs/us-planning/us-ux-07.md`](../us-planning/us-ux-07.md)

> **Correccion fechada el 11-ago-2026 (auditoria cruzada).** Este handoff reclamaba escritura sobre `frontend/app/utils/navegacion.ts` (campo `alcance` de la ola B), prohibía en absoluto tocar `main_a4.tex` y no declaraba dueño de `frontend/package.json`. Se decide que en S4 **nadie escribe `navegacion.ts`** y esta US solo lo **lee** para la tabla ruta-rama y para el alcance publicado; que **US-UX-09 crea `main_a4.tex`** y esta US **añade únicamente sus propios `\input`** y sus propios `contenido/a4_*.tex`, sin tocar `a4_03_guia_estilos.tex` ni `a4_06_cierre.tex` ni reordenar líneas ajenas; y que **esta US es dueña única de `frontend/package.json`** en S4 para añadir Playwright. Porque las rutas `/exploracion/exportar` y `/asistente` ya existen desde US-001 y ninguna US de S4 añade rutas, de modo que abrir `navegacion.ts` solo crea un conflicto sin ganancia; porque una prohibición total sobre el envoltorio del PDF dejaba los `\input` de esta US dependiendo de otra US en el gate del domingo; y porque sin dueño declarado, `package.json` era el único archivo con dos candidatos a modificarlo el mismo fin de semana.

---

## Dominios y sub-tareas tocados

- [ ] backend
- [x] frontend — mínimo: **`frontend/package.json` (+ lockfile) para Playwright y dos archivos de prueba**. `frontend/app/utils/navegacion.ts` **no se escribe**: la matriz del 11-ago-2026 lo deja sin dueño en S4 y esta US solo lo **lee** para la tabla ruta-rama y para el alcance publicado. **Los locales no se tocan**: las tres etiquetas de alcance ya existen como `prototype.scope.*` y las resuelve `BotonPrototipo.vue`
- [ ] ml
- [ ] agent
- [ ] infra
- [ ] db
- [x] docs — seis `.tex` de A4, guion de capturas, figuras y `main_completo.tex`

**Sí se reparte.** Es la única US del sprint con olas paralelas reales, pero la cadena **captura → documento es secuencial y quien captura va primero**. La iteración del CA-6 añade una **segunda pasada de captura** (ola A') entre el documento base y la pre-validación.

| Ola | Cuándo | Subagente | Write-set exclusivo |
|---|---|---|---|
| **A** captura del antes | sáb 15, 10:00 → 12:00 | `frontend-builder` | `frontend/package.json` + `pnpm-lock.yaml` (**dueña única en S4**: añade `@playwright/test`) · `docs/entregables/capturas/guion_a4.md` · `capturas/capturas_a4.mjs` · `figuras/a4/antes/*.png` |
| **B** datos y contratos | sáb 15, 12:00 → 16:00 | `frontend-builder` | `frontend/test/rutaRama.spec.ts` · `frontend/test/alcancePrototipos.spec.ts` · `contenido/a4_05_alcance.tex`. **Sin locales y sin `navegacion.ts`**: el alcance publicado se copia del valor que el código ya declara |
| **C** documento base | sáb 15, 12:00 → 20:00 | `deliverable-writer` | `contenido/a4_00_preliminares.tex` · `a4_01_metodo_prototipado.tex` · `a4_02_prototipos.tex` |
| **A'** iteración y recaptura | sáb 15, 20:00 → 22:00 | `frontend-builder` | **conjunto elegible cerrado**: `app/components/comun/**` · `app/layouts/**` · `app/pages/{index,inicio,exploracion/index,gobierno,administracion}.vue` · `figuras/a4/despues/*.png`. Fuera: `components/chat/**`, `components/exportacion/**`, `components/guia/**`, `pages/asistente.vue`, `pages/exploracion/exportar.vue`, `pages/guia.vue`, `pages/acceso.vue` |
| **D** pre-validación y cierre | dom 16, 09:00 → 16:00 | `deliverable-writer` | `contenido/a4_04_prevalidacion.tex` · `a4_07_anexo.tex` · `docs/entregables/main_completo.tex` |
| **E** compilación y revisión cruzada | dom 16, 16:00 → 20:00 | `deliverable-writer` | ninguno nuevo; corrige dentro de lo ya propio y, si faltara, **añade a `main_a4.tex` únicamente los `\input` de los seis `.tex` de esta US**, al final del bloque y sin reordenar ni tocar las líneas de US-UX-09 |

B y C corren en paralelo porque sus write-sets son disjuntos. A' no puede empezar antes de que A haya archivado las siete capturas del antes.

**Gate del sáb 15, 12:00 — go/no-go de Gemini.** El calendario de A y de B depende de él, y las dos ramas quedan declaradas de antemano:

- **GO**: `/asistente` responde con el agente real. La ola A captura los cuatro estados reales de `tool_call` como secuencia, las cuatro celdas de categoría (b) pasan a (a) y la ola B publica esas pantallas con el alcance que el código declara.
- **NO-GO**: US-023 sirve el guion de demo y la pantalla muestra su franja de honestidad (`chat.demo.scriptedNotice`, propiedad de US-023). Se aplica la válvula §26.5-1: los cuatro estados entran como **galería** en vez de secuencia, la celda de secuencia se declara roadmap y **toda captura de `/asistente` conserva la franja visible** — recortarla sería presentar un guion como respuesta viva.

En ambas ramas la hora de corte es la misma: pasadas las 12:00 no se espera más, se captura lo que haya y la desviación se anota.

---

## Zonas sensibles

| Archivo | Por qué |
|---|---|
| `docs/entregables/main_a4.tex` | **Lo crea US-UX-09**, ya compila y trae `\IfFileExists` para los seis archivos de esta US. Esta US **solo puede añadir sus propios `\input`** si alguno faltara: añade al final, no reordena y no toca ninguna línea de US-UX-09. En la práctica no debería hacer falta ni una línea |
| `contenido/a4_03_guia_estilos.tex` · `a4_06_cierre.tex` | Propiedad exclusiva de US-UX-09. Se leen para no repetir contenido; **no se escriben** en ningún caso, ni siquiera para corregir una referencia |
| `frontend/package.json` · `pnpm-lock.yaml` | **Dueña única en S4: esta US**, y solo para añadir `@playwright/test` (ola A). Ninguna otra US del sprint añade dependencias de frontend; si alguien más las necesita, se coordina antes del sáb 10:00 |
| `docs/entregables/estilo/uxdoc.sty` | **Congelado** por decisión del 11-ago-2026. A1, A2 y A3 ya compilan contra él. El estilo del portal y el del informe son sistemas separados |
| `estilo/a4_tokens.tex` · `generar_tokens_a4.py` | Los emite US-UX-09 desde `design/sistema.py`. Derivación en un solo sentido: nada fluye hacia atrás |
| `frontend/app/pages/asistente.vue` · `app/composables/useChatStream.ts` · `app/types/chat.ts` | Propiedad de **US-023** (la página la crea el vie 14 por la mañana). Esta US los **lee y captura**; no monta componentes dentro ni reescribe la página |
| `frontend/app/components/chat/**` | `ToolCallCard.vue` e `HistorialConversacion.vue` son de **US-028** (el estado `error` de la tarjeta también); `AvisoError.vue` es de **US-024**. Solo lectura y captura |
| `frontend/app/utils/navegacion.ts` | **Nadie lo escribe en S4.** `/exploracion/exportar` y `/asistente` existen desde US-001 y ninguna US del sprint añade rutas. Esta US **lo LEE, no lo escribe**: de ahí salen la tabla ruta-rama del CA-3 y los valores de `alcance` que publica el CA-5. Cualquier edición es invasión |
| `frontend/i18n/locales/{es,en}.json` | Reparto por subárbol: `export.*` y `nav.branch.exploreExports`/`nav.facets.items.exportHistory` de US-009; `chat.page.*`/`chat.controls.*`/`chat.demo.*`/`chat.stream.*` (incluido el vocabulario cerrado `chat.stream.step.*`) de US-023; `chat.error.*` de US-024; `chat.toolCall.*` y `guide.plate.toolCall` de US-028. **Esta US no lo toca**: `prototype.scope.{withData,withoutData,roadmap}` ya existen en los dos locales y abrir `scope.withData` sería una segunda redacción de la misma etiqueta |
| `frontend/app/components/guia/**` · `frontend/test/laminas.spec.ts` | De **US-UX-09**; US-028 añade una lámina y ajusta el conteo. Esta US no toca ni la guía ni su prueba: `/guia` está fuera del conjunto elegible de la ola A' |
| `backend/app/core/permissions.py` · `docs/security.md` | De **US-016**, y **no existen en `f807a18`**. El estado «sin permiso» de cinco pantallas depende de sus scopes: si al sáb 15 10:00 no están, la celda se declara bloqueada en la matriz 7×4 y baja a categoría (c) |
| `db/schema.sql` · `backend/**` · `tests/backend/**` | Ajenos por completo. `schema.sql` es de US-009, única con migración en S4; `tests/backend/test_chat_error.py` es de US-024. Esta US no escribe una sola línea de backend |
| `figuras/a4/antes/` | **Irrecuperable.** Si la captura del antes se toma después de tocar la interfaz, el CA-6 se cae y no hay forma de rehacerlo |

---

## Contratos con otras US

**Lo que esta US espera, con la hora en que debe estar en disco** (orden de ejecución fijado el 11-ago-2026):

| Cuándo | Quién | Qué entrega que esta US necesita | Qué hace esta US con ello |
|---|---|---|---|
| **jue 13, completa** | **US-009** | `/exploracion/exportar` con su franja `export.demo.notice`, la migración y `db/schema.sql` | La captura como una de las siete pantallas. No toca `export.*` ni el esquema |
| **vie 14, 09:00 → 13:00** | **US-023** | `pages/asistente.vue`, `composables/useChatStream.ts`, `types/chat.ts`; subárboles `chat.page.*`, `chat.controls.*`, `chat.demo.*` y `chat.stream.*`, incluido el vocabulario cerrado `chat.stream.step.*` | Lee y captura para el CA-1c. No monta componentes en la página ni define claves de paso |
| **vie 14, 13:00 → 17:00** | **US-028** | `ToolCallCard.vue` con sus cuatro estados —el estado `error` incluido— e `HistorialConversacion.vue`; una lámina nueva en la guía (`guide.plate.toolCall`) con el conteo de `laminas.spec.ts` ya ajustado | Rellena celdas de categoría (b) de la matriz 7×4. No toca la guía ni su prueba; **US-028 no añade dependencias**, Playwright es de esta US |
| **vie 14, 17:00 → 19:00** | **US-024** | `components/chat/AvisoError.vue` y `tests/backend/test_chat_error.py`; consume `chat.stream.step.*` de US-023 y no define claves de paso propias | Captura el aviso de error de turno. No lo escribe ni duplica su estado |
| **vie 14, 20:00** | **cadena del chat** | Congelamiento de `frontend/app/`, una hora después del cierre de US-024 | Verifica con `git log --since`; lo que llegue después se captura igual y la desviación se anota |
| **antes del sáb 15** | **US-016** | `backend/app/core/permissions.py` y `docs/security.md`, que **no existen en `f807a18`** | El estado «sin permiso» de cinco pantallas depende de sus scopes: si al sáb 10:00 no están, la celda se declara bloqueada y baja a categoría (c) |
| **en paralelo, S4** | **US-UX-09** | `main_a4.tex`, `a4_03_guia_estilos.tex`, `a4_06_cierre.tex`, `a4_tokens.tex` y `tokens.generated.ts` | Consume sus tokens a través de la interfaz ya construida; añade **solo sus propios `\input`** y sus seis `contenido/a4_*.tex`. Cero archivos compartidos en escritura salvo esos `\input` |
| **§26.3 del plan** | — | Estados de US al cierre del viernes | Fuente de la tabla de alcance del CA-5; todo cambio posterior al vie 14 se refleja en `a4_05_alcance.tex` antes de la ola E |

**Lo que esta US entrega a otras**: nada en S4. Ninguna US del sprint depende de sus archivos, y `@playwright/test` queda disponible en `frontend/package.json` sin que nadie más lo requiera. Su salida es el PDF de A4, las dos specs nuevas y las figuras del antes y el después.

**Dependencias sin hora fija**: US-025 y US-029 (drill-down y estado compartido del tablero, válvula §26.5-2: si no hay tres niveles se entregan dos y se declara) · US-026 y US-027 (overlay de linaje y bitácora; la bitácora es una de las dos tareas heredadas de la prueba de árbol de A3) · US-017 / US-018 / US-019 (scopes de las pantallas restantes). Todas se capturan, ninguna se implementa aquí.

---

## Decisiones tomadas en planeación

1. **`main_a4.tex` es de US-UX-09 y esta US solo añade sus propios `\input`** (corregido el 11-ago-2026). Ya existe con `\IfFileExists` para `a4_00`, `a4_01`, `a4_02`, `a4_04`, `a4_05` y `a4_07`, así que los seis archivos de esta US entran solos y lo normal es no escribir ni una línea. Si alguno faltara, la ola E lo añade al final del bloque, sin reordenar ni tocar las líneas de US-UX-09: un conflicto de merge en el envoltorio del PDF cuesta el entregable entero, pero depender de otra US para un `\input` propio en el gate del domingo cuesta lo mismo.
2. **«Desplegadas» se cumple como «navegables end to end en el stack del producto», con capturas locales reproducibles a viewport fijo 1440×900.** La URL pública de GCP se cita solo si está viva al capturar. La evidencia no queda a merced de la infraestructura.
3. **Playwright es opcional, el guion no.** Plan A: `pnpm add -D @playwright/test` con corte a los 10 minutos el sáb 10:00. Plan B: captura manual con el mismo guion escrito. El valor del guion es fijar qué se captura, en qué orden, con qué sesión y con qué estado. **Esta US es la dueña única de `frontend/package.json` en S4** y esa es la única dependencia que añade; si se cae al plan B, el `package.json` queda sin tocar.
4. **La captura del antes se toma el sáb 15 a las 12:00, de las siete pantallas, antes de aplicar ningún hallazgo.** A esa hora todavía no se sabe cuál cambiará, y una vez tocada la interfaz el antes se perdió.
5. **Las 28 celdas de la matriz 7×4 se etiquetan (a) implementada y capturable, (b) la produce otra US de S4, (c) documentada como especificación sin código.** Conteo actual: 7 en (a), 11 en (b), 10 en (c), **cero vacías**. Esa matriz es el backlog real del CA-4.
6. **El CA-5 se entrega con dos tablas**: tres estados por pantalla (lo que pide la rúbrica) y una traducción explícita de las seis categorías de §26.3 al esquema de tres, para que ninguna US quede sin declarar. Mapeo: cerrada y cerrada degradada → navegable con datos; demostrada no productiva → navegable sin datos; roadmap, congeladas y de S5 → roadmap.
7. **Los 8 evaluadores son prototipos sintéticos y el PDF lo dice en su primer párrafo.** Presentarlos como personas sería fabricar un resultado; el SUS con humanos es de A5.
8. **Las nueve facetas transversales se auditan, no se corrigen.** `preview` y `dataQuality` no tienen subrama marcada en `MODULOS`; se resuelven como accesos cruzados desde `/exploracion` y se documentan. A3 ya se entregó y su arquitectura no se reescribe para cuadrar una tabla.
9. **Solo dos archivos de prueba nuevos con una prueba cada uno**, `rutaRama.spec.ts` (la tabla ruta-rama del `.tex` cubre las 16 subramas) y `alcancePrototipos.spec.ts` (el alcance publicado en el PDF coincide con `PROTOTIPOS`). Las otras cuatro que el plan traía se retiraron el 11-ago-2026: una era tautológica por la construcción de `RUTAS_CONTRATO` y tres ya existen en `navegacion.spec.ts:85`, `navegacion.spec.ts:158` y `pantallas.spec.ts:132`. El comando es `pnpm -C frontend test -- rutaRama`, no `pnpm test -- contratos`: el argumento filtra por nombre de archivo.
10. **Orden de válvulas de §26.5, con hora**: galería de estados (sáb 12:00) → drill-down a dos niveles (sáb 16:00) → administración a un nivel (sáb 18:00) → exportación fuera del set, seis prototipos (dom 12:00). No negociables: las cinco interfaces de la arquitectura de A3, la iteración documentada y la guía de estilos completa.

---

## Pendientes al abrir implementación

1. **Confirmar el estado real de `/asistente` y de `components/chat/` a las 10:00 del sáb 15.** De ello dependen cuatro celdas de la matriz y el CA-1c.
2. **Verificar que el congelamiento del vie 14 20:00 se cumplió** (`git log --since` sobre `frontend/app/`). Si alguna pantalla cambió después, la captura del antes se toma igual pero se anota la desviación.
3. **Leer el campo `alcance`** de las siete entradas de `PROTOTIPOS` tras el congelamiento y publicar **ese** valor. Hoy las siete dicen `navegable-sin-datos` y nadie las reescribe en S4, así que esa es la verdad que copia `a4_05_alcance.tex` y la que verifica `alcancePrototipos.spec.ts`. Si el estado real de una pantalla al cierre del viernes no coincide con su etiqueta en código, la divergencia se documenta como nota al pie del `.tex` y se abre pendiente para S5: **no se edita `navegacion.ts`**.
4. **Elegir el hallazgo del CA-6 antes de las 20:00 del sábado.** Debe ser barato de aplicar y visible en la captura: si no se ve en la imagen, la iteración no es verificable.
5. **Confirmar si la URL pública de US-003 está viva** para decidir la línea del `a4_01` sobre el despliegue.
6. **Comprobar que `FranjaAlcance.vue` aparece en todas las capturas.** Ninguna captura sin franja entra al PDF (R10).
7. **Nombres y perfiles de los 8 evaluadores prototipo**: se heredan de A3; localizarlos en `docs/entregables/contenido/a3_02_card_sorting.tex` y reutilizar los mismos, no inventar otros.
8. **Reservar el bloque dom 16 16:00 → 20:00 solo para compilar y revisar.** El gate de entrega es a las 20:00, no a las 23:59.
