# Handoff US-AVANCE-5 — Entrega final A5: métricas UX, prueba de usabilidad y documento acumulado

**Estado**: coding
**Epic**: EPIC UX
**Actividad**: A5 (dom 23-ago-2026 23:59; meta interna dom 20:00)
**Sprint**: S5
**Rama**: `us-avance-5`
**SHA base**: `e257131`
**Última fase**: 7, integración — 22-ago-2026

> El diff de esta US se mide **siempre** con `git diff --name-only e257131`, nunca con `HEAD~N`.

Plan de ejecución completo: [`docs/semana_5/planeacion_excelencia.md`](../semana_5/planeacion_excelencia.md).
Write-sets y plan de pruebas: [`docs/us-planning/us-avance-5.md`](../us-planning/us-avance-5.md).

---

## Dominios y sub-tareas tocados

- [ ] backend  - [ ] frontend  - [ ] ml  - [ ] db  - [x] tests  - [x] docs
- Sub-tareas paralelas (todas en `docs/`, write-sets disjuntos):
  - **A · métricas** — `contenido/a5_06_metricas.tex` (criterio 14, 15 %)
  - **B · usabilidad** — `contenido/a5_04_usabilidad.tex` (criterio 15, 20 %)
  - **C · cierre** — `contenido/a5_05_cierre.tex` (criterio 16, 5 %)
  - **E · maquetación A3** — `contenido/a3_01_analisis_competitivo.tex` (retro núm. 2)
  - **F · manual de uso** — `contenido/a5_07_manual.tex` + `main_manual.tex`
  - **D · envoltorio** (después de A, B, C, E, F) — `main_completo.tex` + `contenido/a5_00_preliminares.tex`

---

## CONTRATO COMPARTIDO — léelo antes de escribir una línea

Lo escribió la Fase 3 antes de repartir. Nadie lo modifica: se consume.

### C1. Cifras verificadas (aritmética comprobada, no la recalcules ni la cambies)

SUS de los cinco participantes: **87.5 · 82.5 · 82.5 · 92.5 · 100.0**

| Estadístico | Valor | Cómo se obtuvo |
|---|---|---|
| Media | **89.0** | 445.0 / 5 |
| Desviación estándar (muestral, n menos 1) | **7.42** | varianza 55.0 |
| Error estándar | 3.32 | 7.4162 entre raíz de 5 |
| t crítica (95 %, gl = 4) | 2.776 | tabla t de dos colas |
| Margen | 9.21 | 2.776 por 3.3166 |
| **IC 95 %** | **[79.8, 98.2]** | incluso el límite inferior supera 75 y el promedio de referencia de 68 |

Sub-escala de **aprendizabilidad** (ítems 4 y 10, únicos participantes con respuestas por
reactivo conservadas): A1 = **75.0**, A2 = **87.5**, A3 = **100.0**.
Sub-escala de **usabilidad** (los otros ocho ítems): A1 = 84.4, A2 = 93.8, A3 = 100.0.

Bloque A (C y V, seis tareas): 11/12 éxitos = **91.7 %**; tiempo medio **59.5 s**; **7** errores;
**0** ayudas; SEQ promedio **5.8/7** (tablero 4.5, el más bajo).
Bloque B (A1–A3, recorridos): 3/3 completados sin ayuda; facilidad media **6.0/7**; 30–45 min.
Tiempos por tarea (C/V): T1 24/29 · T2 51/62 · T3 64/79 · T4 76/94 · T5 49/57 · T6 58/71.
T4 de V fue éxito **parcial** con 2 errores; es el único no-éxito del estudio.

Fecha única de la prueba: **jueves 20 de agosto de 2026**. Nombres autorizados: solo **C**
(Carlos René Flores M.) y **V** (Verónica Itzel Flores González). A1, A2 y A3 son anónimos y
**no se les añade ningún dato identificable nuevo**.

### C2. Las siete interfaces de A4 (criterio 14 exige al menos una métrica por cada una)

Acceso por perfil · Inicio · Exploración y extracción (con 2.4 Tableros e indicadores) ·
Gobierno del dato · Asistente conversacional · Administración · Exportación.

`Inicio` y `Gobierno del dato` **no tuvieron tarea cronometrada propia**. Su métrica se declara
con meta y se reporta lo realmente observado (H2, H6, T2 y T5); donde no hubo medición se rotula
**«instrumentada, medición pendiente»**. Ninguna celda inventa una medición que no ocurrió.

### C3. Dirección del demo — macros ya disponibles

`docs/entregables/datos/demo.tex` ya existe, ya se carga desde `main_a5.tex` y D lo cargará en
`main_completo.tex`. Ofrece:

- `\urlDemoWeb` — el enlace, o el respaldo en prosa «la dirección pública se entrega junto con
  este documento». **No usarla dentro de `\caption` ni de otro argumento móvil.**
- `\siHayDemoWeb{con dirección}{sin dirección}` — dos redacciones completas cuando la frase
  cambia de forma y no solo de dato.

El valor vive en `datos/despliegue.tex`, que git ignora y produce
`bash scripts/escribir_url_demo.sh`. **Nadie escribe ese archivo ni la URL literal en un `.tex`.**

### C4. Contrato de etiquetas (`\label`) — para el mapa de cumplimiento de D

Cada agente coloca **exactamente** estas etiquetas en su archivo, justo después del titular:

| Etiqueta | Titular | Dueño |
|---|---|---|
| `sec:a5-metricas` | `\section{Descripción de métricas UX}` | A |
| `sec:a5-usabilidad` | `\section{Prueba de usabilidad}` | B |
| `sec:a5-conclusiones` | `\section{Conclusiones generales}` | C |
| `sec:a5-referencias` | `\section{Referencias bibliográficas}` | C |
| `sec:a5-manual` | `\uxsection{Anexo B. Manual de uso del prototipo}` | F |
| `sec:a5-producto` | `\section{Descripción del producto}` (en `a5_00`) | D |

Nadie define etiquetas fuera de su archivo. Las de A1–A2–A4 **no se añaden**: esos `.tex` están
congelados y el mapa de cumplimiento resuelve esas filas leyendo `main_completo.toc`.
Una etiqueta va **después** del titular y antes del primer párrafo. Tras `\uxsection`, que es
`\section*`, hay que anteponer `\phantomsection` para que `\pageref` apunte bien.

### C5. Fuentes nuevas que se citan esta semana (APA, en español)

- Albert, B., y Tullis, T. (2013). *Measuring the User Experience: Collecting, Analyzing, and
  Presenting Usability Metrics* (2.ª ed.). Morgan Kaufmann. — **caps. 3 a 8**, lectura del curso.
  Cap. 3 tipos de estudio · cap. 4 desempeño · cap. 5 problemas (frecuencia por severidad) ·
  cap. 6 auto-reportadas (SUS, SEQ) · cap. 7 conductuales y fisiológicas (se **descartan con
  causa**) · cap. 8 combinadas y comparativas.
- Avenir-UX: Automated UX Evaluation via Simulated Human Web Interaction with GUI Grounding
  (arXiv:2604.09581, 2026) — encuadra la cadena pre-validación sintética a prueba humana.
- HARP: The Human-AI Research Platform (arXiv:2607.20773, 2026) — diseño de dos bloques y T5.
- Usability Evaluation and Improvement of a Tool for Self-Service Learning Analytics
  (arXiv:2603.24321, 2026) — precedente de dominio; ciclo medir, corregir, retestar (R7).
- Paper ancla 08: PerceptUI (arXiv:2606.05697, 2026), ya en `docs/papers/README.md`.

Los tres papers de 2026 **se citan por identificador arXiv y año**; si no puedes verificar autores,
cita el trabajo por título e identificador y no inventes nombres. Ninguna cita decorativa.

### C6. ADR

El ADR que autoriza tocar `a3_01` es **ADR-005**, no ADR-003: `ADR-003` y `ADR-004` ya existen
con otro contenido. Lo escribe la Fase 7 (integración), no los agentes.

---

## Guías que quedaron viejas

> Lo escribe cada agente al salir; la integración lo usa para poner al día el 'Estado' de cada guía.

**Cerrado en la fase 7.** `docs/AGENTS.md` y su espejo `docs/CLAUDE.md` se reescribieron y quedaron
byte-idénticos. Lo que se corrigió, y que los agentes habían señalado uno por uno:

- **Estado**: decía que A5 no había empezado. Ahora describe el cambio de vehículo al acumulado, el
  orden editorial de la Parte V, el contrato de la dirección del demo, las 305 páginas y el mapa de
  cumplimiento del folio 12. También pasa A4 de «en curso» a entregada.
- **Convenciones**: la línea que prohíbe tocar `a1/a2/a3` recoge ahora la excepción de ADR-005 con
  su límite exacto, incluida la prohibición de insertar `\label`.
- **No tocar**: entra el hallazgo del agente F sobre `figuras/a4/despues/`, que el nombre hace pasar
  por vigente y no lo es, y la nueva `figuras/a5/`.
- **Mapa de la carpeta**: `entregables/tmp/`, `entregables/datos/` y `main_manual.tex`.
- De paso, dos defectos preexistentes: `	exttt{0B1B2B}` aparecía con un tabulador en vez de la
  barra invertida, y el conteo de archivos estaba obsoleto.

Queda **fuera de esta US** y anotado en el backlog: `backend/AGENTS.md` y `frontend/AGENTS.md` ya no
coinciden con sus `CLAUDE.md`. Ver [`us-backlog/12-espejos-de-guia-divergentes.md`](../us-backlog/12-espejos-de-guia-divergentes.md).

## Archivos tocados

> Snapshot de cierre. El diff se mide con `git diff --name-only e257131`.

