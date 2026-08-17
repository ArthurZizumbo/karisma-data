import type { VueWrapper } from '@vue/test-utils'
import type { PaginaCatalogo } from '~/composables/useBusquedaCatalogo'
import type { CampoCatalogo } from '~/types/linaje'

import { mount } from '@vue/test-utils'
import { defineComponent, nextTick } from 'vue'
import { afterEach, describe, expect, it, vi } from 'vitest'

import ExploracionResultadosCatalogo from '~/components/exploracion/ResultadosCatalogo.vue'
import Guia from '~/pages/guia.vue'
import { certificacionDeCampo } from '~/composables/useBusquedaCatalogo'
import { useSistemaDiseno } from '~/stores/sistemaDiseno'
import { CODIGOS_FACETA } from '~/types/linaje'
import {
  BARRA_LATERAL,
  CERTIFICACION,
  ESTADOS_CERTIFICACION,
  SEPARACIONES_CERTIFICACION_POR_TEMA,
} from '~/utils/tokens.generated'
import { crearI18nDePrueba, mensaje } from './i18nDePrueba'

/**
 * US-A4-EXCELENCIA, CA-11 — the three certification states are three.
 *
 * The defect this closes was literal and shipped:
 * `codigo === 'certificado' ? 'circle-check' : 'triangle-alert'`. "En revisión"
 * and "Obsoleto" therefore shared the icon AND the colour, and for the primary
 * persona they mean opposite things: one may be used with reserve, the other
 * must not be used at all. A reader with protanopia had nothing left to tell
 * them apart, because shape was the channel that was supposed to carry it.
 *
 * Two seams can break here and nowhere else:
 *
 * 1. THE SPELLING CROSSES A BOUNDARY. The catalogue stores `en_revision` -that
 *    is the CHECK constraint of the migration- and the design system names the
 *    token `certificacion-en-revision`. A crossing that is forgotten does not
 *    throw: the state resolves to null and the badge ships colourless, which
 *    looks like a design decision.
 * 2. THE COMPONENT COULD DECIDE AGAIN. Nothing stops a future edit from writing
 *    a ternary back into the template, and every other assertion of the
 *    catalogue suite would stay green.
 */

/** One field of the catalogue, in the vocabulary of the interface. */
function campo(fieldId: number, certification: string): CampoCatalogo {
  return {
    fieldId,
    physicalName: `campo_${fieldId}`,
    businessName: `Campo ${fieldId}`,
    definition: 'Definicion sembrada del campo.',
    source: { code: 'liquidez', displayName: 'Tesoreria y liquidez' },
    owner: { area: 'Tesoreria', steward: 'Ana Ruiz' },
    validity: { validFrom: '2024-01-01', validTo: null, isCurrent: true },
    facets: {
      domain: 'liquidez',
      dataType: 'decimal',
      sensitivity: 'interna',
      refreshFrequency: 'diaria',
      certification,
      unit: 'MXN',
      metricAgg: 'sum',
    },
  }
}

/** A page carrying one field per certification value the catalogue admits. */
const PAGINA: PaginaCatalogo = {
  total: CODIGOS_FACETA.certification.length,
  campos: CODIGOS_FACETA.certification.map((codigo, indice) => campo(indice + 1, codigo)),
  dominios: [{ codigo: 'liquidez', total: 3 }],
}

const EnlaceStub = defineComponent({
  props: { to: { type: String, required: true } },
  template: '<a :href="to"><slot /></a>',
})

/** Mounts the result table over the page above. */
function montar(): VueWrapper {
  return mount(ExploracionResultadosCatalogo, {
    props: { pagina: PAGINA, cargando: false, error: null },
    global: {
      plugins: [crearI18nDePrueba('es')],
      components: { NuxtLink: EnlaceStub },
      stubs: { Icon: { props: ['name'], template: '<i :data-icono="name" />' } },
    },
  })
}

