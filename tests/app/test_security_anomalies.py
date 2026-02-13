from app.api import deps
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
    # Note: TestClient uses 'testclient' as host usually, or 127.0.0.1
    for _ in range(6):
        response = test_client.post(
            "/auth/login", data={"username": "victim", "password": "wrongpassword"}
        )
        assert response.status_code == 400

    # 3. Check logs
    logs = (
        db_session.query(AuditLog)
        .filter(AuditLog.action == "LOGIN_FAILED")
        .order_by(AuditLog.timestamp)
        .all()
    )
    assert len(logs) == 6

    # First should be MEDIUM
    assert logs[0].severity == "MEDIUM"

    # The 6th attempt (index 5) should be CRITICAL because there are 5 prior failures
    # Logic: count existing failures. If >= 5, severity=CRITICAL.
    # 1st attempt: count=0. Medium. Logged.
    # 2nd attempt: count=1. Medium. Logged.
    # 3rd attempt: count=2. Medium. Logged.
    # 4th attempt: count=3. Medium. Logged.
    # 5th attempt: count=4. Medium. Logged.
    # 6th attempt: count=5. Critical. Logged.

    assert logs[5].severity == "CRITICAL"


def test_unauthorized_admin_access_logging(test_client, db_session):
    # Override get_current_user to return non-admin
    # We need to save the original override to restore it (though pytest fixture scope might handle it if we are careful)
    # But here we are modifying app.dependency_overrides which is global.

    original_override = fastapi_app.dependency_overrides.get(deps.get_current_user)

    def mock_get_current_user_non_admin():
        return User(id=2, username="hacker", is_admin=False)

    fastapi_app.dependency_overrides[deps.get_current_user] = mock_get_current_user_non_admin

    try:
        # Try to access an admin endpoint (e.g., GET /audit/)
        response = test_client.get("/audit/")
        assert response.status_code == 400  # get_current_active_admin raises 400

        # Check logs
        log = db_session.query(AuditLog).filter(AuditLog.action == "UNAUTHORIZED_ACCESS").first()
        assert log is not None
        assert log.username == "hacker"
        assert log.severity == "CRITICAL"
        assert log.category == "AUTH"
    finally:
        # Restore
        if original_override:
            fastapi_app.dependency_overrides[deps.get_current_user] = original_override
        else:
            del fastapi_app.dependency_overrides[deps.get_current_user]
