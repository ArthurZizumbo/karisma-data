import type { VueWrapper } from '@vue/test-utils'
import { mount } from '@vue/test-utils'
import { defineComponent } from 'vue'
import { describe, expect, it } from 'vitest'
import type { RolUsuario } from '~/types/sesion'
import EstadoSinPermiso from '~/components/comun/EstadoSinPermiso.vue'
import { destinoPorRol } from '~/utils/sesion'
import { type CodigoIdioma, crearI18nDePrueba, mensaje } from './i18nDePrueba'

/**
 * US-017 — the fourth unhappy state, which is the one a reader misreads.
 *
 * "Not found" and "something failed" are already understood by everybody. A
 * closed door is not: without the three things asserted below -what is missing,
 * whom to ask and where to go instead- the reader concludes the product is
 * broken and retries, which is exactly what this state must not teach.
 */

const EnlaceStub = defineComponent({
  props: { to: { type: String, required: true } },
  template: '<a :href="to"><slot /></a>',
})

function montar(
  scopeExigido: RolUsuario,
  rolActual: RolUsuario,
  idioma: CodigoIdioma = 'es',
): VueWrapper {
  return mount(EstadoSinPermiso, {
    props: { scopeExigido, rolActual },
    attachTo: document.body,
    global: {
      plugins: [crearI18nDePrueba(idioma)],
      components: { NuxtLink: EnlaceStub },
      stubs: { Icon: true },
    },
  })
}

describe('el estado sin permiso no ofrece reintentar', () => {
  it('no pinta ningun boton ni ningun control de formulario', () => {
    // Retrying a refusal changes nothing: the role is the same on the second
    // press. Offering the button teaches the reader to insist against a door
    // that will not open, and it is the one control this state is forbidden.
    const wrapper = montar('admin', 'operativo')

    expect(wrapper.findAll('button')).toHaveLength(0)
    expect(wrapper.findAll('[type="button"]')).toHaveLength(0)
    expect(wrapper.findAll('input, select, textarea')).toHaveLength(0)
  })

  it('deja un unico elemento accionable, y es la salida al espacio propio', () => {
    // With no way out other than the browser back button, the reader is stuck
    // on a screen that only says no.
    const wrapper = montar('admin', 'analista')
    const accionables = wrapper.findAll('a, button, [tabindex]:not([tabindex="-1"])')

    expect(accionables).toHaveLength(1)
    // Asserted as a CALL and never as a literal path: the landing table belongs
    // to another User Story and is about to change; pinning its values here
    // would make the two contradict each other on the same day.
    expect(accionables[0]?.attributes('href')).toBe(destinoPorRol('analista'))
  })
})

describe('el estado sin permiso explica que falta y a quien pedirlo', () => {
  it.each(['es', 'en'] as const)('dice a quien solicitar el acceso en %s', (idioma) => {
    // Saying "no permission" and staying quiet about who grants it is half a
    // state: it names the wall and hides the door.
    const texto = montar('admin', 'operativo', idioma).text()

    expect(texto).toContain(mensaje(idioma, 'authz.noPermission.requestTo'))
    expect(texto).toContain(mensaje(idioma, 'authz.noPermission.body'))
  })

  it('nombra el perfil exigido y el propio con su etiqueta, no con el scope crudo', () => {
    // Printing `admin` at the reader leaks the vocabulary of the token into the
    // one screen whose whole job is to be understood.
    const texto = montar('admin', 'operativo').text()

    expect(texto).toContain(mensaje('es', 'authz.role.admin'))
    expect(texto).toContain(mensaje('es', 'authz.role.operativo'))
    expect(texto).not.toContain('scopeExigido')
  })

  it('traduce el estado entero, incluida la salida', () => {
    const texto = montar('analista', 'operativo', 'en').text()

    expect(texto).toContain(mensaje('en', 'authz.noPermission.title'))
    expect(texto).toContain(mensaje('en', 'authz.noPermission.exit'))
    expect(texto).not.toContain(mensaje('es', 'authz.noPermission.title'))
  })
})

describe('el estado sin permiso es anunciable y alcanzable', () => {
  it('publica su marca y su rol de region viva', () => {
    // `data-estado` is what the end to end smoke greps for in the served HTML,
    // and `role=status` is what makes a client side navigation audible to a
    // screen reader instead of silently swapping the content.
    const raiz = montar('admin', 'directivo').get('[data-estado]')

    expect(raiz.attributes('data-estado')).toBe('sin-permiso')
    expect(raiz.attributes('role')).toBe('status')
  })

  it('lleva el foco al encabezado al aparecer', () => {
    // Without this the keyboard reader stays on the sidebar link they just
    // pressed and never learns that the screen changed.
    const wrapper = montar('admin', 'operativo')
    const titulo = wrapper.get('h1')

    expect(titulo.attributes('tabindex')).toBe('-1')
    expect(document.activeElement).toBe(titulo.element)

    wrapper.unmount()
  })
})
