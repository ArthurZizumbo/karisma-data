import type { VueWrapper } from '@vue/test-utils'
import { mount } from '@vue/test-utils'
import { defineComponent } from 'vue'
import { createMemoryHistory, createRouter, RouterLink } from 'vue-router'
import { describe, expect, it } from 'vitest'
import BarraLateral from '~/components/nav/BarraLateral.vue'
import { MODULOS, RUTA_ASISTENTE, RUTA_INDICE, RUTAS_CONTRATO } from '~/utils/navegacion'
import { type CodigoIdioma, crearI18nDePrueba, mensaje } from './i18nDePrueba'

const Vacio = defineComponent({ template: '<div />' })

/**
 * NuxtLink is replaced by the REAL RouterLink, not by a plain <a>.
 *
 * A bare anchor never emits aria-current, so the "exactly one" invariant held by
 * construction and the test could not fail. The dangerous case is /inicio, where
 * the five sub routes 1.1-1.5 share their route with the module: with RouterLink
 * all six are exact-active and their automatic aria-current could produce six.
 * What prevents that is the :aria-current="undefined" fallthrough of the
 * component, and with the stub that line of defence went untested.
 */
async function montarEn(ruta: string, idioma: CodigoIdioma = 'es'): Promise<VueWrapper> {
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [RUTA_INDICE, ...RUTAS_CONTRATO].map(path => ({ path, component: Vacio })),
  })
  await router.push(ruta)
  await router.isReady()

  return mount(BarraLateral, {
    global: {
      plugins: [router, crearI18nDePrueba(idioma)],
      components: { NuxtLink: RouterLink },
      stubs: { Icon: true },
    },
  })
}

describe('BarraLateral: revelación progresiva', () => {
  it('mantiene visibles los cuatro módulos de primer nivel en cualquier ruta', async () => {
    for (const ruta of RUTAS_CONTRATO) {
      const wrapper = await montarEn(ruta)
      expect(wrapper.findAll('[data-modulo-item]')).toHaveLength(MODULOS.length)
    }
  })

  it.each(MODULOS.map(modulo => [modulo.ruta, modulo.id]))(
    'despliega en %s solo el segundo nivel del módulo %s',
    async (ruta, idEsperado) => {
      const wrapper = await montarEn(ruta)
      const segundosNiveles = wrapper.findAll('[data-nivel="2"]')

      expect(segundosNiveles).toHaveLength(1)
      expect(segundosNiveles[0]?.attributes('data-modulo')).toBe(idEsperado)

      // aria-expanded lives on the module link, not on the <ul>: role=list does
      // not accept that attribute and, because the <ul> is rendered with v-if, it
      // only existed while it was true, so it never communicated the collapsed
      // state. The value is asserted on all four modules so the attribute can
      // never go back to being a constant disguised as state.
      const expandidos = MODULOS.map(
        modulo => wrapper.get(`#modulo-${modulo.id}`).attributes('aria-expanded'),
      )

      expect(expandidos.filter(valor => valor === 'true')).toHaveLength(1)
      expect(wrapper.get(`#modulo-${idEsperado}`).attributes('aria-expanded')).toBe('true')
    },
  )

  it('renderiza el segundo nivel en el DOM, no oculto con estilos', async () => {
    const wrapper = await montarEn('/gobierno')
    const html = wrapper.html()

    expect(html).not.toContain('display: none')
    expect(wrapper.findAll('[data-nivel="2"] a').length).toBeGreaterThan(0)
  })

  it('no despliega ningún segundo nivel fuera de los cuatro módulos', async () => {
    for (const ruta of [RUTA_ASISTENTE, '/acceso']) {
      const wrapper = await montarEn(ruta)
      expect(wrapper.findAll('[data-nivel="2"]')).toHaveLength(0)
    }
  })

  it('alcanza toda hoja del segundo nivel en un clic desde su módulo', async () => {
    // This one does measure clicks: it mounts the sidebar on the module
    // route and checks that every leaf is a single link away, with no
    // intermediate steps. With the module already open that is two clicks
    // from the root.
    for (const modulo of MODULOS) {
      const wrapper = await montarEn(modulo.ruta)
      const hojas = wrapper.findAll('[data-nivel="2"] a')

      expect(hojas.length).toBe(modulo.subrutas.length)
      for (const hoja of hojas) {
        const destino = hoja.attributes('href') ?? ''
        expect(destino.split('/').filter(Boolean).length).toBeLessThanOrEqual(2)
      }
    }
  })

  it('no altera el marcado de los módulos hermanos al desplegar', async () => {
    const marcadoPorModulo = new Map<string, Set<string>>()

    for (const modulo of MODULOS) {
      const wrapper = await montarEn(modulo.ruta)
      for (const item of wrapper.findAll('[data-modulo-item]')) {
        const id = item.attributes('data-modulo-item') ?? ''
        if (id === modulo.id) {
          continue
        }
        const marcados = marcadoPorModulo.get(id) ?? new Set<string>()
        marcados.add(item.html())
        marcadoPorModulo.set(id, marcados)
      }
    }

    for (const marcados of marcadoPorModulo.values()) {
      expect(marcados.size).toBe(1)
    }
  })
})

