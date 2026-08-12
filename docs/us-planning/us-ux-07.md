# Planeación US-UX-07 — Interfaces de alta fidelidad (A4)

**Estado**: planning
**Epic**: UX
**Actividad**: A4 (dom 16-ago-2026) — **apartado 3 de la rúbrica, prototipos de alta fidelidad, 50 % = 12.50 de 25 puntos**; apoyo indirecto al apartado 4 (guía de estilos, US-UX-09)
**Sprint**: S4
**Rama**: `us-ux-07`, creada desde **la punta de `us-024`**, última de la cadena del chat (`us-009-exportacion → us-023 → us-028 → us-024`): la ola A captura `/asistente` y los componentes de `chat/`, que solo existen ahí. Convención vigente del usuario desde el 10-ago-2026: **una rama por US, commits locales encadenados, sin PR**. El estándar de la raíz (`feature/EUX-US-UX-07-alta-fidelidad`) queda como **discrepancia RU-11 declarada, no corregida**, igual que en US-001, US-016 y US-UX-09
**SHA base**: punta de `us-024` · ancla del diff: `git diff --name-only $(git rev-parse --short us-024)`
**Estimación**: 5 SP (la mayor del sprint) · **Días**: sáb 15 y dom 16 · **Estado esperado al cierre**: cerrada
**Fuente normativa**: §26 del plan (manda durante S4), con §26.3 (estado de las US), §26.4 (gates con hora), §26.5 (válvulas y no negociables), §26.6 (fuera de S4) y §25.5-2 y §25.5-6 (deuda documental que esta US está obligada a declarar)

---

## Lectura previa ejecutada

| Paso | Resultado |
|---|---|
| `docs/us-handoff/us-ux-07.md` | **No existía** (`ls docs/us-handoff/` → us-001, 002, 006, 008, 009, 015, 016, 017, 018, 025, 026, 027, 029). Se crea con estado `planning` al cerrar esta planeación |
| `frontend/AGENTS.md` | Leído (56 líneas). Es el único AGENTS.md de carpeta que aplica: esta US escribe en `frontend/` y en `docs/`, y `docs/` no tiene guía propia. **No se leyó el de la raíz**, por instrucción |
| `docs/us-planning/us-009.md` | Leído en lo pertinente (`grep` sobre `main_a4`, `a4_03`, `a4_06`, colisión). Su §3.4 fija la regla de colisión: **`main_a4.tex` lo crea quien llegue primero**. Ver ambigüedad 1 |
| `docs/us-planning/us-016.md` | `head -60` para calcar formato, densidad y tono |
| `context/planeacion_proyecto.md` | §25.5 (deuda documental, filas 2 y 6), §26.3, §26.4, §26.5, §26.6 leídas con `sed -n` |
| `frontend/app/utils/navegacion.ts` | Leído completo: `MODULOS` (4 módulos, 16 subramas), `PROTOTIPOS` (7), `RUTAS_CONTRATO` (8), `CLAVES_FACETAS_TRANSVERSALES` (9). Es la fuente de la tabla ruta ↔ rama del CA-3 |
| `mem_search` | **No disponible en este subagente** (el entorno expone Read, Bash, Glob, Grep, Write). Se sustituye por barrido `grep`/`ls` sobre `docs/`, `context/` y `frontend/` |
| `docs/us-resolved/` | **No existe.** No hay US previa de prototipado de la que heredar |
| Skills cargadas (auto-invoke) | `portal-ux-deliverables` (impone: prosa española neutra, pie de figura numerado, cada afirmación con fuente, apertura que retoma A3 y cierre que anticipa A5) · `portal-ux-patterns` (impone: los cuatro estados no felices por pantalla y el patrón de carga sin desplazamiento de maquetación) · `portal-synthetic-users` (impone: los 8 evaluadores prototipo con perfil declarado y hallazgos trazables, nunca cifras inventadas) · `portal-frontend-components` (impone: ninguna cadena visible en un componente Vue, tokens desde `design/sistema.py`) |
| Context7 | **No se usa.** La única API externa nueva sería el runner de Playwright, y la decisión de la ambigüedad 3 la retira del camino crítico. Si se instala, se instala con la versión que fije `pnpm add -D @playwright/test`, no con documentación memorizada |

---

## Qué existe ya — verificado con `ls` y `grep`, no supuesto

| Artefacto | Estado real | Consecuencia para esta US |
|---|---|---|
| `frontend/app/pages/` | **9 rutas ya existen**: `index`, `acceso`, `inicio`, `exploracion/index`, `exploracion/exportar`, `exploracion/tableros`, `gobierno`, `administracion`, `guia`. `asistente.vue` **también aparece listado** | Siete de las ocho rutas del contrato están construidas. La US **no crea pantallas desde cero**: completa estados, captura y documenta. `asistente.vue` es propiedad **exclusiva de US-023** (contrato SSE): esta US lo **lee y lo captura, jamás lo escribe** |
| `frontend/app/utils/navegacion.ts` | `RUTAS_CONTRATO` = 8 rutas derivadas de `MODULOS`; `PROTOTIPOS` = 7 entradas con campo `alcance`, hoy **todas** en `'navegable-sin-datos'` | **Archivo de solo lectura para esta US** (matriz vinculante de `auditoria-cruzada-s4.md` §1: «nadie lo escribe en S4; US-UX-07 solo lo **lee** para la tabla ruta↔rama»). El campo `alcance` alimenta el CA-5 **tal como está declarado en el código**: la tabla del PDF publica el valor real, no uno deseado. `/exploracion/tableros` no es prototipo por decisión ya escrita en el docstring |
| `docs/entregables/main_a4.tex` | **YA EXISTE** y ya compila (`main_a4.pdf`, `.log`, `.fls` presentes). Monta los ocho `\input` con `\IfFileExists` en seis de ellos y `\input` duro en `a4_03_guia_estilos` y `a4_06_cierre` | **La colisión con US-UX-09 está resuelta de hecho: llegó primero.** Consecuencia dura: **US-UX-07 NO toca `main_a4.tex`**. Los seis archivos que crea entran solos por los `\IfFileExists` ya escritos. Ver ambigüedad 1 |
| `docs/entregables/contenido/` | 17 archivos. De A4 solo hay `a4_03_guia_estilos.tex` y `a4_06_cierre.tex`, ambos **propiedad de US-UX-09** | Los seis restantes (`a4_00`, `a4_01`, `a4_02`, `a4_04`, `a4_05`, `a4_07`) son write-set exclusivo de esta US. Cero solape |
| `docs/entregables/estilo/uxdoc.sty` | **Congelada** por decisión del 11-ago-2026. `a4_tokens.tex` lo emite `generar_tokens_a4.py` (US-UX-09) | Esta US **no toca ninguno de los dos**. Las capturas del portal se maquetan con la tipografía del informe: es contenido que viaja, no formato |
| `frontend/app/components/` | **4 grupos**: `acceso/`, `comun/`, `guia/`, `nav/`. **No existe `estado/`, ni `chat/`, ni componentes de vacío/error/permiso salvo `comun/EstadoPendiente.vue`** | `EstadoPendiente.vue` es el único ladrillo reutilizable de los cuatro estados no felices. La matriz 7×4 del CA-4 (§2.3) es el verdadero backlog |
| `frontend/test/` | **16 spec** (más `configuracion.ts` e `i18nDePrueba.ts`, que no son spec), entre ellas `pantallas.spec.ts`, `smokeRutas.spec.ts`, `contratos.spec.ts`, `manifiesto.spec.ts`, `navegacion.spec.ts` | Los tres primeros son los ganchos naturales de las pruebas nuevas. **No se reescriben**: se añaden archivos propios (§6) |
| Playwright | **No instalado.** `frontend/package.json` no lo menciona; el `Makefile` no tiene objetivo de capturas | Riesgo R2. La ambigüedad 3 lo resuelve con un guion Playwright **opcional** y una ruta de captura manual reproducible como plan A. **`frontend/package.json` es write-set de esta US** (matriz vinculante, MENOR-1: «dueña US-UX-07; US-028 no añade dependencias»), y solo se toca si el plan A prospera |
| `backend/app/` | `main.py`, `core/`, `api/{auth,health}.py`, `models/user.py`, `services/`. **Sin routers de datos, chat ni export** | Confirma que el alcance real de las pantallas es **navegable sin datos** salvo lo que US-008/US-025/US-023 entreguen antes del viernes. La tabla de alcance (CA-5) no puede prometer más |
| `db/migrations/` | Dos migraciones: pgvector y `app_user`. Sin `export_job` | La pantalla de exportación es, por construcción, **navegable sin datos**. Queda escrito en la tabla de alcance, no se disimula |
| `docs/entregables/figuras/`, `imagenes/` | Existen y ya sirvieron a A1–A3 | Destino de las capturas. Las de A4 van a un subdirectorio propio para que el `git status` del sábado sea legible |

