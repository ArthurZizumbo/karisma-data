"""Emit the idempotent SQL seed of the semantic catalog.

Two vocabularies, one output. The three sources with a Parquet extract take
their columns from :mod:`ml.data.schemas`, which US-006 owns and freezes; the
nine documented sources without an extract take theirs from
:mod:`ml.data.catalog_content`. Nothing is typed twice, so the row count of the
extract silos cannot drift away from the files that actually exist.

Deterministic by construction: one ``random.Random`` seeded with ``SEED``,
consumed in a fixed order -the thirty four imported entries first, in the order
of ``EXTRACT_SOURCES``, then the two hundred seventy curated ones in their order
of declaration-. Two runs produce byte identical output, which is what makes
``git diff --exit-code db/seeds/catalog.sql`` a gate that means something.

This module imports polars transitively through ml.data.schemas. That is
deliberate and cheap: polars is a main dependency of the project. What it never
does is open a database connection, which is the property that matters: the
tests of tests/ml run on a machine without Docker and without PostgreSQL.
"""

import argparse
import random
import re
from collections.abc import Sequence
from datetime import date
from pathlib import Path
from typing import Final, NamedTuple

import structlog

from ml.data import schemas
from ml.data.catalog_content import (
    ACCENTED_FORMS,
    FIELDS,
    NOTES,
    SEARCH_SYNONYMS,
    SOURCES,
    NoteSpec,
)

logger = structlog.get_logger(__name__)

SEED: Final[int] = 20260720
"""Same seed as US-006, by mandate of ml/AGENTS.md."""

REPO_ROOT: Final[Path] = Path(__file__).resolve().parents[2]
OUTPUT: Final[Path] = REPO_ROOT / "db" / "seeds" / "catalog.sql"

EXTRACT_SOURCES: Final[tuple[str, ...]] = ("creditos", "liquidez", "derivados")
"""Fixed traversal order of the silos with an extract.

Never ``schemas.SILOS.keys()``: the draw order is part of the reproducibility
contract and a dict rebuilt from a set would silently reorder it.
"""

# Polars dtype -> catalog data type code. Seven entries and no inference: a
# dtype nobody looked at must raise instead of quietly becoming "texto".
DTYPE_TO_DATA_TYPE: Final[dict[str, str]] = {
    "String": "texto",
    "Date": "fecha",
    "Boolean": "booleano",
    "Int16": "entero",
    "Int32": "entero",
    "Int64": "entero",
    "Float64": "decimal",
}

# FieldSpec.unit is free prose in schemas.py, the catalog facet is a closed
# list. The only value that does not map is "miles de la divisa", which is not a
# unit but a scale over the currency of the row: there is no single code for it,
# the definition of the column states it, and its tribal note repeats it.
UNIT_TO_UNIT_CODE: Final[dict[str, str | None]] = {
    "MXN": "MXN",
    "USD": "USD",
    "dias": "dias",
    "%": "porcentaje",
    "miles de la divisa": None,
}

# Business domain of each extract silo. schemas.FieldSpec.domain is the closed
# list of VALUES a column accepts, which is a different thing entirely.
SOURCE_DOMAIN: Final[dict[str, str]] = {
    "creditos": "cartera",
    "liquidez": "liquidez",
    "derivados": "mercado",
}

# Columns of the extract silos that carry the name of a person or a company.
# Their sensitivity is curated and never drawn: a personal datum is not a dice
# roll. Every pair is checked against schemas.py, so a typo raises here instead
# of publishing a name as "publica".
PERSONAL_DATA_COLUMNS: Final[tuple[tuple[str, str], ...]] = (
    ("creditos", "nom_cli"),
    ("liquidez", "cliente_desc"),
    ("derivados", "ctpty_name"),
)

SENSITIVITY_CHOICES: Final[tuple[str, ...]] = ("publica", "interna", "restringida")
SENSITIVITY_WEIGHTS: Final[tuple[int, ...]] = (15, 65, 20)
REFRESH_CHOICES: Final[tuple[str, ...]] = ("intradia", "diaria", "semanal", "mensual")
REFRESH_WEIGHTS: Final[tuple[int, ...]] = (10, 55, 15, 20)
ACTIVE_CERTIFICATIONS: Final[tuple[str, ...]] = ("certificado", "en_revision")
ACTIVE_CERTIFICATION_WEIGHTS: Final[tuple[int, ...]] = (65, 35)
OBSOLETE_RATE: Final[float] = 0.05
"""Share of entries with a closed validity, which is what gives the certification
facet something to filter."""

