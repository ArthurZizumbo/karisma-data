import type { ModuloNav, Prototipo } from '~/types/navegacion'

/**
 * Single source of truth for the navigation contract of Karisma Data.
 *
 * The sidebar, the prototype index, the page headings and the end to end smoke
 * script all derive from this module. No route literal is written inside a Vue
 * file: adding a route here is the only way to add a route to the portal, and
 * every entry must point at a branch of the A3 site map.
 *
 * Since the bilingual decision of 10-ago-2026 the module holds no reader facing
 * word either: every label is a translation key resolved by vue-i18n at render
 * time. Routes stay identical in both languages because the i18n strategy is
 * `no_prefix`.
 */

/** Index of the seven prototypes. Not a branch of the A3 map either. */
export const RUTA_INDICE = '/'

/** Entry screen. It frames the portal but it is not a branch of the A3 map. */
export const RUTA_ACCESO = '/acceso'

/** Conversational assistant. Cross cutting to the four categories of the A3 map. */
export const RUTA_ASISTENTE = '/asistente'

/**
 * Living design system of A4. Neither a prototype nor a branch of the A3 map.
 *
 * It stays out of PROTOTIPOS and out of RUTAS_CONTRATO on purpose: the rubric
 * scores prototypes in one section and the style guide in another, so listing
 * the guide as an eighth prototype would blur the two, and putting it in the
 * contract would claim a branch of the A3 map that does not exist.
 */
export const RUTA_GUIA = '/guia'

/**
 * Key of the notice shown on every route so that no screenshot can be read as a
 * live system.
 */
export const CLAVE_AVISO_ALCANCE = 'scope.notice'

/**
 * The nine cards that three or more evaluators asked to duplicate during the A3
 * card sorting. Each one lives in a canonical branch and is also reachable from
 * the other contexts where it was looked for.
 */
export const CLAVES_FACETAS_TRANSVERSALES: readonly string[] = Object.freeze([
  'nav.facets.items.apiConsumption',
  'nav.facets.items.dataQuality',
  'nav.facets.items.preview',
  'nav.facets.items.sourceCatalog',
  'nav.facets.items.myAlerts',
  'nav.facets.items.apiCredentials',
  'nav.facets.items.loadMonitoring',
  'nav.facets.items.permissions',
  'nav.facets.items.exportHistory',
])

/** The four first level categories of the A3 map, in their canonical order. */
export const MODULOS: readonly ModuloNav[] = Object.freeze([
  {
    id: '1',
    claveEtiqueta: 'nav.module.home',
    ruta: '/inicio',
    subrutas: [
      { id: '1.1', claveEtiqueta: 'nav.branch.homeSearch', ruta: '/inicio' },
      { id: '1.2', claveEtiqueta: 'nav.branch.homeRecent', ruta: '/inicio' },
      { id: '1.3', claveEtiqueta: 'nav.branch.homeFavorites', ruta: '/inicio' },
      { id: '1.4', claveEtiqueta: 'nav.branch.homeAlerts', ruta: '/inicio', facetaTransversal: true },
      { id: '1.5', claveEtiqueta: 'nav.branch.homeProfile', ruta: '/inicio' },
    ],
  },
  {
    id: '2',
    claveEtiqueta: 'nav.module.explore',
    ruta: '/exploracion',
    subrutas: [
      { id: '2.1', claveEtiqueta: 'nav.branch.exploreCatalog', ruta: '/exploracion' },
      { id: '2.2', claveEtiqueta: 'nav.branch.exploreQuery', ruta: '/exploracion', facetaTransversal: true },
      { id: '2.3', claveEtiqueta: 'nav.branch.exploreExports', ruta: '/exploracion/exportar', facetaTransversal: true },
      { id: '2.4', claveEtiqueta: 'nav.branch.exploreDashboards', ruta: '/exploracion/tableros' },
    ],
  },
  {
    id: '3',
    claveEtiqueta: 'nav.module.governance',
    ruta: '/gobierno',
    subrutas: [
      { id: '3.1', claveEtiqueta: 'nav.branch.governanceDictionary', ruta: '/gobierno' },
      { id: '3.2', claveEtiqueta: 'nav.branch.governanceLineage', ruta: '/gobierno', facetaTransversal: true },
      { id: '3.3', claveEtiqueta: 'nav.branch.governanceSources', ruta: '/gobierno', facetaTransversal: true },
    ],
  },
  {
    id: '4',
    claveEtiqueta: 'nav.module.administration',
    ruta: '/administracion',
    subrutas: [
      { id: '4.1', claveEtiqueta: 'nav.branch.administrationUsers', ruta: '/administracion', facetaTransversal: true },
      { id: '4.2', claveEtiqueta: 'nav.branch.administrationRequests', ruta: '/administracion' },
      { id: '4.3', claveEtiqueta: 'nav.branch.administrationAudit', ruta: '/administracion' },
      { id: '4.4', claveEtiqueta: 'nav.branch.administrationIntegrations', ruta: '/administracion', facetaTransversal: true },
    ],
  },
])

