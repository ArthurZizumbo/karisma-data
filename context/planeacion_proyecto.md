# Plan de Proyecto UX: Portal Centralizado de Datos Financieros

**Plataforma de inteligencia centralizada con navegación por revelación progresiva, catálogo semántico de datos y agente conversacional (Nuxt 4 + Apache ECharts + FastAPI + Polars + Google ADK + Gemini 3.5 Flash-Lite)**

---

**Documento:** Planeación SCRUM detallada + alineación con el curso — TC4032 Experiencia del Usuario y Diseño de Interfaces, Maestría en Inteligencia Artificial Aplicada (MNA), ITESM.
**Periodo:** 20 de julio a 23 de agosto de 2026 (5 semanas, la semana 1 ya en curso).
**Estado del documento:** plan vivo. Definido el 22-jul-2026; **actualizado el 29-jul-2026** con el cierre de la Actividad 1, la absorción de la rúbrica de la Actividad 2 (§2.3, protocolo §25.2), el estado real de las historias UX (§2.5), el estado verificado de la pista de construcción (§2.6), el método de usuarios prototipo (US-UX-01, §22.1.b), el recálculo de capacidad (§10.2.b) y la cobertura de lo comprometido en A1/A2 por el catálogo técnico (§18.1); **actualizado el 10-ago-2026** con el cierre de A2 y A3 (§2.5), la absorción de la rúbrica de A3 (§2.3.b, protocolo §25.2), el cierre de US-UX-05 y US-UX-06, la reformulación del criterio de validación con participantes (§22.1.b), el re-recálculo de capacidad al abrir S4 (§10.2.b) y el replanteo de A4 sobre prototipo web navegable (US-UX-07, §19). Las secciones marcadas ⚠️ PENDIENTE requieren decisión del equipo o rúbrica aún no publicada.
**Catálogo de historias:** 44 comprometidas — **US-001…US-036** (técnicas, numeración contigua sin huecos) + **US-UX-01…US-UX-08** (entregables del curso), cada una independiente y verificable (INVEST). Más **US-037…US-041**, derivadas de los compromisos de A1/A2 y declaradas **roadmap no comprometido** (§18.1).

### Equipo 8

| Integrante | Rol propuesto ⚠️ (ajustar en kickoff) |
|------------|----------------------------------------|
| Alexandro Mayoral Terán | **Frontend / UX Engineering Lead** — Nuxt 4, Apache ECharts, sistema de diseño, prototipos de alta fidelidad, patrones de revelación progresiva |
| Jacqueline Sarmiento Cervantes | **UX Research / Data Lead** — instrumentos de investigación, personas y journey maps, catálogo de datos, EDA con Polars, arquitectura de información |
| Arthur Jafed Zizumbo Velasco | **Platform / Agent Lead** — GCP, Docker/Terraform, FastAPI, seguridad JWT, Google ADK + Gemini 3.5 Flash-Lite, observabilidad OpenTelemetry, CI/CD |

> Los tres roles son **transversales al curso**: cada integrante entrega individualmente 2 user personas y 2 mapas de empatía en la Actividad 1, y participa en todas las actividades UX. Los roles definen quién lidera cada frente técnico, no quién trabaja solo en él.

### Capacidad del equipo

- **Capacidad:** 3 integrantes × ~12 h/semana × 5 semanas = **180 horas-persona** ≈ **75 story points** (factor 2.4 h/SP ≈ 0.5 día/SP, considerando curva de aprendizaje de Google ADK y coordinación).
- **Cómputo:** máquinas locales para desarrollo; GCP con Cloud Run scale-to-zero y capa gratuita/créditos académicos para staging y demo. No se requiere GPU propia: la inferencia es vía API de Gemini 3.5 Flash-Lite.
- **Herramientas UX:** Figma (prototipos), Google Forms (encuestas), generación de imágenes con IA para fotos de personas, Mermaid/FigJam para journey maps y sitemaps.

---

## Tabla de Contenidos

