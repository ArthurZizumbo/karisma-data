import type { Ref } from 'vue'
import { computed } from 'vue'
import { TEMA_OMISION, TEMAS, type TemaSistema } from '~/utils/tokens.generated'

/**
 * Visual theme of the portal.
 *
 * The axis is colour *and* type family, and it is not the colour mode: the mode
 * says whether the room is lit and the theme says which product this is. They
 * used to share one attribute -`data-theme` carried the mode- and that name is
 * now split in two, `data-modo` and `data-tema`, because a theme landing on top
 * of that spelling guaranteed the confusion.
 *
 * The choice is read from the cookie and rendered through `useHead`, exactly as
 * `useIdioma` does with the language: the server has to emit the attribute with
 * the first byte or the first paint uses the other theme and the reader sees a
 * flash. Applying it after mount is the defect this module exists to avoid.
 *
 * The state is a `useState` and not the cookie ref itself. `useCookie` hands a
 * new ref to every caller, so the store and the application shell would hold
 * two disconnected copies and a change made through one of them would not reach
 * the attribute the other one declared.
 */

/** The two themes, spelled as the generator spells them. */
export type TemaPortal = TemaSistema

/** Name of the cookie that carries the reader's choice across visits. */
export const CLAVE_COOKIE_TEMA = 'karisma_tema'

/** Key of the shared theme state. */
const CLAVE_ESTADO_TEMA = 'karisma-tema'

/** One year in seconds. A theme choice does not expire within a semester. */
const VIGENCIA_COOKIE_TEMA = 60 * 60 * 24 * 365

/** The themes in the order the selector offers them. */
export const TEMAS_PORTAL: readonly TemaPortal[] = TEMAS

/**
 * Narrows an arbitrary cookie value to a theme the system really emits.
 *
 * @param valor - Value read from the cookie or from a control.
 * @returns True when the value is one of the emitted themes.
 */
export function esTemaPortal(valor: unknown): valor is TemaPortal {
  return typeof valor === 'string' && (TEMAS as readonly string[]).includes(valor)
}

/** What the selector and the design system store need from the theme state. */
export interface TemaActivo {
  /** Theme currently painted. */
  readonly tema: Readonly<Ref<TemaPortal>>
  /** Switches the theme and remembers the choice for the next visit. */
  fijarTema: (nuevo: TemaPortal) => void
}

/**
 * Reads and writes the visual theme.
 *
 * @returns The active theme and the operation that changes it.
 */
export function useTema(): TemaActivo {
  const cookie = useCookie<TemaPortal | null>(CLAVE_COOKIE_TEMA, {
    path: '/',
    sameSite: 'lax',
    maxAge: VIGENCIA_COOKIE_TEMA,
  })

  const tema = useState<TemaPortal>(CLAVE_ESTADO_TEMA, () =>
    esTemaPortal(cookie.value) ? cookie.value : TEMA_OMISION,
  )

  function fijarTema(nuevo: TemaPortal): void {
    if (!esTemaPortal(nuevo)) {
      return
    }
    // The cookie is written first for the same reason as in useIdioma: if
    // anything below fails, the next visit still opens in the chosen theme.
    cookie.value = nuevo
    tema.value = nuevo
  }

  /**
   * Render the choice onto the root element, on the server as well.
   *
   * The default theme emits no attribute at all, because it is the `@theme`
   * block of the generated stylesheet and not an override: `undefined` makes
   * useHead omit the attribute, which is the same contract the mode uses for
   * "follow the operating system".
   */
  useHead({
    htmlAttrs: {
      'data-tema': computed(() => (tema.value === TEMA_OMISION ? undefined : tema.value)),
    },
  })

  return { tema, fijarTema }
}
