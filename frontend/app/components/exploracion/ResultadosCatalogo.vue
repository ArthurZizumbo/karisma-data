<script setup lang="ts">
/**
 * Result table of the catalogue screen and the four states it can be in
 * instead of holding rows.
 *
 * THE ROW IS A DOOR. The design review found this list to be a dead end: not
 * one row was interactive and nothing led to the lineage, so the first promise
 * of the product -knowing where a figure comes from- could not be reached from
 * the screen that discovers the figure. The row header is now the control that
 * opens the journey of that field, and the footer of the result carries the
 * exit towards governance, which is where the full record lives.
 *
 * THE THREE CERTIFICATION STATES ARE THREE. They used to be two: a ternary on
 * the code painted "en revisión" and "obsoleto" with the same colour AND the
 * same icon, and for the primary persona they mean opposite things -one may be
 * used with reserve, the other must not be used at all. Neither the shape nor
 * the colour is decided here any more: both arrive from the generated tokens.
 *
 * THE FOUR STATES ANNOUNCE THEMSELVES. Loading and failure already carried a
 * live region; the ready count and the empty explanation did not, so a screen
 * reader was told the search was running and never told how it ended. Each
 * branch carries its own region because only one of them is ever mounted.
 *
 * The empty state is prose and not an empty table. A header row over zero rows
 * reads as a screen that broke halfway: it says why there is nothing and what
 * to change.
 *
 * The definition of a field is deliberately NOT a column. It is prose, it does
 * not survive a thirty four pixel row, and a cell that truncates it would be a
 * table pretending to carry something it hides; it is the record that governance
 * publishes, which is what the exit under the table is for.
 */
import type { CampoCatalogo } from '~/types/linaje'
import type { PaginaCatalogo } from '~/composables/useBusquedaCatalogo'
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import ComunTablaDatos from '~/components/comun/TablaDatos.vue'
import { certificacionDeCampo, LIMITE_PAGINA } from '~/composables/useBusquedaCatalogo'
import { claveDeFaceta } from '~/types/linaje'
import { ANILLO_FOCO, ANILLO_FOCO_INTERNO } from '~/utils/foco'
import { MODULOS } from '~/utils/navegacion'
import { definirColumnas } from '~/utils/tablaDatos'

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

const emit = defineEmits<{ reintentar: [], verLinaje: [campo: CampoCatalogo] }>()

const { t } = useI18n()

/** Governance module of the A3 map, so no route literal enters this file. */
const GOBIERNO = MODULOS.find(modulo => modulo.id === '3')!

/** Geometry of a body cell, so the row keeps the height the system declares. */
const CELDA = 'h-(--table-row-height) px-3 py-1 text-cuerpo'

/** Number of fields the page carries, zero when there is no page. */
const mostrados = computed(() => props.pagina?.campos.length ?? 0)

/** True when the catalogue holds more matches than one page can carry. */
const recortado = computed(() => (props.pagina?.total ?? 0) > mostrados.value)

/**
 * Label of a facet value.
 *
 * @param grupo - Facet group the value belongs to.
 * @param codigo - Value as the backend spells it.
 * @returns Its translation when the interface knows the code, the raw code
 *   otherwise; the dotted key is never printed.
 */
function etiquetaDeFaceta(grupo: 'domain' | 'certification', codigo: string): string {
  const clave = claveDeFaceta(grupo, codigo)
  return clave === null ? codigo : t(clave)
}

/** One row of the table: the field, already translated, and its state mark. */
interface FilaCatalogo {
  readonly campo: CampoCatalogo
  readonly clave: string
  readonly fisico: string
  readonly negocio: string
  readonly dominio: string
  readonly fuente: string
  readonly responsable: string
  readonly certificacion: string
  /** Code as the backend spells it, published so the state is verifiable. */
  readonly codigoCertificacion: string
  /**
   * Colour and icon of the certification state, or null when the design system
   * does not declare that code: the label alone is honest, and an icon borrowed
   * from another state is the defect this component was rebuilt to close.
   */
  readonly marca: { readonly icono: string, readonly clase: string } | null
}

const filas = computed<readonly FilaCatalogo[]>(() =>
  (props.pagina?.campos ?? []).map((campo) => {
    const estado = certificacionDeCampo(campo.facets.certification)
    return {
      campo,
      clave: String(campo.fieldId),
      fisico: campo.physicalName,
      negocio: campo.businessName,
      dominio: etiquetaDeFaceta('domain', campo.facets.domain),
      fuente: campo.source.displayName,
      responsable: campo.owner.steward,
      certificacion: etiquetaDeFaceta('certification', campo.facets.certification),
      codigoCertificacion: campo.facets.certification,
      marca: estado === null ? null : { icono: estado.icono, clase: estado.clase },
    }
  }),
)

/**
 * Columns of the result table.
 *
 * Every one of them sorts on the value the reader reads, because all six are
 * text: there is no formatted figure in this table, so the order the cell shows
 * and the order the column computes cannot diverge.
 */
