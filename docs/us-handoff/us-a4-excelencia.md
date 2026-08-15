# Handoff US-A4-EXCELENCIA — Los dos temas completos y la Actividad 4 en banda alta

**Estado**: planning
**Epic**: UX (con trabajo en E0, sistema de diseño, y E2, pantallas del contrato)
**Sprint**: S4, cierre · **Actividad**: A4 (dom 16-ago-2026)
**Rama**: continúa en `us-entrega-a4`, sobre su árbol **sin commitear**. Sin PR (discrepancia RU-11 declarada)
**SHA base**: `aeafc6e`. Ancla del diff acumulado: `git diff --name-only aeafc6e`. **QA no usa `HEAD~N`**
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

Antes de abrir esta US se corrigió la capa que todas las demás consumen. **Está en el árbol de
trabajo, sin commitear.**

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
