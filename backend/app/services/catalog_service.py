"""Keyword search over the semantic catalog.

Phase one of the two phase plan: ``tsvector`` ranking only. The hybrid phase of
S5 adds a cosine term over the pgvector embedding without changing
``CatalogHit``, which is why the contract already carries a bounded score.

Every statement here is parameterised SQL. The text the user typed never
reaches the query string: it is reduced to whitelisted tokens by
``build_tsquery`` and handed to ``to_tsquery('spanish', :tsquery)`` as a bind
parameter. Two traps are avoided on purpose and both were verified against
PostgreSQL 15 before this module was written. ``CAST(:x AS tsquery)`` skips the
stemmer, so ``saldo`` would never match the stored lexeme ``sald`` and the SQL
would look correct while returning nothing; and ``websearch_to_tsquery``
combines terms with ``AND``, so a typed sentence would return zero results
almost always.

The only strings ever concatenated into a statement are the fixed clause
constants of this module, chosen by name from a closed mapping. No user value
is ever formatted into SQL.
"""

import re
import secrets
from collections.abc import Mapping, Sequence
from hashlib import sha256
from types import MappingProxyType
from typing import Any, Final

import structlog
from sqlalchemy import RowMapping, text
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.catalog import (
    CatalogEntry,
    CatalogHit,
    CatalogSearchResponse,
    Facets,
    OwnerRef,
    SourceRef,
    TribalNoteOut,
    Validity,
)

logger = structlog.get_logger()

# Salt of THIS process, drawn from the operating system entropy pool when the
# module is imported. It is never logged, never returned and never persisted.
#
# Without it the record is confirmable, which is the property a bare digest
# cannot lose: SHA-256 is public and a search box holds little entropy, so
# anybody who suspects that "4152313412341234" was typed hashes it themselves
# and greps the journal. With the username bound by ``structlog.contextvars``,
# one match names who typed it and when. The salt turns that guess into
# something unverifiable from outside the process.
#
# The price, written down so that nobody later reads it as a defect: the
# digests are NOT comparable across restarts nor across instances. On Cloud Run
# with scale-to-zero, two searches separated by a cold start hash the same text
# differently, and two replicas never agree on a value. That is the correct
# trade. The correlation the field is read for -the repeated searches of one
# reader inside one session- happens within a single process, and the
# alternative, a fixed salt kept in configuration, is one more credential to
# rotate and to leak, and the day it leaks it hands the whole property back.
_QUERY_SALT: Final[bytes] = secrets.token_bytes(32)

# A pasted paragraph must not become a three hundred term tsquery.
MAX_TERMS: Final[int] = 12

# One character tokens are dropped: with the prefix operator a single letter
# drags a good part of the catalog into the result set.
MIN_TOKEN_LENGTH: Final[int] = 2

# The whitelist is the defence against tsquery injection, not an escape. The
# accented letters are part of it because the stemmer normalises accents only
# when it receives the whole word: with ``[0-9a-z_]`` the word "credito" with
# an accent would be split into "cr" and "dito".
TOKEN_PATTERN: Final[re.Pattern[str]] = re.compile(r"[0-9a-záéíóúüñ_]+")

# D, C, B, A. business_name wins over physical_name and aliases, and those win
# over the definition: an occurrence in the prose is a hint, not an answer.
RANK_WEIGHTS: Final[str] = "{0.1,0.2,0.4,1.0}"

# Bounds ts_rank to [0, 1) as rank/(rank+1). The contract publishes the score
# without post-processing, so losing this flag would break any progress bar.
RANK_NORMALISATION: Final[int] = 32

DEFAULT_LIMIT: Final[int] = 10
DEFAULT_OFFSET: Final[int] = 0

# Facet dimensions counted over the matching set. ``source`` is here because it
# is a filter of the endpoint; the two nullable dimensions only count the rows
# that carry a value.
FACET_NAMES: Final[tuple[str, ...]] = (
    "source",
    "domain",
    "data_type",
    "sensitivity",
    "refresh_frequency",
    "certification",
    "unit",
    "metric_agg",
)

# --- SQL fragments ---------------------------------------------------------
# Assembled with ``"\n".join`` over these constants and never with a format
# string, so that no code path exists in which a value could be interpolated.

_WITH_QUERY: Final[str] = "WITH q AS (SELECT to_tsquery('spanish', :tsquery) AS query)"

