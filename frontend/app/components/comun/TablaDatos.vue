<script setup lang="ts" generic="TFila extends RowData">
/**
 * The dense table of the portal, and the only one that announces its order.
 *
 * Seven tables were written by hand in this repository and not one of them
 * could be sorted, so a reader looking for the largest figure of a column read
 * every row. TanStack Table v9 is headless -it ships no markup and no CSS- so
 * what it brings is the state machine of the order and nothing that could
 * collide with the design tokens.
 *
 * Three properties are load bearing:
 *
 * 1. THE ORDER IS ANNOUNCED, not merely drawn. `aria-sort` travels on the
 *    `<th>` and the arrow is `aria-hidden`: an order that only exists as a
 *    glyph does not exist for a screen reader, and this product lives in dense
 *    tables.
 * 2. THE ROW IS 34 PIXELS, which is what `DESIGN.md` declares. The height
 *    comes from `--table-row-height` and never from a literal, so the day the
 *    system changes it, every table of the portal changes with it.
 * 3. THE ROW HEADER IS A `<th scope="row">`. Which column holds it is declared
 *    in the column metadata, because it is a property of the column: a table
 *    that decided it cell by cell could contradict itself between two rows.
 *
 * The body has two shapes on purpose. By default the cells come from the
 * column definitions, which is what a table of figures needs; a consumer whose
 * row is a component of its own -one with selects, buttons and cells that
 * appear only for some accounts- passes it through the `fila` slot and keeps
 * the header, the order and the geometry of everything else.
 */
import type { RowData, SortDirection, SortingState } from '@tanstack/vue-table'
import type { ColumnaDatos } from '~/utils/tablaDatos'

import { FlexRender, useTable } from '@tanstack/vue-table'
import { computed, ref, watch } from 'vue'

import { ANILLO_FOCO_INTERNO } from '~/utils/foco'
import { CARACTERISTICAS_TABLA } from '~/utils/tablaDatos'

const props = defineProps<{
  /** Columns in header order. Sorting is declared per column, never here. */
  columnas: readonly ColumnaDatos<TFila>[]
  /** Rows as the owner holds them. The table never mutates this array. */
  filas: readonly TFila[]
  /** Order the table opens with. Absent means the order the rows arrived in. */
  ordenInicial?: SortingState
  /** Sentence shown instead of the rows when there are none, ALREADY TRANSLATED. */
  vacio?: string
  /** `<caption>` of the table, ALREADY TRANSLATED. */
  titulo?: string
  /** True when the caption is for screen readers only. */
  tituloOculto?: boolean
  /** True while the rows are still being fetched. */
  cargando?: boolean
  /** Stable identifier of a row. Falls back to its position. */
  idFila?: (fila: TFila, indice: number) => string
  /** Attributes the owner needs on the `<tr>`, such as its own `data-*`. */
  atributosFila?: (fila: TFila, indice: number) => Record<string, string | undefined>
}>()

const slots = defineSlots<{
  /** Whole row, for a consumer whose row is a component of its own. */
  fila?: (props: { fila: TFila, indice: number }) => unknown
  /** Body drawn while `cargando` is true, in place of the rows. */
  esqueleto?: () => unknown
}>()

/**
 * Order of the table, owned here.
 *
 * Controlled rather than internal because the initial order arrives as a
 * property: with internal state a table whose `ordenInicial` changed -the
 * dashboard swaps metric without unmounting- would keep the order of the
 * previous dataset and silently show the new figures in the old sequence.
 */
const orden = ref<SortingState>(props.ordenInicial === undefined ? [] : [...props.ordenInicial])

watch(
  () => props.ordenInicial,
  (siguiente) => {
    orden.value = siguiente === undefined ? [] : [...siguiente]
  },
)

const columnas = computed(() => [...props.columnas])
const filas = computed(() => props.filas)
const estado = computed(() => ({ sorting: orden.value }))

const tabla = useTable({
  features: CARACTERISTICAS_TABLA,
  columns: columnas,
  data: filas,
  state: estado,
  getRowId: (fila: TFila, indice: number) => props.idFila?.(fila, indice) ?? String(indice),
  onSortingChange: (siguiente: SortingState | ((previo: SortingState) => SortingState)) => {
    orden.value = typeof siguiente === 'function' ? siguiente(orden.value) : siguiente
  },
})

const grupos = computed(() => tabla.getHeaderGroups())
const visibles = computed(() => tabla.getRowModel().rows)
const hayFilas = computed(() => visibles.value.length > 0)

/** Columns of the header, which is how wide the empty row has to span. */
const anchoTotal = computed(() => props.columnas.length)

