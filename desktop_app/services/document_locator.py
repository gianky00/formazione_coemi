import os
from datetime import datetime

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

    # Date Formatting: API DD/MM/YYYY -> Filename DD_MM_YYYY
    file_scadenza = "no scadenza"
    if data_scadenza_str and str(data_scadenza_str).lower() != "none" and str(data_scadenza_str).strip() != "":
        try:
            date_obj = datetime.strptime(str(data_scadenza_str), '%d/%m/%Y')
            file_scadenza = date_obj.strftime('%d_%m_%Y')
        except ValueError:
            pass

    # Construct Path Components
    employee_folder = f"{nome} ({matricola})"
    filename = f"{nome} ({matricola}) - {categoria} - {file_scadenza}.pdf"

    # Structure: DATABASE / DOCUMENTI DIPENDENTI / Name (Matr) / Cat / Status / File
    base_search_path = os.path.join(database_path, "DOCUMENTI DIPENDENTI", employee_folder, categoria)

    # Statuses to check (order doesn't strictly matter if filename is unique per expiration,
    # but strictly speaking a file exists in only one status folder at a time)
    statuses = ["ATTIVO", "IN SCADENZA", "SCADUTO", "STORICO", "RINNOVATO"]

    for status in statuses:
        candidate = os.path.join(base_search_path, status, filename)
        if os.path.isfile(candidate):
            return os.path.normpath(candidate)

    return None
