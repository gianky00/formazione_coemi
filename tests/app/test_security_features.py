import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.core import security
from app.db.models import User, BlacklistedToken, AuditLog
from app.core.config import settings
from app.main import app
from app.api import deps

@pytest.fixture
def enable_real_auth():
    # Save original overrides
    original_overrides = app.dependency_overrides.copy()
    # Remove get_current_user override to enable real auth
    app.dependency_overrides.pop(deps.get_current_user, None)
    yield
    # Restore
    app.dependency_overrides = original_overrides

def test_logout_invalidates_token(test_client: TestClient, db_session: Session, enable_real_auth):
    # 1. Login to get token
    username = "testadmin"
    password = "testpassword"
    hashed = security.get_password_hash(password)
    user = User(username=username, hashed_password=hashed, is_admin=True)
    db_session.add(user)
    db_session.commit()

    login_data = {"username": username, "password": password}
    response = test_client.post("/auth/login", data=login_data)
    assert response.status_code == 200
    token = response.json()["access_token"]

    # 2. Verify token works
    headers = {"Authorization": f"Bearer {token}"}
    response_me = test_client.get("/auth/me", headers=headers)
    assert response_me.status_code == 200

    # 3. Logout
    response_logout = test_client.post("/auth/logout", headers=headers)
    assert response_logout.status_code == 200

    # Verify token is in blacklist DB
    assert db_session.query(BlacklistedToken).filter_by(token=token).first() is not None

    # 4. Verify token is rejected
    response_rejected = test_client.get("/auth/me", headers=headers)
    assert response_rejected.status_code == 401
    assert "invalidated" in response_rejected.json()["detail"]

def test_audit_logging_on_user_create(test_client: TestClient, db_session: Session, enable_real_auth):
    # 1. Setup Admin
    username = "auditadmin"
    password = "auditpassword"
    hashed = security.get_password_hash(password)
    user = User(username=username, hashed_password=hashed, is_admin=True)
    db_session.add(user)
    db_session.commit()

    login_data = {"username": username, "password": password}
    response_login = test_client.post("/auth/login", data=login_data)
    assert response_login.status_code == 200
    token = response_login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Create a new user
    new_user_data = {
        "username": "newuser",
        "password": "newpassword", # This will be ignored now
        "account_name": "New User",
        "is_admin": False
    }
    response = test_client.post("/users/", json=new_user_data, headers=headers)
    assert response.status_code == 200

    # 3. Check Audit Log
    log_entry = db_session.query(AuditLog).filter_by(action="USER_CREATE").first()
    assert log_entry is not None
    assert log_entry.username == "auditadmin" # Who performed the action
    assert "newuser" in log_entry.details
