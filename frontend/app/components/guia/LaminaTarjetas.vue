<script setup lang="ts">
/**
 * Card plate, rebuilt in the diagram world.
 *
 * The measured version was card soup: five rectangles with the same 1px border
 * and the same visual weight, so the consolidated balance carried no more
 * authority than the empty state, and both of the declared elevation levels
 * went unused. The rebuild ranks them.
 *
 * The tool call is where the world earns its keep. It is a chain -announce,
 * run, result, error- so it is drawn as one: nodes tapping off a single rule,
 * with current rising along the ramp as the step completes. That is also the
 * product's anti-hallucination rule made inspectable: the query is visible
 * before the figure, and the failed step carries no figure at all.
 */
import { useI18n } from 'vue-i18n'
import { ANILLO_FOCO } from '~/utils/foco'

const { t } = useI18n()

/** The four unhappy states, each with the shape that carries its meaning. */
const ESTADOS = Object.freeze([
  { id: 'loading', icono: 'lucide:loader', color: 'text-corriente-tenue' },
  { id: 'empty', icono: 'lucide:inbox', color: 'text-corriente-tenue' },
  { id: 'error', icono: 'lucide:x-circle', color: 'text-error', accion: 'retry' },
  { id: 'forbidden', icono: 'lucide:lock', color: 'text-aviso', accion: 'request' },
])

/**
 * The four moments of a tool call, in order.
 *
 * `corriente` is the rung of the luminance ramp each moment sits on: the chain
 * literally brightens as it advances, which is the one channel no dichromacy
 * loses.
 */
const MOMENTOS = Object.freeze([
  { id: 'announced', corriente: 'bg-corriente-apagado', icono: 'lucide:circle-dashed' },
  { id: 'running', corriente: 'bg-corriente-tenue', icono: 'lucide:loader' },
  { id: 'done', corriente: 'bg-corriente-pleno', icono: 'lucide:check' },
  { id: 'error', corriente: 'bg-error', icono: 'lucide:x' },
])
</script>

