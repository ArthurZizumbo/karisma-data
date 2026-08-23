# Planeación de Excelencia — Actividad 5 (Entrega final) · US-AVANCE-5

**Karisma Data · Portal Centralizado de Datos Financieros**
TC4032 Experiencia del usuario y diseño de interfaces · MNA · ITESM · Equipo 8

| | |
|---|---|
| **Actividad** | A5. Entrega final |
| **Disponible** | lun 17-ago-2026 00:00 |
| **Entrega** | dom 23-ago-2026 23:59 (meta interna: **dom 20:00**; el buffer usual de sábado ya no aplica porque esta planeación se escribe el sábado 22 por la tarde) |
| **Puntos** | 15 |
| **Modalidad** | Colaborativa; cuenta para todo el Project Group |
| **Formato** | PDF, nombre exacto `Entregable Actividad 5_equipo_8` |
| **Rúbrica leída** | sáb 22-ago-2026, protocolo §25.2 aplicado (sección 2 de este documento) |
| **Rol de este documento** | Contrato de ejecución de S5 (US-AVANCE-5), mismo papel que §26 del plan jugó para S4 |

---

## 0. Resumen ejecutivo

La rúbrica de A5 reparte 15 puntos en **16 criterios**. Trece de ellos (65 %) evalúan de nuevo
los artefactos de A1–A4 —personas, mapas, escenarios, journey maps, análisis competitivo, card
sorting, arquitectura, mapa de navegación, prototipos, guía de estilo—; solo el 35 % es trabajo
nuevo: **Descripción de métricas UX (15 %)** y **Prueba de usabilidad (20 %)**.

El equipo ya recorrió la mitad difícil del camino. El 20 de agosto se ejecutó la prueba con
**cinco participantes reales** (dos con nombre autorizado, tres anónimos), SUS combinado **89.0**
—por encima de la meta de 75 de §22 del plan— y el resultado está redactado en LaTeX
(`contenido/a5_00…a5_05`) y compilado como `Entregable Actividad 5_equipo_8_v3.pdf`. Con esa
prueba se cierra §22.1.b del plan: la única ventana de validación humana del proyecto **ocurrió**,
y la frase «usabilidad medida» se puede escribir con datos propios.

Lo que falta para la excelencia son cuatro movimientos, en orden de puntos en riesgo:

1. **Cambiar el vehículo de entrega**: el documento que se sube no es el compacto v3 sino el
   **acumulado `main_completo.tex` con una Parte V nueva**. El compacto resume A1–A4 en tablas de
   una fila por artefacto; con la banda «Completo = se incluyen los elementos solicitados», once
   criterios de 5 % quedarían expuestos a «Parcialmente». El acumulado reutiliza los mismos
   archivos que ya obtuvieron banda alta actividad por actividad (sección 4).
2. **Escribir el capítulo de métricas UX** que la rúbrica puntúa con 15 % y que hoy no existe
   como apartado propio: al menos una métrica por **cada una de las siete interfaces** de A4,
   ancladas en los capítulos 3–8 de Albert y Tullis (2013), con lo medido el 20-ago como
   resultado y no como promesa (sección 5.1).
3. **Aplicar la retroalimentación de A1–A4 al documento integrado** —competidores de una página,
   mapas de empatía sin partir, iconografía ya impresa, sin sección de versiones— con una
   excepción de maquetación por ADR, porque las fuentes de A1–A3 están congeladas (sección 6).
4. **Publicar el demo desplegado como evidencia**: la URL pública de Cloud Run entra al documento
   por variable (el repo es público y las direcciones no se versionan), con los cuatro perfiles de
   demostración para que quien evalúa recorra el producto real (sección 7).

Regla heredada que gobierna todo: cada cifra tiene origen (dato propio del 20-ago o cita APA),
nada se narra en tiempo futuro dentro del entregable, y la honestidad del prototipo («datos
sintéticos, no conectado a sistemas reales») no se rebaja para vender el resultado.

---

## 1. La rúbrica de A5, leída literalmente

Fuente: `docs/general/semana_5/Rubrica/Actividad 5. Entrega final.pdf` (15 pts, disponible desde
el 17-ago, intentos ilimitados, entrega por Canvas).

### 1.1 Reparto de puntos

