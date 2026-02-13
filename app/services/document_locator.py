import glob
import os
from datetime import datetime
from typing import Any

from app.utils.file_security import sanitize_filename
from desktop_app.constants import DATE_FORMAT_FILE, DIR_ANALYSIS_ERRORS

# Python-compatible date format for backend parsing (Qt uses 'dd/MM/yyyy')
DATE_FORMAT_PYTHON: str = "%d/%m/%Y"


def _format_file_scadenza(data_scadenza_str: Any) -> str:
    if (
        data_scadenza_str
        and str(data_scadenza_str).lower() != "none"
        and str(data_scadenza_str).strip() != ""
    ):
        try:
            date_obj = datetime.strptime(str(data_scadenza_str), DATE_FORMAT_PYTHON)
            return date_obj.strftime(DATE_FORMAT_FILE)
        except ValueError:
            pass
    return "no scadenza"


def _search_exact_path(base_path: str, filename: str, statuses: list[str]) -> str | None:
    """Search for exact filename in status folders."""
    for status in statuses:
        candidate = os.path.join(base_path, status, filename)
        if os.path.isfile(candidate):
            return os.path.normpath(candidate)
    return None


def _search_partial_match(
    base_path: str, nome_fs: str, categoria_fs: str, statuses: list[str]
) -> str | None:
    """Search for files matching partial pattern (name and category)."""
    for status in statuses:
        status_path = os.path.join(base_path, status)
        if not os.path.isdir(status_path):
            continue
        # Search for files containing the name and category
        pattern = os.path.join(status_path, f"*{nome_fs}*{categoria_fs}*.pdf")
        matches = glob.glob(pattern, recursive=False)
        if matches:
            # Return most recent file
            return os.path.normpath(max(matches, key=os.path.getmtime))
    return None


def _search_in_folder_tree(database_path: str, nome_fs: str, categoria_fs: str) -> str | None:
    """Deep search in the entire DOCUMENTI DIPENDENTI tree."""
    docs_path = os.path.join(database_path, "DOCUMENTI DIPENDENTI")
    if not os.path.isdir(docs_path):
        return None

    # Search for any PDF containing the employee name
    for root, dirs, files in os.walk(docs_path):
        for file in files:
            if file.lower().endswith(".pdf"):
                file_lower = file.lower()
                nome_lower = nome_fs.lower()
                # Match by name in filename
                if nome_lower in file_lower:
                    # If category also matches, prioritize
                    if categoria_fs.lower() in file_lower:
                        return os.path.normpath(os.path.join(root, file))

    # Fallback: just name match
    for root, dirs, files in os.walk(docs_path):
        for file in files:
            if file.lower().endswith(".pdf") and nome_fs.lower() in file.lower():
                return os.path.normpath(os.path.join(root, file))

    return None


def find_document(database_path: str, cert_data: dict[str, Any]) -> str | None:
    """
    Locates the certificate PDF within the database directory structure.
    """
    if not database_path or not cert_data:
        return None

    nome = str(cert_data.get("nome") or "SCONOSCIUTO")
    matricola = cert_data.get("matricola")
    # Robust Matricola check for unvalidated files (often None or N/D or N-A)
    matricola_str = str(matricola).strip().lower()
    if not matricola or matricola_str == "" or matricola_str == "none" or matricola_str == "n/d":
        matricola = "N-A"

    categoria = str(cert_data.get("categoria") or "ALTRO")

    nome_fs = sanitize_filename(nome)
    matricola_fs = sanitize_filename(str(matricola))
    categoria_fs = sanitize_filename(categoria)

    file_scadenza = _format_file_scadenza(cert_data.get("data_scadenza"))

    employee_folder = f"{nome_fs} ({matricola_fs})"
    filename = f"{nome_fs} ({matricola_fs}) - {categoria_fs} - {file_scadenza}.pdf"

    statuses = ["ATTIVO", "IN SCADENZA", "SCADUTO", "STORICO", "RINNOVATO"]

    # 1. Search in Standard Path (exact match)
    base_search_path = os.path.join(
        database_path, "DOCUMENTI DIPENDENTI", employee_folder, categoria_fs
    )
    result = _search_exact_path(base_search_path, filename, statuses)
    if result:
        return result

    # 2. Search in Error Paths (exact match)
    error_categories = ["ASSENZA MATRICOLE", "CATEGORIA NON TROVATA", "DUPLICATI", "ALTRI ERRORI"]
    for err_cat in error_categories:
        base_error_path = os.path.join(
            database_path, DIR_ANALYSIS_ERRORS, err_cat, employee_folder, categoria_fs
        )
        result = _search_exact_path(base_error_path, filename, statuses)
        if result:
            return result

    # 3. Try with orphan folder (N-A) if we have a matricola
    if matricola != "N-A":
        orphan_folder = f"{nome_fs} (N-A)"
        orphan_path = os.path.join(
            database_path, "DOCUMENTI DIPENDENTI", orphan_folder, categoria_fs
        )
        orphan_filename = f"{nome_fs} (N-A) - {categoria_fs} - {file_scadenza}.pdf"
        result = _search_exact_path(orphan_path, orphan_filename, statuses)
        if result:
            return result

    # 4. Partial match search in employee folder
    result = _search_partial_match(base_search_path, nome_fs, categoria_fs, statuses)
    if result:
        return result

    # 5. Deep search in entire DOCUMENTI DIPENDENTI tree
    result = _search_in_folder_tree(database_path, nome_fs, categoria_fs)
    if result:
        return result

    return None


def construct_certificate_path(
    database_path: str, cert_data: dict[str, Any], status: str = "ATTIVO"
) -> str:
    """
    Constructs the expected file path for a certificate based on its data.
    """
    nome = str(cert_data.get("nome") or "SCONOSCIUTO")
    matricola = cert_data.get("matricola")
    if not matricola or str(matricola).strip() == "" or str(matricola).lower() == "none":
        matricola = "N-A"
    categoria = str(cert_data.get("categoria") or "ALTRO")

    nome_fs = sanitize_filename(nome)
    matricola_fs = sanitize_filename(str(matricola))
    categoria_fs = sanitize_filename(categoria)

    file_scadenza = _format_file_scadenza(cert_data.get("data_scadenza"))

    employee_folder = f"{nome_fs} ({matricola_fs})"
    filename = f"{nome_fs} ({matricola_fs}) - {categoria_fs} - {file_scadenza}.pdf"

    return os.path.join(
        database_path, "DOCUMENTI DIPENDENTI", employee_folder, categoria_fs, status, filename
    )
