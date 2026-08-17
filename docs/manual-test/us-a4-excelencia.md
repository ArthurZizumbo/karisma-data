# Prueba manual — US-A4-EXCELENCIA: los dos temas completos y la Actividad 4 en banda alta

**Rama**: `us-a4-excelencia` · **SHA base**: `3d4db21` · **Estado del QA**: `testing`, 16-ago-2026.

> Aquí solo está lo que la suite **no puede** medir. Los 23 criterios de aceptación con su comando
> automatizado viven en la sección 1 de [`docs/us-planning/us-a4-excelencia.md`](../us-planning/us-a4-excelencia.md),
> y el registro de olas en [`docs/us-handoff/us-a4-excelencia.md`](../us-handoff/us-a4-excelencia.md).
> Repetir a mano una aserción de vitest no prueba nada nuevo.
>
> **Por qué esto existe.** Cuatro criterios de esta US son geométricos —CA-8, CA-9, CA-10 y CA-16—
> y happy-dom **no calcula `scrollWidth` ni `getBoundingClientRect`**. Las olas B y C midieron su
> propio marcado en un Chromium sin cabeza, con `<main style="padding:16px">` como lienzo y sin las
> tipografías del sistema instaladas: es el mismo defecto medido con otra fuente y otro contenedor.
> El recorrido V5 sobre las diez rutas **nunca se ejecutó** y es el que manda.

## Preparación

| Paso | Resultado esperado |
|---|---|
| 1. `docker compose up -d db api` y esperar `healthy` | `docker compose ps` muestra las dos filas en `Up (healthy)` |
| 2. `make db-up && make db-seed` | Termina con `12 \| 304 \| 30` |
| 3. `pnpm --dir frontend dev` | `http://localhost:3000` responde |
| 4. Confirmar que la puerta de demostración está encendida (`DEMO_LOGIN_ENABLED`) | El conmutador de perfil aparece en la cabecera. Sin ella, la sección 4 se salta entera y se anota por qué |

---

## 1. V5 — cero desplazamiento horizontal (CA-10). **El que manda**

Es el único defecto de esta US con medición previa reproducible: `/inicio` desbordaba **194 px a
390** con 49 elementos fuera del lienzo. El arreglo son tres `min-w-0` y su efecto solo existe en un
navegador real.

Automatizable con el MCP de Playwright. En cada ruta y en cada ancho:

```js
// browser_evaluate
() => ({ sw: document.documentElement.scrollWidth, cw: document.documentElement.clientWidth })
```

| Paso | Resultado esperado |
|---|---|
| 1. Recorrer las **diez** rutas del chasis —`/`, `/acceso`, `/inicio`, `/exploracion`, `/exploracion/tableros`, `/exploracion/exportar`, `/gobierno`, `/administracion`, `/asistente`, `/guia`— a **390 px** | `scrollWidth === clientWidth` en las diez. **Cero** excepciones: una sola ruta que desborde tumba el criterio |
| 2. Repetir a **768**, **1280** y **1440 px** | Igual: 40 mediciones, 40 iguales |
| 3. Repetir las diez a 390 px con `data-tema="institucional"` | Igual. El tema cambia color, no geometría; si aquí desborda, el chasis no es uno solo |
| 4. En `/inicio` a 390 px, entrar como **operativo**, luego **analista**, luego **directivo** | Las tres composiciones sin desborde. Son tres `Espacio*.vue` distintos y el defecto medido vivía en el `BloqueLista` que comparten |

---

## 2. V3 y V4 — el cromo, contado y alcanzado (CA-8, CA-9)

