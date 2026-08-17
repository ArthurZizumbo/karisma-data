# Handoff US-A4-EXCELENCIA — Los dos temas completos y la Actividad 4 en banda alta

**Estado**: testing
**Epic**: UX (con trabajo en E0, sistema de diseño, y E2, pantallas del contrato)
**Sprint**: S4, cierre · **Actividad**: A4 (dom 16-ago-2026)
**Rama**: `us-a4-excelencia`, con el árbol **limpio**. El de US-ENTREGA-A4 ya quedó commiteado en
`b36f0d5`, así que esta US arranca sobre una punta propia y no sobre un árbol sucio ajeno. Sin PR ni
push hasta visto bueno (discrepancia RU-11 declarada)
**SHA base**: `3d4db21` — `git rev-parse --short HEAD` al abrir implementación, 15-ago-2026.
Ancla del diff de esta US: `git diff --name-only 3d4db21`. **QA no usa `HEAD~N`**
**Estimación**: 21 SP en cinco olas
**Plan**: [`docs/us-planning/us-a4-excelencia.md`](../us-planning/us-a4-excelencia.md)

> **Por qué existe esta US.** US-ENTREGA-A4 entregó un tema llamado institucional que no lo era. La
> revisión fue directa: *«nada que ver con lo de Figma»*, *«no cambia nada con respecto al que ya
> traíamos»*, *«el logo que traíamos pusiste uno que nada que ver»*. Las tres son ciertas y están
> verificadas contra el archivo. Esta US cierra esa brecha y absorbe los hallazgos de las dos
> evaluaciones de diseño del 15-ago.

---

## La causa raíz, escrita para que no se repita

La ola A de US-ENTREGA-A4 construyó la paleta **desde la tabla §2.3 de su propio plan**, no desde el
archivo de diseño. Esa tabla era una transcripción parcial: recogía seis colores de ocho. Los dos que
faltaban son **Acción `086B70` y Apoyo `15989A`**, los verdes azulados que la propia lámina declara
como el corazón de la identidad —*«el azul profundo estructura la navegación; el verde azulado
concentra acciones y selección; el ámbar se reserva para atención»*—.

La renuncia quedó escrita como decisión 10 del plan anterior: *«el color de acción no entra en los 17
tokens: el contrato no tiene ranura de acción y abrirla no cabe en esta US»*. Con esa frase se
descartó justo el color que daba la identidad, y el resultado fue un tema que es la rampa de siempre
en otro azul.

**La lección operativa**: cuando el plan transcribe una fuente, la ola que implementa **relee la
fuente**, no la transcripción. Una tabla intermedia es una copia, y una copia puede estar incompleta
sin que nada lo delate.

---

## Dominios y sub-tareas tocados

- [ ] backend · [ ] ml · [ ] agent · [ ] infra · [ ] db
- [x] design — estados de certificación y ajuste del chasis por tema
- [x] frontend — chasis, marca, superficies, tablas, catálogo y copia
- [x] tests — seis suites nuevas y cuatro ampliadas
- [x] docs — cinco `.tex`, las 11 capturas y los dos envoltorios

**Sí se reparte**, en cinco olas.

| Ola | Qué entrega | SP | Depende de |
|---|---|---|---|
| **A** sistema | Estados de certificación; generados al día | 3 | nada |
| **B** chasis y marca | Barra lateral, marca en SVG, cromo de 6 controles | 6 | A |
| **C** superficies y tablas | Tarjeta, TanStack, indicadores, arreglo del desborde | 5 | A |
| **D** pantallas y copia | Catálogo con linaje, URL, tres estados, i18n | 5 | B y C |
| **E** documento y entrega | Los `.tex`, las capturas, los envoltorios y el PDF | 2 | A–D |

**B y C corren en paralelo.** D es la única que escribe i18n. **Si el reloj aprieta: A, B, E.**

---

## Lo que ya quedó hecho, el 15-ago

Antes de abrir esta US se corrigió la capa que todas las demás consumen. **Ya está commiteado** en
`76dd8e5`, dentro del SHA base de esta US: las olas lo consumen, no lo rehacen.

| Cambio | Estado |
|---|---|
| `--color-accion` = `086B70` bajo el institucional, `14171D` bajo el de omisión | **Hecho.** El de omisión es idéntico a su corriente plena, así que no se mueve un píxel |
| `--color-accion-apoyo` = `15989A` · `--color-seleccion` en tinte | **Hecho** |
| `--color-reticula` separado de `--color-grid`, pintado del propio suelo bajo el institucional | **Hecho** en el token; **falta** que `layouts/portal.vue` lo lea |
| `info` deja de ser un violeta inventado en claro y vuelve al azul del archivo | **Hecho**; en oscuro conserva el violeta, con la razón real escrita |
| Medición: **21 tokens, 0 incumplimientos en las 4 combinaciones**, separación 13.6/21.5 y 14.5/22.6 | **Verificado** |

---

## Zonas sensibles

| Archivo | Por qué |
|---|---|
| `frontend/app/assets/css/main.css` · `app/utils/tokens.generated.ts` | **Generados** por `design/emitir.py`. `make tokens`, jamás a mano |
| `docs/entregables/figuras/a4/{antes,despues}/**` | **Evidencia cerrada.** Una recaptura destruye el par y tumba el criterio de iteración |
| `docs/entregables/figuras/a4/tema/**` | **Se recapturan las 11**: el chasis cambia y las de ayer dejan de corresponder |
| `design/sistema.py` | Fuente única. La prueba de fijación del tema de omisión corre **antes** de cada ola |
| `frontend/test/alcancePrototipos.spec.ts` · `rutaRama.spec.ts` | Leen `.tex`: un cambio de copia puede ponerlas en rojo |
| `frontend/AGENTS.md` | Lo escribe **el orquestador al integrar**, no las olas B, C ni D |
| `AGENTS.md` y `CLAUDE.md` de la raíz | Espejos. TanStack Table entra a la tabla de decisiones irrevocables |

---

## Decisiones tomadas en planeación

1. **Un solo chasis, la identidad en los tokens.** El portal pasa a barra lateral para los dos temas.
   Dos chasis serían dos productos y duplicarían cada estado no feliz. El tema de omisión conserva su
   retícula y su activo por luminancia; el institucional pinta navy, rellena la acción en teal y no
   pinta retícula.
2. **El logotipo sale de la guía, no de las maquetas.** El archivo se contradice: la página normativa
   declara el símbolo K en teja con tres variantes y reglas; las cinco maquetas usan otra marca, una
   cinta con rombo ámbar. Gana la guía. **La discrepancia se declara** en `a4_08`.
3. **El logotipo se dibuja en SVG, no se genera como imagen.** `a4_03` exige marca vectorial y la
   guía prohíbe recolorear o deformar. Un PNG generado sería una reinterpretación.
4. **TanStack Table entra al stack.** Headless, sin estilos: no choca con Tailwind v4 ni con «sin
   sistema de diseño externo». Hoy hay siete tablas escritas a mano y ninguna anuncia su orden.
5. **ECharts no se toca.** Ya está instalado y en uso. Lo que falta son tarjetas de indicador, que se
   construyen con los tokens.
6. **Los cuatro conmutadores se funden a dos.** Tema y modo son el mismo eje. De 11 controles a 6, y
   con rótulo visible.
7. **Se rechaza la ficha de `ui-ux-pro-max` para «Financial Dashboard»**: prescribe dark OLED con
   alertas rojo/verde, y este sistema eliminó el verde del canal de estado por medición (dE 20.0 bajo
   protanopia, justo en el umbral).
8. **Las nueve etiquetas inertes de la barra lateral se retiran.** Son *card sorting* renderizado
   como navegación. `PRODUCT.md` fija que gana el usuario trabajando, no el evaluador.
9. **La copia deja de citar la numeración del mapa.** Hoy un lector de pantalla oye «2.2 Consulta y
   filtros, faceta transversal». La trazabilidad vive en `a4_02`, que es su sitio.
10. **`/exploracion` es descubrimiento y `/gobierno` es defensa del dato.** Hoy abren idénticas.
11. **Los tres estados de certificación se separan.** «En revisión» y «Obsoleto» comparten hoy color
    **e** icono, y significan cosas opuestas para la persona primaria.

---

## Hallazgos que esta US absorbe

### De la revisión de diseño — promedio 2.4 / 4 en las diez heurísticas

| # | Hallazgo | Dónde | Ola |
|---|---|---|---|
| 1 | **El catálogo es un callejón**: ninguna fila es interactiva y no hay ruta al linaje. La promesa n.º 1 del producto no se alcanza desde la pantalla de descubrimiento | `ResultadosCatalogo.vue:154-190` | D |
| 2 | **`/exploracion` es casi clon de `/gobierno`**: misma etiqueta, mismo *placeholder*, mismo vacío | las dos pantallas | D |
| 3 | **«En revisión» y «Obsoleto» comparten color e icono** | `ResultadosCatalogo.vue:60-61` | A y D |
| 4 | **11 controles en el cromo**, ninguno con rótulo | `CabeceraProducto.vue:54-58` | B |
| 5 | **La densidad prometida no se entrega**: fila de 80 px contra los 34 px que declara `DESIGN.md` | `ResultadosCatalogo.vue:158` | C y D |
| 6 | **La búsqueda no es direccionable** y se destruye al usar las salidas que la propia pantalla ofrece | `useBusquedaCatalogo.ts` | D |
| 7 | **Dos de los cuatro estados no se anuncian**: `listo` y `vacio` sin región viva | `ResultadosCatalogo.vue` | D |
| 8 | **Nueve etiquetas inertes** en la barra lateral | `BarraLateral.vue` | B |
| 9 | **La copia publica la numeración del mapa** como descripción de producto | `i18n/locales/*.json:152-155` | D |
| 10 | **`/acceso` tiene el énfasis invertido**: el camino recomendado va en color de precaución y el que nadie puede usar se lleva el botón primario | `acceso.vue` | D |

### De la evidencia mecánica

| # | Hallazgo | Medición | Ola |
|---|---|---|---|
| 11 | **Desplazamiento horizontal a 390 px en `/inicio`: 194 px de exceso**, 49 elementos fuera del lienzo | `scrollWidth 568` contra `clientWidth 375`. Causa: `lg:grid-cols-2` con tres hermanos `shrink-0` en `BloqueLista.vue:101-129`, usado por los cuatro `Espacio*.vue` | C |
| 12 | **El conmutador de perfil es inalcanzable a 390 px**: `left: -144.4`, y la cabecera no desplaza | medido | B |
| 13 | **32 objetivos táctiles por debajo de 44 px** a 390 px | medido | B y C |
| 14 | Detector estático **limpio**; **0 fallos WCAG AA** en las 8 combinaciones, mínimo real **4.54:1** | verificado, y comprobado que el `[]` no era un silencio falso | — |

**Falsos positivos descartados y por qué**: el contraste del botón `Buscar` deshabilitado (WCAG exime
los componentes inactivos); los 86 `tiny-text` (son un token declarado, `--text-micro: 11px`, no
dispersión); la medida de línea de ~200 ch (es siempre la franja de alcance, que no es prosa
continuada); el `cramped-padding` (los enlaces garantizan altura con `min-h-11`, no con relleno).

---

## Pendientes al abrir implementación

1. Confirmar que el árbol de US-ENTREGA-A4 sigue sin commitear y decidir si se commitea antes de abrir.
2. Escribir la prueba de fijación del tema de omisión **antes** de la primera línea de cada ola.
3. `layouts/portal.vue` todavía lee `--color-grid` para la retícula: debe leer `--color-reticula`.
4. Medir la lámina del logotipo para fijar la geometría del SVG en proporción, no en píxeles.
5. Pedir al equipo cuál de las dos marcas del archivo es la vigente. **Mientras tanto gana la guía.**
6. Decidir si el contrato de contraste gana un tercer nivel para componente y texto grande, que es lo
   que permitiría publicar el ámbar `B97812` sin oscurecerlo. **Fuera del alcance de esta US.**

---

## Verificación comprometida

Diez recorridos con el MCP de Playwright, detallados en §6.3 del plan. El que manda es **V5**: cero
desplazamiento horizontal a 390, 768, 1280 y 1440 en las diez rutas del contrato, porque hoy hay un
defecto medido y reproducible. **Se anotan aquí al ejecutarse.**

---

## Nube y schema

**No toca ninguno de los dos.** Ningún recurso de nube, ningún secreto, ninguna migración. La
preferencia de apariencia sigue viviendo en cookie.

---

## Registro de implementación — Ola A

**Cerrada el 15-ago-2026.** Barrera de entrada verde antes de la primera línea (35 passed) y verde al
cerrar (46 passed). El tema de omisión no movió un valor: las 15 capturas entregadas siguen
describiendo el producto.

### Archivos tocados

| Ruta | Qué |
|---|---|
| `design/sistema.py` | `Token` gana `icono`, `sobre` y `es_suelo`; grupos `BARRA_LATERAL` y `CERTIFICACION`; `PREFIJO_CERTIFICACION`; dos reglas nuevas en `REGLAS`; `tokens_de_color()` pasa de 21 a 28 |
| `design/contraste.py` | `FAMILIAS`; `Separacion` gana `familia`; `matriz` e `incumplimientos` miden cada token sobre `token.sobre` y exoneran los suelos; `peor_separacion(tema, modo, familia=None)` |
| `design/emitir.py` | `GRUPOS` única (alimenta CSS y TS); `_nota()`; icono en el CSS y en el módulo tipado; `ESTADOS_CERTIFICACION`; separaciones partidas por familia; `PEOR_SEPARACION_CERTIFICACION` |
| `tests/ml/test_contraste_temas.py` | `FIJACION_CHASIS` (7 pares), octeto del archivo, y cinco pruebas nuevas |
| `tests/ml/test_emision_temas.py` | El icono llega al módulo tipado por sus dos vías |
| `frontend/app/assets/css/main.css` | **GENERADO** por `make tokens` |
| `frontend/app/utils/tokens.generated.ts` | **GENERADO** por `make tokens` |

`docs/entregables/estilo/a4_tokens.tex` **no cambió**: sale de `uxdoc.sty` por `generar_tokens_a4.py`
y esa cadena no lee `design/sistema.py`. `make tokens` lo reescribe idéntico.

### Decisiones

1. **Un estado de certificación no tiene color propio: toma prestado un canal entero.** `_estado()`
   construye el token desde el token semántico (`ok`, `aviso`, `error`), así que «tres estados, tres
   canales» es estructural y no una coincidencia de tres hex que hoy difieren. Efecto lateral
   buscado: las tres distancias de la familia son un subconjunto de las seis semánticas, por eso el
   piso publicado no se movió.
2. **El icono viaja con el color.** `Token.icono` y `ESTADOS_CERTIFICACION` existen para que nadie
   vuelva a elegir la forma en el componente. Los tres son de la colección que ya empaqueta la app:
   `lucide:circle-check`, `lucide:clock` y `lucide:circle-slash` (verificados contra
   `@iconify-json/lucide`).
3. **`Token.sobre`: un color se mide sobre lo que se lee encima, no sobre el suelo de la página.**
   Sin esto la barra lateral institucional era imposible: su etiqueta clara sobre navy da 1.3:1
   contra el suelo blanco y `incumplimientos()` la habría rechazado midiendo algo que el lector no
   ve nunca. Las etiquetas de la barra declaran `sobre="barra-lateral"`; todo lo demás sigue
   midiéndose sobre `ground` y **ninguna razón previa cambió**.
4. **`Token.es_suelo`: un suelo nunca es un frente.** Generaliza la excepción que `ground-alt` tenía
   escrita a mano. La barra navy alcanza 14.64:1 sobre el blanco y eso es una superficie haciendo su
   trabajo, no una marca que informa.
5. **Bajo el tema de omisión el activo NO es un bloque relleno.** `barra-lateral-activo` se pinta del
   propio suelo de la barra: el módulo en curso se distingue por luminancia y peso, que es lo que
   muestran las capturas entregadas. Mismo truco que ya usaba `reticula`, y por la misma razón:
   `transparent` no es un color y la maquinaria de contraste se atragantaría con él.
6. **Las separaciones se emiten partidas por familia.** `SEPARACIONES_POR_TEMA` sigue siendo la de
   las cuatro marcas semánticas —seis parejas, que es lo que publica el informe— y la familia de
   certificación viaja en `SEPARACIONES_CERTIFICACION_POR_TEMA`. En Python `separaciones()` devuelve
   las dos, cada entrada con su `familia`. Consecuencia deliberada: **cero suites del frontend en
   rojo**; `sistemaDeDiseno.spec.ts` sigue esperando `C(4,2) = 6`.
7. **Una sola lista de grupos en el emisor** (`GRUPOS`). Dos listas habrían derivado el día que se
   añade un grupo, y la deriva sería silenciosa: la hoja declararía una propiedad que el módulo
   tipado no menciona.

### Nombres de variable CSS que emite esta ola

Estos siete son nuevos. **Son los únicos nombres que las olas B, C y D deben usar**; no hay más y no
hay sinónimos.

```
--color-barra-lateral               suelo de la barra lateral
--color-barra-lateral-activo        bloque del módulo en curso
--color-barra-lateral-texto         etiqueta en reposo (se lee SOBRE la barra)
--color-barra-lateral-activo-texto  etiqueta del módulo en curso (SOBRE su bloque)
--color-certificacion-certificado   canal ok    · icono lucide:circle-check
--color-certificacion-en-revision   canal aviso · icono lucide:clock
--color-certificacion-obsoleto      canal error · icono lucide:circle-slash
```

Utilidades de Tailwind correspondientes: `bg-barra-lateral`, `bg-barra-lateral-activo`,
`text-barra-lateral-texto`, `text-barra-lateral-activo-texto`,
`text-certificacion-{certificado,en-revision,obsoleto}` (y `bg-`, `border-`, `fill-` sobre los
mismos nombres). **`--color-reticula` ya existía y sigue igual**: bajo el institucional se pinta de
su propio suelo, comprobado ahora por prueba en los dos modos. Sigue pendiente que
`layouts/portal.vue` lea `--color-reticula` en vez de `--color-grid` (ola B).

Del módulo generado `frontend/app/utils/tokens.generated.ts`, exportaciones nuevas:

```
BARRA_LATERAL                        readonly TokenColor[]
CERTIFICACION                        readonly TokenColor[]
ESTADOS_CERTIFICACION                readonly EstadoCertificacion[]   <- lo que consume la ola D
SEPARACIONES_CERTIFICACION_POR_TEMA  readonly SeparacionSemantica[]
PEOR_SEPARACION_CERTIFICACION        { tema: { modo: number } }
```

`EstadoCertificacion` es `{ codigo, token, icono, clase }` con `codigo` en
`'certificado' | 'en-revision' | 'obsoleto'` y `clase` ya formada (`text-certificacion-*`). Campos
añadidos a tipos existentes: `TokenColor.icono?`, `ParContraste.fondo` (el token sobre el que se
midió) y `SeparacionSemantica.familia`.

### Qué quedó desactualizado de `tests/AGENTS.md`

- **'Estado' dice «`tests/ml/` (7 modulos)» y hoy son 9.** La cuenta ya estaba corta antes de esta
  ola: la enumeración —generadores, contratos de columna, anomalías, agregados, manifiesto, semillas
  y seed del catálogo— nunca mencionó `test_contraste_temas.py` ni `test_emision_temas.py`, que son
  los dos módulos del sistema de diseño y los únicos que **no** hablan de silos sintéticos.
- Esos dos módulos merecen su propia frase en el 'Estado', porque su trampa es distinta a la del
  resto: **fijan el tema de omisión byte a byte** y corren *antes* de cada ola de esta US. El total
  de 38 archivos versionados y 33 módulos de prueba no cambia: esta ola no creó archivos.
- Nada más quedó desactualizado. `tests/entregables/` sigue fuera de `make test` y con `--no-cov`, y
  ninguna prueba nueva toca PostgreSQL, SSE ni auth.

### Cifras medidas después del cambio

**Tokens de color: 28** (eran 21; +4 de chasis, +3 de certificación).

| Tema · modo | Incumplimientos | Peor separación (paleta) | Peor separación (certificación) |
|---|---|---|---|
| corriente · claro | **0** | **13.6** | 16.7 |
| corriente · oscuro | **0** | **21.5** | 21.5 |
| institucional · claro | **0** | **14.5** | 14.5 |
| institucional · oscuro | **0** | **22.6** | 22.6 |

Las cuatro cifras de la columna «paleta» son **idénticas a las de antes de la ola**: la familia de
certificación toma prestados los canales semánticos, así que sus tres distancias ya estaban dentro
de las seis medidas. Piso exigido: 13.6 en claro y 21.5 en oscuro; **ninguna de las ocho baja de él**
(CA-4, CA-5 y CA-11 verdes).

Razones de los tokens nuevos, cada una sobre lo que de verdad se lee encima:

| Token | corr. claro | corr. oscuro | inst. claro | inst. oscuro |
|---|---|---|---|---|
| `barra-lateral` sobre el suelo | 1.08 superficie | 1.08 superficie | 14.64 superficie | 1.19 superficie |
| `barra-lateral-activo` sobre el suelo | 1.08 superficie | 1.08 superficie | 6.27 superficie | 6.90 superficie |
| `barra-lateral-texto` **sobre la barra** | 4.69 AA | 4.95 AA | 9.30 AAA | 9.30 AAA |
| `barra-lateral-activo-texto` **sobre el bloque** | 15.41 AAA | 16.38 AAA | 6.27 AA | 6.90 AA |
| `certificacion-certificado` | 5.68 AA | 11.35 AAA | 5.23 AA | 8.67 AAA |
| `certificacion-en-revision` | 4.71 AA | 12.26 AAA | 4.54 AA | 8.07 AAA |
| `certificacion-obsoleto` | 8.42 AAA | 6.37 AA | 7.46 AAA | 5.13 AA |