1. [Resumen Ejecutivo](#1-resumen-ejecutivo)
2. [Alineación con el Curso: las 5 Actividades](#2-alineacion-curso)
3. [Antecedentes Académicos: 10 Papers 2026](#3-antecedentes-academicos)
4. [Propuesta de Valor y Diferenciadores](#4-propuesta-de-valor)
5. [Usuarios y Estrategia de Investigación UX](#5-usuarios-investigacion)
6. [Definición del Producto Digital](#6-producto-digital)
7. [Stack Tecnológico](#7-stack-tecnologico)
8. [Arquitectura de la Solución](#8-arquitectura)
9. [Datos: Fuentes Sintéticas y Catálogo](#9-datos)
10. [Mapa de Épicas Refinado y Story Points](#10-mapa-de-epicas)
11. [EPIC UX (nuevo, transversal): Entregables del Curso](#epic-ux)
12. [EPIC 0: Infraestructura y Configuración Base](#epic-0)
13. [EPIC 1: Ingesta, Catálogo y Exportación](#epic-1)
14. [EPIC 2: Motor Analítico, Seguridad y Usuarios](#epic-2)
15. [EPIC 3: Agente Conversacional](#epic-3)
16. [EPIC 4: Frontend y Dashboards](#epic-4)
17. [EPIC 5: Observabilidad, Pruebas y Producción](#epic-5)
18. [Alcance Descartado y Cobertura de A1/A2](#consolidacion) — incluye §18.1 y las US-037…041 de roadmap
19. [Roadmap Semanal de Sprints](#19-roadmap)
20. [Gates del Calendario Completo](#20-gates)
21. [Gestión de Riesgos](#21-riesgos)
22. [Criterios de Éxito del MVP](#22-criterios)
23. [FinOps: Presupuesto de Operación](#23-finops)
24. [Checklist de Excelencia — Actividad 1](#24-checklist-a1)
25. [Pendientes, Protocolo y Registro de Rúbricas](#25-pendientes) — incluye el [registro de absorción](#25-4-registro)
26. [Avance 4: Contrato de Ejecución de S4](#26-avance-4) — **manda sobre §11–§17 durante la semana del 10 al 16 de agosto**
- [Anexo A: Instrumentos de Investigación (borrador)](#anexo-a)
- [Anexo B: Matriz de Personas y Mapas de Empatía](#anexo-b)
- [Anexo C: Familias de Preguntas del Agente](#anexo-c)
- [Anexo D: Glosario](#anexo-d)

---

## 1. Resumen Ejecutivo {#1-resumen-ejecutivo}

El **Portal Centralizado de Datos Financieros**, con nombre comercial **Karisma Data**, es una plataforma web modular que elimina la dispersión de información entre silos financieros institucionales (créditos, liquidez, derivados) mediante cuatro capacidades integradas:

1. **Espacios de trabajo por rol con revelación progresiva.** El usuario Operativo ve un buscador y validación puntual; el Analista profundiza a filtros complejos y exportación cruda; el Directivo consume tarjetas predictivas y tableros consolidados. La complejidad técnica solo aparece cuando se necesita. El acceso se controla con **autenticación JWT y autorización por roles (RBAC)**.
2. **Catálogo semántico de datos (Data Catalog).** Diccionario institucional buscable en lenguaje de negocio que responde "¿dónde vive este dato?", enriquecido con conocimiento tribal (definiciones, reglas de área, advertencias de uso) y preparado para RAG.
3. **Agente conversacional con herramientas gobernadas.** Un agente Google ADK razonando con Gemini 3.5 Flash-Lite que **no inventa cifras**: invoca endpoints FastAPI gobernados por permisos que ejecutan agregaciones Polars, con visibilidad total de cada tool call en la interfaz (patrón *Tool-Call Visibility*) y streaming SSE con botón de cancelación real.
4. **Exportación pesada sin fricción.** Descargas masivas CSV/Excel delegadas a segundo plano con `job_id`, estado consultable y enlaces firmados de Cloud Storage, sin congelar la interfaz.

### Doble naturaleza del proyecto

Este proyecto vive en dos pistas simultáneas que el plan integra explícitamente:

- **Pista UX (la calificada).** Cinco actividades del curso TC4032: definición de producto y usuarios (A1, dom 26-jul), escenarios y journey maps (A2), análisis competitivo y arquitectura de información (A3), interfaces de alta fidelidad (A4) y entrega final (A5). **Esta pista manda:** cada sprint cierra primero el entregable UX de la semana.
- **Pista de construcción (la que da ventaja).** Los EPICs técnicos 0–5 producen un prototipo funcional real (Nuxt 4 + FastAPI + agente) que eleva la calidad de las evidencias UX: capturas reales para A3/A4, pruebas de usabilidad sobre producto vivo para A5, y un diferenciador frente a equipos que solo entregan mockups.

### Método central: diseño centrado en el usuario con evidencia

El hilo conductor metodológico es el proceso UX completo: diseño de instrumentos propios (encuesta, entrevista semiestructurada, observación contextual) y caracterización de **usuarios prototipo** con el conocimiento de dominio del equipo → personas y mapas de empatía → escenarios y journey maps → arquitectura de información validada con card sorting → prototipos de alta fidelidad → evaluación de usabilidad con usuarios (SUS). La validación con participantes se concentra en A3 y A5, y cada artefacto anterior declara su base (§22.1.b). La novedad 2026 que aporta el equipo: **pre-validación con usuarios sintéticos condicionados por persona** (PerceptUI, §3.8) antes de las pruebas con usuarios reales, y patrones de UX para agentes (transparencia de tool calls, streaming cancelable) fundamentados en literatura CHI/arXiv 2026.

---

## 2. Alineación con el Curso: las 5 Actividades {#2-alineacion-curso}

### 2.1 Calendario de entregas (fechas confirmadas por el equipo, 22-jul-2026)

Las fechas de desarrollo quedaron confirmadas con cadencia dominical. **Tres de las cinco actividades están entregadas** (A1, A2 y A3). Las rúbricas de A4 y A5 siguen ⚠️ pendientes de publicación en Canvas; al publicarse cada una se aplica el protocolo de absorción (§25.2). Nota de calibración de peso: A1 y A2 valen 15 puntos cada una, **A3 vale 20**.

| Actividad | Tema | Fecha de entrega | Rúbrica | Sprint | Estado |
|-----------|------|------------------|---------|--------|--------|
| **A1** | Definición del producto digital y diseño de instrumentos de investigación de usuario | **dom 26-jul-2026** | **Publicada** (15 pts) | S1 | ✅ **Entregada** 26-jul (§2.5) |
| **A2** | Diseño de escenarios y Journey Maps | **dom 2-ago-2026** | **Publicada** (15 pts, absorbida 29-jul → §2.3) | S2 | ✅ **Entregada** 2-ago (§2.5) |
| **A3** | Análisis competitivo y Arquitectura de Información | **dom 9-ago-2026** | **Publicada** (20 pts, absorbida 9-ago → §2.3.b) | S3 | ✅ **Entregada** 9-ago (§2.5) |
| **A4** | Interfaces de alta fidelidad | **dom 16-ago-2026** | ⚠️ Pendiente — revisar Canvas hoy lun 10-ago (§25.2) | S4 | 🟠 **En curso**, semana en ejecución |
| A5 | Entrega final | **dom 23-ago-2026** | ⚠️ Pendiente | S5 | Por iniciar |

### 2.2 Rúbrica de la Actividad 1 (desglose exacto)

Fuente: `docs/general/semana_1/rubrica_tarea_1_UI.pdf`. Entregable: **PDF** nombrado **"Entregable Actividad 1_equipo_8"**, entrega por Canvas, cuenta para todo el Project Group.

| # | Apartado | Peso | Modalidad | Puntos (de 15) |
|---|----------|------|-----------|----------------|
| 1 | Portada con nombres de los integrantes | 2 % | Equipo | 0.30 |
| 2 | Introducción | 3 % | Equipo | 0.45 |
| 3 | Identificación de la audiencia | 5 % | Equipo | 0.75 |
| 4 | Descripción general del problema | 20 % | Equipo | 3.00 |
| 5 | Definición del producto digital | 20 % | Equipo | 3.00 |
| 6 | Dos mapas de empatía **por cada integrante** (6 en total) | 25 % | Individual | 3.75 |
| 7 | Dos user personas **por cada integrante** (6 en total) | 25 % | Individual | 3.75 |

Elementos obligatorios por sección (extraídos de las instrucciones):

- **Audiencia:** descripción de clientes y necesidades; pain points; demografía (edad, sexo, ubicación); intereses; dónde se conectan y buscan información; **herramienta utilizada para identificar la audiencia y sus resultados** (encuestas, entrevistas, redes sociales). ← Aquí entra el "diseño de instrumentos de investigación" del título de la actividad: ver Anexo A.
- **Problema:** identificación; **cuantificación (si es posible)**; impacto; solución que ofrece el producto. Nota explícita de la rúbrica: claros, concisos y **con elementos visuales** (imágenes, gráficos, cuadros).
- **Producto digital:** tipo de producto (software/plataforma web); características y beneficios.
- **Mapas de empatía:** cuatro cuadrantes etiquetados **"Says", "Thinks", "Does", "Feels"** con observaciones clave basadas en la información recopilada.
- **Personas:** foto de perfil + información básica (nombre, edad, sexo, ocupación); antecedentes (educación, situación familiar, intereses); objetivos; pain points y desafíos; comportamientos y hábitos; **frase/cita de la persona**.

La sección 24 contiene el checklist de excelencia con responsables y extras para sobrepasar la rúbrica.

### 2.3 Rúbrica de la Actividad 2 (desglose exacto — absorbida 29-jul-2026)

Fuente: `docs/general/semana_2/Rubrica/Actividad 2. Diseño de escenarios y Journey Maps.pdf`. Objetivo evaluado: **(OEA) 1.4 Definir la interacción del usuario con un producto o servicio digital a través del tiempo**. Entregable: **PDF** nombrado **"Entregable Actividad 2_equipo_8"**, entrega por Canvas, cuenta para todo el Project Group.

| # | Apartado | Peso | Modalidad | Puntos (de 15) |
|---|----------|------|-----------|----------------|
| 1 | Portada con nombres de los integrantes | 2 % | Equipo | 0.30 |
| 2 | Introducción | 3 % | Equipo | 0.45 |
| 3 | **Dos escenarios por cada integrante** (6 en total) | **45 %** | Individual | **6.75** |
| 4 | **Elaboración del Journey Map (en equipo)** | **50 %** | Equipo | **7.50** |

Elementos obligatorios por sección (extraídos de las instrucciones):

- **Cada escenario (los cuatro elementos, Sección 1 de la actividad):** definición del usuario (audiencia objetivo, necesidades y objetivos, pain points); descripción de la tarea (qué quiere conseguir y pasos para lograrlo); identificación de las interacciones clave (puntos de contacto usuario↔producto para completar la tarea); descripción del resultado deseado (resultado de la tarea **y la sensación del usuario** al completarla con éxito).
- **Journey Map de equipo (Sección 2):** cómo el usuario aborda cada etapa; sus pensamientos; los puntos que pueden complicar la adopción del producto; y las oportunidades que pueden mitigarlos. Se construye discutiendo **en equipo** los escenarios individuales y produciendo primero un **listado de actividades** que el usuario ejecuta para cumplir **uno** de los objetivos de los escenarios.
- **Herramienta:** la rúbrica **propone** Custellence (no la exige) y ofrece un ejemplo de referencia con carriles de etapas, acciones, emociones, pensamientos, puntos de contacto, pain points y oportunidades.

**Delta contra lo asumido en el plan del 22-jul (impacto de la absorción).** Los criterios provisionales de US-UX-05 asumían *3 escenarios (uno por perfil) + 3 journey maps*. La rúbrica real pide **6 escenarios (2 por integrante, 45 %)** y **un solo journey map de equipo (50 %)**. Es un cambio de forma, no de fondo: duplica el número de escenarios pero concentra medio punto de la calificación en un único mapa colaborativo. **No se congeló ningún STRETCH**: el delta se absorbió dentro de los 5 SP originales de US-UX-05 porque los escenarios comparten plantilla y los mapas comparten una única fuente de contenido. Ver el estado de cumplimiento en §2.5 y los criterios definitivos en US-UX-05.

### 2.3.b Rúbrica de la Actividad 3 (desglose exacto — absorbida 9-ago-2026)

Fuente: `docs/general/semana_3/Rubrica/`. Entregable: **PDF** nombrado **"Entregable Actividad 3_equipo_8"**, entrega por Canvas, cuenta para todo el Project Group. **Vale 20 puntos**, no 15 como A1 y A2.

| # | Apartado | Peso | Modalidad | Puntos (de 20) |
|---|----------|------|-----------|----------------|
| 1 | Portada con nombres de los integrantes | 2 % | Equipo | 0.40 |
| 2 | Introducción sobre la actividad realizada | 3 % | Equipo | 0.60 |
| 3 | Desarrollo del ejercicio de **análisis competitivo** (5 pasos) | 25 % | Equipo | 5.00 |
| 4 | Desarrollo del ejercicio de **card sorting** (10 pasos) | 25 % | Equipo | 5.00 |
| 5 | Desarrollo del ejercicio de **arquitectura de información** (5 pasos) | 25 % | Equipo | 5.00 |
| 6 | Desarrollo del ejercicio de **mapa de navegación** (6 pasos) | 20 % | Equipo | 4.00 |

**El descriptor que define la calificación.** Los cuatro criterios de desarrollo comparten la misma banda de tres niveles: *Completo* = "se incluyen **todos** los elementos solicitados"; *Parcialmente* = "se incluyen los elementos solicitados **pero puede carecer de contenido** alguno o varios"; *Incompleto* = "faltan elementos o el contenido es irrelevante". Consecuencia operativa, y es la que gobernó toda la semana 3: **la rúbrica no premia profundidad, premia cobertura demostrada de los 26 pasos numerados** (5 + 10 + 5 + 6). Un paso ausente —o presente pero redactado en futuro, sin contenido propio— baja un criterio de 25 % de "Completo" a "Parcialmente", y eso cuesta hasta 3 de los 20 puntos. De ahí la regla de trabajo que se adoptó: cada paso identificable por su subtítulo y ninguno escrito en tiempo futuro.

**Lo que la rúbrica dice sobre los participantes, y qué habilitó.** Textualmente, el equipo "puede apoyarse de usuarios potenciales, o personas cercanas que puedan sugerir un interés para el proyecto". Es permisiva en el reclutamiento y **no exige un número mínimo de participantes humanos**. Eso permitió ejecutar el card sorting con evaluadores prototipo condicionados por persona (§3.8, PerceptUI) sin salir de la banda "Completo", a condición de reportar los pasos 6, 7 y 8 en pasado y con datos calculados sobre salidas crudas archivadas. La consecuencia sobre el compromiso de validación del plan está en §22.1.b: **la validación con personas reales queda concentrada íntegramente en la prueba SUS de A5**.

**Delta contra lo asumido en el plan del 22-jul.** Los criterios provisionales de US-UX-06 pedían benchmark, sitemap, card sorting y flujos por rol. La rúbrica real añade dos exigencias que el plan no modelaba: (a) el **mapa de navegación como cuarto ejercicio con peso propio (20 %)**, separado de la arquitectura de información, y (b) la **secuencia de pasos numerados como unidad de evaluación**. No cambia el esfuerzo comprometido —siguen siendo 4 SP— sino la forma de presentarlo. **No se congeló ningún STRETCH.** El recurso de apoyo que la propia rúbrica nombra, Ramírez Mejía (2023), *Grocery shopping app, Part 3*, quedó citado en el documento.

### 2.4 Mapeo actividad → capítulos del proceso UX → épicas

| Actividad | Proceso UX | Épicas que la alimentan | Evidencia diferenciadora |
|-----------|-----------|--------------------------|--------------------------|
| A1 | Empatizar + Definir | EPIC UX (US-UX-01…04) | 8 personas y 8 mapas de empatía sobre 8 perfiles de uso; tres instrumentos diseñados con trazabilidad pregunta→hipótesis |
| A2 | Definir + Idear | EPIC UX (US-UX-05), E1 (catálogo como escenario) | 6 escenarios + 4 journey maps sobre flujos reales del portal, con taller documentado y alcance declarado |
| A3 | Idear + Estructurar | EPIC UX (US-UX-06), E1/E2 (catálogo, endpoints, roles) | Benchmark de 4–6 productos reales + sitemap y card sorting |
| A4 | Prototipar | EPIC UX (US-UX-07), E3/E4 (agente, dashboard) | Alta fidelidad en Figma **+ prototipo funcional en Nuxt 4** |
| A5 | Probar + Entregar | EPIC UX (US-UX-08), E5 (observabilidad, deploy) | Pruebas de usabilidad (SUS) + pre-validación sintética PerceptUI |

### 2.5 Estado de las entregas y de las historias UX (actualizado al 10-ago-2026)

Registro de avance real. La convención de estado de este plan es: ✅ **cerrada** (entregada y verificada contra su rúbrica) · 🔵 **terminada, pendiente de entrega** · 🟡 **abierta con desviación declarada** · ☐ **no iniciada**. Las casillas `- [ ]` dentro de cada US son tareas; el estado consolidado vive aquí.

| US | Actividad | SP | Estado | Qué se entregó realmente |
|----|-----------|----|--------|--------------------------|
| US-UX-01 | A1 | 3 | ✅ **Cubierta — método de usuarios prototipo** | Los **tres instrumentos quedaron diseñados** (encuesta de 13 preguntas, guía de entrevista semiestructurada y guía de observación contextual AEIOU), con consentimiento informado, plan de aplicación y criterios de análisis por diagramación de afinidad. Por restricción de tiempo la audiencia se caracterizó con **usuarios prototipo** en lugar de campo aplicado: investigación documental + experiencia profesional del equipo + observación de canales, declarado en el documento. Cubre lo que la rúbrica pedía ("la herramienta utilizada y sus resultados"); la meta de n≥15 era autoexigencia del equipo, no requisito de la rúbrica. |
| US-UX-02 | A1 | 3 | ✅ **Cerrada** | Portada con los 3 integrantes, introducción con método y organización, audiencia con los 6 elementos exigidos, problema cuantificado con fuente por renglón y 3 figuras, y producto digital con tipo, características y beneficios. |
| US-UX-03 | A1 | 3 | ✅ **Cerrada y excedida** | **8 personas** en lugar de 6 (Jacqueline 2, Alexandro 4, Arthur 2), todas con foto, básicos (nombre, edad, sexo, ubicación, ocupación), antecedentes, objetivos, pain points, hábitos y frase. Se añadió designación de **persona primaria** (Hartson y Pyla) y una sección de alcance y límite del método que la rúbrica no pedía. |
| US-UX-04 | A1 | 2 | ✅ **Cerrada y excedida** | **8 mapas de empatía** en lugar de 6, cuadrantes "Says/Thinks/Does/Feels" con ≥3 observaciones, plantilla uniforme y cada mapa indivisible en una sola página (corrección de la observación del profesor sobre A1). |
| US-UX-05 | A2 | 5 | ✅ **Cerrada y excedida** | **6 escenarios** (2 por integrante) con los 4 elementos de la rúbrica rotulados + **4 journey maps**: 3 individuales y el **de equipo** con taller documentado, listado de 15 actividades, 7 etapas × 7 carriles, curva emocional, trazabilidad a la característica del producto y anexo tabular. Entregada el 2-ago. |
| US-UX-06 | A3 | 4 | ✅ **Cerrada y excedida** | Los **26 pasos de la rúbrica cubiertos y visibles como subtítulo**, ninguno en tiempo futuro. Benchmark de **6 alternativas** (Bloomberg, Power BI, Pyramid Analytics, ThoughtSpot, Collibra y la práctica actual de bases aisladas + Excel + correo) con precios y calificaciones verificados con URL y fecha de consulta, matriz comparativa, cuatro dimensiones de ventaja y estrategias de mitigación. **Card sorting abierto ejecutado el 9-ago** con 8 evaluadores prototipo condicionados por las 8 personas de A1, mazo de 35 tarjetas, sesión piloto que cambió una etiqueta, salidas crudas archivadas por evaluador en `docs/entregables/datos/a3_sorts/`, matriz de similitud 35×35, dendrograma de enlace promedio y **9 conglomerados** contrastados contra las 4 categorías propuestas. Arquitectura de información de 4 categorías con jerarquía de segundo nivel y **9 facetas transversales** de etiquetado múltiple. **Prueba de árbol de 5 rutas** que confirmó 4 y **refutó 1** (el indicador de riesgo: 1 acierto de 8), con el cambio aplicado sobre el mapa antes de A4. Anexo con el registro completo del ejercicio. Entregada el 9-ago. |

**SP consumidos de la EPIC UX: 20 de 28** (11 de A1 + 5 de A2 + 4 de A3). Restan 8 SP MUST (US-UX-07 5 · US-UX-08 3) más los +4 STRETCH de US-UX-08. **La pista calificada va completa y en tiempo: 3 de 5 actividades entregadas, las tres por encima de la banda "Completo" de su rúbrica.**

**Las desviaciones que arrastran consecuencias, y qué las cierra (actualizado 10-ago):**

1. **El método fue usuarios prototipo, no trabajo de campo aplicado.** Decisión tomada por restricción de tiempo en la semana 1 y registrada aquí el 29-jul: los instrumentos se diseñaron completos y la audiencia se caracterizó con el conocimiento de dominio del equipo, la investigación documental y la observación de canales. Los criterios de campo de US-UX-03/US-UX-04 se reformularon en consecuencia, y el journey map de A2 se declara *mapa de supuestos* siguiendo la advertencia de la propia literatura de journey mapping. **Es un método legítimo y los dos documentos lo declaran, así que no hay deuda oculta**: lo que hay es una secuencia de validación pendiente, y está donde el plan ya la tenía prevista — el card sorting de A3 y la prueba SUS de A5 (≥5 participantes, exigida por la rúbrica de A5). **Actualización 10-ago: el card sorting de A3 se ejecutó con 8 evaluadores prototipo condicionados por persona, no con participantes humanos.** La rúbrica de A3 no los exigía (§2.3.b) y el documento declara el método sin ambigüedad, así que la banda no se pierde; lo que cambia es la aritmética de la validación: **de dos ventanas previstas queda una sola**, la prueba SUS de A5, y por eso deja de ser negociable (§22.1.b). La única línea que no se cruza es presentar los supuestos como hallazgos, y ambos entregables la respetan. Nota de calibración: la meta de n≥15 respuestas era una **autoexigencia del equipo**, no un requisito de la rúbrica, y quedaba desproporcionada frente a lo que A1 pedía (6 personas y 6 mapas); se entregaron 8 de cada uno.
2. **El alcance de perfiles creció de 3 a 8.** *(ver también §5.3, ya actualizada)* El plan modela consistentemente 3 perfiles (Operativo, Analista, Directivo) y los documentos entregados trabajan con **8 perfiles de uso** y 4 roles de control de acceso. Los 4 roles RBAC de US-016 no cambian, así que **la pista técnica no se ve afectada**; lo que cambia es el material de las actividades siguientes: el sitemap de A3 y las pantallas de A4 deben cubrir 8 perfiles agrupados en 4 espacios de trabajo, no 3. Esto ya está reflejado en los criterios de US-UX-06 y US-UX-07. **Cerrado el 9-ago:** la arquitectura de información de A3 resolvió los 8 perfiles en 4 categorías de primer nivel —Inicio, Exploración y extracción, Gobierno del dato, Administración— y el mapa de navegación con su corrección aplicada es el contrato que heredan las pantallas de A4.
3. **La pista de construcción sigue en cero al abrir S4 (§2.6), y eso cambia lo que A4 puede prometer.** Los criterios de US-UX-07 se escribieron asumiendo un prototipo Nuxt corriendo del que salieran capturas reales para la tabla de paridad y para la pre-validación sintética. Ese prototipo no existe. La decisión del 10-ago es no fingir paridad: A4 se construye como **prototipo web navegable de alta fidelidad** —interfaces explorables derivadas de la arquitectura ya validada en A3— y la tabla del documento declara con exactitud qué es diseño navegable y qué está conectado a datos reales. Ver US-UX-07 y §19 (S4).

### 2.6 Estado de la pista de construcción (verificado al 10-ago-2026)

Verificación directa del repositorio, no estimación. **Las 36 historias técnicas están sin iniciar: 0 SP de 58 MUST.** Las seis carpetas de producto contienen únicamente su `AGENTS.md`.

> **Re-verificado el 10-ago-2026 al abrir S4: sin cambios.** `backend/`, `frontend/`, `ml/` y `db/` contienen solo su `AGENTS.md`; `infra/` y `data/` están vacías; no existen `Makefile`, `docker-compose.yml`, `.env.example`, `backend/pyproject.toml`, `frontend/package.json` ni `.github/workflows/`. Los 11 SP técnicos de S2 y los 16 de S3 tampoco se ejecutaron. **Es el tercer sprint consecutivo en el que la pista UX cumple y la de construcción no arranca**, y a dos semanas del cierre ya no es un retraso recuperable dentro del curso: ver el re-recálculo de §10.2.b y la consecuencia sobre A4 en US-UX-07. Lo que sí creció en el mismo periodo es la cadena de análisis reproducible: `docs/entregables/analisis_a3.py` (matriz de similitud, dendrograma y prueba de árbol), `generar_figuras_a3.py`, `generar_anexo_a3.py` y las salidas crudas del card sorting en `datos/a3_sorts/`. Es código real, versionado y auditable — no es código de producto, pero sí es evidencia de método.

| Épica | US | SP MUST | Estado | Verificación |
|-------|----|---------|--------|--------------|
| **E0** Infraestructura | US-001…005 | 6 | ☐ **0 %** | No existen `Makefile`, `docker-compose.yml`, `.env.example`, `backend/pyproject.toml`, `frontend/package.json`, `backend/Dockerfile`, `frontend/Dockerfile` ni `.github/workflows/` |
| **E1** Ingesta y catálogo | US-006…009 | 10 | ☐ **0 %** | `ml/` y `data/` vacíos; no hay `db/migrations/` ni `db/schema.sql` |
| **E2** Motor y seguridad | US-011…019 | 13 | ☐ **0 %** | `backend/` vacío |
| **E3** Agente | US-020…024 | 11 | ☐ **0 %** | Sin `ml/agent/`. El gate "hello tool" de ADK sigue sin ejecutarse |
| **E4** Frontend | US-025…029 | 9 | ☐ **0 %** | `frontend/` vacío |
| **E5** Observabilidad y producción | US-030…034 | 9 | ☐ **0 %** | `infra/` vacío |

**Lo único construido hasta ahora es la cadena documental y de artefactos UX**, que sí es sustancial y reutilizable: el sistema de diseño LaTeX (`docs/entregables/estilo/uxdoc.sty`, 20 componentes), los generadores de figuras en Python con seaborn y matplotlib, el pipeline de journey maps en HTML+CSS con fuente única de contenido (`figuras/journey_data.py`), y las 14 imágenes de personas y escenas. Nada de eso es código de producto, pero la paleta y la tipografía del sistema de diseño **son la fuente de los tokens de Tailwind v4** que pedirá US-UX-07, así que el trabajo no se duplica.

**Herramientas locales verificadas:** Docker 29.5.3, Python 3.12.6, Poetry 2.2.1, pnpm 11.8.0, Node 25.2.1, dbmate 2.32.0, Terraform 1.12.2, gcloud 573. **Faltan dos:** `gitleaks` (sin él el secrets-scan de `make check` no corre y es gate obligatorio de PR) y `corepack` en PATH con Node 25 — además Node 25 no es LTS, así que conviene fijar **Node 22 LTS** en `frontend/Dockerfile` para que las tres máquinas coincidan.

**Consecuencia inmediata:** el primer entregable técnico no es una funcionalidad sino el propio `Makefile`. Los comandos `make dev`, `make data`, `make db-up` y `make check` que `CLAUDE.md` documenta son **contrato, todavía no código**. Arranque el jue 30-jul con US-001 (§19, cola de S2).

---

## 3. Antecedentes Académicos: 10 Papers 2026 {#3-antecedentes-academicos}

Diez artículos científicos de 2026 (arXiv) delimitan el espacio conceptual del proyecto. Todos están descargados en `docs/papers/` con el prefijo numérico que se usa aquí. Se organizan en tres familias: **(a)** acceso conversacional a datos empresariales (§3.1–3.5), **(b)** experiencia de usuario de sistemas agénticos (§3.6–3.9) y **(c)** infraestructura de latencia (§3.10).

### 3.1 Paper 1 — Insight Agents: An LLM-Based Multi-Agent System for Data Insights

**Cita:** J. Bai, Z. Zhang, J. Zhang y Z. Zhu, "Insight Agents: An LLM-Based Multi-Agent System for Data Insights", arXiv:2601.20048, ene-2026. Archivo: `01_insight-agents-multiagent-data-insights_arxiv-2601.20048.pdf`.

**Aporte nuclear.** Sistema conversacional multi-agente de insights de datos desplegado en producción (vendedores de Amazon US) con paradigma *plan-and-execute*: un **agente manager** (detección out-of-domain con encoder-decoder ligero + ruteo con clasificador BERT, optimizando exactitud y latencia) coordina dos **agentes worker** (presentación de datos y generación de insights). La planeación estratégica descompone la consulta en componentes granulares sobre un modelo de datos basado en APIs, con inyección dinámica de conocimiento de dominio. Resultados en producción: 90 % de exactitud en evaluación humana, latencia P90 < 15 s.

**Aplicación en el proyecto.** Es el patrón arquitectónico de referencia del **EPIC 3 (US-020)**: jerarquía manager→workers para separar ruteo barato (¿es consulta de catálogo, de datos o fuera de dominio?) del razonamiento caro, controlando latencia y costo con Gemini 3.5 Flash-Lite. Sus métricas de producción (90 % accuracy humana, P90 15 s) se adoptan como referencia para los criterios de éxito (§22). La descomposición granular sobre APIs valida el diseño "el agente consulta endpoints, no bases crudas".

### 3.2 Paper 2 — Arming Data Agents with Tribal Knowledge (Tk-Boost)

**Cita:** S. Agarwal, A. Biswal, S. Zeighami, A. Cheung, J. Gonzalez y A. G. Parameswaran (UC Berkeley), "Arming Data Agents with Tribal Knowledge", arXiv:2602.13521, feb-2026. Archivo: `02_arming-data-agents-tribal-knowledge_arxiv-2602.13521.pdf`.

**Aporte nuclear.** Framework *bolt-on* que aumenta cualquier agente NL2SQL con **conocimiento tribal**: conocimiento que corrige las *misconceptions* del agente sobre los datos (intención real de cada columna, convenciones del área), acumulado por experiencia. Tk-Boost hace que el agente responda consultas de calibración, analiza sus errores, genera conocimiento correctivo y lo indexa con **condiciones de aplicabilidad**; al responder consultas nuevas recupera ese conocimiento como retroalimentación. Mejora hasta +16.9 % en Spider 2.0 y +13.7 % en BIRD.

**Aplicación en el proyecto.** Fundamenta el diseño del **catálogo semántico (US-008)**: el diccionario de datos no documenta solo "qué es cada tabla" sino las reglas tribales de cada silo ("la fecha de liquidez es T+1", "el ID de cliente en créditos lleva prefijo"). El **análisis de casos de falla (US-036)** adopta su ciclo experiencia→misconception→conocimiento como mecanismo de mejora continua del agente. Ataca directamente el pain point "silos de conocimiento" del planteamiento.

### 3.3 Paper 3 — Beyond Text-to-SQL: An Agentic LLM System for Governed Enterprise Analytics APIs

**Cita:** G. Singh, P. Kavehzadeh, J. Xia, X.-Y. Fu, J. Bouvier Tremblay, M. T. R. Laskar, V. Lum y S. Bhushan TN, "Beyond Text-to-SQL: An Agentic LLM System for Governed Enterprise Analytics APIs", arXiv:2605.21027, may-2026. Archivo: `03_beyond-text-to-sql-governed-enterprise-analytics_arxiv-2605.21027.pdf`.

**Aporte nuclear.** Argumenta que en entornos empresariales el Text-to-SQL directo sobre bases crudas introduce riesgos de confiabilidad y cumplimiento: los pipelines analíticos reales dependen de **APIs gobernadas** que encapsulan lógica de negocio para garantizar consistencia, auditabilidad y seguridad. Presenta *Analytic Agent*, que traduce intenciones en lenguaje natural a interacciones seguras con APIs analíticas: interpreta la meta, **valida permisos**, ejecuta consultas gobernadas y genera visualizaciones conformes, evaluado en 90 casos de uso empresariales reales.

**Aplicación en el proyecto.** Es la justificación académica de la decisión de arquitectura más importante del backend: **el agente ADK solo invoca herramientas que envuelven endpoints FastAPI gobernados por roles** (Operativo/Analista/Directivo, implementados con JWT + scopes en US-015/US-016), nunca SQL/Polars arbitrario (US-020/US-021). La delegación de agregaciones matemáticas a Polars —no al LLM— sigue su principio de no confiar cálculos al modelo. Alinea el módulo de permisos del portal con auditabilidad institucional financiera.

### 3.4 Paper 4 — A Semantic-Layer-Mediated Agent for NL2SQL over Heterogeneous Enterprise Databases

**Cita:** H. J. Kim, S. Khoeurn y Y. J. Yoon, "A Semantic-Layer-Mediated Agent for Natural Language to SQL over Heterogeneous Enterprise Databases", arXiv:2606.31041, jun-2026. Archivo: `04_semantic-layer-agent-nl2sql-enterprise_arxiv-2606.31041.pdf`.

**Aporte nuclear.** Interpone una **capa semántica curada** entre el LLM y las bases: el agente razona sobre una representación intermedia compacta (*Semantic Model Query*, SMQ) y un **compilador determinístico** traduce cada SMQ a SQL específico del dialecto (SQLite, BigQuery, Snowflake), dándole al agente bloques verificados que compone en un bucle *think-act* restringido. Con Gemini 3 Pro logra 94.15 % de exactitud de ejecución en Spider2-snow (3.º del leaderboard), muy por encima de enfoques schema-only. Discute el trade-off grounding vs. overfitting de la capa semántica.

**Aplicación en el proyecto.** Refina el **motor analítico (US-011/US-012)**: el catálogo del portal actúa como capa semántica (métricas y dimensiones financieras curadas) y las "consultas" del agente se expresan contra esa capa, compilándose determinísticamente a operaciones Polars parametrizadas. El LLM nunca redacta código Polars libre: compone consultas válidas por construcción. Esto reduce alucinación de columnas inexistentes en esquemas financieros crípticos y hace el sistema portable entre fuentes heterogéneas (el problema núcleo de la "dispersión de información").

### 3.5 Paper 5 — Don't Retrieve, Navigate (Corpus2Skill)

**Cita:** Y. Sun, P. Wei y L. B. Hsieh, "Don't Retrieve, Navigate: Distilling Enterprise Knowledge into Navigable Agent Skills for QA and RAG", arXiv:2604.14572, abr-2026. Archivo: `05_dont-retrieve-navigate-enterprise-rag_arxiv-2604.14572.pdf`.

**Aporte nuclear.** Destila offline un corpus documental en un **directorio jerárquico de habilidades** que el agente navega en tiempo de servicio: desciende de una vista panorámica por resúmenes progresivamente más finos hasta los documentos, con backtracking. Mejora calidad y grounding sobre baselines densos, híbridos y RAG agéntico. Hallazgo crítico del estudio de generalización: la navegación **no** sustituye universalmente al retrieval — gana en corpus mono-dominio con taxonomía recuperable, pero **el retrieval plano sigue siendo preferible en corpus tabulares homogéneos** o factoides de dominio abierto.

**Aplicación en el proyecto.** Dicta la **estrategia RAG bifurcada** del catálogo (US-008 catálogo; US-012 híbrida plana; US-013 jerarquía navegable): (a) para manuales financieros y reglas de negocio (corpus con taxonomía natural) se planifica jerarquía navegable tipo Corpus2Skill (US-013); (b) para el diccionario tabular de campos y métricas se usa búsqueda híbrida plana (keywords + embeddings), exactamente el caso donde el paper demuestra que la jerarquía pierde. Su hallazgo también es el argumento para mantener el baseline híbrido (US-012) como comparador obligatorio, no como código desechable. Nótese el paralelo conceptual: la jerarquía de navegación es "revelación progresiva para el agente", el mismo patrón que la UI ofrece al humano.

### 3.6 Paper 6 — TwinBI: An Agentic Digital Twin for BI Dashboards

**Cita:** J. Jang y W.-S. Li, "TwinBI: An Agentic Digital Twin for Efficient Augmented Interactions with Business Intelligence Dashboards", arXiv:2606.13731, jun-2026. Archivo: `06_twinbi-agentic-digital-twin-bi-dashboards_arxiv-2606.13731.pdf`.

**Aporte nuclear.** Identifica el problema de **desincronización entre dashboard y asistente LLM** durante análisis multi-paso: al alternar entre manipulación directa (filtros, jerarquías, métricas) y consultas en lenguaje natural se pierde el estado analítico compartido. TwinBI acopla el agente a un **estado ejecutable del dashboard** reconstruido desde un log unificado de interacción, con grounding semántico, tracking de procedencia y artefactos expuestos (vistas de esquema, SQL, comando `/insights`). En A/B con el mismo agente backbone: exactitud exact-match 43.3 %→63.3 %, timeouts 40 %→10 %; el estudio de usabilidad reporta alta exactitud de tarea y carga de trabajo moderada.

**Aplicación en el proyecto.** Refina el **EPIC 4 (US-025/US-029)**: el chat del agente y el dashboard ECharts comparten estado — los filtros activos del dashboard viajan como contexto en cada consulta al agente, y las respuestas del agente pueden mutar el estado del dashboard (drill-down). El comando `/insights` inspira una acción rápida "Resumir vista actual" para el perfil Directivo. Su evidencia (+20 pts de exactitud por dar contexto de estado) justifica el costo de implementar el log unificado de interacción.

### 3.7 Paper 7 — "So There's a Catch-22 Here": Transparencia en Sistemas Multi-Agente LLM

**Cita:** S. Naik, S. Passi, M. Vorvoreanu, S. Saponas y A. Hall (Microsoft), ""So There's a Catch-22 Here": How Early Adopters Who Build Multi-Agent LLM Systems Conceptualize Transparency", arXiv:2606.08323, jun-2026. Archivo: `07_catch22-multiagent-llm-transparency_arxiv-2606.08323.pdf`.

**Aporte nuclear.** Primer estudio empírico (13 entrevistas semiestructuradas, análisis temático) de cómo los early adopters constructores/usuarios de sistemas multi-agente entienden y practican la transparencia. Los participantes articulan encuadres divergentes pero complementarios — reproducibilidad, debugging, delimitación de fronteras, visualización y auditoría — sintetizados en un **marco multidimensional con tres focos: desarrollador, usuario y gobernanza**, posicionando la transparencia como práctica socio-técnica situada.

**Aplicación en el proyecto.** Es la base conceptual del patrón **Tool-Call Visibility (US-028)** y de los *Explainable AI Overlays* (linaje de datos, US-029). El marco de tres focos estructura los requisitos: para el **usuario** (tarjetas "Consultando base de créditos…", estado de ejecución, resultado antes del texto), para el **desarrollador** (trazas OpenTelemetry, US-005/US-030) y para la **gobernanza** (hash de prompts, auditoría de tool calls, US-031). También aporta lenguaje para el reporte de A4/A5: la transparencia no es un toggle sino decisiones de diseño por audiencia.

### 3.8 Paper 8 — PerceptUI: LLM Agents as Human-Aligned Synthetic Users for UI/UX Evaluation

**Cita:** N. Bougie, X. Ye, G. M. Marconi y N. Watanabe, "PerceptUI: LLM Agents as Human-Aligned Synthetic Users for UI/UX Evaluation", arXiv:2606.05697, jun-2026. Archivo: `08_perceptui-llm-synthetic-users-uiux-eval_arxiv-2606.05697.pdf`.

**Aporte nuclear.** Framework de evaluación UI/UX **condicionada por persona**: predice cómo respondería un usuario específico a preguntas sobre una interfaz, con racionales en lenguaje natural. Entrenado en dos etapas (fine-tuning por reflexión contrastiva destilando racionales de decisiones humanas + evolución reflexiva de prompts desde trazas de fallo propias). Logra realismo a nivel humano, generaliza a preguntas y personas no vistas y reproduce distribuciones de respuesta a nivel de población — atacando el costo/lentitud de reclutar participantes en iteración temprana.

**Aplicación en el proyecto.** Aporta el **diferenciador metodológico de la pista UX**: las 6 personas de la Actividad 1 se reutilizan como *condicionamiento* de evaluadores sintéticos para pre-validar wireframes (A3) y prototipos de alta fidelidad (A4) antes de las pruebas con usuarios reales de A5 — más iteraciones de diseño dentro de las 5 semanas. Metodológicamente honesto: se reporta como *pre-validación* complementaria (con sus sesgos declarados), nunca como sustituto de la prueba con humanos que pida la rúbrica.

### 3.9 Paper 9 — Efficient Personalization of Generative User Interfaces

**Cita:** Y.-H. Peng, S. Das, J. P. Bigham y J. Wu (CMU), "Efficient Personalization of Generative User Interfaces", arXiv:2604.09876, abr-2026. Archivo: `09_efficient-personalization-generative-ui_arxiv-2604.09876.pdf`.

**Aporte nuclear.** Con un dataset de 20 diseñadores × juicios pareados sobre 600 UIs generadas, demuestra **desacuerdo sustancial entre diseñadores** (kappa promedio 0.25): aun apelando a los mismos conceptos (jerarquía, limpieza), difieren en cómo los definen y priorizan. Propone un método de personalización *sample-efficient* que representa a un usuario nuevo en términos de diseñadores previos en lugar de una rúbrica fija de conceptos; supera a evaluadores UI preentrenados y a modelos multimodales mayores, y produce interfaces preferidas por 12 diseñadores nuevos.

**Aplicación en el proyecto.** Fundamento empírico de los **espacios de trabajo personalizables (US-027 y dashboard configurable)**: si ni los expertos comparten una definición única de "buen layout" (kappa 0.25), un portal multi-perfil no debe imponer una vista única — debe partir de defaults por rol y permitir reordenar/ocultar módulos con elicitación ligera de preferencias. También informa el sistema de diseño de A4: documentar decisiones por perfil en lugar de buscar "la" interfaz universal.

### 3.10 Paper 10 — Stream2LLM: Overlap Context Streaming and Prefill for Reduced TTFT

**Cita:** R. Bachkaniwala, C. Luo, R. So, D. Mahajan y K. Rong, "Stream2LLM: Overlap Context Streaming and Prefill for Reduced Time-to-First-Token (TTFT)", arXiv:2604.16395, mar-2026. Archivo: `10_stream2llm-context-streaming-ttft_arxiv-2604.16395.pdf`.

**Aporte nuclear.** Identifica la tensión fundamental de los sistemas con recuperación de contexto: esperar el contexto completo arruina el TTFT; proceder sin él degrada calidad. Propone *streaming* incremental de contexto **solapando recuperación con prefill**, con scheduling adaptativo y preempción para dos patrones (append-mode y update-mode), matching de prefijo común más largo para minimizar recómputo, y modelos de costo por hardware. Logra mejoras de TTFT de hasta 11× manteniendo throughput.

**Aplicación en el proyecto.** Marco conceptual del **presupuesto de latencia del chat (US-023, US-034)**: el objetivo TTFT < 700 ms se descompone en (recuperación de catálogo ∥ preparación del prompt) en lugar de secuencial — mientras el tool call de datos corre, el stream ya emite el encabezado de la respuesta y la tarjeta de tool call (percepción de progreso). No implementaremos serving propio (usamos la API de Gemini), pero el principio "solapar recuperación con generación" y la medición TTFT/throughput por percentiles estructuran los criterios de aceptación y las pruebas de latencia de la semana 5.

### 3.11 Tabla de mapeo papers → épicas y actividades

| # | Paper (arXiv) | Épica/US principal | Actividad UX beneficiada |
|---|---------------|--------------------|--------------------------|
| 1 | Insight Agents (2601.20048) | E3 US-020 (arquitectura manager/workers) | A4 (chat), A5 (métricas) |
| 2 | Tribal Knowledge (2602.13521) | E1 US-008 (catálogo); US-036 (casos de falla) | A2 (escenarios de descubrimiento) |
| 3 | Governed Analytics APIs (2605.21027) | E3 US-021 + E2 US-016 (tools gobernadas, permisos) | A3 (IA por roles), A5 (seguridad) |
| 4 | Semantic Layer SMQ (2606.31041) | E2 US-011 (capa semántica + compilación) | A3 (arquitectura de información) |
| 5 | Corpus2Skill (2604.14572) | E1/E2 US-008/012/013 (RAG bifurcado) | A3 (taxonomía del catálogo) |
| 6 | TwinBI (2606.13731) | E4 US-025/029 (estado compartido dashboard↔chat) | A4 (alta fidelidad del dashboard) |
| 7 | Catch-22 Transparency (2606.08323) | E4 US-028; E5 US-031 (tool-call visibility, auditoría) | A4/A5 (patrones de confianza) |
| 8 | PerceptUI (2606.05697) | EPIC UX US-UX-07/08 (pre-validación sintética) | A1 (personas), A4, A5 |
| 9 | Generative UI Personalization (2604.09876) | E4 US-027 (workspaces por rol) | A3/A4 (defaults por perfil) |
| 10 | Stream2LLM (2604.16395) | E3 US-023; E5 US-034 (TTFT, streaming) | A4 (percepción de velocidad), A5 |

---

## 4. Propuesta de Valor y Diferenciadores {#4-propuesta-de-valor}

### 4.1 Posicionamiento frente a alternativas actuales

| Categoría | Statu quo institucional (silos + Excel + correos) | BI tradicional (Power BI/Tableau genérico) | **Portal Centralizado de Datos** |
|-----------|---------------------------------------------------|--------------------------------------------|----------------------------------|
| Acceso a fuentes | Cada área su base; cruces manuales | Conectores, pero modelado por TI centralizado | Conectores asíncronos + catálogo institucional unificado |
| Descubrimiento de datos | Conocimiento tribal no documentado | Catálogo limitado al workspace | **Data Catalog semántico con conocimiento tribal y búsqueda en lenguaje de negocio** |
| Modos de uso | Un solo flujo pesado para todo | Dashboards fijos por reporte | **Revelación progresiva: consulta rápida ↔ análisis profundo ↔ vista directiva** |
| Control de acceso | Carpetas compartidas sin gobierno | Licencias/grupos AD | **JWT + RBAC por perfil (Operativo/Analista/Directivo/Admin) con CRUD de usuarios** |
| Lenguaje natural | No | Q&A básico, caja negra | **Agente ADK con tool-calling gobernado y visibilidad de herramientas** |
| Exportación pesada | Congela la máquina / ticket a TI | Límites de filas, exportes lentos | **Jobs en segundo plano + enlaces firmados (CSV/Excel/API)** |
| Confianza en la IA | N/A | Respuestas sin linaje | **Tool-Call Visibility + linaje de datos + botón Stop real** |
| Latencia percibida | Días (tickets) | Minutos (cargas) | **Streaming SSE, TTFT objetivo < 700 ms** |
| Costo de operación | Horas-persona invisibles | Licencias por usuario | **Serverless scale-to-zero + modelo flash-lite de bajo costo por token** |

### 4.2 Diferenciadores concretos (defendibles en la entrega final)

1. **Trípode de perfiles con un solo producto.** Operativo, Analista y Directivo no son tres apps: son tres niveles de revelación del mismo sistema, y los modos coexisten en una misma persona según la tarea — hipótesis central del proyecto, sustentada en la experiencia profesional del equipo y con su pregunta verificadora en el instrumento (E-08). A1 la desarrolló en 8 perfiles de uso agrupados en 4 roles de acceso.
2. **El agente no calcula: orquesta.** Cifras siempre provenientes de Polars vía endpoints gobernados con permisos JWT (papers §3.3, §3.4) — defendible ante auditoría financiera.
3. **Transparencia como requisito, no adorno.** Patrones tool-call visibility y overlays de linaje fundamentados en el marco empírico de §3.7.
4. **UX medida, no supuesta.** TTFT y P90 con OpenTelemetry; pre-validación sintética por personas (§3.8) + SUS con usuarios reales en A5.
5. **Stack 2026 de bajo costo.** Nuxt 4 (shallowRef, Lazy, SWR) + ECharts para millones de puntos + Gemini 3.5 Flash-Lite (rápido y económico para alto volumen) + Cloud Run scale-to-zero.

---

## 5. Usuarios y Estrategia de Investigación UX {#5-usuarios-investigacion}

### 5.1 Perfiles de la audiencia

> **Actualizado el 29-jul.** El plan del 22-jul modelaba **tres** perfiles. A1 los desarrolló en **ocho perfiles de uso** —consulta operativa, análisis de datos, gobierno y calidad, control y auditoría, habilitación técnica, supervisión directiva, administración de la plataforma e integración de aplicaciones—, cada uno con su persona y su mapa de empatía. Los tres de la tabla siguen siendo los **modos de trabajo dominantes** que gobiernan la revelación progresiva del producto, y los ocho perfiles se agrupan en los **cuatro roles de control de acceso** que implementa US-016. Distinción que conviene no perder: los perfiles son categorías de investigación, los roles son permisos.

Los modos **no son excluyentes**: una misma persona cambia de modo según la tarea (hipótesis central del proyecto, con su pregunta verificadora E-08 en el Anexo A).

| Modo de trabajo | Necesidad dominante | Módulos principales | Métrica de éxito UX |
|--------|--------------------|--------------------|---------------------|
| **Operativo** (consulta rápida) | Validar/consultar datos puntuales con mínima fricción | Buscador global, catálogo, respuestas del agente con fuente | Tiempo a dato validado < 30 s |
| **Analista de datos** (profundidad) | Filtros complejos, cruces de variables, exportación cruda | Explorador de datos, exportación en segundo plano, APIs | Export masivo sin bloquear UI; cruce multi-fuente en < 5 min |
| **Directivo** (abstracción) | Supervisión y decisión con carga cognitiva mínima | Tarjetas predictivas, tableros consolidados, resumen del agente | Comprensión de estado global en < 1 min sin ayuda |

A nivel de sistema existe además el rol **Admin** (gestión de usuarios, US-018/019), que no es un modo de trabajo sobre el dato sino de operación del portal — en A1 corresponde a la persona de administración de la plataforma.

Demografía objetivo (a confirmar con instrumento): profesionales de banca/finanzas en México, 25–55 años, oficinas centrales y esquema híbrido; se conectan en escritorio corporativo (principal) y móvil (consulta); buscan información en intranet, Teams/Slack, correo y con colegas (el "experto de al lado" — exactamente el silo de conocimiento que el portal ataca).

### 5.2 Instrumentos de investigación (Actividad 1 exige indicarlos con resultados)

| Instrumento | Alcance | Meta original (22-jul) | Ejecución real (29-jul) | Producto |
|-------------|---------|------------------------|-------------------------|----------|
| **Encuesta estructurada** (Google Forms, ~13 preguntas, Anexo A.1) | Colegas del sector financiero/datos de la red de los 3 integrantes | n ≥ 15 respuestas antes del vie 24-jul | **Diseñada y lista para aplicar**; no se aplicó por tiempo. La meta n≥15 era autoexigencia del equipo, no requisito de la rúbrica | Instrumento citable en el documento + preguntas verificadoras enlazadas a cada supuesto |
| **Entrevistas semiestructuradas** (30 min, guion Anexo A.2) | 1 por perfil | 3 entrevistas antes del sáb 25-jul | **Guion diseñado**; aplicación diferida a las ventanas de A3/A5 | Guion citable y trazabilidad pregunta → supuesto |
| **Observación contextual** (esquema AEIOU, Anexo A.2) | Tarea real en el puesto de trabajo | No estaba en el plan original | **Diseñada** — instrumento añadido durante A1, con su regla de registro (separar lo observado de lo interpretado) | Tercer instrumento del documento |
| **Observación de canales** (LinkedIn, comunidades de datos/finanzas, foros internos) | Dónde se conectan y buscan información | Lista de canales citable | ✅ **Ejecutada** | Sustento del apartado "dónde se conectan" |
| **Investigación documental** | Costo de la mala UX en herramientas internas; prácticas de gobierno de datos | No estaba en el plan original | ✅ **Ejecutada** — sustituye la cuantificación de encuesta con fuentes públicas citadas | Cuantificación del problema con fuente por renglón |

**Método aplicado: usuarios prototipo.** La caracterización de la audiencia y las ocho personas se construyeron con investigación documental, experiencia profesional del equipo en áreas que operan con información financiera institucional, y observación de canales. Es el método de *proto-personas*: hipótesis fundamentadas y declaradas como tales, con los instrumentos listos para validarlas. Ver US-UX-01 y §22.1.b.

**Regla de honestidad metodológica** (se cumplió y sigue vigente): toda cifra del documento sale de (a) un instrumento propio aplicado, (b) una fuente pública citada y verificada, o (c) se declara como estimación del equipo. Los indicadores sin dato dicen "pendiente de medición" y enlazan a la pregunta que los levantará. No se inventan estadísticas de mercado.

### 5.3 Distribución de personas y mapas de empatía (Sección 2 de A1, individual)

El plan preveía 6 personas y 6 mapas sobre 3 perfiles × 2 variantes (ver plantillas en Anexo B). **Lo entregado el 26-jul fue mayor: 8 personas y 8 mapas sobre 8 perfiles de uso**, repartidos Jacqueline 2 · Alexandro 4 · Arthur 2. La rúbrica exigía 6 (dos por integrante), así que la cobertura quedó por encima del requisito.

| Integrante | Personas entregadas |
|------------|---------------------|
| Jacqueline | **Laura Méndez** (consulta operativa) · **Diego Hernández** (análisis de datos) |
| Alexandro | **Roberto Valdez** (gobierno y calidad) · **Elena Ruiz** (control y auditoría) · **Jorge Mendieta** (habilitación técnica) · **Arturo Castañeda** (supervisión directiva) |
| Arthur | **Mariana Ovalle** (administración de la plataforma) · **Ximena Solís** (integración de aplicaciones) |

Cada integrante hizo el mapa de empatía de sus mismas personas (consistencia narrativa persona↔mapa). Los ocho perfiles de uso se agrupan en los **4 roles de control de acceso** del producto (operativo, analista, directivo, administrador), que son los que implementa US-016: los perfiles son categorías de investigación, los roles son permisos.

---

## 6. Definición del Producto Digital {#6-producto-digital}

**Tipo:** software — plataforma web (portal modular SaaS interno institucional).

### 6.1 Módulos y beneficios

| Módulo | Descripción | Perfil primario | Beneficio |
|--------|-------------|-----------------|-----------|
| **Home por rol** | Espacio de trabajo configurable con módulos frecuentes (búsqueda, métricas, exportación) y defaults por perfil | Todos | Curva de aprendizaje mínima; complejidad solo cuando se necesita |
| **Buscador / Data Catalog** | Diccionario semántico institucional; búsqueda en lenguaje de negocio; sugerencia de fuentes relacionadas; conocimiento tribal por campo | Operativo, Analista | Una sola fuente de verdad; fin del "pregúntale a Godínez" |
| **Explorador analítico** | Filtros complejos, cruces entre fuentes (joins Polars), vistas tabulares y gráficas ECharts de alto volumen | Analista | Cruces masivos sin congelar pantalla |
| **Tarjetas predictivas + tableros** | Vista directiva con previsiones ("Riesgo de liquidez +12 % próximo mes") y drill-down progresivo | Directivo | Supervisión en 1 minuto; profundidad opcional |
| **Agente conversacional** | Chat con Gemini 3.5 Flash-Lite vía Google ADK; tool calls visibles; streaming con Stop real; linaje de datos | Todos | Preguntas complejas en lenguaje natural con respuestas auditables |
| **Exportación** | Descargas CSV/Excel en segundo plano con `job_id` y enlace firmado; acceso vía API | Analista | Extracción pesada sin fricción ni bloqueo |
| **Acceso y administración** | Login JWT, sesión por rol, panel admin de usuarios (alta/edición/desactivación, asignación de rol) | Admin (técnico) | Gobierno de acceso demostrable; base del RBAC de todo el portal |

### 6.2 Patrones UX 2026 comprometidos (con fundamento)

1. **Progressive Disclosure** — resumen → detalle → herramientas avanzadas (planteamiento del proyecto; refuerzo empírico en §3.5: hasta el agente navega jerárquicamente).
2. **Predictive Insight Cards** — previsiones calculadas en la vista principal directiva (US-026).
3. **Tool-Call Visibility + Explainable Overlays** — auditar qué base consultó la IA antes de leer su texto (§3.7, US-028/029).
4. **Streaming + Stop real** — SSE con cancelación que corta la llamada al LLM en milisegundos (US-023; presupuesto de latencia §3.10).
5. **Workspaces personalizables por rol** — defaults por perfil + reordenamiento ligero (§3.9, US-027).
6. **Estado compartido dashboard↔chat** — los filtros del dashboard son contexto del agente y viceversa (§3.6, US-025/029).

---

## 7. Stack Tecnológico {#7-stack-tecnologico}

> Filas marcadas ✔C7 fueron verificadas contra documentación oficial vigente vía Context7 el 22-jul-2026.

### 7.1 Frontend

| Componente | Tecnología | Justificación |
|------------|-----------|---------------|
| Framework | **Nuxt 4** (Vue 3, estructura `app/`) | SSR/renderizado híbrido; `shallowRef` por defecto en `useFetch` reduce hidratación con objetos masivos; HMR rápido |
| Manejador de paquetes | **pnpm** (pin con campo `packageManager` + Corepack) | Instalaciones rápidas con store global de enlaces duros; `pnpm-lock.yaml` determinístico para los 3 integrantes; capa de caché eficiente en Docker (`pnpm fetch` antes de copiar el código) |
| Visualización | **Apache ECharts** (`vue-echarts`, componentes `Lazy*`) | Millones de puntos con canvas/WebGL; lazy loading mejora Time to Interactive |
| Estrategia de render | `routeRules` con **SWR** para dashboard directivo | Cargas instantáneas con revalidación en segundo plano |
| Chat UI | Composable SSE propio + componentes de tarjetas de tool call | Control fino del patrón Tool-Call Visibility |
| Estado | Pinia | Estado compartido dashboard↔chat (patrón TwinBI) |
| Estilos | TailwindCSS v4 | Sistema de diseño consistente con tokens de A4 |
| Guardas de sesión | Middleware de rutas Nuxt + cookie httpOnly con el JWT | Redirección a login y ocultamiento de módulos según rol |

### 7.2 Backend y datos

| Componente | Tecnología | Justificación |
|------------|-----------|---------------|
| API | **FastAPI** (Python 3.12, `async def`, Pydantic v2) | Estándar 2026 para microservicios asíncronos y capas de inferencia IA |
| Manejador de dependencias | **Poetry** (lockfile `poetry.lock`, grupos dev/test) | Entornos reproducibles entre los 3 integrantes y en CI; export a `requirements.txt` para la imagen slim de producción |
| Motor analítico | **Polars 1.x** | DataFrames ultrarrápidos en memoria; joins cruzados entre silos |
| Persistencia | PostgreSQL 15 (+ **pgvector** en fase RAG) | Metadatos del catálogo, usuarios y embeddings del diccionario |
| ORM | **SQLModel** (SQLAlchemy 2 + Pydantic) | Tipado end-to-end para usuarios/catálogo; consistencia con la experiencia previa del equipo (AgroSat) |
| Migraciones | **dbmate** ✔C7 | SQL puro framework-agnóstico: `dbmate new <nombre>` genera `db/migrations/<timestamp>_<nombre>.sql` con secciones `-- migrate:up` / `-- migrate:down`; `dbmate up/rollback`; `schema.sql` versionado en git (dump vía `pg_dump`); binario Go sin dependencias, corre igual en local, CI y Cloud Build; skill ya consolidado del equipo |
| **Autenticación** | **PyJWT + pwdlib (Argon2)** ✔C7 | Recomendación vigente de la documentación oficial de FastAPI (sustituye a python-jose + passlib): tokens firmados HS256 (`SECRET_KEY` de 32 bytes en Secret Manager), hashing `PasswordHash.recommended()` (argon2id), flujo `OAuth2PasswordBearer` + endpoint `/token` |
| **Autorización** | **SecurityScopes de FastAPI** ✔C7 | Los roles (operativo/analista/directivo/admin) viajan como scopes en el claim del JWT; cada endpoint declara `Security(get_current_user, scopes=[...])` → 401 sin token, 403 sin permiso |
| Jobs pesados | BackgroundTasks (MVP) → Cloud Pub/Sub (stretch) | Exportaciones sin bloquear el event loop |
| Almacenamiento | Cloud Storage + signed URLs | Entrega segura de exportes |

### 7.3 Agente e IA

| Componente | Tecnología | Justificación |
|------------|-----------|---------------|
| Framework de agente | **Google ADK** ✔C7 | `LlmAgent(model, name, instruction, tools=[fn])` con function tools Python planas auto-descubiertas; `Runner` + `SessionService` para sesiones; tracing built-in; deploy opcional a Vertex AI Agent Engine |
| LLM | **Gemini 3.5 Flash-Lite** | El más rápido (hasta ~350 tokens/s de salida) y rentable para alto volumen/baja latencia; `thinking_level` ajustable por tipo de consulta |
| Patrón | Manager → workers (presentación / insights), presupuesto limitado de tools | §3.1; evita ciclos infinitos y controla costo |
| RAG | Búsqueda híbrida plana (diccionario) + jerarquía navegable (manuales) | Estrategia bifurcada fundamentada en §3.5 |

### 7.4 Infraestructura, MLOps y observabilidad

| Componente | Tecnología | Justificación |
|------------|-----------|---------------|
| Local reproducible | Docker Compose + Makefile (`make dev`) | 3 integrantes, mismas versiones |
| Cloud | GCP: Cloud Run (scale-to-zero), Secret Manager, Artifact Registry, GCS | FinOps académico |
| IaC | Terraform (módulo mínimo MVP; ampliación stretch) | Reproducibilidad staging/prod |
| CI/CD | GitHub Actions (+ Cloud Build para deploy) | Lint (ruff, eslint) + pytest + Vue Test Utils en cada push; deploy en merge a main; `dbmate up` como paso de migración previo al deploy |
| Observabilidad | **OpenTelemetry** en FastAPI: trace por solicitud; sub-spans `db.retrieval`, `llm.call`, `llm.postprocess`; atributos `llm.usage.*`; **hash de prompts** (privacidad) | US-005/US-030/US-031; FinOps de tokens |

### 7.5 Veredicto de suficiencia del stack

El stack declarado por el equipo **es suficiente** para el MVP; la revisión con Context7 agregó las piezas que faltaban para operarlo con disciplina: **pnpm/Poetry** (reproducibilidad de dependencias en 3 máquinas + CI), **dbmate + SQLModel** (evolución de esquema sin fricción, patrón ya dominado en AgroSat), **PyJWT + pwdlib + SecurityScopes** (auth moderna sin dependencias abandonadas — python-jose/passlib ya no son la recomendación oficial). Se evaluó y **descartó** para el MVP: fastapi-users (abstrae de más para 4 roles fijos y complica el CRUD didáctico), Alembic (duplicaría a dbmate), Redis (la caché en memoria de US-007 basta a esta escala) y Dagster (no hay pipelines ML que orquestar en este curso).

---

## 8. Arquitectura de la Solución {#8-arquitectura}

```
┌────────────────────────────── Usuario (Operativo / Analista / Directivo / Admin) ─────────────────────┐
│                                                                                                       │
│   Nuxt 4 (SSR híbrido + SWR) ── middleware auth (cookie httpOnly JWT, guardas por rol)                │
│   ├── Login / sesión                                   ├── Panel admin de usuarios (rol admin)        │
│   ├── Home por rol (workspaces configurables)          ├── Tarjetas predictivas (Directivo)           │
│   ├── Data Catalog UI (búsqueda semántica)             ├── Explorador + <LazyECharts/> (Analista)     │
│   └── Chat del agente: SSE stream ── tarjetas Tool-Call Visibility ── botón STOP (aborta socket)      │
└───────────────┬───────────────────────────────────────────────────────────────────────┬──────────────┘
                │ REST /api/*  (Bearer JWT con scopes de rol)                           │ SSE /api/chat
┌───────────────▼───────────────────────────────────────────────────────────────────────▼──────────────┐
│  FastAPI (async) ── OpenTelemetry: trace por solicitud                                                │
│  ├── /api/auth/token (OAuth2 password → JWT) ── /api/users CRUD (scope admin)                         │
│  ├── /api/catalog/search ──► Catálogo semántico (PostgreSQL + SQLModel; pgvector en fase RAG)         │
│  ├── /api/{creditos|liquidez|derivados} ──► Capa semántica → consultas Polars parametrizadas          │
│  ├── /api/export ──► BackgroundTasks/PubSub ──► worker Polars ──► GCS + signed URL (job_id)           │
│  └── /api/chat ──► Agente Google ADK (manager → workers)                                              │
│                     │ tool calls gobernadas (propagan el JWT del usuario; presupuesto de tools)       │
│                     ▼                                                                                 │
│                Gemini 3.5 Flash-Lite (streaming; cancelación al desconectar cliente)                  │
│  spans: db.retrieval / llm.call {usage.tokens, model, prompt_hash} / llm.postprocess                  │
│  esquema: migraciones dbmate (db/migrations/*.sql, schema.sql versionado)                             │
└──────────────────────────────────────────────────────────────────────────────────────────────────────┘
   Silos origen (sintéticos en MVP): créditos.parquet │ liquidez.parquet │ derivados.parquet │ manuales/
```

### 8.1 Flujos principales

1. **Acceso.** Login → `/api/auth/token` (OAuth2 password) → JWT con claims `sub` + `scope` (rol) → cookie httpOnly → el middleware de Nuxt monta el workspace del rol; toda llamada REST viaja con `Authorization: Bearer`.
2. **Consulta rápida (Operativo).** Buscador → `/api/catalog/search` → resultado con fuente, definición y conocimiento tribal → botón "ver dato" ejecuta consulta gobernada. Sin agente si no hace falta (latencia mínima).
3. **Análisis profundo (Analista).** Explorador con filtros → cruces Polars → si el resultado supera umbral, botón "Exportar" crea job en segundo plano → notificación con enlace firmado.
4. **Pregunta al agente (los tres).** Chat → manager rutea (OOD/catálogo/datos) → tarjeta "Consultando base de liquidez…" → tool call a endpoint gobernado **con el token del usuario** (el agente nunca ve datos que el usuario no puede ver) → datos renderizados → texto en streaming → overlay de linaje. Stop aborta el socket y mata la llamada LLM.
5. **Supervisión (Directivo).** Home SWR con tarjetas predictivas → drill-down progresivo → "Resumir vista actual" (estado del dashboard como contexto del agente, patrón TwinBI).
6. **Administración (Admin).** Panel de usuarios → alta con contraseña temporal, edición de datos/rol, desactivación (soft delete) → efecto inmediato en permisos.

---

## 9. Datos: Fuentes Sintéticas y Catálogo {#9-datos}

No hay acceso a datos financieros reales de una institución (y no deben usarse): el MVP opera sobre **datasets sintéticos realistas**, lo cual además es una ventaja demo (sin NDA, publicable).

| Dataset sintético | Contenido planeado | Volumen objetivo | Uso |
|-------------------|--------------------|------------------|-----|
| `creditos` | Cartera: ID cliente, producto, saldo, mora, tasa, fechas | ~1–5 M filas | Joins con liquidez; tarjetas de riesgo |
| `liquidez` | Posiciones diarias, buckets de vencimiento, ratios (LCR-like) | ~1 M filas | Series temporales ECharts; predicciones simuladas |
| `derivados` | Operaciones: subyacente, nocional, contraparte, MtM | ~500 K filas | Cruces con créditos por contraparte |
| `catalogo` | Metadatos: tabla, campo, definición, dueño, área, sensibilidad, reglas tribales | ~200–400 entradas | Data Catalog + RAG |
| `usuarios` | Cuentas seed: 1 admin + 2 por perfil (operativo/analista/directivo) con contraseñas hasheadas Argon2 | 7 registros | Auth/RBAC (US-015…019) y pruebas de usabilidad por rol |
| `manuales/` | 3–5 documentos markdown de reglas de negocio simuladas | — | Chunking semántico (fase RAG) |

Principios: esquemas **heterogéneos a propósito** (nombres crípticos distintos por silo, para que la capa semántica tenga sentido, §3.4); generación con Polars + Faker con semilla fija (reproducible); IDs de cliente compartidos entre silos para el RAG relacional (US-014); anomalías inyectadas deliberadamente (para el perfilado EDA de US-010 y para escenarios de journey maps); el esquema relacional (usuarios, catálogo, jobs de exportación) evoluciona **solo** vía migraciones dbmate.

---

## 10. Mapa de Épicas Refinado y Story Points {#10-mapa-de-epicas}

### 10.1 Principios estructurales del plan

1. **EPIC UX transversal (28 SP)**: la calificación del curso sale de las actividades UX, así que sus entregables son historias de primera clase — el plan no optimiza lo no evaluado.
2. **Toda US etiquetada MUST / STRETCH** y redactada en formato completo (Como/quiero/para que + criterios + tareas + estimación). La suma de MUST (86 SP) excede la capacidad (75 SP): el plan declara el déficit y sus válvulas en vez de descubrirlo en la semana 4.
3. **El gobierno de acceso son historias propias** (confirmado por el equipo el 22-jul): autenticación JWT + login (**US-015**), autorización RBAC por scopes (**US-016**), guarda de sesión en frontend (**US-017**) y gestión de usuarios backend/frontend (**US-018/019**). El RBAC no es implícito: tiene criterios y SP propios.
4. **Catálogo contiguo y desagregado (INVEST).** 36 historias técnicas US-001…US-036 sin huecos + US-UX-01…08, cada una independiente, pequeña y verificable; ninguna historia empaqueta entregables de naturaleza distinta. El trabajo fuera del alcance del curso (switch A/B de LLM, drift, benchmark masivo de Q&A) se lista como **descartado explícito** en §18, no como US faltante.
5. **Los papers 2026 quedan anclados a US concretas** (tabla §3.11): cada decisión de arquitectura o patrón UX cita su fundamento.

### 10.2 Presupuesto por épica

| Épica | Descripción | SP MUST | SP STRETCH | Semana foco |
|-------|-------------|---------|------------|-------------|
| **EPIC UX** | Entregables de las 5 actividades del curso · US-UX-01…08 | **28** | +4 | S1–S5 (transversal) |
| E0 | Infraestructura, Docker, dependencias, CI/CD, OTel base · US-001…005 | **6** | +5 | S1 |
| E1 | Ingesta sintética, catálogo, exportación, EDA · US-006…010 | **10** | +4 | S1–S2 |
| E2 | Motor analítico + búsqueda + **auth JWT/RBAC + usuarios** · US-011…019 | **13** | +5 | S2–S3 |
| E3 | Agente ADK + Gemini + streaming/Stop · US-020…024 | **11** | +3 | S3–S4 |
| E4 | Frontend Nuxt 4 + ECharts + patrones UX · US-025…029 | **9** | +7 | S4 |
| E5 | Observabilidad LLM, pruebas, producción · US-030…036 | **9** | +7 | S5 |
| **Total** | 44 historias (36 técnicas + 8 UX) | **86** | **+35** | Capacidad ≈ 75 |

*(Corrección del 29-jul: el stretch de E1 son +4 SP, no +5 — US-007 +1, US-008 +1, US-010 +2 — y el total de stretch del catálogo es +35. Los MUST sí sumaban exacto: 86.)*

**Déficit declarado: −11 SP** sobre capacidad. Válvulas, en orden: (a) los STRETCH no se tocan salvo holgura real; (b) plantillas y generación asistida por IA para artefactos UX (fotos de personas, primeras iteraciones de layouts); (c) el prototipo funcional reduce el costo de A4 (capturas reales en vez de dibujar todo en Figma); (d) degradaciones acordadas de antemano: US-018/019 pueden reducirse a listado + cambio de rol + desactivación (sin formulario de edición completo), US-025 puede demostrarse con 500 K puntos pre-agregados server-side en vez de 1 M crudos. Si una rúbrica llega más pesada de lo previsto, se congela primero E5-stretch y E4-stretch.

### 10.2.b Recálculo al 29-jul-2026: el déficit real es −22 SP, no −11

El déficit de −11 SP se calculó sobre las 5 semanas completas. Al cierre de la semana 2 la aritmética cambió, porque **la pista UX va en tiempo y la pista de construcción no ha empezado**: ninguna de las 36 historias técnicas está iniciada (las carpetas `backend/`, `frontend/`, `ml/`, `db/` contienen solo su `AGENTS.md`; no existen `Makefile`, `docker-compose.yml`, `pyproject.toml`, `package.json` ni `db/migrations/`). Los gates técnicos de §20 del 23-jul, 24-jul y 30-jul están **vencidos sin cumplir**.

| Concepto | SP |
|----------|-----|
| Consumido a la fecha (UX A1 11 + A2 5) | 16 |
| Capacidad restante (cola de S2 ≈ 4 + S3 15 + S4 15 + S5 15) | **≈ 49** |
| Demanda restante UX (US-UX-06 4 · US-UX-07 5 · US-UX-08 3) | 12 |
| Demanda restante técnica MUST (E0 6 · E1 10 · E2 13 · E3 11 · E4 9 · E5 9) | 58 |
| **Déficit real** | **≈ −21 / −22** |

**Por qué las válvulas de §10.2 no bastan.** Esas válvulas congelan STRETCH, pero los STRETCH nunca estuvieron dentro de los 86 SP MUST: congelarlos no libera ni un punto del compromiso. El déficit hay que cerrarlo **recortando MUST, por escrito y con acuerdo previo**, que es exactamente lo que §10.3 y §25.2 mandan hacer en vez de descubrirlo en la semana 5.

**Escalera de recorte acordada (~17 SP), en orden de aplicación.** Cada renglón mantiene el valor de evidencia para las actividades UX y sacrifica completitud técnica; el resto del delta lo absorben el buffer +3 de S5 y la baja carga de código de la semana de A3.

| # | Recorte | SP |
|---|---------|-----|
| 1 | **US-012** búsqueda híbrida y pgvector: diferida por completo. La búsqueda por keyword basta para las pantallas y el Hit Rate@3 no es criterio de ninguna rúbrica | −3 |
| 2 | **US-011** a 3 métricas por silo + 1 join cruzado + 3 consultas de referencia (no 10) | −2.5 |
| 3 | **US-009** sin lifecycle ni auditoría de duración; una sola signed URL | −1.5 |
| 4 | **US-024** solo evento `error` tipado, sin botón Reintentar | −1.5 |
| 5 | **US-018/019** degradación ya acordada: listar + cambiar rol + desactivar | −1 |
| 6 | **US-025** a 500 K puntos pre-agregados (degradación ya acordada) | −1 |
| 7 | **US-026** a 3 tarjetas con proyección estática y 2 niveles de revelación | −1 |
| 8 | **US-005** plegada dentro de US-030; se conserva solo el hook del span `db.retrieval` desde el inicio | −1 |
| 9 | **US-003** al puente `gcloud run deploy` que el propio criterio de la US admite | −1 |
| 10 | **US-032** a notebook con tres cifras | −1 |
| 11 | **US-033** a smoke tests; la cobertura se declara parcial (auth + compilador + conectores) | −1 |
| 12 | **US-029** solo overlay de linaje; el estado compartido con payload estático | −0.5 |
| 13 | **US-013, US-014, US-022, US-035, US-036** y todos los bloques `+N STRETCH`: **congelados** | — |

**Lo que no se recorta, porque es la evidencia del curso:** US-001/002 (sin esqueleto no hay nada), US-006 (sin datos no hay pantalla con contenido), US-015/016/017 (sin auth no hay espacio por rol que fotografiar ni tool call gobernada), US-008 en su versión keyword (es el "momento de la verdad" del journey de A2), US-020/021/023 (el agente es el diferenciador del proyecto), US-028 (las tarjetas de tool call no se pueden simular en Figma) y US-034 (sin deploy no hay prueba SUS ni métricas para A5).

**Re-recálculo al 10-ago-2026 (apertura de S4).** La escalera de recorte anterior se diseñó suponiendo que la construcción arrancaba el 30-jul. No arrancó, y dos sprints después la aritmética vuelve a cambiar.

| Concepto | SP |
|----------|-----|
| Consumido a la fecha (UX A1 11 + A2 5 + A3 4) | 20 |
| Capacidad restante (S4 15 + S5 15) | **30** |
| Demanda restante UX (US-UX-07 5 · US-UX-08 3) | 8 |
| Demanda restante técnica MUST (E0 6 · E1 10 · E2 13 · E3 11 · E4 9 · E5 9) | 58 |
| **Déficit real** | **≈ −36** |

**Lo que esto significa, dicho sin rodeos: la pista de construcción completa ya no cabe en el curso**, ni siquiera aplicando los 17 SP de la escalera de recorte. Con 30 SP de capacidad y 8 comprometidos a las dos actividades que faltan, quedan **≈22 SP para código** frente a los 41 que sobrevivirían tras el recorte máximo. Seguir planificando 36 historias técnicas es planificar una ficción.

**La decisión que sustituye a la escalera, y su criterio.** Se invierte la prioridad: **el código que se escriba en S4 y S5 es el que sostiene la evidencia UX de A4 y A5, y nada más.** En orden:

| # | Qué se construye | Por qué sobrevive | SP aprox. |
|---|------------------|-------------------|-----------|
| 1 | **Prototipo web navegable** con las 5 interfaces de A4 y datos de ejemplo embebidos | *Es* el entregable de A4 y el objeto de la prueba SUS de A5. Sin él no hay ninguna de las dos | 5–7 |
| 2 | **Despliegue accesible por URL** (Cloud Run o alternativa estática equivalente) | Sin URL no hay sesión de usabilidad remota en A5 | 1–2 |
| 3 | Datos sintéticos mínimos que den contenido creíble a las pantallas (recorte de US-006) | Una pantalla vacía no se puede probar con un participante | 2 |
| 4 | Backend real (auth, capa semántica, agente ADK, SSE) | **Se documenta como roadmap**, no como entrega del curso | — |

Los renglones 1–3 caben en la capacidad restante; el 4 no, y por eso pasa a la tabla de alcance de A4 y al apartado de trabajo futuro de A5. **Es un recorte de MUST acordado por escrito y con fecha, que es lo que §10.3 y §25.2 mandan hacer en vez de descubrirlo el 22-ago.** El proyecto no pierde su tesis —la arquitectura, la capa semántica y el agente están diseñados, fundamentados en diez papers y documentados—; pierde su implementación completa dentro del curso, y eso se declara en lugar de disimularse.

### 10.3 Regla de prioridad

> **Regla de oro del equipo:** ante conflicto de tiempo, gana el entregable de la actividad UX de la semana. Un portal impresionante con 70 en las actividades es un mal trade; unas actividades de 100 con un portal honesto de MVP es el objetivo.

---

## 11. EPIC UX (nuevo, transversal): Entregables del Curso {#epic-ux}

**Objetivo:** asegurar 100/100 (y sobrepasar) en las 5 actividades, reutilizando la investigación como insumo de diseño y el producto como evidencia. **Puntos totales de la épica: 28 SP MUST + 4 STRETCH.**

### US-UX-01 — Instrumentos de investigación y definición de usuarios prototipo (A1)

> **Ajuste de método registrado el 29-jul-2026.** Esta historia se escribió el 22-jul asumiendo trabajo de campo aplicado (encuesta con n≥15 y 3 entrevistas). Por restricción de tiempo dentro de la semana 1, el equipo decidió ejecutarla con **usuarios prototipo** (*proto-personas*): los instrumentos se diseñan completos y los usuarios se caracterizan con el conocimiento de dominio que el equipo ya posee, dejando la validación con participantes para las actividades siguientes. El texto de abajo refleja el método realmente aplicado; el original queda descrito en este recuadro para no perder la traza de la decisión.

**Como** equipo de diseño,
- **quiero** los tres instrumentos de investigación diseñados y una caracterización de usuarios prototipo del dominio financiero,
- **para que** audiencia, problema, personas y mapas de empatía tengan una base explícita y trazable, y los instrumentos queden listos para validarla en cuanto haya acceso a participantes.

**Criterios de Aceptación (ajustados al método de usuarios prototipo):**

- **Los tres instrumentos diseñados y listos para aplicar**, que es lo que el título de la actividad exige ("diseño de instrumentos de investigación de usuario"): encuesta de 13 preguntas del Anexo A.1, guía de entrevista semiestructurada del Anexo A.2 y guía de observación contextual con el esquema AEIOU.
- Consentimiento informado redactado según Anexo A.3 y **plan de aplicación** con muestra sugerida, cobertura y evidencia esperada por instrumento.
- **Criterios de análisis declarados** antes de recolectar: diagramación de afinidad, con los temas emergiendo del material en lugar de categorías fijadas de antemano.
- **Usuarios prototipo trazables:** cada persona y cada mapa de empatía se sustenta en investigación documental, experiencia profesional del equipo en áreas que operan con información financiera institucional, y observación de canales — todo declarado en el documento, sin presentar supuestos como hallazgos.
- **Trazabilidad supuesto → pregunta verificadora:** cada indicador sin dato queda rotulado "pendiente de medición" y enlazado a la pregunta del instrumento que lo levantará. Esto es lo que convierte a los usuarios prototipo en hipótesis verificables y no en adivinanzas.

**Tareas técnicas:**

- [x] Diseñar la encuesta de 13 preguntas con sus validaciones
- [x] Redactar el guion de entrevista y la guía de observación AEIOU
- [x] Redactar consentimiento, plan de aplicación y criterios de análisis
- [x] Caracterizar los usuarios prototipo y declarar el método en el documento
- [ ] Aplicar los instrumentos cuando haya acceso a participantes (ventanas: card sorting de A3, prueba SUS de A5)

**Estimación:** 3 puntos (~1.5 días). **Responsable líder:** Jacqueline. **Sprint:** S1.

**Estado al 29-jul-2026: ✅ CUBIERTA con el método de usuarios prototipo.** Lo que la rúbrica de A1 pedía en el rubro de audiencia era "la herramienta utilizada para identificar la audiencia y sus resultados", y eso quedó cubierto: tres instrumentos diseñados, método declarado, y una caracterización con fuente en cada renglón. La meta de **n≥15 respuestas era una autoexigencia del equipo, no un requisito de la rúbrica** — desproporcionada además frente a lo que la actividad pedía (6 personas y 6 mapas, dos por integrante), y de hecho se entregaron **8 de cada uno**. La retroalimentación del profesor sobre A1 confirmó el resultado, con una sola observación de maquetación ya corregida.

**Lo que este método sí implica, y queda dicho.** Los usuarios prototipo son hipótesis fundamentadas: el propio documento las llama arquetipos hipotéticos en el sentido de Cooper, y el journey map de A2 se declara *mapa de supuestos* siguiendo la advertencia de la literatura de journey mapping. Es un método legítimo y honesto, y la coherencia se mantiene mientras el equipo no presente esas hipótesis como hallazgos de campo — algo que los dos documentos entregados ya respetan. La validación llega donde el propio plan la tenía prevista: el **card sorting de A3** y la **prueba SUS de A5 con ≥5 participantes**, que la rúbrica de A5 exige con usuarios y que ya está en US-UX-08. No hay deuda que arrastrar: hay una secuencia de validación en curso.

### US-UX-02 — Documento de Actividad 1: secciones de equipo (A1)

**Como** equipo,
- **quiero** el documento con portada, introducción, identificación de la audiencia, descripción del problema y definición del producto digital,
- **para que** las secciones grupales (50 % de la rúbrica) alcancen la banda "Completo" en cada criterio.

**Criterios de Aceptación:**

- Portada con los nombres de los 3 integrantes, curso, equipo 8 y fecha (rubro 2 %).
- Introducción que describe la actividad, el método (instrumentos + n + fechas de campo) y la organización del documento (rubro 3 %).
- Audiencia con TODOS los elementos de §2.2: clientes/necesidades, pain points, demografía, intereses, dónde se conectan, herramienta de investigación **y sus resultados** (rubro 5 %).
- Problema con identificación, cuantificación (datos de la encuesta E-06/E-07), impacto por perfil y solución; **≥2 elementos visuales**: diagrama de silos "antes/después" y gráfica de encuesta (rubro 20 %).
- Producto digital: tipo (plataforma web) + tabla módulo→perfil→beneficio (§6.1) + patrones UX 2026 (§6.2) (rubro 20 %).
- PDF final con nombre exacto **"Entregable Actividad 1_equipo_8"**, estilos consistentes, referencias en APA.

**Tareas técnicas:**

- [ ] Redactar cada sección (dividido entre los 3 según checklist §24)
- [ ] Diseñar el diagrama de silos antes/después
- [ ] Integrar gráficas de la encuesta
- [ ] Maquetar, exportar a PDF y validar contra checklist §24

**Estimación:** 3 puntos (~1.5 días). **Responsable líder:** Arthur (integración). **Sprint:** S1.

**Estado al 29-jul-2026: ✅ CERRADA.** Entregada el 26-jul con los 5 rubros de equipo cubiertos. Extras sobre la banda "Completo": cuantificación con fuente en cada renglón (los indicadores sin dato dicen "pendiente de medición"), tres figuras propias (mapa de audiencia, matriz de impacto por perfil, flujo actual frente a propuesto), un mockup conceptual del buscador, matriz de trazabilidad pain point → necesidad → característica → persona, y referencias en APA. La audiencia se caracterizó con **8 perfiles de uso** en lugar de los 3 previstos.

### US-UX-03 — 6 user personas, 2 por integrante (A1)

**Como** integrante del equipo,
- **quiero** elaborar 2 user personas con la plantilla común del Anexo B según la matriz de asignación §5.3,
- **para que** los perfiles del portal queden representados en personas consistentes y trazables al método de usuarios prototipo (US-UX-01).

**Criterios de Aceptación:**

- Cada persona incluye: foto de perfil (generada con IA, estilo fotográfico consistente entre las 6), nombre, edad, sexo, ocupación; antecedentes (educación, situación familiar, intereses); objetivos (2–3 ligados al portal); pain points y desafíos (3–4, ≥1 proveniente de encuesta/entrevista); comportamientos y hábitos; frase/cita.
- La asignación respeta la matriz §5.3 (cobertura 2×Operativo, 2×Analista, 2×Directivo).
- Cada persona declara su base: investigación documental, experiencia profesional del equipo u observación de canales (método de usuarios prototipo, US-UX-01), sin presentar supuestos como hallazgos.
- Revisión cruzada: cada integrante revisa las personas de otro antes de integrar.

**Tareas técnicas:**

- [ ] Definir plantilla visual común (1 página por persona)
- [ ] Generar 6 fotos de perfil con IA en estilo homogéneo
- [ ] Redactar 2 personas por integrante y aplicar revisión cruzada

**Estimación:** 3 puntos (1 por integrante, ~0.5 día c/u). **Sprint:** S1.

**Estado al 29-jul-2026: ✅ CERRADA Y EXCEDIDA.** Se entregaron **8 personas** en lugar de las 6 que pedía la rúbrica (Laura Méndez, Diego Hernández, Roberto Valdez, Elena Ruiz, Jorge Mendieta, Arturo Castañeda, Mariana Ovalle, Ximena Solís), repartidas Jacqueline 2 · Alexandro 4 · Arthur 2, todas con la plantilla completa. Extras: designación de **persona primaria** (Laura, procedimiento de Hartson y Pyla), apartado de alcance y límite del método, y criterios de calidad aplicados y contrastados con la literatura. Las ocho son **usuarios prototipo** según el método de US-UX-01, con su base declarada en el documento.

### US-UX-04 — 6 mapas de empatía, 2 por integrante (A1)

**Como** integrante del equipo,
- **quiero** elaborar los mapas de empatía de mis 2 personas,
- **para que** cada persona tenga su correlato emocional documentado y trazable a su base.

**Criterios de Aceptación:**

- Cuadrantes etiquetados exactamente **"Says", "Thinks", "Does", "Feels"** (en inglés, como pide la rúbrica).
- ≥3 observaciones por cuadrante, coherentes con la persona correspondiente.
- Las observaciones del cuadrante "Says" están redactadas en la voz de la persona y son coherentes con su perfil; cuando se apliquen las entrevistas, se sustituyen por citas textuales (US-UX-01).
- Plantilla visual uniforme entre los 6 mapas (misma retícula y código de color por perfil).

**Tareas técnicas:**

- [ ] Plantilla de 4 cuadrantes reutilizable
- [x] Redactar el cuadrante Says en la voz de cada persona (citas textuales cuando se apliquen las entrevistas)
- [ ] Elaborar 2 mapas por integrante y revisar coherencia persona↔mapa

**Estimación:** 2 puntos (~1 día repartido). **Sprint:** S1.

**Estado al 29-jul-2026: ✅ CERRADA Y EXCEDIDA.** **8 mapas** en lugar de los 6 exigidos, uno por persona, con los cuadrantes etiquetados en inglés y ≥3 observaciones cada uno, en la voz de cada persona conforme al método de usuarios prototipo. **Corrección aplicada el 29-jul tras la retroalimentación del profesor sobre A1** (tres mapas quedaron partidos en dos páginas): el componente `\mapaempatia` compone ahora la retícula en una caja, mide su altura y la reserva con `\needspace`, de modo que titular y mapa viajan juntos y ningún mapa admite corte interno. Verificado sobre el PDF: los 8 mapas completos, cada uno en una sola página.

### US-UX-05 — Escenarios y Journey Maps (A2)

**Como** equipo de diseño,
- **quiero** escenarios de uso narrativos y journey maps por perfil sobre los flujos reales del portal,
- **para que** el recorrido emocional y las oportunidades de diseño queden mapeadas de punta a punta antes de estructurar la información.

**Criterios de Aceptación (definitivos — rúbrica publicada y absorbida el 29-jul-2026, §2.3):**

- **Dos escenarios por integrante, 6 en total** (45 % de la rúbrica), cada uno con los cuatro elementos exigidos y rotulados como tales: definición del usuario, descripción de la tarea con sus pasos, identificación de las interacciones clave y descripción del resultado deseado **con la sensación del usuario** al completarlo.
- **Un journey map de equipo** (50 % de la rúbrica) construido a partir de la discusión conjunta de los escenarios individuales, precedido por el **listado de actividades** que el usuario ejecuta para cumplir uno de los objetivos, y que documente cómo aborda cada etapa, sus pensamientos, los puntos que complican la adopción y las oportunidades que los mitigan.
- Portada con los nombres de los 3 integrantes (2 %) e introducción sobre la actividad realizada (3 %).
- Cada escenario y cada mapa conecta explícitamente con una persona de A1; los pain points mantienen la trazabilidad cita/hipótesis → pain → oportunidad.
- Formato visual consistente entre todos los mapas y PDF nombrado **"Entregable Actividad 2_equipo_8"**.
- La herramienta Custellence es **propuesta, no exigida**: se admite plantilla propia si conserva la estructura de carriles del ejemplo de referencia, declarándolo en el documento.

**Tareas técnicas:**

- [x] Redactar los 6 escenarios (2 por integrante) con los 4 elementos rotulados
- [x] Descomponer el objetivo en listado de actividades y construir el journey map de equipo en taller
- [x] Construir los 3 journey maps individuales (extra sobre la rúbrica)
- [x] Validar trazabilidad A1→A2 y armar el PDF
- [x] Subir "Entregable Actividad 2_equipo_8.pdf" a Canvas antes del dom 2-ago 23:59

**Estimación:** 5 puntos (~2.5 días). **Sprint:** S2.

**Estado al 10-ago-2026: ✅ CERRADA.** Entregada el 2-ago-2026 (`docs/semana_2/Entregable Actividad 2_equipo_8.pdf`). Entregado por encima de la rúbrica: **6 escenarios** con los cuatro elementos rotulados explícitamente y **4 journey maps** (3 individuales + el de equipo) en lugar del único exigido. Extras que ninguna banda pedía: taller de construcción documentado con su fundamento bibliográfico (Walter, 2022), listado de 15 actividades, 7 etapas × 7 carriles con curva emocional declarada de −2 a +2, alcance declarado como *mapa de supuestos* con los tres supuestos fuertes y la pregunta que verifica cada uno, matriz de trazabilidad fricción → oportunidad → característica → métrica, principios rectores y antiprincipios, y figura de recorridos entrelazados que conecta los seis escenarios. El anexo con el mapa en formato de tabla salió del documento en la revisión de contenido del 29-jul: era la tercera de tres reproducciones del mismo mapa (panorámica, desarrollo etapa por etapa y tabla) y se conservó solo la panorámica con su lectura interpretativa. **Desviación de forma frente al plan del 22-jul:** se planearon 3 escenarios y 3 mapas; la rúbrica real pedía 6 escenarios y 1 mapa de equipo. Absorbido sin coste extra de SP (§2.3).

### US-UX-06 — Análisis competitivo y Arquitectura de Información (A3)

**Como** equipo de diseño,
- **quiero** un benchmark de productos comparables y la arquitectura de información del portal,
- **para que** las decisiones de estructura y navegación estén justificadas frente a alternativas reales y validadas con usuarios.

**Criterios de Aceptación (definitivos — rúbrica publicada y absorbida el 9-ago-2026, §2.3.b):**

- **Los 26 pasos numerados de la rúbrica, cada uno identificable por su subtítulo y con contenido propio**, nunca redactado en futuro: 5 de análisis competitivo, 10 de card sorting, 5 de arquitectura de información y 6 de mapa de navegación.
- **Análisis competitivo (25 %)**: identificación de competidores, recolección de información con fuentes citadas y fechadas, análisis comparativo, ventaja competitiva y estrategias de mejora. Precios y calificaciones de clientes con URL y fecha de consulta; las estimaciones de agregadores etiquetadas como tales y distinguidas de las tarifas oficiales.
- **Card sorting (25 %)**: los diez pasos con datos calculados sobre salidas crudas archivadas, no simuladas. Si se ejecuta con evaluadores prototipo condicionados por persona (§3.8), la nota de método lo declara sin ambigüedad y el vocabulario del documento no llama "participantes" ni "usuarios" a los evaluadores.
- **Arquitectura de información (25 %)**: los cuatro sistemas de Morville y Rosenfeld (organización, etiquetado, navegación y búsqueda), con las categorías derivadas del ejercicio y no impuestas por el equipo.
- **Mapa de navegación (20 %)**: jerarquía visualizada, subcategorías determinadas, validación con resultados y al menos **un cambio aplicado** por efecto de esa validación.
- Portada con los nombres de los 3 integrantes (2 %) y sección titulada literalmente **"Introducción"** (3 %).
- Trazabilidad viva con A1 y A2: las personas y los escenarios se llaman igual, y el instrumento se ancla en las etapas de fricción del journey map de equipo.

**Tareas técnicas:**

- [x] Investigar y capturar los productos del benchmark (6 alternativas, con capturas de interfaz reales)
- [x] Construir matriz comparativa y conclusiones
- [x] Ejecutar card sorting y sintetizar resultados
- [x] Dibujar sitemap + flujos por rol y armar el PDF
- [ ] ~~Insertar capturas reales de login y catálogo como evidencia de "arquitectura implementada"~~ **No se cumplió**: la pista de construcción sigue en 0 % (§2.6). Se sustituyó por el wireframe de navegación `figuras/a3_wireframe_navegacion.png`, declarado como diseño y no como producto
- [x] Subir "Entregable Actividad 3_equipo_8.pdf" a Canvas antes del dom 9-ago 23:59

**Estimación:** 4 puntos (~2 días). **Sprint:** S3.

**Estado al 10-ago-2026: ✅ CERRADA Y EXCEDIDA.** Entregada el 9-ago-2026 (`docs/semana_3/Entregable Actividad 3_equipo_8.pdf`, 54 páginas). Lo que se entregó, contra lo que la rúbrica pedía:

| Ejercicio | Lo exigido | Lo entregado |
|-----------|-----------|--------------|
| Competitivo (5 pasos) | Identificar, recolectar, analizar, ventaja, estrategias | **6 alternativas** con ficha, postura competitiva de Annacchino, capturas de interfaz reales, precios verificados (Bloomberg 31,980 USD/año y 28,320 USD por asiento con contrato mínimo de 2 años; G2 4.4/5 sobre 69 reseñas), tabla de trazabilidad de fuentes con fecha de consulta, y el hallazgo fechado del **retiro de Power BI Q&A en dic-2026** usado como argumento de ventana competitiva |
| Card sorting (10 pasos) | Ejercicio ejecutado y analizado | Mazo de **35 tarjetas** derivado del portal legado (CIF), sesión piloto que cambió una etiqueta, **8 evaluadores prototipo** condicionados por las 8 personas de A1 y ciegos entre sí, salidas crudas por evaluador en `datos/a3_sorts/P1..P8.json`, matriz de co-ocurrencia 35×35, dendrograma de enlace promedio, **9 conglomerados** frente a las 4 categorías propuestas, tarjetas en disputa y anexo con el registro completo |
| Arquitectura (5 pasos) | Usuarios, contenido, organización, pruebas, navegación | 4 categorías de primer nivel con jerarquía de segundo nivel, **9 facetas transversales** de etiquetado múltiple justificadas por las peticiones de duplicado, y los cuatro sistemas de Morville y Rosenfeld nombrados explícitamente |
| Mapa de navegación (6 pasos) | Jerarquía, subcategorías, validación, iteración | **Prueba de árbol de 5 rutas** en la misma corrida: 4 confirmadas y **1 refutada** —el indicador de riesgo obtuvo 1 acierto de 8 y 6 evaluadores lo buscaron en Exploración—, con el cambio aplicado antes de A4: tableros e indicadores se movieron a Exploración y extracción (2.4) y la tercera categoría se renombró **Gobierno del dato** |

Extras que ninguna banda pedía: análisis reproducible en Python versionado (`analisis_a3.py`, `generar_figuras_a3.py`, `generar_anexo_a3.py`), conteos sobre 8 en lugar de porcentajes —porque con ocho observaciones un porcentaje transmite una precisión que la muestra no tiene—, folksonomía literal de los ocho evaluadores transcrita, y nota de método que acota qué puede afirmarse a partir de 40 datos de prueba de árbol y 280 colocaciones de tarjetas.

**La desviación declarada:** el card sorting se ejecutó con **evaluadores prototipo, no con ≥6 colegas humanos** como decía el criterio provisional del 22-jul. La rúbrica no exigía participantes humanos (§2.3.b) y el documento declara el método en la introducción, en la sección y en el anexo, así que la banda no se pierde. La consecuencia se registra donde importa: §22.1.b y la prueba SUS de A5, que queda como **única** ventana de validación humana del proyecto.

**El regalo que se perdió, y qué lo sustituyó.** El criterio pedía derivar el sitemap de `docs/security.md` y montar capturas de login y catálogo reales. US-016 nunca se implementó, así que el sitemap se construyó desde el card sorting en lugar de desde la matriz de permisos. Costo: un diferenciador, no puntos de banda — exactamente como el plan había previsto el 29-jul. Lo sustituyó `figuras/a3_wireframe_navegacion.png`, que además queda como **punto de partida de la alta fidelidad de A4**.

### US-UX-07 — Interfaces de alta fidelidad (A4)

**Como** equipo de diseño,
- **quiero** el sistema de diseño y las pantallas de alta fidelidad del portal, en paridad con el prototipo funcional,
- **para que** la entrega de A4 muestre tanto el diseño pulido como el producto vivo que lo implementa.

> ⚠️ **Criterios superados por §26.2 (10-ago-2026).** Los de abajo se conservan como registro de
> lo que se asumió el 22-jul, antes de leer la rúbrica. **Los vigentes están en
> [§26](#26-avance-4)**, que reescribe los ocho criterios, retira Figma y sustituye la tabla de
> paridad por la tabla de alcance de tres estados.

**Criterios de Aceptación (provisionales ⚠️, superados — ver §26.2):**

- Sistema de diseño documentado: tokens de color (modo claro; oscuro stretch), tipografía, espaciado, estados de componentes (default/hover/focus/error/loading). **Fuente única: los tokens del prototipo navegable** (`@theme` de Tailwind v4), derivados a su vez de la paleta y la tipografía del sistema LaTeX de A1–A3 (`docs/entregables/estilo/uxdoc.sty`), de modo que los cinco documentos del curso y la interfaz se lean como el mismo producto. Cualquier archivo de Figma se deriva de ahí, no al revés.
- Pantallas de alta fidelidad en Figma: login, **home por espacio de trabajo ×4** (operativo, analista, directivo, administrador — los 8 perfiles de A1 se agrupan en estos 4), catálogo con resultados, explorador con filtros, chat con tarjetas de tool call (estados: anunciando/ejecutando/resultado/error), tarjetas predictivas con drill-down, flujo de exportación (solicitud→job→enlace), panel admin de usuarios.
- Paridad demostrada: tabla pantalla-Figma ↔ ruta del prototipo Nuxt donde exista implementación (E4). **Lo que quede solo en diseño se marca explícitamente como *roadmap* en esa misma tabla** — incluidas las capacidades que A2 promete y el catálogo US-001…036 no cubre (§25.5, hallazgo 2). El silencio sobre ellas es lo único que no funciona: un evaluador puede contrastar las oportunidades del journey contra el prototipo.
- Pre-validación con evaluadores sintéticos condicionados por las **8 personas** (§3.8): protocolo, hallazgos y al menos 1 iteración de diseño documentada. **Debe correr sobre capturas reales del prototipo, no sobre mockups**: es lo que la distingue de una revisión de diseño convencional.

**Tareas técnicas (reformuladas el 10-ago, ver el replanteo al final de la US):**

- [ ] Definir los tokens de diseño derivados de `uxdoc.sty` (paleta, tipografía, escala de espaciado, radios, estados)
- [ ] Construir el **prototipo web navegable** con las 5 interfaces de alta fidelidad explorables
- [ ] Diseñar los estados que no son pantalla completa: vacío, cargando, error, sin permiso, y los 4 estados de la tarjeta de tool call
- [ ] Correr pre-validación sintética sobre las pantallas navegables y aplicar **≥1 iteración documentada** (hallazgo → cambio → versión)
- [ ] Documentar la tabla de alcance —qué es diseño navegable, qué está conectado a datos y qué es *roadmap*— y armar el PDF
- [ ] Subir "Entregable Actividad 4_equipo_8.pdf" a Canvas antes del dom 16-ago 23:59

**Estimación:** 5 puntos (~2.5 días). **Responsable líder:** Alexandro. **Sprint:** S4.

**Nota de replanificación (29-jul): esta es la actividad de mayor exposición del proyecto.** Su mitigación de déficit declarada es "las capturas del prototipo reducen las pantallas dibujadas". Si el frontend no corre el **jue 13-ago** (gate nuevo de §20), la mitigación se invierte y hay que dibujar *más* en la semana que ya iba corta: se pierden el criterio de paridad, la pre-validación sobre pantallas reales y los patrones 3, 4 y 6 de §6.2, que solo se demuestran en movimiento. Es la única semana del calendario donde dos días de retraso son irrecuperables.

**Replanteo del 10-ago-2026: el escenario de riesgo se materializó, y A4 cambia de forma.** El frontend no existe (§2.6), así que la mitigación "las capturas del prototipo reducen las pantallas dibujadas" ya no es aplicable. La decisión del equipo es **no dibujar mockups estáticos ni fingir paridad**, sino invertir la semana en un **prototipo web navegable de alta fidelidad**: una página que el evaluador abre y recorre, con las cinco interfaces del portal derivadas de la arquitectura que A3 validó. Es la opción con más evidencia por hora invertida, porque un prototipo navegable *es* alta fidelidad, sirve de base a la pre-validación sintética sobre pantallas reales —el criterio que distingue esta actividad de una revisión de diseño convencional— y se convierte en el objeto sobre el que corre la prueba SUS de A5.

**Las 5 interfaces, y de dónde sale cada una.** ⚠️ *Set propuesto, pendiente de confirmación del equipo.* La derivación no es libre: cuatro salen literalmente de las categorías de primer nivel que el card sorting produjo y la prueba de árbol corrigió (§US-UX-06), y la quinta es el diferenciador del proyecto, transversal a todas.

| # | Interfaz | Origen en los entregables previos | Patrones UX que demuestra (§6.2) |
|---|----------|-----------------------------------|----------------------------------|
| 1 | **Inicio** — buscador unificado, búsquedas recientes, favoritos, mis alertas | Categoría 1 de la IA de A3; primera etapa del journey map de equipo de A2 | Revelación progresiva; espacios de trabajo por rol |
| 2 | **Exploración y extracción** — catálogo temático facetado, filtros, vista previa, exportación, y **2.4 Tableros e indicadores** | Categoría 2 de la IA, ya con la corrección que la prueba de árbol impuso (los tableros se movieron aquí) | Tarjetas predictivas con drill-down; estado compartido tablero↔chat |
| 3 | **Gobierno del dato** — diccionario y metadatos, linaje y calidad, catálogo de fuentes | Categoría 3 de la IA, renombrada tras el card sorting; es el "momento de la verdad" del journey de A2 | Overlay de linaje explicable |
| 4 | **Asistente conversacional** — chat con tarjetas de tool call en sus 4 estados y streaming con Stop | Diferenciador del proyecto (§4.2); escenarios 1 y 3 de A2; papers 06 y 07 | Transparencia de tool call; streaming real y cancelable |
| 5 | **Administración** — usuarios, roles y permisos, solicitudes y aprobaciones, bitácora de accesos, integraciones | Categoría 4 de la IA; escenario 5 de A2 (acceso mínimo suficiente) | Espacios de trabajo por rol |

El **login** enmarca las cinco como pantalla de entrada, pero no cuenta como una de ellas: su valor de evidencia es bajo y su costo de diseño también. Las **9 facetas transversales** de A3 se resuelven como accesos cruzados entre interfaces, no como duplicados de contenido — ese es el contrato que el mapa de navegación dejó firmado.

**Lo que esta forma de A4 obliga a declarar, y no es negociable.** El documento debe distinguir con exactitud tres estados por pantalla: *navegable con datos de ejemplo*, *navegable sin datos* y *roadmap*. Incluye las capacidades que A2 promete y el catálogo técnico no cubre (§25.5, hallazgo 2). El silencio sobre ellas es lo único que no funciona: un evaluador puede contrastar las oportunidades del journey de A2 contra lo que la pantalla hace.

### US-UX-08 — Evaluación de usabilidad y entrega final (A5)

**Como** equipo,
- **quiero** evaluar la usabilidad del portal con usuarios reales e integrar todo el proceso en la entrega final,
- **para que** el cierre del curso demuestre el ciclo UX completo con métricas.

**Criterios de Aceptación (provisionales ⚠️):**

- Protocolo de prueba moderada con 3 tareas por perfil (sobre el prototipo desplegado en Cloud Run).
- ≥5 participantes reales + cuestionario **SUS**; meta SUS ≥ 75; hallazgos priorizados (severidad × frecuencia) y correcciones aplicadas o backlogueadas.
- Documento final integrador que hila A1→A5 como caso de estudio UX (estándar del Grocery Shopping App del curso, superado con producto real y métricas de §22).
- Video demo de 3 minutos + presentación final.

**Alcance STRETCH (no comprometido):** +4 SP si la rúbrica exige análisis extendido (p. ej. test A/B de variantes, reporte de accesibilidad WCAG).

**Nota de replanificación (29-jul): A5 es donde el ciclo se cierra con usuarios.** A1 y A2 se construyeron con usuarios prototipo (US-UX-01) y A3 aporta la primera validación con el card sorting; **estas sesiones son las que permiten escribir "usabilidad medida" en el documento final**, y la rúbrica de A5 las exige de todos modos. Su valor metodológico sube en consecuencia: contrastan las hipótesis de las cinco semanas anteriores.

Dos precauciones que se deciden ahora y no la semana de la prueba:

- **Un prototipo inestable puntúa peor en SUS que un prototipo de Figma limpio.** Un cold start de Cloud Run, un stream que se corta o un 500 en medio de una tarea bajan el SUS por debajo de 75, y ese hallazgo queda escrito en la entrega final. De ahí el congelamiento del lun 17-ago, `min_instances = 1` durante los días de prueba, datos precalentados y el ensayo del mar 18 con un integrante como participante de prueba.
- **Punto de decisión con fecha: vie 14-ago 12:00.** Si el chat SSE no está estable, las tareas del SUS se limitan a catálogo + dashboard + export, y el agente se muestra en el video demo sin someterlo a prueba. Decidirlo el viernes es método; decidirlo el miércoles 19 con el participante en la llamada es improvisación.

**Tareas técnicas:**

- [ ] Diseñar protocolo y reclutar ≥5 participantes
- [ ] Ejecutar sesiones + SUS y sintetizar hallazgos
- [ ] Redactar documento final integrador
- [ ] Grabar video demo y preparar presentación

**Estimación:** 3 puntos (~1.5 días). **Sprint:** S5.

---

## 12. EPIC 0: Infraestructura y Configuración Base {#epic-0}

**Objetivo:** entorno local reproducible multiservicio, CI/CD y esqueleto de observabilidad antes de tocar reglas de negocio. **Puntos: 6 MUST + 5 STRETCH.**

### US-001 — Entorno Docker Compose Multiservicio y Monorepo

**Como** desarrollador del equipo,
- **quiero** un monorepo con entorno local reproducible levantado con `make dev` y configuración de entorno validada,
- **para que** los tres miembros trabajemos sobre los mismos servicios sin fricción y la app falle rápido si falta configuración.

**Criterios de Aceptación:**

- `make dev` levanta simultáneamente FastAPI (backend), Nuxt 4 (frontend) y PostgreSQL con red bridge compartida y volúmenes de código (HMR).
- Frontend Nuxt 4 con la estructura `app/` (páginas, componentes y layouts aislados de archivos raíz) para HMR rápido; esqueleto FastAPI con routers vacíos.
- Variables de entorno desde `.env.local` con validación estricta de esquema en FastAPI (Pydantic Settings): la app **no arranca** si falta `DATABASE_URL`, `GEMINI_API_KEY` o `JWT_SECRET_KEY`.
- El detalle de manejo de dependencias, imágenes multi-stage y migraciones se declara en US-002.

**Tareas técnicas:**

- [ ] `docker-compose.yml` con servicios backend/frontend/postgres y volúmenes de código
- [ ] Estructura `app/` de Nuxt 4 y esqueleto de routers FastAPI
- [ ] Settings Pydantic con validación estricta de entorno (falla al arrancar)
- [ ] Makefile con `dev`, `test`, `lint`

**Estimación:** 1 punto (~0.5 día). **Sprint:** S1.

### US-002 — Dependencias Reproducibles y Esqueleto de Migraciones

**Como** equipo,
- **quiero** manejo de dependencias determinístico (pnpm + Poetry) y el esqueleto de migraciones dbmate,
- **para que** las tres máquinas y CI instalen exactamente las mismas versiones y el esquema evolucione solo por migraciones versionadas.

**Criterios de Aceptación:**

- Frontend: **pnpm** con versión fijada vía campo `packageManager` (Corepack); `pnpm-lock.yaml` commiteado; capa de caché en Docker (`pnpm fetch` antes de copiar el código).
- Backend: **Poetry** (`poetry.lock` commiteado; grupos `dev`/`test`); Polars 1.x declarado como dependencia core; export a `requirements.txt` para la imagen slim de producción.
- Dockerfiles multi-stage para FastAPI (Poetry export → imagen slim) y Nuxt 4 (caché de pnpm).
- Migraciones de esquema aplicables con `make db-up` (wrapper de `dbmate up`); `db/schema.sql` versionado en git; binario dbmate en la imagen de desarrollo y carpeta `db/migrations/`.

**Tareas técnicas:**

- [ ] Dockerfile multi-stage para FastAPI (Poetry export → imagen slim)
- [ ] Dockerfile para Nuxt 4 con capa de caché de pnpm (`pnpm fetch`)
- [ ] Makefile con `db-new`, `db-up`, `db-rollback` + binario dbmate en la imagen dev
- [ ] Verificar reproducibilidad de lockfiles (instalación limpia en las 3 máquinas)

**Estimación:** 1 punto (~0.5 día). **Sprint:** S1.

### US-003 — Infraestructura GCP con Terraform

**Como** líder de plataforma,
- **quiero** la infraestructura mínima declarada en Terraform para GCP,
- **para que** los despliegues a staging y producción sean predecibles y reproducibles.

**Criterios de Aceptación:**

- MUST (1 SP): módulo mínimo que provisiona 2 servicios Cloud Run (frontend/backend) con **scale-to-zero (`min_instances = 0`)**, bucket GCS para exportes y Secret Manager con `GEMINI_API_KEY` y `JWT_SECRET_KEY` inyectados a Cloud Run.
- La alternativa documentada `gcloud run deploy` (script) es aceptable como puente mientras Terraform madura.

**Alcance STRETCH (no comprometido, +2 SP):** módulos parametrizados por entorno (staging/prod), backend de estado de Terraform en bucket GCS versionado.

**Tareas técnicas:**

- [ ] Módulo Terraform `infra/` con variables (proyecto, región, imágenes)
- [ ] Configurar inyección de Secret Manager → Cloud Run
- [ ] Documentar bootstrap (cuenta, APIs habilitadas, service account de deploy)

**Estimación:** 1 punto MUST (~0.5 día) + 2 stretch. **Sprint:** S1 (stretch: S5).

### US-004 — Pipeline CI/CD con GitHub Actions

**Como** equipo,
- **quiero** un pipeline automatizado que valide y despliegue cada cambio,
- **para que** cada merge a `main` llegue a Cloud Run con pruebas exitosas y sin intervención manual.

**Criterios de Aceptación:**

- Cada push dispara: instalación con Poetry/pnpm (con caché de lockfiles), linting (ruff + eslint) y pruebas unitarias (pytest y Vue Test Utils).
- Merge a `main` dispara: build de imágenes Docker, push a Artifact Registry, **`dbmate up` contra la base del entorno** y deploy a Cloud Run.
- Secretos del pipeline en GitHub Environments (no en el repo).

**Alcance STRETCH (no comprometido, +1 SP):** entornos staging/prod separados con aprobación manual a prod.

**Tareas técnicas:**

- [ ] Workflow `.github/workflows/ci.yml` (lint + test, matriz back/front)
- [ ] Workflow `.github/workflows/deploy.yml` (build, push, migrate, deploy)
- [ ] Configurar secretos y permisos de la service account

**Estimación:** 2 puntos (~1 día). **Sprint:** S1.

### US-005 — Trazabilidad y Observabilidad base (OpenTelemetry)

**Como** ingeniero backend,
- **quiero** el esqueleto de OpenTelemetry en FastAPI desde la semana 1,
- **para que** cuando el agente exista (S3) solo haya que colgar los spans LLM de una instrumentación ya probada.

**Criterios de Aceptación:**

- MUST (1 SP): SDK de OpenTelemetry inicializado; un trace representa cada solicitud HTTP de inicio a fin; span hijo `db.retrieval` en las funciones de extracción Polars; exporter a consola en dev y a Cloud Trace en cloud.
- Los atributos LLM (`llm.usage.*`, `llm.prompt_hash`) se implementan en US-030 (S5) sobre esta base.

**Alcance STRETCH (no comprometido, +2 SP):** dashboard de latencias en Cloud Monitoring desde S2.

**Tareas técnicas:**

- [ ] Instalar e inicializar SDK + instrumentación automática de FastAPI
- [ ] Decorador/context manager para spans `db.retrieval` en extractores
- [ ] Verificar propagación de contexto en llamadas async

**Estimación:** 1 punto MUST (~0.5 día) + 2 stretch. **Sprint:** S1.

---

## 13. EPIC 1: Ingesta, Catálogo y Exportación {#epic-1}

**Objetivo:** eliminar la "dispersión de información" con silos sintéticos realistas, catálogo institucional y exportación sin fricción. **Puntos: 10 MUST + 5 STRETCH.**

### US-006 — Generación de Silos Sintéticos

**Como** analista de datos,
- **quiero** silos financieros sintéticos realistas (créditos, liquidez, derivados) reproducibles,
- **para que** todo el flujo demo opere sobre datos creíbles, versionados y con IDs cruzables entre silos.

**Criterios de Aceptación:**

- Generadores Polars + Faker con **semilla fija** producen los datasets de §9 (`creditos` 1–5 M, `liquidez` ~1 M, `derivados` ~500 K) en Parquet bajo `data/silos/`, con esquemas heterogéneos a propósito (nombres crípticos distintos por silo) e IDs de cliente compartidos entre silos.
- Anomalías inyectadas deliberadamente (~0.1 % de registros: fechas imposibles, montos negativos, duplicados) documentadas en `data/README.md` (insumo del perfilado EDA de US-010 y de los journey maps de A2).
- `make data` regenera los tres datasets de forma determinística.

**Tareas técnicas:**

- [ ] `ml/data/generators.py` (sintéticos con semilla) y script `make data`
- [ ] Documentar esquemas heterogéneos e IDs compartidos en `data/README.md`
- [ ] Inyección tipificada de anomalías (~0.1 %)

**Estimación:** 3 puntos (~1.5 días). **Sprint:** S1 (v0) → S2 (cierre).

### US-007 — Conectores Asíncronos, Caché y Degradación Elegante

**Como** analista de datos,
- **quiero** conectores asíncronos estandarizados con caché y degradación elegante,
- **para que** la extracción no bloquee el event loop y un silo caído no tumbe a los demás.

**Criterios de Aceptación:**

- Lectura vía funciones `async def` que no bloquean el event loop (lectura Polars delegada a threadpool).
- **Graceful degradation**: si un silo falla, los demás siguen respondiendo y el error queda tipificado (excepciones propias por silo).
- Caché en memoria (TTL configurable) para consultas repetitivas.
- Pruebas `pytest-asyncio`: éxito, silo caído, caché hit/miss.

**Alcance STRETCH (no comprometido, +1 SP):** conector a una fuente externa simulada (API mock con latencia y errores aleatorios) para demostrar resiliencia.

**Tareas técnicas:**

- [ ] `ml/data/extractors.py` con lectura async + caché TTL
- [ ] Tipificación de errores por silo (excepciones propias)
- [ ] Pruebas asíncronas de integración de conectores (éxito/caído/caché)

**Estimación:** 1 punto (~0.5 día). **Sprint:** S2.

### US-008 — Módulo de Descubrimiento de Datos (Catálogo Semántico)

**Como** directivo u operativo,
- **quiero** un diccionario de datos centralizado con conocimiento tribal,
- **para que** pueda buscar términos en lenguaje de negocio y saber en qué base institucional existe la información y cómo usarla correctamente.

**Criterios de Aceptación:**

- Tablas `catalog_source`, `catalog_field` y `catalog_tribal_note` creadas vía **migración dbmate** (`db/migrations/*_create_catalog.sql` con `-- migrate:up/down`), modeladas con SQLModel.
- Cada campo documenta: nombre físico, nombre de negocio, definición, dueño/área, sensibilidad, silo de origen; las notas tribales capturan reglas de uso ("fecha valor T+1", "prefijo de ID") con **condición de aplicabilidad** (patrón Tk-Boost §3.2).
- `GET /api/catalog/search?q=` responde búsqueda por keywords (ILIKE + ranking simple) con fuente, definición y notas tribales; protegido con JWT (cualquier rol autenticado).
- **La tarjeta de resultado expone los cuatro campos que el journey de A2 exige en la etapa 3**: fuente, propietario, periodicidad y fecha de última actualización, sin necesidad de abrir la ficha. Es el criterio que sostiene la oportunidad "fuente, propietario y vigencia en la tarjeta".
- **Estado de vigencia por campo con marca de versión retirada y enlace a la vigente** (+0.5 SP, añadido el 29-jul). Atributo del propio catálogo: `is_current` más referencia al sucesor. Cubre las etapas 3, 4 y 7 del journey de equipo y los escenarios 4 (Roberto publica una nueva versión) y 6 (Ximena sobrevive al cambio de esquema), y es la métrica del principio "Sin sorpresas".
- **Copiado con procedencia por omisión** (+0.5 SP, añadido el 29-jul): el endpoint devuelve, junto al valor, un bloque de procedencia listo para pegar (valor + fuente + fecha + definición). Cubre la etapa 6 del journey ("copiar el dato pierde el contexto") y es la métrica del principio "Respaldado": proporción de respuestas con procedencia completa.
- Seed inicial: 200–400 entradas generadas desde los esquemas sintéticos + curaduría manual de ~30 notas tribales.
- Preparado para RAG: el contrato de respuesta ya incluye los campos que consumirá la búsqueda híbrida (US-012) y el agente (US-020/US-021).

**Alcance STRETCH (no comprometido, +1 SP):** sugerencia de fuentes relacionadas ("quien consulta liquidez suele cruzar con créditos").

**Tareas técnicas:**

- [ ] Migración dbmate del esquema del catálogo, con `is_current` y referencia al sucesor
- [ ] Modelos SQLModel + seed desde los generadores
- [ ] Endpoint `GET /api/catalog/search` con los 4 campos en la tarjeta y el bloque de procedencia
- [ ] Curaduría de notas tribales iniciales

**Estimación:** 3 puntos → **4 puntos** (~2 días) tras absorber los dos criterios de A2. **Sprint:** S2 (arranque real mié 5-ago, §19).

**Nota de trazabilidad A1/A2 → producto (29-jul).** Esta US es la que más carga narrativa tiene de los documentos entregados: es el **momento de la verdad** del journey map de equipo (etapa 4, emoción +2 si la ficha responde sus tres preguntas sin intermediarios; −2 si hay que escribirle a alguien). De aquí sale la captura de mayor valor para A3 y A4. Los dos criterios añadidos son las dos capacidades prometidas en A2 más baratas de implementar, porque son atributos de un catálogo que de todos modos hay que seedear.

### US-009 — Exportaciones Pesadas en Segundo Plano

**Como** analista de datos,
- **quiero** solicitar descargas masivas de datos crudos (CSV/Excel) sin congelar la interfaz,
- **para que** pueda procesarlas en otras herramientas mientras sigo trabajando.

**Criterios de Aceptación:**

- `POST /api/export` (scope `analista`+) valida la solicitud y responde **inmediatamente** con `job_id`; el procesamiento (joins Polars, serialización CSV/XLSX) corre en BackgroundTasks.
- `GET /api/export/{job_id}` devuelve estado (`queued|running|done|failed`) consultado por el frontend con polling.
- Al terminar, el archivo se sube a GCS bajo `exports/{user}/{job_id}.{ext}` con **signed URL** de expiración 24 h; los objetos tienen lifecycle de 7 días.
- Registro del job en tabla `export_job` (migración dbmate) con usuario, filtros, tamaño y duración (auditoría).
- Prueba de no-bloqueo: durante un export de 1 M filas, `GET /api/catalog/search` responde < 500 ms.

**Alcance STRETCH (no comprometido, +1 SP):** cola Cloud Pub/Sub + worker separado en Cloud Run (en lugar de BackgroundTasks).

**Tareas técnicas:**

- [ ] Migración dbmate `export_job` + modelo SQLModel
- [ ] Endpoints de creación/estado + worker BackgroundTasks con Polars
- [ ] Generación de signed URLs y lifecycle del bucket
- [ ] Prueba de concurrencia export vs. consulta

**Estimación:** 3 puntos (~1.5 días). **Sprint:** S2.

### US-010 — Perfilado Exploratorio (EDA) de los Silos Sintéticos

**Como** equipo de investigación UX,
- **quiero** un perfilado exploratorio breve de los silos sintéticos,
- **para que** validemos el realismo de los datos y alimentemos escenarios y journey maps con evidencia (A2/A3).

**Alcance:** historia **STRETCH** — entregable propio que alimenta directamente la pista UX (A2/A3).

**Criterios de Aceptación (STRETCH, no comprometido):**

- Notebook breve (Polars) con distribuciones, nulos, cardinalidades y correlaciones básicas por silo.
- **Detección de las anomalías inyectadas** en US-006 (verifica que el generador y el perfilado son consistentes).
- Hallazgos exportables como evidencia visual para A2 (escenarios de descubrimiento) y A3 (taxonomía del catálogo).

**Tareas técnicas:**

- [ ] Notebook `ml/eda/perfilado.ipynb` con perfilado Polars por silo
- [ ] Rutina de verificación de anomalías inyectadas
- [ ] Exportar gráficas para los entregables de A2/A3

**Estimación:** +2 STRETCH. **Sprint:** S2.

---

## 14. EPIC 2: Motor Analítico, Seguridad y Usuarios {#epic-2}

**Objetivo:** capa semántica de consultas Polars, búsqueda híbrida del catálogo y el gobierno de acceso (JWT + roles + gestión de usuarios) que exigen los endpoints gobernados. **Puntos: 13 MUST + 5 STRETCH.**

> Esta épica agrupa dos frentes: **motor analítico y búsqueda** (US-011…015) y **seguridad y usuarios** (US-016…019). Se mantienen en la misma épica porque los endpoints gobernados y el RBAC son interdependientes (el agente hereda los scopes del usuario).

### US-011 — Endpoints Analíticos con Capa Semántica (FastAPI + Polars)

**Como** analista de datos,
- **quiero** que las consultas pesadas se procesen mediante un motor de alto rendimiento detrás de una capa semántica,
- **para que** pueda cruzar variables masivas rápidamente y el agente componga consultas válidas por construcción.

**Criterios de Aceptación:**

- Routers aislados por dominio: `/api/creditos`, `/api/liquidez`, `/api/derivados`, cada uno protegido por scopes (Operativo: lectura puntual; Analista: agregaciones y cruces; Directivo: resúmenes).
- **Capa semántica** (patrón SMQ §3.4): las métricas y dimensiones válidas se declaran en el catálogo; los endpoints aceptan una consulta estructurada (métrica + dimensiones + filtros + rango temporal) validada con Pydantic y un **compilador determinístico** la traduce a expresiones Polars parametrizadas. Nunca se ejecuta código libre proveniente del cliente o del LLM.
- Joins cruzados entre silos (p. ej. exposición por contraparte: créditos ⋈ derivados) resueltos en memoria con Polars lazy.
- Errores tipificados: métrica inexistente → 422 con sugerencia del catálogo (fuzzy match).
- Pruebas: 10 consultas de referencia (Anexo C) con resultados esperados sobre la semilla fija.

**Alcance STRETCH (no comprometido, +1 SP):** agregaciones avanzadas adicionales (ventanas móviles, percentiles) expuestas como métricas del catálogo.

**Tareas técnicas:**

- [ ] Esquema Pydantic de consulta semántica + validación contra catálogo
- [ ] Compilador consulta→Polars (`ml/semantic/compiler.py`)
- [ ] Routers por dominio con dependencias de scopes
- [ ] Suite de 10 consultas de referencia con pytest

**Estimación:** 5 puntos (~2.5 días). **Sprint:** S3.

### US-012 — Búsqueda Híbrida del Catálogo (RAG plano)

**Como** operativo,
- **quiero** buscar qué datos institucionales existen usando términos de negocio aunque no coincidan literalmente,
- **para que** el sistema me devuelva el contexto exacto del catálogo (definición + dónde reside + reglas de uso).

**Criterios de Aceptación:**

- Extensión **pgvector** habilitada vía migración dbmate; embeddings del diccionario (nombre de negocio + definición + notas) almacenados por campo del catálogo.
- Búsqueda **híbrida plana**: score combinado keyword (ILIKE/tsvector) + similitud coseno; justificación explícita: para corpus tabular homogéneo el retrieval plano supera a la jerarquía (§3.5).
- `GET /api/catalog/search` migra a la búsqueda híbrida manteniendo el contrato de US-008.
- Set de evaluación de 20 consultas de negocio con fuente esperada: **Hit Rate@3 ≥ 0.8**.

**Tareas técnicas:**

- [ ] Migración dbmate pgvector + columna de embeddings
- [ ] Job de embeddings del diccionario (API de embeddings de Gemini)
- [ ] Score híbrido y ranking en el endpoint
- [ ] Set de 20 consultas + medición Hit Rate@3

**Estimación:** 3 puntos (~1.5 días). **Sprint:** S3.

### US-013 — Jerarquía Navegable para Manuales (Corpus2Skill)

**Como** analista,
- **quiero** que los manuales financieros y reglas de negocio se naveguen por una jerarquía de resúmenes en vez de retrieval plano,
- **para que** el agente aterrice mejor en corpus documental con taxonomía natural (§3.5).

**Alcance:** historia **STRETCH** — pipeline propio, distinto del RAG plano de US-012.

**Criterios de Aceptación (STRETCH, no comprometido):**

- Chunking semántico de `manuales/` y árbol de resúmenes progresivos (vista panorámica → documentos) con backtracking, tipo Corpus2Skill (§3.5).
- Coexiste con US-012: el diccionario tabular sigue en híbrido plano; solo los manuales usan jerarquía (estrategia RAG bifurcada).
- Comparación documentada contra el baseline plano en las mismas consultas de manuales.

**Tareas técnicas:**

- [ ] Chunking semántico + generación de resúmenes por nivel
- [ ] Navegación por resúmenes con backtracking
- [ ] Evaluación jerarquía vs. plano en corpus de manuales

**Estimación:** +2 STRETCH. **Sprint:** S3 (arranque) → S5.

### US-014 — RAG Relacional Cross-Silo

**Como** analista,
- **quiero** que la búsqueda enlace campos equivalentes entre silos vía los IDs de cliente compartidos,
- **para que** una consulta de negocio recupere contexto de créditos, liquidez y derivados a la vez.

**Alcance:** historia **STRETCH** — capacidad de recuperación distinta de la búsqueda intra-silo de US-012.

**Criterios de Aceptación (STRETCH, no comprometido):**

- Grafo ligero de relaciones entre campos de distintos silos (clave: `id_cliente` compartido de US-006).
- La búsqueda del catálogo sugiere "fuentes relacionadas" cruzando silos, no solo dentro de uno.
- Set de evaluación de consultas cross-silo con fuente esperada.

**Tareas técnicas:**

- [ ] Modelar relaciones cross-silo sobre el catálogo
- [ ] Extender el ranking para sugerir fuentes relacionadas
- [ ] Consultas de evaluación cross-silo

**Estimación:** +2 STRETCH. **Sprint:** S5.

### US-015 — Autenticación JWT y Login (Backend)

**Como** líder de plataforma,
- **quiero** autenticación con JWT emitida por un endpoint OAuth2 password,
- **para que** exista una identidad verificable y un token firmado sobre el cual construir el resto del gobierno de acceso.

**Criterios de Aceptación:**

- `POST /api/auth/token` implementa OAuth2 password flow según la guía oficial de FastAPI ✔C7: verificación con **pwdlib** `PasswordHash.recommended()` (argon2id, hash dummy contra timing attacks), emisión de JWT con **PyJWT** (HS256, `SECRET_KEY` de 32 bytes vía `openssl rand -hex 32` almacenado en Secret Manager, expiración 30 min, claims `sub` + `scope`).
- Tabla `app_user` (migración dbmate): `id`, `username`, `email`, `full_name`, `hashed_password`, `role`, `disabled`, `created_at`; **seed de 7 usuarios** (§9) con contraseñas Argon2.
- `get_current_user` valida firma y expiración; `get_current_active_user` rechaza usuarios `disabled` (patrón oficial ✔C7).
- Pruebas: login ok / credenciales malas / token expirado.

**Tareas técnicas:**

- [ ] Migración dbmate `app_user` + seed Argon2
- [ ] Módulo `api/auth.py`: hashing pwdlib, emisión/validación PyJWT
- [ ] Dependencias `get_current_user` / `get_current_active_user`
- [ ] Pruebas de emisión y validación de token

**Estimación:** 1.5 puntos (~0.75 día). **Sprint:** S2.

### US-016 — Autorización RBAC por Scopes (+ Herencia al Agente)

**Como** líder de plataforma,
- **quiero** que cada endpoint exija el scope del rol correspondiente y que el agente herede los permisos del usuario,
- **para que** cada perfil (Operativo, Analista, Directivo, Admin) consuma solo lo que le corresponde, incluso a través del chat.

**Criterios de Aceptación:**

- Los roles viajan como **scopes** del token (`operativo`, `analista`, `directivo`, `admin`) y los endpoints los exigen con `Security(get_current_user, scopes=[...])` → 401 sin/mal token (`WWW-Authenticate: Bearer`), 403 autenticado sin permiso.
- Matriz de permisos implementada: catálogo (todos los autenticados); consultas puntuales (operativo+); agregaciones/cruces/export (analista+); resúmenes directivos (directivo+); gestión de usuarios (solo admin). Documentada en `docs/security.md`.
- `/api/chat` propaga el token del usuario a cada tool call del agente: el agente **no puede** leer datos que el usuario no puede leer (§3.3).
- Pruebas: 401/403 por matriz de permisos parametrizado por rol; verificación de que una tool rechaza datos fuera del scope del usuario.

**Tareas técnicas:**

- [ ] Dependencias con SecurityScopes por endpoint según la matriz
- [ ] `docs/security.md` con la matriz de permisos
- [ ] Propagación del Bearer del usuario en las tools del agente (coordinada con US-021)
- [ ] Suite de pruebas de permisos por rol

**Estimación:** 1 punto (~0.5 día). **Sprint:** S2.

### US-017 — Guarda de Sesión y Ocultamiento por Rol (Frontend)

**Como** usuario del portal,
- **quiero** iniciar sesión y ver solo los módulos de mi rol,
- **para que** la interfaz sea coherente con mis permisos y no muestre lo que no puedo usar.

**Criterios de Aceptación:**

- Página de login; JWT en **cookie httpOnly**; middleware de rutas Nuxt que redirige a login sin sesión y oculta módulos según el rol del claim.
- Expiración manejada con re-login limpio (sin refresh token en MVP — decisión de alcance documentada, §21 R11).
- Estados de error de login (credenciales inválidas, sesión expirada) consistentes con el sistema de diseño.
- Prueba e2e: rutas protegidas inaccesibles sin sesión; módulos ausentes para roles sin permiso.

**Tareas técnicas:**

- [ ] Página de login + composable de sesión en Nuxt
- [ ] Middleware de rutas + cookie httpOnly
- [ ] Ocultamiento de módulos según rol del JWT
- [ ] Prueba e2e de guardas de sesión

**Estimación:** 0.5 puntos (~medio día). **Sprint:** S2.

### US-018 — CRUD de Usuarios (Backend)

**Como** administrador del portal,
- **quiero** endpoints para crear, consultar, editar y desactivar usuarios y cambiar su rol,
- **para que** el gobierno de acceso sea operable sin tocar la base de datos a mano.

**Criterios de Aceptación:**

- Endpoints REST bajo `/api/users`, todos con scope `admin`: `GET /api/users` (lista paginada con filtro por rol/estado), `POST /api/users` (alta con contraseña temporal hasheada y rol), `GET /api/users/{id}`, `PATCH /api/users/{id}` (nombre, email, rol, contraseña), `DELETE /api/users/{id}` (**soft delete**: `disabled = true`; nunca borrado físico, por auditoría).
- Reglas de negocio: un admin no puede desactivarse ni degradarse a sí mismo; `username`/`email` únicos → 409; contraseñas nunca en respuestas ni en logs.
- Cambios de rol/desactivación surten efecto en el siguiente request del afectado (se apoya en `get_current_active_user` de US-015).
- Pruebas CRUD completas por endpoint incluyendo reglas de negocio (auto-degradación, duplicados).

**Degradación acordada (válvula §10.2):** si S3 se atrasa, el MUST se reduce a alta + cambio de rol + desactivación (sin `PATCH` de edición completa), documentándolo.

**Tareas técnicas:**

- [ ] Router `api/users.py` con esquemas Pydantic (UserCreate/UserUpdate/UserOut)
- [ ] Reglas de negocio + manejo de conflictos (409) y soft delete
- [ ] Pruebas CRUD + permisos (solo admin)

**Estimación:** 1.5 puntos (~0.75 día). **Sprint:** S3.

### US-019 — Panel de Administración de Usuarios (Frontend)

**Como** administrador del portal,
- **quiero** una página para gestionar usuarios visualmente,
- **para que** pueda operar altas, cambios de rol y desactivaciones sin usar la API a mano.

**Criterios de Aceptación:**

- Página `/admin/usuarios` (visible solo para admin) con tabla paginada, alta, edición y desactivación con confirmación.
- Estados de carga, vacío y error consistentes con el sistema de diseño (A4); contraseñas nunca mostradas.
- Consumo de los endpoints de US-018; feedback de conflictos (409) y reglas de negocio en la UI.

**Degradación acordada (válvula §10.2):** si S3 se atrasa, se entrega listar + cambiar rol + desactivar (sin formulario de edición completa), en paridad con US-018.

**Tareas técnicas:**

- [ ] Página `/admin/usuarios` en Nuxt con tabla y formularios
- [ ] Manejo de estados y errores (409, validaciones)
- [ ] Prueba de componente del panel

**Estimación:** 0.5 puntos (~medio día). **Sprint:** S3.

---

## 15. EPIC 3: Agente Conversacional {#epic-3}

**Objetivo:** orquestador inteligente con Google ADK y Gemini 3.5 Flash-Lite para interactuar con los datos en lenguaje natural, con streaming cancelable. **Puntos: 11 MUST + 3 STRETCH.**

### US-020 — Agente Orquestador con Google ADK y Gemini 3.5 Flash-Lite

**Como** directivo,
- **quiero** hacerle preguntas complejas al portal (ej. "Resume el riesgo de liquidez de este mes"),
- **para que** el asistente razone y coordine herramientas para darme una respuesta analítica confiable.

**Criterios de Aceptación:**

- Agente implementado con **`LlmAgent` de Google ADK** ✔C7 (function tools Python con type hints y docstrings — ADK deriva el esquema automáticamente), razonamiento delegado a Gemini 3.5 Flash-Lite; `Runner` + `SessionService` para sesiones de conversación.
- Arquitectura **manager → workers** (§3.1): el manager rutea entre catálogo / datos / fuera-de-dominio (rechazo cortés); workers de presentación de datos y de insights.
- System prompt con **presupuesto limitado de herramientas** (máx. 5 tool calls por consulta) para evitar ciclos infinitos y controlar costo; `thinking_level: "medium"` por defecto, `"high"` solo a petición explícita del Analista.
- Toda cifra en la respuesta proviene de un tool call (regla anti-alucinación); las respuestas citan la fuente del catálogo.
- Evaluación rápida: las 9 familias del Anexo C respondidas correctamente sobre la semilla fija.

**Tareas técnicas:**

- [ ] `LlmAgent` manager + workers, instrucciones y presupuesto de tools
- [ ] Integración de sesiones (SessionService) con la sesión del portal
- [ ] Regla anti-alucinación + citación de fuente del catálogo
- [ ] Corrida de las 9 familias del Anexo C con revisión manual

**Estimación:** 4 puntos (~2 días). **Sprint:** S3.

### US-021 — Suite de Tools Gobernadas del Agente

**Como** ingeniero de agente,
- **quiero** un conjunto de tools que envuelvan endpoints FastAPI gobernados,
- **para que** el agente actúe sobre datos reales sin ejecutar código libre y respetando los permisos del usuario.

**Criterios de Aceptación:**

- Tools registradas (mínimo): `buscar_catalogo` (US-012), `consultar_metricas` (capa semántica US-011), `solicitar_export` (US-009), `resumir_vista` — **todas** envuelven endpoints FastAPI gobernados; ninguna ejecuta código libre.
- Cada tool **propaga el JWT del usuario** y hereda su scope (§3.3, US-016): una tool falla con 403 si el usuario no tiene permiso, y el agente lo comunica.
- Funciones Python tipadas (type hints + docstrings) sobre el cliente HTTP interno; ADK deriva el esquema automáticamente ✔C7.
- Pruebas por tool: contrato de entrada/salida y propagación de permisos.

**Tareas técnicas:**

- [ ] Definición de las 4 tools sobre el cliente HTTP interno
- [ ] Propagación del Bearer del usuario en cada tool (con US-016)
- [ ] Pruebas de contrato y de permisos por tool

**Estimación:** 2 puntos (~1 día). **Sprint:** S3.

### US-022 — Detección Fuera-de-Dominio (OOD) con Clasificador Ligero

**Como** líder de plataforma,
- **quiero** filtrar consultas fuera de dominio antes de invocar al LLM,
- **para que** ahorremos tokens y demos rechazos corteses e instantáneos.

**Alcance:** historia **STRETCH** — componente separable (clasificador previo al LLM).

**Criterios de Aceptación (STRETCH, no comprometido):**

- Clasificador ligero previo al LLM (patrón manager de §3.1) que detecta consultas fuera de dominio y responde con rechazo cortés sin gastar tokens de Gemini.
- Medición del ahorro de tokens vs. rutear todo al LLM (con la telemetría de US-030).

**Tareas técnicas:**

- [ ] Clasificador OOD ligero (heurístico o encoder pequeño)
- [ ] Integración como filtro previo en el manager
- [ ] Medición de ahorro de tokens

**Estimación:** +2 STRETCH. **Sprint:** S4.

### US-023 — Streaming de Respuesta y Botón de Cancelación Real (UX)

**Como** operativo,
- **quiero** ver la respuesta generarse en vivo y poder detenerla si va por mal camino,
- **para que** no pierda tiempo ni tokens esperando respuestas incorrectas.

**Criterios de Aceptación:**

- `/api/chat` emite **SSE** desde un generador asíncrono FastAPI: eventos tipados `tool_call` (anuncio + estado), `token` (texto incremental), `error`, `done`.
- Botón "Detener" visible durante la generación: al pulsarlo el cliente cierra el socket y el backend **detecta la desconexión en milisegundos y cancela la llamada al LLM** (ahorro real de tokens), registrando el evento.
- Presupuesto de latencia (§3.10): la tarjeta de tool call se emite **antes** de esperar datos (percepción de progreso); recuperación de catálogo y preparación de prompt solapadas donde sea posible; TTFT medido por evento en OTel.
- Prueba automatizada: cancelación a mitad de stream no deja tareas colgadas (verificación de cleanup de generadores).

**Alcance STRETCH (no comprometido, +1 SP):** telemetría de cancelaciones (en qué token/tool se canceló) para iterar prompts.

**Tareas técnicas:**

- [ ] Generador SSE con eventos tipados + composable `useChatStream` en Nuxt
- [ ] Captura de desconexión del cliente y cancelación de la corrida del agente
- [ ] Prueba de cancelación y cleanup

**Estimación:** 3.5 puntos (~1.75 días). **Sprint:** S3 (arranque) → S4 (cierre).

### US-024 — Manejo de Errores en el Stream y Reintento

**Como** usuario del agente,
- **quiero** que si algo falla a mitad de respuesta pueda reintentar sin perder la conversación,
- **para que** un error transitorio no me obligue a empezar de cero.

**Alcance:** historia separada de US-023 por ser un flujo de UX propio (error contextual + reintento).

**Criterios de Aceptación:**

- Si un tool call o la API de Gemini falla a mitad de respuesta, el chat muestra el **error contextual** (qué paso falló) y un botón **Reintentar** sin borrar la conversación.
- Diferencia error recuperable (reintentar) de error de permiso (403 → mensaje de rol insuficiente, sin reintento).
- Prueba: fallo inyectado en un tool call → UI de error + reintento exitoso.

**Tareas técnicas:**

- [ ] Evento `error` tipado del SSE mapeado a UI contextual
- [ ] Botón Reintentar que reanuda sin resetear el historial
- [ ] Prueba de fallo inyectado y reintento

**Estimación:** 1.5 puntos (~0.75 día). **Sprint:** S4.

---

## 16. EPIC 4: Frontend y Dashboards {#epic-4}

**Objetivo:** interfaz Nuxt 4 con renderizado híbrido y los patrones UX comprometidos (§6.2) sobre datos de alto volumen. **Puntos: 9 MUST + 7 STRETCH.**

### US-025 — Dashboard de Alto Rendimiento (Nuxt 4 + Apache ECharts)

**Como** analista,
- **quiero** visualizar volúmenes masivos de datos financieros en gráficos interactivos sin congelar la pantalla,
- **para que** pueda hacer análisis profundo con fluidez.

**Criterios de Aceptación:**

- Consumo de datos con `useFetch` aprovechando el **`shallowRef` por defecto de Nuxt 4** (sin reactividad profunda sobre payloads masivos).
- Componentes pesados envueltos con prefijo **`Lazy`** (`<LazyVChart/>`, modales) — fuera del bundle inicial, mejorando Time to Interactive.
- **SWR** vía `routeRules` en las rutas del dashboard directivo (carga percibida instantánea + revalidación).
- Una vista demo con serie de **≥1 M de puntos** fluida (pan/zoom sin jank), usando agregación server-side Polars + `sampling`/`large` de ECharts; degradación acordada: 500 K pre-agregados si el gate de rendimiento falla (§10.2).
- Interacciones de drill-down emiten eventos al store Pinia (base del estado compartido con el chat, §3.6).

**Alcance STRETCH (no comprometido, +2 SP):** virtualización de tablas del explorador (scroll de 100 K filas).

**Tareas técnicas:**

- [ ] Configurar `routeRules` SWR + rutas por rol
- [ ] Componentes ECharts lazy con props tipadas (serie temporal, barras, heatmap)
- [ ] Endpoint de agregación server-side para la vista de 1 M puntos
- [ ] Medición de fluidez (frame drops) en la vista demo

**Estimación:** 3 puntos (~1.5 días). **Sprint:** S4.

### US-026 — Revelación Progresiva y Tarjetas Predictivas

**Como** directivo,
- **quiero** un dashboard que muestre primero resúmenes y previsiones antes de datos técnicos,
- **para que** mi carga cognitiva sea mínima y profundice solo si lo decido.

**Criterios de Aceptación:**

- **Predictive Insight Cards** en la vista principal directiva: previsiones simuladas con etiqueta clara de método (ej. "Riesgo de liquidez +12 % próximo mes — proyección lineal sobre sintéticos"), sin fingir ML real (honestidad de demo).
- **Progressive disclosure**: tarjeta → panel expandible con la serie ECharts → tabla de detalle → enlace al explorador (3 niveles, ≤2 clics entre niveles).
- Estados de carga skeleton y vacíos diseñados (sin layout shift).

**Tareas técnicas:**

- [ ] Sistema de tarjetas resumen + paneles expandibles
- [ ] Cálculo de previsiones simuladas server-side (Polars)
- [ ] Estados skeleton/vacío/error de cada módulo

**Estimación:** 2 puntos (~1 día). **Sprint:** S4.

### US-027 — Workspaces Configurables por Rol

**Como** usuario del portal,
- **quiero** que mi home muestre por defecto los módulos de mi perfil,
- **para que** encuentre primero lo que uso sin configurar nada, con opción de ajustarlo.

**Criterios de Aceptación:**

- **Workspaces por rol** (§3.9): configuración default de módulos por perfil (Operativo: buscador arriba; Analista: explorador + exportaciones; Directivo: tarjetas + resumen del agente); el rol viene del JWT (US-016).
- Fundamento empírico documentado: sin consenso experto sobre "buen layout" (kappa 0.25, §3.9), se parte de defaults por rol en vez de una vista única.

**Alcance STRETCH (no comprometido, +2 SP):** reordenamiento drag-and-drop de módulos persistido por usuario.

**Tareas técnicas:**

- [ ] Defaults de workspace por rol desde la sesión
- [ ] Layout configurable por perfil
- [ ] (STRETCH) Persistencia de reordenamiento por usuario

**Estimación:** 1 punto (~0.5 día). **Sprint:** S4.

### US-028 — Tarjetas de Visibilidad de Tool Calls

**Como** usuario del agente conversacional,
- **quiero** ver exactamente de qué base está extrayendo información la IA y en qué estado va,
- **para que** pueda auditar la respuesta antes de leer el texto y confiar en el sistema.

**Criterios de Aceptación:**

- Patrón **Tool-Call Visibility** (§3.7): por cada tool call, una tarjeta en el chat con (1) anuncio ("Consultando base de créditos…"), (2) estado de ejecución (spinner/tiempo), (3) resultado renderizado (mini-tabla o cifra) **antes** del texto generado.
- Los eventos `tool_call` del SSE (US-023) alimentan las tarjetas sin re-render del historial completo.
- Estados de la tarjeta: anuncio / ejecución / resultado / error, consistentes con el sistema de diseño.

**Tareas técnicas:**

- [ ] Componentes de tarjeta de tool call (estados: anuncio/ejecución/resultado/error)
- [ ] Interceptar eventos del agente ADK → tarjetas en vivo
- [ ] Render de resultado (mini-tabla/cifra) antes del texto

**Estimación:** 2 puntos (~1 día). **Sprint:** S4.

### US-029 — Overlay de Linaje y Estado Compartido Dashboard↔Chat

**Como** usuario del agente conversacional,
- **quiero** ver el linaje de cada respuesta y que el chat conozca el estado de mi dashboard,
- **para que** pueda auditar las fuentes y continuar el análisis sin repetir contexto.

**Criterios de Aceptación:**

- **Explainable overlay** de linaje: expandir una respuesta muestra qué tools se llamaron, con qué parámetros y de qué fuentes del catálogo salieron los datos.
- Estado compartido dashboard↔chat (§3.6): los filtros activos del dashboard viajan como contexto en la consulta; acción "Resumir vista actual" disponible desde el dashboard directivo (store Pinia de US-025).
- El overlay no altera el flujo de lectura: se despliega bajo demanda.

**Alcance STRETCH (no comprometido, +3 SP):** respuestas del agente que mutan el estado del dashboard (drill-down conversacional bidireccional completo, patrón TwinBI pleno).

**Tareas técnicas:**

- [ ] Overlay de linaje por respuesta
- [ ] Serialización del estado del dashboard como contexto del chat
- [ ] Acción "Resumir vista actual" desde el dashboard directivo

**Estimación:** 1 punto (~0.5 día). **Sprint:** S4.

---

## 17. EPIC 5: Observabilidad, Pruebas y Producción {#epic-5}

**Objetivo:** llamadas al LLM medibles y auditables (FinOps + privacidad), y despliegue final verificado en GCP. **Puntos: 9 MUST + 7 STRETCH.**

### US-030 — Trazabilidad End-to-End LLM y FinOps de Tokens

**Como** ingeniero de plataforma,
- **quiero** trazabilidad total sobre cada petición a Gemini con su consumo de tokens,
- **para que** pueda auditar latencias y costo exacto en producción.

**Criterios de Aceptación:**

- Sobre la base de US-005, jerarquía de sub-spans por solicitud de chat: `rag.retrieval` (búsqueda de catálogo), `llm.call` (llamada a Gemini), `llm.postprocess` (formateo/citas), aislando cuellos de botella.
- El span `llm.call` captura semántica FinOps: `llm.usage.prompt_tokens`, `llm.usage.completion_tokens`, `llm.usage.total_tokens`, `llm.model` (identificador de Gemini 3.5 Flash-Lite) y `llm.tool_calls.count`.
- TTFT registrado como atributo por solicitud de streaming (fuente de la métrica de US-034).

**Alcance STRETCH (no comprometido, +2 SP):** desglose de costo por rol de usuario y por familia de pregunta (Anexo C).

**Tareas técnicas:**

- [ ] Sub-spans en el pipeline del agente + atributos `set_attribute` de tokens
- [ ] Registro de TTFT por evento de streaming
- [ ] (STRETCH) Desglose por rol y por familia de pregunta

**Estimación:** 2.5 puntos (~1.25 días). **Sprint:** S5.

### US-031 — Privacidad de Trazas (Hash de Prompts)

**Como** responsable de gobernanza,
- **quiero** que ningún contenido crudo de prompt o respuesta quede en trazas ni logs,
- **para que** la observabilidad no viole la privacidad de los datos financieros.

**Criterios de Aceptación:**

- El contenido crudo de prompt/respuesta **NO** se guarda en trazas ni logs; se almacena `llm.prompt_hash` (SHA-256) para correlación.
- Hash calculado en el punto único de salida a Gemini; verificación automatizada de que ningún log imprime contenido crudo.

**Tareas técnicas:**

- [ ] Hash SHA-256 de prompts en el punto único de salida a Gemini
- [ ] Prueba que falla si algún log emite contenido crudo

**Estimación:** 1 punto (~0.5 día). **Sprint:** S5.

### US-032 — Tablero de Consumo y Costo

**Como** líder de plataforma,
- **quiero** un tablero de consumo de tokens y costo,
- **para que** el FinOps del proyecto sea visible y citable en la entrega final.

**Criterios de Aceptación:**

- Tablero simple (Cloud Monitoring o notebook) con: tokens/día, costo estimado/día, p50/p95 de `llm.call` (fuente: US-030).
- Cifras exportables como evidencia para A5 y §23 (FinOps).

**Tareas técnicas:**

- [ ] Consulta de métricas OTel → tablero
- [ ] Cálculo de costo estimado por día
- [ ] Exportar cifras para A5/§23

**Estimación:** 1.5 puntos (~0.75 día). **Sprint:** S5.

### US-033 — Pruebas Finales, Cobertura y Smoke Tests

**Como** equipo,
- **quiero** automatizar las pruebas finales del sistema,
- **para que** el demo sea resiliente y regresiones queden atrapadas antes del deploy.

**Criterios de Aceptación:**

- Cobertura de pruebas: ≥70 % backend (auth, capa semántica, export), componentes críticos del frontend con Vue Test Utils.
- Smoke tests post-deploy: login, búsqueda de catálogo, consulta semántica, chat con tool call, export — verdes en el pipeline.

**Tareas técnicas:**

- [ ] Completar cobertura backend a ≥70 %
- [ ] Componentes críticos de frontend con Vue Test Utils
- [ ] Smoke tests E2E en el pipeline

**Estimación:** 2 puntos (~1 día). **Sprint:** S5.

### US-034 — Pase a Producción y Medición de Latencia (TTFT/P90)

**Como** equipo,
- **quiero** desplegar a Cloud Run con métricas de latencia confirmadas,
- **para que** las cifras de UX sean reales y citables en la entrega final.

**Criterios de Aceptación:**

- Ambos contenedores desplegados en Cloud Run con **scale-to-zero**; migraciones dbmate aplicadas por el pipeline antes del deploy.
- **TTFT p50 < 700 ms** en respuestas streaming del agente (metodología de percentiles de §3.10 sobre ≥50 corridas) y P90 de consulta completa < 15 s (§3.1); resultados documentados para A5.
- Cold starts monitoreados y decisión documentada (aceptar vs. `min_instances=1` solo el día de la demo/pruebas de usabilidad).

**Alcance STRETCH (no comprometido, +1 SP):** prueba de carga ligera (k6/Locust, 20 usuarios concurrentes) con reporte.

**Tareas técnicas:**

- [ ] Ajustar triggers de deploy + paso de migraciones
- [ ] Script de medición TTFT/P90 (50 corridas, percentiles)
- [ ] Registro de cold starts y decisión para el día de demo

**Estimación:** 2 puntos (~1 día). **Sprint:** S5.

### US-035 — Harness de Evaluación del Agente (LLM-as-Judge)

**Como** equipo,
- **quiero** un harness que puntúe automáticamente las respuestas del agente,
- **para que** la calidad conversacional sea medible y no solo anecdótica.

**Alcance:** historia **STRETCH** — evaluación automática acotada a un set de 30–50 pares (el benchmark masivo quedó descartado, §18).

**Criterios de Aceptación (STRETCH, no comprometido):**

- Set de 30–50 pares de evaluación (pregunta → respuesta/fuente esperada) sobre la semilla fija.
- Juez LLM que puntúa exactitud y grounding; reporte agregado por familia de pregunta (Anexo C).

**Tareas técnicas:**

- [ ] Construir el set de 30–50 pares
- [ ] Prompt de LLM-as-judge + agregación
- [ ] Reporte por familia de pregunta

**Estimación:** +2 STRETCH. **Sprint:** S5.

### US-036 — Análisis de Casos de Falla (Ciclo Tk-Boost)

**Como** ingeniero de agente,
- **quiero** analizar los errores del agente y convertirlos en conocimiento correctivo,
- **para que** el catálogo tribal y los prompts mejoren con la experiencia (§3.2).

**Alcance:** historia **STRETCH** — aplica el ciclo experiencia→misconception→conocimiento de Tk-Boost (§3.2).

**Criterios de Aceptación (STRETCH, no comprometido):**

- Recopilación de casos de falla del harness de US-035; clasificación de misconceptions del agente sobre los datos.
- Conocimiento correctivo indexado con condición de aplicabilidad en el catálogo tribal (US-008).

**Tareas técnicas:**

- [ ] Pipeline de recolección y clasificación de fallas
- [ ] Generación de notas tribales correctivas con condición de aplicabilidad
- [ ] Re-evaluación tras inyectar el conocimiento

**Estimación:** +2 STRETCH. **Sprint:** S5.

---

## 18. Alcance Descartado (fuera del curso) {#consolidacion}

El catálogo vigente (US-001…US-036 + US-UX-01…08) es el alcance completo del proyecto. Lo siguiente se evaluó y se **descartó explícitamente** por estar fuera del alcance del curso — no son US faltantes, son decisiones de alcance firmadas por el equipo:

| Trabajo descartado | Razón de descarte |
|--------------------|-------------------|
| Switch A/B de modelos LLM (selector Gemini vs. alternativas) | No lo pide ninguna actividad UX; valioso pero fuera del MVP |
| Detección de drift (Evidently) | Trabajo de un curso de ML/producción, no de UX |
| RLS a nivel fila e i18n | Seguridad/internacionalización de producción real, post-curso |
| Paper académico + benchmark de 500 Q&A | Post-curso; la evaluación del agente se reduce a 30–50 pares en US-035 |
| Refresh tokens, recuperación de contraseña, OAuth/SSO externo | Alcance de seguridad cerrado en US-015…019 (ver R11, §21); documentado como trabajo futuro en `docs/security.md` |

> Si algo de esta lista se vuelve necesario, entra por refinamiento formal: nueva US numerada al final del catálogo (US-037+), con criterios, SP y sprint — nunca como trabajo silencioso.

### 18.1 Cobertura de lo comprometido en A1 y A2 por el catálogo técnico (29-jul-2026)

A1 cerró con una matriz pain point → necesidad → característica → persona, y A2 con otra que traza cada punto de fricción hasta la característica que lo implementa y la forma en que se verificará. Esas dos matrices son **compromisos de producto ante el evaluador**: en A4 y A5 se puede contrastar lo prometido contra el prototipo. Este es el resultado de cruzarlas con el catálogo US-001…036.

| Característica comprometida en A1/A2 | Dónde se prometió | Cobertura en el catálogo |
|--------------------------------------|-------------------|--------------------------|
| Acceso por permisos y roles, permiso mínimo suficiente | A2 etapa 2 · escenario 5 (Mariana) | ✅ US-015/016/017 + US-018/019 |
| Buscador unificado con fuente, propietario, periodicidad y vigencia en la tarjeta | A2 etapa 3 · escenario 1 (Laura) | ✅ US-008 (criterio explicitado el 29-jul) |
| Ficha con definición oficial, notas tribales y responsable | A2 etapa 4 · escenario 4 (Roberto) | ✅ US-008 |
| Marca de versión retirada con enlace a la vigente | A2 etapas 3, 4 y 7 · escenarios 4 y 6 | ✅ **Absorbido en US-008 el 29-jul** (+0.5 SP) |
| Copiado con procedencia por omisión | A2 etapa 6 · principio "Respaldado" | ✅ **Absorbido en US-008 el 29-jul** (+0.5 SP) |
| Asistente que cita la herramienta consultada antes de responder | A2 etapa 5 · patrón de visibilidad | ✅ US-021 + US-028 |
| Revelación progresiva y tarjetas con señal predictiva | A2 patrones · escenario 3 (Arturo) | ✅ US-026 |
| Espacios de trabajo por rol | A2 patrones · escenarios 1, 3 y 6 | ✅ US-027 |
| Estado compartido entre tablero y asistente | A2 escenario 3, etapa 5 | ✅ US-029 |
| Exportación pesada sin bloquear la interfaz | A1 (Diego) · escenario 2 | ✅ US-009 |
| Consumo por API con contrato documentado | A1 (Ximena) · escenario 6 | ✅ Parcial: el contrato lo da OpenAPI de FastAPI; **las credenciales autogestionadas no están** → US-040 |
| **Consultas guardadas y reutilizables** | A2 etapas 1 y 7 · escenario 1 | ❌ **No estaba en el catálogo** → US-037 |
| **Aviso dirigido a quien tiene la fuente guardada cuando cambia la definición** | A2 etapa 7 · escenarios 4 y 6 · principio "Sin sorpresas" | ❌ **No estaba** → US-038 |
| **Comparación lado a lado de variables legítimamente similares** | A2 etapa 3, excepción del escenario 1 | ❌ **No estaba** → US-039 |
| **Bitácora de accesos y evidencia descargable** | A1 (Elena, control y auditoría) · escenario 3 | ❌ **No estaba** → US-041 |

**Decisión de alcance (29-jul).** Las dos capacidades más baratas y de mayor peso narrativo se **absorbieron en US-008** porque son atributos de un catálogo que hay que seedear de todos modos. Las cinco restantes se numeran aquí para que existan y sean trazables, pero quedan **declaradas como roadmap y NO comprometidas**: con el déficit real de −22 SP (§10.2.b) comprometerlas sería incumplir por escrito. La regla que las gobierna es la de §18: entran por refinamiento formal, nunca como trabajo silencioso.

**Y la obligación que sí se asume:** en la tabla de paridad de A4 (US-UX-07) estas cinco aparecen marcadas como *roadmap declarado*, no se omiten. Un evaluador que compare las oportunidades del journey con el prototipo debe encontrar la respuesta en el documento, no un hueco.

#### US-037 — Consultas guardadas (roadmap, no comprometida)

**Como** usuario operativo, **quiero** guardar una consulta con sus filtros y nombre propio, **para que** la tarea recurrente empiece resuelta a medias en lugar de reconstruirse cada vez. Requiere tabla `saved_query` (usuario, nombre, silo, filtros, fecha) + endpoints CRUD con scope propio + listado visible al abrir el espacio de trabajo. **Estimación: 2 SP.** Prerrequisito de US-038. Es la etapa 1 y la 7 del journey de equipo.

#### US-038 — Aviso dirigido por cambio de versión (roadmap, no comprometida)

**Como** usuario que guardó una fuente, **quiero** enterarme de que su definición cambió antes de volver a usarla, **para que** dos áreas no presenten cifras distintas semanas después. Requiere el versionado de US-008 (ya absorbido) + las consultas guardadas de US-037 + una bandeja de avisos por usuario. **Estimación: 2 SP.** Es el problema más caro que A2 identificó y el que sostiene el principio "Sin sorpresas"; también el supuesto con menos evidencia documental de los tres declarados en A2, así que conviene verificarlo antes de construirlo.

#### US-039 — Comparación lado a lado de variables similares (roadmap, no comprometida)

**Como** usuario que encuentra dos variables de nombre parecido, **quiero** verlas juntas con sus diferencias y propietarios, **para que** la desambiguación no dependa de adivinar. Vista de dos fichas del catálogo en paralelo con las diferencias resaltadas. **Estimación: 1 SP.** Sostiene el antiprincipio "Autoritario" (el sistema no decide por el usuario ante una ambigüedad legítima).

#### US-040 — Credenciales de integración autogestionadas (roadmap, no comprometida)

**Como** perfil de integración, **quiero** generar y rotar mis credenciales de API desde mi perfil, **para que** conectar un proceso no dependa de un ticket. Requiere tabla de tokens de servicio, alta/revocación y documentación del contrato. **Estimación: 2 SP.** Nota de seguridad: toca el alcance de autenticación que R11 declaró cerrado en US-015…019, así que su reentrada exige revisión de seguridad explícita (§`docs/security.md`).

#### US-041 — Bitácora de accesos y evidencia descargable (roadmap, no comprometida)

**Como** perfil de control y auditoría, **quiero** un reporte de trazabilidad con quién accedió a qué y cuándo, **para que** la evidencia no se reconstruya con cadenas de correos. Requiere tabla de bitácora append-only + endpoint de consulta con scope de auditoría + exportación. **Estimación: 3 SP.** Es la característica de Elena en la matriz de A1 y la de mayor costo de las cinco; con el tiempo disponible, se declara roadmap y en A4 se muestra como pantalla de diseño.

---

## 19. Roadmap Semanal de Sprints {#19-roadmap}

### Sprint 1 — lun 20 al dom 26 de julio · **ACTIVIDAD 1** (en curso)

**Objetivo:** Entregable A1 con excelencia + base técnica levantada. **SP:** 11 UX (US-UX-01…04) + 8 técnicos (US-001…005 + US-006 v0) = 19.

| Día | Actividad |
|-----|-----------|
| Lun 20 – Mié 22 | Kickoff: confirmar roles y nombre del producto; diseñar los instrumentos (US-UX-01); US-001 `make dev` |
| Jue 23 | Redacción secciones de equipo (US-UX-02); US-004 CI mínimo; gate de acceso a Gemini + ADK hello tool; borrador de personas con datos parciales |
| Vie 24 | Decisión de método: **usuarios prototipo** en lugar de campo aplicado; personas v1 (US-UX-03); US-006 generadores sintéticos v0; US-005 OTel base |
| Sáb 25 | Última entrevista; 6 mapas de empatía (US-UX-04); integración del PDF; revisión cruzada contra rúbrica §2.2 (checklist §24) |
| **Dom 26** | Ajustes finales + **entrega "Entregable Actividad 1_equipo_8.pdf" en Canvas antes de 23:59** |

### Sprint 2 — lun 27-jul al dom 2-ago · Actividad 2 (Journey Maps)

**Objetivo:** A2 entregada + silos, catálogo, exportación y **login JWT** operativos. **SP:** 5 UX (US-UX-05) + 11 técnicos (US-006 cierre 1, US-007 1, US-008 3, US-009 3, **US-015/016/017 auth+RBAC+sesión 3**) = 16.
Al recibir la rúbrica de A2: protocolo §25.2 (1 h, ajustar US-UX-05). Los journey maps usan los flujos reales §8.1 (ya con login como primera etapa del journey).
**Dom 2-ago: entrega A2.**

> **Cierre real de S2 (actualizado 29-jul).** La parte UX se cumplió y se excedió: A2 quedó terminada con 6 escenarios y 4 journey maps, y la rúbrica se absorbió el 29-jul (§2.3). **Los 11 SP técnicos no se ejecutaron**: cero código. La secuencia de arranque se reprograma a la cola de la semana, con la regla de oro intacta — el domingo es solo para la entrega.
>
> | Día | Arthur (Platform/Agent) | Alexandro (Frontend/UX) | Jacqueline (Research/Data) |
> |-----|-------------------------|-------------------------|----------------------------|
> | **Jue 30** | **US-001**: `Makefile`, `docker-compose.yml` (backend/frontend/postgres con imagen pgvector), `backend/pyproject.toml`, `pnpm dlx nuxi init frontend`, `.env.example`, `backend/app/core/config.py` con Pydantic Settings estricto. Gate: `make dev` arriba. Instalar `gitleaks` (sin él `make check` no corre su secrets-scan) y resolver el pin de pnpm sin corepack | Estética y principios rectores del mapa | Introducción y método de A2 |
> | **Vie 31** | **US-002** + las 3 migraciones en orden (`create_catalog` → `create_app_user` → `create_export_job`), `make db-up`, `db/schema.sql` commiteado. **Spike ADK "hello tool" (45 min)**: es el gate vencido del 23-jul y el go/no-go del fallback de R04 | Exportar el mapa, verificar legibilidad impresa | **US-006 v0**: `ml/data/generators.py` con semilla fija, `make data`, `data/README.md` con las anomalías |
> | **Sáb 1** | Revisión cruzada de A2 (bloque intocable). Solo si A2 quedó cerrado: arranque de `backend/app/core/auth.py` | Revisión cruzada | Revisión cruzada |
> | **Dom 2** | **Entrega A2 en Canvas, objetivo 20:00. Cero código.** | | |
>
> Gate re-fechado: `dbmate up` con `schema.sql` idéntico en las 3 máquinas pasa del **mié 30-jul** al **dom 2-ago**.

### Sprint 3 — lun 3 al dom 9-ago · Actividad 3 (Competitivo + IA) — **sprint crítico**

**Objetivo:** A3 entregada + capa semántica, búsqueda híbrida, **CRUD de usuarios** y agente v1. **SP:** 4 UX (US-UX-06) + 16 técnicos (US-011 5, US-012 3, **US-018/019 usuarios 2**, US-020/021 agente 6) = 20 (−5, el más sobrecomprometido).
Mitigaciones: benchmark competitivo repartido entre los 3 en paralelo; US-020/021 arrancan con las tools de catálogo (US-008 ya listo desde S2); válvula: degradación acordada de US-018/019 (§10.2). El sitemap de A3 incorpora el mapa de permisos (US-016) como evidencia de IA por roles.
**Dom 9-ago: entrega A3.**

> **Replanificación de S3 (29-jul): es la semana barata para el código y hay que aprovecharla.** A3 es la actividad menos dependiente de implementación —benchmark, sitemap y card sorting son trabajo de escritorio—, así que absorbe el arranque atrasado. **Lunes primero: revisar Canvas; si la rúbrica de A3 está publicada, aplicar §25.2 antes de cualquier trabajo de A3.**
>
> | Día | Arthur | Alexandro | Jacqueline |
> |-----|--------|-----------|------------|
> | **Lun 3** | **US-015**: `/api/auth/token`, seed de 7 usuarios Argon2, `get_current_active_user`, tests login ok/malo/expirado | Capturar los 4–6 referentes del benchmark | Instrumento de card sorting + taxonomía exportada del seed real |
> | **Mar 4** | **US-016**: `Security(scopes)` en todos los routers + **`docs/security.md`** + suite 401/403 por rol. **Ese archivo ES la evidencia de arquitectura de información de A3** | **US-017**: `pages/login.vue`, middleware global, cookie httpOnly | **Seed del catálogo**: 200–400 entradas + ~30 notas tribales |
> | **Mié 5** | **US-008** endpoint keyword (ILIKE/tsvector) + tests · **US-007** conectores async | `pages/catalogo.vue`: buscador + tarjetas con fuente, dueño y vigencia | Ejecutar card sorting (≥6 colegas, o PerceptUI declarando el método) |
> | **Jue 6** | **US-011 v0**: `ml/semantic/compiler.py`, 3 métricas + 1 join, 3 consultas de referencia | Sitemap y flujos por rol derivados de `docs/security.md` | Matriz comparativa del benchmark |
> | **Vie 7** | Integrar A3 reusando `docs/entregables/estilo/uxdoc.sty`; insertar capturas de login y catálogo como "arquitectura implementada" | | |
> | **Sáb 8** | Revisión cruzada | | |
> | **Dom 9** | **Entrega A3, 20:00** | | |
>
> Congelado en esta semana: US-012 y pgvector (recorte 1 de §10.2.b), US-013, US-014; US-018/019 se mueven a S4 con su degradación acordada.

> **Cierre real de S3 (10-ago-2026).** La pista UX cumplió y excedió: **A3 entregada el 9-ago** con los 26 pasos de la rúbrica cubiertos, benchmark de 6 alternativas con datos verificados, card sorting ejecutado con 8 evaluadores prototipo y análisis reproducible, arquitectura de 4 categorías con 9 facetas y prueba de árbol que refutó una hipótesis del equipo y produjo un cambio aplicado (US-UX-06). **Los 16 SP técnicos no se ejecutaron: cero código, por tercer sprint consecutivo.** El gate del jue 6-ago (`docs/security.md`) venció sin cumplirse y con él se perdió el diferenciador de "arquitectura implementada"; el sitemap se construyó desde el card sorting, que era el plan B previsto. La semana barata para el código se gastó, en cambio, en levantar la calidad del entregable tras absorber la rúbrica el mismo domingo.

### Sprint 4 — lun 10 al dom 16-ago · Actividad 4 (Alta Fidelidad)

**Objetivo:** A4 entregada + frontend completo con patrones UX. **SP:** 5 UX (US-UX-07) + 14 técnicos (US-023/024 streaming cierre 5, US-025 3, US-026/027 3, US-028/029 3) = 19 (−4).
Mitigaciones: Figma y Nuxt comparten sistema de diseño (sin doble trabajo); capturas del prototipo reducen pantallas dibujadas; pre-validación sintética jue–vie.
**Dom 16-ago: entrega A4.**

> **S4 es la semana que decide el proyecto (29-jul).** La mitigación declarada del déficit de S4 es literalmente "las capturas del prototipo reducen las pantallas dibujadas". Si el frontend no corre, **esa mitigación se invierte**: habría que dibujar más en Figma en la semana que ya iba corta, y se pierden el criterio de paridad de US-UX-07, la pre-validación PerceptUI sobre pantallas reales y los patrones 3, 4 y 6 de §6.2, que solo se demuestran en movimiento. Es la única semana donde dos días de retraso son irrecuperables.
>
> | Día | Arthur | Alexandro | Jacqueline |
> |-----|--------|-----------|------------|
> | **Lun 10** | **US-020 + US-021**: `LlmAgent` manager + tools `buscar_catalogo` y `consultar_metricas` con Bearer propagado | Tokens de Figma **derivados** de `frontend/app/assets/css/main.css`, no al revés | Protocolo PerceptUI + contenido de las tarjetas predictivas |
> | **Mar 11** | **US-023**: `/api/chat` SSE con eventos tipados + cancelación por desconexión | **US-027** homes por rol + **US-025** `LazyVChart` sobre endpoint de agregación | Endpoint de proyección simulada de US-026, etiquetada "proyección simulada" |
> | **Mié 12** | Test de cleanup de generadores · **US-029** overlay de linaje | **US-028** tarjetas de tool call en sus 4 estados | **US-019** panel admin degradado |
> | **Jue 13** | **Congelamiento de pantallas para captura.** Los tres capturan el set completo: login, homes por rol, catálogo, dashboard con drill-down, chat en los 4 estados, flujo de export, `/admin/usuarios`. **Pre-validación PerceptUI sobre capturas reales, no mockups** | | |
> | **Vie 14** | Aplicar una iteración documentada de PerceptUI; maquetar A4; **tabla de paridad pantalla-Figma ↔ ruta Nuxt** marcando como *roadmap* lo que quede solo en diseño. **12:00 — punto de decisión sobre el alcance del SUS de A5** | | |
> | **Sáb 15** | Revisión cruzada | | |
> | **Dom 16** | **Entrega A4, 20:00** | | |
>
> Válvulas de esta semana, en orden: 500 K en lugar de 1 M → US-024 sin Reintentar → US-019 solo en Figma → US-026 a 2 niveles de revelación.

> **Replanteo de S4 (10-ago-2026): la semana se reorganiza alrededor del prototipo navegable.** El plan de arriba asume un backend y un frontend que no existen, así que se sustituye. El objetivo de la semana ya no son 14 SP técnicos repartidos en siete historias, sino **un artefacto: la página con las 5 interfaces de alta fidelidad explorables** (US-UX-07), que es a la vez el entregable de A4 y el objeto de prueba de A5. **SP:** 5 UX + ~8 de construcción del prototipo = 13, dentro de la capacidad de 15 por primera vez en el proyecto.
>
> | Día | Trabajo |
> |-----|---------|
> | **Lun 10** | Tokens de diseño derivados de `uxdoc.sty` (paleta, tipografía, escala, radios, estados); esqueleto navegable con las 5 rutas y la barra lateral de dos niveles que el mapa de A3 fijó; confirmar el set de 5 interfaces con el equipo |
> | **Mar 11** | Interfaces 1 (Inicio) y 2 (Exploración y extracción, con tableros e indicadores en 2.4 y drill-down) |
> | **Mié 12** | Interfaces 3 (Gobierno del dato, con overlay de linaje) y 5 (Administración) |
> | **Jue 13** | Interfaz 4 (Asistente conversacional) con los 4 estados de la tarjeta de tool call y el streaming simulado con Stop. **Congelamiento para pre-validación.** |
> | **Vie 14** | **Pre-validación sintética sobre las pantallas navegables** con las 8 personas; aplicar **≥1 iteración documentada**; maquetar A4 con la tabla de alcance (navegable con datos / navegable sin datos / roadmap). **12:00 — punto de decisión sobre el alcance del SUS de A5** |
> | **Sáb 15** | Revisión cruzada contra la rúbrica de A4 en cuanto se publique (§25.2) |
> | **Dom 16** | **Entrega A4, 20:00** |
>
> Válvulas de esta semana, en orden: los 4 estados de la tarjeta de tool call se muestran como galería en lugar de secuencia animada → el drill-down del tablero se reduce a 2 niveles → la interfaz 5 (Administración) se entrega en un solo nivel. **Lo que no se sacrifica:** las 5 interfaces navegables y la iteración documentada de pre-validación, porque son los dos criterios que ninguna otra evidencia sustituye.

### Sprint 5 — lun 17 al dom 23-ago · Actividad 5 (Entrega Final)

**Objetivo:** A5 entregada con métricas reales de producción. **SP:** 3 UX (US-UX-08) + 9 técnicos (US-030/031/032 observabilidad 5, US-033/034 pruebas+prod 4) = 12 (+3 buffer que absorbe arrastre de S3/S4).
Pruebas de usabilidad (≥5 usuarios, SUS) sobre el deploy de Cloud Run; documento final integrador; video demo 3 min; presentación.
**Dom 23-ago: entrega final.**

> **S5 y el riesgo contraintuitivo (29-jul).** Sin prototipo desplegado no hay prueba SUS ni cifras de §22.3. Pero el riesgo simétrico debe decirse: **un prototipo inestable puntúa peor en SUS que un prototipo de Figma limpio**. Un cold start, un stream que se corta o un 500 en medio de una tarea bajan el SUS por debajo de 75 y el hallazgo queda escrito en el entregable final.
>
> | Día | Trabajo |
> |-----|---------|
> | **Lun 17** | **Congelamiento de funcionalidad.** Arthur: puente `gcloud run deploy` (US-003 recortada) + **US-034** + **US-030/031**; `min_instances = 1` durante los días de prueba. Alexandro: solo defectos bloqueantes. Jacqueline: reclutar ≥5 participantes y cerrar el protocolo de 3 tareas por perfil |
> | **Mar 18** | Smoke tests (login, catálogo, consulta semántica, chat con tool call, export). **Ensayo de la sesión** con un integrante de conejillo: mide la duración real y caza el fallo tonto antes del primer participante |
> | **Mié 19 – Vie 21** | **5+ sesiones moderadas + SUS** (2/2/1), moderador y tomador de notas. En paralelo: medición de TTFT p50/p90 sobre ≥50 corridas y cifras de tokens y costo |
> | **Sáb 22** | Hallazgos priorizados por severidad × frecuencia; documento final integrador A1→A5; video demo de 3 min |
> | **Dom 23** | **Entrega final, 20:00** + presentación |
>
> Sacrificios explícitos de S5, por escrito: US-012, US-013, US-014, US-022, US-032 completa, US-035, US-036, Terraform más allá del puente, y todo `+N STRETCH`.
>
> **Los tres compromisos que sostienen el calendario entero:** `make dev` funcionando el **jue 30-jul** · login JWT end-to-end el **mar 4-ago** · pantallas congeladas para captura el **jue 13-ago**.

### Balance de capacidad

| Sprint | SP plan | Capacidad | Buffer | Mitigación |
|--------|---------|-----------|--------|------------|
| S1 | 19 | 15 | −4 | Plan/investigación ya arrancados; plantillas listas en anexos |
| S2 | 16 | 15 | −1 | Journey maps reutilizan escenarios §8.1; auth sigue la guía oficial FastAPI (bajo riesgo) |
| **S3** | **20** | **15** | **−5 (CRÍTICO)** | Benchmark paralelizado; catálogo listo desde S2; degradación acordada de US-018/019 |
| S4 | 19 | 15 | −4 | Sistema de diseño único Figma↔Nuxt; capturas del prototipo |
| S5 | 12 | 15 | +3 | Buffer que absorbe arrastre |
| **Total** | **86** | **75** | **−11** | Los −11 viven en STRETCH congelados + degradaciones acordadas (§10.2); el MUST duro cabe en 75 si se ejecutan las válvulas |

---

## 20. Gates del Calendario Completo {#20-gates}

Estado verificado al 10-ago-2026. La columna Estado se mantiene actualizada: un gate vencido sin cumplir no se borra, se re-fecha con su nueva fecha comprometida.

| Día | Gate | Criterio de éxito | Estado |
|-----|------|-------------------|--------|
| Mié 22-jul | Encuesta publicada y distribuida en ≥3 canales | Primeras 5 respuestas registradas | ➖ **Sustituido por decisión de método**: se optó por usuarios prototipo (US-UX-01); la encuesta queda diseñada y lista para aplicar |
| Jue 23-jul | Acceso a Gemini 3.5 Flash-Lite verificado (API key en Secret Manager / .env.local) | Respuesta a prompt de prueba con conteo de tokens | ❌ **Vencido** → re-fechado **vie 31-jul** |
| Jue 23-jul | Google ADK "hello tool" local (`LlmAgent` + function tool dummy) | Tool call ejecutado con traza visible | ❌ **Vencido** → re-fechado **vie 31-jul**. Es el go/no-go del fallback de R04: si ADK no arranca, se decide ahí el SDK GenAI directo, no en la semana de A4 |
| Vie 24-jul | `make dev` reproducible en las 3 máquinas (pnpm + Poetry lockfiles) | FastAPI + Nuxt + Postgres arriba en los 3 entornos | ❌ **Vencido** → re-fechado **jue 30-jul** (compromiso duro) |
| Vie 24-jul | Corte de encuesta n≥15 + 2 de 3 entrevistas hechas | Datos suficientes para personas/mapas | ➖ **Sustituido por decisión de método** — A1 se sustentó en usuarios prototipo (documental + experiencia del equipo + observación de canales), declarado en el documento. La meta n≥15 era autoexigencia, no requisito de rúbrica |
| Sáb 25-jul | PDF A1 completo contra checklist §24 | 100 % de renglones en "Completo" | ✅ **Cumplido** |
| **Dom 26-jul** | **Entrega A1 en Canvas** | Confirmación de subida antes de 23:59 | ✅ **Cumplido** |
| Mié 30-jul | `dbmate up` con migraciones de usuarios/catálogo en las 3 máquinas | `schema.sql` idéntico en los 3 entornos | ⏳ Re-fechado **dom 2-ago** |
| **Vie 1-ago** | **Login JWT funcional end-to-end** (US-015/016/017) | Token con scope de rol; 401 sin token y 403 con rol insuficiente verificados desde el frontend | ⏳ Re-fechado **mar 4-ago** |
| **Dom 2-ago** | **Entrega A2 en Canvas** | Confirmación de subida antes de 23:59 | ✅ **Cumplido** |
| Jue 6-ago | `docs/security.md` con la matriz de permisos real | El sitemap de A3 se deriva de permisos implementados | ❌ **Vencido sin cumplir.** Se perdió el diferenciador; el sitemap se construyó desde el card sorting (plan B previsto) |
| **Dom 9-ago** | **Entrega A3 en Canvas** | Confirmación de subida antes de 23:59 | ✅ **Cumplido** (54 páginas, rúbrica de 20 pts absorbida el mismo día) |
| Lun 10-ago | Revisar Canvas por la rúbrica de A4 y aplicar §25.2 antes de trabajar | Rúbrica volcada a tabla criterio→peso→banda | ⏳ **Hoy** |

**Gates nuevos añadidos el 29-jul** (cierran las tres restricciones de fecha del calendario técnico):

| Día | Gate | Criterio de éxito |
|-----|------|-------------------|
| **Jue 6-ago** | `docs/security.md` con la matriz de permisos real | El sitemap de A3 se deriva de permisos implementados, no de hipótesis |
| **Jue 13-ago** | ~~Pantallas congeladas para captura~~ → **5 interfaces navegables terminadas** | Reformulado el 10-ago: no hay prototipo funcional del cual capturar. El criterio pasa a ser que las 5 interfaces de US-UX-07 se recorran de punta a punta y queden congeladas para la pre-validación del vie 14 |
| **Vie 14-ago 12:00** | Decisión sobre el alcance del SUS de A5 | Si el chat SSE no está estable, las tareas se limitan a catálogo + dashboard + export y el agente se muestra solo en el video |
| **Lun 17-ago** | Congelamiento de funcionalidad + deploy verificado | `min_instances = 1` y smoke tests verdes antes de la primera sesión con usuario |

---

## 21. Gestión de Riesgos {#21-riesgos}

| ID | Categoría | Riesgo | Prob. | Impacto | Mitigación |
|----|-----------|--------|-------|---------|------------|
| R01 | Curso | ~~Rúbricas A2–A5 difieren de lo asumido~~ **Materializado 3 veces y absorbido 3 veces (10-ago)** | Media | Medio | A2 absorbida el 29-jul (§2.3), A3 el 9-ago (§2.3.b), ambas sin congelar STRETCH. Quedan A4 y A5: **revisar Canvas los lunes 10 y 17-ago antes de tocar el entregable**. El patrón observado es que las rúbricas cambian la *forma* (número de piezas, pasos numerados, peso por ejercicio), no el fondo, y que el costo de absorberlas tarde es maquetar dos veces |
| R02 | Curso | ~~No juntar n≥15 respuestas de encuesta a tiempo~~ **Materializado y resuelto (29-jul)** | — | — | Se ejecutó el plan B ampliado: método de **usuarios prototipo** con instrumentos diseñados y base declarada (US-UX-01). El riesgo se cierra; su sucesor es mantener la coherencia del método (§22.1.b) y aprovechar las ventanas de validación de A3 y A5 |
| R03 | Personas | Semana con carga laboral/personal de un integrante | Media | Alto | Trabajo asincrónico, plantillas comunes, revisión cruzada; entregables individuales (personas/mapas) empezados desde el miércoles, no el sábado |
| R04 | Técnica | Curva de aprendizaje de Google ADK | Media | Medio | Gate "hello tool" en S1 (2 semanas antes de US-020); fallback: SDK GenAI directo con tool-calling manual |
| R05 | Técnica | Cuotas/latencia de la API de Gemini en demo | Media | Medio | Caché de respuestas frecuentes; datasets pequeños en demo; `thinking_level` medium; medición temprana de TTFT (S3, no S5) |
| R06 | Técnica | ECharts con millones de puntos degrada UX | Media | Medio | Agregación server-side con Polars antes de graficar; `Lazy*`; degradación acordada a 500 K (§10.2); probar volumen real en S4 día 2 |
| R07 | Confianza | El agente alucina cifras en la demo/prueba de usabilidad | Media | Alto | Tool-calling obligatorio para todo dato (§3.3); respuestas sin tool call no muestran números; set de 30–50 pares de evaluación (STRETCH S5) |
| R08 | Datos | Sintéticos poco creíbles restan seriedad a escenarios | Baja | Medio | Esquemas basados en estructuras públicas típicas (carteras, buckets de liquidez); revisión por los 3 (experiencia del dominio) |
| R09 | FinOps | Costo API/cloud se sale del presupuesto académico | Baja | Bajo | Flash-Lite + scale-to-zero + presupuesto §23 con alerta de billing al 50 % |
| R10 | Alcance | Tentación de construir el alcance descartado (§18) | Alta | Medio | Descarte firmado por el equipo; nueva funcionalidad solo por refinamiento formal (US-037+); la regla de oro §10.3 |
| R11 | Alcance | Scope creep de seguridad (refresh tokens, recuperación de contraseña, OAuth externo, RLS por fila) | Media | Medio | Alcance de US-015…019 cerrado por escrito: JWT access simple + seed de usuarios + CRUD admin; todo lo demás documentado como trabajo futuro en `docs/security.md` |
| R12 | Técnica | Desincronización de esquema de BD entre integrantes | Baja | Bajo | dbmate como única vía de cambio de esquema; gate del 30-jul (`schema.sql` idéntico en 3 máquinas); migraciones en PR review. **Degradado el 10-ago:** sin código no hay esquema que desincronizar |
| **R13** | **Curso** | **Materializado (10-ago): la pista de construcción no arranca y ya no cabe en el curso** | — | **Alto** | Tres sprints con 0 SP técnicos ejecutados (§2.6). Déficit re-calculado en ≈ −36 SP (§10.2.b). **Respuesta acordada:** invertir la prioridad y construir solo lo que sostiene A4 y A5 — prototipo web navegable, URL accesible y datos de ejemplo—, y declarar el backend como roadmap en la tabla de alcance de A4 y en el trabajo futuro de A5. El riesgo residual ya no es de calendario sino de **honestidad de la entrega**: lo que no se implemente debe decirse, nunca insinuarse |
| **R14** | **Curso** | **La prueba SUS de A5 es ahora la única validación humana del proyecto** | Media | **Alto** | El card sorting de A3 se resolvió con evaluadores prototipo (§22.1.b), así que se acabaron las ventanas alternas. Mitigación con fecha: **reclutar los ≥5 participantes desde esta semana**, no el lun 17-ago; tener la URL del prototipo navegable arriba antes del mar 18; y ensayar la sesión con un integrante antes del primer participante |

---

## 22. Criterios de Éxito del MVP {#22-criterios}

### 22.1 Curso (los que califican)

- A1: 15/15 con todos los criterios en banda "Completo" (checklist §24). **Al 29-jul: entregada con los 8 rubros en "Completo" y excedida en cantidad (8 personas y 8 mapas); la retroalimentación del profesor fue positiva con una sola observación de maquetación, ya corregida.**
- A2–A5: 100 en cada rúbrica al publicarse, con al menos un diferenciador por actividad (journey maps sobre flujos reales; benchmark con matriz por perfiles; alta fidelidad + prototipo vivo; usabilidad medida con SUS + pre-validación sintética). **Al 10-ago:** A2 entregada el 2-ago con 6 escenarios y 4 journey maps (diferenciador: taller documentado y mapa declarado como mapa de supuestos); **A3 entregada el 9-ago** con los 26 pasos cubiertos (diferenciador: card sorting con análisis reproducible en Python y prueba de árbol que refutó una hipótesis del propio equipo y produjo un cambio aplicado). El diferenciador de A4 se ajusta de "alta fidelidad + prototipo vivo" a **"alta fidelidad navegable + iteración de diseño documentada por pre-validación sintética"**, porque el prototipo funcional con backend no existirá (§10.2.b, R13).
- Documento final que se lee como caso de estudio UX completo (estándar Grocery App, superado en evidencia).

### 22.1.b Criterio de coherencia del método (añadido 29-jul)

A1 y A2 se construyeron con **usuarios prototipo** (US-UX-01). El criterio no es "conseguir campo a toda costa" sino **mantener la coherencia entre lo que el método permite afirmar y lo que los documentos afirman**:

- **Cada artefacto declara su base.** Ya se cumple: A1 llama a sus personas arquetipos hipotéticos y A2 declara su journey map como mapa de supuestos, con los tres supuestos fuertes enunciados junto a la pregunta del instrumento que los verifica.
- **Ninguna cifra sin fuente consultada directamente.** Ya se cumple: los indicadores sin dato dicen "pendiente de medición" y enlazan a su pregunta.
- ~~**La validación llega en su momento previsto:** card sorting de A3 (≥6 participantes) y prueba SUS de A5 (≥5 participantes, exigida por rúbrica).~~ **Reformulado el 10-ago-2026, y es el ajuste más importante de esta revisión.** El card sorting de A3 se ejecutó con **8 evaluadores prototipo condicionados por persona** (protocolo PerceptUI), no con participantes humanos. La rúbrica de A3 no los exigía (§2.3.b) y el entregable declara el método en la introducción, en la sección y en el anexo, así que no hay incoherencia entre lo que el método permite afirmar y lo que el documento afirma — que es el criterio de este apartado. Lo que sí cambia es la aritmética:
  - **De las dos ventanas de validación humana previstas, queda una: la prueba SUS de A5** (≥5 participantes, exigida por su rúbrica). Deja de ser una de dos y pasa a ser la única, y por lo tanto **no es negociable ni posponible**. Si esa sesión no ocurre, el proyecto entero cierra sin un solo dato de comportamiento humano y la frase "usabilidad medida" no se puede escribir en el documento final.
  - **El reclutamiento de los ≥5 participantes arranca ahora, no el lun 17-ago.** Es la tarea con más plazo de espera de todo el calendario y la única que no depende del equipo.
  - **Lo que la cadena de pre-validación sintética sí construyó** es una serie de hipótesis progresivamente más finas: personas y mapas en A1, supuestos declarados en A2, estructura y rutas en A3, pantallas en A4. La prueba de A5 no valida una intuición: contrasta cuatro semanas de predicciones documentadas, y esa es una posición metodológica más fuerte, no más débil — siempre que la prueba efectivamente ocurra.
- En el documento final, el apartado de método explica esta secuencia como una decisión y no como una carencia — que es lo que fue.

### 22.2 Producto/UX

- Flujo Operativo: dato validado con fuente en < 30 s desde el buscador.
- Exportación pesada: `job_id` inmediato; UI nunca bloqueada; enlace firmado funcional.
- Chat: tarjeta de tool call visible **antes** del texto; Stop corta el stream y la llamada LLM; error en stream ofrece Reintentar sin perder conversación.
- Dashboard directivo: carga SWR percibida instantánea; drill-down en ≤2 clics.
- SUS ≥ 75 en la prueba de A5.

### 22.3 Técnicos

- TTFT streaming p50 < 700 ms y P90 documentado (metodología de medición §3.10).
- Latencia P90 de consulta del agente < 15 s (referencia de producción §3.1).
- Búsqueda del catálogo: fuente correcta en el top-3 (Hit Rate@3 ≥ 0.8 sobre el set de evaluación; criterio de US-012).
- **Seguridad:** 100 % de endpoints de datos protegidos con JWT; matriz de permisos verificada por pruebas (401/403 correctos por rol); CRUD admin funcional; cero contraseñas o prompts crudos en logs.
- 100 % de spans LLM con `usage.*` y `prompt_hash`.
- `make dev` reproducible (lockfiles pnpm/Poetry); esquema de BD solo vía dbmate (`schema.sql` versionado); deploy Cloud Run scale-to-zero con smoke tests verdes.

---

## 23. FinOps: Presupuesto de Operación {#23-finops}

| Concepto | Estimación mensual | Nota |
|----------|--------------------|------|
| Gemini 3.5 Flash-Lite (desarrollo + demo) | $5–15 USD | Modelo flash-lite de bajo costo por token; presupuesto de tools limita llamadas; caché de respuestas |
| Cloud Run (front + back, scale-to-zero) | $0–10 USD | Fuera de horario no cuesta; cold start monitoreado en US-034 |
| Cloud Storage + Artifact Registry | $1–5 USD | Exportes con lifecycle de 7 días |
| PostgreSQL (Cloud SQL micro o contenedor en VM mínima) | $0–15 USD | Alternativa MVP: pgvector en contenedor local para dev y solo demo en cloud |
| **Total** | **< $45 USD/mes** | Alerta de billing al 50 % del presupuesto |

---

## 24. Checklist de Excelencia — Actividad 1 {#24-checklist-a1}

Para 15/15 y sobrepasar. Responsable de integración final: Arthur. Deadline interno: **sáb 25-jul 20:00** (buffer de 24 h).

| ✔ | Rubro (peso) | Qué exige la banda "Completo" | Extra de excelencia | Responsable |
|---|--------------|-------------------------------|---------------------|-------------|
| ☑ | Portada (2 %) | Nombres de los 3 integrantes; datos del curso/equipo 8 | Identidad visual del producto (logo/nombre) que reaparecerá en A2–A5 | Alexandro |
| ☑ | Introducción (3 %) | Qué se hizo y cómo está organizado el documento | Párrafo de método: instrumentos + n + fechas de campo | Jacqueline |
| ☑ | Audiencia (5 %) | Clientes/necesidades, pains, demografía, intereses, dónde se conectan, **herramienta y resultados** | Gráficas de la encuesta; tabla de 3 perfiles (§5.1); nota "roles no excluyentes" con dato de E-08 | Jacqueline |
| ☑ | Problema (20 %) | Identificación, cuantificación, impacto, solución; visuales | Diagrama silos antes/después; cuantificación propia (horas/semana buscando datos, de la encuesta); impacto por perfil | Arthur |
| ☑ | Producto (20 %) | Tipo + características y beneficios | Tabla módulo→perfil→beneficio (§6.1); patrones UX 2026 con citas (§6.2); mockup conceptual 1 pantalla | Alexandro |
| ☑ | 6 mapas de empatía (25 %) | 4 cuadrantes Says/Thinks/Does/Feels con observaciones clave | Citas textuales reales de entrevistas en "Says"; plantilla visual uniforme | Cada quien ×2 |
| ☑ | 6 personas (25 %) | Foto, básicos, antecedentes, objetivos, pains, hábitos, frase | Conexión explícita persona↔perfil↔dato de campo; fotos IA consistentes en estilo | Cada quien ×2 |
| ☑ | Formato | PDF, nombre **"Entregable Actividad 1_equipo_8"**, subido por Canvas | Referencias en APA (papers §3 donde aplique); paginación y estilos consistentes | Arthur |

**Cierre del checklist (29-jul-2026).** Los ocho rubros se entregaron en banda "Completo" y se superaron en cantidad: **8 personas y 8 mapas** en lugar de los 6 exigidos. Los tres extras que dependían de campo aplicado —gráficas de la encuesta, cuantificación con horas/semana medidas y citas textuales en "Says"— se resolvieron conforme al método de usuarios prototipo (US-UX-01): cuantificación documental con fuente en cada renglón, indicadores rotulados "pendiente de medición" enlazados a su pregunta verificadora, y cuadrantes "Says" redactados en la voz de cada persona. La retroalimentación del profesor validó el resultado ("lo demás está muy bien presentado y de manera muy atractiva"), con una sola observación de maquetación ya corregida.

**Retroalimentación recibida del profesor sobre A1 y su cierre:** la única observación fue de maquetación —algunos mapas de empatía quedaron divididos en dos páginas—. Corregido el 29-jul en `docs/entregables/estilo/uxdoc.sty`: `\mapaempatia` compone la retícula en una caja, mide su altura y la reserva con `\needspace`, de modo que el mapa no admite corte interno. En la misma pasada se compactó el paginado de los tres documentos (A1 de 52 a 48 páginas, A2 de 53 a 51, acumulado de 106 a 101) eliminando páginas con uno o dos renglones sueltos, y se protegieron los titulares con los hooks `\sectionbreak`/`\subsectionbreak`.

---

## 25. Pendientes y Protocolo para Rúbricas Futuras {#25-pendientes}

### 25.1 Decisiones abiertas del equipo (kickoff)

1. ~~Confirmar nombre del producto~~ ✅ **Resuelto de hecho el 26-jul: Karisma Data**, entregado como marca en A1 y A2 (portada, encabezado y símbolo en `docs/entregables/imagenes/logo_karisma_marca.png`). Registrado el 29-jul en §1. Falta confirmar los roles propuestos (§Equipo).
2. ~~Confirmar fechas de desarrollo~~ ✅ Confirmadas 22-jul (§2.1). ~~Verificar la publicación de las rúbricas~~ ✅ **A2 absorbida el 29-jul** (§2.3) y **A3 el 9-ago** (§2.3.b); ambas en el registro §25.4. **Falta verificar en Canvas A4 (hoy, lun 10-ago) y A5 (lun 17-ago).**
3. Acordar horario fijo de sync (recomendado: 30 min lun/jue + revisión asíncrona sáb).
4. Confirmar cuenta GCP a usar y presupuesto de billing. **Urgente:** es prerrequisito del gate re-fechado del vie 31-jul (acceso a Gemini) y del deploy de S5.

### 25.2 Protocolo de absorción de rúbrica (cuando se publique A2–A5)

1. **T+0 h:** leerla completa; volcarla a tabla criterio→peso→banda "Completo" (formato §2.2).
2. **T+1 h:** mapear cada criterio a la US-UX correspondiente; ajustar sus criterios de aceptación provisionales; recalcular SP.
3. **T+1 día:** si excede lo previsto, congelar STRETCH técnicos del sprint (orden: E5→E4→E2) hasta cubrir el delta.
4. Registrar el ajuste en este documento (sección de la actividad correspondiente) con fecha.

### 25.3 Trabajo explícitamente NO incluido ahora

- ~~Programación de cualquier componente (este documento es solo planeación).~~ **Superado el 29-jul:** el plan sigue siendo la fuente de planeación, pero la pista de construcción arranca el jue 30-jul con US-001 (§19, cola de S2). Lo que este documento no contiene es código, no que el código esté fuera de alcance.
- Todo el alcance descartado de §18: switch A/B de modelos, drift detection, RLS por fila, i18n, paper/benchmark masivo.
- Seguridad avanzada: refresh tokens, recuperación de contraseña, OAuth/SSO externo (documentados como trabajo futuro en `docs/security.md`).

### 25.4 Registro de absorción de rúbricas {#25-4-registro}

Bitácora que exige el paso 4 de §25.2. Una fila por rúbrica absorbida.

| Fecha | Rúbrica | Delta contra lo asumido | SP recalculados | STRETCH congelados | Dónde quedó registrado |
|-------|---------|-------------------------|-----------------|--------------------|------------------------|
| 29-jul-2026 | **A2 — Diseño de escenarios y Journey Maps** (15 pts: 2 % portada · 3 % introducción · 45 % dos escenarios por integrante · 50 % journey map de equipo) | Se asumían 3 escenarios (uno por perfil) y 3 journey maps. La rúbrica pide **6 escenarios** (2 por integrante) y **un journey map de equipo** que concentra el 50 % | Sin cambio: 5 SP. El delta se absorbió porque los escenarios comparten plantilla y los 4 mapas comparten una única fuente de contenido (`figuras/journey_data.py`) | **Ninguno** | §2.3 (desglose), US-UX-05 (criterios definitivos), §2.5 (estado) |
| 9-ago-2026 | **A3 — Análisis competitivo y Arquitectura de Información** (**20 pts**: 2 % portada · 3 % introducción · 25 % análisis competitivo · 25 % card sorting · 25 % arquitectura de información · 20 % mapa de navegación) | La actividad vale **20 puntos, no 15**. Añade el **mapa de navegación como cuarto ejercicio con peso propio** y evalúa por **cobertura de 26 pasos numerados**, no por profundidad. Permite apoyarse en "usuarios potenciales o personas cercanas" sin exigir un mínimo de participantes humanos | Sin cambio: 4 SP. El delta fue de forma (cada paso identificable por su subtítulo), no de esfuerzo | **Ninguno** | §2.3.b (desglose), US-UX-06 (criterios definitivos y cierre), §2.5 (estado), §22.1.b (consecuencia sobre la validación) |
| 10-ago-2026 | **A4 — Interfaces de alta fidelidad** (**25 pts**: 2 % portada · 3 % introducción · **50 % prototipos de alta fidelidad, 10 pts c/u con tope de 50** · **45 % guía de estilos, 9 pts por sección con tope de 45**) | Dos deltas. **(1)** La guía de estilos vale **45 %** y era un criterio de tokens dentro de US-UX-07: la rúbrica nombra siete secciones puntuadas. **(2)** Figma y Lunacy **se recomiendan, no se exigen** —ningún criterio de evaluación las menciona—, así que los prototipos se construyen como la aplicación web real. Los topes de 5 y 5 obligan a entregar **7 pantallas y 11 secciones**, porque con cinco justas una pieza en banda "Parcialmente" cuesta puntos irrecuperables | US-UX-07 se mantiene en 5 SP. Nace **US-UX-09** (guía de estilos, 2 SP) por refinamiento formal. Construcción re-itemizada de ~11 a 21 SP. Total S4: **26 SP sobre 29 de capacidad de una persona** | **Ninguno** (ya congelados el 10-ago) | **§26** (contrato ejecutable de S4), §26.1 (recálculo), [`docs/semana_4/plan_excelencia.md`](../docs/semana_4/plan_excelencia.md) |
| ⏳ Pendiente | A5 — Entrega final | Revisar Canvas el **lun 17-ago** | — | — | — |

### 25.5 Deuda documental detectada el 29-jul

| # | Hallazgo | Acción |
|---|----------|--------|
| 1 | ~~El plan modelaba **3 perfiles**; A1 y A2 trabajan con **8 perfiles de uso** y 4 roles RBAC~~ **Cerrado el 9-ago** | La arquitectura de información de A3 resolvió los 8 perfiles en **4 categorías de primer nivel** (Inicio · Exploración y extracción · Gobierno del dato · Administración) y el mapa de navegación es el contrato que heredan las 5 interfaces de A4 (US-UX-07) |
| 2 | A2 promete capacidades que **no existen en el catálogo US-001…036**: consultas guardadas, marca de versión retirada con enlace a la vigente, notificación dirigida por cambio de definición, copiado con procedencia, comparación lado a lado de variables similares y credenciales de API autogestionadas | Un evaluador de A4/A5 puede contrastar las oportunidades del journey contra el prototipo. Dos salidas legítimas: implementar las dos más baratas y de mayor peso narrativo (**marca de versión retirada** y **copiado con procedencia**, ambas atributos del catálogo ya seedeado, ≈1 SP juntas) y declarar el resto como **roadmap** en la tabla de paridad de A4. El silencio no es opción (R10) |
| 3 | `docs/semana_2/plan_semana_2_excelencia.md` apunta a `docs/documento_proyecto/main.tex`, ruta que ya no existe | La fuente única de entregables es `docs/entregables/` (ver su `README.md`) |
| 4 | Faltan dos herramientas locales: `gitleaks` (sin él el secrets-scan de `make check` no corre, y es gate obligatorio de PR) y `corepack` en PATH con Node 25 | ~~Instalar `gitleaks` el jue 30-jul con US-001~~ **Sin efecto al 10-ago:** no hay `Makefile` ni código que escanear. Se resuelve cuando arranque el prototipo navegable; fijar **Node 22 LTS** en ese momento |
| 5 | **Detectado el 10-ago:** `CLAUDE.md`/`AGENTS.md` documentan `make dev`, `make check`, `make data` y `make db-up` como comandos del proyecto, y ninguno existe | Ya está dicho en §2.6 ("son contrato, todavía no código"), pero conviene repetirlo donde se lee: mientras no exista el `Makefile`, **el QA gate del repo es la revisión cruzada del entregable, no `make check`**. No inventar salidas de comandos que no corren |
| 6 | **Detectado el 10-ago:** el plan comprometía capturas reales de producto como evidencia en A3 y A4, y esa evidencia no existirá | A3 lo sustituyó por un wireframe declarado como diseño. A4 lo sustituye por el prototipo navegable con su **tabla de alcance de tres estados** (navegable con datos / navegable sin datos / roadmap). La regla en ambos casos es la misma: nunca presentar diseño como producto en funcionamiento |

---

## 26. Avance 4: Contrato de Ejecución de S4 {#26-avance-4}

### 26.0 Qué es esta sección y qué manda

Esta sección nace de la **absorción de la rúbrica de A4**, publicada y leída el lunes 10-ago-2026
(protocolo §25.2, registro en §25.4). Contiene las User Stories de S4 **con su alcance recortado
al de esta semana**, no con el alcance de producción que describen §11–§17.

**Regla de precedencia: durante S4 (lun 10 – dom 16 de agosto), en caso de conflicto entre esta
sección y §11–§17, manda §26.** Fuera de esa ventana, §11–§17 siguen siendo la definición del
producto. No se borra nada de las secciones anteriores: se les antepone la referencia, igual que
se hizo con la nota del 29-jul y con el replanteo del 10-ago.

El desarrollo completo de la semana —lectura literal de la rúbrica, las siete pantallas una por
una, el sistema de diseño con sus valores, la infraestructura con sus comandos, el plan de
figuras, el día por día y el checklist final— vive en
[`docs/semana_4/plan_excelencia.md`](../docs/semana_4/plan_excelencia.md). Esta sección es su
contraparte ejecutable: qué historia se cierra, con qué criterios y en qué día.

**Los dos hechos que la rúbrica cambió:**

1. **La guía de estilos vale 45 % de los 25 puntos**, casi tanto como los prototipos (50 %).
   Ninguna US la cubría con ese peso: era un criterio dentro de US-UX-07. Entra como
   **US-UX-09** por refinamiento formal, con criterios y estimación propios, porque enterrar
   medio entregable dentro del criterio de otra historia es exactamente el trabajo silencioso que
   R10 prohíbe.
2. **Figma y Lunacy se recomiendan, no se exigen.** El texto dice «se recomienda el uso de dos
   aplicaciones» y ningún criterio de evaluación las menciona. Los prototipos se construyen como
   **la aplicación web real**, y de ella salen las capturas del documento.

### 26.1 Recálculo de capacidad de S4

El calendario de §19 asumía 15 SP para S4 sobre tres integrantes a ~12 h cada uno (36 h ÷ 2.4 h/SP).
La ejecución real de esta semana es **de una sola persona a 9–12 h diarias**.

| Concepto | Valor |
|----------|-------|
| Horas disponibles lun 10 (media tarde) a dom 16 | ≈ 70 h |
| Constante del plan | 2.4 h/SP |
| **Capacidad nominal de S4** | **≈ 29 SP** |
| Comprometido en §26.2 | **26 SP** |
| **Holgura** | **3 SP (≈ 10 %)** |

Setenta horas de una persona rinden más que treinta y seis repartidas entre tres, y por eso la
capacidad nominal sube. Lo que no sube es la tolerancia al error: una persona sola no tiene de
quién absorber un día perdido, y la holgura del 10 % es delgada. Para eso están las válvulas de
§26.5, escritas de antemano y en orden.

**Corrección de una estimación previa, que conviene registrar.** La tabla de prioridad invertida
de §10.2.b estimó el trabajo de construcción en «prototipo navegable 5–7 SP + URL accesible 1–2 SP
+ datos sintéticos mínimos 2 SP», es decir 8–11 SP. Al itemizarlo por US, la suma de construcción
da **21 SP**. La diferencia no es alcance nuevo: es alcance que la estimación gruesa no veía
porque trataba «el prototipo» como una sola bolsa. Se corrige aquí y no se disimula.

---

### US-001 — Entorno de desarrollo y esqueleto navegable (alcance S4)

**Como** desarrollador del portal,
- **quiero** un monorepo que arranque backend, frontend y base de datos con un solo comando, y un esqueleto de Nuxt 4 con las rutas del mapa de A3 ya navegables,
- **para que** el resto de la semana consista en llenar pantallas y no en pelear con la configuración.

**Criterios de Aceptación (alcance S4):**

- `docker-compose.yml` levanta FastAPI, Nuxt y PostgreSQL con pgvector; `make dev` los arranca.
- `Makefile` con los objetivos que `CLAUDE.md`/`AGENTS.md` ya documentan como contrato: `dev`, `lint`, `test`, `data`, `db-new`, `db-up`, `db-rollback`. Sin `$(shell ...)` evaluado en tiempo de parseo.
- Nuxt 4 con **estructura `app/`**; la estructura de Nuxt 3 es motivo de rechazo.
- Las **ocho rutas del contrato de navegación** existen y responden: `/acceso`, `/inicio`, `/exploracion`, `/exploracion/tableros`, `/exploracion/exportar`, `/gobierno`, `/asistente`, `/administracion`.
- Ruta `/` con el **índice de siete botones**, cada uno con su etiqueta de alcance.
- Barra lateral fija de dos niveles con estado activo y segundo nivel desplegado solo del módulo en uso (revelación progresiva, tal como el mapa de A3 la dejó).
- Franja de aviso de alcance visible en **todas** las rutas, no solo en el índice.

**Tareas técnicas:**

- [ ] `Makefile` y `docker-compose.yml` en la raíz
- [ ] `frontend/` con Nuxt 4, `app/`, Tailwind v4 y `nuxt.config.ts`
- [ ] `backend/` con FastAPI mínimo y `/health`
- [ ] Layout con barra lateral de dos niveles y franja de alcance
- [ ] Las ocho rutas y el índice de siete botones
- [ ] Rama `feature/UX-US-UX-07-alta-fidelidad`

**Estimación:** 1 punto. **Día:** lun 10. **Estado esperado al cierre:** cerrada.

---

### US-002 — Dependencias reproducibles y esqueleto de migraciones (alcance S4)

**Como** desarrollador,
- **quiero** las dependencias de Python y de Node fijadas y reproducibles, y dbmate listo para crear migraciones,
- **para que** el entorno del martes sea el mismo del domingo y el esquema tenga una única vía de cambio.

**Criterios de Aceptación (alcance S4):**

- `backend/pyproject.toml` con Poetry y `poetry.lock` versionado. Nunca `pip` ad-hoc.
- `frontend/package.json` con **`packageManager` fijando pnpm por Corepack** y `pnpm-lock.yaml` versionado. Nunca npm ni yarn.
- **Node 22 LTS fijado**, no el 25 instalado localmente, que no es LTS.
- `db/migrations/` creado y `dbmate` operando contra el PostgreSQL del compose.
- `.env.example` con las tres variables sin las que la aplicación no arranca: `DATABASE_URL`, `JWT_SECRET_KEY`, `GEMINI_API_KEY`.
- `gitleaks` instalado localmente, que es lo que faltaba para que el secrets-scan corra (§25.5-4).

**Fuera de alcance esta semana:** GitHub Actions (US-004). El QA gate sigue siendo la revisión cruzada, como fija §25.5-5.

**Tareas técnicas:**

- [ ] `poetry init` y dependencias del backend
- [ ] `pnpm init` con `packageManager` y Node 22 en `.nvmrc`
- [ ] `dbmate` verificado contra el compose
- [ ] `.env.example` y confirmación de que el backend **no arranca** sin las tres variables
- [ ] Instalar `gitleaks`

**Estimación:** 0.5 puntos. **Día:** lun 10. **Estado esperado al cierre:** cerrada degradada (sin CI).

---

### US-UX-09 — Guía de estilos del producto digital (A4) *(nueva, refinamiento formal del 10-ago)*

**Como** equipo de diseño,
- **quiero** una guía de estilos completa del producto, generada desde la misma fuente que la interfaz,
- **para que** el 45 % de la calificación de A4 quede cubierto y el documento no pueda contradecir a la aplicación.

**Por qué es una US nueva.** La rúbrica de A4 puntúa la guía de estilos a 9 puntos por sección con
tope de 45, y nombra siete secciones. En el catálogo vigente esto era un criterio dentro de
US-UX-07 redactado como «tokens de color, tipografía, espaciado, estados». Con ese peso deja de
ser un criterio y pasa a ser un entregable. Entra por la vía que §18 exige para todo alcance
nuevo: US numerada, con criterios, estimación y sprint.

**Criterios de Aceptación:**

- **Las siete secciones que la rúbrica puntúa**, cada una identificable por su propio subtítulo:
  identidad de la marca · tipografía · paleta de colores · componentes gráficos de la interface ·
  iconografía · conclusiones generales del reporte · referencias bibliográficas.
- **Cuatro secciones adicionales** que la rúbrica menciona en su Sección 2 sin puntuarlas
  explícitamente: imágenes e ilustraciones · retícula y espaciado · microinteracciones y
  animaciones · accesibilidad · voz y tono · documentación y control de versiones.
- **Paleta de cuatro familias × cinco tonos** con hex a la vista, ancladas en los colores ya
  versionados de `docs/entregables/estilo/uxdoc.sty`, más neutros, semánticos y una **paleta
  categórica de series de gráfica** distinta de la de marca.
- **Matriz de contraste WCAG verificada por script**, no a ojo, con las reglas que se derivan de
  ella escritas como reglas (el ámbar `#F97316` nunca lleva texto blanco: 2.6:1).
- **Matriz de botones de 3 variantes × 5 estados**, más variante destructiva y estado de carga,
  frente a las 9 celdas del material de referencia del curso.
- **Un solo script, `generar_tokens_a4.py`**, emite el bloque `@theme` de Tailwind, la matriz de
  contraste y las láminas del documento. La aplicación y el PDF no pueden divergir porque salen
  del mismo archivo.
- **Ruta `/guia`** en la propia aplicación que renderiza el sistema de diseño vivo. Las láminas de
  componentes se capturan de ahí, no se dibujan.
- Guía versionada como **v1.0, 16-ago-2026**, con bitácora de cambios y su política de
  actualización.

**Tareas técnicas:**

- [ ] `generar_tokens_a4.py`: leer paleta de `uxdoc.sty`, emitir `@theme`, matriz de contraste y láminas
- [ ] Escribir el bloque `@theme` en `frontend/app/assets/css/main.css`
- [ ] Ruta `/guia` con paleta, tipografía, botones, campos, chips, tablas, tarjetas e iconos
- [ ] Redactar las once secciones en `contenido/a4_03_guia_estilos.tex`
- [ ] Verificar que ningún color del documento esté escrito a mano

**Estimación:** 2 puntos. **Día:** lun 10 (tokens y `/guia`), sáb 15 (redacción). **Responsable líder:** Arthur. **Sprint:** S4.

---

### US-003 — Despliegue serverless en GCP (alcance S4: puente `gcloud run deploy`)

**Como** equipo,
- **quiero** el prototipo accesible por una dirección pública desde el segundo día de la semana,
- **para que** el reclutamiento de participantes de A5 pueda empezar ya y no el lunes 17.

**Criterios de Aceptación (alcance S4):**

- Proyecto **`tareas-computo-nube`** (número 403109840468), facturación `014738-BE619E-7D4F64`,
  región **`us-central1`**. El proyecto `karisma-data` existe sin facturación y **no se usa**.
- **Dos servicios Cloud Run**: `karisma-api` y `karisma-web`, ambos con `min-instances 0`,
  `max-instances 3`, 512 MiB y concurrencia 80.
- **Cloud SQL `karisma-pg`**: PostgreSQL 15, edición Enterprise, `db-f1-micro`, zonal, 10 GB HDD
  sin crecimiento automático, sin respaldos. Conectada desde Cloud Run con
  `--add-cloudsql-instances`, **sin conector de acceso VPC serverless**, que costaría más que la
  propia base.
- **El navegador solo habla con el frontend**: las rutas `/api/**` se proxyean desde Nitro. Sin
  CORS, cookie `httpOnly` del mismo sitio, y `karisma-api` desplegado con
  `--no-allow-unauthenticated`. **Salida documentada** si esto excede 45 minutos: backend público
  con JWT obligatorio en todo endpoint de datos, y el cierre por IAM pasa a S5. Se declara la
  elección tomada, no se insinúa.
- Artifact Registry con política de limpieza a 3 etiquetas; Secret Manager con `DATABASE_URL` y
  `JWT_SECRET_KEY`.
- **Tres alertas de presupuesto**: 22.50, 36 y 45 USD. El costo proyectado es ≈ 10–14 USD/mes y
  los créditos gratuitos lo absorben; las alertas se ponen igual, porque un crédito que se agota
  sin aviso deja el prototipo caído en mitad de la semana del SUS.

**Fuera de alcance:** Terraform. Sigue congelado, como fijó el recorte #9.

**Tareas técnicas:**

- [ ] Habilitar `run`, `sqladmin`, `artifactregistry`, `secretmanager`, `cloudbuild`
- [ ] Artifact Registry `karisma` con política de limpieza
- [ ] Cloud SQL `karisma-pg` con los flags de arriba
- [ ] Secret Manager y `Dockerfile` multi-etapa de ambos servicios
- [ ] Primer despliegue de los dos servicios y verificación de la dirección pública
- [ ] Tres alertas de presupuesto

**Estimación:** 1 punto. **Día:** mar 11, mañana, con **tope duro de 3 horas**. **Estado esperado al cierre:** cerrada degradada.

---

### US-006 — Silos sintéticos mínimos creíbles (alcance S4)

**Como** evaluador del prototipo,
- **quiero** que cada pantalla tenga datos que se comporten como los de una institución financiera,
- **para que** la evaluación mida el diseño y no la ausencia de contenido.

**Criterios de Aceptación (alcance S4):**

- **Semilla fija `20260720`** en Polars, Faker y numpy. `make data` reproduce byte a byte.
- Tres silos —créditos, liquidez y derivados— con **volúmenes recortados**: lo suficiente para que
  las tablas paginen, los filtros filtren y el preagregado tenga de dónde salir. No hay razón para
  generar cinco millones de filas que nadie va a mirar.
- **Esquemas deliberadamente crípticos y heterogéneos** entre silos (`cli_ref`, `id_cliente`,
  `ctpty_cd` para la misma entidad), porque ese es el problema que el portal resuelve y la
  pantalla debe poder mostrarlo.
- **~0.1 % de anomalías inyectadas** y documentadas en `data/README.md`, para que la vista de
  calidad de datos tenga algo real que reportar.
- **Serie preagregada de 500 000 puntos** lista para el tablero.

**Tareas técnicas:**

- [ ] `ml/data/generators.py` con la semilla y los tres silos
- [ ] Inyección de anomalías y `data/README.md`
- [ ] Preagregado server-side de la serie del tablero
- [ ] Objetivo `make data`

**Estimación:** 1.5 puntos. **Día:** mar 11. **Estado esperado al cierre:** cerrada degradada.

---

### US-015 — Autenticación JWT y acceso (alcance S4)

**Como** usuario del portal,
- **quiero** entrar con mis credenciales y que la sesión determine lo que veo,
- **para que** cada espacio de trabajo se muestre con el rol que le corresponde.

**Criterios de Aceptación (alcance S4):**

- `POST /api/auth/token` con **PyJWT HS256**, `SECRET_KEY` de 32 bytes y expiración de 30 minutos.
- Contraseñas con **pwdlib Argon2**. Los 7 usuarios sembrados llevan la contraseña **prehasheada
  en la migración**, nunca en texto plano en el SQL.
- El JWT vive **solo en cookie `httpOnly`**, establecida por el proxy de Nitro. El cliente nunca
  lo lee; consulta `/api/auth/me`.
- Error 401 con mensaje neutro («Credenciales incorrectas»), sin revelar si el usuario existe.
- Expiración con **re-login limpio**. Sin refresh token: decisión de alcance cerrada por R11.
- **Selector de perfil de demostración** en la pantalla de acceso, con los cuatro roles y su propia
  etiqueta: *acceso de demostración, habilitado únicamente en este prototipo*.

**Tareas técnicas:**

- [ ] `backend/app/core/auth.py` y el endpoint del token
- [ ] Migración `create_app_user` con los 7 usuarios y Argon2
- [ ] Proxy de Nitro que establece la cookie
- [ ] Pantalla `/acceso` con sus cinco estados
- [ ] Selector de demostración con su etiqueta

**Estimación:** 1.5 puntos. **Día:** mar 11. **Estado esperado al cierre:** cerrada.

---

### US-016 — Autorización RBAC por scopes (alcance S4)

**Como** responsable del gobierno del dato,
- **quiero** que cada endpoint declare qué permiso exige,
- **para que** ningún usuario —ni el agente actuando en su nombre— acceda a datos que no le corresponden.

**Criterios de Aceptación (alcance S4):**

- Roles como scopes en el JWT: `operativo`, `analista`, `directivo`, `admin`.
- **Todo endpoint de datos** con `Security(get_current_user, scopes=[...])`.
- **401 sin token o con token inválido**, con cabecera `WWW-Authenticate: Bearer`. **403
  autenticado sin permiso.**
- Matriz de permisos: catálogo para todos los autenticados · consultas puntuales operativo+ ·
  agregaciones, cruces y export analista+ · resúmenes directivos directivo+ · gestión de usuarios
  solo admin.
- **`docs/security.md` escrito**, que es el gate del 6-ago que sigue vencido y sin cumplir.

**Tareas técnicas:**

- [ ] `get_current_user` con `SecurityScopes`
- [ ] Aplicar `Security(...)` a todos los endpoints de datos
- [ ] Redactar `docs/security.md` con la matriz
- [ ] Verificación manual de 401 y 403 por rol

**Estimación:** 1 punto. **Día:** mar 11. **Estado esperado al cierre:** cerrada.

---

### US-008 — Catálogo semántico por palabra clave (alcance S4)

**Como** Laura Méndez, perfil de consulta operativa,
- **quiero** encontrar una fuente escribiendo cómo la llamo yo, no como la llama el sistema de origen,
- **para que** validar una cifra deje de costarme correos y esperas.

**Criterios de Aceptación (alcance S4):**

- `GET /api/catalog/search` con búsqueda **por palabra clave** (ILIKE o tsvector). La búsqueda
  híbrida con pgvector sigue diferida por el recorte #1.
- Catálogo sembrado con **200 a 400 entradas** y **~30 notas de conocimiento tribal**.
- Cada resultado devuelve fuente, definición, propietario, fecha de vigencia y facetas, que es lo
  que alimenta el panel de metadatos.
- La migración `enable_pgvector` **sí se aplica** esta semana, aunque la búsqueda no la use: deja
  el esquema listo y evita una migración más en S5.

**Tareas técnicas:**

- [ ] Migración `create_catalog` con índice tsvector
- [ ] Migración `enable_pgvector`
- [ ] `ml/data/seed_catalog.py` con las entradas y las notas tribales
- [ ] Endpoint de búsqueda y su respuesta Pydantic

**Estimación:** 1 punto. **Día:** mar 11. **Estado esperado al cierre:** cerrada degradada.

---

### US-017 — Guarda de sesión y ocultamiento por rol (alcance S4)

**Como** usuario,
- **quiero** ver solo los módulos que mi rol puede usar,
- **para que** la interfaz no me ofrezca puertas que se van a cerrar en mi cara.

**Criterios de Aceptación (alcance S4):**

- Middleware global de Nuxt que valida la sesión y redirige a `/acceso` sin ella.
- Los módulos sin permiso **no se muestran** en la barra lateral; no basta con deshabilitarlos.
- Acceso directo por URL a una ruta sin permiso devuelve el estado **«sin permiso»** diseñado, con
  indicación de a quién solicitar el acceso y **sin botón de reintento**.
- Expiración de sesión con re-login limpio, sin pantalla en blanco.

**Tareas técnicas:**

- [ ] `app/middleware/auth.global.ts`
- [ ] Composable `useSession` con visibilidad de módulos por scope
- [ ] Estado «sin permiso» como componente reutilizable

**Estimación:** 0.5 puntos. **Día:** mié 12. **Estado esperado al cierre:** cerrada.

---

### US-027 — Espacios de trabajo por rol (alcance S4)

**Como** cada uno de los ocho perfiles de A1,
- **quiero** que la pantalla de inicio me presente primero lo que uso,
- **para que** no tenga que recorrer la interfaz de otro para llegar a la mía.

**Criterios de Aceptación (alcance S4):**

- **Tres composiciones distintas de `/inicio`**: operativo con el buscador dominante; analista con
  explorador y exportaciones recientes; directivo con tres tarjetas de indicador primero y el
  buscador reducido. El administrador entra a `/administracion`.
- Los 8 perfiles de A1 quedan cubiertos por los 4 espacios, con la tabla de correspondencia
  documentada.
- Fundamento empírico citado en el documento: **sin consenso experto sobre «buen layout» (kappa
  0.25 sobre 20 diseñadores y 600 interfaces)**, se parte de defaults por rol en vez de una vista
  única.

**Fuera de alcance:** reordenamiento por arrastre persistido, que es STRETCH y sigue congelado.

**Tareas técnicas:**

- [ ] Las tres composiciones de `/inicio`
- [ ] Búsquedas recientes, favoritos y alertas con datos de ejemplo
- [ ] Tabla perfil → espacio → pantalla principal para el documento

**Estimación:** 1 punto. **Día:** mié 12. **Estado esperado al cierre:** cerrada.

---

### US-025 — Tablero de alto rendimiento (alcance S4: 500 K preagregados)

**Como** Arturo Castañeda, perfil de supervisión directiva,
- **quiero** recorrer una serie larga sin que la interfaz se atasque,
- **para que** pueda mirar el comportamiento completo y no una muestra recortada.

**Criterios de Aceptación (alcance S4):**

- Serie de **500 000 puntos preagregados server-side con Polars**, que es la degradación acordada
  frente al millón original y **se declara como tal en el documento**, no se disfraza.
- Apache ECharts vía `vue-echarts` como **`<LazyVChart/>`**, con importaciones modulares de
  `echarts/core`, `sampling: 'lttb'` y `large: true`.
- **Pan y zoom sin saltos perceptibles.** Medición de fluidez registrada.
- Las interacciones de drill-down **emiten al store Pinia `workspace`**, que es la base del estado
  compartido con el chat.
- Toda gráfica lleva **alternativa en tabla** y **resumen textual** para lector de pantalla, y usa
  la paleta categórica con forma de marcador y patrón de línea propios, para que la información no
  dependa del color.

**Tareas técnicas:**

- [ ] Endpoint de serie preagregada
- [ ] `LazyVChart` con importaciones modulares
- [ ] Store `workspace` y emisión de drill-down
- [ ] Tabla alternativa y resumen textual
- [ ] Medición de fluidez

**Estimación:** 2 puntos. **Día:** mié 12. **Estado esperado al cierre:** cerrada degradada.

---

### US-026 — Revelación progresiva y tarjetas predictivas (alcance S4)

**Como** perfil directivo,
- **quiero** entender el estado global de un vistazo y poder bajar al detalle cuando algo me llame la atención,
- **para que** la profundidad esté disponible sin estar impuesta.

**Criterios de Aceptación (alcance S4):**

- **Tres tarjetas predictivas** con proyección estática, cada una con **etiqueta de método
  visible**: por ejemplo «Riesgo de liquidez +12 % el próximo mes — proyección lineal sobre datos
  sintéticos». **No se finge aprendizaje automático** (honestidad de demo).
- **Drill-down de tres niveles en dos clics como máximo**: tarjeta → panel expandible con la serie
  → tabla de detalle → enlace al explorador.
- Estados de carga con **skeleton y sin desplazamiento de maquetación**, y vacíos diseñados.

**Válvula:** si el reloj aprieta, el drill-down baja a dos niveles. Es la segunda válvula de §26.5.

**Tareas técnicas:**

- [ ] Las tres tarjetas con su etiqueta de método
- [ ] Los tres niveles de revelación
- [ ] Skeleton con dimensiones reservadas

**Estimación:** 1 punto. **Día:** mié 12. **Estado esperado al cierre:** cerrada.

---

### US-029 — Overlay de linaje explicable (alcance S4)

**Como** Roberto Valdez, propietario del dato,
- **quiero** ver de dónde viene una cifra sin salir de donde estoy,
- **para que** pueda responder por ella sin abrir otro sistema.

**Criterios de Aceptación (alcance S4):**

- Al expandir un campo, un panel superpuesto muestra el **recorrido del dato desde su sistema de
  origen** hasta la cifra visible, con las transformaciones intermedias, el propietario y la fecha
  de vigencia.
- **El overlay no altera el flujo de lectura**: se despliega bajo demanda, se cierra y la pantalla
  queda como estaba.
- Foco atrapado mientras está abierto, cierre con `Esc` y con clic fuera, foco devuelto al
  disparador.
- **Estado compartido tablero↔chat con payload estático** (degradación del recorte #12): los
  filtros activos viajan como contexto a `/asistente`, pero el agente no muta el tablero.

**Tareas técnicas:**

- [ ] Componente de overlay con su gestión de foco
- [ ] Datos de linaje en el catálogo sembrado
- [ ] Paso de filtros del tablero al contexto del asistente

**Estimación:** 1 punto. **Día:** jue 13. **Estado esperado al cierre:** cerrada degradada.

---

### US-018 / US-019 — Administración de usuarios (alcance S4: degradación acordada)

**Como** Mariana Ovalle Ríos, perfil de administración de la plataforma,
- **quiero** dar de alta, cambiar de rol y desactivar usuarios,
- **para que** el gobierno del acceso sea demostrable y no una promesa.

**Criterios de Aceptación (alcance S4):**

- **Listar, cambiar rol y desactivar.** Sin formulario de edición completa: es la degradación
  acordada de antemano en §10.2 y el recorte #5.
- **Desactivación por borrado lógico** (`disabled = true`), nunca `DELETE` físico.
- **Un administrador no puede desactivarse a sí mismo.**
- Las acciones destructivas usan el color semántico destructivo, están **separadas espacialmente**
  de las acciones normales y piden confirmación explícita.
- Nunca se renderiza ni se registra `hashed_password`.
- Estados de carga, vacío y error consistentes con el sistema de diseño de US-UX-09.

**Tareas técnicas:**

- [ ] Endpoints de listar, cambiar rol y desactivar con scope `admin`
- [ ] Tabla de usuarios con badges de rol y de estado
- [ ] Modal de confirmación y protección del propio administrador
- [ ] Bitácora de accesos con el acceso cruzado desde `/gobierno`

**Estimación:** 1 punto. **Día:** jue 13. **Estado esperado al cierre:** cerrada degradada.

---

### US-009 — Exportación en segundo plano (alcance S4: flujo completo, fachada de infraestructura)

**Como** Diego Hernández, perfil de análisis de datos,
- **quiero** pedir una extracción grande y seguir trabajando mientras se procesa,
- **para que** la espera deje de bloquear mi jornada.

**Criterios de Aceptación (alcance S4):**

- `POST /api/export` devuelve **`job_id` de inmediato**; el trabajo corre en `BackgroundTasks`.
- **La interfaz nunca se bloquea.** El estado del trabajo se consulta desde cualquier pantalla.
- Historial de exportaciones con **enlace firmado y caducidad de 24 horas**.
- Los tres momentos del flujo —solicitud, trabajo en curso, enlace— son navegables y capturables
  por separado, porque el valor de esta pantalla está en el tiempo y eso es justo lo que un
  archivo de diseño representa mal.

**Fuera de alcance:** política de ciclo de vida del bucket y auditoría de duración (recorte #3).

**Tareas técnicas:**

- [ ] Migración `create_export_job`
- [ ] Endpoint con `BackgroundTasks` y consulta de estado
- [ ] Pantalla `/exploracion/exportar` con los tres momentos
- [ ] Bucket con enlace firmado

**Estimación:** 1 punto. **Día:** jue 13. **Estado esperado al cierre:** demostrada en prototipo.

---

### US-023 — Streaming SSE y cancelación real (alcance S4: transporte real, contenido guionizado)

**Como** cualquiera de los tres perfiles de consulta,
- **quiero** ver la respuesta formarse y poder detenerla cuando ya vi lo que buscaba,
- **para que** la espera sea legible y no un reloj de arena.

**Criterios de Aceptación (alcance S4):**

- `/api/chat` emite **Server-Sent Events reales** desde un generador asíncrono de FastAPI, con
  cuatro eventos tipados: `tool_call`, `token`, `error`, `done`.
- **El contenido es determinista y guionizado**, y así se etiqueta en pantalla y en el documento.
  Lo real —y lo que importa demostrar— es el transporte, el orden de los eventos y la cancelación.
- **Botón «Detener» visible durante toda la generación.** Al pulsarlo el cliente aborta la
  petición, el backend detecta la desconexión y **cancela el generador de verdad**, dejando
  registro del evento. La prueba se documenta con una captura del registro del servidor.
- **La cancelación a mitad de stream no deja tareas colgadas.**
- La tarjeta de tool call **se emite antes de esperar datos**, para que el progreso se perciba.
- **Regla anti-alucinación, que aplica aunque el contenido sea guionizado:** toda cifra procede de
  una tarjeta de tool call visible y cita su fuente del catálogo. Sin tarjeta, no hay número.
- El contrato de eventos se diseña para que **enchufar Gemini detrás cueste una hora, no un día**.

**Go/no-go del sáb 15 a las 12:00.** Si el andamiaje está verde y sobran horas, Gemini 3.5
Flash-Lite se conecta detrás del mismo contrato sin tocar el cliente, y entonces US-020 y US-021
dejan de ser roadmap. Si no, se entrega guionizado y **se declara**.

**Tareas técnicas:**

- [ ] Generador asíncrono con los cuatro eventos
- [ ] Detección de desconexión y cancelación del generador
- [ ] Composable `useChatStream` con `AbortController`
- [ ] Guion determinista de tres conversaciones de ejemplo
- [ ] Captura del registro que prueba la cancelación

**Estimación:** 2 puntos. **Día:** vie 14. **Estado esperado al cierre:** demostrada en prototipo.

---

### US-024 — Error tipado en el stream (alcance S4)

**Como** usuario del asistente,
- **quiero** saber qué paso falló cuando algo se rompe a mitad de una respuesta,
- **para que** pueda decidir si reintentar o pedir un permiso.

**Criterios de Aceptación (alcance S4):**

- Evento `error` **tipado**, que dice qué paso falló y no solo que falló.
- **Distingue error recuperable de error de permiso**: un 403 muestra mensaje de rol insuficiente y
  **no ofrece reintento**.
- El historial de la conversación **no se borra** cuando llega un error.

**Fuera de alcance:** botón «Reintentar». Es el recorte #4, acordado por escrito.

**Tareas técnicas:**

- [ ] Tipado del evento `error` y su emisión desde el generador
- [ ] Tarjeta de tool call en su cuarto estado
- [ ] Diferenciación visual de error recuperable y error de permiso

**Estimación:** 0.5 puntos. **Día:** vie 14. **Estado esperado al cierre:** cerrada degradada.

---

### US-028 — Tarjetas de visibilidad de tool call (alcance S4)

**Como** cualquier usuario que reciba una cifra del asistente,
- **quiero** ver qué consultó antes de leer lo que me dice,
- **para que** pueda auditar la respuesta en lugar de creerla.

**Este es el criterio que no se puede simular en un archivo de diseño**, y por eso nunca entró en
ninguna lista de recortes.

**Criterios de Aceptación (alcance S4):**

- **Cuatro estados de la tarjeta**, en secuencia dentro de la conversación y como galería en la
  guía de estilos:
  1. **Anuncio** — «Consultando base de liquidez…», antes de tener el dato.
  2. **Ejecución** — indicador de progreso y tiempo transcurrido.
  3. **Resultado** — mini-tabla o cifra **antes del texto generado**, con la fuente citada.
  4. **Error** — qué paso falló y qué hacer.
- Los eventos `tool_call` alimentan las tarjetas **sin volver a renderizar el historial completo**.
- Anatomía completa documentada: icono de herramienta, nombre legible de la operación, tiempo,
  resultado plegable y cita de fuente.

**Válvula:** los cuatro estados se muestran como galería en lugar de secuencia animada. Es la
primera válvula de §26.5, y la más barata.

**Tareas técnicas:**

- [ ] Componente `ToolCallCard` con sus cuatro estados
- [ ] Consumo de eventos sin re-render del historial
- [ ] Galería de los cuatro estados en `/guia`

**Estimación:** 1.5 puntos. **Día:** vie 14. **Estado esperado al cierre:** cerrada.

---

### US-UX-07 — Interfaces de alta fidelidad (A4) — **criterios reescritos el 10-ago**

> Los criterios provisionales de §11 se conservan como registro de lo que se asumió el 22-jul.
> **Los vigentes son estos.**

**Como** equipo de diseño,
- **quiero** siete pantallas de alta fidelidad construidas en el stack del producto, desplegadas y recorribles, con su alcance declarado sin ambigüedad,
- **para que** la entrega de A4 muestre el producto y no una representación de él, y para que A5 tenga sobre qué correr la prueba SUS.

**Criterios de Aceptación (vigentes):**

1. **Siete prototipos de alta fidelidad**, navegables y desplegados: acceso · inicio · exploración
   y extracción (con la rama 2.4 y el drill-down) · gobierno del dato (con el overlay de linaje) ·
   asistente conversacional (con los 4 estados y el Stop) · administración · exportación. La
   rúbrica alcanza su tope con cinco; se entregan siete porque una pantalla juzgada
   «Parcialmente» con solo cinco cuesta puntos que ningún otro apartado recupera.
2. **Sistema de diseño con fuente única**, cubierto por US-UX-09. Derivación en un solo sentido:
   `uxdoc.sty` → `@theme` de Tailwind → interfaz → capturas → PDF. **Nada fluye hacia atrás.**
3. **Cada ruta anclada a una rama del mapa de navegación de A3.** Ninguna rama sin ruta, ninguna
   ruta sin rama; se verifica con una tabla de dos columnas. Las **nueve facetas transversales**
   se resuelven como accesos cruzados, no como duplicados de contenido.
4. **Los cuatro estados no felices diseñados** en cada pantalla: vacío, cargando sin desplazamiento
   de maquetación, error, sin permiso.
5. **Tabla de alcance de tres estados** por pantalla —*navegable con datos de ejemplo* ·
   *navegable sin datos* · *roadmap*—, que **sustituye a la tabla de paridad** del criterio 3
   original: con un solo artefacto no hay dos lados que comparar. Incluye las seis capacidades que
   A2 prometió y el catálogo no cubre (§25.5-2) y las US-037…041. **El silencio sobre ellas es lo
   único que no funciona.**
6. **Pre-validación con los 8 evaluadores prototipo sobre capturas reales del prototipo, no sobre
   mockups**, con **al menos una iteración documentada como hallazgo → cambio → versión**, con el
   antes y el después lado a lado. Sin la captura del antes, la iteración no es verificable y no
   cuenta. Dos tareas se heredan de la prueba de árbol de A3: repetir la tarea del indicador de
   riesgo sobre la arquitectura revisada, y medir si el acceso cruzado a la bitácora reduce el
   titubeo de la tarea de autorización.
7. **Nota de herramienta** en la introducción del documento, que justifica construir en web frente
   a las dos aplicaciones que la rúbrica recomienda, anclada a los cuatro requisitos que la propia
   rúbrica pone a un prototipo de alta fidelidad y al objetivo OEA 2.2.
8. **PDF entregado como `Entregable Actividad 4_equipo_8.pdf`** antes del dom 16-ago 23:59, con
   portada de los tres integrantes.

**Tareas técnicas:**

- [ ] Guion de capturas con Playwright a viewport fijo, reproducible
- [ ] `main_a4.tex` y `contenido/a4_00` a `a4_07`
- [ ] Portadilla `\uxparte{IV}` en `main_completo.tex` y actualización de «Sobre este documento»
- [ ] Tabla ruta ↔ rama y tabla de alcance de tres estados
- [ ] Pre-validación, iteración y recaptura de las pantallas afectadas
- [ ] Compilar, revisión cruzada y subir a Canvas

**Estimación:** 5 puntos. **Días:** sáb 15 y dom 16. **Estado esperado al cierre:** cerrada.

---

### 26.3 Estado de todas las US al cierre de S4

Cuatro estados. Esta tabla es la que alimenta directamente la tabla de alcance del PDF, así que
**ninguna US puede quedar sin declarar**.

| Estado | US |
|--------|----|
| **Cerrada** | US-001, US-015, US-016, US-017, US-026, US-027, US-028, US-UX-07, US-UX-09 |
| **Cerrada degradada** | US-002 (sin CI) · US-003 (puente, sin Terraform) · US-006 (volúmenes recortados) · US-008 (solo palabra clave) · US-018/019 (sin edición completa) · US-024 (sin Reintentar) · US-025 (500 K) · US-029 (estado compartido estático) |
| **Demostrada en prototipo, no productiva** | US-009 (exportación) · US-023 (contenido guionizado) |
| **Roadmap declarado en el documento** | US-011 completa · US-020 y US-021 (agente ADK real, salvo que el go/no-go del sábado salga verde) · US-037 a US-041 · las seis capacidades de §25.5-2 |
| **Congeladas, sin cambio** | US-012, US-013, US-014, US-022, US-035, US-036 y todos los bloques `+N STRETCH` |
| **De S5, no se tocan** | US-004, US-005, US-030, US-031, US-032, US-033, US-034, US-UX-08 |

### 26.4 Gates de S4, con hora

| Cuándo | Gate | Si falla |
|--------|------|----------|
| **Mar 11, 12:00** | **Dirección pública viva** con los dos servicios desplegados | Es la mitigación con fecha de R14. Sin URL el martes, el reclutamiento de A5 se retrasa una semana y el riesgo se vuelve estructural |
| **Vie 14, 12:00** | Decisión sobre el alcance de la prueba SUS de A5 | Se decide con lo que haya; no se pospone al lunes |
| **Vie 14, 20:00** | **Congelamiento.** Ninguna pantalla se toca salvo por la iteración del sábado | Sin congelamiento no hay capturas estables y la pre-validación corre sobre un blanco móvil |
| **Sáb 15, 12:00** | Go/no-go de Gemini real | Si es no, se declara guionizado y se sigue. No se negocia después |
| **Dom 16, 20:00** | **Entrega en Canvas** | Margen de 3h59 contra el cierre de las 23:59 |

### 26.5 Válvulas de S4, en orden, y los no negociables

Se aplican **en este orden** y solo cuando el reloj obligue:

1. Los cuatro estados de la tarjeta de tool call se muestran como **galería** en lugar de secuencia animada.
2. El drill-down del tablero baja de **tres niveles a dos**.
3. **Administración** se entrega en un solo nivel.
4. La pantalla de **exportación sale del set** y quedan seis prototipos.

**No negociables**, porque son lo que ninguna otra evidencia sustituye:

- Las **cinco interfaces de la arquitectura** de A3, navegables.
- La **iteración documentada** de pre-validación.
- La **guía de estilos completa** con sus siete secciones puntuadas, que vale 45 %.

### 26.6 Lo que S4 deja fuera, con nombre y razón

El silencio es lo único que no funciona, así que queda escrito:

| Fuera de S4 | Razón |
|-------------|-------|
| **US-011 completa** (10 consultas de referencia) | La versión mínima que alimenta las pantallas sí está. El resto no cambia ninguna banda de la rúbrica |
| **US-020 y US-021** (agente ADK con Gemini real) | El spike «hello tool» nunca se corrió. Se declara roadmap, salvo que el go/no-go del sábado salga verde |
| **US-004** (GitHub Actions) | El QA gate de esta semana es la revisión cruzada (§25.5-5). Un pipeline sin tests que correr no aporta |
| **Terraform más allá del puente** | Recorte #9, ya acordado |
| **US-012, US-013, US-014, US-022, US-035, US-036** | Congeladas desde el 29-jul y el 10-ago |
| **US-030 a US-034** | Son de S5: observabilidad, TTFT, costo y pase a producción |
| **Modo oscuro** | Un modo oscuro mal contrastado resta más de lo que suma, y la semana no da para verificar dos paletas. Queda en el roadmap de la guía de estilos |

---

### A.1 Encuesta (Google Forms, ~7 min, anónima)

**Screening/demografía:** (E-01) Edad por rango. (E-02) Género (opcional). (E-03) Ciudad/país. (E-04) Rol actual: operaciones / análisis de datos / dirección / TI / otro. (E-05) Años de experiencia en el sector financiero-datos.

**Comportamiento y pains:** (E-06) ¿Cuántas fuentes/sistemas distintos consultas para armar un análisis típico? (1 / 2–3 / 4–5 / 6+). (E-07) ¿Cuántas horas a la semana pierdes buscando dónde está un dato o validándolo? (rangos) ← **cuantificación del problema**. (E-08) En una semana típica, ¿alternas entre consultas rápidas y extracciones/análisis profundos? (siempre/a veces/nunca) ← valida "roles no excluyentes". (E-09) ¿Qué es lo más frustrante de cruzar datos de áreas distintas? (opción múltiple + abierta). (E-10) Cuando no sabes dónde vive un dato, ¿a quién/qué recurres primero? (colega / intranet / correo / adivino el sistema / otro) ← silos de conocimiento. (E-11) ¿Qué formato de salida necesitas más? (pantalla / CSV-Excel / API / reporte PDF). (E-12) Si pudieras preguntarle a un asistente "¿dónde está X dato y qué significa?", ¿qué tanto lo usarías? (Likert 1–5) + ¿qué le preguntarías primero? (abierta).

**Canales:** (E-13) ¿Dónde te informas de herramientas/datos? (LinkedIn / comunidades Slack-Discord / YouTube / cursos / colegas).

### A.2 Guion de entrevista semiestructurada (30 min)

1. Cuéntame tu rol y un día típico con datos. 2. Narra la última vez que necesitaste un dato de otra área: paso a paso, ¿cuánto tardó?, ¿qué se sintió? (sondear emociones para "Feels"). 3. ¿Cómo validas que una cifra es correcta antes de usarla? 4. ¿Qué haces cuando la herramienta se queda corta? (Excel escapes, tickets, favores). 5. Si mañana existiera un portal único, ¿qué tendría que hacer en la primera semana para que confíes en él? 6. ¿Qué NO debería hacer jamás? (deal-breakers: opacidad, lentitud, borrar contexto). 7. Cierre: una frase que resuma tu relación con los datos de tu institución (candidata a "frase de la persona").

### A.3 Consentimiento y ética

Participación voluntaria y anónima (encuesta) / con consentimiento verbal registrado (entrevistas); datos usados solo con fines académicos del curso; sin datos confidenciales de instituciones reales.

---

## Anexo B: Matriz de Personas y Mapas de Empatía {#anexo-b}

**Plantilla de persona (idéntica para las 6):** Foto (generada con IA, estilo fotográfico consistente) · Nombre, edad, sexo, ocupación · Antecedentes (educación, situación familiar, intereses) · Objetivos (2–3, ligados al portal) · Pain points y desafíos (3–4, al menos 1 de la investigación) · Comportamientos y hábitos (relación con datos/herramientas) · Frase (idealmente derivada de la pregunta 7 de la entrevista).

**Plantilla de mapa de empatía:** cabecera con nombre de la persona + 4 cuadrantes **SAY / THINK / DO / FEEL** (≥3 viñetas cada uno; "Say" redactado en la voz de la persona, sustituible por cita textual cuando se apliquen las entrevistas).

**Guía de coherencia:** Persona Operativa → urgencia, validación, desconfianza de cifras sin fuente. Analista → profundidad, exportación, fricción de accesos. Directivo → síntesis, riesgo, tiempo escaso, delegación.

---

## Anexo C: Familias de Preguntas del Agente {#anexo-c}

Seed del set de evaluación (STRETCH S5, US-035) y guion de la demo:

- **Descubrimiento:** "¿Dónde encuentro la mora por producto?" → catálogo + fuente + dueño del dato.
- **Definición:** "¿Qué significa el bucket 7–30 días en liquidez?" → diccionario + regla tribal.
- **Consulta puntual:** "Saldo total de cartera vigente a ayer" → tool call a `/api/creditos`.
- **Cruce:** "Exposición total (créditos + derivados) de la contraparte X" → 2 tool calls + join.
- **Tendencia:** "¿Cómo se movió la liquidez a fin de mes los últimos 6 meses?" → serie + gráfica.
- **Resumen directivo:** "Resume el riesgo de liquidez de este mes" → tarjetas + narrativa.
- **Exportación:** "Dame el detalle en Excel" → job en segundo plano + aviso de enlace.
- **Fuera de dominio:** "¿Me recomiendas una película?" → rechazo cortés (ruteo OOD §3.1).
- **Explicabilidad:** "¿De qué tablas sacaste ese número?" → linaje (overlay).
- **Permisos:** un Operativo pide una exportación masiva → el agente explica que requiere rol Analista (RBAC visible también en la conversación, US-016).

---

## Anexo D: Glosario {#anexo-d}

| Término | Uso en el documento |
|---------|---------------------|
| Silo de datos | Fuente aislada por área (créditos, liquidez, derivados) |
| Data Catalog / catálogo semántico | Diccionario institucional buscable con metadatos y conocimiento tribal |
| Conocimiento tribal | Reglas no documentadas que corrigen malinterpretaciones de los datos (§3.2) |
| Capa semántica | Métricas/dimensiones curadas entre el LLM y las fuentes; el agente compone consultas validadas (§3.4) |
| Revelación progresiva | Mostrar resumen primero y detalle bajo demanda |
| Tarjetas predictivas | Predictive Insight Cards: previsiones en la vista principal |
| Tool-Call Visibility | Patrón UI que muestra qué herramienta usa el agente, su estado y su resultado |
| SSE | Server-Sent Events; canal del streaming del chat |
| TTFT | Time To First Token; latencia al primer token de la respuesta |
| SUS | System Usability Scale; cuestionario estándar de usabilidad (A5) |
| **JWT** | JSON Web Token firmado (HS256) que porta identidad y rol; emitido por `/api/auth/token` |
| **RBAC** | Control de acceso basado en roles; implementado con scopes de FastAPI (US-016) |
| **Argon2 / pwdlib** | Algoritmo y librería de hashing de contraseñas recomendados por FastAPI (argon2id) |
| **Scope** | Claim del JWT que representa el rol; los endpoints lo exigen con `SecurityScopes` |
| **dbmate** | Herramienta de migraciones SQL puras (`-- migrate:up/down`, `schema.sql` versionado) |
| Soft delete | Desactivación lógica (`disabled=true`) en lugar de borrado físico, por auditoría |
| MUST / STRETCH | Alcance comprometido vs. deseable sacrificable |
| SP | Story point (≈2.4 h ≈ 0.5 día) |

---

**FIN DEL DOCUMENTO**

**Última actualización:** lunes 10 de agosto de 2026 — cierre de US-UX-05 y US-UX-06 con A2 y A3 entregadas (§2.5), absorción de la rúbrica de A3 (§2.3.b, registro §25.4), reformulación del criterio de validación con participantes tras ejecutar el card sorting con evaluadores prototipo (§22.1.b), re-verificación de la pista de construcción en 0 % al abrir S4 (§2.6), re-recálculo de capacidad con déficit de ≈ −36 SP y la inversión de prioridad que lo cierra (§10.2.b), replanteo de A4 como prototipo web navegable de 5 interfaces (US-UX-07, §19 S4), gates actualizados (§20) y riesgos R13/R14 abiertos (§21).

**Actualización previa:** miércoles 29 de julio de 2026 — cierre de A1 con el método de usuarios prototipo (US-UX-01, §5.2, §22.1.b), absorción de la rúbrica de A2 (§2.3), estado real de las historias UX (§2.5), estado verificado de la pista de construcción (§2.6), recálculo de capacidad con la escalera de recorte (§10.2.b), cobertura de lo comprometido en A1/A2 y US-037…041 de roadmap (§18.1), replanificación del roadmap S2–S5 (§19), gates re-fechados (§20) y registro de absorción (§25.4).
**Mantenedor:** Arthur Zizumbo (Platform/Agent lead) — Equipo 8
**Próxima revisión:** al entregar A2 (dom 2-ago) y al publicarse la rúbrica de A3 (revisar Canvas el lun 3-ago antes de trabajar en A3)
