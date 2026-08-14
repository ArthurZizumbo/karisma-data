<script setup lang="ts">
/*
 * The band is a declaration, not a control.
 *
 * It used to be `sticky top-0`, and so is the guide's plate navigation: two
 * elements competing for the same slot left the navigation 19 pixels down and
 * its current-plate mark one plate behind. Being permanent is a requirement of
 * the prototype; following the scroll never was.
 */
import { useI18n } from 'vue-i18n'
import { CLAVE_AVISO_ALCANCE } from '~/utils/navegacion'

const { t } = useI18n()
</script>

<template>
  <p
    data-franja-alcance
    role="note"
    :aria-label="t('scope.ariaLabel')"
    class="shrink-0 border-b border-grid bg-ground-alt px-4 py-2 text-etiqueta text-corriente-medio md:px-8"
  >
    {{ t(CLAVE_AVISO_ALCANCE) }}
  </p>
</template>
