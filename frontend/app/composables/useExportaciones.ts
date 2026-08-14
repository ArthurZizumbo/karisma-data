/**
 * Facade of the export store, plus the reading rules its screen needs.
 *
 * The components get everything from here and never import the store: a `.vue`
 * that knew how to parse a filter, how to decide that a link died or which
 * catalogue key a backend code maps to would be holding business logic, and the
 * next screen that shows a job would hold a second copy of it.
 *
 * The formatters take no literal. A size is rendered through `Intl` in the unit
 * the reader's language spells, and a deadline through `Intl.RelativeTimeFormat`,
 * so neither "MB" nor "in 3 hours" is ever typed into a template.
 */
import type { ComputedRef, MaybeRefOrGetter } from 'vue'
import type {
  CodigoErrorTrabajo,
  DatasetExportable,
  FalloExportacion,
  FiltrosExportacion,
  FormatoExportacion,
  MomentoExportacion,
} from '~/types/exportacion'
import { computed, onScopeDispose, ref, toValue, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useExportacionesStore } from '~/stores/exportaciones'

/**
 * The three exportable datasets, in the order the form offers them.
 *
 * They mirror `DATASETS_EXPORTABLES` of the backend, which is the tuple of
 * catalogue sources with a real extract behind them. A fourth option would
 * build a request the validator answers with a 422.
 */
export const DATASETS: readonly DatasetExportable[] = Object.freeze([
  'creditos',
  'liquidez',
  'derivados',
])

/** The two formats, with CSV first because it is the one that works today. */
export const FORMATOS: readonly FormatoExportacion[] = Object.freeze(['csv', 'xlsx'])

/** Catalogue leaf under `export.job.error.` for each code of a failed job. */
export const CLAVE_DE_ERROR_TRABAJO: Readonly<Record<CodigoErrorTrabajo, string>> = Object.freeze({
  origen_ausente: 'missingSource',
  columna_desconocida: 'unknownColumn',
  formato_no_disponible: 'formatUnavailable',
  fallo_interno: 'internalFailure',
})

/** Catalogue leaf under `export.error.` for each refused request. */
const CLAVE_DE_FALLO: Readonly<Record<string, string>> = Object.freeze({
  trabajo_no_encontrado: 'notFound',
  enlace_caducado: 'expired',
  firma_invalida: 'signature',
  trabajos_no_disponibles: 'unavailable',
})

/**
 * Catalogue key that explains a refused request.
 *
 * A body with no code of ours -a 500, a proxy that answered HTML, a network
 * that never answered- lands on the generic sentence rather than printing a
 * backend identifier at the reader.
 *
 * @param fallo - Failure as the store recorded it.
 * @returns Dotted key of the sentence to render.
 */
export function claveDeFallo(fallo: FalloExportacion): string {
  const hoja = fallo.codigo === null ? undefined : CLAVE_DE_FALLO[fallo.codigo]
  return `export.error.${hoja ?? 'generic'}`
}

/**
 * Catalogue key that explains why a job ended `fallido`.
 *
 * @param codigo - Value of the `error` field of the job.
 * @returns Dotted key of the sentence to render.
 */
export function claveDeErrorDeTrabajo(codigo: string | null): string {
  const hoja = codigo === null ? undefined : CLAVE_DE_ERROR_TRABAJO[codigo as CodigoErrorTrabajo]
  return `export.job.error.${hoja ?? 'internalFailure'}`
}

/**
 * Reads the filter field into the map the compiler understands.
 *
 * The syntax is `columna=valor` with commas for several values and semicolons
 * or line breaks between pairs, because the backend compiles exactly one thing
 * -`pl.col(columna).is_in([...])`- and a richer editor would offer operators no
 * endpoint accepts. An empty field is a valid request over the whole dataset.
 *
 * @param texto - What the reader typed.
 * @returns The filters, or null when the text is not a list of pairs.
 */
