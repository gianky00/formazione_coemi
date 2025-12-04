import pytest
from app.utils.file_security import verify_file_signature

def test_verify_pdf():
    assert verify_file_signature(b"%PDF-1.4...", "pdf") is True
    assert verify_file_signature(b"garbage", "pdf") is False

def test_verify_csv_utf8():
    assert verify_file_signature(b"a,b,c\n1,2,3", "csv") is True

def test_verify_csv_cp1252():
    # CP1252 char: \x80 (Euro sign in some maps, or just reserved, but valid byte in latin-1/cp1252)
    # Actually \xe9 is é
    content = "è".encode("cp1252")
    assert verify_file_signature(content, "csv") is True

def test_verify_csv_binary_null():
    assert verify_file_signature(b"a,b\x00c", "csv") is False

def test_unknown_type():
    assert verify_file_signature(b"content", "exe") is False

def test_verify_csv_latin1_fallback():
    # Only valid in latin-1, invalid in utf-8
    content = b"\xe9" # é in latin-1. In utf-8 it's a start byte requiring more.
    assert verify_file_signature(content, "csv") is True

def test_verify_csv_latin1_strict_fallback():
    # Byte \x81 is Undefined in cp1252, but valid in latin-1 (Control char).
    # This forces UnicodeDecodeError in cp1252 block, falling back to latin-1.
    content = b"\x81"
    assert verify_file_signature(content, "csv") is True
