from unittest.mock import MagicMock, patch

from app.services.geo_service import GeoLocationService


def test_get_reader_file_exists_but_invalid():
    # Simulate file exists but is not a valid MaxMind database
    with patch("app.core.config.settings") as mock_settings:
        mock_settings.GEOLITE_DB_PATH = "fake.mmdb"
        with (
            patch("pathlib.Path.exists", return_value=True),
            patch("geoip2.database.Reader", side_effect=Exception("Invalid DB format")),
        ):
            GeoLocationService._reader = None
            assert GeoLocationService.get_reader() is None


def test_get_location_db_caching_behavior():
    mock_reader = MagicMock()
    with patch("app.core.config.settings") as mock_settings:
        mock_settings.GEOLITE_DB_PATH = "exists.mmdb"
        with (
            patch("pathlib.Path.exists", return_value=True),
            patch("geoip2.database.Reader", return_value=mock_reader) as mock_init,
        ):
            # CRITICAL: Reset singleton state for test
            GeoLocationService._reader = None

            # First call init
            GeoLocationService.get_location("1.1.1.1")
            # Second call should use cache
            GeoLocationService.get_location("1.1.1.1")

            assert mock_init.call_count == 1


def test_get_location_full_unknown_city_country():
    mock_reader = MagicMock()
    mock_response = MagicMock()
    mock_response.city.name = None
    mock_response.country.name = None
    mock_reader.city.return_value = mock_response

    GeoLocationService._reader = mock_reader
    assert GeoLocationService.get_location("8.8.8.8") == "Unknown"
