#!/usr/bin/env node
/**
 * Screenshot runner for the seven high fidelity prototypes of A4.
 *
 * The written protocol lives next to this file, in `guion_a4.md`, and that
 * document -not this one- is what makes a capture reproducible by a different
 * person. This module only automates it: same viewport, same language, same
 * colour mode, same session per screen and, above all, the same file names, so
 * that `figuras/a4/antes/` and `figuras/a4/despues/` pair up by name alone.
 *
 * The plan is never typed by hand. It is derived from `PROTOTIPOS` in
 * `frontend/app/utils/navegacion.ts`, the single source of truth of the
 * navigation contract. That module is TypeScript and resolves its imports
 * through the `~` alias of Nuxt, so plain Node cannot import it without a
 * bundler; the literal is read and parsed instead, and every parser here fails
 * loudly when the shape it expects is no longer there. A silent fallback would
 * be worse than a crash: it would produce a plan that no longer matches the
 * portal, and nobody would notice until the PDF was printed.
 *
 * Usage:
 *   node docs/entregables/capturas/capturas_a4.mjs
 *   CAPTURAS_BASE_URL=http://localhost:3001 node docs/entregables/capturas/capturas_a4.mjs
 *   CAPTURAS_FASE=despues node docs/entregables/capturas/capturas_a4.mjs
 *
 * Environment:
 *   CAPTURAS_BASE_URL  Portal under capture. Default http://localhost:3001.
 *   CAPTURAS_FASE      'antes' or 'despues'. Picks the default output folder.
 *   CAPTURAS_SALIDA    Explicit output folder; wins over CAPTURAS_FASE.
 *   CAPTURAS_ESCALA    Device pixel ratio of the PNG. Default 1, which is the
 *                      one the archived set was taken at.
 */
import { mkdir, stat } from 'node:fs/promises'
import { existsSync, readFileSync } from 'node:fs'
import { join, resolve } from 'node:path'
import { fileURLToPath, pathToFileURL } from 'node:url'

/** Fixed viewport used for every A4 screenshot, in CSS pixels. */
export const VIEWPORT = Object.freeze({ width: 1440, height: 900 })

/**
 * One screenshot job: route, demo role, forced state and output file name.
 *
 * `role` carries the four literals of the backend -`ROLES` in
 * `frontend/app/utils/sesion.ts` and the body of `POST /api/auth/demo`-, so the
 * highest one is `admin`. Section 4 of the plan wrote `administrador`, a value
 * that exists in neither place; the code wins and the divergence is recorded in
 * the handoff rather than translated silently at this boundary.
 *
 * @typedef {object} CaptureJob
 * @property {string} route Portal path, exactly as `PROTOTIPOS` declares it.
 * @property {'operativo'|'analista'|'directivo'|'admin'} role Demonstration
 *   profile the session is opened with, taken from `rolSugerido`.
 * @property {'normal'|'empty'|'loading'|'error'|'forbidden'} state Screen state
 *   being captured. The before wave captures `normal` only.
 * @property {string} fileName `<numero>_<pantalla>_<estado>.png`, the contract
 *   the before/after pairing depends on.
 */

/** Combining diacritics of NFD, written as escapes so the source stays ASCII. */
const COMBINING_MARKS = new RegExp('[\u0300-\u036f]', 'g')

/** The four roles the demonstration door accepts, lowest to highest. */
const ROLES = Object.freeze(['operativo', 'analista', 'directivo', 'admin'])

/** The five states of the 7x4 matrix, in the vocabulary of the file name. */
const STATES = Object.freeze(['normal', 'empty', 'loading', 'error', 'forbidden'])

/** Repository root, derived from this file so no caller has to pass a path. */
const REPO_ROOT = resolve(fileURLToPath(new URL('.', import.meta.url)), '..', '..', '..')

/** Frontend package root: where `@playwright/test` is installed. */
const FRONTEND_ROOT = join(REPO_ROOT, 'frontend')