---

## Ambigüedades del enunciado, resueltas antes de planear

**1. «Quién crea `main_a4.tex`».** El enunciado y el plan de US-UX-09 lo dejan como carrera. **El repositorio ya la resolvió: `main_a4.tex` existe, compila y trae `\IfFileExists` para los seis archivos de esta US.** Decisión: **US-UX-07 no modifica `main_a4.tex` bajo ninguna circunstancia.** Si al maquetar falta un `\input`, se corrige **pidiéndoselo a US-UX-09**, no editando el archivo. Porqué: dos agentes editando el envoltorio el mismo sábado producen un conflicto de merge en el único archivo del que depende que el PDF exista, y el costo de un conflicto ahí es el entregable entero. La portadilla `\uxparte{IV}` en `main_completo.tex` y la actualización de «Sobre este documento» **sí** son de esta US: `main_completo.tex` no lo reclama nadie más.

**2. «Desplegadas» — ¿GCP real o local?** El gate del mar 11 12:00 (§26.4) exigía dirección pública viva, y §26.6 recorta Terraform «más allá del puente». Decisión: **la evidencia del PDF no depende del despliegue en GCP.** Las capturas se toman contra `make dev` local a viewport fijo, y el PDF declara la URL pública **solo si está viva al momento de capturar**, con una nota de una línea. Porqué: si el CA-1 se ancla a una URL que puede caerse el domingo, la evidencia del entregable queda a merced de la infraestructura; anclada a capturas reproducibles, no. «Desplegadas» se cumple en el sentido que la rúbrica puede verificar: **navegables end to end en el stack del producto**, no maquetas.

**3. «Guion de capturas con Playwright».** Playwright no está instalado y el sábado es el día más cargado del sprint. Decisión: **plan A es un guion Node que Playwright ejecuta si `pnpm add -D @playwright/test` corre limpio en menos de 10 minutos; plan B es captura manual con checklist de viewport fijo 1440×900, modo claro, idioma español, sesión demo por rol sugerido.** El guion se escribe igual en ambos casos, porque su valor real no es automatizar: es **fijar por escrito qué se captura, en qué orden, con qué estado y con qué sesión**, que es lo que hace la captura reproducible. Disparador: sáb 15, 10:00. Porqué: una dependencia nueva con descarga de navegadores el día del congelamiento es exactamente el riesgo que la regla de oro manda no correr.

**4. «Los cuatro estados no felices en cada pantalla» — ¿diseñados o implementados?** El CA-4 dice «diseñados». Decisión: **cada una de las 28 celdas se resuelve como una de tres cosas, y cada celda declara cuál**: (a) *implementada y capturable* — existe en el prototipo y hay captura; (b) *implementada por otra US de S4* — la produce US-023/024/025/026/027/028/029 y esta US solo la captura; (c) *documentada como especificación* — lámina de diseño en el PDF con su regla de comportamiento, sin código. Ninguna celda queda vacía. Porqué: 28 celdas implementadas en dos días es fantasía, y el silencio sobre las no implementadas es lo único que la rúbrica castiga sin recurso (§25.5-6).

**5. «Pre-validación con los 8 evaluadores prototipo».** Los evaluadores son **sintéticos, declarados** (skill `portal-synthetic-users`), heredados de A3. Decisión: **la pre-validación se documenta como protocolo con hallazgos atribuidos a perfiles nombrados, y el PDF declara en su primer párrafo que son evaluadores prototipo derivados de las personas de A1/A2, no participantes humanos.** Los resultados de A5 (SUS) sí serán con personas. Porqué: presentar evaluadores sintéticos como humanos es fabricar un resultado, y esta US no fabrica datos.

**6. «Al menos una iteración documentada, con el antes».** La captura del antes **no existe si se toma tarde**. Decisión: **la captura del antes se toma el sáb 15 a las 12:00, inmediatamente después de la ola A, ANTES de que ningún hallazgo se aplique**, y se archiva en `figuras/a4/antes/` con el mismo nombre que su par del después. Se capturan **las siete pantallas**, no solo la que se prevé cambiar, porque a las 12:00 todavía no se sabe cuál cambiará. Porqué: es literalmente irrecuperable; una vez tocada la interfaz, el antes se perdió.

