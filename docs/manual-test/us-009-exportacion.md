# Pruebas manuales — US-009 (Exportación en segundo plano)

**SHA base**: `a251652` · **Rama**: `us-009-exportacion` (árbol compartido) · **Fecha**: 13-ago-2026
**Estado**: pendiente de ejecución por una persona · **Escrito por**: QA, tras la auditoría del diff

Aquí está **solo** lo que la suite no puede demostrar. Las pruebas de contrato de
`tests/backend/test_export_*.py` cubren la firma HMAC, la caducidad con reloj inyectado, la matriz
de scopes y el ciclo de la migración, y `frontend/test/exportaciones.spec.ts` cubre el store y el
temporizador. Lo que queda abajo exige **navegador real, portal levantado o juicio humano**: nada
de esto se puede afirmar desde un doble en memoria.

> La verificación visual de los pasos marcados **[MCP]** se puede automatizar con el MCP de
> Playwright (`browser_navigate`, `browser_snapshot`, `browser_take_screenshot`). El juicio sobre
> si lo que se ve es honesto sigue siendo humano.

## Preparación

| Paso a paso | Resultado esperado |
|---|---|
| 1. `make dev` y esperar a que la API y el web estén arriba | Los tres contenedores en `running`; `GET http://localhost:8000/health` responde 200 |
| 2. `make data` si `data/silos/` está vacío | Tres `.parquet` en `data/silos/`: `creditos`, `liquidez`, `derivados` |
| 3. Poner `EXPORT_DEMO_DELAY_SECONDS=8` en `backend/.env.local` y `NUXT_PUBLIC_EXPORT_DEMO_DELAY=8` en `frontend/.env.local`, y reiniciar | Ambos archivos siguen ignorados por git: `git status --short` no los muestra |
| 4. Entrar en `http://localhost:3000/acceso` como `dhernandez` (rol `analista`) | Sesión abierta; la barra lateral muestra el módulo de exploración |

> **Devolver los dos retrasos a `0` al terminar.** Con el retraso puesto, todo despliegue estira
> artificialmente la duración del trabajo.

## 1. Los tres momentos de A4, sobre estado real

| Paso a paso | Resultado esperado |
|---|---|
| 1.1 Ir a `/exploracion/exportar` **[MCP]** | La franja de honestidad `export.demo.notice` está visible, y lo está **porque el retraso es mayor que cero**. Con retraso `0` la franja desaparece: comprobarlo también, es lo que la hace honesta y no decorativa |
| 1.2 Pedir `creditos` en `csv` sin filtros y pulsar el botón de exportar **[MCP]** | La respuesta llega **de inmediato**, sin que la interfaz se congele: aparece una tarjeta en estado `pendiente` con su identificador. Juicio humano: si hubo cualquier espera perceptible antes de ver la tarjeta, el criterio de no bloqueo no se cumple |
| 1.3 Mientras el trabajo corre, navegar a `/exploracion/tableros` y volver **[MCP]** | La tarjeta sigue viva y con el estado avanzado. El estado sobrevive al cambio de pantalla porque el temporizador vive en el store, no en la página |
| 1.4 Observar la tarjeta durante los 8 s del retraso **[MCP]** | Se ven **al menos tres** estados distintos: `pendiente`, `en_proceso` y `completado`. Con menos de tres, el intervalo de sondeo de 3 000 ms no está dando muestras del estado intermedio y las capturas de A4 no se pueden tomar |
| 1.5 Añadir `?momento=solicitud`, luego `?momento=proceso`, luego `?momento=enlace` a la URL **[MCP]** | Cada uno fija el trabajo real correspondiente y **desactiva el auto-avance**. Juicio humano: ninguno debe fabricar datos — con historial vacío, `?momento=enlace` tiene que mostrar el vacío explícito, no una tarjeta inventada |
| 1.6 Tomar las tres capturas para A4 **[MCP]** | Las tres llevan la franja de honestidad visible y cifras de un trabajo real. Una captura sin la franja no sirve como evidencia |

