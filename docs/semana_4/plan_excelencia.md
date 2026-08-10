# Plan de Excelencia — Actividad 4 (Semana 4)

**Karisma Data · Portal Centralizado de Datos Financieros**
TC4032 Experiencia del usuario y diseño de interfaces · MNA · ITESM · Equipo 8

| | |
|---|---|
| **Actividad** | A4. Interfaces de alta fidelidad |
| **Disponible** | lun 10-ago-2026 00:00 |
| **Entrega** | dom 16-ago-2026 23:59 (meta interna: **20:00**) |
| **Puntos** | 25 |
| **Modalidad** | Colaborativa |
| **Formato** | PDF, nombre exacto `Entregable Actividad 4_equipo_8` |
| **Plan de ejecución** | Una sola persona, ~70 horas entre el lunes por la tarde y el domingo |
| **Rúbrica leída** | lun 10-ago-2026, protocolo §25.2 aplicado (ver sección 2) |

---

## 0. Resumen ejecutivo

La rúbrica reparte los 25 puntos así: **50 % prototipos de alta fidelidad** y **45 % guía de
estilos**. Esas dos cifras cambian la forma de la semana. `US-UX-07` trataba la guía de estilos
como una tarea de tokens dentro del sistema de diseño; la rúbrica la trata como **medio
entregable**, con siete secciones nombradas y 9 puntos por cada una.

La rúbrica **recomienda** Figma y Lunacy, y no las exige: ningún criterio de evaluación las
menciona. La decisión del equipo es construir **la aplicación web real** —Nuxt 4 sobre FastAPI,
desplegada en dos Cloud Run— y que de esas pantallas operables salgan las capturas del documento.
Es la lectura más exigente de la rúbrica, no la más cómoda: sus cuatro requisitos para un
prototipo de alta fidelidad hablan de representar fielmente el producto final, permitir probar
interacciones y funcionalidades, recoger comentarios sobre la estética y hacer entender el
producto a las personas interesadas. Un archivo de diseño cumple dos de los cuatro. Una
aplicación que se abre en el navegador cumple los cuatro.

El punto de partida es duro y conviene decirlo antes que nada: `backend/`, `frontend/`, `db/` y
`ml/` contienen únicamente su `AGENTS.md`. No hay `Makefile`, ni `docker-compose.yml`, ni
`pyproject.toml`, ni `package.json`, ni migraciones, ni CI. Cero de 58 puntos de historia
técnicos comprometidos. Lo que sí existe y sostiene la semana es la arquitectura de información
validada de A3, la paleta y la tipografía versionadas en `uxdoc.sty`, y las ocho personas de A1.

Se entregan **siete pantallas** y **once secciones de guía de estilos**, cuando la rúbrica alcanza
su tope con cinco y cinco. El margen es deliberado: con cinco pantallas justas, una juzgada
«Parcialmente» cuesta puntos que no se recuperan en ningún otro apartado.

---

## 1. La rúbrica de A4, leída literalmente

### 1.1 Reparto de puntos

| # | Apartado | Peso | Puntos de 25 | Modalidad |
|---|---|---|---|---|
| 1 | Portada con los nombres de los integrantes | 2 % | 0.50 | Equipo |
| 2 | Introducción | 3 % | 0.75 | Equipo |
| 3 | Prototipos de alta fidelidad, **10 puntos por prototipo, máximo 50** | 50 % | 12.50 | Equipo |
| 4 | Guía de estilos, **9 puntos por sección, máximo 45** | 45 % | 11.25 | Equipo |
| | **Total** | **100 %** | **25.00** | |

La rúbrica de Canvas expresa los mismos apartados en su escala interna: 0.5, 0.75, 12.5 y 11.25
puntos, con tres bandas cada uno.

### 1.2 El descriptor que define la calificación

Las tres bandas son idénticas a las de A3, y su redacción importa más que su nombre:

- **Completo** — «se incluyen los elementos solicitados».
- **Parcialmente** — «se incluyen los elementos solicitados pero puede carecer de contenido alguno o varios de los elementos».
- **Incompleto** — «faltan elementos solicitados a incluir o el contenido de los elementos es irrelevante».

De aquí sale la misma conclusión que gobernó A3: **la rúbrica no premia profundidad, premia
cobertura demostrada**. Cada elemento pedido debe ser identificable por su propio subtítulo, y
ninguno puede estar escrito en tiempo futuro. «Se definirá la paleta» vale cero; «la paleta es
esta» vale nueve.

Vale la pena notar una peculiaridad del apartado 4 en la rúbrica de Canvas: la tercera banda
también aparece rotulada «Parcialmente» en lugar de «Incompleto», con el descriptor de
incompleto. Es un error de captura del profesor y no cambia nada, pero conviene no confundirse al
comparar bandas.

### 1.3 Los dos topes, y la aritmética que imponen

La rúbrica pone dos multiplicadores con tope:

- Prototipos: **10 puntos cada uno, máximo 50**. El tope se alcanza con **cinco**.
- Guía de estilos: **9 puntos cada sección, máximo 45**. El tope se alcanza con **cinco**, y la
  rúbrica nombra **siete** posibles: identidad de la marca, tipografía, paleta de colores,
  componentes gráficos de la interface, iconografía, conclusiones generales del reporte y
  referencias bibliográficas.

La consecuencia práctica es de gestión de riesgo, no de esfuerzo. Con exactamente cinco
prototipos, una pantalla juzgada «Parcialmente» baja el apartado completo. Con siete, el
evaluador puede castigar dos y el tope de 50 se sigue alcanzando. Lo mismo con las secciones de
la guía: entregamos las siete nombradas más cuatro que la rúbrica menciona en su Sección 2 sin
puntuarlas explícitamente, bajo la frase «sin que este listado sea limitativo».

**Decisión: siete pantallas y once secciones de guía.**

### 1.4 Figma y Lunacy se recomiendan, no se exigen

El texto de la rúbrica es preciso: «Para desarrollar los prototipos **se recomienda** el uso de
dos aplicaciones, una basada en web (Figma) y una más para descarga e instalación (Lunacy)». A
continuación ofrece tutoriales y políticas de privacidad de ambas. Ningún criterio de evaluación
menciona herramienta alguna. Los criterios evalúan **prototipos** y **secciones de la guía**.

Lo que sí exige la rúbrica es una lista de propiedades. Conviene ponerlas frente a las dos
opciones:

| Lo que la rúbrica pide del prototipo | Archivo de diseño | Aplicación web real |
|---|---|---|
| «Ofrecer una representación lo más fiel al producto final» | Aproximada: simula el producto | **Es** el producto: mismo motor de render, misma tipografía, mismos datos |
| «Permitir probar y evaluar interacciones y funcionalidades» | Transiciones prototipadas entre lienzos | Interacciones reales: filtros que filtran, gráficas que hacen zoom, streaming que se cancela |
| «Facilitar la obtención de comentarios detallados de los usuarios acerca de la estética visual» | Sí | Sí, y además sobre comportamiento, latencia y densidad |
| «Ayudar a las personas interesadas a tener un mejor entendimiento del producto final» | Requiere imaginación del lector | Se abre en un navegador y se recorre |

El objetivo de aprendizaje **OEA 2.2** dice «elaborar prototipos alta fidelidad que representen la
interfase de un producto o servicio digital». No dice con qué. La sustitución de herramienta es,
por tanto, un cumplimiento más estricto del objetivo, no una excepción a él.

**Cómo se escribe en el documento.** En la introducción, un párrafo breve y sin tono defensivo:

> La rúbrica recomienda dos aplicaciones de diseño para elaborar los prototipos. Este equipo
> optó por construirlos directamente en el stack del producto —Nuxt 4 sobre FastAPI, desplegado
> en Google Cloud Run— porque las cuatro propiedades que la actividad pide de un prototipo de
> alta fidelidad se cumplen de manera más completa con una interfaz operable que con un archivo
> de diseño: la representación no se aproxima al producto final, es el producto final; las
> interacciones no se simulan, se ejecutan; y las personas interesadas no necesitan imaginar el
> resultado, lo recorren. Cada pantalla de este documento es una captura de la aplicación en
> funcionamiento, tomada a resolución fija con un guion reproducible, y la dirección pública para
> visitarla se incluye en la sección de alcance.

**Riesgo y su cobertura.** Si el evaluador esperaba archivos de diseño, la defensa está en el
documento mismo: el documento entrega todo lo que un archivo de Figma entregaría —el sistema de
tokens completo, el inventario de componentes con sus estados, la retícula, la matriz de
contraste— y además la dirección viva. No se pierde nada por el cambio; se agrega.

### 1.5 El recurso de apoyo que la rúbrica nombra

La rúbrica cita como referencia a Ramírez Mejía (2023), *Grocery shopping app. A guided UX case
study. Part 4: Prototyping and Style Guide*. Ese material define exactamente lo que el profesor
espera ver en una guía de estilos, y conviene copiar su anatomía antes de superarla:

| Lámina del referente | Contenido exacto | Lo que entregaremos |
|---|---|---|
| Paleta | Cuatro familias (primario, secundario 1, secundario 2, complemento), **cinco tonos cada una**, con hex a la vista | Cuatro familias × cinco tonos, más neutros, más semánticos, más **matriz de contraste WCAG verificada por script** y una paleta categórica de series de gráfica |
| Tipografía | Familia, tres pesos, espécimen `Aa 0123456789 abcdefghijklm ABCDEFGHIJKLM`, escala (Title 1 24 pt Bold, Title 2 18 pt, Main 16 pt, Body 14 pt) | Dos familias con su justificación, espécimen, escala de nueve roles con interlineado, y la regla de cifras tabulares |
| Botones | Matriz 3 variantes × 3 estados = 9 celdas | Matriz **3 variantes × 5 estados = 15 celdas**, más variante destructiva y estado de carga |
| Textos y chips | System, placeholder, user input, disabled; chips success, alert, warning | Campos en sus seis estados, chips en cinco semánticas, y badges de rol |
| Iconos | Lámina de iconos | Familia única declarada, tokens de tamaño, grosor de trazo, reglas de alineación y área táctil |

El referente no incluye retícula, movimiento, accesibilidad, voz y tono ni versionado. La propia
rúbrica sí los menciona en su Sección 2. Ahí está el margen de excelencia.

---

## 2. Absorción de la rúbrica — protocolo §25.2 ejecutado

El plan del proyecto obliga a un protocolo de cuatro pasos cuando se publica una rúbrica. Queda
ejecutado y registrado.

### 2.1 Paso 1 — Volcado a tabla criterio → peso → banda

Hecho en la sección 1.1 de este documento, con el formato de §2.2 del plan.

### 2.2 Paso 2 — Mapeo a la US y recálculo

`US-UX-07` es la única historia afectada. Sus criterios de aceptación provisionales se escribieron
el 22-jul asumiendo un prototipo Nuxt en marcha del que salieran capturas para una tabla de
paridad. **El delta contra lo asumido es doble:**

1. **La guía de estilos pesa 45 %.** El criterio 1 de `US-UX-07` la reducía a «tokens de color,
   tipografía, espaciado, estados de componentes». La rúbrica pide once cosas y puntúa siete.
   Esto sube el trabajo de documentación de medio día a día y medio.