export function analizarFiltros(texto: string): FiltrosExportacion | null {
  const filtros: Record<string, string | string[]> = {}

  for (const bruto of texto.split(/[;\n]/)) {
    const par = bruto.trim()
    if (par === '') {
      continue
    }

    const corte = par.indexOf('=')
    if (corte < 1) {
      return null
    }

    const columna = par.slice(0, corte).trim()
    const valores = par
      .slice(corte + 1)
      .split(',')
      .map(valor => valor.trim())
      .filter(valor => valor !== '')

    if (columna === '' || valores.length === 0) {
      return null
    }

    filtros[columna] = valores.length === 1 ? valores[0]! : valores
  }

  return filtros
}

/** The three moments, in the order the flow walks them. */
export const MOMENTOS: readonly MomentoExportacion[] = Object.freeze([
  'solicitud',
  'proceso',
  'enlace',
])

/**
 * Reads `?momento=` into the moment it pins, if it names one.
 *
 * Pinning does not fabricate anything: it decides which real job stays expanded
 * and switches the auto advance off, so the three states of the flow can be
 * captured one by one for the deliverable. A value the portal does not know is
 * no pin at all, and the screen goes back to following the real state.
 *
 * @param valor - Raw value of the query parameter.
 * @returns The pinned moment, or null when there is none.
 */
export function momentoDeConsulta(valor: unknown): MomentoExportacion | null {
  const bruto = Array.isArray(valor) ? valor[0] : valor
  return typeof bruto === 'string' && (MOMENTOS as readonly string[]).includes(bruto)
    ? (bruto as MomentoExportacion)
    : null
}

/**
 * Seconds the backend stretches a real job by, as the deployment declares it.
 *
 * The stretch is a setting of the API (`EXPORT_DEMO_DELAY_SECONDS`) and the
 * four endpoints of the contract do not publish it, so the interface learns it
 * from its own runtime configuration. Unknown reads as zero, and zero hides the
 * honesty band: a band that announced a stretch that is not happening would be
 * the very thing it exists to prevent.
 *
 * @param publico - Public runtime configuration of the application.
 * @returns The declared delay in seconds, or 0 when there is none.
 */
export function retrasoDeDemostracion(publico: Record<string, unknown>): number {
  const valor = publico.exportDemoDelay
  const numero = typeof valor === 'string' ? Number.parseFloat(valor) : valor
  return typeof numero === 'number' && Number.isFinite(numero) && numero > 0 ? numero : 0
}

/**
 * Whether a signed link is already past its deadline.
 *
 * The backend answers 410 to an expired link, so this only decides what the
 * card offers: a link the portal knows is dead is not presented as a download.
 *
 * @param caducaEn - Instant the signature encodes, as the API sends it.
 * @param ahora - Reference instant.
 * @returns True when the link can no longer be redeemed.
 */
export function haCaducado(caducaEn: string | null, ahora: Date = new Date()): boolean {
  return caducaEn !== null && Date.parse(caducaEn) <= ahora.getTime()
}

/** Largest delay a browser stores. Beyond it, a timeout fires immediately. */
const RETRASO_MAXIMO = 2_147_483_647

/**
 * The same verdict, but bound to the deadline instead of to the render.
 *
 * `haCaducado` answers about the instant it is called, so a card drawn while
 * the link was alive keeps offering the download until something else forces
 * that card to render again: the reader clicks a button the backend answers
 * with a 410. The instant is not a guess -the signature encodes it and the wire
 * publishes it as `caduca_en`- so a SINGLE shot armed for that instant is
 * enough. It is not a second poll: it makes no request, and there is one timer
 * per card, cleared when the deadline changes and when the scope that asked for
 * it is disposed of.
 *
 * The shot re-arms itself instead of declaring the link dead when it fires, and
 * that is not belt and braces: a delay is stored in 32 bits, so anything beyond
 * about 24 days fires AT ONCE, and a timer is also allowed to fire a hair
 * early. Both cases end the same way -the clock is read again and, if the
 * deadline is still ahead, a new shot covers what is left- so the verdict flips
 * when the deadline really passes and never before.
 *
 * @param caducaEn - Instant the signature encodes, as the API sends it.
 * @returns True once the link can no longer be redeemed.
 */