_ENTRY_COLUMNS: Final[str] = """       f.id AS field_id,
       f.physical_name,
       f.business_name,
       f.definition,
       f.domain,
       f.data_type,
       f.sensitivity,
       f.refresh_frequency,
       f.certification,
       f.unit,
       f.metric_agg,
       f.steward,
       f.valid_from,
       f.valid_to,
       (f.valid_to IS NULL OR f.valid_to >= CURRENT_DATE) AS is_current,
       s.code AS source_code,
       s.display_name AS source_display_name,
       s.system_of_record AS source_system_of_record,
       s.has_extract AS source_has_extract,
       s.owner_area AS owner_area,
       s.owner_name AS owner_name"""

_SCORE_COLUMN: Final[str] = "".join(
    [
        "     , ts_rank(CAST(:rank_weights AS float4[]),\n",
        "               f.search_document, q.query, ",
        str(RANK_NORMALISATION),
        ") AS score",
    ]
)

_FROM_RANKED: Final[str] = """  FROM catalog_field f
  JOIN catalog_source s ON s.id = f.source_id
 CROSS JOIN q"""

_FROM_PLAIN: Final[str] = """  FROM catalog_field f
  JOIN catalog_source s ON s.id = f.source_id"""

_MATCH_PREDICATE: Final[str] = "f.search_document @@ q.query"

# Sorting by score alone would leave ties in whatever order the planner
# produced, and a page that reshuffles between two identical requests is a page
# nobody can paginate. The identifier closes the order.
_ORDER_AND_PAGE: Final[str] = """ ORDER BY score DESC, f.business_name ASC, f.id ASC
 LIMIT :limit OFFSET :offset"""

_COUNT_HEAD: Final[str] = "\n".join(
    [_WITH_QUERY, "SELECT count(*) AS total", _FROM_RANKED, "WHERE"]
)

_SEARCH_HEAD: Final[str] = "\n".join(
    [_WITH_QUERY, "SELECT", _ENTRY_COLUMNS, _SCORE_COLUMN, _FROM_RANKED, "WHERE"]
)

_FACET_HEAD: Final[str] = "\n".join(
    [
        _WITH_QUERY + ",",
        """     matched AS (
       SELECT s.code AS source_code,
              f.domain,
              f.data_type,
              f.sensitivity,
              f.refresh_frequency,
              f.certification,
              f.unit,
              f.metric_agg
         FROM catalog_field f
         JOIN catalog_source s ON s.id = f.source_id
        CROSS JOIN q
        WHERE""",
    ]
)

_FACET_TAIL: Final[str] = """     )
SELECT 'source' AS facet, source_code AS value, count(*) AS total
  FROM matched GROUP BY source_code
UNION ALL
SELECT 'domain', domain, count(*) FROM matched GROUP BY domain
UNION ALL
SELECT 'data_type', data_type, count(*) FROM matched GROUP BY data_type
UNION ALL
SELECT 'sensitivity', sensitivity, count(*) FROM matched GROUP BY sensitivity
UNION ALL
SELECT 'refresh_frequency', refresh_frequency, count(*)
  FROM matched GROUP BY refresh_frequency
UNION ALL
SELECT 'certification', certification, count(*)
  FROM matched GROUP BY certification
UNION ALL
SELECT 'unit', unit, count(*)
  FROM matched WHERE unit IS NOT NULL GROUP BY unit
UNION ALL
SELECT 'metric_agg', metric_agg, count(*)
  FROM matched WHERE metric_agg IS NOT NULL GROUP BY metric_agg"""

_DETAIL_STATEMENT: Final[str] = "\n".join(
    [
        "SELECT",
        _ENTRY_COLUMNS,
        _FROM_PLAIN,
        " WHERE f.id = :entry_id",
    ]
)

# The applicability check is the whole Tk-Boost pattern: same engine, same
# accent normalisation, no rule interpreter. An empty ``applicability_terms``
# means the note always applies.
_NOTES_MATCHING_STATEMENT: Final[str] = """WITH q AS (
       SELECT to_tsquery('spanish', :tsquery) AS query)
SELECT n.field_id,
       n.note,
       n.applicability,
       n.author,
       n.recorded_at,
       (n.applicability_terms = '') AS always_applies
  FROM catalog_tribal_note n
 CROSS JOIN q
 WHERE n.field_id = ANY(CAST(:field_ids AS bigint[]))
   AND (n.applicability_terms = ''
        OR to_tsvector('spanish', n.applicability_terms) @@ q.query)
 ORDER BY n.field_id ASC, n.recorded_at DESC, n.id ASC"""

