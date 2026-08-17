import type { VueWrapper } from '@vue/test-utils'
import type { RolUsuario } from '~/types/sesion'

import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'

import { flushPromises, mount } from '@vue/test-utils'
import { ref, shallowRef, unref } from 'vue'
import { createMemoryHistory, createRouter, RouterLink } from 'vue-router'
import { afterEach, describe, expect, it, vi } from 'vitest'

import Exploracion from '~/pages/exploracion/index.vue'
import { LIMITE_PAGINA, PARAMETRO_TERMINO, RUTA_BUSQUEDA } from '~/composables/useBusquedaCatalogo'
import { rutaDeLinaje } from '~/composables/useLinajeCampo'
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

/** Landing screen of governance, which is the exit out of the result. */
const RUTA_GOBIERNO = MODULOS.find(modulo => modulo.id === '3')!.ruta

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

/**
 * The journey of the same field, as `GET /api/catalog/{id}/lineage` answers.
 *
 * Two hops and not five: what this suite measures is that the row opens the
 * lineage OF ITS FIELD, and the shape of the journey is what
 * `diccionarioCampos.spec.ts` already exercises hop by hop.
 */
const LINAJE_CRUDO = {
  field_id: CAMPO_CRUDO.field_id,
  physical_name: CAMPO_CRUDO.physical_name,
  business_name: CAMPO_CRUDO.business_name,
  source: {
    code: 'liquidez',
    display_name: 'Tesoreria y liquidez',
    system_of_record: 'CORE-TES',
    has_extract: true,
  },
  owner: CAMPO_CRUDO.owner,
  validity: CAMPO_CRUDO.validity,
  facets: CAMPO_CRUDO.facets,
  steps: [
    {
      order: 1,
      stage: 'origen',
      system_code: 'CORE-TES',
      system_name: 'Core de tesoreria',
      transformation_code: 'origin_capture',
      transformation_detail: 'Captura diaria en el sistema de registro.',
      owner: { area: 'Tesoreria', steward: 'Ana Ruiz' },
      effective_from: '2024-01-01',
      effective_to: null,
      is_current: true,
      stored: true,
    },
    {
      order: 2,
      stage: 'presentacion',
      system_code: 'PORTAL',
      system_name: 'Portal de datos',
      transformation_code: 'field_publish',
      transformation_detail: CAMPO_CRUDO.physical_name,
      owner: { area: 'Datos', steward: 'Luis Prado' },
      effective_from: '2024-01-01',
      effective_to: null,
      is_current: true,
      stored: false,
    },
  ],
}

interface Escenario {
  /** Body the search answers with. */
  busqueda?: unknown
  /** Failure the search rejects with. */
  fallo?: unknown
  /** True to leave the request in flight, which is the loading state. */
  enVuelo?: boolean
  rol?: RolUsuario
  /** Query string the screen opens on, which is how a term arrives cold. */
  consulta?: Record<string, string>
}

interface DobleFetch {
  /** Paths `useFetch` was installed on, in order. */
  rutas: string[]
  /** Query of every SEARCH that actually left. */
  consultas: Record<string, unknown>[]
  /** Resolved path of every request that left, search and lineage alike. */
  peticiones: string[]
}

/**
 * Installs the transport double of the catalogue endpoint.
 *
 * The `transform` of the composable is applied here, so the snake_case mapping
 * is exercised instead of being bypassed by a pre-mapped fixture.
 */
