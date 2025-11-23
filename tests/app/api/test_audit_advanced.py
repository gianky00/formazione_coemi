from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.db.models import AuditLog, User
from app.utils.audit import log_security_action
from datetime import datetime, timedelta

def test_audit_log_filtering(test_client: TestClient, db_session: Session):
    # 1. Setup: Create users and logs
    user1 = User(username="user1", hashed_password="x", is_admin=True)
    user2 = User(username="user2", hashed_password="x", is_admin=True)
    db_session.add(user1)
    db_session.add(user2)
    db_session.commit()

    # Create logs with different dates and categories
    # User 1
    log1 = AuditLog(user_id=user1.id, username=user1.username, action="ACT1", category="AUTH", timestamp=datetime.utcnow() - timedelta(days=10))
    log2 = AuditLog(user_id=user1.id, username=user1.username, action="ACT2", category="USER_MGMT", timestamp=datetime.utcnow())

    # User 2
    log3 = AuditLog(user_id=user2.id, username=user2.username, action="ACT3", category="AUTH", timestamp=datetime.utcnow())

    # System
    log4 = AuditLog(user_id=None, username="SYSTEM", action="SYS1", category="SYSTEM", timestamp=datetime.utcnow())

    db_session.add_all([log1, log2, log3, log4])
    db_session.commit()

    # 2. Filter by User
    resp = test_client.get(f"/audit/?user_id={user1.id}")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2
    assert all(l["username"] == "user1" for l in data)

    # 3. Filter by Date Range (User 1 only recent)
    start = (datetime.utcnow() - timedelta(days=1)).isoformat()
    resp = test_client.get(f"/audit/?user_id={user1.id}&start_date={start}")
    data = resp.json()
    assert len(data) == 1
    assert data[0]["action"] == "ACT2"

    # 4. Filter by Category
    resp = test_client.get(f"/audit/?category=AUTH")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2
    assert all(l["category"] == "AUTH" for l in data)

    # 5. Create Log via POST
    resp = test_client.post("/audit/", json={"action": "TEST_CREATE", "details": "foo", "category": "CONFIG"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["action"] == "TEST_CREATE"
    assert data["category"] == "CONFIG"
    assert data["username"] == "admin" # Mocked current user
