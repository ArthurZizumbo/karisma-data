"""Shared fixtures for the backend test suite.

The suite is invoked from the repository root while the application lives in
``backend/``. The path bootstrap below keeps ``pytest tests/backend`` working
even when pytest is started without ``-c backend/pyproject.toml``, which is the
only way it would pick up the ``pythonpath`` setting of that file. Everything
that imports ``app`` is therefore imported inside the fixtures, after the
bootstrap has run.
"""

import sys
from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

BACKEND_ROOT = Path(__file__).resolve().parents[2] / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

MINIMAL_ENV: dict[str, str] = {
    "DATABASE_URL": "postgresql://karisma:karisma@localhost:5432/karisma_test",
    # 43 characters: the settings now enforce a 32 character minimum, so a
    # short placeholder would fail validation instead of the case under test.
    "JWT_SECRET_KEY": "test-signing-key-with-enough-entropy-000000",
    "GEMINI_API_KEY": "test-gemini-key",
    "APP_ENV": "test",
    "LOG_LEVEL": "WARNING",
}


@pytest.fixture(autouse=True)
def minimal_env(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Iterator[None]:
    """Provide the minimum viable environment and isolate the settings cache.

    The working directory is moved to an empty temporary folder so that no
    ``.env.local`` of the developer machine leaks into the assertions, and the
    ``lru_cache`` of ``get_settings`` is cleared on both sides of the test.

    Args:
        monkeypatch: Fixture used to patch the environment and the cwd.
        tmp_path: Empty directory used as the working directory of the test.

    Yields:
        None. The fixture only manipulates process-wide state.
    """
    from app.core.config import get_settings

    monkeypatch.chdir(tmp_path)
    for name, value in MINIMAL_ENV.items():
        monkeypatch.setenv(name, value)
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


@pytest.fixture
def client(minimal_env: None) -> Iterator[TestClient]:
    """Return a test client bound to a freshly built application.

    Args:
        minimal_env: Declared explicitly to guarantee that the environment is
            in place before the application factory reads the settings.

    Yields:
        A client that runs the startup and shutdown handlers of the app.
    """
    from app.main import create_app

    with TestClient(create_app()) as test_client:
        yield test_client
