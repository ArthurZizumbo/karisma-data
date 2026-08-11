import { fileURLToPath } from 'node:url'
import vue from '@vitejs/plugin-vue'
import { defineConfig } from 'vitest/config'

const appDir = fileURLToPath(new URL('./app', import.meta.url))

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: { '~': appDir, '@': appDir },
  },
  test: {
    environment: 'happy-dom',
    include: ['test/**/*.spec.ts'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json-summary'],
      // server/ belongs in the measurement: the /api/** proxy is runtime code,
      // and leaving it out of the report made it invisible to coverage.
      include: ['app/**/*.ts', 'app/**/*.vue', 'server/**/*.ts'],
      // Type declarations emit no runtime code.
      exclude: ['app/types/**'],
      thresholds: {
        lines: 50,
        functions: 50,
        branches: 50,
        statements: 50,
      },
    },
  },
})