2. **La rúbrica cuenta prototipos, no pantallas de una lista fija.** El criterio 2 enumeraba nueve
   pantallas específicas en Figma. La rúbrica solo pide «al menos cinco». Esto libera trabajo:
   permite concentrar la profundidad en siete pantallas bien acabadas en lugar de dispersarla en
   nueve a medias.

Los dos efectos se compensan. **La estimación de `US-UX-07` se mantiene en 5 puntos de historia**
para la parte UX; el trabajo de construcción del prototipo sube de ~8 a ~11 por la Cloud SQL y el
backend real que se decidieron el lunes.

### 2.3 Paso 3 — Congelamiento de STRETCH

No se requiere. Todos los bloques `+N STRETCH` de E2, E3, E4 y E5 ya estaban congelados por la
decisión del 10-ago (§10.2.b). No hay nada que congelar que no lo esté.

### 2.4 Paso 4 — Registro, y las tres contradicciones que se resuelven

Fila lista para pegar en §25.4 del plan:

| Fecha | Rúbrica | Delta contra lo asumido | SP recalculados | STRETCH congelados | Dónde quedó registrado |
|---|---|---|---|---|---|
| lun 10-ago-2026 | A4 — Interfaces de alta fidelidad, 25 pts | La guía de estilos pesa 45 %, no era una tarea de tokens: siete secciones puntuadas a 9 pts. Los prototipos se cuentan por pieza («al menos cinco»), no contra una lista fija de nueve pantallas. Figma y Lunacy se recomiendan, no se exigen | US-UX-07 se mantiene en 5 SP UX; la construcción sube de ~8 a ~11 SP | Ninguno (ya congelados el 10-ago) | `docs/semana_4/plan_excelencia.md`, secciones 1 y 2 |

Y tres contradicciones internas de `US-UX-07` que este documento zanja por escrito:

1. **Figma vs. web.** El criterio 2 dice «Pantallas de alta fidelidad en Figma». **Se sustituye**
   por «Pantallas de alta fidelidad construidas en el stack del producto». La procedencia de los
   tokens ya estaba escrita en el sentido correcto —«cualquier archivo de Figma se deriva de ahí,
   no al revés»—; ahora simplemente no hay archivo de Figma.
2. **Paridad vs. alcance.** El criterio 3 pedía una «tabla pantalla-Figma ↔ ruta del prototipo
   Nuxt». Con un solo artefacto, la paridad no tiene dos lados que comparar. **Colapsa en la
   tabla de alcance de tres estados**, que además es el compromiso de honestidad que el plan
   declara no negociable.
3. **Seis personas vs. ocho.** §3.8 del plan dice seis; `US-UX-07` dice ocho; A1 entregó ocho y A3
   corrió con ocho. **Son ocho.** Queda corregido en toda la cadena.

---

## 3. El estado real desde el que arrancamos

Auditoría del repositorio al lunes 10 de agosto, sin adornos.

**No existe:** `Makefile` · `docker-compose.yml` · ningún `Dockerfile` · `.github/workflows/` ·
`infra/` · `backend/pyproject.toml` · `frontend/package.json` · ningún archivo `.sql` ·
`db/migrations/` · `schema.sql` · `.env.example` · `docs/security.md` · un solo dato sintético en
`data/`. Los cuatro directorios de producto contienen exclusivamente su `AGENTS.md`.

**Sí existe y se reutiliza esta semana:**

| Activo | Ruta | Para qué sirve en A4 |
|---|---|---|
| Sistema de diseño documental, 20 componentes y 11 colores | `docs/entregables/estilo/uxdoc.sty` | **Fuente de los tokens** de Tailwind v4. Garantiza que los cuatro documentos del curso y la interfaz se lean como el mismo producto |
| Arquitectura de información validada | `contenido/a3_03_arquitectura.tex` | Cuatro categorías, nueve facetas transversales. **Contrato** de las siete rutas |
| Mapa de navegación corregido | `contenido/a3_04_mapa.tex` | Barra lateral de dos niveles, revelación progresiva, accesos cruzados |
| Ocho evaluadores prototipo ya condicionados | `docs/entregables/datos/a3_sorts/P1..P8.json` | Insumo directo de la pre-validación del sábado |
| Bosquejo de baja fidelidad | `figuras/a3_wireframe_navegacion.png` | Punto de partida declarado de la alta fidelidad |
| Cadena de compilación LaTeX probada tres veces | `docs/entregables/` | El PDF de A4 se arma con la misma receta |

**Regla operativa que se hereda de §25.5-5 del plan y que rige toda la semana:**

> Mientras no exista el `Makefile`, el QA gate del repositorio es la revisión cruzada del
> entregable, no `make check`. **No se inventan salidas de comandos que no corren.**

---

## 4. Decisión de método: el prototipo web *es* la alta fidelidad

### 4.1 Por qué esta decisión, y no un atajo

El plan ya había registrado el 10-ago que el escenario de riesgo se materializó: tres sprints con
la pista de construcción en cero, y un déficit recalculado en −36 puntos de historia. La respuesta
acordada fue invertir la prioridad y construir solo lo que sostiene A4 y A5.

Lo que este documento añade a esa decisión es que la inversión es **más barata en horas y más
cara en evidencia** de lo que parecía. Dibujar nueve pantallas estáticas con el detalle que exige
la banda «Completo» —estados de hover, focus, error, vacío, sin permiso, en cada componente— toma
un tiempo comparable a construirlas en Tailwind, y produce un artefacto que muere el domingo. La
aplicación, en cambio, es el objeto sobre el que corre la prueba SUS de A5 y el activo que queda
del curso.

### 4.2 Cómo se nombra, y cómo no

| Se dice | No se dice |
|---|---|
| «Prototipo de alta fidelidad navegable» | «Producto en producción» |
| «Navegable con datos de ejemplo» | «Conectado a los sistemas de la institución» |
| «Proyección simulada sobre datos sintéticos» | «Pronóstico» |
| «Respuesta guionizada del asistente, transporte real» | «Respuesta del modelo» |
| «Roadmap declarado» | Silencio |

### 4.3 La tabla de alcance de tres estados, que no es negociable

El documento debe distinguir con exactitud, **pantalla por pantalla**, tres estados: *navegable
con datos de ejemplo* · *navegable sin datos* · *roadmap*. La tabla incluye además las
capacidades que A2 prometió y el catálogo técnico no cubre (§25.5, hallazgo 2): consultas
guardadas, marca de versión retirada con enlace a la vigente, aviso dirigido por cambio de
definición, copiado con procedencia, comparación lado a lado de variables similares y credenciales
de API autogestionadas. **El silencio sobre ellas es lo único que no funciona**: un evaluador
puede contrastar las oportunidades del journey map de A2 contra el prototipo.

---

## 5. Arquitectura de la entrega: una página, siete botones

### 5.1 El índice

La ruta `/` es un índice sobrio con **siete botones**, uno por prototipo. Cada botón lleva:

- el número y nombre de la pantalla,
- la rama del mapa de navegación de A3 de la que procede,
- una etiqueta de alcance con el estado de la tabla de tres estados,
- y el rol con el que conviene entrar (porque la pantalla cambia según el rol).

Debajo, una franja fija con el aviso de alcance: *prototipo de alta fidelidad con datos
sintéticos, no conectado a sistemas reales*. La franja aparece en todas las rutas, no solo en el
índice, para que ninguna captura suelta pueda malinterpretarse.

### 5.2 El contrato de navegación

El mapa de A3 quedó declarado como «contrato de navegación» del producto: cada rama del árbol
tiene ruta y ninguna ruta existe sin rama. Se verifica al final de la semana con una tabla de dos
columnas.

| Ruta | Rama del mapa de A3 |
|---|---|
| `/acceso` | Pantalla de entrada (no es rama; enmarca las demás) |
| `/inicio` | 1. Inicio |
| `/exploracion` | 2. Exploración y extracción — 2.1 Catálogo temático, 2.2 Consulta y filtros |
| `/exploracion/tableros` | 2.4 Tableros e indicadores *(rama nacida de la prueba de árbol)* |
| `/exploracion/exportar` | 2.3 Exportaciones |
| `/gobierno` | 3. Gobierno del dato — 3.1 Diccionario y metadatos, 3.2 Linaje y calidad, 3.3 Catálogo de fuentes |
| `/asistente` | Transversal a las cuatro categorías |
| `/administracion` | 4. Administración — 4.1 a 4.4 |

La barra lateral es fija, de dos niveles, con estado activo permanente y con el segundo nivel
desplegado **solo del módulo en uso** — revelación progresiva, exactamente como el mapa la dejó.
Nada de menú hamburguesa: la decisión está justificada en A3 por tratarse de un entorno
corporativo de escritorio.

### 5.3 Las nueve facetas transversales

Se resuelven como **accesos cruzados, no como duplicados de contenido**. En la práctica:

- «Bitácora de accesos» vive en `/administracion` y tiene un enlace visible desde `/gobierno`,
  que es donde la buscaron los perfiles de auditoría y de propiedad del dato.
- «Calidad de datos» y «Consumo por API» —las dos que seis de los ocho evaluadores pidieron
  duplicar— aparecen como chips de faceta en el panel de metadatos, alcanzables desde
  `/exploracion` y desde `/gobierno`.
- Las siete restantes se marcan con un icono de faceta transversal en la barra lateral, con
  `title` y `aria-label` que explican desde dónde más se llega.

### 5.4 Los cuatro estados transversales

Cada pantalla se diseña en sus cuatro estados no felices, y los cuatro se documentan como parte
de la guía de estilos:

| Estado | Regla |
|---|---|
| **Cargando** | Skeleton con la silueta del contenido real, **sin desplazamiento de maquetación**. Aparece solo si la espera supera 300 ms |
| **Vacío** | Mensaje que explica por qué está vacío y ofrece la acción siguiente. Nunca una caja en blanco |
| **Error** | Causa y camino de recuperación, junto al elemento que falló. Distingue error recuperable de error de permiso |
| **Sin permiso** | Mensaje de rol insuficiente, sin botón de reintento, con indicación de a quién solicitar el acceso |

---

## 6. Las siete pantallas, una por una

Para cada pantalla: de dónde sale, qué contiene, qué patrón de los seis comprometidos demuestra,
y su fila en la tabla de alcance.

### 6.0 Pantalla 0 — Acceso

**Origen.** Marco de entrada del portal. En el plan no contaba como una de las cinco; la rúbrica
cuenta prototipos, así que aquí sí cuenta.

**Contenido.** Marca Karisma Data, campos de correo y contraseña con etiqueta visible sobre el
campo, mostrar/ocultar contraseña, mensaje de error inline bajo el campo, y un selector de perfil
de demostración con los cuatro roles —operativo, analista, directivo, administrador— que permite
al evaluador recorrer los cuatro espacios de trabajo sin credenciales.

**Detalle que la distingue.** El selector de demostración lleva su propia etiqueta: *acceso de
demostración, habilitado únicamente en este prototipo*. Es honestidad y a la vez una facilidad
real para quien evalúa.