<template>
  <section data-lamina="tarjetas" class="flex flex-col gap-8">
    <h2 class="text-titulo-2 text-corriente-pleno">
      {{ t('guide.plate.cards') }}
    </h2>

    <!--
      The indicator leads and takes the width it deserves. No border: the figure
      is the object, and a rule tapping in from the left is the only chrome it
      needs.
    -->
    <article data-tarjeta="kpi" class="max-w-lg border-l-2 border-info pl-5">
      <p class="text-etiqueta uppercase text-corriente-tenue">
        {{ t('guide.cards.kpi.label') }}
      </p>
      <p class="font-mono text-display tabular-nums text-corriente-pleno">
        1 284 350
      </p>
      <p class="mt-1 flex items-center gap-1 text-cuerpo text-ok">
        <Icon name="lucide:trending-up" class="size-4 shrink-0" aria-hidden="true" />
        {{ t('guide.cards.kpi.delta') }}
      </p>
      <!-- Honesty of the demo: this label is an acceptance criterion, not decoration. -->
      <p class="mt-2 flex items-center gap-1 text-micro text-aviso">
        <Icon name="lucide:triangle-alert" class="size-3 shrink-0" aria-hidden="true" />
        {{ t('guide.cards.kpi.footnote') }}
      </p>
    </article>

    <div class="flex flex-col gap-3">
      <h3 class="text-titulo-3 text-corriente-pleno">
        {{ t('guide.cards.statesTitle') }}
      </h3>
      <!--
        Secondary by construction: half the measure, no fill, and the divider
        does the separating that five identical borders used to attempt.
      -->
      <ul class="grid gap-x-8 gap-y-4 md:grid-cols-2 xl:grid-cols-4">
        <li
          v-for="estado in ESTADOS"
          :key="estado.id"
          :data-estado="estado.id"
          class="flex flex-col gap-1 border-t border-grid pt-3"
        >
          <p class="flex items-center gap-2 text-titulo-3 text-corriente-pleno">
            <Icon
              :name="estado.icono"
              class="size-4 shrink-0"
              :class="estado.color"
              aria-hidden="true"
            />
            {{ t(`guide.cards.state.${estado.id}`) }}
          </p>
          <!--
            The skeleton reserves the height of the figure so nothing jumps.
            It uses the dimmest rung of the current ramp and not the alternate
            ground: a surface tone measures 1.08:1 against the page and the
            placeholder was invisible, which defeats the whole point of showing
            that something is on its way.
          -->
          <span
            v-if="estado.id === 'loading'"
            class="h-9 w-32 animate-pulse rounded-sm bg-corriente-apagado"
            aria-hidden="true"
          />
          <p class="text-cuerpo text-corriente-medio">
            {{ t(`guide.cards.state.${estado.id}Body`) }}
          </p>
          <button
            v-if="estado.accion"
            type="button"
            class="mt-1 w-fit border border-corriente-medio px-3 py-1 text-etiqueta text-corriente-pleno hover:bg-corriente-pleno hover:text-ground"
            :class="ANILLO_FOCO"
          >
            {{ t(`guide.cards.state.${estado.accion}`) }}
          </button>
        </li>
      </ul>
    </div>

    <div class="flex flex-col gap-3">
      <h3 class="text-titulo-3 text-corriente-pleno">
        {{ t('guide.cards.toolCall.title') }}
      </h3>
      <p class="max-w-(--medida-maxima) text-cuerpo text-corriente-medio">
        {{ t('guide.cards.toolCall.note') }}
      </p>

      <!-- The chain: one rule, four nodes tapping off it, current rising. -->
      <ol class="ml-2 flex flex-col border-l border-corriente-apagado">
        <li
          v-for="momento in MOMENTOS"
          :key="momento.id"
          :data-momento="momento.id"
          class="relative py-3 pl-6"
        >
          <span
            class="absolute -left-[5px] top-5 size-2.5 rounded-full"
            :class="momento.corriente"
            aria-hidden="true"
          />
          <p class="flex items-center gap-2 text-titulo-3 text-corriente-pleno">
            <Icon :name="momento.icono" class="size-4 shrink-0" aria-hidden="true" />
            {{ t(`guide.cards.toolCall.state.${momento.id}`) }}
          </p>
          <!-- The query is visible in all four moments, including the failure. -->
          <p class="mt-1 font-mono text-micro text-corriente-tenue">
            {{ t('guide.cards.toolCall.query') }}
          </p>
          <p class="mt-1 max-w-(--medida-maxima) text-cuerpo text-corriente-medio">
            {{ t(`guide.cards.toolCall.body.${momento.id}`) }}
          </p>
          <div class="mt-2 flex gap-2">
            <button
              v-if="momento.id === 'running'"
              type="button"
              class="border border-corriente-medio px-3 py-1 text-etiqueta text-corriente-pleno"
              :class="ANILLO_FOCO"
            >
              {{ t('guide.cards.toolCall.stop') }}
            </button>
            <button
              v-if="momento.id === 'done'"
              type="button"
              class="border border-corriente-medio px-3 py-1 text-etiqueta text-corriente-pleno"
              :class="ANILLO_FOCO"
            >
              {{ t('guide.cards.toolCall.lineage') }}
            </button>
            <button
              v-if="momento.id === 'error'"
              type="button"
              class="border border-error px-3 py-1 text-etiqueta text-error"
              :class="ANILLO_FOCO"
            >
              {{ t('guide.cards.toolCall.retry') }}
            </button>
          </div>
        </li>
      </ol>
    </div>

    <details class="border-t border-grid pt-3">
      <summary class="cursor-pointer text-etiqueta text-corriente-tenue" :class="ANILLO_FOCO">
        {{ t('guide.palette.why') }}
      </summary>
      <p class="mt-2 max-w-(--medida-maxima) text-cuerpo text-corriente-medio">
        {{ t('guide.cards.description') }}
      </p>
    </details>
  </section>
</template>
