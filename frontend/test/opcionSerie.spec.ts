import type { OpcionesGrafica } from '~/utils/opcionSerie'

import { describe, expect, it } from 'vitest'

import {
  ALTO_GRAFICA,
  construirOpcionSerie,
  identificadorDeLinea,
  indicesColoreados,
} from '~/utils/opcionSerie'
import { MAXIMO_SERIES_COLOREADAS, PALETA_SERIES } from '~/utils/paletaSeries'
import { crearMarco } from './marcoDePrueba'

/**
 * US-025 — the option, which is where every decision about the chart lives.
 *
 * What is NOT tested here is that ECharts paints: mounting a canvas in
 * happy-dom draws nothing, so the assertion could not fail. What is tested is
 * the option handed to it, which is the part a refactor can quietly break.
 */

const BASE: OpcionesGrafica = {
  densidad: 'resumen',
  idioma: 'es',
  modo: 'claro',
  ventana: { inicio: 0, fin: 100 },
  seriesVisibles: [],
}

describe('las dos defensas de pintado viajan en toda serie', () => {
  it('emite sampling lttb y large en cada linea, sea cual sea la densidad', () => {
    // Losing either of the two while adding a new density is CA-3, and the
    // symptom is a pan of the full view that stops being usable.
    for (const densidad of ['resumen', 'detalle', 'completa'] as const) {
      const opcion = construirOpcionSerie(crearMarco({ series: 8, fechas: 50 }), {
        ...BASE,
        densidad,
      })

      expect(opcion.series.length).toBeGreaterThan(0)
      for (const serie of opcion.series) {
        expect(serie.sampling, densidad).toBe('lttb')
        expect(serie.large, densidad).toBe(true)
      }
    }
  })

  it('no dibuja marcadores: dos mil por linea es lo que convierte un pan en diapositivas', () => {
    const opcion = construirOpcionSerie(crearMarco({ series: 3, fechas: 2000 }), BASE)

    expect(opcion.series.every(serie => serie.showSymbol === false)).toBe(true)
    expect(opcion.animation).toBe(false)
  })
})

describe('el eje y los valores', () => {
  it('usa un eje de categoria con las fechas del marco', () => {
    // Moving to a time axis would force the [ts, valor] pair, double the
    // payload and make the zero copy subarray useless.
    const marco = crearMarco({ series: 2, fechas: 4 })
    const opcion = construirOpcionSerie(marco, BASE)

    expect(opcion.xAxis.type).toBe('category')
    expect(opcion.xAxis.data).toEqual(['2018-10-31', '2018-11-01', '2018-11-02', '2018-11-03'])
  })

  it('entrega a cada linea su propio tramo del vector plano', () => {
    // An off by one in the slice draws one line's data under another line's
    // name, and the result looks entirely credible.
    const marco = crearMarco({ series: 3, fechas: 4 })
    const opcion = construirOpcionSerie(marco, BASE)

    expect([...opcion.series[0]!.data]).toEqual([0, 10, 20, 30])
    expect([...opcion.series[1]!.data]).toEqual([1000, 1010, 1020, 1030])
    expect([...opcion.series[2]!.data]).toEqual([2000, 2010, 2020, 2030])
  })

  it('conserva el hueco como NaN en lugar de dibujar un cero', () => {
    // A zero drawn is an assertion about the balance; the gap is the truth.
    const marco = crearMarco({ series: 1, fechas: 3, huecos: [[0, 1]] })
    const opcion = construirOpcionSerie(marco, BASE)

    expect(Number.isNaN(opcion.series[0]!.data[1])).toBe(true)
  })
})