| # | Apartado | Peso | Puntos de 15 | Dónde queda cubierto |
|---|----------|------|--------------|----------------------|
| 1 | Portada con los nombres de los integrantes | 2 % | 0.30 | Portada nueva del acumulado |
| 2 | Introducción («considerando todo el proyecto») | 3 % | 0.45 | Introducción general reescrita |
| 3 | Descripción del producto | 5 % | 0.75 | Parte I (A1) + eco ejecutivo en Parte V |
| 4 | Personas de todos los integrantes | 5 % | 0.75 | Parte I: 8 personas atribuidas por integrante |
| 5 | Mapas de empatía | 5 % | 0.75 | Parte I: 8 mapas, cuadrantes en inglés, sin corte de página |
| 6 | Escenarios de todos los integrantes | 5 % | 0.75 | Parte II: 6 escenarios, 2 por integrante |
| 7 | Journey Map | 5 % | 0.75 | Parte II: journey de equipo + 3 individuales |
| 8 | Análisis competitivo | 5 % | 0.75 | Parte III, con la corrección de una página por competidor |
| 9 | Card Sorting | 5 % | 0.75 | Parte III: 35 tarjetas, dendrograma, decisiones aplicadas |
| 10 | Arquitectura de información | 5 % | 0.75 | Parte III, versión revisada tras la prueba de árbol |
| 11 | Mapa de navegación | 5 % | 0.75 | Parte III, contrato de las rutas del prototipo |
| 12 | Prototipos de alta fidelidad | 5 % | 0.75 | Parte IV: 7 pantallas + tema institucional + flujos |
| 13 | Guía de estilo | 5 % | 0.75 | Parte IV: 11 secciones, iconos impresos (Tabla 28) |
| 14 | **Descripción de métricas UX (≥1 métrica/indicador por cada interfase diseñada)** | **15 %** | **2.25** | **Capítulo nuevo en Parte V (sección 5.1)** |
| 15 | **Prueba de usabilidad (≥1 prueba ligada a la funcionalidad principal de esa interfase)** | **20 %** | **3.00** | **Parte V: `a5_04_usabilidad` mejorado (sección 5.2)** |
| 16 | Conclusiones generales y referencias bibliográficas | 5 % | 0.75 | Parte V: cierre del proyecto + referencias consolidadas |

Las tres bandas son las mismas de A3 y A4 («Completo: se incluyen los elementos solicitados» /
«Parcialmente: … puede carecer de contenido alguno o varios» / «Incompleto»). La conclusión
operativa no cambia: **la rúbrica premia cobertura demostrada, no profundidad**. Cada uno de los
16 apartados debe ser localizable por su propio título y estar redactado en presente. Dos erratas
de captura en Canvas (una banda «Parcialmente» duplicada en Personas, «Parcilamente» en
Escenarios) no alteran nada.

### 1.2 Las dos frases nuevas y su interpretación

- **«Al menos una métrica/indicador por cada interfase diseñada»** (criterio 14). Las interfaces
  diseñadas son las **siete pantallas de A4**: Acceso, Inicio, Exploración y extracción (con 2.4
  Tableros), Gobierno del dato, Asistente, Administración y Exportación. Siete filas mínimo, cada
  una con métrica, instrumento, meta y resultado. La prueba del 20-ago midió directamente seis;
  Inicio y Gobierno se cubren con las métricas que sí se observaron en los recorridos del bloque
  B (tiempo hasta primera acción, identificación de fuente y certificación) y, donde no hay
  medición, la métrica se declara con su meta y su estado «instrumentada, medición pendiente» —
  la rúbrica pide *describir* la métrica a utilizar; medirla además es el extra.
- **«En consecuencia, al menos una prueba de usabilidad relacionada con la funcionalidad
  principal de esa interfase»** (criterio 15). Exactamente la anatomía de la Tabla 8 del v3: una
  tarea por interfaz, ligada a su función principal. Ya cumplido; hay que decirlo con esa
  correspondencia explícita (tarea ↔ interfaz ↔ funcionalidad principal ↔ métrica).

### 1.3 El recurso de apoyo y cómo superarlo

La rúbrica cita a Ramírez Mejía (2023), *Grocery shopping app. Part 5: Usability and Metrics*.
Su anatomía: catálogo de métricas (tiempo de tarea, tasa de éxito, errores, satisfacción,
retención, conversión, facilidad de aprendizaje, accesibilidad), caso con 5 tareas, procedimiento
de 9 pasos con think-aloud y SUS, y recomendación de **8–10 participantes**. Nuestro documento lo
supera en cuatro ejes y lo iguala en el resto: producto real operable en la nube (no maqueta),
dos bloques complementarios (protocolo estandarizado + recorridos contextuales), participantes
profesionales del dominio con consentimiento documentado, y análisis con intervalo de confianza.
El único punto donde el referente pide más —tamaño de muestra— se responde de frente en
Limitaciones con Albert y Tullis (2013, cap. 3: estudios de descubrimiento de problemas) y el
plan de retest R7, no se esconde (sección 5.2.d).

---

## 2. Absorción de la rúbrica — protocolo §25.2 ejecutado

1. **Paso 1 (T+0 h)** — volcado a tabla criterio → peso → banda: hecho, sección 1.1.
2. **Paso 2 (T+1 h)** — mapeo a la US y recálculo. `US-UX-08` es la historia afectada. Tres
   ajustes contra sus criterios provisionales:
   - «Protocolo con 3 tareas por perfil» → **se documenta el protocolo tal como se ejecutó**: 6
     tareas estandarizadas (C y V) + 3 recorridos por contexto (A1–A3). Cubre la intención
     (funcionalidad principal por interfaz) con mejor trazabilidad; no se rehace la prueba.
   - «SUS ≥ 75» → **cumplido: 89.0**, con la lectura estadística de la sección 5.1.d.
   - «Video demo de 3 minutos + presentación final» → **la rúbrica no los pide**. Salen del
     alcance comprometido de la semana y quedan como STRETCH opcional post-entrega (si el curso
     los solicita por otra vía, se planifican aparte). El tiempo liberado se invierte en el
     capítulo de métricas, que sí puntúa.
3. **Paso 3 (T+1 día)** — congelamiento STRETCH: nada que congelar; todos los STRETCH técnicos
   siguen congelados desde el 10-ago (§10.2.b).
4. **Paso 4** — registro. Fila lista para pegar en §25.4 de `context/planeacion_proyecto.md`
   (volcado pendiente, junto con marcar la fila «⏳ A5» como absorbida):

