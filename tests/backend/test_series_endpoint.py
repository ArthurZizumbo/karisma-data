"""The HTTP contract of ``GET /api/metrics/series``.

Nothing here reads the real aggregate and nothing opens PostgreSQL: the user
lookup enters through the repository double of the shared conftest and the data
directory points at a synthetic aggregate written per test. What is measured is
the contract the browser and the smoke script depend on -status codes, stable
error codes, content type, validator- and the permission rule, which is the
first non empty scope the portal serves.
"""

from collections.abc import Callable, Iterator
from pathlib import Path
from typing import TYPE_CHECKING, Any, Final, cast

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from test_series_service import escribir_agregado, fila

from app.core.scopes import ErrorCode, Scope
from app.models.series import MAX_JSON_POINTS, SeriesErrorCode
from app.services import series_service
from app.utils.serie_frame import FRAME_MAGIC, FRAME_MEDIA_TYPE

if TYPE_CHECKING:
    from app.models.user import AppUser

RUTA: Final[str] = "/api/metrics/series"

# Roles that reach the endpoint through the total order of US-016. 'operativo'
# is the one that must not, and it is the reason this row exists at all.
ROLES_QUE_ALCANZAN: Final[frozenset[Scope]] = frozenset(
    {Scope.ANALISTA, Scope.DIRECTIVO, Scope.ADMIN}
)


