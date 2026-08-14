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
import { NOMBRES_DE_EVENTO } from '~/types/chat'

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
 */

/** Route of the stream, behind the proxy that turns the cookie into a bearer. */
export const RUTA_CHAT = '/api/chat'

/** Media type the endpoint answers with, asked for explicitly. */
export const TIPO_DE_MEDIO = 'text/event-stream'

/**
 * Copy of a failure that never reached the wire as an `error` event.
 *
 * A refused or dropped request produces no typed event, so the client mints
 * one in order to have a single shape of failure on screen.
 *
 * It has a key of its own and not the fallback one, and that is the whole
 * point: `chat.stream.errorFallback` is provisional copy that US-024 deletes
 * the moment it mounts `AvisoError`, and a transport failure is not
 * provisional -a dropped connection or a refused request will keep happening
 * after that component lands-. Sharing the key would have left every network
 * failure without copy on somebody else's commit.
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

  let controlador: AbortController | null = null
  let lectorActivo: ReadableStreamDefaultReader<Uint8Array> | null = null

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
   * @param codigo - Stable code of the failure, never a sentence.
   * @param clase - Family of the failure, which decides whether retrying helps.
   * @returns The event the screen renders, shaped like a server one.
   */
  function errorDeTransporte(codigo: string, clase: EventoError['clase']): EventoError {
    return {
      paso: clase === 'permiso' ? 'verificacion_de_permiso' : 'transporte',
      clase,
      codigo,
      mensaje_clave: CLAVE_FALLO_DE_TRANSPORTE,
      recuperable: clase === 'recuperable',
    }
  }

  function fallar(evento: EventoError): void {
    ultimoError.value = evento
    motivoCierre.value = 'error'
    estado.value = 'fallido'
  }

  function reiniciar(): void {
    hilo.value = []
    tarjetas.value = new Map()
    motivoCierre.value = null
    ultimoError.value = null
  }

  /** Reads the body frame by frame until it ends or the reader is cancelled. */
  async function consumir(cuerpo: ReadableStream<Uint8Array>): Promise<void> {
    const lector = cuerpo.getReader()
    lectorActivo = lector
    const decodificador = new TextDecoder()
    let bufer = ''

    try {
      for (;;) {
        const trozo = await lector.read()
        if (trozo.done) {
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
      lectorActivo = null
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

    const enCurso = new AbortController()
    controlador = enCurso

    try {
      const respuesta = await fetch(RUTA_CHAT, {
        method: 'POST',
        headers: { 'accept': TIPO_DE_MEDIO, 'content-type': 'application/json' },
        body: JSON.stringify({ mensaje }),
        // The cookie is httpOnly and same origin: it travels on its own and
        // nothing here ever sees the token.
        credentials: 'same-origin',
        signal: enCurso.signal,
      })

      if (!respuesta.ok) {
        await rechazar(respuesta.status)
        return
      }

      if (respuesta.body === null) {
        fallar(errorDeTransporte('cuerpo_vacio', 'recuperable'))
        return
      }

      await consumir(respuesta.body)

      // The server always closes with `done`. A body that ends without one is a
      // connection that dropped, and saying so is better than a screen that
      // stays in "generating" forever.
      if (estado.value === 'generando') {
        fallar(errorDeTransporte('stream_interrumpido', 'recuperable'))
      }
    }
    catch {
      if (enCurso.signal.aborted) {
        // Reaching here is the ordinary end of a cancellation: aborting the
        // request rejects the read that was in flight.
        motivoCierre.value = 'cancelado'
        estado.value = 'cancelado'
        return
      }
      fallar(errorDeTransporte('red_inalcanzable', 'recuperable'))
    }
    finally {
      controlador = null
    }
  }

  function detener(): void {
    const enCurso = controlador
    if (enCurso === null) {
      return
    }
    controlador = null

    // The local state moves first so the button swaps on the same tick the
    // reader clicked, and the two calls below are what make the change real.
    motivoCierre.value = 'cancelado'
    estado.value = 'cancelado'

    // Aborting the request is what stops the server -and, with a paid model
    // behind it, what stops paying-. Cancelling the reader is what releases the
    // body of a response that already arrived. A button that only flips the
    // local state does neither, and looks identical from the screen.
    enCurso.abort()

    const lector = lectorActivo
    lectorActivo = null
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
