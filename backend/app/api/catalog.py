"""Catalog endpoints. They receive, delegate and answer: no logic here.

Both routes sit behind ``Security(get_current_user)`` with no scope: the
permission matrix reads "catalogo para todos los autenticados", and a scope
list copied from an analytical router would lock the operational profile out of
the screen the catalog exists for. The security dependency is declared first on
purpose, so an anonymous request is answered before a database session is
opened for it.

The bodies carry stable codes and never sentences. The interface is bilingual
and translates them; a sentence here would exist in one language only.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Security, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.auth import get_current_user
from app.core.database import get_session
from app.models.catalog import (
    ENTRY_NOT_FOUND,
    CatalogEntry,
    CatalogSearchResponse,
)
from app.models.user import UserOut
from app.services import catalog_service

router = APIRouter(prefix="/api/catalog", tags=["catalogo"])


@router.get(
    "/search",
    response_model=CatalogSearchResponse,
    summary="Busqueda del catalogo por palabra clave",
)
async def search_catalog(
    current_user: Annotated[UserOut, Security(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
    q: Annotated[str, Query(min_length=2, max_length=120)],
    source: Annotated[list[str] | None, Query()] = None,
    domain: Annotated[list[str] | None, Query()] = None,
    sensitivity: Annotated[list[str] | None, Query()] = None,
    certification: Annotated[list[str] | None, Query()] = None,
    only_current: Annotated[bool, Query()] = True,
    limit: Annotated[int, Query(ge=1, le=50)] = 10,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> CatalogSearchResponse:
    """Rank catalog entries for any authenticated user.

    Args:
        current_user: Caller resolved by the security dependency. The catalog
            is the same for every role, so the identity is only the guard.
        session: Session bound to the request.
        q: Free text typed by the user.
        source: Source codes to keep; repeat the parameter to send several.
        domain: Business domains to keep.
        sensitivity: Sensitivity codes to keep.
        certification: Certification codes to keep.
        only_current: When true, entries with a closed validity are excluded.
        limit: Page size.
        offset: Page offset.

    Returns:
        The ranked page, its facet counts over the whole matching set and the
        tsquery the engine actually ran.
    """
    return await catalog_service.search(
        session,
        raw_query=q,
        sources=source,
        domains=domain,
        sensitivities=sensitivity,
        certifications=certification,
        only_current=only_current,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/{entry_id}",
    response_model=CatalogEntry,
    summary="Ficha de una entrada del catalogo",
)
async def read_catalog_entry(
    current_user: Annotated[UserOut, Security(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
    entry_id: Annotated[int, Path(ge=1)],
    q: Annotated[str | None, Query(max_length=120)] = None,
) -> CatalogEntry:
    """Return the metadata of one catalog entry.

    Args:
        current_user: Caller resolved by the security dependency.
        session: Session bound to the request.
        entry_id: Identifier of the entry, as ``field_id`` publishes it.
        q: Query the reader arrived with, optional. Passing it back attaches
            the tribal notes that term triggers, which is what tells "known
            about this data" from "relevant to what you asked".

    Returns:
        The entry, without a score: there is no ranking outside a search.

    Raises:
        HTTPException: 404 with the code ``catalogo_entrada_no_encontrada``
            when no field carries that identifier.
    """
    entry = await catalog_service.get_entry(session, entry_id, raw_query=q)
    if entry is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=ENTRY_NOT_FOUND
        )
    return entry
