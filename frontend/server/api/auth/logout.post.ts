import { borrarSesion, exigirOrigenPropio } from '../../utils/sesion'

/**
 * Closes the session.
 *
 * It drops the cookie and answers 204 without talking to the backend. The JWT
 * is stateless and there is no revocation list, so there is nothing upstream to
 * tell: inventing a revocation call would add server state to a design that
 * deliberately has none, and would fail on a cold start of a scaled-to-zero
 * service for no gain.
 *
 * The token still exists until it expires. That is what a session with no
 * renewal costs, and the thirty minute lifetime is what bounds it.
 */
export default defineEventHandler((event) => {
  exigirOrigenPropio(event)
  borrarSesion(event)
  return sendNoContent(event, 204)
})
