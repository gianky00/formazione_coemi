from app.core import security
from app.db.models import AuditLog, User
from app.main import app as fastapi_app


def test_brute_force_detection(test_client, db_session):
    # 1. Create a user
    hashed = security.get_password_hash("password123")
    user = User(username="victim", hashed_password=hashed, is_admin=False)
    db_session.add(user)
    db_session.commit()

    # 2. Fail login 6 times
    for _ in range(6):
        response = test_client.post(
            "/auth/login", data={"username": "victim", "password": "wrongpassword"}
        )
        assert response.status_code == 401

    # 3. Check logs
    logs = db_session.query(AuditLog).filter(AuditLog.action == "LOGIN_FAILED").all()
    assert len(logs) >= 6


def test_unauthorized_admin_access_logging(test_client, db_session):
    # 1. Create a non-admin user
    hashed = security.get_password_hash("pass")
    hacker = User(username="hacker", hashed_password=hashed, is_admin=False)
    db_session.add(hacker)
    db_session.commit()

    # 2. Login as non-admin
    resp = test_client.post("/auth/login", data={"username": "hacker", "password": "pass"})
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 3. Try to access an admin endpoint (e.g., GET /audit/)
    # We must ensure dependency overrides don't bypass the check
    fastapi_app.dependency_overrides = {}

    response = test_client.get("/audit/", headers=headers)
    assert response.status_code == 403

    # 4. Check logs
    log = db_session.query(AuditLog).filter(AuditLog.action == "UNAUTHORIZED_ACCESS").first()
    assert log is not None
    assert log.username == "hacker"
