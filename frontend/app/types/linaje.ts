/**
 * Vocabulary of the explainable lineage overlay (US-029).
 *
 * The backend answers in `snake_case` because US-008 fixed that contract and
 * FastAPI publishes it that way; the interface works in `camelCase` because
 * that is the TypeScript convention of this repository. The conversion happens
 * ONCE, inside the composables, with an explicit mapping function: neither a
 * component nor the store ever sees a `snake_case` key.
 *
 * Nothing here is a label. Stage, transformation and the seven facets travel as
 * codes and the catalogues translate them, which is the same rule US-008 gave
 * for its own facets: a label stored in the database is a translation nobody
 * can change without a migration.
 */

/**
 * Hop of the journey, in the order the overlay renders them.
 *
 * `presentacion` is composed by the service from `catalog_field` and is never
 * stored, which the payload declares with `stored: false` and the panel shows.
 */
export type EtapaLinaje =
  | 'origen'
  | 'extraccion'
  | 'transformacion'
  | 'calidad'
  | 'presentacion'

/** The five stages in the order the journey happens. */
export const ETAPAS_LINAJE = [
  'origen',
  'extraccion',
  'transformacion',
  'calidad',
  'presentacion',
] as const

/**
 * Transformation codes the interface can render.
 *
 * Nine come from the database CHECK; `field_publish` belongs to the derived
 * step and is deliberately absent from it. The closed union is what makes the
 * template coverage check possible: a code without a template fails to compile,
 * and a template without an entry here fails the spec.
 */
export const CODIGOS_TRANSFORMACION = [
  'origin_capture',
  'batch_extract',
  'stream_extract',
  'type_normalization',
  'currency_conversion',
  'deduplication',
  'business_rule',
  'reconciliation',
  'quality_rule',
  'field_publish',
] as const

export type CodigoTransformacion = typeof CODIGOS_TRANSFORMACION[number]

/** Who answers for a hop. Already resolved server side: no coalesce here. */
export interface PropietarioRef {
  area: string
  steward: string
}

/** Effective period of a definition or of a hop. */
export interface VigenciaRef {
  validFrom: string
  validTo: string | null
  isCurrent: boolean
}

/** The seven filterable attributes of a field, as codes. */
export interface FacetasCampo {
  domain: string
  dataType: string
  sensitivity: string
  refreshFrequency: string
  certification: string
  unit: string | null
  metricAgg: string | null
}

/** One hop of the journey, as the overlay renders it. */
export interface PasoLinaje {
  order: number
  stage: EtapaLinaje
  systemCode: string
  systemName: string
  transformationCode: CodigoTransformacion
  transformationDetail: string
  owner: PropietarioRef
  effectiveFrom: string
  effectiveTo: string | null
  isCurrent: boolean
  /** False on the terminal step, which is composed and not stored. */
  stored: boolean
}

/** Payload of `GET /api/catalog/{entry_id}/lineage`, already in camelCase. */
export interface LinajeCampo {
  fieldId: number
  physicalName: string
  businessName: string
  source: {
    code: string
    displayName: string
    systemOfRecord: string
    hasExtract: boolean
  }
  owner: PropietarioRef
  validity: VigenciaRef
  facets: FacetasCampo
  steps: readonly PasoLinaje[]
}

/** One row of the dictionary. A projection of `CatalogHit`, not a copy of it. */
export interface CampoCatalogo {
  fieldId: number
  physicalName: string
  businessName: string
  definition: string
  source: { code: string, displayName: string }
  owner: PropietarioRef
  validity: VigenciaRef
  facets: FacetasCampo
}

/**
 * State of a request the screen has to draw.
 *
 * `inicial` is not `cargando` with no data: the dictionary opens without asking
 * for anything, and telling the two apart is what lets the empty state say
 * "type a term" instead of spinning forever.
 */
export type EstadoConsulta = 'inicial' | 'cargando' | 'listo' | 'vacio' | 'error'

// --- Wire shapes: the backend contract, before the mapping ------------------

/** Owner block as the backend spells it. */
interface PropietarioCrudo {
  area: string
  steward: string
}

/** Validity block as the backend spells it. */
interface VigenciaCruda {
  valid_from: string
  valid_to: string | null
  is_current: boolean
}

/** Facet block as the backend spells it. */
interface FacetasCrudas {
  domain: string
  data_type: string
  sensitivity: string
  refresh_frequency: string
  certification: string
  unit: string | null
  metric_agg: string | null
}

/** One hit of `GET /api/catalog/search`, with the fields the dictionary uses. */
export interface CampoCrudo {
  field_id: number
  physical_name: string
  business_name: string
  definition: string
  source: { code: string, display_name: string }
  owner: PropietarioCrudo
  validity: VigenciaCruda
  facets: FacetasCrudas
}

