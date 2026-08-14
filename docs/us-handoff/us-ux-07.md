# Handoff US-UX-07 — Interfaces de alta fidelidad (A4)

**Estado**: testing
**Epic**: UX
**Sprint**: S4 · **Actividad**: A4 (dom 16-ago-2026), apartado 3 de la rúbrica: **prototipos, 50 % = 12.50 de 25 puntos**
**Rama**: `us-ux-07` desde **la punta de `us-024`**, última de la cadena del chat (corregido el 11-ago-2026: la ola A captura `/asistente` y `components/chat/`, que solo existen ahí). Una rama por US, commits locales encadenados, **sin PR** (discrepancia RU-11 declarada frente a `feature/E{epic}-US-XXX-{slug}`)
**SHA base**: `d658be8` (punta de `us-ux-07` al abrir implementacion, dos commits por delante de `us-024` = `eb6a05c`: `7c925dd` matriz+ADR-003 y `d658be8` correccion de `make tokens`). Ancla del diff de todas las fases siguientes: `git diff --name-only d658be8`. **QA no usa `HEAD~N`.**
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

---

# Registro de implementación — 14-ago-2026

**Estado**: testing · **SHA base del diff**: `d658be8` · **Rama**: `us-ux-07`, sin PR

## Cómo se ejecutó realmente

El plan repartía la US en seis olas sobre subagentes. Se lanzaron cuatro en paralelo con write-sets
disjuntos y **se cancelaron a petición del usuario**: cada subagente pedía permiso por comando y el
ruido no compensaba el paralelismo. El trabajo se rehízo de forma secuencial desde el orquestador.
Dos olas alcanzaron a dejar producto antes de la cancelación y se conservó: el guion Node de la ola A
y el arreglo de la ola A'. Lo demás se escribió de cero.

Las capturas no las tomó el guion Node sino el **navegador del MCP de Playwright**, por decisión del
usuario. El guion existe, corre y produce las siete capturas —se verificó contra un directorio
temporal, 7/7—, pero el conjunto archivado es el del MCP, tomado a escala 1. Los dos conjuntos, antes
y después, salieron del mismo instrumento y con el mismo viewport, que es lo que hace comparable la
pareja.

## Gate del go/no-go de Gemini: NO-GO, y es estructural

`backend/app/services/proveedores/` contiene un solo proveedor, `guionizado.py`, y `backend/.env.local`
trae `GEMINI_API_KEY=pendiente-us-020`. No es una demora: no hay proveedor real que activar. Se aplicó
la válvula §26.5-1 —los cuatro estados de `tool_call` como galería y no como secuencia— y toda captura
de `/asistente` conserva visible la franja `chat.demo.scriptedNotice`.

## Archivos

### Creados

| Archivo | Qué es |
|---|---|
| `docs/entregables/capturas/guion_a4.md` | Protocolo de captura reproducible por otra persona |
| `docs/entregables/capturas/capturas_a4.mjs` | Guion Node; deriva el plan de `PROTOTIPOS`, no de una lista escrita |
| `docs/entregables/contenido/a4_00_preliminares.tex` | Introducción y nota de herramienta del CA-7 |
| `docs/entregables/contenido/a4_01_metodo_prototipado.tex` | Método, protocolo de captura y derivación en un solo sentido |
| `docs/entregables/contenido/a4_02_prototipos.tex` | Siete pantallas, tabla ruta-rama y matriz 7x4 |
| `docs/entregables/contenido/a4_04_prevalidacion.tex` | Ocho evaluadores, dos tareas heredadas e iteración con antes y después |
| `docs/entregables/contenido/a4_05_alcance.tex` | Tabla de alcance por pantalla y por US |
| `docs/entregables/contenido/a4_07_anexo.tex` | Protocolo, inventario de figuras y trazabilidad de criterios |
| `frontend/test/rutaRama.spec.ts` | Verifica que la tabla del PDF publica las 20 ramas del contrato |
| `frontend/test/alcancePrototipos.spec.ts` | Verifica que el alcance del PDF coincide con `PROTOTIPOS` |
| `docs/entregables/figuras/a4/antes/*.png` | 7 capturas del antes |
| `docs/entregables/figuras/a4/despues/*.png` | 7 capturas del después más `4_asistente_resultado.png` |
| `docs/semana_4/Entregable Actividad 4_equipo_8.pdf` | El PDF con el nombre que pide la actividad |

