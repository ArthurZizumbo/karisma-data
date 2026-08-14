import type { VueWrapper } from '@vue/test-utils'

import { mount } from '@vue/test-utils'
import { createMemoryHistory, createRouter, RouterLink } from 'vue-router'
import { afterEach, describe, expect, it } from 'vitest'

import ContextoPanelContextoTablero from '~/components/contexto/PanelContextoTablero.vue'
import { RUTA_TABLERO, useWorkspaceStore } from '~/stores/workspace'
import { RUTA_INDICE, RUTAS_CONTRATO } from '~/utils/navegacion'
import { crearI18nDePrueba, mensaje } from './i18nDePrueba'
import { ORIGEN_DE_PRUEBA } from './marcoDePrueba'

/**
 * US-029 — the context of the dashboard, as the assistant screen shows it.
 *
 * The store is the real one, with a real Pinia: its default state is exactly
 * what the empty state has to answer to, and a double would let the panel
 * agree with a fixture instead of with the dashboard.
 *
 * The direction of the arrow is what these assertions defend. The panel reads
 * and never writes, so this file drives the store through the store itself,
 * which is also how the dashboard drives it.
 */

let montado: VueWrapper | null = null

function montar(idioma: 'es' | 'en' = 'es') {
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [RUTA_INDICE, ...RUTAS_CONTRATO].map(path => ({
      path,
      component: { template: '<div />' },
    })),
  })

  const wrapper = mount(ContextoPanelContextoTablero, {
    global: {
      plugins: [router, crearI18nDePrueba(idioma)],
      components: { NuxtLink: RouterLink },
      stubs: { Icon: true },
    },
  })
  montado = wrapper
  return wrapper
}

/** Narrows the view the way the dashboard does, through its own actions. */
function filtrar() {
  const espacio = useWorkspaceStore()
  espacio.aplicarDrillDown('unidadNegocio', 'BANCA_EMPRESAS', 'grafica')
  espacio.aplicarDrillDown('divisa', 'USD', 'leyenda')
  espacio.fijarVentana(20, 60, 'control')
  espacio.registrarOrigen(ORIGEN_DE_PRUEBA)
  return espacio
}

afterEach(() => {
  montado?.unmount()
  montado = null
})

describe('sin contexto el panel no finge tenerlo', () => {
  it('sin filtros no se inventa contexto', () => {
    // Painting the default values as chips would tell the reader they narrowed
    // something they never touched, which is worse than showing nothing.
    const wrapper = montar()

    expect(wrapper.get('[data-estado]').attributes('data-estado')).toBe('sin-contexto')
    expect(wrapper.findAll('[data-chip-contexto]')).toHaveLength(0)
    expect(wrapper.text()).toContain(mensaje('es', 'sharedContext.empty.hint'))
    expect(wrapper.get('[data-abrir-tablero]').attributes('href')).toBe(RUTA_TABLERO)
  })

  it('una carga completa de /asistente cae en el vacio disenado', () => {
    // F5 on the assistant screen starts the store at its defaults: the panel
    // has to say where the context is built, not render an empty frame.
    const wrapper = montar('en')

    expect(wrapper.get('[data-estado]').attributes('data-estado')).toBe('sin-contexto')
    expect(wrapper.text()).toContain(mensaje('en', 'sharedContext.empty.title'))
  })
})

describe('con contexto, tres niveles a dos clics', () => {
  it('un chip por dimension activa', () => {
    // Showing only the metric would announce a context that is not the one
    // that would travel: the window and the level narrow the answer too.
    filtrar()
    const wrapper = montar()

    const dimensiones = wrapper
      .findAll('[data-chip-contexto]')
      .map(chip => chip.attributes('data-dimension'))

    expect(dimensiones).toEqual([
      'metric',
      'grouping',
      'businessUnit',
      'currency',
      'window',
      'density',
      'level',
    ])
    expect(wrapper.get('[data-dimension="businessUnit"]').text()).toContain('BANCA_EMPRESAS')
  })

  it('el contexto que se muestra es el que viajaria', async () => {
    // A `JSON.stringify` of its own diverges from `serializarVista()` the first
    // time a key is added, and then the panel shows something that is not what
    // would be sent.
    const espacio = filtrar()
    const wrapper = montar()

    await wrapper.get('[data-payload-estatico] summary').trigger('click')

    expect(wrapper.get('[data-payload-estatico] pre').text()).toBe(espacio.serializarVista())
  })

  it('el detalle esta a dos clics', async () => {
    // Rendering the JSON from the start makes "two clicks" trivially true and
    // simultaneously false, because the reader never performed them.
    filtrar()
    const wrapper = montar()

    expect(wrapper.find('[data-payload-estatico] pre').exists()).toBe(false)
    expect(wrapper.find('[data-ultima-interaccion]').exists()).toBe(false)

    await wrapper.get('[data-detalle-interaccion] summary').trigger('click')
    expect(wrapper.get('[data-ultima-interaccion]').exists()).toBe(true)

    await wrapper.get('[data-payload-estatico] summary').trigger('click')
    expect(wrapper.get('[data-payload-estatico] pre').exists()).toBe(true)
  })

  it('la ultima interaccion llega con su procedencia y su ficha de origen', async () => {
    // Provenance is the whole point of the second rung: without it the reader
    // cannot tell a filter they clicked on the chart from one they typed.
    filtrar()
    const wrapper = montar()

    await wrapper.get('[data-detalle-interaccion] summary').trigger('click')
    const detalle = wrapper.get('[data-ultima-interaccion]').text()

    expect(detalle).toContain(mensaje('es', 'sharedContext.interaction.control'))
    expect(wrapper.find('[data-origen-serie]').exists()).toBe(true)
  })
})

describe('la degradacion se declara, no se calla', () => {
  it.each(['es', 'en'] as const)('declara el payload estatico en %s', (idioma) => {
    // Forgetting the notice in one catalogue would present as bidirectional,
    // in that language, something that only travels one way.
    filtrar()
    const wrapper = montar(idioma)

    expect(wrapper.get('[data-aviso-estatico]').text()).toBe(
      mensaje(idioma, 'sharedContext.static.notice'),
    )
  })
})
