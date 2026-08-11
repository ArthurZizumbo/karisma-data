import type { Component } from 'vue'
import { mount } from '@vue/test-utils'
import { defineComponent } from 'vue'
import { createMemoryHistory, createRouter } from 'vue-router'
import { afterAll, beforeAll, describe, expect, it, vi } from 'vitest'
import FranjaAlcance from '~/components/nav/FranjaAlcance.vue'
import Acceso from '~/layouts/acceso.vue'
import Default from '~/layouts/default.vue'
import Portal from '~/layouts/portal.vue'
import PantallaDeError from '~/error.vue'
import { AVISO_ALCANCE, RUTA_INDICE, RUTAS_CONTRATO } from '~/utils/navegacion'

const Vacio = defineComponent({ template: '<div />' })

const EnlaceStub = defineComponent({
  props: { to: { type: String, required: true } },
  template: '<a :href="to"><slot /></a>',
})

const router = createRouter({
  history: createMemoryHistory(),
  routes: [RUTA_INDICE, ...RUTAS_CONTRATO].map(path => ({ path, component: Vacio })),
})

function montarConChasis(componente: Component, props: Record<string, unknown> = {}) {
  return mount(componente, {
    props,
    slots: { default: '<p>Contenido de prueba</p>' },
    global: {
      plugins: [router],
      components: { NuxtLink: EnlaceStub },
    },
  })
}

describe('FranjaAlcance', () => {
  it('expone el atributo que consumen el smoke y los tests', () => {
    const wrapper = mount(FranjaAlcance)
    expect(wrapper.find('[data-franja-alcance]').exists()).toBe(true)
  })

  it('muestra el texto único de alcance, sin agregar ni recortar nada', () => {
    const wrapper = mount(FranjaAlcance)
    expect(wrapper.get('[data-franja-alcance]').text()).toBe(AVISO_ALCANCE)
  })

  it('declara el aviso como nota accesible', () => {
    const wrapper = mount(FranjaAlcance)
    const franja = wrapper.get('[data-franja-alcance]')

    expect(franja.attributes('role')).toBe('note')
    expect(franja.attributes('aria-label')).toBe('Aviso de alcance del prototipo')
  })

  it('no ofrece ningún control para descartarla', () => {
    const wrapper = mount(FranjaAlcance)

    expect(wrapper.findAll('button')).toHaveLength(0)
    expect(wrapper.findAll('[role="button"]')).toHaveLength(0)
  })

  it('declara que los datos son sintéticos y que no hay sistemas reales conectados', () => {
    const wrapper = mount(FranjaAlcance)
    const texto = wrapper.text()

    expect(texto).toContain('datos sintéticos')
    expect(texto).toContain('No está conectado a sistemas reales')
  })
})

describe('la franja acompaña a todas las superficies del prototipo', () => {
  beforeAll(async () => {
    vi.stubGlobal('useRuntimeConfig', () => ({ public: { entorno: 'pruebas' } }))
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

    expect(franja.text()).toBe(AVISO_ALCANCE)
    expect(wrapper.text()).toContain('Contenido de prueba')
  })

  it('muestra la barra lateral solo en el layout del portal', () => {
    expect(montarConChasis(Portal).findAll('nav').length).toBeGreaterThan(0)
    expect(montarConChasis(Acceso).findAll('nav')).toHaveLength(0)
    expect(montarConChasis(Default).findAll('nav')).toHaveLength(0)
  })

  it('incluye la franja en el estado de error transversal', () => {
    const wrapper = montarConChasis(PantallaDeError, {
      error: { statusCode: 404, statusMessage: 'Not Found' },
    })

    expect(wrapper.get('[data-franja-alcance]').text()).toBe(AVISO_ALCANCE)
  })
})

describe('estado de error transversal', () => {
  beforeAll(() => {
    vi.stubGlobal('clearError', () => undefined)
  })

  afterAll(() => {
    vi.unstubAllGlobals()
  })

  it.each([
    [404, 'no corresponde a ninguna pantalla'],
    [403, 'no tiene permiso'],
    [500, 'no pudo construir la pantalla'],
    [418, 'error inesperado'],
  ])('explica la causa del error %i', (statusCode, fragmento) => {
    const wrapper = montarConChasis(PantallaDeError, { error: { statusCode } })

    expect(wrapper.text()).toContain(fragmento)
    expect(wrapper.text()).toContain(`Error ${statusCode}`)
  })

  it('ofrece un camino de recuperación accionable', async () => {
    const wrapper = montarConChasis(PantallaDeError, { error: { statusCode: 500 } })
    const boton = wrapper.get('button')

    expect(boton.text()).toContain('Volver al índice de prototipos')
    await boton.trigger('click')
  })
})
