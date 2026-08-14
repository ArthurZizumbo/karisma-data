import type { VueWrapper } from '@vue/test-utils'

import { flushPromises, mount } from '@vue/test-utils'
import { afterEach, describe, expect, it, vi } from 'vitest'

import AdministracionDialogoConfirmacion from '~/components/administracion/DialogoConfirmacion.vue'
import { crearI18nDePrueba, mensaje } from './i18nDePrueba'

/**
 * US-018 — the confirmation dialog, and only what is really its own.
 *
 * `happy-dom@20.11.2` implements `showModal()` as `setAttribute('open', '')`
 * and nothing else: no focus trap, no top layer, no `cancel` event of its own,
 * and no layout either. So the three handlers this component writes are
 * measured here -the cancel button, the `cancel` event, and the click that
 * lands on the backdrop, with the box of the card stated below because nothing
 * here can compute one- and the three behaviours the platform provides are
 * measured in `docs/manual-test/us-018.md` against a real browser. A test that
 * pressed `Esc` here would pass while saying something that is not true.
 *
 * What is verifiable here and matters: the dialog does not close itself. The
 * parent owns `abierto`, and a component that closed on its own would leave the
 * screen believing a question is still on screen after it is gone.
 */

const PROPIEDADES = {
  abierto: true,
  titulo: 'Titulo de prueba',
  cuerpo: 'Cuerpo de prueba',
  etiquetaConfirmar: 'Confirmar',
  tono: 'normal' as const,
}

let montado: VueWrapper | null = null

function montar(propiedades: Partial<typeof PROPIEDADES> = {}) {
  const wrapper = mount(AdministracionDialogoConfirmacion, {
    // Attached to the document: `focus()` only moves `activeElement` for a node
    // that is in it, and where focus lands is one of the assertions.
    attachTo: document.body,
    props: { ...PROPIEDADES, ...propiedades },
    global: { plugins: [crearI18nDePrueba()], stubs: { Icon: true } },
  })
  montado = wrapper
  return wrapper
}

/** The `<dialog>` element itself, which is the root of the component. */
function elemento(wrapper: VueWrapper): HTMLDialogElement {
  return wrapper.get('[data-dialogo-confirmacion]').element as HTMLDialogElement
}

/**
 * The box the browser would measure, stated because happy-dom has no layout.
 *
 * Without layout every rect is zero, and a component that reads the box would
 * be measured against a point that is always inside it. So the box is fixed
 * here and what gets measured is the component's comparison, which is where the
 * defect lives. Coordinates are in the viewport, like the ones a click carries.
 */
const CAJA = Object.freeze({ left: 100, top: 80, right: 484, bottom: 320 })

/**
 * Gives the dialog the box above.
 *
 * @param elemento - The dialog under test.
 */
function medir(elemento: HTMLDialogElement): void {
  vi.spyOn(elemento, 'getBoundingClientRect').mockReturnValue({
    ...CAJA,
    x: CAJA.left,
    y: CAJA.top,
    width: CAJA.right - CAJA.left,
    height: CAJA.bottom - CAJA.top,
    toJSON: () => ({ ...CAJA }),
  } as DOMRect)
}

afterEach(() => {
  montado?.unmount()
  montado = null
  document.body.innerHTML = ''
  vi.restoreAllMocks()
})

describe('el diálogo se abre y se cierra desde su propiedad, nunca por su cuenta', () => {
  it('abre el elemento nativo cuando la pantalla lo pide', () => {
    expect(elemento(montar()).open).toBe(true)
  })

  it('no abre nada mientras la pantalla no lo pida', () => {
    const wrapper = montar({ abierto: false })

    expect(elemento(wrapper).open).toBe(false)
    expect(wrapper.emitted()).toEqual({})
  })

  it('cierra el elemento cuando la pantalla baja la propiedad', async () => {
    const wrapper = montar()

    await wrapper.setProps({ abierto: false })

    expect(elemento(wrapper).open).toBe(false)
  })
})

