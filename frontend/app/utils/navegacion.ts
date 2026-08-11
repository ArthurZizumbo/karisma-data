import type { ModuloNav, Prototipo } from '~/types/navegacion'

/**
 * Single source of truth for the navigation contract of Karisma Data.
 *
 * The sidebar, the prototype index, the page headings and the end to end smoke
 * script all derive from this module. No route literal is written inside a Vue
 * file: adding a route here is the only way to add a route to the portal, and
 * every entry must point at a branch of the A3 site map.
 */

/** Index of the seven prototypes. Not a branch of the A3 map either. */
export const RUTA_INDICE = '/'

/** Entry screen. It frames the portal but it is not a branch of the A3 map. */
export const RUTA_ACCESO = '/acceso'

/** Conversational assistant. Cross cutting to the four categories of the A3 map. */
export const RUTA_ASISTENTE = '/asistente'

/** Notice shown on every route so that no screenshot can be read as a live system. */
export const AVISO_ALCANCE
  = 'Prototipo de alta fidelidad de Karisma Data con datos sintéticos. '
    + 'No está conectado a sistemas reales de ninguna institución.'

/**
 * The nine cards that three or more evaluators asked to duplicate during the A3
 * card sorting. Each one lives in a canonical branch and is also reachable from
 * the other contexts where it was looked for.
 */
export const FACETAS_TRANSVERSALES: readonly string[] = Object.freeze([
  'Consumo por API',
  'Calidad de datos',
  'Vista previa',
  'Catálogo de fuentes',
  'Mis alertas',
  'Credenciales API',
  'Monitoreo de cargas',
  'Permisos',
  'Historial de exportaciones',
])

/** The four first level categories of the A3 map, in their canonical order. */
export const MODULOS: readonly ModuloNav[] = Object.freeze([
  {
    id: '1',
    etiqueta: 'Inicio',
    ruta: '/inicio',
    subrutas: [
      { id: '1.1', etiqueta: 'Buscador unificado', ruta: '/inicio' },
      { id: '1.2', etiqueta: 'Búsquedas recientes', ruta: '/inicio' },
      { id: '1.3', etiqueta: 'Favoritos', ruta: '/inicio' },
      { id: '1.4', etiqueta: 'Mis alertas', ruta: '/inicio', facetaTransversal: true },
      { id: '1.5', etiqueta: 'Mi perfil', ruta: '/inicio' },
    ],
  },
  {
    id: '2',
    etiqueta: 'Exploración y extracción',
    ruta: '/exploracion',
    subrutas: [
      { id: '2.1', etiqueta: 'Catálogo temático', ruta: '/exploracion' },
      { id: '2.2', etiqueta: 'Consulta y filtros', ruta: '/exploracion', facetaTransversal: true },
      { id: '2.3', etiqueta: 'Exportaciones', ruta: '/exploracion/exportar', facetaTransversal: true },
      { id: '2.4', etiqueta: 'Tableros e indicadores', ruta: '/exploracion/tableros' },
    ],
  },
  {
    id: '3',
    etiqueta: 'Gobierno del dato',
    ruta: '/gobierno',
    subrutas: [
      { id: '3.1', etiqueta: 'Diccionario y metadatos', ruta: '/gobierno' },
      { id: '3.2', etiqueta: 'Linaje y calidad', ruta: '/gobierno', facetaTransversal: true },
      { id: '3.3', etiqueta: 'Catálogo de fuentes', ruta: '/gobierno', facetaTransversal: true },
    ],
  },
  {
    id: '4',
    etiqueta: 'Administración',
    ruta: '/administracion',
    subrutas: [
      { id: '4.1', etiqueta: 'Usuarios, roles y permisos', ruta: '/administracion', facetaTransversal: true },
      { id: '4.2', etiqueta: 'Solicitudes y aprobaciones', ruta: '/administracion' },
      { id: '4.3', etiqueta: 'Bitácora de accesos', ruta: '/administracion' },
      { id: '4.4', etiqueta: 'Integraciones', ruta: '/administracion', facetaTransversal: true },
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
    nombre: 'Acceso',
    ruta: RUTA_ACCESO,
    ramaA3: 'Pantalla de entrada; enmarca las demás sin ser rama del mapa',
    alcance: 'navegable-sin-datos',
    rolSugerido: 'operativo',
  },
  {
    numero: 1,
    nombre: 'Inicio',
    ruta: '/inicio',
    ramaA3: '1. Inicio',
    alcance: 'navegable-sin-datos',
    rolSugerido: 'operativo',
  },
  {
    numero: 2,
    nombre: 'Exploración y extracción',
    ruta: '/exploracion',
    ramaA3: '2. Exploración y extracción — 2.1 Catálogo temático, 2.2 Consulta y filtros',
    alcance: 'navegable-sin-datos',
    rolSugerido: 'analista',
  },
  {
    numero: 3,
    nombre: 'Gobierno del dato',
    ruta: '/gobierno',
    ramaA3: '3. Gobierno del dato — 3.1 Diccionario y metadatos, 3.2 Linaje y calidad, 3.3 Catálogo de fuentes',
    alcance: 'navegable-sin-datos',
    rolSugerido: 'analista',
  },
  {
    numero: 4,
    nombre: 'Asistente conversacional',
    ruta: RUTA_ASISTENTE,
    ramaA3: 'Transversal a las cuatro categorías',
    alcance: 'navegable-sin-datos',
    rolSugerido: 'directivo',
  },
  {
    numero: 5,
    nombre: 'Administración',
    ruta: '/administracion',
    ramaA3: '4. Administración — 4.1 a 4.4',
    alcance: 'navegable-sin-datos',
    rolSugerido: 'administrador',
  },
  {
    numero: 6,
    nombre: 'Exportación',
    ruta: '/exploracion/exportar',
    ramaA3: '2.3 Exportaciones',
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
 * Label of the A3 branch rendered by a contract route, used as the page heading.
 * Returns undefined for the index, which is not a branch of the map.
 */
export function etiquetaDeRuta(rutaActual: string): string | undefined {
  const ruta = normalizarRuta(rutaActual)
  const modulo = MODULOS.find(candidato => candidato.ruta === ruta)
  if (modulo) {
    return modulo.etiqueta
  }
  const subruta = MODULOS.flatMap(candidato => candidato.subrutas).find(
    candidato => candidato.ruta === ruta,
  )
  if (subruta) {
    return subruta.etiqueta
  }
  return PROTOTIPOS.find(prototipo => prototipo.ruta === ruta)?.nombre
}
