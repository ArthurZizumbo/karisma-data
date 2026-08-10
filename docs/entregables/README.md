# Entregables del curso — fuente única

Documentos del **Equipo 8** para TC4032 Experiencia del usuario y diseño de interfaces (MNA, ITESM).
Producto: **Karisma Data**, portal centralizado de datos financieros.

Una sola fuente de contenido, tres salidas. El texto de cada actividad vive una única vez en
`contenido/` y se compone tanto en la entrega semanal como en el documento acumulado del
proyecto; no hay dos versiones del mismo párrafo.

## Salidas

| Archivo | Qué produce | Para qué |
|---------|-------------|----------|
| `main_a1.tex` | 48 páginas | Actividad 1, entregada el 26-jul-2026 |
| `main_a2.tex` | 41 páginas | Actividad 2, entregada el 2-ago-2026 |
| `main_a3.tex` | 57 páginas | Actividad 3, se entrega el 9-ago-2026 |
| `main_completo.tex` | 147 páginas | Documento acumulado del proyecto: Parte I (A1), Parte II (A2) y Parte III (A3), con numeración continua |

El PDF que se sube a Canvas se copia con el nombre exacto que exige la actividad:

```bash
cp main_a2.pdf "../semana_2/Entregable Actividad 2_equipo_8.pdf"
```

## Compilar

Requiere **XeLaTeX** (usa `fontspec`). Dos pasadas para llenar el índice:

```bash
latexmk -xelatex main_a2.tex        # o main_a1.tex / main_completo.tex
```

o bien:

```bash
xelatex main_a2.tex && xelatex main_a2.tex
```

Las figuras de cada actividad se regeneran con su propio script:

```bash
cd figuras
python generar_figuras.py .        # figuras 1 a 4 de la Actividad 1
python generar_figuras_a2.py .     # curva emocional y recorridos entrelazados (seaborn)
python journey_html/render.py      # los cuatro journey maps (HTML + CSS Grid)
```

### Cada herramienta en lo suyo

| Artefacto | Herramienta | Por qué |
|-----------|-------------|---------|
| Los cuatro journey maps | HTML + CSS Grid, impreso a PDF con Edge headless | Un mapa es una retícula de etapas por carriles: un problema de maquetación, no de graficación. CSS Grid lo resuelve solo y da tipografía, cajas y color de calidad de producto |
| Curva emocional y recorridos entrelazados | seaborn / matplotlib | Sí son gráficas de datos, con ejes y series |
| Fotografías y marca | MCP de NanoBanana | Imágenes sin una sola letra |

**Los cuatro mapas comparten una única fuente de contenido**, `figuras/journey_data.py`.
Los dos renderizadores la importan, así que corregir una celda es editar un diccionario y
volver a ejecutar. `generar_figuras_a2.py` conserva una función `journey_map` de respaldo en
matplotlib que ya no se invoca.

El diseño sigue el estilo **Data-Dense Dashboard** que la skill `ui-ux-pro-max` recomienda para
producto de gobierno de datos empresarial: retícula, padding mínimo (11 px), tipografía densa
pero legible (12.5 px) y máxima visibilidad de información. Los marcadores de la curva combinan
color, forma (triángulo arriba, cuadrado, triángulo abajo) y valor numérico, de modo que la
información no dependa del color — regla `color-not-only` de esa misma guía.

### Figuras de la Actividad 1

Las cuatro se generan con seaborn sobre la misma paleta. Las dos que son gráficas de datos usan
seaborn de forma nativa; las dos que son diagramas se construyen con primitivas de matplotlib
bajo el tema de seaborn, porque no son series de datos.

| Figura | Tipo | Construcción |
|--------|------|--------------|
| 1. Mapa de la audiencia | Dispersión | `sns.scatterplot` con `hue` por relación con el dato |
| 2. Impacto por perfil | Mapa de calor | `sns.heatmap` con anotación categórica Alto/Medio/Bajo |
| 3. Flujo actual y propuesto | Diagrama | Primitivas de matplotlib con tema seaborn |
| 4. Concepto de la vista de búsqueda | Wireframe | Primitivas de matplotlib con tema seaborn |

Las etiquetas están en español y la tipografía de las figuras es Fira Sans, la misma del cuerpo
del documento.

### Cómo previsualizar un mapa antes de imprimirlo

```bash
python journey_html/render.py                       # deja los HTML en journey_html/build/
cd journey_html/build && python -m http.server 8899 # y abrir http://127.0.0.1:8899/
```

Los HTML son autocontenidos: las fuentes van embebidas en base64 (las mismas Lexend Deca y
Fira Sans que usa el documento LaTeX, tomadas de la instalación local de MiKTeX), de modo que
el PDF no depende de la red y la familia tipográfica coincide con el resto del entregable.

Las ilustraciones de contexto de cada escenario (`imagenes/escena_*.png`) se generaron con el
MCP de NanoBanana. Regla que ya costó descubrir en la Actividad 1: **los modelos de imagen se
usan solo para fotografía y marca, nunca para diagramas con texto en español**. Por eso los
journey maps, que son casi todo texto, se generan con matplotlib y las escenas, que no llevan
una sola letra, con el modelo. Los prompts piden explícitamente pantallas fuera de foco y
llevan lista negativa de texto, letras, números y logotipos.

