import re

def verify_file_signature(file_content: bytes, file_type: str) -> bool:
    """
    Verifies the file signature (magic number) against the expected file type.
    """
    if file_type.lower() == 'pdf':
        # PDF signature: %PDF-
        return file_content.startswith(b'%PDF-')

    elif file_type.lower() == 'csv':
        # CSV doesn't have a strict magic number, but we can check
        # if it's readable text and doesn't contain binary control characters
        # (excluding standard whitespace like \n, \r, \t)
        try:
            # Try to decode as UTF-8 (or other common encodings if needed)
            # If it fails, it's likely binary
            text = file_content.decode('utf-8')
        except UnicodeDecodeError:
            try:
                text = file_content.decode('cp1252') # Common fallback
            except UnicodeDecodeError:
                try:
                     text = file_content.decode('latin-1')
                except:
                     return False

        # Heuristic: check for null bytes which are rare in valid CSVs
        if b'\x00' in file_content:
            return False

        return True

    return False

def sanitize_filename(filename: str) -> str:
    """
    Sanitizes a string to be safe for use as a filename.
    Replaces invalid characters with underscores.
    """
    if not filename:
        return ""
    # Replace invalid chars with _
    # Windows invalid: < > : " / \ | ? *
    # Also good to avoid control chars
    return re.sub(r'[<>:"/\\|?*]', '_', filename).strip()
