import type { Component } from 'vue'
import type { VueWrapper } from '@vue/test-utils'

import { mount } from '@vue/test-utils'
import { defineComponent } from 'vue'
import { createMemoryHistory, createRouter } from 'vue-router'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import Chasis from '~/app.vue'
import { etiquetaDeRuta, RUTA_ACCESO, RUTA_INDICE, RUTAS_CONTRATO } from '~/utils/navegacion'

/**
 * US-001 — the nine screens of the navigable skeleton.
 *
 * This pins down what the end to end smoke can only check with the stack up:
 * that every contract route has a page file which Nuxt maps to that exact
 * route, that every page asks for the right layout -and therefore for the scope
 * banner and the sidebar that belong to it- and that its title comes from the
 * navigation contract and not from a loose literal.
 *
 * `definePageMeta` is a macro compiled by the Nuxt plugin, and it does not
 * exist here: it is replaced by a double that records the declared meta, so the
 * layout each screen asks for is verifiable without booting Nuxt.
 */

/** Page modules as Nuxt discovers them: by file path under app/pages. */
const modulosDePagina = import.meta.glob<{ default: Component }>('../app/pages/**/*.vue')

const PREFIJO_PAGINAS = '../app/pages'

/** Route that Nuxt derives from a page file path. */
function rutaDeArchivo(archivo: string): string {
  const sinPrefijo = archivo.slice(PREFIJO_PAGINAS.length).replace(/\.vue$/, '')
  return sinPrefijo.replace(/\/index$/, '') || RUTA_INDICE
}

const RUTA_POR_ARCHIVO = new Map(
  Object.keys(modulosDePagina).map(archivo => [rutaDeArchivo(archivo), archivo]),
)

/**
 * Layout each screen must ask for.
 *
 * The entry screen is framed without a sidebar, the prototype index uses the
 * default chrome, and every branch of the A3 map lives inside the portal.
 */
function layoutEsperado(ruta: string): string | undefined {
  if (ruta === RUTA_INDICE) {
    return undefined
  }
  return ruta === RUTA_ACCESO ? 'acceso' : 'portal'
}

/** Meta captured from the last `definePageMeta` call of the mounted page. */
let metaDeclarada: Record<string, unknown> | undefined

const router = createRouter({
  history: createMemoryHistory(),
  routes: [RUTA_INDICE, ...RUTAS_CONTRATO].map(path => ({
    path,
    component: defineComponent({ template: '<div />' }),
  })),
})

const EnlaceStub = defineComponent({
  props: { to: { type: String, required: true } },
  template: '<a :href="to"><slot /></a>',
})

async function montarPagina(ruta: string): Promise<VueWrapper> {
  const archivo = RUTA_POR_ARCHIVO.get(ruta)
  if (archivo === undefined) {
    throw new Error(`Ninguna pagina de app/pages/ se mapea a la ruta ${ruta}`)
  }

  const modulo = await modulosDePagina[archivo]!()
  await router.push(ruta)
  await router.isReady()

  return mount(modulo.default, {
    global: {
      plugins: [router],
      components: { NuxtLink: EnlaceStub },
    },
  })
}

beforeEach(() => {
  metaDeclarada = undefined
  vi.stubGlobal('definePageMeta', (meta: Record<string, unknown>) => {
    metaDeclarada = meta
  })

  return () => {
    vi.unstubAllGlobals()
  }
})

describe('ninguna ruta del contrato se queda sin pantalla', () => {
  it('mapea los archivos de app/pages a las nueve rutas, sin sobrantes', () => {
    // A contract route with no file answers 404 and brings the smoke down; a
    // file with no route in the contract is a screen nobody audited.
    const rutasDeArchivos = [...RUTA_POR_ARCHIVO.keys()].sort()

    expect(rutasDeArchivos).toEqual([RUTA_INDICE, ...RUTAS_CONTRATO].sort())
    expect(Object.keys(modulosDePagina)).toHaveLength(9)
  })

  it.each(RUTAS_CONTRATO)('renderiza %s con el atributo de ruta del contrato', async (ruta) => {
    const wrapper = await montarPagina(ruta)

    expect(wrapper.get('[data-ruta]').attributes('data-ruta')).toBe(ruta)
  })
})

describe('cada pantalla pide el layout que le corresponde', () => {
  it.each([RUTA_INDICE, ...RUTAS_CONTRATO])('declara el layout de %s', async (ruta) => {
    await montarPagina(ruta)

    expect(metaDeclarada?.layout).toBe(layoutEsperado(ruta))
  })

  it('deja la pantalla de entrada como la unica fuera del portal', async () => {
    const layouts = new Map<string, unknown>()
    for (const ruta of RUTAS_CONTRATO) {
      await montarPagina(ruta)
      layouts.set(ruta, metaDeclarada?.layout)
    }

    expect(layouts.get(RUTA_ACCESO)).toBe('acceso')
    expect([...layouts.values()].filter(layout => layout === 'acceso')).toHaveLength(1)
    expect([...layouts.values()].filter(layout => layout === 'portal')).toHaveLength(7)
  })
})

describe('el titulo de cada pantalla sale del contrato de navegacion', () => {
  it.each(RUTAS_CONTRATO)('titula %s con la rama del mapa de A3', async (ruta) => {
    const wrapper = await montarPagina(ruta)

    expect(wrapper.get('h1').text()).toBe(etiquetaDeRuta(ruta))
  })

  it('declara en prosa lo que contendra cada pantalla', async () => {
    for (const ruta of RUTAS_CONTRATO) {
      const wrapper = await montarPagina(ruta)
      const descripcion = wrapper.get('p').text()

      expect(descripcion.length).toBeGreaterThan(0)
      expect(descripcion).toMatch(/^Contendr/)
    }
  })

  it('no deja ninguna pantalla sin un unico encabezado de primer nivel', async () => {
    for (const ruta of RUTAS_CONTRATO) {
      const wrapper = await montarPagina(ruta)

      expect(wrapper.findAll('h1')).toHaveLength(1)
    }
  })
})

describe('chasis de la aplicacion', () => {
  const LayoutStub = defineComponent({ template: '<div data-layout><slot /></div>' })
  const PaginaStub = defineComponent({ template: '<section data-pagina />' })

  it('envuelve toda pagina en un layout, que es donde vive la franja de alcance', () => {
    const wrapper = mount(Chasis, {
      global: { components: { NuxtLayout: LayoutStub, NuxtPage: PaginaStub } },
    })

    // If NuxtPage sat outside the layout, the nine routes would lose the
    // banner and any screenshot could be read as a live system (CA-7).
    expect(wrapper.find('[data-layout] [data-pagina]').exists()).toBe(true)
    expect(wrapper.element.matches('[data-layout]')).toBe(true)
  })
})