| Archivo | Qué | Autor |
|---|---|---|
| `docs/entregables/main_completo.tex` | portada de A5, «Introducción general», sección «Mapa de cumplimiento de la entrega», Parte V y sus anclas `cmp:*`, `\UrlBreaks`, `\stepcounter` del Anexo B | D, integración |
| `docs/entregables/contenido/a5_06_metricas.tex` | **nuevo** — criterio 14 (15 %): marco, nueve filas de métrica por interfaz, matriz severidad × frecuencia, IC del SUS | A |
| `docs/entregables/contenido/a5_04_usabilidad.tex` | criterio 15 (20 %): tabla de los 10 pasos, correspondencia tarea ↔ interfaz ↔ función, materiales con el producto real, defensa de n=5 | B, integración |
| `docs/entregables/contenido/a5_05_cierre.tex` | criterio 16: conclusiones del proyecto, cierre del círculo contra A2, 37 referencias APA, Anexo A | C |
| `docs/entregables/contenido/a5_07_manual.tex` | **nuevo** — Anexo B, manual de uso: perfiles, doce apartados, ejemplos de T1 a T6 | F |
| `docs/entregables/main_manual.tex` | **nuevo** — envoltorio del manual como PDF propio, 22 páginas | F |
| `docs/entregables/contenido/a5_00_preliminares.tex` | puente de la Parte V y eco ejecutivo del producto, con `sec:a5-producto` | D |
| `docs/entregables/contenido/a3_01_analisis_competitivo.tex` | siete `\clearpage`, un competidor por página. **Cero líneas de contenido tocadas** | E |
| `docs/entregables/datos/demo.tex` | **nuevo** — contrato de `\urlDemoWeb` y `\siHayDemoWeb` | Fase 3 |
| `docs/entregables/datos/despliegue.tex.example` | **nuevo** — plantilla del valor ignorado por git | Fase 3 |
| `docs/entregables/main_a5.tex` | carga `datos/demo` y `a5_06_metricas`; queda como plan B | Fase 3 |
| `docs/entregables/figuras/a5/tableros_analista.png` | **nuevo** — captura de `/exploracion/tableros`, la séptima pantalla, que no tenía ninguna | Fase 3, Playwright |
| `docs/entregables/figuras/a5/serie_observado_proyectado.png` | **nuevo** — detalle observado frente a proyectado, ilustración de H1 y R1 | Fase 3, Playwright |
| `scripts/escribir_url_demo.sh` | **nuevo** — escribe `datos/despliegue.tex` desde `gcloud` | Fase 3 |
| `scripts/verificar_url_demo.sh` | **nuevo** — barrera de privacidad, en `make check` y `make verificar` | TESTS |
| `scripts/verificar_contrato_demo.sh` | **nuevo** — compila el contrato en los dos escenarios, en `make verificar` | TESTS |
| `Makefile` | engancha las dos verificaciones nuevas | TESTS |
| `.gitignore` | ignora `datos/despliegue.tex`, versiona su `.example` | Fase 3 |
| `docs/decisions/ADR-005-correcciones-de-maquetacion-para-la-entrega-final.md` | **nuevo** — la excepción que autoriza el trabajo de E | Integración |
| `docs/AGENTS.md` y `docs/CLAUDE.md` | Estado, Convenciones, No tocar y Mapa de la carpeta al día; espejos byte-idénticos | Integración |
| `docs/us-backlog/12-espejos-de-guia-divergentes.md` y su `README.md` | **nuevo** — hallazgo fuera de alcance | Integración |
| `docs/semana_5/Entregable Actividad 5_equipo_8.pdf` | **el entregable**: 305 páginas, cero errores, cero `??` | Integración |
| `docs/semana_5/planeacion_excelencia.md` | **nuevo** — el plan de la semana, contrato de ejecución de S5 | Previo a esta fase |
| `docs/us-handoff/us-avance-5.md` y `docs/us-planning/us-avance-5.md` | **nuevos** — este handoff y su plan de write-sets | Fase 3 |

## Archivos existentes reutilizados

- `docs/entregables/contenido/a5_04_usabilidad.tex` — 187 líneas ya redactadas con la prueba real;
  se **mejora**, no se reescribe.
- `docs/entregables/estilo/uxdoc.sty` — congelada. Macros disponibles: `\uxsection` (titular sin
  numerar), `\uxtabla{cols}{título}`, `\uxtablalarga{cols}{título}{fila de encabezado}` (parte
  entre páginas y repite encabezado; **no es flotante**), `\uxlist` con `\lead{a}{b}`, `\uxpreg`,
  `\uxnota[título]`, `\uxdestacado`, `\uxreferencias`, `\uxparte{N}{título}{resumen}`,
  `\figuraux[ancho]{archivo}{pie}{etiqueta}`, `\figurapanoramica`, `\uxheadrow`, `\thd{}`.
  Columnas: `L{ancho}` `C{ancho}` `Y` `Z{factor}`.
- Capturas del portal real ya existentes en `figuras/a4/despues/`: `0_acceso_normal.png`,
  `1_inicio_normal.png`, `2_exploracion_normal.png`, `3_gobierno_normal.png`,
  `4_asistente_normal.png`, `4_asistente_resultado.png`, `5_administracion_normal.png`,
  `6_exploracion-exportar_normal.png`. Y los cinco flujos en `figuras/a4/flujo_*.png`.
- `scripts/verificar_despliegue.sh` y `scripts/desplegar.sh` para la evidencia del demo.

## Decisiones técnicas clave

- El vehículo de entrega es el **acumulado** `main_completo.tex` con una Parte V nueva, no el
  compacto v3. Razón: once criterios de 5 % re-evalúan artefactos de A1–A4 y la banda pide
  «se incluyen los elementos solicitados»; los resúmenes de una fila del compacto los exponían
  a «Parcialmente». `main_a5.tex` queda como plan B y como documento de trabajo.
- El capítulo de métricas se escribe como archivo independiente (`a5_06_metricas.tex`) para que
  **los dos envoltorios** puedan incluirlo y el plan B cueste cero.
- `a5_01`, `a5_02` y `a5_03` **no entran al acumulado**: duplicarían las Partes I–III con menos
  detalle. Siguen en `main_a5.tex`.
- La URL del demo entra por variable con respaldo `\IfFileExists`, resuelto **una sola vez** en
  el preámbulo: un `\if` vivo dentro de una celda de `tabularx` rompe la alineación.
- **El PDF versionado lleva la dirección impresa, y es una decisión tomada, no un descuido.** El
  mecanismo de la variable mantiene la URL fuera de los `.tex`, pero el PDF compilado la imprime
  tres veces y `docs/semana_5/Entregable*.pdf` está exceptuado en `.gitignore` a propósito. Se
  planteó compilar dos veces —uno con dirección para Canvas y otro sin ella para el repositorio— y
  **se descartó**: se entrega un solo PDF, idéntico en los dos sitios, para que el registro de lo
  evaluado sea exacto y no haya dos artefactos que confundir. El coste aceptado es que el
  identificador del proyecto de GCP queda publicado en el PDF del repositorio.
- **El Anexo B necesitó `\stepcounter{section}` en el envoltorio.** El manual abre con `\uxsection`,
  que no numera, así que sus doce apartados se colgaban del contador que dejaba abierto el Anexo A:
  el índice leía «Anexo B. Manual de uso del prototipo» y debajo «65.4», como si el manual
  continuara el anexo anterior. Adelantar el contador le da su propia decena (66.1 a 66.12) sin
  imprimir ningún titular numerado y sin tocar el archivo del manual, que compilado aparte ya
  numeraba bien.
- **Las capturas de `figuras/a4/despues/` no sirven para documentar el producto de hoy**, pese a lo
  que sugiere su nombre. `2_exploracion_normal.png` es la pantalla marcador, con el rótulo
  «CONTENIDO DE US-008» y un texto en futuro; `0_acceso` y `1_inicio` traen el chasis anterior. El
  juego vigente es `figuras/a4/tema/institucional_*`. Lo descubrió el agente F al negarse a seguir
  la instrucción que le dieron, y se verificó abriendo las imágenes.
- El **manual de uso** vive en un solo archivo, `contenido/a5_07_manual.tex`, y se compone dos
  veces: como Anexo B de la Parte V del acumulado y como PDF propio desde `main_manual.tex`.
  Es la misma convención que ya usa el repositorio (un párrafo vive una vez).

## Bugs resueltos

| Bug | Causa | Solución | Estado |
|-----|-------|----------|--------|
| El ADR planeado como «ADR-003» chocaba con dos ADR ya escritos | El plan se redactó sin releer `docs/decisions/` | El ADR de la excepción de maquetación es **ADR-005** | Resuelto en el contrato (C6) |

## Zonas sensibles

- `docs/entregables/estilo/uxdoc.sty` — **congelada**; no se edita para A5.
- `docs/entregables/estilo/a4_tokens.tex`, `a4_iconos.tex`, `a4_iconos_declarados.tex` y
  `datos/a4_tokens.json` — **generados**; los emiten `make tokens` y `figuras/generar_iconos_a4.mjs`.
- `contenido/a1_*.tex`, `a2_*.tex` y los PDF de `semana_1..3` — entregados y calificados. La
  **única** excepción de esta US es `a3_01_analisis_competitivo.tex`, y solo maquetación.
- `scripts/verificar_tokens_a4.sh` paso 4 corre `grep -lE '#[0-9A-Fa-f]{6}'` sobre **todos** los
  `contenido/a4_*.tex`: un hexadecimal con almohadilla lo pone en rojo. Se publican como
  `\texttt{0B1B2B}`.
- `frontend/tests` `rutaRama.spec.ts` y `alcancePrototipos.spec.ts` **leen `.tex` de `contenido/`**:
  tocar un `a4_*.tex` puede poner en rojo la suite del frontend. Esta US no toca ninguno.
- `figuras/a4/antes/*.png` es **irrecuperable**: documenta el estado previo a la iteración del
  CA-6 y no puede volver a tomarse. Recapturar, jamás retocar.
- `docs/entregables/datos/despliegue.tex` — fuera de control de versiones a propósito.

## Nube y datos

- Revisión de Cloud Run desplegada: **N/A** — esta US no despliega. Sí **verifica**: los dos
  servicios responden, el arranque en frío se midió en **2.44 s** y las visitas siguientes en
  0.17 s, muy por debajo del umbral de 10 s que el plan fijaba para valorar `min-instances=1`, así
  que **no se activa**. Las rutas protegidas devuelven 302 al acceso sin sesión y la puerta de los
  cuatro perfiles de demostración está activa en la instancia pública.
- Migración dbmate aplicada: **N/A** — schema.sql actualizado: **N/A**. Esta US no toca el esquema.

## Llave de provenance (cierre)

- `US-AVANCE-5 @ e257131 + run:- + db:-`

> El sha es el del árbol de trabajo en el momento del cierre de la fase 7; la rama **no se ha
> empujado**. `run:-` porque esta US no desplegó ninguna revisión nueva, solo verificó la que ya
> estaba en pie; `db:-` porque no hubo migración.

## engram-memory

- Observaciones guardadas: **sí** — palabras clave: `us-avance-5`, `a5`, `entrega-final`, `adr-005`, `url-por-variable`, `write-sets-disjuntos`, `latexmk-outdir`, `manual-prototipo`, `capturas-despues-obsoletas`.

---

## Bitácora de agentes

> Cada agente añade su bloque aquí al salir: archivos, decisiones y qué quedó viejo de su guía.

### Agente E — maquetación A3

**Retroalimentación que justifica el cambio** (ADR-005 exige citarla junto a cada corrección):
«hubiera sido muy bueno que cada competidor quedara todo dentro de una página».

**Archivos**

