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
  (['search', 'recent', 'favorites', 'alerts'] as const).map(clave => t(`screen.home.capability.${clave}`)),
)
</script>

<template>
  <section :data-ruta="ruta" class="flex flex-col gap-8">
    <CabeceraPantalla :titulo="titulo" :descripcion="t('screen.home.description')" />
    <EstadoPendiente :capacidades="CAPACIDADES" us="US-027" />
  </section>
</template>
