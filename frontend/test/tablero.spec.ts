import type { MarcoSerie } from '~/types/tablero'
import type { Component } from 'vue'

import { flushPromises, mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { defineComponent, ref, shallowRef } from 'vue'
import { createMemoryHistory, createRouter } from 'vue-router'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import {
  codigoDelFallo,
  consultaDeSerie,
  PUNTOS_POR_DENSIDAD,
} from '~/composables/useSerieTablero'
import SeriePanel from '~/components/serie/Panel.vue'
import SerieEstado from '~/components/serie/Estado.vue'
import PaginaTableros from '~/pages/exploracion/tableros.vue'
import { useWorkspaceStore } from '~/stores/workspace'
import { CLAVE_AGRUPACION, CLAVE_DENSIDAD, CLAVE_METRICA } from '~/utils/etiquetasTablero'
import { decidirGuarda } from '~/utils/guarda'
import { ALTO_GRAFICA } from '~/utils/opcionSerie'
import { SCOPE_POR_RUTA } from '~/utils/permisos.generated'
import { clavesDe, crearI18nDePrueba, mensaje } from './i18nDePrueba'
import { crearMarco } from './marcoDePrueba'

/**
 * US-025 — the dashboard screen, its four unhappy states and its drill-down.
 *
 * The page itself is measured from this side on purpose. `test/pantallas.spec`
 * is shared by three User Stories this week and this one does not open it, so
 * the properties that file relies on are asserted here too: whoever breaks them
 * sees the failure in their own suite instead of in somebody else's.
 */

const RUTA = '/exploracion/tableros'

/** Chart double: the panel must not need a canvas to be testable. */
const GraficaFalsa = defineComponent({
  name: 'LazyVChart',
  props: {
    opcion: { type: Object, required: true },
    alto: { type: String, required: true },
    etiqueta: { type: String, required: true },
    describePor: { type: String, required: true },
  },
  emits: ['serie', 'ventana'],
  methods: {
    aplicarVentana: () => undefined,
  },
  template: '<div data-grafica :aria-label="etiqueta" :aria-describedby="describePor" />',
})

function crearRouter() {
  return createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/', component: defineComponent({ template: '<div />' }) },
      { path: RUTA, component: defineComponent({ template: '<div />' }) },
    ],
  })
}

interface EstadoFetch {
  marco?: MarcoSerie | null
  error?: unknown
  estado?: 'idle' | 'pending' | 'success' | 'error'
}

/**
 * Installs the `useFetch` double the panel loads its frame through.
 *
 * The composable is exercised for real -query, state machine, provenance- and
 * only the transport is replaced, which is the piece a unit test cannot reach.
 */
function instalarFetch({ marco = null, error = null, estado = 'success' }: EstadoFetch) {
  const refresh = vi.fn(async () => undefined)
  vi.stubGlobal('useFetch', () => ({
    data: shallowRef(marco),
    error: shallowRef(error),
    status: ref(estado),
    refresh,
  }))
  vi.stubGlobal('navigateTo', vi.fn(async () => undefined))
  return { refresh }
}

async function montarPanel(estadoFetch: EstadoFetch, idioma: 'es' | 'en' = 'es') {
  const { refresh } = instalarFetch(estadoFetch)
  const router = crearRouter()
  await router.push(RUTA)
  await router.isReady()

  const wrapper = mount(SeriePanel as Component, {
    global: {
      plugins: [router, crearI18nDePrueba(idioma)],
      components: { LazyVChart: GraficaFalsa },
      stubs: { Icon: true },
    },
  })
  await flushPromises()
  return { wrapper, refresh }
}

beforeEach(() => {
  setActivePinia(createPinia())
})

afterEach(() => {
  vi.unstubAllGlobals()
})

