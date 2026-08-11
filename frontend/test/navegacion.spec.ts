import { describe, expect, it } from 'vitest'
import {
  claveDeRuta,
  CLAVE_AVISO_ALCANCE,
  CLAVES_FACETAS_TRANSVERSALES,
  MODULOS,
  moduloActivo,
  PROTOTIPOS,
  RUTA_ACCESO,
  RUTA_ASISTENTE,
  RUTA_GUIA,
  RUTA_INDICE,
  RUTAS_CONTRATO,
} from '~/utils/navegacion'
import { mensaje } from './i18nDePrueba'

const RUTAS_ESPERADAS = [
  '/acceso',
  '/inicio',
  '/exploracion',
  '/exploracion/exportar',
  '/exploracion/tableros',
  '/gobierno',
  '/administracion',
  '/asistente',
]

/** The three states of the A4 scope table. */
const ESTADOS_DE_ALCANCE = [
  'navegable-con-datos',
  'navegable-sin-datos',
  'roadmap',
] as const

describe('integridad del contrato de navegación', () => {
  it('declara las ocho rutas del contrato sin duplicados', () => {
    expect(RUTAS_CONTRATO).toHaveLength(8)
    expect(new Set(RUTAS_CONTRATO).size).toBe(8)
    expect([...RUTAS_CONTRATO].sort()).toEqual([...RUTAS_ESPERADAS].sort())
  })

  it('declara los cuatro módulos de primer nivel del mapa de A3', () => {
    expect(MODULOS).toHaveLength(4)
    expect(MODULOS.map(modulo => modulo.ruta)).toEqual([
      '/inicio',
      '/exploracion',
      '/gobierno',
      '/administracion',
    ])
  })

  it('cuelga cada subruta de la ruta de su módulo', () => {
    for (const modulo of MODULOS) {
      expect(modulo.subrutas.length).toBeGreaterThan(0)
      for (const subruta of modulo.subrutas) {
        expect(subruta.ruta.startsWith(modulo.ruta)).toBe(true)
        expect(subruta.id.startsWith(`${modulo.id}.`)).toBe(true)
      }
    }
  })

  it('no deja ninguna ruta fuera de una rama del mapa', () => {
    const rutasDeRamas = new Set([
      RUTA_ACCESO,
      RUTA_ASISTENTE,
      ...MODULOS.flatMap(modulo => [modulo.ruta, ...modulo.subrutas.map(sub => sub.ruta)]),
    ])
    for (const ruta of RUTAS_CONTRATO) {
      expect(rutasDeRamas.has(ruta)).toBe(true)
    }
  })

  it('no deja ninguna ruta del contrato por debajo de dos segmentos', () => {
    // This used to be called "two clicks or fewer" and it measures URL
    // segments, which is not the same thing: a leaf three clicks away behind a
    // one segment URL would have passed. The real click count is guaranteed by
    // the structure of the sidebar (module -> sub route) and is asserted in
    // BarraLateral.spec.ts, against the mounted DOM.
    for (const ruta of RUTAS_CONTRATO) {
      expect(ruta.split('/').filter(Boolean).length).toBeLessThanOrEqual(2)
    }
  })

  it('declara las nueve facetas transversales de A3', () => {
    expect(CLAVES_FACETAS_TRANSVERSALES).toHaveLength(9)
    expect(new Set(CLAVES_FACETAS_TRANSVERSALES).size).toBe(9)
  })

  it('marca facetas transversales en los cuatro módulos, no solo en el total', () => {
    // The previous version flattened the sub routes and asserted on the total,
    // so it claimed "per module" without checking it: it would only have failed
    // if every mark were deleted. Now they are grouped and each group is
    // required to hold.
    const porModulo = MODULOS.map(modulo => ({
      id: modulo.id,
      marcadas: modulo.subrutas.filter(sub => sub.facetaTransversal).length,
    }))

    for (const modulo of porModulo) {
      expect(modulo.marcadas, `el módulo ${modulo.id} no marca ninguna faceta`).toBeGreaterThan(0)
    }

    const total = porModulo.reduce((suma, modulo) => suma + modulo.marcadas, 0)
    expect(total).toBeLessThanOrEqual(CLAVES_FACETAS_TRANSVERSALES.length)
  })

  it('usa un texto de franja único y explícito sobre el alcance', () => {
    expect(mensaje('es', CLAVE_AVISO_ALCANCE)).toBe(
      'Prototipo de alta fidelidad de Karisma Data con datos sintéticos. '
      + 'No está conectado a sistemas reales de ninguna institución.',
    )
  })
})

describe('el contrato de navegación no guarda ninguna palabra suelta', () => {
  /** Every translation key the contract asks the catalogues to resolve. */
  const CLAVES_DEL_CONTRATO = [
    CLAVE_AVISO_ALCANCE,
    ...CLAVES_FACETAS_TRANSVERSALES,
    ...MODULOS.flatMap(modulo => [
      modulo.claveEtiqueta,
      ...modulo.subrutas.map(subruta => subruta.claveEtiqueta),
    ]),
    ...PROTOTIPOS.flatMap(prototipo => [prototipo.claveNombre, prototipo.claveRama]),
  ]

  it.each(CLAVES_DEL_CONTRATO)('resuelve %s en los dos catálogos', (clave) => {
    // A key added to es.json and forgotten in en.json renders the Spanish text
    // through the fallback and nobody notices until an evaluator switches the
    // language. `mensaje` throws when the key is absent, which is the point.
    expect(mensaje('es', clave)).not.toBe('')
    expect(mensaje('en', clave)).not.toBe('')
  })

  it('no deja ninguna etiqueta del árbol en español dentro del catálogo inglés', () => {
    const traducidas = CLAVES_DEL_CONTRATO.filter(
      clave => mensaje('es', clave) !== mensaje('en', clave),
    )

    // 'Karisma Data' is the only reader facing string that is identical in both
    // languages, and it is not part of the tree: every entry here must change.
    expect(traducidas).toHaveLength(CLAVES_DEL_CONTRATO.length)
  })
})

