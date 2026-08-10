# Plan de Excelencia — Actividad 3 (Semana 3)

**Entregable**: PDF `Entregable Actividad 3_equipo_8` · **Vence**: domingo 9-ago-2026, 23:59 (**hoy**)
**Rúbrica**: publicada, **20 puntos**. Absorbida el 9-ago-2026 conforme al protocolo §25.2 del plan.
**Estado del documento LaTeX**: `docs/entregables/main_a3.tex` compilado, 21 páginas, seis secciones escritas.
**Método de validación acordado**: **usuarios prototipo condicionados** (US-UX-01 + PerceptUI, §3.8 del plan). Decisión del equipo, 9-ago-2026.
**Naturaleza de este plan**: el documento ya existe. Esto es una **auditoría contra la rúbrica y un orden de reparación por puntos en riesgo** para las horas que quedan.

> Lo que ya está escrito en `docs/entregables/contenido/a3_*.tex` no se repite aquí. Este plan solo registra lo que **falta, contradice la rúbrica o desperdicia puntos**.

---

## 1. La rúbrica de A3, leída literalmente

### 1.1 Reparto de puntos

| Apartado | Peso | Puntos (de 20) | Estado actual |
|---|---|---|---|
| Portada con los nombres de los integrantes | 2 % | **0.4** | Completo |
| Introducción | 3 % | **0.6** | Riesgo de forma (§2.2) |
| Desarrollo del ejercicio de análisis competitivo | 25 % | **5.0** | Fuerte, con fugas (§2.3) |
| Desarrollo del ejercicio de card sorting | 25 % | **5.0** | **En riesgo mayor** (§2.4) |
| Desarrollo del ejercicio de information architecture | 25 % | **5.0** | Riesgo medio (§2.5) |
| Desarrollo del ejercicio de mapa de navegación | 20 % | **4.0** | Riesgo medio (§2.6) |

### 1.2 El descriptor que define la calificación

Los cuatro criterios de desarrollo usan **el mismo** descriptor de tres niveles:

- **Completo**: "Se incluyen **todos** los elementos solicitados".
- **Parcialmente**: "Se incluyen los elementos solicitados **pero puede carecer de contenido** alguno o varios de los elementos".
- **Incompleto**: "Faltan elementos solicitados a incluir o el contenido de los elementos es irrelevante".

Consecuencia operativa: la rúbrica **no premia profundidad, premia cobertura demostrada**. Enumera **26 pasos numerados** (5 de análisis competitivo + 10 de card sorting + 5 de IA + 6 de navegación) y cada paso ausente —o presente pero vacío de contenido propio— baja el criterio completo a "Parcialmente". La caída de "Completo" a "Parcialmente" en un solo criterio de 25 % cuesta **hasta 3 puntos de 20**.

**De aquí sale toda la estrategia de hoy**: el enemigo no es la falta de participantes humanos, es **el paso sin contenido**. Un paso ejecutado con usuarios prototipo, documentado y con datos calculados, tiene contenido. Un paso redactado en futuro, no.

### 1.3 Lo que la rúbrica dice sobre los participantes, y qué implica nuestra decisión

> "El equipo de trabajo desarrollará un ejercicio de card sorting basado en los hallazgos de la sección anterior. Para esto, **puede apoyarse de usuarios potenciales, o personas cercanas** que puedan sugerir un interés para el proyecto."

La rúbrica es permisiva en el reclutamiento. El equipo decidió **seguir con usuarios prototipo**, en coherencia con el método que ya sostiene A1 y A2. Es una decisión legítima y alineada con el diferenciador declarado del proyecto (§3.1), pero hay que ser exactos sobre su costo y su beneficio:

- **Beneficio real**: los pasos 6, 7 y 8 del card sorting pasan de futuro a pasado con datos **calculados**, no inventados; y el método es reproducible y auditable.
- **Riesgo real, declarado una vez**: el paso 6 dice "reúne participantes"; un evaluador estricto puede leer la ausencia de humanos como contenido faltante. No es evitable sin humanos, sí es **mitigable** con transparencia total del método y con la palanca opcional de §3.8.
- **Consecuencia administrativa**: `context/planeacion_proyecto.md` §22.1.b compromete "card sorting de A3 (≥6 participantes)". Ese compromiso hay que **reescribirlo** para que diga lo que realmente se hizo y mover la validación humana a A5. Un plan que dice una cosa y un entregable que hace otra es la peor de las dos opciones (§7.4).

### 1.4 Recurso de apoyo que la rúbrica nombra

Ramírez Mejía, A. I. (2023). *Grocery shopping app. A guided UX case study. Part 3: Competitive analysis and Information architecture*. TC4032, MNA, ITESM. **No está citado en el documento.** Citarlo es gratuito y señala que el equipo trabajó sobre el material asignado (§5.5).

---

## 2. Auditoría del entregable actual, criterio por criterio

### 2.1 Portada — 0.4 pts — sin acción

`uxdoc.sty` imprime los tres nombres con matrícula. Cumple.

Corrección de 1 minuto: `main_a3.tex` fija la fecha de portada en **5 de agosto de 2026** y la entrega es el **9**. Alinear a `9 de agosto de 2026`.

### 2.2 Introducción — 0.6 pts — [P0, 10 minutos]

La rúbrica pide, textualmente, "una **introducción** sobre la actividad realizada". El documento abre con `\uxsection{0. Preliminares y Objetivos}`.

Es una introducción, pero **no se llama así**, y un criterio de checklist se evalúa por lo que se ve en el índice.

**Reparación en `a3_00_preliminares.tex`:**
1. Renombrar la sección a **`Introducción`** (sin el "0.").
2. Añadir un párrafo de mapa de lectura: qué contiene cada una de las cuatro secciones y qué decisión sostiene cada una.
3. Añadir la línea de continuidad: A1 definió problema y perfiles, A2 escenarios y recorrido, A3 convierte esos hallazgos en estructura.
4. **Anunciar el método aquí, no esconderlo en la sección 2.** Una frase: la validación de esta actividad se ejecutó con usuarios prototipo condicionados, en continuidad con el método de A1 y A2, y la validación con personas reales ocurre en A5. Declararlo al frente convierte una posible objeción en una decisión de método.

### 2.3 Análisis competitivo — 5.0 pts — [P1]

Contenido sólido y objetivo: cuatro competidores con ficha, posturas estratégicas, precios reales, matriz comparativa, ventaja en cuatro dimensiones y estrategias de mitigación. Es la sección más fuerte del documento y **no depende del cambio de método**.

Cuatro fugas concretas:

**(a) Los 5 pasos de la rúbrica no son visibles como pasos.** Card sorting, IA y navegación sí numeran sus pasos en los subtítulos; análisis competitivo no. Renumerar:

| Paso de rúbrica | Subtítulo propuesto | Ya existe como |
|---|---|---|
| 1. Identifica a tus competidores | 1. Identificación de competidores | Competidores Identificados y Posturas Estratégicas |
| 2. Reúne información sobre tus competidores | 2. Recolección de información y fuentes | Trazabilidad de Fuentes |
| 3. Analiza a tus competidores | 3. Análisis comparativo | Matriz de Análisis |
| 4. Identifica tu ventaja competitiva | 4. Ventaja competitiva | Ventaja Competitiva |
| 5. Desarrolla estrategias | 5. Estrategias de mejora y diferenciación | Estrategias de Mejora... |

Es reordenar títulos, no reescribir contenido.

**(b) Las calificaciones de clientes están sin fuente ni fecha.** El documento afirma G2 4.3/5 (Bloomberg), G2 4.5/5 (Power BI) y Capterra 4.4/5 (Pyramid). La rúbrica pide "calificaciones de clientes" y exige "información actualizada". Una calificación sin URL ni fecha de consulta es el punto más atacable de la sección. **Verificar los tres números y añadirlos a la tabla de Trazabilidad de Fuentes con fecha de consulta**; si alguno no se verifica, sustituirlo por una cita textual de reseña o eliminarlo. Un dato menos, verificado, vale más que tres afirmados.

**(c) "Redes sociales" y "material promocional" se mencionan pero no se evidencian.** Basta una fila más en la tabla de fuentes (LinkedIn corporativo de Pyramid, blog oficial de precios de Power BI —ya en referencias— y la página de producto de Bloomberg) para cerrar el paso 2.

**(d) Sin evidencia visual de los competidores.** Hay logotipos, no interfaces. Ver la restricción de §6.3.

**(e) Las cuatro posturas competitivas están usadas sin citar su fuente.** Ver §9.1: la tipología es de Annacchino (2003, cap. 3) y hoy aparece como si fuera criterio propio del equipo.

### 2.3.1 Verificación en línea de los datos ya escritos (consultado el 9-ago-2026)

