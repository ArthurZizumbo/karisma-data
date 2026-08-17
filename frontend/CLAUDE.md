# frontend/ — Nuxt 4 SSR bilingüe de Karisma Data

> Sub-guía del orquestador. Las reglas transversales viven en [`../AGENTS.md`](../AGENTS.md) — aquí no se repiten, solo lo operativo de `frontend/`.

## Estado

Las **ocho** rutas del contrato de navegación (`RUTAS_CONTRATO` en `app/utils/navegacion.ts`, mapa de sitio de A3) montan, pero no todas tienen producto detrás. **El chasis se mide sobre diez**: esas ocho más `/` y `/guia`, que no son ramas del mapa pero sí pantallas que el evaluador abre. Donde antes esta guía decía «nueve» no había ninguna: la cuenta estaba mal y se corrigió midiendo, no recordando.

**Construidas**: `/` (índice público), `/acceso` (formulario y perfiles de demostración), `/inicio` (tres composiciones por rol en una sola ruta), `/exploracion/tableros` (serie ECharts sobre marco binario y tarjetas predictivas), `/gobierno` (diccionario de campos y linaje), `/guia` (láminas del sistema de diseño), `/asistente` (stream SSE real con Detener que aborta de verdad), `/exploracion` (catalogo tematico sobre `useBusquedaCatalogo`, con sus cuatro estados no felices).

**Ya no queda andamiaje** (US-ENTREGA-A4, 14-ago-2026). `/exploracion` era la última pantalla que montaba `comun/EstadoPendiente.vue` y ahora compone desde `useBusquedaCatalogo`. **El componente sigue en disco** y ya no lo usa nada de `app/`: solo lo nombran `exploracionCatalogo.spec.ts`, para comprobar su ausencia, y `modoYSistema.spec.ts`. Borrarlo es trabajo de quien lo necesite, no de esta guía.

**El chat ya no es andamiaje** (US-023, 13-ago-2026). `composables/useChatStream.ts` habla con `/api/chat` por `fetch` + `ReadableStream` + `AbortController` —no `EventSource`, que no admite POST ni cabeceras ni aborto— y expone `analizarTramos` a propósito, para poder probar el parser de framing con marcos partidos por la mitad sin montar un componente. El contrato vive en `app/types/chat.ts` y es **espejo verificado** de `backend/app/models/chat.py`: cuatro eventos (`tool_call`, `token`, `error`, `done`) y tres vocabularios cerrados. `components/chat/` **sigue vacío**: la tarjeta de tool call es de US-028 y el aviso de error de US-024, y `asistente.vue` deja para ellas dos bloques de fallback delimitados con comentarios HTML. `/asistente` exige `operativo` desde que `POST /api/chat` dejó de admitir cualquier sesión.

**La exportación tampoco es andamiaje** (US-009, 13-ago-2026). `/exploracion/exportar` renderiza **siempre desde estado real**: el store Pinia `exportaciones` sondea `GET /api/export/{job_id}` cada **3 000 ms** con **un único temporizador global**, que se apaga sin trabajos vivos, con `document.hidden` y a los 200 sondeos. El ciclo de vida lo arranca `app/plugins/exportaciones.client.ts` y **no un layout**: el criterio es que el estado sea consultable desde cualquier pantalla, y un `useFetch` en la página muere al navegar. La ruta acepta `?momento=solicitud|proceso|enlace`, que **no fabrica datos**: fija qué trabajo real queda expandido y desactiva el auto-avance; con historial vacío muestra el vacío explícito, nunca un enlace falso. `app/types/exportacion.ts` es espejo verificado de `backend/app/models/export.py`. El enlace firmado se usa **tal cual** —es ruta relativa y la reenvía el proxy de Nitro— y se retira solo en el instante que nombra `caduca_en`, con un disparo único por tarjeta que **se rearma**: `setTimeout` guarda su retraso en 32 bits y un plazo de más de ~24 días dispararía de inmediato.