### Modificados

| Archivo | Qué cambió |
|---|---|
| `frontend/app/layouts/portal.vue` · `acceso.vue` · `default.vue` | El arreglo del CA-6: `max-w-none` sobre la franja de alcance |
| `frontend/package.json` · `pnpm-lock.yaml` | `@playwright/test` como dependencia de desarrollo |
| `docs/entregables/main_completo.tex` | Portadilla de la parte IV, los ocho input de A4, «Sobre este documento», portada, pdftitle y la carga de `estilo/a4_tokens` |

### No tocados, verificado contra `d658be8`

`main_a4.tex` · `app/utils/navegacion.ts` · `i18n/locales/{es,en}.json` · `a4_03_guia_estilos.tex` ·
`a4_06_cierre.tex` · `estilo/uxdoc.sty` · `backend/` · `ml/` · `db/` · `tests/`. Los seis con
`git diff --name-only d658be8 | grep -c` igual a 0.

## Decisiones

1. **El hallazgo del CA-6 se midió, no se supuso.** La franja de alcance salía con `max-width: 68ch`
   —455 px dentro de una columna de 1193— porque se compone como párrafo y la hoja global aplica la
   medida de lectura a todo párrafo. Afectaba a las siete pantallas, era barato y se ve en la imagen,
   que es la condición para que la iteración sea verificable. Verificado tras el cambio: 1193 px, y la
   caja baja de 48 a 33 px de alto porque el texto pasa de dos líneas a una.
2. **El arreglo va en los tres layouts y no en `FranjaAlcance.vue`.** El componente vive en
   `components/nav/`, fuera del conjunto elegible cerrado de la ola A'. La clase `max-w-none` funciona
   por dos vías a la vez: la regla del sistema se excluye a sí misma con una negación sobre las clases
   de anchura máxima, así que la clase desactiva la regla **y** fija el valor, sin depender de ganar un
   empate de especificidad. `error.vue` monta la misma franja y queda sin arreglar: no es un layout y
   está fuera del conjunto. Pendiente declarado.
3. **`createRequire` fuera del guion.** La justificación escrita —que bajo import dinámico `chromium`
   cae en el export por omisión— se comprobó falsa: `@playwright/test` publica `index.mjs` como entrada
   ESM y expone `chromium` como export con nombre. Se carga con `await import()` sobre una URL de
   archivo hacia `frontend/node_modules`, porque el guion vive bajo `docs/` y ahí no hay paquetes.
4. **El alcance publicado es el del código, no el observado.** Las siete entradas de `PROTOTIPOS` dicen
   `navegable-sin-datos` y varias pantallas muestran más que eso. Se publica el literal y la
   divergencia se declara en el propio `.tex`: si el documento calificado y la aplicación pueden
   diverger por una edición de última hora, la tabla deja de ser evidencia. `navegacion.ts` no se tocó.
5. **La etiqueta impresa es «En hoja de ruta», no «Roadmap».** Es la que el producto usa en
   `prototype.scope.roadmap`, y la prueba compara contra ella. Publicar un vocabulario distinto del de
   la interfaz habría creado una segunda redacción de la misma etiqueta.
6. **El recuento de la matriz 7x4 es 6 / 12 / 10, no 7 / 11 / 10.** La cuenta del plan incluía una
   octava fila para `/exploracion/tableros`, que es zona de la pantalla de exploración y no un
   prototipo: 8 filas por 4 estados son 32 celdas, no 28. Se publica el recuento sobre las siete
   pantallas y la corrección queda escrita en el `.tex`.
7. **`main_completo.tex` necesitaba cargar `estilo/a4_tokens`.** Reutiliza `a4_03_guia_estilos.tex`,
   que usa la versión y la fecha de la guía, y sin esa línea fallaba con ocho secuencias de control no
   definidas. Se añadió al preámbulo del acumulado; `main_a4.tex` no se tocó.
