<script setup lang="ts">
/**
 * Where the result set goes next: the sibling branches of module 2.
 *
 * The catalogue itself demands no scope -`GET /api/catalog/search` is open to
 * every authenticated reader- but its continuations do not: exports and
 * dashboards are branches 2.3 and 2.4 and both demand `analista`. Until now
 * the sidebar simply hid them, so a reader on the operations profile saw a
 * catalogue with no way forward and no reason given.
 *
 * The refused destinations are NOT rendered disabled: offering a door that
 * answers with a closed door is the defect US-027 identified. They are named,
 * with the profile they ask for and with the one sentence US-017 already wrote
 * for requesting access, so no second wording of the same refusal enters the
 * catalogues.
 *
 * The full screen `comun/EstadoSinPermiso.vue` is deliberately not mounted
 * here: it owns the `h1` of the screen it replaces, and this is a zone of a
 * screen that the reader may otherwise use in full. Two first level headings
 * would be the price of reusing the markup, so what is reused is the copy.
 *
 * Nothing is compared here either. The destinations arrive from the navigation
 * contract and the scopes from the generated map, through `usePermisos`.
 */
import type { SubrutaNav } from '~/types/navegacion'
import type { RolUsuario } from '~/types/sesion'
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { usePermisos } from '~/composables/usePermisos'
import { ANILLO_FOCO } from '~/utils/foco'

const props = defineProps<{
  /** Sibling branches of the active module, taken from the A3 map. */
  subrutas: readonly SubrutaNav[]
}>()

const { t } = useI18n()
const { puedeVerRuta, scopeExigidoPor } = usePermisos()

const permitidas = computed<readonly SubrutaNav[]>(() =>
  props.subrutas.filter(subruta => puedeVerRuta(subruta.ruta)),
)

const bloqueadas = computed<readonly SubrutaNav[]>(() =>
  props.subrutas.filter(subruta => !puedeVerRuta(subruta.ruta)),
)

/**
 * Profile the refused destinations ask for, read from the generated map.
 *
 * Null when none of the refused destinations declares a scope. With today's
 * contract that does not happen: `scopeExigidoPor` reads `SCOPE_POR_RUTA`
 * regardless of the session, and both continuations of module 2 demand
 * `analista`. The branch stays because the map is generated and a future route
 * may join `bloqueadas` without a scope of its own, and naming a profile that
 * nobody asked for would misdescribe the refusal.
 */
const perfilFaltante = computed<RolUsuario | null>(() => {
  for (const subruta of bloqueadas.value) {
    const scope = scopeExigidoPor(subruta.ruta)
    if (scope !== null) {
      return scope
    }
  }
  return null
})
</script>

<template>
  <section data-acciones-catalogo class="flex flex-col gap-2 border-l-2 border-grid pl-5">
    <h2 class="flex items-center gap-2 text-titulo-3 text-corriente-pleno">
      <Icon name="lucide:corner-down-right" class="size-4 shrink-0 text-corriente-tenue" aria-hidden="true" />
      {{ t('catalog.explore.actions.title') }}
    </h2>

    <p class="text-cuerpo text-corriente-medio">
      {{ t('catalog.explore.actions.hint') }}
    </p>

    <ul v-if="permitidas.length > 0" class="flex flex-wrap gap-2">
      <li v-for="subruta in permitidas" :key="subruta.id">
        <NuxtLink
          :to="subruta.ruta"
          :data-continuacion="subruta.id"
          class="inline-flex min-h-11 w-fit items-center gap-2 rounded-md border border-corriente-medio px-3 text-etiqueta text-corriente-pleno hover:bg-corriente-pleno hover:text-ground"
          :class="ANILLO_FOCO"
        >
          {{ t(subruta.claveEtiqueta) }}
        </NuxtLink>
      </li>
    </ul>

    <div v-if="bloqueadas.length > 0" data-estado="sin-permiso" class="flex flex-col gap-1">
      <ul class="ml-1 flex flex-col border-l border-corriente-apagado">
        <li
          v-for="subruta in bloqueadas"
          :key="subruta.id"
          :data-bloqueada="subruta.id"
          class="relative py-1 pl-4 text-cuerpo text-corriente-tenue"
        >
          <span class="absolute left-0 top-1/2 h-px w-2.5 bg-corriente-apagado" aria-hidden="true" />
          {{ t(subruta.claveEtiqueta) }}
        </li>
      </ul>

      <p v-if="perfilFaltante !== null" data-perfil-faltante class="text-micro text-corriente-tenue">
        {{ t('catalog.explore.actions.locked', { profile: t(`authz.role.${perfilFaltante}`) }) }}
      </p>

      <p class="text-micro text-corriente-tenue">
        {{ t('authz.noPermission.requestTo') }}
      </p>
    </div>
  </section>
</template>
