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
import type { Ref } from 'vue'
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

const estadosCompartidos = new Map<string, Ref<unknown>>()

alcance.useCookie = (_nombre: string, opciones?: { default?: () => unknown }) =>
  ref(opciones?.default?.())
alcance.useHead = () => undefined
alcance.useRuntimeConfig = () => ({ public: { entorno: 'prueba' } })

/**
 * `useState`, shared per test and reset between tests.
 *
 * Since US-017 the session guard projects its state through `useState`, so any
 * component that reads a role -the sidebar, the portal layout, the prototype
 * index- needs one to mount at all. A spec that wants to drive that state still
 * replaces this double with `vi.stubGlobal`; this one only keeps mounting from
 * throwing in the specs that do not care who is signed in.
 *
 * The map is cleared before every test on purpose: a session left behind by one
 * spec would decide what another spec renders, and the two would pass or fail
 * depending on the order the files ran in.
 */
alcance.useState = (clave: string, inicial?: () => unknown) => {
  if (!estadosCompartidos.has(clave)) {
    estadosCompartidos.set(clave, ref(inicial?.() ?? null))
  }
  return estadosCompartidos.get(clave)!
}

/**
 * `useRequestFetch`, which on the client is `$fetch` itself.
 *
 * Read from `globalThis` at call time and not captured: the specs that measure
 * requests replace `$fetch` with `vi.stubGlobal`, and a captured reference
 * would keep calling the one that existed when this file was loaded.
 */
alcance.useRequestFetch = () => alcance.$fetch

beforeEach(() => {
  const pinia = createPinia()
  setActivePinia(pinia)
  config.global.plugins = [pinia]
  estadosCompartidos.clear()
})
