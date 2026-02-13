from datetime import datetime, timedelta

from app.db.models import AuditLog
from app.services.file_maintenance import cleanup_audit_logs


def test_audit_cleanup_size_limit(db_session):
    # Create 15 logs with sequential timestamps (very recent to avoid time-based cleanup)
    now = datetime.now()
    for i in range(15):
        # timestamps: now - 14 min, now - 13 min, ...
        log = AuditLog(action=f"LOG_{i}", timestamp=now - timedelta(minutes=15 - i))
        db_session.add(log)
    db_session.commit()

    assert db_session.query(AuditLog).count() == 15

    # Clean with max 10
    cleanup_audit_logs(db_session, max_records=10)

    # Should be 10 left (plus maybe LOG_CLEANUP log if implemented?
    # cleanup_audit_logs calls log_security_action which ADDS a log.
    count = db_session.query(AuditLog).count()

    # Logic:
    # 1. Time based cleanup: 0 deleted (they are recent)
    # 2. Size based cleanup: 5 deleted (15 - 10 = 5). Remaining: 10.
    # 3. log_security_action adds 1 log. Total: 11.

    assert count == 11

    # Verify oldest removed.
    # The first one should be LOG_5 (since 0-4 removed).
    ordered = db_session.query(AuditLog).order_by(AuditLog.timestamp.asc(), AuditLog.id.asc()).all()

    assert ordered[0].action == "LOG_5"
    assert ordered[-1].action == "LOG_CLEANUP"
