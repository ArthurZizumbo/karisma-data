"""Contract of the catalog endpoints, with the session substituted.

The double below answers the four shapes of statement the service sends, so
these cases exercise routing, authorization, query validation and the mapping
from result row to response contract. They do **not** exercise the SQL: the
double never parses it. That is the job of ``test_catalog_integracion.py``, and
saying it here is the difference between a contract test and a test that buys
coverage without meaning any of it.

What a broken row mapping looks like from the outside is the reason this file
exists: the metadata panel of US-UX-07 is built against these field names, and
a renamed block is a screen that renders empty with a 200 behind it.
"""

from collections.abc import Callable, Mapping
from datetime import date
from typing import TYPE_CHECKING, Any, Final, cast

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.database import get_session
from app.core.scopes import Scope
from app.models.catalog import ENTRY_NOT_FOUND

if TYPE_CHECKING:
    from app.models.user import AppUser

FILA_BASE: Final[Mapping[str, Any]] = {
    "field_id": 1,
    "physical_name": "sdo_cap",
    "business_name": "saldo de capital",
    "definition": "Monto insoluto del principal del credito.",
    "domain": "cartera",
    "data_type": "decimal",
    "sensitivity": "restringida",
    "refresh_frequency": "diaria",
    "certification": "certificado",
    "unit": "MXN",
    "metric_agg": "sum",
    "steward": None,
    "valid_from": date(2021, 1, 1),
    "valid_to": None,
    "is_current": True,
    "source_code": "creditos",
    "source_display_name": "Cartera de credito",
    "source_system_of_record": "CORE-CRED",
    "source_has_extract": True,
    "owner_area": "Riesgo de Credito",
    "owner_name": "Ana Ruiz",
    "score": 0.4007,
}

FILAS_DE_NOTAS: Final[tuple[Mapping[str, Any], ...]] = (
    {
        "field_id": 1,
        "note": "El saldo se corta a las 23:00 hora local.",
        "applicability": "Aplica solo a posiciones de mercado local.",
        "author": "Ana Ruiz",
        "recorded_at": date(2025, 11, 4),
        "always_applies": False,
    },
    {
        "field_id": 1,
        "note": "Incluye los creditos reestructurados desde 2023.",
        "applicability": "Aplica siempre.",
        "author": "Luis Mora",
        "recorded_at": date(2025, 6, 10),
        "always_applies": True,
    },
)

FILAS_DE_FACETAS: Final[tuple[Mapping[str, Any], ...]] = (
    {"facet": "source", "value": "creditos", "total": 40},
    {"facet": "sensitivity", "value": "restringida", "total": 12},
    {"facet": "sensitivity", "value": "interna", "total": 28},
)


class ResultadoFalso:
    """Minimum surface of a SQLAlchemy result the service consumes."""

    def __init__(self, filas: list[Mapping[str, Any]]) -> None:
        """Store the rows this result will serve.

        Args:
            filas: Rows, already keyed by column label.
        """
        self._filas = filas

    def mappings(self) -> "ResultadoFalso":
        """Return itself: the double serves mappings and nothing else.

        Returns:
            This same object.
        """
        return self

    def all(self) -> list[Mapping[str, Any]]:
        """Return every row.

        Returns:
            The rows this result was built with.
        """
        return self._filas


