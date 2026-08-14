import { describe, expect, it } from 'vitest'

import { formatearValor, formatearValorCompacto } from '~/utils/serieEstadisticas'

/**
 * US-025 — el formato de los numeros del tablero.
 *
 * Solo se prueba la forma corta y su frontera. La forma exacta la ejercita la
 * pantalla entera y no hace falta fijarla dos veces; lo que si hace falta fijar
 * es cuando el eje deja de escribir la cifra completa, porque es una decision
 * con dos modos de fallar en direcciones opuestas.
 */

describe('la forma corta del eje', () => {
  it('acorta el saldo, que llega al orden del billon', () => {
    // Sin esto, la etiqueta mide catorce caracteres, el eje se come un cuarto
    // del area de dibujo y quedan cinco cifras apiladas que nadie compara de un
    // vistazo. Es lo que se vio en el navegador antes de este cambio.
    const largo = formatearValor(3_623_584_268_288, 'saldo_disponible_mxn', 'en')
    const corto = formatearValorCompacto(3_623_584_268_288, 'saldo_disponible_mxn', 'en')

    expect(largo).not.toBeNull()
    expect(corto).not.toBeNull()
    expect(corto!.length).toBeLessThan(largo!.length / 2)
  })

  it('NO acorta un ratio, que vive entre cero y tres', () => {
    // El fallo en la otra direccion, y el peor de los dos: acortar 0.94 imprime
    // "0" y el eje pasa a mentir en vez de a ser incomodo.
    expect(formatearValorCompacto(0.94, 'ratio_lcr', 'es')).toBe(
      formatearValor(0.94, 'ratio_lcr', 'es'),
    )
  })

  it('deja que Intl elija la abreviatura de cada idioma', () => {
    // Una tabla de sufijos escrita a mano seria un segundo catalogo de
    // traduccion viviendo fuera de los locales, y divergiria el primer dia que
    // alguien afine uno de los dos.
    const en = formatearValorCompacto(2_500_000_000, 'saldo_disponible_mxn', 'en')
    const es = formatearValorCompacto(2_500_000_000, 'saldo_disponible_mxn', 'es')

    expect(en).not.toBeNull()
    expect(es).not.toBeNull()
    expect(en).not.toBe(es)
  })

  it('devuelve null en un hueco, igual que la forma exacta', () => {
    // El llamador pinta el hueco con una cadena traducida; un guion escrito
    // aqui seria un literal visible fuera de los catalogos.
    expect(formatearValorCompacto(Number.NaN, 'saldo_disponible_mxn', 'es')).toBeNull()
    expect(formatearValorCompacto(null, 'saldo_disponible_mxn', 'es')).toBeNull()
  })
})