/** Single source of truth of the capture plan. */
const NAVIGATION_MODULE = join(FRONTEND_ROOT, 'app', 'utils', 'navegacion.ts')

/**
 * ESM entry point of `@playwright/test`, addressed by path and not by name.
 *
 * A bare specifier resolves from the importing file, and this file lives under
 * `docs/`, where there is no `node_modules` and never will be. Only this first
 * hop needs the path: the entry re-exports `playwright/test`, and that bare
 * specifier resolves from the folder of the entry itself.
 */
const PLAYWRIGHT_ENTRY = join(FRONTEND_ROOT, 'node_modules', '@playwright', 'test', 'index.mjs')

/** Exact command that installs the missing dependency. */
const INSTALL_COMMAND = 'pnpm --dir frontend add -D @playwright/test'

/** Exact command that downloads the browser binary. */
const BROWSER_COMMAND = 'pnpm --dir frontend exec playwright install chromium'

/** Public entry screen: it is captured signed out, in its resting state. */
const PUBLIC_ROUTE = '/acceso'

/** Route of the assistant, the one screen with a second mandatory band. */
const ASSISTANT_ROUTE = '/asistente'

/** Marker of the scope band. Rule R10: no capture without it enters the PDF. */
const SCOPE_BAND = '[data-franja-alcance]'

/** Marker of the honesty band of the assistant, mandatory while Gemini is off. */
const SCRIPTED_BAND = '[data-prueba="aviso-demo"]'

/** Milliseconds allowed for a dev server navigation, first compile included. */
const NAVIGATION_TIMEOUT = 60000

/** Milliseconds allowed for a selector to appear once the page has loaded. */
const SELECTOR_TIMEOUT = 20000

/** Milliseconds of quiet after load, so fonts and charts settle before shooting. */
const SETTLE_DELAY = 700

/** Clicks allowed on the demonstration door before giving the session up. */
const SESSION_ATTEMPTS = 3

/** Portal under capture, without a trailing slash. */
function baseUrl() {
  return (process.env.CAPTURAS_BASE_URL ?? 'http://localhost:3001').replace(/\/+$/, '')
}

/**
 * Device pixel ratio of the PNG.
 *
 * The default is the scale the archived set was taken at, so that running this
 * with no environment reproduces `figuras/a4/` and not a denser variant of it.
 * At 1440 CSS pixels wide over the text box of the report, scale 1 already
 * carries the text; a higher one is available for anyone who needs it, and only
 * costs file size.
 */
function deviceScaleFactor() {
  const raw = Number.parseInt(process.env.CAPTURAS_ESCALA ?? '1', 10)
  return Number.isFinite(raw) && raw > 0 ? raw : 1
}

/**
 * Folder the run writes into, from CAPTURAS_SALIDA or from the phase.
 *
 * @returns {string} Absolute path of the output folder.
 */
export function defaultOutputDir() {
  const explicit = process.env.CAPTURAS_SALIDA
  if (explicit !== undefined && explicit !== '') {
    return resolve(explicit)
  }
  const phase = process.env.CAPTURAS_FASE ?? 'antes'
  if (phase !== 'antes' && phase !== 'despues') {
    throw new Error(`CAPTURAS_FASE debe ser 'antes' o 'despues', no '${phase}'`)
  }
  return join(REPO_ROOT, 'docs', 'entregables', 'figuras', 'a4', phase)
}

/**
 * Loads Playwright from the frontend package, or explains how to install it.
 *
 * The entry point is imported by file URL, from `PLAYWRIGHT_ENTRY`, because a
 * bare specifier would resolve from this file and `docs/` holds no packages.
 * Its presence is checked before importing, so a missing dependency is reported
 * with the command that installs it and not with an `ERR_MODULE_NOT_FOUND` that
 * names a path nobody asked for.
 *
 * The namespace is then normalised with `default ?? namespace`. The package is
 * CommonJS behind an ESM shim, so whether `chromium` lands on the namespace or
 * only on the default export depends on how much of it the named export
 * detector of Node manages to read; taking the default first makes the run
 * independent of that, and the guard below turns anything left into a message
 * about the dependency rather than about an undefined property.
 *
 * @returns {Promise<{chromium: object}>} The Playwright entry point.
 */