describe('BarraLateral: estado activo derivado de la ruta', () => {
  it.each(RUTAS_CONTRATO.filter(ruta => ruta !== '/acceso'))(
    'marca exactamente un enlace como página actual en %s',
    async (ruta) => {
      const wrapper = await montarEn(ruta)
      const actuales = wrapper.findAll('[aria-current="page"]')

      expect(actuales).toHaveLength(1)
      expect(actuales[0]?.attributes('href')).toBe(ruta)
    },
  )

  it('marca el asistente cuando la ruta activa es la suya', async () => {
    const wrapper = await montarEn(RUTA_ASISTENTE)
    const actual = wrapper.get('[aria-current="page"]')

    expect(actual.attributes('href')).toBe(RUTA_ASISTENTE)
    expect(actual.text()).toContain(mensaje('es', 'nav.assistant.label'))
  })

  it('no marca ningún enlace cuando la ruta queda fuera de la barra', async () => {
    const wrapper = await montarEn('/acceso')
    expect(wrapper.findAll('[aria-current="page"]')).toHaveLength(0)
  })
})

describe('BarraLateral: el árbol de A3 se traduce entero', () => {
  it('rotula módulos, hojas y facetas en el idioma activo', async () => {
    // The sidebar is the densest surface of the prototype: four modules, sixteen
    // leaves and nine facet chips. A literal left in Spanish anywhere in that
    // tree survives every other test in the suite.
    const wrapper = await montarEn('/exploracion', 'en')
    const texto = wrapper.text()

    expect(texto).toContain(mensaje('en', 'nav.module.explore'))
    expect(texto).toContain(mensaje('en', 'nav.branch.exploreDashboards'))
    expect(texto).toContain(mensaje('en', 'nav.facets.caption'))
    expect(texto).toContain(mensaje('en', 'nav.assistant.label'))
    expect(texto).not.toContain(mensaje('es', 'nav.module.explore'))
  })

  it('traduce los rótulos accesibles, no solo el texto visible', async () => {
    const wrapper = await montarEn('/exploracion', 'en')
    const rotulos = wrapper.findAll('nav').map(nav => nav.attributes('aria-label'))

    expect(rotulos).toContain(mensaje('en', 'nav.aria.main'))
    expect(rotulos).toContain(mensaje('en', 'nav.aria.crossCutting'))

    // The cross cutting facet marker carries its own accessible name, built
    // from the branch label; it must travel with the language too.
    const transversal = wrapper.get('[data-nivel="2"] a[aria-label]')
    expect(transversal.attributes('aria-label')).toContain('cross-cutting facet')
  })
})

describe('accesibilidad estructural del portal', () => {
  it('no introduce ningun encabezado antes del h1 de la pantalla', async () => {
    // The sidebar comes before <main>, so any <h1>-<h6> of its own becomes
    // the first heading of the document and the hierarchy starts below h1.
    // The facets caption names its list through aria-labelledby, which does
    // not need to be a heading to do so.
    const wrapper = await montarEn('/gobierno')

    expect(wrapper.findAll('h1, h2, h3, h4, h5, h6')).toHaveLength(0)
    expect(wrapper.get('#facetas-transversales').element.tagName).toBe('P')
  })
})
