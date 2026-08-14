<script setup lang="ts">
/**
 * Navigation as a wiring diagram.
 *
 * The previous sidebar was a solid navy slab of 240 by 900 pixels: measured as
 * the highest-contrast element of the screen, it won the first read on every
 * captured plate, ahead of the screen title. It is now the same ground as the
 * page, separated by a rule rather than a fill, and the module a reader is on
 * is marked by current instead of by a coloured block.
 *
 * Below the small breakpoint it collapses to a strip of icons. The old one did
 * not: it kept 240 pixels of a 375 pixel viewport and left the content on 135,
 * with 112 pixels of horizontal overflow. The stylesheet declared the collapse
 * and nothing implemented it.
 */
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute } from 'vue-router'
import { usePermisos } from '~/composables/usePermisos'
import { ANILLO_FOCO } from '~/utils/foco'
import {
  CLAVES_FACETAS_TRANSVERSALES,
  RUTA_ACCESO,
  RUTA_ASISTENTE,
  RUTA_INDICE,
  moduloActivo,
} from '~/utils/navegacion'

const route = useRoute()
const { t } = useI18n()

/**
 * The sidebar does not know what a scope is.
 *
 * It receives the modules the reader may use, already filtered at both levels,
 * and paints them. Hiding is real removal from the DOM and not a `disabled`
 * attribute: a greyed out entry still advertises a door that answers 403, which
 * is the reading the criterion of this User Story rules out explicitly.
 */
const { modulosVisibles, asistenteVisible, rol } = usePermisos()

/** Icons are declared, never composed at runtime: the bundler scans literals. */
const ICONO_MODULO: Readonly<Record<string, string>> = {
  '1': 'lucide:house',
  '2': 'lucide:search',
  '3': 'lucide:shield-check',
  '4': 'lucide:settings',
}

const moduloDesplegado = computed(() => moduloActivo(route.path))

function esActivo(ruta: string, rutaDelModulo?: string): boolean {
  if (rutaDelModulo !== undefined && ruta === rutaDelModulo) {
    return false
  }
  return route.path === ruta
}
</script>

