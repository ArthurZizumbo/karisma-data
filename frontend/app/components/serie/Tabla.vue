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
 */
import type { FilaTabla } from '~/types/tablero'
import { ANILLO_FOCO } from '~/utils/foco'

const props = defineProps<{
  /** Sentence of the `<caption>`, already translated. */
  titulo: string
  /** Note under the table, already translated. */
  nota: string
  /** Column headers, the first one being the row header column. */
  columnas: readonly string[]
  filas: readonly FilaTabla[]
}>()

defineEmits<{ seleccionar: [fila: FilaTabla] }>()
</script>

<template>
  <div data-alternativa class="max-w-full overflow-x-auto">
    <table class="w-full border-collapse text-cuerpo">
      <caption class="pb-2 text-left text-micro text-corriente-tenue">
        {{ props.titulo }}
      </caption>
      <thead>
        <tr>
          <th
            v-for="(columna, indice) in props.columnas"
            :key="columna"
            scope="col"
            class="border-b border-corriente-apagado py-1 text-etiqueta uppercase text-corriente-tenue"
            :class="indice === 0 ? 'text-left' : 'text-right'"
          >
            {{ columna }}
          </th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="fila in props.filas"
          :key="fila.clave"
          :data-serie-id="fila.identificador ?? undefined"
          class="border-b border-grid"
        >
          <th scope="row" class="py-1 text-left font-normal text-corriente-pleno">
            <button
              v-if="fila.indiceLinea !== null"
              type="button"
              data-fila-drill
              class="min-h-11 rounded-sm text-left hover:text-info"
              :class="ANILLO_FOCO"
              @click="$emit('seleccionar', fila)"
            >
              {{ fila.encabezado }}
            </button>
            <span v-else>{{ fila.encabezado }}</span>
          </th>
          <td
            v-for="(celda, indice) in fila.celdas"
            :key="indice"
            class="py-1 text-right tabular-nums text-corriente-medio"
          >
            {{ celda }}
          </td>
        </tr>
      </tbody>
    </table>

    <p class="pt-2 text-micro text-corriente-tenue">
      {{ props.nota }}
    </p>
  </div>
</template>
