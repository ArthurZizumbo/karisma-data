// GENERATED FILE - do not edit by hand.
// Source:     backend/app/core/permissions.py (SCOPE_REGISTRY, US-016)
//             backend/app/core/scopes.py      (ROLE_HIERARCHY, US-016)
//             frontend/app/utils/navegacion.ts (MODULOS, the A3 site map)
// Generator:  scripts/generar_permisos_ui.py
// Regenerate: make permisos-ui
import type { RolUsuario } from '~/types/sesion'

/** The four roles, from lowest to highest, mirroring ROLE_HIERARCHY. */
export const ROLES_EN_ORDEN: readonly RolUsuario[] = Object.freeze([
  'operativo',
  'analista',
  'directivo',
  'admin',
])

/**
 * Minimum role of every module and every branch of the A3 map, keyed by
 * its A3 id. A module demands the lowest of its branches; a branch demands the
 * highest of the endpoints it calls.
 */
export const SCOPE_POR_RAMA: Readonly<Record<string, RolUsuario | null>> = Object.freeze({
  '1': null,
  '2': null,
  '3': null,
  '4': 'admin',
  '1.1': null,
  '1.2': null,
  '1.3': null,
  '1.4': null,
  '1.5': null,
  '2.1': null,
  '2.2': 'operativo',
  '2.3': 'analista',
  '2.4': 'analista',
  '3.1': null,
  '3.2': null,
  '3.3': null,
  '4.1': 'admin',
  '4.2': 'admin',
  '4.3': 'admin',
  '4.4': 'admin',
})

/**
 * Minimum role of every route of the navigation contract, keyed by path.
 * '/acceso' is absent on purpose: the entry screen is public, and guarding it
 * would redirect it to itself.
 */
export const SCOPE_POR_RUTA: Readonly<Record<string, RolUsuario | null>> = Object.freeze({
  '/inicio': null,
  '/exploracion': null,
  '/gobierno': null,
  '/administracion': 'admin',
  '/exploracion/exportar': 'analista',
  '/exploracion/tableros': 'analista',
  '/asistente': null,
})

/**
 * Endpoints every branch consumes, as 'METHOD /path/template'.
 *
 * Only test/permisos.spec.ts reads this: it crosses the list against the matrix
 * published in docs/security.md, so a scope changed in the backend and not
 * regenerated here turns the suite red instead of hiding a module from the
 * wrong people.
 */
export const ENDPOINTS_POR_RAMA: Readonly<Record<string, readonly string[]>> = Object.freeze({
  '1.1': [
    'GET /api/catalog/search',
  ],
  '1.2': [],
  '1.3': [],
  '1.4': [],
  '1.5': [
    'GET /api/auth/me',
  ],
  '2.1': [
    'GET /api/catalog/search',
    'GET /api/catalog/{entry_id}',
  ],
  '2.2': [
    'POST /api/query/records',
  ],
  '2.3': [
    'POST /api/export',
    'GET /api/export/{job_id}',
  ],
  '2.4': [
    'GET /api/metrics/series',
    'POST /api/metrics/aggregate',
  ],
  '3.1': [
    'GET /api/catalog/{entry_id}',
  ],
  '3.2': [],
  '3.3': [
    'GET /api/catalog/search',
  ],
  '4.1': [
    'GET /api/users',
    'POST /api/users',
    'PATCH /api/users/{user_id}',
    'DELETE /api/users/{user_id}',
  ],
  '4.2': [],
  '4.3': [],
  '4.4': [],
  'asistente': [
    'POST /api/chat',
  ],
})