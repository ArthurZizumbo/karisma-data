/**
 * TypeScript mirror of SSE contract v1, as `backend/app/models/chat.py` froze it.
 *
 * Four names travel on the wire -`tool_call`, `token`, `error` and `done`- and
 * this module is the only place where their fields are declared on the client.
 * US-024 (typed error notice) and US-028 (tool call card) import from here and
 * neither of them widens a type: a field added without going through the
 * contract silently changes two other screens.
 *
 * The closed vocabularies are literal unions and not `string` on purpose. The
 * interface switches on them, and a fifth value nobody declared would reach the
 * browser as an unhandled case that no test could ever fail on.
 */

/** Life stage of a tool call card. The card is updated by id, never appended. */
export type EstadoTarjeta = 'anuncio' | 'ejecucion' | 'resultado' | 'error'

/** Closed vocabulary of the step of the stream that can fail. */
export type PasoDelStream
  = | 'recuperacion_de_datos'
    | 'verificacion_de_permiso'
    | 'generacion_de_texto'
    | 'transporte'

/** Why the stream ended. */
export type MotivoCierre = 'completado' | 'cancelado' | 'error'

/** Wire name of each event, written in the `event:` line of the frame. */
export type NombreEvento = 'tool_call' | 'token' | 'error' | 'done'

/** The four names, for the parser to reject anything else. */
export const NOMBRES_DE_EVENTO: readonly NombreEvento[] = Object.freeze([
  'tool_call',
  'token',
  'error',
  'done',
])

/** Mini-table or single figure a tool call returned. */
export interface ResultadoTarjeta {
  /**
   * Header of the mini-table, one i18n key per column.
   *
   * Keys and not prose, like `etiqueta` and `mensajeClave` of this same
   * contract: a header names what the column holds, so it is interface and it
   * is translated. While it travelled as Spanish prose, `/guia` with the
   * interface in English rendered a card that was English everywhere except
   * these two headers.
   */
  columnas: string[]
  /**
   * Rows of the mini-table, aligned with `columnas`.
   *
   * These stay data and are NOT translated: they come from the silo, and
   * translating a value the provider returned would be inventing it.
   */
  filas: Array<Array<string | number>>
  /** Scalar the card highlights, already formatted, or null when it is a table. */
  cifra: string | null
}

/**
 * SSE event `tool_call`: one card, four possible states, stable id.
 *
 * `herramienta` is the technical name (`consultar_metrica`); `etiqueta` is the
 * FULL i18n key of the readable name, always shaped
 * `chat.toolCall.tool.<herramienta>`, never a sentence. The card of US-028
 * resolves that key directly: the provisional copy this comment used to name
 * was retired with the fallback block it belonged to.
 */
export interface EventoToolCall {
  id: string
  estado: EstadoTarjeta
  herramienta: string
  etiqueta: string
  /** Milliseconds since the card was announced. Null in the announcement. */
  transcurrido_ms: number | null
  /** Payload of the tool, only in the resolving event. */
  resultado: ResultadoTarjeta | null
  /** Catalogue field the figure comes from. What makes a number citable. */
  fuente: string | null
  /** Step that failed, only when the card ends in error. */
  paso: PasoDelStream | null
}

/** SSE event `token`: one incremental fragment with its monotonic position. */
export interface EventoToken {
  texto: string
  indice: number
}

/**
 * SSE event `error`: typed failure whose message is an i18n key.
 *
 * Exactly five frozen fields. The contract deliberately does not carry the
 * level a permission failure demanded: the client derives it, and the backend
 * never publishes what a caller would have needed in order to see the data.
 */
export interface EventoError {
  paso: PasoDelStream
  /** `recuperable` invites retrying the same turn; `permiso` never does. */
  clase: 'recuperable' | 'permiso'
  /** Stable code of the failure, never a sentence. */
  codigo: string
  /** i18n key of the copy the interface shows. */
  mensaje_clave: string
  recuperable: boolean
}

/**
 * i18n key of the refusal that CAN name the level it demanded.
 *
 * It is the only copy of the family with a `{nivel}` slot, and the scripted
 * provider is the only thing that emits it -the refusal of C4-. Whoever renders
 * it has to supply that level, because the five frozen fields do not carry it,
 * and that is what makes this constant the discriminator: the screen contributes
 * a level exactly when the copy asks for one, and never by guessing.
 */
export const CLAVE_PERMISO_CON_NIVEL = 'chat.error.message.permission'

