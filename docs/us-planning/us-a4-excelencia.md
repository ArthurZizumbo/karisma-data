# Planeación US-A4-EXCELENCIA — Los dos temas completos y la Actividad 4 en banda alta

**Estado**: planning
**Epic**: UX (con trabajo en E0, sistema de diseño, y E2, pantallas del contrato)
**Actividad**: A4 (dom 16-ago-2026) — apartado 3, prototipos, 50 % = 12.50 de 25; apartado 4, guía de estilos, 45 % = 11.25
**Sprint**: S4, cierre
**Rama**: continúa en `us-entrega-a4`, sobre su árbol de trabajo **sin commitear** (61 archivos). Sin PR (discrepancia RU-11 declarada)
**SHA base**: `aeafc6e`. Ancla del diff acumulado: `git diff --name-only aeafc6e`. **QA no usa `HEAD~N`**
**Estimación**: 21 SP en cinco olas
**Fuente normativa**: los tres exportes de `docs/entregables/figma/` · el handoff de US-ENTREGA-A4 · las dos evaluaciones de Impeccable del 15-ago · `PRODUCT.md` y `DESIGN.md`

> **Por qué existe esta US.** US-ENTREGA-A4 entregó un tema llamado institucional que no lo era. La
> revisión del usuario fue directa: *«nada que ver con lo de Figma»*, *«no cambia nada con respecto
> al que ya traíamos»*, *«el logo que traíamos pusiste uno que nada que ver»*. Las tres son ciertas y
> están verificadas contra el archivo. Esta planeación cierra esa brecha y, de paso, absorbe los
> hallazgos de las dos evaluaciones de diseño, que encontraron defectos que ninguna prueba unitaria
> podía ver.
>
> **Lo que salga de aquí es lo que se entrega.** El PDF de la ola E es el archivo que sube a Canvas.

---

## Lectura previa ejecutada

| Paso | Resultado |
|---|---|
| `docs/entregables/figma/*.pdf`, **los tres, abiertos como imagen** | Es la lectura que US-ENTREGA-A4 **no hizo**: trabajó desde la tabla §2.3 de su plan, que era una transcripción parcial. De ahí sale todo lo que falta |
| `docs/us-handoff/us-entrega-a4.md` | Leído completo, incluidos los dos registros de implementación y la fase de QA |
| Impeccable, Assessment A (revisión de diseño) | 10 heurísticas puntuadas, promedio **2.4 / 4**. Cinco problemas prioritarios y cinco banderas rojas por persona |
| Impeccable, Assessment B (detector y navegador) | Detector estático **limpio**; 0 fallos WCAG AA en las 8 combinaciones medidas, mínimo real 4.54:1; **un defecto duro de desplazamiento horizontal** |
| `ui-ux-pro-max`, dominios `ux`, `product`, `color` | Su recomendación para «Financial Dashboard» es dark OLED con alertas rojo/verde. **Se rechaza**, ver ambigüedad 7 |
| `docs/orchestration/checklist-ui.md` | Leído. Sus 10 reglas se aplican en §6.4 |
| `frontend/AGENTS.md`, `docs/AGENTS.md` | Leídos, ya corregidos por la US anterior |

---

## Confirmación del 'Estado' contra el repositorio

Verificado con `grep` y `ls`, no supuesto.

| Comprobación | Resultado |
|---|---|
| `git rev-parse --short HEAD` | `aeafc6e`; **61 archivos sin commitear** de la US anterior |
| `ls frontend/test/*.spec.ts \| wc -l` | **48** |
| `ls -d frontend/app/components/*/ \| wc -l` | **14** familias |
| `ls frontend/app/composables/*.ts \| wc -l` | **18** |
| `grep -rln '<table' frontend/app --include=*.vue` | **7** componentes con tabla escrita a mano |
| `grep -n tanstack frontend/package.json` | **No instalado** |
| `grep -n echarts frontend/package.json` | `echarts@^6.1.0` y `vue-echarts@^8.1.0`, **sí instalados**, usados en 3 archivos |
| Rutas del contrato | **10**: `/`, `/acceso`, `/inicio`, `/exploracion`, `/exploracion/tableros`, `/exploracion/exportar`, `/gobierno`, `/asistente`, `/administracion`, `/guia` |
| Tokens de color hoy | **21**, tras abrir la ranura de acción el 15-ago |

---

## Ambigüedades del encargo, resueltas antes de planear

