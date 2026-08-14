"""Machine manifest and generated data/README.md.

Both documents are rendered from measurements of the files that were actually
written, never from the intention of the generator. The README carries no
generation date on purpose: a timestamp would put ``git diff --exit-code
data/README.md`` in red on every run and would destroy the idempotence gate.
"""

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Final

from ml.data.anomalies import (
    ANOMALY_RATE,
    LABELS_ES,
    AnomalyKind,
    audited_kinds,
    predicate_es,
)
from ml.data.schemas import (
    BUCKETS_VENC,
    DIAS_HABILES,
    DIVISAS,
    FX_MXN,
    N_SERIES,
    SERIE_TABLERO,
    SILOS,
    UNIDADES_NEGOCIO,
)

# Rows the July catalog described for the three systems. The reduction of the
# S4 scope is declared against this number instead of being called "reduced".
CATALOGO_JULIO_FILAS: Final[int] = 6_500_000

_CABECERA: Final[str] = (
    "<!-- Generado por `make data`. No editar a mano: la siguiente corrida lo "
    "reescribe. -->"
)


@dataclass(frozen=True, slots=True)
class SiloReport:
    """What one written silo actually contains."""

    name: str
    path: Path
    rows: int
    columns: int
    size_bytes: int
    sha256: str
    anomalies: dict[AnomalyKind, int]

    @property
    def total_anomalies(self) -> int:
        """Return the anomalies measured over the written file."""
        return sum(self.anomalies.values())


@dataclass(frozen=True, slots=True)
class SerieReport:
    """What the written series actually contains."""

    path: Path
    meta_path: Path
    rows: int
    dates: int
    series: int
    date_min: str
    date_max: str
    sha256: str


@dataclass(frozen=True, slots=True)
class GenerationReport:
    """The whole run, and the only input of the rendered documents."""

    seed: int
    silos: tuple[SiloReport, ...]
    serie: SerieReport | None

    @property
    def total_rows(self) -> int:
        """Return the rows written across the three silos."""
        return sum(silo.rows for silo in self.silos)

    @property
    def total_anomalies(self) -> int:
        """Return the anomalies measured across the three silos."""
        return sum(silo.total_anomalies for silo in self.silos)

    @property
    def anomaly_rate(self) -> float:
        """Return the measured anomaly rate, zero when nothing was written."""
        if self.total_rows == 0:
            return 0.0
        return self.total_anomalies / self.total_rows

    @property
    def is_complete(self) -> bool:
        """Whether the run covers the three silos at their declared volume.

        Only a complete run may rewrite the versioned README: a partial one
        would publish 180 rows where the document says 180 000.
        """
        escritos = {silo.name: silo.rows for silo in self.silos}
        if set(escritos) != set(SILOS):
            return False
        if any(escritos[nombre] != SILOS[nombre].rows for nombre in SILOS):
            return False
        return self.serie is not None and self.serie.rows == SERIE_TABLERO.rows


def sha256_of(path: Path) -> str:
    """Return the hexadecimal digest of a file, read in blocks.

    Args:
        path: File to hash.

    Returns:
        The lowercase hexadecimal digest.
    """
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_manifest(report: GenerationReport, out_dir: Path) -> Path:
    """Write the machine readable manifest next to the silos.

    Args:
        report: Measurements of the run.
        out_dir: Data directory that holds silos/ and aggregates/.

    Returns:
        The path of the written manifest.
    """
    payload: dict[str, object] = {
        "semilla": report.seed,
        "filas_totales": report.total_rows,
        "anomalias_totales": report.total_anomalies,
        "tasa_anomalias": report.anomaly_rate,
        "silos": [
            {
                "nombre": silo.name,
                "archivo": silo.path.name,
                "sistema_origen": SILOS[silo.name].source_system,
                "responsable": SILOS[silo.name].owner,
                "filas": silo.rows,
                "columnas": silo.columns,
                "bytes": silo.size_bytes,
                "sha256": silo.sha256,
                "anomalias": {
                    kind.value: silo.anomalies[kind]
                    for kind in AnomalyKind
                    if kind in audited_kinds(silo.name)
                },
            }
            for silo in report.silos
        ],
    }
    if report.serie is not None:
        payload["serie_tablero"] = {
            "archivo": report.serie.path.name,
            "sidecar": report.serie.meta_path.name,
            "filas": report.serie.rows,
            "fechas": report.serie.dates,
            "series": report.serie.series,
            "fecha_min": report.serie.date_min,
            "fecha_max": report.serie.date_max,
            "sha256": report.serie.sha256,
        }
    destino = out_dir / "silos" / "manifest.json"
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return destino


