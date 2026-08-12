import type { RolUsuario } from '~/types/sesion'

/**
 * Workspace contract of Karisma Data.
 *
 * The portal serves eight profiles with four roles, and the empirical result
 * behind this file is that a single default layout cannot serve them: twenty
 * designers judging six hundred generated interfaces agreed at kappa 0.25
 * (arXiv:2604.09876). So `/inicio` ships three sensible defaults chosen by
 * role, and the fine grained control -reordering and hiding blocks- stays
 * declared as later work instead of being simulated.
 *
 * Nothing here is a layout: this module says WHICH blocks a composition holds
 * and IN WHICH ORDER, and the three templates say what each one looks like.
 * The separation is what lets the order be asserted against the contract rather
 * than against itself.
 */

/** The four workspaces. One per role, no more and no fewer. */
export type ClaveEspacio = RolUsuario

/** The three compositions of /inicio. The admin workspace is a different route. */
export type ClaveComposicion = 'operativo' | 'analista' | 'directivo'

/** Ordered blocks a composition can render. */
export type ClaveBloque
  = | 'buscador'
    | 'recientes'
    | 'favoritos'
    | 'alertas'
    | 'perfil'
    | 'explorador'
    | 'exportaciones'
    | 'indicadores'

/** How much room the unified search takes in a composition. */
export type EnfasisBuscador = 'dominante' | 'normal' | 'reducido'

/**
 * Weight of a badge, never carried by colour alone.
 *
 * The four values map to the semantic tokens of the design system, and every
 * badge that uses one also prints its own word: a reader who cannot tell the
 * amber from the red still reads "Alta" or "Caducada".
 */
export type TonoInsignia = 'neutro' | 'exito' | 'atencion' | 'peligro'

/** Rendering state of a block, published as `data-estado`. */
export type EstadoBloque = 'lista' | 'vacio' | 'cargando'

export interface EspacioTrabajo {
  readonly clave: ClaveEspacio
  /** Route the user lands on after signing in. */
  readonly pantallaPrincipal: string
  /** Composition rendered when the user opens /inicio. */
  readonly composicion: ClaveComposicion
  /** Blocks in render order, which is also keyboard focus order. */
  readonly bloques: readonly ClaveBloque[]
  readonly enfasisBuscador: EnfasisBuscador
}

export interface InsigniaLista {
  /** Translation key of the badge word. Never a literal. */
  readonly claveTexto: string
  readonly tono: TonoInsignia
}

export interface ElementoLista {
  readonly id: string
  /** Translation key of the visible label. Never a literal sentence. */
  readonly claveEtiqueta: string
  /** Contract route, with query string when it carries a search term. */
  readonly destino: string
  /**
   * Physical name or source code the item points at.
   *
   * It is data and not a translation key on purpose: `ratio_lcr` has no English
   * spelling, and a catalogue key whose two languages are identical is exactly
   * what `test/idioma.spec.ts` refuses.
   */
  readonly termino?: string
  /** ISO instant anchored to INSTANTE_DE_REFERENCIA. Never Date.now(). */
  readonly fecha?: string
  readonly insignia?: InsigniaLista
}

/** Unit a present-day figure is expressed in. */
export type UnidadIndicador = 'porcentaje' | 'millones-mxn' | 'dias'

/**
 * A figure of the PRESENT: what a measure is worth today.
 *
 * Deliberately not a forecast. The predictive cards with their method label
 * live in the dashboard and belong to another User Story; mixing the two here
 * would let a projection be read as an observation.
 */
export interface Indicador {
  readonly id: string
  readonly claveEtiqueta: string
  readonly valor: number
  readonly unidad: UnidadIndicador
  /** Change against the previous month. Negative means down. */
  readonly variacion: number
  /** ISO instant of the cut-off, anchored to INSTANTE_DE_REFERENCIA. */
  readonly fecha: string
  readonly destino: string
}