**1. El chasis es uno solo, y la identidad viaja en los tokens.** El archivo de diseño dibuja una
barra lateral navy a altura completa; el portal tiene una cabecera horizontal. La tentación es dar
un chasis a cada tema. **Se rechaza**: dos chasis son dos productos, duplican cada estado no feliz y
harían imposible sostener la matriz 7×4. Decisión: **el chasis pasa a ser de barra lateral para los
dos temas**, porque además resuelve el defecto que la evaluación midió —once controles en una barra
de 52 px— y la identidad se expresa donde debe, en el color y la superficie: el tema de omisión
conserva su retícula visible y su activo por luminancia; el institucional pinta la barra en navy,
rellena la acción en verde azulado y no pinta retícula. Un chasis, dos mundos.

**2. El logotipo se toma de la guía, no de las maquetas.** El archivo se contradice: la página
normativa «Uso del logotipo» declara el **símbolo K** en teja de esquinas redondeadas con tres
variantes —Principal teal, Inverso sobre navy, Monocromático navy— y sus reglas de área de
protección y tamaño mínimo; las cinco maquetas de prototipo usan **otra marca**, una cinta con rombo
ámbar. Se implementa el de la guía, que es la sección normativa y la que trae reglas de aplicación.
**La discrepancia se anota en el handoff y en `a4_08`**, porque callarla sería publicar una elección
sin decir que hubo elección. Hoy el portal no pinta ninguno de los dos: pinta `lucide:circuit-board`,
un icono genérico del paquete, teñido con el color informativo.

**3. El logotipo se dibuja, no se genera.** Se ofreció el MCP de imágenes. Se rechaza: `a4_03` exige
que la marca sea **siempre vectorial**, y la propia guía prohíbe «deformar, rotar, recolorear». Un
PNG generado es una reinterpretación, que es exactamente lo que la regla prohíbe. Se construye como
SVG en línea midiendo la lámina, con las tres variantes y la geometría declarada en proporción.

**4. TanStack Table entra al stack.** Hoy hay **siete** componentes con `<table>` escrito a mano y
ninguno tiene orden, `aria-sort` ni selección. `@tanstack/vue-table` es **headless**: no trae una
sola línea de estilo, así que no choca con la decisión irrevocable de Tailwind v4 con tokens propios
ni con «sin sistema de diseño externo». Entra como dependencia nueva y **se registra en la tabla de
decisiones irrevocables de la raíz**, que hoy no la lista. Lo que aporta es justo lo que la
evaluación reclama: orden anunciado, selección y densidad.

**5. ECharts ya está y no se toca: lo que falta es dónde.** `echarts@6.1.0` y `vue-echarts@8.1.0`
están instalados y viven en `/exploracion/tableros`. Lo que las maquetas muestran y el portal no
tiene son **tarjetas de indicador** en `/inicio` y en el centro de trabajo. Se construyen con los
tokens, y la micrográfica de tendencia usa el `VChart.client.vue` que ya existe. **No se añade
ninguna biblioteca de gráficas.**

**6. Los cuatro conmutadores se funden a dos.** Medido: **11 controles** en la cabecera, todos
icónicos salvo ES/EN, contra un umbral de cuatro opciones visibles. Tema y modo son el mismo eje
partido —«cómo se ve el portal»—: se funden en un control de **apariencia** con etiqueta visible. El
de perfil se queda porque es el motor de la demostración; el de idioma es obligatorio por i18n real.
De 11 controles a 6, y con rótulo.

**7. Se rechaza la recomendación de `ui-ux-pro-max` para este producto.** Su ficha de «Financial
Dashboard» prescribe *dark OLED + alertas rojo/verde*. Aplicarla desharía dos decisiones **medidas**:
el sistema eliminó el verde del canal de estado porque rojo contra verde separa dE 20.0 bajo
protanopia simulada, justo en el umbral; y ninguno de los dos temas usa negro puro por regla propia.
Se conserva de esa skill lo que sí aplica y es verificable: contraste, objetivo táctil, regiones
vivas, etiqueta visible en campos y cifras tabulares.

**8. Las nueve etiquetas inertes de la barra lateral se retiran.** «Consumo por API», «Calidad de
datos», «Vista previa» y seis más se pintan bajo «FACETAS TRANSVERSALES» como `listitem` sin enlace.
Son la salida del *card sorting* de A3 renderizada como navegación. `PRODUCT.md` fija que **gana el
usuario trabajando, no el evaluador**: una etiqueta que no lleva a ningún sitio le cuesta a Laura y
solo le sirve al evaluador. Su contenido ya está publicado en `a4_02` como mapa; en la barra lateral
se retiran.