| Paso | Resultado esperado |
|---|---|
| 1. A **1440 px**, con los paneles cerrados, contar los controles de la cabecera: `document.querySelectorAll('[data-cabecera-producto] a, [data-cabecera-producto] button, [data-cabecera-producto] input')` | **6 o menos**. Con la puerta de demostración abierta salen exactamente seis: marca, buscador, apariencia, perfil y los dos de idioma |
| 2. Mirar el botón de apariencia | Lleva **rótulo visible** —«Apariencia»—, no solo icono. Es la mitad del criterio que la evaluación marcó: once controles y ninguno rotulado |
| 3. A **390 px**, abrir el conmutador de perfil | El disparador está **dentro del lienzo**. El de la entrega anterior medía `left: -144.4` y la cabecera no desplaza, así que era inalcanzable |
| 4. Medir el disparador de perfil y los dos de idioma con `getBoundingClientRect()` a 390 px | Los tres ≥ **44 × 44**. Los de idioma declaran `size-11` desde la integración; si alguno mide 43, el filete se comió el píxel otra vez |
| 5. Abrir el panel de apariencia a **390 px** | Anclado al borde final (`end-0`), enteramente dentro del lienzo. No lo mismo que el defecto que reemplaza |
| 6. `Esc` con el panel abierto | Cierra. El foco no se pierde en el fondo |

---

## 3. V1 y V2 — el chasis y la retícula, por tema (CA-3, CA-7)

| Paso | Resultado esperado |
|---|---|
| 1. Abrir `/inicio` con el tema de omisión | La retícula modular de 24 px **se ve** sobre el suelo |
| 2. Cambiar a **institucional** desde el panel de apariencia | La retícula **desaparece**: `--color-reticula` se resuelve al propio suelo. Si sigue viéndose, `portal.vue` volvió a leer `--color-grid` |
| 3. Recorrer las ocho rutas del contrato más `/guia` | Barra lateral presente, cada entrada con **etiqueta de texto** al lado del icono a ≥ 768 px |
| 4. Abrir `/` y `/acceso` | Mismo chasis —cabecera, franja de alcance, salto al contenido— y **sin barra lateral**. Es deliberado: son las dos pantallas sin sesión |
| 5. Bajar a **390 px** en `/inicio` | La barra colapsa a tira de iconos. Cada icono conserva su `title` con el nombre del módulo |
| 6. Buscar al fondo de la barra las nueve «facetas transversales» | **No están.** Eran `listitem` sin enlace: navegación que no navegaba |
| 7. Contar apariciones del nombre del producto en una pantalla cualquiera | **Una.** La cabecera lo nombra; la barra ya no lo repite |

---

## 4. V6 y V7 — el catálogo deja de ser un callejón (CA-12, CA-13, CA-15)

| Paso | Resultado esperado |
|---|---|
| 1. Entrar como **operativo**, abrir `/exploracion` y buscar `saldo` | Aparece la tabla de campos. Mientras carga, el esqueleto ocupa la **misma altura** que las filas: sin salto de maquetación |
| 2. Con un lector de pantalla —NVDA o VoiceOver— repetir la búsqueda | Se anuncian **las cuatro salidas**: «Buscando campos», el conteo de resultados, el vacío o el error. Antes se anunciaba el inicio y nunca el final |
| 3. Hacer clic en el nombre físico de una fila | Abre el linaje de **ese** campo. La fila es la puerta; si no pasa nada, volvió el callejón |
| 4. Al pie del resultado, seguir el enlace a Gobierno del dato | Llega a `/gobierno`. Es la salida hacia la ficha completa |
| 5. Copiar la URL: debe decir `?q=saldo` | La búsqueda es direccionable |
| 6. Abrir esa URL **en una pestaña nueva** | Abre con el término aplicado **y el resultado pintado**, no con el campo lleno y la tabla vacía |
| 7. Desde el resultado, ir a los tableros y pulsar **Atrás** | Vuelve al catálogo **con el término puesto**. Si vuelve vacío, alguien cambió `replace` por `push` |
| 8. Buscar `zzzzz` | Estado vacío en prosa —titular, motivo y consejo—, **no** una tabla con encabezado y cero filas |
| 9. Detener el backend y reintentar | Estado de error con el código y el botón **Reintentar**, que reintenta de verdad |
| 10. Abrir `/exploracion` y `/gobierno` una al lado de la otra | **Etiqueta, ayuda y estado inicial distintos.** Cada una declara qué resuelve. Antes abrían idénticas (CA-20) |

