from PyQt6.QtCore import QRunnable, pyqtSignal, QObject
import requests
import sentry_sdk

class WorkerSignals(QObject):
    """
    Defines the signals available from a running worker thread.
    Supported signals are:
    finished: No data
    error: str (error message)
    result: object (data returned from processing)
    progress: int, int (current, total)
    """
    finished = pyqtSignal()
    error = pyqtSignal(str)
    result = pyqtSignal(object)
    progress = pyqtSignal(int, int)

class FetchCertificatesWorker(QRunnable):
    def __init__(self, api_client, validated=True):
        super().__init__()
        self.api_client = api_client
        self.validated = validated
        self.signals = WorkerSignals()

    def run(self):
        try:
            params = {}
            if self.validated is not None:
                params['validated'] = str(self.validated).lower()

            response = requests.get(
                f"{self.api_client.base_url}/certificati/",
                params=params,
                headers=self.api_client._get_headers(),
                timeout=60 # Bug 5 Fix: Increased timeout
            )
            response.raise_for_status()
            data = response.json()
            self.signals.result.emit(data)
        except requests.exceptions.RequestException as e:
            sentry_sdk.capture_exception(e)
            self.signals.error.emit(str(e))
        except Exception as e:
            sentry_sdk.capture_exception(e)
            self.signals.error.emit(str(e))
        finally:
            self.signals.finished.emit()

class DeleteCertificatesWorker(QRunnable):
    def __init__(self, api_client, cert_ids):
        super().__init__()
        self.api_client = api_client
        self.cert_ids = cert_ids
        self.signals = WorkerSignals()

    def run(self):
        success_count = 0
        errors = []
        total = len(self.cert_ids)
        try:
            for i, cert_id in enumerate(self.cert_ids):
                self.signals.progress.emit(i + 1, total)
                try:
                    response = requests.delete(
                        f"{self.api_client.base_url}/certificati/{cert_id}",
                        headers=self.api_client._get_headers(),
                        timeout=30
                    )
                    response.raise_for_status()
                    success_count += 1
                except Exception as e:
                    errors.append(f"ID {cert_id}: {str(e)}")

            self.signals.result.emit({"success": success_count, "errors": errors})
        except Exception as e:
            sentry_sdk.capture_exception(e)
            # Bug 6 Fix: Emit partial result even on catastrophic failure if some succeeded
            if success_count > 0 or errors:
                 self.signals.result.emit({"success": success_count, "errors": errors + [f"Critical Stop: {str(e)}"]})
            else:
                 self.signals.error.emit(str(e))
        finally:
            self.signals.finished.emit()

class UpdateCertificateWorker(QRunnable):
    def __init__(self, api_client, cert_id, data):
        super().__init__()
        self.api_client = api_client
        self.cert_id = cert_id
        self.data = data
        self.signals = WorkerSignals()

    def run(self):
        try:
            response = requests.put(
                f"{self.api_client.base_url}/certificati/{self.cert_id}",
                json=self.data,
                headers=self.api_client._get_headers(),
                timeout=30
            )
            response.raise_for_status()
            self.signals.result.emit(True)
        except Exception as e:
            sentry_sdk.capture_exception(e)
            self.signals.error.emit(str(e))
        finally:
            self.signals.finished.emit()

class ValidateCertificatesWorker(QRunnable):
    def __init__(self, api_client, cert_ids):
        super().__init__()
        self.api_client = api_client
        self.cert_ids = cert_ids
        self.signals = WorkerSignals()

    def run(self):
        success_count = 0
        errors = []
        total = len(self.cert_ids)
        try:
            for i, cert_id in enumerate(self.cert_ids):
                self.signals.progress.emit(i + 1, total)
                try:
                    response = requests.put(
                        f"{self.api_client.base_url}/certificati/{cert_id}/valida",
                        headers=self.api_client._get_headers(),
                        timeout=30
                    )
                    response.raise_for_status()
                    success_count += 1
                except Exception as e:
                    errors.append(f"ID {cert_id}: {str(e)}")

            self.signals.result.emit({"success": success_count, "errors": errors})
        except Exception as e:
            sentry_sdk.capture_exception(e)
            # Bug 6 Fix: Partial result logic
            if success_count > 0 or errors:
                 self.signals.result.emit({"success": success_count, "errors": errors + [f"Critical Stop: {str(e)}"]})
            else:
                 self.signals.error.emit(str(e))
        finally:
            self.signals.finished.emit()