Ningún valor por debajo de 4.5:1 en texto. El mínimo real de la matriz sigue siendo **4.54:1**
(`certificacion-en-revision` bajo el institucional claro, que es `aviso` y ya estaba medido ahí).

### Puerta ejecutada

`make tokens` · `pytest tests/ml -q --no-cov` → **103 passed** · `ruff check --config
backend/pyproject.toml design tests/ml` y `ruff format --check` limpios · `mypy --config-file
backend/pyproject.toml design tests/ml` → **Success**. Comprobado además que las cinco suites del
frontend que leen `main.css` o `tokens.generated.ts` siguen en verde
(`sistemaDeDiseno`, `paletaSeries`, `superficie`, `modoYSistema`, `contratos`: 36 pruebas).

**Para las olas B, C y D**: `design/` está cerrado por esta ola. Si falta un token, **no se inventa
un valor en el componente**: se pide aquí y se regenera con `make tokens`.

---

## Registro de implementación — Ola C

**Cerrada el 15-ago-2026.** `pnpm lint` limpio, `pnpm typecheck` limpio y **1 020 pruebas en verde
sobre 52 archivos** (barrido completo sin `--coverage`, porque la ola B escribía a la vez y
`coverage/` se pisa). Las 14 suites del alcance de esta ola suman **232 pruebas**, todas verdes.

### Archivos tocados

| Ruta | C/M | Qué |
|---|---|---|
| `frontend/app/components/comun/TarjetaContenida.vue` | **C** | Superficie contenida: filete, radio por tema y barra de canal |
| `frontend/app/components/comun/TablaDatos.vue` | **C** | Tabla con TanStack v9: orden real, `aria-sort`, fila de 34 px |
| `frontend/app/utils/tablaDatos.ts` | **C** | Registro único de características de TanStack, `MetaColumna`, `ColumnaDatos<T>` y `definirColumnas()` |
| `frontend/app/types/superficie.ts` | **C** | `CanalTarjeta` |
| `frontend/app/components/administracion/TablaUsuarios.vue` | M | Migra a `TablaDatos` por la ranura `fila`; el filtro sube a `min-h-11` |
| `frontend/app/components/tablero/TablaDetalleSerie.vue` | M | Migra a `TablaDatos` por la vía de columnas; ordena por la cifra cruda |
| `frontend/app/components/serie/Tabla.vue` | M | Migra a `TablaDatos` por la ranura `fila`; conserva props y emit |
| `frontend/app/components/inicio/BloqueLista.vue` | M | **Arreglo del desborde**; enlace a objetivo táctil de 44 px |
| `frontend/app/components/inicio/TarjetaIndicador.vue` | M | Firma del plan, cifra en monoespaciada, monta `TarjetaContenida` |
| `frontend/app/components/inicio/EspacioDirectivo.vue` | M | Cuatro tarjetas, rejilla 1/2/4, formateo en la composición |
| `frontend/app/components/inicio/EspacioOperativo.vue` | M | `min-w-0` en el bloque de perfil y en sus filas |
| `frontend/app/components/inicio/EspacioAnalista.vue` | M | Enlace del explorador a 44 px |
| `frontend/app/components/inicio/BuscadorUnificado.vue` | M | `min-w-0` en la raíz |
| `frontend/app/utils/muestrasInicio.ts` | M | Cuarto indicador (**fuera del write-set literal**, ver decisión 7) |
| `frontend/test/tablaDatos.spec.ts` | **C** | 14 pruebas: anuncio, orden real, geometría, vacío y ranura de fila |
| `frontend/test/superficie.spec.ts` | M | Cinco pruebas nuevas de `TarjetaContenida` (CA-16) |
| `frontend/test/inicio.spec.ts` y `espaciosTrabajo.spec.ts` | M | Piso de cuatro tarjetas y su contenido (CA-17) |

`frontend/app/components/inicio/CabeceraEspacio.vue` estaba en el write-set y **no se tocó**: no
desborda, no tiene controles y su copia es de la ola D.

### Decisiones

1. **`TablaDatos` tiene dos cuerpos, y los dos tienen consumidor real.** Por omisión las celdas
   salen de las definiciones de columna con `FlexRender` —así lo usa `TablaDetalleSerie`—; quien
   tiene una fila que es un componente propio la pasa por la ranura `fila` y conserva encabezado,
   orden y geometría —así lo usan `TablaUsuarios`, cuya fila lleva selector de rol y zona
   destructiva, y `serie/Tabla`, cuyo encabezado de fila es un botón que emite—. Ninguna de las dos
   vías es andamiaje: si solo hubiera una, la otra sería código muerto y no se habría escrito.
2. **El orden se computa sobre el valor crudo, nunca sobre el texto impreso.** Las cifras llegan a
   estas tablas ya formateadas, y un orden sobre `1 284,5` contra `987,6` es alfabético disfrazado
   de numérico. `TablaDetalleSerie` guarda `valorCrudo` y `cambioCrudo` junto al texto;
   `TablaUsuarios` ordena el estado por el booleano y la fecha por el instante ISO.
3. **`serie/Tabla` solo ordena su primera columna, y solo cuando las filas son series.** Sus celdas
   numéricas llegan como cadenas desde `serie/Panel.vue`, que **no está en este write-set**:
   ordenarlas exigiría que el panel entregue también los valores crudos. Cuando las filas son puntos
   de una sola línea el encabezado es una fecha formateada y **no ordena nada**, porque una fecha
   ordenada como texto es la misma mentira en otra columna. Queda anotado como trabajo de quien
   pueda tocar `Panel.vue`.
4. **`aria-sort` solo aparece donde se puede ordenar.** Una columna de botones con `aria-sort="none"`
   le anuncia al lector una capacidad que no existe. La columna de acciones de `/administracion` y
   las columnas de cifras de `serie/Tabla` no lo declaran.
5. **La primera pulsación de una columna de cifras abre por el valor más alto.** Es el sentido que
   TanStack infiere del tipo de dato (`sortDescFirst`), y se conserva a propósito: en analítica «lo
   más grande primero» es lo que el lector espera. Lo que sí se comprueba es que el anuncio diga lo
   que la tabla hizo —`descending` en cifras, `ascending` en texto—, porque el único caso en que la
   palabra y el orden podrían discrepar es el del lector que no ve la flecha.
6. **La tabla no cambia el orden que recibe.** `ordenInicial` ausente significa el orden del
   transporte. De eso depende `/administracion`: una cuenta recién creada está donde la puso la API,
   y un orden de omisión la habría movido en silencio.
7. **El cuarto indicador reutiliza una clave que ya existe.** CA-17 pide al menos cuatro tarjetas y
   `INDICADORES` servía tres. La cuarta —días de mora, unidad `dias`, que estaba declarada en el
   sistema y sin usar— toma `workspace.samples.recent.mora`, que es el nombre que el catálogo ya
   publica para ese concepto. La alternativa era una clave nueva que esta ola no puede escribir, y
   hasta que la ola D la añadiera `inicio.spec.ts` habría impreso la ruta de la clave como texto y
   estaría en rojo. El archivo `muestrasInicio.ts` **no estaba en el write-set literal**; se tocó
   porque la tarjeta de indicador de `/inicio` es el encargo de esta ola y ninguna otra escribe ahí.
8. **Las cuatro tarjetas llevan el canal `accion` y no un canal por signo.** La subida de la
   cobertura de liquidez es buena noticia y la subida de la cartera vencida es mala: pintar las dos
   de verde sería la tarjeta emitiendo un juicio que no puede emitir, y el propio componente lo
   tenía escrito desde US-027. La barra es identidad del tema —corriente plena bajo el de omisión,
   verde azulado bajo el institucional— y no estado.
9. **El radio del tema viaja en la clase y no en el store.** `data-tema` vive en la raíz del
   documento, así que `[[data-tema=institucional]_&]:rounded-lg` compila a
   `[data-tema=institucional] .clase` y resuelve sin que cada tarjeta se suscriba a un valor que
   solo necesita para elegir un radio. Verificado compilando el fragmento con el propio Tailwind
   4.3.3 del proyecto. `superficie.spec.ts` lee el nombre del atributo **de la hoja generada** y lo
   compara con el de la clase: escribirlo con el nombre que el modo tenía antes daría una regla que
   nunca casa y una tarjeta cuadrada bajo el institucional, sin nada roto que mirar.
10. **La fila de 34 px y el objetivo táctil de 44 px son incompatibles dentro de una tabla densa, y
    el sistema ya lo había resuelto.** `main.css` sube a 44 px todo control bajo
    `@media (pointer: coarse)`. Por eso el botón de arrastre de `serie/Tabla` deja de llevar
    `min-h-11` y pasa a llenar su celda (`h-full w-full`): con puntero fino el objetivo es la celda
    entera de 34 px, que es **más área** que el botón del tamaño del texto que había, y con dedo la
    regla del sistema lo levanta a 44. Fuera de las tablas sí se subieron a 44 px.

### Claves i18n que esta ola necesita

**Ninguna es bloqueante: la ola C no dejó ni una cadena sin resolver.** Estas dos son deseables y se
anotan para quien integre.

| Clave | es | en | Por qué |
|---|---|---|---|
| `workspace.samples.indicator.diasMora` | `Días de mora` | `Days past due` | Hoy la cuarta tarjeta usa `workspace.samples.recent.mora`, que dice exactamente eso pero está archivada bajo «búsquedas recientes». Si se añade, basta cambiar `claveEtiqueta` del indicador `diasMora` en `app/utils/muestrasInicio.ts` |
| `dashboard.table.empty` | `Ninguna serie coincide con la selección.` | `No series match the current selection.` | `TablaDatos` implementa el estado vacío y `serie/Tabla` no puede pasárselo sin una frase. Ver la limitación de abajo |

### Tokens que faltan en `design/`

`design/` está cerrado por la ola A y **no se inventó ningún hex**. Lo que no existe y se resolvió
con lo que hay:

- **No hay token de geometría por tema.** El emisor publica color y tipografía por tema, pero
  `--radius-*`, `--table-row-height` y `--panel-padding` viven en el bloque `@theme` único. §2.2 del
  plan pide «filete sin radio» bajo el de omisión y «filete más radio» bajo el institucional, y eso
  **no lo resuelve hoy ningún token**: lo resuelve la variante de Tailwind de la decisión 9. Un
  `--radius-tarjeta` por tema dejaría el componente sin condición alguna. Se pide para una ola
  futura, no para ésta.
- **No hay token de ancho de la barra de canal.** Se usa `w-1`, que es `--spacing` por 1, 4 px.

### Tablas que quedan sin migrar

Cuatro de las siete, y ninguna por descuido:

| Componente | Por qué |
|---|---|
| `app/components/guia/LaminaTablas.vue` | `guia/` es de otra ola. **Ya anuncia su orden**: es la lámina normativa de la que sale el aspecto de `TablaDatos` (`data-ordenar`, `aria-sort`, `h-(--table-row-height)`), y `laminas.spec.ts` lo comprueba |
| `app/components/guia/LaminaBotones.vue` | `guia/`. Es una matriz de estados de botón, no una tabla de datos: no tiene filas que ordenar |
| `app/pages/guia.vue` | `pages/` es de otra ola |
| `app/components/chat/ToolCallCard.vue` | Fuera del alcance declarado. Es el resultado de una llamada a herramienta, y migrarla toca el contrato `data-prueba="tabla-resultado"` que fija `toolCallCard.spec.ts` |

Consumidores de `TablaDatos` hoy: `administracion/TablaUsuarios.vue`, `serie/Tabla.vue` y
`tablero/TablaDetalleSerie.vue`.

### El desborde horizontal, medido antes y después

**Causa confirmada, y no era solo la que el `shrink-0` sugería.** Los tres hermanos `shrink-0` de
`BloqueLista` son la mitad de la historia; la otra mitad es que **una pista de rejilla no baja del
tamaño min-content de lo que contiene**, porque el elemento de rejilla conserva `min-width: auto`.
Con `truncate` —que es `white-space: nowrap`— el min-content de la etiqueta es la frase entera, así
que la pista se ensanchaba hasta salirse del lienzo. `overflow-hidden` en el padre habría escondido
el síntoma; `min-w-0` en el bloque, en la fila y en el elemento de rejilla lo corrige en origen.

Medición con Chromium sin cabeza sobre el **marcado real** de las tres composiciones —renderizado
por Vue Test Utils— y la **hoja real** compilada desde `app/assets/css/main.css` con el Tailwind
4.3.3 del proyecto. La fase «antes» es el mismo marcado con las clases que esta ola añadió
retiradas, así que las dos corridas difieren en exactamente el arreglo.

| Composición | Ancho | Antes: `scrollWidth` / `clientWidth` | Elementos fuera | Después |
|---|---|---|---|---|
| operativo | **390** | **551 / 390, exceso 161** | **45** | **390 / 390, exceso 0**, 0 fuera |
| operativo | 768 · 1280 · 1440 | 0 | 0 | 0 |
| analista | **390** | **551 / 390, exceso 161** | **45** | **390 / 390, exceso 0**, 0 fuera |
| analista | 768 · 1280 · 1440 | 0 | 0 | 0 |
| directivo | **390** | **551 / 390, exceso 161** | **23** | **390 / 390, exceso 0**, 0 fuera |
| directivo | 768 · 1280 · 1440 | 0 | 0 | 0 |

Repetido con `data-tema="institucional"` después del arreglo: **exceso 0 en las tres composiciones y
en los cuatro anchos**.

**Lo que esta medición NO es.** El lienzo es `<main style="padding:16px">` y no el contenedor real,
porque el chasis lo estaba reescribiendo la ola B mientras esto corría; y las tipografías del
sistema no están instaladas en el Chromium sin cabeza, así que las anchuras absolutas no son las del
navegador del lector. Por eso las cifras «antes» dan 161 px de exceso y la evaluación midió 194: es
el mismo defecto medido con otra fuente y otro contenedor. **El recorrido V5 sobre las diez rutas
sigue pendiente** y le toca a QA, con el chasis de la ola B ya integrado.

### Objetivos táctiles, medidos antes y después

Mismo banco, a 390 px, contando todo `a, button, input, select, summary, [role=button]` con alto o
ancho por debajo de 44 px:

| Composición | Antes | Después |
|---|---|---|
| operativo | 13 | **0** |
| analista | 17 | **0** |
| directivo | 13 | **0** |

Los enlaces de lista medían 43 px y no 44: la fila reserva `min-h-11`, pero su filete se come un
píxel y el ancla estirada heredaba 43. Por eso el enlace lleva `self-stretch` **y** `min-h-11`. Los
32 objetivos que midió la evaluación incluyen el cromo, que es de la ola B.

### Pruebas rojas dejadas sin tocar

**Ninguna.** Al cerrar esta ola el barrido completo daba 52 archivos y 1 020 pruebas en verde, y
`pnpm lint` limpio. Durante la implementación hubo un error de ESLint en `app/layouts/portal.vue`
(`vue/no-multiple-template-root`, un comentario en la raíz de la plantilla) que **no se tocó por ser
de la ola B**; la ola B lo corrigió antes de este cierre.

### Qué quedó desactualizado del 'Estado' de `frontend/AGENTS.md`

Para el orquestador, que es quien escribe esa guía:

- **La estructura ya no es la que describe.** `app/types/` gana `superficie.ts` y `app/utils/` gana
  `tablaDatos.ts`. El apartado de `utils/` dice «puros + `permisos.generated.ts` +
  `tokens.generated.ts`» y ahora también aloja el **registro de características de TanStack**, que
  es una constante de módulo y no una función pura: vive ahí porque tiene que crearse **una sola
  vez** —el adaptador de Vue vigila las opciones que recibe y un registro reconstruido en cada
  `setup` reconstruiría la tabla con él—.
- **`@tanstack/vue-table@9.1.2` entra al stack y no está en 'Decisiones irrevocables'.** Es la
  **v9**, no la v8: `useTable` en lugar de `useVueTable`, características declaradas explícitamente
  con `tableFeatures({...})`, modelos de fila como ranuras de ese registro y estado sobre átomos. Un
  ejemplo de v8 copiado de internet no compila. El paquete trae sus propias *skills* en
  `node_modules/@tanstack/vue-table/skills/`, que es la fuente que se usó.
- **'Convenciones' merece una línea nueva**: *el orden de una tabla se computa sobre el valor crudo,
  nunca sobre el texto impreso*. Es la trampa que esta ola encontró tres veces seguidas.
- **La cuenta de pruebas cambió.** Decía «45 `*.spec.ts`»; hoy son **52** archivos y 1 020 pruebas
  contando lo que añadieron las olas B y C. `tablaDatos.spec.ts` es nuevo de esta ola.
- **La nota sobre la medida de lectura necesita una hermana.** La guía explica por qué un `<p>` a
  todo el ancho se sale con `max-w-none`; el defecto simétrico —y el que costó 161 px— es que **un
  elemento de rejilla conserva `min-width: auto` y no baja de su tamaño min-content**, así que
  cualquier bloque dentro de un `grid-cols-*` que contenga texto `truncate` necesita `min-w-0`.
- **`app/components/` ya no son «catorce familias» sin más**: `comun/` pasa a alojar las dos piezas
  compartidas de superficie y tabla, que antes no existían.


---

## Registro de implementación — Ola B

**Cerrada el 15-ago-2026.** Suite del frontend completa en verde al cerrar: **52 archivos, 1 020
pruebas**, sin `--coverage` porque la ola C escribía a la vez y `coverage/` se pisa. `pnpm lint` y
`pnpm typecheck` limpios (exit 0 leído directo, no por tubería).

### Archivos tocados

| Ruta | Qué |
|---|---|
| `frontend/app/components/comun/MarcaKarisma.vue` | **Creado.** Símbolo K en teja, SVG en línea, tres variantes, reglas de área de protección y tamaño mínimo |
| `frontend/app/components/comun/SelectorApariencia.vue` | **Creado.** Funde tema y modo: un disparador con rótulo visible y un panel con las 2+3 opciones |
| `frontend/app/components/comun/SelectorTema.vue` · `SelectorModo.vue` | **Borrados.** Los absorbe el de apariencia |
| `frontend/app/components/comun/CabeceraProducto.vue` | Cinco ranuras, seis controles en reposo, buscador real, marca vectorial, paneles anclados al borde final |
| `frontend/app/components/nav/BarraLateral.vue` | Tokens de chasis de la ola A; se retiran las nueve etiquetas inertes y la marca duplicada |
| `frontend/app/layouts/portal.vue` | `--color-grid` → `--color-reticula`; la cabecera vuelve a llevar marca |
| `frontend/app/layouts/default.vue` · `acceso.vue` | Mismo chasis: retícula, salto al contenido, `main#contenido`; sin navegación |
| `frontend/i18n/locales/{es,en}.json` | 7 claves nuevas, solo de cromo (abajo) |
| `frontend/test/marca.spec.ts` · `chasis.spec.ts` · `apariencia.spec.ts` | **Creados** |
| `frontend/test/cabeceraProducto.spec.ts` | Reescrito: mide la fila, no la lista de conmutadores de ayer |
| `frontend/test/BarraLateral.spec.ts` | Facetas fuera; entran superficie por tokens y «cero `listitem` sin enlace» |
| `frontend/test/tema.spec.ts` | Pierde el bloque del selector, que se muda a `apariencia.spec.ts`; conserva cookie y primer render |

### La geometría medida del logotipo, y de qué página salió

**Fuente**: `docs/entregables/figma/Karisma Data - Actividad 4_1.pdf`, **página 1**, sección
**«Uso del logotipo»**. Es el único de los tres PDF que trae la página normativa. Medición con
`pdftoppm -r 600` sobre la teja «Principal», y comprobación de las otras dos con el mismo método;
la página mide 1440 pt de ancho, así que 600 dpi equivale a un factor 8.3333 sobre el píxel de
diseño.

La teja mide **931 × 933 px** a 600 dpi (**112 px de diseño**, cuadrada). Todo lo demás va en
porcentaje de ese lado, que es como entra al `viewBox="0 0 100 100"`:

| Elemento | Medido a 600 dpi | Proporción | En el componente |
|---|---|---|---|
| Radio de la teja | 56 | 6.01 % | `RADIO_TEJA` |
| Radio de barra | 23 (ámbar 19) | 2.47 % | `RADIO_BARRA` |
| Ancho de columna | 131 | 14.06 % | las tres iguales |
| Canal entre columnas | 69 | 7.40 % | derivado, idéntico en los dos huecos |
| Columnas (x) | 166 · 366 · 566 | 17.81 · 39.27 · 60.73 % | `asta`, `brazo-alto`, `brazo-corto` |
| Borde superior de las tres | 183 | 19.64 % | uno solo |
| Alturas | 566 · 366 · 216 | 60.73 · 39.27 · 23.18 % | descendentes |
| Barra ámbar | 333 × 132 en (366, 617) | x 39.27 · y 66.21 · 35.52 × 14.16 % | `base` |

Dos cifras de la barra ámbar **no** son la medición cruda: su borde derecho y su línea de base
salían **2 px** (a 600 dpi) de los de la tercera columna y del asta. Eso es el antialias del
render, no una decisión, así que se igualaron — de ahí `ancho: 35.52` en vez de 35.73 y
`y: 66.21` en vez de 66.20 —. El margen vertical queda simétrico: 19.64 arriba y 19.63 abajo.

**Colores medidos, con su fila de la paleta del mismo archivo**:

| Variante | Teja | Barras claras | Barra de base |
|---|---|---|---|
| Principal | `#086B70` (Acción) | `#FFFFFF` (Superficie) | `#B97812` (Atención) |
| Inverso | `#086B70` | `#FFFFFF` | `#B97812` |
| Monocromático | `#102A43` (Navegación) | `#FFFFFF` | `#FFFFFF` |

