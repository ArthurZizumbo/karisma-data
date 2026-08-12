import type { Ref, ShallowRef } from 'vue'
import type { PasoGuion } from '~/utils/guionFluidez'
import { ref, shallowRef } from 'vue'
import { GUION_ZOOM, PASOS_GUION, UMBRAL_CUADRO_MS, VERSION_GUION } from '~/utils/guionFluidez'

/**
 * Fluidity measurement of the chart, replayed from the frozen script.
 *
 * The measurement is manual and reproducible rather than automated in CI, and
 * that is declared rather than hidden: Playwright is not installed and its
 * script belongs to another User Story. What is code here, and versioned, is the
 * gesture and the arithmetic, so two runs on two machines are comparable and the
 * report carries enough context to be read a month later.
 *
 * The statistics live in exported pure functions because that is the part a test
 * can actually falsify. Measuring the meter with a fake clock would measure the
 * fake clock.
 */

/** Worst frame, in milliseconds, still accepted by the agreed threshold. */
export const PEOR_CUADRO_MS = 250

/** Share of long frames, as a fraction, still accepted. */
export const MAXIMO_CUADROS_LARGOS = 0.05

/** Aggregated frame timings of one run. */
export interface MuestraFluidez {
  cuadros: number
  p50: number
  p95: number
  peor: number
  largos: number
  duracionMs: number
}

/** Where the run happened. A p95 without a machine is an anecdote. */
export interface EntornoMedicion {
  navegador: string
  plataforma: string
  viewport: string
  densidadPixel: number
}

/** The report, exactly as it is written to the evidence file. */
export interface InformeFluidez {
  versionGuion: number
  pasos: number
  umbralMs: number
  muestra: MuestraFluidez
  veredicto: 'cumple' | 'no-cumple'
  entorno: EntornoMedicion
  momento: string
}

/**
 * Percentile of a sample, by nearest rank over the sorted values.
 *
 * @param ordenados - Values already sorted ascending.
 * @param fraccion - Percentile as a fraction between 0 and 1.
 * @returns The value at that rank, or 0 for an empty sample.
 */
function percentil(ordenados: readonly number[], fraccion: number): number {
  if (ordenados.length === 0) {
    return 0
  }
  const rango = Math.ceil(fraccion * ordenados.length) - 1
  return ordenados[Math.min(ordenados.length - 1, Math.max(0, rango))] ?? 0
}

/**
 * Aggregates the intervals BETWEEN frames, never the timestamps themselves.
 *
 * Confusing the two is the classic defect of this measurement: the number comes
 * out enormous and monotonically increasing, and nobody can say why.
 *
 * @param intervalos - Milliseconds elapsed between consecutive frames.
 * @returns The aggregated sample.
 */
export function resumirIntervalos(intervalos: readonly number[]): MuestraFluidez {
  const ordenados = [...intervalos].sort((a, b) => a - b)
  return {
    cuadros: intervalos.length,
    p50: percentil(ordenados, 0.5),
    p95: percentil(ordenados, 0.95),
    peor: ordenados.length === 0 ? 0 : ordenados[ordenados.length - 1] ?? 0,
    largos: intervalos.filter(intervalo => intervalo > UMBRAL_CUADRO_MS).length,
    duracionMs: intervalos.reduce((total, intervalo) => total + intervalo, 0),
  }
}

/**
 * Verdict of a sample against the three agreed limits.
 *
 * @param muestra - Aggregated sample.
 * @returns Whether the run meets the threshold.
 */
export function veredictoDe(muestra: MuestraFluidez): 'cumple' | 'no-cumple' {
  const proporcionLargos = muestra.cuadros === 0 ? 1 : muestra.largos / muestra.cuadros
  const cumple
    = muestra.cuadros > 0
      && muestra.p95 <= UMBRAL_CUADRO_MS
      && muestra.peor <= PEOR_CUADRO_MS
      && proporcionLargos <= MAXIMO_CUADROS_LARGOS
  return cumple ? 'cumple' : 'no-cumple'
}

/**
 * Assembles the report from a run.
 *
 * @param intervalos - Milliseconds between consecutive frames.
 * @param entorno - Machine and viewport the run happened on.
 * @param momento - ISO instant of the run.
 * @returns The report, with the script version inside it.
 */
export function construirInforme(
  intervalos: readonly number[],
  entorno: EntornoMedicion,
  momento: string,
): InformeFluidez {
  const muestra = resumirIntervalos(intervalos)
  return {
    versionGuion: VERSION_GUION,
    pasos: PASOS_GUION,
    umbralMs: UMBRAL_CUADRO_MS,
    muestra,
    veredicto: veredictoDe(muestra),
    entorno,
    momento,
  }
}

/** Reads the environment of the current browser. */
function entornoActual(): EntornoMedicion {
  if (!import.meta.client) {
    return { navegador: '', plataforma: '', viewport: '', densidadPixel: 1 }
  }
  return {
    navegador: navigator.userAgent,
    plataforma: navigator.platform,
    viewport: `${window.innerWidth}x${window.innerHeight}`,
    densidadPixel: window.devicePixelRatio,
  }
}

/** What the measurement panel drives and shows. */
export interface MedidorFluidez {
  midiendo: Ref<boolean>
  informe: ShallowRef<InformeFluidez | null>
  /** Run the frozen script, one dispatch per animation frame. */
  medir: (aplicarPaso: (paso: PasoGuion) => void) => Promise<InformeFluidez>
}

/**
 * Frame meter and runner of the frozen script.
 *
 * @returns The in-flight flag, the last report and the operation that produces
 *   one.
 */
export function useMedidorFluidez(): MedidorFluidez {
  const midiendo = ref(false)
  const informe = shallowRef<InformeFluidez | null>(null)

  async function medir(aplicarPaso: (paso: PasoGuion) => void): Promise<InformeFluidez> {
    midiendo.value = true
    const intervalos: number[] = []

    try {
      let anterior = performance.now()
      for (const paso of GUION_ZOOM) {
        // One dispatch per animation frame: the browser is given the chance to
        // paint between steps, which is exactly what is being measured. Firing
        // the 180 steps in a loop would measure the loop.
        await new Promise<void>((resolver) => {
          requestAnimationFrame(() => resolver())
        })
        aplicarPaso(paso)
        const ahora = performance.now()
        intervalos.push(ahora - anterior)
        anterior = ahora
      }
    }
    finally {
      midiendo.value = false
    }

    const resultado = construirInforme(intervalos, entornoActual(), new Date().toISOString())
    informe.value = resultado
    return resultado
  }

  return { midiendo, informe, medir }
}
