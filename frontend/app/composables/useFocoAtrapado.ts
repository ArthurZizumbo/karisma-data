import type { Ref } from 'vue'
import { onBeforeUnmount, nextTick, watch } from 'vue'
import { enfocables, siguienteEnfocable } from '~/utils/foco'

/**
 * Modal focus management for an overlay: trap, Esc, click outside and return.
 *
 * The element is a native `<dialog>` opened with `showModal()`, which is the
 * shared primitive of the two overlays this sprint ships. On top of it this
 * composable adds an explicit cycle, and that is not redundancy: in the browser
 * the handler calls `preventDefault()`, so it SUBSTITUTES the default move
 * instead of adding to it; and under happy-dom -where `showModal()` is
 * implemented as `setAttribute('open', '')`- it IS the behaviour, which is what
 * makes the four central acceptance criteria verifiable against production
 * code rather than against the test environment.
 */

/** A `<dialog>`, recognised by its behaviour rather than by its constructor. */
interface ElementoDialogo extends HTMLElement {
  open: boolean
  showModal: () => void
  close: () => void
}

/**
 * Reads a node as a dialog when it answers to the dialog API.
 *
 * Duck typing and not `instanceof`: the signature of this composable takes an
 * `HTMLElement` so the panel can stay a plain element in a future consumer, and
 * `HTMLDialogElement` is not the same constructor in every environment the
 * suite runs in.
 */
function comoDialogo(nodo: HTMLElement | null): ElementoDialogo | null {
  const candidato = nodo as ElementoDialogo | null
  return candidato !== null && typeof candidato.showModal === 'function' ? candidato : null
}

export interface OpcionesFoco {
  /** Whether the overlay is open. Drives listener registration. */
  abierto: Ref<boolean>
  /** The dialog element. Focus never leaves its subtree while open. */
  panel: Ref<HTMLElement | null>
  /** Heading that receives focus on open. Must carry tabindex="-1". */
  titulo: Ref<HTMLElement | null>
  /** Called on Esc, on the cancel event and on a click over the scrim. */
  alCerrar: () => void
  /** Fallback focus target when the trigger left the document. */
  respaldo?: Ref<HTMLElement | null>
}

/**
 * Installs the focus cycle of an overlay.
 *
 * Keydown is captured on `document` in the capture phase on purpose: by the
 * bubbling phase the browser has already decided where focus goes, and the trap
 * would arrive one node late on every Tab.
 *
 * Listeners are removed both when `abierto` turns false and in
 * `onBeforeUnmount`. A panel unmounted while open -the back button does exactly
 * that- would otherwise leave a global handler swallowing Tab application wide.
 *
 * @param opciones - The overlay state and the nodes the cycle works on.
 */
export function useFocoAtrapado(opciones: OpcionesFoco): void {
  /** Node that had focus when the overlay opened. The return address. */
  let disparador: HTMLElement | null = null
  let escuchando = false

  function alPulsar(evento: KeyboardEvent): void {
    if (!opciones.abierto.value) {
      return
    }

    if (evento.key === 'Escape') {
      // The browser also emits `cancel`; both paths call the same close and
      // closing twice is idempotent. This one is what makes the rule testable.
      evento.preventDefault()
      opciones.alCerrar()
      return
    }

    if (evento.key !== 'Tab') {
      return
    }

    const panel = opciones.panel.value
    if (panel === null) {
      return
    }

    // Recomputed on every keystroke: the panel swaps its content between
    // loading, ready and error, and a cached list would point at a node that
    // already left the document.
    const destino = siguienteEnfocable(enfocables(panel), document.activeElement, evento.shiftKey)
    evento.preventDefault()
    destino?.focus()
  }

  function alClic(evento: MouseEvent): void {
    // A click whose target is the dialog itself landed on the scrim: the
    // content lives in a child, so a click inside never has that target. The
    // listener sits on the element and not on `document`, which is what stops
    // the panel from closing when a text selection started inside ends outside.
    if (evento.target === opciones.panel.value) {
      opciones.alCerrar()
    }
  }

  function alCancelar(evento: Event): void {
    evento.preventDefault()
    opciones.alCerrar()
  }

  function escuchar(panel: HTMLElement): void {
    if (escuchando) {
      return
    }
    document.addEventListener('keydown', alPulsar, true)
    panel.addEventListener('click', alClic)
    panel.addEventListener('cancel', alCancelar)
    escuchando = true
  }

  function retirar(): void {
    if (!escuchando) {
      return
    }
    document.removeEventListener('keydown', alPulsar, true)
    opciones.panel.value?.removeEventListener('click', alClic)
    opciones.panel.value?.removeEventListener('cancel', alCancelar)
    escuchando = false
  }

  /** Returns focus to the trigger, or to the fallback when it is gone. */
  function devolverFoco(): void {
    const vivo = disparador !== null && document.contains(disparador)
    const destino = vivo ? disparador : (opciones.respaldo?.value ?? null)
    disparador = null
    // Never `document.body`: that drops the keyboard reader at the top of the
    // page and makes them walk the whole sidebar again.
    destino?.focus()
  }

  watch(
    opciones.abierto,
    async (abierto, anterior) => {
      if (abierto) {
        disparador = document.activeElement as HTMLElement | null
        await nextTick()
        const panel = opciones.panel.value
        if (panel === null) {
          return
        }
        const dialogo = comoDialogo(panel)
        if (dialogo !== null && !dialogo.open) {
          dialogo.showModal()
        }
        escuchar(panel)
        // The heading and not the first control: a screen reader announces the
        // name of the dialog, and the first Tab lands on the first real control.
        opciones.titulo.value?.focus()
        return
      }

      retirar()
      comoDialogo(opciones.panel.value)?.close()
      if (anterior === true) {
        devolverFoco()
      }
    },
    { immediate: true },
  )

  onBeforeUnmount(() => {
    retirar()
  })
}