| Fecha | Rúbrica | Delta contra lo asumido | SP recalculados | STRETCH congelados | Dónde quedó registrado |
|---|---|---|---|---|---|
| 22-ago-2026 | A5 — Entrega final, 15 pts | La actividad re-evalúa los 13 artefactos de A1–A4 (5 % c/u, 65 %) y concentra lo nuevo en **métricas UX (15 %)** y **prueba de usabilidad (20 %)**. Exige ≥1 métrica por interfaz diseñada y ≥1 prueba ligada a la funcionalidad principal de cada una. No pide video ni presentación. El vehículo pasa del compacto v3 al acumulado con Parte V | US-UX-08 se mantiene en 3 SP: la prueba ya se ejecutó (20-ago); el delta restante es documental (~1.5 días-persona) | Ninguno (ya congelados el 10-ago) | `docs/semana_5/planeacion_excelencia.md`, secciones 1, 2 y 4 |

---

## 3. El estado real desde el que arrancamos (sáb 22-ago)

**Ya existe y se reutiliza:**

| Activo | Ruta | Estado |
|---|---|---|
| Prueba de usabilidad ejecutada y redactada | `docs/entregables/contenido/a5_04_usabilidad.tex` (187 líneas) | 5 participantes reales el 20-ago: C (Carlos René Flores M.) y V (Verónica Itzel Flores González) con nombre autorizado, A1–A3 anónimos. Bloque A: 11/12 éxitos (91.7 %), media 59.5 s, SEQ 5.8/7. Bloque B: 3/3 sin ayuda, facilidad 6.0/7. SUS: 87.5 · 82.5 · 82.5 · 92.5 · 100.0 → **89.0** |
| Hallazgos, recomendaciones y limitaciones | mismo archivo | H1–H8 con frecuencia y tipo; R1–R7 priorizadas; limitaciones honestas (bloques con unidades distintas, una respuesta SUS retrospectiva, A3 sin tableros) |
| Documento compacto A5 compilado | `docs/semana_5/Entregable Actividad 5_equipo_8_v3.pdf` (32 pp) + `main_a5.tex` + `a5_00…a5_05` | Fuente de la Parte V; sus resúmenes de A1–A4 (`a5_01`–`a5_03`) se retiran del acumulado por redundantes |
| Acumulado A1–A4 | `docs/entregables/main_completo.tex` (Partes I–IV) | Reutiliza los mismos `.tex` que las entregas calificadas; carga `a4_tokens` y `a4_iconos` en el preámbulo |
| Correcciones ya aplicadas en el repo | `estilo/uxdoc.sty`, `estilo/a4_iconos.tex` | Mapas de empatía en caja indivisible (`\mapaempatia` + `\needspace`, 29-jul); Tabla 28 imprime los 27 glifos con `uxtablalarga` (19-ago); la guía de estilos ya no publica seguimiento de versiones |
| Demo desplegado en GCP | `scripts/desplegar.sh`, `scripts/verificar_despliegue.sh` | Dos Cloud Run (`karisma-web`, `karisma-api`) + base administrada; las URL se consultan a `gcloud`, **no viven en el repo** (decisión de repo público) |
| Material de la semana | `docs/general/semana_5/Material_Apoyo/` | Albert y Tullis (2013), caps. 3–8, y Grocery Part 5 |

**No existe todavía (es el trabajo de esta planeación):**

- Capítulo «Métricas UX por interfaz» (criterio 14, 15 %).
- Cita y uso de Albert y Tullis (2013) — el v3 referencia a Brooke, Sauro y Lewis, ISO 9241-11,
  Baxter, Hartson y Pyla, Morville, Spencer, Walter y WCAG, pero **no al libro del curso de esta
  semana**, que es la fuente esperada por el evaluador.
- Portada e introducción de entrega final en el acumulado (hoy dice «Documento del proyecto,
  actualizado al 16 de agosto» y solo declara las partes I–IV).
- Corrección «un competidor por página» en `a3_01_analisis_competitivo.tex` (los siete
  `\subsubsection` fluyen sin `\clearpage`).
- URL del demo dentro del documento (mecanismo por variable, sección 7).
- Mapa de cumplimiento criterio → sección → página (el seguro contra la longitud, sección 4.2).

---

## 4. Decisión de método: qué PDF se entrega

### 4.1 El acumulado con Parte V, y por qué

| | Compacto v3 mejorado | **Acumulado + Parte V (elegido)** |
|---|---|---|
| Criterios 3–13 (11 × 5 % = 55 %) | Resúmenes: personas en tabla de una fila (sin foto, antecedentes ni frase), mapas comprimidos a una línea por cuadrante y rotulados en español, competitivo sin fichas por competidor ni tablas con fechas | Los artefactos completos que ya obtuvieron banda «Completo» en A1–A4, con las convenciones que la rúbrica de cada actividad exigió (cuadrantes en inglés, fechas de obtención, atribución por integrante) |
| Criterios 14–15 (35 %) | Prueba completa; métricas sin apartado propio | Prueba completa + capítulo de métricas dedicado |
| Riesgo dominante | «Parcialmente» en varios de los once criterios re-evaluados (cada banda intermedia cuesta ~0.2–0.4 pts y el techo baja de 15) | Longitud (~150 pp) que fatigue al evaluador |
| Mitigación | — | Introducción con **mapa de cumplimiento** (4.2), portadillas de parte con resumen (ya existen), índice a dos niveles |

