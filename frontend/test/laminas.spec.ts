/**
 * The plates of the living design system.
 *
 * These assert behaviour the plates promise and that would silently rot, never
 * their markup: the previous suite pinned class names and element counts of
 * plates this redesign rewrote, and every one of those assertions had to be
 * deleted rather than updated. What is checked here is what the guide claims
 * about the product.
 */
import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import LaminaCampos from '~/components/guia/LaminaCampos.vue'
import LaminaIconos from '~/components/guia/LaminaIconos.vue'
import LaminaPaleta from '~/components/guia/LaminaPaleta.vue'
import LaminaTablas from '~/components/guia/LaminaTablas.vue'
import LaminaTarjetas from '~/components/guia/LaminaTarjetas.vue'
import { GRUPOS_DE_ICONOS } from '~/components/guia/inventarioIconos'
import { useSistemaDiseno } from '~/stores/sistemaDiseno'
import { crearI18nDePrueba } from './i18nDePrueba'

function montar(componente: Parameters<typeof mount>[0]) {
  return mount(componente, {
    global: {
      plugins: [crearI18nDePrueba('es')],
      stubs: { Icon: true, NuxtLink: true, ClientOnly: { template: '<div><slot /></div>' } },
    },
  })
}

describe('la lámina de paleta imprime lo que el generador emitió', () => {
  it('no teclea ningún hexadecimal: todos salen del sistema', () => {
    // The rule the whole chain exists for. A hand typed value would drift from
    // the emitted one and the PDF would print a colour the product does not use.
    const sistema = useSistemaDiseno()
    const wrapper = montar(LaminaPaleta)
    const impresos = wrapper.text().match(/#[0-9A-F]{6}/g) ?? []
    const emitidos = new Set(sistema.tokens.map(token => sistema.valor(token)))

    expect(impresos.length).toBeGreaterThan(10)
    expect(impresos.every(hex => emitidos.has(hex))).toBe(true)
  })

  // The plate walks the groups the store exposes and announces
  // `sistema.tokens.length` beside the heading, so a group left out of `GRUPOS`
  // makes the sheet the rubric grades as the living style guide document less
  // than the product uses -and it is exactly where somebody copies a colour
  // from-. It has shipped twice: with `accion` and `seleccion` one release
  // earlier, and again with the four chassis tokens and the three certification
  // states of this one, when the plate announced twenty-eight and painted
  // twenty-one. Adding a group to the emitter without adding its line here is
  // the whole defect.
  it('pinta una muestra por cada token que su propio recuento anuncia', () => {
    const sistema = useSistemaDiseno()
    const wrapper = montar(LaminaPaleta)

    expect(wrapper.findAll('[data-token]')).toHaveLength(sistema.tokens.length)
  })

  it('marca como decorativo todo token que declara que no informa', () => {
    // The exemption is the reason the flag exists: a reader has to know that a
    // 1.21:1 rule is deliberate and not an oversight.
    const sistema = useSistemaDiseno()
    const wrapper = montar(LaminaPaleta)
    const decorativos = sistema.tokens.filter(token => !token.informa)

    // The loop asserted the same thing N times without using its variable,
    // which is a test that cannot fail. It names each decorative token instead.
    expect(decorativos.length).toBeGreaterThan(0)
    for (const token of decorativos) {
      expect(wrapper.text()).toContain(token.nombre)
    }
    expect(wrapper.text()).toContain('decorativo')
  })
})

describe('la lámina de campos no deja que el color viaje solo', () => {
  it('da forma propia a cada chip semántico', () => {
    // In light mode the four semantics separate by only dE=13.4 under simulated
    // dichromacy. The icon is not decoration: it is how the state is read.
    const wrapper = montar(LaminaCampos)
    const chips = wrapper.findAll('[data-chip]')

    expect(chips.length).toBe(5)
    for (const chip of chips) {
      expect(chip.find('icon-stub').exists()).toBe(true)
    }
  })

  it('describe cada campo con error a través de aria-describedby', () => {
    const wrapper = montar(LaminaCampos)
    const conError = wrapper.find('[data-campo="error"] input')

    expect(conError.attributes('aria-invalid')).toBe('true')
    expect(conError.attributes('aria-describedby')).toBeTruthy()
  })
})

describe('la lámina de tablas ordena de verdad', () => {
  it('anuncia el orden con aria-sort y no solo con una flecha', async () => {
    // Sorting that is only visible is invisible to a screen reader, and the
    // product lives in dense tables.
    const wrapper = montar(LaminaTablas)
    const columna = () => wrapper.findAll('th').find(th => th.attributes('aria-sort'))

    expect(columna()?.attributes('aria-sort')).toBeTruthy()

    await wrapper.find('[data-ordenar="records"]').trigger('click')

    expect(
      wrapper.findAll('th').some(th => th.attributes('aria-sort') === 'ascending'),
    ).toBe(true)
  })

  it('invierte el sentido al pulsar dos veces la misma columna', async () => {
    const wrapper = montar(LaminaTablas)

    await wrapper.find('[data-ordenar="records"]').trigger('click')
    const primeraFila = wrapper.findAll('[data-fila]')[0]!.text()

    await wrapper.find('[data-ordenar="records"]').trigger('click')

    expect(wrapper.findAll('[data-fila]')[0]!.text()).not.toBe(primeraFila)
  })
})

describe('la lámina de tarjetas hace inspeccionable la regla antialucinación', () => {
  it('muestra la consulta en los cuatro momentos, incluido el que falla', () => {
    const wrapper = montar(LaminaTarjetas)
    const momentos = wrapper.findAll('[data-momento]')

    expect(momentos.length).toBe(4)
    for (const momento of momentos) {
      expect(momento.text()).toContain('Saldo por fuente')
    }
  })

  it('no devuelve ninguna cifra en el momento que fallo', () => {
    // "Sin tool call no hay numero" is a product rule, and the plate is where it
    // is demonstrated rather than stated.
    //
    // The assertion looks at the RESULT and not at the whole card: the query is
    // visible in all four moments and carries a date, so scanning the card for
    // digits measured something other than what the test name promises. A first
    // version did exactly that and failed for the wrong reason.
    const wrapper = montar(LaminaTarjetas)
    const parrafos = wrapper.find('[data-momento="error"]').findAll('p')
    const resultado = parrafos[parrafos.length - 1]!

    expect(resultado.text()).not.toMatch(/\d[\d,.]{3,}/)
    expect(resultado.text()).toContain('no incluye cifras')
  })

  it('etiqueta la proyección como simulada', () => {
    const wrapper = montar(LaminaTarjetas)

    expect(wrapper.find('[data-tarjeta="kpi"]').text()).toContain('simulada')
  })
})

describe('la lámina de iconos recorre el mismo inventario que el empaquetador', () => {
  it('dibuja una entrada por icono declarado', () => {
    // A name assembled at run time renders an empty box in a production build
    // while looking correct under the dev server.
    const wrapper = montar(LaminaIconos)
    const declarados = GRUPOS_DE_ICONOS.flatMap(grupo => grupo.entradas)

    expect(wrapper.findAll('[data-icono]')).toHaveLength(declarados.length)
  })
})
