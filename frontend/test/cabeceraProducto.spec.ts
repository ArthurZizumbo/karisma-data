import type { VueWrapper } from '@vue/test-utils'

import { mount } from '@vue/test-utils'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { defineComponent } from 'vue'
import { createMemoryHistory, createRouter } from 'vue-router'

import CabeceraProducto from '~/components/comun/CabeceraProducto.vue'
import { RUTA_INDICE } from '~/utils/navegacion'
import { crearI18nDePrueba } from './i18nDePrueba'

/**
 * US-ENTREGA-A4, ola B - the one header the four chromes share.
 *
 * The component exists because each layout had grown a header of its own and
 * the language selector ended up mounted in two of them: an evaluator who
 * opened the prototype index in English found no way to leave Spanish, because
 * `detectBrowserLanguage` is off and that control is the only route to it. This
 * wave hangs two more controls on the same row, and one of them is conditional,
 * which is exactly the shape that defect had.
 *
 * So what is measured is the row: that it is complete, that it is in the order
 * the component commits to -which is also the tab order, since nothing reorders
 * a row of buttons- and that the one control the deployment can switch off
 * takes nothing else with it.
 */

/** The four controls, in the order the header declares them. */
const CONTROLES = [
  'data-selector-rol',
  'data-selector-tema',
  'data-selector-modo',
  'data-selector-idioma',
] as const

beforeEach(() => {
  vi.stubGlobal('navigateTo', () => Promise.resolve())
  vi.stubGlobal('$fetch', () => Promise.resolve({}))
})

afterEach(() => {
  vi.unstubAllGlobals()
})

/** Mounts the header with the demonstration door in a given position. */
async function montar(demoAcceso: boolean): Promise<VueWrapper> {
  vi.stubGlobal('useRuntimeConfig', () => ({ public: { entorno: 'prueba', demoAcceso } }))

  const router = createRouter({
    history: createMemoryHistory(),
    routes: [RUTA_INDICE, '/inicio'].map(path => ({
      path,
      component: defineComponent({ template: '<div />' }),
    })),
  })
  await router.push('/inicio')
  await router.isReady()

  return mount(CabeceraProducto, {
    global: {
      plugins: [router, crearI18nDePrueba('es')],
      stubs: { Icon: true },
      components: {
        NuxtLink: defineComponent({
          props: { to: { type: String, required: true } },
          template: '<a :href="to"><slot /></a>',
        }),
      },
    },
  })
}

/** The controls the rendered header carries, in the order it paints them. */
function controlesEnOrden(wrapper: VueWrapper): string[] {
  const marcado = wrapper.html()
  return CONTROLES
    .filter(marca => marcado.includes(marca))
    .sort((uno, otro) => marcado.indexOf(uno) - marcado.indexOf(otro))
}

describe('la cabecera unica lleva la fila completa de conmutadores', () => {
  it('monta los cuatro controles y en el orden que declara', async () => {
    // The defect: a control is added to some chromes and missed in another, or
    // the row is reordered so the tab order stops being the one the component
    // commits to. Both are invisible on the screen the author was looking at.
    const wrapper = await montar(true)

    expect(controlesEnOrden(wrapper)).toEqual([...CONTROLES])
  })

  it('sin la puerta de demostracion pierde el rol y conserva los otros tres', async () => {
    // The shipped defect with the sign flipped: gating the whole group on the
    // flag instead of gating the role control alone would take the language
    // selector down with it, and precisely in the deployment where the door is
    // closed -the one nobody opens locally.
    const wrapper = await montar(false)

    expect(controlesEnOrden(wrapper)).toEqual(
      CONTROLES.filter(marca => marca !== 'data-selector-rol'),
    )
  })
})