describe('la pagina conserva el contrato que comparten tres User Stories', () => {
  it('mantiene el nodo de ruta, el layout, un solo h1 y la descripcion bilingue', async () => {
    // A rewrite that loses any of the four turns test/pantallas.spec red for a
    // reason that file cannot explain, since it never sees this page's content.
    let meta: Record<string, unknown> | undefined
    vi.stubGlobal('definePageMeta', (declarada: Record<string, unknown>) => {
      meta = declarada
    })
    const router = crearRouter()
    await router.push(RUTA)
    await router.isReady()

    const enEspanol = mount(PaginaTableros as Component, {
      global: { plugins: [router, crearI18nDePrueba('es')] },
    })
    const enIngles = mount(PaginaTableros as Component, {
      global: { plugins: [router, crearI18nDePrueba('en')] },
    })

    expect(meta?.layout).toBe('portal')
    expect(enEspanol.get('[data-ruta]').attributes('data-ruta')).toBe(RUTA)
    expect(enEspanol.findAll('h1')).toHaveLength(1)
    expect(enEspanol.get('p').text()).toBe(mensaje('es', 'screen.dashboards.description'))
    expect(enIngles.get('p').text()).toBe(mensaje('en', 'screen.dashboards.description'))
  })

  it('montada sin Nuxt no pide nada ni instancia el store', async () => {
    // The property that keeps the shared spec working: the panel enters under
    // ClientOnly, so outside a Nuxt runtime it is an inert unknown element.
    // Moving it out would make three suites explode at once.
    const peticion = vi.fn()
    vi.stubGlobal('definePageMeta', () => undefined)
    vi.stubGlobal('$fetch', peticion)
    vi.stubGlobal('useFetch', peticion)
    const pinia = createPinia()
    setActivePinia(pinia)

    const router = crearRouter()
    await router.push(RUTA)
    await router.isReady()
    mount(PaginaTableros as Component, {
      global: { plugins: [router, crearI18nDePrueba()] },
    })
    await flushPromises()

    expect(peticion).not.toHaveBeenCalled()
    expect(Object.keys(pinia.state.value)).not.toContain('workspace')
  })
})

describe('los estados que no son el feliz', () => {
  it('reserva la altura de la grafica mientras carga', () => {
    // A skeleton of zero height means the whole page jumps the moment the data
    // lands, which is an explicit A4 criterion.
    const wrapper = mount(SerieEstado, {
      props: { estado: 'cargando', alto: ALTO_GRAFICA },
      global: { plugins: [crearI18nDePrueba()], stubs: { Icon: true } },
    })

    const esqueleto = wrapper.get('[role="status"]')

    expect(esqueleto.attributes('style')).toContain(ALTO_GRAFICA)
    expect(esqueleto.attributes('aria-busy')).toBe('true')
    expect(wrapper.get('[data-estado]').attributes('data-estado')).toBe('cargando')
  })

  it('sin datos sembrados da la instruccion make data en los dos idiomas', async () => {
    // This is the first screen anyone who clones the repository sees, and until
    // the deployment copies the aggregate it is what the public address shows.
    for (const idioma of ['es', 'en'] as const) {
      const wrapper = mount(SerieEstado, {
        props: { estado: 'sin-datos', alto: ALTO_GRAFICA },
        global: { plugins: [crearI18nDePrueba(idioma)], stubs: { Icon: true } },
      })

      expect(wrapper.get('[data-instruccion]').text()).toContain('make data')
      expect(wrapper.get('[data-instruccion]').text()).toBe(
        mensaje(idioma, 'dashboard.state.seedMissing.command'),
      )
      expect(wrapper.find('[data-reintentar]').exists()).toBe(false)
    }
  })

  it('solo el fallo ofrece reintentar', () => {
    // Retrying an empty filter or a missing seed changes nothing, and a button
    // that cannot work teaches the reader to insist.
    const conFallo = mount(SerieEstado, {
      props: { estado: 'error', alto: ALTO_GRAFICA },
      global: { plugins: [crearI18nDePrueba()], stubs: { Icon: true } },
    })
    const vacio = mount(SerieEstado, {
      props: { estado: 'vacio', alto: ALTO_GRAFICA },
      global: { plugins: [crearI18nDePrueba()], stubs: { Icon: true } },
    })

    expect(conFallo.find('[data-reintentar]').exists()).toBe(true)
    expect(vacio.find('[data-reintentar]').exists()).toBe(false)
  })

  it('el rol operativo topa con la puerta cerrada, no con una grafica vacia', () => {
    // The endpoint demands `analista`. If the route ever demanded less, an
    // operative would reach a chart whose every request answers 403, and the
    // interface and the API would be saying different things.
    expect(SCOPE_POR_RUTA[RUTA]).toBe('analista')
    expect(
      decidirGuarda({
        ruta: RUTA,
        sesion: { usuario: 'ops', nombre: 'Operativo', rol: 'operativo' },
        habiaSesion: true,
        scopeExigido: SCOPE_POR_RUTA[RUTA] ?? null,
      }),
    ).toEqual({ tipo: 'sin-permiso', scopeExigido: 'analista' })
  })
})

