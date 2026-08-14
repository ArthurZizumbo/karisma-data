import type { VueWrapper } from '@vue/test-utils'
import type { SolicitudExportacion, TrabajoDetalle, TrabajoResumen } from '~/types/exportacion'

import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { flushPromises, mount } from '@vue/test-utils'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { createMemoryHistory, createRouter } from 'vue-router'

import { analizarFiltros, retrasoDeDemostracion } from '~/composables/useExportaciones'
import Exportar from '~/pages/exploracion/exportar.vue'
import {
  falloDeExportacion,
  INTERVALO_SONDEO_MS,
  MAXIMO_SONDEOS,
  RUTA_EXPORTACION,
  useExportacionesStore,
} from '~/stores/exportaciones'
import { RUTA_INDICE, RUTAS_CONTRATO } from '~/utils/navegacion'
import { crearI18nDePrueba, mensaje } from './i18nDePrueba'

/**
 * US-009 - the export watch, the three moments and the honesty of the screen.
 *
 * Nine defects live here and nowhere else, and each one is expensive in a
 * different way: a timer that is never cleared keeps hitting the backend for as
 * long as the tab is open; an interval lowered "so it looks better" triples the
 * traffic of every active reader; a moment fabricated from the query string
 * produces a screenshot of a link that never existed, which is exactly what the
 * A4 evidence cannot contain; a label typed into a template renders the same
 * Spanish sentence to a reader who chose English; a signed link compared
 * against the instant of the render keeps offering a download the backend
 * already answers with a 410; a history read only at mount hides the export
 * the same analyst asked for in another tab until the page is reloaded; a store
 * that outlives the session shows one analyst the exports of the one who used
 * the tab before them; an emptiness derived from the card the reader collapsed
 * announces that nothing is running over a job that is running; and a failure
 * that no success ever clears leaves the red band on screen for the rest of the
 * visit.
 *
 * The transport is the only thing replaced. The catalogues, the store, the
 * components and the page are the ones the application ships.
 */

const RUTA_PANTALLA = '/exploracion/exportar'

/** A relative path, exactly the shape the backend mints. */
const URL_FIRMADA = `/api/export/a1/download?exp=1786000000&sig=${'f'.repeat(64)}`

const SOLICITUD: SolicitudExportacion = { dataset: 'creditos', formato: 'csv', filtros: {} }

/** One job of the wire, with the fields of the contract and nothing else. */
function trabajo(parcial: Partial<TrabajoDetalle> = {}): TrabajoDetalle {
  return {
    job_id: 'a1',
    dataset: 'creditos',
    formato: 'csv',
    estado: 'pendiente',
    filas: null,
    tamano_bytes: null,
    solicitado_en: '2026-08-13T20:00:00+00:00',
    iniciado_en: null,
    terminado_en: null,
    error: null,
    url_descarga: null,
    caduca_en: null,
    ...parcial,
  }
}

/** A finished job with a live link, as the polling endpoint answers it. */
function completado(parcial: Partial<TrabajoDetalle> = {}): TrabajoDetalle {
  return trabajo({
    estado: 'completado',
    filas: 1_000_000,
    tamano_bytes: 48_000_000,
    iniciado_en: '2026-08-13T20:00:01+00:00',
    terminado_en: '2026-08-13T20:00:12+00:00',
    url_descarga: URL_FIRMADA,
    caduca_en: '2026-12-31T20:00:12+00:00',
    ...parcial,
  })
}

interface Opciones {
  method?: string
  body?: unknown
  query?: Record<string, unknown>
}

/**
 * The four endpoints of `/api/export`, counted call by call.
 *
 * `guion` is the sequence the polling endpoint answers with; once it runs out
 * the last answer repeats, which is what a job that stays in progress looks
 * like from the browser. `historial` is answered as a copy, so a test can push
 * to it -that is what another tab of the same analyst looks like from here-
 * without editing the array the store is already holding. `fallosDeLista` makes
 * that many leading reads of the history fail the way the API does when the job
 * registry is unreachable: a 503 with the code the interface keys its copy on.
 * `fallosDeDetalle` does the same to the poll, with the status the test names:
 * a 500 is the blip in the middle of a watch, and a 401 is the session dying
 * under it.
 */
