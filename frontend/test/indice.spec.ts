import { mount } from '@vue/test-utils'
import { defineComponent } from 'vue'
import { describe, expect, it } from 'vitest'
import Indice from '~/pages/index.vue'
import { PROTOTIPOS, RUTAS_CONTRATO } from '~/utils/navegacion'
import { type CodigoIdioma, crearI18nDePrueba, mensaje } from './i18nDePrueba'

const EnlaceStub = defineComponent({
  props: { to: { type: String, required: true } },
  template: '<a :href="to"><slot /></a>',
})

function montarIndice(idioma: CodigoIdioma = 'es') {
  return mount(Indice, {
    global: {
      plugins: [crearI18nDePrueba(idioma)],
      components: { NuxtLink: EnlaceStub },
    },
  })
}

describe('índice de prototipos en /', () => {
  it('muestra siete botones de prototipo', () => {
    expect(montarIndice().findAll('[data-prototipo]')).toHaveLength(7)
  })

  it('acompaña cada botón de una etiqueta de alcance no vacía', () => {
    const botones = montarIndice().findAll('[data-prototipo]')

    expect(botones).toHaveLength(7)
    for (const boton of botones) {
      const alcance = boton.attributes('data-alcance')
      expect(alcance).toBeDefined()
      expect(alcance).not.toBe('')
    }
  })

  // The defect: the index paints `data-alcance` from a literal of its own instead
  // of reading `PROTOTIPOS`, so a scope corrected in the contract keeps being
  // advertised with its old value on the one surface an evaluator lands on first.
  // The previous form of this test pinned the seven US-001 values instead, which
  // turned a contract check into a snapshot of a moment: it went red when US
  // ENTREGA-A4 corrected six scopes in `navegacion.ts`, with nothing broken.
  it('publica en cada botón el alcance que declara el contrato', () => {
    const alcances = montarIndice()
      .findAll('[data-prototipo]')
      .map(boton => boton.attributes('data-alcance'))

    expect(alcances).toEqual(PROTOTIPOS.map(prototipo => prototipo.alcance))
  })

  it('enlaza cada botón a una ruta del contrato', () => {
    const destinos = montarIndice()
      .findAll('[data-prototipo]')
      .map(boton => boton.attributes('href'))

    expect(destinos).toEqual(PROTOTIPOS.map(prototipo => prototipo.ruta))
    for (const destino of destinos) {
      expect(RUTAS_CONTRATO).toContain(destino)
    }
  })

  it('muestra el nombre, la rama de A3 y el perfil sugerido de cada prototipo', () => {
    const texto = montarIndice().text()

    for (const prototipo of PROTOTIPOS) {
      expect(texto).toContain(mensaje('es', prototipo.claveNombre))
      expect(texto).toContain(mensaje('es', prototipo.claveRama))
    }
    expect(texto).toContain('Navegable sin datos')
    expect(texto).toContain('Perfil operativo')
  })

  it('traduce el índice completo cuando la interfaz está en inglés', () => {
    // The index is the screen with the most text that does not come from a page
    // file: names, A3 branches, scope labels and profiles all travel through the
    // navigation contract. If any of them had kept a Spanish literal, it would
    // surface here and nowhere else.
    const texto = montarIndice('en').text()

    for (const prototipo of PROTOTIPOS) {
      expect(texto).toContain(mensaje('en', prototipo.claveNombre))
      expect(texto).toContain(mensaje('en', prototipo.claveRama))
    }
    expect(texto).toContain('Navigable without data')
    expect(texto).toContain('Operations profile')
    expect(texto).not.toContain('Navegable sin datos')
  })
})
