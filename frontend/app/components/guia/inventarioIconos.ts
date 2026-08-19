/**
 * Lucide inventory of the living design system.
 *
 * @nuxt/icon bundles what its scanner finds in the sources, and the scanner
 * cannot see a name assembled at run time: `:name="'lucide:' + clave"` renders
 * an empty box in a production build while looking correct under `nuxt dev`,
 * where the module still resolves through the Iconify API. That is why the
 * inventory lives in a plain module: `nuxt.config.ts` feeds NOMBRES_DE_ICONO to
 * `icon.clientBundle.icons` and LaminaIconos.vue walks this very same list, so
 * the bundle and the plate cannot disagree.
 *
 * Every entry names a function of the portal, never a shape. One family only,
 * per rule 3 of the interface checklist.
 */

/** One icon of the inventory, tied to the function it stands for. */
export interface EntradaIcono {
  /** Full Iconify name. Always inside the single Lucide family. */
  readonly nombre: string
  /** Translation key of the function, used as the accessible name. */
  readonly clave: string
}

/** A functional group of the inventory. */
export interface GrupoIconos {
  /** Translation key of the group heading. */
  readonly clave: string
  /** Icons that serve that function. */
  readonly entradas: readonly EntradaIcono[]
}

/** One of the three sizes the system allows for an icon. */
export interface TamanoIcono {
  /** Rendered size in pixels. */
  readonly px: number
  /** Tailwind class that renders it, written literally so the scanner sees it. */
  readonly clase: string
}

/** The inventory, grouped by what each icon is for. */
export const GRUPOS_DE_ICONOS: readonly GrupoIconos[] = Object.freeze([
  {
    clave: 'guide.icons.group.search',
    entradas: [
      { nombre: 'lucide:search', clave: 'guide.icons.item.search' },
      { nombre: 'lucide:list-filter', clave: 'guide.icons.item.filter' },
      { nombre: 'lucide:clock', clave: 'guide.icons.item.recent' },
      { nombre: 'lucide:star', clave: 'guide.icons.item.favorite' },
      { nombre: 'lucide:bell', clave: 'guide.icons.item.alert' },
    ],
  },
  {
    clave: 'guide.icons.group.data',
    entradas: [
      { nombre: 'lucide:table-2', clave: 'guide.icons.item.table' },
      { nombre: 'lucide:chart-column', clave: 'guide.icons.item.barChart' },
      { nombre: 'lucide:chart-line', clave: 'guide.icons.item.lineChart' },
      { nombre: 'lucide:database', clave: 'guide.icons.item.source' },
      { nombre: 'lucide:eye', clave: 'guide.icons.item.preview' },
    ],
  },
  {
    clave: 'guide.icons.group.governance',
    entradas: [
      { nombre: 'lucide:book-open', clave: 'guide.icons.item.dictionary' },
      { nombre: 'lucide:git-branch', clave: 'guide.icons.item.lineage' },
      { nombre: 'lucide:shield-check', clave: 'guide.icons.item.quality' },
      { nombre: 'lucide:users', clave: 'guide.icons.item.users' },
      { nombre: 'lucide:key', clave: 'guide.icons.item.credentials' },
    ],
  },
  {
    clave: 'guide.icons.group.actions',
    entradas: [
      { nombre: 'lucide:download', clave: 'guide.icons.item.export' },
      { nombre: 'lucide:file-spreadsheet', clave: 'guide.icons.item.spreadsheet' },
      { nombre: 'lucide:copy', clave: 'guide.icons.item.copy' },
      { nombre: 'lucide:trash-2', clave: 'guide.icons.item.delete' },
      { nombre: 'lucide:chevron-right', clave: 'guide.icons.item.drilldown' },
    ],
  },
  {
    clave: 'guide.icons.group.system',
    entradas: [
      { nombre: 'lucide:bot', clave: 'guide.icons.item.assistant' },
      { nombre: 'lucide:circle-check', clave: 'guide.icons.item.success' },
      { nombre: 'lucide:triangle-alert', clave: 'guide.icons.item.attention' },
      { nombre: 'lucide:circle-alert', clave: 'guide.icons.item.error' },
      { nombre: 'lucide:loader-circle', clave: 'guide.icons.item.loading' },
      { nombre: 'lucide:lock', clave: 'guide.icons.item.noPermission' },
      { nombre: 'lucide:languages', clave: 'guide.icons.item.language' },
    ],
  },
])

/**
 * Flat list of icon names, in inventory order.
 *
 * This is the array `icon.clientBundle.icons` receives. Deriving it instead of
 * writing it twice is the whole point: a new icon added to a group is bundled
 * without touching the configuration.
 */
export const NOMBRES_DE_ICONO: readonly string[] = Object.freeze(
  GRUPOS_DE_ICONOS.flatMap(grupo => grupo.entradas.map(entrada => entrada.nombre)),
)

/**
 * Icons the other plates render through a binding instead of a literal name.
 *
 * A chip that reads its icon from a data array, or a sort header that picks one
 * of two names with a ternary, is invisible to the scanner for the same reason
 * the inventory is. They are listed apart because the icon plate does not
 * document them: they belong to a component, not to the inventory.
 */
export const NOMBRES_AUXILIARES: readonly string[] = Object.freeze([
  'lucide:circle-dashed',
  'lucide:circle-slash',
  'lucide:info',
  'lucide:arrow-up-down',
  'lucide:arrow-up',
  'lucide:inbox',
  'lucide:trending-up',
])

/** Everything /guia can render, deduplicated. This is what gets bundled. */
export const NOMBRES_EMPAQUETADOS: readonly string[] = Object.freeze([
  ...new Set([...NOMBRES_DE_ICONO, ...NOMBRES_AUXILIARES]),
])

/**
 * The three sizes of the system.
 *
 * 16 px for a dense table cell, 20 px for a button or a chip and 24 px for a
 * card heading. Nothing else: a fourth size makes the optical weight of the
 * family drift between screens.
 */
export const TAMANOS_DE_ICONO: readonly TamanoIcono[] = Object.freeze([
  { px: 16, clase: 'size-4' },
  { px: 20, clase: 'size-5' },
  { px: 24, clase: 'size-6' },
])
