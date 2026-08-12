import type { ComputedRef, Ref } from 'vue'
import type { BloqueoDeRuta } from '~/types/guarda'
import type { ModuloNav } from '~/types/navegacion'
import type { RolUsuario } from '~/types/sesion'
import { computed } from 'vue'
import { useSesion } from '~/composables/useSesion'
import { rolAlcanza } from '~/utils/guarda'
import { MODULOS, RUTA_ACCESO, RUTA_ASISTENTE } from '~/utils/navegacion'
import { SCOPE_POR_RAMA, SCOPE_POR_RUTA } from '~/utils/permisos.generated'
import { MOTIVO_EXPIRADA } from '~/utils/sesion'

/**
 * Projection of the generated permission map onto the current session.
 *
 * It deliberately does NOT extend `useSesion`. Identity -who you are- and
 * authorization -what you may see- are different concerns with different
 * lifetimes: the session is minted once by the entry screen, and the projection
 * is recomputed on every navigation and on every card of every screen. Keeping
 * them apart also removes the write collision with the user stories that
 * compose the workspaces, which read the session too.
 *
 * No component compares roles. The sidebar receives a list of modules already
 * filtered and never imports the generated map; the "no permission" state
 * receives the required scope as a property and only translates it.
 */

/** Key of the shared block state, serialized into the SSR payload. */
const CLAVE_BLOQUEO = 'karisma-guarda-bloqueo'

/** Key of the one shot flag that remembers a session lost to a 401. */
const CLAVE_EXPIRADA = 'karisma-guarda-expirada'

/** What the guard, the sidebar and any screen need in order to hide by role. */
export interface ControlDePermisos {
  /** Role of the current session, or null when there is none. */
  rol: ComputedRef<RolUsuario | null>
  /** True when the current role covers the scope. Null means any session. */
  alcanza: (scope: RolUsuario | null) => boolean
  /** Modules of the A3 map the reader may use, with their branches filtered. */
  modulosVisibles: ComputedRef<readonly ModuloNav[]>
  /** Whether the cross cutting assistant entry belongs in the sidebar. */
  asistenteVisible: ComputedRef<boolean>
  /** Minimum role a route demands, read from the generated map. */
  scopeExigidoPor: (ruta: string) => RolUsuario | null
  /** Convenience wrapper over the previous two. */
  puedeVerRuta: (ruta: string) => boolean
  /** Route the reader could not open, rendered by the portal layout. */
  bloqueo: Ref<BloqueoDeRuta | null>
  marcarBloqueo: (nuevo: BloqueoDeRuta) => void
  limpiarBloqueo: () => void
  /**
   * True when a session was lost to a 401 and the reader has not been told yet.
   *
   * It is the only way the guard can tell an expiry from a first visit, and it
   * has to be its own flag rather than "the state used to hold a session":
   * whoever detected the 401 already emptied that state, so by the time the
   * next navigation runs, an expired reader and a brand new visitor look
   * exactly alike. A deliberate sign out does not raise it, which is why
   * leaving on purpose never produces "your session expired".
   */
  expirada: Ref<boolean>
  /**
   * Clears the session after a 401 and returns the path of the clean re-login.
   *
   * Exported for the data user stories: they call it from the error branch of
   * their fetch. Returning the path instead of navigating keeps this composable
   * free of the router, which is what lets it be tested as a function.
   */
  expirarSesion: () => string
  /** Marks the expiry as already explained to the reader. */
  olvidarExpiracion: () => void
}

/**
 * Drops the query string, the hash and any trailing slash of a path.
 *
 * @param ruta - Path as the router reports it.
 * @returns The bare path, with '/' preserved as itself.
 */
function normalizar(ruta: string): string {
  const sinQuery = ruta.split('?')[0]?.split('#')[0] ?? ''
  return sinQuery.length > 1 ? sinQuery.replace(/\/+$/, '') : sinQuery
}

/**
 * Authorization state of the current reader and the five questions it answers.
 *
 * @returns The role, the visibility helpers and the block of the current route.
 */
export function usePermisos(): ControlDePermisos {
  const { sesion } = useSesion()
  const bloqueo = useState<BloqueoDeRuta | null>(CLAVE_BLOQUEO, () => null)
  const expirada = useState<boolean>(CLAVE_EXPIRADA, () => false)

  const rol = computed<RolUsuario | null>(() => sesion.value?.rol ?? null)

  function alcanza(scope: RolUsuario | null): boolean {
    return rolAlcanza(rol.value, scope)
  }

  /**
   * A route with no entry in the map demands a session and nothing more.
   *
   * It is not the last line of defence and it is not meant to be: every data
   * endpoint carries its own `Security(...)` in the backend, so a route missing
   * here costs a screen that renders and then fails its own calls, never a leak.
   * The barrier against forgetting one is `test/permisos.spec.ts`, which
   * requires every route of the contract to have an entry.
   */
  function scopeExigidoPor(ruta: string): RolUsuario | null {
    return SCOPE_POR_RUTA[normalizar(ruta)] ?? null
  }

  function puedeVerRuta(ruta: string): boolean {
    return alcanza(scopeExigidoPor(ruta))
  }

  // Copies, never the frozen objects of MODULOS: filtering in place would be a
  // side effect on the navigation contract that every other screen reads.
  const modulosVisibles = computed<readonly ModuloNav[]>(() =>
    MODULOS.filter(modulo => alcanza(SCOPE_POR_RAMA[modulo.id] ?? null)).map(modulo => ({
      ...modulo,
      subrutas: modulo.subrutas.filter(subruta => alcanza(SCOPE_POR_RAMA[subruta.id] ?? null)),
    })),
  )

  const asistenteVisible = computed<boolean>(() => puedeVerRuta(RUTA_ASISTENTE))

  function marcarBloqueo(nuevo: BloqueoDeRuta): void {
    bloqueo.value = nuevo
  }

  function limpiarBloqueo(): void {
    bloqueo.value = null
  }

  function expirarSesion(): string {
    sesion.value = null
    bloqueo.value = null
    expirada.value = true
    return `${RUTA_ACCESO}?motivo=${MOTIVO_EXPIRADA}`
  }

  function olvidarExpiracion(): void {
    expirada.value = false
  }

  return {
    rol,
    alcanza,
    modulosVisibles,
    asistenteVisible,
    scopeExigidoPor,
    puedeVerRuta,
    bloqueo,
    marcarBloqueo,
    limpiarBloqueo,
    expirada,
    expirarSesion,
    olvidarExpiracion,
  }
}