function instalarFetch(escenario: Escenario): DobleFetch {
  const doble: DobleFetch = { rutas: [], consultas: [], peticiones: [] }

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
      // The screen installs two endpoints since the row opens the journey of
      // its field, and the path is a computed one: it is resolved here, at the
      // moment of the request, because until a row is pressed it is empty.
      const destino = String(unref(ruta))
      doble.peticiones.push(destino)

      if (destino.endsWith('/lineage')) {
        data.value = opciones.transform === undefined
          ? LINAJE_CRUDO
          : opciones.transform(LINAJE_CRUDO)
        status.value = 'success'
        return
      }

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
  await router.push({ path: RUTA_EXPLORACION, query: escenario.consulta ?? {} })
  await router.isReady()

  const wrapper = mount(Exploracion, {
    attachTo: document.body,
    global: {
      plugins: [router, crearI18nDePrueba()],
      components: { NuxtLink: RouterLink },
      stubs: { Icon: true },
    },
  })
  await flushPromises()
  montado = wrapper
  return { wrapper, doble, router }
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

describe('el catalogo deja de ser un callejon', () => {
  it('cada fila abre el linaje de SU campo, no el de otro', async () => {
    // Hallazgo n.o 1 de la revision de diseno: ninguna fila era interactiva y
    // no habia ruta al linaje, asi que la primera promesa del producto -saber
    // de donde sale una cifra- no se alcanzaba desde la pantalla que encuentra
    // la cifra. El identificador del campo viaja en la peticion: una fila que
    // abriera el panel sin pedir SU recorrido pasaria cualquier prueba de
    // apertura y mentiria en la primera pantalla.
    const { wrapper, doble } = await montar()
    await buscar(wrapper)

    const filas = wrapper.findAll('[data-fila-campo]')

    expect(filas).toHaveLength(1)

    await filas[0]!.get('[data-ver-linaje]').trigger('click')
    await flushPromises()

    expect(doble.peticiones).toContain(rutaDeLinaje(CAMPO_CRUDO.field_id))
    expect(wrapper.get('[data-linaje-overlay]').attributes('open')).toBeDefined()
    expect(wrapper.get('[data-encabezado-linaje]').text())
      .toContain(CAMPO_CRUDO.business_name)

    // Y se puede salir. Un panel sin cierre sobre la pantalla de
    // descubrimiento no seria una revelacion, seria una navegacion.
    await wrapper.get('[data-cerrar-linaje]').trigger('click')
    await flushPromises()

    expect(wrapper.get('[data-linaje-overlay]').attributes('open')).toBeUndefined()
  })

  it('el control de la fila nombra el campo que abre', async () => {
    // Veinte filas con el mismo rotulo accesible -"Ver el linaje"- dejan al
    // lector de pantalla eligiendo entre veinte controles identicos.
    const { wrapper } = await montar()
    await buscar(wrapper)

    expect(wrapper.get('[data-ver-linaje]').attributes('aria-label')).toBe(
      mensaje('es', 'catalog.explore.results.openLineage')
        .replace('{field}', CAMPO_CRUDO.physical_name),
    )
  })

  it('el resultado ofrece una salida hacia gobierno del dato', async () => {
    // La segunda mitad de CA-12. La tabla es densa a proposito y no lleva la
    // definicion del campo: esa ficha vive en gobierno, y sin esta salida el
    // recorte seria una perdida de contenido en vez de un reparto.
    const { wrapper } = await montar()
    await buscar(wrapper)

    expect(wrapper.get('[data-salida="gobierno"]').attributes('href')).toBe(RUTA_GOBIERNO)
  })

  it('la lista es la tabla del sistema y anuncia su orden', async () => {
    // La densidad prometida por DESIGN.md son 34 px de fila contra los 80 de
    // la lista anterior, y el orden se anuncia con aria-sort o no existe para
    // quien no ve la flecha.
    const { wrapper } = await montar()
    await buscar(wrapper)

    const tabla = wrapper.get('[data-tabla-datos]')
    const encabezados = tabla.findAll('th[scope="col"]')

    expect(encabezados.length).toBeGreaterThan(1)
    for (const encabezado of encabezados) {
      expect(encabezado.attributes('aria-sort')).toBe('none')
    }

    await tabla.get('[data-ordenar="campo"]').trigger('click')

    expect(tabla.get('th[scope="col"]').attributes('aria-sort')).toBe('ascending')
  })
})

describe('la busqueda del catalogo es direccionable', () => {
  it('abre en frio con el termino de la direccion aplicado y pintado', async () => {
    // CA-13. El buscador del cromo navega a /exploracion?q=<termino> desde la
    // ola B; si esta pantalla no lo aplica, el control lleva a un catalogo que
    // no busco nada y el termino queda de adorno en la barra de direcciones.
    const { wrapper, doble } = await montar({ consulta: { [PARAMETRO_TERMINO]: 'saldo' } })

    expect(doble.consultas).toHaveLength(1)
    expect(doble.consultas[0]).toMatchObject({ q: 'saldo' })
    expect(wrapper.get('[data-estado]').attributes('data-estado')).toBe('listo')
    expect((wrapper.get('[data-campo-busqueda]').element as HTMLInputElement).value).toBe('saldo')
  })

  it('un termino mas corto que el minimo llega a la pantalla y no a la red', async () => {
    // Una direccion escrita a mano puede traer cualquier cosa. El minimo lo
    // decide el endpoint, y el 422 no se le ensena a nadie.
    const { wrapper, doble } = await montar({ consulta: { [PARAMETRO_TERMINO]: 'a' } })

    expect(doble.consultas).toHaveLength(0)
    expect(wrapper.get('[data-estado]').attributes('data-estado')).toBe('inicial')
  })

  it('la busqueda escribe el termino en la direccion', async () => {
    // Sin esto el termino se destruye al usar las salidas que la propia
    // pantalla ofrece: se vuelve al catalogo y ya no hay nada escrito.
    const { wrapper, router } = await montar()
    await buscar(wrapper, 'contraparte')

    expect(router.currentRoute.value.query[PARAMETRO_TERMINO]).toBe('contraparte')
  })

  it('un termino nuevo en la direccion vuelve a consultar sin desmontar', async () => {
    // El buscador del cromo esta en todas las pantallas, catalogo incluido:
    // navegar de /exploracion a /exploracion cambia la direccion y nada mas.
    const { doble, router } = await montar({ consulta: { [PARAMETRO_TERMINO]: 'saldo' } })

    await router.replace({ path: RUTA_EXPLORACION, query: { [PARAMETRO_TERMINO]: 'mora' } })
    await flushPromises()

    expect(doble.consultas).toHaveLength(2)
    expect(doble.consultas[1]).toMatchObject({ q: 'mora' })
  })

  it('publica el termino con replace, y no deja una entrada por busqueda', async () => {
    // La otra mitad de CA-13, y la que decide si el viaje de ida y vuelta
    // sirve de algo: con `push`, cada busqueda deja una entrada, asi que Atras
    // no saca al lector del catalogo -lo devuelve a su busqueda anterior, una
    // por una, hasta la que abrio la pantalla sin termino ninguno-. Sobre la
    // direccion las dos formas se ven igual, y por eso ninguna de las
    // aserciones de arriba lo nota: las dos dejan el mismo `?q=` puesto.
    const { wrapper, router } = await montar()
    await buscar(wrapper, 'contraparte')
    await buscar(wrapper, 'liquidez')

    expect(router.currentRoute.value.query[PARAMETRO_TERMINO]).toBe('liquidez')

    router.back()
    await flushPromises()

    expect(router.currentRoute.value.query[PARAMETRO_TERMINO]).not.toBe('contraparte')
  })

  it('un termino que llega por la direccion suelta el filtro de dominio', async () => {
    // El termino viene de fuera de la pantalla -el buscador del cromo, un
    // enlace compartido, el boton Atras- y responderlo a traves del dominio que
    // el lector acoto para el termino ANTERIOR devuelve un vacio que nadie
    // pidio: la pantalla diria "ningun campo coincide" sobre un catalogo que si
    // tiene la respuesta, y el filtro que lo causo llego de otra busqueda.
    const { wrapper, doble, router } = await montar({
      consulta: { [PARAMETRO_TERMINO]: 'saldo' },
    })

    await wrapper.get('[data-filtro-dominios] [data-dominio="riesgo"]').trigger('click')
    await flushPromises()

    expect(doble.consultas[1]).toMatchObject({ q: 'saldo', domain: 'riesgo' })

    await router.replace({ path: RUTA_EXPLORACION, query: { [PARAMETRO_TERMINO]: 'mora' } })
    await flushPromises()

    expect(doble.consultas[2]).toMatchObject({ q: 'mora' })
    expect(doble.consultas[2]).not.toHaveProperty('domain')
  })
})

describe('los cuatro estados se anuncian', () => {
  it('el resultado y el vacio ganan region viva, y los otros dos la conservan', async () => {
    // CA-15. Cargando y error ya se anunciaban; listo y vacio eran mudos, asi
    // que a quien no ve la pantalla se le decia que la busqueda estaba en
    // marcha y nunca como termino.
    const conFilas = await montar()
    await buscar(conFilas.wrapper)

    expect(conFilas.wrapper.get('[data-conteo]').attributes('role')).toBe('status')

    conFilas.wrapper.unmount()
    montado = null
    vi.unstubAllGlobals()

    const sinFilas = await montar({ busqueda: BUSQUEDA_VACIA })
    await buscar(sinFilas.wrapper, 'nada')

    expect(sinFilas.wrapper.get('[data-estado="vacio"]').attributes('role')).toBe('status')
  })
})