function crearServidor(
  opciones: {
    historial?: TrabajoResumen[]
    guion?: TrabajoDetalle[]
    fallosDeLista?: number
    fallosDeDetalle?: number
    estadoDeDetalle?: number
  } = {},
) {
  const historial = opciones.historial ?? []
  const guion = [...(opciones.guion ?? [])]
  const fallosDeLista = opciones.fallosDeLista ?? 0
  const fallosDeDetalle = opciones.fallosDeDetalle ?? 0
  const estadoDeDetalle = opciones.estadoDeDetalle ?? 500
  const llamadas = { alta: 0, lista: 0, detalle: 0 }
  // Bodies of the requests, kept apart from the counter: what the form chose is
  // only visible on the wire, and a count cannot tell csv from xlsx.
  const solicitados: SolicitudExportacion[] = []
  let ultimo: TrabajoDetalle = trabajo({ estado: 'en_proceso' })

  return {
    llamadas,
    solicitados,
    async manejar(ruta: string, opts: Opciones = {}): Promise<unknown> {
      if (ruta === RUTA_EXPORTACION && opts.method === 'POST') {
        llamadas.alta += 1
        solicitados.push(opts.body as SolicitudExportacion)
        return trabajo({ estado: 'pendiente' })
      }
      if (ruta === RUTA_EXPORTACION) {
        llamadas.lista += 1
        if (llamadas.lista <= fallosDeLista) {
          throw Object.assign(new Error('el registro de trabajos no responde'), {
            status: 503,
            data: { detail: { codigo: 'trabajos_no_disponibles' } },
          })
        }
        return [...historial]
      }
      llamadas.detalle += 1
      if (llamadas.detalle <= fallosDeDetalle) {
        // A loose `detail`, which is the shape both a 500 of the server and the
        // 401 of US-015 arrive with. Neither carries a code of the export
        // contract.
        throw Object.assign(new Error('el sondeo no obtuvo respuesta'), {
          status: estadoDeDetalle,
          data: { detail: 'sesion_expirada' },
        })
      }
      ultimo = guion.shift() ?? ultimo
      return ultimo
    },
  }
}

type Servidor = ReturnType<typeof crearServidor>

/** Installs the transport and the two Nuxt helpers the screen reaches for. */
function instalarEntorno(servidor: Servidor): void {
  vi.stubGlobal('$fetch', vi.fn(async (ruta: string, opts?: Opciones) => servidor.manejar(ruta, opts)))
  vi.stubGlobal('navigateTo', vi.fn(async () => undefined))
  vi.stubGlobal('definePageMeta', () => undefined)
}

/**
 * Drives `document.hidden`, which is read only.
 *
 * @param oculta - Whether the reader is looking at another tab.
 */
function ocultarPestana(oculta: boolean): void {
  Object.defineProperty(document, 'hidden', { configurable: true, get: () => oculta })
}

/**
 * Boots the client plugin the way the Nuxt runtime does, and nothing else.
 *
 * `defineNuxtPlugin` is an auto-import and the module calls it while it is
 * being evaluated, so the double has to be installed before the import: there
 * is no second chance once the module is in the cache.
 *
 * @returns The store the boot created, which is the one the application holds.
 */
async function arrancarLaAplicacion(): Promise<ReturnType<typeof useExportacionesStore>> {
  vi.stubGlobal('defineNuxtPlugin', (arranque: () => void) => arranque)
  const modulo = await import('~/plugins/exportaciones.client')
  const arranque = modulo.default as unknown as () => void
  arranque()
  return useExportacionesStore()
}

let montado: VueWrapper | null = null
let tienda: ReturnType<typeof useExportacionesStore> | null = null

/** The store of this test, with the transport already replaced. */
function abrirTienda(servidor: Servidor): ReturnType<typeof useExportacionesStore> {
  instalarEntorno(servidor)
  tienda = useExportacionesStore()
  return tienda
}

/**
 * Mounts the export screen on a route, with a query and a server.
 *
 * @param servidor - Fake API.
 * @param consulta - Query string of the visit, where `?momento=` travels.
 */
async function montar(
  servidor: Servidor,
  consulta: Record<string, string> = {},
): Promise<VueWrapper> {
  instalarEntorno(servidor)

  const router = createRouter({
    history: createMemoryHistory(),
    routes: [RUTA_INDICE, ...RUTAS_CONTRATO].map(path => ({
      path,
      component: { template: '<div />' },
    })),
  })
  await router.push({ path: RUTA_PANTALLA, query: consulta })
  await router.isReady()

  const wrapper = mount(Exportar, {
    global: {
      plugins: [router, crearI18nDePrueba()],
      stubs: { Icon: true },
    },
  })
  montado = wrapper
  tienda = useExportacionesStore()
  // Twice: the history lands on the first flush and the detail of the job the
  // moment expands is asked for as a consequence of it.
  await flushPromises()
  await flushPromises()

  return wrapper
}

afterEach(() => {
  montado?.unmount()
  montado = null
  // The store listens on `document`, and happy-dom shares one document across
  // the tests of a file: a store left listening would resume its poll when a
  // later test dispatches `visibilitychange`, and would spend the request
  // budget of that test against its server.
  tienda?.detenerSondeo()
  tienda?.olvidarVisibilidad()
  tienda = null
  // Same shared document: a tab left hidden by one test would keep the poll of
  // the next one switched off before it ever armed its timer.
  ocultarPestana(false)
  vi.useRealTimers()
  vi.unstubAllGlobals()
})

