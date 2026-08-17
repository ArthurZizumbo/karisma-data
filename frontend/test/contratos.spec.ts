import { readFileSync, readdirSync } from 'node:fs'
import { join, relative } from 'node:path'
import { fileURLToPath } from 'node:url'

import { describe, expect, it } from 'vitest'

import { type CodigoIdioma, clavesDe, mensaje } from './i18nDePrueba'

/**
 * US-UX-09 — the two contracts that cross a wave boundary.
 *
 * Everything else in this suite checks one artefact against itself. These two
 * checks compare artefacts that different waves wrote and that nothing links at
 * build time:
 *
 * 1. A template writes `bg-primary-400`, the generator never emitted that step,
 *    Tailwind emits no rule and the element paints with no colour at all. The
 *    build succeeds, every other spec stays green and the divergence between
 *    the interface and the PDF only shows up in the screenshot.
 * 2. A template asks for a catalogue key that nobody wrote. vue-i18n prints the
 *    dotted key as visible text, in both languages, and only the screens with
 *    an explicit assertion on that exact string would notice.
 *
 * Both scans read the shipped sources, never a copy typed into the spec.
 */

/**
 * Resolves a path of the repository.
 *
 * The path arrives as a variable on purpose: with a literal, Vite rewrites the
 * `new URL(..., import.meta.url)` pattern into an asset reference and the URL
 * stops being a file one.
 */
function rutaDelRepositorio(relativa: string): string {
  return fileURLToPath(new URL(relativa, import.meta.url))
}

const RAIZ_APP = rutaDelRepositorio('../app')
const RUTA_TEMA = rutaDelRepositorio('../app/assets/css/main.css')

/** Every `.vue` and `.ts` file the application ships, with its relative path. */
function fuentesDeLaAplicacion(): { archivo: string, texto: string }[] {
  const recorrer = (directorio: string): string[] =>
    readdirSync(directorio, { withFileTypes: true }).flatMap(entrada =>
      entrada.isDirectory()
        ? recorrer(join(directorio, entrada.name))
        : [join(directorio, entrada.name)],
    )

  return recorrer(RAIZ_APP)
    .filter(ruta => /\.(vue|ts)$/.test(ruta))
    .map(ruta => ({
      archivo: relative(RAIZ_APP, ruta).replace(/\\/g, '/'),
      texto: readFileSync(ruta, 'utf8'),
    }))
}

const FUENTES = fuentesDeLaAplicacion()

/**
 * Token names declared in the generated `@theme`, grouped by namespace.
 *
 * The compound declarations of the typographic scale
 * (`--text-titulo-1--line-height`) are modifiers of a role, not roles, so they
 * are dropped: only the name a utility class can name is kept.
 */
function tokensDeclarados(): Map<string, Set<string>> {
  const tema = readFileSync(RUTA_TEMA, 'utf8')
  const espacios = new Map<string, Set<string>>()

  for (const [, espacio, nombre] of tema.matchAll(
    /^\s+--(color|text|radius|shadow|font|breakpoint)-([a-z0-9-]+)\s*:/gm,
  )) {
    if (nombre!.includes('--')) {
      continue
    }
    const declarados = espacios.get(espacio!) ?? new Set<string>()
    declarados.add(nombre!)
    espacios.set(espacio!, declarados)
  }

  return espacios
}

const TOKENS = tokensDeclarados()

/** Namespaces a utility prefix can read from, in the order Tailwind resolves. */
const ESPACIOS_POR_PREFIJO: Record<string, string[]> = {
  bg: ['color'],
  text: ['color', 'text'],
  border: ['color'],
  outline: ['color'],
  ring: ['color'],
  divide: ['color'],
  fill: ['color'],
  stroke: ['color'],
  from: ['color'],
  via: ['color'],
  to: ['color'],
  placeholder: ['color'],
  caret: ['color'],
  decoration: ['color'],
  shadow: ['shadow', 'color'],
  rounded: ['radius'],
  font: ['font'],
}

/** Side suffixes Tailwind allows between the prefix and the token name. */
const LADOS = /^(t|b|l|r|x|y|s|e|tl|tr|bl|br|ss|se|es|ee)-/