La instrucción de la actividad empuja en la misma dirección: «conjuntar **todos** los
conocimientos y evidencias del curso… considerando **todas** las etapas», y el aviso del profesor
pide revisar la retroalimentación de A1–A4 «para hacer las mejoras necesarias **previo a la
integración de su documento final**». La integración es el entregable; el compacto fue el
borrador correcto para producir la Parte V, no el vehículo final.

**Contingencia** (si el domingo por la tarde el acumulado no compila estable): se entrega el
compacto v4 con el capítulo de métricas insertado y las referencias completadas. Para que ese plan
B cueste cero, **el capítulo de métricas se escribe como archivo independiente**
(`contenido/a5_06_metricas.tex`) que ambos envoltorios pueden `\input`.

### 4.2 Cambios en `main_completo.tex`

1. **Portada**: `\uxportada{Actividad 5. Entrega final}{Proceso de diseño UX de Karisma Data\\y prueba de usabilidad}{23 de agosto de 2026}` (los nombres del equipo ya los imprime la plantilla). `pdftitle` acorde. Sin marcas de versión: el profesor ya señaló que el seguimiento de versiones sobra en el entregable.
2. **«Sobre este documento» → «Introducción»**: se reescribe considerando todo el proyecto
   (criterio 2): qué problema se atacó, el método semana a semana (instrumentos, n y fechas: 8
   personas prototipo → supuestos declarados en A2 → card sorting con 8 evaluadores → prueba real
   con 5 participantes el 20-ago), los resultados clave (SUS 89.0, 11/12 éxitos), la dirección
   pública del demo con los cuatro perfiles de demostración, y el **mapa de cumplimiento**: tabla
   de 16 filas criterio de la rúbrica → sección y página donde vive. Es la primera página útil
   que verá quien califica un documento largo.
3. **Parte V nueva** («Actividad 5. Métricas UX y prueba de usabilidad», portadilla con resumen
   como las otras cuatro):

   ```
   \uxparte{V}{Actividad 5. Métricas UX y prueba de usabilidad}{...}
   \input{contenido/a5_00_preliminares}   % intro de la parte + nota de alcance + descripción ejecutiva
   \input{contenido/a5_06_metricas}       % NUEVO — criterio 14 (15 %)
   \input{contenido/a5_04_usabilidad}     % criterio 15 (20 %), con las mejoras de 5.2
   \input{contenido/a5_05_cierre}         % conclusiones del PROYECTO + referencias consolidadas + anexo
   ```

   `a5_01_investigacion`, `a5_02_arquitectura` y `a5_03_interfaz` **no entran al acumulado**
   (duplicarían las Partes I–III con menos detalle). Se conservan en el repo para `main_a5.tex`,
   que queda como documento de trabajo no entregado. En `a5_00` se retira la frase «el reporte
   evita reproducir completos los documentos anteriores» (ya no es cierta en el acumulado) y se
   ajusta la redacción de puente.
4. **Numeración**: `a5_06` en lugar de renumerar los existentes, colocado editorialmente antes de
   `a5_04` — mismo precedente que `a4_08` entre `a4_05` y `a4_06`.
5. **Cierre (`a5_05`)**: las conclusiones dejan de cerrar solo la prueba y cierran el proyecto
   como caso de estudio (criterio 16): el arco problema → personas → journey → arquitectura →
   prototipo → medición, qué predicciones de las semanas 1–4 confirmó o refutó la prueba (la
   fricción quedó exactamente donde el journey de A2 la señaló: decidir dónde buscar —H2— y
   confiar en la proyección —H1—), y la siguiente iteración (R1–R7). Referencias: unificar las
   del v3 + **Albert y Tullis (2013)** + los papers ancla ya citados en las partes + los tres
   nuevos de la sección 8.

---

## 5. Los dos criterios nuevos, en detalle

### 5.1 Capítulo «Métricas UX por interfaz» (`a5_06_metricas.tex`, 15 %)

Estructura propuesta (3–5 páginas):

**a) Marco de selección.** Un párrafo: usabilidad como efectividad + eficiencia + satisfacción
(ISO 9241-11), tipos de métricas según Albert y Tullis (2013): desempeño (cap. 4: éxito de tarea,
tiempo, errores, eficiencia), basadas en problemas (cap. 5: frecuencia × severidad),
auto-reportadas (cap. 6: SEQ, SUS) y combinadas/comparativas (cap. 8: lectura contra referencia).
El estudio se clasifica con el cap. 3 (§3.3): evaluación de navegación/arquitectura +
descubrimiento de problemas, formativo con lectura sumativa. Las conductuales/fisiológicas
(cap. 7) se descartan por escrito (sin instrumentación de mirada ni expresión; no aportan al
objetivo del estudio) — descartar con causa también es cobertura.

**b) La tabla que responde la rúbrica** (≥1 métrica por interfaz diseñada; las siete de A4):