**Patrón que demuestra.** Espacios de trabajo por rol: el destino tras entrar cambia según el
perfil.

**Estados.** Normal · campo con error · credencial inválida · cargando · sesión expirada.

### 6.1 Pantalla 1 — Inicio

**Origen.** Categoría 1 de la arquitectura de A3. Primera etapa del journey map de equipo de A2.

**Contenido.** Buscador unificado en posición dominante, búsquedas recientes, favoritos, mis
alertas, y un acceso a mi perfil. La composición **cambia por rol**: el operativo (Laura Méndez)
ve el buscador arriba y ocupando el ancho; el directivo (Arturo Castañeda) ve primero tres
tarjetas de indicador y el buscador reducido; el analista (Diego Hernández) ve accesos al
explorador y a sus exportaciones recientes.

**Fundamento que se cita en el documento.** No se elige un layout universal porque no lo hay: el
estudio de personalización de interfaces generativas midió un acuerdo entre 20 diseñadores
expertos sobre 600 interfaces de apenas kappa 0.25. De ahí que se parta de defaults por rol.

**Patrón que demuestra.** Revelación progresiva y espacios de trabajo por rol.

### 6.2 Pantalla 2 — Exploración y extracción

**Origen.** Categoría 2 de la arquitectura, **ya con la corrección que impuso la prueba de
árbol**: los tableros e indicadores se movieron aquí desde Gobierno porque solo 1 de 8
evaluadores los buscó en Gobierno y 6 vinieron a Exploración.

Es la pantalla más densa y la que más peso tiene. Se compone de tres zonas:

**Zona A — Catálogo temático facetado.** Seis temas (cartera de crédito, liquidez, derivados,
captación, mercado de dinero, acciones), facetas laterales, resultados en tabla densa con
cabecera fija, ordenamiento con `aria-sort`, y panel de metadatos a la derecha que acompaña al
resultado seleccionado **sin abandonar el contexto de la consulta**. Ese panel es la respuesta
directa a la brecha de conocimiento que A2 marcó en la etapa de validación: definición,
propietario, fecha de vigencia y linaje, junto a la cifra.

**Zona B — Consulta y filtros.** Filtros avanzados, vista previa del resultado, compartir consulta.

**Zona C — 2.4 Tableros e indicadores.** Aquí vive la evidencia de rendimiento:

- Serie temporal de **500 000 puntos preagregados server-side con Polars**, renderizada con
  Apache ECharts vía `vue-echarts` como `LazyVChart`, con `sampling: 'lttb'` y `large: true`.
  La cifra es la degradación acordada de antemano frente al millón original, y se declara como
  tal en el documento, no se disfraza.
- **Drill-down de tres niveles en dos clics como máximo**: tarjeta → panel expandible con la
  serie → tabla de detalle → enlace al explorador.
- **Tres tarjetas predictivas** con proyección estática, cada una con **etiqueta de método
  visible**: por ejemplo *«Riesgo de liquidez +12 % el próximo mes — proyección lineal sobre
  datos sintéticos»*. No se finge aprendizaje automático.
- Toda gráfica lleva su **alternativa en tabla** y un **resumen textual** para lector de
  pantalla.

**Patrones que demuestra.** Tarjetas predictivas con drill-down; estado compartido tablero↔chat
(los filtros activos viajan como contexto a `/asistente`); revelación progresiva.

### 6.3 Pantalla 3 — Gobierno del dato

**Origen.** Categoría 3, renombrada tras el card sorting: dejó de llamarse «Gobierno y
Supervisión» al salir de ahí los tableros, y conserva solo el marco del dato.

**Contenido.** Diccionario de datos, metadatos y reglas de negocio; linaje, calidad de datos y
monitoreo de cargas; catálogo de fuentes con su faceta transversal; y el acceso cruzado a la
bitácora de accesos que vive en Administración.

**La pieza central: el overlay de linaje explicable.** Al expandir un campo, un panel superpuesto
muestra el recorrido del dato desde su sistema de origen hasta la cifra que se está mirando, con
las transformaciones intermedias, el propietario responsable y la fecha de vigencia. El overlay
**se despliega bajo demanda y no altera el flujo de lectura**: se cierra y la pantalla queda como
estaba.

Esta pantalla es el «momento de la verdad» del journey map de A2 —el punto en que el usuario
decide si confía en la cifra que se lleva— y por eso recibe el mayor cuidado tipográfico y de
jerarquía de las siete.

**Patrón que demuestra.** Overlay de linaje explicable.

### 6.4 Pantalla 4 — Asistente conversacional

**Origen.** El diferenciador del proyecto, transversal a las cuatro categorías. Escenarios 1 y 3
de A2.

Es la única de las siete que **no se puede simular en un archivo de diseño**, y por eso es la que
más justifica la decisión de método de la sección 4.

**Cómo está construida.** El endpoint `/api/chat` de FastAPI emite **Server-Sent Events reales**
desde un generador asíncrono, con cuatro tipos de evento tipados: `tool_call`, `token`, `error`,
`done`. El contenido de esta semana es **determinista y guionizado**, y así se etiqueta en
pantalla y en el documento. Lo que es real —y es lo que importa demostrar— es el transporte, el
orden de los eventos y la cancelación.

**Los cuatro estados de la tarjeta de tool call**, que se muestran en secuencia dentro de la
conversación y también como galería en la guía de estilos:

| Estado | Qué muestra | Copia de ejemplo |
|---|---|---|
| 1. Anuncio | Qué va a consultar, antes de tener el dato | «Consultando base de liquidez…» |
| 2. Ejecución | Indicador de progreso y tiempo transcurrido | «Consultando base de liquidez · 1.2 s» |
| 3. Resultado | Mini-tabla o cifra **antes** del texto generado | Tabla de 3 filas con la fuente citada |
| 4. Error | Qué paso falló y qué hacer | «No se pudo leer el silo de derivados. Reintentar» |

**El botón Detener.** Visible durante toda la generación. Al pulsarlo, el cliente aborta la
petición, el backend detecta la desconexión y **cancela el generador de verdad**, dejando registro
del evento. La prueba de que la cancelación es real y no cosmética se documenta con una captura
del registro del servidor y una nota de latencia.

**Regla anti-alucinación, que aplica aunque el contenido sea guionizado.** Toda cifra que aparece
en una respuesta procede de una tarjeta de tool call visible y cita su fuente del catálogo. Sin
tarjeta, no hay número. Esa es la disciplina que se está prototipando, y prototiparla mal ahora
enseñaría el hábito equivocado en A5.

**Patrones que demuestra.** Transparencia de tool call; streaming real y cancelable.

**Go/no-go del sábado 15 a las 12:00.** Si el andamiaje está verde y sobran horas, Gemini 3.5
Flash-Lite se enchufa **detrás del mismo contrato de eventos**, sin tocar el cliente. Si no, se
entrega guionizado y se declara. El contrato de eventos se diseña desde el viernes pensando en
que ese cambio sea de una hora, no de un día.

### 6.5 Pantalla 5 — Administración

**Origen.** Categoría 4 de la arquitectura. Escenario 5 de A2, el de acceso mínimo suficiente.

**Contenido.** Usuarios, roles y permisos con la degradación ya acordada —listar, cambiar rol y
desactivar, sin formulario de edición completa—; solicitudes y aprobaciones; bitácora de accesos
con el acceso cruzado desde Gobierno; e integraciones con credenciales API y consumo por API.

**Detalle con respaldo empírico.** «Credenciales API» permanece en segundo nivel dentro de «4.4
Integraciones». Era la única predicción falsable que el documento de A3 dejó escrita antes de la
prueba, y la prueba la confirmó: 7 de 8 evaluadores resolvieron la tarea al primer intento y solo
3 titubearon. Se conserva sin tocar y el documento lo dice.

**Regla de seguridad visible.** Las acciones destructivas —desactivar usuario, revocar
credencial— usan el color semántico destructivo, están separadas espacialmente de las acciones
normales y piden confirmación. Un administrador no puede desactivarse a sí mismo.

**Patrón que demuestra.** Espacios de trabajo por rol; gobierno de acceso demostrable.

### 6.6 Pantalla 6 — Exportación

**Origen.** Rama 2.3 del mapa. Escenario 2 de A2, el del analista que necesita datos crudos.

**Contenido.** El flujo completo en tres momentos, que es justamente lo que un archivo de diseño
representa mal porque el valor está en el tiempo:

1. **Solicitud** — selección de fuentes, formato CSV o Excel, y estimación de filas.
2. **Trabajo en curso** — la petición devuelve un identificador de trabajo de inmediato y **la
   interfaz nunca se bloquea**. El usuario puede seguir navegando; el estado se consulta desde
   cualquier pantalla.
3. **Enlace** — historial de exportaciones con el enlace firmado y su fecha de caducidad a 24
   horas.

**Patrón que demuestra.** Trabajo pesado en segundo plano sin bloquear la interfaz. Es la
respuesta directa al punto de fricción que A2 registró en la etapa de extracción.

### 6.7 Cobertura de perfiles

Las siete pantallas cubren los ocho perfiles de A1 agrupados en cuatro espacios de trabajo, tal
como la arquitectura de A3 los resolvió. La tabla va en el documento:

| Perfil de A1 | Persona | Espacio de trabajo | Pantalla principal |
|---|---|---|---|
| Consulta operativa | Laura Méndez *(primaria)* | Operativo | 1. Inicio |
| Análisis de datos | Diego Hernández | Analista | 2. Exploración · 6. Exportación |
| Gobierno y calidad | Roberto Valdez | Analista | 3. Gobierno del dato |
| Control y auditoría | Elena Ruiz | Analista | 3. Gobierno → 5. Bitácora |
| Habilitación técnica | Jorge Mendieta | Analista | 3. Gobierno del dato |
| Supervisión directiva | Arturo Castañeda | Directivo | 2.4 Tableros · 4. Asistente |
| Administración de plataforma | Mariana Ovalle Ríos | Administrador | 5. Administración |
| Integración de aplicaciones | Ximena Solís Barrera | Administrador | 5.4 Integraciones |

---

## 7. El sistema de diseño y la guía de estilos

Esta sección **es** el 45 % de la calificación. Se escribe con la disciplina de una guía real, no
como apéndice.

### 7.1 Cadena de derivación, en un solo sentido

```
uxdoc.sty  →  generar_tokens_a4.py  →  main.css (@theme de Tailwind v4)  →  interfaz
                        ↓                              ↓
            matriz de contraste            capturas Playwright
                        ↓                              ↓
                    láminas de la guía  →  PDF de la Actividad 4
```

La regla es que **nada fluye hacia atrás**. La paleta que el documento imprime y la que el
navegador pinta salen del mismo archivo, generadas por el mismo script. No pueden divergir.

Esto no es un detalle técnico, es un argumento de la actividad: la guía de estilos de un producto
digital que no está enlazada al código es un documento que envejece el día que se entrega.

### 7.2 Identidad de la marca *(sección puntuada 1/7)*

**Karisma Data · Portal Centralizado de Datos Financieros.** El símbolo representa fuentes
dispersas que convergen en un único dato con autoridad; el logotipo compuesto se arma como
símbolo más nombre en Lexend Deca, de modo que el texto sea siempre vectorial.

