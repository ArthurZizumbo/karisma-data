import type { VueWrapper } from '@vue/test-utils'
import type { RolUsuario } from '~/types/sesion'

import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'

import { flushPromises, mount } from '@vue/test-utils'
import { ref, shallowRef } from 'vue'
import { createMemoryHistory, createRouter, RouterLink } from 'vue-router'
import { afterEach, describe, expect, it, vi } from 'vitest'

import Exploracion from '~/pages/exploracion/index.vue'
import { LIMITE_PAGINA, RUTA_BUSQUEDA } from '~/composables/useBusquedaCatalogo'
import { useSesion } from '~/composables/useSesion'
import { MODULOS, RUTA_INDICE, RUTAS_CONTRATO } from '~/utils/navegacion'
import { crearI18nDePrueba, mensaje } from './i18nDePrueba'

/**
 * US-ENTREGA-A4 — `/exploracion` stops being scaffolding.
 *
 * Two defects are worth a spec here and nothing else is. The first is that the
 * screen gets rewritten without connecting `useBusquedaCatalogo`, which would
 * swap one piece of scaffolding for another that merely looks busier: the
 * assertions below check that the shipped page names no pending state and that
 * the catalogue endpoint is the one it asks. The second is that only the happy
 * path arrives, and the empty answer lands as a list with no rows and no
 * explanation, which reads as a screen that broke halfway.
 *
 * Only the transport is replaced. The composable runs for real -state machine,
 * reactive query and the on demand request- because that is where the defects
 * live; a double of the composable would leave exactly the code under test
 * unmeasured.
 */

/** Route this screen renders, taken from the contract and never typed here. */
const RUTA_EXPLORACION = MODULOS.find(modulo => modulo.id === '2')!.ruta

/** Branches of module 2 that live on a screen of their own. */
const CONTINUACIONES = MODULOS.find(modulo => modulo.id === '2')!
  .subrutas.filter(subruta => subruta.ruta !== RUTA_EXPLORACION)

/**
 * Reads a file of the repository.
 *
 * The path travels as a variable on purpose: with a literal, Vite rewrites the
 * `new URL(..., import.meta.url)` pattern into an asset reference and the URL
 * stops being a file one.
 */
function leerDelRepositorio(relativa: string): string {
  return readFileSync(fileURLToPath(new URL(relativa, import.meta.url)), 'utf8')
}

/** One hit of `GET /api/catalog/search`, as the backend spells it. */
const CAMPO_CRUDO = {
  field_id: 41,
  physical_name: 'saldo_disponible_mxn',
  business_name: 'Saldo disponible',
  definition: 'Saldo de la posicion disponible al cierre del dia habil.',
  source: { code: 'liquidez', display_name: 'Tesoreria y liquidez' },
  owner: { area: 'Tesoreria', steward: 'Ana Ruiz' },
  validity: { valid_from: '2024-01-01', valid_to: null, is_current: true },
  facets: {
    domain: 'liquidez',
    data_type: 'decimal',
    sensitivity: 'interna',
    refresh_frequency: 'diaria',
    certification: 'certificado',
    unit: 'MXN',
    metric_agg: 'sum',
  },
}

const BUSQUEDA_CRUDA = {
  query: 'saldo',
  tsquery: 'saldo',
  total: 42,
  limit: LIMITE_PAGINA,
  offset: 0,
  results: [CAMPO_CRUDO],
  facet_counts: { domain: { liquidez: 30, riesgo: 12 } },
}

const BUSQUEDA_VACIA = { ...BUSQUEDA_CRUDA, total: 0, results: [], facet_counts: { domain: {} } }

interface Escenario {
  /** Body the search answers with. */
  busqueda?: unknown
  /** Failure the search rejects with. */
  fallo?: unknown
  /** True to leave the request in flight, which is the loading state. */
  enVuelo?: boolean
  rol?: RolUsuario
}

interface DobleFetch {
  /** Paths `useFetch` was installed on, in order. */
  rutas: string[]
  /** Query of every request that actually left. */
  consultas: Record<string, unknown>[]
}

/**
 * Installs the transport double of the catalogue endpoint.
 *
 * The `transform` of the composable is applied here, so the snake_case mapping
 * is exercised instead of being bypassed by a pre-mapped fixture.
 */
function instalarFetch(escenario: Escenario): DobleFetch {
  const doble: DobleFetch = { rutas: [], consultas: [] }

  vi.stubGlobal('useFetch', (ruta: unknown, opciones: {
    query?: { value: Record<string, unknown> }
    transform?: (respuesta: unknown) => unknown
    default?: () => unknown
  }) => {
    doble.rutas.push(String(ruta))

    const data = shallowRef<unknown>(opciones.default?.() ?? null)
    const error = shallowRef<unknown>(null)
    const status = ref<'idle' | 'pending' | 'success' | 'error'>('idle')

    const refresh = async (): Promise<void> => {
      doble.consultas.push({ ...opciones.query?.value })
      if (escenario.fallo !== undefined) {
        error.value = escenario.fallo
        status.value = 'error'
        return
      }
      if (escenario.enVuelo === true) {
        status.value = 'pending'
        return
      }
      const cuerpo = escenario.busqueda ?? BUSQUEDA_CRUDA
      data.value = opciones.transform === undefined ? cuerpo : opciones.transform(cuerpo)
      status.value = 'success'
    }

    return { data, error, status, refresh }
  })

  vi.stubGlobal('definePageMeta', () => undefined)
  vi.stubGlobal('navigateTo', vi.fn(async () => undefined))

  return doble
}

