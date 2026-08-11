<script setup lang="ts">
import type { TonoToken } from '~/utils/tokens.generated'

import { useClipboard } from '@vueuse/core'
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { ANILLO_FOCO } from '~/utils/foco'
import { FAMILIAS, NEUTROS, SEMANTICOS, SERIES } from '~/utils/tokens.generated'

/**
 * Colour plate of the living design system.
 *
 * Every hexadecimal on screen is read from the generated palette, never typed:
 * that is the whole reason the plate exists. A value written by hand here would
 * look right and would still make the application diverge from the PDF, which
 * is the defect US-UX-09 was opened to remove.
 */
defineOptions({ name: 'LaminaPaleta' })

/** A labelled block of the plate. Families keep the label the generator emits. */
interface GrupoPaleta {
  /** Stable identifier, also used as the list key. */
  readonly id: string
  /** Translation key of the group heading. */
  readonly clave: string
  /** Generated Spanish label of a brand family, absent on the other groups. */
  readonly etiqueta: string | null
  readonly tokens: readonly TonoToken[]
}

const GRUPOS: readonly GrupoPaleta[] = Object.freeze([
  ...FAMILIAS.map(familia => ({
    id: familia.clave,
    clave: 'guide.palette.group.family',
    etiqueta: familia.etiqueta,
    tokens: familia.tonos,
  })),
  { id: 'neutros', clave: 'guide.palette.group.neutrals', etiqueta: null, tokens: NEUTROS },
  { id: 'semanticos', clave: 'guide.palette.group.semantic', etiqueta: null, tokens: SEMANTICOS },
  { id: 'series', clave: 'guide.palette.group.series', etiqueta: null, tokens: SERIES },
])

const TOTAL_TOKENS = GRUPOS.reduce((suma, grupo) => suma + grupo.tokens.length, 0)

const { t } = useI18n()

/**
 * Clipboard access, with the unsupported branch visible instead of silent.
 *
 * `isSupported` is false during SSR and in a browser that denies the API, so
 * the copy control declares itself unavailable and the value stays printed in
 * full: the reader can still select it by hand.
 */
const { copy, copied, isSupported } = useClipboard()

/** Value of the last swatch the reader asked to copy, announced politely. */
const ultimoHex = ref('')

/** True once a copy was attempted and the browser refused it. */
const falloAlCopiar = ref(false)

async function copiarTono(tono: TonoToken): Promise<void> {
  ultimoHex.value = tono.hex
  falloAlCopiar.value = false
  try {
    await copy(tono.hex)
  }
  catch {
    // A denied clipboard permission rejects the write. Without this branch the
    // rejection would surface as an unhandled promise and the reader would be
    // left believing the value was copied.
    falloAlCopiar.value = true
  }
}
</script>

<template>
  <section
    data-lamina="paleta"
    class="flex flex-col gap-4 rounded-lg border border-line bg-surface p-[var(--card-padding)] shadow-reposo"
  >
    <header class="flex flex-col gap-1">
      <h2 class="font-display text-titulo-2 text-primary-dark">
        {{ t('guide.plate.palette') }}
      </h2>
      <p class="max-w-prose text-cuerpo text-muted">
        {{ t('guide.palette.description') }}
      </p>
      <p class="text-etiqueta text-muted">
        {{ t('guide.palette.total', { total: TOTAL_TOKENS }) }}
      </p>
      <p v-if="!isSupported || falloAlCopiar" class="text-cuerpo text-accent-text">
        {{ t('guide.palette.unsupported') }}
      </p>
    </header>

    <!--
      Polite live region: the confirmation of a copy is the only feedback the
      control gives, and a colour change alone never reaches a screen reader.
    -->
    <p role="status" aria-live="polite" class="min-h-5 text-cuerpo text-success-900">
      <span v-if="copied">{{ t('guide.palette.copied', { hex: ultimoHex }) }}</span>
    </p>

    <div v-for="grupo in GRUPOS" :key="grupo.id" class="flex flex-col gap-2">
      <h3 class="font-display text-titulo-3 text-ink">
        {{ t(grupo.clave) }}
        <span v-if="grupo.etiqueta" lang="es" class="text-cuerpo text-muted">
          · {{ grupo.etiqueta }}
        </span>
      </h3>

      <ul class="grid gap-[var(--grid-gap)] sm:grid-cols-3 lg:grid-cols-5">
        <li v-for="tono in grupo.tokens" :key="tono.nombre" class="flex flex-col gap-1">
          <button
            type="button"
            :data-token="tono.nombre"
            :disabled="!isSupported"
            :aria-label="t('guide.palette.copy', { hex: tono.hex, token: tono.nombre })"
            class="flex flex-col gap-1 rounded-md border border-line-strong bg-surface p-2 text-left hover:border-primary disabled:cursor-not-allowed"
            :class="ANILLO_FOCO"
            @click="copiarTono(tono)"
          >
            <span
              class="h-10 w-full rounded-sm border border-line-strong"
              :style="{ backgroundColor: tono.hex }"
              aria-hidden="true"
            />
            <span class="text-cuerpo text-ink">{{ tono.nombre }}</span>
            <span class="text-etiqueta tabular-nums text-ink">{{ tono.hex }}</span>
            <span class="text-micro text-muted">{{ tono.clase }}</span>
            <span class="flex flex-wrap gap-1">
              <span
                v-if="tono.esAncla"
                :title="t('guide.palette.anchorHint')"
                class="rounded-sm border border-accent-700 px-1 text-micro text-accent-text"
              >
                {{ t('guide.palette.anchor') }}
              </span>
              <span
                v-if="tono.reusa"
                class="rounded-sm border border-line-strong px-1 text-micro text-muted"
              >
                {{ t('guide.palette.reuse', { token: tono.reusa }) }}
              </span>
            </span>
          </button>
          <span lang="es" class="text-micro text-muted">{{ tono.uso }}</span>
        </li>
      </ul>
    </div>
  </section>
</template>