describe('los tres estados de certificacion no comparten canal', () => {
  it('el sistema declara tres iconos distintos y tres clases distintas', () => {
    // The defect in its purest form: two states resolving to the same shape.
    // Reading the table instead of the component is deliberate -the component
    // is forbidden from choosing- so this fails the moment the emitter stops
    // separating them.
    const iconos = ESTADOS_CERTIFICACION.map(estado => estado.icono)
    const clases = ESTADOS_CERTIFICACION.map(estado => estado.clase)

    expect(ESTADOS_CERTIFICACION).toHaveLength(3)
    expect(new Set(iconos).size).toBe(3)
    expect(new Set(clases).size).toBe(3)
  })

  it('traduce la ortografia del catalogo a la del sistema de diseno', () => {
    // `en_revision` with an underscore is what the database stores. Without the
    // crossing the state resolves to null and the badge ships with no icon and
    // no colour, which reads as a decision instead of as a bug.
    const estado = certificacionDeCampo('en_revision')

    expect(estado?.codigo).toBe('en-revision')
    expect(estado?.icono).toBe('lucide:clock')
  })

  it('cada valor que el catalogo admite tiene estado en el sistema', () => {
    // The contract between the two vocabularies. A fifth certification value
    // added to the migration and not to `design/sistema.py` would ship a badge
    // with a label and nothing else, on the screen that decides whether a
    // figure may be used.
    for (const codigo of CODIGOS_FACETA.certification) {
      expect(certificacionDeCampo(codigo), codigo).not.toBeNull()
    }
  })

  it('un codigo que el sistema no declara no toma prestada la forma de otro', () => {
    // Borrowing the icon of a known state is exactly the defect being removed,
    // one level down: an unknown state would inherit the meaning of the state
    // whose shape it stole.
    expect(certificacionDeCampo('en_tramite')).toBeNull()
  })
})

describe('la tabla del catalogo pinta los tres estados', () => {
  it('da a cada fila el icono y la clase de su propio estado', () => {
    const wrapper = montar()
    const celdas = wrapper.findAll('[data-certificacion-campo]')

    expect(celdas).toHaveLength(CODIGOS_FACETA.certification.length)

    for (const [indice, codigo] of CODIGOS_FACETA.certification.entries()) {
      const estado = certificacionDeCampo(codigo)!
      const celda = celdas[indice]!

      expect(celda.attributes('data-certificacion')).toBe(codigo)
      expect(celda.get('[data-icono]').attributes('data-icono')).toBe(estado.icono)
      expect(celda.get('span').classes()).toContain(estado.clase)
    }
  })

  it('nombra el estado con palabras y no solo con color', () => {
    // The rule the whole design system is built on: colour never travels alone.
    // Under simulated dichromacy the semantic marks separate by 13.6 in light
    // mode, which is a measured ceiling and not an oversight.
    const wrapper = montar()
    const celdas = wrapper.findAll('[data-certificacion-campo]')

    for (const [indice, codigo] of CODIGOS_FACETA.certification.entries()) {
      expect(celdas[indice]!.text()).toBe(mensaje('es', `catalog.facet.certification.${codigo}`))
    }
  })
})

afterEach(() => {
  vi.unstubAllGlobals()
})

/** Mounts the style guide, which is a page and therefore declares its meta. */
function montarGuia(): VueWrapper {
  vi.stubGlobal('definePageMeta', () => undefined)
  return mount(Guia, {
    global: {
      plugins: [crearI18nDePrueba('es')],
      components: { NuxtLink: EnlaceStub },
      stubs: {
        Icon: { props: ['name'], template: '<i :data-icono="name" />' },
        ClientOnly: { template: '<div><slot /></div>' },
      },
    },
  })
}

