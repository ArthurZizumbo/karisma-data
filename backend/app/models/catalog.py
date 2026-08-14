"""SQLModel mirror of the catalog schema and the API contracts it feeds.

The tables are created by dbmate (``db/migrations/<ts>_create_catalog.sql``);
these classes only reflect them and never create schema. Two columns are
deliberately unmapped: ``search_document`` is ``GENERATED ALWAYS ... STORED``
and PostgreSQL rejects any statement that writes it, and ``embedding`` is a
``VECTOR(768)`` that nothing reads until the hybrid phase of S5. Mapping either
one would buy a dependency today for a feature that lands next sprint.

The response contracts below are the frozen part of this module: US-UX-07
builds the metadata panel against these field names. Every facet value is a
stable code in ``snake_case`` -``restringida``, never ``Restringida``- because
the interface is bilingual and translates codes; a sentence in the body would
exist in one language only.
"""

from datetime import date, datetime
from typing import Final, Literal

from pydantic import BaseModel
from sqlmodel import Field, SQLModel

# Stable code returned when a catalog entry does not exist. It is contract, not
# prose: the Spanish and English copy of the message lives in the frontend
# locales, keyed on this string.
ENTRY_NOT_FOUND: Final[str] = "catalogo_entrada_no_encontrada"

AttachedBy = Literal["campo", "consulta"]


class CatalogSource(SQLModel, table=True):
    """Mirror of ``catalog_source``: one documented data source of the bank.

    Attributes:
        id: Primary key, ``BIGSERIAL`` on the database side.
        code: Natural key of the source, for example ``creditos``.
        display_name: Business name of the source.
        description: What the source contains, in one paragraph.
        owner_area: Area that answers for the source.
        owner_name: Person that answers for the source.
        system_of_record: System the data is extracted from.
        has_extract: True only for the silos with a Parquet extract.
        created_at: Row creation timestamp, ``now()`` on the database side.
    """

    __tablename__ = "catalog_source"

    id: int | None = Field(default=None, primary_key=True)
    code: str
    display_name: str
    description: str
    owner_area: str
    owner_name: str
    system_of_record: str
    has_extract: bool = False
    created_at: datetime | None = None


class CatalogField(SQLModel, table=True):
    """Mirror of ``catalog_field``: one documented field of a source.

    Attributes:
        id: Primary key, ``BIGSERIAL`` on the database side.
        source_id: Foreign key to ``catalog_source``.
        physical_name: Column name as it exists in the system of record.
        business_name: Name a person uses for the field.
        definition: Business definition, curated and in Spanish.
        aliases: Synonyms separated by spaces, English equivalents included.
        domain: Business domain code.
        data_type: Data type code.
        sensitivity: Sensitivity code.
        refresh_frequency: Refresh frequency code.
        certification: Certification state code.
        unit: Unit code, or ``None`` when the field carries no unit.
        metric_agg: Default aggregation code, or ``None`` when it is not a
            measure.
        steward: Person that curates the definition.
        valid_from: First day the definition is in force.
        valid_to: Last day it was in force; ``None`` means still in force.
        created_at: Row creation timestamp, ``now()`` on the database side.
    """

    __tablename__ = "catalog_field"

    id: int | None = Field(default=None, primary_key=True)
    source_id: int = Field(foreign_key="catalog_source.id", index=True)
    physical_name: str
    business_name: str
    definition: str
    aliases: str = ""
    domain: str
    data_type: str
    sensitivity: str
    refresh_frequency: str
    certification: str
    unit: str | None = None
    metric_agg: str | None = None
    steward: str | None = None
    valid_from: date
    valid_to: date | None = None
    created_at: datetime | None = None


class CatalogTribalNote(SQLModel, table=True):
    """Mirror of ``catalog_tribal_note``: knowledge no schema publishes.

    Attributes:
        id: Primary key, ``BIGSERIAL`` on the database side.
        field_id: Foreign key to ``catalog_field``.
        note: The knowledge itself, written by a person.
        applicability: When the note applies, in prose, for the reader.
        applicability_terms: Trigger terms for the engine; an empty string
            means the note always applies.
        author: Who recorded it.
        recorded_at: When it was recorded.
        created_at: Row creation timestamp, ``now()`` on the database side.
    """

    __tablename__ = "catalog_tribal_note"

    id: int | None = Field(default=None, primary_key=True)
    field_id: int = Field(foreign_key="catalog_field.id", index=True)
    note: str
    applicability: str
    applicability_terms: str = ""
    author: str
    recorded_at: date
    created_at: datetime | None = None


