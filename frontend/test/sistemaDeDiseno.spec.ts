/**
 * The design system, asserted against the rules it publishes.
 *
 * This file replaces three specs written against the previous generator. It is
 * shorter on purpose: the previous ones fixed the markup of plates that this
 * redesign rewrote, which is the kind of test that gets deleted at the first
 * real change and buys coverage that means nothing in the meantime. What
 * survives here is what would still fail if the system regressed.
 */
import { readFileSync, readdirSync } from 'node:fs'
import { join, resolve } from 'node:path'
import { describe, expect, it } from 'vitest'
import {
  ANILLO_FOCO,
  ANILLO_FOCO_CONGELADO,
  ANILLO_FOCO_INTERNO,
  ANILLO_FOCO_INVERSO,
} from '~/utils/foco'
import {
  CONTRASTES,
  CORRIENTE,
  PEOR_SEPARACION,
  SEMANTICOS,
  SEPARACIONES,
  TIPOGRAFIA,
  TOKENS,
} from '~/utils/tokens.generated'

/** vitest runs with the frontend package as its working directory. */
const RAIZ_APP = resolve(process.cwd(), 'app')

/** Every .vue of the application, read once. */
function fuentesVue(directorio = RAIZ_APP): { ruta: string, texto: string }[] {
  return readdirSync(directorio, { withFileTypes: true }).flatMap((entrada) => {
    const ruta = join(directorio, entrada.name)
    if (entrada.isDirectory()) return fuentesVue(ruta)
    if (!entrada.name.endsWith('.vue')) return []
    return [{ ruta, texto: readFileSync(ruta, 'utf8') }]
  })
}

describe('el sistema cumple las reglas que publica', () => {
  it('no deja ningún token que informa por debajo del límite de componente', () => {
    // The flag is the whole point: a token that declares it does not inform is
    // exempt, and one that claims to inform and cannot be seen is a defect.
    const informan = new Set(TOKENS.filter(token => token.informa).map(token => token.nombre))
    const fallan = CONTRASTES.filter(
      par => informan.has(par.token) && par.veredicto === 'falla',
    )

    expect(fallan).toEqual([])
  })

  it('mide cada token en los dos modos y no en uno solo', () => {
    // A ratio measured over a light ground says nothing about the dark one, and
    // the previous system published a single matrix for a single mode.
    for (const modo of ['claro', 'oscuro'] as const) {
      const medidos = CONTRASTES.filter(par => par.modo === modo)

      expect(medidos.length).toBe(TOKENS.length - 1)
    }
  })

  it('mantiene la rampa de corriente separada por luminancia y no por tono', () => {
    // The ramp is the channel no dichromacy loses. If two rungs ever collapse
    // into the same value, state stops being readable for a colourblind reader
    // and nothing else in the suite would notice.
    for (const modo of ['claro', 'oscuro'] as const) {
      const valores = CORRIENTE.map(token => (modo === 'claro' ? token.claro : token.oscuro))

      expect(new Set(valores).size).toBe(CORRIENTE.length)
    }
  })

  it('publica la separación semántica peor de cada modo', () => {
    for (const modo of ['claro', 'oscuro'] as const) {
      const medidas = SEPARACIONES.filter(s => s.modo === modo)

      // Six pairs out of four semantic marks.
      expect(medidas.length).toBe((SEMANTICOS.length * (SEMANTICOS.length - 1)) / 2)
      expect(Math.min(...medidas.map(s => s.distancia))).toBe(PEOR_SEPARACION[modo])
    }
  })

  it('deja el modo claro por debajo del umbral, que es el motivo de la regla de forma', () => {
    // Not an aspiration: on a light ground four semantics all clearing 4.5:1 are
    // capped below 0.16 luminance and cannot separate by 20. The test pins the
    // ceiling so that "colour plus shape plus icon" cannot be softened into a
    // preference later.
    expect(PEOR_SEPARACION.claro).toBeLessThan(20)
    expect(PEOR_SEPARACION.oscuro).toBeGreaterThanOrEqual(20)
  })
})

describe('la escala tipográfica usa el peso como canal', () => {
  it('no fija un solo peso en los nueve roles', () => {
    // The measured page had 750 of 750 text nodes at weight 400, headings
    // included. One weight across nine roles is one channel, not nine roles.
    expect(new Set(TIPOGRAFIA.map(rol => rol.peso)).size).toBeGreaterThan(1)
  })

  it('da a los titulares más peso que al texto corrido', () => {
    const cuerpo = TIPOGRAFIA.find(rol => rol.nombre === 'cuerpo')
    const titulo = TIPOGRAFIA.find(rol => rol.nombre === 'titulo-1')

    expect(titulo!.peso).toBeGreaterThan(cuerpo!.peso)
  })
})

describe('el anillo de foco tiene una sola definición', () => {
  it('congela exactamente el anillo que el navegador pinta', () => {
    // A frozen state that drifts from the live one is the whole defect: the
    // plate would document, and capture into the PDF, a ring no control paints.
    expect(ANILLO_FOCO_CONGELADO).toBe(ANILLO_FOCO.replaceAll('focus-visible:', ''))
  })

  it('mantiene el grosor en las cuatro variantes', () => {
    for (const anillo of [ANILLO_FOCO, ANILLO_FOCO_INVERSO, ANILLO_FOCO_INTERNO]) {
      expect(anillo).toContain('focus-visible:outline-2')
    }
  })

  it('no deja ningún componente escribiendo su propio contorno', () => {
    // Fifteen of eighty three focusable elements fell back to the browser
    // default in the audited build, because the frozen cells wrote their own.
    const culpables = fuentesVue()
      .filter(({ texto }) => /(?<!focus-visible:)outline-\d/.test(texto.replace(/foco'/g, '')))
      .map(({ ruta }) => ruta.replace(RAIZ_APP, '').replace(/\\/g, '/'))
      .filter(ruta => !ruta.includes('utils'))

    expect(culpables).toEqual([])
  })
})
