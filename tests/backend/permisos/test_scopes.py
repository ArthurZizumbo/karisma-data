"""Tests of the role vocabulary: hierarchy, coverage and the two challenges.

Nothing here builds an application or signs a token. The subject is the decision
itself -does this role reach that level- and the two RFC 6750 challenges the API
is allowed to return, which is the part US-017 keys its copy on.
"""

import itertools
from collections.abc import Collection

import pytest
from fastapi import HTTPException

from app.core import scopes as modulo_scopes
from app.core.scopes import (
    REALM,
    ROLE_HIERARCHY,
    ErrorCode,
    Scope,
    covers,
    enforce_scopes,
    forbidden,
    oauth2_scope_descriptions,
    parse_scope_claim,
    unauthorized,
)

# The order the whole matrix depends on. Written out instead of derived from
# ROLE_HIERARCHY so that a reordering of the mapping has something to fail
# against: comparing the mapping with itself would always pass.
ORDEN_ESPERADO = ("operativo", "analista", "directivo", "admin")

# Spelling of the fourth role in frontend/app/types/navegacion.ts, assigned to
# US-017. It is the name a token or an endpoint would realistically carry by
# mistake, which is why the unknown scopes below are that one and not an
# invented string.
FUERA_DEL_VOCABULARIO = "administrador"

# Event name and keyword arguments of one record.
Registro = tuple[str, dict[str, object]]


class _LoggerEspia:
    """Logger double that keeps what it was asked to record.

    ``structlog.testing.capture_logs`` is not usable here: the suite configures
    structlog with ``cache_logger_on_first_use`` and a ``WARNING`` threshold as
    soon as any test builds the application, so whether an ``info`` record is
    captured would depend on the order of the suite. Substituting the module
    logger asks the only question that matters -what does the denial record
    carry- and asks it the same way every run.
    """

    def __init__(self) -> None:
        """Start with an empty list of records."""
        self.registros: list[Registro] = []

    def info(self, event: str, **datos: object) -> None:
        """Record an informational event.

        Args:
            event: Name of the event.
            datos: Keyword arguments of the record.
        """
        self.registros.append((event, datos))

    def warning(self, event: str, **datos: object) -> None:
        """Record a warning event.

        Args:
            event: Name of the event.
            datos: Keyword arguments of the record.
        """
        self.registros.append((event, datos))


@pytest.fixture
def registros(monkeypatch: pytest.MonkeyPatch) -> list[Registro]:
    """Substitute the logger of ``app.core.scopes`` and return its records.

    Args:
        monkeypatch: Fixture used to substitute the module logger.

    Returns:
        The list the double appends to, empty at the start of the test.
    """
    espia = _LoggerEspia()
    monkeypatch.setattr(modulo_scopes, "logger", espia)
    return espia.registros


def test_la_jerarquia_tiene_los_cuatro_roles_en_orden() -> None:
    """The hierarchy is a total order over exactly the four roles of the portal."""
    assert tuple(scope.value for scope in ROLE_HIERARCHY) == ORDEN_ESPERADO
    rangos = list(ROLE_HIERARCHY.values())
    assert rangos == sorted(rangos)
    assert len(set(rangos)) == len(rangos)


@pytest.mark.parametrize(
    ("concedido", "exigido"), list(itertools.product(list(Scope), list(Scope)))
)
def test_rol_superior_cubre_al_inferior(concedido: Scope, exigido: Scope) -> None:
    """Coverage follows the rank of the roles, in that direction and no other.

    Args:
        concedido: Role carried by the token.
        exigido: Role the endpoint demands.
    """
    esperado = ROLE_HIERARCHY[concedido] >= ROLE_HIERARCHY[exigido]

    assert covers({concedido}, [exigido.value]) is esperado


@pytest.mark.parametrize("concedido", list(Scope))
def test_scopes_vacios_solo_exigen_autenticacion(concedido: Scope) -> None:
    """An endpoint with no scopes admits every authenticated caller.

    Args:
        concedido: Role carried by the token.
    """
    assert covers({concedido}, []) is True


def test_scope_desconocido_en_el_token_no_concede_nada() -> None:
    """A role the portal does not know is a permission that grants nothing.

    The alternative is a ``KeyError`` inside a dependency, which is a 500: a
    failure some proxies retry and that leaves no authorization trace.
    """
    concedidos = parse_scope_claim(FUERA_DEL_VOCABULARIO)

    assert concedidos == frozenset()
    assert covers(concedidos, [Scope.OPERATIVO.value]) is False
    assert covers(concedidos, []) is True