| Interfaz (A4) | Funcionalidad principal | Métrica(s) | Instrumento | Meta | Resultado 20-ago |
|---|---|---|---|---|---|
| Acceso por perfil | Entrar al espacio de trabajo correcto | Éxito de tarea; tiempo; selecciones equivocadas | T1 cronometrada | 100 %; ≤45 s; 0 | 2/2 éxito; 24 s y 29 s; 0 |
| Inicio | Retomar el trabajo y lanzar la búsqueda | Tiempo hasta primera acción de búsqueda; fricción de arranque (H2) | Observación bloque A/B | Informativa | Medido cualitativamente: 3/5 dudaron entre buscador global y contextual (H2) |
| Exploración y extracción | Encontrar un campo y distinguir fuente/certificación | Éxito; tiempo; errores; metadatos correctos | T2 | 100 %; ≤90 s; ≤1; 3/3 | 2/2; 51 s y 62 s; 1 y 1; correctos |
| Tableros e indicadores (2.4) | Interpretar último corte, tendencia y proyección | Interpretación correcta; SEQ; distinción dato/proyección (H1) | T4 + SEQ | correcta; SEQ ≥5 | 1 éxito + 1 parcial; SEQ 4.5 — **la métrica que dispara R1** |
| Gobierno del dato | Confiar en la cifra: fuente, responsable, vigencia | Identificación de fuente y certificación; comprensión de procedencia | T2 y T5 (metadatos, fuente citada) + recorridos A1–A3 (H6) | 3/3 metadatos; fuente identificada | Cumplida en T2/T5; H6 la marca fortaleza. Linaje profundo: métrica declarada, medición pendiente (R7) |
| Asistente conversacional | Responder con consulta y fuente visibles | Éxito; tiempo; fuente identificada; ayudas | T5 | 100 %; ≤90 s; sí; 0 | 2/2; 49 s y 57 s; identificada; 0 — valida el patrón de transparencia de tool calls |
| Administración | Cambiar rol / retirar acceso sin acciones accidentales | Éxito; tiempo; acciones accidentales | T6 | 100 %; ≤90 s; 0 | 2/2; 58 s y 71 s; 1 error de V |
| Exportación | Solicitar archivo y comprender estado y caducidad | Éxito; tiempo; comprensión estado/caducidad | T3 | 100 %; ≤120 s; sí | 2/2; 64 s y 79 s; comprendidos |
| **Producto completo** | — | **SUS**; facilidad general (1–7); tasa de éxito global; **accesibilidad de diseño** (contraste verificado por script, matriz de la guía) | SUS post-sesión; valoración bloque B; consolidado; `verificar_tokens` | ≥75; ≥5; ≥90 %; AA | **89.0**; 6.0/7; 91.7 %; matriz AA/AAA publicada en la guía |

(Nota de armado: Tableros vive dentro de Exploración en la arquitectura; la tabla lo desglosa
porque la rúbrica cuenta interfaces diseñadas y A4 lo documentó como pantalla con contenido
propio. Ninguna fila queda sin métrica; ninguna celda inventa una medición que no ocurrió.)

**c) De la métrica al hallazgo.** Medio párrafo + tabla corta: cómo H1–H8 salen de las métricas
(cap. 5: frecuencia × impacto → prioridad), con la matriz severidad × frecuencia de los ocho
hallazgos y el enlace H → R ya escrito en el v3.

**d) Lectura estadística del SUS — el extra que nadie más va a llevar.** Con los cinco valores
(87.5, 82.5, 82.5, 92.5, 100.0): media 89.0, desviación estándar 7.4; **intervalo de confianza al
95 % (t, n=5): [79.8, 98.2]** — incluso el límite inferior supera la meta de 75 y el promedio de
referencia de 68 (Sauro y Lewis, 2016; Albert y Tullis, 2013, cap. 6). Verificar la aritmética al
redactar y rotular con honestidad: muestra pequeña e intencional, el intervalo acota la
incertidumbre, no la elimina — la generalización sigue limitada como ya declara 11.10. Opcional
si el tiempo alcanza: sub-escala de aprendizabilidad (ítems 4 y 10) para A1–A3, únicos con
respuestas por reactivo conservadas (75.0, 87.5, 100.0), citando Lewis y Sauro vía el cap. 6.

**e) Métricas de operación declaradas (§22.3)**: TTFT del streaming y Hit Rate@3 del catálogo se
mencionan en una nota como métricas de producto instrumentadas vía OpenTelemetry fuera del
alcance de esta prueba con usuarios — separa métricas UX de telemetría y muestra que la frontera
es una decisión, no un olvido.

### 5.2 Prueba de usabilidad (`a5_04_usabilidad.tex`, 20 %) — mejoras sobre lo ya escrito

El contenido ejecutado es sólido; los ajustes son de blindaje contra la banda:

- **a) Tabla de correspondencia con los 10 pasos de la instrucción.** La actividad enumera 10
  pasos (objetivos → informe). Una tabla de 10 filas «paso → dónde está en este documento
  (11.1…11.10)» convierte la evaluación del criterio en un ejercicio de palomeo. Costo: 15
  minutos; protege 3 puntos.
- **b) Correspondencia explícita tarea ↔ interfaz ↔ funcionalidad principal** en la introducción
  de 11.3 (la frase «en consecuencia…» de la rúbrica, respondida literalmente).
- **c) Materiales**: declarar que el material de prueba fue el **producto real desplegado**
  (paso 5 de la instrucción admite «producto o sistema real» — nuestra lectura fuerte), con la
  URL por variable y la versión del prototipo fijada; anotar qué sesiones fueron
  presencial/remotas (ya está) y el entorno de ejecución.
