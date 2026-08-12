import type {
  ClaveBloque,
  ClaveComposicion,
  EspacioTrabajo,
} from '~/types/espacios'
import type { RolUsuario } from '~/types/sesion'
import {
  ALERTAS,
  BUSQUEDAS_RECIENTES,
  CONSULTAS_GUARDADAS,
  EXPORTACIONES,
  FAVORITOS,
  INDICADORES,
} from '~/utils/muestrasInicio'

/**
 * Which blocks each workspace shows, and in which order.
 *
 * The order is not styling: it is the acceptance criterion of the User Story
 * and it is also the keyboard focus order, so it lives here as data and the
 * three templates read it. A layout language driven by data was evaluated and
 * rejected -the three compositions are not one grid reordered- but the SET and
 * the SEQUENCE of blocks are data all the same, which is what lets the test
 * compare the DOM against the contract instead of against itself.
 *
 * Import direction, so that nobody creates a cycle: this module reads the
 * samples, and `utils/sesion.ts` reads this module. Never the other way round.
 */

/** Landing route of the three consultation roles. */
export const RUTA_INICIO = '/inicio'

/** Landing route of the platform administrator. */
export const RUTA_ADMINISTRACION = '/administracion'

/** Where the unified search sends a term. */
export const RUTA_EXPLORACION = '/exploracion'

/** Query parameter the exploration screen reads the search term from. */
export const PARAMETRO_BUSQUEDA = 'q'

/** Composition used when there is no session yet, and by the admin on /inicio. */
export const COMPOSICION_POR_DEFECTO: ClaveComposicion = 'operativo'

/**
 * The four workspaces, in the canonical order of the identity contract.
 *
 * The administrator is the only one whose landing screen is not `/inicio`, and
 * the only one whose composition is borrowed: an administrator who opens the
 * home screen by hand gets the operative one, which is the most general. The
 * home screen is not forbidden to them -forbidding routes is the guard's job
 * and `/inicio` is not on its list- it simply is not where they work.
 */
export const ESPACIOS: readonly EspacioTrabajo[] = Object.freeze([
  Object.freeze({
    clave: 'operativo',
    pantallaPrincipal: RUTA_INICIO,
    composicion: 'operativo',
    bloques: Object.freeze(['buscador', 'recientes', 'favoritos', 'alertas', 'perfil'] as const),
    enfasisBuscador: 'dominante',
  }),
  Object.freeze({
    clave: 'analista',
    pantallaPrincipal: RUTA_INICIO,
    composicion: 'analista',
    bloques: Object.freeze([
      'explorador',
      'exportaciones',
      'buscador',
      'favoritos',
      'alertas',
    ] as const),
    enfasisBuscador: 'normal',
  }),
  Object.freeze({
    clave: 'directivo',
    pantallaPrincipal: RUTA_INICIO,
    composicion: 'directivo',
    bloques: Object.freeze(['indicadores', 'buscador', 'alertas', 'favoritos'] as const),
    enfasisBuscador: 'reducido',
  }),
  Object.freeze({
    clave: 'admin',
    pantallaPrincipal: RUTA_ADMINISTRACION,
    composicion: COMPOSICION_POR_DEFECTO,
    bloques: Object.freeze(['buscador', 'recientes', 'favoritos', 'alertas', 'perfil'] as const),
    enfasisBuscador: 'dominante',
  }),
])

/**
 * Every route a block links to, before deduplication.
 *
 * The search block declares the exploration screen because that is where its
 * form navigates, and the profile block declares nothing: it shows who is
 * signed in and offers no door.
 */
const DESTINOS_POR_BLOQUE: Readonly<Record<ClaveBloque, readonly string[]>> = Object.freeze({
  buscador: Object.freeze([RUTA_EXPLORACION]),
  recientes: Object.freeze(BUSQUEDAS_RECIENTES.map(elemento => elemento.destino)),
  favoritos: Object.freeze(FAVORITOS.map(elemento => elemento.destino)),
  alertas: Object.freeze(ALERTAS.map(elemento => elemento.destino)),
  perfil: Object.freeze([]),
  explorador: Object.freeze([
    RUTA_EXPLORACION,
    ...CONSULTAS_GUARDADAS.map(elemento => elemento.destino),
  ]),
  exportaciones: Object.freeze(EXPORTACIONES.map(elemento => elemento.destino)),
  indicadores: Object.freeze(INDICADORES.map(indicador => indicador.destino)),
})

/** Drops the query string and the hash of a path. */
function soloRuta(destino: string): string {
  return destino.split('?')[0]?.split('#')[0] ?? ''
}

/**
 * Workspace of a role.
 *
 * Falls back to the operative workspace when there is no session, which is what
 * keeps `/inicio` renderable during the first server pass, before the guard has
 * resolved who is asking. Rendering nothing there would look like a screen that
 * failed to load.
 *
 * @param rol - Role of the current session, or null when there is none.
 * @returns The workspace of that role, never undefined.
 */
export function espacioDeRol(rol: RolUsuario | null | undefined): EspacioTrabajo {
  return (
    ESPACIOS.find(espacio => espacio.clave === rol)
    ?? ESPACIOS.find(espacio => espacio.clave === COMPOSICION_POR_DEFECTO)!
  )
}

/**
 * Blocks of a composition, in render order.
 *
 * @param composicion - One of the three compositions of the home screen.
 * @returns The ordered blocks the composition renders.
 */
export function bloquesDe(composicion: ClaveComposicion): readonly ClaveBloque[] {
  return ESPACIOS.find(espacio => espacio.clave === composicion)!.bloques
}

/**
 * Every route a composition links to, deduplicated and without query strings.
 *
 * The test that reads this is not decoration: a composition that offers a route
 * the reader's role cannot open turns the home screen into a door slammed in
 * their face, and a route typed from memory turns it into a 404 during the
 * demonstration.
 *
 * @param composicion - One of the three compositions of the home screen.
 * @returns The distinct bare paths reachable from it.
 */
export function destinosDe(composicion: ClaveComposicion): readonly string[] {
  const destinos = bloquesDe(composicion).flatMap(bloque =>
    DESTINOS_POR_BLOQUE[bloque].map(soloRuta),
  )
  return [...new Set(destinos)]
}