| Dato en el documento | Verificado hoy | Acción |
|---|---|---|
| Bloomberg "≈\$30,000 a \$32,000 USD anuales" | **\$31,980 USD/año** por terminal única y **\$28,320 USD/asiento** en contratos multi-terminal. Mínimo **2 años** de contrato, cobro trimestral anticipado. Alza de **6.5 %** aplicada a renovaciones desde el 1-ene-2025 | Precisar la cifra y añadir el contrato mínimo: **refuerza el argumento de TCO**, porque el costo real no es anual sino bienal comprometido |
| Bloomberg "G2 (4.3/5)" | **G2: 4.4/5 sobre 69 reseñas** | Corregir el número y **añadir el n** — una calificación sin denominador no es un dato |
| Bloomberg "interfaz heredada de DOS, exige memorizar comandos" | **Confirmado por las reseñas**: los evaluadores describen "software de los 80", curva de aprendizaje brutal, tareas simples sepultadas bajo códigos de comando, y sobrecarga de información hasta memorizar la navegación | Ya no es opinión del equipo: es **evidencia de reseñas de clientes**, que es exactamente lo que pide el paso 2 de la rúbrica |
| Power BI Pro "≈\$14 USD/mes" | Correcto | Añadir fecha de consulta |
| Pyramid "sin tarifas públicas" | Se sostiene | Sin cambio |

**Nota de honestidad sobre las fuentes de precio.** Bloomberg, Pyramid y Collibra **no publican tarifas oficiales**; las cifras provienen de agregadores de precios y de compras verificadas por terceros. En el documento hay que etiquetarlas como **estimaciones de mercado**, no como precios de lista. Donde sí hay fuente oficial —Power BI— se cita la página del fabricante. Esa distinción, escrita en una línea al pie de la matriz, es más rigor del que suele aparecer en un análisis competitivo de posgrado.

### 2.3.2 El hallazgo que cambia el argumento

**Power BI retira Q&A en diciembre de 2026** y lo sustituye por Copilot. Las condiciones documentadas de ese reemplazo:

- Un administrador debe habilitar Copilot en Fabric; los workspaces **Premium Per User no están soportados** en Desktop.
- Los visuales Q&A existentes **dejarán de funcionar** y las herramientas de configuración —sinónimos, relaciones lingüísticas, "teach Q&A"— se retiran.
- Copilot **no cubre** pronóstico, detección de anomalías ni análisis de influenciadores clave, y no funciona sobre modelos en tiempo real ni conexiones vivas a Analysis Services.

Esto es oro para la sección de ventaja competitiva y hay que usarlo con precisión: el competidor más probable **dentro** de la institución está en plena transición de su capacidad de lenguaje natural, con dependencias de licenciamiento y limitaciones publicadas por el propio fabricante. Convierte un argumento genérico ("nuestra UX es mejor") en uno **fechado y verificable**: durante la ventana en que Power BI migra de Q&A a Copilot, Karisma Data ofrece consulta en lenguaje natural gobernada, sobre el vocabulario de la institución y sin licencia adicional por usuario.

### 2.3.3 Competidores nuevos propuestos

Ordenados por relevancia para el producto, con la postura de Annacchino que les corresponde:

| Competidor | Postura | Datos verificados (9-ago-2026) | Por qué debe estar |
|---|---|---|---|
| **ThoughtSpot** (Spotter) | Persecución Directa | \$25 USD/usuario/mes (Essentials), \$50 (Pro), Enterprise con contrato promedio ≈\$137,000 USD/año | **El competidor conceptual de Karisma Data.** Es el único del panel que ataca la misma promesa: preguntar en lenguaje natural sobre datos gobernados. Omitirlo deja el análisis incompleto justo en el diferenciador del producto |
| **Collibra** | Defensiva (gobierno de datos) | Suscripción base ≈\$170,000 USD/año; cliente mediano ≈\$197,000 USD/año; servicios profesionales a \$500 USD/hora; despliegues de meses a años | Es el referente de catálogo y gobierno. Sus cifras hacen el argumento de TCO **mucho más fuerte** que compararse solo contra Bloomberg, y su tiempo de despliegue valida la estrategia de MVP iterativo ya escrita |
| **Microsoft Purview** | Alternativa Funcional interna | Medido por consumo de Azure: 1 unidad de capacidad por hora por cada 10 GB de metadatos, más vCore-hora de escaneo; integrado con Fabric y etiquetas de sensibilidad | Si la institución ya usa Power BI, **Purview es lo que un directivo va a proponer en la primera reunión**. Conviene responderle en el documento y no en la junta |
| **LSEG Workspace** (ex-Refinitiv Eikon) | Persecución Directa contra Bloomberg | ≈\$22,000–24,000 USD/usuario/año el paquete central; ≈\$26,000 con módulos premium; ≈90 % de la profundidad de datos de Bloomberg | Demuestra que el equipo conoce el mercado de terminales y no solo el nombre más famoso |
| **Atlan** | Persecución Oblicua (gobierno) | Líder del Gartner Magic Quadrant de Gobierno de D&A 2026; linaje a nivel de columna como propiedad consultable, expuesto a agentes vía servidor MCP | Es **hacia donde va Karisma Data**: catálogo + linaje + acceso agéntico. Citarlo demuestra vigilancia tecnológica y obliga a declarar honestamente en qué no vamos a competir |

**Alcance recomendado para hoy.** No meter los cinco. §2.4 del plan del proyecto fija el diferenciador de A3 en un benchmark de **4 a 6 productos**, y ya hay cuatro.

- **Añadir dos con ficha completa: ThoughtSpot y Collibra.** Uno por cada frente que define al producto —conversacional y gobierno—. Con eso el panel queda en seis y cubre las tres familias: terminal financiera, BI y catálogo/gobierno.
- **Purview, LSEG y Atlan** entran en una tabla corta de *"otras alternativas consideradas"*, una línea y una fuente cada una. Cubre el paso 1 de la rúbrica —"investiga los negocios que ofrecen productos o servicios similares"— con amplitud demostrable y sin costo de redacción.

**Dos condiciones de consistencia**, o la sección pierde más de lo que gana:

1. Cada entrada nueva se clasifica con **la misma tipología de Annacchino**, y entra a la **matriz comparativa** con las mismas cuatro dimensiones. Un competidor descrito en prosa pero ausente de la matriz se lee como relleno.
2. Cada cifra nueva va a la tabla de Trazabilidad de Fuentes con URL y **"Consultado el 9 de agosto de 2026"**, y las estimaciones de agregadores se etiquetan como tales (§2.3.1).

**Efecto sobre la ventaja competitiva.** Con ThoughtSpot y Collibra en el panel, el argumento de Karisma Data deja de ser "somos más baratos que Bloomberg" —comparación fácil— y pasa a ser el que de verdad sostiene el producto: **ninguna de las seis alternativas resuelve simultáneamente catálogo gobernado, linaje visible y consulta en lenguaje natural sobre el vocabulario de la institución, sin licencia por usuario.** ThoughtSpot tiene lo conversacional pero no el contexto institucional; Collibra tiene el gobierno pero no la consulta; Power BI tiene la consulta en transición y el gobierno fragmentado. Esa frase, respaldada por las cifras verificadas, es la mejor versión posible de la sección.

### 2.4 Card sorting — 5.0 pts — [P0, el riesgo mayor del entregable]

**Diagnóstico.** La estructura cubre los 10 pasos, pero los pasos **6 (realiza el ejercicio), 7 (observa y documenta) y 8 (analiza los resultados)** están en **futuro** y declaran una simulación sin procedimiento:

- "El ejercicio **se diseñó** para realizarse... **no corresponde** a una captura de una sesión con usuarios".
- "El registro de cada participante **incluirá**...".
- "El análisis **combinará** las agrupaciones con las notas cualitativas".

Tres de diez pasos sin contenido propio encajan literalmente en "puede carecer de contenido alguno o varios" — **Parcialmente, techo de 4.0 de 5.0**.

**Y hay un problema peor que el tiempo verbal.** El dendrograma actual y los porcentajes (84 %, 85 %, 97 %) **los inventó el equipo para ilustrar un formato**. Aunque estén rotulados como simulación —y lo están, con honestidad—, son cifras sin procedimiento detrás. Ese es el verdadero flanco débil, y es el que el método de usuarios prototipo **sí resuelve**: la §3 sustituye números inventados por números **calculados a partir de un ejercicio ejecutado y registrado**.

**Dos huecos metodológicos adicionales que la ejecución cierra sola:**

