<script setup lang="ts">
/**
 * The one block of the home screen that carries a list.
 *
 * Recent searches, favourites, alerts, exports and saved queries are the same
 * object -a label, a route, sometimes a date and sometimes a badge- shown five
 * times, so they are one component and not five nearly identical ones. What
 * differs between them is content, and content arrives as data.
 *
 * Three of the four unhappy states are designed here, and the fourth is
 * deliberately absent: there is no network on this screen, so there is no error
 * state to design, and inventing one would be scaffolding. "No permission" is
 * decided by the guard before the screen mounts.
 *
 * The loading state renders exactly as many placeholder rows as the block will
 * hold, with the same row height, so nothing on the page moves when the session
 * resolves. A spinner of a different size would make the whole column jump.
 */
import type { ClaveBloque, ElementoLista, EstadoBloque, TonoInsignia } from '~/types/espacios'
import { computed, useId } from 'vue'
import { useI18n } from 'vue-i18n'
import { formatearFechaHora } from '~/utils/fechas'
import { ANILLO_FOCO } from '~/utils/foco'

const props = defineProps<{
  /** Block of the composition contract this list stands for. */
  bloque: ClaveBloque
  /** Translation key of the heading. Passed whole, never composed. */
  claveTitulo: string
  /** Translation key of the empty state. */
  claveVacio: string
  /** Items to render, already ordered by whoever owns them. */
  elementos: readonly ElementoLista[]
  /** True while the session has not resolved yet. */
  cargando?: boolean
}>()

const { t, locale } = useI18n()

const idTitulo = useId()

/**
 * Row geometry, written once and shared by the real row and its placeholder.
 *
 * A literal and not a composed string: Tailwind reads these sources with a text
 * scanner, and a class assembled at run time produces no CSS rule at all.
 */
const FILA = 'flex min-h-11 items-center gap-3 border-b border-grid px-1 last:border-b-0'

const estado = computed<EstadoBloque>(() => {
  if (props.cargando === true) {
    return 'cargando'
  }
  return props.elementos.length === 0 ? 'vacio' : 'lista'
})

/** Only a block that actually shows samples claims to be showing samples. */
const conMuestras = computed(() => props.elementos.length > 0)

/** Border and text of a badge. The word is always printed next to the colour. */
const CLASE_INSIGNIA: Readonly<Record<TonoInsignia, string>> = {
  neutro: 'border-grid text-corriente-tenue',
  exito: 'border-ok text-ok',
  atencion: 'border-aviso text-aviso',
  peligro: 'border-error text-error',
}
</script>

<template>
  <section
    :data-bloque="bloque"
    :data-estado="estado"
    :data-origen="conMuestras ? 'ejemplo' : undefined"
    :aria-labelledby="idTitulo"
    :aria-busy="estado === 'cargando' ? 'true' : undefined"
    class="flex flex-col gap-2"
  >
    <div class="flex flex-wrap items-baseline justify-between gap-2">
      <h2 :id="idTitulo" class="text-titulo-3 text-corriente-pleno">
        {{ t(claveTitulo) }}
      </h2>
      <span
        v-if="conMuestras"
        data-insignia-muestra
        class="border border-grid px-1.5 text-micro uppercase text-corriente-tenue"
      >
        {{ t('workspace.sample.badge') }}
      </span>
    </div>

    <ul v-if="estado === 'cargando'" class="flex flex-col">
      <li v-for="posicion in elementos.length" :key="posicion" data-esqueleto :class="FILA">
        <span class="h-3 w-1/2 bg-ground-alt" aria-hidden="true" />
      </li>
    </ul>

    <p v-else-if="estado === 'vacio'" data-vacio class="text-cuerpo text-corriente-tenue">
      {{ t(claveVacio) }}
    </p>

    <ul v-else class="flex flex-col">
      <li v-for="elemento in elementos" :key="elemento.id" :data-elemento="elemento.id" :class="FILA">
        <NuxtLink
          :to="elemento.destino"
          class="flex min-w-0 flex-1 items-center gap-2 text-cuerpo text-corriente-pleno hover:underline"
          :class="ANILLO_FOCO"
        >
          <span class="truncate">{{ t(elemento.claveEtiqueta) }}</span>
          <span
            v-if="elemento.termino"
            class="shrink-0 font-mono text-micro text-corriente-tenue"
          >{{ elemento.termino }}</span>
        </NuxtLink>

        <span
          v-if="elemento.insignia"
          :data-insignia="elemento.insignia.tono"
          class="shrink-0 border px-1.5 text-micro"
          :class="CLASE_INSIGNIA[elemento.insignia.tono]"
        >
          {{ t(elemento.insignia.claveTexto) }}
        </span>

        <time
          v-if="elemento.fecha"
          :datetime="elemento.fecha"
          class="shrink-0 text-micro tabular-nums text-corriente-tenue"
        >{{ formatearFechaHora(elemento.fecha, locale) }}</time>
      </li>
    </ul>

    <slot name="accion" />
  </section>
</template>