async function loadPlaywright() {
  if (!existsSync(PLAYWRIGHT_ENTRY)) {
    throw new Error(
      `@playwright/test no esta instalado. Instalalo con:\n    ${INSTALL_COMMAND}\n`
      + `Despues descarga el navegador con:\n    ${BROWSER_COMMAND}`,
    )
  }
  const loaded = await import(pathToFileURL(PLAYWRIGHT_ENTRY).href)
  const playwright = loaded.default ?? loaded
  if (typeof playwright.chromium?.launch !== 'function') {
    throw new Error(
      `@playwright/test se cargo pero no expone chromium. Reinstalalo con:\n    ${INSTALL_COMMAND}`,
    )
  }
  return playwright
}

/**
 * Launches Chromium, or explains how to download it.
 *
 * @param {object} chromium Playwright browser type.
 * @returns {Promise<object>} A running browser.
 */
async function launchBrowser(chromium) {
  try {
    return await chromium.launch()
  }
  catch (error) {
    const detail = error instanceof Error ? error.message : String(error)
    throw new Error(
      `no se pudo lanzar Chromium. Descargalo con:\n    ${BROWSER_COMMAND}\nDetalle: ${detail}`,
    )
  }
}

/**
 * Body of an exported array literal, matched by brackets rather than by regex.
 *
 * The search starts after the assignment and not after the name: the constant
 * is annotated `readonly Prototipo[]`, so the first bracket of the declaration
 * belongs to the type and closes immediately, which would yield an empty plan
 * instead of a failure.
 *
 * @param {string} source Contents of the TypeScript module.
 * @param {string} exportName Name of the exported constant.
 * @returns {string} Everything between the outer brackets.
 */
function extractArrayLiteral(source, exportName) {
  const declaration = source.indexOf(`export const ${exportName}`)
  if (declaration === -1) {
    throw new Error(`${exportName} ya no se exporta desde ${NAVIGATION_MODULE}`)
  }
  const assignment = source.indexOf('=', declaration)
  if (assignment === -1) {
    throw new Error(`${exportName} ya no se asigna en ${NAVIGATION_MODULE}`)
  }
  const open = source.indexOf('[', assignment)
  if (open === -1) {
    throw new Error(`${exportName} ya no se declara como arreglo en ${NAVIGATION_MODULE}`)
  }
  let depth = 0
  for (let index = open; index < source.length; index += 1) {
    const character = source[index]
    if (character === '[') {
      depth += 1
    }
    else if (character === ']') {
      depth -= 1
      if (depth === 0) {
        return source.slice(open + 1, index)
      }
    }
  }
  throw new Error(`el literal de ${exportName} no cierra en ${NAVIGATION_MODULE}`)
}

/**
 * The `RUTA_*` constants of the navigation module, by name.
 *
 * `PROTOTIPOS` points at two of them instead of repeating the path, so the plan
 * cannot be derived without resolving them first.
 *
 * @param {string} source Contents of the TypeScript module.
 * @returns {Map<string, string>} Constant name to path.
 */
function readRouteConstants(source) {
  const constants = new Map()
  const pattern = /export const (RUTA_[A-Z0-9_]+)\s*=\s*'([^']*)'/g
  let match = pattern.exec(source)
  while (match !== null) {
    constants.set(match[1], match[2])
    match = pattern.exec(source)
  }
  return constants
}

/**
 * Reads a single quoted field out of one object literal.
 *
 * @param {string} fields Text between the braces of the entry.
 * @param {string} name Field to read.
 * @returns {string} Its value.
 */
function readStringField(fields, name) {
  const match = new RegExp(`${name}\\s*:\\s*'([^']*)'`).exec(fields)
  if (match === null) {
    throw new Error(`una entrada de PROTOTIPOS no declara ${name}`)
  }
  return match[1]
}

