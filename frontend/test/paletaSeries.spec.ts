import { describe, expect, it } from 'vitest'

import {
  colorDeSerie,
  estiloDeSerie,
  MAXIMO_SERIES_COLOREADAS,
  PALETA_SERIES,
  patronCss,
  patronDeTrazo,
} from '~/utils/paletaSeries'
import { SERIES } from '~/utils/tokens.generated'

/**
 * US-025 — the categorical palette and the three channels of a line.
 *
 * Two independent commitments meet in this file. One is the derivation chain
 * `design/sistema.py -> tokens.generated.ts -> interface -> screenshots -> PDF`:
 * a hex typed by hand anywhere along it makes the application and the document
 * disagree while every other check stays green. The other is that information
 * never depends on colour alone, which about one reader in twelve needs and
 * which every figure printed in one ink needs too.
 */

describe('los colores salen del sistema de diseno y de ningun otro sitio', () => {
  it('reproduce exactamente los seis tokens categoricos, en los dos modos', () => {
    expect(PALETA_SERIES).toHaveLength(SERIES.length)
    expect(PALETA_SERIES.map(estilo => estilo.nombreToken)).toEqual(
      SERIES.map(token => token.nombre),
    )
    expect(PALETA_SERIES.map(estilo => estilo.claro)).toEqual(SERIES.map(token => token.claro))
    expect(PALETA_SERIES.map(estilo => estilo.oscuro)).toEqual(SERIES.map(token => token.oscuro))
  })

  it('resuelve el color del modo que el lector tiene en pantalla', () => {
    // Painting the light mode blues over the near black ground is a contrast
    // defect the design system already measured and that no test of the
    // palette alone would catch.
    const primero = PALETA_SERIES[0]!

    expect(colorDeSerie(primero, 'claro')).toBe(SERIES[0]!.claro)
    expect(colorDeSerie(primero, 'oscuro')).toBe(SERIES[0]!.oscuro)
  })
})

describe('la informacion no depende del color', () => {
  it('da a cada serie un marcador distinto', () => {
    // Two lines separated by hue alone fail the criterion, and nobody with
    // trichromatic vision would ever notice.
    const simbolos = PALETA_SERIES.map(estilo => estilo.simbolo)

    expect(new Set(simbolos).size).toBe(PALETA_SERIES.length)
  })

  it('da a cada serie un patron de trazo distinto', () => {
    // The same defect, in a document printed in one ink.
    const trazos = PALETA_SERIES.map(estilo => JSON.stringify(estilo.trazo))

    expect(new Set(trazos).size).toBe(PALETA_SERIES.length)
  })

  it('da a cada serie un icono propio de la unica familia del portal', () => {
    const iconos = PALETA_SERIES.map(estilo => estilo.icono)

    expect(new Set(iconos).size).toBe(PALETA_SERIES.length)
    expect(iconos.every(icono => icono.startsWith('lucide:'))).toBe(true)
  })
})

describe('mas alla del sexto color', () => {
  it('devuelve null en lugar de reutilizar el primero en silencio', () => {
    // Colouring a seventh line by wrapping around produces two identical
    // entries in the legend and no error anywhere.
    expect(estiloDeSerie(0)).not.toBeNull()
    expect(estiloDeSerie(MAXIMO_SERIES_COLOREADAS - 1)).not.toBeNull()
    expect(estiloDeSerie(MAXIMO_SERIES_COLOREADAS)).toBeNull()
    expect(estiloDeSerie(-1)).toBeNull()
    expect(estiloDeSerie(1.5)).toBeNull()
  })
})

describe('la muestra de trazo de la leyenda', () => {
  it('reproduce el mismo patron que la grafica dibuja', () => {
    // A legend swatch drawn as a plain rule while the line is dotted breaks the
    // redundancy: in one ink the reader is back to matching by colour.
    const solido = patronCss('solid', '#123456')
    const punteado = patronCss('dotted', '#123456')

    expect(solido).toContain('#123456')
    expect(solido).not.toContain('transparent')
    expect(punteado).toContain('transparent')
    expect(punteado).not.toBe(solido)
  })

  it('conserva la longitud de tinta y de hueco de un patron numerico', () => {
    expect(patronDeTrazo([10, 4, 2, 4])).toEqual([10, 4, 2, 4])
    expect(patronCss([10, 4], '#000001')).toBe(
      'repeating-linear-gradient(to right, #000001 0px 10px, transparent 10px 14px)',
    )
  })
})
