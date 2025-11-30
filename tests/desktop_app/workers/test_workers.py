import sys
from unittest.mock import MagicMock, patch
import pytest

from tests.desktop_app.mock_qt import mock_modules
with patch.dict(sys.modules, mock_modules):
    from desktop_app.workers.data_worker import FetchCertificatesWorker, DeleteCertificatesWorker

class TestWorkers:
    @pytest.fixture
    def api_client(self):
        client = MagicMock()
        client.base_url = "http://api"
        client._get_headers.return_value = {}
        return client

    def test_fetch_worker_success(self, api_client):
        worker = FetchCertificatesWorker(api_client)

        with patch("requests.get") as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = [{"id": 1}]

            # Use mock signals
            worker.signals.result = MagicMock()
            worker.signals.finished = MagicMock()

            worker.run()

            worker.signals.result.emit.assert_called_with([{"id": 1}])
            worker.signals.finished.emit.assert_called()

    def test_fetch_worker_failure(self, api_client):
        worker = FetchCertificatesWorker(api_client)

        with patch("requests.get") as mock_get:
            mock_get.side_effect = Exception("Net Error")

            worker.signals.error = MagicMock()
            worker.signals.finished = MagicMock()

            worker.run()

            worker.signals.error.emit.assert_called_with("Net Error")
            worker.signals.finished.emit.assert_called()

    def test_delete_worker(self, api_client):
        worker = DeleteCertificatesWorker(api_client, [1, 2])

        with patch("requests.delete") as mock_delete:
            # First success, second fail
            success_resp = MagicMock()
            success_resp.raise_for_status.return_value = None

            fail_resp = MagicMock()
            fail_resp.raise_for_status.side_effect = Exception("404")

            mock_delete.side_effect = [success_resp, Exception("404")]

            worker.signals.result = MagicMock()
            worker.signals.progress = MagicMock()

            worker.run()

            worker.signals.progress.emit.assert_any_call(1, 2)
            worker.signals.progress.emit.assert_any_call(2, 2)

            args = worker.signals.result.emit.call_args[0][0]
            assert args["success"] == 1
            assert len(args["errors"]) == 1
