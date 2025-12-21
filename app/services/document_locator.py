import os
from datetime import datetime
from app.utils.file_security import sanitize_filename
from desktop_app.constants import DIR_ANALYSIS_ERRORS, DATE_FORMAT_FILE

# Python-compatible date format for backend parsing (Qt uses 'dd/MM/yyyy')
DATE_FORMAT_PYTHON = "%d/%m/%Y"

def _format_file_scadenza(data_scadenza_str):
    if data_scadenza_str and str(data_scadenza_str).lower() != "none" and str(data_scadenza_str).strip() != "":
        try:
            date_obj = datetime.strptime(str(data_scadenza_str), DATE_FORMAT_PYTHON)
            return date_obj.strftime(DATE_FORMAT_FILE)
        except ValueError:
            pass
    return "no scadenza"

def find_document(database_path: str, cert_data: dict) -> str | None:
    """
    Locates the certificate PDF within the database directory structure.
    """
    # S3776: Refactored to reduce complexity
    if not database_path or not cert_data:
        return None

    nome = cert_data.get('nome') or 'SCONOSCIUTO'
    matricola = cert_data.get('matricola')
    # Robust Matricola check for unvalidated files (often None or N/D or N-A)
    matricola_str = str(matricola).strip().lower()
    if not matricola or matricola_str == "" or matricola_str == "none" or matricola_str == "n/d":
        matricola = 'N-A'

    categoria = cert_data.get('categoria') or 'ALTRO'

    nome_fs = sanitize_filename(nome)
    matricola_fs = sanitize_filename(str(matricola))
    categoria_fs = sanitize_filename(categoria)

    file_scadenza = _format_file_scadenza(cert_data.get('data_scadenza'))

    employee_folder = f"{nome_fs} ({matricola_fs})"
    filename = f"{nome_fs} ({matricola_fs}) - {categoria_fs} - {file_scadenza}.pdf"

    # 1. Search in Standard Path
    base_search_path = os.path.join(database_path, "DOCUMENTI DIPENDENTI", employee_folder, categoria_fs)
    statuses = ["ATTIVO", "IN SCADENZA", "SCADUTO", "STORICO", "RINNOVATO"]

    for status in statuses:
        candidate = os.path.join(base_search_path, status, filename)
        if os.path.isfile(candidate):
            return os.path.normpath(candidate)
    # 2. Search in Error Paths
    error_categories = ["ASSENZA MATRICOLE", "CATEGORIA NON TROVATA", "DUPLICATI", "ALTRI ERRORI"]
    for err_cat in error_categories:
        base_error_path = os.path.join(database_path, DIR_ANALYSIS_ERRORS, err_cat, employee_folder, categoria_fs)
        for status in statuses:
             candidate = os.path.join(base_error_path, status, filename)
             if os.path.isfile(candidate):
                 return os.path.normpath(candidate)

    return None

def construct_certificate_path(database_path: str, cert_data: dict, status: str = "ATTIVO") -> str:
    """
    Constructs the expected file path for a certificate based on its data.
    Useful for creating new files or renaming existing ones.
    """
    nome = cert_data.get('nome') or 'SCONOSCIUTO'
    matricola = cert_data.get('matricola')
    if not matricola or str(matricola).strip() == "" or str(matricola).lower() == "none":
        matricola = 'N-A'
    categoria = cert_data.get('categoria') or 'ALTRO'

    nome_fs = sanitize_filename(nome)
    matricola_fs = sanitize_filename(str(matricola))
    categoria_fs = sanitize_filename(categoria)

    file_scadenza = _format_file_scadenza(cert_data.get('data_scadenza'))

    employee_folder = f"{nome_fs} ({matricola_fs})"
    filename = f"{nome_fs} ({matricola_fs}) - {categoria_fs} - {file_scadenza}.pdf"

    return os.path.join(database_path, "DOCUMENTI DIPENDENTI", employee_folder, categoria_fs, status, filename)
