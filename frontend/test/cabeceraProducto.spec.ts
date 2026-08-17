import type { VueWrapper } from '@vue/test-utils'

import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'

import { mount } from '@vue/test-utils'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { defineComponent, nextTick } from 'vue'
import { createMemoryHistory, createRouter } from 'vue-router'

import CabeceraProducto from '~/components/comun/CabeceraProducto.vue'
import { PARAMETRO_TERMINO } from '~/composables/useBusquedaCatalogo'
import { MODULOS, RUTA_INDICE } from '~/utils/navegacion'
import { crearI18nDePrueba, mensaje } from './i18nDePrueba'

/**
 * US-A4-EXCELENCIA, ola B - the chrome, counted.
 *
 * The design review measured eleven interactive controls in this bar and not
 * one label, and the mechanical pass found the profile switcher rendering at
 * `left: -144.4` on a 390 px viewport, on a bar that does not scroll. Both are
 * defects of the row itself and not of any one control, so the row is what is
 * measured here: how many controls it costs at rest, which slots it carries
 * and in which order, and that the two panels open towards the inside of the
 * canvas instead of past its edge.
 *
 * The count is taken with the panels closed, because that is the state the
 * reader finds and the state a viewport measurement sees.
 */

/** The five slots of the bar, in the order the header commits to. */
const RANURAS = [
  'data-marca-enlace',
  'data-buscador-cromo',
  'data-selector-apariencia',
  'data-perfil-cromo',
  'data-selector-idioma',
] as const

/** Ceiling the acceptance criterion sets for the bar at rest. */
const TOPE_DE_CONTROLES = 6

/**
 * Source of the header, read to prove it declares no parameter of its own.
 *
 * The path travels as a variable for the same reason as in
 * `exploracionCatalogo.spec.ts`: with a literal, Vite rewrites the
 * `new URL(..., import.meta.url)` pattern into an asset reference and the URL
 * stops being a file one.
 */
const RUTA_FUENTE_CABECERA = '../app/components/comun/CabeceraProducto.vue'

/** Anything a keyboard stops on. */
const CONTROLES = 'a, button, input, select, textarea, summary, [role="button"]'

const RUTA_CATALOGO = MODULOS.find(modulo => modulo.id === '2')!.ruta

let navegaciones: unknown[]

beforeEach(() => {
  navegaciones = []
  vi.stubGlobal('navigateTo', (destino: unknown) => {
    navegaciones.push(destino)
    return Promise.resolve()
  })
  vi.stubGlobal('$fetch', () => Promise.resolve({}))
})

afterEach(() => {
  vi.unstubAllGlobals()
})

/** Mounts the header with the demonstration door in a given position. */
async function montar(
  demoAcceso: boolean,
  ruta: string = '/inicio',
): Promise<VueWrapper> {
  vi.stubGlobal('useRuntimeConfig', () => ({ public: { entorno: 'prueba', demoAcceso } }))

  const router = createRouter({
    history: createMemoryHistory(),
    routes: [RUTA_INDICE, '/inicio', RUTA_CATALOGO].map(path => ({
      path,
      component: defineComponent({ template: '<div />' }),
    })),
  })
  await router.push(ruta)
  await router.isReady()

  return mount(CabeceraProducto, {
    global: {
      plugins: [router, crearI18nDePrueba('es')],
      stubs: { Icon: true },
      components: {
        NuxtLink: defineComponent({
          props: { to: { type: [String, Object], required: true } },
          template: '<a :href="typeof to === \'string\' ? to : to.path"><slot /></a>',
        }),
      },
    },
  })
}

/** The slots the rendered bar carries, in the order it paints them. */
function ranurasEnOrden(wrapper: VueWrapper): string[] {
  const marcado = wrapper.html()
  return RANURAS
    .filter(marca => marcado.includes(marca))
    .sort((uno, otro) => marcado.indexOf(uno) - marcado.indexOf(otro))
}

