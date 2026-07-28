# Plan de Proyecto UX: Portal Centralizado de Datos Financieros

**Plataforma de inteligencia centralizada con navegación por revelación progresiva, catálogo semántico de datos y agente conversacional (Nuxt 4 + Apache ECharts + FastAPI + Polars + Google ADK + Gemini 3.5 Flash-Lite)**

---

**Documento:** Planeación SCRUM detallada + alineación con el curso — TC4032 Experiencia del Usuario y Diseño de Interfaces, Maestría en Inteligencia Artificial Aplicada (MNA), ITESM.
**Periodo:** 20 de julio a 23 de agosto de 2026 (5 semanas, la semana 1 ya en curso).
**Estado del documento:** plan definido del equipo (22-jul-2026). Las secciones marcadas ⚠️ PENDIENTE requieren decisión del equipo o rúbrica aún no publicada.
**Catálogo de historias:** 44 en total — **US-001…US-036** (técnicas, numeración contigua sin huecos) + **US-UX-01…US-UX-08** (entregables del curso), cada una independiente y verificable (INVEST).

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
18. [Alcance Descartado (fuera del curso)](#consolidacion)
19. [Roadmap Semanal de Sprints](#19-roadmap)
20. [Gates de las Semanas 1–2](#20-gates)
21. [Gestión de Riesgos](#21-riesgos)
22. [Criterios de Éxito del MVP](#22-criterios)
23. [FinOps: Presupuesto de Operación](#23-finops)
24. [Checklist de Excelencia — Actividad 1](#24-checklist-a1)
25. [Pendientes y Protocolo para Rúbricas Futuras](#25-pendientes)
- [Anexo A: Instrumentos de Investigación (borrador)](#anexo-a)
- [Anexo B: Matriz de Personas y Mapas de Empatía](#anexo-b)
- [Anexo C: Familias de Preguntas del Agente](#anexo-c)
- [Anexo D: Glosario](#anexo-d)

---

## 1. Resumen Ejecutivo {#1-resumen-ejecutivo}

El **Portal Centralizado de Datos Financieros** (nombre comercial ⚠️ PENDIENTE; candidatos: *Faro*, *Atlas Financiero*, *Prisma*) es una plataforma web modular que elimina la dispersión de información entre silos financieros institucionales (créditos, liquidez, derivados) mediante cuatro capacidades integradas:

1. **Espacios de trabajo por rol con revelación progresiva.** El usuario Operativo ve un buscador y validación puntual; el Analista profundiza a filtros complejos y exportación cruda; el Directivo consume tarjetas predictivas y tableros consolidados. La complejidad técnica solo aparece cuando se necesita. El acceso se controla con **autenticación JWT y autorización por roles (RBAC)**.
2. **Catálogo semántico de datos (Data Catalog).** Diccionario institucional buscable en lenguaje de negocio que responde "¿dónde vive este dato?", enriquecido con conocimiento tribal (definiciones, reglas de área, advertencias de uso) y preparado para RAG.
3. **Agente conversacional con herramientas gobernadas.** Un agente Google ADK razonando con Gemini 3.5 Flash-Lite que **no inventa cifras**: invoca endpoints FastAPI gobernados por permisos que ejecutan agregaciones Polars, con visibilidad total de cada tool call en la interfaz (patrón *Tool-Call Visibility*) y streaming SSE con botón de cancelación real.
4. **Exportación pesada sin fricción.** Descargas masivas CSV/Excel delegadas a segundo plano con `job_id`, estado consultable y enlaces firmados de Cloud Storage, sin congelar la interfaz.

### Doble naturaleza del proyecto

Este proyecto vive en dos pistas simultáneas que el plan integra explícitamente:

- **Pista UX (la calificada).** Cinco actividades del curso TC4032: definición de producto y usuarios (A1, dom 26-jul), escenarios y journey maps (A2), análisis competitivo y arquitectura de información (A3), interfaces de alta fidelidad (A4) y entrega final (A5). **Esta pista manda:** cada sprint cierra primero el entregable UX de la semana.
- **Pista de construcción (la que da ventaja).** Los EPICs técnicos 0–5 producen un prototipo funcional real (Nuxt 4 + FastAPI + agente) que eleva la calidad de las evidencias UX: capturas reales para A3/A4, pruebas de usabilidad sobre producto vivo para A5, y un diferenciador frente a equipos que solo entregan mockups.

### Método central: diseño centrado en el usuario con evidencia

El hilo conductor metodológico es el proceso UX completo: investigación con instrumentos propios (encuesta + entrevistas a perfiles financieros reales) → personas y mapas de empatía → escenarios y journey maps → arquitectura de información validada → prototipos de alta fidelidad → evaluación de usabilidad. La novedad 2026 que aporta el equipo: **pre-validación con usuarios sintéticos condicionados por persona** (PerceptUI, §3.8) antes de las pruebas con usuarios reales, y patrones de UX para agentes (transparencia de tool calls, streaming cancelable) fundamentados en literatura CHI/arXiv 2026.

---

## 2. Alineación con el Curso: las 5 Actividades {#2-alineacion-curso}

### 2.1 Calendario de entregas (fechas confirmadas por el equipo, 22-jul-2026)

Las fechas de desarrollo quedaron confirmadas con cadencia dominical. Las rúbricas de A2–A5 siguen ⚠️ pendientes de publicación en Canvas; al publicarse cada una se aplica el protocolo de absorción (§25.2).

| Actividad | Tema | Fecha de entrega | Rúbrica | Sprint |
|-----------|------|------------------|---------|--------|
| **A1** | Definición del producto digital y diseño de instrumentos de investigación de usuario | **dom 26-jul-2026** | **Publicada** (15 pts) | S1 |
| A2 | Diseño de escenarios y Journey Maps | **dom 2-ago-2026** | ⚠️ Pendiente | S2 |
| A3 | Análisis competitivo y Arquitectura de Información | **dom 9-ago-2026** | ⚠️ Pendiente | S3 |
| A4 | Interfaces de alta fidelidad | **dom 16-ago-2026** | ⚠️ Pendiente | S4 |
| A5 | Entrega final | **dom 23-ago-2026** | ⚠️ Pendiente | S5 |

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

### 2.3 Mapeo actividad → capítulos del proceso UX → épicas

| Actividad | Proceso UX | Épicas que la alimentan | Evidencia diferenciadora |
|-----------|-----------|--------------------------|--------------------------|
| A1 | Empatizar + Definir | EPIC UX (US-UX-01…04) | Encuesta real con n≥15 y entrevistas por perfil; gráficas de resultados |
| A2 | Definir + Idear | EPIC UX (US-UX-05), E1 (catálogo como escenario) | Journey maps de los 3 perfiles sobre flujos reales del portal |
| A3 | Idear + Estructurar | EPIC UX (US-UX-06), E1/E2 (catálogo, endpoints, roles) | Benchmark de 4–6 productos reales + sitemap y card sorting |
| A4 | Prototipar | EPIC UX (US-UX-07), E3/E4 (agente, dashboard) | Alta fidelidad en Figma **+ prototipo funcional en Nuxt 4** |
| A5 | Probar + Entregar | EPIC UX (US-UX-08), E5 (observabilidad, deploy) | Pruebas de usabilidad (SUS) + pre-validación sintética PerceptUI |

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

1. **Trípode de perfiles con un solo producto.** Operativo, Analista y Directivo no son tres apps: son tres niveles de revelación del mismo sistema, con evidencia de investigación propia (encuesta + entrevistas) de que los modos coexisten en una misma persona según la tarea.
2. **El agente no calcula: orquesta.** Cifras siempre provenientes de Polars vía endpoints gobernados con permisos JWT (papers §3.3, §3.4) — defendible ante auditoría financiera.
3. **Transparencia como requisito, no adorno.** Patrones tool-call visibility y overlays de linaje fundamentados en el marco empírico de §3.7.
4. **UX medida, no supuesta.** TTFT y P90 con OpenTelemetry; pre-validación sintética por personas (§3.8) + SUS con usuarios reales en A5.
5. **Stack 2026 de bajo costo.** Nuxt 4 (shallowRef, Lazy, SWR) + ECharts para millones de puntos + Gemini 3.5 Flash-Lite (rápido y económico para alto volumen) + Cloud Run scale-to-zero.

---

## 5. Usuarios y Estrategia de Investigación UX {#5-usuarios-investigacion}

### 5.1 Los tres perfiles (audiencia)

Los roles **no son excluyentes**: una misma persona cambia de modo según la tarea (hallazgo a validar explícitamente con la encuesta, pregunta E-08 del Anexo A). A nivel de sistema, además de los tres perfiles existe el rol técnico **Admin** (gestión de usuarios, US-018/019), que no es un perfil UX de investigación sino de operación del portal.

| Perfil | Necesidad dominante | Módulos principales | Métrica de éxito UX |
|--------|--------------------|--------------------|---------------------|
| **Operativo** (consulta rápida) | Validar/consultar datos puntuales con mínima fricción | Buscador global, catálogo, respuestas del agente con fuente | Tiempo a dato validado < 30 s |
| **Analista de datos** (profundidad) | Filtros complejos, cruces de variables, exportación cruda | Explorador de datos, exportación en segundo plano, APIs | Export masivo sin bloquear UI; cruce multi-fuente en < 5 min |
| **Directivo** (abstracción) | Supervisión y decisión con carga cognitiva mínima | Tarjetas predictivas, tableros consolidados, resumen del agente | Comprensión de estado global en < 1 min sin ayuda |

Demografía objetivo (a confirmar con instrumento): profesionales de banca/finanzas en México, 25–55 años, oficinas centrales y esquema híbrido; se conectan en escritorio corporativo (principal) y móvil (consulta); buscan información en intranet, Teams/Slack, correo y con colegas (el "experto de al lado" — exactamente el silo de conocimiento que el portal ataca).

### 5.2 Instrumentos de investigación (Actividad 1 exige indicarlos con resultados)

| Instrumento | Alcance | Meta | Responsable ⚠️ propuesto | Producto |
|-------------|---------|------|--------------------------|----------|
| **Encuesta estructurada** (Google Forms, ~13 preguntas, Anexo A.1) | Colegas del sector financiero/datos de la red de los 3 integrantes | **n ≥ 15** respuestas antes del vie 24-jul | Jacqueline (diseño), todos (distribución) | Gráficas de pains y frecuencias para la sección Problema |
| **Entrevistas semiestructuradas** (30 min, guion Anexo A.2) | 1 por perfil: un operativo, un analista, un directivo | 3 entrevistas antes del sáb 25-jul | Uno por integrante | Citas textuales para mapas de empatía ("Says") y frases de personas |
| **Observación de canales** (LinkedIn, comunidades de datos/finanzas, foros internos) | Dónde se conectan y buscan información | Lista de canales citable | Alexandro | Sustento del apartado "dónde se conectan" |

**Regla de honestidad metodológica:** toda cifra del documento de A1 sale de (a) la encuesta propia, (b) una fuente pública citada y verificada, o (c) se declara como estimación del equipo. No se inventan estadísticas de mercado.

### 5.3 Distribución de personas y mapas de empatía (Sección 2 de A1, individual)

6 personas y 6 mapas cubren los 3 perfiles × 2 variantes cada uno (ver plantillas en Anexo B):

| Integrante | Persona 1 | Persona 2 |
|------------|-----------|-----------|
| Alexandro | **Analista de datos** (riesgo de mercado, usuario power de Python/Excel) | **Operativo** (mesa de derivados, urgencia intradía) |
| Jacqueline | **Directivo** (dirección de liquidez, supervisión regulatoria) | **Analista** (riesgo de crédito, reportes mensuales) |
| Arthur | **Operativo** (tesorería, validación puntual) | **Directivo** (CFO/dirección de riesgos, decisión ejecutiva) |

Cada integrante hace el mapa de empatía de sus mismas 2 personas (consistencia narrativa persona↔mapa, alimentada por las entrevistas).

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
| E1 | Ingesta sintética, catálogo, exportación, EDA · US-006…010 | **10** | +5 | S1–S2 |
| E2 | Motor analítico + búsqueda + **auth JWT/RBAC + usuarios** · US-011…019 | **13** | +5 | S2–S3 |
| E3 | Agente ADK + Gemini + streaming/Stop · US-020…024 | **11** | +3 | S3–S4 |
| E4 | Frontend Nuxt 4 + ECharts + patrones UX · US-025…029 | **9** | +7 | S4 |
| E5 | Observabilidad LLM, pruebas, producción · US-030…036 | **9** | +7 | S5 |
| **Total** | 44 historias (36 técnicas + 8 UX) | **86** | **+36** | Capacidad ≈ 75 |

**Déficit declarado: −11 SP** sobre capacidad. Válvulas, en orden: (a) los STRETCH no se tocan salvo holgura real; (b) plantillas y generación asistida por IA para artefactos UX (fotos de personas, primeras iteraciones de layouts); (c) el prototipo funcional reduce el costo de A4 (capturas reales en vez de dibujar todo en Figma); (d) degradaciones acordadas de antemano: US-018/019 pueden reducirse a listado + cambio de rol + desactivación (sin formulario de edición completo), US-025 puede demostrarse con 500 K puntos pre-agregados server-side en vez de 1 M crudos. Si una rúbrica llega más pesada de lo previsto, se congela primero E5-stretch y E4-stretch.

### 10.3 Regla de prioridad

> **Regla de oro del equipo:** ante conflicto de tiempo, gana el entregable de la actividad UX de la semana. Un portal impresionante con 70 en las actividades es un mal trade; unas actividades de 100 con un portal honesto de MVP es el objetivo.

---

## 11. EPIC UX (nuevo, transversal): Entregables del Curso {#epic-ux}

**Objetivo:** asegurar 100/100 (y sobrepasar) en las 5 actividades, reutilizando la investigación como insumo de diseño y el producto como evidencia. **Puntos totales de la épica: 28 SP MUST + 4 STRETCH.**

### US-UX-01 — Instrumentos de investigación y trabajo de campo (A1)

**Como** equipo de diseño,
- **quiero** una encuesta estructurada y un guion de entrevista aplicados a usuarios reales del dominio financiero,
- **para que** audiencia, problema, personas y mapas de empatía se sustenten en datos recopilados y no en suposiciones.

**Criterios de Aceptación:**

- Encuesta publicada en Google Forms el lun 20-jul con las 13 preguntas del Anexo A.1 (secciones: screening/demografía, comportamiento y pains, canales).
- Distribución en ≥3 canales (redes de los 3 integrantes: LinkedIn, grupos de trabajo, contactos del sector) con corte el vie 24-jul y meta **n ≥ 15**.
- 3 entrevistas semiestructuradas de 30 min (una por perfil: Operativo, Analista, Directivo) con el guion del Anexo A.2, notas y ≥5 citas textuales cada una.
- Consentimiento registrado según Anexo A.3 (participación voluntaria, datos solo para fines académicos).
- Resultados procesados: gráficas exportables (barras de pains E-09, histograma de horas perdidas E-07, pastel de fuentes consultadas E-06) listas para insertar en el PDF.

**Tareas técnicas:**

- [ ] Montar el formulario en Google Forms con validaciones (obligatorias, rangos)
- [ ] Publicar y monitorear respuestas diario (recordatorio a 48 h)
- [ ] Agendar y ejecutar 3 entrevistas (una por integrante)
- [ ] Exportar respuestas a Sheets y generar las 3 gráficas

**Estimación:** 3 puntos (~1.5 días). **Responsable líder:** Jacqueline. **Sprint:** S1.

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

### US-UX-03 — 6 user personas, 2 por integrante (A1)

**Como** integrante del equipo,
- **quiero** elaborar 2 user personas con la plantilla común del Anexo B según la matriz de asignación §5.3,
- **para que** los 3 perfiles del portal queden representados en 6 personas consistentes y basadas en el trabajo de campo.

**Criterios de Aceptación:**

- Cada persona incluye: foto de perfil (generada con IA, estilo fotográfico consistente entre las 6), nombre, edad, sexo, ocupación; antecedentes (educación, situación familiar, intereses); objetivos (2–3 ligados al portal); pain points y desafíos (3–4, ≥1 proveniente de encuesta/entrevista); comportamientos y hábitos; frase/cita.
- La asignación respeta la matriz §5.3 (cobertura 2×Operativo, 2×Analista, 2×Directivo).
- Cada persona referencia al menos un dato o cita del trabajo de campo (US-UX-01).
- Revisión cruzada: cada integrante revisa las personas de otro antes de integrar.

**Tareas técnicas:**

- [ ] Definir plantilla visual común (1 página por persona)
- [ ] Generar 6 fotos de perfil con IA en estilo homogéneo
- [ ] Redactar 2 personas por integrante y aplicar revisión cruzada

**Estimación:** 3 puntos (1 por integrante, ~0.5 día c/u). **Sprint:** S1.

### US-UX-04 — 6 mapas de empatía, 2 por integrante (A1)

**Como** integrante del equipo,
- **quiero** elaborar los mapas de empatía de mis 2 personas,
- **para que** cada persona tenga su correlato emocional documentado con evidencia de campo.

**Criterios de Aceptación:**

- Cuadrantes etiquetados exactamente **"Says", "Thinks", "Does", "Feels"** (en inglés, como pide la rúbrica).
- ≥3 observaciones por cuadrante, coherentes con la persona correspondiente.
- Al menos un "Says" por mapa es cita textual de las entrevistas (US-UX-01).
- Plantilla visual uniforme entre los 6 mapas (misma retícula y código de color por perfil).

**Tareas técnicas:**

- [ ] Plantilla de 4 cuadrantes reutilizable
- [ ] Volcar citas de entrevistas al cuadrante Says
- [ ] Elaborar 2 mapas por integrante y revisar coherencia persona↔mapa

**Estimación:** 2 puntos (~1 día repartido). **Sprint:** S1.

### US-UX-05 — Escenarios y Journey Maps (A2)

**Como** equipo de diseño,
- **quiero** escenarios de uso narrativos y journey maps por perfil sobre los flujos reales del portal,
- **para que** el recorrido emocional y las oportunidades de diseño queden mapeadas de punta a punta antes de estructurar la información.

**Criterios de Aceptación (provisionales hasta publicarse la rúbrica ⚠️; ajustar con protocolo §25.2):**

- 3 escenarios narrativos, uno por perfil: validación urgente (Operativo), cruce multi-fuente + exportación (Analista), supervisión y decisión (Directivo), basados en los flujos §8.1.
- 3 journey maps con etapas, acciones, puntos de contacto, pensamientos, curva emocional, pain points y oportunidades; cada journey conecta explícitamente con una persona de A1.
- Los pain points de los journeys provienen de la investigación de US-UX-01 (trazabilidad cita→pain→oportunidad).
- Formato visual consistente (misma plantilla los 3) y entregable PDF según convención del curso.

**Tareas técnicas:**

- [ ] Redactar los 3 escenarios narrativos
- [ ] Construir los 3 journey maps (FigJam/Figma)
- [ ] Validar trazabilidad investigación→journey y armar el PDF

**Estimación:** 5 puntos (~2.5 días). **Sprint:** S2.

### US-UX-06 — Análisis competitivo y Arquitectura de Información (A3)

**Como** equipo de diseño,
- **quiero** un benchmark de productos comparables y la arquitectura de información del portal,
- **para que** las decisiones de estructura y navegación estén justificadas frente a alternativas reales y validadas con usuarios.

**Criterios de Aceptación (provisionales ⚠️):**

- Benchmark de 4–6 referentes reales (candidatos: Collibra/Alation/DataHub como catálogos; Power BI/Looker/Metabase como BI; ThoughtSpot como búsqueda conversacional) con matriz de características vs. los 3 perfiles y hallazgos accionables.
- Sitemap completo del portal (login, homes por rol, catálogo, explorador, chat, exportaciones, panel admin) coherente con los permisos RBAC de US-016.
- Card sorting ejecutado (remoto con ≥6 colegas, u optimizado con pre-validación sintética §3.8 declarando método) y su impacto documentado en la taxonomía.
- Flujos de navegación por rol (diagramas) y taxonomía del catálogo alineada a la estrategia RAG bifurcada (§3.5).

**Tareas técnicas:**

- [ ] Investigar y capturar los 4–6 productos del benchmark
- [ ] Construir matriz comparativa y conclusiones
- [ ] Ejecutar card sorting y sintetizar resultados
- [ ] Dibujar sitemap + flujos por rol y armar el PDF

**Estimación:** 4 puntos (~2 días). **Sprint:** S3.

### US-UX-07 — Interfaces de alta fidelidad (A4)

**Como** equipo de diseño,
- **quiero** el sistema de diseño y las pantallas de alta fidelidad del portal, en paridad con el prototipo funcional,
- **para que** la entrega de A4 muestre tanto el diseño pulido como el producto vivo que lo implementa.

**Criterios de Aceptación (provisionales ⚠️):**

- Sistema de diseño documentado: tokens de color (modo claro; oscuro stretch), tipografía, espaciado, estados de componentes (default/hover/focus/error/loading).
- Pantallas de alta fidelidad en Figma: login, home por rol ×3, catálogo con resultados, explorador con filtros, chat con tarjetas de tool call (estados: anunciando/ejecutando/resultado/error), tarjetas predictivas con drill-down, flujo de exportación (solicitud→job→enlace), panel admin de usuarios.
- Paridad demostrada: tabla pantalla-Figma ↔ ruta del prototipo Nuxt donde exista implementación (E4).
- Pre-validación con evaluadores sintéticos condicionados por las 6 personas (§3.8): protocolo, hallazgos y al menos 1 iteración de diseño documentada.

**Tareas técnicas:**

- [ ] Definir tokens y librería de componentes en Figma
- [ ] Diseñar las ~10 pantallas de alta fidelidad
- [ ] Correr pre-validación sintética y aplicar iteración
- [ ] Documentar paridad Figma↔Nuxt y armar el PDF

**Estimación:** 5 puntos (~2.5 días). **Responsable líder:** Alexandro. **Sprint:** S4.

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
- Seed inicial: 200–400 entradas generadas desde los esquemas sintéticos + curaduría manual de ~30 notas tribales.
- Preparado para RAG: el contrato de respuesta ya incluye los campos que consumirá la búsqueda híbrida (US-012) y el agente (US-020/US-021).

**Alcance STRETCH (no comprometido, +1 SP):** sugerencia de fuentes relacionadas ("quien consulta liquidez suele cruzar con créditos").

**Tareas técnicas:**

- [ ] Migración dbmate del esquema del catálogo
- [ ] Modelos SQLModel + seed desde los generadores
- [ ] Endpoint `GET /api/catalog/search` con pruebas
- [ ] Curaduría de notas tribales iniciales

**Estimación:** 3 puntos (~1.5 días). **Sprint:** S2.

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

---

## 19. Roadmap Semanal de Sprints {#19-roadmap}

### Sprint 1 — lun 20 al dom 26 de julio · **ACTIVIDAD 1** (en curso)

**Objetivo:** Entregable A1 con excelencia + base técnica levantada. **SP:** 11 UX (US-UX-01…04) + 8 técnicos (US-001…005 + US-006 v0) = 19.

| Día | Actividad |
|-----|-----------|
| Lun 20 – Mié 22 | Kickoff: confirmar roles y nombre del producto; **publicar encuesta** (US-UX-01); agendar 3 entrevistas; US-001 `make dev` |
| Jue 23 | Redacción secciones de equipo (US-UX-02); US-004 CI mínimo; gate de acceso a Gemini + ADK hello tool; borrador de personas con datos parciales |
| Vie 24 | **Corte de encuesta (n≥15)**; gráficas; 6 personas v1 (US-UX-03); US-006 generadores sintéticos v0; US-005 OTel base |
| Sáb 25 | Última entrevista; 6 mapas de empatía (US-UX-04); integración del PDF; revisión cruzada contra rúbrica §2.2 (checklist §24) |
| **Dom 26** | Ajustes finales + **entrega "Entregable Actividad 1_equipo_8.pdf" en Canvas antes de 23:59** |

### Sprint 2 — lun 27-jul al dom 2-ago · Actividad 2 (Journey Maps)

**Objetivo:** A2 entregada + silos, catálogo, exportación y **login JWT** operativos. **SP:** 5 UX (US-UX-05) + 11 técnicos (US-006 cierre 1, US-007 1, US-008 3, US-009 3, **US-015/016/017 auth+RBAC+sesión 3**) = 16.
Al recibir la rúbrica de A2: protocolo §25.2 (1 h, ajustar US-UX-05). Los journey maps usan los flujos reales §8.1 (ya con login como primera etapa del journey).
**Dom 2-ago: entrega A2.**

### Sprint 3 — lun 3 al dom 9-ago · Actividad 3 (Competitivo + IA) — **sprint crítico**

**Objetivo:** A3 entregada + capa semántica, búsqueda híbrida, **CRUD de usuarios** y agente v1. **SP:** 4 UX (US-UX-06) + 16 técnicos (US-011 5, US-012 3, **US-018/019 usuarios 2**, US-020/021 agente 6) = 20 (−5, el más sobrecomprometido).
Mitigaciones: benchmark competitivo repartido entre los 3 en paralelo; US-020/021 arrancan con las tools de catálogo (US-008 ya listo desde S2); válvula: degradación acordada de US-018/019 (§10.2). El sitemap de A3 incorpora el mapa de permisos (US-016) como evidencia de IA por roles.
**Dom 9-ago: entrega A3.**

### Sprint 4 — lun 10 al dom 16-ago · Actividad 4 (Alta Fidelidad)

**Objetivo:** A4 entregada + frontend completo con patrones UX. **SP:** 5 UX (US-UX-07) + 14 técnicos (US-023/024 streaming cierre 5, US-025 3, US-026/027 3, US-028/029 3) = 19 (−4).
Mitigaciones: Figma y Nuxt comparten sistema de diseño (sin doble trabajo); capturas del prototipo reducen pantallas dibujadas; pre-validación sintética jue–vie.
**Dom 16-ago: entrega A4.**

### Sprint 5 — lun 17 al dom 23-ago · Actividad 5 (Entrega Final)

**Objetivo:** A5 entregada con métricas reales de producción. **SP:** 3 UX (US-UX-08) + 9 técnicos (US-030/031/032 observabilidad 5, US-033/034 pruebas+prod 4) = 12 (+3 buffer que absorbe arrastre de S3/S4).
Pruebas de usabilidad (≥5 usuarios, SUS) sobre el deploy de Cloud Run; documento final integrador; video demo 3 min; presentación.
**Dom 23-ago: entrega final.**

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

## 20. Gates de las Semanas 1–2 {#20-gates}

| Día | Gate | Criterio de éxito |
|-----|------|-------------------|
| Mié 22-jul | Encuesta publicada y distribuida en ≥3 canales | Primeras 5 respuestas registradas |
| Jue 23-jul | Acceso a Gemini 3.5 Flash-Lite verificado (API key en Secret Manager / .env.local) | Respuesta a prompt de prueba con conteo de tokens |
| Jue 23-jul | Google ADK "hello tool" local (`LlmAgent` + function tool dummy) | Tool call ejecutado con traza visible |
| Vie 24-jul | `make dev` reproducible en las 3 máquinas (pnpm + Poetry lockfiles) | FastAPI + Nuxt + Postgres arriba en los 3 entornos |
| Vie 24-jul | Corte de encuesta n≥15 + 2 de 3 entrevistas hechas | Datos suficientes para personas/mapas |
| Sáb 25-jul | PDF A1 completo contra checklist §24 | 100 % de renglones en "Completo" |
| **Dom 26-jul** | **Entrega A1 en Canvas** | Confirmación de subida antes de 23:59 |
| Mié 30-jul | `dbmate up` con migraciones de usuarios/catálogo en las 3 máquinas | `schema.sql` idéntico en los 3 entornos |
| **Vie 1-ago** | **Login JWT funcional end-to-end** (US-015/016/017) | Token con scope de rol; 401 sin token y 403 con rol insuficiente verificados desde el frontend |

---

## 21. Gestión de Riesgos {#21-riesgos}

| ID | Categoría | Riesgo | Prob. | Impacto | Mitigación |
|----|-----------|--------|-------|---------|------------|
| R01 | Curso | Rúbricas A2–A5 difieren de lo asumido | Alta | Alto | Protocolo de absorción §25.2; STRETCH técnicos como válvula; criterios provisionales ya escritos por actividad |
| R02 | Curso | No juntar n≥15 respuestas de encuesta a tiempo | Media | Alto | 3 redes personales + recordatorio a 48 h; plan B: bajar meta a n≥10 y compensar con 1 entrevista extra, declarándolo en el método |
| R03 | Personas | Semana con carga laboral/personal de un integrante | Media | Alto | Trabajo asincrónico, plantillas comunes, revisión cruzada; entregables individuales (personas/mapas) empezados desde el miércoles, no el sábado |
| R04 | Técnica | Curva de aprendizaje de Google ADK | Media | Medio | Gate "hello tool" en S1 (2 semanas antes de US-020); fallback: SDK GenAI directo con tool-calling manual |
| R05 | Técnica | Cuotas/latencia de la API de Gemini en demo | Media | Medio | Caché de respuestas frecuentes; datasets pequeños en demo; `thinking_level` medium; medición temprana de TTFT (S3, no S5) |
| R06 | Técnica | ECharts con millones de puntos degrada UX | Media | Medio | Agregación server-side con Polars antes de graficar; `Lazy*`; degradación acordada a 500 K (§10.2); probar volumen real en S4 día 2 |
| R07 | Confianza | El agente alucina cifras en la demo/prueba de usabilidad | Media | Alto | Tool-calling obligatorio para todo dato (§3.3); respuestas sin tool call no muestran números; set de 30–50 pares de evaluación (STRETCH S5) |
| R08 | Datos | Sintéticos poco creíbles restan seriedad a escenarios | Baja | Medio | Esquemas basados en estructuras públicas típicas (carteras, buckets de liquidez); revisión por los 3 (experiencia del dominio) |
| R09 | FinOps | Costo API/cloud se sale del presupuesto académico | Baja | Bajo | Flash-Lite + scale-to-zero + presupuesto §23 con alerta de billing al 50 % |
| R10 | Alcance | Tentación de construir el alcance descartado (§18) | Alta | Medio | Descarte firmado por el equipo; nueva funcionalidad solo por refinamiento formal (US-037+); la regla de oro §10.3 |
| R11 | Alcance | Scope creep de seguridad (refresh tokens, recuperación de contraseña, OAuth externo, RLS por fila) | Media | Medio | Alcance de US-015…019 cerrado por escrito: JWT access simple + seed de usuarios + CRUD admin; todo lo demás documentado como trabajo futuro en `docs/security.md` |
| R12 | Técnica | Desincronización de esquema de BD entre integrantes | Media | Medio | dbmate como única vía de cambio de esquema; gate del 30-jul (`schema.sql` idéntico en 3 máquinas); migraciones en PR review |

---

## 22. Criterios de Éxito del MVP {#22-criterios}

### 22.1 Curso (los que califican)

- A1: 15/15 con todos los criterios en banda "Completo" (checklist §24).
- A2–A5: 100 en cada rúbrica al publicarse, con al menos un diferenciador por actividad (journey maps sobre flujos reales; benchmark con matriz por perfiles; alta fidelidad + prototipo vivo; usabilidad medida con SUS + pre-validación sintética).
- Documento final que se lee como caso de estudio UX completo (estándar Grocery App, superado en evidencia).

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
| ☐ | Portada (2 %) | Nombres de los 3 integrantes; datos del curso/equipo 8 | Identidad visual del producto (logo/nombre) que reaparecerá en A2–A5 | Alexandro |
| ☐ | Introducción (3 %) | Qué se hizo y cómo está organizado el documento | Párrafo de método: instrumentos + n + fechas de campo | Jacqueline |
| ☐ | Audiencia (5 %) | Clientes/necesidades, pains, demografía, intereses, dónde se conectan, **herramienta y resultados** | Gráficas de la encuesta; tabla de 3 perfiles (§5.1); nota "roles no excluyentes" con dato de E-08 | Jacqueline |
| ☐ | Problema (20 %) | Identificación, cuantificación, impacto, solución; visuales | Diagrama silos antes/después; cuantificación propia (horas/semana buscando datos, de la encuesta); impacto por perfil | Arthur |
| ☐ | Producto (20 %) | Tipo + características y beneficios | Tabla módulo→perfil→beneficio (§6.1); patrones UX 2026 con citas (§6.2); mockup conceptual 1 pantalla | Alexandro |
| ☐ | 6 mapas de empatía (25 %) | 4 cuadrantes Says/Thinks/Does/Feels con observaciones clave | Citas textuales reales de entrevistas en "Says"; plantilla visual uniforme | Cada quien ×2 |
| ☐ | 6 personas (25 %) | Foto, básicos, antecedentes, objetivos, pains, hábitos, frase | Conexión explícita persona↔perfil↔dato de campo; fotos IA consistentes en estilo | Cada quien ×2 |
| ☐ | Formato | PDF, nombre **"Entregable Actividad 1_equipo_8"**, subido por Canvas | Referencias en APA (papers §3 donde aplique); paginación y estilos consistentes | Arthur |

---

## 25. Pendientes y Protocolo para Rúbricas Futuras {#25-pendientes}

### 25.1 Decisiones abiertas del equipo (kickoff)

1. Confirmar roles propuestos (§Equipo) y nombre del producto (§1).
2. ~~Confirmar fechas de desarrollo~~ ✅ Confirmadas 22-jul (§2.1). Falta verificar en Canvas la publicación de cada rúbrica A2–A5.
3. Acordar horario fijo de sync (recomendado: 30 min lun/jue + revisión asíncrona sáb).
4. Confirmar cuenta GCP a usar y presupuesto de billing.

### 25.2 Protocolo de absorción de rúbrica (cuando se publique A2–A5)

1. **T+0 h:** leerla completa; volcarla a tabla criterio→peso→banda "Completo" (formato §2.2).
2. **T+1 h:** mapear cada criterio a la US-UX correspondiente; ajustar sus criterios de aceptación provisionales; recalcular SP.
3. **T+1 día:** si excede lo previsto, congelar STRETCH técnicos del sprint (orden: E5→E4→E2) hasta cubrir el delta.
4. Registrar el ajuste en este documento (sección de la actividad correspondiente) con fecha.

### 25.3 Trabajo explícitamente NO incluido ahora

- Programación de cualquier componente (este documento es solo planeación).
- Todo el alcance descartado de §18: switch A/B de modelos, drift detection, RLS por fila, i18n, paper/benchmark masivo.
- Seguridad avanzada: refresh tokens, recuperación de contraseña, OAuth/SSO externo (documentados como trabajo futuro en `docs/security.md`).

---

## Anexo A: Instrumentos de Investigación (borrador) {#anexo-a}

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

**Plantilla de mapa de empatía:** cabecera con nombre de la persona + 4 cuadrantes **SAY / THINK / DO / FEEL** (≥3 viñetas cada uno; "Say" con ≥1 cita textual del campo).

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

**Última actualización:** miércoles 22 de julio de 2026
**Mantenedor:** Arthur Zizumbo (Platform/Agent lead) — Equipo 8
**Próxima revisión:** al entregar A1 (dom 26-jul) y al publicarse la rúbrica de A2
