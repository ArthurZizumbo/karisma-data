import type { Component } from 'vue'

import { readFileSync, readdirSync } from 'node:fs'
import { join, relative } from 'node:path'
import { fileURLToPath } from 'node:url'

import { mount } from '@vue/test-utils'
import { defineComponent, ref } from 'vue'
import { createMemoryHistory, createRouter } from 'vue-router'
import { afterAll, beforeAll, describe, expect, it, vi } from 'vitest'

import Acceso from '~/layouts/acceso.vue'
import Default from '~/layouts/default.vue'
import PantallaDeError from '~/error.vue'
import Portal from '~/layouts/portal.vue'
import Guia from '~/pages/guia.vue'
import Indice from '~/pages/index.vue'
import { RUTA_INDICE, RUTAS_CONTRATO } from '~/utils/navegacion'
import { CONTRASTES, REGLAS_DERIVADAS } from '~/utils/tokens.generated'
import { crearI18nDePrueba } from './i18nDePrueba'

/**
 * QA of 11-ago-2026, finding 1 — the guide contradicted itself inside the PDF.
 *
 * The generated matrix measures muted over surface-alt at 4.27:1 and grades it
 * "AA-grande", valid for large text only. The interface was painting secondary
 * text of 11 to 14 px in that pair: the usage column of the type plate and the
 * rule column of the matrix itself were drawn, at 14 px, in the pair the same
 * screen was declaring insufficient.
 *
 * What this spec fails on, concretely: any element whose resting text colour
 * and nearest resting background resolve to a pair the generator measured
 * below 4.5:1. It is not a snapshot of the markup -it asserts nothing about
 * which elements exist- so a rewritten screen does not touch it; only a screen
 * that reintroduces an insufficient pair does.
 *
 * Two artefacts feed it and neither is retyped here: the hexadecimals come from
 * the generated `@theme`, and the ratios from the generated matrix. If the
 * generator ever remeasures a pair, this spec changes verdict with it, which is
 * the point: the published rule and the markup cannot diverge in silence.
 */

/** Minimum ratio WCAG 2.x demands of normal text (under 18.66 px bold, 24 px). */
const MINIMO_TEXTO_NORMAL = 4.5

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

