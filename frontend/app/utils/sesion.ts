import type { RolUsuario, SesionUsuario } from '~/types/sesion'

/**
 * Pure session helpers, shared by the browser and by the Nitro routes.
 *
 * Nothing here touches an H3 event or a Vue ref, which is what lets the same
 * three rules -what a role is, where a role lands, how a profile is read- hold
 * on both sides of the proxy instead of being written twice and drifting.
 */

/** The four roles, in the order the demonstration selector offers them. */
export const ROLES: readonly RolUsuario[] = Object.freeze([
  'operativo',
  'analista',
  'directivo',
  'admin',
])

/**
 * Landing route of each role.
 *
 * Every value is a route of `RUTAS_CONTRATO`, and a test pins that: a landing
 * route that no page file serves turns a correct login into a 404, which is the
 * one failure that looks like a broken product on the first click.
 *
 * US-027 changes this table and nothing else when the four workspaces get their
 * own screens.
 */
const DESTINOS: Readonly<Record<RolUsuario, string>> = Object.freeze({
  operativo: '/inicio',
  analista: '/exploracion',
  directivo: '/exploracion/tableros',
  admin: '/administracion',
})

/**
 * Query value that asks the entry screen to explain that the session expired.
 *
 * Declared here because US-017 writes the redirect and this screen reads it:
 * two literals would let the guard send a reason the screen does not recognise.
 */
export const MOTIVO_EXPIRADA = 'expirada'

/**
 * Route a role lands on right after entering.
 *
 * @param rol - Role of the session that was just opened.
 * @returns Path of the landing screen.
 */
export function destinoPorRol(rol: RolUsuario): string {
  return DESTINOS[rol]
}

/**
 * Narrows an arbitrary value to a role the portal really has.
 *
 * @param valor - Value read from the network or from a query string.
 * @returns True when the value is one of the four scopes of the backend.
 */
export function esRolUsuario(valor: unknown): valor is RolUsuario {
  return typeof valor === 'string' && (ROLES as readonly string[]).includes(valor)
}

/**
 * Reads the HTTP status out of whatever the fetch layer threw.
 *
 * ofetch reports it as `status`, h3 as `statusCode` and a plain Response as
 * `response.status`; the three shapes cross this codebase and picking only one
 * of them turns an expected 401 into a generic server error.
 *
 * @param error - Value caught from a failed request.
 * @returns The status code, or 0 when the failure carries none, which is what a
 *   network error looks like.
 */
export function estadoDeFallo(error: unknown): number {
  const fallo = error as {
    status?: unknown
    statusCode?: unknown
    response?: { status?: unknown }
  } | null
  for (const candidato of [fallo?.status, fallo?.statusCode, fallo?.response?.status]) {
    if (typeof candidato === 'number') {
      return candidato
    }
  }
  return 0
}

/**
 * Maps the body of `GET /api/auth/me` to a session.
 *
 * It validates instead of casting because the role decides the landing route
 * and the visible modules: a spelling the portal does not know -`administrador`
 * is the one already living in the navigation contract- would produce a session
 * that navigates nowhere.
 *
 * @param perfil - Body received from the backend.
 * @returns The session of that profile.
 * @throws When the body is not a profile of the contract.
 */
export function aSesionUsuario(perfil: unknown): SesionUsuario {
  const dato = perfil as { username?: unknown, full_name?: unknown, role?: unknown } | null
  const usuario = typeof dato?.username === 'string' ? dato.username : ''
  const rol = dato?.role

  if (usuario === '' || !esRolUsuario(rol)) {
    throw new Error('perfil fuera del contrato de /api/auth/me')
  }

  // A profile with no readable name is signed in all the same: the chrome shows
  // the login name rather than an empty space where a person should be.
  const nombre = typeof dato?.full_name === 'string' && dato.full_name !== ''
    ? dato.full_name
    : usuario

  return { usuario, nombre, rol }
}
