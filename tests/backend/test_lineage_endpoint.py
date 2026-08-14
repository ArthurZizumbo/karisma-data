"""Contract of the lineage endpoint, with the session substituted.

The double below answers by the table each statement reads, so these cases
exercise routing, authorization, the composition of the derived hop and the
mapping onto the response contract. They do **not** exercise the SQL: the
double never parses it, and the ordering of the journey is SQL. That is the job
of ``test_lineage_integracion.py``, and saying it here is the difference
between a contract test and a test that buys coverage without meaning any of
it.

What a broken contract looks like from the outside is the reason this file
exists: the overlay of US-029 renders five hops keyed on these field names, and
a renamed block is a panel that opens empty with a 200 behind it.
"""

from collections.abc import Callable, Iterator
from datetime import date
from typing import TYPE_CHECKING, Any, Final, cast

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.database import get_session
from app.core.scopes import Scope
from app.models.catalog import CatalogField, CatalogSource
from app.models.lineage import (
    FIELD_PUBLISH_CODE,
    LINEAGE_STEP_COUNT,
    CatalogLineageStep,
    LineageErrorCode,
)

if TYPE_CHECKING:
    from app.models.user import AppUser

RUTA: Final[str] = "/api/catalog/7/lineage"

ETAPAS_ESPERADAS: Final[tuple[str, ...]] = (
    "origen",
    "extraccion",
    "transformacion",
    "calidad",
    "presentacion",
)

FUENTE: Final[CatalogSource] = CatalogSource(
    id=3,
    code="creditos",
    display_name="Cartera de credito",
    description="Contratos de credito vigentes y vencidos.",
    owner_area="Direccion de Credito",
    owner_name="Ricardo Salas",
    system_of_record="SIC-Core",
    has_extract=True,
)


def _campo(*, steward: str | None = None, valid_to: date | None = None) -> CatalogField:
    """Build the catalog entry the journey ends at.

    Args:
        steward: Person that curates the definition, or ``None`` when the field
            declares none of its own.
        valid_to: Last day the definition was in force.

    Returns:
        A fresh row, safe for a case to mutate.
    """
    return CatalogField(
        id=7,
        source_id=3,
        physical_name="sdo_cap",
        business_name="saldo de capital",
        definition="Monto insoluto del principal del credito.",
        aliases="saldo insoluto",
        domain="cartera",
        data_type="decimal",
        sensitivity="restringida",
        refresh_frequency="diaria",
        certification="certificado",
        unit="MXN",
        metric_agg="sum",
        steward=steward,
        valid_from=date(2021, 1, 1),
        valid_to=valid_to,
    )


# The four stored hops of the source. The owner changes from hop to hop on
# purpose: the criterion asks for the owner OF EACH HOP, and rows that all
# named the owner of the source would let a panel pass while showing one owner
# five times. The quality hop is already closed, which is the only way to see
# that ``is_current`` is computed and not hardcoded.
PASOS: Final[tuple[CatalogLineageStep, ...]] = (
    CatalogLineageStep(
        id=41,
        source_id=3,
        step_order=1,
        stage="origen",
        system_code="SIC-Core",
        system_name="Core bancario SIC",
        transformation_code="origin_capture",
        transformation_detail="SIC-Core.CRE_CONTRATO",
        owner_area="Tecnologia de Core",
        owner_name="Alberto Nunez",
        effective_from=date(2018, 1, 1),
    ),
    CatalogLineageStep(
        id=42,
        source_id=3,
        step_order=2,
        stage="extraccion",
        system_code="KRS-Ingesta",
        system_name="Ingesta Karisma",
        transformation_code="batch_extract",
        transformation_detail="job_creditos_nocturno",
        owner_area="Plataforma de Datos",
        owner_name="Emilio Cazares",
        effective_from=date(2022, 3, 1),
    ),
    CatalogLineageStep(
        id=43,
        source_id=3,
        step_order=3,
        stage="transformacion",
        system_code="KRS-Semantica",
        system_name="Capa semantica Karisma",
        transformation_code="business_rule",
        transformation_detail="regla_saldo_insoluto_v3",
        owner_area="Riesgo de Credito",
        owner_name="Sofia Aranda",
        effective_from=date(2023, 7, 1),
    ),
    CatalogLineageStep(
        id=44,
        source_id=3,
        step_order=4,
        stage="calidad",
        system_code="KRS-Calidad",
        system_name="Control de calidad Karisma",
        transformation_code="quality_rule",
        transformation_detail="ctrl_cuadre_saldo_vs_mayor",
        owner_area="Calidad de Datos",
        owner_name="Teresa Villalba",
        effective_from=date(2024, 2, 1),
        effective_to=date(2025, 12, 31),
    ),
)


