import pytest
from app.db.models import AuditLog
from app.services.file_maintenance import cleanup_audit_logs
from datetime import datetime

def test_audit_cleanup_size_limit(db_session):
    # Create 15 logs with sequential timestamps
    for i in range(15):
        # timestamps: 10:00, 10:01, ...
        log = AuditLog(action=f"LOG_{i}", timestamp=datetime(2025, 1, 1, 10, i))
        db_session.add(log)
    db_session.commit()

    assert db_session.query(AuditLog).count() == 15

    # Clean with max 10
    cleanup_audit_logs(db_session, max_records=10)

    # Should be 10 left (plus maybe LOG_CLEANUP log if implemented?
    # cleanup_audit_logs calls log_security_action which ADDS a log.
    # So count might be 11?
    # LOG_CLEANUP is added *after* delete commit.

    count = db_session.query(AuditLog).count()
    # It deleted 5. Left 10. Added 1 (LOG_CLEANUP). Total 11.
    # Or 10 if LOG_CLEANUP wasn't committed? It is committed inside log_security_action.

    # Let's check logic.
    # deleted_excess = 5.
    # log_security_action adds 1.

    assert count == 11

    # Verify oldest removed.
    # The first one should be LOG_5 (since 0-4 removed).
    # But we added LOG_CLEANUP at end (newest).

    ordered = db_session.query(AuditLog).order_by(AuditLog.timestamp.asc(), AuditLog.id.asc()).all()
    # first 10 should be LOG_5...LOG_14
    # last one LOG_CLEANUP

    assert ordered[0].action == "LOG_5"
    assert ordered[-1].action == "LOG_CLEANUP"
