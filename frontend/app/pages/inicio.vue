<script setup lang="ts">
/**
 * Home screen: one route, three compositions chosen by role.
 *
 * The page is a selector and nothing else. It keeps the three things the
 * navigation contract owns -the route attribute, the single heading taken from
 * the A3 branch and the summary paragraph- and mounts one of the three sibling
 * compositions underneath.
 *
 * It is deliberately ONE route and not three. Splitting it into
 * `/inicio/operativo` and company would add screens the site map does not have,
 * and the workspace is a property of who is asking, not of the address.
 *
 * There is no `fetch` here and there is no SWR rule either: the screen depends
 * on the reader, so a cached response would serve one role's home to another.
 */
import type { ClaveComposicion } from '~/types/espacios'
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import CabeceraPantalla from '~/components/comun/CabeceraPantalla.vue'
import EspacioAnalista from '~/components/inicio/EspacioAnalista.vue'
import EspacioDirectivo from '~/components/inicio/EspacioDirectivo.vue'
import EspacioOperativo from '~/components/inicio/EspacioOperativo.vue'
import { useEspacioTrabajo } from '~/composables/useEspacioTrabajo'
import { useTituloDeRuta } from '~/composables/useTituloDeRuta'

definePageMeta({ layout: 'portal' })

const { t } = useI18n()
const { titulo, ruta } = useTituloDeRuta()
const { espacio, cargando, nombre, rol } = useEspacioTrabajo()

/** The three compositions, resolved by the key the workspace contract carries. */
const COMPOSICIONES = {
  operativo: EspacioOperativo,
  analista: EspacioAnalista,
  directivo: EspacioDirectivo,
} as const satisfies Record<ClaveComposicion, unknown>

const composicion = computed(() => COMPOSICIONES[espacio.value.composicion])
</script>

<template>
  <section :data-ruta="ruta" class="flex flex-col gap-8">
    <CabeceraPantalla :titulo="titulo" :descripcion="t('screen.home.description')" />

    <component
      :is="composicion"
      :cargando="cargando"
      :nombre="nombre"
      :rol="rol"
    />
  </section>
</template>
