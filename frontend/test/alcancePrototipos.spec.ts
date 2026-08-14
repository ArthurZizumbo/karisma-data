import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { describe, expect, it } from 'vitest'
import type { EstadoAlcance } from '~/types/navegacion'
import { PROTOTIPOS } from '~/utils/navegacion'

/**
 * The scope table of the A4 deliverable has to say what the code says.
 *
 * The defect this guards against is concrete and cheap to commit: someone
 * changes `PROTOTIPOS[i].alcance` after the screens freeze and does not touch
 * `a4_05_alcance.tex`, or edits the table and not the code. Either way the
 * graded document ends up claiming a reach the prototype does not have, which
 * is the one failure mode the scope table exists to prevent.
 *
 * The comparison runs against the printed Spanish label and not against a
 * hidden marker on purpose: what an evaluator reads is the label, so that is
 * what has to match. Renaming a label without renaming its counterpart here
 * fails, which is the intended cost of touching published vocabulary.
 *
 * Nothing here mounts a component. What it measures is a declaration.
 */

/** Delimiters the .tex writes around the seven machine read rows. */
const TABLA_INICIO = '% tabla-alcance:inicio'
const TABLA_FIN = '% tabla-alcance:fin'

/** Printed label of each scope value, exactly as the table prints it. */
const ETIQUETA_PUBLICADA: Readonly<Record<EstadoAlcance, string>> = Object.freeze({
  'navegable-con-datos': 'Navegable con datos de ejemplo',
  'navegable-sin-datos': 'Navegable sin datos',
  'roadmap': 'En hoja de ruta',
})

/**
 * Reads a file of the repository.
 *
 * The path travels as a variable on purpose: with a literal, Vite rewrites the
 * `new URL(..., import.meta.url)` pattern into an asset reference and the URL
 * stops being a file one.
 *
 * @param relativa Path of the input, relative to this spec.
 * @param origen Who writes it, for the error message.
 */
function leerDelRepositorio(relativa: string, origen: string): string {
  const ruta = fileURLToPath(new URL(relativa, import.meta.url))
  try {
    return readFileSync(ruta, 'utf8')
  }
  catch {
    // Explicit rather than an `undefined` three assertions later: a check that
    // silently skips when its input is missing is not a barrier.
    throw new Error(`falta ${relativa}, que es el insumo de esta prueba. ${origen}`)
  }
}

const alcance = leerDelRepositorio(
  '../../docs/entregables/contenido/a4_05_alcance.tex',
  'Lo escribe US-UX-07 y es la seccion de alcance del PDF de A4',
)

/** Body between the two delimiters, without the delimiters themselves. */
function cuerpoDeLaTabla(fuente: string): string {
  const inicio = fuente.indexOf(TABLA_INICIO)
  const fin = fuente.indexOf(TABLA_FIN)
  if (inicio === -1 || fin === -1 || fin < inicio) {
    throw new Error(
      `a4_05_alcance.tex perdio los delimitadores ${TABLA_INICIO} / ${TABLA_FIN}, `
      + 'que son los que acotan las siete filas que esta prueba lee',
    )
  }
  return fuente.slice(inicio + TABLA_INICIO.length, fin)
}

/**
 * Scope label published for a route, read from its row.
 *
 * The route is matched with its closing brace so that `/exploracion` does not
 * also match the row of `/exploracion/exportar`.
 *
 * @param cuerpo Body of the table.
 * @param ruta Route as `PROTOTIPOS` declares it.
 */
function etiquetaDeLaFila(cuerpo: string, ruta: string): string {
  const marca = `\\texttt{${ruta}} &`
  const linea = cuerpo
    .split('\n')
    .find(candidata => candidata.includes(marca))
  if (linea === undefined) {
    throw new Error(`la tabla de alcance no tiene fila para ${ruta}`)
  }
  const celdas = linea.split('&').map(celda => celda.trim())
  const etiqueta = celdas[2]
  if (etiqueta === undefined) {
    throw new Error(`la fila de ${ruta} no llega a la tercera celda, que es la del alcance`)
  }
  return etiqueta
}

describe('alcance publicado en el PDF de A4', () => {
  const cuerpo = cuerpoDeLaTabla(alcance)

  it('publica una fila por prototipo y ninguna de mas', () => {
    const filas = cuerpo
      .split('\n')
      .filter(linea => linea.includes('\\texttt{/'))
    expect(filas).toHaveLength(PROTOTIPOS.length)
  })

  it.each(PROTOTIPOS.map(prototipo => [prototipo.ruta, prototipo.alcance] as const))(
    'la fila de %s publica el alcance que el codigo declara',
    (ruta, declarado) => {
      expect(etiquetaDeLaFila(cuerpo, ruta)).toBe(ETIQUETA_PUBLICADA[declarado])
    },
  )
})