8. **Una octava figura para el CA-1c.** `4_asistente_resultado.png` documenta un turno resuelto con su
   tarjeta de llamada a herramienta y el campo del catálogo citado. Vive solo en `despues/` y no forma
   pareja: documenta un estado de la conversación, no una versión distinta de la pantalla.

## Lo que quedó desactualizado del «Estado» de las guías de carpeta

> **Corregido en QA, 14-ago-2026.** Esta sección se escribió antes de actualizar las guías y
> describía un estado que ya no existe; se reescribe con lo que quedó, y con lo que faltaba.

- **`frontend/AGENTS.md`**: **ya actualizado en este mismo diff.** Declara **42 `*.spec.ts` y tres
  auxiliares**, que es la cuenta real del directorio, describe `@playwright/test` como dependencia
  de desarrollo y describe las dos pruebas que **leen archivos `.tex` del directorio de
  entregables**. La redacción anterior de este renglón —«dice 38, ahora son 40, la suite da 42
  porque la guía excluye auxiliares»— no cerraba: hay 42 `*.spec.ts` y tres auxiliares, y no hay
  dos números que conciliar.
- **`docs/AGENTS.md`**: **actualizado en QA** (hallazgo QA-06). Decía que de A4 solo existían
  `a4_03_guia_estilos.tex` y `a4_06_cierre.tex` y que `semana_4/` no tenía PDF de entrega; ahora
  declara los ocho `.tex`, el PDF, la carga de `estilo/a4_tokens` en `main_completo.tex` y el
  artefacto nuevo de capturas. Su «No tocar» gana un renglón para `figuras/a4/{antes,despues}/`,
  que salen de `capturas_a4.mjs` y no de `generar_figuras*.py`: recapturar, jamás retocar, y
  `antes/` es irrecuperable. `docs/CLAUDE.md` copiado encima, espejo verificado.

## Verificación

| Comprobación | Resultado |
|---|---|
| `make check` | exit 0. Sin fugas, mapa de permisos al día e idempotente |
| `pnpm --dir frontend test` | **42 archivos, 798 pruebas, todas en verde**. Cobertura de líneas 93.61 % contra un umbral de 50 |
| `pnpm --dir frontend lint` y `typecheck` | exit 0 |
| `latexmk -xelatex main_a4.tex` | exit 0, **61 páginas**, 0 referencias sin resolver, 0 desbordes |
| `latexmk -xelatex main_completo.tex` | exit 0, **208 páginas**, 0 referencias sin resolver |
| Hexadecimales en los seis `.tex` propios | 0 |
| `node capturas_a4.mjs` contra directorio temporal | **7/7 capturas escritas** |
| Pares antes/después con nombre idéntico | 7 de 7 |

### Flujo recorrido en el navegador, no solo en pruebas

- Índice público: los siete prototipos publican «Navegable sin datos» y su perfil, idéntico a lo que
  la tabla del PDF declara.
- Guarda sin sesión: `/administracion` devuelve a `/acceso`.
- Rol insuficiente: `operativo` sobre `/administracion` responde 403 y dibuja el estado «sin permiso»
  con la URL intacta, sin control de reintento y con una sola salida al espacio propio.
- Asistente: pregunta enviada, tarjeta de llamada a herramienta resuelta en 0.3 s, tabla devuelta,
  cifra 3.42 % y **fuente del catálogo citada** (`catalogo.creditos.morosidad_cartera`). La respuesta
  escrita repite la procedencia. La regla anti-alucinación se sostiene en vivo.
- Franja de alcance presente en las siete pantallas (R10).

## Pendientes

1. **`error.vue` conserva la franja con la medida de lectura.** Fuera del conjunto elegible de la ola
   A'. El arreglo es la misma clase.
2. **El selector de modo de color arranca en oscuro** en un perfil de navegador nuevo, y la guía de
   estilos declara el modo oscuro fuera de alcance. La primera impresión del prototipo ocurre en una
   paleta que el documento dice no haber verificado. Registrado como hallazgo no atendido en
   `a4_04_prevalidacion.tex`; el protocolo de captura fija el modo claro de forma explícita.