## 2. El enlace firmado, contra el reloj de verdad

La suite demuestra las 24 h moviendo un reloj inyectado. Lo que **no** puede demostrar es que el
enlace que el navegador recibe es el que el servidor firmó.

| Paso a paso | Resultado esperado |
|---|---|
| 2.1 Con el trabajo `completado`, copiar el enlace de descarga de la tarjeta | Es una ruta **relativa** (`/api/export/<job_id>/download?exp=...&sig=...`), nunca absoluta: si fuera absoluta, el proxy de Nitro no la reenviaría |
| 2.2 Pulsar el enlace en el navegador | Descarga un `.csv`. Abrirlo: la primera línea es la cabecera críptica del silo (`cli_ref,nom_cli,prod_cd,sdo_cap,...`). Juicio humano: es el dato real, no un marcador ni un archivo vacío |
| 2.3 Comparar el `caduca_en` que muestra la tarjeta con la hora de término del trabajo | La diferencia es **exactamente 24 h**. Es `terminado_en + 24 h`, no `created_at + 24 h`: el `COMMENT` de la columna en la migración dice lo segundo y está mal (hallazgo QA-C1) |
| 2.4 Editar a mano el `sig` de la URL (cambiar un carácter hexadecimal por otro) y pedirla | **403** con `detail.codigo = firma_invalida`. Nunca 410, nunca 200 |
| 2.5 Poner en `sig` 64 caracteres **no hexadecimales** y pedirla | **422** por el patrón del parámetro. Antes del arreglo de QA (hallazgo QA-B2) esto daba **500** |
| 2.6 Editar a mano el `exp` de la URL (subirlo un año) y pedirla | **403** `firma_invalida`, **no 410 ni 200**. Esto es lo que prueba que el vencimiento viaja *dentro* del material firmado; si diera 410 o 200, la caducidad sería decorativa |
| 2.7 Poner `EXPORT_LINK_TTL_HOURS=0` en `backend/.env.local`, reiniciar, exportar y pedir el enlace | **410** con `detail.codigo = enlace_caducado`. Devolver el ajuste a `24` al terminar |

## 3. Propiedad del trabajo: que no sea un oráculo de enumeración

| Paso a paso | Resultado esperado |
|---|---|
| 3.1 Anotar el `job_id` de un trabajo de `dhernandez`. Cerrar sesión y entrar como **otro** `analista` | El historial del segundo analista **no** muestra ese trabajo |
| 3.2 Pedir a mano `GET /api/export/<job_id>` con la sesión del segundo analista | **404**, no 403. Un 403 confirmaría que el identificador existe |
| 3.3 Pedir el enlace de descarga completo del primer analista con la sesión del segundo | **404**. La firma válida no sustituye a la sesión |
| 3.4 Entrar como `admin` y abrir el historial | Ve **todos** los trabajos del portal, con dataset, filas y tamaño, pero **ninguna fila trae enlace de descarga**. Juicio humano: gobierno es leer quién exportó qué, no poder descargarlo |
| 3.5 Entrar como usuario `operativo` y navegar a `/exploracion/exportar` | La pantalla no es alcanzable: la guarda por rol la corta antes. Y `POST /api/export` a mano devuelve **403** |

## 4. Fuga de datos entre sesiones en la misma pestaña

> Hallazgo QA-A4, corregido en esta pasada de QA. Este paso es la comprobación de que el arreglo
> funciona en un navegador real, que es donde el defecto vivía.

| Paso a paso | Resultado esperado |
|---|---|
| 4.1 Como `dhernandez`, lanzar una exportación y esperar a que aparezca en el historial | La tarjeta y la fila del historial están visibles |
| 4.2 **Sin cerrar la pestaña**, cerrar sesión y entrar como otro `analista` | El historial del segundo usuario aparece **vacío o solo con sus propios trabajos**. Si asoma cualquier trabajo del primero —aunque sea un instante antes de recargar—, el arreglo no cerró el defecto |

