import os
from datetime import date
from unittest.mock import MagicMock, patch

from app.db.models import Certificato, Dipendente
from app.services import sync_service


def test_link_orphans_success():
    mock_db = MagicMock()
    mock_dipendente = MagicMock(spec=Dipendente)
    mock_dipendente.id = 10
    mock_dipendente.nome = "Mario"
    mock_dipendente.cognome = "Rossi"

    orphan = MagicMock(spec=Certificato)
    orphan.id = 1
    orphan.dipendente_id = None
    orphan.nome_dipendente_raw = "Mario Rossi"
    orphan.data_nascita_raw = "01/01/1980"
    orphan.corso.categoria_corso = "SICUREZZA"
    orphan.data_scadenza_calcolata = date(2025, 1, 1)
    orphan.file_path = None

    mock_db.query.return_value.options.return_value.filter.return_value.all.return_value = [orphan]

    # Setup paths
    orphan_path = os.path.join("tmp", "orphan", "mario.pdf")
    linked_path = os.path.join("tmp", "linked", "mario_linked.pdf")

    def side_effect_exists(path):
        if path == orphan_path:
            return True
        return False  # Destination does not exist

    with (
        patch(
            "app.services.sync_service.matcher.find_employee_by_name", return_value=mock_dipendente
        ),
        patch("app.services.sync_service.find_document", return_value=orphan_path),
        patch("app.services.sync_service.construct_certificate_path", return_value=linked_path),
        patch(
            "app.services.sync_service.certificate_logic.get_certificate_status",
            return_value="attivo",
        ),
        patch("os.path.exists", side_effect=side_effect_exists),
        patch("os.makedirs"),
        patch("shutil.move") as mock_move,
        patch("app.services.sync_service.settings") as mock_settings,
    ):
        mock_settings.DATABASE_PATH = "tmp"

        count = sync_service.link_orphaned_certificates(mock_db)

        assert count == 1
        assert orphan.dipendente_id == 10
        mock_move.assert_called_with(orphan_path, linked_path)


def test_link_orphans_no_match():
    mock_db = MagicMock()
    orphan = MagicMock(spec=Certificato)
    orphan.dipendente_id = None
    orphan.nome_dipendente_raw = "Unknown"
    mock_db.query.return_value.options.return_value.filter.return_value.all.return_value = [orphan]

    with patch("app.services.sync_service.matcher.find_employee_by_name", return_value=None):
        count = sync_service.link_orphaned_certificates(mock_db)
        assert count == 0
        assert orphan.dipendente_id is None
