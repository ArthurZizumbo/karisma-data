import type { Component } from 'vue'
import type { VueWrapper } from '@vue/test-utils'

import { flushPromises, mount } from '@vue/test-utils'
import { defineComponent, ref } from 'vue'
import { createMemoryHistory, createRouter } from 'vue-router'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import Chasis from '~/app.vue'
import { claveDeRuta, RUTA_ACCESO, RUTA_GUIA, RUTA_INDICE, RUTAS_CONTRATO } from '~/utils/navegacion'
import { type CodigoIdioma, crearI18nDePrueba, mensaje } from './i18nDePrueba'

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

async function montarPagina(ruta: string, idioma: CodigoIdioma = 'es'): Promise<VueWrapper> {
  const archivo = RUTA_POR_ARCHIVO.get(ruta)
  if (archivo === undefined) {
    throw new Error(`Ninguna pagina de app/pages/ se mapea a la ruta ${ruta}`)
  }

  const modulo = await modulosDePagina[archivo]!()
  await router.push(ruta)
  await router.isReady()

  return mount(modulo.default, {
    global: {
      plugins: [router, crearI18nDePrueba(idioma)],
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
  it('mapea los archivos de app/pages a las diez rutas, sin sobrantes', () => {
    // A contract route with no file answers 404 and brings the smoke down; a
    // file with no route in the contract is a screen nobody audited.
    //
    // Two files sit outside the contract and both are enumerated here so the
    // exception has to be argued rather than inherited: the prototype index and
    // the A4 style guide, which is neither a prototype nor a branch of the map.
    const rutasDeArchivos = [...RUTA_POR_ARCHIVO.keys()].sort()

    expect(rutasDeArchivos).toEqual([RUTA_INDICE, RUTA_GUIA, ...RUTAS_CONTRATO].sort())
    expect(Object.keys(modulosDePagina)).toHaveLength(10)
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

    expect(wrapper.get('h1').text()).toBe(mensaje('es', claveDeRuta(ruta) as string))
  })

  it.each(RUTAS_CONTRATO)('retitula %s al cambiar la interfaz a ingles', async (ruta) => {
    const wrapper = await montarPagina(ruta, 'en')

    expect(wrapper.get('h1').text()).toBe(mensaje('en', claveDeRuta(ruta) as string))
  })

  it('declara en prosa lo que contendra cada pantalla, en los dos idiomas', async () => {
    // Two defects hide here and nowhere else. A page that keeps a Spanish
    // literal instead of a key renders the same sentence in both languages; a
    // page that points at a key the catalogue does not have renders the key
    // path itself, which vue-i18n prints verbatim.
    for (const ruta of RUTAS_CONTRATO) {
      const enEspanol = (await montarPagina(ruta)).get('p').text()
      const enIngles = (await montarPagina(ruta, 'en')).get('p').text()

      expect(enEspanol.length).toBeGreaterThan(0)
      expect(enEspanol).not.toMatch(/^screen\./)
      expect(enIngles).not.toMatch(/^screen\./)
      expect(enIngles).not.toBe(enEspanol)
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

  /**
   * app.vue resolves the stored language before rendering, so its setup is
   * async and it needs the Suspense boundary that Nuxt gives it in production.
   */
  const Envoltura = defineComponent({
    components: { Chasis },
    template: '<Suspense><Chasis /></Suspense>',
  })

  it('envuelve toda pagina en un layout, que es donde vive la franja de alcance', async () => {
    vi.stubGlobal('useHead', () => undefined)
    vi.stubGlobal('useCookie', () => ref(null))

    const wrapper = mount(Envoltura, {
      global: {
        plugins: [crearI18nDePrueba()],
        components: { NuxtLayout: LayoutStub, NuxtPage: PaginaStub },
      },
    })
    await flushPromises()

    // If NuxtPage sat outside the layout, the nine routes would lose the
    // banner and any screenshot could be read as a live system (CA-7).
    expect(wrapper.find('[data-layout] [data-pagina]').exists()).toBe(true)
    expect(wrapper.element.matches('[data-layout]')).toBe(true)
  })

  it('aplica el idioma guardado en la cookie antes del primer render', async () => {
    // Without this the server would emit Spanish for a reader who chose English
    // and the interface would swap after hydration: a visible flash, and a
    // hydration mismatch on every translated node.
    vi.stubGlobal('useHead', () => undefined)
    vi.stubGlobal('useCookie', () => ref('en'))

    const i18n = crearI18nDePrueba('es')
    mount(Envoltura, {
      global: {
        plugins: [i18n],
        components: { NuxtLayout: LayoutStub, NuxtPage: PaginaStub },
      },
    })
    await flushPromises()

    expect(i18n.global.locale.value).toBe('en')
  })
})
