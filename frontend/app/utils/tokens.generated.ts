/**
 * Karisma Data - sistema de diseno del portal v2.0 - 2026-08-16
 *
 * GENERADO. No editar a mano: la siguiente corrida lo sobrescribe.
 *
 * Fuente:    design/sistema.py
 * Emisor:    design/emitir.py
 * Regenerar: make tokens
 *
 * El estilo del INFORME vive en docs/entregables/estilo/uxdoc.sty y es otro
 * sistema: esta cadena no lo lee ni lo escribe.
 */

export type TemaSistema = 'corriente' | 'institucional'

export type ModoSistema = 'claro' | 'oscuro'

export interface PaletaTema {
  readonly claro: string
  readonly oscuro: string
}

export interface TokenColor {
  readonly nombre: string
  /** Valor del TEMA DE OMISION, que es el que sostiene las capturas. */
  readonly claro: string
  readonly oscuro: string
  readonly clase: string
  readonly informa: boolean
  readonly uso: string
  /** El mismo token en cada tema, para la lamina comparativa. */
  readonly temas: Readonly<Record<TemaSistema, PaletaTema>>
}

export interface RolTipografico {
  readonly nombre: string
  readonly tamanoPx: number
  readonly interlineaPx: number
  readonly peso: number
  readonly familia: string
  readonly uso: string
}

export const VERSION_SISTEMA = 'v2.0'
export const FECHA_SISTEMA = '2026-08-16'

export const TEMAS: readonly TemaSistema[] = ['corriente', 'institucional']
export const TEMA_OMISION: TemaSistema = 'corriente'

/**
 * La familia tipografica es parte del eje del tema, no un interruptor
 * aparte: el tema de omision conserva Lexend Deca y Fira Sans y el
 * institucional usa Inter, que es lo que declara el archivo de diseno.
 */
export const FAMILIAS_POR_TEMA: Readonly<
  Record<TemaSistema, Readonly<Record<string, string>>>
> = {
  corriente: {
    display: '"Lexend Deca", system-ui, sans-serif',
    sans: '"Fira Sans", system-ui, sans-serif',
    mono: '"IBM Plex Mono", ui-monospace, monospace',
  },
  institucional: {
    display: '"Inter", system-ui, sans-serif',
    sans: '"Inter", system-ui, sans-serif',
    mono: '"IBM Plex Mono", ui-monospace, monospace',
  },
}

export const SUPERFICIE: readonly TokenColor[] = [
  {
    nombre: 'ground',
    claro: '#F4F6F9',
    oscuro: '#0A0A0C',
    clase: 'bg-ground',
    informa: true,
    uso: 'Suelo de la pantalla. En oscuro nunca es negro puro: casi negro en el tema de omision, azul profundo en el institucional.',
    temas: {
      corriente: { claro: '#F4F6F9', oscuro: '#0A0A0C' },
      institucional: { claro: '#FFFFFF', oscuro: '#0B1B2B' },
    },
  },
  {
    nombre: 'ground-alt',
    claro: '#EAEEF4',
    oscuro: '#131519',
    clase: 'bg-ground-alt',
    informa: true,
    uso: 'Fila alterna de tabla, cabecera de panel y celda agrupada.',
    temas: {
      corriente: { claro: '#EAEEF4', oscuro: '#131519' },
      institucional: { claro: '#F1F4F8', oscuro: '#102A43' },
    },
  },
  {
    nombre: 'grid',
    claro: '#DCE2EB',
    oscuro: '#1C2028',
    clase: 'bg-grid',
    informa: false,
    uso: 'Filete de un pelo: borde de tarjeta, separador de fila y linea de tabla.',
    temas: {
      corriente: { claro: '#DCE2EB', oscuro: '#1C2028' },
      institucional: { claro: '#DCE3EC', oscuro: '#1D3348' },
    },
  },
  {
    nombre: 'reticula',
    claro: '#DCE2EB',
    oscuro: '#1C2028',
    clase: 'bg-reticula',
    informa: false,
    uso: 'Cuadricula modular del chasis. Decorativa, y solo el tema de omision la pinta.',
    temas: {
      corriente: { claro: '#DCE2EB', oscuro: '#1C2028' },
      institucional: { claro: '#FFFFFF', oscuro: '#0B1B2B' },
    },
  },
]

