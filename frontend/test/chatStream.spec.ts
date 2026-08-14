import type { VueWrapper } from '@vue/test-utils'
import type { ControlDeChat } from '~/composables/useChatStream'
import type { EventoToolCall, ItemHilo } from '~/types/chat'

import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'

import { flushPromises, mount } from '@vue/test-utils'
import { defineComponent, h, nextTick } from 'vue'
import { afterEach, describe, expect, it, vi } from 'vitest'

import HistorialConversacion from '~/components/chat/HistorialConversacion.vue'
import {
  analizarTramos,
  CLAVE_FALLO_DE_TRANSPORTE,
  RUTA_CHAT,
  useChatStream,
} from '~/composables/useChatStream'
import { usePermisos } from '~/composables/usePermisos'
import {
  CLAVE_AVISO_DEMO,
  CLAVE_ESTADO_CHAT,
  CLAVE_PASO,
  CLAVE_PERMISO_CON_NIVEL,
  CLAVE_PERMISO_GENERICA,
  PROVEEDOR_DE_CHAT,
} from '~/types/chat'
import { RUTA_ACCESO } from '~/utils/navegacion'
import { MOTIVO_EXPIRADA } from '~/utils/sesion'
import {
  desmontarPaginas,
  FALLO_DE_PERMISO,
  FALLO_RECUPERABLE,
  marco,
  montarPagina,
  preguntar,
  servidorSSE,
  tarjetaAnunciada,
} from './dobles/chat'
import { clavesDe, crearI18nDePrueba, mensaje } from './i18nDePrueba'

/**
 * US-023 — the transport of the assistant and its cancellation.
 *
 * Only the network is doubled, and it is doubled as a stream and not as a
 * value: the fake server hands over one chunk at a time and keeps the read in
 * flight until it is fed or aborted, which is the only way "the button stops
 * the server" can be measured without a socket. The composable, the reducer
 * and the page run for real, because that is where the defects of this User
 * Story live.
 *
 * What is deliberately not measured: the look of the tool call card and of the
 * error notice. Both are provisional markup that US-028 and US-024 rewrite the
 * same day, and pinning them would buy coverage that gets deleted on Monday.
 *
 * That server, the framing helper, the two typed failures and the page harness
 * are shared with the other chat suites in `dobles/chat.ts`. What stays here is
 * what only this suite uses: the refusals, the switchboard and the readings of
 * the thread.
 */

/**
 * Resolves a path of the repository.
 *
 * The path arrives as a variable on purpose: with a literal, Vite rewrites the
 * `new URL(..., import.meta.url)` pattern into an asset reference and the URL
 * stops being a file one.
 */
function rutaDelRepositorio(relativa: string): string {
  return fileURLToPath(new URL(relativa, import.meta.url))
}

const ANUNCIO: EventoToolCall = tarjetaAnunciada('c1')

const RESUELTA: EventoToolCall = {
  ...ANUNCIO,
  estado: 'resultado',
  transcurrido_ms: 260,
  resultado: {
    columnas: ['chat.toolCall.column.metric', 'chat.toolCall.column.value'],
    filas: [['morosidad', '3.42 %']],
    cifra: '3.42 %',
  },
  fuente: 'catalogo.creditos.morosidad_cartera',
}

const SEGUNDA_TARJETA: EventoToolCall = tarjetaAnunciada('c2', 'agregar_serie')

/** A request the endpoint refuses before any stream is opened. */
function servidorQueRechaza(estadoHttp: number) {
  return vi.fn(() => Promise.resolve({ ok: false, status: estadoHttp, body: null }))
}

/**
 * A refusal that arrives with a body, which is what the endpoint really sends.
 *
 * FastAPI answers a 422, a 429 or a 500 with a JSON payload, so the response of
 * a refused request carries a `ReadableStream` that nobody here is going to
 * read. The double exposes whether it was released and whether the turn was
 * aborted, because neither is visible from the screen.
 */
function servidorQueRechazaConCuerpo(estadoHttp: number) {
  let liberaciones = 0
  let senal: AbortSignal | null = null

  const fetchFalso = vi.fn((_ruta: string, opciones: RequestInit) => {
    senal = opciones.signal ?? null
    return Promise.resolve({
      ok: false,
      status: estadoHttp,
      body: {
        cancel: async (): Promise<void> => {
          liberaciones += 1
        },
      },
    })
  })

  return { fetchFalso, liberaciones: () => liberaciones, senal: () => senal }
}

/**
 * A request that stays in flight until the test decides how it ends.
 *
 * The slowest part of a turn is the wait for the headers, so it is also the
 * likeliest moment for the reader to give up and ask again. A double that
 * resolved on its own could not put the two turns in that order.
 */
function servidorQueTarda() {
  let responder: ((respuesta: unknown) => void) | null = null
  let senal: AbortSignal | null = null

  const fetchFalso = vi.fn((_ruta: string, opciones: RequestInit) => {
    senal = opciones.signal ?? null
    return new Promise<unknown>((resolver) => {
      responder = resolver
    })
  })

  return {
    fetchFalso,
    /** Answers the request that was in flight with a refusal. */
    rechazarCon: (estadoHttp: number) => {
      responder?.({ ok: false, status: estadoHttp, body: null })
    },
    senal: () => senal,
  }
}

/** Anything that can answer one request, whatever it answers with. */
interface Conexion {
  fetchFalso: (ruta: string, opciones: RequestInit) => Promise<unknown>
}

