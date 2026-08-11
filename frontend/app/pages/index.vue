<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import BotonPrototipo from '~/components/nav/BotonPrototipo.vue'
import { ANILLO_FOCO } from '~/utils/foco'
import { PROTOTIPOS, RUTA_GUIA, RUTA_INDICE } from '~/utils/navegacion'

const { t } = useI18n()
</script>

<template>
  <section :data-ruta="RUTA_INDICE" class="flex flex-col gap-6">
    <header class="flex flex-col gap-2">
      <h1 class="font-display text-titulo-1 text-corriente-pleno">
        {{ t('screen.index.title') }}
      </h1>
      <p class="max-w-prose text-muted">
        {{ t('screen.index.subtitle') }}
      </p>
    </header>

    <ul class="grid gap-[var(--grid-gap)] sm:grid-cols-2 xl:grid-cols-3">
      <li v-for="prototipo in PROTOTIPOS" :key="prototipo.numero">
        <BotonPrototipo :prototipo="prototipo" />
      </li>
    </ul>

    <!--
      Separate block on purpose. The A4 rubric scores prototypes in one section
      and the style guide in another, so the guide is not an eighth numbered
      button: it is the system the seven above are built with, and it carries no
      data-prototipo attribute.
    -->
    <aside
      data-guia
      class="flex flex-col gap-2 rounded-lg border border-t-4 border-line border-t-accent-700 bg-surface-alt p-[var(--card-padding)]"
    >
      <h2 class="font-display text-titulo-2 text-primary-dark">
        {{ t('guide.entry.heading') }}
      </h2>
      <p class="max-w-prose text-cuerpo text-ink">
        {{ t('guide.entry.description') }}
      </p>
      <NuxtLink
        :to="RUTA_GUIA"
        class="inline-flex min-h-11 w-fit items-center rounded-md border border-primary bg-surface px-4 text-cuerpo text-primary hover:bg-primary-100"
        :class="ANILLO_FOCO"
      >
        {{ t('guide.entry.action') }}
      </NuxtLink>
    </aside>
  </section>
</template>
