<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import {
  FACETAS_TRANSVERSALES,
  MODULOS,
  RUTA_ASISTENTE,
  RUTA_INDICE,
  moduloActivo,
} from '~/utils/navegacion'

const route = useRoute()

/**
 * Active module is derived from the route on every render. Keeping it as local
 * state would desynchronise the sidebar from the browser back button.
 */
const moduloDesplegado = computed(() => moduloActivo(route.path))

/**
 * Exactly one entry may carry aria-current. A sub branch that still lives inside
 * its module landing screen shares that route, so the module link wins.
 */
function esActivo(ruta: string, rutaDelModulo?: string): boolean {
  if (rutaDelModulo !== undefined && ruta === rutaDelModulo) {
    return false
  }
  return route.path === ruta
}
</script>

<template>
  <aside
    class="sticky top-0 flex h-screen w-[var(--sidebar-width)] shrink-0 flex-col gap-4 overflow-y-auto border-r border-line bg-primary-dark px-3 py-4 text-surface"
  >
    <NuxtLink
      :to="RUTA_INDICE"
      class="font-display text-lg text-surface underline-offset-4 hover:underline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-secondary-soft"
    >
      Karisma Data
    </NuxtLink>

    <nav aria-label="Navegación principal">
      <ul class="flex flex-col gap-1">
        <li
          v-for="modulo in MODULOS"
          :key="modulo.id"
          :data-modulo-item="modulo.id"
        >
          <NuxtLink
            :id="`modulo-${modulo.id}`"
            :to="modulo.ruta"
            :aria-current="esActivo(modulo.ruta) ? 'page' : undefined"
            :aria-expanded="moduloDesplegado?.id === modulo.id"
            class="block rounded-md px-3 py-2 text-sm hover:bg-primary focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-secondary-soft aria-[current=page]:bg-primary aria-[current=page]:font-medium"
          >
            {{ modulo.id }}. {{ modulo.etiqueta }}
          </NuxtLink>

          <ul
            v-if="moduloDesplegado?.id === modulo.id"
            data-nivel="2"
            :data-modulo="modulo.id"
            :aria-labelledby="`modulo-${modulo.id}`"
            class="mt-1 flex flex-col gap-0.5 border-l border-secondary-soft pl-3 ml-3"
          >
            <li v-for="subruta in modulo.subrutas" :key="subruta.id">
              <NuxtLink
                :to="subruta.ruta"
                :title="subruta.facetaTransversal
                  ? `${subruta.etiqueta}: faceta transversal, alcanzable desde más de una rama`
                  : undefined"
                :aria-label="subruta.facetaTransversal
                  ? `${subruta.id} ${subruta.etiqueta}, faceta transversal`
                  : undefined"
                :aria-current="esActivo(subruta.ruta, modulo.ruta) ? 'page' : undefined"
                class="flex items-center gap-2 rounded-sm px-2 py-1 text-sm text-secondary-soft hover:bg-primary hover:text-surface focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-secondary-soft aria-[current=page]:bg-primary aria-[current=page]:text-surface"
              >
                <Icon
                  v-if="subruta.facetaTransversal"
                  name="lucide:circle-dot"
                  class="size-3 shrink-0"
                  aria-hidden="true"
                />
                <span>{{ subruta.id }} {{ subruta.etiqueta }}</span>
              </NuxtLink>
            </li>
          </ul>
        </li>
      </ul>
    </nav>

    <hr class="border-t border-secondary-soft opacity-40">

    <nav aria-label="Acceso transversal" class="flex flex-col gap-2">
      <NuxtLink
        :to="RUTA_ASISTENTE"
        :aria-current="esActivo(RUTA_ASISTENTE) ? 'page' : undefined"
        class="block rounded-md px-3 py-2 text-sm hover:bg-primary focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-secondary-soft aria-[current=page]:bg-primary aria-[current=page]:font-medium"
      >
        Asistente conversacional
      </NuxtLink>
      <p class="px-3 text-sm text-secondary-soft">
        Transversal a las cuatro categorías.
      </p>
    </nav>

    <section class="mt-auto flex flex-col gap-1" aria-labelledby="facetas-transversales">
      <!--
        This used to be an <h2> and, since the sidebar comes before <main>, it
        became the FIRST heading of the document: the hierarchy started at h2
        and the <h1> of the screen appeared afterwards. It is downgraded to a
        <p>, which still names the list through aria-labelledby without
        entering the heading tree.
      -->
      <p id="facetas-transversales" class="px-3 text-sm text-secondary-soft">
        Facetas transversales
      </p>
      <ul class="flex flex-wrap gap-1 px-3">
        <li
          v-for="faceta in FACETAS_TRANSVERSALES"
          :key="faceta"
          :title="`${faceta}: se alcanza desde más de una rama del mapa`"
          class="rounded-sm border border-secondary-soft px-2 py-0.5 text-sm text-secondary-soft"
        >
          {{ faceta }}
        </li>
      </ul>
    </section>
  </aside>
</template>
