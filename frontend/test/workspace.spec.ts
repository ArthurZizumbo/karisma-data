import type { OrigenSerie } from '~/types/tablero'

import { createPinia, setActivePinia } from 'pinia'
import { isProxy, isReactive } from 'vue'
import { beforeEach, describe, expect, it } from 'vitest'

import { RUTA_TABLERO, useWorkspaceStore } from '~/stores/workspace'

/**
 * US-025 — the shared dashboard-chat workspace.
 *
 * The store is the contract two later User Stories build on: US-026 reads its
 * filters to line its cards up with the chart, and US-029 reads its context to
 * explain why the numbers on screen are the ones on screen. What this file pins
 * down is therefore not "the store works" but the four properties those two
 * depend on: the provenance of every change, a snapshot free of Vue proxies, a
 * serialisation that does not depend on click order, and the absence of any
 * series data inside it.
 */

const ORIGEN: OrigenSerie = {
  silo: 'liquidez',
  archivo: 'data/aggregates/serie_tablero.parquet',
  filasAgregadas: 500000,
  filasCrudas: 1000000,
  generadoPor: 'make data',
  semilla: 20260720,
  transformaciones: ['filtro mto_disp >= 0'],
  notaTipoCambioEs: 'Tipo de cambio sintetico fijo.',
  notaTipoCambioEn: 'Fixed synthetic exchange rate.',
}

beforeEach(() => {
  setActivePinia(createPinia())
})

describe('el drill-down deja constancia de donde vino', () => {
  it('guarda el filtro y su procedencia', () => {
    // Recording the filter without where it came from leaves the lineage
    // overlay of US-029 unable to say why the dashboard is filtered, which is
    // exactly what it promises to say.
    const workspace = useWorkspaceStore()

    workspace.aplicarDrillDown('unidadNegocio', 'TESORERIA', 'grafica')

    expect(workspace.filtros.unidadNegocio).toEqual(['TESORERIA'])
    expect(workspace.ultimaInteraccion?.origen).toBe('grafica')
    expect(workspace.ultimaInteraccion?.dimension).toBe('unidadNegocio')
    expect(workspace.ultimaInteraccion?.valor).toBe('TESORERIA')
    expect(Date.parse(workspace.ultimaInteraccion?.momento ?? '')).not.toBeNaN()
  })

  it('sube al segundo nivel de revelacion cuando algo estrecha la vista', () => {
    const workspace = useWorkspaceStore()
    expect(workspace.nivel).toBe(1)

    workspace.aplicarDrillDown('divisa', 'USD', 'tabla')

    expect(workspace.nivel).toBe(2)
  })

  it('mueve la agrupacion al pedir una serie individual', () => {
    // Sending a key filter while the endpoint still groups by business unit
    // answers five aggregates, so the drill-down would appear to do nothing.
    const workspace = useWorkspaceStore()

    workspace.aplicarDrillDown('serie', 7, 'grafica')

    expect(workspace.filtros.agrupacion).toBe('serie')
    expect(workspace.filtros.seriesId).toEqual([7])
  })

  it('alterna el mismo valor en lugar de acumularlo', () => {
    const workspace = useWorkspaceStore()

    workspace.aplicarDrillDown('divisa', 'USD', 'leyenda')
    workspace.aplicarDrillDown('divisa', 'USD', 'leyenda')

    expect(workspace.filtros.divisa).toEqual([])
  })
})

describe('el contexto que viaja al agente', () => {
  it('es un objeto llano, sin proxies de Vue', () => {
    // Handing over the reactive state would send the agent proxies with
    // getters: JSON.stringify of one of those can throw or produce a different
    // object on each call, and the prompt hash would measure noise.
    const workspace = useWorkspaceStore()
    workspace.aplicarDrillDown('unidadNegocio', 'TESORERIA', 'control')
    workspace.registrarOrigen(ORIGEN)

    const contexto = workspace.contextoAgente

    expect(isProxy(contexto)).toBe(false)
    expect(isReactive(contexto.filtros)).toBe(false)
    expect(isReactive(contexto.filtros.unidadNegocio)).toBe(false)
    expect(() => structuredClone(contexto)).not.toThrow()
    expect(contexto.ruta).toBe(RUTA_TABLERO)
    expect(contexto.origen?.archivo).toBe(ORIGEN.archivo)
  })

  it('serializa la misma cadena para el mismo estado, sea cual sea el orden de los clics', () => {
    // With key order inherited from insertion, the prompt hash would change
    // without the view changing and the observability span would measure the
    // order somebody clicked in.
    const primero = useWorkspaceStore()
    primero.aplicarDrillDown('divisa', 'USD', 'grafica')
    primero.aplicarDrillDown('divisa', 'MXN', 'grafica')
    primero.registrarOrigen(ORIGEN)
    const cadenaA = primero.serializarVista()

    setActivePinia(createPinia())
    const segundo = useWorkspaceStore()
    segundo.aplicarDrillDown('divisa', 'MXN', 'tabla')
    segundo.aplicarDrillDown('divisa', 'USD', 'tabla')
    segundo.registrarOrigen(ORIGEN)

    expect(segundo.serializarVista()).toBe(cadenaA)
  })

  it('ordena las claves del snapshot', () => {
    const workspace = useWorkspaceStore()
    const claves = Object.keys(JSON.parse(workspace.serializarVista()) as Record<string, unknown>)

    expect(claves).toEqual([...claves].sort())
  })
})