/**
 * i18n key of the refusal that CANNOT name the level it demanded.
 *
 * A rejection minted from an HTTP status knows that permission was missing and
 * nothing else: 403 carries no level and contract v1 does not transport one. So
 * this is the honest copy of that path, and it is also what the notice falls
 * back to when a caller supplies no level, which is the same case said twice.
 */
export const CLAVE_PERMISO_GENERICA = 'chat.error.message.permissionGeneric'

/** SSE event `done`: closes the stream exactly once. */
export interface EventoDone {
  motivo: MotivoCierre
  /**
   * Fragments that actually left the server.
   *
   * Compared with the length of the answer it is what tells a real
   * cancellation from a cosmetic one.
   */
  tokens_emitidos: number
  duracion_ms: number
}

/** Any event the stream can carry. The union is closed: there is no fifth. */
export type EventoChat = EventoToolCall | EventoToken | EventoError | EventoDone

/** One parsed frame: its wire name and the body that belongs to that name. */
export type EventoSSE
  = | { nombre: 'tool_call', datos: EventoToolCall }
    | { nombre: 'token', datos: EventoToken }
    | { nombre: 'error', datos: EventoError }
    | { nombre: 'done', datos: EventoDone }

/**
 * State of the conversation as the screen renders it.
 *
 * A finished turn goes back to `inactivo`: there is no `completado`, because
 * the screen does the same thing after a completed answer as before the first
 * one -it waits for the next question-. What ended the stream is in
 * `motivoCierre`, which is where US-028 reads `interrumpida` from.
 */
export type EstadoChat = 'inactivo' | 'generando' | 'cancelado' | 'fallido'

/**
 * Reduced card: the last event received plus what the client derives.
 *
 * `iniciadaEnMs` is the instant the announcement arrived, kept across the
 * states of the card so the interface can tell how long a card that never
 * resolved has been running. The server sends `transcurrido_ms` for the ones
 * that do resolve, and that one is authoritative.
 */
export interface TarjetaToolCall extends EventoToolCall {
  iniciadaEnMs: number
}

/**
 * Item of the thread, in arrival order, discriminated by `tipo`.
 *
 * The order of this array is what makes "the card appears before the number it
 * justifies" measurable: with the answer kept as a separate string there is no
 * index to compare against.
 */
export type ItemHilo
  = | { tipo: 'tarjeta', id: string, tarjeta: TarjetaToolCall }
    | { tipo: 'texto', id: string, texto: string }

/**
 * i18n key of each step of the stream.
 *
 * It exists so that the card of US-028 and the error notice of US-024 spell the
 * same step the same way. Without it one would print `verificacion_de_permiso`
 * raw and the other "Verificacion de permiso" on the same screen.
 */
export const CLAVE_PASO: Readonly<Record<PasoDelStream, string>> = Object.freeze({
  recuperacion_de_datos: 'chat.stream.step.dataRetrieval',
  verificacion_de_permiso: 'chat.stream.step.permissionCheck',
  generacion_de_texto: 'chat.stream.step.textGeneration',
  transporte: 'chat.stream.step.transport',
})

/**
 * i18n key of each state of the conversation, or null when there is no copy.
 *
 * `fallido` has none on purpose: the failure is announced by the error notice,
 * with its step and its code, and a second sentence saying "it failed" next to
 * it would be noise in the one state where the reader needs a single message.
 */
export const CLAVE_ESTADO_CHAT: Readonly<Record<EstadoChat, string | null>> = Object.freeze({
  inactivo: 'chat.stream.status.idle',
  generando: 'chat.stream.status.generating',
  cancelado: 'chat.stream.status.cancelled',
  fallido: null,
})

/** Source of the events behind the stream. The transport does not change. */
export type ProveedorDeChat = 'guionizado' | 'gemini'

/**
 * Provider the demonstration runs on today.
 *
 * It is a constant and not a runtime flag because the honesty of the demo
 * cannot depend on a value that may be missing: an undefined environment
 * variable would silently drop the notice, which is the one thing this constant
 * exists to prevent. The go/no-go of 15-ago-2026 flips this line and the notice
 * changes with it, in the interface and in the test that measures it.
 */
export const PROVEEDOR_DE_CHAT: ProveedorDeChat = 'guionizado'

/** i18n key of the permanent honesty notice, per provider. */
export const CLAVE_AVISO_DEMO: Readonly<Record<ProveedorDeChat, string>> = Object.freeze({
  guionizado: 'chat.demo.scriptedNotice',
  gemini: 'chat.demo.aiNotice',
})
