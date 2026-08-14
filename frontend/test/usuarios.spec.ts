import type { VueWrapper } from '@vue/test-utils'
import type { RolUsuario } from '~/types/sesion'
import type { PaginaUsuarios, UsuarioAdmin } from '~/types/usuarios'

import { flushPromises, mount } from '@vue/test-utils'
import { createMemoryHistory, createRouter, RouterLink } from 'vue-router'
import { afterEach, describe, expect, it, vi } from 'vitest'

import AdministracionTablaUsuarios from '~/components/administracion/TablaUsuarios.vue'
import { useSesion } from '~/composables/useSesion'
import { RETARDO_ESQUELETO, useUsuarios } from '~/composables/useUsuarios'
import Administracion from '~/pages/administracion.vue'
import { RUTA_ADMINISTRACION } from '~/utils/espaciosTrabajo'
import { RUTA_ACCESO, RUTA_INDICE, RUTAS_CONTRATO } from '~/utils/navegacion'
import { MOTIVO_EXPIRADA } from '~/utils/sesion'
import { crearI18nDePrueba, mensaje } from './i18nDePrueba'

/**
 * US-018/019 — the administration panel, from the request to the painted row.
 *
 * Only the transport is doubled. The composable runs for real -state machine,
 * client filter, translation of a status into a state of the screen- and so do
 * the three components, because that is where the defects of this User Story
 * live. A double of the composable would leave exactly the code under test
 * unmeasured.
 *
 * The fake server keeps rows and mutates them, so "the row changes when the
 * server answers" is measured against an answer and not against an intention:
 * a client that repainted optimistically would still pass a test whose server
 * always agrees, and would fail the ones below where it refuses.
 */

/** Seven accounts, the ones the seed of US-015 creates. No others exist. */
const SEMILLA: readonly (readonly [string, string, RolUsuario])[] = Object.freeze([
  ['acastaneda', 'Arturo Castaneda', 'directivo'],
  ['dhernandez', 'Diego Hernandez', 'analista'],
  ['eruiz', 'Elena Ruiz', 'operativo'],
  ['jmendieta', 'Jorge Mendieta', 'analista'],
  ['lmendez', 'Laura Mendez', 'operativo'],
  ['movalle', 'Mariana Ovalle', 'admin'],
  ['rvaldez', 'Roberto Valdez', 'directivo'],
])

const CREADO = '2026-08-11T21:12:50Z'
const MODIFICADO = '2026-08-13T09:30:00Z'

/** The same row, writable, which is what the fake server holds. */
type FilaMutable = { -readonly [K in keyof UsuarioAdmin]: UsuarioAdmin[K] }

/** Ordered by username ascending, which is the order the endpoint promises. */
const CUENTAS: readonly UsuarioAdmin[] = Object.freeze(
  SEMILLA.map(([username, nombre, role], indice) => ({
    id: `0000000${indice}-0000-4000-8000-000000000000`,
    username,
    email: `${username}@karisma.demo`,
    full_name: nombre,
    role,
    disabled: false,
    created_at: CREADO,
    updated_at: CREADO,
  })),
)

const USUARIOS_EN_ORDEN = CUENTAS.map(cuenta => cuenta.username)

/** A business code this build does not know: a fourth `UserErrorCode`. */
const CODIGO_DESCONOCIDO = 'cuota_de_administradores_agotada'

interface Opciones {
  method?: string
  body?: unknown
  query?: unknown
}

interface Llamada {
  ruta: string
  metodo: string
  cuerpo?: unknown
}

/**
 * Builds a refusal shaped the way ofetch reports one.
 *
 * @param estado - HTTP status. Zero is what a network failure looks like.
 * @param detalle - Business code the API puts in `detail`, if any.
 * @returns The value the request rejects with.
 */
function refusal(estado: number, detalle?: string): unknown {
  return Object.assign(new Error(`http ${estado}`), {
    status: estado,
    statusCode: estado,
    data: detalle === undefined ? undefined : { detail: detalle },
  })
}

/**
 * A server that holds the seven rows and really mutates them.
 *
 * @param cuentas - Rows it starts with.
 * @param campoDeMas - Extra field glued onto every row it answers with. The
 *   real backend never sends one; it is here so the screen can be measured
 *   against a payload that carries what must never be printed.
 * @returns The rows, the calls received and the handler `$fetch` delegates to.
 */
