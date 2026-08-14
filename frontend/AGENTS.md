# frontend/ — Nuxt 4 SSR bilingüe de Karisma Data

> Sub-guía del orquestador. Las reglas transversales viven en [`../AGENTS.md`](../AGENTS.md) — aquí no se repiten, solo lo operativo de `frontend/`.

## Estado

Las nueve rutas del contrato de navegación (`RUTAS_CONTRATO` en `app/utils/navegacion.ts`, mapa de sitio de A3) montan, pero no todas tienen producto detrás.

**Construidas**: `/` (índice público), `/acceso` (formulario y perfiles de demostración), `/inicio` (tres composiciones por rol en una sola ruta), `/exploracion/tableros` (serie ECharts sobre marco binario y tarjetas predictivas), `/gobierno` (diccionario de campos y linaje), `/guia` (láminas del sistema de diseño), `/asistente` (stream SSE real con Detener que aborta de verdad).

**Pendientes**: `/exploracion` monta `comun/EstadoPendiente.vue`, que declara las capacidades futuras y la US que las entrega. Es la única pantalla de andamiaje que queda.

**El chat ya no es andamiaje** (US-023, 13-ago-2026). `composables/useChatStream.ts` habla con `/api/chat` por `fetch` + `ReadableStream` + `AbortController` —no `EventSource`, que no admite POST ni cabeceras ni aborto— y expone `analizarTramos` a propósito, para poder probar el parser de framing con marcos partidos por la mitad sin montar un componente. El contrato vive en `app/types/chat.ts` y es **espejo verificado** de `backend/app/models/chat.py`: cuatro eventos (`tool_call`, `token`, `error`, `done`) y tres vocabularios cerrados. `components/chat/` **sigue vacío**: la tarjeta de tool call es de US-028 y el aviso de error de US-024, y `asistente.vue` deja para ellas dos bloques de fallback delimitados con comentarios HTML. `/asistente` exige `operativo` desde que `POST /api/chat` dejó de admitir cualquier sesión.

**La exportación tampoco es andamiaje** (US-009, 13-ago-2026). `/exploracion/exportar` renderiza **siempre desde estado real**: el store Pinia `exportaciones` sondea `GET /api/export/{job_id}` cada **3 000 ms** con **un único temporizador global**, que se apaga sin trabajos vivos, con `document.hidden` y a los 200 sondeos. El ciclo de vida lo arranca `app/plugins/exportaciones.client.ts` y **no un layout**: el criterio es que el estado sea consultable desde cualquier pantalla, y un `useFetch` en la página muere al navegar. La ruta acepta `?momento=solicitud|proceso|enlace`, que **no fabrica datos**: fija qué trabajo real queda expandido y desactiva el auto-avance; con historial vacío muestra el vacío explícito, nunca un enlace falso. `app/types/exportacion.ts` es espejo verificado de `backend/app/models/export.py`. El enlace firmado se usa **tal cual** —es ruta relativa y la reenvía el proxy de Nitro— y se retira solo en el instante que nombra `caduca_en`, con un disparo único por tarjeta que **se rearma**: `setTimeout` guarda su retraso en 32 bits y un plazo de más de ~24 días dispararía de inmediato.

También existen 16 composables, tres stores Pinia (`workspace`, compartido tablero↔chat; `sistemaDiseno`, modo de color; `exportaciones`, trabajos en segundo plano), un plugin de cliente, un middleware global y tres layouts. El JWT sale de la cookie solo dentro de `server/`.

## Estructura

```
frontend/
├── app/
│   ├── pages/         # las nueve rutas del contrato
│   ├── components/    # doce familias, entre ellas echarts/, serie/, tablero/ y exportacion/
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
```

pnpm exclusivo; versión fijada en `packageManager`, Node 22 (`.nvmrc`).

## Convenciones

