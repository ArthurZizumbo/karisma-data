import type { VueWrapper } from '@vue/test-utils'

import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'

import { mount } from '@vue/test-utils'
import { defineComponent } from 'vue'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import {
  GRUPOS_DE_ICONOS,
  NOMBRES_DE_ICONO,
  NOMBRES_EMPAQUETADOS,
  TAMANOS_DE_ICONO,
} from '~/components/guia/inventarioIconos'
import Guia from '~/pages/guia.vue'
import Indice from '~/pages/index.vue'
import { RUTA_GUIA } from '~/utils/navegacion'
import {
  CONTRASTES,
  FAMILIAS,
  HALLAZGOS,
  NEUTROS,
  SEMANTICOS,
  SERIES,
} from '~/utils/tokens.generated'
import { type CodigoIdioma, crearI18nDePrueba, mensaje } from './i18nDePrueba'

/**
 * US-UX-09, ola B — the /guia route as a verifiable contract.
 *
 * The plates are the source of figures 14 to 16 of the A4 document, so what is
 * pinned here is what the capture script selects by and what the rubric counts:
 * the eight plates, the seventeen button cells, the six field states, the five
 * semantic chips and the four tool call states. The assertions on hexadecimals
 * are the ones that keep the application and the PDF from diverging.
 *
 * `Icon` is a global component of @nuxt/icon and does not exist outside Nuxt. It
 * is replaced by a double that consumes only the `name` prop, so every other
 * attribute -data-icono, role, aria-label- is the one the plate wrote, not one
 * the double invented.
 */

/**
 * Reads a file of the repository.
 *
 * The path arrives as a variable on purpose: with a literal, Vite rewrites the
 * `new URL(..., import.meta.url)` pattern into an asset reference and the URL
 * stops being a file one.
 */
function leerDelRepositorio(relativa: string): string {
  return readFileSync(fileURLToPath(new URL(relativa, import.meta.url)), 'utf8')
}

const IconoStub = defineComponent({
  props: { name: { type: String, required: true } },
  template: '<span :data-icono-nombre="name"></span>',
})

const EnlaceStub = defineComponent({
  props: { to: { type: String, required: true } },
  template: '<a :href="to"><slot /></a>',
})

/** Meta captured from the `definePageMeta` call of the mounted page. */
let metaDeclarada: Record<string, unknown> | undefined

beforeEach(() => {
  metaDeclarada = undefined
  vi.stubGlobal('definePageMeta', (meta: Record<string, unknown>) => {
    metaDeclarada = meta
  })

  return () => {
    vi.unstubAllGlobals()
  }
})

function montarGuia(idioma: CodigoIdioma = 'es'): VueWrapper {
  return mount(Guia, {
    global: {
      plugins: [crearI18nDePrueba(idioma)],
      components: { Icon: IconoStub, NuxtLink: EnlaceStub },
    },
  })
}

/** The 37 colour tokens the generator emits, flattened. */
const TOKENS = [...FAMILIAS.flatMap(familia => familia.tonos), ...NEUTROS, ...SEMANTICOS, ...SERIES]

/** Every hexadecimal the generated module authorises the page to print. */
const HEX_GENERADOS = new Set([
  ...TOKENS.map(token => token.hex),
  ...CONTRASTES.flatMap(par => [par.frenteHex, par.fondoHex]),
  ...HALLAZGOS.flatMap(hallazgo => [
    hallazgo.par.frenteHex,
    hallazgo.par.fondoHex,
    hallazgo.sustituto.frenteHex,
    hallazgo.sustituto.fondoHex,
  ]),
])

const LAMINAS_ESPERADAS = [
  'paleta',
  'tipografia',
  'botones',
  'campos',
  'tablas',
  'tarjetas',
  'iconos',
  'accesibilidad',
]

/** Heading key of each plate, resolved from the catalogues and not retyped. */
const CLAVE_DE_LAMINA: Record<string, string> = {
  paleta: 'guide.plate.palette',
  tipografia: 'guide.plate.typography',
  botones: 'guide.plate.buttons',
  campos: 'guide.plate.fields',
  tablas: 'guide.plate.tables',
  tarjetas: 'guide.plate.cards',
  iconos: 'guide.plate.icons',
  accesibilidad: 'guide.plate.accessibility',
}