**9. La copia de navegación deja de citar la numeración del mapa.** Hoy el portal publica como
descripción de producto «4. Administración — 4.1 a 4.4» y el nombre accesible de dos ítems es «2.2
Consulta y filtros, faceta transversal». Un lector de pantalla oye la numeración de un entregable
académico. Se reescribe a lenguaje de negocio; la trazabilidad al mapa vive en `a4_02`, que es su
sitio.

**10. `/exploracion` y `/gobierno` dejan de abrir igual.** La evaluación lo llamó el hallazgo mayor:
misma etiqueta, mismo *placeholder*, mismo vacío casi idéntico. Decisión: **`/exploracion` es
descubrimiento y `/gobierno` es defensa del dato**. El catálogo gana filas interactivas que llevan al
linaje; el diccionario conserva su buscador pero abre declarando qué resuelve. Ninguna de las dos
pierde su rama del contrato de A3.

**11. Se documenta lo que no cabe.** El SUS de A5, la paginación con desplazamiento del catálogo y el
tercer nivel de la escala de contraste para componente y texto grande **no entran**. Se declaran en
el handoff con su motivo, no se dejan implícitos.

---

## 1. Criterios de aceptación con métricas verificables

| CA | Criterio | Métrica | Cómo se verifica |
|---|---|---|---|
| **CA-1** | El tema institucional lleva su color de acción | `--color-accion` resuelve a `#086B70` en claro y su elevación en oscuro; el de omisión resuelve a su corriente plena, **byte a byte igual que hoy** | `test_contraste_temas.py` + medición en navegador |
| **CA-2** | El octeto del archivo está completo | Los **8** colores declarados aparecen en el sistema con su procedencia citada; ninguno inventado sin declararse | Tabla de `a4_08` cruzada contra `design/sistema.py` |
| **CA-3** | La retícula no se hereda | `--color-reticula` se pinta del propio suelo bajo el tema institucional; el chasis no dibuja cuadrícula | Recorrido V1 |
| **CA-4** | Cero incumplimientos, cuatro combinaciones | `incumplimientos(tema, modo)` vacío en las 4 | `pytest tests/ml/test_contraste_temas.py` |
| **CA-5** | La separación bajo dicromacia no baja | Peor par ≥ **13.6** en claro y ≥ **21.5** en oscuro, en los dos temas | `separaciones(tema, modo)` |
| **CA-6** | **El logotipo es el de la guía, vectorial y en tres variantes** | `MarcaKarisma.vue` emite SVG; 3 variantes; **cero `<img>` y cero iconos de paquete** en la marca | `marca.spec.ts` + inspección visual |
| **CA-7** | **El chasis es de barra lateral en las 10 rutas** | Barra lateral presente y navegación con etiqueta de texto en las 10 rutas del contrato | `chasis.spec.ts` + recorrido V2 |
| **CA-8** | **El cromo baja de 11 controles a 6** | Conteo de controles interactivos en `[data-cabecera-producto]` ≤ **6**; el de apariencia lleva rótulo visible | Medición en navegador (V3) |
| **CA-9** | **El conmutador de perfil es alcanzable en móvil** | A 390 px el control es visible y su caja está dentro del lienzo; objetivo ≥ 44×44 | V4 |
| **CA-10** | **Cero desplazamiento horizontal del cuerpo** | A 390, 768, 1280 y 1440: `scrollWidth === clientWidth` en las 10 rutas | V5. **Hoy `/inicio` desborda 194 px a 390** |
| **CA-11** | **«En revisión» y «Obsoleto» dejan de compartir canal** | Los tres estados de certificación con **icono distinto** y color distinto; verificado bajo las tres dicromacias | `certificacion.spec.ts` + `contraste.py` |
| **CA-12** | **El catálogo deja de ser un callejón** | Cada fila lleva al linaje del campo; ≥1 salida hacia `/gobierno` desde el resultado | `exploracionCatalogo.spec.ts` + V6 |
| **CA-13** | **La búsqueda es direccionable** | `/exploracion?q=saldo` abre con el término aplicado y el resultado pintado; el término sobrevive a la ida y vuelta | V7 |
| **CA-14** | **Las tablas se construyen con TanStack** | Los 7 componentes con tabla usan `@tanstack/vue-table`; orden anunciado con `aria-sort`; altura de fila **34 px** como declara `DESIGN.md` | `tablaDatos.spec.ts` |
| **CA-15** | **Los cuatro estados se anuncian** | `listo` y `vacio` ganan región viva; `cargando` y `error` la conservan | `exploracionCatalogo.spec.ts` |
| **CA-16** | **Superficies contenidas** | Tarjeta con filete de un pelo, radio ≤ **8 px** y barra de color a la izquierda, como declara la guía | `superficies.spec.ts` + V8 |
| **CA-17** | **Tarjetas de indicador en `/inicio`** | ≥4 tarjetas con etiqueta, marca de tiempo y cifra; la cifra en monoespaciada | V9 |
| **CA-18** | **La copia deja de citar el mapa** | `grep -E '[0-9]\.[0-9]' ` sobre los valores visibles de i18n → **0** en descripciones de producto | `contratos.spec.ts` ampliada |
| **CA-19** | **Las nueve etiquetas inertes se retiran** | Cero `listitem` sin enlace en la barra lateral | `chasis.spec.ts` |
| **CA-20** | **`/exploracion` y `/gobierno` abren distinto** | Etiqueta, ayuda y estado inicial **distintos**, cada uno declarando qué resuelve | Revisión + `contratos.spec.ts` |
| **CA-21** | **El PDF de la entrega queda listo** | `Entregable Actividad 4_equipo_8.pdf` en `docs/semana_4/`, sin referencias sin resolver ni desbordes | `latexmk -xelatex main_a4.tex` |
| **CA-22** | **El acumulado incorpora el avance** | `main_completo.tex` compila con la parte IV completa | `latexmk -xelatex main_completo.tex` |
| **CA-23** | QA gate | `make check` limpio; frontend ≥ 50 %; gate `backend/app` + `ml` ≥ 70 % | `make check && make test` |

