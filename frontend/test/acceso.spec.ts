import type { VueWrapper } from '@vue/test-utils'
import type { Ref } from 'vue'

import { flushPromises, mount } from '@vue/test-utils'
import { defineComponent, ref } from 'vue'
import { createMemoryHistory, createRouter } from 'vue-router'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import Acceso from '~/pages/acceso.vue'
import { RUTA_ACCESO } from '~/utils/navegacion'
import { destinoPorRol, ROLES } from '~/utils/sesion'
import { type CodigoIdioma, crearI18nDePrueba, mensaje } from './i18nDePrueba'

/**
 * US-015 — the entry screen.
 *
 * What is pinned here is the behaviour the screen promises and nothing about
 * how it is laid out: US-UX-07 may recompose this page on 15-ago and fixing its
 * markup would manufacture exactly the scaffolding debt this User Story
 * removes. What cannot change without breaking the product is that the five
 * designed states exist, that the message never tells apart what the backend
 * deliberately kept neutral, that the message is the one of the reader's
 * language and not the one the API sent, and that each role lands where it
 * belongs.
 */

/** Session the doubled Nitro route answers with. */
const SESION_OPERATIVA = { usuario: 'lmendez', nombre: 'Laura Méndez', rol: 'operativo' }

const router = createRouter({
  history: createMemoryHistory(),
  routes: [{ path: RUTA_ACCESO, component: defineComponent({ template: '<div />' }) }],
})

let peticiones: { ruta: string, cuerpo: unknown }[]
let navegaciones: string[]
let responder: (ruta: string, cuerpo: unknown) => Promise<unknown>

/** Fresh useState store per test, so no session leaks into the next one. */
let estados: Map<string, Ref<unknown>>

beforeEach(() => {
  peticiones = []
  navegaciones = []
  estados = new Map<string, Ref<unknown>>()
  responder = () => Promise.resolve(SESION_OPERATIVA)

  vi.stubGlobal('definePageMeta', () => undefined)
  vi.stubGlobal('useRuntimeConfig', () => ({ public: { entorno: 'prueba', demoAcceso: true } }))
  vi.stubGlobal('useState', (clave: string, inicial?: () => unknown) => {
    if (!estados.has(clave)) {
      estados.set(clave, ref(inicial?.() ?? null))
    }
    return estados.get(clave)!
  })
  vi.stubGlobal('navigateTo', (destino: string) => {
    navegaciones.push(destino)
    return Promise.resolve()
  })
  vi.stubGlobal('$fetch', (ruta: string, opciones: { body?: unknown } = {}) => {
    peticiones.push({ ruta, cuerpo: opciones.body })
    return responder(ruta, opciones.body)
  })

  return () => {
    vi.unstubAllGlobals()
  }
})

/** Mounts the screen on the entry route, optionally with a query and a locale. */
async function montarAcceso(
  opciones: { idioma?: CodigoIdioma, consulta?: Record<string, string> } = {},
): Promise<VueWrapper> {
  await router.push({ path: RUTA_ACCESO, query: opciones.consulta ?? {} })
  await router.isReady()

  return mount(Acceso, {
    global: {
      plugins: [router, crearI18nDePrueba(opciones.idioma ?? 'es')],
      stubs: { Icon: true },
    },
  })
}

/** Types a complete pair of credentials and sends the form. */
async function entrar(wrapper: VueWrapper, contrasena = 'clave-de-prueba'): Promise<void> {
  await wrapper.get('[data-campo="usuario"]').setValue('lmendez')
  await wrapper.get('[data-campo="contrasena"]').setValue(contrasena)
  await wrapper.get('form').trigger('submit')
}

/** Makes the next request fail with a given HTTP status. */
function fallarCon(estado: number, datos: unknown = {}): void {
  responder = () => Promise.reject(Object.assign(new Error('fallo'), { status: estado, data: datos }))
}