def _miles(value: int) -> str:
    """Return an integer with a thin space every three digits."""
    return f"{value:,}".replace(",", " ")


def _seccion_volumenes(report: GenerationReport) -> list[str]:
    """Render the table of volumes, sizes and digests."""
    lineas = [
        "## Volumenes y huellas",
        "",
        "| Silo | Sistema origen | Filas | Columnas | Bytes | SHA-256 |",
        "|---|---|---:|---:|---:|---|",
    ]
    for silo in report.silos:
        lineas.append(
            f"| `{silo.name}` | {SILOS[silo.name].source_system} "
            f"| {_miles(silo.rows)} | {silo.columns} "
            f"| {_miles(silo.size_bytes)} | `{silo.sha256[:16]}...` |"
        )
    if report.serie is not None:
        lineas.append(
            f"| `serie_tablero` | Karisma Data | {_miles(report.serie.rows)} "
            f"| {len(SERIE_TABLERO.fields)} "
            f"| {_miles(report.serie.path.stat().st_size)} "
            f"| `{report.serie.sha256[:16]}...` |"
        )
    recorte = round((1 - report.total_rows / CATALOGO_JULIO_FILAS) * 100)
    lineas += [
        "",
        f"Los tres silos suman **{_miles(report.total_rows)} filas**. El catalogo "
        f"de julio describia unos {_miles(CATALOGO_JULIO_FILAS)}: el alcance de "
        f"este sprint es un **recorte del {recorte} %**, declarado como tal.",
        "",
        "El volumen de `liquidez` no es una preferencia sino un piso aritmetico: "
        f"la serie preagregada publica {_miles(DIAS_HABILES * N_SERIES)} puntos y "
        "cada uno necesita al menos una fila cruda detras.",
        "",
    ]
    return lineas


def _seccion_diccionario() -> list[str]:
    """Render one dictionary table per silo, with both locales."""
    lineas = ["## Diccionario de datos", ""]
    for nombre, silo in SILOS.items():
        lineas += [
            f"### `{nombre}` — {silo.source_system} ({silo.owner})",
            "",
            "| Columna | Etiqueta (es) | Label (en) | Tipo | Unidad |",
            "|---|---|---|---|---|",
        ]
        for campo in silo.fields:
            unidad = campo.unit or "-"
            lineas.append(
                f"| `{campo.name}` | {campo.label_es} | {campo.label_en} "
                f"| {campo.dtype} | {unidad} |"
            )
        lineas.append("")
    return lineas


def _seccion_heterogeneidad() -> list[str]:
    """Render the six axes on which the three systems disagree."""
    return [
        "## Heterogeneidad deliberada",
        "",
        "Los tres sistemas nunca se pusieron de acuerdo, y esa es justamente la "
        "materia del portal. La misma entidad aparece con seis diferencias a la "
        "vez:",
        "",
        "| Eje | `creditos` | `liquidez` | `derivados` |",
        "|---|---|---|---|",
        "| Columna del cliente | `cli_ref` | `id_cliente` | `ctpty_cd` |",
        "| Codificacion | `CLI-100042` | `100042` | `C100042C` |",
        "| Fecha | tipo fecha | tipo fecha, `fec_val` es T+1 | texto `AAAAMMDD` |",
        "| Moneda | codigo interno `01` | ISO-4217 en `divisa` | implicita USD |",
        "| Unidad del importe | pesos | **miles** de la divisa | dolares |",
        "| Razon social | truncada a 30 | completa | mayusculas sin acentos |",
        "",
        "**Regla de normalizacion**, ejecutable en "
        "`ml/data/schemas.py::normalize_client_key`: se quita el prefijo `CLI-` "
        "en creditos, se toma el entero tal cual en liquidez y se leen los seis "
        "digitos entre la `C` y la letra verificadora en derivados. Las tres "
        "codificaciones se reducen al mismo entero, y por eso los cruces "
        "devuelven filas.",
        "",
        "Los conjuntos de clientes estan anidados: los de `derivados` son un "
        "subconjunto de los de `liquidez`, y estos de los de `creditos`.",
        "",
    ]