describe('la ruta /guia arma las ocho láminas del sistema', () => {
  it('declara el layout del portal, que es donde vive la franja de alcance', () => {
    montarGuia()

    // Without the portal layout the guide would render with no scope banner and
    // the capture could be read as a live system.
    expect(metaDeclarada?.layout).toBe('portal')
  })

  it('marca la ruta con la constante que el smoke recorre', () => {
    expect(montarGuia().get('[data-ruta]').attributes('data-ruta')).toBe(RUTA_GUIA)
  })

  it('monta las ocho láminas, cada una con su data-lamina', () => {
    // The capture script selects by this attribute. A renamed or missing plate
    // leaves a figure of the document without a source.
    const laminas = montarGuia()
      .findAll('[data-lamina]')
      .map(lamina => lamina.attributes('data-lamina'))

    expect(laminas).toEqual(LAMINAS_ESPERADAS)
  })

  it('enlaza el índice de la página con cada lámina que existe', () => {
    const wrapper = montarGuia()
    const anclas = wrapper
      .findAll('[data-indice-lamina]')
      .map(ancla => ancla.attributes('data-indice-lamina'))

    expect(anclas).toEqual(LAMINAS_ESPERADAS)
    for (const id of LAMINAS_ESPERADAS) {
      expect(wrapper.find(`#lamina-${id}`).exists()).toBe(true)
    }
  })

  it('no deja la página sin un único encabezado de primer nivel', () => {
    expect(montarGuia().findAll('h1')).toHaveLength(1)
  })
})

