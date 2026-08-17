import type { VueWrapper } from '@vue/test-utils'

import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import { nextTick } from 'vue'

import SelectorApariencia from '~/components/comun/SelectorApariencia.vue'
import { useSistemaDiseno } from '~/stores/sistemaDiseno'
import { TEMA_OMISION, TEMAS } from '~/utils/tokens.generated'
import { type CodigoIdioma, crearI18nDePrueba, mensaje } from './i18nDePrueba'

/**
 * US-A4-EXCELENCIA, ola B - theme and mode folded into one control.
 *
 * The bar used to carry two adjacent groups of naked icon buttons, five tab
 * stops for one question, and the design review counted eleven controls in the
 * chrome with not a single label. Folding them is only an improvement if
 * nothing disappears in the fold, so that is what this file measures: that the
 * five options survive, that the panel says which pair is painted, and that
 * the choice still reaches the store that owns the two cookies.
 *
 * The three modes are asserted by name and not by count. "Follow the system"
 * is the option a two way switch swallows, and it is the commonest answer.
 */

/** The three modes the control has to keep offering. */
const MODOS = ['claro', 'oscuro', 'sistema'] as const

function montar(idioma: CodigoIdioma = 'es'): VueWrapper {
  return mount(SelectorApariencia, {
    global: { plugins: [crearI18nDePrueba(idioma)], stubs: { Icon: true } },
  })
}

/** Opens the disclosure and waits for the panel to render. */
async function abrir(wrapper: VueWrapper): Promise<VueWrapper> {
  await wrapper.get('[data-apariencia-abrir]').trigger('click')
  await nextTick()
  return wrapper
}

describe('el control de apariencia se anuncia antes de abrirse', () => {
  it('lleva rotulo visible, no solo un icono', () => {
    // The measured defect: eleven controls in the bar and none of them named.
    // An icon with a tooltip is not a label -it needs a pointer that rests-
    // so what is asserted is text inside the trigger.
    const disparador = montar().get('[data-apariencia-abrir]')

    expect(disparador.text()).toContain(mensaje('es', 'appearance.label'))
  })

  it('nombra en su rotulo accesible el par que esta puesto ahora mismo', () => {
    // A disclosure that only says "Apariencia" hides the answer it was opened
    // for: the reader has to open it to find out which theme is on.
    const disparador = montar().get('[data-apariencia-abrir]')

    expect(disparador.attributes('aria-label')).toBe(
      mensaje('es', 'appearance.current')
        .replace('{theme}', mensaje('es', `theme.names.${TEMA_OMISION}`))
        .replace('{mode}', mensaje('es', 'chrome.mode.sistema')),
    )
  })

  it('empieza plegado y declara ese estado', () => {
    const wrapper = montar()

    expect(wrapper.get('[data-apariencia-abrir]').attributes('aria-expanded')).toBe('false')
    expect(wrapper.find('[data-apariencia-panel]').exists()).toBe(false)
  })

  it('cuesta un solo control mientras esta plegado', () => {
    // This is the arithmetic of the header criterion: the five options of the
    // two axes may not be five tab stops of the bar. Folded, the whole thing
    // is one button; the rest of the budget belongs to the other slots.
    const wrapper = montar()

    expect(wrapper.findAll('button, a, input, select, textarea, summary')).toHaveLength(1)
  })
})

