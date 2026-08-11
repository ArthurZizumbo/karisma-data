import tailwindcss from '@tailwindcss/vite'

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
    '@nuxt/eslint',
    '@nuxt/fonts',
    '@nuxt/icon',
  ],

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
   */
  icon: {
    mode: 'svg',
    clientBundle: {
      scan: true,
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