describe('la lamina normativa publica lo que el producto usa', () => {
  it('imprime los cuatro tokens del chasis con el valor que el generador emitio', () => {
    // The guide is the normative reference of the system and it did not show a
    // single one of the seven tokens the chassis and the catalogue were built
    // with: a sheet that documents less than the product is a sheet somebody
    // will copy a colour from, and get it wrong.
    const sistema = useSistemaDiseno()
    const wrapper = montarGuia()
    const texto = wrapper.get('[data-lamina="chasis"]').text()

    expect(BARRA_LATERAL).toHaveLength(4)
    for (const token of BARRA_LATERAL) {
      expect(texto, token.nombre).toContain(token.nombre)
      expect(texto, token.nombre).toContain(sistema.valor(token))
    }
  })

  it('imprime los tres estados de certificacion con su icono y su valor', () => {
    const sistema = useSistemaDiseno()
    const wrapper = montarGuia()
    const lamina = wrapper.get('[data-lamina="chasis"]')

    for (const estado of ESTADOS_CERTIFICACION) {
      const fila = lamina.get(`[data-estado-certificacion="${estado.codigo}"]`)
      const token = CERTIFICACION.find(candidato => candidato.nombre === estado.token)!

      expect(fila.get('[data-icono]').attributes('data-icono')).toBe(estado.icono)
      expect(fila.text()).toContain(sistema.valor(token))
    }
  })

  it('muestra la superficie contenida en sus cinco canales', () => {
    // The surface of wave C shipped into four screens without ever appearing in
    // the sheet that is supposed to define it.
    const wrapper = montarGuia()
    const lamina = wrapper.get('[data-lamina="chasis"]')

    const canales = lamina.findAll('[data-canal-superficie]')
      .map(nodo => nodo.attributes('data-canal-superficie'))

    expect(canales).toEqual(['accion', 'aviso', 'ok', 'error', 'neutro'])
    // `neutro` is the absence of a channel: four bars over five cards.
    expect(lamina.findAll('[data-barra-canal]')).toHaveLength(4)
  })
})

describe('la separacion dicromatica de la familia viaja aparte de la paleta', () => {
  /** Distances a list of the accessibility plate prints, in row order. */
  function distancias(wrapper: VueWrapper, marca: string): number[] {
    return wrapper.findAll(`[${marca}]`).map(fila => Number(fila.findAll('span').at(-1)!.text()))
  }

  it('imprime las tres parejas del estado sin fundirlas con las seis semanticas', () => {
    // Merging the two lists would be wrong twice over. It would state a floor
    // between marks that never share a surface -a certification badge against
    // the warning colour of a form- and it would move the worst pair of the
    // palette, which is the figure the graded report prints as the floor of
    // the whole system. The store keeps the families apart; this is the plate
    // proving that it does, on the sheet where the number is published.
    const wrapper = montarGuia()
    const nombresDeEstado = new Set(CERTIFICACION.map(token => token.nombre))

    const semanticas = wrapper.findAll('[data-separacion]')
    const deEstado = wrapper.findAll('[data-separacion-certificacion]')

    // Six over four marks, three over three states.
    expect(semanticas).toHaveLength(6)
    expect(deEstado).toHaveLength(3)
    for (const fila of deEstado) {
      const [uno, otro] = fila.findAll('span')[0]!.text().split(' · ')
      expect(nombresDeEstado.has(uno!) && nombresDeEstado.has(otro!), fila.text()).toBe(true)
    }
    for (const fila of semanticas) {
      expect([...nombresDeEstado].some(nombre => fila.text().includes(nombre)), fila.text())
        .toBe(false)
    }
  })

  it('publica las distancias de la combinacion en pantalla y no las del otro modo', async () => {
    // The store filters that table by theme AND mode. Drop either condition and
    // the plate lists the twelve rows of every combination, or prints the light
    // numbers while the page is dark: a figure without provenance, on the one
    // sheet whose whole job is to show where a figure comes from.
    const sistema = useSistemaDiseno()
    const wrapper = montarGuia()
    const esperadas = (modo: 'claro' | 'oscuro'): number[] =>
      SEPARACIONES_CERTIFICACION_POR_TEMA
        .filter(s => s.tema === sistema.tema && s.modo === modo)
        .map(s => s.distancia)

    expect(distancias(wrapper, 'data-separacion-certificacion')).toEqual(esperadas('claro'))

    sistema.elegir('oscuro')
    await nextTick()

    expect(distancias(wrapper, 'data-separacion-certificacion')).toEqual(esperadas('oscuro'))
    expect(esperadas('oscuro')).not.toEqual(esperadas('claro'))
  })
})
