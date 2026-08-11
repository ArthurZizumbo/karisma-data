"""Tests for the unauthenticated health probe (CA-8)."""

from fastapi.testclient import TestClient


def test_health_ok(client: TestClient) -> None:
    """The probe answers 200 with the exact contracted payload.

    Args:
        client: Test client bound to the application.
    """
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "servicio": "karisma-api"}


def test_health_sin_token(client: TestClient) -> None:
    """The probe answers without credentials.

    Docker Compose and Cloud Run call it anonymously, so it must never be
    guarded by ``Security`` nor challenge the caller.

    Args:
        client: Test client bound to the application.
    """
    anonymous = client.get("/health")
    with_garbage_token = client.get(
        "/health", headers={"Authorization": "Bearer not-a-token"}
    )

    assert anonymous.status_code == 200
    assert "www-authenticate" not in anonymous.headers
    assert with_garbage_token.status_code == 200
    assert with_garbage_token.json() == anonymous.json()