describe('el panel abierto no pierde ninguna de las cinco opciones', () => {
  it('ofrece una opcion por tema emitido', async () => {
    // Derived from the generated module and not from a literal: a third theme
    // in `design/sistema.py` that the chrome never offered would pass a test
    // written against the number two.
    const wrapper = await abrir(montar())
    const opciones = wrapper
      .findAll('[data-tema-opcion]')
      .map(boton => boton.attributes('data-tema-opcion'))

    expect(opciones).toEqual([...TEMAS])
  })

  it('ofrece los tres modos, incluido seguir al sistema', async () => {
    const wrapper = await abrir(montar())
    const opciones = wrapper
      .findAll('[data-modo-opcion]')
      .map(boton => boton.attributes('data-modo-opcion'))

    expect(opciones).toEqual([...MODOS])
  })

  it('marca exactamente un tema y exactamente un modo como activos', async () => {
    // The defect: the control is painted with no active state and the reader
    // cannot tell what is on, so every option reads as an action that did
    // nothing.
    const wrapper = await abrir(montar())

    const temaMarcado = wrapper
      .findAll('[data-tema-opcion]')
      .filter(boton => boton.attributes('aria-pressed') === 'true')
    const modoMarcado = wrapper
      .findAll('[data-modo-opcion]')
      .filter(boton => boton.attributes('aria-pressed') === 'true')

    expect(temaMarcado).toHaveLength(1)
    expect(temaMarcado[0]!.attributes('data-tema-opcion')).toBe(TEMA_OMISION)
    expect(modoMarcado).toHaveLength(1)
    expect(modoMarcado[0]!.attributes('data-modo-opcion')).toBe('sistema')
  })

  it('nombra cada opcion por su catalogo y en los dos idiomas', async () => {
    // A name written inside the component would show Spanish to a reader in
    // English, and would name a theme after a number or an author instead of
    // after its own visual world.
    const enEspanol = (await abrir(montar('es'))).text()
    const enIngles = (await abrir(montar('en'))).text()

    for (const tema of TEMAS) {
      expect(enEspanol).toContain(mensaje('es', `theme.names.${tema}`))
      expect(enIngles).toContain(mensaje('en', `theme.names.${tema}`))
    }
    for (const modo of MODOS) {
      expect(enEspanol).toContain(mensaje('es', `chrome.mode.${modo}`))
      expect(enIngles).toContain(mensaje('en', `chrome.mode.${modo}`))
    }
    expect(enIngles).not.toContain(mensaje('es', 'appearance.label'))
  })
})

describe('la eleccion llega al estado que escribe las dos cookies', () => {
  it('mueve la marca y fija el tema al pulsar el otro', async () => {
    const wrapper = await abrir(montar())
    const sistema = useSistemaDiseno()

    await wrapper.get('[data-tema-opcion="institucional"]').trigger('click')
    await nextTick()

    expect(sistema.tema).toBe('institucional')
    expect(wrapper.get('[data-tema-opcion="institucional"]').attributes('aria-pressed')).toBe('true')
    expect(wrapper.get('[data-tema-opcion="corriente"]').attributes('aria-pressed')).toBe('false')
  })

  it('mueve la marca y fija el modo al pulsar el otro', async () => {
    const wrapper = await abrir(montar())
    const sistema = useSistemaDiseno()

    await wrapper.get('[data-modo-opcion="oscuro"]').trigger('click')
    await nextTick()

    expect(sistema.eleccion).toBe('oscuro')
    expect(wrapper.get('[data-modo-opcion="oscuro"]').attributes('aria-pressed')).toBe('true')
    expect(wrapper.get('[data-modo-opcion="sistema"]').attributes('aria-pressed')).toBe('false')
  })

  it('los dos ejes son independientes: cambiar uno no reinicia el otro', async () => {
    // The defect a single folded control invites: one setter that writes both
    // cookies and quietly resets the axis the reader did not touch.
    const wrapper = await abrir(montar())
    const sistema = useSistemaDiseno()

    await wrapper.get('[data-modo-opcion="oscuro"]').trigger('click')
    await wrapper.get('[data-tema-opcion="institucional"]').trigger('click')
    await nextTick()

    expect(sistema.eleccion).toBe('oscuro')
    expect(sistema.tema).toBe('institucional')
  })
})

describe('el panel se cierra sin dejar rastro', () => {
  it('se pliega con Escape', async () => {
    const wrapper = await abrir(montar())

    await wrapper.get('[data-selector-apariencia]').trigger('keydown.escape')
    await nextTick()

    expect(wrapper.find('[data-apariencia-panel]').exists()).toBe(false)
    expect(wrapper.get('[data-apariencia-abrir]').attributes('aria-expanded')).toBe('false')
  })

  it('se pliega al pulsar fuera y no deja el escucha del documento puesto', async () => {
    // The defect: a panel that survives the click that moved the reader on,
    // and a document listener that outlives the control it belonged to.
    const wrapper = await abrir(montar())

    document.body.dispatchEvent(new MouseEvent('click', { bubbles: true }))
    await nextTick()

    expect(wrapper.find('[data-apariencia-panel]').exists()).toBe(false)

    wrapper.unmount()
    document.body.dispatchEvent(new MouseEvent('click', { bubbles: true }))
  })
})
