/**
 * Decoder of the KSER1 binary frame.
 *
 * The transport is binary because of what happens after the bytes arrive, not
 * because of the bytes themselves: `new Float32Array(buffer, offset, n)` is a
 * view over the very same memory, and `subarray` hands one line to the chart
 * without allocating a single object, while parsing the equivalent JSON costs
 * between 65 and 130 ms on the main thread and materialises half a million
 * numbers right when the reader starts to pan.
 *
 * The frame is written by `backend/app/utils/serie_frame.py` and the two sides
 * are pinned to the same golden witness in `tests/fixtures/`, which is what
 * makes it impossible for the encoder and this decoder to drift without one of
 * the two suites turning red the same day.
 *
 * It rejects loudly instead of guessing. A proxy that answers an HTML error page
 * with a 200 -a defect this repository has already had- would otherwise be read
 * as a chart of perfectly plausible looking noise.
 */
import type {
  AgrupacionTablero,
  EtiquetaSerie,
  MarcoSerie,
  MetricaTablero,
  OrigenSerie,
} from '~/types/tablero'

/** Magic of the frame, as four ASCII bytes. */
const MAGIA = 'KSER'

/** Only version this decoder speaks. */
const VERSION_SOPORTADA = 1

/** Bytes of the fixed prefix that precedes the JSON header. */
const PREFIJO = 24

/** Why a frame was refused. */
export type MotivoMarcoInvalido = 'magia' | 'version' | 'longitud' | 'cabecera'

/** A body that is not a frame this build can read. */
export class MarcoInvalidoError extends Error {
  constructor(readonly motivo: MotivoMarcoInvalido) {
    super(`marco invalido: ${motivo}`)
    this.name = 'MarcoInvalidoError'
  }
}

/** Shape of the JSON header, exactly as the encoder writes it. */
interface CabeceraCruda {
  metrica: string
  agrupacion: string
  unidad: string
  fecha_min: string
  fecha_max: string
  offsets: { fechas: number, series: number, valores: number, total: number }
  conteo: { puntos: number, fechas: number, series: number }
  reduccion: { metodo: string, bloque: number, puntos_originales: number }
  origen: {
    silo: string
    archivo: string
    filas_agregadas: number
    filas_crudas: number | null
    generado_por: string
    semilla: number | null
    transformaciones: string[]
    nota_tipo_cambio_es: string
    nota_tipo_cambio_en: string
  }
  catalogo: { clave: string, serie_id: number | null, label_es: string, label_en: string }[]
}

/** Reads the four magic bytes without allocating a decoder. */
function leerMagia(vista: DataView): string {
  let magia = ''
  for (let indice = 0; indice < 4; indice += 1) {
    magia += String.fromCharCode(vista.getUint8(indice))
  }
  return magia
}

/** Narrows the header to the shape this decoder needs, or refuses. */
function exigirCabecera(valor: unknown): CabeceraCruda {
  const cabecera = valor as Partial<CabeceraCruda> | null
  if (
    cabecera === null
    || typeof cabecera !== 'object'
    || cabecera.offsets === undefined
    || cabecera.conteo === undefined
    || cabecera.origen === undefined
    || !Array.isArray(cabecera.catalogo)
  ) {
    throw new MarcoInvalidoError('cabecera')
  }
  return cabecera as CabeceraCruda
}

/** Header provenance block, renamed to the vocabulary of the interface. */
function aOrigen(cruda: CabeceraCruda['origen']): OrigenSerie {
  return {
    silo: cruda.silo,
    archivo: cruda.archivo,
    filasAgregadas: cruda.filas_agregadas,
    filasCrudas: cruda.filas_crudas,
    generadoPor: cruda.generado_por,
    semilla: cruda.semilla,
    transformaciones: [...cruda.transformaciones],
    notaTipoCambioEs: cruda.nota_tipo_cambio_es,
    notaTipoCambioEn: cruda.nota_tipo_cambio_en,
  }
}

/** Header catalogue, renamed the same way. */
function aCatalogo(cruda: CabeceraCruda['catalogo']): readonly EtiquetaSerie[] {
  return cruda.map(entrada => ({
    clave: entrada.clave,
    serieId: entrada.serie_id,
    labelEs: entrada.label_es,
    labelEn: entrada.label_en,
  }))
}

/**
 * Decodes a KSER1 frame into typed views over the very same buffer.
 *
 * The offsets are READ from the header and never recomputed here: all the
 * padding arithmetic lives on the encoding side, which is the first of the three
 * defences against the one expensive defect of a private format. The other two
 * are the eight byte alignment of every block -`new Float32Array` throws a
 * `RangeError` on an offset that is not a multiple of four- and the shared
 * golden witness.
 *
 * @param buffer - Body of the response, exactly as it arrived.
 * @returns The decoded frame, whose three arrays are views and not copies.
 * @throws MarcoInvalidoError when the body is not a frame this build can read.
 */
export function decodificarMarco(buffer: ArrayBuffer): MarcoSerie {
  if (buffer.byteLength < PREFIJO) {
    throw new MarcoInvalidoError('longitud')
  }

  const vista = new DataView(buffer)
  if (leerMagia(vista) !== MAGIA) {
    throw new MarcoInvalidoError('magia')
  }
  if (vista.getUint16(4, true) !== VERSION_SOPORTADA) {
    throw new MarcoInvalidoError('version')
  }

  const longitudCabecera = vista.getUint32(8, true)
  const numeroFechas = vista.getUint32(12, true)
  const numeroSeries = vista.getUint32(16, true)

  if (PREFIJO + longitudCabecera > buffer.byteLength) {
    throw new MarcoInvalidoError('longitud')
  }

  let cruda: CabeceraCruda
  try {
    const texto = new TextDecoder().decode(new Uint8Array(buffer, PREFIJO, longitudCabecera))
    cruda = exigirCabecera(JSON.parse(texto))
  }
  catch (error) {
    if (error instanceof MarcoInvalidoError) {
      throw error
    }
    throw new MarcoInvalidoError('cabecera')
  }

  const { offsets, conteo } = cruda

  // A truncated download would otherwise build the views over fewer bytes than
  // the header declares, and the RangeError would surface somewhere that
  // explains nothing.
  if (offsets.total > buffer.byteLength) {
    throw new MarcoInvalidoError('longitud')
  }

  // Counts that do not agree are how a filter leaving 249 series and a vector
  // sized for 250 ends up drawing one line's data under another line's name,
  // with an entirely credible looking result.
  if (
    conteo.fechas !== numeroFechas
    || conteo.series !== numeroSeries
    || conteo.puntos !== numeroFechas * numeroSeries
  ) {
    throw new MarcoInvalidoError('cabecera')
  }

  return {
    metrica: cruda.metrica as MetricaTablero,
    agrupacion: cruda.agrupacion as AgrupacionTablero,
    unidad: cruda.unidad,
    fechaMin: cruda.fecha_min,
    fechaMax: cruda.fecha_max,
    fechas: new Int32Array(buffer, offsets.fechas, numeroFechas),
    seriesId: new Uint16Array(buffer, offsets.series, numeroSeries),
    valores: new Float32Array(buffer, offsets.valores, conteo.puntos),
    catalogo: aCatalogo(cruda.catalogo),
    conteo: { ...conteo },
    reduccion: {
      metodo: cruda.reduccion.metodo,
      bloque: cruda.reduccion.bloque,
      puntosOriginales: cruda.reduccion.puntos_originales,
    },
    origen: aOrigen(cruda.origen),
  }
}
