<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { ANILLO_FOCO } from '~/utils/foco'

/**
 * Card plate of the living design system.
 *
 * Two families of cards live here. The indicator card publishes its four
 * unhappy states next to the happy one, because a system that only documents
 * the happy path is the reason every screen invents its own empty message. The
 * tool call card publishes the four moments of an assistant query, and it is
 * what makes the anti hallucination rule visible: the query is announced before
 * it runs, and the failure state carries no figures at all.
 */
defineOptions({ name: 'LaminaTarjetas' })

/** One of the four unhappy states of an indicator card. */
interface EstadoTarjeta {
  /** Slug written into data-tarjeta. */
  readonly id: string
  readonly icono: string
  readonly claveTitulo: string
  readonly claveCuerpo: string
  readonly claveAccion: string | null
  readonly clasesIcono: string
}

/** One of the four moments of an assistant tool call. */
interface EstadoConsulta {
  /** Slug written into data-tool-call. */
  readonly id: string
  readonly icono: string
  readonly claveTitulo: string
  readonly claveCuerpo: string
  readonly claveAccion: string
  readonly clases: string
  readonly clasesIcono: string
  readonly girando: boolean
}

const ESTADOS_TARJETA: readonly EstadoTarjeta[] = Object.freeze([
  {
    id: 'carga',
    icono: 'lucide:loader-circle',
    claveTitulo: 'guide.cards.state.loading',
    claveCuerpo: 'guide.cards.state.loadingBody',
    claveAccion: null,
    clasesIcono: 'text-muted',
  },
  {
    id: 'vacio',
    icono: 'lucide:inbox',
    claveTitulo: 'guide.cards.state.empty',
    claveCuerpo: 'guide.cards.state.emptyBody',
    claveAccion: null,
    clasesIcono: 'text-muted',
  },
  {
    id: 'error',
    icono: 'lucide:circle-alert',
    claveTitulo: 'guide.cards.state.error',
    claveCuerpo: 'guide.cards.state.errorBody',
    claveAccion: 'guide.cards.state.retry',
    clasesIcono: 'text-danger',
  },
  {
    id: 'sin-permiso',
    icono: 'lucide:lock',
    claveTitulo: 'guide.cards.state.forbidden',
    claveCuerpo: 'guide.cards.state.forbiddenBody',
    claveAccion: 'guide.cards.state.request',
    clasesIcono: 'text-accent-text',
  },
])

const ESTADOS_CONSULTA: readonly EstadoConsulta[] = Object.freeze([
  {
    id: 'anuncio',
    icono: 'lucide:bot',
    claveTitulo: 'guide.cards.toolCall.state.announced',
    claveCuerpo: 'guide.cards.toolCall.body.announced',
    claveAccion: 'guide.cards.toolCall.stop',
    clases: 'border-line-strong bg-surface-alt',
    // Ink and not the muted neutral: the announcement card is filled with
    // surface-alt, where muted measures 4.27:1.
    clasesIcono: 'text-ink',
    girando: false,
  },
  {
    id: 'ejecucion',
    icono: 'lucide:loader-circle',
    claveTitulo: 'guide.cards.toolCall.state.running',
    claveCuerpo: 'guide.cards.toolCall.body.running',
    claveAccion: 'guide.cards.toolCall.stop',
    clases: 'border-primary bg-primary-100',
    clasesIcono: 'text-primary-700',
    girando: true,
  },
  {
    id: 'resultado',
    icono: 'lucide:circle-check',
    claveTitulo: 'guide.cards.toolCall.state.done',
    claveCuerpo: 'guide.cards.toolCall.body.done',
    claveAccion: 'guide.cards.toolCall.lineage',
    clases: 'border-success-700 bg-success-100',
    clasesIcono: 'text-success-900',
    girando: false,
  },
  {
    id: 'error',
    icono: 'lucide:circle-alert',
    claveTitulo: 'guide.cards.toolCall.state.error',
    claveCuerpo: 'guide.cards.toolCall.body.error',
    claveAccion: 'guide.cards.toolCall.retry',
    clases: 'border-danger bg-surface',
    clasesIcono: 'text-danger',
    girando: false,
  },
])

