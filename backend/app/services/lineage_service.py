"""Assemble the lineage of a catalog field.

Two queries and one composition, never one per step: a round trip per hop is
how a five row answer becomes slow, and with a seeded catalog of twelve sources
the N+1 would be invisible until the day the catalog grows.

The upstream stretch is read from ``catalog_lineage_step``, which hangs from
the source. The terminal hop is composed here from the catalog entry itself and
is marked ``stored=False``, because storing it would duplicate columns
``catalog_field`` already owns and create a second truth for the same fact.
"""

from datetime import date

import structlog
from sqlmodel import col, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.catalog import CatalogField, CatalogSource, Facets, OwnerRef, SourceRef
from app.models.catalog import Validity as CatalogValidity
from app.models.lineage import (
    FIELD_PUBLISH_CODE,
    PRESENTATION_SYSTEM_CODE,
    PRESENTATION_SYSTEM_NAME,
    CatalogLineageStep,
    FieldLineageResponse,
    LineageStage,
    LineageStepOut,
)

logger = structlog.get_logger()


class FieldNotFoundError(LookupError):
    """Raised when the requested catalog field does not exist."""


async def get_field_lineage(
    session: AsyncSession, *, entry_id: int
) -> FieldLineageResponse:
    """Return the five step journey of a field.

    Args:
        session: Async session provided by the request scope.
        entry_id: Primary key of ``catalog_field``.

    Returns:
        The stored hops of the owning source, in step order, plus the derived
        presentation step.

    Raises:
        FieldNotFoundError: When no catalog field carries that identifier.
    """
    entry = await _fetch_entry(session, entry_id)
    if entry is None:
        # The typed failure is raised here and translated to HTTP by the
        # router: a service that knew about status codes could not be reused by
        # the agent tools of US-020 without dragging FastAPI along.
        raise FieldNotFoundError(str(entry_id))

    field, source = entry
    rows = await _fetch_steps(session, source_id=field.source_id)
    steps = [_step_out(row) for row in rows]
    steps.append(build_presentation_step(field, source, len(steps) + 1))

    logger.info(
        "linaje_de_campo",
        entry_id=entry_id,
        fuente=source.code,
        pasos_sembrados=len(rows),
        pasos=len(steps),
    )
    return FieldLineageResponse(
        field_id=entry_id,
        physical_name=field.physical_name,
        business_name=field.business_name,
        source=SourceRef(
            code=source.code,
            display_name=source.display_name,
            system_of_record=source.system_of_record,
            has_extract=source.has_extract,
        ),
        owner=resolve_owner(field, source),
        validity=CatalogValidity(
            valid_from=field.valid_from,
            valid_to=field.valid_to,
            is_current=in_force(field.valid_to),
        ),
        facets=Facets(
            domain=field.domain,
            data_type=field.data_type,
            sensitivity=field.sensitivity,
            refresh_frequency=field.refresh_frequency,
            certification=field.certification,
            unit=field.unit,
            metric_agg=field.metric_agg,
        ),
        steps=steps,
    )


def build_presentation_step(
    field: CatalogField, source: CatalogSource, order: int
) -> LineageStepOut:
    """Compose the terminal step from the catalog entry itself.

    It is not persisted on purpose: storing it would duplicate columns that
    ``catalog_field`` already owns, and the first correction of a definition
    would leave the lineage saying one thing and the dictionary another, with
    nothing to detect it.

    Args:
        field: Catalog entry the journey ends at.
        source: Source that owns the entry, used to resolve the owner.
        order: Position of the hop, one past the last stored one.

    Returns:
        The derived hop, marked ``stored=False`` so the reader can tell what is
        kept from what is composed.
    """
    return LineageStepOut(
        order=order,
        stage=LineageStage.PRESENTACION,
        system_code=PRESENTATION_SYSTEM_CODE,
        system_name=PRESENTATION_SYSTEM_NAME,
        transformation_code=FIELD_PUBLISH_CODE,
        # The physical name is the datum the template interpolates: the hop
        # answers "this is the column behind the figure", and the column is
        # data, not a label to translate.
        transformation_detail=field.physical_name,
        owner=resolve_owner(field, source),
        effective_from=field.valid_from,
        effective_to=field.valid_to,
        is_current=in_force(field.valid_to),
        stored=False,
    )


def resolve_owner(field: CatalogField, source: CatalogSource) -> OwnerRef:
    """Return who answers for the field: steward first, source owner after.

    Resolved on the server so the client never writes a coalesce. US-008 made
    that rule for the metadata panel and the overlay honours the same one: two
    screens doing the same fallback is how they end up disagreeing.

    Args:
        field: Catalog entry.
        source: Source that owns it.

    Returns:
        The area of the source and the person that answers for the field.
    """
    return OwnerRef(area=source.owner_area, steward=field.steward or source.owner_name)


def in_force(effective_to: date | None) -> bool:
    """Report whether a period that ends on that date is in force today.

    Args:
        effective_to: Last day of the period, or ``None`` when it is open.

    Returns:
        ``True`` when the period is open or has not ended yet.
    """
    return effective_to is None or effective_to >= date.today()


async def _fetch_entry(
    session: AsyncSession, entry_id: int
) -> tuple[CatalogField, CatalogSource] | None:
    """Read the catalog entry and its source in one statement.

    Args:
        session: Async session provided by the request scope.
        entry_id: Primary key of ``catalog_field``.

    Returns:
        The entry and its source, or ``None`` when the identifier is unknown.
    """
    statement = (
        select(CatalogField, CatalogSource)
        .join(
            CatalogSource, onclause=col(CatalogSource.id) == col(CatalogField.source_id)
        )
        .where(col(CatalogField.id) == entry_id)
    )
    result = await session.exec(statement)
    return result.first()


async def _fetch_steps(
    session: AsyncSession, *, source_id: int
) -> list[CatalogLineageStep]:
    """Read the stored hops of a source, in journey order.

    The order is taken from ``step_order`` and never from the identifier: rows
    inserted in another order would make the journey start at the quality
    control, and the unique index of the migration is exactly this prefix.

    Args:
        session: Async session provided by the request scope.
        source_id: Identifier of the source that owns the journey.

    Returns:
        The hops, ordered.
    """
    statement = (
        select(CatalogLineageStep)
        .where(col(CatalogLineageStep.source_id) == source_id)
        .order_by(col(CatalogLineageStep.step_order))
    )
    result = await session.exec(statement)
    return list(result.all())


def _step_out(row: CatalogLineageStep) -> LineageStepOut:
    """Map one stored hop onto the response contract.

    Args:
        row: Row of ``catalog_lineage_step``.

    Returns:
        The hop, marked ``stored=True``.
    """
    return LineageStepOut(
        order=row.step_order,
        stage=LineageStage(row.stage),
        system_code=row.system_code,
        system_name=row.system_name,
        transformation_code=row.transformation_code,
        transformation_detail=row.transformation_detail,
        owner=OwnerRef(area=row.owner_area, steward=row.owner_name),
        effective_from=row.effective_from,
        effective_to=row.effective_to,
        is_current=in_force(row.effective_to),
        stored=True,
    )
