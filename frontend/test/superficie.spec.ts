import type { Ref } from 'vue'
import type { Modo } from '~/composables/useModo'

import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

import { mount } from '@vue/test-utils'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { defineComponent, isRef, nextTick, ref } from 'vue'

import TarjetaContenida from '~/components/comun/TarjetaContenida.vue'
import { useModo } from '~/composables/useModo'
import { useSistemaDiseno } from '~/stores/sistemaDiseno'
import { PEOR_SEPARACION_POR_TEMA, TEMA_OMISION } from '~/utils/tokens.generated'

/**
 * US-ENTREGA-A4 - the two axes of the surface, where they meet the stylesheet.
 *
 * `modoYSistema.spec.ts` already measures the mode against the default theme,
 * and `tema.spec.ts` measures the theme axis on its own. What neither of them
 * touches is the seam between the two, and the seam is where this change can
 * fail without looking broken: the mode attribute was renamed from `data-theme`
 * to `data-modo`, and every token now resolves through a pair of coordinates
 * instead of one.
 *
 * Nothing here asserts what a colour is. The expected values come from the
 * generated module -the same one the emitter writes and the report reproduces-
 * and what is measured is that the composable and the store agree with the
 * sheet the browser will actually apply.
 */

/** The generated stylesheet, which is the other half of every contract below. */
const CSS = readFileSync(resolve(process.cwd(), 'app/assets/css/main.css'), 'utf8')

/**
 * Attribute the generated sheet keys an explicit mode on.
 *
 * Read from the sheet and never typed, because the whole point of these
 * assertions is that the composable and the sheet spell it the same way: a
 * literal here would be a third copy of the name and would agree with whichever
 * of the two it was last synchronised against.
 */
