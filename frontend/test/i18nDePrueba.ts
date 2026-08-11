import type { Composer, I18n } from 'vue-i18n'
import { createI18n } from 'vue-i18n'

import en from '../i18n/locales/en.json'
import es from '../i18n/locales/es.json'

/**
 * The i18n instance the specs install instead of booting Nuxt.
 *
 * Every spec that mounts a component needs one, which is why it lives in a
 * shared module and not copied into each file. The catalogues are the real
 * ones: a test that mounted with invented messages would pass while the
 * shipped translation was missing.
 */

export type CodigoIdioma = 'es' | 'en'

/** The two catalogues exactly as the application ships them. */
export const MENSAJES = { es, en }

/** Composer with the one method @nuxtjs/i18n adds on top of vue-i18n. */
type ComposerConSetLocale = Composer & { setLocale: (codigo: string) => Promise<void> }

/**
 * Builds an i18n instance equivalent to the one the Nuxt module installs.
 *
 * `setLocale` is added by @nuxtjs/i18n to the composer, so the double provides
 * it too: without it, mounting a component that switches the language would
 * fail for a reason unrelated to the component under test.
 *
 * @param idioma - Language the instance starts in.
 * @returns The plugin, ready to be passed to `global.plugins`.
 */
export function crearI18nDePrueba(idioma: CodigoIdioma = 'es'): I18n {
  const i18n = createI18n({
    legacy: false,
    locale: idioma,
    fallbackLocale: 'es',
    messages: MENSAJES,
  })

  const composer = i18n.global as ComposerConSetLocale
  composer.setLocale = async (codigo: string) => {
    composer.locale.value = codigo
  }

  return i18n
}

/**
 * Reads a message of a catalogue by its dotted key, the way a template does.
 *
 * @param idioma - Catalogue to read from.
 * @param clave - Dotted key, for example 'nav.module.home'.
 * @returns The translated string.
 * @throws When the key is absent, so a stale key in a spec fails loudly instead
 *   of comparing against `undefined`.
 */
export function mensaje(idioma: CodigoIdioma, clave: string): string {
  const valor = clave.split('.').reduce<unknown>(
    (nodo, tramo) => (nodo as Record<string, unknown> | undefined)?.[tramo],
    MENSAJES[idioma],
  )
  if (typeof valor !== 'string') {
    throw new Error(`La clave ${clave} no existe en el catalogo ${idioma}`)
  }
  return valor
}

/** Every dotted key of a catalogue, sorted. */
export function clavesDe(idioma: CodigoIdioma): string[] {
  const claves: string[] = []
  const recorrer = (nodo: Record<string, unknown>, prefijo: string): void => {
    for (const [nombre, valor] of Object.entries(nodo)) {
      const clave = prefijo === '' ? nombre : `${prefijo}.${nombre}`
      if (typeof valor === 'string') {
        claves.push(clave)
        continue
      }
      recorrer(valor as Record<string, unknown>, clave)
    }
  }
  recorrer(MENSAJES[idioma] as unknown as Record<string, unknown>, '')
  return claves.sort()
}
