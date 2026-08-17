import type { VueWrapper } from '@vue/test-utils'
import type { Router } from 'vue-router'

import { flushPromises, mount } from '@vue/test-utils'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { defineComponent } from 'vue'
import { createMemoryHistory, createRouter, RouterLink } from 'vue-router'

import SelectorRol from '~/components/comun/SelectorRol.vue'
import BotonPrototipo from '~/components/nav/BotonPrototipo.vue'
import Acceso from '~/pages/acceso.vue'
import type { RolUsuario } from '~/types/sesion'
import { MOTIVO_SESION_REQUERIDA, PARAMETRO_DESTINO } from '~/utils/guarda'
import { PROTOTIPOS, RUTA_ACCESO } from '~/utils/navegacion'
import { destinoPorRol, ROLES } from '~/utils/sesion'
import { crearI18nDePrueba, mensaje } from './i18nDePrueba'

/**
 * US-ENTREGA-A4, ola B - changing profile from the chrome.
 *
 * The two defects this file exists for are the ones that would leave the demo
 * looking right and being wrong: a role switched in the browser, which leaves
 * the guard of the server deciding with the old token, and a demonstration
 * control shipped to a deployment whose door is closed, where every click
 * answers 404.
 */

/** Requests the doubled Nitro layer saw, in order. */
let peticiones: { ruta: string, metodo: unknown, cuerpo: unknown }[]

/** Navigations the component asked for. */
let navegaciones: unknown[]

/** How the doubled `/api/auth/demo` answers. */
let responder: (cuerpo: unknown) => Promise<unknown>

let router: Router

/** Session body of a role, shaped as `POST /api/auth/demo` answers it. */
function sesionDe(rol: RolUsuario): Record<string, string> {
  return { usuario: 'demo', nombre: 'Perfil de demostracion', rol }
}

beforeEach(async () => {
  peticiones = []
  navegaciones = []
  responder = cuerpo => Promise.resolve(sesionDe((cuerpo as { rol: RolUsuario }).rol))

  router = createRouter({
    history: createMemoryHistory(),
    routes: ['/inicio', '/administracion', '/exploracion', '/gobierno', RUTA_ACCESO].map(path => ({
      path,
      component: defineComponent({ template: '<div />' }),
    })),
  })
  await router.push('/inicio')
  await router.isReady()

  vi.stubGlobal('navigateTo', (destino: unknown) => {
    navegaciones.push(destino)
    return Promise.resolve()
  })
  vi.stubGlobal('$fetch', (ruta: string, opciones: { method?: unknown, body?: unknown } = {}) => {
    peticiones.push({ ruta, metodo: opciones.method, cuerpo: opciones.body })
    return responder(opciones.body)
  })
})

afterEach(() => {
  vi.unstubAllGlobals()
})

/** Mounts the control with the demonstration flag in a given position. */
function montarSelector(demoAcceso: boolean, idioma: 'es' | 'en' = 'es'): VueWrapper {
  vi.stubGlobal('useRuntimeConfig', () => ({ public: { entorno: 'prueba', demoAcceso } }))

  return mount(SelectorRol, {
    global: { plugins: [router, crearI18nDePrueba(idioma)], stubs: { Icon: true } },
  })
}