/**
 * What `aria-sort` says for a column.
 *
 * `undefined` removes the attribute, which is what a column that cannot be
 * sorted must have: `aria-sort="none"` on every header would tell a screen
 * reader that the whole table is sortable and that nothing is sorted.
 *
 * @param sentido - Direction the column reports, or false when unsorted.
 * @param ordenable - True when the column can be sorted at all.
 * @returns The value of `aria-sort`, or undefined.
 */
function anuncioDeOrden(
  sentido: false | SortDirection,
  ordenable: boolean,
): 'ascending' | 'descending' | 'none' | undefined {
  if (!ordenable) {
    return undefined
  }
  if (sentido === 'asc') {
    return 'ascending'
  }
  return sentido === 'desc' ? 'descending' : 'none'
}

/**
 * Arrow of a sortable header.
 *
 * @param sentido - Direction the column reports, or false when unsorted.
 * @returns Name of the icon in the packaged collection.
 */
function iconoDeOrden(sentido: false | SortDirection): string {
  if (sentido === 'asc') {
    return 'lucide:chevron-up'
  }
  return sentido === 'desc' ? 'lucide:chevron-down' : 'lucide:chevrons-up-down'
}

/** Alignment of a column, figures to the end and everything else to the start. */
function alineacion(alineado: 'inicio' | 'fin' | undefined): string {
  return alineado === 'fin' ? 'text-right' : 'text-left'
}

/** Geometry shared by every cell, so the row keeps its declared height. */
const CELDA = 'h-(--table-row-height) px-3 py-1'
</script>

<template>
  <div data-tabla-datos class="max-w-full overflow-x-auto border border-grid">
    <table class="w-full border-collapse" :aria-busy="cargando === true ? 'true' : undefined">
      <caption
        v-if="titulo !== undefined"
        :class="tituloOculto === true
          ? 'sr-only'
          : 'px-3 py-2 text-left text-micro text-corriente-tenue'"
      >
        {{ titulo }}
      </caption>

      <thead>
        <tr v-for="grupo in grupos" :key="grupo.id" class="bg-ground-alt">
          <th
            v-for="encabezado in grupo.headers"
            :key="encabezado.id"
            scope="col"
            :colspan="encabezado.colSpan > 1 ? encabezado.colSpan : undefined"
            :aria-sort="anuncioDeOrden(
              encabezado.column.getIsSorted(),
              encabezado.column.getCanSort(),
            )"
            :class="[
              CELDA,
              'text-etiqueta text-corriente-pleno',
              alineacion(encabezado.column.columnDef.meta?.alineacion),
              encabezado.column.columnDef.meta?.clase ?? '',
            ]"
          >
            <template v-if="!encabezado.isPlaceholder">
              <button
                v-if="encabezado.column.getCanSort()"
                type="button"
                :data-ordenar="encabezado.column.id"
                class="inline-flex w-full items-center gap-1 rounded-sm hover:text-accion"
                :class="[
                  ANILLO_FOCO_INTERNO,
                  encabezado.column.columnDef.meta?.alineacion === 'fin' ? 'justify-end' : '',
                ]"
                @click="encabezado.column.getToggleSortingHandler()?.($event)"
              >
                <FlexRender :header="encabezado" />
                <Icon
                  :name="iconoDeOrden(encabezado.column.getIsSorted())"
                  class="size-3 shrink-0"
                  aria-hidden="true"
                />
              </button>
              <FlexRender v-else :header="encabezado" />
            </template>
          </th>
        </tr>
      </thead>

      <tbody v-if="cargando === true && slots.esqueleto !== undefined" aria-hidden="true">
        <slot name="esqueleto" />
      </tbody>

      <tbody v-else-if="hayFilas">
        <template v-for="(fila, indice) in visibles" :key="fila.id">
          <slot name="fila" :fila="fila.original" :indice="indice">
            <tr
              v-bind="atributosFila?.(fila.original, indice)"
              class="border-t border-grid"
            >
              <component
                :is="celda.column.columnDef.meta?.encabezadoFila === true ? 'th' : 'td'"
                v-for="celda in fila.getAllCells()"
                :key="celda.id"
                :scope="celda.column.columnDef.meta?.encabezadoFila === true ? 'row' : undefined"
                :class="[
                  CELDA,
                  'text-cuerpo',
                  celda.column.columnDef.meta?.encabezadoFila === true
                    ? 'font-normal text-corriente-pleno'
                    : 'text-corriente-medio',
                  alineacion(celda.column.columnDef.meta?.alineacion),
                  celda.column.columnDef.meta?.clase ?? '',
                ]"
              >
                <FlexRender :cell="celda" />
              </component>
            </tr>
          </slot>
        </template>
      </tbody>

      <tbody v-else-if="vacio !== undefined">
        <tr data-tabla-vacia class="border-t border-grid">
          <td :colspan="anchoTotal" :class="[CELDA, 'text-cuerpo text-corriente-tenue']">
            {{ vacio }}
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