describe('el sondeo se apaga solo', () => {
  it('deja de preguntar en cuanto el trabajo llega a un estado terminal', async () => {
    // The defect: an interval that is never cleared. The job finishes, the card
    // stops changing, and the browser keeps asking the backend about a job that
    // will never move again for as long as the tab is open.
    vi.useFakeTimers()
    const servidor = crearServidor({
      guion: [trabajo({ estado: 'en_proceso' }), completado()],
    })
    const exportaciones = abrirTienda(servidor)

    await exportaciones.solicitar(SOLICITUD)
    expect(exportaciones.sondeando).toBe(true)

    await vi.advanceTimersByTimeAsync(INTERVALO_SONDEO_MS)
    expect(exportaciones.sondeando).toBe(true)

    await vi.advanceTimersByTimeAsync(INTERVALO_SONDEO_MS)
    expect(exportaciones.sondeando).toBe(false)

    const gastadas = servidor.llamadas.detalle
    await vi.advanceTimersByTimeAsync(INTERVALO_SONDEO_MS * 5)

    expect(servidor.llamadas.detalle - gastadas).toBe(0)
  })

  it('abandona un trabajo que nunca termina a los diez minutos', async () => {
    // The second way this leaks: the background task is lost when the container
    // scales to zero, so the job never reaches a terminal state and the loop
    // above never fires. The ceiling is what ends it.
    vi.useFakeTimers()
    const servidor = crearServidor()
    const exportaciones = abrirTienda(servidor)

    await exportaciones.solicitar(SOLICITUD)
    await vi.advanceTimersByTimeAsync(INTERVALO_SONDEO_MS * (MAXIMO_SONDEOS + 1))

    expect(servidor.llamadas.detalle).toBe(MAXIMO_SONDEOS)
    expect(exportaciones.sondeando).toBe(false)
    expect(exportaciones.trabajos[0]?.caducadoEnCliente).toBe(true)
  })

  it('se calla mientras la pestana esta oculta', async () => {
    // A reader who walked away is not reading anything, and the poll is the
    // only thing in this screen that costs the portal money while nobody looks.
    vi.useFakeTimers()
    const servidor = crearServidor()
    const exportaciones = abrirTienda(servidor)

    await exportaciones.solicitar(SOLICITUD)
    Object.defineProperty(document, 'hidden', { configurable: true, get: () => true })
    document.dispatchEvent(new Event('visibilitychange'))

    await vi.advanceTimersByTimeAsync(INTERVALO_SONDEO_MS * 4)
    expect(servidor.llamadas.detalle).toBe(0)

    Object.defineProperty(document, 'hidden', { configurable: true, get: () => false })
    document.dispatchEvent(new Event('visibilitychange'))
    await vi.advanceTimersByTimeAsync(INTERVALO_SONDEO_MS)

    expect(servidor.llamadas.detalle).toBe(1)
  })
})

describe('la vigilancia no es de la pantalla', () => {
  it('sigue el trabajo despues de que el lector se vaya a otra ruta', async () => {
    // CA-4 entire: the state of a job is readable from any screen. The defect
    // is the timer put back where it is easiest to write -the page, through a
    // `useFetch` or an `onUnmounted` that "cleans up"-, and every case above
    // stays green under it, because none of them mounts anything: they drive
    // the store directly. The reader asks for a million rows, walks to the
    // dashboard while it runs and comes back to a screen that never learnt the
    // export finished, with a link that was minted and never offered.
    vi.useFakeTimers()
    const servidor = crearServidor({
      historial: [trabajo({ estado: 'en_proceso' })],
      guion: [trabajo({ estado: 'en_proceso' }), trabajo({ estado: 'en_proceso' }), completado()],
    })
    const wrapper = await montar(servidor)
    const exportaciones = useExportacionesStore()

    await vi.advanceTimersByTimeAsync(INTERVALO_SONDEO_MS)
    expect(servidor.llamadas.detalle).toBe(1)

    // Leaving the route is what unmounts the page. Nothing else of the
    // navigation reaches the store, which is the point being made.
    wrapper.unmount()
    montado = null

    await vi.advanceTimersByTimeAsync(INTERVALO_SONDEO_MS)
    expect(exportaciones.sondeando).toBe(true)
    expect(servidor.llamadas.detalle).toBe(2)

    await vi.advanceTimersByTimeAsync(INTERVALO_SONDEO_MS)

    expect(exportaciones.trabajos[0]?.estado).toBe('completado')
    expect(exportaciones.trabajos[0]?.url_descarga).toBe(URL_FIRMADA)
  })

  it('queda atenta a la pestana antes de que exista ningun trabajo', async () => {
    // This is the whole reason the plugin exists, and it is invisible until a
    // job is asked for from a tab that is already in the background: a reader
    // who launched the export and switched away before the request landed, or
    // a session restored in a tab nobody is looking at. `iniciarSondeo` returns
    // on a hidden document BEFORE it attaches the visibility listener, so with
    // nothing having attached it at boot the tab coming back to the front is
    // heard by nobody: the timer is never armed and the job is never asked
    // about again for as long as that tab lives.
    vi.useFakeTimers()
    const servidor = crearServidor()
    instalarEntorno(servidor)
    ocultarPestana(true)

    const exportaciones = await arrancarLaAplicacion()
    tienda = exportaciones

    await exportaciones.solicitar(SOLICITUD)
    await vi.advanceTimersByTimeAsync(INTERVALO_SONDEO_MS * 3)
    expect(servidor.llamadas.detalle).toBe(0)

    ocultarPestana(false)
    document.dispatchEvent(new Event('visibilitychange'))
    await vi.advanceTimersByTimeAsync(INTERVALO_SONDEO_MS)

    expect(servidor.llamadas.detalle).toBe(1)
  })

  it('no pone nada en el cable por el mero hecho de arrancar', async () => {
    // The defect is a `cargarHistorial()` added to the boot so that some badge
    // can count something. It would run on every visit of every reader on every
    // screen, including the role this endpoint answers 403 to, and it would
    // spend a request nobody asked for before the first paint. Reading the
    // history is the job of the screen that shows it.
    const servidor = crearServidor()
    instalarEntorno(servidor)

    tienda = await arrancarLaAplicacion()

    expect(servidor.llamadas).toEqual({ alta: 0, lista: 0, detalle: 0 })
    expect(tienda.sondeando).toBe(false)
  })
})

