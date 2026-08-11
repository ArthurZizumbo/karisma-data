<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { GRUPOS_DE_ICONOS, TAMANOS_DE_ICONO } from '~/components/guia/inventarioIconos'

/**
 * Icon plate of the living design system.
 *
 * The plate walks the very inventory that nuxt.config.ts hands to
 * `icon.clientBundle.icons`. Reading the list from anywhere else would let the
 * bundle and the plate drift, and the drift only shows up in a production
 * build: `nuxt dev` still resolves an unbundled icon through the Iconify API,
 * so the hole appears in the deployed capture and nowhere before it.
 *
 * Every icon carries its own accessible name, size included, because the three
 * sizes stand next to each other and a lone name repeated three times tells a
 * screen reader nothing about which one is which.
 */
defineOptions({ name: 'LaminaIconos' })

const { t } = useI18n()
</script>

<template>
  <section
    data-lamina="iconos"
    class="flex flex-col gap-4 rounded-lg border border-line bg-surface p-[var(--card-padding)] shadow-reposo"
  >
    <header class="flex flex-col gap-1">
      <h2 class="font-display text-titulo-2 text-primary-dark">
        {{ t('guide.plate.icons') }}
      </h2>
      <p class="max-w-prose text-cuerpo text-muted">
        {{ t('guide.icons.description') }}
      </p>
      <p class="max-w-prose text-cuerpo text-muted">
        {{ t('guide.icons.family') }}
      </p>
      <p class="max-w-prose text-cuerpo text-muted">
        {{ t('guide.icons.sizes') }}
      </p>
    </header>

    <div v-for="grupo in GRUPOS_DE_ICONOS" :key="grupo.clave" class="flex flex-col gap-2">
      <h3 class="font-display text-titulo-3 text-ink">
        {{ t(grupo.clave) }}
      </h3>
      <ul class="grid gap-[var(--grid-gap)] sm:grid-cols-3 lg:grid-cols-5">
        <li
          v-for="entrada in grupo.entradas"
          :key="entrada.nombre"
          class="flex flex-col items-center gap-1 rounded-md border border-line-strong bg-surface-alt p-2 text-center"
        >
          <span class="flex items-end gap-3">
            <Icon
              v-for="tamano in TAMANOS_DE_ICONO"
              :key="tamano.px"
              :name="entrada.nombre"
              :data-icono="entrada.nombre"
              role="img"
              :aria-label="t('guide.icons.label', { name: t(entrada.clave), size: tamano.px })"
              :class="tamano.clase"
              class="shrink-0 text-ink"
            />
          </span>
          <span aria-hidden="true" class="text-cuerpo text-ink">{{ t(entrada.clave) }}</span>
          <span aria-hidden="true" class="text-micro text-ink">{{ entrada.nombre }}</span>
        </li>
      </ul>
    </div>
  </section>
</template>