describe('la cabecera cabe en el presupuesto de controles', () => {
  it('no pasa de seis controles interactivos con todo encendido', async () => {
    // The criterion, verbatim: eleven down to six. It is asserted with the
    // demonstration door OPEN, which is the expensive configuration and the
    // one every capture of the deliverable is taken in.
    const wrapper = await montar(true)

    expect(wrapper.get('[data-cabecera-producto]').findAll(CONTROLES).length)
      .toBeLessThanOrEqual(TOPE_DE_CONTROLES)
  })

  it('monta las cinco ranuras y en el orden que declara', async () => {
    // The defect: a control is added to some chromes and missed in another, or
    // the row is reordered so the tab order stops being the one the component
    // commits to. Both are invisible on the screen the author was looking at.
    const wrapper = await montar(true)

    expect(ranurasEnOrden(wrapper)).toEqual([...RANURAS])
  })

  it('sin la puerta de demostracion pierde el perfil y conserva el resto', async () => {
    // The shipped defect with the sign flipped: gating the whole group on the
    // flag instead of gating the profile control alone would take the language
    // selector down with it, and precisely in the deployment where the door is
    // closed -the one nobody opens locally.
    const wrapper = await montar(false)

    expect(ranurasEnOrden(wrapper)).toEqual(
      RANURAS.filter(marca => marca !== 'data-perfil-cromo'),
    )
  })
})

describe('los conmutadores plegados no dejan opciones fuera del lienzo', () => {
  it('empieza con el perfil plegado y lo declara', async () => {
    const wrapper = await montar(true)

    expect(wrapper.get('[data-perfil-abrir]').attributes('aria-expanded')).toBe('false')
    expect(wrapper.find('[data-perfil-panel]').exists()).toBe(false)
    expect(wrapper.find('[data-selector-rol]').exists()).toBe(false)
  })

  it('abre el perfil sobre el conmutador real, no sobre una copia', async () => {
    // The four profiles mint a real session through `POST /api/auth/demo`.
    // Folding them behind a disclosure may not fork that control into a second
    // implementation: the panel mounts the same component the entry screen
    // does, so the door stays one door.
    const wrapper = await montar(true)

    await wrapper.get('[data-perfil-abrir]').trigger('click')
    await nextTick()

    expect(wrapper.get('[data-perfil-abrir]').attributes('aria-expanded')).toBe('true')
    expect(wrapper.findAll('[data-perfil-panel] [data-rol-demo]').length).toBeGreaterThan(0)
  })

  it.each([
    ['apariencia', '[data-apariencia-abrir]', '[data-apariencia-panel]'],
    ['perfil', '[data-perfil-abrir]', '[data-perfil-panel]'],
  ])('ancla el panel de %s al borde final de su propio disparador', async (_nombre, disparador, panel) => {
    // This is the measured defect, written as an assertion: the profile
    // switcher rendered at `left: -144.4` on a 390 px viewport and the bar
    // does not scroll, so the control was unreachable. A panel anchored to the
    // end edge of a trigger that is itself inside the bar cannot leave it.
    const wrapper = await montar(true)

    await wrapper.get(disparador).trigger('click')
    await nextTick()

    const clases = wrapper.get(panel).classes()

    expect(clases).toContain('absolute')
    expect(clases).toContain('end-0')
    expect(clases.some(clase => clase.startsWith('start-') || clase.startsWith('left-'))).toBe(false)
  })
})

describe('todo control propio de la barra alcanza el objetivo tactil', () => {
  it('declara 44 px de alto en cada uno', async () => {
    // Thirty-two targets under 44 px were measured at 390 px. The system
    // emits a floor for coarse pointers, but that rule keys on the pointer and
    // not on the width, so a control measured with a mouse still came out
    // short. The bar declares its own floor for the controls it owns.
    //
    // The two groups it composes -language and profile- carry their own
    // markup and are out of the write set of this wave.
    const wrapper = await montar(true)
    const propios = wrapper
      .get('[data-cabecera-producto]')
      .findAll(CONTROLES)
      .filter(control => control.element.closest('[data-selector-idioma]') === null)

    expect(propios.length).toBeGreaterThan(0)
    for (const control of propios) {
      expect(control.classes(), control.html()).toContain('min-h-11')
    }
  })
})

