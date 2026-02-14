from unittest.mock import patch

from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.api import deps
from app.db.models import User
from app.main import app


def test_get_updater_config(test_client: TestClient):
    """
    Tests the public endpoint for license updater configuration.
    """
    response = test_client.get("/app_config/config/updater")
    assert response.status_code == 200
    data = response.json()
    assert "github_token" in data
    assert "repo_owner" in data
    assert "repo_name" in data


def test_get_mutable_config_as_admin(test_client: TestClient, admin_token_headers: dict):
    """
    Tests that an admin can successfully retrieve the mutable settings.
    """
    app.dependency_overrides[deps.get_current_active_admin] = lambda: User(
        id=1, username="admin", is_admin=True
    )

    response = test_client.get("/app_config/config", headers=admin_token_headers)
    assert response.status_code == 200
    data = response.json()
    assert "SMTP_HOST" in data
    assert "ALERT_THRESHOLD_DAYS" in data


def test_get_mutable_config_as_non_admin(test_client: TestClient, user_token_headers: dict):
    """
    Tests that a regular user is forbidden from retrieving settings.
    """

    # Simulate non-admin via override that raises 403
    def forbidden_admin():
        raise HTTPException(status_code=403, detail="Forbidden")

    app.dependency_overrides[deps.get_current_active_admin] = forbidden_admin

    response = test_client.get("/app_config/config", headers=user_token_headers)
    assert response.status_code == 403


def test_update_mutable_config_as_admin(test_client: TestClient, admin_token_headers: dict):
    """
    Tests that an admin can successfully update the mutable settings.
    """
    app.dependency_overrides[deps.get_current_active_admin] = lambda: User(
        id=1, username="admin", is_admin=True
    )

    new_settings = {
        "SMTP_HOST": "smtp.newhost.com",
        "GEMINI_API_KEY_ANALYSIS": "new_key_123",
        "ALERT_THRESHOLD_DAYS": 99,
    }

    with patch("app.core.config.settings.save_mutable_settings") as mock_save:
        response = test_client.put(
            "/app_config/config", json=new_settings, headers=admin_token_headers
        )

        assert response.status_code == 204
        mock_save.assert_called_once()


def test_update_mutable_config_as_non_admin(test_client: TestClient, user_token_headers: dict):
    """
    Tests that a regular user is forbidden from updating settings.
    """

    def forbidden_admin():
        raise HTTPException(status_code=403, detail="Forbidden")

    app.dependency_overrides[deps.get_current_active_admin] = forbidden_admin

    new_settings = {"SMTP_HOST": "hacker.com"}
    response = test_client.put("/app_config/config", json=new_settings, headers=user_token_headers)
    assert response.status_code == 403


def test_update_mutable_config_with_invalid_data(
    test_client: TestClient, admin_token_headers: dict
):
    """
    Tests that the endpoint rejects invalid data (e.g., wrong type).
    """
    app.dependency_overrides[deps.get_current_active_admin] = lambda: User(
        id=1, username="admin", is_admin=True
    )

    invalid_settings = {"SMTP_PORT": "not-an-integer"}
    response = test_client.put(
        "/app_config/config", json=invalid_settings, headers=admin_token_headers
    )
    assert response.status_code == 400


def test_update_mutable_config_with_empty_body(test_client: TestClient, admin_token_headers: dict):
    """
    Tests that the endpoint rejects an empty request body.
    """
    app.dependency_overrides[deps.get_current_active_admin] = lambda: User(
        id=1, username="admin", is_admin=True
    )

    response = test_client.put("/app_config/config", json={}, headers=admin_token_headers)
    assert response.status_code == 400
