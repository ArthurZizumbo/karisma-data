# docs/ — Entregables del curso, orquestación y artefactos por User Story

> Sub-guía del orquestador. Las reglas transversales viven en [`../AGENTS.md`](../AGENTS.md) — aquí no se repiten, solo lo operativo de `docs/`.

## Estado

**Cuatro de cinco actividades entregadas.** A1 (26-jul, 15/15, con la observación de maquetación ya corregida), A2 (2-ago) y A3 (9-ago). El PDF subido a Canvas está en `semana_1/`, `semana_2/` y `semana_3/` como `Entregable Actividad N_equipo_8.pdf`; su fuente vive en `entregables/contenido/a1_*.tex`, `a2_*.tex` y `a3_*.tex`. Material cerrado.

**A4 entregada el 16-ago.** `entregables/main_a4.tex` declara **nueve** `\input` en su orden final, casi todos envueltos en `\IfFileExists` para compilar a media semana, y **los nueve existen**: `a4_03_guia_estilos.tex` y `a4_06_cierre.tex` son de US-UX-09, seis de US-UX-07 y `a4_08_tema_y_flujos.tex` de US-ENTREGA-A4 (14-ago-2026), que lo colocó **entre `a4_05` y `a4_06`** porque es cuerpo, no anexo. `semana_4/` **ya tiene su PDF de entrega** con el nombre que exige la actividad, junto a `plan_excelencia.md` y las figuras generadas. `main_completo.tex` incorpora la parte IV y carga `estilo/a4_tokens` en el preámbulo, porque reutiliza `a4_03` y sin esa línea faltan ocho secuencias de control.

**El documento de A4 se compactó a documentación ejecutiva** (US-A4-EXCELENCIA, 16-ago-2026). Dos reglas nuevas que ahorran buscar. Primera: **el sistema de diseño se documenta en un solo sitio**, `a4_03_guia_estilos.tex`, cuyo capítulo «Especificación del sistema de tokens y paleta institucional» absorbió la paleta institucional, su matriz de contraste y la de dicromacias; su capítulo de marca absorbió además la normativa del logotipo. `a4_08_tema_y_flujos.tex` **conserva el nombre pero ya solo publica los cinco flujos de tarea** y su verificación técnica, **cada pie con la palabra diseño** para que ninguna lámina se lea como captura del portal. Segunda: **el documento no narra su propio desarrollo**. No se escribe «iteración», no se cita la rúbrica, no se justifica por qué una figura no se rehizo; los hallazgos se publican como decisiones de diseño con su medición, agrupadas en tres ejes técnicos. Las capturas de la sección de prototipos son las del **tema institucional en ejecución**. **Disciplina de saltos, pedida por el evaluador**: un bloque visual no se parte ni comparte página. Hay un `\clearpage` antes de cada uno de los siete prototipos y del chasis común en `a4_02`, y otro antes de cada uno de los cinco flujos y de la verificación técnica en `a4_08`. Sin ellos las capturas del portal ---que ocupan cerca de media caja de texto--- no caben junto a su texto, el flotante aterriza una página más tarde y una página acaba con dos titulares y ninguna figura. Está medido, no supuesto. Cuidado con una trampa real: el paso 4 de `scripts/verificar_tokens_a4.sh` corre `grep -lE '#[0-9A-Fa-f]{6}'` sobre **todos** los `contenido/a4_*.tex` y un solo hexadecimal con almohadilla lo pone en rojo — los colores se publican como `\texttt{0B1B2B}`, sin almohadilla.

**Las capturas del prototipo son un artefacto nuevo** (US-UX-07). `entregables/capturas/` trae el protocolo escrito, `guion_a4.md`, y su ejecutable `capturas_a4.mjs`, que deriva el plan de captura de `PROTOTIPOS` parseando `frontend/app/utils/navegacion.ts` como texto. Salida en `figuras/a4/{antes,despues}/`, pareadas por nombre de archivo. Dos pruebas del frontend, `rutaRama.spec.ts` y `alcancePrototipos.spec.ts`, **leen `.tex` de `contenido/`** y los comparan contra el contrato de navegación: un `.tex` de esta carpeta puede poner la suite del frontend en rojo.

