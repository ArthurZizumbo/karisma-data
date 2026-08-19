/**
 * Cloud Run metadata server token fetcher and in-memory cache.
 *
 * Used by the Nitro proxy handler (server/api/[...].ts) to attach an ID token
 * to the X-Serverless-Authorization header when calling private Cloud Run services.
 */

/**
 * Failure of the metadata server, told apart from any other error.
 *
 * The callers need the distinction: a session handler answers 401 when the
 * credential is wrong and 502 when the identity layer is unreachable, and
 * without a type to check on, both collapse into "log in again", which is the
 * one thing the user cannot fix.
 */
export class ErrorDeIdentidad extends Error {
  constructor(mensaje: string) {
    super(mensaje)
    this.name = 'ErrorDeIdentidad'
  }
}

interface EntradaCache {
  token: string
  expiracionMs: number
}

/** In-memory cache of ID tokens keyed by audience. */
const cacheDeTokens = new Map<string, EntradaCache>()

/** Metadata server endpoint on Cloud Run. Only reachable inside GCP runtime. */
export const URL_METADATOS = 'http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/identity'

/** Margin before expiration when token should be renewed (1 minute). */
export const MARGEN_DE_RENOVACION_MS = 60_000

/**
 * Extracts expiration timestamp (in ms) from an unverified JWT token payload.
 *
 * @param token Raw JWT string.
 * @returns Expiration timestamp in milliseconds since epoch, or 0 if unparseable.
 */
function extraerExpiracion(token: string): number {
  try {
    const partes = token.split('.')
    const partePayload = partes[1]
    if (!partePayload) {
      return 0
    }
    const cargaCruda = Buffer.from(partePayload, 'base64url').toString('utf8')
    const carga = JSON.parse(cargaCruda) as { exp?: number }
    return typeof carga.exp === 'number' ? carga.exp * 1000 : 0
  }
  catch {
    return 0
  }
}

/**
 * Fetches or returns a cached ID token for the specified audience from the
 * Cloud Run instance metadata server.
 *
 * Throws if the metadata server does not answer or returns an error status.
 *
 * @param audiencia Expected audience (typically the target Cloud Run URL).
 * @returns Fresh or valid cached ID token.
 */
export async function tokenDeIdentidad(audiencia: string): Promise<string> {
  const ahora = Date.now()
  const cacheado = cacheDeTokens.get(audiencia)
  if (cacheado && cacheado.expiracionMs - ahora > MARGEN_DE_RENOVACION_MS) {
    return cacheado.token
  }

  const url = `${URL_METADATOS}?audience=${encodeURIComponent(audiencia)}`
  let respuesta: Response
  try {
    respuesta = await fetch(url, {
      headers: {
        'Metadata-Flavor': 'Google',
      },
    })
  }
  catch (causa) {
    // Outside Cloud Run the host does not even resolve, and that network error
    // has to arrive typed like the HTTP one below: the caller decides by type,
    // not by reading a message.
    throw new ErrorDeIdentidad(`Error al obtener token de identidad: ${String(causa)}`)
  }

  if (!respuesta.ok) {
    throw new ErrorDeIdentidad(`Error al obtener token de identidad: ${respuesta.status} ${respuesta.statusText}`)
  }

  const token = await respuesta.text()
  const expiracionMs = extraerExpiracion(token)
  cacheDeTokens.set(audiencia, { token, expiracionMs })
  return token
}

/**
 * Clears the in-memory token cache. Intended for testing purposes.
 */
export function limpiarCacheDeIdentidad(): void {
  cacheDeTokens.clear()
}