describe('el cambio de perfil acuna una sesion real', () => {
  it('ofrece los cuatro perfiles del contrato de identidad', () => {
    const perfiles = montarSelector(true)
      .findAll('[data-rol-demo]')
      .map(boton => boton.attributes('data-rol-demo'))

    expect(perfiles).toEqual([...ROLES])
  })

  it('llama a POST /api/auth/demo al elegir un perfil', async () => {
    // The defect: the role is switched in client state, the cookie keeps the
    // old token and the guard of the server goes on deciding with it. Nothing
    // on screen would look different until a data call answered 403.
    const wrapper = montarSelector(true)

    await wrapper.get('[data-rol-demo="analista"]').trigger('click')
    await flushPromises()

    expect(peticiones).toEqual([
      { ruta: '/api/auth/demo', metodo: 'POST', cuerpo: { rol: 'analista' } },
    ])
  })

  it('marca el perfil que la sesion abrio, y solo despues de abrirla', async () => {
    const wrapper = montarSelector(true)

    expect(wrapper.findAll('[aria-pressed="true"]')).toHaveLength(0)

    await wrapper.get('[data-rol-demo="directivo"]').trigger('click')
    await flushPromises()

    const marcados = wrapper
      .findAll('[data-rol-demo]')
      .filter(boton => boton.attributes('aria-pressed') === 'true')

    expect(marcados.map(boton => boton.attributes('data-rol-demo'))).toEqual(['directivo'])
  })

  it('no deja pintada una pantalla que el perfil nuevo no alcanza', async () => {
    // The guard decides on the server, so the reader is moved to the space of
    // the profile they just opened instead of standing on a screen that would
    // answer 403 at the first request.
    await router.push('/administracion')
    const wrapper = montarSelector(true)

    await wrapper.get('[data-rol-demo="operativo"]').trigger('click')
    await flushPromises()

    expect(navegaciones).toEqual([destinoPorRol('operativo')])
  })

  it('no mueve a nadie cuando el perfil nuevo alcanza la pantalla actual', async () => {
    const wrapper = montarSelector(true)

    await wrapper.get('[data-rol-demo="analista"]').trigger('click')
    await flushPromises()

    expect(navegaciones).toEqual([])
  })

  it('no cambia el rol cuando la puerta del backend responde 404', async () => {
    // Without this the interface would show a profile the token does not
    // carry, which is the exact lie the server side guard exists to prevent.
    responder = () => Promise.reject(Object.assign(new Error('sin puerta'), { status: 404 }))
    const wrapper = montarSelector(true)

    await wrapper.get('[data-rol-demo="admin"]').trigger('click')
    await flushPromises()

    expect(wrapper.findAll('[aria-pressed="true"]')).toHaveLength(0)
    expect(navegaciones).toEqual([])
    expect(wrapper.get('[data-fallo-rol]').text()).toBe(
      mensaje('es', 'access.errors.demoDisabled'),
    )
  })
})

describe('sin la bandera de demostracion el control no existe', () => {
  it('no pinta nada cuando la puerta esta apagada', () => {
    // The defect: the switch travels to an environment where the door is shut
    // and offers four buttons that can only answer 404.
    const wrapper = montarSelector(false)

    expect(wrapper.find('[data-selector-rol]').exists()).toBe(false)
    expect(wrapper.findAll('[data-rol-demo]')).toHaveLength(0)
  })

  it('nombra los perfiles por catalogo en los dos idiomas', () => {
    const enEspanol = montarSelector(true, 'es').text()
    const enIngles = montarSelector(true, 'en').text()

    for (const rol of ROLES) {
      expect(enEspanol).toContain(mensaje('es', `authz.role.${rol}`))
      expect(enIngles).toContain(mensaje('en', `authz.role.${rol}`))
    }
  })
})

