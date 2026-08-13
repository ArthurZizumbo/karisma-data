import type { VueWrapper } from '@vue/test-utils'

import { mount } from '@vue/test-utils'
import { defineComponent, nextTick, ref } from 'vue'
import { afterEach, describe, expect, it, vi } from 'vitest'

import PanelLinaje from '~/components/gobierno/PanelLinaje.vue'

/**
 * US-029 — the focus cycle of the overlay, which is the criterion itself.
 *
 * What is measured here is production code and not the platform:
 * `happy-dom@20.11.2` implements `showModal()` as `setAttribute('open', '')`,
 * so it traps nothing, answers no key and emits no `cancel`. Every assertion
 * below therefore fails when `useFocoAtrapado` is wrong and passes only when it
 * is right, which is the opposite of a test that measures the environment.
 *
 * `attachTo: document.body` is mandatory: in happy-dom a node outside the
 * document does not receive focus, and every assertion here is about focus.
 */

/** Trigger plus panel, which is the only shape in which focus can be returned. */
const Anfitrion = defineComponent({
  components: { PanelLinaje },
  setup() {
    const abierto = ref(false)
    return { abierto }
  },
  template: `
    <div>
      <button data-disparador type="button" @click="abierto = true">Ver el linaje</button>
      <PanelLinaje
        :abierto="abierto"
        titulo="Linaje de saldo_disponible"
        etiqueta-cerrar="Cerrar"
        @cerrar="abierto = false"
      >
        <button data-uno type="button">uno</button>
        <button data-dos type="button">dos</button>
      </PanelLinaje>
    </div>
  `,
})

let montado: VueWrapper | null = null

/** Mounts the host in the document and returns it with its main nodes. */
function montar() {
  const wrapper = mount(Anfitrion, { attachTo: document.body })
  montado = wrapper
  return {
    wrapper,
    disparador: wrapper.get('[data-disparador]').element as HTMLElement,
    dialogo: () => wrapper.get('[data-linaje-overlay]').element as HTMLElement,
  }
}

/** Opens the panel the way a reader does: from the trigger that has focus. */
async function abrir(disparador: HTMLElement, wrapper: VueWrapper) {
  disparador.focus()
  await wrapper.get('[data-disparador]').trigger('click')
  await nextTick()
  await nextTick()
}

/** Sends a key the way the browser does: from the node that holds focus. */
function pulsar(tecla: string, conShift = false): void {
  const objetivo = document.activeElement ?? document
  objetivo.dispatchEvent(
    new KeyboardEvent('keydown', { key: tecla, shiftKey: conShift, bubbles: true, cancelable: true }),
  )
}

/** Classes declared on the dialog element, as a list. */
function clasesDelDialogo(dialogo: HTMLElement): string[] {
  return (dialogo.getAttribute('class') ?? '').split(/\s+/).filter(clase => clase !== '')
}

afterEach(() => {
  montado?.unmount()
  montado = null
  document.body.innerHTML = ''
  vi.restoreAllMocks()
})

describe('apertura del panel', () => {
  it('al abrir el foco entra en el titulo del panel', async () => {
    // Leaving focus on the trigger makes the keyboard reader hunt for a panel
    // they cannot see; the heading is what a screen reader announces.
    const { wrapper, disparador, dialogo } = montar()

    await abrir(disparador, wrapper)

    expect(dialogo().hasAttribute('open')).toBe(true)
    expect(document.activeElement?.tagName).toBe('H2')
    expect(document.activeElement?.getAttribute('tabindex')).toBe('-1')
    expect(dialogo().getAttribute('aria-labelledby')).toBe(document.activeElement?.id)
  })
})

describe('el foco no sale del panel', () => {
  it('Tab desde el ultimo enfocable vuelve al primero', async () => {
    // A handler registered in the bubbling phase arrives one node late: the
    // browser already moved focus and the trap only corrects it afterwards.
    const { wrapper, disparador, dialogo } = montar()
    await abrir(disparador, wrapper)

    const dos = wrapper.get('[data-dos]').element as HTMLElement
    dos.focus()
    pulsar('Tab')

    expect(document.activeElement).toBe(wrapper.get('[data-cerrar-linaje]').element)
    expect(dialogo().contains(document.activeElement)).toBe(true)
  })

  it('Shift+Tab desde el primero lleva al ultimo', async () => {
    // The direction most hand written traps forget, and the one through which
    // focus escapes upwards into the browser chrome.
    const { wrapper, disparador, dialogo } = montar()
    await abrir(disparador, wrapper)

    const cerrar = wrapper.get('[data-cerrar-linaje]').element as HTMLElement
    cerrar.focus()
    pulsar('Tab', true)

    expect(document.activeElement).toBe(wrapper.get('[data-dos]').element)
    expect(dialogo().contains(document.activeElement)).toBe(true)
  })

  it('recorre el ciclo completo sin salirse ni una vez', async () => {
    const { wrapper, disparador, dialogo } = montar()
    await abrir(disparador, wrapper)

    for (let paso = 0; paso < 6; paso += 1) {
      pulsar('Tab')
      expect(dialogo().contains(document.activeElement)).toBe(true)
    }
  })
})

