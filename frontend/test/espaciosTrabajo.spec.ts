import type { ClaveComposicion } from '~/types/espacios'

import { describe, expect, it } from 'vitest'

import {
  bloquesDe,
  destinosDe,
  ESPACIOS,
  espacioDeRol,
  RUTA_ADMINISTRACION,
  RUTA_INICIO,
} from '~/utils/espaciosTrabajo'
import { rolAlcanza } from '~/utils/guarda'
import { RUTAS_CONTRATO } from '~/utils/navegacion'
import {
  ALERTAS,
  BUSQUEDAS_RECIENTES,
  CONSULTAS_GUARDADAS,
  EXPORTACIONES,
  FAVORITOS,
  INDICADORES,
  INSTANTE_DE_REFERENCIA,
} from '~/utils/muestrasInicio'
import { SCOPE_POR_RUTA } from '~/utils/permisos.generated'
import { ROLES } from '~/utils/sesion'

/**
 * US-027 — the composition contract, checked without mounting Vue.
 *
 * What is asserted here is the part of the User Story that cannot be seen in a
 * screenshot: that the four roles are covered, that the three compositions are
 * really three and not one name repeated, and that no shortcut on the home
 * screen leads anywhere the reader cannot go. The templates are measured
 * against this contract in `test/inicio.spec.ts`, which is what keeps a layout
 * change from silently rewriting the criterion it was supposed to satisfy.
 */

const COMPOSICIONES: readonly ClaveComposicion[] = ['operativo', 'analista', 'directivo']

/** Sample dates of every collection, which must all sit before the frozen clock. */
const FECHAS_DE_MUESTRA = [
  ...BUSQUEDAS_RECIENTES,
  ...FAVORITOS,
  ...ALERTAS,
  ...EXPORTACIONES,
  ...CONSULTAS_GUARDADAS,
]
  .map(elemento => elemento.fecha)
  .filter((fecha): fecha is string => fecha !== undefined)
  .concat(INDICADORES.map(indicador => indicador.fecha))

describe('los cuatro espacios cubren a los cuatro roles', () => {
  it('declara un espacio por rol y ninguno de mas', () => {
    // A fifth workspace, or a role left without one, would send that reader to
    // `espacioDeRol`'s fallback and give them somebody else's home screen while
    // every other test stayed green.
    expect(ESPACIOS.map(espacio => espacio.clave)).toEqual([...ROLES])
  })

  it('aterriza en una ruta que alguna pagina sirve de verdad', () => {
    // A landing route with no page file turns a correct login into a 404: the
    // reader types the right password and the product looks broken on the very
    // first click.
    for (const espacio of ESPACIOS) {
      expect(RUTAS_CONTRATO, espacio.clave).toContain(espacio.pantallaPrincipal)
    }
  })

  it('deja al administrador como el unico que no aterriza en inicio', () => {
    const fuera = ESPACIOS.filter(espacio => espacio.pantallaPrincipal !== RUTA_INICIO)

    expect(fuera.map(espacio => espacio.clave)).toEqual(['admin'])
    expect(fuera[0]?.pantallaPrincipal).toBe(RUTA_ADMINISTRACION)
  })

  it('da al administrador que abre inicio la composicion operativa', () => {
    // `/inicio` is not forbidden to the administrator -forbidding routes is the
    // guard's job and this one is not on its list- so the screen has to resolve
    // to something. The most general composition is the honest answer; a blank
    // screen would read as a failure.
    expect(espacioDeRol('admin').composicion).toBe('operativo')
  })

  it.each([null, undefined])('resuelve al espacio operativo sin sesion (%s)', (rol) => {
    // During the first server pass the guard has not answered yet. Returning
    // undefined here would leave the home screen blank in the served HTML.
    expect(espacioDeRol(rol).clave).toBe('operativo')
  })
})

