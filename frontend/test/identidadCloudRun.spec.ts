import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import {
  limpiarCacheDeIdentidad,
  tokenDeIdentidad,
  URL_METADATOS,
} from '../server/utils/identidadCloudRun'

/**
 * Creates a mock unverified JWT string with a specific expiration timestamp in seconds.
 *
 * @param expSeconds Expiration timestamp in seconds since epoch.
 * @returns Serialized fake JWT.
 */
function crearJwtConExpiracion(expSeconds: number): string {
  const header = Buffer.from(JSON.stringify({ alg: 'RS256', typ: 'JWT' })).toString('base64url')
  const payload = Buffer.from(JSON.stringify({ exp: expSeconds, aud: 'https://ejemplo.com' })).toString('base64url')
  const signature = Buffer.from('firma-falsa').toString('base64url')
  return `${header}.${payload}.${signature}`
}

describe('identidadCloudRun', () => {
  beforeEach(() => {
    limpiarCacheDeIdentidad()
    vi.restoreAllMocks()
  })

  afterEach(() => {
    limpiarCacheDeIdentidad()
    vi.restoreAllMocks()
  })

  it('pide el token con Metadata-Flavor: Google y la audiencia en la consulta', async () => {
    const aud = 'https://karisma-api-xyz.a.run.app'
    const expEnElFuturo = Math.floor(Date.now() / 1000) + 3600
    const tokenSimulado = crearJwtConExpiracion(expEnElFuturo)

    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      statusText: 'OK',
      text: async () => tokenSimulado,
    })
    vi.stubGlobal('fetch', mockFetch)

    const token = await tokenDeIdentidad(aud)

    expect(token).toBe(tokenSimulado)
    expect(mockFetch).toHaveBeenCalledTimes(1)
    expect(mockFetch).toHaveBeenCalledWith(
      `${URL_METADATOS}?audience=${encodeURIComponent(aud)}`,
      {
        headers: {
          'Metadata-Flavor': 'Google',
        },
      },
    )
  })

  it('dos llamadas seguidas con la misma audiencia hacen una sola peticion (cache)', async () => {
    const aud = 'https://karisma-api-xyz.a.run.app'
    const expEnElFuturo = Math.floor(Date.now() / 1000) + 3600
    const tokenSimulado = crearJwtConExpiracion(expEnElFuturo)

    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      statusText: 'OK',
      text: async () => tokenSimulado,
    })
    vi.stubGlobal('fetch', mockFetch)

    const primerToken = await tokenDeIdentidad(aud)
    const segundoToken = await tokenDeIdentidad(aud)

    expect(primerToken).toBe(tokenSimulado)
    expect(segundoToken).toBe(tokenSimulado)
    expect(mockFetch).toHaveBeenCalledTimes(1)
  })

  it('con el token a menos de MARGEN_DE_RENOVACION_MS del exp renueva pidiendo uno nuevo', async () => {
    const aud = 'https://karisma-api-xyz.a.run.app'
    // Token expires in 30 seconds (less than 60s margin)
    const expCasiVencido = Math.floor((Date.now() + 30_000) / 1000)
    const primerToken = crearJwtConExpiracion(expCasiVencido)

    const expRenovado = Math.floor((Date.now() + 3600_000) / 1000)
    const segundoToken = crearJwtConExpiracion(expRenovado)

    const mockFetch = vi.fn()
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        statusText: 'OK',
        text: async () => primerToken,
      })
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        statusText: 'OK',
        text: async () => segundoToken,
      })
    vi.stubGlobal('fetch', mockFetch)

    const res1 = await tokenDeIdentidad(aud)
    expect(res1).toBe(primerToken)
    expect(mockFetch).toHaveBeenCalledTimes(1)

    // Second call should renew because remaining lifetime is < MARGEN_DE_RENOVACION_MS
    const res2 = await tokenDeIdentidad(aud)
    expect(res2).toBe(segundoToken)
    expect(mockFetch).toHaveBeenCalledTimes(2)
  })

  it('audiencias distintas no comparten entrada de cache', async () => {
    const aud1 = 'https://servicio-1.a.run.app'
    const aud2 = 'https://servicio-2.a.run.app'
    const expEnElFuturo = Math.floor(Date.now() / 1000) + 3600
    const token1 = crearJwtConExpiracion(expEnElFuturo)
    const token2 = crearJwtConExpiracion(expEnElFuturo)

    const mockFetch = vi.fn()
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        statusText: 'OK',
        text: async () => token1,
      })
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        statusText: 'OK',
        text: async () => token2,
      })
    vi.stubGlobal('fetch', mockFetch)

    const res1 = await tokenDeIdentidad(aud1)
    const res2 = await tokenDeIdentidad(aud2)

    expect(res1).toBe(token1)
    expect(res2).toBe(token2)
    expect(mockFetch).toHaveBeenCalledTimes(2)
  })

  it('lanza error si el servidor de metadatos responde con error HTTP', async () => {
    const aud = 'https://karisma-api-xyz.a.run.app'

    const mockFetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 404,
      statusText: 'Not Found',
      text: async () => 'Error',
    })
    vi.stubGlobal('fetch', mockFetch)

    await expect(tokenDeIdentidad(aud)).rejects.toThrow(/Error al obtener token de identidad/)
  })

  it('limpiarCacheDeIdentidad vacia las entradas cacheadas', async () => {
    const aud = 'https://karisma-api-xyz.a.run.app'
    const expEnElFuturo = Math.floor(Date.now() / 1000) + 3600
    const token = crearJwtConExpiracion(expEnElFuturo)

    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      statusText: 'OK',
      text: async () => token,
    })
    vi.stubGlobal('fetch', mockFetch)

    await tokenDeIdentidad(aud)
    expect(mockFetch).toHaveBeenCalledTimes(1)

    limpiarCacheDeIdentidad()

    await tokenDeIdentidad(aud)
    expect(mockFetch).toHaveBeenCalledTimes(2)
  })
})
