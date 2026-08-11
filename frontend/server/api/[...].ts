/**
 * Runtime proxy for every /api/** request.
 *
 * The browser only ever talks to this origin, so no CORS layer exists anywhere
 * in the stack and the JWT cookie can stay httpOnly once US-015 introduces it.
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

export default defineEventHandler(async (event) => {
  const { apiBase } = useRuntimeConfig(event)

  const separador = event.path.indexOf('?')
  const rutaCruda = separador === -1 ? event.path : event.path.slice(0, separador)
  const consulta = separador === -1 ? '' : event.path.slice(separador)

  // h3 decodes the path before routing, so `/api/%2e%2e/openapi.json` still
  // matches this catch-all while resolving to `/openapi.json` upstream. Without
  // collapsing the traversal here, every backend route outside /api would be
  // reachable from the public origin and the single-origin boundary that this
  // whole design rests on would not exist.
  const rutaNormalizada = new URL(rutaCruda, ORIGEN_DE_RESOLUCION).pathname

  if (rutaNormalizada !== PREFIJO && !rutaNormalizada.startsWith(`${PREFIJO}/`)) {
    throw createError({ statusCode: 404, statusMessage: 'Not Found' })
  }

  // The forwarding headers are rewritten, never relayed. h3 passes through
  // whatever the client sent, so a request could claim any origin IP. Today
  // uvicorn ignores them (`forwarded_allow_ips` defaults to 127.0.0.1), but the
  // moment someone sets FORWARDED_ALLOW_IPS=* -the usual shortcut under Docker-
  // the spoof becomes effective and poisons both the logs and the login rate
  // limiting that US-015 will hang off the client IP.
  const solicitud = getRequestURL(event)
  const cabeceras: Record<string, string> = {
    'x-forwarded-for': getRequestIP(event, { xForwardedFor: false }) ?? '',
    'x-forwarded-proto': solicitud.protocol.replace(':', ''),
    'x-forwarded-host': solicitud.host,
    // Emptied on purpose: the RFC 7239 header would otherwise survive untouched
    // and contradict the three above.
    'forwarded': '',
  }

  // streamRequest keeps large bodies off the heap: h3 would otherwise buffer the
  // whole payload in memory before forwarding, which both caps this service at
  // its container memory and breaks the duplex streaming the SSE chat needs.
  return proxyRequest(event, `${apiBase}${rutaNormalizada}${consulta}`, {
    streamRequest: true,
    headers: cabeceras,
  })
})
