<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import CabeceraPantalla from '~/components/comun/CabeceraPantalla.vue'
import EstadoPendiente from '~/components/comun/EstadoPendiente.vue'
import { useTituloDeRuta } from '~/composables/useTituloDeRuta'

definePageMeta({ layout: 'portal' })

const { t } = useI18n()
const { titulo, ruta } = useTituloDeRuta()

/**
 * What this screen will hold, and the User Story that delivers it.
 *
 * Declared rather than implied: a title over an empty page reads as a screen
 * that failed to load, which is the one reading the deliverable cannot afford.
 */
const CAPACIDADES = computed(() =>
  (['dictionary', 'lineage', 'owner', 'quality'] as const).map(clave => t(`screen.governance.capability.${clave}`)),
)
</script>

<template>
  <section :data-ruta="ruta" class="flex flex-col gap-8">
    <CabeceraPantalla :titulo="titulo" :descripcion="t('screen.governance.description')" />
    <EstadoPendiente :capacidades="CAPACIDADES" us="US-029" />
  </section>
</template>
