import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'

import { beforeEach, describe, expect, it, vi } from 'vitest'

/**
 * US-001 — the runtime proxy for `/api/**` (`server/api/[...].ts`).
 *
 * It replaces the `routeRules` proxy, which Nitro compiles into the bundle and
 * whose target is therefore frozen at build time. The three properties pinned
 * here are the ones that can break without anything complaining:
 *
 *   1. the target comes from `runtimeConfig.apiBase` on EVERY request;
 *   2. the full path travels untouched, the `/api` prefix included;
 *   3. the HTTP method and the live event are propagated to the forward.
 *
 * `defineEventHandler`, `useRuntimeConfig` and `proxyRequest` are Nitro auto
 * imports: here they are replaced by doubles that mimic their real contract.
 * The `useRuntimeConfig` double resolves the configuration from
 * `event.context.nitro` when it is there, exactly as Nitro does, so that
 * "read per request" is a verifiable claim and not a promise made by the
 * module comment.
 *
 * No test opens a network connection: the fake `proxyRequest` is the boundary.
 */

interface ConfiguracionDeRuntime {
  apiBase: string
  apiAudience?: string
}

/** Minimal shape of the h3 event that the handler actually reads. */
interface EventoFalso {
  path: string
  method: string
  context: { nitro: { runtimeConfig?: ConfiguracionDeRuntime } }
  /** Request headers, read since US-015 for the origin check. */
  cabeceras: Record<string, string>
  /** Cookies of the request, read since US-015 for the bearer injection. */
  cookies: Record<string, string>
}

/** Answer of the fake upstream, so assertions read the handler output. */
interface RespuestaReenviada {
  destino: string
  metodo: string
  evento: EventoFalso
  cabeceras?: Record<string, string>
}

type Manejador = (evento: EventoFalso) => Promise<RespuestaReenviada>

const BASE_INICIAL = 'http://api-de-compose:8000'

/** Runtime config of the process, mutable to emulate a redeploy. */
let configuracionDelProceso: ConfiguracionDeRuntime

function crearEvento(path: string, method = 'GET'): EventoFalso {
  return { path, method, context: { nitro: {} }, cabeceras: {}, cookies: {} }
}

/**
 * Installs the Nitro auto-imports as globals and loads the handler afresh.
 *
 * The module is imported after the stubs are in place because
 * `defineEventHandler` runs at import time.
 */
async function cargarManejador(): Promise<Manejador> {
  vi.resetModules()
  const modulo = await import('../server/api/[...]')
  return modulo.default as unknown as Manejador
}

beforeEach(() => {
  configuracionDelProceso = { apiBase: BASE_INICIAL }

  vi.stubGlobal('defineEventHandler', (manejador: Manejador) => manejador)

  vi.stubGlobal('getRequestURL', () => new URL('https://karisma-web.example/api/x'))
  vi.stubGlobal('getRequestIP', () => '203.0.113.7')

  // Added by US-015: the handler reads the session cookie to build the bearer
  // header and the fetch metadata headers to reject a foreign origin.
  vi.stubGlobal(
    'getHeader',
    (evento: EventoFalso, nombre: string) => evento.cabeceras[nombre.toLowerCase()],
  )
  vi.stubGlobal('getCookie', (evento: EventoFalso, nombre: string) => evento.cookies[nombre])

  vi.stubGlobal(
    'createError',
    (opciones: { statusCode: number, statusMessage?: string }) =>
      Object.assign(new Error(opciones.statusMessage ?? 'Error'), opciones),
  )

  vi.stubGlobal(
    'useRuntimeConfig',
    (evento?: EventoFalso): ConfiguracionDeRuntime =>
      evento?.context.nitro.runtimeConfig ?? configuracionDelProceso,
  )

  vi.stubGlobal(
    'proxyRequest',
    async (
      evento: EventoFalso,
      destino: string,
      opciones?: { headers?: Record<string, string> },
    ): Promise<RespuestaReenviada> => ({
      destino,
      metodo: evento.method,
      evento,
      cabeceras: opciones?.headers,
    }),
  )

  return () => {
    vi.unstubAllGlobals()
  }
})