Contenido de la sección: significado del símbolo · construcción del logotipo compuesto · área de
resguardo (una altura de símbolo por cada lado) · tamaño mínimo (16 px de alto para el símbolo
solo, 96 px de ancho para el compuesto) · versiones permitidas (positiva sobre superficie clara,
negativa sobre primaria 700 y 900, símbolo solo para favicon y avatar) · **usos incorrectos
ilustrados** (deformar la proporción, recolorear fuera de la paleta, colocar sobre fotografía sin
capa de contraste, añadir sombra o contorno) · y la relación entre la marca del producto y la
institucional del Tec, que conviven en la portada de los entregables pero no en la interfaz.

Atributos de marca que gobiernan las decisiones visuales, en orden: **confiable · preciso ·
sobrio · rápido**. Cuando dos opciones de diseño empatan, gana la que refuerza el primero.

### 7.3 Tipografía *(sección puntuada 2/7)*

**Titulares: Lexend Deca.** Elegida por su legibilidad en tamaños grandes y su carácter
corporativo sin rigidez. Se distribuye únicamente en peso Regular, y ese límite es una decisión
de diseño, no una carencia: **la jerarquía se construye con tamaño, color y filete, nunca con
negrita simulada**.

**Cuerpo: Fira Sans.** Humanista, con altura de x generosa, buenas cifras y un juego completo de
pesos. Rinde bien a 12-14 px, que es la escala real de un producto denso de escritorio.

Espécimen que va en la lámina, replicando el formato del referente:
`Aa 0123456789 abcdefghijklm ABCDEFGHIJKLM` en cada familia y peso.

**Escala tipográfica de nueve roles:**

| Rol | Familia | Tamaño / interlineado | Peso | Uso |
|---|---|---|---|---|
| Display | Lexend Deca | 32 / 40 | Regular | Título del índice de prototipos |
| Título 1 | Lexend Deca | 24 / 32 | Regular | Encabezado de pantalla |
| Título 2 | Lexend Deca | 18 / 26 | Regular | Sección dentro de una pantalla |
| Título 3 | Fira Sans | 16 / 24 | Medium 500 | Encabezado de tarjeta y de panel |
| Cuerpo | Fira Sans | 14 / 21 | Regular | Texto general de la interfaz |
| Cuerpo amplio | Fira Sans | 16 / 24 | Regular | Prosa larga y campos de formulario |
| Etiqueta | Fira Sans | 12 / 16 | Medium 500 | Rótulos, cabeceras de tabla, chips |
| Dato tabular | Fira Sans | 13 / 20 | Regular | Celdas numéricas, con cifras tabulares |
| Micro | Fira Sans | 11 / 15 | Regular | Marcas de tiempo y notas al pie de tarjeta |

**Tres reglas que se documentan y se justifican:**

1. **Cifras tabulares obligatorias.** Toda columna numérica, todo importe y todo contador usan
   `font-variant-numeric: tabular-nums`. Sin esto las columnas bailan al actualizarse y un portal
   financiero pierde credibilidad en el primer parpadeo.
2. **14 px de cuerpo en escritorio, 16 px en campos por debajo de 768 px.** La recomendación
   general de 16 px de cuerpo está pensada para lectura móvil; este es un producto denso de
   escritorio y la ficha de estilo que corresponde a esta categoría fija 12-14 px. La excepción
   son los campos de formulario en pantallas estrechas, que suben a 16 px para evitar el
   auto-zoom de iOS. Se declara la tensión y se resuelve, en lugar de ignorar una de las dos
   reglas.
3. **Medida de línea entre 60 y 75 caracteres** en todo bloque de prosa; las tablas y los paneles
   quedan exentos por naturaleza.

### 7.4 Paleta de colores *(sección puntuada 3/7)*

Cuatro familias de cinco tonos, replicando la estructura del referente y anclando cada familia en
un color ya versionado en `uxdoc.sty`, de modo que los documentos del curso y la interfaz sean el
mismo producto.

**Primaria — Azul institucional.** Estructura, navegación, acciones primarias, titulares.

| Tono | Hex | Uso |
|---|---|---|
| 100 | `#DBE7FD` | Fondo de estado seleccionado |
| 300 | `#7BA3F5` | Bordes activos, relleno secundario de gráfica |
| **500** | **`#2563EB`** | **Ancla.** Botón primario, enlaces, foco |
| 700 | `#1F4D78` | Cabeceras de tabla, barra lateral, titulares |
| 900 | `#132F49` | Texto sobre superficie primaria clara |

**Secundaria — Azul de datos.** Series, rellenos, cuadrantes, superficies informativas.

| Tono | Hex | Uso |
|---|---|---|
| 100 | `#E8F0FE` | Superficie de panel informativo |
| 300 | `#B8CCE4` | Relleno suave, área bajo curva |
| **500** | **`#3B82F6`** | **Ancla.** Serie primaria de gráfica |
| 700 | `#1D4ED8` | Serie primaria en modo denso |
| 900 | `#152F63` | Contorno de serie sobre fondo claro |

**Acento — Ámbar.** Uso escaso y deliberado: filete bajo titulares, marca, momento de la verdad,
estado «requiere atención».

| Tono | Hex | Uso |
|---|---|---|
| 100 | `#FEEBD9` | Fondo de aviso |
| 300 | `#FBB273` | Borde de aviso |
| **500** | **`#F97316`** | **Ancla.** Filete, marcador de cambio, icono de atención |
| 700 | `#C2540A` | **Texto de aviso** (el 500 no alcanza contraste para texto) |
| 900 | `#7C3606` | Texto de aviso en alta densidad |

**Complemento — Verde de confirmación.** Dato vigente, validación superada, trabajo completado.

| Tono | Hex | Uso |
|---|---|---|
| 100 | `#DCFCE7` | Fondo de confirmación |
| 300 | `#5FC783` | Borde de confirmación |
| 500 | `#22A055` | Icono y marcador de éxito |
| **700** | **`#166534`** | **Ancla.** Texto de confirmación |
| 900 | `#0C3D1F` | Texto de confirmación en alta densidad |

**Neutros.** `#F8FAFC` superficie · `#EEF3FA` fila alterna de tabla · `#CBD5E1` filete ·
`#94A3B8` texto deshabilitado · `#64748B` texto secundario · `#1E293B` texto · `#0F172A` texto de
máximo énfasis.

**Semánticos.** Destructivo `#EF4444` con `#B91C1C` para texto · advertencia `#C2540A` ·
informativo `#2563EB` · éxito `#166534`.

**Regla que gobierna todo lo anterior: no hay negro puro ni blanco puro.** La superficie más clara
es `#F8FAFC` y el texto más oscuro es `#0F172A`.

**Matriz de contraste, verificada por script y no a ojo.** El documento imprime la matriz
completa; estas son las tres reglas que salen de ella y que hay que respetar sin excepción:

| Combinación | Ratio | Veredicto |
|---|---|---|
| `#1E293B` sobre `#F8FAFC` | ≈ 13:1 | AAA. Texto de cuerpo |
| Blanco sobre `#2563EB` | ≈ 5.2:1 | AA. Botón primario |
| Blanco sobre `#166534` | ≈ 7.4:1 | AAA. Confirmación |
| `#64748B` sobre `#F8FAFC` | ≈ 4.6:1 | AA justo. **Solo texto secundario de 14 px o más** |
| **Blanco sobre `#F97316`** | **≈ 2.6:1** | **Falla.** El ámbar nunca lleva texto blanco; el texto de aviso usa `#C2540A` sobre `#FEEBD9` |

**Paleta categórica de series**, distinta de la paleta de marca porque una gráfica con seis series
en tonos del mismo azul es ilegible. Seis hues distinguibles en deuteranopia, y cada serie lleva
además **forma de marcador y patrón de línea propios**, de modo que la información no dependa del
color:

| # | Hex | Marcador | Línea |
|---|---|---|---|
| 1 | `#2563EB` | Círculo | Sólida |
| 2 | `#F97316` | Triángulo arriba | Discontinua |
| 3 | `#0F766E` | Cuadrado | Punteada |
| 4 | `#7C3AED` | Rombo | Guión-punto |
| 5 | `#B91C1C` | Triángulo abajo | Sólida gruesa |
| 6 | `#64748B` | Cruz | Discontinua fina |

Sobre esa base, tres colores semánticos que **nunca** se usan para categorías: positivo `#166534`,
negativo `#B91C1C`, neutro `#94A3B8`.

**Modo oscuro.** Declarado explícitamente como fuera de alcance de esta entrega, con la razón: un
modo oscuro mal contrastado resta más de lo que suma, y la semana no da para verificar dos
paletas. Queda en el roadmap de la guía con su versión asignada.

### 7.5 Componentes gráficos de la interface *(sección puntuada 4/7)*

**Botones — matriz de 15 celdas**, frente a las 9 del referente.

Tres variantes: **Contenido** (acción primaria, una por pantalla), **Contorno** (acción
secundaria), **Texto** (acción terciaria y de navegación). Cinco estados por variante: normal,
hover, **focus visible**, activo, deshabilitado. Más dos filas adicionales: **carga** (con
indicador y el botón inhabilitado durante la operación) y **destructivo** (en color semántico y
separado espacialmente de las acciones normales).

Reglas de la lámina: altura 32 px en densidad alta y 40 px en densidad normal · área táctil mínima
de 44 × 44 px aunque el botón se vea más pequeño · **el rótulo nunca se parte en dos líneas** ·
**una sola acción primaria por pantalla** · icono siempre a la izquierda del texto y alineado a la
línea base.

**Campos de formulario — seis estados.** Normal, con foco, con valor, error, deshabilitado y solo
lectura, que es distinto de deshabilitado y se ve distinto. Reglas: **etiqueta visible sobre el
campo**, nunca solo el marcador de posición · texto de ayuda persistente bajo los campos
complejos · **el error va debajo del campo que falló**, no en un resumen al principio · validación
al salir del campo, no en cada tecla · el error se anuncia con `role="alert"`.

**Chips y badges — cinco semánticas.** Neutro, informativo, éxito, aviso, error. Más los badges de
rol (operativo, analista, directivo, administrador) y el chip de faceta transversal, que lleva su
icono propio. Todos con icono además de color, por la regla de no depender del color.

**Tablas de datos.** Cabecera fija al desplazar · altura de fila de 36 px · fila alterna
`#EEF3FA` · resaltado al pasar el cursor · ordenamiento con `aria-sort` reflejando el estado ·
cifras alineadas a la derecha con cifras tabulares · columna de acciones anclada a la derecha ·
paginación o virtualización a partir de 50 filas.

**Tarjetas KPI.** Rótulo, cifra grande en cifras tabulares, variación con signo, icono de
dirección y **micrográfica de tendencia**. La variación nunca se comunica solo con color: lleva
flecha y signo.

**Tarjeta de tool call.** Sus cuatro estados, con la anatomía completa: icono de herramienta,
nombre legible de la operación, tiempo transcurrido, resultado plegable y cita de fuente. Se
imprime como galería en la guía y en secuencia en la pantalla 4.

