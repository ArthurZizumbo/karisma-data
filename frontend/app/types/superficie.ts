/**
 * Contained surfaces of Karisma Data.
 *
 * A card is not a box with a shadow: it is a piece of surface that says which
 * channel the thing inside belongs to. The channel is a NAME and never a
 * colour, so the component that paints it can resolve it against whichever
 * theme is mounted -the default one paints the action channel in plain
 * current, the institutional one paints it teal- without a single consumer
 * having to know which theme it is running under.
 *
 * `neutro` is the absence of a channel and not a fifth colour. A card that
 * carries no state paints no bar, because a bar that always shows up stops
 * meaning anything.
 */

/** Channel a contained surface paints on its left edge. */
export type CanalTarjeta = 'accion' | 'aviso' | 'ok' | 'error' | 'neutro'
