import type { VueWrapper } from '@vue/test-utils'
import type { Component } from 'vue'
import type { ClaveComposicion } from '~/types/espacios'
import type { RolUsuario, SesionUsuario } from '~/types/sesion'

import { flushPromises, mount } from '@vue/test-utils'
import { defineComponent } from 'vue'
import { createMemoryHistory, createRouter } from 'vue-router'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import BloqueLista from '~/components/inicio/BloqueLista.vue'
import EspacioAnalista from '~/components/inicio/EspacioAnalista.vue'
import EspacioDirectivo from '~/components/inicio/EspacioDirectivo.vue'
import EspacioOperativo from '~/components/inicio/EspacioOperativo.vue'
import { bloquesDe, destinosDe, RUTA_INICIO } from '~/utils/espaciosTrabajo'
import { formatearFecha } from '~/utils/fechas'
import { BUSQUEDAS_RECIENTES, INDICADORES } from '~/utils/muestrasInicio'
import { RUTAS_CONTRATO } from '~/utils/navegacion'
import { type CodigoIdioma, crearI18nDePrueba, mensaje } from './i18nDePrueba'

/**
 * US-027 — the three compositions of the home screen, and the page that picks
 * one.
 *
 * The compositions are mounted directly, one by one. With a single page full of
 * `v-if` every assertion about any composition would have to mount the whole
 * screen and double the session first, so the scaffolding would be paid three
 * times and a regression in role resolution would turn the three of them red at
 * once, hiding which one actually broke. Here the role resolution is tested
 * once, over a pure function, in `test/espaciosTrabajo.spec.ts`.
 *
 * What is deliberately NOT asserted: the exact layout -how many columns, which
 * paddings-. Another User Story may recompose this screen on Saturday for the
 * report figures, and pinning the markup would be debt erased by the first real
 * change. What is pinned is the ORDER, because the order is the acceptance
 * criterion and it is also the keyboard focus order.
 */

/** Session the doubled composable reports, driven by each test. */
const doble = vi.hoisted(() => ({
  sesion: null as SesionUsuario | null,
  cargando: false,
}))

vi.mock('~/composables/useSesion', async () => {
  const { computed } = await import('vue')
  return {
    useSesion: () => ({
      sesion: computed(() => doble.sesion),
      cargando: computed(() => doble.cargando),
    }),
  }
})

const EnlaceStub = defineComponent({
  props: { to: { type: String, required: true } },
  template: '<a :href="to"><slot /></a>',
})

const router = createRouter({
  history: createMemoryHistory(),
  routes: RUTAS_CONTRATO.map(path => ({
    path,
    component: defineComponent({ template: '<div />' }),
  })),
})

const COMPOSICIONES: Readonly<Record<ClaveComposicion, Component>> = {
  operativo: EspacioOperativo,
  analista: EspacioAnalista,
  directivo: EspacioDirectivo,
}

const CLAVES: readonly ClaveComposicion[] = ['operativo', 'analista', 'directivo']

interface OpcionesDeMontaje {
  cargando?: boolean
  nombre?: string
  rol?: RolUsuario | null
  idioma?: CodigoIdioma
}

function montarComposicion(
  clave: ClaveComposicion,
  opciones: OpcionesDeMontaje = {},
): VueWrapper {
  return mount(COMPOSICIONES[clave], {
    props: {
      cargando: opciones.cargando ?? false,
      nombre: opciones.nombre ?? 'Laura Méndez',
      rol: opciones.rol === undefined ? 'operativo' : opciones.rol,
    },
    global: {
      plugins: [router, crearI18nDePrueba(opciones.idioma ?? 'es')],
      components: { NuxtLink: EnlaceStub },
      stubs: { Icon: true },
    },
  })
}

/** Blocks of a mounted composition, in document order. */
function bloquesEnElDom(wrapper: VueWrapper): string[] {
  return wrapper.findAll('[data-bloque]').map(bloque => bloque.attributes('data-bloque') ?? '')
}

async function montarPagina(idioma: CodigoIdioma = 'es'): Promise<VueWrapper> {
  const modulo = (await import('~/pages/inicio.vue')) as { default: Component }
  await router.push(RUTA_INICIO)
  await router.isReady()

  return mount(modulo.default, {
    global: {
      plugins: [router, crearI18nDePrueba(idioma)],
      components: { NuxtLink: EnlaceStub },
      stubs: { Icon: true },
    },
  })
}

beforeEach(() => {
  doble.sesion = null
  doble.cargando = false
  vi.stubGlobal('definePageMeta', () => undefined)
})

afterEach(() => {
  vi.unstubAllGlobals()
  vi.useRealTimers()
})