- **Falta la matriz de similitud.** Baxter, Courage y Caine (2015, cap. 11) describen **dos** técnicas de análisis: matriz de similitud y análisis de conglomerados. El documento solo trae dendrograma.
- **El argumento facetado se sostiene en aire.** Hoy la decisión de etiquetado múltiple se justifica con un dendrograma inventado. El capítulo 11 documenta que los participantes piden colocar una misma tarjeta en varios grupos y que hay que anotarlo a mano. Con ocho evaluadores condicionados por perfiles distintos, **el desacuerdo entre perfiles es exactamente el dato que justifica las facetas** (§3.5). Es el mayor salto de calidad disponible hoy.

### 2.5 Arquitectura de la información — 5.0 pts — [P0/P1]

Pasos 1, 2, 3 y 5 cubiertos con contenido propio. Dos problemas:

**(a) Paso 4 "Prueba la arquitectura de la información": diseñado, no ejecutado.** La tabla de tree testing con cinco tareas está bien construida, pero: "El instrumento **solicitará**...", "Esto **permitirá** verificar...". Mismo patrón, mismo castigo. **Se ejecuta hoy con los mismos ocho evaluadores** (§3.6): 5 tareas × 8 = 40 observaciones y una tabla de resultados en lugar de una tabla de intenciones.

**(b) Paso 5 "Diseña la navegación": descrito, no dibujado.** El texto argumenta bien la barra lateral fija frente al menú hamburguesa, pero no hay ninguna imagen. La figura ya está generada: `figuras/a3_wireframe_navegacion.png` (§6.2).

**(c) Palanca de marco teórico.** El documento cubre los sistemas de **organización** y **navegación** de Morville y Rosenfeld (2006) —ya citados— pero no nombra los otros dos que **ya implementa**: **etiquetado** (sustituir "Logs de Sistema" por "Bitácora de Accesos" es exactamente eso) y **búsqueda** (el buscador facetado). Dos frases.

### 2.6 Mapa de navegación — 4.0 pts — [P1]

Los seis pasos están presentes; 1, 2, 3 y 6 con contenido propio. Dos en futuro:

- **Paso 4 "Valida y mejora"**: la rúbrica pide "recopilando e **incorporando** sus comentarios... y **refinándolo**". Exige **cambios aplicados**, no un plan de recolección. La tabla de cambios que el documento ya anuncia (versión anterior / observación / modificación / justificación) **hay que llenarla** con lo que salga de la sesión sintética. Tres filas reales cierran el paso.
- **Paso 5 "Implementa y prueba"**: aquí el futuro es legítimo —el desarrollo es de A4 en adelante— pero hay que anclarlo: qué se prototipa, con qué tareas se prueba y en qué actividad ocurre. Ver §7.

La hipótesis declarada sobre "Credenciales API" (segundo nivel, no enterrada) es excelente porque es **falsable**. Contrastarla hoy con los evaluadores de perfil técnico (Ximena, Jorge, Mariana) y reportar si se confirmó o se refutó. Un supuesto refutado y corregido vale más que cinco confirmados.

### 2.7 Hallazgo transversal: el tiempo verbal es el defecto principal

Repartidos entre las cuatro secciones hay del orden de **veinte verbos en futuro o condicional** dentro de criterios llamados "**Desarrollo del** ejercicio". Un desarrollo redactado en futuro se lee como un ejercicio no desarrollado.

Regla de edición para la pasada final: **dentro de las secciones 1 a 4, todo verbo en futuro debe (a) volverse pasado porque se ejecutó, o (b) mudarse a un apartado explícito de "siguientes pasos" al cierre de su sección.** Ningún futuro suelto en medio del desarrollo.

---

## 3. El método: card sorting con usuarios prototipo condicionados

Esta sección sustituye por completo la de reclutamiento humano. Recupera hasta **2 puntos** repartidos entre card sorting, IA y mapa, y es la acción de mayor retorno de la jornada.

### 3.1 Por qué esta decisión es coherente, y no un atajo

No es una improvisación de último momento: **estaba escrita en el plan del proyecto desde el 22-jul**.

- §3.8 del plan adopta **PerceptUI** (Bougie et al., 2026, arXiv:2606.05697) y dice textualmente que las personas de A1 se reutilizan "como *condicionamiento* de evaluadores sintéticos para **pre-validar wireframes (A3)** y prototipos de alta fidelidad (A4)".
- §1 del plan lo nombra "la novedad 2026 que aporta el equipo".
- La skill `portal-synthetic-users` ya tiene el protocolo, la plantilla de prompt y el checklist.
- A1 y A2 se construyeron con **usuarios prototipo** (US-UX-01) y ambos documentos ya declaran su base.

O sea: A3 no cambia de método, **lo continúa**. Lo que cambia es que por primera vez el método produce datos, no solo descripciones. Eso es un argumento fuerte para escribir en el documento, no algo que esconder.

### 3.2 Cómo se nombra, y cómo no

Esto define si la sección se lee como rigor o como truco. Regla de vocabulario, sin excepciones:

| Nunca escribir | Escribir |
|---|---|
| "participantes", "los usuarios agruparon" | "evaluadores prototipo", "los evaluadores condicionados agruparon" |
| "se aplicó a 8 personas" | "se ejecutó con 8 evaluadores condicionados, uno por persona de A1" |
| "resultados del card sorting" | "resultados de la pre-validación sintética del card sorting" |
| "el 75 % de los usuarios..." | "6 de los 8 evaluadores..." (frecuencias absolutas, no porcentajes con aire de encuesta) |

Los porcentajes con denominador pequeño inflan la percepción de evidencia. **Con n = 8 se reportan conteos**, no porcentajes.

### 3.3 Los ocho evaluadores

Uno por cada persona de A1 — el proyecto entregó **8 personas y 8 mapas de empatía**, así que el condicionamiento es completo y no hay que inventar perfiles:

| # | Persona de A1 | Perfil | Qué aporta al sorteo |
|---|---|---|---|
| 1 | Laura Méndez | Operativo | Inmediatez; penaliza jerarquías profundas |
| 2 | Diego Hernández | Analista | Cruce de fuentes; es quien más pedirá etiquetas múltiples |
| 3 | Arturo Castañeda | Directivo | Resúmenes; agrupará por decisión, no por origen del dato |
| 4 | Roberto Valdez | Propietario de datos | Gobierno y linaje; separa definición de consumo |
| 5 | Ximena Solís Barrera | Integración | API y credenciales; prueba la hipótesis de segundo nivel |
| 6 | Mariana Ovalle Ríos | Administración | Accesos y bitácora |
| 7 | Elena Ruiz | Auditoría | Trazabilidad; escenario de reserva de A2, aquí se aprovecha |
| 8 | Jorge Mendieta | Ingeniería de datos | Conectores y cargas; escenario de reserva de A2 |

Ocho evaluadores **cubre en número** el "≥6" que §22.1.b del plan comprometía, pero no en naturaleza. Decirlo así en el documento, sin ambigüedad.

**Sobre el tamaño de muestra**: Baxter, Courage y Caine (2015, cap. 11), citando a Tullis y Wood (2004), sitúan en 15–20 participantes el 90 % de correlación con el conjunto completo y recomiendan, con presupuesto limitado, correr 6–8 y verificar estabilidad. Citarlo es correcto **como referencia del estándar**, pero hay que ser preciso: ese umbral se estableció para participantes humanos y **no es trasladable** a evaluadores sintéticos. Se cita para justificar el orden de magnitud del diseño, no para reclamar su poder estadístico. Esa precisión, escrita, es lo que distingue a un equipo que leyó el capítulo de uno que lo citó.

### 3.3.1 Las personas son las de A1, y son las mismas en todo el documento

**Sí: se usan las personas ya publicadas en A1, sin reescribirlas.** Esa es la condición que le da valor al método —el condicionamiento reutiliza investigación previa del propio equipo— y también la que mantiene la coherencia de la serie A1→A2→A3. Si una ficha se retoca para que "funcione mejor" en el ejercicio, deja de ser reutilización y pasa a ser un perfil ad-hoc.

Y no valen solo para la sección 2: **ya sostienen argumentos en las cuatro secciones del documento**. Este es el uso actual:

| Sección | Personas presentes | Hueco |
|---|---|---|
| Introducción | Laura, Roberto | — |
| 1. Análisis competitivo | Laura, Diego, Arturo, Roberto, Ximena | Falta Mariana; **faltan anclas para ThoughtSpot y Collibra** (§2.3.3) |
| 2. Card sorting | Laura, Diego, Arturo, Roberto, Ximena, Mariana | Elena y Jorge ausentes |
| 3. Arquitectura | Laura, Diego, Arturo, Ximena, Mariana | Falta Roberto pese a ser el perfil de gobierno |
| 4. Mapa de navegación | Laura, Ximena, Mariana | — |
| Conclusión | **ninguna** | El cierre no aterriza en nadie |

Tres reglas para la pasada final:

