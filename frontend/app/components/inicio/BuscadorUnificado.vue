<script setup lang="ts">
/**
 * Unified search of the home screen, in the three sizes the workspaces need.
 *
 * One component and not three: what changes between an operative reader and an
 * executive one is how much room the box takes and whether it is the primary
 * action of the screen, not what it does. `enfasis` is the whole difference,
 * and it is published as `data-enfasis` because the acceptance criterion is
 * literally about the weight the box carries in each composition.
 *
 * The empty term is refused on purpose. Submitting nothing would navigate to a
 * results screen with no query, which reads as a product that lost the search
 * the reader just typed.
 */
import type { EnfasisBuscador } from '~/types/espacios'
import { computed, ref, useId } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { ANILLO_FOCO } from '~/utils/foco'
import { PARAMETRO_BUSQUEDA, RUTA_EXPLORACION } from '~/utils/espaciosTrabajo'

const props = defineProps<{
  /** How much room the box takes in the composition that holds it. */
  enfasis: EnfasisBuscador
}>()

const { t } = useI18n()
const router = useRouter()

const idTitulo = useId()
const idCampo = useId()
const termino = ref('')

const hayTermino = computed(() => termino.value.trim() !== '')

/** Only the dominant box is the primary action of its screen. */
const esDominante = computed(() => props.enfasis === 'dominante')

/** The reduced box is a single line: no heading on screen and no hint. */
const esReducido = computed(() => props.enfasis === 'reducido')

const claseTitulo = computed(() =>
  esReducido.value
    ? 'sr-only'
    : esDominante.value
      ? 'text-titulo-2 font-display text-corriente-pleno'
      : 'text-titulo-3 text-corriente-pleno',
)

const claseCampo = computed(() =>
  esDominante.value
    ? 'min-h-13 text-cuerpo-amplio'
    : 'min-h-11 text-cuerpo',
)

const claseAccion = computed(() =>
  esDominante.value
    ? 'bg-corriente-pleno text-ground hover:bg-corriente-medio disabled:bg-corriente-apagado'
    : 'border border-corriente-medio text-corriente-pleno hover:bg-ground-alt disabled:border-grid disabled:text-corriente-apagado',
)

/**
 * Sends the term to the exploration screen.
 *
 * The results are not duplicated here: a second surface of results would have
 * to be designed, tested and captured twice, and the site map already gives
 * them a branch of their own.
 */
function buscar(): void {
  const consulta = termino.value.trim()
  if (consulta === '') {
    return
  }
  void router.push({ path: RUTA_EXPLORACION, query: { [PARAMETRO_BUSQUEDA]: consulta } })
}
</script>

<template>
  <section
    data-bloque="buscador"
    :data-enfasis="enfasis"
    :aria-labelledby="idTitulo"
    class="flex flex-col gap-2"
    :class="esDominante ? 'border border-grid bg-ground-alt p-(--panel-padding)' : ''"
  >
    <h2 :id="idTitulo" :class="claseTitulo">
      {{ t('workspace.search.label') }}
    </h2>

    <form class="flex flex-wrap items-stretch gap-2" @submit.prevent="buscar">
      <div class="relative flex min-w-64 flex-1 items-center">
        <Icon
          name="lucide:search"
          class="pointer-events-none absolute left-3 size-4 shrink-0 text-corriente-tenue"
          aria-hidden="true"
        />
        <input
          :id="idCampo"
          v-model="termino"
          data-campo-busqueda
          type="search"
          :aria-labelledby="idTitulo"
          :placeholder="t('workspace.search.placeholder')"
          class="w-full border border-corriente-medio bg-ground pl-9 pr-3 text-corriente-pleno placeholder:text-corriente-tenue"
          :class="[claseCampo, ANILLO_FOCO]"
        >
      </div>

      <button
        data-accion-busqueda
        type="submit"
        :disabled="!hayTermino"
        class="flex min-h-11 items-center px-4 text-etiqueta"
        :class="[claseAccion, ANILLO_FOCO]"
      >
        {{ t('workspace.search.action') }}
      </button>
    </form>

    <p v-if="!esReducido" class="max-w-(--medida-maxima) text-micro text-corriente-tenue">
      {{ t('workspace.search.hint') }}
    </p>
  </section>
</template>