**7. «Tabla de alcance de tres estados» frente a los seis estados de §26.3.** §26.3 tiene seis categorías (cerrada, cerrada degradada, demostrada no productiva, roadmap, congelada, de S5) y el CA-5 pide tres. Decisión: **la tabla del PDF tiene tres columnas de alcance por pantalla, y una segunda tabla —de US, no de pantallas— traduce las seis categorías de §26.3 a esas tres.** Mapeo fijo: cerrada y cerrada degradada → *navegable con datos de ejemplo*; demostrada en prototipo no productiva → *navegable sin datos*; roadmap, congeladas y de S5 → *roadmap*. Porqué: el CA-5 pide legibilidad para el evaluador y §26.3 pide exhaustividad para el equipo; una tabla por cada propósito cuesta media página y evita una traducción implícita que nadie podría auditar.

**8. «Las nueve facetas transversales como accesos cruzados, no duplicados».** Ya están modeladas: `CLAVES_FACETAS_TRANSVERSALES` tiene las nueve y `MODULOS` marca `facetaTransversal: true` en siete subramas. Decisión: **la US verifica la aritmética (9 claves ↔ 7 marcas) y resuelve el desajuste declarándolo, no editando el mapa de A3.** Dos facetas —`preview` y `dataQuality`— no tienen subrama marcada; se resuelven como acceso cruzado desde la pantalla de exploración y se documentan como tal. Porqué: A3 ya se entregó; cambiar su arquitectura para que cuadre una tabla es reescribir la historia.

---

## 1. Criterios de aceptación con métricas verificables

| CA | Criterio | Métrica numérica o binaria | Cómo se verifica |
|---|---|---|---|
| **CA-1** | Siete prototipos navegables y desplegados | `PROTOTIPOS.length === 7` y las 8 rutas de `RUTAS_CONTRATO` responden 200 en SSR, más `/exploracion/tableros` | `pnpm -C frontend test -- smokeRutas` en verde + `pnpm build` sin error + captura de las 7 en `figuras/a4/despues/` |
| **CA-1b** | Rama 2.4 con drill-down y overlay de linaje presentes | Binario: `/exploracion/tableros` monta el drill-down (US-025/029) y `/gobierno` monta el overlay (US-026); si no, se captura el estado que exista y se declara | Captura + fila propia en la tabla de alcance |
| **CA-1c** | Asistente con los 4 estados y el Stop | Binario: la captura muestra las cuatro tarjetas `tool_call` (`anuncio`/`ejecucion`/`resultado`/`error`) y el botón Stop | Captura de `/asistente`, propiedad de US-023/028. Válvula §26.5-1: galería en vez de secuencia |
| **CA-2** | Sistema de diseño de fuente única, derivación en un solo sentido | Binario: cero literales hex en los `.tex` de esta US; cero literales de color en los componentes que toque | `grep -nE '#[0-9A-Fa-f]{6}' docs/entregables/contenido/a4_0*.tex` → 0 aciertos (excluyendo a4_03 y a4_06, ajenos) |
| **CA-3** | Cada ruta anclada a una rama, sin huecos | 8 rutas ↔ 16 subramas, **0 ramas sin ruta y 0 rutas sin rama**; 9 facetas declaradas | `pnpm -C frontend test -- rutaRama` (el argumento es un filtro por nombre de archivo: con `contratos` la prueba nueva **no se ejecutaría**) + tabla de dos columnas en `a4_02_prototipos.tex` |
| **CA-4** | Cuatro estados no felices por pantalla | **28 celdas, 0 vacías.** Cada celda con etiqueta a/b/c de la ambigüedad 4 | Matriz completa en `a4_02_prototipos.tex` + `grep -c` de filas = 7 |
| **CA-4b** | Carga sin desplazamiento de maquetación | Binario por pantalla: el esqueleto de carga ocupa la misma caja que el contenido | Inspección declarada en la matriz; sin métrica CLS automatizada (no hay Lighthouse en el stack: se declara) |
| **CA-5** | Tabla de alcance de tres estados | **7 filas de pantalla + tabla de US con las 6 categorías de §26.3 traducidas**, incluidas las 6 capacidades de §25.5-2 y US-037 a US-041. 0 US sin declarar | `a4_05_alcance.tex`; conteo cruzado contra §26.3 |
| **CA-6** | Pre-validación con 8 evaluadores sobre capturas reales, ≥1 iteración con antes y después | 8 perfiles nombrados · ≥1 hallazgo → cambio → versión · **2 imágenes lado a lado** · 2 tareas heredadas del árbol de A3 | `a4_04_prevalidacion.tex` + existencia de par `antes/X.png` y `despues/X.png` con el mismo nombre |
| **CA-7** | Nota de herramienta en la introducción | 1 sección · 4 requisitos de la rúbrica citados uno a uno · objetivo OEA 2.2 nombrado | `a4_00_preliminares.tex`; revisión cruzada |
| **CA-8** | PDF entregado a tiempo con portada de los tres | Binario: `Entregable Actividad 4_equipo_8.pdf` subido antes del **dom 16, 20:00** (gate §26.4, margen 3h59) | `latexmk -xelatex main_a4.tex` sin `??` + captura de Canvas |
| **CA-9** | Portadilla `\uxparte{IV}` y «Sobre este documento» | Binario en `main_completo.tex` | `grep -n 'uxparte{IV}' docs/entregables/main_completo.tex` → 1 acierto |
| **CA-10** | QA gate del repo | `make check` limpio; frontend ≥ 50 % (`lines: 50` en `frontend/vitest.config.ts`); el gate combinado `--cov=backend/app --cov=ml --cov-fail-under=70` (`backend/pyproject.toml:70`) queda **intacto**, porque esta US no añade una sola línea a ninguno de esos dos paquetes | `make check && make test` |

---

## 2. Arquitectura y flujo de capas

### 2.1 Diagrama: de dónde sale cada píxel del PDF

```
  design/sistema.py  (fuente unica de tokens del PORTAL)
        |
        +--> generar_tokens_a4.py --> estilo/a4_tokens.tex   [US-UX-09, no se toca]
        |                                    |
        +--> frontend/app/utils/tokens.generated.ts          [US-UX-09]
                     |
                     v
        frontend/app/pages/*.vue  +  components/*  +  i18n/locales/{es,en}.json
                     |
                     |  make dev   (SSR real, viewport 1440x900)
                     v
        +---------------------------------------------+
        |  GUION DE CAPTURAS  (docs/entregables/       |
        |  capturas/guion_a4.md  + capturas_a4.mjs)    |
        +---------------------------------------------+
                     |                        |
        figuras/a4/antes/*.png     figuras/a4/despues/*.png
                     |                        |
                     +------------+-----------+
                                  v
      contenido/a4_00, a4_01, a4_02, a4_04, a4_05, a4_07   [ESTA US]
      contenido/a4_03_guia_estilos, a4_06_cierre           [US-UX-09]
                                  |
                        main_a4.tex  (YA EXISTE, NO SE TOCA)
                                  |
                     latexmk -xelatex, dos pasadas
                                  v
                Entregable Actividad 4_equipo_8.pdf

  uxdoc.sty (estilo del INFORME, CONGELADO) ----> maqueta el PDF
      ^ nada fluye hacia atras: el portal nunca lee uxdoc.sty
```

