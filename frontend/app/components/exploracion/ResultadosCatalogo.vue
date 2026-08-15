<script setup lang="ts">
/**
 * Result list of the catalogue screen and the three states it can be in
 * instead of holding rows.
 *
 * The component branches on the three properties and nothing else, so the
 * screen can never render a list and a state at the same time. The order of
 * the branches is the order of the reader's questions: did it fail, is it
 * still coming, was anything asked for at all, did anything match.
 *
 * The empty state is prose and not an empty table. A header row over zero rows
 * reads as a screen that broke halfway, and it is the reading the deliverable
 * cannot afford: it says why there is nothing and what to change.
 *
 * The loading state reserves the height of five rows. A spinner of its own
 * height moves everything below it the moment the answer lands, which is the
 * layout jump this screen is measured against.
 */
import type { PaginaCatalogo } from '~/composables/useBusquedaCatalogo'
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { LIMITE_PAGINA } from '~/composables/useBusquedaCatalogo'
import { claveDeFaceta } from '~/types/linaje'
import { ANILLO_FOCO } from '~/utils/foco'

const props = defineProps<{
  /** The page to draw, or null while there is nothing to draw yet. */
  pagina: PaginaCatalogo | null
  /** True while the request is in flight. */
  cargando: boolean
  /**
   * Typed backend code of the failure, the empty string for a failure that
   * carried none, and null when the search did not fail. The distinction
   * matters: the designed error is the same either way, and only the line that
   * prints the code depends on there being one.
   */
  error: string | null
}>()

defineEmits<{ reintentar: [] }>()

const { t } = useI18n()

/** Number of fields the page carries, zero when there is no page. */
const mostrados = computed(() => props.pagina?.campos.length ?? 0)

/** True when the catalogue holds more matches than one page can carry. */
const recortado = computed(() => (props.pagina?.total ?? 0) > mostrados.value)

/**
 * Certification badge of a field: state, and therefore never colour alone.
 *
 * @param codigo - Certification value as the backend spells it.
 * @returns The label and the icon that repeat the state without relying on hue.
 */
function certificacion(codigo: string): { etiqueta: string, icono: string, clase: string } {
  const clave = claveDeFaceta('certification', codigo)
  return {
    etiqueta: clave === null ? codigo : t(clave),
    icono: codigo === 'certificado' ? 'lucide:circle-check' : 'lucide:triangle-alert',
    clase: codigo === 'certificado' ? 'text-ok' : 'text-aviso',
  }
}

/**
 * Domain label of a field.
 *
 * @param codigo - Domain value as the backend spells it.
 * @returns Its translation when the interface knows the code, the raw code
 *   otherwise; the dotted key is never printed.
 */
function dominio(codigo: string): string {
  const clave = claveDeFaceta('domain', codigo)
  return clave === null ? codigo : t(clave)
}
</script>

