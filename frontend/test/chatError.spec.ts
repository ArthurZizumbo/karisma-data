import type { VueWrapper } from '@vue/test-utils'
import type { EventoError, EventoToolCall } from '~/types/chat'
import type { RolUsuario } from '~/types/sesion'

import { flushPromises, mount } from '@vue/test-utils'
import { afterEach, describe, expect, it, vi } from 'vitest'

import AvisoError from '~/components/chat/AvisoError.vue'
import { useChatStream } from '~/composables/useChatStream'
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
import { crearI18nDePrueba, mensaje } from './i18nDePrueba'

/**
 * US-024 — the typed error of the turn, and the retry that must not exist.
 *
 * What is measured here is measured nowhere else. That an `error` event does
 * not erase what already arrived, which is the one criterion written in the
 * negative and the one a refactor breaks first. That neither variant of the
 * notice renders anything activatable, which is cut #4 expressed as a DOM
 * assertion instead of as a paragraph in a document. That the two families
 * differ by more than their words, so a reader who does not finish the
 * sentence still knows whether asking again is worth anything. That the copy
 * the notice resolves through variables -its two headings, the level named
 * inside an English sentence- is copy the catalogues really have, which no
 * scanner of literals can see. And that the page mounts it at all: the block
 * inside `asistente.vue` is one element in a file two other User Stories were
 * rewriting the same night, and a notice nobody renders is a component with
 * green tests and no screen.
 *
 * The provider is not doubled and the copy is not invented: the catalogues are
 * the real ones and the failure is `_C4_PERMISO` field by field, so a test that
 * went green against a message the server never sends is not possible here.
 * That failure, its recoverable twin, the streaming server and the page harness
 * come from `dobles/chat.ts`, shared with the other chat suites; what stays here
 * is the notice mounted by hand, which is what this suite is about.
 */

const PRIMERA_TARJETA: EventoToolCall = tarjetaAnunciada('tc-1')

const SEGUNDA_TARJETA: EventoToolCall = tarjetaAnunciada('tc-2', 'agregar_serie')

/** Props of the notice, with the two the caller decides left open. */
function propsDelAviso(
  fallo: EventoError,
  nivelRequerido: RolUsuario | null = 'analista',
): Record<string, unknown> {
  return {
    paso: fallo.paso,
    clase: fallo.clase,
    codigo: fallo.codigo,
    mensajeClave: fallo.mensaje_clave,
    recuperable: fallo.recuperable,
    nivelRequerido,
  }
}

/** The notice mounted by hand, which this suite releases on its own. */
let montado: VueWrapper | null = null

function montarAviso(
  fallo: EventoError,
  nivelRequerido: RolUsuario | null = 'analista',
  idioma: 'es' | 'en' = 'es',
): VueWrapper {
  const wrapper = mount(AvisoError, {
    props: propsDelAviso(fallo, nivelRequerido),
    global: { plugins: [crearI18nDePrueba(idioma)], stubs: { Icon: true } },
  })
  montado = wrapper
  return wrapper
}

afterEach(() => {
  montado?.unmount()
  montado = null
  desmontarPaginas()
  vi.unstubAllGlobals()
})

describe('el error del turno no borra lo que ya llego', () => {
  it('conserva el hilo y el mapa de tarjetas al aplicar el evento error', async () => {
    // The defect this catches: a `reiniciar()`, a `hilo.value = []` or a
    // `tarjetas.value = new Map()` slipped into the `error` branch of the
    // reducer, which is the most natural thing to write when somebody decides
    // that a failed turn "starts over". The reader would lose the two cards
    // that explain WHY it failed at the exact moment they matter, and the only
    // assertion that exists on the other error path measures the length of a
    // one item thread, so nothing would go red.
    //
    // The comparison is by content and not only by length: a handler that
    // replaced the thread with two empty placeholders would keep the count.
    const servidor = servidorSSE()
    vi.stubGlobal('fetch', servidor.fetchFalso)

    const { estado, hilo, tarjetas, ultimoError, enviar } = useChatStream()
    const turno = enviar('exposicion agregada por contraparte')
    await flushPromises()

    servidor.entregar(
      marco('tool_call', PRIMERA_TARJETA)
      + marco('tool_call', SEGUNDA_TARJETA)
      + marco('token', { texto: 'Consultando la exposicion ', indice: 0 }),
    )
    await flushPromises()

    const antes = JSON.parse(JSON.stringify(hilo.value)) as unknown[]
    expect(antes).toHaveLength(3)
    expect([...tarjetas.value.keys()]).toEqual(['tc-1', 'tc-2'])

    servidor.entregar(marco('error', FALLO_DE_PERMISO))
    await flushPromises()

    // Without this the whole test would pass over a reducer that dropped the
    // event: nothing was erased because nothing was applied.
    expect(ultimoError.value).toEqual(FALLO_DE_PERMISO)

    expect(hilo.value).toHaveLength(3)
    expect(JSON.parse(JSON.stringify(hilo.value))).toEqual(antes)
    expect([...tarjetas.value.keys()]).toEqual(['tc-1', 'tc-2'])

    servidor.entregar(
      marco('done', { motivo: 'error', tokens_emitidos: 1, duracion_ms: 140 }),
    )
    servidor.cerrar()
    await turno

    // The close does not erase it either: the notice is drawn next to the
    // history that produced it, not instead of it.
    expect(estado.value).toBe('fallido')
    expect(hilo.value).toHaveLength(3)
    expect(JSON.parse(JSON.stringify(hilo.value))).toEqual(antes)
  })
})