**(a) Elena Ruiz y Jorge Mendieta dejan de estar ausentes.** Hoy no aparecen en ninguna sección de A3, aunque existen desde A1 y tienen escenario de reserva en A2. Como evaluadores 7 y 8 (§3.3), sus agrupaciones y sus racionales entran de forma natural en los pasos 7 y 8 del card sorting — **sin escribir un escenario nuevo**. Así se salda la deuda #3 de A2 (§5) con trabajo que de todas formas se iba a hacer.

**(b) Cada competidor nuevo necesita su ancla de persona.** Las cuatro fichas actuales funcionan porque cada debilidad aterriza en alguien: la curva de Bloomberg golpea a Laura, los workspaces aislados de Power BI golpean a Diego, la falta de API del *status quo* golpea a Ximena, el gobierno por correo golpea a Roberto. Si ThoughtSpot y Collibra entran sin ancla, se leerán como relleno investigado. Anclas sugeridas:

- **ThoughtSpot** → **Diego** y **Arturo**: resuelve la pregunta en lenguaje natural, pero sobre el modelo de datos que le carguen, sin el vocabulario ni las notas tribales de la institución — y con costo por usuario que impide abrirlo a toda la organización.
- **Collibra** → **Roberto** y **Elena**: resuelve el gobierno y el linaje que ambos necesitan, pero con un despliegue de meses a años y un TCO que ninguna de las dos puede justificar para el alcance de un portal de consulta.

**(c) Coherencia de nombre y rol.** Nombre completo en la primera aparición de cada sección y solo el nombre de pila después; el mismo rol atribuido en todo el documento. Revisar en particular `a3_03_arquitectura.tex`, que anuncia "cuatro arquetipos clave" y enseguida enumera cinco nombres.

**(d) El cierre aterriza en personas.** Hoy la conclusión no menciona a ninguna. Después de la corrida hay material para cerrar con lo concreto: qué supuesto de qué perfil quedó sostenido por la pre-validación y cuál sigue esperando la prueba con humanos de A5.

### 3.4 Procedimiento de ejecución (reproducible y auditable)

Esto es lo que convierte "simulación" en "método". Cada paso deja archivo.

1. **Fijar el instrumento.** Volcar las 35 tarjetas con su definición a `docs/entregables/datos/a3_tarjetas.csv` (`id, etiqueta, definicion`). Sale directo de la tabla que ya está en `a3_02_card_sorting.tex`.
2. **Fijar las fichas de condicionamiento.** Un archivo por persona en `docs/entregables/datos/personas/`, extraído de `a1_cuerpo.tex`: demografía, antecedentes, objetivos, pain points, hábitos y frase. **Sin editar para el ejercicio** — se usa lo publicado en A1; si se retoca, deja de ser reutilización de investigación previa.
3. **Correr las 8 sesiones** con la plantilla de prompt de la skill `portal-synthetic-users`, en sort **abierto**: el evaluador crea sus grupos y **les pone nombre**. Preguntas de cierre obligatorias:
   - ¿Qué tarjeta te costó más ubicar y por qué?
   - ¿Alguna la pondrías en dos grupos a la vez? ¿Cuál y por qué? ← **la pregunta clave** (§3.5)
   - ¿Alguna etiqueta no se entiende en tu vocabulario de trabajo?
4. **Guardar la salida cruda** de cada sesión en `docs/entregables/datos/a3_sorts/P1.json … P8.json`. **Esto es la documentación del paso 7**: sin salida cruda archivada, el ejercicio vuelve a ser una afirmación.
5. **Normalizar** a una sola tabla larga: `evaluador, tarjeta, grupo_asignado, nombre_del_grupo, observacion`.
6. **Calcular** matriz de similitud y dendrograma desde esa tabla (§6.1). Nada de figuras dibujadas a mano.
7. **Frecuencia de palabras** sobre los nombres de grupo — técnica que el capítulo 11 recomienda para nombrar categorías. Es lo que convierte la promesa de "folksonomía dirigida" de la sección de ventaja competitiva en algo demostrado.

**Condición de honestidad del procedimiento**: se archiva lo que salga, incluido lo incómodo. Si un evaluador agrupa de forma que rompe la arquitectura propuesta, **eso se reporta y se discute**; es justo el tipo de hallazgo que sube la calificación.

### 3.5 El desacuerdo entre perfiles es el hallazgo, no el ruido

Con ocho evaluadores condicionados por perfiles deliberadamente distintos, lo valioso no es dónde coinciden sino **dónde no**:

- Si *Derivados* cae en "Exploración" para Diego y en "Gobierno" para Roberto → la tarjeta es **transversal**, y ahí está la evidencia procedimental del **etiquetado múltiple** que hoy el documento afirma sin respaldo.
- Si *Credenciales API* aparece en primer nivel para Ximena y en tercero para Laura → la hipótesis del mapa de navegación queda **contrastada**, con veredicto.
- Si *Bitácora de Accesos* se agrupa distinto entre Mariana y Elena → hay un problema de etiqueta, no de estructura.

**Producto concreto**: una tabla de "tarjetas en disputa" con la tarjeta, los grupos en que cayó, qué perfiles la colocaron en cada uno y la decisión de arquitectura resultante (faceta, renombre o reubicación). Es la tabla más citable del documento y hoy no existe.

### 3.6 La prueba de árbol, en la misma corrida

Las cinco tareas ya están redactadas en `a3_03_arquitectura.tex`. Al cierre de cada sesión, presentar solo los cuatro módulos de primer nivel y pedir el primer clic, luego el segundo nivel. Registrar: ruta elegida, acierto/fallo, retroceso, duda.

5 tareas × 8 evaluadores = **40 observaciones**. Se reporta tasa de acierto **por tarea** (x de 8), no un promedio global — el promedio esconde justo la tarea que falla.

### 3.7 Qué se reescribe en el documento

| Archivo | Subsección | Cambio |
|---|---|---|
| `a3_00_preliminares.tex` | — | Renombrar a "Introducción"; declarar el método al frente (§2.2) |
| `a3_02_card_sorting.tex` | 6 | "Simulación del ejercicio" → **"Aplicación del ejercicio con evaluadores prototipo"**: fecha, n = 8, condicionamiento, modalidad, herramienta |
| `a3_02_card_sorting.tex` | 7 | Observaciones reales por evaluador; nombres de grupo **literales**; referencia a las salidas archivadas |
| `a3_02_card_sorting.tex` | 8 | **Matriz de similitud + dendrograma calculados**; los porcentajes 84/85/97 se sustituyen por conteos sobre 8 o se eliminan |
| `a3_02_card_sorting.tex` | 8 (nuevo) | **Tabla de tarjetas en disputa** (§3.5) |
| `a3_02_card_sorting.tex` | 9 | Las cuatro categorías se confirman, ajustan o renombran según los nombres que dieron los evaluadores |
| `a3_02_card_sorting.tex` | 10 | Qué se cambió del instrumento y de la taxonomía después de la corrida |
| `a3_02_card_sorting.tex` | `uxnota` | **Reescribir por completo**: ya no advierte sobre una simulación ilustrativa, sino que declara método, alcance, sesgos y límites (§3.9) |
| `a3_03_arquitectura.tex` | 4 | Tabla de resultados de la prueba de árbol (aciertos por tarea, x de 8) |
| `a3_03_arquitectura.tex` | 5 | Insertar el wireframe |
| `a3_04_mapa.tex` | 4 | Tabla de cambios con filas reales; veredicto sobre "Credenciales API" |
| `a3_05_cierre.tex` | — | Ajustar: el cierre habla hoy de "la simulación permitió revisar la cobertura"; ahora hay resultados |

**Lo que no se toca**: el rigor con que el documento distingue hipótesis de evidencia. Se mantiene — aplicado ahora a datos de un método declarado.

### 3.9 La nota de método, obligatoria

Reemplaza la `uxnota` actual. Debe decir, en este orden y sin adornos:

1. **Qué se hizo**: card sorting abierto con 8 evaluadores condicionados por las personas de A1, protocolo PerceptUI (Bougie et al., 2026), fecha y herramienta.
2. **Qué permite afirmar**: cobertura y coherencia interna de la taxonomía, detección de tarjetas ambiguas o transversales, hipótesis de vocabulario y de rutas.
3. **Qué NO permite afirmar**: comportamiento de usuarios reales, generalización estadística, ni medición alguna sobre el desempeño del CIF actual.
4. **Sesgos declarados**: los evaluadores heredan sesgos del modelo y de **cómo el propio equipo redactó las personas**; sus respuestas son predicciones plausibles, no datos de campo, y no se mezclan con ninguna cifra de instrumento.
5. **Cuándo llega la validación humana**: prueba de usabilidad SUS de A5, ≥5 participantes reales, exigida por rúbrica.