### 2.2 Recorrido de una captura, paso a paso

1. `make dev` levanta Nuxt SSR y FastAPI. La sesión se establece por `POST /api/auth/demo` (ruta pública) con el `rolSugerido` que `PROTOTIPOS` declara para esa pantalla.
2. El guion fija viewport 1440×900, `karisma_locale=es`, modo claro, y espera al estado de red inactivo.
3. Navega a la ruta, fuerza el estado a capturar (normal, vacío, cargando, error, sin permiso) por el mecanismo que la pantalla exponga; si la pantalla no expone forzado de estado, la celda cae en la categoría (c) de la ambigüedad 4 y se documenta como especificación.
4. Escribe `figuras/a4/<fase>/<numero>_<pantalla>_<estado>.png`. El nombre es el contrato: el par antes/después se detecta por igualdad de nombre entre carpetas.
5. El `.tex` inserta la figura con `\uxfigura` y pie numerado; **ningún `.tex` teclea un color ni una ruta absoluta**.

### 2.3 Matriz 7×4 pantallas × estados no felices — el backlog real del CA-4

Categorías: **(a)** implementada y capturable hoy · **(b)** la produce otra US de S4, esta US solo captura · **(c)** documentada como especificación en el PDF, sin código.

| # | Pantalla | Vacío | Cargando sin desplazamiento | Error | Sin permiso |
|---|---|---|---|---|---|
| 0 | `/acceso` | (c) — no aplica contenido vacío; se documenta como «formulario en reposo» | (a) botón en espera, `FormularioAcceso` | (a) credencial inválida, US-015 | (c) — la pantalla es la puerta; se documenta |
| 1 | `/inicio` | (a) `EstadoPendiente` | (c) esqueleto especificado | (c) | (b) US-016/017 marcan lo no autorizado |
| 2 | `/exploracion` | (b) US-008 sin resultados de búsqueda | (b) US-008 | (c) | (b) US-016 |
| 2.4 | `/exploracion/tableros` | (b) US-025 sin serie | (b) US-025/029 esqueleto de gráfico | (b) US-025 | (b) US-016 |
| 3 | `/gobierno` | (b) US-026 linaje sin nodos | (b) US-026 overlay | (c) | (b) US-027 bitácora |
| 4 | `/asistente` | (a) conversación sin mensajes | (b) US-028 tarjeta en `ejecucion` | (b) US-024 `AvisoError` | (b) US-024 clase `permiso`, `recuperable false` |
| 5 | `/administracion` | (a) `EstadoPendiente` | (c) | (c) | (b) US-018/019 |
| 6 | `/exploracion/exportar` | (a) sin trabajos de exportación | (c) | (c) | (b) US-016 |

**Conteo**: 28 celdas · 7 en (a) · 11 en (b) · 10 en (c) · **0 vacías**. Las 10 celdas (c) son el contenido de la sección de estados de `a4_02_prototipos.tex`: cada una con su regla de comportamiento escrita en una frase. Ninguna se implementa el fin de semana, y ninguna se calla.

### 2.4 Tabla ruta ↔ rama del CA-3 (fuente: `navegacion.ts`, verificada)

| Rama del mapa de A3 | Ruta real | Estado |
|---|---|---|
| 1 Inicio | `/inicio` | Anclada |
| 1.1 búsqueda · 1.2 recientes · 1.3 favoritos · 1.5 perfil | `/inicio` | Colapsan en la pantalla del módulo; declarado |
| 1.4 mis alertas *(faceta)* | `/inicio` | Anclada + acceso cruzado |
| 2 Exploración y extracción | `/exploracion` | Anclada |
| 2.1 catálogo | `/exploracion` | Anclada |
| 2.2 consulta *(faceta)* | `/exploracion` | Anclada + acceso cruzado |
| 2.3 exportaciones *(faceta)* | `/exploracion/exportar` | Anclada, pantalla propia |
| 2.4 tableros | `/exploracion/tableros` | Anclada, **zona C de la pantalla 2, no prototipo aparte** |
| 3 Gobierno del dato | `/gobierno` | Anclada |
| 3.1 diccionario | `/gobierno` | Anclada |
| 3.2 linaje *(faceta)* · 3.3 fuentes *(faceta)* | `/gobierno` | Ancladas + acceso cruzado |
| 4 Administración | `/administracion` | Anclada |
| 4.1 usuarios *(faceta)* · 4.2 solicitudes · 4.3 bitácora · 4.4 integraciones *(faceta)* | `/administracion` | Ancladas; válvula §26.5-3: un solo nivel |
| Transversal a las 4 categorías | `/asistente` | Anclada, no es rama del mapa: se declara |
| Fuera del mapa por decisión | `/` (índice) y `/guia` | Declaradas fuera; `/guia` puntúa en el apartado 4 |

**Huecos detectados y su resolución**: (i) `/asistente`, `/` y `/guia` son rutas sin rama, **declaradas por diseño** en el docstring de `navegacion.ts`; (ii) las facetas `preview` y `dataQuality` de `CLAVES_FACETAS_TRANSVERSALES` no tienen subrama con `facetaTransversal: true` — se resuelven como accesos cruzados desde `/exploracion` y se documentan (ambigüedad 8). **Ninguna rama del mapa queda sin ruta.**

---

## 3. Archivos exactos a crear o modificar

