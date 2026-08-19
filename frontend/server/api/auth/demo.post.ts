import type { SesionUsuario } from '~/types/sesion'
import { esRolUsuario } from '~/utils/sesion'
import { ErrorDeIdentidad, tokenDeIdentidad } from '../../utils/identidadCloudRun'
import {
  establecerSesion,
  exigirOrigenPropio,
  fallaDeAutenticacion,
  leerPerfilDeSesion,
} from '../../utils/sesion'

/**
 * Opens a session for one of the four demonstration profiles, with no password.
 *
 * The door is real and it is labelled as such on screen: with the flag on,
 * anyone who reaches the URL gets in. It is acceptable in an evaluated
 * prototype over synthetic data and it stops being acceptable the day there is
 * a real figure behind it, which is why the backend mounts the route only when
 * DEMO_LOGIN_ENABLED is true and answers 404 -not 403- otherwise: a 403 would
 * confirm that the door is there.
 *
 * The role in the body only selects the canonical user. The scope of the token
 * comes from that user's row, so this route cannot mint a permission the same
 * person would not get by typing their password.
 */

/** Body this route accepts from the browser. */
interface CuerpoDemostracion {
  rol?: unknown
}

/** Body of POST /api/auth/demo on the backend. */
interface TokenDemostracion {
  access_token: string
}

export default defineEventHandler(async (event): Promise<SesionUsuario> => {
  exigirOrigenPropio(event)

  const { apiBase, apiAudience } = useRuntimeConfig(event) as { apiBase: string, apiAudience?: string }
  const cuerpo = await readBody<CuerpoDemostracion | null>(event)
  const rol = cuerpo?.rol

  if (!esRolUsuario(rol)) {
    // Rejected here rather than upstream: the backend would answer 422 and the
    // screen would report a server failure for what is a bad request.
    throw createError({
      statusCode: 400,
      statusMessage: 'Bad Request',
      data: { codigo: 'rol_desconocido' },
    })
  }

  const cabeceras: Record<string, string> = {}
  if (apiAudience) {
    try {
      const idToken = await tokenDeIdentidad(apiAudience)
      cabeceras['x-serverless-authorization'] = `Bearer ${idToken}`
    }
    catch {
      throw createError({
        statusCode: 502,
        statusMessage: 'Bad Gateway',
        data: { codigo: 'servicio_no_disponible' },
      })
    }
  }

  try {
    const emision = await $fetch<TokenDemostracion>(`${apiBase}/api/auth/demo`, {
      method: 'POST',
      headers: cabeceras,
      body: { rol },
    })
    const sesion = await leerPerfilDeSesion(apiBase, emision.access_token, apiAudience)
    establecerSesion(event, emision.access_token)
    return sesion
  }
  catch (error) {
    // An unreachable metadata server is not a closed demonstration door:
    // saying so sends the reader hunting for a backend flag that is in fact on.
    if (error instanceof ErrorDeIdentidad) {
      throw createError({
        statusCode: 502,
        statusMessage: 'Bad Gateway',
        data: { codigo: 'servicio_no_disponible' },
      })
    }
    throw fallaDeAutenticacion(error, 'demo_deshabilitado')
  }
})
