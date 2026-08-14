# Guion de capturas de la Actividad 4

Este documento fija qué se captura, en qué orden, con qué sesión y con qué estado. Su valor no
es automatizar: es hacer que otra persona, en otra máquina, obtenga las mismas imágenes. El guion
ejecutable [`capturas_a4.mjs`](capturas_a4.mjs) implementa exactamente lo que aquí se describe, y
la ruta manual del apartado 7 lo sustituye cuando Playwright no está disponible.

Las figuras que consume el PDF viven en `../figuras/a4/antes/` y `../figuras/a4/despues/`.

---

## 1. Precondiciones

El portal se captura corriendo, con su backend real detrás. No se capturan maquetas.

```bash
make dev                      # db + api + web con Docker Compose
```

`make dev` publica el portal en `http://127.0.0.1:3000` y el api en `http://127.0.0.1:8000`.

**Advertencia sobre el contenedor `web`.** La imagen de `web` se construye una vez y sirve el
bundle ya compilado: si hay commits posteriores a esa construcción, el contenedor sirve código
viejo y las capturas documentan una versión que no es la entregada. Antes de capturar se compara
la fecha de construcción de la imagen contra el último commit que toca `frontend/`:

```bash
docker image inspect $(docker inspect karisma-data-web-1 --format '{{.Image}}') --format 'built={{.Created}}'
git log -1 --format='%ci' -- frontend/
```

Si la imagen es anterior, hay dos salidas válidas: reconstruirla con `make dev` o usar el bucle
rápido que el propio `docker-compose.yml` documenta, que es un `pnpm dev` en el host contra el api
del Compose. El segundo es el que produjo las capturas archivadas:

```bash
cd frontend
NUXT_API_BASE=http://localhost:8000 pnpm dev --port 3001
```

Ese servidor escucha en `http://localhost:3001` y refleja el árbol de trabajo tal como está en
disco, sin paso de construcción intermedio.

La sesión de demostración exige `DEMO_LOGIN_ENABLED=true` en `backend/.env.local`. Sin esa bandera
el backend responde 404 a la puerta de demostración y el guion no puede abrir sesión.

---

## 2. Parámetros fijos de toda captura

| Parámetro | Valor | Por qué |
|---|---|---|
| Viewport | **1440 x 900** píxeles CSS | Es la resolución de trabajo del perfil directivo descrito en A1 y cabe en la caja de texto del informe sin reducción agresiva |
| Modo de color | **claro** | La guía de estilos declara el modo oscuro fuera de alcance. Capturar en oscuro documentaría una paleta que el propio entregable dice no haber verificado |
| Idioma | **español**, cookie `karisma_locale=es` | Los entregables del curso son en español. La interfaz es bilingüe y la URL no cambia con el idioma |
| Espera | red inactiva más la franja de alcance visible en el DOM | Una captura tomada antes de que el estado llegue muestra un esqueleto y lo hace pasar por contenido |
| Escala | **1**, en el conjunto archivado y por omisión en el guion. Otras por `CAPTURAS_ESCALA` | A 1440 píxeles de ancho sobre la caja de texto del informe la densidad resultante basta para impresión. Reproducir el conjunto archivado no exige exportar nada: el valor por omisión ya es el suyo |

**El modo de color arranca en oscuro en un perfil de navegador limpio.** Es un paso obligatorio del
protocolo, no una preferencia: antes de la primera captura se pulsa el botón **Claro** del grupo
«Modo de color» de la cabecera. El guion ejecutable lo hace por su cuenta; en la ruta manual se
verifica a ojo en la primera pantalla y se da por fijado para el resto de la corrida, porque la
preferencia persiste entre navegaciones.

---

## 3. Contrato de nombres de archivo

```
<numero>_<pantalla>_<estado>.png
```

- `<numero>` es el ordinal que `PROTOTIPOS` declara en `frontend/app/utils/navegacion.ts`.
- `<pantalla>` es la ruta sin barras iniciales, en minúsculas, sin acentos, con las barras internas
  convertidas en guion. Lo produce `screenSlug()` del guion ejecutable.
