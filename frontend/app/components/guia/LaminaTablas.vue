<script setup lang="ts">
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { ANILLO_FOCO_INTERNO } from '~/utils/foco'

/**
 * Table plate of the living design system.
 *
 * The sort is real, not painted. A header that showed an arrow without moving
 * anything would document a behaviour the product does not have, and a header
 * that sorted without updating `aria-sort` would leave a screen reader unable
 * to tell which column is ordered: the arrow alone never reaches it.
 */
defineOptions({ name: 'LaminaTablas' })

/** Sortable columns. Status is a category and is deliberately not sortable. */
type Columna = 'fuente' | 'registros' | 'importe'

interface FilaTabla {
  readonly id: string
  readonly claveFuente: string
  readonly registros: number
  readonly importe: number
  readonly claveEstado: string
  readonly clasesEstado: string
}

interface EncabezadoOrdenable {
  readonly columna: Columna
  readonly clave: string
  /** Numeric columns align right and carry tabular figures. */
  readonly numerica: boolean
}

/** Synthetic demo figures with a fixed seed of values, never real data. */
const FILAS: readonly FilaTabla[] = Object.freeze([
  {
    id: 'tesoreria',
    claveFuente: 'guide.tables.row.treasury',
    registros: 128450,
    importe: 4820115,
    claveEstado: 'guide.tables.status.ready',
    clasesEstado: 'border-success-700 bg-success-100 text-success-900',
  },
  {
    id: 'credito',
    claveFuente: 'guide.tables.row.credit',
    registros: 96310,
    importe: 12405780,
    claveEstado: 'guide.tables.status.ready',
    clasesEstado: 'border-success-700 bg-success-100 text-success-900',
  },
  {
    id: 'captacion',
    claveFuente: 'guide.tables.row.deposits',
    registros: 54872,
    importe: 8130640,
    claveEstado: 'guide.tables.status.running',
    clasesEstado: 'border-primary bg-primary-100 text-primary-700',
  },
  {
    id: 'mercados',
    claveFuente: 'guide.tables.row.markets',
    registros: 12045,
    importe: 2507930,
    claveEstado: 'guide.tables.status.failed',
    clasesEstado: 'border-danger bg-surface text-danger',
  },
  {
    id: 'operacion',
    claveFuente: 'guide.tables.row.operations',
    registros: 7318,
    importe: 640275,
    claveEstado: 'guide.tables.status.ready',
    clasesEstado: 'border-success-700 bg-success-100 text-success-900',
  },
])

const ENCABEZADOS: readonly EncabezadoOrdenable[] = Object.freeze([
  { columna: 'fuente', clave: 'guide.tables.column.source', numerica: false },
  { columna: 'registros', clave: 'guide.tables.column.records', numerica: true },
  { columna: 'importe', clave: 'guide.tables.column.amount', numerica: true },
])

const { t, locale } = useI18n()

const columnaActiva = ref<Columna>('importe')
const ascendente = ref(false)

/** Grouping separators follow the interface language, the figures do not. */
const formatoEntero = computed(() => new Intl.NumberFormat(locale.value === 'en' ? 'en-US' : 'es-MX'))

const filasOrdenadas = computed(() => {
  const factor = ascendente.value ? 1 : -1
  return [...FILAS].sort((primera, segunda) => {
    if (columnaActiva.value === 'fuente') {
      return factor * t(primera.claveFuente).localeCompare(t(segunda.claveFuente), locale.value)
    }
    const valorPrimera = columnaActiva.value === 'registros' ? primera.registros : primera.importe
    const valorSegunda = columnaActiva.value === 'registros' ? segunda.registros : segunda.importe
    return factor * (valorPrimera - valorSegunda)
  })
})

/** Value of aria-sort for a header: the state, not the affordance. */
function estadoDeOrden(columna: Columna): 'ascending' | 'descending' | 'none' {
  if (columnaActiva.value !== columna) {
    return 'none'
  }
  return ascendente.value ? 'ascending' : 'descending'
}