class SesionFalsa:
    """Double of the session that answers by the shape of the statement.

    The dispatch reads the statement because the service sends four different
    ones per search and the double has to tell them apart. The markers it looks
    for are properties the statements cannot lose without changing what they
    mean: a search ranks, a count counts, the facets union and the notes read
    their own table.
    """

    def __init__(
        self,
        *,
        filas: list[Mapping[str, Any]] | None = None,
        total: int = 0,
        facetas: list[Mapping[str, Any]] | None = None,
        notas: list[Mapping[str, Any]] | None = None,
        ficha: list[Mapping[str, Any]] | None = None,
    ) -> None:
        """Prepare the answers of every statement.

        Args:
            filas: Rows of the ranked page.
            total: Number of matches before pagination.
            facetas: Rows of the facet count query.
            notas: Rows of the tribal note query.
            ficha: Rows of the detail query.
        """
        self.filas = filas or []
        self.total = total
        self.facetas = facetas or []
        self.notas = notas or []
        self.ficha = ficha or []
        self.llamadas: list[tuple[str, Mapping[str, Any]]] = []

    async def connection(self) -> "SesionFalsa":
        """Return itself: the service asks the session for its connection.

        Returns:
            This same object.
        """
        return self

    async def execute(
        self, statement: object, params: Mapping[str, Any] | None = None
    ) -> ResultadoFalso:
        """Record the call and answer the statement it recognises.

        Args:
            statement: Textual statement sent by the service.
            params: Bind parameters of that statement.

        Returns:
            The prepared rows of that shape of statement.
        """
        sql = str(statement)
        self.llamadas.append((sql, dict(params or {})))
        if "catalog_tribal_note" in sql:
            return ResultadoFalso(list(self.notas))
        if "UNION ALL" in sql:
            return ResultadoFalso(list(self.facetas))
        if "count(*) AS total" in sql:
            return ResultadoFalso([{"total": self.total}])
        if ":entry_id" in sql:
            return ResultadoFalso(list(self.ficha))
        return ResultadoFalso(list(self.filas))

    def parametros_de_la_busqueda(self) -> Mapping[str, Any]:
        """Return the parameters of the first statement that ranked.

        Returns:
            The bind parameters of the paged search.
        """
        for sql, params in self.llamadas:
            if "ts_rank" in sql:
                return params
        raise AssertionError("el servicio no envio ninguna consulta con ranking")


@pytest.fixture
def sesion_falsa() -> SesionFalsa:
    """Return a session double serving one hit with its two notes.

    Returns:
        The double, ready to be injected through ``dependency_overrides``.
    """
    return SesionFalsa(
        filas=[dict(FILA_BASE)],
        total=1,
        facetas=list(FILAS_DE_FACETAS),
        notas=list(FILAS_DE_NOTAS),
        ficha=[dict(FILA_BASE)],
    )


