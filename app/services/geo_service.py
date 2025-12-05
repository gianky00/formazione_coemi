import os
import geoip2.database
from typing import Optional
import threading

class GeoLocationService:
    _reader = None
    _db_path = "GeoLite2-City.mmdb"
    _lock = threading.Lock()

    @classmethod
    def get_reader(cls):
        if cls._reader:
            return cls._reader

        with cls._lock:
            if cls._reader: return cls._reader

            paths = [
                cls._db_path,
                os.path.join("app", "assets", cls._db_path),
                # Fallback for frozen/different cwd
                os.path.join(os.path.dirname(__file__), "..", "assets", cls._db_path)
            ]

            for path in paths:
                if os.path.exists(path):
                    try:
                        cls._reader = geoip2.database.Reader(path)
                        return cls._reader
                    except Exception:
                        pass
            return None

    @classmethod
    def get_location(cls, ip: str) -> str:
        if ip in ("127.0.0.1", "::1", "localhost"):
            return "Localhost"

        reader = cls.get_reader()
        if reader:
            try:
                response = reader.city(ip)
                city = response.city.name or ""
                country = response.country.name or ""
                if city and country:
                    return f"{city}, {country}"
                elif country:
                    return country
                elif city:
                    return city
            except Exception:
                pass

        return "Unknown"

    @classmethod
    def close(cls):
        with cls._lock:
            if cls._reader:
                cls._reader.close()
                cls._reader = None
