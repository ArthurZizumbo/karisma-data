<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { useTituloDeRuta } from '~/composables/useTituloDeRuta'

definePageMeta({ layout: 'portal' })

const { t } = useI18n()
const { titulo, ruta } = useTituloDeRuta()
</script>

<template>
  <section :data-ruta="ruta" class="flex flex-col gap-2">
    <h1 class="font-display text-2xl text-primary-dark">
      {{ titulo }}
    </h1>
    <p class="max-w-prose text-muted">
      {{ t('screen.administration.description') }}
    </p>
  </section>
</template>
