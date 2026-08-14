import { computed, type ComputedRef } from 'vue'
import { useI18n } from 'vue-i18n'

/**
 * Interface language of Karisma Data.
 *
 * The module is configured with `detectBrowserLanguage: false`, so it neither
 * reads nor writes the cookie: doing so would let `accept-language` decide the
 * language of an evaluated demo on the first visit. Reading and writing the
 * choice is therefore this composable's job, and it is the reason the logic
 * lives here instead of inside the selector component: `app.vue` restores the
 * stored language before the first render and the selector stores it, which is
 * the same rule used twice.
 */

/** Name of the cookie that carries the reader's choice across visits. */
export const CLAVE_COOKIE_IDIOMA = 'karisma_locale'

/** One year in seconds. A language choice does not expire within a semester. */
const VIGENCIA_COOKIE_IDIOMA = 60 * 60 * 24 * 365

/** The two languages of the interface. */
export type CodigoIdioma = 'es' | 'en'

/** One option of the language selector. */
export interface OpcionIdioma {
  /** Locale code, identical to the one declared in nuxt.config. */
  codigo: CodigoIdioma
  /**
   * Endonym: each language names itself. A reader who cannot read the language
   * currently on screen still recognises the option, which is why this string
   * is not translated.
   */
  endonimo: string
  /** Two letter form shown inside the button. */
  abreviatura: string
}

export const IDIOMAS: readonly OpcionIdioma[] = Object.freeze([
  { codigo: 'es', endonimo: 'Español', abreviatura: 'ES' },
  { codigo: 'en', endonimo: 'English', abreviatura: 'EN' },
])

/** Narrows an arbitrary cookie value to a language the interface really has. */
export function esCodigoIdioma(valor: unknown): valor is CodigoIdioma {
  return IDIOMAS.some(idioma => idioma.codigo === valor)
}

/** What the selector and the application shell need from the language state. */
export interface ControlDeIdioma {
  /** Language currently rendered. */
  idiomaActual: ComputedRef<CodigoIdioma>
  /** The two options, in the order they are offered. */
  opciones: readonly OpcionIdioma[]
  /** Switches the interface and remembers the choice for the next visit. */
  cambiarIdioma: (codigo: CodigoIdioma) => Promise<void>
  /** Applies the stored choice. Does nothing when there is none. */
  restaurarIdiomaGuardado: () => Promise<void>
}

/**
 * Reads and writes the interface language.
 *
 * @returns The current language, the available options and the two operations
 *   that change it.
 */
export function useIdioma(): ControlDeIdioma {
  const { locale, setLocale } = useI18n()
  const cookie = useCookie<CodigoIdioma | null>(CLAVE_COOKIE_IDIOMA, {
    path: '/',
    sameSite: 'lax',
    maxAge: VIGENCIA_COOKIE_IDIOMA,
  })

  const idiomaActual = computed<CodigoIdioma>(() =>
    esCodigoIdioma(locale.value) ? locale.value : 'es',
  )

  async function cambiarIdioma(codigo: CodigoIdioma): Promise<void> {
    if (!esCodigoIdioma(codigo)) {
      return
    }
    // The cookie is written first on purpose: if loading the messages of the
    // new language fails, the next visit still opens in the language the
    // reader asked for instead of silently reverting to Spanish.
    cookie.value = codigo
    await setLocale(codigo)
  }

  async function restaurarIdiomaGuardado(): Promise<void> {
    const guardado = cookie.value
    if (!esCodigoIdioma(guardado) || guardado === locale.value) {
      return
    }
    await setLocale(guardado)
  }

  return { idiomaActual, opciones: IDIOMAS, cambiarIdioma, restaurarIdiomaGuardado }
}
