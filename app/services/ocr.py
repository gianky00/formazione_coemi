import os
from fastapi import UploadFile
from pathlib import Path

# Definisce la cartella di upload in modo relativo alla posizione di questo file
UPLOAD_DIRECTORY = Path(__file__).resolve().parent.parent / "uploads"

def save_uploaded_file(upload_file: UploadFile) -> str:
    """
    Questa funzione non salva più il file, ma crea la cartella 'uploads' se non esiste
    per compatibilità con la logica precedente. Restituisce un percorso fittizio.
    """
    # Crea la cartella 'uploads' se non esiste, per evitare errori in altre parti del codice
    # che potrebbero fare affidamento sulla sua esistenza.
    if not UPLOAD_DIRECTORY.exists():
        UPLOAD_DIRECTORY.mkdir()

    # Restituisce un percorso non utilizzato per mantenere la firma della funzione.
    # La logica che utilizzava questo percorso è stata rimossa.
    return ""

def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Questa funzione è obsoleta e non contiene più la logica di Tesseract.
    Restituisce una stringa vuota per mantenere la compatibilità dove viene chiamata.
    """
    return ""