const ACCION
  = `inline-flex min-h-11 items-center justify-center gap-2 whitespace-nowrap rounded-md border border-primary bg-surface px-4 text-cuerpo text-primary ${ANILLO_FOCO}`

const { t } = useI18n()
</script>

<template>
  <section
    data-lamina="tarjetas"
    class="flex flex-col gap-4 rounded-lg border border-line bg-surface p-[var(--card-padding)] shadow-reposo"
  >
    <header class="flex flex-col gap-1">
      <h2 class="font-display text-titulo-2 text-primary-dark">
        {{ t('guide.plate.cards') }}
      </h2>
      <p class="max-w-prose text-cuerpo text-muted">
        {{ t('guide.cards.description') }}
      </p>
    </header>

    <ul class="grid gap-[var(--grid-gap)] sm:grid-cols-2 lg:grid-cols-3">
      <li
        data-tarjeta="kpi"
        class="flex flex-col gap-1 rounded-lg border border-line-strong bg-surface p-[var(--card-padding)] shadow-reposo"
      >
        <span class="text-etiqueta text-muted">{{ t('guide.cards.kpi.label') }}</span>
        <span class="text-display tabular-nums text-ink-strong">1 284 350</span>
        <span class="flex items-center gap-1 text-cuerpo text-success-900">
          <Icon name="lucide:trending-up" class="size-5 shrink-0" aria-hidden="true" />
          {{ t('guide.cards.kpi.delta') }}
        </span>
        <span class="mt-auto text-micro text-accent-text">
          {{ t('guide.cards.kpi.footnote') }}
        </span>
      </li>

      <li
        v-for="estado in ESTADOS_TARJETA"
        :key="estado.id"
        :data-tarjeta="estado.id"
        class="flex flex-col gap-1 rounded-lg border border-line-strong bg-surface p-[var(--card-padding)]"
      >
        <span class="flex items-center gap-2">
          <Icon
            :name="estado.icono"
            class="size-6 shrink-0"
            :class="[estado.clasesIcono, estado.id === 'carga' ? 'animate-spin motion-reduce:animate-none' : '']"
            aria-hidden="true"
          />
          <span class="text-titulo-3 text-ink">{{ t(estado.claveTitulo) }}</span>
        </span>

        <!--
          The skeleton keeps the height of the figure it replaces. Without it the
          card grows when the value lands and the whole grid jumps.
        -->
        <span
          v-if="estado.id === 'carga'"
          class="h-10 w-2/3 animate-pulse rounded-sm bg-surface-alt motion-reduce:animate-none"
          aria-hidden="true"
        />

        <p class="text-cuerpo text-muted">{{ t(estado.claveCuerpo) }}</p>

        <button v-if="estado.claveAccion" type="button" :class="ACCION" class="mt-auto">
          {{ t(estado.claveAccion) }}
        </button>
      </li>
    </ul>

    <div class="flex flex-col gap-2">
      <h3 class="font-display text-titulo-3 text-ink">
        {{ t('guide.cards.toolCall.title') }}
      </h3>
      <p class="max-w-prose text-cuerpo text-muted">
        {{ t('guide.cards.toolCall.note') }}
      </p>

      <ul class="grid gap-[var(--grid-gap)] sm:grid-cols-2">
        <li
          v-for="consulta in ESTADOS_CONSULTA"
          :key="consulta.id"
          :data-tool-call="consulta.id"
          class="flex flex-col gap-2 rounded-lg border p-[var(--card-padding)]"
          :class="consulta.clases"
        >
          <span class="flex items-center gap-2">
            <Icon
              :name="consulta.icono"
              class="size-5 shrink-0"
              :class="[consulta.clasesIcono, consulta.girando ? 'animate-spin motion-reduce:animate-none' : '']"
              aria-hidden="true"
            />
            <span class="text-titulo-3 text-ink">{{ t(consulta.claveTitulo) }}</span>
          </span>
          <p class="rounded-sm border border-line-strong bg-surface px-2 py-1 text-etiqueta text-ink">
            {{ t('guide.cards.toolCall.query') }}
          </p>
          <p class="text-cuerpo text-ink">{{ t(consulta.claveCuerpo) }}</p>
          <button type="button" :class="ACCION" class="mt-auto self-start">
            {{ t(consulta.claveAccion) }}
          </button>
        </li>
      </ul>
    </div>
  </section>
</template>
