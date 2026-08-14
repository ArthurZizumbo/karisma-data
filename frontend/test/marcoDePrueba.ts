import type {
  AgrupacionTablero,
  EtiquetaSerie,
  MarcoSerie,
  MetricaTablero,
  OrigenSerie,
} from '~/types/tablero'

/**
 * Synthetic frames for the specs that do not need the golden witness.
 *
 * The witness is three dates by two lines, which is the right size for pinning
 * the byte layout and the wrong size for exercising the six colour cap or the
 * full load. This builder produces frames of any shape with values that are
 * distinguishable per line, so an off by one in a slice shows up as a wrong
 * number rather than as a passing test.
 */

/** Provenance block every synthetic frame carries. */
export const ORIGEN_DE_PRUEBA: OrigenSerie = {
  silo: 'liquidez',
  archivo: 'data/aggregates/serie_tablero.parquet',
  filasAgregadas: 500000,
  filasCrudas: 1000000,
  generadoPor: 'make data',
  semilla: 20260720,
  transformaciones: ['group_by(fec_pos, unidad_negocio)', 'media por bloque de 5 dias habiles'],
  notaTipoCambioEs: 'Tipo de cambio sintetico fijo. No es una cotizacion de mercado.',
  notaTipoCambioEn: 'Fixed synthetic exchange rate. Not a market quote.',
}

export interface FormaDelMarco {
  series: number
  fechas: number
  metrica?: MetricaTablero
  agrupacion?: AgrupacionTablero
  /** True when each line carries its own key, as `agrupacion=serie` does. */
  conClaves?: boolean
  /** Positions, as `[linea, punto]`, written as a hole. */
  huecos?: readonly (readonly [number, number])[]
}

/**
 * Builds a frame of the requested shape.
 *
 * Line i starts at `i * 1000` and grows by ten per point, so the value at any
 * position identifies both the line and the point it belongs to.
 *
 * @param forma - Shape of the frame.
 * @returns A frame equivalent to a decoded one.
 */
export function crearMarco(forma: FormaDelMarco): MarcoSerie {
  const { series, fechas } = forma
  const conClaves = forma.conClaves ?? false
  const valores = new Float32Array(series * fechas)

  for (let linea = 0; linea < series; linea += 1) {
    for (let punto = 0; punto < fechas; punto += 1) {
      valores[linea * fechas + punto] = linea * 1000 + punto * 10
    }
  }
  for (const [linea, punto] of forma.huecos ?? []) {
    valores[linea * fechas + punto] = Number.NaN
  }

  const catalogo: EtiquetaSerie[] = []
  for (let linea = 0; linea < series; linea += 1) {
    catalogo.push({
      clave: conClaves ? String(linea) : `UNIDAD_${linea}`,
      serieId: conClaves ? linea : null,
      labelEs: `Linea ${linea}`,
      labelEn: `Line ${linea}`,
    })
  }

  const dias = new Int32Array(fechas)
  for (let punto = 0; punto < fechas; punto += 1) {
    // 17835 is 31-oct-2018, the first business day of the contract window.
    dias[punto] = 17835 + punto
  }

  const claves = new Uint16Array(series)
  for (let linea = 0; linea < series; linea += 1) {
    claves[linea] = conClaves ? linea : 65535
  }

  return {
    metrica: forma.metrica ?? 'saldo_disponible_mxn',
    agrupacion: forma.agrupacion ?? (conClaves ? 'serie' : 'unidad_negocio'),
    unidad: 'MXN',
    fechaMin: '2018-10-31',
    fechaMax: '2018-11-30',
    fechas: dias,
    seriesId: claves,
    valores,
    catalogo,
    conteo: { puntos: series * fechas, fechas, series },
    reduccion: { metodo: 'media_por_bloque', bloque: 5, puntosOriginales: fechas * 5 },
    origen: ORIGEN_DE_PRUEBA,
  }
}