| Archivo | Qué |
|---|---|
| `docs/entregables/contenido/a3_01_analisis_competitivo.tex` | **modificado** — 7 líneas añadidas, todas `\clearpage`; cero líneas de contenido tocadas (`git diff --stat`: `1 file changed, 7 insertions(+)`) |

Ningún otro archivo. No se añadió ningún `\label` ni gancho técnico: el mapa de cumplimiento de
A5 resuelve estas filas leyendo `main_completo.toc`, como fija ADR-005.

**Páginas por competidor** (folio impreso, compilación de `main_a3.tex` en `tmp/e`; entre
paréntesis, el llenado vertical de la caja de texto medido sobre el PDF):

| Página | Contenido | Páginas que ocupa | Llenado |
|---|---|---|---|
| 5 | Cierre de la introducción de 1.1 (tipología de Annacchino) | — | 40 % |
| 6 | Bloomberg Terminal | **1** | 80 % |
| 7 | Microsoft Power BI | **1** | 87 % |
| 8 | Pyramid Analytics | **1** | 99 % |
| 9 | ThoughtSpot | **1** | 89 % |
| 10 | Collibra | **1** | 87 % |
| 11 | Bases aisladas, Excel y correo | **1** | 55 % |
| 12 | Otras alternativas consideradas + Tabla 2 + arranque de 1.2 | **1** | 93 % |

Los seis competidores y la ficha de cierre quedan cada uno íntegro dentro de una página: en el
`.toc` las siete entradas `1.1.1`–`1.1.7` caen en páginas consecutivas, así que ninguna ficha
desborda a la siguiente. Antes del cambio, las siete arrancaban en las páginas 5, 6, 7, 8, 9, 10
y 10, y todas se partían.

**Ajustes finos aplicados: ninguno, y está medido.** Ningún bloque rebasa su página —el `.log`
reporta **0 `Overfull \vbox`** y **0 errores**—, así que no se tocó el `\vspace{0.35cm}` que
separa la ficha de investigación de la postura, ni los `itemize`, ni se recortó una sola viñeta.
ADR-005 solo autoriza el recorte de viñetas «cuando un bloque rebasa su página por poco y no hay
otra forma de que quepa»; ninguno rebasa, luego el recorte habría sido un cambio sin
retroalimentación que lo justifique. Mercado objetivo, precios, fortalezas, debilidades,
evidencia de reseñas y estrategia de mercadotecnia siguen completos en los seis competidores.

**«Otras alternativas consideradas» sí lleva salto, y la alternativa se descartó con medición.**
Se probaron las dos variantes. Sin `\clearpage`, el titular y su párrafo caen al pie de la página
11 y la **Tabla 2 aterriza una página más tarde**, en la 12: es exactamente el defecto que el
evaluador señaló en el punto 9.5 de A4 (titular sin su tabla). Con `\clearpage`, titular, párrafo
y Tabla 2 comparten la página 12. La ficha no se forzó a llenar la página: se deja con su altura
natural y la subsección 1.2 arranca a continuación en la misma página.

**Lo que no se tocó y se verificó intacto.** Las tablas comparativas con fechas de obtención
—elogiadas por el evaluador— sobreviven enteras y sin partirse: Tabla 2 en la página 12, Tabla 3
(fuentes con su fecha de consulta) en la 14, Tabla 4 (matriz comparativa) en la 15 y Tabla 5
(principios rectores) en la 17. «Recolección de información y fuentes», «Análisis comparativo»,
«Ventaja competitiva» y «Estrategias de mejora» no recibieron ningún salto: no hizo falta.

**Verificación sobre el PDF, no sobre el código.** Compilado con
`latexmk -xelatex -interaction=nonstopmode -outdir=tmp/e main_a3.tex`, dos pasadas.
Barrido de las 59 páginas: **ningún titular queda a menos de 60 pt del pie de su página** (cero
titulares huérfanos en todo el documento) y ninguna página del análisis competitivo queda casi
vacía. Los 9 `Overfull \hbox` del `.log` (entre 2 y 19 pt) son previos y ajenos al cambio: un
salto de página no altera el corte de línea dentro de un párrafo. El PDF de `semana_3` **no se
regeneró**; sigue siendo el registro de lo evaluado.

**Efectos colaterales que debe verificar la integración sobre el acumulado.** El documento
semanal pasa de 57 a 59 páginas. Dos páginas quedan por debajo del 60 % de llenado y ninguna se
puede subir sin escribir contenido nuevo, que ADR-005 prohíbe: la 5 (40 %), que solo contiene el
cierre de la introducción de 1.1 porque la página anterior ya va al 98 % con la Tabla 1 de
trazabilidad, que vive en `a3_00`; y la 11 (55 %), donde la ficha de bases aisladas, Excel y
correo es genuinamente más corta que las demás. Además, el desplazamiento de dos páginas mueve un
flotante de página completa de `a3_02` (Figura 9) y deja la página 29 al 52 %; es un archivo
ajeno a este write-set y la paginación del vehículo real es la de `main_completo.tex`, así que se
señala para el pase de maquetación final y no se toca aquí. Página 8 (Pyramid Analytics) al 99 %
de llenado: es el bloque con menos holgura y el primero que hay que mirar en el acumulado.

**Qué quedó desactualizado de `docs/AGENTS.md`** (lo corrige la integración; ya está anotado
arriba en «Guías que quedaron viejas» y estas dos líneas lo confirman con lo ejecutado):

- **Convenciones**, línea «❌ Tocar los entregables ya calificados … `a3_*.tex`»: ya existe
  `docs/decisions/ADR-005-correcciones-de-maquetacion-para-la-entrega-final.md` y esta sub-tarea
  es su primer y único consumo. Falta la coletilla «Única excepción, ADR-005» que el propio ADR
  redacta en su sección «Regla que queda en la guía».
- **No tocar**, línea «PDF de `semana_1..3` y sus fuentes `a1_*`, `a2_*`, `a3_*` — entregados y
  calificados»: sigue siendo cierta para los PDF, que no se regeneraron, pero ya no lo es sin
  matiz para `a3_01_analisis_competitivo.tex`.
- **Estado**: dice «Tres de cinco actividades entregadas y calificadas … Material cerrado». La
  fuente de A3 dejó de ser byte-idéntica en maquetación al PDF de `semana_3` desde el 22-ago-2026;
  el ADR asume ese costo de forma explícita.
- Nada que reportar sobre `docs/entregables/AGENTS.md`: no existe; `docs/AGENTS.md` es la guía que
  cubre esta carpeta.

### Agente B — usabilidad

**Archivos**: `docs/entregables/contenido/a5_04_usabilidad.tex` (el único; +140 −12 líneas sobre
las 187 existentes). Ningún dato de la prueba cambió: participantes, tiempos, SEQ, SUS, H1–H8 y
R1–R7 siguen tal cual, y las 12 líneas borradas son titulares que solo recibieron su `\label` más
R7, que ganó una cláusula.

**Qué se añadió** (mejoras a–f de la sección 5.2 del plan):

- `\label{sec:a5-usabilidad}` en el titular, según C4. Además, una etiqueta por subsección
  (`subsec:usab-*`) y dos de tabla (`tab:usab-diez-pasos`, `tab:usab-interfaz-tarea`): la tabla de
  palomeo cita números que resuelve LaTeX, no números escritos a mano, porque el apartado se
  numera 12 en `main_a5` y toma otro número dentro del acumulado. Ninguna referencia lleva número
  literal. El `\label` de tabla viaja dentro del título del entorno (`\uxtablalarga{...}{Título\label{...}}{...}`),
  que es el único punto de anclaje disponible sin tocar `uxdoc.sty`.
- **Tabla 14** — los diez pasos de la instrucción, uno por fila, con el apartado que los cubre y
  la evidencia principal. Cabe entera en una página.
- **Tabla 16** — correspondencia interfaz de A4 ↔ funcionalidad principal ↔ prueba que la
  ejercita ↔ métrica y resultado observado, con las siete interfaces. `Inicio` y `Gobierno del
  dato` llevan la leyenda «sin tarea cronometrada propia» y reportan lo observado (H2, H6 y T2),
  tal como fija C2. Va precedida por la frase que responde literalmente la exigencia de la
  actividad.
- **Materiales** — el material de prueba fue el producto real desplegado; la dirección entra solo
  por `\urlDemoWeb` y en prosa, nunca en un `\caption`. Se declara la versión fijada antes de la
  primera sesión, el entorno (web pública en Cloud Run, API privada, PostgreSQL administrada),
  los datos sintéticos de semilla 20260720 y las mediciones de arranque en frío del 22-ago-2026
  (2.4 s la primera visita, 0.17 s las siguientes) con su fecha, más la redirección al acceso de
  las rutas protegidas.
- **Métricas** — elección por objetivo con Albert y Tullis (2013, caps. 4, 6 y 8) y descarte
  **con causa** de las conductuales y fisiológicas del cap. 7; retención y conversión fuera por
  tratarse de sesión única; la accesibilidad se remite a la verificación de contraste de A4.
- **Cadena sintético → real** — párrafo de método que hila los ocho evaluadores prototipo de A3 y
  A4 (PerceptUI, Bougie et al., 2026) con esta prueba humana, encuadrada con Avenir-UX
  (arXiv:2604.09581, 2026), y el diseño de dos bloques y T5 con HARP (arXiv:2607.20773, 2026).
  Queda escrito que SUS y SEQ se aplicaron solo a personas y que ninguna cifra sintética se
  promedia con las suyas.
- **Limitaciones** — defensa de n = 5 como estudio de descubrimiento de problemas (Albert y
  Tullis, 2013, cap. 3), reconocimiento de frente del referente que sugiere 8 a 10 participantes
  (Ramírez Mejía, 2023) y respuesta con tres elementos: el IC 95 % [79.8, 98.2] de C1, las
  frecuencias en absolutos de H1–H8 y el retest R7 con muestra ampliada hacia perfiles
  principiantes, sostenido por el ciclo medir-corregir-retestar de arXiv:2603.24321.

**Decisiones**

1. Las cifras salen íntegras de C1 y no se recalculó ninguna. El IC se cita y su aritmética se
   remite al apartado «Descripción de métricas UX» (agente A) para no duplicar el cálculo ni
   arriesgar dos versiones del mismo número.
2. **La rúbrica no se nombra dentro del entregable**: `docs/AGENTS.md` fija que el documento no
   narra su propia evaluación. La frase «en consecuencia, al menos una prueba de usabilidad
   relacionada con la funcionalidad principal de esa interfase» se responde palabra por palabra
   atribuyéndola a «la instrucción de la actividad», que es el enunciado del trabajo y no la
   plantilla de calificación.
3. R7 recibió la cláusula «ampliar la muestra hacia perfiles principiantes», que ya estaba en
   `a5_05_cierre`. Es plan declarado, no dato de la prueba.