_NOTES_ALWAYS_STATEMENT: Final[str] = """SELECT n.field_id,
       n.note,
       n.applicability,
       n.author,
       n.recorded_at,
       true AS always_applies
  FROM catalog_tribal_note n
 WHERE n.field_id = ANY(CAST(:field_ids AS bigint[]))
   AND n.applicability_terms = ''
 ORDER BY n.field_id ASC, n.recorded_at DESC, n.id ASC"""

# Closed mapping from filter name to its clause. The service picks clauses by
# name; nothing that arrives in a request ever becomes SQL.
_FILTER_CLAUSES: Final[Mapping[str, str]] = MappingProxyType(
    {
        "sources": "s.code = ANY(CAST(:sources AS text[]))",
        "domains": "f.domain = ANY(CAST(:domains AS text[]))",
        "sensitivities": "f.sensitivity = ANY(CAST(:sensitivities AS text[]))",
        "certifications": "f.certification = ANY(CAST(:certifications AS text[]))",
    }
)

_ONLY_CURRENT_CLAUSE: Final[str] = "(f.valid_to IS NULL OR f.valid_to >= CURRENT_DATE)"


def build_tsquery(raw_query: str) -> str:
    """Turn a free text query into a safe OR tsquery with a prefix last term.

    Only whitelisted tokens survive, so the result can never carry tsquery
    operators typed by the user. The terms are joined with ``OR`` and not with
    ``AND``: people type sentences, and six terms combined with ``AND`` return
    nothing almost always. Precision is the job of the ranking, which grows
    with the number of lexemes that match. The last token gets ``:*`` so that
    typing forward keeps matching.

    Args:
        raw_query: What the user typed.

    Returns:
        A tsquery source string such as ``sald | venc | carter:*``. Empty when
        no usable token remains, which the caller must treat as "no results"
        rather than as an error.
    """
    tokens = [
        token
        for token in TOKEN_PATTERN.findall(raw_query.lower())
        if len(token) >= MIN_TOKEN_LENGTH
    ][:MAX_TERMS]
    if not tokens:
        return ""
    tokens[-1] = f"{tokens[-1]}:*"
    return " | ".join(tokens)


def query_fingerprint(raw_query: str) -> str:
    """Return the per process fingerprint of a typed query.

    Equal texts give equal fingerprints for as long as this process lives, and
    that is the entire contract: it is what lets a reader's repeated searches be
    told apart in the journal. Nothing else may be inferred from the value, and
    in particular it must not be compared against a digest computed anywhere
    else, because the salt of ``_QUERY_SALT`` is unique to this process.

    Args:
        raw_query: The text exactly as the user typed it.

    Returns:
        A hexadecimal digest, meaningless outside this process.
    """
    return sha256(_QUERY_SALT + raw_query.encode("utf-8")).hexdigest()


async def search(
    session: AsyncSession,
    *,
    raw_query: str,
    sources: Sequence[str] | None = None,
    domains: Sequence[str] | None = None,
    sensitivities: Sequence[str] | None = None,
    certifications: Sequence[str] | None = None,
    only_current: bool = True,
    limit: int = DEFAULT_LIMIT,
    offset: int = DEFAULT_OFFSET,
) -> CatalogSearchResponse:
    """Rank catalog entries against a keyword query.

    Args:
        session: Async session provided by the request scope.
        raw_query: Free text typed by the user.
        sources: Optional source codes to keep.
        domains: Optional business domains to keep.
        sensitivities: Optional sensitivity codes to keep.
        certifications: Optional certification codes to keep.
        only_current: When true, entries whose validity is already closed are
            excluded.
        limit: Page size, already validated by the router.
        offset: Page offset, already validated by the router.

    Returns:
        The full response payload, tribal notes attached and facets counted
        over the whole matching set.
    """
    tsquery = build_tsquery(raw_query)
    if not tsquery:
        # A query with no usable term is not a client error and it is not a
        # trip to the database either: an empty tsquery matches nothing by
        # definition.
        logger.info("catalogo_busqueda_sin_terminos", limit=limit, offset=offset)
        return CatalogSearchResponse(
            query=raw_query,
            tsquery="",
            total=0,
            limit=limit,
            offset=offset,
            results=[],
            facet_counts={},
        )

    clauses, params = _filters(
        sources=sources,
        domains=domains,
        sensitivities=sensitivities,
        certifications=certifications,
        only_current=only_current,
    )
    params["tsquery"] = tsquery
    where = " AND ".join([_MATCH_PREDICATE, *clauses])

    total = await _count(session, where, params)
    rows = await _page(session, where, params, limit=limit, offset=offset)
    notes = await _attach_tribal_notes(
        session, [int(row["field_id"]) for row in rows], tsquery
    )
    facet_counts = await _count_facets(session, where, params)

    # The tsquery is NOT logged, and the omission is the point. build_tsquery
    # does not lemmatise: it lowercases and splits, so the terms survive almost
    # literally -an account number or an address typed into the box comes back
    # out whole- and structlog.contextvars has the username bound by this point.
    # That single line would correlate an identity with free text the user
    # typed, which is the same rule that keeps raw prompts out of the traces.
    # The fingerprint keeps the only property the log needs: telling repeated
    # searches apart without being able to read -or to confirm- any of them.
    logger.info(
        "catalogo_busqueda",
        consulta_hash=query_fingerprint(raw_query),
        terminos=tsquery.count("|") + 1,
        total=total,
        devueltos=len(rows),
        limit=limit,
        offset=offset,
    )
    return CatalogSearchResponse(
        query=raw_query,
        tsquery=tsquery,
        total=total,
        limit=limit,
        offset=offset,
        results=[
            CatalogHit(
                score=float(row["score"]),
                **_entry_fields(row, notes.get(int(row["field_id"]), [])),
            )
            for row in rows
        ],
        facet_counts=facet_counts,
    )