describe('la tarjeta del indice entra con el perfil que declara', () => {
  /** Prototype whose profile is not the most general one, so the role shows. */
  const TARJETA = PROTOTIPOS.find(prototipo => prototipo.rolSugerido === 'admin')!

  function montarTarjeta(demoAcceso: boolean): VueWrapper {
    vi.stubGlobal('useRuntimeConfig', () => ({ public: { entorno: 'prueba', demoAcceso } }))

    return mount(BotonPrototipo, {
      props: { prototipo: TARJETA },
      global: {
        plugins: [router, crearI18nDePrueba('es')],
        stubs: { Icon: true },
        components: {
          NuxtLink: defineComponent({
            props: { to: { type: String, required: true } },
            template: '<a :href="to"><slot /></a>',
          }),
        },
      },
    })
  }

  it('acuna la sesion de su perfil y aterriza dentro de la pantalla', async () => {
    // The defect: one click from the index lands on the entry form. The index
    // is the surface the evaluator opens first, and a prototype that asks for a
    // password before showing anything is read as one that does not work.
    const wrapper = montarTarjeta(true)

    await wrapper.get('[data-prototipo]').trigger('click')
    await flushPromises()

    expect(peticiones).toEqual([
      { ruta: '/api/auth/demo', metodo: 'POST', cuerpo: { rol: TARJETA.rolSugerido } },
    ])
    expect(navegaciones).toEqual([TARJETA.ruta])
  })

  /**
   * Mounts the card with the REAL `RouterLink`, not the inert stub.
   *
   * The stub the other cases use is an `<a>` that does nothing on click, and
   * that is precisely the blind spot this case exists to cover: the component
   * ships inside a `NuxtLink`, whose own click handler calls
   * `preventDefault()`. Against the stub every ordering works. Against the real
   * link only one does.
   */
  function montarTarjetaConEnlaceReal(): VueWrapper {
    vi.stubGlobal('useRuntimeConfig', () => ({ public: { entorno: 'prueba', demoAcceso: true } }))

    return mount(BotonPrototipo, {
      props: { prototipo: TARJETA },
      global: {
        plugins: [router, crearI18nDePrueba('es')],
        stubs: { Icon: true },
        // `NuxtLink` is a Nuxt auto import and does not exist here. Left
        // unregistered it renders as an unknown element with no behaviour, and
        // the case would pass without exercising anything. `RouterLink` is what
        // `NuxtLink` delegates the click to, so it is the piece under test.
        components: { NuxtLink: RouterLink },
      },
    })
  }

  it('acuna la sesion aunque el enlace real prevenga el clic primero', async () => {
    // The defect, and it shipped: bound as a plain `@click`, this handler runs
    // AFTER the one vue-router puts on the anchor, which has already called
    // `preventDefault()`. A guard on `evento.defaultPrevented` then reads its
    // own link as someone else's decision, returns, and the card degrades into
    // the bare link it used to be -no session minted, reader on the entry form-
    // while every unit case stayed green, because the stubbed `NuxtLink` never
    // prevented anything. Verified against a live portal before being written.
    //
    // The click lands on a descendant of the anchor on purpose: that is where a
    // reader clicks, and it makes the anchor a true ancestor, so the capture
    // pass is unambiguously before the bubbling one.
    const wrapper = montarTarjetaConEnlaceReal()

    await wrapper.get('[data-prototipo] span').trigger('click')
    await flushPromises()

    expect(peticiones).toEqual([
      { ruta: '/api/auth/demo', metodo: 'POST', cuerpo: { rol: TARJETA.rolSugerido } },
    ])
    expect(navegaciones).toEqual([TARJETA.ruta])
  })

  it('deja pasar el clic con modificador tambien con el enlace real', async () => {
    // The other half of the same ordering: running first must not mean running
    // always. A modified click has to reach the browser untouched, and vue
    // router skips it by the same rule, so neither of the two moves the reader.
    const wrapper = montarTarjetaConEnlaceReal()

    await wrapper.get('[data-prototipo] span').trigger('click', { ctrlKey: true })
    await flushPromises()

    expect(peticiones).toEqual([])
    expect(navegaciones).toEqual([])
  })

  it('navega como siempre cuando la puerta de demostracion esta apagada', async () => {
    // Without the flag the card is the link it always was: the guard bounces,
    // and the entry screen now says why and takes the reader back.
    const wrapper = montarTarjeta(false)

    await wrapper.get('[data-prototipo]').trigger('click')
    await flushPromises()

    expect(peticiones).toEqual([])
    expect(navegaciones).toEqual([])
    expect(wrapper.get('[data-prototipo]').attributes('href')).toBe(TARJETA.ruta)
  })

  it('no se queda con un clic que pedia otra pestana', async () => {
    // Intercepting a modified click takes away the only way to read seven
    // prototypes side by side.
    const wrapper = montarTarjeta(true)

    await wrapper.get('[data-prototipo]').trigger('click', { ctrlKey: true })
    await flushPromises()

    expect(peticiones).toEqual([])
    expect(navegaciones).toEqual([])
  })

  /**
   * The rest of the ways a reader asks for a new tab.
   *
   * `ctrlKey` has its own case above; the middle button is not a modifier at
   * all but a different button, and the card has to leave it alone for exactly
   * the same reason.
   */
  const EN_PESTANA_NUEVA: [string, Record<string, unknown>][] = [
    ['con Meta, que es como se pide en macOS', { metaKey: true }],
    ['con Shift, que la abre en una ventana aparte', { shiftKey: true }],
    ['con Alt, que el navegador resuelve a su manera', { altKey: true }],
    ['con el boton central del raton', { button: 1 }],
  ]

  it.each(EN_PESTANA_NUEVA)('tampoco se queda con el clic %s', async (caso, gesto) => {
    // The same defect as the Ctrl case above and the same cost, only spread
    // over the readers the Ctrl case does not cover: an interception that
    // spared Ctrl alone would still take the seven parallel tabs away from
    // everyone on macOS and from anyone who opens links with the middle button.
    // Reading the index side by side is how the seven prototypes get compared.
    const wrapper = montarTarjeta(true)

    await wrapper.get('[data-prototipo]').trigger('click', gesto)
    await flushPromises()

    expect(peticiones, caso).toEqual([])
    expect(navegaciones, caso).toEqual([])
    expect(wrapper.get('[data-prototipo]').attributes('href'), caso).toBe(TARJETA.ruta)
  })

  it('manda al acceso con el destino cuando la puerta responde 404', async () => {
    // The fallback is the bounce of the guard, written by hand because the card
    // never reached it: the reader is handed the entry screen with the screen
    // they asked for, not a bare form.
    responder = () => Promise.reject(Object.assign(new Error('sin puerta'), { status: 404 }))
    const wrapper = montarTarjeta(true)

    await wrapper.get('[data-prototipo]').trigger('click')
    await flushPromises()

    expect(navegaciones).toEqual([
      {
        path: RUTA_ACCESO,
        query: { [PARAMETRO_DESTINO]: TARJETA.ruta, motivo: MOTIVO_SESION_REQUERIDA },
      },
    ])
  })
})

