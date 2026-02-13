from app.core import security
from app.db.models import User


def test_login_previous_timestamp(test_client, db_session):
    # 1. Create user
    hashed = security.get_password_hash("pass")
    user = User(username="login_test", hashed_password=hashed, is_admin=False)
    db_session.add(user)
    db_session.commit()

    # 2. Login 1 (First time)
    resp1 = test_client.post("/auth/login", data={"username": "login_test", "password": "pass"})
    assert resp1.status_code == 200
    data1 = resp1.json()
    assert data1["previous_login"] is None

    # 3. Login 2 (Second time)
    resp2 = test_client.post("/auth/login", data={"username": "login_test", "password": "pass"})
    assert resp2.status_code == 200
    data2 = resp2.json()
    assert data2["previous_login"] is not None

    # 4. Login 3
    # Small delay to ensure timestamp difference if fast execution
    import time

    time.sleep(0.1)

    resp3 = test_client.post("/auth/login", data={"username": "login_test", "password": "pass"})
    assert resp3.status_code == 200
    data3 = resp3.json()

    assert data3["previous_login"] is not None
    assert data3["previous_login"] != data2["previous_login"]
