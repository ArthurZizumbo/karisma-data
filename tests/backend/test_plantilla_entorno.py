"""Contract tests for ``backend/.env.example``, the environment template.

``tests/backend/test_config.py`` proves that the application refuses to start
without ``DATABASE_URL``, ``JWT_SECRET_KEY`` and ``GEMINI_API_KEY``. That test
reads the process environment; nothing there guarantees that the template a
developer copies still declares those three keys, nor that it stays free of
real values. This module closes that gap by asserting the template as a
versioned text file.

The same ``DATABASE_URL`` feeds dbmate through ``make db-up``, and the
PostgreSQL of the compose serves no TLS: without the ``?sslmode=disable``
suffix dbmate aborts. The template must document it, so the assertion below
treats that piece of prose as part of the contract.

Nothing here connects to PostgreSQL, Cloud SQL, GCS or Gemini: the file on
disk is the whole subject under test.
"""

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
ENV_TEMPLATE = REPO_ROOT / "backend" / ".env.example"

REQUIRED_KEYS = ("DATABASE_URL", "JWT_SECRET_KEY", "GEMINI_API_KEY")
SECRET_KEYS = (*REQUIRED_KEYS, "POSTGRES_USER", "POSTGRES_PASSWORD")
DEFAULTED_KEYS = {"APP_ENV": "local", "LOG_LEVEL": "INFO"}
SSLMODE_SUFFIX = "?sslmode=disable"

ASSIGNMENT_PATTERN = re.compile(r"^([A-Z][A-Z0-9_]*)=(.*)$")


def read_template() -> str:
    """Return the content of the environment template.

    Returns:
        The file decoded as UTF-8.
    """
    return ENV_TEMPLATE.read_text(encoding="utf-8")


def assignments() -> list[tuple[str, str]]:
    """Return every ``KEY=value`` pair declared by the template.

    Commented lines are skipped, so the documented example connection string
    is never mistaken for a declaration.

    Returns:
        The list of ``(key, value)`` pairs in the order they appear, with the
        value stripped of surrounding whitespace.
    """
    pairs: list[tuple[str, str]] = []
    for line in read_template().splitlines():
        match = ASSIGNMENT_PATTERN.match(line.strip())
        if match is not None:
            pairs.append((match.group(1), match.group(2).strip()))
    return pairs


def declared_keys() -> list[str]:
    """Return the keys declared by the template, duplicates included.

    Returns:
        The list of declared key names in file order.
    """
    return [key for key, _ in assignments()]


def value_of(key: str) -> str:
    """Return the value assigned to a key by the template.

    Args:
        key: Name of the environment variable.

    Returns:
        The assigned value, empty when the key is declared without one.

    Raises:
        KeyError: If the key is not declared at all.
    """
    for name, value in assignments():
        if name == key:
            return value
    raise KeyError(key)


def test_plantilla_de_entorno_existe() -> None:
    """The template is present and carries declarations."""
    assert ENV_TEMPLATE.is_file(), "Falta backend/.env.example"
    assert assignments(), "backend/.env.example no declara ninguna variable"


@pytest.mark.parametrize("key", REQUIRED_KEYS)
def test_plantilla_declara_las_tres_obligatorias(key: str) -> None:
    """Each variable required by the strict settings is declared.

    Args:
        key: Name of the required environment variable.
    """
    assert key in declared_keys(), (
        f"backend/.env.example no declara {key}, obligatoria para arrancar"
    )


@pytest.mark.parametrize("key", REQUIRED_KEYS)
def test_obligatorias_declaradas_sin_valor(key: str) -> None:
    """The required variables are declared empty, never pre-filled.

    A template that ships a working value invites committing it, and the real
    values live in ``.env.local`` and in Secret Manager.

    Args:
        key: Name of the required environment variable.
    """
    assert value_of(key) == "", (
        f"{key} trae un valor en backend/.env.example: la plantilla se copia, "
        "no se rellena"
    )


@pytest.mark.parametrize("key", SECRET_KEYS)
def test_ninguna_credencial_lleva_valor(key: str) -> None:
    """No credential-bearing key ships a value in the template.

    Args:
        key: Name of the credential-bearing environment variable.
    """
    assert value_of(key) == "", f"{key} no puede llevar valor en la plantilla"


