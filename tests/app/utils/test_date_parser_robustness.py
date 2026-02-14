from datetime import date

from app.utils.date_parser import parse_date_flexible


def test_parse_date_empty_or_none():
    assert parse_date_flexible("") is None
    assert parse_date_flexible(None) is None  # type: ignore
    assert parse_date_flexible("   ") is None


def test_parse_date_invalid_strings():
    assert parse_date_flexible("not a date") is None
    assert parse_date_flexible("31/02/2023") is None  # Invalid day for month
    # 2023-13-01 is actually parsed as 13th Jan 2023 by dateutil (YYYY-DD-MM fallback)
    assert parse_date_flexible("2023-13-01") == date(2023, 1, 13)
    assert parse_date_flexible("2023-13-40") is None  # Truly invalid


def test_parse_date_single_digits():
    # dateutil should handle these even if strptime doesn't with %d/%m/%Y
    assert parse_date_flexible("1/1/2023") == date(2023, 1, 1)
    assert parse_date_flexible("01/1/23") == date(2023, 1, 1)


def test_parse_date_italian_text():
    # dateutil_parser might struggle with Italian month names by default,
    # but let's see what it does.
    # Actually, dateutil is mainly English.
    # If the project needs Italian, it might need extra config.
    # Let's test English for now as it's the default behavior of dateutil.
    assert parse_date_flexible("1 January 2023") == date(2023, 1, 1)
    assert parse_date_flexible("2023 Oct 15") == date(2023, 10, 15)


def test_parse_date_various_delimiters():
    assert parse_date_flexible("12 05 2024") == date(2024, 5, 12)
    assert parse_date_flexible("12-05-2024") == date(2024, 5, 12)


def test_parse_date_future_past():
    assert parse_date_flexible("01/01/1900") == date(1900, 1, 1)
    assert parse_date_flexible("31/12/2099") == date(2099, 12, 31)


def test_parse_date_short_year():
    # %d/%m/%y handles 2-digit years
    # 23 -> 2023 (usually 0-68 -> 2000-2068, 69-99 -> 1969-1999)
    assert parse_date_flexible("01/01/23") == date(2023, 1, 1)
    assert parse_date_flexible("01/01/70") == date(1970, 1, 1)