---

## 2. Arquitectura de la solución

### 2.1 De dónde sale cada decisión visual

```
  docs/entregables/figma/*.pdf        el archivo de diseño, leído como imagen
        |                             (los 8 colores, los 12 conjuntos, el chasis)
        v
  design/sistema.py                   21 tokens x 2 temas x 2 modos + familias
        |                             (unica fuente; nada se teclea aguas abajo)
        +--> design/contraste.py  ---> matriz y separaciones POR TEMA
        +--> design/emitir.py
                 |
                 +--> frontend/app/assets/css/main.css        [GENERADO]
                 +--> frontend/app/utils/tokens.generated.ts  [GENERADO]
                              |
                              v
        chasis (barra lateral)  ->  superficies  ->  componentes  ->  capturas  ->  documento
```

### 2.2 El chasis, y qué cambia con el tema

| Pieza | Tema de omisión | Tema institucional |
|---|---|---|
| Fondo del chasis | retícula modular visible | sin retícula: `--color-reticula` es su propio suelo |
| Barra lateral | suelo alterno, activo por luminancia y peso | navy `#102A43`, activo en bloque de acción relleno |
| Acción primaria | corriente plena, `#14171D` | verde azulado `#086B70` |
| Selección | tinte neutro | tinte de acción `#E6F2F1` |
| Tarjeta | filete de un pelo, sin radio | filete más radio ≤ 8 px y barra de color a la izquierda |
| Familia | Lexend Deca y Fira Sans | Inter |

**Lo que no cambia con el tema**: la estructura, el orden de tabulación, los estados no felices, la
franja de alcance y las seis series de datos. Un tema que cambiara la estructura sería otro producto.

### 2.3 Los ocho colores del archivo, y dónde aterriza cada uno

| Rol del archivo | Valor | Token del sistema | Nota |
|---|---|---|---|
| Navegación | `102A43` | `corriente-pleno` claro · `ground-alt` oscuro | Estructura |
| Secundario | `1D4C6E` | `corriente-medio` claro · base de `info` | |
| **Acción** | `086B70` | **`accion`** | La ranura que faltaba |
| **Apoyo** | `15989A` | **`accion-apoyo`** | Realce y foco |
| Atención | `B97812` | base de `aviso` | Oscurecido 12 % para cumplir 4.5:1; la divergencia se declara |
| Éxito | `287A58` | `ok` | |
| Error | `B8443F` | base de `error` | Oscurecido 20 %: a su valor el par error/éxito cae a dE 10.1 |
| Superficie | `FFFFFF` | `ground` | |

