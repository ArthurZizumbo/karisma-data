"""Content, invariants and reproducibility of the semantic catalog seed.

Every test here answers the same question before being written: which concrete
defect makes it fail. The interesting half of the suite guards the border
between this module and PostgreSQL -the closed lists of the CHECK constraints,
the generated column that refuses to be written- because those defects do not
show up until the seed is applied, on another machine, in the middle of a
deploy.
"""

import json
import random
from collections import Counter
from pathlib import Path

import pytest

from ml.data import catalog_content, schemas, seed_catalog

# The closed lists of db/migrations/<ts>_create_catalog.sql. Duplicated here on
# purpose: this file is the only place where the emitter and the CHECK
# constraints are compared, and a copy that has to agree is exactly what makes
# the disagreement visible.
DOMAINS = {
    "cartera",
    "riesgo",
    "liquidez",
    "mercado",
    "cliente",
    "contable",
    "operacion",
    "regulatorio",
}
DATA_TYPES = {"entero", "decimal", "texto", "fecha", "booleano", "categoria"}
SENSITIVITIES = {"publica", "interna", "restringida"}
REFRESH = {"intradia", "diaria", "semanal", "mensual"}
CERTIFICATIONS = {"certificado", "en_revision", "obsoleto"}
UNITS = {"MXN", "USD", "porcentaje", "dias", "conteo"}
METRIC_AGGS = {"sum", "mean", "count", "max", "min"}

REFERENCE_QUERIES = Path(__file__).parent / "data" / "consultas_referencia.json"


@pytest.fixture(scope="module")
def entries() -> tuple[seed_catalog.CatalogEntry, ...]:
    """Return every catalog entry once for the whole module."""
    return seed_catalog.catalog_entries()


@pytest.fixture(scope="module")
def resolved() -> tuple[seed_catalog.ResolvedField, ...]:
    """Return every entry with its drawn metadata, over the fixed seed."""
    # S311: the draw has to be reproducible, which is the opposite of what a
    # cryptographic generator gives.
    return seed_catalog.resolve_fields(random.Random(seed_catalog.SEED))  # noqa: S311


@pytest.fixture(scope="module")
def sql() -> str:
    """Return the emitted seed script once for the whole module."""
    return seed_catalog.build_seed()


def test_el_catalogo_tiene_entre_200_y_400_entradas(
    entries: tuple[seed_catalog.CatalogEntry, ...],
) -> None:
    """Defect: someone trims the content below the accepted range of the US."""
    assert 200 <= len(entries) <= 400


def test_hay_treinta_notas_tribales() -> None:
    """Defect: the tribal knowledge shrinks and the Tk-Boost demo has nothing."""
    assert len(catalog_content.NOTES) == 30


def test_no_hay_claves_naturales_duplicadas(
    entries: tuple[seed_catalog.CatalogEntry, ...],
) -> None:
    """Defect: two entries share (source, physical_name).

    The UNIQUE constraint would abort the seed at apply time, which is late and
    on a machine that is not the one that introduced the duplicate.
    """
    duplicated = [
        key
        for key, count in Counter(
            (entry.source_code, entry.physical_name) for entry in entries
        ).items()
        if count > 1
    ]
    assert duplicated == []


def test_toda_nota_apunta_a_un_campo_declarado() -> None:
    """Defect: a note names a column nobody declares.

    The INSERT ... SELECT of the seed would insert zero rows in silence and the
    count of thirty would hold in the file and not in the database.
    """
    assert len(seed_catalog.resolved_notes()) == 30


def test_toda_nota_declara_su_condicion_de_aplicabilidad() -> None:
    """Defect: a note is seeded without a condition and Tk-Boost is decoration."""
    for note in catalog_content.NOTES:
        assert note.applicability.strip()


def test_las_notas_no_se_repiten_sobre_el_mismo_campo() -> None:
    """Defect: two identical notes on one field trip the UNIQUE at apply time."""
    keys = Counter(
        (note.source_code, note.physical_name, note.note)
        for note in catalog_content.NOTES
    )
    assert [key for key, count in keys.items() if count > 1] == []


def test_los_tres_silos_estan_cubiertos_columna_por_columna(
    entries: tuple[seed_catalog.CatalogEntry, ...],
) -> None:
    """Defect: the catalog documents a column no Parquet has, or misses one.

    Both halves matter: an entry without a column is a field the explorer cannot
    query, and a column without an entry is a column without a definition.
    """
    for source_code in seed_catalog.EXTRACT_SOURCES:
        documented = {
            entry.physical_name for entry in entries if entry.source_code == source_code
        }
        assert documented == set(schemas.SILOS[source_code].columns)


