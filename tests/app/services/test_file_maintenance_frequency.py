from unittest.mock import MagicMock, patch

import pytest

from app.db.models import AuditLog, Certificato
from app.services import file_maintenance


@pytest.fixture
def mock_db_session():
    return MagicMock()


def test_maintenance_skips_if_already_ran(mock_db_session):
    # Setup: Mock query to return an AuditLog when searching for SYSTEM_MAINTENANCE
    mock_db_session.query.return_value.filter.return_value.first.return_value = AuditLog(id=1)

    with (
        patch("app.services.file_maintenance.settings") as mock_settings,
        patch("app.services.file_maintenance.os.path.exists", return_value=True),
    ):
        mock_settings.DATABASE_PATH = "/mock"

        file_maintenance.organize_expired_files(mock_db_session)

        # Verify that we checked AuditLog
        # Verify that we DID NOT query Certificato

        # Helper to check calls
        calls = mock_db_session.query.call_args_list
        # calls[0] should be AuditLog
        # Should be no call with Certificato

        has_audit_query = any(args[0] == AuditLog for args, _ in calls)
        has_cert_query = any(args[0] == Certificato for args, _ in calls)

        assert has_audit_query, "Should check AuditLog"
        assert not has_cert_query, "Should skip Certificato query"


def test_maintenance_runs_if_not_ran_today(mock_db_session):
    # Setup: Mock query to return None for AuditLog
    # Chain: query(AuditLog).filter().first() -> None
    # Then: query(Certificato)...

    # We need to handle sequential calls to query() returning different mocks?
    # Or side_effect on query(Model).

    def query_side_effect(model):
        mock_q = MagicMock()
        if model == AuditLog:
            mock_q.filter.return_value.first.return_value = None
        elif model == Certificato:
            # Return empty list to stop logic
            mock_q.filter.return_value.all.return_value = []
        return mock_q

    mock_db_session.query.side_effect = query_side_effect

    with (
        patch("app.services.file_maintenance.settings") as mock_settings,
        patch("app.services.file_maintenance.os.path.exists", return_value=True),
        patch("app.services.file_maintenance.log_security_action") as mock_log,
    ):
        mock_settings.DATABASE_PATH = "/mock"

        file_maintenance.organize_expired_files(mock_db_session)

        # Should have called log_security_action at end
        mock_log.assert_called()