def test_scope_desconocido_en_el_endpoint_niega_el_acceso() -> None:
    """A misdeclared endpoint denies instead of opening or crashing."""
    assert covers({Scope.ADMIN}, ["analysta"]) is False
    assert covers({Scope.ADMIN}, [Scope.ANALISTA.value, "analysta"]) is False


def test_el_scope_del_token_distingue_mayusculas() -> None:
    """The claim is compared literally: no case folding, no fuzzy matching.

    Folding the case would make ``ADMIN`` in a hand written token, or a row that
    escaped the ``CHECK`` of the table, grant administration.
    """
    assert parse_scope_claim("ADMIN") == frozenset()
    assert parse_scope_claim("Admin") == frozenset()
    assert parse_scope_claim("admin") == frozenset({Scope.ADMIN})


def test_el_espacio_del_scope_es_separador_y_no_significa_nada_mas() -> None:
    """Whitespace delimits names, so padding is not a second vocabulary.

    RFC 6749 defines ``scope`` as a space delimited list, and splitting on
    whitespace is what implements that. It is not normalization of the name:
    ``admin`` surrounded by blanks is the same name, while ``ADMIN`` is not.
    """
    assert parse_scope_claim("  operativo   analista \t") == frozenset(
        {Scope.OPERATIVO, Scope.ANALISTA}
    )
    assert parse_scope_claim("") == frozenset()
    assert parse_scope_claim("   ") == frozenset()


@pytest.mark.parametrize("codigo", list(ErrorCode))
def test_reto_401_incluye_realm_y_scope(codigo: ErrorCode) -> None:
    """Every 401 carries the challenge, with the level when the endpoint has one.

    Args:
        codigo: Failure code the challenge is built for.
    """
    sin_nivel = unauthorized(codigo)
    con_nivel = unauthorized(codigo, [Scope.ANALISTA.value])

    for excepcion in (sin_nivel, con_nivel):
        assert excepcion.status_code == 401
        assert excepcion.detail == codigo.value
        assert excepcion.headers is not None
        reto = excepcion.headers["WWW-Authenticate"]
        assert reto.startswith(f'Bearer realm="{REALM}"')

    assert 'scope="analista"' in con_nivel.headers["WWW-Authenticate"]  # type: ignore[index]
    assert "scope=" not in sin_nivel.headers["WWW-Authenticate"]  # type: ignore[index]


def test_el_reto_401_solo_publica_las_razones_seguras() -> None:
    """The challenge names the reason only when disclosing it costs nothing.

    An absent credential is not an invalid token, and neither an expired session
    nor a revoked one tells the caller whether the account exists.
    """
    ausente = unauthorized(ErrorCode.CREDENCIALES_AUSENTES).headers
    invalida = unauthorized(ErrorCode.CREDENCIALES_INVALIDAS).headers
    expirada = unauthorized(ErrorCode.SESION_EXPIRADA).headers
    revocada = unauthorized(ErrorCode.SESION_REVOCADA).headers
    assert ausente is not None
    assert invalida is not None
    assert expirada is not None
    assert revocada is not None

    assert "error=" not in ausente["WWW-Authenticate"]
    assert 'error="invalid_token"' in invalida["WWW-Authenticate"]
    assert "error_description" not in invalida["WWW-Authenticate"]
    assert 'error_description="sesion_expirada"' in expirada["WWW-Authenticate"]
    assert 'error_description="sesion_revocada"' in revocada["WWW-Authenticate"]


def test_reto_403_declara_insufficient_scope() -> None:
    """The 403 says the token is fine and the level is not, as RFC 6750 asks.

    A 403 carrying ``invalid_token`` would send a conforming client back to the
    login screen, where nothing it can do changes the answer.
    """
    excepcion = forbidden([Scope.ADMIN.value])

    assert excepcion.status_code == 403
    assert excepcion.detail == ErrorCode.PERMISOS_INSUFICIENTES.value
    assert excepcion.headers is not None
    reto = excepcion.headers["WWW-Authenticate"]
    assert 'error="insufficient_scope"' in reto
    assert 'scope="admin"' in reto
    assert "invalid_token" not in reto


