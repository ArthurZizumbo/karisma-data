import { beforeEach, describe, expect, it, vi } from 'vitest'

import { limpiarCacheDeIdentidad } from '../server/utils/identidadCloudRun'

/**
 * US-M01 — the identity token inside the three session handlers.
 *
 * `identidadCloudRun.spec.ts` pins the fetcher and its cache; the proxy is
 * pinned in `proxyApi.spec.ts`. What neither of them can see is what the login
 * handlers do with that token, and the QA of 19-ago-2026 found those three
 * branches with no coverage at all: the header that reaches the API, and the
 * answer when the metadata server is unreachable.
 *
 * The defect each test denies is written on the test itself. Two of them exist
 * because the wrong status code here is not cosmetic: a 401 tells the person in
 * front of the screen that their password is wrong, and no amount of retyping
 * fixes a metadata server that does not answer.
 *
 * No test opens a socket: `fetch` -the metadata server- and `$fetch` -the API-
 * are both doubled, and the doubles implement the same contract as the ones in
 * `sesionNitro.spec.ts`, whose file this one deliberately does not touch.
 */

interface EventoFalso {
  path: string
  method: string
  origen: string
  cabeceras: Record<string, string>
  cookies: Record<string, string>
  cuerpo: unknown
  context: { nitro: Record<string, unknown> }
}

interface LlamadaUpstream {
  url: string
  opciones: Record<string, unknown>
}

const API_BASE = 'http://api-de-compose:8000'
const AUDIENCIA = 'https://karisma-api-ejemplo.a.run.app'
const TOKEN = 'jwt.de.prueba.sin-secreto'

const PERFIL = {
  id: '0f6d2a1e-0000-4000-8000-000000000001',
  username: 'lmendez',
  email: 'lmendez@karisma.demo',
  full_name: 'Laura Méndez',
  role: 'operativo',
  disabled: false,
}

let llamadas: LlamadaUpstream[]
let audienciaConfigurada: string | undefined

/**
 * Builds an unverified JWT whose payload carries the given expiry.
 *
 * @param segundosDeVida Seconds from now until `exp`.
 * @returns Serialized fake token.
 */
function tokenConVida(segundosDeVida: number): string {
  const exp = Math.floor(Date.now() / 1000) + segundosDeVida
  const cabecera = Buffer.from(JSON.stringify({ alg: 'RS256', typ: 'JWT' })).toString('base64url')
  const carga = Buffer.from(JSON.stringify({ exp, aud: AUDIENCIA })).toString('base64url')
  return `${cabecera}.${carga}.${Buffer.from('firma').toString('base64url')}`
}

function crearEvento(parcial: Partial<EventoFalso> = {}): EventoFalso {
  return {
    path: '/api/auth/token',
    method: 'POST',
    origen: 'https://karisma-web.example',
    cabeceras: {},
    cookies: {},
    cuerpo: { usuario: 'lmendez', contrasena: 'clave-de-prueba' },
    context: { nitro: {} },
    ...parcial,
  }
}

async function cargar(ruta: string): Promise<(evento: EventoFalso) => Promise<unknown>> {
  vi.resetModules()
  const modulo = await import(/* @vite-ignore */ ruta)
  return modulo.default as unknown as (evento: EventoFalso) => Promise<unknown>
}

const cargarToken = (): Promise<(evento: EventoFalso) => Promise<unknown>> =>
  cargar('../server/api/auth/token.post')
const cargarDemo = (): Promise<(evento: EventoFalso) => Promise<unknown>> =>
  cargar('../server/api/auth/demo.post')

/** Cabeceras of the call the handler made to a given upstream path. */
function cabecerasDe(ruta: string): Record<string, string> {
  const llamada = llamadas.find(l => new URL(l.url).pathname === ruta)
  expect(llamada, `no hubo llamada a ${ruta}`).toBeDefined()
  return (llamada!.opciones.headers ?? {}) as Record<string, string>
}