describe('el aviso no ofrece reintento en ninguna de sus dos variantes', () => {
  it.each([
    ['permiso', FALLO_DE_PERMISO],
    ['recuperable', FALLO_RECUPERABLE],
  ] as const)('no renderiza ningun control activable con el fallo %s', (_familia, fallo) => {
    // The defect this catches: cut #4 walked back in as a button, a link or a
    // `[role=button]`, including a disabled one -offering a retry and refusing
    // it is still offering it-. It is the agreement most likely to be undone by
    // somebody who finds it trivial, and prose in a document cannot fail.
    const wrapper = montarAviso(fallo)

    expect(wrapper.findAll('button, a[href], [role=button]')).toHaveLength(0)
  })

  it('enuncia la via de salida solo cuando el fallo es recuperable', () => {
    // The defect this catches: showing the way out on a refusal. Telling
    // somebody whose role will not change to send the question again is the
    // same false promise as the button, written as a sentence, and it is the
    // one difference between the two variants that has to hold in the copy.
    const recuperable = montarAviso(FALLO_RECUPERABLE)
    expect(recuperable.text()).toContain(mensaje('es', 'chat.error.action.resend'))
    recuperable.unmount()

    const permiso = montarAviso(FALLO_DE_PERMISO)
    expect(permiso.text()).not.toContain(mensaje('es', 'chat.error.action.resend'))
  })
})

describe('las dos variantes se distinguen sin leer el texto', () => {
  it('expone data-recuperable, cambia de clases y anuncia el fallo en ambas', () => {
    // The defect this catches: two variants that render identically and only
    // differ in their sentence. The reader who scans would get no signal that
    // one failure is worth acting on and the other is not, and a notice without
    // `role=alert` is never announced at all -the screen reader stays on the
    // question while the answer silently dies-.
    const permiso = montarAviso(FALLO_DE_PERMISO)
    const raizPermiso = permiso.get('[data-prueba="aviso-error"]')
    const clasesPermiso = raizPermiso.classes()

    expect(raizPermiso.attributes('data-recuperable')).toBe('false')
    expect(raizPermiso.attributes('role')).toBe('alert')
    permiso.unmount()

    const recuperable = montarAviso(FALLO_RECUPERABLE)
    const raizRecuperable = recuperable.get('[data-prueba="aviso-error"]')

    expect(raizRecuperable.attributes('data-recuperable')).toBe('true')
    expect(raizRecuperable.attributes('role')).toBe('alert')
    expect(raizRecuperable.classes()).not.toEqual(clasesPermiso)
  })

  it('nombra el paso que fallo con la clave del vocabulario de US-023', () => {
    // The defect this catches: spelling the step here instead of resolving the
    // shared key. The card of US-028 and this notice would print the same step
    // two different ways on the same screen -one raw, one translated- which is
    // exactly what moving those four leaves to `chat.stream.step.*` prevented.
    const wrapper = montarAviso(FALLO_DE_PERMISO)

    expect(wrapper.get('[data-prueba="paso-fallido"]').text()).toBe(
      mensaje('es', 'chat.stream.step.permissionCheck'),
    )
    expect(wrapper.get('[data-prueba="codigo-error"]').text()).toBe('permisos_insuficientes')
  })
})