Es la sección que un evaluador con formación en investigación va a buscar. Escrita así, convierte la principal objeción del documento en su mayor muestra de madurez.

### 3.8 Palanca opcional, 30 minutos, si aparece alguien

Si en el transcurso de la tarde hay dos o tres personas cercanas disponibles, correr el sorteo con ellas **como conjunto de contraste** y añadir un párrafo: ¿el sorteo sintético coincidió con el humano? Coincidencia = evidencia de que el condicionamiento funcionó. Discrepancia = hallazgo publicable y honesto. No sustituye nada, no cambia el método declarado y es de las cosas que ningún otro equipo va a entregar. **Opcional; no bloquea la entrega.**

---

## 4. Palancas de excelencia (solo lo que no está en el documento)

**4.1 Matriz de rúbrica → sección → página, al inicio.** Con 26 pasos evaluados por cobertura, una tabla de una página que mapee cada paso a su sección le ahorra la búsqueda al evaluador y hace visible que ningún paso falta. Se usó en A1; aquí conviene aún más, porque esta rúbrica es la más checklist de las tres.

**4.2 Matriz de similitud.** Segunda técnica de análisis del capítulo 11, hoy ausente. Mapa de calor con el número de evaluadores que agruparon cada par de tarjetas.

**4.3 Tabla de tarjetas en disputa.** §3.5. La palanca de mayor retorno de todo el documento.

**4.4 Wireframe de navegación.** Ya generado (§6.2). Cierra el paso 5 de IA y tiende el puente a A4.

**4.5 Citar el recurso de apoyo de la propia rúbrica.** Ramírez Mejía (2023), en referencias y en el cuerpo del análisis competitivo.

**4.6 Nombrar los cuatro sistemas de Morville y Rosenfeld.** §2.5(c). Dos frases.

**4.7 Trazar el card sorting a las etapas 3 y 4 del journey de A2.** Compromiso escrito en el plan de A2. Una frase en el propósito: las tarjetas de *Exploración y extracción* corresponden a la etapa de búsqueda y las de *Gobierno* a la de validación —el momento de la verdad del journey—.

**4.8 Evaluar a los competidores contra los principios rectores de A2.** Otro compromiso de A2 y **la palanca más diferenciadora del análisis competitivo**. La matriz compara hoy curva de aprendizaje, integración, UX y costo —criterios genéricos—. Añadir una tabla que puntúe a cada competidor contra los cinco principios ya publicados (Respaldado, Simple primero, Profundidad a un paso, Sin sorpresas, Explicable) convierte el benchmark en una evaluación con criterio propio. No requiere investigación nueva.

**4.9 No repetir la distinción IA / mapa de navegación.** El documento ya la resuelve bien una vez, en `a3_03_arquitectura.tex`. No reforzarla en la introducción ni en el cierre: sería redundancia visible.

---

## 5. Deuda heredada del plan de A2

| # | Compromiso de A2 | Destino en A3 |
|---|---|---|
| 1 | Validar el journey map con datos de campo y publicar la versión anotada | **Reformulado**: la corrida sintética toca las etapas 3–4. Declarar en el cierre qué supuesto quedó sostenido por la pre-validación y cuál sigue esperando a A5 |
| 2 | Journey maps complementarios de analista y directivo | **Cerrado en A2** (`journey_diego.pdf`, `journey_arturo.pdf`). No se arrastra |
| 3 | Escenarios de reserva: Elena Ruiz (auditoría), Jorge Mendieta (ingeniería) | **Se aprovechan hoy**: son los evaluadores 7 y 8 (§3.3). La deuda se salda sin escribir escenarios nuevos |
| 4 | Brecha de conocimiento por etapa → requisito de contenido del sitemap | **Pendiente y barato**: una fila más en la tabla de trazabilidad de `a3_03_arquitectura.tex` ligando cada brecha del journey al nodo de la IA que la resuelve |
| 5 | Principios rectores y antiprincipios como criterio del benchmark | **Pendiente**: palanca §4.8 |
| 6 | Card sorting apoyado en las etapas 3 y 4 del journey | **Pendiente**: palanca §4.7 |

Cinco de seis se cierran con material que ya existe. Es coherencia longitudinal a costo casi nulo, y es lo que distingue una serie de entregables de una pila de tareas sueltas.

---

## 6. Plan de figuras

Confirmado: **todas las figuras de datos se generan con matplotlib**, desde los datos archivados en §3.4, extendiendo `docs/entregables/generar_figuras_a3.py`. Ninguna figura de resultados se dibuja a mano ni se genera con un modelo de imagen.

### 6.1 Funciones a añadir al script

```python
def generar_matriz_similitud():
    """Heatmap 35x35: numero de evaluadores que agruparon cada par de tarjetas.

    Lee docs/entregables/datos/a3_sorts/*.json, cuenta co-ocurrencias por par,
    ordena las tarjetas por el orden hoja del dendrograma para que los bloques
    de la matriz coincidan visualmente con los clusteres.
    Escala 0-8 con la paleta institucional. Salida: figuras/a3_matriz_similitud.png
    """

def generar_dendrograma_real():
    """Reemplaza generar_dendrograma_card_sorting().

    Distancia = 1 - (co-ocurrencias / n_evaluadores); linkage average.
    El pie de figura debe declarar n=8 y el metodo de condicionamiento.
    Salida: figuras/a3_dendrograma.png
    """

def generar_tarjetas_en_disputa():
    """Barras horizontales apiladas: por cada tarjeta con desacuerdo, cuantos
    evaluadores la pusieron en cada grupo, coloreado por grupo.
    Solo tarjetas colocadas en >=2 grupos distintos.
    Salida: figuras/a3_disputa.png
    """
```

`generar_mapa_navegacion()` y `generar_matriz_competitiva()` se conservan; el mapa de sitio se regenera solo si el sorteo mueve alguna etiqueta.

**Detalle de rigor en los pies de figura**: cada figura derivada de la corrida sintética lleva en su `\figuraux` el `n = 8` y la palabra "prototipo" o "sintética". Una figura que no dice de dónde viene se lee como dato de campo.

### 6.2 Inventario

| Figura | Estado | Origen |
|---|---|---|
| `cif_header.png`, `cif_menu.png` | Existen | **Captura real** — la evidencia más valiosa del documento |
| `a3_matriz_competitiva.png` | Existe | matplotlib; posiciones por juicio del equipo, **declararlo en el pie** |
| `a3_arquitectura_informacion.png` | Existe | matplotlib |
| `a3_mapa_sitio.png` | Existe | matplotlib; regenerar si cambia una etiqueta |
| `a3_tablero_simulado.png` | Existe | matplotlib; se relabela como instrumento aplicado |
| `a3_dendrograma.png` | Existe, **inventado** | **Regenerar desde datos** (§6.1) |
| `a3_matriz_similitud.png` | **Falta** | matplotlib (§6.1) |
| `a3_disputa.png` | **Falta** | matplotlib (§6.1) |
| `a3_wireframe_navegacion.png` | **Generada** | Nano Banana (Gemini 3 Pro Image) |
| Capturas de competidores | **Faltan** | Captura manual (§6.3) |

La figura `a3_wireframe_navegacion.png` ya está en `docs/entregables/figuras/`: barra lateral fija con los cuatro módulos —Inicio, Exploración (activo), Gobierno, Administración—, los tres subniveles de Exploración —Catálogo temático, Búsqueda facetada, Exportaciones—, buscador unificado y panel lateral de metadatos. Etiquetas en español verificadas.

```latex
\figuraux{figuras/a3_wireframe_navegacion.png}{Diseño de la navegación: barra lateral
fija con los cuatro módulos, buscador unificado y panel de metadatos. Bosquejo de
baja fidelidad elaborado para esta actividad; la interfaz de alta fidelidad se
desarrolla en la Actividad 4.}{fig:wireframe}
```

El pie **debe** decir que es un bosquejo propio de baja fidelidad. Sin esa aclaración, un wireframe limpio se puede leer como captura de un producto que aún no existe.

### 6.3 Regla sobre imágenes generadas con IA

**Permitido** — ilustración de conceptos propios, rotulada:
- Bosquejos y wireframes del producto propio (es diseño, no evidencia).
- Diagramas conceptuales.
- Retratos de personas ficticias, como ya se hizo en A1.

**Prohibido** — fabricación de evidencia:
- **Fotografías o capturas de sesiones de card sorting con usuarios.** Serían evidencia falsificada. El ejercicio se ejecutó con evaluadores prototipo y así se documenta: con las salidas archivadas de §3.4, no con una foto.
- **Capturas de interfaces de competidores generadas con IA.** Serían una representación inventada de un producto de terceros dentro de un análisis que la rúbrica exige objetivo y actualizado. Se toman de sus sitios públicos o no se incluyen.