| Ruta | C/M | Qué cambia | Quién lo escribe |
|---|---|---|---|
| `docs/entregables/contenido/a4_00_preliminares.tex` | C | Portada con los tres integrantes, «Sobre este documento», **nota de herramienta del CA-7** con los 4 requisitos y OEA 2.2 | Ola C |
| `docs/entregables/contenido/a4_01_metodo_prototipado.tex` | C | Método: stack del producto como medio de prototipado, viewport fijo, protocolo de captura, herencia de A3 | Ola C |
| `docs/entregables/contenido/a4_02_prototipos.tex` | C | Las 7 pantallas con figura y pie numerado · **tabla ruta ↔ rama (CA-3)** · **matriz 7×4 de estados (CA-4)** | Ola C |
| `docs/entregables/contenido/a4_04_prevalidacion.tex` | C | Protocolo de los 8 evaluadores · las 2 tareas heredadas del árbol de A3 · hallazgo → cambio → versión · **figura antes/después lado a lado** | Ola D |
| `docs/entregables/contenido/a4_05_alcance.tex` | C | **Tabla de alcance de tres estados por pantalla** + tabla de US con §26.3 traducida + 6 capacidades de §25.5-2 + US-037…041 | Ola B |
| `docs/entregables/contenido/a4_07_anexo.tex` | C | Guion de capturas, inventario de figuras, tabla de trazabilidad CA ↔ sección ↔ evidencia | Ola D |
| `docs/entregables/main_completo.tex` | M | `\uxparte{IV}` + actualización de «Sobre este documento» | Ola D |
| `docs/entregables/capturas/guion_a4.md` | C | Guion escrito: qué, en qué orden, con qué sesión, con qué estado | Ola A |
| `docs/entregables/capturas/capturas_a4.mjs` | C | Guion Playwright (plan A de la ambigüedad 3); inerte si Playwright no se instala | Ola A |
| `docs/entregables/figuras/a4/antes/*.png` | C | 7 capturas del **antes**, sáb 15 12:00 | Ola A |
| `docs/entregables/figuras/a4/despues/*.png` | C | Capturas del **después** y de los estados, sáb 15 20:00 y dom 16 10:00 | Ola A' |
| `frontend/app/utils/navegacion.ts` | **L (lectura)** | **No se modifica.** La matriz vinculante lo declara sin dueño de escritura en S4; se lee `PROTOTIPOS[i].alcance` y `MODULOS` para las tablas del CA-3 y del CA-5. Si el valor real de un `alcance` quedara desfasado tras el congelamiento, se declara como pendiente en el handoff y se publica el valor del código, no uno corregido a mano | Olas A y B (solo lectura) |
| `frontend/package.json` · `pnpm-lock.yaml` | M **condicional** | Únicamente si el plan A de la ambigüedad 3 prospera: `pnpm add -D @playwright/test`. Dueña única por la matriz vinculante (MENOR-1). Si a las 10:10 del sáb 15 la instalación no está limpia, **ninguno de los dos archivos se toca** y se sigue con el plan B | Ola A |
| `frontend/i18n/locales/es.json` · `en.json` | **no se tocan** | Las tres etiquetas de alcance **ya existen** como `prototype.scope.{withData,withoutData,roadmap}` en los dos locales y ya las resuelve `components/nav/BotonPrototipo.vue:25-27` vía `CLAVE_ALCANCE`. El subárbol `scope.*` existente es otra cosa: `notice` y `ariaLabel` de la franja. Abrir `scope.withData` sería un segundo vocabulario para la misma etiqueta | — |
| `frontend/test/rutaRama.spec.ts` | C | Prueba del CA-3 (§6) | Ola B |
| `frontend/test/alcancePrototipos.spec.ts` | C | Prueba del CA-5 (§6) | Ola B |
| `docs/us-handoff/us-ux-07.md` | C | Handoff, estado `planning` | Ahora |

> **Corrección fechada el 11-ago-2026 (auditoría cruzada).** Tres defectos del write-set: (a) el plan
> abría `scope.*` en los locales para etiquetas que **ya existen** como `prototype.scope.*` y que
> `BotonPrototipo.vue` ya resuelve, lo que habría dejado la primera redacción huérfana; (b) la ola A'
> declaraba como write-set «los componentes que el hallazgo obligue a tocar», que no es un write-set
> sino el agujero por donde entra la colisión, y cae en la ventana en que US-024 aún puede estar
> escribiendo; (c) la rama nacía de `f807a18`, donde `/asistente` y `components/chat/` no existen y no
> se podrían capturar. Se decide no tocar los locales, cerrar el conjunto elegible de A' y encadenar la
> rama a la punta de `us-024`.

> **Corrección fechada el 11-ago-2026 (auditoría cruzada, segunda pasada).** Quedaban dos huecos en
> el write-set. (a) El plan declaraba `frontend/app/utils/navegacion.ts` como modificado («solo el
> campo `alcance`»), pero la matriz de colisión vinculante de `docs/us-planning/auditoria-cruzada-s4.md`
> §1 lo cierra como archivo que **nadie escribe en S4** y del que esta US es solo lectora. Manda la
> matriz: el archivo pasa a lectura y la tabla del PDF publica el `alcance` que el código declara; un
> desfase se declara como pendiente del handoff, no se parchea a mano el sábado. Motivo: el CA-5
> pierde su valor si el entregable calificado y el código pueden divergir por una edición de última
> hora que nadie más está esperando. (b) La misma matriz asigna `frontend/package.json` a esta US
> (MENOR-1, Playwright) y el plan no lo declaraba en ninguna fila, pese a que la ambigüedad 3 corre
> `pnpm add -D @playwright/test`: un archivo que se toca sin figurar en el write-set es exactamente el
> defecto que el protocolo de archivo compartido existe para evitar. Se declara con su condición y su
> hora de corte.

**Prohibido tocar** (write-set ajeno o congelado): `docs/entregables/main_a4.tex` · `contenido/a4_03_guia_estilos.tex` · `contenido/a4_06_cierre.tex` · `estilo/uxdoc.sty` · `estilo/a4_tokens.tex` · `generar_tokens_a4.py` · `frontend/app/pages/asistente.vue` · `frontend/app/components/chat/**` · `frontend/app/utils/navegacion.ts` (sin dueño de escritura en S4 por la matriz vinculante) · `frontend/i18n/locales/{es,en}.json` · todo `backend/`, `ml/`, `db/`, `tests/backend/`.

---

## 4. Firmas públicas de los módulos nuevos

Esta US casi no produce código. Lo poco que produce va con firma completa y sin implementación.

```ts
// docs/entregables/capturas/capturas_a4.mjs

/** Fixed viewport used for every A4 screenshot, in CSS pixels. */
export const VIEWPORT: Readonly<{ width: number; height: number }>

/** One screenshot job: route, demo role, forced state and output file name. */
export interface CaptureJob {
  readonly route: string
  readonly role: 'operativo' | 'analista' | 'directivo' | 'administrador'
  readonly state: 'normal' | 'empty' | 'loading' | 'error' | 'forbidden'
  readonly fileName: string
}

/** Ordered capture plan derived from PROTOTIPOS; the single source of the run. */
export function buildCapturePlan(): readonly CaptureJob[]

/** Runs one job against a live dev server and writes the PNG under outputDir. */
export async function runCapture(job: CaptureJob, outputDir: string): Promise<string>
```

```ts
// frontend/app/types/navegacion.ts  (firma ya existente, solo se lee)

/** How much of a screen is actually usable right now. */
export type EstadoAlcance = 'navegable-con-datos' | 'navegable-sin-datos' | 'roadmap'
```

