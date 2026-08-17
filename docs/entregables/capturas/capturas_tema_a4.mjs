#!/usr/bin/env node
/**
 * Screenshot runner for the theme evidence of A4.
 *
 * Sibling of `capturas_a4.mjs` and deliberately not a copy of it. The capture
 * plan -which routes, in which order, with which demonstration role- is
 * imported from that module, so it keeps being derived from `PROTOTIPOS` in
 * `frontend/app/utils/navegacion.ts` and cannot drift from the portal. What
 * this file adds is the one axis the other one has no reason to carry: the
 * pair theme plus colour mode, which is a cookie the shell reads before the
 * first paint.
 *
 * Two sets are written, and they answer two different questions:
 *
 *   1. The seven prototypes under the institutional theme in light mode. They
 *      show that the theme is the whole product and not a swatch on a page.
 *   2. The four combinations of theme by mode over `/inicio`. One screen, four
 *      appearances, so the reader can compare the axis without changing the
 *      content underneath.
 *
 * File names are fixed by the document that prints them: the eleven names
 * already exist in `figuras/a4/tema/` and the `.tex` refers to them, so they
 * are declared here instead of being derived. The cross check against the
 * imported plan is what keeps that declaration honest: adding or removing a
 * prototype fails the run rather than silently skipping a screenshot.
 *
 * Usage:
 *   node docs/entregables/capturas/capturas_tema_a4.mjs
 *   CAPTURAS_BASE_URL=http://localhost:3001 node docs/entregables/capturas/capturas_tema_a4.mjs
 *
 * Environment:
 *   CAPTURAS_BASE_URL  Portal under capture. Default http://localhost:3001.
 *   CAPTURAS_SALIDA    Explicit output folder. Default figuras/a4/tema.
 *   CAPTURAS_ESCALA    Device pixel ratio of the PNG. Default 1, the scale the
 *                      archived set was taken at.
 */
import { mkdir, stat } from 'node:fs/promises'
import { existsSync } from 'node:fs'
import { join, resolve } from 'node:path'
import { fileURLToPath, pathToFileURL } from 'node:url'

import { VIEWPORT, buildCapturePlan } from './capturas_a4.mjs'

/** Repository root, derived from this file so no caller has to pass a path. */
const REPO_ROOT = resolve(fileURLToPath(new URL('.', import.meta.url)), '..', '..', '..')

/** Frontend package root: where `@playwright/test` is installed. */
const FRONTEND_ROOT = join(REPO_ROOT, 'frontend')

/** ESM entry point of `@playwright/test`, addressed by path and not by name. */
const PLAYWRIGHT_ENTRY = join(FRONTEND_ROOT, 'node_modules', '@playwright', 'test', 'index.mjs')

/** Exact command that installs the missing dependency. */
const INSTALL_COMMAND = 'pnpm --dir frontend add -D @playwright/test'

/** Exact command that downloads the browser binary. */
const BROWSER_COMMAND = 'pnpm --dir frontend exec playwright install chromium'

/** Public entry screen: it is captured signed out, in its resting state. */
const PUBLIC_ROUTE = '/acceso'

/** Route of the assistant, the one screen with a second mandatory band. */
const ASSISTANT_ROUTE = '/asistente'

/** Route the four theme by mode combinations are taken over. */
const COMBINATION_ROUTE = '/inicio'

/** Marker of the scope band. Rule R10: no capture without it enters the PDF. */
const SCOPE_BAND = '[data-franja-alcance]'

/** Marker of the honesty band of the assistant, mandatory while Gemini is off. */
const SCRIPTED_BAND = '[data-prueba="aviso-demo"]'

/** Milliseconds allowed for a dev server navigation, first compile included. */
const NAVIGATION_TIMEOUT = 60000

/** Milliseconds allowed for a selector to appear once the page has loaded. */
const SELECTOR_TIMEOUT = 20000

/** Milliseconds of quiet after load, so fonts and charts settle before shooting. */
const SETTLE_DELAY = 900

/** Clicks allowed on the demonstration door before giving the session up. */
const SESSION_ATTEMPTS = 3

/** Cookie the shell reads to pick the theme before the first paint. */
const THEME_COOKIE = 'karisma_tema'

/** Cookie the shell reads to pick the colour mode before the first paint. */
const MODE_COOKIE = 'karisma_modo'

/** Cookie the i18n strategy reads: the language is not a URL prefix. */
const LOCALE_COOKIE = 'karisma_locale'

/**
 * File name stem of each prototype inside `figuras/a4/tema/`.
 *
 * This numbering is NOT the one of `PROTOTIPOS`: the archived theme set writes
 * `4_administracion` and `5_asistente`, the other way round from the before and
 * after set, and `6_exportacion` instead of `6_exploracion-exportar`. The names
 * are a contract with the `.tex` that prints them, so they are declared rather
 * than derived -and every one of them is cross checked against the imported
 * plan below, which is what stops the declaration from rotting.
 */
