import pytest
import os
from app.db.models import User
from app.core import security

@pytest.fixture
def admin_user(db_session):
    """Ensure the admin user exists in the DB with ID 1."""
    # Check if exists first to avoid conflict if session is reused?
    # db_session is function scoped and cleared.
    u = User(id=1, username="admin", hashed_password="pw", is_admin=True)
    db_session.add(u)
    db_session.commit()
    return u

def test_read_users(test_client, admin_token_headers, admin_user):
    response = test_client.get("/users/", headers=admin_token_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["username"] == "admin"

def test_create_user_success(test_client, admin_token_headers, admin_user):
    payload = {
        "username": "newuser",
        "account_name": "New User",
        "is_admin": False,
        "password": "initialpassword"
    }

    response = test_client.post("/users/", json=payload, headers=admin_token_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "newuser"
    assert data["id"] is not None
    assert data["id"] != 1

def test_create_user_duplicate(test_client, admin_token_headers, db_session, admin_user):
    # Create manually first
    u = User(username="duplicate", hashed_password="pw", is_admin=False)
    db_session.add(u)
    db_session.commit()

    payload = {"username": "duplicate", "is_admin": False}
    response = test_client.post("/users/", json=payload, headers=admin_token_headers)
    assert response.status_code == 400

def test_update_user_success(test_client, admin_token_headers, db_session, admin_user):
    u = User(username="toupdate", hashed_password="pw", is_admin=False)
    db_session.add(u)
    db_session.commit()

    payload = {"account_name": "Updated Name"}
    response = test_client.put(f"/users/{u.id}", json=payload, headers=admin_token_headers)
    assert response.status_code == 200
    assert response.json()["account_name"] == "Updated Name"

def test_update_user_password(test_client, admin_token_headers, db_session, admin_user):
    u = User(username="pwchange", hashed_password="old", is_admin=False)
    db_session.add(u)
    db_session.commit()

    payload = {"password": "newpassword"}
    response = test_client.put(f"/users/{u.id}", json=payload, headers=admin_token_headers)
    assert response.status_code == 200

    # Verify hash changed
    db_session.refresh(u)
    assert security.verify_password("newpassword", u.hashed_password)

def test_update_user_duplicate_username(test_client, admin_token_headers, db_session, admin_user):
    u1 = User(username="u1", hashed_password="pw", is_admin=False)
    u2 = User(username="u2", hashed_password="pw", is_admin=False)
    db_session.add_all([u1, u2])
    db_session.commit()

    payload = {"username": "u2"} # Try to rename u1 to u2
    response = test_client.put(f"/users/{u1.id}", json=payload, headers=admin_token_headers)
    assert response.status_code == 400

def test_update_user_not_found(test_client, admin_token_headers, admin_user):
    response = test_client.put("/users/9999", json={"username": "ghost"}, headers=admin_token_headers)
    assert response.status_code == 404

def test_delete_user_success(test_client, admin_token_headers, db_session, admin_user):
    u = User(username="todelete", hashed_password="pw", is_admin=False)
    db_session.add(u)
    db_session.commit()

    response = test_client.delete(f"/users/{u.id}", headers=admin_token_headers)
    assert response.status_code == 200

    # Verify deleted
    assert db_session.query(User).filter_by(id=u.id).first() is None

def test_delete_user_self_prevention(test_client, admin_token_headers, admin_user):
    # admin_user has ID 1. Current user in token is ID 1.
    response = test_client.delete("/users/1", headers=admin_token_headers)
    assert response.status_code == 400
    assert "cannot delete your own account" in response.json()["detail"]

def test_delete_user_not_found(test_client, admin_token_headers, admin_user):
    response = test_client.delete("/users/9999", headers=admin_token_headers)
    assert response.status_code == 404
