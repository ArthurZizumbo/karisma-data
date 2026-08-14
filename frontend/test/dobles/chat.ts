import type { VueWrapper } from '@vue/test-utils'
import type { EventoError, EventoToolCall } from '~/types/chat'
import type { CodigoIdioma } from '../i18nDePrueba'

import { flushPromises, mount } from '@vue/test-utils'
import { defineComponent } from 'vue'
import { createMemoryHistory, createRouter } from 'vue-router'
import { vi } from 'vitest'

import Asistente from '~/pages/asistente.vue'
import { RUTA_ASISTENTE, RUTA_INDICE, RUTAS_CONTRATO } from '~/utils/navegacion'
import { crearI18nDePrueba } from '../i18nDePrueba'

/**
 * Doubles and fixtures shared by the three chat suites.
 *
 * Extracted from `chatStream.spec.ts` and `chatError.spec.ts`, which carried
 * the same SSE server, the same framing helper, the same two typed failures and
 * the same page harness in two copies. The duplication was declared and
 * deliberate while three User Stories were writing the same tree on the same
 * day -editing a spec of another owner was the larger risk- and this module is
 * the destination that decision named.
 *
 * What is doubled here is the network and only the network. The composable, the
 * reducer, the page and the catalogues run for real, because that is where the
 * defects live.
 */

/** One SSE frame, framed exactly as `chat_stream.formatear_evento` writes it. */
export function marco(nombre: string, datos: unknown): string {
  return `event: ${nombre}\ndata: ${JSON.stringify(datos)}\n\n`
}

/** What one read of the body resolves with. */
export interface Trozo {
  done: boolean
  value?: Uint8Array
}

/**
 * A server that streams, so that cancelling it means something.
 *
 * The read is kept in flight until it is fed or aborted. A double that resolved
 * the whole body at once would make every assertion pass over a client that
 * never streamed and never aborted, and it would apply an error and its close
 * in the same tick, leaving no state in between to compare against.
 */
export function servidorSSE() {
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

/**
 * An announced card, with the id and the tool left to the caller.
 *
 * The two suites used to hardcode their own ids -`tc-1` and `c1`- for the same
 * fixture. Building it keeps the id at the call site, where it is read, and
 * stops a shared constant from tying two suites to one identifier.
 */
export function tarjetaAnunciada(
  id: string,
  herramienta: string = 'consultar_metrica',
): EventoToolCall {
  return {
    id,
    estado: 'anuncio',
    herramienta,
    etiqueta: `chat.toolCall.tool.${herramienta}`,
    transcurrido_ms: null,
    resultado: null,
    fuente: null,
    paso: null,
  }
}

/**
 * The typed failure C4 of the script sends, field by field.
 *
 * Copied from `_C4_PERMISO` of `proveedores/guionizado.py` and not invented: it
 * is the material the notice is written against, so a suite that went green
 * against a message the server never sends is not possible here.
 */
export const FALLO_DE_PERMISO: EventoError = {
  paso: 'verificacion_de_permiso',
  clase: 'permiso',
  codigo: 'permisos_insuficientes',
  mensaje_clave: 'chat.error.message.permission',
  recuperable: false,
}

/**
 * The recoverable failure C3 sends, which is the other half of the material.
 *
 * A silo that did not answer, at the step that asked it: the only thing that
 * tells this failure apart from a dropped socket.
 */
export const FALLO_RECUPERABLE: EventoError = {
  paso: 'recuperacion_de_datos',
  clase: 'recuperable',
  codigo: 'silo_no_disponible',
  mensaje_clave: 'chat.error.message.recoverable',
  recuperable: true,
}

/** Wrappers mounted through this module, so a suite can release them all. */
const montados: VueWrapper[] = []

/**
 * The assistant screen, framed the way Nuxt frames it.
 *
 * `definePageMeta` is a macro the Nuxt plugin compiles away and that does not
 * exist here, and the page titles itself with its own route: both are supplied
 * so that a failure to mount is a failure of the page and not of the harness.
 */
export async function montarPagina(idioma: CodigoIdioma = 'es'): Promise<VueWrapper> {
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
  montados.push(wrapper)
  return wrapper
}

/** Types a question and submits it, the way the reader does. */
export async function preguntar(wrapper: VueWrapper, texto: string): Promise<void> {
  await wrapper.get('[data-prueba="pregunta"]').setValue(texto)
  await wrapper.get('form').trigger('submit')
  await flushPromises()
}

/**
 * Releases every page this module mounted, and only those.
 *
 * Mounted components outlive their test unless somebody unmounts them, and the
 * page under test owns an interval and an abort controller: a suite that leaked
 * one would keep a clock ticking into the next case. It empties the registry as
 * it goes, so calling it twice -or calling it mid case and again on teardown-
 * never unmounts the same wrapper twice.
 *
 * Global stubs are deliberately left alone. A case that renders the same page
 * once per language has to release the first mount while its `fetch` double is
 * still in place, so unstubbing belongs to the `afterEach` of each suite and
 * not here.
 */
export function desmontarPaginas(): void {
  while (montados.length > 0) {
    montados.pop()?.unmount()
  }
}