Misma línea en A4 y A5.

---

## 7. El frente web: Nuxt 4 y `ui-ux-pro-max`

Respuesta corta: **la idea es buena y es exactamente el diferenciador del proyecto — pero no es de hoy, es de A4.**

### 7.1 El estado real de `frontend/`

```
frontend/
└── AGENTS.md          <- eso es todo
```

**Cero código.** No hay `package.json`, ni `nuxt.config.ts`, ni `app/`. Levantar Nuxt 4 + Tailwind v4 + tokens de diseño + las pantallas desde cero es trabajo de varias horas, con instalación de dependencias y lockfile de por medio.

### 7.2 Por qué hoy no

1. **La rúbrica de A3 no da un solo punto por un sitio funcionando.** Da 4 puntos por un mapa de navegación y 5 por la arquitectura. Ambos se entregan como documento.
2. **Regla de oro del proyecto**: ante conflicto de tiempo, gana el entregable UX de la semana. Faltan horas para las 23:59 y hay tres pasos de rúbrica en futuro (§2.4, §2.5, §2.6).
3. **El riesgo es asimétrico**: un Nuxt a medias no aporta nada al PDF, pero las horas que consume salen directamente de los puntos que sí están en juego.

### 7.3 Por qué sí, la semana que viene, y por qué A3 lo prepara

§2.4 del plan del proyecto ya fija el diferenciador de A4: "**Alta fidelidad en Figma + prototipo funcional en Nuxt 4**". Y el documento de A3 ya llama a su mapa de navegación "el **contrato de navegación**" para construir los prototipos. Ese contrato es literalmente el árbol de rutas:

```
app/pages/
├── index.vue                    -> Inicio / buscador unificado
├── exploracion/
│   ├── catalogo.vue             -> Catálogo temático integrado
│   ├── buscar.vue               -> Búsqueda facetada
│   └── exportaciones.vue        -> Motor de exportación
├── gobierno/
│   ├── diccionario.vue          -> Metadatos, linaje, reglas de negocio
│   └── tableros.vue             -> KPIs de calidad y riesgo
└── admin/
    ├── usuarios.vue             -> Accesos, permisos, bitácora
    └── credenciales.vue         -> Credenciales API
```

Si el card sorting de hoy mueve una etiqueta, **mueve una ruta**. Esa es la trazabilidad IA → código que casi nadie entrega, y es gratis: sale de haber hecho A3 bien.

### 7.4 Cómo encaja `ui-ux-pro-max` cuando llegue el momento

Es una skill de inteligencia de diseño (estilos, paletas, tipografía, guías de UX, stacks Vue/Tailwind). **Complementa, no sustituye**, lo que el proyecto ya tiene:

| Frente | Qué usar |
|---|---|
| Paleta, tipografía, jerarquía visual, estados de interacción | `ui-ux-pro-max` |
| Estructura Nuxt 4 (`app/`), Pinia, composables, middleware | `frontend/AGENTS.md` + `portal-frontend-components` / `portal-frontend-composables` |
| Los seis patrones UX comprometidos del portal | `portal-ux-patterns` |
| Gráficas y el caso de 1 M de puntos | `portal-echarts-dashboards` |

**En conflicto manda `frontend/AGENTS.md`** y las decisiones irrevocables del stack: Nuxt 4 con estructura `app/` (no Nuxt 3), pnpm vía Corepack, Tailwind v4 con tokens `@theme`, ECharts vía `vue-echarts`, **UI solo en español sin i18n**, sin emojis. Si la skill propone shadcn/ui, otra paleta o strings en inglés, se descarta esa parte y se conserva el criterio de diseño.

### 7.5 Arranque concreto, lunes 10-ago

Un solo bloque, antes de tocar diseño: `pnpm dlx nuxi init` con la estructura `app/`, Tailwind v4 con los tokens de color ya usados en `uxdoc.sty` (uxnavy `#1F4D78`, uxblue `#2563EB`, uxamber `#F97316`) para que el PDF y la interfaz se vean de la misma familia, y las ocho rutas de §7.3 como páginas vacías. Con el esqueleto navegable, la pre-validación sintética de A4 tiene un estímulo real en lugar de una imagen — y ahí el método de usuarios prototipo rinde el doble.

**Efecto lateral que conviene no perder de vista**: la pista de construcción está en cero y el plan del proyecto la da por arrancada desde el 30-jul. Empezar el lunes por `frontend/` también salda esa deuda.

---

## 8. Todo lo que hay que hacer

Lista completa, sin reparto por persona: **70 tareas para hoy** más 2 posteriores a la entrega, agrupadas por frente y marcadas por prioridad:

- **[P0]** — puntos de rúbrica directamente en riesgo. Si algo se cae, no es esto.
- **[P1]** — sube la calificación dentro del criterio.
- **[P2]** — pulido; se sacrifica primero.

### 8.A · Corrida del ejercicio — ruta crítica

Nada de 8.E depende de esto, pero **todo 8.B sí**. Arrancar por aquí.

| # | Tarea | Prio |
|---|---|---|
| 1 | Volcar las 35 tarjetas con su definición a `docs/entregables/datos/a3_tarjetas.csv` | P0 |
| 2 | Extraer las 8 fichas de persona de `a1_cuerpo.tex` a `datos/personas/`, **sin editarlas** | P0 |
| 3 | Correr las 8 sesiones de sort abierto con la plantilla de `portal-synthetic-users` | P0 |
| 4 | Incluir en cada sesión las tres preguntas de cierre de §3.4 (tarjeta difícil / doble ubicación / etiqueta confusa) | P0 |
| 5 | Aplicar la prueba de árbol (5 tareas) al final de cada sesión — 40 observaciones | P0 |
| 6 | Archivar la salida cruda en `datos/a3_sorts/P1.json … P8.json` | P0 |
| 7 | Normalizar todo a una tabla larga `evaluador, tarjeta, grupo, nombre_grupo, observacion` | P0 |
| 8 | Frecuencia de palabras sobre los nombres de grupo, para proponer etiquetas | P1 |

### 8.B · Figuras de datos (matplotlib)

| # | Tarea | Prio |
|---|---|---|
| 9 | Añadir `generar_matriz_similitud()` a `generar_figuras_a3.py` y generar la figura | P1 |
| 10 | Reemplazar el dendrograma inventado por `generar_dendrograma_real()` desde los datos | P0 |
| 11 | Añadir `generar_tarjetas_en_disputa()` y generar la figura | P1 |
| 12 | Poner `n = 8` y la naturaleza sintética en el pie de **cada** figura derivada de la corrida | P0 |
| 13 | Relabelar `a3_tablero_simulado.png` como instrumento aplicado, no como simulación | P1 |
| 14 | Regenerar `a3_mapa_sitio.png` solo si la corrida movió alguna etiqueta | P1 |
| 15 | Declarar en el pie de `a3_matriz_competitiva.png` que las posiciones son juicio del equipo | P2 |

### 8.C · Reescritura con resultados

| # | Tarea | Prio |
|---|---|---|
| 16 | Card sorting paso 6: "Simulación" → **"Aplicación con evaluadores prototipo"** (fecha, n, condicionamiento, modalidad) | P0 |
| 17 | Card sorting paso 7: observaciones reales por evaluador + nombres de grupo literales + referencia a las salidas archivadas | P0 |
| 18 | Card sorting paso 8: insertar matriz de similitud y dendrograma calculados | P0 |
| 19 | Card sorting paso 8: **eliminar o recalcular** los porcentajes 84 %, 85 % y 97 % | P0 |
| 20 | Card sorting paso 8: añadir la **tabla de tarjetas en disputa** (§3.5) | P1 |
| 21 | Card sorting paso 9: confirmar, ajustar o renombrar las cuatro categorías según los nombres de los evaluadores | P0 |
| 22 | Card sorting paso 10: registrar qué se cambió del instrumento y de la taxonomía tras la corrida | P1 |
| 23 | **Reescribir la `uxnota` como nota de método** con los cinco puntos de §3.9 | P0 |
| 24 | IA paso 4: tabla de resultados de la prueba de árbol, aciertos por tarea (x de 8) | P0 |
| 25 | Mapa paso 4: llenar la tabla de cambios con filas reales | P0 |
| 26 | Mapa paso 4: veredicto explícito sobre la hipótesis de "Credenciales API" | P1 |
| 27 | Ajustar `a3_05_cierre.tex`: ya no hay simulación, hay resultados | P1 |

### 8.D · Análisis competitivo