- **d) Limitaciones**: añadir la defensa de n=5 con causa: rúbrica y US exigen ≥5; el objetivo es
  descubrimiento de problemas (Albert y Tullis, cap. 3; el referente Grocery sugiere 8–10 para
  significancia — se reconoce y se responde con el intervalo de confianza de 5.1.d y el retest
  R7 con muestra ampliada hacia perfiles principiantes).
- **e) Cadena sintético → real**: un párrafo en método que hile la pre-validación con evaluadores
  prototipo (A3–A4, PerceptUI) con esta prueba humana, citando el paper ancla 08 y Avenir-UX
  (sección 8): la literatura de 2026 usa SUS/SEQ simulados como **complemento previo**, y este
  proyecto ejecutó exactamente esa secuencia terminando en personas reales. Es la posición
  metodológica de §22.1.b convertida en argumento con fuentes.
- **f) Privacidad, sin retrocesos**: nombres solo con autorización expresa (C y V), códigos para
  A1–A3, consentimientos y notas identificables fuera del entregable (ya declarado en 14.3). Al
  integrar al repo público, verificar que ningún dato de contacto ni área identificable de más
  viaje en los `.tex`.

---

## 6. Retroalimentación del profesor A1–A4 → acción en el documento integrado

| # | Retroalimentación recibida | Estado en el repo hoy | Acción para A5 |
|---|---|---|---|
| 1 | A1/A2: mapas de empatía divididos en dos páginas | Corregido el 29-jul (`\mapaempatia` compone en caja y reserva altura con `\needspace`) | **Verificar en el PDF compilado** que los 8 mapas del acumulado quedan enteros; es checklist, no trabajo |
| 2 | A3: «hubiera sido muy bueno que cada competidor quedara todo dentro de una página» | **Pendiente**: los siete `\subsubsection` de `a3_01` fluyen sin salto | `\clearpage` antes de cada competidor + ajuste fino si alguno rebasa la página (recortar viñetas, no contenido evaluado). Requiere la excepción del ADR (abajo) |
| 3 | A3: tablas comparativas con fechas de obtención (elogiado) | Presente | Verificar intacto tras los saltos |
| 4 | A4: punto 9.5 Iconografía sin contenido; Tabla 28 sin los íconos | Corregido el 19-ago: la Tabla 28 imprime los 27 glifos con nombre y rótulo accesible (`uxtablalarga`, no flotante) | Verificar que el acumulado los imprime (carga `estilo/a4_iconos` en el preámbulo: sí) |
| 5 | A4: seguimiento de versiones innecesario en este entregable | Corregido: la guía «deja de versionarse» | Barrido final: ninguna sección de historial de versiones, ningún «v3» en portada ni nombre de archivo |
| 6 | General: cuidado con los saltos de página | Disciplina establecida en A4 (`\clearpage` ante bloques visuales) | **Pase completo de maquetación** del acumulado: ningún titular huérfano, ninguna figura separada de su texto, cazar páginas casi vacías (en el v3: pp. 7, 20–21 y 29) |

**La excepción que esto exige — ADR-003.** `docs/AGENTS.md` congela las fuentes de A1–A3
(«ese PDF es el registro de lo evaluado»). La corrección №2 toca `a3_01`. Se escribe
`docs/decisions/ADR-003-correcciones-de-maquetacion-para-la-entrega-final.md` con la regla: *los
PDF de `semana_1..3` permanecen intactos como registro de lo evaluado; sus fuentes `.tex` admiten
únicamente correcciones de maquetación derivadas de retroalimentación del evaluador, aplicadas
para la integración de A5; el contenido evaluado no se reescribe*. Tras el ADR, actualizar la
línea correspondiente de `docs/AGENTS.md`/`docs/CLAUDE.md` (espejos) — y de paso su sección
**Estado**, que aún dice que A5 no ha empezado.

---

## 7. El demo desplegado como evidencia verificable

- **Dónde aparece**: (1) en la Introducción, junto al mapa de cumplimiento; (2) en 11.4
  Materiales («producto real, versión fijada, dirección pública»); (3) en el cierre, como
  invitación a recorrer los cuatro perfiles de demostración. Siempre con la etiqueta de
  honestidad ya acuñada: *prototipo de alta fidelidad con datos sintéticos, no conectado a
  sistemas reales de ninguna institución*.
- **Mecanismo respetuoso del repo público** (las URL de Cloud Run no se versionan — decisión de
  E0): crear `docs/entregables/datos/despliegue.tex` **ignorado por git** que define
  `\urlDemoWeb`; se escribe localmente con la salida de
  `gcloud run services describe karisma-web --format="value(status.url)"` (o desde
  `verificar_despliegue.sh`). En los `.tex` versionados: `\IfFileExists` con respaldo «la
  dirección pública se entrega con el documento» para que el repo compile sin el archivo.
- **Verificación previa a la entrega**: correr `scripts/verificar_despliegue.sh` el domingo antes
  de subir; comprobar el arranque en frío con una visita real (el evaluador llegará a instancia
  fría; si tarda >10 s, valorar `min-instances=1` solo durante la semana de calificación y
  revertir después — respeta el presupuesto de §23 y se anota la decisión).
- **Acceso de demostración**: confirmar que el selector de perfiles de demostración está activo
  en la instancia pública (condición registrada del despliegue) y que las capturas del documento
  siguen correspondiendo a lo que la URL muestra.

---

