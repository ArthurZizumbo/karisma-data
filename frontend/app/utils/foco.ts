/**
 * Focus ring of Karisma Data, defined once.
 *
 * The style guide used to carry three different rings: the button plate froze
 * the state in primary-700, the field plate used the primary with a one pixel
 * offset, and the fifteen real controls painted the primary with two. The
 * plates therefore documented -and captured into the A4 document- a ring the
 * prototype never produced, and anyone copying a plate cell into a new control
 * got a fourth one. `uxdoc.sty` declares primary-500 as "anillo de foco", so
 * that is the only colour a ring may use.
 *
 * The dead class names are deliberately not spelled out in this file: Tailwind
 * scans it as plain text and would emit CSS for a ring the system dropped.
 *
 * Every constant below is a LITERAL string. Tailwind reads the sources with a
 * text scanner and never evaluates them: a class assembled at run time out of
 * fragments produces no CSS rule, and the focus ring would simply disappear,
 * which is worse than the three rings this module replaces.
 */

/**
 * The ring, for any control on a light surface.
 *
 * `focus-visible` and not `focus`: a pointer click must not leave a ring
 * behind, or the reader reads it as a selected state.
 */
export const ANILLO_FOCO
  = 'focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-info'

/**
 * The same ring, painted unconditionally.
 *
 * A plate has no pointer and no caret, so the focus cell has to render the ring
 * without the browser pseudo class. It is `ANILLO_FOCO` with the variant
 * dropped and nothing else: the test pins that equality, because a plate that
 * documents a ring the browser does not paint is the defect this module exists
 * to close.
 */
export const ANILLO_FOCO_CONGELADO = 'outline-2 outline-offset-2 outline-info'

/**
 * The ring for controls that live on the dark chrome, such as the sidebar.
 *
 * primary-500 over primary-700 is not visible enough to mark focus, so the
 * inverse ring uses the pale secondary, which the guide measures against the
 * dark background.
 */
export const ANILLO_FOCO_INVERSO
  = 'focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-corriente-apagado'

/**
 * The inverse ring, drawn inwards.
 *
 * A control that fills its container edge to edge -the sort button inside a
 * sticky table header- would have an outward ring clipped by the scroll
 * container, so the offset is negative and the ring lands inside the cell.
 */
export const ANILLO_FOCO_INTERNO
  = 'focus-visible:outline-2 focus-visible:outline-offset-[-2px] focus-visible:outline-ground'

/**
 * Selector of what can receive focus inside an overlay (US-029).
 *
 * The list is short on purpose: it names the controls this product actually
 * renders inside a panel. A longer copy of the canonical browser list would
 * carry branches -`iframe`, `object`, `[contenteditable]`- that no template
 * here produces and that therefore no test could ever exercise.
 *
 * `summary` is in it because the journey renders every hop as a `<details>`,
 * and a trap that skipped the disclosure triangles would leave the reader
 * unable to open a single step with the keyboard.
 */
export const SELECTOR_ENFOCABLE
  = 'a[href], area[href], button, input, select, textarea, summary, [tabindex]'

/**
 * Whether a node found by the selector can really take focus.
 *
 * @param nodo - Candidate node.
 * @returns True when the node is neither disabled, nor hidden, nor removed
 *   from the tab order with a negative `tabindex`.
 */
function esAlcanzable(nodo: HTMLElement): boolean {
  if (nodo.hasAttribute('disabled')) {
    return false
  }
  // Self or ancestor: the panel hides whole blocks, not single controls.
  if (nodo.closest('[hidden]') !== null) {
    return false
  }
  const tabindex = nodo.getAttribute('tabindex')
  // The heading of the panel carries tabindex="-1" so that focus can be moved
  // onto it programmatically; including it in the cycle would trap Tab on the
  // title and the reader would never reach a control.
  return tabindex === null || Number.parseInt(tabindex, 10) >= 0
}

/**
 * Focusable descendants of a container, in document order.
 *
 * Recomputed on every keystroke rather than cached when the overlay opens: the
 * panel swaps its content between loading, ready and error, and a cached list
 * would hand focus to a node that already left the document.
 *
 * @param contenedor - Element whose subtree is searched.
 * @returns The focusable nodes, in the order the document declares them.
 */
export function enfocables(contenedor: HTMLElement): HTMLElement[] {
  return [...contenedor.querySelectorAll<HTMLElement>(SELECTOR_ENFOCABLE)].filter(esAlcanzable)
}

/**
 * Next node of a focus cycle, wrapping at both ends.
 *
 * @param lista - Focusable nodes in document order.
 * @param actual - Node holding focus, or null when focus sits on the container.
 * @param haciaAtras - True for Shift+Tab.
 * @returns The node that must receive focus, or null when the list is empty.
 */
export function siguienteEnfocable(
  lista: readonly HTMLElement[],
  actual: Element | null,
  haciaAtras: boolean,
): HTMLElement | null {
  if (lista.length === 0) {
    return null
  }

  const indice = actual === null ? -1 : lista.indexOf(actual as HTMLElement)
  if (indice === -1) {
    // Focus is on the dialog or on its heading, which are outside the cycle.
    // Tab enters at the first control and Shift+Tab at the last one.
    return haciaAtras ? lista[lista.length - 1]! : lista[0]!
  }

  const paso = haciaAtras ? -1 : 1
  // The modulo is the whole point: `indice + 1` alone breaks exactly at the
  // last node, which is where focus escapes to the browser chrome.
  return lista[(indice + paso + lista.length) % lista.length]!
}
