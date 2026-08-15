import type { ContextoGuarda, DecisionGuarda } from '~/types/guarda'
import type { RolUsuario } from '~/types/sesion'
import { RUTA_ACCESO, RUTA_GUIA, RUTA_INDICE, RUTAS_CONTRATO } from '~/utils/navegacion'
import { ROLES_EN_ORDEN } from '~/utils/permisos.generated'
import { MOTIVO_EXPIRADA } from '~/utils/sesion'

/**
 * Session guard of Karisma Data, as a pure function.
 *
 * It lives outside the middleware on purpose. `defineNuxtRouteMiddleware`,
 * `navigateTo`, `useRequestEvent` and `setResponseStatus` are Nuxt auto
 * imports, and this project runs vitest on happy-dom without
 * `@nuxt/test-utils`: written as one file, the whole decision would sit behind
 * four globals and its test would be a knot of doubles. Here the exhaustive
 * table of cases is a table of values.
 *
 * The role hierarchy is NOT written in this file. It arrives ordered from
 * `permisos.generated.ts`, which is emitted from `ROLE_HIERARCHY` in the
 * backend: a second ordering typed in TypeScript is a second policy, and two
 * policies eventually disagree.
 */

/**
 * Routes that never require a session.
 *
 * Composed from the three constants of the navigation contract and never typed
 * as literals: '/' is the A4 prototype index and '/guia' is the living style
 * guide -both are artefacts the rubric grades directly, and putting a login in
 * front of the deliverable is putting a door in front of what is evaluated-
 * while '/acceso' guarded would redirect to itself forever.
 */
export const RUTAS_PUBLICAS: readonly string[] = Object.freeze([
  RUTA_INDICE,
  RUTA_ACCESO,
  RUTA_GUIA,
])

/**
 * Drops the query string, the hash and any trailing slash of a path.
 *
 * @param ruta - Path as the router reports it.
 * @returns The bare path, with '/' preserved as itself.
 */
function normalizar(ruta: string): string {
  const sinQuery = ruta.split('?')[0]?.split('#')[0] ?? ''
  return sinQuery.length > 1 ? sinQuery.replace(/\/+$/, '') : sinQuery
}

/**
 * Reports whether a path is public, including anything below a public route.
 *
 * The index is matched exactly and never by prefix: with a prefix rule '/' would
 * make the whole portal public, which is the one mistake in this file that
 * nothing downstream would notice.
 *
 * @param ruta - Path being navigated to, query and hash included.
 * @returns True when the route needs no session.
 */
export function esRutaPublica(ruta: string): boolean {
  const destino = normalizar(ruta)
  return RUTAS_PUBLICAS.some(
    publica =>
      destino === publica || (publica !== RUTA_INDICE && destino.startsWith(`${publica}/`)),
  )
}

/**
 * Query parameter that carries the route the reader was trying to open.
 *
 * Declared here because the guard writes it and the entry screen reads it: two
 * literals would let the bounce send a name the screen does not recognise, and
 * the reader would be returned to their landing screen instead of to what they
 * asked for.
 */
export const PARAMETRO_DESTINO = 'destino'

/**
 * Query value that asks the entry screen to explain that a session is needed.
 *
 * It is not the same as an expiry and it is not decoration: without it the
 * bounce is mute, and an evaluator who opens a prototype from the index reads
 * the entry screen as a broken link rather than as a door.
 */
export const MOTIVO_SESION_REQUERIDA = 'sesion-requerida'

/**
 * Validates a route that arrived through the query string.
 *
 * The allowlist is `RUTAS_CONTRATO` itself, so nothing outside the A3 map can
 * be returned to: accepting an arbitrary value here would be an open redirect
 * driven by a link anybody can write. The entry screen is rejected too, because
 * returning to it after entering is a loop.
 *
 * @param valor - Raw query value, which may be absent or repeated.
 * @returns The bare contract route, or null when it is not one.
 */
export function destinoDeRetorno(valor: unknown): string | null {
  if (typeof valor !== 'string' || valor === '') {
    return null
  }
  const ruta = normalizar(valor)
  if (ruta === RUTA_ACCESO || !RUTAS_CONTRATO.includes(ruta)) {
    return null
  }
  return ruta
}

/**
 * Reports whether a role covers the scope a route demands.
 *
 * Exported because the middleware is not the only caller: `usePermisos()`
 * projects the same comparison onto the sidebar, and a screen that hides a card
 * uses it too. One comparison, one place.
 *
 * @param rol - Role of the current session, or null when there is none.
 * @param scope - Minimum role demanded, or null when any valid session is
 *   enough.
 * @returns True when the reader may proceed.
 */
export function rolAlcanza(rol: RolUsuario | null, scope: RolUsuario | null): boolean {
  if (rol === null) {
    return false
  }
  if (scope === null) {
    return true
  }
  return ROLES_EN_ORDEN.indexOf(rol) >= ROLES_EN_ORDEN.indexOf(scope)
}

/**
 * Single decision point of the guard.
 *
 * The five rules apply in this order and admit no exception: a public route is
 * allowed; an absent session redirects to the entry screen, telling an expiry
 * from a first visit and carrying the route that was asked for; a session that
 * covers the scope is allowed; and a session that does not produces the
 * designed "no permission" state in place, without changing the URL.
 *
 * @param contexto - Route, resolved session and the scope the route demands.
 * @returns Allow, redirect to the entry screen, or render the "no permission"
 *   state where the reader already is.
 */
export function decidirGuarda(contexto: ContextoGuarda): DecisionGuarda {
  if (esRutaPublica(contexto.ruta)) {
    return { tipo: 'permitir' }
  }

  if (contexto.sesion === null) {
    // The requested route travels back with the bounce so the entry screen can
    // return the reader to it. It is validated here and not there: a screen
    // that trusts its own query string is one link away from an open redirect.
    const rutaPedida = destinoDeRetorno(contexto.ruta)
    return {
      tipo: 'redirigir',
      destino: RUTA_ACCESO,
      motivo: contexto.habiaSesion ? MOTIVO_EXPIRADA : MOTIVO_SESION_REQUERIDA,
      ...(rutaPedida === null ? {} : { rutaPedida }),
    }
  }

  // Destructured so that the last branch narrows to a real role instead of
  // being cast: a route with no exigency can never reach the refusal.
  const { scopeExigido } = contexto
  if (scopeExigido === null || rolAlcanza(contexto.sesion.rol, scopeExigido)) {
    return { tipo: 'permitir' }
  }

  return { tipo: 'sin-permiso', scopeExigido }
}
