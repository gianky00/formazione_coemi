import pytest
from unittest.mock import MagicMock, patch
from app.db.models import AuditLog, BlacklistedToken, User
from app.core import security
from app.api import deps
from datetime import timedelta

# We use 'test_client' fixture from conftest.py
# We use 'db_session' fixture to inspect the database

def test_brute_force_detection(test_client, db_session):
    """
    Test that >5 failed login attempts trigger a CRITICAL audit log.
    """
    username = "admin" # Admin is created by the override_user_auth/test_client setup usually,
                       # but here we rely on the DB.
                       # test_client fixture creates an admin user in get_current_user override,
                       # but for LOGIN we need the user in the DB to verify password.

    # Ensure user exists in the DB (conftest db_session creates tables but empty)
    # The 'test_client' fixture overrides get_current_user but doesn't necessarily seed the DB for 'login'.
    # We must seed it.

    user = db_session.query(User).filter(User.username == username).first()
    if not user:
        user = User(
            username=username,
            hashed_password=security.get_password_hash("password123"),
            is_admin=True
        )
        db_session.add(user)
        db_session.commit()

    # Clean up previous logs to have a clean state
    db_session.query(AuditLog).delete()
    db_session.commit()

    # Attempt 1-5 (MEDIUM/LOW severity)
    # The logic checks count of PAST failures.
    # 0 past failures -> 1st attempt fails -> Log.
    # ...
    # 4 past failures -> 5th attempt fails -> Log.
    # 5 past failures -> 6th attempt fails -> Log CRITICAL.

    for i in range(5):
        response = test_client.post(
            "/auth/login", # relative to base_url set in test_client
            data={"username": username, "password": "wrong_password"}
        )
        assert response.status_code == 400

    # Verify not yet CRITICAL (last log was attempt 5, count was 4)
    # Wait, if I have 5 failures in DB.
    # Next attempt: failed_count = 5. if failed_count >= 5 -> Critical.

    # Attempt 6 (Should trigger CRITICAL)
    test_client.post("/auth/login", data={"username": username, "password": "wrong_password"})

    # Check the last log
    critical_log = db_session.query(AuditLog).filter(
        AuditLog.action == "LOGIN_FAILED",
        AuditLog.severity == "CRITICAL"
    ).first()

    assert critical_log is not None
    assert "Tentativo di login fallito" in critical_log.details

def test_login_session_locked(test_client, db_session):
    """
    Test that if session lock cannot be acquired, login returns read_only=True.
    """
    username = "testuser"
    password = "password123"
    hashed = security.get_password_hash(password)

    user = User(username=username, hashed_password=hashed, is_admin=False)
    db_session.add(user)
    db_session.commit()

    owner_info = {"username": "other_user", "host": "1.2.3.4"}

    with patch("app.api.routers.auth.db_security.acquire_session_lock", return_value=(False, owner_info)):
        response = test_client.post(
            "/auth/login",
            data={"username": username, "password": password}
        )

    assert response.status_code == 200
    data = response.json()
    assert data["read_only"] is True
    assert data["lock_owner"] == owner_info

def test_login_session_unlocked(test_client, db_session):
    """
    Test that if session lock is acquired, login returns read_only=False.
    """
    username = "testuser2"
    password = "password123"
    hashed = security.get_password_hash(password)

    user = User(username=username, hashed_password=hashed, is_admin=False)
    db_session.add(user)
    db_session.commit()

    with patch("app.api.routers.auth.db_security.acquire_session_lock", return_value=(True, None)):
        response = test_client.post(
            "/auth/login",
            data={"username": username, "password": password}
        )

    assert response.status_code == 200
    data = response.json()
    assert data["read_only"] is False

def test_logout_cleanup_called(test_client, db_session):
    """
    Test that logout calls db_security.cleanup().
    """
    username = "admin_logout"
    password = "password123"

    # Seed user
    user = User(
        username=username,
        hashed_password=security.get_password_hash(password),
        is_admin=True
    )
    db_session.add(user)
    db_session.commit()

    # Login first to get token
    resp = test_client.post("/auth/login", data={"username": username, "password": password})
    assert resp.status_code == 200
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    with patch("app.api.routers.auth.db_security.cleanup") as mock_cleanup:
        response = test_client.post("/auth/logout", headers=headers)

    assert response.status_code == 200
    mock_cleanup.assert_called_once()

    # Verify token is blacklisted
    blacklisted = db_session.query(BlacklistedToken).filter(BlacklistedToken.token == token).first()
    assert blacklisted is not None