class ResultadoFalso:
    """Minimum surface of a SQLModel result the service consumes.

    The rows are typed as ``object`` because one statement selects a pair of
    models and the other selects one model: the double is injected at run time
    through ``dependency_overrides`` and nothing type checks it against the
    service, so a looser annotation buys nothing here.
    """

    def __init__(self, filas: list[object]) -> None:
        """Store the rows this result will serve.

        Args:
            filas: Rows, as model instances or tuples of them.
        """
        self._filas = filas

    def first(self) -> object | None:
        """Return the first row, or ``None`` when there is none.

        Returns:
            The row the service reads as the catalog entry.
        """
        return self._filas[0] if self._filas else None

    def all(self) -> list[object]:
        """Return every row.

        Returns:
            The rows this result was built with.
        """
        return list(self._filas)


class SesionFalsa:
    """Double of the session that answers by the table each statement reads.

    The dispatch reads the compiled statement because the service sends two of
    them and the double has to tell them apart. The marker is a property
    neither statement can lose without changing what it means: the journey
    reads its own table and the entry does not.
    """

    def __init__(
        self,
        *,
        entrada: tuple[CatalogField, CatalogSource] | None,
        pasos: tuple[CatalogLineageStep, ...] = PASOS,
    ) -> None:
        """Prepare the answers of both statements.

        Args:
            entrada: Catalog entry with its source, or ``None`` to play the
                identifier nobody carries.
            pasos: Stored hops of that source.
        """
        self.entrada = entrada
        self.pasos = pasos
        self.sentencias: list[str] = []

    async def exec(self, statement: object) -> ResultadoFalso:
        """Record the statement and answer the table it reads.

        Args:
            statement: Select sent by the service.

        Returns:
            The prepared rows for that statement.
        """
        sql = str(statement)
        self.sentencias.append(sql)
        if "catalog_lineage_step" in sql:
            return ResultadoFalso(list(self.pasos))
        return ResultadoFalso([self.entrada] if self.entrada is not None else [])


@pytest.fixture
def sesion_falsa() -> SesionFalsa:
    """Return a session double serving one entry and its four stored hops.

    Returns:
        The double, ready to be injected through ``dependency_overrides``.
    """
    return SesionFalsa(entrada=(_campo(), FUENTE))


@pytest.fixture
def crear_cliente_linaje(
    crear_cliente: Callable[..., TestClient],
) -> Callable[[SesionFalsa], TestClient]:
    """Return a factory of clients bound to a given session double.

    Args:
        crear_cliente: Factory of clients bound to the repository double.

    Returns:
        A callable taking the session double and returning a started client.
    """

    def _crear(sesion: SesionFalsa) -> TestClient:
        cliente = crear_cliente(demo=False)
        # TestClient.app is typed as the generic ASGI callable; the override
        # registry only exists on the FastAPI instance underneath it.
        aplicacion = cast(FastAPI, cliente.app)
        aplicacion.dependency_overrides[get_session] = lambda: sesion
        return cliente

    return _crear


