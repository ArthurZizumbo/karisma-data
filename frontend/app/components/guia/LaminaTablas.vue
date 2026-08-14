<script setup lang="ts">
/**
 * Table plate, rebuilt in the diagram world.
 *
 * A dense table is where this product lives, so the plate is the densest thing
 * in the guide on purpose: 34 pixel rows, tabular figures, and separation by
 * rule rather than by fill. The zebra stripe stays, because scanning a wide row
 * without it costs more than the ink it spends.
 *
 * Sorting announces itself with aria-sort and not only with an arrow, which is
 * what makes the column readable to a screen reader instead of merely visible.
 */
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { ANILLO_FOCO, ANILLO_FOCO_INTERNO } from '~/utils/foco'

const { t } = useI18n()

interface Fila {
  readonly clave: string
  readonly registros: number
  readonly importe: number
  readonly estado: 'ready' | 'running' | 'failed'
}

/** Demonstration data, deliberately uneven so the alignment has work to do. */
const FILAS: readonly Fila[] = Object.freeze([
  { clave: 'treasury', registros: 96310, importe: 12405780.4, estado: 'ready' },
  { clave: 'credit', registros: 1284350, importe: 987654321.05, estado: 'running' },
  { clave: 'deposits', registros: 7412, importe: 45120.9, estado: 'ready' },
  { clave: 'markets', registros: 233087, importe: 3210987.65, estado: 'failed' },
  { clave: 'operations', registros: 512, importe: 8930.15, estado: 'ready' },
])

const ESTADO = Object.freeze({
  ready: { color: 'text-ok', icono: 'lucide:check' },
  running: { color: 'text-info', icono: 'lucide:loader' },
  failed: { color: 'text-error', icono: 'lucide:x' },
})

const orden = ref<{ columna: 'records' | 'amount', ascendente: boolean }>({
  columna: 'amount',
  ascendente: false,
})

const filas = computed<readonly Fila[]>(() => {
  const clave = orden.value.columna === 'records' ? 'registros' : 'importe'
  const factor = orden.value.ascendente ? 1 : -1
  return [...FILAS].sort((a, b) => (a[clave] - b[clave]) * factor)
})

function ordenar(columna: 'records' | 'amount'): void {
  orden.value = {
    columna,
    ascendente: orden.value.columna === columna ? !orden.value.ascendente : true,
  }
}

function ariaSort(columna: 'records' | 'amount'): 'ascending' | 'descending' | 'none' {
  if (orden.value.columna !== columna) return 'none'
  return orden.value.ascendente ? 'ascending' : 'descending'
}

const numero = new Intl.NumberFormat('es-MX')
const moneda = new Intl.NumberFormat('es-MX', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
</script>

<template>
  <section data-lamina="tablas" class="flex flex-col gap-4">
    <h2 class="text-titulo-2 text-corriente-pleno">
      {{ t('guide.plate.tables') }}
    </h2>

    <div class="overflow-x-auto border border-grid">
      <table class="w-full border-collapse text-left">
        <caption class="sr-only">{{ t('guide.tables.caption') }}</caption>
        <thead>
          <tr class="bg-ground-alt">
            <th scope="col" class="h-(--table-row-height) px-3 text-etiqueta text-corriente-pleno">
              {{ t('guide.tables.column.source') }}
            </th>
            <th
              v-for="columna in (['records', 'amount'] as const)"
              :key="columna"
              scope="col"
              :aria-sort="ariaSort(columna)"
              class="h-(--table-row-height) px-3 text-right text-etiqueta text-corriente-pleno"
            >
              <button
                type="button"
                :data-ordenar="columna"
                class="inline-flex items-center gap-1"
                :class="ANILLO_FOCO_INTERNO"
                :aria-label="t('guide.tables.sort', { column: t(`guide.tables.column.${columna}`) })"
                @click="ordenar(columna)"
              >
                {{ t(`guide.tables.column.${columna}`) }}
                <Icon
                  v-if="orden.columna === columna"
                  :name="orden.ascendente ? 'lucide:arrow-up' : 'lucide:arrow-down'"
                  class="size-3 shrink-0"
                  aria-hidden="true"
                />
              </button>
            </th>
            <th scope="col" class="h-(--table-row-height) px-3 text-etiqueta text-corriente-pleno">
              {{ t('guide.tables.column.status') }}
            </th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="fila in filas"
            :key="fila.clave"
            data-fila
            class="border-t border-grid even:bg-ground-alt"
          >
            <td class="h-(--table-row-height) px-3 text-cuerpo text-corriente-pleno">
              {{ t(`guide.tables.row.${fila.clave}`) }}
            </td>
            <!-- Figures are tabular and right aligned: columns have to line up. -->
            <td class="h-(--table-row-height) px-3 text-right font-mono text-dato tabular-nums text-corriente-pleno">
              {{ numero.format(fila.registros) }}
            </td>
            <td class="h-(--table-row-height) px-3 text-right font-mono text-dato tabular-nums text-corriente-pleno">
              {{ moneda.format(fila.importe) }}
            </td>
            <td class="h-(--table-row-height) px-3">
              <span class="inline-flex items-center gap-1 text-etiqueta" :class="ESTADO[fila.estado].color">
                <Icon :name="ESTADO[fila.estado].icono" class="size-3 shrink-0" aria-hidden="true" />
                {{ t(`guide.tables.status.${fila.estado}`) }}
              </span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- The designed empty state, which is one of the four unhappy ones. -->
    <div data-vacio class="flex flex-col gap-1 border border-dashed border-corriente-apagado p-6">
      <p class="flex items-center gap-2 text-titulo-3 text-corriente-pleno">
        <Icon name="lucide:inbox" class="size-4 shrink-0 text-corriente-tenue" aria-hidden="true" />
        {{ t('guide.tables.empty.title') }}
      </p>
      <p class="max-w-(--medida-maxima) text-cuerpo text-corriente-medio">
        {{ t('guide.tables.empty.body') }}
      </p>
    </div>

    <details class="border-t border-grid pt-3">
      <summary class="cursor-pointer text-etiqueta text-corriente-tenue" :class="ANILLO_FOCO">
        {{ t('guide.palette.why') }}
      </summary>
      <p class="mt-2 max-w-(--medida-maxima) text-cuerpo text-corriente-medio">
        {{ t('guide.tables.sortHint') }}
      </p>
    </details>
  </section>
</template>
