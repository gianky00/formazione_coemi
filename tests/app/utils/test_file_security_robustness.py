from app.utils.file_security import get_pdf_text_preview, sanitize_filename


def test_sanitize_filename_basic():
    assert sanitize_filename("test.pdf") == "test.pdf"
    assert sanitize_filename("test/../file.pdf") == "test_.._file.pdf"
    assert sanitize_filename('viva l"italia?.pdf') == "viva_l_italia_.pdf"
    assert sanitize_filename("<tag>:*|") == "_tag____"
    assert sanitize_filename("   spaced   ") == "spaced"
    assert sanitize_filename("") == ""
    assert sanitize_filename(None) == ""


def test_get_pdf_text_preview_logic():
    # Simple ASCII within PDF structure
    pdf_content = b"%PDF-1.4\n1 0 obj\n<< /Title (Test Document) >>\nendobj\ntrailer\n<< /Root 1 0 R >>\n%%EOF"
    preview = get_pdf_text_preview(pdf_content, max_chars=20)

    # It should extract printable chars
    assert "PDF-1.4" in preview
    assert len(preview) <= 20


def test_get_pdf_text_preview_empty_or_none():
    assert get_pdf_text_preview(b"") == ""
    assert get_pdf_text_preview(None) == ""


def test_get_pdf_text_preview_non_printable():
    # Only non-printable bytes
    content = bytes([0, 1, 2, 3, 4, 5])
    # Based on chr(b) if 32 <= b <= 126 else " "
    # it should return a string of spaces, then stripped
    assert get_pdf_text_preview(content) == ""


def test_get_pdf_text_preview_newline_handling():
    content = b"Line1\nLine2\rLine3"
    preview = get_pdf_text_preview(content)
    # re.sub(r"\s+", " ", text) will convert \n and \r to single space
    assert preview == "Line1 Line2 Line3"
