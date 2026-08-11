import { computed, type ComputedRef } from 'vue'
import { useRoute } from 'vue-router'

import { etiquetaDeRuta } from '~/utils/navegacion'

/** What every screen of the contract needs from the current route. */
export interface PantallaDeContrato {
  /** Branch label of the A3 site map, or the raw path when off contract. */
  titulo: ComputedRef<string>
  /** Current path, published as the `data-ruta` attribute of the contract. */
  ruta: ComputedRef<string>
}

/**
 * Route-derived data shared by the nine screens of the navigation contract.
 *
 * The eight module pages repeated the same two-line block verbatim, which is
 * the DRY rule of the project applied to code used more than once. It also
 * fixes a latent defect: the pages stored the title in a plain const, so once a
 * route takes dynamic params and Vue reuses the component instance the heading
 * would keep the first value it ever computed.
 *
 * @returns The heading and the path, both reactive.
 */
export function useTituloDeRuta(): PantallaDeContrato {
  const route = useRoute()

  return {
    titulo: computed(() => etiquetaDeRuta(route.path) ?? route.path),
    ruta: computed(() => route.path),
  }
}
