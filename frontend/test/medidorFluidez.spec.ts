import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import SerieMedidor from '~/components/serie/Medidor.vue'
import {
  construirInforme,
  MAXIMO_CUADROS_LARGOS,
  PEOR_CUADRO_MS,
  resumirIntervalos,
  veredictoDe,
} from '~/composables/useMedidorFluidez'
import { GUION_ZOOM, PASOS_GUION, UMBRAL_CUADRO_MS, VERSION_GUION } from '~/utils/guionFluidez'
import { crearI18nDePrueba, mensaje } from './i18nDePrueba'

/**
 * US-025 — the fluidity measurement, which is evidence that reaches the A4
 * document.
 *
 * The run itself is not simulated here: a meter driven by a fake clock measures
 * the fake clock. What is measured is everything that decides what the reported
 * number MEANS -the threshold, the percentile, the verdict and the script- since
 * those are the parts that can be wrong while the run looks perfectly healthy.
 */

const ENTORNO = {
  navegador: 'Chrome/141',
  plataforma: 'Win32',
  viewport: '1440x900',
  densidadPixel: 2,
}

describe('el guion de pan y zoom esta congelado', () => {
  it('tiene exactamente los pasos que declara', () => {
    // Changing the gesture and comparing against an earlier measurement is
    // comparing two different experiments.
    expect(GUION_ZOOM).toHaveLength(PASOS_GUION)
  })

  it('no se puede modificar en caliente', () => {
    expect(Object.isFrozen(GUION_ZOOM)).toBe(true)
    expect(Object.isFrozen(GUION_ZOOM[0])).toBe(true)
  })

  it('recorre acercar, desplazar y alejar sin salirse del eje', () => {
    for (const paso of GUION_ZOOM) {
      expect(paso.inicio).toBeGreaterThanOrEqual(0)
      expect(paso.fin).toBeLessThanOrEqual(100)
      expect(paso.inicio).toBeLessThan(paso.fin)
    }

    const primero = GUION_ZOOM[0]!
    const ultimo = GUION_ZOOM[PASOS_GUION - 1]!
    const medio = GUION_ZOOM[Math.floor(PASOS_GUION / 3) - 1]!

    // The zoom really closes in, the pan really moves and the view really opens
    // back up: a script that never widened the window would skip the expensive
    // gesture, which is precisely the one worth measuring.
    expect(medio.fin - medio.inicio).toBeLessThan(primero.fin - primero.inicio)
    expect(GUION_ZOOM[Math.floor((2 * PASOS_GUION) / 3) - 1]!.inicio).toBeGreaterThan(medio.inicio)
    expect(ultimo).toEqual({ inicio: 0, fin: 100 })
  })
})

describe('la muestra se calcula sobre los intervalos, no sobre las marcas', () => {
  it('promedia y ordena diferencias entre cuadros', () => {
    // Feeding timestamps instead of differences produces an enormous, steadily
    // growing number and nobody can say why.
    const muestra = resumirIntervalos([16, 17, 16, 100, 16])

    expect(muestra.cuadros).toBe(5)
    expect(muestra.p50).toBe(16)
    expect(muestra.peor).toBe(100)
    expect(muestra.duracionMs).toBe(165)
  })

  it('toma el percentil 95 por rango sobre la muestra ordenada', () => {
    const intervalos = Array.from({ length: 100 }, (_, indice) => indice + 1)

    expect(resumirIntervalos(intervalos).p95).toBe(95)
  })

  it('cuenta como largo el cuadro que pasa del umbral, y solo ese', () => {
    // A meter that counts everything or nothing produces evidence that means
    // nothing, and that evidence goes into the document.
    const muestra = resumirIntervalos([UMBRAL_CUADRO_MS, UMBRAL_CUADRO_MS + 0.5, 10])

    expect(muestra.largos).toBe(1)
  })
})

describe('el veredicto no se pronuncia con un solo numero', () => {
  it('falla cuando el peor cuadro se dispara aunque el p95 este bien', () => {
    // A single stall of half a second is exactly what the reader perceives, and
    // a p95 alone hides it.
    const intervalos = [...Array.from({ length: 99 }, () => 16), PEOR_CUADRO_MS + 1]

    expect(veredictoDe(resumirIntervalos(intervalos))).toBe('no-cumple')
  })

  it('falla cuando hay demasiados cuadros largos', () => {
    const largos = Math.floor(100 * MAXIMO_CUADROS_LARGOS) + 1
    const intervalos = [
      ...Array.from({ length: 100 - largos }, () => 16),
      ...Array.from({ length: largos }, () => UMBRAL_CUADRO_MS + 5),
    ]

    expect(veredictoDe(resumirIntervalos(intervalos))).toBe('no-cumple')
  })

  it('no declara que se cumple sin haber medido nada', () => {
    expect(veredictoDe(resumirIntervalos([]))).toBe('no-cumple')
  })

  it('cumple cuando los tres limites se respetan', () => {
    expect(veredictoDe(resumirIntervalos(Array.from({ length: 100 }, () => 16)))).toBe('cumple')
  })
})

describe('el informe dice donde y con que guion se midio', () => {
  it('lleva dentro la version del guion, sus pasos y la maquina', () => {
    // "p95 = 21 ms" without saying where is not a datum, it is an anecdote; and
    // two measurements of two different scripts are not comparable.
    const informe = construirInforme([16, 17], ENTORNO, '2026-08-12T10:00:00.000Z')

    expect(informe.versionGuion).toBe(VERSION_GUION)
    expect(informe.pasos).toBe(PASOS_GUION)
    expect(informe.umbralMs).toBe(UMBRAL_CUADRO_MS)
    expect(informe.entorno).toEqual(ENTORNO)
    expect(informe.momento).toBe('2026-08-12T10:00:00.000Z')
    expect(informe.muestra.cuadros).toBe(2)
  })

  it('el panel anuncia el veredicto que el informe trae, no el contrario', () => {
    // An inverted verdict would put a green "meets the threshold" into the
    // screenshot that goes into the document, which is the one place where
    // being wrong costs the most and shows the least.
    const fallido = construirInforme([...Array.from({ length: 20 }, () => 400)], ENTORNO, 'ahora')
    const wrapper = mount(SerieMedidor, {
      props: { midiendo: false, informe: fallido },
      global: { plugins: [crearI18nDePrueba()], stubs: { Icon: true } },
    })

    expect(fallido.veredicto).toBe('no-cumple')
    expect(wrapper.get('[data-veredicto]').text()).toBe(
      mensaje('es', 'dashboard.measure.verdict.fail'),
    )
    expect(wrapper.get('[data-medida="p95"]').exists()).toBe(true)
    expect(wrapper.text()).toContain(String(VERSION_GUION))
  })

  it('sin informe no ensena cifras que nadie ha medido', () => {
    const wrapper = mount(SerieMedidor, {
      props: { midiendo: false, informe: null },
      global: { plugins: [crearI18nDePrueba()], stubs: { Icon: true } },
    })

    expect(wrapper.find('[data-veredicto]').exists()).toBe(false)
    expect(wrapper.find('[data-medida]').exists()).toBe(false)
    expect(wrapper.get('[data-accion="medir"]').text()).toBe(mensaje('es', 'dashboard.measure.run'))
  })
})