async def get_entry(
    session: AsyncSession, entry_id: int, *, raw_query: str | None = None
) -> CatalogEntry | None:
    """Return one catalog entry by its identifier.

    Args:
        session: Async session provided by the request scope.
        entry_id: Identifier of the entry, as ``field_id`` publishes it.
        raw_query: Query the reader arrived with, when there is one. Notes
            conditioned on a term are attached only when that term is in it;
            without a query the entry carries the notes that always apply.

    Returns:
        The entry, or ``None`` when no field carries that identifier.
    """
    rows = await _rows(session, _DETAIL_STATEMENT, {"entry_id": entry_id})
    if not rows:
        return None
    row = rows[0]

    tsquery = build_tsquery(raw_query) if raw_query else ""
    notes = await _attach_tribal_notes(session, [entry_id], tsquery)
    return CatalogEntry(**_entry_fields(row, notes.get(entry_id, [])))


async def _rows(
    session: AsyncSession, statement: str, params: dict[str, Any]
) -> Sequence[RowMapping]:
    """Run one statement on the connection of the session and map its rows.

    The connection of the session is used instead of ``session.execute`` on
    purpose: SQLModel deprecates that method in favour of ``exec``, and ``exec``
    is typed for ``select`` statements, not for the textual SQL this module
    sends. Going through the connection keeps the work inside the transaction
    of the request and out of the deprecation path.

    Args:
        session: Async session provided by the request scope.
        statement: Assembled SQL, with named bind parameters.
        params: Values of those parameters.

    Returns:
        The rows, as mappings keyed by column label.
    """
    connection = await session.connection()
    result = await connection.execute(text(statement), params)
    return result.mappings().all()


async def _count(session: AsyncSession, where: str, params: dict[str, Any]) -> int:
    """Count the entries that match, ignoring pagination.

    Args:
        session: Async session provided by the request scope.
        where: Predicate shared by every statement of the search.
        params: Bind parameters of that predicate.

    Returns:
        The number of matching entries.
    """
    rows = await _rows(session, "\n".join([_COUNT_HEAD, where]), params)
    return 0 if not rows else int(rows[0]["total"])


async def _page(
    session: AsyncSession,
    where: str,
    params: dict[str, Any],
    *,
    limit: int,
    offset: int,
) -> Sequence[RowMapping]:
    """Fetch one ranked page of entries.

    Args:
        session: Async session provided by the request scope.
        where: Predicate shared by every statement of the search.
        params: Bind parameters of that predicate.
        limit: Page size.
        offset: Page offset.

    Returns:
        The rows of the page, ordered by descending score.
    """
    return await _rows(
        session,
        "\n".join([_SEARCH_HEAD, where, _ORDER_AND_PAGE]),
        {
            **params,
            "rank_weights": RANK_WEIGHTS,
            "limit": limit,
            "offset": offset,
        },
    )


