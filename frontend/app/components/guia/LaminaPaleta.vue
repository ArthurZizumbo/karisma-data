<script setup lang="ts">
/**
 * Colour plate: the specimen leads and the prose folds.
 *
 * The measured page put its first colour 718 pixels down, behind four
 * paragraphs of justification, in a 508 pixel column that left 55% of the width
 * empty. The audience decided on 11-ago-2026 is the team that builds: they come
 * to copy a token, compare a state or check a ratio, so the swatch comes first
 * and the reasoning waits behind a disclosure.
 *
 * Every hex and every ratio is read from the store, never typed. The store
 * resolves each token against the mode on screen, so switching to dark does not
 * leave a light-mode value printed under a dark swatch.
 */
import { useI18n } from 'vue-i18n'
import { useClipboard } from '@vueuse/core'
import { ANILLO_FOCO } from '~/utils/foco'
import { useSistemaDiseno } from '~/stores/sistemaDiseno'
import type { TokenColor } from '~/utils/tokens.generated'

const { t } = useI18n()
const sistema = useSistemaDiseno()
const { copy, copied, isSupported } = useClipboard()

/**
 * The five groups, in the order the emitter lays them out in `TOKENS`.
 *
 * Every group the store exposes is listed here and the order matches the
 * source, because this plate is what the A4 rubric grades as the living style
 * guide: a group left out makes the heading count tokens the page never paints,
 * which is the defect `laminas.spec.ts` caught when `accion` arrived.
 */
const GRUPOS: readonly { clave: string, tokens: readonly TokenColor[] }[] = [
  { clave: 'surface', tokens: sistema.superficie },
  { clave: 'current', tokens: sistema.corriente },
  { clave: 'action', tokens: sistema.accion },
  { clave: 'semantic', tokens: sistema.semanticos },
  { clave: 'series', tokens: sistema.series },
]

/** Ratio of a token against the ground, in the mode on screen. */
function razon(nombre: string): number | undefined {
  return sistema.contrastes.find((par) => par.token === nombre)?.ratio
}
</script>

<template>
  <section data-lamina="paleta" class="flex flex-col gap-6">
    <div class="flex flex-wrap items-baseline justify-between gap-2">
      <h2 class="text-titulo-2 text-corriente-pleno">
        {{ t('guide.palette.title') }}
      </h2>
      <p class="text-micro text-corriente-tenue">
        {{ t('guide.palette.count', { count: sistema.tokens.length }) }}
      </p>
    </div>

    <div v-for="grupo in GRUPOS" :key="grupo.clave" class="flex flex-col gap-2">
      <h3 class="text-etiqueta uppercase text-corriente-tenue">
        {{ t(`guide.palette.group.${grupo.clave}`) }}
      </h3>
      <ul class="grid grid-cols-[repeat(auto-fill,minmax(180px,1fr))] gap-3">
        <li
          v-for="token in grupo.tokens"
          :key="token.nombre"
          data-token
          class="flex flex-col border border-grid bg-ground"
        >
          <!-- The swatch is the specimen: it takes the height, not the caption. -->
          <span
            class="h-16 w-full border-b border-grid"
            :style="{ backgroundColor: sistema.valor(token) }"
            aria-hidden="true"
          />
          <div class="flex flex-col gap-1 p-3">
            <code class="text-etiqueta text-corriente-pleno">{{ token.nombre }}</code>
            <button
              type="button"
              data-copiar
              class="flex items-center gap-1 text-left font-mono text-micro text-corriente-medio hover:text-corriente-pleno"
              :class="ANILLO_FOCO"
              :aria-label="t('guide.palette.copy', { token: token.nombre })"
              @click="copy(sistema.valor(token))"
            >
              <Icon name="lucide:copy" class="size-3 shrink-0" aria-hidden="true" />
              {{ sistema.valor(token) }}
            </button>
            <p class="flex items-center gap-1 text-micro text-corriente-tenue">
              <template v-if="razon(token.nombre) !== undefined">
                <Icon
                  v-if="!token.informa"
                  name="lucide:eye-off"
                  class="size-3 shrink-0"
                  aria-hidden="true"
                />
                {{ razon(token.nombre) }}:1
                <span v-if="!token.informa">{{ t('guide.palette.decorative') }}</span>
              </template>
            </p>
          </div>
        </li>
      </ul>
    </div>

    <p v-if="copied" role="status" class="text-micro text-ok">
      {{ t('guide.palette.copied') }}
    </p>
    <!--
      `isSupported` is false on the server, where there is no navigator, and
      true in the browser: rendering it directly emitted a node the client then
      discarded, which is the hydration mismatch the audit found. ClientOnly
      keeps the branch out of the server pass entirely.
    -->
    <ClientOnly>
      <p v-if="!isSupported" class="text-micro text-corriente-tenue">
        {{ t('guide.palette.noClipboard') }}
      </p>
    </ClientOnly>

    <!-- The reasoning that used to open the plate now closes it. -->
    <details class="border-t border-grid pt-3">
      <summary
        class="cursor-pointer text-etiqueta text-corriente-tenue"
        :class="ANILLO_FOCO"
      >
        {{ t('guide.palette.why') }}
      </summary>
      <ul class="mt-2 flex max-w-(--medida-maxima) flex-col gap-1">
        <li
          v-for="regla in sistema.reglas"
          :key="regla"
          class="text-cuerpo text-corriente-medio"
        >
          {{ regla }}
        </li>
      </ul>
    </details>
  </section>
</template>