describe('la sesion que termina no deja rastro del lector anterior', () => {
  it('olvida los trabajos del lector anterior en vez de reinyectarlos como filas', async () => {
    // The defect, and it is a leak of data between people: the store belongs to
    // the application, not to the visit. `detalles` alone is enough to bring
    // the whole thing back, because `trabajos` appends every detail the history
    // does not carry -the branch that keeps a job requested a second ago on
    // screen-, so the next analyst to use this tab reads the dataset, the row
    // count, the size and the instants of an extraction that was never theirs.
    vi.useFakeTimers()
    const servidor = crearServidor()
    const exportaciones = abrirTienda(servidor)

    await exportaciones.solicitar(SOLICITUD)
    expect(exportaciones.trabajos.map(fila => fila.job_id)).toEqual(['a1'])
    expect(exportaciones.sondeando).toBe(true)

    exportaciones.olvidar()

    expect(exportaciones.trabajos).toEqual([])
    expect(exportaciones.trabajoDestacado).toBeNull()
    expect(exportaciones.fallo).toBeNull()
    expect(exportaciones.sondeando).toBe(false)

    // And the watch is really gone, not merely disarmed: a poll that resumed
    // would be asking the backend about a job with a cookie that no longer
    // exists, on behalf of a reader who left.
    const gastadas = servidor.llamadas.detalle
    await vi.advanceTimersByTimeAsync(INTERVALO_SONDEO_MS * 3)

    expect(servidor.llamadas.detalle - gastadas).toBe(0)
  })

  it('se vacia solo en cuanto el backend deja de reconocer la sesion', async () => {
    // The wiring, which is where the leak happens in real life: nobody calls
    // `olvidar` by hand. The session dies in the middle of the watch, the poll
    // receives the 401, the reader is sent to the entry screen -and the rows
    // stay behind in a store that survives the navigation and the next sign in.
    vi.useFakeTimers()
    const servidor = crearServidor({ fallosDeDetalle: 1, estadoDeDetalle: 401 })
    const exportaciones = abrirTienda(servidor)

    await exportaciones.solicitar(SOLICITUD)
    expect(exportaciones.trabajos).toHaveLength(1)

    await vi.advanceTimersByTimeAsync(INTERVALO_SONDEO_MS)

    const navegar = (globalThis as unknown as { navigateTo: ReturnType<typeof vi.fn> }).navigateTo

    expect(exportaciones.trabajos).toEqual([])
    expect(exportaciones.sondeando).toBe(false)
    expect(navegar).toHaveBeenCalled()
  })
})

describe('el intervalo del sondeo', () => {
  it('pregunta una sola vez cada tres segundos', async () => {
    // The defect: lowering the interval to half a second "so it moves". Nothing
    // visible would change -the bar is indeterminate- and every active reader
    // would multiply their traffic by six against an endpoint that reads a row
    // by primary key.
    vi.useFakeTimers()
    const servidor = crearServidor()
    const exportaciones = abrirTienda(servidor)

    await exportaciones.solicitar(SOLICITUD)

    await vi.advanceTimersByTimeAsync(INTERVALO_SONDEO_MS - 1)
    expect(servidor.llamadas.detalle).toBe(0)

    await vi.advanceTimersByTimeAsync(1)
    expect(servidor.llamadas.detalle).toBe(1)

    await vi.advanceTimersByTimeAsync(INTERVALO_SONDEO_MS * 2)
    expect(servidor.llamadas.detalle).toBe(3)
    // Three rounds, three reads of one row by primary key, and the history
    // untouched. A round that also re-read the list would double the traffic of
    // the screen to fetch a list that only changes when a job starts or ends.
    expect(servidor.llamadas.lista).toBe(0)
  })
})

