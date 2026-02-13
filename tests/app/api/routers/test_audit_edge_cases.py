from datetime import datetime

from app.db.models import AuditLog


def test_export_audit_logs_empty(test_client, admin_token_headers, db_session):
    db_session.query(AuditLog).delete()
    db_session.commit()

    res = test_client.get("/audit/export", headers=admin_token_headers)
    assert res.status_code == 200
    # If empty, pandas writes BOM + newline (utf-8-sig) but no headers if columns not inferred
    assert res.content.startswith(b"\xef\xbb\xbf")


def test_read_audit_logs_end_date_midnight(test_client, admin_token_headers, db_session):
    # Create log at 23:00 today
    today_late = datetime.now().replace(hour=23, minute=0, second=0)
    log = AuditLog(username="late", action="TEST", timestamp=today_late)
    db_session.add(log)
    db_session.commit()

    # Query with end_date = Today (00:00:00)
    # Logic should expand it to 23:59:59
    today_str = datetime.now().date().isoformat()
    res = test_client.get(f"/audit/?end_date={today_str}", headers=admin_token_headers)

    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 1
    assert any(l["username"] == "late" for l in data)
