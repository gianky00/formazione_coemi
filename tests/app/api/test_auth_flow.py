from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core import security
from app.db.models import User

# Note: We do NOT use the global override_get_current_user here because we want to test the LOGIN flow
# which issues tokens.


def test_login_updates_previous_access(test_client: TestClient, db_session: Session):
    # 1. Create a user manually
    password = "password123"
    hashed = security.get_password_hash(password)
    user = User(username="testuser", hashed_password=hashed, is_admin=False)
    db_session.add(user)
    db_session.commit()

    # 2. Login First Time
    response = test_client.post("/auth/login", data={"username": "testuser", "password": password})
    assert response.status_code == 200
    data = response.json()
    assert data["previous_login"] is None

    # Reload user to check last_login
    db_session.refresh(user)
    first_login_time = user.last_login
    assert first_login_time is not None
    assert user.previous_login is None

    # 3. Login Second Time
    response = test_client.post("/auth/login", data={"username": "testuser", "password": password})
    assert response.status_code == 200
    data = response.json()

    # Verify previous_login in response
    assert data["previous_login"] is not None
    # Check that previous_login matches the FIRST login time
    # Pydantic serializes to string, DB has datetime.
    # We compare string representations or parse.
    # Note: DB might store microseconds, response might truncate or formatted differently.

    # Let's check DB state directly
    db_session.refresh(user)
    assert user.previous_login == first_login_time
    assert user.last_login > first_login_time
