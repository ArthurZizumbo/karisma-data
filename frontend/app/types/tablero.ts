/**
 * Shared vocabulary of the high performance dashboard (US-025).
 *
 * Everything the chart, the store, the table and the agent context speak is
 * declared here once. US-026 and US-029 consume these types and do not edit
 * them: a second spelling of `FiltrosTablero` is how the dashboard and the chat
 * end up describing two different views of the same screen.
 */

/** The three numeric columns the preaggregated series offers. */
export type MetricaTablero = 'saldo_disponible_mxn' | 'ratio_lcr' | 'n_posiciones'

/** How the 250 keys are collapsed before they reach the browser. */
export type AgrupacionTablero = 'unidad_negocio' | 'divisa' | 'bucket_venc' | 'serie'

/** Reading density. 'completa' is the 250 line, 500 000 point evidence load. */
export type DensidadTablero = 'resumen' | 'detalle' | 'completa'

/** Dimension a drill-down narrows. */
export type DimensionDrill = 'unidadNegocio' | 'divisa' | 'bucketVenc' | 'serie' | 'rangoFechas'

/** Which control the reader used. Provenance, not decoration: US-029 reads it. */
export type OrigenInteraccion = 'grafica' | 'tabla' | 'leyenda' | 'control'

/** State of the panel. Shared vocabulary with the `data-estado` attribute. */
export type EstadoTablero = 'cargando' | 'listo' | 'vacio' | 'sin-datos' | 'error'

/** Closed window of the time axis, in ISO dates. */
export interface RangoFechas {
  desde: string
  hasta: string
}

/** Everything that narrows the view. Travels to the agent on every chat turn. */
export interface FiltrosTablero {
  metrica: MetricaTablero
  agrupacion: AgrupacionTablero
  unidadNegocio: readonly string[]
  divisa: readonly string[]
  bucketVenc: readonly string[]
  seriesId: readonly number[]
  rangoFechas: RangoFechas | null
}

/** Where a drill-down came from. Without it the chat context has no provenance. */
export interface InteraccionTablero {
  origen: OrigenInteraccion
  dimension: DimensionDrill
  valor: string | number | RangoFechas | null
  momento: string
}

/** Visible slice of the x axis, as dataZoom percentages. */
export interface VentanaTablero {
  inicio: number
  fin: number
}

/** Serialisable snapshot travelling to the agent (TwinBI). No Vue proxies. */
export interface ContextoAgente {
  ruta: string
  filtros: FiltrosTablero
  densidad: DensidadTablero
  nivel: NivelRevelacion
  ventana: VentanaTablero
  seriesVisibles: readonly number[]
  origen: OrigenSerie | null
}

/** Progressive disclosure rung: 1 summary, 2 drilled lines, 3 detail table. */
export type NivelRevelacion = 1 | 2 | 3

/** One line of the chart, as the frame catalogue declares it. */
export interface EtiquetaSerie {
  clave: string
  serieId: number | null
  labelEs: string
  labelEn: string
}

/** Provenance of the loaded frame. The payload US-029 paints as lineage. */
export interface OrigenSerie {
  silo: string
  archivo: string
  filasAgregadas: number
  filasCrudas: number | null
  generadoPor: string
  semilla: number | null
  transformaciones: readonly string[]
  notaTipoCambioEs: string
  notaTipoCambioEn: string
}

/** Server side reduction that produced the points actually received. */
export interface ReduccionSerie {
  metodo: string
  bloque: number
  puntosOriginales: number
}

/** Cardinalities the frame declares in its own header. */
export interface ConteoSerie {
  puntos: number
  fechas: number
  series: number
}

/** Decoded KSER1 frame. The three arrays are views over the received buffer. */
export interface MarcoSerie {
  metrica: MetricaTablero
  agrupacion: AgrupacionTablero
  unidad: string
  fechaMin: string
  fechaMax: string
  /** Days since the epoch, UTC. One entry per column of the grid. */
  fechas: Int32Array
  /** Key of each line, 65535 when the line is an aggregate of several. */
  seriesId: Uint16Array
  /** Row major: line i occupies [i * conteo.fechas, (i + 1) * conteo.fechas). */
  valores: Float32Array
  catalogo: readonly EtiquetaSerie[]
  conteo: ConteoSerie
  reduccion: ReduccionSerie
  origen: OrigenSerie
}

/**
 * One entry of the HTML legend.
 *
 * The legend is HTML and not the ECharts one because a canvas legend cannot be
 * reached with the keyboard, cannot be read aloud and cannot carry a marker
 * shape next to a translated label.
 */
export interface EntradaLeyenda {
  /** Position of the line within the frame. */
  indice: number
  /** Key of the line, or null when the line is an aggregate of several. */
  serieId: number | null
  /** Label already resolved to the language on screen. */
  etiqueta: string
  /** Colour already resolved for the colour mode on screen. */
  color: string
  /** Icon of the marker shape, from the single icon family. */
  icono: string
  /** Stroke pattern as a CSS background. */
  patron: string
  /** Whether the reader kept this line switched on. */
  activa: boolean
  /** False for a line drawn in the muted grey of the full view. */
  coloreada: boolean
}

/**
 * One row of the table alternative to the chart.
 *
 * The row arrives already formatted. The table renders and does not compute:
 * two places deciding how a balance is written is how a screen ends up showing
 * two different figures for the same number.
 */
export interface FilaTabla {
  /** Stable key for the render, unique within the table. */
  clave: string
  /** Row header: the line label, or the date in the per point shape. */
  encabezado: string
  /** Position of the line within the frame, or null when the row is a point. */
  indiceLinea: number | null
  /** Identifier of the line, as the reader's selection expresses it. */
  identificador: number | null
  /** Formatted cells, in the order of the declared columns. */
  celdas: readonly string[]
}

/** Descriptive statistics of one line, computed over that line alone. */
export interface EstadisticaSerie {
  indice: number
  minimo: number
  maximo: number
  media: number
  ultimo: number
  primero: number
  indiceMaximo: number
  indiceMinimo: number
}