No se añade **ni una función ni un tipo**: `EstadoAlcance` ya existe en `app/types/navegacion.ts` —no
en `utils/`, que no exporta ningún tipo—. Y desde la segunda pasada de la auditoría **tampoco cambia
ningún valor**: `app/utils/navegacion.ts` es archivo de solo lectura para esta US, así que el literal
`PROTOTIPOS` se consulta y se publica, nunca se edita.

> **Corrección fechada el 11-ago-2026 (auditoría cruzada).** El bloque declaraba un tipo
> `AlcancePrototipo` en `frontend/app/utils/navegacion.ts`. Ni el nombre ni el archivo existen: el tipo
> real es `EstadoAlcance` y vive en `frontend/app/types/navegacion.ts` (lo consume
> `components/nav/BotonPrototipo.vue`). Se corrige el nombre y la ruta. Motivo: un
> `import type { AlcancePrototipo } from '~/utils/navegacion'` rompe `pnpm -C frontend typecheck`, y
> escribirlo «para desbloquear» abriría un segundo vocabulario de alcance.

---

## 5. Dominios, olas y write-sets disjuntos

**Checklist de dominios**: [ ] backend · [x] frontend (mínimo: dos spec nuevas y, condicionalmente, la dependencia de Playwright; **cero claves i18n y cero líneas de `navegacion.ts`**) · [ ] ml · [ ] agent · [ ] infra · [ ] db · [x] docs

**Sí se reparte.** Es la única US del sprint que se reparte de verdad: guion de capturas, `.tex` de contenido, tabla de alcance y pre-validación son trabajos distintos sobre archivos distintos. Pero **la cadena captura → documento es secuencial y el que captura va primero**, y la iteración del CA-6 mete una **segunda pasada de captura** después de tocar la interfaz.

| Ola | Cuándo | Agente / subagente | Write-set exclusivo | Depende de |
|---|---|---|---|---|
| **A — captura del antes** | **sáb 15, 10:00 → 12:00** | `frontend-builder` | `capturas/guion_a4.md` · `capturas/capturas_a4.mjs` · `figuras/a4/antes/*` · `frontend/package.json` y `pnpm-lock.yaml` **solo si el plan A prospera antes de las 10:10** | Congelamiento vie 14 20:00 (§26.4) **y** el hallazgo del CA-6 elegido sobre una pantalla **distinta de `/asistente`** (ver R3b) |
| **B — datos y contratos** | **sáb 15, 12:00 → 16:00**, en paralelo con C | `frontend-builder` | `frontend/test/rutaRama.spec.ts` · `frontend/test/alcancePrototipos.spec.ts` · `contenido/a4_05_alcance.tex`. **Lee, no escribe**: `frontend/app/utils/navegacion.ts` y los dos locales | Ola A (necesita el inventario real) |
| **C — documento base** | **sáb 15, 12:00 → 20:00**, en paralelo con B | `deliverable-writer` | `contenido/a4_00_preliminares.tex` · `a4_01_metodo_prototipado.tex` · `a4_02_prototipos.tex` | Ola A (inserta las figuras del antes como provisionales) |
| **A' — iteración y recaptura** | **sáb 15, 20:00 → 22:00** | `frontend-builder` | `frontend/app/components/comun/**` · `frontend/app/layouts/**` · `frontend/app/pages/{index,inicio,exploracion/index,gobierno,administracion}.vue` · `docs/entregables/figuras/a4/despues/*`. **El conjunto elegible es este y ningún otro**: quedan fuera `components/chat/**`, `components/exportacion/**`, `components/guia/**`, `pages/asistente.vue`, `pages/exploracion/exportar.vue`, `pages/guia.vue` y `pages/acceso.vue`, todos con dueña viva esta semana. Si el único hallazgo relevante cayera fuera, se documenta como hallazgo **no atendido** en `a4_04_prevalidacion.tex` en vez de invadir write-set ajeno | Olas A y C; **hallazgo del CA-6 ya elegido dentro del conjunto** |
| **D — pre-validación y cierre** | **dom 16, 09:00 → 16:00** | `deliverable-writer` | `contenido/a4_04_prevalidacion.tex` · `a4_07_anexo.tex` · `main_completo.tex` | Ola A' (sin el después no hay iteración) |
| **E — compilación y revisión cruzada** | **dom 16, 16:00 → 20:00** | `deliverable-writer` | ninguno nuevo: solo corrige dentro de los archivos ya propios | Todas |

> **Corrección fechada el 11-ago-2026 (auditoría cruzada, segunda pasada).** La ola B seguía
> reclamando `i18n/locales/*.json` (subárbol `scope.*`) y `navegacion.ts` (campo `alcance`), aunque §3
> ya había retirado lo primero —las etiquetas viven en `prototype.scope.*` y abrir `scope.withData`
> crearía un segundo vocabulario— y la matriz vinculante retira lo segundo. Un write-set que se
> corrige en una sección y sobrevive en otra es peor que no corregirlo: el agente que ejecuta la ola
> lee §5, no §3. La ola B queda reducida a dos spec nuevas y su `.tex`, y sus dos fuentes pasan a
> lectura. La ola A gana `frontend/package.json` con su corte de las 10:10.

**Regla de frontera con US-UX-09**: si la ola E encuentra que falta un `\input` en `main_a4.tex`, **no lo edita**: lo escribe como pendiente en el handoff y lo resuelve US-UX-09. Los seis archivos de esta US ya están cubiertos por los `\IfFileExists` existentes, así que este caso no debería ocurrir.

**Regla de frontera con US-023/024/028**: esta US **lee y captura** `/asistente` y los componentes de `chat/`. Si a la hora de capturar no existen, la celda cae en categoría (b) no disponible y se documenta como roadmap en la tabla de alcance. **No se escribe ni una línea en esos archivos.**

---

## 6. Plan de tests

Regla de la raíz: cada prueba declara qué defecto concreto la haría fallar. Las que no la responden no se escriben; por eso aquí solo hay dos archivos nuevos y ninguna prueba sobre `.tex`.

| Prueba | Archivo | Qué defecto concreto la haría fallar | Umbral |
|---|---|---|---|
| `cada rama del mapa de A3 aparece en la tabla ruta-rama del PDF` | `frontend/test/rutaRama.spec.ts` | La tabla de `a4_02_prototipos.tex` se escribe a mano y omite una de las 16 subramas: el PDF afirmaría una cobertura que el mapa no tiene. Se lee el `.tex` y se comparan sus filas contra `MODULOS` | 16 subramas + 4 módulos presentes en el `.tex`, 0 ausentes |
| `el alcance publicado en el PDF coincide con el declarado en el código` | `frontend/test/alcancePrototipos.spec.ts` | Tras el congelamiento del vie 14 20:00 alguien actualiza `PROTOTIPOS[i].alcance` y no la tabla de `a4_05_alcance.tex`, o al revés: el entregable calificado mentiría sobre lo que el prototipo hace | 7 filas del `.tex` == 7 valores de `PROTOTIPOS` |

