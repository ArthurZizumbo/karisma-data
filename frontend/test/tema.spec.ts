import type { Ref } from 'vue'

import { mount } from '@vue/test-utils'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { defineComponent, isRef, nextTick, ref } from 'vue'

import Chasis from '~/app.vue'
import { CLAVE_COOKIE_TEMA, useTema, type TemaPortal } from '~/composables/useTema'
import { TEMA_OMISION } from '~/utils/tokens.generated'
import { crearI18nDePrueba } from './i18nDePrueba'

/**
 * US-ENTREGA-A4, ola B - the theme axis as the reader operates it.
 *
 * Nothing here asserts what a theme looks like: a colour is a decision taken in
 * `design/sistema.py` and verified by the contrast suite, not a behaviour. What
 * is measured is the behaviour the interface promises around it -that the
 * choice survives and that it reaches the first paint- because each of those
 * has a defect that shipped before.
 *
 * The control itself moved to `apariencia.spec.ts` when US-A4-EXCELENCIA
 * folded `SelectorTema` and `SelectorModo` into `SelectorApariencia`: one
 * axis, one control, one suite.
 */

/** Cookies of the current test, addressed by name as `useCookie` does. */
let galletas: Map<string, Ref<unknown>>

/** Every entry declared through `useHead` while the test ran. */
let entradas: Record<string, unknown>[]

beforeEach(() => {
  galletas = new Map<string, Ref<unknown>>()
  entradas = []

  vi.stubGlobal('useCookie', (nombre: string) => {
    if (!galletas.has(nombre)) {
      galletas.set(nombre, ref(null))
    }
    return galletas.get(nombre)!
  })
  vi.stubGlobal('useHead', (entrada: Record<string, unknown>) => {
    entradas.push(entrada)
  })
})

afterEach(() => {
  vi.unstubAllGlobals()
})

/** Value the root element would be rendered with, resolving the computed. */
function atributoDeTema(): unknown {
  for (const entrada of entradas) {
    const atributos = entrada.htmlAttrs as Record<string, unknown> | undefined
    if (atributos !== undefined && 'data-tema' in atributos) {
      const valor = atributos['data-tema']
      return isRef(valor) ? valor.value : valor
    }
  }
  return undefined
}

/** Mounts a component whose setup does nothing but read the theme. */
function montarLector(): { temaEnSetup: TemaPortal | undefined } {
  const capturado: { temaEnSetup: TemaPortal | undefined } = { temaEnSetup: undefined }
  const Lector = defineComponent({
    setup() {
      const { tema } = useTema()
      // Read inside setup on purpose: it is what proves the value is known
      // before the first render and not applied afterwards.
      capturado.temaEnSetup = tema.value
      return () => null
    },
  })
  mount(Lector)
  return capturado
}

describe('la preferencia de tema viaja en cookie y llega al primer render', () => {
  it('lee el tema guardado durante el setup, no despues de montar', () => {
    // The defect: the theme is applied on the client only, so the first paint
    // of the server uses the other one and the reader sees the flash.
    galletas.set(CLAVE_COOKIE_TEMA, ref('institucional'))

    const capturado = montarLector()

    expect(capturado.temaEnSetup).toBe('institucional')
    expect(atributoDeTema()).toBe('institucional')
  })

  it('declara el atributo a traves del head y no tocando el documento', () => {
    galletas.set(CLAVE_COOKIE_TEMA, ref('institucional'))

    montarLector()

    expect(entradas.some(entrada => 'htmlAttrs' in entrada)).toBe(true)
    expect(document.documentElement.getAttribute('data-tema')).toBeNull()
  })

  it('no anuncia el tema de omision, que es el bloque base de la hoja', () => {
    // Emitting `data-tema="corriente"` would claim an override that the
    // stylesheet does not declare, and the day one is added it would win by
    // specificity over the mode.
    const capturado = montarLector()

    expect(capturado.temaEnSetup).toBe(TEMA_OMISION)
    expect(atributoDeTema()).toBeUndefined()
  })

  it('ignora un valor de cookie que el sistema no emite', () => {
    galletas.set(CLAVE_COOKIE_TEMA, ref('tema-inventado'))

    expect(montarLector().temaEnSetup).toBe(TEMA_OMISION)
  })

  it('guarda la eleccion en la cookie que el servidor lee', () => {
    // The name is the contract between this composable and the first render:
    // written under another name the choice is remembered by nobody.
    const Escritor = defineComponent({
      setup() {
        const { fijarTema } = useTema()
        fijarTema('institucional')
        return () => null
      },
    })

    mount(Escritor)

    expect(galletas.get(CLAVE_COOKIE_TEMA)?.value).toBe('institucional')
  })

  it('el chasis aplica el tema antes de que la pagina se pinte', async () => {
    // app.vue is what renders on the server. If the attribute were declared by
    // the header instead, an error page or a layout without chrome would paint
    // in the wrong theme.
    galletas.set(CLAVE_COOKIE_TEMA, ref('institucional'))

    const Envoltura = defineComponent({
      components: { Chasis },
      template: '<Suspense><Chasis /></Suspense>',
    })

    mount(Envoltura, {
      global: {
        plugins: [crearI18nDePrueba('es')],
        components: {
          NuxtLayout: defineComponent({ template: '<div><slot /></div>' }),
          NuxtPage: defineComponent({ template: '<section />' }),
        },
      },
    })
    await nextTick()

    expect(atributoDeTema()).toBe('institucional')
  })
})