const ATRIBUTO_MODO = /:root\[([a-z-]+)="oscuro"\]\s*\{/.exec(CSS)?.[1]

/**
 * Attribute the generated sheet keys the optional theme on.
 *
 * Read from the sheet for the same reason as the one above: the contained
 * surface conditions its radius on this attribute through a Tailwind variant,
 * and a component spelling it the other way would compile to a rule that never
 * matches -a card that stays square under the institutional theme, with
 * nothing broken to look at.
 */
const ATRIBUTO_TEMA = /:root\[([a-z-]+)="institucional"\]\s*\{/.exec(CSS)?.[1]

/** Cookies of the current test, addressed by name as `useCookie` does. */
let galletas: Map<string, Ref<unknown>>

/** Every entry declared through `useHead` while the test ran. */
let entradas: Record<string, unknown>[]

beforeEach(() => {
  galletas = new Map<string, Ref<unknown>>()
  entradas = []

  vi.stubGlobal('useCookie', (nombre: string, opciones?: { default?: () => unknown }) => {
    if (!galletas.has(nombre)) {
      galletas.set(nombre, ref(opciones?.default?.() ?? null))
    }
    return galletas.get(nombre)!
  })
  vi.stubGlobal('useHead', (entrada: Record<string, unknown>) => {
    entradas.push(entrada)
  })
})

afterEach(() => {
  vi.unstubAllGlobals()
})

/** Attributes the root element would carry right now, computeds resolved. */
function atributosDelHead(): Record<string, unknown> {
  const salida: Record<string, unknown> = {}
  for (const entrada of entradas) {
    const atributos = entrada.htmlAttrs as Record<string, unknown> | undefined
    if (atributos === undefined) {
      continue
    }
    for (const [clave, valor] of Object.entries(atributos)) {
      salida[clave] = isRef(valor) ? valor.value : valor
    }
  }
  return salida
}

/** Mounts a component whose setup does nothing but read and write the mode. */
function montarModo(preferencia: Modo = 'claro') {
  let control: ReturnType<typeof useModo> | undefined
  const Lector = defineComponent({
    setup() {
      control = useModo(ref(preferencia))
      return () => null
    },
  })
  mount(Lector)
  return control!
}

describe('el modo explicito viaja en el atributo que la hoja generada selecciona', () => {
  it('escribe la eleccion en data-modo y no en el nombre que el modo tenia antes', () => {
    // The defect this closes is the most expensive one of the rename, because
    // it is the quiet half: `data-theme` put back in the composable leaves the
    // media query of the sheet working, so a reader whose operating system is
    // dark still sees dark and nothing looks broken. What stops applying is the
    // explicit choice, and only for whoever forces it against their system.
    const { elegir } = montarModo()

    elegir('oscuro')

    expect(Object.keys(atributosDelHead())).toEqual([ATRIBUTO_MODO])
    expect(atributosDelHead()[ATRIBUTO_MODO!]).toBe('oscuro')
  })

  it('no escribe atributo alguno mientras el modo lo decide el sistema', () => {
    // The sheet excludes only an explicit light choice from its media query, so
    // an attribute written for "follow the system" pins the mode: the reader
    // would stay in light for good, and the day their operating system flipped
    // to dark the portal would be the one thing on the screen that did not.
    const { elegir } = montarModo()

    elegir('sistema')

    expect(Object.keys(atributosDelHead())).toEqual([ATRIBUTO_MODO])
    expect(atributosDelHead()[ATRIBUTO_MODO!]).toBeUndefined()
  })

  it('deletrea el claro forzado igual que la exclusion de la consulta de medios', () => {
    // The defect: the composable writes one spelling and the sheet excludes
    // another. A reader on a dark operating system who asks for light would get
    // the media query applied on top of their choice and see dark anyway, which
    // is the one case an explicit control exists for.
    const { elegir } = montarModo('oscuro')

    elegir('claro')

    expect(atributosDelHead()[ATRIBUTO_MODO!]).toBe('claro')
    expect(CSS).toContain(`:not([${ATRIBUTO_MODO}="claro"])`)
  })
})

describe('el store resuelve cada token contra el tema y el modo a la vez', () => {
  it('devuelve el valor del tema puesto y no el del tema de omision', async () => {
    // The defect: `valor()` goes back to reading the flat `claro`/`oscuro`
    // fields, which are the default theme's by definition. The guide would keep
    // printing the default palette while the page painted the institutional
    // one, so the swatch and the surface right beside it would disagree -and
    // the swatch is precisely what the report reproduces as evidence.
    const sistema = useSistemaDiseno()
    const suelo = sistema.porNombre('ground')

    sistema.fijarTema('institucional')
    await nextTick()

    expect(sistema.valor(suelo)).toBe(suelo.temas.institucional.claro)
    expect(sistema.valor(suelo)).not.toBe(suelo.claro)

    sistema.elegir('oscuro')
    await nextTick()

    expect(sistema.valor(suelo)).toBe(suelo.temas.institucional.oscuro)
    expect(sistema.valor(suelo)).not.toBe(suelo.oscuro)
  })

  it('vuelve al valor del tema de omision cuando el lector lo repone', async () => {
    // The mirror of the case above: a theme that cannot be left is a theme the
    // reader cannot compare against the evidence already delivered, which was
    // captured on the default one.
    const sistema = useSistemaDiseno()
    const suelo = sistema.porNombre('ground')

    sistema.fijarTema('institucional')
    await nextTick()
    sistema.fijarTema(TEMA_OMISION)
    await nextTick()

    expect(sistema.valor(suelo)).toBe(suelo.temas[TEMA_OMISION].claro)
  })

  it('publica la matriz de contraste del tema en pantalla y no la del otro', async () => {
    // The defect: the filter keeps the mode and drops the theme. The ground is
    // not the same in the two themes, so a ratio measured over one says nothing
    // about the other; with the theme condition gone the guide would publish
    // every token twice, each with the number of a surface the reader is not
    // looking at.
    const sistema = useSistemaDiseno()
    const enOmision = sistema.contrastes.map(par => par.ratio)

    sistema.fijarTema('institucional')
    await nextTick()

    expect(sistema.contrastes.every(par => par.tema === 'institucional')).toBe(true)
    expect(sistema.contrastes).toHaveLength(enOmision.length)
    expect(sistema.contrastes.map(par => par.ratio)).not.toEqual(enOmision)
  })

  it('lleva la peor separacion del tema puesto, que no es la del otro', async () => {
    // This is the number the report prints as the floor of the whole palette.
    // Read from the default theme while the institutional one is on screen it
    // would state 13.6 where the measurement says 14.5: a figure without its
    // own provenance, which is the single thing this product promises it never
    // publishes.
    const sistema = useSistemaDiseno()
    const enOmision = sistema.peorSeparacion

    sistema.fijarTema('institucional')
    await nextTick()

    expect(sistema.peorSeparacion).toBe(PEOR_SEPARACION_POR_TEMA.institucional.claro)
    expect(sistema.peorSeparacion).not.toBe(enOmision)
  })
})

describe('la superficie contenida lleva filete, radio del tema y barra de canal', () => {
  /** Class list of a card, which is where all three decisions are written. */
  function clasesDeTarjeta(canal?: string): string[] {
    return mount(TarjetaContenida, { props: canal === undefined ? {} : { canal } })
      .get('[data-tarjeta]')
      .classes()
  }

  it('separa con un filete de un pelo y no con una sombra', () => {
    // The portal is dense. A shadow under every card turns a screen of figures
    // into a screen of floating boxes, and the guide answers the question with
    // one pixel of the grid colour.
    const clases = clasesDeTarjeta()

    expect(clases).toContain('border')
    expect(clases).toContain('border-grid')
    expect(clases.some(clase => clase.startsWith('shadow'))).toBe(false)
  })

  it('condiciona el radio al atributo de tema que la hoja generada selecciona', () => {
    // The defect is silent in both directions. Spelled with the name the mode
    // used to have, the rule never matches and the institutional theme keeps
    // square cards; written without a condition, the default theme grows a
    // radius it never had and the fifteen delivered screenshots stop
    // describing the product.
    const clases = clasesDeTarjeta()
    const conRadio = clases.filter(clase => clase.includes('rounded'))

    expect(ATRIBUTO_TEMA).toBeTruthy()
    expect(conRadio).toHaveLength(1)
    expect(conRadio[0]).toContain(`[${ATRIBUTO_TEMA}=institucional]`)
    expect(conRadio[0]?.startsWith('rounded')).toBe(false)
  })

  it('pinta la barra solo cuando la tarjeta declara un canal', () => {
    // A stripe on every card is a stripe that means nothing, and the reader
    // stops looking at it exactly when one of them starts meaning something.
    const neutra = mount(TarjetaContenida, { props: { canal: 'neutro' } })
    const conCanal = mount(TarjetaContenida, { props: { canal: 'error' } })

    expect(neutra.find('[data-barra-canal]').exists()).toBe(false)
    expect(conCanal.get('[data-barra-canal]').classes()).toContain('bg-error')
    expect(conCanal.get('[data-barra-canal]').attributes('aria-hidden')).toBe('true')
  })

  it('reserva sitio para la barra en lugar de dibujarla encima del contenido', () => {
    // Absolutely positioned over the padding, the bar would sit on the first
    // letter of the heading at every card that carries one.
    expect(clasesDeTarjeta('accion')).toContain('pl-5')
    expect(clasesDeTarjeta('neutro')).toContain('p-4')
  })

  it('rotula la tarjeta con su propio titulo cuando lo lleva', () => {
    // Four cards side by side with no accessible name are four regions called
    // "article", and the reader cycling through them cannot tell which figure
    // they landed on.
    const wrapper = mount(TarjetaContenida, { props: { titulo: 'Cobertura de liquidez' } })
    const rotulo = wrapper.get('[data-tarjeta]').attributes('aria-labelledby')

    expect(rotulo).toBeTruthy()
    expect(wrapper.get('h3').attributes('id')).toBe(rotulo)
  })
})

describe('el chasis es dueno de los dos ejes del sistema de diseno', () => {
  /**
   * `app.vue` has to instantiate the design system store itself.
   *
   * The defect, and it shipped: `useModo` registers `data-modo` through
   * `useHead` from inside the store setup, and a head entry belongs to the
   * component instance that was active when it was registered. Left to whoever
   * read the store first, that owner was a control living in a layout. Entering
   * through the demonstration door swaps the `acceso` layout for `portal`, the
   * owner unmounts, the entry is disposed, and the reader who chose dark lands
   * on a light page while the selector still reads dark -until a reload, which
   * is the one action nobody performs to check a preference they just set.
   * Verified in a live browser before this case was written.
   *
   * `useTema` never had the defect because `app.vue` always called it. This
   * reads the source rather than mounting `app.vue`, which needs the Nuxt
   * runtime: what has to be true is a property of who registers the entry, and
   * that is decided at the call site.
   */
  it('app.vue instancia el store, y no lo deja al primer lector', () => {
    const chasis = readFileSync(
      resolve(import.meta.dirname, '../app/app.vue'),
      'utf8',
    )

    expect(chasis).toContain('useSistemaDiseno')
    expect(chasis).toContain('useTema()')

    // Both axes registered before the language is awaited: after the await the
    // Nuxt context is gone and `useHead` would land nowhere.
    const posicionStore = chasis.indexOf('useSistemaDiseno()')
    const posicionEspera = chasis.indexOf('await restaurarIdiomaGuardado()')
    expect(posicionStore).toBeGreaterThan(-1)
    expect(posicionEspera).toBeGreaterThan(posicionStore)
  })
})
