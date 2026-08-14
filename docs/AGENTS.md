# docs/ — Entregables del curso, orquestación y artefactos por User Story

> Sub-guía del orquestador. Las reglas transversales viven en [`../AGENTS.md`](../AGENTS.md) — aquí no se repiten, solo lo operativo de `docs/`.

## Estado

**Tres de cinco actividades entregadas y calificadas.** A1 (26-jul, 15/15, con la observación de maquetación ya corregida), A2 (2-ago) y A3 (9-ago). El PDF subido a Canvas está en `semana_1/`, `semana_2/` y `semana_3/` como `Entregable Actividad N_equipo_8.pdf`; su fuente vive en `entregables/contenido/a1_*.tex`, `a2_*.tex` y `a3_*.tex`. Material cerrado.

**A4 en curso, entrega el 16-ago.** `entregables/main_a4.tex` declara los ocho `\input` en su orden final, envueltos en `\IfFileExists` para compilar a media semana; hoy solo existen `contenido/a4_03_guia_estilos.tex` y `contenido/a4_06_cierre.tex`. `semana_4/` aún no tiene PDF de entrega, solo `plan_excelencia.md` y figuras generadas.

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
- ✅ Sección nueva de A4 → `contenido/a4_NN_*.tex`. `main_a4.tex` ya la incluye: no edites su lista de `\input`.
- ✅ Compilar desde `entregables/` con XeLaTeX, dos pasadas: `latexmk -xelatex main_a4.tex`.
- ✅ Copiar el PDF a `semana_N/` con el nombre exacto que exige la actividad.
- ✅ Cada actividad abre retomando la anterior y cierra anticipando la siguiente.
- ✅ Hallazgo fuera de alcance → `us-backlog/NN-slug.md` más su renglón en el `README.md` de esa carpeta.

## No tocar

- PDF de `semana_1..3` y sus fuentes `a1_*`, `a2_*`, `a3_*` — entregados y calificados.
- `estilo/uxdoc.sty` — congelada.
- `estilo/a4_tokens.tex` y `datos/a4_tokens.json` — los genera `make tokens`; `make verificar` los rediff.
- `figuras/*.png` — salen de `figuras/generar_figuras.py`, `generar_figuras_a2.py` y `generar_figuras_a3.py`: edita el script, no el PNG.
- `semana_4/figuras/` — generadas, ignoradas por git.
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
