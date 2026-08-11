<script setup lang="ts">
/**
 * Type plate: each role is shown at its real size, weight and leading.
 *
 * The previous scale had nine roles and one weight. The rendered page measured
 * 750 of 750 text nodes at weight 400, headings included, and a title to body
 * ratio of 1.71: with size as the only channel and steps of 1.2, no jump read
 * as a jump. Weight is a channel now, and the specimen prints it so the
 * difference is visible rather than claimed.
 */
import { useI18n } from 'vue-i18n'
import { useSistemaDiseno } from '~/stores/sistemaDiseno'

const { t } = useI18n()
const sistema = useSistemaDiseno()

/** The sample sentence carries ascenders, descenders and figures. */
const MUESTRA = 'Saldo de cartera vigente 1,284,596.30'
</script>

<template>
  <section data-lamina="tipografia" class="flex flex-col gap-6">
    <h2 class="text-titulo-2 text-corriente-pleno">
      {{ t('guide.type.title') }}
    </h2>

    <ul class="flex flex-col divide-y divide-grid">
      <li
        v-for="rol in sistema.tipografia"
        :key="rol.nombre"
        data-rol
        class="flex flex-col gap-1 py-4 md:flex-row md:items-baseline md:gap-6"
      >
        <!-- The specimen first and at full size; the metadata is the caption. -->
        <p
          class="min-w-0 flex-1 truncate text-corriente-pleno"
          :style="{
            fontSize: `${rol.tamanoPx}px`,
            lineHeight: `${rol.interlineaPx}px`,
            fontWeight: rol.peso,
            fontFamily: `var(--font-${rol.familia})`,
          }"
        >
          {{ MUESTRA }}
        </p>
        <dl class="flex shrink-0 gap-4 font-mono text-micro text-corriente-tenue">
          <div>
            <dt class="sr-only">{{ t('guide.type.role') }}</dt>
            <dd class="text-corriente-medio">{{ rol.nombre }}</dd>
          </div>
          <div>
            <dt class="sr-only">{{ t('guide.type.size') }}</dt>
            <dd>{{ rol.tamanoPx }}/{{ rol.interlineaPx }}</dd>
          </div>
          <div>
            <dt class="sr-only">{{ t('guide.type.weight') }}</dt>
            <dd>{{ rol.peso }}</dd>
          </div>
        </dl>
      </li>
    </ul>

    <details class="border-t border-grid pt-3">
      <summary class="cursor-pointer text-etiqueta text-corriente-tenue">
        {{ t('guide.type.why') }}
      </summary>
      <p class="mt-2 max-w-(--medida-maxima) text-cuerpo text-corriente-medio">
        {{ t('guide.type.rationale') }}
      </p>
    </details>
  </section>
</template>