describe('el enlace deja de ofrecerse cuando caduca', () => {
  it('retira la descarga en el instante exacto de la caducidad, sin recargar', async () => {
    // The defect: `caduca_en` compared against the instant of the render. A
    // link that runs out while the reader is looking at it keeps being offered
    // until something else redraws that card, and the click lands on the 410 of
    // the backend. The instant is not a guess -the signature encodes it- so one
    // shot armed for it is enough, and it costs no request.
    vi.useFakeTimers()
    vi.setSystemTime(new Date('2026-08-13T20:00:12+00:00'))
    const servidor = crearServidor({
      historial: [completado({ caduca_en: '2026-08-13T20:05:12+00:00' })],
    })
    const wrapper = await montar(servidor)

    expect(wrapper.get('[data-accion="descargar"]').attributes('href')).toBe(URL_FIRMADA)
    expect(wrapper.find('[data-aviso="caducado"]').exists()).toBe(false)

    await vi.advanceTimersByTimeAsync(5 * 60 * 1000)
    await flushPromises()

    expect(wrapper.find('[data-accion="descargar"]').exists()).toBe(false)
    expect(wrapper.get('[data-aviso="caducado"]').text()).toBe(mensaje('es', 'export.link.expired'))
    // Zero requests: the deadline travelled with the link, so learning that it
    // passed is not something the portal has to ask anyone about.
    expect(servidor.llamadas.detalle).toBe(0)
    expect(servidor.llamadas.lista).toBe(1)
  })

  it('no deja el disparo de caducidad vivo tras desmontar la pantalla', async () => {
    // The rule of this User Story is that no timer outlives its component. The
    // shot is armed per card, so the way it leaks is unmounting the screen with
    // a link still alive, which is what walking to another route does.
    vi.useFakeTimers()
    vi.setSystemTime(new Date('2026-08-13T20:00:12+00:00'))
    const wrapper = await montar(
      crearServidor({ historial: [completado({ caduca_en: '2026-08-13T20:05:12+00:00' })] }),
    )

    expect(vi.getTimerCount()).toBeGreaterThan(0)

    wrapper.unmount()
    montado = null

    expect(vi.getTimerCount()).toBe(0)
  })
})

describe('el historial se relee cuando un trabajo termina', () => {
  it('trae el trabajo que otra pestana pidio, sin recargar la pantalla', async () => {
    // The defect: the terminal state arrives through the poll and is merged
    // over the summary, so the job of THIS tab ends up right; an export the
    // same analyst asked for in another tab does not exist for this screen
    // until the page is reloaded by hand.
    vi.useFakeTimers()
    const historial: TrabajoResumen[] = []
    const servidor = crearServidor({
      historial,
      guion: [trabajo({ estado: 'en_proceso' }), completado()],
    })
    const exportaciones = abrirTienda(servidor)

    await exportaciones.cargarHistorial()
    await exportaciones.solicitar(SOLICITUD)
    // The other tab asks for its own export while this one waits.
    historial.push(
      trabajo({
        job_id: 'b2',
        dataset: 'liquidez',
        estado: 'fallido',
        error: 'columna_desconocida',
        solicitado_en: '2026-08-13T19:00:00+00:00',
        terminado_en: '2026-08-13T19:00:04+00:00',
      }),
    )

    await vi.advanceTimersByTimeAsync(INTERVALO_SONDEO_MS)
    expect(servidor.llamadas.lista).toBe(1)
    expect(exportaciones.trabajos.map(fila => fila.job_id)).toEqual(['a1'])

    await vi.advanceTimersByTimeAsync(INTERVALO_SONDEO_MS)

    expect(servidor.llamadas.lista).toBe(2)
    // No duplicate row and no reordering: the list is the one the server sent,
    // `created_at` descending, with the polled detail merged over it.
    expect(exportaciones.trabajos.map(fila => fila.job_id)).toEqual(['a1', 'b2'])

    const gastadas = servidor.llamadas.lista
    await vi.advanceTimersByTimeAsync(INTERVALO_SONDEO_MS * 5)
    // One reread per transition to a terminal state, and there was one.
    expect(servidor.llamadas.lista - gastadas).toBe(0)
  })

  it('no relee por un trabajo que ya conocia terminado', async () => {
    // A job the history already reported as finished has not transitioned to
    // anything. Asking for its signed link -which the summary never carries-
    // must not put the list back on the wire, or opening the screen with an old
    // export would pay for the history twice.
    const servidor = crearServidor({
      historial: [trabajo({ estado: 'completado', terminado_en: '2026-08-13T20:00:12+00:00' })],
      guion: [completado()],
    })
    const wrapper = await montar(servidor)

    expect(servidor.llamadas.detalle).toBe(1)
    expect(servidor.llamadas.lista).toBe(1)
    expect(wrapper.get('[data-accion="descargar"]').attributes('href')).toBe(URL_FIRMADA)
  })
})