describe('el buscador del cromo lleva de verdad al catalogo', () => {
  it('lleva el termino escrito a la ruta del catalogo', async () => {
    // A search box in the chrome that navigates without the term is the
    // defect: the reader retypes it on arrival and the address cannot be
    // shared. The route comes from the navigation contract, never a literal,
    // and so does the name of the parameter: written here as `q` this
    // assertion would go on passing while the header and the catalogue drifted
    // apart, which is the seam the test below is about.
    const wrapper = await montar(true)

    await wrapper.get('[data-buscador-cromo] input').setValue('  saldo  ')
    await wrapper.get('[data-buscador-cromo]').trigger('submit')

    expect(navegaciones).toEqual([
      { path: RUTA_CATALOGO, query: { [PARAMETRO_TERMINO]: 'saldo' } },
    ])
  })

  it('no ensucia la direccion cuando el campo queda vacio', async () => {
    const wrapper = await montar(true)

    await wrapper.get('[data-buscador-cromo] input').setValue('   ')
    await wrapper.get('[data-buscador-cromo]').trigger('submit')

    expect(navegaciones).toEqual([{ path: RUTA_CATALOGO, query: {} }])
  })

  it('se siembra con el termino que ya viaja en la direccion', async () => {
    // The term surviving the round trip is what makes the search shareable:
    // landing on `?q=saldo` has to show `saldo` in the field, or the address
    // and the chrome say different things.
    const wrapper = await montar(true, `${RUTA_CATALOGO}?${PARAMETRO_TERMINO}=saldo`)

    expect((wrapper.get('[data-buscador-cromo] input').element as HTMLInputElement).value)
      .toBe('saldo')
  })

  it('nombra el parametro con el del composable y no con una copia propia', async () => {
    // The two halves of one journey live in two files written by two different
    // waves: this bar publishes the term and `/exploracion` reads it. Until
    // the integration they each spelled their own `'q'`, and the day one of
    // them changes the other keeps navigating with a letter nobody reads -no
    // error, no empty state, just a catalogue that opens without the term and
    // an address that carries it. It cannot be caught by asserting behaviour
    // here, because two copies of the same letter behave identically; what is
    // measured is that there is only one letter.
    const fuente = readFileSync(
      fileURLToPath(new URL(RUTA_FUENTE_CABECERA, import.meta.url)),
      'utf8',
    )

    expect(fuente).toContain('PARAMETRO_TERMINO')
    expect(fuente).not.toMatch(/(['"])q\1/)

    // And the constant is really the one that travels: seeded from the address
    // and written back into it, both through the shared name.
    const wrapper = await montar(true, `${RUTA_CATALOGO}?${PARAMETRO_TERMINO}=mora`)

    expect(wrapper.get('[data-buscador-cromo] input').attributes('name'))
      .toBe(PARAMETRO_TERMINO)
    expect((wrapper.get('[data-buscador-cromo] input').element as HTMLInputElement).value)
      .toBe('mora')
  })
})

describe('la barra nombra el producto una sola vez', () => {
  it('monta la marca vectorial y ningun icono de paquete en su lugar', async () => {
    // The shipped defect: `lucide:circuit-board` tinted with the informative
    // colour standing in for a logotype. The mark is now an inline drawing,
    // and the header is where it is mounted.
    const wrapper = await montar(true)
    const marca = wrapper.get('[data-marca-enlace]')

    expect(marca.attributes('href')).toBe(RUTA_INDICE)
    expect(marca.find('[data-marca-karisma]').exists()).toBe(true)
    expect(marca.findAll('img')).toHaveLength(0)
    expect(marca.html()).not.toContain('circuit-board')
  })

  it('rotula el enlace de la marca aunque el nombre no quepa en pantalla', async () => {
    // Below 768 px the plate rules the symbol alone, so the visible wordmark
    // is not rendered. Without the accessible name the link would announce
    // itself as "link" and nothing else.
    const wrapper = await montar(true)

    expect(wrapper.get('[data-marca-enlace]').attributes('aria-label')).toBe(
      mensaje('es', 'brand.name'),
    )
  })
})