**Los iconos de la guia de estilos se imprimen, no se describen** (19-ago-2026, observacion del evaluador de A4). El punto 9.5 salia con el titular y nada debajo: su tabla era un flotante que aterrizaba una pagina mas tarde, ya pasada la 9.6, y ademas nombraba los iconos en prosa sin mostrar ni uno. La Tabla 28 ahora imprime **los 27 glifos** del inventario con su nombre y su rotulo accesible, y se compone con `uxtablalarga` -xltabular, NO flotante, repite encabezado al partirse-, que es lo unico que garantiza que un titular no vuelva a quedarse sin su tabla. La emite `figuras/generar_iconos_a4.mjs` desde `inventarioIconos.ts` y `i18n/locales/es.json`, rasterizando con el Chromium de Playwright. **La estructura de la seccion 9 no cambio**: siguen siendo las mismas seis subsecciones. Un primer intento agrego una 9.6 con rutas `.vue` y el comportamiento del empaquetador y **se revirtio**: el evaluador ya habia senalado que el trabajo brinca a la etapa de desarrollo, y una guia de estilos no publica rutas de archivos de codigo. Dos hechos que la revision dejo escritos: el grosor de trazo real es de **dos unidades sobre un lienzo de 24** -2 px a 24 px y 1,33 px a 16 px-, no el 1,5 px uniforme que la guia declaraba; y la interfaz usa 65 iconos distintos frente a los 27 declarados, diferencia que el documento resume en una frase, sin catalogo.

**A5 (23-ago) está en curso y el vehículo de entrega cambió** (US-AVANCE-5, 22-ago-2026). Lo que se sube a Canvas **no es el compacto** `main_a5.tex` sino el acumulado **`main_completo.tex` con una Parte V nueva**. La razón está medida contra la rúbrica: once de sus dieciséis criterios re-evalúan los artefactos de A1–A4 bajo la banda «se incluyen los elementos solicitados», y los resúmenes de una fila por artefacto del compacto los exponían a «Parcialmente». La Parte V incluye, en este orden editorial, `a5_00_preliminares`, `a5_06_metricas` (criterio 14, 15 %), `a5_04_usabilidad` (criterio 15, 20 %), `a5_05_cierre` (criterio 16, con las referencias consolidadas de todo el volumen) y `a5_07_manual` como Anexo B. **`a5_01`, `a5_02` y `a5_03` no entran al acumulado**: duplicarían las Partes I–III con menos detalle. Siguen en `main_a5.tex`, que queda como documento de trabajo y plan B de contingencia. El acumulado mide **305 páginas**, así que tras la «Introducción general» del folio 10 viene una sección propia, «Mapa de cumplimiento de la entrega» en el folio 12: dieciséis filas, criterio de la rúbrica → sección → página, y es la mitigación acordada contra la fatiga del evaluador. Trece de sus filas resuelven con `\pageref` contra anclas `cmp:*` que viven **solo en el envoltorio**; las de los criterios 3, 4 y 5 llevan la página **escrita a mano** porque su contenido está dentro de `a1_cuerpo.tex` y ADR-005 prohíbe insertarle ganchos. Si tocas la estructura del volumen, esa tabla es lo primero que hay que volver a verificar, y esas tres filas hay que volver a medirlas.

**La dirección del demo entra al documento por variable, nunca literal.** El repositorio es público y una URL de Cloud Run lleva dentro el identificador del proyecto de GCP. El contrato está partido en dos mitades: `entregables/datos/demo.tex` **se versiona** y define siempre `\urlDemoWeb` y `\siHayDemoWeb{con}{sin}`; `entregables/datos/despliegue.tex` **lo ignora git** y solo define el valor, escrito por `scripts/escribir_url_demo.sh` preguntando a `gcloud`. Sin ese archivo el documento compila igual y dice, en lugar del enlace, que la dirección se entrega junto con el documento. Un detalle que no es cosmético: el condicional se resuelve **una sola vez en el preámbulo**, no dentro del cuerpo de las macros, para que en el punto de uso solo quede texto y ningún `\if` vivo llegue a una celda de `tabularx`. Verificado en los dos escenarios con cero errores de TeX.

**`us-resolved/` y `us-research/` no existen.** Las fases 1 y 2 del flujo prometen escribir ahí y nunca se produjo ninguno: lo que se investiga y se decide de una US vive en `us-handoff/` y `us-planning/`. No los busques.

**Si repartes trabajo LaTeX entre varios agentes, dales `-outdir` distinto.** Varios `latexmk` sobre el mismo `main_*.tex` en `entregables/` se pisan el `.aux`, el `.fdb_latexmk` y el `.pdf`, y cada agente acaba leyendo errores ajenos como propios. La convención es `latexmk -xelatex -outdir=tmp/<letra> main_X.tex`; `entregables/tmp/` ya está en `.gitignore`.