### Nitidez de las figuras

Todo se inserta en **PDF vectorial**, no en PNG: a esta densidad de texto, un mapa rasterizado
se ve pixelado en cuanto el lector amplía.

Trampas resueltas, para no volver a descubrirlas:

- **Journey maps.** El tamaño de `@page` debe caber el contenido completo: si se queda corto,
  Edge recorta el último carril sin avisar. Se mide con el navegador
  (`document.body.scrollHeight`) antes de fijarlo, no a ojo.
- **CSS Grid y `display: contents`.** Cada celda lleva `grid-row` y `grid-column` explícitos. Con
  auto-placement, el recuadro del momento de la verdad se coloca como una celda más y desplaza
  toda la retícula una columna.
- **Colisión de nombres de clase.** `.marca` servía para la marca del encabezado y para el
  marcador de la curva: el `<span>` del nombre heredaba `position: absolute; width: 15px` y
  aparecía flotando en mitad de la página.
- **Gráficas de matplotlib.** `pdf.fonttype = 42` es obligatorio; sin eso salen subsets Type 3 y
  algunos visores renderizan mal glifos sueltos (la `J` de Fira Sans aparecía como coma).
- **Ancho de la página horizontal en LaTeX.** Se calcula sobre `\paperheight`, no sobre
  `\linewidth`: al abrir `landscape`, `\linewidth` todavía no refleja la caja intercambiada.

## Estructura

```
entregables/
├── main_a1.tex            envoltorio de la Actividad 1
├── main_a2.tex            envoltorio de la Actividad 2
├── main_completo.tex      documento acumulado del proyecto
├── contenido/
│   ├── a1_cuerpo.tex      secciones 1 a 15 de la Actividad 1
│   ├── a1_anexo.tex       consentimiento informado
│   ├── a2_00_preliminares.tex   introducción
│   ├── a2_01_metodo.tex         método, plantilla de escenario y alcance declarado
│   ├── a2_02_escenarios.tex     seis escenarios, dos por integrante
│   ├── a2_03_journey.tex        journey map de equipo
│   ├── a2_04_cierre.tex         trazabilidad, principios rectores y referencias
│   └── a2_05_anexo.tex          journey map en formato de tabla (fuera de las salidas
│                                 desde la revisión de contenido del 29-jul; ningún
│                                 `main_*.tex` lo incluye)
├── estilo/uxdoc.sty       sistema de diseño (tipografía, color, componentes)
├── figuras/               figuras y sus scripts generadores
└── imagenes/              logotipos, marca y las ocho fotografías de personas
```

`docs/documento_proyecto/` conserva intacta la versión de la Actividad 1 tal como se entregó.
Esta carpeta es la que evoluciona; aquella no se toca.

## Añadir una actividad nueva

1. Escribir el contenido en `contenido/aN_*.tex`, sin preámbulo ni `\begin{document}`.
2. Crear `main_aN.tex` copiando el envoltorio de la actividad anterior y cambiando portada,
   encabezado y `\input`.
3. Añadir en `main_completo.tex` una portadilla `\uxparte{N}{...}{...}` y los `\input`
   correspondientes, y actualizar la portada, el `pdftitle` y la sección
   «Sobre este documento».

## Sistema de diseño

Derivado del design system generado con la skill `ui-ux-pro-max` para la consulta
*"enterprise data governance platform, professional, trustworthy"*.

| Rol | Valor | Nota |
|-----|-------|------|
| Titulares | Lexend Deca | Se distribuye solo en peso Regular: la jerarquía es tamaño + color + filete, nunca negrita |
| Cuerpo | Fira Sans | Sustituto disponible de Source Sans 3 |
| Primario | `#1F4D78` | Estructura, titulares, cabeceras de tabla |
| Interactivo | `#2563EB` | Enlaces, subtítulos, acentos |
| Secundario | `#3B82F6` | Cuadrantes, rellenos |
| Acento | `#F97316` | Filete bajo titulares, marca y momento de la verdad |
| Superficie | `#F8FAFC` | Fondos de caja |
| Texto | `#1E293B` | Cuerpo |

### Componentes de `uxdoc.sty`

