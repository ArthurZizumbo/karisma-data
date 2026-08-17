<script setup lang="ts">
/**
 * Domain counts of the catalogue screen, drawn as the left column.
 *
 * The counts arrive already computed over the WHOLE matching set and never
 * over the visible page, which is what keeps a chip from changing meaning as
 * the reader narrows: "Riesgo 34" means thirty four matches in the catalogue,
 * not thirty four rows below.
 *
 * The component decides nothing. It receives the counts and the active domain
 * and emits the one the reader chose; narrowing and re-querying belong to
 * `useBusquedaCatalogo`, which owns the request.
 *
 * The narrowed row is painted with the selection token and not only with a
 * darker ink. `--color-seleccion` is the tint the design system reserves for
 * exactly this -a neutral one under the default theme and a tint of the action
 * colour under the institutional one- so the column says which domain is
 * filtering the result with the same mark the rest of the portal uses.
 */
import type { ConteoDominio } from '~/composables/useBusquedaCatalogo'
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { claveDeFaceta } from '~/types/linaje'
import { ANILLO_FOCO } from '~/utils/foco'

const props = defineProps<{
  /** Domains of the whole matching set, ordered by the composable. */
  conteos: readonly ConteoDominio[]
  /** Domain the reader narrowed to, or null for the whole catalogue. */
  activo: string | null
}>()

const emit = defineEmits<{ filtrar: [dominio: string | null] }>()

const { t } = useI18n()

/** One row of the column: the domain, already translated, and its count. */
interface OpcionDominio {
  codigo: string
  etiqueta: string
  total: number
}

const opciones = computed<OpcionDominio[]>(() =>
  props.conteos.map(({ codigo, total }) => {
    const clave = claveDeFaceta('domain', codigo)
    // An unknown code is shown as it arrived. Printing the dotted key would
    // put `catalog.facet.domain.tesoreria` on screen, in both languages.
    return { codigo, total, etiqueta: clave === null ? codigo : t(clave) }
  }),
)

/** Matches of the whole set, so "all domains" carries a number too. */
const total = computed(() => props.conteos.reduce((suma, conteo) => suma + conteo.total, 0))
</script>

<template>
  <section
    data-filtro-dominios
    role="group"
    :aria-label="t('catalog.explore.domains.title')"
    class="flex flex-col gap-2"
  >
    <h2 class="flex items-center gap-2 text-titulo-3 text-corriente-pleno">
      <Icon name="lucide:list-filter" class="size-4 shrink-0 text-corriente-tenue" aria-hidden="true" />
      {{ t('catalog.explore.domains.title') }}
    </h2>

    <p v-if="opciones.length === 0" data-sin-dominios class="text-micro text-corriente-tenue">
      {{ t('catalog.explore.domains.empty') }}
    </p>

    <template v-else>
      <ul class="flex flex-col">
        <li>
          <button
            type="button"
            data-dominio="todos"
            :aria-pressed="activo === null"
            class="flex min-h-11 w-full items-center justify-between gap-3 border-b border-grid px-2 text-cuerpo"
            :class="[
              ANILLO_FOCO,
              activo === null ? 'bg-seleccion text-corriente-pleno' : 'text-corriente-tenue hover:text-corriente-medio',
            ]"
            @click="emit('filtrar', null)"
          >
            <span>{{ t('catalog.explore.domains.all') }}</span>
            <span class="font-mono text-micro">{{ total }}</span>
          </button>
        </li>

        <li v-for="opcion in opciones" :key="opcion.codigo">
          <button
            type="button"
            :data-dominio="opcion.codigo"
            :aria-pressed="activo === opcion.codigo"
            class="flex min-h-11 w-full items-center justify-between gap-3 border-b border-grid px-2 text-cuerpo"
            :class="[
              ANILLO_FOCO,
              activo === opcion.codigo ? 'bg-seleccion text-corriente-pleno' : 'text-corriente-tenue hover:text-corriente-medio',
            ]"
            @click="emit('filtrar', activo === opcion.codigo ? null : opcion.codigo)"
          >
            <span class="truncate">{{ opcion.etiqueta }}</span>
            <span class="font-mono text-micro">{{ opcion.total }}</span>
          </button>
        </li>
      </ul>

      <p class="text-micro text-corriente-tenue">
        {{ t('catalog.explore.domains.hint') }}
      </p>
    </template>
  </section>
</template>