describe('cada composicion abre por lo que ese perfil hace primero', () => {
  it('la operativa abre con el buscador dominante', () => {
    // The primary persona locates and checks a figure: anything above the
    // search box costs her a scroll on the one action she always performs.
    const wrapper = montarComposicion('operativo')
    const primero = wrapper.findAll('[data-bloque]')[0]

    expect(primero?.attributes('data-bloque')).toBe('buscador')
    expect(primero?.attributes('data-enfasis')).toBe('dominante')
  })

  it('la analista abre con el explorador y las exportaciones', () => {
    // Sorted "for consistency", the analyst would receive first the search box
    // that is not their task and last the queries they built yesterday.
    expect(bloquesEnElDom(montarComposicion('analista')).slice(0, 2)).toEqual([
      'explorador',
      'exportaciones',
    ])
  })

  it('la directiva muestra cuatro tarjetas antes que el buscador reducido', () => {
    // Cards below the fold would make the executive screen the operative one
    // with a different title. Four is the floor the criterion names, and each
    // one has to carry its label, its timestamp and its figure: a card that
    // lost the cut-off would be a number with no provenance, which is the one
    // thing this product promises it never shows.
    const wrapper = montarComposicion('directivo')
    const bloques = bloquesEnElDom(wrapper)
    const buscador = wrapper.get('[data-bloque="buscador"]')
    const tarjetas = wrapper.findAll('[data-indicador]')

    expect(bloques[0]).toBe('indicadores')
    expect(tarjetas.length).toBeGreaterThanOrEqual(4)
    for (const tarjeta of tarjetas) {
      expect(tarjeta.get('h3').text().length).toBeGreaterThan(0)
      expect(tarjeta.get('[data-marca-tiempo]').attributes('datetime')).toBeTruthy()
      expect(tarjeta.get('[data-cifra]').classes()).toContain('font-mono')
    }
    expect(buscador.attributes('data-enfasis')).toBe('reducido')
    expect(bloques.indexOf('buscador')).toBeGreaterThan(0)
  })

  it.each(CLAVES)('el orden del DOM de %s es el del contrato de bloques', (clave) => {
    // The defect: template and contract drift apart, and then the document of
    // the report describes an order the screen does not have.
    expect(bloquesEnElDom(montarComposicion(clave))).toEqual([...bloquesDe(clave)])
  })

  it.each(CLAVES)('%s enlaza solo a los destinos que su contrato declara', (clave) => {
    // A route typed straight into a template escapes every assertion made over
    // the contract, and answers 404 in the middle of the demonstration.
    const enlaces = montarComposicion(clave)
      .findAll('a[href]')
      .map(enlace => (enlace.attributes('href') ?? '').split('?')[0] ?? '')

    expect(enlaces.length).toBeGreaterThan(0)
    for (const enlace of new Set(enlaces)) {
      expect(destinosDe(clave), `${clave} -> ${enlace}`).toContain(enlace)
    }
  })
})

describe('las composiciones se dejan leer y recorrer', () => {
  it.each(CLAVES)('%s no introduce un segundo encabezado de primer nivel', (clave) => {
    // The page already owns the only `h1` of the screen, taken from the A3
    // branch, and `test/pantallas.spec.ts` pins that there is exactly one.
    expect(montarComposicion(clave).findAll('h1')).toHaveLength(0)
  })

  it.each(CLAVES)('%s baja de nivel de encabezado sin saltos', (clave) => {
    // A block that titles with `h4` because it looks smaller announces a false
    // hierarchy to a screen reader.
    const niveles = montarComposicion(clave)
      .findAll('h1, h2, h3, h4, h5, h6')
      .map(encabezado => Number(encabezado.element.tagName.slice(1)))

    expect(niveles.length).toBeGreaterThan(0)
    expect(niveles[0]).toBe(2)
    for (const [indice, nivel] of niveles.entries()) {
      expect(nivel - (niveles[indice - 1] ?? nivel), `${clave}:${indice}`).toBeLessThanOrEqual(1)
    }
  })

  it.each(CLAVES)('%s rotula cada bloque con un encabezado que existe', (clave) => {
    // Without `aria-labelledby` a screen reader announces "region" four times
    // in a row and the reader cannot tell favourites from alerts.
    const wrapper = montarComposicion(clave)

    for (const bloque of wrapper.findAll('[data-bloque]')) {
      const idRotulo = bloque.attributes('aria-labelledby')
      expect(idRotulo, bloque.attributes('data-bloque')).toBeTruthy()

      const rotulo = wrapper.element.querySelector(`[id="${idRotulo}"]`)
      expect(rotulo?.textContent?.trim(), idRotulo).toBeTruthy()
    }
  })
})

