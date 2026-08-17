/**
 * Light and dark mode for the portal.
 *
 * The operating system decides by default, because the real scene is an
 * eight-hour shift in a dense table and nobody should have to configure that.
 * The reader may still override it, and the choice survives a reload in a
 * cookie so the server renders the same mode the client will keep.
 *
 * The composable owns the reader's *choice*. What the system currently prefers
 * lives in the store, which is a per-request singleton under SSR: holding it
 * here in a module ref would leak one visitor's preference into another's
 * render, and holding it in `useState` made the composable unusable outside a
 * Nuxt runtime, which took fifteen chassis tests down with it.
 */
import { computed, type Ref } from 'vue'

/** Explicit reader choice, or the system preference when no choice was made. */
export type ModoElegido = 'claro' | 'oscuro' | 'sistema'

export type Modo = 'claro' | 'oscuro'

const COOKIE_MODO = 'karisma_modo'

/**
 * Read and write the colour mode.
 *
 * @param preferenciaDelSistema What `prefers-color-scheme` currently reports.
 * @returns The stored choice, the resolved mode, and a setter.
 */
export function useModo(preferenciaDelSistema: Ref<Modo>) {
  const eleccion = useCookie<ModoElegido>(COOKIE_MODO, {
    default: () => 'sistema',
    sameSite: 'lax',
    maxAge: 60 * 60 * 24 * 365,
  })

  /** What the interface actually paints right now. */
  const modo = computed<Modo>(() =>
    eleccion.value === 'sistema' ? preferenciaDelSistema.value : eleccion.value,
  )

  function elegir(nuevo: ModoElegido): void {
    eleccion.value = nuevo
  }

  /**
   * Render the choice onto the root element, on the server as well.
   *
   * An earlier version wrote the attribute only inside the click handler, so
   * the cookie survived a reload and the attribute did not: the store printed
   * dark values onto a page still painted light. Declaring it through useHead
   * makes the server emit the attribute with the first byte, which also removes
   * the flash of the wrong mode that a client-side write always causes.
   *
   * Following the system emits no attribute at all, because `undefined` makes
   * useHead omit it. The stylesheet's media query excludes only an explicit
   * light choice, so a stale `data-modo` would pin the mode and ignore the
   * operating system.
   */
  useHead({
    htmlAttrs: {
      'data-modo': computed(() =>
        eleccion.value === 'sistema' ? undefined : eleccion.value,
      ),
    },
  })

  return { eleccion, modo, elegir }
}
