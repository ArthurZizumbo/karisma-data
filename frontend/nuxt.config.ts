import tailwindcss from '@tailwindcss/vite'
import { NOMBRES_EMPAQUETADOS } from './app/components/guia/inventarioIconos'

/**
 * Base URL of the FastAPI service. Nitro proxies /api/** to it so the browser
 * always talks to a single origin: no CORS layer is required anywhere.
 *
 * The value below is only the build-time default. The proxy itself lives in
 * server/api/[...].ts and re-reads runtimeConfig.apiBase on every request, so
 * NUXT_API_BASE reconfigures an already-built image. A `routeRules` proxy could
 * not: route rules are frozen into the Nitro bundle at build time.
 */
const apiBase = process.env.NUXT_API_BASE ?? 'http://localhost:8000'

/**
 * Bind mounts on Windows do not emit inotify events, so the dev watcher needs
 * polling inside Compose. Enabled only when the container asks for it.
 */
const usePolling
  = process.env.WATCHPACK_POLLING === 'true' || process.env.CHOKIDAR_USEPOLLING === 'true'

export default defineNuxtConfig({
  modules: [
    '@pinia/nuxt',
    '@nuxt/eslint',
    '@nuxt/fonts',
    '@nuxt/icon',
    '@nuxtjs/i18n',
    '@vueuse/nuxt',
  ],

  /**
   * Bilingual interface, decided on 10-ago-2026: Spanish and English with real
   * i18n. Only the web application is bilingual; the A4 deliverable stays in
   * Spanish.
   *
   * `strategy: 'no_prefix'` is the load bearing choice. RUTAS_CONTRATO is
   * anchored to the A3 site map and pinned by test/navegacion.spec.ts and by
   * scripts/smoke_rutas.sh; a /en/ prefix would rewrite all nine URLs and break
   * both. The language travels in a cookie and the addresses never change.
   *
   * `detectBrowserLanguage: false` is equally deliberate. With detection on,
   * the module resolves the locale as cookie -> accept-language -> navigator,
   * so an evaluator whose browser is configured in English would open the demo
   * in English on the first visit. Disabling it makes the boot deterministic
   * (always Spanish) and moves the cookie to app code: useIdioma() writes
   * `karisma_locale` when the reader chooses, and app.vue applies it before the
   * first render, which is why there is no flash of the wrong language.
   */
  i18n: {
    strategy: 'no_prefix',
    defaultLocale: 'es',
    detectBrowserLanguage: false,
    locales: [
      { code: 'es', language: 'es-MX', file: 'es.json' },
      { code: 'en', language: 'en-US', file: 'en.json' },
    ],
  },

  /**
   * The two families declared in the @theme block of main.css were tokens with
   * nothing behind them: no @font-face, no link tag, so every screen fell back
   * to the system sans-serif and the A4 screenshots would not match the PDF.
   * The module downloads them at build time and serves them from this origin,
   * which also keeps the Playwright captures deterministic: a remote font
   * introduces a flash of unstyled text that changes between runs.
   */
  fonts: {
    families: [
      { name: 'Lexend Deca', provider: 'google' },
      { name: 'Fira Sans', provider: 'google' },
    ],
  },

  /**
   * One icon family only, per rule 3 of the interface checklist. The Lucide
   * collection is installed as a package so the icons are bundled instead of
   * fetched from the Iconify API at runtime.
   *
   * `scan` alone is not enough for /guia. The scanner reads the sources looking
   * for literal names, and the icon plate iterates an inventory, so every
   * `:name` there is assembled at run time and no scan can see it: under
   * `nuxt dev` the module still answers through the Iconify API and the plate
   * looks complete, while the production bundle ships it empty. Declaring the
   * inventory here closes that gap, and it is the same array the plate walks,
   * so the two cannot drift.
   */
  icon: {
    mode: 'svg',
    clientBundle: {
      scan: true,
      icons: [
        ...NOMBRES_EMPAQUETADOS,
        // Chassis inventory. `scan: true` does not see a name composed at
        // runtime, so the sidebar and the header declare theirs here and the
        // components read from the same literals.
        'lucide:circle',
        'lucide:circuit-board',
        'lucide:contrast',
        'lucide:git-branch',
        'lucide:house',
        'lucide:message-square',
        'lucide:monitor',
        'lucide:moon',
        'lucide:search',
        'lucide:settings',
        'lucide:shield-check',
        'lucide:sun',
        // Dashboard inventory (US-025). The six marker shapes come from the
        // series palette, where they are composed from a table at run time, so
        // the scanner cannot see them either.
        'lucide:copy',
        'lucide:database',
        'lucide:diamond',
        'lucide:filter-x',
        'lucide:gauge',
        'lucide:info',
        'lucide:map-pin',
        'lucide:maximize',
        'lucide:navigation',
        'lucide:refresh-cw',
        'lucide:square',
        'lucide:table',
        'lucide:triangle',
        'lucide:triangle-alert',
      ],
    },
  },
  /**
   * One extra scan root, and it exists for a single reason: the name.
   *
   * `frontend/AGENTS.md` and CA-2 of US-025 require the chart to be written as
   * `<LazyVChart/>`. With the default `pathPrefix: true` the wrapper in
   * `app/components/echarts/VChart.client.vue` would auto-import as
   * `EchartsVChart`, so the required name would simply not exist. Declaring the
   * directory without the prefix registers it as `VChart`, and Nuxt derives the
   * lazy form from that. The second entry restores the default behaviour for
   * the rest of `components/`, which every screen consumes through explicit
   * imports and stays as it is.
   */
  components: [
    { path: '~/components/echarts', pathPrefix: false },
    { path: '~/components', pathPrefix: true },
  ],

  /**
   * No `routeRules` here, and the omission is a decision rather than a gap.
   *
   * The dashboard skill proposes `swr` on the dashboard route. `/exploracion/
   * tableros` sits behind the global guard, which resolves the session during
   * SSR and renders the "no permission" state in place: an SWR entry caches the
   * rendered HTML per route, so it would hand an `operativo` the markup that
   * was rendered for an `analista`. What replaces it is caching of the DATA and
   * not of the page -ETag plus `Cache-Control: private, max-age=300` on
   * `GET /api/metrics/series`- which lives in the browser of the authorised
   * reader and never in a shared cache.
   */
  ssr: true,
  devtools: { enabled: false },
  css: ['~/assets/css/main.css'],
  runtimeConfig: {
    // Overridable at runtime through NUXT_API_BASE.
    apiBase,
    public: {
      // Overridable at runtime through NUXT_PUBLIC_ENTORNO.
      entorno: process.env.NUXT_PUBLIC_ENTORNO ?? 'local',
      // Whether the entry screen offers the credential-free demonstration
      // profiles. This flag only decides what is shown: the real gate is
      // DEMO_LOGIN_ENABLED on the backend, which does not even mount the route
      // when it is off. On by default because the prototype is evaluated with
      // the door open; a deployment that closes it sets NUXT_PUBLIC_DEMO_ACCESO
      // to false so the interface stops advertising a door that answers 404.
      demoAcceso: process.env.NUXT_PUBLIC_DEMO_ACCESO !== 'false',
      // Mirror of EXPORT_DEMO_DELAY_SECONDS on the backend, which stretches a
      // real export so its in-progress state can be captured. The interface
      // cannot read that setting -no endpoint publishes it- and deriving it
      // from how long a job took would state a delay nobody configured, so the
      // honesty notice is driven by this value instead. Zero, the default,
      // hides the notice because there is nothing artificial to declare.
      exportDemoDelay: Number(process.env.NUXT_PUBLIC_EXPORT_DEMO_DELAY ?? 0),
    },
  },
  compatibilityDate: '2026-08-10',
  vite: {
    plugins: [tailwindcss()],
    server: {
      watch: usePolling ? { usePolling: true, interval: 400 } : undefined,
    },
  },
})