describe('los estados no felices del bloque de lista estan disenados', () => {
  function montarBloque(elementos: typeof BUSQUEDAS_RECIENTES, cargando = false): VueWrapper {
    return mount(BloqueLista, {
      props: {
        bloque: 'recientes',
        claveTitulo: 'workspace.recent.title',
        claveVacio: 'workspace.recent.empty',
        elementos,
        cargando,
      },
      global: {
        plugins: [router, crearI18nDePrueba()],
        components: { NuxtLink: EnlaceStub },
        stubs: { Icon: true },
      },
    })
  }

  it('sin elementos explica el vacio en vez de pintar una lista de cero filas', () => {
    // An empty `<ul>` is a block that looks broken; the designed empty state
    // says what would appear there and why it does not.
    const wrapper = montarBloque([])

    expect(wrapper.get('[data-bloque]').attributes('data-estado')).toBe('vacio')
    expect(wrapper.findAll('ul')).toHaveLength(0)
    expect(wrapper.get('[data-vacio]').text()).toBe(mensaje('es', 'workspace.recent.empty'))
  })

  it('cargando reserva exactamente las filas que va a ocupar', () => {
    // Layout jump: a spinner of another size makes the whole column move the
    // moment the session resolves, which is the defect this state exists to
    // avoid. Same row count and the same row class, so the height is equal by
    // construction and not by coincidence.
    const wrapper = montarBloque(BUSQUEDAS_RECIENTES, true)
    const esqueletos = wrapper.findAll('[data-esqueleto]')

    expect(wrapper.get('[data-bloque]').attributes('data-estado')).toBe('cargando')
    expect(wrapper.get('[data-bloque]').attributes('aria-busy')).toBe('true')
    expect(esqueletos).toHaveLength(BUSQUEDAS_RECIENTES.length)

    const filaReal = montarBloque(BUSQUEDAS_RECIENTES).findAll('li')[0]
    expect(esqueletos[0]?.classes()).toEqual(filaReal?.classes())
  })

  it('no ofrece enlaces mientras carga', () => {
    // A link over a placeholder invites a click that leads nowhere yet.
    expect(montarBloque(BUSQUEDAS_RECIENTES, true).findAll('a')).toHaveLength(0)
  })

  it('las tarjetas de indicador reservan su caja mientras carga', () => {
    // The executive composition opens with three cards, so they are the tallest
    // thing on the screen: if they collapsed while the session resolved, the
    // search box and the two lists below would jump the moment it arrived.
    const cargando = montarComposicion('directivo', { cargando: true })
    const resuelta = montarComposicion('directivo')

    const tarjetasCargando = cargando.findAll('[data-indicador]')
    expect(tarjetasCargando).toHaveLength(INDICADORES.length)
    expect(cargando.get('[data-bloque="indicadores"]').attributes('data-estado')).toBe('cargando')
    expect(tarjetasCargando[0]?.classes()).toEqual(
      resuelta.findAll('[data-indicador]')[0]?.classes(),
    )
    expect(cargando.findAll('[data-variacion]')).toHaveLength(0)
  })
})

describe('la interfaz de las composiciones es bilingue de verdad', () => {
  it.each(CLAVES)('%s no deja ninguna clave sin resolver', (clave) => {
    // vue-i18n prints an unknown key verbatim, so a typo reaches the captured
    // figure of the report as the literal text `workspace.recent.title`.
    for (const idioma of ['es', 'en'] as const) {
      expect(montarComposicion(clave, { idioma }).text(), idioma).not.toMatch(/workspace\./)
    }
  })

  it.each(CLAVES)('%s cambia de redaccion al cambiar de idioma', (clave) => {
    // A Spanish literal left in a template renders the same sentence in both
    // languages and nothing else would notice.
    const enEspanol = montarComposicion(clave, { idioma: 'es' }).text()
    const enIngles = montarComposicion(clave, { idioma: 'en' }).text()

    expect(enIngles).not.toBe(enEspanol)
    expect(enIngles).toContain(mensaje('en', 'workspace.sample.badge'))
    expect(enEspanol).toContain(mensaje('es', 'workspace.sample.badge'))
  })

  it('saluda con el nombre de la sesion y nombra el perfil', () => {
    const texto = montarComposicion('analista', { nombre: 'Diego Hernández', rol: 'analista' })
      .get('[data-cabecera-espacio]')
      .text()

    expect(texto).toContain('Diego Hernández')
    expect(texto).toContain(mensaje('es', 'authz.role.analista'))
  })
})