**La entrega de A4 dejó rastro aquí** (US-UX-07, 14-ago-2026). `@playwright/test` es dependencia de desarrollo y el navegador está descargado: lo usa `docs/entregables/capturas/capturas_a4.mjs`, un guion que vive fuera de `frontend/` y **lee `app/utils/navegacion.ts` parseándolo como texto** para derivar su plan de captura. Los tres layouts pasan `max-w-none` a `FranjaAlcance` por el motivo que explica la sección de convenciones. Y dos pruebas nuevas —`rutaRama.spec.ts` y `alcancePrototipos.spec.ts`— **leen archivos `.tex` de `docs/entregables/`** y los comparan contra el contrato de navegación: es la primera vez que la suite del frontend toma un entregable como insumo.

**El sistema de diseño tiene dos ejes desde A4** (US-ENTREGA-A4, 14-ago-2026). Al **tema** (`corriente` de omisión, `institucional` opcional con su propia paleta y con Inter) y al **modo** (claro/oscuro) los emite `design/emitir.py` en el mismo CSS generado. El atributo que transportaba el modo se llamaba `data-theme` y **ahora es `data-modo`**; el tema entra como `data-tema` y el de omisión no lo emite, porque es el bloque `@theme` de la hoja. Los dos viajan en cookie —`karisma_modo` y `karisma_tema`— y `app.vue` los aplica antes del primer render, igual que el idioma. La cabecera **ya no monta cuatro conmutadores**; ver el párrafo de US-A4-EXCELENCIA. **El de rol solo existe con `DEMO_LOGIN_ENABLED`** y acuña sesión de verdad contra `POST /api/auth/demo`: nunca cambia el rol en el cliente, porque la guarda decide en el servidor. La misma bandera gobierna que la tarjeta del índice acuñe la sesión de su `rolSugerido`. El rebote sin sesión dejó de ser mudo: la guarda manda `?destino=<ruta>&motivo=sesion-requerida` y `utils/guarda.ts` **valida el destino contra `RUTAS_CONTRATO`**, porque una pantalla que confía en su propio query string está a un enlace de una redirección abierta.

**El chasis pasó a barra lateral y el tema institucional se completó** (US-A4-EXCELENCIA, 15-ago-2026). Los dos temas comparten **un solo chasis** —dos habrían sido dos productos y habrían duplicado cada estado no feliz—, y la identidad viaja en los tokens: el de omisión conserva retícula y activo por luminancia; el institucional pinta la barra en navy, rellena la acción en verde azulado y **no pinta retícula**, porque `--color-reticula` se resuelve a su propio suelo y `layouts/portal.vue` lo lee en vez de `--color-grid`. `design/` emite **28 tokens de color** (eran 21) con dos grupos nuevos, `BARRA_LATERAL` y `CERTIFICACION`, y un `ESTADOS_CERTIFICACION` que empareja color **e icono**: los tres estados de un campo dejaron de compartir triángulo, que es lo que hacía que «En revisión» y «Obsoleto» —opuestos— se leyeran igual. **El cromo bajó de 11 controles a 6**: `SelectorTema.vue` y `SelectorModo.vue` desaparecieron dentro de `SelectorApariencia.vue` —tema y modo son el mismo eje— y la cabecera monta cinco ranuras: marca, buscador, apariencia, perfil e idioma. La marca es `comun/MarcaKarisma.vue`, **SVG en línea con tres variantes**, medida sobre la página normativa del archivo de diseño; antes era un icono genérico del paquete. De la barra lateral salieron las nueve etiquetas inertes de «facetas transversales»: eran el card sorting de A3 renderizado como navegación, `listitem` sin enlace, y su mapa completo vive en el entregable.