# Quarter starts from 2019 to 2025. A first day of quarter has no leap year edge
# when the closing date adds whole years to it.
VALID_FROM_DATES: Final[tuple[date, ...]] = tuple(
    date(year, month, 1) for year in range(2019, 2026) for month in (1, 4, 7, 10)
)
VALIDITY_YEARS: Final[tuple[int, ...]] = (1, 2, 3)

# Frozen names. No Faker here: the catalog content is curated, not drawn, and a
# steward whose name changes with the Faker version is a diff nobody asked for.
STEWARDS: Final[tuple[str, ...]] = (
    "Adriana Cortes",
    "Daniel Ocampo",
    "Hugo Beltran",
    "Ivan Zepeda",
    "Jorge Nieto",
    "Marcela Rios",
    "Paola Iniguez",
    "Renata Fuentes",
    "Ricardo Salas",
    "Sofia Aranda",
)

_WORD: Final[re.Pattern[str]] = re.compile(r"[0-9a-z_]+")

_HEADER: Final[str] = """\
-- Generado por ml/data/seed_catalog.py. No editar a mano: la siguiente corrida
-- lo reescribe y "make db-seed" comparara byte a byte.
--
-- Semilla {seed}. {sources} fuentes, {fields} campos, {notes} notas tribales.
--
-- Idempotente por construccion: abre transaccion, vacia las tres tablas
-- reiniciando las secuencias y vuelve a insertar. Sembrar dos veces deja la
-- base identica hasta en las claves primarias, y por eso reseembrar BORRA los
-- embedding que escriba la fase de busqueda hibrida: hay que reejecutar el job
-- de embeddings despues de cada "make db-seed".
--
-- Las columnas search_document y embedding no aparecen en ninguna lista: la
-- primera es GENERATED ALWAYS y PostgreSQL rechaza que se le escriba, la
-- segunda se queda nula hasta S5.
"""


class CatalogEntry(NamedTuple):
    """One catalog row before its operational metadata is drawn.

    The single shape both vocabularies collapse into, so that the rest of the
    emitter does not care where a field came from.
    """

    source_code: str
    physical_name: str
    business_name: str
    definition: str
    aliases: tuple[str, ...]
    domain: str
    data_type: str
    unit: str | None
    metric_agg: str | None
    sensitivity: str | None
    """None means: draw it with the seeded generator."""


class ResolvedField(NamedTuple):
    """A :class:`CatalogEntry` with every drawn attribute already decided."""

    entry: CatalogEntry
    sensitivity: str
    refresh_frequency: str
    certification: str
    valid_from: date
    valid_to: date | None
    steward: str


def accented_variants(*texts: str) -> tuple[str, ...]:
    """Return the accented spelling of every word that needs one.

    The corpus is written without diacritics, following ml/data/schemas.py, and
    the Spanish stemmer only reconciles the two spellings for short words:
    ``credito`` and ``credito`` collapse, ``tesoreria`` and ``tesoreria`` do
    not. Indexing the accented form as an alias is what lets somebody who types
    correct Spanish find the entry.

    Args:
        *texts: Texts to scan, in the order their words should be emitted.

    Returns:
        The accented spellings found, without repetitions and in reading order.
    """
    found: list[str] = []
    for text in texts:
        for word in _WORD.findall(text.lower()):
            accented = ACCENTED_FORMS.get(word)
            if accented is not None and accented not in found:
                found.append(accented)
    return tuple(found)


def alias_text(entry: CatalogEntry) -> str:
    """Render the alias column of one entry.

    Args:
        entry: The catalog entry.

    Returns:
        Space separated aliases plus the accented spellings the search needs,
        with no repetitions.
    """
    parts: list[str] = []
    for alias in (
        *entry.aliases,
        *accented_variants(entry.business_name, entry.definition, *entry.aliases),
    ):
        if alias not in parts:
            parts.append(alias)
    return " ".join(parts)


def _value_labels(field: schemas.FieldSpec) -> tuple[str, ...]:
    """Return the human labels of the values a coded column accepts.

    ``prod_cd`` stores ``HIP`` and nobody searches for ``HIP``: they search for
    "hipotecario". Those labels are published by schemas.DOMAIN_LABELS in both
    locales, so they are imported like everything else.

    Args:
        field: Column specification of the silo.

    Returns:
        The Spanish and English labels of every accepted value, or an empty
        tuple when the column is not coded.

    Raises:
        KeyError: If a coded value has no label pair. A code that reaches the
            screen without both locales shows up raw in one of the two.
    """
    if field.domain is None:
        return ()
    labels = schemas.DOMAIN_LABELS.get(field.name)
    if labels is None:
        return ()
    rendered: list[str] = []
    for code in field.domain:
        label_es, label_en = labels[code]
        rendered.extend((label_es, label_en))
    return tuple(rendered)