/**
 * Hands a different connection to each request, so two turns can overlap.
 *
 * A single double would answer the second question with the body of the first,
 * and the whole point of these cases is what each turn does to the other one.
 */
function centralita(...conexiones: Conexion[]) {
  let atendidas = 0

  return vi.fn((ruta: string, opciones: RequestInit) => {
    const conexion = conexiones[atendidas]
    atendidas += 1
    if (conexion === undefined) {
      throw new Error(`la peticion ${atendidas} no tiene conexion preparada`)
    }
    return conexion.fetchFalso(ruta, opciones)
  })
}

/**
 * The composable inside a component, which is the only place it has a scope.
 *
 * Called from the top of a spec there is no scope to dispose, and disposal is
 * half of what these cases measure.
 */
function montarComposable(): { control: ControlDeChat, anfitrion: VueWrapper } {
  const capturado: { control?: ControlDeChat } = {}
  const anfitrion = mount(
    defineComponent({
      setup() {
        capturado.control = useChatStream()
        return () => h('div')
      },
    }),
  )

  const control = capturado.control
  if (control === undefined) {
    throw new Error('el componente anfitrion no llamo al composable')
  }
  return { control, anfitrion }
}

/**
 * The same composable wired to the real thread, which is what owns a clock.
 *
 * `montarPagina` drives this suite everywhere else and it is deliberately not
 * used by the case below, for one reason: `asistente.vue` destructures four of
 * the five refs and leaves `tarjetas` inside the composable, and the map is
 * half of what the defect emptied. This host composes what the page composes
 * -one `useChatStream`, one `HistorialConversacion` fed by its thread- so the
 * 250 ms interval of the thread and the `onScopeDispose` of the composable are
 * both live while the clock is advanced.
 */
function montarConversacion(): { control: ControlDeChat, anfitrion: VueWrapper } {
  const capturado: { control?: ControlDeChat } = {}
  const anfitrion = mount(
    defineComponent({
      setup() {
        const control = useChatStream()
        capturado.control = control
        return () =>
          h(HistorialConversacion, {
            hilo: control.hilo.value,
            motivoCierre: control.motivoCierre.value,
          })
      },
    }),
    { global: { plugins: [crearI18nDePrueba('es')], stubs: { Icon: true } } },
  )

  const control = capturado.control
  if (control === undefined) {
    throw new Error('el componente anfitrion no llamo al composable')
  }
  return { control, anfitrion }
}

/** The answer as the reader sees it: every text block of the thread, joined. */
function textoDelHilo(hilo: readonly ItemHilo[]): string {
  return hilo
    .filter((item): item is Extract<ItemHilo, { tipo: 'texto' }> => item.tipo === 'texto')
    .map(item => item.texto)
    .join('')
}

afterEach(() => {
  desmontarPaginas()
  vi.unstubAllGlobals()
  // A case that installs fake timers and dies on an assertion would hand them
  // to the next file, where the first `await` on a timer hangs until the run
  // times out. It is a no-op when no case faked anything.
  vi.useRealTimers()
})

describe('el parser de framing SSE', () => {
  it('reconstruye un marco partido a la mitad y conserva el resto pendiente', () => {
    // The defect this catches: parsing each chunk with `split('\n\n')` and
    // throwing away the tail. An event cut by the network is then lost in
    // silence -almost never on localhost, routinely behind a proxy- and the
    // answer arrives with a hole nobody can see.
    const completo
      = marco('tool_call', ANUNCIO)
        + marco('tool_call', RESUELTA)
        + marco('token', { texto: 'La morosidad ', indice: 0 })

    const corte = completo.length - 12
    const primera = analizarTramos(completo.slice(0, corte))

    expect(primera.eventos).toHaveLength(2)
    expect(primera.resto).toBe(completo.slice(completo.indexOf('event: token'), corte))

    const segunda = analizarTramos(primera.resto + completo.slice(corte))

    expect(segunda.resto).toBe('')
    expect(segunda.eventos).toHaveLength(1)
    expect(segunda.eventos[0]).toEqual({
      nombre: 'token',
      datos: { texto: 'La morosidad ', indice: 0 },
    })
  })

  it('descarta el marco cuyo nombre no es uno de los cuatro del contrato', () => {
    // The defect this catches: letting an undeclared name through. The reducer
    // switches on four names, so a fifth one would travel to the interface as
    // an item nothing knows how to draw.
    const { eventos, resto } = analizarTramos(
      marco('heartbeat', { latido: 1 }) + marco('done', { motivo: 'completado', tokens_emitidos: 3, duracion_ms: 90 }),
    )

    expect(resto).toBe('')
    expect(eventos.map(evento => evento.nombre)).toEqual(['done'])
  })

  it('descarta el marco cuyo cuerpo no es JSON y aplica el que viene detras', () => {
    // The defect this catches: parsing the body without a guard. One malformed
    // frame throws inside the read loop, so the `done` that travelled in the
    // same chunk is never applied: the turn ends on the wire and the screen
    // stays generating forever, with the Stop button as its only way out.
    const roto = `event: token
data: {"texto": roto

`
    const { eventos, resto } = analizarTramos(
      roto + marco('done', { motivo: 'completado', tokens_emitidos: 1, duracion_ms: 90 }),
    )

    expect(resto).toBe('')
    expect(eventos.map(evento => evento.nombre)).toEqual(['done'])
  })
})

