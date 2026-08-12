/**
 * US-026 - the contract the predictive cards of the dashboards screen hang on.
 *
 * Types only, so this module is excluded from coverage by `vitest.config.ts`.
 * The one thing worth stating here is what is deliberately absent: there is no
 * field carrying the visible sentence of a method. The label is derived from
 * `MetodoAplicado` by the single function that knows the templates, so no layer
 * of the tree has a place to park a text the computation did not produce.
 */

/** The three dashboard metrics of S4. Frozen: the grid renders one card each. */
export type MetricaId = 'cobertura-liquidez' | 'saldo-disponible' | 'concentracion-divisa'

/** How a value is rendered. Drives Intl, not business meaning. */
export type UnidadMetrica = 'porcentaje' | 'millones-mxn'

/** Registered projection methods. Adding one without a template does not compile. */
export type IdMetodo = 'ols-lineal'

/**
 * The four states a card can be in.
 *
 * 'error' is a card state and not only a section state because the grid renders
 * three cards whatever the response says: a card that vanished on failure would
 * be a layout shift with another name.
 */
export type EstadoTarjeta = 'cargando' | 'listo' | 'vacio' | 'error'

export interface PuntoMensual {
  /** Calendar month as YYYY-MM. Never a Date: the clock must not leak in. */
  readonly mes: string
  readonly valor: number
}

export interface MetodoAplicado {
  readonly id: IdMetodo
  /** Translation key of the visible method label. Never a sentence. */
  readonly clavePlantilla: string
  /**
   * Parameters measured by the computation, not requested by the caller.
   * Keys are English because they are i18n interpolation names.
   */
  readonly parametros: {
    readonly points: number
    readonly horizon: number
    readonly r2: number
  }
}

export interface Proyeccion {
  readonly metricaId: MetricaId
  /** Last observed month, as it came from the published history. */
  readonly ultimo: PuntoMensual
  /** Projected month, produced by the regression. */
  readonly proyectado: PuntoMensual
  /** Percentage change of the projection against the last observed value. */
  readonly variacionPct: number
  /** Points actually fed to the regression, oldest first. */
  readonly serieUsada: readonly PuntoMensual[]
  readonly metodo: MetodoAplicado
}

export interface MetricaTablero {
  readonly id: MetricaId
  /** Translation key of the visible metric name. */
  readonly claveEtiqueta: string
  readonly unidad: UnidadMetrica
  /** Physical column of the catalogue this metric is derived from. */
  readonly campoOrigen: string
}

export interface HistoricoMetrica {
  readonly id: MetricaId
  readonly campoOrigen: string
  /** Translation key describing how the monthly value was aggregated. */
  readonly claveAgregacion: string
  readonly puntos: readonly PuntoMensual[]
}

export interface VentanaHistorico {
  readonly desde: string
  readonly hasta: string
  readonly meses: number
}

export interface PayloadHistoricos {
  readonly fuente: string
  readonly ventana: VentanaHistorico
  readonly metricas: readonly HistoricoMetrica[]
}

export interface TarjetaPrediccion {
  readonly metrica: MetricaTablero
  readonly historico: HistoricoMetrica | null
  /** Null when there is not enough history. The card then shows the empty state. */
  readonly proyeccion: Proyeccion | null
}
