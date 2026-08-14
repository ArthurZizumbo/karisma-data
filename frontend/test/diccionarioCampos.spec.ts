import type { VueWrapper } from '@vue/test-utils'
import type { RolUsuario } from '~/types/sesion'

import { flushPromises, mount } from '@vue/test-utils'
import { ref, shallowRef } from 'vue'
import { createMemoryHistory, createRouter, RouterLink } from 'vue-router'
import { afterEach, describe, expect, it, vi } from 'vitest'

import GobiernoDiccionarioCampos from '~/components/gobierno/DiccionarioCampos.vue'
import { useSesion } from '~/composables/useSesion'
import { CLAVE_TRANSFORMACION, CODIGOS_FACETA, CODIGOS_TRANSFORMACION, ETAPAS_LINAJE } from '~/types/linaje'
import { RUTA_INDICE, RUTAS_CONTRATO } from '~/utils/navegacion'
import { clavesDe, crearI18nDePrueba, mensaje } from './i18nDePrueba'

/**
 * US-029 — the dictionary, its four states and the journey it opens.
 *
 * Only the transport is replaced. The composables run for real -state machine,
 * query, snake_case mapping and the on demand request- because that is where
 * the defects of this User Story live; a double of the composable would leave
 * exactly the code under test unmeasured.
 */

/** One hit of `GET /api/catalog/search`, as the backend spells it. */
const CAMPO_CRUDO = {
  field_id: 41,
  physical_name: 'saldo_disponible_mxn',
  business_name: 'Saldo disponible',
  definition: 'Saldo de la posicion disponible al cierre del dia habil.',
  source: { code: 'liquidez', display_name: 'Tesoreria y liquidez' },
  owner: { area: 'Tesoreria', steward: 'Ana Ruiz' },
  validity: { valid_from: '2024-01-01', valid_to: null, is_current: true },
  facets: {
    domain: 'liquidez',
    data_type: 'decimal',
    sensitivity: 'interna',
    refresh_frequency: 'diaria',
    certification: 'certificado',
    unit: 'MXN',
    metric_agg: 'sum',
  },
}

const BUSQUEDA_CRUDA = {
  query: 'saldo',
  tsquery: 'saldo',
  total: 1,
  limit: 20,
  offset: 0,
  results: [CAMPO_CRUDO],
  facet_counts: { domain: { liquidez: 1, riesgo: 3 } },
}

const BUSQUEDA_VACIA = { ...BUSQUEDA_CRUDA, total: 0, results: [], facet_counts: { domain: {} } }

/**
 * One hop, spelled the way the endpoint answers.
 *
 * The shape was read from the running API and not invented: the first hop
 * carries the system of record as its code, and the terminal one carries the
 * physical name of the field as its detail, which is what the two ends of the
 * journey have to name.
 */
function paso(
  orden: number,
  etapa: string,
  guardado: boolean,
  sistema: { codigo: string, nombre: string },
  transformacion: { codigo: string, detalle: string },
) {
  return {
    order: orden,
    stage: etapa,
    system_code: sistema.codigo,
    system_name: sistema.nombre,
    transformation_code: transformacion.codigo,
    transformation_detail: transformacion.detalle,
    owner: { area: `Area ${orden}`, steward: `Persona ${orden}` },
    effective_from: '2024-01-01',
    effective_to: orden === 2 ? '2026-12-31' : null,
    is_current: true,
    stored: guardado,
  }
}

const LINAJE_CRUDO = {
  field_id: 41,
  physical_name: 'saldo_disponible_mxn',
  business_name: 'Saldo disponible',
  source: {
    code: 'liquidez',
    display_name: 'Tesoreria y liquidez',
    system_of_record: 'CORE-TESORERIA',
    has_extract: true,
  },
  owner: { area: 'Tesoreria', steward: 'Ana Ruiz' },
  validity: { valid_from: '2024-01-01', valid_to: null, is_current: true },
  facets: CAMPO_CRUDO.facets,
  steps: [
    paso(1, 'origen', true,
      { codigo: 'CORE-TESORERIA', nombre: 'Posicion diaria de tesoreria' },
      { codigo: 'origin_capture', detalle: 'CORE-TESORERIA.POSICION_DIA' }),
    paso(2, 'extraccion', true,
      { codigo: 'KRS-Ingesta', nombre: 'Ingesta de silos' },
      { codigo: 'batch_extract', detalle: 'job_liquidez_nocturno' }),
    paso(3, 'transformacion', true,
      { codigo: 'KRS-Semantica', nombre: 'Capa semantica' },
      { codigo: 'currency_conversion', detalle: 'tipo de cambio de cierre' }),
    paso(4, 'calidad', true,
      { codigo: 'KRS-Calidad', nombre: 'Control de calidad' },
      { codigo: 'quality_rule', detalle: 'conciliacion contra el mayor' }),
    paso(5, 'presentacion', false,
      { codigo: 'KRS-Portal', nombre: 'Karisma Data' },
      { codigo: 'field_publish', detalle: 'saldo_disponible_mxn' }),
  ],
}