/** Body of `GET /api/catalog/search`. */
export interface BusquedaCruda {
  query: string
  total: number
  results: readonly CampoCrudo[]
  facet_counts: Record<string, Record<string, number>>
}

/** One hop as the backend spells it. */
export interface PasoCrudo {
  order: number
  stage: EtapaLinaje
  system_code: string
  system_name: string
  transformation_code: CodigoTransformacion
  transformation_detail: string
  owner: PropietarioCrudo
  effective_from: string
  effective_to: string | null
  is_current: boolean
  stored: boolean
}

/** Body of `GET /api/catalog/{entry_id}/lineage`. */
export interface LinajeCrudo {
  field_id: number
  physical_name: string
  business_name: string
  source: {
    code: string
    display_name: string
    system_of_record: string
    has_extract: boolean
  }
  owner: PropietarioCrudo
  validity: VigenciaCruda
  facets: FacetasCrudas
  steps: readonly PasoCrudo[]
}

// --- Closed vocabularies and their catalogue keys ---------------------------

/**
 * Catalogue key of each stage.
 *
 * An explicit map and not string concatenation: the scan of
 * `test/contratos.spec` only sees keys written as literals, so a key assembled
 * at run time would be invisible to the check that every used key exists, and
 * vue-i18n would print the dotted path on screen in both languages.
 */
export const CLAVE_ETAPA: Record<EtapaLinaje, string> = Object.freeze({
  origen: 'lineage.stage.origen',
  extraccion: 'lineage.stage.extraccion',
  transformacion: 'lineage.stage.transformacion',
  calidad: 'lineage.stage.calidad',
  presentacion: 'lineage.stage.presentacion',
})

/** Catalogue key of each transformation. Every template interpolates {detail}. */
export const CLAVE_TRANSFORMACION: Record<CodigoTransformacion, string> = Object.freeze({
  origin_capture: 'lineage.transformation.origin_capture',
  batch_extract: 'lineage.transformation.batch_extract',
  stream_extract: 'lineage.transformation.stream_extract',
  type_normalization: 'lineage.transformation.type_normalization',
  currency_conversion: 'lineage.transformation.currency_conversion',
  deduplication: 'lineage.transformation.deduplication',
  business_rule: 'lineage.transformation.business_rule',
  reconciliation: 'lineage.transformation.reconciliation',
  quality_rule: 'lineage.transformation.quality_rule',
  field_publish: 'lineage.transformation.field_publish',
})

/** The seven facet groups of the catalogue, as US-008 named them. */
export type GrupoFaceta =
  | 'domain'
  | 'dataType'
  | 'sensitivity'
  | 'refreshFrequency'
  | 'certification'
  | 'unit'
  | 'aggregation'

/**
 * Values each facet group admits, counted against the CHECK constraints of the
 * catalogue migration. They are data and not labels: the catalogues translate
 * them and the database never stores a translated word.
 */
export const CODIGOS_FACETA: Record<GrupoFaceta, readonly string[]> = Object.freeze({
  domain: ['cartera', 'riesgo', 'liquidez', 'mercado', 'cliente', 'contable', 'operacion', 'regulatorio'],
  dataType: ['entero', 'decimal', 'texto', 'fecha', 'booleano', 'categoria'],
  sensitivity: ['publica', 'interna', 'restringida'],
  refreshFrequency: ['intradia', 'diaria', 'semanal', 'mensual'],
  certification: ['certificado', 'en_revision', 'obsoleto'],
  unit: ['MXN', 'USD', 'porcentaje', 'dias', 'conteo'],
  aggregation: ['sum', 'mean', 'count', 'max', 'min'],
})

/** Catalogue key of the name of each group. */
export const CLAVE_GRUPO_FACETA: Record<GrupoFaceta, string> = Object.freeze({
  domain: 'catalog.facet.group.domain',
  dataType: 'catalog.facet.group.dataType',
  sensitivity: 'catalog.facet.group.sensitivity',
  refreshFrequency: 'catalog.facet.group.refreshFrequency',
  certification: 'catalog.facet.group.certification',
  unit: 'catalog.facet.group.unit',
  aggregation: 'catalog.facet.group.aggregation',
})

/**
 * Catalogue key of one facet value.
 *
 * @param grupo - Facet group the value belongs to.
 * @param codigo - Value as the backend spells it.
 * @returns The dotted key, or null when the value is not one this interface
 *   knows: rendering the raw code is honest, rendering the dotted key is not.
 */
export function claveDeFaceta(grupo: GrupoFaceta, codigo: string): string | null {
  return CODIGOS_FACETA[grupo].includes(codigo) ? `catalog.facet.${grupo}.${codigo}` : null
}
