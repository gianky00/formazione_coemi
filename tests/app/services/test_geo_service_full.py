import pytest
from unittest.mock import MagicMock, patch
from app.services.geo_service import GeoLocationService

def teardown_module(module):
    """Ensure reader is closed and reset after tests."""
    GeoLocationService.close()
    GeoLocationService._reader = None

def test_get_location_localhost():
    assert GeoLocationService.get_location("127.0.0.1") == "Localhost"
    assert GeoLocationService.get_location("::1") == "Localhost"
    assert GeoLocationService.get_location("localhost") == "Localhost"

def test_get_location_no_db_file():
    GeoLocationService._reader = None
    with patch("os.path.exists", return_value=False):
        assert GeoLocationService.get_location("8.8.8.8") == "Unknown"

def test_get_location_db_found_success():
    GeoLocationService._reader = None
    mock_reader = MagicMock()
    mock_response = MagicMock()
    mock_response.city.name = "Milan"
    mock_response.country.name = "Italy"
    mock_reader.city.return_value = mock_response

    with patch("os.path.exists", return_value=True), \
         patch("geoip2.database.Reader", return_value=mock_reader):

        loc = GeoLocationService.get_location("1.2.3.4")
        assert loc == "Milan, Italy"
        # Verify reader is cached
        assert GeoLocationService._reader == mock_reader

def test_get_location_db_found_partial_data():
    GeoLocationService._reader = None
    mock_reader = MagicMock()

    # Country only
    mock_resp_country = MagicMock()
    mock_resp_country.city.name = None
    mock_resp_country.country.name = "Italy"
    mock_reader.city.return_value = mock_resp_country

    with patch("os.path.exists", return_value=True), \
         patch("geoip2.database.Reader", return_value=mock_reader):
        assert GeoLocationService.get_location("1.1.1.1") == "Italy"

    # Reset
    GeoLocationService._reader = None
    mock_reader.city.reset_mock()

    # City only
    mock_resp_city = MagicMock()
    mock_resp_city.city.name = "Milan"
    mock_resp_city.country.name = None
    mock_reader.city.return_value = mock_resp_city

    with patch("os.path.exists", return_value=True), \
         patch("geoip2.database.Reader", return_value=mock_reader):
        assert GeoLocationService.get_location("2.2.2.2") == "Milan"

def test_get_location_lookup_exception():
    GeoLocationService._reader = MagicMock()
    GeoLocationService._reader.city.side_effect = Exception("Lookup failed")

    assert GeoLocationService.get_location("8.8.8.8") == "Unknown"

def test_close_reader():
    mock_reader = MagicMock()
    GeoLocationService._reader = mock_reader

    GeoLocationService.close()
    mock_reader.close.assert_called_once()