### 2.4 Los tres estados de certificación, que hoy son dos

El defecto: `codigo === 'certificado' ? 'circle-check' : 'triangle-alert'`. «En revisión» y
«Obsoleto» comparten icono **y** color, y significan cosas opuestas para la persona primaria.

| Estado | Icono | Canal | Por qué |
|---|---|---|---|
| Certificado | marca de verificación | `ok` | Se puede usar |
| En revisión | reloj | `aviso` | Se puede usar con reserva |
| Obsoleto | círculo tachado | `error` | **No se debe usar** |

Tres formas y tres canales, que es la regla que el sistema declara como su eje. La separación de los
tres se mide bajo las tres dicromacias antes de embarcarse.

---

## 3. Archivos exactos a crear o modificar

| Ruta | C/M | Qué cambia | Ola |
|---|---|---|---|
| `design/sistema.py` | M | Estados de certificación como tokens; ajuste de la barra lateral por tema | A |
| `design/contraste.py` | M | Los tres estados de certificación entran a `separaciones` | A |
| `design/emitir.py` | M | Emisión de lo anterior | A |
| `tests/ml/test_contraste_temas.py` | M | Fijación ampliada y separación de los tres estados | A |
| `tests/ml/test_emision_temas.py` | M | Resolución por combinación de los tokens nuevos | A |
| `frontend/app/assets/css/main.css` | **G** | **Generado por `make tokens`** | A |
| `frontend/app/utils/tokens.generated.ts` | **G** | **Generado** | A |
| `frontend/app/components/comun/MarcaKarisma.vue` | C | El símbolo K en SVG, tres variantes | B |
| `frontend/app/components/comun/SelectorApariencia.vue` | C | Funde tema y modo en un control con rótulo | B |
| `frontend/app/components/comun/{SelectorTema,SelectorModo}.vue` | **B** | Se retiran: los absorbe `SelectorApariencia` | B |
| `frontend/app/components/comun/CabeceraProducto.vue` | M | Barra fina: marca, buscador, apariencia, perfil, idioma | B |
| `frontend/app/components/nav/BarraLateral.vue` | M | Navegación con etiqueta; se retiran las nueve inertes | B |
| `frontend/app/layouts/portal.vue` | M | Chasis de barra lateral; retícula por token | B |
| `frontend/app/layouts/{default,acceso}.vue` | M | Mismo chasis, sin navegación | B |
| `frontend/app/components/comun/TarjetaContenida.vue` | C | Superficie con filete, radio ≤ 8 px y barra de color | C |
| `frontend/app/components/comun/TablaDatos.vue` | C | Tabla con TanStack: orden, `aria-sort`, fila de 34 px | C |
| `frontend/app/components/{administracion/TablaUsuarios,tablero/TablaDetalleSerie,serie/Tabla}.vue` | M | Pasan a `TablaDatos` | C |
| `frontend/app/components/inicio/TarjetaIndicador.vue` | C | Indicador con etiqueta, marca de tiempo y cifra | C |
| `frontend/app/components/inicio/BloqueLista.vue` | M | **Corrige el desborde de 194 px a 390** | C |
| `frontend/app/components/inicio/Espacio{Operativo,Analista,Directivo}.vue` | M | Tarjetas de indicador; mismo arreglo de rejilla | C |
| `frontend/app/components/exploracion/ResultadosCatalogo.vue` | M | Filas interactivas al linaje; tres estados; región viva; columnas | D |
| `frontend/app/components/exploracion/{BuscadorCatalogo,FiltroDominios,AccionesCatalogo}.vue` | M | Acción primaria en la columna de lectura; copia de producto | D |
| `frontend/app/pages/exploracion/index.vue` | M | Término desde la URL; distinción con gobierno | D |
| `frontend/app/composables/useBusquedaCatalogo.ts` | M | Sincroniza el término con el query | D |
| `frontend/app/pages/{acceso,index,inicio,gobierno,asistente,administracion,guia}.vue` | M | Chasis nuevo; énfasis corregido en acceso; `guia` publica los tokens nuevos | D |
| `frontend/i18n/locales/{es,en}.json` | M | Copia de producto; se retira la numeración del mapa | D |
| `frontend/package.json` | M | `@tanstack/vue-table` | C |
| `frontend/test/*.spec.ts` | C/M | §6 | A–D |
| `docs/entregables/contenido/a4_08_tema_y_flujos.tex` | M | Los 8 colores, el logotipo con su discrepancia, el chasis | E |
| `docs/entregables/contenido/a4_0{2,3,4,5,7}.tex` | M | Pantallas recontadas, iteración tercera, alcance e inventario | E |
| `docs/entregables/figuras/a4/tema/*.png` | M | **Se recapturan las 11**: el chasis cambió | E |
| `docs/semana_4/Entregable Actividad 4_equipo_8.pdf` | M | Se regenera | E |
| `AGENTS.md` y `CLAUDE.md` de la raíz | M | TanStack Table entra a las decisiones irrevocables | E |