describe('índice de prototipos', () => {
  it('declara siete prototipos numerados de cero a seis', () => {
    expect(PROTOTIPOS).toHaveLength(7)
    expect(PROTOTIPOS.map(prototipo => prototipo.numero)).toEqual([0, 1, 2, 3, 4, 5, 6])
  })

  it('apunta cada prototipo a una ruta del contrato y con etiqueta de alcance', () => {
    for (const prototipo of PROTOTIPOS) {
      expect(RUTAS_CONTRATO).toContain(prototipo.ruta)
      // alcance is a union of three literals: comparing it against '' was an
      // unreachable assertion. What can actually break is somebody introducing
      // a state outside the three state table of A4.
      expect(ESTADOS_DE_ALCANCE).toContain(prototipo.alcance)
      expect(prototipo.claveRama).not.toBe('')
    }
  })

  it('deja tableros fuera del índice porque es zona de la pantalla de exploración', () => {
    expect(PROTOTIPOS.map(prototipo => prototipo.ruta)).not.toContain('/exploracion/tableros')
  })
})

describe('la guía de estilos entra como constante propia, no como octavo prototipo', () => {
  it('declara RUTA_GUIA con la dirección que el smoke recorre', () => {
    expect(RUTA_GUIA).toBe('/guia')
  })

  it('no la mete en el contrato de navegación, que sigue en ocho rutas', () => {
    // RUTAS_CONTRATO declares branches of the A3 site map and /guia is not one:
    // adding it there would claim a branch that the card sorting never produced
    // and would make `moduloActivo` and `claveDeRuta` answer for a route with no
    // label in either catalogue.
    expect(RUTAS_CONTRATO).toHaveLength(8)
    expect(RUTAS_CONTRATO).not.toContain(RUTA_GUIA)
  })

  it('no la cuenta como prototipo, que sigue en siete botones', () => {
    // The A4 rubric scores prototypes in one section and the style guide in
    // another. An eighth numbered button would move points from one to the
    // other and break the map the A3 deliverable already promised.
    expect(PROTOTIPOS).toHaveLength(7)
    expect(PROTOTIPOS.map(prototipo => prototipo.ruta)).not.toContain(RUTA_GUIA)
  })

  it('no la confunde con ninguna de las otras rutas sueltas', () => {
    expect(new Set([RUTA_INDICE, RUTA_ACCESO, RUTA_ASISTENTE, RUTA_GUIA]).size).toBe(4)
  })
})

describe('moduloActivo', () => {
  const CASOS: Array<[string, string | undefined]> = [
    ['/acceso', undefined],
    ['/inicio', '1'],
    ['/exploracion', '2'],
    ['/exploracion/tableros', '2'],
    ['/exploracion/exportar', '2'],
    ['/gobierno', '3'],
    ['/asistente', undefined],
    ['/administracion', '4'],
  ]

  it.each(CASOS)('resuelve %s al módulo esperado', (ruta, idEsperado) => {
    expect(moduloActivo(ruta)?.id).toBe(idEsperado)
  })

  it('excluye el índice, que no pertenece a ningún módulo', () => {
    expect(moduloActivo(RUTA_INDICE)).toBeUndefined()
    expect(moduloActivo('')).toBeUndefined()
  })

  it('ignora la barra final, la consulta y el fragmento', () => {
    expect(moduloActivo('/gobierno/')?.id).toBe('3')
    expect(moduloActivo('/exploracion/tableros?filtro=liquidez')?.id).toBe('2')
    expect(moduloActivo('/administracion#4.3')?.id).toBe('4')
  })

  it('no confunde un prefijo parcial con un módulo', () => {
    expect(moduloActivo('/inicios')).toBeUndefined()
  })
})

describe('claveDeRuta', () => {
  it.each(RUTAS_ESPERADAS)('devuelve una clave traducible para %s', (ruta) => {
    const clave = claveDeRuta(ruta)
    expect(clave).toBeTruthy()
    expect(mensaje('es', clave as string)).not.toBe('')
    expect(mensaje('en', clave as string)).not.toBe('')
  })

  it('devuelve la rama de A3, no la ruta, en los dos idiomas', () => {
    expect(mensaje('es', claveDeRuta('/exploracion/tableros') as string))
      .toBe('Tableros e indicadores')
    expect(mensaje('en', claveDeRuta('/exploracion/tableros') as string))
      .toBe('Dashboards and indicators')
    expect(mensaje('es', claveDeRuta('/gobierno') as string)).toBe('Gobierno del dato')
    expect(mensaje('en', claveDeRuta('/gobierno') as string)).toBe('Data governance')
  })

  it('no reconoce el índice como rama del mapa', () => {
    expect(claveDeRuta(RUTA_INDICE)).toBeUndefined()
  })
})
