import type { RouteLocationRaw } from 'vue-router'
import type { BloqueoDeRuta } from '~/types/guarda'
import type { RolUsuario, SesionUsuario } from '~/types/sesion'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { usePermisos } from '~/composables/usePermisos'
import {
  decidirGuarda,
  destinoDeRetorno,
  esRutaPublica,
  MOTIVO_SESION_REQUERIDA,
  PARAMETRO_DESTINO,
  rolAlcanza,
  RUTAS_PUBLICAS,
} from '~/utils/guarda'
import {
  RUTA_ACCESO,
  RUTA_ASISTENTE,
  RUTA_GUIA,
  RUTA_INDICE,
  RUTAS_CONTRATO,
} from '~/utils/navegacion'
import { MOTIVO_EXPIRADA, ROLES } from '~/utils/sesion'

/**
 * US-017 — the session guard, in its two halves.
 *
 * The decision is a pure function and the middleware is glue, and they are
 * tested apart because they fail apart: the first fails by deciding wrong, the
 * second by wiring the decision to the wrong effect. Nothing here starts Nuxt;
 * the project has no @nuxt/test-utils and a User Story of half a point is not
 * the place to add it.
 */

/** Routes of the product, which is every contract route except the entry one. */
const RUTAS_DE_PRODUCTO = RUTAS_CONTRATO.filter(ruta => ruta !== RUTA_ACCESO)

function sesionDe(rol: RolUsuario): SesionUsuario {
  return { usuario: 'dhernandez', nombre: 'Diego Hernandez', rol }
}

describe('decidirGuarda: sin sesion no se entra al producto', () => {
  it.each(RUTAS_DE_PRODUCTO)('rebota %s a la pantalla de acceso', (ruta) => {
    // The candidate to be forgotten is /asistente: it is a contract route and
    // it is NOT a branch of MODULOS, so a guard written from the sidebar would
    // leave it open.
    const decision = decidirGuarda({
      ruta,
      sesion: null,
      habiaSesion: false,
      scopeExigido: null,
    })

    expect(decision).toEqual({
      tipo: 'redirigir',
      destino: RUTA_ACCESO,
      motivo: MOTIVO_SESION_REQUERIDA,
      rutaPedida: ruta,
    })
  })

  it.each([RUTA_INDICE, RUTA_ACCESO, RUTA_GUIA])('deja pasar la ruta publica %s', (ruta) => {
    // Guarding /acceso would redirect it to itself forever, and closing / and
    // /guia would put a login in front of the two artefacts the A4 rubric
    // grades directly.
    expect(
      decidirGuarda({ ruta, sesion: null, habiaSesion: false, scopeExigido: null }),
    ).toEqual({ tipo: 'permitir' })
  })

  it('deja pasar cualquier subruta de la guia de estilos', () => {
    // With an equality comparison a plate of the guide would be guarded while
    // its index is public, which is the sort of half-open door nobody notices
    // until the demo.
    expect(esRutaPublica(`${RUTA_GUIA}/lo-que-sea`)).toBe(true)
    expect(esRutaPublica('/inicio')).toBe(false)
  })

  it('no confunde el indice con un prefijo de todo el portal', () => {
    // '/' matched as a prefix would make the whole portal public, and every
    // other assertion in this file would still pass.
    expect(RUTAS_PUBLICAS).toContain(RUTA_INDICE)
    expect(esRutaPublica('/administracion')).toBe(false)
  })

  it('ignora la cadena de consulta y el ancla al decidir si es publica', () => {
    // '/acceso?motivo=expirada' is exactly the URL the guard itself produces:
    // if the query made it non public, the redirect would loop.
    expect(esRutaPublica(`${RUTA_ACCESO}?motivo=${MOTIVO_EXPIRADA}`)).toBe(true)
    expect(esRutaPublica(`${RUTA_GUIA}#paleta`)).toBe(true)
    expect(esRutaPublica('/gobierno?q=saldo')).toBe(false)
  })
})

