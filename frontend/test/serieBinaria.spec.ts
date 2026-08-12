import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'

import { describe, expect, it } from 'vitest'

import { decodificarMarco, MarcoInvalidoError } from '~/utils/serieBinaria'

/**
 * US-025 — the decoder against the witness the encoder produced.
 *
 * This file and `tests/backend/test_serie_frame.py` read the SAME bytes. That is
 * the whole point: a private binary format has exactly one expensive failure
 * mode, which is the two ends drifting apart, and Python encoding and decoding
 * against itself would never notice. With a shared witness, a change of field
 * order, of type or of endianness turns one of the two suites red the same day.
 */

/**
 * Resolves a path of the repository.
 *
 * The path arrives as a variable on purpose: with a literal, Vite rewrites the
 * `new URL(..., import.meta.url)` pattern into an asset reference and the URL
 * stops being a file one.
 */
function rutaDelRepositorio(relativa: string): string {
  return fileURLToPath(new URL(relativa, import.meta.url))
}

/** The witness as an ArrayBuffer, decoded from its base64 line. */
function testigo(): ArrayBuffer {
  const texto = readFileSync(rutaDelRepositorio('../../tests/fixtures/serie_frame_golden.b64'), 'utf8')
  const bytes = Buffer.from(texto.trim(), 'base64')
  // A slice and not `bytes.buffer`: Node allocates small buffers inside a shared
  // pool, so the raw buffer would carry unrelated bytes before and after.
  return bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength)
}

interface Descripcion {
  bytes: number
  cabecera: {
    conteo: { puntos: number, fechas: number, series: number }
    offsets: { fechas: number, series: number, valores: number, total: number }
    metrica: string
    agrupacion: string
    catalogo: { clave: string, serie_id: number | null, label_es: string, label_en: string }[]
    origen: { archivo: string, filas_crudas: number | null, semilla: number | null }
  }
  fechas: number[]
  series_id: number[]
  valores: (number | null)[]
}

/** The human readable side of the witness, written by the same generator. */
function descripcion(): Descripcion {
  return JSON.parse(
    readFileSync(rutaDelRepositorio('../../tests/fixtures/serie_frame_golden.json'), 'utf8'),
  ) as Descripcion
}

describe('el decodificador lee el testigo dorado que produce el backend', () => {
  it('reconstruye las tres rejillas y la cabecera', () => {
    const esperado = descripcion()
    const marco = decodificarMarco(testigo())

    expect(marco.conteo).toEqual(esperado.cabecera.conteo)
    expect([...marco.fechas]).toEqual(esperado.fechas)
    expect([...marco.seriesId]).toEqual(esperado.series_id)
    expect(marco.metrica).toBe(esperado.cabecera.metrica)
    expect(marco.agrupacion).toBe(esperado.cabecera.agrupacion)
  })

  it('coloca cada valor donde el codificador lo puso, con el hueco como NaN', () => {
    // An off by one in the padding arithmetic would shift every value by one
    // position and the chart would still look entirely plausible.
    const esperado = descripcion()
    const marco = decodificarMarco(testigo())

    const leidos = [...marco.valores].map(valor => (Number.isNaN(valor) ? null : valor))

    expect(leidos).toEqual(esperado.valores)
  })

  it('traduce el catalogo y la procedencia al vocabulario de la interfaz', () => {
    // The lineage overlay of US-029 paints this block: a field lost in the
    // rename would leave it with nothing to show and no error anywhere.
    const esperado = descripcion()
    const marco = decodificarMarco(testigo())

    expect(marco.catalogo).toHaveLength(esperado.cabecera.catalogo.length)
    expect(marco.catalogo[0]).toEqual({
      clave: esperado.cabecera.catalogo[0]!.clave,
      serieId: esperado.cabecera.catalogo[0]!.serie_id,
      labelEs: esperado.cabecera.catalogo[0]!.label_es,
      labelEn: esperado.cabecera.catalogo[0]!.label_en,
    })
    expect(marco.origen.archivo).toBe(esperado.cabecera.origen.archivo)
    expect(marco.origen.filasCrudas).toBe(esperado.cabecera.origen.filas_crudas)
    expect(marco.origen.semilla).toBe(esperado.cabecera.origen.semilla)
  })

  it('entrega vistas sobre el mismo buffer, sin copiar', () => {
    // Somebody "simplifying" the decoder with Array.from would delete the only
    // reason the binary transport exists, and nothing else would fail.
    const buffer = testigo()
    const marco = decodificarMarco(buffer)

    expect(marco.valores.buffer).toBe(buffer)
    expect(marco.fechas.buffer).toBe(buffer)
    expect(marco.seriesId.buffer).toBe(buffer)
    expect(marco.valores.byteOffset).toBe(descripcion().cabecera.offsets.valores)
  })
})

describe('el decodificador rechaza en voz alta lo que no es un marco', () => {
  it('rechaza un cuerpo cuya magia no es KSER', () => {
    // The proxy answering an HTML error page with a 200 is a defect this
    // repository has already had. Read as numbers it would paint plausible
    // looking noise, which nobody would report as a bug.
    const pagina = new TextEncoder().encode('<!doctype html><html><body>502</body></html>')

    expect(() => decodificarMarco(pagina.buffer as ArrayBuffer)).toThrow(MarcoInvalidoError)
    expect(() => decodificarMarco(pagina.buffer as ArrayBuffer)).toThrow(/magia/)
  })

  it('rechaza un cuerpo mas corto que el prefijo', () => {
    expect(() => decodificarMarco(new ArrayBuffer(8))).toThrow(/longitud/)
  })

  it('rechaza un marco truncado antes de crear las vistas', () => {
    // A cut download would otherwise build a Float32Array over fewer bytes than
    // the header declares, and the RangeError would surface somewhere that
    // explains nothing about what actually happened.
    const completo = testigo()
    const truncado = completo.slice(0, completo.byteLength - 16)

    expect(() => decodificarMarco(truncado)).toThrow(/longitud/)
  })

  it('rechaza una version que no sabe leer', () => {
    const buffer = testigo()
    new DataView(buffer).setUint16(4, 2, true)

    expect(() => decodificarMarco(buffer)).toThrow(/version/)
  })

  it('rechaza una cabecera cuyos conteos no cuadran', () => {
    // A filter leaving 249 series and a vector sized for 250 would otherwise
    // draw one line's data under another line's name.
    const buffer = testigo()
    new DataView(buffer).setUint32(16, 3, true)

    expect(() => decodificarMarco(buffer)).toThrow(/cabecera/)
  })
})