describe('el destino sale de runtimeConfig en cada solicitud', () => {
  it('reenvia al apiBase declarado', async () => {
    const manejador = await cargarManejador()

    const respuesta = await manejador(crearEvento('/api/health'))

    expect(respuesta.destino).toBe(`${BASE_INICIAL}/api/health`)
  })

  it('no congela el destino al importar el modulo', async () => {
    // This is the whole reason the handler exists: a compiled `routeRules`
    // would still point at BASE_INICIAL after the variable changed.
    const manejador = await cargarManejador()
    await manejador(crearEvento('/api/health'))

    configuracionDelProceso.apiBase = 'https://karisma-api-abc.a.run.app'
    const despliegue = await manejador(crearEvento('/api/health'))

    configuracionDelProceso.apiBase = 'http://otro-destino:9000'
    const redespliegue = await manejador(crearEvento('/api/health'))

    expect(despliegue.destino).toBe('https://karisma-api-abc.a.run.app/api/health')
    expect(redespliegue.destino).toBe('http://otro-destino:9000/api/health')
  })

  it('pasa el evento a useRuntimeConfig para honrar la configuracion por solicitud', async () => {
    // Without the event, `useRuntimeConfig()` returns the shared configuration
    // of the process and ignores the one Nitro resolves per request.
    const manejador = await cargarManejador()
    const evento = crearEvento('/api/health')
    evento.context.nitro.runtimeConfig = { apiBase: 'http://api-de-esta-solicitud:8000' }

    const respuesta = await manejador(evento)

    expect(respuesta.destino).toBe('http://api-de-esta-solicitud:8000/api/health')
  })
})

describe('la ruta completa viaja intacta', () => {
  // The sample used to be /api/auth/token. Since US-015 that path has a Nitro
  // handler of its own and the proxy refuses it on purpose, so it can no longer
  // stand for "any endpoint of the backend". /api/auth/me replaces it and is a
  // better witness anyway: it is the one route under /api/auth that really does
  // travel through here, so it proves the prefix survives without borrowing a
  // path that is now somebody else's. The assertion below did not change.
  it.each([
    '/api/health',
    '/api/auth/me',
    '/api/catalog/search',
    '/api/chat',
    '/api/exploracion/creditos/2026',
  ])('conserva %s sin recortar el prefijo /api', async (ruta) => {
    const manejador = await cargarManejador()

    const respuesta = await manejador(crearEvento(ruta))

    expect(respuesta.destino).toBe(`${BASE_INICIAL}${ruta}`)
    expect(new URL(respuesta.destino).pathname).toBe(ruta)
  })

  it('no reescribe /api/auth/me como /auth/me', async () => {
    // The backend serves ALL of its endpoints under /api/*: stripping the
    // prefix -the classic proxy configuration mistake- breaks every one at once.
    const manejador = await cargarManejador()

    const respuesta = await manejador(crearEvento('/api/auth/me'))

    expect(respuesta.destino).not.toBe(`${BASE_INICIAL}/auth/me`)
    expect(new URL(respuesta.destino).pathname.startsWith('/api/')).toBe(true)
  })

  it('conserva la cadena de consulta que h3 incluye en event.path', async () => {
    const manejador = await cargarManejador()

    const respuesta = await manejador(crearEvento('/api/creditos?anio=2026&silo=liquidez'))

    expect(respuesta.destino).toBe(`${BASE_INICIAL}/api/creditos?anio=2026&silo=liquidez`)
    expect(new URL(respuesta.destino).searchParams.get('anio')).toBe('2026')
  })
})

describe('el metodo y el evento vivo se propagan', () => {
  it.each(['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])('reenvia una solicitud %s', async (metodo) => {
    const manejador = await cargarManejador()

    const respuesta = await manejador(crearEvento('/api/export', metodo))

    expect(respuesta.metodo).toBe(metodo)
    expect(respuesta.destino).toBe(`${BASE_INICIAL}/api/export`)
  })

  it('entrega el mismo evento, no una copia, para que cuerpo y cabeceras fluyan', async () => {
    const manejador = await cargarManejador()
    const evento = crearEvento('/api/chat', 'POST')

    const respuesta = await manejador(evento)

    expect(respuesta.evento).toBe(evento)
  })

  it('devuelve la respuesta del reenvio en vez de descartarla', async () => {
    const manejador = await cargarManejador()

    const respuesta = await manejador(crearEvento('/api/health'))

    expect(respuesta).toMatchObject({ destino: `${BASE_INICIAL}/api/health`, metodo: 'GET' })
  })
})

