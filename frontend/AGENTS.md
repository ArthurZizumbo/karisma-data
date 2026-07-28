# frontend/ — Guía de carpeta (Nuxt 4)

Complementa la raíz ([`../AGENTS.md`](../AGENTS.md)); en conflicto dentro de `frontend/`, manda esta guía.

## Estructura `app/` (Nuxt 4 — no usar layout de Nuxt 3)

```
frontend/
├── app/
│   ├── pages/            # login, catalogo, explorador, dashboard, admin/usuarios
│   ├── components/       # chat/, dashboard/, admin/, common/ — pesados con prefijo Lazy*
│   ├── layouts/          # default (nav por rol), auth (login sin nav)
│   ├── composables/      # useChatStream, useSession, useSerie* (useFetch shallowRef)
│   ├── middleware/       # auth.global.ts (sesión + guarda requiredRole)
│   ├── stores/           # Pinia: workspace (estado compartido dashboard↔chat)
│   ├── types/            # tipos compartidos (chat, auth, dashboard)
│   └── assets/css/       # main.css con tokens @theme (paridad Figma, A4)
├── nuxt.config.ts        # routeRules SWR en /dashboard
└── package.json          # packageManager: pnpm (Corepack)
```

## Reglas de la carpeta

- **UI solo en español** — strings directos en templates; PROHIBIDO i18n (`useI18n`, locales). Sin emojis.
- `<script setup lang="ts">` y tipos estrictos en todo; props/emits tipados.
- **Nuxt 4**: `useFetch` devuelve `shallowRef` — jamás reactividad profunda sobre payloads masivos; componentes pesados como `Lazy*`; SWR vía `routeRules` en el dashboard directivo.
- **ECharts**: siempre `vue-echarts` como `<LazyVChart/>`, imports modulares de `echarts/core`; series >=1M puntos con agregación server-side Polars + `sampling: 'lttb'` + `large: true` (degradación acordada: 500K).
- **Pinia**: único estado cross-component; drill-down de gráficas emite al store `workspace`; sus filtros viajan como contexto del agente (TwinBI).
- **Sesión**: JWT solo en cookie httpOnly; el cliente consume `/api/auth/me`; guardas por rol en middleware y ocultamiento de módulos por scope.
- **Chat**: consumir `/api/chat` únicamente vía `useChatStream` (eventos `tool_call|token|error|done`, Stop con `AbortController`, Reintentar sin borrar historial).
- Tailwind v4 con tokens `@theme` de `main.css`; nada de valores mágicos inline.
- Sin lógica de negocio en componentes: componentes presentan, composables/stores orquestan.

## Comandos (pnpm, nunca npm/yarn)

```bash
pnpm install          # deps (lockfile pnpm-lock.yaml determinístico)
pnpm dev              # dev server (o make dev desde la raíz para el stack completo)
pnpm lint             # eslint (incluido en make lint)
pnpm test             # vitest + Vue Test Utils (cobertura >=50 %)
pnpm add <pkg>        # agregar dependencia
```

## Skills relevantes

| Acción | Skill |
|--------|-------|
| Componentes, páginas, estados skeleton/vacío/error, panel admin, login | `portal-frontend-components` |
| Composables, Pinia, middleware, sesión, estado compartido | `portal-frontend-composables` |
| Gráficas ECharts, 1M puntos, SWR, drill-down | `portal-echarts-dashboards` |
| Cliente SSE del chat (useChatStream, Stop, Reintentar) | `portal-sse-streaming` |
| Revisión contra los 6 patrones UX comprometidos | `portal-ux-patterns` |

## QA antes de PR

`make check` limpio; vitest en verde con cobertura >=50 %; si tocó chat: evento `tool_call` visible antes del texto y Stop verificado; si tocó UI: revisar contra la tabla de `portal-ux-patterns`.