export const CORRIENTE: readonly TokenColor[] = [
  {
    nombre: 'corriente-apagado',
    claro: '#A8B2C1',
    oscuro: '#4A5361',
    clase: 'bg-corriente-apagado',
    informa: false,
    uso: 'Conector en reposo. Filete decorativo: PROHIBIDO que informe (1.98:1 y 2.54:1).',
    temas: {
      corriente: { claro: '#A8B2C1', oscuro: '#4A5361' },
      institucional: { claro: '#A8B4C4', oscuro: '#46586B' },
    },
  },
  {
    nombre: 'corriente-tenue',
    claro: '#5F6A7D',
    oscuro: '#7A8698',
    clase: 'bg-corriente-tenue',
    informa: true,
    uso: 'Texto secundario y nodo alcanzable. En claro se oscurece para cumplir 4.5:1.',
    temas: {
      corriente: { claro: '#5F6A7D', oscuro: '#7A8698' },
      institucional: { claro: '#4A5A6E', oscuro: '#93A6BC' },
    },
  },
  {
    nombre: 'corriente-medio',
    claro: '#414B5B',
    oscuro: '#B4C2D4',
    clase: 'bg-corriente-medio',
    informa: true,
    uso: 'Conector recorrido, etiqueta de eje y borde de campo que informa.',
    temas: {
      corriente: { claro: '#414B5B', oscuro: '#B4C2D4' },
      institucional: { claro: '#1D4C6E', oscuro: '#BFD0E2' },
    },
  },
  {
    nombre: 'corriente-pleno',
    claro: '#14171D',
    oscuro: '#E8F4FF',
    clase: 'bg-corriente-pleno',
    informa: true,
    uso: 'Corriente plena: texto de cuerpo, cifra de tabla y nodo activo.',
    temas: {
      corriente: { claro: '#14171D', oscuro: '#E8F4FF' },
      institucional: { claro: '#102A43', oscuro: '#EAF2FA' },
    },
  },
]

export const ACCION: readonly TokenColor[] = [
  {
    nombre: 'accion',
    claro: '#14171D',
    oscuro: '#E8F4FF',
    clase: 'bg-accion',
    informa: true,
    uso: 'Accion primaria y seleccion: boton, fila elegida y pestana en curso.',
    temas: {
      corriente: { claro: '#14171D', oscuro: '#E8F4FF' },
      institucional: { claro: '#086B70', oscuro: '#3FB3B5' },
    },
  },
  {
    nombre: 'accion-apoyo',
    claro: '#414B5B',
    oscuro: '#B4C2D4',
    clase: 'bg-accion-apoyo',
    informa: true,
    uso: 'Realce de la accion: subrayado en curso, filete de foco y grafico de apoyo.',
    temas: {
      corriente: { claro: '#414B5B', oscuro: '#B4C2D4' },
      institucional: { claro: '#15989A', oscuro: '#5FD0D2' },
    },
  },
  {
    nombre: 'seleccion',
    claro: '#E7EAF0',
    oscuro: '#181B22',
    clase: 'bg-seleccion',
    informa: false,
    uso: 'Superficie elegida: fila marcada, tarjeta seleccionada y paso en curso.',
    temas: {
      corriente: { claro: '#E7EAF0', oscuro: '#181B22' },
      institucional: { claro: '#E6F2F1', oscuro: '#123443' },
    },
  },
]