function crearServidor(
  cuentas: readonly UsuarioAdmin[] = CUENTAS,
  campoDeMas: Record<string, unknown> = {},
) {
  const filas: FilaMutable[] = cuentas.map(cuenta => ({ ...cuenta }))
  const llamadas: Llamada[] = []
  let pendiente: { error: unknown, veces: number } | null = null
  let retenida: ((pagina: PaginaUsuarios) => void) | null = null

  function vestir(fila: FilaMutable): UsuarioAdmin {
    return { ...fila, ...campoDeMas } as UsuarioAdmin
  }

  function pagina(): PaginaUsuarios {
    return { items: filas.map(vestir), total: filas.length, limit: 200, offset: 0 }
  }

  function manejar(ruta: string, opciones: Opciones = {}): unknown {
    const metodo = opciones.method ?? 'GET'
    llamadas.push({ ruta, metodo, cuerpo: opciones.body })

    if (pendiente !== null && pendiente.veces > 0) {
      pendiente.veces -= 1
      throw pendiente.error
    }

    if (metodo === 'GET') {
      if (retenida !== null) {
        // The answer is held so the wait can be measured, not simulated.
        return new Promise<PaginaUsuarios>((resolver) => {
          retenida = resolver
        })
      }
      return pagina()
    }

    const fila = filas.find(candidata => ruta.endsWith(candidata.id))
    if (fila === undefined) {
      throw refusal(404, 'usuario_no_encontrado')
    }
    if (metodo === 'DELETE') {
      fila.disabled = true
    }
    else {
      const cuerpo = opciones.body as { role?: RolUsuario, disabled?: boolean }
      if (cuerpo.role !== undefined) {
        fila.role = cuerpo.role
      }
      if (cuerpo.disabled !== undefined) {
        fila.disabled = cuerpo.disabled
      }
    }
    fila.updated_at = MODIFICADO
    return vestir(fila)
  }

  return {
    filas,
    llamadas,
    manejar,
    /** Makes the next `veces` requests fail with `error`. */
    fallar(error: unknown, veces = 1): void {
      pendiente = { error, veces }
    },
    /** Holds the next list request until `soltar` is called. */
    retener(): void {
      retenida = () => undefined
    },
    soltar(): void {
      const resolver = retenida
      retenida = null
      resolver?.(pagina())
    },
    /** Peticiones de listado recibidas. */
    lecturas(): number {
      return llamadas.filter(llamada => llamada.metodo === 'GET').length
    },
  }
}

type Servidor = ReturnType<typeof crearServidor>

/** Installs the transport and the two Nuxt helpers the screen reaches for. */
function instalarEntorno(servidor: Servidor) {
  const navegar = vi.fn(async () => undefined)
  vi.stubGlobal('$fetch', vi.fn(async (ruta: string, opciones?: Opciones) =>
    await servidor.manejar(ruta, opciones)))
  vi.stubGlobal('navigateTo', navegar)
  vi.stubGlobal('definePageMeta', () => undefined)
  return navegar
}

let montado: VueWrapper | null = null

/**
 * Mounts the screen with a session and a server.
 *
 * @param servidor - Fake API.
 * @param opciones - Login name of the session -null leaves the screen without
 *   one- and language of the interface.
 */
async function montar(
  servidor: Servidor,
  opciones: { usuario?: string | null, idioma?: 'es' | 'en' } = {},
) {
  const navegar = instalarEntorno(servidor)

  const { usuario = 'movalle', idioma = 'es' } = opciones
  if (usuario !== null) {
    useSesion().sesion.value = { usuario, nombre: 'Mariana Ovalle', rol: 'admin' }
  }

  const router = createRouter({
    history: createMemoryHistory(),
    routes: [RUTA_INDICE, ...RUTAS_CONTRATO].map(path => ({
      path,
      component: { template: '<div />' },
    })),
  })
  await router.push(RUTA_ADMINISTRACION)
  await router.isReady()

  const wrapper = mount(Administracion, {
    attachTo: document.body,
    global: {
      plugins: [router, crearI18nDePrueba(idioma)],
      components: { NuxtLink: RouterLink },
      stubs: { Icon: true },
    },
  })
  montado = wrapper
  await flushPromises()

  return { wrapper, navegar }
}

