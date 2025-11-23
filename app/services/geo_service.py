import os
import geoip2.database
from typing import Optional

class GeoLocationService:
    _reader = None
    _db_path = "GeoLite2-City.mmdb" # Expecting it in root or configured path

    @classmethod
    def get_location(cls, ip: str) -> str:
        if ip in ("127.0.0.1", "::1", "localhost"):
            return "Localhost"

        # Try to find the DB file
        if not cls._reader:
            try:
                # check current dir
                if os.path.exists(cls._db_path):
                    cls._reader = geoip2.database.Reader(cls._db_path)
                # check app/assets if we decide to put it there
                elif os.path.exists(os.path.join("app", "assets", cls._db_path)):
                     cls._reader = geoip2.database.Reader(os.path.join("app", "assets", cls._db_path))
            except Exception:
                pass

        if cls._reader:
            try:
                response = cls._reader.city(ip)
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
        if cls._reader:
            cls._reader.close()