<template>
  <section class="flex flex-col gap-3">
    <h2 class="flex items-center gap-2 text-titulo-3 text-corriente-pleno">
      <Icon name="lucide:table-2" class="size-4 shrink-0 text-corriente-tenue" aria-hidden="true" />
      {{ t('catalog.explore.results.title') }}
    </h2>

    <div v-if="error !== null" data-estado="error" role="alert" class="flex flex-col gap-3">
      <h3 class="flex items-start gap-2 text-titulo-3 text-corriente-pleno">
        <Icon name="lucide:circle-alert" class="mt-0.5 size-4 shrink-0 text-error" aria-hidden="true" />
        {{ t('catalog.explore.state.error.title') }}
      </h3>
      <p class="text-cuerpo text-corriente-medio">
        {{ t('catalog.explore.state.error.body') }}
      </p>
      <p v-if="error !== ''" data-codigo-error class="font-mono text-micro text-corriente-tenue">
        {{ error }}
      </p>
      <button
        type="button"
        data-reintentar
        class="inline-flex min-h-11 w-fit items-center gap-2 rounded-md border border-corriente-medio px-3 text-etiqueta text-corriente-pleno hover:bg-corriente-pleno hover:text-ground"
        :class="ANILLO_FOCO"
        @click="$emit('reintentar')"
      >
        <Icon name="lucide:refresh-cw" class="size-4 shrink-0" aria-hidden="true" />
        {{ t('catalog.explore.state.error.retry') }}
      </button>
    </div>

    <div
      v-else-if="cargando"
      data-estado="cargando"
      role="status"
      aria-busy="true"
      class="flex flex-col gap-2"
    >
      <span class="sr-only">{{ t('catalog.explore.state.loading') }}</span>
      <span
        v-for="fila in 5"
        :key="fila"
        data-esqueleto
        aria-hidden="true"
        class="h-20 animate-pulse rounded-sm bg-ground-alt"
      />
    </div>

    <div v-else-if="pagina === null" data-estado="inicial" class="flex flex-col gap-2">
      <h3 class="flex items-center gap-2 text-titulo-3 text-corriente-pleno">
        <Icon name="lucide:search" class="size-4 shrink-0 text-corriente-tenue" aria-hidden="true" />
        {{ t('catalog.explore.state.initial.title') }}
      </h3>
      <p class="text-cuerpo text-corriente-medio">
        {{ t('catalog.explore.state.initial.body') }}
      </p>
    </div>

    <div v-else-if="mostrados === 0" data-estado="vacio" class="flex flex-col gap-2">
      <h3 class="flex items-center gap-2 text-titulo-3 text-corriente-pleno">
        <Icon name="lucide:inbox" class="size-4 shrink-0 text-corriente-tenue" aria-hidden="true" />
        {{ t('catalog.explore.state.empty.title') }}
      </h3>
      <p class="text-cuerpo text-corriente-medio">
        {{ t('catalog.explore.state.empty.body') }}
      </p>
      <p class="text-micro text-corriente-tenue">
        {{ t('catalog.explore.state.empty.advice') }}
      </p>
    </div>

    <div v-else data-estado="listo" class="flex flex-col gap-3">
      <p data-conteo class="text-micro text-corriente-tenue">
        {{ t('catalog.explore.results.shown', { shown: mostrados, total: pagina.total }) }}
      </p>

      <ul data-resultados class="flex flex-col">
        <li
          v-for="campo in pagina.campos"
          :key="campo.fieldId"
          data-fila-campo
          class="flex min-h-20 flex-col justify-center gap-1 border-b border-grid py-3"
        >
          <p class="flex flex-wrap items-baseline gap-x-3 gap-y-1">
            <span class="font-mono text-cuerpo text-corriente-pleno">{{ campo.physicalName }}</span>
            <span class="text-cuerpo text-corriente-medio">{{ campo.businessName }}</span>
          </p>

          <p class="max-w-(--medida-maxima) text-micro text-corriente-tenue">
            {{ campo.definition }}
          </p>

          <p class="flex flex-wrap items-center gap-x-3 gap-y-1 text-micro text-corriente-tenue">
            <span data-dominio-campo>{{ dominio(campo.facets.domain) }}</span>
            <span data-fuente-campo>
              {{ t('catalog.explore.results.source') }}: {{ campo.source.displayName }}
            </span>
            <span data-responsable-campo>
              {{ t('catalog.explore.results.owner') }}: {{ campo.owner.steward }}
            </span>
            <span
              data-certificacion-campo
              class="inline-flex items-center gap-1"
              :class="certificacion(campo.facets.certification).clase"
            >
              <Icon
                :name="certificacion(campo.facets.certification).icono"
                class="size-3.5 shrink-0"
                aria-hidden="true"
              />
              {{ certificacion(campo.facets.certification).etiqueta }}
            </span>
          </p>
        </li>
      </ul>

      <p v-if="recortado" data-recorte class="text-micro text-corriente-tenue">
        {{ t('catalog.explore.results.capped', { limit: LIMITE_PAGINA }) }}
      </p>
    </div>
  </section>
</template>
