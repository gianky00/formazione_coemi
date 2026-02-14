import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.api import deps
from app.core import security
from app.db.models import User
from app.main import app


@pytest.fixture
def enable_real_auth():
    # Save original overrides
    original_overrides = app.dependency_overrides.copy()
    # Remove get_current_user override to enable real auth
    app.dependency_overrides.pop(deps.get_current_user, None)
    yield
    # Restore
    app.dependency_overrides = original_overrides


def test_change_own_password(test_client: TestClient, db_session: Session, enable_real_auth):
    # 1. Setup User
    username = "pwchangeuser"
    old_password = "oldpassword"
    new_password = "newpassword"
    hashed = security.get_password_hash(old_password)
    user = User(username=username, hashed_password=hashed, is_admin=False)
    db_session.add(user)
    db_session.commit()

    # 2. Login
    login_data = {"username": username, "password": old_password}
    response = test_client.post("/auth/login", data=login_data)
    assert response.status_code == 200
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 3. Change Password (Success)
    payload = {
        "old_password": old_password,
        "new_password": new_password,
        "confirm_password": new_password,
    }
    response = test_client.post("/auth/change-password", json=payload, headers=headers)

    assert response.status_code == 200
    assert "Password cambiata con successo" in response.json()["message"]

    # 4. Verify DB updated
    db_session.refresh(user)
    assert security.verify_password(new_password, user.hashed_password)

    # 5. Verify Old Password no longer works (status 401 now)
    response = test_client.post("/auth/login", data=login_data)
    assert response.status_code == 401

    # 6. Verify New Password works
    login_data_new = {"username": username, "password": new_password}
    response = test_client.post("/auth/login", data=login_data_new)
    assert response.status_code == 200


def test_change_password_wrong_old(test_client: TestClient, db_session: Session, enable_real_auth):
    # 1. Setup User
    username = "pwfailuser"
    password = "password"
    hashed = security.get_password_hash(password)
    user = User(username=username, hashed_password=hashed, is_admin=False)
    db_session.add(user)
    db_session.commit()

    # 2. Login
    login_data = {"username": username, "password": password}
    token = test_client.post("/auth/login", data=login_data).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 3. Change Password (Fail)
    payload = {
        "old_password": "wrongpassword",
        "new_password": "newpassword",
        "confirm_password": "newpassword",
    }
    response = test_client.post("/auth/change-password", json=payload, headers=headers)

    assert response.status_code == 400
    assert "Vecchia password errata" in response.json()["detail"]
