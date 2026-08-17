import type { ColumnDef, RowData } from '@tanstack/vue-table'

import {
  createSortedRowModel,
  rowSortingFeature,
  sortFn_alphanumeric,
  sortFn_basic,
  sortFn_datetime,
  sortFn_text,
  tableFeatures,
} from '@tanstack/vue-table'

/**
 * The one feature registry every table of the portal is built from.
 *
 * TanStack Table v9 registers features explicitly: a table that never declares
 * `rowSortingFeature` has no sorting state, no `getCanSort` and no
 * `getToggleSortingHandler`, and the failure is a missing method rather than a
 * column that quietly refuses to sort. Declaring the registry once, at module
 * scope, is also what the adapter asks for -it watches the options it is given
 * and a registry rebuilt on every setup would rebuild the table with it.
 *
 * Only the sorting functions the portal actually uses are registered. The full
 * `sortFns` object is exported by the library and deprecated for exactly this
 * reason: registering it drags every built-in comparator into the bundle.
 *
 * Nothing else is registered on purpose. Pagination, filtering and selection
 * are not features this product has decided on yet, and a registry that offers
 * them would invite a table to grow a control that no acceptance criterion
 * asked for.
 */
export const CARACTERISTICAS_TABLA = tableFeatures({
  rowSortingFeature,
  sortedRowModel: createSortedRowModel(),
  sortFns: {
    alphanumeric: sortFn_alphanumeric,
    basic: sortFn_basic,
    datetime: sortFn_datetime,
    text: sortFn_text,
  },
  columnMeta: {} as MetaColumna,
})

/**
 * Per column metadata the portal reads, declared through the features slot.
 *
 * It travels on the column definition and not on the markup because the two
 * things it decides -whether a cell is the row header and which way its text
 * is aligned- are properties of the COLUMN, and a table that had to repeat
 * them cell by cell would let one row disagree with the rest.
 */
export interface MetaColumna {
  /**
   * True when this column holds the row header.
   *
   * A `<td>` in that position would leave every figure of the row without a
   * header to be announced against, which is the whole reason these tables are
   * tables and not grids of `<div>`.
   */
  readonly encabezadoFila?: boolean
  /** Text alignment of the column. Figures are read right aligned. */
  readonly alineacion?: 'inicio' | 'fin'
  /**
   * Extra classes for the column, header cell included.
   *
   * Header and body share them on purpose: a rule that separated the last
   * column in the body and not in the header would read as a table whose
   * header is one column short.
   */
  readonly clase?: string
}

/** The feature registry as a type, so a column definition can name it. */
export type CaracteristicasTabla = typeof CARACTERISTICAS_TABLA

/**
 * A column of `TablaDatos`.
 *
 * The alias exists because in v9 a column definition is generic over the
 * feature registry as well as over the row, and every consumer spelling
 * `ColumnDef<typeof CARACTERISTICAS_TABLA, Fila>` by hand would be a fourth
 * copy of a decision that belongs here.
 */
export type ColumnaDatos<TFila extends RowData> = ColumnDef<CaracteristicasTabla, TFila>

/**
 * Types a column list without widening it.
 *
 * A bare `const COLUMNAS = [...]` leaves the cell templates with implicit
 * `any` parameters, and an annotated `const COLUMNAS: ColumnaDatos<F>[]` loses
 * the literal types of the accessor keys. This identity function keeps both:
 * the argument is contextually typed and the return value is the inferred
 * array.
 *
 * @param columnas - Column definitions, in the order the header declares them.
 * @returns The same array, typed.
 */
export function definirColumnas<TFila extends RowData>(
  columnas: readonly ColumnaDatos<TFila>[],
): readonly ColumnaDatos<TFila>[] {
  return columnas
}