function ordenarPor(columna: Columna): void {
  if (columnaActiva.value === columna) {
    ascendente.value = !ascendente.value
    return
  }
  columnaActiva.value = columna
  ascendente.value = true
}
</script>

<template>
  <section
    data-lamina="tablas"
    class="flex flex-col gap-4 rounded-lg border border-line bg-surface p-[var(--card-padding)] shadow-reposo"
  >
    <header class="flex flex-col gap-1">
      <h2 class="font-display text-titulo-2 text-primary-dark">
        {{ t('guide.plate.tables') }}
      </h2>
      <p class="max-w-prose text-cuerpo text-muted">
        {{ t('guide.tables.description') }}
      </p>
      <p class="max-w-prose text-cuerpo text-muted">
        {{ t('guide.tables.sortHint') }}
      </p>
    </header>

    <div class="max-h-72 overflow-auto rounded-md border border-line-strong">
      <table class="w-full border-collapse text-left">
        <caption class="px-2 py-2 text-left text-etiqueta text-muted">
          {{ t('guide.tables.caption') }}
        </caption>
        <thead>
          <tr>
            <th
              v-for="encabezado in ENCABEZADOS"
              :key="encabezado.columna"
              scope="col"
              :aria-sort="estadoDeOrden(encabezado.columna)"
              :data-columna="encabezado.columna"
              class="sticky top-0 z-10 bg-primary-700 p-0 text-surface"
            >
              <button
                type="button"
                class="flex h-[var(--table-row-height)] w-full items-center gap-1 px-2 text-etiqueta"
                :class="[ANILLO_FOCO_INTERNO, encabezado.numerica ? 'justify-end' : 'justify-start']"
                :aria-label="t('guide.tables.sort', { column: t(encabezado.clave) })"
                @click="ordenarPor(encabezado.columna)"
              >
                {{ t(encabezado.clave) }}
                <Icon
                  :name="estadoDeOrden(encabezado.columna) === 'none' ? 'lucide:arrow-up-down' : 'lucide:arrow-up'"
                  class="size-4 shrink-0"
                  :class="estadoDeOrden(encabezado.columna) === 'descending' ? 'rotate-180' : ''"
                  aria-hidden="true"
                />
              </button>
            </th>
            <th
              scope="col"
              class="sticky top-0 z-10 h-[var(--table-row-height)] bg-primary-700 px-2 text-etiqueta text-surface"
            >
              {{ t('guide.tables.column.status') }}
            </th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="fila in filasOrdenadas"
            :key="fila.id"
            :data-fila="fila.id"
            class="h-[var(--table-row-height)] border-b border-line odd:bg-surface even:bg-surface-alt"
          >
            <th scope="row" class="px-2 text-left text-cuerpo font-normal text-ink">
              {{ t(fila.claveFuente) }}
            </th>
            <td class="px-2 text-right text-dato tabular-nums text-ink">
              {{ formatoEntero.format(fila.registros) }}
            </td>
            <td class="px-2 text-right text-dato tabular-nums text-ink">
              {{ formatoEntero.format(fila.importe) }}
            </td>
            <td class="px-2">
              <span
                class="inline-flex items-center rounded-sm border px-2 py-0.5 text-etiqueta"
                :class="fila.clasesEstado"
              >
                {{ t(fila.claveEstado) }}
              </span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!--
      The empty table is part of the system, not an accident: without it, every
      screen improvises its own way of saying that a filter matched nothing.
    -->
    <div
      data-tabla-vacia
      class="flex flex-col items-center gap-1 rounded-md border border-dashed border-line-strong bg-surface-alt px-4 py-6 text-center"
    >
      <Icon name="lucide:inbox" class="size-6 text-ink" aria-hidden="true" />
      <p class="text-titulo-3 text-ink">
        {{ t('guide.tables.empty.title') }}
      </p>
      <p class="max-w-prose text-cuerpo text-ink">
        {{ t('guide.tables.empty.body') }}
      </p>
    </div>
  </section>
</template>