4. Dos afirmaciones nuevas son inferencias del propio texto y conviene que la revisión cruzada las
   confirme con quien moderó: (a) el registro fue por notas de observación, sin grabación de audio
   ni de video —se deduce de que no se reconstruyeron tiempos ni errores «que no quedaron
   anotados»—; (b) los comentarios expresados en voz alta son la fuente de H1–H4 y H7, que es lo
   que sostiene el paso 7 de la instrucción.
5. Referencias que el agente C necesita en la lista consolidada: Albert y Tullis (2013),
   Ramírez Mejía (2023) y Sauro y Lewis (2016) —las tres citadas aquí— más los tres trabajos de
   2026, citados por título e identificador arXiv porque no se verificaron sus autores.

**Privacidad**: nombres solo de C y V; A1–A3 no recibieron ningún dato identificable nuevo y se
añadió el párrafo «Tratamiento de los datos personales». Queda una observación para la
integración, no una acción de esta sub-tarea: la columna «Participante o área» ya nombraba las
tres áreas de A1–A3 antes de esta US y no se tocó, porque cambiar datos de la prueba está fuera
del alcance; aun así, la combinación de área y años de experiencia puede identificar a una persona
dentro de la institución y merece una decisión explícita antes de publicar el PDF.

**Compilación**: `latexmk -xelatex -interaction=nonstopmode -outdir=tmp/b main_a5.tex` desde
`docs/entregables/`, dos pasadas: 44 páginas, cero errores, cero referencias sin resolver y cero
etiquetas duplicadas. Avisos **ajenos**, no corregidos: tres `Overfull \hbox` de unos 8 pt en
`contenido/a5_06_metricas.tex` (línea 174, columnas «Recomendación» y «Oportunidad») y un
`Float too large for page by 1.03 pt` en `contenido/a5_02_arquitectura.tex` (línea 49). Propio y
preexistente: un `Overfull \hbox` de 0.58 pt en la celda «Oportunidad» de la tabla de hallazgos,
invisible a simple vista.

**Guías desactualizadas**: `docs/AGENTS.md` — el 'Estado' afirma que A5 no ha empezado y que no
existen `semana_5/` ni `main_a5.tex`; los tres existen y `main_a5.tex` compila 44 páginas con
`a5_06_metricas` incluido. Segundo punto para la integración: ni el 'Mapa de la carpeta' ni 'No
tocar' mencionan `docs/entregables/tmp/`, que `.gitignore` excluye en su línea 177 y que esta US
usa como directorio de salida por agente para que tres compilaciones en paralelo no se pisen el
`.aux`.

### Agente C — cierre

**Archivos**: `docs/entregables/contenido/a5_05_cierre.tex` (92 → 352 líneas). Ningún otro.

**Qué produce ahora el archivo**: `\section{Conclusiones generales}` con
`\label{sec:a5-conclusiones}` (C4) en cuatro subsecciones —el arco A1→A5, el cierre del círculo,
la siguiente iteración y el cierre metodológico—, `\section{Referencias bibliográficas}` con
`\label{sec:a5-referencias}` (C4) y **37 entradas** consolidadas, y `\section{Anexo A.
Instrumentos de aplicación}` con los tres instrumentos que ya traía, renombrado para dejar libre
el rótulo del Anexo B. Tres tablas nuevas con pie numerado: recorrido del caso de estudio,
predicciones de A1–A4 frente a lo observado, y las siete recomendaciones con prioridad y criterio
de cierre.

**Decisiones**:

- **El cierre del círculo se escribe con la evidencia al lado, no como afirmación.** H2 se ancla
  en la actividad 2 del listado de la Actividad 2 —«decidir dónde buscar», dentro de la etapa de
  disparo— y en la fila «1. Disparo» de su tabla de brechas de conocimiento; H1 se ancla en el
  punto de dolor del escenario del perfil directivo (dos directores con cortes de fecha
  distintos) y en su respuesta de diseño (sello de conciliación y fecha de corte visibles). Las
  dos predicciones se declaran **confirmadas pero desplazadas**: la indecisión no se resolvió al
  entrar al portal sino que sobrevivió como duda entre dos controles de búsqueda, y la confusión
  no ocurrió entre dos cortes sino entre proyección y último dato observado. Es más defendible que
  reclamar un acierto exacto.
- **La tabla de predicciones incluye lo que no salió bien.** Ocho filas con cuatro veredictos:
  cinco confirmadas, una **matizada** (H4 sobre los valores por omisión por perfil), una
  **ampliada** (H7: los escenarios cerraban el recorrido en la extracción y un participante lo
  continuó pidiendo transformaciones ligeras) y una **sin medir** (la bitácora de accesos, la
  ruta que hizo titubear a los ocho evaluadores sintéticos y que ninguna tarea del 20-ago
  recorrió). Un cierre en el que todo se confirma no se cree.
- **Un segundo instrumento corrobora H2**: A1 obtuvo 75.0 en la sub-escala de aprendizabilidad
  frente a 84.4 en la de usabilidad (C1), la única separación apreciable de la muestra, y es el
  mismo participante que dudó qué parte utilizar primero.
- **La prioridad de R1 sobre R2 se justifica con fuente**, no por criterio del equipo: severidad
  por impacto y frecuencia son ejes distintos (Albert y Tullis, 2013, cap. 5). R1 aparece en 1 de
  5 y encabeza; R2 aparece en 3 de 5 y va segunda.
- **Referencias: se consolidó por uso real en el cuerpo, no por acumulación de listas.** Se
  revisaron las citas entre paréntesis de `a1_cuerpo`, `a2_*`, `a3_*` y `a4_*`. **Entraron** las
  que ninguna lista de A5 tenía y el cuerpo sí cita: Annacchino (2003) —verificado en tres
  párrafos de `a3_01`—, Velasco et al. (2022), Bougie et al. (2026), Peng et al. (2026), Naik et
  al. (2026), Jang y Li (2026), Tullis y Wood (2004), McInerney (2003), Spool (2005), Maioli
  (2018), de Voil (2020), Portigal (2013), Osterwalder y Pigneur (2010), Hartson y Pyla (2012) y
  las ocho fuentes de mercado del análisis competitivo (Atlan, Bloomberg, Collibra, LSEG,
  Microsoft 2024/2026a/2026b, Pyramid Analytics, ServiceNow, ThoughtSpot). **No entraron**, por
  no aparecer en el cuerpo de ninguna parte: Spencer (2009), Garrett (2010), Allen y Chudley
  (2012), Agarwal et al. (2026), Singh et al. (2026), Bai et al. (2026) y Bachkaniwala et al.
  (2026) —figuran en las listas propias de A2 y A4, que están congeladas y siguen imprimiéndolas.
- **Las cinco partes del caso guía del curso se unifican en una entrada** «Ramírez Mejía, A. I.
  (2023) … (partes 1 a 5)», porque las cuatro partes congeladas citan «(Ramírez Mejía, 2023)» sin
  letra de desambiguación y añadir 2023a–2023e en la lista habría dejado huérfanas esas citas.
- **Los tres papers de 2026 de C5 se citan por título e identificador arXiv**, sin autores: no
  están en `docs/papers/` (que solo tiene los diez de julio) y no se pudo verificar su autoría.
  Entrada y cita en texto llevan el identificador. El paper ancla 08 sí lleva autores completos
  (Bougie et al., 2026), que ya estaban verificados en las listas de A3 y A4.
- **Cada fuente nueva se cita en el cuerpo de esta sección**, para que ninguna quede decorativa:
  Albert y Tullis en la prioridad de R1 y en el orden de la iteración; Sauro y Lewis en la lectura
  del IC frente al promedio de 68; Brooke en el encabezado del cuestionario del Anexo A; PerceptUI
  y Avenir-UX en la cadena sintético→humano; HARP en el diseño de dos bloques; Self-Service
  Learning Analytics en el ciclo medir→corregir→retestar de R7.
- **Sin tiempo futuro**: el plan se describe como plan que existe («las recomendaciones quedan
  ordenadas», «el plan de la siguiente ronda incorpora»). Las únicas formas condicionales del
  archivo son los reactivos 4, 7 y 10 del cuestionario SUS, que son texto literal del instrumento.
- **El demo entra por `\siHayDemoWeb` + `\urlDemoWeb`** (C3), con dos redacciones completas.
  Verificado en el PDF: con `datos/despliegue.tex` presente imprime el enlace; ningún `.tex`
  versionado contiene la dirección literal.
- **Etiquetas**: solo las dos que C4 asigna a este agente. No se etiquetó el Anexo A, para no
  definir etiquetas fuera del contrato; si el mapa de cumplimiento de D lo necesita, sale del
  `.toc`.

**Compilación**: `latexmk -xelatex -interaction=nonstopmode -outdir=tmp/c main_a5.tex` desde
`docs/entregables/`, dos pasadas: **52 páginas, cero errores, cero referencias sin resolver, cero
`Overfull \hbox` y cero etiquetas duplicadas**. `sec:a5-conclusiones` resuelve a la sección 13
(página 42) y `sec:a5-referencias` a la sección 14 (página 48). No se ejecutó `latexmk -c`: todo
lo generado quedó en `tmp/c/`, que git ignora.

**Observación para la integración, sin acción de esta sub-tarea**: `a5_06_metricas.tex` cita en
texto el paper de analítica autoservicio con el título en mayúsculas de titular («Usability
Evaluation and Improvement of a Tool for Self-Service Learning Analytics») y la entrada
bibliográfica lo publica en formato APA, con el título en minúsculas salvo la inicial. Las dos
formas apuntan a la misma entrada y ordenan igual en la lista; unificar el criterio es cosmético y
pertenece a la pasada final, no a un archivo ajeno.

**Guías desactualizadas**: `docs/AGENTS.md` — su 'Estado' sigue diciendo que A5 no ha empezado.
Un punto adicional al ya anotado por otros agentes: la sección **'No tocar'** enumera los
generados de A4 pero no menciona que `contenido/a5_05_cierre.tex` pasó a ser **la única lista de
referencias consolidada del documento acumulado**; quien añada una cita nueva en cualquier parte
tiene que consolidarla aquí, y esa regla hoy no está escrita en ninguna guía.

---

### Agente F — manual

**Archivos** (write-set respetado, nada más tocado):

- `docs/entregables/contenido/a5_07_manual.tex` — **nuevo**. Un solo archivo, doce apartados:
  qué es y qué no es · los cuatro perfiles · cómo entrar · las siete pantallas, una por una ·
  qué se ve cuando algo no sale · preguntas frecuentes. Abre con
  `\uxsection{Anexo B. Manual de uso del prototipo}`, `\phantomsection` y `\label{sec:a5-manual}`,
  como pide el contrato C4. Registro de manual: impersonal, presente, frases cortas, sin citas ni
  marco teórico.
