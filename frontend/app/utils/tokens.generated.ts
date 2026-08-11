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

export interface TokenColor {
  readonly nombre: string
  readonly claro: string
  readonly oscuro: string
  readonly clase: string
  readonly informa: boolean
  readonly uso: string
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

export const SUPERFICIE: readonly TokenColor[] = [
  {
    nombre: 'ground',
    claro: '#F4F6F9',
    oscuro: '#0A0A0C',
    clase: 'bg-ground',
    informa: true,
    uso: 'Suelo de la pantalla. En oscuro es casi negro, nunca negro puro.',
  },
  {
    nombre: 'ground-alt',
    claro: '#EAEEF4',
    oscuro: '#131519',
    clase: 'bg-ground-alt',
    informa: true,
    uso: 'Fila alterna de tabla, cabecera de panel y celda agrupada.',
  },
  {
    nombre: 'grid',
    claro: '#DCE2EB',
    oscuro: '#1C2028',
    clase: 'bg-grid',
    informa: false,
    uso: 'La reticula visible del diagrama. Decorativa por definicion.',
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
  },
  {
    nombre: 'corriente-tenue',
    claro: '#7A8698',
    oscuro: '#7A8698',
    clase: 'bg-corriente-tenue',
    informa: true,
    uso: 'Texto secundario y nodo alcanzable. El unico token identico en los dos modos.',
  },
  {
    nombre: 'corriente-medio',
    claro: '#414B5B',
    oscuro: '#B4C2D4',
    clase: 'bg-corriente-medio',
    informa: true,
    uso: 'Conector recorrido, etiqueta de eje y borde de campo que informa.',
  },
  {
    nombre: 'corriente-pleno',
    claro: '#14171D',
    oscuro: '#E8F4FF',
    clase: 'bg-corriente-pleno',
    informa: true,
    uso: 'Corriente plena: texto de cuerpo, cifra de tabla y nodo activo.',
  },
]

export const SEMANTICOS: readonly TokenColor[] = [
  {
    nombre: 'error',
    claro: '#C4341A',
    oscuro: '#FF5A36',
    clase: 'bg-error',
    informa: true,
    uso: 'Error y accion destructiva. Siempre con icono de aspa.',
  },
  {
    nombre: 'aviso',
    claro: '#8A5A00',
    oscuro: '#FFC233',
    clase: 'bg-aviso',
    informa: true,
    uso: 'Aviso. Siempre con icono de triangulo.',
  },
  {
    nombre: 'ok',
    claro: '#1F6F43',
    oscuro: '#4ADE80',
    clase: 'bg-ok',
    informa: true,
    uso: 'Confirmacion. Siempre con icono de marca.',
  },
  {
    nombre: 'info',
    claro: '#1D4ED8',
    oscuro: '#7DD3FC',
    clase: 'bg-info',
    informa: true,
    uso: 'Informativo y enlace. Siempre subrayado o con icono.',
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
  },
  {
    nombre: 'serie-2',
    claro: '#B45309',
    oscuro: '#FFC233',
    clase: 'bg-serie-2',
    informa: true,
    uso: 'Serie 2. Marcador cuadrado, linea de guiones.',
  },
  {
    nombre: 'serie-3',
    claro: '#1F6F43',
    oscuro: '#4ADE80',
    clase: 'bg-serie-3',
    informa: true,
    uso: 'Serie 3. Marcador triangulo, linea de puntos.',
  },
  {
    nombre: 'serie-4',
    claro: '#6D28D9',
    oscuro: '#C4B5FD',
    clase: 'bg-serie-4',
    informa: true,
    uso: 'Serie 4. Marcador rombo, guion y punto.',
  },
  {
    nombre: 'serie-5',
    claro: '#0E7490',
    oscuro: '#67E8F9',
    clase: 'bg-serie-5',
    informa: true,
    uso: 'Serie 5. Marcador cruz, linea larga.',
  },
  {
    nombre: 'serie-6',
    claro: '#9D174D',
    oscuro: '#F9A8D4',
    clase: 'bg-serie-6',
    informa: true,
    uso: 'Serie 6. Marcador estrella, guion doble.',
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
]

export const TOKENS: readonly TokenColor[] = [
  ...SUPERFICIE,
  ...CORRIENTE,
  ...SEMANTICOS,
  ...SERIES,
]