**Panel de metadatos.** Encabezado con el nombre del campo, bloque de definición, propietario,
fecha de vigencia, chips de faceta, y el disparador del overlay de linaje.

**Navegación.** Barra lateral de 240 px con dos niveles, estado activo permanente, segundo nivel
desplegado solo del módulo en uso, y barra superior de 56 px con buscador, rol activo y menú de
usuario.

**Superposiciones.** Modal, panel lateral y overlay de linaje comparten reglas: velo al 50 % de
negro, cierre con `Esc` y con clic fuera, foco atrapado dentro mientras están abiertos, foco
devuelto al disparador al cerrar, y confirmación si hay cambios sin guardar.

**Retroalimentación.** Toast que se descarta solo a los cuatro segundos, que **no roba el foco** y
que se anuncia con `aria-live="polite"` · skeleton · barra de progreso indeterminada.

### 7.6 Iconografía *(sección puntuada 5/7)*

**Una sola familia para todo el producto: Lucide.** No se mezclan familias y no se dibujan iconos
a mano. La razón se escribe: mezclar familias produce grosores y radios inconsistentes que el ojo
detecta aunque el lector no sepa nombrar por qué algo se ve poco cuidado.

Reglas: grosor de trazo **1.5 px en todos los tamaños** · tokens de tamaño **16 / 20 / 24 px**, sin
valores intermedios · alineación a la línea base del texto que acompañan · **contorno en toda la
interfaz, relleno reservado exclusivamente al estado activo** de la navegación · área táctil de 44
× 44 px aunque el icono mida 16 · **`aria-label` obligatorio en todo icono sin texto** · contraste
mínimo 3:1 contra su fondo · **nunca emoji como icono estructural**.

Inventario del producto, agrupado por función y con el nombre exacto del icono: navegación (los
cuatro módulos), acciones (buscar, filtrar, exportar, compartir, copiar), estado (vigente, en
revisión, retirado, error), datos (tabla, gráfica, linaje, fuente), gobierno (diccionario,
calidad, carga), administración (usuario, rol, llave, bitácora) y asistente (enviar, detener,
herramienta, reintentar).

### 7.7 Imágenes e ilustraciones

Regla que ya costó descubrir en A1 y que aquí se documenta como norma: **los modelos de imagen se
usan solo para fotografía y marca, nunca para diagramas con texto en español.** Las figuras con
etiquetas se generan con matplotlib o con HTML y CSS; los retratos de las personas y las escenas
de contexto, con modelo de imagen y con lista negativa explícita de texto, letras, números y
logotipos.

En la interfaz no hay fotografía decorativa. Las únicas imágenes son la marca, los avatares
iniciales generados a partir de las iniciales del usuario, y los gráficos de datos.

### 7.8 Retícula, espaciado y diseño adaptativo

Retícula de **12 columnas** con canal de 8 px. Ritmo de espaciado en base 4: **4, 8, 12, 16, 24,
32, 48, 64**, sin valores fuera de la escala.

Tokens de densidad, tomados de la ficha de estilo que corresponde a un producto de tablero denso:

```css
--sidebar-width: 240px;
--header-height: 56px;
--grid-gap: 8px;
--card-padding: 12px;
--table-row-height: 36px;
```

**Una sola escala de radios**, y su única excepción documentada:

```css
--radius-sm: 4px;    /* campos, botones, chips cuadrados */
--radius-md: 6px;    /* tarjetas, paneles */
--radius-lg: 10px;   /* modales, hojas laterales */
--radius-full: 999px; /* excepción única: badges de rol y avatares */
```

**Tres niveles de sombra y ni uno más:** reposo (sin sombra, solo filete), elevado (tarjeta sobre
superficie) y flotante (modal y menú). Mezclar sistemas de elevación es el error que más rápido
delata una interfaz sin sistema.

Puntos de quiebre: **1440 / 1280 / 1024 / 768**. El producto es de escritorio; por debajo de 1024
px la barra lateral colapsa a iconos y por debajo de 768 px las tablas pasan a tarjetas apiladas.
**Nunca hay desplazamiento horizontal de página**: las tablas anchas se desplazan dentro de su
propio contenedor.

### 7.9 Microinteracciones y animaciones

Duración **150-300 ms** para microinteracciones, hasta 400 ms para transiciones complejas, nunca
más de 500 ms. Curva `ease-out` al entrar y `ease-in` al salir, con la salida al 60-70 % de la
duración de la entrada, porque una salida lenta se percibe como lentitud del sistema.

**Solo se animan `transform` y `opacity`.** Nunca `width`, `height`, `top` ni `left`: provocan
recálculo de maquetación y saltos.

**Toda animación comunica algo.** El inventario del producto es corto a propósito, y cada entrada
declara qué comunica:

| Animación | Duración | Qué comunica |
|---|---|---|
| Despliegue del segundo nivel de la barra lateral | 200 ms | Que ese contenido pertenece al módulo abierto |
| Aparición de tarjeta de tool call | 180 ms | Que el sistema empezó a trabajar |
| Llegada de token en el streaming | continuo | Progreso real, no simulado |
| Apertura del overlay de linaje | 240 ms desde el disparador | De dónde viene el panel y adónde vuelve |
| Transición de nivel en el drill-down | 220 ms | Que se está bajando en la misma jerarquía |
| Toast | 150 ms entrar / 100 ms salir | Confirmación sin interrumpir |

`prefers-reduced-motion` se respeta en las seis: las transiciones se reducen a cambio de opacidad
o se eliminan, y el streaming pasa a mostrar la respuesta completa al terminar.

### 7.10 Directrices de accesibilidad

- Contraste **4.5:1 en texto** y **3:1 en elementos gráficos y datos**, verificado por script y
  publicado como matriz.
- **Anillo de foco visible** de 2 px en todo elemento interactivo. No se elimina nunca.
- Orden de tabulación **igual al orden visual**. Enlace de salto al contenido principal.
- Jerarquía de encabezados secuencial, sin saltar niveles.
- **La información nunca depende solo del color**: se acompaña de icono, forma, patrón o texto.
- Toda gráfica tiene **alternativa en tabla** y **resumen textual** para lector de pantalla.
- Los iconos sin texto llevan `aria-label`; las imágenes significativas, texto alternativo.
- Los errores de formulario se anuncian con `role="alert"` y el foco va al primer campo inválido.
- El contenido se mantiene legible al 200 % de escala de texto, sin truncamientos.
- Área táctil mínima de 44 × 44 px.

### 7.11 Voz y tono

Español neutro. **Sin emojis** en ninguna cadena de la interfaz. Segunda persona en las acciones
(«Exportar», no «Exportación»). Los mensajes de error dicen **causa y remedio**, nunca solo
«Datos inválidos». Las cifras se acompañan siempre de su fuente. Las proyecciones llevan su
etiqueta de método a la vista. No hay superlativos ni lenguaje comercial: es una herramienta de
trabajo, y el tono que la marca reclama es «confiable, preciso, sobrio».

Tabla de ocho pares «se dice / no se dice» en el documento, incluyendo los cuatro de la sección
4.2 de este plan.

### 7.12 Documentación y control de versiones de la guía

La guía se versiona con el producto. **v1.0, 16-ago-2026.** Vive en dos lugares que no pueden
divergir porque salen del mismo generador: el bloque `@theme` de
`frontend/app/assets/css/main.css` y esta sección del PDF. Todo cambio entra por modificación del
generador, nunca editando el CSS o el documento por separado. La bitácora de cambios registra
fecha, qué cambió, por qué y quién lo aprobó. Entradas ya previstas para v1.1: modo oscuro,
densidad compacta y las correcciones que salgan de la prueba SUS de A5.

### 7.13 Conclusiones generales del reporte *(sección puntuada 6/7)*

No es un resumen. Es la sección donde se cierra el argumento de la actividad: qué se aprendió al
convertir una arquitectura validada en pantallas, qué decisión de diseño cambió por evidencia y
no por gusto, qué quedó fuera y por qué, y qué se lleva la Actividad 5. Se escribe **en pasado y
con cifras**, siguiendo la disciplina que ya funcionó en A3.

### 7.14 Referencias bibliográficas *(sección puntuada 7/7)*

Ver sección 15 de este plan.

---

## 8. Evaluación de `taste-skill` e `impeccable.style`

Se revisaron ambas a petición del usuario, junto a la que ya está en uso.

### 8.1 `ui-ux-pro-max` — se queda como fuente generativa única

Ya es la procedencia documentada del sistema de diseño de A1 a A3: `uxdoc.sty` declara en su
cabecera que su paleta y tipografía derivan de la consulta *«enterprise data governance platform,
professional, trustworthy»*. Consultada de nuevo para el producto, devuelve la ficha **Data-Dense
Dashboard**, que es exactamente la categoría de este portal, y con ella los tokens de densidad que
la sección 7.8 adopta y las reglas de gráficas que la 7.4 y la 6.2 aplican: agregar por intervalos
por encima de 10 000 puntos, leyenda interactiva, tabla alternativa obligatoria, contraste de dato
de 3:1, ordenamiento con `aria-sort`.

**Veredicto: se mantiene.** No hay razón para cambiar la fuente a mitad del proyecto, y el
argumento de continuidad entre los cinco documentos del curso y la interfaz depende de ella.

### 8.2 `taste-skill` — complementa en una sola pantalla, y hay que decir en cuál

El propio SKILL.md declara **fuera de alcance**: *«Dashboards, dense product UI, data tables,
multi-step forms»*. Eso describe **seis de nuestras siete pantallas**. Como sistema de diseño, no
aplica: está pensado para páginas de aterrizaje, portafolios y rediseños de marca.

Donde sí aplica es en la ruta `/`, que es literalmente una página de aterrizaje: el índice con los
siete botones. Y su lista de «forbidden AI tells» es útil como **checklist de revisión** para todo
el producto, porque cataloga los defectos que delatan una interfaz generada sin criterio.

**Se adopta como checklist, no como sistema.** Diez reglas concretas que entran en la revisión del
sábado:

1. Un solo color de acento en toda la página, sin excepción.
2. Una sola escala de radios (ya en la sección 7.8).
3. Una sola familia de iconos, sin SVG dibujados a mano (ya en la 7.6).
4. Ni negro puro ni blanco puro (ya en la 7.4).
5. Prohibido el falso producto dibujado con `div`: se ponen **capturas reales**, que es justo lo
   que esta entrega tiene.
6. Verificación de contraste en botones, sin botón blanco con texto blanco ni botón transparente
   sin borde.
7. Sin rótulo de CTA que se parta en dos líneas en escritorio.
8. Sin dos llamadas a la acción con la misma intención en una misma página.
9. Sin etiquetas de versión decorativas ni tiras de texto ornamental del tipo `001 · Índice`.
10. El movimiento debe estar motivado; sin marquesinas y sin `addEventListener("scroll")` a mano.

**Y dos reglas suyas que se rechazan, con razón escrita**, porque adoptar una guía entera sin
criterio es el error que la propia guía denuncia:

- **La prohibición total del guion largo.** Es una heurística anti-slop pensada para copia
  publicitaria en inglés. En prosa española el guion largo es tipografía correcta y los cuatro
  documentos previos del curso lo usan. Se conserva en el documento; en las cadenas de interfaz,
  que son cortas, no aparece de todos modos.
- **La exigencia de fotografía real en toda página.** Este es un producto de datos. La sección 7.7
  ya declara que no hay fotografía decorativa, y añadirla restaría seriedad.

### 8.3 `impeccable.style` — complementa como auditoría, y no se instala esta semana

Es un sistema de detección: 58 verificaciones que atrapan los defectos por omisión que los agentes
producen, 23 comandos (`/polish`, `/audit`, `/typeset`, `/distill`), extensión de navegador con
capa de detección, integración en revisión de pull request, y exportación de un `DESIGN.md`
portable. Se distribuye como skill de Claude Code y como CLI. Es gratuito.

Es genuinamente complementario: `ui-ux-pro-max` **genera** el sistema, `impeccable` **audita** lo
construido. No compiten.

**Veredicto: evaluada, adoptada como gate posterior, no instalada esta semana.** Dos razones. La
primera es de calendario: una herramienta cuyo modo de operación es proponer cambios de estilo
sobre el código no entra la semana en que se congelan pantallas el viernes para fotografiarlas el
sábado. La segunda es de método: el propio proyecto tiene una regla de congelar el instrumental
durante la ventana de evaluación. Queda registrada como decisión con fecha para la semana del 24
de agosto, cuando A5 ya esté entregada y el prototipo pase a ser un activo y no un entregable.

### 8.4 Cuadro de decisión

| Herramienta | Rol | Cuándo | Estado |
|---|---|---|---|
| `ui-ux-pro-max` | Fuente generativa del sistema de diseño | Ya en uso desde A1 | **Se mantiene** |
| `taste-skill` | Checklist anti-defecto, 10 reglas, aplicadas al índice y a la revisión | Revisión del sábado 15 | **Adoptado parcialmente**, con dos rechazos razonados |
| `impeccable.style` | Auditoría automatizada y `DESIGN.md` | Semana del 24-ago | **Evaluado, diferido** |

---

## 9. Stack y despliegue: dos Cloud Run y una Cloud SQL

Infraestructura mínima serverless sobre créditos de GCP ya disponibles. Nada que no sirva para
desplegar la aplicación.

### 9.1 Proyecto y región

| Parámetro | Valor |
|---|---|
| Proyecto | `tareas-computo-nube` (número 403109840468) |
| Facturación | `014738-BE619E-7D4F64`, activa y verificada |
| Región | `us-central1` — la más económica y la que ya tiene configurada el cliente `gcloud` |
| Cuenta | `artzizumbo@gmail.com` |

Nota de registro: existe también un proyecto `karisma-data` sin facturación asociada. **No se
usa.** El despliegue va en `tareas-computo-nube`, como el usuario indicó.

### 9.2 Servicios habilitados

`run` · `sqladmin` · `artifactregistry` · `secretmanager` · `cloudbuild`. Ninguno más.

### 9.3 Los dos contenedores

**`karisma-api`** — FastAPI con Poetry, `Dockerfile` de dos etapas (construcción de dependencias y
tiempo de ejecución sobre `python:3.12-slim`), arranque con Uvicorn. Configuración estricta de
Pydantic Settings: **la aplicación no arranca sin `DATABASE_URL` ni `JWT_SECRET_KEY`.**

**`karisma-web`** — Nuxt 4 en modo SSR con pnpm sobre **Node 22 LTS** (no el 25 que está
instalado, que no es LTS), `Dockerfile` de dos etapas con `corepack` habilitado, salida de Nitro
en `.output`.

Ambos con `min-instances 0`, `max-instances 3` como tope de radio de explosión, 512 MiB, 1 vCPU y
concurrencia 80.

### 9.4 Por qué el navegador solo habla con el frontend

Las rutas `/api/**` se sirven desde el propio Nuxt mediante un proxy de Nitro que reenvía al
backend. Tres beneficios que se documentan:

1. **No hay CORS que configurar.** El navegador ve un solo origen.
2. **La cookie del JWT es `httpOnly` y del mismo sitio.** No hay token accesible desde JavaScript.
3. **El backend puede quedar cerrado a internet.** Se despliega con
   `--no-allow-unauthenticated` y se concede `roles/run.invoker` a la cuenta de servicio del
   frontend; el proxy firma cada llamada con un token de identidad obtenido del servidor de
   metadatos.

**Salida documentada** si el punto 3 cuesta más de 45 minutos el martes: backend público con JWT
obligatorio en todo endpoint de datos, y el cierre por IAM se registra como trabajo de A5. Se
declara la elección tomada, no se insinúa.

### 9.5 Cloud SQL mínima

| Parámetro | Valor | Por qué |
|---|---|---|
| Instancia | `karisma-pg` | |
| Motor | PostgreSQL 15 | El del plan |
| Nivel | `db-f1-micro` (núcleo compartido, edición Enterprise) | El más barato que existe: ~8 USD/mes |
| Disponibilidad | Zonal, sin alta disponibilidad | La alta disponibilidad duplica el cómputo |
| Almacenamiento | 10 GB HDD, **sin crecimiento automático** | HDD cuesta la mitad que SSD y el volumen real son kilobytes |
| Respaldos | Desactivados | No hay dato que perder: todo se regenera con semilla fija |
| Conexión | `--add-cloudsql-instances` desde Cloud Run, por Auth Proxy sobre socket Unix | **Evita el conector de acceso VPC serverless, que costaría más que la propia base** |

Las cuatro migraciones canónicas de dbmate, en este orden: `create_catalog` (con
`catalog_source`, `catalog_field`, `catalog_tribal_note` e índice tsvector) → `create_app_user`
(con los 7 usuarios sembrados y contraseñas **prehasheadas con Argon2**, nunca en texto plano) →
`create_export_job` → `enable_pgvector`. Se ejecutan desde local a través de `cloud-sql-proxy`
sobre `127.0.0.1:5432`, y `schema.sql` se versiona en el mismo commit.

### 9.6 Comandos de bootstrap y despliegue

```bash
# --- Bootstrap, una sola vez ---------------------------------------------
gcloud config set project tareas-computo-nube
gcloud config set run/region us-central1

gcloud services enable \
  run.googleapis.com sqladmin.googleapis.com artifactregistry.googleapis.com \
  secretmanager.googleapis.com cloudbuild.googleapis.com

gcloud artifacts repositories create karisma \
  --repository-format=docker --location=us-central1 \
  --description="Imagenes de Karisma Data"

gcloud sql instances create karisma-pg \
  --database-version=POSTGRES_15 --edition=enterprise --tier=db-f1-micro \
  --region=us-central1 --availability-type=zonal \
  --storage-type=HDD --storage-size=10GB --no-storage-auto-increase \
  --no-backup

gcloud sql databases create karisma --instance=karisma-pg
gcloud sql users create karisma_app --instance=karisma-pg --password="<generada>"

# --- Migraciones, desde local --------------------------------------------
cloud-sql-proxy tareas-computo-nube:us-central1:karisma-pg --port 5432 &
DATABASE_URL="postgres://karisma_app:<pass>@127.0.0.1:5432/karisma?sslmode=disable" dbmate up

# --- Despliegue -----------------------------------------------------------
gcloud run deploy karisma-api --source backend \
  --add-cloudsql-instances tareas-computo-nube:us-central1:karisma-pg \
  --set-secrets DATABASE_URL=karisma-db-url:latest,JWT_SECRET_KEY=karisma-jwt:latest \
  --min-instances 0 --max-instances 3 --memory 512Mi --cpu 1 --concurrency 80 \
  --no-allow-unauthenticated

gcloud run deploy karisma-web --source frontend \
  --set-env-vars API_BASE="$(gcloud run services describe karisma-api --format='value(status.url)')" \
  --min-instances 0 --max-instances 3 --memory 512Mi --cpu 1 --concurrency 80 \
  --allow-unauthenticated
```

### 9.7 FinOps

Presupuesto del proyecto: **menos de 45 USD/mes con alerta al 50 %**. Los créditos gratuitos lo
absorben, y las alertas se ponen igual porque un crédito que se agota sin aviso deja el prototipo
caído en mitad de la semana de la prueba SUS.

| Recurso | Configuración | USD/mes |
|---|---|---|
| Cloud Run `karisma-web` | min 0, max 3, 512 MiB | 0 – 2 |
| Cloud Run `karisma-api` | min 0, max 3, 512 MiB | 0 – 2 |
| Cloud SQL `karisma-pg` | db-f1-micro, zonal, 10 GB HDD, sin respaldos | ≈ 9 (≈ 8 cómputo + ≈ 0.90 disco) |
| Artifact Registry | 1 repositorio, política de limpieza a 3 etiquetas | 0 (menos de 0.5 GB es gratuito) |
| Secret Manager | 3 secretos | < 0.10 |
| Cloud Storage | 1 bucket de exportes, ciclo de vida de 7 días | < 0.05 |
| Gemini Flash-Lite | Solo si se activa el sábado, con tope de tokens | 0 – 5 |
| Semana de A5 | `min-instances 1` durante 5 días | + 2 – 3 puntual |
| **Total** | | **≈ 10 – 14 USD/mes** |

Alertas de facturación en tres umbrales: **22.50 (50 %), 36 (80 %) y 45 USD (100 %)**.

Cinco palancas que se aplican desde el primer despliegue: escalado a cero fuera de uso · tope de 3
instancias · política de limpieza en Artifact Registry para que las imágenes viejas no acumulen ·
ciclo de vida de 7 días en el bucket · y presupuesto de llamadas a herramientas del agente, con
tope de cinco por consulta, si Gemini se activa.

**Una nota honesta que va en el documento y que conviene no omitir:** apagar la instancia de Cloud
SQL ahorra poco, porque GCP cobra la dirección IP mientras la instancia está detenida. El ahorro
real es **borrar la instancia al cerrar A5**, y ese paso queda con fecha en la sección 17.

---

## 10. Datos: los silos mínimos creíbles

El objetivo no es el volumen, es la credibilidad. Una pantalla vacía no se puede evaluar y una
pantalla con datos inventados a mano se nota.

- **Semilla fija `20260720`** en Polars, Faker y numpy. `make data` reproduce byte a byte.
- **Volúmenes recortados** frente al plan original: lo suficiente para que las tablas paginen, los
  filtros filtren y el preagregado de 500 000 puntos tenga de dónde salir. No hay razón para
  generar cinco millones de filas que nadie va a mirar.
- **Esquemas deliberadamente crípticos y heterogéneos entre silos** (`cli_ref`, `id_cliente`,
  `ctpty_cd` para la misma entidad), porque ese es el problema que el portal resuelve y la
  pantalla debe mostrarlo.
- **~0.1 % de anomalías inyectadas**, documentadas en `data/README.md`, para que la pantalla de
  calidad de datos tenga algo real que reportar.
- **Catálogo de 200 a 400 entradas** con unas 30 notas de conocimiento tribal, que es lo que
  alimenta el panel de metadatos y la búsqueda.
