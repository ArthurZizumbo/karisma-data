# docs/ — Entregables del curso, orquestación y artefactos por User Story

> Sub-guía del orquestador. Las reglas transversales viven en [`../AGENTS.md`](../AGENTS.md) — aquí no se repiten, solo lo operativo de `docs/`.

## Estado

**Tres de cinco actividades entregadas y calificadas.** A1 (26-jul, 15/15, con la observación de maquetación ya corregida), A2 (2-ago) y A3 (9-ago). El PDF subido a Canvas está en `semana_1/`, `semana_2/` y `semana_3/` como `Entregable Actividad N_equipo_8.pdf`; su fuente vive en `entregables/contenido/a1_*.tex`, `a2_*.tex` y `a3_*.tex`. Material cerrado.

**A4 en curso, entrega el 16-ago.** `entregables/main_a4.tex` declara **nueve** `\input` en su orden final, casi todos envueltos en `\IfFileExists` para compilar a media semana, y **los nueve existen**: `a4_03_guia_estilos.tex` y `a4_06_cierre.tex` son de US-UX-09, seis de US-UX-07 y `a4_08_tema_y_flujos.tex` de US-ENTREGA-A4 (14-ago-2026), que lo colocó **entre `a4_05` y `a4_06`** porque es cuerpo, no anexo. `semana_4/` **ya tiene su PDF de entrega** con el nombre que exige la actividad, junto a `plan_excelencia.md` y las figuras generadas. `main_completo.tex` incorpora la parte IV y carga `estilo/a4_tokens` en el preámbulo, porque reutiliza `a4_03` y sin esa línea faltan ocho secuencias de control.

**El documento de A4 se compactó a documentación ejecutiva** (US-A4-EXCELENCIA, 16-ago-2026). Dos reglas nuevas que ahorran buscar. Primera: **el sistema de diseño se documenta en un solo sitio**, `a4_03_guia_estilos.tex`, cuyo capítulo «Especificación del sistema de tokens y paleta institucional» absorbió la paleta institucional, su matriz de contraste y la de dicromacias; su capítulo de marca absorbió además la normativa del logotipo. `a4_08_tema_y_flujos.tex` **conserva el nombre pero ya solo publica los cinco flujos de tarea** y su verificación técnica, **cada pie con la palabra diseño** para que ninguna lámina se lea como captura del portal. Segunda: **el documento no narra su propio desarrollo**. No se escribe «iteración», no se cita la rúbrica, no se justifica por qué una figura no se rehizo; los hallazgos se publican como decisiones de diseño con su medición, agrupadas en tres ejes técnicos. Las capturas de la sección de prototipos son las del **tema institucional en ejecución**. **Disciplina de saltos, pedida por el evaluador**: un bloque visual no se parte ni comparte página. Hay un `\clearpage` antes de cada uno de los siete prototipos y del chasis común en `a4_02`, y otro antes de cada uno de los cinco flujos y de la verificación técnica en `a4_08`. Sin ellos las capturas del portal ---que ocupan cerca de media caja de texto--- no caben junto a su texto, el flotante aterriza una página más tarde y una página acaba con dos titulares y ninguna figura. Está medido, no supuesto. Cuidado con una trampa real: el paso 4 de `scripts/verificar_tokens_a4.sh` corre `grep -lE '#[0-9A-Fa-f]{6}'` sobre **todos** los `contenido/a4_*.tex` y un solo hexadecimal con almohadilla lo pone en rojo — los colores se publican como `	exttt{0B1B2B}`, sin almohadilla.

**Las capturas del prototipo son un artefacto nuevo** (US-UX-07). `entregables/capturas/` trae el protocolo escrito, `guion_a4.md`, y su ejecutable `capturas_a4.mjs`, que deriva el plan de captura de `PROTOTIPOS` parseando `frontend/app/utils/navegacion.ts` como texto. Salida en `figuras/a4/{antes,despues}/`, pareadas por nombre de archivo. Dos pruebas del frontend, `rutaRama.spec.ts` y `alcancePrototipos.spec.ts`, **leen `.tex` de `contenido/`** y los comparan contra el contrato de navegación: un `.tex` de esta carpeta puede poner la suite del frontend en rojo.

**Los iconos de la guia de estilos se imprimen, no se describen** (19-ago-2026, observacion del evaluador de A4). El punto 9.5 salia con el titular y nada debajo: su tabla era un flotante que aterrizaba una pagina mas tarde, ya pasada la 9.6, y ademas nombraba los iconos en prosa sin mostrar ni uno. La Tabla 28 ahora imprime **los 27 glifos** del inventario con su nombre y su rotulo accesible, y se compone con `uxtablalarga` -xltabular, NO flotante, repite encabezado al partirse-, que es lo unico que garantiza que un titular no vuelva a quedarse sin su tabla. La emite `figuras/generar_iconos_a4.mjs` desde `inventarioIconos.ts` y `i18n/locales/es.json`, rasterizando con el Chromium de Playwright. **La estructura de la seccion 9 no cambio**: siguen siendo las mismas seis subsecciones. Un primer intento agrego una 9.6 con rutas `.vue` y el comportamiento del empaquetador y **se revirtio**: el evaluador ya habia senalado que el trabajo brinca a la etapa de desarrollo, y una guia de estilos no publica rutas de archivos de codigo. Dos hechos que la revision dejo escritos: el grosor de trazo real es de **dos unidades sobre un lienzo de 24** -2 px a 24 px y 1,33 px a 16 px-, no el 1,5 px uniforme que la guia declaraba; y la interfaz usa 65 iconos distintos frente a los 27 declarados, diferencia que el documento resume en una frase, sin catalogo.

**A5 (23-ago) no ha empezado**: no hay `semana_5/` ni `main_a5.tex`. **`us-resolved/` y `us-research/` no existen.** Las fases 1 y 2 del flujo prometen escribir ahí y nunca se produjo ninguno: lo que se investiga y se decide de una US vive en `us-handoff/` y `us-planning/`. No los busques.

De los 281 archivos, 175 están versionados; el resto son auxiliares de LaTeX, figuras generadas y material de terceros.

## Mapa de la carpeta

| Ruta | Qué es | Quién la escribe |
|------|--------|------------------|
| `entregables/` | Fuente única de A1–A5: `main_a*.tex`, `main_completo.tex`, `contenido/`, `estilo/`, `figuras/`, `datos/`, `imagenes/`. Un párrafo vive una vez y se compone en la entrega semanal y en el acumulado | `deliverable-writer` |
| `semana_1/` … `semana_4/` | El PDF subido a Canvas y el `plan_*_excelencia.md` de esa semana | quien entrega |
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

- ❌ Tocar los entregables ya calificados: `contenido/a1_*.tex`, `a2_*.tex`, `a3_*.tex` y los PDF de `semana_1..3`. Ya se entregaron y se calificaron; ese PDF es el registro de lo evaluado.
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
