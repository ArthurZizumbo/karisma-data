import { readFileSync, readdirSync } from 'node:fs'
import { join, relative } from 'node:path'
import { fileURLToPath } from 'node:url'

import { describe, expect, it } from 'vitest'

import {
  ANILLO_FOCO,
  ANILLO_FOCO_CONGELADO,
  ANILLO_FOCO_INTERNO,
  ANILLO_FOCO_INVERSO,
} from '~/utils/foco'
import { FAMILIAS } from '~/utils/tokens.generated'

/**
 * QA of 11-ago-2026, finding 2 — three focus rings and none of them the real one.
 *
 * The button plate froze the state in primary-700, the field plate used the
 * primary with a one pixel offset, and the fifteen controls of the portal
 * painted a third ring. The plates captured into the A4 document a ring the
 * prototype never produced. The retired class names are not spelled out here:
 * Tailwind also scans the specs and would emit CSS for them.
 *
 * What fails here, concretely: a component that writes its own ring instead of
 * importing it, a frozen plate state that stops matching the ring the browser
 * paints, or a ring repainted in a colour other than the one `uxdoc.sty`
 * declares for it.
 */

/**
 * Resolves a path of the repository.
 *
 * The path arrives as a variable on purpose: with a literal, Vite rewrites the
 * `new URL(..., import.meta.url)` pattern into an asset reference and the URL
 * stops being a file one.
 */
function rutaDelRepositorio(relativa: string): string {
  return fileURLToPath(new URL(relativa, import.meta.url))
}

const RAIZ_APP = rutaDelRepositorio('../app')

function fuentesVue(): { archivo: string, texto: string }[] {
  const recorrer = (directorio: string): string[] =>
    readdirSync(directorio, { withFileTypes: true }).flatMap(entrada =>
      entrada.isDirectory()
        ? recorrer(join(directorio, entrada.name))
        : [join(directorio, entrada.name)],
    )

  return recorrer(RAIZ_APP)
    .filter(ruta => ruta.endsWith('.vue'))
    .map(ruta => ({
      archivo: relative(RAIZ_APP, ruta).replace(/\\/g, '/'),
      texto: readFileSync(ruta, 'utf8'),
    }))
}

/** Colour of every `--color-*` token of the generated theme. */
function coloresDelTema(): Map<string, string> {
  const tema = readFileSync(rutaDelRepositorio('../app/assets/css/main.css'), 'utf8')

  return new Map(
    [...tema.matchAll(/^\s+--color-([a-z0-9-]+)\s*:\s*(#[0-9A-Fa-f]{6})/gm)].map(
      ([, nombre, hex]) => [nombre!, hex!.toUpperCase()],
    ),
  )
}

describe('el anillo de foco tiene una sola definición', () => {
  it('congela exactamente el anillo que el navegador pinta', () => {
    // A frozen state that drifts from the live one is the whole defect: the
    // plate would document, and capture into the PDF, a ring no control paints.
    expect(ANILLO_FOCO_CONGELADO).toBe(ANILLO_FOCO.replaceAll('focus-visible:', ''))
  })

  it('usa el color que uxdoc.sty declara como anillo de foco', () => {
    const declarado = FAMILIAS.flatMap(familia => familia.tonos).filter(tono =>
      tono.uso.toLowerCase().includes('anillo de foco'),
    )

    expect(declarado.map(tono => tono.nombre)).toEqual(['primary-500'])

    // `outline-primary` resolves through the alias of the generated theme. If
    // the ring ever went back to primary-700, or the alias moved, these two
    // hexadecimals would stop matching and nothing else would notice.
    const colores = coloresDelTema()

    expect(ANILLO_FOCO.endsWith('outline-primary')).toBe(true)
    expect(colores.get('primary')).toBe(declarado[0]!.hex.toUpperCase())
  })

  it('mantiene el grosor y el desplazamiento en las cuatro variantes', () => {
    for (const anillo of [ANILLO_FOCO, ANILLO_FOCO_INVERSO, ANILLO_FOCO_INTERNO]) {
      expect(anillo).toContain('focus-visible:outline-2')
      expect(anillo).toContain('focus-visible:outline-offset-')
    }
  })

  it('no deja ningún componente escribiendo su propio anillo', () => {
    // Any `outline-*` utility typed into a template is, by construction, a ring
    // that the plate does not document: the four rings of the system live in
    // app/utils/foco.ts and reach the markup through an import.
    const propios = fuentesVue()
      .filter(({ texto }) => /outline-/.test(texto))
      .map(({ archivo }) => archivo)

    expect(propios).toEqual([])
  })
})
