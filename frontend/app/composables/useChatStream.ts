import type { Ref, ShallowRef } from 'vue'
import type {
  EstadoChat,
  EventoDone,
  EventoError,
  EventoSSE,
  EventoToken,
  EventoToolCall,
  ItemHilo,
  MotivoCierre,
  NombreEvento,
  TarjetaToolCall,
} from '~/types/chat'
import { onScopeDispose, ref, shallowRef } from 'vue'
import { usePermisos } from '~/composables/usePermisos'
import { CLAVE_PERMISO_GENERICA, NOMBRES_DE_EVENTO } from '~/types/chat'

/**
 * SSE client of the assistant: one question, one stream, one real cancellation.
 *
 * `fetch` with a `ReadableStream` and an `AbortController`, and deliberately
 * not `EventSource`: that API cannot POST, cannot carry headers and cannot be
 * aborted, and this User Story is about the abort. The price is the framing
 * parser below, which is exported so it can be tested with a frame cut in half
 * -the failure that never happens on localhost and does happen behind a proxy-.
 *
 * No header of session travels from here. The cookie is httpOnly, the browser
 * attaches it to the same origin request, and the Nitro proxy is the only place
 * where it becomes an `Authorization: Bearer`.
 *
 * The thread holds one answer, not a conversation. `ItemHilo` has no shape for
 * the reader's own question -there is no persistence of conversations in S4-,
 * so keeping the previous turn would paint two answers in a row with nothing
 * between them. Every turn starts from an empty thread, and that is a decision
 * of the frozen type rather than of this file.
 *
 * Every write that happens after an `await` is guarded by the identity of its
 * turn. An aborted turn does not die where it was aborted: its rejection takes
 * a macrotask to travel and one microtask -a `nextTick`- is not enough, so a
 * `detener()` followed by a new `enviar()` leaves the old turn unwinding on top
 * of the new one. Without an identity it would null somebody else's controller,
 * write `cancelado` over a stream that is generating, and append its frames to
 * a thread that is already answering another question.
 */

/** Route of the stream, behind the proxy that turns the cookie into a bearer. */
export const RUTA_CHAT = '/api/chat'

/** Media type the endpoint answers with, asked for explicitly. */
export const TIPO_DE_MEDIO = 'text/event-stream'

/**
 * Copy of a transport failure that never reached the wire as an `error` event.
 *
 * A dropped or unreachable request produces no typed event, so the client mints
 * one in order to have a single shape of failure on screen.
 *
 * It has a key of its own and it is permanent: a connection that drops will
 * keep dropping, so this copy never belonged to the provisional subtree that
 * the screen used before `AvisoError` existed and that no longer exists.
 *
 * It covers the `recuperable` family alone. A refusal is not a transport
 * failure -nothing broke on the way, the server said no- and telling the reader
 * that the transport failed under a title that says their access level is not
 * enough is two answers to the same question.
 */
export const CLAVE_FALLO_DE_TRANSPORTE = 'chat.stream.transportError'

/** Separator of two frames on the wire, exactly as the backend writes it. */
const FIN_DE_MARCO = '\n\n'

/** Field prefixes of a frame. Anything else in it is not ours to read. */
const PREFIJO_EVENTO = 'event:'
const PREFIJO_DATOS = 'data:'

/** State the conversation lands in for each reason the stream ended. */
const ESTADO_AL_CERRAR: Readonly<Record<MotivoCierre, EstadoChat>> = Object.freeze({
  completado: 'inactivo',
  cancelado: 'cancelado',
  error: 'fallido',
})

/** Whether a wire name is one of the four the contract declares. */
function esNombreDeEvento(valor: string): valor is NombreEvento {
  return (NOMBRES_DE_EVENTO as readonly string[]).includes(valor)
}

/**
 * Reads one complete frame into the event it carries.
 *
 * @param marco - Frame without its trailing blank line.
 * @returns The typed event, or null when the frame is not one of the four.
 */
function interpretarMarco(marco: string): EventoSSE | null {
  let nombre: string | null = null
  const datos: string[] = []

  for (const linea of marco.split('\n')) {
    if (linea.startsWith(PREFIJO_EVENTO)) {
      nombre = linea.slice(PREFIJO_EVENTO.length).trim()
      continue
    }
    if (linea.startsWith(PREFIJO_DATOS)) {
      datos.push(linea.slice(PREFIJO_DATOS.length).trim())
    }
  }

  if (nombre === null || !esNombreDeEvento(nombre) || datos.length === 0) {
    return null
  }

  try {
    // The body is trusted for its shape and for nothing else: it is the
    // serialisation of the same models the contract froze, and a frame whose
    // name is not one of the four was already dropped above.
    const cuerpo = JSON.parse(datos.join('\n')) as EventoSSE['datos']
    return { nombre, datos: cuerpo } as EventoSSE
  }
  catch {
    return null
  }
}