@pytest.fixture
def cliente_linaje(
    crear_cliente_linaje: Callable[[SesionFalsa], TestClient],
    sesion_falsa: SesionFalsa,
) -> TestClient:
    """Return a client whose session is the double of this module.

    Args:
        crear_cliente_linaje: Factory of clients bound to a session double.
        sesion_falsa: Double serving one entry with its four hops.

    Returns:
        A started client.
    """
    return crear_cliente_linaje(sesion_falsa)


@pytest.fixture
def usuario_por_rol(usuarios_semilla: dict[str, "AppUser"]) -> dict[Scope, str]:
    """Map each role to the login identifier of one seeded user carrying it.

    Args:
        usuarios_semilla: Rows served by the repository double.

    Returns:
        One login identifier per role.
    """
    por_rol: dict[Scope, str] = {}
    for usuario in usuarios_semilla.values():
        por_rol.setdefault(Scope(usuario.role), usuario.username)
    return por_rol


@pytest.fixture
def cabecera_de_rol(
    usuario_por_rol: dict[Scope, str], token_de: Callable[..., str]
) -> Callable[[Scope], dict[str, str]]:
    """Return a factory of authorization headers per role.

    Args:
        usuario_por_rol: Login identifier of a seeded user per role.
        token_de: Factory of signed tokens from the shared conftest.

    Returns:
        A callable taking a role and returning the header a caller sends.
    """

    def _cabecera(rol: Scope) -> dict[str, str]:
        return {"Authorization": f"Bearer {token_de(usuario_por_rol[rol], rol.value)}"}

    return _cabecera


@pytest.fixture
def cabeceras(cabecera_de_rol: Callable[[Scope], dict[str, str]]) -> dict[str, str]:
    """Return the authorization header of an operational user.

    Args:
        cabecera_de_rol: Factory of headers per role.

    Returns:
        The header the least privileged profile sends.
    """
    return cabecera_de_rol(Scope.OPERATIVO)


@pytest.fixture
def cuerpo(cliente_linaje: TestClient, cabeceras: dict[str, str]) -> dict[str, Any]:
    """Return the payload of a successful request.

    Args:
        cliente_linaje: Client with the session double injected.
        cabeceras: Authorization header of an operational user.

    Returns:
        The decoded body.
    """
    respuesta = cliente_linaje.get(RUTA, headers=cabeceras)
    assert respuesta.status_code == 200
    return cast(dict[str, Any], respuesta.json())


def test_sin_token_responde_401_con_www_authenticate(
    cliente_linaje: TestClient,
) -> None:
    """The lineage of a field is not public.

    Removing the ``Security(...)`` would publish the owners, the systems of
    record and the internal job names of the institution to anyone.

    Args:
        cliente_linaje: Client with the session double injected.
    """
    respuesta = cliente_linaje.get(RUTA)

    assert respuesta.status_code == 401
    assert respuesta.headers["www-authenticate"].startswith('Bearer realm="karisma"')


@pytest.mark.parametrize("rol", list(Scope))
def test_cualquier_sesion_valida_obtiene_el_recorrido(
    cliente_linaje: TestClient,
    cabecera_de_rol: Callable[[Scope], dict[str, str]],
    rol: Scope,
) -> None:
    """Every role gets the same journey, the operational one included.

    A ``scopes=[Scope.ANALISTA]`` added "just in case" would leave the
    operational profile without the lineage, and that profile is precisely the
    one that needs to see where a figure comes from before trusting it.

    Args:
        cliente_linaje: Client with the session double injected.
        cabecera_de_rol: Factory of headers per role.
        rol: Role carried by the token.
    """
    respuesta = cliente_linaje.get(RUTA, headers=cabecera_de_rol(rol))

    assert respuesta.status_code == 200
    assert len(respuesta.json()["steps"]) == LINEAGE_STEP_COUNT


