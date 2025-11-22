from app.db.models import User
from app.core.security import get_password_hash

def test_auth_flow(test_client, db_session):
    # 1. Seed Admin User
    admin_user = User(
        username="admin",
        hashed_password=get_password_hash("allegretti@coemi"),
        account_name="Amministratore",
        is_admin=True
    )
    db_session.add(admin_user)
    db_session.commit()

    # 2. Login as Admin
    login_payload = {"username": "admin", "password": "allegretti@coemi"}
    response = test_client.post("/auth/login", data=login_payload)
    assert response.status_code == 200
    token_data = response.json()
    assert "access_token" in token_data
    assert token_data["username"] == "admin"
    assert token_data["is_admin"] is True

    access_token = token_data["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}

    # 3. Create New User (as Admin)
    new_user_payload = {
        "username": "newuser",
        "password": "newpassword",
        "account_name": "New User",
        "is_admin": False
    }
    response = test_client.post("/users/", json=new_user_payload, headers=headers)
    assert response.status_code == 200
    new_user_data = response.json()
    assert new_user_data["username"] == "newuser"

    # 4. Verify New User exists via List (as Admin)
    response = test_client.get("/users/", headers=headers)
    assert response.status_code == 200
    users = response.json()
    assert len(users) == 2 # admin + newuser

    # 5. Login as New User
    login_payload_user = {"username": "newuser", "password": "newpassword"}
    response = test_client.post("/auth/login", data=login_payload_user)
    assert response.status_code == 200
    user_token_data = response.json()
    assert user_token_data["username"] == "newuser"
    assert user_token_data["is_admin"] is False

    user_token = user_token_data["access_token"]
    user_headers = {"Authorization": f"Bearer {user_token}"}

    # 6. Try to create user as Non-Admin (Should Fail)
    fail_payload = {
        "username": "failuser",
        "password": "failpassword"
    }
    response = test_client.post("/users/", json=fail_payload, headers=user_headers)
    assert response.status_code == 400 # or 403 if I used scopes, but deps raises 400 for not active admin

    # 7. Update User (Reset Password) as Admin
    update_payload = {"password": "resetpassword"}
    response = test_client.put(f"/users/{new_user_data['id']}", json=update_payload, headers=headers)
    assert response.status_code == 200

    # 8. Login with New Password
    login_payload_reset = {"username": "newuser", "password": "resetpassword"}
    response = test_client.post("/auth/login", data=login_payload_reset)
    assert response.status_code == 200