/** The row of one account. */
function fila(wrapper: VueWrapper, username: string) {
  return wrapper.get(`[data-fila-usuario="${username}"]`)
}

/** Confirms whatever the dialog is asking. */
async function confirmar(wrapper: VueWrapper): Promise<void> {
  await wrapper.get('[data-accion="confirmar"]').trigger('click')
  await flushPromises()
}

afterEach(() => {
  montado?.unmount()
  montado = null
  document.body.innerHTML = ''
  vi.unstubAllGlobals()
  vi.useRealTimers()
})

describe('la tabla dibuja lo que el servidor devolvió', () => {
  it('renderiza las siete cuentas en el orden del servidor, con su rol y su estado', async () => {
    const { wrapper } = await montar(crearServidor())

    const filas = wrapper.findAll('[data-fila-usuario]')
    expect(filas).toHaveLength(7)
    expect(filas.map(uno => uno.attributes('data-fila-usuario'))).toEqual(USUARIOS_EN_ORDEN)
    expect(filas.map(uno => uno.get('[data-insignia-rol]').attributes('data-insignia-rol')))
      .toEqual(CUENTAS.map(cuenta => cuenta.role))
    expect(filas.map(uno => uno.get('[data-chip-estado]').attributes('data-chip-estado')))
      .toEqual(Array.from({ length: 7 }, () => 'activo'))
    expect(wrapper.get('[data-estado-panel]').attributes('data-estado-panel')).toBe('listo')
  })

  it('marca como desactivada la cuenta que el servidor devuelve deshabilitada', async () => {
    const cuentas = CUENTAS.map(cuenta =>
      cuenta.username === 'eruiz' ? { ...cuenta, disabled: true } : cuenta)

    const { wrapper } = await montar(crearServidor(cuentas))

    expect(fila(wrapper, 'eruiz').get('[data-chip-estado]').attributes('data-chip-estado'))
      .toBe('desactivado')
    // A disabled account is re-enabled, never disabled again: the last column
    // holds the action that the state of the row allows and no other.
    expect(fila(wrapper, 'eruiz').find('[data-zona="destructiva"]').exists()).toBe(false)
    expect(fila(wrapper, 'eruiz').get('[data-accion-fila]').attributes('data-accion-fila'))
      .toBe('reactivar')
  })

  it('no imprime nada que el cuerpo traiga de más, y el hash es el ejemplo', async () => {
    // The backend never selects the column. This measures the other half: a
    // screen that dumped the raw object into the markup "to debug" would print
    // whatever arrived, and this is what would catch it.
    const servidor = crearServidor(CUENTAS, {
      hashed_password: '$argon2id$v=19$m=65536,t=3,p=4$prueba$prueba',
    })

    const { wrapper } = await montar(servidor)

    expect(wrapper.html()).not.toContain('hashed_password')
    expect(wrapper.html()).not.toContain('$argon2')
  })
})

describe('la fila del administrador conectado', () => {
  it('no ofrece a quien manda el control que lo dejaría fuera', async () => {
    const { wrapper } = await montar(crearServidor())

    expect(fila(wrapper, 'movalle').attributes('data-propia')).toBe('true')
    expect(wrapper.findAll('[data-zona="destructiva"]')).toHaveLength(6)
    expect(wrapper.findAll('[data-selector-rol]')).toHaveLength(6)
    expect(fila(wrapper, 'movalle').find('[data-selector-rol]').exists()).toBe(false)
    expect(fila(wrapper, 'movalle').text()).toContain(mensaje('es', 'admin.users.self.badge'))
    expect(fila(wrapper, 'movalle').text()).toContain(mensaje('es', 'admin.users.self.note'))
    // The role is still readable: what disappears is the control, not the fact.
    expect(fila(wrapper, 'movalle').get('[data-insignia-rol]').attributes('data-insignia-rol'))
      .toBe('admin')
  })

  it('deja la zona destructiva con un solo elemento accionable y ningún control normal', async () => {
    const { wrapper } = await montar(crearServidor())

    for (const zona of wrapper.findAll('[data-zona="destructiva"]')) {
      expect(zona.findAll('button, select, input, a, [tabindex]')).toHaveLength(1)
      expect(zona.find('[data-selector-rol]').exists()).toBe(false)
    }
  })

  it('viste la acción irreversible con la variante destructiva de la guía', async () => {
    const { wrapper } = await montar(crearServidor())

    const clases = wrapper.get('[data-zona="destructiva"] button').classes()
    expect(clases).toContain('border-error')
    expect(clases).toContain('text-error')
  })
})