async def _attach_tribal_notes(
    session: AsyncSession, field_ids: list[int], tsquery: str
) -> dict[int, list[TribalNoteOut]]:
    """Fetch the notes of the page in one query and filter by applicability.

    One query for the whole page, never one per hit: an N+1 is the only way a
    catalog of a few hundred rows becomes slow.

    Args:
        session: Async session provided by the request scope.
        field_ids: Identifiers of the entries of the page.
        tsquery: Compiled query. Empty means only the notes that always apply.

    Returns:
        The notes of each entry, indexed by identifier. Entries without notes
        are absent from the mapping.
    """
    if not field_ids:
        return {}

    statement = _NOTES_MATCHING_STATEMENT if tsquery else _NOTES_ALWAYS_STATEMENT
    params: dict[str, Any] = {"field_ids": field_ids}
    if tsquery:
        params["tsquery"] = tsquery

    notes: dict[int, list[TribalNoteOut]] = {}
    for row in await _rows(session, statement, params):
        notes.setdefault(int(row["field_id"]), []).append(
            TribalNoteOut(
                note=row["note"],
                applicability=row["applicability"],
                author=row["author"],
                recorded_at=row["recorded_at"],
                attached_by="campo" if row["always_applies"] else "consulta",
            )
        )
    return notes


async def _count_facets(
    session: AsyncSession, where: str, params: dict[str, Any]
) -> dict[str, dict[str, int]]:
    """Count every facet value over the matching set, ignoring pagination.

    The counts are what the filter panel paints next to each value, so they
    have to describe the whole result and not the page: a facet showing "3"
    where there are forty is worse than no count at all.

    Args:
        session: Async session provided by the request scope.
        where: Predicate shared by every statement of the search.
        params: Bind parameters of that predicate.

    Returns:
        Value counts per facet name. Facets with no value present in the
        matching set come back as empty mappings, so the panel can render every
        dimension without probing for keys.
    """
    statement = "\n".join([_FACET_HEAD, where, _FACET_TAIL])
    counts: dict[str, dict[str, int]] = {name: {} for name in FACET_NAMES}
    for row in await _rows(session, statement, params):
        counts.setdefault(str(row["facet"]), {})[str(row["value"])] = int(row["total"])
    return counts


def _filters(
    *,
    sources: Sequence[str] | None,
    domains: Sequence[str] | None,
    sensitivities: Sequence[str] | None,
    certifications: Sequence[str] | None,
    only_current: bool,
) -> tuple[tuple[str, ...], dict[str, Any]]:
    """Pick the clauses of the active filters and bind their values.

    Args:
        sources: Source codes to keep, or ``None``.
        domains: Business domains to keep, or ``None``.
        sensitivities: Sensitivity codes to keep, or ``None``.
        certifications: Certification codes to keep, or ``None``.
        only_current: Whether to exclude entries with a closed validity.

    Returns:
        The clauses, taken from the closed mapping of this module, and the bind
        parameters that feed them.
    """
    requested: Mapping[str, Sequence[str] | None] = {
        "sources": sources,
        "domains": domains,
        "sensitivities": sensitivities,
        "certifications": certifications,
    }
    clauses: list[str] = []
    params: dict[str, Any] = {}
    for name, values in requested.items():
        if not values:
            continue
        clauses.append(_FILTER_CLAUSES[name])
        params[name] = list(values)
    if only_current:
        clauses.append(_ONLY_CURRENT_CLAUSE)
    return tuple(clauses), params


def _entry_fields(row: RowMapping, notes: list[TribalNoteOut]) -> dict[str, Any]:
    """Map one result row onto the fields every catalog contract shares.

    Args:
        row: Row as the statements of this module select it.
        notes: Tribal notes already filtered by applicability.

    Returns:
        The keyword arguments of ``CatalogEntry``, so that ``CatalogHit`` only
        has to add its score.
    """
    return {
        "field_id": int(row["field_id"]),
        "physical_name": row["physical_name"],
        "business_name": row["business_name"],
        "definition": row["definition"],
        "source": SourceRef(
            code=row["source_code"],
            display_name=row["source_display_name"],
            system_of_record=row["source_system_of_record"],
            has_extract=bool(row["source_has_extract"]),
        ),
        # The fallback is resolved here and not in the client: a field without
        # its own steward answers to whoever owns the source, and making the
        # panel do that coalesce is how two screens end up disagreeing.
        "owner": OwnerRef(
            area=row["owner_area"],
            steward=row["steward"] or row["owner_name"],
        ),
        "validity": Validity(
            valid_from=row["valid_from"],
            valid_to=row["valid_to"],
            is_current=bool(row["is_current"]),
        ),
        "facets": Facets(
            domain=row["domain"],
            data_type=row["data_type"],
            sensitivity=row["sensitivity"],
            refresh_frequency=row["refresh_frequency"],
            certification=row["certification"],
            unit=row["unit"],
            metric_agg=row["metric_agg"],
        ),
        "tribal_notes": notes,
    }