## 8. Investigación permitida: tres papers de 2026 (agosto) y su papel

Autorizados hasta 3; propuestos estos, cada uno con un uso concreto (verificar autores y datos
bibliográficos en arXiv al citar; si alguno no resiste la lectura rápida, se cita solo el que
aporte — ninguna cita decorativa):

1. **Avenir-UX: Automated UX Evaluation via Simulated Human Web Interaction with GUI Grounding**
   (arXiv:2604.09581, 2026). Evalúa UX con SUS, SEQ y think-aloud **simulados**. Se cita en el
   método (5.2.e) para encuadrar nuestra cadena pre-validación sintética → prueba humana como la
   secuencia que la literatura actual recomienda, reforzando al paper ancla 08 (PerceptUI).
2. **HARP: The Human-AI Research Platform** (arXiv:2607.20773, 2026). Evaluación de interacción
   humano-agente conversacional con participantes reales en escenarios controlados. Se cita al
   justificar el diseño de dos bloques y las tareas del asistente (T5).
3. **Usability Evaluation and Improvement of a Tool for Self-Service Learning Analytics**
   (arXiv:2603.24321, 2026). Evaluación SUS de una herramienta de analítica autoservicio y su
   ciclo de mejora — el precedente de dominio más cercano para interpretar resultados y sostener
   el ciclo medir → corregir → retest (R7).

Se citan en `a5_06_metricas` / `a5_04_usabilidad` y entran a las referencias consolidadas junto
con la lectura de la semana en el formato dado:

> Albert, B., y Tullis, T. (2013). *Measuring the User Experience: Collecting, Analyzing, and
> Presenting Usability Metrics* (2.ª ed.). Morgan Kaufmann. [capítulos 3 a 8]

---

## 9. Cronograma sáb 22-ago → dom 23-ago

| Cuándo | Qué | Sale |
|---|---|---|
| Sáb 15:30–16:30 | Comunicar al equipo la decisión de vehículo (sección 4) y este plan; rama `us-avance-5`; ADR-003 + espejos de `docs/` | Acuerdo + rama lista |
| Sáb 16:30–19:00 | `main_completo.tex`: portada A5, Introducción reescrita con mapa de cumplimiento, portadilla Parte V, `\input` de la parte; ajuste de puente en `a5_00`; primera compilación completa (`latexmk -xelatex main_completo.tex`, dos pasadas, desde `docs/entregables/`) | Acumulado compila con Parte V |
| Sáb 19:00–22:00 | **`a5_06_metricas.tex` completo** (tabla de 5.1.b, marco, matriz severidad × frecuencia, IC del SUS verificado a mano) | Criterio 14 cubierto |
| Sáb 22:00–23:00 | `a3_01`: un competidor por página; verificación visual de los 8 mapas de empatía en el acumulado | Feedback №1–3 cerrado |
| Dom 09:00–10:30 | Mejoras de `a5_04` (tabla 10 pasos, correspondencias, defensa n=5, cadena sintético→real); referencias consolidadas en `a5_05` (Albert y Tullis + 3 papers verificados) | Criterios 15 y 16 en banda alta |
| Dom 10:30–11:30 | URL del demo: `datos/despliegue.tex` + `\IfFileExists`; `verificar_despliegue.sh` en verde; visita de arranque en frío | Evidencia viva enlazada |
| Dom 11:30–13:00 | **Pase de maquetación completo** del PDF (titulares, figuras, páginas vacías) y **checklist de la sección 10, criterio por criterio** | Documento en banda «Completo» × 16 |
| Dom 13:00–16:00 | Revisión cruzada de los tres integrantes (cada quien un tercio del PDF + su parte individual); incorporación de observaciones; compilación final | PDF final |
| Dom 16:00–17:00 | Copia a `docs/semana_5/Entregable Actividad 5_equipo_8.pdf` (sin sufijo de versión); `make check` antes del PR (sin leerlo a través de una tubería); dejar rama lista — **push/PR solo con visto bueno** | Entrega lista |
| Dom ≤20:00 (tope 23:59) | Subida a Canvas por quien entrega; confirmación en el grupo; volcar la fila de §25.4 al plan y registrar el cierre en memoria | Entregado |

Riesgo de agenda: si `a5_06` no está cerrado el sábado a las 23:00, el domingo se recorta primero
la revisión cruzada a una sola pasada (nunca el capítulo de métricas ni el checklist de rúbrica).

---

## 10. Checklist de excelencia — verificación final (dom 11:30)

