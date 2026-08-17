import type { VueWrapper } from '@vue/test-utils'

import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import MarcaKarisma from '~/components/comun/MarcaKarisma.vue'
import { crearI18nDePrueba, mensaje } from './i18nDePrueba'

/**
 * US-A4-EXCELENCIA, ola B - the logotype of the normative page.
 *
 * The shipped defect is exact: the portal named itself with
 * `lucide:circuit-board`, a packaged icon tinted with the informative colour,
 * where the design file has a page called "Uso del logotipo" declaring the K
 * symbol on a rounded tile, three variants and two rules. The reviewer's
 * sentence -"el logo que traiamos pusiste uno que nada que ver"- is the defect
 * this component closes.
 *
 * What is measured here is what the guide normalises and what a careless edit
 * would silently break: that the drawing is vector and inline, that the three
 * variants are three different drawings and not one prop with no effect, that
 * the proportion survives any size because it lives in a viewBox, and that the
 * accent bar gives up the amber in the one-ink variant.
 *
 * Nothing here asserts a hex against the design file by eye: the values were
 * measured off the page rendered at 600 dpi and they are pinned below, so an
 * edit that "adjusts" a colour has to say so out loud.
 */

/** The three variants of the normative page. */
const VARIANTES = ['principal', 'inverso', 'monocromatico'] as const

/** Values measured on the plate, and the palette row each one comes from. */
const ACCION = '#086B70'
const NAVEGACION = '#102A43'
const ATENCION = '#B97812'
const SUPERFICIE = '#FFFFFF'

function montar(props: Record<string, unknown> = {}): VueWrapper {
  return mount(MarcaKarisma, {
    props,
    global: { plugins: [crearI18nDePrueba('es')] },
  })
}

/** Fill of every rectangle of the symbol, in document order. */
function rellenos(wrapper: VueWrapper): string[] {
  return wrapper.findAll('svg rect').map(rect => rect.attributes('fill') ?? '')
}