export const SEMANTICOS: readonly TokenColor[] = [
  {
    nombre: 'error',
    claro: '#8C1D18',
    oscuro: '#FF5A36',
    clase: 'bg-error',
    informa: true,
    uso: 'Error y accion destructiva. Siempre con icono de aspa.',
    temas: {
      corriente: { claro: '#8C1D18', oscuro: '#FF5A36' },
      institucional: { claro: '#933632', oscuro: '#EC5B51' },
    },
  },
  {
    nombre: 'aviso',
    claro: '#9A6200',
    oscuro: '#FFC233',
    clase: 'bg-aviso',
    informa: true,
    uso: 'Aviso en texto. Siempre con icono de triangulo.',
    temas: {
      corriente: { claro: '#9A6200', oscuro: '#FFC233' },
      institucional: { claro: '#A36A10', oscuro: '#E8A33D' },
    },
  },
  {
    nombre: 'ok',
    claro: '#1F6F43',
    oscuro: '#4ADE80',
    clase: 'bg-ok',
    informa: true,
    uso: 'Confirmacion. Siempre con icono de marca.',
    temas: {
      corriente: { claro: '#1F6F43', oscuro: '#4ADE80' },
      institucional: { claro: '#287A58', oscuro: '#5FCB94' },
    },
  },
  {
    nombre: 'info',
    claro: '#6D28D9',
    oscuro: '#C4B5FD',
    clase: 'bg-info',
    informa: true,
    uso: 'Informativo y enlace. Siempre subrayado o con icono.',
    temas: {
      corriente: { claro: '#6D28D9', oscuro: '#C4B5FD' },
      institucional: { claro: '#17395B', oscuro: '#B9A7F2' },
    },
  },
]

export const SERIES: readonly TokenColor[] = [
  {
    nombre: 'serie-1',
    claro: '#1D4ED8',
    oscuro: '#7DD3FC',
    clase: 'bg-serie-1',
    informa: true,
    uso: 'Serie 1. Marcador circulo, linea continua.',
    temas: {
      corriente: { claro: '#1D4ED8', oscuro: '#7DD3FC' },
      institucional: { claro: '#1D4ED8', oscuro: '#7DD3FC' },
    },
  },
  {
    nombre: 'serie-2',
    claro: '#B45309',
    oscuro: '#FFC233',
    clase: 'bg-serie-2',
    informa: true,
    uso: 'Serie 2. Marcador cuadrado, linea de guiones.',
    temas: {
      corriente: { claro: '#B45309', oscuro: '#FFC233' },
      institucional: { claro: '#B45309', oscuro: '#FFC233' },
    },
  },
  {
    nombre: 'serie-3',
    claro: '#1F6F43',
    oscuro: '#4ADE80',
    clase: 'bg-serie-3',
    informa: true,
    uso: 'Serie 3. Marcador triangulo, linea de puntos.',
    temas: {
      corriente: { claro: '#1F6F43', oscuro: '#4ADE80' },
      institucional: { claro: '#1F6F43', oscuro: '#4ADE80' },
    },
  },
  {
    nombre: 'serie-4',
    claro: '#6D28D9',
    oscuro: '#C4B5FD',
    clase: 'bg-serie-4',
    informa: true,
    uso: 'Serie 4. Marcador rombo, guion y punto.',
    temas: {
      corriente: { claro: '#6D28D9', oscuro: '#C4B5FD' },
      institucional: { claro: '#6D28D9', oscuro: '#C4B5FD' },
    },
  },
  {
    nombre: 'serie-5',
    claro: '#0E7490',
    oscuro: '#67E8F9',
    clase: 'bg-serie-5',
    informa: true,
    uso: 'Serie 5. Marcador cruz, linea larga.',
    temas: {
      corriente: { claro: '#0E7490', oscuro: '#67E8F9' },
      institucional: { claro: '#0E7490', oscuro: '#67E8F9' },
    },
  },
  {
    nombre: 'serie-6',
    claro: '#9D174D',
    oscuro: '#F9A8D4',
    clase: 'bg-serie-6',
    informa: true,
    uso: 'Serie 6. Marcador estrella, guion doble.',
    temas: {
      corriente: { claro: '#9D174D', oscuro: '#F9A8D4' },
      institucional: { claro: '#9D174D', oscuro: '#F9A8D4' },
    },
  },
]