describe('los cinco estados de la pantalla de entrada existen', () => {
  it('empieza en el estado normal', async () => {
    const wrapper = await montarAcceso()

    expect(wrapper.get('[data-estado]').attributes('data-estado')).toBe('normal')
  })

  it('marca el campo invalido sin llegar al servidor', async () => {
    // A request per empty field is the reflex implementation, and it turns a
    // typo into a round trip and into a message about credentials for something
    // the screen already knew.
    const wrapper = await montarAcceso()

    await wrapper.get('form').trigger('submit')

    expect(wrapper.get('[data-estado]').attributes('data-estado')).toBe('campo-invalido')
    expect(peticiones).toHaveLength(0)
  })

  it('se declara cargando mientras la peticion viaja', async () => {
    // Without this state the reader presses again, and a second attempt with a
    // correct password lands on a screen that already navigated away.
    let liberar: (sesion: unknown) => void = () => undefined
    responder = () => new Promise((resolver) => {
      liberar = resolver
    })
    const wrapper = await montarAcceso()

    await entrar(wrapper)

    expect(wrapper.get('[data-estado]').attributes('data-estado')).toBe('cargando')
    expect(wrapper.get('[data-accion="entrar"]').attributes('disabled')).toBeDefined()

    liberar(SESION_OPERATIVA)
    await flushPromises()
  })

  it('declara la credencial invalida cuando el servidor responde 401', async () => {
    fallarCon(401)
    const wrapper = await montarAcceso()

    await entrar(wrapper)
    await flushPromises()

    expect(wrapper.get('[data-estado]').attributes('data-estado')).toBe('credencial-invalida')
    expect(navegaciones).toEqual([])
  })

  it('explica la sesion caducada cuando la guarda manda ese motivo', async () => {
    // The state that usually goes undesigned. Without it a reader whose session
    // expired lands on an ordinary form and reads it as having been logged out
    // for no reason, or as having typed something wrong.
    const wrapper = await montarAcceso({ consulta: { motivo: 'expirada' } })

    expect(wrapper.get('[data-estado]').attributes('data-estado')).toBe('sesion-expirada')
    expect(wrapper.get('[data-aviso="expirada"]').text()).toContain(
      mensaje('es', 'access.expired.title'),
    )
  })
})

describe('el mensaje de credenciales', () => {
  it('es el mismo sea cual sea el fallo, como el 401 del backend', async () => {
    // The backend answers the same body for an unknown user, a wrong password
    // and a disabled account. A screen that told them apart would undo that
    // neutrality from the other side of the wire.
    const mensajes: string[] = []

    for (const datos of [
      { detail: 'Credenciales incorrectas', codigo: 'credenciales_invalidas' },
      { detail: 'Usuario no encontrado' },
      { detail: 'Usuario deshabilitado' },
    ]) {
      fallarCon(401, datos)
      const wrapper = await montarAcceso()
      await entrar(wrapper)
      await flushPromises()
      mensajes.push(wrapper.get('[data-aviso="error"]').text())
    }

    expect(new Set(mensajes).size).toBe(1)
    expect(mensajes[0]).toBe(mensaje('es', 'access.errors.credentials'))
  })

  it('se lee en el idioma de la interfaz y no en el del backend', async () => {
    // The literal `Credenciales incorrectas` is fixed by the acceptance
    // criteria on the API side. Painting the `detail` would drop Spanish into
    // the English interface, which is the defect this assertion exists for.
    fallarCon(401, { detail: 'Credenciales incorrectas', codigo: 'credenciales_invalidas' })
    const wrapper = await montarAcceso({ idioma: 'en' })

    await entrar(wrapper)
    await flushPromises()

    expect(wrapper.get('[data-aviso="error"]').text()).toBe('Incorrect credentials')
    expect(wrapper.text()).not.toContain('Credenciales incorrectas')
  })

  it('distingue un fallo del servidor de una credencial rechazada', async () => {
    // Telling somebody to check a password that was in fact correct sends them
    // to reset a credential that never failed.
    fallarCon(502)
    const wrapper = await montarAcceso()

    await entrar(wrapper)
    await flushPromises()

    expect(wrapper.get('[data-aviso="error"]').text()).toBe(mensaje('es', 'access.errors.server'))
    expect(wrapper.get('[data-estado]').attributes('data-estado')).toBe('normal')
  })
})