describe('el destino es configurable sin reconstruir la imagen', () => {
  function leerDelRepositorio(relativa: string): string {
    return readFileSync(fileURLToPath(new URL(relativa, import.meta.url)), 'utf8')
  }

  const plantillaEntorno = leerDelRepositorio('../.env.example')
  const compose = leerDelRepositorio('../../docker-compose.yml')

  it('documenta NUXT_API_BASE como la unica palanca del destino', () => {
    expect(plantillaEntorno).toMatch(/^NUXT_API_BASE=/m)
  })

  it('apunta el contenedor al servicio de Compose que realmente existe', () => {
    // If somebody renames the Compose service, the proxy fails at runtime with
    // an ENOTFOUND that no build ever catches.
    //
    // The value is read from docker-compose.yml and NOT from .env.example, and
    // that is the whole point of the case. The two ways of running the portal
    // need DIFFERENT destinations: inside the Compose network the backend is
    // "api", from the host it is "localhost". Compose settles it by declaring
    // NUXT_API_BASE under "environment", which wins over "env_file", so the
    // template is free to describe the host -where whoever edits it lives-.
    // Asserting "api:8000" against the template demanded the value that breaks
    // "pnpm dev": the screen paints and every call dies on a name that only
    // resolves inside Docker. Corrected on 12-ago-2026; the assertion used to
    // contradict the comment of the very file it was reading.
    const destino = compose.match(/^ {6}NUXT_API_BASE: "(\S+)"$/m)?.[1] ?? ''
    const servicio = new URL(destino).hostname

    expect(destino).toBe('http://api:8000')
    expect(compose).toMatch(new RegExp(`^ {2}${servicio}:$`, 'm'))
  })

  it('deja la plantilla del host apuntando a donde el host puede llegar', () => {
    // The other half of the same decision, and the one that actually breaks a
    // developer's afternoon when it regresses.
    const destino = plantillaEntorno.match(/^NUXT_API_BASE=(\S+)$/m)?.[1] ?? ''

    expect(new URL(destino).hostname).toBe('localhost')
  })

  it('declara apiBase en la mitad privada de runtimeConfig', () => {
    // Only a key declared in runtimeConfig accepts the environment variable at
    // runtime; and declaring it under `public` would publish the internal
    // address of the backend in the HTML the browser receives.
    const configuracionNuxt = leerDelRepositorio('../nuxt.config.ts')
    const bloque = configuracionNuxt.match(/runtimeConfig:\s*\{([\s\S]*?)\n {2}\},/)?.[1] ?? ''
    const bloquePublico = bloque.match(/public:\s*\{([\s\S]*?)\}/)?.[1] ?? ''

    expect(bloque).toMatch(/^ {4}apiBase,$/m)
    expect(bloquePublico).not.toBe('')
    expect(bloquePublico).not.toMatch(/apiBase/)
  })
})

describe('no deja escapar del prefijo /api', () => {
  // h3 routes on the RAW path -it does NOT decode before matching, and the
  // first version of this comment claimed the opposite, which is what hid the
  // alias defect the block below now covers-. What reaches this handler is
  // therefore whatever the client typed, escapes included, and the handler
  // decodes once before deciding anything.
  //
  // Verified by exploiting it against the live Compose before fixing it:
  // "/api/%2e%2e/openapi.json" returned the full OpenAPI schema through the
  // public origin. Without these cases the single-origin boundary that the
  // whole design rests on does not exist, and on Cloud Run the backend is left
  // with ingress closed and reachable all the same.
  it.each([
    ['/api/%2E%2E/openapi.json'],
    ['/api/../health'],
    ['/api/../../docs'],
    ['/api/subruta/../../redoc'],
  ])('rechaza %s sin tocar el backend', async (ruta) => {
    const manejador = await cargarManejador()

    await expect(manejador(crearEvento(ruta))).rejects.toMatchObject({
      statusCode: 404,
    })
  })

  it('conserva el recorrido que se queda dentro del prefijo', async () => {
    const manejador = await cargarManejador()

    const respuesta = await manejador(crearEvento('/api/catalogo/../busqueda'))

    expect(respuesta.destino).toBe(`${BASE_INICIAL}/api/busqueda`)
  })

  it('mantiene intacta la cadena de consulta', async () => {
    const manejador = await cargarManejador()

    const respuesta = await manejador(crearEvento('/api/busqueda?q=creditos&pagina=2'))

    expect(respuesta.destino).toBe(`${BASE_INICIAL}/api/busqueda?q=creditos&pagina=2`)
  })
})

