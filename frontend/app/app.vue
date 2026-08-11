<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { useIdioma } from '~/composables/useIdioma'

const { locale } = useI18n()

// The document language is what tells a screen reader which voice to use. It is
// declared before the await so the head entry is registered while the Nuxt
// context is still active.
useHead({ htmlAttrs: { lang: locale } })

const { restaurarIdiomaGuardado } = useIdioma()

// Awaited on purpose: app.vue renders inside the root Suspense boundary, so
// resolving the stored language here means the server already emits the right
// words and hydration finds the same text. Restoring it after mount would show
// a flash of Spanish to a reader who chose English.
await restaurarIdiomaGuardado()
</script>

<template>
  <NuxtLayout>
    <NuxtPage />
  </NuxtLayout>
</template>