describe('los hexadecimales impresos salen del generador, no del teclado', () => {
  it('no imprime ningún hexadecimal ajeno a tokens.generated.ts', () => {
    // This is CA-11 turned into a test. A colour typed into a plate looks right
    // on screen and still makes the interface diverge from the PDF, and nothing
    // else in the suite would notice.
    const impresos = [...new Set(montarGuia().text().match(/#[0-9A-Fa-f]{6}/g) ?? [])]

    expect(impresos.length).toBeGreaterThan(0)
    expect(impresos.filter(hex => !HEX_GENERADOS.has(hex))).toEqual([])
  })

  it('imprime a la vista el valor de los 37 tokens de color', () => {
    const texto = montarGuia().text()

    for (const token of TOKENS) {
      expect(texto, token.nombre).toContain(token.hex)
    }
  })

  it('rotula cada muestra de la paleta con su propio token y su propio valor', () => {
    // An off by one in the loop would copy the neighbour's value while the
    // swatch kept looking correct.
    const muestras = montarGuia().findAll('[data-token]')

    expect(muestras).toHaveLength(TOKENS.length)
    for (const [indice, muestra] of muestras.entries()) {
      const token = TOKENS[indice]!
      expect(muestra.attributes('data-token')).toBe(token.nombre)
      expect(muestra.attributes('aria-label')).toContain(token.hex)
      expect(muestra.attributes('aria-label')).toContain(token.nombre)
    }
  })
})

describe('la matriz de botones tiene diecisiete celdas y ningún hueco', () => {
  it('rinde las tres variantes por cinco estados más la destructiva y la de carga', () => {
    const celdas = montarGuia()
      .findAll('[data-boton-celda]')
      .map(celda => celda.attributes('data-boton-celda'))

    expect(celdas).toHaveLength(17)
    expect(new Set(celdas).size).toBe(17)

    for (const variante of ['contenido', 'contorno', 'texto']) {
      for (const estado of ['reposo', 'puntero', 'foco', 'activo', 'deshabilitado']) {
        expect(celdas, `${variante}-${estado}`).toContain(`${variante}-${estado}`)
      }
    }
    expect(celdas).toContain('destructiva-reposo')
    expect(celdas).toContain('contenido-carga')
  })

  it('deshabilita de verdad las celdas que dice deshabilitadas', () => {
    // A cell that only looked disabled would still take the click and the focus,
    // and the guide would document a state the product does not have.
    const wrapper = montarGuia()

    for (const id of ['contenido-deshabilitado', 'contorno-deshabilitado', 'texto-deshabilitado']) {
      expect(wrapper.get(`[data-boton-celda="${id}"] button`).attributes('disabled')).toBeDefined()
    }
    const carga = wrapper.get('[data-boton-celda="contenido-carga"] button')
    expect(carga.attributes('disabled')).toBeDefined()
    expect(carga.attributes('aria-busy')).toBe('true')
  })
})

describe('los campos publican sus seis estados y respetan el hallazgo 4', () => {
  it('rinde los seis estados de campo', () => {
    const estados = montarGuia()
      .findAll('[data-campo-estado]')
      .map(campo => campo.attributes('data-campo-estado'))

    expect(estados).toEqual([
      'reposo',
      'foco',
      'relleno',
      'error',
      'deshabilitado',
      'solo-lectura',
    ])
  })

  it('nunca dibuja un borde de campo con el filete decorativo', () => {
    // Finding 4 of the contrast matrix: `line` reaches 1.42:1 over the surface,
    // so a field bordered with it has, for measuring purposes, no border. The
    // regression is one character away -`border-line` instead of
    // `border-line-strong`- and it is invisible to the eye.
    const campos = montarGuia().findAll('[data-campo-estado] input')

    expect(campos).toHaveLength(6)
    for (const campo of campos) {
      expect(campo.classes(), campo.attributes('id')).not.toContain('border-line')
    }
  })

  it('ata el campo inválido a su mensaje de error', () => {
    const wrapper = montarGuia()
    const campo = wrapper.get('[data-campo-estado="error"] input')

    expect(campo.attributes('aria-invalid')).toBe('true')
    const descrito = campo.attributes('aria-describedby')
    expect(descrito).toBeTruthy()
    expect(wrapper.get(`#${descrito}`).text()).toBe(mensaje('es', 'guide.fields.error'))
  })

  it('rinde las cinco semánticas de chip y las cuatro insignias de rol', () => {
    const wrapper = montarGuia()

    expect(wrapper.findAll('[data-chip]').map(chip => chip.attributes('data-chip'))).toEqual([
      'neutro',
      'informativo',
      'correcto',
      'aviso',
      'rechazo',
    ])
    expect(
      wrapper.findAll('[data-badge-rol]').map(insignia => insignia.attributes('data-badge-rol')),
    ).toEqual(['operativo', 'analista', 'directivo', 'administrador'])
  })
})

describe('la tabla ordena de verdad y lo anuncia', () => {
  it('arranca ordenada por importe descendente y lo dice en aria-sort', () => {
    const wrapper = montarGuia()

    expect(wrapper.get('[data-columna="importe"]').attributes('aria-sort')).toBe('descending')
    expect(wrapper.get('[data-columna="registros"]').attributes('aria-sort')).toBe('none')
    expect(wrapper.findAll('[data-fila]')[0]!.attributes('data-fila')).toBe('credito')
  })

  it('mueve las filas y el aria-sort al pulsar otro encabezado', async () => {
    // Two defects hide here: a header that paints an arrow without sorting, and
    // a sort that reorders the rows without moving `aria-sort`, which leaves a
    // screen reader unable to tell which column is ordered.
    const wrapper = montarGuia()

    await wrapper.get('[data-columna="registros"] button').trigger('click')

    expect(wrapper.get('[data-columna="registros"]').attributes('aria-sort')).toBe('ascending')
    expect(wrapper.get('[data-columna="importe"]').attributes('aria-sort')).toBe('none')
    expect(wrapper.findAll('[data-fila]')[0]!.attributes('data-fila')).toBe('operacion')
  })
})

describe('las tarjetas publican los cuatro estados no felices y los cuatro de consulta', () => {
  it('acompaña la tarjeta de indicador de sus cuatro estados', () => {
    const tarjetas = montarGuia()
      .findAll('[data-tarjeta]')
      .map(tarjeta => tarjeta.attributes('data-tarjeta'))

    expect(tarjetas).toEqual(['kpi', 'carga', 'vacio', 'error', 'sin-permiso'])
  })

  it('rinde los cuatro momentos de la tarjeta de consulta del asistente', () => {
    const estados = montarGuia()
      .findAll('[data-tool-call]')
      .map(tarjeta => tarjeta.attributes('data-tool-call'))

    expect(estados).toEqual(['anuncio', 'ejecucion', 'resultado', 'error'])
  })

  it('etiqueta la cifra proyectada como simulada', () => {
    // Honesty of the demo: a projected figure without its label reads as a
    // measurement.
    expect(montarGuia().get('[data-tarjeta="kpi"]').text()).toContain(
      mensaje('es', 'guide.cards.kpi.footnote'),
    )
  })
})

describe('la iconografía se nombra y se empaqueta', () => {
  it('recorre el inventario completo en los tres tamaños', () => {
    const iconos = montarGuia().findAll('[data-icono]')

    expect(iconos).toHaveLength(NOMBRES_DE_ICONO.length * TAMANOS_DE_ICONO.length)
    expect(NOMBRES_DE_ICONO).toHaveLength(
      GRUPOS_DE_ICONOS.reduce((suma, grupo) => suma + grupo.entradas.length, 0),
    )
  })

  it('da nombre accesible a todo icono que va solo y esconde el decorativo', () => {
    // An icon that carries meaning on its own and has no accessible name is
    // silence for a screen reader; a decorative one that is announced is noise.
    for (const icono of montarGuia().findAll('[data-icono-nombre]')) {
      if (icono.attributes('data-icono') === undefined) {
        expect(icono.attributes('aria-hidden'), icono.attributes('data-icono-nombre')).toBe('true')
        continue
      }
      expect(icono.text().trim()).toBe('')
      expect(icono.attributes('role')).toBe('img')
      expect(icono.attributes('aria-label')?.trim()).toBeTruthy()
    }
  })

  it('declara en el empaquetado todo icono que la guía renderiza', () => {
    // The gotcha of @nuxt/icon: `clientBundle.scan` reads literal names out of
    // the sources and cannot see one assembled at run time. An icon fed from a
    // data array and not declared here renders through the Iconify API under
    // `nuxt dev` and ships as a hole in the production build, which is exactly
    // where the A4 captures are taken.
    const renderizados = new Set(
      montarGuia()
        .findAll('[data-icono-nombre]')
        .map(icono => icono.attributes('data-icono-nombre')!),
    )

    expect(renderizados.size).toBeGreaterThan(0)
    for (const nombre of renderizados) {
      expect(NOMBRES_EMPAQUETADOS, nombre).toContain(nombre)
    }
  })

  it('mantiene una sola familia de iconos', () => {
    for (const nombre of NOMBRES_EMPAQUETADOS) {
      expect(nombre.startsWith('lucide:'), nombre).toBe(true)
    }
  })

  it('pasa el inventario a nuxt.config, que es lo que empaqueta el build', () => {
    // Without this line in the configuration the plate is complete in dev and
    // empty in production, and no other test in the suite reads the config.
    const configuracion = leerDelRepositorio('../nuxt.config.ts')

    expect(configuracion).toContain('icons: [...NOMBRES_EMPAQUETADOS]')
    expect(configuracion).toContain('scan: true')
  })
})

describe('la lámina de accesibilidad publica los cuatro hallazgos y la matriz', () => {
  it('imprime los cuatro hallazgos con su par medido y su sustituto', () => {
    const wrapper = montarGuia()
    const hallazgos = wrapper.findAll('[data-hallazgo]')

    expect(hallazgos).toHaveLength(HALLAZGOS.length)
    for (const [indice, hallazgo] of hallazgos.entries()) {
      const emitido = HALLAZGOS[indice]!
      expect(hallazgo.attributes('data-hallazgo')).toBe(String(emitido.numero))
      expect(hallazgo.text()).toContain(emitido.par.ratio.toFixed(2))
      expect(hallazgo.text()).toContain(emitido.sustituto.ratio.toFixed(2))
    }
  })

  it('imprime la matriz completa que el generador midió', () => {
    // The count is the point: a plate that showed a hand picked subset would let
    // the pair that fails disappear from the document.
    expect(montarGuia().findAll('[data-par-contraste]')).toHaveLength(CONTRASTES.length)
  })
})

describe('la guía habla los dos idiomas', () => {
  it('traduce el encabezado y los rótulos de componente al inglés', () => {
    // A Spanish literal left in a template renders the same sentence in both
    // languages, and only a comparison against the two catalogues catches it.
    const texto = montarGuia('en').text()

    expect(texto).toContain(mensaje('en', 'guide.title'))
    expect(texto).not.toContain(mensaje('es', 'guide.title'))
    expect(texto).toContain(mensaje('en', 'guide.buttons.label.filled'))
    expect(texto).not.toContain(mensaje('es', 'guide.buttons.label.filled'))
    for (const id of LAMINAS_ESPERADAS) {
      const clave = CLAVE_DE_LAMINA[id]!
      expect(texto, clave).toContain(mensaje('en', clave))
    }
  })
})

describe('el índice enlaza la guía sin contarla como prototipo', () => {
  it('la ofrece en un bloque propio, fuera de los siete botones', () => {
    // If the guide were added as an eighth numbered button it would move points
    // from the prototype section of the rubric to the style guide one, and the
    // A3 site map would gain a branch that the card sorting never produced.
    const wrapper = mount(Indice, {
      global: {
        plugins: [crearI18nDePrueba()],
        components: { NuxtLink: EnlaceStub, Icon: IconoStub },
      },
    })

    const bloque = wrapper.get('[data-guia]')
    expect(bloque.get('a').attributes('href')).toBe(RUTA_GUIA)
    expect(bloque.find('[data-prototipo]').exists()).toBe(false)
    expect(wrapper.findAll('[data-prototipo]')).toHaveLength(7)
  })
})
