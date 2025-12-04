import os
from datetime import datetime
from app.utils.file_security import sanitize_filename

def find_document(database_path: str, cert_data: dict) -> str | None:
    """
    Locates the certificate PDF within the database directory structure.

    Args:
        database_path: The root path of the database.
        cert_data: Dictionary containing 'nome', 'matricola', 'categoria', 'data_scadenza'.

    Returns:
        Absolute path to the file if found, else None.
    """
    if not database_path or not cert_data:
        return None

    nome = cert_data.get('nome') or 'SCONOSCIUTO'

    # Logic matches import_view.py: defaults to 'N-A' if missing
    matricola = cert_data.get('matricola')
    if not matricola or str(matricola).strip() == "" or str(matricola).lower() == "none":
        matricola = 'N-A'

    categoria = cert_data.get('categoria') or 'ALTRO'
    data_scadenza_str = cert_data.get('data_scadenza')

    # Sanitize components for file system usage
    nome_fs = sanitize_filename(nome)
    matricola_fs = sanitize_filename(str(matricola))
    categoria_fs = sanitize_filename(categoria)

    # Date Formatting: API DD/MM/YYYY -> Filename DD_MM_YYYY
    file_scadenza = "no scadenza"
    if data_scadenza_str and str(data_scadenza_str).lower() != "none" and str(data_scadenza_str).strip() != "":
        try:
            date_obj = datetime.strptime(str(data_scadenza_str), '%d/%m/%Y')
            file_scadenza = date_obj.strftime('%d_%m_%Y')
        except ValueError:
            pass

    # Construct Path Components
    employee_folder = f"{nome_fs} ({matricola_fs})"
    filename = f"{nome_fs} ({matricola_fs}) - {categoria_fs} - {file_scadenza}.pdf"

    # Structure: DATABASE / DOCUMENTI DIPENDENTI / Name (Matr) / Cat / Status / File
    base_search_path = os.path.join(database_path, "DOCUMENTI DIPENDENTI", employee_folder, categoria_fs)

    # Statuses to check (order doesn't strictly matter if filename is unique per expiration,
    # but strictly speaking a file exists in only one status folder at a time)
    statuses = ["ATTIVO", "IN SCADENZA", "SCADUTO", "STORICO", "RINNOVATO"]

    # 1. Search in Standard Path
    for status in statuses:
        candidate = os.path.join(base_search_path, status, filename)
        if os.path.isfile(candidate):
            return os.path.normpath(candidate)

    # 2. Search in Error Paths (for Validation View items)
    # Structure: ERRORI ANALISI / <ErrCategory> / <EmployeeFolder> / <Category> / <Status> / <Filename>
    error_categories = ["ASSENZA MATRICOLE", "CATEGORIA NON TROVATA", "DUPLICATI", "ALTRI ERRORI"]

    for err_cat in error_categories:
        base_error_path = os.path.join(database_path, "ERRORI ANALISI", err_cat, employee_folder, categoria_fs)
        for status in statuses:
             candidate = os.path.join(base_error_path, status, filename)
             if os.path.isfile(candidate):
                 return os.path.normpath(candidate)

    return None