**Prohibido tocar**: `estilo/uxdoc.sty` · `estilo/a4_tokens.tex` y `generar_tokens_a4.py` ·
**`figuras/a4/antes/**` y `despues/**`** · `backend/`, `db/`, `ml/`.

---

## 4. Firmas públicas de cada módulo nuevo

```ts
// frontend/app/components/comun/MarcaKarisma.vue
defineProps<{ variante?: 'principal' | 'inverso' | 'monocromatico', conNombre?: boolean }>()

// frontend/app/components/comun/TablaDatos.vue
defineProps<{
  columnas: readonly ColumnDef<TFila>[]
  filas: readonly TFila[]
  ordenInicial?: SortingState
  vacio?: string
}>()

// frontend/app/components/comun/TarjetaContenida.vue
defineProps<{ canal?: 'accion' | 'aviso' | 'ok' | 'error' | 'neutro', titulo?: string }>()

// frontend/app/components/inicio/TarjetaIndicador.vue
defineProps<{ etiqueta: string, valor: string, actualizado: string, canal?: CanalTarjeta }>()
```

```python
# design/sistema.py
CERTIFICACION: Final[tuple[Token, ...]]  # certificado, en-revision, obsoleto
```

**Cero tipos nuevos en el contrato de navegación.** `EstadoAlcance` no se toca.

---

## 5. Dominios y sub-tareas, con el write-set disjunto

**Checklist de dominios**: [ ] backend · [x] frontend · [ ] ml · [ ] db · [x] tests · [x] docs · [x] design

| Ola | Qué entrega | SP | Write-set exclusivo | Depende de |
|---|---|---|---|---|
| **A** sistema | Estados de certificación, generados al día | 3 | `design/**`, `tests/ml/**` | nada |
| **B** chasis y marca | Barra lateral, marca en SVG, cromo de 6 controles | 6 | `components/comun/{MarcaKarisma,SelectorApariencia,CabeceraProducto}.vue`, `components/nav/BarraLateral.vue`, `layouts/**` | A |
| **C** superficies y tablas | Tarjeta, TanStack, indicadores, arreglo del desborde | 5 | `components/comun/{TarjetaContenida,TablaDatos}.vue`, `components/inicio/**`, las 3 tablas, `package.json` | A |
| **D** pantallas y copia | Catálogo con linaje, URL, tres estados, i18n de producto | 5 | `components/exploracion/**`, `pages/**`, `composables/useBusquedaCatalogo.ts`, `i18n/**` | B y C |
| **E** documento y entrega | Los `.tex`, las 11 capturas nuevas, los dos envoltorios, el PDF | 2 | `docs/entregables/**`, `docs/semana_4/**`, guías de la raíz | A–D |

**A va primero y sola**: emite lo que las demás consumen. **B y C corren en paralelo**: sus
write-sets son disjuntos y ninguna toca i18n. **D va después de las dos** porque compone sobre el
chasis y las superficies, y es la única que escribe i18n. **E cierra.**

**Regla del AGENTS.md de carpeta**: B, C y D escriben en `frontend/`. **Ninguna actualiza
`frontend/AGENTS.md`**; lo hace el orquestador al integrar.

**Si el reloj aprieta, el orden es A, B, E.** Con A y B el tema deja de ser falso y el cromo deja de
ser una barra de depuración, que es el 80 % de lo que la revisión señaló.

---

## 6. Plan de tests

Cada prueba declara qué defecto concreto la haría fallar. Las que no lo respondan no se escriben.

### 6.1 Sistema — `tests/ml/`

| Prueba | Defecto que la haría fallar | Umbral |
|---|---|---|
| Los tres estados de certificación separan | «En revisión» y «Obsoleto» vuelven a compartir canal y dos estados opuestos se leen igual | peor par de los tres ≥ el piso del tema |
| El tema de omisión sigue fijado | Un token de `corriente` cambia y las 15 capturas entregadas dejan de corresponder | valores de hoy, byte a byte |
| Los 8 colores del archivo están presentes | Alguien vuelve a derivar la paleta de una transcripción y se pierde un color | los 8, con su procedencia |

