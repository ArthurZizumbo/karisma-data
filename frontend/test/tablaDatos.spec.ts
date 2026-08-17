import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import { h } from 'vue'

import TablaDatos from '~/components/comun/TablaDatos.vue'
import { definirColumnas } from '~/utils/tablaDatos'

/**
 * US-A4-EXCELENCIA - the dense table of the portal, and its order.
 *
 * Seven tables were written by hand in this repository and not one of them
 * could be sorted; the design review measured 80 pixel rows where `DESIGN.md`
 * declares 34. What is asserted here is exactly those two things plus the one
 * that makes the order usable without a screen: the announcement.
 *
 * What is deliberately NOT asserted: that TanStack sorts correctly. Its own
 * suite covers that. What can break here is the seam -a handler wired to the
 * wrong column, an `aria-sort` written on a header that cannot be sorted, a
 * cell that stopped being a row header- and every case below names the defect
 * it would catch.
 */

interface Fila {
  readonly clave: string
  readonly fuente: string
  readonly registros: number
}

const FILAS: readonly Fila[] = Object.freeze([
  { clave: 'tesoreria', fuente: 'Tesorería', registros: 96310 },
  { clave: 'credito', fuente: 'Crédito', registros: 1284350 },
  { clave: 'depositos', fuente: 'Depósitos', registros: 7412 },
])

const COLUMNAS = definirColumnas<Fila>([
  {
    id: 'fuente',
    accessorFn: fila => fila.fuente,
    header: 'Fuente',
    sortFn: 'alphanumeric',
    meta: { encabezadoFila: true },
  },
  {
    id: 'registros',
    accessorFn: fila => fila.registros,
    header: 'Registros',
    sortFn: 'basic',
    meta: { alineacion: 'fin', clase: 'tabular-nums' },
    cell: ({ row }) => String(row.original.registros),
  },
  {
    id: 'acciones',
    header: 'Acciones',
    enableSorting: false,
    cell: () => h('button', { type: 'button' }, 'Abrir'),
  },
])

interface Opciones {
  filas?: readonly Fila[]
  vacio?: string
  titulo?: string
  ordenInicial?: { id: string, desc: boolean }[]
}

function montar(opciones: Opciones = {}) {
  return mount(TablaDatos, {
    props: {
      columnas: COLUMNAS,
      filas: opciones.filas ?? FILAS,
      vacio: opciones.vacio,
      titulo: opciones.titulo,
      ordenInicial: opciones.ordenInicial,
      idFila: (fila: Fila) => fila.clave,
      atributosFila: (fila: Fila) => ({ 'data-fuente': fila.clave }),
    },
    global: { stubs: { Icon: true } },
  })
}

/** The row headers in document order, which is the order the reader sees. */
function ordenEnPantalla(wrapper: ReturnType<typeof montar>): string[] {
  return wrapper.findAll('tbody tr').map(fila => fila.attributes('data-fuente') ?? '')
}

describe('la tabla anuncia su orden y no solo lo dibuja', () => {
  it('abre con aria-sort en none sobre las columnas ordenables', () => {
    // The defect: the attribute is written only once there is an order, so a
    // screen reader entering the table is told nothing about which columns can
    // be sorted, and the reader has to click one to find out.
    const encabezados = montar().findAll('th[scope="col"]')

    expect(encabezados.map(uno => uno.attributes('aria-sort'))).toEqual([
      'none',
      'none',
      undefined,
    ])
  })

  it('no declara aria-sort en la columna que no se puede ordenar', () => {
    // `aria-sort="none"` on every header announces a sortable column where
    // there is a column of buttons, and the reader who acts on the
    // announcement finds a header that does nothing.
    const acciones = montar().findAll('th[scope="col"]')[2]

    expect(acciones?.attributes('aria-sort')).toBeUndefined()
    expect(acciones?.find('[data-ordenar]').exists()).toBe(false)
  })

  it('invierte el sentido al pulsar dos veces la misma columna', async () => {
    // The defect this closes is the seam, not the algorithm: a handler taken
    // from the wrong column, or an announcement computed from the state of the
    // table instead of from the state of the column, leaves the arrow and the
    // word disagreeing.
    const wrapper = montar()
    const anuncio = (indice: number) =>
      wrapper.findAll('th[scope="col"]')[indice]?.attributes('aria-sort')

    await wrapper.get('[data-ordenar="fuente"]').trigger('click')
    expect(anuncio(0)).toBe('ascending')

    await wrapper.get('[data-ordenar="fuente"]').trigger('click')
    expect(anuncio(0)).toBe('descending')
  })

  it('abre una columna de cifras por el valor mas alto, y la de texto por la A', async () => {
    // Not a taste: the announcement has to say what the column actually did.
    // A header that reported `ascending` while the largest figure sat at the
    // top would be the one case where the word and the order disagree, and the
    // reader without a screen is the only one who would not notice.
    const wrapper = montar()

    await wrapper.get('[data-ordenar="registros"]').trigger('click')
    expect(wrapper.findAll('th[scope="col"]')[1]?.attributes('aria-sort')).toBe('descending')

    await wrapper.get('[data-ordenar="fuente"]').trigger('click')
    expect(wrapper.findAll('th[scope="col"]')[0]?.attributes('aria-sort')).toBe('ascending')
  })

  it('reordena las filas de verdad, y por la cifra y no por su texto', async () => {
    // An order that only moved the arrow would be a table lying twice: to the
    // eye and to the announcement. And an order computed over the printed text
    // would answer `Tesorería, Depósitos, Crédito`, which is the alphabet
    // walking backwards and not the magnitude of anything.
    const wrapper = montar()

    await wrapper.get('[data-ordenar="registros"]').trigger('click')

    expect(ordenEnPantalla(wrapper)).toEqual(['credito', 'tesoreria', 'depositos'])
  })

  it('respeta el orden inicial que recibe y no el del arreglo', () => {
    // A table opened by a screen that already knows how it wants to be read
    // -newest first- would otherwise show the order of the transport and move
    // under the reader on the first interaction.
    const wrapper = montar({ ordenInicial: [{ id: 'fuente', desc: true }] })

    expect(ordenEnPantalla(wrapper)).toEqual(['tesoreria', 'depositos', 'credito'])
    expect(wrapper.findAll('th[scope="col"]')[0]?.attributes('aria-sort')).toBe('descending')
  })

  it('sin orden pedido dibuja las filas como llegaron', () => {
    // The administration screen depends on this: an account just created is
    // where the API put it, and a default order would have moved it silently.
    expect(ordenEnPantalla(montar())).toEqual(['tesoreria', 'credito', 'depositos'])
  })
})