/**
 * The seven buttons of the index at '/'. Eight routes, seven prototypes:
 * '/exploracion/tableros' is zone C of screen 2, not a prototype of its own,
 * and the A4 rubric scores prototypes.
 */
export const PROTOTIPOS: readonly Prototipo[] = Object.freeze([
  {
    numero: 0,
    claveNombre: 'prototype.name.access',
    ruta: RUTA_ACCESO,
    claveRama: 'prototype.branch.access',
    alcance: 'navegable-sin-datos',
    rolSugerido: 'operativo',
  },
  {
    numero: 1,
    claveNombre: 'nav.module.home',
    ruta: '/inicio',
    claveRama: 'prototype.branch.home',
    alcance: 'navegable-sin-datos',
    rolSugerido: 'operativo',
  },
  {
    numero: 2,
    claveNombre: 'nav.module.explore',
    ruta: '/exploracion',
    claveRama: 'prototype.branch.explore',
    alcance: 'navegable-sin-datos',
    rolSugerido: 'analista',
  },
  {
    numero: 3,
    claveNombre: 'nav.module.governance',
    ruta: '/gobierno',
    claveRama: 'prototype.branch.governance',
    alcance: 'navegable-sin-datos',
    rolSugerido: 'analista',
  },
  {
    numero: 4,
    claveNombre: 'nav.assistant.label',
    ruta: RUTA_ASISTENTE,
    claveRama: 'prototype.branch.assistant',
    alcance: 'navegable-sin-datos',
    rolSugerido: 'directivo',
  },
  {
    numero: 5,
    claveNombre: 'nav.module.administration',
    ruta: '/administracion',
    claveRama: 'prototype.branch.administration',
    alcance: 'navegable-sin-datos',
    rolSugerido: 'admin',
  },
  {
    numero: 6,
    claveNombre: 'prototype.name.export',
    ruta: '/exploracion/exportar',
    claveRama: 'prototype.branch.export',
    alcance: 'navegable-sin-datos',
    rolSugerido: 'analista',
  },
])

/**
 * The eight routes of the contract, derived from the modules so the list can
 * never drift from the sidebar. Sub branches that still live inside their module
 * landing screen collapse into a single route.
 */
export const RUTAS_CONTRATO: readonly string[] = Object.freeze(
  [
    RUTA_ACCESO,
    ...MODULOS.flatMap(modulo => [modulo.ruta, ...modulo.subrutas.map(subruta => subruta.ruta)]),
    RUTA_ASISTENTE,
  ].filter((ruta, indice, todas) => todas.indexOf(ruta) === indice),
)

/** Drops the query string, the hash and any trailing slash of a path. */
function normalizarRuta(rutaActual: string): string {
  const sinQuery = rutaActual.split('?')[0]?.split('#')[0] ?? ''
  return sinQuery.length > 1 ? sinQuery.replace(/\/+$/, '') : sinQuery
}

/**
 * Module whose second level must be revealed for a given path.
 *
 * Matching is done by route prefix and the index is excluded on purpose: '/' is
 * not part of any module. The function is pure so its test does not mount Vue,
 * and so the sidebar derives the active module instead of storing it.
 */
export function moduloActivo(rutaActual: string): ModuloNav | undefined {
  const ruta = normalizarRuta(rutaActual)
  if (!ruta || ruta === RUTA_INDICE) {
    return undefined
  }
  return MODULOS.find(modulo => ruta === modulo.ruta || ruta.startsWith(`${modulo.ruta}/`))
}

/**
 * Translation key of the A3 branch rendered by a contract route, used as the
 * page heading. Returns undefined for the index, which is not a branch of the
 * map.
 */
export function claveDeRuta(rutaActual: string): string | undefined {
  const ruta = normalizarRuta(rutaActual)
  const modulo = MODULOS.find(candidato => candidato.ruta === ruta)
  if (modulo) {
    return modulo.claveEtiqueta
  }
  const subruta = MODULOS.flatMap(candidato => candidato.subrutas).find(
    candidato => candidato.ruta === ruta,
  )
  if (subruta) {
    return subruta.claveEtiqueta
  }
  return PROTOTIPOS.find(prototipo => prototipo.ruta === ruta)?.claveNombre
}
