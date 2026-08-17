<script setup lang="ts">
/**
 * US-026, level 3 - the twenty four observed months and the projected one.
 *
 * A real `<table>` and not a grid of `<div>`: the chart above is a picture with
 * no structure, so this is the only place where a screen reader can walk the
 * figures row by row. The `<caption>` says what the table is and `scope` ties
 * every cell to its header.
 *
 * The projected row is marked with a word and not only with a shade: it is the
 * one row of the table that is not a measurement, and colour alone cannot carry
 * that difference. The mark travels on the row and not on its position, which
 * is what lets the reader sort the table by value without losing track of which
 * figure is the forecast.
 *
 * The columns sort on the RAW figure and print the formatted one. Sorting the
 * printed text would order `1 284,5` before `987,6` because that is what a
 * string comparison says, and the reader would be looking at a column that
 * claims to be sorted and is not.
 *
 * The explorer link closes the chain. Three levels of progressive disclosure
 * that end in a dead end would be three levels of nothing: the link carries the
 * physical column of the metric as the search term, so the reader lands on the
 * catalogue entry the figure came from.
 */
import type { HistoricoMetrica, MetricaTablero, Proyeccion } from '~/types/prediccion'

import { computed, h } from 'vue'
import { useI18n } from 'vue-i18n'

import ComunTablaDatos from '~/components/comun/TablaDatos.vue'
import { esCodigoIdioma } from '~/composables/useIdioma'
import { ANILLO_FOCO } from '~/utils/foco'
import { formatearMes, formatearCifra, formatearCambio } from '~/utils/formatoTablero'
import { destinoExplorador } from '~/utils/metricasTablero'
import { definirColumnas } from '~/utils/tablaDatos'
import { variacionPorcentual } from '~/utils/proyeccion'

const props = defineProps<{
  metrica: MetricaTablero
  historico: HistoricoMetrica
  proyeccion: Proyeccion
}>()

const { t, locale } = useI18n()

const idioma = computed(() => (esCodigoIdioma(locale.value) ? locale.value : 'es'))

interface FilaDetalle {
  /** ISO month, which is also what the month column sorts on. */
  readonly clave: string
  readonly mes: string
  readonly valor: string
  readonly variacion: string
  /** Raw figure behind `valor`, so the column sorts by magnitude. */
  readonly valorCrudo: number
  /** Raw change behind `variacion`. Absent on the first row, which has none. */
  readonly cambioCrudo?: number
  readonly proyectada: boolean
}

const filas = computed<readonly FilaDetalle[]>(() => {
  const puntos = [...props.historico.puntos, props.proyeccion.proyectado]
  const hueco = t('forecast.table.gap')

  return puntos.map((punto, indice) => {
    const anterior = puntos[indice - 1]
    const cambio
      = anterior === undefined ? null : variacionPorcentual(anterior.valor, punto.valor)
    return {
      clave: punto.mes,
      mes: formatearMes(punto.mes, idioma.value),
      valor: formatearCifra(punto.valor, props.metrica.unidad, idioma.value) ?? hueco,
      variacion: formatearCambio(cambio, idioma.value) ?? hueco,
      valorCrudo: punto.valor,
      cambioCrudo: cambio ?? undefined,
      proyectada: indice === puntos.length - 1,
    }
  })
})

const columnas = computed(() => definirColumnas<FilaDetalle>([
  {
    id: 'mes',
    accessorFn: fila => fila.clave,
    header: t('forecast.table.month'),
    sortFn: 'text',
    meta: { encabezadoFila: true },
    cell: ({ row }) => (row.original.proyectada
      ? h('span', [
          row.original.mes,
          ' ',
          h(
            'span',
            { class: 'text-micro text-corriente-tenue' },
            t('forecast.table.projectedRow'),
          ),
        ])
      : row.original.mes),
  },
  {
    id: 'valor',
    accessorFn: fila => fila.valorCrudo,
    header: t('forecast.table.value'),
    sortFn: 'basic',
    meta: { alineacion: 'fin', clase: 'tabular-nums' },
    cell: ({ row }) => row.original.valor,
  },
  {
    id: 'variacion',
    accessorFn: fila => fila.cambioCrudo,
    header: t('forecast.table.change'),
    sortFn: 'basic',
    // The first month has no previous one to compare against, and a hole that
    // floated to the top on every sort would read as the smallest change.
    sortUndefined: 'last',
    meta: { alineacion: 'fin', clase: 'tabular-nums' },
    cell: ({ row }) => row.original.variacion,
  },
]))

const destino = computed(() => destinoExplorador(props.metrica))

/** Marks the forecast row wherever the order puts it. */
function atributosFila(fila: FilaDetalle): Record<string, string> {
  return { 'data-fila': fila.proyectada ? 'proyectada' : 'observada' }
}
</script>

<template>
  <div data-nivel="3" class="flex flex-col gap-3">
    <ComunTablaDatos
      :columnas="columnas"
      :filas="filas"
      :titulo="t('forecast.table.caption', { metric: t(props.metrica.claveEtiqueta) })"
      :id-fila="(fila: FilaDetalle) => fila.clave"
      :atributos-fila="atributosFila"
    />

    <NuxtLink
      data-accion="explorar"
      :to="destino"
      class="inline-flex min-h-11 w-fit items-center gap-2 rounded-md border border-corriente-apagado px-3 text-etiqueta text-corriente-medio hover:border-corriente-medio hover:text-corriente-pleno"
      :class="ANILLO_FOCO"
    >
      {{ t('forecast.action.explore') }}
    </NuxtLink>
  </div>
</template>
