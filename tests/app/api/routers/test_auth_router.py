from app.api import deps
from app.core import security
from app.db.models import AuditLog, BlacklistedToken, User
from app.db.session import get_db
from app.main import app


def test_login_success(test_client, db_session):
    # Remove auth overrides to test real login
    app.dependency_overrides = {}
    app.dependency_overrides[get_db] = lambda: db_session

    # Create user
    hashed = security.get_password_hash("secret")
    user = User(username="testuser", hashed_password=hashed)
    db_session.add(user)
    db_session.commit()

    response = test_client.post("/auth/login", data={"username": "testuser", "password": "secret"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["username"] == "testuser"
    assert data["is_admin"] is False

    # Verify audit log
    log = db_session.query(AuditLog).filter_by(action="LOGIN", username="testuser").first()
    assert log is not None


def test_login_failure(test_client, db_session):
    app.dependency_overrides = {}
    app.dependency_overrides[get_db] = lambda: db_session

    response = test_client.post("/auth/login", data={"username": "wrong", "password": "wrong"})
    assert response.status_code == 400
    assert "Incorrect email or password" in response.json()["detail"]

    # Verify audit log for failure
    log = db_session.query(AuditLog).filter_by(action="LOGIN_FAILED").first()
    assert log is not None


def test_login_brute_force_detection(test_client, db_session):
    app.dependency_overrides = {}
    app.dependency_overrides[get_db] = lambda: db_session

    # Fail 5 times
    for _ in range(5):
        test_client.post("/auth/login", data={"username": "attacker", "password": "wrong"})

    # 6th attempt
    test_client.post("/auth/login", data={"username": "attacker", "password": "wrong"})

    # Check for critical log
    logs = db_session.query(AuditLog).filter_by(action="LOGIN_FAILED", severity="CRITICAL").all()
    assert len(logs) >= 1


def test_logout(test_client, db_session):
    # Use default overrides which simulate authenticated user (admin)

    # Needs a token dependency, normally extracted from header.
    # test_client calls with headers usually.
    # But deps.oauth2_scheme extracts from Authorization header.
    # The default test_client override for get_current_user bypasses token check?
    # No, deps.oauth2_scheme is still there.
    # We need to provide a fake token header.

    response = test_client.post("/auth/logout", headers={"Authorization": "Bearer fake-token"})
    assert response.status_code == 200

    # Verify blacklist
    # Wait, the logout endpoint adds 'fake-token' to blacklist.
    token = db_session.query(BlacklistedToken).filter_by(token="fake-token").first()
    assert token is not None


def test_change_password_success(test_client, db_session):
    # Setup: override current user with a known one
    hashed = security.get_password_hash("oldpass")
    user = User(username="changer", hashed_password=hashed)
    db_session.add(user)
    db_session.commit()

    app.dependency_overrides[deps.get_current_user] = lambda: user
    app.dependency_overrides[deps.check_write_permission] = lambda: None
    app.dependency_overrides[get_db] = lambda: db_session

    response = test_client.post(
        "/auth/change-password",
        json={"old_password": "oldpass", "new_password": "newpass", "confirm_password": "newpass"},
    )

    assert response.status_code == 200

    db_session.refresh(user)
    assert security.verify_password("newpass", user.hashed_password)


def test_change_password_wrong_old(test_client, db_session):
    hashed = security.get_password_hash("oldpass")
    user = User(username="changer2", hashed_password=hashed)
    db_session.add(user)
    db_session.commit()

    app.dependency_overrides[deps.get_current_user] = lambda: user
    app.dependency_overrides[deps.check_write_permission] = lambda: None
    app.dependency_overrides[get_db] = lambda: db_session

    response = test_client.post(
        "/auth/change-password",
        json={"old_password": "wrong", "new_password": "newpass", "confirm_password": "newpass"},
    )

    assert response.status_code == 400
    assert "password attuale non è corretta" in response.json()["detail"]
