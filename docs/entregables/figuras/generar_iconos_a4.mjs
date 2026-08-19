#!/usr/bin/env node
/**
 * Icon plates of the A4 style guide: PNG glyphs plus the generated TeX table.
 *
 * The evaluator of A4 asked for the icons themselves, not for their names: the
 * inventory table listed functions in prose while the screens next to it were
 * full of strokes nobody could match to a row. This script closes that gap by
 * printing the glyph of every icon the inventory declares.
 *
 * Nothing here is typed by hand. Both inputs are read from the running
 * product and any of them failing to parse is a crash, never a fallback:
 *
 *   1. `frontend/app/components/guia/inventarioIconos.ts` — the declared
 *      inventory, parsed as text. It is TypeScript behind the `~` alias of
 *      Nuxt, so plain Node cannot import it; the same reason and the same
 *      technique as `capturas/capturas_a4.mjs`.
 *   2. `frontend/i18n/locales/es.json` — the Spanish label of each group and
 *      each icon. The document must call an icon what the interface calls it.
 *
 * The glyphs come from `@iconify-json/lucide`, the same package the interface
 * bundles, and are rasterised by the Chromium that Playwright already installed
 * for the A4 screenshots. No new dependency and no hand drawing: rule 3 of the
 * interface checklist says one family only, and a redrawn icon would break it
 * inside the very guide that states it.
 *
 * Usage:
 *   node docs/entregables/figuras/generar_iconos_a4.mjs
 *
 * Outputs (both generated, neither edited by hand):
 *   docs/entregables/figuras/a4/iconos/*.png
 *   docs/entregables/estilo/a4_iconos.tex y a4_iconos_declarados.tex
 */
import { mkdir, writeFile, readdir, unlink } from 'node:fs/promises'
import { existsSync, readFileSync } from 'node:fs'
import { dirname, join, relative, resolve } from 'node:path'
import { fileURLToPath, pathToFileURL } from 'node:url'

const AQUI = dirname(fileURLToPath(import.meta.url))
const RAIZ = resolve(AQUI, '..', '..', '..')
const FRONTEND = join(RAIZ, 'frontend')
const INVENTARIO = join(FRONTEND, 'app', 'components', 'guia', 'inventarioIconos.ts')
const LOCALES_ES = join(FRONTEND, 'i18n', 'locales', 'es.json')
const ICONIFY = join(FRONTEND, 'node_modules', '@iconify-json', 'lucide', 'icons.json')

const SALIDA_PNG = join(AQUI, 'a4', 'iconos')
const ESTILO = join(RAIZ, 'docs', 'entregables', 'estilo')
const SALIDA_TEX = join(ESTILO, 'a4_iconos.tex')
const SALIDA_TABLA_DECLARADOS = join(ESTILO, 'a4_iconos_declarados.tex')

/**
 * Ink of the report, `uxink` of `estilo/uxdoc.sty`.
 *
 * Written here and not in the generated TeX on purpose: the style sheet of the
 * report is frozen and owns its palette, so the raster carries the colour and
 * the document carries no second definition of it.
 */
const TINTA = '#1E293B'

/** Canvas of a Lucide icon, in its own units. */
const LIENZO = 24

/** Pixel ratio of the raster. 24 x 12 = 288 px, ample for print at 1 em. */
const ESCALA = 12

/** The three sizes the system allows, mirrored from TAMANOS_DE_ICONO. */
const TAMANOS = [16, 20, 24]

/** Icon used for the size sample of section 9.2. It is in the inventory. */
const ICONO_DE_MUESTRA = 'search'

const INSTALAR_NAVEGADOR = 'pnpm --dir frontend exec playwright install chromium'

/**
 * Read a file or die loudly.
 *
 * @param {string} ruta Absolute path.
 * @returns {string} File contents.
 */
function leer(ruta) {
  if (!existsSync(ruta)) {
    throw new Error(`No existe ${relative(RAIZ, ruta)}. Sin ese archivo esta lamina no se puede generar.`)
  }
  return readFileSync(ruta, 'utf8')
}

/**
 * Parse GRUPOS_DE_ICONOS and NOMBRES_AUXILIARES out of the inventory module.
 *
 * @returns {{grupos: Array<{clave: string, entradas: Array<{nombre: string, clave: string}>}>, auxiliares: string[]}}
 */