def test_ninguna_fuente_con_extracto_se_documenta_a_mano() -> None:
    """Defect: a silo column is retyped in catalog_content.

    That is what produced two truths for one column and the eighteen versus
    thirty four count error. The vocabulary of those three sources belongs to
    ml.data.schemas.
    """
    with_extract = {
        source.code for source in catalog_content.SOURCES if source.has_extract
    }
    documented = {field.source_code for field in catalog_content.FIELDS}
    assert documented & with_extract == set()


def test_las_facetas_respetan_las_listas_cerradas_de_la_migracion(
    resolved: tuple[seed_catalog.ResolvedField, ...],
) -> None:
    """Defect: a value outside a CHECK aborts the whole seed at apply time.

    The transaction rolls back, the tables are left empty by the TRUNCATE that
    already ran, and the message names a constraint instead of a field.
    """
    for field in resolved:
        entry = field.entry
        assert entry.domain in DOMAINS
        assert entry.data_type in DATA_TYPES
        assert entry.unit is None or entry.unit in UNITS
        assert entry.metric_agg is None or entry.metric_agg in METRIC_AGGS
        assert field.sensitivity in SENSITIVITIES
        assert field.refresh_frequency in REFRESH
        assert field.certification in CERTIFICATIONS


def test_obsoleto_si_y_solo_si_tiene_fecha_de_cierre(
    resolved: tuple[seed_catalog.ResolvedField, ...],
) -> None:
    """Defect: the draw produces an obsolete entry with an open validity.

    catalog_field_obsolete_chk rejects it and the seed aborts entirely.
    """
    for field in resolved:
        assert (field.certification == "obsoleto") == (field.valid_to is not None)
        if field.valid_to is not None:
            assert field.valid_to >= field.valid_from


def test_hay_entradas_obsoletas_y_vigentes(
    resolved: tuple[seed_catalog.ResolvedField, ...],
) -> None:
    """Defect: the certification facet has nothing to filter.

    With zero obsolete entries the closed validity path is never exercised and
    the panel cannot show a retired field, which is the case that makes a
    catalog credible.
    """
    certifications = Counter(field.certification for field in resolved)
    assert certifications["obsoleto"] > 0
    assert certifications["certificado"] > 0
    assert certifications["en_revision"] > 0


def test_la_emision_es_determinista() -> None:
    """Defect: module level randomness, date.today(), or iterating a set.

    Any of the three makes two runs differ and turns the byte to byte gate of
    the versioned artifact into a coin toss.
    """
    assert seed_catalog.build_seed() == seed_catalog.build_seed()


def test_el_artefacto_versionado_esta_al_dia() -> None:
    """Defect: the content changed and db/seeds/catalog.sql was not regenerated.

    Across processes this also catches the two defects the in process check
    cannot see: a set iterated under a different hash seed and a date.today()
    that moved since the file was written.
    """
    assert seed_catalog.main(["--check"]) == 0


def test_el_sql_abre_transaccion_y_trunca_antes_de_insertar(sql: str) -> None:
    """Defect: the TRUNCATE is lost and the seed stops being idempotent.

    The second application would either duplicate rows or fail on the UNIQUE,
    and make db-seed would only be safe on an empty database.
    """
    begin = sql.index("BEGIN;")
    truncate = sql.index("TRUNCATE catalog_tribal_note, catalog_field, catalog_source")
    first_insert = sql.index("INSERT INTO catalog_source")
    assert begin < truncate < first_insert
    assert "RESTART IDENTITY CASCADE" in sql
    assert sql.rstrip().endswith(";")
    assert "COMMIT;" in sql


def test_el_sql_no_escribe_las_dos_columnas_que_no_se_pueden_escribir(
    sql: str,
) -> None:
    """Defect: search_document or embedding reach an INSERT column list.

    PostgreSQL rejects any write to a GENERATED ALWAYS column, so the whole seed
    aborts; embedding stays null until the hybrid search phase writes it.
    """
    body = sql[sql.index("BEGIN;") :]
    assert "search_document" not in body
    assert "embedding" not in body


def test_el_sql_escapa_las_comillas_simples() -> None:
    """Defect: an apostrophe in a definition closes the literal early.

    A single quote that reaches PostgreSQL unescaped turns curated prose into a
    syntax error, and the seed is applied by a script nobody reads line by line.
    """
    assert seed_catalog.sql_literal("l'apostrophe") == "'l''apostrophe'"
    assert seed_catalog.sql_literal(None) == "NULL"