interface Escenario {
  /** Body the search answers with, or null when it fails. */
  busqueda?: unknown
  /** Body the lineage answers with, or null when it fails. */
  linaje?: unknown
  falloBusqueda?: unknown
  falloLinaje?: unknown
  /** True to leave the search in flight, which is the loading state. */
  enVuelo?: boolean
  rol?: RolUsuario
  idioma?: 'es' | 'en'
}

interface DobleFetch {
  refrescos: { busqueda: number, linaje: number }
}

/**
 * Installs one `useFetch` double for the two endpoints of the screen.
 *
 * They are told apart by their url: the search is a literal path and the
 * lineage is a computed one, because it only exists once a field was chosen.
 * The `transform` of the composable is applied here, so the snake_case mapping
 * is exercised instead of being bypassed by a pre-mapped fixture.
 */
function instalarFetch(escenario: Escenario): DobleFetch {
  const refrescos = { busqueda: 0, linaje: 0 }

  vi.stubGlobal('useFetch', (ruta: unknown, opciones: {
    transform?: (respuesta: unknown) => unknown
    default?: () => unknown
  }) => {
    const esBusqueda = typeof ruta === 'string'
    const cuerpo = esBusqueda ? escenario.busqueda : escenario.linaje
    const fallo = esBusqueda ? escenario.falloBusqueda : escenario.falloLinaje

    const data = shallowRef<unknown>(opciones.default?.() ?? null)
    const error = shallowRef<unknown>(null)
    const status = ref<'idle' | 'pending' | 'success' | 'error'>('idle')

    const refresh = async (): Promise<void> => {
      if (esBusqueda) {
        refrescos.busqueda += 1
      }
      else {
        refrescos.linaje += 1
      }
      if (fallo !== undefined) {
        error.value = fallo
        status.value = 'error'
        return
      }
      if (esBusqueda && escenario.enVuelo === true) {
        status.value = 'pending'
        return
      }
      data.value = opciones.transform === undefined ? cuerpo : opciones.transform(cuerpo)
      status.value = 'success'
    }

    return { data, error, status, refresh }
  })

  vi.stubGlobal('navigateTo', vi.fn(async () => undefined))

  return { refrescos }
}

let montado: VueWrapper | null = null

/** Mounts the dictionary with a session, a language and a transport. */
function montar(escenario: Escenario = {}) {
  const doble = instalarFetch({ busqueda: BUSQUEDA_CRUDA, linaje: LINAJE_CRUDO, ...escenario })

  const { sesion } = useSesion()
  sesion.value = { usuario: 'demo', nombre: 'Perfil de demostracion', rol: escenario.rol ?? 'operativo' }

  const router = createRouter({
    history: createMemoryHistory(),
    routes: [RUTA_INDICE, ...RUTAS_CONTRATO].map(path => ({
      path,
      component: { template: '<div />' },
    })),
  })

  const wrapper = mount(GobiernoDiccionarioCampos, {
    attachTo: document.body,
    global: {
      plugins: [router, crearI18nDePrueba(escenario.idioma ?? 'es')],
      components: { NuxtLink: RouterLink },
      stubs: { Icon: true },
    },
  })
  montado = wrapper
  return { wrapper, doble }
}

/** Types a term and submits the form, which is the only way to search. */
async function buscar(wrapper: VueWrapper, termino = 'saldo'): Promise<void> {
  await wrapper.get('[data-campo-busqueda]').setValue(termino)
  await wrapper.get('form').trigger('submit')
  await flushPromises()
}

/** Opens the lineage of the first card. */
async function abrirLinaje(wrapper: VueWrapper): Promise<void> {
  await wrapper.get('[data-disparador-linaje]').trigger('click')
  await flushPromises()
  await flushPromises()
}

afterEach(() => {
  montado?.unmount()
  montado = null
  document.body.innerHTML = ''
  vi.unstubAllGlobals()
})