**Principal e Inverso son el mismo dibujo.** Se midieron las tres tejas por separado y los
histogramas coinciden: lo que cambia en la lámina es el fondo de la tarjeta (navy `#102A43`), no el
relleno. Para que la prop no fuera decorativa, la variante gobierna además **el color del nombre**
en la marca completa: `currentColor` en principal — hereda la tinta de quien la monta —, blanco en
inverso — que es como el archivo la compone sobre navy — y navy en monocromático.

**Reglas de la misma página, transcritas** (verificadas a 300 dpi porque a baja resolución la
fracción se leía «16»): *«Área de protección: reserva alrededor del símbolo un espacio libre mínimo
equivalente a **½K**»*, *«Tamaño mínimo: símbolo digital **32 px**; marca completa **120 px de
ancho**»*, *«Usos incorrectos: no deformar, rotar, recolorear, separar elementos ni añadir
efectos»*. Las tres están implementadas: `size-8` (32 px y piso a la vez), `pe-4` (16 px = ½ de 32)
y `min-w-30` (120 px) cuando lleva nombre.

**Para la ola E (`a4_08`, riesgo R6)**: la discrepancia se confirma. La página normativa de
`Actividad 4_1.pdf` declara la teja teal con la K; las maquetas usan otra marca. **Ganó la guía.**
La captura del portal debe compararse contra esa página 1, no contra las maquetas.

### Decisiones

1. **El logotipo se dibuja con hex literales y no con tokens.** Es la única excepción de la ola y
   está razonada en el propio componente: `--color-accion` es teal solo bajo el institucional y
   tinta bajo el de omisión, así que pintar la teja con el token **repintaría la marca al cambiar
   de tema**, que es exactamente lo que la guía prohíbe. `marca.spec.ts` fija esto al revés: falla
   si el marcado llega a contener `var(--color-`. **Petición a `design/`**: hace falta un grupo
   `marca-*` invariante al tema (`marca-teja`, `marca-tinta`, `marca-acento`, `marca-claro`) para
   que estos cuatro valores dejen de vivir en un componente. Mientras no exista, viven ahí.
2. **De 11 controles a 6, contados con la puerta de demostración abierta.** El reparto en reposo
   es: marca 1, buscador 1, apariencia 1, perfil 1, idioma 2. Los dos grupos que derramaban sus
   opciones en la fila — tema+modo, 5 botones; perfil, 4 — son revelaciones ahora. `SelectorRol` no
   se tocó: se monta **dentro** del panel de perfil, así que la puerta sigue siendo una sola y
   sigue acuñando sesión real contra `POST /api/auth/demo`.
3. **Los paneles se anclan a `end-0` sobre su propio disparador.** Es el defecto medido escrito
   como regla: `left: -144.4` en 390 px con una barra que no desplaza. `cabeceraProducto.spec.ts`
   falla si aparece cualquier clase `start-*` o `left-*` en un panel.
4. **La cabecera envuelve (`flex-wrap`).** Una barra fina que se niega a envolver o desborda el
   lienzo o expulsa un control; las dos cosas están medidas. En estrecho el buscador se lleva una
   línea propia (`order-last w-full`) y no se pierde nada.
5. **El buscador del cromo navega a `/exploracion?q=<término>` y se siembra desde la URL.** La ruta
   sale del contrato (`MODULOS`), nunca de un literal. **Que `/exploracion` aplique el término es la
   ola D (CA-13)**: si esa ola se congela, el control sigue siendo completo — lleva al catálogo y el
   término sobrevive visible en la dirección y en el campo —, pero el resultado no viene filtrado.
   Está probado en los dos sentidos, incluido el campo vacío.
6. **Un solo chasis, y `default`/`acceso` lo heredan entero menos la navegación.** Ganan retícula,
   salto al contenido y `main#contenido`. `FranjaAlcance.spec.ts` sigue exigiendo cero `nav` en esas
   dos y **no se tocó**: «mismo chasis» no es «misma navegación».
7. **La marca se monta una vez por pantalla, y es la cabecera.** La barra lateral la repetía, así
   que el portal nombraba el producto dos veces y las dos pantallas sin barra una. Se retiró
   `conMarca` de `CabeceraProducto`: ya no había ningún chasis que quisiera la cabecera sin marca.
8. **El nombre de la marca aparece desde 768 px.** No es un capricho de maquetación: es la regla de
   tamaño mínimo del archivo. Por debajo de ese ancho la marca completa no alcanza sus 120 px, y la
   lámina manda usar el símbolo solo. Ojo con los breakpoints de este sistema, que **no son los de
   Tailwind**: `sm` = 768 px y `md` = 1024 px, declarados en el `@theme`.
9. **Las etiquetas de la barra siguen apareciendo en `md` (1024 px).** Es lo que declara el propio
   sistema — `--breakpoint-sm: 768px` dice «se colapsa a franja de iconos» y `--breakpoint-md` dice
   «vuelve con etiqueta» —, y los dos viewports de prototipado de la lámina son 1440 y 1024. No se
   inventó un chasis móvil nuevo; la franja de iconos es la que ya estaba.
10. **`CLAVES_FACETAS_TRANSVERSALES` sigue exportada.** `app/utils/navegacion.ts` está fuera de mi
    write-set, así que se retiró **el renderizado**, no la constante. Hoy no la consume ningún
    componente: solo `navegacion.spec.ts`, que la mide como contrato del mapa de A3. Sus claves
    i18n (`nav.facets.caption`, `nav.facets.hint`, `nav.facets.items.*`) quedan **huérfanas en el
    catálogo**; retirarlas es de quien toque `navegacion.ts`. `nav.facets.branchTitle` y
    `branchAria` **siguen en uso**, en las hojas del segundo nivel.

### Claves i18n añadidas

Siete, todas de cromo y de navegación, que es la concesión de esta ola. Ninguna reescribe copia de
producto: eso es de la ola D.

```
appearance.label            Apariencia                   / Appearance
appearance.current          Apariencia: {theme}, {mode}  / Appearance: {theme}, {mode}
chrome.search.label         Buscar en el catálogo        / Search the catalogue
chrome.search.placeholder   Campo, fuente o tablero      / Field, source or dashboard
chrome.profile.label        Perfil de demostración       / Demonstration profile
chrome.profile.current      Perfil: {profile}            / Profile: {profile}
chrome.profile.signedOut    Sin sesión                   / Signed out
```

`appearance` se colocó junto a `theme`, y las dos de `chrome` dentro de su objeto. El resto del
catálogo salió byte a byte igual: antes de escribir se comprobó que el volcado de
`json.dumps(indent=2)` reproduce el archivo original, así que el diff son **13 líneas de alta en
cada idioma y nada más**. `idioma.spec.ts` sigue verde: ninguna de las siete coincide entre los dos
idiomas.

### Tokens consumidos, y el que faltó

Los siete de la ola A, sin sinónimos: `bg-barra-lateral`, `bg-barra-lateral-activo`,
`text-barra-lateral-texto` y `text-barra-lateral-activo-texto` (los dos activos con
`aria-[current=page]:` delante), más `--color-reticula` en los tres layouts. Los tres de
certificación **no** los toca esta ola: son de la D. Para el filete del segundo nivel se usó
`barra-lateral-texto/40`, modificador de opacidad sobre un token declarado, porque no hay un token
de regla que se lea sobre la barra.

**Lo que faltó y no se inventó**: los cuatro valores de marca (decisión 1).

### Pruebas rojas de otra ola

**Ninguna.** Al cerrar, las 52 suites pasan juntas, incluidas las que la ola C tenía en vuelo
(`superficie`, `inicio`, `espaciosTrabajo`, `tablaDatos`). No hubo que dejar nada sin tocar por ser
ajeno, y tampoco hubo errores de tipos apuntando fuera del write-set.

### Lo que queda abierto, y de quién es

- **CA-8, CA-9 y CA-10 en navegador siguen sin verificar.** El conteo de controles y el ancla de los
  paneles están probados en el DOM, pero V3, V4 y V5 se miden con Playwright a 390, 768, 1280 y
  1440. Es trabajo de la verificación comprometida, no de esta ola.
- **Dos objetivos táctiles por debajo de 44 px siguen ahí**: los botones de `SelectorIdioma`
  (`px-2 py-0.5`), que está **fuera del write-set** de esta ola. Los controles propios de la
  cabecera declaran `min-h-11` y `cabeceraProducto.spec.ts` lo exige uno por uno, excluyendo
  explícitamente ese grupo. Quien pueda tocar ese archivo cierra los dos últimos.
- **`EstadoPendiente.vue` sigue en disco** y sin consumidores en `app/`. Esta ola no lo movió.

### Qué quedó desactualizado de `frontend/AGENTS.md`

Lo escribe el orquestador al integrar; aquí queda la lista.

- **'Estado', párrafo del sistema de diseño**: *«La cabecera monta cuatro conmutadores: rol, tema,
  modo e idioma»* ya no es cierto. Monta **cinco ranuras** — marca, buscador, apariencia, perfil,
  idioma — y **seis controles en reposo**. `SelectorTema.vue` y `SelectorModo.vue` **ya no existen**.
- **'Estado', primer párrafo**: dice *«Las nueve rutas del contrato»* y `RUTAS_CONTRATO` tiene
  **ocho**; el chasis se mide sobre **diez** (esas ocho más `/` y `/guia`), que es la cifra de CA-7 y
  la que fija `chasis.spec.ts`. La cuenta ya estaba mal antes de esta ola.
- **'Estructura'**: `comun/` gana `MarcaKarisma.vue` y `SelectorApariencia.vue` y pierde los dos
  selectores que se fundieron.
- **'Tests'**: dice **45 `*.spec.ts`** y hoy son **52** en disco (tres los añade esta ola: `marca`,
  `chasis`, `apariencia`; el resto son de la ola C). Los cuatro auxiliares no cambian.
- **'Convenciones'** merece una línea nueva: **la marca es la única excepción al «color desde los
  tokens»**, y está declarada en el propio componente con su razón. Sin esa línea, el siguiente
  lector la lee como un descuido.
- Nada más. El aviso de `data-modo`/`data-tema` sigue vigente, la prohibición de `routeRules` con
  `swr` también, y la nota de `max-w-none` en `FranjaAlcance` se cumple en los tres layouts.

---

## Registro de implementación — Ola D

**Cerrada el 15-ago-2026.** `pnpm lint` limpio, `pnpm typecheck` limpio y **1 049 pruebas en verde
sobre 53 archivos**, esta vez **con `--coverage`** porque ya no había nadie escribiendo a la vez:
**93.95 % de líneas** y 93.96 % de sentencias, sobre el 93.89 % con el que cerró la ola C. Umbral
declarado: 50 %.

### Archivos tocados

| Ruta | C/M | Qué |
|---|---|---|
| `frontend/app/components/exploracion/ResultadosCatalogo.vue` | M | La lista pasa a `TablaDatos`; la cabecera de fila es el botón que abre el linaje; salida a `/gobierno`; los tres estados de certificación; región viva en `listo` y en `vacio` |
| `frontend/app/components/exploracion/BuscadorCatalogo.vue` | M | Prop `termino` que siembra la caja desde la dirección; el botón `Buscar` pasa a ser la acción primaria de la pantalla |
| `frontend/app/components/exploracion/FiltroDominios.vue` | M | El dominio activo se pinta con `--color-seleccion` |
| `frontend/app/components/comun/SelectorIdioma.vue` | M | Los dos últimos objetivos táctiles del cromo suben a 44 × 44 (`size-11`) |
| `frontend/app/composables/useBusquedaCatalogo.ts` | M | `OpcionesBusqueda.sincronizarUrl`, `PARAMETRO_TERMINO`, `certificacionDeCampo()`; se retira `limpiar()` |
| `frontend/app/pages/exploracion/index.vue` | M | Sincroniza con la URL, monta el overlay de linaje y declara qué resuelve frente a `/gobierno` |
| `frontend/app/pages/acceso.vue` | M | Énfasis corregido: superficie de canal `accion` para los perfiles y revelación para las credenciales; el rechazo de la demostración se anuncia en la página |
| `frontend/app/pages/guia.vue` | M | Lámina nueva `chasis`: los cuatro tokens de barra lateral, los tres estados de certificación y la superficie contenida en sus cinco canales |
| `frontend/app/utils/muestrasInicio.ts` | M | Una línea: `claveEtiqueta` del indicador `diasMora` |
| `frontend/i18n/locales/{es,en}.json` | M | 22 claves nuevas o reescritas por idioma (abajo) |
| `frontend/test/certificacion.spec.ts` | **C** | 9 pruebas: los tres canales, el cruce de ortografía, la tabla y la lámina normativa |
| `frontend/test/exploracionCatalogo.spec.ts` | M | +9: fila → linaje, salida a gobierno, `aria-sort`, apertura en frío, término en la dirección, región viva |
| `frontend/test/contratos.spec.ts` | M | +5: barrido de numeración del mapa (CA-18) y divergencia de las dos pantallas (CA-20) |
| `frontend/test/acceso.spec.ts` | M | +5: orden, canal, revelación, puerta apagada y aviso fuera del formulario |
| `frontend/test/idioma.spec.ts` | M | +1: objetivo táctil de 44 px |

**Estaban en el write-set y NO se tocaron, cada uno con su razón**:
`components/exploracion/AccionesCatalogo.vue` (la zona de continuaciones ya separa lo alcanzable de
lo cerrado y su única deuda era de copia, que vive en i18n); `pages/{index,inicio,gobierno,asistente,
administracion}.vue` (el chasis se lo dio la ola B en los layouts y su copia es i18n: cambiarlas
habría sido movimiento sin defecto detrás); y las suites `accionesCatalogo`, `diccionarioCampos`,
`panelLinaje`, `pantallas`, `indice` y `smokeRutas`, que pasan sin retoques.

### Decisiones

1. **La cabecera de fila ES la puerta al linaje.** Una columna de acciones habría gastado una
   columna de una tabla densa en repetir el nombre del campo que el lector ya está señalando. El
   botón lleva `aria-label` con el nombre físico: veinte filas con el rótulo «Ver el linaje» dejan
   al lector de pantalla eligiendo entre veinte controles idénticos.
2. **El linaje se abre EN la pantalla, con el overlay de gobierno, y no navegando.** Mandar la fila
   a `/gobierno` habría exigido que esa pantalla aceptara un campo por la URL, y el estado de
   búsqueda vive dentro de `gobierno/DiccionarioCampos.vue`, que no es de esta ola. Montar el mismo
   `OverlayLinaje` y el mismo `useLinajeCampo` evita además la segunda respuesta a «de dónde sale
   esto», que es la que habría derivado.
3. **La definición del campo sale de la tabla y esa es la salida a `/gobierno`.** Es prosa, no
   sobrevive a una fila de 34 px, y una celda que la trunca es una tabla fingiendo que lleva algo
   que esconde. Con eso el reparto de CA-20 deja de ser una frase: `/exploracion` encuentra el campo
   —nombre físico, nombre de negocio, dominio, fuente, responsable y certificación— y `/gobierno`
   publica la ficha. El enlace bajo la tabla es lo que impide que el recorte sea pérdida.
4. **Seis columnas y ninguna cabecera nueva en el catálogo.** Los rótulos se reúsan de
   `lineage.card.*` y de `catalog.facet.group.*`: el mismo concepto se llama igual en las dos
   pantallas, y una clave nueva por columna habría sido copia con otro nombre.
5. **`sincronizarUrl` es una opción y no el comportamiento por omisión.** `/gobierno` monta el mismo
   composable desde un componente cuya caja de texto es suya, y una dirección que llevara un término
   que la caja no muestra sería una pantalla contradiciendo su propia URL. Las dos ramas tienen
   consumidor real: ninguna es andamiaje.
6. **`replace` y no `push` al publicar el término.** Con `push`, cada búsqueda deja una entrada y el
   botón Atrás de quien fue a los tableros aterriza en el catálogo **sin** el término, que es el
   defecto exacto que CA-13 cierra.
7. **El término que llega por la dirección limpia el filtro de dominio.** Viene de fuera de la
   pantalla —el buscador del cromo, un enlace compartido, el botón Atrás— y responderlo a través de
   un filtro que el lector puso para otro término devuelve un vacío que nadie pidió.
8. **La apertura en frío corre en `onMounted` y no en el `setup`.** El `useFetch` del catálogo es
   `server: false`: una petición disparada mientras el servidor renderiza contestaría a un componente
   que nadie ha hidratado.
9. **Cada estado lleva su propia región viva.** Son cuatro ramas `v-if` mutuamente excluyentes y solo
   una está montada; un envoltorio permanente habría sido un elemento cuyo único trabajo es un `role`
   y habría anidado `status` dentro de `status` con el que `cargando` ya declaraba.
10. **El botón `Buscar` es la acción primaria de `/exploracion`.** La pantalla no tenía ninguna: lo
    único que el catálogo existe para hacer pesaba menos que los enlaces de al lado. Se rellena con
    `--color-accion`, que es tinta plena bajo el tema de omisión —idéntico a los primarios que ya
    había— y verde azulado bajo el institucional.
11. **En `/acceso` el formulario de credenciales pasa a revelación, y solo con la puerta de
    demostración abierta.** Con la puerta cerrada es la única vía de entrada y esconderla sería el
    mismo defecto con el signo cambiado. Se abre solo cuando la guarda avisa de sesión caducada,
    porque esa explicación vive dentro del formulario.
12. **El rechazo de la demostración lo anuncia la página.** Las dos negativas compartían la región de
    mensaje del formulario; plegado, el lector habría pulsado un perfil, fallado y no visto nada.
    `origenFallo` decide dónde se dibuja el aviso, y `data-aviso` conserva el mismo contrato.
13. **`limpiar()` se retira del composable.** No tenía ni un consumidor en `app/` ni una prueba, y con
    la sincronización habría sido una segunda forma —no ejercitada— de escribir en la dirección.
14. **La lámina nueva importa los grupos del módulo generado y resuelve el valor con el store.** El
    store no expone `BARRA_LATERAL` ni `CERTIFICACION` y `stores/` no es de esta ola; la excepción es
    la mínima: del generado sale la lista, del store sale el hex del tema y modo en pantalla.

### La copia que cambió, y por qué

**CA-18 — la numeración del mapa sale del producto.** Las siete descripciones de `prototype.branch.*`
publicaban la sección de un entregable académico como descripción de pantalla («4. Administración —
4.1 a 4.4»), y `nav.facets.branchAria` hacía que un lector de pantalla oyera «2.2 Consulta y filtros,
faceta transversal». Ahora dicen qué hay dentro:

| Clave | Antes (es) | Ahora (es) |
|---|---|---|
| `prototype.branch.access` | Pantalla de entrada; enmarca las demás sin ser rama del mapa | Entrada al portal: credenciales y perfiles de demostración |
| `prototype.branch.home` | 1. Inicio | Espacio de trabajo del perfil que entra |
| `prototype.branch.explore` | 2. Exploración y extracción — 2.1 Catálogo temático, 2.2 Consulta y filtros | Catálogo temático de campos, con búsqueda y filtros por dominio |
| `prototype.branch.governance` | 3. Gobierno del dato — 3.1 …, 3.2 …, 3.3 … | Diccionario de campos, linaje del dato y catálogo de fuentes |
| `prototype.branch.assistant` | Transversal a las cuatro categorías | Asistente conversacional, alcanzable desde cualquier pantalla |
| `prototype.branch.administration` | 4. Administración — 4.1 a 4.4 | Usuarios, roles y permisos del portal |
| `prototype.branch.export` | 2.3 Exportaciones | Exportaciones a CSV en segundo plano |
| `nav.facets.branchAria` | `{id} {label}, faceta transversal` | `{label}, faceta transversal` |

Métrica verificada, en los dos idiomas: **cero valores visibles con `[0-9]\.[0-9]` fuera de
`guide.*`**, y cero que abran con «N. ». La exención de `guide.*` está argumentada en la prueba y
tiene su propia comprobación de que no está vacía: ahí un número —4.55:1, +2.4 %, 12 405 780.40— *es*
el contenido. La trazabilidad al mapa no se pierde: sigue en la tabla rama↔ruta de `a4_02`.

**CA-20 — las dos pantallas dejan de abrir iguales.** Compartían etiqueta («Buscar en el catálogo»),
marcador de posición («saldo, límite, contraparte») y título de estado inicial («Empieza por una
búsqueda»). Ahora cada una declara qué resuelve:

| | `/exploracion` (descubrimiento) | `/gobierno` (defensa del dato) |
|---|---|---|
| descripción | Encuentra el campo que necesitas antes de pedir el dato… | Defiende la cifra que ya tienes: quién responde por cada campo… |
| etiqueta | ¿Qué dato necesitas? | Campo cuyo origen hay que verificar |
| marcador | saldo disponible, exposición, mora | nombre físico, nombre de negocio o sinónimo |
| estado inicial | Empieza por lo que necesitas medir | Empieza por el campo en duda |

`contratos.spec.ts` compara los cinco pares en los dos idiomas: si vuelven a coincidir, rojo.

**Claves nuevas** (22 por idioma): `access.demo.recommended`, `access.credentials.hint`,
`catalog.explore.results.openLineage`, `catalog.explore.results.fullRecord`,
`workspace.samples.indicator.diasMora`, `dashboard.table.empty`, `guide.plate.chassis` y las diez de
`guide.chassis.*`. Las dos que pidió la ola C entraron con el texto que ella dejó escrito, y el
indicador `diasMora` ya no toma prestada la clave de «búsquedas recientes».

### Lo que queda pedido, y de quién es

**Para la ola E (documento):**

- **Ninguna prueba que lee `.tex` quedó en rojo.** `alcancePrototipos.spec.ts` y `rutaRama.spec.ts`
  comparan `PROTOTIPOS` y `MODULOS` contra las tablas delimitadas, y esta ola no tocó ninguna de las
  dos constantes. No hay que ajustar nada por obligación.