- ❌ Escribir texto visible en template o script. Toda cadena va a `i18n/locales/es.json` **y** `en.json`, con clave jerárquica en inglés (`screen.home.description`), resuelta con `const { t } = useI18n()` de `vue-i18n`.
- ❌ Editar `app/assets/css/main.css` a mano.
- ❌ `routeRules` con `swr` en el portal: tras la guarda global, una entrada cacheada daría a un `operativo` el HTML de un `analista`. Se cachea el dato, no la página.
- `strategy: 'no_prefix'`: la URL no cambia con el idioma, y así `RUTAS_CONTRATO` sigue anclado al mapa de A3.
- El idioma viaja en la cookie `karisma_locale`: la escribe `useIdioma()` y la aplica `app.vue` antes del primer render. `detectBrowserLanguage: false` fija el arranque en español.
- Clave nueva, a los dos catálogos en el mismo commit: `test/contratos.spec.ts` los compara aplanados. `fallbackLocale: 'es'` cubre el hueco con el texto español.
- ✅ `<script setup lang="ts">`, props y emits tipados.
- ✅ `useFetch` devuelve `shallowRef` y el dataset grande se queda ahí. Pinia guarda decisiones (filtros, densidad, revelación), nunca los puntos.
- ✅ Componente pesado en forma `Lazy*`, con sufijo `.client` si toca canvas o `window`.
- ✅ ECharts solo en `app/components/echarts/VChart.client.vue`: registro modular desde `echarts/core`, nunca el barril; alto volumen con `sampling: 'lttb'` y `large: true`.
- ✅ Color, tipografía y espaciado desde los tokens `@theme`; sin valores mágicos inline.

## No tocar

- `app/assets/css/main.css` y `app/utils/tokens.generated.ts` — generados por `design/emitir.py` a partir de `design/sistema.py`, y solo por él. `make tokens` corre los dos emisores del repositorio, cada uno sobre sus propios archivos: el del informe, `docs/entregables/generar_tokens_a4.py`, ya no escribe aquí. `scripts/verificar_tokens_a4.sh` no regenera nada: compara lo que hay en disco contra lo que el emisor produce hoy, así que una edición a mano aparece como divergencia y el guion no la pisa.
- `app/utils/permisos.generated.ts` — proyección de los scopes del backend; `make permisos-ui`. Tras regenerar, `git add` antes de `make check`: el guion compara con `git diff`, y sin indexar una regeneración legítima se ve igual que una edición a mano.
- `pnpm-lock.yaml` — cambia solo vía `pnpm add` / `pnpm install`.
- `.nuxt/`, `.output/`, `node_modules/`, `coverage/` — generados; jamás commitear.
- `RUTAS_CONTRATO` — renombrar una ruta rompe las pruebas de navegación y pantallas, `scripts/smoke_rutas.sh` y el mapa de permisos.

## Tests

En `frontend/test/`: 38 `*.spec.ts` y tres auxiliares — `configuracion.ts` (Pinia nueva por prueba), `i18nDePrueba.ts` (catálogos reales) y `marcoDePrueba.ts` (marcos binarios sintéticos).

Vitest con `happy-dom` y Vue Test Utils; alias `~`/`@` hacia `app/`. Umbral en `vitest.config.ts`: 50 % de líneas, funciones, ramas y sentencias sobre `app/**` y `server/**`, sin `app/types/**` ni `tokens.generated.ts`, que no emiten runtime.

Se prueba contrato y lógica: claves i18n paritarias, pines del manifiesto, permisos contra `docs/security.md`, funciones puras, composables y montaje de pantallas. Nada sobre el marcado de `EstadoPendiente`: la US que lo sustituya lo borra.

## Skills

| Acción | Skill |
|--------|-------|
| Componentes, páginas, estados vacío/carga/error | `portal-frontend-components` |
| Composables, Pinia, middleware, sesión | `portal-frontend-composables` |
| Gráficas ECharts, alto volumen, drill-down | `portal-echarts-dashboards` |
| Cliente SSE del chat (Stop, Reintentar, tool calls) | `portal-sse-streaming` |
| Revisión contra los seis patrones UX | `portal-ux-patterns` |
| Pruebas Vitest y Vue Test Utils | `portal-testing` |