describe('la cancelacion llega al servidor', () => {
  it('aborta la peticion y cancela el lector, no solo el estado local', async () => {
    // The defect this catches: a Stop that only flips a local flag. The screen
    // looks stopped, the backend keeps generating -and, with a paid model
    // behind it, keeps paying- and no assertion on the visible state would
    // ever notice.
    const servidor = servidorSSE()
    vi.stubGlobal('fetch', servidor.fetchFalso)

    const { estado, hilo, motivoCierre, enviar, detener } = useChatStream()
    const turno = enviar('como va la morosidad')
    await flushPromises()

    servidor.entregar(marco('token', { texto: 'La morosidad ', indice: 0 }))
    await flushPromises()

    expect(servidor.fetchFalso).toHaveBeenCalledWith(
      RUTA_CHAT,
      expect.objectContaining({ method: 'POST' }),
    )
    expect(estado.value).toBe('generando')
    expect(servidor.senal()?.aborted).toBe(false)

    detener()

    expect(servidor.senal()?.aborted).toBe(true)
    expect(servidor.cancelaciones()).toBe(1)

    await turno

    expect(estado.value).toBe('cancelado')
    expect(motivoCierre.value).toBe('cancelado')
    // What had already arrived stays on screen: a cancellation is not an undo.
    expect(hilo.value).toHaveLength(1)
  })

  it('aborta la peticion cuando muere el scope que abrio el stream', async () => {
    // The defect this catches: a composable whose only exit is the Detener
    // button. Navigating away calls nothing, so the reader who asks and walks
    // to the dashboard leaves the request open against a model that keeps
    // generating -and keeps charging- with nobody reading it, which is the
    // spend this User Story exists to stop. Nothing on screen would tell:
    // the component that would have shown it is already gone.
    const servidor = servidorSSE()
    vi.stubGlobal('fetch', servidor.fetchFalso)

    // The composable is called from inside a component and not at the top of
    // the test on purpose: what is being measured is the disposal of its
    // scope, and outside one there is no scope to dispose.
    const { control, anfitrion } = montarComposable()

    const turno = control.enviar('como va la morosidad')
    await flushPromises()

    servidor.entregar(marco('token', { texto: 'La morosidad ', indice: 0 }))
    await flushPromises()

    expect(servidor.senal()?.aborted).toBe(false)

    anfitrion.unmount()

    expect(servidor.senal()?.aborted).toBe(true)
    expect(servidor.cancelaciones()).toBe(1)

    await turno

    expect(control.estado.value).toBe('cancelado')
  })
})

/** Cadence of the shared clock of `HistorialConversacion`, in milliseconds. */
const PULSO_DEL_RELOJ_MS = 250

/**
 * How long the thread is left alone after the cut.
 *
 * The defect was seen between three and nine seconds after Detener; fifteen is
 * that window with room on both sides, and it is fifty ticks of the clock the
 * thread runs.
 */
const ESPERA_TRAS_EL_CORTE_MS = 15_000

/**
 * Advances the fake clock in ticks, flushing what each one queued.
 *
 * One jump of fifteen seconds fires every pending timer back to back with no
 * render in between, and a callback that scheduled another one would be
 * collapsed into the same instant. Stepping at the cadence of the clock the
 * component actually runs makes the run look like the run in the browser.
 *
 * @param ms - Milliseconds of fake time to let pass.
 */
async function avanzar(ms: number): Promise<void> {
  for (let transcurrido = 0; transcurrido < ms; transcurrido += PULSO_DEL_RELOJ_MS) {
    vi.advanceTimersByTime(PULSO_DEL_RELOJ_MS)
    // The microtask queue is drained separately: `advanceTimersByTime` runs the
    // callbacks, and anything they awaited resolves only after this.
    await flushPromises()
  }
}

/** Everything the cancelled turn left behind, as content and not as counts. */
function retratoDe(control: ControlDeChat, anfitrion: VueWrapper) {
  return {
    estado: control.estado.value,
    motivoCierre: control.motivoCierre.value,
    hilo: JSON.parse(JSON.stringify(control.hilo.value)) as unknown,
    tarjetas: JSON.parse(JSON.stringify([...control.tarjetas.value])) as unknown,
    items: anfitrion.findAll('[data-item]').map(nodo => nodo.attributes('data-item')),
    // The rendered text carries the stopwatch of every card, so a clock that
    // kept ticking after the cut shows up here and not only in a screenshot.
    texto: anfitrion.text(),
  }
}

