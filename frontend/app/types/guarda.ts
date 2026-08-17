import type { RolUsuario, SesionUsuario } from '~/types/sesion'

/**
 * Session guard contract of Karisma Data.
 *
 * The three shapes below are everything the guard needs in order to decide, and
 * everything it produces. Nothing here knows about the router, the network or
 * Nuxt: the decision is a value, so the exhaustive table of cases is a table of
 * inputs and expected values rather than a set of doubles.
 */

/**
 * Why the guard is sending the reader back to the entry screen.
 *
 * The bounce is never mute. `expirada` is a session that ended and `sesion-requerida`
 * is a first visit to a screen that needs one: told apart, the first reader is
 * explained and the second one is invited, and neither reads the redirect as a
 * broken link.
 */
export type MotivoDeSalida = 'expirada' | 'sesion-requerida'

/**
 * What the guard decided for one navigation.
 *
 * A discriminated union so the middleware cannot forget a case: adding a
 * variant breaks the exhaustive check at build time instead of falling through
 * to "allow", which is the failure mode a boolean would have.
 */
export type DecisionGuarda
  = | { readonly tipo: 'permitir' }
    | {
        readonly tipo: 'redirigir'
        /** Screen the reader is sent to, which is always the entry one. */
        readonly destino: string
        readonly motivo: MotivoDeSalida
        /**
         * Route that was asked for, so the entry screen can give it back.
         *
         * Absent when the requested path is not a route of the contract: it
         * travels through the query string, and anything accepted there that
         * the contract does not list is an open redirect.
         */
        readonly rutaPedida?: string
      }
    | { readonly tipo: 'sin-permiso', readonly scopeExigido: RolUsuario }

/** Everything the decision depends on. No Nuxt, no router, no network. */
export interface ContextoGuarda {
  /** Path being navigated to. Query string and hash are tolerated. */
  readonly ruta: string
  /** Session already resolved, or null when there is none. */
  readonly sesion: SesionUsuario | null
  /**
   * True when a session existed in local state before this navigation.
   *
   * It is what tells an expiry from a first visit: the same absence of session
   * means "your session ended" for one reader and "you never entered" for the
   * other, and telling them the same thing is how a portal makes a legitimate
   * user believe the product is broken.
   */
  readonly habiaSesion: boolean
  /**
   * Minimum role the route demands, or null when any valid session is enough.
   *
   * It comes from the generated map. The guard never resolves it itself: that
   * would be a second copy of the permission matrix.
   */
  readonly scopeExigido: RolUsuario | null
}

/** Route the reader tried to open and could not. Rendered by the portal layout. */
export interface BloqueoDeRuta {
  readonly ruta: string
  readonly scopeExigido: RolUsuario
}
