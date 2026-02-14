import re


def verify_file_signature(file_content: bytes, file_type: str) -> bool:
    """
    Verifies the file signature (magic number) against the expected file type.
    """
    if file_type.lower() == "pdf":
        # PDF signature: %PDF-
        return file_content.startswith(b"%PDF-")

    elif file_type.lower() == "csv":
        import contextlib

        # CSV doesn't have a strict magic number, but we can check
        # if it's readable text and doesn't contain binary control characters
        # (excluding standard whitespace like \n, \r, \t)
        readable = False
        with contextlib.suppress(UnicodeDecodeError):
            file_content.decode("utf-8")
            readable = True

        if not readable:
            with contextlib.suppress(UnicodeDecodeError):
                file_content.decode("cp1252")
                readable = True

        if not readable:
            with contextlib.suppress(Exception):
                file_content.decode("latin-1")
                readable = True

        if not readable:
            return False

        # Heuristic: check for null bytes which are rare in valid CSVs
        return b"\x00" not in file_content

    return False


def sanitize_filename(filename: str) -> str:
    """
    Sanitizes a string to be safe for use as a filename.
    Replaces invalid characters and spaces with underscores.
    """
    if not filename:
        return ""
    # Replace invalid chars and spaces with _
    sanitized = re.sub(r'[<>:"/\\|?*\s]', "_", filename)
    return sanitized.strip("_")


def get_pdf_text_preview(pdf_bytes: bytes, max_chars: int = 10000) -> str:
    """
    Extracts a text preview from raw PDF bytes.
    Robust fallback if specialized libraries are missing.
    """
    if not pdf_bytes:
        return ""

    import contextlib

    with contextlib.suppress(Exception):
        # Very basic extraction: find text within PDF operators (simplified)
        # In a real scenario, use PyMuPDF or pypdf.
        # For now, we extract printable ASCII strings as a heuristic.
        text = "".join(chr(b) if 32 <= b <= 126 or b in [10, 13] else " " for b in pdf_bytes)
        # Clean up multiple spaces
        text = re.sub(r"\s+", " ", text)
        return text[:max_chars].strip()
    return ""