@pytest.fixture
def crear_cliente_catalogo(
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
def cliente_catalogo(
    crear_cliente_catalogo: Callable[[SesionFalsa], TestClient],
    sesion_falsa: SesionFalsa,
) -> TestClient:
    """Return a client whose session is the double of this module.

    Args:
        crear_cliente_catalogo: Factory of clients bound to a session double.
        sesion_falsa: Double serving one hit with its two notes.

    Returns:
        A started client.
    """
    return crear_cliente_catalogo(sesion_falsa)


@pytest.fixture
def token_de_rol(
    usuarios_semilla: dict[str, "AppUser"], token_de: Callable[..., str]
) -> Callable[[Scope], str]:
    """Return a factory of valid tokens per role, derived from the seed.

    The mapping is derived and not retyped so that a change to the seeded users
    moves these cases with it instead of leaving a stale literal.

    Args:
        usuarios_semilla: Rows served by the repository double.
        token_de: Factory of signed tokens from the parent conftest.

    Returns:
        A callable taking a role and returning its encoded token.
    """
    por_rol: dict[Scope, str] = {}
    for usuario in usuarios_semilla.values():
        por_rol.setdefault(Scope(usuario.role), usuario.username)

    def _token(rol: Scope) -> str:
        return token_de(por_rol[rol], rol.value)

    return _token


@pytest.fixture
def cabeceras(token_de_rol: Callable[[Scope], str]) -> dict[str, str]:
    """Return the authorization header of an operational user.

    Args:
        token_de_rol: Factory of valid tokens per role.

    Returns:
        The header a signed in caller sends.
    """
    return {"Authorization": f"Bearer {token_de_rol(Scope.OPERATIVO)}"}


@pytest.mark.parametrize("ruta", ["/api/catalog/search?q=saldo", "/api/catalog/1"])
def test_sin_token_responde_401_con_www_authenticate(
    cliente_catalogo: TestClient, ruta: str
) -> None:
    """Neither catalog route answers an anonymous request.

    Removing the ``Security(...)`` of either endpoint would publish the whole
    data dictionary of the institution, definitions and owners included.

    Args:
        cliente_catalogo: Client with the session double injected.
        ruta: Route under test.
    """
    respuesta = cliente_catalogo.get(ruta)

    assert respuesta.status_code == 401
    assert respuesta.headers["www-authenticate"].startswith('Bearer realm="karisma"')


@pytest.mark.parametrize("rol", list(Scope))
def test_cada_rol_autenticado_recibe_200(
    cliente_catalogo: TestClient, token_de_rol: Callable[[Scope], str], rol: Scope
) -> None:
    """The catalog is for every signed in role, which is the policy row.

    A ``scopes=["analista"]`` copied from another router would answer 403 to
    the operational profile, which is the persona the catalog was designed for.

    Args:
        cliente_catalogo: Client with the session double injected.
        token_de_rol: Factory of valid tokens per role.
        rol: Role carried by the token.
    """
    respuesta = cliente_catalogo.get(
        "/api/catalog/search?q=saldo",
        headers={"Authorization": f"Bearer {token_de_rol(rol)}"},
    )

    assert respuesta.status_code == 200


def test_hit_trae_los_cinco_bloques_del_panel(
    cliente_catalogo: TestClient, cabeceras: dict[str, str]
) -> None:
    """A hit carries source, owner, validity, facets and tribal notes.

    This is the shape US-UX-07 builds against. Renaming or dropping a block
    leaves the panel empty behind a 200, which is the failure nobody sees in a
    backend log.

    Args:
        cliente_catalogo: Client with the session double injected.
        cabeceras: Authorization header of a signed in caller.
    """
    cuerpo = cliente_catalogo.get(
        "/api/catalog/search?q=saldo", headers=cabeceras
    ).json()
    hit = cuerpo["results"][0]

    assert {"source", "owner", "validity", "facets", "tribal_notes"} <= set(hit)
    assert hit["source"]["code"] == "creditos"
    assert hit["source"]["has_extract"] is True
    # The steward of the row is null: the fallback to the owner of the source
    # is resolved by the backend so that no client has to coalesce it.
    assert hit["owner"] == {"area": "Riesgo de Credito", "steward": "Ana Ruiz"}
    assert hit["validity"] == {
        "valid_from": "2021-01-01",
        "valid_to": None,
        "is_current": True,
    }
    assert cuerpo["total"] == 1
    assert cuerpo["tsquery"] == "saldo:*"


def test_facetas_devuelven_codigos_y_no_etiquetas(
    cliente_catalogo: TestClient, cabeceras: dict[str, str]
) -> None:
    """Facets travel as stable codes, in the hit and in the counts.

    Answering "Restringida" instead of ``restringida`` would leave the English
    locale with nothing to key its copy on, and would force the client to
    compare prose.

    Args:
        cliente_catalogo: Client with the session double injected.
        cabeceras: Authorization header of a signed in caller.
    """
    cuerpo = cliente_catalogo.get(
        "/api/catalog/search?q=saldo", headers=cabeceras
    ).json()

    assert cuerpo["results"][0]["facets"] == {
        "domain": "cartera",
        "data_type": "decimal",
        "sensitivity": "restringida",
        "refresh_frequency": "diaria",
        "certification": "certificado",
        "unit": "MXN",
        "metric_agg": "sum",
    }
    assert cuerpo["facet_counts"]["sensitivity"] == {
        "restringida": 12,
        "interna": 28,
    }


def test_las_notas_declaran_como_se_adjuntaron(
    cliente_catalogo: TestClient, cabeceras: dict[str, str]
) -> None:
    """A conditional note is marked ``consulta`` and an unconditional one ``campo``.

    Collapsing both into one value turns the Tk-Boost pattern into a plain text
    field: the panel can no longer tell "this is known about the data" from
    "this is relevant to what you asked".

    Args:
        cliente_catalogo: Client with the session double injected.
        cabeceras: Authorization header of a signed in caller.
    """
    cuerpo = cliente_catalogo.get(
        "/api/catalog/search?q=saldo", headers=cabeceras
    ).json()
    notas = cuerpo["results"][0]["tribal_notes"]

    assert [nota["attached_by"] for nota in notas] == ["consulta", "campo"]


@pytest.mark.parametrize(
    "consulta",
    [
        "/api/catalog/search?q=a",
        "/api/catalog/search",
        "/api/catalog/search?q=saldo&limit=0",
        "/api/catalog/search?q=saldo&limit=51",
        "/api/catalog/search?q=saldo&offset=-1",
    ],
)
def test_parametros_invalidos_devuelven_422(
    cliente_catalogo: TestClient, cabeceras: dict[str, str], consulta: str
) -> None:
    """Out of range paging and a one character query are rejected at the door.

    Relaxing the ``Query`` constraints pushes the validation into the service,
    where a negative offset becomes a database error and a 500.

    Args:
        cliente_catalogo: Client with the session double injected.
        cabeceras: Authorization header of a signed in caller.
        consulta: Request under test.
    """
    assert cliente_catalogo.get(consulta, headers=cabeceras).status_code == 422


def test_consulta_sin_terminos_utiles_responde_200_sin_tocar_la_base(
    crear_cliente_catalogo: Callable[[SesionFalsa], TestClient],
    cabeceras: dict[str, str],
) -> None:
    """Punctuation is an empty result, not an error and not a query.

    Losing the short circuit sends ``to_tsquery('spanish', '')`` to the engine
    on every keystroke that carries no word yet.

    Args:
        crear_cliente_catalogo: Factory of clients bound to a session double.
        cabeceras: Authorization header of a signed in caller.
    """
    sesion = SesionFalsa()
    respuesta = crear_cliente_catalogo(sesion).get(
        "/api/catalog/search?q=...", headers=cabeceras
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["results"] == []
    assert respuesta.json()["total"] == 0
    assert respuesta.json()["tsquery"] == ""
    assert sesion.llamadas == []


def test_filtros_de_faceta_llegan_al_servicio_como_lista(
    cliente_catalogo: TestClient, sesion_falsa: SesionFalsa, cabeceras: dict[str, str]
) -> None:
    """A repeated filter arrives as several values, not as the last one.

    Declaring ``str`` instead of ``list[str]`` collapses
    ``source=creditos&source=liquidez`` into one code, and the screen silently
    filters by half of what the user selected.

    Args:
        cliente_catalogo: Client with the session double injected.
        sesion_falsa: Double that recorded the bind parameters.
        cabeceras: Authorization header of a signed in caller.
    """
    cliente_catalogo.get(
        "/api/catalog/search?q=saldo&source=creditos&source=liquidez"
        "&domain=cartera&sensitivity=interna&certification=certificado",
        headers=cabeceras,
    )
    params = sesion_falsa.parametros_de_la_busqueda()

    assert params["sources"] == ["creditos", "liquidez"]
    assert params["domains"] == ["cartera"]
    assert params["sensitivities"] == ["interna"]
    assert params["certifications"] == ["certificado"]


def test_la_ficha_devuelve_la_entrada_sin_score(
    cliente_catalogo: TestClient, cabeceras: dict[str, str]
) -> None:
    """The detail carries every block of a hit and no score.

    There is no ranking outside a search, so publishing a score there would be
    a number the panel could paint without anything behind it.

    Args:
        cliente_catalogo: Client with the session double injected.
        cabeceras: Authorization header of a signed in caller.
    """
    respuesta = cliente_catalogo.get("/api/catalog/1", headers=cabeceras)
    cuerpo = respuesta.json()

    assert respuesta.status_code == 200
    assert "score" not in cuerpo
    assert cuerpo["field_id"] == 1
    assert {"source", "owner", "validity", "facets", "tribal_notes"} <= set(cuerpo)


def test_ficha_inexistente_devuelve_404_con_codigo(
    crear_cliente_catalogo: Callable[[SesionFalsa], TestClient],
    cabeceras: dict[str, str],
) -> None:
    """An unknown identifier answers 404 with a code, never with a sentence.

    The interface is bilingual: a Spanish sentence in the body would exist in
    one language only, and the English locale would print it as it came.

    Args:
        crear_cliente_catalogo: Factory of clients bound to a session double.
        cabeceras: Authorization header of a signed in caller.
    """
    respuesta = crear_cliente_catalogo(SesionFalsa()).get(
        "/api/catalog/999999", headers=cabeceras
    )

    assert respuesta.status_code == 404
    assert respuesta.json() == {"detail": ENTRY_NOT_FOUND}
