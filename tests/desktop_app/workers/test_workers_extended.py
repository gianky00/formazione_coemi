import sys
from unittest.mock import MagicMock, patch
import pytest

from tests.desktop_app.mock_qt import mock_modules
with patch.dict(sys.modules, mock_modules):
    from desktop_app.workers.data_worker import UpdateCertificateWorker, ValidateCertificatesWorker

class TestWorkersExtended:
    @pytest.fixture
    def api_client(self):
        client = MagicMock()
        client.base_url = "http://api"
        client._get_headers.return_value = {}
        return client

    def test_update_worker(self, api_client):
        worker = UpdateCertificateWorker(api_client, 1, {"data": "val"})

        with patch("requests.put") as mock_put:
            mock_put.return_value.raise_for_status.return_value = None

            worker.signals.result = MagicMock()
            worker.signals.finished = MagicMock()

            worker.run()

            mock_put.assert_called_with(
                "http://api/certificati/1",
                json={"data": "val"},
                headers={}
            )
            worker.signals.result.emit.assert_called_with(True)
            worker.signals.finished.emit.assert_called()

    def test_validate_worker(self, api_client):
        worker = ValidateCertificatesWorker(api_client, [1, 2])

        with patch("requests.put") as mock_put:
            # First success, second fail
            success_resp = MagicMock()
            success_resp.raise_for_status.return_value = None

            mock_put.side_effect = [success_resp, Exception("Error")]

            worker.signals.result = MagicMock()
            worker.signals.progress = MagicMock()

            worker.run()

            # Should emit progress
            worker.signals.progress.emit.assert_any_call(1, 2)

            # Result
            args = worker.signals.result.emit.call_args[0][0]
            assert args["success"] == 1
            assert len(args["errors"]) == 1