3. **Las etiquetas de `PROTOTIPOS[i].alcance` están desfasadas** respecto de lo que las pantallas
   muestran. Corrección para S5, cuando el contrato de navegación tenga US dueña.
4. **Divergencia de nombre de rol**: la sección 4 del plan escribe `administrador` y el código usa
   `admin` (`ROLES` en `app/utils/sesion.ts` y el cuerpo de `POST /api/auth/demo`). Manda el código.
5. ~~**El contenedor `karisma-data-web-1` sirve una imagen anterior** a los tres últimos commits.~~
   **Resuelto el 14-ago-2026.** La imagen se reconstruyó con `docker compose build web` y el
   contenedor se recreó con `docker compose up -d web`. Verificado en el navegador contra el puerto
   3000: la clase `max-w-none` está en el marcado servido y la franja mide 1440 px de ancho por 33 de
   alto, es decir, el arreglo del CA-6 viaja en la imagen. `scripts/smoke_rutas.sh` da **10 de 10
   rutas en verde**, con la franja de alcance presente en todas, el 403 con estado sin permiso para
   `operativo` y la sesión de demostración operativa. Las capturas del entregable se siguen tomando
   contra `pnpm dev` del host, que es lo que el guion documenta.
6. **El PDF no se ha subido a Canvas.** El archivo con el nombre exigido está en `docs/semana_4/`.
7. **Sin `git commit`**: la rama queda lista y el commit espera visto bueno.

---

# Registro de QA — 14-ago-2026

**Estado**: testing · **Ancla del diff**: `git diff --name-only d658be8` · **Rama**: `us-ux-07`, sin PR

Pruebas manuales: [`docs/manual-test/us-ux-07.md`](../manual-test/us-ux-07.md).

## Gates

| Comprobación | Resultado |
|---|---|
| `make check` | **exit 0**. eslint, typecheck, gitleaks sin fugas, CA-7b en verde, mapa de permisos al día e idempotente |
| `make test` | **exit 0**. Frontend **42 archivos, 798 pruebas, todas en verde**; cobertura de líneas **93.61 %** contra un umbral de 50. Backend sin cambios: el gate de 70 % queda intacto porque el diff no toca `backend/` ni `ml/` |
| `pnpm audit --audit-level=high` | **0 hallazgos** de severidad alta o crítica; 1 de severidad baja, preexistente |
| Archivos de «No tocar» tocados | **0 de 12** comprobados uno a uno contra `d658be8`: `main_a4.tex`, `navegacion.ts`, los dos locales, `a4_03`, `a4_06`, `uxdoc.sty`, `a4_tokens.tex`, `main.css`, `tokens.generated.ts`, `permisos.generated.ts`, `db/schema.sql` |
| `backend/` · `ml/` · `db/` · `tests/` | **0 archivos** en el diff |
| Líneas ❌ de `frontend/AGENTS.md` y `docs/AGENTS.md` | Sin violaciones: cero cadenas visibles en plantilla, cero hexadecimales en los seis `.tex` propios, cero tiempo futuro, cero emojis, `main.css` intacto, sin `routeRules` con `swr`, sin tocar entregables calificados de A1 a A3 |
| Espejos `AGENTS.md` / `CLAUDE.md` de `frontend/` | Byte-idénticos |
| Identificadores de nube por valor | Cero en los seis `.tex`, en el guion de captura y en los PDF nuevos. La única mención de `karisma-data-web-1` es el nombre local del contenedor de Compose, no un identificador de proyecto |

## Criterios de aceptación