def _curated_sensitivity(source_code: str, field: schemas.FieldSpec) -> str | None:
    """Return the sensitivity that must not be drawn for one silo column.

    Two cases, and neither is a dice roll. A column holding the name of a person
    or a company is restricted. A client key is internal even though it is not a
    name: it identifies somebody, and a catalog that shows "publica" next to a
    client identifier is exactly the screenshot this project must not produce.

    Args:
        source_code: Silo the column belongs to.
        field: Column specification.

    Returns:
        The curated sensitivity, or None when it is safe to draw it.
    """
    if (source_code, field.name) in PERSONAL_DATA_COLUMNS:
        return "restringida"
    if field.is_client_key:
        return "interna"
    return None


def entries_from_schemas() -> tuple[CatalogEntry, ...]:
    """Adapt the thirty four frozen columns of the three extract silos.

    Maps ``label_es`` to the business name, ``description_es`` to the
    definition, ``label_en`` into the alias list and the Polars dtype to a
    catalog data type code. Nothing here types a column name: it walks
    ``schemas.SILOS`` in ``EXTRACT_SOURCES`` order.

    Returns:
        Exactly one entry per column of the three silos, in traversal order.

    Raises:
        KeyError: If a dtype, a unit or a coded value has no mapping, or if a
            curated table points at a column that does not exist. Failing loudly
            beats guessing "texto" for a column nobody looked at.
    """
    for source_code, physical_name in (*SEARCH_SYNONYMS, *PERSONAL_DATA_COLUMNS):
        schemas.SILOS[source_code].field(physical_name)

    entries: list[CatalogEntry] = []
    for source_code in EXTRACT_SOURCES:
        silo = schemas.SILOS[source_code]
        for field in silo.fields:
            aliases = (
                field.label_en,
                *_value_labels(field),
                *SEARCH_SYNONYMS.get((source_code, field.name), ()),
            )
            entries.append(
                CatalogEntry(
                    source_code=source_code,
                    physical_name=field.name,
                    business_name=field.label_es,
                    definition=field.description_es,
                    aliases=aliases,
                    domain=(
                        "cliente" if field.is_client_key else SOURCE_DOMAIN[source_code]
                    ),
                    data_type=(
                        "categoria"
                        if field.domain is not None
                        else DTYPE_TO_DATA_TYPE[str(field.dtype)]
                    ),
                    unit=(
                        None if field.unit is None else UNIT_TO_UNIT_CODE[field.unit]
                    ),
                    metric_agg=field.aggregation,
                    sensitivity=_curated_sensitivity(source_code, field),
                )
            )
    return tuple(entries)


def entries_from_content() -> tuple[CatalogEntry, ...]:
    """Adapt the two hundred seventy curated fields of the documented sources.

    Returns:
        One entry per declared field, in order of declaration.

    Raises:
        ValueError: If an entry names a source that is not declared, or one
            declared with an extract. That source's vocabulary belongs to
            ml.data.schemas and duplicating it is the defect this raises on.
    """
    extract_codes = {source.code for source in SOURCES if source.has_extract}
    known_codes = {source.code for source in SOURCES}
    entries: list[CatalogEntry] = []
    for field in FIELDS:
        if field.source_code not in known_codes:
            raise ValueError(
                f"{field.physical_name}: unknown source {field.source_code!r}"
            )
        if field.source_code in extract_codes:
            raise ValueError(
                f"{field.physical_name}: {field.source_code!r} has an extract, so its "
                "vocabulary comes from ml.data.schemas"
            )
        entries.append(
            CatalogEntry(
                source_code=field.source_code,
                physical_name=field.physical_name,
                business_name=field.business_name,
                definition=field.definition,
                aliases=field.aliases,
                domain=field.domain,
                data_type=field.data_type,
                unit=field.unit,
                metric_agg=field.metric_agg,
                sensitivity=field.sensitivity,
            )
        )
    return tuple(entries)


def catalog_entries() -> tuple[CatalogEntry, ...]:
    """Return every catalog entry in the frozen traversal order.

    Returns:
        The imported entries of the three extract silos followed by the curated
        ones. The order is part of the reproducibility contract: changing it
        changes every drawn attribute downstream.
    """
    return (*entries_from_schemas(), *entries_from_content())


