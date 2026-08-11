import { mount } from '@vue/test-utils'
import { defineComponent } from 'vue'
import { describe, expect, it } from 'vitest'
import Indice from '~/pages/index.vue'
import { PROTOTIPOS, RUTAS_CONTRATO } from '~/utils/navegacion'

const EnlaceStub = defineComponent({
  props: { to: { type: String, required: true } },
  template: '<a :href="to"><slot /></a>',
})

function montarIndice() {
  return mount(Indice, {
    global: { components: { NuxtLink: EnlaceStub } },
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

  it('declara los siete botones como navegables sin datos al cerrar US-001', () => {
    const alcances = montarIndice()
      .findAll('[data-prototipo]')
      .map(boton => boton.attributes('data-alcance'))

    expect(alcances).toEqual(Array.from({ length: 7 }, () => 'navegable-sin-datos'))
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
      expect(texto).toContain(prototipo.nombre)
      expect(texto).toContain(prototipo.ramaA3)
    }
    expect(texto).toContain('Navegable sin datos')
    expect(texto).toContain('Perfil operativo')
  })
})