**No se escriben, y son cinco pruebas que el plan sí traía** (retiradas por la auditoría del
11-ago-2026, cada una con su razón verificada):

- *«toda rama del mapa tiene ruta»* — **tautología por construcción**:
  `frontend/app/utils/navegacion.ts:176` define `RUTAS_CONTRATO` como
  `[RUTA_ACCESO, ...MODULOS.flatMap(m => [m.ruta, ...m.subrutas.map(s => s.ruta)]), RUTA_ASISTENTE]`.
  Añadir una subrama **añade su ruta automáticamente**: el defecto declarado es imposible.
- *«toda ruta del contrato existe como página»* — ya existe: `pantallas.spec.ts:132`
  (`expect(rutasDeArchivos).toEqual([RUTA_INDICE, RUTA_GUIA, ...RUTAS_CONTRATO].sort())`).
- *«las nueve facetas están declaradas»* — ya existe, literalmente: `navegacion.spec.ts:85-86`.
- *«cada prototipo declara un alcance de los tres válidos»* — ya existe: `navegacion.spec.ts:158`
  (`expect(ESTADOS_DE_ALCANCE).toContain(prototipo.alcance)`), con un comentario del repositorio que
  documenta haber corregido ahí mismo una aserción inalcanzable.
- *«las claves i18n de alcance existen en es y en en»* y *«ninguna cadena de alcance vive en un
  componente»* — no hay claves nuevas (las etiquetas ya son `prototype.scope.*`), y la paridad y la
  resolución de literales ya las cubren `idioma.spec.ts:42` y `contratos.spec.ts:214`.

**Tampoco se escriben**: pruebas sobre la existencia de PNG (el defecto lo detecta la compilación de LaTeX, que falla con figura ausente), ni pruebas sobre el `.tex` más allá de las dos filas de arriba (LaTeX ya es su propio verificador), ni pruebas del guion Playwright mientras Playwright sea opcional. Cobertura: **frontend ≥ 50 %** (`lines: 50` en `frontend/vitest.config.ts`) se mantiene con las 16 spec existentes más estas dos. El gate de backend es **combinado** sobre `backend/app` **y** `ml` (`--cov=backend/app --cov=ml --cov-fail-under=70`, `backend/pyproject.toml:70`) y **no lo mueve esta US**: no añade ni una línea a ninguno de los dos paquetes, así que no aporta numerador ni denominador. Esta US **no promete cobertura de backend**: solo declara que no la degrada.

> **Corrección fechada el 11-ago-2026 (auditoría cruzada, segunda pasada).** El plan citaba el umbral
> como «backend ≥ 70 % intacto, esta US no toca `backend/app`». El gate real de `backend/pyproject.toml:70`
> mide `backend/app` **y** `ml` sobre un denominador común, de modo que «no toca `backend/app`» no era
> argumento suficiente para afirmar que el umbral no se mueve. Se corrige la cita y se reformula la
> promesa: una US de documento y capturas no puede prometer una cobertura de una capa que no escribe,
> solo puede comprometerse a no degradarla.

---

## 7. Nube

**No toca la nube.** Por la ambigüedad 2, la evidencia del PDF se ancla a capturas locales reproducibles y no al despliegue en GCP; el gate del mar 11 pertenece a US-003 y su resultado se cita, no se produce aquí. Si la URL pública está viva al capturar, se añade una línea al `a4_01`; ese es todo el acoplamiento.

---

## 8. Schema

**No toca schema.** Ninguna migración, ninguna tabla, ningún cambio en `db/schema.sql`. La ausencia de `export_job` en `db/migrations/` no se corrige aquí: se **declara** en la tabla de alcance como la razón por la que `/exploracion/exportar` es *navegable sin datos*.

---

## 9. Rúbrica: a qué responde y con cuántos puntos

| Apartado de la rúbrica A4 | Peso | Puntos sobre 25 | Cobertura de esta US |
|---|---|---|---|
| **3 · Prototipos de alta fidelidad** | **50 %** | **12.50** | **Directo y completo.** CA-1, CA-1b, CA-1c, CA-3, CA-4. El tope se alcanza con cinco pantallas; se entregan **siete** para que dos juzgadas «Parcialmente» no bajen la banda |
| 4 · Guía de estilos | 45 % | 11.25 | **Ajeno**: es de US-UX-09. Esta US aporta las capturas que documentan el producto y respeta la derivación en un solo sentido (CA-2) |
| Introducción y método | resto | — | CA-7 (nota de herramienta con los 4 requisitos y OEA 2.2) y CA-6 (pre-validación con iteración) |

| CA | Sección del PDF | Evidencia |
|---|---|---|
| CA-1 / 1b / 1c | `a4_02_prototipos.tex` | 7 figuras con pie numerado |
| CA-2 | `a4_01` + `a4_03` (ajeno) | Diagrama de derivación en un solo sentido |
| CA-3 | `a4_02_prototipos.tex` | Tabla de dos columnas + `rutaRama.spec.ts` |
| CA-4 | `a4_02_prototipos.tex` | Matriz 7×4, 28 celdas etiquetadas |
| CA-5 | `a4_05_alcance.tex` | Dos tablas: pantallas y US |
| CA-6 | `a4_04_prevalidacion.tex` | Figura antes/después lado a lado |
| CA-7 | `a4_00_preliminares.tex` | Nota de herramienta |
| CA-8 / CA-9 | `main_a4.tex` (ajeno) + `main_completo.tex` | PDF y portadilla |

---

## 10. Riesgos y mitigaciones

