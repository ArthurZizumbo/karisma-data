# Pruebas manuales — US-UX-07 (Interfaces de alta fidelidad, A4)

**SHA base**: `d658be8` · **Rama**: `us-ux-07` · **Fecha**: 14-ago-2026

Aquí **solo** está lo que no puede automatizarse en `vitest`: lo que exige un navegador real, la
dirección desplegada, el PDF impreso o juicio humano. Lo mecánicamente verificable ya lo cubren
`make check`, `make test`, `scripts/smoke_rutas.sh` y las dos pruebas nuevas
(`rutaRama.spec.ts`, `alcancePrototipos.spec.ts`), y **no se repite aquí**.

Requisito previo para los bloques 1 a 6: `pnpm --dir frontend dev` en el puerto 3001, o
`make dev` con la imagen `web` reconstruida (`docker compose build web`), en el puerto 3000.
El guion de captura documenta 3001 como valor por omisión.

> Marcado **[Playwright]** lo que puede automatizarse con el MCP de Playwright. El resto pide ojo
> humano, el PDF en papel o una segunda máquina.

---

## 1. El arreglo del CA-6 viaja en las tres plantillas — **[Playwright]**

`FranjaAlcance.spec.ts` ya afirma la clase sobre los cuatro chasis (hallazgo QA-01, corregido), y
esa prueba es la barrera. Lo que este bloque añade es lo que una prueba de montaje **no** puede
ver: que la clase se traduzca en un ancho real en el navegador. Vitest comprueba que la clase está
escrita; solo el navegador comprueba que la regla de `main.css` cedió.

| Paso a paso | Resultado esperado |
|---|---|
| 1. Abrir `/acceso` a viewport 1440 × 900. 2. En consola: `document.querySelector('[data-franja-alcance]').getBoundingClientRect()` | `width` = **1440** (no 455). La plantilla es `acceso.vue` |
| 3. Iniciar sesión de demostración como `directivo` y abrir `/inicio`. 4. Repetir la medición | `width` = ancho de la columna de contenido del portal (**~1193–1208**), no 455. La plantilla es `portal.vue` |
| 5. Abrir una ruta que use la plantilla `default` (por ejemplo `/`). 6. Repetir la medición | `width` = ancho completo del contenedor, no 455 |
| 7. En las tres, leer `height` de la misma caja | **~33 px** (una línea), no 48 (dos líneas). Es la diferencia visible entre las figuras `antes/` y `despues/` |

Importa porque las figuras `figuras/a4/antes/2_exploracion_normal.png` y `despues/…` son la
evidencia del CA-6 en un documento calificado: si la clase desaparece, el PDF afirma una
iteración que el código ya no tiene.

## 2. `error.vue` con la franja a todo el ancho — **hallazgo QA-02, corregido en QA** — **[Playwright]**

| Paso a paso | Resultado esperado |
|---|---|
| 1. Navegar a una ruta inexistente, por ejemplo `/ruta-que-no-existe`. 2. Medir `[data-franja-alcance]` con `getBoundingClientRect()` | `width` = ancho completo del contenedor, **no 455**. `height` ≈ 33 px |

`error.vue` monta `FranjaAlcance` y **no es una plantilla**, así que no hereda el arreglo de los
tres layouts y tiene que repetirlo. Era el cuarto punto de montaje y el único sin corregir; la
pantalla de error es, además, uno de los cuatro estados no felices que el entregable declara. La
clase ya está puesta y `FranjaAlcance.spec.ts` la afirma sobre las cuatro superficies, de modo que
este bloque queda como verificación en navegador de lo que la prueba unitaria ya sostiene.

## 3. La paleta de la primera impresión sigue al sistema operativo — **hallazgo QA-03** — **[Playwright]**

**No es un defecto de código y no se corrige.** `useModo.ts` fija `'sistema'` como modo por
omisión y `sistemaDiseno.ts` lo resuelve con `prefers-color-scheme`: en un equipo con el sistema
en oscuro, el portal abre en oscuro, y eso es exactamente lo que el composable declara querer. Lo
que la prueba mide es la **tensión** entre esa decisión y la guía de estilos, que declara el modo
oscuro fuera de alcance verificado.

| Paso a paso | Resultado esperado |
|---|---|
| 1. Abrir un contexto con `colorScheme: 'dark'`. 2. Abrir `/`. 3. Observar la paleta | Abre en **oscuro**. Es el comportamiento diseñado |
| 4. Repetir con `colorScheme: 'light'` | Abre en **claro** |
| 5. En ambos casos, pulsar el control **Claro** del selector de modo y recargar | La elección persiste. El protocolo de captura la fija de forma explícita, y por eso las siete figuras salen en claro pase lo que pase en la máquina de quien captura |

El juicio humano que se pide es de producto, no de código: **decidir para S5** si la guía de
estilos verifica el modo oscuro o si el portal deja de seguir al sistema. Hoy la primera
impresión de un evaluador con el sistema en oscuro ocurre en una paleta que el documento dice no
haber verificado, y eso está registrado como hallazgo no atendido en `a4_04_prevalidacion.tex`.

## 4. Reproducibilidad del guion de captura por otra persona

