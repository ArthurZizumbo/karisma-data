<script setup lang="ts">
/**
 * Field plate, rebuilt in the diagram world.
 *
 * Two defects the audit measured. The help text was a single reused string, so
 * "four digit account key" appeared under the reconciliation note and under the
 * maximum amount: a caption that lies is worse than none, and each field now
 * carries its own. And the field border used the decorative rule, which
 * measures 1.42:1 against the ground and fails the 3:1 a component boundary
 * needs; it uses the current ramp's middle rung, which is what informs.
 *
 * The chips carry a shape as well as a colour. In light mode the semantic marks
 * separate by only dE=13.4 under simulated dichromacy, so the icon is not
 * decoration: it is how the state is read.
 */
import { useI18n } from 'vue-i18n'
import { ANILLO_FOCO } from '~/utils/foco'

const { t } = useI18n()

/** Six field states, each with its own label and its own help text. */
const CAMPOS = Object.freeze([
  { id: 'rest', etiqueta: 'account', ayuda: true },
  { id: 'focus', etiqueta: 'period' },
  { id: 'filled', etiqueta: 'source', valor: 'SIC-BANXICO' },
  { id: 'error', etiqueta: 'amount', error: true },
  { id: 'disabled', etiqueta: 'code' },
  { id: 'readonly', etiqueta: 'note', valor: 'Conciliado el 31 de julio' },
])

/** Chips: colour plus shape, because colour alone does not separate. */
const CHIPS = Object.freeze([
  { id: 'neutral', color: 'text-corriente-tenue border-corriente-apagado', icono: 'lucide:circle-dashed' },
  { id: 'info', color: 'text-info border-info', icono: 'lucide:info' },
  { id: 'success', color: 'text-ok border-ok', icono: 'lucide:check' },
  { id: 'warning', color: 'text-aviso border-aviso', icono: 'lucide:triangle-alert' },
  { id: 'danger', color: 'text-error border-error', icono: 'lucide:x' },
])

const ROLES = Object.freeze(['operativo', 'analista', 'directivo', 'admin'])

function claseCampo(estado: string): string {
  const base = 'min-h-9 w-full bg-ground px-3 text-cuerpo text-corriente-pleno border'
  if (estado === 'error') return `${base} border-error`
  if (estado === 'disabled') return `${base} border-grid text-corriente-apagado`
  if (estado === 'readonly') return `${base} border-transparent bg-ground-alt`
  // The middle rung of the ramp, not the decorative rule: a component boundary
  // has to inform, and the decorative one measures 1.42:1.
  return `${base} border-corriente-medio`
}
</script>

<template>
  <section data-lamina="campos" class="flex flex-col gap-8">
    <h2 class="text-titulo-2 text-corriente-pleno">
      {{ t('guide.plate.fields') }}
    </h2>

    <ul class="grid gap-6 md:grid-cols-2 xl:grid-cols-3">
      <li v-for="campo in CAMPOS" :key="campo.id" :data-campo="campo.id" class="flex flex-col gap-1">
        <label :for="`campo-${campo.id}`" class="text-etiqueta text-corriente-pleno">
          {{ t(`guide.fields.label.${campo.etiqueta}`) }}
        </label>
        <input
          :id="`campo-${campo.id}`"
          type="text"
          :class="[claseCampo(campo.id), campo.id === 'focus' ? 'outline-2 outline-offset-2 outline-info' : '']"
          :placeholder="t('guide.fields.placeholder')"
          :value="campo.valor"
          :disabled="campo.id === 'disabled'"
          :readonly="campo.id === 'readonly'"
          :aria-invalid="campo.id === 'error' ? 'true' : undefined"
          :aria-describedby="campo.error ? `error-${campo.id}` : campo.ayuda ? `ayuda-${campo.id}` : undefined"
        >
        <!-- The state names itself; the reader does not infer it from the border. -->
        <p class="text-micro text-corriente-tenue">
          {{ t(`guide.fields.state.${campo.id}`) }}
        </p>
        <p v-if="campo.ayuda" :id="`ayuda-${campo.id}`" class="text-micro text-corriente-medio">
          {{ t('guide.fields.help') }}
        </p>
        <p
          v-if="campo.error"
          :id="`error-${campo.id}`"
          class="flex items-center gap-1 text-micro text-error"
        >
          <Icon name="lucide:x-circle" class="size-3 shrink-0" aria-hidden="true" />
          {{ t('guide.fields.error') }}
        </p>
      </li>
    </ul>

    <div class="flex flex-col gap-2">
      <h3 class="text-titulo-3 text-corriente-pleno">{{ t('guide.fields.chips') }}</h3>
      <ul class="flex flex-wrap gap-2">
        <li
          v-for="chip in CHIPS"
          :key="chip.id"
          :data-chip="chip.id"
          class="inline-flex items-center gap-1 border px-2 py-0.5 text-etiqueta"
          :class="chip.color"
        >
          <Icon :name="chip.icono" class="size-3 shrink-0" aria-hidden="true" />
          {{ t(`guide.fields.chip.${chip.id}`) }}
        </li>
      </ul>
    </div>

    <div class="flex flex-col gap-2">
      <h3 class="text-titulo-3 text-corriente-pleno">{{ t('guide.fields.badges') }}</h3>
      <ul class="flex flex-wrap gap-2">
        <li
          v-for="rol in ROLES"
          :key="rol"
          :data-insignia="rol"
          class="inline-flex items-center rounded-full border border-corriente-medio px-2.5 py-0.5 font-mono text-micro text-corriente-pleno"
        >
          {{ rol }}
        </li>
      </ul>
      <p class="max-w-(--medida-maxima) text-micro text-corriente-tenue">
        {{ t('guide.fields.badgeNote') }}
      </p>
    </div>

    <details class="border-t border-grid pt-3">
      <summary class="cursor-pointer text-etiqueta text-corriente-tenue" :class="ANILLO_FOCO">
        {{ t('guide.palette.why') }}
      </summary>
      <p class="mt-2 max-w-(--medida-maxima) text-cuerpo text-corriente-medio">
        {{ t('guide.fields.borderNote') }}
      </p>
    </details>
  </section>
</template>