describe('la geometria de la fila es la que declara el sistema', () => {
  it('toma el alto de fila del token y nunca de un literal', () => {
    // Measured before this component existed: 80 pixel rows against the 34 the
    // system declares. A literal here would drift from the token the day the
    // system changes it, and every table would drift at a different pace.
    const wrapper = montar()
    const celdas = [
      ...wrapper.findAll('th[scope="col"]'),
      ...wrapper.findAll('tbody th, tbody td'),
    ]

    expect(celdas.length).toBeGreaterThan(0)
    for (const celda of celdas) {
      expect(celda.classes(), celda.text()).toContain('h-(--table-row-height)')
    }
  })

  it('la columna declarada como encabezado de fila es un th con scope row', () => {
    // Without it every figure of the row is announced against its column and
    // against nothing else, and the reader hears six numbers with no idea
    // which source they belong to. That is the whole reason these are tables.
    const wrapper = montar()
    const primeras = wrapper.findAll('tbody tr').map(fila => fila.element.firstElementChild)

    expect(primeras).toHaveLength(3)
    for (const celda of primeras) {
      expect(celda?.tagName).toBe('TH')
      expect(celda?.getAttribute('scope')).toBe('row')
    }
    expect(wrapper.findAll('tbody td')).toHaveLength(6)
  })

  it('lleva la clase de la columna al encabezado y al cuerpo a la vez', () => {
    // A rule or an alignment applied only to the body leaves a header one
    // column out of step with the figures under it.
    const wrapper = montar()

    expect(wrapper.findAll('th[scope="col"]')[1]?.classes()).toContain('tabular-nums')
    expect(wrapper.findAll('tbody td')[0]?.classes()).toContain('tabular-nums')
    expect(wrapper.findAll('tbody td')[0]?.classes()).toContain('text-right')
  })

  it('publica en la fila los atributos de su dueno, y sobreviven al orden', async () => {
    // The dashboard marks its projected row this way, and the mark has to
    // travel with the row: computed from the position it would land on
    // whichever month happened to be last after a sort, and the reader would
    // see a measurement labelled as a forecast.
    const wrapper = montar()

    await wrapper.get('[data-ordenar="fuente"]').trigger('click')

    expect(wrapper.findAll('tbody tr[data-fuente]')).toHaveLength(3)
    expect(ordenEnPantalla(wrapper)).toEqual(['credito', 'depositos', 'tesoreria'])
  })
})

describe('la tabla dice lo que pasa cuando no hay filas', () => {
  it('escribe la frase de vacio en lugar de un cuerpo en blanco', () => {
    // A header with nothing under it reads as a table still loading, and the
    // reader waits for rows that are never coming.
    const wrapper = montar({ filas: [], vacio: 'Ninguna fuente coincide.' })

    expect(wrapper.get('[data-tabla-vacia]').text()).toBe('Ninguna fuente coincide.')
    expect(wrapper.get('[data-tabla-vacia] td').attributes('colspan')).toBe('3')
    expect(wrapper.findAll('th[scope="col"]')).toHaveLength(3)
  })

  it('sin frase de vacio no inventa una fila', () => {
    // A row of dashes would be indistinguishable from data, and the caller
    // that has its own empty panel would end up showing two.
    const wrapper = montar({ filas: [] })

    expect(wrapper.find('[data-tabla-vacia]').exists()).toBe(false)
    expect(wrapper.findAll('tbody tr')).toHaveLength(0)
  })
})

describe('el consumidor con fila propia conserva el orden y el encabezado', () => {
  it('sustituye la fila entera y sigue recibiendo las filas ordenadas', async () => {
    // The administration screen renders an account with its role selector and
    // its destructive zone, so it owns the row. What it must not own is the
    // order: a slot fed from the untouched array would ignore the header the
    // reader just clicked.
    const wrapper = mount(TablaDatos, {
      props: {
        columnas: COLUMNAS,
        filas: FILAS,
        idFila: (fila: Fila) => fila.clave,
      },
      slots: {
        fila: `<tr :data-propia="params.fila.clave"><td>{{ params.fila.fuente }}</td></tr>`,
      },
      global: { stubs: { Icon: true } },
    })

    expect(wrapper.findAll('[data-propia]')).toHaveLength(3)

    await wrapper.get('[data-ordenar="registros"]').trigger('click')

    expect(wrapper.findAll('[data-propia]').map(fila => fila.attributes('data-propia')))
      .toEqual(['credito', 'tesoreria', 'depositos'])
  })
})