describe('decidirGuarda: la expiracion se distingue de la primera visita', () => {
  it('anuncia la expiracion cuando habia sesion y ya no la hay', () => {
    // Without the reason the entry screen renders its `normal` state and the
    // reader is thrown out with no explanation, which reads as a fault.
    expect(
      decidirGuarda({
        ruta: '/exploracion',
        sesion: null,
        habiaSesion: true,
        scopeExigido: null,
      }),
    ).toEqual({
      tipo: 'redirigir',
      destino: RUTA_ACCESO,
      motivo: MOTIVO_EXPIRADA,
      rutaPedida: '/exploracion',
    })
  })

  it('no le dice a un visitante nuevo que su sesion expiro', () => {
    // The bounce is never mute, but the two reasons are not interchangeable:
    // telling a first visitor that their session expired accuses them of
    // losing something they never had.
    const decision = decidirGuarda({
      ruta: '/exploracion',
      sesion: null,
      habiaSesion: false,
      scopeExigido: null,
    })

    expect(decision).toHaveProperty('motivo', MOTIVO_SESION_REQUERIDA)
  })

  it('manda el rebote a una direccion sin prefijo de idioma', () => {
    // The i18n strategy is `no_prefix` precisely so that RUTAS_CONTRATO stays
    // anchored to the A3 map. A locale segment here would break the contract,
    // the smoke and the site map at once.
    const decision = decidirGuarda({
      ruta: '/inicio',
      sesion: null,
      habiaSesion: false,
      scopeExigido: null,
    })

    expect(decision).toHaveProperty('destino', RUTA_ACCESO)
    expect(RUTA_ACCESO).not.toMatch(/^\/[a-z]{2}\//)
  })
})

describe('decidirGuarda: con sesion manda la jerarquia, no la igualdad', () => {
  it.each(ROLES)('deja pasar a %s donde no se exige rol', (rol) => {
    // "Any valid session" compiled as "no permission" would close the catalogue
    // to everybody, which is most of the portal.
    expect(
      decidirGuarda({
        ruta: '/exploracion',
        sesion: sesionDe(rol),
        habiaSesion: true,
        scopeExigido: null,
      }),
    ).toEqual({ tipo: 'permitir' })
  })

  it.each(
    ROLES.flatMap(rol => ROLES.map(exigido => [rol, exigido] as const)),
  )('con %s ante una pantalla de %s decide segun el rango', (rol, exigido) => {
    // The expected value is derived from ROLES, which US-015 owns, and not from
    // ROLES_EN_ORDEN, which this US generates: comparing the map against itself
    // would pass whatever the generator emitted.
    const alcanza = ROLES.indexOf(rol) >= ROLES.indexOf(exigido)
    const decision = decidirGuarda({
      ruta: '/administracion',
      sesion: sesionDe(rol),
      habiaSesion: true,
      scopeExigido: exigido,
    })

    expect(decision.tipo).toBe(alcanza ? 'permitir' : 'sin-permiso')
    expect(rolAlcanza(rol, exigido)).toBe(alcanza)
  })

  it('refleja el scope exigido en la negativa, y no rebota al acceso', () => {
    // Turning a 403 into a bounce is what makes a legitimate reader believe
    // they lost their session and retype a password that was never the problem.
    expect(
      decidirGuarda({
        ruta: '/administracion',
        sesion: sesionDe('operativo'),
        habiaSesion: true,
        scopeExigido: 'admin',
      }),
    ).toEqual({ tipo: 'sin-permiso', scopeExigido: 'admin' })
  })

  it('no reconoce ningun rol cuando no hay sesion', () => {
    expect(rolAlcanza(null, null)).toBe(false)
    expect(rolAlcanza(null, 'operativo')).toBe(false)
  })
})

describe('auth.global: el pegamento entre la decision y su efecto', () => {
  let evento: { id: string } | undefined
  let redirecciones: RouteLocationRaw[]
  let respuestas: number[]
  let cargarSesion: ReturnType<typeof vi.fn>
  let sesion: { value: SesionUsuario | null }

  /**
   * Loads the middleware with the Nuxt auto imports doubled.
   *
   * The module is re-imported per test because `defineNuxtRouteMiddleware` runs
   * at import time: a cached module would keep the stub of the first test.
   */
  async function correr(ruta: string): Promise<unknown> {
    const modulo = await import('~/middleware/auth.global')
    return await (modulo.default as unknown as (to: { path: string }) => Promise<unknown>)({
      path: ruta,
    })
  }

  function bloqueoActual(): BloqueoDeRuta | null {
    return usePermisos().bloqueo.value
  }

  beforeEach(() => {
    vi.resetModules()
    evento = undefined
    redirecciones = []
    respuestas = []
    sesion = { value: null }
    cargarSesion = vi.fn(() => Promise.resolve())

    vi.doMock('~/composables/useSesion', () => ({
      useSesion: () => ({ sesion, cargarSesion }),
    }))

    vi.stubGlobal(
      'defineNuxtRouteMiddleware',
      (manejador: unknown) => manejador,
    )
    vi.stubGlobal('navigateTo', (destino: RouteLocationRaw) => {
      redirecciones.push(destino)
      return destino
    })
    vi.stubGlobal('useRequestEvent', () => evento)
    vi.stubGlobal('setResponseStatus', (_evento: unknown, codigo: number) => {
      respuestas.push(codigo)
    })
  })

  afterEach(() => {
    vi.doUnmock('~/composables/useSesion')
    vi.unstubAllGlobals()
  })

  it('no pide la sesion en una ruta publica', async () => {
    // Every visit to the prototype index would otherwise cost a call to
    // /api/auth/me and, on Cloud Run with scale to zero, a cold start of the
    // backend that nobody asked for.
    await correr(RUTA_INDICE)

    expect(cargarSesion).not.toHaveBeenCalled()
    expect(redirecciones).toEqual([])
  })

  it('no revalida la sesion que ya esta en memoria', async () => {
    sesion.value = sesionDe('analista')

    await correr('/exploracion')

    expect(cargarSesion).not.toHaveBeenCalled()
  })

  it('pide la sesion una sola vez cuando el estado esta vacio', async () => {
    cargarSesion = vi.fn(() => {
      sesion.value = sesionDe('operativo')
      return Promise.resolve()
    })

    await correr('/inicio')

    expect(cargarSesion).toHaveBeenCalledTimes(1)
    expect(redirecciones).toEqual([])
  })

  it('rebota al acceso, sin reventar, si la peticion de sesion falla', async () => {
    // An unhandled rejection inside a global middleware turns a network hiccup
    // into an error page: the reader sees a stack instead of the entry screen.
    cargarSesion = vi.fn(() => Promise.reject(new Error('red caida')))

    await correr('/inicio')

    expect(sesion.value).toBeNull()
    expect(redirecciones).toEqual([
      { path: RUTA_ACCESO, query: { destino: '/inicio', motivo: MOTIVO_SESION_REQUERIDA } },
    ])
  })

  it('explica la expiracion despues de que un 401 cerrara la sesion', async () => {
    // `expirarSesion()` is what a screen calls when a data request answers 401.
    // Without the flag it leaves behind, this navigation is indistinguishable
    // from a first visit and the reader is thrown out with no explanation.
    usePermisos().expirarSesion()

    await correr('/inicio')

    expect(redirecciones).toEqual([
      { path: RUTA_ACCESO, query: { destino: '/inicio', motivo: MOTIVO_EXPIRADA } },
    ])
  })

  it('no repite el aviso de expiracion en la navegacion siguiente', async () => {
    // Said twice it stops being an explanation and becomes an accusation: the
    // second time the reader did not lose anything, they simply had not entered
    // yet.
    usePermisos().expirarSesion()

    await correr('/inicio')
    await correr('/gobierno')

    expect(redirecciones).toEqual([
      { path: RUTA_ACCESO, query: { destino: '/inicio', motivo: MOTIVO_EXPIRADA } },
      { path: RUTA_ACCESO, query: { destino: '/gobierno', motivo: MOTIVO_SESION_REQUERIDA } },
    ])
  })

  it('marca el bloqueo y NO redirige cuando falta permiso', async () => {
    // Redirecting here would lose the address the reader tried to open, and
    // with it the ability to share it or to press the back button.
    sesion.value = sesionDe('operativo')

    await correr('/administracion')

    expect(redirecciones).toEqual([])
    expect(bloqueoActual()).toEqual({ ruta: '/administracion', scopeExigido: 'admin' })
  })

  it('fija el 403 en la respuesta solo cuando hay peticion que responder', async () => {
    sesion.value = sesionDe('operativo')

    await correr('/administracion')
    expect(respuestas).toEqual([])

    evento = { id: 'peticion-de-servidor' }
    await correr('/administracion')
    expect(respuestas).toEqual([403])
  })

  it('limpia el bloqueo heredado antes de decidir la navegacion siguiente', async () => {
    // A sticky block paints an allowed screen as refused, and the reader has no
    // way to tell that from a real refusal.
    sesion.value = sesionDe('admin')
    usePermisos().marcarBloqueo({ ruta: '/administracion', scopeExigido: 'admin' })

    await correr('/exploracion')

    expect(bloqueoActual()).toBeNull()
  })

  it('deja pasar el asistente a cualquier sesion y lo cierra sin ella', async () => {
    sesion.value = sesionDe('operativo')
    await correr(RUTA_ASISTENTE)
    expect(redirecciones).toEqual([])

    sesion.value = null
    await correr(RUTA_ASISTENTE)
    expect(redirecciones).toEqual([
      { path: RUTA_ACCESO, query: { destino: RUTA_ASISTENTE, motivo: MOTIVO_SESION_REQUERIDA } },
    ])
  })
})

describe('el rebote dice adonde iba y por que, sin abrir una redireccion', () => {
  it('devuelve la ruta pedida junto al motivo de primera visita', () => {
    // The defect: the bounce is mute. An evaluator opens `/gobierno` from the
    // index, lands on a bare entry form and reads the prototype as one that
    // does not open, which is the single most expensive misreading of A4.
    const decision = decidirGuarda({
      ruta: '/gobierno',
      sesion: null,
      habiaSesion: false,
      scopeExigido: null,
    })

    expect(decision).toEqual({
      tipo: 'redirigir',
      destino: RUTA_ACCESO,
      motivo: MOTIVO_SESION_REQUERIDA,
      rutaPedida: '/gobierno',
    })
  })

  it('normaliza la ruta pedida antes de devolverla', () => {
    // Query and hash belong to the navigation, not to the contract route, and
    // carrying them into the query string of the bounce would nest one URL
    // inside another.
    const decision = decidirGuarda({
      ruta: '/gobierno?q=saldo#linaje',
      sesion: null,
      habiaSesion: false,
      scopeExigido: null,
    })

    expect(decision).toHaveProperty('rutaPedida', '/gobierno')
  })

  it('no devuelve nada cuando la ruta pedida no es del contrato', () => {
    const decision = decidirGuarda({
      ruta: '/pantalla-que-no-existe',
      sesion: null,
      habiaSesion: false,
      scopeExigido: null,
    })

    expect(decision).not.toHaveProperty('rutaPedida')
  })

  it.each([
    'https://evil.example/robo',
    '//evil.example',
    '/pantalla-que-no-existe',
    RUTA_ACCESO,
    RUTA_INDICE,
    '',
    ' /gobierno',
  ])('rechaza %s como destino de retorno', (valor) => {
    // The allowlist is RUTAS_CONTRATO itself. Anything else accepted here is an
    // open redirect driven by a query string that any link can write, and the
    // entry screen is rejected on top of that because returning to it loops.
    expect(destinoDeRetorno(valor)).toBeNull()
  })

  it('rechaza un destino que no es una cadena', () => {
    // Vue Router hands repeated parameters as an array, and `?destino=/a&destino=/b`
    // is exactly how a crafted link would try to smuggle one past a check
    // written for strings.
    expect(destinoDeRetorno(['/gobierno'])).toBeNull()
    expect(destinoDeRetorno(undefined)).toBeNull()
    expect(destinoDeRetorno(null)).toBeNull()
  })

  it.each(RUTAS_DE_PRODUCTO)('acepta %s, que si esta en el contrato', (ruta) => {
    expect(destinoDeRetorno(ruta)).toBe(ruta)
  })

  it('publica el nombre del parametro que la pantalla de acceso lee', () => {
    // Two literals -one written by the guard, one read by the screen- is how a
    // bounce ends up carrying a destination nobody picks up.
    expect(PARAMETRO_DESTINO).toBe('destino')
  })
})
