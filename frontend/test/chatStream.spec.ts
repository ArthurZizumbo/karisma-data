import type { VueWrapper } from '@vue/test-utils'
import type { ControlDeChat } from '~/composables/useChatStream'
import type { EventoError, EventoToolCall } from '~/types/chat'

import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'

import { flushPromises, mount } from '@vue/test-utils'
import { defineComponent, h } from 'vue'
import { createMemoryHistory, createRouter } from 'vue-router'
import { afterEach, describe, expect, it, vi } from 'vitest'

import {
  analizarTramos,
  CLAVE_FALLO_DE_TRANSPORTE,
  RUTA_CHAT,
  useChatStream,
} from '~/composables/useChatStream'
import { usePermisos } from '~/composables/usePermisos'
import Asistente from '~/pages/asistente.vue'
import { CLAVE_AVISO_DEMO, CLAVE_ESTADO_CHAT, CLAVE_PASO, PROVEEDOR_DE_CHAT } from '~/types/chat'
import { RUTA_ACCESO, RUTA_ASISTENTE, RUTA_INDICE, RUTAS_CONTRATO } from '~/utils/navegacion'
import { MOTIVO_EXPIRADA } from '~/utils/sesion'
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

/** One SSE frame, framed exactly as `chat_stream.formatear_evento` writes it. */
function marco(nombre: string, datos: unknown): string {
  return `event: ${nombre}\ndata: ${JSON.stringify(datos)}\n\n`
}

const ANUNCIO: EventoToolCall = {
  id: 'c1',
  estado: 'anuncio',
  herramienta: 'consultar_metrica',
  etiqueta: 'chat.toolCall.tool.consultar_metrica',
  transcurrido_ms: null,
  resultado: null,
  fuente: null,
  paso: null,
}

const RESUELTA: EventoToolCall = {
  ...ANUNCIO,
  estado: 'resultado',
  transcurrido_ms: 260,
  resultado: { columnas: ['metrica', 'valor'], filas: [['morosidad', '3.42 %']], cifra: '3.42 %' },
  fuente: 'catalogo.creditos.morosidad_cartera',
}

const SEGUNDA_TARJETA: EventoToolCall = {
  ...ANUNCIO,
  id: 'c2',
  herramienta: 'agregar_serie',
  etiqueta: 'chat.toolCall.tool.agregar_serie',
}

/**
 * The typed failure C4 of the script sends, field by field.
 *
 * Copied from `_C4_PERMISO` and not invented: it is the material US-024 writes
 * its notice against, so a client that mangled it would otherwise be measured
 * against something the server never sends.
 */
const FALLO_DE_PERMISO: EventoError = {
  paso: 'verificacion_de_permiso',
  clase: 'permiso',
  codigo: 'permisos_insuficientes',
  mensaje_clave: 'chat.error.message.permission',
  recuperable: false,
}

/** A request the endpoint refuses before any stream is opened. */
function servidorQueRechaza(estadoHttp: number) {
  return vi.fn(() => Promise.resolve({ ok: false, status: estadoHttp, body: null }))
}

/** What one read of the body resolves with. */
interface Trozo {
  done: boolean
  value?: Uint8Array
}

/**
 * A server that streams, so that cancelling it means something.
 *
 * A double that resolved the whole body at once would make every assertion
 * below pass over a client that never streamed and never aborted.
 */
function servidorSSE() {
  const codificador = new TextEncoder()
  const pendientes: Trozo[] = []
  let esperando: ((trozo: Trozo) => void) | null = null
  let senal: AbortSignal | null = null
  let cancelaciones = 0

  function empujar(trozo: Trozo): void {
    if (esperando !== null) {
      const entregarAhora = esperando
      esperando = null
      entregarAhora(trozo)
      return
    }
    pendientes.push(trozo)
  }

  const lector = {
    read: (): Promise<Trozo> =>
      new Promise<Trozo>((resolver, rechazar) => {
        const listo = pendientes.shift()
        if (listo !== undefined) {
          resolver(listo)
          return
        }
        esperando = resolver
        senal?.addEventListener(
          'abort',
          () => {
            // What a real body does when its request is aborted: the read in
            // flight rejects instead of hanging forever.
            rechazar(Object.assign(new Error('peticion abortada'), { name: 'AbortError' }))
          },
          { once: true },
        )
      }),
    cancel: async (): Promise<void> => {
      cancelaciones += 1
    },
  }

  const fetchFalso = vi.fn((_ruta: string, opciones: RequestInit) => {
    senal = opciones.signal ?? null
    return Promise.resolve({ ok: true, status: 200, body: { getReader: () => lector } })
  })

  return {
    fetchFalso,
    /** Delivers one chunk of the body, of any size and cut anywhere. */
    entregar: (trozo: string) => empujar({ done: false, value: codificador.encode(trozo) }),
    /** Ends the body the way a completed answer does. */
    cerrar: () => empujar({ done: true }),
    senal: () => senal,
    cancelaciones: () => cancelaciones,
  }
}

let montado: VueWrapper | null = null

async function montarPagina(idioma: 'es' | 'en' = 'es'): Promise<VueWrapper> {
  vi.stubGlobal('definePageMeta', () => undefined)

  const router = createRouter({
    history: createMemoryHistory(),
    routes: [RUTA_INDICE, ...RUTAS_CONTRATO].map(path => ({
      path,
      component: defineComponent({ template: '<div />' }),
    })),
  })
  await router.push(RUTA_ASISTENTE)
  await router.isReady()

  const wrapper = mount(Asistente, {
    global: {
      plugins: [router, crearI18nDePrueba(idioma)],
      stubs: { Icon: true },
    },
  })
  montado = wrapper
  return wrapper
}

/** Types a question and submits it, the way the reader does. */
async function preguntar(wrapper: VueWrapper, texto: string): Promise<void> {
  await wrapper.get('[data-prueba="pregunta"]').setValue(texto)
  await wrapper.get('form').trigger('submit')
  await flushPromises()
}

afterEach(() => {
  montado?.unmount()
  montado = null
  vi.unstubAllGlobals()
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
      mensaje_clave: CLAVE_FALLO_DE_TRANSPORTE,
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

      wrapper.unmount()
      montado = null
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

  it('separa la copia del fallo de transporte de la del fallback', () => {
    // US-024 deletes `chat.stream.errorFallback` in the same commit in which it
    // mounts `AvisoError`. A dropped connection or a refused request is not
    // provisional and will keep happening after that, so if both pointed at the
    // same leaf every network failure would lose its copy on somebody else's
    // commit -and nothing here would have failed.
    expect(CLAVE_FALLO_DE_TRANSPORTE).not.toBe('chat.stream.errorFallback')
    expect(mensaje('es', CLAVE_FALLO_DE_TRANSPORTE))
      .not.toBe(mensaje('es', 'chat.stream.errorFallback'))
  })
})