---

## 5. Las tablas, ordenadas y densas (CA-14)

| Paso | Resultado esperado |
|---|---|
| 1. En `/exploracion`, medir la altura de una fila con el inspector | **34 px**, que es lo que declara `DESIGN.md`. Antes eran 80 |
| 2. Hacer clic en el encabezado «Nombre de negocio» | Ordena. La flecha cambia y el `<th>` declara `aria-sort="ascending"` |
| 3. Con lector de pantalla, tabular por los encabezados | Solo los ordenables se anuncian como tales. Una columna de botones **no** ofrece un orden que no tiene |
| 4. Repetir en `/administracion` (usuarios) y en el detalle de una serie del tablero | Mismo comportamiento: mismo componente |
| 5. En el detalle de serie, ordenar la columna de cifras | El orden es **numérico**. Si `1 284,5` queda antes que `987,6`, se está ordenando el texto impreso |
| 6. Ir a `/guia` y comparar la lámina de tablas con lo anterior | Coinciden. La lámina es la norma de la que sale el componente |

---

## 6. La marca y las superficies, que es juicio visual (CA-6, CA-16, CA-17)

| Paso | Resultado esperado |
|---|---|
| 1. Inspeccionar la marca de la cabecera | Es un `<svg>` en línea. **Cero `<img>` y cero iconos del paquete**. El anterior era `lucide:circuit-board` teñido de azul informativo |
| 2. Cambiar de tema y de modo con la marca a la vista | La marca **no se repinta**. La teja sigue en verde azulado y la barra en ámbar: la guía prohíbe recolorearla, y por eso sus cuatro hex viven en el componente y no en los tokens |
| 3. Comparar la marca contra la página normativa del archivo de diseño | Proporciones, no píxeles: teja con radio ≈ 6 % del lado, tres barras claras, barra de acento a dos columnas. **Contra la página normativa, no contra las cinco maquetas**: el archivo se contradice y esa discrepancia se declara en `a4_03` |
| 4. Bajar a 640 px | El nombre desaparece y queda el símbolo. No se renderiza pequeño: no se renderiza |
| 5. Mirar una tarjeta de indicador en `/inicio` como **directivo** | Filete de un pelo, barra de color a la izquierda y radio ≤ 8 px bajo el institucional, cero bajo el de omisión |
| 6. Contar las tarjetas de indicador de `/inicio` como directivo | **Cuatro**, cada una con etiqueta, marca de tiempo y cifra en **monoespaciada tabular** |
| 7. Abrir `/inicio` como **operativo** y como **analista** | **No hay tarjetas de indicador**: pertenecen a la composición directiva. Comprobar que la composición se sostiene igual sin ellas, o abrir hallazgo |

---

## 7. Los tres estados de certificación, bajo dicromacia (CA-11)

Es el criterio que ninguna prueba de DOM puede juzgar: la suite comprueba que los tres iconos son
distintos; que se **distingan** es percepción.

| Paso | Resultado esperado |
|---|---|
| 1. En `/exploracion`, buscar hasta ver los tres estados —vigente, en revisión, obsoleto— en la misma pantalla | Los tres con **icono distinto** y color distinto. «En revisión» y «Obsoleto» compartían triángulo y color, y significan cosas opuestas |
| 2. Activar en DevTools la emulación de **protanopia**, **deuteranopia** y **tritanopia** | En las tres se siguen distinguiendo. Si solo el icono los separa, el color no está haciendo su parte |
| 3. Repetir con el tema institucional en claro y en oscuro | Cuatro combinaciones, mismo resultado |
| 4. Poner la pantalla en escala de grises | Se distinguen **solo por la forma**. Es la prueba de que el canal no es únicamente el color |

