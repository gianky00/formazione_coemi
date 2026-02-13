from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core import security
from app.db.models import User


def test_trigger_maintenance_endpoint(test_client: TestClient, db_session: Session, mocker):
    # Mock organize_expired_files to avoid actual file system ops and verify call
    mock_maintenance = mocker.patch("app.api.routers.system.organize_expired_files")

    # 1. Setup User
    username = "maint_user"
    password = "password"
    hashed = security.get_password_hash(password)
    user = User(username=username, hashed_password=hashed, is_admin=False)
    db_session.add(user)
    db_session.commit()

    # 2. Login
    login_data = {"username": username, "password": password}
    response = test_client.post("/auth/login", data=login_data)
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 3. Call endpoint
    response = test_client.post("/system/maintenance/background", headers=headers)
    assert response.status_code == 200
    assert response.json() == {"status": "started"}

    # NOTE: BackgroundTasks in FastAPI TestClient run synchronously after the response is returned.
    # So the mock should have been called.
    mock_maintenance.assert_called_once()
