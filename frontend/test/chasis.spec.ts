import type { Component } from 'vue'
import type { VueWrapper } from '@vue/test-utils'

import { mount } from '@vue/test-utils'
import { afterAll, beforeAll, describe, expect, it, vi } from 'vitest'
import { defineComponent } from 'vue'
import { createMemoryHistory, createRouter, RouterLink } from 'vue-router'

import Acceso from '~/layouts/acceso.vue'
import Default from '~/layouts/default.vue'
import Portal from '~/layouts/portal.vue'
import { useSesion } from '~/composables/useSesion'
import { MODULOS, RUTA_ACCESO, RUTA_GUIA, RUTA_INDICE, RUTAS_CONTRATO } from '~/utils/navegacion'
import { crearI18nDePrueba, mensaje } from './i18nDePrueba'

/**
 * US-A4-EXCELENCIA, ola B - one chassis, and the theme is the only thing that
 * changes between the two products.
 *
 * The portal used to frame its screens three different ways: a sidebar with a
 * mark of its own on the eight contract routes, a bare column on the prototype
 * index and another one on the entry screen, each with its own header and its
 * own ground. Three chassis are three products, and every unhappy state has to
 * be built three times.
 *
 * What is measured here is the frame and not any screen: that the ten routes
 * of the contract are framed by the same pieces, that navigation carries a
 * text label and not just an icon, that no list entry of the bar is inert, and
 * that the modular grid is read from its own token. None of those can be seen
 * from inside a page, which is why they are not asserted in `pantallas.spec`.
 */

/**
 * The ten routes the criterion counts.
 *
 * Eight come from the navigation contract; the prototype index and the living
 * style guide are the other two, and they are declared apart in
 * `utils/navegacion.ts` because neither is a branch of the A3 map.
 */
const RUTAS_DEL_CHASIS: readonly string[] = Object.freeze([
  RUTA_INDICE,
  ...RUTAS_CONTRATO,
  RUTA_GUIA,
])

/**
 * Layout each route is framed by.
 *
 * The same rule `pantallas.spec.ts` holds the pages to. That suite pins what
 * each page declares; this one measures what the frame does with it.
 */
function layoutDe(ruta: string): Component {
  if (ruta === RUTA_INDICE) {
    return Default
  }
  return ruta === RUTA_ACCESO ? Acceso : Portal
}

const Vacio = defineComponent({ template: '<div />' })

const router = createRouter({
  history: createMemoryHistory(),
  routes: [...RUTAS_DEL_CHASIS].map(path => ({ path, component: Vacio })),
})

beforeAll(() => {
  vi.stubGlobal('useRuntimeConfig', () => ({ public: { entorno: 'prueba', demoAcceso: true } }))
  vi.stubGlobal('navigateTo', () => Promise.resolve())
  vi.stubGlobal('$fetch', () => Promise.resolve({}))
})

afterAll(() => {
  vi.unstubAllGlobals()
})

/**
 * Mounts the chassis of a route with an administrator signed in.
 *
 * The role is the widest one on purpose: the sidebar hides what a profile may
 * not open, and a chassis measured through a narrow role would be measured on
 * three modules out of four.
 */
async function montarChasis(ruta: string): Promise<VueWrapper> {
  const { sesion } = useSesion()
  sesion.value = { usuario: 'demo', nombre: 'Perfil de demostracion', rol: 'admin' }

  await router.push(ruta)
  await router.isReady()

  return mount(layoutDe(ruta), {
    slots: { default: '<h1>Contenido de la pantalla</h1>' },
    global: {
      plugins: [router, crearI18nDePrueba('es')],
      components: { NuxtLink: RouterLink },
      stubs: { Icon: true },
    },
  })
}