El valor del guion es que un tercero obtenga el mismo conjunto. Se prueba con alguien que **no**
haya participado en la captura.

| Paso a paso | Resultado esperado |
|---|---|
| 1. Seguir `docs/entregables/capturas/guion_a4.md` de principio a fin, sin consultar a nadie. 2. `pnpm --dir frontend exec playwright install chromium`. 3. `CAPTURAS_FASE=despues CAPTURAS_SALIDA=/tmp/a4 node docs/entregables/capturas/capturas_a4.mjs` | **7/7 capturas escritas**, con los mismos siete nombres de archivo que `figuras/a4/despues/` |
| 4. Comparar las dimensiones en píxeles de cada PNG contra su homónimo archivado | **Coinciden, sin exportar ninguna variable** (hallazgo QA-04, corregido: `CAPTURAS_ESCALA` vale 1 por omisión, que es la escala del conjunto archivado) |
| 5. Comparar el contenido de cada par a simple vista | Misma pantalla, mismo rol, misma franja de alcance visible, mismo estado |

## 5. Fidelidad de las figuras del PDF contra la aplicación viva — juicio humano

| Paso a paso | Resultado esperado |
|---|---|
| 1. Abrir el PDF de `docs/semana_4/` en las páginas de la sección de prototipos. 2. Al lado, abrir cada una de las siete rutas con el rol que declara el pie de figura | Cada figura corresponde a la pantalla que su pie nombra, con el mismo rol, y **la franja de alcance se ve en las siete** (regla R10) |
| 3. Verificar la figura de `/asistente` | Conserva visible la franja de honestidad `chat.demo.scriptedNotice`: el gate de Gemini salió NO-GO y recortarla presentaría un guion como respuesta viva |
| 4. Verificar `4_asistente_resultado.png` | Muestra un turno resuelto con su tarjeta de llamada a herramienta y la fuente del catálogo citada. No forma pareja antes/después: documenta un estado, no una versión |

## 6. Los cuatro estados no felices etiquetados (b) existen de verdad — **[Playwright]**

La matriz 7 × 4 declara 12 celdas construidas por otras historias del sprint. El entregable las
afirma; conviene verificarlas antes de la entrega, porque una celda (b) que no exista convierte la
matriz en una promesa.

| Paso a paso | Resultado esperado |
|---|---|
| 1. Sesión como `operativo`. 2. Abrir `/administracion` | 403 con el estado «sin permiso» dibujado, **URL intacta**, sin control de reintento y con una sola salida al espacio propio |
| 3. Cerrar sesión. 4. Abrir `/administracion` directamente | Redirige a `/acceso` |
| 5. Sesión con permiso. 6. Abrir `/exploracion/exportar` con el historial vacío | Vacío explícito. **Nunca un enlace de descarga falso** |
| 7. Abrir `/asistente` y enviar una pregunta | Aparece la tarjeta de llamada a herramienta antes del texto, y la respuesta cita la fuente del catálogo |

## 7. La dirección pública de GCP — segunda máquina o red distinta

| Paso a paso | Resultado esperado |
|---|---|
| 1. Desde una máquina que no sea la de desarrollo, abrir la dirección pública de US-003 | Responde, o **no responde**. Las dos son respuestas válidas |
| 2. Contrastar con la línea de `a4_01_metodo_prototipado.tex` sobre el despliegue | Lo que el PDF afirma coincide con lo observado. La evidencia del entregable son las capturas locales reproducibles, no la dirección: si está caída, el `.tex` no debe prometerla |

## 8. Legibilidad del PDF impreso — juicio humano, en papel

| Paso a paso | Resultado esperado |
|---|---|
| 1. Imprimir en carta las páginas con figuras de pantalla del PDF de `semana_4/`. 2. Leer sin lupa los rótulos de la barra lateral y los encabezados de tabla dentro de cada captura | Se leen. Una captura de 1440 px reducida a la caja de texto del informe pierde el texto pequeño, y ese es el riesgo que esta prueba mide |
| 3. Revisar que ninguna figura se corte entre páginas ni desborde el margen | Ninguna |

## 9. Entrega en Canvas (CA-8) — juicio humano

| Paso a paso | Resultado esperado |
|---|---|
| 1. Subir `docs/semana_4/Entregable Actividad 4_equipo_8.pdf` a Canvas **antes del dom 16-ago-2026, 20:00**. 2. Descargar de vuelta el archivo subido y abrirlo | Nombre exacto, se abre sin error y trae las 61 páginas. La captura del acuse queda como evidencia del CA-8 |

---

## Hallazgos que estas pruebas confirman

| ID | Qué | Estado | Dónde |
|---|---|---|---|
| QA-01 | El arreglo del CA-6 no tenía prueba automática que lo sostuviera | corregido; el bloque queda como verificación en navegador | Bloque 1 |
| QA-02 | `error.vue` conservaba la medida de lectura en la franja | corregido | Bloque 2 |
| QA-03 | La paleta de la primera impresión sigue al sistema operativo | no es defecto; decisión de producto para S5 | Bloque 3 |
| QA-04 | El guion salía a escala 2 y el conjunto archivado está a escala 1 | corregido: la escala por omisión es 1 | Bloque 4 |
