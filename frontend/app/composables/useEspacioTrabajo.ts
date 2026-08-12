import type { ComputedRef } from 'vue'
import type { EspacioTrabajo } from '~/types/espacios'
import type { RolUsuario } from '~/types/sesion'
import { computed } from 'vue'
import { useSesion } from '~/composables/useSesion'
import { espacioDeRol } from '~/utils/espaciosTrabajo'

/**
 * Workspace of the current reader.
 *
 * Read only, and that is the design rather than an omission: the global guard
 * loads the session before the route renders, so the home screen never fires a
 * request of its own. A second `cargarSesion()` here would duplicate the call
 * on every navigation and, worse, would race the guard for the same shared
 * state.
 *
 * It also does not touch `usePermisos`. Nothing on this screen is hidden by
 * role: the composition contract already gives each workspace only routes its
 * own role can open, which is a property proven once over data instead of a
 * filter evaluated on every render.
 */

/** What the home screen needs in order to choose and label its composition. */
export interface EspacioActivo {
  /** Workspace derived from the session role. Never null. */
  espacio: ComputedRef<EspacioTrabajo>
  /** True while the guard has not resolved the session yet. */
  cargando: ComputedRef<boolean>
  /** Display name of the signed in user, empty string when unknown. */
  nombre: ComputedRef<string>
  /** Role of the session, or null before it resolves. */
  rol: ComputedRef<RolUsuario | null>
}

/**
 * Workspace, name and role of the reader, all derived from the shared session.
 *
 * @returns The active workspace and the two labels the compositions print.
 */
export function useEspacioTrabajo(): EspacioActivo {
  const { sesion, cargando } = useSesion()

  return {
    espacio: computed(() => espacioDeRol(sesion.value?.rol ?? null)),
    // Only while there is nothing to show yet. A refresh of an already resolved
    // session must not blank the screen the reader is looking at.
    cargando: computed(() => cargando.value && sesion.value === null),
    nombre: computed(() => sesion.value?.nombre ?? ''),
    rol: computed(() => sesion.value?.rol ?? null),
  }
}
