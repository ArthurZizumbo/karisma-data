<script setup lang="ts">
import type { NuxtError } from '#app'
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import CabeceraProducto from '~/components/comun/CabeceraProducto.vue'
import FranjaAlcance from '~/components/nav/FranjaAlcance.vue'
import { ANILLO_FOCO } from '~/utils/foco'
import { RUTA_INDICE } from '~/utils/navegacion'

const props = defineProps<{ error: NuxtError }>()

const { t } = useI18n()

/** Cause stated in the reader language, never the raw stack trace. */
const CLAVES_DE_CAUSA: Record<number, string> = {
  403: 'error.cause.forbidden',
  404: 'error.cause.notFound',
  500: 'error.cause.serverError',
}

const CLAVE_GENERICA = 'error.cause.unknown'

// statusCode is optional in NuxtError: an error thrown without a code arrived
// here as undefined and was used to index anyway. nuxt typecheck caught it, and
// until now it was not running in any gate.
const claveDeCausa = computed(() =>
  props.error.statusCode === undefined
    ? CLAVE_GENERICA
    : CLAVES_DE_CAUSA[props.error.statusCode] ?? CLAVE_GENERICA,
)

function volverAlIndice(): void {
  clearError({ redirect: RUTA_INDICE })
}
</script>

<template>
  <div class="flex min-h-screen flex-col bg-ground font-sans text-corriente-pleno">
    <!--
      The error screen renders outside every layout, so it mounts the product
      header itself. Without it the reader lands here with no way back to the
      index and no way to change the interface language.
    -->
    <CabeceraProducto />

    <!--
      `max-w-none` for the same reason as in the three layouts: `FranjaAlcance`
      renders a `<p>` and the system caps prose at `--medida-maxima` (68ch),
      which left the notice 455 px wide. This screen is not a layout, so it does
      not inherit the fix and has to repeat it. The error state is one of the
      four the prototype declares, and it is the one where a notice that reads
      as a stray card is least affordable.
    -->
    <FranjaAlcance class="max-w-none" />

    <main class="mx-auto flex w-full max-w-2xl flex-1 flex-col gap-4 px-6 py-12">
      <p class="text-sm text-corriente-tenue">
        {{ t('error.code', { code: error.statusCode }) }}
      </p>
      <h1 class="font-display text-2xl text-corriente-medio">
        {{ t('error.title') }}
      </h1>
      <p class="text-corriente-pleno">
        {{ t(claveDeCausa) }}
      </p>
      <p class="text-sm text-corriente-tenue">
        {{ t('error.hint') }}
      </p>
      <div>
        <button
          type="button"
          data-volver-al-indice
          class="rounded-md bg-info px-4 py-2 text-ground hover:bg-corriente-medio"
          :class="ANILLO_FOCO"
          @click="volverAlIndice"
        >
          {{ t('error.action.backToIndex') }}
        </button>
      </div>
    </main>
  </div>
</template>
