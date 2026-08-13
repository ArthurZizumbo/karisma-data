"""Lineage endpoint. It receives, delegates and answers: no logic here.

The route is its own router and not a third operation of ``api/catalog.py``:
that module belongs to US-008 and its detail route -``GET /api/catalog/{entry_id}``-
is deferred to S5 by its own plan. The journey is fetched on demand, only when
the reader opens the overlay, so hanging it off the search response would ship
twenty lineages to render one.

It sits behind ``Security(get_current_user)`` with no scope, the same rule the
matrix states for the catalog: the operational profile is precisely the one
that needs to see where a figure comes from before trusting it. The security
dependency is declared first on purpose, so an anonymous request is answered
before a database session is opened for it.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Security, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.auth import get_current_user
from app.core.database import get_session
from app.models.lineage import ErrorLinaje, FieldLineageResponse, LineageErrorCode
from app.models.user import UserOut
from app.services import lineage_service

router = APIRouter(prefix="/api/catalog", tags=["linaje"])


@router.get(
    "/{entry_id}/lineage",
    response_model=FieldLineageResponse,
    summary="Linaje de un campo del catalogo",
)
async def read_field_lineage(
    current_user: Annotated[UserOut, Security(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
    entry_id: Annotated[int, Path(ge=1)],
) -> FieldLineageResponse:
    """Serve the journey of a catalog field to any authenticated reader.

    Args:
        current_user: Caller resolved by the security dependency. The lineage
            is the same for every role, so the identity is only the guard.
        session: Session bound to the request.
        entry_id: Identifier of the entry, as ``field_id`` publishes it.

    Returns:
        The five hops of the journey: four stored and the derived terminal one.

    Raises:
        HTTPException: 404 with the code ``campo_no_encontrado`` when no field
            carries that identifier, which the screen renders as its designed
            error state instead of as an empty panel.
    """
    try:
        return await lineage_service.get_field_lineage(session, entry_id=entry_id)
    except lineage_service.FieldNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ErrorLinaje(
                codigo=LineageErrorCode.CAMPO_NO_ENCONTRADO, entry_id=entry_id
            ).as_detail(),
        ) from error