Hoy hay 324 archivos versionados bajo `docs/`; el resto de lo que verás en disco son auxiliares de LaTeX, figuras generadas y material de terceros, todo ignorado a propósito.

## Mapa de la carpeta

| Ruta | Qué es | Quién la escribe |
|------|--------|------------------|
| `entregables/` | Fuente única de A1–A5: `main_a*.tex`, `main_completo.tex`, `main_manual.tex`, `contenido/`, `estilo/`, `figuras/`, `datos/`, `imagenes/`. Un párrafo vive una vez y se compone en la entrega semanal y en el acumulado | `deliverable-writer` |
| `entregables/tmp/` | Salidas de `latexmk -outdir`, una por agente cuando el trabajo se reparte. Ignorada por git; se borra sin pensarlo | quien compila |
| `entregables/datos/` | Insumos de datos del documento: `a3_tarjetas.csv`, `a4_tokens.json` (generado) y el contrato del demo, `demo.tex` versionado más `despliegue.tex` ignorado | la US dueña |
| `semana_1/` … `semana_5/` | El PDF subido a Canvas y el `plan_*_excelencia.md` o `planeacion_excelencia.md` de esa semana | quien entrega |
| `papers/` | Los 10 artículos arXiv 2026 y el `README.md` con sus identificadores | nadie: se cita, no se edita |
| `orchestration/` | `auto-invoke.md`, `skills-catalog.md`, `skill-owners.md`, `commands.md`, `checklist-ui.md`: la maquinaria del harness | el orquestador |
| `decisions/` | ADR: una decisión fechada por archivo, con su contexto y sus consecuencias. La raíz guarda la regla; el porqué vive aquí. Un ADR no se edita cuando cambia de opinión: se escribe otro que lo derogue | quien toma la decisión |
| `us-handoff/` | Un `us-XXX.md` por US; lo abre la fase 1 y lo actualiza cada fase | todos los subagentes |
| `us-planning/` | Criterios, archivos exactos, write-sets y plan de tests | fase 2 |
| `manual-test/` | Pasos que exigen navegador real o juicio humano | fase 4 |
| `us-backlog/` | Hallazgos fuera del alcance de la US en curso, con la US que los absorbe | quien lo descubre |
| `catalogo-semantico.md`, `espacios-de-trabajo.md`, `security.md` | Normativos, escritos a mano; el código los implementa y los tests los fijan | la US dueña |
| `general/` | Rúbricas, lecturas y prompts del harness. **Fuera de control de versiones a propósito**: `.gitignore` excluye `docs/general/` por ser material con derechos de autor | fuera del repo |

## Convenciones

- ❌ Tocar los entregables ya calificados: `contenido/a1_*.tex`, `a2_*.tex`, `a3_*.tex` y los PDF de `semana_1..3`. Ya se entregaron y se calificaron; ese PDF es el registro de lo evaluado. **Única excepción, [ADR-005](decisions/ADR-005-correcciones-de-maquetacion-para-la-entrega-final.md)**: correcciones de **maquetación** derivadas de retroalimentación explícita del evaluador y aplicadas para la integración de A5 —saltos de página, espaciado vertical de un bloque, y recorte de viñetas redundantes solo si el bloque rebasa su página—. El contenido evaluado no se reescribe, los PDF entregados no se regeneran, y **no se insertan `\label` ni otros ganchos técnicos**: el mapa de cumplimiento resuelve esas filas leyendo `main_completo.toc` justamente para no abrir los archivos congelados. Cada corrección se anota en el handoff junto a la retroalimentación que la justifica; sin retroalimentación citada, no hay excepción. Lo ejecutado bajo este ADR es un `\clearpage` antes de cada competidor de `a3_01_analisis_competitivo.tex`, y nada más.
- ❌ Escribir en tiempo futuro. Los entregables describen lo que existe, no lo que se hará: un paso redactado en futuro baja su criterio de "Completo" a "Parcialmente".
- ❌ Derivar el aspecto del portal de `estilo/uxdoc.sty`: es la hoja de estilo **del informe** y está **congelada** (decisión del 11-ago-2026).
- ❌ Cifras sin origen. Cada afirmación empírica sale de un dato del equipo o de una cita APA de `papers/`; lo no medido se rotula pendiente o hipótesis.
- ✅ Sección nueva de A4 → `contenido/a4_NN_*.tex`. `main_a4.tex` incluye `a4_00` a `a4_08`: si tu sección es una de esas, **no edites la lista de `\input`**. Si es una `a4_09` o posterior, la línea no existe y hay que añadirla **a los dos envoltorios**, `main_a4.tex` y `main_completo.tex`, en su lugar editorial y no al final por comodidad.
- ✅ Compilar desde `entregables/` con XeLaTeX, dos pasadas: `latexmk -xelatex main_a4.tex`.
- ✅ Copiar el PDF a `semana_N/` con el nombre exacto que exige la actividad.
- ✅ Cada actividad abre retomando la anterior y cierra anticipando la siguiente.
- ✅ Hallazgo fuera de alcance → `us-backlog/NN-slug.md` más su renglón en el `README.md` de esa carpeta.