describe('los tres momentos salen del estado real', () => {
  it('con historial vacio, momento=enlace declara el vacio y no ofrece enlace', async () => {
    // The defect this exists to stop: a query parameter that draws the third
    // moment out of nothing. The capture would show a signed link that no job
    // ever produced, and the evidence of A4 would be a mock-up presented as a
    // running system.
    const wrapper = await montar(crearServidor(), { momento: 'enlace' })

    expect(wrapper.get('[data-ruta]').attributes('data-momento')).toBe('enlace')
    expect(wrapper.find('[data-accion="descargar"]').exists()).toBe(false)
    expect(wrapper.find('[data-vacio="momento"]').exists()).toBe(true)
    expect(wrapper.get('[data-historial]').attributes('data-estado')).toBe('vacio')
  })

  it('con un trabajo terminado, momento=proceso no inventa uno en curso', async () => {
    const servidor = crearServidor({ historial: [completado()], guion: [completado()] })
    const wrapper = await montar(servidor, { momento: 'proceso' })

    expect(wrapper.get('[data-ruta]').attributes('data-momento')).toBe('proceso')
    expect(wrapper.find('[data-vacio="momento"]').exists()).toBe(true)
    expect(wrapper.find('[data-accion="descargar"]').exists()).toBe(false)
    // The job is still in the history: what the pin decides is which one is
    // expanded, never which ones exist.
    expect(wrapper.get('[data-trabajo="a1"]').attributes('data-expandido')).toBe('false')
  })

  it('con un trabajo terminado, momento=solicitud no presta el enlace del tercero', async () => {
    // The first moment is the only one with no job in it, and that is what
    // makes it easy to get wrong: expanding "the most recent job" is the
    // natural simplification, and it would put the signed link of the third
    // moment inside the capture of the first. The pin decides which real job
    // stays expanded, and in this moment the answer is none.
    const servidor = crearServidor({ historial: [completado()], guion: [completado()] })
    const wrapper = await montar(servidor, { momento: 'solicitud' })

    expect(wrapper.get('[data-ruta]').attributes('data-momento')).toBe('solicitud')
    expect(wrapper.get('[data-ruta]').attributes('data-fijado')).toBe('true')
    expect(wrapper.get('[data-etiqueta="momento"]').text()).toBe(
      mensaje('es', 'export.moment.request'),
    )
    expect(wrapper.find('[data-formulario="exportacion"]').exists()).toBe(true)
    expect(wrapper.find('[data-accion="descargar"]').exists()).toBe(false)
    expect(wrapper.get('[data-trabajo="a1"]').attributes('data-expandido')).toBe('false')
    // And this moment is NOT an empty state: the form is what it consists of,
    // so the sentence that declares a moment with nothing in it would be a
    // second and contradictory reading of a screen that has all it needs.
    expect(wrapper.find('[data-vacio="momento"]').exists()).toBe(false)
  })

  it('un momento que el portal no conoce no fija nada ni imprime su clave', async () => {
    // The defect is a query parameter taken at face value. `momentoVisible`
    // would hold a word the catalogue has no leaf for, the label would render
    // the dotted key at the reader -`export.moment.undefined`- and the screen
    // would be pinned to a moment that does not exist, which is worse than the
    // moment it was showing before anybody asked.
    const servidor = crearServidor({ historial: [completado()], guion: [completado()] })
    const wrapper = await montar(servidor, { momento: 'lunes' })

    expect(wrapper.get('[data-ruta]').attributes('data-fijado')).toBe('false')
    expect(wrapper.get('[data-ruta]').attributes('data-momento')).toBe('enlace')
    expect(wrapper.get('[data-etiqueta="momento"]').text()).toBe(
      mensaje('es', 'export.moment.link'),
    )
  })

  it('colapsar la tarjeta del trabajo en curso no declara vacio el momento', async () => {
    // The defect: the emptiness derived from the expanded row instead of from
    // the state. Closing a card is a reading gesture -one click, and the reader
    // does it to see the whole list- and it empties `trabajoDestacado`, so the
    // screen printed "there is no job at this moment" over a job that was
    // running, spinning, in the list right below the sentence.
    const servidor = crearServidor({
      historial: [trabajo({ estado: 'en_proceso' })],
      guion: [trabajo({ estado: 'en_proceso' })],
    })
    const wrapper = await montar(servidor, { momento: 'proceso' })

    expect(wrapper.get('[data-trabajo="a1"]').attributes('data-expandido')).toBe('true')
    expect(wrapper.find('[data-vacio="momento"]').exists()).toBe(false)

    await wrapper.get('[data-trabajo="a1"] [data-accion="alternar"]').trigger('click')
    await flushPromises()

    expect(wrapper.get('[data-trabajo="a1"]').attributes('data-expandido')).toBe('false')
    // The job did not move: it is in the history, in progress, and the moment
    // it belongs to is the one being rendered.
    expect(wrapper.get('[data-trabajo="a1"]').attributes('data-estado')).toBe('en_proceso')
    expect(wrapper.find('[data-vacio="momento"]').exists()).toBe(false)
  })

  it('sin fijar nada, el enlace del trabajo terminado se ofrece tal cual llego', async () => {
    const servidor = crearServidor({ historial: [completado()], guion: [completado()] })
    const wrapper = await montar(servidor)

    expect(wrapper.get('[data-ruta]').attributes('data-momento')).toBe('enlace')
    expect(wrapper.get('[data-trabajo="a1"]').attributes('data-expandido')).toBe('true')
    // Relative and untouched: the Nitro proxy forwards it with the session,
    // and a rewritten host would send the browser where no session exists.
    expect(wrapper.get('[data-accion="descargar"]').attributes('href')).toBe(URL_FIRMADA)
  })
})

