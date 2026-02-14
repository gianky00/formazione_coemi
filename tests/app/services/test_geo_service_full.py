from unittest.mock import MagicMock, patch

from app.services.geo_service import GeoLocationService


def test_get_location_localhost():
    assert GeoLocationService.get_location("127.0.0.1") == "Localhost"
    assert GeoLocationService.get_location("::1") == "Localhost"


def test_get_location_no_db_file():
    GeoLocationService._reader = None
    with patch("app.services.geo_service.settings") as mock_settings:
        mock_settings.GEOLITE_DB_PATH = "/tmp/missing.mmdb"
        with patch("os.path.exists", return_value=False):
            assert GeoLocationService.get_location("8.8.8.8") == "Unknown"


def test_get_location_db_found_success():
    GeoLocationService._reader = None
    mock_reader = MagicMock()
    mock_response = MagicMock()
    mock_response.city.name = "Milan"
    mock_response.country.name = "Italy"
    mock_reader.city.return_value = mock_response

    with patch("app.services.geo_service.settings") as mock_settings:
        mock_settings.GEOLITE_DB_PATH = "/tmp/found.mmdb"
        with (
            patch("pathlib.Path.exists", return_value=True),
            patch("geoip2.database.Reader", return_value=mock_reader),
        ):
            loc = GeoLocationService.get_location("1.2.3.4")
            assert loc == "Milan, Italy"


def test_get_location_db_found_partial_data():
    GeoLocationService._reader = None
    mock_reader = MagicMock()

    # Country only
    mock_resp_country = MagicMock()
    mock_resp_country.city.name = None
    mock_resp_country.country.name = "Italy"
    mock_reader.city.return_value = mock_resp_country

    with patch("app.services.geo_service.settings") as mock_settings:
        mock_settings.GEOLITE_DB_PATH = "/tmp/found.mmdb"
        with (
            patch("pathlib.Path.exists", return_value=True),
            patch("geoip2.database.Reader", return_value=mock_reader),
        ):
            assert GeoLocationService.get_location("1.1.1.1") == "Italy"


def test_get_location_lookup_exception():
    GeoLocationService._reader = MagicMock()
    GeoLocationService._reader.city.side_effect = Exception("Lookup failed")
    assert GeoLocationService.get_location("8.8.8.8") == "Unknown"


def test_close_service():
    mock_reader = MagicMock()
    GeoLocationService._reader = mock_reader
    GeoLocationService.close()
    mock_reader.close.assert_called_once()
    assert GeoLocationService._reader is None