describe('las tres maneras de salir sin confirmar', () => {
  it('el botón de cancelar avisa y deja el cierre a la pantalla', async () => {
    const wrapper = montar()

    await wrapper.get('[data-accion="cancelar"]').trigger('click')

    expect(wrapper.emitted('cancelar')).toHaveLength(1)
    expect(wrapper.emitted('confirmar')).toBeUndefined()
    // Still open: whoever owns the state closes it, and until then the screen
    // and the DOM say the same thing.
    expect(elemento(wrapper).open).toBe(true)
  })

  it('el evento cancel, que es lo que produce Esc, avisa igual', async () => {
    const wrapper = montar()

    await wrapper.get('[data-dialogo-confirmacion]').trigger('cancel')

    expect(wrapper.emitted('cancelar')).toHaveLength(1)
    expect(wrapper.emitted('confirmar')).toBeUndefined()
  })

  it('un clic en el telón cierra', async () => {
    const wrapper = montar()
    medir(elemento(wrapper))

    // There is no node for `::backdrop`, so a click outside the card reports
    // the dialog itself as its target and lands beyond its box.
    await wrapper.get('[data-dialogo-confirmacion]').trigger('click', {
      clientX: CAJA.left - 20,
      clientY: CAJA.top - 20,
    })

    expect(wrapper.emitted('cancelar')).toHaveLength(1)
  })

  it('un clic en el relleno del diálogo no cierra, aunque el target sea el diálogo', async () => {
    // The 24 px of padding are visible box belonging to the dialog and to no
    // child, so a click on the inner edge of the card reports the dialog as its
    // target just like the backdrop does. Deciding on the target alone takes it
    // for a click outside and throws away the destructive action the reader was
    // one press away from confirming.
    const wrapper = montar()
    const dialogo = elemento(wrapper)
    medir(dialogo)

    await wrapper.get('[data-dialogo-confirmacion]').trigger('click', {
      clientX: CAJA.left + 8,
      clientY: CAJA.top + 8,
    })

    expect(wrapper.emitted('cancelar')).toBeUndefined()
    expect(dialogo.open).toBe(true)
  })

  it('un clic sobre el contenido no cierra ni cuando no trae coordenadas', async () => {
    // A control activated with the keyboard produces a click at (0, 0) that
    // bubbles up to this handler, and (0, 0) is outside every box that is not
    // in the corner of the viewport. Deciding on the geometry alone would read
    // that as a click on the backdrop and cancel what the reader just chose.
    const wrapper = montar()
    medir(elemento(wrapper))

    await wrapper.get('h2').trigger('click')

    expect(wrapper.emitted('cancelar')).toBeUndefined()
  })
})

describe('confirmar es lo único que ejecuta', () => {
  it('emite confirmar una sola vez y no lo mezcla con cancelar', async () => {
    const wrapper = montar()

    await wrapper.get('[data-accion="confirmar"]').trigger('click')

    expect(wrapper.emitted('confirmar')).toHaveLength(1)
    expect(wrapper.emitted('cancelar')).toBeUndefined()
  })
})

describe('el foco y los dos tonos', () => {
  it('deja el foco en la salida y no sobre la acción irreversible', async () => {
    const wrapper = montar({ tono: 'destructivo' })
    await flushPromises()

    expect(document.activeElement).toBe(wrapper.get('[data-accion="cancelar"]').element)
  })

  it('publica el tono y viste la acción destructiva como la guía la define', () => {
    const wrapper = montar({ tono: 'destructivo' })

    expect(wrapper.get('[data-dialogo-confirmacion]').attributes('data-tono')).toBe('destructivo')
    // The destructive variant of the button plate, not a colour invented here.
    const clases = wrapper.get('[data-accion="confirmar"]').classes()
    expect(clases).toContain('border-error')
    expect(clases).toContain('text-error')
  })

  it('viste la acción normal con la variante llena y sin el rojo', () => {
    const wrapper = montar({ tono: 'normal' })

    expect(wrapper.get('[data-dialogo-confirmacion]').attributes('data-tono')).toBe('normal')
    const clases = wrapper.get('[data-accion="confirmar"]').classes()
    expect(clases).toContain('bg-corriente-pleno')
    expect(clases).not.toContain('text-error')
  })
})

describe('las cadenas del diálogo salen de los catálogos', () => {
  it('rotula la salida en el idioma de la interfaz', () => {
    const wrapper = mount(AdministracionDialogoConfirmacion, {
      props: PROPIEDADES,
      global: { plugins: [crearI18nDePrueba('en')], stubs: { Icon: true } },
    })
    montado = wrapper

    expect(wrapper.get('[data-accion="cancelar"]').text()).toBe(
      mensaje('en', 'admin.users.confirm.cancel'),
    )
  })
})