const columnas = computed(() => definirColumnas<FilaCatalogo>([
  {
    id: 'campo',
    accessorFn: fila => fila.fisico,
    header: t('lineage.card.physicalName'),
    sortFn: 'text',
    meta: { encabezadoFila: true },
  },
  {
    id: 'negocio',
    accessorFn: fila => fila.negocio,
    header: t('lineage.card.businessName'),
    sortFn: 'text',
  },
  {
    id: 'dominio',
    accessorFn: fila => fila.dominio,
    header: t('catalog.facet.group.domain'),
    sortFn: 'text',
  },
  {
    id: 'fuente',
    accessorFn: fila => fila.fuente,
    header: t('catalog.explore.results.source'),
    sortFn: 'text',
  },
  {
    id: 'responsable',
    accessorFn: fila => fila.responsable,
    header: t('catalog.explore.results.owner'),
    sortFn: 'text',
  },
  {
    id: 'certificacion',
    accessorFn: fila => fila.certificacion,
    header: t('catalog.facet.group.certification'),
    sortFn: 'text',
  },
]))
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
        @click="emit('reintentar')"
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
        class="h-(--table-row-height) animate-pulse rounded-sm bg-ground-alt motion-reduce:animate-none"
      />
    </div>

    <div v-else-if="pagina === null" data-estado="inicial" class="flex flex-col gap-2">
      <h3 class="flex items-center gap-2 text-titulo-3 text-corriente-pleno">
        <Icon name="lucide:compass" class="size-4 shrink-0 text-corriente-tenue" aria-hidden="true" />
        {{ t('catalog.explore.state.initial.title') }}
      </h3>
      <p class="text-cuerpo text-corriente-medio">
        {{ t('catalog.explore.state.initial.body') }}
      </p>
    </div>

    <!--
      The empty answer announces itself: the reader who does not see the list
      was told the search was running and, without this region, never told how
      it ended.
    -->
    <div
      v-else-if="mostrados === 0"
      data-estado="vacio"
      role="status"
      class="flex flex-col gap-2"
    >
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
      <p data-conteo role="status" class="text-micro text-corriente-tenue">
        {{ t('catalog.explore.results.shown', { shown: mostrados, total: pagina.total }) }}
      </p>

      <ComunTablaDatos
        :columnas="columnas"
        :filas="filas"
        :titulo="t('catalog.explore.results.title')"
        titulo-oculto
        :id-fila="(fila: FilaCatalogo) => fila.clave"
      >
        <template #fila="{ fila }">
          <tr data-fila-campo :data-campo="fila.clave" class="border-t border-grid">
            <th scope="row" :class="[CELDA, 'text-left font-normal text-corriente-pleno']">
              <!--
                The row header is the door to the lineage. A separate action
                column would spend a column of a dense table on repeating the
                name of the field the reader is already pointing at.
              -->
              <button
                type="button"
                data-ver-linaje
                :aria-label="t('catalog.explore.results.openLineage', { field: fila.fisico })"
                class="flex h-full w-full items-center gap-2 rounded-sm text-left hover:underline hover:underline-offset-2"
                :class="ANILLO_FOCO_INTERNO"
                @click="emit('verLinaje', fila.campo)"
              >
                <Icon name="lucide:git-branch" class="size-3.5 shrink-0" aria-hidden="true" />
                <span class="truncate font-mono">{{ fila.fisico }}</span>
              </button>
            </th>
            <td :class="[CELDA, 'text-corriente-pleno']">
              {{ fila.negocio }}
            </td>
            <td data-dominio-campo :class="[CELDA, 'text-corriente-medio']">
              {{ fila.dominio }}
            </td>
            <td data-fuente-campo :class="[CELDA, 'text-corriente-medio']">
              {{ fila.fuente }}
            </td>
            <td data-responsable-campo :class="[CELDA, 'text-corriente-medio']">
              {{ fila.responsable }}
            </td>
            <td
              data-certificacion-campo
              :data-certificacion="fila.codigoCertificacion"
              :class="[CELDA, 'text-corriente-medio']"
            >
              <span class="inline-flex items-center gap-1" :class="fila.marca?.clase">
                <Icon
                  v-if="fila.marca !== null"
                  :name="fila.marca.icono"
                  class="size-3.5 shrink-0"
                  aria-hidden="true"
                />
                {{ fila.certificacion }}
              </span>
            </td>
          </tr>
        </template>
      </ComunTablaDatos>

      <p v-if="recortado" data-recorte class="text-micro text-corriente-tenue">
        {{ t('catalog.explore.results.capped', { limit: LIMITE_PAGINA }) }}
      </p>

      <!--
        The exit out of the result: the definition, the validity and the access
        log of a field are the record governance keeps, and this screen is the
        one that finds the field, not the one that defends it.
      -->
      <NuxtLink
        :to="GOBIERNO.ruta"
        data-salida="gobierno"
        class="inline-flex min-h-11 w-fit items-center gap-2 text-etiqueta text-corriente-pleno underline underline-offset-4 hover:no-underline"
        :class="ANILLO_FOCO"
      >
        <Icon name="lucide:book-open" class="size-4 shrink-0" aria-hidden="true" />
        {{ t('catalog.explore.results.fullRecord', { screen: t(GOBIERNO.claveEtiqueta) }) }}
      </NuxtLink>
    </div>
  </section>
</template>
