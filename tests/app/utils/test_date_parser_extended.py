import pytest
from datetime import date
from app.utils.date_parser import parse_date_flexible

def test_parse_date_ambiguous_italian():
    # 02/03/2023 -> 2 March in Italy (DD/MM/YYYY priority)
    d = parse_date_flexible("02/03/2023")
    assert d == date(2023, 3, 2)

def test_parse_date_fallback_dots():
    # 02.03.2023 -> 2 March
    d = parse_date_flexible("02.03.2023")
    assert d == date(2023, 3, 2)

def test_parse_date_iso():
    d = parse_date_flexible("2023-03-02")
    assert d == date(2023, 3, 2)

def test_parse_date_slash_iso():
    d = parse_date_flexible("2023/03/02")
    assert d == date(2023, 3, 2)
