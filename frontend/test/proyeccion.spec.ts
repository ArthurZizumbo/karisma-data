import type { PuntoMensual } from '~/types/prediccion'

import { describe, expect, it, vi } from 'vitest'

import { destinoExplorador, METRICAS_PREDICCION, RUTA_EXPLORADOR } from '~/utils/metricasTablero'
import {
  etiquetaMetodo,
  MINIMO_PUNTOS,
  mesSiguiente,
  PLANTILLAS_METODO,
  proyectarLineal,
  VENTANA_POR_DEFECTO,
} from '~/utils/proyeccion'
import { RUTAS_CONTRATO } from '~/utils/navegacion'
import { clavesDe } from './i18nDePrueba'

/**
 * US-026 - the computation and its label, without mounting Vue.
 *
 * Everything the predictive cards show hangs on this module: the figure, the
 * change, and the sentence that states how the figure was produced. The screen
 * is presentation over these values, so a defect here is a plausible wrong
 * number wearing a rigorous label, which is the exact failure the User Story
 * exists to prevent.
 */

/** Monthly points with consecutive months, oldest first. */
function serie(valores: readonly number[], desde = '2024-07'): PuntoMensual[] {
  let mes = desde
  return valores.map((valor) => {
    const punto: PuntoMensual = { mes, valor }
    mes = mesSiguiente(mes)
    return punto
  })
}

/** A perfect line: value = 2 * index + 1. */
function recta(puntos: number, desde = '2024-07'): PuntoMensual[] {
  return serie(Array.from({ length: puntos }, (_, indice) => 2 * indice + 1), desde)
}

describe('proyectarLineal', () => {
  it('ajusta exactamente una recta perfecta', () => {
    // A regression with the intercept sign flipped, or with the index shifted
    // by one month, produces a plausible and wrong figure. The only way to see
    // it is to feed it a line whose continuation is known in advance.
    const proyeccion = proyectarLineal('saldo-disponible', recta(12))

    expect(proyeccion).not.toBeNull()
    expect(proyeccion!.proyectado.valor).toBe(25)
    expect(proyeccion!.metodo.parametros.r2).toBe(1)
  })

  it('proyecta el mes siguiente y no el mismo', () => {
    // The classic end of year defect: 2026-12 turning into 2026-13, which no
    // formatter would render and every screenshot would carry.
    const proyeccion = proyectarLineal('saldo-disponible', recta(8, '2026-05'))

    expect(proyeccion!.ultimo.mes).toBe('2026-12')
    expect(proyeccion!.proyectado.mes).toBe('2027-01')
  })

  it('usa solo la ventana pedida y toma los ultimos meses', () => {
    // Taking the first twelve of twenty four projects the past: the figure
    // looks reasonable and describes a year that already happened.
    const proyeccion = proyectarLineal('saldo-disponible', recta(24), { ventana: 12 })

    expect(proyeccion!.serieUsada).toHaveLength(12)
    expect(proyeccion!.serieUsada[0]!.valor).toBe(25)
    expect(proyeccion!.serieUsada.at(-1)!.valor).toBe(47)
  })

  it('mide los parametros que uso, no los que le pidieron', () => {
    // Lock 2 of the anti drift mechanism. Without this assertion the label can
    // promise twelve months of history that never existed.
    const proyeccion = proyectarLineal('saldo-disponible', recta(8), { ventana: 12 })

    expect(proyeccion!.serieUsada).toHaveLength(8)
    expect(proyeccion!.metodo.parametros.points).toBe(8)
    expect(proyeccion!.metodo.parametros.horizon).toBe(1)
  })

  it('devuelve null por debajo del minimo', () => {
    // Publishing a trend out of five points and putting a method name on top
    // of it is the dishonesty this User Story is about.
    expect(proyectarLineal('saldo-disponible', recta(MINIMO_PUNTOS - 1))).toBeNull()
    expect(proyectarLineal('saldo-disponible', recta(MINIMO_PUNTOS))).not.toBeNull()
  })

  it('devuelve null ante una serie degenerada', () => {
    // Twelve identical values leave no variance to explain: R squared is 0/0.
    // Without this branch the card prints "R2 NaN".
    const plana = serie(Array.from({ length: 12 }, () => 1.5))

    expect(proyectarLineal('cobertura-liquidez', plana)).toBeNull()
  })

  it('descarta los puntos que no son numeros antes de ajustar', () => {
    // A regenerated payload with a null in the middle would otherwise poison
    // every sum and turn the whole card into NaN.
    const conHueco = recta(12) as PuntoMensual[]
    conHueco[4] = { mes: conHueco[4]!.mes, valor: Number.NaN }

    const proyeccion = proyectarLineal('saldo-disponible', conHueco)

    expect(proyeccion!.serieUsada).toHaveLength(11)
    expect(Number.isFinite(proyeccion!.proyectado.valor)).toBe(true)
  })

  it('mide la variacion contra el ultimo observado', () => {
    // Measuring it against the first point of the window gives a much larger
    // and much more flattering figure, and nothing on screen would say so.
    const proyeccion = proyectarLineal('saldo-disponible', recta(12))

    expect(proyeccion!.ultimo.valor).toBe(23)
    expect(proyeccion!.variacionPct).toBeCloseTo(((25 - 23) / 23) * 100, 10)
  })

  it('proyecta con la ventana por defecto cuando no se le pide ninguna', () => {
    // The default is what the three cards of the screen actually use, so a
    // change of its value has to be visible in the descriptor as well.
    const proyeccion = proyectarLineal('saldo-disponible', recta(24))

    expect(proyeccion!.serieUsada).toHaveLength(VENTANA_POR_DEFECTO)
    expect(proyeccion!.metodo.parametros.points).toBe(VENTANA_POR_DEFECTO)
  })
})