describe('los datos de ejemplo se leen como ejemplo', () => {
  it.each(CLAVES)('%s declara el origen de todo bloque con datos', (clave) => {
    // Without the badge a synthetic figure of a prototype can be read as an
    // institutional one, which is the single reading this deliverable cannot
    // afford. The search box is exempt because it holds no data.
    const wrapper = montarComposicion(clave)

    for (const bloque of wrapper.findAll('[data-bloque]')) {
      if (bloque.attributes('data-bloque') === 'buscador') {
        continue
      }
      const declarado
        = bloque.attributes('data-origen') === 'ejemplo'
          || bloque.find('[data-origen="ejemplo"]').exists()

      expect(declarado, `${clave}:${bloque.attributes('data-bloque')}`).toBe(true)
    }
  })

  it.each(CLAVES)('%s no depende del reloj del proceso', (clave) => {
    // With relative dates the figure captured on Saturday would not match the
    // one captured on Wednesday, and the report would document a screen that no
    // longer exists.
    vi.useFakeTimers()

    vi.setSystemTime(new Date('2026-08-12T09:00:00Z'))
    const enAgosto = montarComposicion(clave).text()
    vi.setSystemTime(new Date('2027-03-04T22:15:00Z'))
    const enMarzo = montarComposicion(clave).text()

    expect(enMarzo).toBe(enAgosto)
  })

  it('formatea las fechas en UTC y no en la zona del proceso', () => {
    // Without a fixed time zone the server pass and the browser format the same
    // instant differently, Vue reports a hydration mismatch on every date and
    // the text visibly swaps after the page settles.
    const original = process.env.TZ
    try {
      process.env.TZ = 'UTC'
      const enUtc = formatearFecha('2026-08-12T02:00:00Z', 'es')
      process.env.TZ = 'America/Mexico_City'
      const enMexico = formatearFecha('2026-08-12T02:00:00Z', 'es')

      expect(enMexico).toBe(enUtc)
    }
    finally {
      process.env.TZ = original
    }
  })
})

describe('el buscador unificado lleva el termino al explorador', () => {
  it('navega a exploracion con el termino escrito', async () => {
    // If the form reloaded the page or dropped the term, the demonstration
    // would break on the very first click of the guided walkthrough.
    const wrapper = montarComposicion('operativo')
    await wrapper.get('[data-campo-busqueda]').setValue('ratio_lcr')
    await wrapper.get('form').trigger('submit')
    await flushPromises()

    expect(router.currentRoute.value.path).toBe('/exploracion')
    expect(router.currentRoute.value.query.q).toBe('ratio_lcr')
  })

  it('no navega con el campo vacio', async () => {
    // Navigating with no term lands on a results screen with nothing to show,
    // which reads as a product that lost the search the reader just typed.
    await router.push(RUTA_INICIO)
    const wrapper = montarComposicion('operativo')
    await wrapper.get('[data-campo-busqueda]').setValue('   ')
    await wrapper.get('form').trigger('submit')
    await flushPromises()

    expect(router.currentRoute.value.path).toBe(RUTA_INICIO)
    expect(wrapper.get('[data-accion-busqueda]').attributes('disabled')).toBeDefined()
  })
})

describe('la pagina de inicio monta el espacio del rol de la sesion', () => {
  it.each([
    ['operativo', 'operativo'],
    ['analista', 'analista'],
    ['directivo', 'directivo'],
    ['admin', 'operativo'],
  ] as const)('con el perfil %s pinta la composicion %s', async (rol, esperada) => {
    // The heart of the User Story. The administrator falls back to the
    // operative composition on purpose: `/inicio` is not forbidden to them and
    // the most general layout is the honest default.
    doble.sesion = { usuario: 'x', nombre: 'Nombre de prueba', rol }

    const wrapper = await montarPagina()

    expect(wrapper.get('[data-espacio]').attributes('data-espacio')).toBe(esperada)
  })

  it('sin sesion resuelta sigue sirviendo una pantalla, en estado de carga', async () => {
    // During the first server pass the guard has not answered yet. A blank
    // screen there reads as a page that failed to load.
    doble.cargando = true

    const wrapper = await montarPagina()

    expect(wrapper.get('[data-espacio]').attributes('data-espacio')).toBe('operativo')
    expect(wrapper.get('[data-bloque="recientes"]').attributes('data-estado')).toBe('cargando')
  })

  it('conserva la ruta, el unico encabezado y el parrafo de resumen del contrato', async () => {
    // These three are what keeps `test/pantallas.spec.ts` green without editing
    // it, and that suite is shared with two other User Stories this week. The
    // failure belongs here, not there.
    doble.sesion = { usuario: 'lmendez', nombre: 'Laura Méndez', rol: 'operativo' }

    const wrapper = await montarPagina()

    expect(wrapper.get('[data-ruta]').attributes('data-ruta')).toBe(RUTA_INICIO)
    expect(wrapper.findAll('h1')).toHaveLength(1)
    expect(wrapper.get('h1').text()).toBe(mensaje('es', 'nav.module.home'))
    expect(wrapper.get('p').text()).toBe(mensaje('es', 'screen.home.description'))
  })
})