describe('los cuatro estados del diccionario', () => {
  it('el estado inicial no pide nada y explica que hacer', async () => {
    // An `immediate: true` would fire a search for the empty string the moment
    // the screen loads, and the endpoint answers that with a 422.
    const { wrapper, doble } = montar()

    expect(doble.refrescos.busqueda).toBe(0)
    expect(wrapper.get('[data-estado]').attributes('data-estado')).toBe('inicial')
    expect(wrapper.text()).toContain(mensaje('es', 'lineage.dictionary.state.initial.title'))
    expect(wrapper.find('[data-resultados]').exists()).toBe(false)
  })

  it('cargando reserva el sitio de las fichas y lo anuncia', async () => {
    // A spinner of its own height moves everything below it the moment the
    // answer lands, which is the layout jump the criterion forbids.
    const { wrapper } = montar({ enVuelo: true })
    await buscar(wrapper)

    const estado = wrapper.get('[data-estado]')
    expect(estado.attributes('data-estado')).toBe('cargando')
    expect(estado.get('[role="status"]').attributes('aria-busy')).toBe('true')
    expect(estado.findAll('span[aria-hidden="true"]')).toHaveLength(3)
    expect(estado.text()).toContain(mensaje('es', 'lineage.dictionary.state.loading'))
  })

  it('sin resultados muestra un vacio disenado', async () => {
    // A list of zero elements and no text reads as a broken screen.
    const { wrapper } = montar({ busqueda: BUSQUEDA_VACIA })
    await buscar(wrapper, 'nada')

    expect(wrapper.get('[data-estado]').attributes('data-estado')).toBe('vacio')
    expect(wrapper.text()).toContain(mensaje('es', 'lineage.dictionary.state.empty.body'))
  })

  it('el error ofrece reintentar y vuelve a pedir', async () => {
    // An error state with no way out forces a full page reload, and the term
    // the reader typed is lost with it.
    const { wrapper, doble } = montar({ falloBusqueda: { statusCode: 500 } })
    await buscar(wrapper)

    expect(wrapper.get('[data-estado]').attributes('data-estado')).toBe('error')
    expect(wrapper.text()).toContain(mensaje('es', 'lineage.dictionary.state.error.body'))

    await wrapper.get('[data-reintentar-busqueda]').trigger('click')
    await flushPromises()

    expect(doble.refrescos.busqueda).toBe(2)
  })

  it('un 401 termina la sesion en vez de quedarse en blanco', async () => {
    // Without the hook US-017 exported, a session that died mid search leaves a
    // dictionary that silently stops answering and never explains why.
    const { wrapper } = montar({ falloBusqueda: { statusCode: 401 } })
    await buscar(wrapper)

    const navegar = (globalThis as unknown as { navigateTo: ReturnType<typeof vi.fn> }).navigateTo
    expect(navegar).toHaveBeenCalledWith(expect.stringContaining('/acceso?motivo='))
  })
})

describe('el recorrido del dato', () => {
  it('recorrido completo: cinco pasos en orden, del origen a la cifra', async () => {
    // Walking an object instead of the ordered array leaves the order to the
    // engine, and the journey would read starting from the quality control.
    const { wrapper } = montar()
    await buscar(wrapper)
    await abrirLinaje(wrapper)

    const pasos = wrapper.findAll('[data-paso-linaje]')

    expect(pasos).toHaveLength(5)
    expect(pasos.map(nodo => nodo.attributes('data-etapa'))).toEqual([...ETAPAS_LINAJE])
    expect(pasos[0]!.text()).toContain('CORE-TESORERIA')
    expect(pasos[4]!.text()).toContain('saldo_disponible_mxn')
  })

  it('cada paso responde por si mismo', async () => {
    // The criterion asks for the owner and the validity OF EACH HOP: showing
    // them once in the header would answer a different question, because the
    // owner of the extraction job is not the owner of the source.
    const { wrapper } = montar()
    await buscar(wrapper)
    await abrirLinaje(wrapper)

    for (const nodo of wrapper.findAll('[data-paso-linaje]')) {
      expect(nodo.get('[data-transformacion]').text()).not.toBe('')
      expect(nodo.get('[data-propietario]').text()).not.toBe('')
      expect(nodo.get('[data-vigencia]').text()).not.toBe('')
    }
  })

  it('el paso derivado se distingue del sembrado', async () => {
    // If `stored` is not rendered the reader cannot tell what the portal keeps
    // from what it composes, which is the honesty commitment of this journey.
    const { wrapper } = montar()
    await buscar(wrapper)
    await abrirLinaje(wrapper)

    const pasos = wrapper.findAll('[data-paso-linaje]')
    const derivados = pasos.map(nodo => nodo.attributes('data-derivado'))

    expect(derivados).toEqual(['false', 'false', 'false', 'false', 'true'])
    expect(pasos[4]!.text()).toContain(mensaje('es', 'lineage.step.derived'))
    expect(wrapper.get('[data-nota-derivado]').text()).toBe(mensaje('es', 'lineage.panel.derivedNote'))
  })

  it('el error del linaje ofrece reintentar sin cerrar el panel', async () => {
    // A 404 on a field that does not exist has to render the designed error
    // inside the panel, not an empty overlay the reader has to close.
    const { wrapper, doble } = montar({
      falloLinaje: { statusCode: 404, data: { detail: { codigo: 'campo_no_encontrado' } } },
    })
    await buscar(wrapper)
    await abrirLinaje(wrapper)

    const panel = wrapper.get('[data-linaje-overlay]')
    expect(panel.get('[data-estado]').attributes('data-estado')).toBe('error')
    expect(panel.get('[data-codigo-error]').text()).toBe('campo_no_encontrado')

    await wrapper.get('[data-reintentar-linaje]').trigger('click')
    await flushPromises()

    expect(doble.refrescos.linaje).toBe(2)
  })

  it('abrir y cerrar no cambia la lista', async () => {
    // Reordering the results when a panel opens -"last opened first"- would
    // leave the screen different from how the reader found it.
    const { wrapper } = montar()
    await buscar(wrapper)

    const antes = wrapper.get('[data-resultados]').element.outerHTML
    await abrirLinaje(wrapper)
    await wrapper.get('[data-cerrar-linaje]').trigger('click')
    await flushPromises()

    expect(wrapper.get('[data-resultados]').element.outerHTML).toBe(antes)
  })
})