- **Sí hay que ajustar por verdad**: `a4_03_guia_estilos.tex` dice **«las siete láminas vivas de la
  ruta `/guia` —paleta, tipografía, botones, campos, tablas, tarjetas e iconos—»** en dos sitios
  (§ de alcance y § de simetría de láminas) y **«siete láminas vivas»** en la bitácora de versiones.
  Ya estaba corto antes de esta ola —había diez, con linaje, accesibilidad y tarjetas de tool call— y
  **ahora son once**: entra `chasis`, con los cuatro tokens de barra lateral, los tres estados de
  certificación y la superficie contenida. Es material directo para `a4_03` y para `a4_08`.
- **Las capturas del catálogo cambian de forma**, no solo de tema: la lista de fichas de 80 px es
  ahora una tabla de seis columnas con fila de 34 px, cada fila abre el linaje y el resultado lleva
  salida a gobierno. Y `/acceso` cambia de composición: perfiles en tarjeta de canal `accion` y
  credenciales plegadas.
- **La numeración del mapa ya no aparece en ninguna pantalla.** Si alguna leyenda de figura afirma
  que el portal publica la rama del mapa, hay que reescribirla; la trazabilidad vive en la tabla de
  `a4_02`, que es su sitio y sigue delimitada.

**Para quien pueda tocar archivos fuera de este write-set:**

- `app/components/serie/Tabla.vue` debe pasar `:vacio="t('dashboard.table.empty')"` a `TablaDatos`.
  La clave ya existe en los dos catálogos; hasta que alguien la consuma es la única cadena declarada
  sin consumidor del repositorio.
- `app/components/comun/CabeceraProducto.vue` declara su propio `PARAMETRO_BUSQUEDA = 'q'`. El
  composable ahora exporta `PARAMETRO_TERMINO` con ese mismo valor: el cromo debería importarlo, o
  el día que uno cambie el otro se queda navegando con una letra que nadie lee.
- `app/components/nav/BarraLateral.vue` sigue pasando `{ id }` a `nav.facets.branchAria`, que ya no
  lo interpola. No rompe nada —vue-i18n ignora el parámetro sobrante— pero es un argumento muerto.
- `app/stores/sistemaDiseno.ts` no expone `BARRA_LATERAL`, `CERTIFICACION`,
  `SEPARACIONES_CERTIFICACION_POR_TEMA` ni `PEOR_SEPARACION_CERTIFICACION`. Mientras no lo haga, la
  lámina de chasis importa los dos grupos del módulo generado (decisión 14) y **la lámina no puede
  publicar la separación dicromática de la familia de certificación**, que el emisor sí calcula.

### Tokens que faltaron, y qué se hizo en su lugar

`design/` está cerrado desde la ola A y **no se inventó ningún hexadecimal**.

- **No hay token de enlace.** La salida a `/gobierno` se pinta con `text-corriente-pleno` más
  subrayado, que es lo que ya hacían el índice y el aviso de sesión. Un `--color-enlace` es una
  decisión de sistema, no de pantalla: hoy cada enlace del portal la toma por su cuenta.
- **No hay token de realce para una fila de tabla que es una puerta.** El botón de la cabecera de
  fila se subraya al pasar por encima en vez de cambiar de color: `hover:text-accion` —que es lo que
  usa el botón de orden de `TablaDatos`— **no se ve bajo el tema de omisión**, donde `accion` y
  `corriente-pleno` son el mismo valor. Vale la pena revisar ese hover de la ola C con el mismo
  argumento.
- **No hay token de ancho de columna ni de truncado**, así que la tabla del catálogo hereda de
  `TablaDatos` y desborda con barra horizontal en pantallas estrechas, que es lo que ese componente
  ya decidió.

### Qué quedó desactualizado del 'Estado' de `frontend/AGENTS.md`

Lo escribe el orquestador al integrar; aquí queda la lista de esta ola, además de las que dejaron A,
B y C.

- **`/exploracion` ya no es «catalogo tematico sobre `useBusquedaCatalogo`, con sus cuatro estados no
  felices» y nada más.** Hoy es la pantalla de descubrimiento: tabla densa del sistema, cada fila
  abre el linaje **con el mismo overlay que monta `/gobierno`**, el término vive en la dirección y el
  resultado tiene salida a gobierno. Que una pantalla de `exploracion/` monte un componente de
  `gobierno/` es deliberado y merece la frase, porque es la única forma de que no haya dos paneles de
  linaje.
- **`useBusquedaCatalogo` recibe opciones.** El 'Estado' lo describe como una sola cosa; hoy tiene dos
  modos —con y sin dirección— y **exporta también el cruce de vocabulario de la certificación**
  (`certificacionDeCampo`), que es lo que impide que un componente vuelva a elegir icono. Perdió
  `limpiar()`, que no tenía consumidor.
- **La cuenta de composables baja de 18 a 18 pero la de pruebas sube**: `test/` tiene **53
  `*.spec.ts`** (la guía dice 45; las olas B y C ya la habían dejado en 52) y **1 049 pruebas**.
  `certificacion.spec.ts` es el archivo nuevo de esta ola.
- **La guía de estilos tiene once láminas.** El 'Estado' habla de `/guia` como «láminas del sistema de
  diseño» sin número, pero `a4_03` sí las cuenta y ahí hay que corregir.
- **'Convenciones' merece dos líneas nuevas**: (a) *el término de búsqueda del catálogo viaja en la
  dirección con `replace`, nunca con `push`*, con el motivo del botón Atrás; y (b) *el estado de
  certificación no se elige en el componente: sale de `ESTADOS_CERTIFICACION`, y la ortografía cruza
  una frontera —`en_revision` en la base, `en-revision` en el token—*.
- **La nota de i18n puede ganar una frase**: la copia de producto **no cita la numeración del mapa de
  A3**, y hay una prueba que lo mide en `contratos.spec.ts`. Sin esa línea, el siguiente lector que
  quiera «dar trazabilidad» la vuelve a meter.
- Nada más. El aviso de `data-modo`/`data-tema`, la prohibición de `routeRules` con `swr` y la nota
  de `max-w-none` siguen vigentes y esta ola los cumple.

### Puerta ejecutada

`pnpm lint` → exit 0, sin salida · `pnpm typecheck` → exit 0 · `pnpm test` (con `--coverage`) →
**53 archivos, 1 049 pruebas, 0 fallos**; líneas 93.95 %, sentencias 93.96 %, funciones 91.96 %,
ramas 85.56 %. Los tres códigos de salida se leyeron directos, no por tubería.

**Sin verificar en navegador**: los recorridos V6, V7 y V8 (fila → linaje, `?q=` en frío y
superficies) son de la verificación comprometida con Playwright, igual que V3–V5 de la ola B. Esta
ola los deja probados en el DOM y no medidos a 390, 768, 1280 y 1440.

---

## Registro de implementación — Pruebas

**Cerrado el 15-ago-2026.** Diez pruebas nuevas en ocho archivos —nueve en `frontend/test/` y una en
`tests/ml/`—, ninguna línea de producción tocada. Las seis que valía la pena verificar se comprobaron **mutando el código de producción, con
copia previa y restauración inmediata**: cada mutación pone en rojo exactamente su prueba y ninguna
otra. Write-set: `frontend/test/**` y `tests/**`.

`alcancePrototipos.spec.ts` y `rutaRama.spec.ts` **no se tocaron**: son de quien reescribe los `.tex`
en paralelo.

### Qué se añadió, y el defecto que atrapa cada una

| Archivo | Prueba | Defecto concreto que la pone en rojo | Mutación comprobada |
|---|---|---|---|
| `frontend/test/modoYSistema.spec.ts` | *reparte cada token en exactamente un grupo, y en el orden de la fuente* | `design/` abre un grupo y el store sigue exponiendo los que conocía: todo consumidor que recorre grupos pinta menos tokens de los que `tokens` cuenta. Es el defecto que ya se entregó una vez —la lámina anunciaba 21 y pintaba 18— | Se retira `barraLateral:` del store, rojo |
| `frontend/test/certificacion.spec.ts` | *imprime las tres parejas del estado sin fundirlas con las seis semánticas* | Fundir las dos listas mide marcas que nunca comparten superficie **y** mueve la peor pareja de la paleta, que es la cifra que el informe publica como piso | Cubierta por la mutación de la fila siguiente, sobre el mismo store |
| `frontend/test/certificacion.spec.ts` | *publica las distancias de la combinación en pantalla y no las del otro modo* | El store filtra por tema **y** modo; sin una de las dos condiciones la lámina lista las doce filas de todas las combinaciones, o imprime las cifras de claro con la página en oscuro | Se quita `s.modo === modo.value`, rojo |
| `frontend/test/laminas.spec.ts` | *pinta una muestra por cada token que su propio recuento anuncia* — **`it.fails`, defecto vivo** | Ver «Defecto real encontrado» abajo. Está marcada, no borrada: hoy documenta el hueco y el día que se corrija pedirá volver a `it` | — |
| `frontend/test/cabeceraProducto.spec.ts` | *nombra el parámetro con el del composable y no con una copia propia* | Las dos mitades del viaje de búsqueda las escribieron dos olas distintas y cada una deletreaba su `'q'`. El día que una cambie, la otra navega con una letra que nadie lee: sin error, sin estado vacío, un catálogo que abre sin término y una dirección que sí lo trae. **No se puede atrapar midiendo comportamiento** —dos copias de la misma letra se comportan igual—, así que se mide que sólo haya una letra | — |
| `frontend/test/exploracionCatalogo.spec.ts` | *publica el término con replace, y no deja una entrada por búsqueda* | Con `push` cada búsqueda deja una entrada y Atrás no saca al lector del catálogo: lo devuelve a su búsqueda anterior, una por una. Sobre la dirección las dos formas se ven idénticas, y por eso ninguna aserción anterior lo notaba | `router.replace` a `router.push`, rojo |
| `frontend/test/exploracionCatalogo.spec.ts` | *un término que llega por la dirección suelta el filtro de dominio* | Responder un término que viene de fuera a través del dominio que el lector acotó para el término anterior devuelve un vacío que nadie pidió, sobre un catálogo que sí tiene la respuesta | Se quita `dominio.value = null`, rojo |
| `frontend/test/usuarios.spec.ts` | *ordena la columna de modificación por el instante ISO* | La trampa que esta US encontró tres veces: las celdas llegan formateadas y ordenar el texto impreso es un orden alfabético disfrazado. `tablaDatos.spec.ts` prueba el componente sobre una tabla sintética suya; que **estas** columnas apunten al dato crudo no lo medía nadie | `accessorFn` sobre la fecha formateada, rojo |
| `frontend/test/prediccionesTablero.spec.ts` | *ordena la columna de cifras por la magnitud del punto* | Lo mismo en el otro consumidor y con el caso literal de la convención: `1 284,5` contra `987,6`. La columna anunciaría `descending` con la cifra menor arriba, y quien no ve la flecha oye que está ordenada | `accessorFn: fila => fila.valor`, rojo |
| `tests/ml/test_emision_temas.py` | *ningún grupo de color se queda fuera de las dos salidas* | Un grupo abierto en `sistema.py` y olvidado en `GRUPOS` del emisor no falla: la propiedad CSS nunca se declara —`bg-<nombre>` compila a nada—, el módulo tipado nunca exporta el grupo, y `tokens_de_color()` lo sigue contando. Es el mismo defecto de la lámina, una capa más abajo, y `GRUPOS` existe precisamente para impedirlo | Se retira `CERTIFICACION` de `GRUPOS`, la comparación cae de 28 a 25 |

Dos aserciones existentes se **endurecieron**, no se añadieron: las dos del buscador del cromo en
`cabeceraProducto.spec.ts` escribían `q` como literal y ahora derivan de `PARAMETRO_TERMINO`. Con el
literal seguían pasando mientras las dos mitades derivaban, que es justo lo que hay que impedir.

Todas llevan en su cabecera el defecto que las pone en rojo, y dos llevan además una aserción de
**discriminación** —que el orden alcanzado no coincide con el del texto impreso— para que la prueba
no pueda pasar por coincidencia de los datos de ejemplo.

### Defecto real encontrado, escrito y NO corregido ---CERRADO el 16-ago-2026---

> **Ya no es cierto.** `LaminaPaleta.vue` lista hoy los **siete** grupos que el store
> publica ---`GRUPOS` incluye `sidebar`, `certification` y `series`--- y en la suite **no
> queda ningun `it.fails`**: la corrida ya no reporta «1 expected fail». Una ola posterior
> lo cerro sin volver aqui, y el QA lo verifico contra el archivo. Lo que sigue se conserva
> como registro de por que la prueba se escribio antes que el arreglo; **no salgas a buscar
> este defecto**.

**`app/components/guia/LaminaPaleta.vue` anuncia 28 tokens y pinta 21.**

- **Reproducción**: montar `LaminaPaleta` y contar `[data-token]`, salen 21. El encabezado imprime
  `guide.palette.count` con `sistema.tokens.length`, que son 28.
- **Causa**: su constante `GRUPOS` lista cinco de los siete grupos que el store publica. Los cuatro
  tokens de barra lateral y los tres estados de certificación que abrió la ola A no tienen muestra en
  la lámina de paleta. El propio componente declara en su docstring que «todo grupo que el store
  expone está listado aquí», y desde esta US eso ya no es cierto; el store declara la otra mitad de
  la misma regla con el antecedente escrito: *«announced twenty-one and painted eighteen»*.
- **Alcance real**: los siete sí se ven en la lámina nueva `chasis`, así que no es un color
  inalcanzable; pero la lámina que el evaluador lee como paleta del sistema publica un recuento que
  su propia página no sostiene, y es la hoja de la que alguien copia un valor.
- **Estado**: la prueba existe, marcada con `it.fails` y con la reproducción en el comentario. La
  suite queda en verde y vitest la reporta como «1 expected fail». **El arreglo es una línea por
  grupo en `GRUPOS` de `LaminaPaleta.vue`**, y al aterrizar la prueba empieza a pasar, `it.fails`
  enrojece y pide volver a `it`. No se tocó porque este pase escribe pruebas, no producción.

### Huecos encontrados y NO cubiertos, con el motivo

1. **`peorSeparacionCertificacion` no tiene ningún consumidor.** El store la expone y ninguna
   pantalla la lee: `guia.vue` publica la lista de parejas, no el peor de la familia. Probar una
   computada dormida es probar andamiaje. Queda anotado para que quien publique esa cifra en la
   lámina traiga su prueba con ella, o para que se retire.
2. **`useBusquedaCatalogo` sin `sincronizarUrl` —la rama de `/gobierno`— no gana prueba propia.** El
   defecto sería que la opción se volviera el comportamiento por omisión y el diccionario publicara
   un término en su dirección. Es real pero de daño bajo, porque la caja de `/gobierno` sí muestra
   ese término, y las pruebas de esa pantalla ya montan el composable entero.
3. **`FiltroDominios` pintando el dominio activo con `--color-seleccion`.** Es aspecto de tema, que
   está fuera del alcance de este pase por instrucción explícita. `aria-pressed`, que es lo que
   recibe quien no ve la pantalla, ya está probado.
4. **`BloqueLista` y el desborde horizontal.** El arreglo son tres `min-w-0` y su efecto sólo se mide
   con un navegador real: happy-dom no calcula `scrollWidth`. Fijar las clases sería fijar marcado, y
   la medición de verdad es el recorrido V5 con Playwright, que sigue pendiente y no es de este pase.
5. **`serie/Tabla` y su decisión de no ordenar las columnas de cifras**, que llegan como cadenas
   desde `Panel.vue`. `tablaDatos.spec.ts` ya prueba que una columna sin orden no declara
   `aria-sort`, que es el defecto observable; una tercera copia de la misma aserción sería ruido.
6. **La marca, el chasis, la apariencia, la tabla, la superficie, `/acceso`, la copia sin numeración
   del mapa y la divergencia de las dos pantallas** ya tienen prueba de las olas B, C y D, y se
   revisaron una por una antes de escribir nada. No se duplicó ninguna.

### Lo que quedó desactualizado de las guías

- **`frontend/AGENTS.md`, sección 'Tests'**: dice **53 `*.spec.ts` y 1 049 pruebas**; hoy son los
  mismos **53 archivos** y **1 058 pruebas** (1 057 en verde y 1 marcada `it.fails`). Merece además
  una línea nueva: **hay una prueba marcada como defecto vivo**, y qué significa «1 expected fail» al
  pie de la corrida, para que nadie la lea como una prueba rota ni la borre para dejar verde algo que
  ya lo está.
- **`tests/AGENTS.md`, 'Estado'**: `tests/ml/` sigue siendo 9 módulos —la ola A ya anotó que la guía
  decía 7— y ahora suma **104 pruebas**. Ningún archivo nuevo en `tests/`.

### Puerta ejecutada

Los códigos de salida se leyeron directos, no por tubería.

| Comando | Resultado |
|---|---|
| `pnpm --dir frontend exec vitest run --coverage` | **53 archivos, 1 057 pruebas en verde y 1 `expected fail`**; líneas **94.03 %**, sentencias 94.04 %, funciones 92.22 %, ramas 85.57 %. Umbral 50 % |
| `poetry -P backend run pytest -c backend/pyproject.toml tests/ml -q --no-cov` | **104 passed**, eran 103 |
| `pnpm --dir frontend lint` | exit 0, sin salida |
| `pnpm --dir frontend typecheck` | exit 0 |
| `ruff check` · `ruff format --check` · `mypy` sobre `tests/ml` | exit 0 los tres |

---

## Registro de implementación — Ola E

**Cerrada el 15-ago-2026.** Los dos envoltorios compilan con XeLaTeX sin una sola referencia sin
resolver y **sin un solo desborde de caja atribuible a un `a4_*.tex`**. Las once capturas se
rehicieron en una pasada guionizada, dos veces: la primera a las 18:22 y la segunda a las 18:55,
porque entre una y otra seguía habiendo escritura concurrente en `frontend/app/`. El PDF final está
en `docs/semana_4/` con el nombre exacto.

### Archivos tocados

| Ruta | C/M | Qué |
|---|---|---|
| `docs/entregables/contenido/a4_08_tema_y_flujos.tex` | M | Reescrito casi entero. Los ocho colores con procedencia, el chasis, los 28 tokens, la matriz sobre lo que se lee encima, las dos divergencias, la medición en navegador, las once capturas y **la sección nueva del logotipo** |
| `docs/entregables/contenido/a4_02_prototipos.tex` | M | Recuento de las siete pantallas contra el producto de hoy; subsección nueva del chasis común de las diez rutas |
| `docs/entregables/contenido/a4_03_guia_estilos.tex` | M | Siete → **once** láminas en los tres sitios; dos frases de capturas corregidas; subsección nueva que separa la marca del informe de la del portal |
| `docs/entregables/contenido/a4_04_prevalidacion.tex` | M | **Cuarta iteración** completa: diez hallazgos numerados, cuatro mediciones mecánicas antes y después, cambio, versión |
| `docs/entregables/contenido/a4_05_alcance.tex` | M | Columna de evidencia al día en cuatro filas; subsección nueva «Lo que el prototipo hace hoy» |
| `docs/entregables/contenido/a4_07_anexo.tex` | M | Inventario de las once capturas (dos tablas), inventario técnico recontado, procedencia con Acción y Apoyo, criterio 11 de trazabilidad |
| `docs/entregables/capturas/capturas_tema_a4.mjs` | **C** | Guion de las once capturas del tema. Importa `buildCapturePlan` y `VIEWPORT` del guion hermano |
| `docs/entregables/figuras/a4/tema/*.png` | M | **Las once, recapturadas** a 1440×900 |
| `docs/semana_4/Entregable Actividad 4_equipo_8.pdf` | M | Regenerado: **112 páginas**, 6 376 016 bytes |

**No se tocó**, y estaba prohibido: `estilo/uxdoc.sty`, `estilo/a4_tokens.tex`,
`generar_tokens_a4.py`, `figuras/a4/antes/**` y `figuras/a4/despues/**`, `main_a4.tex`,
`main_completo.tex`, `capturas/capturas_a4.mjs`, `capturas/guion_a4.md`, `a4_00`, `a4_01`, `a4_06`,
y `frontend/`, `design/`, `backend/`, `db/`, `ml/`.

### Qué cifras del documento estaban mal, y contra qué se verificaron

Todas se verificaron **contra el código o contra el navegador**, nunca contra el `.tex` anterior.
Fuente de cada verificación entre corchetes.

| Afirmación publicada | Qué decía | Qué dice el código | Fuente |
|---|---|---|---|
| Tamaño del contrato de tokens | «los **diecisiete** tokens» en `a4_08` (2 veces), `a4_04` y `a4_07` (2 veces) | **28** | `len(sistema.tokens_de_color())` |
| Destino de **Acción `086B70`** | «Ninguno: se aplica desde la capa de componentes» | token `accion` | `design/sistema.py:ACCION` |
| Destino de **Apoyo `15989A`** | «Ninguno: con 3,51:1 no puede llevar texto» | token `accion-apoyo`; el 3,51:1 es cierto y ahora se publica como veredicto «AA texto grande» | `contraste.matriz('institucional','claro')` |
| `info` claro institucional | `123C7A`, razón **10,75:1** | **`17395B`**, razón **11,85:1** | `sistema.py` + `contraste.matriz` |
| Par error/informativo, claro | **62,6** protanopia | **45,4** protanopia | `contraste.separaciones` |
| Par aviso/informativo, claro | **59,9** tritanopia | **54,3** tritanopia | ídem |
| Par confirmación/informativo, claro | **20,1** tritanopia | **22,8** tritanopia | ídem |
| Familia del tema de omisión | «Lexend Deca» en la tabla de medición del navegador | **Fira Sans** en cuerpo, Lexend Deca en titular | `getComputedStyle(document.body).fontFamily` a 1440×900 |
| Láminas vivas de `/guia` | «**siete**: paleta, tipografía, botones, campos, tablas, tarjetas e iconos» (×3 en `a4_03`) | **once**: entran chasis, linaje, accesibilidad y tarjetas de tool call | `LAMINAS` en `app/pages/guia.vue` |
| Barra lateral del catálogo | «el bloque de facetas transversales» como pieza viva | Retirado: nueve etiquetas inertes fuera | `BarraLateral.vue` + `chasis.spec.ts` |
| Estados de certificación | dos colores, dos iconos | tres canales, tres iconos | `ESTADOS_CERTIFICACION` |
| Capturas del documento | «todas en modo claro y tema de omisión» (`a4_03`) | dos capturas en modo oscuro y siete bajo el institucional | `figuras/a4/tema/` |
| Prosa de `a4_08` | «El color de acción no entra en los diecisiete tokens» — subsección entera | La ranura existe; la subsección se sustituyó por «Los ocho estados interactivos» reescritos con nombre de token | `design/sistema.py` |
| Iteración 3 | «Esta iteración tampoco se recaptura» | Se recaptura, en carpeta nueva y sin tocar el par | `figuras/a4/tema/` |