function leerInventario() {
  const fuente = leer(INVENTARIO)

  const bloque = fuente.match(/GRUPOS_DE_ICONOS[^=]*=\s*Object\.freeze\(\[([\s\S]*?)\n\]\)/)
  if (!bloque) {
    throw new Error('No se encontro GRUPOS_DE_ICONOS en inventarioIconos.ts. El parser espera Object.freeze([...]).')
  }

  const grupos = []
  const porGrupo = /\{\s*clave:\s*'([^']+)',\s*entradas:\s*\[([\s\S]*?)\],\s*\}/g
  let coincidencia
  while ((coincidencia = porGrupo.exec(bloque[1])) !== null) {
    const entradas = []
    const porEntrada = /\{\s*nombre:\s*'([^']+)',\s*clave:\s*'([^']+)'\s*\}/g
    let entrada
    while ((entrada = porEntrada.exec(coincidencia[2])) !== null) {
      entradas.push({ nombre: entrada[1], clave: entrada[2] })
    }
    if (entradas.length === 0) {
      throw new Error(`El grupo ${coincidencia[1]} quedo sin entradas: el parser ya no reconoce la forma del modulo.`)
    }
    grupos.push({ clave: coincidencia[1], entradas })
  }
  if (grupos.length === 0) {
    throw new Error('GRUPOS_DE_ICONOS se leyo vacio. El parser ya no reconoce la forma del modulo.')
  }

  const auxiliar = fuente.match(/NOMBRES_AUXILIARES[^=]*=\s*Object\.freeze\(\[([\s\S]*?)\]\)/)
  if (!auxiliar) {
    throw new Error('No se encontro NOMBRES_AUXILIARES en inventarioIconos.ts.')
  }
  const auxiliares = [...auxiliar[1].matchAll(/'([^']+)'/g)].map(m => m[1])

  return { grupos, auxiliares }
}

/**
 * Resolve a dotted i18n key against the Spanish locale.
 *
 * @param {object} locale Parsed es.json.
 * @param {string} clave Dotted key.
 * @returns {string} The translated string.
 */
function etiqueta(locale, clave) {
  const valor = clave.split('.').reduce((nodo, parte) => (nodo === undefined ? undefined : nodo[parte]), locale)
  if (typeof valor !== 'string') {
    throw new Error(`La clave ${clave} no existe en i18n/locales/es.json. El documento no inventa nombres.`)
  }
  return valor
}

/**
 * Resolve one Lucide icon to its SVG body, following aliases.
 *
 * @param {object} datos Parsed icons.json of @iconify-json/lucide.
 * @param {string} nombre Icon name without the `lucide:` prefix.
 * @returns {string} Inner SVG markup.
 */
function cuerpoDeIcono(datos, nombre) {
  let actual = nombre
  for (let salto = 0; salto < 5; salto += 1) {
    const definicion = datos.icons?.[actual]
    if (definicion?.body) {
      if (definicion.width && definicion.width !== LIENZO) {
        throw new Error(`El icono ${nombre} declara un lienzo de ${definicion.width}, no de ${LIENZO}.`)
      }
      return definicion.body
    }
    const alias = datos.aliases?.[actual]
    if (!alias?.parent) break
    if (alias.rotate || alias.hFlip || alias.vFlip) {
      throw new Error(`El alias ${actual} aplica una transformacion que este generador no reproduce.`)
    }
    actual = alias.parent
  }
  throw new Error(`El icono lucide:${nombre} no existe en @iconify-json/lucide.`)
}

/**
 * Load Playwright, which ships as CommonJS behind an ESM shim.
 *
 * Imported by file URL and not by bare specifier: `docs/` holds no packages, so
 * `import('@playwright/test')` would resolve from this file and fail. The same
 * reason and the same path as `capturas/capturas_a4.mjs`.
 *
 * @returns {Promise<object>} The chromium browser type.
 */
async function cargarChromium() {
  const entrada = join(FRONTEND, 'node_modules', '@playwright', 'test', 'index.mjs')
  if (!existsSync(entrada)) {
    throw new Error(`@playwright/test no esta instalado. Instalalo con:\n    pnpm --dir frontend install`)
  }
  const modulo = await import(pathToFileURL(entrada).href)
  const chromium = modulo.chromium ?? modulo.default?.chromium
  if (typeof chromium?.launch !== 'function') {
    throw new Error(`@playwright/test se cargo pero no expone chromium. Reinstalalo con:\n    ${INSTALAR_NAVEGADOR}`)
  }
  return chromium
}