def test_los_alias_traen_el_termino_en_ingles_en_los_conceptos_frecuentes(
    entries: tuple[seed_catalog.CatalogEntry, ...],
) -> None:
    """Defect: the catalog is seeded only in Spanish.

    The interface is bilingual and the definitions are not translated on
    purpose, so somebody navigating in English finds nothing unless the alias
    column carries the English term. Checked on a short explicit list, never on
    the whole catalog.
    """
    expected = {
        ("creditos", "sdo_cap"): "outstanding principal",
        ("creditos", "dias_mora"): "days past due",
        ("liquidez", "ratio_lcr"): "liquidity coverage ratio",
        ("derivados", "nocional_usd"): "notional",
        ("clientes", "cli_rfc"): "tax id",
        ("regulatorio", "reg_icap"): "capital adequacy ratio",
    }
    by_key = {(entry.source_code, entry.physical_name): entry for entry in entries}
    for key, term in expected.items():
        assert term in seed_catalog.alias_text(by_key[key]).lower()


def test_los_alias_traen_la_grafia_acentuada_cuando_el_lexema_cambia(
    entries: tuple[seed_catalog.CatalogEntry, ...],
) -> None:
    """Defect: somebody typing correct Spanish finds nothing.

    Verified against PostgreSQL 15.18: the spanish configuration reconciles
    accents only for short words. tesoreria and tesoreria stem to tesoreri and
    tesor, garantia and garantia to garanti and garant. The corpus is written
    without diacritics, so the accented spelling has to be indexed as an alias
    or half the interface stops finding its own content.
    """
    by_key = {(entry.source_code, entry.physical_name): entry for entry in entries}
    assert "tesorería" in seed_catalog.alias_text(by_key[("tesoreria", "tes_f_pos")])
    assert "garantía" in seed_catalog.alias_text(by_key[("garantias", "g_val_com")])
    assert "estimación" in seed_catalog.alias_text(by_key[("provisiones", "prv_eprc")])


def test_un_alias_repetido_se_emite_una_sola_vez() -> None:
    """Defect: the same alias is indexed twice and inflates its own ranking.

    It happens on its own: the English label of a silo column can coincide with
    a curated synonym, and weight B would then count the term twice.
    """
    entry = seed_catalog.CatalogEntry(
        source_code="creditos",
        physical_name="sdo_cap",
        business_name="Saldo de capital",
        definition="Capital insoluto en pesos.",
        aliases=("adeudo", "adeudo", "outstanding principal"),
        domain="cartera",
        data_type="decimal",
        unit="MXN",
        metric_agg="sum",
        sensitivity="interna",
    )
    assert seed_catalog.alias_text(entry) == "adeudo outstanding principal"


def test_una_columna_codificada_indexa_las_etiquetas_de_sus_valores(
    entries: tuple[seed_catalog.CatalogEntry, ...],
) -> None:
    """Defect: prod_cd is searchable by HIP and not by hipotecario.

    Nobody types the internal code. The labels live in schemas.DOMAIN_LABELS in
    both locales and are imported, never retyped.
    """
    by_key = {(entry.source_code, entry.physical_name): entry for entry in entries}
    aliases = seed_catalog.alias_text(by_key[("creditos", "prod_cd")]).lower()
    assert "hipotecario" in aliases
    assert "mortgage" in aliases


def test_el_dato_personal_no_se_sortea(
    entries: tuple[seed_catalog.CatalogEntry, ...],
) -> None:
    """Defect: the name of a person is published with a drawn sensitivity.

    A one in three chance of labelling a client name as public is not a bug that
    shows up in a screenshot.
    """
    by_key = {(entry.source_code, entry.physical_name): entry for entry in entries}
    for source_code, physical_name in seed_catalog.PERSONAL_DATA_COLUMNS:
        assert by_key[(source_code, physical_name)].sensitivity == "restringida"


def test_ninguna_clave_de_cliente_queda_como_dato_publico(
    entries: tuple[seed_catalog.CatalogEntry, ...],
) -> None:
    """Defect: a client identifier is published with a drawn sensitivity.

    It is not a name, so it escapes the restricted list, and one draw in six
    lands on "publica". A catalog of data governance that shows a client key as
    open data is the screenshot this project must not produce.
    """
    by_key = {(entry.source_code, entry.physical_name): entry for entry in entries}
    keys = [
        (source_code, field.name)
        for source_code in seed_catalog.EXTRACT_SOURCES
        for field in schemas.SILOS[source_code].fields
        if field.is_client_key
    ]
    assert len(keys) == 3
    for key in keys:
        assert by_key[key].sensitivity == "interna"


def test_las_veinte_consultas_de_referencia_estan_congeladas() -> None:
    """Defect: an expected source code is misspelled.

    That query can never be satisfied by any result, so the Hit Rate baseline
    is quietly capped below the gate and no message ever says why.
    """
    data = json.loads(REFERENCE_QUERIES.read_text(encoding="utf-8"))
    queries = data["queries"]
    codes = {source.code for source in catalog_content.SOURCES}
    assert len(queries) == 20
    assert len({query["id"] for query in queries}) == 20
    for query in queries:
        assert query["expected_source"] in codes
        assert query["query"].strip()
