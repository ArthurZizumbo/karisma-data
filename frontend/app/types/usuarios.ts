import type { RolUsuario } from '~/types/sesion'

/**
 * Wire contract of the user administration panel.
 *
 * Every name below is the one the backend spells, and that is deliberate. The
 * session type of US-015 does rename its three fields, but a Nitro route does
 * that renaming there; `/api/users` falls through the wildcard proxy, so a
 * translation layer here would only give the same record two vocabularies -the
 * divergence this project already paid for once with `administrador` against
 * `admin`.
 *
 * Nothing in this module can carry a password hash: the backend never selects
 * the column, and no type here declares it.
 */

/** One row of the user administration table, as `GET /api/users` returns it. */
export interface UsuarioAdmin {
  readonly id: string
  readonly username: string
  readonly email: string
  readonly full_name: string
  readonly role: RolUsuario
  readonly disabled: boolean
  readonly created_at: string
  readonly updated_at: string
}

/**
 * One page of the list.
 *
 * An object and not a bare array: turning an array response into an object
 * later is a breaking change for the client, and the shape costs nothing today.
 */
export interface PaginaUsuarios {
  readonly items: readonly UsuarioAdmin[]
  readonly total: number
  readonly limit: number
  readonly offset: number
}

/**
 * The four states the panel can be in. `listo` is the only happy one.
 *
 * `vacio` is reachable only through the client side filter: the endpoint always
 * returns at least the administrator who asked, so an empty list has a cause
 * the reader produced and can undo.
 */
export type EstadoPanel = 'cargando' | 'listo' | 'vacio' | 'error'

/**
 * Something the administrator asked for and has not confirmed yet.
 *
 * A discriminated union so the dialog cannot forget a case: adding a variant
 * breaks the exhaustive switch at build time instead of quietly rendering the
 * copy of another action.
 */
export type AccionUsuario
  = | { readonly tipo: 'cambiar-rol', readonly usuario: UsuarioAdmin, readonly rolNuevo: RolUsuario }
    | { readonly tipo: 'desactivar', readonly usuario: UsuarioAdmin }
    | { readonly tipo: 'reactivar', readonly usuario: UsuarioAdmin }

/** The three business codes `UserErrorCode` returns in `detail`. */
export type CodigoConflicto
  = | 'admin_no_puede_degradarse'
    | 'admin_no_puede_desactivarse'
    | 'usuario_no_encontrado'

/**
 * Business conflict reported by the backend, ready to be rendered.
 *
 * The interface hides the controls that would produce one, but the conflict is
 * still reachable -two tabs, a stale list, a `curl`- so it is a state of the
 * screen and not an impossible branch. The backend is the only authority on it.
 */
export interface ConflictoUsuario {
  readonly codigo: CodigoConflicto
  readonly username: string
}