/**
 * Rasterise every icon to a transparent PNG named after the icon.
 *
 * @param {Map<string, string>} cuerpos Icon name to SVG body.
 * @returns {Promise<void>}
 */
async function rasterizar(cuerpos) {
  const chromium = await cargarChromium()
  let navegador
  try {
    navegador = await chromium.launch()
  }
  catch (error) {
    throw new Error(`Chromium no arranco. Instalalo con:\n    ${INSTALAR_NAVEGADOR}\n\n${error.message}`)
  }

  const contexto = await navegador.newContext({ deviceScaleFactor: ESCALA })
  const pagina = await contexto.newPage()

  const marca = (nombre, cuerpo, lado) => `<svg id="i-${nombre}-${lado}" xmlns="http://www.w3.org/2000/svg" `
    + `width="${lado}" height="${lado}" viewBox="0 0 ${LIENZO} ${LIENZO}" color="${TINTA}">${cuerpo}</svg>`

  const piezas = [...cuerpos].map(([nombre, cuerpo]) => marca(nombre, cuerpo, LIENZO))
  // Size sample of section 9.2: the same icon at the three allowed sizes, side
  // by side and baseline aligned, exactly as the rule states.
  const muestra = TAMANOS.map(px => marca(`${ICONO_DE_MUESTRA}-muestra`, cuerpos.get(ICONO_DE_MUESTRA), px)
    .replace(`i-${ICONO_DE_MUESTRA}-muestra-${px}`, `muestra-${px}`)).join('')

  await pagina.setContent(
    `<!doctype html><html><body style="margin:0;background:transparent">`
    + `<div style="display:flex;flex-wrap:wrap;gap:8px;padding:8px">${piezas.join('')}</div>`
    + `<div id="muestra-tamanos" style="display:flex;align-items:flex-end;gap:12px;padding:8px;width:max-content">${muestra}</div>`
    + `</body></html>`,
  )

  await mkdir(SALIDA_PNG, { recursive: true })
  for (const nombre of cuerpos.keys()) {
    await pagina.locator(`#i-${nombre}-${LIENZO}`).screenshot({
      path: join(SALIDA_PNG, `${nombre}.png`),
      omitBackground: true,
    })
  }
  await pagina.locator('#muestra-tamanos').screenshot({
    path: join(SALIDA_PNG, 'muestra-tamanos.png'),
    omitBackground: true,
  })

  await navegador.close()
}

/**
 * Escape the few characters LaTeX would read as syntax.
 *
 * @param {string} texto Plain text.
 * @returns {string} The same text, safe inside a cell.
 */
