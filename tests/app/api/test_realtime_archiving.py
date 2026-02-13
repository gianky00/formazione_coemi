import os
from datetime import datetime, timedelta
from unittest.mock import patch

from app.db.models import AuditLog, Certificato, Corso, Dipendente
from app.services.file_maintenance import cleanup_audit_logs
from app.utils.file_security import sanitize_filename


def test_realtime_archiving_on_create(test_client, db_session, test_dirs):
    # Setup Data
    cat = "ANTINCENDIO"
    dip = Dipendente(nome="Mario", cognome="Rossi", matricola="123")
    corso = Corso(nome_corso="Corso A", categoria_corso=cat)
    # Old cert (Valid but old)
    cert_old = Certificato(
        dipendente=dip,
        corso=corso,
        data_rilascio=datetime.strptime("01/01/2020", "%d/%m/%Y").date(),
        data_scadenza_calcolata=datetime.strptime("01/01/2025", "%d/%m/%Y").date(),
    )
    db_session.add(dip)
    db_session.add(corso)
    db_session.add(cert_old)
    db_session.commit()
    db_session.refresh(cert_old)

    # Create Old File (in ATTIVO because > today? Or expired?)
    # Assume 2025 is future.
    nome_fs = sanitize_filename("Rossi Mario")
    folder = os.path.join(str(test_dirs), "DOCUMENTI DIPENDENTI", f"{nome_fs} (123)", cat, "ATTIVO")
    os.makedirs(folder, exist_ok=True)
    old_filename = f"{nome_fs} (123) - {cat} - 01_01_2025.pdf"
    old_path = os.path.join(folder, old_filename)
    with open(old_path, "w") as f:
        f.write("old")

    # Create New Cert via API
    # 2024. New cert release 2024.
    payload = {
        "nome": "Rossi Mario",
        "data_nascita": "",
        "corso": "Corso A",
        "categoria": cat,
        "data_rilascio": "01/01/2024",
        "data_scadenza": "01/01/2029",
    }

    # Patch shutil.move
    with patch("shutil.move") as mock_move:
        response = test_client.post("/certificati/", json=payload)

    assert response.status_code == 200

    # Verify Archiving Triggered
    mock_move.assert_called()
    args = mock_move.call_args[0]
    # Check that destination has STORICO
    assert "STORICO" in args[1]


def test_audit_cleanup(db_session):
    # Setup logs
    today = datetime.now()
    old_date = today - timedelta(days=400)
    recent_date = today - timedelta(days=10)

    log_old = AuditLog(action="OLD", timestamp=old_date)
    log_recent = AuditLog(action="RECENT", timestamp=recent_date)

    db_session.add(log_old)
    db_session.add(log_recent)
    db_session.commit()

    # Run cleanup
    cleanup_audit_logs(db_session, retention_days=365)

    # Verify
    assert db_session.query(AuditLog).filter(AuditLog.action == "OLD").first() is None
    assert db_session.query(AuditLog).filter(AuditLog.action == "RECENT").first() is not None