def resolve_fields(rng: random.Random) -> tuple[ResolvedField, ...]:
    """Draw the operational metadata of every catalog entry.

    Five draws happen for every entry, always in the same order and always all
    five, even when the value ends up discarded: a branch that skips a draw
    would make a curated sensitivity shift every attribute of every entry that
    comes after it.

    Args:
        rng: Seeded generator, consumed in the order of ``catalog_entries()``.

    Returns:
        One resolved field per entry, in the same order.
    """
    resolved: list[ResolvedField] = []
    for entry in catalog_entries():
        drawn_sensitivity = rng.choices(SENSITIVITY_CHOICES, SENSITIVITY_WEIGHTS)[0]
        refresh = rng.choices(REFRESH_CHOICES, REFRESH_WEIGHTS)[0]
        is_obsolete = rng.random() < OBSOLETE_RATE
        active = rng.choices(ACTIVE_CERTIFICATIONS, ACTIVE_CERTIFICATION_WEIGHTS)[0]
        valid_from = rng.choice(VALID_FROM_DATES)
        years = rng.choice(VALIDITY_YEARS)
        steward = rng.choice(STEWARDS)
        resolved.append(
            ResolvedField(
                entry=entry,
                sensitivity=entry.sensitivity or drawn_sensitivity,
                refresh_frequency=refresh,
                certification="obsoleto" if is_obsolete else active,
                valid_from=valid_from,
                valid_to=(
                    valid_from.replace(year=valid_from.year + years)
                    if is_obsolete
                    else None
                ),
                steward=steward,
            )
        )
    return tuple(resolved)


def resolved_notes() -> tuple[NoteSpec, ...]:
    """Return the tribal notes after checking that every target exists.

    Returns:
        The declared notes, unchanged, in order of declaration.

    Raises:
        ValueError: If a note points at a field nobody declares. The seed would
            insert zero rows for it in silence, and the count of thirty would
            hold in the file and not in the database.
    """
    declared = {(entry.source_code, entry.physical_name) for entry in catalog_entries()}
    for note in NOTES:
        if (note.source_code, note.physical_name) not in declared:
            raise ValueError(
                f"tribal note points at {note.source_code}.{note.physical_name}, "
                "which no source declares"
            )
        if not note.applicability.strip():
            raise ValueError(
                f"tribal note on {note.source_code}.{note.physical_name} has no "
                "applicability condition"
            )
    return NOTES


def sql_literal(value: str | None) -> str:
    """Render a Python value as a SQL literal.

    Args:
        value: Text to quote, or None.

    Returns:
        ``NULL`` or the single quoted text with its quotes doubled.
    """
    if value is None:
        return "NULL"
    escaped = value.replace("'", "''")
    return f"'{escaped}'"


def _date_literal(value: date | None) -> str:
    """Render a date as a SQL literal.

    Args:
        value: The date, or None.

    Returns:
        ``NULL`` or a ``DATE 'YYYY-MM-DD'`` literal.
    """
    return "NULL" if value is None else f"DATE '{value.isoformat()}'"


