/**
 * Light and dark mode for the portal.
 *
 * The operating system decides by default, because the real scene is an
 * eight-hour shift in a dense table and nobody should have to configure that.
 * The reader may still override it, and the choice survives a reload in a
 * cookie so the server renders the same mode the client will keep: writing it
 * to localStorage would flash the wrong mode on every server-rendered page.
 *
 * The value is applied to the root element as `data-theme`, which the generated
 * stylesheet reads. Nothing here holds a colour: `design/sistema.py` owns them.
 */
import { computed } from 'vue'

/** Explicit reader choice, or the system preference when no choice was made. */
export type ModoElegido = 'claro' | 'oscuro' | 'sistema'

const COOKIE_MODO = 'karisma_modo'

/**
 * Read and write the colour mode.
 *
 * @returns The current choice, the resolved mode, and a setter.
 */
export function useModo() {
  const eleccion = useCookie<ModoElegido>(COOKIE_MODO, {
    default: () => 'sistema',
    sameSite: 'lax',
    maxAge: 60 * 60 * 24 * 365,
  })

  const preferenciaDelSistema = useState<'claro' | 'oscuro'>('modo-sistema', () => 'claro')

  /** What the interface actually paints right now. */
  const modo = computed<'claro' | 'oscuro'>(() =>
    eleccion.value === 'sistema' ? preferenciaDelSistema.value : eleccion.value,
  )

  function elegir(nuevo: ModoElegido): void {
    eleccion.value = nuevo
    aplicar()
  }

  /**
   * Write the resolved mode onto the root element.
   *
   * `data-theme` is removed rather than set to a value when the reader follows
   * the system: the stylesheet's media query excludes itself only for an
   * explicit light choice, so leaving a stale attribute would pin the mode.
   */
  function aplicar(): void {
    if (!import.meta.client) return
    const raiz = document.documentElement
    if (eleccion.value === 'sistema') {
      raiz.removeAttribute('data-theme')
    } else {
      raiz.setAttribute('data-theme', eleccion.value)
    }
  }

  if (import.meta.client) {
    const consulta = window.matchMedia('(prefers-color-scheme: dark)')
    preferenciaDelSistema.value = consulta.matches ? 'oscuro' : 'claro'
    consulta.addEventListener('change', (evento) => {
      preferenciaDelSistema.value = evento.matches ? 'oscuro' : 'claro'
    })
  }

  return { eleccion, modo, elegir, aplicar }
}
