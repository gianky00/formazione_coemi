from datetime import datetime, date
from typing import Optional
import re
from dateutil import parser as dateutil_parser

def parse_date_flexible(date_str: str) -> Optional[date]:
    """
    Tries to parse a date string from various formats.
    Supported formats:
    - DD/MM/YYYY
    - DD-MM-YYYY
    - YYYY-MM-DD
    - DD/MM/YY
    - DD.MM.YYYY

    Falls back to dateutil.parser with dayfirst=True for ambiguous dates (e.g. 02/03/2023 -> 2nd March).
    """
    if not date_str:
        return None

    date_str = date_str.strip()

    # Simple manual formats first (fastest and strictly defined)
    formats = [
        '%d/%m/%Y',
        '%d-%m-%Y',
        '%Y-%m-%d',
        '%Y/%m/%d',
        '%d.%m.%Y',
        '%d/%m/%y',
        '%d-%m-%y'
    ]

    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue

    # Robust fallback for other formats
    try:
        dt = dateutil_parser.parse(date_str, dayfirst=True)
        return dt.date()
    except (ValueError, TypeError, OverflowError):
        pass

    return None