/**
 * Reads a numeric field out of one object literal.
 *
 * @param {string} fields Text between the braces of the entry.
 * @param {string} name Field to read.
 * @returns {number} Its value.
 */
function readNumberField(fields, name) {
  const match = new RegExp(`${name}\\s*:\\s*(-?\\d+)`).exec(fields)
  if (match === null) {
    throw new Error(`una entrada de PROTOTIPOS no declara ${name}`)
  }
  return Number.parseInt(match[1], 10)
}

/**
 * Reads the `ruta` field, which may be a literal or a `RUTA_*` constant.
 *
 * @param {string} fields Text between the braces of the entry.
 * @param {Map<string, string>} constants Result of readRouteConstants.
 * @returns {string} The path.
 */
function readRouteField(fields, constants) {
  const literal = /ruta\s*:\s*'([^']*)'/.exec(fields)
  if (literal !== null) {
    return literal[1]
  }
  const reference = /ruta\s*:\s*([A-Z][A-Z0-9_]*)/.exec(fields)
  if (reference === null) {
    throw new Error('una entrada de PROTOTIPOS no declara ruta')
  }
  const resolved = constants.get(reference[1])
  if (resolved === undefined) {
    throw new Error(`PROTOTIPOS apunta a ${reference[1]}, que ya no se exporta`)
  }
  return resolved
}

/**
 * Screen segment of the file name, derived from the route.
 *
 * Lower case, no accents, one dash per path separator: `/exploracion/exportar`
 * becomes `exploracion-exportar`. Deriving it beats writing it down, because a
 * name typed by hand can disagree with the route it claims to show.
 *
 * @param {string} route Portal path.
 * @returns {string} Slug used inside the file name.
 */