describe('el hilo cancelado sobrevive al paso del tiempo', () => {
  it('sigue igual quince segundos despues de Detener, con el reloj corriendo', async () => {
    // The defect this catches was seen twice in a real browser on the build
    // before the corrections, with a real clock: between three and nine seconds
    // after pressing Detener the thread emptied itself, the screen went back to
    // its empty state, and the cancellation notice disappeared along with the
    // partial answer and its cards. No console error and no page reload.
    //
    // THE ROOT CAUSE IS NOT IDENTIFIED. It does not reproduce on the corrected
    // build and it did not reproduce again in a clean session, so this case is
    // a net and not the proof of a fix: whoever reads it in six months should
    // know that it was written without a culprit, and that going red here means
    // the culprit has been found rather than reintroduced.
    //
    // The gap it closes is structural and it is why nothing caught it. Every
    // other case of this suite asserts on the state of the instant right after
    // the cut and ends there; the clock is faked and nobody advances it. Any
    // delayed write -a `setTimeout` that resets, a debounce that fires late, an
    // interval that outlives its watch- lands in the seconds after the last
    // assertion of every existing case.
    //
    // Comparison is by content and not by length, the way F-1 of
    // `chatError.spec.ts` does it: a handler that replaced the thread with two
    // empty placeholders would keep the count.
    vi.useFakeTimers()

    const servidor = servidorSSE()
    vi.stubGlobal('fetch', servidor.fetchFalso)

    const { control, anfitrion } = montarConversacion()
    const turno = control.enviar('como va la morosidad')
    await flushPromises()

    servidor.entregar(
      marco('tool_call', ANUNCIO)
      + marco('tool_call', RESUELTA)
      + marco('token', { texto: 'La morosidad ', indice: 0 })
      + marco('tool_call', SEGUNDA_TARJETA),
    )
    await flushPromises()
    await nextTick()

    // The fixture has to be worth comparing: a resolved card, a fragment of the
    // answer and a second card still in flight. Two empty states compared
    // against each other is an assertion that cannot fail.
    expect(control.hilo.value).toHaveLength(3)
    expect([...control.tarjetas.value.keys()]).toEqual(['c1', 'c2'])
    expect(textoDelHilo(control.hilo.value)).toBe('La morosidad ')

    // And the clock the delayed write would have ridden on has to be running
    // before the cut, or advancing time afterwards would prove nothing.
    const cronometrosAntes = anfitrion.findAll('[data-prueba="transcurrido"]').map(n => n.text())
    await avanzar(1000)

    expect(anfitrion.findAll('[data-prueba="transcurrido"]').map(n => n.text()))
      .not.toEqual(cronometrosAntes)

    control.detener()
    await flushPromises()
    await turno
    await nextTick()

    const antes = retratoDe(control, anfitrion)

    expect(antes.estado).toBe('cancelado')
    expect(antes.motivoCierre).toBe('cancelado')
    expect(antes.items).toEqual(['tarjeta', 'texto', 'tarjeta'])

    await avanzar(ESPERA_TRAS_EL_CORTE_MS)

    const despues = retratoDe(control, anfitrion)

    // Named one by one before the whole portrait, so a failure says which half
    // of the screen went away instead of printing two objects side by side.
    expect(despues.hilo).toEqual(antes.hilo)
    expect(despues.tarjetas).toEqual(antes.tarjetas)
    expect(despues.motivoCierre).toBe('cancelado')
    expect(despues.estado).toBe('cancelado')
    expect(despues).toEqual(antes)

    anfitrion.unmount()
  })
})

describe('la identidad del turno', () => {
  it('el turno cancelado no se lleva por delante la cancelacion del siguiente', async () => {
    // The defect this catches: `controlador` as state of the composable and not
    // of the turn. The abort rejects the read that was in flight, and the
    // `catch` and the `finally` of the OLD turn run one microtask later -after
    // a Reintentar has already opened the new one-. The old turn then writes
    // `cancelado` over a stream that is generating and nulls the reference of
    // somebody else's controller, so `detener()` returns on its first line and
    // the button is not even rendered: an answer nobody can stop, against a
    // model that keeps charging. `detener(); await nextTick(); enviar(...)` is
    // exactly the shape of the Reintentar of US-024, and a microtask is not
    // enough for the old turn to have finished unwinding.
    const primera = servidorSSE()
    const segunda = servidorSSE()
    vi.stubGlobal('fetch', centralita(primera, segunda))

    const { control, anfitrion } = montarComposable()

    const viejo = control.enviar('como va la morosidad')
    await flushPromises()
    primera.entregar(marco('token', { texto: 'PRIMERA respuesta ', indice: 0 }))
    await flushPromises()

    control.detener()
    await nextTick()

    const nuevo = control.enviar('y la liquidez')
    await flushPromises()
    await viejo

    expect(control.estado.value).toBe('generando')
    expect(control.motivoCierre.value).toBeNull()

    segunda.entregar(marco('token', { texto: 'La liquidez ', indice: 0 }))
    await flushPromises()

    expect(textoDelHilo(control.hilo.value)).toBe('La liquidez ')

    // The whole point: the second turn is still stoppable, both by the button
    // and by leaving the screen.
    control.detener()

    expect(segunda.senal()?.aborted).toBe(true)
    expect(segunda.cancelaciones()).toBe(1)
    expect(control.estado.value).toBe('cancelado')

    await nuevo
    anfitrion.unmount()
  })

  it('la respuesta de un turno cancelado no pinta su fallo sobre la pregunta siguiente', async () => {
    // The defect this catches: the third write that happens after an `await`,
    // the one nobody looks at because it is a `return` away from the `fetch`.
    // Waiting for the headers is the slowest part of a turn, so it is also when
    // the reader gives up and asks again -and when the abandoned request comes
    // back as a 503 it publishes its failure over a stream that is generating:
    // the new question turns red before its first token, with a code that
    // belongs to a request nobody is waiting for.
    const lenta = servidorQueTarda()
    const segunda = servidorSSE()
    vi.stubGlobal('fetch', centralita(lenta, segunda))

    const { control, anfitrion } = montarComposable()

    const viejo = control.enviar('como va la morosidad')
    await flushPromises()

    control.detener()
    await nextTick()

    const nuevo = control.enviar('y la liquidez')
    await flushPromises()

    // The refusal of the abandoned request lands with the new turn already open.
    lenta.rechazarCon(503)
    await flushPromises()
    await viejo

    expect(control.estado.value).toBe('generando')
    expect(control.ultimoError.value).toBeNull()

    segunda.entregar(marco('token', { texto: 'La liquidez ', indice: 0 }))
    await flushPromises()

    expect(textoDelHilo(control.hilo.value)).toBe('La liquidez ')

    control.detener()
    await nuevo
    anfitrion.unmount()
  })

  it('el turno anterior no escribe en el hilo de la pregunta siguiente', async () => {
    // The defect this catches: a reader with no identity either. `done` closes
    // the turn on screen, but the body is not over -the server writes the frame
    // and then closes the socket-, so the read of the previous turn is still in
    // flight when the reader asks again. Without an identity that loop applies
    // what it receives to a thread that now belongs to another question, and
    // its body is never released: a sentence of the previous answer appears in
    // the middle of the new one, which is worse than losing it.
    const primera = servidorSSE()
    const segunda = servidorSSE()
    vi.stubGlobal('fetch', centralita(primera, segunda))

    const { control, anfitrion } = montarComposable()

    const viejo = control.enviar('como va la morosidad')
    await flushPromises()
    primera.entregar(
      marco('token', { texto: 'La morosidad ', indice: 0 })
      + marco('done', { motivo: 'completado', tokens_emitidos: 1, duracion_ms: 90 }),
    )
    await flushPromises()

    expect(control.estado.value).toBe('inactivo')

    const nuevo = control.enviar('y la liquidez')
    await flushPromises()
    segunda.entregar(marco('token', { texto: 'La liquidez ', indice: 0 }))

    // The tail of the previous body, arriving after the new question opened.
    primera.entregar(marco('token', { texto: 'cola del turno anterior', indice: 1 }))
    await flushPromises()

    expect(textoDelHilo(control.hilo.value)).toBe('La liquidez ')
    // And the body of the retired turn is released instead of left open.
    expect(primera.cancelaciones()).toBe(1)

    await viejo
    control.detener()
    await nuevo
    anfitrion.unmount()
  })
})

