import type { Component } from 'vue'
import { mount } from '@vue/test-utils'
import { defineComponent, ref } from 'vue'
import { createMemoryHistory, createRouter } from 'vue-router'
import { afterAll, beforeAll, describe, expect, it, vi } from 'vitest'
import FranjaAlcance from '~/components/nav/FranjaAlcance.vue'
import Acceso from '~/layouts/acceso.vue'
import Default from '~/layouts/default.vue'
import Portal from '~/layouts/portal.vue'
import PantallaDeError from '~/error.vue'
import { CLAVE_AVISO_ALCANCE, RUTA_INDICE, RUTAS_CONTRATO } from '~/utils/navegacion'
import { type CodigoIdioma, crearI18nDePrueba, mensaje } from './i18nDePrueba'

const Vacio = defineComponent({ template: '<div />' })

const EnlaceStub = defineComponent({
  props: { to: { type: String, required: true } },
  template: '<a :href="to"><slot /></a>',
})

const router = createRouter({
  history: createMemoryHistory(),
  routes: [RUTA_INDICE, ...RUTAS_CONTRATO].map(path => ({ path, component: Vacio })),
})

function montarFranja(idioma: CodigoIdioma = 'es') {
  return mount(FranjaAlcance, { global: { plugins: [crearI18nDePrueba(idioma)] } })
}

function montarConChasis(
  componente: Component,
  props: Record<string, unknown> = {},
  idioma: CodigoIdioma = 'es',
) {
  return mount(componente, {
    props,
    slots: { default: '<p>Contenido de prueba</p>' },
    global: {
      plugins: [router, crearI18nDePrueba(idioma)],
      components: { NuxtLink: EnlaceStub },
      stubs: { Icon: true },
    },
  })
}

describe('FranjaAlcance', () => {
  it('expone el atributo que consumen el smoke y los tests', () => {
    expect(montarFranja().find('[data-franja-alcance]').exists()).toBe(true)
  })

  it('muestra el texto único de alcance, sin agregar ni recortar nada', () => {
    expect(montarFranja().get('[data-franja-alcance]').text()).toBe(
      mensaje('es', CLAVE_AVISO_ALCANCE),
    )
  })

  it('declara el aviso como nota accesible', () => {
    const franja = montarFranja().get('[data-franja-alcance]')

    expect(franja.attributes('role')).toBe('note')
    expect(franja.attributes('aria-label')).toBe('Aviso de alcance del prototipo')
  })

  it('no ofrece ningún control para descartarla', () => {
    const wrapper = montarFranja()

    expect(wrapper.findAll('button')).toHaveLength(0)
    expect(wrapper.findAll('[role="button"]')).toHaveLength(0)
  })

  it('declara que los datos son sintéticos y que no hay sistemas reales conectados', () => {
    // The honesty banner is contract, not layout: it is what keeps a screenshot
    // of the prototype from being read as a live system. Both wordings are
    // pinned so that a catalogue edit cannot quietly weaken the disclaimer.
    const enEspanol = montarFranja('es').text()

    expect(enEspanol).toContain('datos sintéticos')
    expect(enEspanol).toContain('No está conectado a sistemas reales')

    const enIngles = montarFranja('en').text()

    expect(enIngles).toContain('synthetic data')
    expect(enIngles).toContain('not connected to the real systems')
  })

  it('traduce también la etiqueta accesible del aviso', () => {
    expect(montarFranja('en').get('[data-franja-alcance]').attributes('aria-label')).toBe(
      'Prototype scope notice',
    )
  })
})