**Lo que sí seguía siendo cierto y se dejó intacto**: cero incumplimientos en las cuatro
combinaciones, mínimo real 4,54:1, separación 13,6/21,5 y 14,5/22,6, las seis series con mínimo
5,02 en claro y 9,43 en oscuro, y toda la matriz de contraste salvo `info` en claro.

### Cifras nuevas que esta ola midió

- **Medición en navegador de las cuatro combinaciones** (Chromium sin cabeza, 1440×900, sesión de
  administración): suelo `F4F6F9` / `0A0A0C` / `FFFFFF` / `0B1B2B`; barra lateral `EAEEF4` /
  `131519` / `102A43` / `102A43`; acción `14171D` / `E8F4FF` / `086B70` / `3FB3B5`; familia de
  cuerpo Fira Sans / Fira Sans / Inter / Inter; **0 desbordes de contenido** en las cuatro.
- **V5 ejecutado y verde**: **160 mediciones** de `scrollWidth` contra `clientWidth` —10 rutas del
  chasis (`/`, `/acceso`, `/inicio`, `/exploracion`, `/exploracion/exportar`,
  `/exploracion/tableros`, `/gobierno`, `/asistente`, `/administracion`, `/guia`) × 4 anchos (390,
  768, 1280, 1440) × 4 combinaciones de tema y modo— con **exceso 0 en todas**. Cierra el hallazgo
  11 (194 px a 390) y es la primera vez que ese recorrido se corre sobre el chasis integrado.

### Decisiones

1. **La iteración nueva se numera cuarta, no tercera.** El encargo la llama «la tercera», pero
   `a4_04` ya publicaba tres iteraciones numeradas —franja de alcance, paleta y catálogo
   construido—, todas de la misma ronda de evaluadores prototipo. Renumerar habría contradicho un
   texto ya escrito; llamarla tercera habría creado dos terceras. Entra como **cuarta**, con su
   origen distinto declarado en la primera frase: revisión de diseño y pasada mecánica, no ronda
   sintética.
2. **Las siete figuras de `a4_02` no se sustituyen, y el documento lo dice en voz alta.** Son
   `despues/`, evidencia cerrada. La alternativa —dejarlas sin comentario— habría hecho que el
   lector descubriera por su cuenta que el chasis de las figuras 3 a 9 no es el de las figuras 14 a
   24. Cada prototipo declara ahora qué cambió y remite a la figura del estado entregado.
3. **El logotipo va en `a4_08` y no en `a4_03`.** Lo fija la decisión 2 del plan y lo confirma
   ADR-002: `a4_03` documenta la marca **del informe**, con sus 16 y 96 px de tinta sobre papel.
   Publicar la del portal ahí habría enfrentado dos juegos de cifras en la misma sección. `a4_03`
   gana en cambio una subsección de tres líneas que nombra la diferencia y remite.
4. **La captura del catálogo se toma con término en la dirección.** `/exploracion` en reposo es un
   estado vacío por diseño, y fotografiarlo habría documentado la pantalla que la iteración
   sustituyó. `QUERY_BY_ROUTE` añade `?q=saldo` a esa ruta y solo a esa; el pie declara la
   dirección exacta. No es un estado montado para la foto: es lo que produce un enlace compartido,
   que es justamente la capacidad que CA-13 cerró.
5. **`a4_08` deja de agrupar todo bajo `\uxsection`.** El banner sigue siendo `\uxsection` —como en
   todos los archivos— pero el cuerpo se reparte en cuatro `\section` numeradas. Motivo medido: con
   una sola sección sin número, las subsecciones seguían contando bajo la última numerada de
   `a4_05` y el índice imprimía `22.20.Flujo 4` con el número pegado al título, nueve desbordes de
   caja. Ninguna sección llega ahora a diez subsecciones y los nueve desbordes desaparecen. **Este
   defecto ya estaba en el PDF entregado**: `21.10.Flujo 1` se lee así en la página 5 del PDF de
   Canvas.
6. **El inventario de capturas se parte en dos tablas y factoriza el prefijo.**
   `combinacion_institucional_oscuro_inicio.png` mide 43 caracteres en monoespaciada de 9 pt y se
   salía 26,77 pt de su columna. Publicar el prefijo en el pie de la tabla y el resto en la celda
   deja la información completa y la caja dentro del margen.
7. **La tabla de las siete capturas es `uxtablalarga` y no `uxtabla`.** `uxtabla` es un flotante y
   no se parte; con once capturas inventariadas en la misma subsección la página se iba 218,42 pt
   de alto. `uxtablalarga` es longtable y se parte, que es para lo que existe.
8. **Se retiran las comillas rectas del fragmento de HTML.** Bajo `babel` español la comilla recta
   es carácter activo: `lang="es"` se imprimía como `lang=.es"data-tema=ïnstitucional"`. Los
   atributos se publican sin comillas y la frase dice que van entrecomillados.
9. **La divergencia del logotipo se publica dos veces, con el mismo texto.** En la sección propia y
   como fila nueva de la tabla de verificación técnica del archivo («Marcas de producto declaradas:
   **2**»). Una verificación técnica que declara seis ceros y calla la única incidencia abierta es
   una verificación que no se leyó entera.
10. **Las once figuras del tema van a 0,84 del ancho de caja y no a 0,92.** A 0,92 cada una
    medía 9,5 cm de alto y dos no cabían juntas con sus pies, así que LaTeX les daba página
    propia: once páginas con una imagen y tres cuartos de blanco. A 0,84 el par cabe y el
    documento baja de 115 a **112 páginas**, con cada figura acompañada de su prosa. A 14,3 cm
    de ancho una captura de 1440 píxeles sigue por encima de 250 puntos por pulgada, de modo
    que no se pierde legibilidad. Agruparlas de dos en dos dentro de un mismo flotante habría
    apretado más, pero exige un macro de par que `uxdoc.sty` no tiene y esa hoja está congelada.

### Las once capturas rehechas

Todas a **1440×900 píxeles CSS, escala 1, español, modo y tema fijados por cookie y verificados en
la raíz del documento antes de disparar**. Portal servido por `pnpm dev --port 3001` con
`NUXT_API_BASE=http://localhost:8000` contra el api del Compose, que es el bucle rápido que declara
`guion_a4.md`: el contenedor `web` sirve un bundle anterior a las olas B, C y D.

| Archivo | Ruta capturada | Sesión | Tema · modo | Bytes |
|---|---|---|---|---|
| `institucional_claro_0_acceso.png` | `/acceso` | sin sesión | institucional · claro | 73 099 |
| `institucional_claro_1_inicio.png` | `/inicio` | operativo | institucional · claro | 128 574 |
| `institucional_claro_2_exploracion.png` | `/exploracion?q=saldo` | analista | institucional · claro | 181 173 |
| `institucional_claro_3_gobierno.png` | `/gobierno` | analista | institucional · claro | 111 161 |
| `institucional_claro_4_administracion.png` | `/administracion` | admin | institucional · claro | 148 957 |
| `institucional_claro_5_asistente.png` | `/asistente` | directivo | institucional · claro | 107 580 |
| `institucional_claro_6_exportacion.png` | `/exploracion/exportar` | analista | institucional · claro | 120 093 |
| `combinacion_corriente_claro_inicio.png` | `/inicio` | operativo | omisión · claro | 132 815 |
| `combinacion_corriente_oscuro_inicio.png` | `/inicio` | operativo | omisión · oscuro | 137 550 |
| `combinacion_institucional_claro_inicio.png` | `/inicio` | operativo | institucional · claro | 128 610 |
| `combinacion_institucional_oscuro_inicio.png` | `/inicio` | operativo | institucional · oscuro | 131 011 |

`figuras/a4/antes/**` y `despues/**` **no se tocaron**: `git status` los deja sin modificar y el par
de la primera iteración sigue emparejado por nombre.

**Dos hallazgos del guion, que valen como método**:

- **El tema de omisión no escribe `data-tema`.** `useTema` emite el atributo solo para la anulación,
  porque ese tema *es* el bloque base de la hoja generada. La primera corrida falló las dos capturas
  de omisión con `tema= modo=claro`; la comprobación trata ahora el atributo ausente como
  `corriente`, con la razón escrita en el propio guion. Sin esa comprobación las dos capturas se
  habrían escrito igual y nadie habría notado nada.
- **La numeración de `tema/` no es la de `PROTOTIPOS`.** Ahí administración es la 4 y asistente la
  5, al revés que en `antes/` y `despues/`, y exportación es `6_exportacion` y no
  `6_exploracion-exportar`. Los nombres se declaran en el guion —son contrato con el `.tex`— y se
  cruzan contra el plan importado: añadir o quitar un prototipo hace fallar la corrida en vez de
  saltarse una captura en silencio. La divergencia queda anotada en `a4_07`.

### Resultado de las dos compilaciones

```
latexmk -xelatex main_a4.tex        -> exit 0 · 112 páginas · 6 376 016 bytes
latexmk -xelatex main_completo.tex  -> exit 0 · 259 páginas
```

**Referencias sin resolver: 0 en los dos.** `grep -c undefined` sobre los dos `.log` da 0, incluidas
las referencias hacia adelante de `a4_02` y `a4_04` a figuras de `a4_08`.

**Avisos, todos declarados:**

| Aviso | Dónde | De quién es |
|---|---|---|
| `LaTeX Warning: You have requested package 'estilo/uxdoc'` | los dos | Preexistente: el paquete se llama `uxdoc` y se pide por ruta. `uxdoc.sty` está congelada |
| 4 `Overfull \hbox` de 0,21 a 0,93 pt | `main_a4`, índice | Números de página de **tres cifras** (100, 100, 106 y 108) contra el `\@pnumwidth` de `uxdoc.sty`. **No corregible desde el write-set**: el índice se compone en `main_a4.tex` antes de cualquier `\input`. Preexistente desde que el documento pasó de 99 páginas |
| 26 `Overfull \hbox` sub-punto | `main_completo`, índice | Lo mismo, sobre 259 páginas |
| 9 `Overfull \hbox` de 2 a 19 pt | `main_completo`, cuerpo de `a3_01`, `a3_02`, `a3_03`, `a3_06` | Entregado y calificado; fuera del write-set |
| `xdvipdfmx:warning: Object @page.1 already defined` | los dos | Preexistente, de `hyperref` sobre la portada |
| `MiKTeX ... unsupported version of Windows` | los dos | Del entorno, no del documento |

**Desbordes atribuibles a un `a4_*.tex`: cero, en los dos envoltorios.** Se comprobó recorriendo el
`.log` con el archivo de entrada en curso: `Counter({'PREAMBULO/TOC': 4})` en `main_a4` y
`Counter({'PREAMBULO/TOC': 26, 'a3_*': 9})` en `main_completo`. Al empezar la ola eran **20** en
`main_a4`, de los cuales 9 del índice por la numeración de subsecciones, 7 de la tabla nueva de
`a4_07`, 2 de `a4_08` y un `Float too large` de 29,13 pt en `a4_05`; además de un
`Overfull \vbox` de 218,42 pt en `a4_07`, cerrado con la decisión 7.

### Puerta ejecutada

- `pnpm exec vitest run test/alcancePrototipos.spec.ts test/rutaRama.spec.ts` → **10 pruebas en
  verde**, corrido tres veces: antes de tocar nada, después de `a4_02` y `a4_05`, y al cerrar.
  **Ninguna prueba se debilitó**: las tablas delimitadas conservan ruta, nombre y etiqueta, y solo
  cambió la columna de evidencia, que ninguna prueba lee.
- `scripts/verificar_tokens_a4.sh` → verde en los cinco pasos, incluido el paso 4, que recorre los
  22 archivos de contenido buscando hexadecimales con almohadilla: **0**. Los ocho colores nuevos de
  `a4_08` y los tres de `a4_07` se publican como `\texttt{086B70}`.
- Suite completa del frontend antes de empezar: **53 archivos, 1 049 pruebas, 0 fallos**. Al cerrar:
  **53 archivos, 1 057 pruebas + 1 `it.fails` esperado**. Las ocho pruebas nuevas y el `it.fails` de
  `laminas.spec.ts` **no son de esta ola**: son de escritura concurrente en `frontend/app/` y
  `frontend/test/` entre las 18:25 y las 18:34. Ninguna suite quedó en rojo y esta ola no tocó un
  solo archivo de `frontend/`.

### Riesgo que sí se materializó, y cómo se atendió

**Escritura concurrente durante la captura.** Entre la primera y la segunda pasada de capturas
cambiaron `TablaUsuarios.vue` (18:31), `useBusquedaCatalogo.ts` (18:33), `TablaDetalleSerie.vue`
(18:33) y `stores/sistemaDiseno.ts` (18:34) — es decir, después de que se hubieran fotografiado
`/administracion` y `/exploracion`. Las once se rehicieron completas a las 18:55 y los tamaños
resultantes son iguales salvo decenas de bytes, así que aquellos cambios no alteraron lo que estas
pantallas pintan. **Quien vuelva a compilar después de tocar `frontend/` tiene que recapturar**: el
PDF entregado corresponde al árbol de las 18:55.

### Qué quedó desactualizado del 'Estado' de `docs/AGENTS.md`

Lo escribe el orquestador; aquí queda la lista.

- **«`main_a4.tex` declara nueve `\input` […] y los nueve existen»** sigue siendo cierto, pero la
  frase que sigue ya no: `a4_08` no es «de US-ENTREGA-A4» a estas alturas —esta US lo reescribió
  casi entero— y su contenido no son «tres bloques» sino **cuatro**: el tema, el logotipo, los
  flujos y la verificación técnica.
- **«El sistema de diseño llegó al documento con dos temas […] publica la segunda paleta»** se queda
  corto: la paleta pasó de **17 a 28 tokens**, entró la sección del logotipo con la discrepancia del
  archivo declarada, y `a4_03` ya no tiene «una única línea tocada por esa US» —esta ola le corrigió
  tres recuentos, dos frases sobre capturas y le añadió una subsección—.
- **La trampa del paso 4 de `verificar_tokens_a4.sh` sigue vigente y merece quedarse**: es la razón
  por la que los once hexadecimales nuevos de esta ola se escriben sin almohadilla.
- **«Las capturas del prototipo son un artefacto nuevo […] `guion_a4.md` y su ejecutable
  `capturas_a4.mjs`»** ya no describe la carpeta: hay **dos ejecutables**. `capturas_tema_a4.mjs`
  importa `buildCapturePlan` y `VIEWPORT` del primero y añade el eje de tema y modo, la
  comprobación de apariencia en la raíz del documento y el mapa de nombres de `figuras/a4/tema/`.
  Salida en una **tercera** carpeta.
- **'No tocar' necesita una línea**: `figuras/a4/tema/**` **sí se recaptura** —a diferencia de
  `antes/` y `despues/`— y se recaptura entera, porque las once forman un conjunto de un mismo
  estado del producto. Recapturar tres de once produciría una galería con dos chasis.
- **La cuenta de archivos cambió**: «De los 281 archivos, 175 están versionados» ya no cuadra;
  `capturas_tema_a4.mjs` es un archivo nuevo versionado.
- Nada más. `semana_5/` sigue sin existir, `us-resolved/` y `us-research/` tampoco, y las
  convenciones ❌ se cumplieron todas: no se tocó `a1_*`, `a2_*`, `a3_*` ni sus PDF, no se escribió
  en tiempo futuro, no se derivó nada de `uxdoc.sty` y ninguna cifra nueva viaja sin su origen.

### Tres afirmaciones falsas que esta ola NO pudo tocar

Salieron del recuento y **quedan dentro del PDF entregado**, contradiciendo lo que esta ola corrigió
en sus propios archivos. Los tres viven fuera del write-set literal —`a4_00`, `a4_01` y `a4_06` no
estaban en el encargo— y por eso se declaran aquí con su arreglo exacto en lugar de aplicarse.

| Archivo | Línea | Dice | Debería decir |
|---|---|---|---|
| `a4_06_cierre.tex` | 19 | «repartidos en **siete láminas** de la ruta viva del sistema de diseño» | **once**. Es el mismo recuento que `a4_03` corrigió en sus tres apariciones. Sin este cambio el PDF se contradice a sí mismo: la guía dice once y el cierre dice siete, con cuarenta páginas de distancia |
| `a4_00_preliminares.tex` | 33 | «una pre-validación sobre capturas reales del prototipo con **tres** iteraciones documentadas» | **cuatro**. `a4_04` publica ahora la cuarta, provocada por la revisión de diseño y la pasada mecánica |
| `a4_01_metodo_prototipado.tex` | 118 | «Modo claro y tema de omisión […] fijar una sola combinación es lo que hace comparables entre sí las siete capturas» | Sigue siendo cierto **del par antes y después**, y conviene acotarlo a él: las once capturas del tema recorren las cuatro combinaciones a propósito, y el párrafo se lee hoy como si el documento no tuviera ninguna |

El tercero es matizable; los dos primeros son cifras equivocadas. Son tres ediciones de una línea
cada una y ninguna toca tabla leída por prueba.


### Lo que queda abierto, y de quién es

1. **Los dos desbordes del índice** (0,21 y 0,33 pt sobre números de página de tres cifras) exigen
   subir `\@pnumwidth` en `uxdoc.sty`, que está **congelada** porque A1, A2 y A3 compilan contra
   ella. Es una decisión de equipo con ADR, no un arreglo de esta ola.
2. **La marca vigente del producto sigue sin confirmar.** El documento aplica la de la página
   normativa y lo declara. Corresponde al equipo cerrar la discrepancia con el archivo.
3. **El tercer nivel del contrato de contraste** —uno para componente y texto grande— es lo que
   permitiría publicar el ámbar `B97812` sin oscurecerlo. Queda declarado en `a4_08` como pendiente
   de sistema, tal como el plan lo dejó fuera de alcance.
4. **Comentario obsoleto en `design/sistema.py`**, fuera del write-set: la nota de `aviso` dice que
   el ámbar de identidad «ships as `aviso-marca` below», y **ese token no existe**. El documento no
   repite la afirmación —publica la derivación del 12 %— pero el comentario debería corregirse o
   convertirse en la petición de token que en realidad es.
5. **`docs/manual-test/`** no recibió pasos nuevos de esta ola: la comprobación de apariencia vive
   dentro del guion de captura y falla sola.

---

## Registro de integración — orquestador

**Cerrado el 15-ago-2026.** Las cinco olas y la pasada de pruebas entregaron; esto es lo que hubo que
resolver **entre** ellas, que por definición no era de nadie.

### Costuras cerradas

1. **`CabeceraProducto` declaraba su propio `'q'`.** El cromo navega a `/exploracion?q=` (ola B) y el
   catálogo lee el término (ola D), y cada mitad tenía su constante. Ahora las dos importan
   `PARAMETRO_TERMINO` del composable, que es el dueño del vocabulario del cable. Ni el linter ni la
   suite habrían visto la deriva: dos literales iguales no se contradicen hasta que uno cambia.
2. **`guia.vue` importaba del módulo generado, saltándose el store.** El docstring de
   `stores/sistemaDiseno.ts` declara que los componentes leen tokens de ahí **y nunca del generado**,
   justo para que un renombre del emisor llegue a un archivo. El store no exponía los grupos que
   abrió la ola A porque `stores/` no era de ninguna ola. Ahora expone `barraLateral`,
   `certificacion`, `estadosCertificacion`, `separacionesCertificacion` y
   `peorSeparacionCertificacion`, y la única importación que queda del generado en todo `app/` es de
   **tipos**.
3. **La lámina de paleta anunciaba 28 tokens y pintaba 21.** Lo encontró la pasada de pruebas y lo
   dejó escrito como `it.fails` sin corregirlo, que era su encargo. `LaminaPaleta.vue` recorría cinco
   de los siete grupos: le faltaban los cuatro del chasis y los tres de certificación. **Es el mismo
   defecto que ya se entregó una vez** —anunció 21 y pintó 18 cuando llegó `accion`—, y cae sobre la
   lámina que la rúbrica califica como guía de estilos viva, que es exactamente de donde alguien
   copia un color. Corregido, y la prueba vuelve a ser `it`.
4. **Una clave i18n sin consumidor posible.** `dashboard.table.empty` se añadió para el vacío de
   `serie/Tabla`, pero esa tabla solo se monta con marco no nulo y sus filas salen del marco: el
   vacío **no es alcanzable**. Se retiró en vez de cablearla. `TablaDatos.vacio` se conserva porque
   lo fija §4 del plan y es el contrato de una primitiva reutilizable, no andamiaje de pantalla.
5. **Tres afirmaciones falsas dentro del PDF**, en `a4_00`, `a4_01` y `a4_06`, fuera del write-set de
   la ola E. La peor: el cierre decía «siete láminas» mientras la guía ya decía once, con cuarenta
   páginas de distancia. Corregidas y **el PDF recompilado**.