describe('la entrada en frio devuelve a la pantalla que se pidio', () => {
  async function montarAcceso(
    demoAcceso: boolean,
    consulta: Record<string, string> = {},
  ): Promise<VueWrapper> {
    vi.stubGlobal('definePageMeta', () => undefined)
    vi.stubGlobal('useRuntimeConfig', () => ({ public: { entorno: 'prueba', demoAcceso } }))
    await router.push({ path: RUTA_ACCESO, query: consulta })
    await router.isReady()

    return mount(Acceso, {
      global: {
        plugins: [router, crearI18nDePrueba('es')],
        stubs: { Icon: true },
        components: {
          NuxtLink: defineComponent({
            props: { to: { type: String, required: true } },
            template: '<a :href="to"><slot /></a>',
          }),
        },
      },
    })
  }

  /** True when the demonstration block is written before the form. */
  function perfilesAntesDelFormulario(wrapper: VueWrapper): boolean {
    const marcado = wrapper.html()
    return marcado.indexOf('data-demostracion') < marcado.indexOf('<form')
  }

  it('pone los cuatro perfiles antes del formulario con la puerta abierta', async () => {
    // The defect: whoever bounced here from a prototype has no password, and a
    // credential form on top tells them to look for one that does not exist.
    const wrapper = await montarAcceso(true)

    expect(wrapper.findAll('[data-rol]')).toHaveLength(4)
    expect(perfilesAntesDelFormulario(wrapper)).toBe(true)
  })

  it('conserva la pantalla de siempre con la puerta cerrada', async () => {
    const wrapper = await montarAcceso(false)

    expect(wrapper.find('[data-demostracion]').exists()).toBe(false)
    expect(wrapper.find('form').exists()).toBe(true)
  })

  it('declara que abre cada perfil, y no solo su nombre', async () => {
    const wrapper = await montarAcceso(true)

    expect(wrapper.findAll('[data-abre]')).toHaveLength(4)
    expect(wrapper.get('[data-rol="admin"]').text()).toContain(
      mensaje('es', 'roleSwitch.opens.admin'),
    )
  })

  it('dice por que reboto y nombra la pantalla que se pedia', async () => {
    // A mute bounce is what makes an evaluator conclude that the prototype does
    // not open. The screen is named from the navigation contract, never typed.
    const wrapper = await montarAcceso(true, {
      destino: '/gobierno',
      motivo: MOTIVO_SESION_REQUERIDA,
    })

    expect(wrapper.get('[data-aviso="sesion-requerida"]').text()).toContain(
      mensaje('es', 'nav.module.governance'),
    )
  })

  it('aterriza en la ruta pedida cuando el perfil elegido la alcanza', async () => {
    const wrapper = await montarAcceso(true, {
      destino: '/gobierno',
      motivo: MOTIVO_SESION_REQUERIDA,
    })

    await wrapper.get('[data-rol="analista"]').trigger('click')
    await flushPromises()

    expect(navegaciones).toEqual(['/gobierno'])
  })

  it('no navega a un destino que el contrato no publica', async () => {
    // An arbitrary value in the query string is an open redirect that any link
    // can drive, so it is dropped and the profile lands in its own space.
    const wrapper = await montarAcceso(true, {
      destino: 'https://evil.example/robo',
      motivo: MOTIVO_SESION_REQUERIDA,
    })

    await wrapper.get('[data-rol="analista"]').trigger('click')
    await flushPromises()

    expect(navegaciones).toEqual([destinoPorRol('analista')])
  })

  it('dice el desvio en vez de mover a nadie a una pantalla prohibida', async () => {
    // The reader asked for a screen their new profile cannot open. Landing
    // somewhere else in silence is the same mute bounce, one step later.
    const wrapper = await montarAcceso(true, {
      destino: '/administracion',
      motivo: MOTIVO_SESION_REQUERIDA,
    })

    await wrapper.get('[data-rol="operativo"]').trigger('click')
    await flushPromises()

    const desvio = wrapper.get('[data-aviso="desviado"]')

    expect(navegaciones).toEqual([])
    expect(desvio.text()).toContain(mensaje('es', 'authz.role.admin'))
    expect(desvio.get('[data-accion="ir-a-mi-espacio"]').attributes('href')).toBe(
      destinoPorRol('operativo'),
    )
  })
})