describe('las cadenas del catalogo cubren lo que la pantalla pinta', () => {
  it('todo codigo de transformacion tiene plantilla, y ninguna plantilla sobra', async () => {
    // A code seeded without its key renders the dotted path as visible text, in
    // both languages; a template with no code is copy nobody will ever read.
    const declaradas = clavesDe('es').filter(clave => clave.startsWith('lineage.transformation.'))

    expect(declaradas.sort()).toEqual(
      CODIGOS_TRANSFORMACION.map(codigo => CLAVE_TRANSFORMACION[codigo]).sort(),
    )

    for (const codigo of CODIGOS_TRANSFORMACION) {
      for (const idioma of ['es', 'en'] as const) {
        expect(mensaje(idioma, CLAVE_TRANSFORMACION[codigo]), codigo).toContain('{detail}')
      }
    }
  })

  it('las 34 etiquetas de faceta existen en los dos catalogos', async () => {
    // The card renders a facet by composing its key from the code the backend
    // sends, so a missing value is invisible to the scan of contratos.spec and
    // shows up on screen as `catalog.facet.domain.cartera`.
    const codigos = Object.entries(CODIGOS_FACETA)
    const total = codigos.reduce((suma, [, valores]) => suma + valores.length, 0)

    expect(total).toBe(34)
    for (const [grupo, valores] of codigos) {
      for (const valor of valores) {
        for (const idioma of ['es', 'en'] as const) {
          expect(mensaje(idioma, `catalog.facet.${grupo}.${valor}`)).not.toBe('')
        }
      }
    }
  })

  it('la ficha traduce las facetas en lugar de mostrar el codigo', async () => {
    const { wrapper } = montar()
    await buscar(wrapper)

    const chips = wrapper.findAll('[data-chip-faceta]').map(chip => chip.text())

    expect(chips.join(' ')).toContain(mensaje('es', 'catalog.facet.domain.liquidez'))
    expect(chips.join(' ')).toContain(mensaje('es', 'catalog.facet.unit.MXN'))
    expect(chips.join(' ')).not.toContain('catalog.facet.')
  })
})

describe('acceso cruzado a la bitacora', () => {
  it('solo el perfil de administracion recibe el enlace', async () => {
    // Offering a door that answers with a closed door is the defect US-027
    // identified; whoever cannot enter reads the copy US-017 already wrote.
    const { wrapper } = montar({ rol: 'admin' })

    expect(wrapper.get('[data-acceso-bitacora]').attributes('href')).toBe('/administracion')
    expect(wrapper.find('[data-sin-bitacora]').exists()).toBe(false)
  })

  it.each(['operativo', 'analista', 'directivo'] as const)('con %s el enlace no esta en el DOM', async (rol) => {
    const { wrapper } = montar({ rol })

    expect(wrapper.find('[data-acceso-bitacora]').exists()).toBe(false)
    expect(wrapper.get('[data-sin-bitacora]').text()).toBe(mensaje('es', 'authz.noPermission.requestTo'))
  })
})