6. **`@tanstack/vue-table@9.1.2` lo instalé yo antes de lanzar B y C**, porque `pnpm add` escribe el
   lockfile y la ola B estaba corriendo pruebas contra él. Registrado en las decisiones irrevocables
   de `AGENTS.md` y `CLAUDE.md` de la raíz, que son espejos y se movieron juntos.

### Las guías de carpeta

Las escribió el orquestador, como fija el plan: `frontend/AGENTS.md` y `tests/AGENTS.md`, cada una
con su espejo `CLAUDE.md` byte-idéntico. Entraron las siete correcciones que reportaron las olas —el
chasis, el cromo de seis controles, TanStack v9, la cuenta de rutas, la de pruebas— y cinco
convenciones nuevas que salieron de defectos medidos, no de opinión: el orden de tabla sobre el valor
crudo, `min-w-0` en rejilla, `replace` y no `push` para el término, el estado de certificación desde
`ESTADOS_CERTIFICACION`, y la marca como única excepción declarada al color desde tokens.

### ¿Hay que recapturar? No, y esta es la razón

La ola E capturó a las 18:55 y después toqué `frontend/`. **Las 11 capturas siguen siendo válidas**
porque lo que cambió después vive **solo en `/guia`**: `LaminaPaleta.vue` y tres claves bajo
`guide.palette.group` y `guide.accessibility`. Sus únicos consumidores en todo `app/` son
`components/guia/**` y `pages/guia.vue`, y **`/guia` no está entre las 11**: son las siete pantallas
bajo el tema institucional claro más las cuatro combinaciones sobre `/inicio`. `permisos.generated.ts`
lo reescribió `make check` byte a byte igual.

### Puerta ejecutada, al cierre

| Puerta | Resultado |
|---|---|
| `make check` | **exit 0**: ruff, ruff format, los dos mypy, eslint, `nuxt typecheck`, gitleaks —sin fugas y con su propia verificación de que el escaneo detecta— y mapa de permisos al día |
| `make test` — backend y ml | **826 passed**, 17 skipped (integración con BD, sin `KARISMA_TEST_DATABASE_URL`), cobertura **98.23 %** sobre un piso de 70 |
| `make test` — frontend | **53 archivos, 1 058 pruebas**, cobertura de líneas **94.03 %** sobre un piso de 50 |
| `latexmk -xelatex main_a4.tex` | **exit 0**, 113 páginas, 0 referencias sin resolver. 5 desbordes, todos del índice: números de página de tres cifras contra el `\@pnumwidth` de `uxdoc.sty`, que está **congelada** y se compone antes de cualquier `\input` |
| `latexmk -xelatex main_completo.tex` | **exit 0**, 260 páginas. Mayor desborde 5.11 pt, del cuerpo de A3, ya entregado |
| PDF de entrega | `docs/semana_4/Entregable Actividad 4_equipo_8.pdf`, byte a byte idéntico a `main_a4.pdf` |

Punto de partida de la US: 48 suites y 880 pruebas en el frontend. Cierre: **53 y 1 058**.

### Instantánea de archivos

**92 rutas** en el árbol de trabajo, **80** de ellas ya versionadas (`git diff --name-only 3d4db21`);
el resto son archivos nuevos.

| Carpeta | Archivos |
|---|---|
| `frontend/test` | 19 |
| `docs/entregables/figuras/a4/tema` | 11 |
| `docs/entregables/contenido` | 9 |
| `frontend/app/components/comun` | 8 |
| `frontend/app/components/inicio` | 6 |
| `frontend` | 4 |
| `design` | 3 |
| `frontend/app/components/exploracion` | 3 |
| `frontend/app/layouts` | 3 |
| `frontend/app/utils` | 3 |
| `(raiz)` | 2 |
| `frontend/app/pages` | 2 |
| `frontend/i18n/locales` | 2 |
| `tests` | 2 |
| `tests/ml` | 2 |
| `docs/entregables/capturas` | 1 |
| `docs/semana_4` | 1 |
| `docs/us-handoff` | 1 |
| `frontend/app/assets/css` | 1 |
| `frontend/app/components/administracion` | 1 |
| `frontend/app/components/guia` | 1 |
| `frontend/app/components/nav` | 1 |
| `frontend/app/components/serie` | 1 |
| `frontend/app/components/tablero` | 1 |
| `frontend/app/composables` | 1 |
| `frontend/app/pages/exploracion` | 1 |
| `frontend/app/stores` | 1 |
| `frontend/app/types` | 1 |

### Nube, schema y despliegue

**Nada de los tres.** Ningún recurso de nube, ningún secreto, **ninguna migración** y **ningún
despliegue**: la preferencia de apariencia sigue viviendo en cookie. El stack de Docker local se usó
solo como backend real de las capturas.

### Lo que queda abierto, y de quién es

- **Un grupo `marca-*` invariante al tema en `design/`.** Mientras no exista, los cuatro hex del
  logotipo viven en `MarcaKarisma.vue` con su razón escrita y una prueba que falla si alguien mete
  un `var(--color-` ahí.
- **No hay color de enlace**, y `hover:text-accion` no se ve bajo el tema de omisión, donde `accion`
  y `corriente-pleno` son el mismo valor. Por eso la fila-puerta del catálogo se subraya.
- **No hay token de geometría por tema**: el radio del institucional se resuelve con una variante de
  Tailwind sobre `data-tema`.
- **`peorSeparacionCertificacion` no tiene consumidor todavía.** Se expone porque el store publica la
  familia entera; probarla hoy sería probar andamiaje.
- **Sin push ni PR**, a la espera de visto bueno.

---

## Registro de integración — ortografía del español, cargador y redacción

**Cerrado el 16-ago-2026**, a petición del usuario después de cerrar las cinco olas.

### 1. Los acentos y la eñe, medidos y no supuestos

El primer barrido, por lista de palabras sospechosas, dio **128 hallazgos y casi todos falsos**:
`esta`, `solo`, `como`, `consulta` y `acciones` no llevan tilde. El método que sí sirvió fue buscar
**la misma palabra escrita de las dos formas dentro del propio catálogo** —evidencia, no sospecha— y
completarlo con dos reglas seguras: un singular en `-cion` o `-sion` siempre la lleva, y el plural
`-ciones` nunca.

| Superficie | Hallazgos | Qué se hizo |
|---|---|---|
| `frontend/i18n/locales/es.json` | **7** | «Busquedas», «Catalogo tematico», «Bitacora», «toda grafica», «Desactivacion por borrado logico», «esta declarado», «fallo el transporte». Cinco eran del mismo grupo de claves: una tanda de copia tecleada sin acentos |
| `ml/data/catalog_content.py` | **515 líneas** | El corpus del catálogo estaba escrito entero en ASCII. 205 palabras distintas, aplicadas **solo dentro de prosa** |
| `ml/data/schemas.py` | 7 etiquetas | «Tesoreria», «Dolar estadounidense», «Credito PyME», «Tarjeta de credito» |
| `ml/data/seed_catalog.py` | 5 nombres | Beltrán, Iván, Ríos, Íñiguez, Sofía. Cortes, Salas, Nieto, Ocampo, Aranda y Zepeda se quedan: son válidos sin tilde |
| `db/seeds/catalog_lineage.sql` | 14 líneas | Curado a mano, sin emisor |
| Cuerpo de los `.tex` | **0** | El entregable ya estaba bien escrito; los tres «diseno» que aparecen son comentarios LaTeX |

**Ni una eñe faltaba en texto visible.** Se buscó en `frontend/app`, `i18n`, `server`, los `.tex` y
`scripts`: los 25 hallazgos son identificadores (`tamano`, `data-tamano-icono`) y comentarios en
inglés, donde el ASCII es lo correcto.

**Lo que no se tocó, y por qué.** Los **1 935** literales que son código —slugs de dominio
(`operacion`, `categoria`), nombres de columna (`tipo_operacion`, `nocional_usd`)— quedaron intactos:
son el vocabulario del cable y acentuarlos habría roto el contrato con el frontend, con `db/seeds` y
con el mapa de facetas. La frontera se implementó con `(?<![w_])` y `(?![w_])`, que es lo que impide
que `operacion` dentro de `tipo_operacion` se toque.

**Un falso positivo detectado a mano**: «Paso de abandono» y «Paso del flujo digital» son el
sustantivo *paso*, no el pretérito *pasó*. Revertidos. El único `pasó` que queda es «el RFC pasó la
validación», que sí es verbo.

### 2. El filtrado sin cargador

Medido con Playwright antes de tocar nada, porque el catálogo y el diccionario **sí** tenían
esqueleto y había que encontrar cuál no. El defecto está en `useSerieTablero.ts`: `estado` devuelve
`cargando` solo cuando `data.value === null`, es decir **solo en la primera carga**. Al cambiar un
filtro el marco anterior sigue en `data`, `estado` se queda en `listo` y la pantalla no dice nada.

Instrumentado en el navegador: cambiar la métrica disparó
`GET /api/metrics/series?metrica=ratio_lcr` y durante toda la petición hubo **0 esqueletos, 0
`aria-busy` y 0 regiones vivas**. El lector estaba mirando las cifras anteriores sin manera de
saberlo.

**Arreglo**: un `revalidando` propio (`status === 'pending' && data !== null`). El panel marca
`aria-busy`, pinta una barra y anuncia por región viva, **sin desmontar la gráfica**: un esqueleto
aquí sería peor que el silencio, porque tira la instancia de ECharts y con ella la ventana a la que
el lector hizo acercamiento. Verificado después: **275 ms** de cargador y `canvas` montado en las 931
muestras.

De los cinco composables que hacen `useFetch`, **era el único** con esa ceguera:
`useBusquedaCatalogo`, `useLinajeCampo` y `usePrediccionesTablero` ya miraban `status`, y el filtro de
`/administracion` es de cliente y no pide nada.

### 3. La redacción

Se midió antes de opinar. Las muletillas típicas de texto generado **no estaban**: los 34 «cabe» son
«cabecera», y «En resumen» aparecía una vez, dentro del bloque que se retiró.

Lo que sí delataba al documento eran **18 menciones de la rúbrica**, y dos bloques enteros escritos
para el evaluador y no para el lector:

1. Una sección que **defendía la herramienta contra la recomendación de la rúbrica**, con una tabla
   cuyo encabezado era literalmente «Lo que la rúbrica pide». Ahora es «Sobre el medio del prototipo»
   y contrasta las cuatro propiedades **de un prototipo de alta fidelidad**, que es la norma
   profesional y no una lista de cotejo.
2. Una **tabla de trazabilidad con los pesos** de cada apartado, seguida de un párrafo que explicaba
   la estrategia de calificación: *«el tope se alcanza con cinco pantallas… con siete, el margen
   absorbe dos juicios parciales»*. **Retirados los dos.** En su lugar, la razón real por la que hay
   siete pantallas: exportación y asistente sostienen el recorrido, y sin ellas encontrar un dato no
   termina en nada y la promesa del lenguaje natural se queda sin demostrar.

También salió la apelación al objetivo de aprendizaje OEA 2.2, y las cinco menciones sueltas de
`a4_01`, `a4_02`, `a4_03`, `a4_06` y `a4_07` se reescribieron sin nombrarla. **Cero menciones en el
cuerpo del documento.**

### 4. Consecuencias, ejecutadas

| Paso | Resultado |
|---|---|
| `python -m ml.data.seed_catalog` | `db/seeds/catalog.sql` regenerado, 12 fuentes · 304 campos · 30 notas |
| `make db-seed` | Base resembrada. Comprobado en el portal: «Cartera de crédito», «Garantías y colaterales», «Tesorería y flujo de efectivo» |
| **Las 11 capturas, rehechas** | Una sola pasada guionizada a 1440×900 con `capturas_tema_a4.mjs`. `antes/` y `despues/` **sin tocar** |
| `latexmk main_a4.tex` | exit 0, **113 páginas**, 0 referencias sin resolver. Los desbordes bajan de 5 a **2**, los dos del índice contra `uxdoc.sty`, que está congelada |
| `latexmk main_completo.tex` | exit 0, 260 páginas |
| PDF de entrega | Republicado, byte a byte idéntico a `main_a4.pdf` |
| `make check` · `make test` | **exit 0** los dos. Backend y ml **826 passed**; frontend **53 archivos y 1 063 pruebas**, cobertura 94.04 % |

La prueba de `tests/ml` que exige que el seed versionado esté al día **se puso en rojo sola** al
cambiar el contenido y sin haber regenerado: hizo exactamente su trabajo.

### 5. Barreras nuevas

- `idioma.spec.ts` — dos pruebas que recorren el catálogo español: una palabra de la lista que
  siempre lleva tilde escrita sin ella, o una eñe escrita como ene, ponen la suite en rojo **con la
  clave señalada**. Verificado por mutación: devolver «Bitacora» da rojo nombrando
  `screen.administration.capability.audit`. Se descartó una tercera prueba por duplicar a la primera,
  y cuatro palabras salieron de la lista —`practica`, `publico`, `calculo`, `termino`— porque son la
  primera persona de cuatro verbos corrientes.
- `tablero.spec.ts` — tres pruebas del refiltrado: que anuncia, que **no desmonta la gráfica** y que
  deja de anunciar al terminar. Verificado por mutación: con `revalidando` siempre falso, rojo.

**Instantánea al cierre**: 100 rutas en el árbol de trabajo. Sin push ni PR, a la espera de visto
bueno.

---

## Registro de integración — observaciones del profesor sobre la entrega anterior

**Cerrado el 16-ago-2026.** Dos observaciones de la calificación previa, aplicadas a esta entrega.

### 1. «No era necesario incluir la rúbrica»

**Ya estaba resuelto** en la pasada de redacción de esta misma sesión, y de la forma más fuerte de
las dos que el usuario planteaba: en lugar de mover la tabla al anexo, se retiró. Con ella salieron
el párrafo que explicaba la estrategia de puntaje, la sección que defendía la herramienta contra la
recomendación de la rúbrica y las cinco menciones sueltas del resto de los archivos. **Cero
menciones de la rúbrica en el cuerpo del documento.**

### 2. Disciplina de saltos de página

Se midió el PDF antes de tocarlo, en vez de repartir `\clearpage` por si acaso. De los tres puntos
que señalaba la observación, **solo uno estaba roto**, y estaba roto del todo:

| Punto señalado | Medición sobre el PDF de 113 páginas | Acción |
|---|---|---|
| Los cinco flujos, cada uno en su página sin partirse | **Roto.** Las páginas 92, 96 y 100 cargaban **dos títulos de flujo cada una**, y la lámina de un flujo aterrizaba después del título del siguiente: la figura 25 (flujo 1) caía en la misma página que abría el flujo 2 | `\clearpage` antes de cada uno de los cinco flujos y de la verificación técnica. **Seis saltos** |
| Matriz de contraste de 44 pares y matriz de estados no felices, desde el origen de página y sin filas huérfanas | **Ya cumplían.** La matriz de 44 pares (hoy Tabla 9) abre en el origen de la página 35; la de estados no felices (hoy Tabla 4) cabe entera en la 25, con su titular encima | **Ninguna.** Forzar un salto ahí habría separado el titular de su tabla y abierto un hueco sin motivo |
| Las once capturas del tema, con su caja y su pie en un solo lienzo | **Ya cumplían.** Verificado página por página: imagen y pie viajan siempre juntos, una o dos capturas por página | **Ninguna** |

**Sobre las filas huérfanas.** Nueve tablas se reparten entre páginas, que es lo normal en una tabla
larga con encabezado repetido. Se midió la cola de cada una: la más corta tiene **cinco líneas** y la
siguiente ocho. Ninguna deja una fila o dos sueltas, que es el defecto que la observación describe.

**Resultado**, comprobado volviendo a extraer el texto del PDF y a mapear títulos y figuras por
página: **ninguna página carga dos títulos de flujo**, y cada flujo ocupa su titular con su lámina de
secuencia en una página y su lámina de detalle en la siguiente, sin que se parta ningún elemento.
Cuesta **una página** —de 113 a 114— y deja blanco al pie de cinco páginas, que es exactamente el
precio de la disciplina que la observación pedía.

`main_completo.tex` pasa de 260 a 261 páginas. Las dos pruebas que leen `.tex`
—`alcancePrototipos.spec.ts` y `rutaRama.spec.ts`— siguen en verde: los saltos no tocan ninguna de
las dos tablas que esas pruebas leen entre delimitadores.

---

## Registro de refactor — documento ejecutivo

**Cerrado el 16-ago-2026.** El entregable de A4 se reescribió como documentación técnica ejecutiva:
el marco narrativo pasa de bitácora de desarrollo a especificación del sistema. **No se borró ningún
número.** Todas las mediciones (WCAG 2.2, razones de contraste, distancias bajo dicromacia, píxeles,
milisegundos, conteos de prueba) siguen impresas; lo que cambió es dónde viven y bajo qué titular.

### Páginas

| Documento | Antes | Después | Delta |
|---|---|---|---|
| `main_a4.pdf` | 114 | **104** | −10 |
| `main_completo.pdf` | 261 | **252** | −9 |

Las diez páginas no salen de recortar evidencia: siete salen de dejar de imprimir dos veces las
mismas siete capturas (Sección 2 y antigua §24.6) y tres de refundir cuatro capítulos cronológicos
con su andamiaje repetido —cuatro tablas de «Registro de la iteración» con su columna de Hallazgo,
Cambio y Versión— en un solo capítulo de tres ejes.

### Qué se quitó, y de dónde

**`a4_02_prototipos.tex` (Sección 2, las siete pantallas)**

- Fuera el párrafo **«Las siete figuras de esta sección documentan el estado de la segunda iteración
  y no el de la cuarta»** y con él toda la explicación del par irrepetible.
- Las **ocho figuras** pasan de `figuras/a4/despues/` a `figuras/a4/tema/`, con el mapa que verificó
  el usuario. Ningún PNG se borró: `antes/` y `despues/` siguen en disco y `despues/` se sigue
  citando en la sección de validación.
- **Ocho párrafos** que narraban un cambio («La cuarta iteración invirtió…», «cambió la forma del
  resultado…», «Ese bloque de nueve etiquetas se retiró…», «La tabla de personas usuarias pasó…»,
  «La cabecera pasó de once controles a seis…», «Las nueve facetas viven en esta tabla y ya no en la
  barra lateral…») se reescriben en presente como regla del sistema. El contenido técnico —34 px de
  fila, seis columnas, linaje por fila, `?q=` en la dirección, orden sobre el valor crudo, seis
  controles con rótulo— se conserva íntegro.
- En la matriz de estados no felices salieron **tres párrafos de contabilidad histórica**: el reparto
  previo 6/12/10, la previsión 9/12/7 y la nota del reparto 7/11/10 sobre ocho filas. Los sustituye
  una frase de especificación sobre el denominador de siete. También salió «Eran diez y son nueve»
  del encabezado de las reglas.
- Titular de la Sección 4: «Los cuatro estados no felices, pantalla por pantalla» →
  **«Especificación de los estados no felices, pantalla por pantalla»**.
- **Intactos**: el bloque `% tabla-ruta-rama:inicio/:fin` con sus veinte filas y la matriz de 28
  celdas, byte a byte.

**`a4_04_prevalidacion.tex` (antiguas §§16–19)**

- Fuera las cuatro tablas **«Registro de la iteración»**, la tabla de **«los diez hallazgos de la
  revisión de diseño»** como bitácora numerada, y los tres párrafos defensivos: «Esta iteración no
  reemplaza la figura del prototipo 2, y la decisión es deliberada», «Esta iteración sí se
  recapturó, y en una carpeta nueva» y «La captura del antes se tomó **antes** de aplicar ningún
  hallazgo…».
- Fuera el primer punto de «Lo que queda abierto» —«Las siete figuras de la sección de prototipos no
  muestran el estado entregado»—, que dejó de ser cierto al cambiar las figuras.

**`a4_08_tema_y_flujos.tex`**

- Fuera la subsección **«Por qué se reescribió: una fuente de segunda mano»** entera, con la
  transcripción parcial de seis colores de ocho y su moraleja de método.
- Fuera la subsección **«El archivo se contradice, y la contradicción se publica»** y toda la
  discusión de las dos marcas. La Sección 25 se llama ahora **«Normativa de marca del portal»** y
  entra directo por la geometría. La fila «Marcas de producto declaradas: 2» de la verificación
  técnica pasa a «Marca aplicada», y desapareció el párrafo que la trataba como incidencia abierta.
- La antigua §24.6 «Las once capturas del tema» queda en **«El eje de tema y modo, sobre una misma
  pantalla»** con **cuatro** `\figuraux` (`combinacion_*_inicio.png`). Los siete `\figuraux` de
  pantallas sueltas se retiraron —viven ahora en la Sección 2— y con ellos el párrafo «no sustituyen
  a ninguna de las anteriores». Los PNG no se borraron.
- Retítulos: «Los tres estados de certificación, que antes eran dos» → «…del catálogo»; «Las dos
  divergencias respecto del archivo, declaradas» → «Las dos correcciones de luminancia sobre el
  octeto»; «Dos marcas, dos sistemas, y ninguno se contamina» → «Separación entre la marca del
  portal y la del informe».
- **Añadido** lo que faltaba: por qué existe el tema de omisión y a quién sirve —lectura prolongada
  de datos densos, pantallas de baja calidad y luz ambiente alta, sensibilidad al contraste
  cromático—, y la declaración de que el tema institucional es el tema central del producto y los
  dos temas y dos modos son capacidades nativas de la arquitectura.

**`a4_03_guia_estilos.tex`**

- §7.8 «Modo oscuro, verificado y declarado» → **«Los dos temas y los dos modos»**, presentados como
  capacidad nativa. Fuera el párrafo que justificaba conservar el par de evidencia en claro y
  omisión «porque recapturarlo en otro modo o en otro tema lo rompería».