describe('cierre del panel', () => {
  it('Esc cierra y devuelve el foco al disparador', async () => {
    // Closing without returning focus drops the keyboard reader at the top of
    // the document, with the whole sidebar to walk again.
    const { wrapper, disparador } = montar()
    await abrir(disparador, wrapper)

    pulsar('Escape')
    await nextTick()
    await nextTick()

    expect(wrapper.find('[data-linaje-overlay]').attributes('open')).toBeUndefined()
    expect(document.activeElement).toBe(disparador)
  })

  it('el evento cancel cierra, que es lo que emite el navegador', async () => {
    // Attending only the key would leave Esc dead in production, where the
    // platform answers with `cancel` instead of with a keydown.
    const { wrapper, disparador, dialogo } = montar()
    await abrir(disparador, wrapper)

    dialogo().dispatchEvent(new Event('cancel', { cancelable: true }))
    await nextTick()
    await nextTick()

    expect(wrapper.find('[data-linaje-overlay]').attributes('open')).toBeUndefined()
    expect(document.activeElement).toBe(disparador)
  })

  it('un click cuyo target es el dialogo cierra', async () => {
    const { wrapper, disparador, dialogo } = montar()
    await abrir(disparador, wrapper)

    dialogo().dispatchEvent(new MouseEvent('click', { bubbles: true }))
    await nextTick()

    expect(wrapper.find('[data-linaje-overlay]').attributes('open')).toBeUndefined()
  })

  it('un click dentro del contenido no cierra', async () => {
    // The same defect seen from the other side: with a listener on `document`,
    // the previous case passes and this one closes the panel the reader was
    // reading, which is how a text selection started inside dismisses it.
    const { wrapper, disparador } = montar()
    await abrir(disparador, wrapper)

    await wrapper.get('[data-uno]').trigger('click')

    expect(wrapper.get('[data-linaje-overlay]').attributes('open')).toBe('')
  })
})

describe('la pantalla queda como estaba', () => {
  it('no deja estilo, clase ni hijo persistente en el body', async () => {
    // A scroll lock with `document.body.style.overflow` removes the scrollbar
    // on the desktop, reflows everything behind and leaves the screen
    // different from how the reader found it.
    const { wrapper, disparador } = montar()
    const hijosAntes = document.body.childElementCount

    await abrir(disparador, wrapper)

    expect(document.body.getAttribute('style')).toBeNull()
    expect(document.body.className).toBe('')

    pulsar('Escape')
    await nextTick()
    await nextTick()

    expect(document.body.getAttribute('style')).toBeNull()
    expect(document.body.className).toBe('')
    expect(document.body.childElementCount).toBe(hijosAntes)
  })

  it('al desmontar abierto no queda ningun oyente global', async () => {
    // Navigating back with the panel open would otherwise leave a handler
    // capturing Tab across the whole application.
    const alta = vi.spyOn(document, 'addEventListener')
    const baja = vi.spyOn(document, 'removeEventListener')

    const { wrapper, disparador } = montar()
    await abrir(disparador, wrapper)

    const puestos = alta.mock.calls.filter(([tipo]) => tipo === 'keydown').map(([, oyente]) => oyente)
    wrapper.unmount()
    montado = null
    const quitados = baja.mock.calls.filter(([tipo]) => tipo === 'keydown').map(([, oyente]) => oyente)

    expect(puestos).toHaveLength(1)
    expect(quitados).toEqual(puestos)
  })
})

describe('forma y movimiento declarados', () => {
  it('en movil es hoja inferior y en escritorio panel lateral', async () => {
    // An `h-screen` or an `inset-0` turns the sheet into a full screen, which
    // the reader perceives as a navigation and not as a layer.
    const { wrapper, disparador, dialogo } = montar()
    await abrir(disparador, wrapper)

    const clases = clasesDelDialogo(dialogo())

    expect(clases).toEqual(expect.arrayContaining([
      'm-0',
      'mt-auto',
      'w-full',
      'max-w-none',
      'max-h-[80dvh]',
      'rounded-t-lg',
      'overscroll-contain',
      'sm:ml-auto',
      'sm:h-full',
      'sm:w-[28rem]',
      'sm:max-h-none',
    ]))
    expect(clases).not.toContain('h-screen')
    expect(clases).not.toContain('h-full')
    expect(clases).not.toContain('inset-0')
    expect(clases).not.toContain('fixed')
  })

  it('anima los 240 ms de la guia y solo opacidad y transformacion', async () => {
    // The style guide reserves 240 ms for this exact overlay, and forbids
    // animating width, height, top or left because they force a layout
    // recalculation and the panel jumps while it opens.
    const { wrapper, disparador, dialogo } = montar()
    await abrir(disparador, wrapper)

    const clases = clasesDelDialogo(dialogo())
    const transicion = clases.find(clase => clase.includes('transition-['))

    expect(clases).toContain('motion-safe:duration-240')
    expect(clases).toContain('motion-safe:ease-out')
    expect(transicion).toBeDefined()
    expect(transicion).toContain('opacity')
    expect(transicion).toContain('transform')
    expect(transicion).not.toMatch(/width|height|top|left/)
    // Without motion-safe the animation would ignore prefers-reduced-motion.
    expect(clases.filter(clase => clase.startsWith('transition'))).toEqual([])
  })
})