### 6.2 Frontend — vitest, umbral 50 %

| Prueba | Archivo | Defecto que la haría fallar |
|---|---|---|
| La marca emite SVG, nunca un icono de paquete | `marca.spec.ts` | Vuelve `lucide:circuit-board` y el portal publica un logotipo que no es el suyo |
| Las tres variantes se distinguen | `marca.spec.ts` | El inverso se pinta igual que el principal sobre navy y desaparece |
| El chasis monta barra lateral en las 10 rutas | `chasis.spec.ts` | Una ruta se queda con el chasis viejo y el portal tiene dos navegaciones |
| Cero elementos de lista sin enlace en la barra | `chasis.spec.ts` | Vuelven las nueve etiquetas inertes |
| El cromo no pasa de 6 controles | `chasis.spec.ts` | Alguien añade un quinto conmutador y vuelve la barra de once |
| El control de apariencia ofrece los 2 temas y los 3 modos | `apariencia.spec.ts` | Al fundir los dos grupos se pierde una opción en silencio |
| La tabla anuncia su orden | `tablaDatos.spec.ts` | Se ordena visualmente sin `aria-sort` y un lector de pantalla no se entera |
| La fila mide 34 px | `tablaDatos.spec.ts` | Vuelve la fila de 80 px y la densidad que el sistema declara es falsa |
| Cada fila del catálogo lleva al linaje | `exploracionCatalogo.spec.ts` | El catálogo vuelve a ser un callejón y la promesa n.º 1 del producto no tiene ruta |
| `listo` y `vacio` anuncian | `exploracionCatalogo.spec.ts` | Dos de los cuatro estados vuelven a ser mudos |
| El término viaja en la URL | `exploracionCatalogo.spec.ts` | No se puede compartir un hallazgo y salir a exportar lo destruye |
| Los tres estados de certificación tienen icono distinto | `certificacion.spec.ts` | Vuelven a compartir triángulo y color |
| La copia no cita la numeración del mapa | `contratos.spec.ts` | Vuelve «4.1 a 4.4» como descripción de producto |

**No se escriben**: pruebas sobre el aspecto de un tema, sobre la existencia de PNG, ni sobre el
contenido de los `.tex` más allá de las dos que ya existen.

### 6.3 Verificación en navegador con el MCP de Playwright

| # | Recorrido | Criterio |
|---|---|---|
| V1 | Las 4 combinaciones sobre `/inicio` y `/exploracion` | Suelos distintos; **sin retícula** bajo el institucional |
| V2 | Las 10 rutas del contrato | Barra lateral presente, activo marcado, etiquetas de texto |
| V3 | Conteo del cromo | ≤ 6 controles; el de apariencia con rótulo visible |
| V4 | El perfil a 390 px | Visible, dentro del lienzo, objetivo ≥ 44×44 |
| V5 | **Desplazamiento horizontal a 390, 768, 1280 y 1440** | `scrollWidth === clientWidth` en las 10 rutas |
| V6 | Fila del catálogo → linaje | Aterriza en el linaje del campo |
| V7 | `/exploracion?q=saldo` en frío | Abre con el término aplicado y resultados |
| V8 | Superficies bajo el institucional | Tarjeta con radio ≤ 8 px y barra de color |
| V9 | Indicadores en `/inicio` | ≥4 tarjetas con cifra en monoespaciada |
| V10 | Las 11 capturas del tema | 1440×900, chasis nuevo |

---

## 7. Nube

**No toca la nube.** Ningún recurso, ningún comando, ningún secreto.

## 8. Schema

**No toca schema.** Ninguna migración. La preferencia de apariencia sigue en cookie.

---

## 9. Rúbrica: a qué rubro responde

| Apartado | Peso | Cómo lo mueve |
|---|---|---|
| **3 · Prototipos de alta fidelidad** | 50 % | **Directo.** El prototipo pasa a parecerse a su propio archivo de diseño, el catálogo deja de ser un callejón y el cromo deja de ser una barra de depuración. Sin desplazamiento horizontal en móvil |
| **4 · Guía de estilos** | 45 % | **Directo.** Los 8 colores con su procedencia, el logotipo con sus tres variantes y sus reglas, y la discrepancia del archivo declarada en vez de escondida |
| Introducción y método | 3 % | La tercera iteración documentada, esta vez provocada por una revisión de diseño con hallazgos numerados |