# --- API contracts: codes only, never display labels -----------------------


class SourceRef(BaseModel):
    """Where the field lives.

    Attributes:
        code: Natural key of the source, and the value the ``source`` filter
            takes.
        display_name: Business name of the source.
        system_of_record: System the data is extracted from.
        has_extract: Whether the prototype holds a real extract of the source.
    """

    code: str
    display_name: str
    system_of_record: str
    has_extract: bool


class OwnerRef(BaseModel):
    """Who answers for the field. Already resolved: no coalesce in the client.

    Attributes:
        area: Area that owns the source.
        steward: Person that curates the field; falls back to the owner of the
            source when the field declares no steward of its own.
    """

    area: str
    steward: str


class Validity(BaseModel):
    """Effective period of the definition.

    Attributes:
        valid_from: First day the definition is in force.
        valid_to: Last day it was in force; ``None`` means still in force.
        is_current: Whether the definition is in force today. Computed by the
            database so that the filter and the flag cannot disagree.
    """

    valid_from: date
    valid_to: date | None
    is_current: bool


class Facets(BaseModel):
    """Filterable attributes. Every value is a stable code, never a label.

    Attributes:
        domain: Business domain code.
        data_type: Data type code.
        sensitivity: Sensitivity code.
        refresh_frequency: Refresh frequency code.
        certification: Certification state code.
        unit: Unit code, or ``None``.
        metric_agg: Default aggregation code, or ``None``.
    """

    domain: str
    data_type: str
    sensitivity: str
    refresh_frequency: str
    certification: str
    unit: str | None
    metric_agg: str | None


class TribalNoteOut(BaseModel):
    """A tribal note that survived its applicability check.

    Attributes:
        note: The knowledge itself.
        applicability: When it applies, in prose.
        author: Who recorded it.
        recorded_at: When it was recorded.
        attached_by: ``campo`` when the note always applies to the field,
            ``consulta`` when a term of the query triggered it. The panel uses
            it to tell "this is known about the data" from "this is relevant to
            what you asked".
    """

    note: str
    applicability: str
    author: str
    recorded_at: date
    attached_by: AttachedBy


class CatalogEntry(BaseModel):
    """One catalog entry as the metadata panel needs it.

    Attributes:
        field_id: Identifier of the entry, and the path parameter of the detail
            endpoint.
        physical_name: Column name in the system of record.
        business_name: Name a person uses for the field.
        definition: Business definition, in Spanish in both locales.
        source: Where the field lives.
        owner: Who answers for it.
        validity: Effective period of the definition.
        facets: Filterable attributes, as codes.
        tribal_notes: Notes that apply, each declaring how it got attached.
    """

    field_id: int
    physical_name: str
    business_name: str
    definition: str
    source: SourceRef
    owner: OwnerRef
    validity: Validity
    facets: Facets
    tribal_notes: list[TribalNoteOut]


class CatalogHit(CatalogEntry):
    """A catalog entry ranked against a query.

    Attributes:
        score: ``ts_rank`` with normalisation 32, so the value is bounded to
            ``[0, 1)`` and the panel can paint it as a bar without inventing a
            maximum. The hybrid phase of S5 adds a cosine term to this same
            field, which is why the contract already carries a bounded score.
    """

    score: float


class CatalogSearchResponse(BaseModel):
    """Payload of ``GET /api/catalog/search``.

    Attributes:
        query: What the user typed, echoed back.
        tsquery: What the engine actually ran. Empty when the query carried no
            usable term, which is the case that answers 200 with no results.
        total: Matches before pagination.
        limit: Page size that was applied.
        offset: Page offset that was applied.
        results: The page, ordered by descending score.
        facet_counts: Value counts per facet over the whole matching set, never
            over the page. Keyed by facet name; ``source`` is included because
            it is a filter, and the nullable facets only count the rows that
            carry a value.
    """

    query: str
    tsquery: str
    total: int
    limit: int
    offset: int
    results: list[CatalogHit]
    facet_counts: dict[str, dict[str, int]]