describe('el store guarda decisiones, nunca datos', () => {
  it('no admite ningun arreglo tipado ni ninguna lista larga', () => {
    // Parking the frame here would put deep reactivity over half a million
    // numbers and turn every pan into a walk over proxies, which is the
    // performance defect this User Story exists to avoid.
    const workspace = useWorkspaceStore()
    workspace.registrarOrigen(ORIGEN)
    workspace.aplicarDrillDown('serie', 7, 'grafica')
    workspace.alternarSerie(7)

    const sospechosos: string[] = []
    const recorrer = (valor: unknown, ruta: string): void => {
      if (ArrayBuffer.isView(valor) || valor instanceof ArrayBuffer) {
        sospechosos.push(`${ruta}: arreglo binario`)
        return
      }
      if (Array.isArray(valor)) {
        if (valor.length > 300) {
          sospechosos.push(`${ruta}: ${valor.length} elementos`)
        }
        valor.forEach((elemento, indice) => recorrer(elemento, `${ruta}[${indice}]`))
        return
      }
      if (valor !== null && typeof valor === 'object') {
        for (const [clave, dato] of Object.entries(valor)) {
          recorrer(dato, `${ruta}.${clave}`)
        }
      }
    }
    recorrer(workspace.$state, 'workspace')

    expect(sospechosos).toEqual([])
  })
})

describe('volver al estado por omision', () => {
  it('limpiarFiltros no deja nada detras', () => {
    // A partial reset that leaves seriesId behind is a chart that "does not come
    // back", and the reader concludes the screen is broken.
    const workspace = useWorkspaceStore()
    const inicial = useWorkspaceStore().serializarVista()

    workspace.aplicarDrillDown('serie', 3, 'grafica')
    workspace.fijarDensidad('completa')
    workspace.fijarVentana(20, 60, 'grafica')
    workspace.alternarSerie(3)
    workspace.fijarNivel(3)
    workspace.limpiarFiltros()

    expect(workspace.serializarVista()).toBe(inicial)
    expect(workspace.ultimaInteraccion).toBeNull()
    expect(workspace.hayFiltros).toBe(false)
  })

  it('alternarSerie no duplica identificadores', () => {
    // A push without a check shows the same series twice in the legend.
    const workspace = useWorkspaceStore()

    workspace.alternarSerie(4)
    workspace.alternarSerie(4)
    workspace.alternarSerie(2)

    expect(workspace.seriesVisibles).toEqual([2])
  })

  it('olvida la seleccion al cambiar de densidad', () => {
    // The selection is expressed in identifiers of the current view, and the
    // full load regroups by individual key: the same number would silently mean
    // a different line before and after.
    const workspace = useWorkspaceStore()
    workspace.alternarSerie(1)

    workspace.fijarDensidad('completa')

    expect(workspace.seriesVisibles).toEqual([])
  })
})

describe('la ventana visible', () => {
  it('se acota al rango valido y se ordena sola', () => {
    const workspace = useWorkspaceStore()

    workspace.fijarVentana(140, -20, 'grafica')

    expect(workspace.ventana).toEqual({ inicio: 0, fin: 100 })
  })

  it('deja constancia de quien la movio', () => {
    const workspace = useWorkspaceStore()

    workspace.fijarVentana(10, 40, 'control')

    expect(workspace.ventana).toEqual({ inicio: 10, fin: 40 })
    expect(workspace.ultimaInteraccion?.origen).toBe('control')
  })
})
