/**
 * Shared setup for every spec.
 *
 * Pinia is installed globally because the design system now lives in a store:
 * without it, mounting any component that reads a token fails with
 * "getActivePinia() was called but there was no active Pinia", which took the
 * whole chassis suite down when the store landed.
 *
 * A fresh instance per test keeps the mode of one spec from leaking into the
 * next: the store holds the reader's colour choice, and a leaked choice would
 * make an assertion pass or fail depending on the order the files ran in.
 */
import { createPinia, setActivePinia } from 'pinia'
import { config } from '@vue/test-utils'
import { beforeEach } from 'vitest'
import { ref } from 'vue'

/**
 * Nuxt auto-imports these; the specs run outside a Nuxt runtime.
 *
 * Assigned onto globalThis rather than through `vi.stubGlobal`, which restores
 * its stubs between files and left `useHead` undefined by the time a store
 * created inside a component called it.
 */
const alcance = globalThis as unknown as Record<string, unknown>

alcance.useCookie = (_nombre: string, opciones?: { default?: () => unknown }) =>
  ref(opciones?.default?.())
alcance.useHead = () => undefined
alcance.useRuntimeConfig = () => ({ public: { entorno: 'prueba' } })

beforeEach(() => {
  const pinia = createPinia()
  setActivePinia(pinia)
  config.global.plugins = [pinia]
})