## 5. El gate de no bloqueo, que la suite mide en frío

| Paso a paso | Resultado esperado |
|---|---|
| 5.1 Con `EXPORT_DEMO_DELAY_SECONDS=0`, lanzar una exportación de `creditos` completo (180 000 filas) en `csv` | El trabajo tarda segundos, no minutos |
| 5.2 **Durante** ese trabajo, en otra pestaña, pedir repetidamente `GET /health` y `GET /api/catalog/search?q=saldo` | Todas responden por debajo de **500 ms**. Si alguna se pasa, `sink_csv` está materializando y hay que revisar `_producir` |
| 5.3 Repetir 5.1 y 5.2 con formato `xlsx` sobre `creditos` | Igual por debajo de 500 ms. El tope medido de XLSX son 200 000 filas; por encima, el trabajo termina `fallido` con `formato_no_disponible`, que es el comportamiento correcto y no un error |

## 6. Los cuatro estados no felices, a ojo

| Paso a paso | Resultado esperado |
|---|---|
| 6.1 Entrar a `/exploracion/exportar` con historial vacío **[MCP]** | Estado vacío explícito con acción siguiente, no una tabla de cero filas |
| 6.2 Recargar la pantalla con la red estrangulada a 3G lento (DevTools) **[MCP]** | Sale un esqueleto que **reserva la altura**. Juicio humano: al llegar los datos no debe haber salto de maquetación |
| 6.3 Parar el contenedor de la API y recargar **[MCP]** | Franja de error con texto traducible y un botón de reintento que funciona al levantar la API. Nunca un `detail` crudo del backend ni un identificador técnico en pantalla |
| 6.4 Repetir 6.3, esperar a que la franja aparezca, levantar la API y dejar que el sondeo siga | La franja roja **desaparece** en cuanto un sondeo vuelve a salir bien. Antes del arreglo de QA (hallazgo QA-B7) se quedaba puesta para siempre |
| 6.5 Colapsar la tarjeta destacada con un clic mientras el trabajo corre **[MCP]** | La pantalla **no** debe decir que no hay ningún trabajo: el trabajo sigue vivo y visible en la lista de abajo (hallazgo QA-B6, corregido) |
| 6.6 Entrar como `operativo` **[MCP]** | Sin permiso, resuelto por la guarda de ruta, no por una pantalla en blanco |
| 6.7 Activar «reducir movimiento» en el sistema operativo y observar un trabajo en proceso **[MCP]** | El icono de carga y la barra de progreso **no animan** |
| 6.8 Con un lector de pantalla (NVDA o VoiceOver), dejar un trabajo corriendo sin tocar nada | El cambio de estado a `completado` **se anuncia solo**. Es el único texto de la pantalla que cambia sin acción del lector, y sin región viva nadie se entera de que su exportación terminó |

## 7. Lo que esta US declaró fuera y por tanto NO se prueba aquí

No son huecos de QA: son recortes escritos en el §10.2 del plan (recorte #3) y en el handoff.

- **Bucket GCS real y su ciclo de vida de 7 días.** `AlmacenGCS` está escrito y no ejecutado. El
  criterio de las 24 h se entrega con la fachada local firmada. El día que exista el proyecto GCP,
  el cambio es `EXPORT_STORAGE_BACKEND=gcs` y esta sección se reescribe.
- **Auditoría de duración del trabajo.** Las columnas `started_at` y `finished_at` existen y la
  duración es derivable, pero no hay vista que la explote.
- **Pérdida de un trabajo vivo si Cloud Run escala a cero.** Deuda declarada: el store lo marca
  `caducado_en_cliente` a los 10 minutos. Reproducible solo en la nube.