export function useCaducidadDeEnlace(
  caducaEn: MaybeRefOrGetter<string | null>,
): ComputedRef<boolean> {
  const referencia = ref(Date.now())
  let disparo: ReturnType<typeof setTimeout> | null = null

  function cancelar(): void {
    if (disparo !== null) {
      clearTimeout(disparo)
      disparo = null
    }
  }

  /**
   * Arms the shot for a deadline, replacing any previous one.
   *
   * @param valor - Deadline of the link the card is showing now, if any.
   */
  function programar(valor: string | null): void {
    cancelar()
    referencia.value = Date.now()
    if (valor === null) {
      return
    }
    const limite = Date.parse(valor)
    if (!Number.isFinite(limite) || limite <= referencia.value) {
      return
    }
    disparo = setTimeout(
      () => {
        disparo = null
        programar(valor)
      },
      Math.min(limite - referencia.value, RETRASO_MAXIMO),
    )
  }

  // The deadline arrives as a prop and it changes: a job with no link yet
  // carries null, and the poll fills it in the moment the extraction ends. A
  // shot armed once at setup would be armed for the wrong instant, or for none.
  watch(() => toValue(caducaEn), programar, { immediate: true })
  onScopeDispose(cancelar)

  return computed(() => haCaducado(toValue(caducaEn), new Date(referencia.value)))
}

/** The four formatters of the screen, bound to the language being rendered. */
export interface FormatoExportaciones {
  /** Row count, grouped the way the language groups thousands. */
  filas: (valor: number | null) => string
  /** Byte size in the largest unit that keeps it readable. */
  tamano: (valor: number | null) => string
  /** Date and time of an instant of the wire. */
  instante: (valor: string | null) => string
  /** How long is left, or how long ago it ran out. */
  caducidad: (valor: string | null, ahora?: Date) => string
}

/** Units of the size ladder, from bytes up. `Intl` spells each one. */
const UNIDADES = ['byte', 'kilobyte', 'megabyte', 'gigabyte'] as const

/** Placeholder for a figure the job has not produced yet. Not a word. */
const SIN_DATO = '—'

/**
 * Formatters for the current language.
 *
 * @returns The four functions the card and the history render figures with.
 */
export function useFormatoExportaciones(): FormatoExportaciones {
  const { locale } = useI18n()

  return {
    filas: (valor) => {
      return valor === null ? SIN_DATO : new Intl.NumberFormat(locale.value).format(valor)
    },
    tamano: (valor) => {
      if (valor === null) {
        return SIN_DATO
      }
      let escala = 0
      let cifra = valor
      while (cifra >= 1024 && escala < UNIDADES.length - 1) {
        cifra /= 1024
        escala += 1
      }
      return new Intl.NumberFormat(locale.value, {
        style: 'unit',
        unit: UNIDADES[escala]!,
        unitDisplay: 'short',
        maximumFractionDigits: escala === 0 ? 0 : 1,
      }).format(cifra)
    },
    instante: (valor) => {
      return valor === null
        ? SIN_DATO
        : new Intl.DateTimeFormat(locale.value, {
            dateStyle: 'short',
            timeStyle: 'short',
          }).format(new Date(valor))
    },
    caducidad: (valor, ahora = new Date()) => {
      if (valor === null) {
        return SIN_DATO
      }
      const restante = Date.parse(valor) - ahora.getTime()
      const formato = new Intl.RelativeTimeFormat(locale.value, { numeric: 'auto' })
      const minutos = Math.round(restante / 60_000)
      if (Math.abs(minutos) < 60) {
        return formato.format(minutos, 'minute')
      }
      const horas = Math.round(restante / 3_600_000)
      return Math.abs(horas) < 24
        ? formato.format(horas, 'hour')
        : formato.format(Math.round(restante / 86_400_000), 'day')
    },
  }
}

/**
 * Everything the screen reads and every action it can take.
 *
 * The Pinia instance, not a copy of it: the values arrive already unwrapped, so
 * a template writes `exportaciones.trabajos` and a destructured field cannot
 * quietly stop being reactive.
 */
export type PanelExportaciones = ReturnType<typeof useExportacionesStore>

/**
 * The export state, for the screen and for anything that watches it later.
 *
 * A thin facade on purpose: the store is the single instance -one timer for the
 * whole application- and this only spares every component the import.
 *
 * @returns The shared export state and its actions.
 */
export function useExportaciones(): PanelExportaciones {
  return useExportacionesStore()
}