export const TIPOGRAFIA: readonly RolTipografico[] = [
  {
    nombre: 'display',
    tamanoPx: 40,
    interlineaPx: 44,
    peso: 600,
    familia: 'display',
    uso: 'Cifra unica que domina una pantalla.',
  },
  {
    nombre: 'titulo-1',
    tamanoPx: 28,
    interlineaPx: 34,
    peso: 600,
    familia: 'display',
    uso: 'Titulo de pantalla, uno por vista.',
  },
  {
    nombre: 'titulo-2',
    tamanoPx: 20,
    interlineaPx: 26,
    peso: 600,
    familia: 'display',
    uso: 'Titulo de panel y de lamina.',
  },
  {
    nombre: 'titulo-3',
    tamanoPx: 15,
    interlineaPx: 20,
    peso: 600,
    familia: 'sans',
    uso: 'Encabezado de grupo y de columna.',
  },
  {
    nombre: 'cuerpo',
    tamanoPx: 14,
    interlineaPx: 21,
    peso: 400,
    familia: 'sans',
    uso: 'Texto por omision de la interfaz densa.',
  },
  {
    nombre: 'cuerpo-amplio',
    tamanoPx: 16,
    interlineaPx: 26,
    peso: 400,
    familia: 'sans',
    uso: 'Parrafo largo: ayuda y respuesta del asistente.',
  },
  {
    nombre: 'etiqueta',
    tamanoPx: 12,
    interlineaPx: 16,
    peso: 500,
    familia: 'sans',
    uso: 'Etiqueta de campo y encabezado de tabla.',
  },
  {
    nombre: 'dato',
    tamanoPx: 16,
    interlineaPx: 22,
    peso: 500,
    familia: 'mono',
    uso: 'Cifra de tabla y de tarjeta, con cifras tabulares.',
  },
  {
    nombre: 'micro',
    tamanoPx: 11,
    interlineaPx: 15,
    peso: 500,
    familia: 'sans',
    uso: 'Nota al pie y leyenda de grafica.',
  },
]

export const REGLAS: readonly string[] = [
  'El estado se lee por luminancia. El color lo refuerza y nunca lo sustituye.',
  'No hay verde en la rampa de corriente: rojo contra verde separa dE=20.0 bajo protanopia, justo en el umbral.',
  'Todo semantico viaja con forma e icono. El color solo no distingue error de aviso: bajo protanopia separan dE=7.2 si se les deja solos.',
  'corriente-apagado y grid no informan nunca. Quedan por debajo de 3:1 a proposito, porque son filete y reticula, no limite de componente.',
  'El peso es un canal de jerarquia: 400 para texto corrido, 500 para etiquetas y cifras, 600 para titulares. Nueve roles con un solo peso no son nueve roles.',
  'La prosa no pasa de 68 caracteres por linea.',
  'La barra lateral colapsa de verdad por debajo de 768 px. El sistema anterior lo declaraba y no lo implementaba, y dejaba el contenido en 135 px.',
  'El tema cambia color Y familia tipografica, y los dos temas cumplen el mismo liston en los dos modos. Un tema opcional que rebajara el umbral seria una excepcion, no un tema.',
  'La paleta de series no cambia con el tema: es canal de datos, no identidad. Lo que si se vuelve a medir es su razon sobre el suelo de cada tema.',
]

export interface ParContraste {
  readonly token: string
  readonly tema: TemaSistema
  readonly modo: ModoSistema
  readonly ratio: number
  readonly veredicto: string
}

export interface SeparacionSemantica {
  readonly uno: string
  readonly otro: string
  readonly tema: TemaSistema
  readonly modo: ModoSistema
  readonly dicromacia: string
  readonly distancia: number
}