| # | Tarea | Prio |
|---|---|---|
| 28 | Renumerar los subtítulos a los 5 pasos literales de la rúbrica | P0 |
| 29 | Corregir Bloomberg: **\$31,980/año** terminal única, **\$28,320/asiento** multi-terminal, contrato mínimo 2 años, cobro trimestral | P1 |
| 30 | Corregir Bloomberg G2: **4.4/5 sobre 69 reseñas** (no 4.3 sin denominador) | P1 |
| 31 | Añadir la evidencia de reseñas: interfaz "de los 80", curva brutal, sobrecarga de información | P1 |
| 32 | Verificar y fechar las calificaciones de Power BI y Pyramid | P1 |
| 33 | Nota al pie de la matriz: distinguir **estimaciones de agregadores** de precios de fuente oficial | P1 |
| 34 | Añadir el hallazgo del **retiro de Q&A en dic-2026** y las limitaciones de Copilot | P1 |
| 35 | Ficha completa de **ThoughtSpot** (postura, mercado, precios, fortalezas, debilidades, marketing) | P1 |
| 36 | Ficha completa de **Collibra** (misma estructura) | P1 |
| 37 | Anclar ThoughtSpot a Diego/Arturo y Collibra a Roberto/Elena | P1 |
| 38 | Tabla de "otras alternativas consideradas": Purview, LSEG Workspace, Atlan | P1 |
| 39 | Clasificar cada entrada nueva con la tipología de posturas de Annacchino | P1 |
| 40 | Meter **los seis** competidores a la matriz comparativa, con las mismas dimensiones | P1 |
| 41 | Reescribir la tesis de ventaja competitiva: ninguna de las seis resuelve a la vez catálogo gobernado + linaje visible + consulta en lenguaje natural sin licencia por usuario | P1 |
| 42 | Añadir filas de redes sociales y material promocional a la tabla de fuentes (paso 2 de la rúbrica) | P1 |
| 43 | Toda cifra nueva con URL y "Consultado el 9 de agosto de 2026" | P0 |
| 44 | Capturas reales de interfaces de competidores — o decidir omitirlas (§6.3) | P2 |

### 8.E · Forma y estructura — sin dependencias, se puede hacer ya

| # | Tarea | Prio |
|---|---|---|
| 45 | Renombrar "0. Preliminares y Objetivos" → **"Introducción"** | P0 |
| 46 | Añadir párrafo de mapa de lectura en la introducción | P1 |
| 47 | Añadir la línea de continuidad A1 → A2 → A3 | P1 |
| 48 | **Declarar el método de usuarios prototipo al frente**, en la introducción | P0 |
| 49 | Corregir la fecha de portada: 5-ago → **9 de agosto de 2026** | P0 |
| 50 | Insertar `a3_wireframe_navegacion.png` en IA paso 5, con pie que lo declare bosquejo propio | P1 |
| 51 | Anclar el paso 5 del mapa: qué se prototipa, con qué tareas, en qué actividad | P2 |

### 8.F · Personas y coherencia

| # | Tarea | Prio |
|---|---|---|
| 52 | Incorporar a **Elena Ruiz y Jorge Mendieta** al documento (entran solos vía los evaluadores 7 y 8) | P1 |
| 53 | Corregir en `a3_03_arquitectura.tex`: anuncia "cuatro arquetipos" y enumera cinco nombres | P1 |
| 54 | Verificar mismo nombre y mismo rol para cada persona en las cuatro secciones | P1 |
| 55 | Cerrar la conclusión sobre personas concretas: qué supuesto de quién quedó sostenido | P1 |

### 8.G · Citas y referencias

| # | Tarea | Prio |
|---|---|---|
| 56 | Añadir las cinco entradas APA 7 de §9.2 (Annacchino, Bougie et al., Ramírez Mejía, Tullis y Wood, Velasco et al.) | P0 |
| 57 | **Citar Annacchino** donde se usan las cuatro posturas — hoy están sin atribución | P0 |
| 58 | **Citar Velasco et al.** en "mirada sistémica", "ilusión de orientación" y la estación de metro — hoy sin atribución | P0 |
| 59 | Citar Bougie et al. en la nota de método; sin esa cita el método queda sin respaldo | P0 |
| 60 | Citar Baxter et al. en el cuerpo (pasos 2, 5 y 8) y Tullis y Wood con la precisión de §3.3 | P1 |
| 61 | Citar Ramírez Mejía al abrir el análisis competitivo | P2 |

### 8.H · Palancas

| # | Tarea | Prio |
|---|---|---|
| 62 | Tabla de principios rectores de A2 aplicada a los seis competidores (§4.8) | P1 |
| 63 | Matriz rúbrica → sección al inicio del documento (§4.1) | P1 |
| 64 | Nombrar los cuatro sistemas de Morville y Rosenfeld: etiquetado y búsqueda (§4.6) | P2 |
| 65 | Trazas a A2: card sorting ↔ etapas 3–4 del journey (§4.7) y brecha de conocimiento → nodo de IA (§5 punto 4) | P2 |

### 8.I · Cierre — reservar 60 minutos completos

| # | Tarea | Prio |
|---|---|---|
| 66 | **Pasada de tiempo verbal** en las secciones 1 a 4 (§2.7) | P0 |
| 67 | **Pasada de vocabulario**: evaluadores y no participantes, conteos y no porcentajes (§3.2) | P0 |
| 68 | Recorrer el checklist de §10 | P0 |
| 69 | Compilar, revisar figuras y saltos de página | P0 |
| 70 | Exportar como `Entregable Actividad 3_equipo_8.pdf` y subir por "Entregar tarea" | P0 |

### 8.J · Después de entregar

| # | Tarea | Cuándo |
|---|---|---|
| 71 | Actualizar §22.1.b de `context/planeacion_proyecto.md` para que el compromiso escrito coincida con el método ejecutado (§1.3) | lunes 10-ago |
| 72 | Arrancar el esqueleto Nuxt 4 con las ocho rutas de §7.3 | lunes 10-ago |

### 8.K · Orden y regla de corte

```
8.A (corrida)  ->  8.B (figuras)  ->  8.C (reescritura)     <- ruta crítica
8.D, 8.E, 8.F, 8.G, 8.H                                     <- en paralelo, desde ya
                          8.I (cierre)                       <- reservar 60 min
```

Si hay que sacrificar algo, se cae en este orden: **8.H → 8.D(44) → 8.F → 8.B(15)**. Lo que nunca se sacrifica es la tarea **23** (nota de método): sin ella, los datos nuevos crean más problema del que resuelven. Y se sube a las 23:40 aunque 8.C quede a medias — un PDF completo tarde-pero-a-tiempo vale más que uno perfecto a las 00:05.

---

## 9. Referencias en APA 7

### 9.1 Hallazgo previo: el documento usa dos fuentes sin citarlas

Al cotejar el material de apoyo de la semana contra el texto escrito aparece un problema de atribución que hay que corregir hoy, y que además es una oportunidad:

**(a) Las cuatro posturas competitivas son de Annacchino.** El documento clasifica a los competidores como *Postura Defensiva*, *Persecución Oblicua*, *Alternativa Funcional* y *Sustituto Oportunista* — sin citar de dónde sale esa tipología. Sale, literalmente, de la sección **"Competitive Analysis — Structuring the Advantage"** del capítulo 3 de Annacchino (2003), que define los cuatro grupos: *Defensive Orientation*, *Direct Pursuit Orientation*, *Oblique Pursuit Orientation* y *Opportunistic Pursuit Orientation*. Incluso el término "alternativa funcional" viene de ahí: Annacchino describe la persecución oblicua como aquella que se manifiesta "developing **functional alternatives** to solving the problem, currently solved by the defensive player".

**(b) El marco entero de la sección de IA es de Velasco, Morales y Penado.** Las expresiones **"mirada sistémica"**, **"ilusión de orientación"**, la analogía de la **estación de metro** y los **"sistemas de rotulado"** —que el documento usa en `a3_00_preliminares.tex`, `a3_03_arquitectura.tex` y `a3_04_mapa.tex`— provienen del capítulo 2 de *UX Latam*. Están tomadas casi textualmente y no hay ni una cita.

Usar conceptos ajenos sin atribución es un riesgo académico real, y aquí es **innecesario**: son fuentes del propio material de apoyo del curso. Citarlas no solo repara la atribución, **fortalece las dos secciones que más pesan** (25 % cada una) al mostrar que la clasificación de competidores y la arquitectura de información se apoyan en literatura y no en criterio propio. Es la corrección de mayor retorno por minuto invertido de todo el plan.

### 9.2 Entradas nuevas