describe('la franja acompaña a todas las superficies del prototipo', () => {
  beforeAll(async () => {
    vi.stubGlobal('useRuntimeConfig', () => ({ public: { entorno: 'pruebas' } }))
    vi.stubGlobal('useCookie', () => ref(null))
    vi.stubGlobal('clearError', () => undefined)
    await router.push(RUTA_INDICE)
    await router.isReady()
  })

  afterAll(() => {
    vi.unstubAllGlobals()
  })

  it.each([
    ['portal', Portal],
    ['acceso', Acceso],
    ['default', Default],
  ])('incluye la franja en el layout %s', (_nombre, layout) => {
    const wrapper = montarConChasis(layout as Component)
    const franja = wrapper.get('[data-franja-alcance]')

    expect(franja.text()).toBe(mensaje('es', CLAVE_AVISO_ALCANCE))
    expect(wrapper.text()).toContain('Contenido de prueba')
  })

  it('muestra la barra lateral solo en el layout del portal', () => {
    expect(montarConChasis(Portal).findAll('nav').length).toBeGreaterThan(0)
    expect(montarConChasis(Acceso).findAll('nav')).toHaveLength(0)
    expect(montarConChasis(Default).findAll('nav')).toHaveLength(0)
  })

  it.each([
    ['portal', Portal, {}],
    ['acceso', Acceso, {}],
    ['default', Default, {}],
    ['error', PantallaDeError, { error: { statusCode: 404 } }],
  ])('ofrece el selector de idioma en el chasis %s', (_nombre, chasis, props) => {
    // The previous version of this check cleared only the portal and the entry
    // screen, on the grounds that "the index is reached from those two". It had
    // the real flow backwards: the prototype index is the FIRST screen an
    // evaluator opens, `pages/index.vue` declares no layout so it is framed by
    // `default`, and `detectBrowserLanguage` is false, so the selector is the
    // only route to English. An English speaking reader landed on the index,
    // and on the error screen, with no way out of Spanish.
    const wrapper = montarConChasis(chasis as Component, props as Record<string, unknown>)

    expect(wrapper.find('[data-selector-idioma]').exists()).toBe(true)
  })

  it.each([
    ['portal', Portal, {}],
    ['acceso', Acceso, {}],
    ['default', Default, {}],
    ['error', PantallaDeError, { error: { statusCode: 404 } }],
  ])('saca la franja del chasis %s de la medida de lectura', (_nombre, chasis, props) => {
    // The defect this guards against is cheap to commit and expensive to find:
    // `FranjaAlcance` renders a `<p>`, `main.css` caps every paragraph at
    // `--medida-maxima` (68ch) and the notice came out 455 px wide inside a
    // 1193 px column, reading as a stray card instead of a declaration
    // governing the screen. Removing the class from a single surface leaves the
    // whole suite green while it silently invalidates the before/after figures
    // of `figuras/a4/`, which are evidence in a graded document.
    //
    // The class is asserted on the four mount points and not on the component,
    // because the component cannot carry it: whoever mounts it decides.
    const wrapper = montarConChasis(chasis as Component, props as Record<string, unknown>)

    expect(wrapper.get('[data-franja-alcance]').classes()).toContain('max-w-none')
  })

  it('incluye la franja en el estado de error transversal', () => {
    const wrapper = montarConChasis(PantallaDeError, {
      error: { statusCode: 404, statusMessage: 'Not Found' },
    })

    expect(wrapper.get('[data-franja-alcance]').text()).toBe(mensaje('es', CLAVE_AVISO_ALCANCE))
  })
})

describe('estado de error transversal', () => {
  beforeAll(() => {
    // The error screen mounts the product header, so it needs the same globals
    // the layouts need: without them the recovery path is never rendered.
    vi.stubGlobal('useRuntimeConfig', () => ({ public: { entorno: 'pruebas' } }))
    vi.stubGlobal('useCookie', () => ref(null))
    vi.stubGlobal('clearError', () => undefined)
  })

  afterAll(() => {
    vi.unstubAllGlobals()
  })

  it.each([
    [404, 'error.cause.notFound'],
    [403, 'error.cause.forbidden'],
    [500, 'error.cause.serverError'],
    [418, 'error.cause.unknown'],
  ])('explica la causa del error %i', (statusCode, clave) => {
    const wrapper = montarConChasis(PantallaDeError, { error: { statusCode } })

    expect(wrapper.text()).toContain(mensaje('es', clave as string))
    expect(wrapper.text()).toContain(`Error ${statusCode}`)
  })

  it('explica la causa en inglés cuando la interfaz está en inglés', () => {
    const wrapper = montarConChasis(PantallaDeError, { error: { statusCode: 403 } }, 'en')

    expect(wrapper.text()).toContain(mensaje('en', 'error.cause.forbidden'))
    expect(wrapper.text()).not.toContain(mensaje('es', 'error.cause.forbidden'))
  })

  it('ofrece un camino de recuperación accionable', async () => {
    const wrapper = montarConChasis(PantallaDeError, { error: { statusCode: 500 } })
    // Selected by its own hook and not by position: the header of the screen
    // now contributes the two buttons of the language selector.
    const boton = wrapper.get('[data-volver-al-indice]')

    expect(boton.text()).toContain(mensaje('es', 'error.action.backToIndex'))
    await boton.trigger('click')
  })
})
