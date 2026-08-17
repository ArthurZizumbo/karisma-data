<script setup lang="ts">
/**
 * The table alternative to the chart.
 *
 * Every chart of this portal carries one, and it is not a courtesy: a canvas is
 * a picture with no structure, so without the table the figures simply do not
 * exist for a screen reader. The `<caption>` says what the table is, `scope`
 * ties every cell to its row and its column, and the row header is a button so
 * the same drill-down the chart offers with a pointer is available from the
 * keyboard alone.
 *
 * Numbers are right aligned with tabular figures: in a dense column, digits of
 * different widths make two magnitudes look alike.
 *
 * ONLY THE FIRST COLUMN SORTS, and only when the rows are series. The figures
 * arrive here already formatted -`1 284,5` is a string by the time it reaches
 * this component- so an order computed over them would be an alphabetical
 * order wearing the clothes of a numeric one, and `987,6` would sit above
 * `1 284,5`. Sorting the rest would mean the panel handing over the raw values
 * as well, which is a change in `serie/Panel.vue`. When the rows are points of
 * a single line the header is a formatted date, so nothing sorts: a date sorted
 * as text is the same lie in another column.
 */
import type { FilaTabla } from '~/types/tablero'

import { computed } from 'vue'

import ComunTablaDatos from '~/components/comun/TablaDatos.vue'
import { ANILLO_FOCO_INTERNO } from '~/utils/foco'
import { definirColumnas } from '~/utils/tablaDatos'

const props = defineProps<{
  /** Sentence of the `<caption>`, already translated. */
  titulo: string
  /** Note under the table, already translated. */
  nota: string
  /** Column headers, the first one being the row header column. */
  columnas: readonly string[]
  filas: readonly FilaTabla[]
}>()

const emit = defineEmits<{ seleccionar: [fila: FilaTabla] }>()

/** True when the rows are lines of the frame and not points of a single one. */
const porSerie = computed(() => props.filas.some(fila => fila.indiceLinea !== null))

const columnas = computed(() => definirColumnas<FilaTabla>(
  props.columnas.map((encabezado, indice) => (indice === 0
    ? {
        id: 'encabezado',
        accessorFn: (fila: FilaTabla) => fila.encabezado,
        header: encabezado,
        sortFn: 'alphanumeric' as const,
        enableSorting: porSerie.value,
        meta: { encabezadoFila: true },
      }
    : {
        id: `celda-${indice - 1}`,
        accessorFn: (fila: FilaTabla) => fila.celdas[indice - 1] ?? '',
        header: encabezado,
        enableSorting: false,
        meta: { alineacion: 'fin' as const },
      })),
))

/** Geometry of a body cell, shared so the row keeps its declared height. */
const CELDA = 'h-(--table-row-height) px-3 py-1 text-cuerpo'
</script>

<template>
  <div data-alternativa class="flex flex-col">
    <ComunTablaDatos
      :columnas="columnas"
      :filas="props.filas"
      :titulo="props.titulo"
      :id-fila="(fila: FilaTabla) => fila.clave"
    >
      <template #fila="{ fila }">
        <tr :data-serie-id="fila.identificador ?? undefined" class="border-t border-grid">
          <th
            scope="row"
            :class="[CELDA, 'text-left font-normal text-corriente-pleno']"
          >
            <button
              v-if="fila.indiceLinea !== null"
              type="button"
              data-fila-drill
              class="flex h-full w-full items-center rounded-sm text-left hover:text-info"
              :class="ANILLO_FOCO_INTERNO"
              @click="emit('seleccionar', fila)"
            >
              {{ fila.encabezado }}
            </button>
            <span v-else>{{ fila.encabezado }}</span>
          </th>
          <td
            v-for="(celda, indice) in fila.celdas"
            :key="indice"
            :class="[CELDA, 'text-right tabular-nums text-corriente-medio']"
          >
            {{ celda }}
          </td>
        </tr>
      </template>
    </ComunTablaDatos>

    <p class="pt-2 text-micro text-corriente-tenue">
      {{ props.nota }}
    </p>
  </div>
</template>