describe('las tres composiciones son tres y no un nombre repetido', () => {
  it('no comparte el conjunto de bloques entre ninguna pareja', () => {
    // This is the defect that empties the whole User Story: three labels over
    // the same screen. Compared pairwise so the failure names the pair.
    for (const [indice, primera] of COMPOSICIONES.entries()) {
      for (const segunda of COMPOSICIONES.slice(indice + 1)) {
        expect([...bloquesDe(primera)], `${primera} vs ${segunda}`).not.toEqual([
          ...bloquesDe(segunda),
        ])
      }
    }
  })

  it('abre la operativa con el buscador y la directiva con los indicadores', () => {
    // The literal criterion of the scope: search first for the operative
    // profile, indicators first for the executive one. A block reordered "for
    // balance" loses it without breaking anything visible.
    expect(bloquesDe('operativo')[0]).toBe('buscador')
    expect(bloquesDe('directivo')[0]).toBe('indicadores')
  })

  it('abre la analista con el explorador y las exportaciones, en ese orden', () => {
    expect(bloquesDe('analista').slice(0, 2)).toEqual(['explorador', 'exportaciones'])
  })

  it('ofrece el buscador en las tres, con tres pesos distintos', () => {
    // The silent degradation this catches is the one where every composition
    // ends up with the same dominant search box and the three workspaces become
    // one with three titles.
    const enfasis = COMPOSICIONES.map(
      composicion => ESPACIOS.find(espacio => espacio.clave === composicion)!.enfasisBuscador,
    )

    for (const composicion of COMPOSICIONES) {
      expect(bloquesDe(composicion), composicion).toContain('buscador')
    }
    expect(enfasis).toEqual(['dominante', 'normal', 'reducido'])
  })

  it('reserva el bloque de perfil a la composicion operativa', () => {
    const conPerfil = COMPOSICIONES.filter(composicion => bloquesDe(composicion).includes('perfil'))

    expect(conPerfil).toEqual(['operativo'])
  })

  it('no repite un bloque dentro de una misma composicion', () => {
    // A duplicated block renders the same list twice and, worse, makes the DOM
    // order assertion of the templates ambiguous.
    for (const composicion of COMPOSICIONES) {
      const bloques = bloquesDe(composicion)

      expect(new Set(bloques).size, composicion).toBe(bloques.length)
    }
  })
})

describe('ninguna composicion ofrece una puerta que se cierra', () => {
  it('enlaza solo a rutas del contrato de navegacion', () => {
    // A link to `/dashboard` or `/exportar` written from memory answers 404 in
    // the middle of the demonstration.
    for (const composicion of COMPOSICIONES) {
      for (const destino of destinosDe(composicion)) {
        expect(RUTAS_CONTRATO, `${composicion} -> ${destino}`).toContain(destino)
      }
    }
  })

  it('no enlaza a administracion desde ninguna de las tres', () => {
    // The administration module demands the `admin` scope, and none of the
    // three compositions is rendered for that role alone. Offering the link
    // would be the home screen inviting the reader to a door the guard closes
    // in their face.
    for (const composicion of COMPOSICIONES) {
      expect(destinosDe(composicion), composicion).not.toContain(RUTA_ADMINISTRACION)
    }
  })

  it('solo enlaza a rutas que el rol de esa composicion alcanza', () => {
    // The general form of the rule above, read from the generated permission
    // map: the analyst composition may point at the export screen because the
    // analyst reaches it, and the operative one may not.
    for (const composicion of COMPOSICIONES) {
      for (const destino of destinosDe(composicion)) {
        expect(
          rolAlcanza(composicion, SCOPE_POR_RUTA[destino] ?? null),
          `${composicion} -> ${destino}`,
        ).toBe(true)
      }
    }
  })
})

describe('las muestras no dependen del reloj', () => {
  it('ancla toda fecha de ejemplo antes del instante de referencia', () => {
    // With dates relative to `Date.now()` the figure captured for the report on
    // Saturday would not match the one captured on Wednesday, and an item dated
    // after the frozen clock would read as a search made in the future.
    const referencia = Date.parse(INSTANTE_DE_REFERENCIA)

    expect(FECHAS_DE_MUESTRA.length).toBeGreaterThan(10)
    for (const fecha of FECHAS_DE_MUESTRA) {
      expect(Number.isNaN(Date.parse(fecha)), fecha).toBe(false)
      expect(Date.parse(fecha), fecha).toBeLessThanOrEqual(referencia)
    }
  })

  it('sirve las cuatro tarjetas de indicador y las cinco busquedas que el alcance pide', () => {
    // The criterion names the floor: at least four indicator cards for the
    // executive, and five recent searches for the operative reader. A
    // collection trimmed while refactoring changes the shape of the captured
    // figure and drops the screen below the criterion.
    expect(INDICADORES.length).toBeGreaterThanOrEqual(4)
    expect(BUSQUEDAS_RECIENTES).toHaveLength(5)
  })

  it('cada indicador declara su unidad, su corte y su salida', () => {
    // The card receives sentences, so a figure without a unit or without a
    // cut-off would render a card with a blank line where the reader looks for
    // the provenance of the number -and the composition would still mount.
    for (const indicador of INDICADORES) {
      expect(indicador.claveEtiqueta, indicador.id).toMatch(/^workspace\./)
      expect(Number.isFinite(indicador.valor), indicador.id).toBe(true)
      expect(Number.isNaN(Date.parse(indicador.fecha)), indicador.id).toBe(false)
      expect(indicador.destino, indicador.id).not.toBe('')
    }
  })
})