describe('el selector de demostracion', () => {
  it('ofrece los cuatro roles con la etiqueta de honestidad', async () => {
    // Both halves are acceptance criteria: losing a role leaves a profile with
    // no way in, and losing the label leaves a credential-free door with
    // nothing saying so.
    const wrapper = await montarAcceso()

    const botones = wrapper.findAll('[data-rol]')

    expect(botones.map(boton => boton.attributes('data-rol'))).toEqual([...ROLES])
    expect(wrapper.get('[data-demostracion]').text()).toContain(
      mensaje('es', 'access.demo.label'),
    )
  })

  it('rotula la puerta tambien en ingles', async () => {
    const wrapper = await montarAcceso({ idioma: 'en' })

    expect(wrapper.get('[data-demostracion]').text()).toContain(
      mensaje('en', 'access.demo.label'),
    )
  })

  it('avisa cuando la puerta esta apagada en el backend', async () => {
    fallarCon(404)
    const wrapper = await montarAcceso()

    await wrapper.get('[data-rol="analista"]').trigger('click')
    await flushPromises()

    // Drawn as the fourth unhappy state of the design system and not as an
    // error: the door is shut by configuration and retrying changes nothing.
    expect(wrapper.get('[data-aviso="sin-permiso"]').text()).toBe(
      mensaje('es', 'access.errors.demoDisabled'),
    )
  })
})

describe('cada perfil aterriza donde le toca', () => {
  it.each([...ROLES])('lleva a %s a su pantalla inicial', async (rol) => {
    // A landing route that does not match the role sends the reader to a screen
    // their profile was not designed for, and with US-017 in place, to a guard
    // that bounces them straight back here.
    responder = (ruta, cuerpo) => Promise.resolve({ ...SESION_OPERATIVA, rol, ruta, cuerpo })
    const wrapper = await montarAcceso()

    await wrapper.get(`[data-rol="${rol}"]`).trigger('click')
    await flushPromises()

    expect(peticiones).toEqual([{ ruta: '/api/auth/demo', cuerpo: { rol } }])
    expect(navegaciones).toEqual([destinoPorRol(rol)])
  })

  it('manda las credenciales tecleadas a la ruta de Nitro y no al backend', async () => {
    const wrapper = await montarAcceso()

    await entrar(wrapper)
    await flushPromises()

    expect(peticiones).toEqual([
      { ruta: '/api/auth/token', cuerpo: { usuario: 'lmendez', contrasena: 'clave-de-prueba' } },
    ])
    expect(navegaciones).toEqual([destinoPorRol('operativo')])
  })
})

describe('la contrasena no se queda escrita en la pagina', () => {
  it('no la publica como atributo del marcado', async () => {
    // With `:value` instead of `v-model` the typed password becomes an
    // attribute, and server side rendering would serialise it into the HTML.
    const clave = 'contrasena-que-no-debe-quedarse'
    fallarCon(401)
    const wrapper = await montarAcceso()

    await entrar(wrapper, clave)
    await flushPromises()

    expect(wrapper.html()).not.toContain(clave)
  })
})

describe('la pantalla sigue cumpliendo el contrato de navegacion', () => {
  it('se titula con la accion que pide, no con la rama del mapa', async () => {
    // This is the assertion that replaces the scaffolding one retired from
    // pantallas.spec.ts: /acceso left the list that measures every h1 against
    // the A3 branch, so without this line nothing would notice a heading that
    // went back to a loose literal or to a key the catalogue does not have.
    //
    // Its `data-ruta` and its single h1 are NOT re-asserted here: pantallas.spec.ts
    // still iterates the whole contract for both, /acceso included, and a second
    // copy is the kind that survives after the first one stops being true.
    const wrapper = await montarAcceso()

    expect(wrapper.get('h1').text()).toBe(mensaje('es', 'access.title'))
  })
})