def emit_sql(fields: Sequence[ResolvedField], notes: Sequence[NoteSpec]) -> str:
    """Render the complete idempotent seed script.

    The script opens a transaction, truncates the three tables restarting the
    identity sequences, and inserts sources, fields and notes resolving the
    foreign keys with sub-selects on the natural keys, never on an identifier
    the file would have to guess.

    Args:
        fields: Every resolved catalog entry, in traversal order.
        notes: Every validated tribal note, in order of declaration.

    Returns:
        The SQL script, ending with a newline.
    """
    lines: list[str] = [
        _HEADER.format(
            seed=SEED, sources=len(SOURCES), fields=len(fields), notes=len(notes)
        ),
        "BEGIN;",
        "",
        "SET client_encoding = 'UTF8';",
        "",
        "TRUNCATE catalog_tribal_note, catalog_field, catalog_source",
        "    RESTART IDENTITY CASCADE;",
        "",
        "INSERT INTO catalog_source (code, display_name, description, owner_area,",
        "                            owner_name, system_of_record, has_extract)",
        "VALUES",
    ]
    rendered_sources = [
        "    ("
        + ", ".join(
            (
                sql_literal(source.code),
                sql_literal(source.display_name),
                sql_literal(source.description),
                sql_literal(source.owner_area),
                sql_literal(source.owner_name),
                sql_literal(source.system_of_record),
                "true" if source.has_extract else "false",
            )
        )
        + ")"
        for source in SOURCES
    ]
    lines.append(",\n".join(rendered_sources) + ";")

    current_source = ""
    for resolved in fields:
        entry = resolved.entry
        if entry.source_code != current_source:
            current_source = entry.source_code
            lines.extend(("", f"-- {current_source}"))
        lines.extend(
            (
                "INSERT INTO catalog_field (source_id, physical_name, business_name,",
                "                           definition, aliases, domain, data_type,",
                "                           sensitivity, refresh_frequency,",
                "                           certification, unit, metric_agg, steward,",
                "                           valid_from, valid_to)",
                f"SELECT s.id, {sql_literal(entry.physical_name)},",
                f"       {sql_literal(entry.business_name)},",
                f"       {sql_literal(entry.definition)},",
                f"       {sql_literal(alias_text(entry))},",
                f"       {sql_literal(entry.domain)}, {sql_literal(entry.data_type)},",
                f"       {sql_literal(resolved.sensitivity)},"
                f" {sql_literal(resolved.refresh_frequency)},",
                f"       {sql_literal(resolved.certification)},"
                f" {sql_literal(entry.unit)}, {sql_literal(entry.metric_agg)},",
                f"       {sql_literal(resolved.steward)},"
                f" {_date_literal(resolved.valid_from)},"
                f" {_date_literal(resolved.valid_to)}",
                "  FROM catalog_source s"
                f" WHERE s.code = {sql_literal(entry.source_code)};",
            )
        )

    lines.extend(("", "-- notas tribales"))
    for note in notes:
        lines.extend(
            (
                "INSERT INTO catalog_tribal_note (field_id, note, applicability,",
                "                                 applicability_terms, author,",
                "                                 recorded_at)",
                f"SELECT f.id, {sql_literal(note.note)},",
                f"       {sql_literal(note.applicability)},",
                f"       {sql_literal(note.applicability_terms)},",
                # date.fromisoformat, and not the raw string: it is the only
                # value of the emitter that does not pass through sql_literal,
                # and a NoteSpec with a quote in recorded_at would emit runnable
                # SQL into a 234 KB artifact that make db-seed applies with the
                # migration DSN. Parsing it makes a malformed date fail here,
                # loudly, instead of downstream and quietly.
                f"       {sql_literal(note.author)}, "
                f"{_date_literal(date.fromisoformat(note.recorded_at))}",
                "  FROM catalog_field f",
                "  JOIN catalog_source s ON s.id = f.source_id",
                f" WHERE s.code = {sql_literal(note.source_code)}",
                f"   AND f.physical_name = {sql_literal(note.physical_name)};",
            )
        )

    lines.extend(
        (
            "",
            "COMMIT;",
            "",
            "-- Lo que quedo sembrado, medido y no prometido. Es la unica salida",
            "-- de make db-seed cuando psql corre en modo silencioso.",
            "SELECT (SELECT count(*) FROM catalog_source)      AS fuentes,",
            "       (SELECT count(*) FROM catalog_field)       AS campos,",
            "       (SELECT count(*) FROM catalog_tribal_note) AS notas;",
            "",
        )
    )
    return "\n".join(lines)


def build_seed() -> str:
    """Render the seed script from the frozen content.

    Returns:
        The SQL script. Two calls in the same process return the same text.
    """
    # S311: nothing here is a secret. A reproducible draw is exactly what a
    # fixed seed buys, and a cryptographic generator would destroy it.
    rng = random.Random(SEED)  # noqa: S311
    return emit_sql(resolve_fields(rng), resolved_notes())


def main(argv: Sequence[str] | None = None) -> int:
    """Write the seed to disk, or check that the file on disk is up to date.

    Args:
        argv: Arguments, or None to read them from the process.

    Returns:
        The process exit code. One when ``--check`` finds any difference, which
        is what the reproducibility gate uses.
    """
    parser = argparse.ArgumentParser(
        prog="python -m ml.data.seed_catalog",
        description=(
            "Emite el seed idempotente del catalogo semantico con semilla fija."
        ),
    )
    parser.add_argument("--out", default=str(OUTPUT), help="ruta del archivo SQL")
    parser.add_argument(
        "--check",
        action="store_true",
        help="no escribe: compara y devuelve 1 si el archivo difiere",
    )
    args = parser.parse_args(argv)

    destination = Path(args.out)
    sql = build_seed().encode("utf-8")
    if args.check:
        current = destination.read_bytes() if destination.exists() else b""
        if current != sql:
            logger.error("catalog_seed_outdated", path=str(destination))
            return 1
        logger.info("catalog_seed_up_to_date", path=str(destination))
        return 0

    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(sql)
    logger.info(
        "catalog_seed_written",
        path=str(destination),
        sources=len(SOURCES),
        fields=len(catalog_entries()),
        notes=len(NOTES),
        bytes=len(sql),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
