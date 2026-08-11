import type { SesionUsuario } from '~/types/sesion'
import {
  establecerSesion,
  exigirOrigenPropio,
  fallaDeAutenticacion,
  leerPerfilDeSesion,
} from '../../utils/sesion'

/**
 * Exchanges a username and a password for a session.
 *
 * This route exists so that the JWT never reaches the browser. It talks to the
 * backend twice -once to mint the token, once to read the profile it belongs
 * to- writes the token into an httpOnly cookie and answers with three fields
 * that carry no credential at all.
 *
 * The backend speaks the OAuth2 password flow, so the credentials leave here as
 * `application/x-www-form-urlencoded`. That is also what makes the Authorize
 * button of Swagger work, which is the tool every endpoint of US-016 is probed
 * with by hand.
 */

/** Body this route accepts from the browser. */
interface CuerpoDeAcceso {
  usuario?: unknown
  contrasena?: unknown
}

/** Body of POST /api/auth/token on the backend. */
interface TokenEmitido {
  access_token: string
}

export default defineEventHandler(async (event): Promise<SesionUsuario> => {
  exigirOrigenPropio(event)

  const { apiBase } = useRuntimeConfig(event)
  const cuerpo = await readBody<CuerpoDeAcceso | null>(event)

  // Coerced rather than validated: an empty field is a wrong credential and the
  // backend already answers it with the same neutral 401 as an unknown user.
  const formulario = new URLSearchParams({
    username: typeof cuerpo?.usuario === 'string' ? cuerpo.usuario : '',
    password: typeof cuerpo?.contrasena === 'string' ? cuerpo.contrasena : '',
  })

  let emision: TokenEmitido
  try {
    emision = await $fetch<TokenEmitido>(`${apiBase}/api/auth/token`, {
      method: 'POST',
      headers: { 'content-type': 'application/x-www-form-urlencoded' },
      body: formulario.toString(),
    })
  }
  catch (error) {
    throw fallaDeAutenticacion(error)
  }

  try {
    const sesion = await leerPerfilDeSesion(apiBase, emision.access_token)
    establecerSesion(event, emision.access_token)
    return sesion
  }
  catch (error) {
    // The cookie is written only after the profile reads back. A token whose
    // profile cannot be read is a token the interface could not act on, and
    // storing it would leave a session that looks open and answers nothing.
    throw fallaDeAutenticacion(error)
  }
})
