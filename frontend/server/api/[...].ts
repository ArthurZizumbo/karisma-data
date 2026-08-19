import { tokenDeIdentidad } from '../utils/identidadCloudRun'
import { exigirOrigenPropio, leerTokenDeSesion } from '../utils/sesion'

/**
 * Runtime proxy for every /api/** request.
 *
 * The browser only ever talks to this origin, so no CORS layer exists anywhere
 * in the stack and the JWT cookie stays httpOnly: this handler is the only
 * place where the token leaves the cookie, and it puts it straight into the
 * Authorization header of the forwarded request.
 *
 * This is a runtime handler and not a `routeRules` proxy on purpose. Route
 * rules are compiled into the Nitro bundle, so their target is frozen at build
 * time: the key `/api/**` cannot be reached by any environment variable name.
 * That is invisible under Docker Compose, where the build already knows the
 * service host, and it breaks on Cloud Run, where `gcloud run deploy --source`
 * accepts no build arguments and the API URL is only known after the backend
 * is deployed. Reading `apiBase` per request keeps a single image valid in
 * every environment, reconfigured with NUXT_API_BASE alone.
 */

/** Prefix this proxy is allowed to forward. Anything else is not ours. */
const PREFIJO = '/api'

/** Placeholder origin: only the resolved pathname is ever used. */
const ORIGEN_DE_RESOLUCION = 'http://placeholder.invalid'

/**
 * Routes Nitro serves itself, which must never be reached through this proxy.
 *
 * Each of them exists to keep the JWT out of the browser: they call the API,
 * put the token in the httpOnly cookie and answer with the session alone. A
 * request that lands here asking for one of them has bypassed that handler by
 * spelling the path differently, and forwarding it would return the raw token
 * to whoever asked. There is no legitimate caller: the browser reaches these
 * three by their real path and Nitro routes them before this file runs.
 */
const RUTAS_PROPIAS_DE_NITRO: ReadonlySet<string> = new Set([
  '/api/auth/token',
  '/api/auth/demo',
  '/api/auth/logout',
])

export default defineEventHandler(async (event) => {
  const { apiBase, apiAudience } = useRuntimeConfig(event) as { apiBase: string, apiAudience?: string }

  const separador = event.path.indexOf('?')
  const rutaCruda = separador === -1 ? event.path : event.path.slice(0, separador)
  const consulta = separador === -1 ? '' : event.path.slice(separador)

  // h3 routes on the RAW path: it does not percent-decode before matching, and
  // neither does `new URL`. Uvicorn decodes exactly once. That asymmetry is the
  // whole problem, and an earlier version of this comment asserted the opposite,
  // which is what kept the defect below invisible.
  //
  // Two consequences, and both are closed by decoding once here, before any
  // decision is taken on the path:
  //
  //  1. `/api/auth%2Fdemo` does not match `server/api/auth/demo.post.ts` -the
  //     encoded slash is not a separator for the router- so it fell through to
  //     this proxy, which forwarded it verbatim to uvicorn, which decoded it
  //     into `/api/auth/demo` and answered with a real JWT. The token came back
  //     to the page as JSON, outside the httpOnly cookie, readable by any script
  //     on it. That is the exact property this whole design exists to deny.
  //  2. `/api/%2e%2e/openapi.json` only collapses to `/openapi.json` -and so
  //     only gets rejected as outside the prefix- once the escapes are gone.
  //     Without the decode it travelled onward and depended on the upstream
  //     refusing it, which is somebody else's decision to change.
  //
  // One decode and no more: uvicorn does one, so a second here would let
  // `%252F` through the same door.
  let rutaDecodificada: string
  try {
    rutaDecodificada = decodeURIComponent(rutaCruda)
  }
  catch {
    // A malformed escape (`%zz`) is not a path this service can reason about.
    throw createError({ statusCode: 400, statusMessage: 'Bad Request' })
  }

  const rutaNormalizada = new URL(rutaDecodificada, ORIGEN_DE_RESOLUCION).pathname

  if (rutaNormalizada !== PREFIJO && !rutaNormalizada.startsWith(`${PREFIJO}/`)) {
    throw createError({ statusCode: 404, statusMessage: 'Not Found' })
  }

  if (RUTAS_PROPIAS_DE_NITRO.has(rutaNormalizada)) {
    throw createError({ statusCode: 404, statusMessage: 'Not Found' })
  }

  // Server half of the CSRF defence of QA-M2. `SameSite=Strict` already keeps
  // the browser from attaching the cookie to a cross site request; this covers
  // the browser that does not apply it. It only rejects a request that claims a
  // foreign origin, so curl, the smoke script and the agent tools still pass.
  exigirOrigenPropio(event)

  let tokenIdentidad: string | undefined
  if (apiAudience) {
    try {
      tokenIdentidad = await tokenDeIdentidad(apiAudience)
    }
    catch {
      throw createError({ statusCode: 502, statusMessage: 'Bad Gateway' })
    }
  }

  // The forwarding headers are rewritten, never relayed. h3 passes through
  // whatever the client sent, so a request could claim any origin IP. Today
  // uvicorn ignores them (`forwarded_allow_ips` defaults to 127.0.0.1), but the
  // moment someone sets FORWARDED_ALLOW_IPS=* -the usual shortcut under Docker-
  // the spoof becomes effective and poisons the logs of every request. It would
  // also poison a per-IP limit on login attempts, which US-001 announced here
  // and US-015 deliberately did not build: the entry is
  // `docs/us-backlog/05-limitacion-de-intentos-de-acceso.md`.
  const solicitud = getRequestURL(event)
  const token = leerTokenDeSesion(event)
  const cabeceras: Record<string, string> = {
    'x-forwarded-for': getRequestIP(event, { xForwardedFor: false }) ?? '',
    'x-forwarded-proto': solicitud.protocol.replace(':', ''),
    'x-forwarded-host': solicitud.host,
    // Emptied on purpose: the RFC 7239 header would otherwise survive untouched
    // and contradict the three above.
    'forwarded': '',
    // The session lives in the cookie and only here does it become a bearer
    // token. Written unconditionally, never relayed: a client that sends its
    // own Authorization would otherwise reach the API with it, and the session
    // would stop living in one place.
    'authorization': token === undefined ? '' : `Bearer ${token}`,
    // The cookie does not travel upstream. The backend has no use for it and a
    // token arriving by two routes ends up written in an upstream log.
    'cookie': '',
  }

  if (tokenIdentidad) {
    cabeceras['x-serverless-authorization'] = `Bearer ${tokenIdentidad}`
  }

  // streamRequest keeps large bodies off the heap: h3 would otherwise buffer the
  // whole payload in memory before forwarding, which both caps this service at
  // its container memory and breaks the duplex streaming the SSE chat needs.
  return proxyRequest(event, `${apiBase}${rutaNormalizada}${consulta}`, {
    streamRequest: true,
    headers: cabeceras,
  })
})
