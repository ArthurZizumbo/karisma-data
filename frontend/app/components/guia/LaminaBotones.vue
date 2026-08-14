<script setup lang="ts">
/**
 * Button plate, rebuilt in the diagram world.
 *
 * Seventeen cells: three variants by five states, plus the destructive action
 * and the loading one. The frozen states are the point of the plate, because
 * hover, focus and pressed cannot be photographed from a live control.
 *
 * Two defects the audit measured and this rebuild fixes. The state label used
 * to sit *below* its button in 11px muted, the weakest type in the cell, so the
 * reader had to remember which cell was which across a five column grid; it is
 * a caption above the specimen now. And the frozen focus cells published a ring
 * the product never paints: they draw the one real definition, and the plate
 * prints its literal class string so copying it cannot produce a fourth.
 */
import { useI18n } from 'vue-i18n'
import { ANILLO_FOCO, ANILLO_FOCO_CONGELADO } from '~/utils/foco'

const { t } = useI18n()

const VARIANTES = Object.freeze([
  {
    id: 'filled',
    reposo: 'bg-corriente-pleno text-ground border border-corriente-pleno',
    puntero: 'bg-corriente-medio text-ground border border-corriente-medio',
    pulsado: 'bg-corriente-medio text-ground border border-corriente-medio translate-y-px',
    inerte: 'bg-ground-alt text-corriente-apagado border border-grid',
  },
  {
    id: 'outline',
    reposo: 'border border-corriente-medio text-corriente-pleno',
    puntero: 'border border-corriente-pleno text-corriente-pleno bg-ground-alt',
    pulsado: 'border border-corriente-pleno text-corriente-pleno bg-ground-alt translate-y-px',
    inerte: 'border border-grid text-corriente-apagado',
  },
  {
    id: 'text',
    reposo: 'text-corriente-pleno border border-transparent',
    puntero: 'text-corriente-pleno border border-transparent bg-ground-alt',
    pulsado: 'text-corriente-pleno border border-transparent bg-ground-alt translate-y-px',
    inerte: 'text-corriente-apagado border border-transparent',
  },
])

const ESTADOS = Object.freeze(['rest', 'hover', 'focus', 'active', 'disabled'])

/** Frozen presentation of one cell; the live focus ring is never simulated. */
function clases(variante: (typeof VARIANTES)[number], estado: string): string {
  const base = 'inline-flex min-h-9 items-center px-3 text-etiqueta'
  if (estado === 'hover') return `${base} ${variante.puntero}`
  if (estado === 'active') return `${base} ${variante.pulsado}`
  if (estado === 'disabled') return `${base} ${variante.inerte}`
  if (estado === 'focus') return `${base} ${variante.reposo} ${ANILLO_FOCO_CONGELADO}`
  return `${base} ${variante.reposo}`
}
</script>

<template>
  <section data-lamina="botones" class="flex flex-col gap-6">
    <h2 class="text-titulo-2 text-corriente-pleno">
      {{ t('guide.plate.buttons') }}
    </h2>

    <div class="overflow-x-auto">
      <table class="border-collapse">
        <caption class="sr-only">{{ t('guide.buttons.description') }}</caption>
        <thead>
          <tr>
            <th scope="col" class="pr-4 pb-2 text-left text-etiqueta text-corriente-tenue">
              <span class="sr-only">{{ t('guide.plate.buttons') }}</span>
            </th>
            <!-- The state names the column: read once, not once per cell. -->
            <th
              v-for="estado in ESTADOS"
              :key="estado"
              scope="col"
              class="px-3 pb-2 text-left text-etiqueta text-corriente-tenue"
            >
              {{ t(`guide.buttons.state.${estado}`) }}
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="variante in VARIANTES" :key="variante.id">
            <th scope="row" class="pr-4 text-left text-etiqueta text-corriente-pleno">
              {{ t(`guide.buttons.variant.${variante.id}`) }}
            </th>
            <td v-for="estado in ESTADOS" :key="estado" class="px-3 py-2">
              <span
                :data-boton-celda="`${variante.id}-${estado}`"
                :class="clases(variante, estado)"
                :aria-disabled="estado === 'disabled' ? 'true' : undefined"
              >
                {{ t(`guide.buttons.label.${variante.id}`) }}
              </span>
            </td>
          </tr>
          <tr>
            <th scope="row" class="pr-4 text-left text-etiqueta text-error">
              {{ t('guide.buttons.variant.destructive') }}
            </th>
            <td class="px-3 py-2">
              <span
                data-boton-celda="destructive-rest"
                class="inline-flex min-h-9 items-center gap-1 border border-error px-3 text-etiqueta text-error"
              >
                <Icon name="lucide:trash-2" class="size-3.5 shrink-0" aria-hidden="true" />
                {{ t('guide.buttons.label.destructive') }}
              </span>
            </td>
            <td colspan="4" class="px-3 py-2 text-micro text-corriente-tenue">
              {{ t('guide.buttons.rule') }}
            </td>
          </tr>
          <tr>
            <th scope="row" class="pr-4 text-left text-etiqueta text-corriente-pleno">
              {{ t('guide.buttons.state.loading') }}
            </th>
            <td class="px-3 py-2">
              <span
                data-boton-celda="filled-loading"
                aria-busy="true"
                class="inline-flex min-h-9 items-center gap-2 border border-corriente-pleno bg-corriente-pleno px-3 text-etiqueta text-ground"
              >
                <Icon name="lucide:loader" class="size-3.5 shrink-0 animate-spin" aria-hidden="true" />
                {{ t('guide.buttons.label.loading') }}
              </span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="flex flex-col gap-1 border-l-2 border-info pl-4">
      <p class="text-etiqueta uppercase text-corriente-tenue">
        {{ t('guide.buttons.focusRing') }}
      </p>
      <!-- The literal string, so copying the plate cannot invent a fourth ring. -->
      <code data-anillo-foco class="font-mono text-micro text-corriente-pleno">
        {{ ANILLO_FOCO }}
      </code>
    </div>

    <details class="border-t border-grid pt-3">
      <summary class="cursor-pointer text-etiqueta text-corriente-tenue" :class="ANILLO_FOCO">
        {{ t('guide.palette.why') }}
      </summary>
      <p class="mt-2 max-w-(--medida-maxima) text-cuerpo text-corriente-medio">
        {{ t('guide.buttons.frozenNote') }}
      </p>
    </details>
  </section>
</template>