const STEM_BY_ROUTE = Object.freeze({
  '/acceso': '0_acceso',
  '/inicio': '1_inicio',
  '/exploracion': '2_exploracion',
  '/gobierno': '3_gobierno',
  '/administracion': '4_administracion',
  '/asistente': '5_asistente',
  '/exploracion/exportar': '6_exportacion',
})

/**
 * Query string appended to a route so its capture shows content.
 *
 * `/exploracion` at rest is an empty state by design -it asks nothing of the
 * server until the reader names a concept- and a screenshot of that state
 * documents the screen the third iteration replaced, not the one it built. The
 * term travels in the address, which is the capability itself: opening
 * `/exploracion?q=saldo` cold applies the search, so this is the screen a
 * shared link produces and not a state assembled for the photograph.
 *
 * The key is the route and not the file name, so a route that stops existing
 * takes its entry with it instead of leaving an orphan here.
 */
const QUERY_BY_ROUTE = Object.freeze({
  '/exploracion': '?q=saldo',
})

/** The two themes, spelled as `design/sistema.py` spells them. */
const THEMES = Object.freeze(['corriente', 'institucional'])

/**
 * Theme the shell paints when it writes no `data-tema` at all.
 *
 * `useTema` emits the attribute only for the override, because the default
 * theme IS the `@theme` block of the generated stylesheet. So an absent
 * attribute is not a failure to apply the cookie: it is how the default theme
 * looks, and the check below has to read it that way or it would reject the
 * two captures that document precisely that theme.
 */
const IMPLICIT_THEME = 'corriente'

/** The two colour modes, spelled as the cookie stores them. */
const MODES = Object.freeze(['claro', 'oscuro'])

/** Portal under capture, without a trailing slash. */
function baseUrl() {
  return (process.env.CAPTURAS_BASE_URL ?? 'http://localhost:3001').replace(/\/+$/, '')
}

/** Device pixel ratio of the PNG; the default is the archived one. */
function deviceScaleFactor() {
  const raw = Number.parseInt(process.env.CAPTURAS_ESCALA ?? '1', 10)
  return Number.isFinite(raw) && raw > 0 ? raw : 1
}

/**
 * Folder the run writes into.
 *
 * @returns {string} Absolute path of the output folder.
 */
export function outputDir() {
  const explicit = process.env.CAPTURAS_SALIDA
  if (explicit !== undefined && explicit !== '') {
    return resolve(explicit)
  }
  return join(REPO_ROOT, 'docs', 'entregables', 'figuras', 'a4', 'tema')
}

/**
 * One screenshot job of this runner.
 *
 * @typedef {object} ThemeJob
 * @property {string} route Portal path, exactly as `PROTOTIPOS` declares it.
 * @property {'operativo'|'analista'|'directivo'|'admin'} role Demonstration
 *   profile the session is opened with.
 * @property {'corriente'|'institucional'} theme Theme cookie value.
 * @property {'claro'|'oscuro'} mode Colour mode cookie value.
 * @property {string} fileName Name the `.tex` prints.
 */

/**
 * Builds the eleven jobs, from the plan the sibling module derives.
 *
 * The seven prototype jobs take their route and their role from that plan, so
 * a screen added to the navigation contract shows up here too. The four
 * combination jobs reuse the role of `/inicio` for the same reason: a hard
 * coded `operativo` would survive a change of the contract and capture a
 * screen no reader reaches that way.
 *
 * @returns {readonly ThemeJob[]} The eleven jobs, prototypes first.
 */
export function buildThemePlan() {
  const plan = buildCapturePlan()

  const rutasDelPlan = plan.map(job => job.route).sort()
  const rutasDeclaradas = Object.keys(STEM_BY_ROUTE).sort()
  if (rutasDelPlan.join('|') !== rutasDeclaradas.join('|')) {
    throw new Error(
      'los nombres de archivo declarados ya no cubren el contrato de navegacion.\n'
      + `  plan:      ${rutasDelPlan.join(', ')}\n`
      + `  declarado: ${rutasDeclaradas.join(', ')}`,
    )
  }

  const inicio = plan.find(job => job.route === COMBINATION_ROUTE)
  if (inicio === undefined) {
    throw new Error(`${COMBINATION_ROUTE} ya no esta en PROTOTIPOS, y es la ruta de las cuatro combinaciones`)
  }

  const pantallas = plan.map(job => Object.freeze({
    route: job.route,
    role: job.role,
    theme: 'institucional',
    mode: 'claro',
    fileName: `institucional_claro_${STEM_BY_ROUTE[job.route]}.png`,
  }))

  const combinaciones = []
  for (const theme of THEMES) {
    for (const mode of MODES) {
      combinaciones.push(Object.freeze({
        route: COMBINATION_ROUTE,
        role: inicio.role,
        theme,
        mode,
        fileName: `combinacion_${theme}_${mode}_inicio.png`,
      }))
    }
  }

  return Object.freeze([...pantallas, ...combinaciones])
}