export function screenSlug(route) {
  const withoutAccents = route.normalize('NFD').replace(COMBINING_MARKS, '').toLowerCase()
  const trimmed = withoutAccents.replace(/^\/+/, '').replace(/\/+$/, '')
  const body = trimmed === '' ? 'indice' : trimmed
  return body.replace(/\//g, '-').replace(/[^a-z0-9-]/g, '-')
}

/**
 * Reads `PROTOTIPOS` and returns its entries, in declaration order.
 *
 * @param {string} source Contents of the TypeScript module.
 * @returns {Array<{numero: number, ruta: string, rolSugerido: string, alcance: string}>} Entries.
 */
function parsePrototypes(source) {
  const body = extractArrayLiteral(source, 'PROTOTIPOS')
  const constants = readRouteConstants(source)
  const entries = []
  const objectPattern = /\{([^{}]*)\}/g
  let match = objectPattern.exec(body)
  while (match !== null) {
    const fields = match[1]
    entries.push({
      numero: readNumberField(fields, 'numero'),
      ruta: readRouteField(fields, constants),
      rolSugerido: readStringField(fields, 'rolSugerido'),
      alcance: readStringField(fields, 'alcance'),
    })
    match = objectPattern.exec(body)
  }
  if (entries.length === 0) {
    throw new Error(`PROTOTIPOS quedo vacio en ${NAVIGATION_MODULE}`)
  }
  return entries
}

/**
 * Ordered capture plan derived from PROTOTIPOS; the single source of the run.
 *
 * @param {'normal'|'empty'|'loading'|'error'|'forbidden'} [state] State to
 *   capture. The before wave uses the default, `normal`.
 * @returns {readonly CaptureJob[]} One job per prototype, in map order.
 */
export function buildCapturePlan(state = 'normal') {
  if (!STATES.includes(state)) {
    throw new Error(`estado desconocido: ${state}`)
  }
  let source
  try {
    source = readFileSync(NAVIGATION_MODULE, 'utf8')
  }
  catch {
    throw new Error(
      `no se pudo leer ${NAVIGATION_MODULE}; el plan se deriva de ahi y no de una lista escrita`,
    )
  }
  const jobs = parsePrototypes(source).map((entry) => {
    if (!ROLES.includes(entry.rolSugerido)) {
      throw new Error(`rol desconocido en PROTOTIPOS: ${entry.rolSugerido}`)
    }
    return Object.freeze({
      route: entry.ruta,
      role: entry.rolSugerido,
      state,
      fileName: `${entry.numero}_${screenSlug(entry.ruta)}_${state}.png`,
    })
  })
  return Object.freeze(jobs)
}

/**
 * Opens a demonstration session through the entry screen of the portal.
 *
 * Through the interface and not through a bare request on purpose: the Nitro
 * route applies `exigirOrigenPropio`, so a call without same-origin headers is
 * answered with 403. Clicking the button is also the path a human follows when
 * Playwright is unavailable, which keeps the manual plan B identical.
 *
 * The wait before the first click is not padding. The screen is server
 * rendered, and a click that lands before hydration hits a button that still
 * has no handler: nothing happens, nothing fails, and the run stalls on a
 * navigation that will never come. The retry covers the same race when the dev
 * server is compiling the route for the first time.
 *
 * @param {object} page Playwright page.
 * @param {'operativo'|'analista'|'directivo'|'admin'} role Profile to enter as.
 * @returns {Promise<void>}
 */
async function openSession(page, role) {
  await page.goto(`${baseUrl()}${PUBLIC_ROUTE}`, { waitUntil: 'domcontentloaded' })
  await waitForQuiet(page)
  const button = page.locator(`[data-demostracion] button[data-rol="${role}"]`)
  await button.waitFor({ state: 'visible', timeout: SELECTOR_TIMEOUT })

  for (let attempt = 1; attempt <= SESSION_ATTEMPTS; attempt += 1) {
    try {
      await button.click({ timeout: SELECTOR_TIMEOUT })
    }
    catch {
      // The button detached: the click of the previous attempt did land after
      // all, and the page is already navigating away.
    }
    try {
      await page.waitForURL((url) => url.pathname !== PUBLIC_ROUTE, { timeout: SELECTOR_TIMEOUT })
      return
    }
    catch {
      if (attempt === SESSION_ATTEMPTS) {
        throw new Error(`la puerta de demostracion no abrio sesion como ${role}`)
      }
    }
  }
}

/**
 * Waits until the page has stopped fetching and has finished painting text.
 *
 * `networkidle` is bounded and its expiry is not fatal: under `nuxt dev` the
 * first visit to a route compiles it, and a long tail of module requests must
 * not turn into a missing capture.
 *
 * @param {object} page Playwright page.
 * @returns {Promise<void>}
 */
async function waitForQuiet(page) {
  try {
    await page.waitForLoadState('networkidle', { timeout: NAVIGATION_TIMEOUT })
  }
  catch {
    await page.waitForLoadState('load', { timeout: NAVIGATION_TIMEOUT })
  }
  await page.evaluate(() => document.fonts.ready)
  await page.waitForTimeout(SETTLE_DELAY)
}

/**
 * Runs one job against a live dev server and writes the PNG under outputDir.
 *
 * @param {CaptureJob} job Job to run.
 * @param {string} outputDir Folder the PNG is written into.
 * @param {object} [sharedBrowser] Browser to reuse; one is launched when absent.
 * @returns {Promise<string>} Absolute path of the file written.
 */
export async function runCapture(job, outputDir, sharedBrowser) {
  // Playwright is only loaded when this call has to launch its own browser.
  // Under `main()` the browser arrives already running, and resolving the entry
  // point once per job bought nothing.
  const ownsBrowser = sharedBrowser === undefined
  const browser = ownsBrowser
    ? await launchBrowser((await loadPlaywright()).chromium)
    : sharedBrowser
  const target = resolve(outputDir, job.fileName)
  const portal = baseUrl()

  // One context per job: the session of a role must never leak into the next
  // screen, and the after wave has to be able to run the plan in any order.
  const context = await browser.newContext({
    viewport: { ...VIEWPORT },
    deviceScaleFactor: deviceScaleFactor(),
    colorScheme: 'light',
    reducedMotion: 'reduce',
    locale: 'es-MX',
  })
  context.setDefaultTimeout(SELECTOR_TIMEOUT)
  context.setDefaultNavigationTimeout(NAVIGATION_TIMEOUT)

  // The language is a cookie, not a URL prefix: the i18n strategy is
  // `no_prefix`, so without this the capture would depend on the browser.
  await context.addCookies([
    { name: 'karisma_locale', value: 'es', url: portal },
    { name: 'karisma_modo', value: 'claro', url: portal },
  ])

  const page = await context.newPage()
  try {
    // The entry screen is captured signed out: it is the door, and a session
    // would show a screen no reader reaches that way.
    if (job.route !== PUBLIC_ROUTE) {
      await openSession(page, job.role)
    }

    await page.goto(`${portal}${job.route}`, { waitUntil: 'domcontentloaded' })
    await waitForQuiet(page)

    // R10 of the capture protocol. Failing here is the point: a screenshot
    // without the scope band cannot be told apart from a live system.
    await page.locator(SCOPE_BAND).first().waitFor({ state: 'visible', timeout: SELECTOR_TIMEOUT })

    // While the language model is off, the assistant may not be shown without
    // the band that says its answers are scripted.
    if (job.route === ASSISTANT_ROUTE) {
      await page
        .locator(SCRIPTED_BAND)
        .first()
        .waitFor({ state: 'visible', timeout: SELECTOR_TIMEOUT })
    }

    await mkdir(outputDir, { recursive: true })
    await page.screenshot({
      path: target,
      fullPage: false,
      animations: 'disabled',
      caret: 'hide',
      scale: 'device',
    })

    const written = await stat(target)
    if (written.size === 0) {
      throw new Error(`${job.fileName} se escribio vacio`)
    }
    return target
  }
  finally {
    await context.close()
    if (ownsBrowser) {
      await browser.close()
    }
  }
}

/**
 * Runs the whole plan with a single browser and reports one line per job.
 *
 * @returns {Promise<number>} Process exit code.
 */
async function main() {
  const outputDir = defaultOutputDir()
  const plan = buildCapturePlan()
  const { chromium } = await loadPlaywright()
  const browser = await launchBrowser(chromium)
  const failures = []

  process.stdout.write(`portal:   ${baseUrl()}\n`)
  process.stdout.write(`salida:   ${outputDir}\n`)
  process.stdout.write(`viewport: ${VIEWPORT.width}x${VIEWPORT.height} @${deviceScaleFactor()}x\n\n`)

  try {
    await mkdir(outputDir, { recursive: true })
    for (const job of plan) {
      const label = `${job.fileName.padEnd(32)} ${job.route.padEnd(22)} ${job.role}`
      try {
        const written = await runCapture(job, outputDir, browser)
        const size = (await stat(written)).size
        process.stdout.write(`ok    ${label}  ${size} bytes\n`)
      }
      catch (error) {
        failures.push(job.fileName)
        const detail = error instanceof Error ? error.message : String(error)
        process.stdout.write(`FALLO ${label}\n      ${detail.split('\n')[0]}\n`)
      }
    }
  }
  finally {
    await browser.close()
  }

  process.stdout.write(`\n${plan.length - failures.length}/${plan.length} capturas escritas\n`)
  if (failures.length > 0) {
    process.stdout.write(`faltan: ${failures.join(', ')}\n`)
    return 1
  }
  return 0
}

// Only when invoked directly: importing the module -from a test, or from the
// after wave- must not launch a browser as a side effect.
if (process.argv[1] !== undefined && import.meta.url === pathToFileURL(process.argv[1]).href) {
  main()
    .then((code) => {
      process.exitCode = code
    })
    .catch((error) => {
      process.stderr.write(`${error instanceof Error ? error.message : String(error)}\n`)
      process.exitCode = 1
    })
}
