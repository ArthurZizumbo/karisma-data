import type { Ref } from 'vue'

import { ref } from 'vue'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { esFalloDeAcceso, useSesion } from '~/composables/useSesion'
import { RUTAS_CONTRATO } from '~/utils/navegacion'
import { aSesionUsuario, destinoPorRol, esRolUsuario, estadoDeFallo, ROLES } from '~/utils/sesion'

/**
 * US-015 — the pure half of the session, which both sides of the proxy share.
 *
 * Nothing here mounts a component or opens a connection: these are the three
 * rules that decide where a login lands, what counts as a role and what a
 * failed request actually said, and each of them breaks silently.
 */

describe('el destino de cada rol existe de verdad', () => {
  it('manda a los cuatro roles a una ruta del contrato', () => {
    // A landing route that no page file serves turns a correct login into a
    // 404: the reader types the right password and the product looks broken on
    // the very first click.
    for (const rol of ROLES) {
      expect(RUTAS_CONTRATO, rol).toContain(destinoPorRol(rol))
    }
  })

  it('no manda dos roles al mismo sitio', () => {
    // Two roles sharing a landing screen is the shape the table takes when
    // somebody copies a line and forgets to change it, and it silently undoes
    // the whole point of routing by profile.
    const destinos = ROLES.map(destinoPorRol)

    expect(new Set(destinos).size).toBe(ROLES.length)
  })
})

describe('el vocabulario de roles es el del backend', () => {
  it('nombra los cuatro scopes con la grafia del backend', () => {
    // The four literals are contract with the JWT `scope` claim, not a local
    // preference: a plural, an accent or a capital here and the session stops
    // matching the tokens the API signs.
    //
    // Deliberately not asserted next to this: that ROLES passes esRolUsuario.
    // The guard is implemented as `ROLES.includes(...)`, so that expectation
    // could not fail under any edit and would buy coverage without meaning.
    expect([...ROLES]).toEqual(['operativo', 'analista', 'directivo', 'admin'])
  })

  it('rechaza administrador', () => {
    // `RolSugerido` of the navigation contract spells the fourth role
    // `administrador` while the JWT scope says `admin`. Letting that spelling
    // into a session would produce a role with no landing route.
    expect(esRolUsuario('administrador')).toBe(false)
  })

  it.each([undefined, null, '', 'ADMIN', 'Analista', 7, ['admin']])(
    'rechaza %s como rol',
    (valor) => {
      expect(esRolUsuario(valor)).toBe(false)
    },
  )
})

describe('el perfil de /api/auth/me se valida antes de convertirse en sesion', () => {
  it('traduce los tres campos que la interfaz usa', () => {
    const sesion = aSesionUsuario({
      id: 'no-importa',
      username: 'lmendez',
      full_name: 'Laura Méndez',
      role: 'operativo',
      disabled: false,
    })

    expect(sesion).toEqual({ usuario: 'lmendez', nombre: 'Laura Méndez', rol: 'operativo' })
  })

  it.each([
    [{ username: 'movalle', full_name: 'Mariana Ovalle', role: 'administrador' }],
    [{ username: '', full_name: 'Sin nombre', role: 'admin' }],
    [{ full_name: 'Sin usuario', role: 'admin' }],
    [null],
  ])('rechaza %o', (perfil) => {
    // Casting instead of validating would hand the screen a role it cannot
    // route, and the failure would surface as a navigation to `undefined`
    // several screens away from the cause.
    expect(() => aSesionUsuario(perfil)).toThrow()
  })

  it('usa el nombre de usuario cuando el perfil no trae nombre legible', () => {
    // The alternative is a blank space in the chrome where a person should be.
    const sesion = aSesionUsuario({ username: 'eruiz', full_name: '', role: 'operativo' })

    expect(sesion.nombre).toBe('eruiz')
  })
})

describe('useSesion, que es lo que US-017 consume el miercoles', () => {
  let estados: Map<string, Ref<unknown>>
  let peticiones: string[]
  let responder: (ruta: string) => Promise<unknown>

  beforeEach(() => {
    estados = new Map<string, Ref<unknown>>()
    peticiones = []
    responder = () => Promise.resolve({})

    vi.stubGlobal('useState', (clave: string, inicial?: () => unknown) => {
      if (!estados.has(clave)) {
        estados.set(clave, ref(inicial?.() ?? null))
      }
      return estados.get(clave)!
    })
    vi.stubGlobal('$fetch', (ruta: string) => {
      peticiones.push(ruta)
      return responder(ruta)
    })
  })

  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('lee la sesion que la cookie ya trae', async () => {
    responder = () => Promise.resolve({
      username: 'dhernandez',
      full_name: 'Diego Hernández',
      role: 'analista',
    })
    const { sesion, cargarSesion, cargando } = useSesion()

    await cargarSesion()

    expect(peticiones).toEqual(['/api/auth/me'])
    expect(sesion.value).toEqual({
      usuario: 'dhernandez',
      nombre: 'Diego Hernández',
      rol: 'analista',
    })
    expect(cargando.value).toBe(false)
  })

  it('no convierte en error la visita sin cookie', async () => {
    // A first visit has no session and that is not a failure. Letting the 401
    // escape would push the guard of US-017 into an error screen on the most
    // ordinary path there is: opening the portal for the first time.
    responder = () => Promise.reject(Object.assign(new Error('Unauthorized'), { status: 401 }))
    const { sesion, cargarSesion } = useSesion()

    await expect(cargarSesion()).resolves.toBeUndefined()
    expect(sesion.value).toBeNull()
  })

  it('olvida la sesion aunque la salida falle', async () => {
    // Leaving the name of the previous reader on screen because the network
    // hiccuped is worse than a cookie that outlives the click, and the cookie
    // is dropped by the same request.
    responder = () => Promise.resolve({ usuario: 'movalle', nombre: 'Mariana Ovalle', rol: 'admin' })
    const { sesion, iniciarSesion, cerrarSesion } = useSesion()
    await iniciarSesion({ usuario: 'movalle', contrasena: 'clave-de-prueba' })
    expect(sesion.value).not.toBeNull()

    responder = () => Promise.reject(new Error('sin red'))
    await expect(cerrarSesion()).rejects.toThrow()

    expect(sesion.value).toBeNull()
  })

  it.each([
    [401, 'credenciales'],
    [404, 'demo-deshabilitado'],
    [502, 'servidor'],
  ])('traduce el %i en el motivo %s', async (estado, motivo) => {
    // Reporting a 502 as a rejected credential sends the reader to reset a
    // password that never failed; reporting a 401 as a server fault tells them
    // to wait for something that will never fix itself.
    responder = () => Promise.reject(Object.assign(new Error('fallo'), { status: estado }))
    const { iniciarSesionDemo, sesion } = useSesion()

    await expect(iniciarSesionDemo('directivo')).rejects.toSatisfy(
      error => esFalloDeAcceso(error) && error.motivo === motivo,
    )
    expect(sesion.value).toBeNull()
  })
})

describe('el estado de un fallo se lee venga como venga', () => {
  it.each([
    [{ status: 401 }, 401],
    [{ statusCode: 401 }, 401],
    [{ response: { status: 404 } }, 404],
    [new Error('conexion rechazada'), 0],
  ])('lee %o como %i', (error, esperado) => {
    // ofetch reports it as `status`, h3 as `statusCode` and a bare Response as
    // `response.status`. Reading only one of the three turns an expected 401
    // into a generic server error, and the screen tells the reader to try again
    // later when what they actually mistyped was the password.
    expect(estadoDeFallo(error)).toBe(esperado)
  })
})