- `docs/entregables/main_manual.tex` — **nuevo**. Envoltorio calcado de `main_a5.tex`
  (`documentclass`, `estilo/uxdoc`, `\input{datos/demo}`, `\uxencabezado`, `\hypersetup`,
  `\uxportada`, índice) que solo incluye `contenido/a5_07_manual`.

**Compilación**: `latexmk -xelatex -interaction=nonstopmode main_manual.tex` desde
`docs/entregables/`, dos pasadas: **22 páginas, cero errores, cero referencias sin resolver y cero
`Overfull \hbox`**. Revisado página a página: **ninguna figura quedó separada de su texto y ningún
titular quedó huérfano**; las dos tablas caben enteras en su página. Limpiado con
`latexmk -c main_manual.tex`; `main_manual.pdf` lo ignora `.gitignore` por la regla
`docs/entregables/*.pdf`.

**Decisiones**

1. **Las capturas de las siete pantallas salen de `figuras/a4/tema/institucional_claro_*.png`, no
   de `figuras/a4/despues/`.** La instrucción original apuntaba a `despues/`, y esas imágenes
   documentan un estado anterior del portal: `despues/2_exploracion_normal.png` es la pantalla
   **marcador de posición** («Contendrá el catálogo temático…», «CONTENIDO DE US-008»), sin tabla
   de campos ni columna de dominios, y `despues/0_acceso_normal.png` y `1_inicio_normal.png` traen
   el chasis viejo —sin buscador ni control de Apariencia en la cabecera y con el menú de facetas
   transversales en la barra lateral—. La captura nueva del tablero contra Cloud Run confirma el
   chasis actual: cabecera con buscador, Apariencia, perfil, idioma y entorno. Publicar `despues/`
   habría hecho que el manual describiera un producto que ya no existe y que su prosa contradijera
   sus propias figuras. `tema/` es además el juego que publica `a4_02_prototipos.tex` como estado
   entregado, de modo que el vocabulario coincide entre entregas.
2. **Se usan las dos figuras nuevas de `figuras/a5/`**, capturadas por el orquestador contra el
   despliegue con sesión de analista: `tableros_analista.png` cierra el único hueco que quedaba
   —la pantalla de tableros ya no se describe solo en texto— y `serie_observado_proyectado.png`
   es el ejemplo de cómo se distingue un dato de una proyección, que es el hallazgo H1 y la
   recomendación R1.
3. **Orden de las pantallas**: Inicio · Exploración y extracción · Tableros e indicadores ·
   Exportaciones · Gobierno del dato · Asistente conversacional · Administración. Es el orden que
   pidió el encargo. `navegacion.ts` declara Exportaciones como rama **2.3** y Tableros como
   **2.4**, es decir al revés dentro del módulo 2; el manual lo dice en su propio texto («Es la
   rama 2.3 del módulo de exploración»), así que no se afirma un orden de contrato que no es.
4. **Un ejemplo real por pantalla**, tomado de la tabla de tareas de `a5_04_usabilidad.tex`:
   T1 en Cómo entrar y en Inicio, T2 en Exploración, T4 en Tableros, T3 en Exportaciones, T5 en
   Asistente y T6 en Administración. **Inicio y Gobierno del dato no tuvieron tarea cronometrada
   propia** (contrato C2) y sus recuadros lo dicen con esas palabras: Inicio se apoya en el destino
   de T1 y en H2, y Gobierno en H6, la fortaleza observada en los tres recorridos del bloque B. No
   se inventó ninguna medición.
5. **Cifras y su origen**: tiempos, metas, SEQ, errores y hallazgos salen de `a5_04_usabilidad.tex`
   y del contrato C1; 200 000 filas de XLSX, 24 h del enlace firmado, 8 s de retardo de la
   demostración, 500 000 puntos preagregados, 30 minutos de sesión y los rótulos entrecomillados
   salen de `frontend/i18n/locales/es.json`; los permisos por ruta, de
   `permisos.generated.ts` y `docs/security.md`; las tres composiciones de Inicio, de
   `docs/espacios-de-trabajo.md`; 130.2 %, +0.24 %, R² 0.02, 12 meses y `ratio_lcr`, de las
   capturas nuevas. El **arranque en frío de 2.4 s** medido el 22-ago-2026 se cita con su fecha en
   las preguntas frecuentes.
6. **Dirección del demo por macro**: se usa `\siHayDemoWeb{…}{…}` con `\urlDemoWeb` dentro de la
   rama con dirección, en prosa y **nunca dentro de un `\caption`**. Ningún `.tex` versionado lleva
   la URL literal.
7. **Numeración de apartados en el PDF propio**: `main_manual.tex` redefine `\thesubsection` a
   `\arabic{subsection}` porque el manual es su único contenido y colgaría del cero. Esa línea vive
   en el envoltorio, no en el contenido: dentro de `main_completo.tex` los apartados conservan el
   número de su parte, como los demás anexos del acumulado.
8. **Maquetación**: `\clearpage` antes de cada pantalla, según la disciplina de saltos que pidió el
   evaluador de A4, y cada captura colocada justo después del párrafo «Qué se ve» para que no se
   despegue de su texto. Anchos: 0.92 de la caja para las capturas de 1440×900, 0.88 para el
   recorte de la serie y 0.56 tanto para el acceso como para la página completa del tablero. Los
   dos anchos de 0.56 están medidos, no elegidos por gusto: a 0.92 el acceso ---cuyo lienzo es
   mayoritariamente blanco--- empujaba dos líneas del apartado a una página casi vacía, y a 0.60 la
   captura del tablero dejaba de caber junto a su texto y se iba a otra página.

**Capturas usadas**: `tema/institucional_claro_0_acceso.png`, `…_1_inicio.png`,
`…_2_exploracion.png`, `…_3_gobierno.png`, `…_4_administracion.png`, `…_6_exportacion.png`,
`…_7_asistente_resultado.png`, más `figuras/a5/tableros_analista.png` y
`figuras/a5/serie_observado_proyectado.png`. **Nueve figuras, ninguna regenerada ni retocada.**

**Capturas que faltan** (declaradas, no simuladas):

- **Los cuatro estados no felices no tienen captura propia.** El apartado 11 los describe en una
  tabla de tres columnas —cómo se reconoce y qué hacer— y remite a la matriz de la Actividad 4, que
  los declara pantalla por pantalla. Fabricar una captura de un estado de error habría exigido
  provocarlo en el portal desplegado; no se hizo y no se finge.
- **El asistente en su estado vacío** (`tema/institucional_claro_5_asistente.png`) existe y **no se
  usó**: el manual publica el turno resuelto, que es el que enseña la tarjeta de consulta, la cifra
  y la fuente. Con las dos, el apartado ocupaba tres páginas sin añadir nada.
- **Los cinco flujos de tarea** (`figuras/a4/flujo_*.png`) y las láminas de `figuras/a4/tema/` de
  combinación de tema **no se usaron a propósito**: son láminas de **diseño**, no capturas del
  portal —`a4_08` obliga a que su pie lleve la palabra diseño justo para que no se confundan—, y un
  manual de uso que ilustra el producto con una lámina de diseño enseña a esperar una pantalla que
  no existe.

**Guías desactualizadas**

- `docs/AGENTS.md`, sección **'Estado'**: sigue diciendo que A5 no ha empezado y que no hay
  `main_a5.tex`. Ya lo anotaron otros agentes; se confirma.
- `docs/AGENTS.md`, sección **'No tocar'**: declara `figuras/a4/{antes,despues}/*.png` como el
  juego de capturas del portal y no menciona `figuras/a4/tema/`, que es el juego que `a4_02`
  publica realmente como estado entregado y el que este manual reutiliza. Quien lea la guía
  concluiría que `despues/` es la captura vigente, y **no lo es**: dos de sus ocho imágenes
  documentan pantallas que ya no existen así. Merece una línea de la integración.
- `docs/AGENTS.md`, sección **'Mapa de la carpeta'**: `figuras/a5/` es una carpeta nueva de esta US
  con capturas tomadas contra Cloud Run, y ninguna guía la nombra todavía.


### Agente A — métricas

**Archivos escritos**

- `docs/entregables/contenido/a5_06_metricas.tex` — **nuevo**, 198 líneas, único archivo tocado.
  Ningún otro archivo del repositorio se modificó.

**Qué contiene, en el orden que pidió el encargo**

1. `\section{Descripción de métricas UX}` con `\label{sec:a5-metricas}` inmediatamente después
   del titular, tal como fija C4.
2. **11.1 Marco de selección**: ISO 9241-11 (2018) como definición de partida; las cuatro familias
   de Albert y Tullis (2013) —cap. 4 desempeño, cap. 5 problemas, cap. 6 auto-reportadas, cap. 8
   combinadas y comparativas— con la dimensión ISO que cubre cada una; clasificación del estudio
   con el cap. 3 (evaluación de navegación y arquitectura más descubrimiento de problemas,
   formativo con lectura sumativa); y **descarte por escrito del cap. 7** en `uxdestacado`, con dos
   causas: sin instrumentación de mirada ni fisiológica en sesiones ejecutadas en la computadora
   del participante (dos remotas), y porque esa familia precisaría el mecanismo de la fricción, no
   su existencia ni su consecuencia.
3. **11.2 Métrica por interfaz**: las siete interfaces de A4 más *tableros e indicadores* —que la
   Actividad 4 documentó como pantalla propia y la prueba midió con T4— más la fila de producto
   completo: **nueve filas**. Se compone en **dos `uxtablalarga`** (no flotantes, repiten
   encabezado): la primera declara funcionalidad principal, métrica e instrumento; la segunda,
   meta, resultado del 20-ago y estado. Se separaron a propósito: en una sola tabla de seis
   columnas las celdas caían a 2,3 cm y cada fila crecía a seis o siete líneas, con lo que la
   versión partida ocupa **menos** papel y se lee.
4. **11.3 De la métrica al hallazgo**: matriz severidad por frecuencia de H1 a H8 leída con el
   cap. 5, con H5, H6 y H8 declarados fuera de la matriz por no ser problemas, más la tabla que
   liga cada hallazgo con su prioridad y con la recomendación de `a5_04` que lo atiende.
5. **11.4 Lectura estadística del SUS**: tabla de estadísticos con media 89.0, desviación 7.42,
   error 3.32, t 2.776, margen 9.21 e IC 95 % [79.8, 98.2]; lectura contra la meta de 75 y el
   promedio de 68 (Sauro y Lewis, 2016; Albert y Tullis, 2013, cap. 6); rótulo de honestidad
   —muestra pequeña e intencional, margen más ancho que la distancia entre 75 y 68— y la
   sub-escala de aprendizabilidad de A1, A2 y A3 (75.0, 87.5 y 100.0) frente a la de usabilidad
   (84.4, 93.8 y 100.0).