describe('el color deja de distinguir por encima de seis lineas', () => {
  it('colorea como mucho seis, y apaga el resto', () => {
    const marco = crearMarco({ series: 10, fechas: 5 })
    const opcion = construirOpcionSerie(marco, { ...BASE, densidad: 'detalle' })

    const coloreadas = opcion.series.filter(serie =>
      PALETA_SERIES.some(estilo => estilo.claro === serie.lineStyle.color),
    )

    expect(coloreadas).toHaveLength(MAXIMO_SERIES_COLOREADAS)
    expect(opcion.series.filter(serie => serie.symbol === 'none')).toHaveLength(4)
  })

  it('deja la carga completa entera en gris mientras nadie elige nada', () => {
    // 250 hues cannot be mapped back to any legend. The grey cloud reads as
    // aggregate behaviour, which is what it is.
    const marco = crearMarco({ series: 250, fechas: 20, conClaves: true })
    const opcion = construirOpcionSerie(marco, { ...BASE, densidad: 'completa' })

    expect(opcion.series).toHaveLength(250)
    expect(
      opcion.series.every(
        serie => !PALETA_SERIES.some(estilo => estilo.claro === serie.lineStyle.color),
      ),
    ).toBe(true)
  })

  it('levanta de la nube solo lo que el lector eligio', () => {
    const marco = crearMarco({ series: 250, fechas: 20, conClaves: true })
    const opcion = construirOpcionSerie(marco, {
      ...BASE,
      densidad: 'completa',
      seriesVisibles: [7, 42],
    })

    expect(opcion.series[7]!.lineStyle.color).toBe(PALETA_SERIES[0]!.claro)
    expect(opcion.series[42]!.lineStyle.color).toBe(PALETA_SERIES[1]!.claro)
    expect(opcion.series[7]!.z).toBeGreaterThan(opcion.series[8]!.z)
  })

  it('nunca colorea mas de seis aunque se elijan mas', () => {
    const marco = crearMarco({ series: 20, fechas: 5, conClaves: true })
    const elegidas = [1, 2, 3, 4, 5, 6, 7, 8]

    expect(indicesColoreados(marco, { densidad: 'detalle', seriesVisibles: elegidas })).toHaveLength(
      MAXIMO_SERIES_COLOREADAS,
    )
  })
})

describe('el identificador con el que la leyenda y el store hablan', () => {
  it('es la clave de la serie cuando el marco la trae', () => {
    const marco = crearMarco({ series: 3, fechas: 2, conClaves: true })

    expect(identificadorDeLinea(marco, 2)).toBe(2)
  })

  it('es la posicion en el marco cuando la linea es un agregado', () => {
    // Aggregated lines have no key: without this fallback the legend would try
    // to toggle a line identified as null and nothing would happen.
    const marco = crearMarco({ series: 3, fechas: 2 })

    expect(marco.catalogo[2]!.serieId).toBeNull()
    expect(identificadorDeLinea(marco, 2)).toBe(2)
  })
})

describe('el idioma y el modo llegan hasta la grafica', () => {
  it('rotula cada linea en el idioma en pantalla', () => {
    const marco = crearMarco({ series: 2, fechas: 3 })

    expect(construirOpcionSerie(marco, BASE).series[0]!.name).toBe('Linea 0')
    expect(construirOpcionSerie(marco, { ...BASE, idioma: 'en' }).series[0]!.name).toBe('Line 0')
  })

  it('pinta con la variante oscura del token cuando el modo es oscuro', () => {
    const marco = crearMarco({ series: 1, fechas: 3 })

    expect(construirOpcionSerie(marco, { ...BASE, modo: 'oscuro' }).series[0]!.lineStyle.color).toBe(
      PALETA_SERIES[0]!.oscuro,
    )
  })
})

describe('la ventana visible entra en la opcion', () => {
  it('arranca el dataZoom donde el lector lo dejo', () => {
    // Without this, reloading after a filter change would throw the reader back
    // to the whole period and lose the slice they were reading.
    const marco = crearMarco({ series: 1, fechas: 10 })
    const opcion = construirOpcionSerie(marco, { ...BASE, ventana: { inicio: 25, fin: 75 } })

    expect(opcion.dataZoom).toHaveLength(2)
    expect(opcion.dataZoom.every(zoom => zoom.start === 25 && zoom.end === 75)).toBe(true)
  })
})

describe('la altura reservada', () => {
  it('es una sola constante en pixeles', () => {
    // Two heights, one for the skeleton and one for the chart, is how a layout
    // shift appears the moment the data lands.
    expect(ALTO_GRAFICA).toMatch(/^\d+px$/)
  })
})

describe('la reticula habla el dialecto de ECharts 6', () => {
  it('pide contener las etiquetas por outerBoundsMode, no por outerBounds', () => {
    // Este caso existe por un defecto que llego a la rama y que ninguna prueba
    // vio: la opcion traia `outerBounds: 'same'`. En ECharts 6 `outerBounds` es
    // un rectangulo -{left, right, top, bottom, width, height}- y la cadena va
    // en `outerBoundsMode`. Con la cadena en el sitio equivocado, mergeLayoutParam
    // intenta escribir `.width` sobre un string, lanza un TypeError, setOption
    // aborta y la grafica NO SE PINTA: el contenedor se queda sin canvas y la
    // pagina parece correcta salvo por el hueco. Se descubrio en navegador real
    // porque aqui el tipo de la opcion es Record<string, unknown> y typecheck no
    // podia verlo.
    const opcion = construirOpcionSerie(crearMarco({ series: 3, fechas: 20 }), BASE)

    expect(opcion.grid.outerBoundsMode).toBe('same')
    expect(typeof opcion.grid.outerBounds).not.toBe('string')
  })
})
