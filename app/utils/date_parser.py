from datetime import datetime, date
from typing import Optional
import re

from typing import Union

def parse_date_flexible(date_input: Union[str, date]) -> Optional[date]:
    """
    Robustly parses a date from a string or returns it if already a date object.
    Supported formats:
    - DD/MM/YYYY
    - DD-MM-YYYY
    - YYYY-MM-DD
    - DD/MM/YY
    - DD.MM.YYYY
    """
    if not date_input:
        return None
        
    if isinstance(date_input, date):
        return date_input

    date_str = str(date_input).strip()

    # Remove text like "nato il " if present, though unlikely in raw date fields
    # simple cleanup

    formats = [
        '%d/%m/%Y',
        '%d-%m-%Y',
        '%Y-%m-%d',
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
