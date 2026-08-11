/**
 * Navigation contract types.
 *
 * They mirror the A3 site map: every route in the portal must map to a branch of
 * that map, and every branch must be reachable through a route.
 *
 * Since the bilingual decision of 10-ago-2026 the contract carries translation
 * keys instead of Spanish labels. The structure is language independent; the
 * words live in i18n/locales/{es,en}.json and nowhere else.
 */

/** How much of a screen is actually usable right now. */
export type EstadoAlcance
  = | 'navegable-con-datos'
    | 'navegable-sin-datos'
    | 'roadmap'

/** Profile the screen is primarily designed for. Mirrors the JWT scopes. */
export type RolSugerido = 'operativo' | 'analista' | 'directivo' | 'administrador'

/** Second level entry of the sidebar: a sub branch of the A3 map. */
export interface SubrutaNav {
  /** A3 identifier, for example '2.4'. */
  id: string
  /** Translation key of the label shown to the reader. */
  claveEtiqueta: string
  /** Route that renders this sub branch. */
  ruta: string
  /** True when the branch owns one of the nine cross cutting facets of A3. */
  facetaTransversal?: boolean
}

/** First level entry of the sidebar: a top category of the A3 map. */
export interface ModuloNav {
  /** A3 identifier, for example '2'. */
  id: string
  /** Translation key of the label shown to the reader. */
  claveEtiqueta: string
  /** Route that renders the module landing screen. */
  ruta: string
  /** Second level entries revealed only while this module is active. */
  subrutas: SubrutaNav[]
}

/** Entry of the prototype index rendered at '/'. */
export interface Prototipo {
  /** Position in the index, 0 to 6. */
  numero: number
  /** Translation key of the name shown to the reader. */
  claveNombre: string
  /** Route the button navigates to. */
  ruta: string
  /** Translation key of the A3 branch this prototype implements. */
  claveRama: string
  /** Honest scope label; never promises data that does not exist yet. */
  alcance: EstadoAlcance
  /** Profile the prototype is primarily designed for. */
  rolSugerido: RolSugerido
}