describe('la franja de honestidad de la demostracion', () => {
  it('no aparece cuando el despliegue no estira nada', async () => {
    // Announcing a stretch that is not happening is the same class of lie the
    // band exists to prevent.
    const wrapper = await montar(crearServidor())

    expect(wrapper.find('[data-franja="demo"]').exists()).toBe(false)
  })

  it('aparece cuando el despliegue declara un retraso de demostracion', async () => {
    vi.stubGlobal('useRuntimeConfig', () => ({
      public: { entorno: 'prueba', exportDemoDelay: 8 },
    }))
    const wrapper = await montar(crearServidor())

    expect(wrapper.get('[data-franja="demo"]').text()).toContain('8')
  })

  it('declara exportDemoDelay en la mitad publica de runtimeConfig', () => {
    // The two cases above stub `useRuntimeConfig`, so they say what the screen
    // does with the value and nothing about whether the value can ever arrive.
    // Nuxt exposes only the keys declared in `runtimeConfig`, and `NUXT_PUBLIC_*`
    // overrides an existing key instead of creating one: without this line the
    // demonstration sets the variable, the interface reads `undefined`, the
    // band stays hidden, and the capture of A4 shows a job stretched by eight
    // seconds with nothing on screen declaring the stretch. That is the exact
    // lie the band was written to prevent.
    // Through a variable, and not with the path written into the call: Vite
    // rewrites a literal `new URL(..., import.meta.url)` into an asset URL at
    // transform time, and the result is no longer a file: URL to read.
    const relativa = '../nuxt.config.ts'
    const configuracion = readFileSync(fileURLToPath(new URL(relativa, import.meta.url)), 'utf8')
    const bloque = configuracion.match(/runtimeConfig:\s*\{([\s\S]*?)\n {2}\},/)?.[1] ?? ''
    const publico = bloque.match(/public:\s*\{([\s\S]*?)\}/)?.[1] ?? ''

    expect(publico).toMatch(/exportDemoDelay:/)
    expect(publico).toMatch(/NUXT_PUBLIC_EXPORT_DEMO_DELAY/)
  })

  it('lee el ajuste ausente como cero y nunca como verdadero', () => {
    expect(retrasoDeDemostracion({})).toBe(0)
    expect(retrasoDeDemostracion({ exportDemoDelay: '8' })).toBe(8)
    expect(retrasoDeDemostracion({ exportDemoDelay: 'si' })).toBe(0)
  })
})

describe('el historial que el registro no pudo servir', () => {
  it('nombra el registro caido y deja volver a pedirlo', async () => {
    // The 503 the backend translates its unreachable registry into exists so
    // that this screen has a designed emptiness instead of a stack trace, and
    // three defects would waste it: a code mapped to the generic sentence,
    // which tells the reader nothing and suggests nothing; a retry that emits
    // an event nobody handles, which leaves reloading the page as the only way
    // out; and a failure that leaves the phase in `cargando`, which is a
    // skeleton pulsing forever over a list that is never going to come.
    const servidor = crearServidor({ fallosDeLista: 1 })
    const wrapper = await montar(servidor)

    expect(wrapper.get('[data-historial]').attributes('data-estado')).toBe('error')
    expect(wrapper.get('[data-fallo]').text()).toBe(mensaje('es', 'export.error.unavailable'))

    await wrapper.get('[data-accion="reintentar"]').trigger('click')
    await flushPromises()

    expect(servidor.llamadas.lista).toBe(2)
    expect(wrapper.find('[data-fallo]').exists()).toBe(false)
    expect(wrapper.get('[data-historial]').attributes('data-estado')).toBe('vacio')
  })
})

describe('la franja de error describe el estado de ahora', () => {
  it('retira el error del sondeo en cuanto el trabajo vuelve a responder', async () => {
    // The defect: `fallo` written by every refused request and cleared by none
    // of the successful ones. A single blip in a watch that lasts minutes left
    // the red band on screen for the rest of the visit, next to the card of the
    // same job announcing that it finished and offering its link: two readings
    // of one job, and the loud one is the stale one.
    vi.useFakeTimers()
    const servidor = crearServidor({
      fallosDeDetalle: 1,
      guion: [trabajo({ estado: 'en_proceso' }), completado()],
    })
    const exportaciones = abrirTienda(servidor)

    await exportaciones.solicitar(SOLICITUD)
    await vi.advanceTimersByTimeAsync(INTERVALO_SONDEO_MS)
    expect(exportaciones.fallo).toEqual({ estado: 500, codigo: null })

    await vi.advanceTimersByTimeAsync(INTERVALO_SONDEO_MS)

    // The job is still running, so nothing else has been read from the wire:
    // the answer of the poll is the only thing that can have cleared the band,
    // which is exactly the path being pinned. Clearing it only when the history
    // is re-read would leave the band up for the whole extraction.
    expect(exportaciones.fallo).toBeNull()
    expect(exportaciones.trabajos[0]?.estado).toBe('en_proceso')
    expect(servidor.llamadas.lista).toBe(0)

    await vi.advanceTimersByTimeAsync(INTERVALO_SONDEO_MS)

    expect(exportaciones.fallo).toBeNull()
    expect(exportaciones.trabajos[0]?.estado).toBe('completado')
  })
})

describe('los dos cuerpos de error del contrato', () => {
  it('lee el codigo estable de un fallo propio de exportacion', () => {
    // `{"detail": {"codigo": ...}}` is the shape of the four export failures.
    expect(falloDeExportacion({ status: 410, data: { detail: { codigo: 'enlace_caducado' } } })).toEqual(
      { estado: 410, codigo: 'enlace_caducado' },
    )
  })

  it('no confunde el detalle suelto de una sesion caida con un codigo', () => {
    // US-015 answers `{"detail": "sesion_expirada"}`, a loose string. Reading it
    // as an object would print `[object Object]` at the reader, and reading the
    // export bodies as strings would lose every code.
    expect(falloDeExportacion({ status: 401, data: { detail: 'sesion_expirada' } })).toEqual({
      estado: 401,
      codigo: null,
    })
    expect(falloDeExportacion(new Error('sin red'))).toEqual({ estado: 0, codigo: null })
  })
})

