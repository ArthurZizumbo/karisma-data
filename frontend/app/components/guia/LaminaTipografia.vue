<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { ESCALA_TIPOGRAFICA } from '~/utils/tokens.generated'

/**
 * Type plate of the living design system.
 *
 * The specimen is rendered with the very fonts the portal serves from its own
 * origin, so what the capture shows is the type the product uses. Sizes come
 * from the generated scale and are applied as inline measures: a class assembled
 * at run time could be dropped by the CSS scanner and the plate would then
 * document a size the reader is not seeing.
 */
defineOptions({ name: 'LaminaTipografia' })

/** The two families of the system, with the class that renders each. */
const FAMILIAS = Object.freeze([
  { id: 'display', clave: 'guide.typography.family.display', clase: 'font-display' },
  { id: 'sans', clave: 'guide.typography.family.sans', clase: 'font-sans' },
])

const { t } = useI18n()
</script>

<template>
  <section
    data-lamina="tipografia"
    class="flex flex-col gap-4 rounded-lg border border-line bg-surface p-[var(--card-padding)] shadow-reposo"
  >
    <header class="flex flex-col gap-1">
      <h2 class="font-display text-titulo-2 text-primary-dark">
        {{ t('guide.plate.typography') }}
      </h2>
      <p class="max-w-prose text-cuerpo text-muted">
        {{ t('guide.typography.description') }}
      </p>
      <p class="max-w-prose text-cuerpo text-muted">
        {{ t('guide.typography.weightNote') }}
      </p>
    </header>

    <ul class="grid gap-[var(--grid-gap)] lg:grid-cols-2">
      <li
        v-for="familia in FAMILIAS"
        :key="familia.id"
        :data-familia="familia.id"
        class="flex flex-col gap-2 rounded-md border border-line-strong bg-surface-alt p-3"
      >
        <span class="text-etiqueta text-ink">{{ t(familia.clave) }}</span>
        <p :class="familia.clase" class="text-titulo-1 text-ink">
          {{ t('guide.typography.specimen') }}
        </p>
      </li>
    </ul>

    <div class="overflow-x-auto">
      <table class="w-full border-collapse text-left">
        <caption class="sr-only">
          {{ t('guide.plate.typography') }}
        </caption>
        <thead>
          <tr class="bg-primary-700 text-surface">
            <th scope="col" class="px-2 py-2 text-etiqueta">
              {{ t('guide.typography.column.role') }}
            </th>
            <th scope="col" class="px-2 py-2 text-etiqueta">
              {{ t('guide.typography.column.token') }}
            </th>
            <th scope="col" class="px-2 py-2 text-right text-etiqueta">
              {{ t('guide.typography.column.size') }}
            </th>
            <th scope="col" class="px-2 py-2 text-right text-etiqueta">
              {{ t('guide.typography.column.lineHeight') }}
            </th>
            <th scope="col" class="px-2 py-2 text-etiqueta">
              {{ t('guide.typography.column.usage') }}
            </th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="rol in ESCALA_TIPOGRAFICA"
            :key="rol.clave"
            :data-rol="rol.clave"
            class="border-b border-line odd:bg-surface even:bg-surface-alt"
          >
            <td class="px-2 py-2">
              <span
                :class="rol.familia === 'display' ? 'font-display' : 'font-sans'"
                :style="{ fontSize: `${rol.tamanoPx}px`, lineHeight: `${rol.interlineaPx}px` }"
                class="text-ink"
              >{{ rol.etiqueta }}</span>
            </td>
            <td class="px-2 py-2 text-cuerpo text-ink">{{ rol.clase }}</td>
            <td class="px-2 py-2 text-right text-cuerpo tabular-nums text-ink">{{ rol.tamanoPx }}</td>
            <td class="px-2 py-2 text-right text-cuerpo tabular-nums text-ink">
              {{ rol.interlineaPx }}
            </td>
            <td lang="es" class="px-2 py-2 text-cuerpo text-ink">{{ rol.uso }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</template>
