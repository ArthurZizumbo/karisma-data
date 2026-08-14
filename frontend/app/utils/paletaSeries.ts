/**
 * Categorical palette of the dashboard: colour, marker shape and stroke.
 *
 * Information never depends on colour alone, which is a committed acceptance
 * criterion and not a preference: about one reader in twelve cannot separate
 * the green and the amber of this same palette, and every figure of the A4
 * document is also printed in one ink. Each of the six lines therefore carries
 * three redundant channels, and each channel is distinct on its own.
 *
 * The six colours are READ from `tokens.generated.ts`, never typed here. That
 * file is emitted by `make tokens` from `design/sistema.py`, so a hex written by
 * hand is how the application and the PDF start disagreeing without anything
 * failing.
 */
import type { TokenColor } from '~/utils/tokens.generated'
import { SERIES } from '~/utils/tokens.generated'

/** Colour mode of the interface, as the design system store reports it. */
export type ModoColor = 'claro' | 'oscuro'

/** Marker shapes ECharts ships natively. No custom path, no image. */
export type SimboloSerie = 'circle' | 'rect' | 'triangle' | 'diamond' | 'pin' | 'arrow'

/** Stroke pattern, in the form `lineStyle.type` accepts. */
export type TrazoSerie = 'solid' | 'dashed' | 'dotted' | readonly number[]

/** One categorical style: the three redundant channels of one line. */
export interface EstiloSerie {
  /** Name of the design token, so the legend can be traced back to the guide. */
  nombreToken: string
  /** Colour in light mode, exactly as the token declares it. */
  claro: string
  /** Colour in dark mode, exactly as the token declares it. */
  oscuro: string
  /** Marker shape, for the chart and for the legend. */
  simbolo: SimboloSerie
  /** Icon of the marker shape, from the single icon family of the portal. */
  icono: string
  /** Stroke pattern, distinguishable in greyscale. */
  trazo: TrazoSerie
}

/**
 * Marker and stroke of each of the six categorical tokens.
 *
 * The order matches `SERIES`, and the shapes are the ones ECharts draws without
 * a custom path: the design system prose names a cross and a star for the fifth
 * and the sixth, and ECharts 6 has neither, so asking for them would silently
 * fall back to a circle and two lines would become indistinguishable in print.
 * Pin and arrow keep the six shapes apart, which is the property the criterion
 * actually measures.
 */
const FORMAS: readonly { simbolo: SimboloSerie, icono: string, trazo: TrazoSerie }[] = [
  { simbolo: 'circle', icono: 'lucide:circle', trazo: 'solid' },
  { simbolo: 'rect', icono: 'lucide:square', trazo: 'dashed' },
  { simbolo: 'triangle', icono: 'lucide:triangle', trazo: 'dotted' },
  { simbolo: 'diamond', icono: 'lucide:diamond', trazo: [10, 4, 2, 4] },
  { simbolo: 'pin', icono: 'lucide:map-pin', trazo: [16, 6] },
  { simbolo: 'arrow', icono: 'lucide:navigation', trazo: [10, 3, 10, 8] },
]

/** Six styles: exactly the six categorical tokens of the style guide. */
export const PALETA_SERIES: readonly EstiloSerie[] = Object.freeze(
  SERIES.map((token: TokenColor, indice: number) => {
    const forma = FORMAS[indice]
    if (forma === undefined) {
      // The generator emitted more categorical tokens than the palette knows how
      // to keep apart. Failing here is the point: silently reusing a shape would
      // produce two lines a greyscale reader cannot tell apart.
      throw new Error(`falta la forma de la serie ${token.nombre}`)
    }
    return Object.freeze({
      nombreToken: token.nombre,
      claro: token.claro,
      oscuro: token.oscuro,
      simbolo: forma.simbolo,
      icono: forma.icono,
      trazo: forma.trazo,
    })
  }),
)

/** How many lines may be drawn in colour before the view has to go muted. */
export const MAXIMO_SERIES_COLOREADAS = PALETA_SERIES.length

/**
 * Style of the nth coloured line.
 *
 * @param indice - Position of the line among the coloured ones.
 * @returns The style, or null past the sixth: beyond it the caller must go
 *   muted, because a seventh colour would repeat the first one in silence and
 *   two entries of the legend would become the same entry.
 */
export function estiloDeSerie(indice: number): EstiloSerie | null {
  if (!Number.isInteger(indice) || indice < 0 || indice >= PALETA_SERIES.length) {
    return null
  }
  return PALETA_SERIES[indice] ?? null
}

/**
 * Colour of a style in the mode currently on screen.
 *
 * @param estilo - One entry of the palette.
 * @param modo - Mode the reader is seeing.
 * @returns The hex of that token in that mode.
 */
export function colorDeSerie(estilo: EstiloSerie, modo: ModoColor): string {
  return modo === 'oscuro' ? estilo.oscuro : estilo.claro
}

/** Dash pattern of the three named strokes, in pixels of ink and of gap. */
const PATRON_POR_NOMBRE: Record<'solid' | 'dashed' | 'dotted', readonly number[]> = {
  solid: [8],
  dashed: [8, 4],
  dotted: [2, 3],
}

/** The stroke as a plain list of alternating ink and gap lengths. */
export function patronDeTrazo(trazo: TrazoSerie): readonly number[] {
  return typeof trazo === 'string' ? PATRON_POR_NOMBRE[trazo] : trazo
}

/**
 * The stroke as a CSS background, so the legend can show the very same pattern
 * the chart draws.
 *
 * A legend swatch that is a plain rule while the line is dotted breaks the
 * redundancy the palette exists for: in one ink, the reader would be back to
 * matching by colour.
 *
 * @param trazo - Stroke pattern of one style.
 * @param color - Colour already resolved for the mode on screen.
 * @returns A `repeating-linear-gradient` reproducing the pattern.
 */
export function patronCss(trazo: TrazoSerie, color: string): string {
  const patron = patronDeTrazo(trazo)
  const paradas: string[] = []
  let posicion = 0
  patron.forEach((longitud, indice) => {
    const tinta = indice % 2 === 0 ? color : 'transparent'
    paradas.push(`${tinta} ${posicion}px ${posicion + longitud}px`)
    posicion += longitud
  })
  return `repeating-linear-gradient(to right, ${paradas.join(', ')})`
}