**Las tablas son headless y `/exploracion` dejó de ser un callejón** (misma US). `comun/TablaDatos.vue` monta **TanStack Table v9** —`useTable`, características declaradas con `tableFeatures({...})`; **un ejemplo de v8 copiado de internet no compila**— y da orden real, `aria-sort` y fila de 34 px, que es la densidad que `DESIGN.md` declaraba y ninguna tabla entregaba. La usan `administracion/TablaUsuarios`, `tablero/TablaDetalleSerie`, `serie/Tabla` y el catálogo; siguen a mano `guia/LaminaTablas` —que es la lámina normativa de la que sale el aspecto—, `guia/LaminaBotones`, `pages/guia.vue` y `chat/ToolCallCard`. `comun/TarjetaContenida.vue` es la superficie del sistema (filete, radio por tema, barra de canal) y `inicio/TarjetaIndicador.vue` la de cifra. En `/exploracion` **cada fila abre el linaje con el mismo `OverlayLinaje` y el mismo `useLinajeCampo` que monta `/gobierno`**: montar un segundo panel habría sido una segunda respuesta a «de dónde sale esto». El término vive en la dirección (`?q=`), `useBusquedaCatalogo` recibe opciones —con y sin sincronización de URL, las dos con consumidor real— y exporta `certificacionDeCampo()`, que cruza la ortografía del cable (`en_revision`) con la del token (`en-revision`).

También existen 18 composables, tres stores Pinia (`workspace`, compartido tablero↔chat; `sistemaDiseno`, **tema y modo** de color; `exportaciones`, trabajos en segundo plano), un plugin de cliente, un middleware global y tres layouts. El JWT sale de la cookie solo dentro de `server/`.

## Estructura

```
frontend/
├── app/
│   ├── pages/         # las ocho rutas del contrato, mas / y /guia
│   ├── components/    # catorce familias, entre ellas echarts/, serie/, tablero/, exportacion/ y exploracion/
│   ├── layouts/       # default, portal (nav por rol), acceso
│   ├── composables/ · middleware/ · plugins/ · stores/ · types/
│   ├── utils/         # puros + permisos.generated.ts + tokens.generated.ts
│   └── assets/css/    # main.css — GENERADO
├── i18n/              # i18n.config.ts + locales/{es,en}.json
├── server/            # api/[...].ts (proxy) + api/auth/{token,demo,logout}
├── public/datos/ · test/
└── nuxt.config.ts · vitest.config.ts · eslint.config.mjs · pnpm-workspace.yaml
```

## Comandos

```bash
pnpm dev          # nuxt dev --dotenv .env.local
pnpm lint         # eslint .
pnpm typecheck    # nuxt typecheck (vue-tsc)
pnpm test         # vitest run --coverage

make dev          # (raíz) db + api + web con Docker Compose
make lint/test    # (raíz) incluyen pnpm --dir frontend
make tokens       # regenera main.css y tokens.generated.ts
make permisos-ui  # regenera permisos.generated.ts

# Capturas del entregable. El guion vive en docs/ y usa el navegador instalado aqui.
pnpm exec playwright install chromium          # una vez por maquina
node ../docs/entregables/capturas/capturas_a4.mjs   # CAPTURAS_FASE=antes|despues
```

pnpm exclusivo; versión fijada en `packageManager`, Node 22 (`.nvmrc`).

## Convenciones

