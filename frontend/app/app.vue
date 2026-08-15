<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { useIdioma } from '~/composables/useIdioma'
import { useTema } from '~/composables/useTema'
import { useSistemaDiseno } from '~/stores/sistemaDiseno'

const { locale } = useI18n()

// The document language is what tells a screen reader which voice to use. It is
// declared before the await so the head entry is registered while the Nuxt
// context is still active.
useHead({ htmlAttrs: { lang: locale } })

// The theme is applied here, before the first render, for the same reason the
// language is: `useTema` declares `data-tema` through useHead, so the server
// emits it with the first byte. Applied after mount it would paint one theme
// and swap to the other in front of the reader.
useTema()

// The store is instantiated HERE and not wherever it happens to be read first,
// and that is not tidiness. `useModo` declares `data-modo` through useHead from
// inside the store setup, and a head entry belongs to the component instance
// that was active when it was registered. Left to the first reader, that owner
// is a control inside a layout: entering through the demonstration door swaps
// the `acceso` layout for `portal`, the owner unmounts, the entry is disposed
// and the attribute vanishes -the reader who chose dark lands on a light page
// while the selector still says dark, until a reload puts it back. Registering
// it on the chassis, which never unmounts, gives the mode the same lifetime the
// theme already has one line above.
useSistemaDiseno()

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