describe('no relega al cliente las cabeceras de reenvio', () => {
  it('reescribe x-forwarded-* con datos propios y vacia forwarded', async () => {
    // A client can send "X-Forwarded-For: 6.6.6.6". Today uvicorn ignores it
    // because forwarded_allow_ips is 127.0.0.1, but the day somebody sets
    // FORWARDED_ALLOW_IPS=* the spoof becomes effective and poisons both the
    // logs and the login rate limiting of US-015.
    const manejador = await cargarManejador()

    const respuesta = await manejador(crearEvento('/api/health'))

    expect(respuesta.cabeceras?.['x-forwarded-for']).toBe('203.0.113.7')
    expect(respuesta.cabeceras?.['x-forwarded-proto']).toBe('https')
    expect(respuesta.cabeceras?.['x-forwarded-host']).toBe('karisma-web.example')
    expect(respuesta.cabeceras?.forwarded).toBe('')
  })

  it('no relaya el authorization que manda el cliente', async () => {
    // Since US-015 the session lives in an httpOnly cookie and only this
    // handler turns it into a bearer. Relaying the header the client sent would
    // reopen the second door: a token typed by hand would reach the API with
    // the same authority, and the session would stop living in one place.
    const manejador = await cargarManejador()
    const evento = crearEvento('/api/catalogo')
    evento.cabeceras.authorization = 'Bearer token-inventado-por-el-cliente'

    const respuesta = await manejador(evento)

    expect(respuesta.cabeceras?.authorization).toBe('')
  })

  it('vacia la cookie hacia el upstream', async () => {
    // The backend authenticates with the bearer and has no use for the cookie.
    // Letting it through would deliver the token by two routes at once, and the
    // second one ends up written in an upstream access log.
    const manejador = await cargarManejador()
    const evento = crearEvento('/api/catalogo')
    evento.cookies.karisma_sesion = 'jwt.de.prueba.sin-secreto'

    const respuesta = await manejador(evento)

    expect(respuesta.cabeceras?.cookie).toBe('')
    expect(respuesta.cabeceras?.authorization).toBe('Bearer jwt.de.prueba.sin-secreto')
  })
})

describe('no reenvia una ruta que Nitro se sirve a si mismo', () => {
  // The defect this block exists for was live and exploitable, and it was found
  // by the security audit of US-015, not by a test.
  //
  // The three routes under server/api/auth/ are the reason the JWT never
  // reaches the browser: each one calls the API, puts the token in the
  // httpOnly cookie and answers with the session alone. Nitro matches them on
  // the RAW path, so "/api/auth%2Fdemo" -where the slash is an escape and not
  // a separator- missed the specific handler and fell through to this proxy,
  // which forwarded it verbatim. Uvicorn decodes once, resolved it to
  // /api/auth/demo and answered with a real JWT, which came back to the page
  // as JSON: readable by any script on it, and with DEMO_LOGIN_ENABLED on -the
  // state in which the A4 captures are recorded- as an admin.
  //
  // Reproduced against the live Compose: POST /api/auth%2Fdemo answered 200
  // with access_token in the body. Two doors close it, and both are needed:
  // decoding once before deciding, and refusing the three paths outright.
  it.each([
    ['/api/auth%2Ftoken'],
    ['/api/auth%2Fdemo'],
    ['/api/auth%2Flogout'],
    ['/api/%61uth/demo'],
    ['/api/auth/%64emo'],
  ])('rechaza el alias %s sin tocar el backend', async (ruta) => {
    const manejador = await cargarManejador()

    await expect(manejador(crearEvento(ruta, 'POST'))).rejects.toMatchObject({
      statusCode: 404,
    })
  })

  it('rechaza tambien la ruta escrita tal cual, que nunca deberia llegar aqui', async () => {
    // Nitro resolves it before this file runs, so a request that arrives here
    // spelling it plainly has been routed by something that is not Nitro. The
    // proxy has no way to serve it correctly, and forwarding it is the leak.
    const manejador = await cargarManejador()

    await expect(manejador(crearEvento('/api/auth/token', 'POST'))).rejects.toMatchObject({
      statusCode: 404,
    })
  })

  it('deja pasar el resto de /api/auth, que si es del backend', async () => {
    // /api/auth/me has no Nitro handler: it is read through the proxy with the
    // bearer injected from the cookie, and closing the whole prefix would take
    // the session check down with it.
    const manejador = await cargarManejador()

    const respuesta = await manejador(crearEvento('/api/auth/me'))

    expect(respuesta.destino).toBe(`${BASE_INICIAL}/api/auth/me`)
  })

  it('un escape mal formado es 400 y no una ruta', async () => {
    // decodeURIComponent throws on "%zz". Letting it propagate would turn a
    // malformed request into a 500 with a stack trace.
    const manejador = await cargarManejador()

    await expect(manejador(crearEvento('/api/%zz/catalogo'))).rejects.toMatchObject({
      statusCode: 400,
    })
  })
})