def test_el_recorrido_llega_hasta_la_cifra_visible(cuerpo: dict[str, Any]) -> None:
    """Five hops, numbered from one, ending at the column behind the figure.

    Without the composition of the terminal step the journey would stop at the
    quality control and the criterion -"from the system of record to the figure
    on screen"- would be answered by four hops that never mention the field.

    Args:
        cuerpo: Payload of a successful request.
    """
    pasos = cuerpo["steps"]

    assert [paso["stage"] for paso in pasos] == list(ETAPAS_ESPERADAS)
    assert [paso["order"] for paso in pasos] == [1, 2, 3, 4, 5]
    assert pasos[-1]["transformation_code"] == FIELD_PUBLISH_CODE
    assert pasos[-1]["transformation_detail"] == "sdo_cap"
    assert pasos[0]["system_code"] == FUENTE.system_of_record


def test_el_paso_derivado_se_declara_como_tal(cuerpo: dict[str, Any]) -> None:
    """Four hops are stored and one is composed, and the body says which.

    Emitting ``stored`` as true in the five would present as kept a hop that is
    recomputed on every request, which is the honesty the contract promises and
    not an implementation detail.

    Args:
        cuerpo: Payload of a successful request.
    """
    assert [paso["stored"] for paso in cuerpo["steps"]] == [
        True,
        True,
        True,
        True,
        False,
    ]


def test_cada_paso_responde_por_su_propietario_y_su_vigencia(
    cuerpo: dict[str, Any],
) -> None:
    """Every hop carries its own owner and its own period, not the field's.

    The owner of the extraction is not the owner of the source and the validity
    of a conversion rule is not the validity of the definition. A panel fed
    with the owner of the entry five times would render and say nothing.

    Args:
        cuerpo: Payload of a successful request.
    """
    pasos = cuerpo["steps"]

    assert all(paso["owner"]["area"] and paso["owner"]["steward"] for paso in pasos)
    assert all(paso["effective_from"] for paso in pasos)
    assert len({paso["owner"]["steward"] for paso in pasos}) > 1
    assert pasos[1]["owner"]["steward"] == "Emilio Cazares"


def test_la_vigencia_cerrada_de_un_paso_se_declara_no_vigente(
    cuerpo: dict[str, Any],
) -> None:
    """``is_current`` is computed from the dates and never hardcoded.

    The quality hop of the double closed on 31-dec-2025. Emitting true there
    would tell the reader that a control which is no longer running still
    guards the figure.

    Args:
        cuerpo: Payload of a successful request.
    """
    pasos = cuerpo["steps"]

    assert [paso["is_current"] for paso in pasos[:3]] == [True, True, True]
    assert pasos[3]["effective_to"] == "2025-12-31"
    assert pasos[3]["is_current"] is False


@pytest.mark.parametrize(
    ("steward", "esperado"),
    [(None, "Ricardo Salas"), ("Sofia Aranda", "Sofia Aranda")],
    ids=["sin custodio propio", "con custodio propio"],
)
def test_el_propietario_se_resuelve_en_el_servidor(
    crear_cliente_linaje: Callable[[SesionFalsa], TestClient],
    cabeceras: dict[str, str],
    steward: str | None,
    esperado: str,
) -> None:
    """A field with no steward answers to whoever owns the source.

    Leaving the fallback to the client is how two screens end up disagreeing:
    US-008 resolved it on the server for the metadata panel and the overlay
    honours the same rule instead of writing a second coalesce.

    Args:
        crear_cliente_linaje: Factory of clients bound to a session double.
        cabeceras: Authorization header of an operational user.
        steward: Person the field declares, or ``None``.
        esperado: Person the answer must name.
    """
    cliente = crear_cliente_linaje(
        SesionFalsa(entrada=(_campo(steward=steward), FUENTE))
    )

    cuerpo = cliente.get(RUTA, headers=cabeceras).json()

    assert cuerpo["owner"] == {"area": FUENTE.owner_area, "steward": esperado}
    assert cuerpo["steps"][-1]["owner"]["steward"] == esperado


