<script setup lang="ts">
import { AVISO_ALCANCE } from '~/utils/navegacion'
</script>

<template>
  <p
    data-franja-alcance
    role="note"
    aria-label="Aviso de alcance del prototipo"
    class="sticky top-0 z-10 shrink-0 border-b border-line bg-secondary-soft px-6 py-2 text-sm text-ink"
  >
    {{ AVISO_ALCANCE }}
  </p>
</template>
