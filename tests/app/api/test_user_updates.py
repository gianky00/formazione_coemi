from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.core import security
from app.db.models import User

def test_update_user_duplicate_username(test_client: TestClient, db_session: Session):
    # 1. Create two users manually
    user1 = User(
        username="user1",
        hashed_password=security.get_password_hash("password"),
        is_admin=False
    )
    user2 = User(
        username="user2",
        hashed_password=security.get_password_hash("password"),
        is_admin=False
    )
    db_session.add(user1)
    db_session.add(user2)
    db_session.commit()
    db_session.refresh(user1)
    db_session.refresh(user2)

    # 2. Try to update user1's username to "user2"
    update_data = {
        "username": "user2"
    }

    # This should return 400 or 409, not raise an IntegrityError
    response = test_client.put(f"/users/{user1.id}", json=update_data)

    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]