describe('nada se ejecuta sin confirmación', () => {
  it('desactivar abre el diálogo y no emite ninguna petición hasta confirmar', async () => {
    const servidor = crearServidor()
    const { wrapper } = await montar(servidor)

    await fila(wrapper, 'eruiz').get('[data-accion-fila="desactivar"]').trigger('click')

    const dialogo = wrapper.get('[data-dialogo-confirmacion]')
    expect((dialogo.element as HTMLDialogElement).open).toBe(true)
    expect(dialogo.attributes('data-tono')).toBe('destructivo')
    expect(dialogo.text()).toContain(
      mensaje('es', 'admin.users.confirm.deactivate.body').replace('{name}', 'Elena Ruiz'),
    )
    // One call so far, and it is the list this screen loaded with.
    expect(servidor.llamadas).toHaveLength(1)

    await confirmar(wrapper)

    expect(servidor.llamadas[1]).toMatchObject({ metodo: 'DELETE' })
    expect(servidor.llamadas[1]!.ruta).toContain(CUENTAS[2]!.id)
    expect(fila(wrapper, 'eruiz').get('[data-chip-estado]').attributes('data-chip-estado'))
      .toBe('desactivado')
    expect((wrapper.get('[data-dialogo-confirmacion]').element as HTMLDialogElement).open)
      .toBe(false)
  })

  it('cancelar cierra el diálogo y deja la cuenta como estaba', async () => {
    const servidor = crearServidor()
    const { wrapper } = await montar(servidor)

    await fila(wrapper, 'eruiz').get('[data-accion-fila="desactivar"]').trigger('click')
    await wrapper.get('[data-accion="cancelar"]').trigger('click')
    await flushPromises()

    expect((wrapper.get('[data-dialogo-confirmacion]').element as HTMLDialogElement).open)
      .toBe(false)
    expect(servidor.llamadas).toHaveLength(1)
    expect(fila(wrapper, 'eruiz').get('[data-chip-estado]').attributes('data-chip-estado'))
      .toBe('activo')
  })

  it('elegir un rol devuelve el desplegable a su sitio hasta que el servidor responde', async () => {
    const servidor = crearServidor()
    const { wrapper } = await montar(servidor)

    const selector = fila(wrapper, 'eruiz').get('[data-selector-rol]')
    await selector.setValue('analista')

    // The badge is the confirmed role and the selector went back to it: nothing
    // on screen claims a change that has not happened.
    expect((selector.element as HTMLSelectElement).value).toBe('operativo')
    expect(fila(wrapper, 'eruiz').get('[data-insignia-rol]').attributes('data-insignia-rol'))
      .toBe('operativo')
    const dialogo = wrapper.get('[data-dialogo-confirmacion]')
    expect(dialogo.attributes('data-tono')).toBe('normal')
    expect(dialogo.text()).toContain(mensaje('es', 'authz.role.analista'))
    expect(servidor.llamadas).toHaveLength(1)

    await confirmar(wrapper)

    expect(servidor.llamadas[1]).toMatchObject({ metodo: 'PATCH', cuerpo: { role: 'analista' } })
    expect(fila(wrapper, 'eruiz').get('[data-insignia-rol]').attributes('data-insignia-rol'))
      .toBe('analista')
  })

  it('reactivar viaja como una modificación del campo, no como un endpoint nuevo', async () => {
    const cuentas = CUENTAS.map(cuenta =>
      cuenta.username === 'eruiz' ? { ...cuenta, disabled: true } : cuenta)
    const servidor = crearServidor(cuentas)
    const { wrapper } = await montar(servidor)

    await fila(wrapper, 'eruiz').get('[data-accion-fila="reactivar"]').trigger('click')
    expect(wrapper.get('[data-dialogo-confirmacion]').attributes('data-tono')).toBe('normal')

    await confirmar(wrapper)

    expect(servidor.llamadas[1]).toMatchObject({ metodo: 'PATCH', cuerpo: { disabled: false } })
    expect(fila(wrapper, 'eruiz').get('[data-chip-estado]').attributes('data-chip-estado'))
      .toBe('activo')
  })
})