---

## 8. `/acceso`, donde el énfasis estaba invertido

| Paso | Resultado esperado |
|---|---|
| 1. Abrir `/acceso` con la puerta de demostración **abierta** | Los cuatro perfiles vienen **primero**, en la tarjeta de acción. El formulario de credenciales queda detrás de una revelación |
| 2. Comprobar cuál lleva el énfasis primario | El camino recomendado. Antes el botón primario se lo llevaba el formulario **que nadie en una demostración puede usar**, y el camino recomendado iba en color de precaución |
| 3. Apagar `DEMO_LOGIN_ENABLED` y recargar | El estado «sin permiso» se anuncia en la misma región de mensaje. La página lo explica; no desaparece en silencio |
| 4. Entrar como cada uno de los cuatro roles | La barra lateral muestra **solo** los módulos de ese rol. Un módulo oculto es una entrada **ausente del DOM**, no un `disabled`: una puerta gris sigue anunciando una puerta |

---

## 9. Idioma, foco y movimiento

| Paso | Resultado esperado |
|---|---|
| 1. Cambiar a inglés desde la cabecera y recorrer las diez rutas | **Ninguna cadena en español** queda suelta. La URL **no cambia** (`no_prefix`) |
| 2. Comprobar acentos y eñes en las pantallas en español | Se ven bien en pantalla y en las capturas. Es el defecto que la integración persiguió y midió |
| 3. Recorrer `/exploracion` **solo con `Tab`** | Anillo de foco visible en cada parada. La primera parada es el salto al contenido |
| 4. Activar `prefers-reduced-motion` en el sistema y recargar con la tabla cargando | El esqueleto **no pulsa**. Aparece y desaparece sin animación |
| 5. A 1440 y 1280 px en `/guia` | Ningún rótulo de botón se parte en dos líneas (regla 7 de `checklist-ui.md`) |

---

## 10. El entregable (CA-21, CA-22)

| Paso | Resultado esperado |
|---|---|
| 1. `ls docs/semana_4/` | **Hoy falla.** El archivo se llama `Entregable Actividad 4_equipo.pdf` y la actividad exige `Entregable Actividad 4_equipo_8.pdf`. Ver **BUG-1** |
| 2. Abrir el PDF y comprobar la portada, el índice y la numeración | 104 páginas, sin referencias `??` y sin cajas desbordadas visibles |
| 3. Buscar la palabra «rúbrica» en el cuerpo | **Cero apariciones.** Es la observación del profesor sobre la entrega anterior |
| 4. Hojear las páginas de los cinco flujos | **Un solo titular de flujo por página**, con su lámina de secuencia; la de detalle en la siguiente. Ninguna página con dos titulares |
| 5. Comparar las once capturas del tema contra el portal en ejecución | Corresponden al chasis de barra lateral y a la marca en SVG. Una captura con el cromo antiguo delata que no se recapturó |
| 6. Abrir `main_completo.pdf` y revisar la parte IV | 252–254 páginas, la parte IV completa y coherente con `main_a4.pdf` |

---

## Lo que esta prueba **no** cubre, y por qué

- **La paleta y el contraste.** `tests/ml/test_contraste_temas.py` mide las cuatro combinaciones con
  aritmética WCAG y las separaciones bajo las tres dicromacias. Juzgarlas a ojo sería peor medición.
- **La reproducibilidad de los generados.** `make tokens` y `python -m ml.data.seed_catalog` se
  reejecutaron en QA y devolvieron los cuatro archivos **byte a byte iguales**. Nada que mirar.
- **El conteo de claves i18n.** `contratos.spec.ts` compara los dos catálogos aplanados.
- **La cobertura.** Backend y ml al 98,23 % con 826 pruebas; frontend al 94,04 % con 1 063.