let montado: VueWrapper | null = null

/** Mounts the screen on its contract route, with a session and a transport. */
async function montar(escenario: Escenario = {}) {
  const doble = instalarFetch(escenario)

  const { sesion } = useSesion()
  sesion.value = { usuario: 'demo', nombre: 'Perfil de demostracion', rol: escenario.rol ?? 'analista' }

  const router = createRouter({
    history: createMemoryHistory(),
    routes: [RUTA_INDICE, ...RUTAS_CONTRATO].map(path => ({
      path,
      component: { template: '<div />' },
    })),
  })
  await router.push(RUTA_EXPLORACION)
  await router.isReady()

  const wrapper = mount(Exploracion, {
    attachTo: document.body,
    global: {
      plugins: [router, crearI18nDePrueba()],
      components: { NuxtLink: RouterLink },
      stubs: { Icon: true },
    },
  })
  montado = wrapper
  return { wrapper, doble }
}

/** Types a term and submits the form, which is the only way to search. */
async function buscar(wrapper: VueWrapper, termino = 'saldo'): Promise<void> {
  await wrapper.get('[data-campo-busqueda]').setValue(termino)
  await wrapper.get('[data-buscador-catalogo]').trigger('submit')
  await flushPromises()
}

afterEach(() => {
  montado?.unmount()
  montado = null
  document.body.innerHTML = ''
  vi.unstubAllGlobals()
})

describe('la pantalla de catalogo compone desde el composable', () => {
  it('no queda ni una referencia al estado de andamiaje', async () => {
    // The defect: the screen is rewritten without wiring the composable and a
    // different piece of scaffolding is left in its place. This is the metric
    // of CA-7 read from the shipped file, so it cannot pass on a stale import.
    const fuente = leerDelRepositorio('../app/pages/exploracion/index.vue')

    expect(fuente).not.toContain('EstadoPendiente')

    const { wrapper } = await montar()

    expect(wrapper.find('[data-pendiente]').exists()).toBe(false)
    expect(wrapper.get('[data-ruta]').attributes('data-ruta')).toBe(RUTA_EXPLORACION)
  })

  it('pide el catalogo al endpoint del contrato y no antes de que se lo pidan', async () => {
    // `immediate: false` is what keeps the endpoint from answering a 422 to the
    // empty term the moment the page loads; a request on mount would put that
    // error in front of a reader who typed nothing.
    const { wrapper, doble } = await montar()

    expect(doble.rutas).toContain(RUTA_BUSQUEDA)
    expect(doble.consultas).toHaveLength(0)

    await buscar(wrapper, 'saldo')

    expect(doble.consultas).toHaveLength(1)
    expect(doble.consultas[0]).toMatchObject({ q: 'saldo', limit: LIMITE_PAGINA })
  })

  it('un termino mas corto que el minimo no sale a la red', async () => {
    // Below the minimum the endpoint accepts, the form says so and nothing
    // leaves, which is why this screen never shows a 422 to a reader.
    const { wrapper, doble } = await montar()

    await wrapper.get('[data-campo-busqueda]').setValue('a')

    expect(wrapper.get('[data-accion-busqueda]').attributes('disabled')).toBeDefined()

    await wrapper.get('[data-buscador-catalogo]').trigger('submit')
    await flushPromises()

    expect(doble.consultas).toHaveLength(0)
  })

  it('los conteos por dominio salen del total de coincidencias y acotan la consulta', async () => {
    // Counting over the visible page instead of the whole matching set would
    // make a chip change meaning as the reader narrows.
    const { wrapper, doble } = await montar()
    await buscar(wrapper)

    const filtro = wrapper.get('[data-filtro-dominios]')
    expect(filtro.get('[data-dominio="liquidez"]').text()).toContain('30')
    expect(filtro.get('[data-dominio="riesgo"]').text()).toContain('12')

    await filtro.get('[data-dominio="riesgo"]').trigger('click')
    await flushPromises()

    expect(doble.consultas).toHaveLength(2)
    expect(doble.consultas[1]).toMatchObject({ q: 'saldo', domain: 'riesgo' })
    expect(filtro.get('[data-dominio="riesgo"]').attributes('aria-pressed')).toBe('true')
  })

  it('la lista dice cuantos campos muestra de cuantos coinciden', async () => {
    // Twenty rows over forty two matches, with no line saying so, reads as a
    // catalogue of twenty fields: the screen would understate itself by half.
    const { wrapper } = await montar()
    await buscar(wrapper)

    expect(wrapper.get('[data-estado]').attributes('data-estado')).toBe('listo')
    expect(wrapper.findAll('[data-fila-campo]')).toHaveLength(1)
    expect(wrapper.get('[data-conteo]').text()).toBe(
      mensaje('es', 'catalog.explore.results.shown')
        .replace('{shown}', '1')
        .replace('{total}', '42'),
    )
    expect(wrapper.find('[data-recorte]').exists()).toBe(true)
  })
})

