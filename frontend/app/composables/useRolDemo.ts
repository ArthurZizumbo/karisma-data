import type { ComputedRef, Ref } from 'vue'
import type { MotivoFalloAcceso, RolUsuario, SesionUsuario } from '~/types/sesion'
import { ref } from 'vue'
import { usePermisos } from '~/composables/usePermisos'
import { esFalloDeAcceso, useSesion } from '~/composables/useSesion'
import { destinoPorRol, ROLES } from '~/utils/sesion'

/**
 * Demonstration profile of the current reader, changed from the chrome.
 *
 * The role is NEVER changed in the browser. Every switch mints a real session
 * through `POST /api/auth/demo`, which is the same door the entry screen uses:
 * a role held in client state would leave the guard of the server deciding with
 * the old token, and the one security story this portal tells -the server
 * decides, and the agent never sees data the reader may not see- would become
 * decoration.
 *
 * The composable does not navigate. It reports where the reader should end up
 * and the component moves them, which is the same split `usePermisos` uses for
 * `expirarSesion`: it keeps this module free of the router, so its test is a
 * table of values instead of a knot of doubles.
 */

/** Where the reader ends up after a profile was minted. */
export type ResultadoEntrada
  = | {
    /** The requested route is within reach of the new role. */
    readonly tipo: 'abierta'
    readonly ruta: string
    readonly sesion: SesionUsuario
  }
  | {
    /** The new role cannot open the requested route, so it lands on its own. */
    readonly tipo: 'desviada'
    readonly ruta: string
    readonly pedida: string
    readonly scopeExigido: RolUsuario | null
    readonly sesion: SesionUsuario
  }
  | {
    /** The door refused. No session was minted and nothing moved. */
    readonly tipo: 'fallo'
    readonly motivo: MotivoFalloAcceso
  }

/** What a control needs in order to offer the four demonstration profiles. */
export interface ControlDeRolDemo {
  /** Role of the current session, or null when there is none. */
  rolActual: ComputedRef<RolUsuario | null>
  /** The four roles, in the canonical order of the identity contract. */
  roles: readonly RolUsuario[]
  /** Whether the demonstration door is offered at all in this deployment. */
  disponible: boolean
  /** True while a session is being minted; the controls rest. */
  cambiando: Readonly<Ref<boolean>>
  /** Why the last attempt failed, already stripped of the backend wording. */
  motivoFallo: Readonly<Ref<MotivoFalloAcceso | null>>
  /** Mints a session for the role and reports where the reader belongs. */
  entrarComoRol: (rol: RolUsuario, rutaPedida: string) => Promise<ResultadoEntrada>
}

/**
 * Session state of the demonstration profiles and the one operation that
 * changes it.
 *
 * @returns The current role, the four options, the in-flight flag, the last
 *   failure and the operation that mints a session.
 */
export function useRolDemo(): ControlDeRolDemo {
  const { iniciarSesionDemo } = useSesion()
  const { rol, puedeVerRuta, scopeExigidoPor, limpiarBloqueo, olvidarExpiracion } = usePermisos()

  /**
   * Whether the door is shown at all.
   *
   * The real gate is DEMO_LOGIN_ENABLED on the backend, which does not even
   * mount the route when it is off. This flag only decides whether the
   * interface advertises a door that would answer 404.
   */
  const disponible = useRuntimeConfig().public.demoAcceso === true

  const cambiando = ref<boolean>(false)
  const motivoFallo = ref<MotivoFalloAcceso | null>(null)

  async function entrarComoRol(
    rol: RolUsuario,
    rutaPedida: string,
  ): Promise<ResultadoEntrada> {
    motivoFallo.value = null

    if (!disponible) {
      // Not a request: the deployment already said the door is closed, and
      // asking anyway would turn a configuration into a network error.
      motivoFallo.value = 'demo-deshabilitado'
      return { tipo: 'fallo', motivo: 'demo-deshabilitado' }
    }

    cambiando.value = true
    try {
      const sesion = await iniciarSesionDemo(rol)

      // The refusal of the previous role does not survive the new session: the
      // portal layout paints the block until something clears it, and the
      // reader who just changed profile precisely to reach that screen would
      // find it still refused.
      limpiarBloqueo()
      olvidarExpiracion()

      if (puedeVerRuta(rutaPedida)) {
        return { tipo: 'abierta', ruta: rutaPedida, sesion }
      }

      return {
        tipo: 'desviada',
        ruta: destinoPorRol(sesion.rol),
        pedida: rutaPedida,
        scopeExigido: scopeExigidoPor(rutaPedida),
        sesion,
      }
    }
    catch (error) {
      const motivo: MotivoFalloAcceso = esFalloDeAcceso(error) ? error.motivo : 'servidor'
      motivoFallo.value = motivo
      return { tipo: 'fallo', motivo }
    }
    finally {
      cambiando.value = false
    }
  }

  return { rolActual: rol, roles: ROLES, disponible, cambiando, motivoFallo, entrarComoRol }
}