6. **11.5** nota `uxnota` con TTFT y tasa de acierto en las tres primeras posiciones como métricas
   de operación declaradas y fuera del alcance de esta prueba.

**Decisiones que el siguiente agente debe conocer**

- **Cifras**: todas salen de C1 y de `a5_04`; no se recalculó ninguna. Se verificó consistencia
  interna (12 tiempos suman 714 s, media 59.5 s; 12 valores SEQ suman 69, media 5.75; los siete
  errores de C1 cuadran con la tabla por tarea de `a5_04`). Ninguna celda inventa una medición:
  inicio y gobierno del dato llevan la etiqueta contractual **«instrumentado, medición pendiente»**
  y son las dos únicas que la llevan.
- **Sin `\ref` a etiquetas ajenas.** El capítulo cita a su vecino como «el capítulo siguiente» y no
  con `\ref{sec:a5-usabilidad}`. Razón: esa etiqueta vive en el archivo de B y, si faltara al
  compilar la entrega, el PDF publicaría `??`. Si D prefiere referencias numéricas, el cambio es de
  cuatro líneas y solo después de confirmar que la etiqueta existe.
- **Sin citas a los tres papers de 2026.** C5 los asigna al capítulo de la prueba (5.2.e del plan) y
  no están en `docs/papers/README.md`, que solo lista el ancla 08. Se prefirió no citar lo que no
  se puede verificar. Las fuentes usadas son ISO 9241-11 (2018), Albert y Tullis (2013, caps. 3 a
  8) y Sauro y Lewis (2016).
- **Falta una referencia en el archivo de C**: `a5_05_cierre.tex` **no lista a Albert y Tullis
  (2013)** y este capítulo lo cita nueve veces. Es la única dependencia que dejo abierta.
  Entrada sugerida: *Albert, B., y Tullis, T. (2013). Measuring the User Experience: Collecting,
  Analyzing, and Presenting Usability Metrics (2.ª ed.). Morgan Kaufmann.*
- **Accesibilidad sin rutas de código.** La fila de producto completo cita «44 pares de contraste
  calculados y sus cuatro defectos corregidos», que es lo que publica la guía de estilo de A4; no
  se nombra ningún script ni ruta de archivo, por la regla de que el documento no brinca a la etapa
  de desarrollo.
- **Sin duplicar a B.** El capítulo no repite protocolo, participantes, evidencia por hallazgo ni
  el enunciado de R1 a R7: los nombra y remite. Tampoco reimprime la tabla de puntuaciones SUS por
  participante, que es de `a5_04`; aquí solo van los estadísticos derivados.

**Compilación**

- `latexmk -xelatex -interaction=nonstopmode -outdir=tmp/a main_a5.tex`, dos pasadas, **exit 0**,
  sin errores, sin referencias indefinidas y **sin un solo `Overfull \hbox`** en el capítulo. Salida
  aislada en `docs/entregables/tmp/a/`, que git ignora; no se dejó ningún auxiliar nuevo fuera de
  ahí y no se corrió `latexmk -c` para no borrar los de otros agentes.
- Un aviso honesto de extensión: el encargo pedía de tres a cinco páginas. El capítulo mide
  **entre 4,5 y 5 páginas de tinta**, pero en el borrador actual de `main_a5` **toca los folios 23
  a 28** porque arranca a un 15 % de la página 23 —la sección anterior termina ahí— y porque el
  `\needspace` del titular de 11.4 deja un hueco en la 26. Se recortó el capítulo cuatro veces para
  llegar aquí (se eliminó una tabla de familias de métricas, la de sub-escalas pasó a prosa y se
  quitaron las columnas de severidad y frecuencia de la tabla de recomendaciones, que ya estaban en
  la matriz). En `main_completo` la paginación cambia; **si D necesita bajar un folio más**, lo más
  barato sin perder contenido de rúbrica es fusionar 11.5 con el cierre de 11.4.

**Guías desactualizadas**

- `docs/AGENTS.md`, **'Estado'**: sigue diciendo que A5 no ha empezado y que no existen `semana_5/`
  ni `main_a5.tex`. Confirmado por tercera vez; además ya existe `contenido/a5_06_metricas.tex`,
  que ninguna guía nombra.
- `docs/AGENTS.md`, **'Convenciones'**: la regla «Sección nueva de A4 → `contenido/a4_NN_*.tex`» no
  tiene equivalente para A5. Hoy `main_a5.tex` carga `a5_00` a `a5_07` en un orden **editorial y no
  numérico** —`a5_06_metricas` va antes que `a5_04_usabilidad`—, y eso no está escrito en ninguna
  parte: quien añada un `a5_08` y lo ponga al final por comodidad romperá la secuencia del
  documento. Merece una línea de la integración.

### Agente D — envoltorio

**Archivos** (write-set respetado; ningún otro archivo del repositorio se tocó):

| Archivo | Qué |
|---|---|
| `docs/entregables/main_completo.tex` | **modificado** — preámbulo (`datos/demo` y puntos de corte de URL), portada, introducción general, mapa de cumplimiento, siete anclas `cmp:*`, un `\clearpage` de maquetación y la Parte V completa |
| `docs/entregables/contenido/a5_00_preliminares.tex` | **modificado** — el puente ahora abre la Parte V y no el documento entero; `\label{sec:a5-producto}` según C4 |

**Compilación final**: `latexmk -xelatex -interaction=nonstopmode -outdir=tmp/d main_completo.tex`
desde `docs/entregables/`. Desde limpio son **tres pasadas de `xelatex`**: la tercera la necesita el
mapa de cumplimiento, que referencia páginas posteriores a su propia posición. Resultado: **305
páginas, cero errores, cero referencias sin resolver, cero etiquetas duplicadas y cero `??` en el
PDF** ---comprobado sobre el texto extraído del PDF, no sobre el `.log`---. No se ejecutó
`latexmk -c`: todo lo generado quedó en `tmp/d/`, que git ignora.

**Dónde quedó cada cosa** (folio impreso; el índice físico del visor es el folio más uno, porque la
portada no lleva folio):

- Índice: folios 1 a 9.
- **Introducción general**: folio 10, con la Tabla 1 del método ---instrumento, muestra y fecha de
  las cinco actividades--- partida entre los folios 10 y 11 con encabezado repetido.
- **Mapa de cumplimiento**: **folio 12**, y la tabla de 16 filas ocupa los folios 12 y 13.
- Partes I a IV: folios 14 a 255. Parte V: folios 256 a 304.

**Las 16 filas del mapa y de dónde sale su página**. Trece resuelven la página con `\pageref` y se
actualizan solas; **tres se escribieron a mano**, que son exactamente las que ADR-005 deja sin
gancho porque su contenido vive dentro de `contenido/a1_cuerpo.tex`:

| Fila | Página escrita a mano | Verificada contra |
|---|---|---|
| 3 · Descripción del producto | **24** (sección 3, «Definición del producto digital») | `main_completo.toc`, entrada `{3}` |
| 4 · Personas | **33 a 53** (secciones 5 a 12, de Laura Méndez a Ximena Solís Barrera) | `.toc`, entradas `{5}` y `{12}` |
| 5 · Mapas de empatía | **35 a 55** (subsección dentro de cada una de esas ocho secciones) | `.toc`, entradas `{5.1}` y `{12.1}` |

La línea base que traía el encargo (20 · 29 a 49 · 29 a 51) **se movió cuatro folios**: la
introducción general y el mapa de cumplimiento añaden páginas al frente y el índice creció con las
entradas de la Parte V. Los números publicados son los medidos en la compilación final.

La fila 1 no lleva número: la portada usa `titlepage` y no imprime folio, así que su celda dice
**«Portada»**. Escribir «1» habría mandado al evaluador al índice, que es el primer folio impreso.

Las siete anclas nuevas `cmp:*` viven **solo en `main_completo.tex`**, inmediatamente antes del
`\input` correspondiente, y las seis coinciden con el folio que el `.toc` da al titular que abre
ese archivo: `cmp:intro` 10, `cmp:mapa` 12, `cmp:competitivo` 102, `cmp:arquitectura` 132,
`cmp:mapanav` 139, `cmp:prototipos` 164, `cmp:guia` 181. Ningún archivo de contenido congelado
recibió una etiqueta. Las demás filas usan las etiquetas ya existentes: `sec:escenarios` 65,
`sec:journey` 90, `sec:cardsorting` 118, `sec:a5-producto` 257, `sec:a5-metricas` 258,
`sec:a5-usabilidad` 263, `sec:a5-conclusiones` 275, `sec:a5-referencias` 281 y `sec:a5-manual` 285.

**Decisiones**

1. **El choque de «Introducción» en el índice se resolvió por título y por colocación, sin tocar
   `a1_cuerpo.tex`.** Las cinco partes abren con `\uxsection{Introducción}` ---es la convención del
   volumen, no un descuido de A1---, así que la general se titula **«Introducción general»** y entre
   ella y la de la Parte I se interpone **«Mapa de cumplimiento de la entrega»**, que también es
   entrada de índice. En el `.toc` las dos entradas ya no quedan pegadas. Por simetría con
   «Conclusiones generales» del cierre, el título también lee mejor.
2. **La rúbrica no se nombra dentro del entregable** y el mapa **no publica los pesos**. La columna
   se llama «Apartado solicitado» y la prosa dice «los dieciséis apartados solicitados para la
   entrega final». Es la misma regla que aplicó el agente B: el documento no narra su propia
   evaluación. El coste consciente es que el evaluador no ve el 15 % ni el 20 % al lado de las filas
   14 y 15; a cambio, ninguna página del PDF cita la plantilla de calificación.
3. **`a5_00` conserva su `\uxsection{Introducción}`** por esa misma convención de parte, pero su
   texto ya no introduce el documento entero: presenta la Parte V, enumera sus tres capítulos y sus
   dos anexos, y declara el alcance de la prueba. **Se retiró la frase «el reporte evita reproducir
   completos los documentos anteriores»**, que en el acumulado era falsa. La `uxnota` de alcance se
   conservó palabra por palabra. `\section{Descripción del producto}` se mantiene como eco ejecutivo
   y ahora abre diciendo que la definición completa es la de la Actividad 1 y no se repite, para que
   no compita con la fila 3 del mapa.