| # | Riesgo | Prob. | Impacto | Mitigación | Disparador de la válvula |
|---|---|---|---|---|---|
| R1 | **La captura del antes se toma tarde y la iteración del CA-6 deja de ser verificable** | Media | **Crítico**: el CA-6 se cae entero y no hay recuperación | Ola A cierra a las 12:00 del sáb con las **siete** pantallas archivadas antes de tocar nada | Si a las 12:30 no están las 7, se congela toda modificación de interfaz hasta tenerlas |
| R2 | Playwright no instala o descarga navegadores durante el sábado | Alta | Medio | Plan B ya escrito: captura manual con checklist de viewport fijo | sáb 15, 10:00: si `pnpm add -D @playwright/test` no está limpio en 10 min, plan B |
| R3 | US-023/028 no entregan `/asistente` con los 4 estados a tiempo | Media | Alto: CA-1c parcial | Válvula §26.5-1: los 4 estados como **galería** en lugar de secuencia animada | sáb 15, 12:00 (mismo gate del go/no-go de Gemini) |
| R3b | **El gate del sáb 15 12:00 sale GO y US-023 reescribe `/asistente`** (cambia la clave de la franja de honestidad a la advertencia de IA) **después** de que la ola A archivara el «antes» | Media | Alto: la pareja antes/después de `/asistente` dejaría de atribuirse al hallazgo del CA-6 y el criterio perdería su trazabilidad | **`/asistente` queda excluida del par antes/después del CA-6**: la iteración documentada se toma sobre una de las otras seis pantallas, elegida al cerrar la ola A. Si el GO se confirma, se recaptura `/asistente` en la ola A' y el pie de figura declara que el cambio proviene del gate de Gemini, no de la pre-validación | sáb 15, 12:00: el orquestador comunica el resultado del go/no-go **antes** de abrir la ola B |
| R4 | Colisión con US-UX-09 en `main_a4.tex` | **Baja** (ya resuelta: el archivo existe con `\IfFileExists`) | Crítico si ocurriera | Prohibición absoluta de editarlo desde esta US | Cualquier necesidad de editar → pendiente en handoff, lo hace US-UX-09 |
| R5 | La tabla de alcance omite una US y el evaluador encuentra el hueco | Media | Alto (§25.5-6: el silencio es lo único que no funciona) | Conteo cruzado obligatorio contra las seis categorías de §26.3, US por US | Ola B no cierra hasta que el conteo cuadre |
| R6 | El drill-down de tres niveles no está listo | Media | Bajo | Válvula §26.5-2: **baja de tres niveles a dos**, y se declara en la tabla | sáb 15, 16:00 |
| R7 | Administración con cuatro subniveles no cabe | Media | Bajo | Válvula §26.5-3: **un solo nivel** | sáb 15, 18:00 |
| R8 | El tiempo del domingo no alcanza para siete pantallas | Baja | Medio | Válvula §26.5-4: **exportación sale del set, quedan seis**. Es la última válvula: las cinco interfaces de la arquitectura de A3 son **no negociables** | dom 16, 12:00 |
| R9 | La compilación de LaTeX falla por figura ausente el domingo por la tarde | Media | Alto | El anexo `a4_07` lleva inventario de figuras; la ola E compila dos veces con margen | dom 16, 18:00 sin PDF limpio → se retiran las figuras opcionales del anexo |
| R10 | Se presenta el prototipo como sistema en producción | Baja | **Crítico reputacional** | La franja de alcance (`CLAVE_AVISO_ALCANCE`) aparece en **todas** las capturas, por construcción del componente `FranjaAlcance.vue` | Ninguna captura sin franja se acepta en el PDF |

---

## 11. Checklist de cierre verificable

- [ ] Congelamiento del vie 14 20:00 respetado: ninguna pantalla tocada salvo por la iteración del CA-6, y esa iteración **dentro del conjunto elegible de la ola A'**
- [ ] `/asistente` **fuera** del par antes/después del CA-6 (R3b); si el go/no-go salió GO, su recaptura lleva pie de figura que lo declara
- [ ] `figuras/a4/antes/` con **7 PNG**, timestamp anterior a cualquier commit de la ola A'
- [ ] `figuras/a4/despues/` con el par de cada captura del antes que cambió, mismo nombre de archivo
- [ ] `capturas/guion_a4.md` describe el protocolo completo y es ejecutable por una persona distinta
- [ ] Los seis `.tex` de esta US creados; **`main_a4.tex` sin una sola línea modificada** (`git diff --name-only $(git rev-parse --short us-024) | grep -c main_a4.tex` → `0`)
- [ ] Tabla ruta ↔ rama en `a4_02`: 0 ramas sin ruta, huecos declarados
- [ ] Matriz 7×4: **28 celdas, 0 vacías**, cada una etiquetada (a)/(b)/(c)
- [ ] Tabla de alcance de tres estados con las 7 pantallas + las 6 capacidades de §25.5-2 + US-037 a US-041 + las seis categorías de §26.3 traducidas
- [ ] Pre-validación: 8 evaluadores prototipo nombrados, declarados sintéticos, con las 2 tareas heredadas del árbol de A3
- [ ] ≥1 iteración documentada hallazgo → cambio → versión, con antes y después **lado a lado** en la misma figura
- [ ] Nota de herramienta con los 4 requisitos de la rúbrica y OEA 2.2 citados uno a uno
- [ ] `\uxparte{IV}` en `main_completo.tex` y «Sobre este documento» actualizado
- [ ] `grep -nE '#[0-9A-Fa-f]{6}'` sobre los seis `.tex` propios → 0 aciertos
- [ ] Ninguna cadena visible añadida dentro de un componente Vue; **cero claves i18n nuevas**: las etiquetas de alcance ya existen como `prototype.scope.*` y los locales no se tocan
- [ ] `pnpm test` en verde, **frontend ≥ 50 %**
- [ ] `make check` limpio (ruff + mypy + eslint + secrets-scan)
- [ ] `frontend/app/utils/navegacion.ts` **sin una sola línea modificada** (`git diff --name-only $(git rev-parse --short us-024) | grep -c 'utils/navegacion.ts'` → `0`); cualquier desfase de `alcance` queda como pendiente del handoff
- [ ] `frontend/package.json` y `pnpm-lock.yaml` modificados **solo** si el plan A de Playwright prosperó; si se activó el plan B, ambos intactos
- [ ] `make test` en verde, **gate combinado `backend/app` + `ml` ≥ 70 % sin variación** (esta US no escribe en ninguno de los dos)
- [ ] QA gate de la raíz, punto 6: checklist de la actividad verificado contra la rúbrica
- [ ] `latexmk -xelatex main_a4.tex` en dos pasadas, sin `??` en el índice, sin `Overfull` en las tablas grandes
- [ ] PDF renombrado a `Entregable Actividad 4_equipo_8.pdf` con portada de **Alexandro Mayoral, Jacqueline Sarmiento y Arthur Zizumbo**
- [ ] Subido a Canvas antes del **dom 16, 20:00** (gate §26.4, margen 3h59 contra las 23:59)
- [ ] Commits sin trailer `Co-Authored-By`; rama `us-ux-07` encadenada sobre la punta de `us-024`, sin PR
- [ ] `docs/us-handoff/us-ux-07.md` actualizado de `planning` a `cerrada` con los pendientes reales