---

## 10. Riesgos y mitigaciones

| # | Riesgo | Prob. | Impacto | Mitigación |
|---|---|---|---|---|
| R1 | **No cabe antes del domingo 20:00** | **Alta** | **Crítico** | Las olas son independientes y el orden de recorte está escrito: A, B, E. El PDF queda compilable al cerrar cada ola |
| R2 | El chasis nuevo rompe las 48 suites | Alta | Medio | B corre sola y deja la suite en verde antes de que C y D empiecen |
| R3 | Recapturar las 11 imágenes consume la última hora | Media | Medio | Se recapturan **al final**, en una sola pasada guionizada |
| R4 | TanStack cambia el marcado y tumba pruebas de montaje | Media | Medio | `TablaDatos` conserva los `data-*` que las pruebas ya consultan |
| R5 | El tema de omisión se mueve sin querer | Baja | **Crítico** | La prueba de fijación corre antes de cada ola |
| R6 | La marca dibujada no coincide con la lámina | Media | Alto | Se mide sobre la lámina y se compara la captura contra ella |
| R7 | Retirar las nueve etiquetas se lee como perder cobertura de A3 | Media | Bajo | `a4_02` conserva el mapa completo; se anota en el documento |

---

## 11. Discrepancias entre las fuentes

| Fuente | Dice | Se resuelve |
|---|---|---|
| Guía de Figma contra maquetas de Figma | Logotipo «K» en teja teal · cinta con rombo ámbar | Gana la guía, por normativa. **Se declara** |
| Plan de US-ENTREGA-A4 §2.3 contra el archivo | 6 colores · **8** colores | Gana el archivo |
| `ui-ux-pro-max` contra `design/sistema.py` | dark OLED con rojo/verde · verde eliminado por medición | Gana la medición |
| `checklist-ui.md` regla 4 contra el archivo | ni blanco puro · Superficie `FFFFFF` | Gana el archivo, y se anota la excepción |
| `DESIGN.md` contra el catálogo | fila de 34 px · fila de 80 px | Gana `DESIGN.md` |
| Raíz contra `package.json` | no lista TanStack Table | Se añade a las decisiones irrevocables |

---

## 12. Checklist de cierre verificable

- [ ] Los 8 colores del archivo presentes, con procedencia citada uno por uno
- [ ] `--color-accion` teal bajo el institucional; el tema de omisión sin mover un valor
- [ ] Retícula apagada bajo el institucional, comprobada en navegador
- [ ] Cero incumplimientos y separación sobre el piso, en las 4 combinaciones
- [ ] Los tres estados de certificación con icono y canal distintos, medidos bajo 3 dicromacias
- [ ] Logotipo en SVG, tres variantes, **cero iconos de paquete** en la marca
- [ ] Discrepancia del logotipo declarada en el handoff y en `a4_08`
- [ ] Chasis de barra lateral en las 10 rutas, con etiquetas de texto
- [ ] Cromo de **6 controles** con rótulo visible; perfil alcanzable a 390 px
- [ ] Las nueve etiquetas inertes, retiradas
- [ ] **Cero desplazamiento horizontal** a 390, 768, 1280 y 1440, en las 10 rutas
- [ ] Cada fila del catálogo lleva al linaje; `/exploracion` y `/gobierno` abren distinto
- [ ] `?q=` aplicado en frío; el término sobrevive a la ida y vuelta
- [ ] Los cuatro estados anuncian; fila de 34 px; orden con `aria-sort`
- [ ] Tarjetas con radio ≤ 8 px y barra de color; indicadores en `/inicio`
- [ ] La copia no cita la numeración del mapa en ninguna cadena visible
- [ ] TanStack Table registrado en las decisiones irrevocables de la raíz
- [ ] `make check` limpio · `make test` en verde · cobertura sobre los pisos
- [ ] Las 11 capturas rehechas con el chasis nuevo; `antes/` y `despues/` intactas
- [ ] `main_a4.tex` y `main_completo.tex` sin referencias sin resolver ni desbordes
- [ ] PDF regenerado en `docs/semana_4/` con el nombre exacto
- [ ] Subido a Canvas antes del **dom 16, 20:00**
- [ ] Handoff actualizado; commits sin trailer de asistente; **a la espera de visto bueno**
