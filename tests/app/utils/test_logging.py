from unittest.mock import patch

from app.utils.logging import setup_logging


def test_setup_logging_success(tmp_path):
    # Mock settings or just call it.
    # It sets up handlers. We don't want to mess up global logging for other tests,
    # so we might patch logging.basicConfig.

    with patch("logging.basicConfig") as mock_basic:
        setup_logging()
        mock_basic.assert_called()
