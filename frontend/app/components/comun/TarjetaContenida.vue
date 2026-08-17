<script setup lang="ts">
/**
 * The contained surface of the design system: a hairline, a small radius and a
 * bar of colour on the left edge.
 *
 * Three properties, and each one is a decision the guide already took:
 *
 * 1. A HAIRLINE AND NOT A SHADOW. The portal is dense, and a shadow under
 *    every card turns a screen of figures into a screen of floating boxes. One
 *    pixel of `--color-grid` separates without adding depth, and it is the
 *    same rule that already draws the tables.
 * 2. THE RADIUS COMES FROM THE THEME, not from a property. Under the default
 *    theme the card is square, which is what the fifteen delivered screenshots
 *    show; under the institutional one it takes `--radius-lg`, six pixels,
 *    inside the eight the guide allows. The condition lives in the class and
 *    not in the script because `data-tema` is on the root element: asking the
 *    store here would make every card a subscriber of a value it only needs in
 *    order to pick a border radius.
 * 3. THE BAR IS A CHANNEL, NOT DECORATION. It is painted from the semantic
 *    tokens, so a card whose channel is `error` carries the same colour as the
 *    error state everywhere else, and it never travels alone: whatever the card
 *    holds says in words what the bar says in colour.
 *
 * `neutro` is the default and paints no bar. A card that always shows a stripe
 * would be a card whose stripe means nothing.
 */
import type { CanalTarjeta } from '~/types/superficie'

import { computed, useId } from 'vue'

const props = defineProps<{
  /** Channel the surface belongs to. Absent means no channel and no bar. */
  canal?: CanalTarjeta
  /** Heading of the card, ALREADY TRANSLATED. Absent leaves the card unlabelled. */
  titulo?: string
}>()

const idTitulo = useId()

const canal = computed<CanalTarjeta>(() => props.canal ?? 'neutro')

/** True when the card carries a channel, which is when it paints a bar. */
const conBarra = computed(() => canal.value !== 'neutro')

/**
 * Fill of the left bar, one entry per channel.
 *
 * Whole literals and never a composed string: Tailwind reads these sources
 * with a text scanner, so `bg-${canal}` would produce no rule at all.
 */
const RELLENO: Readonly<Record<CanalTarjeta, string>> = {
  accion: 'bg-accion',
  aviso: 'bg-aviso',
  ok: 'bg-ok',
  error: 'bg-error',
  neutro: '',
}

/**
 * Chrome of the surface.
 *
 * The radius is conditioned on the theme attribute of the root element with an
 * arbitrary variant, which compiles to `[data-tema=institucional] .clase`. The
 * default theme emits no `data-tema`, so it gets no radius and its delivered
 * screenshots keep describing the product.
 */
const SUPERFICIE = 'relative flex flex-col border border-grid bg-ground-alt '
  + '[[data-tema=institucional]_&]:rounded-lg'
</script>

<template>
  <article
    :data-tarjeta="canal"
    :aria-labelledby="titulo === undefined ? undefined : idTitulo"
    :class="[SUPERFICIE, conBarra ? 'gap-2 py-4 pl-5 pr-4' : 'gap-2 p-4']"
  >
    <span
      v-if="conBarra"
      data-barra-canal
      aria-hidden="true"
      class="absolute inset-y-0 left-0 w-1"
      :class="RELLENO[canal]"
    />

    <h3 v-if="titulo !== undefined" :id="idTitulo" class="text-titulo-3 text-corriente-medio">
      {{ titulo }}
    </h3>

    <slot />
  </article>
</template>
