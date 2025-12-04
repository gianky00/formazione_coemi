import pytest
from unittest.mock import patch, MagicMock
from app.db.models import User, AuditLog
from app.api import deps
from fastapi import HTTPException

# --- Auth Deps ---
def test_get_current_user_deleted(db_session):
    # Mock token decoding to return a user ID that doesn't exist
    # jwt.decode is called in get_current_user -> calls security.decode_token?
    # No, get_current_user code:
    # payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[security.ALGORITHM])

    with patch("jose.jwt.decode") as mock_jwt:
        mock_jwt.return_value = {"sub": "999"} # ID 999

        # Ensure ID 999 is not in DB
        assert db_session.query(User).filter_by(id=999).first() is None

        with pytest.raises(HTTPException) as exc:
            deps.get_current_user(token="valid_token", db=db_session)
        # deps.py raises 401 credentials_exception if user is not found
        assert exc.value.status_code == 401

# --- System Concurrency ---
def test_maintenance_already_running(test_client, user_token_headers):
    # Patch the global variable in system module
    with patch("app.api.routers.system.MAINTENANCE_RUNNING", True):
        res = test_client.post("/system/maintenance/background", headers=user_token_headers)
        assert res.status_code == 200
        assert res.json()["status"] == "skipped"

# --- Config Exception ---
def test_move_database_exception(test_client, admin_token_headers):
    # Mock db_security in the config router
    with patch("app.api.routers.config.db_security") as mock_sec:
        mock_sec.move_database.side_effect = Exception("Disk Full")

        # Need mock path check too, otherwise 400 "invalid folder"
        with patch("pathlib.Path.is_dir", return_value=True):
            res = test_client.post("/config/move-database", json={"new_path": "/tmp/new"}, headers=admin_token_headers)

        assert res.status_code == 500
        assert "Disk Full" in res.json()["detail"]

# --- Audit Categories ---
def test_audit_categories_filtering(test_client, admin_token_headers, db_session):
    # Insert categories: Valid, None, Empty
    l1 = AuditLog(username="u", action="a", category="VALID")
    l2 = AuditLog(username="u", action="a", category=None)
    l3 = AuditLog(username="u", action="a", category="")
    db_session.add_all([l1, l2, l3])
    db_session.commit()

    res = test_client.get("/audit/categories", headers=admin_token_headers)
    assert res.status_code == 200
    cats = res.json()
    assert "VALID" in cats
    assert None not in cats
    assert "" not in cats