/**
 * Loads Playwright from the frontend package, or explains how to install it.
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
 * Waits until the page has stopped fetching and has finished painting text.
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
 * Opens a demonstration session through the entry screen of the portal.
 *
 * Through the interface and not through a bare request: the Nitro route applies
 * `exigirOrigenPropio` and answers 403 to a call without same origin headers.
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
      // The button detached: the click of the previous attempt did land, and
      // the page is already navigating away.
    }
    try {
      await page.waitForURL(url => url.pathname !== PUBLIC_ROUTE, { timeout: SELECTOR_TIMEOUT })
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
 * Verifies that the shell really is painting the theme and the mode asked for.
 *
 * The attributes live on the root element and the server writes them from the
 * cookies before the first paint. Reading them back is what turns "the cookie
 * was set" into "the screenshot shows that theme": a capture taken with the
 * cookie ignored would be indistinguishable from a correct one by file size.
 *
 * @param {object} page Playwright page.
 * @param {ThemeJob} job Job being run.
 * @returns {Promise<void>}
 */
async function assertAppearance(page, job) {
  const crudo = await page.evaluate(() => ({
    tema: document.documentElement.dataset.tema ?? '',
    modo: document.documentElement.dataset.modo ?? '',
  }))
  const tema = crudo.tema === '' ? IMPLICIT_THEME : crudo.tema
  if (tema !== job.theme || crudo.modo !== job.mode) {
    throw new Error(
      `${job.fileName} se iba a tomar con tema=${tema} modo=${crudo.modo}, `
      + `y pedia tema=${job.theme} modo=${job.mode}`,
    )
  }
}

/**
 * Runs one job against a live dev server and writes the PNG.
 *
 * @param {ThemeJob} job Job to run.
 * @param {string} carpeta Folder the PNG is written into.
 * @param {object} browser Browser to reuse.
 * @returns {Promise<string>} Absolute path of the file written.
 */
export async function runThemeCapture(job, carpeta, browser) {
  const target = resolve(carpeta, job.fileName)
  const portal = baseUrl()

  // One context per job: the session of a role must never leak into the next
  // screen, and neither must the appearance of the previous combination.
  const context = await browser.newContext({
    viewport: { ...VIEWPORT },
    deviceScaleFactor: deviceScaleFactor(),
    colorScheme: job.mode === 'oscuro' ? 'dark' : 'light',
    reducedMotion: 'reduce',
    locale: 'es-MX',
  })
  context.setDefaultTimeout(SELECTOR_TIMEOUT)
  context.setDefaultNavigationTimeout(NAVIGATION_TIMEOUT)

  await context.addCookies([
    { name: LOCALE_COOKIE, value: 'es', url: portal },
    { name: MODE_COOKIE, value: job.mode, url: portal },
    { name: THEME_COOKIE, value: job.theme, url: portal },
  ])

  const page = await context.newPage()
  try {
    // The entry screen is captured signed out: it is the door, and a session
    // would show a screen no reader reaches that way.
    if (job.route !== PUBLIC_ROUTE) {
      await openSession(page, job.role)
    }

    const consulta = QUERY_BY_ROUTE[job.route] ?? ''
    await page.goto(`${portal}${job.route}${consulta}`, { waitUntil: 'domcontentloaded' })
    await waitForQuiet(page)
    await assertAppearance(page, job)

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

    await mkdir(carpeta, { recursive: true })
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
  }
}

/**
 * Runs the eleven jobs with a single browser and reports one line per job.
 *
 * @returns {Promise<number>} Process exit code.
 */
async function main() {
  const carpeta = outputDir()
  const plan = buildThemePlan()
  const { chromium } = await loadPlaywright()
  const browser = await launchBrowser(chromium)
  const failures = []

  process.stdout.write(`portal:   ${baseUrl()}\n`)
  process.stdout.write(`salida:   ${carpeta}\n`)
  process.stdout.write(`viewport: ${VIEWPORT.width}x${VIEWPORT.height} @${deviceScaleFactor()}x\n\n`)

  try {
    await mkdir(carpeta, { recursive: true })
    for (const job of plan) {
      const destino = `${job.route}${QUERY_BY_ROUTE[job.route] ?? ''}`
      const label = `${job.fileName.padEnd(42)} ${destino.padEnd(24)} ${job.theme}/${job.mode}`
      try {
        const written = await runThemeCapture(job, carpeta, browser)
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

// Only when invoked directly: importing the module must not launch a browser.
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
