import type { ComputedRef, Ref } from 'vue'
import type { CampoCatalogo, EstadoConsulta, LinajeCampo, LinajeCrudo, PasoLinaje, PasoCrudo } from '~/types/linaje'
import { computed, ref, watch } from 'vue'
import { codigoDelFallo } from '~/composables/useSerieTablero'
import { usePermisos } from '~/composables/usePermisos'

/**
 * Lineage of one field, fetched on demand.
 *
 * On demand is not a preference, it is the acceptance criterion: attaching the
 * journey to the search response would ship twenty lineages to render one, and
 * the reading flow would pay for a panel nobody opened.
 *
 * The overlay is opened by `abrir(campo)` and not by a route, so the field the
 * reader asked for is remembered here: the panel needs its name for the title
 * while the journey is still travelling, and a title that appears only after
 * the answer arrives is a layout jump on every open.
 */

/** Route of the lineage endpoint, as the permission registry publishes it. */
export function rutaDeLinaje(fieldId: number): string {
  return `/api/catalog/${fieldId}/lineage`
}

/** Maps one hop onto the vocabulary of the interface. */
export function mapearPaso(crudo: PasoCrudo): PasoLinaje {
  return {
    order: crudo.order,
    stage: crudo.stage,
    systemCode: crudo.system_code,
    systemName: crudo.system_name,
    transformationCode: crudo.transformation_code,
    transformationDetail: crudo.transformation_detail,
    owner: { area: crudo.owner.area, steward: crudo.owner.steward },
    effectiveFrom: crudo.effective_from,
    effectiveTo: crudo.effective_to,
    isCurrent: crudo.is_current,
    stored: crudo.stored,
  }
}

/** Maps the lineage payload, keeping the order the service answered with. */
export function mapearLinaje(crudo: LinajeCrudo): LinajeCampo {
  return {
    fieldId: crudo.field_id,
    physicalName: crudo.physical_name,
    businessName: crudo.business_name,
    source: {
      code: crudo.source.code,
      displayName: crudo.source.display_name,
      systemOfRecord: crudo.source.system_of_record,
      hasExtract: crudo.source.has_extract,
    },
    owner: { area: crudo.owner.area, steward: crudo.owner.steward },
    validity: {
      validFrom: crudo.validity.valid_from,
      validTo: crudo.validity.valid_to,
      isCurrent: crudo.validity.is_current,
    },
    facets: {
      domain: crudo.facets.domain,
      dataType: crudo.facets.data_type,
      sensitivity: crudo.facets.sensitivity,
      refreshFrequency: crudo.facets.refresh_frequency,
      certification: crudo.facets.certification,
      unit: crudo.facets.unit,
      metricAgg: crudo.facets.metric_agg,
    },
    steps: crudo.steps.map(mapearPaso),
  }
}

/** What the overlay needs in order to open, draw and close. */
export interface LinajeAbierto {
  abierto: Ref<boolean>
  campo: Ref<CampoCatalogo | null>
  linaje: Ref<LinajeCampo | null>
  estado: ComputedRef<EstadoConsulta>
  /** Typed backend code when the state is 'error'. */
  codigo: ComputedRef<string | null>
  abrir: (campo: CampoCatalogo) => Promise<void>
  cerrar: () => void
  reintentar: () => Promise<void>
}

/**
 * Journey of one field, and the state of the panel that shows it.
 *
 * @returns The open flag, the payload and the three actions of the overlay.
 */
export function useLinajeCampo(): LinajeAbierto {
  const { expirarSesion } = usePermisos()

  const abierto = ref(false)
  const campo = ref<CampoCatalogo | null>(null)

  const ruta = computed(() => (campo.value === null ? '' : rutaDeLinaje(campo.value.fieldId)))

  const { data, error, status, refresh } = useFetch(ruta, {
    // Nothing is requested until the reader opens a panel, and the request is
    // explicit rather than driven by the url: `abrir` decides when it leaves.
    immediate: false,
    server: false,
    watch: false,
    // The wire vocabulary dies here: no component below ever sees a snake_case
    // key, and there is one place where that conversion can be wrong.
    transform: (respuesta: unknown): LinajeCampo => mapearLinaje(respuesta as LinajeCrudo),
    default: (): LinajeCampo | null => null,
  })

  const linaje = computed<LinajeCampo | null>(() => data.value ?? null)

  const codigo = computed<string | null>(() => codigoDelFallo(error.value))

  const estado = computed<EstadoConsulta>(() => {
    if (!abierto.value) {
      return 'inicial'
    }
    if (error.value !== null && error.value !== undefined) {
      return 'error'
    }
    // The payload of the previously opened field is still in the shallowRef
    // until the new answer lands. Showing it would attribute one field's
    // journey to another, which is the worst thing a lineage panel can do.
    if (
      data.value === null
      || status.value === 'pending'
      || data.value.fieldId !== campo.value?.fieldId
    ) {
      return 'cargando'
    }
    return 'listo'
  })

  async function abrir(nuevo: CampoCatalogo): Promise<void> {
    campo.value = nuevo
    abierto.value = true
    await refresh()
  }

  function cerrar(): void {
    abierto.value = false
  }

  async function reintentar(): Promise<void> {
    if (campo.value === null) {
      return
    }
    await refresh()
  }

  // The hook US-017 exported for this branch. A 401 while the panel is open
  // ends on the entry screen with its reason, never on an empty overlay.
  watch(error, async (fallo) => {
    if ((fallo as { statusCode?: number } | null)?.statusCode === 401) {
      abierto.value = false
      await navigateTo(expirarSesion())
    }
  })

  return { abierto, campo, linaje, estado, codigo, abrir, cerrar, reintentar }
}