describe('los cuatro estados no felices de la pantalla de catalogo', () => {
  it('cargando reserva la altura de las filas y lo anuncia', async () => {
    // A spinner of its own height moves everything below it the moment the
    // answer lands, which is the layout jump this screen is measured against.
    const { wrapper } = await montar({ enVuelo: true })
    await buscar(wrapper)

    const estado = wrapper.get('[data-estado="cargando"]')

    expect(estado.attributes('aria-busy')).toBe('true')
    expect(estado.attributes('role')).toBe('status')
    expect(estado.findAll('[data-esqueleto]')).toHaveLength(5)
    expect(estado.text()).toContain(mensaje('es', 'catalog.explore.state.loading'))
  })

  it('sin resultados explica por que no hay nada, en vez de una tabla vacia', async () => {
    // The defect this closes: the happy path ships and the empty answer lands
    // as a list of zero rows, which reads as a screen that failed to load.
    const { wrapper } = await montar({ busqueda: BUSQUEDA_VACIA })
    await buscar(wrapper, 'nada')

    const estado = wrapper.get('[data-estado="vacio"]')

    expect(wrapper.find('[data-resultados]').exists()).toBe(false)
    expect(estado.text()).toContain(mensaje('es', 'catalog.explore.state.empty.body'))
    expect(estado.text()).toContain(mensaje('es', 'catalog.explore.state.empty.advice'))
  })

  it('el error conserva el termino escrito y ofrece reintentar', async () => {
    // An error state that empties the box makes the reader retype the term to
    // try again, which is the cost this state exists to avoid.
    const { wrapper, doble } = await montar({ fallo: { statusCode: 500 } })
    await buscar(wrapper, 'contraparte')

    const estado = wrapper.get('[data-estado="error"]')

    expect(estado.attributes('role')).toBe('alert')
    expect(estado.text()).toContain(mensaje('es', 'catalog.explore.state.error.body'))
    expect(
      (wrapper.get('[data-campo-busqueda]').element as HTMLInputElement).value,
    ).toBe('contraparte')

    await estado.get('[data-reintentar]').trigger('click')
    await flushPromises()

    expect(doble.consultas).toHaveLength(2)
    expect(doble.consultas[1]).toMatchObject({ q: 'contraparte' })
  })

  it('sin permiso nombra la continuacion cerrada y el perfil que pide', async () => {
    // The catalogue demands no scope and its continuations demand `analista`.
    // Hiding them, which is what the sidebar does, leaves an operations reader
    // on a screen with no way forward and no reason given.
    const { wrapper } = await montar({ rol: 'operativo' })

    const estado = wrapper.get('[data-estado="sin-permiso"]')

    expect(wrapper.findAll('[data-continuacion]')).toHaveLength(0)
    expect(estado.findAll('[data-bloqueada]')).toHaveLength(CONTINUACIONES.length)
    expect(estado.get('[data-perfil-faltante]').text()).toContain(mensaje('es', 'authz.role.analista'))
    expect(estado.text()).toContain(mensaje('es', 'authz.noPermission.requestTo'))
  })

  it('con el perfil que alcanza, las continuaciones son enlaces y no un aviso', async () => {
    // The mirror of the case above: a refusal shown to whoever is allowed in
    // would be the same defect with the sign flipped.
    const { wrapper } = await montar({ rol: 'analista' })

    const enlaces = wrapper.findAll('[data-continuacion]')

    expect(enlaces).toHaveLength(CONTINUACIONES.length)
    expect(enlaces.map(enlace => enlace.attributes('href')))
      .toEqual(CONTINUACIONES.map(subruta => subruta.ruta))
    expect(wrapper.find('[data-estado="sin-permiso"]').exists()).toBe(false)
  })

  it('las cuatro marcas de estado existen en el DOM', async () => {
    // The screen is scored on four unhappy states, not on the happy path. This
    // is the count itself: a state that was designed but never wired leaves its
    // mark missing here even though every other assertion above passes.
    const marcas: string[] = []

    for (const escenario of [
      { enVuelo: true } as Escenario,
      { busqueda: BUSQUEDA_VACIA } as Escenario,
      { fallo: { statusCode: 500 } } as Escenario,
      { rol: 'operativo' } as Escenario,
    ]) {
      const { wrapper } = await montar(escenario)
      if (escenario.rol === undefined) {
        await buscar(wrapper)
      }
      marcas.push(
        ...wrapper.findAll('[data-estado]').map(nodo => nodo.attributes('data-estado')!),
      )
      wrapper.unmount()
      montado = null
      vi.unstubAllGlobals()
    }

    // The initial state also carries a mark and is not one of the four: it is
    // the designed opening of the screen, not a state something went wrong in.
    for (const marca of ['cargando', 'vacio', 'error', 'sin-permiso']) {
      expect(marcas, marca).toContain(marca)
    }
  })
})