/**
 * Splits a raw buffer into complete SSE frames, keeping the incomplete tail.
 *
 * Exported on purpose: it is the only way to exercise the parser with a frame
 * cut in half, which is what a `split()` over each chunk gets wrong. The tail
 * is returned untouched so the caller can prepend it to the next chunk.
 *
 * @param bufer - Everything received and not yet parsed.
 * @returns The events of every complete frame, and the pending tail.
 */
export function analizarTramos(bufer: string): { eventos: EventoSSE[], resto: string } {
  const tramos = bufer.split(FIN_DE_MARCO)
  const resto = tramos.pop() ?? ''
  const eventos: EventoSSE[] = []

  for (const tramo of tramos) {
    const evento = interpretarMarco(tramo)
    if (evento !== null) {
      eventos.push(evento)
    }
  }

  return { eventos, resto }
}

/**
 * One turn and the two things it has to be able to release.
 *
 * They belong to the turn and not to the composable on purpose: a relieved turn
 * keeps running for as long as its rejection takes to arrive, and the reference
 * it clears on its way out has to be its own.
 */
interface Turno {
  controlador: AbortController
  lector: ReadableStreamDefaultReader<Uint8Array> | null
}

/** What the assistant screen needs in order to drive one conversation. */
export interface ControlDeChat {
  /** State of the turn, as the screen renders it. */
  estado: Readonly<Ref<EstadoChat>>
  /** Cards and text in arrival order. The shallowRef is never made deep. */
  hilo: Readonly<ShallowRef<readonly ItemHilo[]>>
  /** The same cards, by their stable id, for an update that is not an append. */
  tarjetas: Readonly<Ref<ReadonlyMap<string, TarjetaToolCall>>>
  /** Why the stream ended, or null while it is open. */
  motivoCierre: Readonly<Ref<MotivoCierre | null>>
  /** Last typed failure of the turn, or null when there was none. */
  ultimoError: Readonly<Ref<EventoError | null>>
  /** Opens the stream for one question. Resolves when the turn is over. */
  enviar: (mensaje: string) => Promise<void>
  /** Aborts the request and releases the body. Safe to call with none open. */
  detener: () => void
}

/**
 * Drives one SSE conversation, with a cancellation that reaches the server.
 *
 * @returns The state of the turn, its thread, its cards and the two actions.
 */