```
Annacchino, M. A. (2003). New product development: From initial idea to product
management. Elsevier.

Bougie, N., Ye, X., Marconi, G. M., y Watanabe, N. (2026). PerceptUI: LLM agents
as human-aligned synthetic users for UI/UX evaluation. arXiv.
https://arxiv.org/abs/2606.05697

Ramírez Mejía, A. I. (2023). Grocery shopping app. A guided UX case study.
Part 3: Competitive analysis and information architecture [Diapositivas].
TC4032, Experiencia del usuario y diseño de interfaces, Maestría en
Inteligencia Artificial Aplicada, ITESM.

Tullis, T., y Wood, L. (2004). How many users are enough for a card-sorting
study? Proceedings of the Usability Professionals Association Conference.

Velasco, J., Morales, L., y Penado, C. (2022). Arquitectura de la información.
En M. Del Río y F. Linares (Eds.), UX Latam: Historias sobre definición y
diseño de servicios digitales (pp. 47-63). Universidad del Pacífico.
```

Ya presente en `a3_05_cierre.tex`, **no duplicar**:

```
Baxter, K., Courage, C., y Caine, K. (2015). Understanding your users: A practical
guide to user research methods (2.ª ed.). Morgan Kaufmann.
```

### 9.3 Dos reglas de APA 7 que aquí importan

**(a) Un capítulo de un libro de autoría propia NO lleva entrada separada.** Annacchino y Baxter et al. son libros escritos por sus autores, no compilaciones. En APA 7 se referencia **el libro completo** y el capítulo se ubica en la cita del texto:

- (Annacchino, 2003, cap. 3)
- (Baxter et al., 2015, cap. 11)

Crear una entrada tipo "Annacchino, M. A. (2003). Competitive analysis: Structuring the advantage. En New product development..." sería un error de formato. La única de las tres que **sí** lleva entrada de capítulo es *UX Latam*, porque es un **libro editado**: la autoría del capítulo (Velasco, Morales y Penado) es distinta de la de los editores (Del Río y Linares), y por eso van los editores precedidos de "En" y sus iniciales delante del apellido.

**(b) La cita del texto usa "et al." desde tres autores.** Primera y todas las apariciones: (Baxter et al., 2015), (Velasco et al., 2022), (Bougie et al., 2026). Annacchino es autor único: (Annacchino, 2003).

### 9.4 Dónde citar cada una en el cuerpo

Una referencia que solo aparece en la bibliografía no defiende nada. Ubicaciones mínimas:

| Fuente | Dónde | Para sostener qué |
|---|---|---|
| Annacchino (2003, cap. 3) | `a3_01_analisis_competitivo.tex`, al introducir las posturas | La tipología de cuatro posturas competitivas y el criterio de clasificarlas en la matriz comparativa |
| Annacchino (2003, cap. 3) | `a3_01`, en Ventaja Competitiva | Que la persecución oblicua busca un área no disputada mediante alternativas funcionales — es el argumento central de Karisma Data |
| Velasco et al. (2022) | `a3_00_preliminares.tex` | "Mirada sistémica" e "ilusión de orientación", en su primera aparición |
| Velasco et al. (2022) | `a3_03_arquitectura.tex` | Que la clasificación y el rotulado en el lenguaje del usuario son el mecanismo de la orientación; y que la IA se resuelve **antes** que la interfaz |
| Velasco et al. (2022) | `a3_04_mapa.tex` | La analogía de la estación de metro, que hoy se usa sin fuente |
| Baxter et al. (2015, cap. 11) | `a3_02_card_sorting.tex`, pasos 2, 5 y 8 | Límite de 90 tarjetas, sesión piloto, y las dos técnicas de análisis (matriz de similitud y conglomerados) |
| Tullis y Wood (2004) | `a3_02`, paso 6 | El estándar de 15–20 participantes, citado vía Baxter et al. y **con la precisión de §3.3**: es referencia del orden de magnitud, no traslado de su poder estadístico a evaluadores sintéticos |
| Bougie et al. (2026) | `a3_02`, nota de método (§3.9) | El protocolo de condicionamiento por persona. **Sin esta cita el método queda sin respaldo** |
| Ramírez Mejía (2023) | `a3_01`, al abrir la sección | Que el análisis sigue el enfoque del caso guía del curso |

Un detalle de coherencia que suma: Velasco et al. (2022) sostienen que la arquitectura de información permite "enfocarse en la estructura primero y la interfaz después". Es exactamente lo que el proyecto hace al separar A3 (estructura) de A4 (alta fidelidad). Decirlo en una frase, con la cita, convierte una decisión de calendario en una decisión de método fundamentada.

---

## 10. Checklist final antes de subir

**Cobertura de los 26 pasos**

- [ ] Competitivo: los 5 pasos identificables por su subtítulo
- [ ] Card sorting: los 10 pasos con contenido propio; **6, 7 y 8 en pasado y con datos calculados**
- [ ] IA: los 5 pasos; el **4 con resultados (x de 8 por tarea)**, el **5 con figura**
- [ ] Navegación: los 6 pasos; el **4 con cambios aplicados**

**Método (lo que se juega esta entrega)**

- [ ] Nota de método con los cinco puntos de §3.9
- [ ] Vocabulario de §3.2 aplicado: cero apariciones de "participantes" o "usuarios" refiriéndose a los evaluadores
- [ ] Conteos sobre 8, no porcentajes
- [ ] Salidas crudas archivadas en `docs/entregables/datos/a3_sorts/`
- [ ] Cada figura derivada de la corrida declara `n = 8` y su naturaleza en el pie
- [ ] Ningún número heredado de la simulación anterior sobrevive sin recalcularse (84 %, 85 %, 97 %)

**Forma**

- [ ] Sección titulada literalmente **"Introducción"**
- [ ] Portada con los tres nombres y matrículas, fecha **9 de agosto de 2026**
- [ ] Archivo nombrado exactamente `Entregable Actividad 3_equipo_8.pdf`
- [ ] PDF subido por el botón "Entregar tarea"

**Integridad**

- [ ] Ninguna cifra presentada como comportamiento de usuarios reales
- [ ] Cero imágenes generadas con IA que representen evidencia de campo o interfaces de terceros
- [ ] Calificaciones de clientes con fuente y fecha de consulta

**Análisis competitivo (lo verificado hoy)**

- [ ] Bloomberg: **\$31,980 / \$28,320 por asiento**, contrato mínimo de 2 años; **G2 4.4/5 sobre 69 reseñas**
- [ ] Estimaciones de agregadores etiquetadas como tales; Power BI citado desde fuente oficial
- [ ] ThoughtSpot y Collibra con ficha completa, postura de Annacchino y **presencia en la matriz comparativa**
- [ ] Tabla de "otras alternativas consideradas" con Purview, LSEG y Atlan
- [ ] Hallazgo del retiro de Q&A (dic-2026) usado en la ventaja competitiva, con su fuente
- [ ] Toda cifra nueva con URL y "Consultado el 9 de agosto de 2026"

**Coherencia de personas** (§3.3.1)

- [ ] Fichas de A1 usadas **sin editar** como condicionamiento
- [ ] Elena Ruiz y Jorge Mendieta presentes en el documento, no solo en A1
- [ ] Cada competidor —los seis— aterriza en al menos una persona
- [ ] Mismo rol atribuido a cada persona en las cuatro secciones; "cuatro arquetipos" no enumera cinco nombres
- [ ] La conclusión cierra sobre personas concretas

**Coherencia general**

- [ ] Personas y escenarios llamados igual que en A1 y A2
- [ ] "Karisma Data" en todo el documento, sin restos de "Faro" ni "el Portal" a secas
- [ ] Sin repetir la distinción IA / mapa fuera de donde ya está resuelta
- [ ] Las cuatro categorías del card sorting, de la IA y del mapa **coinciden entre sí**
- [ ] Annacchino y Velasco et al. citados en el cuerpo, no solo en la bibliografía (§9.4)

---

## 11. Lo que se arrastra a la Actividad 4

1. **Esqueleto Nuxt 4** con las ocho rutas de §7.3, arrancado el lunes 10-ago (§7.5).
2. **Del wireframe al prototipo**: `a3_wireframe_navegacion.png` es el punto de partida de la alta fidelidad, con `ui-ux-pro-max` para el sistema visual y `portal-ux-patterns` para los seis patrones comprometidos.
3. **Segunda ronda de pre-validación sintética**, ahora sobre pantallas navegables en lugar de una imagen — con **≥1 iteración de diseño documentada** (hallazgo → cambio → versión), que es criterio de aceptación de la skill.
4. **Las etiquetas que los evaluadores rechacen hoy**: son requisitos de nomenclatura para la interfaz.
5. **Ronda cerrada de validación** del card sorting sobre la taxonomía ya ajustada.
6. **La validación humana sigue pendiente y con fecha**: prueba SUS de A5 con ≥5 participantes reales. Es el cierre del ciclo que A1–A3 dejan planteado como hipótesis, y hay que llegar a esa semana sin volver a posponerlo.
