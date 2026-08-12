<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import CabeceraPantalla from '~/components/comun/CabeceraPantalla.vue'
import { useTituloDeRuta } from '~/composables/useTituloDeRuta'
import { ALTO_GRAFICA } from '~/utils/opcionSerie'

definePageMeta({ layout: 'portal' })

const { t } = useI18n()
const { titulo, ruta } = useTituloDeRuta()

/**
 * Dashboards screen, zone C of the A3 map.
 *
 * The four properties `test/pantallas.spec.ts` measures on every contract route
 * are preserved deliberately, and that file is not opened by this User Story: a
 * single `data-ruta` root, the declared layout, one `h1` taken from the A3
 * branch, and a first `<p>` that is the bilingual description of the screen.
 *
 * The panel enters under `ClientOnly` for two independent reasons. The chart
 * cannot render on the server -there is no canvas- and its payload is an
 * `ArrayBuffer` that would have to be inflated to base64 to survive the SSR
 * response. The fallback is the very same skeleton the panel uses while it
 * loads, with the very same reserved height, so hydration does not move a single
 * pixel of the page.
 *
 * US-026 inserts its predictive cards ahead of the panel, in its own commit. The
 * three conditions it has to preserve are the ones above plus the presence of
 * `[data-zona="serie"]`.
 */
</script>

<template>
  <section :data-ruta="ruta" class="flex flex-col gap-8">
    <CabeceraPantalla :titulo="titulo" :descripcion="t('screen.dashboards.description')" />

    <ClientOnly>
      <LazySeriePanel />
      <template #fallback>
        <SerieEstado estado="cargando" :alto="ALTO_GRAFICA" />
      </template>
    </ClientOnly>
  </section>
</template>