/**
 * La matriz completa: cada token sobre el suelo de SU tema y su modo.
 *
 * El suelo no es el mismo en los dos temas, ni siquiera dentro del
 * mismo modo, asi que una razon medida en uno no dice nada del otro.
 */
export const CONTRASTES_POR_TEMA: readonly ParContraste[] = [
  { token: 'ground-alt', tema: 'corriente', modo: 'claro', ratio: 1.08, veredicto: 'superficie' },
  { token: 'grid', tema: 'corriente', modo: 'claro', ratio: 1.2, veredicto: 'grafico' },
  { token: 'reticula', tema: 'corriente', modo: 'claro', ratio: 1.2, veredicto: 'grafico' },
  { token: 'corriente-apagado', tema: 'corriente', modo: 'claro', ratio: 1.98, veredicto: 'grafico' },
  { token: 'corriente-tenue', tema: 'corriente', modo: 'claro', ratio: 5.05, veredicto: 'AA' },
  { token: 'corriente-medio', tema: 'corriente', modo: 'claro', ratio: 8.14, veredicto: 'AAA' },
  { token: 'corriente-pleno', tema: 'corriente', modo: 'claro', ratio: 16.58, veredicto: 'AAA' },
  { token: 'accion', tema: 'corriente', modo: 'claro', ratio: 16.58, veredicto: 'AAA' },
  { token: 'accion-apoyo', tema: 'corriente', modo: 'claro', ratio: 8.14, veredicto: 'AAA' },
  { token: 'seleccion', tema: 'corriente', modo: 'claro', ratio: 1.11, veredicto: 'grafico' },
  { token: 'error', tema: 'corriente', modo: 'claro', ratio: 8.42, veredicto: 'AAA' },
  { token: 'aviso', tema: 'corriente', modo: 'claro', ratio: 4.71, veredicto: 'AA' },
  { token: 'ok', tema: 'corriente', modo: 'claro', ratio: 5.68, veredicto: 'AA' },
  { token: 'info', tema: 'corriente', modo: 'claro', ratio: 6.56, veredicto: 'AA' },
  { token: 'serie-1', tema: 'corriente', modo: 'claro', ratio: 6.19, veredicto: 'AA' },
  { token: 'serie-2', tema: 'corriente', modo: 'claro', ratio: 4.64, veredicto: 'AA' },
  { token: 'serie-3', tema: 'corriente', modo: 'claro', ratio: 5.68, veredicto: 'AA' },
  { token: 'serie-4', tema: 'corriente', modo: 'claro', ratio: 6.56, veredicto: 'AA' },
  { token: 'serie-5', tema: 'corriente', modo: 'claro', ratio: 4.95, veredicto: 'AA' },
  { token: 'serie-6', tema: 'corriente', modo: 'claro', ratio: 7.28, veredicto: 'AAA' },
  { token: 'ground-alt', tema: 'corriente', modo: 'oscuro', ratio: 1.08, veredicto: 'superficie' },
  { token: 'grid', tema: 'corriente', modo: 'oscuro', ratio: 1.21, veredicto: 'grafico' },
  { token: 'reticula', tema: 'corriente', modo: 'oscuro', ratio: 1.21, veredicto: 'grafico' },
  { token: 'corriente-apagado', tema: 'corriente', modo: 'oscuro', ratio: 2.54, veredicto: 'grafico' },
  { token: 'corriente-tenue', tema: 'corriente', modo: 'oscuro', ratio: 5.36, veredicto: 'AA' },
  { token: 'corriente-medio', tema: 'corriente', modo: 'oscuro', ratio: 10.93, veredicto: 'AAA' },
  { token: 'corriente-pleno', tema: 'corriente', modo: 'oscuro', ratio: 17.72, veredicto: 'AAA' },
  { token: 'accion', tema: 'corriente', modo: 'oscuro', ratio: 17.72, veredicto: 'AAA' },
  { token: 'accion-apoyo', tema: 'corriente', modo: 'oscuro', ratio: 10.93, veredicto: 'AAA' },
  { token: 'seleccion', tema: 'corriente', modo: 'oscuro', ratio: 1.15, veredicto: 'grafico' },
  { token: 'error', tema: 'corriente', modo: 'oscuro', ratio: 6.37, veredicto: 'AA' },
  { token: 'aviso', tema: 'corriente', modo: 'oscuro', ratio: 12.26, veredicto: 'AAA' },
  { token: 'ok', tema: 'corriente', modo: 'oscuro', ratio: 11.35, veredicto: 'AAA' },
  { token: 'info', tema: 'corriente', modo: 'oscuro', ratio: 10.71, veredicto: 'AAA' },
  { token: 'serie-1', tema: 'corriente', modo: 'oscuro', ratio: 11.86, veredicto: 'AAA' },
  { token: 'serie-2', tema: 'corriente', modo: 'oscuro', ratio: 12.26, veredicto: 'AAA' },
  { token: 'serie-3', tema: 'corriente', modo: 'oscuro', ratio: 11.35, veredicto: 'AAA' },
  { token: 'serie-4', tema: 'corriente', modo: 'oscuro', ratio: 10.71, veredicto: 'AAA' },
  { token: 'serie-5', tema: 'corriente', modo: 'oscuro', ratio: 13.65, veredicto: 'AAA' },
  { token: 'serie-6', tema: 'corriente', modo: 'oscuro', ratio: 10.91, veredicto: 'AAA' },
  { token: 'ground-alt', tema: 'institucional', modo: 'claro', ratio: 1.1, veredicto: 'superficie' },
  { token: 'grid', tema: 'institucional', modo: 'claro', ratio: 1.29, veredicto: 'grafico' },
  { token: 'reticula', tema: 'institucional', modo: 'claro', ratio: 1.0, veredicto: 'grafico' },
  { token: 'corriente-apagado', tema: 'institucional', modo: 'claro', ratio: 2.1, veredicto: 'grafico' },
  { token: 'corriente-tenue', tema: 'institucional', modo: 'claro', ratio: 7.05, veredicto: 'AAA' },
  { token: 'corriente-medio', tema: 'institucional', modo: 'claro', ratio: 9.09, veredicto: 'AAA' },
  { token: 'corriente-pleno', tema: 'institucional', modo: 'claro', ratio: 14.64, veredicto: 'AAA' },
  { token: 'accion', tema: 'institucional', modo: 'claro', ratio: 6.27, veredicto: 'AA' },
  { token: 'accion-apoyo', tema: 'institucional', modo: 'claro', ratio: 3.51, veredicto: 'AA-grande' },
  { token: 'seleccion', tema: 'institucional', modo: 'claro', ratio: 1.15, veredicto: 'grafico' },
  { token: 'error', tema: 'institucional', modo: 'claro', ratio: 7.46, veredicto: 'AAA' },
  { token: 'aviso', tema: 'institucional', modo: 'claro', ratio: 4.54, veredicto: 'AA' },
  { token: 'ok', tema: 'institucional', modo: 'claro', ratio: 5.23, veredicto: 'AA' },
  { token: 'info', tema: 'institucional', modo: 'claro', ratio: 11.85, veredicto: 'AAA' },
  { token: 'serie-1', tema: 'institucional', modo: 'claro', ratio: 6.7, veredicto: 'AA' },
  { token: 'serie-2', tema: 'institucional', modo: 'claro', ratio: 5.02, veredicto: 'AA' },
  { token: 'serie-3', tema: 'institucional', modo: 'claro', ratio: 6.15, veredicto: 'AA' },
  { token: 'serie-4', tema: 'institucional', modo: 'claro', ratio: 7.1, veredicto: 'AAA' },
  { token: 'serie-5', tema: 'institucional', modo: 'claro', ratio: 5.36, veredicto: 'AA' },
  { token: 'serie-6', tema: 'institucional', modo: 'claro', ratio: 7.88, veredicto: 'AAA' },
  { token: 'ground-alt', tema: 'institucional', modo: 'oscuro', ratio: 1.19, veredicto: 'superficie' },
  { token: 'grid', tema: 'institucional', modo: 'oscuro', ratio: 1.34, veredicto: 'grafico' },
  { token: 'reticula', tema: 'institucional', modo: 'oscuro', ratio: 1.0, veredicto: 'grafico' },
  { token: 'corriente-apagado', tema: 'institucional', modo: 'oscuro', ratio: 2.38, veredicto: 'grafico' },
  { token: 'corriente-tenue', tema: 'institucional', modo: 'oscuro', ratio: 6.98, veredicto: 'AA' },
  { token: 'corriente-medio', tema: 'institucional', modo: 'oscuro', ratio: 11.06, veredicto: 'AAA' },
  { token: 'corriente-pleno', tema: 'institucional', modo: 'oscuro', ratio: 15.41, veredicto: 'AAA' },
  { token: 'accion', tema: 'institucional', modo: 'oscuro', ratio: 6.9, veredicto: 'AA' },
  { token: 'accion-apoyo', tema: 'institucional', modo: 'oscuro', ratio: 9.49, veredicto: 'AAA' },
  { token: 'seleccion', tema: 'institucional', modo: 'oscuro', ratio: 1.33, veredicto: 'grafico' },
  { token: 'error', tema: 'institucional', modo: 'oscuro', ratio: 5.13, veredicto: 'AA' },
  { token: 'aviso', tema: 'institucional', modo: 'oscuro', ratio: 8.07, veredicto: 'AAA' },
  { token: 'ok', tema: 'institucional', modo: 'oscuro', ratio: 8.67, veredicto: 'AAA' },
  { token: 'info', tema: 'institucional', modo: 'oscuro', ratio: 8.19, veredicto: 'AAA' },
  { token: 'serie-1', tema: 'institucional', modo: 'oscuro', ratio: 10.44, veredicto: 'AAA' },
  { token: 'serie-2', tema: 'institucional', modo: 'oscuro', ratio: 10.79, veredicto: 'AAA' },
  { token: 'serie-3', tema: 'institucional', modo: 'oscuro', ratio: 9.99, veredicto: 'AAA' },
  { token: 'serie-4', tema: 'institucional', modo: 'oscuro', ratio: 9.43, veredicto: 'AAA' },
  { token: 'serie-5', tema: 'institucional', modo: 'oscuro', ratio: 12.01, veredicto: 'AAA' },
  { token: 'serie-6', tema: 'institucional', modo: 'oscuro', ratio: 9.6, veredicto: 'AAA' },
]