function escapar(texto) {
  return texto
    .replace(/\\/g, '\\textbackslash{}')
    .replace(/([&%$#_{}])/g, '\\$1')
    .replace(/~/g, '\\textasciitilde{}')
    .replace(/\^/g, '\\textasciicircum{}')
}

/**
 * Write the macros of the plate and the table of the declared inventory.
 *
 * @param {object} entrada Everything the tables need.
 * @param {Array} entrada.grupos Declared inventory groups.
 * @param {object} entrada.locale Parsed es.json.
 * @param {string[]} entrada.declarados Names inside the declared inventory.
 * @returns {Promise<void>}
 */
async function emitirTex({ grupos, locale, declarados }) {
  const lineas = []

  lineas.push(
    '% ===========================================================================',
    '%  a4_iconos.tex - GENERADO por figuras/generar_iconos_a4.mjs. No editar.',
    '%',
    '%  Los glifos salen de @iconify-json/lucide, el mismo paquete que empaqueta',
    '%  la interfaz, y las etiquetas de i18n/locales/es.json. Regenerar con:',
    '%      node docs/entregables/figuras/generar_iconos_a4.mjs',
    '% ===========================================================================',
    '',
    '% Un icono a la altura de la linea, alineado a la base del texto que acompana.',
    '\\newcommand{\\iconoLucide}[1]{%',
    '  \\raisebox{-0.16em}{\\includegraphics[height=1.05em]{figuras/a4/iconos/#1}}}',
    '',
    '% Los tres tamanos del sistema, en una sola imagen medida en el navegador.',
    '\\newcommand{\\muestraTamanosIcono}{%',
    '  \\includegraphics[height=2.4em]{figuras/a4/iconos/muestra-tamanos}}',
    '',
  )

  // --- Tabla del inventario declarado --------------------------------------
  // Las dos tablas viajan en archivos propios y no dentro de un \newcommand:
  // uxtablalarga se construye con \NewEnviron, que recolecta su cuerpo, y ese
  // mecanismo no sobrevive a quedar guardado dentro de una macro. Se \input-ean
  // en el punto exacto de la seccion, que ademas es lo que las mantiene junto a
  // su titular en vez de flotando a la pagina siguiente.
  const declaradas = []
  declaradas.push(
    '% GENERADO por figuras/generar_iconos_a4.mjs. No editar.',
    '% Inventario declarado: los iconos que GRUPOS_DE_ICONOS nombra uno a uno.',
    '\\begin{uxtablalarga}{|L{2.9cm}|C{1.0cm}|L{3.5cm}|Y|}%',
    '  {Inventario declarado de iconos: glifo, nombre técnico y función en el portal}%',
    '  {\\thd{Grupo} & \\thd{Icono} & \\thd{Nombre Lucide} & \\thd{Función en el portal}}',
  )
  for (const grupo of grupos) {
    const rotuloGrupo = escapar(etiqueta(locale, grupo.clave))
    grupo.entradas.forEach((entrada, indice) => {
      const nombre = entrada.nombre.replace('lucide:', '')
      const celdaGrupo = indice === 0 ? `\\textbf{${rotuloGrupo}}` : ''
      declaradas.push(
        `  ${celdaGrupo} & \\iconoLucide{${nombre}} & \\texttt{${escapar(nombre)}} `
        + `& ${escapar(etiqueta(locale, entrada.clave))} \\\\`,
      )
    })
  }
  declaradas.push('\\end{uxtablalarga}', '')

  // --- La unica cifra que el texto cita, para no escribirla a mano ---------
  lineas.push(
    '% Cifra del inventario, emitida para que la prosa no la escriba a mano.',
    `\\newcommand{\\cifraIconosDeclarados}{${declarados.length}}`,
    '',
  )

  await writeFile(SALIDA_TEX, lineas.join('\n'), 'utf8')
  await writeFile(SALIDA_TABLA_DECLARADOS, declaradas.join('\n'), 'utf8')
  return { declarados: declarados.length }
}

/**
 * Remove PNGs of icons that left the inventory, so the folder never lies.
 *
 * @param {Set<string>} vigentes Names that must survive.
 * @returns {Promise<number>} How many files were deleted.
 */
async function limpiarHuerfanos(vigentes) {
  if (!existsSync(SALIDA_PNG)) return 0
  let borrados = 0
  for (const archivo of await readdir(SALIDA_PNG)) {
    if (!archivo.endsWith('.png')) continue
    const nombre = archivo.slice(0, -4)
    if (nombre === 'muestra-tamanos' || vigentes.has(nombre)) continue
    await unlink(join(SALIDA_PNG, archivo))
    borrados += 1
  }
  return borrados
}

async function principal() {
  const { grupos } = leerInventario()
  const locale = JSON.parse(leer(LOCALES_ES))
  const datos = JSON.parse(leer(ICONIFY))

  const declarados = grupos.flatMap(grupo => grupo.entradas.map(entrada => entrada.nombre.replace('lucide:', '')))

  const nombres = [...new Set(declarados)].sort()
  const cuerpos = new Map(nombres.map(nombre => [nombre, cuerpoDeIcono(datos, nombre)]))

  process.stdout.write(`iconos declarados: ${declarados.length}\n`)
  process.stdout.write(`glifos a rasterizar: ${cuerpos.size}\n\n`)

  await rasterizar(cuerpos)
  const borrados = await limpiarHuerfanos(new Set(nombres))
  const resumen = await emitirTex({ grupos, locale, declarados })

  process.stdout.write(`PNG en ${relative(RAIZ, SALIDA_PNG)}: ${cuerpos.size} + muestra de tamanos\n`)
  if (borrados > 0) process.stdout.write(`PNG huerfanos borrados: ${borrados}\n`)
  process.stdout.write(`TeX en ${relative(RAIZ, SALIDA_TEX)}: ${resumen.declarados} declarados\n`)
}

principal().catch((error) => {
  process.stderr.write(`\n${error.message}\n`)
  process.exitCode = 1
})