- ❌ Escribir texto visible en template o script. Toda cadena va a `i18n/locales/es.json` **y** `en.json`, con clave jerárquica en inglés (`screen.home.description`), resuelta con `const { t } = useI18n()` de `vue-i18n`.
- ❌ Editar `app/assets/css/main.css` a mano.
- ❌ Escribir `data-theme`. El modo va en **`data-modo`** y el tema en **`data-tema`**: un atributo con nombre prestado garantiza que el siguiente eje no quepa. El tema de omisión **no emite `data-tema`**; solo el institucional lo declara.
- ❌ `routeRules` con `swr` en el portal: tras la guarda global, una entrada cacheada daría a un `operativo` el HTML de un `analista`. Se cachea el dato, no la página.
- `strategy: 'no_prefix'`: la URL no cambia con el idioma, y así `RUTAS_CONTRATO` sigue anclado al mapa de A3.
- El idioma viaja en la cookie `karisma_locale`: la escribe `useIdioma()` y la aplica `app.vue` antes del primer render. `detectBrowserLanguage: false` fija el arranque en español.
- Clave nueva, a los dos catálogos en el mismo commit: `test/contratos.spec.ts` los compara aplanados. `fallbackLocale: 'es'` cubre el hueco con el texto español.
- ✅ `<script setup lang="ts">`, props y emits tipados.
- ✅ `useFetch` devuelve `shallowRef` y el dataset grande se queda ahí. Pinia guarda decisiones (filtros, densidad, revelación), nunca los puntos.
- ✅ Componente pesado en forma `Lazy*`, con sufijo `.client` si toca canvas o `window`.
- ✅ ECharts solo en `app/components/echarts/VChart.client.vue`: registro modular desde `echarts/core`, nunca el barril; alto volumen con `sampling: 'lttb'` y `large: true`.
- ✅ Color, tipografía y espaciado desde los tokens `@theme`; sin valores mágicos inline.
- ✅ Los tokens se leen del store `sistemaDiseno`, **nunca del módulo generado**: el store es lo único que sabe el tema y el modo en pantalla, y así un renombre en el emisor llega a un archivo y no a cada consumidor. La única importación admitida de `tokens.generated` es de **tipos**.
- ⚠️ **La marca es la única excepción al «color desde los tokens»**, y está declarada en el propio componente con su razón: `--color-accion` es teal solo bajo el institucional, así que pintar la teja con el token repintaría el logotipo al cambiar de tema, que es lo que la guía de marca prohíbe. `marca.spec.ts` falla si aparece `var(--color-` en su marcado. Falta un grupo `marca-*` invariante en `design/`; mientras no exista, esos cuatro hex viven ahí.
- ❌ Ordenar una tabla por el texto impreso. **El orden se computa sobre el valor crudo**: las cifras llegan formateadas y `1 284,5` contra `987,6` es un orden alfabético disfrazado de numérico. Y `aria-sort` solo se declara donde de verdad se puede ordenar: anunciarlo en una columna de botones ofrece al lector una capacidad que no existe.
- ⚠️ **Un elemento de rejilla conserva `min-width: auto`** y no baja de su tamaño min-content; con `truncate` (`white-space: nowrap`) ese min-content es la frase entera. Es el defecto simétrico del de la medida de lectura y costó 161 px de desplazamiento horizontal en `/inicio`: cualquier bloque dentro de un `grid-cols-*` que contenga texto truncado necesita `min-w-0` en el bloque, en la fila y en el item.
- ❌ Publicar el término de búsqueda con `push`. Va con **`replace`**: con `push` cada búsqueda deja una entrada y el botón Atrás de quien salió a los tableros aterriza en el catálogo **sin** el término.
- ❌ Elegir en el componente el icono o el color de un estado de certificación. Salen de `ESTADOS_CERTIFICACION`, que empareja los dos; el componente que elige forma es exactamente cómo dos estados opuestos acabaron compartiendo triángulo.
- ⚠️ **Un `<p>` hereda la medida de lectura.** `main.css` aplica `max-width: var(--medida-maxima)` —68ch— a `p:not([class*='max-w'])` y a `li`, con las excepciones de celda de tabla y navegación. Es correcto para prosa y equivocado para cualquier elemento a todo el ancho: una franja, un aviso de sistema o una barra compuesta como párrafo salen a 455 px dentro de una columna de 1193 y se leen como una tarjeta suelta. Se sale con `max-w-none`, que **desactiva la regla y fija el valor a la vez**, porque la propia regla se excluye con `:not([class*='max-w'])` y así no depende de ganar un empate de especificidad. Es lo que hacen los tres layouts con `FranjaAlcance`.

## No tocar