describe('el reductor del hilo', () => {
  it('sustituye solo el objeto de la tarjeta que cambia', async () => {
    // The defect this catches: rebuilding the whole thread on every event. The
    // interface would repaint two live cards on each frame, and the identity
    // US-028 renders by -its CA-5- would stop being a signal of anything.
    const servidor = servidorSSE()
    vi.stubGlobal('fetch', servidor.fetchFalso)

    const { hilo, tarjetas, enviar } = useChatStream()
    const turno = enviar('como va la liquidez')
    await flushPromises()

    servidor.entregar(marco('tool_call', ANUNCIO) + marco('tool_call', SEGUNDA_TARJETA))
    await flushPromises()

    const anunciada = tarjetas.value.get('c1')
    const intacta = tarjetas.value.get('c2')
    const itemIntacto = hilo.value[1]

    servidor.entregar(marco('tool_call', RESUELTA))
    await flushPromises()

    expect(tarjetas.value.get('c2')).toBe(intacta)
    expect(hilo.value[1]).toBe(itemIntacto)
    expect(tarjetas.value.get('c1')).not.toBe(anunciada)
    expect(tarjetas.value.get('c1')?.estado).toBe('resultado')
    // The announcement instant survives the states of its own card, which is
    // what lets the interface time a card that never resolves.
    expect(tarjetas.value.get('c1')?.iniciadaEnMs).toBe(anunciada?.iniciadaEnMs)

    servidor.entregar(marco('token', { texto: 'El coeficiente ', indice: 0 }))
    servidor.entregar(marco('done', { motivo: 'completado', tokens_emitidos: 1, duracion_ms: 120 }))
    servidor.cerrar()
    await turno

    // Arrival order, which is what makes "the card comes before the figure it
    // justifies" measurable at all.
    expect(hilo.value.map(item => item.tipo)).toEqual(['tarjeta', 'tarjeta', 'texto'])
  })
})