| CA | Estado | Evidencia |
|---|---|---|
| CA-1 · siete prototipos navegables | **cumple** | `PROTOTIPOS.length === 7`; `smokeRutas.spec.ts` en verde; siete figuras en `figuras/a4/despues/` |
| CA-1b · drill-down y overlay de linaje | **cumple con declaración** | Capturados en el estado que existe y declarados en la tabla de alcance |
| CA-1c · asistente con los cuatro estados y Stop | **cumple degradado, válvula §26.5-1** | Gate NO-GO estructural: solo existe el proveedor `guionizado.py`. Galería en vez de secuencia y franja de honestidad visible en toda captura de `/asistente` |
| CA-2 · derivación en un solo sentido | **cumple** | `grep -nE '#[0-9A-Fa-f]{6}'` sobre los seis `.tex` propios da 0 |
| CA-3 · cada ruta anclada a una rama | **cumple** | `rutaRama.spec.ts` compara las 20 identidades de `MODULOS` contra la tabla acotada por `% tabla-ruta-rama:inicio/fin` |
| CA-4 · cuatro estados no felices por pantalla | **cumple, con recuento corregido** | Matriz de 7 × 4 = 28 celdas, ninguna vacía. 6 / 12 / 10, no el 7 / 11 / 10 del plan: la cuenta anterior incluía una octava fila para los tableros, que son zona de exploración y no prototipo. La corrección está escrita en el `.tex` |
| CA-4b · carga sin desplazamiento de maquetación | **cumple como inspección declarada** | Subsección propia que declara el método y su ausencia de instrumento. No hay métrica CLS en el stack, y el `.tex` lo dice en vez de publicar una cifra sin origen |
| CA-5 · tabla de alcance de tres estados | **cumple** | Cuatro tablas en `a4_05_alcance.tex`; `alcancePrototipos.spec.ts` compara las siete filas contra `PROTOTIPOS[i].alcance` por su etiqueta impresa |
| CA-6 · pre-validación con iteración | **cumple** | Ocho evaluadores prototipo declarados sintéticos en el primer párrafo, dos tareas heredadas del árbol de A3, par antes/después sobre `/exploracion`. **R3b respetado**: `/asistente` queda fuera del par |
| CA-7 · nota de herramienta | **cumple** | Sección propia en `a4_00_preliminares.tex` con OEA 2.2 nombrado |
| CA-8 · PDF entregado a tiempo | **pendiente de acción humana** | El archivo con el nombre exigido está en `docs/semana_4/`; no se ha subido a Canvas |
| CA-9 · portadilla y «Sobre este documento» | **cumple** | `\uxparte{IV}` en la línea 102 de `main_completo.tex`, ocho `\input` de A4, portada y `pdftitle` actualizados |
| CA-10 · QA gate del repo | **cumple** | `make check` y `make test` en verde |

## Hallazgos

Ninguno bloqueante. Los cuatro primeros tienen su procedimiento en `docs/manual-test/us-ux-07.md`.

1. **QA-01 · El arreglo del CA-6 no tiene prueba que lo sostenga.** `max-w-none` vive en tres
   plantillas y ninguna de las 798 pruebas lo afirma; `pantallas.spec.ts:223` verifica que la franja
   está montada, no su anchura. Además `layouts/acceso.vue` y `layouts/default.vue` **no aparecen en
   el informe de cobertura**: el umbral no los mira. El defecto concreto: una limpieza de clases en
   cualquiera de los tres layouts deja la suite en verde y a la vez invalida las figuras
   `antes/despues/2_exploracion_normal.png`, que son evidencia de un documento calificado. Es el
   hallazgo de mayor consecuencia del diff y el más barato de cerrar: una prueba de montaje por
   plantilla que afirme la clase sobre `[data-franja-alcance]`.
2. **QA-02 · `error.vue` conserva la medida de lectura.** Cuarto punto de montaje de
   `FranjaAlcance` y el único sin corregir, porque no es una plantilla y quedó fuera del conjunto
   elegible de la ola A'. Ya estaba declarado como pendiente; se confirma. La pantalla de error es,
   además, uno de los cuatro estados no felices que el entregable declara.
3. **QA-03 · El modo de color arranca en oscuro en un perfil nuevo.** Ya registrado como hallazgo no
   atendido en `a4_04_prevalidacion.tex`; se confirma y queda con procedimiento de verificación.