- `app/assets/css/main.css` y `app/utils/tokens.generated.ts` — generados por `design/emitir.py` a partir de `design/sistema.py`, y solo por él. `make tokens` corre los dos emisores del repositorio, cada uno sobre sus propios archivos: el del informe, `docs/entregables/generar_tokens_a4.py`, ya no escribe aquí. `scripts/verificar_tokens_a4.sh` no regenera nada: compara lo que hay en disco contra lo que el emisor produce hoy, así que una edición a mano aparece como divergencia y el guion no la pisa.
- `app/utils/permisos.generated.ts` — proyección de los scopes del backend; `make permisos-ui`. Tras regenerar, `git add` antes de `make check`: el guion compara con `git diff`, y sin indexar una regeneración legítima se ve igual que una edición a mano.
- `pnpm-lock.yaml` — cambia solo vía `pnpm add` / `pnpm install`.
- `.nuxt/`, `.output/`, `node_modules/`, `coverage/` — generados; jamás commitear.
- `RUTAS_CONTRATO` — renombrar una ruta rompe las pruebas de navegación y pantallas, `scripts/smoke_rutas.sh` y el mapa de permisos.
- `PROTOTIPOS` — además de alimentar el índice, **lo parsea como texto un guion de fuera del frontend**, `docs/entregables/capturas/capturas_a4.mjs`, que deriva de ahí su plan de captura. Renombrar la constante, o cambiar la forma del literal a algo que no sea una lista de objetos planos, deja el guion sin plan y sin las figuras del entregable. El campo `alcance` lo publica el PDF de A4 y `test/alcancePrototipos.spec.ts` compara los dos: cambiar uno sin el otro pone la suite en rojo, que es lo que debe pasar.

## Tests

En `frontend/test/`: **53 `*.spec.ts`** y **1 063 pruebas**, más cuatro auxiliares — `configuracion.ts` (Pinia nueva por prueba), `i18nDePrueba.ts` (catálogos reales) y `marcoDePrueba.ts` (marcos binarios sintéticos) y el directorio `dobles/`.

Vitest con `happy-dom` y Vue Test Utils; alias `~`/`@` hacia `app/`. Umbral en `vitest.config.ts`: 50 % de líneas, funciones, ramas y sentencias sobre `app/**` y `server/**`, sin `app/types/**` ni `tokens.generated.ts`, que no emiten runtime.

Se prueba contrato y lógica: claves i18n paritarias, pines del manifiesto, permisos contra `docs/security.md`, funciones puras, composables y montaje de pantallas. Nada sobre el marcado de `EstadoPendiente`, que ya no monta ninguna pantalla.

**Dos pruebas leen entregables.** `rutaRama.spec.ts` y `alcancePrototipos.spec.ts` abren archivos `.tex` de `docs/entregables/contenido/` y los comparan contra `MODULOS` y `PROTOTIPOS`: el defecto que atajan es que el PDF calificado afirme una cobertura o un alcance que el código no tiene. Siguen el patrón de `permisos.spec.ts` —`leerDelRepositorio()` con la ruta en una variable, porque con un literal Vite reescribe `new URL(..., import.meta.url)` como referencia de recurso— y **acotan lo que leen con delimitadores de comentario LaTeX** (`% tabla-ruta-rama:inicio` / `:fin`). Si falta el archivo, la prueba **falla con el motivo**; no se salta: una prueba que se ausenta cuando falta su insumo no es una barrera.

## Skills

| Acción | Skill |
|--------|-------|
| Componentes, páginas, estados vacío/carga/error | `portal-frontend-components` |
| Composables, Pinia, middleware, sesión | `portal-frontend-composables` |
| Gráficas ECharts, alto volumen, drill-down | `portal-echarts-dashboards` |
| Cliente SSE del chat (Stop, Reintentar, tool calls) | `portal-sse-streaming` |
| Revisión contra los seis patrones UX | `portal-ux-patterns` |
| Pruebas Vitest y Vue Test Utils | `portal-testing` |
