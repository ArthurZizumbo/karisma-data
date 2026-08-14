import type { ComputedRef, Ref } from 'vue'
import type {
  AccionUsuario,
  CodigoConflicto,
  ConflictoUsuario,
  EstadoPanel,
  PaginaUsuarios,
  UsuarioAdmin,
} from '~/types/usuarios'
import { useTimeoutFn } from '@vueuse/core'
import { computed, ref, shallowRef } from 'vue'
import { usePermisos } from '~/composables/usePermisos'
import { useSesion } from '~/composables/useSesion'
import { estadoDeFallo } from '~/utils/sesion'

/**
 * State of the user administration panel.
 *
 * It owns three things and no more: the request, the client side filter and the
 * translation of an HTTP status into a state of the screen. It never decides
 * whether an action is allowed -that is the backend's job and only its job- and
 * it never guesses the result of one: the row changes when the server answers,
 * so a panel that updated itself and then had to take it back cannot exist.
 *
 * `$fetch` and not `useFetch`: two of the three operations are mutations, the
 * list is loaded on mount from the browser, and the panel is behind a guard
 * that already resolved the session before the page mounted. There is nothing
 * to render on the server for a list only an administrator can read.
 */

/** Path published by the permission registry of US-016. Not invented here. */
export const RUTA_USUARIOS = '/api/users'

/**
 * Page size asked for.
 *
 * The endpoint caps at 200 and the portal has seven accounts, so one request
 * holds the whole list and the filter can stay on the client, where it answers
 * without a round trip. A pager would be interface for a page that never comes.
 */
export const LIMITE_USUARIOS = 200

/**
 * Milliseconds a reload may take before the table degrades to its skeleton.
 *
 * Below this the reader never sees the swap, so a fast answer does not make the
 * panel blink on every action. Above it, the wait is long enough that leaving
 * stale rows on screen would be a lie about what the portal holds.
 */
export const RETARDO_ESQUELETO = 300

/** The three conflict codes `UserErrorCode` returns, and nothing else. */
const CODIGOS_CONFLICTO: readonly CodigoConflicto[] = Object.freeze([
  'admin_no_puede_degradarse',
  'admin_no_puede_desactivarse',
  'usuario_no_encontrado',
])

/**
 * Reads the business code out of a refused request.
 *
 * The body is `{"detail": "<codigo>"}` by contract, never prose: the interface
 * is bilingual and the wording lives in the catalogues. A code this build does
 * not know is reported as no code at all, which lands on the generic error
 * state instead of printing a backend identifier at the reader.
 *
 * @param error - Value thrown by the request.
 * @returns The conflict code, or null when the body carries none.
 */
export function codigoDeConflicto(error: unknown): CodigoConflicto | null {
  const detalle = (error as { data?: { detail?: unknown } } | null)?.data?.detail
  if (typeof detalle !== 'string') {
    return null
  }
  return CODIGOS_CONFLICTO.includes(detalle as CodigoConflicto)
    ? (detalle as CodigoConflicto)
    : null
}

/**
 * Lowercases and strips the diacritics of a term.
 *
 * Six of the seven seeded names carry none, and the seventh would otherwise be
 * unreachable by typing the name the way the reader says it.
 *
 * @param texto - Text typed or read from a row.
 * @returns The comparable form of that text.
 */
function normalizar(texto: string): string {
  return texto.normalize('NFD').replace(/\p{Diacritic}/gu, '').toLowerCase()
}

/** Everything the administration screen needs in order to draw the panel. */
export interface PanelUsuarios {
  /** Everything the last successful load returned, in server order. */
  usuarios: Ref<readonly UsuarioAdmin[]>
  /** State the table publishes as `data-estado-panel`. */
  estado: ComputedRef<EstadoPanel>
  /** Free text filter over full name, username and email. Client side only. */
  filtro: Ref<string>
  usuariosVisibles: ComputedRef<readonly UsuarioAdmin[]>
  /** Last business conflict the server reported, or null. */
  conflicto: Ref<ConflictoUsuario | null>
  /**
   * Login name of the administrator running the session, or null.
   *
   * A value and not a predicate: the table receives it once and each row
   * decides for itself, so the comparison is stated in exactly one place. The
   * interface compares login names because the session of US-015 does not carry
   * the id, and adding one would reopen the frozen contract of /api/auth/me for
   * a convenience. The backend compares ids, which is where the rule is really
   * enforced; this comparison only avoids offering a control the server would
   * refuse.
   */
  usernamePropio: ComputedRef<string | null>
  /** GET /api/users. Degrades to the skeleton only after 300 ms of waiting. */
  cargar: () => Promise<void>
  /** Applies a confirmed action and reloads the list. Never optimistic. */
  aplicar: (accion: AccionUsuario) => Promise<void>
  limpiarConflicto: () => void
}

/**
 * Body of the PATCH that each non destructive action sends.
 *
 * Re-enabling travels as `{"disabled": false}` and not as an endpoint of its
 * own, which is what keeps the permission registry at three live routes.
 *
 * @param accion - Action the administrator confirmed.
 * @returns The body of the request, or null when the action is a DELETE.
 */
