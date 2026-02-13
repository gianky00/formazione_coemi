import os
from datetime import date, timedelta
from unittest.mock import MagicMock, patch

from app.db.models import AuditLog, Certificato, Corso, Dipendente
from app.services import file_maintenance


def test_organize_expired_files_moves_archived():
    # Setup Data
    dip = Dipendente(nome="Mario", cognome="Rossi", matricola="123")
    corso = Corso(categoria_corso="SICUREZZA")
    cert = Certificato(
        dipendente=dip, corso=corso, data_scadenza_calcolata=date.today() - timedelta(days=1)
    )

    mock_db_session = MagicMock()

    def query_side_effect(model):
        if model == AuditLog:
            mock_query = MagicMock()
            mock_query.filter.return_value.first.return_value = None
            return mock_query
        elif model == Certificato:
            mock_query = MagicMock()
            mock_query.filter.return_value.all.return_value = [cert]
            return mock_query
        return MagicMock()

    mock_db_session.query.side_effect = query_side_effect

    base_path = os.path.join("mock", "db", "path")

    # Mocks
    with (
        patch("app.services.file_maintenance.settings") as mock_settings,
        patch(
            "app.services.file_maintenance.certificate_logic.get_certificate_status",
            return_value="archiviato",
        ),
        patch(
            "app.services.file_maintenance.archive_certificate_file", return_value=True
        ) as mock_archive_func,
        patch("app.services.file_maintenance.scan_and_archive_orphans", return_value=0),
        patch("app.services.file_maintenance.clean_all_empty_folders"),
        patch("app.services.file_maintenance.cleanup_audit_logs"),
        patch("os.path.exists", return_value=True),
    ):  # Fix: Mock existence of database path
        mock_settings.DATABASE_PATH = base_path

        file_maintenance.organize_expired_files(mock_db_session)

        # Assert that archive_certificate_file was called with the certificate
        mock_archive_func.assert_called_with(mock_db_session, cert)
