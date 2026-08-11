/**
 * The colour mode and the store that resolves tokens against it.
 *
 * These assertions exist because each one corresponds to a defect that actually
 * happened during the redesign, not because the store needed coverage.
 */
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import { defineComponent, h, nextTick } from 'vue'
import EstadoPendiente from '~/components/comun/EstadoPendiente.vue'
import { useSistemaDiseno } from '~/stores/sistemaDiseno'
import { crearI18nDePrueba } from './i18nDePrueba'

const CSS = readFileSync(resolve(process.cwd(), 'app/assets/css/main.css'), 'utf8')

/** Mount a component that only needs i18n and the globally installed Pinia. */
function montar(componente: Parameters<typeof mount>[0], props: Record<string, unknown> = {}) {
  return mount(componente, {
    props,
    global: {
      plugins: [crearI18nDePrueba('es')],
      stubs: { Icon: true, NuxtLink: true },
    },
  })
}

describe('el store resuelve cada token contra el modo en pantalla', () => {
  it('devuelve el valor claro por omisión y el oscuro cuando el lector lo elige', async () => {
    // The defect: the store printed dark values onto a page still painted light,
    // because the choice and the rendered value came from different places.
    const sistema = useSistemaDiseno()
    const suelo = sistema.porNombre('ground')

    expect(sistema.valor(suelo)).toBe(suelo.claro)

    sistema.elegir('oscuro')
    await nextTick()

    expect(sistema.valor(suelo)).toBe(suelo.oscuro)
  })

  it('cambia la matriz de contraste al cambiar de modo', async () => {
    // A ratio measured over a light ground says nothing about the dark one, so
    // showing the light matrix in dark mode would publish a wrong number.
    const sistema = useSistemaDiseno()
    const enClaro = sistema.contrastes.map(par => par.ratio)

    sistema.elegir('oscuro')
    await nextTick()

    expect(sistema.contrastes.map(par => par.ratio)).not.toEqual(enClaro)
  })

  it('no acepta un nombre de token que no existe', () => {
    // A silent fallback would paint a transparent swatch and read as a design
    // decision instead of as a typo.
    const sistema = useSistemaDiseno()

    expect(() => sistema.porNombre('corriente-inventada')).toThrow(/desconocido/)
  })

  it('no declara ningún incumplimiento en ninguno de los dos modos', async () => {
    const sistema = useSistemaDiseno()

    expect(sistema.incumplimientos).toEqual([])

    sistema.elegir('oscuro')
    await nextTick()

    expect(sistema.incumplimientos).toEqual([])
  })
})

describe('la hoja generada declara el objetivo táctil mínimo', () => {
  it('lo condiciona al tipo de puntero y no al ancho de pantalla', () => {
    // Measured at 375px: 58 controls under 44px, every one of them by height.
    // Fixing them one by one would have left the next one out, so the rule is
    // emitted by the system. It keys on coarse pointers because the rule is
    // about fingers: a mouse at 375px does not need 44px.
    expect(CSS).toContain('@media (pointer: coarse)')
    expect(CSS).toMatch(/min-height:\s*44px/)
    expect(CSS).not.toMatch(/@media \(max-width[^)]*\)\s*\{[^}]*min-height:\s*44px/)
  })

  it('deja que un enlace dentro de un párrafo siga el flujo del texto', () => {
    expect(CSS).toMatch(/p a,\s*\n?\s*\.sr-only \{\s*\n?\s*min-height: revert;/)
  })
})

describe('una pantalla sin contenido declara qué historia lo entrega', () => {
  const Anfitrion = defineComponent({
    setup() {
      return () => h(EstadoPendiente, { capacidades: ['Buscador', 'Favoritos'], us: 'US-027' })
    },
  })

  it('nombra la User Story en vez de dejar la pantalla en blanco', () => {
    // A title over an empty page reads as a screen that failed to load, which is
    // the one reading this deliverable cannot afford.
    const wrapper = montar(Anfitrion)

    expect(wrapper.text()).toContain('US-027')
  })

  it('dibuja un nodo por capacidad', () => {
    const wrapper = montar(Anfitrion)

    expect(wrapper.findAll('[data-capacidad]')).toHaveLength(2)
    expect(wrapper.text()).toContain('Buscador')
  })
})