describe('el turno que falla', () => {
  it('publica el error tipado y cierra el turno como fallido', async () => {
    // The defect this catches: a reducer that drops the `error` event, or a
    // `done` whose motive is not translated. The turn that broke would end
    // looking like one that answered -Enviar back, nothing to show- because
    // `completado` maps to `inactivo`, and US-028 derives `interrumpida` from
    // this very field. C4 is the only permission material US-024 has, so what
    // is asserted are its five frozen fields and not a shape.
    const servidor = servidorSSE()
    vi.stubGlobal('fetch', servidor.fetchFalso)

    const { estado, motivoCierre, ultimoError, enviar } = useChatStream()
    const turno = enviar('exposicion agregada por contraparte')
    await flushPromises()

    servidor.entregar(
      marco('error', FALLO_DE_PERMISO)
      + marco('done', { motivo: 'error', tokens_emitidos: 0, duracion_ms: 40 }),
    )
    servidor.cerrar()
    await turno

    expect(ultimoError.value).toEqual(FALLO_DE_PERMISO)
    expect(motivoCierre.value).toBe('error')
    expect(estado.value).toBe('fallido')
  })

  it('no deja la pantalla generando cuando el cuerpo termina sin done', async () => {
    // The defect this catches: falling out of the read loop without saying
    // anything. A connection that drops mid answer -the ordinary failure of a
    // stream that stays open for minutes- would leave the screen generating
    // forever: the input disabled, Detener over a request nobody is serving
    // and no way to ask again. What had already arrived stays on screen, which
    // is what tells this apart from a failure that wipes the turn.
    const servidor = servidorSSE()
    vi.stubGlobal('fetch', servidor.fetchFalso)

    const { estado, hilo, ultimoError, enviar } = useChatStream()
    const turno = enviar('como va la morosidad')
    await flushPromises()

    servidor.entregar(marco('token', { texto: 'La morosidad ', indice: 0 }))
    servidor.cerrar()
    await turno

    expect(estado.value).toBe('fallido')
    expect(ultimoError.value?.codigo).toBe('stream_interrumpido')
    expect(hilo.value).toHaveLength(1)
  })

  it('conserva el diagnostico del servidor cuando el cuerpo se corta detras', async () => {
    // The defect this catches: closing a dropped body with a generic transport
    // failure on top of a diagnosis that already arrived. The server said which
    // silo did not answer and at which step, the socket died a frame later, and
    // the screen ends up saying "the transport failed" -so US-024 draws its
    // notice over a code the client invented and the reader is told to retry
    // something that was already told to it in better words.
    const servidor = servidorSSE()
    vi.stubGlobal('fetch', servidor.fetchFalso)

    const { estado, motivoCierre, ultimoError, enviar } = useChatStream()
    const turno = enviar('exposicion agregada por contraparte')
    await flushPromises()

    servidor.entregar(marco('error', FALLO_RECUPERABLE))
    servidor.cerrar()
    await turno

    expect(ultimoError.value).toEqual(FALLO_RECUPERABLE)
    // The turn still ends: preserving the diagnosis is not leaving the screen
    // generating forever, which is the other half of this branch.
    expect(estado.value).toBe('fallido')
    expect(motivoCierre.value).toBe('error')
  })

  it('convierte una red que no responde en un fallo recuperable de transporte', async () => {
    // The defect this catches: mislabelling the most likely failure of the
    // demonstration -backend down, proxy down, wifi gone-. Minted as `permiso`
    // it would offer no Reintentar over the one failure retrying does fix;
    // dropped, the rejection of `fetch` would escape `enviar` as an unhandled
    // promise and the screen would stay generating with no notice at all.
    vi.stubGlobal('fetch', vi.fn(() => Promise.reject(new TypeError('Failed to fetch'))))

    const { estado, motivoCierre, ultimoError, enviar } = useChatStream()
    await enviar('como va la morosidad')

    expect(ultimoError.value).toEqual({
      paso: 'transporte',
      clase: 'recuperable',
      codigo: 'red_inalcanzable',
      mensaje_clave: CLAVE_FALLO_DE_TRANSPORTE,
      recuperable: true,
    })
    expect(estado.value).toBe('fallido')
    expect(motivoCierre.value).toBe('error')
  })

  it('libera el cuerpo de una peticion rechazada y aborta su turno', async () => {
    // The defect this catches: returning from the refusal without touching the
    // response. A 422, a 429 or a 500 answers with a JSON body, and the branch
    // that publishes the failure never calls `getReader()`, so nobody releases
    // that stream and nobody aborts the controller of the turn: one leaked body
    // per refused request, which is exactly what a burst of 429 produces.
    const servidor = servidorQueRechazaConCuerpo(503)
    vi.stubGlobal('fetch', servidor.fetchFalso)

    const { estado, ultimoError, enviar } = useChatStream()
    await enviar('como va la morosidad')

    expect(ultimoError.value?.codigo).toBe('http_503')
    expect(estado.value).toBe('fallido')
    expect(servidor.liberaciones()).toBe(1)
    expect(servidor.senal()?.aborted).toBe(true)
  })

  it('convierte un 403 en un fallo de permiso que no invita a reintentar', async () => {
    // The defect this catches: leaving a refused request without a typed
    // failure, or minting it as recoverable. US-024 offers Reintentar on
    // `recuperable`, and retrying a permission failure walks the reader
    // through the same refusal with no explanation of why.
    vi.stubGlobal('fetch', servidorQueRechaza(403))

    const { estado, ultimoError, enviar } = useChatStream()
    await enviar('exposicion agregada por contraparte')

    expect(estado.value).toBe('fallido')
    expect(ultimoError.value).toEqual({
      paso: 'verificacion_de_permiso',
      clase: 'permiso',
      codigo: 'http_403',
      mensaje_clave: CLAVE_PERMISO_GENERICA,
      recuperable: false,
    })
  })

  it('un 401 expira la sesion y saca al lector a la entrada', async () => {
    // The defect this catches: treating an expired session as one more
    // recoverable failure. The reader would sit in front of an assistant that
    // stopped answering with no reason given, and every question afterwards
    // would be refused the same way. `expirada` is asserted next to the
    // navigation because navigating without expiring lands on an entry screen
    // that does not know why it was reached.
    const navegar = vi.fn(async () => undefined)
    vi.stubGlobal('navigateTo', navegar)
    vi.stubGlobal('fetch', servidorQueRechaza(401))

    const { estado, ultimoError, enviar } = useChatStream()
    await enviar('como va la morosidad')

    expect(navegar).toHaveBeenCalledWith(`${RUTA_ACCESO}?motivo=${MOTIVO_EXPIRADA}`)
    expect(usePermisos().expirada.value).toBe(true)
    expect(ultimoError.value?.codigo).toBe('http_401')
    expect(estado.value).toBe('fallido')
  })

  it('no repinta como fallo de red el error de permiso que ya publico', async () => {
    // The defect this catches: a `catch` that covers everything after the
    // `fetch`, including the navigation of the 401. A `navigateTo` that rejects
    // -an aborted navigation, a guard that redirects elsewhere- turns a failure
    // already published as `permiso`/`http_401` into a recoverable network one,
    // and US-024 then offers a Reintentar that cannot work: the session was
    // already emptied by `expirarSesion()`.
    vi.stubGlobal('navigateTo', vi.fn(() => Promise.reject(new Error('navegacion abortada'))))
    vi.stubGlobal('fetch', servidorQueRechaza(401))

    const { estado, ultimoError, enviar } = useChatStream()
    await enviar('como va la morosidad')

    expect(ultimoError.value).toEqual({
      paso: 'verificacion_de_permiso',
      clase: 'permiso',
      codigo: 'http_401',
      mensaje_clave: CLAVE_PERMISO_GENERICA,
      recuperable: false,
    })
    expect(estado.value).toBe('fallido')
  })
})

