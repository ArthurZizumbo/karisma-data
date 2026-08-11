/**
 * Session contract of Karisma Data.
 *
 * The JWT never reaches the browser. Nitro exchanges the credentials, keeps the
 * token in an httpOnly cookie and hands the application the three fields below,
 * which is why no type in this module carries a token and nothing anywhere
 * decodes one.
 */

/**
 * The four roles of the portal, spelled exactly as the backend spells them in
 * the `scope` claim and in the CHECK constraint of `app_user`.
 *
 * `RolSugerido` in types/navegacion.ts says `administrador` for the fourth one.
 * The two vocabularies are deliberately not merged here: that one labels a
 * prototype card of the A3 map and this one is the vocabulary of the token.
 * Reconciling them belongs to US-017, which builds the sidebar by role.
 */
export type RolUsuario = 'operativo' | 'analista' | 'directivo' | 'admin'

/** Who is signed in, as the interface sees them. */
export interface SesionUsuario {
  /** Login name, unique in `app_user`. */
  readonly usuario: string
  /** Readable name shown in the chrome. */
  readonly nombre: string
  /** Role that decides the landing screen and the visible modules. */
  readonly rol: RolUsuario
}

/** What the entry form collects. Never stored, never logged. */
export interface CredencialesAcceso {
  readonly usuario: string
  readonly contrasena: string
}

/**
 * Body of `GET /api/auth/me`.
 *
 * The field names are the backend's, not ours: this is a wire shape, and
 * renaming it here would hide the day the contract changes.
 */
export interface PerfilDeUsuario {
  readonly username: string
  readonly full_name: string
  readonly role: string
}

/**
 * The five states the entry screen is designed for.
 *
 * They are published as `data-estado` on the form so the five are verifiable
 * instead of asserted, and so a state that nobody designed cannot reach the
 * screen disguised as the normal one.
 */
export type EstadoAcceso
  = | 'normal'
    | 'campo-invalido'
    | 'credencial-invalida'
    | 'cargando'
    | 'sesion-expirada'

/**
 * Why an attempt to enter failed, already stripped of the backend wording.
 *
 * The 401 of the backend carries a Spanish `detail` on purpose, and the
 * interface is bilingual: the reason travels as one of these three values and
 * the screen resolves its own message. Three failures share `credenciales`
 * -unknown user, wrong password, disabled user- because a neutral 401 that the
 * interface then tells apart is not neutral.
 */
export type MotivoFalloAcceso = 'credenciales' | 'demo-deshabilitado' | 'servidor'

/**
 * How a refusal is presented.
 *
 * The two are not decoration. An error is something the reader can act on -a
 * password to retype, an attempt to repeat- and it is drawn with the error
 * colour and the alert shape. `sin-permiso` is the fourth unhappy state of the
 * design system: the door itself is closed, retrying changes nothing, and it
 * carries the warning colour and the lock, which is the same pair the indicator
 * card uses for the same meaning.
 */
export type TonoAviso = 'error' | 'sin-permiso'

/** A refusal, ready to be rendered: what it says and how it is shown. */
export interface AvisoAcceso {
  /** Translation key of the message. Never a string the backend sent. */
  readonly clave: string
  readonly tono: TonoAviso
}
