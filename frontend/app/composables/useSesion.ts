import type { Ref } from 'vue'
import type {
  CredencialesAcceso,
  MotivoFalloAcceso,
  RolUsuario,
  SesionUsuario,
} from '~/types/sesion'
import { aSesionUsuario, estadoDeFallo } from '~/utils/sesion'

/**
 * Session of the current reader, shared through useState.
 *
 * None of the five operations below ever sees a JWT. The token is minted,
 * stored and replayed by Nitro, so this module has nothing to decode and no
 * credential to keep: that is what makes "the token never reaches the browser"
 * a property of the design instead of a promise.
 *
 * `useState` and not a module ref: under SSR a module ref is shared by every
 * visitor being rendered at that moment, which would leak one reader's session
 * into another reader's HTML.
 *
 * Module visibility by scope is NOT here. US-017 put it in `usePermisos`,
 * because identity and authorization are different concerns with different
 * lifetimes; the only thing it changed in this file is the transport of
 * `cargarSesion`, and it changed nothing of the public surface.
 */

/** Key of the shared session state. */
const CLAVE_SESION = 'karisma-sesion'

/** Key of the shared in-flight flag. */
const CLAVE_CARGANDO = 'karisma-sesion-cargando'

/**
 * An attempt to enter that the server refused, with the reason already
 * translated out of the backend's wording.
 */
export class FalloDeAcceso extends Error {
  constructor(readonly motivo: MotivoFalloAcceso) {
    super(`acceso rechazado: ${motivo}`)
    this.name = 'FalloDeAcceso'
  }
}

/**
 * Narrows a caught value to a refusal this composable produced.
 *
 * @param error - Value caught while entering.
 * @returns True when the failure carries one of the three known reasons.
 */
export function esFalloDeAcceso(error: unknown): error is FalloDeAcceso {
  return error instanceof FalloDeAcceso
}

/** What a screen needs in order to open, read and close a session. */
export interface ControlDeSesion {
  /** Who is signed in, or null. */
  sesion: Ref<SesionUsuario | null>
  /** True while a request of this composable is in flight. */
  cargando: Ref<boolean>
  /** Reads the session the cookie already carries. */
  cargarSesion: () => Promise<void>
  /** Exchanges credentials for a session. */
  iniciarSesion: (credenciales: CredencialesAcceso) => Promise<SesionUsuario>
  /** Opens a session for one of the four demonstration profiles. */
  iniciarSesionDemo: (rol: RolUsuario) => Promise<SesionUsuario>
  /** Drops the cookie and forgets the session. */
  cerrarSesion: () => Promise<void>
}

/**
 * Reads the reason a request to enter failed.
 *
 * A 401 is a rejected credential, whichever of the three neutral cases produced
 * it. A 404 can only come from the demonstration route when the flag is off.
 * Everything else -a 502, a network error- is reported as a server failure, so
 * the reader is never told to check a password that was in fact correct.
 *
 * @param error - Value thrown by the request.
 * @returns The reason, as the screen will render it.
 */
function motivoDelFallo(error: unknown): MotivoFalloAcceso {
  const estado = estadoDeFallo(error)
  if (estado === 401) {
    return 'credenciales'
  }
  if (estado === 404) {
    return 'demo-deshabilitado'
  }
  return 'servidor'
}

/**
 * Session state and the four operations that change it.
 *
 * @returns The shared session, the in-flight flag and the four operations.
 */
export function useSesion(): ControlDeSesion {
  const sesion = useState<SesionUsuario | null>(CLAVE_SESION, () => null)
  const cargando = useState<boolean>(CLAVE_CARGANDO, () => false)

  async function entrar(ruta: string, cuerpo: Record<string, string>): Promise<SesionUsuario> {
    cargando.value = true
    try {
      // The Nitro route answers with the session and with nothing else: there
      // is no token in this payload to forget to strip.
      const abierta = await $fetch<SesionUsuario>(ruta, { method: 'POST', body: cuerpo })
      sesion.value = abierta
      return abierta
    }
    catch (error) {
      sesion.value = null
      throw new FalloDeAcceso(motivoDelFallo(error))
    }
    finally {
      cargando.value = false
    }
  }

  async function cargarSesion(): Promise<void> {
    cargando.value = true
    try {
      // `useRequestFetch()` and not `$fetch`: during server rendering the
      // browser cookie does not travel on its own. A bare `$fetch` opens a new
      // request with none of the incoming headers, the proxy finds no
      // `karisma_sesion`, the backend answers 401 and the guard would bounce a
      // reader with a perfectly valid session to the entry screen on every full
      // reload. On the client it is `$fetch` itself.
      const peticion = useRequestFetch()
      sesion.value = aSesionUsuario(await peticion('/api/auth/me'))
    }
    catch {
      // A visitor with no cookie is not an error: it is the ordinary first
      // visit, and the entry screen is where they belong.
      sesion.value = null
    }
    finally {
      cargando.value = false
    }
  }

  async function iniciarSesion(credenciales: CredencialesAcceso): Promise<SesionUsuario> {
    return await entrar('/api/auth/token', {
      usuario: credenciales.usuario,
      contrasena: credenciales.contrasena,
    })
  }

  async function iniciarSesionDemo(rol: RolUsuario): Promise<SesionUsuario> {
    return await entrar('/api/auth/demo', { rol })
  }

  async function cerrarSesion(): Promise<void> {
    try {
      await $fetch('/api/auth/logout', { method: 'POST' })
    }
    finally {
      // Forgotten here whatever the server answered: leaving the name on screen
      // after the reader asked to leave is worse than a cookie that outlives
      // the click, and the cookie is dropped by the same request.
      sesion.value = null
    }
  }

  return { sesion, cargando, cargarSesion, iniciarSesion, iniciarSesionDemo, cerrarSesion }
}
