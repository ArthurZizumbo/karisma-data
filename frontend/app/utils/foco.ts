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
  = 'focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary'

/**
 * The same ring, painted unconditionally.
 *
 * A plate has no pointer and no caret, so the focus cell has to render the ring
 * without the browser pseudo class. It is `ANILLO_FOCO` with the variant
 * dropped and nothing else: the test pins that equality, because a plate that
 * documents a ring the browser does not paint is the defect this module exists
 * to close.
 */
export const ANILLO_FOCO_CONGELADO = 'outline-2 outline-offset-2 outline-primary'

/**
 * The ring for controls that live on the dark chrome, such as the sidebar.
 *
 * primary-500 over primary-700 is not visible enough to mark focus, so the
 * inverse ring uses the pale secondary, which the guide measures against the
 * dark background.
 */
export const ANILLO_FOCO_INVERSO
  = 'focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-secondary-soft'

/**
 * The inverse ring, drawn inwards.
 *
 * A control that fills its container edge to edge -the sort button inside a
 * sticky table header- would have an outward ring clipped by the scroll
 * container, so the offset is negative and the ring lands inside the cell.
 */
export const ANILLO_FOCO_INTERNO
  = 'focus-visible:outline-2 focus-visible:outline-offset-[-2px] focus-visible:outline-surface'