def test_ninguna_clave_se_declara_dos_veces() -> None:
    """Every key appears once: a second declaration silently wins."""
    keys = declared_keys()
    duplicated = sorted({key for key in keys if keys.count(key) > 1})

    assert not duplicated, (
        f"backend/.env.example declara claves repetidas: {duplicated}"
    )


def test_ningun_valor_de_la_plantilla_parece_una_conexion_real() -> None:
    """No declared value contains a URL scheme.

    Catches a connection string, an endpoint or a signed URL pasted into the
    template by mistake, whatever the key is called.
    """
    leaking = sorted({key for key, value in assignments() if "://" in value})

    assert not leaking, f"backend/.env.example expone cadenas de conexion en: {leaking}"


def test_plantilla_documenta_el_sufijo_sslmode_para_dbmate() -> None:
    """The template explains the suffix that dbmate needs against the compose.

    The rule is invisible in the empty declaration, so it has to live in the
    prose next to it: the documented example carries the suffix and the text
    names dbmate as the reason.
    """
    template = read_template()
    documented = [
        line
        for line in template.splitlines()
        if line.lstrip().startswith("#") and SSLMODE_SUFFIX in line
    ]

    assert documented, (
        f"La plantilla no documenta el sufijo {SSLMODE_SUFFIX} que dbmate "
        "exige contra el PostgreSQL del compose"
    )
    assert any("postgresql://" in line for line in documented), (
        f"El ejemplo documentado debe mostrar la URL completa con {SSLMODE_SUFFIX}"
    )
    assert "dbmate" in template.lower(), (
        "La plantilla no explica que la misma DATABASE_URL la consume dbmate"
    )


@pytest.mark.parametrize(("key", "expected"), sorted(DEFAULTED_KEYS.items()))
def test_opcionales_documentan_su_valor_por_defecto(key: str, expected: str) -> None:
    """The optional keys show the same defaults the settings apply.

    Args:
        key: Name of the optional environment variable.
        expected: Default value declared by the application settings.
    """
    assert value_of(key) == expected, (
        f"{key} deberia documentar el valor por defecto {expected}"
    )


# ---------------------------------------------------------------------------
# The secret scan exempts the .env.example files by path (.gitleaks.toml), so a
# real value pasted into a template would be seen by nobody. backend/ already
# had a net above; frontend/ had none. These two cases provide it.
# ---------------------------------------------------------------------------

FRONTEND_TEMPLATE = REPO_ROOT / "frontend" / ".env.example"


def frontend_assignments() -> list[tuple[str, str]]:
    """Return the ``KEY=value`` pairs declared by the frontend template.

    Returns:
        One tuple per assignment, in file order.
    """
    pairs: list[tuple[str, str]] = []
    for raw in FRONTEND_TEMPLATE.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        pairs.append((key.strip(), value.strip()))
    return pairs


def test_plantilla_del_frontend_existe_y_declara_variables() -> None:
    """The frontend template must exist and declare at least one variable."""
    assert FRONTEND_TEMPLATE.is_file(), "Falta frontend/.env.example"
    assert frontend_assignments(), "frontend/.env.example no declara ninguna variable"


def test_plantilla_del_frontend_no_lleva_credenciales() -> None:
    """No value of the frontend template may carry credentials.

    ``NUXT_API_BASE`` is a URL by design, so a bare scheme is not a finding
    here. What must never appear is user:password inside that URL, nor a value
    under a key that names a secret.
    """
    sospechosas = ("SECRET", "TOKEN", "PASSWORD", "KEY", "CREDENTIAL")
    hallazgos: list[str] = []

    for key, value in frontend_assignments():
        if any(palabra in key.upper() for palabra in sospechosas) and value:
            hallazgos.append(key)
        if "://" in value and "@" in value.split("://", 1)[1]:
            hallazgos.append(key)

    assert not hallazgos, (
        f"frontend/.env.example expone credenciales en: {sorted(set(hallazgos))}"
    )