| ✔ | Criterio (peso) | Banda «Completo» exige | Extra de excelencia |
|---|---|---|---|
| ☐ | Portada (2 %) | Nombres de los 3 integrantes, curso, equipo 8 | Identidad Karisma Data consistente A1→A5; sin marca de versión |
| ☐ | Introducción (3 %) | Considerando todo el proyecto | Párrafo de método con n y fechas + **mapa de cumplimiento** + URL del demo |
| ☐ | Descripción del producto (5 %) | Tipo, características, beneficios | Parte I completa + eco ejecutivo con tabla capacidad→valor en Parte V |
| ☐ | Personas (5 %) | De todos los integrantes | 8 completas con foto, atribuidas, conectadas a perfiles RBAC |
| ☐ | Mapas de empatía (5 %) | 4 cuadrantes | 8 mapas, cuadrantes en inglés, **cada uno entero en su página** |
| ☐ | Escenarios (5 %) | De todos los integrantes | 6, dos por integrante, plantilla uniforme |
| ☐ | Journey Map (5 %) | Presente | De equipo + 3 individuales, emociones y momento de la verdad; **cerrado el círculo: la prueba confirmó H1/H2 donde el journey predijo fricción** |
| ☐ | Análisis competitivo (5 %) | Presente | 6 competidores, **uno por página**, tablas con fecha de obtención |
| ☐ | Card sorting (5 %) | Presente | 35 tarjetas, dendrograma reproducible, decisiones aplicadas |
| ☐ | Arquitectura (5 %) | Presente | Versión revisada tras prueba de árbol, facetas transversales |
| ☐ | Mapa de navegación (5 %) | Presente | Contrato ruta↔rama verificado en el prototipo |
| ☐ | Prototipos (5 %) | Presente | 7 pantallas del producto real + estados no felices + demo público |
| ☐ | Guía de estilo (5 %) | Presente | 11 secciones; Tabla 28 con los 27 glifos impresos; matriz de contraste verificada |
| ☐ | **Métricas UX (15 %)** | ≥1 métrica por interfaz diseñada | Tabla 7 interfaces + producto; medidas reales del 20-ago; IC 95 % del SUS; matriz severidad×frecuencia; descarte razonado del cap. 7 |
| ☐ | **Prueba de usabilidad (20 %)** | ≥1 prueba ligada a la funcionalidad principal | 5 usuarios reales, dos bloques, tabla de 10 pasos de la instrucción, defensa n=5 con fuentes, producto real como material |
| ☐ | Conclusiones y referencias (5 %) | Presentes | Cierre del proyecto como caso de estudio; referencias APA consolidadas con la lectura del curso y 3 papers 2026 |

Verificaciones transversales: cifras con origen en las 16 secciones · sin tiempo futuro · sin
emojis · español neutro · sin datos personales no autorizados · nombre de archivo exacto ·
paginación e índice correctos tras la última compilación.

---

## 11. Riesgos y contingencias

| Riesgo | Señal | Contingencia |
|---|---|---|
| El acumulado no compila estable con la Parte V | Errores de macros o flotantes el sábado por la noche | Plan B de 4.1: compacto v4 = `main_a5.tex` + `a5_06` + referencias; la decisión se toma el domingo a las 13:00, no a las 22:00 |
| Longitud fatiga al evaluador | — | Mapa de cumplimiento en la Introducción; portadillas con resumen; índice a dos niveles |
| Demo caído o arranque en frío lento el día de la calificación | `verificar_despliegue.sh` en rojo o primera visita >10 s | El documento no depende de la URL (capturas y alcance completos); valorar `min-instances=1` una semana con nota de costo |
| Trampa del verificador de tokens | Un hexadecimal con `#` en cualquier `a4_*.tex` editado pone en rojo el paso 4 de `verificar_tokens_a4.sh` | Colores como `\texttt{0B1B2B}`; regla viva si el barrido №5 toca archivos de A4 |
| Privacidad de participantes | Nombres o áreas de más en los `.tex` públicos | Solo C y V con nombre (autorización expresa); consentimientos fuera del repo; revisión específica en el paso del dom 11:30 |
| Divergencia con el trabajo del equipo sobre el v3 | Compañeros editando el compacto en paralelo | La decisión de vehículo se comunica **antes** de tocar nada (sáb 15:30); `a5_04`/`a5_05` son la fuente única en ambos vehículos |
| Push/PR sin acuerdo | — | La rama queda lista y **no se empuja sin visto bueno del equipo** |

---

## 12. Definition of Done de US-AVANCE-5

1. PDF `Entregable Actividad 5_equipo_8.pdf` compilado del acumulado (Partes I–V), copiado a
   `docs/semana_5/` y subido a Canvas antes del domingo 23:59 (meta 20:00).
2. Los 16 criterios verificados en banda «Completo» con el checklist de la sección 10.
3. Capítulo de métricas con ≥1 métrica por cada una de las 7 interfaces de A4, citando a Albert
   y Tullis (2013, caps. 3–8).
4. Las 6 retroalimentaciones de A1–A4 cerradas o verificadas en el documento integrado, con
   ADR-003 escrito y los espejos de `docs/` sincronizados.
5. URL del demo incluida por variable, despliegue verificado en verde el día de la entrega.
6. Fila de absorción volcada a §25.4 del plan y estado de `docs/AGENTS.md` actualizado (A5 en
   curso → entregada).
7. Cierre registrado en memoria del proyecto (engram): decisión de vehículo, resultado SUS, y
   pendientes post-curso (R1–R7, retest).

---

*Referencias de esta planeación*: Rúbrica A5 (Canvas, 17-ago-2026) · Albert, B., y Tullis, T.
(2013). *Measuring the User Experience* (2.ª ed.), caps. 3–8 · Ramírez Mejía, A. I. (2023).
*Grocery shopping app. Part 5: Usability and Metrics* · Sauro, J., y Lewis, J. R. (2016).
*Quantifying the User Experience* (2.ª ed.) · Brooke, J. (1996). SUS · arXiv:2604.09581 ·
arXiv:2607.20773 · arXiv:2603.24321 (verificar autores al citar) ·
`context/planeacion_proyecto.md` §22, §25.2, §25.4 · retroalimentaciones del profesor A1–A4.