| Componente | Uso | Desde |
|------------|-----|-------|
| `\uxportada{actividad}{título}{fecha}` | Portada con logotipo institucional y marca | v2.0 parametrizada |
| `\uxencabezado{texto}` | Rótulo del encabezado de página | v2.0 |
| `\uxparte{numeral}{título}{descripción}` | Portadilla de parte del documento acumulado | v2.0 |
| `\uxsection{}` | Titular sin numeración con la presencia de `\section` | v1.0 |
| `uxtabla{cols}{título}` | Tabla con cabecera navy y cebra suave | v1.0 |
| `uxlist` + `\lead{}{}` | Viñeta con entradilla | v1.0 |
| `uxpreg` | Lista numerada para instrumentos y pasos de escenario | v1.0 |
| `uxnota[título]`, `uxdestacado` | Cajas de nota y de cita | v1.0 |
| `uxreferencias` | Lista de referencias con sangría francesa | v2.0 |
| `\personahead{}{}{}`, `personadatos`, `\personabloque{}` | Fichas de persona | v1.0 |
| `\mapaempatia{nombre}{says}{thinks}{does}{feels}` | Mapa de empatía: **imprime él mismo su titular**, no lleva `\subsection` delante | v2.1 |
| `\aportacion[qué]{nombre}{matrícula}` | Banda de atribución individual | v2.0 con argumento opcional |
| `\escenariohead{foto}{título}{persona}{datos}` | Cabecera de escenario | v2.0 |
| `\elemento{rótulo}{glosa}` | Rótulo de los cuatro elementos exigidos por la rúbrica | v2.0 |
| `uxmomento` | Caja del momento de la verdad | v2.0 |
| `\figuraux{}{}{}` | Figura a ancho de columna | v1.0 |
| `\figurapanoramica{}{}{}` | Figura a sangre en página horizontal | v2.0 |

### Tipos de columna

- `L{ancho}` fija a la izquierda · `C{ancho}` fija centrada
- `Y` elástica · `Z{factor}` elástica ponderada

Los factores `Z` de una misma tabla **deben sumar el número de columnas elásticas**. Si no,
`tabularx` desborda el ancho de página. Es el error más frecuente al añadir tablas.

## Trampas conocidas

- **Lexend solo tiene peso Regular.** Aplicarle `\bfseries` produce negrita simulada con trazo
  hueco. La jerarquía se construye con tamaño, color y filete.
- **`tabularx` no puede partirse** entre las dos mitades de `\newenvironment`: el cuerpo se
  captura con `\NewEnviron` de `environ`.
- **`\parskip` se filtra dentro de las celdas `p`** y descuadra las tablas: va a 0 dentro de
  cada entorno de tabla.
- **En `landscape` la caja de texto ya viene intercambiada**, así que `\linewidth` es el lado
  largo; `\figurapanoramica` desborda 2.4 cm centrados para aprovechar el margen.
- **Las figuras a página completa no deben ser flotantes**: `figure[p]` dentro de `landscape`
  se desplaza al final del documento y deja la página del título vacía.
- **Los modelos de imagen no sirven para diagramas con texto en español.** Las figuras con
  etiquetas se generan con matplotlib; los modelos de imagen se reservan para fotografías y
  marcas sin texto.
- **Un `tcbraster` se parte entre sus filas.** Fue la observación del profesor sobre la
  Actividad 1: tres de los ocho mapas de empatía quedaron divididos en dos páginas. Un bloque
  visual que debe leerse de una sola vez se compone primero en una caja (`\sbox`), se mide su
  altura y se reserva con `\needspace` antes de imprimir el titular; colocado desde la caja ya
  no ofrece punto de corte. `\mapaempatia` es el ejemplo a copiar.
- **Los flotantes de fábrica dejan páginas a medias.** `\textfraction=0.2` exige una quinta
  parte de texto en cualquier página con flotante, así que una tabla grande se expulsa a página
  propia y la anterior queda corta. Los parámetros están aflojados en `uxdoc.sty`.
- **Viudas y huérfanas.** LaTeX las castiga con solo 150 y las admite sin más. En este
  documento `\widowpenalty` y `\clubpenalty` están en 10000: antes que un renglón suelto, la
  página termina antes.
- **El índice hereda el `\parskip` del documento** (6 pt por entrada) y a ese ritmo las
  últimas entradas caen en una página propia casi vacía. Dentro del índice el `\parskip` baja
  a 1 pt y el colchón previo de cada sección (`\l@section`) de 1 em a 0.7 em: el de A2 cabe
  así en una sola página.
- **Solo abren página nueva los bloques con identidad propia**: bandas de aportación
  individual, personas, escenarios, journey maps y anexos. Las secciones de texto corrido
  fluyen una tras otra; encadenar `\clearpage` en todas dejaba un final de sección medio
  vacío por cada una.
- **Un titular nunca queda solo al pie**: titlesec ejecuta `\sectionbreak` /
  `\subsectionbreak` antes de cada titular y ahí se exige sitio con `\needspace` para el
  titular más las primeras líneas de su contenido. Sin esto, al fluir las secciones el
  titular de la sección 2 quedaba colgado al final de una página y la 2.4 separada de su
  figura.
- **Una sección que derrama uno o dos renglones a una página propia** no se arregla con
  espaciado global: se le permite crecer con `\enlargethispage{2\baselineskip}` justo antes
  del párrafo final.

## Marca

**Karisma Data** · Portal Centralizado de Datos Financieros. El símbolo
(`imagenes/logo_karisma_marca.png`) representa fuentes dispersas que convergen en un único dato
con autoridad. El logotipo compuesto se arma en LaTeX —símbolo más nombre en Lexend— para que
el texto sea vectorial.