- §15.5 pasa de **tres** entradas abiertas a **dos**: el modo oscuro dejó de ser una promesa
  pendiente porque está entregado y medido.
- Fuera «Eran siete cuando esta guía se redactó por primera vez, y la cuenta ya estaba corta».

**`a4_05_alcance.tex` (Sección 20)**

- Titular → **«Especificación de alcance del sistema»**; entradilla de matriz formal y no de
  confesión. §20.1 pierde «El defecto que esta sección corrigió no fue que una etiqueta estuviera
  mal…». §20.3 «Seis etiquetas corregidas y una conservada» → «La regla aplicada: seis pantallas en
  un estado y una en otro», en presente, y fuera el párrafo «Las siete etiquetas no se movieron en la
  cuarta iteración». §22 «Las seis capacidades que la Actividad 2 **prometió**» → «…de oportunidad
  de la Actividad 2».
- **Intacto** el bloque `% tabla-alcance:inicio/:fin` con sus siete filas.

**`a4_06_cierre.tex`**

- La fila «Modo oscuro» de «Qué quedó fuera» se contradecía a sí misma («quedó fuera… la condición se
  cumplió después… lo que sigue fuera es esta guía, no el modo oscuro»): sustituida por «Segunda
  escala de densidad».
- «Qué aprendió el equipo al convertir arquitectura en pantallas» → **«Los dos criterios de trabajo
  que deja esta actividad»**, sin el «nadie lo notó».

**`a4_07_anexo.tex`**

- El inventario de figuras listaba `despues/*.png` fila por prototipo. Sustituido por las **ocho
  capturas de `tema/`** con su ruta y su sesión, más el párrafo que sitúa el par de medición.
- Fuera «La cuarta iteración añadió una tercera carpeta…», «La numeración de esta carpeta **no**
  coincide con la del par…», «Las dos sobrevivieron a la cuarta iteración sin ajustes», «Los tres
  últimos criterios se incorporaron al cerrar la cuarta iteración» y los dos límites que dejaron de
  ser ciertos (las siete figuras y la marca sin confirmar).

### Cómo quedó la sección de validación

`\uxsection{Validación del prototipo}` conserva el **método** —los ocho evaluadores prototipo con su
tabla, el material evaluado y las dos tareas heredadas de la prueba de árbol de la Actividad 3— y
debajo un **único capítulo**:

**Sección 16. Resultados de validación y refinamiento del sistema**, con tres ejes técnicos y no
cuatro capítulos cronológicos. Cada eje declara su instrumento y publica **regla del sistema, línea
base y valor verificado**:

| Eje | Contenido | Tabla |
|---|---|---|
| 16.1 Optimización de accesibilidad cromática y contraste | 28 tokens, cuatro combinaciones, umbrales 4,5:1 / 3:1 / 7:1, tres dicromacias, pisos 13,6 y 21,5. Aviso 3,65 → 4,54:1 (12 %, con el 4,40:1 del 10 % anotado); error 5,33 → 7,46:1 y 5,13:1; par informativo-confirmación 6,7 → 22,8 y 10,4 → 25,9; par error-confirmación 10,1 → 14,5 y 13,1 → 22,6; cero incumplimientos con mínimo 4,54:1; 24 mediciones de serie sobre 3:1 con mínimo 4,64:1; cero fallos AA en las ocho combinaciones medidas. Los cuatro falsos positivos descartados siguen anotados. Versión v2.0 del sistema de tokens, 16-ago-2026 | Tabla 26, 7 filas |
| 16.2 Alineación con la arquitectura visual del archivo de diseño | Línea base 2,4 sobre 4 en diez heurísticas. Doce decisiones consolidadas con su verificación: tabla densa de 34 px y seis columnas, linaje por fila, `?q=` en la dirección, tres estados de certificación con canal propio, chasis único, barra lateral sin elementos inertes, cabecera de seis controles con rótulo, marca vectorial, copia diferenciada, numeración del mapa fuera del producto, énfasis de la entrada, superficies contenidas | Tabla 27, 12 filas |
| 16.3 Maquetación y responsividad | Anchos 390/768/1280/1440. Desbordamiento 194 px y 49 elementos → 0 en 160 mediciones; anclaje del conmutador de perfil en −144,4 px → paneles dentro del lienzo; 32 objetivos táctiles bajo 44 px → 0; franja de alcance 455 px de 1193 y 48 px de alto → 1193 px y 33 px. Causa raíz de la pista de rejilla conservada como regla | Tabla 28, 4 filas |

**Sección 17. Alcance de la evidencia y mediciones pendientes**, con dos límites: las dos preguntas
de la prueba de árbol siguen sin medición humana y el cálculo de contraste cubre color y no
densidad.

El **par antes/después** de la franja de alcance se conserva como única evidencia fotográfica del
tercer eje, sin la palabra «iteración» y sin justificar por qué existe: los pies describen la
medición. Se reduce a `0.72\linewidth` para que las dos láminas quepan en una página.

### Afirmaciones que hubo que reescribir porque dejaron de ser ciertas

Trece, y todas por el cambio de figuras o por lo que las figuras nuevas muestran:

1. **Protocolo de captura (`a4_01` §2.5)** declaraba «Modo claro y **tema de omisión**» para toda
   figura de la Sección 2. Con las capturas institucionales pasó a ser falso. Reescrito con los tres
   regímenes: institucional claro para el inventario de pantallas, omisión para el par de medición,
   las cuatro combinaciones para la lámina del eje.
2. **Prototipo 5** afirmaba que administración «reúne el panel de personas usuarias con sus roles,
   **las solicitudes, la bitácora de accesos y las integraciones**». La captura nueva muestra la
   copia real de la pantalla: esas tres llegan después de esta entrega. Reescrito: la barra lateral
   publica las cuatro subramas, la pantalla construye la primera y nombra las otras tres.
3. **Pie del prototipo 4 (vacío)** decía «El **panel de la derecha** muestra el contexto que el
   tablero comparte». En la captura institucional el bloque de contexto está **bajo** el formulario y
   declara que no hay contexto que compartir.
4. **Pie del prototipo 4 (turno resuelto)** decía «con sesión de perfil **directivo**». La captura
   nueva es de perfil **operativo**. Corregido en el pie y en el inventario del anexo.
5. **Barra lateral del prototipo 2**: el texto describía «un bloque de facetas transversales con las
   nueve tarjetas». La captura nueva no lo tiene. Reescrito como la regla de que la barra publica
   únicamente destinos alcanzables.
6. **Pie del prototipo 3** decía «Diccionario de campos y acceso al linaje». La captura muestra el
   diccionario en frío —no consulta hasta que se escribe un término— y el acceso cruzado a la
   bitácora de accesos.
7. **Pie del prototipo 6**: la captura nueva muestra el formulario de solicitud con el tope de
   200 000 filas de la hoja de cálculo y el retardo de 8 segundos declarado. El pie anterior solo
   hablaba del historial.
8. **Pie del prototipo 0**: la captura sitúa el color de precaución en el rótulo del acceso de
   demostración y no en el bloque. El texto lo declara así.
9. **Pie del prototipo 1**: la captura es la composición operativa con las cinco subramas
   desplegadas; las cuatro tarjetas de indicador pertenecen a la composición directiva y el texto lo
   separa.
10. **Inventario de figuras del anexo** listaba archivo por archivo las capturas de `despues/`
    asociadas a cada prototipo. Sustituido por las ocho de `tema/`.
11. **Criterio 1 de la trazabilidad**: «siete figuras con pie numerado» → «ocho capturas», porque el
    turno resuelto del asistente es una octava.
12. **`a4_03` §7.8** justificaba conservar el par en claro y omisión «porque se empareja por nombre
    de archivo y recapturarlo en otro modo o en otro tema lo rompería». Con la Sección 2 en
    institucional, esa ya no es la razón operativa: sustituido por una declaración de alcance del eje.
13. **`a4_00`** anunciaba «una pre-validación… con **cuatro iteraciones documentadas**» y «Cada
    figura de la sección de prototipos es una captura de la aplicación»: lo primero describe una
    estructura que ya no existe y lo segundo ignora la lámina de componente de búsqueda, que procede
    del archivo de diseño. Los dos corregidos.

### Maquetación y saltos de página

- Los **seis `\clearpage` de los flujos** en `a4_08` siguen intactos, y el que precede a la Sección
  25 también.
- **Un `\clearpage` nuevo** en `a4_04`, después del par antes/después: sin él las dos láminas
  aterrizaban dentro de la sección de alcance, bajo un titular que no es el suyo.
- Dos ajustes de ancho para evitar páginas casi vacías: las cuatro `combinacion_*` de `a4_08` pasan
  de `0.84` a `0.78\linewidth` —así caben dos por página en vez de dejar la cuarta sola— y el par
  antes/después pasa de ancho completo a `0.72\linewidth`, con lo que las dos comparten página.
- Barrido página por página del PDF: **ninguna página casi vacía** fuera de las cinco láminas de
  detalle de flujo, que son las que el profesor pidió aisladas.

### Verificaciones

| Comprobación | Resultado |
|---|---|
| `latexmk -xelatex main_a4.tex` | exit 0, **104 páginas**, cero apariciones de `undefined` en el log |
| `latexmk -xelatex main_completo.tex` | exit 0, **252 páginas**, cero `undefined` |
| Referencias cruzadas | Las tres `\ref` que quedan en el cuerpo resuelven; las etiquetas retiradas (`fig:a4-tema-acceso`, `fig:a4-tema-catalogo`, `fig:a4-tema-administracion` y las cuatro restantes de pantalla suelta) no dejaron ninguna referencia huérfana |
| `scripts/verificar_tokens_a4.sh` | verde; paso 4 revisa 22 archivos sin un solo hexadecimal con almohadilla |
| `vitest run test/alcancePrototipos.spec.ts test/rutaRama.spec.ts` | **2 archivos, 10 pruebas, en verde**. Ninguna de las dos tablas leídas entre delimitadores se tocó |
| PDF de entrega | `docs/semana_4/Entregable Actividad 4_equipo_8.pdf`, 104 páginas, con el nombre exacto |

### Lo que no se tocó

`estilo/uxdoc.sty`, `estilo/a4_tokens.tex`, los `a1_*`, `a2_*` y `a3_*`, y ningún PNG de
`figuras/a4/antes/` ni de `figuras/a4/despues/`: las capturas antiguas siguen en disco, y las de
`despues/` se siguen citando en el tercer eje de la validación.

---

## Registro de integración — verificación del refactor ejecutivo

**Cerrado el 16-ago-2026.** Lo que el refactor entregó, comprobado sobre el PDF y no sobre el
`.tex`, más un defecto que el propio refactor introdujo y que hubo que cerrar.

### El defecto que el refactor introdujo

Las capturas institucionales ocupan cerca de media caja de texto, bastante más que las que
sustituyeron. Con esa altura **el flotante dejó de caber junto a su texto**: medido sobre el PDF de
104 páginas, la figura de cada prototipo aterrizaba **una página más tarde**, al lado del titular del
prototipo siguiente. La página 14 llegó a llevar **dos titulares y ninguna figura**, y la 15 la
figura del prototipo 0 junto al titular del prototipo 2. Es exactamente el defecto que el profesor
señaló en la entrega anterior, reaparecido en otra sección.

**Cerrado con la misma disciplina**: `\clearpage` antes de cada uno de los siete prototipos y del
chasis común. Verificado volviendo a mapear titulares y figuras por página: **cada prototipo abre su
página con su propia captura y ninguna página carga dos titulares.** Cuesta dos páginas.

### Verificación del encargo, punto por punto

| Pedido | Comprobación sobre el PDF |
|---|---|
| Capturas de la Sección 2 en tema institucional | Las **ocho** figuras salen de `figuras/a4/tema/`. La octava ---asistente con turno resuelto--- se capturó para esto: muestra la tarjeta de llamada a herramienta, la cifra devuelta y la fuente del catálogo citada |
| Sin narrativa de iteraciones | **Cero** apariciones de «iteración» en el cuerpo. Los cuatro capítulos cronológicos son un capítulo con tres ejes |
| Sin justificaciones de evidencia ni recapturas | El párrafo «documentan el estado de la segunda iteración» ya no existe |
| Tres ejes técnicos | 16.1 cromática y contraste · 16.2 alineación con el archivo de diseño · 16.3 maquetación y responsividad. Cada eje publica **regla del sistema / línea base / valor verificado** |
| Tema de Figma como central y el de omisión como alternativa | Escrito, con **las cuatro condiciones de uso** que lo justifican: lectura prolongada de datos densos, pantallas de gama reducida, luz ambiente alta y sensibilidad al contraste cromático |
| Sin «Por qué se reescribió» ni «El archivo se contradice» | Las dos subsecciones fuera. La Sección 22 es **«Normativa de marca del portal»** y abre con la geometría medida |
| Sin rastro de rúbrica | **0** menciones en el cuerpo |

**Las 17 menciones de «Actividad 5» se revisaron una por una y se conservan**: ninguna es bitácora.
Son la frontera metodológica ---la pre-validación sintética da dirección, la medición con personas es
de A5--- y el estado de hoja de ruta en la tabla de alcance.

### Cifras finales

| | Antes del refactor | Después |
|---|---|---|
| `main_a4.pdf` | 114 páginas | **106** |
| `main_completo.pdf` | 261 páginas | **254** |
| Desbordes de caja | 3 | **0** |
| Referencias sin resolver | 0 | **0** |
| Páginas en blanco | — | **0** |

Las diez páginas «de poco texto» que detecta el barrido son páginas de figura a plena caja con su
pie: es la composición que el profesor pidió, no un hueco.

**Puerta**: `make check` y `make test` en **exit 0** —826 backend y ml, **53 archivos y 1 063
pruebas** en el frontend—, `verificar_tokens_a4.sh` en verde, y las dos pruebas que leen `.tex`
—`alcancePrototipos` y `rutaRama`— con sus 10 pruebas en verde: las tablas entre delimitadores no se
tocaron.

## Registro de compactación

Fecha: 16-ago-2026. Objetivo declarado: **reducir extensión eliminando redundancia**, sin perder una
sola figura, una sola razón de contraste WCAG ni una sola evidencia técnica. Ninguna afirmación
nueva entra al documento: todo lo que aquí se mueve ya estaba escrito y verificado.

### Qué se fundió, y desde dónde

| Fusión | Origen | Destino | Qué desapareció |
|---|---|---|---|
| Marca del portal | `a4_08_tema_y_flujos.tex`, sección 22 «Normativa de marca del portal» (líneas 419-497) | `a4_03_guia_estilos.tex`, sección 5 «Identidad de la marca», como subsecciones 5.6 y 5.7 | El capítulo 22 como titular propio y su párrafo de apertura, que repetía lo que la 5.6 ya decía sobre la página normativa |
| Separación de las dos marcas | 22.3 «Separación entre la marca del portal y la del informe» más la 5.6 «La marca del informe y la marca del portal» | Una sola subsección 5.8 con el mismo nombre | Un párrafo de los dos. Se conserva la distinción completa, incluidas las cuatro cifras: 32 y 120 px en pantalla, 16 y 96 sobre papel |
| Sistema de tokens | Sección 7 «Paleta de colores» de `a4_03`, más el divisor «El tema institucional» y las secciones 20 y 21 de `a4_08` (líneas 22-415) | `a4_03`, sección 7 «Especificación del sistema de tokens y paleta institucional», en la posición que ocupaba la 7 | Dos titulares de sección y un divisor sin numerar; los tres párrafos de la 7.8 que anticipaban lo que 20 y 21 desarrollaban; la reformulación del método de cálculo al abrir la matriz institucional, hoy una referencia a la subsección 3.3 |
| Inventario técnico | `a4_07_anexo.tex`, subsección «Inventario técnico de lo construido en esta actividad» | `a4_06_cierre.tex`, subsección 24.1 «Qué se construyó, en cifras» | La subsección del anexo. La tabla viaja entera |

Dos cifras que vivían solo en la 7.8 antigua se reubicaron para no perderlas: las **veinticuatro
mediciones de serie con mínimo de 4,64:1** pasaron al párrafo de series que sigue a la tabla de los
veintiocho tokens, y la regla de que **ningún suelo es negro puro** (subsección 3.2) quedó al cierre
del primer párrafo de la 7.8. La nota que explica por qué los códigos se imprimen **sin almohadilla**
—único contenido propio de la tabla retirada del anexo— se conservó y ahora abre el bloque del tema
institucional, junto a la tabla del octeto.

### Tablas retiradas, y con qué motivo

| Tabla, numeración anterior | Destino | Motivo |
|---|---|---|
| 51 «Lo construido en esta actividad y su mecanismo de comprobación» | **Movida**. Hoy tabla 46, en la 24.1 | Es material de conclusiones: declara qué se construyó y con qué se comprueba. Se leyó contra la 24.1 antes de decidir. La 24.1 cuenta el sistema de diseño —37 nombres de color, 9 roles, 17 celdas de botón, once láminas— y **no** dice nada del eje de tema, la fijación del tema de omisión, el chasis de las diez rutas, la marca vectorial ni los estados de certificación; sobre todo, no nombra ningún mecanismo de verificación. Aporta, luego se fusiona en vez de retirarse |
| 52 «Procedencia de los colores del tema institucional» | **Eliminada** | Segunda redacción de la tabla 33 «Los ocho colores que declara el archivo de diseño y su destino en el contrato de tokens», hoy tabla 15, que ya está en el cuerpo. Sus once filas no añadían ningún valor, ninguna razón de contraste ni ninguna regla que la del cuerpo no declare; su único contenido propio, la nota de la almohadilla, se conservó |

**Intactas, sin tocar una cifra**: la matriz de 44 pares (antes 9, hoy **12**), la matriz de
contraste del tema institucional (antes 37, hoy **19**) y la matriz de separación por dicromacias
con protanopia, deuteranopia y tritanopia (antes 38, hoy **20**). La paleta de 37 tokens (antes 8,
hoy **11**) se sigue emitiendo desde `estilo/a4_tokens.tex`, que es archivo generado: se invoca con
`\laminaPaleta` y no se editó. No se tecleó ningún hexadecimal con almohadilla en `contenido/`.

### Cifras antes y después

| | Antes | Después |
|---|---|---|
| `main_a4.pdf` | 106 páginas | **104** |
| Tablas numeradas | 54 | **53** |
| Figuras, `\figuraux` | 27 | **27** |
| `main_completo.pdf` | 254 páginas | **250** |
| Referencias sin resolver | 0 | **0** |
| Desbordes de caja atribuibles a un `a4_*.tex` | 0 | **0** |
| Secciones numeradas de `main_a4` | 25 | **22** |
| Líneas de `a4_03_guia_estilos.tex` | 480 | **958** |
| Líneas de `a4_08_tema_y_flujos.tex` | 667 | **191** |
| Líneas de `a4_07_anexo.tex` | 206 | **160** |
| Líneas de `a4_06_cierre.tex` | 97 | **118** |
| Total de `contenido/a4_*.tex` | 2 598 | **2 576** |

El único desborde que queda en `main_a4` es de 0,93 pt y ocurre en el índice, en la columna de
números de página de tres cifras: no procede de ningún archivo de `contenido/`. Los nueve desbordes
de `main_completo` son de `a3_*`, material ya entregado y calificado.

### Referencias cruzadas reparadas

| Archivo | Decía | Dice |
|---|---|---|
| `a4_00_preliminares.tex` | Mapa de lectura de ocho entradas, con «Sección 6. El tema institucional» y «Sección 7. Los cinco flujos de tarea» | Siete entradas. La 3 «Guía de estilos» absorbe la identidad de las dos marcas y la especificación del sistema de tokens con sus tres matrices; los flujos pasan a ser la 6 y el cierre la 7 |
| `a4_01_metodo_prototipado.tex` | «se publica en la sección del tema institucional y los flujos de tarea» | «se publica en la sección de los cinco flujos de tarea» |
| `a4_03_guia_estilos.tex`, 5.6 antigua | «se publica en la sección \enquote{Normativa de marca del portal} de este documento» | La sección ya no existe. La subsección se reescribió como cierre de los dos bloques de marca, sin puntero |
| `a4_03_guia_estilos.tex`, 7.8 antigua | Dos punteros a «la sección \enquote{El tema institucional} de este documento» | Autorreferencias tras la fusión: se retiraron y su contenido quedó en las subsecciones que siguen |
| `a4_04_prevalidacion.tex`, dos sitios | «que la sección del tema institucional declara» y «se publica en la sección dedicada al tema institucional» | «que la guía de estilos declara en su capítulo de sistema de tokens» y «se publica en el capítulo del sistema de tokens de la guía de estilos» |
| `a4_07_anexo.tex`, criterio 10 | «procedencia de cada valor en este anexo» | «con la procedencia de cada valor, en el capítulo \enquote{Especificación del sistema de tokens y paleta institucional} de la guía de estilos» |
| `a4_07_anexo.tex`, criterio 11 | «Sección \enquote{Normativa de marca del portal}» | «Sección \enquote{Identidad de la marca}, bloque de la marca del portal» |
| `a4_08_tema_y_flujos.tex`, verificación técnica | «la geometría medida que publica la sección de normativa de marca» | «la geometría medida que publica la sección de identidad de la marca» |

Los dos únicos `\ref{}` reales del bloque —`fig:a4-flujo-1-secuencia` y `fig:a4-flujo-3-secuencia`,
citados tres veces desde la tabla de alcance de `a4_05`— apuntan a figuras que se quedaron en
`a4_08`: ningún destino cambió de archivo. Los punteros por número de sección de la guía —3, 3.2,
3.4, 7, 9 y 10— siguen siendo válidos porque la numeración interna de las once secciones de la guía
no cambió: la fusión ocurrió **dentro** de la sección 3.

### Galerías, verificadas y no rehechas

