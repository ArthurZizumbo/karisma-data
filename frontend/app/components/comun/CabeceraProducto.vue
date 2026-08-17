<script setup lang="ts">
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute } from 'vue-router'
import MarcaKarisma from '~/components/comun/MarcaKarisma.vue'
import SelectorApariencia from '~/components/comun/SelectorApariencia.vue'
import SelectorIdioma from '~/components/comun/SelectorIdioma.vue'
import SelectorRol from '~/components/comun/SelectorRol.vue'
import { PARAMETRO_TERMINO } from '~/composables/useBusquedaCatalogo'
import { useRolDemo } from '~/composables/useRolDemo'
import { ANILLO_FOCO } from '~/utils/foco'
import { MODULOS, RUTA_INDICE } from '~/utils/navegacion'

/**
 * Product header shared by the four chromes of the prototype.
 *
 * The design review counted eleven interactive controls in this bar, none of
 * them with a label, and the mechanical pass found two defects on a 390 px
 * viewport: the profile switcher rendered at `left: -144.4` -outside the
 * canvas, on a bar that does not scroll- and several targets fell under 44 px.
 *
 * The bar now carries five slots and, at rest, six controls: the mark, the
 * search field, appearance, profile and the two buttons of the language pair.
 * The two groups that used to spill their options into the row -theme and
 * mode, five buttons; profile, four- are disclosures now, anchored to the end
 * edge of their own trigger so no panel can leave the canvas again.
 *
 * `flex-wrap` is the other half of that fix. A thin bar that refuses to wrap
 * either overflows the viewport or pushes a control out of it, and both are
 * measured defects of the previous version. On a narrow screen the row breaks
 * into two and nothing is lost.
 */

const { t } = useI18n()
const route = useRoute()
const entorno = useRuntimeConfig().public.entorno
const { rolActual, disponible: perfilDisponible } = useRolDemo()

/** Landing screen of the catalogue, taken from the navigation contract. */
const RUTA_CATALOGO = MODULOS.find(modulo => modulo.id === '2')!.ruta

/**
 * The term the chrome shows, seeded from the address.
 *
 * Reading it from the route is what keeps the field from being a hole: after
 * a search the address carries `?q=...`, the reader lands on the catalogue and
 * the bar still shows what they typed, on that screen and on every screen they
 * reach from it.
 */
const termino = ref<string>(
  typeof route.query[PARAMETRO_TERMINO] === 'string' ? route.query[PARAMETRO_TERMINO] : '',
)

const perfilAbierto = ref<boolean>(false)

/** Name of the open profile, or the explicit absence of one. */
const nombreDePerfil = computed<string>(() =>
  rolActual.value === null
    ? t('chrome.profile.signedOut')
    : t(`authz.role.${rolActual.value}`),
)

async function buscar(): Promise<void> {
  const limpio = termino.value.trim()
  await navigateTo({
    path: RUTA_CATALOGO,
    query: limpio === '' ? {} : { [PARAMETRO_TERMINO]: limpio },
  })
}
</script>

<template>
  <header
    data-cabecera-producto
    class="flex min-h-(--header-height) shrink-0 flex-wrap items-center gap-2 border-b border-grid bg-ground px-3 py-2 md:flex-nowrap md:gap-3 md:px-6 md:py-0"
  >
    <NuxtLink
      :to="RUTA_INDICE"
      data-marca-enlace
      class="flex min-h-11 items-center rounded-md text-corriente-pleno"
      :class="ANILLO_FOCO"
      :aria-label="t('brand.name')"
    >
      <MarcaKarisma con-nombre />
    </NuxtLink>

    <!--
      The search field is the one slot that grows. On a narrow screen it takes
      a line of its own -`order-last w-full`- instead of squeezing the controls
      out of the canvas, which is the defect this bar was measured for.
    -->
    <form
      role="search"
      data-buscador-cromo
      class="order-last w-full md:order-none md:w-auto md:max-w-72 md:flex-1"
      @submit.prevent="buscar"
    >
      <label class="flex min-h-11 items-center gap-2 rounded-md border border-corriente-apagado px-2">
        <Icon name="lucide:search" class="size-4 shrink-0 text-corriente-tenue" aria-hidden="true" />
        <span class="sr-only">{{ t('chrome.search.label') }}</span>
        <input
          v-model="termino"
          type="search"
          :name="PARAMETRO_TERMINO"
          :placeholder="t('chrome.search.placeholder')"
          class="min-h-11 w-full min-w-0 bg-transparent text-cuerpo text-corriente-pleno outline-none placeholder:text-corriente-tenue"
        >
      </label>
    </form>

    <div class="ms-auto flex items-center gap-2">
      <SelectorApariencia />

      <!--
        The profile only exists with the demonstration door open: the switch
        mints a real session against `POST /api/auth/demo`, and a deployment
        with the door closed answers 404. Behind a disclosure it costs the bar
        one control instead of four, and the panel is anchored to the end edge
        so it can no longer render outside the viewport.
      -->
      <div v-if="perfilDisponible" data-perfil-cromo class="relative">
        <button
          type="button"
          data-perfil-abrir
          :aria-expanded="perfilAbierto"
          aria-haspopup="true"
          :aria-label="t('chrome.profile.current', { profile: nombreDePerfil })"
          :title="t('chrome.profile.current', { profile: nombreDePerfil })"
          class="flex min-h-11 min-w-11 items-center gap-1.5 rounded-md border border-corriente-apagado px-2 text-etiqueta text-corriente-pleno hover:bg-corriente-apagado"
          :class="ANILLO_FOCO"
          @click="perfilAbierto = !perfilAbierto"
        >
          <Icon name="lucide:user-round-cog" class="size-4 shrink-0" aria-hidden="true" />
          <span class="hidden sm:inline">{{ nombreDePerfil }}</span>
        </button>

        <div
          v-if="perfilAbierto"
          data-perfil-panel
          class="absolute end-0 top-full z-40 mt-1 flex flex-col gap-2 rounded-lg border border-grid bg-ground p-3 shadow-menu"
        >
          <p class="max-w-none text-micro uppercase tracking-wide text-corriente-tenue">
            {{ t('chrome.profile.label') }}
          </p>
          <SelectorRol />
        </div>
      </div>

      <SelectorIdioma />

      <span
        class="hidden rounded-sm border border-corriente-apagado px-2 py-1 text-micro text-corriente-tenue lg:inline"
      >
        {{ t('chrome.environment', { environment: entorno }) }}
      </span>
    </div>
  </header>
</template>