describe('el panel con datos', () => {
  it('declara la degradacion acordada siempre que hay serie', async () => {
    // The 500 K figure is a non negotiable declaration of the delivery, and a
    // refactor that dropped the notice would hide the one number the document
    // is built on.
    const { wrapper } = await montarPanel({ marco: crearMarco({ series: 5, fechas: 30 }) })

    expect(wrapper.get('[data-zona="serie"]').attributes('data-estado')).toBe('listo')
    expect(wrapper.get('[data-degradacion]').text()).toBe(
      mensaje('es', 'dashboard.degradation.notice'),
    )
    expect(wrapper.get('[data-degradacion]').text()).toContain('500 000')
  })

  it('describe la grafica con un resumen no vacio que cambia de idioma', async () => {
    // A sentence typed into the template would be read in Spanish to an English
    // reader, and the person who would notice is the least likely to report it.
    const marco = crearMarco({ series: 5, fechas: 30 })
    const { wrapper: enEspanol } = await montarPanel({ marco })
    setActivePinia(createPinia())
    const { wrapper: enIngles } = await montarPanel({ marco }, 'en')

    const textoEs = enEspanol.get('[data-resumen]').text()
    const textoEn = enIngles.get('[data-resumen]').text()

    expect(textoEs.length).toBeGreaterThan(40)
    expect(textoEs).not.toMatch(/^dashboard\./)
    expect(textoEn).not.toBe(textoEs)
    expect(enEspanol.get('[data-grafica]').attributes('aria-describedby')).toBe(
      enEspanol.get('[data-resumen]').attributes('id'),
    )
  })

  it('ofrece la alternativa en tabla con caption y encabezados con alcance', async () => {
    // Without caption and scope the table is a grid with no meaning for a
    // screen reader, and the criterion would be met only in name.
    const { wrapper } = await montarPanel({ marco: crearMarco({ series: 5, fechas: 30 }) })

    expect(wrapper.find('[data-alternativa]').exists()).toBe(false)
    await wrapper.get('[data-accion="tabla"]').trigger('click')

    const tabla = wrapper.get('[data-alternativa]')

    expect(tabla.get('caption').text().length).toBeGreaterThan(10)
    expect(tabla.findAll('th[scope="col"]')).toHaveLength(6)
    expect(tabla.findAll('th[scope="row"]')).toHaveLength(5)
    expect(wrapper.get('[data-accion="tabla"]').attributes('aria-expanded')).toBe('true')
  })

  it('una fila de la tabla dispara el mismo drill-down que la grafica', async () => {
    // A drill-down reachable only with a pointer leaves the main function of
    // this screen out of reach of the keyboard.
    const { wrapper } = await montarPanel({ marco: crearMarco({ series: 5, fechas: 30 }) })
    const workspace = useWorkspaceStore()

    await wrapper.get('[data-accion="tabla"]').trigger('click')
    await wrapper.findAll('[data-fila-drill]')[2]!.trigger('click')

    expect(workspace.filtros.unidadNegocio).toEqual(['UNIDAD_2'])
    expect(workspace.ultimaInteraccion?.origen).toBe('tabla')

    wrapper.findComponent(GraficaFalsa).vm.$emit('serie', 3)
    await flushPromises()

    expect(workspace.filtros.unidadNegocio).toEqual(['UNIDAD_2', 'UNIDAD_3'])
    expect(workspace.ultimaInteraccion?.origen).toBe('grafica')
  })

  it('la leyenda enciende y apaga lineas con el teclado', async () => {
    const { wrapper } = await montarPanel({ marco: crearMarco({ series: 5, fechas: 30 }) })
    const workspace = useWorkspaceStore()
    const entradas = wrapper.findAll('[data-leyenda-item]')

    expect(entradas).toHaveLength(5)
    expect(entradas[0]!.attributes('aria-pressed')).toBe('false')

    await entradas[1]!.trigger('click')

    expect(workspace.seriesVisibles).toEqual([1])
    expect(workspace.ultimaInteraccion?.origen).toBe('leyenda')
  })

  it('un cambio de metrica reescribe la consulta que se pide', async () => {
    const { wrapper } = await montarPanel({ marco: crearMarco({ series: 5, fechas: 30 }) })
    const workspace = useWorkspaceStore()

    await wrapper.get('[data-control="metrica"] [data-opcion="ratio_lcr"]').trigger('click')

    expect(workspace.filtros.metrica).toBe('ratio_lcr')
  })

  it('publica la procedencia que el overlay de linaje va a pintar', async () => {
    const { wrapper } = await montarPanel({ marco: crearMarco({ series: 5, fechas: 30 }) })
    const workspace = useWorkspaceStore()

    expect(wrapper.get('[data-origen-serie]').text()).toContain(
      'data/aggregates/serie_tablero.parquet',
    )
    expect(wrapper.findAll('[data-transformacion]').length).toBeGreaterThan(0)
    expect(workspace.origen?.archivo).toBe('data/aggregates/serie_tablero.parquet')
  })

  it('esconde el medidor de fluidez mientras nadie lo pida', async () => {
    // Instrumentation on a demo screen reads as a laboratory instead of a
    // product; it appears with ?medicion=1 and not before.
    const { wrapper } = await montarPanel({ marco: crearMarco({ series: 5, fechas: 30 }) })

    expect(wrapper.find('[data-medicion]').exists()).toBe(false)
  })
})