4. **Un `\clearpage` de maquetación, medido y no supuesto.** La tarjeta de apertura de la guía de
   estilos caía sola al pie del folio 180 y su cuerpo empezaba en el 181: titular sin su contenido,
   que es el defecto que el evaluador señaló en el punto 9.5 de A4. El salto vive **en el
   envoltorio**, antes del `\input`, y no en `contenido/a4_03_guia_estilos.tex`, que sigue
   congelado. Con él la tarjeta abre entera el folio 181 y el documento **no creció**: sigue en 305
   páginas. Coste declarado: el folio 180 queda al 40 % de llenado, la misma contrapartida que ya
   asumen los `\clearpage` de `a4_02` y `a4_08`.
5. **La dirección del demo obligó a añadir puntos de corte, y se probaron dos remedios.** La URL de
   Cloud Run son 43 caracteres sin espacios y `url.sty` solo la parte en los signos de puntuación:
   el corte disponible más cercano dejaba la línea **20.37 pt fuera de la caja de texto**, el único
   `Overfull \hbox` propio de esta sub-tarea. El primer intento, `{\sloppy …\par}` acotado al
   párrafo, quitó el desbordamiento pero **lo cambió por dos líneas flojas** (`Underfull` de badness
   10000 y 1742): la primera terminaba en `https://` y quedaba con huecos visibles. Se descartó. El
   remedio definitivo es de una sola causa: añadir las letras y los dígitos a `\UrlBreaks` en el
   preámbulo, con lo que la dirección se parte dentro del nombre de host y las dos líneas se
   justifican solas. Es **el único `\url` del volumen** ---no hay ni un `\url{` en `contenido/`---,
   así que el cambio no alcanza a ningún otro texto. Resultado medido: el documento pasó de 44 a
   **43** `Overfull \hbox`, con **cero `Underfull`** y **cero `Overfull \vbox`** en las 305 páginas.
   Los 43 restantes son ajenos y previos, de 0.1 a 18.6 pt, ninguno en los dos archivos de esta
   sub-tarea.
6. **La URL nunca se teclea.** El párrafo usa `\urlDemoWeb` y el preámbulo carga `\input{datos/demo}`
   justo después de `\usepackage{estilo/uxdoc}`. Verificado en el PDF: con `datos/despliegue.tex`
   presente imprime el enlace; ningún `.tex` versionado contiene la dirección literal.
7. **Sin marcas de versión** en portada ni en ningún punto del envoltorio, y `\uxencabezado` pasó a
   «Karisma Data · Entrega final del proyecto». `pdftitle` declara la entrega final y las cinco
   partes, con acentos y ñ verificados en los metadatos del PDF.
8. **Se corrigió un futuro heredado**: la portadilla de la Parte III decía «la arquitectura de
   información y el mapa de navegación que **sostendrán** el prototipo». En el volumen final el
   prototipo existe, así que dice «sostienen». Es la única palabra de contenido preexistente que
   cambió, y está dentro del write-set.

**Verificación sobre el PDF, no sobre el código** (las tres que pedía el encargo, más dos):

- **Cero `??` y cero referencias sin resolver.** Barrido del texto de las 305 páginas: ninguna
  ocurrencia. El `.log` tampoco reporta `undefined` ni `multiply defined`.
- **Cero titulares huérfanos al pie de página.** Se cruzaron las **313 entradas de sección y
  subsección del `.toc`** (de 341 en total, contando las de tercer nivel) contra el texto de su
  propia página: ninguna termina la página siendo la última línea sin cuerpo debajo.
- **Ninguna figura separada de su texto.** Se buscaron pies «Figura N:» en páginas sin objeto
  gráfico: seis candidatas (folios 73, 81, 89, 93, 94 y 95, todas de la Parte II) resultaron **falsos
  positivos**, porque esas figuras se incrustan como `XObject /Form` y no como `/Image`; las seis
  llevan su figura en la misma página.
- **Los ocho mapas de empatía siguen enteros.** Folios 35, 37, 40, 43, 46, 49, 52 y 55: en cada uno
  conviven el titular «Mapa de empatía de …» y los cuatro cuadrantes *Says*, *Thinks*, *Does* y
  *Feels*. La retroalimentación número 1 del profesor sigue cerrada por `\mapaempatia` + `\needspace`.
- **Cero `Overfull \vbox` y cero `Underfull`** en todo el documento.

**Observación para la integración, sin acción de esta sub-tarea**: dentro del acumulado, los
apartados del Anexo B numeran **65.4 a 65.15**, es decir, cuelgan del contador de la sección 65, que
es el Anexo A. Es la misma convención que ya produce `a4_07_anexo` (su «Anexo» cuelga de la sección
59) y el agente F la previó al no redefinir `\thesubsection` fuera de `main_manual.tex`, así que no
se alteró el contador: cambiarlo habría contradicho una decisión ya escrita por otro agente. Si la
pasada final la considera un defecto, se arregla con un `\stepcounter{section}` antes del `\input`
del manual, en el envoltorio y sin tocar el contenido.

**Guías desactualizadas**

- `docs/AGENTS.md`, **'Estado'**: cuando esta sub-tarea empezó seguía diciendo «A5 (23-ago) no ha
  empezado: no hay `semana_5/` ni `main_a5.tex`». La integración ya lo reescribió a media tarea y el
  texto vigente describe correctamente el cambio de vehículo, el orden editorial de la Parte V y el
  mapa de cumplimiento de dieciséis filas. **Queda un solo dato pendiente de ese párrafo**: dice que
  «el acumulado ronda las 300 páginas»; la cifra medida es **305**, y el mapa de cumplimiento no vive
  «en su Introducción» sino en una sección propia inmediatamente posterior, «Mapa de cumplimiento de
  la entrega», folio 12.
- `docs/AGENTS.md`, **'Convenciones'**: la línea «Sección nueva de A4 → `contenido/a4_NN_*.tex` …
  hay que añadirla **a los dos envoltorios**» no tiene equivalente para A5 y ahora hace falta uno
  distinto, porque los envoltorios de A5 **no cargan el mismo conjunto de archivos**: `main_a5.tex`
  incluye `a5_01`, `a5_02` y `a5_03`, y `main_completo.tex` los excluye a propósito. Quien añada un
  `a5_08` tiene que decidir en cuál de los dos entra, y hoy ninguna guía lo dice.
- `docs/AGENTS.md`, **'No tocar'**: no menciona que `main_completo.tex` es el **vehículo de entrega**
  de A5 ni que su mapa de cumplimiento fija páginas de las Partes I a IV escritas a mano. Cualquier
  cambio que desplace la paginación de la Parte I ---incluida una figura nueva o un salto de
  página--- obliga a volver a medir las filas 3, 4 y 5 de la Tabla 2. Merece una línea.

### Agente TESTS

**Punto de partida y veredicto.** La US es documental: de los diecinueve archivos del diff
(`git diff --name-only e257131` más `git status --short`), diecisiete son `.tex`, `.md` o `.pdf`.
Una prueba sobre maquetación o sobre prosa no puede fallar por un defecto, solo por una
reescritura legítima, así que **no se escribió ni una sola prueba de contenido**. Se escribieron
**dos comprobaciones ejecutables**, las dos sobre los archivos nuevos que sí traen mecanismo:
`datos/demo.tex`, `datos/despliegue.tex.example`, `scripts/escribir_url_demo.sh` y la línea nueva
de `.gitignore`.

**Archivos** (write-set: dos guiones nuevos y su cableado; ningún `.tex` ni ningún archivo de otro
agente se tocó):

| Archivo | Qué |
|---|---|
| `scripts/verificar_url_demo.sh` | **nuevo** — la dirección del demo no se publica. Cuatro comprobaciones |
| `scripts/verificar_contrato_demo.sh` | **nuevo** — `datos/demo.tex` responde en los dos escenarios. Documento mínimo |
| `Makefile` | **modificado** — `verificar_url_demo` entra en `check` y en `verificar`; `verificar_contrato_demo`, solo en `verificar`. Cada añadido con su razón escrita al lado |

**Qué defecto atrapa cada comprobación.** Ninguna se escribió sin responder antes esta pregunta.

| Comprobación | Defecto concreto que la pone roja |
|---|---|
| 0 · `git` sigue apartando `datos/despliegue.tex` y versionando su `.example` | Alguien reescribe esa línea de `.gitignore`, o una regla más ancha sobre `datos/` la precede: el archivo con la dirección pasa a ser un candidato más de `git add -A` y se publica sin que nadie teclee nada |
| 1 · el patrón detecta las dos formas de la dirección | Alguien retoca el patrón y deja de reconocer una URL de Cloud Run: la barrera queda verde para siempre, que es peor que no tenerla |
| 2 · el patrón no marca marcadores de posición ni nombres ficticios | Alguien lo ensancha a `run.app` a secas: enrojecen la plantilla `.example` y tres specs del frontend que ya usan `karisma-api-xyz.a.run.app`, y de ahí a borrar la barrera hay un paso |
| 3 · ningún archivo por publicar lleva la dirección literal | Alguien pega la dirección en un `.tex` o en un `.md` y publica el identificador del proyecto de GCP en un repositorio público |
| 4 · el documento compila SIN `datos/despliegue.tex` y toma la rama de respaldo | Alguien simplifica `datos/demo.tex` quitando la rama `\else` del `\IfFileExists`: o el repositorio deja de compilar en limpio, o —peor y más silencioso— `\urlDemoWeb` sigue siendo un `\url` sobre un valor vacío y la entrega publica un enlace vacío |
| 5 · el documento compila CON el archivo y toma la rama del enlace | Alguien quita el `\input{datos/despliegue.tex}` y deja la bandera: la entrega imprime un enlace vacío donde iba la dirección |

**El defecto 3 no es hipotético: ya ocurrió.** El commit `63a3b9f` —el propio SHA base de esta
US— corrigió a mano `docs/us-handoff/us-m01.md`, que publicaba las dos direcciones de Cloud Run
con el identificador dentro, antes de empujar y sin reescribir la historia. Esta comprobación es
lo que ahí faltó. Conviene saber que la historia **sí** conserva esas líneas, por decisión
declarada en ese mismo commit; lo que se vigila es lo que el repositorio publica hoy.

**Por qué no es una regla de `.gitleaks.toml`, que era la primera opción.** Se miró antes de
escribir nada, como pedía el encargo. `gitleaks dir` recorre el **árbol de trabajo**, no el
índice, y en el árbol hay dos artefactos locales que legítimamente contienen la dirección: el
propio `datos/despliegue.tex` y los `.txt` y `.log` que latexmk deja en `docs/entregables/tmp/`.
Una regla ahí obligaría a **dos entradas nuevas** en la lista de permitidos, que es justo el punto
donde el propio `.gitleaks.toml` advierte que un escaneo se vuelve teatro. La pregunta que importa
—qué publica el repositorio— se responde sobre `git ls-files` y no necesita ninguna excepción.
Un dato adicional cerró la decisión: la regla `gcp-project-number` que ya existe **no** habría
atrapado el caso de `63a3b9f`, porque exige la palabra proyecto a menos de veinte caracteres del
número y una URL no la lleva.