describe('el campo de filtros', () => {
  it('lee los pares que el compilador de Polars entiende', () => {
    expect(analizarFiltros('divisa=MXN,USD; unidad=banca')).toEqual({
      divisa: ['MXN', 'USD'],
      unidad: 'banca',
    })
    expect(analizarFiltros('   ')).toEqual({})
  })

  it('rechaza lo que no es un par en vez de enviarlo', () => {
    // A text the endpoint would answer 422 to is refused where the reader can
    // fix it, and a pair with no column would silently filter by nothing.
    expect(analizarFiltros('divisa')).toBeNull()
    expect(analizarFiltros('=MXN')).toBeNull()
    expect(analizarFiltros('divisa=')).toBeNull()
  })
})

describe('los dos formatos del contrato se ofrecen', () => {
  it('deja pedir XLSX y manda a la API el formato que el lector eligio', async () => {
    // The defect: the XLSX radio left disabled from the days when the backend
    // shipped no spreadsheet writer. `polars[xlsxwriter]` is installed now and
    // the writer holds a measured cap of 200,000 rows, so a disabled option
    // refuses an extraction the API completes -and refuses it in the one place
    // that cannot know how tall the dataset is-. The check is double on
    // purpose: the attribute, and the request that reaches the wire, because a
    // disabled control also swallows the change event that moves the model.
    const servidor = crearServidor()
    const wrapper = await montar(servidor)

    const opcion = wrapper.get('[data-formato="xlsx"] input')
    expect(opcion.attributes('disabled')).toBeUndefined()

    await opcion.setValue()
    await wrapper.get('[data-formulario="exportacion"]').trigger('submit')
    await flushPromises()

    expect(servidor.solicitados).toEqual([{ dataset: 'creditos', formato: 'xlsx', filtros: {} }])
  })

  it('explica el fallo de formato por el tope de filas que lo provoca', () => {
    // `formato_no_disponible` now has two causes: the writer missing, which is
    // a matter of the deployment, and the 200,000 row cap, which is the one an
    // analyst can hit from the form. A sentence that only said "not available
    // in this prototype" described a portal that no longer exists and left the
    // reader with no move; the cap and CSV are the move.
    for (const idioma of ['es', 'en'] as const) {
      expect(mensaje(idioma, 'export.job.error.formatUnavailable')).toMatch(/200[\s,.]?000/)
      expect(mensaje(idioma, 'export.format.xlsxRowLimit')).toMatch(/200[\s,.]?000/)
    }
  })
})

describe('ninguna cadena visible se escribe en un componente', () => {
  const ARCHIVOS = [
    '../app/components/exportacion/FormularioExportacion.vue',
    '../app/components/exportacion/TarjetaTrabajo.vue',
    '../app/components/exportacion/HistorialExportaciones.vue',
    '../app/pages/exploracion/exportar.vue',
  ]

  /** Body of the single `<template>` block of a component. */
  function plantilla(fuente: string): string {
    const inicio = fuente.indexOf('<template>')
    const fin = fuente.lastIndexOf('</template>')
    return fuente.slice(inicio + '<template>'.length, fin)
  }

  /**
   * Text nodes of a template once every interpolation is taken out.
   *
   * What is left has to be punctuation or nothing: a letter there is a sentence
   * that never reached the catalogues.
   */
  function sueltos(cuerpo: string): string[] {
    // Attribute values are emptied before the text nodes are read: a binding
    // like `v-if="retraso > 0"` carries a `>` that would otherwise be taken for
    // the end of a tag, and the scan would report the markup as visible prose.
    const sinComentarios = cuerpo
      .replace(/<!--[\s\S]*?-->/g, '')
      .replace(/="[^"]*"/g, '=""')
      .replace(/='[^']*'/g, '=\'\'')
    const restos: string[] = []

    for (const [, entre] of sinComentarios.matchAll(/>([^<]*)</g)) {
      const resto = entre.replace(/\{\{[\s\S]*?\}\}/g, '').trim()
      if (/\p{L}/u.test(resto)) {
        restos.push(resto)
      }
    }

    return restos
  }

  it('resuelve por catalogo todo texto y todo atributo que el lector oye', () => {
    const hallazgos: string[] = []
    let interpolaciones = 0

    for (const relativa of ARCHIVOS) {
      const fuente = readFileSync(fileURLToPath(new URL(relativa, import.meta.url)), 'utf8')
      const cuerpo = plantilla(fuente)
      interpolaciones += [...cuerpo.matchAll(/\{\{[\s\S]*?\}\}/g)].length

      for (const resto of sueltos(cuerpo)) {
        hallazgos.push(`${relativa}: ${resto}`)
      }
      // An unbound `aria-label`, `title`, `placeholder` or `alt` is a literal
      // too, and it is the one a reader with a screen reader hears.
      for (const [, atributo] of cuerpo.matchAll(/\s(aria-label|title|placeholder|alt)="/g)) {
        hallazgos.push(`${relativa}: ${atributo}`)
      }
    }

    expect(hallazgos).toEqual([])
    // Floor, so an empty scan cannot pass as a clean one.
    expect(interpolaciones).toBeGreaterThan(20)
  })
})