- `<estado>` pertenece al vocabulario cerrado `normal`, `empty`, `loading`, `error`, `forbidden`.

**El nombre es el contrato.** El par antes/después se detecta por igualdad de nombre entre las dos
carpetas: una captura del después con otro nombre no forma pareja con nada y la iteración del
criterio 6 deja de ser verificable.

### Conjunto archivado

| # | Archivo | Ruta | Rol de la sesión |
|---|---|---|---|
| 0 | `0_acceso_normal.png` | `/acceso` | sin sesión |
| 1 | `1_inicio_normal.png` | `/inicio` | operativo |
| 2 | `2_exploracion_normal.png` | `/exploracion` | analista |
| 3 | `3_gobierno_normal.png` | `/gobierno` | analista |
| 4 | `4_asistente_normal.png` | `/asistente` | directivo |
| 5 | `5_administracion_normal.png` | `/administracion` | admin |
| 6 | `6_exploracion-exportar_normal.png` | `/exploracion/exportar` | analista |

Los siete nombres existen en `antes/` y en `despues/`, con el mismo contenido de nombre y distinta
imagen.

### Captura adicional del asistente

| Archivo | Ruta | Rol | Qué documenta |
|---|---|---|---|
| `4_asistente_resultado.png` | `/asistente` | directivo | Un turno resuelto, con su tarjeta de llamada a herramienta, la tabla devuelta y el campo del catálogo citado |

Vive **solo en `despues/`** y no forma pareja con nada. Documenta un estado de la conversación, no
una versión distinta de la pantalla, así que emparejarla con un antes sugeriría un cambio que no
ocurrió. Se toma a mano tras enviar una pregunta, porque el guion ejecutable captura el estado en
reposo de cada ruta y no conduce una conversación.

El sufijo `resultado` pertenece al vocabulario de los cuatro estados de la tarjeta de llamada a
herramienta —anuncio, ejecución, resultado y error—, que es el que corresponde a lo que la imagen
muestra. El vocabulario cerrado de estados del guion ejecutable, en cambio, describe estados de
pantalla y sigue siendo el del apartado anterior.

**Sobre el nombre del rol de administración.** El literal es `admin`, que es el que aceptan
`ROLES` en `frontend/app/utils/sesion.ts` y el cuerpo de `POST /api/auth/demo`. La sección 4 del
plan de la historia escribió `administrador`, un valor que no existe en ninguno de los dos sitios;
manda el código y la divergencia queda declarada aquí en lugar de traducirse en silencio.

---

## 4. Orden de la corrida y cambio de sesión

El orden es el de la tabla anterior, que es el de `PROTOTIPOS`, y no se altera: el número del
archivo tiene que corresponder al orden en que el índice del portal presenta las pantallas.

La sesión se abre **desde la interfaz**, entrando a `/acceso` y pulsando el botón del perfil de
demostración. No se abre con una petición suelta desde la terminal: la ruta de Nitro aplica
`exigirOrigenPropio` y responde 403 a una llamada que no venga del propio portal. Pulsar el botón
es además el camino que recorre una persona, que es lo que el guion documenta.

Para cambiar de rol se vuelve a `/acceso` y se pulsa otro perfil; la sesión nueva sustituye a la
anterior. Para capturar `/acceso` sin sesión se cierra la vigente con `POST /api/auth/logout` desde
el propio portal.

---

## 5. Ejecución con el guion

```bash
node docs/entregables/capturas/capturas_a4.mjs
```

| Variable | Valor por omisión | Qué controla |
|---|---|---|
| `CAPTURAS_BASE_URL` | `http://localhost:3001` | Portal bajo captura |
| `CAPTURAS_FASE` | `antes` | Elige la carpeta de salida entre `antes` y `despues` |
| `CAPTURAS_SALIDA` | — | Carpeta explícita; gana sobre `CAPTURAS_FASE` |
| `CAPTURAS_ESCALA` | 1 | Relación de píxeles del PNG. Es la escala del conjunto archivado, de modo que la corrida sin variables produce figuras comparables con las que ya están en `figuras/a4/` |