describe('dónde queda el foco cuando la fila se repinta', () => {
  it('devuelve el foco a la acción de la fila y no a un nodo que ya no está', async () => {
    // El boton que abre el dialogo no sobrevive a lo que abre: al desactivar,
    // la celda cambia de rama y lo sustituye el boton que reactiva. El
    // navegador devuelve el foco al invocador cuando el dialogo se cierra, y
    // para cuando la fila se repinta ese nodo esta desconectado: el foco cae al
    // cuerpo del documento y quien navega con teclado vuelve al principio de la
    // pagina despues de cada accion. Sin la entrega explicita, esta asercion
    // encuentra el foco en el boton de cancelar del dialogo ya cerrado, que es
    // la misma perdida del sitio vista desde happy-dom.
    const servidor = crearServidor()
    const { wrapper } = await montar(servidor)

    const invocador = fila(wrapper, 'eruiz')
      .get('[data-accion-fila="desactivar"]').element as HTMLButtonElement
    invocador.focus()
    await fila(wrapper, 'eruiz').get('[data-accion-fila="desactivar"]').trigger('click')

    await confirmar(wrapper)
    await flushPromises()

    expect(invocador.isConnected).toBe(false)
    expect(document.activeElement)
      .toBe(fila(wrapper, 'eruiz').get('[data-accion-fila="reactivar"]').element)
  })
})

describe('el filtro y su estado vacío', () => {
  it('acota por nombre, por usuario y por correo', async () => {
    const { wrapper } = await montar(crearServidor())

    await wrapper.get('[data-campo-filtro]').setValue('Elena')
    expect(wrapper.findAll('[data-fila-usuario]')).toHaveLength(1)

    await wrapper.get('[data-campo-filtro]').setValue('rvaldez')
    expect(wrapper.findAll('[data-fila-usuario]')).toHaveLength(1)

    await wrapper.get('[data-campo-filtro]').setValue('@karisma.demo')
    expect(wrapper.findAll('[data-fila-usuario]')).toHaveLength(7)
  })

  it('encuentra a quien se escribe con acento aunque el dato llegue sin el', async () => {
    // La migracion que siembra las siete cuentas es ASCII por la regla de
    // `db/AGENTS.md`, y quien administra escribe el apellido como se escribe.
    // Sin la normalizacion del termino -un `toLowerCase()` "que hace lo mismo"-
    // la busqueda natural devuelve el estado vacio para una cuenta que existe,
    // y el estado vacio dice que nadie coincide, no que se busco otra cosa.
    const { wrapper } = await montar(crearServidor())

    await wrapper.get('[data-campo-filtro]').setValue('Hernández')

    expect(wrapper.findAll('[data-fila-usuario]')).toHaveLength(1)
    expect(fila(wrapper, 'dhernandez').text()).toContain('Diego Hernandez')

    await wrapper.get('[data-campo-filtro]').setValue('Castañeda')

    expect(wrapper.findAll('[data-fila-usuario]')).toHaveLength(1)
    expect(fila(wrapper, 'acastaneda').text()).toContain('Arturo Castaneda')
  })

  it('explica la causa y ofrece deshacerla cuando nada coincide', async () => {
    const { wrapper } = await montar(crearServidor())

    await wrapper.get('[data-campo-filtro]').setValue('zzzz')

    expect(wrapper.get('[data-estado-panel]').attributes('data-estado-panel')).toBe('vacio')
    expect(wrapper.text()).toContain(mensaje('es', 'admin.users.state.empty.title'))
    expect(wrapper.text()).toContain(
      mensaje('es', 'admin.users.state.empty.body').replace('{total}', '7'),
    )
    expect(wrapper.findAll('[data-fila-usuario]')).toHaveLength(0)

    await wrapper.get('[data-limpiar-filtro]').trigger('click')

    expect(wrapper.findAll('[data-fila-usuario]')).toHaveLength(7)
    expect(wrapper.get('[data-estado-panel]').attributes('data-estado-panel')).toBe('listo')
  })
})