4. **QA-04 · El guion de captura y el conjunto archivado no coinciden en escala.**
   `CAPTURAS_ESCALA` vale 2 por omisión y el conjunto archivado se tomó a escala 1 con el MCP.
   `guion_a4.md` declara las dos cosas en dos filas distintas, la 57 y la 147, sin decir que
   reproducir el archivado exige `CAPTURAS_ESCALA=1`. Un protocolo cuyo propósito es la
   reproducibilidad por otra persona debería fijarlo en el comando.
5. **QA-05 · La sección «Lo que quedó desactualizado» de este handoff ya no describe el
   repositorio.** Afirma que `frontend/AGENTS.md` declara 38 specs y no menciona Playwright; hoy
   declara 42, describe `@playwright/test` y describe las dos pruebas que leen `.tex`. Su
   aritmética tampoco cierra: hay exactamente 42 `*.spec.ts` y tres auxiliares, que es justo lo que
   la guía dice, así que no hay dos números que conciliar.
6. **QA-06 · `docs/AGENTS.md` sí quedó desactualizado, y no se corrigió.** Sigue diciendo que de A4
   «hoy solo existen `a4_03_guia_estilos.tex` y `a4_06_cierre.tex`» y que `semana_4/` no tiene PDF.
   Su lista de «No tocar» cubre `figuras/*.png` como salida de `generar_figuras*.py`, y ahora existe
   `figuras/a4/**`, que sale de `capturas_a4.mjs` y se edita por otro camino. Asimetría con
   `frontend/AGENTS.md`, que sí se puso al día en este mismo diff.
7. **QA-07 · `runCapture` recarga Playwright en cada trabajo.** `loadPlaywright()` se llama una vez
   por captura, siete veces por corrida, cuando `main()` ya lo cargó. El `import` está cacheado, así
   que el costo real es un `existsSync`; es limpieza, no defecto.

## Fuera del alcance de esta US, presente en el árbol de trabajo

Sin rastrear y **sin tocar**, por indicación del usuario: `context/planeacion_proyecto_mvp.md`,
`docs/us-planning/us-entrega-a4.md`, `docs/us-handoff/us-entrega-a4.md` y
`docs/entregables/figma/*.pdf`. Son trabajo futuro y la consolidación de la entrega, no producto de
US-UX-07, y por eso no aparecen en su tabla de archivos creados.

Una advertencia sobre el último: `docs/entregables/figma/` son **26 MB** de PDF sin rastrear y sin
regla en `.gitignore`, de modo que un `git add -A` los deja en la historia de un repositorio
público y sin reescritura posterior. No traen identificadores de nube, verificado, pero el peso es
permanente. Conviene decidir explícitamente si entran, y con qué regla, antes del commit.

## Correcciones de QA — 14-ago-2026

| Hallazgo | Resolución | Archivos |
|---|---|---|
| QA-01 · el arreglo del CA-6 sin prueba | **corregido** | `frontend/test/FranjaAlcance.spec.ts` |
| QA-02 · `error.vue` con la medida de lectura | **corregido** | `frontend/app/error.vue` |
| QA-03 · paleta de la primera impresión | **no es defecto; se reclasifica** | ninguno |
| QA-04 · escala del guion contra la del conjunto archivado | **corregido** | `capturas_a4.mjs` · `guion_a4.md` |
| QA-05 · sección desactualizada de este handoff | **corregido** | este archivo |
| QA-06 · `docs/AGENTS.md` desactualizado | **corregido** | `docs/AGENTS.md` · `docs/CLAUDE.md` |
| QA-07 · Playwright recargado por trabajo | **corregido** | `capturas_a4.mjs` |

**QA-01.** La afirmación entra en `FranjaAlcance.spec.ts`, que ya montaba las cuatro superficies,
en vez de abrir un tercer archivo de prueba: la decisión 9 de planeación cerró la US en dos, y este
`it.each` pertenece al describe que ya recorre los cuatro chasis. Afirma `max-w-none` sobre
`[data-franja-alcance]` en `portal`, `acceso`, `default` y `error`. **Se comprobó que puede
fallar**: quitando la clase de `layouts/default.vue` la suite da `AssertionError: expected
[ 'shrink-0', 'border-b', …(7) ] to include 'max-w-none'`, y con la clase de vuelta pasa. La
afirmación va sobre los puntos de montaje y no sobre el componente porque el componente no puede
llevarla: quien lo monta decide su anchura.

