import type { VueWrapper } from '@vue/test-utils'
import type { SubrutaNav } from '~/types/navegacion'

import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import { defineComponent } from 'vue'

import AccionesCatalogo from '~/components/exploracion/AccionesCatalogo.vue'
import { useSesion } from '~/composables/useSesion'
import { MODULOS } from '~/utils/navegacion'
import { crearI18nDePrueba, mensaje } from './i18nDePrueba'

/**
 * US-ENTREGA-A4, ola C - the continuation zone when reachability is mixed.
 *
 * `exploracionCatalogo.spec.ts` measures the two pure states of this zone from
 * the screen: an `operativo`, who reaches neither continuation, and an
 * `analista`, who reaches both. That is everything the shipped contract can
 * produce, because branches 2.3 and 2.4 demand the same profile - and it is
 * precisely why the mixed case has to be exercised here, against branches taken
 * from other modules of the same A3 map. A zone that renders its two halves as
 * alternatives passes both of those tests and fails the first reader who can
 * open one door and not the other.
 */

/** Branch every profile below reaches, taken from the contract. */
const ALCANZABLE: SubrutaNav = MODULOS
  .find(modulo => modulo.id === '2')!
  .subrutas.find(subruta => subruta.id === '2.4')!

/** Branch that demands the highest profile, so an analyst cannot open it. */
const CERRADA: SubrutaNav = MODULOS
  .find(modulo => modulo.id === '4')!
  .subrutas.find(subruta => subruta.id === '4.1')!

/** Mounts the zone for an analyst, who reaches one destination of the two. */
function montar(): VueWrapper {
  const { sesion } = useSesion()
  sesion.value = { usuario: 'demo', nombre: 'Perfil de demostracion', rol: 'analista' }

  return mount(AccionesCatalogo, {
    props: { subrutas: [ALCANZABLE, CERRADA] },
    global: {
      plugins: [crearI18nDePrueba('es')],
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

describe('la zona de continuaciones separa lo alcanzable de lo cerrado', () => {
  it('ofrece la puerta abierta y nombra la cerrada en la misma pantalla', () => {
    // The defect: the two halves are written as alternatives -a `v-else`, or a
    // single list with a flag- so the reader either loses the destination they
    // could open or is never told about the one they cannot. Both readings pass
    // the two pure states the screen can reach today.
    const wrapper = montar()

    expect(wrapper.get(`[data-continuacion="${ALCANZABLE.id}"]`).attributes('href'))
      .toBe(ALCANZABLE.ruta)
    expect(wrapper.get(`[data-bloqueada="${CERRADA.id}"]`).text())
      .toContain(mensaje('es', CERRADA.claveEtiqueta))
  })

  it('no pinta la cerrada como enlace, ni siquiera desactivado', () => {
    // The refusal this zone exists for: offering a door that answers with a
    // closed door. A blocked destination rendered as a link -disabled or not-
    // spends a click of the reader to tell them what the zone already says in
    // one line.
    const wrapper = montar()

    expect(wrapper.find(`[data-continuacion="${CERRADA.id}"]`).exists()).toBe(false)
    expect(wrapper.get(`[data-bloqueada="${CERRADA.id}"]`).find('a').exists()).toBe(false)
  })

  it('nombra el perfil que pide la cerrada y no el de la que ya alcanza', () => {
    // The defect: the missing profile is read from the first destination of the
    // list instead of from the first refused one. The zone would then ask the
    // reader to request the profile they are already using, which reads as a
    // screen that refuses without knowing why.
    const wrapper = montar()

    expect(wrapper.get('[data-perfil-faltante]').text())
      .toContain(mensaje('es', 'authz.role.admin'))
    expect(wrapper.get('[data-perfil-faltante]').text())
      .not.toContain(mensaje('es', 'authz.role.analista'))
  })
})