describe('la pantalla del asistente', () => {
  it('ofrece Detener desde el primer tick de la generacion y nunca junto a Enviar', async () => {
    // The defect this catches: tying the button to "there is at least one
    // token". During the first second, which is exactly when a reader wants to
    // abort, the button would not be there.
    const servidor = servidorSSE()
    vi.stubGlobal('fetch', servidor.fetchFalso)

    const wrapper = await montarPagina()

    expect(wrapper.find('[data-prueba="detener"]').exists()).toBe(false)
    expect(wrapper.find('[data-prueba="enviar"]').exists()).toBe(true)

    await preguntar(wrapper, 'como va la morosidad')

    // Not a single frame has arrived yet, and the button is already there.
    expect(wrapper.find('[data-prueba="detener"]').exists()).toBe(true)
    expect(wrapper.find('[data-prueba="enviar"]').exists()).toBe(false)

    servidor.entregar(marco('tool_call', ANUNCIO))
    await flushPromises()

    expect(wrapper.find('[data-prueba="detener"]').exists()).toBe(true)
    expect(wrapper.find('[data-prueba="enviar"]').exists()).toBe(false)

    await wrapper.get('[data-prueba="detener"]').trigger('click')
    await flushPromises()

    expect(servidor.senal()?.aborted).toBe(true)
    expect(wrapper.find('[data-prueba="detener"]').exists()).toBe(false)
    expect(wrapper.find('[data-prueba="enviar"]').exists()).toBe(true)
  })

  it('no dice que no hay conversacion mientras el turno ya esta generando', async () => {
    // The defect this catches: an empty state tied to `hilo.length === 0` and
    // to nothing else. Between the submit and the first token -the second the
    // reader watches hardest- the log claims there is nothing to show while
    // the server is already answering, right next to a Detener button over a
    // request that is very much alive. The skeleton takes that slot so the
    // wait is drawn as a wait, and the empty state comes back only when the
    // turn is over with nothing in the thread.
    const servidor = servidorSSE()
    vi.stubGlobal('fetch', servidor.fetchFalso)

    const wrapper = await montarPagina()

    expect(wrapper.find('[data-prueba="hilo-vacio"]').exists()).toBe(true)
    expect(wrapper.find('[data-prueba="hilo-esperando"]').exists()).toBe(false)

    await preguntar(wrapper, 'como va la morosidad')

    // Not a single frame has arrived, and the thread is still empty.
    expect(wrapper.find('[data-prueba="hilo-vacio"]').exists()).toBe(false)
    expect(wrapper.get('[data-prueba="hilo-esperando"]').text())
      .toBe(mensaje('es', 'chat.page.waitingFirstToken'))

    servidor.entregar(marco('token', { texto: 'La morosidad ', indice: 0 }))
    await flushPromises()

    expect(wrapper.find('[data-prueba="hilo-esperando"]').exists()).toBe(false)
    expect(wrapper.find('[data-prueba="hilo-vacio"]').exists()).toBe(false)

    await wrapper.get('[data-prueba="detener"]').trigger('click')
    await flushPromises()

    // A cancelled turn that did leave something on screen keeps it: the empty
    // state is about an empty thread, not about a stream that is not running.
    expect(wrapper.find('[data-prueba="hilo-vacio"]').exists()).toBe(false)
  })

  it('mantiene la franja de honestidad en los tres estados', async () => {
    // The defect this catches: tying the notice to the empty thread, or hiding
    // it while generating. The warning would disappear at the exact moment the
    // scripted content appears. It also covers the GO branch of the sabado:
    // the expected copy is read from the provider constant, so flipping the
    // provider changes the sentence and keeps the measurement.
    const servidor = servidorSSE()
    vi.stubGlobal('fetch', servidor.fetchFalso)

    const esperado = mensaje('es', CLAVE_AVISO_DEMO[PROVEEDOR_DE_CHAT])
    const wrapper = await montarPagina()

    expect(wrapper.get('[data-prueba="estado-stream"]').text()).toBe(mensaje('es', 'chat.stream.status.idle'))
    expect(wrapper.get('[data-prueba="aviso-demo"]').text()).toBe(esperado)

    await preguntar(wrapper, 'como va la morosidad')
    servidor.entregar(marco('token', { texto: 'La morosidad ', indice: 0 }))
    await flushPromises()

    expect(wrapper.get('[data-prueba="estado-stream"]').text()).toBe(mensaje('es', 'chat.stream.status.generating'))
    expect(wrapper.get('[data-prueba="aviso-demo"]').text()).toBe(esperado)

    await wrapper.get('[data-prueba="detener"]').trigger('click')
    await flushPromises()

    expect(wrapper.get('[data-prueba="estado-stream"]').text()).toBe(mensaje('es', 'chat.stream.status.cancelled'))
    expect(wrapper.get('[data-prueba="aviso-demo"]').text()).toBe(esperado)
  })

  it('no escribe ninguna cadena visible dentro del componente', async () => {
    // The defect this catches: writing "Detener" in the template. The screen
    // would look right in Spanish and stay Spanish in English, and the only
    // assertions that would notice are the ones that compare a rendered string
    // against a catalogue it never read.
    const servidor = servidorSSE()
    vi.stubGlobal('fetch', servidor.fetchFalso)

    const fuente = readFileSync(rutaDelRepositorio('../app/pages/asistente.vue'), 'utf8')
      .replace(/<!--[\s\S]*?-->/g, ' ')
      .replace(/\/\*[\s\S]*?\*\//g, ' ')
      .replace(/^\s*\/\/.*$/gm, ' ')

    for (const idioma of ['es', 'en'] as const) {
      const wrapper = await montarPagina(idioma)
      await preguntar(wrapper, 'como va la morosidad')
      servidor.entregar(marco('tool_call', RESUELTA))
      await flushPromises()

      const visibles = textosVisibles(wrapper.element)

      // Two labels of the screen are named so the scan cannot pass over an
      // empty render, which is how a check like this rots without a sound.
      expect(visibles).toContain(mensaje(idioma, 'chat.page.title'))
      expect(visibles).toContain(mensaje(idioma, 'chat.controls.stop'))
      expect(visibles.filter(texto => fuente.includes(texto))).toEqual([])

      // Released here and not on teardown, because the next language mounts the
      // same page and needs the `fetch` double this suite stubbed to survive.
      desmontarPaginas()
    }
  })
})

/**
 * Every rendered text node, which is what a reader actually sees.
 *
 * Short runs are dropped because a single character of punctuation coming from
 * a child component would collide with any file by accident and say nothing
 * about this one; no visible label of an interface is that short.
 */
function textosVisibles(elemento: Element): string[] {
  const textos: string[] = []

  const recorrer = (nodo: Node): void => {
    for (const hijo of Array.from(nodo.childNodes)) {
      if (hijo.nodeType === Node.TEXT_NODE) {
        const texto = (hijo.textContent ?? '').trim()
        if (texto.length >= 3) {
          textos.push(texto)
        }
        continue
      }
      recorrer(hijo)
    }
  }

  recorrer(elemento)
  return textos
}

describe('las claves que no pasan por t() tambien tienen que existir', () => {
  /**
   * Every i18n key this User Story names inside a plain object.
   *
   * `CLAVE_PASO`, `CLAVE_ESTADO_CHAT` and `CLAVE_AVISO_DEMO` are lookup tables,
   * and `CLAVE_FALLO_DE_TRANSPORTE` is a constant: the interface resolves them
   * as `t(CLAVE_PASO[paso])`, with the key in a variable.
   */
  const CLAVES_INDIRECTAS = [
    ...Object.values(CLAVE_PASO),
    ...Object.values(CLAVE_ESTADO_CHAT).filter((clave): clave is string => clave !== null),
    ...Object.values(CLAVE_AVISO_DEMO),
    CLAVE_FALLO_DE_TRANSPORTE,
    CLAVE_PERMISO_GENERICA,
    CLAVE_PERMISO_CON_NIVEL,
  ]

  it.each(CLAVES_INDIRECTAS)('resuelve %s en los dos catalogos', (clave) => {
    // The gap this closes is a real one and it had nobody watching it.
    // `contratos.spec.ts` finds keys written as literals inside a `t('...')`
    // call; none of these is. Rename a leaf in the JSON, or drop one when the
    // fallback subtree is cleaned up, and vue-i18n prints the key path itself
    // -`chat.stream.step.dataRetrieval` on screen, in both languages- with the
    // whole suite still green.
    for (const idioma of ['es', 'en'] as const) {
      expect(clavesDe(idioma), `${idioma}: falta ${clave}`).toContain(clave)
      expect(mensaje(idioma, clave).trim()).not.toBe('')
    }
  })

  it('no pinta un fallo de transporte cuando lo que hubo fue un rechazo', () => {
    // The agreement this case used to guard is consumed: the two provisional
    // fallback leaves are gone from both catalogues, and asserting that the
    // constant is not the name of a leaf nobody declares any more is an
    // assertion that cannot fail.
    //
    // What replaces it is the defect that is alive. A refusal and a dropped
    // socket are different events with different copy, and the client fabricates
    // the typed error for both. Point the refusal at the transport key and the
    // notice heads itself "Tu nivel de acceso no alcanza" over a body that says
    // the transport failed: two sentences that contradict each other, and the
    // copy written for exactly this case unreachable. The families are asserted
    // apart, so collapsing them back into one key goes red here.
    expect(CLAVE_PERMISO_GENERICA).not.toBe(CLAVE_FALLO_DE_TRANSPORTE)
    expect(CLAVE_PERMISO_GENERICA.startsWith('chat.error.')).toBe(true)
    expect(CLAVE_FALLO_DE_TRANSPORTE.startsWith('chat.stream.')).toBe(true)
  })
})
