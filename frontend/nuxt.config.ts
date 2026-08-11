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
      ],
    },
  },
  ssr: true,
  devtools: { enabled: false },
  css: ['~/assets/css/main.css'],
  runtimeConfig: {
    // Overridable at runtime through NUXT_API_BASE.
    apiBase,
    public: {
      // Overridable at runtime through NUXT_PUBLIC_ENTORNO.
      entorno: process.env.NUXT_PUBLIC_ENTORNO ?? 'local',
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