def _seccion_anomalias(report: GenerationReport) -> list[str]:
    """Render the measured anomalies with the predicate that detects each."""
    lineas = [
        "## Anomalias inyectadas",
        "",
        "Los conteos de esta tabla no son los que el inyector pretendia "
        "escribir: son los que una auditoria independiente encontro en el "
        "archivo ya escrito, con los predicados de la ultima columna.",
        "",
        "| Silo | Tipo | Conteo | Predicado detector |",
        "|---|---|---:|---|",
    ]
    for silo in report.silos:
        for kind in AnomalyKind:
            if kind not in audited_kinds(silo.name):
                continue
            lineas.append(
                f"| `{silo.name}` | {LABELS_ES[kind]} | {silo.anomalies[kind]} "
                f"| `{predicate_es(silo.name, kind)}` |"
            )
    tasa = report.anomaly_rate * 100
    lineas += [
        "",
        f"Total: **{_miles(report.total_anomalies)} anomalias** sobre "
        f"{_miles(report.total_rows)} filas, es decir **{tasa:.3f} %** "
        f"(objetivo de diseno: {ANOMALY_RATE * 100:.3f} %).",
        "",
        "Ninguna anomalia cae sobre la espina de `liquidez`, las primeras "
        f"{_miles(DIAS_HABILES * N_SERIES)} filas: si una cayera ahi, esa celda "
        "de la rejilla se filtraria al agregar y la serie publicada tendria un "
        "punto menos.",
        "",
    ]
    return lineas


def _seccion_serie(report: GenerationReport) -> list[str]:
    """Render the frozen contract of the preaggregated series."""
    if report.serie is None:
        return []
    serie = report.serie
    lineas = [
        "## Serie preagregada del tablero",
        "",
        f"`data/aggregates/{serie.path.name}` y su sidecar `{serie.meta_path.name}`.",
        "",
        f"- **Grano**: una fila por (fecha, serie_id). {_miles(serie.rows)} filas "
        f"= {_miles(serie.dates)} dias habiles x {serie.series} claves.",
        f"- **Ventana**: del {serie.date_min} al {serie.date_max}, lunes a viernes.",
        "- **Orden en disco**: `(serie_id, fecha)`. Es parte del contrato: una "
        "serie es un tramo contiguo y el tablero la lee sin recorrer el archivo.",
        f"- **Rejilla**: {len(UNIDADES_NEGOCIO)} unidades de negocio x "
        f"{len(DIVISAS)} divisas x {len(BUCKETS_VENC)} buckets de vencimiento, "
        f"con `serie_id = unidad * 50 + divisa * 10 + bucket`.",
        "- **Derivada, no fabricada**: sale de agrupar `liquidez.parquet`, asi "
        "que cada punto tiene filas crudas detras y `n_posiciones` nunca es "
        "cero.",
        "",
        "| Columna | Etiqueta (es) | Label (en) | Tipo | Unidad |",
        "|---|---|---|---|---|",
    ]
    for campo in SERIE_TABLERO.fields:
        unidad = campo.unit or "-"
        lineas.append(
            f"| `{campo.name}` | {campo.label_es} | {campo.label_en} "
            f"| {campo.dtype} | {unidad} |"
        )
    lineas += [
        "",
        "`saldo_disponible_mxn` ya resuelve las dos trampas del origen: "
        "multiplica por mil los miles de `mto_disp` y convierte la divisa a "
        "pesos con el tipo de cambio sintetico fijo.",
        "",
    ]
    return lineas