## No tocar

- PDF de `semana_1..3` y sus fuentes `a1_*`, `a2_*`, `a3_*` — entregados y calificados.
- `estilo/uxdoc.sty` — congelada.
- `estilo/a4_tokens.tex` y `datos/a4_tokens.json` — los genera `make tokens`; `make verificar` los rediff.
- `figuras/*.png` — salen de `figuras/generar_figuras.py`, `generar_figuras_a2.py` y `generar_figuras_a3.py`: edita el script, no el PNG.
- `figuras/a4/{antes,despues}/*.png` — **capturas, no diagramas**: las produce `capturas/capturas_a4.mjs` contra el portal vivo, y el protocolo que las hace reproducibles es `capturas/guion_a4.md`. Recapturar, jamás retocar. `antes/` es **irrecuperable**: documenta el estado previo a la iteración del CA-6 y no puede volver a tomarse.
- **Cuál es el juego de capturas vigente, porque el nombre engaña** (hallazgo de US-AVANCE-5, 22-ago-2026). `despues/` **no** es «el portal de ahora»: es el par de `antes/` en aquella comparación, y dos de sus ocho imágenes documentan pantallas que ya no existen así. `despues/2_exploracion_normal.png` es la pantalla **marcador de posición**, con el rótulo «CONTENIDO DE US-008» y un texto en futuro («Contendrá el catálogo temático…»); `despues/0_acceso_normal.png` y `1_inicio_normal.png` traen el chasis anterior, sin buscador ni control de Apariencia en la cabecera. El juego que retrata el producto operable es **`figuras/a4/tema/institucional_*`**, que es el que publica `a4_02_prototipos.tex`. Para ilustrar cualquier documento nuevo, usa `tema/`; usar `despues/` haría que el texto contradijera su propia figura.
- `figuras/a5/*.png` — capturas de US-AVANCE-5 tomadas contra el portal desplegado en Cloud Run con sesión de perfil analista, para el manual de uso. `tableros_analista.png` es la pantalla `/exploracion/tableros`, la única de las siete que no tenía captura; `serie_observado_proyectado.png` es el detalle que distingue dato observado de proyección, ilustración directa del hallazgo H1 y de la recomendación R1. Recapturar contra el portal, jamás retocar.
- `semana_4/figuras/` — generadas, ignoradas por git.
- `figuras/a4/iconos/*.png`, `estilo/a4_iconos.tex` y `estilo/a4_iconos_declarados.tex` — los emite `figuras/generar_iconos_a4.mjs` desde el inventario del portal. Edita el guion o el inventario del codigo, jamas la salida: un glifo retocado a mano dejaria de ser el que la interfaz dibuja.
- Auxiliares LaTeX (`.aux`, `.log`, `.fls`, `.fdb_latexmk`, `.toc`, `.out`, `.xdv`) y `main_a*.pdf` — ignorados, se regeneran.
- `general/` y `papers/*.pdf` — material de terceros fuera del repositorio.

## Skills

| Acción | Skill |
|--------|-------|
| Redactar o maquetar el documento de una actividad, o absorber una rúbrica recién publicada (protocolo §25.2) | `portal-ux-deliverables` |
| Instrumentos, personas, escenarios, journey maps, SUS | `portal-ux-research` |
| Benchmark competitivo, sitemap, card sorting | `portal-ux-research` + `portal-ux-deliverables` |
| Guía de estilos y pantallas de alta fidelidad (A4) | `portal-ux-patterns` + `portal-frontend-components` |
| Pre-validación sintética de pantallas | `portal-synthetic-users` |
| Revisar defectos de interfaz | [`orchestration/checklist-ui.md`](orchestration/checklist-ui.md) (archivo, no skill) |