function cuerpoDe(accion: AccionUsuario): Record<string, unknown> | null {
  if (accion.tipo === 'cambiar-rol') {
    return { role: accion.rolNuevo }
  }
  return accion.tipo === 'reactivar' ? { disabled: false } : null
}

/**
 * Panel state and the three operations the screen performs on it.
 *
 * @returns The list, its state, the filter and the actions.
 */
export function useUsuarios(): PanelUsuarios {
  const { sesion } = useSesion()
  const { expirarSesion } = usePermisos()

  // shallowRef: rows are replaced whole, never edited in place, and a deep
  // proxy over the list would buy reactivity nothing here reads.
  const usuarios = shallowRef<readonly UsuarioAdmin[]>([])
  const filtro = ref('')
  const conflicto = ref<ConflictoUsuario | null>(null)

  /**
   * Where the request is, which is not the same question as what the table
   * draws: `vacio` is decided by the filter and is derived below.
   */
  const fase = ref<'cargando' | 'listo' | 'error'>('cargando')

  const { start: iniciarEspera, stop: detenerEspera } = useTimeoutFn(
    () => {
      fase.value = 'cargando'
    },
    RETARDO_ESQUELETO,
    { immediate: false },
  )

  const usuariosVisibles = computed<readonly UsuarioAdmin[]>(() => {
    const termino = normalizar(filtro.value.trim())
    if (termino === '') {
      return usuarios.value
    }
    return usuarios.value.filter(usuario =>
      normalizar(`${usuario.full_name} ${usuario.username} ${usuario.email}`).includes(termino),
    )
  })

  const estado = computed<EstadoPanel>(() => {
    if (fase.value !== 'listo') {
      return fase.value
    }
    return usuariosVisibles.value.length === 0 ? 'vacio' : 'listo'
  })

  const usernamePropio = computed<string | null>(() => sesion.value?.usuario ?? null)

  function limpiarConflicto(): void {
    conflicto.value = null
  }

  /**
   * Puts the row the server just returned in place of the stale one.
   *
   * @param fila - Row exactly as the endpoint answered it.
   */
  function reemplazar(fila: UsuarioAdmin): void {
    usuarios.value = usuarios.value.map(usuario => (usuario.id === fila.id ? fila : usuario))
  }

  /**
   * Ends a session the server no longer recognises.
   *
   * @param error - Value thrown by the request.
   * @returns True when the failure was a 401 and the reader is on their way out.
   */
  async function expiro(error: unknown): Promise<boolean> {
    if (estadoDeFallo(error) !== 401) {
      return false
    }
    // The hook US-017 exported for exactly this branch: a session that died
    // while the panel was open ends on the entry screen with its reason, not on
    // a table that quietly stops answering.
    await navigateTo(expirarSesion())
    return true
  }

  async function cargar(): Promise<void> {
    limpiarConflicto()
    if (usuarios.value.length === 0 || fase.value === 'error') {
      // Nothing to preserve, so there is no swap to hide: the cold open shows
      // the skeleton at once. So does the retry after a failure, and that is
      // the second half of the condition rather than a consequence of the
      // first: a failure while acting on a loaded table leaves the rows in
      // memory, and a retry that only started the timer would answer the click
      // with 300 ms of the same error state -no skeleton, no change, no way of
      // telling whether the button did anything.
      fase.value = 'cargando'
    }
    else {
      iniciarEspera()
    }

    try {
      const pagina = await $fetch<PaginaUsuarios>(RUTA_USUARIOS, {
        query: { limit: LIMITE_USUARIOS, offset: 0 },
      })
      detenerEspera()
      usuarios.value = pagina.items
      fase.value = 'listo'
    }
    catch (error) {
      detenerEspera()
      if (!(await expiro(error))) {
        fase.value = 'error'
      }
    }
  }

  async function aplicar(accion: AccionUsuario): Promise<void> {
    limpiarConflicto()
    const ruta = `${RUTA_USUARIOS}/${accion.usuario.id}`
    const cuerpo = cuerpoDe(accion)

    try {
      const fila = cuerpo === null
        ? await $fetch<UsuarioAdmin>(ruta, { method: 'DELETE' })
        : await $fetch<UsuarioAdmin>(ruta, { method: 'PATCH', body: cuerpo })
      // The answer carries the new `disabled` and the new `updated_at`, which
      // is why the endpoints reply 200 with the resource instead of 204: the
      // row is repainted from what the server confirmed, never from what the
      // click intended, and nothing has to be waited for to learn the outcome.
      reemplazar(fila)
      // And then the list is read again, because this row is not the only thing
      // that may have moved: another administrator works on the same table. The
      // repaint above is what makes that second read invisible, and the 300 ms
      // rule is what keeps it from blinking.
      await cargar()
    }
    catch (error) {
      if (await expiro(error)) {
        return
      }
      const codigo = codigoDeConflicto(error)
      if (codigo !== null) {
        // The row is left exactly as it was. A refused action that repainted
        // the table anyway would be the interface telling the reader something
        // about the portal that is not true.
        conflicto.value = { codigo, username: accion.usuario.username }
        return
      }
      fase.value = 'error'
    }
  }

  return {
    usuarios,
    estado,
    filtro,
    usuariosVisibles,
    conflicto,
    usernamePropio,
    cargar,
    aplicar,
    limpiarConflicto,
  }
}