describe('la marca es vectorial y se dibuja aqui', () => {
  it('emite un svg en linea, sin imagen ni icono de paquete', () => {
    // CA-6, verbatim: zero `<img>` and zero packaged icons in the mark. A PNG
    // would be a reinterpretation of a drawing the guide forbids deforming,
    // and `a4_03` asks for a vector mark.
    const wrapper = montar()

    expect(wrapper.findAll('svg')).toHaveLength(1)
    expect(wrapper.findAll('img')).toHaveLength(0)
    expect(wrapper.html()).not.toContain('lucide')
    expect(wrapper.html()).not.toContain('<Icon')
  })

  it('fija la geometria en proporcion y no en pixeles', () => {
    // The rule of the plate is "conservar su proporcion" at every size, and a
    // viewBox is the only way to promise it. Measured on the page: the tile is
    // 931 x 933 px at 600 dpi, so it is square.
    expect(montar().get('svg').attributes('viewBox')).toBe('0 0 100 100')
  })

  it('dibuja la teja y las cuatro barras, y ninguna se sale de la teja', () => {
    // The K is a stem and two descending arms over a baseline bar: five
    // rectangles. A bar whose box left the tile would be clipped on one plate
    // and not on another, which is how a mark starts to look "almost right".
    const wrapper = montar()
    const rects = wrapper.findAll('svg rect')

    expect(rects).toHaveLength(5)
    for (const rect of rects) {
      const x = Number(rect.attributes('x'))
      const y = Number(rect.attributes('y'))
      const ancho = Number(rect.attributes('width'))
      const alto = Number(rect.attributes('height'))

      expect(x, rect.html()).toBeGreaterThanOrEqual(0)
      expect(y, rect.html()).toBeGreaterThanOrEqual(0)
      expect(x + ancho, rect.html()).toBeLessThanOrEqual(100)
      expect(y + alto, rect.html()).toBeLessThanOrEqual(100)
    }
  })

  it('conserva las proporciones medidas en la lamina', () => {
    // Every ratio below was measured on "Uso del logotipo" at 600 dpi. They
    // are asserted together because the mark is a rhythm and not four
    // independent boxes: the three columns share a width and a gutter, the
    // three bars share a top edge, and the stem and the accent share a
    // baseline.
    const wrapper = montar()
    const caja = (selector: string) => {
      const rect = wrapper.get(selector)
      return {
        x: Number(rect.attributes('x')),
        y: Number(rect.attributes('y')),
        ancho: Number(rect.attributes('width')),
        alto: Number(rect.attributes('height')),
      }
    }

    const asta = caja('[data-marca-barra="asta"]')
    const alto = caja('[data-marca-barra="brazo-alto"]')
    const corto = caja('[data-marca-barra="brazo-corto"]')
    const base = caja('[data-marca-barra="base"]')

    // One width for the three columns, and one gutter between them.
    expect(alto.ancho).toBe(asta.ancho)
    expect(corto.ancho).toBe(asta.ancho)
    expect(alto.x - (asta.x + asta.ancho)).toBeCloseTo(corto.x - (alto.x + alto.ancho), 1)

    // One top edge for the three bars, and descending heights.
    expect(alto.y).toBe(asta.y)
    expect(corto.y).toBe(asta.y)
    expect(asta.alto).toBeGreaterThan(alto.alto)
    expect(alto.alto).toBeGreaterThan(corto.alto)

    // The accent spans from the second column to the end of the third, and it
    // shares its baseline with the stem.
    expect(base.x).toBe(alto.x)
    expect(base.x + base.ancho).toBeCloseTo(corto.x + corto.ancho, 1)
    expect(base.y + base.alto).toBeCloseTo(asta.y + asta.alto, 1)

    // Vertical margins are symmetric: 19.6 % measured top and bottom.
    expect(asta.y).toBeCloseTo(100 - (asta.y + asta.alto), 1)
  })

  it('redondea la teja, como la lamina', () => {
    // Measured radius: 56 px over a 932 px side, 6.0 %. A square tile would be
    // another mark.
    const teja = montar().get('[data-marca-teja]')

    expect(Number(teja.attributes('rx'))).toBeGreaterThan(0)
    expect(Number(teja.attributes('width'))).toBe(100)
    expect(Number(teja.attributes('height'))).toBe(100)
  })
})

describe('las tres variantes son tres dibujos distintos', () => {
  it.each(VARIANTES)('declara la variante %s en el marcado', (variante) => {
    expect(montar({ variante }).get('[data-marca-karisma]').attributes('data-variante'))
      .toBe(variante)
  })

  it('usa la teja de accion en la principal y en la inversa', () => {
    // Both plates were measured and the drawing is identical, teal tile
    // included: what the inverse variant changes is the ground it is meant
    // for, and the wordmark it carries there.
    for (const variante of ['principal', 'inverso'] as const) {
      expect(rellenos(montar({ variante }))[0], variante).toBe(ACCION)
    }
  })

  it('cambia a una sola tinta en la monocromatica', () => {
    // "Para documentos sin color, sellos y aplicaciones de una tinta". The
    // amber is the first thing that has to go: one ink cannot carry the
    // attention channel and the structure at the same time.
    const monocromatica = rellenos(montar({ variante: 'monocromatico' }))

    expect(monocromatica[0]).toBe(NAVEGACION)
    expect(new Set(monocromatica.slice(1))).toEqual(new Set([SUPERFICIE]))
    expect(monocromatica).not.toContain(ATENCION)
  })

  it('reserva el ambar para la barra de base de las variantes en color', () => {
    // Exactly one element carries the attention channel, and it is the same
    // one in both coloured variants. Painting a second element amber would
    // spend on decoration a colour this system reserves for a state.
    for (const variante of ['principal', 'inverso'] as const) {
      const wrapper = montar({ variante })

      expect(rellenos(wrapper).filter(relleno => relleno === ATENCION), variante).toHaveLength(1)
      expect(wrapper.get('[data-marca-acento]').attributes('fill'), variante).toBe(ATENCION)
    }
  })

  it('no se recolorea con el tema: los rellenos son literales del archivo', () => {
    // The guide forbids recolouring the mark. Painting the tile with
    // `--color-accion` would repaint it every time the reader switched theme,
    // because that token is teal only under the institutional one.
    const marcado = montar().html()

    expect(marcado).not.toContain('var(--color-')
    expect(marcado).toContain(ACCION)
  })

  it('pinta el nombre segun la variante, que es lo que distingue inverso de principal', () => {
    // Standalone the two coloured variants are the same drawing. In a lockup
    // they are not: over navy the file sets the wordmark in white, and over a
    // light ground it takes the ink of whatever hosts it.
    const nombreDe = (variante: typeof VARIANTES[number]): string =>
      montar({ variante, conNombre: true }).get('[data-marca-nombre]').attributes('style') ?? ''

    expect(nombreDe('inverso')).toContain('color')
    expect(nombreDe('inverso')).not.toBe(nombreDe('principal'))
    expect(nombreDe('monocromatico')).not.toBe(nombreDe('principal'))
  })
})

