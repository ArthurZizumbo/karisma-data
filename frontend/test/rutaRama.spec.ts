import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { describe, expect, it } from 'vitest'
import { MODULOS } from '~/utils/navegacion'

/**
 * Every branch of the A3 map has to appear in the route table of the A4 PDF.
 *
 * The defect this guards against: the table of `a4_02_prototipos.tex` is typed
 * by hand and drops one of the sixteen sub branches, so the graded document
 * claims a coverage the navigation contract does not have. Nobody rereads a
 * twenty row table against a TypeScript literal, which is exactly why a machine
 * should.
 *
 * The hook is the branch identifier in the first cell of each row -`1.1`,
 * `2.4`, `4.3`- because that is what `MODULOS` declares and the only field of
 * the table that cannot be reworded. The `.tex` documents the agreement next to
 * its delimiters.
 *
 * Nothing here mounts a component. What it measures is a declaration.
 */

/** Delimiters the .tex writes around the machine read rows. */
const TABLA_INICIO = '% tabla-ruta-rama:inicio'
const TABLA_FIN = '% tabla-ruta-rama:fin'

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

const prototipos = leerDelRepositorio(
  '../../docs/entregables/contenido/a4_02_prototipos.tex',
  'Lo escribe US-UX-07 y es la seccion de prototipos del PDF de A4',
)

/** Body between the two delimiters, without the delimiters themselves. */
function cuerpoDeLaTabla(fuente: string): string {
  const inicio = fuente.indexOf(TABLA_INICIO)
  const fin = fuente.indexOf(TABLA_FIN)
  if (inicio === -1 || fin === -1 || fin < inicio) {
    throw new Error(
      `a4_02_prototipos.tex perdio los delimitadores ${TABLA_INICIO} / ${TABLA_FIN}, `
      + 'que son los que acotan la tabla ruta a rama que esta prueba lee',
    )
  }
  return fuente.slice(inicio + TABLA_INICIO.length, fin)
}

/**
 * Branch identifiers of the first cell of every data row.
 *
 * A data row is one that has cells and whose first one is an identifier: that
 * leaves out the comment lines, the environment opening -whose header cells
 * travel as an argument- and its closing.
 *
 * @param cuerpo Body of the table.
 */
function identificadoresPublicados(cuerpo: string): string[] {
  return cuerpo
    .split('\n')
    .filter(linea => !linea.trimStart().startsWith('%'))
    .filter(linea => linea.includes('&') && linea.includes('\\\\'))
    .map(linea => linea.split('&')[0]?.trim() ?? '')
    .filter(primera => /^\d+(\.\d+)?$/.test(primera))
}

/** The four modules and their sixteen sub branches, as the contract declares. */
const IDENTIFICADORES_DEL_CONTRATO = [
  ...MODULOS.map(modulo => modulo.id),
  ...MODULOS.flatMap(modulo => modulo.subrutas.map(subruta => subruta.id)),
]

describe('tabla ruta a rama del PDF de A4', () => {
  const publicados = identificadoresPublicados(cuerpoDeLaTabla(prototipos))

  it('publica los cuatro modulos y las dieciseis subramas del contrato', () => {
    expect(IDENTIFICADORES_DEL_CONTRATO).toHaveLength(20)
    expect([...publicados].sort()).toEqual([...IDENTIFICADORES_DEL_CONTRATO].sort())
  })

  it('no publica una rama dos veces', () => {
    expect(new Set(publicados).size).toBe(publicados.length)
  })
})
