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
}

/** Minimal shape of the h3 event that the handler actually reads. */
interface EventoFalso {
  path: string
  method: string
  context: { nitro: { runtimeConfig?: ConfiguracionDeRuntime } }
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
  return { path, method, context: { nitro: {} } }
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
  it.each([
    '/api/health',
    '/api/auth/token',
    '/api/catalog/search',
    '/api/chat',
    '/api/exploracion/creditos/2026',
  ])('conserva %s sin recortar el prefijo /api', async (ruta) => {
    const manejador = await cargarManejador()

    const respuesta = await manejador(crearEvento(ruta))

    expect(respuesta.destino).toBe(`${BASE_INICIAL}${ruta}`)
    expect(new URL(respuesta.destino).pathname).toBe(ruta)
  })

  it('no reescribe /api/auth/token como /auth/token', async () => {
    // The backend serves ALL of its endpoints under /api/*: stripping the
    // prefix -the classic proxy configuration mistake- breaks every one at once.
    const manejador = await cargarManejador()

    const respuesta = await manejador(crearEvento('/api/auth/token'))

    expect(respuesta.destino).not.toBe(`${BASE_INICIAL}/auth/token`)
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

  it('apunta la plantilla al servicio de Compose que realmente existe', () => {
    // If somebody renames the Compose service, the proxy fails at runtime with
    // an ENOTFOUND that no build ever catches.
    const destino = plantillaEntorno.match(/^NUXT_API_BASE=(\S+)$/m)?.[1] ?? ''
    const servicio = new URL(destino).hostname

    expect(destino).toBe('http://api:8000')
    expect(compose).toMatch(new RegExp(`^ {2}${servicio}:$`, 'm'))
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
  // h3 decodes the path BEFORE routing, so "/api/%2e%2e/openapi.json" still
  // matches this catch-all while resolving to "/openapi.json" against the
  // backend. Verified by exploiting it against the live Compose before fixing
  // it: it returned the full OpenAPI schema through the public origin. Without
  // these cases the single-origin boundary that the whole design rests on does
  // not exist, and on Cloud Run the backend is left with ingress closed and
  // reachable all the same.
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
})