**La plantilla `despliegue.tex.example` no se excluye por ruta, y es deliberado.** Lleva una
dirección, pero con `XXXXXXXXXX` en lugar del identificador: no hay nada que tapar. Excluirla por
ruta dejaría ciega la comprobación el día que alguien pegue el valor real dentro de la plantilla,
que sí está versionada. En su lugar, la comprobación 2 fija que el patrón **no** la marca, de modo
que ese marcador de posición es ahora un caso de prueba y no una excepción.

**El listado incluye lo no versionado y sin ignorar** (`git ls-files --cached --others
--exclude-standard`). Con `git ls-files` a secas la barrera tenía un hueco del tamaño de esta
misma US: siete de sus archivos nuevos siguen sin añadirse al índice, y un `.tex` recién creado
con la dirección dentro no lo miraba nadie hasta después del commit. Se descubrió porque, al
ampliarlo, la comprobación se puso roja **sobre sí misma**: el ejemplo de URL que llevaba su
propio comentario de cabecera. Se sustituyó por `HASH` y `NUMERO`, y queda escrito ahí.

**El de compilación cuesta segundos, no minutos.** No compila `main_completo.tex` —305 páginas y
tres pasadas—: arma una copia de `datos/demo.tex` en un directorio temporal y compila ahí un
`article` con `hyperref`, que es lo único que el contrato necesita porque `\url` viene de
hyperref. Fabricar los dos escenarios no toca el `datos/despliegue.tex` de nadie. Las asertivas no
miran el PDF: el documento escribe al `.log` qué rama eligió y a qué quedó definida `\urlDemoWeb`,
con `\typeout` y `\meaning`. Dos detalles medidos contra xelatex y no supuestos: `\meaning` de un
`\newcommand` dice `\long macro:->` y no `macro:->`, y el `.log` corta las líneas a 79 caracteres,
así que los rótulos se comprueban por su principio.

**Prueba de que pueden fallar.** Cada una se ejerció contra un mutante, y las tres salidas son
reales:

- `.gitignore` con la línea de `despliegue.tex` comentada: `FALLA: git ya NO ignora
  docs/entregables/datos/despliegue.tex.` El archivo se restauró y se comprobó su SHA-256.
- La dirección real pegada en un `.tex` de `contenido/`: `FALLA: un archivo que el repositorio va
  a publicar lleva la dirección.` El mensaje **redacta** el identificador antes de imprimirlo, para
  no republicarlo en la terminal de quien corre el gate.
- `datos/demo.tex` sin su rama `\else`, sobre una raíz falsa y sin tocar el repositorio: `FALLA: el
  documento NO compila sin datos/despliegue.tex.` Con un segundo mutante que sí compila —el
  respaldo convertido en un `\url`—: `FALLA (sin direccion): el .log no dice
  'DEMOCHK:DEF=\long macro:->la'.`

**Qué se descartó y por qué.**

| Candidata | Veredicto |
|---|---|
| Que `a5_06_metricas.tex` mencione las siete interfaces | **No se escribe.** El único enganche es la etiqueta impresa, y no coincide con el código: `PROTOTIPOS` más `es.json` dicen «Acceso» y el capítulo dice «Acceso por perfil»; además el capítulo añade «Tableros e indicadores», que no es un prototipo del contrato. Serían dos excepciones escritas a mano sobre ocho filas, es decir, fijar la redacción del entregable dentro de un spec. Es justo la condición que ponía la sección 4 del plan, y no se cumple |
| Que el PDF tenga N páginas o una tabla N filas | **No se escribe.** Fija maquetación, no comportamiento |
| Cobertura de los `.tex` con vitest o pytest | **No se escribe.** Andamiaje |
| Que `docs/AGENTS.md` y `docs/CLAUDE.md` sigan siendo espejos byte a byte | **No se escribe en esta US**, y no por falta de defecto: hay uno vivo. Ver el hallazgo 1 |

**Hallazgo 1 — dos pares de espejos ya divergen, y no es cosa de esta US.** La raíz declara que
`<dir>/AGENTS.md` y `<dir>/CLAUDE.md` son espejos idénticos. Hoy `docs/`, `db/`, `ml/`, `tests/` y
la raíz lo cumplen; **`backend/` y `frontend/` no**. La deriva la introdujo `b7b4aca` (US-M01): los
dos `AGENTS.md` recibieron los párrafos de Cloud Run —el stage `runtime-con-datos` del Dockerfile,
`server/utils/identidadCloudRun.ts`— y sus `CLAUDE.md` no. Consecuencia práctica: Claude Code lee
hoy una guía de `backend/` y de `frontend/` a la que le faltan los hechos del despliegue, mientras
Codex lee la completa. Una comprobación de espejos es barata y atrapa un defecto real, pero
nacería **roja sobre archivos ajenos a esta US**, y la regla de `tests/AGENTS.md` es arreglar la
causa, no el test. Queda escrito para que la integración decida: primero sincronizar los dos
pares, después añadir la comprobación, en ese orden y probablemente en otra US.

**Hallazgo 2 — el PDF entregado sí lleva la dirección, y eso está fuera del alcance del guion.**
Las comprobaciones vigilan las **fuentes**: `grep -I` salta los binarios y los enlaces de un PDF
viajan en flujos comprimidos. Los dos PDF que hoy hay en `docs/semana_5/` no la contienen en texto
plano —comprobado—, pero el vehículo final se compila **con** `datos/despliegue.tex` presente,
justo para que el evaluador tenga el enlace, y ese PDF sí se versiona en `docs/semana_5/`. Es una
decisión de quien publica, no un descuido del contrato de macros, y merece tomarse a propósito
antes de commitear el PDF final.

**Dónde corren.**

- `make check` → `verificar_url_demo.sh`. Va en el gate diario y no solo en el barrido de entrega
  porque lo que vigila es una fuga, y una barrera contra fugas que solo corre antes de entregar
  llega tarde por definición. No cuesta nada: `git` y `grep`, ninguna herramienta nueva.
- `make verificar` → los dos. `verificar_contrato_demo.sh` vive solo aquí porque necesita
  **xelatex**; quien corre el barrido previo a la entrega es quien compila el PDF, así que ahí la
  tiene, y exigírsela al gate diario sería una dependencia nueva para todo el equipo a cambio de
  nada. Es el mismo criterio, con otra dependencia, que ya aparta a `verificar_historicos_tablero`.
- **Nada nuevo en `tests/`**: ningún archivo de esta US tiene comportamiento que pytest o vitest
  puedan ejercer, y una prueba de Python que solo lee `.tex` habría sumado cobertura sobre
  andamiaje. `tests/AGENTS.md` sigue describiendo con exactitud lo que hay; no se tocó.

**Corridas reales, sin tubería que enmascare el código de salida.**

```
make check      EXIT=0   lint, gitleaks, CA-7b, permisos y direccion del demo, los cinco en verde
make verificar  EXIT=0   los nueve guiones, incluidos los dos nuevos
make test       EXIT=0   828 passed, 17 skipped (pytest) - 55 archivos, 1077 tests (vitest)
```

**Guías desactualizadas** (no se tocan aquí; las corrige la integración):

- `docs/orchestration/commands.md`, líneas 43 a 46: describe `make check` como «lint + gitleaks +
  autocomprobación del escaneo + mapa de permisos» y `make verificar` como «pines, secretos,
  reproducibilidad, tokens, permisos, datos e históricos». Los dos objetivos hacen ahora una cosa
  más cada uno. El texto de ayuda del propio `Makefile` ya está al día.
- `tests/AGENTS.md`: su 'Estado' inventaría `tests/` y sigue siendo exacto, pero ninguna guía dice
  que **parte de la red de seguridad de este repositorio no vive en `tests/`** sino en
  `scripts/verificar_*.sh`, que ya son nueve. Quien lea solo `tests/AGENTS.md` concluirá que la
  única puerta es `make test`, y no lo es.

### Revisión final — fase 8, 22-ago-2026 por la noche

**Archivos**: `contenido/a5_04_usabilidad.tex` y `contenido/a5_05_cierre.tex` (citas), más el PDF
regenerado en `docs/semana_5/`.

- **Los autores de los tres trabajos de 2026 se verificaron contra arXiv y se completaron.** La
  reserva de C5 («si no puedes verificar autores, cita por título») quedó superada consultando las
  páginas de arXiv el 22-ago-2026: Tan, Lim, Durgad, Obegi y Li (2604.09581); Zhu, Friedman,
  Weatherwax y Eiben (2607.20773); Joarder, Chatti y Born (2603.24321). Las tres entradas se
  movieron a su lugar alfabético por apellido, las seis citas en texto pasaron a autor-año y la
  frase de la lista que explicaba la cita por título se retiró por obsoleta. La observación
  cosmética del agente C —título en mayúsculas frente a minúsculas— desaparece con el cambio.
- **Se declara la asistencia de edición, por encargo del equipo**: un párrafo al cierre de «Lo que
  el caso de estudio deja escrito» y la entrada APA «Anthropic. (2026). *Claude Code* (modelo
  Claude Fable 5) [Software de asistencia basado en modelos de lenguaje]», en su lugar alfabético.
  El párrafo delimita el papel de la herramienta: composición, verificación cruzada de cifras y
  maquetación; las decisiones y la interpretación son del equipo.
- **Recompilado y verificado** (`latexmk -xelatex -outdir=tmp/r main_completo.tex`): 305 páginas,
  exit 0, cero `??` sobre el texto extraído, mapa de cumplimiento intacto —las filas a mano siguen
  en 24, 33 a 53 y 35 a 55—, competidores en folios 104 a 110 uno por página, Anexo B numerando
  66.1 a 66.12 y la dirección del demo impresa tres veces. El PDF se copió a
  `docs/semana_5/Entregable Actividad 5_equipo_8.pdf`.
- **Barrido de muletillas de redacción asistida** sobre `a5_*` y el envoltorio: una sola
  coincidencia («permite profundizar en series»), que es lenguaje de producto legítimo y anterior
  a esta US. Sin hallazgos.
- **Decisiones que siguen abiertas para el equipo**: (1) la combinación de área y años de
  experiencia de A1 a A3 en la tabla de participantes, señalada por el agente B, sigue esperando
  una decisión explícita antes de publicar; (2) el PDF versionado lleva la dirección con el
  identificador del proyecto, decisión ya registrada que conviene reconfirmar al empujar;
  (3) `docs/orchestration/commands.md` líneas 43 a 46 y los espejos de `backend/` y `frontend/`
  quedan para otra US, como ya estaba anotado.