/**
 * First segment of every declared name, per namespace.
 *
 * This is what makes the check safe to run over utilities the design system
 * does not own: `text-sm` and `rounded-xl` resolve against Tailwind's own
 * defaults, their head is not a name this system declares, and they are left
 * alone. `text-titulo-4` and `bg-serie-7` do have a declared head, so an
 * undeclared tail is a broken class and not a default.
 */
const CABEZAS = new Map(
  [...TOKENS].map(([espacio, nombres]) => [
    espacio,
    new Set([...nombres].map(nombre => nombre.split('-')[0]!)),
  ]),
)

interface ClaseInspeccionada {
  readonly archivo: string
  readonly clase: string
  readonly espacios: string[]
  readonly nombre: string
}

/**
 * Utility classes written in the sources that name a token of this system.
 *
 * Variants (`hover:`, `focus-visible:`, `md:`), the important marker and the
 * opacity modifier are stripped, because none of them changes which token the
 * utility resolves against.
 */
function clasesDeToken(): ClaseInspeccionada[] {
  const inspeccionadas: ClaseInspeccionada[] = []

  for (const { archivo, texto } of FUENTES) {
    for (const bruta of new Set(texto.split(/[\s"'`{}()[\],;]+/))) {
      const utilidad = bruta.slice(bruta.lastIndexOf(':') + 1).replace(/^!/, '').split('/')[0]!
      const guion = utilidad.indexOf('-')
      if (guion < 1) {
        continue
      }

      const prefijo = utilidad.slice(0, guion)
      const espacios = ESPACIOS_POR_PREFIJO[prefijo]
      if (espacios === undefined) {
        continue
      }

      const nombre = utilidad.slice(guion + 1).replace(LADOS, '')
      const cabeza = nombre.split('-')[0]!
      if (!espacios.some(espacio => CABEZAS.get(espacio)?.has(cabeza) ?? false)) {
        continue
      }

      inspeccionadas.push({ archivo, clase: utilidad, espacios, nombre })
    }
  }

  return inspeccionadas
}

describe('el @theme generado cubre toda clase de token que la interfaz escribe', () => {
  it('declara cada token que una plantilla nombra', () => {
    const inspeccionadas = clasesDeToken()
    const huerfanas = inspeccionadas.filter(
      ({ espacios, nombre }) =>
        !espacios.some(espacio => TOKENS.get(espacio)?.has(nombre) ?? false),
    )

    // Without these two floors the assertion above would also pass over an
    // empty scan, which is the way a check like this rots without a sound.
    //
    // The colour floor was 30 while the theme carried 37 compatibility aliases
    // of US-001 on top of the real tokens. Those aliases were retired once no
    // template referenced them, so the floor now sits under the real count: it
    // still catches an empty scan and no longer measures scaffolding.
    expect(TOKENS.get('color')!.size).toBeGreaterThan(12)
    expect(inspeccionadas.length).toBeGreaterThan(50)
    expect(huerfanas.map(({ archivo, clase }) => `${archivo}: ${clase}`)).toEqual([])
  })
})

describe('ninguna plantilla pide una cadena que los catálogos no tengan', () => {
  /** Dotted keys named as literals: in a `t('...')` call or in a data module. */
  function clavesUsadas(): Map<string, string> {
    const patrones = [
      /(?:\$t|\bt|\bte|\btm)\(\s*['"`]([a-z][\w]*(?:\.[\w]+)+)['"`]/gi,
      /clave[A-Za-z]*:\s*['"`]([a-z][\w]*(?:\.[\w]+)+)['"`]/gi,
    ]
    const usadas = new Map<string, string>()

    for (const { archivo, texto } of FUENTES) {
      for (const patron of patrones) {
        for (const [, clave] of texto.matchAll(patron)) {
          if (!usadas.has(clave!)) {
            usadas.set(clave!, archivo)
          }
        }
      }
    }

    return usadas
  }

  it('resuelve en los dos idiomas toda clave escrita como literal', () => {
    const usadas = clavesUsadas()
    const declaradas = { es: new Set(clavesDe('es')), en: new Set(clavesDe('en')) }
    const ausentes = [...usadas].filter(
      ([clave]) => !declaradas.es.has(clave) || !declaradas.en.has(clave),
    )

    expect(usadas.size).toBeGreaterThan(100)
    expect(ausentes.map(([clave, archivo]) => `${archivo}: ${clave}`)).toEqual([])
  })
})

describe('la copia del producto no publica la numeracion del mapa', () => {
  /**
   * Values the reader can see, minus the plates of the style guide.
   *
   * The exemption is by subtree and it is argued: `guide.*` publishes measured
   * numbers -a 4.55:1 contrast ratio, a +2.4 % delta, a figure of twelve
   * million with two decimals- and there a number IS the content. Everywhere
   * else a number with a dot in the middle can only be a branch identifier of
   * the A3 site map, which is a section of an academic deliverable and not a
   * name of this product.
   *
   * @param idioma - Catalogue to read from.
   * @returns Every visible key and value outside the guide.
   */
  function copiaDeProducto(idioma: CodigoIdioma): [string, string][] {
    return clavesDe(idioma)
      .filter(clave => !clave.startsWith('guide.'))
      .map(clave => [clave, mensaje(idioma, clave)])
  }

  /** True when a sentence carries the numbering of the site map. */
  function citaElMapa(valor: string): boolean {
    // `2.2`, `4.1 a 4.4` -the metric of CA-18- and a value that opens with the
    // number of a first level category, as `1. Inicio` did.
    return /[0-9]\.[0-9]/.test(valor) || /^[0-9]+\.\s/.test(valor)
  }

  it.each(['es', 'en'] as const)('no numera ninguna descripcion de producto en %s', (idioma) => {
    // The defect, shipped and measured: the index published "4. Administración
    // — 4.1 a 4.4" as the description of a screen, and a screen reader read the
    // accessible name of two branches as "2.2 Consulta y filtros, faceta
    // transversal". The trace to the map is not lost: it lives in a4_02, which
    // is the deliverable that owns it.
    const copia = copiaDeProducto(idioma)
    const numeradas = copia.filter(([, valor]) => citaElMapa(valor))

    expect(copia.length).toBeGreaterThan(400)
    expect(numeradas.map(([clave, valor]) => `${clave}: ${valor}`)).toEqual([])
  })

  it('mide de verdad: la guia si publica cifras con punto y queda fuera', () => {
    // Without this the assertion above would also pass over a filter that
    // excluded everything, which is how a scan like this rots without a sound.
    const conCifras = clavesDe('es')
      .filter(clave => clave.startsWith('guide.'))
      .filter(clave => citaElMapa(mensaje('es', clave)))

    expect(conCifras.length).toBeGreaterThan(0)
  })
})

describe('el catalogo y el gobierno del dato no abren con la misma pantalla', () => {
  /**
   * The four sentences each screen opens with, key by key.
   *
   * The pairing is what is under test: `/exploracion` answers "which field do
   * I need" and `/gobierno` answers "where does this figure come from and who
   * answers for it", and the design review found both opening with the same
   * label, the same placeholder and almost the same empty state, which made
   * the second read as a duplicate of the first.
   */
  const APERTURAS: readonly [string, string][] = [
    ['screen.explore.description', 'screen.governance.description'],
    ['catalog.explore.search.label', 'lineage.dictionary.searchLabel'],
    ['catalog.explore.search.placeholder', 'lineage.dictionary.searchPlaceholder'],
    ['catalog.explore.state.initial.title', 'lineage.dictionary.state.initial.title'],
    ['catalog.explore.state.initial.body', 'lineage.dictionary.state.initial.body'],
  ]

  it.each(['es', 'en'] as const)('cada pantalla declara en %s lo que resuelve', (idioma) => {
    // Two screens with the same opening copy are one screen rendered twice, and
    // the site map would be claiming a module that the product does not have.
    const repetidas = APERTURAS.filter(
      ([catalogo, gobierno]) => mensaje(idioma, catalogo) === mensaje(idioma, gobierno),
    )

    expect(repetidas.map(([catalogo]) => catalogo)).toEqual([])
  })
})