def test_los_cinco_codigos_de_error_son_estables() -> None:
    """The codes are the contract US-017 keys its two locales on.

    Renaming one of them silently leaves a screen without copy in both
    languages, which is why the literals are written out here.
    """
    assert [codigo.value for codigo in ErrorCode] == [
        "credenciales_ausentes",
        "credenciales_invalidas",
        "sesion_expirada",
        "sesion_revocada",
        "permisos_insuficientes",
    ]


def test_enforce_scopes_deja_pasar_a_quien_alcanza() -> None:
    """The enforcement is silent when the caller reaches the level."""
    enforce_scopes({Scope.ADMIN}, [Scope.DIRECTIVO.value])
    enforce_scopes({Scope.OPERATIVO}, [])


def test_enforce_scopes_lanza_el_403_cuando_no_alcanza() -> None:
    """The enforcement raises the challenge instead of returning a boolean."""
    with pytest.raises(HTTPException) as error:
        enforce_scopes({Scope.OPERATIVO}, [Scope.ANALISTA.value])

    assert error.value.status_code == 403
    assert error.value.detail == ErrorCode.PERMISOS_INSUFICIENTES.value


def test_enforce_scopes_no_registra_el_token(
    registros: list[Registro],
) -> None:
    """The denial record carries the levels and nothing that identifies a session.

    The username arrives through ``structlog.contextvars``, bound by
    ``app.core.auth``; a token or a password reaching this record would put a
    live credential in the log of every denied request.

    Args:
        registros: Records captured from the module logger.
    """
    with pytest.raises(HTTPException):
        enforce_scopes({Scope.OPERATIVO}, [Scope.ADMIN.value])

    assert len(registros) == 1
    evento, datos = registros[0]
    assert evento == "autorizacion_denegada"
    assert set(datos) == {"scopes_exigidos", "scopes_del_token"}
    assert datos["scopes_exigidos"] == ["admin"]
    assert datos["scopes_del_token"] == ["operativo"]


def test_un_scope_desconocido_deja_rastro_de_advertencia(
    registros: list[Registro],
) -> None:
    """A misdeclared endpoint is denied and recorded, not swallowed.

    Without the record the endpoint denies everybody and nobody knows why, which
    reads as a hierarchy bug for as long as it takes to find the typo.

    Args:
        registros: Records captured from the module logger.
    """
    permitido = covers({Scope.ADMIN}, [FUERA_DEL_VOCABULARIO])

    assert permitido is False
    assert [evento for evento, _ in registros] == ["scope_desconocido"]
    assert registros[0][1]["scopes_exigidos"] == [FUERA_DEL_VOCABULARIO]


def test_el_catalogo_de_scopes_del_esquema_oauth2_cubre_los_cuatro_roles() -> None:
    """The Authorize button of the interactive docs lists every role.

    The catalogue is handed to ``OAuth2PasswordBearer``, and FastAPI keeps a
    reference to it: a role missing here cannot be probed by hand.
    """
    descripciones = oauth2_scope_descriptions()

    assert sorted(descripciones) == sorted(scope.value for scope in Scope)
    assert all(texto.strip() for texto in descripciones.values())

    descripciones["operativo"] = "modificado"
    assert oauth2_scope_descriptions()["operativo"] != "modificado"


@pytest.mark.parametrize(
    ("concedidos", "exigidos", "esperado"),
    [
        (frozenset(), [], True),
        (frozenset(), [Scope.OPERATIVO.value], False),
        ({Scope.ANALISTA}, [Scope.OPERATIVO.value, Scope.DIRECTIVO.value], False),
        ({Scope.DIRECTIVO}, [Scope.OPERATIVO.value, Scope.DIRECTIVO.value], True),
    ],
)
def test_covers_falla_cerrado_en_los_bordes(
    concedidos: Collection[Scope], exigidos: list[str], esperado: bool
) -> None:
    """The edges of the decision: no roles, and several demanded at once.

    Several demanded scopes are satisfied by the highest of them, which is the
    reading a total order forces. Getting this backwards would let an
    ``analista`` into an endpoint that also names ``directivo``.

    Args:
        concedidos: Roles carried by the token.
        exigidos: Scope names the endpoint declared.
        esperado: Whether access is allowed.
    """
    assert covers(concedidos, exigidos) is esperado