describe('los dos finales infelices que llegan del servidor', () => {
  it('un fallo de red deja causa y reintento, y el reintento vuelve a pedir', async () => {
    const servidor = crearServidor()
    servidor.fallar(refusal(0))
    const { wrapper } = await montar(servidor)

    expect(wrapper.get('[data-estado-panel]').attributes('data-estado-panel')).toBe('error')
    expect(wrapper.text()).toContain(mensaje('es', 'admin.users.state.error.title'))

    await wrapper.get('[data-reintentar]').trigger('click')
    await flushPromises()

    expect(servidor.lecturas()).toBe(2)
    expect(wrapper.findAll('[data-fila-usuario]')).toHaveLength(7)
  })

  it('un 409 deja la fila intacta y muestra el conflicto que el servidor nombró', async () => {
    // No session in state -a reload that lost it, the guard already let the
    // navigation through- so the interface hides nothing and the request the
    // backend refuses really leaves. This is why the rule lives there and not
    // here: hiding a control is convenience, the 409 is the rule.
    const servidor = crearServidor()
    const { wrapper } = await montar(servidor, { usuario: null })
    servidor.fallar(refusal(409, 'admin_no_puede_desactivarse'))

    await fila(wrapper, 'movalle').get('[data-accion-fila="desactivar"]').trigger('click')
    await confirmar(wrapper)

    expect(wrapper.get('[data-conflicto]').attributes('data-conflicto'))
      .toBe('admin_no_puede_desactivarse')
    expect(wrapper.get('[data-conflicto]').text())
      .toBe(mensaje('es', 'admin.users.conflict.disableSelf'))
    expect(fila(wrapper, 'movalle').get('[data-chip-estado]').attributes('data-chip-estado'))
      .toBe('activo')
    // Refused means refused: nothing was reloaded to paper over the failure.
    expect(servidor.lecturas()).toBe(1)
  })

  it('un 401 termina la sesión una sola vez en lugar de repintar un error', async () => {
    const servidor = crearServidor()
    servidor.fallar(refusal(401, 'sesion_revocada'))

    const { navegar } = await montar(servidor)

    expect(navegar).toHaveBeenCalledTimes(1)
    expect(navegar).toHaveBeenCalledWith(`${RUTA_ACCESO}?motivo=${MOTIVO_EXPIRADA}`)
  })
})

describe('la negativa que llega mientras se ejecuta una accion', () => {
  it('un 401 en la accion tambien termina la sesion, no solo en la carga', async () => {
    // El 401 de la carga ya esta medido; este es el otro sitio donde se atrapa,
    // y es el probable: el panel se queda abierto y la sesion muere debajo. Sin
    // la comprobacion en este `catch` el 401 cae en el estado de error generico
    // y el lector se queda con un reintento que fallara siempre, sin camino de
    // vuelta al acceso.
    const servidor = crearServidor()
    const { wrapper, navegar } = await montar(servidor)
    servidor.fallar(refusal(401, 'sesion_revocada'))

    await fila(wrapper, 'eruiz').get('[data-accion-fila="desactivar"]').trigger('click')
    await confirmar(wrapper)

    expect(navegar).toHaveBeenCalledTimes(1)
    expect(navegar).toHaveBeenCalledWith(`${RUTA_ACCESO}?motivo=${MOTIVO_EXPIRADA}`)
    expect(wrapper.find('[data-conflicto]').exists()).toBe(false)
    expect(servidor.lecturas()).toBe(1)
  })

  it.each([
    ['un codigo que este build no conoce', refusal(409, CODIGO_DESCONOCIDO), CODIGO_DESCONOCIDO],
    ['una negativa sin cuerpo de dominio', refusal(500), 'http 500'],
  ])('%s cae en el estado de error y no se imprime al lector', async (_caso, negativa, crudo) => {
    // `codigoDeConflicto` solo reconoce los tres codigos que el backend publica
    // hoy. Quitar esa lista blanca -o el tipo del `detail`- pone el
    // identificador del backend en la frase del conflicto: el lector recibe
    // `cuota_de_administradores_agotada` o `http 500` en lugar de un estado con
    // accion siguiente. Es alcanzable sin tocar nada: basta con que el backend
    // gane un cuarto codigo antes de que se despliegue esta interfaz.
    const servidor = crearServidor()
    const { wrapper } = await montar(servidor)
    servidor.fallar(negativa)

    await fila(wrapper, 'eruiz').get('[data-accion-fila="desactivar"]').trigger('click')
    await confirmar(wrapper)

    expect(wrapper.find('[data-conflicto]').exists()).toBe(false)
    expect(wrapper.get('[data-estado-panel]').attributes('data-estado-panel')).toBe('error')
    expect(wrapper.get('[data-reintentar]').exists()).toBe(true)
    expect(wrapper.text()).not.toContain(crudo)
    // La tabla sobre la que estaba el lector ya no existe, asi que el foco va a
    // lo unico que queda por hacer aqui y no al principio del documento.
    expect(document.activeElement).toBe(wrapper.get('[data-reintentar]').element)
  })
})