def _seccion_limitaciones() -> list[str]:
    """Render the limitations that are declared instead of hidden."""
    tipos = ", ".join(f"{divisa} {valor}" for divisa, valor in FX_MXN.items())
    return [
        "## Limitaciones declaradas",
        "",
        "1. **Sin calendario de dias festivos.** Los dias habiles son de lunes a "
        "viernes. Un calendario mexicano real cambiaria el conteo y no cambiaria "
        "nada de lo que las pantallas demuestran.",
        f"2. **Tipo de cambio sintetico fijo** (pesos por unidad): {tipos}. No es "
        "una cotizacion de mercado ni pretende parecerlo.",
        "3. **Volumenes recortados** respecto del catalogo de julio, con el "
        "porcentaje declarado arriba.",
        "4. **`make data` no siembra la base de datos.** Solo escribe archivos, "
        "para que corra en una maquina sin Docker.",
        "5. **Ningun campo tiene forma de RFC ni de identificador fiscal.** "
        "Ninguna pantalla lo necesita.",
        "",
    ]


def _seccion_regenerar() -> list[str]:
    """Render how to regenerate and how to verify."""
    return [
        "## Como regenerar y como verificar",
        "",
        "```bash",
        "make data                     # regenera los cuatro parquet y este archivo",
        "bash scripts/verificar_datos.sh   # reproducibilidad, volumenes y anomalias",
        "```",
        "",
        "Los parquet, el manifiesto y el sidecar **no se versionan**: se "
        "regeneran con la semilla fija y dos corridas seguidas producen los "
        "mismos bytes. Quien clone el repositorio tiene que correr `make data` "
        "antes de que el explorador y el tablero muestren algo.",
        "",
        "Este archivo es el unico de `data/` que si se versiona, y es "
        "**generado**: lo escribe `ml/data/manifest.py`. Editarlo a mano deja "
        "`git diff --exit-code data/README.md` en rojo en la siguiente corrida.",
        "",
    ]


def render_readme(report: GenerationReport) -> str:
    """Render data/README.md from measurements only.

    Carries no timestamp on purpose: a generation date would put
    ``git diff --exit-code data/README.md`` in red on every run and would
    destroy the idempotence gate.

    Args:
        report: Measurements of the run.

    Returns:
        The complete document, ending in a single newline.
    """
    lineas = [
        _CABECERA,
        "",
        "# Datos sinteticos de Karisma Data",
        "",
        "**Advertencia: todo lo que hay en `data/` es sintetico.** Ninguna cifra "
        "proviene de una institucion real, ninguna persona ni empresa nombrada "
        "existe, y el tipo de cambio es un valor fijo inventado. Los datos "
        "imitan la forma y los defectos de tres sistemas internos que no se "
        "hablan entre si, que es el problema que el portal resuelve.",
        "",
        f"Semilla fija: **{report.seed}**. Con ella, dos corridas de `make data` "
        "producen los mismos bytes.",
        "",
    ]
    lineas += _seccion_volumenes(report)
    lineas += _seccion_diccionario()
    lineas += _seccion_heterogeneidad()
    lineas += _seccion_anomalias(report)
    lineas += _seccion_serie(report)
    lineas += _seccion_limitaciones()
    lineas += _seccion_regenerar()
    return "\n".join(lineas).rstrip("\n") + "\n"


def write_readme(report: GenerationReport, out_dir: Path) -> Path:
    """Write the versioned README inside the data directory of the run.

    The document lands in the output directory itself and never in a path
    derived from it: a run pointed at a scratch folder must not be able to
    overwrite the versioned document of the repository.

    Args:
        report: Measurements of the run.
        out_dir: Data directory of the run.

    Returns:
        The path of the written document.

    Raises:
        ValueError: If the run is not complete. A partial run would publish
            numbers that contradict the ones the deliverable already cites.
    """
    if not report.is_complete:
        raise ValueError(
            "only a complete run at the declared volumes may rewrite data/README.md"
        )
    destino = out_dir / "README.md"
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(render_readme(report), encoding="utf-8", newline="\n")
    return destino
