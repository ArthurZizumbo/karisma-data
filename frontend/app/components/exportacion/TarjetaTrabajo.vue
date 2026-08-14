<script setup lang="ts">
/**
 * Second and third moments: one job, one card, addressed by its `job_id`.
 *
 * The same card renders the work in flight and the finished link because they
 * are the same record at two instants, and splitting them into two components
 * would mean deciding, in the markup, which of the two the reader is looking
 * at -exactly the decision this User Story forbids taking anywhere but from
 * real state.
 *
 * Collapsed it shows what the job is and how it is doing; expanded it adds the
 * figures and the link. Two rungs, and the second one is one click away.
 *
 * The icon names are literal on every branch and never assembled in a binding:
 * the icon module scans the sources as text, so a name built at run time ships
 * as an empty box in the production bundle.
 *
 * `url_descarga` is used verbatim. It arrives as a relative path so the Nitro
 * proxy forwards it with the session cookie; prefixing a host would send the
 * browser somewhere with no session and a signature nobody there can check.
 *
 * The deadline of that link is watched, not read once. `caduca_en` names the
 * exact instant the signature stops being redeemable, so the card arms a single
 * shot for it -no request, no second poll- and stops offering the download the
 * moment it passes, with the screen open and untouched. Cleared when the card
 * goes away, which is what keeps one timer per visible job and not one per job
 * ever rendered.
 *
 * Two things here change without the reader doing anything -the state word and
 * the appearance of the link- and both are announced from containers that are
 * mounted before the change, not inserted with it. A live region born already
 * populated is silent in every screen reader, so a card that only grew a
 * `role="status"` when the job ended would still leave that reader waiting.
 * The motion of the spinner and of the progress bar is decoration over that
 * same state, so both stop under `prefers-reduced-motion` while the words and
 * the colours keep saying the same thing.
 */
import type { TrabajoVigilado } from '~/types/exportacion'
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import {
  claveDeErrorDeTrabajo,
  useCaducidadDeEnlace,
  useFormatoExportaciones,
} from '~/composables/useExportaciones'
import { esTerminal } from '~/stores/exportaciones'
import { ANILLO_FOCO } from '~/utils/foco'

const props = defineProps<{
  /** The job, with the polled detail already merged over the summary. */
  trabajo: TrabajoVigilado
  /** True when this is the row the current moment expands. */
  expandido: boolean
}>()

const emit = defineEmits<{
  /** The reader asked to open or close this row. Carries the job id. */
  alternar: [string]
}>()

const { t } = useI18n()
const formato = useFormatoExportaciones()

/** True while the job can still change state on its own. */
const enCurso = computed(() => !esTerminal(props.trabajo.estado) && !props.trabajo.caducadoEnCliente)

/** True once this link ran out, whether or not anything else moved meanwhile. */
const caducoElEnlace = useCaducidadDeEnlace(() => props.trabajo.caduca_en)

/** True when there is a live link to offer. */
const descargable = computed(
  () =>
    props.trabajo.estado === 'completado'
    && props.trabajo.url_descarga !== null
    && !caducoElEnlace.value,
)

/** True when the job finished but its signed link already ran out. */
const caducado = computed(
  () => props.trabajo.estado === 'completado' && caducoElEnlace.value,
)

const idDetalle = computed(() => `exportacion-detalle-${props.trabajo.job_id}`)

/** Ramp step of each state, so the colour says the same as the word. */
const TONO: Readonly<Record<string, string>> = Object.freeze({
  pendiente: 'text-corriente-tenue',
  en_proceso: 'text-info',
  completado: 'text-ok',
  fallido: 'text-error',
})
</script>