/** La matriz del tema de omision, que es la que publica el PDF. */
export const CONTRASTES: readonly ParContraste[] = CONTRASTES_POR_TEMA.filter(
  (par) => par.tema === 'corriente',
)

export const SEPARACIONES_POR_TEMA: readonly SeparacionSemantica[] = [
  { uno: 'error', otro: 'aviso', tema: 'corriente', modo: 'claro', dicromacia: 'deuteranopia', distancia: 22.1 },
  { uno: 'error', otro: 'ok', tema: 'corriente', modo: 'claro', dicromacia: 'protanopia', distancia: 16.7 },
  { uno: 'error', otro: 'info', tema: 'corriente', modo: 'claro', dicromacia: 'tritanopia', distancia: 62.1 },
  { uno: 'aviso', otro: 'ok', tema: 'corriente', modo: 'claro', dicromacia: 'protanopia', distancia: 32.3 },
  { uno: 'aviso', otro: 'info', tema: 'corriente', modo: 'claro', dicromacia: 'tritanopia', distancia: 37.6 },
  { uno: 'ok', otro: 'info', tema: 'corriente', modo: 'claro', dicromacia: 'tritanopia', distancia: 13.6 },
  { uno: 'error', otro: 'aviso', tema: 'corriente', modo: 'oscuro', dicromacia: 'deuteranopia', distancia: 21.5 },
  { uno: 'error', otro: 'ok', tema: 'corriente', modo: 'oscuro', dicromacia: 'protanopia', distancia: 26.1 },
  { uno: 'error', otro: 'info', tema: 'corriente', modo: 'oscuro', dicromacia: 'tritanopia', distancia: 77.9 },
  { uno: 'aviso', otro: 'ok', tema: 'corriente', modo: 'oscuro', dicromacia: 'protanopia', distancia: 33.9 },
  { uno: 'aviso', otro: 'info', tema: 'corriente', modo: 'oscuro', dicromacia: 'tritanopia', distancia: 33.6 },
  { uno: 'ok', otro: 'info', tema: 'corriente', modo: 'oscuro', dicromacia: 'tritanopia', distancia: 30.4 },
  { uno: 'error', otro: 'aviso', tema: 'institucional', modo: 'claro', dicromacia: 'tritanopia', distancia: 20.7 },
  { uno: 'error', otro: 'ok', tema: 'institucional', modo: 'claro', dicromacia: 'protanopia', distancia: 14.5 },
  { uno: 'error', otro: 'info', tema: 'institucional', modo: 'claro', dicromacia: 'protanopia', distancia: 45.4 },
  { uno: 'aviso', otro: 'ok', tema: 'institucional', modo: 'claro', dicromacia: 'protanopia', distancia: 37.8 },
  { uno: 'aviso', otro: 'info', tema: 'institucional', modo: 'claro', dicromacia: 'tritanopia', distancia: 54.3 },
  { uno: 'ok', otro: 'info', tema: 'institucional', modo: 'claro', dicromacia: 'tritanopia', distancia: 22.8 },
  { uno: 'error', otro: 'aviso', tema: 'institucional', modo: 'oscuro', dicromacia: 'deuteranopia', distancia: 22.6 },
  { uno: 'error', otro: 'ok', tema: 'institucional', modo: 'oscuro', dicromacia: 'protanopia', distancia: 23.3 },
  { uno: 'error', otro: 'info', tema: 'institucional', modo: 'oscuro', dicromacia: 'tritanopia', distancia: 67.6 },
  { uno: 'aviso', otro: 'ok', tema: 'institucional', modo: 'oscuro', dicromacia: 'protanopia', distancia: 37.8 },
  { uno: 'aviso', otro: 'info', tema: 'institucional', modo: 'oscuro', dicromacia: 'tritanopia', distancia: 35.3 },
  { uno: 'ok', otro: 'info', tema: 'institucional', modo: 'oscuro', dicromacia: 'tritanopia', distancia: 25.9 },
]

export const SEPARACIONES: readonly SeparacionSemantica[] = SEPARACIONES_POR_TEMA.filter(
  (s) => s.tema === 'corriente',
)

/**
 * Peor separacion semantica por tema y modo, DERIVADA del calculo.
 *
 * Estuvo escrita a mano y se desincronizo del computo: declaraba 13.4
 * donde la medicion daba 13.6, que es el mismo defecto que este sistema
 * existe para impedir. Una prueba lo detecto y ahora no puede repetirse.
 */
export const PEOR_SEPARACION_POR_TEMA = {
  corriente: {
    claro: 13.6,
    oscuro: 21.5,
  },
  institucional: {
    claro: 14.5,
    oscuro: 22.6,
  },
} as const

/** La del tema de omision, que es la que el informe reproduce. */
export const PEOR_SEPARACION = PEOR_SEPARACION_POR_TEMA.corriente

export const TOKENS: readonly TokenColor[] = [
  ...SUPERFICIE,
  ...CORRIENTE,
  ...ACCION,
  ...SEMANTICOS,
  ...SERIES,
]
