import { computed, type ComputedRef } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute } from 'vue-router'

import { claveDeRuta } from '~/utils/navegacion'

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
 * Since the bilingual decision of 10-ago-2026 the navigation contract holds
 * translation keys, so the heading is translated here and stays reactive to a
 * language change as well as to a route change.
 *
 * @returns The heading and the path, both reactive.
 */
export function useTituloDeRuta(): PantallaDeContrato {
  const route = useRoute()
  const { t } = useI18n()

  return {
    titulo: computed(() => {
      const clave = claveDeRuta(route.path)
      return clave === undefined ? route.path : t(clave)
    }),
    ruta: computed(() => route.path),
  }
}