describe('el nivel exigido lo aporta la pantalla, no el contrato', () => {
  it('nombra el nivel cuando lo recibe y usa la copia generica cuando no', () => {
    // The defect this catches: interpolating a level that nobody supplied. The
    // contract freezes five fields and none of them carries it, so a notice
    // that always used `chat.error.message.permission` would render the slot
    // `{nivel}` raw or as a hole in the sentence -"requiere nivel  o
    // superior"- in front of a reader who is already being refused.
    const conNivel = montarAviso(FALLO_DE_PERMISO, 'analista')
    const textoConNivel = conNivel.get('[data-prueba="mensaje-error"]').text()

    expect(textoConNivel).toContain(mensaje('es', 'authz.role.analista'))
    expect(textoConNivel).not.toContain('{nivel}')
    conNivel.unmount()

    const sinNivel = montarAviso(FALLO_DE_PERMISO, null)

    expect(sinNivel.get('[data-prueba="mensaje-error"]').text()).toBe(
      mensaje('es', 'chat.error.message.permissionGeneric'),
    )
  })

  it('nombra ese nivel tambien dentro de la frase en ingles', () => {
    // The defect this catches: the English leaf of
    // `chat.error.message.permission` losing its `{nivel}` slot, or spelling it
    // `{level}`, which is what somebody writing English copy naturally types.
    // vue-i18n silently ignores a parameter the message does not name, so the
    // refusal renders whole and well formed while dropping the one piece of
    // information that tells the reader what to ask their administrator for.
    // `idioma.spec.ts` compares key sets and non-empty values and never looks
    // inside a message, and the case above renders in Spanish only.
    const wrapper = montarAviso(FALLO_DE_PERMISO, 'analista', 'en')
    const texto = wrapper.get('[data-prueba="mensaje-error"]').text()

    expect(texto).toContain(mensaje('en', 'authz.role.analista'))
    expect(texto).not.toMatch(/[{}]/)
  })
})

describe('el encabezado de cada familia sale del catalogo', () => {
  it('titula cada variante con su propia copia', () => {
    // The defect this catches: a typo in `chat.error.title.*`, or that leaf
    // renamed in the catalogues. Nobody watches those two keys: the notice
    // resolves them through a computed, so the scanner of `contratos.spec.ts`
    // -which only finds keys written as literals inside a `t('...')` call-
    // never sees them, and `idioma.spec.ts` compares the two catalogues
    // against each other, so a leaf renamed in both is renamed symmetrically
    // and stays green. The heading would print its own path,
    // `chat.error.title.permission`, in Spanish and in English alike.
    //
    // It also catches the two families sharing one heading: a recoverable
    // failure titled as a refusal tells a reader who only has to ask again
    // that their access level is the problem.
    const permiso = montarAviso(FALLO_DE_PERMISO)
    expect(permiso.text()).toContain(mensaje('es', 'chat.error.title.permission'))
    permiso.unmount()

    const recuperable = montarAviso(FALLO_RECUPERABLE)
    expect(recuperable.text()).toContain(mensaje('es', 'chat.error.title.recoverable'))
  })
})

describe('la pantalla monta el aviso fuera de la lista de mensajes', () => {
  it('lo dibuja al fallar el turno, con el nivel que aporta la pantalla', async () => {
    // The defect this catches: the integration inside `asistente.vue` going
    // away or being wired wrong. It is one element and one `v-if` in a page
    // two other User Stories were rewriting the same night, and no test drives
    // a failing turn against the DOM: `chatStream.spec.ts` mounts the page but
    // asserts the failure over the refs of the composable, and the cases above
    // mount the notice by hand with props nobody has to bind. Delete the
    // element, delete its `v-if`, or cross `:mensaje-clave` with `:codigo`,
    // and the reader whose turn just died is told nothing at all while every
    // suite stays green -and A4 loses the capture of the error state-.
    //
    // Outside the log and not inside it, because the error of the *turn* is
    // not the error of a card: US-028 paints a broken tool by id inside the
    // list, and a notice drawn in there would compete with it and read as one
    // more message of an answer that is not coming.
    const servidor = servidorSSE()
    vi.stubGlobal('fetch', servidor.fetchFalso)

    const wrapper = await montarPagina()
    expect(wrapper.find('[data-prueba="aviso-error"]').exists()).toBe(false)

    await preguntar(wrapper, 'exposicion agregada por contraparte')
    servidor.entregar(
      marco('error', FALLO_DE_PERMISO)
      + marco('done', { motivo: 'error', tokens_emitidos: 0, duracion_ms: 40 }),
    )
    servidor.cerrar()
    await flushPromises()

    expect(wrapper.findAll('[data-prueba="aviso-error"]')).toHaveLength(1)
    expect(wrapper.get('[data-prueba="hilo"]').find('[data-prueba="aviso-error"]').exists())
      .toBe(false)

    // The level is a constant of this screen and never a field of the event,
    // so a lost `:nivel-requerido` falls back to the generic copy and this is
    // the only place where that binding is exercised at all.
    expect(wrapper.get('[data-prueba="mensaje-error"]').text())
      .toContain(mensaje('es', 'authz.role.analista'))
    expect(wrapper.get('[data-prueba="codigo-error"]').text()).toBe('permisos_insuficientes')
  })
})