export function useChatStream(): ControlDeChat {
  const { expirarSesion } = usePermisos()

  const estado = ref<EstadoChat>('inactivo')
  const hilo = shallowRef<readonly ItemHilo[]>([])
  const tarjetas = shallowRef<ReadonlyMap<string, TarjetaToolCall>>(new Map())
  const motivoCierre = ref<MotivoCierre | null>(null)
  const ultimoError = shallowRef<EventoError | null>(null)

  let turnoVigente: Turno | null = null

  /** Whether this turn is still the one the screen is answering with. */
  function esVigente(turno: Turno): boolean {
    return turnoVigente === turno
  }

  /**
   * Applies one card, replacing only its own object.
   *
   * Every other item of the thread and every other entry of the map keep their
   * identity, which is what lets a screen with two live cards repaint the one
   * that moved instead of all of them.
   */
  function aplicarTarjeta(datos: EventoToolCall): void {
    const previa = tarjetas.value.get(datos.id)
    const tarjeta: TarjetaToolCall = {
      ...datos,
      iniciadaEnMs: previa?.iniciadaEnMs ?? Date.now(),
    }

    const mapa = new Map(tarjetas.value)
    mapa.set(datos.id, tarjeta)
    tarjetas.value = mapa

    hilo.value
      = previa === undefined
        ? [...hilo.value, { tipo: 'tarjeta', id: datos.id, tarjeta }]
        : hilo.value.map(item =>
            item.tipo === 'tarjeta' && item.id === datos.id ? { ...item, tarjeta } : item,
          )
  }

  /**
   * Appends a fragment to the block of text that is being written.
   *
   * A fragment that arrives after a card opens a new block, so the order of the
   * thread keeps saying which card justifies which sentence.
   */
  function aplicarToken(datos: EventoToken): void {
    const ultimo = hilo.value[hilo.value.length - 1]

    hilo.value
      = ultimo !== undefined && ultimo.tipo === 'texto'
        ? [...hilo.value.slice(0, -1), { ...ultimo, texto: ultimo.texto + datos.texto }]
        : [...hilo.value, { tipo: 'texto', id: `texto-${datos.indice}`, texto: datos.texto }]
  }

  /** Closes the turn with the reason the server gave. */
  function cerrar(datos: EventoDone): void {
    motivoCierre.value = datos.motivo
    estado.value = ESTADO_AL_CERRAR[datos.motivo]
  }

  function aplicar(evento: EventoSSE): void {
    switch (evento.nombre) {
      case 'tool_call':
        aplicarTarjeta(evento.datos)
        break
      case 'token':
        aplicarToken(evento.datos)
        break
      case 'error':
        ultimoError.value = evento.datos
        break
      case 'done':
        cerrar(evento.datos)
        break
    }
  }

  /**
   * Mints the typed failure of something that never reached the wire.
   *
   * The copy follows the family and not the origin. A refusal already sets its
   * step to `verificacion_de_permiso`, and the notice titles it "your access
   * level is not enough": pairing that title with the transport sentence
   * describes a failure that did not happen -nothing broke on the way- and
   * leaves the copy written for this exact case unreachable. The generic one is
   * the honest choice here and not a fallback: an HTTP status carries no level,
   * so this branch cannot name what was missing even if it wanted to.
   *
   * @param codigo - Stable code of the failure, never a sentence.
   * @param clase - Family of the failure, which decides whether retrying helps.
   * @returns The event the screen renders, shaped like a server one.
   */
  function errorDeTransporte(codigo: string, clase: EventoError['clase']): EventoError {
    const esPermiso = clase === 'permiso'
    return {
      paso: esPermiso ? 'verificacion_de_permiso' : 'transporte',
      clase,
      codigo,
      mensaje_clave: esPermiso ? CLAVE_PERMISO_GENERICA : CLAVE_FALLO_DE_TRANSPORTE,
      recuperable: clase === 'recuperable',
    }
  }

  /**
   * Closes the turn as failed, without repainting a failure already published.
   *
   * The server names what broke -which silo, at which step, with the code US-024
   * draws its notice from- and the client can only mint a generic transport
   * failure. When both happen in the same turn the one carrying the diagnosis
   * wins: a stream that reports `silo_no_disponible` and then drops must not end
   * up saying that the transport failed. The state moves either way, because a
   * turn left in `generando` forever is worse than a coarse message.
   */
  function fallar(evento: EventoError): void {
    if (ultimoError.value === null) {
      ultimoError.value = evento
    }
    motivoCierre.value = 'error'
    estado.value = 'fallido'
  }

  function reiniciar(): void {
    hilo.value = []
    tarjetas.value = new Map()
    motivoCierre.value = null
    ultimoError.value = null
  }

  /**
   * Releases a body nobody is going to read.
   *
   * A refused request still answers with a payload -FastAPI serialises its
   * detail as JSON- and that branch never reaches `getReader()`, so without
   * cancelling it the stream is left open: one body per refusal, which a burst
   * of 429 turns into as many as the reader has patience for.
   */
  function descartarCuerpo(cuerpo: ReadableStream<Uint8Array> | null): void {
    void cuerpo?.cancel().catch(() => undefined)
  }

  /** Reads the body frame by frame until it ends or the turn is relieved. */
  async function consumir(cuerpo: ReadableStream<Uint8Array>, turno: Turno): Promise<void> {
    const lector = cuerpo.getReader()
    turno.lector = lector
    const decodificador = new TextDecoder()
    let bufer = ''

    try {
      for (;;) {
        const trozo = await lector.read()
        if (trozo.done) {
          break
        }

        // A `done` closes the turn on screen while its body is still open -the
        // server writes that frame and then closes the socket-, so the reader
        // can ask again with this loop still in flight. What arrives now belongs
        // to the question that was replaced, and applying it would write a
        // sentence of the previous answer into the middle of the current one.
        if (!esVigente(turno)) {
          break
        }

        bufer += decodificador.decode(trozo.value, { stream: true })
        const { eventos, resto } = analizarTramos(bufer)
        bufer = resto

        for (const evento of eventos) {
          aplicar(evento)
        }
      }
    }
    finally {
      // Only the turn that still holds the reader releases it: `detener` takes
      // it away precisely so that it is not cancelled twice.
      const abandonado = turno.lector === lector && !esVigente(turno)
      turno.lector = null
      if (abandonado) {
        void lector.cancel().catch(() => undefined)
      }
    }
  }

  /** Translates a refused request into the same shape as a typed failure. */
  async function rechazar(estadoHttp: number): Promise<void> {
    const clase: EventoError['clase']
      = estadoHttp === 401 || estadoHttp === 403 ? 'permiso' : 'recuperable'
    fallar(errorDeTransporte(`http_${estadoHttp}`, clase))

    if (estadoHttp === 401) {
      // The hook US-017 exported for exactly this branch: a session that died
      // while the reader was waiting ends on the entry screen with its reason,
      // not on an assistant that quietly stops answering.
      await navigateTo(expirarSesion())
    }
  }

  async function enviar(mensaje: string): Promise<void> {
    if (estado.value === 'generando') {
      return
    }

    reiniciar()
    estado.value = 'generando'

    const turno: Turno = { controlador: new AbortController(), lector: null }
    turnoVigente = turno

    try {
      const respuesta = await fetch(RUTA_CHAT, {
        method: 'POST',
        headers: { 'accept': TIPO_DE_MEDIO, 'content-type': 'application/json' },
        body: JSON.stringify({ mensaje }),
        // The cookie is httpOnly and same origin: it travels on its own and
        // nothing here ever sees the token.
        credentials: 'same-origin',
        signal: turno.controlador.signal,
      })

      // The reader may have cancelled and asked again while the request was in
      // flight, and everything below this line writes state that is shared.
      if (!esVigente(turno)) {
        descartarCuerpo(respuesta.body)
        return
      }

      if (!respuesta.ok) {
        descartarCuerpo(respuesta.body)
        await rechazar(respuesta.status)
        return
      }

      if (respuesta.body === null) {
        fallar(errorDeTransporte('cuerpo_vacio', 'recuperable'))
        return
      }

      await consumir(respuesta.body, turno)

      // The server always closes with `done`. A body that ends without one is a
      // connection that dropped, and saying so is better than a screen that
      // stays in "generating" forever.
      if (esVigente(turno) && estado.value === 'generando') {
        fallar(errorDeTransporte('stream_interrumpido', 'recuperable'))
      }
    }
    catch {
      if (!esVigente(turno)) {
        // Two ways to get here and neither is a failure to report. A
        // cancellation: `detener` retires the turn and then aborts it, and the
        // abort is what rejects the read that was in flight, with the state
        // already moved on the tick of the click. Or a turn relieved while its
        // rejection travelled, whose screen is answering another question now.
        return
      }
      fallar(errorDeTransporte('red_inalcanzable', 'recuperable'))
    }
    finally {
      // Its own reference and only if nobody took it first: a relieved turn
      // that cleared this would leave the live one uncancellable, with the
      // button gone from the screen and the scope disposal returning on its
      // first line.
      if (esVigente(turno)) {
        turnoVigente = null
      }
      // Whatever ended the turn -a `done`, a refusal, a drop-, nobody is going
      // to read this request again, and aborting after the fact is idempotent.
      // It happens here and not next to the refusal so that the `catch` above
      // can still tell a cancellation from a failure of its own.
      turno.controlador.abort()
    }
  }

  function detener(): void {
    const turno = turnoVigente
    if (turno === null) {
      return
    }
    turnoVigente = null

    // The local state moves first so the button swaps on the same tick the
    // reader clicked, and the two calls below are what make the change real.
    motivoCierre.value = 'cancelado'
    estado.value = 'cancelado'

    // Aborting the request is what stops the server -and, with a paid model
    // behind it, what stops paying-. Cancelling the reader is what releases the
    // body of a response that already arrived. A button that only flips the
    // local state does neither, and looks identical from the screen.
    turno.controlador.abort()

    const lector = turno.lector
    turno.lector = null
    if (lector !== null) {
      // Already errored by the abort in a real stream, so its rejection is the
      // expected outcome and not a failure to report.
      void lector.cancel().catch(() => undefined)
    }
  }

  // Leaving the screen has to abort as hard as pressing Detener does. Nothing
  // else calls it: the reader asks, walks to the dashboard, and the request
  // stays open against a model that keeps generating -and keeps charging- for
  // a component that no longer exists. `detener` is idempotent, so a scope
  // that dies with no request open returns on its first line.
  onScopeDispose(detener)

  return { estado, hilo, tarjetas, motivoCierre, ultimoError, enviar, detener }
}
