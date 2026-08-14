<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import EstadoSinPermiso from '~/components/comun/EstadoSinPermiso.vue'
import CabeceraProducto from '~/components/comun/CabeceraProducto.vue'
import BarraLateral from '~/components/nav/BarraLateral.vue'
import FranjaAlcance from '~/components/nav/FranjaAlcance.vue'
import { usePermisos } from '~/composables/usePermisos'

const { t } = useI18n()
const { bloqueo, rol } = usePermisos()

/**
 * The refusal is rendered here and not through `createError(403)`.
 *
 * `error.vue` is a global error screen with no sidebar: it would pull the
 * reader out of the portal to tell them a permission is missing, and its
 * "go back" action lands on the prototype index. Replacing the content of
 * `<main>` keeps the scope band -which the smoke greps on every route- and
 * keeps the navigation, which is the way out that is not a retry.
 */
const sinPermiso = computed(() =>
  bloqueo.value === null || rol.value === null
    ? null
    : { scopeExigido: bloqueo.value.scopeExigido, rolActual: rol.value },
)
</script>

<template>
  <div
    class="flex min-h-screen bg-ground font-sans text-corriente-pleno bg-[linear-gradient(to_right,var(--color-grid)_1px,transparent_1px),linear-gradient(to_bottom,var(--color-grid)_1px,transparent_1px)] bg-size-[24px_24px]"
  >
    <!--
      First focusable element of the document. Without it, a keyboard user walks
      through the ~20 sidebar links on EVERY one of the seven screens before
      reaching the content. It only becomes visible once it receives focus.
    -->
    <a
      href="#contenido"
      class="sr-only focus:not-sr-only focus:absolute focus:left-4 focus:top-4 focus:z-50 focus:rounded-md focus:bg-corriente-pleno focus:px-4 focus:py-2 focus:text-ground"
    >
      {{ t('chrome.skipToContent') }}
    </a>

    <BarraLateral />

    <div class="flex min-w-0 flex-1 flex-col">
      <!-- The sidebar already names the product, so the header does not. -->
      <CabeceraProducto :con-marca="false" />

      <!--
        `max-w-none` is what turns the notice back into a band.

        The design system caps prose at `--medida-maxima` (68ch) and
        `FranjaAlcance` renders a `<p>`, so the scope notice came out 455 px
        wide inside a 1208 px column: a card pinned to the top left corner
        instead of a declaration governing the screen. The system rule opts out
        of anything that already declares its own measure
        -`p:not([class*='max-w'])`-, so the class both stops the rule from
        matching and sets the value; neither depends on winning a specificity
        tie. The band is a system declaration, not running prose: its single
        sentence stays on one line and never sweeps the full column.
      -->
      <FranjaAlcance class="max-w-none" />

      <main id="contenido" class="flex-1 px-4 py-8 md:px-8">
        <!--
          The page is not mounted while the route is blocked: no useFetch of the
          refused screen ever fires against an endpoint that would answer 403.
        -->
        <EstadoSinPermiso
          v-if="sinPermiso"
          :scope-exigido="sinPermiso.scopeExigido"
          :rol-actual="sinPermiso.rolActual"
        />
        <slot v-else />
      </main>
    </div>
  </div>
</template>
