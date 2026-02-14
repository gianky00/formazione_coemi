import contextlib
import logging

import geoip2.database
from geoip2.models import City

from app.core.config import settings

logger = logging.getLogger(__name__)


class GeoLocationService:
    _reader: geoip2.database.Reader | None = None

    @classmethod
    def get_reader(cls) -> geoip2.database.Reader | None:
        """Inizializza e ritorna il database GeoLite2."""
        if cls._reader is None:
            db_path = settings.GEOLITE_DB_PATH
            if not db_path:
                return None

            from pathlib import Path

            if not Path(db_path).exists():
                logger.warning(f"GeoLite2 database not found at {db_path}")
                return None

            try:
                cls._reader = geoip2.database.Reader(db_path)
            except Exception as e:
                logger.error(f"Failed to load GeoLite2 database: {e}")
                return None
        return cls._reader

    @classmethod
    def get_location(cls, ip_address: str) -> str:
        """Ritorna la stringa 'Città, Paese' per un dato IP."""
        if not ip_address or ip_address in ("127.0.0.1", "localhost", "::1"):
            return "Localhost"

        try:
            reader = cls.get_reader()
            if not reader:
                return "Unknown"

            response: City = reader.city(ip_address)
            city = response.city.name
            country = response.country.name or "Unknown"

            if city:
                return f"{city}, {country}"
            return country
        except Exception:
            return "Unknown"

    @classmethod
    def close(cls) -> None:
        """Chiude il database GeoLite2."""
        if cls._reader:
            with contextlib.suppress(Exception):
                cls._reader.close()
            cls._reader = None