<template>
  <article
    :data-trabajo="trabajo.job_id"
    :data-estado="trabajo.estado"
    :data-expandido="expandido"
    class="flex flex-col gap-2 border border-corriente-apagado bg-ground p-4"
  >
    <div class="flex flex-wrap items-center justify-between gap-2">
      <h3 class="min-w-0">
        <button
          data-accion="alternar"
          type="button"
          :aria-expanded="expandido"
          :aria-controls="idDetalle"
          class="flex items-center gap-2 text-titulo-3 text-corriente-pleno"
          :class="ANILLO_FOCO"
          @click="emit('alternar', trabajo.job_id)"
        >
          <Icon v-if="expandido" name="lucide:chevron-down" class="size-4 shrink-0" aria-hidden="true" />
          <Icon v-else name="lucide:chevron-right" class="size-4 shrink-0" aria-hidden="true" />
          {{ t(`export.dataset.${trabajo.dataset}`) }}
        </button>
      </h3>

      <!--
        The one piece of text on this screen that changes with nobody touching
        anything: the poll walks it from queued to running to done every three
        seconds. So the paragraph itself is the live region. It renders on every
        branch, which means it is already in the accessibility tree when the word
        swaps -a region inserted with its text already inside is not announced,
        and that is exactly the defect a `role="status"` added at the instant of
        the change would reproduce. `aria-atomic` because the icon and the word
        are one statement, not two.
      -->
      <p
        data-etiqueta="estado"
        aria-live="polite"
        aria-atomic="true"
        class="flex items-center gap-2 text-etiqueta uppercase"
        :class="TONO[trabajo.estado]"
      >
        <!-- The spin is the only proof the job is alive, so it yields to a
             reader who asked the system for less motion, like the loaders of
             the access form and the assistant. -->
        <Icon
          v-if="enCurso"
          name="lucide:loader"
          class="size-3.5 shrink-0 animate-spin motion-reduce:animate-none"
          aria-hidden="true"
        />
        <Icon v-else name="lucide:circle" class="size-3.5 shrink-0" aria-hidden="true" />
        {{ t(`export.job.state.${trabajo.estado}`) }}
      </p>
    </div>

    <p class="flex items-center gap-2 text-micro text-corriente-tenue">
      <span>{{ t(`export.format.${trabajo.formato}`) }}</span>
      <span>{{ formato.instante(trabajo.solicitado_en) }}</span>
    </p>

    <div
      v-if="enCurso"
      data-progreso
      role="progressbar"
      :aria-label="t(`export.job.state.${trabajo.estado}`)"
      class="h-1 w-full overflow-hidden bg-ground-alt"
    >
      <span class="block h-full w-1/3 animate-pulse bg-info motion-reduce:animate-none" />
    </div>

    <div v-if="expandido" :id="idDetalle" class="flex flex-col gap-3 pt-1">
      <dl class="grid grid-cols-2 gap-x-4 gap-y-1 sm:grid-cols-4">
        <div class="flex flex-col">
          <dt class="text-micro text-corriente-tenue">
            {{ t('export.job.rows') }}
          </dt>
          <dd data-dato="filas" class="text-dato text-corriente-pleno">
            {{ formato.filas(trabajo.filas) }}
          </dd>
        </div>
        <div class="flex flex-col">
          <dt class="text-micro text-corriente-tenue">
            {{ t('export.job.size') }}
          </dt>
          <dd data-dato="tamano" class="text-dato text-corriente-pleno">
            {{ formato.tamano(trabajo.tamano_bytes) }}
          </dd>
        </div>
        <div class="flex flex-col">
          <dt class="text-micro text-corriente-tenue">
            {{ t('export.job.requestedAt') }}
          </dt>
          <dd data-dato="solicitado" class="text-dato text-corriente-pleno">
            {{ formato.instante(trabajo.solicitado_en) }}
          </dd>
        </div>
        <div class="flex flex-col">
          <dt class="text-micro text-corriente-tenue">
            {{ t('export.job.expiresAt') }}
          </dt>
          <dd data-dato="caduca" class="text-dato text-corriente-pleno">
            {{ formato.instante(trabajo.caduca_en) }}
          </dd>
        </div>
      </dl>

      <!--
        Outcome of the job, and the second thing here that arrives on its own.
        The container exists from the moment the row opens and stays empty while
        the work is still running, so it is in the accessibility tree before the
        link, the failure or the expiry land inside it: a region born already
        full is silent, and the reader would never learn their file is ready.
        The branches are mutually exclusive -one message replaces another whole-
        so `aria-atomic` reads the new one complete, and none of them carries its
        own `role="status"`: a live region nested inside another takes over its
        own subtree and gets the same announcement counted twice.
      -->
      <div aria-live="polite" aria-atomic="true">
        <p
          v-if="trabajo.caducadoEnCliente"
          data-aviso="detenido"
          class="flex items-start gap-2 border-l-2 border-aviso pl-3 text-cuerpo text-corriente-medio"
        >
          <Icon name="lucide:clock" class="mt-0.5 size-4 shrink-0 text-aviso" aria-hidden="true" />
          {{ t('export.job.stalled') }}
        </p>

        <p
          v-else-if="trabajo.estado === 'fallido'"
          data-aviso="fallido"
          class="flex items-start gap-2 border-l-2 border-error pl-3 text-cuerpo text-corriente-medio"
        >
          <Icon
            name="lucide:circle-alert"
            class="mt-0.5 size-4 shrink-0 text-error"
            aria-hidden="true"
          />
          {{ t(claveDeErrorDeTrabajo(trabajo.error)) }}
        </p>

        <div v-else-if="descargable" class="flex flex-col gap-1">
          <a
            data-accion="descargar"
            :href="trabajo.url_descarga ?? undefined"
            download
            class="flex min-h-9 items-center gap-2 self-start border border-corriente-pleno px-4 text-cuerpo text-corriente-pleno hover:bg-ground-alt"
            :class="ANILLO_FOCO"
          >
            <Icon name="lucide:download" class="size-4 shrink-0" aria-hidden="true" />
            {{ t('export.link.download') }}
          </a>
          <p data-dato="caducidad" class="text-micro text-corriente-tenue">
            {{ t('export.link.expiresIn', { cuando: formato.caducidad(trabajo.caduca_en) }) }}
          </p>
        </div>

        <p
          v-else-if="caducado"
          data-aviso="caducado"
          class="flex items-start gap-2 border-l-2 border-aviso pl-3 text-cuerpo text-corriente-medio"
        >
          <Icon name="lucide:clock" class="mt-0.5 size-4 shrink-0 text-aviso" aria-hidden="true" />
          {{ t('export.link.expired') }}
        </p>
      </div>
    </div>
  </article>
</template>
