import { describe, expect, it } from 'vitest'
import {
  AVISO_ALCANCE,
  etiquetaDeRuta,
  FACETAS_TRANSVERSALES,
  MODULOS,
  moduloActivo,
  PROTOTIPOS,
  RUTA_ACCESO,
  RUTA_ASISTENTE,
  RUTA_INDICE,
  RUTAS_CONTRATO,
} from '~/utils/navegacion'

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
    expect(FACETAS_TRANSVERSALES).toHaveLength(9)
    expect(new Set(FACETAS_TRANSVERSALES).size).toBe(9)
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
    expect(total).toBeLessThanOrEqual(FACETAS_TRANSVERSALES.length)
  })

  it('usa un texto de franja único y explícito sobre el alcance', () => {
    expect(AVISO_ALCANCE).toBe(
      'Prototipo de alta fidelidad de Karisma Data con datos sintéticos. '
      + 'No está conectado a sistemas reales de ninguna institución.',
    )
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
      expect(prototipo.ramaA3).not.toBe('')
    }
  })

  it('deja tableros fuera del índice porque es zona de la pantalla de exploración', () => {
    expect(PROTOTIPOS.map(prototipo => prototipo.ruta)).not.toContain('/exploracion/tableros')
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

describe('etiquetaDeRuta', () => {
  it.each(RUTAS_ESPERADAS)('devuelve un título no vacío para %s', (ruta) => {
    const etiqueta = etiquetaDeRuta(ruta)
    expect(etiqueta).toBeTruthy()
    expect(etiqueta?.length).toBeGreaterThan(0)
  })

  it('devuelve el nombre de la rama de A3, no la ruta', () => {
    expect(etiquetaDeRuta('/exploracion/tableros')).toBe('Tableros e indicadores')
    expect(etiquetaDeRuta('/exploracion/exportar')).toBe('Exportaciones')
    expect(etiquetaDeRuta('/gobierno')).toBe('Gobierno del dato')
  })

  it('no reconoce el índice como rama del mapa', () => {
    expect(etiquetaDeRuta(RUTA_INDICE)).toBeUndefined()
  })
})