describe('la etiqueta de metodo no puede separarse del calculo', () => {
  it('registra una plantilla por cada metodo y la tiene en los dos catalogos', () => {
    // Adding a method and leaving its label pointing at a key nobody wrote
    // makes vue-i18n print the dotted path verbatim, in both languages, right
    // inside the figure that goes into the A4 document.
    const claves = { es: new Set(clavesDe('es')), en: new Set(clavesDe('en')) }
    const plantillas = Object.values(PLANTILLAS_METODO)

    expect(plantillas.length).toBeGreaterThan(0)
    for (const plantilla of plantillas) {
      expect(claves.es.has(plantilla), `es: ${plantilla}`).toBe(true)
      expect(claves.en.has(plantilla), `en: ${plantilla}`).toBe(true)
    }
  })

  it('se compone con la clave y los parametros del descriptor', () => {
    // A component that built the sentence by concatenation would leave the
    // English reader with a Spanish label and no test would notice.
    const proyeccion = proyectarLineal('saldo-disponible', recta(12))!
    const traductor = vi.fn(() => 'etiqueta')

    const etiqueta = etiquetaMetodo(proyeccion.metodo, 'es', traductor)

    expect(etiqueta).toBe('etiqueta')
    expect(traductor).toHaveBeenCalledWith(proyeccion.metodo.clavePlantilla, {
      points: '12',
      horizon: '1',
      r2: '1.00',
    })
  })

  it('cambia de texto cuando cambia la ventana del calculo', () => {
    // The assertion that turns red the day somebody writes the label as a
    // fixed string again.
    const historico = recta(24)
    const t = (clave: string, parametros: Record<string, string>): string =>
      `${clave}|${parametros.points}`

    const doce = etiquetaMetodo(proyectarLineal('saldo-disponible', historico, { ventana: 12 })!.metodo, 'es', t)
    const seis = etiquetaMetodo(proyectarLineal('saldo-disponible', historico, { ventana: 6 })!.metodo, 'es', t)

    expect(doce).toContain('12')
    expect(seis).toContain('6')
    expect(doce).not.toBe(seis)
  })
})

describe('el destino del explorador existe en el contrato de navegacion', () => {
  it('apunta las tres metricas a una ruta declarada, con su columna fisica', () => {
    // A link to "/explorador" written from memory answers 404 in the middle of
    // the demo, and the card looks perfectly fine until somebody clicks it.
    expect(METRICAS_PREDICCION).toHaveLength(3)
    expect(RUTAS_CONTRATO).toContain(RUTA_EXPLORADOR)

    for (const metrica of METRICAS_PREDICCION) {
      const destino = destinoExplorador(metrica)

      expect(destino.split('?')[0]).toBe(RUTA_EXPLORADOR)
      expect(destino).toContain(`q=${metrica.campoOrigen}`)
    }
  })
})
