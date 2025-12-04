from datetime import datetime, date
from typing import Optional
import re

def parse_date_flexible(date_str: str) -> Optional[date]:
    """
    Tries to parse a date string from various formats.
    Supported formats:
    - DD/MM/YYYY
    - DD-MM-YYYY
    - YYYY-MM-DD
    - DD/MM/YY
    - DD.MM.YYYY
    """
    if not date_str:
        return None

    date_str = date_str.strip()

    # Remove text like "nato il " if present, though unlikely in raw date fields
    # simple cleanup

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

    return None