describe('el panel sin datos', () => {
  it('traduce el 503 tipificado del backend al estado disenado', async () => {
    // If the state never fired because the backend answers something else, the
    // designed screen would be dead code that nobody ever sees.
    const { wrapper } = await montarPanel({
      marco: null,
      error: { statusCode: 503, data: { detail: { codigo: 'datos_no_sembrados' } } },
      estado: 'error',
    })

    expect(wrapper.get('[data-zona="serie"]').attributes('data-estado')).toBe('sin-datos')
    expect(wrapper.get('[data-instruccion]').text()).toContain('make data')
    expect(wrapper.find('[data-degradacion]').exists()).toBe(false)
  })

  it('un filtro sin resultados es el estado vacio, no un fallo', async () => {
    const { wrapper } = await montarPanel({ marco: crearMarco({ series: 0, fechas: 30 }) })

    expect(wrapper.get('[data-zona="serie"]').attributes('data-estado')).toBe('vacio')
    expect(wrapper.find('[data-reintentar]').exists()).toBe(false)
  })

  it('reintentar vuelve a pedir sin perder los filtros', async () => {
    const { wrapper, refresh } = await montarPanel({
      marco: null,
      error: new Error('red'),
      estado: 'error',
    })
    const workspace = useWorkspaceStore()
    workspace.aplicarDrillDown('divisa', 'USD', 'control')

    await wrapper.get('[data-reintentar]').trigger('click')

    expect(refresh).toHaveBeenCalledTimes(1)
    expect(workspace.filtros.divisa).toEqual(['USD'])
  })
})

describe('la consulta que se le pide al endpoint', () => {
  it('fuerza las claves individuales y los 2 000 puntos en la carga completa', () => {
    // This is the headline figure of the delivery. Asking for the full density
    // while still grouping by business unit would answer five lines of 2 000
    // points, and "500 000 points" would quietly stop being true while the
    // screen kept saying it.
    const consulta = consultaDeSerie(
      {
        metrica: 'saldo_disponible_mxn',
        agrupacion: 'unidad_negocio',
        unidadNegocio: [],
        divisa: [],
        bucketVenc: [],
        seriesId: [],
        rangoFechas: null,
      },
      'completa',
    )

    expect(consulta.agrupacion).toBe('serie')
    expect(consulta.max_puntos).toBe(PUNTOS_POR_DENSIDAD.completa)
    expect(consulta.serie_id).toBeUndefined()
  })

  it('manda cada filtro con el nombre que el backend publico', () => {
    // A camel case parameter name is ignored by FastAPI without any error: the
    // screen would show the filter applied and the server would answer the
    // unfiltered series.
    const consulta = consultaDeSerie(
      {
        metrica: 'ratio_lcr',
        agrupacion: 'serie',
        unidadNegocio: ['TESORERIA'],
        divisa: ['USD'],
        bucketVenc: ['1M'],
        seriesId: [7, 9],
        rangoFechas: { desde: '2020-01-01', hasta: '2020-12-31' },
      },
      'detalle',
    )

    expect(consulta).toEqual({
      metrica: 'ratio_lcr',
      agrupacion: 'serie',
      max_puntos: PUNTOS_POR_DENSIDAD.detalle,
      unidad_negocio: ['TESORERIA'],
      divisa: ['USD'],
      bucket_venc: ['1M'],
      serie_id: [7, 9],
      desde: '2020-01-01',
      hasta: '2020-12-31',
    })
  })

  it('lee el codigo estable del fallo y no su mensaje', () => {
    // Distinguishing the designed empty state from a real failure depends on
    // the code alone; matching on the message would break with any rewording.
    expect(codigoDelFallo({ data: { detail: { codigo: 'datos_no_sembrados' } } })).toBe(
      'datos_no_sembrados',
    )
    expect(codigoDelFallo({ data: { detail: 'Not Found' } })).toBeNull()
    expect(codigoDelFallo(new Error('red'))).toBeNull()
  })
})

describe('las claves de los vocabularios cerrados existen en los dos catalogos', () => {
  it('resuelve toda metrica, agrupacion y densidad', () => {
    // These keys are looked up through a map, so the literal scan of
    // test/contratos.spec cannot see them: a typo would render the dotted path
    // itself on screen, in both languages.
    const declaradas = { es: new Set(clavesDe('es')), en: new Set(clavesDe('en')) }
    const usadas = [
      ...Object.values(CLAVE_METRICA),
      ...Object.values(CLAVE_AGRUPACION),
      ...Object.values(CLAVE_DENSIDAD),
    ]

    expect(usadas.filter(clave => !declaradas.es.has(clave) || !declaradas.en.has(clave))).toEqual(
      [],
    )
  })
})