/** Colour of every `--color-*` token of the generated theme, class name included. */
function coloresDelTema(): Map<string, string> {
  const tema = readFileSync(rutaDelRepositorio('../app/assets/css/main.css'), 'utf8')

  return new Map(
    [...tema.matchAll(/^\s+--color-([a-z0-9-]+)\s*:\s*(#[0-9A-Fa-f]{6})/gm)].map(
      ([, nombre, hex]) => [nombre!, hex!.toUpperCase()],
    ),
  )
}

const COLORES = coloresDelTema()

/** Ratio of every pair the generator measured, keyed by foreground/background. */
const RATIO_POR_PAR = new Map(
  CONTRASTES.map(par => [
    `${par.frenteHex.toUpperCase()}|${par.fondoHex.toUpperCase()}`,
    par.ratio,
  ]),
)

/** `.vue` files that fill something with the alternate row neutral. */
function archivosConFondoAlterno(): string[] {
  const recorrer = (directorio: string): string[] =>
    readdirSync(directorio, { withFileTypes: true }).flatMap(entrada =>
      entrada.isDirectory()
        ? recorrer(join(directorio, entrada.name))
        : [join(directorio, entrada.name)],
    )

  return recorrer(RAIZ_APP)
    .filter(ruta => ruta.endsWith('.vue'))
    .filter(ruta => readFileSync(ruta, 'utf8').includes('bg-surface-alt'))
    .map(ruta => relative(RAIZ_APP, ruta).replace(/\\/g, '/'))
    .sort()
}

/**
 * Every surface the walk below renders, and therefore the only ones it can
 * clear. The list is asserted against the sources: a new file that fills with
 * `bg-surface-alt` has to enter the walk or the spec fails, so the check cannot
 * quietly stop covering the interface.
 */
const SUPERFICIES_CUBIERTAS = [
  'components/comun/CabeceraProducto.vue',
  'components/guia/LaminaBotones.vue',
  'components/guia/LaminaCampos.vue',
  'components/guia/LaminaIconos.vue',
  'components/guia/LaminaTablas.vue',
  'components/guia/LaminaTarjetas.vue',
  'components/guia/LaminaTipografia.vue',
  'components/nav/BotonPrototipo.vue',
  'pages/guia.vue',
  'pages/index.vue',
]

const IconoStub = defineComponent({
  props: { name: { type: String, required: true } },
  // The icon keeps the class it was given: its colour is part of what is walked.
  template: '<span :data-icono-nombre="name"><slot /></span>',
})

const EnlaceStub = defineComponent({
  props: { to: { type: String, required: true } },
  template: '<a :href="to"><slot /></a>',
})

const router = createRouter({
  history: createMemoryHistory(),
  routes: [RUTA_INDICE, ...RUTAS_CONTRATO].map(path => ({
    path,
    component: defineComponent({ template: '<div />' }),
  })),
})

function montar(componente: Component, props: Record<string, unknown> = {}): HTMLElement {
  return mount(componente, {
    props,
    slots: { default: '<p>Contenido de prueba</p>' },
    global: {
      plugins: [router, crearI18nDePrueba('es')],
      components: { Icon: IconoStub, NuxtLink: EnlaceStub },
    },
  }).element as HTMLElement
}

/** Colour token a class names, or undefined when the class names no token. */
function tokenDeClase(clase: string, prefijo: string): string | undefined {
  const nombre = clase.startsWith(prefijo) ? clase.slice(prefijo.length) : undefined
  return nombre !== undefined && COLORES.has(nombre) ? nombre : undefined
}

/**
 * Background tokens an element paints while at rest.
 *
 * `odd:` and `even:` are kept because the striped row paints one of them
 * unconditionally, and text inside such a row has to clear both. Every other
 * variant -`hover:`, `focus-visible:`, `aria-pressed:`- describes a state the
 * reader has to provoke and is out of scope here.
 */
function fondosEnReposo(elemento: Element): string[] {
  return [...elemento.classList]
    .map(clase => clase.replace(/^(?:odd|even):/, ''))
    .map(clase => tokenDeClase(clase, 'bg-'))
    .filter((nombre): nombre is string => nombre !== undefined)
}

interface Infraccion {
  readonly superficie: string
  readonly frente: string
  readonly fondo: string
  readonly ratio: number
  readonly texto: string
}

function infraccionesDe(superficie: string, raiz: HTMLElement): Infraccion[] {
  const infracciones: Infraccion[] = []

  for (const elemento of [raiz, ...raiz.querySelectorAll('*')]) {
    const frentes = [...elemento.classList]
      .map(clase => tokenDeClase(clase, 'text-'))
      .filter((nombre): nombre is string => nombre !== undefined)

    if (frentes.length === 0) {
      continue
    }

    // WCAG 1.4.3 exempts inactive controls: the disabled state is drawn with
    // the muted neutral on purpose, and that is what says it is inactive.
    if (elemento.closest('[disabled], [aria-disabled="true"]') !== null) {
      continue
    }

    let contenedor: Element | null = elemento
    while (contenedor !== null && fondosEnReposo(contenedor).length === 0) {
      contenedor = contenedor.parentElement
    }
    if (contenedor === null) {
      continue
    }

    for (const frente of frentes) {
      for (const fondo of fondosEnReposo(contenedor)) {
        const ratio = RATIO_POR_PAR.get(`${COLORES.get(frente)}|${COLORES.get(fondo)}`)
        if (ratio !== undefined && ratio < MINIMO_TEXTO_NORMAL) {
          infracciones.push({
            superficie,
            frente,
            fondo,
            ratio,
            texto: (elemento.textContent ?? '').trim().slice(0, 40),
          })
        }
      }
    }
  }

  return infracciones
}

describe('ningún texto normal se pinta sobre un par que la matriz mide por debajo de AA', () => {
  beforeAll(async () => {
    vi.stubGlobal('useRuntimeConfig', () => ({ public: { entorno: 'pruebas' } }))
    vi.stubGlobal('useCookie', () => ref(null))
    vi.stubGlobal('clearError', () => undefined)
    vi.stubGlobal('definePageMeta', () => undefined)
    await router.push(RUTA_INDICE)
    await router.isReady()
  })

  afterAll(() => {
    vi.unstubAllGlobals()
  })

  it.each([
    ['índice de prototipos', () => montar(Indice)],
    ['guía de estilos', () => montar(Guia)],
    ['chasis del portal', () => montar(Portal)],
    ['chasis de acceso', () => montar(Acceso)],
    ['chasis por omisión', () => montar(Default)],
    ['pantalla de error', () => montar(PantallaDeError, { error: { statusCode: 404 } })],
  ])('%s', (superficie, render) => {
    const infracciones = infraccionesDe(superficie, render()).map(
      ({ frente, fondo, ratio, texto }) => `${frente} sobre ${fondo} (${ratio}:1) en "${texto}"`,
    )

    expect([...new Set(infracciones)]).toEqual([])
  })

  it('recorre toda superficie de la aplicación que se rellena con el neutro alterno', () => {
    // Without this the walk above would silently stop covering the interface:
    // a new plate filled with surface-alt would never be mounted and its text
    // would go unmeasured.
    expect(archivosConFondoAlterno()).toEqual(SUPERFICIES_CUBIERTAS)
  })
})

describe('la regla que el marcado obedece sigue siendo la que el generador publica', () => {
  it('mide el neutro secundario sobre el relleno alterno por debajo del texto normal', () => {
    // The rule "muted only over surface, ink over surface-alt" is derived from
    // this measurement and from nothing else. Lighten surface-alt or darken
    // muted in uxdoc.sty, regenerate, and the rule loses its basis while every
    // other spec stays green: this is what fails then.
    const par = CONTRASTES.find(
      candidato => candidato.frente === 'muted' && candidato.fondo === 'surface-alt',
    )

    expect(par).toBeDefined()
    expect(par!.ratio).toBeLessThan(MINIMO_TEXTO_NORMAL)
    expect(par!.veredicto).toBe('AA-grande')
  })

  it('publica la regla del neutro secundario entre las reglas derivadas', () => {
    expect(REGLAS_DERIVADAS.filter(regla => regla.includes('muted'))).toHaveLength(1)
  })
})