describe('las diez rutas se enmarcan con las mismas piezas', () => {
  it('cuenta diez rutas y no otra cifra', () => {
    // The number in the criterion is derived, never typed: adding a branch to
    // the A3 map has to move this count, and moving it has to be deliberate.
    expect(RUTAS_DEL_CHASIS).toHaveLength(10)
    expect(new Set(RUTAS_DEL_CHASIS).size).toBe(10)
  })

  it.each(RUTAS_DEL_CHASIS)('monta cabecera, franja y contenido en %s', async (ruta) => {
    const wrapper = await montarChasis(ruta)

    expect(wrapper.find('[data-cabecera-producto]').exists()).toBe(true)
    expect(wrapper.find('[data-franja-alcance]').exists()).toBe(true)
    expect(wrapper.get('main').attributes('id')).toBe('contenido')
    expect(wrapper.text()).toContain('Contenido de la pantalla')
  })

  it.each(RUTAS_DEL_CHASIS)('abre el orden de tabulacion con el salto al contenido en %s', async (ruta) => {
    // Without it a keyboard reader walks the six controls of the bar -and, in
    // the portal, the whole sidebar- before reaching the screen, on every one
    // of the ten routes. It has to be the FIRST focusable node, so it is
    // checked by position and not by presence.
    const wrapper = await montarChasis(ruta)
    const primero = wrapper.get('a, button, input, select, textarea, summary')

    expect(primero.attributes('href')).toBe('#contenido')
    expect(primero.text()).toBe(mensaje('es', 'chrome.skipToContent'))
  })

  it.each(RUTAS_DEL_CHASIS)('lee la reticula de su propio token en %s', async (ruta) => {
    // CA-3. The chassis borrowed `--color-grid`, the hairline of tables and
    // separators, to paint the modular grid. Under the institutional theme the
    // grid is not part of the identity and `--color-reticula` is painted with
    // the ground itself, so reading the right token is what makes the chassis
    // stop drawing a grid with no condition written in any component.
    const marcado = (await montarChasis(ruta)).html()

    expect(marcado).toContain('var(--color-reticula)')
    expect(marcado).not.toContain('var(--color-grid)')
  })
})

describe('la navegacion del portal se lee, no se adivina', () => {
  /** The eight routes framed by the portal, which is where the bar lives. */
  const RUTAS_CON_BARRA = RUTAS_DEL_CHASIS.filter(ruta => layoutDe(ruta) === Portal)

  it('son ocho: el indice y el acceso se enmarcan sin navegacion', () => {
    expect(RUTAS_CON_BARRA).toHaveLength(8)
  })

  it.each(RUTAS_CON_BARRA)('monta la barra lateral en %s', async (ruta) => {
    expect((await montarChasis(ruta)).find('[data-barra-lateral]').exists()).toBe(true)
  })

  it.each(RUTAS_CON_BARRA)('da etiqueta de texto a cada entrada de %s', async (ruta) => {
    // The criterion, in the shape a test can fail on: an icon with a tooltip
    // is not a label. Every module of the bar renders the word the navigation
    // contract gives it, and the word comes from the catalogue.
    const wrapper = await montarChasis(ruta)
    const etiquetas = wrapper
      .findAll('[data-modulo-item] > a')
      .map(enlace => enlace.text().trim())

    expect(etiquetas.length).toBeGreaterThan(0)
    for (const etiqueta of etiquetas) {
      expect(etiqueta).not.toBe('')
    }
    expect(etiquetas).toEqual(MODULOS.map(modulo => mensaje('es', modulo.claveEtiqueta)))
  })

  it.each(RUTAS_DEL_CHASIS)('no deja ningun elemento de lista sin enlace en %s', async (ruta) => {
    // CA-19, measured over the whole chassis and not only over the bar: the
    // nine inert "cross cutting facet" chips are gone, and nothing else may
    // take their place.
    const wrapper = await montarChasis(ruta)
    const inertes = wrapper.findAll('li').filter(item => !item.find('a').exists())

    expect(inertes.map(item => item.text())).toEqual([])
  })

  it('enmarca el indice y el acceso con el mismo chasis y sin navegacion', async () => {
    // Not "without a chassis": same ground, same grid, same header, same band.
    // A second frame would be a second product and would double every unhappy
    // state the prototype declares.
    for (const ruta of [RUTA_INDICE, RUTA_ACCESO]) {
      const wrapper = await montarChasis(ruta)

      expect(wrapper.findAll('nav'), ruta).toHaveLength(0)
      expect(wrapper.find('[data-barra-lateral]').exists(), ruta).toBe(false)
      expect(wrapper.find('[data-cabecera-producto]').exists(), ruta).toBe(true)
      expect(wrapper.html(), ruta).toContain('var(--color-reticula)')
    }
  })
})

describe('el producto se nombra una vez por pantalla', () => {
  it.each(RUTAS_DEL_CHASIS)('monta una sola marca en %s', async (ruta) => {
    // The portal named itself twice -sidebar and header- and the two screens
    // without a sidebar named it once. One mark per screen, and it is the
    // vector one: no packaged icon stands in for it anywhere in the chassis.
    const wrapper = await montarChasis(ruta)

    expect(wrapper.findAll('[data-marca-karisma]')).toHaveLength(1)
    expect(wrapper.findAll('img')).toHaveLength(0)

    // Scoped to the mark itself: `lucide:circuit-board` is still a legitimate
    // icon of this system -it names the default theme inside the appearance
    // panel- and what the criterion forbids is it standing in for a logotype.
    const marca = wrapper.get('[data-marca-enlace]')

    expect(marca.find('[data-marca-karisma] svg').exists()).toBe(true)
    expect(marca.html()).not.toContain('circuit-board')
  })
})