describe('cabecera de identidad Cloud Run (x-serverless-authorization)', () => {
  it('sin apiAudience no anade la cabecera x-serverless-authorization y conserva authorization', async () => {
    configuracionDelProceso = { apiBase: BASE_INICIAL, apiAudience: '' }
    const manejador = await cargarManejador()
    const evento = crearEvento('/api/catalog/search')
    evento.cookies.karisma_sesion = 'jwt.sesion.usuario'

    const respuesta = await manejador(evento)

    expect(respuesta.cabeceras?.['x-serverless-authorization']).toBeUndefined()
    expect(respuesta.cabeceras?.authorization).toBe('Bearer jwt.sesion.usuario')
  })

  it('con apiAudience inyecta x-serverless-authorization y conserva el JWT de la sesion', async () => {
    configuracionDelProceso = {
      apiBase: 'https://karisma-api-xyz.a.run.app',
      apiAudience: 'https://karisma-api-xyz.a.run.app',
    }

    const expEnElFuturo = Math.floor(Date.now() / 1000) + 3600
    const header = Buffer.from(JSON.stringify({ alg: 'RS256', typ: 'JWT' })).toString('base64url')
    const payload = Buffer.from(JSON.stringify({ exp: expEnElFuturo })).toString('base64url')
    const idTokenSimulado = `${header}.${payload}.firma`

    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      statusText: 'OK',
      text: async () => idTokenSimulado,
    })
    vi.stubGlobal('fetch', mockFetch)

    const manejador = await cargarManejador()
    const evento = crearEvento('/api/catalog/search')
    evento.cookies.karisma_sesion = 'jwt.sesion.usuario'

    const respuesta = await manejador(evento)

    expect(respuesta.cabeceras?.['x-serverless-authorization']).toBe(`Bearer ${idTokenSimulado}`)
    expect(respuesta.cabeceras?.authorization).toBe('Bearer jwt.sesion.usuario')
  })

  it('si el servidor de metadatos falla responde 502 y proxyRequest no se llama', async () => {
    configuracionDelProceso = {
      apiBase: 'https://karisma-api-xyz.a.run.app',
      apiAudience: 'https://karisma-api-xyz.a.run.app',
    }

    const mockFetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 500,
      statusText: 'Internal Server Error',
      text: async () => 'Error',
    })
    vi.stubGlobal('fetch', mockFetch)

    const spyProxyRequest = vi.fn()
    vi.stubGlobal('proxyRequest', spyProxyRequest)

    const manejador = await cargarManejador()
    const evento = crearEvento('/api/catalog/search')

    await expect(manejador(evento)).rejects.toMatchObject({
      statusCode: 502,
      statusMessage: 'Bad Gateway',
    })

    expect(spyProxyRequest).not.toHaveBeenCalled()
  })
})