**QA-02.** `error.vue` recibe la misma clase y el comentario que explica por qué la repite en vez
de heredarla. Se corrige **después** de archivar los dos conjuntos de capturas, así que no toca la
evidencia: la pantalla de error no es una de las siete del entregable y no forma parte de ninguna
pareja antes/después. Con esto los cuatro puntos de montaje de `FranjaAlcance` quedan alineados y
el pendiente 1 del registro de implementación queda cerrado.

**QA-03 no se corrige, y la razón importa.** No es un defecto: `useModo.ts` declara `'sistema'`
como modo por omisión y `sistemaDiseno.ts` lo resuelve contra `prefers-color-scheme`, de modo que
abrir en oscuro en un equipo con el sistema en oscuro es el comportamiento diseñado, no una
regresión. Lo que existe es una **tensión de producto**: la guía de estilos declara el modo oscuro
fuera de alcance verificado y el portal sigue al sistema de todos modos. Cambiar el valor por
omisión ahora tendría dos costos y ningún beneficio: contradiría lo que `a4_04_prevalidacion.tex`
ya publica como hallazgo no atendido en un PDF construido y pendiente de subir, y tocaría
`stores/` y `composables/`, fuera del conjunto elegible de la ola A'. Queda como decisión de S5:
o la guía verifica el modo oscuro, o el portal deja de seguir al sistema. Las capturas no dependen
de esto: el protocolo fija el modo claro de forma explícita.

**QA-04.** `CAPTURAS_ESCALA` pasa a valer **1** por omisión, que es la escala del conjunto
archivado, de modo que `node capturas_a4.mjs` sin variables reproduce `figuras/a4/` y no una
variante más densa. Es lo coherente con el propósito declarado del guion, que es que otra persona
obtenga el mismo conjunto. Las dos filas de `guion_a4.md` que decían cosas distintas —la 57 con la
escala del conjunto y la 147 con el valor por omisión— ahora dicen lo mismo. Verificado tras el
cambio: el módulo sigue derivando sus **siete** trabajos de `PROTOTIPOS`.

**QA-07.** `runCapture` solo resuelve el punto de entrada de Playwright cuando tiene que lanzar su
propio navegador. Bajo `main()` el navegador llega ya corriendo y la carga por trabajo no compraba
nada.

### Gates después de las correcciones

| Comprobación | Resultado |
|---|---|
| `make check` | **exit 0** |
| `make test` | **exit 0**. Backend **779 pasadas, 17 saltadas**. Frontend **42 archivos, 802 pruebas** (798 + las cuatro nuevas), cobertura de líneas **93.61 %**. `error.vue` entra al informe con **100 % de líneas** |
| La prueba nueva puede fallar | **verificado**: sin la clase en un layout, falla con el motivo |
| `node -e` sobre `buildCapturePlan()` | **7 trabajos** derivados de `PROTOTIPOS`, sin cambios de nombre |
| Archivos de «No tocar» | siguen intactos; los archivos tocados en QA son `error.vue`, `FranjaAlcance.spec.ts`, `capturas_a4.mjs`, `guion_a4.md`, `docs/AGENTS.md` y su espejo |

### Lo que sigue sin cerrarse, y no depende de código

1. **CA-8**: el PDF no se ha subido a Canvas. Gate del dom 16-ago a las 20:00.
2. **QA-03** como decisión de producto para S5, según lo anterior.
3. **Las etiquetas de `PROTOTIPOS[i].alcance` siguen desfasadas** respecto de lo que las pantallas
   muestran. Corrección para S5, cuando el contrato de navegación tenga US dueña.
4. **`docs/entregables/figma/`**: 26 MB sin rastrear y sin regla en `.gitignore`. Decisión previa
   al commit.
5. **Sin `git commit`**: la rama sigue esperando visto bueno.