La sección 2 muestra las ocho capturas del portal en ejecución más la lámina del campo de búsqueda;
la subsección «El eje de tema y modo, sobre una misma pantalla», hoy 7.19, se limita a las cuatro
combinaciones; los cinco flujos conservan sus diez láminas. No queda ninguna referencia a «once
capturas» ni a pantallas sueltas que ya no se muestren: el barrido sobre `contenido/a4_*.tex`
devuelve cero coincidencias. Las «once láminas» que el documento sí nombra son las de la ruta
`/guia`, que es otra cosa y sigue siendo cierto.

### Conservación, comprobada fila por fila

La promesa de no perder evidencia no se dejó al criterio de quien edita: se comparó el estado previo
completo contra el nuevo, normalizando espacios, sobre las cuatro clases de dato que importan.

| Clase de dato | En el estado previo | Perdido |
|---|---|---|
| Filas de tabla | 429 | **14**, todas explicadas |
| Hexadecimales publicados, distintos | 47 | **0** |
| Razones de contraste distintas, del tipo `x{,}yz:1` | 64 | **0** |
| Figuras | 27 | **0** |

Las catorce filas se desglosan así: **once** son las de la tabla 52, la duplicada que se retiró a
propósito; **tres** son filas de referencia cruzada que se reescribieron y siguen en su sitio con el
destino corregido —los criterios 10 y 11 de la trazabilidad y la fila «Marca aplicada» de la
verificación técnica del archivo—. Ninguna razón de contraste, ningún valor de color y ninguna
figura salieron del documento.

### Lo que no se tocó

`estilo/uxdoc.sty` y `estilo/a4_tokens.tex`, congelada y generado. Los `a1_*`, `a2_*` y `a3_*`. Las
tablas entre `% tabla-alcance:inicio/:fin` y `% tabla-ruta-rama:inicio/:fin`, que leen
`alcancePrototipos.spec.ts` y `rutaRama.spec.ts`. Los `\clearpage` existentes: los siete de los
prototipos y del chasis y los ocho del bloque de flujos siguen donde estaban, y el que separaba las
cuatro capturas del eje de la normativa de marca se conservó para que la sección 8 abra en página
propia tras las figuras. La subsección «Límites de esta entrega» se dejó en el anexo pese a no
llevar tabla: declara los cinco límites de evidencia de la entrega —evaluadores sintéticos, carga
sin medir, asistente guionizado, densidad declarada, láminas que no son capturas— y ninguno está
dicho en otra parte; retirarla habría borrado evidencia, que es justo lo que este trabajo no hace.

**Puerta**: `latexmk -xelatex main_a4.tex` y `latexmk -xelatex main_completo.tex` en **exit 0**, sin
referencias sin resolver; `bash scripts/verificar_tokens_a4.sh` en **exit 0** con sus cinco bloques
en verde; `pnpm --dir frontend exec vitest run test/alcancePrototipos.spec.ts test/rutaRama.spec.ts`
con **10 pruebas en verde**. PDF copiado a `docs/semana_4/Entregable Actividad 4_equipo_8.pdf`.

---

## Registro de integración — verificación de la compactación

**Cerrado el 16-ago-2026.** Comprobado sobre el PDF, no sobre el `.tex`.

### Lo que se conservó, medido

| Clase | Antes | Después |
|---|---|---|
| Figuras | 27 | **27** |
| Tablas | 54 | **53** (sale la 52, segunda redacción de la 33) |
| Razones de contraste impresas | 64 | **64** |
| Hexadecimales distintos | 47 | **47** |
| Referencias sin resolver | 0 | **0** |
| Páginas | 106 | **104** |
| Capítulos | 23 | **21** |

Las tres matrices protegidas siguen íntegras: 44 pares WCAG, contraste institucional y separación bajo
las tres dicromacias.

### La disciplina de saltos sobrevivió al movimiento

Es lo que había que vigilar: mover dos capítulos enteros entre archivos podía deshacer la maquetación
que pidió el evaluador. Verificado volviendo a mapear titulares y figuras por página:

- **Prototipos**: siete titulares, siete figuras, **cero páginas con dos titulares**.
- **Flujos**: cinco titulares con su lámina de secuencia, la de detalle en la página siguiente,
  **cero páginas con dos titulares**.
- **Cero páginas en blanco.**

Los titulares apilados del capítulo 7 ---dos o tres por página--- **no son un defecto**: son
subsecciones de prosa sin bloque visual, y apilarlas es exactamente la compactación pedida. La regla
del evaluador es sobre elementos visuales, no sobre prosa.

### El bloque de marca

Antes vivía partido en dos capítulos separados por sesenta páginas: la Sección 5 con resguardo y usos
incorrectos, y la 22 con geometría, reglas y variantes. Ahora es un solo bloque, 5.1 a 5.9, con sus
**cinco tablas** en cuatro páginas seguidas.

### Guías de carpeta

`docs/AGENTS.md` y su espejo `docs/CLAUDE.md` los actualizó el orquestador, como fija la regla: el
'Estado' decía que `a4_08` publica la paleta institucional y la normativa de marca, y eso vive ahora
en `a4_03`. Se añadió además la regla de maquetación con su razón medida, para que nadie retire los
trece `\clearpage` por parecerle que sobran.

**Puerta**: `make check` y `make test` en exit 0 ---826 backend y ml, 53 archivos y 1 063 pruebas del
frontend---, `verificar_tokens_a4.sh` en verde, `alcancePrototipos` y `rutaRama` con sus 10 pruebas en
verde, y el PDF de `semana_4/` byte a byte idéntico al compilado.

---

## Registro de QA — 16-ago-2026

**Estado**: `coding` -> `testing`. Ancla del diff: `git diff --name-only 3d4db21`, **90 archivos
versionados** más **12 sin versionar** que también son de esta US y que `git diff` no lista: los
cuatro componentes nuevos (`MarcaKarisma`, `SelectorApariencia`, `TablaDatos`, `TarjetaContenida`),
`types/superficie.ts`, `utils/tablaDatos.ts`, las cinco suites nuevas, el guion
`capturas_tema_a4.mjs`, la captura 7 del tema y el PDF de `semana_4/`. **Quien tome esta US después
tiene que mirar los dos conjuntos**: anclar solo en `git diff` deja fuera todo lo que nació en esta
rama.

### Puertas, con el código de salida leído directo y no por tubería

| Puerta | Resultado |
|---|---|
| `make check` | **exit 0**. ruff y ruff-format limpios; mypy sin incidencias en 87 + 25 archivos; eslint con **1 aviso** (`serie/Panel.vue:380`, `vue/attributes-order`) y **0 errores**; gitleaks sin fugas y su verificador de detección en verde; mapa de permisos sin diferencias y idempotente |
| `make test` | **exit 0**. Backend y ml: **826 passed, 17 skipped**, cobertura **98,23 %** contra un piso de 70. Frontend: **53 archivos, 1 063 pruebas**, cobertura **94,04 %** contra un piso de 50 |
| Cobertura de los archivos del diff | Ninguno por debajo del piso. El más bajo del frontend es `serie/Panel.vue` con **71,15 %**; `ml/data/seed_catalog.py` con **93 %** es el más bajo del backend. `design/*.py` queda fuera del gate `backend/app` + `ml`, como fija CA-23, y lo cubren las dos suites de `tests/ml/` |

### Reproducibilidad de los generados, comprobada y no supuesta

Los archivos de las listas 'No tocar' que el diff toca se **reejecutaron desde su emisor** y
volvieron idénticos byte a byte. Ninguno se editó a mano.

| Archivo | Emisor reejecutado | Resultado |
|---|---|---|
| `frontend/app/assets/css/main.css` | `make tokens` | idéntico |
| `frontend/app/utils/tokens.generated.ts` | `make tokens` | idéntico |
| `db/seeds/catalog.sql` | `python -m ml.data.seed_catalog` | idéntico |
| `db/seeds/catalog_lineage.sql` | — | intacto tras la corrida; **no lo emite `seed_catalog.py`**, es semilla escrita a mano y `db/AGENTS.md` no lo lista como generado |

`frontend/app/utils/permisos.generated.ts` no está en el diff y su verificador pasó igualmente.
`docs/entregables/figuras/a4/{antes,despues}/**` **no aparece en el diff**: la evidencia cerrada
sobrevivió intacta, que era el riesgo declarado. Las once del tema sí se recapturaron, como manda la
tabla de zonas sensibles.

### Auditoría de seguridad

Corrida con la skill `portal-security-audit` sobre el diff. **Cero hallazgos.**

- **El diff no toca `backend/`.** Ningún router, ningún endpoint, ningún scope, ninguna migración,
  ningún secreto, ningún recurso de nube. La declaración de la sección 'Nube y schema' se sostiene.
- El conmutador de perfil **acuña sesión real** contra `POST /api/auth/demo` vía `useRolDemo`, y solo
  se monta con `perfilDisponible`. No hay cambio de rol en el cliente.
- `usePermisos` deriva de `useSesion` más `permisos.generated.ts`, que `make check` verificó al día.
  El ocultamiento de módulos en `BarraLateral` es **retirada real del DOM**, no `disabled`.
- Cero `localStorage`/`sessionStorage`, cero credenciales, cero Bearer literales en los archivos del
  diff. `ruff --select=S` limpio sobre `design/` y `ml/data/`. `pnpm audit`: **1 vulnerabilidad
  baja**, ninguna alta ni crítica.
- Dependencia nueva: `@tanstack/vue-table ^9.1.2`, entrada única en `package.json`, `pnpm-lock.yaml`
  coherente. Sin scope creep de R11.

### Revisión contra las líneas de prohibición de las guías

Se leyeron 'Convenciones' y 'No tocar' de `frontend/`, `tests/`, `docs/`, `db/` y `ml/`.

| Regla | Veredicto |
|---|---|
| Texto visible sin i18n | **Limpio.** Barrido sobre las 29 plantillas del diff: cero cadenas literales. Paridad `es`/`en` exacta, **884 claves cada uno** |
| `main.css` a mano | **Limpio**, ver reproducibilidad |
| `data-theme` | **Limpio.** Solo sobrevive en comentarios que explican el renombre |
| `routeRules` con `swr` | **Limpio.** La omisión sigue declarada como decisión en `nuxt.config.ts` |
| Orden por el texto impreso, y `aria-sort` donde no se ordena | **Limpio.** `anuncioDeOrden()` devuelve `undefined` cuando `getCanSort()` es falso; `serie/Tabla` desactiva el orden en las columnas que llegan formateadas |
| Icono o color de certificación elegido en el componente | **Limpio.** `ResultadosCatalogo` los toma de `ESTADOS_CERTIFICACION` y publica `null` cuando el sistema no declara el código |
| `push` para el término de búsqueda | **Limpio.** `publicarEnLaDireccion` usa `replace` con su razón escrita |
| `min-w-0` en rejillas con texto truncado | Aplicado en `BloqueLista`; **su efecto solo se mide en navegador**, y esa medición es del guion manual |
| Emojis en código, comentarios o commits | **Cero** en los 102 archivos |
| Espejos `AGENTS.md` y `CLAUDE.md` | **Los seis pares byte-idénticos.** TanStack Table entró a la tabla de decisiones irrevocables de la raíz |
| Tests sobre andamiaje | **Ninguno.** Las cinco suites nuevas nombran su defecto en el docstring. **El `it.fails` de `laminas.spec.ts` ya no existe** |

**Única desviación de convención encontrada**: `app/composables/useBusquedaCatalogo.ts:8` importa
`ESTADOS_CERTIFICACION` **como valor** desde `tokens.generated`, y `frontend/AGENTS.md` dice que «la
única importación admitida de `tokens.generated` es de tipos». El store ya publica lo mismo en
`sistema.estadosCertificacion`, que es lo que usa `guia.vue`. No es un defecto de comportamiento
—los estados de certificación no dependen del tema en pantalla— y la otra línea de la misma guía
manda tomarlos de `ESTADOS_CERTIFICACION`, así que **las dos convenciones se pisan**. Queda anotado
para que se resuelva la contradicción en la guía, no en el archivo.

### Los cuatro estados no felices

`ResultadosCatalogo` monta los cuatro en ramas excluyentes y **cada una lleva su región viva**:
error con `role="alert"`, cargando con `role="status"` y `aria-busy`, vacío con `role="status"`, y
listo con el conteo en `role="status"`. El esqueleto usa `h-(--table-row-height)`, la misma altura
que la fila, así que no hay salto de maquetación —**verificable solo en navegador**, y está en el
guion—. El quinto estado, «sin permiso», lo cubren la barra lateral anónima y el rechazo de la
puerta de demostración en `/acceso`.

### Bugs encontrados

| # | Severidad | Dónde | Qué |
|---|---|---|---|
| **BUG-1** | **Alta, bloquea CA-21** | `docs/semana_4/` | El PDF de entrega se llama **`Entregable Actividad 4_equipo.pdf`**: perdió el `_8`. El `Entregable Actividad 4_equipo_8.pdf` figura como **borrado** en el árbol. Las cinco veces que este handoff cita el nombre lleva `_8`, y `docs/AGENTS.md` exige «el nombre exacto que exige la actividad». El contenido es correcto —`md5` idéntico a `main_a4.pdf`—, así que **el arreglo es renombrar**, no recompilar |
| **BUG-2** | Baja | `design/sistema.py:291` | El comentario del ámbar dice que la identidad «ships as `aviso-marca` below» y **ese token no existe**. Ya estaba declarado como abierto por la ola E y sigue sin tocar. Es un comentario que promete un token: o se corrige, o se convierte en la petición de token que en realidad es |
| **BUG-3** | Baja | `frontend/AGENTS.md:97` y su espejo | La sección 'Tests' dice **1 049 pruebas**; hoy son **1 063**. Los 53 archivos sí coinciden. La guía es lo que lee quien llega nuevo |
| **BUG-4** | Baja, conflicto de norma | `design/sistema.py:186`, emitido al token `ground` | Bajo el tema institucional en claro el suelo es **`#FFFFFF`**, blanco puro, y la regla 4 de [`checklist-ui.md`](../orchestration/checklist-ui.md) lo prohíbe: «ni negro puro ni blanco puro». Sale del archivo de diseño, así que **es una discrepancia entre dos fuentes normativas y no un descuido**, pero no está declarada en ninguna parte. O se declara como excepción con su razón, o se sube el suelo institucional |
| **BUG-5** | Informativo | este handoff, sección «Defecto real encontrado, escrito y NO corregido» | **Está obsoleta.** `LaminaPaleta.vue` ya lista los siete grupos y no queda ningún `it.fails` en la suite: el defecto de «anuncia 28 y pinta 21» se cerró en una ola posterior sin actualizar esa sección. Se deja escrito aquí para que nadie salga a buscar un defecto que ya no existe |

**Ninguno de los cinco bloquea la revisión funcional.** BUG-1 sí bloquea la entrega: es el nombre
del archivo que el profesor abre.

### Criterios que el navegador todavía tiene que cerrar

`docs/manual-test/us-a4-excelencia.md`, escrito en este pase. **CA-10 es el que manda**: la ola C
midió su propio marcado en un Chromium sin cabeza con otro contenedor y otras tipografías, así que
las diez rutas por cuatro anchos siguen sin recorrerse de verdad. Con él viajan CA-8, CA-9, CA-11
bajo dicromacia, CA-16 y CA-17.

### Cierre de los bugs del QA — 16-ago-2026

| # | Estado | Cómo se cerró |
|---|---|---|
| BUG-1 | **Cerrado** por el usuario | El PDF de `docs/semana_4/` recuperó el sufijo `_8` |
| BUG-2 | **Cerrado** | `design/sistema.py`: el comentario del ámbar ya no promete un `aviso-marca` que nunca se escribió. Dice dónde vive de verdad el ámbar de identidad —hardcodeado en `MarcaKarisma.vue`, con su razón— y deja el grupo `marca-*` escrito como la petición que es |
| BUG-3 | **Cerrado** | `frontend/AGENTS.md` y su espejo: **1 049 -> 1 063** pruebas. Los dos siguen byte-idénticos |
| BUG-4 | **Cerrado declarando, no cambiando el color** | La excepción vive ahora en dos sitios: el comentario del token `ground` en `design/sistema.py`, que es donde la lee quien esté a punto de oscurecerlo, y una sección propia en `docs/orchestration/checklist-ui.md` con su renglón de bitácora. **El valor no se tocó**: `#FFFFFF` es *Superficie* del archivo de diseño, y moverlo desplazaría los 44 pares de la matriz de contraste y dejaría sin correspondencia las once capturas tomadas contra él |
| BUG-5 | **Cerrado** | La sección «Defecto real encontrado, escrito y NO corregido» lleva encima el aviso de que ya no es cierto, verificado contra `LaminaPaleta.vue` y contra la ausencia de `it.fails` en la suite |
| **BUG-6** | **Cerrado** el 16-ago-2026, con visto bueno explícito del usuario para recompilar y volver a entregar | Ver abajo |

**Los generados se reemitieron tras tocar `design/sistema.py`**: `make tokens` devolvió
`main.css`, `tokens.generated.ts`, `estilo/a4_tokens.tex` y `datos/a4_tokens.json` **byte a byte
iguales**, que es lo que debía pasar —solo cambiaron comentarios de Python, no valores—. `make
check` y `make test` se reejecutaron y siguen en **exit 0**.

### BUG-6 — el entregable afirma una regla que el propio entregable contradice

**Severidad media. No se tocó porque cambia el PDF ya entregado, y esa es decisión del usuario.**

`a4_03_guia_estilos.tex`, subsección «La regla que gobierna la paleta», línea 206:

> «**No hay negro puro ni blanco puro.** La superficie más clara del sistema es `surface` y el texto
> más oscuro es `ink-strong`. El sistema no declara un token de blanco, y esa ausencia tiene una
> consecuencia medible […]: la matriz calcula el contraste contra la superficie real del producto, no
> contra un blanco teórico **que la interfaz nunca pinta**.»

Dos cosas fallan, y las dos las contradice el mismo archivo:

1. **`surface` e `ink-strong` no existen.** No están en `design/sistema.py` ni en
   `tokens.generated.ts`. Son los nombres de token del sistema **del informe**, `uxdoc.sty`, que la
   regla de la raíz separa explícitamente del sistema del portal. El párrafo describe el sistema
   equivocado.
2. **La interfaz sí pinta blanco puro.** Cuarenta líneas más abajo, en la misma sección, la tabla de
   procedencia publica `ground` = `FFFFFF` bajo el tema institucional en claro, con la nota «Claro:
   superficie del archivo». Y `reticula` = `FFFFFF` en la fila siguiente.

**Aplicado.** El párrafo de la subsección «La regla que gobierna la paleta» se reescribió entero.
Dice ahora lo que el sistema hace: nombra los tokens reales —`ground` y `corriente-pleno`—, publica
los cuatro valores (`F4F6F9` y `14171D` en el de omisión, `FFFFFF` y `102A43` en el institucional),
sostiene la regla del negro **sin tocarla** —dos afirmaciones del mismo archivo dependen de ella, la
de los cuatro suelos y la del suelo profundo del institucional— y **declara la excepción del blanco
con su procedencia**: *Superficie* del archivo de identidad es blanco puro y el tema existe para
llevar ese archivo. La consecuencia medible se corrigió con él: la matriz calcula contra el suelo
**real de cada tema**, que es la razón por la que las razones de un tema no se leen como las del
otro. Ninguna tabla leída por prueba y ninguna cifra de contraste se tocaron.

**Verificación de la recompilación**

| Comprobación | Resultado |
|---|---|
| `latexmk -xelatex main_a4.tex` | **exit 0**, **104 páginas** —las mismas—, **0 referencias sin resolver**, convergido sin rerun pendiente |
| Desbordes de `main_a4` | **1**, el de 0,93 pt del índice sobre números de tres cifras, que ya estaba declarado y no procede de `contenido/`. **`a4_03` no aporta ninguno** |
| `latexmk -xelatex main_completo.tex` | **exit 0**, **251 páginas**, 0 referencias sin resolver. Sus desbordes son de `a1`–`a3`, material entregado y congelado |
| Trampa del paso 4 de `verificar_tokens_a4.sh` | **Sorteada**: el párrafo publica los hexadecimales como `	exttt{FFFFFF}`, sin almohadilla. El barrido de `a4_*.tex` da cero |
| `bash scripts/verificar_tokens_a4.sh` | **exit 0**, los cinco bloques en verde |
| `alcancePrototipos.spec.ts` y `rutaRama.spec.ts` | **10 pruebas en verde**: las tablas entre delimitadores no se tocaron |
| PDF de entrega | Recopiado a `docs/semana_4/Entregable Actividad 4_equipo_8.pdf`, **`md5` idéntico** a `main_a4.pdf` (`40721b67…`) |

### Lo que queda abierto

**Cero bugs abiertos.** Los seis están cerrados y verificados contra el archivo.

1. El aviso de eslint en `serie/Panel.vue:380` —`vue/attributes-order`—, que **no es un bug**: `make
   check` pasa en exit 0 con él.
2. Los diez recorridos del guion manual, con el MCP de Playwright. **CA-10 es el que manda**, y es
   verificación pendiente, no defecto encontrado.
3. **Sin push ni PR**, a la espera de visto bueno.

### Efecto del QA sobre el ancla del diff

Este pase añadió **dos archivos que no estaban en `git diff --name-only 3d4db21`** y que quien
commitee tiene que incluir:

- `docs/orchestration/checklist-ui.md` — la excepción de la regla 4, consecuencia de BUG-4.
- `docs/manual-test/us-a4-excelencia.md` — el guion, sin versionar todavía.

Y volvió a tocar dos que sí estaban: `design/sistema.py` (solo comentarios, los generados no se
movieron) y `docs/entregables/contenido/a4_03_guia_estilos.tex`, con su PDF recompilado.