- **Siete usuarios sembrados**: un administrador y dos por perfil, con contraseñas Argon2.

---

## 11. Pre-validación sintética sobre pantallas reales

El criterio que distingue esta actividad de una revisión de diseño convencional, y el segundo de
los dos elementos no negociables de la semana.

### 11.1 Qué es y cómo se nombra

Ocho **evaluadores prototipo** condicionados por las ocho personas de A1, bajo el protocolo
PerceptUI. Se nombran así, siempre, en todo el documento: no son usuarios, no son participantes y
no sustituyen a nadie. Se reporta como **pre-validación complementaria con sus sesgos
declarados**, nunca como sustituto de la prueba con personas reales de A5.

### 11.2 Qué la distingue esta vez

En A3 los evaluadores clasificaron tarjetas sin ver interfaz. **Aquí corren sobre capturas reales
del prototipo**, que es exactamente lo que `US-UX-07` exige y lo que en el plan del 29-jul se
identificó como el riesgo mayor: si el frontend no existía, la pre-validación caía sobre mockups y
perdía su valor. Existe.

### 11.3 Protocolo

Cinco tareas, una por pantalla principal, con las sesiones a ciegas entre sí. Por cada evaluador y
tarea se registra: **primera impresión antes de actuar · dónde daría el primer clic · qué esperaba
encontrar y qué encontró · si titubeó · qué le resultó confuso · qué haría distinto.** Los conteos
se reportan en absolutos sobre 8, porque con esa n un porcentaje exagera la fuerza de la
evidencia. La regla se hereda de A3 y se mantiene.

Dos tareas se heredan expresamente de la prueba de árbol de A3, para cerrar el ciclo:

- **Repetir la tarea 3** —consultar un indicador de riesgo— sobre la arquitectura revisada, para
  comprobar si el traslado de los tableros a Exploración eleva el acierto sobre el 1 de 8 que
  obtuvo la ubicación original.
- **Medir si el acceso cruzado a la bitácora reduce el titubeo** de la tarea 4, donde titubearon
  los ocho.

### 11.4 La iteración documentada

**Al menos una**, y se documenta como cadena completa: **hallazgo → cambio aplicado → versión**,
con captura del antes y del después lado a lado. Sin la captura del antes, la iteración no es
verificable y no cuenta.

### 11.5 Nota de método obligatoria

Se reproduce en el documento, con el mismo tono que en A3: los evaluadores prototipo producen
predicciones plausibles condicionadas por las personas, no comportamiento observado. Sirven para
descartar decisiones caras antes de la prueba con personas reales. No la sustituyen.

---

## 12. El documento: estructura y plan de figuras

### 12.1 Archivos LaTeX

Siguiendo la receta de `docs/entregables/README.md`, sección «Añadir una actividad nueva»:

```
docs/entregables/
├── main_a4.tex                          envoltorio de la Actividad 4
├── contenido/
│   ├── a4_00_preliminares.tex           introducción + trazabilidad rúbrica → sección
│   ├── a4_01_metodo_prototipado.tex     fidelidad, nota de herramienta, los 4 requisitos
│   ├── a4_02_prototipos.tex             las siete pantallas
│   ├── a4_03_guia_estilos.tex           las once secciones de la guía
│   ├── a4_04_prevalidacion.tex          protocolo, hallazgos, iteración documentada
│   ├── a4_05_alcance.tex                tabla de tres estados + roadmap declarado
│   ├── a4_06_cierre.tex                 conclusiones + referencias
│   └── a4_07_anexo.tex                  tokens completos, matriz de contraste, sesiones
```

Y en `main_completo.tex`, la portadilla `\uxparte{IV}{...}{...}` con sus `\input`, más la
actualización de la portada, el `pdftitle` y la sección «Sobre este documento».

Compilación: `latexmk -xelatex main_a4.tex` desde `docs/entregables/`, dos pasadas para el índice.
Copia final: `cp main_a4.pdf "../semana_4/Entregable Actividad 4_equipo_8.pdf"`.

### 12.2 Figuras

| # | Figura | Generador |
|---|---|---|
| 1 | Índice de los siete prototipos | Captura Playwright, viewport 1440 × 900 |
| 2-8 | Las siete pantallas, una por figura | Captura Playwright, guion reproducible |
| 9 | Cuatro estados de la tarjeta de tool call, en galería | Captura Playwright |
| 10 | Los cuatro estados transversales (vacío, cargando, error, sin permiso) | Captura Playwright |
| 11 | Lámina de paleta: 4 familias × 5 tonos con hex | `generar_tokens_a4.py` |
| 12 | Matriz de contraste WCAG | `generar_tokens_a4.py` |
| 13 | Espécimen tipográfico y escala | `generar_tokens_a4.py` |
| 14 | Matriz de botones 3 × 5 más destructivo y carga | Captura de la ruta `/guia` |
| 15 | Campos, chips y badges | Captura de la ruta `/guia` |
| 16 | Lámina de iconografía | Captura de la ruta `/guia` |
| 17 | Retícula y escala de espaciado | `generar_tokens_a4.py` |
| 18 | Rutas del prototipo contra ramas del mapa de A3 | matplotlib |
| 19 | Antes y después de la iteración de pre-validación | Composición con PIL |

> **Palanca de excelencia.** Existe una ruta `/guia` en la propia aplicación que renderiza el
> sistema de diseño vivo. Las láminas de la guía de estilos no se dibujan: se capturan de ahí. Es
> imposible que el documento describa un botón que la aplicación no tiene.

Reglas heredadas que se respetan: `pdf.fonttype = 42` en toda figura de matplotlib · nada de
modelos de imagen para diagramas con texto en español · capturas a resolución fija y con guion,
no recortes a mano.

---

## 13. Todo lo que hay que hacer, día por día

Plan para **una sola persona**, de 9 a 12 horas diarias. El lunes arranca a media tarde, así que
cuenta como día corto. La modalidad de la actividad sigue siendo colaborativa y la portada lleva a
los tres integrantes; lo que este calendario planifica es la ejecución.

### 13.A · Lunes 10 — Fundamentos (~7 h)

- [ ] Absorción de la rúbrica y registro de la fila de §25.4 en el plan del proyecto.
- [ ] Andamiaje del monorepo: `Makefile`, `docker-compose.yml`, `backend/pyproject.toml` con
      Poetry, `frontend/package.json` con pnpm y Node 22 LTS fijado por `packageManager`.
- [ ] `generar_tokens_a4.py`: lee la paleta de `uxdoc.sty`, emite el bloque `@theme` de Tailwind
      v4, la matriz de contraste y las láminas.
- [ ] Nuxt 4 con estructura `app/` (nunca la de Nuxt 3), Tailwind v4, layout con barra lateral de
      dos niveles y las **ocho rutas navegables vacías** más el índice de siete botones.
- [ ] Primer commit en rama `feature/UX-US-UX-07-alta-fidelidad`.

**Cierra:** US-001 y US-002 parciales.

### 13.B · Martes 11 — Nube y datos (~11 h)

**Mañana, bloque de infraestructura — tope duro de 3 horas.**

- [ ] Bootstrap de GCP: APIs, Artifact Registry, Cloud SQL, Secret Manager.
- [ ] **Despliegue de los dos servicios con un «hola mundo».** La dirección pública tiene que
      estar viva el día 2. Es la mitigación con fecha del riesgo R14 y lo que permite reclutar
      participantes de A5 desde esta semana.
- [ ] Las cuatro migraciones dbmate aplicadas y `schema.sql` versionado.

**Tarde.**

- [ ] `ml/data/generators.py` con semilla fija y los tres silos.
- [ ] Sembrado de catálogo (200-400 entradas, ~30 notas tribales) y de los 7 usuarios.
- [ ] Backend: autenticación JWT con Argon2, `/api/catalog/search` por palabra clave,
      endpoints semánticos mínimos sobre Polars.
- [ ] Proxy de Nitro y cookie `httpOnly` funcionando de extremo a extremo.

**Cierra:** US-003 (puente `gcloud run deploy`), US-002, US-006 recortada, US-015, US-016.

### 13.C · Miércoles 12 — Las dos pantallas más pesadas (~11 h)

- [ ] Pantalla 0, Acceso, con el selector de perfil de demostración.
- [ ] Pantalla 1, Inicio, en sus tres composiciones por rol.
- [ ] Pantalla 2, Exploración y extracción: catálogo facetado, panel de metadatos, y la rama 2.4
      con ECharts a 500 000 puntos y drill-down de tres niveles.
- [ ] Ruta `/guia` con el sistema de diseño vivo.

**Cierra:** US-017, US-025 degradada, US-026, US-027.

### 13.D · Jueves 13 — Gobierno, administración y exportación (~11 h)

- [ ] Pantalla 3, Gobierno del dato, con el overlay de linaje.
- [ ] Pantalla 5, Administración, con la degradación acordada y la separación de acciones
      destructivas.
- [ ] Pantalla 6, Exportación, con el flujo de tres momentos.
- [ ] Los cuatro estados transversales en las cinco pantallas ya construidas.

**Cierra:** US-019 degradada, US-029 overlay, US-009 fachada.

### 13.E · Viernes 14 — El diferenciador, y congelamiento (~11 h)

- [ ] Pantalla 4, Asistente: `/api/chat` con SSE real, los cuatro eventos tipados, las cuatro
      tarjetas de tool call y el botón Detener que cancela el generador de verdad.
- [ ] **12:00 — decisión sobre el alcance de la prueba SUS de A5**, que el plan fija como gate.
- [ ] Barrido de accesibilidad: foco, orden de tabulación, `aria-label`, contraste.
- [ ] **20:00 — congelamiento.** Ninguna pantalla se toca después de esta hora salvo por la
      iteración del sábado.
- [ ] Capturas de las siete pantallas y de las láminas con el guion de Playwright.

**Cierra:** US-023, US-024 (evento de error tipado), US-028.

### 13.F · Sábado 15 — Pre-validación y redacción (~12 h)

- [ ] **12:00 — go/no-go de Gemini real.** Si es no, se declara y se sigue.
- [ ] Pre-validación con los ocho evaluadores prototipo sobre las capturas reales.
- [ ] Al menos una iteración documentada: hallazgo, cambio, versión, con antes y después.
- [ ] Recaptura de las pantallas afectadas por la iteración.
- [ ] Redacción de `a4_00`, `a4_01`, `a4_02` y `a4_03` completos.

### 13.G · Domingo 16 — Cierre (~10 h)

- [ ] `a4_04`, `a4_05`, `a4_06` y el anexo.
- [ ] Referencias en APA 7 verificadas una por una.
- [ ] Compilación con `latexmk -xelatex`, dos pasadas, revisión de índice, de figuras cortadas y
      de titulares colgados al pie.
- [ ] Checklist de la sección 16, rubro por rubro.
- [ ] Revisión cruzada con Alexandro y Jacqueline.
- [ ] **20:00 — entrega en Canvas** como `Entregable Actividad 4_equipo_8.pdf`.

### 13.H · Válvulas y regla de corte

Se aplican **en este orden**, y solo cuando el reloj obligue:

1. Los cuatro estados de la tarjeta de tool call se muestran como galería en lugar de secuencia
   animada.
2. El drill-down del tablero baja de tres niveles a dos.
3. Administración se entrega en un solo nivel.
4. La pantalla 6, Exportación, sale del set y quedan seis prototipos.

**No negociables, porque son los dos criterios que ninguna otra evidencia sustituye:** las cinco
interfaces de la arquitectura navegables, y la iteración documentada de pre-validación. A eso se
suma, por peso de rúbrica, la guía de estilos completa con sus siete secciones puntuadas.

---

## 14. Las historias de usuario: qué se cierra y qué es roadmap

Cuatro estados, y la tabla completa alimenta directamente la tabla de alcance del PDF.

| US | Título | Estado al cierre de la semana |
|---|---|---|
| **US-UX-07** | Interfaces de alta fidelidad (A4) | **Cerrada** |
| US-001 | Entorno Docker Compose y monorepo | **Cerrada** |
| US-002 | Dependencias reproducibles y esqueleto dbmate | **Cerrada** |
| US-003 | Infraestructura GCP | **Cerrada degradada** — puente `gcloud run deploy`; Terraform sigue congelado |
| US-006 | Silos sintéticos | **Cerrada degradada** — volúmenes recortados, semilla fija intacta |
| US-008 | Catálogo semántico | **Cerrada degradada** — versión por palabra clave; la búsqueda híbrida sigue diferida |
| US-009 | Exportaciones en segundo plano | **Demostrada en prototipo** — flujo completo, sin lifecycle ni auditoría de duración |
| US-015 | Autenticación JWT | **Cerrada** |
| US-016 | Autorización RBAC por scopes | **Cerrada** |
| US-017 | Guarda de sesión y ocultamiento por rol | **Cerrada** |
| US-018 / US-019 | CRUD y panel de usuarios | **Cerrada degradada** — listar, cambiar rol, desactivar |
| US-023 | Streaming SSE y cancelación real | **Demostrada en prototipo** — transporte y cancelación reales, contenido guionizado |
| US-024 | Errores en el stream | **Cerrada degradada** — evento `error` tipado |
| US-025 | Dashboard de alto rendimiento | **Cerrada degradada** — 500 000 puntos preagregados |
| US-026 | Revelación progresiva y tarjetas predictivas | **Cerrada** — 3 tarjetas, proyección estática etiquetada |
| US-027 | Workspaces por rol | **Cerrada** |
| US-028 | Tarjetas de visibilidad de tool call | **Cerrada** |
| US-029 | Overlay de linaje y estado compartido | **Cerrada degradada** — overlay completo, estado compartido con payload estático |
| US-020 / US-021 | Agente ADK y suite de tools | **Roadmap declarado** — salvo que el go/no-go del sábado salga verde |
| US-011 | Endpoints con capa semántica completa | **Roadmap declarado** — la versión mínima que alimenta las pantallas sí está |
| US-012, US-013, US-014, US-022, US-035, US-036 | | **Congeladas**, como ya estaban |
| US-030 a US-034 | Observabilidad, pruebas y producción | **Semana de A5** |
| US-037 a US-041 | Consultas guardadas, avisos, comparación, credenciales autogestionadas, bitácora descargable | **Roadmap declarado en la tabla de alcance** |

Además, las seis capacidades que A2 prometió y el catálogo técnico no cubre se declaran una por
una en la tabla de alcance con estado *roadmap*. Ninguna se omite.

---

## 15. Referencias en APA 7

Sobre las 20 entradas que A3 ya trae, estas son las nuevas de A4, con el sitio del cuerpo donde se
cita cada una:

| Entrada | Dónde se cita |
|---|---|
| Ramírez Mejía, A. I. (2023). *Grocery shopping app. A guided UX case study. Part 4: Prototyping and Style Guide* [Diapositivas]. TC4032, ITESM. | Sección de método (anatomía de la guía de estilos) |
| Hartson, R., y Pyla, P. (2019). *The UX book: Agile UX design for a quality user experience* (2.ª ed.), cap. 11 Prototyping. Morgan Kaufmann. | Método: fidelidad alta contra baja |
| Allen, J., y Chudley, J. (2012). *Smashing UX design*, cap. 5 Patterns, properties and principles of good UX design. Wiley. | Guía de estilos: principios de patrón y consistencia |
| Bai, J., Zhang, Z., Zhang, J., y Zhu, Z. (2026). *Insight Agents: An LLM-based multi-agent system for data insights*. arXiv:2601.20048 | Pantalla 4, asistente conversacional |
| Jang, J., y Li, W.-S. (2026). *TwinBI: An agentic digital twin for efficient augmented interactions with business intelligence dashboards*. arXiv:2606.13731 | Pantalla 2, estado compartido tablero↔chat |
| Naik, S., Passi, S., Vorvoreanu, M., Saponas, S., y Hall, A. (2026). *"So there's a catch-22 here": How early adopters who build multi-agent LLM systems conceptualize transparency*. arXiv:2606.08323 | Tarjetas de tool call y overlay de linaje |
| Bougie, N., Ye, X., Marconi, G. M., y Watanabe, N. (2026). *PerceptUI: LLM agents as human-aligned synthetic users for UI/UX evaluation*. arXiv:2606.05697 | Pre-validación sintética (ya citada en A3) |
| Peng, Y.-H., Das, S., Bigham, J. P., y Wu, J. (2026). *Efficient personalization of generative user interfaces*. arXiv:2604.09876 | Pantalla 1, defaults por rol y el dato de kappa 0.25 |
| Bachkaniwala, R., Luo, C., So, R., Mahajan, D., y Rong, K. (2026). *Stream2LLM: Overlap context streaming and prefill for reduced time-to-first-token*. arXiv:2604.16395 | Percepción de velocidad en el streaming |
| W3C. (2023). *Web Content Accessibility Guidelines (WCAG) 2.2*. | Directrices de accesibilidad |
| Morville, P., y Rosenfeld, L. (2006). *Information architecture for the World Wide Web* (3.ª ed.). O'Reilly. | Contrato de navegación heredado de A3 |

Dos reglas de APA 7 que aquí importan y que ya costaron una corrección en A3: la sangría es
francesa y va en el entorno `uxreferencias`, no a mano; y las fuentes en línea llevan fecha de
consulta cuando el contenido puede cambiar.

---

## 16. Checklist final antes de subir

Formato idéntico al de la sección §24 del plan, que dio 15/15 en A1.

| ✔ | Rubro (peso) | Qué exige la banda «Completo» | Extra de excelencia |
|---|---|---|---|
| ☐ | **Portada (2 %)** | Nombres de los tres integrantes, datos del curso y equipo 8 | Marca Karisma Data y logotipo institucional, coherentes con A1-A3 |
| ☐ | **Introducción (3 %)** | Qué se hizo y cómo se organiza el documento | Nota de herramienta que justifica la sustitución de Figma; tabla de trazabilidad rúbrica → sección con su peso |
| ☐ | **Prototipos (50 %)** | Al menos cinco prototipos de alta fidelidad basados en los hallazgos de A3 | **Siete**, todos capturados de la aplicación en funcionamiento; dirección pública incluida; cuatro estados transversales por pantalla; tabla ruta ↔ rama del mapa de A3 |
| ☐ | Identidad de la marca (9 pts) | Logotipo, paleta, tipografía, directrices | Área de resguardo, tamaño mínimo, versiones y usos incorrectos ilustrados |
| ☐ | Tipografía (9 pts) | Tipos, tamaños, interlineado, reglas | Espécimen por peso, escala de nueve roles, regla de cifras tabulares, tensión 14/16 px resuelta y justificada |
| ☐ | Paleta de colores (9 pts) | Primarios, secundarios, casos de uso, texto y fondo | Cuatro familias × cinco tonos, neutros, semánticos, **matriz de contraste verificada por script**, paleta categórica de series con forma y patrón |
| ☐ | Componentes de la interface (9 pts) | Botones, formularios, iconos, menús, patrones de interacción | Matriz de botones de 15 celdas, campos en seis estados, tarjeta de tool call en cuatro, tablas con `aria-sort` |
| ☐ | Iconografía (9 pts) | Lámina de iconos | Familia única declarada, tokens de tamaño, grosor, alineación, área táctil, inventario por función |
| ☐ | Conclusiones generales (9 pts) | Cierre del reporte | Escritas en pasado y con cifras; qué cambió por evidencia y no por gusto |
| ☐ | Referencias (9 pts) | Bibliografía | APA 7 con sangría francesa; se cita el recurso que la propia rúbrica nombra |
| ☐ | **Secciones no puntuadas que suman** | — | Imágenes, retícula, microinteracciones, accesibilidad, voz y tono, versionado de la guía |
| ☐ | **Tabla de alcance** | — | Tres estados por pantalla y roadmap declarado sin omisiones |
| ☐ | **Pre-validación** | — | Ocho evaluadores sobre capturas reales, con al menos una iteración documentada con antes y después |
| ☐ | **Formato** | PDF, nombre `Entregable Actividad 4_equipo_8`, subido por Canvas | Paginación y estilos consistentes con A1-A3; índice completo; sin titulares colgados al pie |

Verificaciones mecánicas de última hora:

- [ ] Ninguna frase del documento en tiempo futuro.
- [ ] Ninguna captura que muestre datos que se puedan confundir con reales.
- [ ] La franja de aviso de alcance visible en todas las capturas.
- [ ] Cada rama del mapa de A3 tiene ruta, y cada ruta tiene rama.
- [ ] Los diez puntos del checklist anti-defecto de la sección 8.2, verificados sobre el índice.
- [ ] La aplicación desplegada responde, y la dirección impresa en el PDF funciona.
- [ ] Sin emojis en ninguna parte: ni en la interfaz, ni en el documento, ni en los commits.

---

## 17. Lo que se arrastra a la Actividad 5

- **Despliegue con `min-instances 1`** durante los días de prueba, del 17 al 21 de agosto.
- **Reclutamiento de al menos cinco participantes**, que arranca esta semana y no el lunes 17: la
  dirección viva desde el martes existe precisamente para eso.
- **Las dos verificaciones que A3 dejó abiertas**: repetir la tarea 3 sobre la arquitectura
  revisada y medir si el acceso cruzado a la bitácora reduce el titubeo de la tarea 4.
- **Prueba SUS con meta de 75 o más**, con registro de tasa de éxito y de ruta elegida en las
  mismas cinco tareas, para comparar contra las 28 coincidencias de 40 de la corrida de A3.
- **Medición de TTFT p50 y p90** sobre al menos 50 corridas, y las cifras de tokens y costo.
- **`docs/security.md`** con la matriz de permisos, que sigue sin escribirse desde que su gate
  venció el 6 de agosto.
- **`impeccable.style`** como gate de auditoría, semana del 24 de agosto.
- **Borrar la instancia de Cloud SQL** al cerrar A5, que es el único ahorro real que queda por
  hacer en la nube.

---

*Documento de planeación interna. Equipo 8 · Karisma Data · TC4032 · MNA ITESM.
Escrito el lunes 10 de agosto de 2026, después de leer la rúbrica publicada en Canvas.*