@pytest.fixture(autouse=True)
def sin_cache() -> Iterator[None]:
    """Empty the in-process cache around every test.

    Yields:
        None. The fixture only clears process-wide state.
    """
    series_service.clear_cache()
    yield
    series_service.clear_cache()


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
        A callable taking a role and returning the header mapping.
    """

    def _cabecera(rol: Scope) -> dict[str, str]:
        return {"Authorization": f"Bearer {token_de(usuario_por_rol[rol], rol.value)}"}

    return _cabecera


@pytest.fixture
def raiz_de_datos(tmp_path: Path) -> Path:
    """Write a small synthetic aggregate and return its root.

    Args:
        tmp_path: Directory of the test.

    Returns:
        The root that plays the role of ``data/``.
    """
    return escribir_agregado(
        tmp_path / "datos",
        [
            fila(
                serie_id=serie,
                dia=dia,
                unidad="TESORERIA" if serie == 0 else "MERCADOS",
                divisa="MXN" if serie == 0 else "USD",
            )
            for serie in (0, 1)
            for dia in range(4)
        ],
    )


@pytest.fixture
def cliente_con_datos(
    crear_cliente: Callable[..., TestClient],
    monkeypatch: pytest.MonkeyPatch,
    raiz_de_datos: Path,
) -> TestClient:
    """Return a client whose application reads the synthetic aggregate.

    The variable is exported before the factory runs because the settings are
    resolved while the application is being built.

    Args:
        crear_cliente: Factory of clients bound to the repository double.
        monkeypatch: Used to export the data directory.
        raiz_de_datos: Root holding the synthetic aggregate.

    Returns:
        A started client.
    """
    monkeypatch.setenv("DATA_DIR", str(raiz_de_datos))
    return crear_cliente(demo=False)


@pytest.fixture
def cliente_sin_datos(
    crear_cliente: Callable[..., TestClient],
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> TestClient:
    """Return a client pointed at a data directory nobody seeded.

    Args:
        crear_cliente: Factory of clients bound to the repository double.
        monkeypatch: Used to export the data directory.
        tmp_path: Directory of the test, deliberately left empty.

    Returns:
        A started client.
    """
    monkeypatch.setenv("DATA_DIR", str(tmp_path / "vacio"))
    return crear_cliente(demo=False)


@pytest.mark.parametrize("rol", list(Scope))
def test_matriz_de_permisos(
    cliente_con_datos: TestClient,
    cabecera_de_rol: Callable[[Scope], dict[str, str]],
    rol: Scope,
) -> None:
    """Only ``analista`` and above read the series, and ``operativo`` gets 403.

    Publishing this endpoint with the wrong scope would let a profile that does
    not even have the dashboard in its sidebar read its data by typing the URL:
    the interface and the API would be saying different things about the same
    permission.

    Args:
        cliente_con_datos: Client of an application with data.
        cabecera_de_rol: Factory of authorization headers.
        rol: Role carried by the token.
    """
    respuesta = cliente_con_datos.get(RUTA, headers=cabecera_de_rol(rol))

    if rol in ROLES_QUE_ALCANZAN:
        assert respuesta.status_code == 200
    else:
        assert respuesta.status_code == 403
        assert respuesta.json()["detail"] == ErrorCode.PERMISOS_INSUFICIENTES.value


def test_sin_token_devuelve_401_con_www_authenticate(
    cliente_con_datos: TestClient,
) -> None:
    """An anonymous request is challenged, and the challenge names the level.

    A data endpoint without ``Security`` would answer 200 here. The startup
    guard of US-016 would also catch it; this case additionally fixes the header
    a conforming client reads to know what to ask for.

    Args:
        cliente_con_datos: Client of an application with data.
    """
    respuesta = cliente_con_datos.get(RUTA)

    assert respuesta.status_code == 401
    assert respuesta.json()["detail"] == ErrorCode.CREDENCIALES_AUSENTES.value
    reto = respuesta.headers["www-authenticate"]
    assert reto.startswith('Bearer realm="karisma"')
    assert 'scope="analista"' in reto


def test_binario_declara_tipo_y_longitud(
    cliente_con_datos: TestClient,
    cabecera_de_rol: Callable[[Scope], dict[str, str]],
) -> None:
    """The frame travels with its own media type and its own cardinality.

    Served as ``application/json`` the fetch layer of the browser would try to
    parse two megabytes of floats and fail with an error that explains nothing.

    Args:
        cliente_con_datos: Client of an application with data.
        cabecera_de_rol: Factory of authorization headers.
    """
    respuesta = cliente_con_datos.get(RUTA, headers=cabecera_de_rol(Scope.ANALISTA))

    assert respuesta.status_code == 200
    assert respuesta.headers["content-type"] == FRAME_MEDIA_TYPE
    assert respuesta.content[:4] == FRAME_MAGIC
    assert int(respuesta.headers["content-length"]) == len(respuesta.content)
    assert respuesta.headers["x-karisma-puntos"] == "8"
    assert respuesta.headers["cache-control"] == "private, max-age=300"


def test_etag_se_repite_y_el_if_none_match_da_304(
    cliente_con_datos: TestClient,
    cabecera_de_rol: Callable[[Scope], dict[str, str]],
) -> None:
    """The same query gets the same validator, and a conditional request 304s.

    A validator computed over the body would cost more than the aggregation it
    is meant to save, and one that never changes would keep serving the previous
    series after ``make data``. This case pins the first half; the next one pins
    the second.

    Args:
        cliente_con_datos: Client of an application with data.
        cabecera_de_rol: Factory of authorization headers.
    """
    cabeceras = cabecera_de_rol(Scope.ANALISTA)
    primera = cliente_con_datos.get(RUTA, headers=cabeceras)
    segunda = cliente_con_datos.get(RUTA, headers=cabeceras)
    validador = primera.headers["etag"]

    condicional = cliente_con_datos.get(
        RUTA, headers={**cabeceras, "If-None-Match": validador}
    )

    assert validador.startswith('W/"')
    assert segunda.headers["etag"] == validador
    assert condicional.status_code == 304
    assert condicional.content == b""
    assert condicional.headers["etag"] == validador


def test_el_etag_distingue_consultas_distintas(
    cliente_con_datos: TestClient,
    cabecera_de_rol: Callable[[Scope], dict[str, str]],
) -> None:
    """Two different questions never share a validator.

    Sharing one would serve the browser the cached answer of another query, and
    the chart would show the wrong metric with no error anywhere.

    Args:
        cliente_con_datos: Client of an application with data.
        cabecera_de_rol: Factory of authorization headers.
    """
    cabeceras = cabecera_de_rol(Scope.ANALISTA)
    saldo = cliente_con_datos.get(RUTA, headers=cabeceras)
    divisas = cliente_con_datos.get(
        RUTA, params={"agrupacion": "divisa"}, headers=cabeceras
    )

    assert saldo.headers["etag"] != divisas.headers["etag"]


def test_etag_cambia_cuando_cambia_el_parquet(
    cliente_con_datos: TestClient,
    cabecera_de_rol: Callable[[Scope], dict[str, str]],
    raiz_de_datos: Path,
) -> None:
    """Regenerating the data invalidates the validator in the same second.

    Without this ``make data`` would leave every browser showing the previous
    series until the cache expired on its own, and nothing would say so.

    Args:
        cliente_con_datos: Client of an application with data.
        cabecera_de_rol: Factory of authorization headers.
        raiz_de_datos: Root holding the synthetic aggregate.
    """
    cabeceras = cabecera_de_rol(Scope.ANALISTA)
    antes = cliente_con_datos.get(RUTA, headers=cabeceras)

    escribir_agregado(
        raiz_de_datos,
        [fila(serie_id=0, dia=dia, saldo=float(dia)) for dia in range(9)],
    )
    series_service.clear_cache()
    despues = cliente_con_datos.get(RUTA, headers=cabeceras)

    assert antes.status_code == despues.status_code == 200
    assert antes.headers["etag"] != despues.headers["etag"]


def test_datos_no_sembrados_devuelve_503_con_codigo(
    cliente_sin_datos: TestClient,
    cabecera_de_rol: Callable[[Scope], dict[str, str]],
) -> None:
    """A clone without ``make data`` gets the code the empty state waits for.

    If the backend answered anything else -a 500, a 404, an empty 200- the
    designed empty state of the screen would never appear, and the first thing
    an evaluator opening the public address sees would be a crash.

    Args:
        cliente_sin_datos: Client pointed at an empty data directory.
        cabecera_de_rol: Factory of authorization headers.
    """
    respuesta = cliente_sin_datos.get(RUTA, headers=cabecera_de_rol(Scope.ANALISTA))

    assert respuesta.status_code == 503
    detalle = respuesta.json()["detail"]
    assert detalle["codigo"] == SeriesErrorCode.DATOS_NO_SEMBRADOS.value
    assert detalle["archivo"] == "serie_tablero.parquet"


def test_json_por_encima_del_tope_devuelve_413_tipificado(
    crear_cliente: Callable[..., TestClient],
    monkeypatch: pytest.MonkeyPatch,
    cabecera_de_rol: Callable[[Scope], dict[str, str]],
    tmp_path: Path,
) -> None:
    """The readable variant refuses to become a fourteen megabyte body.

    Raising the ceiling "just to try it" would let the browser download a JSON
    of half a million numbers, which is the exact cost this User Story exists to
    avoid. The stable code is what lets the client tell this refusal from the
    413 of a proxy.

    Args:
        crear_cliente: Factory of clients bound to the repository double.
        monkeypatch: Used to export the data directory.
        cabecera_de_rol: Factory of authorization headers.
        tmp_path: Directory of the test.
    """
    raiz = escribir_agregado(
        tmp_path / "datos",
        [
            fila(serie_id=serie, dia=dia, bucket=str(serie))
            for serie in range(51)
            for dia in range(1000)
        ],
    )
    monkeypatch.setenv("DATA_DIR", str(raiz))
    cliente = crear_cliente(demo=False)

    respuesta = cliente.get(
        RUTA,
        params={"formato": "json", "agrupacion": "serie", "max_puntos": 1000},
        headers=cabecera_de_rol(Scope.ANALISTA),
    )

    assert respuesta.status_code == 413
    detalle = respuesta.json()["detail"]
    assert detalle["codigo"] == SeriesErrorCode.PAYLOAD_EXCESIVO.value
    assert detalle["puntos"] == 51_000
    assert detalle["maximo"] == MAX_JSON_POINTS


def test_la_variante_json_publica_el_bloque_de_origen(
    cliente_con_datos: TestClient,
    cabecera_de_rol: Callable[[Scope], dict[str, str]],
) -> None:
    """The readable variant carries the provenance, not only the numbers.

    US-029 renders that block verbatim and the anti-hallucination rule of the
    project rests on it: a figure on screen without a source is a figure nobody
    can defend.

    Args:
        cliente_con_datos: Client of an application with data.
        cabecera_de_rol: Factory of authorization headers.
    """
    respuesta = cliente_con_datos.get(
        RUTA, params={"formato": "json"}, headers=cabecera_de_rol(Scope.ANALISTA)
    )
    cuerpo: dict[str, Any] = respuesta.json()

    assert respuesta.status_code == 200
    assert respuesta.headers["content-type"].startswith("application/json")
    assert cuerpo["origen"]["archivo"].endswith("serie_tablero.parquet")
    assert cuerpo["origen"]["transformaciones"]
    assert cuerpo["conteo"] == {"puntos": 8, "fechas": 4, "series": 2}
    assert len(cuerpo["valores"]) == 2


@pytest.mark.parametrize(
    "consulta",
    [
        {"metrica": "saldo_total"},
        {"agrupacion": "cliente"},
        {"max_puntos": 5},
        {"serie_id": 3},
        {"desde": "2020-02-01", "hasta": "2020-01-01"},
        {"columna": "hashed_password"},
    ],
    ids=[
        "metrica-inexistente",
        "agrupacion-inexistente",
        "max-puntos-fuera-de-rango",
        "serie-id-sin-agrupacion-serie",
        "ventana-invertida",
        "parametro-ajeno",
    ],
)
def test_una_consulta_fuera_del_vocabulario_devuelve_422(
    cliente_con_datos: TestClient,
    cabecera_de_rol: Callable[[Scope], dict[str, str]],
    consulta: dict[str, Any],
) -> None:
    """The closed vocabulary is the semantic layer, and it is enforced here.

    The client never sends an expression: it sends a validated query that the
    deterministic compiler turns into Polars. A metric name that fell through
    would reach the engine as a column name, and a parameter accepted and
    ignored would draw an unfiltered chart the reader believes is filtered.

    Args:
        cliente_con_datos: Client of an application with data.
        cabecera_de_rol: Factory of authorization headers.
        consulta: Query parameters under test.
    """
    respuesta = cliente_con_datos.get(
        RUTA, params=consulta, headers=cabecera_de_rol(Scope.ANALISTA)
    )

    assert respuesta.status_code == 422


def test_openapi_declara_el_scope_analista(cliente_con_datos: TestClient) -> None:
    """What the code enforces and what the document publishes are the same.

    A divergence between the ``Security`` of the endpoint and the row of the
    registry is the ``scope_divergente`` class the guard of US-016 tipifies, and
    it is what would make ``docs/security.md`` describe a permission nobody
    applies.

    Args:
        cliente_con_datos: Client of an application with data.
    """
    # The schema is read from the application and not from /openapi.json:
    # outside APP_ENV=local the document is deliberately not served, and what
    # is being audited is what the application declares, not what it publishes.
    aplicacion = cast(FastAPI, cliente_con_datos.app)
    esquema = aplicacion.openapi()

    requisitos = esquema["paths"][RUTA]["get"]["security"]
    declarados = [next(iter(requisito.values())) for requisito in requisitos]
    assert declarados == [["analista"]]