describe('la regla de los 300 milisegundos', () => {
  it('conserva las filas mientras la espera es corta y solo después degrada', async () => {
    vi.useFakeTimers()
    const servidor = crearServidor()
    instalarEntorno(servidor)
    useSesion().sesion.value = { usuario: 'movalle', nombre: 'Mariana Ovalle', rol: 'admin' }

    const panel = useUsuarios()
    await panel.cargar()
    expect(panel.estado.value).toBe('listo')

    servidor.retener()
    const recarga = panel.cargar()

    vi.advanceTimersByTime(RETARDO_ESQUELETO - 100)
    expect(panel.estado.value).toBe('listo')
    expect(panel.usuarios.value).toHaveLength(7)

    vi.advanceTimersByTime(200)
    expect(panel.estado.value).toBe('cargando')

    servidor.soltar()
    await recarga

    expect(panel.estado.value).toBe('listo')
  })

  it('el reintento tras un error degrada de inmediato, sin esperar los 300 ms', async () => {
    // La regla de los 300 ms existe para no parpadear cuando hay filas que
    // conservar, y despues de un fallo no hay ninguna que conservar aunque la
    // lista siga en memoria: lo que la pantalla dibuja es el estado de error.
    // Decidirlo mirando la lista y no la fase deja ese panel de error intacto
    // durante 300 ms despues del clic, y un reintento que no mueve nada es
    // indistinguible de un clic que no llego.
    vi.useFakeTimers()
    const servidor = crearServidor()
    instalarEntorno(servidor)
    useSesion().sesion.value = { usuario: 'movalle', nombre: 'Mariana Ovalle', rol: 'admin' }

    const panel = useUsuarios()
    await panel.cargar()
    expect(panel.estado.value).toBe('listo')

    // Un fallo que no vacia la lista: la accion se rechaza con un error
    // generico, las siete filas siguen en memoria y la pantalla pasa a error.
    servidor.fallar(refusal(500))
    await panel.aplicar({ tipo: 'desactivar', usuario: CUENTAS[2]! })
    expect(panel.estado.value).toBe('error')
    expect(panel.usuarios.value).toHaveLength(7)

    servidor.retener()
    const reintento = panel.cargar()

    expect(panel.estado.value).toBe('cargando')

    servidor.soltar()
    await reintento

    expect(panel.estado.value).toBe('listo')
  })

  it('el esqueleto reserva una fila por cuenta, no un giro de altura propia', async () => {
    const wrapper = mount(AdministracionTablaUsuarios, {
      props: {
        usuarios: [],
        total: 3,
        estado: 'cargando' as const,
        usernamePropio: 'movalle',
        filtro: '',
      },
      global: { plugins: [crearI18nDePrueba()], stubs: { Icon: true } },
    })
    montado = wrapper

    expect(wrapper.findAll('[data-fila-esqueleto]')).toHaveLength(3)
    expect(wrapper.findAll('[data-fila-usuario]')).toHaveLength(0)
    expect(wrapper.get('[data-estado-panel]').attributes('data-estado-panel')).toBe('cargando')
    expect(wrapper.get('[role="status"]').text()).toBe(mensaje('es', 'admin.users.state.loading'))
  })
})

describe('la pantalla habla los dos idiomas', () => {
  it('rotula la acción destructiva en inglés sin cambiar el marcador de la zona', async () => {
    const { wrapper } = await montar(crearServidor(), { idioma: 'en' })

    const boton = wrapper.get('[data-zona="destructiva"] button')
    expect(boton.text()).toBe(mensaje('en', 'admin.users.action.deactivate'))
    expect(boton.text()).not.toBe(mensaje('es', 'admin.users.action.deactivate'))
  })
})