def test_la_ficha_viaja_con_el_vocabulario_del_catalogo(
    cuerpo: dict[str, Any],
) -> None:
    """The header of the panel reuses the contract of US-008, code by code.

    A second spelling of ``SourceRef`` or of ``Facets`` is the divergence the
    previous audit punished: the overlay and the metadata panel would drift
    apart on the first facet either one added.

    Args:
        cuerpo: Payload of a successful request.
    """
    assert cuerpo["field_id"] == 7
    assert cuerpo["physical_name"] == "sdo_cap"
    assert cuerpo["source"] == {
        "code": "creditos",
        "display_name": "Cartera de credito",
        "system_of_record": "SIC-Core",
        "has_extract": True,
    }
    assert cuerpo["validity"] == {
        "valid_from": "2021-01-01",
        "valid_to": None,
        "is_current": True,
    }
    assert cuerpo["facets"]["domain"] == "cartera"
    assert cuerpo["facets"]["unit"] == "MXN"
    assert cuerpo["facets"]["metric_agg"] == "sum"


def test_campo_inexistente_devuelve_404_tipado(
    crear_cliente_linaje: Callable[[SesionFalsa], TestClient],
    cabeceras: dict[str, str],
) -> None:
    """An unknown identifier is a designed error and never a stack trace.

    Without the typed failure the service would walk into an attribute of
    ``None`` and answer 500, and the screen -which keys its copy on the code-
    would have nothing to paint but a blank panel.

    Args:
        crear_cliente_linaje: Factory of clients bound to a session double.
        cabeceras: Authorization header of an operational user.
    """
    cliente = crear_cliente_linaje(SesionFalsa(entrada=None))

    respuesta = cliente.get("/api/catalog/999999/lineage", headers=cabeceras)

    assert respuesta.status_code == 404
    assert respuesta.json()["detail"] == {
        "codigo": LineageErrorCode.CAMPO_NO_ENCONTRADO.value,
        "entry_id": 999999,
    }


def test_el_recorrido_no_se_pide_sin_pasar_por_la_seguridad(
    cliente_linaje: TestClient, sesion_falsa: SesionFalsa
) -> None:
    """The anonymous request is answered before any statement is sent.

    Declaring the session dependency ahead of the security one would open a
    connection for every unauthenticated probe, which is a cheap way to make an
    unauthenticated caller consume the pool.

    Args:
        cliente_linaje: Client with the session double injected.
        sesion_falsa: Double that records every statement it receives.
    """
    cliente_linaje.get(RUTA)

    assert sesion_falsa.sentencias == []


@pytest.fixture
def cliente_sin_pasos(
    crear_cliente_linaje: Callable[[SesionFalsa], TestClient],
) -> Iterator[TestClient]:
    """Return a client whose source has no stored hops at all.

    Args:
        crear_cliente_linaje: Factory of clients bound to a session double.

    Yields:
        The client, so the case reads as the situation it describes.
    """
    yield crear_cliente_linaje(SesionFalsa(entrada=(_campo(), FUENTE), pasos=()))


def test_una_fuente_sin_pasos_sembrados_sigue_llegando_a_la_cifra(
    cliente_sin_pasos: TestClient, cabeceras: dict[str, str]
) -> None:
    """With no seeded hops the answer is the derived one, numbered first.

    The numbering is computed from what was read and not from a literal five,
    so a source the seed forgot degrades to a one hop journey instead of
    answering a body with holes in it. The integration suite is what makes sure
    no seeded source is in that situation.

    Args:
        cliente_sin_pasos: Client whose source has no stored hops.
        cabeceras: Authorization header of an operational user.
    """
    cuerpo = cliente_sin_pasos.get(RUTA, headers=cabeceras).json()

    assert [paso["order"] for paso in cuerpo["steps"]] == [1]
    assert cuerpo["steps"][0]["stage"] == "presentacion"
    assert cuerpo["steps"][0]["stored"] is False