<template>
  <aside
    data-barra-lateral
    class="sticky top-0 flex h-screen w-(--sidebar-collapsed) shrink-0 flex-col gap-6 overflow-y-auto overflow-x-hidden border-r border-grid bg-ground px-2 py-4 md:w-(--sidebar-width) md:px-4"
  >
    <NuxtLink
      :to="RUTA_INDICE"
      class="flex items-center gap-2 text-titulo-3 text-corriente-pleno"
      :class="ANILLO_FOCO"
    >
      <Icon name="lucide:circuit-board" class="size-5 shrink-0 text-info" aria-hidden="true" />
      <span class="hidden md:inline">{{ t('brand.name') }}</span>
    </NuxtLink>

    <!--
      Fifth unhappy state, and it comes for free: '/guia' is public and uses this
      layout, so without it the style guide would be captured for A4 with an
      empty sidebar and no explanation. Showing the four modules instead would
      offer doors that close, which is the opposite of what this US is for.
    -->
    <nav
      v-if="rol === null"
      data-sesion-anonima
      :aria-label="t('nav.session.ariaLabel')"
      class="hidden flex-col gap-2 md:flex"
    >
      <p class="text-micro text-corriente-tenue">
        {{ t('nav.session.anonymous') }}
      </p>
      <NuxtLink
        :to="RUTA_ACCESO"
        class="inline-flex min-h-9 w-fit items-center gap-2 border border-corriente-medio px-2 text-etiqueta text-corriente-pleno hover:bg-corriente-pleno hover:text-ground"
        :class="ANILLO_FOCO"
      >
        <Icon name="lucide:log-in" class="size-4 shrink-0" aria-hidden="true" />
        {{ t('nav.session.signIn') }}
      </NuxtLink>
    </nav>

    <p
      v-else
      data-perfil-activo
      class="hidden px-2 text-micro uppercase tracking-wide text-corriente-tenue md:block"
    >
      {{ t('nav.session.profile', { role: t(`authz.role.${rol}`) }) }}
    </p>

    <nav v-if="rol !== null" :aria-label="t('nav.aria.main')">
      <ul class="flex flex-col gap-0.5">
        <li
          v-for="modulo in modulosVisibles"
          :key="modulo.id"
          :data-modulo-item="modulo.id"
        >
          <NuxtLink
            :id="`modulo-${modulo.id}`"
            :to="modulo.ruta"
            :title="t(modulo.claveEtiqueta)"
            :aria-current="esActivo(modulo.ruta) ? 'page' : undefined"
            :aria-expanded="moduloDesplegado?.id === modulo.id"
            class="flex items-center gap-2 rounded-md px-2 py-1.5 text-cuerpo text-corriente-tenue hover:text-corriente-pleno aria-[current=page]:font-semibold aria-[current=page]:text-corriente-pleno"
            :class="ANILLO_FOCO"
          >
            <Icon
              :name="ICONO_MODULO[modulo.id] ?? 'lucide:circle'"
              class="size-4 shrink-0"
              aria-hidden="true"
            />
            <span class="hidden md:inline">{{ t(modulo.claveEtiqueta) }}</span>
          </NuxtLink>

          <!--
            The branch list is the connector: a rule leaves the module and each
            branch taps off it. It is hidden on the icon strip, where there is no
            room for a second level and a tooltip already names the module.
          -->
          <ul
            v-if="moduloDesplegado?.id === modulo.id"
            data-nivel="2"
            :data-modulo="modulo.id"
            :aria-labelledby="`modulo-${modulo.id}`"
            class="ml-4 hidden flex-col border-l border-corriente-apagado md:flex"
          >
            <li v-for="subruta in modulo.subrutas" :key="subruta.id" class="relative pl-3">
              <span
                class="absolute left-0 top-1/2 h-px w-2.5 bg-corriente-apagado"
                aria-hidden="true"
              />
              <NuxtLink
                :to="subruta.ruta"
                :title="subruta.facetaTransversal
                  ? t('nav.facets.branchTitle', { label: t(subruta.claveEtiqueta) })
                  : undefined"
                :aria-label="subruta.facetaTransversal
                  ? t('nav.facets.branchAria', { id: subruta.id, label: t(subruta.claveEtiqueta) })
                  : undefined"
                :aria-current="esActivo(subruta.ruta, modulo.ruta) ? 'page' : undefined"
                class="flex items-center gap-2 rounded-sm px-2 py-1 text-etiqueta text-corriente-tenue hover:text-corriente-pleno aria-[current=page]:font-semibold aria-[current=page]:text-corriente-pleno"
                :class="ANILLO_FOCO"
              >
                <Icon
                  v-if="subruta.facetaTransversal"
                  name="lucide:git-branch"
                  class="size-3 shrink-0"
                  aria-hidden="true"
                />
                <span>{{ t(subruta.claveEtiqueta) }}</span>
              </NuxtLink>
            </li>
          </ul>
        </li>
      </ul>
    </nav>

    <nav
      v-if="asistenteVisible"
      :aria-label="t('nav.aria.crossCutting')"
      class="flex flex-col gap-1"
    >
      <NuxtLink
        :to="RUTA_ASISTENTE"
        :title="t('nav.assistant.label')"
        :aria-current="esActivo(RUTA_ASISTENTE) ? 'page' : undefined"
        class="flex items-center gap-2 rounded-md px-2 py-1.5 text-cuerpo text-corriente-tenue hover:text-corriente-pleno aria-[current=page]:font-semibold aria-[current=page]:text-corriente-pleno"
        :class="ANILLO_FOCO"
      >
        <Icon name="lucide:message-square" class="size-4 shrink-0" aria-hidden="true" />
        <span class="hidden md:inline">{{ t('nav.assistant.label') }}</span>
      </NuxtLink>
      <p class="hidden px-2 text-micro text-corriente-tenue md:block">
        {{ t('nav.assistant.note') }}
      </p>
    </nav>

    <!--
      The nine cross-cutting facets used to be nine bordered blocks stacked
      vertically, which read as broken buttons. They are a list of taps off a
      single rule now, and they disappear on the icon strip.
    -->
    <section
      v-if="rol !== null"
      class="mt-auto hidden flex-col gap-1 md:flex"
      aria-labelledby="facetas-transversales"
    >
      <p id="facetas-transversales" class="text-micro uppercase tracking-wide text-corriente-tenue">
        {{ t('nav.facets.caption') }}
      </p>
      <ul class="ml-1 flex flex-col border-l border-corriente-apagado">
        <li
          v-for="clave in CLAVES_FACETAS_TRANSVERSALES"
          :key="clave"
          :title="t('nav.facets.hint', { facet: t(clave) })"
          class="relative py-1 pl-4 text-micro text-corriente-tenue"
        >
          <span
            class="absolute left-0 top-1/2 h-px w-2.5 bg-corriente-apagado"
            aria-hidden="true"
          />
          {{ t(clave) }}
        </li>
      </ul>
    </section>
  </aside>
</template>
