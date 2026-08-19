import type { H3Event } from 'h3'
import type { SesionUsuario } from '~/types/sesion'
import { aSesionUsuario, estadoDeFallo } from '~/utils/sesion'
import { tokenDeIdentidad } from './identidadCloudRun'

/**
 * Server side of the session: the cookie, the origin check and the second call
 * to the backend.
 *
 * The three routes under `server/api/auth/` and the `/api/**` proxy share this
 * module so that the four places that touch the token agree by construction.
 * The token itself never leaves this side of the process: it goes into the
 * cookie and into the `Authorization` header of the forwarded request, and
 * nothing Nitro returns to the browser ever contains it.
 */

/** Name of the httpOnly cookie that carries the JWT. The client never reads it. */
export const NOMBRE_COOKIE_SESION = 'karisma_sesion'

/**
 * Lifetime in seconds. Mirrors ACCESS_TOKEN_EXPIRE_MINUTES on the backend.
 *
 * The cookie dies exactly when the token dies. A longer cookie would leave the
 * browser holding a credential the API already rejects, and the reader would
 * meet a 401 on a screen that believed it had a session.
 */
export const VIDA_COOKIE_SEGUNDOS = 1800

/** Methods that cannot change state, and therefore need no origin check. */
const METODOS_SEGUROS: readonly string[] = Object.freeze(['GET', 'HEAD', 'OPTIONS'])

/** Attributes of the session cookie, fixed by the acceptance criteria. */
export interface OpcionesCookieSesion {
  readonly httpOnly: true
  readonly sameSite: 'strict'
  readonly path: '/'
  readonly maxAge: number
  readonly secure: boolean
}

/**
 * Attributes the session cookie is written with.
 *
 * `secure` follows the protocol of the request and not `import.meta.dev`. Under
 * Docker Compose the container serves the production build over
 * http://localhost:3000, so `import.meta.dev` is false there and a Secure
 * cookie would simply not be stored: the login would work under `pnpm dev` and
 * do nothing under `make dev`, which is the environment where the captures are
 * recorded.
 *
 * @param event - Request that is being answered.
 * @returns The attributes, ready for setCookie.
 */
export function opcionesDeCookie(event: H3Event): OpcionesCookieSesion {
  return {
    httpOnly: true,
    sameSite: 'strict',
    path: '/',
    maxAge: VIDA_COOKIE_SEGUNDOS,
    secure: getRequestURL(event).protocol === 'https:',
  }
}

/**
 * Stores the token of a freshly opened session.
 *
 * @param event - Request that is being answered.
 * @param token - JWT emitted by the backend.
 */
export function establecerSesion(event: H3Event, token: string): void {
  setCookie(event, NOMBRE_COOKIE_SESION, token, opcionesDeCookie(event))
}

/**
 * Drops the session cookie.
 *
 * Nothing else happens on the way out: the JWT is stateless and there is no
 * revocation list, which is the other half of a session that is never renewed.
 *
 * @param event - Request that is being answered.
 */
export function borrarSesion(event: H3Event): void {
  deleteCookie(event, NOMBRE_COOKIE_SESION, opcionesDeCookie(event))
}

/**
 * Reads the token of the current session.
 *
 * @param event - Request that is being answered.
 * @returns The JWT, or undefined when the visitor has no session.
 */
export function leerTokenDeSesion(event: H3Event): string | undefined {
  return getCookie(event, NOMBRE_COOKIE_SESION)
}

/**
 * Second half of the CSRF defence required by QA-M2 of the US-001 handoff.
 *
 * `SameSite=Strict` is the browser's half; this is the server's, because an old
 * browser or an extension may not apply it. It returns false only when the
 * request positively claims a foreign origin. A request with neither
 * Sec-Fetch-Site nor Origin is not a browser navigation and passes: curl, the
 * smoke script and the agent tools all live there.
 *
 * @param event - Request that is being answered.
 * @returns True when nothing in the request claims a foreign origin.
 */
export function esSolicitudDelPropioSitio(event: H3Event): boolean {
  const sitio = getHeader(event, 'sec-fetch-site')
  if (sitio !== undefined && sitio !== '') {
    return sitio === 'same-origin'
  }

  const origen = getHeader(event, 'origin')
  if (origen === undefined || origen === '') {
    return true
  }
  return origen === getRequestURL(event).origin
}

/**
 * Rejects a state changing request that claims a foreign origin.
 *
 * Applied by the proxy and by the three authentication routes alike: the routes
 * are more specific than the catch-all, so a check written only inside the
 * catch-all would leave the login and the logout uncovered, which are precisely
 * the two a cross site form would aim at.
 *
 * @param event - Request that is being answered.
 * @throws A 403 when the request is unsafe and comes from somewhere else.
 */
export function exigirOrigenPropio(event: H3Event): void {
  if (METODOS_SEGUROS.includes(event.method) || esSolicitudDelPropioSitio(event)) {
    return
  }
  throw createError({
    statusCode: 403,
    statusMessage: 'Forbidden',
    data: { codigo: 'origen_ajeno' },
  })
}

/**
 * Reads the profile the token belongs to.
 *
 * This is the second call the entry routes make, and the reason they make it:
 * decoding the claims here would mean writing the claim parser a second time,
 * in a second language, and exposing the token to do it. One extra hop inside
 * the same network is cheaper than either.
 *
 * @param apiBase - Base URL of the FastAPI service.
 * @param token - JWT just emitted for this session.
 * @returns The session as the browser will see it, with no token in it.
 */
export async function leerPerfilDeSesion(
  apiBase: string,
  token: string,
  apiAudience?: string,
): Promise<SesionUsuario> {
  const headers: Record<string, string> = { authorization: `Bearer ${token}` }
  if (apiAudience) {
    // The failure is not swallowed, and that is the whole point: forwarding
    // without the identity token reaches a private Cloud Run service, which
    // answers 403. The caller would then report a rejected session -wrong
    // credentials, expired token- for what is an unreachable metadata server,
    // and the interface would tell the user to log in again over and over. The
    // three callers of this function turn a throw into a 502, which names the
    // layer that actually broke.
    const idToken = await tokenDeIdentidad(apiAudience)
    headers['x-serverless-authorization'] = `Bearer ${idToken}`
  }
  const perfil = await $fetch(`${apiBase}/api/auth/me`, {
    headers,
  })
  return aSesionUsuario(perfil)
}

/**
 * Translates an upstream failure into the answer the browser receives.
 *
 * The `detail` of the backend is never relayed. It is a Spanish literal fixed
 * by the acceptance criteria and the interface is bilingual: what travels is
 * the status and a code, and the screen resolves its own wording.
 *
 * @param error - Value thrown by the call to the backend.
 * @param codigoAusente - Code to report when the backend answered 404, which
 *   only the demonstration route can produce.
 * @returns The error to throw back to the browser.
 */
export function fallaDeAutenticacion(error: unknown, codigoAusente?: string): Error {
  const estado = estadoDeFallo(error)

  if (estado === 401) {
    return createError({
      statusCode: 401,
      statusMessage: 'Unauthorized',
      data: { codigo: 'credenciales_invalidas' },
    })
  }
  if (estado === 404 && codigoAusente !== undefined) {
    return createError({
      statusCode: 404,
      statusMessage: 'Not Found',
      data: { codigo: codigoAusente },
    })
  }
  return createError({
    statusCode: 502,
    statusMessage: 'Bad Gateway',
    data: { codigo: 'servicio_no_disponible' },
  })
}
