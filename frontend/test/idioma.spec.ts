import { mount } from '@vue/test-utils'
import { ref } from 'vue'
import { afterEach, describe, expect, it, vi } from 'vitest'

import SelectorIdioma from '~/components/comun/SelectorIdioma.vue'
import { CLAVE_COOKIE_IDIOMA, IDIOMAS } from '~/composables/useIdioma'
import { clavesDe, crearI18nDePrueba, MENSAJES, mensaje } from './i18nDePrueba'

/**
 * US-UX-09, ola I — the bilingual foundation.
 *
 * Two things can break here and nowhere else: a translation that exists in one
 * catalogue and not in the other, and a language choice that is not remembered.
 * The module is configured with `detectBrowserLanguage: false` precisely so
 * that `accept-language` cannot pick the language of an evaluated demo, which
 * means writing the cookie is application code and has to be tested as such.
 */

function montarSelector(idioma: 'es' | 'en' = 'es') {
  const i18n = crearI18nDePrueba(idioma)
  const cookie = ref<string | null>(null)
  vi.stubGlobal('useCookie', (nombre: string) => {
    expect(nombre).toBe(CLAVE_COOKIE_IDIOMA)
    return cookie
  })

  const wrapper = mount(SelectorIdioma, {
    global: { plugins: [i18n], stubs: { Icon: true } },
  })

  return { wrapper, cookie, i18n }
}

afterEach(() => {
  vi.unstubAllGlobals()
})

describe('los dos catálogos son intercambiables', () => {
  it('declara exactamente el mismo conjunto de claves en español y en inglés', () => {
    // A key present only in es.json falls back to Spanish at runtime, so the
    // English interface degrades silently. This is the assertion that stops it.
    expect(clavesDe('en')).toEqual(clavesDe('es'))
  })

  it('no deja ningún mensaje vacío en ninguno de los dos', () => {
    for (const idioma of ['es', 'en'] as const) {
      for (const clave of clavesDe(idioma)) {
        expect(mensaje(idioma, clave).trim(), `${idioma}:${clave}`).not.toBe('')
      }
    }
  })

  /**
   * A value that is an identifier rather than prose.
   *
   * A dotted module path or an all-caps system code is what the reader types,
   * so translating it would be a defect: `smq.saldo_consolidado` has no English
   * spelling. The shape is checked mechanically instead of enumerating names,
   * because a growing allowlist eventually stops being a check; prose can never
   * satisfy this pattern.
   */
  function esIdentificador(valor: string): boolean {
    return /^[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)+$/.test(valor) || /^[A-Z][A-Z0-9-]{2,}$/.test(valor)
  }

  it('traduce de verdad: solo lo intraducible coincide en los dos idiomas', () => {
    // The failure mode this catches is the cheap one: copying es.json over
    // en.json to make the build pass and leaving the Spanish text in place.
    //
    // Two exceptions are enumerated because they are neither identifiers nor
    // translatable: 'Karisma Data' is a proper name, and 'Error {code}' is
    // spelled the same way in both languages.
    const identicas = clavesDe('es').filter(
      clave =>
        mensaje('es', clave) === mensaje('en', clave)
        && !esIdentificador(mensaje('es', clave)),
    )

    expect(identicas).toEqual(['brand.name', 'error.code'])
  })

  it('conserva los parámetros de interpolación en las dos redacciones', () => {
    // A message that loses its {code} or its {environment} when translated
    // renders a sentence with a hole in it, and nothing else would report it.
    const parametros = (texto: string): string[] =>
      [...texto.matchAll(/\{(\w+)\}/g)].map(coincidencia => coincidencia[1]!).sort()

    for (const clave of clavesDe('es')) {
      expect(parametros(mensaje('en', clave)), clave).toEqual(parametros(mensaje('es', clave)))
    }
  })

  it('declara un catálogo por cada idioma que el selector ofrece', () => {
    expect(Object.keys(MENSAJES).sort()).toEqual(IDIOMAS.map(idioma => idioma.codigo).sort())
  })
})

describe('SelectorIdioma', () => {
  it('ofrece los dos idiomas nombrados en su propio idioma', () => {
    // The endonym is deliberate: a reader who cannot read the language on
    // screen still recognises the option that will rescue them.
    const { wrapper } = montarSelector()
    const botones = wrapper.findAll('[data-idioma]')

    expect(botones).toHaveLength(2)
    expect(botones.map(boton => boton.attributes('data-idioma'))).toEqual(['es', 'en'])
    expect(botones.map(boton => boton.attributes('lang'))).toEqual(['es', 'en'])
  })

  it('marca el idioma activo y describe el otro como una acción', () => {
    const { wrapper } = montarSelector('es')

    expect(wrapper.get('[data-idioma="es"]').attributes('aria-pressed')).toBe('true')
    expect(wrapper.get('[data-idioma="en"]').attributes('aria-pressed')).toBe('false')
    expect(wrapper.get('[data-idioma="en"]').attributes('aria-label')).toBe(
      'Ver la interfaz en English',
    )
  })

  it('rotula el grupo para que el lector de pantalla anuncie de qué se trata', () => {
    const { wrapper } = montarSelector('en')

    expect(wrapper.get('[data-selector-idioma]').attributes('role')).toBe('group')
    expect(wrapper.get('[data-selector-idioma]').attributes('aria-label')).toBe(
      mensaje('en', 'language.groupLabel'),
    )
  })

  it('cambia la interfaz y recuerda la elección al pulsar el otro idioma', async () => {
    const { wrapper, cookie, i18n } = montarSelector('es')

    await wrapper.get('[data-idioma="en"]').trigger('click')

    expect(i18n.global.locale.value).toBe('en')
    expect(cookie.value).toBe('en')
    expect(wrapper.get('[data-idioma="en"]').attributes('aria-pressed')).toBe('true')
  })
})
