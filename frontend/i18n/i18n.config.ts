/**
 * Vue I18n runtime options for Karisma Data.
 *
 * The module scans `<rootDir>/i18n/i18n.config.{js,mjs,ts}` on its own, so the
 * file is picked up without a `vueI18n` entry in nuxt.config.
 *
 * `locale` is deliberately absent: `setupVueI18nOptions` overwrites it with the
 * `defaultLocale` declared in nuxt.config, and writing it twice would let the
 * two drift apart.
 */
export default defineI18nConfig(() => ({
  legacy: false,
  // A key missing from en.json renders its Spanish text instead of the raw key
  // path. A visible untranslated string is a defect a reader reports; a naked
  // `nav.module.home` on screen is one nobody can act on.
  fallbackLocale: 'es',
  // Every message of this project is a literal string: no HTML is interpolated
  // through the catalogue, so the compiler must reject a tag rather than escape
  // it silently.
  warnHtmlMessage: true,
}))