beforeEach(() => {
  llamadas = []
  audienciaConfigurada = AUDIENCIA
  limpiarCacheDeIdentidad()

  vi.stubGlobal('defineEventHandler', (manejador: unknown) => manejador)
  vi.stubGlobal('useRuntimeConfig', () => ({ apiBase: API_BASE, apiAudience: audienciaConfigurada }))
  vi.stubGlobal('readBody', (evento: EventoFalso) => Promise.resolve(evento.cuerpo))
  vi.stubGlobal('getRequestURL', (evento: EventoFalso) => new URL(evento.path, evento.origen))
  vi.stubGlobal(
    'getHeader',
    (evento: EventoFalso, nombre: string) => evento.cabeceras[nombre.toLowerCase()],
  )
  vi.stubGlobal('getCookie', (evento: EventoFalso, nombre: string) => evento.cookies[nombre])
  vi.stubGlobal('getRequestIP', () => '203.0.113.7')
  vi.stubGlobal('setCookie', () => {})
  vi.stubGlobal('deleteCookie', () => {})
  vi.stubGlobal(
    'createError',
    (opciones: { statusCode: number, statusMessage?: string, data?: unknown }) =>
      Object.assign(new Error(opciones.statusMessage ?? 'Error'), opciones),
  )

  vi.stubGlobal('$fetch', (url: string, opciones: Record<string, unknown> = {}) => {
    llamadas.push({ url, opciones })
    const ruta = new URL(url).pathname
    if (ruta === '/api/auth/me') return Promise.resolve(PERFIL)
    return Promise.resolve({ access_token: TOKEN, token_type: 'bearer' })
  })

  return () => {
    vi.unstubAllGlobals()
    limpiarCacheDeIdentidad()
  }
})

describe('el token de identidad en el inicio de sesion', () => {
  it('viaja hacia el API y hacia el perfil, sin tocar la cabecera de sesion', async () => {
    // Defect: the identity token written into `authorization` instead of its
    // own header. The API would then read a Google token where it expects the
    // portal JWT and every role check downstream would collapse.
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      statusText: 'OK',
      text: async () => tokenConVida(3600),
    }))
    const manejador = await cargarToken()

    await manejador(crearEvento())

    const alEmitir = cabecerasDe('/api/auth/token')
    expect(alEmitir['x-serverless-authorization']).toMatch(/^Bearer /)
    expect(alEmitir['content-type']).toBe('application/x-www-form-urlencoded')

    const alPerfil = cabecerasDe('/api/auth/me')
    expect(alPerfil.authorization).toBe(`Bearer ${TOKEN}`)
    expect(alPerfil['x-serverless-authorization']).toMatch(/^Bearer /)
  })

  it('sin audiencia configurada no pide token ni anade cabecera', async () => {
    // Defect: a call to the metadata server under Compose or `pnpm dev`, where
    // that host does not resolve. The login would hang or fail in the one
    // environment the captures are recorded in.
    audienciaConfigurada = undefined
    const espia = vi.fn()
    vi.stubGlobal('fetch', espia)
    const manejador = await cargarToken()

    await manejador(crearEvento())

    expect(espia).not.toHaveBeenCalled()
    expect(cabecerasDe('/api/auth/token')['x-serverless-authorization']).toBeUndefined()
    expect(cabecerasDe('/api/auth/me')['x-serverless-authorization']).toBeUndefined()
  })

  it('si el servidor de metadatos falla responde 502 y no 401', async () => {
    // Defect: reporting an unreachable identity layer as a rejected credential.
    // The interface would ask for the password again, the password is right,
    // and nobody would look at the layer that actually broke.
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
      ok: false,
      status: 500,
      statusText: 'Internal Server Error',
      text: async () => 'sin token',
    }))
    const manejador = await cargarToken()

    await expect(manejador(crearEvento())).rejects.toMatchObject({ statusCode: 502 })
    expect(llamadas).toHaveLength(0)
  })

  it('el acceso de demostracion tambien responde 502 y no lo llama puerta cerrada', async () => {
    // Defect: `demo_deshabilitado` for a metadata failure. That code sends the
    // reader to check DEMO_LOGIN_ENABLED on the backend, which is on.
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new Error('getaddrinfo ENOTFOUND')))
    const manejador = await cargarDemo()

    const evento = crearEvento({ path: '/api/auth/demo', cuerpo: { rol: 'operativo' } })
    await expect(manejador(evento)).rejects.toMatchObject({ statusCode: 502 })
  })

  it('si el metadatos cae entre la emision y el perfil, sigue siendo 502', async () => {
    // Defect: the silent catch this file was written for. `leerPerfilDeSesion`
    // used to swallow the failure and call a private Cloud Run service with no
    // identity, which answers 403; the handler read that 403 as a rejected
    // session and told the user to log in again, forever.
    //
    // The first token is born already inside the renewal margin, so the cache
    // cannot serve it twice and the second call reaches the doubled server.
    const metadatos = vi.fn()
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        statusText: 'OK',
        text: async () => tokenConVida(10),
      })
      .mockResolvedValueOnce({
        ok: false,
        status: 503,
        statusText: 'Service Unavailable',
        text: async () => 'caido',
      })
    vi.stubGlobal('fetch', metadatos)
    const manejador = await cargarToken()

    await expect(manejador(crearEvento())).rejects.toMatchObject({ statusCode: 502 })
    expect(metadatos).toHaveBeenCalledTimes(2)
    expect(llamadas.map(l => new URL(l.url).pathname)).toEqual(['/api/auth/token'])
  })
})