El plan de captura **se deriva de `PROTOTIPOS`** leyendo el módulo de navegación, no de una lista
tecleada en el guion. Añadir un prototipo al contrato de navegación añade su captura sin editar
este archivo, y quitarlo la retira: el guion no puede quedar desfasado respecto del portal.

`@playwright/test` se resuelve por ruta de archivo hacia `frontend/node_modules`, porque este guion
vive bajo `docs/`, donde no hay paquetes instalados ni los habrá. Si falta, el guion informa el
comando exacto que lo instala en lugar de fallar con un error de resolución de módulo:

```bash
pnpm --dir frontend add -D @playwright/test
pnpm --dir frontend exec playwright install chromium
```

---

## 6. La captura del antes y la del después

La captura del **antes** se toma con la interfaz intacta, antes de aplicar ningún hallazgo de la
pre-validación. Es irrecuperable: una vez tocada la interfaz, el antes se perdió y la iteración
documentada del criterio 6 deja de ser verificable. Se capturan **las siete pantallas** y no solo
la que se prevé cambiar, porque a la hora de capturar todavía no se sabe cuál cambiará.

La captura del **después** se toma con el cambio ya aplicado, con el mismo guion, el mismo viewport
y el mismo nombre de archivo, en `../figuras/a4/despues/`.

Para reproducir el estado del antes cuando el cambio ya está en el árbol de trabajo, se aparta el
cambio con un `git stash` acotado a los archivos que lo contienen, se corre el guion con
`CAPTURAS_FASE=antes` y se devuelve el cambio con `git stash pop`. El estado del antes queda así
definido por el código y no por el recuerdo de quien capturó.

---

## 7. Ruta manual, cuando Playwright no está

Produce el mismo conjunto sin depender de la instalación del navegador. Se recorre una vez por
pantalla, en el orden de la tabla del apartado 3.

1. Fijar la ventana del navegador a un área de contenido de 1440 x 900 píxeles CSS. En las
   herramientas de desarrollo, activar el modo de dispositivo y escribir las dos medidas a mano;
   no basta con maximizar la ventana.
2. Entrar a `/acceso` y pulsar **Claro** en el grupo «Modo de color». Verificar que el selector de
   idioma marca **ES**.
3. Capturar `/acceso` sin sesión.
4. Para cada pantalla siguiente: volver a `/acceso`, pulsar el botón del perfil que la tabla indica,
   navegar a la ruta, esperar a que el contenido termine de llegar y capturar solo el área de
   contenido, sin la barra del navegador ni el escritorio.
5. Guardar con el nombre exacto de la tabla, en `../figuras/a4/antes/` o `../figuras/a4/despues/`.
6. Comprobar que la franja de alcance aparece en las siete imágenes.

---

## 8. Reglas que ninguna captura puede saltarse

**La franja de alcance aparece en todas.** Es la pieza que impide leer el prototipo como un sistema
en producción, y su ausencia es el riesgo R10 del plan. Ninguna captura sin franja entra al PDF.
El guion espera a que la franja exista en el DOM antes de disparar, de modo que una captura sin
ella falla en vez de escribirse.

**La franja de honestidad del asistente se conserva.** El portal responde en `/asistente` con un
proveedor guionizado: el único que el backend monta es `guionizado.py`, y la clave de Gemini está
declarada como pendiente. El transporte, las tarjetas de llamada a herramienta y la cancelación son
reales; el contenido está escrito de antemano. La pantalla lo dice en su propia franja y esa franja
**no se recorta de la captura**: hacerlo presentaría un guion como respuesta viva.

Por la misma razón, los cuatro estados de la tarjeta de llamada a herramienta se documentan como
galería y no como secuencia. Es la primera válvula prevista en el plan para esta actividad.

**Ninguna captura se retoca.** Si una imagen no muestra lo que debía, se vuelve a capturar.