describe('la marca se anuncia una sola vez', () => {
  it('nombra el producto cuando viaja sola', () => {
    // A drawing with no accessible name is announced as nothing at all, and
    // the mark is the only thing in the bar that says whose portal this is.
    const svg = montar().get('svg')

    expect(svg.attributes('role')).toBe('img')
    expect(svg.attributes('aria-label')).toBe(mensaje('es', 'brand.name'))
  })

  it('se calla cuando el nombre viaja escrito a su lado', () => {
    // Otherwise a screen reader announces "Karisma Data" twice in a row.
    const wrapper = montar({ conNombre: true })

    expect(wrapper.get('svg').attributes('aria-hidden')).toBe('true')
    expect(wrapper.get('svg').attributes('aria-label')).toBeUndefined()
    expect(wrapper.get('[data-marca-nombre]').text()).toBe(mensaje('es', 'brand.name'))
  })

  it('traduce nada del nombre, que es propio, pero lo lee del catalogo', () => {
    // 'Karisma Data' is a proper name and reads the same in both languages;
    // what matters is that it is not typed inside the component, which is the
    // rule every visible string of this interface follows.
    const enIngles = mount(MarcaKarisma, {
      props: { conNombre: true },
      global: { plugins: [crearI18nDePrueba('en')] },
    })

    expect(enIngles.get('[data-marca-nombre]').text()).toBe(mensaje('en', 'brand.name'))
  })
})

describe('las dos reglas de aplicacion viajan con la marca', () => {
  it('reserva el area de proteccion y no la deja al criterio de quien la monta', () => {
    // "Reserva alrededor del simbolo un espacio libre minimo equivalente a
    // 1/2 K". With a 32 px symbol that is 16 px, and it is declared by the
    // component so that no host can crowd the mark by forgetting it.
    expect(montar().get('[data-marca-karisma]').classes()).toContain('pe-4')
  })

  it('no baja del tamano minimo digital del simbolo', () => {
    // "Simbolo digital: 32 px". The class is the size and the floor at once:
    // the symbol is never rendered smaller than the plate allows.
    expect(montar().get('[data-marca-simbolo]').classes()).toContain('size-8')
  })

  it('reserva el ancho minimo de la marca completa cuando lleva el nombre', () => {
    // "Marca completa: 120 px de ancho".
    const conNombre = montar({ conNombre: true }).get('[data-marca-karisma]')
    const sola = montar().get('[data-marca-karisma]')

    expect(conNombre.classes()).toContain('min-w-30')
    expect(sola.classes()).not.toContain('min-w-30')
  })
})
