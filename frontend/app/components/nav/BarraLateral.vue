<script setup lang="ts">
/**
 * Navigation of the portal, with a text label on every entry.
 *
 * Two things changed with the second theme. The bar has a surface of its own
 * again -`--color-barra-lateral`, navy under the institutional theme and an
 * alternate ground under the default one- and the module in use is marked with
 * `--color-barra-lateral-activo`, which under the default theme is that same
 * ground: there the current module is told apart by luminance and weight, as
 * the captured plates show, and under the institutional theme it fills with
 * the action colour. The component carries no condition on the theme; the four
 * tokens do the work.
 *
 * The nine "cross cutting facets" are gone. They were the A3 card sorting
 * rendered as navigation -nine `listitem` with no link, at the bottom of the
 * bar- and they made a promise no click could keep. Their content is published
 * as a map in the deliverable, which is where the traceability belongs.
 *
 * The product name is not repeated here: the header names it once, above the
 * whole chassis.
 *
 * Below the small breakpoint the bar collapses to a strip of icons, which is
 * what the design system declares at 768 px and what keeps a 232 px bar from
 * eating a 390 px viewport.
 */
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute } from 'vue-router'
import { usePermisos } from '~/composables/usePermisos'
import { ANILLO_FOCO } from '~/utils/foco'
import { RUTA_ACCESO, RUTA_ASISTENTE, moduloActivo } from '~/utils/navegacion'

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

/** Shared by every first level entry, so the active state cannot drift apart. */
const CLASE_ENTRADA
  = 'flex min-h-11 items-center gap-2 rounded-md px-2 text-cuerpo text-barra-lateral-texto '
    + 'hover:text-barra-lateral-activo-texto aria-[current=page]:bg-barra-lateral-activo '
    + 'aria-[current=page]:font-semibold aria-[current=page]:text-barra-lateral-activo-texto'

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
    class="sticky top-0 flex h-screen w-(--sidebar-collapsed) shrink-0 flex-col gap-6 overflow-y-auto overflow-x-hidden border-r border-grid bg-barra-lateral px-2 py-4 md:w-(--sidebar-width) md:px-3"
  >
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
      <p class="max-w-none text-micro text-barra-lateral-texto">
        {{ t('nav.session.anonymous') }}
      </p>
      <NuxtLink
        :to="RUTA_ACCESO"
        class="inline-flex min-h-11 w-fit items-center gap-2 rounded-md border border-barra-lateral-texto px-2 text-etiqueta text-barra-lateral-texto hover:bg-barra-lateral-activo hover:text-barra-lateral-activo-texto"
        :class="ANILLO_FOCO"
      >
        <Icon name="lucide:log-in" class="size-4 shrink-0" aria-hidden="true" />
        {{ t('nav.session.signIn') }}
      </NuxtLink>
    </nav>

    <p
      v-else
      data-perfil-activo
      class="hidden max-w-none px-2 text-micro uppercase tracking-wide text-barra-lateral-texto md:block"
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
            :class="[CLASE_ENTRADA, ANILLO_FOCO]"
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
            class="ml-4 hidden flex-col border-l border-barra-lateral-texto/40 md:flex"
          >
            <li v-for="subruta in modulo.subrutas" :key="subruta.id" class="relative pl-3">
              <span
                class="absolute left-0 top-1/2 h-px w-2.5 bg-barra-lateral-texto/40"
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
                class="flex min-h-9 items-center gap-2 rounded-sm px-2 text-etiqueta text-barra-lateral-texto hover:text-barra-lateral-activo-texto aria-[current=page]:font-semibold aria-[current=page]:text-barra-lateral-activo-texto"
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
      class="mt-auto flex flex-col gap-1"
    >
      <NuxtLink
        :to="RUTA_ASISTENTE"
        :title="t('nav.assistant.label')"
        :aria-current="esActivo(RUTA_ASISTENTE) ? 'page' : undefined"
        :class="[CLASE_ENTRADA, ANILLO_FOCO]"
      >
        <Icon name="lucide:message-square" class="size-4 shrink-0" aria-hidden="true" />
        <span class="hidden md:inline">{{ t('nav.assistant.label') }}</span>
      </NuxtLink>
      <p class="hidden max-w-none px-2 text-micro text-barra-lateral-texto md:block">
        {{ t('nav.assistant.note') }}
      </p>
    </nav>
  </aside>
</template>
