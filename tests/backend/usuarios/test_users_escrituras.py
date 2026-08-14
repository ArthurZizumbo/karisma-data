"""The two statements that write ``app_user``, as PostgreSQL would receive them.

The suite runs without PostgreSQL, so the subject here is not a database: it is
the text ``SqlAdminUserRepository`` builds, compiled with the PostgreSQL dialect
and read. That is the technique the other statement tests of this package
already use, and what it measures is production code -never a double, never a
connection-.

Both defects below are invisible from HTTP. The in-memory repository of
``conftest.py`` stamps the modification itself and writes by primary key by
construction, so the endpoint would keep answering a fresh ``updated_at`` and a
single changed row while the deployed statement did neither. What the projection
tests cover is the list of columns read back; the ``SET`` clause and the
``WHERE`` clause of these two writes were nobody's subject until here.
"""

import uuid
from collections.abc import Awaitable, Callable
from typing import Final

import pytest

from app.core.scopes import Scope
from app.services.user_service import SqlAdminUserRepository

from .conftest import SesionEspia, sql_de

# Row every write in this module aims at. Any key works: what is under test is
# the shape of the statement, not the row it would find.
DESTINO: Final[uuid.UUID] = uuid.UUID(int=1)

type Escritura = Callable[[SqlAdminUserRepository], Awaitable[None]]


async def cambiar_rol(repositorio: SqlAdminUserRepository) -> None:
    """Ask the repository for the role write.

    Args:
        repositorio: Repository bound to the spy session.
    """
    await repositorio.update_role(DESTINO, Scope.OPERATIVO)


async def desactivar(repositorio: SqlAdminUserRepository) -> None:
    """Ask the repository for the soft delete write.

    Args:
        repositorio: Repository bound to the spy session.
    """
    await repositorio.set_disabled(DESTINO, disabled=True)


# One parameter per statement, so a defect in only one of the two writes is
# reported by name instead of hiding behind the other.
ESCRITURAS = [
    pytest.param(cambiar_rol, id="update_role"),
    pytest.param(desactivar, id="set_disabled"),
]


@pytest.mark.asyncio
@pytest.mark.parametrize("escritura", ESCRITURAS)
async def test_las_dos_escrituras_fechan_la_modificacion_con_el_reloj_de_la_base(
    sesion_espia: SesionEspia, escritura: Escritura
) -> None:
    """The stamp is written in the same statement that changes the row.

    Dropping ``updated_at`` from the ``values`` leaves the only audit trail this
    screen has frozen at the creation of the account -the substitute the US
    accepted when the access log went to the roadmap- and no test over HTTP
    would notice, because the double moves the stamp on its own and the body
    keeps arriving with a newer date.

    The assertion names ``now()`` and not a bound parameter for a second defect
    of the same line: a stamp taken from the application clock drifts from the
    ``created_at`` the database wrote, and two dates of the same row would then
    come from two clocks.
    """
    repositorio = SqlAdminUserRepository(sesion_espia)  # type: ignore[arg-type]

    await escritura(repositorio)

    asignaciones = sql_de(sesion_espia.sentencias[0]).split(" WHERE ")[0]
    assert "updated_at=now()" in asignaciones


@pytest.mark.asyncio
@pytest.mark.parametrize("escritura", ESCRITURAS)
async def test_las_dos_escrituras_alcanzan_una_sola_fila_por_su_clave(
    sesion_espia: SesionEspia, escritura: Escritura
) -> None:
    """An update without its ``WHERE`` changes every account of the portal.

    ``_write`` already shares the execution and the commit of both statements,
    and moving their construction in there is the refactor that loses the
    clause. Nothing downstream would report it: the statement matches every row,
    ``result.first()`` hands back a plausible one and the endpoint answers 200
    with it. The double of this package cannot show the defect either, because
    it looks the row up by key before writing it.
    """
    repositorio = SqlAdminUserRepository(sesion_espia)  # type: ignore[arg-type]

    await escritura(repositorio)

    assert "WHERE app_user.id = " in sql_de(sesion_espia.sentencias[0])
