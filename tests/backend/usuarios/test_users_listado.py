"""The shape of the page, its order and the window the database really cuts.

Two subjects and two techniques, because the defects live in different layers.
Over HTTP the subject is the contract: a bare array instead of an object is a
breaking change no client can absorb silently, and a ``total`` computed over the
page instead of over the table turns "7 users" into "1 user" on the last page.
Under it, the subject is the statement ``SqlAdminUserRepository`` builds: the
suite runs without PostgreSQL, so the statement is compiled with the PostgreSQL
dialect and read. That is what catches an ordering left to the planner -which
would move the rows of the A4 capture on every run- and a page sliced in Python
after reading the whole table.
"""

import uuid
from datetime import UTC, datetime
from typing import Final

import pytest
from fastapi.testclient import TestClient

from app.core.scopes import Scope
from app.services.user_service import (
    SqlAdminUserRepository,
    get_admin_user_repository,
)

from .conftest import SesionEspia, sql_de

# The seven seeded users in the order the endpoint promises. Written out and not
# derived from the seed: this literal is the order of the A4 capture, so a change
# to it has to be a decision and not a side effect.
ORDEN_ESPERADO: Final[tuple[str, ...]] = (
    "acastaneda",
    "dhernandez",
    "eruiz",
    "jmendieta",
    "lmendez",
    "movalle",
    "rvaldez",
)


def test_pagina_es_un_objeto_con_sus_cuatro_campos(
    cliente_admin: TestClient, cabecera_admin: dict[str, str]
) -> None:
    """The response is the paged object of the contract, never a bare array."""
    respuesta = cliente_admin.get("/api/users", headers=cabecera_admin)

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert set(cuerpo) == {"items", "total", "limit", "offset"}
    assert cuerpo["total"] == len(ORDEN_ESPERADO)
    assert cuerpo["limit"] == 50
    assert cuerpo["offset"] == 0


def test_el_orden_por_username_llega_intacto_al_cable(
    cliente_admin: TestClient, cabecera_admin: dict[str, str]
) -> None:
    """The order the repository promises survives the service and the router."""
    respuesta = cliente_admin.get("/api/users", headers=cabecera_admin)

    nombres = [item["username"] for item in respuesta.json()["items"]]
    assert tuple(nombres) == ORDEN_ESPERADO


def test_cada_usuario_llega_con_los_ocho_campos_del_contrato(
    cliente_admin: TestClient, cabecera_admin: dict[str, str]
) -> None:
    """Every row carries the eight fields the interface reads, and no more.

    The interface of ola B was written against this list before the endpoint
    existed; a field renamed here without warning leaves the table blank.
    """
    respuesta = cliente_admin.get("/api/users", headers=cabecera_admin)

    primero = respuesta.json()["items"][0]
    assert set(primero) == {
        "id",
        "username",
        "email",
        "full_name",
        "role",
        "disabled",
        "created_at",
        "updated_at",
    }


def test_la_sesion_no_gana_la_marca_de_modificacion(
    cliente_admin: TestClient, cabecera_admin: dict[str, str]
) -> None:
    """``/api/auth/me`` keeps the seven fields of US-015, not eight.

    ``updated_at`` lives in ``UserAdminOut``, and that inheritance is the whole
    point of there being two response models: writing the field into ``UserOut``
    instead -the shorter move, now that the table and its mirror carry the
    column- changes the shape of the endpoint every session of the portal reads,
    on a US whose scope is the administration panel. The test above would keep
    passing with the field moved up to the parent, because it counts the eight
    fields of the administration contract and would still find them.
    """
    respuesta = cliente_admin.get("/api/auth/me", headers=cabecera_admin)

    assert respuesta.status_code == 200
    assert set(respuesta.json()) == {
        "id",
        "username",
        "email",
        "full_name",
        "role",
        "disabled",
        "created_at",
    }


def test_la_ultima_pagina_no_encoge_el_total(
    cliente_admin: TestClient, cabecera_admin: dict[str, str]
) -> None:
    """``total`` counts the table and the page counts the window."""
    respuesta = cliente_admin.get(
        "/api/users", params={"limit": 2, "offset": 6}, headers=cabecera_admin
    )

    cuerpo = respuesta.json()
    assert len(cuerpo["items"]) == 1
    assert cuerpo["items"][0]["username"] == ORDEN_ESPERADO[-1]
    assert cuerpo["total"] == len(ORDEN_ESPERADO)
    assert (cuerpo["limit"], cuerpo["offset"]) == (2, 6)


@pytest.mark.parametrize(
    ("parametros", "esperado"),
    [
        ({"limit": 0}, 422),
        ({"limit": 201}, 422),
        ({"offset": -1}, 422),
    ],
    ids=["limit-cero", "limit-fuera-de-tope", "offset-negativo"],
)
def test_la_ventana_se_valida_en_el_borde(
    cliente_admin: TestClient,
    cabecera_admin: dict[str, str],
    parametros: dict[str, int],
    esperado: int,
) -> None:
    """A window outside its bounds is refused instead of clamped in silence.

    Without the bounds a client can ask for the whole table in one request, and
    an ``offset`` below zero reaches PostgreSQL as an error the caller cannot
    read.
    """
    respuesta = cliente_admin.get(
        "/api/users", params=parametros, headers=cabecera_admin
    )

    assert respuesta.status_code == esperado


@pytest.mark.asyncio
async def test_la_consulta_ordena_y_pagina_en_la_base(
    sesion_espia: SesionEspia,
) -> None:
    """The SQL orders by username and cuts the window with LIMIT and OFFSET."""
    repositorio = SqlAdminUserRepository(sesion_espia)  # type: ignore[arg-type]

    await repositorio.list_page(limit=2, offset=6)

    pagina = sql_de(sesion_espia.sentencias[0], literales=True)
    assert "ORDER BY app_user.username" in pagina
    assert "LIMIT 2" in pagina
    assert "OFFSET 6" in pagina


@pytest.mark.asyncio
async def test_el_total_se_cuenta_en_su_propia_consulta(
    sesion_espia: SesionEspia,
) -> None:
    """The total comes from a COUNT over the table, not from the page length."""
    repositorio = SqlAdminUserRepository(sesion_espia)  # type: ignore[arg-type]

    await repositorio.list_page(limit=2, offset=6)

    total = sql_de(sesion_espia.sentencias[1])
    assert "count(*)" in total.lower()
    assert "FROM app_user" in total
    assert "LIMIT" not in total.upper()


@pytest.mark.asyncio
async def test_la_fila_proyectada_se_mapea_campo_a_campo() -> None:
    """The eight projected columns land on the eight fields, in that order.

    The mapping is positional, so a column inserted in the projection without
    moving the unpacking puts the role in the name and the address in the role.
    Nothing would raise: the row would simply be wrong on the screen, and every
    value is a string.
    """
    clave = uuid.UUID(int=7)
    creado = datetime(2026, 8, 11, 12, 0, tzinfo=UTC)
    modificado = datetime(2026, 8, 13, 9, 0, tzinfo=UTC)
    sesion = SesionEspia(
        (
            (
                clave,
                "movalle",
                "movalle@karisma.mx",
                "Mariana Ovalle",
                "admin",
                False,
                creado,
                modificado,
            ),
        )
    )
    repositorio = SqlAdminUserRepository(sesion)  # type: ignore[arg-type]

    fila = await repositorio.get_by_id(clave)

    assert fila is not None
    assert fila.id == clave
    assert fila.username == "movalle"
    assert fila.email == "movalle@karisma.mx"
    assert fila.full_name == "Mariana Ovalle"
    assert fila.role is Scope.ADMIN
    assert fila.disabled is False
    assert (fila.created_at, fila.updated_at) == (creado, modificado)


@pytest.mark.asyncio
async def test_una_escritura_que_encuentra_la_fila_se_confirma() -> None:
    """The update is committed, so it survives the end of the request.

    Without the commit the session closes and PostgreSQL rolls the transaction
    back: the endpoint answers 200 with the new role and the row keeps the old
    one. Nothing in the suite that doubles the repository would ever see it.
    """
    clave = uuid.UUID(int=7)
    sesion = SesionEspia(
        (
            (
                clave,
                "dhernandez",
                "dhernandez@karisma.mx",
                "Diego Hernandez",
                "operativo",
                False,
                datetime(2026, 8, 11, 12, 0, tzinfo=UTC),
                datetime(2026, 8, 13, 9, 0, tzinfo=UTC),
            ),
        )
    )
    repositorio = SqlAdminUserRepository(sesion)  # type: ignore[arg-type]

    fila = await repositorio.update_role(clave, Scope.OPERATIVO)

    assert fila is not None
    assert sesion.confirmaciones == 1


@pytest.mark.asyncio
async def test_una_escritura_sin_fila_no_confirma_nada(
    sesion_espia: SesionEspia,
) -> None:
    """An update that matched nothing does not open a transaction to commit."""
    repositorio = SqlAdminUserRepository(sesion_espia)  # type: ignore[arg-type]

    fila = await repositorio.set_disabled(uuid.UUID(int=7), disabled=True)

    assert fila is None
    assert sesion_espia.confirmaciones == 0


@pytest.mark.asyncio
async def test_la_dependencia_entrega_el_repositorio_de_administracion(
    sesion_espia: SesionEspia,
) -> None:
    """The seam hands over the administration repository, not the read one.

    They share a table and neither implements the protocol of the other, so the
    mix-up only shows up in production: every test of this package substitutes
    this dependency and would never notice.
    """
    repositorio = await get_admin_user_repository(sesion_espia)  # type: ignore[arg-type]

    assert isinstance(repositorio, SqlAdminUserRepository)
